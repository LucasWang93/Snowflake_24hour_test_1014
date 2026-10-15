# Progress

## Current checkpoint — post-freeze budget repair (v0.5.2-budget)
User authorized diagnosis, metering repair, production rollout and real public QA;
requested1200 actual model submissions plus more reviewer request/session capacity.

## Completed
- Root cause: original120/rolling24h budget reserved2 per admission, including local
  failures/refusals.60 requests exhausted it; timestamps had not expired. No midnight
  reset bug: rolling window was working. Old event rows retained, not fabricated calls.
- New model_submissions ledger debits at actual Cortex execute boundary, not admission.
  Local/pre-submit failures count0; submitted/uncertain remote attempts remain charged.
  Per-call cutoff automatically expires after86400s; wrong leases and >2 calls reject.
- Production1200/day,12 requests/principal/min,60 global/min,256 sessions,2h TTL.
  All configurable/validated.55s deadline, single warehouse lease, SQL rules unchanged.
- Private DB backup before policy-only migration; all original sessions/events/gate
  preserved. Release budget-20261015 active; no token/credential/grant changes.
-203 offline passed /25 live skips, Ruff/Bash pass. Public real Alabama2020 answer
  5,024,279 in31.0242s, ledger exactly2 submissions; local refusal checked separately.

## In progress
- Repair, production rollout and verification complete. Integrating the newer remote
  checkpoint before the final authorized push; no additional live test needed.

## Blocked
- No model-budget availability blocker after repair. Finite1200-call cap can still
  legitimately exhaust; it is not a Snowflake credit balance or unlimited allowance.
- Original submission metadata, independent GitHub invitation audit and inherited
  PUBLIC privilege residual remain outside this fix. No submission email sent.

## Next three actions
1. Use existing reviewer token at public demo; no new credentials or budget reset needed.
2. Monitor actual ledger timestamps and credit balance; only change policy through
   approved idle-app/backup/matching-config workflow. Do not clear leases/quarantine.
3. Read BUDGET_FIX_REPORT.md and this checkpoint first in a new session; preserve
   prior evidence and complete remaining submission facts only when authorized.

## Verification evidence
BUDGET_FIX_REPORT.md and budget_fix/ contain tests/build/migration/runtime/public
results. Previous FINAL_SUBMISSION_AUDIT.md is a dated freeze snapshot, not the new
production release. No full Census inventory or Cortex evaluation repeated.

---

## Historical checkpoint — final submission freeze (v0.5.1-freeze)
Scope: conservative local cleanup, documentation reconciliation and offline audit.
Production remains v0.4.4-dev at https://census-104-248-239-52.sslip.io; no deployment,
server restart, credential/grant/warehouse/control-state change or live Cortex calls.

## Completed
- Baseline 230 tracked files (~38 MB) classified; preserve all source/skills/scripts,
  catalog/raw metadata, test assets and referenced historical failures/SQL evidence.
- No tracked deletions/moves. Remove only local disposable caches; add token/SQLite
  ignore rules. Exact inventory/cleanup results in final_submission_checks/.
- README/Reflection and technical docs reviewed against original five-page PDF.
  Correct stale current public-repository/hosting assertions; preserve dated evidence.
- Full offline 191 passed /25 opt-in skips, Ruff/Bash and pip check pass. Manifest/import/
  CLI/search/link/Docker-context checks recorded. Clean tracked export uses existing
  dependencies, not a claimed fresh installation. No secret findings within scan scope.
- Fresh trusted HTTPS page 200 and health 200/ok. Historical actual question/follow-up
  and first independent 19/25 vs reused 25/25 regression retained; no costly live retest.
- FINAL_SUBMISSION_AUDIT.md and token-free email draft prepared. Routine reviewed
  commit/push/tag follow checks; production release remains unchanged.

## In progress
- Final packaging checkpoint recorded by v0.5.1-freeze and DEVELOPMENT_VERSIONS.md.
  Resolve final commit with git rev-parse; final handoff verifies origin/main matches.
- No application implementation or deployment work in progress.

## Blocked
- Receipt timestamp/timezone/recipient remain unknown: PDF only says receipt+24h;
  user confirmation requested. Email unsent and requires explicit send authorization.
- Operator now reports GitHub Private and all 11 reviewers invited. Independently
  UNVERIFIED: no authenticated GitHub API available; unauthenticated404 proves neither.
  The old private=false result in phase5_final/ is historical, not current fact.
