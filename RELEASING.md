# Release and maintenance policy

## Branches and ownership

`main` accepts squash merges through pull requests. The intended GitHub rules
require a fresh code-owner approval, approval of the last push, resolved review
threads, and the `quality` check from GitHub Actions with an up-to-date branch.
Force pushes, deletion and merge commits are blocked, without ruleset bypass
actors. A second reviewer is therefore required when the owner authors a change.
CODEOWNERS names the initial maintainer; change it through a reviewed PR.

After the initial push and passing CI, an organization administrator runs:

```sh
python scripts/github_admin.py --repo audio-sdk
```

Replace audio-sdk with this repository's name. The script requires an
already authenticated GitHub CLI, checks admin access, verifies the current
commit's real CI status, applies the settings and reads them back. Actual
readback is saved under `build/github-settings.json`. Configuration files alone
are not proof that GitHub enforces a policy. Private-repository protection and
environment support depend on the organization's GitHub plan; an API refusal
must be resolved rather than described as enforced.

## CI and publishing

CI uses immutable GitHub Action commits, read-only tokens, clean Linux/macOS
runners, and an aggregate `quality` check that fails if any required job fails or
is cancelled. Workflow changes are reviewed as code. Dependabot proposes action
updates. Repository Actions must not approve their own pull requests.

Public release tags are `v0.1.0` or `v0.1.0-rc.1` (and alpha/beta equivalents).
The release workflow reruns CI, requires the tag's commit to be on main, requires
approval in the `release` environment, verifies both platform archive checksums,
and attests the artifacts before publishing them. Release tags cannot be rewritten
or deleted. A corrected release uses a new version. PyPI upload, public benchmark
publication, third-party code execution and model distribution are not enabled by
these workflows.

Before creating a stable release, record scope-specific source/license decisions,
passing hosted runs for the advertised targets, clean install evidence, remaining
limitations, and release notes. Local tests or a CI configuration are not a
production qualification. Do not reclassify pending legal, model, data, parity or
workload evidence as passing. Historical task handoffs retain their original scope.
