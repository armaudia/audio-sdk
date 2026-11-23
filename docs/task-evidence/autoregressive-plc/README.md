# SDK-AUTOREGRESSIVE-PLC — deterministic synthetic evidence

Task-local, proposal-only fixture for a minimal **autoregressive (AR) packet-loss
concealment** reference. It is **synthetic**, **optional**, **unregistered**, and
changes no installed SDK behavior, public API, ABI, descriptor, registry default,
`CONTRACTS.md`, top-level `CMakeLists.txt`, board, handoff or `main`.

The installed v0 geometry is preserved exactly: 16 kHz, mono, float32,
160-sample frames. Any other frame size or rate is explicitly outside v0 and is
not exercised here.

## Boundary model and algorithm

The shipped public v0 facade has no frame-level "packet lost" flag: its frame
flags only admit `AS_FRAME_FINAL_INPUT`, and `AS_RESULT_CONCEALMENT = 4` is a
*result* flag. The fixture therefore models the **host delivery-adapter
boundary**: one call per source frame, with a missing packet represented as
`present=False`, `valid_count=0`; concealed output frames carry flag `4` and
`valid_count=0`. No SDK source is changed to enable this, and no new public flag
is implied.

The AR reference is a causal, model-free all-pole forward predictor:

- order 16, context 128 samples (8 × order) taken from previously received or
  already synthesized samples;
- autocorrelation Toeplitz system with diagonal ridge
  `r0 × 1e-5 + 1e-10`, solved by pure-Python Gaussian elimination with partial
  pivoting;
- bounded prediction `clip(pred, ±1.5 × max|centered context|)`, then
  `clip(value, ±0.99)`, with clamped-sample counting;
- zero-fill fallback, counted explicitly, when the context is too short or the
  system is singular/nonfinite.

The AR predictor itself is causal with **0 intrinsic algorithmic delay**. The
800-sample (5-frame) output buffer is an explicit host-adapter scheduling
choice that keeps source slots one-to-one with output frames and supports the
4-frame maximum burst with one-frame lookahead for the linear baseline. It is
not an AR algorithm latency claim.

Conditions: `identity_clean`, `zero_fill_noisy_control` (adverse/noisy control),
`linear_interpolation_baseline` (established task-matched baseline, algorithm
pinned from commit `03519fb4451a4555c4d1b226cc40d27e4cd7eaa7`,
`docs/task-evidence/linear-interpolation-plc/fixture.py`, SHA-256
`35054c6f79279d9ab64b301a2f2c24dbfdbf776c4e579fe4e9f5d3ede7129e61`), and
`autoregressive_plc` (candidate). All four use the same 9-frame erasure mask.

This is the **model-free AR control** from the pinned source evidence. It is not
Opus decoder PLC, not Opus 1.5 deep PLC/DRED, and not the unavailable
Generative PLC / Complex-Bin2bin candidate (candidate-matrix record 28); that
candidate requires an exact checkpoint/runtime and remains blocked.

## Files

