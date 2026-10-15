# Challenge specification

Status: official PDF reconciled; verified Phase 1–3 retained. Phase 4 authenticated
HTTPS Web demo now externally verified, including actual data and restart. Strict
account privilege isolation remains open. Phase 5 submission preparation is authorized;
README/Reflection and final smoke are verified. GitHub privacy/access and submission
metadata remain blockers (PHASE5_REPORT.md). No email sent.

## Objective
Build a chatting agent that answers questions about United States Census population
using verified Snowflake data and Cortex. Phase 1 supplies its semantic foundation;
Phase 2 implements the core agent and multi-turn interaction. Phase 3 adds reliability
controls; Phase 4 supplies the actual authenticated public Web deployment.

## Rules
Official source: [Applied AI: Candidate Homework Assignment](<reference/Applied AI_ Candidate Homework Assignment .pdf>), five pages. Read in full before Phase 2.
AI tools are explicitly encouraged (pp.1,4). Submission is due 24 hours after receipt
(pp.1,3); the absolute receipt/deadline timestamp is not established by the PDF.
The application need not run exclusively on Snowflake (p.4). Required data is the
US Open Census Marketplace dataset using a free trial; the cited SafeGraph fallback
is allowed only if that source is inaccessible (p.2). Existing Marketplace access
is verified, so no fallback or infrastructure reset is needed.

Current authorization covers completed Phase 1–4, Phase 5 final documentation/audit,
existing DigitalOcean demo and routine reviewed Git checkpoints. No final email,
unapproved grants/revokes or new paid infrastructure. CODEX_APP is local-only using
DEV_WH. Follow docs/PROGRESS.md for continuation; prior scope is retained in reports.

## Requirements
The traceability table is the canonical requirement register. Existing SF-1 through
SF-6 and P1-1 through P1-6 IDs are retained. AS-1 through AS-18 cover official and user-added obligations. SF/P1 requirements
remain supporting engineering slices, not separate invented PDF mandates.
Each requirement occurs once as a register row and has a verification method.
"Complete" means its recorded slice passed, not that the PDF or full agent passed.

## Acceptance criteria
Phase 1: account for every discoverable indicator family and supplied definition;
return exact schema mappings for five required searches; preserve release/source,
universe and geography; reject unsupported aggregations; distinguish real SQL tests
from local/mocked checks. Missing definitions must be quarantined, not fabricated.

Full homework per PDF: functional multi-turn data-grounded agent, explicit
clarification/refusal and guarded execution, public deployed UI, meaningful end-to-end
evaluation, reproducible README and Reflection, verified reviewer access, and correct
final email. Unimplemented deliverables remain pending even after source reconciliation.

Quality gates apply to the whole homework: A: PDF rules reconciled; absolute deadline/recipient details remain open;
B/C/D now include targeted core-agent tests, not deployed-homework completion;
E remains pending fresh reproduction,
reviewer-access checks and delivery review. None of those whole-homework gates is
marked complete merely because the catalog passed.

## Deliverables
Implemented: `data/semantic_catalog.json`, `census_catalog/`, Phase 1 metadata/search/
integration evidence, deterministic and opt-in real tests, `PHASE1_REPORT.md`, and
`snowflake_config.md`. The five synchronized engineering documents describe this state.

Implemented in Phase 2: `census_agent/`, local CLI, explicit conversation state,
canonical runtime SQL validation and grounded answers; targeted tests/evidence.

Implemented Phase 3/4: isolated authenticated service, independent evaluation with
preserved first-run failures, Web UI and actual public acceptance evidence.

Implemented in Phase 5: complete README and four-topic REFLECTION.md, final offline
checks and a minimal authenticated external two-turn smoke.

Pending: strict effective permission cleanup, repository privacy/reviewer access
verification, credit headroom confirmation and final submission email. Reflection must be Markdown and cover the four topics on p.3. The public-demo
access instructions, private repository and named reviewers are mandatory.

