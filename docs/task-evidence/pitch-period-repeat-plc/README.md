# SDK-PITCH-PERIOD-REPEAT-PLC — deterministic synthetic evidence

Task-local, optional, unregistered fixture for a minimal **pitch-period repeat
packet-loss concealment (PLC)** reference. It is **synthetic**, **proposal-only**
and changes no installed SDK behavior, public API, ABI, descriptor, registry
default, `CONTRACTS.md`, top-level `CMakeLists.txt`, board, handoff or `main`.

The installed v0 geometry is preserved exactly: 16 kHz, mono, float32,
160-sample frames. No other rate or frame size is exercised.

## Boundary model and algorithm

The shipped public v0 facade has no frame-level "packet lost" flag:
`AS_RESULT_CONCEALMENT = 4` is a *result* flag. This fixture therefore models
the **host delivery-adapter boundary** at the public provider/session contract:
one call per source frame, with a missing packet represented as
`present=False`, `valid_count=0`; concealed output frames carry flag `4` and
`valid_count=0`. No SDK source is changed and no new public flag is implied.
`boundary` in `report.json` records that ABI and installed defaults are
unchanged.

The candidate is causal and model-free:

- normalized autocorrelation over the previous 480 samples (three frames),
  integer lags 40–240 samples (400–66.7 Hz at 16 kHz);
- silence gate `energy < 1e-8` and voicing gate `score < 0.55` reject
  unvoiced/silent material;
- when voiced, the last detected period is repeated cyclically across the
  erased frame with gain `0.95 - 0.05 × consecutive_erased`, floored at 0.70,
  and output clipped to ±0.99;
- when unvoiced, silent or without sufficient context, zero-fill is used and
  counted explicitly as a fallback.

The estimator and repeater have **0 intrinsic algorithmic delay**. The
800-sample (5-frame) output buffer is an explicit host-adapter scheduling
choice that keeps source slots one-to-one with output frames, supports the
4-frame maximum burst and provides the linear baseline's right endpoint. It is
not a candidate latency claim.

Conditions on the same 11-frame erasure mask:

| Condition | Role |
| --- | --- |
| `identity_clean` | identity control, bit-exact on all valid and erased source samples |
| `zero_fill_noisy_control` | adverse/zero-fill control |
| `linear_interpolation_baseline` | established task-matched baseline (pinned source) |
| `autoregressive_baseline` | established task-matched AR control (pinned source) |
| `pitch_period_repeat` | candidate |

The baselines are local faithful ports of the pinned task-local fixtures, not
the upstream files themselves. This fixture is the **model-free pitch-repeat
control** from the pinned source evidence. It is not Opus decoder PLC, not
Opus 1.5 deep PLC/DRED, and not the unavailable Generative PLC / Complex-Bin2bin
candidate (candidate-matrix record 28); those remain blocked or out of scope.

## Files

| Path | Purpose |
| --- | --- |
| `fixture.py` | Deterministic generator, pitch estimator, boundary session, controls, metrics and report writer. |
| `report.json` | Canonical machine-readable synthetic report (deterministic bytes). |
| `runtime-measurements.json` | Non-deterministic unpaced wall-clock/RSS envelope pointer; not qualifying timing evidence. |
| `test_fixture.py` | 31 Python unittest checks. |
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
| `docs/task-evidence/linear-interpolation-plc/fixture.py` (git blob at `d665c29`) | `35054c6f79279d9ab64b301a2f2c24dbfdbf776c4e579fe4e9f5d3ede7129e61` |
| `docs/task-evidence/autoregressive-plc/fixture.py` (git blob at `d665c29`) | `dad8145457a14fa84ca0c3446cadc961b1bf7d1ff70d729b8c7dc8f765c67a0d` |

Pinned scorer: Python 3.12.16, `numpy 2.5.4`, `pystoi 0.4.1`,
`pystoi/stoi.py` SHA-256
`482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`,
non-extended STOI at 16 kHz. SI-SDR is the zero-mean v1 formula implemented
locally. A missing or unpinned scorer yields no value and never triggers a
substitute metric; no missing result qualifies the candidate.

## Synthetic material

