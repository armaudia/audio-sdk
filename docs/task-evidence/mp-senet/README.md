<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MP-SENET - MP-SENet readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for `mp-senet`
(title "MP-SENet", mode `feasibility`, `verification_profile: enhancement`).
It is **not** an MP-SENet implementation, adapter or reproduction. No upstream
source checkout, checkpoint, weight byte, inference script, runtime, corpus,
recording, enhanced waveform, listening result, device timing, benchmark or
release claim is present. **No result here qualifies MP-SENet.**

Pinned base: `d2eae1246561fe11c5a3d17733ddd46db53e7803`.
Branch: `swarm/SDK-MP-SENET`. Owner: `agent-MP-SENET`.
Reviewer: `reviewer-MP-SENET`.

## Exact external blocker

`research/noise_suppression_candidate_census.md`, line 31, records one row:

> **MP-SENet** | Parallel magnitude and phase spectrum estimation; offline
> 16 kHz quality reference | Official MIT repository includes pretrained
> VoiceBank+DEMAND checkpoint and inference script; author-reported PESQ 3.50.
> | Medium-priority phase-aware comparator. Checkpoint hash and dataset
> overlap; non-streaming and VoiceBank trained.

The discovery log (`research/evidence/pilot-discovery-20261027/source.txt`,
line 51) adds that the author repository provides MIT code, inference and a
pretrained checkpoint, that the authors report VoiceBank+DEMAND PESQ 3.50, and
that the paper/checkpoint are not directly comparable to DNS2020 and need
overlap/hash checks. The generated candidate accounting report marks
`candidate-mp-senet` **blocked**, with code `available` and weights
`located_unverified`, and asks for the artifact to be pinned/hashed, the
training/test overlap to be resolved and CPU/RAM to be measured.

The exact blocker is therefore the combination of:

1. **No verified source identity or license text.** The repository is
   described as MIT, but no immutable 40-hex commit, `LICENSE` text, notice or
   per-file SHA-256 is staged. A reported label is not a reviewed license.
2. **No exact checkpoint identity.** The census and accounting report say a
   pretrained VoiceBank+DEMAND checkpoint exists, but no file name, revision,
   byte count, SHA-256, tensor schema or checkpoint-specific terms is recorded.
   Training/test overlap with VoiceBank/DEMAND remains unresolved.
3. **No locked offline runtime.** No Python/PyTorch environment, wheel hash,
   device profile, determinism setting or offline load path exists.
4. **No frozen offline phase-aware geometry.** The evidence says the model
   estimates magnitude and phase spectra in parallel and is non-streaming, but
   records no FFT/STFT window, hop, branch layout, padding, output length or
   normalization contract.
5. **No rights-cleared 16 kHz cohort and no matched result.** No paired
   clean-reference score, clean-speech preservation, peak, invalid-output,
   alignment, state, memory or timing record exists.
6. **No opt-in intake.** No provider, descriptor, default selection, ABI,
   shared build, CI, board or handoff change is made.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from adjacent LaCo-SENet, ConvFSENet, GTCRN, FastEnhancer,
DeepFilterNet3, DTLN or other survey evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The official `yxlu-0102/MP-SENet` source at an immutable 40-hex commit with reviewed MIT license text, notice, per-file SHA-256 and a map from model, inference script and configuration to source files. |
| `BLK-02` | The exact pretrained VoiceBank+DEMAND checkpoint with file name, immutable revision, byte count, SHA-256, tensor schema, inference-script identity and checkpoint-specific terms. |
| `BLK-03` | A locked offline runtime with exact interpreter, PyTorch/package versions, wheel hashes, CPU/MPS device, determinism settings and a recorded supported platform. |
| `BLK-04` | Reviewed source, checkpoint and VoiceBank+DEMAND training-data terms; corpus and clean-reference permission; output use, redistribution and attribution. |
| `BLK-05` | The frozen offline whole-utterance contract: sample rate, channels, FFT/STFT window and hop, magnitude and phase branch layout, padding, output length, normalization, no streaming lookahead and fresh state per call. |
| `BLK-06` | A rights-cleared 16 kHz mono cohort with paired clean references where permitted, quiet/active and idle-noise strata, onset/offset cases, held-out splits, controls, baseline and independent results. |

**Reopen condition.** A caller supplies the exact source and reviewed MIT
license, the exact checkpoint with verified identity and checkpoint terms, an
isolated hash-pinned runtime on a recorded platform, the frozen offline
phase-aware geometry, a rights-cleared 16 kHz matched cohort, a deterministic
reproduced Enhancement result set with separate quality and timing evidence,
and an opt-in OFF-by-default provider intake with independent exact-head
review. Until then this task stays `DEFER`.

## Recorded upstream identity

None of the following is a local asset. No byte is present, opened, hashed or
executed here, so every identity field remains null and cannot qualify the
candidate.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/yxlu-0102/MP-SENet` | absent |
| Source license | MIT, as reported by the census | not locally verified |
| Source commit | not recorded | absent |
| Model repository | `https://github.com/yxlu-0102/MP-SENet` | absent |
| Model revision | not recorded | absent |
| Checkpoint file | not recorded | absent |
| Checkpoint bytes | not recorded | absent |
| Checkpoint SHA-256 | not recorded | absent |
| Inference script | described as provided | absent |
| Tensor schema | not recorded | absent |
| Reported metric | PESQ 3.50 on VoiceBank+DEMAND | source-reported, not measured here |
| Paper | `https://www.isca-archive.org/interspeech_2023/lu23e_interspeech.html` | not read locally |