## Ambiguity
Facts independently checked from code/artifacts: 71 tables plus 2 views; real region
AWS_CA_CENTRAL_1; 59 indicator tables; 16,878 indicator fields; 16,582 dictionary-backed
fields; 296 physical columns lack definitions. Five Phase 1 search cases and nine
recorded Phase 1 real tests passed; unchanged evidence is preserved. Source products are ACS detailed/collapsed families and decennial
redistricting; ACS prefix year is provider release year, not proven survey interval.

Accepted design: catalog-grounded single workflow with Cortex structured intent/ID
choice and deterministic SQL/answers; explicit conversational state. Streamlit/AgentService with single-host Docker/Caddy/SQLite is deployed; advanced
aggregation remains explicitly unsupported.

Open questions: receipt timestamp/email recipient not specified in PDF; undefined field meanings;
exact ACS survey interval; national/territory scope, global key/coverage guarantees,
historical geography crosswalks, city/place resolution, and supported answer categories.

## Traceability
PDF rows cite page/section. SF/P1 rows are user-defined supporting slices; their
Phase 1 completion remains unchanged. AS-3 is explicitly user-added, not a mandatory
PDF provider choice. Related PDF tips are consolidated with the core obligation
instead of duplicating context/latency/degradation requirements.

| Requirement ID | PDF Requirement | Implementation | Verification | Status |
| --- | --- | --- | --- | --- |
| SF-1 | User setup slice; supports PDF p.2 data requirement: authenticate and select correct Snowflake context | Existing connector/config loader; account context captured | `snowflake_evidence.json` context and query ID; local connector boundary tests | Complete (configuration slice) |
| SF-2 | User setup slice; supports PDF p.2 data requirement: inventory and count all queryable objects | 71 tables + 2 views; 73 COUNT(*) results recorded | Inspect inventory/count query IDs and successful results; do not repeat discovery | Complete (configuration slice) |
| SF-3 | User setup slice; supports PDF p.2 data requirement: inspect core columns and examples | Three DESCRIBE results and five rows per core table | `snowflake_evidence.json` core schemas/samples; exact identifier tests | Complete (configuration slice) |
| SF-4 | User setup slice; supports PDF p.2 data requirement: verify Cortex and alternative models | Three available models; gemma2-9b recorded unknown-model failure | Recorded outputs, elapsed times and query IDs in `snowflake_config.md`/evidence; no new model calls | Complete (availability test, not agent quality) |
| SF-5 | User setup slice; supports PDF p.2 data requirement: suspend warehouse after tests | Probe and live-test fixture cleanup perform ALTER and SHOW | Stored cleanup query IDs and confirmed suspended state, last live test 2026-10-14 | Complete (recorded cleanup) |
| SF-6 | User setup slice; supports PDF p.2 data requirement: credential-safe configuration/report | Ignored owner-only .env; safe loader; config summary | Ignore/tracked-file/mode inspection without reading values; redaction/permission tests; documentation audit | Complete (configuration boundary) |
| P1-1 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: cover all indicator families and descriptions | `census_catalog/build.py` catalog: 59 tables, 16,878 fields, 16,582 definitions | `test_all_discovered_families_and_dictionary_definitions_are_accounted_for`; snapshot reconciliation | Complete (all supplied definitions; 296 gaps explicit) |
| P1-2 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: retrieve relevant verified fields and associated schema | `Catalog.search`, `mapping`, `table_schema`; offline lexical index | Five-case retrieval assertions; `phase1_search_results.json`; five recorded real select tests | Complete (defined cases) |
| P1-3 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: preserve year/product and verify CBG/FIPS mappings | `Geography` and year-specific FIPS/reference data | `tests/test_geography.py`; three recorded product/release joins for two sampled CBGs | Complete (bounded geography scope) |
| P1-4 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: prevent unsafe statistical aggregation | `classify`, `sum_counts`, explicit unsupported policies | `tests/test_aggregation.py` mixed/duplicate/non-additive/missing/overflow cases; bounded real SQL SUM comparison | Complete (implemented policies) |
| P1-5 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: preserve exact identifiers and avoid invented definitions | Exact schema reconciliation; undefined columns quarantined | Exact-case, paired-MOE, schema-drift and quarantine tests; query provenance | Complete (captured schema) |
| P1-6 | User Phase 1 slice; supports PDF p.4 mapping/schema tips: deterministic/real tests, evidence report, stop at Phase 1 | Unchanged existing test suite and `PHASE1_REPORT.md` | 58 local tests; nine recorded real tests; original Phase 1 code/evidence preserved | Complete (Phase 1 only) |
| AS-1 | PDF pp.1–2, Core Functionality: interactive natural-language Census-grounded agent | Phase 1 grounding exists; `census_agent` core pipeline implemented | Real question/SQL/reference-result/answer tests; ambiguity/refusal cases | Complete (Phase 2 supported core scope) |
| AS-2 | PDF pp.2,5: preserve context across turns and accurate follow-ups | Explicit resolved/pending state, follow-up merge and comparison implemented | Three multi-turn scenarios; updates, pending clarification, resets, isolation | Complete (three real scenarios plus offline edges) |
| AS-3 | User Phase 2 requirement, not PDF mandate: Cortex primary LLM, initially llama3.3-70b | Bounded llama3.3-70b structured intent/catalog choice implemented | Real Cortex query IDs and provider/error tests | Complete (actual bounded Cortex calls) |
| AS-4 | PDF pp.2,5: graceful degradation, ambiguous/partial/conflicting/unanswerable inputs; user: safe SQL boundary | Canonical SQL validator, domain/semantic guards and safe errors implemented | Unknown/empty/error cases; unvalidated SQL cannot reach data executor | Complete (tested core/hosted boundary; inherited permissions remain a risk) |
| AS-5 | PDF pp.2,4: public web interface; no local setup for evaluation; authentication allowed | Streamlit/AgentService on existing DigitalOcean host with public trusted HTTPS | Fresh external browser auth/data/follow-up/isolation/rate/privacy; post-restart real answer | Complete (Phase 4 measured functional deployment; risks disclosed) |
| AS-6 | PDF p.2: meaningful tests, explain strategy/tradeoffs; pp.3–4 evaluation dimensions | 191 offline tests; preserved Phase 1–3 real evaluations and Phase 4 external smoke | Independent SQL/reference results, held-out failures, regression and deployment evidence | Complete (documented bounded evaluation; not universal accuracy) |
| AS-7 | PDF pp.1–2: README explains architecture/demo and documents interpretations | Final README: demo/access, architecture, setup, evaluation and limitations | Source review, offline search, dependency checks and external two-turn smoke; prior real Docker build | Complete (document and commands verified; no fresh local dependency-install claim) |
| AS-8 | PDF pp.1,3–4: Markdown reflection covering process/architecture, more-time changes, unaddressed failures and testing/future tests; discuss AI use | Root REFLECTION.md covers all four topics with actual phase evidence and AI use | Compare headings/content to PDF p.3, preserve 19/25 first evaluation vs 25/25 regression | Complete (document reviewed) |
| AS-9 | PDF p.3: private GitHub repository shared with the 11 named reviewers | GitHub unauthenticated API returned private=false; no API credentials available | Change visibility then authenticated effective-access check for all 11 exact PDF handles | BLOCKED (public repository; all 11 access states unverified) |
| AS-10 | PDF pp.1,3: email private repository link within 24 hours of receipt | No email sent; exact recipient/receipt timestamp still needed | Deadline check, repository/demo links, authorized send and receipt | Pending |
| AS-11 | PDF p.1: read requirements before coding; current user: reconcile original PDF | Five-page PDF read; old 23 IDs reconciled; missing obligations added | Source/page audit and unique-ID/test-method comparison; reconciliation report | Complete (source reconciliation) |
| AS-12 | PDF pp.2,5: responses within 60 seconds under normal conditions | 55-second service deadline and actual browser progress; normal hosted turns measured | External factual 17.0037s, follow-up 14.0131s, restart factual 13.0037s; prior core evidence | Complete (measured cases <60s; no SLA claim) |
| AS-13 | PDF pp.2,5: dedicated guardrails for off-topic/inappropriate requests and grounded scope | Explicit local/structured-domain and canonical SQL validation implemented | Adversarial/off-topic/inappropriate cases refuse before data SQL | Complete (tested core domain/content cases) |
| AS-14 | PDF p.2: free-trial Snowflake Marketplace US Open Census source; conditional disclosed SafeGraph fallback | Existing verified Marketplace database reused; no fallback | Existing source/context evidence and Phase 2 source query IDs; trial status user-provided | Complete (source access; no reconfiguration) |
| AS-15 | PDF p.3: repository includes all solution implementation code | Phase 1–4 implementation, Docker configuration, tests and evidence in repository | Reviewed source allowlist/manifests, authorized GitHub checkpoint and unchanged core source | Complete (implementation included; final documentation tracked separately) |
| AS-16 | PDF p.4: comprehensive metadata/join mapping and sufficient schema context, no manually limited prompt subset | Full Phase 1 catalog reused; 296 undefined fields remain excluded | Family coverage plus dynamic catalog-choice tests; document unsupported/cross-table scope | Partial (documented semantic gaps) |
| AS-17 | PDF p.4: verify final demo in clean deployed environment for missing config/connections/auth loops | Live HTTPS demo with production identity and persistent server control | phase4_activation/browser_final.json plus post_restart_browser.json and exact SQLite snapshots | Complete (actual clean external browser/restart verification) |
| AS-18 | PDF p.5: streaming or progress feedback for interactivity; correctness and fast-fail paths | CLI stages and Web loading/status/provenance with fast local guard refusals | Post-restart browser observes loading progress and expandable provenance; live refusals | Complete (progress feedback; no token streaming claimed) |

