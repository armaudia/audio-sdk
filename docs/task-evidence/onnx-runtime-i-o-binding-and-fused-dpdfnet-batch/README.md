<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ONNX-RUNTIME-I-O-BINDING-AND-FUSED-DPDFNET-BATCH — task-local synthetic evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ONNX Runtime I/O binding and fused DPDFNet batch`
(`component_id=onnx-runtime-i-o-binding-and-fused-dpdfnet-batch`). The acceptance
profile is **Tool**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`fused_batch_integration`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result never qualifies the
candidate.

This package documents and exercises the developer-facing **wrapper boundary**
for two proposed capabilities: caller-preallocated ONNX Runtime output bindings
and a fused multi-lane DPDFNet batch with independent per-lane recurrent state.
A deterministic stdlib synthetic stand-in exercises validation, binding, lane
isolation and refusal mechanics. It is **not** ONNX Runtime, **not** DPDFNet,
**not** a fused tensor kernel, and substitutes for no gate.

No candidate artifact was downloaded, loaded, built, vendored or invoked. No
ONNX Runtime, ONNX graph, DPDFNet weight, `dpdfnet` package, real audio, corpus,
device clock, listener, benchmark or release artifact is present or claimed.
There is no candidate output and no speedup result. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build, CI, board
or handoff file changes. Only this task-local directory is added.

## Exact external blocker

### Runtime

- `importlib.util.find_spec("onnxruntime")` returns `None` in the pinned CPython
  `3.12.16` interpreter; the exact import error is
  `ModuleNotFoundError: No module named 'onnxruntime'`.
- No SDK requirement, lock, CMake option or Python dependency pins ONNX
  Runtime. The scanned files are recorded in
  `report.json:runtime_readiness.sdk_files_scanned`.
- A non-SDK, gitignored `cpp-library/.deps/onnxruntime-osx-arm64-1.31.1` tree
  was observed on the investigation host. It is not an approved or pinned SDK
  input, its terms are not cleared, and it was **not** imported, linked, invoked
  or used. Its version is provenance only.
- The pinned `cpp-library` boundary keeps ONNX Runtime optional
  (`AE_ENABLE_ONNXRUNTIME`, default `OFF`) and creates a shared `Ort::Env` only
  when enabled. No such build or session is produced here.

### Model and fused batch

- The asset ledger records `data/models/dpdfnet/baseline.onnx` as **8,722,707
  bytes**, SHA-256
  `371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0`, and
  `data/models/dpdfnet/dpdfnet2.onnx` as **10,178,747 bytes**, SHA-256
  `4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c`, under
  source revision `dd6818d00f50c836fed43a6243ebe49116de5964` and package
  `dpdfnet==0.6.0`.
- Both assets are **absent from this workspace** and were not read, downloaded
  or fabricated.
- Their `model_revision` is `null` and `model_download_revision` is
  `main (mutable; retrieval-time commit not recorded)`. No immutable artifact
  revision resolves the exact bytes.
- The pinned exports declare fixed per-frame/spectrum shapes. No batch-capable
  export with declared batched tensors, independent per-lane recurrent-state
  packing and exact input/output names exists.
- The existing scheduled pool **groups** compatible session heads for dispatch,
  but processes one frame at a time. The implementation record states no backend
  exposes a vectorized multi-frame kernel and no performance gain is assumed.
  Dispatch coalescing is not batched inference and is not presented as such.
- No target pacing, deadline, memory or speedup measurement exists.

### Rights

Apache-2.0 is recorded for the package and model card, but weight-specific terms,
training-data provenance, runtime redistribution, product-use clearance and legal
review are absent. No upstream portion may be copied, packaged, downloaded or
redistributed.

**Reopen condition.** Admit the candidate only when an exact ONNX Runtime
distribution (name, version, platform, byte count, SHA-256, cleared terms) is
pinned in an SDK lock/requirement file; exact batch-capable DPDFNet ONNX bytes
are addressed by an immutable artifact revision plus byte count and SHA-256 and
resolve from caller storage; written weight/runtime/training-data terms and a
rights/redistribution decision exist; and real per-lane scalar/batched parity,
I/O-binding parity, target pacing/deadline/memory evidence and independent review
are available. Until then all eight release gates stay `blocked`.

## Proposed developer-facing boundary

`contract.json` declares `audio-sdk/onnx-runtime-fused-batch-adapter/0.1` as a
task-local proposal, not a public ABI. A future optional adapter would expose the
same shape:

```python
boundary = FusedBatchBoundary.open(
    runtime_id="onnxruntime-cpu-fused-batch-synthetic/0.1",
    model_asset=(model_id, model_bytes, sha256, byte_count),
    config={
        "model": "synthetic-ort-fused-batch-probe",
        "execution_provider": "cpu_reference",
        "graph_optimization": "disabled",
        "intra_op_num_threads": 1,
        "inter_op_num_threads": 1,
        "deterministic": True,
        "output_binding": "caller_preallocated",
        "max_batch": 4,
    },
)
capability = boundary.capabilities()          # declared tensors, not a runtime query
result = boundary.run(
    [
        {"instance_id": "lane-a", "frame": frame_a},
        {"instance_id": "lane-b", "frame": frame_b},
    ],
    bindings=[{"waveform_out": out_a, "state_out": state_a},
              {"waveform_out": out_b, "state_out": state_b}],  # optional binding
)
boundary.reset()                              # quiesced control work
boundary.close()
```

The synthetic stand-in in `reference.py` implements exactly this call sequence,
including validate-before-create, exact configuration, caller-owned asset,
per-lane held state, preallocated output binding, all-or-nothing commit, reset
and idempotent close. `production_adapter_path=not_implemented`;
`evaluation_path=task_local_python_fixture`.

## Locked model and session shapes

`synthetic_model.json` is canonical JSON, **not** an ONNX protobuf:

| Field | Value |
| --- | --- |
| Asset ID | `synthetic-ort-fused-batch-probe` |
| Schema | `.../synthetic-model/0.1` |
| Kind | `synthetic_non_onnx_descriptor` |
| Evaluation | `lane_state_fused_batch_probe_v1` |
| `real_onnx_graph` / `real_model_weights` | `false` / `false` |
| `max_batch` | `4` |
| Batch dimension | `0`, min 1 lane, max 4 lanes |
| `waveform_in` / `waveform_out` | `f32` per-lane `[1,160]`, max `[4,160]` |
| `state_in` / `state_out` | `f32` per-lane `[1,16]`, max `[4,16]` |
| State init | 16 zeros |
| Coefficients | `0.75`, `0.25`, `0.5`, `0.125` |

The frozen arithmetic uses only IEEE float32 round-to-nearest additions and
multiplications: `y[i] = f32(0.75*x[i] + 0.25*s[0])`, then
`s[j] = f32(0.5*s[j] + 0.125*sign(j)*x[i])`. There are no transcendental
functions, fused multiply-adds, threads, random weights or vendor kernels. The
caller owns the model bytes, lane feeds, optional explicit state and output
buffers; the stand-in copies and validates them.

Declared session requirements: CPU execution provider, sequential execution,
disabled graph optimization, one intra-op and one inter-op thread, memory
pattern off, caller-preallocated I/O binding and deterministic compute. Public v0
geometry remains 16 kHz, mono, float32 and 160 samples per call; no installed
behavior changes.

### I/O binding and batch contract

- Outputs are caller-owned, writable lists with **exact** capacity: 160 waveform
  floats and 16 state floats per lane.
- A bound output may not alias an input frame, an explicit input state, another
  lane's output, or the sibling output of the same lane.
- Bindings are ordered exactly with the lane list; missing, extra, non-list or
  non-writable outputs fail before any compute or state change.
- One call accepts 1–4 lanes. Each lane has independent held recurrent state,
  keyed by stable instance ID.
- Validation, compute staging and state/output commit are separate. Any invalid
  lane, bridge or binding rejects the whole call; no lane state advances and no
  caller output is written.
- A post-compute nonfinite lane output marks the boundary `needs_reset`; no lane
  state or output is delivered until a quiesced reset.

## Conditions and controls (synthetic only)

`report.json:conditions` is produced by executed calls and recomputed by
`verify.py`. The impulse and constant cases carry hand-checkable exact goldens:

| Condition | Expected first output samples | Result |
| --- | --- | --- |
| `impulse` | `0.75`, `0.03125`, `0.015625`, … | exact |
| `constant_one` | `0.75`, `0.78125`, `0.796875`, … | exact |
| `constant_negative_one` | `-0.75`, `-0.78125`, … | exact |
| `silence` | zeros, zero state | exact |
| `lcg_two_frames` | two stateful frames; reset replay matches frame 0 | exact replay |
| `fused_batch_parity` | four lanes; batch digests equal per-lane scalar digests | all lanes equal |
| `io_binding_equivalence` | two lanes; bound result equals unbound result | equal |
| `lane_state_isolation` | lane A equals its solo run after a two-lane batch | equal |
| `atomic_rejection` | invalid lane 3 rejects; state and sentinels unchanged | closed |

All values are synthetic fixture properties. They are not DPDFNet output, not a
quality result and not a speedup measurement.

## Fail-closed boundary exercise

`report.json:adverse` records actual rejections, not assertions. Totals are
derived from the enumerated case dictionaries, not typed by hand:

```text
model_rejections=19
config_rejections=8
feed_rejections=13
batch_rejections=4
binding_rejections=11
fault_rejections=1
rights_rejections=3
runtime_rejections=2
rejection_cases=61
lifecycle_checks=5 (3 rejected, 2 accepted)
total_checks=66
```

- 19 model-asset cases: asset ID, digest, byte count, tuple arity, oversize,
  malformed, duplicate-key, non-object, schema, real-graph claim, evaluation,
  max batch, tensor missing/extra/shape/dtype, coefficient, nonfinite coefficient
  and state init.
- 8 configuration cases: missing/extra key, model, provider, optimization,
  threading, determinism and output binding.
- 13 lane-feed cases: missing/extra field, frame shape/bool/string/nonfinite/
  infinite/out-of-range, state shape/nonfinite, duplicate/invalid instance ID and
  explicit state overriding a held lane. Every rejection leaves all lane state
  unchanged.
- 4 batch cases: empty, over-max, non-list and non-object item.
- 11 binding cases: arity, non-list, non-object, missing/extra output, waveform
  and state capacity, non-writable tuple, input alias, cross-lane alias and
  sibling-output alias. Every rejection leaves state and buffers unchanged.
- 1 deterministic injected lane-output fault: the whole batch is rejected, no
  state advances, no buffer is written, `needs_reset` is set, the next run is
  rejected, and reset recovers.
- 3 rights requests and 2 runtime IDs, including the unpinned local candidate.
- 5 lifecycle checks: run after close, idempotent double close, reset after
  close, unknown-lane reset and a valid reset to exact zeros. Three are
  rejections and two are accepted lifecycle checks.

`failed_open=0`. Every rejection uses a stable code and never advances state or
writes caller memory.

## Tool acceptance profile

Pinned from `plan/swarm/VERIFICATION.md` and mapped in
`report.json:tool_profile`:

| Required case | Evidence | Status |
| --- | --- | --- |
| Version, install, provenance | runtime unavailable probe, exact import error | blocked |
| Clean checkout/extracted package | not applicable to evidence-only directory | not run |
| One typical CLI/API use | open → capability → scalar → batch-4 → bound batch → reset → replay → close ×2 → rejected run | synthetic pass |
| Caller-owned inputs | model bytes, frames, states, output buffers | synthetic pass |
| Malformed inputs | model/config/feed/batch/binding/fault/lifecycle matrix | synthetic pass |
| Missing optional selection | unknown runtime/model/lane, absent state | synthetic pass |
| Compile/build evidence | no C++/CMake/link/package change | not run |
| Synthetic runtime evidence | frozen float32 CPU probe, batch boundary only | synthetic pass |
| Measured workload support | no runtime, model, device timing or memory measurement | not reported |

The tool profile is not satisfied: the pinned runtime and batch-capable model are
missing, no installed adapter exists and no workload is measured.

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_onnx_runtime_pin` | blocked | Pin exact version/platform/bytes/SHA-256 and clear terms. |
| `batch_capable_model_identity` | blocked | Immutable batch-capable ONNX revision, byte count and SHA-256. |
| `artifact_rights_and_redistribution` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `io_binding_reference_parity` | blocked | Real bound/returned outputs match an approved reference. |
| `fused_batch_lane_parity` | blocked | Real per-lane scalar/batched parity and failure isolation. |
| `target_runtime_timing_and_memory` | blocked | Target pacing, deadline and memory measurement. |
| `provider_intake_and_default_selection` | blocked | Opt-in intake, OFF default, licensing and review. |
| `independent_review_and_release` | blocked | Independent review at the exact head and release approval. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
other paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | DPDFNet artifact digests, byte counts, revisions and license metadata. |
| `source:adapters/dpdfnet/requirements.lock` | `2d43db167c1c221992ac51bd15ae365bfc18ddc21eb405c53ce8a444e5af34a4` | Recorded CPython 3.11 lock including `onnxruntime==1.31.1` and `dpdfnet==0.6.0`. |
| `source:adapters/dpdfnet/run.py` | `40fbd148eb80ec21a33290e4cb4bc9258afb54f65d4d5fd5d82b552deac5ae02` | Per-frame offline/streaming wrapper and 640-sample lag handling. |
| `source:realtime-audio-library/implementation_record.md` | `12b7c17d6ae969cb3e9697f3309667518048f27792b283178d326746e1bbfb81` | Scheduler coalescing without a batched backend kernel; no speedup claimed. |
| `source:cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | Fixed DPDFNet shapes; true batch needs a compatible export and state packing. |
| `source:cpp-library/src/stages/onnx_common.cpp` | `f8eaee5455fefb1dd0dcaac10092a25f673f138f76af07d21dfed69fa95712c8` | Optional runtime anchor; no session or graph is created. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | External asset, batch-table and no-download boundary. |
| `worktree:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` | Unchanged provider intake rules. |

The board is referenced by stable linked-row identity only
(`tasks[id=SDK-ONNX-RUNTIME-I-O-BINDING-AND-FUSED-DPDFNET-BATCH]`); the mutable
full `plan/swarm/TASKS.json` is never hashed or pinned.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, blockers, modelled boundary, results, pins, commands and gates. |
| `contract.json` | Task-local proposal, binding/batch semantics, blockers and reopen conditions. |
| `synthetic_model.json` | Caller-supplied synthetic model descriptor; not an ONNX protobuf. |
| `reference.py` | Deterministic stand-in, exact float32 probe, rejections and report model. |
| `run.py` | Regenerates JSON artifacts, sidecars, README digest and source pins. |
| `report.json` / `report.json.sha256` | Canonical Tool evidence report and digest sidecar. |
| `test_reference.py` | Deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin/JSON/README/reproduction/licensing/scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Canonical artifacts and local digests

| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `synthetic_model.json` | `b1dc69c3ee207f9aa1a4fb89a0131c9040b5064c7eeeed1cb8f29bb13c8fe478` | 1,657 |
| `contract.json` | `c23a4cc0ec39d8bdca64c513acf426c3be5bc96ca22e6d94c3a1855049d3ebe1` | 6,661 |

Other artifact digests are regenerated into `SOURCES.sha256`. `report.json` is
canonical JSON (`sort_keys`, minimal separators, no `-0.0`/NaN/Infinity,
trailing newline); `report.json.sha256` is regenerated from those exact bytes.

<!-- REPORT_SHA256_START -->
`report.json` SHA-256: `19d165ae523024f219d01e711ec2497ad8991405d0048c0b22871099ccb17344`
<!-- REPORT_SHA256_END -->

## Reproduction

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and the pinned
interpreter `/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ONNX-RUNTIME-I-O-BINDING-AND-FUSED-DPDFNET-BATCH diff --check
```

`run.py` and `verify.py` read no network, model, media or runtime asset.
Three in-process passes and three cold-start interpreter processes regenerate
byte-identical bytes. `run.py --all` also rewrites the README digest block and
`SOURCES.sha256`; never hand-edit canonical artifacts.

## Negative claims

`onnx_runtime_imported`, `onnx_runtime_invoked`, `onnx_runtime_linked`,
`real_onnx_graph`, `real_model_weights`, `dpdfnet_executed`,
`fused_tensor_kernel`, `speedup_claim`, `runtime_download`, `real_media`,
`device_timing`, `listening_result`, `benchmark_claim` and `release_claim` are
all `false`. No provider registration, installed-v0/ABI/registry/default/
shared-build/CI change, real corpus/weights/runtime, listening, device timing,
benchmark or release claim exists.
