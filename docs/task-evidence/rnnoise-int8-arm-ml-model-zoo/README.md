<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO — INT8 RNNoise readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for the RNNoise INT8
(Arm ML Model Zoo) row (mode `feasibility`, verification profile `enhancement`).
It is **not** an implementation, adapter, provider, runtime, model or
reproduction. No Arm or Renesas source checkout, INT8 model byte, feature
extractor, gain applier, corpus, recording, enhanced waveform, listening
result, device timing, benchmark or release claim is present. **No result here
qualifies this candidate.**

Pinned base: `80dc1fb371e1846a5d50f5b28c955ab92bfcbe46`.
Branch: `swarm/SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO`.
Owner: `agent-RNNOISE-INT8-ARM-ML-MODEL-ZOO`.
Reviewer: `reviewer-RNNOISE-INT8-ARM-ML-MODEL-ZOO`.

## Exact external blocker

`research/noise_suppression_candidate_census.md`, line 53, records one row:

> Quantized recurrent denoiser with Opus-style features; Cortex-M/NPU
> deployment variant. Arm documentation describes a TFLite quantized RNNoise
> taking hand-crafted features and outputting band gains; the Renesas reference
> implementation publishes CPU/NPU C exports and reports Edinburgh Noisy Speech
> PESQ, with weights attributed to Apache-2.0 Arm ML Zoo. Embedded deployment
> comparator only; different 48 kHz feature/quantization path from the already
> tested float RNNoise. Pin the original model, verify exact upstream hash and
> terms, and measure on matching MCU/NPU hardware.

The pinned inventory row records `considered`, `sdk-model`, area `Enhancement`
and profile `enhancement`. It is scope evidence only. The pinned asset register
contains a separate `RNNoise-Xiph-default` float entry and no Arm INT8 or
Renesas quantized candidate file, byte count, digest or terms. The census gives
no numeric PESQ value in this workspace; the PESQ mention is a source lead and
is not a local measurement.

The exact blocker is therefore the combination of:

1. **No runnable source identity or reviewed terms.** No Renesas/Arm source
   snapshot, immutable 40-hex commit, license text, notice, per-file SHA-256 or
   component map is staged. A weight attribution is not a source grant for a
   specific commit or exported C/TFLite code.
2. **No exact INT8 model identity.** No quantized model filename, revision,
   byte count, SHA-256, tensor schema, quantization scale/zero-point, feature
   dimensions, band-gain count or checkpoint-specific terms is recorded.
3. **No offline target runtime.** No TFLite Micro/C export, compiler/toolchain
   lock, target image, determinism setting or offline load path exists.
4. **No frozen feature/gain geometry or SDK bridge.** The 48 kHz hand-crafted
   feature path and band-gain output are named, but no frame/hop, state, delay,
   padding or `f32/16000/mono/160` mapping is frozen.
5. **No rights-cleared paired cohort or matched Enhancement result.** No
   consent, clean reference, control, baseline, paired score, preservation,
   peak, invalid-output, alignment, listening, memory or MCU/NPU timing record
   exists.
6. **No opt-in intake.** No provider, descriptor, registry, default, ABI,
   shared build, CI, board or handoff change is made.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from the installed float RNNoise v0.2 path, the RNNoise
speech-probability path, the Xiph asset-register entry or any other candidate.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The Renesas RNNoise reference implementation and referenced Arm materials at an immutable 40-hex commit with reviewed license text, notice, per-file SHA-256 and a map from feature extraction, model export and build scripts to source files. |
| `BLK-02` | The exact INT8 RNNoise model file at immutable identity with filename, byte count, SHA-256, tensor schema, quantization scale/zero-point, feature dimensions, band-gain count and checkpoint-specific terms. |
| `BLK-03` | A locked offline TFLite Micro/C export runtime with exact compiler/toolchain versions, wheel or source digests, target platform, determinism settings and no download step. |
| `BLK-04` | Reviewed source, model, training-data and corpus terms, clean-reference permission, output use, redistribution and attribution for the exact revision. |
| `BLK-05` | Frozen feature/gain contract: 48 kHz mono input, frame/hop, INT8 tensor layout, band gains, padding, recurrent state, delay and an exact `f32/16000/mono/160` SDK bridge or explicit no-bridge finding. |
| `BLK-06` | A frozen rights-cleared paired cohort, Enhancement results and matching Cortex-M/NPU memory, deadline and content/availability timing. |

**Reopen condition.** A caller supplies the exact source revision and reviewed
terms, the exact INT8 model bytes and digest, an offline target-runtime lock,
the frozen 48 kHz feature/band-gain geometry and `f32/16000/mono/160` SDK
bridge, a rights-cleared matched cohort, independent Enhancement evidence with
target-hardware timing/memory, and opt-in OFF-by-default intake with exact-head
review. Every gate must clear before this task reopens.

## Recorded upstream identity