- Snowflake monetary headroom remains unverified; prior 52 call units were a dated
  snapshot. Existing inherited PUBLIC learning-role privilege residual is unchanged.

## Next three actions
1. Operator provides receipt/timezone/recipient and authenticated visibility/invitation
   evidence against the exact 11-account list in FINAL_SUBMISSION_AUDIT.md.
2. Confirm trial-credit capacity and attach existing reviewer token privately; never
   commit it, reset budgets or change production merely for submission packaging.
3. Review SUBMISSION_EMAIL_DRAFT.md and authorize a send only when ready. Stop here;
   do not implement new phases or send email automatically.

## Verification evidence
Current report: FINAL_SUBMISSION_AUDIT.md; logs/JSON: final_submission_checks/.
Preflight2 remains PARTIAL due outstanding delivery/historical unchecked items and
precommit worktree; tests pass. Skips/unverified operations are never marked PASS.
New session: read AGENTS.md, this checkpoint, final audit and Git state first.

---

## Historical checkpoint — Phase 5 submission preparation (v0.5.0-prep)
Authorized scope: final audit/documentation/verification and routine reviewed commit/push.
No new Agent features, redeployment or email sending. Public demo remains
https://census-104-248-239-52.sslip.io; deployed application stays v0.4.4-dev.

## Completed
- Final README and root four-topic REFLECTION.md with actual architectural decisions,
  Codex/human roles, independent19/25 vs regression25/25, deployment/latency and limits.
- PDF30-ID traceability reviewed, documentation synchronized, token-free email draft.
- Doctor0; verify0:191 passed /25 opt-in live skips, Ruff and Bash syntax pass; pip check0.
  Offline population search returns three mappings. Evidence in phase5_final/.
- External HTTPS200/login and two actual turns: ACS2020 Autauga55,639 in27.0405s;
  “And in2019?”55,380 in12.9892s. Prior independent SQL references agree.
- Read-only budget after smoke:68/120 reserved units,52 left (~26 admissions), idle and
  unquarantined. No reset/service restart; secret temporary copy removed after smoke.
- High-confidence secret scan of reachable history and eligible files: no findings;
  exact current reviewer tokens checked without printing. Scope/limitations recorded.
- Final preflight2: outstanding delivery items/working tree, not a complete PASS.

## In progress
- Final submission package prepared; reviewed checkpoint commit/push recorded through
  Git and DEVELOPMENT_VERSIONS.md. Production source/config/state left unchanged.
- Waiting for external delivery facts; no feature/deployment work is in progress.

## Blocked
- **AS-9: GitHub API confirms repository PUBLIC (private=false).** No GitHub API auth
  available locally; all11 reviewer invitation/effective access states unverified.
  Operator must make repo Private and add exact PDF handles; see PHASE5_REPORT.md.
- **AS-10:** original receipt timestamp/timezone and final recipient unknown; PDF gives
  receipt+24h only. Narrow relevant connected-mailbox searches found no assignment.
  User asked for confirmation. Email draft remains unsent; signature needs confirmation.
- Snowflake credit headroom unverified: APP_ROLE sees no HOMEWORK_GUARD monitor;
  warehouse reports monitor null. Admin must confirm trial balance/monitor coverage.
  App52-unit allowance is not a monetary-credit guarantee.
- Existing P1 PUBLIC learning-role inheritance remains. No automatic grant/revoke;
  explicit APP_ROLE OPERATE then safe administrator inheritance review remains advised.

## Next three actions
1. Operator makes GitHub repo private and verifies11 reviewers (names/actions in report).
2. Confirm receipt/timezone/recipient, Snowflake credit headroom and private reviewer
   access-note inclusion. Do not commit credentials or reset any quota.
3. Recheck these changed facts, review SUBMISSION_EMAIL_DRAFT.md, request explicit
   authorization before sending. Stop after preparation; do not start another phase.

## Verification evidence
See PHASE5_REPORT.md and phase5_final/{verify.log,dependencies.log,doctor.log,
public_smoke.json,runtime_budget.json,snowflake_budget.json,github_probe.json,
secret_audit.json,traceability.json,preflight.log}. Historical evaluation failures
remain under slurm_runs/ and phase4_*; none was overwritten or relabeled held-out.

New session: read AGENTS.md and this current checkpoint first, then PHASE5_REPORT.md,
CHALLENGE_SPEC.md and Git state. Resume only remaining delivery facts; do not repeat
Census discovery/full evaluations, redeploy the demo or send email without authorization.

