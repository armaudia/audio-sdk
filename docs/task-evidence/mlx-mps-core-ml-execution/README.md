<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MLX-MPS-CORE-ML-EXECUTION — accelerator execution blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the
MLX / MPS / Core ML execution feasibility row. It is **not** an accelerator
runtime integration. No MLX, MPS or Core ML runtime, wheel, binding, model,
compiled Core ML artifact, preprocessing asset, corpus, waveform, inference,
CPU-parity comparison, device-timing measurement, benchmark or release claim is
present. **No result here qualifies any accelerator.**

The structured inventory marks `mlx-mps-core-ml-execution` as
`evidence_status=considered`, disposition `sdk-tool`, with the **Tool**
acceptance profile (`verification_profile: tool`, `plan/INVENTORY.json`). The
task row is `mode=feasibility`; its plan note is *"Treat each accelerator as a
separate runtime, with CPU parity and availability evidence for each."* The
deliverable asks for runnable source, exact assets, permitted scope, task
geometry and matched evidence before an adapter, fixture or tooling entry point
is added. None of those prerequisites exists.

Task owner: `agent-MLX-MPS-CORE-ML-EXECUTION`; reviewer:
`reviewer-MLX-MPS-CORE-ML-EXECUTION`. Claim base: audio-sdk
`7dc9c84b2ed963ecda895194b19e8d8979a2f748`; branch
`swarm/SDK-MLX-MPS-CORE-ML-EXECUTION`. Write scope is only
`docs/task-evidence/mlx-mps-core-ml-execution/`.

## Exact external blocker

MLX, MPS and Core ML are three **separate** runtimes. Each one lacks an exact
licensed runtime identity, an exact model/asset bundle, CPU parity evidence and
availability evidence.

| Runtime | Exact state on this task |
| --- | --- |
| MLX | No `ml-explore/mlx` checkout or wheel at an immutable 40-hex revision, version, install root, lock SHA-256, offline load path or reviewed license text. No MLX model. No CPU parity, availability or device-timing result. The pinned RE-USE adapter names an unpinned community Swift/MLX port and absent NVIDIA weights; it is not generic MLX execution evidence. |
| MPS | No PyTorch build providing the MPS backend, no wheel install root, version, lock, Metal device profile or reviewed license text. No `torch`, no Metal device query, no model, no CPU parity, availability or device-timing result. |
| Core ML | No pinned Core ML deployment target, toolchain/binding identity (`coremltools` or Swift), version lock, reviewed license record or compiled model artifact. A system Xcode/Core ML toolchain may be **observed** on the host; it is not a pinned runtime and is **not admitted**. The only sibling execution record is an adverse ONNX Runtime Core ML provider trial that the sibling record rejects for concurrent use. |

No fixed path in this workspace contains an admitted accelerator runtime root,
lock, license text, model file, compiled model or preprocessing asset. Nothing is
downloaded, vendored, staged, mirrored or inferred from a URL. Consequently:

- runtime version, install location, provenance and license cannot be pinned;
- model, config, preprocessing and per-file SHA-256 cannot be pinned;
- sample rate, tensor layout, precision, frame hop and preprocessing contract are
  **unestablished** for any accelerator and are not invented;
- no accelerator output exists, so no CPU parity, exact-tolerance comparison,
  cold/warm availability, device timing, memory, throughput or RTF value is
  reported;
- source-reported or sibling-recorded numbers are labelled with their original
  scope and are never presented as this task's result;
- missing, adverse, invalid and nonfinite evidence is never promoted to a pass,
  partial qualification or capability claim.

## Sibling accelerator/execution evidence (adverse, not inherited)

The pinned sibling record
`realtime-audio-library/evaluation/cpu_saving_20261031/README.md` screened the
locally installed **ONNX Runtime 1.31.1 Core ML execution provider** on one
DPDFNet graph. It partitioned **312 of 319** nodes into four Core ML partitions.
A temporary patched native build completed **80 frames for one stream**
(recorded p50/p95/p99/max 3.40/3.89/4.01/4.02 ms, no paired CPU baseline). The
eight-stream and sixteen-stream native runs failed with
`GetElementType is not implemented` and queue/deadline failures. The sibling
record explicitly **rejects this configuration for concurrent library use**.

This package records that as `HIST-01`, with `admitted_as_result=false`,
`paired_cpu_baseline=false`, `reproducible_library_build=false` and
`concurrent_use_rejected=true`. It is **not** MLX, MPS or Core ML qualification,
not a speedup, and not a current-runtime measurement. The DPDFNet graph, local
ONNX Runtime wheel and patched build are absent, so the trial cannot be rebuilt
here.

