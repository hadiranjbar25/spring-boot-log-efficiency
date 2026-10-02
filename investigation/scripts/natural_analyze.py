#!/usr/bin/env python3
"""Classify returned text without assuming that files on disk were read."""
import argparse,csv,json,pathlib,re,shlex
from analyze import ROOT,measure,extract
CATEGORIES=['log_inspection','test_command','source_read','mixed','other']
LOG=re.compile(r'failure\.(?:log|stdout|stderr)|surefire-reports|[\w/.-]+\.log\b')
SOURCE=re.compile(r'(?:Defects|FailureCasesTest|ProfileVerificationTest)\.java|\b(?:src/|pom\.xml|test\.sh|AGENTS\.md)|(?:cat|sed|head|tail|rg|grep)\b.*\.(?:java|kt|xml|ya?ml)\b')
READ=re.compile(r'\b(?:cat|rg|grep|tail|head|sed|awk|less|more|python3?|wc)\b')
TEST=re.compile(r'(?:^|[\s;&|])(?:\./test\.sh|mvn|\./mvnw)(?:\s|$)')
def shell_body(cmd):
 try:
  p=shlex.split(cmd)
  if len(p)>=3 and p[1] in ['-lc','-c']:return p[2]
 except ValueError:pass
 return cmd

def classify(command,text,log):
 body=shell_body(command)
 # Explicitly reading test.sh counts as source; invoking it counts as a test command.
 readbody=re.sub(r'\brg\s+--files\b[^;\n]*','',body)
 test=bool(TEST.search(body) or re.search(r'(?:^|[\s/])jshell(?:\s|$)',body) or ('python' in body and re.search(r'(?m)^\s*assert\b',body)))
 log_read=bool(LOG.search(readbody) and READ.search(readbody))
 source=bool(SOURCE.search(body) and READ.search(body))
 # source regex includes test.sh even in "cat failure.log; ./test.sh"; remove command invocations for source detection.
 source=bool(SOURCE.search(TEST.sub('',readbody)) and READ.search(TEST.sub('',readbody)))
 source=source or bool(re.search(r'\b(?:rg|grep)\b[^;\n]*\binvestigation(?:/|\s|$)',readbody))
 other=bool(re.search(r'(?:^|[;|\n&])\s*(?:pwd|ls|find|git)\b|\brg\s+--files',body))
 if log_read and (source or test or other):cat='mixed'
 elif source and (test or other):cat='mixed'
 elif test:cat='test_command'
 elif log_read:cat='log_inspection'
 elif source:cat='source_read'
 else:cat='other'
 intervals=[];rules=[]
 if cat=='log_inspection':intervals=[(0,len(text))];rules=['entire log-directed result']
 elif cat=='mixed' and log_read:
  # A fully redirected test followed only by a tail returns the tail body.
  redirected=re.fullmatch(r'\s*\./test\.sh(?:\s+[^;>]+)?\s*>\s*(/[^\s;]+\.log)\s+2>&1;\s*tail\s+-n\s+\d+\s+\1\s*',body)
  if redirected:
   intervals=[(0,len(text))];rules=['fully redirected test followed only by log tail']
  candidates=[]
  if re.search(r'\bcat\s+(?:--\s+)?[\'\"]?failure\.log\b',body):candidates.append(('literal full-file match',log))
  # Only exact, deterministic slice matches. Unknown pipelines/search formatting remain unallocated.
  for a,b in re.findall(r"\bsed\s+-n\s+[\'\"]?(\d+),(\d+)p[\'\"]?\s+failure\.log",body):candidates.append(('literal sed slice match',''.join(log.splitlines(True)[int(a)-1:int(b)])))
  for op,n in re.findall(r'\b(head|tail)\s+-n\s*(\d+)\s+failure\.log',body):
   ls=log.splitlines(True);candidates.append(('literal '+op+' match',''.join(ls[:int(n)] if op=='head' else ls[-int(n):])))
  for rule,value in candidates:
   if not value:continue
   offset=0
   while True:
    start=text.find(value,offset)
    if start<0:break
    intervals.append((start,start+len(value)));rules.append(rule);offset=start+len(value)
 # Merge overlapping intervals but retain repeated occurrences at distinct positions.
 merged=[]
 for a,b in sorted(intervals):
  if merged and a<merged[-1][1]:merged[-1]=(merged[-1][0],max(b,merged[-1][1]))
  else:merged.append((a,b))
 segments=[text[a:b] for a,b in merged]
 primary=sum(measure(s)['tokens'] for s in segments)
 unresolved=cat=='mixed' and log_read and not merged
 return {'category':cat,'log_directed':log_read,'source_directed':source,'test_execution':test,'log_bytes_lower':sum(len(s.encode()) for s in segments),'log_bytes_upper':len(text.encode()) if unresolved else sum(len(s.encode()) for s in segments),'log_token_lower':primary,'log_token_upper':measure(text)['tokens'] if unresolved else primary,'unallocated_log_mixed':unresolved,'segment_rules':rules,'segments':[{'start_character':a,'end_character':b,**measure(text[a:b])} for a,b in merged]},segments

