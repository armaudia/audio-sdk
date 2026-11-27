<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-XLSTM-SENET2 - xLSTM-SENet2 blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`xLSTM-SENet2` (`component_id=xlstm-senet2`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**; `status=incomplete`;
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

## Exact blocker

Pinned discovery evidence (`research/noise_suppression_candidate_census.md`)
lists xLSTM-SENet2 as a conditional high-quality comparator with upstream
VoiceBank+DEMAND metrics and a CUDA/PyTorch runtime note. This package does
**not** treat that mention as exact runnable source, pinned weights, reviewed
rights, or SDK-ready runtime evidence. No exact reviewed source revision,
immutable checkpoint digest, pinned offline runtime, rights-cleared cohort,
approved parity/protocol, model execution, audio scoring, listening, timing,
benchmark, or release claim is present.

## Scope and boundary

- Task-local only: `docs/task-evidence/xlstm-senet2/`.
- No provider registration, descriptor/default/registry change.
- No installed-v0/API/ABI/shared CMake/CI change.
- No real corpus, weights, runtime, listening, device timing, benchmark, or
  release claim.
- Stable linked-row identity is gated; mutable full `plan/swarm/TASKS.json` is
  never hashed.

## Enhancement profile (blocked)

Per `plan/swarm/VERIFICATION.md` Enhancement: identity/noisy control and an
established task-matched baseline; paired SI-SDR and STOI where permitted clean
references exist; clean-speech preservation, peaks and invalid outputs; for
unpaired speech a separately labeled predictive screen or authorized listening;
alignment, state, memory and measured content/availability timing for the exact
runtime. All required results are blocked.

## Release gates (all blocked)

RG-01 source revision/license provenance; RG-02 checkpoint identity/geometry;
RG-03 rights/output terms; RG-04 pinned runtime/deterministic load; RG-05
consent/reference availability/output use; RG-06 frozen cohort/controls; RG-07
separate enhancement quality and timing; RG-08 independent review and release
boundary.

## Strict verifier scope

`verify.py` is read-only. It checks pins, contract/report disposition, gates,
fail-closed admission, licensing, task-local scope, and 3x cold-start
regeneration. It enforces newest-merge-base branch-diff scope against
`origin/main` then `main`; if neither base is available it fails closed with
`scope_base_unavailable`, and any out-of-scope branch diff fails as
`base_out_of_scope_change`.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

`run.py` performs 3 cold-start byte-identical regenerations.

## Non-claims

No model/source/weights/runtime bundled or executed. No audio read/scored. No
SI-SDR/STOI, preservation, peak/invalid, listening, timing, availability,
device, benchmark, or release result. Missing/blocked evidence never qualifies.
