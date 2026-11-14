# Local release-hardening evidence, 2026-11-14

Status: local engineering checks, not a production or public-release qualification.
The user's publication request authorizes repository preparation and publishing;
it does not supply missing third-party model or dataset permissions.

## Verified locally

- Clean Release build and native CTest: 11/11 passed.
- Installed C11/C++20 consumers and both built-in provider conformance runs passed.
- Installed external-provider CTest: 10/10 passed.
- Fresh Python 3.12 wheel installation outside the checkout: 5/5 tests passed,
  including integer-boundary rejection and exact counters above 2^53.
- GitHub-policy precondition unit tests: 2/2 passed.
- Repeated normalized archive creation produced identical bytes. Before the
  notice/install-layout update, the clean build reproduced Candidate 09 exactly.
- Updated native package SHA-256:
  `1c2406000291132f8a8587894dd2d7a69eb079366bb8b702623c61a491c54440`.
- Native source/runtime behavior is unchanged; the new package carries corrected
  notices and an installed root license. Python validation and release tools changed.

## Prepared, requiring hosted verification

- Linux x86-64 and macOS arm64 CI, with pinned official Action commits, read-only
  tokens, machine-readable test reports and an aggregate required quality check.
- SDK CI additionally runs address/undefined and thread sanitizer jobs.
- Code ownership, dependency update configuration, main/tag rulesets and an
  administration script with preconditions and settings readback.
- Public-repository release workflows rerun CI, verify reviewed ancestry and
  archive checksums, require release-environment approval and attest artifacts.
- Source history was checked for common GitHub/AWS/private-key secret patterns;
  no matches were found. This is not an independent security audit.

## Outstanding

GitHub authentication, repository creation/push, hosted job results, policy and
visibility readback, and release-environment configuration are not yet complete.
The public benchmark license choice is pending. Workload/target acceptance,
independent security review, corpus and model rights/reference evidence remain
outside the locally verified scope. Do not call the private neural product a
qualified commercial release.
