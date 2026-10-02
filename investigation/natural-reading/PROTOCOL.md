# Natural-reading trial protocol

This protocol changes the reading intervention. The previous full-read investigation remains in [REPORT.full-read.md](../REPORT.full-read.md), with its original raw directories unchanged. Do not combine the prior aggressive treatment with these conservative trials.

## Treatment and task

Default Boot logging versus the final conservative configuration: `spring.profiles.active=agent`, fixture-specific duplicate exception ownership (`experiment.deduplicate=true`), and **full Surefire reports** (`trimStackTrace=false`). Neither condition enables the Maven `agent-reports` profile. Identical implementation and test source; only logging options differ.

The exact user task is:

> This test fails. Diagnose the cause, make the smallest correct implementation change, and verify the fix. Complete test output is available in failure.log.

No reading command, full read, cause, case description, or token-saving goal is supplied. Both workspaces get identical `AGENTS.md` instructions to use `./test.sh`, edit only the implementation, preserve tests/configuration/functionality, avoid outside evaluation data, and explain the diagnosis. The exact file is stored with every session. Naming the implementation file constrains the repair surface; it does not identify the defective method or its repair. This is a small fixture evaluation, not unrestricted repository diagnosis.

Model: `gpt-6-astra`; reasoning effort: `low`; CLI: 0.154.0-alpha.6.2; wall budget: 120 seconds per session. Each invocation is fresh, ephemeral, and ignores user CLI configuration. Two independent workspaces may run concurrently. The ordered schedule alternates default/conservative by case and repetition; concurrency means chronological completion order can differ. Three repetitions × eight available cases × two conditions are planned. Containers are added only when the daemon is available.

## Isolation, setup and evaluation

`natural_trials.py` creates an external temporary directory containing only POM, application source, experimental Java fixtures/resources, neutral instructions, and test.sh. Author comments are stripped identically from Defects.java. It never copies reports, previous trials, the case manifest, reference repairs, or evaluation scripts into that directory. This is instruction/workspace isolation, not protection against an adversarial agent that ignores the prohibition on outside reads.

Before each trial, a separate Maven invocation runs `ProfileVerificationTest`: it checks active Spring profiles and the **actual Logback console encoder pattern** and writes a separate text artifact. Its stdout/stderr are also separate. FailureCasesTest no longer prints the effective logging regex. The failing invocation runs with the intended case and profile; the evaluator checks the known failure identity and nonzero exit before starting the agent. The profile probe also runs for the context-free unit case, where logging has no runtime application effect.

`failure.log` is the complete initial stdout followed by stderr; it has no byte/line cap. Stream concatenation does not assert cross-stream temporal ordering. Maven build output remains included. The agent chooses whether, when, and how much to read. Setup's generated target directory is removed before the session, so there are no probe reports or precompiled classes available. The complete log is retained outside the workspace as immutable evidence.

The Kotlin compiler daemon is disabled for **both** conditions to avoid the known daemon-directory sandbox blocker. Codex otherwise uses its normal workspace-write sandbox. In particular, loopback restrictions can still prevent an agent-run HTTP test; the independent external verifier has access needed for controlled component tests. This environmental friction must not be confused with a logging effect.

After the session, an independent pristine verifier gets only the proposed Defects.java. Tests, configuration and build commands come from the original snapshot, never the agent's target/classes or modified scripts. All initial immutable-file changes are recorded. Original behavioral criteria remain unchanged, including the two-stage HTTP failure; a route-only fix does not pass. Patches and diagnoses require explicit review before `fix_valid` or `root_cause_correct` is set. Green tests alone do not justify functionality-removing changes.

On a quota error, stop scheduling new debugging work. Already-running sessions may finish. Every planned slot gets an outcome, distinguishing not scheduled, model never began, interrupted after activity, setup failure, and actual debugging outcome. No zero-token quota slot enters an active-trial mean. Completed usage records may be absent for interrupted sessions.

## Primary measurement and classification

The primary observable is **cumulative reference-tokenized text actually returned from log inspection**, including repeated reads. Only completed CLI command-event `aggregated_output` strings are used; every string is saved verbatim under `returned-text/`. This observes the CLI-visible tool body, not hidden model protocol wrappers. Do not equate it to whole-session usage.

