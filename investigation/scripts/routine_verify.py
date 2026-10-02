#!/usr/bin/env python3
"""Independent fixture, preservation, stream, and evidence checks for the new cohort."""
import hashlib,json,pathlib,xml.etree.ElementTree as ET
from analyze import ROOT,measure
D=ROOT/'investigation';B=D/'routine-reading/main'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
old=json.loads((D/'routine-reading/preserved-sha256.json').read_text());changed=[p for p,h in old.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h];assert not changed,changed
baseline=json.loads((D/'baselines/full-read/preserved-sha256.json').read_text());baseline_changed=[p for p,h in baseline.items() if not (ROOT/p).exists() or sha(ROOT/p)!=h];assert not baseline_changed,baseline_changed
initial=[];sources={};tests=set();streams=[]
for p in sorted((B/'initial').glob('*/*/*/result.json')):
 m=json.loads(p.read_text());d=p.parent;assert m['valid'] and m['profile']['verified'];assert m['counts']==m['expected_counts']
 log=(d/'test-output.log').read_bytes();assert log==(d/'stdout').read_bytes()+(d/'stderr').read_bytes();assert b'EFFECTIVE profiles=' not in log
 assert '-DtrimStackTrace=false' in m['command'] and not any('agent-reports' in x for x in m['command'])
 sources.setdefault(m['scenario'],set()).add(m['source_sha256']);tests.add(m['test_sha256']);initial.append(m)
 for f in sorted(d.glob('initial-container-logs/*.log')):
  streams.append({'path':str(f.relative_to(ROOT)),'sha256':sha(f),'alternate_combined_copy':f.name.endswith('.container.log'),**measure(f.read_text())})
 if m['scenario']=='container':
  folder=d/'initial-container-logs'
  assert (folder/'routine-worker.container.STDOUT.log').read_text()=='worker ready\n'
  assert (folder/'routine-worker.container.STDERR.log').read_text()=='WARN cache stale request=worker-7 age=61s threshold=60s\n'
assert len(initial)==36 and len(tests)==1 and all(len(v)==1 for v in sources.values())
controls=[json.loads(p.read_text()) for p in (B/'controls').glob('*/*/*/result.json')]
assert len(controls)==2 and all(m['valid'] and m['counts']=={'tests':13,'failures':0,'errors':0,'skipped':0} for m in controls)
trials=[json.loads(p.read_text()) for p in (B/'trials').glob('*/*/*/outcome.json')]
assert len(trials)==36
for o in trials:
 if o.get('workspace'):
  assert not pathlib.Path(o['workspace']).exists()
  assert o['profile']['verified']
 if o['debugging_began']:
  assert not o['immutable_changes']
  assert o['verification_counts'] is not None
validation={'full_read_baseline_files_checked':len(baseline),'historical_files_checked':len(old),'changed_historical_files':changed,'initial_runs':len(initial),'all_initial_test_counts_correct':True,'all_initial_profile_probes_passed':True,'source_hashes_by_scenario':{s:sorted(v) for s,v in sources.items()},'test_hashes':sorted(tests),'mixed_reference_controls_passed':len(controls),'container_streams':streams,'raw_container_streams_identical_across_both_conditions':True,'active_agent_trials':sum(o['debugging_began'] for o in trials),'planned_slots':len(trials),'temporary_trial_directories_removed':True}
(B/'verification.json').write_text(json.dumps(validation,indent=2))
files=[*sorted((D/'scripts').glob('routine_*.py')),D/'src/test/java/com/ai/token/experiment/RoutineCasesTest.java',D/'src/test/java/com/ai/token/experiment/RoutineService.java',ROOT/'pom.xml',ROOT/'src/main/resources/application-agent.yml',D/'routine-reading/PROTOCOL.md',D/'scripts/test_routine_measurement.py']
(B/'source-manifest.json').write_text(json.dumps({str(p.relative_to(ROOT)):sha(p) for p in files},indent=2))
raw={str(p.relative_to(ROOT)):sha(p) for root in ['initial','controls','trials'] for p in (B/root).rglob('*') if p.is_file() and 'returned-text' not in p.parts}
(B/'raw-manifest.json').write_text(json.dumps(raw,indent=2))
print('Verified 36 captures, 2 mixed controls,',len(old),'preserved files,',validation['active_agent_trials'],'active agent trials')
