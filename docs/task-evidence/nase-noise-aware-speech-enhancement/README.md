<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NASE - NASE readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`nase-noise-aware-speech-enhancement` (title "NASE (Noise-aware Speech
Enhancement)", mode `feasibility`, `verification_profile: enhancement`). It is
**not** a NASE implementation, adapter or reproduction. No upstream source
checkout, diffusion checkpoint, BEATs conditioning encoder, weight byte,
sampler configuration, inference script, runtime, corpus, recording, enhanced
waveform, listening result, device timing, benchmark or release claim is
present. **No result here qualifies NASE.**

Pinned base: `e3e3deccb3c852bce8255305700be219ccceadb8`.
Branch: `swarm/SDK-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT`.
Owner: `agent-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT`.
Reviewer: `reviewer-NASE-NOISE-AWARE-SPEECH-ENHANCEMENT`.

## Exact external blocker

`research/noise_suppression_candidate_census.md`, line 71, records one row:

> **NASE (Noise-aware Speech Enhancement)** | Diffusion model conditioned by
> learned noise-aware BEATs embeddings; offline quality reference | Official
> research repo includes a pretrained VoiceBank+DEMAND checkpoint, test
> samples, evaluation scripts and code. | Useful distinct diffusion/
> noise-conditioning reference. Verify checkpoint and BEATs terms/provenance,
> model size and runtime; evaluate paired speech-preservation and quality
> metrics.

The discovery log (`research/evidence/pilot-discovery-20261027/source.txt`,
line 94) adds that the official diffusion-model codebase ships a pretrained
VoiceBank-DEMAND checkpoint, test outputs and metric scripts, that it uses a
learned noise-aware BEATs conditioning model, and that checkpoint and BEATs
terms plus compute cost are still unverified. The candidate accounting report
(`reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/`
`candidate_accounting.csv`, line 57) marks `candidate-nase` **blocked**, with
code `available` and weights `located_unverified`, because checkpoint and BEATs
encoder terms/provenance, artifact hashes, dependency compatibility and
inference cost are not verified. The asset register
(`research/noise_suppression_assets_20261027.json`) contains 20 separate
denoising assets and no NASE entry.

The exact blocker is therefore the combination of:

1. **No verified source identity or licence text.** The repository is named,
   but no immutable 40-hex commit, `LICENSE` text, notice, model card or
   per-file SHA-256 is staged. A repository name is not a reviewed licence.
2. **No exact NASE checkpoint identity.** The records say a pretrained
   VoiceBank+DEMAND checkpoint exists, but no file name, revision, byte count,
   SHA-256, tensor schema or checkpoint-specific terms is recorded.
3. **No exact BEATs conditioning encoder identity.** The learned noise-aware
   BEATs conditioning model is named, but no encoder checkpoint, revision,
   byte count, SHA-256, feature-extraction configuration or separate terms is
   recorded.
4. **No locked offline runtime or deterministic diffusion sampler.** No
   Python/PyTorch environment, wheel hash, device profile, sampler step count,
   noise schedule, seed policy, determinism setting or offline load path
   exists.
5. **No frozen offline diffusion geometry.** The evidence says "offline" and
   "diffusion" but records no sample rate, STFT window, hop, sampler,
   conditioning layout, padding, output length or normalization contract.
6. **No rights-cleared 16 kHz cohort and no matched result.** No paired
   clean-reference score, clean-speech preservation, peak, invalid or
   nonfinite-output record, alignment, state, memory or timing record exists.
7. **No opt-in intake.** No provider, descriptor, default selection, ABI,
   shared build, CI, board or handoff change is made.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from adjacent MP-SENet, LaCo-SENet, ConvFSENet, ROSE-CD, CoF,
