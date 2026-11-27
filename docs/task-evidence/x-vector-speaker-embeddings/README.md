<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-X-VECTOR-SPEAKER-EMBEDDINGS - X-vector speaker embeddings blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`X-vector speaker embeddings` (`component_id=x-vector-speaker-embeddings`).
The acceptance profile is **Spatial**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**;
`status=incomplete`; `qualification.status=not_qualified`. A missing, blocked
or rejected result may never qualify the candidate.

## Exact blocker

Pinned planning records identify x-vector speaker embeddings only as a
considered SDK-model candidate with category-registry evidence; no reviewed
runnable implementation, checkpoint/release/version, license, weights digest,
runtime, consented cohort, or spatial/verification protocol is present in the
pinned workspace evidence. This package does **not** fabricate assets, download
weights, run models, read/score audio, or claim quality/timing. It records the
exact absence and blocks all release gates.

## Scope and boundary

- Task-local only: `docs/task-evidence/x-vector-speaker-embeddings/`.
- No provider registration, descriptor/default/registry change.
- No installed-v0/API/ABI/shared CMake/CI change.
- No real corpus, weights, runtime, listening, device timing, benchmark, or
  release claim.
- Stable linked-row identity is gated; mutable full `plan/swarm/TASKS.json` is
  never hashed.

## Spatial profile (blocked)

Per `plan/swarm/VERIFICATION.md` Spatial: record geometry, layout, timestamp
calibration, source/target/reference conditions and permissions; compare
localization/activity/extraction with task-matched held-out labels; report
leakage, target damage, channel loss, and changes in room/reference conditions.
Task note additionally requires consented speaker verification/embeddings with
separate roles and score calibration. All required results are blocked.

## Release gates (all blocked)

RG-01 source revision/license provenance; RG-02 checkpoint identity/geometry;
RG-03 rights/output terms; RG-04 pinned runtime/deterministic load; RG-05
consent/reference availability/output use; RG-06 frozen cohort/controls; RG-07
separate spatial quality and timing; RG-08 independent review and release
boundary.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

`run.py` performs 3 cold-start byte-identical regenerations. `verify.py` is
read-only and confirms pins, disposition, gates, fail-closed admission,
licensing/scope, merge-base scope enforcement, and 3x cold-start regeneration.

## Non-claims

No model/source/weights/runtime bundled or executed. No audio read/scored. No
quality, calibration, leakage/damage, timing, availability, device, benchmark,
listening, or release result. Missing/blocked evidence never qualifies.
