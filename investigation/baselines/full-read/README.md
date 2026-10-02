# Reproduce the logging investigation

Read [REPORT.md](REPORT.md) for results and limitations. Run commands below from the repository root. Intentional failures live only in `investigation/src/test/java`; ordinary tests exclude the `investigation` JUnit tag even if stale compiled fixtures exist.

## Prerequisites

- Java 25, Maven 3.9.16, Python 3.9+, network access for first dependency/tokenizer download.
- Docker daemon and available `postgres:17.6-alpine` / `alpine:3.22.1` images for cases 09–10. Neither is replaced with a simulation.
- Authenticated Codex CLI accepting `gpt-6-astra` for blind trials. This run used CLI 0.154.0-alpha.6.2.
- Allow loopback HTTP binding for case 07. On this machine the command sandbox required approved execution outside its socket restriction. Kotlin daemon files also required access outside the project.

```sh
export JAVA_HOME=$(/usr/libexec/java_home -v 25)   # macOS; set your JDK path elsewhere
export INVESTIGATION_JAVA_HOME="$JAVA_HOME"
export PATH="$JAVA_HOME/bin:$PATH"
python3 -m venv investigation/.venv
investigation/.venv/bin/pip install -r investigation/requirements-lock.txt
export TIKTOKEN_CACHE_DIR="$PWD/investigation/.tokenizer-cache"
investigation/.venv/bin/python -c 'import tiktoken; tiktoken.get_encoding("o200k_base")'
env -u DEBUG mvn -B -ntp -Dmaven.repo.local="$PWD/investigation/.m2" -Pinvestigation -DskipTests test
```

The Python runner normalizes `DEBUG`, `SPRING_*`, `LOGGING_*`, and Java/Maven injected options across conditions. Build dependencies are cached locally; runner commands use Maven offline mode and fail honestly when a dependency is missing. `setup.py` records the original implementation step and must **not** be rerun; it is not an idempotent bootstrap script. The checked-in POM already contains the integration.

## Practical developer command

Recommended configuration preserves the full test-runner report:

```sh
env -u DEBUG mvn -Dmaven.repo.local="$PWD/investigation/.m2" -Dspring.profiles.active=agent test
```

Set `JAVA_HOME` first. No Spring profile is globally activated. For application launches, use `--spring.profiles.active=agent` or `SPRING_PROFILES_ACTIVE=agent`. P1 and P2 are in `application-agent.yml`. P3 is case-06-specific sole-owner logging and is not a general exception suppression policy. P4 is separately available with `-Pagent-reports`, but is **not recommended as the default** because it removes useful application frames.

One explicitly failing experimental case with the complete conservative configuration:

```sh
env -u DEBUG mvn -Dmaven.repo.local="$PWD/investigation/.m2" -Pinvestigation \
  -Dspring.profiles.active=agent -Dexperiment.deduplicate=true \
  -Dexperiment.case=06 -Dtest=FailureCasesTest test
```

Expected exit: 1. To reproduce the aggressive candidate used in the blind trials, replace `-Pinvestigation` with `-Pinvestigation,agent-reports`.

## Measurements and extraction

Use a new batch name: raw run directories are write-once. Do not run multiple matrix runners against the same `target/` concurrently. Independent trials use separate temporary projects.

```sh
python3 investigation/scripts/run.py --batch reproduce --workers 1
python3 investigation/scripts/run.py --batch reproduce-safe --configs safe --workers 1
investigation/.venv/bin/python investigation/scripts/analyze.py --batch reproduce
investigation/.venv/bin/python investigation/scripts/analyze.py --batch reproduce-safe
```

Default matrix: 114 runs (eight cases, applicable conditions, three repetitions). Extra `safe` condition: 24 runs. Every run records exact command, exit, intended identity, profile evidence and hashes. Sources reset through a fresh JVM; H2 is in-memory and closed; HTTP server uses an ephemeral local port and is stopped; executor is closed. 100-second per-run timeout. No output byte/line cap is applied to raw captures.

