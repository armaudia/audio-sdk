<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RT-VC — caller-supplied-asset feasibility evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`RT-VC` (`component_id=rt-vc`). The acceptance profile is **voice**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. A missing result never qualifies the
candidate.

This package does **not** implement a voice converter. The pinned voice-conversion
ledger (line 16) says `RT-VC` has `No checkpoint in official checkout`, records the
local run as `Blocked`, and explains that the official checkout has example
audio/code but no obtainable inference checkpoint or complete weight setup. The
official source checkout is present at commit
`9d9a55d0fb6cd53ebba108a0bab3380b1fc3c066` (tree
`934262ee05d2fc8ba55e3337631e733474d5edcd`), but it is source provenance only: no
license text is pinned, no checkpoint or complete weight setup is present, and the
source is not executed.

The fixed p360 target reference is recorded from the pinned ledger at SHA-256
`fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44`. Its
dataset/license provenance is explicitly unconfirmed, so it is **not** treated as
a permitted target. This package does not read or hash that audio file.

The package models the boundary a future caller would have to satisfy using the
`CONTRACTS.md` `as_asset_v0` rule: an asset ID, byte count, SHA-256 and
`storage=external`, supplied by the caller. The manifest is validated as a
shape-only intake control; it never supplies absent bytes, rights, consent,
matched evidence or qualification. The only admitted request is an
identity-source control at the installed public v0 geometry (16 kHz mono
`float32`, 160 samples per frame). Candidate conversion and p360-target requests
fail closed.

## What is verified

- The linked task row's stable identity (`id`, `title`, `mode`, `repository`,
  `component`) matches this package; the mutable full `TASKS.json` is never
  hashed or pinned.
- Read-only source pins match the voice ledger, inventory records, verification
  profile, accent census and pinned RT-VC source files.
- Boundary pins prove that no provider file, descriptor, registry, default, ABI,
  `CONTRACTS.md`, shared build or CI file changed.
- Fixed absence probes prove that no checkpoint, complete weight setup, rights
  record, consent record, cohort, runtime or reference audio is present. The
  pre-existing p360 reference is recorded from the ledger but not read.
- A deterministic synthetic identity control exercises only the declared public
  v0 geometry. It is not an RT-VC run and has no qualification effect.
- Adverse controls reject invalid PCM, unknown or blocked targets, wrong
  geometry, incomplete manifests, relative paths, bad digests and hash
  mismatches before any processing.
- Eight release gates and eight exact blockers remain blocked with concrete
  external reopening conditions.
- Scope is checked against the dirty worktree and against commits added by this
  branch relative to the newest merge base with `origin/main` (falling back to
  `main`). An unresolved base emits `scope_base_unavailable`; a committed path
  outside `docs/task-evidence/rt-vc/` emits `base_out_of_scope_change`.

## Readiness conclusion

`DEFER` before `opt_in_adapter_exposure`. The exact external blocker is that the
pinned official RT-VC source at `9d9a55d` has no obtainable inference checkpoint
or complete weight setup, no pinned source-code license text, and no cleared
p360 dataset/license provenance. Separate content-preservation, identity,
target-voice realization and naturalness outcomes, consented cohort, metric
specification, alignment, first-output/tail timing, listening, bench validation,
exact-head review and release approval are all absent.

Reopening requires caller-owned immutable bytes, a 40-hex source revision and tree
digest for the exact licensed checkpoint and complete weight setup; written code,
checkpoint, training-data, p360, reference-voice consent, output-use and
redistribution rights; a hash-pinned isolated runtime and requirements lock; a
rights-cleared group with frozen p360 references; matched voice outcomes; and the
full independent adapter, listening, bench and release gates.

## Non-claims

No RT-VC conversion was executed. No checkpoint, complete weight setup, runtime
or audio was downloaded, vendored or read. No source-reported number is reused
as an RT-VC metric. No listening panel, human rating, predictive score or device
timing was run. No provider, descriptor, registry, default, public ABI,
`CONTRACTS.md`, shared build or CI file was changed. No board, handoff, benchmark
submission or release claim was made.

## Reproduction

Use the pinned Python 3.12.16 interpreter with bytecode writing disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --readme
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
```

Three cold-start rounds must be byte-identical before `run.py` writes anything.
The verifier repeats three cold regenerations in a temporary directory, checks
the canonical report digest sidecar, validates the README digest table below,
checks licensing, checks dirty and committed scope, and fails closed on any
mismatch.

## Digest table

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `874d6beb8970beac6e8d35aba8a083d6adfa3f5b7ceec4509179e77a41802412` | 2432 |
| `reference.py` | `446243777ef3d7e6d309d7fd34493a4717729fbf703d856dacb371af6b033cc0` | 62761 |
| `report.json` | `915f180de341fc85f71b96cef18b8465c223080cc1c5f6aa468f3a5d23b75caa` | 36454 |
| `run.py` | `0967c027ad8765a035a848c5350dbbac57ad75bafe5a03e6bb6ffce8c184790f` | 6031 |
| `test_reference.py` | `eca8387057316407cd705e601dbbb974995bd1241995ba5d661bbf90891e442c` | 13793 |
| `verify.py` | `94ba865eceb4a994940b522a8467f87bedfc622e05fd35502bdeec12b1399ef4` | 37590 |
<!-- digest-table:end -->

`contract.json` and `SOURCES.sha256` are excluded from the README table to avoid
a self-reference cycle. They are pinned in `SOURCES.sha256` and checked by
`verify.py`.
