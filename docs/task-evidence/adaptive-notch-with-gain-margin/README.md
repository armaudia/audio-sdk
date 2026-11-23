# SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN — optional reference evidence

Task-local, synthetic/model-free DSP evidence for adaptive notch plus a bounded
gain margin on the public v0 provider boundary. It ships **optional and
unregistered** initially. The installed SDK, its ABI, descriptors, registry,
defaults and frozen v0 behaviour are unchanged. No real audio, trained model,
download, licensed runtime, listening test, device measurement, CPU/deadline
result, release qualification or benchmark ingestion is claimed.

This directory is distinct from the earlier `adaptive-feedback-notch` task
evidence. No file outside this directory was written; the sibling evidence,
shared `CMakeLists.txt`, `CONTRACTS.md`, public headers, descriptor registry and
all other worktrees were left untouched.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, exactly 160 samples/frame. There
  is no adapter-sized variant; any other frame size is outside v0 and is not
  implemented here.
- `fixture.py` is the deterministic reference: detector, narrow notches,
  bounded margin, fixed-gain control, recursive closed-loop simulator and all
  metrics. `report.py` emits the canonical report.
- `provider/` is an optional, task-local C provider built only by an explicit
  opt-in CMake consumer project. It uses only `audio_sdk/provider_v0.h` and
  `audio_sdk/session_v0.h`. With `AS_ENABLE_NOTCH_MARGIN=OFF` it is not
  compiled, linked or registered. With `ON` it registers exactly one provider
  on one caller-owned registry; no global/default registry is touched.
- The C provider is a boundary smoke check, not full numerical parity with the
  Python report. The fixed-gain comparison lives in the Python closed-loop
  matrix, where identical program material and loop conditions are enforced.

## Pinned sources (SHA-256)

| Path | SHA-256 | Use |
| --- | --- | --- |
| `research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | Source evidence: recursive loop model, 14 dB pilot prominence, 3 dB notch+margin, −5 dB fixed margin, false-trigger and closed-loop cautions. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech, gain/response, attack/release, headroom, delay, numerical behaviour, state transitions, interacting nonlinear configurations. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table boundary (source pin). |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session boundary (source pin). |

`audio-benchmark-platform/plan/swarm/TASKS.json` is mutable shared board state.
Its read-time digest is recorded as a snapshot in `contract.json` and in the
report fixture specification; it is not a qualification source and does not
gate any result. The source research reports 19 false notch activations over
12 utterances and no production sign-off, so false-trigger, tone-artifact and
loop-stability controls are reported explicitly rather than hidden.

Pinned base: `9677040cba2929f9936eaa565f200f585d5270a8` (origin/main at
dispatch). Branch: `swarm/SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN`.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `a12365ccde27bbfe170b247dd1988be85aee13c7ea5609ed2e84efc08353d32f` |
| `report.py` | `3d7581ea581e7aa2119980699fa5697101d4a66eda695510b9a331dc3b31a576` |
| `report.json` | `b6732740cab7fafd9e270953d7b8f72b6d7951ee5e6d08c1e344a6e9ed228645` |
| `report.json.sha256` | `d81c48510761405650a81fd47861f859b69b78e4714432d63e10443864b5270b` |
| `test_fixture.py` | `d9aebec6370d77aa99a1d5fd334cd61580716d22cfe65095d3cc8b2af14adc1d` |
| `provider/CMakeLists.txt` | `c7e188d66f55dd7fefffa203c7128f52f44d216daa502417d6e3808bf377c0a2` |
| `provider/margin_provider.c` | `9cfd306bc831c7d220688a1faf140961cd91dd15f39208e4f7f8f2eaabe1cfd6` |
| `provider/config/config.json` | `ed0a42d5f2410b8cbcfa6d8cce6e666350afc1f7d7d3fd488ed39eb7626e30f6` |
| `provider/config/descriptor.h.in` | `5976b5b325c10d42a16d6b66109405f892af30d94bb4a09258914f0f3184e9df` |
| `provider/tests/test_provider.c` | `57d91132cf2721fb98d8bc219196b36390ecc902802df449e5c246f3654abf6e` |

`report.json` is canonical JSON (sorted keys, compact separators, no trailing
newline, `allow_nan=False`); the file digest above is also its canonical report
digest. `fixture_digest` inside the report
(`9a1bb542f21987d3309d9debdd0cee38d28b4a28d000db4fdeb669d563a94857`)
pins the format, controls, seeds and loop specification. The checked-in
`report.json.sha256` file is authoritative and is verified by the test suite.

## Reproduction (from this directory)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 report.py > /tmp/notch-margin-report.json
shasum -a 256 /tmp/notch-margin-report.json report.json
cmp /tmp/notch-margin-report.json report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

The test suite regenerates the report in memory and asserts byte equality with
`report.json`, so any drift in fixture, seeds or metrics fails closed. Python
3.11.5 stdlib only was used for the frozen report.

Optional C boundary check (SDK build and installs live outside the worktree):

```sh
WT=<worktree root>
TMP=<scratch dir>
cmake -S "$WT" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 2
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"
cmake -S "$WT/docs/task-evidence/adaptive-notch-with-gain-margin/provider" \
  -B "$TMP/off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" -DAS_ENABLE_NOTCH_MARGIN=OFF
