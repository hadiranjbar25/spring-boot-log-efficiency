# Everyday verification, mixed-suite debugging, and failure diagnosis

This revision adds five passing-operation scenarios and a mostly passing suite with one failure. **Normal-operation volume, observed agent behavior, and failure diagnosis are separate results.** The previous failure-only report is preserved [here](REPORT.failure-only.md); its raw data and tables are unchanged. Its 49.3% non-container and 37.2% container reductions cannot be generalized to everyday verification.

## New study status and primary findings

| Agent state | Planned slots |
| --- | --- |
| finished | 20 |
| not_scheduled_quota | 15 |
| quota_interrupted | 1 |


The schedule plans three independent trials per scenario and logging condition (36 slots), prioritizing the live mixed suite. **21 sessions performed agent work.** Setup/data-collection runs below are not agent trials. Never-begun slots do not count as debugging failures or zero-consumption successes. [Schedule and exact settings](routine-reading/main/schedule.json).

**Capture qualification:** retained `command_execution.aggregated_output` bodies are measurable, but they are not established as complete model-visible tool responses. Some `cat AGENTS.md; ./test.sh` records contain only Maven output and omit the expected initial instructions. The cause is not established. [Concrete capture audit](routine-reading/main/capture-audit.json). Counts below are **retained-event text**, with attribution bounds inside those bodies; they are partial command-output evidence, not guaranteed bounds on complete model-visible consumption. Omitted chunks and possible tool-level truncation cannot be recovered from these events alone. No missing text is filled in from files. Thus percentage differences in retained events do not establish total consumed-output savings. Historical CLI-body figures below should likewise be read as retained text, not independently proven complete model-input totals. Exact full-file matches establish the retained body; they do not resolve hidden protocol/chunk behavior. Raw historical evidence remains unchanged.

| Scenario / arm / repeat | Inspection tokens lower–upper | Test-command tokens | Source tokens | Mixed tokens | Implementation valid | Success assessment | Warning recognized |
| --- | --- | --- | --- | --- | --- | --- | --- |
| container / conservative / 1 | 1937–1937 | 4257 | 1779 | 2413 | True | previous pass; live Docker blocked | True |
| container / default / 1 | 2462–2695 | 11401 | 414 | 4370 | True | previous pass; live Docker blocked | True |
| database / conservative / 1 | 1192–1192 | 0 | 0 | 4225 | True | True | True |
| database / conservative / 2 | 1192–1192 | 0 | 1390 | 1427 | True | None | None |
| database / default / 1 | 1286–1286 | 0 | 0 | 6478 | True | True | True |
| http / conservative / 1 | 1193–1193 | 2506 | 0 | 2945 | True | previous pass; live HTTP blocked | True |
| http / conservative / 2 | 1193–1193 | 2512 | 1390 | 1436 | True | previous pass; live HTTP blocked | True |
| http / default / 1 | 1286–1286 | 2574 | 0 | 3006 | True | previous pass; live HTTP blocked | True |
| http / default / 2 | 1286–1286 | 2586 | 1281 | 1623 | True | previous pass; live HTTP blocked | True |
| integration / conservative / 1 | 1225–1225 | 0 | 0 | 6492 | True | True | True |
| integration / conservative / 2 | 1228–1228 | 1222 | 1390 | 1472 | True | True | True |
| integration / default / 1 | 1351–1351 | 2212 | 0 | 5382 | True | True | True |
| integration / default / 2 | 1354–1354 | 0 | 0 | 6618 | True | True | True |
| mixed / conservative / 1 | 0–0 | 4421 | 1523 | 0 | True | True | True |
| mixed / conservative / 2 | 0–0 | 3547 | 1523 | 0 | True | True | True |
| mixed / default / 1 | 0–0 | 4346 | 1508 | 0 | True | True | True |
| mixed / default / 2 | 0–0 | 4346 | 1508 | 0 | True | True | True |
| unit / conservative / 1 | 869–869 | 869 | 0 | 2520 | True | True | True |
| unit / conservative / 2 | 867–867 | 867 | 0 | 2518 | True | True | True |
| unit / default / 1 | 867–867 | 865 | 0 | 2588 | True | True | True |
| unit / default / 2 | 867–867 | 867 | 0 | 2934 | True | True | True |


