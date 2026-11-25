<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ONNX-RUNTIME-REFERENCE-RUNTIME — task-local synthetic evidence

Evidence-only, incomplete and **not qualified**. Decision: **DEFER** before
`runtime_integration`. `status=synthetic_boundary_incomplete`,
`qualification_status=not_qualified`.

This package documents and exercises the proposed developer-facing ONNX Runtime
adapter boundary with a deterministic, caller-supplied synthetic model
descriptor and frozen float32 probe. It does **not** add an SDK adapter, import
or link ONNX Runtime, parse a real ONNX graph, load weights, download anything,
use real audio, measure a device, listen, benchmark or claim a release. Missing
evidence never qualifies a candidate.

## Exact readiness blocker

The pinned runtime is **not available**:

- `importlib.util.find_spec("onnxruntime")` returns `None` in the pinned
  CPython `3.12.16` interpreter; the exact import error is
  `ModuleNotFoundError: No module named 'onnxruntime'`.
- No SDK requirement, lock, CMake option or Python dependency pins ONNX
  Runtime. The scanned files are recorded in
  `report.json:runtime_readiness.sdk_files_scanned`.
- A non-SDK local `.deps` tree containing `onnxruntime-osx-arm64-1.31.1` was
  observed during investigation. It is not an approved or pinned SDK input, its
  distribution terms are not cleared, and it was **not** imported, linked,
  invoked or used. Its version is provenance only.
- The pinned `cpp-library` boundary makes ONNX Runtime optional
  (`AE_ENABLE_ONNXRUNTIME`, default `OFF`) and creates a shared `Ort::Env` only
  when enabled. No such build or session is produced here.

Reopen only when **all** of the following are recorded in
`report.json:runtime_readiness.reopen_conditions`:

1. An exact ONNX Runtime distribution (name, version, platform, byte count and
   SHA-256) is pinned in an SDK lock/requirement file and its redistribution
   terms are cleared under review.
2. The exact install location and import result are captured from the pinned
   CPython 3.12.16 environment.
3. A rights-cleared caller-owned ONNX graph supplies exact input/output names,
   dtypes, shapes, opset and byte digest.
4. The adapter is exercised against that graph and deterministic CPU output is
   compared with an approved reference.

## Proposed developer-facing boundary

`contract.json` declares `audio-sdk/onnx-runtime-adapter/0.1` as a task-local
proposal, not a public ABI. A future optional adapter would expose the same
shape:

```python
adapter = OnnxRuntimeAdapter.open(
    runtime_id="onnxruntime-cpu-reference-synthetic/0.1",
    model_asset=(model_id, model_bytes, sha256, byte_count),
    config={
        "model": "synthetic-ort-adapter-probe",
        "execution_provider": "cpu_reference",
        "graph_optimization": "disabled",
        "intra_op_num_threads": 1,
        "inter_op_num_threads": 1,
        "deterministic": True,
    },
)
capability = adapter.capabilities()          # declared tensors, not a runtime query
result = adapter.run(
    {"waveform_in": frame, "state_in": state},
    {"waveform_out": out_buffer, "state_out": state_buffer},  # optional binding
)
adapter.close()
```

The synthetic stand-in in `reference.py` implements exactly this call sequence,
including validate-before-create, exact configuration, caller-owned assets,
optional held state, preallocated output binding, reset and idempotent close.
`production_adapter_path=not_implemented`; `evaluation_path=task_local_python_fixture`.

## Caller-supplied synthetic fixture

`synthetic_model.json` is canonical JSON, **not** an ONNX protobuf:

| Field | Value |
| --- | --- |
| asset ID | `synthetic-ort-adapter-probe` |
| schema | `audio-sdk/onnx-runtime-reference-runtime/synthetic-model/0.1` |
| kind | `synthetic_non_onnx_descriptor` |
| evaluation | `linear_state_probe_v1` |
| `real_onnx_graph` | `false` |
| tensor geometry | exact f32 `[1,160]` / `[1,16]` inputs and outputs |
| state init | 16 zeros |
| coefficients | `0.75`, `0.25`, `0.125`, alternating unit signs |

The frozen arithmetic uses only IEEE float32 round-to-nearest additions and
multiplications. There are no transcendental functions, threads, random model
weights or vendor kernels. The caller owns the model bytes, feeds and output
buffers; the adapter copies and validates them.

## Locked model and session shapes

| Tensor | Role | Dtype | Shape |
| --- | --- | --- | --- |
| `waveform_in` | input | `f32` | `[1, 160]` |
| `state_in` | input | `f32` | `[1, 16]` |
| `waveform_out` | output | `f32` | `[1, 160]` |
| `state_out` | output | `f32` | `[1, 16]` |

Declared session requirements: CPU execution provider, sequential execution,
disabled graph optimization, one intra-op and one inter-op thread, memory
pattern off and deterministic compute. Public v0 geometry remains 16 kHz, mono,
float32 and 160 samples per call; no installed behavior changes.

## Fail-closed boundary exercise

`report.json:adverse` records actual rejections, not assertions. The totals are
derived from the enumerated case dictionaries, not typed by hand:

```text
model_rejections=18
config_rejections=8
feed_rejections=9
binding_rejections=6
rights_rejections=3
runtime_rejections=2
rejection_cases=46
lifecycle_checks=5 (3 rejected, 2 accepted)
total_checks=51
```