cmake --build "$TMP/off" --parallel 2 && ctest --test-dir "$TMP/off" --output-on-failure
cmake -S "$WT/docs/task-evidence/adaptive-notch-with-gain-margin/provider" \
  -B "$TMP/on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" -DAS_ENABLE_NOTCH_MARGIN=ON
cmake --build "$TMP/on" --parallel 2 && ctest --test-dir "$TMP/on" --output-on-failure
```

Result: OFF build left the provider unlinked/unregistered with built-ins
unchanged (1/1 ctest); ON build registered one caller-local provider,
attenuated a sustained 1 kHz tone, rejected unsupported modes, missing config
bytes, wrong format, stale epoch, wrong position and nonfinite input, then
passed reset/drain/close (1/1 ctest).

Read-only board check, from the workspace root:

```sh
python3 plan/swarm/check.py --task SDK-ADAPTIVE-NOTCH-WITH-GAIN-MARGIN
git diff --check
```

## Synthetic DSP results

All values come from `report.json`; every stimulus is analytic or seeded LCG.
No missing result is treated as a pass.

- Format and delay: impulse peak at sample 0, step crossing 0 samples,
  silence peak 0.0 with zero activations, `buffering_delay_samples: 0`.
- Gain/response: fixed −5 dB control measured 0.562341325190352 linear gain
  against 0.562341325190349 configured; 39/39 swept frequencies activated the
  detector, steady gain 0.00218–0.08788; 300-frame chirp produced 21
  activations.
- Attack/release: 1 kHz burst from frame 20 to 120 activated at frame 23
  (3-frame attack), released at frame 143 (23-frame release), one margin step
  to −3 dB, transitions `idle->active@23:1000`, `active->idle@143:1000`.
- Clean-speech-like input: 0 false activations in 300 frames for both notch
  profiles; the fixed-gain control attenuates the same input as intended.
- Tonal-vowel stress: 5 activations in 300 frames (10.0/minute) and four margin
  steps reaching the −12 dB floor. This false-trigger risk is reported, not
  suppressed. Injected 1 kHz tone in speech: one activation in the tone
  region, zero in the clean region, tone power reduced from −26.408 to
  −40.132 dB; clean-region tone ratio unchanged at −15.436 dB.
- Headroom/nonlinearity: 3.0-peak input with tanh interaction produced peak
  0.799117, 11.49 dB headroom to input peak and zero nonfinite samples.
- Closed loop: six cases × four controls = 24 runs. Cases are loop gains
  1.05/1.15/1.30 on a linear path plus 1.15 with pre-tanh, post-clip and dual
  resonant paths. In every case the fixed −5 dB control decayed with zero
  rejected frames, and notch+bounded-margin also decayed with zero rejected
  frames and at least one detection plus margin step. Identity and notch-only
  either ran away until frames were fail-closed/rejected (linear/dual paths)
  or sustained feedback with pre-tanh/post-clip nonlinearity. Example at
  1.15/linear: fixed tail −42.7 dB and program SDR 7.1 dB; notch+margin tail
  −47.1 dB, program SDR −11.0 dB, margin floor −6 dB. The fixed control is
  therefore the level-preservation leader on this synthetic loop; the
  adaptive candidate buys tail suppression with speech attenuation and
  false-trigger risk. This is a comparison, not a product selection.
- Adverse controls: nonfinite, wrong-shape, out-of-range, stale-epoch and
  wrong-position frames are rejected with state unchanged. Missing, unknown,
  wrong-type, nonfinite, out-of-range and stale-profile settings fail closed.
  Reset, close and instance independence are explicit; the C boundary adds the
  same invalid-mode/session checks at the public API.

## Deferrals, blockers and reopening conditions

No measurement here establishes gain-before-feedback, maximum stable gain,
real-world false-trigger rate, speech intelligibility/quality, target-device
latency, CPU/memory/deadline compliance or production safety.

1. **Measured loop evidence missing.** Reopen with pinned loudspeaker/mic IRs,
   calibrated gain-before-feedback, delay drift, path changes and amplifier
   saturation on an instrumented physical loop.
2. **Held-out perceptual evidence missing.** Reopen with speaker/path-held-out
   real speech and music false-trigger plus authorized listening or a
   separately labeled intelligibility screen; MOS/STOI are not claimed here.
3. **Runtime qualification missing.** Reopen with maximum stable gain, residual
   tone, attack/release, clipping, latency and CPU/memory on the intended
   target runtime under paced load.
4. **Release/rights review missing.** Reopen only after provider intake,
   license/notice review, descriptor and public catalog review; until then this
   provider stays OFF by default, unregistered and outside the installed SDK.
5. **Benchmark ingestion missing.** These results are not an `audio_bench`
   bundle and were not validated by `python -m audio_bench validate`; no
   hosted submission or publication claim is made.

Until those gates pass, the installed v0 behaviour remains frozen and this
directory remains optional task-local reference evidence.
