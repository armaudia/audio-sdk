# Block-NLMS AFC — synthetic task evidence

Task: `SDK-BLOCK-NLMS-AFC` · candidate: `dsp.block-nlms-afc.afcref.v0` ·
status: **evidence_complete_synthetic_only**.

## Delivery

- Base: `dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc`
- Branch: `swarm/SDK-BLOCK-NLMS-AFC`
- Pull request: https://github.com/armaudia/audio-sdk/pull/45 (opened against `main`, not merged)
- Evidence commit at PR creation: `aa4556b9d503541b290be19dc6a86266533c89a9`
- Exact final delivery head SHA: recorded in the task response

## Scope and measurement separation

Task-local optional reference at the public v0 provider boundary. Not
installed, not a default, no real weights, no downloads, no licensed runtime,
no listening and no release qualification. Installed v0 remains 16 kHz mono
f32, 160 samples/frame.

Reference/adaptation sections: `echo_return_loss`, `convergence`, `tracking`,
`double_talk`, `reference_latency`, `frequency_sweep`, `chirp_sweep`.

Attenuation/stability sections: `gain_before_feedback`, `adverse_loop`,
`headroom_and_nonlinearity`.

Shared waveform controls: `impulse`, `silence`, `step`, `clean_speech`.

ERLE and weight convergence do not measure loop attenuation or
gain-before-feedback. Closed-loop gain values do not measure reference-path
quality. Simulator-relative gains are not physical acoustic measurements.

## Reference and adaptation evidence

All fixtures are deterministic analytic or seeded f32 arrays pinned by
`fixtures/FIXTURES.sha256`. The reference asset is explicitly supplied by the
caller; missing, wrong-id, wrong-size, wrong-digest, short, nonfinite or
out-of-range references are rejected.

| measurement | result |
| --- | ---: |
| Echo-only ERLE early (frames 0–19) | 3.795 dB |
| Echo-only ERLE steady (frames 80–159) | 8.040 dB |
| Echo-only ERLE final frame | 9.082 dB |
| Frames to 6 dB trailing mean | 23 |
| Frames to 9 dB trailing mean | 104 |
| False double-talk frames (echo only) | 0 |
| ERLE before path change | 6.583 dB |
| ERLE immediately after path change | 8.291 dB |
| ERLE late after path change | 7.477 dB |
| Double-talk ERLE (frames 80–159) | 1.511 dB |
| Echo-only comparison ERLE | 7.999 dB |
| Double-talk near-end SDR | 8.607 dB |
| Double-talk frames / mode transitions | 44 / 64 |
| Frequency sweep ERLE min / max | 41.953 / 44.287 dB |
| Chirp ERLE (frames 100–119) | 7.614 dB |
| Impulse / step added delay | 0 / 0 samples |
| Silence peak output | 0.0 |
| Clean-speech RMS ratio / envelope screen | 1.0 / 1.0 |

Double-talk bias is reported, not qualified away: correlated playback and
near-end speech can bias adaptation; the coherence/power freeze limits but does
not remove it. The clean-speech screen is a pinned synthetic envelope
correlation, not standard STOI.

Reference latency evidence includes a causal closed-loop lag sweep (0, 8, 16,
32 samples), an offline adaptation lag sweep (0, 4, 8, 16, 32 samples) and an
offline leading-reference sweep (4, 16, 32 samples). Zero lag is best. Leading
reference is generated via fixed asset advance for offline adaptation only and
is explicitly noncausal for live v0 streaming. Positive closed-loop lag rows
show rejected frames or degraded program SDR rather than being counted as
wins.

## Attenuation and stability evidence

Gain-before-feedback uses a frame-causal recursive loop
`mic = program + G * delayed_returned_playback`; all values are
simulator-relative dimensionless loop gains.

| profile | max stable loop gain | Δ vs identity | tail at G=0.8 | program SDR at G=0.8 |
| --- | ---: | ---: | ---: | ---: |
| identity | 0.6 | 0.000 dB | -15.157 dB | 4.705 dB |
| afc | 1.2 | +6.021 dB | -24.072 dB | 7.789 dB |
| afc_margin | 1.6 | +8.519 dB | -41.655 dB | 9.680 dB |
| fixed_margin | 1.2 | +6.021 dB | -41.929 dB | 7.331 dB |

