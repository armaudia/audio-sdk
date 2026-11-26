# SDK-URGENT-BSRNN-FLOW — blocker evidence (DEFER)

Task: `SDK-URGENT-BSRNN-FLOW`
Component: `urgent-bsrnn-flow`
Profile: `enhancement`
Decision: `DEFER`
Status: `incomplete` / proposal-only
Qualification: `not_qualified`

## Purpose

Bounded deterministic task-local evidence package. This package records that
exact licensed URGENT BSRNN-Flow source, checkpoint/weights, runtime, rights
review, matched real-corpus evidence, and target-device timing are **not**
present in this worktree/workspace probes at evidence time. It makes no model,
runtime, quality, timing, listening, benchmark, or release claim.

## Scope

- Writes only under `docs/task-evidence/urgent-bsrnn-flow/`.
- No provider registration, no installed-v0/ABI/registry/default/shared-build/CI change.
- No network/download. No real corpus/weights/runtime execution.
- No mutable full `plan/swarm/TASKS.json` hash. Linked-row identity is a stable
  projection hash of selected task-row fields only.

## Evidence posture

- `decision = DEFER`
- `qualification.status = not_qualified`
- 8 blocked release gates (RG-01..RG-08), all `qualifies=false`.
- Absence probes cover workspace/worktree/home candidate locations; all absent
  at generation time.
- Source-reported research notes are context only, not measured evidence.

## Files

- `reference.py` — stdlib-only deterministic builder, strict JSON loader, probes, pins.
- `contract.json` — machine-readable blocker contract.
- `report.json` — machine-readable blocker report.
- `report.json.sha256` — SHA-256 digest sidecar.
- `SOURCES.sha256` — digests for package files and pinned source/boundary inputs.
- `run.py` — deterministic 3x byte-identical regeneration.
- `verify.py` — read-only verification (pins, schema/policy, scope, 3x regen).
- `test_reference.py` — pytest coverage for policy, strict JSON, probes, pins, regen.
- `*.license` — SPDX sidecars.

## Regenerate

```sh
python3 docs/task-evidence/urgent-bsrnn-flow/run.py all
python3 docs/task-evidence/urgent-bsrnn-flow/verify.py
python3 -m pytest -q docs/task-evidence/urgent-bsrnn-flow/test_reference.py
```
