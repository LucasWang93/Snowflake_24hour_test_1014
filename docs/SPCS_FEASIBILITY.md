# SPCS feasibility — read-only Phase 4 investigation

**Decision: BLOCKED for deployment using the currently authorized identity.**
SPCS control-plane metadata is **AVAILABLE** in this account/region. Whether the
account is currently a Trial and whether an administrator could provision a new
pool under its billing entitlement remain **UNVERIFIED**. Do not interpret the
successful SHOW commands, existing system pools, or workload parameter as billing
approval or successful service deployment.

Inspection: 2026-10-14T21:54:49.315851+00:00 through 2026-10-14T21:55:48.852894+00:00. Existing connector 4.8.0 and authorized
configuration loader used. Full noncredential SQL outputs/query IDs/errors are in
[spcs_feasibility_evidence.json](spcs_feasibility_evidence.json). This is a feasibility
report, not authorization to provision. Application/configuration and Phase 1–4
historical evidence are unchanged. No image build, data scan or Cortex evaluation.

## 1. Account and role status

| Observed field | Actual output |
| --- | --- |
| Configured account identifier | `ssybhom-kx56542` |
| CURRENT_ACCOUNT() | `GA75621` (account locator, not the configured organization/account name) |
| CURRENT_REGION() | `AWS_CA_CENTRAL_1` |
| CURRENT_USER() | `CODEX_APP` |
| CURRENT_ROLE() | `PUBLIC` |
| CURRENT_SECONDARY_ROLES() | `{"roles":"","value":"ALL"}` |
| CURRENT_WAREHOUSE() | `SNOWFLAKE_LEARNING_WH`, inherited default |
| IS_ROLE_IN_SESSION('ACCOUNTADMIN') | `false` |

`SHOW GRANTS TO USER "CODEX_APP"`: 77 rows, untruncated. They comprise 73 SELECT
object grants, database/schema/warehouse USAGE, and SNOWFLAKE.CORTEX_USER database-role
USAGE; no account-role grant to ACCOUNTADMIN. No data was selected to verify them anew.
`SHOW GRANTS TO ROLE PUBLIC`: 110 rows, untruncated. Relevant actual grants:

| Privilege | Object | Result |
| --- | --- | --- |
| BIND SERVICE ENDPOINT | ACCOUNT GA75621 | Granted to PUBLIC |
| USAGE | SYSTEM_COMPUTE_POOL_CPU and SYSTEM_COMPUTE_POOL_GPU | Granted to PUBLIC |
| USAGE | SNOWFLAKE.SPCS_VIEWER / SPCS_REGISTRY_VIEWER / CORTEX_USER database roles | Granted to PUBLIC |
| USAGE | Account role SNOWFLAKE_LEARNING_ROLE | PUBLIC inherits this role |
| CREATE COMPUTE POOL | Account | Not present in visible user/PUBLIC/learning-role grants |

Learning-role grants (all five rows): CREATE SCHEMA and USAGE on
SNOWFLAKE_LEARNING_DB; MONITOR, OPERATE and USAGE on SNOWFLAKE_LEARNING_WH.
They do not supply CREATE COMPUTE POOL. BIND SERVICE ENDPOINT alone is insufficient.
No deployment schema/image repository was created to obtain additional rights.

**ACCOUNTADMIN access is not available through CODEX_APP:** an explicit session-only
`USE ROLE ACCOUNTADMIN` returned `003013 (42501): Requested role 'ACCOUNTADMIN' is not
assigned to the executing user.` Query ID: `01c7bba3-3204-bb79-0008-3d1a00032216`.
The role exists and SHOW GRANTS OF ROLE lists a different user; that does not grant
this session access. No other user's credentials were inspected or attempted.
The failed switch left PUBLIC/ALL unchanged; both connections were closed.

## 2. Availability and existing compute pools

