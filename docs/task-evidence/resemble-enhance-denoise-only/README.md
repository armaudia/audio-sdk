<!-- SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RESEMBLE-ENHANCE-DENOISE-ONLY — Resemble Enhance denoise-only blocker/readiness evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`resemble-enhance-denoise-only` (`SDK-RESEMBLE-ENHANCE-DENOISE-ONLY`). Profile:
**Enhancement** (`plan/swarm/VERIFICATION.md`). Decision: **DEFER** before
`opt_in_provider_or_reference_exposure`; `evidence_status=incomplete`;
`qualification.status="not_qualified"`.

This package records an exact blocker/readiness boundary because the required
exact licensed source/weights/runtime are **not present** in this worktree. It
does **not** download, copy, build, load, execute, vendor, or redistribute
Resemble Enhance source, weights, checkpoints, packages, runtimes, or audio. No
result qualifies the candidate. No provider registration, installed-v0/ABI/
registry/default/shared-build/CI change, real corpus/weights/runtime, listening,
device-timing, benchmark, or release claim is made.

## Exact blockers

The exact blockers are recorded verbatim in `contract.json` and `report.json`:

1. Exact Resemble Enhance denoise-only source revision/archive and immutable
   license/provenance are not staged in this worktree; the census identifies an
   official repository with `--denoise_only` and MIT code, but no pinned commit,
   archive digest, or complete source snapshot is present here.
2. Exact pretrained weights/assets, model-card or runtime terms, and
   redistribution/product-use clearance for the denoise-only path are absent; no
   weight, checkpoint, package, or runtime was downloaded, copied, built, or
   executed.
3. No exact runnable runtime, reference-output parity vector, or task-matched
   enhancement evidence exists for this candidate in this worktree; no real
   audio, listening, device timing, benchmark, or release claim is produced.
4. No rights-cleared real cohort, independent listening, target-runtime
   timing/memory/resource evidence, opt-in adapter/provider intake, or
   public/default decision exists; every release gate remains blocked.

## Stable linked-row identity

This package gates only stable linked-row identity fields from
`plan/swarm/TASKS.json` (id, title, repository, mode, depends_on, component,
deliverable, acceptance, evidence). It **never** hashes the mutable full
`TASKS.json`. The projection and SHA-256 are recorded in
`report.json:linked_row_identity`.

## Enhancement profile application

| Requirement | Status |
|---|---|
| Identity/noisy control and task-matched baseline | blocked - no exact runtime/assets |
| Paired SI-SDR and STOI where permitted clean refs exist | blocked - no rights-cleared real cohort or exact runtime |
| Clean-speech preservation, peaks, invalid outputs | blocked |
| Unpaired predictive/listening as separately labeled evidence | blocked |
| Alignment, state, memory, content/availability timing | blocked |

Missing/invalid/nonfinite/adverse schema cases are fail-closed and non-qualifying;
see `report.json:adverse_cases`.

## Files

| File | Purpose |
|---|---|
| `README.md` | Scope, blockers, profile, reproduction. |
| `contract.json` | Machine-readable contract and blocker/gate record. |
| `reference.py` | Deterministic stdlib-only reference/builder. |
| `report.json` | Canonical machine-readable report. |
| `report.json.sha256` | SHA-256 of `report.json`. |
| `SOURCES.sha256` | Pinned source/sdk/task file digests. |
| `verify.py` | Read-only strict verifier. |
| `test_reference.py` | Deterministic unit tests. |
| `run.py` | 3x/byte-identical regeneration entrypoint. |
| `*.license` | REUSE sidecars for non-commentable artifacts. |

## Reproduction

All commands run from this evidence directory. No network, no weights, no
runtime, no audio.

```sh
cd docs/task-evidence/resemble-enhance-denoise-only
python3 run.py
python3 -m unittest -v test_reference.py
python3 verify.py
```

For 3x byte-identical regeneration:

```sh
for i in 1 2 3; do python3 run.py; sha256sum report.json report.json.sha256 SOURCES.sha256; done
```

## Gates

All eight release gates are blocked:

1. `source_revision_archive_and_license_provenance`
2. `weights_assets_and_terms`
3. `exact_runtime_reproduction`
4. `native_or_caller_boundary`
5. `real_cohort_enhancement_evidence`
6. `independent_listening_and_preservation`
7. `target_runtime_timing_memory_resources`
8. `opt_in_intake_and_public_surface`

Reopen only when the exact missing artifact/rights/runtime/evidence requirements
in `contract.json:reopening_conditions` are satisfied and independently reviewed.
Until then the candidate remains DEFER / incomplete / not_qualified.
