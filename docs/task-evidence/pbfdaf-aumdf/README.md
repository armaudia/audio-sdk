<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PBFDAF-AUMDF task-local blocker evidence

## Scope

This directory contains bounded, deterministic, task-local feasibility evidence for `SDK-PBFDAF-AUMDF` (PBFDAF / AUMDF, partitioned-block frequency-domain adaptive filter / alternatively updated MDF). It is **proposal-only**, **incomplete**, and **not qualified**.

- Decision: `DEFER`
- Evidence status: `incomplete`
- Qualification: `not_qualified` (`candidate_qualified=false`, `no_missing_result_qualifies_candidate=true`)
- Release gates: 8 blocked
- No provider registration, no installed-v0/ABI/registry/default/shared-build/CI change
- No real corpus, weights, runtime, listening, device timing, benchmark, or release claim

## Task identity (stable linked-row only)

The package gates only stable linked-row identity from `audio-benchmark-platform/plan/swarm/TASKS.json`. It records `mutable_file_sha256_at_read` for provenance but sets `whole_file_hashed=false` and never hashes the mutable whole plan/swarm/TASKS.json into report/contract bytes. Mutable fields (`owner`, `status`, `review`, `handoff`, `blocked_reason`, `dispatch_priority`) are excluded.

## Exact blockers

| ID | Requirement | State |
|---|---|---|
| `reference_runtime_absent` | Exact licensed PBFDAF/AUMDF reference implementation/runtime with immutable revision, license terms, reproducible build/run instructions. | absent |
| `rights_record_absent` | Rights record covering code/runtime use, fixtures, and paired render/capture assets needed for qualification. | absent |
| `paired_cohort_absent` | Rights-cleared paired render/capture cohort with frozen echo-only, near-end-only, double-talk, path-change, no-reference conditions. | absent |
| `mdf_parity_baseline_unexecuted` | Task-matched MDF/PBFDAF comparison on same frozen cohort; convergence, ERLE, near-end preservation, cost. | absent |
| `timing_evidence_absent` | Algorithmic/content delay, availability, memory, deadline behavior for exact runtime/device profile. | absent |
| `provider_intake_incomplete` | Opt-in provider intake, descriptor/license review, independent exact-head review before any registration/default. | absent |

## Room profile (blocked)

Per `plan/swarm/VERIFICATION.md` Room profile: freeze render/reference or measured RIRs, channel/rate/hop, excitation, delay, movement, noise, reset schedule; include echo-only, near-end-only, double-talk, no-reference cases; report echo attenuation, near-end damage, nonfinite failures, alignments including delayed/missing render; no-reference suppressor gets independent comparison. All required items are unsatisfied for qualification.

## Deterministic synthetic accounting control

`reference.py` provides stdlib-only, deterministic synthetic accounting (not real AEC, not real audio): partitioned-block geometry bookkeeping, finite arithmetic checks, state reset, and adverse-case rejection. Adverse/missing/invalid/nonfinite cases are rejected before processing and recorded as `state_unchanged=true`.

## Regeneration

```sh
cd docs/task-evidence/pbfdaf-aumdf
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py all` regenerates `report.json`, `report.json.sha256`, `contract.json`, and `SOURCES.sha256`. Cold-start regeneration is checked by tests/verify for byte-identical output.

## Files

- `reference.py` - stdlib-only deterministic reference/control/audit
- `report.json` / `report.json.sha256` - canonical report and SHA-256 sidecar
- `contract.json` - machine-readable contract
- `SOURCES.sha256` - pinned source/boundary/package digests
- `run.py` - deterministic regeneration/check
- `verify.py` - strict read-only verifier
- `test_reference.py` - unit tests
- `*.license` - REUSE sidecars for machine-generated artifacts