---

## Historical checkpoint — Phase 4 latency fixes completed (v0.4.4-dev)

- Same Alabama 2020 decennial result: 5,024,279, identical SQL and parameters. Paired
  profiled service 15.0294s ->13.6739s; clean public browser 12.9913s; contextual follow-up
  13.0160s; guarded refusal 2.9941s. Modest measured gain, not instant response/SLA.
- Image-built fingerprinted complete BM25 index avoids repeated construction;
  physical validation/fallback preserved. Confirmed cleanup is not repeated on close;
  any new SQL/failure/connection invalidates that observation.
- Final verification: 191 passed /25 live skips, Ruff passes; new module 11 passed.
  Source hashes match deployed healthy release /opt/census/releases/latency-20261014.
  APP_ROLE/AGENT_PROD/environment credentials and existing security/control limits stay.
- Profiled request cleanup confirmed suspension. A later diagnostic snapshot observed
  STARTED with no active lease/quarantine; preserve this separate fact, do not claim
  the latest snapshot was SUSPENDED. No new investigation during documentation closeout.
- Evidence/limitations: PHASE4_REPORT.md, PHASE4_LATENCY.md, phase4_latency/. First busy
  attempt/cache prototype/fixture failure and earlier phase evidence remain preserved.
- Read AGENTS.md and this file first in the next session. Scope completed; no next
  phase started. Await the next specific task before final-delivery work.

## Historical v0.4.3 checkpoint — Phase 4 public chat activated
Authorized scope: Phase 4 only. User confirmed APP_ROLE and exclusive application
warehouse; do not start Phase 5 or send submission email. New sessions read AGENTS.md,
PROGRESS.md and current PHASE4_REPORT.md first, then inspect Git/current configuration.
Working plan/acceptance completed: verified APP_ROLE/NONE -> enable server config ->
external nine-case browser suite -> independent SQL -> restart/persistence/real answer.

## Completed
- Public HTTPS Census Chat: https://census-104-248-239-52.sslip.io.
- AGENT_PROD/APP_ROLE/secondary NONE, password solely from deployment environment;
  no development .env fallback. Three reviewed gates now 1; existing controls preserved.
- CODEX_APP local .env warehouse changed to DEV_WH; actual context-only connection
  verified. Production remains SNOWFLAKE_LEARNING_WH; no local credential values shown.
- Final nine clean external browser checks pass: auth/invalid token, factual population,
  multi-turn, unsupported year, independent owner, prompt refusal/rate and visible privacy.
- Actual ACS Autauga population: 2020 55,639 (17.0037s), 2019 follow-up 55,380 (14.0131s).
  Independent LIKE-based SQL agrees; 45/32 distinct CBGs, no invalid counts.
- Controlled app/proxy restart preserves exact session/state/event hashes, private
  SQLite volume and 0600 permissions. SSH ended before fresh authenticated browser;
  real 2020 answer succeeds in 13.0037s; loading/provenance observed.
- First assertion-timeout failure and later rate-test failure preserved. Only browser
  test runner adjusted; core Agent/catalog/AgentService/tests unchanged.
- Evidence in docs/phase4_activation; 109 protected source/test/catalog/old-evidence
  files match dc24cc4, 30 requirement IDs remain unique with verification methods.
- Doctor exit 0; verify exit 0; final preflight exit 2: 180 passed /25 live skips,
  Ruff passes; unchecked final-delivery items and precommit tree are incomplete, not
  failures. Both app/proxy running, warehouse SUSPENDED, control not quarantined.
- Final snapshot: 48/120 rolling reserved-call units consumed; 72 remaining (~36
  admissions). This is an observation, not a reset or guarantee for later users.

## In progress
- Phase 4 functional work and latency follow-up complete; current checkpoint v0.4.4-dev.
- No next phase started; remaining work awaits user direction/operator permission review.

## Blocked
- Functional demo is available; strict account-level least privilege remains open.
  PUBLIC still inherits SNOWFLAKE_LEARNING_ROLE (learning DB CREATE SCHEMA, production
  warehouse USAGE/OPERATE/MONITOR). This contradicts the direct-grant audit; do not
  describe CODEX_APP as permission-isolated from production. Operator exclusivity is
  operational. APP_ROLE cleanup currently inherits OPERATE from PUBLIC.