Classification rules in `natural_analyze.py` are checked against every observed command:

- `log_inspection`: content inspection targeting failure.log, another `.log`, or Surefire reports. Count the full returned body, including grep line numbers and context separators. Filename-only `rg --files` is discovery, not content inspection.
- `test_command`: an invocation of ./test.sh, Maven or the wrapper. Count its returned output separately, even if it contains logs. A deliberate reread of a saved test log is log inspection, not test execution.
- `source_read`: reading implementation/test/build/instruction files without log or test output in that command.
- `mixed`: commands combining those categories or log content with discovery. Retain and count the entire mixed result separately. For `cat failure.log`, simple numbered sed ranges, head or tail, attribute only **literal matches** of the corresponding original log text inside the returned string. Save segment offsets and exact returned substrings. Repeated occurrences at different offsets count repeatedly. Unallocated log-containing mixed output contributes zero to the lower bound and its entire returned token count to the upper bound; never silently label source text as log tokens.
- `other`: discovery, version/status commands and other output. Editing-only operations are reviewed separately; completed file-change events are not shell-output reads.

The primary lower bound sums pure log results and exactly separable log segments from mixed results. The upper bound additionally includes unresolved log-containing mixed result bodies. Segments are tokenized independently at their observed boundaries. Whole mixed-result tokens are a separate overlapping diagnostic view and must **not** be added again to primary log tokens. Tokenization is not perfectly additive across concatenation boundaries.

Counters record log-inspection calls, searches, exact repeated log command strings, context/slice requests, full-file `cat` invocations and test reruns. “Context request” does not assert a larger window was actually returned; inspect the saved command and body. A full-file request may still be tool-truncated; count only the returned body. Unknown or new command forms require review rather than automatic assumptions. Search aliases and reads via non-shell tools are a limitation of the classifier and must be reported if observed.

All reference counts use actual tiktoken 0.14.0 `o200k_base`, not a byte ratio. This tokenizer does not establish exact `gpt-6-astra` log-token counts. Actual Codex session input, cached input, output and reasoning usage remain separate fields; cached input is part of input. Report complete matched pairs for session comparisons and disclose missing usage.

## Secondary measurements

Complete failure.log counts and the unchanged fixed 20-line, filtered 40-line, boundary and exact-dedup extraction policies are secondary. These files are not assumed to have been read. Their instrument-free captures are not directly pooled with baseline captures that printed logging patterns. Raw stdout/stderr and setup/profile records are retained per trial. Independent verifier XML/text reports are retained; setup's generated Surefire report files are not preserved separately from its complete console capture.

## Reproduction

From repository root, with Java 25/Maven and the existing investigation dependencies/tokenizer installed (see [legacy prerequisites](../README.full-read.md)):

```sh
export INVESTIGATION_JAVA_HOME=$(/usr/libexec/java_home -v 25)
export TIKTOKEN_CACHE_DIR="$PWD/investigation/.tokenizer-cache"
python3 investigation/scripts/natural_trials.py --batch NEW_BATCH --repeats 3 --workers 2 --seconds 120
investigation/.venv/bin/python investigation/scripts/natural_analyze.py --batch NEW_BATCH
investigation/.venv/bin/python investigation/scripts/test_natural_analyze.py
```

Use a new batch name; the runner refuses overwrite. On a Docker-capable host add `--cases 01,02,03,04,05,06,07,08,09,10`. Fixture subprocesses have 100-second guards and process-group termination, and containers retain their existing bounded readiness checks/cleanup. Never replace blocked container output with simulated logs.

## Docker follow-up amendment

After Docker activation, cases 09 and 10 use a separate `containers` batch, leaving `main` unchanged. Setup-only preflights confirm real intended failures in both arms, and evaluator-only repair controls confirm original criteria. The runner copies initial real container stdout/stderr and a combined alternate copy into `container-logs/` for voluntary discovery. These files are not mentioned in the neutral task. Raw copies are retained outside workspaces before target cleanup and after verification. Only returned inspection text enters the primary measure; stored stream counts remain secondary. Do not sum combined copies with their component streams as producer volume. Model, budget, sandbox, alternating schedule and full Surefire are unchanged. Record agent Docker permission failures separately from external real-container verification. Reports keep this later cohort separate from the earlier Docker-blocked cohort.
