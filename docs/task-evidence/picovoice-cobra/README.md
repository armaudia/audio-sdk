<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PICOVOICE-COBRA — Picovoice Cobra blocker evidence

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **external-adapter blocker package** for inventory
component `picovoice-cobra` (analysis profile). Picovoice Cobra is a
proprietary vendor VAD/probability engine requiring approved runtime, access
key/terms, and rights review. This workspace has **no approved public or
user-supplied Cobra runtime, access key policy approval, vendor model/library
artifacts, rights record, held-out cohort, parity output, or paced timing
evidence**. It creates **no provider registration, no descriptor/default, no
installed v0/ABI/registry/shared build/CI change, no runtime download, no
network/device use, no real corpus, and no release/benchmark claim**.

Task owner: `agent-PICOVOICE-COBRA`; reviewer: `reviewer-PICOVOICE-COBRA`.
Claim base: audio-sdk `01cc99e1de5b724a3a999e86d85f5771736197ae`; branch
`swarm/SDK-PICOVOICE-COBRA`. Depends on `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`.
Write scope is task-local only: `docs/task-evidence/picovoice-cobra/`.

## Why no result can qualify

The task row requires documenting the vendor boundary and only prototyping an
isolated adapter if an approved public or user-supplied runtime is available.
No such runtime/assets/rights are present. Source-reported/vendor-reported
scores are provenance only and are never reproduced, pooled, or qualified.
Missing or unapproved evidence never qualifies the candidate.

## Exact blockers and 8 blocked release gates

| Blocker | State | Requirement |
| --- | --- | --- |
| `vendor_runtime_absent` | absent | Approved Picovoice Cobra runtime/library with exact version/platform/SHA-256 and license/terms review. |
| `access_key_and_terms_unapproved` | absent | Approved access-key handling and vendor terms; keys never committed/logged. |
| `vendor_assets_unpinned` | absent | Exact model/library artifacts or vendor-managed immutable IDs with SHA-256 where distributable. |
| `rights_and_redistribution_uncleared` | absent | Code/runtime/model/data/output redistribution and usage rights cleared. |
| `held_out_cohort_absent` | absent | Rights-cleared, label-complete held-out cohort with frozen outputs and stratified analysis scoring. |
| `parity_and_quality_absent` | absent | Approved reference/parity outputs and analysis-profile quality evidence against exact runtime. |
| `timing_and_target_unmeasured` | absent | Paced target-device timing/resources under approved runtime. |
| `provider_intake_not_started` | absent | Opt-in external-adapter intake, descriptor/registry review, independent public-surface/release decision. |

Blocked gates (all `blocked`): `approved_runtime_and_terms`,
`artifact_identity_and_rights`, `held_out_cohort_and_labels`,
`exact_reference_or_parity_evidence`, `analysis_profile_quality`,
`paced_target_timing`, `opt_in_adapter_intake`,
`public_default_and_release`.

## Boundary

- **No runtime execution/download.** Python stdlib only. No `pvcobra`, no
  vendor SDK install, no network, no audio device, no model load/inference.
- **No secrets.** Access keys must never be committed, logged, or embedded in
  manifests/reports. The manifest contract rejects `access_key_present=true`.
- **No qualifying claim.** Synthetic controls are structural accounting only;
  they perform no VAD and cannot qualify. Source-reported scores are labeled
  as not measured here.
- **Stable TASKS identity only.** The mutable full `plan/swarm/TASKS.json` is
  never hashed. Only the linked stable row identity is pinned/gated.

## Reproduction

```sh
cd docs/task-evidence/picovoice-cobra
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 run.py all --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json`, and
`SOURCES.sha256`. `verify.py` is read-only/fail-closed, checks strict JSON,
pins, blockers/gates, boundary/scope, adverse controls, and requires 3
byte-identical cold-start regenerations.
