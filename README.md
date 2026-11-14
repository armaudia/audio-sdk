# audio-sdk

Source-linked C11 audio processing SDK, contract 0.1. The implemented scope is
mono float32 at 16 kHz in 160-sample (10 ms) application frames. It includes
SpeexDSP noise suppression, an 80 Hz high-pass filter, independent sessions,
synchronous processing and a bounded C worker interface.

## Build and test

```sh
cmake -S . -B build/all -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/all --parallel 2
ctest --test-dir build/all --output-on-failure --timeout 60
```

For complete installed-package and Python 3.12 checks:

```sh
python3.12 -m venv build/check-env
build/check-env/bin/python -m pip install --require-hashes -r requirements-build.txt
build/check-env/bin/python scripts/ci.py --output build/ci
```

The complete check requires a new output directory. It builds both library forms,
checks installed C/C++ and external providers, installs the Python wheel into a
fresh environment, tests it outside the checkout, and verifies normalized archive
repeatability. Native packages are written to `build/ci/dist/`.

## Use

C/C++ consumers use the installed `AudioSDK::audio_sdk` CMake target or pkg-config.
See [provider integration](docs/provider-v0.md), the [public contract](CONTRACTS.md)
and [WAV/provider-switching examples](examples/README.md).

The Python binding supports synchronous mode 2 and requires an absolute
`AUDIO_SDK_LIBRARY` path. Its `Registry`/`Session` interface exposes process,
reset, drain and close. Use C submit/pull for buffered-worker mode 3.
Provider switching creates independent sessions; settings are fixed per provider.
There is no implicit resampling, microphone capture or neural model.

## Support and release scope

Current checked local evidence is macOS arm64. Linux x86-64 and hosted CI must
pass before those targets are advertised as supported. Read [release policy](RELEASING.md)
and [historical handoff](HANDOFF.md). Passing synthetic conformance does not
establish production workload latency, speech quality or hardware suitability.

Callback-safe mode 1, a stable binary plugin ABI, legacy `ae_*_v1` compatibility,
LiveKit, separate engine plugins and additional formats are outside this release.

## License

First-party code is MIT; vendored SpeexDSP/FFT code retains its BSD notices.
See [LICENSE](LICENSE) and [NOTICE](licenses/NOTICE).
