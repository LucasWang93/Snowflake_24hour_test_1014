# Reviewer access

**Public entry point: https://census-104-248-239-52.sslip.io**

HTTPS and browser loading are verified. **Census login/data access is currently
blocked pending Snowflake application-role/PUBLIC-baseline review and warehouse
exclusivity confirmation. AGENT_PROD production credentials are installed server-side;
connectivity is verified, but the public permission gates remain closed.** The page reports safe
configuration unavailability. This is not yet an accepted running Census demo.
Reviewers should wait for operator confirmation before using the steps below.

After the operator confirms the Snowflake blocker is cleared, open the URL and enter the
reviewer access token delivered through the private handoff. Tokens are never stored
in Git or embedded in a page/URL. No application installation is required for reviewers.

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
no deployment SLA is claimed before measurement. Operator intervention may be needed
after an uncertain timeout. Never send Snowflake passwords, private keys or other
secrets in chat. Final submission email has not been sent.

The operator holds individual tokens in the private Droplet handoff directory; they
are not included here or in Git. Droplet: 104.248.239.52; existing SSH key authentication
remains functional. Request a token via the approved private handoff once enabled.
An owned DNS hostname can later replace the temporary sslip.io hostname. No final
submission email or reviewer repository-access change has been performed.
