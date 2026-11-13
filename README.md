# audio-sdk

Local implementation candidate for the source-linked C11 audio-sdk v0.1
contract. It provides a fixed mono float32 / 16 kHz / 160-sample runtime, a
SpeexDSP provider (`D=160`), a first-party high-pass provider (`D=0`),
standalone provider conformance, CMake/pkg-config installation, and a thin
stdlib-only Python ctypes binding.

Start with [`HANDOFF.md`](HANDOFF.md) for task status, hashes, installed paths,
conformance evidence, and blockers. The normative source contract is
[`CONTRACTS.md`](CONTRACTS.md); task acceptance criteria are in
[`TEST_PLAN.md`](TEST_PLAN.md).

Build and test locally:

```sh
cmake -S . -B build/all -DCMAKE_BUILD_TYPE=Release
cmake --build build/all --parallel 2
ctest --test-dir build/all --output-on-failure
```

This is not a stable binary plugin ABI and does not implement the legacy
`ae_*_v1` adapter, LiveKit integration, neural engines, or additional formats.
The current candidate has only local macOS arm64 evidence; do not treat it as a
published or cross-platform qualified release.