- P1: operator should grant warehouse OPERATE explicitly to APP_ROLE, review/remediate
  PUBLIC inheritance while preserving development access, then verify role/NONE again.
  No grant changes/revokes performed here; default PUBLIC CORTEX_USER can remain.
- Final README/Reflection, repository reviewer access and private token handoff/email
  remain pending. No final-submission readiness or Phase 5 completion claim.

## Next three actions
1. Use private reviewer token to access the public URL; instructions in REVIEWER_ACCESS.
   Preserve /etc/census/app.env, tokens and census_census_control volume on Droplet.
2. Operator reviews remaining inherited warehouse/schema privileges; explicitly grant
   APP_ROLE OPERATE before removing any inherited cleanup access. Do not reset budgets.
3. Await user's next-phase instruction before final README/Reflection/access/submission
   work. Current functional Phase 4 verification is complete; do not redo discovery.

## Historical harness / configuration evidence
The following preparation and Phase 1 records retain the context at their original
time. Current scope/status is above and in PHASE2_REPORT.md when finalized.

## Verification evidence
Preparation checks run on 2026-10-14 with Python 3.11.13:

| Command/check | Observed outcome |
| --- | --- |
| `python3 -m venv .venv` | Exit 0; isolated environment created |
| `.venv/bin/python -m pip install 'pytest==8.4.2' 'ruff==0.14.0'` | Exit 0; development tools installed |
| `./scripts/doctor.sh` | Exit 0; tool versions inspected; no application environment keys declared |
| `./scripts/verify.sh` | Exit 2; all three Bash syntax checks pass; Ruff skipped (no Python source); pytest collected zero tests |
| `./scripts/preflight.sh` | Exit 2; pending templates and untracked harness files reported; no candidate secret filenames detected |
| `python3 /gpfs/radev/home/sw2572/.codex/skills/.system/skill-creator/scripts/quick_validate.py <skill-directory>` (each of six skills) | All six report valid |
| `.venv/bin/python -m pip check` | Exit 0; no broken requirements |
| `git diff --check` and alternate-index staged diff check | Exit 0; no whitespace errors |
| Isolated temporary-repository harness smoke checks | Nine expected exit-status checks passed; no challenge solution or benchmark involved |

The isolated checks covered: absent suite (2), successful formatting/lint/tests (0),
failing tests (1), failing lint (1), tracked ignored credential filename (1), missing
documentation section (1), pending documents (2), and missing interpreter in doctor
and verify (1 each). Fixtures were empty credential filenames and trivial harness-only
Python tests, outside this repository. An initial same-size fixture rewrite reused
cached bytecode; the smoke check was rerun with `PYTHONDONTWRITEBYTECODE=1` and passed.

ShellCheck is unavailable and explicitly skipped. No actual challenge functionality,
external service integration, evaluation baseline, or clean application reproduction
has been tested. Document checks are structural, and secret checks use filenames only.
Harness baseline is being committed locally at the user's request; original README
and initial history are preserved. No remote push is included.

## Activation commands
```bash
python3 -m venv .venv  # only if an environment is not already present
.venv/bin/python -m pip install -r requirements-dev.txt
./scripts/doctor.sh
./scripts/verify.sh     # exit 2 is expected until code/tests are configured
./scripts/preflight.sh  # exit 2 is expected until requirements/docs/review are complete
```
When the challenge arrives, read its rules first and invoke `$challenge-intake`.
If AI assistance is forbidden, stop AI-assisted challenge work. Otherwise populate
the specification and traceability before choosing architecture or implementation.

## Initial baseline submission — 2026-10-14
At the user's request, ran `bash scripts/doctor.sh` (exit 0),
`bash scripts/verify.sh` (exit 2), and `bash scripts/preflight.sh` (exit 2), in that
order before the local harness commit. Incomplete statuses reflect absent challenge
code/tests, pending templates and pre-commit working tree changes; no challenge
gate was marked passed. All three Bash syntax checks passed. ShellCheck remains
unavailable. The commit contains preparation files only.

## Snowflake configuration slice — 2026-10-14
Completed real authenticated tests using connector 4.8.0. See `snowflake_config.md`,
`docs/snowflake_evidence.json` and `docs/snowflake_metadata.json` for query IDs,
counts, schemas, samples, model outputs/errors and warehouse state.

