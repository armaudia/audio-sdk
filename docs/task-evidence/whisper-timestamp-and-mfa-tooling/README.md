<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Whisper-timestamp and MFA tooling — task evidence (DEFER)

**Task:** `SDK-WHISPER-TIMESTAMP-AND-MFA-TOOLING`  
**Component:** `whisper-timestamp-and-mfa-tooling`  
**Mode:** `research-control`  
**Profile:** `evidence`  
**Decision:** `DEFER`  
**Status:** `proposal_only_incomplete` / `not_qualified`

## What this package is

A deterministic, task-local, stdlib-only blocker/evidence package for the
Whisper-timestamp + MFA comparison tooling row. It pins historical provenance
artifacts by SHA-256, records exact absence of weights/runtimes/corpora,
validates a fail-closed manifest schema with adverse controls, and emits
canonical `contract.json` / `report.json` + SHA-256 sidecar.

## What this package is not

- No Whisper, MFA, PyTorch, ffmpeg runtime, model weight, acoustic model,
  dictionary, AMI audio, transcript, or TextGrid downloaded/imported/executed.
- No ASR/WER/boundary/rate result reproduced or qualified.
- No provider/adapter registered or enabled by default.
- No public ABI/CONTRACTS/registry/shared build/CI/default behavior change.
- No listening, device timing, benchmark, or release claim.

## Exact blockers

| ID | Gate | Status | Required action |
|---|---|---:|---|
| BLK-01 | RG-01 | open | Stage exact Whisper tiny.en weight/package/license and MFA 3.4.3 acoustic/dictionary/source/license artifacts with immutable digests/byte counts and reviewed terms. |
| BLK-02 | RG-02 | open | Provide locked offline Whisper+MFA runtimes, deterministic settings, install/import digests, and clean-room reproduction logs. |
| BLK-03 | RG-03 | open | Pin exact cohort/audio/annotations/language/transcript normalization/aligned subset and review AMI/Whisper/MFA terms. |
| BLK-04 | RG-04 | open | Produce fresh frozen WER/boundary/rate scoring with matched aligned subset, finite/nonfinite checks, and negative controls. |
| BLK-05 | RG-05 | open | Keep tooling adapter OFF/unregistered until gates clear; then separate opt-in intake with independent exact-head review. |

## Release gates (all blocked)

| Gate | Status | Detail |
|---|---:|---|
| RG-01 exact_source_runtime_asset_identity | blocked | Exact source revisions, packages, model/acoustic/dictionary assets, hashes, byte counts, and complete license/notice bundles absent/unverified. |
| RG-02 pinned_offline_runtime_and_reproduction | blocked | Pinned offline environments, lockfiles/install/import digests, deterministic settings, clean-room reproduction absent. |
| RG-03 rights_terms_and_cohort | blocked | Cohort/annotations/language/normalization/subset pins and rights review not staged. |
| RG-04 scoring_controls_and_validity | blocked | No fresh WER/boundary/rate scoring with frozen normalizer, matched aligned subset, finite/nonfinite checks, controls. |
| RG-05 tool_boundary_and_release | blocked | No reviewed opt-in developer/evidence adapter boundary; default/shared build/CI/registry untouched. |

## Historical provenance (not evidence)

Pinned report records one 15s AMI crop smoke run (Whisper tiny.en CPU, MFA 3.4.3):
WER 11.76% (4/34), oracle boundary MAE 23.79ms, ASR boundary MAE 23.17ms.
This is provenance only: not reproduced here, not independent timing gold, not
device/runtime/release evidence, and not qualifying.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 -m unittest -q test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 verify.py
```

## Pinned digest table

| File | SHA-256 |
|---|---|
| `contract.json` | `646c33fd50784142ea929d7ed5520ffee3d266e3f67830eec2b8b702bdc9b8b2` |
| `report.json` | `4aba6633c7cd44f13ac7a1890ee01e717f4bc820e74fc8a035edd2d8500aae2a` |
