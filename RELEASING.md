# Release and maintenance policy

## Branches and ownership

`main` accepts squash merges through pull requests. The intended GitHub rules
require a fresh code-owner approval, approval of the last push, resolved review
threads, and the `quality` check from GitHub Actions with an up-to-date branch.
Force pushes, deletion and merge commits are blocked, without ruleset bypass
actors. A second reviewer is therefore required when the owner authors a change.
CODEOWNERS names the initial maintainer; change it through a reviewed PR.

To audit the complete source history and inspect the exact destination:

```sh
python scripts/publish_repository.py
```

With an authenticated GitHub CLI, add `--apply` to create the repository with its
requested visibility and push the audited commit to main. It refuses a dirty
working tree, an unexpected origin, model/key files or common secret patterns in
history, and a mismatched existing repository visibility. It never force-pushes.

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

CI uses immutable GitHub Action commits, read-only tokens, and an aggregate
`quality` check. Linux and macOS run installed-consumer tests. Windows also runs
both providers from the extracted archive with the compiler directories removed
from `PATH`. The WebAssembly static archive is tested in Node.js using the packaged
C example and both built-in providers. Browser integration requires its own tests.

Public release tags are `v0.1.0` or `v0.1.0-rc.1` (and alpha/beta equivalents).
The release workflow reruns CI, requires the tag's commit to be on main, requires
approval in the `release` environment, verifies the four platform archive checksums,
and attests the artifacts before publishing them. Assets are attached to a draft
first, then the release is published with repository release immutability enabled. Only organization owners may create release tags. Separate immutable-tag rules
without bypass actors prevent those tags from being rewritten or deleted. A corrected release uses a new version. PyPI upload, public benchmark
publication, third-party code execution and model distribution are not enabled by
these workflows.

Before creating a stable release, record scope-specific source/license decisions,
passing hosted runs for the advertised targets, clean install evidence, remaining
limitations, and release notes. Local tests or a CI configuration are not a
production qualification. Do not reclassify pending legal, model, data, parity or
workload evidence as passing. Historical task handoffs retain their original scope.
