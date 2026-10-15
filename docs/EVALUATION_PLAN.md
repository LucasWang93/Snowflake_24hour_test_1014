# Evaluation plan

Status: Phases 1–4 evidence is preserved; the authenticated public demo is live.
Phase 5 final checks: 191 offline passes /25 opt-in skips, dependency/lint checks,
public HTTPS login and two actual grounded conversational turns. Original independent
19/25 and subsequent 25/25 regression remain distinct. GitHub privacy/access is now operator-reported but not independently verified;
absolute submission metadata remains unresolved; see FINAL_SUBMISSION_AUDIT.md.
Earlier phase sections retain their historical results, including deployment blocks
that were subsequently resolved. No new data discovery or full Cortex evaluation.

## Dimensions
Current checks cover catalog coverage/provenance, exact schema, lexical retrieval,
release/product separation, CBG/FIPS resolution, unsupported aggregations and a
small real-data boundary sample. Phase 2 evaluation adds grounded answers,
statistical accuracy, multi-turn state, ambiguity, SQL security, failure recovery,
latency/resource use and deployed reproduction. These are distinct evaluation scopes.

## Datasets and cases
Completed inputs: `snowflake_inventory.json`, `snowflake_evidence.json`,
`snowflake_metadata.json`, full `phase1_metadata.json`, Census state reference,
`data/semantic_catalog.json`, `phase1_search_results.json` and
`phase1_integration_results.json`. Initial metadata retained only core fields;
Phase 1 full dictionaries supersede it for catalog coverage without deleting it.

Five predefined 2020 search cases: population, median age, household income,
education and employment. Assertions check relevant family within top five, exact
verified identifiers and associated schema; saved top results are not a held-out
benchmark. Real tests use CBGs `010010201001` and `010010201002`, with two source
releases and decennial redistricting. No nationwide scan or broad statistical
accuracy claim follows from this sample.

Phase 2 cases explicitly label metric/universe/year/product/geography, approved
reference SQL and expected result/answer; include counts, medians, ratios, MOEs,
unknown fields, unavailable years, ambiguous counties and unsupported locations.
Keep development cases separate from a representative held-out suite once official
scope is reconciled. Add multi-turn follow-ups/corrections/resets and adversarial
inputs. Data provenance, query IDs, environment, timestamps and seeds must be recorded.

## Metrics and baselines
Phase 1 observed: 59/59 discoverable indicator tables; 16,878 captured physical fields;
16,582/16,582 supplied definitions mapped; 296 missing definitions quarantined; 5/5
predefined retrieval cases pass; nine recorded real tests pass. All 73 object schemas
are retained, but ancillary/derived views without definitions are not semantically
indexed. Semantic coverage is not 100% of physical fields.

Historical local index/load = 3.617s. Single search observations: population 58.391ms,
median age 2.746ms, household income 13.368ms, education 11.261ms, employment 18.505ms.
These are not p95, throughput, general accuracy, or calibrated confidence. Early
ranking failure categories were corrected using generic lexical/title weighting
and definition diversity; no held-out baseline comparison was recorded.

Planned measurable outcomes: approved-case SQL/result/answer correctness, exact
metric/universe/year/geography selection, clarification/refusal correctness,
conversation-state retention/isolation, security-case rejection before execution,
failure recovery and bounded query/response behavior. Measure stage and end-to-end
p50/p95 with warm/cold distinctions, requests/tokens/credits where observable, and
reproduction success. Numeric reference tolerance is relative 1e-12 / absolute 1e-9. The PDF response
limit is strictly under 60s; sample timings do not establish a production SLA.
Representative held-out coverage and credit-cost measurement remain outstanding. Use approved reference SQL as a
correctness baseline and a simple deterministic retrieval/planning baseline where
applicable; capture real comparisons before making improvement claims.

## Requirement-to-test map
All requirement IDs below correspond to the unique register in CHALLENGE_SPEC.md.
Methods awaiting implementation remain planned. PDF/page mapping is now in the
canonical register; prior provisional-table notes are historical.