At G=1.2, identity and plain AFC are rejected or lose program fidelity, while
margin profiles remain decaying with program SDR around 7 dB. The adverse loop
at G=1.2 covers dual return paths, pre-tanh nonlinearity and post-clip
limiting: identity produces sustained feedback in the nonlinear conditions and
fail-closed rejections in the dual-path condition; margin profiles remain
decayed without clipped samples. Post-clip identity clips 21,076 samples;
margin profiles clip 0. These are closed-loop simulator results only.

Headroom to input peak is 1.937 dB at input peak 3.0 and output peak 2.400359;
no nonfinite samples or clipped output samples occur at G=1.2 in the measured
headroom condition.

## Numerical, state and load controls

- Rejections: nonfinite frame, out-of-range frame, stale epoch, wrong position,
  wrong shape; missing/nonfinite/out-of-range/short reference; missing,
  nonfinite, out-of-range, unknown-key, wrong-profile and wrong-taps config.
  Every rejection status begins with `rejected_`.
- State is unchanged on rejection; reset reproduces byte-identical output;
  two live sessions keep independent state; closed-session status is `closed`.
- State-transition suite records 79 unique transitions and confirms reset
  changes work state.
- Load proxy: 1 block update/frame, 5,120 multiply-accumulates/frame, 128
  f32 weight bytes. CPU seconds and deadline margin are explicitly not
  measured. Buffering delay is 0 samples in every waveform control.
- `verify.py` fails closed on any absent or nonfinite report value.

## Test counts

| suite | result |
| --- | ---: |
| Full SDK CTest (default test/conformance targets) | 11/11 passed |
| Consumer `AS_ENABLE_BLOCK_NLMS_AFC=OFF` | 1/1 passed |
| Consumer `AS_ENABLE_BLOCK_NLMS_AFC=ON` | 1/1 passed |
| Python `test_reference.py` | 9/9 passed |
| `tools/verify.py` | passed |

`verify.py` checks 12 source-pinned files, 7 fixture files, 5 external
source/boundary headers, 17 required sections, recursive absent/nonfinite
values and byte-identical report regeneration.

## Gates

All evidence gates report `result: passed` except `release_qualification`,
which is `not_performed`. Every gate has `release_gate: blocked`.

## Digests

- `SOURCES.sha256`: `26522ccb48ec9ad14eb763c97beaf50c3ec9142f74d965e7591e573b8f509efa`
- `fixtures/FIXTURES.sha256`: `0fe388c234e65865c51e2919415605bf8050fd2d2de81ad424e2c9f2fb4d4ddf`
- `evidence/report.json`: `8f61033f4a27ccfa1cd0e0193c5a9b4ba022fd0f38144fc940005941a528a069`
- `fixtures/reference_asset.f32`: `79639f2ff6af92657a99206d963beb38c50a286504b163222d9200c85b289085`

## Full file list

```text
SOURCES.sha256
README.md
evidence/REPORT.md
evidence/report.json
fixtures/FIXTURES.sha256
fixtures/impulse.f32
fixtures/near_end.f32
fixtures/playback_a.f32
fixtures/playback_b.f32
fixtures/reference_asset.f32
fixtures/silence.f32
fixtures/step.f32
provider/CMakeLists.txt
provider/config/config.json
provider/config/descriptor.h.in
provider/src/block_nlms_afc_provider.c
provider/src/block_nlms_afc_provider.h
provider/tests/test_provider.c
tools/afc_reference.py
tools/evaluate.py
tools/generate_fixtures.py
tools/test_reference.py
tools/verify.py
```

## Exact blockers and reopening conditions

1. Live playback-reference delivery requires a future public API extension;
   v0 has no reference field in `as_frame_v0`. Reopen when a reviewed ABI
   contract exists and the provider consumes a live reference without pinned
   asset replay.
2. No measured acoustic room or feedback loop, calibrated geometry or loop-gain
   reference exists. Reopen with device and pinned measurement setup.
3. No real weights, licensed runtime, listening test, MOS or real-speech
   evaluation. Reopen with rights-cleared material and blinded listening.
4. No target-device timing, CPU/deadline, RSS or concurrent-load measurement.
   Reopen with target hardware and pinned build/toolchain.
5. Descriptor intake, license and release review are not performed. Reopen
   with reviewer sign-off before any release claim.

No board record, handoff, other worktree, other branch, PR, ruleset, shared
`CMakeLists.txt`, `CONTRACTS.md`, public API/ABI, descriptor registry, default
or installed v0 behavior was changed. Main was not merged.