None of the following is a local asset. No byte is present, opened, hashed or
executed here, so every identity field remains null and cannot qualify the
candidate.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/renesas/ruhmi-model-zoo/tree/main/audio/noise_suppression/rnnoise` | absent |
| Source license | Apache-2.0 attribution for Arm ML Zoo weights, as reported by the census | not locally verified |
| Source commit | not recorded | absent |
| Model repository | `https://github.com/renesas/ruhmi-model-zoo/tree/main/audio/noise_suppression/rnnoise` | absent |
| Model revision | not recorded | absent |
| INT8 model file | not recorded | absent |
| Model bytes / SHA-256 | not recorded | absent |
| Quantization parameters | not recorded | absent |
| Reported approach | INT8 recurrent denoiser; hand-crafted features; band-gain output | lead only |
| Reported metric | Edinburgh Noisy Speech PESQ, no numeric value in this workspace | source-reported, not measured here |
| Arm guide | `https://documentation-service.arm.com/static/6821edae8f79851ff2c3e485?token=` | not read locally |

These values make a future exact-asset check unambiguous. They are **not**
local measurements and must not be compared with installed float RNNoise
results.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Single-channel noise suppression | no execution |
| Domain | Cortex-M/NPU embedded deployment, hand-crafted feature path | no local target |
| Channels | 1 | no local audio |
| Feature sample rate | 48 kHz (reported path) | no feature script |
| Weight precision | INT8 | no model bytes |
| Output | Band gains | no inference |
| Frame/hop, feature dimensions, quantization scale/zero-point | not recorded | unverified |
| Recurrent state, padding, delay | not recorded | unverified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | preserved; no INT8 mapping |

The public v0 geometry is unchanged. Mono compatibility is not an adapter; no
descriptor, provider, registry, default, ABI, shared build or CI mapping is
added.

## What this package verifies

1. **Absence evidence.** 21 fixed workspace, SDK-worktree and home-cache probes
   are checked without a recursive walk. All are absent. The report builder and
   verifier fail if any later appears.
2. **No invented identity.** The model file, bytes, SHA-256, revision, feature
   geometry and quantization parameters remain `null`. The PESQ lead is
   labelled `source_reported_lead_not_measured_here`,
   `admitted_as_result=false` and `qualifies=false`.
3. **Asset-register absence.** The pinned register is parsed strictly; its
   separate float RNNoise entry is not admitted for this INT8 task.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed.
6. **Fail-closed caller-asset validation.** A synthetic manifest schema checks
   exact source, checkpoint, runtime, 48 kHz hand-crafted feature/INT8
   band-gain geometry, `f32/16000/mono/160` SDK bridge, input, controls and
   rights. No field is resolved, loaded or executed; the sole accepted control
   qualifies nothing.
7. **Enhancement profile accounting.** Eight requirement rows are recorded as
   blocked or documented; no missing result is promoted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/rnnoise-int8-arm-ml-model-zoo/` as
   `base_out_of_scope_change`. Three regression tests cover newer sibling
   merges, an out-of-scope branch edit and a missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control or baseline output on the exact INT8 asset. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared paired cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or band-gain validity record. |
| Separately labeled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and content/availability timing | blocked | No target runtime, recurrence state, memory or timing record. |
| Exact feature/gain geometry and SDK bridge | blocked | No frame/hop, tensor schema, scale/zero-point, band count, delay or bridge contract. |
| Matching Cortex-M/NPU hardware and cohort strata | blocked | No device, toolchain, deadline, memory or stratum definition. |
| Separation of paired, unpaired, synthetic, human and source-reported evidence | documented | The Renesas PESQ lead is labelled source-reported; no result of any class is promoted. |

## Matched-evidence boundary

`rnnoise-v0-2`, `rnnoise-speech-probability` and `RNNoise-Xiph-default` are
separate paths with their own assets, geometry and blockers. Their checkpoints,
scores, timings, state models and rights records are not inherited. The float
RNNoise adapter and its DNS pilot numbers are not INT8 Arm ML Zoo measurements.

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
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
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
| `LICENSES.md` | `abc62103ee1e394852d23f78326f1f38ff9ae2b449b04a92c8796398c6328717` | 2030 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `888d0b05a88d5c9ad46e612f791a8b06a5018998bead9a98c5cd33cbda5ce321` | 33583 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `d16a03ba47dc8d1fdd53a81169adeb3280c0a51faf2ad39c57de235484e42c35` | 94862 |
| `report.json` | `60ca4ce9f0235a1d1e8265d7ee0bb9bd93335264146859a042486625d4d05052` | 54152 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `890c5f896190758f773dc090c7ae21aab20a18e069d8d20149db7d221a78d04d` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `70cdc57e7f20da0a4182b098ca368f47d744924a0f2bb882104efc55801f289b` | 4952 |
| `test_reference.py` | `541ae83b0ff9cfd4a62b509198fa6f03c4d60d3fe254297dddc15c8eb27f7eaa` | 33838 |
| `verify.py` | `67eb6afa418b377a519ec9dd6fcada6bdf5b04a9dbb0df039a6faeb232b2891d` | 28583 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pth`, `.pt`, `.th`, `.onnx`, `.tflite`, `.safetensors`, binary library,
compiled object, upstream source copy, license text copy or model weight.
