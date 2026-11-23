# SDK-SPEEXDSP-NS-REFERENCE · installed Speex NS control

**Status: reference-verification only.** This package retains the shipped
`speex.ns.v0` baseline and verifies the exact installed Release runtime as a
control for follow-on work. No public header, ABI, descriptor, registry,
default provider, suppression policy, sample rate, activity output or installed
v0 behavior was changed. No real corpus, model, rights-qualified audio,
listening test or release claim is included.

The Enhancement profile is applied with synthetic, model-free stimuli:
identity/noisy control plus the established task-matched installed conformance
baseline; paired SI-SDR and STOI against synthetic clean references; clean
preservation, peaks, invalid/missing/nonfinite controls; alignment, state,
memory and measured content/availability timing. Historical source-reported
numbers are retained but never pooled with local scores.

## Scope and source pins

Pinned base: `3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41`.
Board check (read-only) passed for `SDK-SPEEXDSP-NS-REFERENCE`.

| Source (relative to `/Users/htsakanyan/workspace/audio/audioml`) | SHA-256 | Summary used |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | SpeexDSP NS is an evaluated CLN row, separate from SpeexDSP VAD and MDF; compared with WebRTC NS/RNNoise/noisy identity. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | No-weight classical baseline; pin build and attenuation; 30-pair DNS pilot is exploratory, not a representative holdout. |
| `audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c` | `d1a98e3aff897375db4f0fc7668329be5254faa361ccaba1635a5089ea8a71e6` | Fixed 16 kHz mono/160 samples; denoise on, AGC/dereverb off, VAD computed but not exported, −20 dB suppression, 160-sample declared buffering, PCM16 quantization. |
| `adapters/speexdsp/adapter.json` | `8daaf37bb19ae75bb705e31e98964cbf732e666b140823dfa1bd4f5f3496ad3c` | Offline CLN-01 waveform adapter identity at source commit `7a158783`; weights not required; distinct from the SDK provider. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | `SpeexDSP-NS-only`: Xiph `7a158783`, BSD-3-Clause, pinned header and native library digests. |
| `research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Source-reported pilot: median SNR gain +0.560 dB, STOI .9375, RTF .0006, 20 ms measured delay; STOI regression made it unsuitable as default on that subset. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Source-reported DNS pilot mean ΔSI-SDR +1.06 dB, ΔSTOI −0.0057, RTF about .0006; experimental C++ backend exists. |

Also pinned by the build, not edited here: build ID
`audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`,
descriptor digest `8dcfbd3ca87ae85f0c1d6390ede34b62b5a44461bef65d52c7bf0cf5c303b733`,
SpeexDSP revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`.

## Artifacts and exact digests

| Path | SHA-256 | Note |
| --- | --- | --- |
| `fixture.py` | `df71a8e047499690f0cbb2f8338f8938a1498845223221f2ab8bc0eded8295bf` | Deterministic stimuli, installed-runtime probe, canonical report builder |
| `test_fixture.py` | `64845b7a1b1a5c2c2c9d13b047b314295f6f9a8835c0e4bd61761e27426807d2` | 11 unittest checks |
| `conformance-report.json` | `accbe82e7460ec79a66f29b8b7b791a3d1cf7da56cf5d432a0f60de00c30f529` | Exact installed conformance report, 40 pass / 0 fail / 0 skip |
| `report.json` | `f76732e46c10d45d072557635e422be911128b9355d0763eaa9b6fa52ff661ec` | Canonical deterministic evidence; two consecutive generations were byte-identical |
| `runtime-measurements.json` | `77fe5e6e576c985d053a2625315345d96b89696c902ed0af18fe2ddd2e55a54a` | Locally observed digest only; timings/RSS are deliberately non-deterministic |

`conformance-report.json` and `report.json` are pinned. The timing report
digest is informational and must not be used as a reproducibility gate.

## Reproduction

All build/install output lives outside the worktree. `SOURCE_ROOT` is only
needed by the source-pin test.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEEXDSP-NS-REFERENCE
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/speex-ns-ref
TASK=$WT/docs/task-evidence/speexdsp-ns-reference
mkdir -p "$SCRATCH"

cmake -S "$WT" -B "$SCRATCH/build" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$SCRATCH/install"
cmake --build "$SCRATCH/build" --parallel 4
ctest --test-dir "$SCRATCH/build" --output-on-failure
cmake --install "$SCRATCH/build"
"$SCRATCH/install/bin/audio_sdk_conformance" --provider speex.ns.v0 \
  --report "$SCRATCH/conformance.json"
cp "$SCRATCH/conformance.json" "$TASK/conformance-report.json"

