# Delivery checklist

Current: Phase 5 final preparation; **not ready to submit**. Live demo and technical
package are verified; private repository/reviewer access is operator-reported but independently unverified;
submission metadata remains unresolved. See FINAL_SUBMISSION_AUDIT.md. Earlier snapshots below are historical, not current assertions.

## Functional
- [x] AS-1/AS-2/AS-3: supported grounded Cortex agent, explicit context and multi-turn;
  Phase 2 real16-test evidence and fresh public two-turn regression preserved.
- [x] AS-5/AS-17/AS-18: public authenticated HTTPS UI, loading/provenance, actual
  deployment and restart acceptance in PHASE4_REPORT.md; final external smoke passes.
- [x] SF/P1: existing data/catalog/geography/statistical foundation and evidence preserved.
- [ ] AS-16: universal semantic coverage is not claimed;296 undefined fields quarantined,
  unsupported geography/aggregations and cross-table questions explicitly disclosed.

## Reliability
- [x] Bounded workers/connections, owner-isolated state, canonical SQL and safe failure
  responses; regression and real Phase 3/4 evidence retained.
- [x] AS-12: final browser27.0405s/12.9892s, both under60s; no SLA/p95 claim.
- [x] Final packaging does not change/restart the deployed service or SQLite state.
- [ ] Administrator confirms actual Snowflake trial-credit headroom/monitor assignment.

## Evaluation
- [x] AS-6: final191 offline passes /25 opt-in live skips, Ruff and dependency checks pass.
- [x] First independent19/25 and later25/25 regression clearly distinguished; failures retained.
- [x] Ground-truth SQL, mocked outage tests and real integration evidence labeled.
- [x] Final HTTPS/login and one real question/contextual follow-up verified externally.
- [ ] Sustained load, broad new held-out accuracy, p95/cost and third-party security audit.

## Security
- [x] No high-confidence secret findings in reachable Git history and eligible worktree;
  prior exact token check retained; fresh format/entropy/key scan clean; .env ignored.
  Scope in final_submission_checks/security.json; no ignored secrets read.
- [x] Public adapter uses production secrets/AGENT_PROD/APP_ROLE/NONE without dev fallback;
  private diagnostics excluded. No new grants, secret rotation or safety-limit changes.
- [ ] P1 residual: administrator reviews PUBLIC learning-role inheritance and grants
  APP_ROLE explicit OPERATE before safely removing inherited cleanup access.
- [ ] Independently verify private GitHub visibility and all 11 valid invitations/access;
  operator reports both actions completed, but no authenticated API audit is available.

## Documentation
- [x] AS-7: final README includes live access, architecture, source, setup, tests and limits.
- [x] AS-8: root REFLECTION.md covers all four PDF topics, AI use and actual evidence.
- [x] AS-11: original PDF reconciliation and30 unique IDs with verification methods checked.
- [x] Architecture/decisions/evaluation/progress and Phase5 report synchronized.

## Reproducibility
- [x] Existing actual Docker build/install/launch and restart evidence retained; deployment
  remains v0.4.4-dev. No fresh local install is claimed from the existing environment.
- [x] Offline search example, doctor, verify, pip check and preflight actually executed.
- [x] All implementation code/config and evidence included; no secret/runtime state packaged.
- [ ] Gate E complete delivery: private access, receipt/deadline/recipient and private
  demo credential handoff still need confirmation. Preflight exit2 is incomplete.

## Submission
- [ ] AS-9: private visibility independently verified (operator reports Private; current
  unauthenticated API404 cannot establish it).
- [ ] AS-9: all 11 exact PDF accounts have valid invitations or accepted access; operator
  reports all invited. Each independent state is UNVERIFIED in FINAL_SUBMISSION_AUDIT.md.
- [ ] AS-10: actual assignment receipt/timezone, deadline=receipt+24h and recipient confirmed.
- [x] Token-free email draft prepared in SUBMISSION_EMAIL_DRAFT.md; no send/schedule.
- [ ] Existing demo token included through private channel with actual submission;
  never include Snowflake credentials. Retrieval steps in REVIEWER_ACCESS.md.
- [ ] Final email explicitly authorized and sent; intentionally not part of this phase.

