# Challenge specification

Status: official PDF reconciled; Phase 1 preserved; Phase 2 core agent authorized
implemented and targeted acceptance passed. Public UI/deployment remain outside this phase.

## Objective
Build a chatting agent that answers questions about United States Census population
using verified Snowflake data and Cortex. Phase 1 supplies its semantic foundation;
Phase 2 now implements the local agent and multi-turn interaction. Public UI and
deployment are not implemented.

## Rules
Official source: [Applied AI: Candidate Homework Assignment](<reference/Applied AI_ Candidate Homework Assignment .pdf>), five pages. Read in full before Phase 2.
AI tools are explicitly encouraged (pp.1,4). Submission is due 24 hours after receipt
(pp.1,3); the absolute receipt/deadline timestamp is not established by the PDF.
The application need not run exclusively on Snowflake (p.4). Required data is the
US Open Census Marketplace dataset using a free trial; the cited SafeGraph fallback
is allowed only if that source is inaccessible (p.2). Existing Marketplace access
is verified, so no fallback or infrastructure reset is needed.

User instructions authorize Phase 2 with Cortex initially llama3.3-70b, CLI, bounded
real tests and permission inspection. They exclude public deployment, extensive UI,
new orchestration frameworks, Phase 1 restart and automatic Phase 3 work. Keep
credentials private; do not commit/push/share/send without appropriate authorization.

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

Pending: public UI/deployment, broader held-out evaluation, full README, Reflection, reviewer access
verification and final submission email. Reflection must be Markdown and cover the four topics on p.3. The public-demo
access instructions, private repository and named reviewers are mandatory.

## Ambiguity
Facts independently checked from code/artifacts: 71 tables plus 2 views; real region
AWS_CA_CENTRAL_1; 59 indicator tables; 16,878 indicator fields; 16,582 dictionary-backed
fields; 296 physical columns lack definitions. Five Phase 1 search cases and nine
recorded Phase 1 real tests passed; unchanged evidence is preserved. Source products are ACS detailed/collapsed families and decennial
redistricting; ACS prefix year is provider release year, not proven survey interval.

Accepted design: catalog-grounded single workflow with Cortex structured intent/ID
choice and deterministic SQL/answers; explicit conversational state. UI framework
and deployment remain undecided; advanced aggregation is explicitly unsupported.

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
| AS-4 | PDF pp.2,5: graceful degradation, ambiguous/partial/conflicting/unanswerable inputs; user: safe SQL boundary | Canonical SQL validator, domain/semantic guards and safe errors implemented | Unknown/empty/error cases; unvalidated SQL cannot reach data executor | Complete (tested core boundary; deployment review pending) |
| AS-5 | PDF pp.2,4: public web interface; no local setup for evaluation; authentication allowed | Not implemented in Phase 2 | Independent browser/public URL and full conversation smoke check | Pending (later phase) |
| AS-6 | PDF p.2: meaningful tests, explain strategy/tradeoffs; pp.3–4 evaluation dimensions | Phase 1 evidence retained; Phase 2: 58 offline tests and 16 real tests passed | Five metric families, three conversations, ground-truth SQL, security and failure cases | Partial (Phase 2 evidence complete; broader/hosted evaluation pending) |
| AS-7 | PDF pp.1–2: README explains architecture/demo and documents interpretations | Initial README preserved; complete final README pending | Fresh engineer can understand choices, access demo and reproduce commands | Pending |
| AS-8 | PDF pp.1,3–4: Markdown reflection covering process/architecture, more-time changes, unaddressed failures and testing/future tests; discuss AI use | No final reflection artifact | Four-topic checklist plus honest limitations and AI-tool usage review | Pending |
| AS-9 | PDF p.3: private GitHub repository shared with the 11 named reviewers | No privacy/access change in Phase 2 | Verify private visibility and effective access for exact listed handles | Pending |
| AS-10 | PDF pp.1,3: email private repository link within 24 hours of receipt | No email sent; exact recipient/receipt timestamp still needed | Deadline check, repository/demo links, authorized send and receipt | Pending |
| AS-11 | PDF p.1: read requirements before coding; current user: reconcile original PDF | Five-page PDF read; old 23 IDs reconciled; missing obligations added | Source/page audit and unique-ID/test-method comparison; reconciliation report | Complete (source reconciliation) |
| AS-12 | PDF pp.2,5: responses within 60 seconds under normal conditions | Bounded request budget in Phase 2; no streaming UI yet | Measure every live answer turn including model/query/cleanup; report failures, not just averages | Complete (all measured Phase 2 turns <60s; not a production SLA) |
| AS-13 | PDF pp.2,5: dedicated guardrails for off-topic/inappropriate requests and grounded scope | Explicit local/structured-domain and canonical SQL validation implemented | Adversarial/off-topic/inappropriate cases refuse before data SQL | Complete (tested core domain/content cases) |
| AS-14 | PDF p.2: free-trial Snowflake Marketplace US Open Census source; conditional disclosed SafeGraph fallback | Existing verified Marketplace database reused; no fallback | Existing source/context evidence and Phase 2 source query IDs; trial status user-provided | Complete (source access; no reconfiguration) |
| AS-15 | PDF p.3: repository includes all solution implementation code | Phase 1/2 code and evidence included in development checkpoints; final application packaging pending | Review tracked/untracked implementation manifest before authorized commit/submission | Partial (core checkpoint packaged; final application pending) |
| AS-16 | PDF p.4: comprehensive metadata/join mapping and sufficient schema context, no manually limited prompt subset | Full Phase 1 catalog reused; 296 undefined fields remain excluded | Family coverage plus dynamic catalog-choice tests; document unsupported/cross-table scope | Partial (documented semantic gaps) |
| AS-17 | PDF p.4: verify final demo in clean deployed environment for missing config/connections/auth loops | No deployment in Phase 2 | Independent clean public-deployment end-to-end and error checks | Pending (later phase) |
| AS-18 | PDF p.5: streaming or progress feedback for interactivity; correctness and fast-fail paths | CLI stage progress and bounded failures implemented | Progress callback/CLI and refusal-latency checks; deployed UX later | Partial (CLI progress complete; deployed UX pending) |

## Ordered implementation plan
Phase 2 is now explicitly authorized. Stop after its core/CLI/evaluation scope.
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