The paired clean reference is generated under fixed seeds: 250 frames / 40 000
samples / 2.5 s. Voiced regions use exact-period harmonic surrogates with
known periods (120, 160 and 100 samples), an unvoiced region uses deterministic
band-limited noise, and a silence region is exactly zero. Erasures are
stratified as voiced isolated (frame 20), voiced two-frame burst (60–61),
voiced four-frame burst (80–83), unvoiced (150), silence (190) and voiced tail
burst (220–221): 11 frames / 1760 concealed samples.

The estimator is separately probed on deterministic voiced (80/120/200-sample
period), unvoiced and silence material. All five probe cases pass: estimated
periods are 80, 120 and 199 respectively (tolerance ±3), and unvoiced/silence
return no period with explicit reasons. During the scored stream, all nine
voiced erasures are detected as voiced and both unvoiced/silence erasures fall
back to zero-fill.

## Measured synthetic result (not a quality claim)

| Condition | SI-SDR (dB) | STOI | concealed RMSE |
| --- | ---: | ---: | ---: |
| zero-fill control | 13.589343 | 0.807333 | 0.265660 |
| linear interpolation | 12.783500 | 0.859246 | 0.290483 |
| autoregressive | 13.781399 | 0.836350 | 0.260423 |
| pitch-period repeat | 22.139532 | 0.851298 | 0.101429 |

The candidate improves SI-SDR and concealed-region RMSE over every control on
this synthetic signal; linear interpolation has higher STOI here. That is a
synthetic comparison only, not a held-out speech, MOS, listening or release
result. All metrics are available where claimed, every output is finite and
below magnitude 1, valid source samples are bit-identical, and no missing
result qualifies the candidate (`overall_synthetic_pass = true`).

Additional evidence: decoded intervals and decoded duration (2.5 s),
impulse alignment (0-sample content lag, source mapping exact), independent
sessions, epoch reset/replay, bounded 480-sample history and 5-frame queue,
over-max burst rejection, leading-erasure zero-fill fallback, stale/duplicate/
out-of-order/nonfinite/short/missing/bad-shape controls, and a 37-sample final
partial frame with flag 2. Erasure-burst and voicing-stratified RMSE tables are
in `report.json`.

## Reproduction

From this directory, with the pinned Python 3.12 environment:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python fixture.py report.json runtime-measurements.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python -m unittest -v test_fixture.py
```

`report.json` regenerates byte-for-byte identically (SHA-256
`114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445`).
Regenerating `runtime-measurements.json` changes its bytes because it records
unpaced wall-clock timing; the committed file is a snapshot only.

Read-only board and whitespace checks (from the workspace root / worktree root):

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-PITCH-PERIOD-REPEAT-PLC
git diff --check
```

## Local artifact digests (committed snapshots)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `e72b4fb431ad8865a48d871bd36b0843165cdbed85aa5754d5f3dc5aab4d7d18` |
| `test_fixture.py` | `4202dd27c02e08ffa485ef07f13efda031fe3549a9a7214875677eeb72f209b5` |
| `report.json` | `114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445` |
| `runtime-measurements.json` | `cd98aa4e350d45afd540bbcaf08d131a2ae3b0f72fbb34086356a20aa287c40f` |

## Blockers and reopening conditions

| Blocker | Status | Reopening condition |
| --- | --- | --- |
| `real_clean_reference` | blocked | Freeze a rights-qualified paired real cohort, references, crop and alignment policy. |
| `authorized_listening` | blocked | Register and run an independently reviewed listening test with consent and output-use permissions. |
| `target_runtime_timing` | blocked | Measure the exact installed build on the intended host with pacing, load, buffer and deadline budgets. |
| `codec_network_pipeline` | blocked | Pin codec/network/jitter-buffer/FEC/DRED assets and test the exact integrated path. |
| `generative_plc_assets` | blocked | Pin the exact licensed checkpoint, runtime and codec-aligned packet-loss benchmark for Generative PLC / Complex-Bin2bin. |

No real clean cohort, weights, downloads, licensed runtime, listening result,
target-device timing, codec trace or release claim is made. Until every gate
passes, this directory remains optional task-local reference evidence and the
installed v0 behavior stays frozen.
