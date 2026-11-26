<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TFLITE-LITERT — TFLite / LiteRT blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for `SDK-TFLITE-LITERT` under
`docs/task-evidence/tflite-litert/` only. No provider registration, no SDK
public API/ABI/default/descriptor/registry/shared build/CI change, no
TFLite/LiteRT source/runtime/delegate/model/weights download, no real corpus,
no device timing, no listening, no benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

This task is a feasibility/tooling intake. No exact pinned TFLite/LiteRT
runtime/source revision, immutable delegate/build provenance, reviewed
license/redistribution terms, exact model/task geometry, rights-cleared matched
inputs, or deterministic/target-device execution evidence is present in this
worktree. Generic runtime presence is not a qualified task result.

## Pinned Inputs

- Linked task row identity (stable fields only, no mutable board hash):
  `SDK-TFLITE-LITERT` in `audio-benchmark-platform/plan/swarm/TASKS.json`.
- Dependency rows: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
- `research/noise_suppression_candidate_census.md`
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Tool profile)
- `audio-benchmark-platform/plan/audio-sdk/README.md`
- `audio-benchmark-platform/plan/INVENTORY.json`
- SDK boundary pins: `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`,
  `api/include/audio_sdk/session_v0.h`, `docs/provider-intake.md`

## Required Artifacts

| File | Purpose |
|---|---|
| `README.md` | Scope, decision, pins, gates, reproduction. |
| `contract.json` | Machine-readable contract and blocker/gate record. |
| `reference.py` | Stdlib-only deterministic model and strict JSON helpers. |
| `report.json` | Canonical blocker report. |
| `report.json.sha256` | SHA-256 of canonical `report.json` bytes. |
| `SOURCES.sha256` | SHA-256 manifest for task-local files and pinned inputs. |
| `verify.py` | Read-only verifier; fail-closed checks. |
| `test_reference.py` | Deterministic unit tests. |
| `run.py` | 3x byte-identical regeneration of canonical artifacts. |
| `*.license` | REUSE sidecars for generated/text files. |

## Release Gates (all blocked)

| Gate | Status | Reopen condition |
|---|---|---|
| RG-01 | blocked | Exact TFLite/LiteRT source/runtime revision and immutable build/delegate provenance. |
| RG-02 | blocked | Reviewed license, attribution, redistribution, patent/export, and model/runtime terms. |
| RG-03 | blocked | Exact model/weights/delegate geometry, format, reset/drain semantics, immutable asset digests. |
| RG-04 | blocked | Versioned optional adapter/tool boundary preserving installed v0 behavior. |
| RG-05 | blocked | Deterministic signature smoke and adverse/missing/invalid/nonfinite rejection on pinned assets. |
| RG-06 | blocked | Rights-cleared matched inputs and reference-backend parity/full-checkpoint evidence. |
| RG-07 | blocked | Paced target-device/runtime CPU, memory, deadline, availability, delegate measurements. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Non-Claims

- No TFLite/LiteRT source/runtime/delegate/model/weights executed or bundled.
- No real audio/corpus/device/listening/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No sibling TFLite/LiteRT evidence inherited.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/tflite-litert/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/tflite-litert/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/tflite-litert/verify.py
```