Gate status: A source/rules understood, absolute timing incomplete; B supported slice
verified; C tested functional/edge cases pass; D bounded evaluation/failures documented;
E full delivery blocked. Passing tests do not establish complete assignment coverage.

---

# Historical delivery checklist snapshots

Status: Phase 1 foundation verified within bounded scope; full homework is not ready
for delivery. The official five-page PDF is now reconciled (AS-11); IDs and page references
are in CHALLENGE_SPEC.md. Phase 2 core agent is implemented; targeted live acceptance passed.
Phase 3 reliability is implemented and verified within its bounded scope. Phase 4 public authenticated demo and external ten-point functional acceptance passed;
strict inherited-permission cleanup and final delivery remain outstanding.

Checked items below are supported by inspected source/tests/artifacts or the fresh
offline test run. Historical Phase 1 live evidence is labeled and preserved. Phase 2 adds bounded
Cortex/data calls with separate artifacts. Planned items stay unchecked.

### Functional
- [x] SF-1/SF-2/SF-3: historical connector context, 71 tables + 2 views, 73 exact counts,
  three schemas and samples independently inspected in stored evidence.
- [x] SF-4: historical availability of three Cortex models and one unknown-model
  alternative inspected; this is not functional agent behavior.
- [x] P1-1/P1-5: catalog covers 59 indicator tables and all 16,582 supplied definitions;
  exact physical schema retained for 16,878 fields; 296 undefined fields quarantined.
- [x] P1-2: five required search cases return relevant verified physical mappings;
  retrieval/schema tests pass; earlier real returned-column queries inspected.
- [x] P1-3: year-specific CBG/FIPS resolver implemented; ambiguity/leading-zero tests
  pass; earlier real geography joins inspected for the sampled CBGs.
- [x] P1-4: unsupported aggregation and mixed/duplicate/invalid data fail explicitly;
  earlier real bounded sum agrees with SQL.
- [x] AS-1/AS-3 (core implementation): functional question -> grounded plan -> validated SQL -> results ->
  answer Agent using Cortex, with real end-to-end evidence.
- [x] AS-2 (core implementation/tests): functional multi-turn conversation, corrections/reset and session isolation.
- [x] Existing Phase 1 modules/APIs/artifacts preserved; SHA-256 comparisons recorded.
- [x] Gate A source intake: official PDF requirements and AI rules read and reconciled.
  Absolute deadline/recipient operational details still require confirmation before submission.
- [x] Gate B (core slice): actual Cortex -> validated SQL -> grounded answer verified.
  Public UI and real external multi-turn/restart acceptance now pass (Phase 4).

### Reliability
- [x] Existing probe/config boundaries have deterministic tests; Phase 1 search,
  geography and aggregation reject implemented invalid/unsupported cases.
- [x] SF-5: historical live cleanup ended with SUSPENDED; query IDs/state inspected.
  This does not claim continuous monitoring of current warehouse state.
- [x] Phase 1 limitations and fallback/quarantine policies are documented.
- [x] AS-4 (core boundary): canonical SQL validation, model/data failures, empty/invalid
  results, finite timeouts/resources and zero automatic retries; mock and real cases.
  Comprehensive hosted security/reliability review remains pending.
- [x] Core recovery preserves successful state and avoids automatic retries; unit tests.
- [ ] Whole-application P0/P1 hardening review completed; deferred P2 issues documented.

### Evaluation
- [x] P1-6: fresh offline run: 58 passed, nine live tests explicitly skipped, exit 0.
  The 58 include 44 Phase 1 offline cases and 14 existing connector helper cases.
- [x] P1-6: saved real integration run independently inspected: nine passed tests,
  ten bounded SQL queries; mocks/captured data distinguished from real results.
- [x] Phase 1 report/search timings/provenance/failure categories retained; no invented
  general accuracy or p95 claims.
- [x] AS-6 (bounded documented scope): end-to-end evaluation covering representative/held-out questions,
  statistical accuracy, ambiguity, multi-turn behavior and SQL security.
- [ ] AS-6: approved reference baselines and measured latency/resource/cost results.
- [ ] Gate C: whole-application functional and edge-case tests pass (Phase 1 portion does).
- [ ] Gate D: complete agent evaluation and meaningful failure analysis finish.

