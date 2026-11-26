<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SUPERPOWERED — Superpowered blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for `SDK-SUPERPOWERED` under
`docs/task-evidence/superpowered/` only. No provider registration, no SDK
public API/ABI/default/descriptor/registry/shared build/CI change, no
Superpowered source/binary/runtime/license key download, no real corpus,
no device timing, no listening, no benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

Pinned research identifies Superpowered as a commercial, sunsetting
playback-speed SDK candidate and marks it **"Do not adopt"** in
`cpp-library/pipeline-validation/playback-speed-candidates.md`. No exact
licensed source/binary/runtime, reviewed rights, deterministic execution,
matched corpus, or target-device timing evidence is present in this worktree.

## Pinned Inputs

- Linked task row identity (stable fields only, no mutable board hash):
  `SDK-SUPERPOWERED` in `audio-benchmark-platform/plan/swarm/TASKS.json`.
- Dependency rows: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`.
- `cpp-library/pipeline-validation/playback-speed-candidates.md`
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Rate profile)
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
| RG-01 | blocked | Exact licensed Superpowered SDK provenance/version/terms reviewed. |
| RG-02 | blocked | Commercial/license/redistribution/patent/export review complete. |
| RG-03 | blocked | Pinned runtime/build and verified task geometry. |
| RG-04 | blocked | Versioned optional adapter boundary preserving installed v0. |
| RG-05 | blocked | Rate-profile deterministic controls on pinned inputs. |
| RG-06 | blocked | Rights-cleared matched corpus + authorized listening/labeled screen. |
| RG-07 | blocked | Paced target-device timing/CPU/memory/availability telemetry. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Non-Claims

- No Superpowered SDK/source/binary/license key/model/runtime executed or bundled.
- No real audio/corpus/device/listening/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No sibling TSM evidence inherited.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/superpowered/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/superpowered/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/superpowered/verify.py
```
