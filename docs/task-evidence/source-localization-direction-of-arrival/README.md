<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL — source localization / DOA evidence

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **Spatial-profile feasibility and readiness conclusion**
for inventory component `source-localization-direction-of-arrival`
(`sdk-reference`, `considered`). It records the source lead (`S26`), the exact
calibration/label/exposure requirements, a metadata-only caller-supplied-asset
boundary and model-free synthetic array geometry. It creates **no new
implementation, provider, processor, ABI, default, descriptor, registry,
shared-build, CI, board, handoff, benchmark or release change**. Missing or
blocked evidence never qualifies the candidate.

Task: `SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL` · branch `swarm/SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL` · base `022a7ad3cedf35aba70ef93b32b71ae51e1e30ca` · profile
`Spatial` · decision `DEFER` before `opt_in_adapter_exposure`. Installed v0
remains unchanged: 16 kHz, mono, `f32`, 160-sample frames. The synthetic array
below is reference-only and is not an installed v0 format.

## Exact readiness conclusion

The only named source is **S26**, a Pyroomacoustics DOA documentation **search
excerpt**. No package revision, source archive, runtime lockfile or offline
loader is staged. No rights-cleared calibrated array recording, held-out
angular/track labels, timestamp drift measurement, contact permission or
advertised angle/confidence mode is staged. Adjacent packages
(`survey-cln-08`, `hush`, `3d-microphone-spatial-time-alignment`,
`offline-multichannel-wpe`) and the catalogued SRP-PHAT / MUSIC / NormMUSIC
families are **excluded** from DOA evidence. Four exact blockers and eight
blocked gates are machine-readable in `report.json` and `contract.json`.

1. **XB-01 — `no_runnable_local_doa_source_or_runtime`.** Reopen: stage the
   exact licensed source/package revision and locked offline runtime with byte
   counts and SHA-256 values, then reproduce it.
2. **XB-02 — `calibrated_array_geometry_and_clock_absent`.** Reopen: provide
   immutable measured geometry and timestamp calibration for a rights-cleared
   array recording.
3. **XB-03 — `permitted_task_matched_spatial_labels_absent`.** Reopen: stage a
   permitted, calibrated corpus with frozen conditions and held-out
   angular/track labels.
4. **XB-04 — `angle_confidence_controls_and_release_gates_unmet`.** Reopen:
   complete the Spatial profile on the exact runtime and pass independent
   opt-in review with the default OFF.

`RG-01` through `RG-08` are all `blocked` with `qualifies=false`: source/runtime
identity, geometry/calibration, caller boundary/modes, permitted conditions,
held-out separated outcomes, leakage/channel-loss/condition shift, failure
controls/abstention, and opt-in intake/release.

## Boundary and caller-supplied-asset model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  No header, descriptor, registry, default, shared CMake, CI or installed
  behavior changes.
- The task-local caller contract requires exactly 23 metadata fields: adapter,
  configuration, S26 URL/revision, package revision, runtime digest, ULA
  geometry fields, angle/grid settings, ambiguity mode, confidence threshold,
  calibration digest, drift, label-manifest path/digest, permissions, room
  condition and a caller asset with path/digest/size/revision.
- A manifest is validated as **metadata only**. It must be structurally exact,
  use the pinned geometry, reject forced ambiguity, verify an absolute asset's
  SHA-256 and byte count, and still fails as `DOA_SOURCE_REVISION_UNPINNED`.
  No asset is loaded, imported, converted or executed.
- The synthetic 4-mic, 0.05 m broadside ULA at 16 kHz with 343 m/s uses integer
  TDOA arithmetic only. The 30° and 150° mirror angles yield the identical
  integer delay tuple `(0, 1, 2, 3)`; the mirror control is an abstention
  prompt, **not** a pass. Single-channel angles are not identifiable, zero
  information abstains, and confidence is uncalibrated. No signal, transform,
  beamformer or angle search runs.

## Spatial profile application