### Security
- [x] SF-6: source/tests support owner-only config loading and redaction; earlier
  ignore/mode checks recorded; sync also checked ignored/untracked/mode 600 without
  reading values and found no documentation credential-assignment/key/token patterns.
  This is not the final application/submission security audit.
- [x] AS-4: canonical typed query recompilation and exact SQL/parameter/bound equality
  enforced by backend before data execution; arbitrary model SQL is never executed.
- [x] AS-4/AS-5 tested boundary: local SQL/security regressions plus live session isolation,
  prompt refusal, server-only credentials and inspected public/log surfaces pass. This
  does not establish account-level least privilege or a complete penetration test.
- [ ] Final staged files/diff and submission artifacts reviewed for accidental secrets.
- [x] Core effective permission visibility and resource bounds inspected; PUBLIC/ALL
  mode and direct-user access documented, without claiming least privilege.
- [ ] Deployment threat model, restricted identity and hosted concurrency reviewed.

### Documentation
- [x] Five engineering documents now separate actual Phase 1 from planned components
  and map reconciled official/user obligations to unique requirement IDs and verifications.
- [x] Valid setup/Phase 1 decisions, evidence, assumptions, tradeoffs and risks preserved.
- [x] AS-11: original PDF read; requirement/page reconciliation and missing IDs recorded
  in PDF_RECONCILIATION.md. Absolute receipt time/recipient remain unresolved.
- [ ] AS-7: README includes final objective, setup/configuration, run/example/test steps,
  public URL, architecture and limitations; current README remains the initial placeholder.
- [ ] AS-8: Reflection exists and matches official format/content with actual decisions
  and measured evidence; no Reflection artifact has been verified.

### Reproducibility
- [x] Phase 1 report describes offline catalog build/search and opt-in real test commands.
- [x] Deterministic catalog rebuild/exact-schema and malformed-input tests pass.
- [ ] AS-7/Gate E: clean checkout installation, example, tests and final application
  reproduction verified by a reviewer; current environment is already configured.
- [ ] Full verification, submission packaging and independent complete delivery review.

### Submission
- [x] AS-5: publicly accessible deployed UI, confirmed from fresh external browser
  contexts with actual authenticated data, multi-turn usage and safe unsupported errors.
- [ ] AS-9: exact GitHub reviewer identities/permissions confirmed against PDF and
  effective access verified; no permission change was performed here.
- [ ] AS-11: deadline/timezone, approved tools/models, output format, links/files,
  submission recipient and required content verified from official instructions.
- [ ] Review all uncommitted/untracked work and intentionally include the final files.
- [ ] AS-10: final submission email checked against official instructions; send only
  with explicit authorization and record delivery confirmation. No email has been sent.
- [ ] Final handoff includes working URL, repository access, setup/run/test commands,
  end-to-end evaluation, README, Reflection and known limitations.
- [ ] Final deployment/push/sharing/email actions explicitly authorized; none is
  authorized merely by this documentation checklist.

### Historical checkpoint — Phase 2 status
Core local interface, Cortex semantics, canonical SQL validation, grounded answers,
explicit state and failure handling are implemented. Six questions across five families, three conversations and SQL safety pass: 16
real tests; 58 Phase 2 offline checks. PHASE2_REPORT.md records actual acceptance; the complete PDF delivery is still pending.
No public deployment, commit/push, reviewer-sharing or email action is performed.
Stop after Phase 2; do not automatically start Phase 3.

### Historical checkpoint — Post-PDF obligations
- [x] AS-12 (measured Phase 2 cases): all 21 turns under 60s, individual timings retained.
- [x] AS-13 (core tested boundary): dedicated off-topic/inappropriate intent validation and graceful refusals.
- [x] AS-14: required Marketplace source access already verified; fallback not used.
- [ ] AS-15: final private-repository packaging contains all implementation code.
- [ ] AS-16: comprehensive schema context with remaining 296 undefined-field and
  unsupported statistical/cross-table cases explicitly disclosed.
- [ ] AS-17: clean deployed-demo checks; deferred outside Phase 2.
- [x] AS-18 (CLI only): progress/fast-fail interaction verified in CLI; deployed UX later.
Reviewer handles and reflection's four required content areas are recorded in the
reconciliation report. No deployment, sharing or email action is performed here.

