# SDK-FND-NN · Optional neural and offline runtime boundary

**Status: proposal and model-free stub fixture only.** No weights, downloads,
native runtime, model output, adapter protocol change or public v0 ABI change
is present. The pinned reference digest is a deterministic stub value, not a
model result.

## Exact blocker

No supported real asset, verified download, license/rights statement or
alternate runtime is available for this foundation. The task therefore stays
within the accepted model-free boundary: exact asset identity, frozen tensor
and hook shapes, finite state, distinct offline/streaming entry points and a
pinned **model-free** reference digest. Missing/changed assets fail closed.
Reopen real-model work only with an exact asset ID/byte count/SHA-256, rights
and attribution record, supported runtime revision, and a frozen matched
reference. No missing-result may qualify a candidate.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `fe1839163b80c899a915c56b371e03228230246de00042ff058d7bcff9a5bf4f` | External asset identity, no provider file/network access, finite state, versioned boundary |
| `adapters/README.md` | `24d8915f0ff59ee026ef86b396f64f1b3e68d3a5678f98a353273b712f09e1ee` | Adapter callers do not download; explicit assets and worker validation remain authoritative |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Missing optional selections and malformed inputs fail explicitly |

Pinned task base: `00cc09c56b34ab49c7db20b177e322eb002c16da`.

## Proposed interface

[`contract.json`](contract.json) defines `audio-sdk/neural-runtime-boundary/0.1`.
It freezes four f32 tensors (`waveform_in [1,160]`, `state_in [1,16]`,
`waveform_out [1,160]`, `state_out [1,16]`) and three hooks
(`capability_query`, `process_mode`, `resume_prepare`). Model IDs are immutable.
Assets are external and verified by ID, byte count and SHA-256. Only two
explicit stub runtime IDs load; everything else is rejected. Offline and
streaming runners are separate instances.

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. Only declared CPU-reference and alternate stub runtimes load; unlisted runtimes are rejected.
2. Duplicate model IDs with changed version or graph digest are rejected.
3. Missing and changed assets fail before any tensor call; no download is attempted.
4. Capability query reports the frozen tensor shapes and hooks.
5. A pinned model-free reference input produces exact f32 digest `42990c3122a8873462194c3b89ee3194011cba38dc050edf480c3f442b8bd19e`.
6. Streaming state has 16 finite values, advances deterministically, and rejects NaN state without changing state.
7. Wrong tensor shape and nonfinite input are rejected.
8. Offline and streaming entry points reject each other.
9. Unsupported `process_mode` and malformed `resume_prepare` history are explicit failures.
10. Close is idempotent, and reports are canonical.

## Reproduction

```sh
cd docs/task-evidence/neural-runtime-boundary
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

Expected: 11 tests passed.

## Boundary and reopening

This closes only the versioned boundary/fixture question. It does not qualify
FastEnhancer, DPDFNet, GTCRN, DTLN, DeepFilterNet3, RNNoise, any weight set,
CPU cost, alternate runtime, device or pipeline. Reopen with the exact missing
asset/runtime/rights evidence listed above and separate acceptance scope.
