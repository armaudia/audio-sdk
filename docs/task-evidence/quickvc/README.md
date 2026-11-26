<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-QUICKVC — caller-supplied-asset feasibility evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`QuickVC` (`component_id=quickvc`). The acceptance profile is **voice**, assigned
by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. A missing result never qualifies the
candidate.

This package does **not** implement an accent converter. The external research
record states that `QuickVC / ContentVec` was **not tested as standalone
systems**, describes them as generic VC architecture and content-encoder
components, and records that no accent-target checkpoint was available. A
generic LLVC QuickVC architecture checkout is present at pinned MIT revision
`1627c5d358cf9bb2b92b0ccc513d8b36807c923d`, but it is source provenance only:
it is not an accent converter, it is not executed, and no checkpoint or encoder
snapshot is present.

The package models the boundary a future caller would have to satisfy using the
`CONTRACTS.md` `as_asset_v0` rule: an asset ID, byte count, SHA-256 and
`storage=external`, supplied by the caller. The manifest is validated as a
shape-only intake control; it never supplies absent bytes, rights, consent,
matched evidence or qualification. The only admitted request is an
identity-source control at the installed public v0 geometry (16 kHz mono
`float32`, 160 samples per frame). Candidate conversion targets fail closed.

## What is verified

- The linked task row's stable identity (`id`, `title`, `mode`, `repository`,
  `component`) matches this package; the mutable full `TASKS.json` is never
  hashed or pinned.
- Read-only source pins match the accent record, inventory records, verification
  profile and generic source checkout provenance.
- Boundary pins prove that no provider file, descriptor, registry, default, ABI,
  `CONTRACTS.md`, shared build or CI file changed.
- Fixed absence probes prove that no QuickVC checkpoint, HuBERT/ContentVec
  encoder, accent target, rights record, cohort, runtime or reference audio is
  present.
- A deterministic synthetic identity control exercises only the declared public
  v0 geometry. It is not a QuickVC run and has no qualification effect.
- Adverse controls reject invalid PCM, unknown or candidate targets, wrong
  geometry, incomplete manifests, relative paths, bad digests and hash
  mismatches before any processing.
- Eight release gates and eight exact blockers remain blocked with concrete
  external reopening conditions.
- Scope is checked against the dirty worktree and against commits added by this
  branch relative to the newest merge base with `origin/main` (falling back to
  `main`). An unresolved base emits `scope_base_unavailable`; a committed path
  outside `docs/task-evidence/quickvc/` emits `base_out_of_scope_change`.

## Readiness conclusion

`DEFER` before `opt_in_adapter_exposure`. No accent-target QuickVC checkpoint or
exact HuBERT/ContentVec encoder snapshot is available under cleared rights, and
the accent census explicitly records QuickVC/ContentVec as untested standalone
components. The generic MIT-licensed LLVC source at `1627c5d` cannot by itself
produce converted speech. Separate text/semantic, identity, accent-target and
naturalness outcomes, consented cohort, metric specification, alignment,
first-output/tail timing, listening, bench validation, exact-head review and
release approval are all absent.

Reopening requires caller-owned immutable bytes and a 40-hex source revision for
the exact licensed checkpoint and encoder; written code, weight, training-data,
reference-voice consent, output-use and redistribution rights; a hash-pinned
isolated runtime; a rights-cleared language/L1/speaker-stratified cohort with
frozen target-accent references; matched voice outcomes; and the full
independent adapter, listening, bench and release gates.

## Non-claims

No QuickVC or ContentVec conversion was executed. No checkpoint, encoder,
config, model byte or audio was downloaded or read. No source-reported LLVC
number is reused as a QuickVC metric. No listening panel, human rating,
predictive score or device timing was run. No provider, descriptor, registry,
default, public ABI, `CONTRACTS.md`, shared build or CI file was changed. No
board, handoff, benchmark submission or release claim was made.

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
The verifier repeats a cold regeneration in a temporary directory, checks the
canonical report digest sidecar, validates the README digest table below,
checks licensing, checks dirty and committed scope, and fails closed on any
mismatch.

## Digest table

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `9afd448ba3dffa1d28303aa4b5558e9e822cf501fb1969d6eb0fbba754582ffa` | 2234 |
| `reference.py` | `35a266709b183970bfabef7040c030193333d110369d85549c499882895e60b2` | 59870 |
| `report.json` | `62514a8b250f291b9e1df0ec6a9da5eb61a65d0eaf31801fd0df01c803fb4948` | 34868 |
| `run.py` | `64570b67819b5f04223f7f8282f517ffd36f2358fb16113998a1e9a74568aa0f` | 6033 |
| `test_reference.py` | `b4d18eb637d6e4b9e618ee5c01554bb437474f3023a477df1fca109269cccc64` | 13818 |
| `verify.py` | `5d3ee38cfc2c29ba411d74ec5b0838a5866643b20aa9590272e4afaecef45a6d` | 36476 |
<!-- digest-table:end -->

`contract.json` and `SOURCES.sha256` are excluded from the README table to avoid
a self-reference cycle. They are pinned in `SOURCES.sha256` and checked by
`verify.py`.
