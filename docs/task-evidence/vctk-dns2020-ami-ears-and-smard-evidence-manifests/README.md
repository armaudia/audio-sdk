<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`VCTK, DNS2020, AMI, EARS and SMARD evidence manifests`
(`component_id=vctk-dns2020-ami-ears-and-smard-evidence-manifests`).
Acceptance profile: **Evidence**. Decision: **DEFER** before
`rights_cleared_manifests_and_release_approval`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package does **not** ingest, decode, copy, download, score, admit, release
or publish any corpus. It records a fail-closed blocker package: no
machine-readable per-corpus manifest, intended-use/rights records,
source/pair/group hash manifest, overlap-prevention record, scoring/aggregation
plan, rights-cleared subset, approval record or opt-in adapter/release decision
is present. Local research artifacts are observed by fixed path/hash metadata
only and are never admitted.

## Scope and boundary

- Task-local only under `docs/task-evidence/vctk-dns2020-ami-ears-and-smard-evidence-manifests/`.
- No provider registration, no descriptor/default change, no installed-v0/ABI/
  registry/shared build/CI behavior change.
- No real corpus/weights/runtime, no listening, no device timing, no benchmark
  or release claim.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`.

## Gates (all blocked)

1. `corpus_manifest_and_exact_identity`
2. `intended_use_and_rights_per_corpus`
3. `source_pair_group_hashes_and_overlap_prevention`
4. `scoring_cohort_aggregation_and_failed_item_policy`
5. `evidence_separation_and_controls`
6. `local_rights_cleared_subset_or_approval_record`
7. `opt_in_adapter_and_release_boundary`
8. `public_default_release_and_benchmark_claim`

## Files

- `reference.py` - stdlib-only deterministic audit/control/report model.
- `contract.json` - task contract, scope, boundary, blockers, gates.
- `report.json` - canonical machine-readable evidence report.
- `report.json.sha256` - SHA-256 sidecar for `report.json`.
- `SOURCES.sha256` - fail-closed SHA-256 manifest for pinned sources, boundary
  files and package files. It never hashes mutable full `plan/swarm/TASKS.json`;
  only stable linked-row identity is gated.
- `run.py` - deterministic regeneration/check (`report.json`, `sources`, `all`).
- `verify.py` - read-only fail-closed verifier, including 3 cold-start regen.
- `test_reference.py` - Python unittest acceptance checks.
- `*.license` - REUSE sidecars for generated/artifact files.

## Reproduction

```sh
cd docs/task-evidence/vctk-dns2020-ami-ears-and-smard-evidence-manifests
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` and `verify.py` require `SOURCE_ROOT` (workspace root containing
`audio-benchmark-platform/...` and `research/...`) and resolve `SDK_ROOT` from
the checkout. `verify.py` performs 3 fresh interpreter cold-start regenerations
and requires byte-identical report/sidecar outputs.

## Non-claims

No corpus is admitted or scored. No rights are approved. No adapter is exposed.
No public/default/release/benchmark claim is made. Missing evidence never
qualifies.