### Historical checkpoint — Phase 2 acceptance and checkpoint
- [x] Five metric families, six real questions, three multi-turn scenarios and
  independent reference SQL comparisons passed (final job 2847530, 16 tests).
- [x] Answer numbers checked against actual SQL, provenance/query IDs retained;
  all measured normal turns <60s; final warehouse confirmed SUSPENDED.
- [x] Core SQL security, non-additive aggregation, ambiguity and service-error
  regression tests pass; failed evaluations preserved with corrected causes.
- [x] Five synchronized documents, PDF reconciliation, Phase 2 report and explicit
  next-session/development-checkpoint policy recorded.
- [ ] Final private-repository reviewer access, hosted threat model and clean public
  demo verification remain pending; core evaluation does not satisfy these.
Development commits/pushes are now explicitly authorized by the user; deployment,
reviewer-sharing changes and submission email are not part of this checkpoint.

### Phase 3 reliability / deployment readiness
- [x] Core process/thread ownership and overlap/reset guards preserve regression APIs.
- [x] Authenticated per-owner state, fresh request-worker connections and shared
  atomic single-warehouse admission avoid unsafe connection/state overlap.
- [x] Shared rate/model-call reserve, bounded sessions/TTL, overload and safe public
  response/logging interfaces implemented; offline tests distinguish mocks.
- [x] Parent/worker deadlines, crash/timeout quarantine and operator recovery tested.
- [x] First independent evaluation recorded honestly: 19/25, failed cases retained;
  subsequent reused cases explicitly classified as regression.
- [x] Final Phase 3 report, 25/25 regressions, real concurrency, Phase 2 16/16,
  <60s measured normal turns, effective grant audit and source/preservation review.
- [ ] Administrator-provisioned restricted identity/role and broad PUBLIC baseline review.
- [ ] Exclusive application warehouse or separately designed concurrency/cleanup policy.
- [ ] Local durable control storage and TLS/token provisioning integrated into hosting;
  multi-host transactional control if deployment needs it.
- [ ] Public UI and clean deployed/security/held-out verification; not implemented here.
- [ ] Final README/Reflection, private reviewer access and authorized final email.
No public UI/deployment or submission email in Phase 3. A core security boundary is
not proof of least-privilege credentials or production-wide factual coverage.

Final Phase 3 scope is complete, not the complete homework/public delivery. Offline
140 passed / 25 live skips; final real job 2848330 passed both suites. First held-out
19/25 and intermediate 15/16 Phase 2 failure remain recorded. Whole-app/deployed
security, restricted identity, hosting, README/Reflection, reviewer access and final
submission remain unchecked. Stop after Phase 3.

### Historical checkpoint — Phase 4 current status (not public-deployment acceptance)
- [x] Streamlit interactive chat over AgentService; bounded per-browser history,
  progress/status, reset/logout, safe errors and source/product/release provenance.
- [x] Shared existing auth/SQLite admission/process isolation and unchanged budgets;
  local isolation/rate/private-output tests pass with clearly labeled Census mocks.
- [x] Public adapter refuses development identity, admin/PUBLIC role, password fallback
  and missing HTTPS/storage/warehouse/permission confirmations; explicit AGENT_PROD
  environment-password mode and optional key-pair transport.
- [x] Deployment configuration/runbook, reviewer instructions, admin SQL proposal,
  no-secret-output token tool and clean-browser smoke runner included.
- [ ] Administrator has reviewed PUBLIC/inherited grants and verified restricted
  service key-pair SELECT/Cortex/suspend access on an exclusive app warehouse.
- [ ] Approved durable host/domain and server-side secrets provisioned; Docker/Caddy
  build/launch and private SQLite volume/restart behavior actually verified.
- [ ] Public HTTPS URL page/auth/data/follow-up/unsupported/isolation/rate/privacy
  and <60s browser checks pass from a clean external client.
- [ ] Application still works after developer SSH disconnect and controlled restart.
- [ ] Final demo URL and actual reviewer credentials privately delivered.
- [ ] Full README/Reflection, final private reviewer permissions and authorized email.
Local tests/configuration do not check AS-5/AS-17 as complete. Phase 4 is blocked, not
ready for final submission. No paid service created, grants changed or email sent.

