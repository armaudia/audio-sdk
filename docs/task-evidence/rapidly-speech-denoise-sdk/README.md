<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RAPIDLY-SPEECH-DENOISE-SDK — Rapidly vendor-boundary blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`rapidly-speech-denoise-sdk` (mode `external-adapter`, verification profile
`enhancement`). It is **not** a Rapidly adapter, vendor integration, license
grant or benchmark. No Rapidly SDK, native binary, model byte, commercial
entitlement, reviewed terms, runtime, corpus, recording, enhanced waveform,
listening result, device timing, benchmark or release claim is present.
**No result here qualifies the Rapidly speech-denoise SDK.**

Claim base: audio-sdk `80dc1fb371e1846a5d50f5b28c955ab92bfcbe46`; branch
`swarm/SDK-RAPIDLY-SPEECH-DENOISE-SDK`. Owner:
`agent-RAPIDLY-SPEECH-DENOISE-SDK`; reviewer:
`reviewer-RAPIDLY-SPEECH-DENOISE-SDK`. Depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`. Write scope is task-local only:
`docs/task-evidence/rapidly-speech-denoise-sdk/`.

## Exact external blocker

The census records one row at line 56 of
`research/noise_suppression_candidate_census.md`:

> **Rapidly speech-denoise SDK** | On-device commercial denoiser, outputs
> speech and isolated-noise busses | Official SDK bundles macOS/native binaries
> and models, supports CPU, 48 kHz trained models and 11/21/32/96 ms latency
> variants; unlicensed output is audibly watermarked. | Commercial product
> comparator only; benchmark demo mode cannot yield valid quality scores.
> Requires a suitable model entitlement and explicit commercial terms.

The pinned candidate-store snapshot adds: `benchmark_state: not_run`,
`commercial_license_required: true`, `watermarked_without_license: true`,
`trained_rate_hz: 48000`, latency variants `11/21/32/96 ms`, model sizes
`615/851/854/925 KB`, output busses `dialogue` and `noise`, `weights:
located_unverified` and `eligibility.state: blocked`. The task deliverable says
to document the vendor boundary and prototype only if an approved public or
user-supplied runtime is available. No such runtime, entitlement or terms are
present.

The exact blocker is the combination of:

1. **No locally verified SDK artifact.** The source repository is reported as
   available, but no release version, native binary, immutable revision, byte
   count or SHA-256 is present. `code: available` upstream is not a local asset
   or a rights grant.
2. **No reviewed commercial terms or entitlement.** A commercial license and a
   suitable watermark-free model entitlement are required. No terms record,
   telemetry/deployment review or entitlement is present; no secret may be
   committed, logged or embedded in a manifest.
3. **Unlicensed output is watermarked.** The census says demo-mode output
   cannot yield valid quality scores. Any watermarked or unentitled output is
   inadmissible as evidence, independently of any quality measurement.
4. **Model identity is unverified.** Four latency variants and four model
   sizes are reported, but the store records weights as `located_unverified`.
   No model revision, byte count or SHA-256 is locally verified.
5. **No rate/format/frame contract.** The models are reported as 48 kHz
   trained; the installed v0 path is 16 kHz mono float32 with 160-sample
   frames. No resampler, chunk/hop, reset or tail contract is supplied. Rate
   and channel proximity is not an adapter.
6. **No rights-cleared matched cohort or result.** There is no 16 kHz mono
   held-out cohort, identity/noisy control, baseline, frozen output, paired
   score, preservation record or paced timing evidence.

| Blocker | State | Requirement to reopen |
| --- | --- | --- |
| `BLK-01` | absent | Immutable Rapidly SDK release with version, platform, library byte count and SHA-256. |
| `BLK-02` | unreviewed | Reviewed commercial terms, telemetry/deployment terms and a watermark-free entitlement held outside git. |
| `BLK-03` | blocked | Proof of watermark-free output under an approved entitlement before any quality measurement. |
| `BLK-04` | absent | Exact 48 kHz model variant, latency variant, revision, byte count and SHA-256. |
| `BLK-05` | absent | Frozen 48 kHz-to-16 kHz, mono, float32, 160-sample mapping with resampler, chunk/hop and reset/tail policy. |
| `BLK-06` | absent | Rights-cleared 16 kHz mono cohort with controls, baseline, frozen outputs and paired scores. |
| `BLK-07` | absent | Alignment, state, memory and paced content/availability timing on the target device. |
| `BLK-08` | not_started | Opt-in adapter intake, descriptor/registry review, default decision and release approval. |

**Reopen condition.** A caller supplies the exact SDK and model artifacts with
verified identity, reviewed commercial/telemetry/deployment terms and a
watermark-free entitlement, the frozen 48 kHz-to-16 kHz mono float32
160-sample contract, a rights-cleared 16 kHz matched cohort, a deterministic
reproduced Enhancement result set with separate quality and timing evidence,
and an opt-in OFF-by-default provider intake with independent exact-head
review. Until then this task stays `DEFER`.

## Recorded upstream identity (source-reported, not locally verified)

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/rapidly-labs/rapidly-sdk` | absent; no immutable revision |
| Models documentation | `https://www.rapidly.io/docs/sdk/introduction/models` | absent |
| Release version | not reported | absent |
| Model revision / SHA-256 | not reported | absent |
| Trained rate | 48 kHz | reported only |
| Latency variants | 11 / 21 / 32 / 96 ms | reported only |
| Model sizes | 615 / 851 / 854 / 925 KB | reported only |
| Output busses | `dialogue`, `noise` | reported only |
| Platform | macOS and other desktop/mobile targets | reported only |
| Commercial license | required | reported only |
| Unlicensed output | audibly watermarked | reported only |
| Weights | `located_unverified` | reported only |
| Benchmark state | `not_run` | reported only |
| Eligibility | `blocked` | reported only |
| Source-reported score | none | not reproduced, pooled or qualified |

