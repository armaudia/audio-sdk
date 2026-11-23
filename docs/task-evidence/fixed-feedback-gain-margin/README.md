# SDK-FIXED-FEEDBACK-GAIN-MARGIN — optional reference evidence

Task-local, synthetic/model-free DSP evidence for a bounded fixed feedback gain
margin on the public v0 provider boundary. It ships **optional, unlinked,
unregistered and OFF by default**. The installed SDK, its ABI, descriptors,
registry, defaults, public API/ABI and frozen v0 behaviour are unchanged. No
room, physical-loop, device, model, listening, target-timing, benchmark or
release claim is made.

No file outside `docs/task-evidence/fixed-feedback-gain-margin/` was written.
The shared `CMakeLists.txt`, `CONTRACTS.md`, public headers, descriptor
registry, board state, other branches, other worktrees and `main` were not
modified.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, exactly 160 samples/frame. There is
  no adapter-sized variant; any other format is rejected.
- `fixture.py` owns the deterministic DSP, all metrics and the recursive
  synthetic feedback-path trials. `report.py` writes canonical JSON to stdout.
- `provider/` is an opt-in CMake consumer check using only the public v0
  provider and session headers. With `AS_ENABLE_FIXED_FEEDBACK_MARGIN=OFF` the
  provider is not compiled, linked or registered. With `ON` it registers one
  provider on one caller-owned registry only.
- The C provider is a boundary smoke check, not the numerical authority. The
  full gain, sweep, speech, headroom and feedback-path matrix lives in the
  Python report.
- The static gain stage has no detector, adaptation, room model or loop state.
  Attack/release are explicitly marked `not_applicable_static_bounded_gain`.
- The research's −5 dB fixed margin is a conservative baseline comparator, not
  a production selection. `report.json` records `selected: null` and no
  candidate is eligible for selection while release gates remain open.

## Pinned sources (SHA-256)

| Path | SHA-256 | Use |
| --- | --- | --- |
| `research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | Research comparator: fixed −5 dB fallback, recursive-loop cautions and no production sign-off. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech, gain response, headroom, delay, numerical and state controls. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table boundary. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session boundary. |

`audio-benchmark-platform/plan/swarm/TASKS.json` is mutable shared board state.
Its read-time digest `7e27b37f6d53cc76a96bab73b2f24ec7983ea05a03e1562e5963975378e7cbfd`
is recorded as a snapshot; it is neither a qualification source nor a gate.

Pinned base: `dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc`. Branch:
`swarm/SDK-FIXED-FEEDBACK-GAIN-MARGIN`.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `36e003772e1ea1dd215062ed00829287dbb6cab60b6f5e9573bb982921bec333` |
| `report.py` | `3d7581ea581e7aa2119980699fa5697101d4a66eda695510b9a331dc3b31a576` |
| `report.json` | `c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf` |
| `report.json.sha256` | `3fe70839215e787a1f4e78595475c062eae51cac7b85c3bd8d0b8afe84f72b8f` |
| `test_fixture.py` | `a2f5e61f96c50250849eba450269df79964b1788f52cbdeb848837b53f51b470` |
| `provider/CMakeLists.txt` | `288c81d38bea8b2a9ec257490196459cf161cffc9cebdaae73feab94c39ffbf2` |
| `provider/fixed_gain_provider.c` | `8d49add2f5ee367be1d375dd3d897ef2551be584107a85ca1f8a85872dc46e0f` |
| `provider/config/config.json` | `528f1c3ee558f5b75f3e61e7def0cea9cea32293e8e8b734b4ccc331471e6f33` |
| `provider/config/descriptor.h.in` | `7b194f6598e79076c855244c18a7d11c523055331d83d0a26dff293ed58b441a` |
| `provider/tests/test_provider.c` | `7581c0454bcc56308a408221afac60ef321e63bfe10a622511ba4f7a5a11113e` |

`report.json` is canonical JSON (sorted keys, compact separators, no trailing
newline, `allow_nan=False`); its SHA-256 is also the canonical report digest.
`fixture_digest` inside the report is
`9c124fa104cfe0666166a3a6131d07040455d01ae5f7782e1220c60dd6d1105d`; it pins
the format, controls, seeds, explicit FIR taps, delays, loop gains and
nonlinearities. The checked-in `report.json.sha256` is authoritative.

## Reproduction (from this directory)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 report.py > /tmp/fbmg-report.json
shasum -a 256 /tmp/fbmg-report.json report.json
cmp /tmp/fbmg-report.json report.json
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
```

The test suite regenerates the report in memory and asserts byte equality with
`report.json`; any drift in fixture, seeds or metrics fails closed. Python
3.11.5 stdlib only was used for the frozen report.

Optional C boundary check (SDK build/install lives outside the worktree):

```sh
WT=<worktree root>
TMP=<scratch dir>
cmake -S "$WT" -B "$TMP/sdk" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk" --parallel 4
cmake --install "$TMP/sdk" --prefix "$TMP/prefix"
cmake -S "$WT/docs/task-evidence/fixed-feedback-gain-margin/provider" \
  -B "$TMP/off" -DCMAKE_PREFIX_PATH="$TMP/prefix" -DAS_ENABLE_FIXED_FEEDBACK_MARGIN=OFF
cmake --build "$TMP/off" --parallel 2 && ctest --test-dir "$TMP/off" --output-on-failure
cmake -S "$WT/docs/task-evidence/fixed-feedback-gain-margin/provider" \
  -B "$TMP/on" -DCMAKE_PREFIX_PATH="$TMP/prefix" -DAS_ENABLE_FIXED_FEEDBACK_MARGIN=ON
cmake --build "$TMP/on" --parallel 2 && ctest --test-dir "$TMP/on" --output-on-failure
```