Stream.FM, GTCRN, FastEnhancer, DeepFilterNet3, DTLN or other survey evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The official `YUCHEN005/NASE` source at an immutable 40-hex commit with reviewed licence text, notice, per-file SHA-256 and a map from the model, diffusion sampler, metric scripts and test samples to source files. |
| `BLK-02` | The exact pretrained VoiceBank+DEMAND NASE checkpoint with file name, immutable revision, byte count, SHA-256, tensor schema, inference configuration and checkpoint-specific terms. |
| `BLK-03` | The exact BEATs conditioning encoder checkpoint and feature-extraction configuration at immutable identity, with byte count, SHA-256, tensor schema and separate terms. |
| `BLK-04` | A locked offline runtime with exact interpreter, PyTorch/package versions, wheel hashes, CPU/MPS device, deterministic seeded sampler, step count, noise schedule and a recorded supported platform. |
| `BLK-05` | Reviewed source, NASE checkpoint, BEATs encoder and VoiceBank+DEMAND training-data terms; corpus and clean-reference permission; output use, redistribution and attribution. |
| `BLK-06` | The frozen offline whole-utterance diffusion contract plus a rights-cleared 16 kHz mono cohort, paired clean references, strata, controls, baseline, independent Enhancement, listening, timing and preservation results. |

**Reopen condition.** A caller supplies the exact source and reviewed licence,
the exact NASE checkpoint and BEATs encoder with verified identity and terms,
an isolated hash-pinned runtime with a deterministic seeded diffusion sampler
on a recorded platform, the frozen offline geometry, a rights-cleared 16 kHz
matched cohort, a deterministic reproduced Enhancement result set with separate
quality, preservation and timing evidence, and an opt-in OFF-by-default
provider intake with independent exact-head review. Until then this task stays
`DEFER`.

## Recorded upstream identity

None of the following is a local asset. No byte is present, opened, hashed or
executed here, so every identity field remains null and cannot qualify the
candidate.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/YUCHEN005/NASE` | absent |
| Source licence | not recorded in the pinned evidence | unresolved |
| Source commit | not recorded | absent |
| Model repository | `https://github.com/YUCHEN005/NASE` | absent |
| Model revision | not recorded | absent |
| Checkpoint file | not recorded | absent |
| Checkpoint bytes | not recorded | absent |
| Checkpoint SHA-256 | not recorded | absent |
| Conditioning encoder | learned noise-aware BEATs embeddings | identity absent |
| BEATs checkpoint | not recorded | absent |
| Inference script | described as provided | absent |
| Tensor schema | not recorded | absent |
| Reported metric | none recorded in the pinned evidence | not measured here |
| Paper | no URL recorded in the pinned evidence | not read locally |

These values are retained only to make the future exact-asset check
unambiguous. They are **not** local measurements and must not be compared with
the project DNS2020 results.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Single-channel speech enhancement / noise suppression | No execution |
| Domain | VoiceBank+DEMAND | no local cohort |
| Channels | 1 | no local audio |
| Sample rate | not recorded in the pinned evidence | unverified |
| Approach | Diffusion conditioned by learned noise-aware BEATs embeddings | lead only |
| Mode | Offline quality reference, no streaming claim | no inference contract |
| Diffusion steps and noise schedule | not recorded | unverified |
| BEATs conditioning layout | not recorded | unverified |
| STFT window, hop, padding | not recorded | unverified |
| Output length and normalization | not recorded | unverified |
| Streaming lookahead | not claimed; not measured | unverified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | preserved; no NASE mapping |

The public v0 mono path is channel-compatible with the reported single-channel
domain, but the reported sample rate is not recorded and no descriptor,
provider, registry, default, ABI, shared build or CI mapping is added. Channel
compatibility is not an adapter.

## What this package verifies

1. **Absence evidence.** 19 fixed workspace, SDK-worktree and home-cache probes
   are checked without a recursive walk. All are absent. The report builder and
   verifier fail if any later appears, so a stale absence claim cannot ship.
2. **No invented identity.** The checkpoint file, bytes, SHA-256, model
   revision, BEATs checkpoint and sample rate are `null`. No upstream metric is
   quoted, admitted or promoted.
