# SDK-EBU-R128-FFMPEG-LOUDNORM — deterministic synthetic R128 loudness-target evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
an EBU R 128 / FFmpeg `loudnorm`-style loudness target. The candidate is a
**minimal Python reference**, not an FFmpeg wrapper, not a BS.1770/EBU Mode
meter and not a licensed asset. It is **synthetic, optional, unregistered and
OFF by default**, changes no installed SDK behavior, public API/ABI, descriptor
registry, registry default, `CONTRACTS.md`, build text, board, handoff, other
worktree or branch. Installed v0 stays exactly **16 kHz, mono, float32, 160
samples per call**. No FFmpeg binary, GPL component, WAV, corpus, download,
device, listening test or network benchmark is vendored, shipped or used.

## External developer tool invocation and FFmpeg provenance

The first action was an external-tool invocation, recorded byte-for-byte in
`tool-provenance.json`: `ffmpeg -version` raised `FileNotFoundError`;
`which -a ffmpeg` returned 1 with empty output; the historical bundled path
`data/envs/ffmpeg/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1`
also raised `FileNotFoundError`. No independent `ebur128`/`bs1770gain` meter
was found. Therefore **no local FFmpeg version/build/configuration output could
be captured**, no synthetic two-pass `loudnorm` invocation was run, and the
FFmpeg tool gate is **blocked**.

Historical provenance is pinned from the source report, results and asset
ledger, not from any binary held here:

| Field | Record |
| --- | --- |
| Historical executable | `data/envs/ffmpeg/lib/python3.11/site-packages/imageio_ffmpeg/binaries/ffmpeg-macos-aarch64-v7.1` |
| Reported version | FFmpeg 7.1, `imageio-ffmpeg` 0.6.0 |
| Binary SHA-256 | `6d175a4743ca50256e89a8cdd731100f9cee33bd79aeea46894d209410dc6617` |
| Binary bytes | `49368728` |
| GPL dependency/build configuration | `GPL-2.0-or-later` reported by the local asset ledger; exact configure flags are not present in the pinned record and are **not invented** |
| Local build string | `null` — absent executable, so unavailable |
| Vendored / downloaded / shipped / wrapped | all `false` |

Any future vendored binary needs a separate license review before it may be
considered; this package none uses. The historical 29/30 ±0.2 LU and 30/30
true-peak-cap results in the pinned report are **same-implementation**,
source-reported context only. They are not rerun, pooled or qualified here.

## Boundary model and explicit formulas

Whole-programme analysis cannot be a causal v0 `process` provider. This fixture
models an **offline host analyzer** plus a separate **static-gain frame
adapter** at the documented public boundary:

- Analysis is a control-plane pass over the complete synthetic signal. It
  estimates gated integrated loudness and true peak.
- The solved scalar gain is applied through 16 kHz mono f32, 160-sample frames.
  The adapter consumes padded input, produces 160 samples, maps output sample 0
  to `first_input_sample` (`D = 0`), checks epoch/order/validity/final state,
  and has no hidden queue or drain output.
- The conceptual ID `dsp.ebu-r128-loudnorm-ref.v0` is recorded with
  `registered=false`, `enabled_by_default=false`, `descriptor_settings={}`.
  No C provider is compiled, installed or registered.

Formulas (all local, deterministic and non-standards):

1. **K-weighting estimate.** Two RBJ biquads at 16 kHz: high shelf
   `1681.97 Hz`, `+4 dB`, slope parameter `S=1`; high-pass `38 Hz`, `Q=0.5`;
   shelf then high-pass; zero initial state. This is an approximation, **not**
   EBU Mode K-weighting.
2. **Gated loudness.** 400 ms blocks (`6400` samples), 100 ms hop (`1600`
   samples). Block LUFS is `-0.691 + 10*log10(mean_square)`. Blocks below
   `max(-70 LUFS, ungated - 10 LU)` are excluded. Integrated LUFS is
   `-0.691 + 10*log10(mean(10^((block+0.691)/10)))` over the remaining blocks.
   The LRA estimate is the 90th-minus-10th percentile of gated block LUFS and
   needs at least 10 gated blocks; `LRA=7 LU` is recorded but **not enforced**.
3. **True-peak estimate.** 4x Catmull-Rom cubic interpolation at `t=1/4,1/2,3/4`
   for every adjacent sample pair, endpoint neighbours clamped. For
   `p0,p1,p2,p3`, the interpolated value is
   `0.5*(2*p1 + (-p0+p2)*t + (2*p0-5*p1+4*p2-p3)*t^2 + (-p0+3*p1-3*p2+p3)*t^3)`.
   This captures intersample peaks but is **not** BS.1770 true peak.
