# Timing regression and measured delay

## Legacy failure retained

`conformance/legacy_timing_probe.c` is historical failing-before evidence. It
was compiled against the original `cpp-library` ABI 1.1 build, not this SDK.
The deterministic fixture uses xorshift64* seed `20261113`, marker bursts at
sample offsets 640 and 3200, and normalized cross-correlation over
`[-640,+640]`.

Observed baseline:

| Legacy chain | Declared delay | Measured lag | Correlation | Result |
|---|---:|---:|---:|---|
| `identity` | 0 | 0 | 1.000000 | consistent |
| `speex.ns_activity` | 0 | 160 | 0.999472 | **inconsistent** |
| `dsp.highpass` | 0 | 0 | 0.982234 | consistent |

The machine-readable historical report is
`build/baseline-logs/legacy-timing-before.json` (local build evidence; build
directories are not part of source or release artifacts).

## Cause and v0 resolution

The SpeexDSP WOLA filterbank buffers exactly one 10 ms frame. The old
descriptor advertised zero and therefore shifted scoreable content by 160
samples relative to its metadata. The v0 Speex descriptor declares
`buffering_delay_samples: 160`; the high-pass and identity timing remain zero.
The provider does not “fix” measurements by fitting a per-file lag.

The standalone conformance checks repeat the delay measurement at stream
origins 0 and 123456 and across a new epoch. They require the residual mapping
to be within one sample of the declared integer delay. A high-pass has
frequency-dependent phase; its integer buffering delay remains zero and is
not claimed to describe its transfer-function phase.