## Ordered implementation plan
Current scope: Phase 5 final submission preparation, without sending email.
The ordered Phase 2–4 implementation plan below is historical and completed within
its recorded scope; current final actions are in PHASE5_REPORT.md and PROGRESS.md.
1. PDF reconciliation complete (AS-11); decide supported question/geo/statistic
   boundaries and preserve the Phase 1 gaps. Do not repeat verified infrastructure setup.
2. Implement a smallest grounded question -> schema -> validated SQL -> result -> answer
   slice using Cortex (AS-1/AS-3/AS-4); test unsupported/ambiguous cases before broadening.
3. Add explicit conversation state and multi-turn regression cases (AS-2).
4. Finish targeted Phase 2 reference/security/latency evaluation and report; stop.
5. Later, with authorization, add UI and public deployment with end-to-end/security evaluation
   (AS-5/AS-6); select stack/latency thresholds only with task evidence.
6. Complete README/Reflection, fresh reproduction, reviewer access and submission
   review (AS-7 through AS-10). Deploy/share/send only when separately authorized.

## Historical configuration and Phase 1 evidence
The preparation repository initially had only README and its initial commit. Earlier
setup kept tooling minimal and added no speculative agent. Historical configuration
completed authentication, 73 counts, three core schemas/samples and four model probes.
`llama3.1-70b` (0.741s), `llama3.3-70b` (1.875s), `mistral-7b` (0.746s) succeeded;
`gemma2-9b` failed with unknown model after 20.953s. User-disallowed legacy Mistral
models were not tested. These are single availability probes, not quality benchmarks.