The candidate matrix at
`research/voice-enhancement-20261101/candidate_matrix.csv` has **no Rapidly
row**. No score is attached to this candidate by any pinned evidence file.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Single-channel denoise / noise suppression | No execution |
| Model training rate | 48 kHz | reported only |
| Channels | 1 | reported only |
| Latency variants | 11/21/32/96 ms | reported only |
| Output busses | dialogue + noise | reported only |
| Chunk / frame / hop / resampler | not recorded | unverified |
| 48 kHz-to-16 kHz mapping | not recorded | unverified |
| Reset / tail / pacing | not recorded | unverified |
| SDK v0 installed geometry | 16 kHz, mono, float32, 160 samples/frame | preserved; no Rapidly mapping |

The public v0 mono path is rate- and channel-adjacent to a single-channel
denoiser, but the reported 48 kHz training rate has no verified mapping to the
16 kHz v0 path. No descriptor, provider, registry, default, ABI, shared build
or CI mapping is added.

## What this package verifies

1. **Absence evidence.** 20 fixed workspace, SDK-worktree and home-cache
   probes are checked without a recursive walk. All are absent. The report
   builder and verifier fail if any later appears, so a stale absence claim
   cannot ship.
2. **Recorded-identity discipline.** Every vendor fact is marked
   `source_reported_not_locally_verified`, `locally_verified=false`,
   `admitted_as_result=false` and `qualifies=false`. The eight required
   artifacts keep `sha256`, `bytes` and `revision` null; no local identity is
   invented.
3. **Asset-register absence.** The pinned asset register is parsed strictly;
   it has no Rapidly entry. No identity is inferred from it.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact vendor, SDK, runtime, geometry, input, control and rights
   fields. Unknown or missing fields, duplicate keys, nonfinite values,
   floats, unsafe paths, unresolved text, wrong interpreter, online runtime,
   stereo or non-16 kHz geometry, a 16 kHz model rate, a missing resampler
   contract, an uncleared watermark, unconsented input, false controls and
   false rights are rejected. One synthetic schema control is accepted to
   prove the validator is not blanket-rejecting; it is marked synthetic,
   `qualifies=false`, and is not evidence.
7. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted and no
   watermarked output is admitted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/rapidly-speech-denoise-sdk/` as
   `base_out_of_scope_change`. Regression tests cover sibling merges, an
   out-of-scope branch edit and a missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control, baseline or entitled runtime output. |
| Paired SI-SDR and STOI | blocked | No rights-cleared paired 16 kHz cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labelled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and timing | blocked | No runtime, state, resampler or paced timing record. |
| Geometry, rate/format/frame and 48 kHz-to-16 kHz mapping | blocked | Reported 48 kHz models; no frozen contract. |
| Quiet/active, idle-noise and onset/offset strata | blocked | No corpus or stratum definition. |
| Evidence-class separation | documented | Census/store facts are labelled source-reported; no result of any class is promoted. |

## Matched-evidence boundary

The other commercial/comparator packages and historical DNS/AMI evidence are
separate components with their own assets, terms, geometry and blockers. Their
fixtures, checkpoints, scores, timings, state models and rights records are
not inherited. No Rapidly output exists here, so no comparison is made.

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
directory. Repository checks are the installed-package `python scripts/ci.py`,
`python -m reuse lint` and `git diff --check`.

## Source pins

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/store/snapshots/c85645e6921fd19919c389112656a361e58dc708f4524ced4f766c3a7e2d4d75.jsonl` | `c85645e6921fd19919c389112656a361e58dc708f4524ced4f766c3a7e2d4d75` |
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
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `919363cac7632afa7145efae2a38974988c3d9d6935d4b29262531fabb79c8ea` | 2466 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `fcf866e5290480366adb1d5f437d34a5c747a420b3236a6a3dab374bad572375` | 27398 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `bb146c566de8f101f37ea2a30fe7486a88c451bd62edd6d9ba36ff87e087e6a4` | 75894 |
| `report.json` | `3d5337e2be2f36addf8833e74a417a1c5f56bd885f1e51675c9e42dc3ffc2c49` | 42425 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `3fd9c840dbbc83de9214fa1ac0fb79c55e0fa3880626d1b3a0030f893b880007` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `990d10cbb5fefb3f43222d10dcc031fbdcc80f83da567299cb539eea55762d1f` | 4638 |
| `test_reference.py` | `5b8db946a5aac1f0de6e7f885dd593ed3fc1bf87885ca19389bf2c85f5d1a409` | 19854 |
| `verify.py` | `374e41af9006e73f9cefc5b2253e653b8105304af2c2ade3187567efde34ed08` | 19546 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.