| Path | Purpose |
| --- | --- |
| `fixture.py` | Deterministic generator, AR reference session, baseline models, metrics and report writer. |
| `report.json` | Canonical machine-readable report (deterministic bytes). |
| `runtime-measurements.json` | Non-deterministic unpaced wall-clock/RSS envelope pointer; not qualifying timing evidence. |
| `test_fixture.py` | 24 Python unittest checks. |
| `README.md` | This file. |

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Path | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `research/voice-enhancement-20261101/agent-opus-plc/REPORT.md` | `79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b` |
| `api/include/audio_sdk/provider_v0.h` (this worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (this worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Pinned scorer: Python 3.12.16, `numpy 2.5.4`, `pystoi 0.4.1`,
`pystoi/stoi.py` SHA-256
`482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`,
non-extended STOI at 16 kHz. SI-SDR is the zero-mean v1 definition implemented
locally in `fixture.py`. A missing or unpinned scorer returns `None` with a
reason and never triggers a substitute metric.

## Reproduction

From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python fixture.py report.json runtime-measurements.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py
```

`report.json` regenerates byte-for-byte identically; regenerating
`runtime-measurements.json` changes its SHA-256 because it records unpaced
wall-clock time.

Board verification (from the workspace root):

```sh
python3 plan/swarm/check.py --task SDK-AUTOREGRESSIVE-PLC
```

Base commit: `9677040cba2929f9936eaa565f200f585d5270a8`.

## Expected counts and digests

- Cohort: 250 frames = 40,000 samples = 2.5 s, seed `20261125`; 9 erased
  frames = 1,440 samples. Erased frame indices:
  `20, 60, 61, 80, 140, 200, 201, 202, 203` (isolated, two-frame burst,
  four-frame maximum burst).
- Produced frames per condition: 255 (5 startup + 250 source frames); drain
  frames: 5. Valid content samples: 40,000 for identity, 38,560 for all
  erased conditions; each concealed frame carries `valid_count = 0`.
- Clean reference digest:
  `6b6a3c232b1c9e5d7316fc9c2e97981392e1155b29b3ff1f7f872916bcaf5730`.
- Fixture spec digest:
  `19f80b95cf901cbe378accef6fc80abc6675c91549e34e1ef8f0d251c74f316b`.
- Candidate output digest:
  `90e2a6e324530c6102eb4ec38c979d9090193a6f8b198e89363791cc13e3fa88`.
- Linear-baseline output digest:
  `850978c5954eda9e99c90d277bf13d43453e49449810b8f8a21f9a7181fea8f7`.
- Zero-fill/noisy-control output digest:
  `e1c3ce8dc9fa973e702ed059dc5e0f0f4d77b65c113c57c9f0b5812d953f4b75`.
- `report.json` SHA-256:
  `4730ceb74e03782c90dcd78332443c2129cdf56af14ef29bcc89435b68007aec`.
- `fixture.py` SHA-256:
  `dad8145457a14fa84ca0c3446cadc961b1bf7d1ff70d729b8c7dc8f765c67a0d`.
- `test_fixture.py` SHA-256:
  `49651993c757392164d4b9e80e1f3a5663e621ae9fd8f5054f99272290215fe2`.
- Tests: 24 passed, 0 failed, 0 skipped.
- Flags: `controls_all_pass=true`, `alignment_pass=true`, `state_pass=true`,
  `all_outputs_finite=true`, `all_metrics_available=true`.

Pinned paired scores (synthetic clean reference only):

| Condition | SI-SDR (dB) | STOI | SI-SDR Δ vs noisy control | STOI Δ vs noisy control | Concealed RMSE |
| --- | --- | --- | --- | --- | --- |
| Identity clean | undefined (bit-exact) | 1.000000 | — | — | 0.000000 |
| Zero-fill noisy control | 11.891468 | 0.952010 | 0.000000 | 0.000000 | 0.027454 |
| Linear interpolation baseline | 12.157196 | 0.950965 | +0.265728 | -0.001045 | 0.026593 |
| Autoregressive PLC | 13.145847 | 0.953606 | +1.254379 | +0.001596 | 0.023853 |

Identity SI-SDR is intentionally undefined because the estimate is
bit-identical to the synthetic reference; no substitute value is invented.
Valid (non-erased) samples are bit-identical for every condition, with RMS
gain ratios 1.000000 (identity and zero-fill), 1.002891 (linear) and 1.010579
(AR). Peak absolute output is 0.178134 for every condition; no output sample
reaches 1.0 and no nonfinite value appears. These are synthetic observations,
not a general perceptual claim.

Burst-stratified concealed RMSE (synthetic):

| Stratum | Erased frames | Identity | Zero-fill | Linear | AR |
| --- | --- | --- | --- | --- | --- |
| Isolated | 20, 80, 140 | 0.000000 | 0.029583 | 0.026931 | 0.024841 |
| Two-frame burst | 60, 61 | 0.000000 | 0.044009 | 0.043135 | 0.039015 |
| Four-frame burst | 200, 201, 202, 203 | 0.000000 | 0.008434 | 0.010813 | 0.007507 |

## Alignment, validity and adverse controls

Recorded in `report.json` under `alignment`, `state`, `state_observations`,
`decoded_intervals`, `availability`, `erasure_stratification` and `adverse`:

- Declared 800-sample buffering delay, raw source origin `-800`, measured
  impulse peak index `4800` (expected `4800`), content lag `0`, and every
  per-frame source mapping checked. AR intrinsic delay is recorded as `0`.
- One 160-sample output slot per source frame; concealed slots are flagged `4`
  with zero valid samples and excluded from 38,560 valid content samples.
  Decoded duration is 2.5 s for each condition, first valid output at process
  call index 5; no zero-length produced frame.
- Missing frame, wrong shape, short frame, zero-length frame, nonfinite input,
  stale/invalid epoch, duplicate packet and out-of-order packet are each
  rejected without changing stream/valid-content state; a valid frame after
  rejection is accepted.
- A fifth consecutive erasure is rejected (`rejected_burst_length`); a good
  frame immediately after a four-frame burst is accepted. Leading erasure
  produces zero-valid concealment via the explicit AR zero-fill fallback (1
  fallback frame); two trailing erased frames are explicitly counted as
  unresolved for the linear baseline; a boundary burst across frames 99–102 is
  fully concealed.
- Final short frame: 37 valid samples accepted from an 8-frame-plus-37 stream.
- Isolated sessions are uncoupled; reset to a higher epoch is bit-identical to
  a fresh session, rejects stale frames, and processing after close is
  rejected. After 250 frames the AR context is exactly 128 samples and queue
  depth never exceeds 5 (0 after drain). All 9 AR concealments use causal
  synthesis; no solver fallback or output clamp occurred in the scored cohort.

## Runtime envelope (non-qualifying)

`runtime-measurements.json` records unpaced wall-clock and process high-water
RSS for this Python reference on Darwin arm64, Python 3.12.16: median
per-frame process time about 0.045 ms across conditions, AR maximum about
0.525 ms, AR first valid output after about 5 process calls. `qualification_status`
is `blocked`. These are not paced, deadline, target-device or installed-provider
timing claims; source-reported RTF values in
`REALTIME_COMPONENT_CANDIDATES.md` are pinned context, not verified here.

## Explicit non-claims, blockers and reopening conditions

- `real_clean_reference` — no rights-qualified paired real cohort. Reopen with
  a frozen permitted paired cohort, references, crop and alignment policy.
- `authorized_listening` — no listeners, registration or results. Reopen with
  an independently reviewed, consented listening test.
- `target_runtime_timing` — no paced target-device or installed-provider
  deadline evidence. Reopen with paced, loaded, deadline-budgeted measurement
  of the exact installed build.
- `codec_network_pipeline` — no codec-native PLC, network trace, jitter buffer,
  FEC/DRED, stereo path or mobile pipeline. Reopen with pinned integrated
  assets and the exact path.
- `generative_plc_assets` — no exact checkpoint/runtime for Generative PLC /
  Complex-Bin2bin. Reopen with pinned licensed assets and a codec-aligned
  packet-loss benchmark.

No real weights, downloads, licensed runtime or listening result is used. No
MOS, real-speech STOI, target-device pacing, CPU/deadline result, codec/network
pipeline qualification or release claim is made. No attempt to qualify a candidate
from any missing result is accepted:
`no_missing_result_qualifies_candidate = true`, so the candidate remains
`proposal_only_synthetic_incomplete` for real quality and availability decisions.
