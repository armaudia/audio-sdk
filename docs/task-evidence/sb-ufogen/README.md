<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SB-UFOGEN — SB-UFOGen dereverberation blocker evidence

## Decision

`DEFER` / `proposal_only_not_qualified` / `not_qualified`.

This package is a deterministic, task-local blocker record for **SB-UFOGen** as
a dereverberation/room candidate. It does **not** implement, download,
reconstruct, load, or execute SB-UFOGen. No source, checkpoint, weights, runtime,
corpus audio, dereverberated output, listening result, device timing, or
benchmark result is included.

## Exact linked evidence

- Task row: `SDK-SB-UFOGEN` in `plan/swarm/TASKS.json` (stable identity
  projected only; mutable board fields are never hashed/gated).
- Inventory row: `sb-ufogen` in `plan/INVENTORY.json` (verification profile
  `room`, disposition `sdk-model`, evidence status `considered`).
- Evidence: `research/dereverberation_candidates_20261028.md` records SB-UFOGen
  as a strong utterance-level quality reference with no verified usable official
  checkpoint/inference path or causal streaming implementation; published GPU
  results are not local measurements.
- Profile: Room (`plan/swarm/VERIFICATION.md`).
- Merged sibling evidence packages: `docs/task-evidence/nemo-schr-dinger-bridge-dereverberation/`,
  `docs/task-evidence/online-mono-wpe-reference/`,
  `docs/task-evidence/rose-cd-one-step/` (context only; not SB-UFOGen execution).

## Why blocked

| Gap | Required before reopen |
|---|---|
| Source/license | Official SB-UFOGen source at immutable revision/archive/tree digest with reviewed license/notice. |
| Weights/assets | All required checkpoints/config/vocoder/assets with per-file byte count + SHA-256 and reviewed terms. |
| Runtime | Pinned lockfile/install digest and offline deterministic load/inference path. |
| Geometry/timing | Exact sample-rate/channels/frame/hop/lookahead/state/reset/drain/content-delay contract for the target SDK geometry. |
| Rights/cohort | Rights-cleared frozen room cohort: render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise, reset schedule. |
| Outcomes | Echo/late-reverb attenuation, near-end preservation, nonfinite/peak behavior, alignments, and device timing/resources on target. |
| Comparison | Identity/noisy control and established task-matched baseline on the same frozen cohort with matched scoring. |
| Intake/release | Opt-in provider intake, OFF default, independent exact-head review, release approval. |

## Release gates (all blocked)

RG-01..RG-08 are all `blocked`, `qualifies=false`. No missing/blocked/synthetic
result qualifies.

## Boundary

No provider registration, no public API/ABI, no descriptor/registry/default, no
shared CMake/CI change, no real corpus/weights/runtime, no listening, no device
timing, no benchmark, no release claim. Installed v0 geometry remains 16 kHz,
mono, float32, 160 samples.

## Regenerate / verify

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`verify.py` checks strict JSON, canonical bytes, exact pins, blocker semantics,
stable linked-row identity, licensing, absent prohibited artifacts, merge-base
git scope, and 3 cold-start byte-identical regenerations.