3. **Asset-register absence.** The pinned asset register is parsed strictly:
   20 candidate ids, none for NASE. No checkpoint identity is inferred.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, NASE checkpoint, BEATs encoder, runtime, seeded
   diffusion sampler, 16 kHz mono offline geometry, input, controls and rights
   fields. Unknown or missing fields, duplicate JSON keys, nonfinite values,
   floats, unsafe paths, an unresolved licence, wrong interpreter, stereo or
   non-16 kHz geometry, streaming mode, non-zero lookahead, a non-BEATs
   encoder, a non-deterministic sampler, missing state reset, rate mismatch,
   unconsented input, false controls and false rights are rejected. One
   synthetic schema control is accepted to prove the validator is not
   blanket-rejecting; it is marked `synthetic_schema_control`,
   `qualifies=false` and is not evidence.
7. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/nase-noise-aware-speech-enhancement/` as
   `base_out_of_scope_change`. Regression tests cover sibling merges, an
   out-of-scope branch edit and a missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control or baseline output on exact NASE assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared 16 kHz paired cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labeled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and content/availability timing | blocked | No runtime, state, sampler timing or content-delay record. |
| Offline diffusion and BEATs conditioning geometry | blocked | No rate, STFT window/hop, sampler steps, noise schedule, conditioning layout, padding or output-length contract. |
| Quiet/active, idle-noise and onset/offset strata | blocked | No corpus or stratum definition. |
| Separation of paired, unpaired, synthetic, human and source-reported evidence | documented | The census is labelled a source lead; no result of any class is promoted. |

## Matched-evidence boundary

`mp-senet`, `laco-senet`, `convfsenet`, `rose-cd`, `cof`, `stream-fm`,
`gtcrn-streaming-onnx` and `fastenhancer-small-reference` are separate
components with their own assets, geometry and blockers. Their checkpoints,
BEATs or text encoders, diffusion settings, scores, timings, state models and
rights records are not inherited. The 30-pair DNS2020 results for other
candidates are same-task-context comparators only; they are not NASE
measurements and no upstream NASE metric is comparable to them.

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

<!-- DIGEST_TABLE_SOURCE_START -->
| Source pin | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/candidate_accounting.csv` | `7261b99e06460b612dcbebeec3859de60a7040a18444fc19a637ebddc4a58e3c` |
| `source:reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/manifest.json` | `e6a3e7c07504dd7919fc6314732c1db2e8bd2017c77a94aca1dc457737208440` |
| `source:research/evidence/pilot-discovery-20261027/source.txt` | `3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
<!-- DIGEST_TABLE_SOURCE_END -->

## Boundary pins

<!-- DIGEST_TABLE_BOUNDARY_START -->
| Boundary pin | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- DIGEST_TABLE_BOUNDARY_END -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `f5fbafd70bc6e007fd9811757594c4e23a3d68a987b6bd762b67502e8027c63a` | 1754 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `27c778e34a8003274662499e0b6dd2b9f1167cb2436cdd2d29a56f5191fc1583` | 23079 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `b3f61f7c37daaf9999240559c1e7894533d12bd82dabf7f49336060c7e647b2b` | 80368 |
| `report.json` | `92d4aeefe60067382dfb7a8dc487620df3c13b25079ab3a5c8b9a38613ec5d63` | 34075 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `6e1855ecfd6c89a2bc8f4cfe773a532ac8aa32feb78360fa7466276a7369c969` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `b88b3b198b3b8e5dc667ef68c165cb1cf68efef2ecf1dcf724cacd360b36a27a` | 4458 |
| `test_reference.py` | `8475d2cd8d0497cf9d89ed0fe2cd686c442cae141b32292c48fb26af5fba53e9` | 18300 |
| `verify.py` | `281e668c1ba2e45a34d3e756d93403acf9b49ab16f10c1c9e79a8999fb355277` | 21835 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pt`, `.pth`, `.ckpt`, `.onnx`, `.safetensors`, binary library, compiled
object, upstream source copy, licence text copy or model weight.