The pinned `adapters/reuse-mlx/README.md` names `nvidia/Real-time_RE-USE` at
`4c0c186272ca853cd18d832fc5c28777b62f32d1` and the community
`PositiveLoss/re-use-swift-mlx` port at
`362be1ade00c3fcc534639df1d10c72d7e4a9e02`, requires `model.safetensors`, and
targets Swift 6.1+, macOS 14+ and Apple Silicon. It is an offline adapter for one
voice checkpoint, not a pinned generic MLX runtime, and its weights are absent.
It is recorded as `HIST-02` and is not inherited.

No MPS execution record exists (`HIST-03`).

| Missing artifact | Exact requirement |
| --- | --- |
| MLX runtime | `ml-explore/mlx` at an immutable 40-hex commit with version, wheel/source install root, offline load path, lock SHA-256 and reviewed license text. |
| MPS runtime | The exact PyTorch build providing the MPS backend at an immutable 40-hex commit with version, wheel install root, lock SHA-256, reviewed license text and a recorded Metal device profile. |
| Core ML runtime | An exact Core ML deployment target with pinned toolchain and binding identity (`coremltools` or Swift), version, lock SHA-256, reviewed license text and a compiled model artifact with SHA-256. An OS framework observation is not admission. |
| Model and assets | The exact model file set, config and preprocessing asset with per-file byte count and SHA-256 at an immutable revision, after a weights-only inspection. |
| CPU parity | A deterministic CPU reference input and output hash per accelerator with an exact declared tolerance and per-runtime comparisons. |
| Availability | An exact host/device profile with cold and warm availability, device-timing harness, deadline budget and recorded misses for each runtime. |
| Rights | Reviewed runtime licenses, model and training-data terms, output use, redistribution and per-runtime derivative-output approval. |

The machine-readable record is `report.json` → `runtime_probe`,
`absence_evidence`, `historical_evidence`, `required_artifacts`,
`exact_blockers`, `tool_profile` and `gates`. `contract.json` carries the same
disposition, pins, scope and all eight blocked release gates.

## What this package verifies

1. **Fixed absence and host observation.** Fixed workspace/worktree probe roots
   and fixed home-cache probe roots are checked for admitted MLX, MPS and Core ML
   runtimes; no recursive walk is performed. All admitted roots are absent.
   `reference.build_report()` and `verify.py` fail closed if any admitted root
   later appears. Import availability is recorded **without importing** the
   package. Host OS/architecture and Xcode/Core ML toolchain presence are
   recorded as observations only, with `observation_is_admission=false`.
