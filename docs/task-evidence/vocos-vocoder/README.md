<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOCOS-VOCODER — Vocos vocoder research-control blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory is
task-local evidence for `SDK-VOCOS-VOCODER` (`component=vocos-vocoder`,
`mode=research-control`, Voice profile). It is **not** a Vocos vocoder
implementation and **not** a qualification result. No vocoder source import,
weight load, Torch runtime, feature input, audio, corpus, listening, device
timing, benchmark, or release claim is present. **No result here qualifies Vocos
vocoder.**

## Proceed / defer decision

**DEFER.** Exact upstream Vocos source/license/notice provenance, immutable
vocoder weights, pinned Torch runtime, reviewed weight/output terms, and a
rights-cleared feature cohort are absent. A modified Vocos-derived copy is
vendored in MeanVC2 under Apache-2.0, but it is not admitted as exact upstream
source and no exact source+weights+runtime conjunction is present. Before any
processor exposure, this row needs a separate versioned intake with reviewed
rights, deterministic offline runtime, Voice-profile measurements, and an
explicit OFF-by-default boundary.

## Scope

- Task-local only: `docs/task-evidence/vocos-vocoder/`.
- Stable linked-row identity gating only; the mutable board file is not hashed.
- Deterministic stdlib-only regeneration, strict JSON, exact pins, 3x
  byte-identical cold-start regen, and adverse/missing/invalid/nonfinite
  rejection coverage.
- No provider registration, installed-v0/ABI/registry/default/shared-build/CI
  change, real corpus/weights/runtime, listening, device timing, benchmark, or
  release claim.

## Historical provenance only

A historical 2026-11-01 MeanVC2-bundled Vocos JIT decoder-only CPU probe
(synthetic mel `[1,80,100]`, 4 Torch threads, warmup 1, timed 5, mean
`0.17284687500214205s`, output `0.99s`, RTF `0.17459280303246671`, finite) is
pinned as `historical_provenance_only`. The 32 MB bundle and JIT file were
removed after that run; no byte count/SHA-256 is known. It is **not rerun**,
**not merged task evidence**, **not a quality/timing/release result**, and it
**qualifies nothing**.

## Reproduction

```sh
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

Cold-start regeneration repeats 3x and must be byte-identical. Network and
runtime are not required.
