<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOICEFILTER — VoiceFilter blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for `SDK-VOICEFILTER` under
`docs/task-evidence/voicefilter/` only. No provider registration, no SDK public
API/ABI/default/descriptor/registry/shared build/CI change, no VoiceFilter
source, checkpoint, weights, enrollment/reference audio, runtime
download/execution, no real corpus, no listening, no device timing, no
benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

Inventory/candidate evidence marks VoiceFilter as blocked/unavailable:
original Google weights/runtime are not open; third-party substitutes are
separate candidates and must not be silently substituted. No exact licensed
source, exact checkpoint/assets, pinned runtime, rights-cleared spatial
cohort, or qualified Spatial-profile evidence is present in this worktree.
Missing or adverse results are non-qualifying.

## Stable linked-row identity

This package gates on stable linked-row identity only. It never hashes the
mutable full `plan/swarm/TASKS.json`. `linked_row_identity` stores the stable
projection and its SHA-256 for `SDK-VOICEFILTER` and dependency rows
`SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.

## Pinned inputs

- Stable task/dependency row projections from `audio-benchmark-platform/plan/swarm/TASKS.json`.
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Spatial profile).
- `audio-benchmark-platform/plan/audio-sdk/README.md`.
- `audio-benchmark-platform/plan/INVENTORY.json`.
- `research/voice-enhancement-20261101/candidate_matrix.csv`.
- `research/voice-enhancement-20261101/agent-transform-space/REPORT.md`.
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
| RG-01 | blocked | Exact immutable VoiceFilter/substitute source revision, reviewed license, exact checkpoint/weights identity, per-file digests. |
| RG-02 | blocked | Exact checkpoint/weights/config/reference-cue assets with immutable digests and reviewed rights/consent/redistribution/output-use terms; frozen enrollment/reference protocol. |
| RG-03 | blocked | Pinned reproducible runtime and exact task geometry/reference timing/cue conditioning/adapter boundary. |
| RG-04 | blocked | Versioned optional adapter boundary preserving installed v0 behavior. |
| RG-05 | blocked | Deterministic fixture conformance, 3x cold-start byte-identical regen, strict adverse/missing/invalid/nonfinite rejection. |
| RG-06 | blocked | Rights-cleared matched Spatial-profile evidence: geometry/layout/timestamp calibration, source/target/reference conditions, labels, leakage, target damage, channel loss, room/reference changes. |
| RG-07 | blocked | Paced target-device/runtime CPU, memory, deadline, availability, failure measurements. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Spatial profile requirements (blocked)

Spatial profile requires recorded geometry/layout/timestamp calibration and
source/target/reference conditions/permissions; task-matched held-out
localization/activity/extraction labels; leakage, target damage, channel loss,
and room/reference-condition changes; exact source intervals, availability,
dropped/stale events, and cross-hop behavior; frozen enrollment/reference cue
protocol and target-absent/overlap controls; rights-cleared matched cohort;
target-device pacing/CPU/memory/deadline/availability; and fail-closed
missing/invalid/nonfinite/adverse handling. All are blocked/not qualified here.

## Non-claims

- No VoiceFilter source/checkpoint/weights/runtime/reference audio executed or bundled.
- No real audio/corpus/enrolled speaker/listening/device timing/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No network/download/fabrication/substitution of absent artifacts.
- No sibling evidence inherited as VoiceFilter result.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/voicefilter/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/voicefilter/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/voicefilter/verify.py
```
