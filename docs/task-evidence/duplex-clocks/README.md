# SDK-FND-DUPLEX · Reference, multichannel and clock contracts

**Status: proposal and model-free fixture only.** No public v0 header, ABI,
descriptor, provider registry, engine default or installed behavior changes.
This is a deterministic Python model of a separate versioned interface.

## Scope and source pins

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `fe1839163b80c899a915c56b371e03228230246de00042ff058d7bcff9a5bf4f` | Epoch/sample coordinates, explicit buffers, no hidden graph, no process-global state |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | AEC render/capture boundary, implementation-specific delay, absent live clock-drift evidence |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Task acceptance: matched/missing/discontinuous/drifting traces and teardown |

Pinned task base: `00cc09c56b34ab49c7db20b177e322eb002c16da`.
The source report explicitly lacks live clock-drift, blind-set and target-device
evidence; this fixture does not supply any.

## Proposed interface

[`contract.json`](contract.json) defines `audio-sdk/duplex-reference/0.1`.
Sessions declare render/capture layouts, source rates, a bounded integer ppm
drift and one clock ID. Traces are contiguous, explicit segment sequences.
Layouts cover mono, stereo interleaved and quad interleaved. A missing role is
a state, not silence. Rate conversion uses exact rational arithmetic to the
fixed 16 kHz target plus declared integer ppm drift; wall time never selects
an echo path.

## Fixture acceptance

[`fixture.py`](fixture.py) and [`test_fixture.py`](test_fixture.py) verify:

1. An impulse at 48 kHz source sample 960 maps to 16 kHz target sample 320 and aligns with a 16 kHz capture impulse at 320.
2. A declared +6250 ppm capture drift maps source sample 322 back to target sample 320 with the exact known amplitude; negative mappings are rejected rather than clamped.
3. Missing capture is `rejected_missing`; gaps and overlaps are `rejected_gap` and never interpolated.
4. Stereo/mono layout mismatch and undeclared rates are rejected before frames are read.
5. A stereo capture trace preserves declared channel order.
6. `close()` is idempotent, clears admitted traces and rejects later submit/frame calls.
7. An empty channel tuple is rejected without an exception.
8. Reports are canonical JSON with a stable SHA-256 digest.

## Reproduction

```sh
cd docs/task-evidence/duplex-clocks
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

Expected: 8 tests passed.

## Boundary and reopening

This closes only the versioned interface/fixture question. It does not qualify
AEC, echo-path delay, clock tracking, resampling quality, mobile hardware or
any pipeline. Reopen for implementation with pinned render/capture traces,
exact device clock domains, a declared resampler and drift bound, layout
ownership, teardown sequencing and target-device evidence.
