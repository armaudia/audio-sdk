<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# NVIDIA RE-USE — model/runtime/rights blocker evidence

This package is **task-local, proposal-only, incomplete and not qualified**
evidence for `SDK-NVIDIA-RE-USE` (`nvidia-re-use`, enhancement). Decision:
`DEFER`; qualification: `not_qualified`. A missing, blocked, rejected or
source-reported result never qualifies the candidate.

## Exact blocker

Pinned evidence identifies NVIDIA Real-time RE-USE as a universal Mamba speech
restoration model (30 compute/lookahead points, 8-48 kHz, explicit online API).
The upstream checkpoint is reported under NVIDIA NSCLv1 noncommercial terms; a
community Swift/MLX port exists as separate integration scope, not an NVIDIA
implementation or endorsement. On this host/workspace:

- no pinned `model.safetensors` (or approved equivalent) with SHA-256/byte count;
- no pinned `reuse-fast-cli` binary/build/lock/runtime parity record;
- no NSCLv1 license text and no written use/redistribution/derived-output decision;
- no verified candidate operating-point geometry/content delay record;
- no rights-cleared matched cohort with pinned SI-SDR/STOI scorer and controls.

No files were downloaded, cloned, built, converted, loaded or executed. No
candidate audio was produced.

## Boundary

- Installed v0 unchanged: 16 kHz mono float32, 160 samples/frame.
- No provider registration, descriptor, registry, default, public API/C ABI,
  shared build or CI change.
- No real corpus, weights, runtime, listening, timing, benchmark or release claim.
- The mutable full `plan/swarm/TASKS.json` is never hashed; only stable linked-row
  identity is pinned.

## Reproduction

```sh
python3 -m unittest -v test_reference.py
python3 run.py --all
python3 run.py --verify-repro
python3 verify.py
```

## Files

| File | Purpose |
| --- | --- |
| `reference.py` | Deterministic stdlib-only blocker/reference validator |
| `report.json` | Machine-readable DEFER/not_qualified report |
| `contract.json` | Exact artifact/runtime/rights requirements and gates |
| `SOURCES.sha256` | Pinned source/boundary/package hashes |
| `run.py` | 3x byte-identical regeneration |
| `test_reference.py` | Adverse/rejection/board-identity tests |
| `verify.py` | Read-only fail-closed verification |
