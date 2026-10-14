# Phase 4 production identity update — 2026-10-14

Current scope: operator-provided AGENT_PROD uses deployment secrets/environment.
No development .env is copied, read or used as production fallback. This update
supersedes the earlier proposed new key-pair user; historical recovery evidence below
remains valid at its original checkpoint. Public Census acceptance is still blocked.

## Implemented and verified
- Explicit SNOWFLAKE_AUTH_MODE=password accepts only AGENT_PROD; credentials come
  from os.environ and are injected into isolated AgentService workers. CODEX_APP,
  missing values, mixed authentication and PUBLIC/admin primary roles fail closed.
- Key-pair mode remains available through deploy/compose.keypair.yaml; base password
  deployment no longer mounts a private key. Existing server key is preserved unused.
- Production credential stored only in /etc/census/app.env, mode 0600. No local .env
  modification, credential in source/Git, user/role/grant changes or new resources.
- Offline verification: **180 passed / 25 live skips**, Ruff formatting/lint passed;
  Phase 4 targeted **40 passed** (11 new production-auth checks). Mock connector tests
  explicitly fail if the development .env loader is invoked. Skips are not live passes.
- Actual AGENT_PROD Droplet login succeeded. Bounded SELECT of existing verified schema
  returned CBG 010010201001, B01003e1=674 (1.117s). llama3.3-70b COMPLETE returned
  Hello! (0.802s). Explicit suspension succeeded and SHOW confirmed SUSPENDED.
  Query IDs and raw nonsecret outcomes: phase4_production_identity/connection_probe.json.

## Deployed configuration and external check
New release `/opt/census/releases/prod-env-20261014` is active via `/opt/census/current`.
App and proxy recreated successfully; app healthy. Runtime/Compose hashes match local
source. Container reports AGENT_PROD/password, password present (value never output),
no private-key setting and no /app/.env. Durable SQLite DB remains mode 0600 and the
existing operator probe file remains on the same volume. No volume was removed.
New external clean browser: trusted HTTPS HTTP 200, safe unavailable page in 1.458s;
no chat input or observed private markers. Confirmation flags remain 0/0/1 for
permissions/exclusivity/storage. Evidence: deployment.json, deployed_config.json and
external_after_update.json. Prior preservation manifest: 86/89 unchanged; only backend
comment, runtime and Web tests changed. Doctor exit 0; verify exit 0; preflight exit 2
reflects pending delivery items/precommit changes, not failed tests. Detailed logs kept.

## Remaining security prerequisite / operator action
The real probe used AGENT_PROD with PUBLIC/ALL, not the hosted named-role/NONE
configuration. Grant inspection found 77 direct user grants, 110 PUBLIC grants and
no visible app-role membership; CENSUS_APP_READONLY lookup returned 002003/02000.
PUBLIC inherits SNOWFLAKE_LEARNING_ROLE with CREATE SCHEMA and warehouse OPERATE/
MONITOR. New username and working Cortex access do not prove least privilege.
See phase4_production_identity/permissions.json; no full data inventory was repeated.

Exact administrator proposal: **deploy/agent_prod_permissions.sql**. It grants a
named read-only data/Cortex role with usage/operation of the existing warehouse to
AGENT_PROD; it does not create a user/warehouse, change passwords or revoke development
access. Administrator must separately review inherited PUBLIC grants and confirm
exclusive application use of SNOWFLAKE_LEARNING_WH. Application gates remain 0 until
those facts are confirmed; no silent PUBLIC/ALL fallback or removal of Phase 3 controls.

Public URL remains https://census-104-248-239-52.sslip.io with a safe unavailable page.
Authenticated public ten-point acceptance is still unrun, not passed. Real production
connectivity timings above are not agent end-to-end answer latency. No Phase 5/email.

---

# Phase 4 recovery — DigitalOcean deployment

**Current status: HTTPS infrastructure deployed; authenticated Census service BLOCKED
on Snowflake administrator provisioning/review. Phase 4 is not accepted as complete.**

Public entry point: **https://census-104-248-239-52.sslip.io**. It currently displays
an explicit safe configuration-unavailable page. It is not yet a working Census demo.
All subsequent initial-checkpoint notes below are historical, not current host status.

## Actual recovery work — 2026-10-14

- Existing Droplet 104.248.239.52 initialized; Ubuntu security/user-space updates and
  kernel upgraded to 6.8.0-147, then controlled host reboot completed. SSH still works.
- Ubuntu deferred three phased updates (apparmor/libapparmor1/open-vm-tools);
  those were not forced. Password/keyboard-interactive SSH authentication is disabled;
  root and deploy-user password status locked; existing key access remains.
- Docker Engine 29.9.1 and Compose plugin 5.6.0 installed from Docker's signed repository;
  Docker enabled at boot and observed active after reboot. No new paid infrastructure.
