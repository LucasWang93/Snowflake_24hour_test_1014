# Progress

## Completed
- Official five-page PDF read/reconciled: 30 canonical requirement IDs, original IDs preserved.
- Phase 1 preserved: catalog, geography, aggregation, tests and stored evidence unchanged.
- Phase 2 core modules/CLI implemented; Cortex structured semantics, canonical SQL,
  grounded results, explicit multi-turn state and bounded failures.
- Offline verification: 58 Phase 2 tests; full suite 116 passed / 25 live skips; Ruff pass.

## In progress
- None within Phase 2. Implementation, evaluation and handoff are complete.
  No Phase 3 work is in progress.

## Blocked
- No core implementation blocker. Final submission still needs absolute receipt time
  and email recipient; public deployment/reviewer access are outside Phase 2.

## Next three actions
1. In a new session, read AGENTS.md and this file, then inspect Git state and PHASE2_REPORT.md.
2. Wait for explicit next-phase authorization; select a minimal public UI/hosting design
   and review restricted identity/session isolation before implementation.
3. Later complete deployed/held-out evaluation, README/Reflection, reviewer access
   and authorized submission. Do not rerun Phase 1 or start those actions now.

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
