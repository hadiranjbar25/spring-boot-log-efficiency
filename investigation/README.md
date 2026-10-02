# Agent-selected log reading investigation

Read [REPORT.md](REPORT.md) for the revised natural-reading study. The original forced-first-full-read investigation is preserved in [REPORT.full-read.md](REPORT.full-read.md); its raw artifacts and results are unchanged. New evidence is exclusively under `natural-reading/`.

## Reproduce the new trials

Prerequisites: Java 25, Maven 3.9.16, Python 3.9+, the investigation Maven dependencies, an authenticated Codex CLI accepting `gpt-6-astra`, and the local tokenizer environment. Initial dependency installation is described in [README.full-read.md](README.full-read.md). Network access may be needed for setup; Maven trial commands use the existing offline dependency cache.

```sh
export JAVA_HOME=$(/usr/libexec/java_home -v 25)
export INVESTIGATION_JAVA_HOME="$JAVA_HOME"
export PATH="$JAVA_HOME/bin:$PATH"
export TIKTOKEN_CACHE_DIR="$PWD/investigation/.tokenizer-cache"
python3 investigation/scripts/natural_trials.py --batch NEW_BATCH --repeats 3 --workers 2 --seconds 120
investigation/.venv/bin/python investigation/scripts/natural_analyze.py --batch NEW_BATCH
investigation/.venv/bin/python investigation/scripts/test_natural_analyze.py
```

Use a new batch name; trials cannot overwrite earlier artifacts. The report generator `natural_report.py` composes the reviewed `containers` follow-up with the preserved earlier `main` report when container results exist. It does not rewrite historical tables or plots. Review diagnoses, patches and classification before generating conclusions; evaluators put assessments in `reviews.json`, separate from immutable session outcomes. Unknown `fix_valid` is not a completed review. Do not infer correctness solely from a zero test exit.

Both conditions use full Surefire reports. The conservative condition enables the Spring `agent` profile and the fixture-specific duplicate-ownership flag. `agent-reports` is never enabled in these trials. The only task prompt is:

> This test fails. Diagnose the cause, make the smallest correct implementation change, and verify the fix. Complete test output is available in failure.log.

Identical AGENTS.md constraints preserve tests/expectations and identify the allowed implementation file, but prescribe no reading strategy. Full reads, searches and context reads are free choices. The model is `gpt-6-astra`, low reasoning effort, 120 seconds per fresh session. Condition launch order alternates by case/repetition. Stop-on-quota scheduling preserves distinct not-begun and interrupted outcomes.

## Data and primary endpoint

- `natural-reading/main/trials/`: separate profile checks, complete initial stdout/stderr, failure.log, prompt, CLI session, actual tool output, patch, diagnosis and independent verification reports.
- `natural-reading/main/trial-results.csv/json`: cumulative returned-log bounds, strategy counters, separate output classes, success and usage.
- `natural-reading/main/tool-results.csv/json`: every command, classification, returned-body path and recovered log-segment offsets.
- `natural-reading/main/secondary-results.csv/json`: complete-file counts and predetermined windows/boundaries. These are secondary, not assumed model input.
- `natural-reading/main/reviews.json`: evaluator assessments without rewriting raw outcomes.
- `natural-reading/main/schedule.json`: all planned cases, conditions, repetitions, settings and exact task.
- `natural-reading/pilot/`: excluded harness validation; never pooled with main trials.
- `natural-reading/PROTOCOL.md`: exact classification and isolation rules.
- `baselines/full-read/preserved-sha256.json`: integrity manifest for the prior evidence.
- `natural-reading/verification.json`: baseline integrity, instrumentation, configuration and independent-report checks; the final ordinary-suite rerun was blocked by automatic approval-review quota.
- `natural-reading/main/classification-audit.json`: completed command-category review; `raw-manifest.json`: immutable new artifact hashes.

The primary endpoint sums actual returned log-inspection text, including repeated reads. Test execution, source reading, mixed output and other output are reported separately. Exact log segments can be recovered from mixed bodies; uncertain allocation is reported as bounds. Reference counts use real `o200k_base` tokenization, not a byte ratio. Actual session input/cached input/output usage is a separate measurement.

Profile activation is checked before each session by a separate Java test, including the actual Logback encoder. The regex appears only in that separate evidence, not in failure.log. Final verification occurs in another pristine workspace using original tests and only the proposed implementation.

## Docker follow-up

Docker was enabled after the original natural-reading cohort. Real cases 09–10 are recorded separately in `natural-reading/containers/`; setup-only preflights and evaluator repair controls are separate batches. The earlier Docker blocker remains historical evidence. Run fresh container trials with `--cases 09,10 --repeats 3`; use `--setup-only` to validate failure identity without launching agents. The same model, budget, full Surefire and neutral task apply. Container stream files are available for voluntary inspection in each workspace and retained outside it. The unchanged agent sandbox may block Docker access even when independent verification succeeds. See the current report for actual trial dispositions and outcomes.

The pre-container report is preserved in [REPORT.natural-pre-containers.md](REPORT.natural-pre-containers.md). `container_verify.py` checks historical hashes and current evidence; `container_report.py` composes the report after classification and manual patch review.

## Containers and developer usage

Docker is currently unavailable; the exact new probe is in `natural-reading/environment/docker.stderr`. With a working daemon, use the real fixtures:

```sh
docker info
python3 investigation/scripts/natural_trials.py --batch WITH_CONTAINERS \
  --cases 01,02,03,04,05,06,07,08,09,10 --repeats 3 --workers 2 --seconds 120
```

No simulated container logs are used. The same existing readiness bounds and Testcontainers cleanup apply.

For ordinary local debugging, opt in without runner trimming:

```sh
env -u DEBUG mvn -Dmaven.repo.local="$PWD/investigation/.m2" \
  -Dspring.profiles.active=agent test
```

Set Java 25 first. Add `-Dkotlin.compiler.daemon=false` inside the restricted local sandbox if necessary. The profile is not globally enabled, and intentional fixtures remain excluded from the ordinary suite.
