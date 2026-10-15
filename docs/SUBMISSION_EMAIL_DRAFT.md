# Final submission email draft — NOT SENT

To: **Await operator confirmation from the original assignment email.**
Subject: Snowflake Applied AI Homework — Census Chat — Lucas Wang

Hi [confirmed recipient name],

Thank you for the opportunity. My Census Chat homework is available here:

- Source repository: https://github.com/LucasWang93/Snowflake_24hour_test_1014
- Live HTTPS demo: https://census-104-248-239-52.sslip.io
- Reviewer access: enter the token in the accompanying private access note into the
  demo's “Reviewer access token” field. No installation or Snowflake account is needed.
- Architecture, reproduction and evaluation: README.md in the repository.
- Engineering reflection: REFLECTION.md in the repository.

The application uses Snowflake Cortex for structured intent and metadata selection,
a complete supplied-definition Census catalog, canonical validated SQL and
result-grounded answers. It supports contextual follow-ups and clarifies unsupported
statistical or geographic requests. Deployment retains authenticated session
isolation, bounded workers, shared admission/budgets and persistent control state.

Try: “Using ACS release 2020, what is the total population of Autauga County, Alabama?”
Then: “And in 2019?” The verified results are 55,639 and 55,380, respectively.

The README and Reflection describe supported scope, preserved independent-evaluation
failures, regression results and remaining operational limitations, including
Snowflake privilege inheritance and single-host capacity.

Best,
Lucas Wang

---

## Operator checks before sending

This file intentionally contains no token and is not a complete credential handoff.
Attach/send the existing reviewer token privately using the approved channel; never
paste Snowflake credentials into the email. Authorized operator retrieval steps are
in REVIEWER_ACCESS.md. Existing token files remain on the host; no rotation performed.

1. Confirm the candidate signature, actual recipient and receipt timestamp/timezone
   against the original email. Deadline = receipt +24 hours; never infer from Git/PDF dates.
2. Operator reports repository now **Private** and all 11 accounts invited. Obtain
   authenticated visibility/invitation confirmation; current API404 is inconclusive.
3. Compare invitee/collaborator names against all 11 exact PDF handles; valid pending
   invitations and accepted access are distinct. See FINAL_SUBMISSION_AUDIT.md.
4. Confirm remaining Snowflake trial credits/monitor coverage with the account admin.
5. Include the private demo access note, and verify the submitted commit has pushed.
6. Obtain explicit user authorization to send. No email has been sent or scheduled.
