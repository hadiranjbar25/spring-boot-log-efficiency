#!/usr/bin/env python3
"""Evaluator-only real-container repair controls; never copied to trial workspaces."""
import pathlib,tempfile,shutil,json
from natural_trials import ROOT,REL,JAVA,snapshot,basecmd,preserve_container_logs,environment,execute
batch=ROOT/'investigation/natural-reading/container-controls'
batch.mkdir(exist_ok=False)
for case in ['09','10']:
 for condition in ['default','conservative']:
  dest=batch/case/condition;dest.mkdir(parents=True)
  work=pathlib.Path(tempfile.mkdtemp(prefix='container-control-'))
  try:
   snapshot(work);p=work/REL;s=p.read_text()
   s=s.replace('"same@example.test"','"user" + id + "@example.test"') if case=='09' else s.replace('service ready','worker ready')
   p.write_text(s);shutil.copy2(p,dest/'Defects.java')
   env=environment();env['PATH']=JAVA+'/bin:'+env['PATH']
   cmd=basecmd(case,condition)+['-Dtest=FailureCasesTest','test']
   code,seconds=execute(cmd,work,dest/'stdout',dest/'stderr',100,env)
   preserve_container_logs(work,dest,'control')
   if (work/'target/surefire-reports').exists():shutil.copytree(work/'target/surefire-reports',dest/'reports')
   (dest/'result.json').write_text(json.dumps({'case':case,'condition':condition,'command':cmd,'exit':code,'seconds':seconds},indent=2))
   print(case,condition,code,flush=True)
  finally:shutil.rmtree(work)
