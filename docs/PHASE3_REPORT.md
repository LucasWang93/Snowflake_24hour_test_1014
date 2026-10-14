# Phase 3 — Reliability and independent evaluation

Phase 3 only. Original PDF, synchronized documents, Phase 1/2 code/tests/reports and
existing evidence were inspected before changes. No public UI, deployment, full
inventory scan, grant/credential replacement or submission email. Preserved Phase 1
catalog/metadata and all accepted Phase 2 evidence; 54 nonsecret preservation hashes
are in `phase3_preservation.json`. Core canonical SQL, source grounding and CLI remain.

## Implemented hardening

- `control.py`: fail-closed bearer digest authentication, principal-owned sessions,
  atomic SQLite admission, shared sliding-window rates/model-call budget, session
  capacity/TTL, stale-lease quarantine and trusted operator recovery.
- `service.py`: authenticated deployment interface; disposable spawned request
  workers own their state, fresh connector session and cursors. Parent enforces a
  default 55s wall-clock budget, suppresses late results and terminates stuck workers.
  Bounded worker output files are read only after process exit; no partial-pipe hang.
- `agent.py` / `types.py`: agent/state/reset overlap locks, deadline checks after
  model/data calls and before successful state commit, filtered public projection.
- `backend.py`: process/thread ownership, trusted role/secondary-mode/query-tag
  options, visible inherited-role audit, CURRENT_SESSION IDs, safe error attributes
  and existing bounded model/SQL/cleanup. No raw connector error text in diagnostics.
- `planning.py`: original-wording retrieval and literal intent constraints fix the
  observed household-count/source/tenure/poverty failures without physical-ID mappings.
- `evaluation/phase3.py` and immutable `phase3_cases.json`: independent reference SQL,
  saved outcomes, per-case errors/latency, real concurrency/ownership checks.

No new dependency/service. Every public request must enter AgentService; low-level
CLI/evaluator APIs remain trusted operator interfaces. Return `ServiceResult.public`
to a browser; diagnostics/as_dict contain private operational context and must not
be exposed by a future UI.

## Commands and measured verification

| Check | Actual result |
| --- | --- |
| Phase 2 core + Phase 3 offline targeted pytest | 82 passed (58 existing core + 24 new) |
| `bash scripts/verify.sh` | 140 passed / 25 explicitly skipped; Ruff formatting/lint pass, exit 0 |
| First frozen independent run | Job 2848148: 19/25 pass, exit 1; evidence preserved |
| Same-case regression after fixes | Job 2848266: 25/25 pass; final job 2848330: 25/25 pass, concurrency pass, exit 0:0 |
| Existing Phase 2 live regression | Job 2848270: 15/16; final job 2848330: 16/16 pass |
| Preservation/source/credential/traceability audit | Final audit artifact; no secret values read by general inspection |

The 25 offline skips are nine historical Phase 1 and sixteen opt-in Phase 2 live
checks, not passes. Failure-provider/connector tests are explicit mocks; normal
Cortex/data/reference calls and concurrent session check are actual Snowflake.
Phase 1 real tests were not rerun or overwritten. All new live runs have separate
scripts/logs/job IDs/code manifests. Phase 2 regression was explicitly scheduled
`afterany:2848266`, verified with scontrol to avoid warehouse interference.

## Independent methodology and honest first-run result

Case SHA256 `327c865f50a109bb0e12080ebbb3ee00c26064ab7b27b7a4f014dde7fdb11ac8` was frozen
before any agent/model run. Nine factual cases, two new conversations/five turns and
11 negative cases differ from the six Phase 2 development questions. They cover ACS
2019/2020 and decennial redistricting, state/county/CBG scopes and new statistical
families/categories. This is independently authored against metadata/reference SQL,
not an external blind or broadly representative benchmark.

Predeclared golden columns, definitions and allowed mappings are checked against
captured physical schema. Developer-written SQL uses independently specified fields
and LIKE prefixes versus agent SUBSTR; raw reference rows/query IDs are saved.
Expected numeric values are fetched from Snowflake, not assumed from model output.
Checks include exact source/year/geography/field, numeric tolerance rel 1e-12 / abs
1e-9 and actual number text in the answer. All cases/outcomes are saved before exit.

First-run breakdown: **6/9 factual**, **3/5 conversation turns**, **10/11 negative**.
Failures H4/T1a/T1b: model confused household counts with household income, so core
asked clarification. H6: unsupported invented ownership filter. H9: shortened poverty
label did not match its metadata cell, producing safe refusal. N5: missing statistical
product was guessed as decennial and executed an accurate count for an unjustified
product; this was a semantic P1 safety defect, not a fabricated value.