Corrections retained: supplied us-east-1 was inaccurate (actual AWS_CA_CENTRAL_1);
"73 tables" means 71 tables plus two views. Phase 1 fetched metadata, not Census
statistical tables, and performed ten bounded SQL queries for nine live tests.
Whole-homework delivery remains outstanding even though Phase 1 is complete.

## PDF reconciliation — 2026-10-14
Original 23 IDs retained. Seven IDs (AS-12–AS-18) add missing explicit obligations.
Corrected AS-3: Cortex is a user constraint, not a PDF mandate. AS-4 now distinguishes
SQL safety from the dedicated content/domain boundary AS-13. Multi-turn/stateful
and graceful-degradation tips map to AS-2/AS-4 rather than duplicate IDs. Reflection
contents, private repository, exact reviewer accounts and 24-hour rule are clarified.
Official data source is AS-14; SF/P1 items remain supporting engineering work.
No PDF ban on AI use; no required exclusive Snowflake hosting or specific UI stack.
See PDF_RECONCILIATION.md. Deployment, reviewer-access changes and email remain
outside Phase 2; their authorization is not implied by the assignment document.

## Phase 2 acceptance — 2026-10-14
Core pipeline/CLI complete within documented supported scope. Final live suite:
16 passed, six questions across five families, three multi-turn scenarios, independent
reference SQL and adversarial/unsupported cases; all measured turns under 60s.
Full offline suite 116 passed / 25 opt-in skips; Phase 1 original evidence preserved.
See PHASE2_REPORT.md. UI/deployment and final submission remain pending; stop after Phase 2.

