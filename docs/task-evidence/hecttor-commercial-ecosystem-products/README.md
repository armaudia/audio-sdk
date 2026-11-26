<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-HECTTOR-COMMERCIAL-ECOSYSTEM-PRODUCTS — vendor-boundary blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local external-comparison record for
`hecttor-commercial-ecosystem-products` (title "Hecttor / commercial ecosystem
products", mode `external-adapter`, `verification_profile: external`). It is
**not** a Hecttor adapter, vendor integration or benchmark. No Hecttor SDK,
platform build, evaluation key, license text, model asset, runtime, processed
data, vendor output, listening result, device timing, benchmark or release
claim is present. **No result here qualifies any Hecttor product.**

## Exact external blocker

The census names exactly one Hecttor product:

> **Hecttor Hermes noise cancellation** | Commercial native SDK with two
> optional denoising model families and blend control | Official docs support
> six SDK languages/platforms, multiple sample rates, denoise-only module
> configuration; evaluation license/key and platform build are supplied
> through onboarding. | Include as licensed black-box comparator if evaluation
> access is available; isolate noise cancellation and disable Voice
> Boost/speed-control; freeze SDK/model/version and document
> telemetry/deployment terms.

`research/noise_suppression_candidate_census.md`, line 80. The product note at
line 122 adds that noise cancellation is an independent feature but "requires
commercial evaluation onboarding and a key; assess only if access is granted
and its data-handling terms fit the benchmark."

The record supplies a product name, two optional model families, a blend
control, six SDK language/platform targets, multiple but unspecified sample
rates, a denoise-only module configuration and onboarding-gated access. It
supplies **no** release version, ABI, platform build, artifact file name, byte
count, SHA-256, license text, evaluation key, telemetry statement, deployment
grant, frame/hop/reset/drain contract, channel layout, processed data, vendor
output or score. The local 20-row asset register has no Hecttor entry.

The exact blocker is therefore: **no approved, identity-pinned, rights-cleared
Hecttor evaluation runtime and no rights-cleared processed data or vendor
output.** Missing artifacts are not downloaded, reconstructed, mirrored,
substituted or inferred from adjacent commercial-vendor or open-model evidence.

Six open blockers:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Approved Hecttor evaluation onboarding for the exact product, with scope, duration, permitted use, evaluation license text and key reference. |
| `BLK-02` | The exact Hermes release and platform build, with version, ABI, install location, byte counts, SHA-256 values and a signed artifact manifest. |
| `BLK-03` | A locked offline host runtime with exact OS, interpreter, vendor SDK, package versions, device, determinism settings and install digest. |
| `BLK-04` | Reviewed vendor, evaluation, telemetry, data-handling, deployment, redistribution and output-use terms with an independent review reference. |
| `BLK-05` | Frozen denoise-only configuration with Voice Boost and speed-control disabled, exact rate/frame/hop/reset/drain contract, channel layout, model/blend selection and state behavior. |
| `BLK-06` | A rights-cleared input cohort, vendor-processed output on the approved runtime, and separated local-runtime, vendor-output-scoring and vendor-claim results with controls, baseline, metrics, preservation, peaks, invalid outputs, alignment, timing and memory. |

**Reopen condition.** A caller supplies approved onboarding and entitlement, the
exact product release and platform artifact with verified identity and rights, a
locked offline runtime, the denoise-only isolation contract, a rights-cleared
input cohort, vendor-processed outputs, separated scoring/claim records, and an
opt-in OFF-by-default provider intake with independent exact-head review. Until
then this task stays `DEFER`.

## Vendor boundary

| Property | Reported by source | Verified here |
| --- | --- | --- |
| Vendor | Hecttor | Name only; no legal entity or terms record |
| Product | Hermes noise cancellation | Name only; no release identity |
| Model families | 2 optional denoising families | Not mapped, loaded or executed |
| Blend control | Present | Configuration unverified |
| SDK targets | 6 languages/platforms | No build, ABI or platform package |
| Sample rates | Multiple, unspecified | No rate list, frame, hop or resampling policy |
| Denoise-only module | Reported available | Isolation not verified |
| Access | Evaluation onboarding + key | Not approved; no key present |
| Telemetry / deployment terms | Recommended by census | Not documented or reviewed |
| Latency / timing | Not reported | Not measured |
| Source or model portability | Not a portability claim | Explicitly out of scope |

The installed v0 geometry is unchanged at 16 kHz, mono, float32, 160 samples
per frame. It is not a Hecttor path, and no vendor multi-rate or multi-platform
mapping is asserted.

## External profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Document allowed access and exact candidate or processed data | blocked | Onboarding approval, key, release and processed data are absent. |
| Pin exact product, release, SDK platform build and artifact identity | blocked | Only product name and broad capabilities are reported. |
| Pin exact processed data and provenance | blocked | No clip, output bundle or provenance exists. |
| Separate local runtime, vendor-output scoring and vendor claim | documented | Three explicit empty classes; nothing is pooled. |
| Verify fallback and disclosure without a licensed runtime, code or asset | documented | Fixed absence probes, shape-only validation and explicit DEFER disclosure. |
| Review vendor terms, telemetry, data handling and deployment | blocked | No terms text or grant is recorded. |
| Isolate noise cancellation and disable Voice Boost/speed-control | blocked | No runtime or frozen configuration to verify. |
| Produce matched vendor-output scoring and product comparison | blocked | No approved runtime, output, scorer, cohort or score. |

## What this package verifies

1. **Absence evidence.** A fixed list of workspace, SDK-worktree and home-cache
   probes is checked without a recursive walk. All are absent, and the report
   builder fails if any later appears.
2. **Asset-register absence.** The pinned register is parsed strictly: 20
   candidates, no Hecttor or Hermes entry. No release or artifact identity is
   invented.
3. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers every task-local file except itself.
4. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim, review,
   handoff, priority and history never enter canonical bytes.
5. **Fail-closed vendor-access validation.** A strict manifest requires exact
   vendor, product, release, artifact/terms digests, onboarding approval,
   evaluation-key digest, platform build, absolute install root, telemetry
   disclosure, denoise-only isolation, Voice Boost/speed-control disablement,
   locked offline deterministic runtime, mono accepted-rate input, consent,
   controls and rights. Unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, unsupported rates, stereo input, unapproved
   access, enabled Voice Boost/speed-control and false rights are rejected. One
   synthetic schema control is accepted to prove the validator is not
   blanket-rejecting and remains `qualifies=false`.
6. **Fail-closed vendor-output validation.** A second strict bundle shape
   records hashed input/output pairs, byte counts, finiteness, rate/channel
   agreement, claim state and output rights. A nonfinite or mismatched bundle
   is rejected. The accepted synthetic control is not vendored output and is
   never scored.
7. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside the task directory as
   `base_out_of_scope_change`.

## Fallback and disclosure

Without a licensed runtime, code or asset, the package can only:

- prove a fixed absence inventory and the absence of a local asset-register row;
- validate a caller-supplied access manifest and vendor-output bundle for shape
  and internal consistency, without resolving a path, importing a vendor SDK,
  reading a key or opening audio;
- disclose `DEFER` and `not_qualified` explicitly, with no score, ranking,
  latency, resource or quality claim.

The fallback produces **no** Hecttor output. It cannot substitute for the
vendor runtime, a rights-cleared cohort, processed data or an approved scorer.

## Evidence classes kept separate

| Class | State |
| --- | --- |
| Local runtime result | Empty: no runtime present or executed |
| Vendor-output scoring | Empty: no output bundle, scorer or score |
| Vendor claim | Empty: no claim record; nothing verified |
| Synthetic schema control | Present, `qualifies=false`, not evidence |
| Peer commercial-vendor evidence | Not inherited or pooled |
| Open-model or survey evidence | Not inherited or pooled |

## Reproduction

The canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, the report sidecar, the
README digest tables and `SOURCES.sha256` three times and requires
byte-identical output. `verify.py` is read-only and writes only to a temporary
directory. Repository checks are `python scripts/ci.py`, `python -m reuse lint`
and `git diff --check`.

## Source pins

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:docs/task-evidence/ai-coustics-quail/README.md` | `66239ce8eeff8598145c0b356f09c91ece6a53f1cbe425a77e5b3d5bfc8e2781` |
| `sdk:docs/task-evidence/ai-coustics-quail/report.json` | `77ac817a110bd243849c6e117e9b805f6a5aad082b5dd3befc6b20ff2dc218a0` |
| `sdk:docs/task-evidence/ai-coustics-rook/README.md` | `ce038c74b0983d57f9d1d3f75713df810c9e2c5e9a3b79c6710b4012e6f44ff3` |
| `sdk:docs/task-evidence/ai-coustics-rook/report.json` | `e69a2bf3dd3e7fd496176c77c04285d9bd5d37f09fd4f76a51be394239832f20` |
| `sdk:docs/task-evidence/desert-ant-labs-clear/README.md` | `9be228d342086644c42e8bf6d3cebc8c0800a3050a91b2a7a4ecf55a061914c7` |
| `sdk:docs/task-evidence/desert-ant-labs-clear/report.json` | `d25b33e6ca4febbd6ea8af385c3736e96ce45ed31ccb46ad16740a4f81be52ac` |
| `sdk:docs/task-evidence/h-gtcrn/README.md` | `e36ed7a596a6f9954c492de441486464a8bc2d8fdd02222c5a6a6eb27eec3fe4` |
| `sdk:docs/task-evidence/h-gtcrn/report.json` | `d40ed21b30cd44806765aa6d11e3633601fd6b300aeca817572e4e9b2555a788` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `2bde46e307f4749f02fe4118a749da3f42f0e03a2132ab2065b8c4250334b0b5` | 1353 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `0d8a8bd571c446fdfe6df152bf6abf9c10486d38cd3400ff1238d08803124d8b` | 25821 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `79981e5900ca98aa3a7e82d385fbf13f13fc4de9fd2eb2c3def1a20c3700f6cb` | 91972 |
| `report.json` | `c66f5fb2f76b0b639f6c605c21d9bb6121025cc931a26ab3a253ef3cf1977cb4` | 47138 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `268db4be2c80e3872b95a211e1bc34d7471be4234153dbf2e3f493eabd2cbd25` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `8421add3f32898f42c233053009840a79e049fe30ddacfb670447b0b1b01253c` | 4917 |
| `test_reference.py` | `12125b28f6eb0913f778fa918a47d5560902879a6dbcef79ed4f9baa31646ab2` | 30226 |
| `verify.py` | `3a8e8130c4209cd26aa4052710aed77afe12e467c9a02b425c300f9e377b44a8` | 27493 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