export AUDIO_SDK_LIBRARY="$SCRATCH/install/lib/libaudio_sdk.dylib"
export AUDIO_SDK_EXPECTED_BUILD_ID=$(python3 -c "import json;print(json.load(open('$SCRATCH/build/build-info.json'))['build_id'])")
export PYTHONPATH="$WT/bindings/python:$TASK"
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
PYTHONDONTWRITEBYTECODE=1 $PY fixture.py conformance-report.json report.json runtime-measurements.json
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_fixture.py

python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SPEEXDSP-NS-REFERENCE
```

Local results: Release CTest **11/11 passed**; installed conformance
**40/40 passed**; fixture **11/11 tests passed**; board check exit 0.
`python3 -m json.tool` accepted both JSON reports; `git diff --check` was clean.

## Fixture design

- Deterministic LCG noise, band-limited voiced surrogate, noise-only, silence
  and an isolated impulse; 32,000 samples (2 s, 200 frames) per scored stream.
  No corpus, weights, model or file I/O beyond the reports.
- Shipped stdlib ctypes binding (`bindings/python`) loads the **installed**
  `libaudio_sdk.dylib`; the build ID is checked at import. One provider, one
  synchronous session per stream, fixed 16 kHz mono/160-sample frames.
- Identity/noisy control uses the unprocessed mixture as baseline. Paired
  SI-SDR is zero-mean v1 arithmetic; STOI is pystoi 0.4.1 non-extended
  (`numpy 2.5.4`, Python 3.12.16, Darwin arm64). Values are rounded to six
  decimals only in the report; no caps, lag search or sample pooling.
- Alignment uses the impulse's measured output index, not the declared delay.
  Content mapping is `[0,32000)` source → `[160,32000)` raw, first output
  source sample −160 (160-sample buffering), measured content lag 0 samples.
- State controls: separate instances are uncoupled and bit-identical for the
  same input, reset is bit-identical and propagates epoch 2, different stimuli
  differ. NaN input is rejected as `invalid_argument` with no state change.

## Results (synthetic installed runtime only)

Paired deltas are provider minus identity/noisy control. Positive SI-SDR delta
is better; STOI delta can be negative and is reported as an adverse result.

| Condition | SI-SDR identity → provider (Δ) | STOI identity → provider (Δ) | RMS gain | Peak | Invalid/clipped |
| --- | --- | --- | --- | --- | --- |
| `noisy_snr10` | 9.998819 → 14.045325 (+4.046506) | 0.536170 → 0.548902 (+0.012732) | 0.933556 | 0.977295 | 0 |
| `noisy_snr0` | −0.003825 → 4.921662 (+4.925487) | 0.510899 → 0.498268 (−0.012631) | 0.748204 | 0.991364 | 0 |
| `noise_only` | −67.030754 → −59.998479 (+7.032275) | 0.290647 → 0.222462 (−0.068185) | 0.487130 | 0.594727 | 0 |
| `clean_only` | undefined (`exact_reconstruction`) → 21.210407 | 1.000000 → 0.963888 (−0.036112) | 0.971046 | 0.824738 | 0 |
| `silence` | undefined (`zero_projection`) → undefined | 0.0 → 0.0 (0.0) | undefined | 0.0 | 0 |

Every valid output was finite, with no peak at or above 1.0. Clean-only STOI
fell by 0.036112 and both noisy/clean preservation cases show speech damage
despite SI-SDR gains; that is the expected suppression tradeoff for this
synthetic surrogate and is not a quality pass.

Invalid/missing/nonfinite controls all passed: missing library path fails
closed, wrong build ID fails identity check, NaN frame is rejected and leaves
state unchanged, missing reference and truncated output are null/invalid with
explicit reasons, and 10 conformance `create.reject.*` checks pass. No missing
result was treated as a score.

Measured, unpaced single-stream timing on this host (200 process frames per
condition): median per process call 0.0309–0.0314 ms, maximum 0.0453–0.6820 ms
(one outlier in `noisy_snr10`); first-valid-output availability 0.000077–
0.000101 s; total 2-second stream wall time 0.0065–0.0072 s; drain wall
0.000023–0.000030 s. Coarse `ru_maxrss` delta ranged 0–1,397,760 bytes across
conditions. These are observations of this exact installed runtime, not a
deadline budget, RTF qualification, availability SLA or memory attribution.

## Boundary and reopen conditions

This closes only the installed v0 reference/control question. It does not
qualify real-corpus quality, rights, listening, suppression policy, target
device, hosted CI, paced load, buffer/backpressure behavior or any release
decision. The DNS pilot and EARS figures in the pinned research remain
source-reported and are not rerun here.

Reopen with a declared, rights-qualified matched cohort and clean references;
agreed metric/preservation margins and content/availability budgets; a frozen
scorer and build for that cohort; paced installed-runtime measurement under
load and on the target host; and independent sealed review. A changed sample
rate, suppression setting, activity/VAD export or provider policy is a new
task and must not inherit this control.