Corrections: preserve literal household-count meaning; household totals require the
Households universe/Total cell; source ambiguity is decided from request/context,
not a model guess; scope-only follow-ups preserve the current metric; retrieve raw
question alongside planned phrases; normalize ownership to verified tenure; remove
only the fixed metadata framing clause for poverty filters, retaining exact categories
and numeric thresholds. Existing bachelor-only, medians/ratios/MOE and SQL guards stay.

**The 25/25 second result is regression, not new held-out accuracy.** Original cases,
first results and code manifest remain unchanged. Phase 2 live job 2848270 exposed
an additional missing-metric educational follow-up (15/16 passed); an explicit
educational-attainment filter/topic rule and captured regression fixed it. Final
combined job 2848330 verifies all 25 Phase 3 cases plus all 16 Phase 2 real tests. Additional genuinely held-out cases
are still needed before broad public-deployment accuracy claims.

## Actual factual results and regression latency

H1: Alabama state, 2020 decennial. H2: vacant units, Autauga County, ACS 2019.
H3: unemployed civilians, Baldwin County, ACS 2019. H4: households, Baldwin County,
ACS 2020. H5: median gross rent dollars, CBG 010010201001, ACS 2019. H6: median
owner-occupied home value dollars, CBG 010010201002, ACS 2020. H7: published population
MOE, CBG 010010201002, ACS 2019. H8: total decennial population, CBG 010010201001.
H9: below-poverty individuals, Autauga County, ACS 2019.

| Case | Selected physical mapping | Independent SQL value | First outcome | Regression outcome | Service seconds |
| --- | --- | --- | --- | --- | --- |
| H1 | 2020_REDISTRICTING_CBG_DATA.P0010001 | 5,024,279 | answered | answered | 14.0527 |
| H2 | 2019_CBG_B25.B25002e3 | 2,096 | answered | answered | 14.2908 |
| H3 | 2019_CBG_B23.B23025e5 | 4,226 | answered | answered | 13.1587 |
| H4 | 2020_CBG_B11.B11001e1 | 84,047 | clarification | answered | 16.6937 |
| H5 | 2019_CBG_B25.B25064e1 | 779 | answered | answered | 14.4717 |
| H6 | 2020_CBG_B25.B25077e1 | 148,600 | unsupported | answered | 13.2040 |
| H7 | 2019_CBG_B01.B01003m1 | 291 | answered | answered | 12.1474 |
| H8 | 2020_REDISTRICTING_CBG_DATA.P0010001 | 575 | answered | answered | 15.8139 |
| H9 | 2019_CBG_B17.B17021e2 | 8,340 | unsupported | answered | 14.3063 |

Full question/answer/definition/geography/release/source, SQL/params, model/data/
reference query IDs and outputs: `../slurm_runs/phase3_independent_v1/results.json`
and `../slurm_runs/phase3_final_v3/results.json`; the intermediate 25/25 run remains
in `phase3_regression_v2`. Final Phase 2 evidence is `phase3_final_v3/phase2_results.json`. No extra data/model discovery.
All answers retain ACS release/unknown interval and statistical/coverage caveats.
Medians and published MOEs are CBG values; state/county non-additive sums are refused.

## Sessions, deadlines, overload and failures

A real concurrent request was refused as overloaded while another worker owned the
shared warehouse lease. A different principal's new conversation did not inherit
state; a cross-owner session request was unauthorized. In the 25-case regression,
**22 connected requests had 22 distinct Snowflake session IDs**.
Accepted workers close their own connections; no unsafe shared cursor/state. The
existing low-level agent/connection additionally rejects concurrent or foreign-thread
use; reset is blocked during a request. SQLite transactions are per-operation,
owner-bound and atomic across local processes (true race tested offline).

Normal service range 0.6816–16.6937s across 25 turns; answered
range 11.4185–16.6937s, median 13.6284s,
nearest-rank sample p95 16.6937s.
Timing starts before authentication/admission/worker/catalog/connection and ends after
cleanup/result/state handling. All measured turns <60s. This small regression sample
is not an SLA/throughput/credit-cost measurement. Original first range 0.6526–13.2936s. Intermediate regression range
0.7471–17.3636s. Final Phase 2 real regression timings are separately recorded in
its 21-turn artifact; they are not included in service/worker latency summaries.

Model/data operations retain 20s/15s caps, statement/queue/network/login bounds and
zero application retries. Worker soft budget reserves cleanup; outer default 55s
plus bounded termination/join waits protects the caller even from a hung provider.
Offline uncooperative-worker, crashed-worker and failed-cleanup cases suppress results
and quarantine subsequent admission. Soft late model/data results cannot commit
state. EOF/SQLite contention/unknown/malformed outputs are safe responses, not crashes.
Connector/Cortex outages were mocked, not induced/reported as actual service outages.
Host OS/local filesystem behavior remains a prerequisite, not a real-time guarantee.

