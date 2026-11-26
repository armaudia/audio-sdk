<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOCOS-BWE — Vocos-BWE blocker evidence (DEFER)

Task-local, proposal-only, incomplete and not-qualified evidence for `SDK-VOCOS-BWE`
(`component_id=vocos-bwe`, Restoration profile). Decision: **DEFER**. Status:
`incomplete`. Qualification: `not_qualified`. Missing evidence never qualifies.

This package writes only `docs/task-evidence/vocos-bwe/`. It contains no Vocos-BWE
source, checkpoint, runtime, feature tensor, generated waveform, corpus,
listening result, device timing, benchmark, provider registration, SDK
API/ABI/default/descriptor/registry/shared-build/CI change, or release claim.
Generic Vocos vocoder evidence is **not** Vocos-BWE bandwidth-extension evidence.

## Exact blocker

Inventory evidence (`plan/INVENTORY.json`, `component_id=vocos-bwe`) records
Vocos-BWE as `unavailable/blocked`: "No exact Vocos-BWE model/checkpoint/adapter;
generic vocoder evidence is not bandwidth extension." Candidate-matrix and
research report pins in this package preserve that finding. Fixed absence probes
confirm no exact Vocos-BWE source revision, LICENSE/NOTICE bundle, immutable
archive digest, checkpoint/weights, runtime lock/install digest, rights/consent/
output-use review, rights-cleared restoration cohort, or approved reference
parity/protocol is present. No artifact was downloaded or fabricated.

## What this package verifies

- Stable linked-row identity only: `SDK-VOCOS-BWE` + dependency rows by
  `{id,title,component,mode,repository,depends_on}`. The mutable shared board is
  not hashed and cannot gate or promote claims.
- Pinned read-only inputs: candidate matrix, transform-spatial/denoise reports,
  INVENTORY, VERIFICATION Restoration profile, audio-sdk plan README, unchanged
  SDK boundary files, and merged sibling `docs/task-evidence/vocos/report.json`.
- Fixed absence probes (workspace/worktree/home cache, no recursive walk). Any
  present probe fails closed with `artifact_present_reopen_required`.
- Fail-closed caller-supplied manifest admission schema. It rejects malformed,
  missing, invalid, out-of-range, non-integer, non-canonical, aliased, duplicate,
  and nonfinite cases; one synthetic schema control is accepted as
  `synthetic_schema_control_not_evidence` with `qualifies=false`. No audio,
  feature, weight, model, or network path is used.
- Restoration-profile accounting: 3 blocked requirements, 4 blocked quality
  outcomes, 4 blocked timing rows, 8 blocked release gates.

## Blocked release gates

| Gate | Status | Reopen condition |
|---|---:|---|
| RG-01 Source revision and license provenance | blocked | Exact Vocos-BWE source, 40-hex revision, LICENSE/NOTICE and immutable archive digest reviewed. |
| RG-02 Checkpoint identity and geometry | blocked | Immutable checkpoint/weights with filename, byte count, SHA-256, format and narrowband/BWE geometry verified offline. |
| RG-03 Rights and output terms | blocked | Reviewed source/weight/model-card/output terms settle attribution, redistribution, commercial and output use. |
| RG-04 Pinned runtime and deterministic load | blocked | Locked offline runtime with install digest loads pinned assets deterministically with fixed seed and host profile. |
| RG-05 Consent, reference availability and output use | blocked | Signed consent, reference-availability, output-use and commercial-terms records exist. |
| RG-06 Frozen cohort and controls | blocked | Rights-cleared frozen cohort with exact geometry, hashes, degradation/bandwidth strata and matched controls. |
| RG-07 Separate restoration quality and timing | blocked | Approved protocol produces reviewed restoration quality, concealment/validity, peak/timing and baseline comparisons. |
| RG-08 Independent review and release boundary | blocked | Exact-head independent review confirms no default/ABI/shared-build/CI/provider/registry change and no unqualified claim. |

## Non-claims

No Vocos-BWE source/weights/runtime execution, no audio/feature read, no
restoration quality/listening, no alignment/timing, no device/resource
benchmark, no consent/rights clearance, no provider registration/default/ABI/
shared-build/CI change. Generic Vocos vocoder evidence is not BWE evidence.
Missing evidence is not qualifying.

## Reproduction

```sh
python3 docs/task-evidence/vocos-bwe/run.py all
python3 -m unittest -v docs.task-evidence.vocos-bwe.test_reference
python3 docs/task-evidence/vocos-bwe/verify.py
python3 -m reuse lint
```
