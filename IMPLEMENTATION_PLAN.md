# audio-sdk implementation plan

Owner: SDK maintainer; assign a person in S01. Read [shared dependencies](../plan/implementation_handoff_20261113.md) and [CONTRACTS.md](CONTRACTS.md) first. Required v0.1 tasks are S01–S08. S09 is required only for a LiveKit-supported claim. Later capability tasks S10–S12 require their own release and budget.

## Target tree

```text
include/audio_enhance/             retained application C/C++ headers
include/audio_sdk/                 provider_v0.h, session_v0.h
src/api/                          legacy adapter, v0 facade
src/core/                         config, registry, interval accounting
src/execution/                    reference sequential engine, bounded bridge
providers/speex/                  cleared Speex wrapper
providers/highpass/               first-party filter wrapper
conformance/                      standalone C executable + fixtures + schema tests
schemas/                          descriptor, effective configuration
bindings/python/                  ctypes package, tests, locks
integrations/livekit/              optional package and lock
examples/{wav,switch_provider,livekit}/
cmake/                            install/export configuration
third_party/speexdsp/              exact inventoried source and notices
licenses/                         first/third-party license texts
scripts/                          consumer and release verification
.github/workflows/                build, conformance, package candidate
```

Do not create empty implementation subtrees merely to imitate this diagram. Create files in the task that implements them. Existing documentation is the only current content.

## S01 — Source freeze and public allocation (12–20 hours)

Dependencies: none; coordinate B01/P01. Outputs: `docs/migration/source-allocation.csv`, `asset-rights.csv`, `source-snapshot.json`, `release-license-decision.json`, `deps/lock.json`.

1. Inventory `../../cpp-library/include`, `src/api`, `src/core`, `src/execution`, `src/stages`, tests, CMake, tools and `third_party`; paths here are migration inputs relative to this directory. Record relative path, SHA-256, upstream revision if available, ownership evidence, destination, decision, notices and reviewer. The parent workspace is not a Git repository; use a content manifest when no commit exists. Never invent a source SHA.
2. Assign reference lifecycle/timing/facade/configuration to SDK; optimized FastEnhancer/Silero kernels/weights and adaptive/batching policies to pro only when rights permit; evaluation scripts/data to bench. Exclude customer/private research histories entirely.
3. Trace both checked-in and generated assets: CMake embeds Medium `fe.q8`, generated Tiny16/Tiny48/Small48 weights and native VAD assets. Inspect generator inputs, object/archive contents and install manifests. `cmake/audio_enhance_models.json` currently says not redistributed; correct package-specific metadata after inspection rather than reusing this blanket claim.
4. Use first-party Apache-2.0 as the release proposal, pending the founder's recorded rights/license decision. Preserve third-party terms. Unknown provenance/rights is excluded from the initial package. Do not overwrite existing LICENSE in the source workspace or infer company ownership of upstream code.
5. Copy only the reviewed public allowlist into this directory. Keep original source hashes and patch references; remove build directories, `.deps`, weights, private include paths and network acquisition side effects.
6. Name maintainers/reviewer, capture exact toolchain/OS versions, and inspect all package outputs for excluded paths/assets. Commit inventory only after review.

Exit: SDK source export has no unclassified file; DSP-only build has zero model assets. Unknown optional rights cannot block work on reviewed first-party/Speex files. Test rows S-T01/S-T12.

## S02 — Characterize and repair content timing (16–28 hours)

Dependencies: local source freeze; export only after S01. Outputs: `conformance/timing_content.c`, deterministic fixture definitions, `docs/timing-regression.md`, corrected source path.