4. **Gain.** `gain_loudness = 10^((-23 - measured_LUFS)/20)`;
   `gain_tp = 10^(-1/20)/estimated_true_peak`; `MAX_GAIN = 64`. A single gain
   `min(gain_loudness, gain_tp, MAX_GAIN)` is applied. The true-peak ceiling and
   the safety cap are explicit nonlinear interactions, reported verbatim.
   No clipping, limiter, dynamic mode or per-frame adaptation is applied.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, boundary, pins, reproduction, counts, results, regressions and gates. |
| `reference.py` | Deterministic generator, loudness/true-peak reference, gain solver, frame adapter, cohorts and report builder. |
| `run.py` | Regenerates `report.json`, `report.json.sha256` and `tool-provenance.json`. |
| `report.json` | Canonical machine-readable DSP report; regenerated byte-for-byte. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `tool-provenance.json` | External-tool invocation record and historical FFmpeg/GPL provenance. |
| `test_reference.py` | 36 Python unittest checks; no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, reproduction, licensing and write-scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every pinned external file and every task-local artifact. |

## Source and artifact pins (SHA-256)

External paths are relative to `/Users/htsakanyan/workspace/audio/audioml`; SDK
paths are relative to this worktree. All pins are rechecked by `verify.py`.

| Path | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `research/voice-enhancement-20261101/agent-r128-eval/REPORT.md` | `b6afa2b82f888882dd3c7d24d262848aa6218b65d5fb490d88cb007d17b23ef5` |
| `research/voice-enhancement-20261101/agent-r128-eval/results.json` | `9bdfef51364931b351d07fb425c7f08f1845b3e1168095369964da746ddfb783` |
| `research/voice-enhancement-20261101/agent-r128-independent-audit/REPORT.md` | `12616c2eb6b394484f359c910a84dac7b327558b0dbae381906b8b8dc3ad6896` |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` (worktree) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` (worktree) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Pinned base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`.

## Reproduction

From this directory, using the pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-EBU-R128-FFMPEG-LOUDNORM
```

`report.json` regenerates byte-for-byte identically; `verify.py` performs an
exact byte comparison and prints its SHA-256. No network, download, external
tool or licensed asset is invoked by regeneration.

## Expected counts and digests

- Cohort: 250 frames / 40,000 samples / 2.5 s, seed `20261124`; frozen
  voiced/unvoiced/silence regions matching the pinned generator.
- Four main conditions run the same synthetic speech: identity, fixed `+6 dB`,
  sample-peak control and `candidate_linear_loudnorm_ref`. Each has 250 frames,
  40,000 valid samples, zero rejections and finite output.
- Frequency response: seven tones at `100, 250, 500, 1000, 2000, 4000, 6000 Hz`
  plus a chirp; maximum absolute gain error `0.000122 dB`.
- Final partial window: 8 full frames + 37 samples (1,317 samples), valid
  samples conserved, no rejections.
- `fixture_digest`:
  `9580e377fcb59d83875b1a38311c449490a50f2cb71987276d70ef6afca360e0`.
- Clean reference digest:
  `fd97ef083def8b4a18a7e42d708bc940d8a66388cb7c25c08fa8a1846fce91d2`.
- `report.json` SHA-256:
  `186639e731d78ea00939c5491311c599fb63d1c563777588ff186320aa311e4d`.
- `reference.py` SHA-256:
  `b22ed92b7581bcc9fdc82231f70ac1ac0ae7e7ba244e25443921c627dc13113c`.
- `run.py` SHA-256:
  `dc9c890173c12e6c5dfb2de39a99104f6d49fc5858e938c0c13ba73c3e1e34a4`.
- `test_reference.py` SHA-256:
  `1b41a87dffaa94c4ae29a57d304c40df58c244c441b5e8943479606980274658`.
- `verify.py` SHA-256:
  `7e6a00166c1c9b687001271a35c94a84bfc857573b310228ac5f518637732a41`.
- `tool-provenance.json` SHA-256:
  `e4b4f6e9f04da792a27fa60ebbf1821bc2d067b77693a65de50b11d7614d3f5d`.
- Tests: **36 passed, 0 failed, 0 skipped**.
- Flags: `controls_all_pass=true`, `alignment_pass=true`, `state_pass=true`,
  `all_outputs_finite=true`, `all_valid_frames_conserved=true`,
  `no_missing_result_qualifies_candidate=true`.

## Synthetic results (all estimates, not standards measurements)

