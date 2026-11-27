<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION — blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for
`SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION` under
`docs/task-evidence/waveform-only-filler-stutter-deletion/` only. No provider
registration, no SDK public API/ABI/default/descriptor/registry/shared
build/CI change, no waveform deletion source/model/weights/runtime
download/execution, no real corpus, no labeled edit targets, no listening, no
device timing, no benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

Inventory/candidate evidence marks waveform-only filler/stutter deletion as
considered/research-control and out of scope: VAD labels speech and cannot
safely delete valid speech; no labeled edit target exists. No exact licensed
source/runtime/assets, no rights-cleared labeled filler/stutter edit targets,
no deterministic edit-boundary mapping, and no qualified Rate-profile evidence
is present in this worktree. Missing or adverse results are non-qualifying.

## Stable linked-row identity

This package gates on stable linked-row identity only. It never hashes the
mutable full `plan/swarm/TASKS.json`. `linked_row_identity` stores the stable
projection and its SHA-256 for `SDK-WAVEFORM-ONLY-FILLER-STUTTER-DELETION` and
dependency rows `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`.

## Pinned inputs

- Stable task/dependency row projections from `audio-benchmark-platform/plan/swarm/TASKS.json`.
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Rate profile).
- `audio-benchmark-platform/plan/audio-sdk/README.md`.
- `audio-benchmark-platform/plan/INVENTORY.json`.
- `research/voice-enhancement-20261101/candidate_matrix.csv`.
- `research/voice-enhancement-20261101/agent-segmentation/REPORT.md`.
- SDK boundary pins: `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`,
  `api/include/audio_sdk/session_v0.h`, `docs/provider-intake.md`,
  `CMakeLists.txt`, `REUSE.toml`, `scripts/ci.py`.

## Required artifacts

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

## Release gates (all blocked)

| Gate | Status | Reopen condition |
|---|---|---|
| RG-01 | blocked | Exact immutable source/revision, reviewed license, exact task definition, per-file digests. |
| RG-02 | blocked | Rights-cleared labeled filler/stutter edit targets with reviewed rights/consent/redistribution/output-use terms and frozen edit policy distinguishing valid speech from deletable disfluency. |
| RG-03 | blocked | Pinned reproducible runtime and exact task geometry/edit-boundary mapping/buffering/content delay/adapter boundary. |
| RG-04 | blocked | Versioned optional adapter boundary preserving installed v0 behavior. |
| RG-05 | blocked | Deterministic fixture conformance, 3x cold-start byte-identical regen, strict adverse/missing/invalid/nonfinite rejection. |
| RG-06 | blocked | Rights-cleared matched Rate-profile evidence: source/output mapping, duration, pitch, transient audibility, playback buffering, 1x/rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, speech preservation. |
| RG-07 | blocked | Paced target-device/runtime CPU, memory, deadline, availability, failure measurements. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Rate profile requirements (blocked)

Rate profile requires source/output mapping, duration, pitch, transient
audibility and playback buffering; 1x, rate changes, unfamiliar speech, music,
silence, rebuffer, drift and the final partial window; pause/filler decisions
tied to source timestamps and measured speech preservation; exact source
intervals, availability, dropped/stale events and cross-hop behavior;
rights-cleared matched cohort; target-device pacing/CPU/memory/deadline/
availability; deterministic 3x byte-identical regen and strict adverse
rejection; and fail-closed missing/invalid/nonfinite/adverse handling. All are
blocked/not qualified here.

## Non-claims

- No waveform-only filler/stutter deletion source/model/weights/runtime/edit output executed or bundled.
- No real audio/corpus/labeled edit targets/listening/device timing/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No network/download/fabrication/substitution of absent artifacts.
- No VAD-only gate treated as safe filler/stutter deletion.
- No sibling evidence inherited as this task's result.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/waveform-only-filler-stutter-deletion/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/waveform-only-filler-stutter-deletion/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/waveform-only-filler-stutter-deletion/verify.py
```