Matched comparisons below retain only case/repetition pairs in which both sessions actually began. Output classes remain separate. No complete-file count is substituted for consumed text.

| Scenario | Matched pairs | Inspection tokens D / C | Test-command tokens D / C | Whole mixed tokens D / C |
| --- | --- | --- | --- | --- |
| mixed | 2 | 0–0 / 0–0 | 8692 / 7968 | 0 / 0 |
| unit | 2 | 1734–1734 / 1736–1736 | 1732 / 1736 | 5522 / 5038 |
| integration | 2 | 2705–2705 / 2453–2453 | 2212 / 1222 | 12000 / 7964 |
| http | 2 | 2572–2572 / 2386–2386 | 5160 / 5018 | 4629 / 4381 |
| database | 1 | 1286–1286 / 1192–1192 | 0 / 0 | 6478 / 4225 |
| container | 1 | 2462–2695 / 1937–1937 | 11401 / 4257 | 4370 / 2413 |


Combined **inspection plus returned test output** is the intended new workflow endpoint for this addition, distinct from the old log-only endpoint. Pure test results are counted once; attributable mixed log segments count once; unresolved mixed test/source text broadens bounds to the whole body. Source-only/discovery text is excluded and remains separately reported. The retained-event version prevents a live test run from being mistaken for zero output, but missing emitted chunks still prevent a complete consumption claim.

| Scenario | Pairs | Default retained combined tokens | Conservative retained combined tokens | Retained change | Successful agent reruns D / C |
| --- | --- | --- | --- | --- | --- |
| mixed | 2 | 8,692–8,692 | 7,968–7,968 | -8.3% | 2 / 2 |
| unit | 2 | 3,466–3,466 | 3,472–3,472 | +0.2% | 2 / 2 |
| integration | 2 | 4,917–6,265 | 3,675–4,897 | bounded; see totals | 2 / 2 |
| http | 2 | 7,732–7,732 | 7,404–7,404 | -4.2% | 0 / 0 |
| database | 1 | 1,286–2,572 | 1,192–2,381 | bounded; see totals | 1 / 1 |
| container | 1 | 13,863–14,096 | 6,194–6,194 | bounded; see totals | 0 / 0 |


| Scenario / arm | Log calls | Searches | Context requests | Full-file requests | Exact repeats | Test commands |
| --- | --- | --- | --- | --- | --- | --- |
| mixed / default | 0 | 0 | 0 | 0 | 0 | 4 |
| mixed / conservative | 0 | 0 | 0 | 0 | 0 | 5 |
| unit / default | 2 | 0 | 0 | 2 | 0 | 2 |
| unit / conservative | 2 | 0 | 0 | 2 | 0 | 2 |
| integration / default | 2 | 0 | 0 | 2 | 0 | 3 |
| integration / conservative | 2 | 0 | 0 | 2 | 0 | 2 |
| http / default | 2 | 0 | 0 | 2 | 0 | 4 |
| http / conservative | 2 | 0 | 0 | 2 | 0 | 4 |
| database / default | 1 | 0 | 0 | 1 | 0 | 1 |
| database / conservative | 2 | 0 | 0 | 2 | 0 | 1 |
| container / default | 3 | 1 | 1 | 3 | 0 | 1 |
| container / conservative | 1 | 0 | 0 | 1 | 0 | 1 |


The live mixed-suite result is especially sensitive to reruns: an agent can read a smaller formatted run yet consume more cumulative output by performing additional verification. Interpretation must include both inspection and test-command columns, and any unresolved mixed attribution. Do not add the whole mixed column to attributed log segments a second time.

Implementation validity is independently checked against original tests; it does not imply that an agent completed a successful rerun. Per-trial `agent_rerun_success` and reviews distinguish successful verification from accurate reports of a previous pass followed by a sandbox-blocked attempt. HTTP/container attempts with environment-generated exceptions are not evidence of ordinary successful-operation savings; inspect them separately.

These counts describe the returned strings retained in completed command events. Mixed full bodies overlap attributed segments and are not additive. A zero file-inspection count does not imply zero output consumed: live test-command output is a separate endpoint, particularly for the mixed suite. [Complete per-trial and usage table](routine-reading/main/trial-results.csv), [commands and returned strings](routine-reading/main/tool-results.json). Manual outcomes are separate from raw sessions.

### Outcome interpretation for this collection

