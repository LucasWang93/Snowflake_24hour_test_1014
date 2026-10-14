# Snowflake operator action required

Host setup/image/HTTPS work proceeds independently. No administrator credentials
are available through CODEX_APP (ACCOUNTADMIN activation was denied in the preserved
SPCS feasibility inspection). No application-role grants have been executed by Codex.

1. Review and execute `deploy/digitalocean_admin.sql` in the authorized account.
   `/etc/census/admin_provision.sql` on the Droplet is the same public-key-only SQL.
   It uses the existing imported database and existing SNOWFLAKE_LEARNING_WH;
   it does not create another warehouse or paid service. The new RSA private key
   exists only on the Droplet, owner UID 10001, mode 400. Never send it or admin
   credentials through chat/Git.
2. Audit PUBLIC/inherited grants before declaring effective least privilege. PUBLIC
   currently inherits SNOWFLAKE_LEARNING_ROLE, which permits schema creation in the
   learning database. A new primary role does not remove this inheritance.
3. One possible administrator-reviewed migration, ONLY after reviewing all affected
   users and preserving their required access, is:

```sql
-- Optional proposal, NOT EXECUTED; separate administrator approval/review required.
-- Preserve CODEX_APP's development privileges via its existing ALL secondary mode.
GRANT ROLE SNOWFLAKE_LEARNING_ROLE TO USER CODEX_APP;
-- Preserve administrator/engineering access via its nonpublic hierarchy.
GRANT ROLE SNOWFLAKE_LEARNING_ROLE TO ROLE SYSADMIN;
REVOKE ROLE SNOWFLAKE_LEARNING_ROLE FROM ROLE PUBLIC;
```

Review remaining PUBLIC account privileges (including BIND SERVICE ENDPOINT and
MANAGE ARTIFACT PUBLICATION) and affected users. Do not perform a blanket revoke.
An alternative is explicit documented baseline risk acceptance; that does not make
the effective credential strictly read-only, and requires an operator decision.
This work will not silently mark an unreviewed baseline as reviewed.

4. Confirm SNOWFLAKE_LEARNING_WH is exclusively used by AgentService while hosted.
   Existing operator CLI/reference scripts bypass the shared lease and must not run
   concurrently. Existing development permissions are preserved, but verification
   must use the service boundary or an agreed maintenance window.
5. Tell the deployment operator which steps actually succeeded and whether the
   PUBLIC baseline/exclusive warehouse were reviewed. No secrets are needed in the
   reply. Then run bounded real SELECT/Cortex/cleanup/permission verification with
   the new service identity before enabling the two administrator flags.

Until those confirmations, CENSUS_PERMISSIONS_REVIEWED=0 and
CENSUS_EXCLUSIVE_WAREHOUSE=0 on the Droplet. The HTTPS page fails closed and
reports unavailable configuration. No development .env/password is a fallback.