2. **Stable pins.** The reviewed planning records, the structured inventory, the
   pinned RE-USE adapter, the pinned sibling Core ML trial artifacts and the SDK
   boundary files are pinned by SHA-256. These are read-only provenance inputs,
   not execution evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local accelerator-execution manifest
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted model files, unresolved
   tokens, non-integral or out-of-range integers, invalid runtime IDs,
   unavailable accelerators, inexact parity, unmeasured availability, unverified
   controls and false rights are rejected. One synthetic structural control is
   accepted to prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control` and `qualifies=false`.
5. **Tool profile accounting.** Version/install/provenance, clean package,
   typical CLI/API use, caller-owned inputs, malformed inputs, missing optional
   selections, compile/build separation, synthetic runtime evidence and measured
   workload support are each recorded as **blocked**, separately for MLX, MPS
   and Core ML.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, `scripts/ci.py`, the CI workflow and
   `.gitattributes` are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No provider is
   installed or registered; no descriptor, default, ABI, shared build, CI, board
   or handoff change is made.

## Tool profile application

| Tool requirement | Status here | Evidence |
| --- | --- | --- |
| Record version, install location and provenance | blocked | No MLX, MPS or Core ML runtime version, install root, lock or provenance exists. |
| Verify a clean checkout or extracted package | blocked | No extracted accelerator runtime package exists. |
| Run one typical CLI/API use | blocked | No model or compiled Core ML artifact exists. |
| Verify caller-owned inputs | blocked | No buffer/asset ownership test exists on a pinned runtime. |
| Reject malformed inputs | blocked | No malformed-input control exists. |
| Report missing optional selections | blocked | No missing-optional-selection control exists. |
| Separate compile/build and synthetic runtime evidence | blocked | Neither exists on a pinned runtime. |
| Produce measured workload support | blocked | No paced workload, memory or resource measurement exists. |
| MLX CPU parity and availability | blocked | No MLX runtime, reference or observation exists. |
| MPS CPU parity and availability | blocked | No MPS runtime, Metal query, reference or observation exists. |
| Core ML CPU parity and availability | blocked | No pinned Core ML runtime/model; the sibling trial is adverse and rejected. |
| Keep runtimes separate | blocked | No per-runtime result exists; pooling remains prohibited. |

## Admission contract (task-local; not an SDK or accelerator contract)

The schema is `audio-sdk/accelerator-execution-manifest/0.1`. Unknown and
missing fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths,
duplicate or unsorted model files, unresolved tokens, non-integral or
out-of-range integers, invalid runtime IDs, unavailable accelerators, inexact
parity, unmeasured availability, unverified Tool controls and any false right
are rejected. The one accepted control is synthetic and never qualifies.
Admission never loads a model, imports a runtime, reads audio or measures a
device.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `RG-01` | Exact licensed runtime identity pinned separately for MLX, MPS and Core ML | blocked |
| `RG-02` | Exact model/config/preprocessing assets and rights pinned | blocked |
| `RG-03` | CPU parity per accelerator with exact tolerance | blocked |
| `RG-04` | Availability and device timing per runtime on the exact host | blocked |
| `RG-05` | Tool controls: clean install, typical use, caller-owned inputs, malformed inputs, missing optional selections | blocked |
| `RG-06` | Compile/build, synthetic runtime and measured workload separated and not pooled | blocked |
| `RG-07` | Opt-in tool/provider intake and independent review | blocked |
| `RG-08` | Release approval | blocked |

## Pinned source and boundary inputs (SHA-256)

`source:` paths are relative to the workspace root; other paths are relative to
the SDK worktree. Exact digests and byte verification live in
`SOURCES.sha256` and `report.json`; this table lists roles only.

| Pinned input | Role |
| --- | --- |
| `source:adapters/reuse-mlx/README.md` | RE-USE Swift/MLX adapter scope and source-reported revisions |
| `source:adapters/reuse-mlx/adapter.json` | Adapter protocol identity (`nvidia-reuse-swift-mlx-cli-v1`) |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | Structured row and Tool profile |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | Runtime and tooling inventory context |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | Unchanged plan and build surface |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | Tool acceptance profile |
| `source:realtime-audio-library/accelerator_options.md` | Accelerator ownership options |
| `source:realtime-audio-library/evaluation/cpu_saving_20261031/README.md` | Adverse sibling Core ML trial |
| `source:realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/*` | Trial JSON, patch and recorded failure |
| `source:realtime-audio-library/evaluation/performance_investigation_20261031/decision_log.md` | Core ML provider rejection decision |
| `CONTRACTS.md` | Unchanged public contract |
| `api/include/audio_sdk/provider_v0.h` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | Unchanged session facade |
| `CMakeLists.txt` / `scripts/ci.py` / `REUSE.toml` / CI | Unchanged build, CI and licensing |

`verify.py` fails closed on a missing, stale, malformed, duplicated or extra
pin, on any worktree change outside this directory, and on any cold-start byte
difference.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `LICENSES.md` | Licensing and asset-rights notes. |
| `contract.json` | Strict machine-readable `decision="DEFER"`, `proposal_only` / `incomplete`, `qualification.status="not_qualified"`, eight blocked gates, seven exact blockers and the admission contract. |
| `reference.py` | Strict validators, fixed probes, stable board identity, admission controls and canonical report/contract builders. |
| `run.py` | Regenerates contract, report, digest sidecar and manifest three times and requires byte-identical output. |
| `report.json` / `report.json.sha256` | Canonical evidence and its digest. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs. |
| `test_reference.py` | Deterministic unittest acceptance suite (no skips, no network). |
| `verify.py` | Read-only strict JSON, pin, profile, licensing, scope and three cold-start regeneration verifier. |
| `*.json.license`, `*.sha256.license` | REUSE sidecars. |

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

`run.py all` repeats three times and fails if any rebuild differs by one byte.
`verify.py` never writes to this directory: it builds three isolated scratch
copies with symlinks to the pinned read-only inputs and checks cold-start
regeneration there. It also gates this branch's merge-base diff so committed
out-of-scope files cannot pass.

## Remaining gates

Exact licensed MLX, MPS and Core ML runtime identities; exact model and
preprocessing assets; per-runtime CPU parity with declared tolerance;
per-runtime availability and device timing on an exact host/device; Tool
controls for clean install, typical use, caller-owned inputs, malformed inputs
and missing optional selections; separated compile/build, synthetic runtime and
measured workload evidence; rights-cleared model/output terms; opt-in tool or
provider intake; independent exact-head review and hosted checks; and release
approval all remain blocked. Missing or adverse evidence never qualifies a
runtime. No merge, formal approval or release action is taken here.
