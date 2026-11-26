<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-UNIVNET — UnivNet blocker evidence (DEFER)

Task-local, proposal-only, incomplete and not-qualified evidence for `SDK-UNIVNET`
(`component_id=univnet`, Voice profile). Decision: **DEFER**. Status:
`incomplete`. Qualification: `not_qualified`. Missing evidence never qualifies.

This package writes only `docs/task-evidence/univnet/`. It contains no UnivNet
source, checkpoint, runtime, feature tensor, generated waveform, corpus,
listening result, device timing, benchmark, provider registration, SDK
API/ABI/default/descriptor/registry/shared-build/CI change, or release claim.

## Exact blocker

Inventory evidence (`plan/INVENTORY.json`, `component_id=univnet`) records
UnivNet as "not run" in `research/accent-conversion-20261101/README.md`: general
vocoder family, no task-compatible acoustic model/checkpoint pair acquired.
Fixed absence probes in this package confirm no exact upstream UnivNet source
revision, LICENSE/NOTICE bundle, immutable archive digest, checkpoint/weights,
runtime lock/install digest, rights/consent/output-use review, rights-cleared
feature cohort, or approved reference parity/protocol is present. No artifact
was downloaded or fabricated.

## What this package verifies

- Stable linked-row identity only: `SDK-UNIVNET` + dependency rows by
  `{id,title,component,mode,repository,depends_on}`. The mutable shared board is
  not hashed and cannot gate or promote claims.
- Pinned read-only inputs: accent-conversion research note, INVENTORY,
  VERIFICATION Voice profile, audio-sdk plan README, and unchanged SDK boundary
  files (`CONTRACTS.md`, v0 headers, CMake, REUSE, CI, README).
- Fixed absence probes (workspace/worktree/home cache, no recursive walk). Any
  present probe fails closed with `artifact_present_reopen_required`.
- Fail-closed caller-supplied manifest admission schema. It rejects malformed,
  missing, invalid, out-of-range, non-integer, non-canonical, aliased, duplicate,
  and nonfinite cases; one synthetic schema control is accepted as
  `synthetic_schema_control_not_evidence` with `qualifies=false`. No feature,
  audio, weight, model, or network path is used.
- Voice-profile accounting: 8 blocked requirements, 4 blocked quality outcomes,
  4 blocked timing rows, 8 blocked release gates.

## Blocked release gates

| Gate | Status | Reopen condition |
|---|---:|---|
| RG-01 Source revision and license provenance | blocked | Exact upstream UnivNet source, 40-hex revision, LICENSE/NOTICE and immutable archive digest reviewed. |
| RG-02 Checkpoint identity and geometry | blocked | Immutable checkpoint/weights with filename, byte count, SHA-256, format and mel/conditioning geometry verified offline. |
| RG-03 Rights and output terms | blocked | Reviewed source/weight/model-card/output terms settle attribution, redistribution, commercial and output use. |
| RG-04 Pinned runtime and deterministic load | blocked | Locked offline runtime with install digest loads pinned assets deterministically with fixed seed and host profile. |
| RG-05 Consent, reference availability and output use | blocked | Signed consent, reference-availability, output-use and commercial-terms records exist. |
| RG-06 Frozen cohort and controls | blocked | Rights-cleared frozen cohort with exact geometry, hashes, language/speaker groups and matched/mismatched/zero controls. |
| RG-07 Separate content, identity, naturalness and listening | blocked | Approved protocol produces reviewed content, conditional identity/similarity, naturalness, alignment and timing outcomes. |
| RG-08 Independent review and release boundary | blocked | Exact-head independent review confirms no default/ABI/shared-build/CI/provider/registry change and no unqualified claim. |

## Non-claims

No source/weights/runtime execution, no audio/feature read, no quality/listening,
no alignment/timing, no device/resource benchmark, no consent/rights clearance,
no provider registration/default/ABI/shared-build/CI change. Missing evidence is
not qualifying.

## Reproduction

```sh
python3 docs/task-evidence/univnet/run.py all
python3 -m unittest -v docs.task-evidence.univnet.test_reference
python3 docs/task-evidence/univnet/verify.py
python3 -m reuse lint
```