- 71 tables + 2 views discovered; all 73 COUNT(*) queries succeeded.
- Three core tables sampled: 2020_CBG_B01 (161 columns),
  2020_REDISTRICTING_CBG_DATA (299 columns), and
  2020_METADATA_CBG_GEOGRAPHIC_DATA (5 columns).
- Live COMPLETE: llama3.1-70b 0.741s, llama3.3-70b 1.875s, mistral-7b 0.746s.
  gemma2-9b failed with unknown model after 20.953s; no retry.
- Actual region: AWS_CA_CENTRAL_1. Provided us-east-1 was incorrect.
- Warehouse X-Small, AUTO_SUSPEND=60, AUTO_RESUME=true; ALTER SUSPEND succeeded
  after full tests and metadata checks; SHOW confirmed SUSPENDED both times.
- `.env` ignored and owner-only; includes a tested default model.
- No background agent/server deployed. Full chat-agent correctness is untested.
- Current changes are local and uncommitted; no push is included in this slice.

Final local checks for this slice: `bash scripts/doctor.sh` exit 0;
`bash scripts/verify.sh` exit 0 (Ruff formatting/lint and 14 unit tests pass);
`bash scripts/preflight.sh` exit 2 (full challenge templates and local changes
remain pending); `pip check` and `git diff --check` exit 0. ShellCheck skipped.
Doctor does not load .env; process-variable MISSING messages do not invalidate
the live connector verification that explicitly loads the authorized .env.

## Phase 1 working plan
Acceptance: full-family verified mappings, five required search cases,
year/product-aware geography, fail-closed aggregation and evidence-backed tests.
In progress: acquire only missing dictionaries/FIPS/schema metadata.
Next: (1) reconcile dictionary IDs with physical columns; (2) implement local
search and safe geography/aggregation; (3) run targeted real tests and report.
Existing environment/artifacts and Git history will be preserved.

## Phase 1 completed
Built full-family machine-readable catalog and offline retrieval, FIPS geography
utilities and guarded aggregation. All supplied field definitions map to exact
physical schema; 296 undefined columns explicitly quarantined. Five required
search cases pass; nine targeted real integration tests passed. Warehouse suspended.
See PHASE1_REPORT.md for evidence, commands and limitations.
Next actions: none in this phase. Stop and await explicit instructions; do not
implement a UI/agent or automatically begin Phase 2.

Final Phase 1 local verification: `bash scripts/verify.sh` exit 0, Ruff pass,
58 passed / 9 explicitly skipped live tests. Separate opt-in run: 9 real tests
passed, warehouse suspended. Existing infrastructure/artifact preservation hashes
verified unchanged and `.env` remains ignored/untracked/mode 600. No Phase 2.

`bash scripts/preflight.sh` exit 2: full homework templates and local changes
remain pending; its Ruff/test checks passed. Phase 1 scope is complete, not a
claim that all homework delivery gates are complete.

## Phase 2 active plan
PDF read in full and reconciled (30 IDs, prior IDs preserved). AI explicitly allowed.
Acceptance: 5 metric families, 3 multi-turn scenarios, verified numbers/SQL/query IDs,
unsafe SQL cannot execute, bounded Cortex/SQL, graceful failures and <60s live turns.
Slices: typed intent/context -> catalog selection -> canonical SQL/validation ->
Cortex/connector/permission audit -> grounded answer/CLI -> offline and bounded live
evaluation -> hardening/report/docs. Preserve all Phase 1 files/evidence; no deployment.

## Phase 2 completed / new-session handoff
- Implemented reusable `census_agent` core, local CLI, Cortex intent/catalog choice,
  canonical SQL validation, grounded answers, explicit state and safe failures.
- PDF reconciled: prior 23 IDs retained, seven additions, 30 with verification methods.
- Real acceptance: job 2847530, 16 passed; six questions across five families,
  three conversations, independent reference SQL and negative/security cases.
- Full offline verification: 116 passed / 25 explicitly skipped; Ruff pass.
- Failed live runs and root causes preserved; final cleanup confirmed SUSPENDED.
- Phase 1/configuration preserved byte-for-byte for 27 recorded files.
- Key decisions: one constrained workflow; model proposes semantics/IDs, not SQL
  or numbers; only additive counts sum; CBG-only medians/means/MOEs; exact category
  constraints; PUBLIC/ALL preserves existing direct-user data access; finite
  timeouts, no application retries and per-turn suspension.
- Limitations: 296 undefined fields, unknown survey interval, bounded lexical/model
  recall, unsupported ratios/cross-table/cross-year/city/place calculations,
  unverified full geographic coverage; broader user grants and synchronous shared
  backend need review before hosting. No production SLA/credit-cost claim.
