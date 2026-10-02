# Passing verification and live mixed-suite protocol

This addition is separate from failure-only natural-reading and forced-full-read results. It compares default logging against the unchanged conservative Spring agent profile with full Surefire reports. No aggressive trimming is used. Original evidence is protected by `preserved-sha256.json`; the prior report is `../REPORT.failure-only.md`.

## Scenarios and evaluation criteria

| Scenario | Ground truth and criterion |
| --- | --- |
| unit | Two passing arithmetic checks after a quantity-price repair; no Spring startup or application log emission. JVM/Maven warnings can still occur. |
| integration | One passing real Spring context/bean and refresh check; INFO request/count/status and WARN stale-cache/fallback context must remain visible. |
| http | One passing real loopback HTTP GET with status 200, body 30, response request ID, and logged method/path/status/request ID. A tiny JDK HTTP server is used, not a production embedded servlet server. |
| database | One passing H2 operation preserving uniqueness and both inserted records; logged request/operation/table/row count. |
| container | One passing real Alpine readiness check; host startup/status plus actual separate stdout and stderr, including a controlled cache warning. |
| mixed | Thirteen executed dynamic tests, twelve passing and one quantity-price assertion failing initially; original thirteen must all pass after the smallest implementation repair. INFO records and a nonfatal stale-cache warning coexist with the failure. No Docker or network listener is needed in this suite. |

These are small controlled fixtures, not sampled production traffic. Stale-cache warnings are deliberately authored observability signals, not independent spontaneous incidents. All test expectations remain in the test files. The evaluator's scenario descriptions, criteria, reference patches, prior reports and session artifacts are excluded from agent workspaces. Source and tests necessarily reveal behavior when inspected.

## Tasks

Passing scenarios receive exactly:

> A change is ready for verification. Verify the behavior, report whether it succeeds, and note any warnings or unexpected behavior. The change is in change.diff. Complete previous test output is available in test-output.log.

The already-applied change is provided as a diff; the source is correct. Successful verification means correctly recognizing the observed passing result, preserving functionality, and accurately reporting any inability to rerun. Warning recognition is assessed separately from success recognition: it is not inferred from a passing test or reading a warning. Unknown/missing explanations remain unknown. A correct report of a previous pass with a blocked live rerun is recorded as such, separately from `agent_rerun_success`; independent implementation validity must not be confused with agent verification completion. Environment-blocked HTTP/container sessions can contain exception output and are excluded from general claims about successful-operation consumption. Operational warnings must not be represented as a failed test unless the test actually failed.

Mixed suites receive exactly:

> Run the test suite, investigate any failures, make the smallest correct implementation change if needed, and verify the suite. Report the result and any warnings or unexpected behavior.

**No prepared log or report is copied into mixed workspaces.** Agents must run the suite and decide what output to inspect. The evaluator separately checks the initial one-of-thirteen failure before launch. Neither prompt prescribes search commands or full-file reads, mentions token savings, or discloses the defect.

Identical per-arm AGENTS.md identifies `./test.sh` and the editable implementation file, prohibits edits to expectations/configuration and reading outside the workspace, and instructs agents to keep temporary files inside it. Fresh external directories exclude evaluation material. Setup target directories are deleted. Passing scenarios can discover separate container streams in `container-logs/`; streams are not mentioned in the task. File presence is not consumption.

## Settings, repetitions, and quota

Model gpt-6-astra, low reasoning effort, Codex workspace-write, fresh ephemeral session, 120-second budget. Three repetitions per case/condition are planned (36 slots), with condition order alternating by case/repetition. Agent sessions run sequentially, prioritizing the mixed suite. This differs from the earlier cohort's two concurrent agents; no cross-cohort causal claim is permitted. Initial data collection can use two workers. Stop all further scheduling after a quota error. Never-begun, not-scheduled, interrupted, setup failures and genuine debugging failures remain distinct.

All setups separately assert the actual active profile and Logback encoder before measuring logs. Each launched trial repeats this profile check immediately before launch; its output is outside the agent workspace and measured log. Maven has `-DtrimStackTrace=false`, offline dependencies and the Kotlin daemon disabled in both arms. Docker/loopback sandbox failures may block agent reruns even when external checks succeed; record the discrepancy, not a false successful rerun.

## Measures and attribution

1. **Actual inspection text:** cumulative reference-tokenized strings returned by log reads/searches, including repetitions. Preserve commands, bodies, mixed segments and uncertainty bounds. Full reads are observed choices.
2. **Actual test-command output:** separately count returned live test/verification text. In the mixed workflow this can contain the only failure evidence an agent reads; zero file inspection does not mean zero output consumed.
A separately labeled combined verification-output endpoint adds identifiable log-inspection segments and pure returned test-command text exactly once. Mixed test/source bodies have a lower bound containing identified log segments and an upper bound equal to the whole returned body; mixed source-only output is excluded. This is a new endpoint, not a redefinition or recalculation of earlier failure-only results.

3. **Source, mixed and other results:** separate totals; mixed full bodies overlap attributed segments and must not be summed twice. Unknown mixed log attribution gives bounds. Do not claim an overall workflow saving from a log-only endpoint if test output offsets it.
4. **Provider usage:** input, cached input and output, where present; separate from o200k_base reference counts. Do not infer missing usage or attribute every session difference to logging.
5. **Outcomes:** exact diagnosis, independent full-suite repair, correct recognition of passing behavior, warning recognition, immutable changes, elapsed session and independent-verifier time. Manual judgments remain separate from raw outcomes.
6. **Secondary only:** three complete captures per scenario/arm, application event context retention, container streams, test result identities. No agent participation means no primary reading-behavior conclusion, even when secondary volume differences are measurable.

The existing audited classifier handles log files and test commands. For initial passing `test-output.log` attribution, only the classifier's command string is normalized to the legacy `failure.log` token; raw command strings remain unchanged. `change.diff` is likewise normalized to a recognized source filename for classification, so reading a diff alongside a log is mixed, never all-log output. Unknown agent-created mixed files are not reconstructed from later filesystem state. Every actual returned string remains the authority. New forms require a recorded classification audit, not assumed full-file reads. Test run counts include recognized direct verification commands.

## Independent checks and preservation

Fresh verifier copies receive only proposed RoutineService.java with original tests, source/config and full Surefire. Mixed acceptance requires 13 tests, zero failures/errors/skips, a valid implementation repair and no immutable edits. Passing scenarios must preserve their original count and behavior. Two evaluator-only mixed reference controls confirm that correcting multiplication passes all thirteen checks. Stored stdout/stderr are complete; concatenation does not imply interstream ordering.

Container stdout, stderr and the alternate combined copy are retained separately. Do not add the combined copy to its component streams as producer volume. Normal-operation warning retention is checked in emitted messages; that proves availability, not agent awareness. Previous raw evidence and derived tables are never regenerated by this addition.

## Observed capture limitation

During audit, completed `cat AGENTS.md; ./test.sh` bodies started at Maven output and omitted the known initial AGENTS.md prefix. Cause is not established. Ephemeral JSONL does not provide enough evidence to recover possible earlier emitted/model-visible chunks. All counts therefore describe retained completed-event strings; finite lower/upper intervals concern attribution within that captured subset, not total-consumption bounds. Actual model-visible output may also be affected by tool-level truncation; neither a full-consumption lower nor upper bound is established by these event summaries. Do not infer zero for missing chunks, fabricate them from files, or claim a complete consumed-output percentage. Direct full initial-log matches remain evidence of that returned body. New outcomes and warning recognition can still be independently scored. See capture-audit.json and the report qualification.