Twenty sessions completed and one database session was quota-interrupted after inspection; fifteen slots were never scheduled. All four completed mixed-suite sessions (two per arm) located the sole failure, made only the multiplication repair, and passed all thirteen original tests. Ten completed passing-verification sessions (unit, integration, database) successfully reran their selected tests and correctly reported success. Six HTTP/container sessions correctly distinguished a prior pass from sandbox-blocked live verification; they are not fully successful normal-operation reruns. The interrupted session has no recorded success or warning assessment.

All twenty completed sessions reported the relevant warning(s), including JVM deprecation warnings where there was no application warning. Container default repetition 1 actually read combined and stderr streams, consuming the same warning twice; conservative repetition 1 identified the warning from source inspection and did not read those stream files. Correct recognition therefore does not establish a common reading strategy. The stale-cache message is authored by the fixture and does not implement or prove real fallback behavior. There is no evidence of equivalence from this small sample.

## Design: passing verification and live failure discovery

| Scenario | What runs | Evaluation |
| --- | --- | --- |
| Passing unit | Two arithmetic checks, no Spring startup/log events | Recognize success without application-log evidence; measure any overhead. |
| Passing integration | Real Spring context, bean and refresh; INFO plus WARN | Recognize pass while noticing the nonfatal stale-cache warning and fallback. |
| Successful HTTP request | Real loopback JDK HTTP server and client; GET /price | Retain method/path/status/request ID; assert 200, body 30 and correlation header. |
| Successful database operation | Two real H2 inserts under a unique constraint | Retain both rows and request/operation/table/count without exceptions. |
| Successful container test | Real Alpine readiness, stdout and stderr | Separate host formatting from container-origin text and retain a stderr warning. |
| Mostly passing suite | Twelve passing record checks, one failing price assertion | Locate the failure, repair implementation, rerun all thirteen; do not ignore a coexisting warning. |


Passing tasks receive an already-applied, correct implementation change as `change.diff` and complete previous `test-output.log`. They may rerun tests or inspect any available evidence. Mixed tasks receive **no prepared log or test report**: the agent must start by executing the suite. The initial 12/13 outcome is known only to the evaluator, not stated in the prompt. Source, tests, implementation scope and budgets are identical across logging conditions within each scenario.

Passing prompt:

> A change is ready for verification. Verify the behavior, report whether it succeeds, and note any warnings or unexpected behavior. The change is in change.diff. Complete previous test output is available in test-output.log.

Mixed-suite prompt:

> Run the test suite, investigate any failures, make the smallest correct implementation change if needed, and verify the suite. Report the result and any warnings or unexpected behavior.

The profile is the unchanged conservative Spring `agent` profile, with full Surefire (`-DtrimStackTrace=false`); no aggressive trimming. Separate activation/encoder probes run before initial measurement and before each launched trial. The model is `gpt-6-astra`, low reasoning effort, fresh ephemeral workspace-write sessions with a 120-second budget. Condition order alternates; agent sessions are sequential to avoid shared temporary-file interference. Initial collection can use two workers. This concurrency change and different fixtures preclude causal comparisons across cohorts.

The same neutral workspace instructions identify `./test.sh` and `RoutineService.java` and preserve tests/configuration. Mixed repairs are independently verified in pristine copies with all thirteen original tests; expected counts cannot be changed. Passing judgments separately score correct recognition of success and reported warnings. No passing exit code or log read alone proves either recognition. Docker and loopback sandbox restrictions may affect agent verification; outer-evaluator successes must never be described as agent-side successes. [Full protocol and criteria](routine-reading/PROTOCOL.md).

## Secondary normal-operation output volumes

The following are **complete stored console captures**, not agent consumption. Means use three independent captures per condition. They include Maven, JVM startup/compile warnings, full Surefire and application text; setup profile probes are excluded. The unit fixture emits no application logs but still has build/JVM output.

| Scenario | n default / conservative | Default tokens mean | Conservative tokens mean | Change |
| --- | --- | --- | --- | --- |
| unit | 3 / 3 | 867.7 | 868.0 | +0.0% |
| integration | 3 / 3 | 1,350.0 | 1,226.3 | -9.2% |
| http | 3 / 3 | 1,287.0 | 1,193.3 | -7.3% |
| database | 3 / 3 | 1,289.0 | 1,193.0 | -7.4% |
| container | 3 / 3 | 2,429.0 | 1,937.7 | -20.2% |
| mixed | 3 / 3 | 2,393.0 | 1,997.3 | -16.5% |