- Created locked-password `census-deploy` user, tested existing SSH key login, retained
  root key access. Deploy user cannot read server secrets or access Docker socket.
- UFW active, default inbound deny, only TCP 22/80/443 allowed (IPv4/IPv6). Port 8501
  is not published; external connection test fails as intended.
- Transferred a Git allowlist of application/catalog/deployment files only. No development
  .env, SSH private keys, Slurm/history/diagnostic artifacts copied. Built the actual image
  on Droplet; image pip check passed. Existing Agent/catalog/Web Python source unchanged.
- Running `census-app-1` (healthy, UID 10001) and `census-proxy-1` (Caddy 2.10.2).
  Compose retains one app/one proxy, local persistent volume, private mounted key/env,
  restart policies, 55s service deadline and existing shared budgets/lease/quarantine.
  App bounded to 2 GiB/2 CPUs/64 PIDs; proxy 256 MiB/0.5 CPU/64 PIDs and minimum bind
  capability. Both use no-new-privileges and rotated local logs (10 MB × 3). Proxy uses
  its image default root user with reduced capabilities; application runs nonroot.
- Server-only Snowflake RSA key generated once, mode 400/UID 10001; private key never
  left Droplet. Two random reviewer token/digest pairs generated under root-only
  `/var/lib/census-operator/reviewers`; tokens never printed or committed.
- Administrator SQL with the actual matching **public** key is in
  `deploy/digitalocean_admin.sql` and `/etc/census/admin_provision.sql`. It reuses the
  existing warehouse. No Snowflake users/roles/grants were created by Codex.
- One local read-only SHOW DATABASES confirmed IMPORTED DATABASE; query ID is saved
  in `phase4_recovery/database_kind.json`. No Census scans or Cortex calls repeated.
- PUBLIC learning-role/schema-creation inheritance still requires admin review;
  see `phase4_recovery/ADMIN_ACTION.md`. Primary-role naming alone does not establish
  effective read-only credentials. No unapproved revokes or development fallback.

## Actual public verification and failures

| Phase 4 acceptance | Actual observed outcome |
| --- | --- |
| 1. Public page loads | PASS for deployed page: external Yale HTTP 200 and fresh Chromium context render Census Chat |
| 2. Reviewer authentication | BLOCKED / NOT RUN: administrator gates closed; no login widget until configured |
| 3. Real grounded Census question | NOT RUN: new service identity/grants not provisioned/confirmed |
| 4. Multi-turn follow-up | NOT RUN against deployment |
| 5. Unsupported questions | NOT RUN against deployment; prior offline/core evidence preserved |
| 6. Independent authenticated sessions | NOT RUN against deployment; prior tests do not substitute |
| 7. Live auth failures/rate limits | NOT RUN against deployment; unchanged guard implementations retain offline passes |
| 8. Secrets/private diagnostics | No raw diagnostics/secrets visible on observed unconfigured page; image/source transfer/file modes verified; authenticated/network surface still pending |
| 9. Normal answers <60s | UNMEASURED for hosted Census answers; page render 1.258s, after restart 1.221s only |
| 10. SSH disconnect/restart survival | PASS for infrastructure/unconfigured page and actual SQLite control session across app/proxy restart + container recreation; authenticated Census request still pending |

External TLS verified using the client's default trust store: TLSv1.3, Let's Encrypt
issuer YE2, SAN matches hostname, valid until 2027-01-12. No self-signed certificate or
TLS-verification bypass. HTTP returns 308 to HTTPS; security headers present. Caddy
configuration validation passed with only a formatting warning. Temporary sslip.io
DNS resolved to the exact Droplet IP; no domain purchase/DNS operator action needed.
This depends on third-party DNS availability; a controlled domain is preferable for
longer-lived hosting. For a supplied hostname, create A -> 104.248.239.52, remove any
incorrect AAAA, and update origin/proxy hostname together before re-verification.

Actual SQLiteControl was initialized by a trusted operator storage probe, no fake
Census/auth response. A private probe session survived restart and forced container
recreation with mode 700/600. Authentication/data state behavior is not inferred from
that probe. Outbound TLS from the app container to Snowflake verified; no login/data
operation was inferred from TLS connectivity. Both administrator gates remain `0`.

Evidence: `phase4_recovery/host_status.json`, `storage_and_egress.json`,
`external_initial.json`, `external_after_restart.json`, `public_blocked.png`,
`database_kind.json` and `verify.log`. Browser used an isolated /tmp tool install;
existing Yale project environment was not reinstalled/reconfigured. Actual Docker
build/launch/OS logs remain on Droplet under /var/log/census-*.log, with no secrets.
Full local verification: **169 passed / 25 live skips**, Ruff pass. Preflight exit 2
reflects unchecked deployment/final-delivery items and precommit changes; its tests pass. This does not
establish clean hosted factual correctness. Prior failed/live evidence remains intact.

