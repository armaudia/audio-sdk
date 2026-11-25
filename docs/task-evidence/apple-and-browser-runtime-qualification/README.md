# Apple and browser runtime qualification probe

`SDK-APPLE-AND-BROWSER-RUNTIME-QUALIFICATION` · `audio-sdk/apple-and-browser-runtime-probe/0.1`

This developer tool compiles the same C11 consumer against extracted SDK
headers and static archives on macOS and for Emscripten + Node. The linked
[CI workflow](../../../.github/workflows/ci.yml) uses a separate packaged
example for its Node smoke. Neither Node run is browser evidence.

| Evidence lane | What this tool can establish | What it cannot establish |
| --- | --- | --- |
| Installed Apple native | C11 static link and unpaced execution on the exact macOS host and architecture recorded | Another architecture/OS, iOS or simulator execution, Audio Unit/Core Audio I/O or scheduling |
| Installed Emscripten + Node | C11 static link with Emscripten pthread flags and execution under Node; no SDK worker in this fixture | Web loading, AudioWorklet execution, browser threading or render deadlines |
| Browser / AudioWorklet | Blocked in this probe; no browser artifact or render host | Even browser main-thread Wasm loading or an offline render is not evidence of real-time worklet deadlines |
| Device scheduling | Blocked in this probe; no device I/O, clocks or paced run | Callback safety, jitter, availability, end-to-end latency or deadline compliance |

## Reproduce from a clean SDK checkout

Use trusted local tools and extracts. Record `git rev-parse HEAD` and the
archive SHA-256 values alongside the private report. The report records the
exact extracted location, SDK build information (including version, target and
runtime input digest), hashes of the consumed headers/archive member and probe
sources, compiler/runtime commands and outputs, host, and output hashes. The
hashes identify local inputs; this tool does not verify release attestations.

From the repository root, with Python **3.12.16**, CMake, and Apple clang
available for the native lane:

```sh
set -eu
umask 077
out=$(mktemp -d "${TMPDIR:-/tmp}/audio-sdk-runtime.XXXXXX")
task=docs/task-evidence/apple-and-browser-runtime-qualification
python3.12 -m venv "$out/venv"
export PATH="$out/venv/bin:$PATH"
python --version
python -m pip install --require-hashes -r requirements-build.txt
python -m unittest discover -s "$task" -p 'test_*.py' -v
git rev-parse HEAD
python scripts/ci.py --output "$out/native-ci"
native="$out/native-ci/extracted/audio-sdk-0.1.0"
shasum -a 256 "$out/native-ci/candidate/audio-sdk-0.1.0.tar.gz"
```

For the optional Node lane, use a local Emscripten installation and Node.
The commands below follow the CI package path; set `emscripten_root` to the
active Emscripten root (Homebrew: `em-config EMSCRIPTEN_ROOT`; activated
emsdk: `$EMSDK/upstream/emscripten`). Hosted CI pins Emscripten **5.0.1**;
a local run with another version is a separate observation. No models, audio
files or external runtime assets are needed.

```sh
cmake -S . -B "$out/wasm-build" \
  -DCMAKE_TOOLCHAIN_FILE="$emscripten_root/cmake/Modules/Platform/Emscripten.cmake" \
  -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib \
  -DAS_BUILD_SHARED=OFF -DAS_BUILD_TESTS=OFF -DAS_BUILD_CONFORMANCE=OFF \
  -DAS_BUILD_EXAMPLES=OFF -DCMAKE_C_FLAGS=-pthread -DCMAKE_CXX_FLAGS=-pthread
cmake --build "$out/wasm-build" --parallel 2
sh scripts/package.sh "$out/wasm-build" "$out/wasm-candidate" --wasm
zip="$out/wasm-candidate/audio-sdk-0.1.0-wasm32-emscripten.zip"
shasum -a 256 "$zip"
python -m zipfile -e "$zip" "$out/wasm-extracted"
wasm="$out/wasm-extracted"
```

```sh
python "$task/probe.py" --native-prefix "$native" --wasm-prefix "$wasm" \
  --output "$out/probe"
```

Omit either prefix flag to record that lane as unavailable without failing
the invocation. An explicitly selected lane that cannot compile or run
exits nonzero and preserves its stage and diagnostic in `report.json`.
Malformed CLI arguments and existing output directories are rejected (exit 2).

Both smoke lanes use caller-owned buffers and one generated float32 impulse
at 16 kHz, mono, 160 samples, in unpaced mode 2. Mode 2 invokes on the
caller's thread, not an SDK worker. Expected results: both built-ins consume
160 samples; high-pass delivers `[0,160)` immediately in source coordinates
and Speex reports 160 samples of startup buffering then delivers `[0,160)`
on drain. Both end at EOS. The controls expect `AS_INVALID_ARGUMENT` for
malformed or omitted provider IDs and `AS_UNSUPPORTED` for a syntactically
valid unregistered optional ID or unavailable inline callback mode, all
without returning a session. This is ABI and synthetic sample-mapping
evidence, not an audio-quality or elapsed-time test.

## Remaining release gates

- **Apple targets:** build and install for each claimed OS/architecture and
  run on that target. A cross-compile, SDK listing or simulator run does not
  substitute for physical-device execution or I/O timing.
- **Browser / AudioWorklet:** build a browser-targeted SDK host and serve in a
  secure context. Record browser/OS/version and isolation state (COOP/COEP
  and SharedArrayBuffer when using shared memory). Verify actual processor
  startup, negotiated rate/render quantum and their adaptation to 16 kHz /
  160 samples. Check continuity, availability, misses and backpressure under
  a declared paced load. Browser presence and Node smoke do not pass this gate.
- **Device scheduling:** require an approved target and I/O route, known
  negotiated format and buffer sizes, calibrated clock mapping and a
  preregistered workload/deadline/resource budget. Record misses, dropped or
  concealed output, availability and callback safety under load. Do not infer
  physical timing from content buffer offsets.
- **Release:** independent review, hosted `quality` on the exact candidate,
  platform-specific evidence and the documented [release policy](../../../RELEASING.md).
  No model, corpus, real audio, public workload result or support claim is
  produced by this probe.
