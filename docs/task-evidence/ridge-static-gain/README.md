# SDK-RIDGE-STATIC-GAIN — deterministic synthetic static-gain held-out evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
a minimal static-gain reference with a peak ceiling. The candidate is modelled
in Python at the public audio-sdk v0 boundary. It is **synthetic, optional,
unregistered and OFF by default**, and **no default strategy is selected or
advertised**. It changes no installed SDK behavior, public API/ABI, descriptor
registry, registry default, `CONTRACTS.md`, build text, board, handoff, other
worktree or branch. The installed v0 geometry is untouched: **16 kHz, mono,
float32, exactly 160 samples per call**.

## Public-boundary model

The model mirrors `as_session_process_v0` / `as_session_drain_next_v0` for a
stateless inline provider:

- one padded 160-sample input frame per call; `valid_count` is 1–160, with a
  partial final frame carrying `AS_FINAL_INPUT` and zero caller padding;
- one produced 160-sample output frame with `source_first_sample =
  first_input_sample`, i.e. declared buffering/content delay **D = 0**; the
  impulse probe measures 0 samples of content lag;
- static strategies apply **one fixed scalar gain per session** (calibrated
  before frame admission), so there is no attack/release and no per-frame
  adaptation; `drain` emits no audio and reports a single EOS;
- peak policy is `min(direct_gain, ceiling / input_peak, max_gain)` with
  `ceiling = 0.85` and `max_gain = 64`; it is a gain cap, **not hard clipping**;
- silence (RMS = 0) falls back to identity gain rather than infinity;
- nonfinite input, bad padding, wrong counts, stale epochs, duplicates,
  out-of-order/future frames and processing after final are rejected by the
  facade boundary without advancing state.

No provider is compiled, registered or packaged. The conceptual ID
`dsp.ridge-static-gain-ref.v0` is recorded with `registered=false`,
`enabled_by_default=false`, `default_selected=false`, `descriptor_settings={}`.
There is no new descriptor field, no new public flag and no provider intake.

## Held-out comparison design

The frozen cohort has 240 one-second 16 kHz clips (seed `20261028`), split by
clip index into **180 train** (`0..179`) and **60 held-out** (`180..239`) with no
shuffling or overlap. Each clip is a deterministic harmonic/formant surrogate
with voiced, unvoiced and pause-floor regions, perturbed by a frozen RMS level
in `[-36, -12] dBFS`. Clips with `index % 7 == 3` carry a frozen overloaded
transient that makes the ceiling bind (8 held-out clips).

Strategies scored on the same held-out clips:

| Strategy | Definition |
| --- | --- |
| `no_gain` | identity control, no ceiling protection |
| `target_rms` | direct dB rule from the held-out clip's measured RMS, with ceiling/gain clamp |
| `ridge` | one-feature ridge fit on **train only**: `x = log10(measured RMS)`, `y = log10(applied capped gain)`, λ = `1e-6`, then applied to held-out `x` with the same safety cap |
| `envelope_agc` | stateful attack/release control (2/8 frames) with peak protection; a control, not the static reference |

The label intentionally includes the ceiling cap, so the linear ridge estimate
cannot represent the capped region exactly. This is an honest, unfavourable
result for ridge; the direct rule remains the reference and **no strategy is
promoted to a default**.

## Files

| Path | Purpose |
| --- | --- |
| `reference.py` | Deterministic generator, v0 boundary session model, static/ridge/no-gain/envelope strategies, DSP probes, metrics and report writer. |
| `run.py` | Regenerates `report.json` and `report.json.sha256` byte-for-byte from frozen inputs. |
| `report.json` | Canonical machine-readable DSP report (193,098 bytes, sorted keys). |
| `report.json.sha256` | sha256sum-style digest line for the committed report. |
| `test_reference.py` | 30 Python unittest checks; no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, regeneration, licensing and write-scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every pinned external file and task artifact. |
| `README.md` | This file. |

