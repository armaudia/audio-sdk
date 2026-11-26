<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SPATIALNET — SpatialNet feasibility evidence (DEFER)

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility evidence for `SpatialNet` (`component_id=spatialnet`). The assigned acceptance profile is **Spatial**. Machine-readable decision: **DEFER**; `status=proposal_only_asset_intake_incomplete_not_qualified`; `evidence_status=incomplete`; `qualification_status=not_qualified`. No result in this package qualifies the candidate.

This package does **not** import, load, link, execute, copy, vendor or download SpatialNet source, weights, runtime, adapter, or any synchronized multichannel corpus. It does not read, write, render or play real audio; does not measure device timing, callback deadlines, pacing or synchronization; does not benchmark the SDK; and makes no release claim. Synthetic geometry/control outputs are deterministic controls only and never qualify SpatialNet.

## Boundary

Installed v0 geometry is unchanged and documented only: `16000 Hz`, 1 channel, `float32`, 160 samples per call. No provider, default, descriptor, registry entry, ABI, CONTRACTS, shared-build or CI file is changed. The adapter/provider remains OFF, unregistered and not exposed. Board, handoff, reviewer dispatch and release state are untouched. Only `docs/task-evidence/spatialnet/` is written.

## Decision, gates and blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact runnable source; exact assets and rights; synchronized multichannel corpus; installed-v0 boundary intake; task-matched evidence; Spatial-profile evidence; device timing/pacing; and public admission review. `DEFER` is before `opt_in_adapter_exposure`. Exact blockers B-01 through B-04 and reopening conditions are in `report.json` and `contract.json`.

Source-reported evidence is provenance only and kept separate: the candidate matrix and spatial follow-up reports mark SpatialNet unavailable/blocked due to missing local weights/adapter and no synchronized multichannel clean-target corpus; mono evidence cannot score array enhancement. WPE multichannel evidence is a different DSP task and is not pooled.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied as blocked: geometry/layout, timestamp calibration, source/target/reference conditions and permissions, task-matched held-out localization/activity/extraction labels, leakage/target-damage/channel-loss, and room/reference changes all lack required real evidence. The deterministic synthetic geometry delay-alignment control verifies only integer arithmetic and is explicitly `qualifies=false`.

## Reproduction

```text
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`run.py` performs three cold-start rounds and refuses to accept non-identical report, contract or source bytes. `verify.py` is read-only and fails closed on duplicate-key/nonfinite JSON, stale pins, stale canonical artifacts, stale README digest tables, unexpected files, license gaps, whitespace damage, unavailable scope base, out-of-scope changes and a dirty diff check. The board link pins only stable row identity, never the mutable full `plan/swarm/TASKS.json`.

Base commit: `4c0f5464eeddff2204b527e8bc4ad09c41b2a657`.
Task ID: `SDK-SPATIALNET`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
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
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->
