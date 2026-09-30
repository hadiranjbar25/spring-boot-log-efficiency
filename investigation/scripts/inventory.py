"""Index every raw artifact, including invalid/incomplete pilots, without modifying it."""
import csv,hashlib,json,pathlib
from analyze import ROOT,measure
rows=[]
for p in sorted((ROOT/'investigation/raw').rglob('*')):
 if not p.is_file():continue
 relative=p.relative_to(ROOT/'investigation/raw');parts=relative.parts
 batch,case,config,repeat=parts[:4]
 mp=ROOT/'investigation/raw'/batch/case/config/repeat/'metadata.json'
 meta=json.loads(mp.read_text()) if mp.exists() else {}
 raw=p.read_bytes();text=raw.decode('utf-8',errors='replace')
 producer=('experiment runner metadata' if p.name=='metadata.json' else 'Surefire report (may embed application output)' if 'reports' in p.parts else 'container process' if '.container.' in p.name else 'Maven and forked JVM stderr' if p.name=='stderr.log' else 'Maven, Surefire, application and Spring stdout')
 rows.append({'batch':batch,'case':case,'config':config,'run':int(repeat),'path':str(p.relative_to(ROOT)),'producer':producer,'status':'primary' if batch in ('v2','conservative-v2') else 'runtime blocker' if batch=='container-blocker' else 'exploratory / excluded','command':meta.get('command_shell','unavailable: interrupted pilot; see runner and environment progress logs'),'profile_expected':meta.get('profile_expected'),'profile_verified':meta.get('profile_verified'),'identity_verified':meta.get('identity_verified'),'exit':meta.get('exit'),'environment':'investigation/environment/final.json',**measure(text),'bytes':len(raw),'sha256':hashlib.sha256(raw).hexdigest()})
base=ROOT/'investigation/raw-artifact-inventory'
base.with_suffix('.json').write_text(json.dumps(rows,indent=2))
with base.with_suffix('.csv').open('w') as f:w=csv.DictWriter(f,fieldnames=rows[0]);w.writeheader();w.writerows(rows)
print('raw files indexed:',len(rows))
