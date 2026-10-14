# Single-instance deployment runbook

Current host: DigitalOcean 104.248.239.52; Ubuntu 24.04, Docker 29.9.1,
Compose 5.6.0. HTTPS entry point **https://census-104-248-239-52.sslip.io** is deployed
and externally verified with real authenticated Census answers and post-restart access.
**Functional demo is live. Inherited PUBLIC permissions remain a documented follow-up.**

Current release path `/opt/census/releases/latency-20261014`, symlink `/opt/census/current`;
image includes v0.4.4-dev metadata-index/cleanup improvements. Production identity and
reviewed flags remain APP_ROLE/AGENT_PROD; v0.4.3 public acceptance is preserved.
Operator commands run as root over existing SSH key; `census-deploy` can upload code
but has no Docker group/secret-file access. Server-only paths:
`/etc/census/compose.env`, `/etc/census/app.env` (mode 600),
`/etc/census/snowflake.p8` (mode 400 UID 10001),
`/var/lib/census-operator/reviewers` (private reviewer handoff).
Never display env/private-key/token file contents in logs or Git.

```bash
ssh -i ~/.ssh/id_ed25519_ace_mr root@104.248.239.52
cd /opt/census/current
docker compose --env-file /etc/census/compose.env -p census -f deploy/compose.yaml ps
# After approved configuration changes, preserve volumes and use:
docker compose --env-file /etc/census/compose.env -p census -f deploy/compose.yaml up -d
```

Do not use `down -v` or delete the control DB. Docker itself was observed active after
host security reboot. Both containers have restart policies; app/proxy controlled
restart and recreation preserved a real SQLite control probe. Authenticated real data access now also passes after restart; see phase4_activation.
Budget/session/event hashes were identical immediately before and after restart.

## Hosting choice

Use one approved persistent Linux Docker host, with DNS and inbound 80/443, outbound
Snowflake/Cortex connectivity, 2 GB application memory as a configuration starting
point (not a measured sizing guarantee), and a local Docker volume. Run one app
container plus Caddy HTTPS proxy. Never scale app replicas or mount SQLite over
NFS/shared network storage. Do not run this persistent service on the Slurm login node.

| Option | Judgment |
| --- | --- |
| Existing approved Linux host + Docker/Caddy | Selected deployable configuration; preserves Python spawn and local SQLite, no new hosting purchase if host already exists |
| Render paid Python/Docker service + disk | Viable alternative if user connects account and explicitly authorizes cost; single instance, mounted persistent disk, provider HTTPS and secrets; not provisioned |
| Sites / ephemeral free serverless hosting | Rejected for this backend: Workers do not preserve Python process/local-file execution; free Render has no persistent disk and can idle |

