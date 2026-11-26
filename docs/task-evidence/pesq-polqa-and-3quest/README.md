<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PESQ-POLQA-AND-3QUEST — PESQ, POLQA and 3QUEST blocker

**Disposition: `DEFER` / `proposal_only_incomplete` / `incomplete` / `not_qualified`.** This package is a bounded, deterministic, task-local evidence/control package for inventory component `pesq-polqa-and-3quest` (Evidence profile, `research-control`). The exact licensed PESQ, POLQA and 3QUEST scorer implementations/runtimes/entitlements, rights-cleared cohort, parity/reference outputs, and approved execution/review path are absent. It creates **no provider registration, no installed-v0/ABI/registry/default/shared-build/CI change, no real corpus/weights/runtime download, no listening, no device timing, no benchmark, and no release claim**.

Task owner: `agent-PESQ-POLQA-AND-3QUEST`; reviewer: `reviewer-PESQ-POLQA-AND-3QUEST`. Claim base: audio-sdk `fb0ee3e326beb269c87358251aceb61352329635`; branch `swarm/SDK-PESQ-POLQA-AND-3QUEST`. Depends on `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`. Write scope is only `docs/task-evidence/pesq-polqa-and-3quest/`.

## Exact blocker / missing artifacts and rights

| Required artifact / right | State | Why no result can qualify |
|---|---|---|
| PESQ license/entitlement + exact runtime | absent | No approved PESQ license, binary, mode contract, or digest exists here. |
| POLQA license/entitlement + exact runtime | absent | No approved POLQA license, binary, mode contract, or digest exists here. |
| 3QUEST license/entitlement + exact runtime | absent | No approved 3QUEST license, binary, mode contract, or digest exists here. |
| Pinned scorer identities | absent | No immutable revision/SHA-256 for scorer binaries/sources/command contracts. |
| Rights-cleared cohort | absent | No item-level pinned, rights-cleared reference/degraded cohort with declared mode/sample rate/alignment. |
| Parity/reference outputs | absent | No approved scorer outputs/parity vectors; no local execution result exists. |
| Pinned isolated runtime | absent | Incidental system tools/environments cannot qualify. |
| Independent review/admission | absent | No review/release/admission decision allows processor or benchmark exposure. |

Missing evidence is never promoted to pass, partial qualification, or capability. Historical/source-reported values (including the 2026-10-29 DNS2020 30-item Speex PESQ replay summary) are **provenance only**, not reproduced here, not qualified, and not release evidence.

## Evidence-profile controls (task-local)

The package enforces deterministic controls only:
- strict JSON parsing (reject duplicate keys, non-object roots, nonfinite JSON constants);
- exact pin checks for read-only source/boundary documents;
- stable linked-row task identity gate (no hash of mutable full `plan/swarm/TASKS.json`);
- caller-supplied scorer manifest validation only (`validate_only_no_execution_no_network`, reject before processing on missing/invalid fields);
- deterministic synthetic PCM accounting/control fixture (not speech, not a score);
- adverse/missing/invalid/nonfinite rejection cases;
- 3 cold-start byte-identical regenerations checked by `verify.py`.

## Eight blocked release gates

| Gate | Status |
|---|---|
| `licensed_scorer_entitlements` | blocked |
| `exact_scorer_identity` | blocked |
| `pinned_runtime_environment` | blocked |
| `rights_cleared_cohort` | blocked |
| `exact_reference_parity` | blocked |
| `evidence_profile_controls` | blocked |
| `processor_exposure_review` | blocked |
| `public_benchmark_release` | blocked |

Machine-readable disposition: `decision="DEFER"`, `status="proposal_only_incomplete"`, `evidence_status="incomplete"`, `qualification.status="not_qualified"`, `qualification.candidate_qualified=false`, `qualification.no_missing_result_qualifies_candidate=true`, all eight gates `blocked`.

## Boundary / non-claims

No PESQ/POLQA/3QUEST binary, license, runtime, or entitlement is present or executed. No score/rating/MOS/intelligibility/benchmark/device-timing/listening result is fabricated. No real audio/corpus/rights-cleared media is consumed or redistributed. No network/download/asset staging occurs. No provider registration, installed-v0/ABI/registry/default/shared-build/CI change is made. Historical/source-reported values are provenance only and not reproduced/qualified here.

## Files

- `reference.py` - stdlib-only deterministic reference/builder/validators.
- `contract.json` - machine-readable contract/disposition/gates/blockers.
- `report.json` - canonical machine-readable evidence report.
- `report.json.sha256` - SHA-256 sidecar for canonical report bytes.
- `SOURCES.sha256` - SHA-256 pins for read-only source/worktree/package files; mutable full `TASKS.json` is never hashed.
- `run.py` - regenerate/check report, contract, sources.
- `verify.py` - read-only fail-closed verifier with 3 cold-start regenerations.
- `test_reference.py` - unit/acceptance tests.
- `*.license` - REUSE sidecars for JSON/SHA256/manifest files.

## Reproduce

```sh
cd docs/task-evidence/pesq-polqa-and-3quest
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```
