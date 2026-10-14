# Reviewer access

**Public entry point: https://census-104-248-239-52.sslip.io**

The authenticated application is live and externally tested, including a real answer
following a controlled restart. Open the URL and enter an individual reviewer access
token from the private handoff. No installation or Snowflake credential is needed.
Tokens are never embedded in Git, page source or URL parameters.

1. Sign in and ask: “Using ACS release 2020, what is the total population of Autauga
   County, Alabama?” Recorded reference expectation: 55,639.
2. Follow up: “And in 2019?” Recorded reference expectation: 55,380.
3. Expand **Data provenance** to see universe, release/product and physical field.
   ACS year is a provider release label; its survey interval is not verified.
4. Use **New conversation** to reset context, or **Sign out** to clear browser history
   and credentials. Reload/reconnect can require a new login; no browser resume token.

Counts may aggregate over distinct CBGs; medians/ratios/MOEs require a supported scope.
Unknown questions clarify/refuse. Only one query runs at a time; a busy response means
retry shortly. Defaults are six requests per reviewer/minute and a shared 120 reserved
model-call-unit daily allowance. Requests aim to finish within 55s backend deadline;
measured factual browser requests were 13–17.1s, without claiming a deployment SLA. Operator intervention may be needed
after an uncertain timeout. Never send Snowflake passwords, private keys or other
secrets in chat. Final submission email has not been sent.

The operator holds individual tokens in the private Droplet handoff directory; they
are not included here or in Git. Droplet: 104.248.239.52; existing SSH key authentication
remains functional. Request a token via the approved private handoff.
An owned DNS hostname can later replace the temporary sslip.io hostname. No final
submission email or reviewer repository-access change has been performed.

For the authorized operator only, download an existing token to a private LOCAL file;
this prints no token value and does not copy Snowflake credentials or private keys:

```bash
umask 077
scp -i ~/.ssh/id_ed25519_ace_mr \
  root@104.248.239.52:/var/lib/census-operator/reviewers/reviewer1.token \
  ./census-reviewer.token
```

Run this outside the repository; do not commit/upload the downloaded token. Use its
contents only in the password-style reviewer login field, and deliver reviewer tokens
through the agreed private channel. This document is not final credential delivery.

The functional demo retains a documented Snowflake PUBLIC-inheritance permission
residual (PHASE4_REPORT.md); no strict account-level least-privilege claim is made.