Result: OFF left the provider unlinked and unregistered with built-ins unchanged
(1/1 ctest); ON registered one caller-local provider, measured 0.562341323 gain
against 0.562341325 expected on a 1 kHz tone, rejected unsupported modes,
missing config bytes, wrong format, stale epoch, wrong position and nonfinite
input, then passed reset/drain/close (1/1 ctest).

Read-only checks, from the workspace root:

```sh
python3 plan/swarm/check.py --task SDK-FIXED-FEEDBACK-GAIN-MARGIN
git diff --check
```

## Synthetic DSP results

All values come from `report.json`. Every stimulus is analytic or generated by
a fixed-seed LCG. No missing result is treated as a pass.

- Format/delay: silence peak 0.0 with zero activations; impulse peak at sample
  0 with 0 added delay; step crossing at 0 samples; `buffering_delay_samples: 0`.
- Gain/response: configured gain −5.0 dB, measured 0.562341325190 linear
  (0.562341325190 configured), measured gain −5.0 dB. All 39 frequencies from
  200 Hz to 4 kHz measured 0.562341325 linear gain; 300-frame chirp passed.
- Steps/impulses: static bounded gain has zero attack, zero release and zero
  gain changes; step settling is 0 frames.
- Clean-speech-like input: identity RMS ratio 1.0; −3/−5/−8 dB controls measured
  0.707945784/0.562341325/0.398107171 with correlation 1.0 to the scaled
  program. Tonal-vowel crest factor is unchanged at 2.346056.
- Headroom/nonlinearity: 3.0-peak input produced 1.687301 peak with linear gain
  (4.999 dB headroom) and 0.449376 with tanh interaction (16.49 dB headroom),
  both with zero nonfinite samples.
- Synthetic feedback paths: two explicit three-tap symmetric FIRs with reported
  taps, 1-sample FIR group delay, bulk delays 319/239 samples and aligned
  positive-feedback phase at 1 kHz/2 kHz. Six cases × four controls = 24 full
  runs; all 12 required metrics are present and finite in every row. Cases
  cover loop gains 1.05/1.15/1.30 on the linear path, 1.15 with pre-tanh and
  post-clip, and 1.0 on the second path.
- Bounded-gain outcome: −5 dB and −8 dB decayed in all 24 bounded-control rows
  with zero rejected frames, negative feedback growth and tail decay from
  −8.838 dB to −81.439 dB. −3 dB decayed in four cases but sustained feedback
  in three and fail-closed at loop gain 1.30. Identity sustained or fail-closed
  in every case. These are recursive-simulator proxies only: no room, physical
  loop, loudspeaker, amplifier or device behaviour is inferred.
- Program-quality trade-off: at loop gain 1.15/linear, −5 dB had tail −15.024 dB,
  tail decay −34.496 dB and program SDR 3.051 dB; −3 dB had tail 2.225 dB and
  SDR −8.949 dB; −8 dB had tail −26.960 dB and SDR 5.013 dB. This is a
  comparison across synthetic paths, not a selection.
- Completeness rule: `no missing result may qualify a candidate`; every candidate
  reports `all_results_present: true`, `missing_results: []`, five open release
  gates, `eligible_for_selection: false`, and `selected: null`.
- Adverse controls: nonfinite, wrong-shape, out-of-range, stale-epoch and
  wrong-position frames are rejected with DSP state unchanged. Missing, unknown,
  wrong-type, nonfinite, out-of-range and stale-profile settings fail closed.
  Reset, close and instance independence are explicit; the C boundary repeats
  the invalid-mode/session checks at the public API.

The −600 dB values in zero-energy metric cells are the finite 1e-30 numerical
clamp recorded in the report, not measured values.

## Deferrals, blockers and reopening conditions

No measurement here establishes gain-before-feedback, maximum stable gain,
real-world path phase/delay drift, speech intelligibility/quality, target-device
latency, CPU/memory/deadline compliance or production safety.

1. **Measured loop/path evidence missing.** Reopen with pinned
   loudspeaker/microphone IRs, calibrated gain-before-feedback, delay drift,
   path changes and nonlinear saturation on an instrumented physical loop.
2. **Held-out perceptual evidence missing.** Reopen with held-out real speech
   and music plus authorized listening or a separately labeled intelligibility
   screen; MOS/STOI are not claimed here.
3. **Target runtime qualification missing.** Reopen with maximum stable gain,
   residual tone, clipping, latency and CPU/memory on the intended runtime
   under paced load.
4. **Release/rights review missing.** Reopen only after provider intake,
   license/notice review, descriptor and public catalog review. Until then the
   provider stays OFF, unlinked, unregistered and outside the installed SDK.
5. **Benchmark validation/submission missing.** This is not an `audio_bench`
   bundle and was not validated under the current submission policy; no hosted
   submission or publication claim is made.

Until those gates pass, installed v0 behaviour remains frozen and this
directory remains optional task-local reference evidence.