| Requirement ID | Measurable verification / evidence | State |
| --- | --- | --- |
| SF-1 | Inspect captured context/query ID and connector auth boundary checks | Recorded configuration complete |
| SF-2 | 71 tables + 2 views, 73 successful counts with query IDs | Recorded configuration complete; no repeat scans |
| SF-3 | Three exact DESCRIBE schemas, five rows each; identifier quoting checks | Recorded configuration complete |
| SF-4 | Three nonempty Cortex responses; unknown-model alternative documented; timings/query IDs | Recorded availability complete; not agent quality |
| SF-5 | Stored ALTER/SHOW cleanup confirms suspended; unit double distinguishes failure/already-suspended | Recorded cleanup complete, not fresh warehouse monitoring |
| SF-6 | Redaction, owner-only/symlink config tests; ignore/untracked/mode inspection; doc scan | Configuration boundary complete; full application audit pending |
| P1-1 | Coverage/dictionary reconciliation in `tests/test_semantic_catalog.py`; no unmapped supplied definition | Complete within supplied metadata |
| P1-2 | Five retrieval assertions, exact schema context and five historical real select cases | Complete for defined cases |
| P1-3 | `tests/test_geography.py` leading zeros, unknown year, ambiguous county, null territory; three sampled real joins | Complete for implemented resolver/sample |
| P1-4 | `tests/test_aggregation.py` disjoint count, non-additive/mixed/duplicate/missing/overflow rejection; bounded SQL SUM reference | Complete for implemented policies |
| P1-5 | Exact case, paired MOE, schema drift, quarantine and deterministic rebuild tests | Complete for captured schema |
| P1-6 | Existing offline suite, separate saved nine real test outcomes, unchanged Phase 1 report | Complete for Phase 1 |
| AS-1 | Golden questions: approved SQL/reference result and answer must match metric, universe, year, product and geography; unsupported statistics refuse | Phase 2 golden/reference tests implemented |
| AS-2 | Scripted follow-ups change geography/year/metric explicitly; corrections/reset work; two sessions never share state | Phase 2 three-scenario tests implemented |
| AS-3 | Bounded real Cortex intent/catalog-choice calls; answers deterministic plus routing inspection; validate chosen IDs/structured outputs; retain existing availability evidence | Phase 2 real planner/choice and mock failure tests implemented |
| AS-4 | Reject write/DDL/multiple statements/system access/noncatalog IDs and prompt injection before SQL execution; clarify ambiguous county/year/universe; test timeout, empty result, unknown model, retry bounds and safe cleanup | Phase 2 canonical SQL rejection and mock recovery tests implemented |
| AS-5 | Public login page, invalid/valid reviewer auth, actual grounded multi-turn, UI/server credential separation | Phase 4 external acceptance passed; final Phase 5 HTTPS/login/two-turn smoke passed |
| AS-6 | Representative held-out end-to-end cases, reference-query comparisons, failure taxonomy, measured latency and resource/cost summary | First Phase 3 independent 19/25; regression 25/25; Phase 4 hosted acceptance; broader fresh held-out work remains |
| AS-7 | Fresh checkout with documented dependencies and exact setup/run/test/example commands succeeds | Final README reviewed; existing real Docker build and current offline example/checks; no new clean local install claim |
| AS-8 | Reflection matches PDF format and accurately explains actual design, evidence, limits and tradeoffs | Root REFLECTION.md four-topic/evidence review complete |
| AS-9 | Exact reviewer accounts have required effective repository access | UNVERIFIED: operator reports private + all 11 invitations; current API404 cannot independently confirm |
| AS-10 | PDF-confirmed recipient/deadline/content/links; authorized send and receipt | Pending submission check; no email sent |
| AS-11 | Five-page PDF reconciliation, 30 unique IDs with page/source and nonempty verification | Complete; absolute receipt/recipient remain open |
| AS-12 | Each real turn measured including model, query and cleanup; assert <60s | Phase 2 live assertions; no production SLA |
| AS-13 | Local rejection plus structured domain classification; unsafe/off-topic cases produce no data SQL | Phase 2 unit/live cases |
| AS-14 | Existing Marketplace evidence and actual core data queries; fallback unused | Source access verified |
| AS-15 | All implementation files included in final private-repo submission manifest | All implemented source/config included in checkpoints; final docs prepared |
| AS-16 | Full catalog family/schema tests, dynamic candidates, exact filters, undefined fields quarantined | Partial: 296 unknown fields and unsupported calculations |
| AS-17 | `scripts/deployment_smoke.py` with two fresh browser contexts, HTTPS URL and private token files; separate post-SSH probe | Phase 4 actual external acceptance/restart passed; final Phase 5 two-turn smoke passed |
| AS-18 | CLI callbacks and Streamlit status feedback, disabled busy input, graceful refusals | Actual deployed loading/provenance observed in Phase 4; public follow-up reconfirmed |