## Pinned source and artifact digests (SHA-256)

External paths are relative to `/Users/htsakanyan/workspace/audioml` (`source:`)
or this worktree. The full machine-checked set is in `SOURCES.sha256`.

| Path | SHA-256 |
| --- | --- |
| `source:research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `reference.py` | `b9b09816bb6a44df340e52a2e994ba7b7c4776698b002b9bf4887119c711b28b` |
| `run.py` | `ce1e263ee3e5425696431719c42ce9cb537c3a5532ab5c5de41a0a5493e8e600` |
| `test_reference.py` | `e9a1785fd5c27e2ce04135f891ef9f06682ca43d4437b195da688beb8f9a8d9c` |
| `verify.py` | `4b9250986128b210564ad5b51d350b7efc92acec4ce54b04e4422e5e0acca155` |
| `report.json` | `a0a81ae8ff9d7d966b1a47d6ac001f14fc0c4a7a82be316c8f5522ed06c37e2a` |
| `report.json.sha256` | `65a75dddfa582d430c84fa0ffd293b9082986b4b4e133743597fe8ab4590a34f` |

The pinned research document reports source-reported held-out values of
0.000 dB (ridge static gain), 3.825 dB (envelope AGC), 4.414 dB (identity) and
2.577 dB RMSE (EQ estimate) on its own synthetic screen. Those numbers are
**context only**: this fixture uses its own frozen generator, target, ceiling
and stateful control and does **not** reproduce or pool them. It reproduces the
*experimental structure* — train/held-out split, direct target-RMS reference,
no-gain control and a ridge estimate — before any default selection.

## Reproduction

From this directory, with the pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-RIDGE-STATIC-GAIN
```

`run.py` rewrites `report.json` and its digest file; `verify.py` regenerates the
report in memory and requires exact byte equality. Pinned base commit:
`bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`.

## Expected counts and digests

- Cohort: 240 clips × 16,000 samples = 3.84 M synthetic samples; 180 train /
  60 held-out; target `-24.0 dBFS` RMS, ceiling `0.85`, max gain `64`, ridge λ
  `1e-6`, seed `20261028`.
- Held-out streams: 60 clips × 4 strategies × 100 frames = 24,000 accepted
  process calls; every stream ends with one EOS drain result.
- Fixture spec digest:
  `87e902ebd4e6fba4c450c6205ca785835adbc27c77d76ea35c72fc12650f20fb`.
- Ridge fit: slope `-1.177793`, intercept `-1.681723`, train items `180`;
  feature/label digests `5d0f14d8fb98dcd0ed30250527fc55538d9cd77b9e58b99ce34bfe52c3ef455e` /
  `a1400bfefd5c6ac7dbdad1e4f39944b244081b929277110b822e85f79d23aff5`.
- `report.json` SHA-256:
  `a0a81ae8ff9d7d966b1a47d6ac001f14fc0c4a7a82be316c8f5522ed06c37e2a`.
- Tests: 30 passed, 0 failed, 0 skipped (pinned Python 3.12.16).
- Flags: `controls_complete=true`, `all_outputs_finite=true`,
  `no_missing_result_qualifies_candidate=true`, `default_selected=false`.

## Held-out results (synthetic; lower absolute RMS error is better)

| Strategy | Mean abs RMS error (dB) | RMS of error (dB) | Max abs error (dB) | Max peak | Clipped samples | Ceiling-bound clips |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `target_rms` | 2.290003 | 6.299514 | 18.841516 | 0.85 | 0 | 8 |
| `ridge` | 4.234889 | 6.729790 | 18.841516 | 0.85 | 0 | 8 |
| `no_gain` | 17.213793 | 18.351371 | 29.522561 | 1.123759 | 8 | 0 |
| `envelope_agc` | 0.561937 | 0.669930 | 1.483478 | 0.85 | 0 | 60 |