Extraction rules live in `analyze.py`: same failure marker regex for both configurations, fixed 20 raw lines including the marker, fixed 40 raw lines then frame removal, boundary-aware failure region, and exact complete-exception-block deduplication. All five outputs derive from the same stdout-then-stderr concatenation. The concatenation does not imply temporal ordering between streams. The report documents information losses and parser limits.

```sh
# Real containers only: first start your Docker daemon.
docker info
python3 investigation/scripts/run.py --cases 09,10 --batch containers-ready --workers 1
investigation/.venv/bin/python investigation/scripts/analyze.py --batch containers-ready
```

Testcontainers closes containers in try-with-resources. Readiness is capped at eight seconds; the container process exits after 45 seconds. The runner has an outer 100-second guard and a five-second termination grace. Testcontainers' cleanup service is left enabled. Separate container STDOUT and STDERR logs are retained by the log consumer; the host console stays separate. On a forcibly terminated JVM, rely on Testcontainers cleanup and inspect remaining labeled containers before removing only those created for this experiment.

## Independent debugging trials

```sh
python3 investigation/scripts/trials.py --batch reproduce --repeats 3 --workers 2 --seconds 120
# analyze_trials.py currently defaults to the recorded v1 batch:
investigation/.venv/bin/python -c 'import sys; sys.path.insert(0,"investigation/scripts"); from analyze_trials import main; main("reproduce")'
```

Each trial creates a fresh external temporary project, compiles the same failing source, supplies a complete `failure.log`, and invokes a new ephemeral Codex session with fixed model, low reasoning effort, tools and time budget. It copies no report, cases.json, earlier patches, reference repairs, or outcome metadata. The prompt prohibits outside reads and permits editing only `Defects.java`. This is protocol isolation, not a security boundary against a malicious agent. Cached Maven dependencies are shared. The model can request original stdout/stderr and rerun tests; all completed command outputs are saved and counted. No informed parent session stands in for a blind trial.

Immutable files are checked and restored before an external verification run. Review every patch and diagnosis before populating `root_cause_correct`/`fix_valid`: a green test is not automatically a valid fix. Session wall time excludes setup and adds external verification separately. Agents may finish early. A timeout can still leave a valid patch; report both outcomes. No resumes or retry sessions are counted as independent trials.

The recorded run exhausted account usage after 12 patches; subsequent slots did not execute. Four supplemental sessions ran after reset, for 16 active trials total (one per case and condition). The current runner stops scheduling after a quota error. The preserved `v1` trial treatment includes P4. The final conservative recommendation omits P4; do not present these trials as a direct test of that revised bundle. To evaluate it, copy `trials.py`, remove `,agent-reports` from its treatment command, use a fresh batch name and repeat the complete protocol.

## Artifacts

- `raw/`: untouched per-run stdout, stderr, metadata, Surefire XML/text reports.
- `extracted/`: derived readings; `results.csv/json`: consolidated final extraction metrics; `results-*.csv/json`: batch-specific extraction metrics; `artifacts-*.csv/json`: producer-specific raw metrics and hashes.
- `trials/`: complete JSONL sessions, returned command text, diagnosis, patch, verification, and usage where available.
- `environment/`: baseline, compilation, runtime probes, progress, version and source manifests.
- `raw-artifact-inventory.csv/json`: all raw files including excluded pilots; `verification.json`: final integrity checks.
- `variants/`: preserved earlier profile versions, including ineffective settings.
- `positive-controls*`: external known-repair checks; never trial input.
- `plots/`: standalone figures; `REPORT.md`: full interpretation.

`o200k_base` counts are actual tokenizer counts, not byte-ratio estimates. This installed tiktoken cannot map `gpt-6-astra`; do not label these as exact Astra model-input token counts. Codex's session usage is separately recorded as actual model-reported usage.
