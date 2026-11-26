<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TF-GRIDNET-URGENT-2025-BASELINE — TF-GridNet URGENT 2025 blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for
`SDK-TF-GRIDNET-URGENT-2025-BASELINE` under
`docs/task-evidence/tf-gridnet-urgent-2025-baseline/` only. No provider
registration, no SDK public API/ABI/default/descriptor/registry/shared
build/CI change, no TF-GridNet/ESPnet/URGENT source/checkpoint/runtime
download, no real corpus, no device timing, no listening, no benchmark, and no
release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

Pinned research identifies TF-GridNet URGENT 2025 baseline as a robustness-phase
candidate deferred due large dependency/inference cost and distinct test
distribution. No exact licensed source/checkpoint/runtime, reviewed rights,
deterministic execution, matched corpus, or target-device timing evidence is
present in this worktree.

## Pinned Inputs

- Linked task row identity (stable fields only, no mutable board hash):
  `SDK-TF-GRIDNET-URGENT-2025-BASELINE` in
  `audio-benchmark-platform/plan/swarm/TASKS.json`.
- Dependency rows: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
- `research/noise_suppression_candidate_census.md`
- `research/selected_audio_enhancement_candidates.md`
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Enhancement profile)
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
| `*.license` | REUSE sidecars for generated/text files as needed. |

## Release Gates (all blocked)

| Gate | Status | Reopen condition |
|---|---|---|
| RG-01 | blocked | Exact licensed TF-GridNet/URGENT source+checkpoint provenance/version reviewed. |
| RG-02 | blocked | Code/model/data/license/redistribution/patent/export review complete. |
| RG-03 | blocked | Pinned runtime/build and verified multi-distortion task geometry. |
| RG-04 | blocked | Versioned optional adapter boundary preserving installed v0. |
| RG-05 | blocked | Enhancement-profile deterministic controls on pinned inputs. |
| RG-06 | blocked | Rights-cleared matched corpus + authorized listening/labeled screen. |
| RG-07 | blocked | Paced target-device timing/CPU/memory/availability telemetry. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Non-Claims

- No TF-GridNet/ESPnet/URGENT source/checkpoint/runtime executed or bundled.
- No real audio/corpus/device/listening/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No sibling enhancement evidence inherited.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/tf-gridnet-urgent-2025-baseline/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/tf-gridnet-urgent-2025-baseline/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/tf-gridnet-urgent-2025-baseline/verify.py
```