Paired mean-absolute-error deltas against the direct `target_rms` reference:
ridge **+1.944886 dB (worse)**, no-gain **+14.923790 dB (worse)**,
envelope AGC **−1.728066 dB (better)**. Each strategy is worse than the direct
rule on 52 of 60 held-out clips. The 8 ceiling-bound overloaded clips produce
18.841516 dB error for both direct and ridge gains: the peak ceiling prevents
an exact RMS target. These are synthetic observations only; the stateful
envelope control's advantage on stationary one-second clips is **not** a reason
to select a default, and no such selection is made.

All 164 explicit regressions are recorded verbatim in
`report.json["held_out"]["regressions"]`: 52 ridge-worse, 52 no-gain-worse,
52 envelope-worse and 8 ceiling-tradeoff entries. `no_gain` produces 8 samples
at or above 1.0 on overloaded inputs, while every ceiling-protected strategy
stays at or below 0.85 with zero nonfinite samples.

## DSP profile probes

- **Sweep** (20 Hz–8 kHz exponential, 200 frames): one static gain
  `0.405661`, ten-band gain-ratio flatness `0.000000 dB`; no frequency shaping.
- **Steps** (eight 25-frame levels from −42 to −6 dBFS, 200 frames): static
  gain has exactly one value and cannot track steps; the envelope control has
  176 distinct gain values on the same probe.
- **Impulse** at source sample 4000: measured output peak at 4000, content lag
  `0`, one nonzero output sample, exact per-frame source mapping.
- **Silence**: identity fallback gain `1.0`, output peak `0`, headroom `0.85`,
  zero nonfinite samples.
- **Synthetic speech** (125 frames, voiced/unvoiced/pause-floor): one static
  gain `0.510168` across all 20 regions; SNR is unchanged and no noise gating
  occurs. The no-gain control is bit-identical to the input.
- **Headroom/peak** (frozen transient, input peak `2.207805`): raw gain
  `0.485860` capped to `0.384998`, output peak `0.850000`, zero samples at or
  above 1.0, zero hard clipping.
- **Numerical/state**: nonfinite, bad-padding, stale-epoch, duplicate,
  out-of-order, future, after-final, closed and invalid-gain inputs are each
  rejected without changing state; reset to a higher epoch is bit-identical to
  a fresh session and rejects stale frames; sessions are uncoupled.
- **Interacting nonlinearity**: attack/release smoothing plus the same ceiling
  and gain clamp produce 98 distinct gains and 94 ceiling-bound frames on the
  overloaded transient; the report states explicitly that smoothing and the
  cap interact.
- **Final partial window**: 7 full frames plus 37 samples; final flag `2`,
  1157 valid content samples, zeroed padding, 8 produced frames.

## Exact gates and reopening conditions

`no_missing_result_qualifies_candidate = true`: any missing metric, blocked
gate or failed control keeps the candidate `not_qualified`. Status is
`proposal_only_synthetic_incomplete`; nothing here supports a release, quality
or default claim.

| Gate | Status | Exact reopening condition |
| --- | --- | --- |
| `real_speech_benchmark` | blocked | Freeze a permitted, speaker/session-split paired cohort with fixed crop, RMS target and peak policy. |
| `blinded_listening_quality` | blocked | Run an independently reviewed blinded listening and intelligibility protocol on permitted material. |
| `pinned_external_controls` | blocked | Pin WebRTC AGC2 / FFmpeg code, version, license, hashes and runtime, then rerun the same cohort. No such tool or asset is installed here and none was downloaded. |
| `target_runtime_deadline` | blocked | Measure the exact installed build on the target under pacing, load, deadline, CPU and memory budgets. |
| `provider_intake` | blocked | Independent opt-in provider review with OFF default, empty descriptor settings and clean SPDX headers. |
| `default_selection` | blocked | Joint review of real-speech cohort, listening result and pinned external controls before any default is chosen. |

No real audio, download, licensed runtime, device, listening result, external
benchmark, provider registration or shared-source change is used.
