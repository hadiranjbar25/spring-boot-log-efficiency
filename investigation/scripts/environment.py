import hashlib,json,os,pathlib,platform,subprocess
from run import ROOT, environment
commands={'java':['java','-version'],'maven':['mvn','-version'],'docker':['docker','version'],'codex':['codex','--version']}
env=environment();env['PATH']=env['JAVA_HOME']+'/bin:'+env['PATH']
result={'platform':platform.platform(),'python':platform.python_version(),'timezone':os.environ.get('TZ','Europe/Berlin'),'commands':{},'sources':{}}
for key,cmd in commands.items():
 p=subprocess.run(cmd,env=env,capture_output=True,text=True,timeout=20)
 result['commands'][key]={'command':cmd,'exit':p.returncode,'stdout':p.stdout,'stderr':p.stderr}
for folder in ['src','investigation/src','investigation/scripts']:
 for p in (ROOT/folder).rglob('*'):
  if p.is_file() and '__pycache__' not in p.parts:result['sources'][str(p.relative_to(ROOT))]=hashlib.sha256(p.read_bytes()).hexdigest()
(ROOT/'investigation/environment/final.json').write_text(json.dumps(result,indent=2))