Reference tokenizer: tiktoken `o200k_base`; exact Astra attribution is not claimed. Random paths, timestamps, run duration and lifecycle messages can change counts slightly even when formatting is irrelevant. Small unit-test differences must not be interpreted as a profile effect. Mixed-suite figures are initial failing-run volumes, **not normal-operation savings** and not evidence of efficient agent failure discovery. [All counts, bytes, signals and raw paths](routine-reading/main/secondary-results.json).

## Warning and request-context retention

| Scenario | Expected application signals | Signals retained in all valid captures |
| --- | --- | --- |
| mixed | inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database; quantity price | True |
| unit | No application events | True |
| integration | refresh completed request=refresh-7 records=12 status=ok; inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database | True |
| http | request=http-7 method=GET path=/price status=200 total=30 | True |
| database | request=db-7 operation=insert table=users rows=2 status=committed | True |
| container | request=worker-7 readiness=ok | True |


The integration/mixed warning is a controlled `inventory cache stale` event containing request ID, age, threshold and database fallback. HTTP retains method, path, status and request correlation; database retains operation, table, row count and status. The fixture does not exercise production servlet access logging, distributed tracing, high-volume concurrency, or long-running operation after startup. Retention means text remains available; it does **not** mean an agent noticed or correctly interpreted it.

Container stdout (`worker ready`) and stderr (`WARN cache stale request=worker-7 age=61s threshold=60s`) are retained as actual Docker stream files. Those raw streams are separate from host Spring/Testcontainers logging. The combined `.container.log` is an alternate copy, not extra producer volume. [Stream counts and hashes](routine-reading/main/verification.json). The Spring formatter cannot shorten raw container streams; host-prefix savings must not be advertised as container-output compression.

Representative passing output (message payloads preserved under both profiles):

```text
refresh completed request=refresh-7 records=12 status=ok
inventory cache stale request=refresh-7 age=61s threshold=60s fallback=database
request=http-7 method=GET path=/price status=200 total=30
request=db-7 operation=insert table=users rows=2 status=committed
```

These excerpts omit prefixes for presentation. Full returned/produced strings remain in raw artifacts. [Integration default](routine-reading/main/initial/integration/default/1/test-output.log), [integration conservative](routine-reading/main/initial/integration/conservative/1/test-output.log), [container streams](routine-reading/main/initial/container/conservative/1/initial-container-logs/).

## Commands, independent verification, and actual usage

Initial checks retain exact Maven commands, exit status, test counts and profile artifacts in each `result.json`. All mixed initial runs must have 13 tests, exactly one assertion failure, no errors/skips; [reference controls](routine-reading/main/controls/) independently confirm the multiplication repair passes all thirteen under both conditions. The ordinary application test suite passed after these additions; [command/result](routine-reading/ordinary-suite.json). The 13 existing classifier checks and 5 new routine-measurement checks also passed. Ordinary application tests remain separate. Setup measurements are not successful autonomous repairs.

