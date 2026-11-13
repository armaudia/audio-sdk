# audio-sdk test and acceptance plan

Tests below are to be created/migrated; their names are acceptance IDs, not tests already run. Use synthetic deterministic fixtures in public CI. A required failure blocks the capability/package. Model/host tests are optional only when their capability is absent from the package and documentation.

## Test matrix

| ID / scope | Setup and procedure | Exact expected outcome |
|---|---|---|
| S-T01 baseline/build | Configure release with neural off; run original applicable CTest suite; compile installed header as C11 and C++20; count discovered tests | No compile warnings/errors; nonzero expected tests run; unsupported component tests explicitly absent; no private/bench include or link dependency |
| S-T02 timing regression | Identity and 160-sample delay, impulses and seeded broadband markers, start samples 0/123456, two epochs; isolated Speex fixture; high-pass known transfer response | Identity maps to current source; delay fixture maps n−160; actual wrapper metadata matches independently checked D within one sample; no per-scored-file lag fitting; save original failing trace |
| S-T03 boundaries/drain | Lengths 0,1,159,160,161,165,319,320,321 and every final remainder 1–159; D=0,1,159,160,161,512; repeat drain; invalid output capacity; malicious infinite drain | Exact accepted source interval union delivered once; startup/final padding invalid; EOS bounded by descriptor; no fake accepted flush input; bad drain fails; repeat EOS empty |
| S-T04 registry/layout | Wrong size/major/minor/reserved bytes, duplicate ID, oversized descriptor, invalid UTF-8/ID, unknown schema field, null/short query buffer, register after session creation | Precise defined error; required_size returned; no partial query data; no mutable borrowed descriptor/table memory; no crash/leak |
| S-T05 invalid processing | Null/overlap/misaligned buffers, wrong count/rate/epoch/position, NaN/Inf input, bad final padding, insufficient capacity; snapshot state then retry correct frame | Backend not invoked; no consumed/valid samples or state advancement; retry equals fresh baseline. Misbehaving backend output count/NaN produces backend failure and NEEDS_RESET |
| S-T06 lifecycle/failure | Process before successful create, process after final/drain, reset with old epoch, backend failure on a selected frame, failing reset, close twice via null handle, registry close with live session | Invalid transitions rejected; backend failure blocks future process until successful reset; failed reset stays failed; null close harmless; registry returns BUSY until sessions released |
| S-T07 bounded concurrency | Fill input to three frames with stalled worker; fill output with paused consumer; concurrent process/reset/close guards; 1,000 interleaved reset/close cycles under TSan | Fourth unaccepted frame explicitly rejected; no silent drop/overwrite; queue occupancy <=3 each; output room reserved before input consume; no race/use-after-free/deadlock; cancellation inventory correct |
| S-T08 provider state | Two instances on different seeded streams vs independent baselines; reset reused instance vs new instance; Speex all-frame execution; high-pass expected coefficients/step response | Bit-identical on same deterministic build; no cross-stream recurrent state; no hidden silence shortcut; high-pass D=0; Speex clipping/quantization declared |
| S-T09 external install | Install prefix; standalone external provider and C/C++ consumer compiled in fresh directory; run with source/siblings unavailable; static and shared | Only installed public headers/libraries required; correct loader/transitive dependencies; no weights/pro symbols/private paths; conformance report inventories all checks |
| S-T10 Python | ctypes size/offset checks against native probe; close/context exceptions; missing/wrong library; one float32 frame; full WAV; two-provider example; threaded processing guard | Exact layouts/statuses, bounded ownership, no double-free; unsupported shape/rate fails; output hashes agree with C route; no hidden conversion |
| S-T11 LiveKit optional | Pinned RTC frames at 10 ms pacing, wrong lengths including 161/320/800 samples, participant reset, cancellation with pending work, expected output unavailable, queue full and malformed format | Preserve source order and explicit 30 ms host shift plus D; first three frames invalid startup; reject wrong lengths; finite conversion; no event-loop wait for inference; stop on missed output/admission; no old-epoch output; abrupt close records cancelled tail; managed drain/close tested |
| S-T12 package/export | Inspect archive and installed tree, symbol/dependency list; minimal offline load; repeated clean builds; incompatible CPU/contract | No excluded kernels/weights, complete notices; precise unsupported error before unsupported instructions execute; package digest identifies actual bytes; no qualified label from build alone |
| S-T13 exact integers | C emits clocks 9007199254740993 and near int64 limit; Python serialize/parse; effective config JCS subset vectors | Exact round-trip, no float conversion; reject overflow and −0; fixture shared with bench; deterministic hash |
| S-T14 callback safety | Instrument prepare and steady-state separately; allocation/free/lock/file/network/log hooks around all reachable process/submit/pull calls; stress zero/quiet/nonzero input | Zero forbidden operations in callback-safe paths after preparation; initialization excluded and reported; uninstrumented new path remains worker-only; instrumented builds never used for capacity claims |

## Execution commands to implement and retain

S06 registers the native suite with CTest and produces the conformance executable. Once those targets exist:

```sh
cmake -S . -B build/release -DCMAKE_BUILD_TYPE=Release -DAE_BUILD_TESTS=ON -DAE_COMPONENT_FASTENHANCER=OFF -DAE_COMPONENT_SILERO_VAD=OFF -DAE_ENABLE_ONNXRUNTIME=OFF
cmake --build build/release --parallel 2
ctest --test-dir build/release --output-on-failure
cmake --install build/release --prefix "$PWD/build/install"
build/install/bin/audio_sdk_conformance --provider speex.ns.v0 --report build/speex-conformance.json
build/install/bin/audio_sdk_conformance --provider dsp.highpass80.v0 --report build/highpass-conformance.json
```

Run ASan/UBSan using `-DAE_ENABLE_SANITIZERS=ON`; run TSan in a separate build using `-DAE_ENABLE_TSAN=ON`. Run release callback instrumentation separately because sanitizer allocators invalidate the existing macOS interposition technique. S07 adds platform presets with exact compiler/deployment target; these snippets do not claim such presets already exist. S08 registers Python tests and documents `python -m pytest bindings/python/tests`; S09 adds its optional separate lock/test directory.

## Release evidence

Retain source/toolchain/dependency locks, package digest, installed inventory, test count/statuses, conformance revision, callback-safety scope and sanitizer results. Run on both targets before claiming both. A release candidate with one missing required test remains a candidate. S09 cloud access and neural/model rights may be blocked while the DSP SDK ships, but the absent capabilities must be plainly absent from release metadata. Quality/capacity/qualification are bench outputs, not SDK build checks.
