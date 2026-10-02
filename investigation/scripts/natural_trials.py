#!/usr/bin/env python3
"""Natural log-reading evaluation. Never writes to baseline raw/trial directories."""
import argparse, concurrent.futures, difflib, hashlib, json, os, pathlib, shlex, shutil, subprocess, tempfile, threading, time
from run import ROOT, JAVA, environment
from trials import execute
PROMPT='This test fails. Diagnose the cause, make the smallest correct implementation change, and verify the fix. Complete test output is available in failure.log.'
GUARD='''Use ./test.sh to run the failing test. Implementation is in investigation/src/test/java/com/ai/token/experiment/Defects.java. Modify only that implementation file. Do not change tests, expectations, build configuration, logging, or test.sh; do not remove functionality or hard-code test results. You may inspect the repository and use debugging tools normally. Do not read outside this workspace except installed tools and the shared Maven dependency cache. Do not use subagents. Explain the diagnosis and verification in your final response.
'''
STOP=threading.Event()
MODEL='gpt-6-astra'
REL=pathlib.Path('investigation/src/test/java/com/ai/token/experiment/Defects.java')
def save(p,data):p.write_text(json.dumps(data,indent=2))
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def snapshot(to):
 shutil.copy2(ROOT/'pom.xml',to/'pom.xml');shutil.copytree(ROOT/'src',to/'src');shutil.copytree(ROOT/'investigation/src',to/'investigation/src')
 p=to/REL;p.write_text('\n'.join(l for l in p.read_text().splitlines() if not l.strip().startswith(('/**','//')))+'\n')
 (to/'AGENTS.md').write_text(GUARD)
def preserve_container_logs(work,dest,phase):
 paths=sorted((work/'target').glob('*.container.*'))+sorted((work/'target').glob('*.retrieval-error.log'))
 if paths:
  folder=dest/(phase+'-container-logs');folder.mkdir()
  for p in paths:shutil.copy2(p,folder/p.name)
  return paths
 return []
def basecmd(case,condition):
 cmd=['mvn','-o','-B','-ntp',f'-Dmaven.repo.local={ROOT}/investigation/.m2','-Pinvestigation','-Dkotlin.compiler.daemon=false','-DtrimStackTrace=false','-Dspring.output.ansi.enabled=never',f'-Dexperiment.case={case}']
 if condition=='conservative':cmd+=['-Dspring.profiles.active=agent','-Dexperiment.deduplicate=true']
 return cmd
