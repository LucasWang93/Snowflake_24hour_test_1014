# Progress

## Current checkpoint — production identity environment switch
- Authorized scope: complete Phase 4 with AGENT_PROD supplied via deployment secrets/
  environment only. CODEX_APP remains local development only; do not start Phase 5.
- Working plan: (1) inspect production grants; (2) implement/test explicit production
  auth without .env fallback; (3) deploy while preserving security gates/control volume;
  (4) record real connection results and remaining operator actions; checkpoint Git.
- Acceptance: production connector receives AGENT_PROD credentials solely from server
  environment; missing/mixed credentials and developer identity fail closed; existing
  security controls and local configuration remain intact. No fabricated hosted answers.

## Completed
- Prior Phase 1–3 and Phase 4 HTTPS infrastructure evidence preserved.
- AGENT_PROD secret provisioned only in Droplet /etc/census/app.env (0600); no password
  in repository or local development .env. Production auth reads os.environ explicitly.
- Fresh production identity login, bounded SELECT and llama3.3-70b COMPLETE succeeded;
  explicit suspension succeeded and SHOW confirmed SUSPENDED. Evidence/query IDs:
  phase4_production_identity/connection_probe.json and permissions.json.
- These operator probes used observed PUBLIC/ALL, not the approved public runtime role.

## In progress
- Phase 4 public data activation awaits operator role/review/exclusivity inputs.
  Production environment-auth code is deployed, with closed security gates.
- Verified checkpoint v0.4.2-dev: 180 passed /25 live skips; targeted Phase 4 40 passed;
  doctor exit 0, verify exit 0, preflight exit 2 (pending delivery items/working tree).
- New app/proxy recreation completed healthy at /opt/census/releases/prod-env-20261014;
  exact deployed source hashes match local changes. Control volume/0600 DB retained;
  container has AGENT_PROD password mode, no /app/.env and no key-file setting.
- External clean Chromium after update: HTTPS 200, safe unavailable page in 1.458s,
  no chat input or observed private markers. This is page latency, not answer latency.
- Evidence: docs/phase4_production_identity/{deployment,deployed_config,
  external_after_update,audit}.json plus actual test logs. Prior manifest: 86/89
  unchanged, three intentional source/test changes; old evaluation artifacts intact.

## Blocked
- AGENT_PROD has 77 direct grants but no visible named account role. Runtime requires
  reviewed nonadmin application role with secondary NONE; CENSUS_APP_READONLY lookup
  returned 002003/02000. PUBLIC still inherits learning database CREATE SCHEMA and
  warehouse OPERATE/MONITOR; a new username alone does not prove least privilege.
- Operator must execute/review deploy/agent_prod_permissions.sql, review PUBLIC baseline
  and confirm exclusive application use of SNOWFLAKE_LEARNING_WH. No grants altered.
- CENSUS_PERMISSIONS_REVIEWED and CENSUS_EXCLUSIVE_WAREHOUSE remain 0. Public URL
  https://census-104-248-239-52.sslip.io remains unavailable for Census chat pending review.
- Authenticated public acceptance remains unrun. Final README/Reflection, repository
  reviewer access and submission email remain outstanding; no Phase 5 or email work.

## Next three actions
1. New session: read AGENTS.md, PROGRESS.md and current PHASE4_REPORT.md; inspect Git.
2. Operator supplies reviewed role (proposed CENSUS_APP_READONLY) and warehouse
   exclusivity confirmation. Do not expose secrets or execute unapproved grant changes.
3. Verify actual role/NONE SELECT/Cortex/suspend, enable only confirmed gates and run
   external authenticated smoke suite plus restart checks. Preserve SQLite volume.

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
