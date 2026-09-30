#!/usr/bin/env python3
"""Raw artifacts are write-once. Run from repository root. No token estimates."""
import argparse, concurrent.futures, hashlib, json, os, pathlib, shutil, signal, subprocess, time
ROOT=pathlib.Path(__file__).resolve().parents[2]
CASES=json.loads((ROOT/'investigation/cases.json').read_text())
JAVA=os.environ.get('INVESTIGATION_JAVA_HOME','/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home')

def environment():
    env=os.environ.copy()
    for key in list(env):
        if key.startswith(('SPRING_','LOGGING_')) or key in ('DEBUG','JAVA_TOOL_OPTIONS','JDK_JAVA_OPTIONS','MAVEN_OPTS'):
            env.pop(key,None)
    env['JAVA_HOME']=JAVA
    return env

def command(case,config,directory):
    cmd=['mvn','-o','-B','-ntp',f'-Dmaven.repo.local={ROOT}/investigation/.m2','-Pinvestigation'+(',agent-reports' if config in ('p4','agent') else ''),'-Dtest=FailureCasesTest',f'-Dexperiment.case={case}',f'-Dexperiment.artifactDir={directory}',f'-Dexperiment.reportDir={directory}/reports','-Dspring.output.ansi.enabled=never']
    if config in ('agent','safe','p1','p2'): cmd += [f'-Dspring.profiles.active={"agent" if config=="safe" else config}']
    if config in ('p3','agent','safe'): cmd += ['-Dexperiment.deduplicate=true']
    # Already compiled once; no compiler output or stale state differences between conditions.
    return cmd+['surefire:test']

def run(case,config,repeat,batch):
    directory=ROOT/f'investigation/raw/{batch}/{case}/{config}/{repeat}'
    directory.mkdir(parents=True,exist_ok=False)
    cmd=command(case,config,directory); start=time.monotonic()
    with (directory/'stdout.log').open('wb') as out,(directory/'stderr.log').open('wb') as err:
        p=subprocess.Popen(cmd,cwd=ROOT,env=environment(),stdout=out,stderr=err,start_new_session=True)
        try: code=p.wait(timeout=100)
        except subprocess.TimeoutExpired:
            os.killpg(p.pid,signal.SIGTERM)
            try: p.wait(timeout=5)
            except subprocess.TimeoutExpired: os.killpg(p.pid,signal.SIGKILL); p.wait()
            code=124
    stdout=(directory/'stdout.log').read_text(errors='replace')
    meta={'case':case,'config':config,'run':repeat,'command':cmd,'command_shell':__import__('shlex').join(cmd),'exit':code,'seconds':time.monotonic()-start,'failure_identity':CASES[case]['identity'],'identity_verified':CASES[case]['identity'] in stdout,'profile_expected': ('agent' if config=='safe' else config) if config in ('agent','safe','p1','p2') else 'default','profile_verified': case=='01' or ('profiles=['+('agent' if config=='safe' else config if config in ('agent','p1','p2') else '')+']') in stdout,'java_home':JAVA,'normalized_environment':'DEBUG, SPRING_*, LOGGING_*, JAVA_TOOL_OPTIONS, JDK_JAVA_OPTIONS, MAVEN_OPTS cleared','environment_path':'investigation/environment/final.json','compiled_fixture_sha256':hashlib.sha256((ROOT/'target/test-classes/com/ai/token/experiment/Defects.class').read_bytes()).hexdigest(),'source_sha256':hashlib.sha256((ROOT/'investigation/src/test/java/com/ai/token/experiment/Defects.java').read_bytes()).hexdigest()}
    (directory/'metadata.json').write_text(json.dumps(meta,indent=2))
    print(case,config,repeat,code,meta['identity_verified'],flush=True)
    return meta

if __name__=='__main__':
    ap=argparse.ArgumentParser(); ap.add_argument('--cases',default=','.join(f'{i:02}' for i in range(1,9))); ap.add_argument('--configs'); ap.add_argument('--repeats',type=int,default=3); ap.add_argument('--batch',default='v1'); ap.add_argument('--workers',type=int,default=1)
    args=ap.parse_args()
    if not (ROOT/'target/test-classes/com/ai/token/experiment/Defects.class').exists():
        raise SystemExit('Compile with -Pinvestigation -DskipTests test first; do not run ordinary Maven builds concurrently.')
    jobs=[(case,c,r,args.batch) for r in range(1,args.repeats+1) for case in args.cases.split(',') for c in (args.configs.split(',') if args.configs else CASES[case]['applicable'])]
    with concurrent.futures.ThreadPoolExecutor(max_workers=args.workers) as pool:
        result=list(pool.map(lambda x:run(*x),jobs))
    if not all(m['identity_verified'] and m['profile_verified'] and m['exit']==1 for m in result): raise SystemExit('Some runs did not trigger expected failure/profile; inspect metadata.')
