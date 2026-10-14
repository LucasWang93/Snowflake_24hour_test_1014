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