1. Before refactoring, build a minimal baseline with the inspected CMake flags below. Save configure/build/CTest logs and emitted feature/recipe manifests.
2. Exercise the actual application C API with identity, test-only 160-sample delay and broadband signed marker bursts. Generate fixture samples from a fixed integer PRNG seed `20261113`; store recipe and expected positions. Test multiple stream origins, timestamps, resets and final partial frames.
3. Reproduce the historical basic/Speex delay discrepancy in an isolated chain. Inspect `src/core/session.cpp` delay accumulation/output timestamps, `src/core/registry.cpp` descriptors, `src/stages/speex_ns.cpp` framing and model hop adapters. Compare declared buffering to an independently known transfer path. Use normalized correlation only on predefined nonscored fixtures with a bounded lag range, unique peak and tolerance of one sample; never fit scored utterance alignment. A fixture unable to locate a unique mapping fails/blocks that mapping.
4. Save a regression that fails with the original code. Fix the responsible buffering/descriptor/timestamp path once; do not add a benchmark-only compensating lag. Verify composition: sequential buffering delays add; analysis delay does not alter audio position.
5. Preserve old ABI fields and document changed semantics/release notes. Perceptual phase response of a filter is not an extra integer buffering delay.

Exit: reproducible failing-before/passing-after fixture on actual boundary; source interval maps agree. Model-specific mappings remain excluded until their separate tests pass. S-T02/S-T03.

Existing baseline commands (run from the original `cpp-library` before extraction; after extraction from this repository only once equivalent build files exist):

```sh
cmake -S . -B build/characterize -DCMAKE_BUILD_TYPE=Release -DAE_BUILD_TESTS=ON -DAE_BUILD_BENCHMARKS=OFF -DAE_ENABLE_ONNXRUNTIME=OFF -DAE_COMPONENT_FASTENHANCER=OFF -DAE_COMPONENT_SILERO_VAD=OFF
cmake --build build/characterize --parallel 2
ctest --test-dir build/characterize --output-on-failure
```

These flags exist in the inspected source. Success is not asserted here. Additional trimmed-build test registration is part of S06; do not remove failing tests just to make extraction pass.

## S03 — Freeze and implement public provider/header schemas (24–40 hours)

Dependencies: S01, S02. Outputs: headers, schemas, registry, initializer/query/error tests, `docs/provider-v0.md`.

1. Translate every structure and operation in CONTRACTS.md into C declarations with layout assertions. Add complete field/lifetime comments and exact reserved-byte rules. Keep the existing `ae_*_v1` definitions unchanged.
2. Implement registry create/copy/register/query/close with no mutable globals. Freeze mutation after the first session. Copy descriptors/tables, pin code lifetime, reject duplicate IDs and unsupported contract versions.
3. Implement strict settings validation and fully resolved effective configuration, including clipping behavior, queue counts and execution policy. Control-layer canonicalization must pass shared restricted JCS vectors; reject duplicate keys, unsafe numbers, invalid decimal strings, unknown fields and invalid UTF-8.
4. Create positive/negative schema fixtures. Avoid recursive package hashes: embedded descriptor identifies source/build/configuration; external package manifest identifies the archive digest.
5. Build a standalone provider in a separate fixture project using only installed public headers. Implement a deterministic delayed identity provider with create/process/reset/drain/destroy and faults selected before preparation. It must register without editing SDK factory source or including `src/` headers.
6. Senior review checks all signatures, counts, ownership, status codes, ABI layout and failure transitions before S04/P02/B04 bind to them. Publish a contract fixture digest in the SDK release manifest.

Exit: C11 and C++20 consumers compile, malformed/incompatible registrations fail precisely, independent fixture runs. S-T04/S-T05.

## S04 — Implement sequential facade and bounded delivery (24–40 hours)

Dependencies: S03. Outputs: v0 session facade, reference engine, drain/reset/queue implementation and tests.

