<!--
SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
-->

# SDK-LIBFUZZER-ABI-STREAM-SEQUENCE-INSTRUMENTATION — tool evidence

Task-local, proposal-only, synthetic evidence. No SDK API/ABI, installed v0
behavior, public surface, build file, CI configuration, provider registry,
descriptor setting, board entry, handoff or other task's evidence is changed.
The package models the documented SDK v0 endpoint semantics in pure Python;
it does **not** link, compile or exercise a native SDK build. Its status is
`proposal_only_synthetic_incomplete` / `not_qualified`, and
`no_missing_result_qualifies_candidate` is `true`.

## What is here

| File | Purpose |
| --- | --- |
| `fixture.py` | Seeded byte generator, caller-owned value objects, explicit reject/accept oracle, two endpoint models, scenario replay, gate definitions, canonical report builder. |
| `run.py` | Developer entry point: canonical report regeneration, manifest inspection, CLI scenario replay from generated or caller-supplied bytes. |
| `adapter.json` | Machine-readable manifest: entry point, operations, scenarios, seed, generator, endpoints, registration state and libFuzzer invocation notes. |
| `test_fixture.py` | 35 deterministic `unittest` cases over pins, generator, boundary, inline and buffered replay, report shape, CLI and licensing. |
| `verify.py` | Single-shot gate verifier printing `pins_ok`, `json_ok`, `licensing_ok`, `scope_ok`, `reproduction_ok`. |
| `report.json` | Canonical, strict-JSON, byte-reproducible result report. |
| `report.json.sha256` | SHA-256 pin of `report.json`. |
| `SOURCES.sha256` | SHA-256 pins for read-only sources, pinned toolchain runtime and all task-local files (except `SOURCES.sha256` itself, which cannot pin its own digest). |
| `README.md` | This file. |

There are no generated binaries, no vendored runtime, no corpus artifact and
no network, device, clock or audio input. Python writes bytecode nowhere
(`PYTHONDONTWRITEBYTECODE=1`).

## Installed tool version, provenance and clean checkout

- SDK worktree branch: `swarm/SDK-LIBFUZZER-ABI-STREAM-SEQUENCE-INSTRUMENTATION`.
- Base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0` (ancestor of HEAD;
  the only writes are under `docs/task-evidence/libfuzzer-abi-stream-sequence/`).
- Pinned interpreter:
  `/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`; standard library
  only, no third-party imports.
- Host: local macOS 27.2 arm64. No target-device claim is made.
- Apple toolchain: `/usr/bin/clang++` is Apple clang 21.0.0
  (`clang-2100.4.1.1`). A standalone `-fsanitize=fuzzer,address` link probe
  fails because
  `/Applications/Xcode.app/.../lib/clang/21/lib/darwin/libclang_rt.fuzzer_osx.a`
  is absent.
- Homebrew toolchain: `/opt/homebrew/opt/llvm/bin/clang++` is Homebrew clang
  23.1.4. The same standalone probe compiled and ran 8 inputs with
  `-seed=20261124 -verbosity=0 -print_final_stats=1` (exit 0, 34 MB peak RSS).
- Pinned runtime:
  `/opt/homebrew/Cellar/llvm/23.1.4/lib/clang/23/lib/darwin/libclang_rt.fuzzer_osx.a`,
  SHA-256 `99fbbcbef1df8ce4612c003ec16d1303b53d90ee794186f1d83f1d053427191a`.
  The probe source is `probe.cpp` under the temporary probe directory recorded
  in `fixture.py`; no probe binary is committed.

Read-only input pins are recorded in `SOURCES.sha256` and asserted by both
`test_fixture.py` and `verify.py`. They include the task profile, the v0
contract and public headers, and the frozen libFuzzer corpus sources
`stream_sequences.cpp`, `direct_request_fuzzer.cpp` and `abi_config_fuzzer.cpp`
plus `implementation_record.md`. These sources inform scenario *shape* only;
no code from them is compiled here and their source-reported campaign numbers
are never rerun, pooled or presented as this task's measurements.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_fixture.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json   # byte-identical rewrite
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --report      # identical bytes to stdout
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --inspect
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py            # five explicit checks
shasum -a 256 report.json
```

