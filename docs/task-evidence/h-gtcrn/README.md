<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-H-GTCRN — two-microphone H-GTCRN readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for `h-gtcrn` (title
"H-GTCRN", mode `feasibility`, `verification_profile: enhancement`). It is
**not** an H-GTCRN implementation. No upstream checkout, checkpoint, weight
fragment, FD-WPE or AuxIVA asset, runtime, two-channel recording, enhanced
signal, listening result, device timing, benchmark or release claim is
present. **No result here qualifies H-GTCRN.**

## Exact external blocker

The census records one row:

> **H-GTCRN** | Two-microphone low-SNR enhancement combining GTCRN, FD-WPE,
> AuxIVA and spatial features | Official MIT repository publishes inference
> code and two checkpoint variants. | Conditional multichannel task, not
> comparable on mono CLN-01. Retain for a separate stereo/spatial suppression
> benchmark; checkpoint-specific terms/hash and compatible multichannel data
> must be verified before acquisition.

`research/noise_suppression_candidate_census.md`, line 37. The row supplies a
repository link (`https://github.com/Max1Wz/H-GTCRN`), an MIT label, two
unnamed checkpoint variants, two microphones and four components. It supplies
**no** immutable revision, source file, license text, checkpoint file name,
byte count, SHA-256, checkpoint-specific terms, runtime lock, sample rate,
frame/hop, STFT window, lookahead, channel order, FD-WPE/AuxIVA/spatial-feature
settings, cohort, clean reference or output. The local asset register has no
H-GTCRN row; its only GTCRN entry is the separate mono `GTCRN-DNS3` component.

The exact blocker is therefore: **no caller-supplied, rights-cleared,
identity-verified H-GTCRN asset set and no rights-cleared two-channel low-SNR
matched cohort.** Missing artifacts are not downloaded, reconstructed, mirrored,
substituted or inferred from adjacent GTCRN, AuxIVA or survey evidence.

Six open blockers:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The official source at an immutable 40-hex commit, with reviewed MIT license text, notice, per-file SHA-256 and a map from GTCRN, FD-WPE, AuxIVA and spatial features to source files. |
| `BLK-02` | Both reported checkpoint variants with exact file names, revision, byte counts, SHA-256 values and checkpoint-specific terms separate from the code license. |
| `BLK-03` | A locked offline runtime with exact Python/framework/package versions, wheel hashes, device, determinism settings and install location. |
| `BLK-04` | Reviewed source, checkpoint and training-data terms; corpus, clean-reference, output-use and redistribution rights with an independent review reference. |
| `BLK-05` | Frozen two-microphone geometry and state: channel order, rate, frame, hop, STFT, lookahead, FD-WPE, AuxIVA, spatial features, reset and streaming behavior. The census records none of these. |
| `BLK-06` | A rights-cleared two-channel low-SNR cohort with capture/array geometry, speaker consent, quiet/active and onset/offset strata, held-out splits, controls, baseline, paired SI-SDR/STOI where permitted, preservation, peaks, invalid outputs, alignment, timing and memory. |

**Reopen condition.** A caller supplies the exact source and both checkpoints
with verified identity and artifact-specific rights, an isolated hash-pinned
runtime, the exact two-channel geometry and state contract, a rights-cleared
matched cohort, a deterministic reproduced Enhancement result set, separate
mode/platform and timing evidence, and an opt-in OFF-by-default provider
intake with independent exact-head review. Until then this task stays `DEFER`.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Two-microphone low-SNR enhancement | No execution |
| Components | GTCRN, FD-WPE, AuxIVA, spatial features | No source or asset identity |
| Channels | 2 | No two-channel input or output exists |
| Checkpoint variants | 2, unnamed | No file, revision, bytes or SHA-256 |
| Sample rate / frame / hop / STFT / lookahead | not reported | unverified |
| Channel order / array geometry | not reported | unverified |
| FD-WPE / AuxIVA / spatial-feature settings | not reported | unverified |
| Mono CLN-01 comparability | explicitly not comparable | no mono result inherited |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | unchanged; no H-GTCRN mapping |

The public v0 mono path is preserved and is not a two-channel H-GTCRN path.
No descriptor, provider, registry, default, ABI, shared build or CI change is
made.

## What this package verifies

1. **Absence evidence.** A fixed list of workspace, SDK-worktree and home-cache
   probes is checked without a recursive walk. All are absent. The report
   builder and verifier fail if any later appears, so a stale absence claim
   cannot ship.
