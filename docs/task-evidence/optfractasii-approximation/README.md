<!-- SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPTFRACTASII-APPROXIMATION - blocker evidence package

**Status: `incomplete`; evidence `incomplete`; decision `DEFER`; qualification `not_qualified`.** This directory is bounded, deterministic, task-local blocker evidence for the OptFractASII approximation research-control row. It is **not** an implementation, not a qualified DSP result, and not a release claim. No exact licensed upstream OptFractASII artifact, runtime, rights-cleared cohort, listening result, device timing, or benchmark result is present. **No result here qualifies.**

## Task identity

| Field | Value |
| --- | --- |
| Task | `SDK-OPTFRACTASII-APPROXIMATION` |
| Title | OptFractASII approximation |
| Mode | `research-control` |
| Profile | `DSP` |
| Decision | `DEFER` |
| Qualification | `not_qualified` |
| Base commit | `0b0f2dee5902278fcea1a47f576b4df70e99ab3a` |
| Branch | `swarm/SDK-OPTFRACTASII-APPROXIMATION` |
| Write scope | `docs/task-evidence/optfractasii-approximation/` only |

## Scope and boundary

This package records only task-local evidence files under `docs/task-evidence/optfractasii-approximation/`. It makes no provider registration, descriptor/registry/default change, public ABI/header change, shared CMake/CI change, installed-v0 behavior change, board/handoff change, or release claim. The mutable shared board is never pinned; only stable linked-row identity is gated.

## Source-reported context (not qualification)

The pinned research note `research/listening_intelligibility_20261028.md` is source-reported context only. It describes a small objective screen where a local OptFractASII-inspired approximation was **not** selected for deployment; no listener test was run and margins were small/uncertain. This package does not promote those numbers to qualified DSP evidence.

## Exact blockers

| ID | Status | Blocker | Reopen condition |
| --- | --- | --- | --- |
| BLK-01 | open | No exact immutable upstream OptFractASII source/license/notice/reproduction recipe. | Supply exact immutable artifact with reviewed license/notice and per-file hashes. |
| BLK-02 | open | No pinned offline runtime and exact task geometry/delay/energy contract. | Provide locked runtime, geometry manifest, and deterministic execution logs. |
| BLK-03 | open | No rights-cleared target/masker cohort with consent/hearing-profile/output-use decisions. | Provide reviewed rights/consent manifests and immutable cohort hashes. |
| BLK-04 | open | No qualified DSP-profile measurements or held-out masker comparison with equalized energy. | Run DSP profile on exact pinned artifact/runtime/cohort with required controls. |
| BLK-05 | open | No authorized listening/labeled screen, device timing, or independent OFF-by-default review. | Provide listener/device evidence and independent review after prior gates clear. |

## Release gates (all blocked)

| Gate | Status | Qualifies | Reopen condition |
| --- | --- | --- | --- |
| RG-01 | blocked | false | Exact artifact identity/license/notice. |
| RG-02 | blocked | false | Keep research note source-reported unless exact evidence exists. |
| RG-03 | blocked | false | Pinned runtime and geometry. |
| RG-04 | blocked | false | Rights-cleared cohort. |
| RG-05 | blocked | false | DSP profile measurements. |
| RG-06 | blocked | false | Held-out masker comparison. |
| RG-07 | blocked | false | Listener/device timing evidence. |
| RG-08 | blocked | false | Independent OFF-by-default release review. |

## Reproduction

All commands run from this directory with CPython 3.11.5 and `PYTHONDONTWRITEBYTECODE=1`.

```sh
python3 reference.py > /tmp/optfractasii-report.json
python3 run.py all --repeats 3
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py all` regenerates `contract.json`, `report.json`, `report.json.sha256`, `SOURCES.sha256`, and README digest tables three times and fails on byte drift. `verify.py` is read-only/fail-closed and performs cold-start regeneration in a temp directory.

## Pinned source digests

<!-- digest-table: source -->
| key | sha256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/listening_intelligibility_20261028.md` | `f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a` |
<!-- digest-table: end -->

## Pinned boundary digests

<!-- digest-table: boundary -->
| key | sha256 |
| --- | --- |
| `boundary:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `boundary:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `boundary:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `boundary:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `boundary:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| key | sha256 |
| --- | --- |
| `artifact:LICENSES.md` | `966cd25a388c0c62449353b138ceaf6ee5a4ad28df0f11d6a45cbaa4ae9c93fa` |
| `artifact:SOURCES.sha256.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `artifact:contract.json` | `4a0c8679406b599457ebbf9ca7394fcf5998561bc4acda20080c36758ff0cd6c` |
| `artifact:contract.json.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `artifact:reference.py` | `c4f7f5bc19205e8c2a58db07b0163e6c2b96ca1f75ec1684309af567533cd4d6` |
| `artifact:report.json` | `7eb9d015a42a7cb3bacbf824c74fe919eced53888faaba64840623c9547704c4` |
| `artifact:report.json.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `artifact:report.json.sha256` | `c97e534a4dbbbc4405a7a715422526dc59f0bcb2c369a92faa6ba3ab1afad0da` |
| `artifact:report.json.sha256.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `artifact:run.py` | `cc5302ad10716bb5ad890e9861701209f97c1da97715f6cbf822a476c062a9a0` |
| `artifact:test_reference.py` | `cc87769ef1a942b08c305e2de8d7ebae6a3abd1e4ffd254869ffabb20188098f` |
| `artifact:verify.py` | `298d9196381cbbc4075f5ede85ba548f418a44f83fb814081f55a341346d72d4` |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