SQL security is enforced by canonical recompilation and exact equality, beyond
quoting alone. Implemented negative cases include
DDL/DML/COPY, multiple statements, unapproved functions/system schemas, hidden object
references, excessive results/resources and instructions to ignore catalog policies.
Only the canonical typed query language is executable; backend validation occurs
before connecting or obtaining a cursor. No arbitrary model SQL is accepted.

Failure-recovery evaluation should use deterministic mocks for outages/rate limits
first, label them as mocks, then use bounded authorized real cases where useful.
Do not retry unsupported models or unsafe operations indiscriminately. Test returned
errors, session consistency, credential redaction and warehouse cleanup separately.
Public deployment tests and end-to-end agent accuracy require the actual implementation;
they are not replaced by local catalog tests.

## Commands
Completed historical commands are preserved here for reproducibility, not rerun by
this sync: existing probe inventory/full modes, Phase 1 metadata-only collector,
`python -m census_catalog build`, and
`.venv/bin/python -m pytest -q tests/test_phase1_live.py --snowflake-live`.
The full configuration probe includes scans/model calls; do not use it for this sync.

Safe offline verification:
```bash
.venv/bin/python -m pytest -q
bash scripts/verify.sh
bash scripts/preflight.sh
```
No `--snowflake-live` option means those nine live tests skip before loading credentials
or opening a connection. A future live rerun requires appropriate scope/authorization;
it consumes remote resources and overwrites its live evidence artifact.

Phase 2 commands (do not rerun full discovery or prior Phase 1 live suite):
```bash
.venv/bin/python -m pytest -q tests/phase2/test_core.py
.venv/bin/python -m census_agent --help
.venv/bin/python -m census_agent --question "Using ACS 2020, what is the total population of Autauga County, Alabama?" --json
# Opt-in, credit-consuming; use a fresh evidence path for each run:
RUN_PHASE2_LIVE=1 PHASE2_EVIDENCE=/tmp/phase2-new-run.json .venv/bin/python -m pytest -q -s tests/phase2/test_live.py
```
The actual durable live submissions and results are recorded in PHASE2_REPORT.md
and `slurm_runs/phase2_core_v1` / `phase2_core_v2`. Public UI/deployment evaluation
commands remain pending. CLI exit 2 denotes clarification/refusal, not a crash.

## Observed results
| Check | Evidence / actual outcome | Scope / limitation |
| --- | --- | --- |
| Configuration data access | `snowflake_evidence.json`: 73/73 counts, three schemas/samples, context AWS_CA_CENTRAL_1 | Historical configuration, not refreshed in this sync |
| Cortex availability | llama3.1-70b 0.741s; llama3.3-70b 1.875s; mistral-7b 0.746s; gemma2-9b unknown model after 20.953s | Single greeting per model, not accuracy/p95; legacy Mistral models not called |
| Catalog/search | Metadata/catalog plus `phase1_search_results.json`: coverage and five cases above | Captured metadata and predefined cases, not arbitrary question correctness |
| Actual Phase 1 integration | `phase1_integration_results.json`: 9 passed, 10 bounded queries; 2026-10-14T16:32:35.795402Z to 16:32:54.562367Z | Five field selects, three geography joins, two-query sum check; not rerun |
| Statistical real reference | Guarded B01001e1 sum = SQL SUM = 1941.0 for the two tested CBGs | Not a national population total or median/MOE validation |
| Local verification | Phase 1 report: Ruff pass, 58 passed / 9 skipped; sync independently reran `pytest -q`: 58 passed / 9 skipped, exit 0 | 44 Phase 1 offline tests plus 14 connector helper tests; live skips are not passes |
| Warehouse cleanup | Recorded ALTER/SHOW confirms SUSPENDED, last live ALTER ID `01c7ba60-3204-bd57-0008-3d1a000176de` | Last observed state; no new warehouse query in sync |
| Earlier preflight | Phase 1 report: exit 2 for uncommitted work/full-homework pending items | Not full homework readiness or a catalog test failure |
| Sync preflight | `bash scripts/preflight.sh`: Ruff pass, 58 passed / 9 skipped; exit 2 for unchecked delivery tasks and uncommitted work | Document structure checked; full homework intentionally remains incomplete; no remote calls |