Typical developer use through the documented developer-facing entry point:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --scenario stream_sequence --seed 20261124
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --scenario malformed_output --seed 20261124
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --scenario stream_sequence --bytes 8101414101022242
```

The last form supplies caller-owned raw bytes (hex) instead of the seeded
generator. Every buffer in the model is allocated and copied by the caller;
aliasing is explicit and rejected. No provider, descriptor, registry entry or
default is created; the conceptual tool ID in the report is evidence-only.

## Scenarios and oracle

- **Stream sequence** (read-only provenance: `stream_sequences.cpp`): four
  deterministic seed corpora plus three generated 128-operation cohorts drive
  two independent buffered sessions over the documented v0 endpoints
  (`as_session_submit_v0`, `as_session_pull_v0`, `as_session_begin_drain_v0`,
  `as_session_reset_v0`, `as_session_get_stats_v0`, `as_session_close_v0`)
  plus caller-local frame allocation/release. Operations encode stream slot,
  opcode, wrong-generation and malformed-input bits. The oracle rejects stale
  epochs, wrong input positions, malformed headers, nonfinite samples, queue
  overflow with `AS_RESOURCE_EXHAUSTED`, cross-lifecycle misuse and unknown
  provider selection with `AS_UNSUPPORTED`; it accepts FIFO submit/pull in
  three-frame order. Invariants: queue depth ≤ 3, FIFO order per session,
  exactly-once delivery, terminal EOS after drain, empty queue after drain,
  uncoupled sessions, and no state/counter advance on rejection (apart from a
  diagnostic rejection counter).
- **Malformed output** (read-only provenance: `direct_request_fuzzer.cpp` and
  `abi_config_fuzzer.cpp`): 27 explicit cases plus five named cases and three
  generated 160-case cohorts drive `as_session_process_v0`. Counts include
  `0, 1, 159, 160, 161, 320`; capacities include `0, 159, 160, 161, 320`;
  pointer layouts include independent, exact alias, partial overlap and
  adjacent nonoverlap. Header size/version/reserved mutations, partial final
  frames, padding, nonfinite input, lifecycle and backend inconsistency are
  covered. The independent oracle checks status, rule ID, write class
  (none / zero-prefix / full-160), input immutability, tail immutability and
  state immutability on rejection. Backend failures enter `needs_reset` and
  recover only with a strictly greater epoch.

Rules R01–R15 are listed verbatim in `fixture.py` and embedded in
`report.json.fixture.spec.rules`. The inline model implements the documented
validate-then-zero order; an invalid output structure receives no speculative
write.

## libFuzzer invocation description

The SDK checkout has no libFuzzer target, and this task cannot add build or CI
files. Therefore **the SDK libFuzzer gate is blocked**; the deterministic
replay above is the authoritative evidence in this package.

The exact standalone invocation used for toolchain provenance is:

```sh
/opt/homebrew/opt/llvm/bin/clang++ -fsanitize=fuzzer,address -o <probe>/probe.bin.bin <probe>/probe.cpp
<probe>/probe.bin.bin -runs=8 -seed=20261124 -verbosity=0 -print_final_stats=1
```

The frozen source corpus reports (not rerun here) used:

```sh
realtime-audio-library/build/preset-macos-fuzz/ae_stream_sequence_fuzzer <corpus-dir> -runs=10000 -max_len=128 -seed=20261029 -verbosity=0 -print_final_stats=1
```

A future, separately authorized SDK target should use the same finite campaign
shape with a checked-in seed corpus, ASan/UBSan/coverage instrumentation and
pinned compiler/runtime digests:

```sh
<sdk-fuzz-build>/as_stream_sequence_fuzzer <corpus-dir> -runs=10000 -max_len=128 -seed=20261124 -timeout=2 -verbosity=0 -print_final_stats=1
```

## Honesty / non-claims

- No public API/ABI change, default change, provider registration or installed
  v0 behavior change. Geometry remains 16 kHz, mono, f32, 160 samples/call.
- No build file, CI file, board file, handoff, other worktree branch or other
  task's evidence is touched.
- No native SDK harness was compiled or linked; no coverage, robustness,
  security or quality qualification follows from these finite deterministic
  replays.
- No paced, loaded, deadline, CPU, memory or device measurement is claimed.
  `measured_workload_support` is blocked and no timing number enters the
  report.
- Homebrew libFuzzer availability is proven only by a standalone probe, not by
  any SDK-linked fuzz target.
- Missing results do not qualify the candidate; all report gates except the
  explicitly blocked ones pass only as synthetic evidence controls.
