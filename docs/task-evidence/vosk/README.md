<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOSK — Vosk feasibility blocker evidence (DEFER)

## Scope

Task-local deterministic evidence package for `SDK-VOSK` under
`docs/task-evidence/vosk/` only. No provider registration, no SDK public
API/ABI/default/descriptor/registry/shared build/CI change, no Vosk source,
model, wheel, runtime download/execution/load, no real corpus, no listening, no
device timing, no benchmark, and no release claim.

## Decision

- `status`: `incomplete`
- `decision`: `DEFER`
- `qualification.status`: `not_qualified`
- `proposal_only` in effect: blocker/readiness handoff only; not a qualified
  implementation.

Vosk is inventoried as `sdk-reference` with `verification_profile=rate`
(`cpp-library/pipeline-validation/playback-speed-candidates.md:878` records it
as an alternative content gate: "Older acoustic models; check accuracy on fast
speech"). This package does not qualify Vosk. It records exact external
blockers and fail-closed gates.

## Stable linked-row identity

This package gates on stable linked-row identity only. It never hashes the
mutable full `plan/swarm/TASKS.json`. `linked_row_identity` stores the stable
projection and SHA-256 for `SDK-VOSK` and dependency/foundation rows.

## Pinned inputs

- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` (Rate profile).
- `audio-benchmark-platform/plan/INVENTORY.json` (stable component identity).
- `audio-benchmark-platform/plan/audio-sdk/README.md`.
- `cpp-library/pipeline-validation/playback-speed-candidates.md`.
- SDK boundary pins: `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`,
  `api/include/audio_sdk/session_v0.h`, `docs/provider-intake.md`.
- Sibling boundary pin: `docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json`
  (separate component; not inherited as Vosk qualification).

## Rate profile (all blocked/not qualified)

Rate requires measured source/output mapping, duration, pitch, transient
audibility and playback buffering; 1×, rate changes, unfamiliar speech, music,
silence, rebuffer, drift and the final partial window; and pause/filler
decisions tied to source timestamps with measured speech preservation. No
admitted Vosk runtime/model/rights-cleared cohort exists here, so all Rate
requirements are blocked and non-qualifying.

## Required artifacts / release gates (all blocked)

| Gate | Status | Reopen condition |
|---|---|---|
| RG-01 | blocked | Exact immutable Vosk source revision, complete license/NOTICE/dependency provenance, reviewed terms. |
| RG-02 | blocked | Exact model archive/checkpoint IDs, immutable digests, model cards/licenses, reviewed acquisition/evaluation/redistribution/output-use rights. |
| RG-03 | blocked | Pinned runtime/wheel/archive, lock, offline install/load proof, reviewed runtime license/notice. |
| RG-04 | blocked | Separately reviewed opt-in adapter boundary preserving installed v0 geometry/ABI/default/registry/shared build. |
| RG-05 | blocked | Deterministic conformance, strict invalid/nonfinite/missing/adverse rejection, 3x cold-start byte-identical qualifying artifacts. |
| RG-06 | blocked | Rights-cleared matched Rate-profile evidence with required controls and speech-preservation measurements. |
| RG-07 | blocked | Paced target-device CPU/memory/deadline/availability/failure measurements with exact provenance. |
| RG-08 | blocked | Exact-head independent review, hosted CI, explicit release approval. |

## Exact external blockers

- BLK-01/RG-01: exact Vosk source/license/NOTICE/provenance not pinned/admitted.
- BLK-02/RG-02: exact model assets/digests/licenses/model cards/output-use rights not admitted.
- BLK-03/RG-03: pinned offline runtime/wheel/archive and deterministic load proof not admitted.
- BLK-04/RG-04: no separately reviewed opt-in adapter boundary; installed v0/default/ABI/registry/shared build must remain unchanged.
- BLK-05/RG-06: no rights-cleared matched Rate-profile evidence.
- BLK-06/RG-07: no paced target-device timing/resources/failure accounting.

## Non-claims

- No Vosk source/runtime/model downloaded, executed, loaded, bundled, or admitted.
- No provider registration/default/API/ABI/descriptor/registry/shared build/CI change.
- No real audio/corpus/listening/device timing/benchmark/release claim.
- No absent artifact fabricated/substituted; no sibling evidence inherited as Vosk qualification.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 docs/task-evidence/vosk/run.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v docs/task-evidence/vosk/test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 docs/task-evidence/vosk/verify.py
```
