<!--
SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
-->

# YAMNet ONNX — task evidence (DEFER)

**Task:** `SDK-YAMNET-ONNX`  
**Status:** `proposal_only_incomplete`  
**Decision:** `DEFER` (`not_qualified`)  
**Defer before:** `opt_in_adapter_exposure`

## What this package is

A bounded, deterministic, task-local evidence/blocker package for the YAMNet
ONNX feasibility row. It records exact blocker state and provides a tiny
stdlib-only synthetic rate/content contract control. The control is **not**
model output, **not** real audio, and has **no qualification effect**.

## What this package is not

- No YAMNet ONNX model, checkpoint, runtime, label artifact, or derived weight
  downloaded, loaded, executed, vendored, or redistributed.
- No real audio, corpus, device timing, listening, public benchmark, release,
  or qualification claim.
- No provider registration, descriptor/registry/default/shared build/CI change,
  and no installed v0/ABI behavior change.
- No network access.

## Pinned context (not measured here)

Source-reported context only (not measured/qualified here): YAMNet ONNX is a
generic event model, not podcast-tuned; AudioSet labels are CC BY 4.0; 521
classes, 0.96s window / 0.48s hop. This package treats AudioSet label handling
and cadence as advisory contract requirements only; scores remain advisory and
unverified.

## Exact blockers

| ID | Gate(s) | Requirement |
|---|---|---|
| `deployable_asset_absent` | exact_source_and_asset_identity, matched_reference_parity | Exact local YAMNet ONNX model/checkpoint + AudioSet label-map artifact with immutable hashes/byte counts/provenance. |
| `rights_uncleared` | rights_and_publication, public_default_and_release | Model/label/data rights, notices, redistribution, product-use, publication terms. |
| `exact_runtime_absent` | runtime_and_reproducibility, matched_reference_parity | Isolated pinned runtime with deterministic execution recipe and recorded platform. |
| `reference_parity_absent` | matched_reference_parity, runtime_and_reproducibility | Approved exact-runtime reference on frozen inputs with hashed outputs/parity verification. |
| `rate_cohort_absent` | rate_cohort_and_scoring, public_default_and_release | Rights-cleared held-out rate/content cohort with source/output mapping, duration/pitch/transient/playback controls and task-matched scoring. |
| `label_cadence_unverified` | label_cadence_and_contract, adapter_boundary_and_isolation | Verified AudioSet label handling, class ordering, score calibration/cadence, window/hop, timestamp mapping; scores advisory. |
| `adapter_boundary_incomplete` | adapter_boundary_and_isolation, public_default_and_release | Optional caller-supplied-asset adapter boundary, off by default, outside installed v0/shared build/CI/public registration. |
| `public_default_release_blocked` | public_default_and_release | Explicit default/resource/deadline/release/public-benchmark approval; missing evidence cannot qualify. |

All 8 release gates are `blocked`. `qualification.status=not_qualified`,
`candidate_qualified=false`, `no_missing_result_qualifies_candidate=true`.

## Task row identity

Stable linked-row SHA-256 (mutable TASKS.json fields excluded): `2cfe5276c47832afe73f0ed1a339571355cbc33f91a06b94bdf9f74fc552e3ad`

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py report.json
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py sources
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, and `contract.json`.
`run.py sources` regenerates `SOURCES.sha256` from pinned source/worktree files
plus current package files. `verify.py` checks pins, strict JSON, contract,
stable task-row identity (never hashes mutable full `TASKS.json`), adverse
controls, scope, licensing, README digest/claims, diff-check, and 3 cold-start
byte-identical regenerations.