1. Implement mode 2 synchronous processing first. Validate pointers/counts/epoch/state before backend invocation; zero result validity on failure. Validate returned finite samples and count/position invariants. Never silently clip float input in the facade.
2. Implement the full lifecycle in CONTRACTS.md, including input-final marker, empty stream, partial final input, bounded drain and cancellation inventory. Do not route drain to an unbounded loop of fake accepted frames.
3. Implement mode 1 admission only after callback-safety checks pass. All state, descriptors, scratch and configuration parsing must be prepared outside process.
4. Implement mode 3 with one worker, exactly three-frame input/output queues and no shared worker pool/batching. Reserve output capacity before consuming input; record rejection/missing output explicitly. Wrap legacy worker paths only if they meet these exact bounds; otherwise retain them exclusively for the old ABI and use the new simple bridge for v0.
5. Add atomic guards/references and control-thread join; close/reset never race with a provider's process. Block new admission before waiting. Reset removes all old-epoch work and records cancelled content.
6. Add session info/stats caller-buffer queries and a JSON control manifest; processing only updates bounded counters. Use uint64 overflow checks. Never format JSON or perform asset/config I/O on a callback.
7. Connect the old API through a deliberate compatibility layer; new extensions are additive. Old modes/presets keep their names and documented restrictions, not a false v0 conformance badge.

Exit: interval conservation and queue/race tests pass, injected failures need reset, consumer can cleanly drain/close. S-T03/S-T06/S-T07.

## S05 — Implement two production example providers (12–24 hours)

Dependencies: S04, cleared source from S01. Outputs: Speex and high-pass adapters, descriptors and parameter docs.

1. Port Speex preprocessing behind the public table. Preserve float-to-PCM16 policy (`lrint(clamp(x,-1,1)*32767)` with FE_TONEAREST verified on the processing thread; convert back by dividing by 32768), suppression default −20 dB, AGC off and dereverb off. Freeze all Speex VAD/settings defaults even when analysis is not exported. Record internal PCM16 quantization in configuration; do not call the path float-exact.
2. Eliminate the existing wrapper's quiet-frame skipping in v0: adaptation is off and every accepted frame executes the same declared processing path. A later adaptive implementation gets another configuration/provider revision.
3. Port the first-party high-pass with cutoff `80` Hz and Q `0.7071067811865476`, double-precision filter state and float32 output. Start with fixed settings; reject overrides in this provider ID. D=0 buffering; no clipping/limiter or VAD is implicitly added.
4. Implement drain using each provider's known buffering recipe and bounded calls. Test Speex reset reinitialization errors; reset is control work, not callback work.
5. Verify isolated providers separately from `basic.v1` (Speex/VAD/limiter). Preserve explicit IDs and attribution; no ranking calls high-pass an equivalent noise suppressor.

Exit: both providers pass independent conformance; switching closes/recreates and explains differences. S-T08.

## S06 — Standalone conformance and installation (16–28 hours)

Dependencies: S03–S05. Outputs: conformance executable `audio_sdk_conformance`, installed fixtures, consumer scripts and test registration.

1. Migrate relevant tests from `cpp-library/tests`: ABI layout, edge behavior, buffered contracts, callback instrumentation, package smoke. Gate model/AEC/playback tests on the components actually built. Preserve supported legacy checks; mark unsupported tests explicitly rather than treating zero discovered tests as success.
2. Package conformance with no bench/pro/Python quality dependency. CLI to implement: `audio_sdk_conformance --provider <id> --report <json-path>`; exit 0 only when all required checks pass, 1 conformance failure, 2 invalid invocation/environment. The report lists every expected test/status and version/digest.
3. Export installed CMake target `AudioSDK::audio_sdk`, include dirs, shared/static libraries and pkg-config metadata. Retain `AudioEnhance` compatibility exports only where their original names/semantics still hold. No build-tree absolute paths or private headers in installed usage requirements.
4. Create/install a release build, then configure the fixture/consumer from another working directory against only the install prefix. Verify shared loader paths and static transitive Speex/system dependencies. Run with sibling directories unavailable.
5. Run sanitizer/race builds separately; collect callback allocation/lock instrumentation on a supported toolchain. If instrumentation is unavailable, do not promote an untested new provider to callback-safe; processing-thread mode remains usable.

Exit: S-T01–S-T09 and S-T13 required rows pass; S-T14 passes for each advertised callback-safe path, installed external provider succeeds without private source.

## S07 — Reproducible native packaging and CI (12–20 hours)

Dependencies: S06. Outputs: platform build presets, trusted candidate manifests, CI, release/rollback docs.