2. **Asset-register absence.** The pinned `noise_suppression_assets_20261027.json`
   is parsed strictly: 20 candidate ids, no H-GTCRN entry, and only the
   separate `GTCRN-DNS3` mono component. No checkpoint identity is invented.
3. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
4. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
5. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, checkpoint, runtime, two-channel geometry, input,
   control and rights fields. Unknown or missing fields, duplicate JSON keys,
   nonfinite values, floats, unsafe paths, wrong interpreter, mono geometry,
   missing FD-WPE/AuxIVA/spatial components, rate mismatch, unconsented input,
   false controls and false rights are all rejected. One synthetic schema
   control is accepted to prove the validator is not blanket-rejecting; it is
   marked `synthetic_schema_control`, `qualifies=false` and is not evidence.
6. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted.
7. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/h-gtcrn/` as `base_out_of_scope_change`. Regression tests
   cover sibling merges, an out-of-scope branch edit and a missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control or baseline output on exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared two-channel cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labeled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and content/availability timing | blocked | No runtime, state, timing or memory record. |
| Two-channel geometry, channel order and component settings | blocked | Census records channels and components only. |
| Quiet/active, idle-noise and low-SNR strata | blocked | No corpus or stratum. |
| Separation of paired, unpaired, synthetic, human and source-reported evidence | documented | Absence only; no result of any class exists. |

## Matched-evidence boundary

`gtcrn-dns3-offline` and `gtcrn-streaming-onnx` are separate mono base-GTCRN
components. `auxiva` is deliberately isolated from this bundled row. The
`survey-spk-01` coverage survey records H-GTCRN as considered with no local
execution. None of their fixtures, checkpoints, scores, timings, state models or
rights records are inherited. The mono CLN-01 candidate matrix does not list
H-GTCRN and cannot score it.

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
directory. Repository checks are `python scripts/ci.py`, `python -m reuse
lint` and `git diff --check`.

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
| `sdk:docs/task-evidence/auxiva/README.md` | `efeeda6457b5e9e8153253b93e107cc003fc1c9b705bdd399ac908a03254d81b` |
| `sdk:docs/task-evidence/auxiva/report.json` | `92f21086d2988286c487228171621b0c5c35f2bf65141acac160f9811581db26` |
| `sdk:docs/task-evidence/gtcrn-dns3-offline/README.md` | `c602bfab8b0b313a6b2e3976281858c6db7b9f102cc4f220ec4e9f75c47e267b` |
| `sdk:docs/task-evidence/gtcrn-dns3-offline/report.json` | `b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd` |
| `sdk:docs/task-evidence/gtcrn-streaming-onnx/README.md` | `ca8ab3a8d0d482ce86e2032d54b9f4f5ede000a18f7b1d59dd3d18a7fa199553` |
| `sdk:docs/task-evidence/gtcrn-streaming-onnx/report.json` | `34970e44019cf99eddccfebddce2c19de1dbddda7108fe69e77040f2b503163d` |
| `sdk:docs/task-evidence/survey-spk-01/README.md` | `554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d` |
| `sdk:docs/task-evidence/survey-spk-01/report.json` | `04f17e36954b792bcba59b59fef537f6e699654cc6fd71c39e46567809a6ff2f` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `f25415bbda535459d8ce5fbcd03391c1eafc6f68a79577ac0c2df67025afdbf9` | 1846 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `abf5d2cc7b3736fb66811b0d88ceebba9f8ee0ec40135773e1e6bf1400f9b5a2` | 23535 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `7115e2ae53d3156dcdc5095fcf9cabb1a4a687d4b9389d984dcc48e04dd35cea` | 82388 |
| `report.json` | `d40ed21b30cd44806765aa6d11e3633601fd6b300aeca817572e4e9b2555a788` | 42384 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `4b1dad925ffe4c7e3c9abc4bb745a07d2c8227248ee819b935562a298669321f` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `175d60b243faf15fdb028739abdaf08be67be037b93743fd16a2d72b658371f2` | 4891 |
| `test_reference.py` | `7413e95dbef637b31557b24ea4dd69571ddfacbfe73e941427ca7b82fa669507` | 27540 |
| `verify.py` | `7e620f0cca6f64847361aaff90fec4267674e786da5ae8bb34d567d62b7e86ab` | 25462 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.