### Historical checkpoint — Phase 4 DigitalOcean recovery checkpoint — current
- [x] Existing Droplet initialized with security updates, patched kernel, Docker/Compose
  signed repository, boot enablement and successful controlled host reboot.
- [x] Existing root SSH access preserved; nonroot deployment-user key access tested;
  deploy user cannot read server secrets or control Docker.
- [x] UFW only SSH/HTTP/HTTPS; one nonroot app + one proxy, resource/log bounds,
  private mounts and one persistent control volume; public 8501 blocked.
- [x] Actual image build, dependency check, Compose validation/launch and Caddy validation.
- [x] Public trusted HTTPS URL/redirect/headers and clean external browser page verified:
  https://census-104-248-239-52.sslip.io (currently safe unconfigured page).
- [x] Actual SQLite control-probe session survived controlled restart/recreation;
  mode 700/600; public page available after launch SSH exits.
- [x] Server-only Snowflake key and reviewer tokens generated without exposing values;
  exact public-key administrator SQL and permission-review action provided.
- [ ] Administrator provisions/reviews restricted key-pair identity and PUBLIC baseline,
  confirms exclusive existing warehouse; current confirmation flags remain false.
- [ ] Actual hosted-identity SELECT/Cortex/grant/suspension validation.
- [ ] Real reviewer login, questions/follow-up/unsupported/isolation/rate/privacy/latency
  and authenticated post-restart acceptance against deployed URL.
- [ ] Phase 4 acceptance / readiness for Phase 5 or final submission.
Earlier no-host/no-URL notes are historical. Physical hosting is ready; functional
Census deployment is still blocked. Existing 169 offline passes/25 skips and prior
real tests do not replace the unrun deployed data/auth cases. No final email.

### Historical checkpoint — Current production identity checkpoint (supersedes key-pair provisioning requirement)
- [x] AGENT_PROD password provisioned only in owner-only deployment environment;
  production adapter rejects CODEX_APP and never loads development .env.
- [x] Explicit authentication methods; missing/mixed credentials fail closed; optional
  key-pair mount removed from the password deployment. Existing local config preserved.
- [x] Real AGENT_PROD login, bounded SELECT, Cortex and suspension verified with query IDs.
  These probes used PUBLIC/ALL and do not establish approved runtime permissions.
- [ ] Administrator supplies reviewed named role to AGENT_PROD, reviews PUBLIC baseline
  and confirms exclusive warehouse. Exact proposal: deploy/agent_prod_permissions.sql.
- [ ] Live named-role/NONE SELECT/Cortex/cleanup and authenticated public ten-point suite.
- [ ] Final public demo acceptance and submission prerequisites. No Phase 5/email.

### Current Phase 4 functional acceptance — 2026-10-14
- [x] Live trusted HTTPS https://census-104-248-239-52.sslip.io and real reviewer login.
- [x] AGENT_PROD/APP_ROLE/secondary NONE, environment-only production credentials;
  local CODEX_APP uses DEV_WH. No development .env in the deployed app.
- [x] External data/follow-up/unsupported/owner-isolation/auth/prompt-refusal/rate/privacy
  checks pass; factual browser requests 13.0037–17.0037s in recorded final cases.
- [x] Independent role/NONE SQL confirms population 55,639 /55,380; real cleanup verified.
- [x] Controlled restart: exact sessions/states/quota events survive in 0600 SQLite;
  SSH exits before fresh browser authenticates and obtains a real answer.
- [x] Loading indicator and expandable provenance observed in deployed browser.
- [x] Two initial test-runner failures preserved; fixes change no app limits/logic.
- [ ] P1: account-level PUBLIC inheritance cleanup and APP_ROLE explicit OPERATE;
  do not claim strict effective least privilege. No privileges changed by this work.
- [ ] Final README/Reflection, reviewer GitHub permissions, private credential handoff
  and submission email. Functional Phase 4 success is not final-submission readiness.
No Phase 5 started. Evidence and limits: PHASE4_REPORT.md and phase4_activation/.