Default shared limits: one active request, 6 per principal / 20 global per minute,
120 reserved model-call units per rolling day, max 128 sessions, TTL 1800s. Evaluation
uses 60/60 per minute and 100 call units to avoid testing accuracy through artificial
rate rejections; shared budget/rate rejection uses deterministic separate tests.
These are call-count controls, not a monetary Snowflake budget. Multi-host deployments
must replace the local store with shared transactional control; separate per-worker
files bypass the invariant. Runtime files are owner-only and Git-ignored.

Quarantine never auto-clears on lease expiration or worker kill because a server
query may remain active. Operator must confirm no active server queries and a
suspended warehouse before trusted recovery; a live lease cannot be cleared.
Recovery is not exposed by AgentService or a public endpoint. Normal connected
requests confirm suspension; local fast refusals do not touch a connection. Final
fixture/reference cleanup SUSPENDED=True.

## Security and effective permissions

Canonical SQL equality enforcement is unchanged and backend-enforced before any
data cursor. Existing adversarial write/system/function/second-statement/table/param/
limit tests pass. New ownership/auth/deadline/public-error/log checks pass; raw SQL,
intent/model output, permission snapshots and error text are not public fields.
Operational logs whitelist request UUID/status/elapsed/health; no token, question,
session ID or arbitrary exception text. Query tags correlate request UUID with
Snowflake diagnostics. Real tokens used in evaluation are ephemeral, never artifacts.

Fresh audits show primary PUBLIC, secondary ALL, direct user data/Cortex access and
inherited SNOWFLAKE_LEARNING_ROLE with CREATE SCHEMA on the learning DB plus
MONITOR/OPERATE/USAGE on the existing warehouse. Primary PUBLIC has 110 visible grants.
Audit follows at most four inherited roles; it does not prove complete account access.
No grantable role-provisioning privileges were demonstrated, so no CREATE/GRANT/revoke
or credential/warehouse changes were attempted. Broad PUBLIC baseline remains.

A dedicated read-only data role/identity is preferred, with separately scoped warehouse
usage/operation and NONE secondary mode when its verified access permits. Constructor
supports migration; [DEPLOYMENT_PERMISSIONS.md](DEPLOYMENT_PERMISSIONS.md) records the
admin-reviewed plan. Direct-user behavior and PUBLIC inheritance follow
[Snowflake access control](https://docs.snowflake.com/en/user-guide/security-access-control-overview).
**No least-privilege credential claim.** Restriction/review requires administrator
provisioning and validation before hosting, without breaking current access.

## Hardening findings / remaining deployment blockers

| Severity | Finding / disposition |
| --- | --- |
| P1 fixed | Shared connector/state and overlapping reset: process ownership, isolated workers/state and core locks |
| P1 fixed | Cross-request warehouse suspension: atomic shared lease, deliberate single active request |
| P1 fixed | Uncooperative model/connector can outlive soft timeout: parent process deadline, termination and quarantine |
| P1 fixed | Model invented product or misread household/tenure/poverty semantics: literal/context/metadata constraints and preserved regression cases |
| P1 before hosting | Broad PUBLIC/user privileges; restricted identity and exclusive application warehouse need administrator review |
| P1 before hosting | TLS/auth token provisioning/revocation, public-adapter output boundary and local durable control storage must be integrated |
| P1 if multi-host | Local SQLite cannot coordinate separate hosts/pods; shared transactional store required |
| P2 | Single active request intentionally reduces throughput; overload and exhausted budgets return safe responses |
| P2 | Operator recovery/alerting must be operationally owned; no automatic unsafe recovery |
| P2 | Statistical unknown fields/interval/coverage, unsupported cities/ratios/cross-year/complex joins and model/lexical recall remain |

No P0 exposure was observed in these tests; this is not a penetration-test or complete
security certification. First held-out failures limit general accuracy claims. New
held-out topics and deployed clean-browser tests are still needed. Public UI,
README/Reflection, private reviewer access and submission email remain unimplemented.
Stop after Phase 3; new-session continuation starts with AGENTS.md and PROGRESS.md.

## Reproduce without infrastructure reset

```bash
.venv/bin/python -m pytest -q tests/phase3 tests/phase2/test_core.py
bash scripts/verify.sh
# New path only; real calls consume trial resources. Use Slurm for a batch run.
RUN_PHASE3_LIVE=1 .venv/bin/python -m evaluation.phase3 --output /tmp/phase3-new-run.json
```

For deployment adapters, construct BearerAuthenticator from server-held SHA256
digests of cryptographically random tokens, SQLiteControl on a private local file,
and AgentService. Call create_session/ask/reset with the authenticated token and
return only result.public. Spawn-based Python callers require the usual
`if __name__ == "__main__"` guard. No public HTTP/UI layer or real demo credentials
were created here. Existing CLI continues as a trusted local operator interface.
