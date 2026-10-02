#!/usr/bin/env python3
"""Verify new Docker evidence without rewriting historical artifacts."""
import json,hashlib,xml.etree.ElementTree as ET
from analyze import ROOT,measure
D=ROOT/'investigation';B=D/'natural-reading/containers'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
checks={}
for name,p in [('full_read',D/'baselines/full-read/preserved-sha256.json'),('pre_container',D/'natural-reading/pre-container-snapshot/preserved-sha256.json')]:
 old=json.loads(p.read_text());bad=[f for f,h in old.items() if not (ROOT/f).exists() or sha(ROOT/f)!=h]
 checks[name]={'checked':len(old),'changed_or_missing':bad};assert not bad,bad
rows=json.loads((B/'trial-results.json').read_text());active=[r for r in rows if r['debugging_began']]
source=set();tests=set();streams=[];verified=[]
for r in active:
 p=ROOT/r['evidence'];s=json.loads((p/'setup.json').read_text());o=json.loads((p/'outcome.json').read_text());log=(p/'failure.log').read_bytes()
 assert s['profile_verified'] and s['identity_verified']
 assert log==(p/'initial.stdout').read_bytes()+(p/'initial.stderr').read_bytes()
 assert b'EFFECTIVE profiles=' not in log
 assert not o['immutable_changes']
 assert '-DtrimStackTrace=false' in s['initial_command'] and '-Pinvestigation' in s['initial_command']
 assert not any('agent-reports' in c for c in s['initial_command'])
 source.add(s['source_sha256']);tests.add(s['test_sha256'])
 reports=list((p/'verification-reports').glob('TEST-*.xml'));assert len(reports)==1
 x=ET.parse(reports[0]).getroot();assert x.attrib['tests']=='1' and x.attrib['skipped']=='0'
 verified.append({'case':r['case'],'condition':r['condition'],'run':r['run'],'tests':x.attrib['tests'],'errors':x.attrib['errors'],'failures':x.attrib['failures']})
 for f in p.glob('*-container-logs/*.log'):
  streams.append({'path':str(f.relative_to(ROOT)),'alternate_combined_copy':f.name.endswith('.container.log'),**measure(f.read_text())})
 assert not __import__('pathlib').Path(o['workspace']).exists()
assert len(source)<=1 and len(tests)<=1
controls=[json.loads(p.read_text()) for p in (D/'natural-reading/container-controls').glob('*/*/result.json')]
assert len(controls)==4 and all(r['exit']==0 for r in controls)
checks.update({'active_trials':len(active),'source_hashes':sorted(source),'test_hashes':sorted(tests),'independent_reports':verified,'container_stream_counts_secondary':streams,'positive_controls_passed':len(controls),'all_active_profiles_and_failure_identities_verified':True,'complete_initial_captures':True,'immutable_files_unchanged':True,'temporary_trial_workspaces_removed':True})
(B/'verification.json').write_text(json.dumps(checks,indent=2))
raw={str(p.relative_to(ROOT)):sha(p) for p in B.rglob('*') if p.is_file() and 'returned-text' not in p.parts and 'secondary-extractions' not in p.parts and p.name not in ['raw-manifest.json','verification.json','trial-results.json','trial-results.csv','secondary-results.json','secondary-results.csv'] and (p.name!='tool-results.json' or 'trials' in p.parts) and p.name!='tool-results.csv'}
(B/'raw-manifest.json').write_text(json.dumps(raw,indent=2))
print('Verified',len(active),'active trials, four controls, and preserved historical evidence')