Region support is documented for this commercial AWS region in Snowflake's
[SPCS regional coverage](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/overview#available-regions-and-considerations),
and both compute metadata commands succeeded here. Actual pools:

| Name | State | Family | Min–max nodes | Active nodes | Owner |
| --- | --- | --- | --- | --- | --- |
| `SYSTEM_COMPUTE_POOL_CPU` | SUSPENDED | `CPU_X64_S` | 1–2 | 0 | ACCOUNTADMIN |
| `SYSTEM_COMPUTE_POOL_GPU` | SUSPENDED | `GPU_NV_S` | 1–2 | 0 | ACCOUNTADMIN |

These are Snowflake-created system pools, not our application pools. Their documented
workloads are notebooks, managed Streamlit, model serving and ML jobs; their existence
and PUBLIC USAGE do not authorize this custom Docker service. See
[system compute pools](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-compute-pool#system-compute-pools).
No pool was resumed or reused. There was no failed CREATE probe and no fabricated
"Trial error". Current identity lacks the account privilege needed to create a pool.

## 3. Compute pool families: actual account output

`SHOW COMPUTE POOL INSTANCE FAMILIES` returned **27 rows**, untruncated. Values below
are returned vCPU/allocatable memory values, not inferred from names. All reported
current_node_usage=0 and storage_gib=93.13. Blank messages mean no restriction text
was returned, not guaranteed capacity/quota or entitlement to create a pool.

| Family | vCPU | Memory GiB | GPUs | Returned restriction message |
| --- | --- | --- | --- | --- |
| `CPU_X64_XS` | 1 | 6 | 0 | No restriction message returned |
| `CPU_X64_S` | 3 | 13 | 0 | No restriction message returned |
| `CPU_X64_M` | 6 | 28 | 0 | No restriction message returned |
| `CPU_X64_L` | 28 | 116 | 0 | No restriction message returned |
| `CPU_X64_SL` | 14 | 58 | 0 | No restriction message returned |
| `HIGHMEM_X64_S` | 6 | 58 | 0 | No restriction message returned |
| `HIGHMEM_X64_M` | 28 | 240 | 0 | No restriction message returned |
| `HIGHMEM_X64_L` | 124 | 984 | 0 | No restriction message returned |
| `GPU_NV_S` | 6 | 27 | 1 | No restriction message returned |
| `GPU_NV_M` | 44 | 178 | 4 | No restriction message returned |
| `GPU_NV_L` | 92 | 1112 | 8 | No restriction message returned |
| `GPU_NV_XL` | 188 | 1843 | 8 | Instance family available by reservation only. |
| `GPU_NV_2XL` | 188 | 1843 | 8 | Instance family available by reservation only. |
| `GEN_X64_G2_2` | 1 | 6 | 0 | No restriction message returned |
| `GEN_X64_G2_4` | 3 | 13 | 0 | No restriction message returned |
| `GEN_X64_G2_8` | 6 | 28 | 0 | No restriction message returned |
| `GEN_X64_G2_32` | 28 | 116 | 0 | No restriction message returned |
| `MEM_X64_G2_8` | 6 | 58 | 0 | No restriction message returned |
| `MEM_X64_G2_32` | 28 | 240 | 0 | No restriction message returned |
| `MEM_X64_G2_64` | 60 | 492 | 0 | No restriction message returned |
| `MEM_X64_G2_192` | 188 | 1436 | 0 | No restriction message returned |
| `GPU_B300_G1_192` | 188 | 3969 | 8 | Instance family available by reservation only. |
| `GEN_ARM_G1_2` | 1 | 6 | 0 | No restriction message returned |
| `GEN_ARM_G1_4` | 3 | 13 | 0 | No restriction message returned |
| `GEN_ARM_G1_8` | 6 | 28 | 0 | No restriction message returned |
| `GEN_ARM_G1_16` | 14 | 58 | 0 | No restriction message returned |
| `GEN_ARM_G1_32` | 28 | 116 | 0 | No restriction message returned |

Candidate for a later small single-instance validation: CPU_X64_XS (1 vCPU/6 GiB),
subject to startup/deadline/memory testing. GPU is unnecessary because Cortex runs
remote inference. The family listing includes ARM entries; it does not prove our
image supports ARM. Use an explicit linux/amd64 image and an x86 family for the first
migration, consistent with current [SPCS image guidance](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/spcs-guidelines-and-limitations).

## 4. Trial and billing assessment

**Current Trial/billing state: UNVERIFIED with these permissions.** Earlier project
context describes a trial, but this investigation cannot establish whether it has
since been upgraded. `SHOW PARAMETERS LIKE '%TRIAL%' IN ACCOUNT` returned zero rows;
that is not a paid-account certificate. SHOW ACCOUNTS and SHOW ORGANIZATION ACCOUNTS
both returned `003001 / 42501`, requiring MANAGE ORGANIZATION ACCOUNTS. The latter is
organization-account metadata, not a supported substitute for a trial-status flag.
No current billing/contract status was retrieved.

Actual SPCS account parameters: ALLOWED_SPCS_WORKLOAD_TYPES=`ALL`,
DISALLOWED_SPCS_WORKLOAD_TYPES=empty; full-encryption enforcement=false and
tri-secret/rekey opt-out=false. These do not prove that Trial restrictions are lifted.

Snowflake's [SPCS prerequisites](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/tutorials/common-setup#configure-prerequisites)
state that Trial accounts are not supported. Therefore **if this account is still a
Trial, upgrading to an eligible paid account is necessary under that documented
prerequisite**. If already upgraded, no further billing upgrade is established as
necessary, but delegated privileges/quotas/reviewer access still need review.
An administrator should confirm status in Snowsight/Billing before deciding.
[Adding a card alone does not upgrade a trial](https://docs.snowflake.com/en/user-guide/admin-trial-account#upgrading-to-a-paid-account).
No card, upgrade or billing change was made.

Compute pool nodes and persistent block volumes add separate costs to existing
warehouse/Cortex use; an idle app can still cost money, and suspending a service does
not eliminate preserved-volume storage cost. No compute pool/service/volume was
created or started. Both SHOW WAREHOUSES checks returned SUSPENDED for the learning
warehouse and system notebook warehouse; no ALTER/SUSPEND was needed or issued.
This is not a billing-invoice or metered-credit audit.

## 5. Required privileges (proposed, not granted)

| Purpose | Required permission / boundary | Current finding |
| --- | --- | --- |
| Provision custom pool | CREATE COMPUTE POOL on account | Missing from inspected grant closure |
| Run service | USAGE on approved custom pool; CREATE SERVICE on deployment schema; parent DB/schema access | No approved custom pool; target schema not provisioned |
| Register/push/read image | CREATE IMAGE REPOSITORY on schema if provisioning; WRITE/READ on repository as applicable | No repository provisioned or image built |
| Public ingress | BIND SERVICE ENDPOINT on account for service owner | Already broadly present in PUBLIC; still review least privilege |
| Supply secrets | READ on explicitly referenced Snowflake secrets; admin provisioner needs CREATE SECRET on target schema | Not provisioned or exercised |
| Stage specification (if used) | READ on its stage; write privileges only for uploader | Inline specification could avoid this stage |
| SQL and Cortex execution | Restricted service-owner role with verified Census read + Cortex role and warehouse USAGE/OPERATE for existing suspension policy | CODEX_APP's direct grants do not transfer automatically to a managed service user |
| Reviewer endpoint access | Appropriate service role to account reviewer role, parent object visibility as required | No reviewer roles/users provisioned |

See [CREATE COMPUTE POOL access control](https://docs.snowflake.com/en/sql-reference/sql/create-compute-pool#access-control-requirements),
[CREATE SERVICE privileges](https://docs.snowflake.com/en/sql-reference/sql/create-service#access-control-requirements)
and [service endpoint roles](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/working-with-services).
Have an administrator delegate provisioning rights to a nonadmin owner role rather
than exposing ACCOUNTADMIN to the app. Snowflake's
[networking guide](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/service-network-communications)
notes ACCOUNTADMIN cannot be used to create the service itself. No GRANT/REVOKE here.
Do not create deployment objects in the imported Census database; use a separate
approved writable deployment schema, while preserving read-only Census access.

## 6. Compatibility with the current application

| Requirement | Feasibility and necessary adaptation | Evidence level |
| --- | --- | --- |
| Python/Streamlit | Existing OCI image structure is suitable in principle. SPCS specification replaces Compose; expose app port 8501 using managed ingress, no Caddy purchase/certificate stack needed | Platform container support documented; our image not built/run here |
| Spawn multiprocessing | Normal unprivileged Python child processes appear compatible; preserve main guard, fresh worker connection, parent deadline and quarantine | Architecture inference, not a verified SPCS multiprocessing test |
| Durable SQLite | Use a persistent **block** volume for one private control directory; one service instance (MIN_INSTANCES=MAX_INSTANCES=1), all workers use same file; verify locks, restart/suspend/upgrade continuity and mode 700/600 | Block persistence documented; SQLite correctness/UID 10001 mount ownership untested |
| Other storage | Ephemeral local/memory volumes lose durable admission state; stage/object-storage mounts are not a verified POSIX SQLite-locking substitute. Multiple replicas get independent volume state and violate shared budgets | Reject as an unsafe shortcut for current control design |
| Private secrets | Managed secret mounts/env can supply reviewer digest JSON. Verify UID/file permissions and prevent values in specs/logs | Platform documented; actual secret injection untested |
| Snowflake connection | Prefer managed service-user OAuth: read current mounted token for each new worker connection and use SNOWFLAKE_HOST/account. Existing public runtime requires key pair/user and backend lacks OAuth token/host handling, so **not deployable unchanged** | Specific code incompatibility verified by inspection; adaptation not implemented |
| Census/Cortex | Can execute SQL via connector using a restricted service owner role. Grant verified source read/Cortex/warehouse rights to that role; do not rely on CODEX_APP's user grants | Platform SQL path documented; no new Cortex/data tests |
| HTTPS/WebSockets | Platform provides authenticated HTTPS ingress. Streamlit WebSocket, XSRF/CORS, redirects, browser server address/port and <60s end-to-end must be tested against actual ingress | HTTPS documented; this Streamlit ingress path unverified |
| Reliable public service | Managed long-running service can be restarted by platform; persistent lease/quarantine must survive and require safe recovery after a crash | Documented lifecycle, no availability/SLA claim |

[Block volume lifecycle](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/block-storage-volume)
preserves data across service upgrade and suspend/resume, but drop/recreate is not a
safe persistence strategy and can introduce snapshot/storage costs. Single instance
preserves our present safety model, not high availability. Test nonroot mount ownership;
never relax SQLite/key permissions merely to make startup succeed.

[Managed SQL credentials](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/spcs-execute-sql)
use an automatically refreshed, service-scoped OAuth file; owner role plus PUBLIC define
that service user's rights. Preserve per-request token loading and connection ownership.
A customer-managed key-pair alternative requires separate endpoint/network/secret
validation, potentially external access integration; it is not assumed equivalent.
[SPCS secret support](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference#containers-secrets-field)
can replace filesystem/env provisioning while retaining BearerAuthenticator and
AgentService. No implementation, container rebuild or weakening of guards occurred.

## 7. Reviewer access constraints

"Public" means internet-addressable, **not anonymous**. Snowflake
[public endpoints](https://docs.snowflake.com/en/developer-guide/snowpark-container-services/specification-reference#spec-endpoints-field-optional)
require Snowflake authentication and endpoint authorization. Reviewers need an
appropriately granted user in the hosting account; their own unrelated Snowflake
account or GitHub invitation is insufficient. Do not share admin/development credentials.

Existing app bearer tokens alone cannot pass Snowflake ingress. Lowest-change plan:
retain app login and provision reviewer Snowflake access, accepting two authentication
steps. A later trusted-ingress identity adapter would need explicit design/testing;
never bypass existing auth or trust unverified headers. Validate clean browser login,
MFA/SSO/network policies, WebSocket continuity and each reviewer's access before relying
on SPCS for the assignment. No reviewers were contacted or provisioned.

## 8. Estimated migration effort

**Estimate, not measured:** 3–6 engineering hours after account eligibility,
admin/provisioning approval and access to an image builder are available:

- 1–2h: managed OAuth configuration/backend/permission-audit adaptation and targeted tests.
- 1–2h: image build/push, one-instance specification, persistent mount/secrets and readiness.
- 1–2h: clean reviewer/browser, real Census/follow-up, rate/isolation/deadline and restart tests.

Billing/admin/reviewer onboarding and unexpected mount/ingress issues are excluded.
Current Slurm environment lacks Docker/Podman; an approved external builder or CI
would be needed. Existing Agent/catalog/SQL semantics should not need replacement.
This is not a commitment to achieve deployment within that estimate.

## 9. Recommended next steps — approval required

1. Administrator confirms actual Trial/paid eligibility in Snowsight/Billing. If Trial,
   decide explicitly whether to upgrade; no upgrade/card action is authorized by this report.
2. Confirm reviewers can receive scoped Snowflake ingress access. If they cannot,
   retain the previously documented external single-instance HTTPS deployment alternative.
3. Approve a bounded SPCS plan/cost ceiling and dedicated nonadmin service-owner role,
   custom small x86 pool, writable deployment schema, restricted source/Cortex/warehouse
   grants, secrets and one persistent volume. Separate pool costs from warehouse cleanup.
4. Only after approval, implement the small managed-auth/mount/spec changes, then
   build/push/create and test deployed browser/SQL/restart behavior with fresh evidence.

**Stop here. No Snowflake resources, grants, billing or application code changed.
No Phase 5. Resource creation waits for explicit user approval.**

## Appendix — every command actually executed

Only SELECT/SHOW and one denied session-only USE ROLE; no CREATE/ALTER/DROP/GRANT/
REVOKE/DML. SQL timeouts 10–15s; row bounds 200–500; no returned result was truncated.
This inspection used no warehouse-backed tables or usage-history scans. The two
connections inherited the user's default warehouse despite omitting the constructor's
warehouse argument; both final metadata checks confirmed it remained suspended.

| SQL | Actual result | Query ID |
| --- | --- | --- |
| `SELECT CURRENT_ACCOUNT(), CURRENT_REGION(), CURRENT_ROLE(), CURRENT_SECONDARY_ROLES(), CURRENT_USER(), CURRENT_WAREHOUSE()` | 1 rows | `01c7bba2-3204-bca1-0008-3d1a00035006` |
| `SHOW COMPUTE POOLS` | 2 rows | `01c7bba2-3204-bd12-0008-3d1a00016fda` |
| `SHOW COMPUTE POOL INSTANCE FAMILIES` | 27 rows | `01c7bba3-3204-bd70-0008-3d1a0003400a` |
| `SHOW GRANTS TO USER "CODEX_APP"` | 77 rows | `01c7bba3-3204-bca1-0008-3d1a0003500a` |
| `SHOW GRANTS TO ROLE PUBLIC` | 110 rows | `01c7bba3-3204-bd70-0008-3d1a0003400e` |
| `SHOW ROLES LIKE 'ACCOUNTADMIN'` | 1 rows | `01c7bba3-3204-bb79-0008-3d1a00032206` |
| `SHOW GRANTS OF ROLE ACCOUNTADMIN` | 1 rows | `01c7bba3-3204-bd12-0008-3d1a00016fde` |
| `SELECT IS_ROLE_IN_SESSION('ACCOUNTADMIN') AS ACCOUNTADMIN_IN_SESSION` | 1 rows | `01c7bba3-3204-bb79-0008-3d1a0003220a` |
| `SHOW ORGANIZATION ACCOUNTS` | ERROR 003001 / 42501 | `01c7bba3-3204-bd70-0008-3d1a00034012` |
| `SHOW WAREHOUSES` | 2 rows | `01c7bba3-3204-bb79-0008-3d1a0003220e` |
| `SHOW GRANTS TO ROLE SNOWFLAKE_LEARNING_ROLE` | 5 rows | `01c7bba3-3204-bd70-0008-3d1a00034016` |
| `SHOW PARAMETERS LIKE '%TRIAL%' IN ACCOUNT` | 0 rows | `01c7bba3-3204-bd70-0008-3d1a0003401a` |
| `SHOW PARAMETERS LIKE '%SPCS%' IN ACCOUNT` | 4 rows | `01c7bba3-3204-bb79-0008-3d1a00032212` |
| `SHOW ACCOUNTS` | ERROR 003001 / 42501 | `01c7bba3-3204-bd70-0008-3d1a0003401e` |
| `USE ROLE ACCOUNTADMIN` | ERROR 003013 / 42501 | `01c7bba3-3204-bb79-0008-3d1a00032216` |
| `SELECT CURRENT_ROLE(), CURRENT_SECONDARY_ROLES()` | 1 rows | `01c7bba3-3204-bb79-0008-3d1a0003221a` |
| `SHOW WAREHOUSES` | 2 rows | `01c7bba3-3204-bca1-0008-3d1a0003500e` |
