#!/usr/bin/env python3
"""Read-only evidence validation; only the derived integrity artifact is written."""
import hashlib,json,pathlib,xml.etree.ElementTree as ET
from natural_trials import ROOT,PROMPT
D=ROOT/'investigation';B=D/'natural-reading/main'
old=json.loads((D/'baselines/full-read/preserved-sha256.json').read_text())
baseline_changed=[p for p,h in old.items() if not (ROOT/p).exists() or hashlib.sha256((ROOT/p).read_bytes()).hexdigest()!=h]
outcomes=[json.loads(p.read_text()) for p in (B/'trials').glob('*/*/*/outcome.json')]
active=[o for o in outcomes if o['debugging_began']]
problems=[];hashes=set();testhashes=set();xmlcounts=[]
for o in active:
 d=B/'trials'/o['case']/o['condition']/str(o['run']);setup=json.loads((d/'setup.json').read_text())
 if not setup['profile_verified'] or not setup['identity_verified']:problems.append(str(d)+': invalid setup')
 if (d/'prompt.txt').read_text()!=PROMPT:problems.append(str(d)+': task mismatch')
 text=(d/'failure.log').read_text()
 if 'EFFECTIVE profiles=' in text or '%replace(%wEx)' in text:problems.append(str(d)+': verification instrumentation in failure.log')
 if '-DtrimStackTrace=false' not in setup['initial_command'] or any('agent-reports' in c for c in setup['initial_command']):problems.append(str(d)+': report configuration mismatch')
 if o['model']!='gpt-6-astra' or o['reasoning_effort']!='low' or o['budget_seconds']!=120:problems.append(str(d)+': model/budget mismatch')
 if o['immutable_changes']:problems.append(str(d)+': immutable changes')
 if hashlib.sha256((d/'failure.log').read_bytes()).hexdigest()!=setup['failure_sha256']:problems.append(str(d)+': raw log changed')
 if (d/'failure.log').read_bytes()!=(d/'initial.stdout').read_bytes()+(d/'initial.stderr').read_bytes():problems.append(str(d)+': incomplete initial capture')
 hashes.add(setup['source_sha256']);testhashes.add(setup['test_sha256'])
 xmls=list((d/'verification-reports').glob('TEST-*.xml'))
 for p in xmls:
  e=ET.parse(p).getroot();xmlcounts.append({'case':o['case'],'condition':o['condition'],'run':o['run'],'tests':int(e.attrib['tests']),'failures':int(e.attrib['failures']),'errors':int(e.attrib['errors'])})
  if int(e.attrib['tests'])!=1:problems.append(str(d)+': unexpected test count')
checks={'baseline_files_checked':len(old),'baseline_changed':baseline_changed,'planned_outcomes':len(outcomes),'active_trials':len(active),'unique_initial_source_hashes':sorted(hashes),'unique_initial_test_hashes':sorted(testhashes),'problems':problems,'verification_reports':xmlcounts,'ordinary_suite_rerun':{'status':'not_executed','reason':'Automatic approval review rejected the command because the approval reviewer hit the account usage limit. Per-trial verification is separate.'}}
(D/'natural-reading/verification.json').write_text(json.dumps(checks,indent=2))
# Original artifact hashes are independent of report/analysis regeneration.
manifest={}
for p in sorted((B/'trials').rglob('*')):
 if p.is_file() and 'returned-text' not in p.parts and 'secondary-extractions' not in p.parts:
  manifest[str(p.relative_to(ROOT))]={'bytes':p.stat().st_size,'sha256':hashlib.sha256(p.read_bytes()).hexdigest()}
(D/'natural-reading/main/raw-manifest.json').write_text(json.dumps(manifest,indent=2))
assert not baseline_changed and not problems and len(hashes)==1 and len(testhashes)==1
print('Verified',len(active),'active trials,',len(old),'unchanged baseline artifacts,',len(xmlcounts),'independent test reports')