| Scenario / arm / repeat | Input | Cached input | Output | Seconds session / verifier |
| --- | --- | --- | --- | --- |
| container / conservative / 1 | 120566 | 94976 | 570 | 41.83973520799998 / 8.303853541999956 |
| container / default / 1 | 133242 | 115968 | 608 | 45.46230149999997 / 6.667810207999992 |
| database / conservative / 1 | 84492 | 76160 | 359 | 41.46241050000003 / 5.603273584000021 |
| database / conservative / 2 | None | None | None | 17.073431208000102 / 5.120246791999989 |
| database / default / 1 | 92058 | 81152 | 346 | 46.14469779199999 / 5.662062042000002 |
| http / conservative / 1 | 107975 | 97920 | 534 | 62.26673137499995 / 5.6925280000000384 |
| http / conservative / 2 | 107666 | 97664 | 544 | 38.794231999999965 / 5.630787332999944 |
| http / default / 1 | 108480 | 95872 | 553 | 52.53753666699998 / 5.681798916999924 |
| http / default / 2 | 122788 | 109952 | 547 | 43.50477762499986 / 5.788748209000005 |
| integration / conservative / 1 | 92150 | 51712 | 357 | 54.474370041999975 / 5.719320625000023 |
| integration / conservative / 2 | 66773 | 58752 | 405 | 31.708585375000098 / 5.59315704200003 |
| integration / default / 1 | 137730 | 125056 | 463 | 43.74718299999995 / 5.5870331670000155 |
| integration / default / 2 | 92477 | 81408 | 356 | 33.590771292 / 5.538457083999901 |
| mixed / conservative / 1 | 127548 | 114048 | 660 | 95.362915875 / 5.902953958000012 |
| mixed / conservative / 2 | 86431 | 72064 | 576 | 76.16997724999999 / 5.542245958999956 |
| mixed / default / 1 | 105350 | 85760 | 622 | 52.560866292 / 5.528798875 |
| mixed / default / 2 | 88320 | 65536 | 601 | 48.00147770800004 / 5.492556959000012 |
| unit / conservative / 1 | 65362 | 57984 | 393 | 48.058598750000016 / 5.6579480829999795 |
| unit / conservative / 2 | 65404 | 52352 | 405 | 33.737366250000036 / 5.4136360830000285 |
| unit / default / 1 | 65409 | 58112 | 381 | 27.213335750000027 / 5.423332249999987 |
| unit / default / 2 | 65909 | 58240 | 398 | 34.344947166 / 5.167650167000033 |


Recorded command (mixed, default, repetition 1):

```sh
/bin/zsh -lc ./test.sh
```

[Returned body](routine-reading/main/trials/mixed/default/1/returned-text/001.txt)

```text
[ERROR] 
[ERROR] See /private/var/folders/n6/1nrbxjp5209dyzpfgv0hf4p80000gn/T/routine-agent-m4go6dsy/target/surefire-reports for the individual test results.
[ERROR] See dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```

Recorded command (mixed, conservative, repetition 1):

```sh
/bin/zsh -lc ./test.sh
```

[Returned body](routine-reading/main/trials/mixed/conservative/1/returned-text/001.txt)

```text
[ERROR] 
[ERROR] See /private/var/folders/n6/1nrbxjp5209dyzpfgv0hf4p80000gn/T/routine-agent-8a389dgp/target/surefire-reports for the individual test results.
[ERROR] See dump files (if any exist) [date].dump, [date]-jvmRun[N].dump and [date].dumpstream.
[ERROR] -> [Help 1]
[ERROR] 
[ERROR] To see the full stack trace of the errors, re-run Maven with the -e switch.
[ERROR] Re-run Maven using the -X switch to enable full debug logging.
[ERROR] 
[ERROR] For more information about the errors and possible solutions, please read the following articles:
[ERROR] [Help 1] http://cwiki.apache.org/confluence/display/MAVEN/MojoFailureException
```