Render's [disk requirements](https://render.com/docs/disks) and
[free-service limits](https://render.com/docs/free) explain the tradeoff. The supplied
[Streamlit Docker pattern](https://docs.streamlit.io/deploy/tutorials/docker) is adapted
to a nonroot process and an explicit source allowlist.
[Caddy](https://caddyserver.com/docs/automatic-https) handles certificates/redirects;
its [reverse proxy](https://caddyserver.com/docs/caddyfile/directives/reverse_proxy)
supports WebSockets. These are documented platform capabilities, not tested deployment results.

## Administrator prerequisites

1. Current provisioned identity/role are AGENT_PROD/APP_ROLE. Operator confirmed
   SNOWFLAKE_LEARNING_WH exclusivity; real role/NONE data/Cortex/suspend checks pass.
   Older provisioning scripts are historical alternatives, not required launch actions.
   Review DEPLOYMENT_PERMISSIONS.md: PUBLIC still inherits learning-role warehouse/
   schema privileges. Grant APP_ROLE explicit OPERATE before reviewing/removing that
   inheritance; a named role alone is not effective least privilege. Do not alter
   working development grants incidentally.
2. Current operator-approved production authentication uses AGENT_PROD password from
   server secrets/environment. Set SNOWFLAKE_AUTH_MODE=password and SNOWFLAKE_USER=AGENT_PROD,
   with SNOWFLAKE_PASSWORD stored only in the protected deployment environment file.
   No development .env is transferred/read. Do not set private-key names in password mode.
   Optional legacy key-pair mode is retained using SNOWFLAKE_AUTH_MODE=keypair and
   `-f deploy/compose.keypair.yaml` after the base Compose file; it refuses passwords.
   Its private key remains owner-only and must be readable by container UID 10001.
3. Verify actual effective privileges, data SELECT, Cortex and warehouse suspension
   using the new identity and `secondary_roles=NONE`. Preserve query IDs in protected
   operator evidence. Canonical SQL and the administrator-review flag do not prove
   effective least privilege.
4. Retain an operator for quarantine recovery. No automatic recovery, budget reset or
   new grant/role/user/resource creation is authorized by a normal application request.

## Server-side configuration

Create an owner-only server environment file outside this checkout, for example
`/etc/census/app.env`; never run commands that display it. Required names:

```text
CENSUS_HTTPS_ORIGIN
CENSUS_REVIEWER_DIGESTS
CENSUS_SNOWFLAKE_ROLE=APP_ROLE
CENSUS_PERMISSIONS_REVIEWED
CENSUS_EXCLUSIVE_WAREHOUSE
CENSUS_DURABLE_STORAGE
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_DATABASE
SNOWFLAKE_SCHEMA
SNOWFLAKE_AUTH_MODE=password
SNOWFLAKE_PASSWORD  (server secret; never put its value in documentation)
```

The three confirmation flags must be `1` **only after** the named properties have
been independently reviewed. HTTPS origin must match DNS/proxy hostname. Role must
be a reviewed app role; PUBLIC/admin roles and CODEX_APP are refused. Password mode
requires AGENT_PROD and reads only os.environ; missing credentials fail closed. Local
.env is never a fallback. Base Compose fixes the durable control path and has no key
mount. Optional key-pair override validates a regular nonsymlink owner-only key.
The server env file remains owner-only.
Control directory is private, DB mode 600. Keep an untouched volume across restart
and redeployment; do not delete/reinitialize it to evade quotas or quarantine.

Provision reviewer tokens on the approved host, not in Git or this chat:

```bash
python scripts/create_reviewer_token.py --directory /absolute/private/handoff --principal reviewer1
```

This writes a random 256-bit token and SHA256 digest mapping to separate owner-only
files outside the checkout and prints paths only. Repeat with distinct principal
names. Merge digest mappings into the server's `CENSUS_REVIEWER_DIGESTS` JSON value,
max 32 principals. Distribute each token through an approved private handoff; do not
print it in terminal logs or put it in URLs, source, README or submission Git history.
Two actual reviewer token/digest pairs now exist only in the protected server handoff
directory; no token values were printed or committed. Existing test tokens remain
explicit offline fixtures. Revocation removes the digest and restarts the app;
persist SQLite so budgets/quarantine survive. Use distinct tokens for independent
reviewers; shared tokens intentionally share one principal's rate quota.

## Launch (only on the approved host)

Docker/Compose are now installed and boot-enabled on the Droplet; none was installed
on the Slurm node. Set only nonsecret path/domain shell variables:

```bash
export CENSUS_DOMAIN=census.your-approved-domain.example
export CENSUS_SERVER_ENV_FILE=/etc/census/app.env
docker compose -f deploy/compose.yaml config --quiet
docker compose -f deploy/compose.yaml up -d --build
docker compose -f deploy/compose.yaml ps
```

Do not print `docker compose config`, container inspect/env or secret files; they can
expand secrets. Only Caddy publishes ports. Restrict host firewall to needed inbound
ports; deny external 8501. Ensure Docker itself starts on host boot. Both services use
`restart: unless-stopped`; app has a 70s stop grace, process limits and private local
volume. Infrastructure restart and SQLite-volume behavior have passed; authenticated
Census availability is now externally verified after restart. HTTPS/XSRF/
CORS stay enabled; static serving is disabled, traceback details hidden, telemetry off.

The image copies only code, catalog, web requirements and Streamlit configuration;
`.dockerignore` additionally excludes credentials, Git and all evaluation diagnostics.
Docker image build, Compose config/launch and Caddy validation have passed on
Droplet. They were not run on the Slurm node.
Streamlit health is liveness only; it does not establish configuration/data readiness.

## Reviewer access and smoke verification

See `REVIEWER_ACCESS.md` for browser steps. No reviewer setup should be required once
hosted. From a clean client distinct from the deployment host:

```bash
python -m pip install -r requirements-browser.txt
python -m playwright install chromium
python scripts/deployment_smoke.py --url https://your-actual-hostname \
  --token-file /private/reviewer1.token --second-token-file /private/reviewer2.token \
  --output /private/new-deployment-smoke.json
```

Use a fresh output path; failures are saved without raw exception messages or tokens.
The runner rejects HTTP/private/localhost addresses, uses new browser contexts and
checks page/auth, 2020 ACS Autauga population 55,639, follow-up 2019 population 55,380,
unsupported year, independent context, real shared limits, visible privacy and <60s
turns. The two numerical expectations come from independent reference SQL in final
Phase 2/3 evidence, not invented LLM answers; refresh independent operator reference
queries if data changes. This is a deployment regression smoke, not new held-out accuracy.
Review screenshots/network behavior manually for unexpected private metadata; the
automated visible-surface scan is not a complete secret-exposure audit.

Separately disconnect the developer SSH session, then open the HTTPS URL from the
independent client and execute another authenticated question. Record timestamp,
URL, response and latency. Verify DB/session budget continuity through controlled
restart and inspect service supervision. Do not infer persistence from a successful
local test or a Docker restart policy. The actual ten checks are now recorded in phase4_activation; future deployments must
repeat affected checks. A smoke PASS alone does not establish SSH persistence.

## Recovery and limits

Preserved defaults: one active request, six requests/principal/minute, 20 global/minute,
120 reserved Cortex-call units/rolling day; two units/request without refund; 55s parent
deadline, bounded model/SQL and owner session TTL. UI status is progress feedback, not
streamed inference. No new Agent/statistical capability. No CLI/probes on the app's
warehouse while public traffic is active. A lost process/uncertain cleanup quarantines
admission. Stop traffic, independently verify no active server queries and suspended
warehouse, then use existing trusted `recover_after_operator_check`; never expose it
as a public endpoint or clear quarantine by deleting the DB. No automatic unsafe recovery.

## DigitalOcean activation and permission follow-up

Current role APP_ROLE/AGENT_PROD was provisioned by the operator. Real role/NONE
SELECT/Cortex/suspend and public acceptance pass; server confirmation flags are 1.
Do not execute older CENSUS_WEB_APP/CENSUS_APP_READONLY/key provisioning proposals as
new launch steps. They remain historical alternatives; no grant changes were performed
by this activation work. Never use development credentials as a deployment fallback.

PUBLIC still inherits the learning role's production warehouse/schema privileges;
review actual evidence and the explicit OPERATE proposal in DEPLOYMENT_PERMISSIONS.md.
Do not remove inherited OPERATE before APP_ROLE has its own cleanup privilege. The
operator's exclusive-usage confirmation is operational, not account privilege isolation.
Any approved grant changes require targeted role/NONE cleanup checks afterward.

Current hostname uses sslip.io and a publicly trusted Let's Encrypt certificate.
Caddy handles renewal using persistent caddy_data. For an owned domain, create an A
record to 104.248.239.52, ensure any AAAA reaches this same service, update
CENSUS_DOMAIN/CENSUS_HTTPS_ORIGIN together and reverify TLS/XSRF/WebSocket behavior.

## Current acceptance / restart reproduction
The final clean public browser suite passes in phase4_activation/browser_final.json;
controlled restart plus fresh authenticated real answer passes in post_restart_browser.json.
All reviewer token files remain private. Run the browser tool from a trusted client
with the optional browser dependencies, using NEW evidence paths:

```bash
python scripts/deployment_smoke.py --url https://census-104-248-239-52.sslip.io \
  --token-file /absolute/private/reviewer1.token \
  --second-token-file /absolute/private/reviewer2.token --output /new/evidence.json
# On the Droplet, only after in-flight requests finish:
cd /opt/census/current
docker compose --env-file /etc/census/compose.env -p census -f deploy/compose.yaml restart app proxy
```

Close SSH, use a fresh client, authenticate and query again. Check unchanged SQLite
session/state/event fingerprints before sending the new request; do not delete the
DB, reset events or weaken limits. Local `.env` now points CODEX_APP to DEV_WH.
Server credentials and APP_ROLE stay independent of that file. Tests reserve shared
budget units; final_runtime.json records the observed remaining allowance, not an SLA.

## Derived search index / performance release
Docker build computes an immutable index from the authoritative catalog; no manual
cache download or service installation. source/code/payload fingerprints are checked
on load, then physical schema is still validated. Missing/stale cache rebuilds safely.
Rebuild the image after catalog/search code changes; do not edit the derived artifact
or bake credentials into it. Fresh SQL remains uncached by this application.
For app replacement, use the shared admission lease for a short maintenance interval
only after existing requests finish; preserve the SQLite volume/events and release the
lease once replacement succeeds. Current exact source/image hashes and healthy state
are in phase4_latency/deployment.json. No warehouse size/role/limit change.
