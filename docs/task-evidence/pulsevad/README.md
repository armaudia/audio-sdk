<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PULSEVAD — PulseVAD blocker evidence

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility blocker package** for inventory component
`pulsevad` (analysis profile). PulseVAD is an upstream tiny causal VAD candidate
reported as a 2,118-parameter model with 200 ms non-overlapping windows and
ONNX/TorchScript/C assets. This workspace has **no pinned source revision, no
reviewed license text, no exact runtime/weights/graph artifact, no
rights-cleared cohort, no parity output, and no paced timing evidence**. It
creates **no provider registration, no descriptor/default, no installed
v0/ABI/registry/shared build/CI change, no runtime download, no network/device
use, no real corpus, and no release/benchmark claim**.

Task owner: `agent-PULSEVAD`; reviewer: `reviewer-PULSEVAD`. Claim base:
audio-sdk `80dc1fb371e1846a5d50f5b28c955ab92bfcbe46`; branch
`swarm/SDK-PULSEVAD`. Depends on `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`,
`SDK-FND-PROVIDER`. Write scope is task-local only:
`docs/task-evidence/pulsevad/`.

## Why no result can qualify

The task row requires verifying runnable source, exact assets, permitted scope,
task geometry and matched evidence before reproducing the exact model/runtime as
a caller-supplied-asset reference. No such pinned source/runtime/assets/rights
are present. Source-reported/upstream-reported scores are provenance only and
are never reproduced, pooled, or qualified. Missing or unapproved evidence never
qualifies the candidate.

## Exact blockers and 8 blocked release gates

| Blocker | State | Requirement |
| --- | --- | --- |
| `source_revision_unpinned` | absent | Exact reviewed PulseVAD source revision with immutable commit, license text, and per-file digests. |
| `runtime_or_asset_absent` | absent | Approved runtime or exact ONNX/TorchScript/C asset with platform, version, SHA-256, and execution contract. |
| `weights_or_graph_unpinned` | absent | Exact model/weight/graph identity with SHA-256, byte count, and input/output contract. |
| `rights_and_redistribution_uncleared` | absent | Code/model/data/output redistribution and usage rights cleared. |
| `held_out_cohort_absent` | absent | Rights-cleared, label-complete held-out cohort with frozen outputs and stratified analysis scoring. |
| `parity_and_quality_absent` | absent | Approved reference/parity outputs and analysis-profile quality evidence against exact runtime. |
| `timing_and_target_unmeasured` | absent | Paced target-device timing/resources including 200 ms window buffering implications under approved runtime. |
| `provider_intake_not_started` | absent | Opt-in adapter/provider intake, descriptor/registry review, independent public-surface/release decision. |

Blocked gates (all `blocked`): `exact_source_and_license`,
`artifact_identity_and_rights`, `held_out_cohort_and_labels`,
`exact_reference_or_parity_evidence`, `analysis_profile_quality`,
`paced_target_timing`, `opt_in_adapter_intake`,
`public_default_and_release`.

## Boundary

- **No runtime execution/download.** Python stdlib only. No PulseVAD import,
  no vendor SDK install, no network, no audio device, no model load/inference.
- **No qualifying claim.** Synthetic controls are structural accounting only;
  they perform no VAD and cannot qualify. Source-reported scores are labeled
  as not measured here.
- **Stable TASKS identity only.** The mutable full `plan/swarm/TASKS.json` is
  never hashed. Only the linked stable row identity is pinned/gated.

## Reproduction

```sh
cd docs/task-evidence/pulsevad
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 run.py all --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json`, and
`SOURCES.sha256`. `verify.py` is read-only/fail-closed, checks strict JSON,
pins, blockers/gates, boundary/scope, adverse controls, and requires 3
byte-identical cold-start regenerations.