Recorded command (unit, default, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff; cat test-output.log; cat test.sh'
```

[Returned body](routine-reading/main/trials/unit/default/1/returned-text/001.txt)

```text
[INFO] Finished at: 2026-10-02T17:43:04+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
#!/bin/sh
export JAVA_HOME=/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home
unset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG
exec mvn -o -B -ntp -Dmaven.repo.local=/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2 -Pinvestigation -Dkotlin.compiler.daemon=false -DtrimStackTrace=false -Dspring.output.ansi.enabled=never -Dexperiment.scenario=unit -Dtest=RoutineCasesTest test "$@"
```

Recorded command (unit, conservative, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff; cat test.sh; cat test-output.log'
```

[Returned body](routine-reading/main/trials/unit/conservative/1/returned-text/001.txt)

```text
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  4.722 s
[INFO] Finished at: 2026-10-02T17:43:04+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
```

Recorded command (integration, default, repetition 1):

```sh
/bin/zsh -lc 'pwd; git status --short; cat change.diff; cat test-output.log'
```

[Returned body](routine-reading/main/trials/integration/default/1/returned-text/000.txt)

```text
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.032 s
[INFO] Finished at: 2026-10-02T17:43:16+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
```

Recorded command (integration, conservative, repetition 1):

```sh
/bin/zsh -lc 'pwd; git status --short; cat change.diff; cat test-output.log'
```

[Returned body](routine-reading/main/trials/integration/conservative/1/returned-text/000.txt)

```text
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.048 s
[INFO] Finished at: 2026-10-02T17:43:16+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
```

Recorded command (http, default, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff; cat test-output.log; cat test.sh'
```

[Returned body](routine-reading/main/trials/http/default/1/returned-text/001.txt)

```text
[INFO] Finished at: 2026-10-02T17:43:28+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
#!/bin/sh
export JAVA_HOME=/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home
unset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG
exec mvn -o -B -ntp -Dmaven.repo.local=/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2 -Pinvestigation -Dkotlin.compiler.daemon=false -DtrimStackTrace=false -Dspring.output.ansi.enabled=never -Dexperiment.scenario=http -Dtest=RoutineCasesTest test "$@"
```

Recorded command (http, conservative, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff; cat test-output.log; cat test.sh'
```

[Returned body](routine-reading/main/trials/http/conservative/1/returned-text/001.txt)

```text
[INFO] Finished at: 2026-10-02T17:43:28+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
#!/bin/sh
export JAVA_HOME=/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home
unset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG
exec mvn -o -B -ntp -Dmaven.repo.local=/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2 -Pinvestigation -Dkotlin.compiler.daemon=false -DtrimStackTrace=false -Dspring.output.ansi.enabled=never -Dspring.profiles.active=agent -Dexperiment.deduplicate=true -Dexperiment.scenario=http -Dtest=RoutineCasesTest test "$@"
```

Recorded command (database, default, repetition 1):

```sh
/bin/zsh -lc 'pwd; git status --short; cat change.diff; cat test-output.log'
```

[Returned body](routine-reading/main/trials/database/default/1/returned-text/000.txt)

```text
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.152 s
[INFO] Finished at: 2026-10-02T17:43:40+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
```

Recorded command (database, conservative, repetition 1):

```sh
/bin/zsh -lc 'pwd; git status --short; cat change.diff; cat test-output.log'
```

[Returned body](routine-reading/main/trials/database/conservative/1/returned-text/000.txt)

```text
[INFO] ------------------------------------------------------------------------
[INFO] BUILD SUCCESS
[INFO] ------------------------------------------------------------------------
[INFO] Total time:  5.110 s
[INFO] Finished at: 2026-10-02T17:43:40+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
```

Recorded command (container, default, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff; cat test-output.log; cat test.sh'
```

[Returned body](routine-reading/main/trials/container/default/1/returned-text/001.txt)

```text
[INFO] Finished at: 2026-10-02T17:43:55+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
#!/bin/sh
export JAVA_HOME=/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home
unset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG
exec mvn -o -B -ntp -Dmaven.repo.local=/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2 -Pinvestigation -Dkotlin.compiler.daemon=false -DtrimStackTrace=false -Dspring.output.ansi.enabled=never -Dexperiment.scenario=container -Dtest=RoutineCasesTest test "$@"
```

Recorded command (container, conservative, repetition 1):

```sh
/bin/zsh -lc 'cat change.diff test-output.log test.sh'
```

[Returned body](routine-reading/main/trials/container/conservative/1/returned-text/001.txt)

```text
[INFO] Finished at: 2026-10-02T17:43:55+02:00
[INFO] ------------------------------------------------------------------------
WARNING: A terminally deprecated method in sun.misc.Unsafe has been called
WARNING: sun.misc.Unsafe::objectFieldOffset has been called by org.jetbrains.kotlin.com.intellij.util.containers.Unsafe (file:/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2/org/jetbrains/kotlin/kotlin-compiler-embeddable/2.3.21/kotlin-compiler-embeddable-2.3.21.jar)
WARNING: Please consider reporting this to the maintainers of class org.jetbrains.kotlin.com.intellij.util.containers.Unsafe
WARNING: sun.misc.Unsafe::objectFieldOffset will be removed in a future release
#!/bin/sh
export JAVA_HOME=/Users/hadiranjbar/Library/Java/JavaVirtualMachines/openjdk-25/Contents/Home
unset DEBUG SPRING_PROFILES_ACTIVE LOGGING_CONFIG
exec mvn -o -B -ntp -Dmaven.repo.local=/Users/hadiranjbar/Downloads/java/token.usage/investigation/.m2 -Pinvestigation -Dkotlin.compiler.daemon=false -DtrimStackTrace=false -Dspring.output.ansi.enabled=never -Dspring.profiles.active=agent -Dexperiment.deduplicate=true -Dexperiment.scenario=container -Dtest=RoutineCasesTest test "$@"
```

Provider input/cached input/output, when available, are whole-session values and are never substituted for reference-tokenized returned text. Source reads, reasoning, repeated context, tool framing, cache state and test execution all affect them. Unknown usage stays unavailable.

The confirmatory mixed-suite batch intended to retain model-visible tool-response chunks **never started**: automatic approval review rejected its preparation/launch because the reviewer hit its usage limit. This is distinct from the already-running batch’s model quota interruption. No confirmatory commands, repairs or token counts are claimed. [Exact disposition](routine-reading/confirmatory-status.json).

## Interpretation and limitations

Passing-operation savings must be assessed on their own. Exception-heavy failure reductions cannot establish everyday benefit; pure unit tests offer no application-prefix savings, raw container streams remain separate, and live test output can dominate actual consumption. Preserving known message payloads demonstrates that these controlled warnings/context are not filtered out, but does not prove preservation of every diagnostic signal or agent recognition.

The mostly passing suite is a more realistic discovery task than a supplied failure log, but remains a small synthetic suite with an identified implementation file and only one defect. No equivalence or non-inferiority claim is supported by these sample sizes. **Conclusion:** the conservative profile reduced complete available passing logs by roughly 7–9% for integration/HTTP/database and 20% for host/container-test console output, with effectively no unit-test reduction. Known warning/request payloads and raw container streams remained available. Agents demonstrated correct mixed-suite repair and warning awareness in the observed sample, but the capture gap prevents a complete cumulative-consumption claim; sandbox-blocked verification must remain separate. The active-trial outcomes and capture limitations, not file-volume percentages, determine which aspects of the central question have actually been observed. Missing scenarios/repetitions and unrecorded explanations remain unobserved. Extra reruns can offset shorter formatting; there is no general everyday-workflow saving without evidence from both inspections and live test output.

## Reproduction and evidence

Official documentation describes `--json` as an emitted event stream and `--ephemeral` as disabling rollout persistence; it does not establish full model-visible chunk capture for this installed build. [OpenAI non-interactive mode documentation](https://learn.chatgpt.com/docs/non-interactive-mode). A future confirmatory cohort should retain/audit raw model-visible tool-response chunks before claiming complete consumed-output totals.

```sh
python3 investigation/scripts/routine_trials.py --batch NEW_BATCH --mode collect
python3 investigation/scripts/routine_trials.py --batch NEW_BATCH --mode trials
```

The harness refuses existing raw slots and stops scheduling on quota. Analyzer/report scripts explicitly select the recorded `main` cohort. Do not restart the same schedule over existing sessions; use a new batch after resources are available. [Protocol](routine-reading/PROTOCOL.md), [source fixtures](src/test/java/com/ai/token/experiment/RoutineCasesTest.java), [trial outcomes](routine-reading/main/trial-results.json), [raw integrity checks](routine-reading/main/verification.json), [preserved historical hashes](routine-reading/preserved-sha256.json).

## Earlier failure diagnosis: separate cohorts

The complete [failure-only investigation](REPORT.failure-only.md), [earlier natural-reading report](REPORT.natural-pre-containers.md), and [forced-full-read baseline](REPORT.full-read.md) remain preserved. Their task prompts, per-case findings, commands, returned excerpts, fixes and limitations are available there; no old raw artifacts or result tables were regenerated.

| Earlier cohort | Active trials | Verified repairs default / treatment | Retained-log comparison |
| --- | --- | --- | --- |
| Forced-first-full-read baseline | 16 | 7/8 / 7/8 | Different prompt and aggressive Surefire treatment; not pooled. |
| Natural reading, cases 01–08 | 22 | 8/11 / 8/11 | 49.3% less identifiable retained log text across 11 matched pairs. |
| Natural reading, Docker cases 09–10 | 9 | 4/5 / 4/4 | 37.2% less across 4 matched completed pairs; one unpaired quota interruption. |


These remain failure-diagnosis findings, not evidence about passing work. The historical natural-reading primary endpoint counted retained inspection bodies, while this addition also examines live test output. The newly documented event-capture limitation prevents treating any command-body tally as an independently established complete model-input total. The earlier [raw natural-reading ledger](natural-reading/main/tool-results.json), [Docker ledger](natural-reading/containers/tool-results.json), and [baseline integrity manifest](baselines/full-read/preserved-sha256.json) remain unchanged.
