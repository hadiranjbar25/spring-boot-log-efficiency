#!/usr/bin/env python3
"""Measure routine secondary captures and actual returned text, without filling missing trials."""
import json,pathlib,re
from analyze import ROOT,measure
from natural_analyze import classify,shell_body,write_table,CATEGORIES
from routine_measurement import normalize_command
B=ROOT/'investigation/routine-reading/main'
SIGNALS={'unit':[], 'integration':['refresh completed request=refresh-7 records=12 status=ok','inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database'],'http':['request=http-7 method=GET path=/price status=200 total=30'],'database':['request=db-7 operation=insert table=users rows=2 status=committed'],'container':['request=worker-7 readiness=ok'],'mixed':['inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database','quantity price']}
secondary=[]
for p in sorted((B/'initial').glob('*/*/*/result.json')):
 m=json.loads(p.read_text());d=p.parent;s=(d/'test-output.log').read_text()
 streams=[{'path':str(f.relative_to(ROOT)),**measure(f.read_text())} for f in sorted(d.glob('initial-container-logs/*.log'))]
 secondary.append({k:m[k] for k in ['scenario','condition','run','valid','exit','seconds','counts']}|{'evidence':str(d.relative_to(ROOT)),**measure(s),'signals':{x:x in s for x in SIGNALS[m['scenario']]},'container_streams':streams})
write_table(B/'secondary-results',secondary)
reviews=json.loads((B/'reviews.json').read_text()) if (B/'reviews.json').exists() else {}
rows=[];tools=[]
for p in sorted((B/'trials').glob('*/*/*/outcome.json')):
 o=json.loads(p.read_text());d=p.parent;o.update(reviews.get(f"{o['scenario']}/{o['condition']}/{o['run']}",{}))
 row={k:o.get(k) for k in ['scenario','condition','run','status','debugging_began','elapsed_seconds','verification_exit','verification_counts','verification_seconds','fix_valid','success_recognized','warning_recognized','agent_rerun_success','review']}
 row.update({'evidence':str(d.relative_to(ROOT)),'log_tokens_lower':0,'log_tokens_upper':0,'log_calls':0,'search_calls':0,'context_requests':0,'full_file_requests':0,'repeated_commands':0,'test_commands':0,'unallocated_mixed_calls':0,'verification_output_tokens_lower':0,'verification_output_tokens_upper':0,'actual_total_text_upper':None,'complete_model_tool_response_capture':False})
 for c in CATEGORIES:row[c+'_tokens']=0
 usage=o.get('usage',[])
 for k in ['input_tokens','cached_input_tokens','output_tokens']:row[k]=sum(u.get(k,0) for u in usage) if usage else None
 seen=set();initial=B/'initial'/o['scenario']/o['condition']/str(o['run'])/'test-output.log';log=initial.read_text() if o['scenario']!='mixed' else ''
 commands=json.loads((d/'tool-results.json').read_text()) if (d/'tool-results.json').exists() else []
 for i,item in enumerate(commands):
  command=item['command'];body=item.get('aggregated_output','');normalized=normalize_command(command)
  cl,segments=classify(normalized,body,log);m=measure(body);row[cl['category']+'_tokens']+=m['tokens']
  row['log_tokens_lower']+=cl['log_token_lower'];row['log_tokens_upper']+=cl['log_token_upper'];row['unallocated_mixed_calls']+=int(cl['unallocated_log_mixed'])
  combined_lower=cl['log_token_lower'];combined_upper=cl['log_token_upper']
  if cl['category']=='test_command':combined_lower=combined_upper=m['tokens']
  elif cl['category']=='mixed' and cl['test_execution']:
   combined_upper=max(combined_upper,m['tokens'])
  row['verification_output_tokens_lower']+=combined_lower;row['verification_output_tokens_upper']+=combined_upper
  shell=shell_body(command)
  if cl['log_directed']:
   row['log_calls']+=1;row['repeated_commands']+=int(shell in seen);seen.add(shell)
   row['search_calls']+=int(bool(re.search(r'\b(?:rg|grep|awk)\b',shell)))
   row['context_requests']+=int(bool(re.search(r'\b(?:head|tail|sed)\b',shell)))
   row['full_file_requests']+=len(re.findall(r'\bcat\s+(?:--\s+)?[\'\"]?[\w/.-]+\.log\b',normalized))
  row['test_commands']+=int(cl['test_execution'])
  path=d/'returned-text'/f'{i:03}.txt';path.parent.mkdir(exist_ok=True);path.write_text(body)
  for n,s in enumerate(segments):(path.parent/f'{i:03}.log-segment-{n}.txt').write_text(s)
  tools.append({'scenario':o['scenario'],'condition':o['condition'],'run':o['run'],'index':i,'command':command,'returned_text':str(path.relative_to(ROOT)),**cl,**m})
 rows.append(row)
write_table(B/'trial-results',rows);write_table(B/'tool-results',tools)
print(len(secondary),'complete captures;',sum(r['debugging_began'] for r in rows),'active agent trials;',len(tools),'returned command bodies')

audit=[]
for t in tools:
 body=(ROOT/t['returned_text']).read_text()
 shell=shell_body(t['command'])
 if shell=='cat AGENTS.md; ./test.sh' and body.startswith('[INFO] Scanning for projects...'):
  audit.append({'scenario':t['scenario'],'condition':t['condition'],'run':t['run'],'command':t['command'],'returned_text':t['returned_text'],'observation':'Expected AGENTS.md prefix is absent from completed command body. Cause not established; earlier emitted chunks/model-visible protocol not recoverable from ephemeral JSONL.'})
(B/'capture-audit.json').write_text(json.dumps({'missing_prefix_examples':audit,'actual_model_tool_responses_complete':False,'scope':'Counts describe retained completed-event bodies; finite bounds are attribution bounds within them, not a bound on unobserved chunks. Actual model-visible consumption may differ; these are not guaranteed consumption bounds, and no missing text is reconstructed.','documentation':'https://learn.chatgpt.com/docs/non-interactive-mode'},indent=2))