## Phase 3 authorized scope and traceability
The current user authorizes Phase 3 reliability/evaluation only. AS-2/AS-4 cover
owner-bound sessions, safe concurrent ownership, deadlines, graceful provider/
overload errors and filtered diagnostics. AS-6 covers frozen independent cases,
reference SQL, failure analysis and explicit held-out-versus-regression separation.
AS-12 measures the entire service request, including startup/connection/cleanup.
SF-5/SF-6 retain suspension/credential exclusions. AS-5/AS-7/AS-8/AS-9/AS-10/AS-17
remain full-delivery obligations, not authorization to deploy, share or email now.

Phase 3 acceptance: existing offline/targeted Phase 2 real regressions pass; new
cases have honest recorded outcomes; session/connection isolation and SQL/credential
security tests pass; provider/overload faults degrade safely; measured normal turns
<60s; remaining restricted-identity/hosting risks explicit. Stop after Phase 3.
See PHASE3_REPORT.md for actual measured results; never replace first-run failures
with later regression successes. No new full inventory scan or public UI.

Phase 3 actual evidence: first frozen run 19/25; final reused-case regression 25/25,
real session isolation pass, existing Phase 2 live 16/16, full offline 140 pass / 25
live skips. PHASE3_REPORT.md distinguishes first held-out failures from regressions,
records actual latency and identifies restricted-identity/hosting blockers.

## Phase 4 authorization and actual status
Public authenticated chat is deployed and externally verified at
https://census-104-248-239-52.sslip.io. AS-5/AS-17 functional acceptance now has actual
browser/data/auth/restart evidence; AS-18 loading/provenance was observed. Core
statistical/SQL/security controls are unchanged. Production AGENT_PROD uses APP_ROLE,
secondary NONE, deployment environment credentials and the confirmed exclusive
SNOWFLAKE_LEARNING_WH; developer CODEX_APP now uses DEV_WH.

PUBLIC still inherits learning-role warehouse and schema privileges, contrary to the
operator's direct-grant-only audit. Strict account isolation is outstanding; the
functional demo does not prove it. Operator should give APP_ROLE explicit OPERATE
before reviewing/remediating PUBLIC inheritance. No grants changed. Full README,
Reflection, reviewer repository/access handoff and final email are still pending.
No Phase 5 started; see PHASE4_REPORT.md and PROGRESS.md for current evidence/risks.
