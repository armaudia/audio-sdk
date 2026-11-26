<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PSDN-ZERO-SHOT-AC — PSDN zero-shot AC blocker evidence

## Decision

`DEFER` / `proposal_only_not_qualified` / `not_qualified`.

This package is a deterministic, task-local blocker record for **PSDN zero-shot
AC**. It does **not** implement, download, reconstruct, load, or execute PSDN.
No source, checkpoint, weights, runtime, corpus audio, converted output,
listening result, device timing, or benchmark result is included.

## Exact linked evidence

- Task row: `SDK-PSDN-ZERO-SHOT-AC` in `plan/swarm/TASKS.json` (stable identity
  projected only; mutable board fields are never hashed/gated).
- Evidence: `research/accent-conversion-20261101/README.md:173` —
  “Paper and samples inspected; no official runnable checkpoint/repo located.”
- Profile: Voice (`plan/swarm/VERIFICATION.md`).
- Merged sibling surveys: `docs/task-evidence/survey-trn-03/`,
  `docs/task-evidence/survey-trn-04/` (PSDN is a boundary/considered lead, not
  a local execution).

## Why blocked

| Gap | Required before reopen |
|---|---|
| Source/license | Official PSDN source at immutable revision/archive/tree digest with reviewed license/notice. |
| Weights/assets | All required checkpoints/config/vocoder/assets with per-file byte count + SHA-256 and reviewed terms. |
| Runtime | Pinned lockfile/install digest and offline deterministic load path. |
| Rights/consent | Source-speaker consent, target/reference availability, output-use terms. |
| Cohort | Frozen rights-cleared cohort with manual transcripts, groups, matched controls. |
| Outcomes | Separate content, identity/similarity, naturalness, accent outcomes + independent listening. |
| Timing/resources | Alignment, first-output/tail, peaks, nonfinite, device timing, CPU/memory, deadlines. |
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