1. Minimal PR matrix: Linux x86-64 GCC and macOS arm64 Clang release builds, one Linux ASan/UBSan build and separate Linux TSan queue tests. Resolve compiler exact versions into the toolchain lock. Disable model and advanced components in the public default.
2. Pin every third-party action to a reviewed full commit. PRs run read-only with no private secrets. No submitted code runs on a persistent personal machine. Use the disposable policy in B08 for dedicated hardware.
3. Candidate archive contains include/lib/CMake/pkg-config/conformance/descriptors/schemas/notices/manifest. Build ID records compiler flags, source allocation digest and dependencies. Linux baseline disables native ISA auto-selection; inspect `readelf`/`ldd`, macOS `otool -L` for unexpected dependencies. Record commands and outputs.
4. Build twice in clean directories. Compare artifacts; if nondeterministic paths/timestamps occur, remove them or document the exact differences and use immutable per-build digests. Never claim bit reproducibility without equality.
5. Produce SHA-256 package manifest and size inventory outside the archive's own embedded identity. Use candidate IDs until review; do not advertise workload qualification merely because CI passed.
6. Provide upgrade/rollback by explicit package/version path and recreation of sessions; no live process binary replacement.

Exit: S-T09/S-T12 pass on each claimed target. Bench consumes the exact archive digest.

## S08 — C/Python examples and provider switching (12–20 hours)

Dependencies: S07. Outputs: ctypes binding, WAV/switching examples, install/contribution guide, Python locks.

1. Implement a small CPython 3.12 `ctypes` wrapper for the installed v0 facade; declare argtypes/restype and struct widths exactly. Native provider functions remain native; do not implement real-time DSP with a Python callback table.
2. Use explicit library path from user config, validate SDK contract/build identity on load, fail if mismatched; do not search the current directory for arbitrary libraries. Sessions implement context-manager close and explicit drain/reset. Pin Python owner's references while ctypes calls release the GIL; worker is native.
3. Expose contiguous mono float32 buffers; copy/convert before processing only when requested and recorded. No automatic rate/shape conversion. WAV example declares PCM decode/encode policy and preserves raw float output.
4. Switching example processes the same fixture with A, drains/closes, then B in a fresh epoch. Print IDs/config/delay/output hashes and expected task differences. No hot swap or neural prerequisite.
5. Give external contributors a provider template, fixed local synthetic input, conformance command and installation troubleshooting. Measure a fresh engineer's build/registration steps and document actual assistance.

Exit: S-T10 and installed examples run in clean CPython without bench/pro/network access.

## S09 — Optional LiveKit host path (16–28 hours)

Dependencies: S08 and a frozen host package pair. Outputs: optional `audio-sdk-livekit` package, exact hashed host lock, host buffering report.