Some connector-helper tests mock cursors/connections; offline catalog tests use captured
metadata and synthetic malformed inputs. Only saved integration evidence documents
actual Snowflake SQL. That historical sync did not run agent/multi-turn/SQL-security tests. Current Phase 2
tests are recorded separately below; public UI/deployment tests remain unperformed.

## Failure analysis and limitations
Retain prior findings: unsupported gemma2-9b; supplied region differed from actual
AWS_CA_CENTRAL_1; 73 objects were 71 tables + 2 views; initial ALTER on an already
suspended warehouse errored, with SHOW confirming suspension. A third-party X509
deprecation warning occurred in the live run; no package change was made for it.

Current limits: 296 undefined fields, unknown ACS survey interval, conservative
aggregation blocking, sampled rather than nationwide geography validation, missing
city/place/crosswalk support, no general retrieval benchmark and no held-out agent
baseline. Distinguish metadata coverage from semantic correctness and lexical rank
from confidence. Classify future failures as retrieval/schema, universe/product/year,
geography, aggregation, SQL safety, conversation state, grounding, provider failure,
latency/resource, deployment or reproduction, attaching case IDs and actual evidence.

Historical documentation-sync audit: 23 unique provisional requirement IDs have nonempty
source/implementation/verification/status and matching evaluation rows. All six
Phase 1 IDs carry bounded completion; future IDs are planned/pending and related
delivery tasks remain unchecked. Referenced artifacts exist. Nonsecret file hashes
confirm only the five requested documents changed; code/configuration/skills/evidence
were preserved. Documentation credential-pattern checks found no private-key, token
or password-assignment patterns; no credential values were read. Ignore/tracking/mode
inspection confirms .env is excluded and owner-only. These checks do not certify
complete official-PDF coverage or constitute a full application security audit.

## Official PDF and Phase 2 evaluation update
AS-12: hard <60s normal response check, measured end-to-end per live turn.
AS-13: off-topic/inappropriate/adversarial intent must refuse before data execution.
AS-14: reuse verified Marketplace source; no fallback/data rediscovery.
AS-15: final code packaging/manifest review remains pending.
AS-16: dynamic full-catalog resolution plus explicit unsupported metadata/join gaps.
AS-17: clean deployed-demo test remains pending outside Phase 2.
AS-18: CLI progress/fast-fail checks now; deployed interactivity later.
AS-11: PDF reconciliation complete; receipt timestamp and submission recipient remain
open operational inputs. AS-8 checks all four reflection topics and AI-use discussion.
AS-9 must verify private repository and all 11 PDF handles; AS-10 email within 24 hours
of receipt. No access change or message is sent during Phase 2.
Phase 2 implemented evaluation: >=5 metric families, >=3 multi-turn scenarios, independent
reference SQL, unsafe-SQL nonexecution, semantic distinction/count-vs-median/MOE,
Cortex/Snowflake error paths, actual role grants and per-stage/end-to-end timings.

## Completed Phase 2 evidence — 2026-10-14
- 58 deterministic Phase 2 tests passed; model/service doubles explicitly mocked.
- Full `bash scripts/verify.sh`: 116 passed, 25 opt-in live skips, Ruff pass, exit 0.
- Final real run: job 2847530, 16 passed, 21 turns (six golden questions, three
  three-turn scenarios, six unsupported/adversarial questions) plus backend SQL
  tampering rejection. Independent reference SQL output/answer-number checks passed.
- Failed runs retained: 2847474 (13 passed / 2 failed), 2847509 (15 / 1),
  2847520 (15 / 1); root causes and regressions documented in PHASE2_REPORT.md.
- Per-turn latency, model/data/reference query IDs, token usage, visible effective
  grants and final SUSPENDED state: `../slurm_runs/phase2_core_v4/results.json`.
- Development cases are not held-out/general accuracy, concurrency throughput,
  credit-cost measurement or a production SLA. No UI/deployment evaluation ran.
- 30 unique canonical IDs have corresponding evaluation methods; old 23-ID audit
  above is explicitly historical. Phase 1/configuration preservation hashes pass.