- Remaining tasks: public conversational UI/deployment; restricted hosted identity,
  per-session lifecycle and guardrails; clean browser/deployed/held-out evaluation;
  README and four-topic Markdown Reflection; private GitHub reviewer permissions;
  receipt deadline/recipient and final authorized email. These are not executed.
- User authorized GitHub checkpoints after completed phases or substantial changes.
  Foundation commit `baf2cca`; Phase 2 commit identified by `v0.2.0-dev` and
  docs/DEVELOPMENT_VERSIONS.md. Read AGENTS.md + PROGRESS.md first in a new session.
- Stop after Phase 2. No public deployment or automatic Phase 3.

Final preflight: exit 2; its Ruff/offline checks pass (116 passed / 25 live skips).
Incomplete status reflects outstanding full-homework delivery and checkpoint staging;
not a Phase 2 test failure. GitHub checkpoint versions: v0.1.0-dev / v0.2.0-dev.

## Phase 3 working plan — 2026-10-14
Acceptance: existing regressions pass; distinct frozen factual/negative/conversation
cases with independent SQL; concurrent owners cannot share state/connections; bounded
wall-clock requests; shared rate/model-call budgets and authentication fail closed;
no diagnostic secrets; graceful provider/overload errors; measured normal turns <60s.
1. Harden core ownership/deadlines and add authenticated process-isolated service.
2. Implement SQLite atomic session/admission/budget control (one active trial query),
   public diagnostic filtering and safe logs; test concurrency/failure boundaries.
3. Freeze independent cases before live evaluation; run bounded real tests and audit
   visible permissions, preserve failures, then report/development checkpoint.
No inventory scan, UI, deployment or final email. Preserve Phase 1/2 evidence.

## Phase 3 completed / handoff — 2026-10-14
Implemented `control.py` and `service.py`; hardened core/backend/types/planning and
added `evaluation/phase3.py`, frozen cases and 24 new reliability tests. No new
application dependencies, full inventory scan, grant/credential changes or public UI.
54 original Phase 1/2/config/evidence files retain their recorded hashes.

First frozen independent run 2848148: 19/25 (6/9 factual, 3/5 conversation turns,
10/11 negative). Fixes preserve literal household counts/product ambiguity, verified
tenure/poverty labels and original wording retrieval. Run 2848266: 25/25 regression.
Phase 2 regression 2848270: 15/16 (omitted educational metric), corrected with explicit
context rule/test. Final combined 2848330: all 25 Phase 3 + all 16 Phase 2 real tests
pass, warehouse suspended. First and intermediate failures were never overwritten.

Decisions: disposable processes with parent 55s deadline; one shared warehouse lease
rather than unsafe concurrent suspend; owner-bound state/auth with local transactional
budgets; safe public projection and whitelisted logs; quarantine uncertain server
cleanup until verified operator recovery. Model emits semantics/IDs, never executable
SQL or statistics. PUBLIC/ALL preserved because restricted grants cannot be safely
provisioned from demonstrated rights; admin migration is a hosting blocker.

Limits: first held-out accuracy was 19/25; later success is regression, not fresh
blind accuracy. More held-out/deployed validation needed. SQLite is single-host with
shared local file/limits; no multi-host claim. Throughput intentionally one active
request; actual credit cost unmeasured. 296 unknown fields, unknown ACS interval,
coverage/city/cross-year/ratio/complex-join limitations remain. No least-privilege,
public-deployment or complete security certification claim.

Development checkpoint: v0.3.0-dev; see DEVELOPMENT_VERSIONS.md and Git tag for exact
commit. User's regular checkpoint/validated-change commit policy remains active.
Stop here; continue a new session only within the next authorized scope.

## Phase 4 implementation checkpoint — 2026-10-14 (deployment blocked)
- Implemented authenticated Streamlit UI, private per-browser history/reset/logout,
  progress, public-only answers and allowlisted provenance over existing AgentService.
- Added fail-closed dedicated key-pair deployment config; backend optional trusted
  config preserves operator CLI defaults. No new Agent/statistical features.
- Docker/Caddy single-instance/private-volume configuration, admin SQL proposal,
  reviewer/token runbook and external HTTPS browser runner created. No paid resources,
  grants, credentials or warehouse settings changed.