def trial(case,condition,repeat,batch,seconds,setup_only=False):
 dest=batch/'trials'/case/condition/str(repeat);dest.mkdir(parents=True,exist_ok=False)
 basic={'case':case,'condition':condition,'run':repeat,'model':MODEL,'reasoning_effort':'low','budget_seconds':seconds}
 if STOP.is_set():
  save(dest/'outcome.json',{**basic,'status':'not_scheduled_quota','debugging_began':False});return
 work=pathlib.Path(tempfile.mkdtemp(prefix='natural-read-'));verify=None
 try:
  snapshot(work);original=(work/REL).read_text();env=environment();env['PATH']=JAVA+'/bin:'+env['PATH']
  cmd=basecmd(case,condition)+['-Dtest=FailureCasesTest','test']
  script='#!/bin/sh\nexport JAVA_HOME='+shlex.quote(JAVA)+'\nunset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG\nexec '+shlex.join(cmd)+' "$@"\n'
  (work/'test.sh').write_text(script);(work/'test.sh').chmod(0o755)
  # Probe in its own Maven invocation, before the measured failing invocation.
  probe=basecmd(case,condition)+['-Dtest=ProfileVerificationTest',f'-Dexperiment.profileArtifact={dest}/profile-verification.txt','test']
  code,_=execute(probe,work,dest/'profile-probe.stdout',dest/'profile-probe.stderr',100,env)
  profile_ok=code==0 and (dest/'profile-verification.txt').exists()
  initial,setup_seconds=execute(['./test.sh'],work,dest/'initial.stdout',dest/'initial.stderr',100,env) if profile_ok else (-1,0)
  container_paths=preserve_container_logs(work,dest,'initial') if profile_ok else []
  raw=(dest/'initial.stdout').read_bytes()+(dest/'initial.stderr').read_bytes() if profile_ok else b''
  (dest/'failure.log').write_bytes(raw);(work/'failure.log').write_bytes(raw)
  identity=json.loads((ROOT/'investigation/cases.json').read_text())[case]['identity']
  identity_ok=initial==1 and identity in raw.decode(errors='replace')
  save(dest/'setup.json',{'probe_command':probe,'profile_verified':profile_ok,'initial_command':cmd,'initial_exit':initial,'identity_verified':identity_ok,'identity':identity,'setup_seconds':setup_seconds,'source_sha256':sha(work/REL),'test_sha256':sha(work/'investigation/src/test/java/com/ai/token/experiment/FailureCasesTest.java'),'failure_sha256':sha(dest/'failure.log')})
  if not (profile_ok and identity_ok):
   save(dest/'outcome.json',{**basic,'status':'setup_failed','debugging_began':False,'profile_verified':profile_ok,'identity_verified':identity_ok});print(case,condition,repeat,'SETUP FAILED',flush=True);return
  if setup_only:
   save(dest/'outcome.json',{**basic,'status':'setup_validated','debugging_began':False,'profile_verified':True,'identity_verified':True})
   print(case,condition,repeat,'SETUP VALIDATED',flush=True);return
  # No probe artifact, reference criteria, previous findings, or author metadata in trial workspace.
  if container_paths:
   logs=work/'container-logs';logs.mkdir()
   for p in container_paths:shutil.copy2(p,logs/p.name)
  shutil.rmtree(work/'target')
  frozen={str(p.relative_to(work)):p.read_bytes() for p in work.rglob('*') if p.is_file() and p.relative_to(work)!=REL}
  (dest/'prompt.txt').write_text(PROMPT);(dest/'AGENTS.md').write_text(GUARD)
  cli=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','-s','workspace-write','-m',MODEL,'-c','model_reasoning_effort="low"','-C',str(work),PROMPT]
  status,elapsed=execute(cli,work,dest/'session.jsonl',dest/'session.stderr',seconds,env)
  transcript=(dest/'session.jsonl').read_text(errors='replace')
  quota="You've hit your usage limit" in transcript or 'usage_limit_reached' in transcript
  if quota:STOP.set()
  events=[]
  for line in transcript.splitlines():
   try:events.append(json.loads(line))
   except ValueError:pass
  commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
  messages=[e['item'].get('text','') for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
  began=bool(commands)
  changed=[p for p,b in frozen.items() if not (work/p).exists() or (work/p).read_bytes()!=b]
  proposed=(work/REL).read_text() if (work/REL).exists() else ''
  patch=''.join(difflib.unified_diff(original.splitlines(True),proposed.splitlines(True),fromfile='a/Defects.java',tofile='b/Defects.java'))
  (dest/'patch.diff').write_text(patch);(dest/'Defects.java').write_text(proposed);(dest/'diagnosis.txt').write_text('\n'.join(messages));save(dest/'tool-results.json',commands)
  verify_code=None;verify_seconds=None
  if began:
   # New pristine verifier; agent-generated target/classes, scripts and expectations are never trusted.
   verify=pathlib.Path(tempfile.mkdtemp(prefix='natural-verify-'));snapshot(verify);(verify/REL).write_text(proposed)
   verify_code,verify_seconds=execute(cmd,verify,dest/'verification.stdout',dest/'verification.stderr',100,env)
   preserve_container_logs(verify,dest,'verification')
   if (verify/'target/surefire-reports').exists():shutil.copytree(verify/'target/surefire-reports',dest/'verification-reports')
  out={**basic,'status':'quota_interrupted' if quota and began else 'not_begun_quota' if quota else 'timeout' if status==124 else 'finished' if began else 'not_begun_error','debugging_began':began,'session_exit':status,'elapsed_seconds':elapsed,'verification_exit':verify_code,'verification_seconds':verify_seconds,'immutable_changes':changed,'patch_present':bool(patch),'profile_verified':profile_ok,'identity_verified':identity_ok,'usage':[e['usage'] for e in events if e.get('type')=='turn.completed' and 'usage' in e],'tool_calls':len(commands),'command':cli,'verification_command':cmd,'workspace':str(work),'root_cause_correct':None,'fix_valid':None}
  preserve_container_logs(work,dest,'agent-final')
  save(dest/'outcome.json',out);print(case,condition,repeat,out['status'],verify_code,round(elapsed,1),flush=True)
 finally:
  shutil.rmtree(work)
  if verify is not None:shutil.rmtree(verify)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--batch',required=True);p.add_argument('--cases',default='01,02,03,04,05,06,07,08');p.add_argument('--repeats',type=int,default=3);p.add_argument('--seconds',type=int,default=120);p.add_argument('--workers',type=int,default=2);p.add_argument('--setup-only',action='store_true');a=p.parse_args()
 batch=ROOT/'investigation/natural-reading'/a.batch;batch.mkdir(parents=True,exist_ok=False)
 jobs=[(c,condition,r,batch,a.seconds,a.setup_only) for r in range(1,a.repeats+1) for i,c in enumerate(a.cases.split(',')) for condition in (['default','conservative'] if (r+i)%2 else ['conservative','default'])]
 save(batch/'schedule.json',{'model':MODEL,'reasoning_effort':'low','budget_seconds':a.seconds,'workers':a.workers,'prompt':PROMPT,'jobs':[{'case':j[0],'condition':j[1],'run':j[2]} for j in jobs]})
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(lambda args:trial(*args),jobs))
