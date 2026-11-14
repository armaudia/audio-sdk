# Individual CLA acceptance process

The beneficiary is **Tsakanyan Hovhannes**, acting personally, not through a
company or LLC. The public agreement is [version 1.0](individual.md).

Contributors retain copyright. Accepted contributions also remain available
under the open-source license of the targeted component at Submission. The CLA
additionally permits commercial relicensing by the Maintainer; it does not clear
third-party material or transfer copyright ownership.

Before a substantive external contribution is merged, request private signing
instructions from Tsakanyan Hovhannes using a verified contact channel on
[his GitHub profile](https://github.com/hovhannest). A paper signature or explicit
verifiable electronic acceptance may be used by prior agreement. Public PR
comments are not the default signing channel.

The Maintainer verifies the legal name, contact, GitHub identity, authority,
agreement version/hash and signature or explicit acceptance. Signed records and
employer authorizations are retained in access-controlled private storage outside
these source repositories. They are used to administer contribution rights and
retained only as needed to evidence grants and applicable obligations. Requests
to correct records or remove nonessential contact data use the same private
channel. No actual acceptance records or signatures exist merely because this
agreement has been published.

After verification the Maintainer adds a minimal approval to approvals.json:
stable GitHub user ID, GitHub login, agreement SHA-256 and an opaque record ID.
No legal name, email, signature or acceptance document is committed publicly.
CI trusts only the ledger already present in the PR's base revision; a PR cannot
approve its own contributor by editing the ledger. The owner is exempt for his
own first-party code. Empty approvals mean external contributions cannot merge
until a real private acceptance has been verified.

Corporate-owned work requires appropriate written authorization or an additional
rights-holder agreement before approval. There is no automatic corporate CLA.
