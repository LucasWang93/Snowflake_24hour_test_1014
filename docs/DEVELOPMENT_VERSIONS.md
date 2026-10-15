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
the current phase. No session can be opened automatically by this repository. Phase 4
functional public acceptance is complete; resume from PHASE4_REPORT.md/PROGRESS.md
only within new user instructions. Do not automatically start Phase 5.

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

## v0.4.2-dev — AGENT_PROD server-environment authentication
Explicit production-password mode with no development .env fallback, CODEX_APP
rejection and exclusive authentication-method selection; optional legacy key-pair
Compose override. Existing named-role/NONE/review/exclusive-warehouse gates unchanged.
180 offline passes /25 live skips; targeted Phase 4 40 passes. Actual AGENT_PROD
PUBLIC/ALL login, one bounded SELECT, Cortex hello and suspension passed; named app
role is not yet usable/reviewed. Evidence in phase4_production_identity. This is a
validated configuration checkpoint, not complete public Census acceptance. No
Snowflake grant or development credential changes. Tag created after successful commit.

The update is running from /opt/census/releases/prod-env-20261014 (local/deployed
source hashes match), with AGENT_PROD password mode and no image .env/private-key
mount. App healthy, control volume preserved; fresh external HTTPS page observed
safe unavailable state in 1.458s. Permission/exclusivity flags remain closed, public
authenticated checks blocked. Doctor 0, verify 0, preflight 2 (pending items).

## v0.4.3-dev — Phase 4 live public chat acceptance
Tag records server activation with AGENT_PROD/APP_ROLE/secondary NONE and all reviewed
flags, developer warehouse DEV_WH, real public nine-case browser suite plus separate
controlled-restart/SSH-exit authenticated data check. Independent reference SQL agrees
with actual 55,639/55,380 answers. Browser factual times 17.0037s/14.0131s and 13.0037s
after restart. Exact control sessions/states/events survive unchanged.

No Agent/catalog/service or statistical changes; app image/source remains the prior
production-auth build. Browser runner fixes its assertion timeout and uses local
refusals to hit real rate limits; both original runner failures are preserved. Existing
180 offline passes/25 live skips and Ruff retained; final checks recorded in new logs.
Production auth config never reads development .env. Actual PUBLIC learning-role
inheritance remains a documented P1 permission residual, not a least-privilege claim.
No grant/revoke/budget reset or paid infrastructure changes. README/Reflection, private
reviewer access/handoff and submission remain pending; no Phase 5/email. Commit/tag
and authorized push occur only after evidence/diff/secret checks.

## v0.4.4-dev — measured request startup/cleanup improvements
Build-derived fingerprinted complete search index and safe fallback; deduplicate only
already-confirmed warehouse cleanup, invalidating on every new SQL/connection. 11 new
tests; full 191 passed /25 live skips. Exact Alabama result/SQL unchanged; profiled
15.0294s ->13.6739s, public browser 12.9913s, context follow-up 13.0160s, refusal 2.9941s.
No model/warehouse change, statistical result caching, shared connector or new dependency.
Image deployed to latency-20261014 under existing admission lease; SQLite/quotas/secrets
preserved. Initial busy/profile fixture/cache-prototype outcomes retained. No instant
answer/SLA/strict least-privilege claim; prior permission/delivery gaps still visible.

Closeout records cleanup query classification (two permission SHOWs plus one cleanup
SHOW), source-hash match and a separate later diagnostic warehouse STARTED observation;
no mislabeled final SUSPENDED claim. Phase 4 report now contains the fixes/results/
remaining-task handoff directly. No new phase or additional live test for doc sync.

## v0.5.0-prep — final submission preparation, not sent
Docs-only final package: complete README/Reflection, PDF traceability and final audit,
reviewer status, email draft and operational handoff. Production remains v0.4.4-dev;
no source/security/configuration/SQLite-state change or service restart. Final191 offline
passes /25 explicit live skips, Ruff/pip checks pass. Public HTTPS/login plus real
55,639 ->55,380 contextual smoke passed (27.0405s/12.9892s). Budget68/120 used;
no reset. Secret/history check has no high-confidence findings.

Ready NO: GitHub API private=false, all11 effective reviewer grants unverified,
receipt/timezone/recipient not confirmed, monetary headroom not visible to app role.
PUBLIC inherited permission residual retained. Preflight2 is incomplete, not success.
Tag/commit identifies this reviewed preparation state; routine push is authorized.
No email sent. Resolve external delivery facts before claiming final submission.

## v0.5.1-freeze — conservative cleanup and final audit
No tracked evidence/source/test/config deletion or archival move; remove only local
ignored caches, add token/SQLite ignore rules. All original artifacts, failed runs,
SQL references and skills preserved. Current docs distinguish operator-reported
Private/all11 invitations from independent UNVERIFIED API status, and historical
PUBLIC/ALL/blocking checkpoints from deployed APP_ROLE/NONE functionality.
Full191 offline passes /25 live skips, Ruff/pip pass; imports/CLI, links, context,
Git history secret checks and clean tracked-tree verification recorded. Fresh HTTPS
page and health200; no model/data call or remote operation/deploy/restart.
Ready NO: actual receipt/deadline/recipient and authenticated invitation/visibility
confirmation remain missing; credit headroom and inherited permission risk disclosed.
Final preflight2 retained without weakening checks. Tag identifies final cleanup
commit; exact commit is returned by git rev-parse v0.5.1-freeze^{commit} and final handoff.
Routine reviewed push authorized. No email sent and production remains v0.4.4-dev.

## v0.5.2-budget — post-freeze reviewer reliability repair
User-approved actual-submission ledger,1200 rolling24h calls,12/60 request rates,
256 sessions/2h TTL. Preserve legacy events, private DB backup and policy-only
migration. Single warehouse lease/deadline/SQL/stats/auth unchanged. Full203 offline
passes /25 live skips; public Alabama5,024,279 in31.0242s, exactly2 model debits.
No credit-limit or unlimited-availability claim. Production budget-20261015; no
credential/grant change or final email. See BUDGET_FIX_REPORT.md for actual evidence.
