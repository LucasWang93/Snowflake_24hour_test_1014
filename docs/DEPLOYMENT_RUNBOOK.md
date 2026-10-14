# Single-instance deployment runbook

Status: application/configuration implemented; no approved host/domain or restricted
Snowflake key-pair identity supplied. **No public URL exists or has been tested.**
Phase 4 is blocked on those inputs, not accepted as a deployed application.

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

1. Review `DEPLOYMENT_PERMISSIONS.md` and `deploy/admin_permissions.sql`. The SQL is
   a proposal, not an executed migration. Approve an exclusively assigned warehouse,
   restricted role and dedicated `TYPE=SERVICE` user. Review PUBLIC/inherited grants;
   a new role alone does not remove broad inherited account privileges. Do not alter
   working development grants incidentally.
2. Provision a Snowflake RSA key pair on the deployment host using the organization's
   secret-management process. Set its public key on the new user; mount the private
   key owner-readable only, readable by container UID 10001. No development password
   or `.env` is copied into the image. The connector's
   [key-pair parameters](https://docs.snowflake.com/en/developer-guide/python-connector/python-connector-connect#using-key-pair-authentication-and-key-pair-rotation)
   are supported; **live authentication with this new identity remains untested**.
3. Verify actual effective privileges, data SELECT, Cortex and warehouse suspension
   using the new identity and `secondary_roles=NONE`. Preserve query IDs in protected
   operator evidence. Canonical SQL and the administrator-review flag do not prove
   effective least privilege.
4. Supply host/domain access and an operator for quarantine recovery. Current access
   does not demonstrate rights to create roles/users or to provision public hosting.

## Server-side configuration

Create an owner-only server environment file outside this checkout, for example
`/etc/census/app.env`; never run commands that display it. Required names:

```text
CENSUS_HTTPS_ORIGIN
CENSUS_REVIEWER_DIGESTS
CENSUS_SNOWFLAKE_ROLE
CENSUS_PERMISSIONS_REVIEWED
CENSUS_EXCLUSIVE_WAREHOUSE
CENSUS_DURABLE_STORAGE
SNOWFLAKE_ACCOUNT
SNOWFLAKE_USER
SNOWFLAKE_WAREHOUSE
SNOWFLAKE_DATABASE
SNOWFLAKE_SCHEMA
SNOWFLAKE_PRIVATE_KEY_PASSPHRASE  (only for encrypted keys)
```

The three confirmation flags must be `1` **only after** the named properties have
been independently reviewed. HTTPS origin must match DNS/proxy hostname. Role must
be a reviewed app role; PUBLIC/admin roles, CODEX_APP and password-based deployment
are refused. Local .env is not a fallback. Compose fixes the key mount and durable
control path. The key file is regular, nonsymlink and mode 400/600, owned by UID 10001;
the containing host directory stays private. The env file also remains owner-only.
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
No actual reviewer token was generated for hosting in this phase. Test tokens are
explicit offline fixtures. Revocation removes the digest and restarts the app;
persist SQLite so budgets/quarantine survive. Use distinct tokens for independent
reviewers; shared tokens intentionally share one principal's rate quota.

## Launch (only on the approved host)

Install Docker/Compose there through the host operator; none is installed on the
current Slurm node. Set only nonsecret path/domain shell variables:

```bash
export CENSUS_DOMAIN=census.your-approved-domain.example
export CENSUS_SERVER_ENV_FILE=/etc/census/app.env
export CENSUS_PRIVATE_KEY_FILE=/etc/census/snowflake.p8
docker compose -f deploy/compose.yaml config --quiet
docker compose -f deploy/compose.yaml up -d --build
docker compose -f deploy/compose.yaml ps
```

Do not print `docker compose config`, container inspect/env or secret files; they can
expand secrets. Only Caddy publishes ports. Restrict host firewall to needed inbound
ports; deny external 8501. Ensure Docker itself starts on host boot. Both services use
`restart: unless-stopped`; app has a 70s stop grace, process limits and private local
volume. Actual restart/availability behavior is **pending verification**. HTTPS/XSRF/
CORS stay enabled; static serving is disabled, traceback details hidden, telemetry off.

The image copies only code, catalog, web requirements and Streamlit configuration;
`.dockerignore` additionally excludes credentials, Git and all evaluation diagnostics.
Docker build/Compose/Caddy validation have **not run** on this node (tools absent).
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
local test or a Docker restart policy. All ten public acceptance checks remain pending
until recorded against the actual URL; a smoke PASS alone does not mark SSH persistence.

## Recovery and limits

Preserved defaults: one active request, six requests/principal/minute, 20 global/minute,
120 reserved Cortex-call units/rolling day; two units/request without refund; 55s parent
deadline, bounded model/SQL and owner session TTL. UI status is progress feedback, not
streamed inference. No new Agent/statistical capability. No CLI/probes on the app's
warehouse while public traffic is active. A lost process/uncertain cleanup quarantines
admission. Stop traffic, independently verify no active server queries and suspended
warehouse, then use existing trusted `recover_after_operator_check`; never expose it
as a public endpoint or clear quarantine by deleting the DB. No automatic unsafe recovery.