## Phase 3 independent and operational evaluation
Frozen `evaluation/phase3_cases.json` SHA256:
`327c865f50a109bb0e12080ebbb3ee00c26064ab7b27b7a4f014dde7fdb11ac8`.
Distinct from six Phase 2 golden questions: nine factual cases (households, vacant
units, unemployment, rent, property value, poverty, population/MOE), two conversations
with five turns, eleven negative cases; 2019/2020, CBG/county/state, ACS/decennial.
Independent predeclared golden columns and developer-written SQL check numbers,
physical metric/source/year/geography and answer text. All outcomes are saved before
acceptance checks; source/model/data query IDs and cleanup remain inspectable.

First untouched held-out-from-development run: job 2848148, 19 passed / 6 failed.
Stand-alone factual 6/9, conversation turns 3/5, negative 10/11. Its 22 completed
model/data connections had distinct CURRENT_SESSION IDs. One ambiguous population
request silently chose decennial: its data was real but the product was unjustified.
The other failures safely clarified/refused rather than return wrong numbers.
Concurrent real-session admission/ownership checks passed; final warehouse suspended.

After targeted fixes, the same set is a REGRESSION set, job 2848266; do not report
its result as fresh held-out accuracy. Original JSON/questions/expected fields and
first-run evidence remain unchanged. Existing Phase 2 real regressions run separately
under job 2848270 into a new artifact, after the Phase 3 job to avoid shared-warehouse
interference. Source/code manifests accompany every run; no full inventory rescans.

Offline tests use explicitly mocked workers/providers for hard hangs/crashes,
connector/Cortex failures, soft deadline state rollback, safe errors/logging, busy
SQLite, authentication, cross-owner/reset, shared rate/call budgets, lost leases,
quarantine/recovery, capacity/TTL, core overlaps and backend ownership. A true
multi-process SQLite race must admit exactly one requester. Public output must omit
raw diagnostic data and credentials; canonical SQL regressions remain intact.

Latency is measured at AgentService ingress through admission/worker startup/catalog/
connection/inference/SQL/cleanup/result transfer. Target normal turns <60s; default
parent deadline 55s plus bounded termination waits. Report per-case and sample-only
summary; no throughput, SLA, broad recall or Snowflake-credit measurement claim.

Commands:
```bash
.venv/bin/python -m pytest -q tests/phase3 tests/phase2/test_core.py
bash scripts/verify.sh
# Credit-consuming opt-in; new output path only; use durable Slurm for batch runs.
RUN_PHASE3_LIVE=1 .venv/bin/python -m evaluation.phase3 --output /tmp/phase3-new-results.json
```
Phase 3 outcomes belong in PHASE3_REPORT.md. Public UI, deployed authentication/TLS,
restricted identity migration, clean hosted/held-out retesting and complete delivery
remain separate pending checks under AS-4/AS-5/AS-6/AS-7/AS-9/AS-12/AS-17.

## Final Phase 3 verification — 2026-10-14
Job 2848330: COMPLETED/exit 0:0, 25/25 Phase 3 regression cases and 16/16 original
Phase 2 real tests; real concurrent owners/session isolation pass. All final service
turns 0.6816–16.6937s including full request lifecycle; Phase 2 direct-core turns
0.2810–11.2684s measured separately. Final fixtures confirmed SUSPENDED.
Full offline verification: 140 passed / 25 explicit live skips, Ruff pass, exit 0.

Intermediate Phase 2 live job 2848270 had 15/16: a category-only education follow-up
omitted metric; explicit educational-attainment intent/context handling and a
captured regression fixed it. Its evidence remains. Initial frozen first-run 19/25
is still the held-out result; later 25/25 runs are regressions. Final source hashes
are bound to the combined run manifest. No genuine outage, p95/SLA/throughput/cost
or complete deployed-security certification is inferred from these cases.

## Phase 4 verification scope

New tests: `tests/phase4/test_web.py` (Streamlit AppTest + actual local control/worker
processes with explicitly mocked Census provider), `test_deployment.py` (private
credential provisioning, public-URL checks and configuration boundaries). Covers
login/invalid tokens, multi-turn/reset/logout, independent owners, provenance/private
output, unavailable configuration/provider and unchanged shared rate limits; rejected
legacy credentials/roles/HTTP/unsafe key/control paths. These are offline tests.