1. Inspect the pinned RTC `FrameProcessor[AudioFrame]` API and Agents `AudioInputOptions.noise_cancellation`. Record signatures/source revision and run a local no-network API spike before writing the adapter. Upstream references are in the review report. If no compatible released pair passes, mark this capability blocked; never monkey-patch undocumented internals.
2. Configure input at 16 kHz/mono with exactly 10 ms (160-sample) RTC frames. Reject other frame lengths/rates/channels in this first host release; there is no hidden resampler/rechunker. Disable other noise cancellation/AGC and record upstream processing. The inspected RTC FrameProcessor has synchronous `_process(frame)` and `_close()` methods, so do not implement it as an async-returning processor.
3. `_process` converts signed PCM16 to float32 (sample/32768), submits to native buffered mode, and returns immediately without waiting for inference. Use a fixed three-frame (30 ms) host delivery shift: first three invocations return explicitly recorded invalid startup zeros; on invocation four and later, pull the oldest completed provider output before submitting current input. If the expected output is NOT_READY after startup or input admission fails, stop with an integration/deadline diagnostic; never silently drop/replace content. Provider D adds to the fixed host shift. Input/output frames remain 160 samples; validity/source position are retained in sidecar diagnostics. This host buffering can exceed the initial latency objective and must be measured rather than hidden.
4. Output conversion is clamp(round-to-nearest-ties-even(x*32768),-32768,32767), with clipping count. Copy into host-owned memory. Native SPSC queues remain capacity three; no Python work-item queue is added. One processor instance belongs to one participant/track. `enabled=false` means explicit bypass with the same fixed host delay and a new configuration/epoch; do not silently change timing. Reset on track discontinuity; no state shared between participants.
5. Implement the pinned `enabled`, `_process` and `_close` protocol plus managed wrapper `aclose()`. `_close()` only closes admission and schedules control-thread teardown; `aclose()` awaits that teardown off the event-loop thread, joins the native worker and records abandoned tail intervals. A synchronous FrameProcessor has no public flush callback in the inspected contract: clean offline drain is available through the managed wrapper before track stop, while abrupt RTC close is cancellation, never clean full-content delivery. Tests assert this distinction.
6. Offline tests invoke the same processor with fake RTC frames at a real/simulated 10 ms schedule so the worker can run; injecting frames in an unpaced burst is an overload test. One optional local room test uses synthetic lawful audio and developer-supplied credentials outside public CI. Trace host/native positions and availability, including 30 ms shift and startup/cancelled tail. No cloud test means offline host evidence only. Neural host support remains absent until its actual delay/deadline path passes.

Exit: S-T11 passes with exact lock. Live cloud test unavailable means offline host evidence only and no deployed-room claim.

## S10–S12 — Controlled follow-on releases

These are separately estimated work packages, not hidden v0.1 requirements. Implement in this order; each change creates a new capability/descriptor version.

| Task | Dependencies / work | Tests and exit |
|---|---|---|
| S10 neural reference (24–48h) | Reviewed model rights; exact weights/hash; optional ONNX lock; model-specific input/output tensor names, dtypes, shapes, recurrent states, hop/history, normalization and finite padding recipe derived from inspected model. Export these in `docs/providers/<id>/model-contract.json`; never generic-loader streaming claims. Start at 16 kHz only; adaptation off; processing-thread mode | Tensor impulse/step/seeded-noise and full recording parity against upstream; state isolation/reset; D verification; drain bound; no required asset available means creation fails, not DSP fallback. No B/P neural comparison before contract artifact passes |
| S11 execution-domain engine contract (40–72h) | Implement the exact ownership, graph bounds, signatures, leases, timed analysis and optional policy/batch hooks in the follow-on engine section of CONTRACTS.md; publish the additive `engine_v1.h` RFC and then implementation: engine domain create/admit/remove stream/enqueue/pull/quiesce/reset/close; one owner for queue/workers, facade leases outputs, domain holds session refs, bounded stream admission and cancellation barriers. No private fields. Fixed-rate scalar process remains universal fallback. Batch capability declares model/precision/shape/state compatibility and max batch | Independent external engine fixture using installed headers; public provider/external engine and external provider/public engine; full overload/reset/close matrix; unsupported graph rejects. Freeze layout/semantics only after compiled fixture. P07 cannot start before this artifact exists |
| S12 format/host/binding breadth (separately scoped research/design; excluded from this implementation release) | Separate changes for native 48 kHz, stereo, render-reference AEC, variable-rate playback, Rust/C#, Pipecat. Each starts with a concrete capability RFC specifying formats, ownership, content map and missing-input/error behavior; use existing cleared code only after allocation. Variable rate uses piecewise input→output mapping and count-changing API; never overload fixed scalar D | Extend standalone conformance first, then host bindings and B12 task cohorts. Format conversion has pinned resampler/delay. AEC uses aligned render fixtures; variable rate tests monotonic mapping/drain/count conservation and never enters equal-length NS rankings. No capability is advertised on the strength of the roadmap |

A junior implements a frozen capability contract, not an invented future ABI. S11/S12 are design-and-implementation work with required reviewed artifacts; the initial handoff does not falsely provide a stable engine ABI for a product whose capability requirements are not yet validated.