| Condition | Applied gain | Input LUFS | Output LUFS | Error vs −23 LU | Output TP est. | TP headroom |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| Identity control | 1.000000 | −33.846402 | −33.846402 | −10.846402 LU | −17.166320 dBTP | +16.166320 dB |
| Fixed +6 dB control | 1.995262 | −33.846402 | −27.846402 | −4.846402 LU | −11.166320 dBTP | +10.166320 dB |
| Sample-peak control | 6.824907 | −33.846402 | −17.164467 | +5.835533 LU | −0.484385 dBTP | **−0.515615 dB** |
| Candidate static R128 reference | 3.485942 | −33.846402 | −23.000000 | 0.000000 LU | −6.319918 dBTP | +5.319918 dB |

The candidate hits its own LUFS target exactly on the synthetic speech cohort
because the same estimator is used in both passes; that is **internal
consistency, not independent accuracy**. The sample-peak control is a losing
control: it overshoots the loudness target and violates the −1 dBTP ceiling by
0.515615 dB. Identity and fixed-gain controls miss the loudness target by
10.846402 LU and 4.846402 LU respectively.

Other DSP observations:

- **Sweeps/steps:** frequency response and chirp/step gain error at most
  `0.000122 dB`; the transformation is one scalar, so no frequency-shaped
  response or time-varying gain is claimed.
- **Impulse:** peak input and output both at sample 4000; measured lag `0`;
  `D=0`. Loudness gain would be `8.413023`, but the true-peak ceiling reduces
  the gain to `1.782502`, output TP is exactly `−1.000000 dBTP` and loudness
  error is `−13.478442 LU`.
- **Silence:** no positive block, LUFS `null` with `no_positive_block`; gain
  falls back to identity `1.0`; output is all zero and finite.
- **Intersample peaks:** a `0.4/0.4` pair has sample peak `0.4` but cubic TP
  estimate `0.45` (`+1.023050 dB` overshoot). A sparse `0.9/0.9` pair case
  has TP estimate `1.0125` and forces true-peak-limited gain `0.880248`;
  output TP is `−1.000000 dBTP` and loudness error `−6.914641 LU`.
- **Near silence:** a 1 kHz tone at amplitude `0.001` reaches the `64x` safety
  cap with loudness error `−4.172401 LU`; this is recorded as an explicit
  limitation. A full-scale 1 kHz tone is scaled down without clipping.
- **Numerical/state:** NaN analysis is rejected with `nonfinite_input`; frames
  with missing/short/wrong shape/nonfinite/bad padding/stale epoch, duplicates,
  out-of-order, future packets, process after final and process after close are
  rejected without changing non-rejection counters. Reset to a higher epoch is
  bit-identical to a fresh session; sessions are uncoupled and the queue is
  empty after drain.
- **Partial final frame:** 37 valid samples in a flagged final 160-sample
  frame, with zero padding verified and all 1,317 valid samples conserved.

Nine regressions are recorded verbatim in `report.json["regressions"]`,
including the four control/target failures above, impulse and sparse
true-peak-capping errors, the gain cap, and the unimplemented LRA/dynamic-mode
targets. No losing control is hidden and no missing result qualifies the
candidate.

## Exact gates and reopening conditions

| Gate | Status | Exact reopening condition |
| --- | --- | --- |
| `local_external_tool` | blocked | Invoke an approved local FFmpeg build, capture exact `version`/`configuration` and hash, review its GPL dependency configuration separately, then run a synthetic two-pass loudnorm probe under an approved license. |
| `independent_ebu_meter` | blocked | Pin and independently review a licensed BS.1770/EBU Mode meter and remeasure frozen synthetic vectors with an explicit agreement protocol. |
| `ebu_test_set_and_programme_cohort` | blocked | Freeze an approved test set and complete-programme cohort with rights, targets and independent scoring. |
| `dynamic_mode_and_lra_enforcement` | blocked | Implement and independently test a deterministic dynamic-mode reference with explicit LRA and true-peak interaction. |
| `live_provider_intake` | blocked | Define and review an analyzer/host protocol with explicit lookahead and descriptor settings; no automatic registration or default. |
| `target_runtime_timing` | blocked | Measure the exact approved runtime on the target under pacing, load and bounded CPU/memory budgets. |
| `public_frame_boundary` | pass | Synthetic frame/epoch/reset/close behavior only; independent review is still required for any provider intake. |
| `dsp_profile_synthetic` | pass | DSP profile cohorts are complete; this is not a quality or standards claim. |
| `gpl_binary_exclusion` | pass | No FFmpeg binary, GPL component or licensed asset is vendored, downloaded, shipped or wrapped here. |

`no_missing_result_qualifies_candidate = true`: status is
`proposal_only_synthetic_incomplete`, `not_qualified`. No real programme
loudness measurement, listening result, independent-meter agreement, EBU test
set result, live-provider result or release claim is made.