External acceptance plan: public page + reviewer auth; actual 2020 ACS Autauga
population 55,639 then 2019 follow-up 55,380; unsupported year; new owner's empty
context; real rate limit; visible diagnostics/token exclusion; all turns <60s. Those
values are from existing independent reference SQL, not a new held-out benchmark.
Use `scripts/deployment_smoke.py` with a NEW evidence path. Optional operator-only
`requirements-browser.txt` is not in the app image. No deployed test has run.

SSH-disconnect availability, real key-pair privileges/cleanup, Docker build, proxy/TLS
and storage persistence need separate actual host evidence. Health HTTP 200 alone
is liveness, not readiness. Ten Phase 4 external checks remain pending. No repeated
Phase 1 discovery or Phase 2/3 full real evaluations; historical artifacts unchanged.
See PHASE4_REPORT.md for measured local commands/results and any initial test defects.

## Phase 4 DigitalOcean recovery — actual partial public evidence
New artifacts in phase4_recovery: real Docker/host status and file modes; external
client TLSv1.3/Let's Encrypt SAN/expiry/HTTP 308/200/security headers/closed 8501; clean
Chromium page loads 1.258s and 1.221s after controlled restart/recreation; no private
diagnostics on the observed unavailable page. Actual SQLite session persisted with
private permissions, not a mocked data answer. Outbound Snowflake TLS is connectivity
only. Public acceptance 1 passes; 8 and 10 have infrastructure-only evidence. Cases
2–7/9 and authenticated scope of 8/10 remain BLOCKED/UNRUN pending administrator action.
169 offline passes/25 live skips remain regression, not deployed factual results.
No previous real evaluations/scans rerun. Preserve initial Phase 4 and SPCS evidence.

## Production identity switch — targeted evidence (2026-10-14)
Requirements AS-4/AS-5/AS-17: test environment-only AGENT_PROD connector kwargs with
mock transport and forbid the development loader; reject missing password/account,
CODEX_APP/unapproved password user, mixed methods, unknown mode, PUBLIC role and
unconfirmed gates. Preserve key-pair and all Phase 1–4 regression coverage.
Targeted Phase 4 result: 40 passed (11 new checks). These connector assertions are
mocks, not hosted statistical answers. Full verification is recorded separately in
phase4_production_identity/verify.log.

Real production probes on Droplet: authenticated identity AGENT_PROD/PUBLIC/ALL;
SELECT returned CBG 010010201001, B01003e1=674 (1.117s); llama3.3-70b returned Hello!
(0.802s). ALTER SUSPEND succeeded and SHOW confirmed SUSPENDED. Complete query IDs and
bounded commands are in connection_probe.json. This is one connectivity smoke check,
not a new Census benchmark, answer-accuracy evaluation or named-role/NONE acceptance.
permissions.json records all visible grant results and 002003/02000 for missing app
role. Public authenticated suite remains blocked until operator prerequisites are met;
no skipped or blocked deployment case becomes PASS because these probes succeeded.

## Phase 4 activated deployment — actual final outcomes
AS-5/AS-17: nine final clean-browser cases passed using distinct real reviewer tokens,
public trusted HTTPS and actual Cortex/Snowflake: page, invalid auth, valid auth,
ACS 2020 Autauga 55,639, 2019 follow-up 55,380, unavailable 1850 clarification,
second owner's empty context, prompt-injection refusals/real rate limit, visible privacy.
AS-12: final factual browser latency 17.0037s; follow-up 14.0131s. AS-18: loading status
and expandable provenance observed on post-restart question (13.0037s).
Independent APP_ROLE/NONE reference SQL under the shared warehouse lease confirms
55,639/45 distinct CBGs and 55,380/32, invalid counts 0. SQL/query IDs saved separately.

Tenth acceptance: controlled app/proxy restart, SSH command ended, exact before/after
SQLite sessions/state/event hashes and 0600 mode match; new clean browser authenticates
and receives a real answer. No automatic browser-session resume is claimed.
Final server snapshot confirms SUSPENDED and unquarantined control. No benchmark
p95, throughput, universal accuracy, cost amount or production SLA is fabricated.