## Specific remaining operator action

Have the authorized account administrator execute/review the public-key SQL and
PUBLIC baseline, preserving development privileges. Confirm exclusive use of
SNOWFLAKE_LEARNING_WH during hosting. No additional warehouse is required or created.
See [ADMIN_ACTION.md](phase4_recovery/ADMIN_ACTION.md) for exact proposal and optional
baseline migration; no administrator password/private key needs to leave their custody.

After confirmation: validate new identity's actual SELECT, Cortex, effective grants
and suspension, then enable the reviewed permissions/exclusive-warehouse flags and
recreate app from the same private env. Run the existing public browser suite with
fresh evidence plus an authenticated post-restart turn. Do not count readiness
checks as passing before then. **Phase 5/final submission is not ready.** No email sent.

Recovery checkpoint: `v0.4.1-dev`, specifically an administrator-gated deployment.

---

# Initial Phase 4 implementation checkpoint — historical record

**Status: PARTIAL / PUBLIC DEPLOYMENT BLOCKED.** No working public URL is available.
The Web adapter, secure single-instance deployment configuration and smoke runner
are implemented and locally tested. They do not satisfy public-deployment acceptance.
No Phase 5/final submission work started and no email sent.

## Implementation

| Component | Actual behavior |
| --- | --- |
| `web_app.py`, `census_web/app.py` | Streamlit chat, multi-turn visible history, loading/status, safe errors, reset/logout, allowlisted provenance and latency |
| `census_web/runtime.py` | Shared AgentService facade; existing BearerAuthenticator/SQLiteControl/workers; private durable path, dedicated key-pair config and explicit admin attestations required |
| `census_agent/backend.py` | Optional trusted `connection_config` and connector key-pair parameters; legacy local loader/password defaults preserved; no Agent/statistical behavior changed |
| `deploy/Dockerfile`, `.dockerignore` | Nonroot UID 10001, explicit code/catalog allowlist, no .env/Git/evaluation diagnostics in image |
| `deploy/compose.yaml`, `Caddyfile`, `streamlit.toml` | One app, one HTTPS proxy, one persistent local SQLite volume, mounted server key/env, restart policy, bounded process/resources, CORS/XSRF on and static serving/traceback details off |
| `deploy/admin_permissions.sql` | Administrator proposal for restricted service role/user/warehouse and grant review; NOT EXECUTED |
| `scripts/create_reviewer_token.py` | Operator-only random token/digest files, owner-only outside checkout, no token stdout/overwrite |
| `scripts/deployment_smoke.py` | Optional Playwright clean-browser HTTPS runner; public-address check, two contexts, saved failures, no raw exception/token dumps |
| `docs/DEPLOYMENT_RUNBOOK.md`, `REVIEWER_ACCESS.md` | Concrete host/admin/auth/run/test/recovery steps; missing URL explicitly disclosed |

Only service facade/auth/control configuration is cached. Browser credentials/history
are private Streamlit session state; owner-bound conversational intent remains in
shared SQLite. No connector/cursor/ConversationState is shared. Existing single
active warehouse lease, 55s parent deadline, rate/model budgets and quarantine remain.
Questions max 2,000 characters; visible history max 40 messages. Plain-text answer
rendering prevents untrusted link/image/HTML interpretation. UI never accesses
ServiceResult.diagnostics or renders raw SQL/model/audit/error objects.

## Actual verification

| Command / check | Observed result | Scope |
| --- | --- | --- |
| `.venv/bin/python -m pip install 'streamlit==1.65.0'` | Exit 0; Streamlit and required transitive packages installed | Sole new app dependency; existing connector unchanged, no separate LLM/framework |
| `.venv/bin/python -m pytest -q tests/phase4 --tb=short` | 29 passed, exit 0 | 22 UI/config tests + 7 provisioning/packaging/runner checks; explicitly mocked Census provider |
| `bash scripts/verify.sh` | Exit 0; 169 passed / 25 skipped; Ruff formatting/lint and Bash syntax pass | Existing Phase 1–3 offline regressions plus new tests; nine Phase 1/16 Phase 2 opt-in live skips are NOT passes |
| Temporary Streamlit subprocess + stdlib HTTP client | Loopback health/page HTTP 200; subprocess stopped in finally | Unconfigured local HTTP liveness only; no auth/data/browser/public HTTPS claim; `phase4_checks/loopback_http.json` |
| `.venv/bin/python -m pip check` | Exit 0 | No broken installed requirements |
| `.venv/bin/python scripts/deployment_smoke.py --help` | Exit 0 | CLI interface only; no public smoke run or Playwright/browser install |
| `git diff --check` | Exit 0 | Whitespace review |
| `bash scripts/preflight.sh` | Exit 2; embedded verification passes (169/25) | Unchecked full-delivery items and precommit working changes; not a test failure |
| Preservation / credential exclusion audit | See `phase4_checks/audit.json` | Existing artifacts unchanged; .env ignored/untracked/mode 600; no credential-file contents read |

