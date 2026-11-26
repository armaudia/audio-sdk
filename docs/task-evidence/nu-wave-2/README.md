<!--
SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
-->

# NU-Wave 2 — task-local feasibility evidence

This package records a **bounded feasibility investigation** for task
`SDK-NU-WAVE-2`. It is proposal evidence only. No model, checkpoint, runtime,
rights record, cohort, parity vector or measured result is present, fabricated
or reused. The decision is `DEFER`; the qualification is `not_qualified`.

## Scope

| Field | Value |
| --- | --- |
| Task | `SDK-NU-WAVE-2` |
| Component | `nu-wave-2` |
| Mode | `feasibility` |
| Verification profile | `restoration` |
| Installed v0 geometry | 16 kHz mono float32, 160-sample frames |
| Candidate geometry | `unestablished` — never asserted |
| Control geometry | 16 kHz input, 48 kHz declared output, 3.5 kHz cutoff |

The control signal is deterministic and synthetic. It exercises metadata
accounting, duration conservation and adverse-input rejection only. No
bandwidth extension, generative reconstruction, high-band synthesis or artifact
latency measurement runs.

## Evidence and blockers

Pinned research records NU-Wave 2 as an upstream lead, not a qualified candidate:
no immutable source revision, exact checkpoint, model card, runtime lock,
licensed input cohort, degradation manifest, parity vector or rights record is
available. The caller-supplied asset manifest is admitted only as a strict
shape-and-digest gate; admitting a manifest does not execute a model or create a
result. The mutable full `plan/swarm/TASKS.json` is never hashed; only the
stable linked-row identity is pinned.

Eight release gates remain blocked (RG-01 through RG-08). No processor,
provider registration, public API/ABI change, registry default, shared build or
CI change, installed-v0 behavior change, listening claim, device-timing claim,
benchmark or release claim is made.

## Reproduction

From this directory, with Python 3.11 or newer:

```sh
python3 -m unittest -v test_reference.py
python3 run.py all
python3 run.py all --check
python3 verify.py
python3 -m reuse lint
```

`run.py all` regenerates `report.json`, `report.json.sha256`, `contract.json`
and `SOURCES.sha256`. Regeneration is byte-identical across three repeats, and
`verify.py` performs three additional cold-start checks in a temporary
directory. `SOURCES.sha256` pins only stable source, boundary and package files;
the mutable board file is excluded.

## Files

| File | Purpose |
| --- | --- |
| `reference.py` | Deterministic stdlib-only evidence model and strict gates |
| `report.json` | Machine-readable feasibility report (`DEFER`, `not_qualified`) |
| `contract.json` | Caller-supplied asset contract; no opt-in adapter is exposed |
| `SOURCES.sha256` | Exact source/boundary/package pins |
| `run.py` | Byte-reproducible artifact generator |
| `test_reference.py` | Unit tests for strict parsing and adverse controls |
| `verify.py` | Read-only fail-closed verification |