Two initial runner failures are retained: browser_first.json (default assertion 5s),
browser_retry.json (model-backed rate probe too slow to hit six/minute). Fix test
assertion timeout and use locally guarded refusals; no app logic/limits changed.
Final evidence: phase4_activation/browser_final.json, reference_sql.json,
post_restart_browser.json, before_restart.json/after_restart.json, network.json and
final_runtime.json. Earlier Phase 1–3 evaluations are not rerun or relabeled.
PUBLIC learning-role inheritance remains a P1 permission residual, distinct from a
passed application SQL/credential boundary and default PUBLIC CORTEX_USER.

## Phase 4 latency follow-up — actual before/after, not new held-out evaluation
AS-12: exact Alabama decennial question through existing AgentService/lease: profiled
15.0294s before, 13.6739s after; both 5,024,279 and identical SQL/params. Cortex varies,
so do not attribute all difference causally or report aggregate percentiles. Separate
2-CPU index load probe: 1.4277s ->0.7183s; all postings/ranked mappings match. Initial
slower cache prototype and busy profiling attempt are retained.
Public HTTPS real question 12.9913s, contextual follow-up 13.0160s, guarded refusal
2.9941s pass, with visible private-marker/token exclusion. 11 new deterministic
cache/invalidation/cleanup tests and 191 full offline passes /25 explicit live skips.
Old Phase 1–4 real evidence remains unchanged. See PHASE4_LATENCY.md for commands,
profiling conditions, initial fixture failure and remaining runtime/permission limits.

## Historical Phase 5 preparation snapshot — 2026-10-14 America/New_York
- AS-7/AS-8: completed README and four-topic Reflection, checked against PDF and source.
- AS-1/AS-2/AS-5/AS-12/AS-17: fresh external clean Chromium HTTPS 200/login;
  ACS 2020 Autauga 55,639 in 27.0405s; contextual 2019 answer 55,380 in 12.9892s.
  These are browser timings; visible service timings were 26.44s/12.15s. This is a
  deployment regression using earlier independently verified SQL values, not a new
  held-out evaluation. Two admitted turns reserved four unchanged budget units.
- AS-6: full offline 191 passed /25 explicit live skips, Ruff passes; pip check passes.
  ShellCheck remains unavailable. Logs: phase5_final/verify.log and dependencies.log.
- AS-4/SF-6: content scan covers all reachable Git blobs and eligible working files,
  current reviewer token exact matches, high-confidence key/token/password patterns;
  no findings. Scope/limitations recorded in phase5_final/secret_audit.json.
- AS-9: GitHub API returns private=false. All 11 reviewer permissions unverified
  because no API authentication is configured; this requirement has NOT passed.
- AS-10: PDF only defines receipt +24h. No matching assignment email was located in
  the narrowly searched connected mailbox; receipt/recipient must be confirmed by user.
- Capacity: after smoke 68/120 reserved units consumed, 52 left =26 two-unit admissions;
  11 reviewers x two turns require44 units if no intervening use. This is not a
  credit/cost guarantee. SHOW monitor returned no visible rows; warehouse monitor
  reported null. Administrator credit/monitor confirmation remains required.

## Final repository freeze verification
Repeat full offline regression and Ruff checks without new dependencies or live
model calls; validate manifests/imports/CLI, local Markdown links, complete reachable
Git history and tracked/nonignored files for high-confidence secret patterns. Audit
Docker allowlist/COPY sources statically; do not claim a new image build. HTTPS page
and health endpoint are the only fresh public checks. Preserve the earlier real
question/follow-up and first-independent19/25 vs reused25/25 regression evidence.
Results/commands: FINAL_SUBMISSION_AUDIT.md and final_submission_checks/. GitHub SSH
can verify default branch/pushed revision; it cannot verify privacy/invitations.
Operator confirmation and unauthenticated404 remain separate evidence types.

## Post-freeze budget repair evaluation
New deterministic real-SQLite/mocked-connector tests cover zero-call and legacy
reservations, actual Cortex execute boundary, failed submissions, failed cursor
creation, cross-instance persistence, exact rolling24h expiry, lease and two-call
bounds, concurrent budget debits, worker hook/status, production overrides/invalid
config. Full203 passed /25 live skips. Public real Alabama answer5,024,279 in31.0242s
corresponds to exactly2 durable ledger submissions. Local-refusal evidence separately
checks no added model usage. These are targeted regressions, not held-out accuracy.
See BUDGET_FIX_REPORT.md and budget_fix/.
