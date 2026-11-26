<!--
SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
-->

# VoiceFilter-Lite / personal VAD — task evidence (DEFER)

**Task:** `SDK-VOICEFILTER-LITE-PERSONAL-VAD`  
**Decision:** `DEFER` (proposal-only, incomplete, `not_qualified`)  
**Defer before:** `opt_in_adapter_exposure`

## What this package is

A bounded, deterministic, task-local evidence/blocker package for the
VoiceFilter-Lite / personal VAD feasibility row. It records the exact blocker
state and provides a tiny stdlib-only synthetic spatial/TSE scoring control.
The control is **not** model output, **not** real audio, and has **no
qualification effect**.

## What this package is not

- No model, checkpoint, runtime, wheel, or derived weight downloaded, loaded,
  executed, vendored, or redistributed.
- No enrolled-speaker/target-speaker extraction corpus consumed or fabricated.
- No network, device timing, listening, public benchmark, release, or
  qualification claim.
- No provider registration, descriptor/registry/default/shared build/CI change,
  no installed v0/ABI behavior change.

## Exact blockers

| ID | Gate(s) | Requirement |
|---|---|---|
| `deployable_checkpoint_absent` | exact_source_and_asset_identity, matched_reference_parity | Exact deployable local checkpoint/runtime artifact with immutable hashes/byte counts/provenance. |
| `enrolled_target_cohort_absent` | spatial_cohort_and_scoring, matched_reference_parity | Rights-cleared enrolled-speaker cohort with overlapping speakers and clean target references. |
| `rights_uncleared` | rights_and_publication, public_default_and_release | Source/checkpoint/data rights, notices, redistribution, product-use, publication terms. |
| `exact_runtime_absent` | runtime_and_reproducibility, matched_reference_parity | Isolated pinned runtime with deterministic execution recipe and recorded platform. |
| `reference_parity_absent` | matched_reference_parity, runtime_and_reproducibility | Approved exact-runtime reference on frozen inputs with hashed outputs/parity verification. |
| `geometry_delay_contract_unverified` | geometry_delay_and_state, adapter_boundary_and_isolation | Verified geometry/enrollment conditioning/sample-time mapping/delay/reset/state isolation/invalid-input handling. |
| `adapter_boundary_incomplete` | adapter_boundary_and_isolation, public_default_and_release | Optional caller-supplied-asset adapter boundary, off by default, outside installed v0/shared build/CI/public registration. |
| `public_default_release_blocked` | public_default_and_release | Explicit default/resource/deadline/release/public-benchmark approval; missing evidence cannot qualify. |

All 8 release gates are `blocked`. `qualification.status=not_qualified`,
`candidate_qualified=false`, `no_missing_result_qualifies_candidate=true`.

## Reproduce

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
PYTHONDONTWRITEBYTECODE=1 python3 run.py sources
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, and `contract.json`.
`run.py sources` regenerates `SOURCES.sha256` from pinned source/worktree files
plus current package files. `verify.py` checks pins, strict JSON, contract,
stable task-row identity (never hashes mutable full `TASKS.json`), adverse
controls, scope, licensing, and 3 cold-start byte-identical regenerations.