Geometry/layout, timestamp calibration, source/target/reference conditions and
permissions are recorded in `report.json:spatial_profile`. Localization,
activity and extraction are tracked as separate blocked outcomes with
task-matched held-out labels required. Leakage, target damage, channel loss and
room/reference-condition changes are explicit reopen requirements. The
`Spatial` acceptance gate is `false`; the integer TDOA control is not an angle
or confidence result. No listening, device timing or benchmark claim is made.

## Source and boundary pins

Pinned documents are read-only identities. `source:` keys are workspace
relative; boundary keys are SDK-worktree relative. The mutable
`plan/swarm/TASKS.json` is never pinned as a whole; only the stable six-field
task-row identity (SHA-256 `359d422c87f32d0b69b14dab79c077bc73fc0219b3e87fee3c150ad98174b14d`) is gated.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/swarm/handoffs/SDK-SURVEY-CLN-08.md` | `e009dd94a26cbc3dca5bef8183fa4b0a55415449a2b4aab218189fab80ab2836` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/search_log.jsonl` | `61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Pin key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/3d-microphone-spatial-time-alignment/README.md` | `514636b719e6579651bf941a6ac3cb93740cc9a40e3f2b4bcd39c2ddea610264` |
| `docs/task-evidence/3d-microphone-spatial-time-alignment/report.json` | `5d3623c835a1b19d79867a64ba1b6dff18e8593918a8173cff91550c1c532f03` |
| `docs/task-evidence/hush/README.md` | `0426a592204381138e7fa7ba04f37f4aff92eee6ac75b6bda31f0861c485e76f` |
| `docs/task-evidence/hush/report.json` | `deaa6ff7bf89bb2727619e69cd41ce40b481ae7db93d25a007cb04b3a218cac4` |
| `docs/task-evidence/offline-multichannel-wpe/README.md` | `8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9` |
| `docs/task-evidence/offline-multichannel-wpe/report.json` | `4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba` |
| `docs/task-evidence/survey-cln-08/README.md` | `33730b2bc2a34b05bb7392d8877c498a1b9112a2d41b9e83d31fa6853f8850e7` |
| `docs/task-evidence/survey-cln-08/SOURCES.sha256` | `94c38bc39aacaa7f64b81fe02172e2ba167ac90b019974f6d581e39a1462c7a0` |
| `docs/task-evidence/survey-cln-08/report.json` | `5d88cea01296895fd275d867cc80a67590187a9255125bbf947a38197cf89fbe` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifacts and canonical form

`report.json` is the canonical machine-readable conclusion; `contract.json`
is the strict acceptance contract; `SOURCES.sha256` pins all source/boundary
documents and local artifacts; `report.json.sha256` is the report digest
sidecar. JSON is canonical: sorted keys, compact separators, `allow_nan=False`,
one trailing LF. `verify.py` re-derives every artifact byte-for-byte and fails
closed on stale pins, duplicate-key/nonfinite JSON, README digest drift,
license gaps, non-task-local branch scope, whitespace damage and dirty diff.

## Reproduce

From the SDK worktree root, with pinned Python 3.12.16 and no bytecode writes:

```sh
export PYTHONDONTWRITEBYTECODE=1
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12
cd docs/task-evidence/source-localization-direction-of-arrival
$PY -m unittest -v test_reference.py
$PY run.py --all
$PY run.py --check
$PY verify.py
```

From the SDK root also run the installed-package CI, licensing and whitespace
checks:

```sh
$PY scripts/ci.py --output build/ci
python3 -m reuse lint
git diff --check
```

No network access, download, real audio, listening test, device-clock
measurement, benchmark or release action is part of reproduction.

## Licensing

All files are authored for this repository under Apache-2.0 with
`SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes`. JSON and manifest files
carry `.license` sidecars; Python and Markdown files carry SPDX headers. No
third-party code, model, audio, corpus or asset is vendored, copied or modified.
The REUSE configuration covers `docs/**`; no licensing annotation is changed.
