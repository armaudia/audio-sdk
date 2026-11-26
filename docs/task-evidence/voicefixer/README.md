<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOICEFIXER — VoiceFixer blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for `SDK-VOICEFIXER` under
`docs/task-evidence/voicefixer/` only. No provider registration, no SDK public
API/ABI/default/descriptor/registry/shared build/CI change, no VoiceFixer
source, checkpoint, weights, runtime download/execution, no real corpus, no
listening, no device timing, no benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only`: `true`

VoiceFixer is an `sdk-model` restoration candidate in inventory. No exact
pinned licensed source, exact checkpoint/assets, pinned runtime,
rights-cleared matched Restoration cohort, or qualified Restoration-profile
evidence is present in this worktree. Missing or adverse results are
non-qualifying.

## Stable linked-row identity

This package gates on stable linked-row identity only. It never hashes the
mutable full `plan/swarm/TASKS.json`. `linked_row_identity` stores the stable
projection and its SHA-256 for `SDK-VOICEFIXER` and dependency rows
`SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.

## Pinned inputs

- Stable task/dependency row projections from `audio-benchmark-platform/plan/swarm/TASKS.json`.
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Restoration profile).
- `audio-benchmark-platform/plan/audio-sdk/README.md`.
- `audio-benchmark-platform/plan/INVENTORY.json`.
- SDK boundary pins: `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`,
  `api/include/audio_sdk/session_v0.h`, `docs/provider-intake.md`.

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
| RG-01 | blocked | Exact immutable VoiceFixer source revision, reviewed license, per-file digests. |
| RG-02 | blocked | Exact checkpoint/weights/config/assets with immutable digests and reviewed rights/redistribution/output-use terms. |
| RG-03 | blocked | Pinned reproducible runtime and exact task geometry/adapter boundary. |
| RG-04 | blocked | Versioned optional adapter boundary preserving installed v0 behavior. |
| RG-05 | blocked | Deterministic fixture conformance, 3x cold-start byte-identical regen, strict adverse/missing/invalid/nonfinite rejection. |
| RG-06 | blocked | Rights-cleared matched Restoration-profile evidence: frozen corruption/metadata/clean baseline, degradation/erasure/bandwidth strata, concealment/validity, decoded intervals, task-specific quality, peak/timing bounds, controls. |
| RG-07 | blocked | Paced target-device/runtime CPU, memory, deadline, availability, failure measurements. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Restoration profile requirements (blocked)

Restoration profile requires frozen corruption/metadata and corresponding
clean/audio packet baseline; stratification by degradation, erasure burst and
bandwidth; discrete concealment/validity; decoded intervals; task-specific
quality; and bounds on output peaks and timing. All are blocked/not qualified
here.

## Non-claims

- No VoiceFixer source/checkpoint/weights/runtime executed or bundled.
- No real audio/corpus/listening/device timing/benchmark/release result.
- No provider registration/default/API/ABI/shared build/CI/board change.
- No network/download/fabrication/substitution of absent artifacts.
- No sibling evidence inherited as VoiceFixer result.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/voicefixer/run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v docs/task-evidence/voicefixer/test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/voicefixer/verify.py
```