These values are retained only to make the future exact-asset check
unambiguous. They are **not** local measurements and must not be compared with
the project DNS2020 results.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Single-channel speech enhancement / noise suppression | No execution |
| Domain | VoiceBank+DEMAND, 16 kHz | no local cohort |
| Channels | 1 | no local audio |
| Approach | Parallel magnitude and phase spectrum estimation | lead only |
| Mode | Offline whole-utterance, non-streaming | no inference contract |
| FFT/STFT window, hop, padding | not recorded | unverified |
| Magnitude/phase branch layout | not recorded | unverified |
| Output length and normalization | not recorded | unverified |
| Streaming lookahead | not applicable / none claimed | unverified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | preserved; no MP-SENet mapping |

The public v0 mono path is rate- and channel-compatible with the reported
domain, but no descriptor, provider, registry, default, ABI, shared build or CI
mapping is added. Rate and channel compatibility is not an adapter.

## What this package verifies

1. **Absence evidence.** 24 fixed workspace, SDK-worktree and home-cache probes
   are checked without a recursive walk. All are absent. The report builder and
   verifier fail if any later appears, so a stale absence claim cannot ship.
2. **No invented identity.** The checkpoint file, bytes, SHA-256 and model
   revision are `null`. Only the source-reported PESQ 3.50 is retained, marked
   `source_reported_not_measured_here`, `admitted_as_result=false` and
   `qualifies=false`.
3. **Asset-register absence.** The pinned asset register is parsed strictly:
   20 candidate ids, none for MP-SENet. No checkpoint identity is inferred.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, checkpoint, inference-script, runtime, 16 kHz mono
   offline geometry, input, control and rights fields. Unknown or missing
   fields, duplicate JSON keys, nonfinite values, floats, unsafe paths, an
   unresolved source license, wrong interpreter, stereo or non-16 kHz
   geometry, streaming mode, non-zero lookahead, a missing explicit phase
   branch, a non-whole-utterance declaration, missing state reset, rate
   mismatch, unconsented input, false controls and false rights are rejected.
   One synthetic schema control is accepted to prove the validator is not
   blanket-rejecting; it is marked `synthetic_schema_control`,
   `qualifies=false` and is not evidence.
7. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/mp-senet/` as `base_out_of_scope_change`. Three
   regression tests cover sibling merges, an out-of-scope branch edit and a
   missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control or baseline output on exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared 16 kHz paired cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labeled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and content/availability timing | blocked | No runtime, state, chunk timing or content-delay record. |
| Offline phase-aware geometry and magnitude/phase contract | blocked | No FFT/STFT window, hop, branch layout, padding or output-length contract. |
| Quiet/active, idle-noise and onset/offset strata | blocked | No corpus or stratum definition. |
| Separation of paired, unpaired, synthetic, human and source-reported evidence | documented | Upstream VoiceBank PESQ 3.50 is labelled source-reported; no result of any class is promoted. |

## Matched-evidence boundary

`fastenhancer-small-reference`, `laco-senet`, `gtcrn-streaming-onnx` and
`convfsenet` are separate components with their own assets, geometry and
blockers. Their fixtures, checkpoints, scores, timings, state models and rights
records are not inherited. The 30-pair DNS2020 results for other candidates are
same-task-context comparators only; they are not MP-SENet measurements and the
upstream VoiceBank figure is not comparable to them.

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
| `source:reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/candidate_accounting.csv` | `3ab7b404129737666c1e74c7e9a7107f45c8c0575018d2591bef75d3782473c5` |
| `source:reports/95d98095b79471cf92fdaf736d7296a14811147499fe76ed4076de5c39b8e30d/manifest.json` | `6c745b13486b92ec7f1e4db868f3109ce246cac6c944968d22bfd9cb01ae397f` |
| `source:research/evidence/pilot-discovery-20261027/source.txt` | `3591d17581fb9c9168f10d3816f42a9c6178d6168ea386de6eafc6280c18c590` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/pilot_evaluation_progress.md` | `7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf` |
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
| `LICENSES.md` | `9659b5d8043460e342cbfce707b12f7c0583262dd7b18b972b36e8c26cf5e785` | 2040 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `ae7e08aba2f69befab992d823fd161e11f0a0b0ffc9846ae5d81b90fb6405a16` | 26541 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `9031761508bca0ec48b2789f707776f1d5f766b46bf779f48cd5f7fcfc475304` | 92052 |
| `report.json` | `989c64c1c069e55d9b871f308a607669507d605247f85f614f13132efa2b010f` | 48290 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `5d22feb9665ed7b5eebe30e70f325cac0d770d7a1e75451f8ab142b37d0852a8` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `7e427eb8e55d9f757dca39ac24ad942d9eb728061bcd2a2e3ccccbf255e61e70` | 4895 |
| `test_reference.py` | `34a514502d0706977d840af636e586bf454e7e81298530d5deb663ec3ab4882c` | 32135 |
| `verify.py` | `36fd679dc50cb2f241cddbeb7aa637d0bf2d5d06e38c5657d8b4f14d704d04fd` | 28271 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pth`, `.pt`, `.th`, `.onnx`, `.safetensors`, binary library, compiled
object, upstream source copy, license text copy or model weight.
