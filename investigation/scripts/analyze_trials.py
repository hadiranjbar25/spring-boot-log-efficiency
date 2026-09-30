import csv,json,pathlib,re,statistics
from analyze import ROOT,measure

def main(batch='v1'):
 rows=[];tools=[]
 for path in sorted((ROOT/f'investigation/trials/{batch}').glob('*/*/*/outcome.json')):
  o=json.loads(path.read_text());directory=path.parent
  results=json.loads((directory/'tool-results.json').read_text())
  usage=o.get('usage',[])
  row={k:o[k] for k in ('case','config','run','model','session_exit','initial_exit','verification_exit','elapsed_seconds','verification_seconds','tool_calls','patch_present','root_cause_correct','fix_valid')}
  row['immutable_changes']=json.dumps(o['immutable_changes'])
  for field in ['input_tokens','cached_input_tokens','output_tokens','reasoning_output_tokens']:
   row[field]=sum(u.get(field,0) for u in usage) if usage else None
  row['log_related_tool_calls']=0;row['fuller_output_requests']=0;row['log_related_o200k_tokens']=0;row['pure_initial_read_o200k_tokens']=0;row['truncated_tool_results']=0
  for index,item in enumerate(results):
   cmd=item.get('command','');text=item.get('aggregated_output','')
   relevant=bool(re.search(r'failure\.(?:log|stdout|stderr)|(?:cat|tail|head|sed|rg).*\.(?:log|txt)|test\.sh|\bmvn\b|surefire-reports',cmd))
   fuller=bool(re.search(r'failure\.(?:stdout|stderr)|surefire-reports',cmd))
   pure=bool(re.search(r"cat failure\.log['\"]?$",cmd))
   counts=measure(text)
   if relevant:
    row['log_related_tool_calls']+=1;row['log_related_o200k_tokens']+=counts['tokens'] or 0
   if pure:row['pure_initial_read_o200k_tokens']+=counts['tokens'] or 0
   row['fuller_output_requests']+=int(fuller)
   truncated=bool(re.search(r'truncated|tokens omitted',text,re.I));row['truncated_tool_results']+=int(truncated)
   dest=directory/'returned-tool-text'/f'{index:03}.txt';dest.parent.mkdir(exist_ok=True);dest.write_text(text)
   tools.append({'case':o['case'],'config':o['config'],'run':o['run'],'index':index,'command':cmd,'log_related':relevant,'fuller_output':fuller,'pure_initial_read':pure,'truncated_marker':truncated,'path':str(dest.relative_to(ROOT)),**counts})
  row['time_to_external_verification_seconds']=o['elapsed_seconds']+o['verification_seconds']
  rows.append(row)
 for name,data in [('trial-results',rows),('tool-results',tools)]:
  dest=ROOT/f'investigation/{name}-{batch}';dest.with_suffix('.json').write_text(json.dumps(data,indent=2))
  if data:
   with dest.with_suffix('.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=data[0]);w.writeheader();w.writerows(data)
 print('trials',len(rows),'passing verification',sum(r['verification_exit']==0 for r in rows))
if __name__=='__main__': main()