- 18 model-asset cases: digest, byte count, asset id, extra asset, oversize,
  malformed/duplicate JSON, schema, real-graph claim, evaluation, tensor
  order/shape/dtype/extra, coefficient, nonfinite coefficient and state init.
- 8 configuration cases: missing/extra key, model, provider, optimization,
  threading, determinism and non-object config.
- 9 feed cases: missing/extra feed, shape, dtype, bool, nonfinite, range and
  state shape/nonfinite; every rejection leaves held state unchanged.
- 6 binding cases: missing/extra output, wrong capacity, non-writable tuple and
  aliasing an input list.
- 3 rights cases and 2 runtime-id cases, including the unpinned local candidate.
- 5 lifecycle checks: run-after-close, idempotent double close, invalid reset
  shape, nonfinite reset and a valid reset that returns exact zeros. Three are
  rejections and two are accepted lifecycle checks.

`failed_open=0`. Every rejection uses a stable code and never advances state.
The verifier recomputes all six group lengths and the 46/5/51 totals and checks
that this README block and `report.json` agree exactly.

## Tool acceptance profile

Pinned from `audio-benchmark-platform/plan/swarm/VERIFICATION.md` and mapped in
`report.json:tool_profile`:

| Required case | Evidence | Status |
| --- | --- | --- |
| Version, install, provenance | runtime unavailable probe, exact import error | blocked |
| Clean checkout/extracted package | not applicable to evidence-only dir | not run |
| One typical CLI/API use | create → capability → run ×2 → reset → run replay → close ×2 → rejected run | synthetic pass |
| Caller-owned inputs | model bytes, feeds, output buffers | synthetic pass |
| Malformed inputs | model/config/feed/binding/lifecycle matrix | synthetic pass |
| Missing optional selection | unknown runtime/provider/model, absent state | synthetic pass |
| Compile/build evidence | no C++/CMake/link/package change | not run |
| Synthetic runtime evidence | frozen float32 CPU probe only | synthetic pass |
| Measured workload support | no runtime or device measurement | not reported |

The tool profile is not satisfied: the pinned tool is missing and no measured
workload or installed adapter exists.

## Evidence content

- `boundary_checks.typical_api_use` is produced by an executed canonical probe:
  it calls `capability()`, performs two runs, calls `reset()`, replays the first
  frame, closes twice and confirms the post-close run is rejected. Its
  `capability`, `reset`, `run_after_reset` and `close` sections are compared
  with a fresh execution by the verifier.
- `conditions.impulse` and `conditions.constant_*` carry hand-checkable exact
  goldens (`0.75`, `-0.75`, `0.125`, zeros) and raw float32 digests.
- `conditions.lcg_three_frames` carries three stateful frames, final state,
  reset replay and digest equality.
- `conditions.explicit_state_and_bindings` proves the preallocated binding path
  matches the returned-output path.
- Three fresh adapter instances produce one repeated digest; report generation
  is repeated three times byte-identically.
- Source, boundary and artifact pins are generated into `SOURCES.sha256`.
- `report.json` is canonical JSON (`sort_keys`, minimal separators, no
  `-0.0`/NaN/Infinity, trailing newline); `report.json.sha256` is regenerated
  from those exact bytes.

## Rights, scope and negative claims

The synthetic descriptor is generated in this directory and contains no
external bytes. ONNX Runtime redistribution terms, the observed unpinned local
candidate, real model weights and any real ONNX graph remain **uncleared**;
`rights_gap.blocked=true`. No vendoring, linking, installed adapter, public
provider, registry entry, default selection or release claim is permitted.

Only this directory is written. No shared C++, CMake, CI, contract, public
header, descriptor, registry, default, board or handoff file changes.
`onnx_runtime_imported`, `onnx_runtime_invoked`, `real_onnx_graph`,
`real_model_weights`, `real_media`, `runtime_download`, `device_timing`,
`listening_result`, `benchmark_claim` and `release_claim` are all `false`.

## Canonical artifacts and local digests

| File | SHA-256 |
| --- | --- |
| `report.json` | `76f8bd1499e7aa5f9aeb633dc2f2192e2717c76a2a5442bbb024239dd211a92c` |
| `report.json.sha256` | see sidecar |
| `contract.json` | see `SOURCES.sha256` |
| `adapter.json` | see `SOURCES.sha256` |
| `provider.json` | see `SOURCES.sha256` |
| `synthetic_model.json` | `4809717bc3c59739bb312a9e3faf77a7c574335964fb35f764bb5f46b5fa8d9f` |
| `SOURCES.sha256` | generated manifest of all pins and package files |

## Files

- `reference.py` — synthetic model, exact float32 probe, adapter stand-in,
  rejections and canonical report builder.
- `run.py` — regenerates all JSON artifacts, sidecars, report digest and pins.
- `test_reference.py` — 30 deterministic unittest cases.
- `verify.py` — read-only strict pins/JSON/reproduction/rejection/licensing/scope
  verifier.
- `contract.json`, `adapter.json`, `provider.json` — task-local boundary
  documents; none registers a provider.
- `synthetic_model.json` — caller-supplied synthetic model descriptor.
- `report.json`, `report.json.sha256`, `SOURCES.sha256` and `.license` sidecars.

## Reproduction

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and the pinned
interpreter `/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output <scratch>/ci
git -C <worktree> diff --check
```

`run.py` and `verify.py` read no network, model, media or runtime asset. The
report digest changes only when the documented boundary or fixture changes;
regenerate and re-read the sidecar, never hand-edit canonical artifacts.
