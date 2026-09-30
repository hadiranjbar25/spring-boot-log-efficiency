#!/usr/bin/env python3
"""Fresh external copies; metadata and known fixes never copied into agent workspace."""
import argparse, concurrent.futures, difflib, hashlib, json, os, pathlib, shlex, shutil, signal, subprocess, tempfile, time, threading
QUOTA_STOP=threading.Event()
from run import ROOT, JAVA, environment
MODEL='gpt-6-astra'

def execute(cmd,cwd,out,err,timeout,env):
 start=time.monotonic()
 with open(out,'wb') as o,open(err,'wb') as e:
  p=subprocess.Popen(cmd,cwd=cwd,env=env,stdout=o,stderr=e,start_new_session=True,stdin=subprocess.DEVNULL)
  try: code=p.wait(timeout=timeout)
  except subprocess.TimeoutExpired:
   os.killpg(p.pid,signal.SIGTERM)
   try:p.wait(timeout=5)
   except subprocess.TimeoutExpired:os.killpg(p.pid,signal.SIGKILL);p.wait()
   code=124
 return code,time.monotonic()-start

def trial(case,config,repeat,batch,seconds):
 if QUOTA_STOP.is_set(): return {'case':case,'config':config,'run':repeat,'status':'not_started_quota'}
 dest=ROOT/f'investigation/trials/{batch}/{case}/{config}/{repeat}';dest.mkdir(parents=True,exist_ok=False)
 work=pathlib.Path(tempfile.mkdtemp(prefix='logging-trial-'))
 # Small clean project snapshot, no reports, answers, previous patches or cached classes.
 shutil.copy2(ROOT/'pom.xml',work/'pom.xml');shutil.copytree(ROOT/'src',work/'src')
 shutil.copytree(ROOT/'investigation/src',work/'investigation/src')
 # Remove experiment-author comments, equal across conditions.
 source=work/'investigation/src/test/java/com/ai/token/experiment/Defects.java'
 s=source.read_text();s='\n'.join(l for l in s.splitlines() if not l.strip().startswith(('/**','//')))+'\n';source.write_text(s)
 original=source.read_text()
 env=environment();env['PATH']=JAVA+'/bin:'+env['PATH']; env['KOTLIN_DAEMON_RUN_FILES_PATH']=str(work/'.kotlin')
 cmd=['mvn','-o','-B','-ntp',f'-Dmaven.repo.local={ROOT}/investigation/.m2','-Pinvestigation'+(',agent-reports' if config=='agent' else ''),'-Dtest=FailureCasesTest',f'-Dexperiment.case={case}','-Dspring.output.ansi.enabled=never']
 if config=='agent':cmd+=['-Dspring.profiles.active=agent','-Dexperiment.deduplicate=true']
 cmd+=['test']
 shell='#!/bin/sh\nexport JAVA_HOME='+shlex.quote(JAVA)+'\nunset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG\nexec '+shlex.join(cmd)+' "$@"\n'
 (work/'test.sh').write_text(shell);(work/'test.sh').chmod(0o755)
 # Prepare from same failing state; provide the identical complete-console reading method.
 code,_=execute(['./test.sh'],work,work/'failure.stdout',work/'failure.stderr',90,env)
 (work/'failure.log').write_bytes((work/'failure.stdout').read_bytes()+(work/'failure.stderr').read_bytes())
 shutil.copy2(work/'failure.log',dest/'initial.log')
 frozen={str(p.relative_to(work)):p.read_bytes() for p in work.rglob('*') if p.is_file() and ('target' not in p.parts) and p.name not in ('Defects.java','failure.log','failure.stdout','failure.stderr')}
 prompt='''Fix the failing behavior exercised by ./test.sh in this repository. Start by reading failure.log. You may inspect source and run tools normally. Modify only investigation/src/test/java/com/ai/token/experiment/Defects.java. Do not change tests, build settings, logging, test.sh, expectations, or disable functionality. Make the smallest real behavioral repair; do not hard-code test results or swallow errors. Run ./test.sh to verify. Explain the root cause and repair in your final answer. Full original logs are in failure.stdout and failure.stderr if needed. Do not read outside this workspace except the build dependency cache and installed tools. You have '''+str(seconds)+''' seconds. Do not use subagents.'''
 (dest/'prompt.txt').write_text(prompt)
 cli=['codex','exec','--ignore-user-config','--ephemeral','--skip-git-repo-check','--json','-s','workspace-write','-m',MODEL,'-c','model_reasoning_effort="low"','-C',str(work),prompt]
 status,elapsed=execute(cli,work,dest/'session.jsonl',dest/'session.stderr',seconds,env)
 if "You've hit your usage limit" in (dest/'session.jsonl').read_text(errors='replace'): QUOTA_STOP.set()
 patch=''.join(difflib.unified_diff(original.splitlines(True),source.read_text().splitlines(True),fromfile='a/Defects.java',tofile='b/Defects.java'))
 (dest/'patch.diff').write_text(patch)
 changed=[p for p,b in frozen.items() if not (work/p).exists() or (work/p).read_bytes()!=b]
 # Restore immutable files before independent verification, even if agent altered them.
 for p,b in frozen.items():(work/p).parent.mkdir(parents=True,exist_ok=True);(work/p).write_bytes(b)
 verify,verify_seconds=execute(['./test.sh'],work,dest/'verification.stdout',dest/'verification.stderr',90,env)
 events=[]
 for line in (dest/'session.jsonl').read_text(errors='replace').splitlines():
  try:events.append(json.loads(line))
  except ValueError:pass
 usage=[e['usage'] for e in events if e.get('type')=='turn.completed' and 'usage' in e]
 commands=[e['item'] for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='command_execution']
 messages=[e['item'].get('text','') for e in events if e.get('type')=='item.completed' and e.get('item',{}).get('type')=='agent_message']
 (dest/'diagnosis.txt').write_text('\n'.join(messages))
 (dest/'tool-results.json').write_text(json.dumps(commands,indent=2))
 result={'case':case,'config':config,'run':repeat,'model':MODEL,'reasoning_effort':'low','time_budget_seconds':seconds,'initial_exit':code,'session_exit':status,'elapsed_seconds':elapsed,'verification_exit':verify,'verification_seconds':verify_seconds,'immutable_changes':changed,'patch_present':bool(patch),'usage':usage,'tool_calls':len(commands),'root_cause_correct':None,'fix_valid':None,'workspace':str(work),'command':cli}
 (dest/'outcome.json').write_text(json.dumps(result,indent=2)); print(case,config,repeat,status,verify,elapsed,flush=True)
 # Preserve source and test result; discard only own temporary project to prevent cross-trial leakage.
 shutil.copy2(source,dest/'Defects.java');shutil.rmtree(work)
 return result

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--cases',default='01,02,03,04,05,06,07,08');p.add_argument('--repeats',type=int,default=3);p.add_argument('--batch',default='v1');p.add_argument('--seconds',type=int,default=120);p.add_argument('--workers',type=int,default=2);a=p.parse_args()
 jobs=[(c,config,r,a.batch,a.seconds) for r in range(1,a.repeats+1) for c in a.cases.split(',') for config in (('default','agent') if r%2 else ('agent','default'))]
 with concurrent.futures.ThreadPoolExecutor(max_workers=a.workers) as pool:list(pool.map(lambda x:trial(*x),jobs))
