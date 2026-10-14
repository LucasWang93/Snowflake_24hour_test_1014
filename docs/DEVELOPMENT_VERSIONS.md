# Development versions

The user authorized GitHub checkpoints after each completed phase or substantial
validated change. Preserve failed-run evidence, review diffs/secret exclusions,
run appropriate checks, commit and push the existing branch without force.
Each later checkpoint must update this log and PROGRESS.md with actual evidence.

| Version | Checkpoint | Git reference | Verification / limitations |
| --- | --- | --- | --- |
| harness | Preparation harness | `6497c8e` | Historical harness checks; no application claims |
| v0.1.0-dev | Snowflake foundation and Phase 1 semantic catalog | `baf2cca` | 58 offline checks and saved 9 real Phase 1 passes; original artifacts unchanged |
| v0.2.0-dev | Phase 2 core conversational agent and original-PDF reconciliation | `b038e3b` / tag `v0.2.0-dev` | 58 Phase 2 offline / 16 real tests; full offline 116 passed + 25 skips; <60s live turns; no UI/deployment or final submission claims |
| v0.3.0-dev | Phase 3 reliability/auth/admission/deadlines and independent evaluation | Tag `v0.3.0-dev` | 140 offline pass + 25 skips; first held-out 19/25, final regressions 25/25 plus Phase 2 real 16/16; no UI/deployment |
| v0.4.0-dev | Phase 4 authenticated Web adapter and deployment preparation (BLOCKED, partial) | Tag `v0.4.0-dev` | 169 offline passed / 25 live skips; 29 new adapter/deployment checks; no public URL, real key-pair or external browser/SSH-persistence evidence |

`git log --oneline` and `git show v0.2.0-dev` identify the exact Phase 2 commit.
Tags are created only after the corresponding commit succeeds. This file is a
development record, not proof of GitHub reviewer permissions or full delivery.

## Continue in a new Codex session

Read `AGENTS.md` and `docs/PROGRESS.md` first, inspect Git state, then read the
current specification, architecture, decisions, evaluation plan and phase report.
Reuse the configured environment and Phase 1 artifacts. Do not rerun discovery.
Resume only the authorized scope; wait for the user's next-phase instruction after
Phase 3. No session can be opened automatically by this repository. Current authorized scope is
Phase 4; public hosting is blocked. Resume from PHASE4_REPORT.md and DEPLOYMENT_RUNBOOK.md
when host/admin inputs change; do not automatically start a later phase.

## Phase 4 feasibility checkpoint — 2026-10-14
`spcs-feasibility-20261014`: documentation-only SPCS/account/grant assessment, with
17 actual metadata outcomes, 27 families and explicit blocked/unverified distinctions.
Application remains v0.4.0-dev, unchanged. No resources/permissions/billing or Docker
changes; no repeated full tests because implementation is unchanged. Prior tracked
files were verified unchanged before appending these two checkpoint/handoff records;
79 preservation hashes still match. Resource creation requires explicit new approval.

## v0.4.1-dev — DigitalOcean HTTPS infrastructure recovery
Tag v0.4.1-dev records the actual Droplet build/launch, trusted public HTTPS, clean
external browser unavailable-page and SQLite restart/recreation evidence, plus bounded
proxy/log configuration and exact public-key administrator SQL. Agent/catalog/Web
Python source and previous evidence unchanged. 169 offline passed /25 live skips.
Source deployed from 08e5bfb plus this checkpoint's Compose hardening; running image
hashes are recorded separately. Admin flags remain false; no real hosted data/auth
acceptance or Phase 4 completion claimed. Snowflake grants/billing unchanged.
