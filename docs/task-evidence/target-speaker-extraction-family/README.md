<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-TARGET-SPEAKER-EXTRACTION-FAMILY — blocker evidence package

Task-local, **proposal-only**, **incomplete**, **not qualified** evidence for
`target-speaker-extraction-family` (`SDK-TARGET-SPEAKER-EXTRACTION-FAMILY`).
Acceptance profile: **Spatial** (from `plan/INVENTORY.json` / `plan/swarm/VERIFICATION.md`).
Decision: **DEFER** before `source_checkpoint_runtime_rights_and_evidence_admission`;
`evidence_status=incomplete`, `qualification.status=not_qualified`. No missing,
blocked, rejected, or surrogate result qualifies the candidate.

## Exact blocker

Pinned research records identify this as a family-level blocked row: no selected
extraction model, no exact licensed source revision, no checkpoint/weights/runtime
identity, no enrollment/reference-cue protocol, and no rights-cleared enrolled
overlap corpus with clean target references and target-absent negatives. No
source, checkpoint, runtime, corpus, or enrollment cue is present, downloaded,
copied, imported, loaded, or executed by this package.

## Scope and boundary

- Task-local only: `docs/task-evidence/target-speaker-extraction-family/`.
- No provider registration, no descriptor/registry/default change, no installed
  v0/ABI/public API/shared build/dependency lock/CI change.
- No real corpus, weights, runtime, listening, device timing, benchmark, or
  release claim unless supplied and independently qualified.
- Installed v0 remains 16 kHz mono `float32`, 160 samples/frame.

## Deterministic surrogate (not qualification)

`reference.py` builds a frozen synthetic 3-channel 16 kHz / 256-sample probe
fixture with target, overlap, masker-only, and tail strata. It runs a fixed
model-free boundary surrogate to exercise multichannel validation, declared
delay, partial tail, reset, streaming parity, silence, finite bounds, and
fail-closed adverse/missing/invalid/nonfinite rejection. The surrogate is **not**
a target-speaker extractor, has no enrollment/model/runtime, and cannot qualify
the candidate.

## Spatial profile mapping

| Required case | Status |
| --- | --- |
| Frozen geometry/layout/timestamp/reference conditions | Blocked for real candidate; probe-only synthetic 3ch/16k/256 geometry declared |
| Source/target/reference conditions and permissions | Blocked; no rights-cleared enrolled corpus/cues |
| Localization/activity/extraction held-out labels | Blocked; no real candidate output or labels |
| Leakage, target damage, channel loss, room/reference changes | Blocked for real candidate; surrogate controls only |
| Exact source intervals, availability, dropped/stale events | Blocked for real candidate; deterministic surrogate state checks only |

## Release gates (all blocked)

| Gate | Status | Qualifies |
| --- | --- | --- |
| exact_source_checkpoint_and_license | blocked | false |
| rights_cleared_enrolled_corpus | blocked | false |
| cue_protocol_and_geometry | blocked | false |
| exact_runtime_and_determinism | blocked | false |
| target_preservation_and_leakage_scoring | blocked | false |
| adverse_missing_invalid_nonfinite_controls | blocked | false |
| target_runtime_timing_and_memory | blocked | false |
| opt_in_provider_intake_and_release | blocked | false |

## Reproduction

```sh
cd docs/task-evidence/target-speaker-extraction-family
PYTHONDONTWRITEBYTECODE=1 python3 reference.py  # no CLI; module only
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` builds the report three times and requires byte-identical canonical JSON
before writing artifacts. It never hashes mutable full `plan/swarm/TASKS.json`;
only the stable linked-row identity digest is gated.

## Source pins

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: boundary-end -->

## Artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `contract.json` | `3e54da2487c649383ec3dde85d1910b0bae210f8c5f8810e1d78c3e90a5283e8` | 12477 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `94f8b9336ae585eb1522d0752dcf6a94c3645db3f2a7d2a804656c4fa560dcfd` | 64079 |
| `report.json` | `3f03067844d0afc10d0913ad7b570673f80f474d660f1ea4e02f0d39ba9822be` | 22265 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `d9fa673789ab7c6bd870a75132a3f4cc6ef8f749515c16c4bf4a5e7b88186309` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `f9cead02e3441f82cd949851597f47271d0b1c214780e4dfc0361952c351a538` | 1439 |
| `test_reference.py` | `39425879b926792bd093bf68a8425e9eef6edc2b71fe533f6876f408c25ce270` | 4998 |
| `verify.py` | `5b26e4fcee38b30340552955b6b1cdee48bcc0d3e438a9014fad20ffd9db8268` | 13894 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
