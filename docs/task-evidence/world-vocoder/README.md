<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WORLD-VOCODER — WORLD vocoder feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory is
task-local feasibility evidence for `SDK-WORLD-VOCODER` (`component=world-vocoder`,
`mode=feasibility`, Voice profile). It is **not** a WORLD vocoder implementation
and **not** a qualification result. No WORLD source import, build, execution,
weight, runtime, feature input, audio, corpus, listening, device timing,
benchmark, or release claim is present. **No result here qualifies WORLD vocoder.**

## Proceed / defer decision

**DEFER.** Exact WORLD source revision/license/notice provenance, pinned
deterministic build/runtime, reviewed terms/output use, and a rights-cleared
Voice-profile cohort with controls are absent. Before any adapter/provider
exposure, this row needs a separate versioned intake with reviewed rights,
deterministic offline runtime, Voice-profile measurements, and an explicit
OFF-by-default/opt-in boundary. A readiness conclusion with an exact external
blocker is not a qualification or release pass.

## Scope

- Task-local only: `docs/task-evidence/world-vocoder/`.
- Stable linked-row identity gating only; the mutable board file is not hashed.
- Deterministic stdlib-only regeneration, strict JSON, exact pins, 3x
  byte-identical cold-start regen, and adverse/missing/invalid/nonfinite
  rejection coverage.
- No provider registration, installed-v0/ABI/registry/default/shared-build/CI
  change, real corpus/weights/runtime, listening, device timing, benchmark, or
  release claim.

## Boundary

Installed public v0 geometry remains unchanged and unexercised by this package:
16 kHz, mono, float32, 160-sample frames. No SDK callback is invoked, no model
I/O is claimed, and no provider is registered or default-enabled.

## Reproduction

Pinned interpreter: Python 3.12.16. Environment:

```sh
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
```

Commands:

```sh
python3.12 run.py all
python3.12 -m unittest -v test_reference.py
python3.12 verify.py
```

Cold-start regeneration repeats 3x and must be byte-identical. Network and
runtime are not required.

## Canonical digests

- `contract.json` SHA-256: `733a52da7760a151a64ab0664bce7daea9f4917cb022177db721c27b06c1dbfd`
- `report.json` SHA-256: `b26257e6e4e3fa1bc418a3845751d2a8a6ee25f8f8a9b7827e8c38b3634d1e94`
- `report.json.sha256` SHA-256: `5a3a7da8f58fe87c0980d0bd05552e9e35eeac131bba8430797a4abc6e64a60c`
- `SOURCES.sha256` SHA-256: `dab4477d75cc0d9fd44bda147f034c77430b63939e985673c7107d25c3f706e8`
