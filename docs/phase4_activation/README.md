# Phase 4 activation evidence — 2026-10-14

Scope: existing DigitalOcean app, AGENT_PROD/APP_ROLE/secondary NONE, unchanged
AgentService/Census code and persistent control volume. No Phase 5 or final email.

- permissions.json: actual role/user/PUBLIC grants, not a claimed account-wide audit.
- role_probe.json: real role/NONE SELECT, Cortex and warehouse-suspension results.
- development_context.json: local CODEX_APP now uses DEV_WH; no Census/model calls.
- runtime_status.json: deployed identity, flags and private SQLite metadata; no secrets.
- browser_first.json: original failure at the default 5-second assertion timeout.
- browser_retry.json: factual/follow-up/unsupported/isolation pass; rate probe fails
  because model-backed off-topic requests span the one-minute rate window.
- browser_final.json: rerun with 60-second assertions and locally refused adversarial
  requests for rate testing. Production limits are never adjusted for test success.
- network.json: externally verified trust, redirect, headers and blocked port 8501.
- doctor.log / verify.log: actual local commands; skipped live suites are not passes.

The browser runner reads two owner-only reviewer token files from a temporary private
client directory. Token values are never printed or stored here. The default browser
trust settings are used. Public response artifacts contain only fixed test questions
and the same sanitized text a reviewer sees. Private diagnostic fields are not rendered.

Production role activation does not prove strict least privilege: PUBLIC still
inherits SNOWFLAKE_LEARNING_ROLE with learning-database CREATE SCHEMA and production
warehouse USAGE/OPERATE/MONITOR. Operator confirmed demo warehouse exclusivity and
authorized activation; this inherited-permission residual remains visible. No grant
changes are performed. System-default PUBLIC CORTEX_USER is a separate limitation.
