#!/usr/bin/env python3
import argparse, csv, hashlib, json, os, pathlib, re, statistics
ROOT=pathlib.Path(__file__).resolve().parents[2]
os.environ.setdefault('TIKTOKEN_CACHE_DIR',str(ROOT/'investigation/.tokenizer-cache'))
try:
 import tiktoken
 ENC=tiktoken.get_encoding('o200k_base')
except (ImportError,Exception): ENC=None
CASES=json.loads((ROOT/'investigation/cases.json').read_text())

def measure(text):
 return {'bytes':len(text.encode()),'lines':len(text.splitlines()),'tokens':len(ENC.encode(text,disallowed_special=())) if ENC else None,'tokenizer':f'tiktoken {tiktoken.__version__} o200k_base' if ENC else 'unavailable'}

# First failure event, not CASE_BEGIN / startup / effective configuration.
MARKER=re.compile(r'(?:\bERROR\b.*(?:client setup failed|GET /orders|save users failed|invoice-42|Application run failed)|\[ERROR\].*(?:<<< FAILURE!|<<< ERROR!))')
FRAME=re.compile(r'^\s*at (?:org\.springframework\.|org\.junit\.|org\.apache\.|java\.|jdk\.|ch\.qos\.)')

def extract(text):
 lines=text.splitlines(keepends=True); hits=[i for i,l in enumerate(lines) if MARKER.search(l)]; first=hits[0] if hits else len(lines)
 # Boundary-aware: first event through before Maven's post-test Results section.
 end=next((i-1 for i in range(first+1,len(lines)) if lines[i].strip()=='[INFO] Results:'),len(lines))
 boundary=lines[first:end]
 # Only identical complete exception blocks; preserve timestamps/messages and count repeats explicitly.
 dedup=[]; seen={}; i=0
 header=re.compile(r'^(?:[\w.$]+\.)?[\w$]*(?:Exception|Error)(?::|\s|$)')
 while i<len(boundary):
  if header.search(boundary[i]):
   j=i+1
   while j<len(boundary) and (boundary[j].startswith(('\t','    ','Caused by:')) or not boundary[j].strip()): j+=1
   block=''.join(boundary[i:j]); key=hashlib.sha256(block.encode()).hexdigest()
   if key in seen: dedup.append('[identical exception block repeated; see block '+str(seen[key])+']\n')
   else: seen[key]=len(seen)+1; dedup.extend(boundary[i:j])
   i=j
  else: dedup.append(boundary[i]); i+=1
 return {'complete':text,'window20':''.join(lines[first:first+20]),'filtered40':''.join(l for l in lines[first:first+40] if not FRAME.match(l)),'boundary':''.join(boundary),'dedup':''.join(dedup)},len(hits)

def main(batch):
 rows=[]; artifact_rows=[]
 for meta_path in sorted((ROOT/f'investigation/raw/{batch}').glob('*/*/*/metadata.json')):
  meta=json.loads(meta_path.read_text()); directory=meta_path.parent
  base={k:meta[k] for k in ('case','config','run','exit','profile_verified','identity_verified','failure_identity','command_shell')}
  for path in sorted(directory.rglob('*')):
   if not path.is_file() or path.name=='metadata.json':continue
   producer='test-runner report' if path.suffix in ('.xml','.txt') else ('container stdout/stderr' if '.container.' in path.name else 'Maven + forked JVM stdout' if path.name=='stdout.log' else 'Maven + forked JVM stderr')
   artifact_rows.append({**base,'source':str(path.relative_to(ROOT)),'producer':producer,'sha256':hashlib.sha256(path.read_bytes()).hexdigest(),**measure(path.read_text(errors='replace'))})
  # Deterministic complete console = stdout then stderr; no claim of cross-stream time ordering.
  text=(directory/'stdout.log').read_text(errors='replace')+(directory/'stderr.log').read_text(errors='replace')
  outputs,count=extract(text)
  for method,value in outputs.items():
   out=ROOT/f'investigation/extracted/{batch}/{meta["case"]}/{meta["config"]}/{meta["run"]}/{method}.txt';out.parent.mkdir(parents=True,exist_ok=True);out.write_text(value)
   facts={k:v in value for k,v in CASES[meta['case']]['facts'].items()}
   rows.append({**base,'method':method,'source':str(directory.relative_to(ROOT)),'path':str(out.relative_to(ROOT)),'producer':'deterministic console extraction (not automatically agent input)','command':f'python investigation/scripts/analyze.py --batch {batch}','matches':count,'facts_present':sum(facts.values()),'facts_required':len(facts),'all_facts':all(facts.values()),'facts':json.dumps(facts,sort_keys=True),**measure(value),'within_source_bytes':len(value.encode())<=len(text.encode())})
 for name,data in [('results',rows),('artifacts',artifact_rows)]:
  dest=ROOT/f'investigation/{name}-{batch}';dest.with_suffix('.json').write_text(json.dumps(data,indent=2))
  if data:
   with dest.with_suffix('.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
 print(json.dumps({'runs':len(rows)//5,'extractions':len(rows),'valid':sum(r['identity_verified'] and r['profile_verified'] for r in rows)//5,'missing_diagnostics':sum(not r['all_facts'] for r in rows)}))
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--batch',default='v1');main(p.parse_args().batch)