def write_table(base,rows):
 base.with_suffix('.json').write_text(json.dumps(rows,indent=2))
 if rows:
  keys=list(dict.fromkeys(k for r in rows for k in r))
  with base.with_suffix('.csv').open('w') as f:
   w=csv.DictWriter(f,fieldnames=keys);w.writeheader();w.writerows([{k:json.dumps(v) if isinstance(v,(dict,list)) else v for k,v in r.items()} for r in rows])

def analyze(batch):
 trialrows=[];toolrows=[];secondary=[]
 reviews=json.loads((batch/'reviews.json').read_text()) if (batch/'reviews.json').exists() else {}
 for p in sorted((batch/'trials').glob('*/*/*/outcome.json')):
  o=json.loads(p.read_text());dest=p.parent
  o.update(reviews.get(o['case']+'/'+o['condition']+'/'+str(o['run']),{}))
  row={k:o.get(k) for k in ['case','condition','run','status','debugging_began','session_exit','elapsed_seconds','verification_exit','verification_seconds','immutable_changes','root_cause_correct','fix_valid']}
  row['evidence']=str(dest.relative_to(ROOT));log=(dest/'failure.log').read_text() if (dest/'failure.log').exists() else ''
  row.update({'log_tokens_lower':0,'log_tokens_upper':0,'log_bytes_lower':0,'log_bytes_upper':0,'log_inspection_calls':0,'search_calls':0,'repeated_log_commands':0,'context_requests':0,'full_file_reads':0,'test_reruns':0,'unallocated_mixed_calls':0,'truncation_markers':0})
  for category in CATEGORIES:row[category+'_tokens']=0
  seen=set();usage=o.get('usage',[])
  for key in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']:row[key]=sum(u.get(key,0) for u in usage) if usage else None
  tools=json.loads((dest/'tool-results.json').read_text()) if (dest/'tool-results.json').exists() else []
  for i,item in enumerate(tools):
   command=item.get('command','');text=item.get('aggregated_output','');cl,segments=classify(command,text,log);body=shell_body(command)
   token=measure(text)['tokens'];row[cl['category']+'_tokens']+=token
   row['log_tokens_lower']+=cl['log_token_lower'];row['log_tokens_upper']+=cl['log_token_upper']
   row['log_bytes_lower']+=cl['log_bytes_lower'];row['log_bytes_upper']+=cl['log_bytes_upper']
   if cl['log_directed']:
    row['log_inspection_calls']+=1
    row['repeated_log_commands']+=int(body in seen);seen.add(body)
    row['search_calls']+=int(bool(re.search(r'\b(?:rg|grep|awk)\b',body)))
    row['context_requests']+=int(bool(re.search(r'\b(?:sed|tail|head)\b|\s-[ABC]\s*\d+',body)))
    row['full_file_reads']+=len(re.findall(r'\bcat\s+(?:--\s+)?[\'\"]?failure\.log\b',body))
   row['test_reruns']+=int(cl['test_execution']);row['unallocated_mixed_calls']+=int(cl['unallocated_log_mixed'])
   truncated=bool(re.search(r'truncated|tokens omitted',text,re.I));row['truncation_markers']+=int(truncated)
   target=dest/'returned-text'/f'{i:03}.txt';target.parent.mkdir(exist_ok=True);target.write_text(text)
   for n,segment in enumerate(segments):(target.parent/f'{i:03}.log-segment-{n}.txt').write_text(segment)
   toolrows.append({'case':o['case'],'condition':o['condition'],'run':o['run'],'index':i,'command':command,'returned_text':str(target.relative_to(ROOT)),'exit_code':item.get('exit_code'),'truncation_marker':truncated,**cl,**measure(text)})
  trialrows.append(row)
  if log:
   methods,matches=extract(log)
   for method,value in methods.items():
    path=dest/'secondary-extractions'/f'{method}.txt';path.parent.mkdir(exist_ok=True);path.write_text(value)
    secondary.append({'case':o['case'],'condition':o['condition'],'run':o['run'],'method':method,'matches':matches,'path':str(path.relative_to(ROOT)),**measure(value)})
 write_table(batch/'trial-results',trialrows);write_table(batch/'tool-results',toolrows);write_table(batch/'secondary-results',secondary)
 print('classified',len(tools) if len(trialrows)==1 else len(toolrows),'tool results;',sum(r['debugging_began'] is True for r in trialrows),'active trials')
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);a=p.parse_args();analyze(ROOT/'investigation/natural-reading'/a.batch)
