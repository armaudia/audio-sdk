# audio-sdk

Source-linked C11 audio processing SDK, contract 0.1. The implemented scope is
mono float32 at 16 kHz in 160-sample (10 ms) application frames. Each session
runs one provider for one stream.

## Shipped components

| Component | Implemented behavior |
| --- | --- |
| [`speex.ns.v0`](schemas/providers/speex.ns.v0.descriptor.json) | SpeexDSP noise suppression with a fixed −20 dB setting and 160 samples of buffering. Converts to PCM16 inside the provider. See the [SpeexDSP NS reference](docs/task-evidence/speexdsp-ns-reference/README.md). |
| [`dsp.highpass80.v0`](schemas/providers/dsp.highpass80.v0.descriptor.json) | Second-order 80 Hz high-pass filter with zero buffering delay. See the [high-pass reference](docs/task-evidence/sdk-high-pass-80-hz/README.md). |
| [C provider API](api/include/audio_sdk/provider_v0.h) | Built-in discovery, explicit registration of source-linked providers and validation of caller-supplied assets using ID, byte count and SHA-256. |
| [C session API](api/include/audio_sdk/session_v0.h) | Synchronous processing (mode 2) and buffered submit/pull (mode 3) for both built-in providers. Each mode 3 session has one worker, bounded input and output queues and explicit backpressure. Sessions expose source intervals, valid sample ranges, reset epochs, drain, close, timing and stats. |
| [Python binding](bindings/python) | Mode 2 through `Registry` and `Session`, with process, reset, drain and close. Requires an absolute `AUDIO_SDK_LIBRARY` path. Installed-wheel checks use Python 3.12. |
| [Native packages](RELEASING.md) | Headers-only `AudioSDK::api`, compiled core via `AudioSDK::core` or `AudioSDK::audio_sdk`, optional `AudioSDK::audio_sdk_shared`, and the `audio-sdk` pkg-config module. |
| [Conformance](conformance) | The installed `audio_sdk_conformance` CLI checks both built-in providers. Standalone fixtures verify [external provider integration](conformance/external_provider/README.md) and [provider registration with a caller-supplied asset](conformance/provider_registration/README.md). |

See the [public contract](CONTRACTS.md) and the [provider integration guide](docs/provider-v0.md)
for input format, lifecycle and timing requirements. The host handles audio I/O,
sample-rate conversion, and any sequencing across providers.

## Pipeline examples and recipes

