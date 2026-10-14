# Evaluation plan

Status: configuration/Phase 1 evidence preserved; Phase 2 core agent implemented
and targeted acceptance passed. UI/deployment evaluation remains planned. CHALLENGE_SPEC.md is the canonical requirement
register. Official PDF has been read and reconciled; AS-11 source audit is complete.
Historical synchronization notes below describe the prior state. Phase 2 tests have run; public deployment tests remain a later phase.
No remote discovery or Cortex tests were rerun during documentation synchronization.

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
| AS-5 | Independent unauthenticated reviewer-browser access to public URL and real multi-turn use; UI/server credential separation and error display | Planned deployment smoke/security tests |
| AS-6 | Representative held-out end-to-end cases, reference-query comparisons, failure taxonomy, measured latency and resource/cost summary | Phase 2 targeted evaluation; held-out evaluation pending |
| AS-7 | Fresh checkout with documented dependencies and exact setup/run/test/example commands succeeds | Pending README/reproduction |
| AS-8 | Reflection matches PDF format and accurately explains actual design, evidence, limits and tradeoffs | Pending artifact review |
| AS-9 | Exact reviewer accounts have required effective repository access | Pending permissions verification; no access mutation authorized here |
| AS-10 | PDF-confirmed recipient/deadline/content/links; authorized send and receipt | Pending submission check; no email sent |
| AS-11 | Five-page PDF reconciliation, 30 unique IDs with page/source and nonempty verification | Complete; absolute receipt/recipient remain open |
| AS-12 | Each real turn measured including model, query and cleanup; assert <60s | Phase 2 live assertions; no production SLA |
| AS-13 | Local rejection plus structured domain classification; unsafe/off-topic cases produce no data SQL | Phase 2 unit/live cases |
| AS-14 | Existing Marketplace evidence and actual core data queries; fallback unused | Source access verified |
| AS-15 | All implementation files included in final private-repo submission manifest | Core checkpoints packaged; final application pending |
| AS-16 | Full catalog family/schema tests, dynamic candidates, exact filters, undefined fields quarantined | Partial: 296 unknown fields and unsupported calculations |
| AS-17 | Clean public deployed-browser setup/auth/real conversation checks | Pending outside Phase 2 |
| AS-18 | CLI progress callbacks and fast-fail output; later browser progress | CLI implemented; deployed UX pending |

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