Full verification output is retained in `docs/phase4_checks/verify.log`. ShellCheck
is absent and explicitly skipped. Docker, Podman, cloud hosting CLIs, Caddy and an
approved public-service host are absent here; no Docker build, Compose launch or
TLS certificate has been tested. Do not infer a clean deployed installation from
this already-configured Python environment.

Initial local test defects were corrected: AppTest's relative path resolves against
the test file (six initial failures/16 passes); its generic element `.type` differs
from the password proto enum (one remaining failure/21 passes). Final 29 local tests
pass. These were offline test harness defects, not real Census evaluation results.
No Phase 1–3 live evaluations or discovery were repeated; no new Cortex/data calls.

## Ten deployed acceptance checks

| Check | Actual status |
| --- | --- |
| Public page loads | BLOCKED — no URL/approved host; local HTTP only |
| Reviewer authentication | Offline adapter test passes; public untested |
| Actual grounded Census answer | Historical core evidence preserved; new deployment untested |
| Multi-turn follow-up | Offline adapter test passes; public untested |
| Unsupported query | Offline adapter graceful message passes; public untested |
| Independent user sessions | Offline real SQLite/process + mocked provider passes; public untested |
| Rate limits / auth failures | Offline adapter tests pass; public untested |
| Secrets / diagnostics excluded | Code/config/fixture tests and artifact review pass; public/network audit pending |
| Normal request <60s | Existing Phase 3 0.6816–16.6937s retained as historical service evidence; new public latency UNMEASURED |
| Survives developer SSH disconnect | UNTESTED — restart config is not observed availability |

The future browser runner uses two independently SQL-verified historical values:
2020 ACS Autauga County population 55,639; 2019 55,380. References and actual query
IDs are preserved in `slurm_runs/phase3_final_v3/phase2_results.json`. This runner is
a deployed regression smoke, not a new held-out accuracy evaluation. Refresh operator
reference SQL if the source changes. Separate post-SSH/restart evidence is mandatory.

## Specific blockers and viable alternative

**Host blocker (P0 submission requirement):** current machine is a Yale Slurm login
node, not an approved persistent public service host. No deployment credentials or
hosting environment names are present. Sites hosting runs Workers and cannot preserve
the retained Python multiprocessing/local SQLite model. Plugin discovery found Render
and Railway integrations available but unconnected; no access/provisioning occurred.
Render durable disks require paid service, so no resource was created without explicit
cost authorization. Deployment investigation stopped after identifying these missing
inputs; no repeated hosting attempts or indefinite waiting.

**Identity blocker (P1 security):** current PUBLIC/ALL development identity and broader
PUBLIC/inherited learning-role grants are unsuitable for unattended public deployment.
No administrator-provisioned restricted identity, reviewed PUBLIC baseline, private
key or exclusive application warehouse has been supplied. Runtime refuses development
credentials. Existing grants/access/warehouse configuration remain unchanged. Exact
proposed admin commands are in `deploy/admin_permissions.sql`; grant review and live
key-pair SELECT/Cortex/suspend testing remain required. Flags are operator attestations,
not automated proof of least privilege. Key-pair transport currently has mocked
connector tests only.

**Selected viable path:** supply an existing approved Linux Docker host, domain and
server-side restricted Snowflake key, then run supplied single-instance Docker/Caddy
configuration using durable local volume. It supports required process isolation,
secrets and HTTPS without an additional hosting purchase if the host already exists.
Alternative: connect an authorized Render account and explicitly approve a paid
single-instance service with persistent disk; retain the same adapter/control design.
No multi-host shortcut or ephemeral SQLite fallback.

## Readiness and handoff

Ready for the operator-host/configuration step, not final submission. Public URL,
private reviewer credential delivery, new identity/privilege evidence, external browser
E2E and post-SSH/restart availability remain outstanding. Full final README/Reflection,
private GitHub reviewer permissions and final email are also unfinished.

New session: read AGENTS.md, PROGRESS.md, this report and DEPLOYMENT_RUNBOOK.md;
inspect Git. Resume Phase 4 deployment only after host/admin inputs change. Preserve
existing real evidence; do not repeat scans/full evaluations or start a later phase.
Development checkpoint `v0.4.0-dev` explicitly denotes this partial deployment-blocked
state, not Phase 4 acceptance. See DEVELOPMENT_VERSIONS.md for the Git reference.
