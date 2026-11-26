<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Stream.FM speech-enhancement checkpoint evidence

**Task:** `SDK-STREAM-FM-SPEECH-ENHANCEMENT-CHECKPOINT`  
**Decision:** `DEFER`  
**Status:** `proposal_only_incomplete`  
**Qualification:** `not_qualified`

## Scope

This directory is a bounded, deterministic, task-local feasibility/blocker package for
Stream.FM speech enhancement. It records what is locally pinned, what is missing, and the exact
gates required before any implementation, qualification, or release claim.

A local Stream.FM source checkout is present and pinned by SHA-256 in `SOURCES.sha256`:

- `data/checkouts/StreamFM` at revision `ab2700c1154acc5c2ce67a5344182028336413f5`
- AGPL-3.0 license file, README, SE config, predictor config, and requirements are pinned

No pretrained checkpoint weights, rights record, locked runtime execution, parity vector, matched
enhancement cohort, or device timing evidence is present. No runtime is downloaded, built,
imported, or executed.

## What this package does not claim

- No Stream.FM checkpoint weights or model assets are bundled.
- No AGPL/model/corpus redistribution rights are approved.
- No real audio, corpus, listening, device timing, benchmark, or release claim is made.
- The synthetic signal control is deterministic local arithmetic only; it is **not** Stream.FM
  output, not quality evidence, and not parity.
- No provider registration, descriptor/registry/default change, installed-v0 ABI change, shared
  build/CI change, board mutation, or handoff change is made.

## Blocked release gates

All eight gates are blocked:

1. `exact_runtime_and_asset_identity`
2. `rights_licence_and_redistribution`
3. `reproducible_isolated_execution`
4. `exact_reference_parity_or_provenance`
5. `enhancement_cohort_and_scoring`
6. `task_geometry_and_boundary`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Reproduction

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py all` regenerates `report.json`, `report.json.sha256`, `contract.json`, and
`SOURCES.sha256` in that order. `verify.py` is read-only and checks canonical bytes, digests,
SPDX sidecars, git scope, source/boundary pins, rejection behavior, and three fresh-process
cold-start regenerations for byte identity.

## Mutable board rule

The mutable full `plan/swarm/TASKS.json` board file is never hashed. Only stable linked-row
identity is projected into `task_row_identity` and gated by tests/verify.
