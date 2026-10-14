# Deployment permission boundary

Phase 3 preserves working credentials/grants; no role, user, grant or warehouse
configuration change has been made. Fresh visible role/user audits and actual data/
Cortex queries are recorded with the Phase 3 evaluation, not inferred from this plan.

The current identity uses PUBLIC plus secondary ALL. Direct user grants require ALL
in the observed account behavior; see [Snowflake access control](https://docs.snowflake.com/en/user-guide/security-access-control-overview).
PUBLIC/inherited learning-role privileges are broader than Census read access. A
successful SELECT or canonical application SQL does not establish least privilege.
Audits follow up to four visible role grants; absent visibility is not absent privilege.

## Administrator-reviewed migration plan (not executed)

Prefer a dedicated service identity and role with read-only data access, Cortex use,
and usage of a dedicated application warehouse. The existing account's broad PUBLIC
privileges remain inherited even with a new named role; an administrator must review
that baseline before claiming least privilege. Do not revoke PUBLIC/user grants or
replace working credentials as an incidental change to this repository.

For a database imported from a share, an administrator can review this proposed
privilege set ([shared database privileges](https://docs.snowflake.com/en/user-guide/security-access-control-considerations)):

```sql
-- Proposal only: verify database import type, PUBLIC baseline and new service user.
CREATE ROLE CENSUS_APP_READONLY;
GRANT IMPORTED PRIVILEGES ON DATABASE
  US_OPEN_CENSUS_DATA_NEIGHBORHOOD_INSIGHTS_FREE_DATASET TO ROLE CENSUS_APP_READONLY;
GRANT DATABASE ROLE SNOWFLAKE.CORTEX_USER TO ROLE CENSUS_APP_READONLY;
-- On a separately approved application warehouse:
-- GRANT USAGE ON WAREHOUSE <approved_app_warehouse> TO ROLE CENSUS_APP_READONLY;
-- GRANT ROLE CENSUS_APP_READONLY TO USER <approved_service_user>;
```

If the imported source instead exposes database roles, grant only the provider's
appropriate read database role; do not guess it. Per-turn ALTER SUSPEND additionally
needs warehouse OPERATE, so either grant OPERATE only on the approved app warehouse
or move suspension to a separately authorized operator. OPERATE is an operational
privilege, not a data-write privilege. Do not give ACCOUNTADMIN/SECURITYADMIN to the
application. No new passwords or demo tokens belong in this document or Git.

`SnowflakeBackend(role="CENSUS_APP_READONLY", secondary_roles="NONE")` is supported
for the future migration. Verify exact data/Cortex/cleanup access with that identity
before changing deployment configuration. The legacy PUBLIC/ALL default remains
working. Provisioning requires grantable rights not demonstrated by the available
application audit; the plan is a deployment blocker, not a completed role migration.

## Application enforcement today

- Canonical typed SQL, exact revalidation and bound values before a data cursor.
- No arbitrary SQL/model SQL, schema mutation, unapproved functions or unrestricted
  geography; non-additive aggregation remains blocked.
- A spawned worker owns one fresh Snowflake session/connection and all cursors.
- All hosted callers must use the authenticated AgentService and SAME local control
  file. One shared lease serializes the trial warehouse, preventing simultaneous
  data execution and per-turn suspension from different service workers.
- CLI/reference probes bypass the service admission layer: do not run them while
  the shared warehouse is serving users. An exclusively assigned application
  warehouse and an admin-provisioned restricted identity are deployment prerequisites.

## Phase 4 initial public-adapter policy (historical key-pair configuration)
The Web runtime requires a dedicated key-pair identity and reviewed named app role,
secondary NONE, explicit PUBLIC/privilege review and exclusive-warehouse attestations.
It rejects the development user/password path. Backend accepts optional trusted
`connection_config` for connector SNOWFLAKE_JWT/private_key_file parameters without
changing existing operator defaults. Live key-pair access and actual effective
least privilege remain unverified; no grants or credentials were modified.

Exact proposed administrator role/service-user/warehouse statements are supplied in
`deploy/admin_permissions.sql`, not executed. Provisioning a new warehouse must first
be approved under the trial-credit policy; an approved exclusive existing warehouse
can be assigned instead. TYPE=SERVICE uses noninteractive key-pair authentication;
private key material is server-only, never Git/chat. See DEPLOYMENT_RUNBOOK.md.

## Current production identity — AGENT_PROD (2026-10-14)
Operator authorized password authentication exclusively through deployment secrets/
environment. Runtime accepts explicit SNOWFLAKE_AUTH_MODE=password with AGENT_PROD;
CODEX_APP remains local-only. Key-pair mode remains supported separately. No development
.env is read by the Web runtime or its injected backend; no password fallback exists.

Actual Droplet login, bounded Census SELECT, llama3.3-70b COMPLETE and explicit suspend
succeeded; SHOW confirmed SUSPENDED. Evidence in phase4_production_identity includes
query IDs. This probe used PUBLIC/ALL: it is connectivity evidence, not production
least-privilege acceptance. The user has 77 direct grants and no visible account-role
membership. CENSUS_APP_READONLY lookup returned 002003/02000. PUBLIC has 110 grants,
including inherited learning-role CREATE SCHEMA, OPERATE and MONITOR. No grants changed.

The named-role/NONE policy, permission-review and exclusive-warehouse gates remain
unchanged and closed. Exact proposal for this existing identity/warehouse is
`deploy/agent_prod_permissions.sql`; it replaces the previous proposed new service
user/key-pair provisioning path for this deployment. Administrator must review PUBLIC
baseline separately and confirm warehouse exclusivity. No revokes/default changes or
new paid warehouse are included. Do not claim a reviewed read-only deployment yet.

## Current activation — APP_ROLE (supersedes prior provisioning blocker)
Operator provisioned APP_ROLE and authorized activation/exclusive warehouse use.
Real AGENT_PROD/APP_ROLE/secondary NONE SELECT/Cortex/suspension succeeded; production
flags enabled and external authenticated acceptance plus restart passed. CODEX_APP
local connection selects DEV_WH. Old CENSUS_APP_READONLY/new-key-pair scripts remain
historical proposals; they were not executed as part of activation.

Fresh permissions.json/role_probe.json in phase4_activation show PUBLIC STILL inherits
SNOWFLAKE_LEARNING_ROLE with learning DB CREATE SCHEMA and production WH USAGE/OPERATE/
MONITOR. Direct PUBLIC grants alone miss it; CODEX_APP's default DEV_WH does not prove
production privilege isolation. APP_ROLE's own warehouse grant is USAGE, so successful
suspension currently relies on PUBLIC inheritance. No strict least-privilege claim.

P1 operator follow-up (not executed):
```sql
GRANT OPERATE ON WAREHOUSE SNOWFLAKE_LEARNING_WH TO ROLE APP_ROLE;
SHOW GRANTS TO ROLE PUBLIC;
SHOW GRANTS TO ROLE SNOWFLAKE_LEARNING_ROLE;
```
Then review/remediate PUBLIC inheritance with the administrator without revoking
needed developer privileges. Retest cleanup with APP_ROLE/NONE before any inheritance
removal. System PUBLIC CORTEX_USER is separate and need not be removed for this demo.
All canonical SQL, server secrets, isolation/admission/deadline/quarantine controls are
unchanged; functional public acceptance does not close the account-level residual.