| Example or recipe | Implementation |
| --- | --- |
| [C provider switching](examples/README.md#c-provider-switching) | `as_example_c` processes the same synthetic impulse in independent Speex and high-pass sessions and prints output validity ranges. |
| [Python WAV switching](examples/README.md#python-wav-switching) | Processes the same mono 16 kHz PCM16 WAV in independent provider sessions, with explicit sample conversion and a fixed input sample rate. |
| [Capture recipe](docs/task-evidence/pipe-capture/README.md) | Synthetic host fixture with a high-pass, noise suppression and peak limiter chain. Includes identity and single-stage controls, an advisory tap, bypass, timeout and drain. |
| [Duplex recipe](docs/task-evidence/pipe-duplex/README.md) | Synthetic host fixture with timestamped render alignment, a pinned SpeexDSP MDF reference CLI, noise suppression and peak-limiter policy stages, and an optional residual-suppression surrogate. |
| [Control recipe](docs/task-evidence/pipe-control/README.md) | Synthetic identity loopback with explicit drain and session switching. A separate probe installs a fixture wheel and loads its providers and recipes. |

The two switching examples use the public session API. The three recipe
directories contain opt-in reference hosts and synthetic fixtures under
`docs/task-evidence/`.

## Build and test

```sh
cmake -S . -B build/all -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/all --parallel 2
ctest --test-dir build/all --output-on-failure --timeout 60
```

Run the complete installed-package and Python 3.12 checks from a new output
directory.

```sh
python3.12 -m venv build/check-env
build/check-env/bin/python -m pip install --require-hashes -r requirements-build.txt
build/check-env/bin/python scripts/ci.py --output build/ci
```

The complete check builds both library forms, checks installed C/C++ consumers
and external providers, tests the Python wheel in a fresh environment outside
the checkout, and verifies normalized archive repeatability. Native packages
are written to `build/ci/dist/`.

Build only the public headers with the standalone API project or with
`-DAS_BUILD_CORE=OFF` at the repository root.

```sh
cmake -S api -B build/api-only
cmake --build build/api-only
ctest --test-dir build/api-only --output-on-failure
cmake --install build/api-only --prefix /path/to/api-prefix
```

Top-level build options include `AS_BUILD_SHARED`, `AS_BUILD_TESTS`,
`AS_BUILD_CONFORMANCE`, `AS_BUILD_EXAMPLES`, `AS_ENABLE_SANITIZERS`,
`AS_ENABLE_TSAN` and `AS_WARNINGS_AS_ERRORS`.

## Support and release scope

The [CI workflow](.github/workflows/ci.yml) checks native packages on Linux,
macOS and Windows, a static wasm32/Emscripten build with Node.js, and sanitizers
and licensing on Linux. The [release policy](RELEASING.md) defines the evidence
required for platform support, production latency, speech quality and hardware
suitability. Published artifacts are on the [releases page](https://github.com/armaudia/audio-sdk/releases).

## Reference implementations and evidence

The repository also tracks experimental algorithms, proposal fixtures and
evaluation tooling. These entries live under `docs/task-evidence/` and each
link records its scope and reproduction steps. The standard SDK packages ship
the runtime components listed above. See the [evidence handoff](docs/evidence-handoff.md)
for how fixture results are recorded.

- **Noise suppression and voice activity** · [Spectral subtraction](docs/task-evidence/classical-spectral-subtraction/README.md), [Wiener denoising](docs/task-evidence/classical-wiener-denoising/README.md), [Speex NS advisory probability](docs/task-evidence/speex-ns-advisory-probability/README.md), [Speex AGC and activity](docs/task-evidence/speex-agc-and-activity-output/README.md), [SpeexDSP VAD](docs/task-evidence/speexdsp-vad/README.md), [fixed RMS VAD](docs/task-evidence/fixed-rms-vad/README.md), [adaptive energy VAD](docs/task-evidence/adaptive-energy-vad/README.md), [energy-to-Silero cascade](docs/task-evidence/adaptive-energy-to-silero-cascade/README.md), [RNNoise speech probability](docs/task-evidence/rnnoise-speech-probability/README.md), [WebRTC VAD](docs/task-evidence/webrtc-vad/README.md).
- **Echo cancellation and dereverberation** · [SpeexDSP MDF](docs/task-evidence/speexdsp-mdf-reference/README.md), [MDF residual postfilter](docs/task-evidence/speex-mdf-residual-postfilter/README.md), [NLMS AEC](docs/task-evidence/nlms-aec/README.md), [RLS AEC](docs/task-evidence/rls-aec/README.md), [RLS-to-NLMS AEC](docs/task-evidence/fixed-rls-to-nlms-aec/README.md), [offline mono WPE](docs/task-evidence/offline-mono-wpe/README.md), [online mono WPE](docs/task-evidence/online-mono-wpe-reference/README.md), [offline multichannel WPE](docs/task-evidence/offline-multichannel-wpe/README.md), [online multichannel WPE](docs/task-evidence/online-multichannel-wpe/README.md).
- **Acoustic feedback suppression** · [Narrow biquad notch](docs/task-evidence/narrow-biquad-notch/README.md), [adaptive feedback notch](docs/task-evidence/adaptive-feedback-notch/README.md), [adaptive notch with gain margin](docs/task-evidence/adaptive-notch-with-gain-margin/README.md), [block NLMS AFC](docs/task-evidence/block-nlms-afc/README.md), [block NLMS AFC with gain margin](docs/task-evidence/block-nlms-afc-with-margin/README.md), [fixed gain margin](docs/task-evidence/fixed-feedback-gain-margin/README.md), [logistic gain controller](docs/task-evidence/logistic-feedback-gain-controller/README.md).
- **Dynamics, EQ and loudness** · [Peak limiter](docs/task-evidence/peak-limiter-reference/README.md), [envelope AGC](docs/task-evidence/envelope-agc/README.md), [feed-forward compressor](docs/task-evidence/feed-forward-compressor/README.md), [de-esser](docs/task-evidence/de-esser/README.md), [six-band spectral tilt](docs/task-evidence/fixed-six-band-spectral-tilt/README.md), [full-band receive DRC](docs/task-evidence/full-band-receive-drc/README.md), [target gain with peak ceiling](docs/task-evidence/static-target-gain-with-peak-ceiling/README.md), [ridge static gain](docs/task-evidence/ridge-static-gain/README.md), [learned inverse EQ](docs/task-evidence/learned-inverse-eq/README.md), [EBU R128 and FFmpeg loudnorm](docs/task-evidence/ebu-r128-ffmpeg-loudnorm/README.md).
- **Restoration and packet loss concealment** · [Median-residual click gate](docs/task-evidence/median-residual-click-gate/README.md), [linear-interpolation declipping](docs/task-evidence/linear-interpolation-declipping/README.md), [band-limited POCS declipping](docs/task-evidence/band-limited-pocs-declipping/README.md), [zero fill](docs/task-evidence/zero-fill-plc/README.md), [pitch-period repeat](docs/task-evidence/pitch-period-repeat-plc/README.md), [linear interpolation](docs/task-evidence/linear-interpolation-plc/README.md), [autoregressive PLC](docs/task-evidence/autoregressive-plc/README.md), [Opus 1.4 decoder PLC](docs/task-evidence/opus-1-4-standard-decoder-plc/README.md).
- **Time-scale modification** · [Whole-clip duration planner](docs/task-evidence/d1-whole-clip-duration-planner/README.md), [granular TSM](docs/task-evidence/granular-tsm/README.md), [OLA/SOLA](docs/task-evidence/ola-sola/README.md), [PSOLA/Praat](docs/task-evidence/psola-praat/README.md), [Signalsmith Stretch](docs/task-evidence/signalsmith-stretch/README.md).
- **PCM and resampling controls** · [Identity PCM and no-op fixtures](docs/task-evidence/identity-pcm-and-noop-fixtures/README.md), [typed frames, resampling and drift diagnostics](docs/task-evidence/typed-frame-resample-and-drift-diagnostics/README.md), [NumPy/SciPy/SoundFile WAV resampling](docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md).
- **Follow-on contracts** · [Ordered processing chains](docs/task-evidence/ordered-chain-graph/README.md), [duplex clocks](docs/task-evidence/duplex-clocks/README.md), [analysis events](docs/task-evidence/analysis-events/README.md), [elastic PCM packets](docs/task-evidence/elastic-pcm-packets/README.md), [neural runtime boundary](docs/task-evidence/neural-runtime-boundary/README.md), [engine v1](docs/task-evidence/engine-v1/README.md).
- **Evaluation** · [Blind listening and MUSHRA-style design](docs/task-evidence/ab-blind-listening-and-mushra-style-design/README.md), [ERLE and double-talk preservation](docs/task-evidence/erle-and-double-talk-preservation/README.md), [impairment taxonomy](docs/task-evidence/quality-impairment-taxonomy/README.md), [SI-SDR, SDR and SNR](docs/task-evidence/si-sdr-sdr-and-snr/README.md), [SRMR and reverberation metrics](docs/task-evidence/srmr-and-reverb-metrics/README.md), [STOI and ESTOI](docs/task-evidence/stoi-estoi/README.md).
- **Integration and qualification tooling** · [Benchmark subprocess protocol](docs/task-evidence/bench-subprocess-protocol/README.md), [C/Rust bindings](docs/task-evidence/c-raii-rust-c-bindings/README.md), [Clang sanitizer matrix](docs/task-evidence/clang-sanitizers-qualification-matrix/README.md), [libFuzzer stream-sequence target](docs/task-evidence/libfuzzer-abi-stream-sequence/README.md), [nightly release evidence installer fixture](docs/task-evidence/nightly-release-evidence-installer/README.md).

## License

The standalone API and integration materials are Apache-2.0. The core runtime
and core tests are MPL-2.0. Third-party notices are preserved. See
[the file-level map](LICENSE.md), [NOTICE](notices/NOTICE) and [contributor policy](CONTRIBUTING.md).

Distributed native packages include corresponding covered source and licenses.
External SDK code contributions require verified private acceptance of the published
individual CLA benefiting Tsakanyan Hovhannes personally. See the [CLA](CLA/README.md).