- Actual offline: 29 new tests pass; full verify exit 0, 169 pass / 25 opt-in live skips,
  Ruff pass. Loopback unconfigured HTTP health/page 200; test subprocess stopped.
  No public browser/data/TLS/SSH-persistence claim and no new live Cortex/SQL calls.
- Existing Phase 1–3 data/test/report/evaluation hashes retained; see preservation audit.
- Blocking inputs: approved persistent host/domain and restricted Snowflake key-pair
  identity with reviewed PUBLIC baseline/exclusive warehouse. No public URL.
- Version v0.4.0-dev is a partial development checkpoint, not Phase 4 completion.
  Resume only this deployment when inputs change; do not advance phases or send email.

Final Phase 4 preparation preflight: exit 2 (unchecked deployment/full-delivery items
and precommit changes); its Ruff/tests pass, 169 passed / 25 skipped. No deployed
acceptance or clean Docker reproduction is claimed. Current evidence is retained in
docs/phase4_checks; resume Phase 4 only after host/admin prerequisites are available.

## Phase 4 SPCS read-only feasibility — 2026-10-14
- Read-only account/pool/family/grant inspection completed; 17 metadata statements,
  including one denied session-only ACCOUNTADMIN activation. No resource/grant/billing
  changes, image build, data scans or Cortex calls. Warehouses remain SUSPENDED.
- Regional/account metadata available: 27 families and two suspended system pools.
  Current CODEX_APP deployment is BLOCKED: no CREATE COMPUTE POOL privilege and
  ACCOUNTADMIN activation denied (003013/42501). Current Trial/paid status UNVERIFIED;
  documented SPCS Trial exclusion means upgrade is conditional on admin confirmation.
- SPCS migration is feasible in principle, not selected/provisioned: managed OAuth
  adapter, one persistent block volume/service instance, UID/SQLite checks and reviewer
  Snowflake ingress access are needed. See SPCS_FEASIBILITY.md and captured query IDs.
- App/config and all prior evidence unchanged. Wait for explicit approval before any
  Snowflake resources; no Phase 5. Checkpoint tag: spcs-feasibility-20261014.

## Phase 4 DigitalOcean recovery — 2026-10-14
- Initialized approved existing Droplet; security/kernel updates, controlled reboot,
  official Docker/Compose, key-based root/nonroot SSH and UFW 22/80/443 verified.
- Actual application image built. App/proxy running, nonroot app, bounded resources/logs,
  private server key/env and persistent SQLite. No development credentials/history copied.
- HTTPS https://census-104-248-239-52.sslip.io externally verified with Let's Encrypt,
  redirect/security headers, closed 8501 and clean-browser safe unavailable page.
- SQLite probe survived app/proxy restart and container recreation; 700/600 permissions.
  Page remains available after launch SSH exits. Authenticated use remains untested.
- New service RSA private key stays on Droplet; exact public-key SQL supplied for admin;
  two reviewer tokens remain server-only. No Snowflake grants/billing/resources changed.
- Genuine blocker: administrator identity/PUBLIC review/exclusive-warehouse confirmation.
  Both corresponding runtime flags remain 0; no unsafe fallback or invented E2E results.
- Actual local regression 169 passed /25 skipped; external page loads 1.258/1.221s,
  not data-answer latency. Evidence under docs/phase4_recovery.
- Existing Agent/catalog/Web source and prior recorded evidence preserved (89 hashes).
  Checkpoint v0.4.1-dev is infrastructure-ready, not Phase 4 acceptance or Phase 5.

Recovery preflight exit 2: outstanding administrator/public functional/final-submission
items and precommit changes. Its Ruff/tests pass (169/25); not a data-readiness pass.
Ubuntu left three phased updates deferred; running patched kernel 6.8.0-147 and
key-only SSH verified. Server no longer needs host or DNS provisioning; admin identity
and privilege/exclusivity confirmation are the remaining functional blocker.

## Reusable skill captured — v0.5.3-skills
User requested retaining these lessons for future projects. business-first-delivery
now exists as a versioned .agents skill and matching personal ~/.codex/skills copy.
Six existing skills plus AGENTS link to business coverage/feasibility/false-refusal
and end-to-end readiness gates. No app/deployment or new live call. Structural
validation, copy/reference checks and full203 offline passes /25 live skips verified.
See SKILL_CAPTURE.md. Existing uncommitted diagnostic/proposal work remains separate;
no redesign implementation is authorized by creating this skill.
