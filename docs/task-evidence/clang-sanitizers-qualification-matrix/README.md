# Clang sanitizers, fuzzing and qualification matrix — task-local Tool evidence

- Task: `SDK-CLANG-SANITIZERS-FUZZING-AND-QUALIFICATION-MATRIX`
- Profile: **Tool**
- Status: `proposal_only_synthetic_incomplete`
- Qualification status: **`not_qualified`**
- Base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`
- Tool version: `0.1.0`
- Install location: `docs/task-evidence/clang-sanitizers-qualification-matrix/`

This directory is deterministic, task-local tooling. It maps the **exact**
overflow, state, malformed-input, missing-selection and installed-consumer
scenarios already present in the pinned SDK sources into a reproducible
qualification matrix. It does **not** qualify a row, build an instrumented SDK,
run a fuzz engine against SDK code, or rerun the installed consumer. No build
file, CI file, public API/ABI, default, descriptor setting, registry entry,
installed v0 behavior, board entry or handoff was changed.

The pinned qualification ledger
`cpp-library/qualification/README.md` says a row is `qualified` only with
evidence produced on that exact platform/runtime, and explicitly forbids
promotion from a different platform, a different runtime, a compile-only result
or a synthetic unit test. This package obeys that boundary: every SDK-target
matrix row is `not-run` or `unavailable`, and `qualified_rows=[]`.

## Scope and fixed boundary

The installed v0 boundary remains exactly:

| Field | Value |
| --- | --- |
| Contract | `audio-sdk/v0` |
| Sample rate | 16000 Hz |
| Channels | 1 (mono) |
| Sample format | `f32` |
| Frame | 160 samples/call |
| ABI major/minor | 0 / 1 |
| Statuses used | `OK=0`, `INVALID_ARGUMENT=1`, `UNSUPPORTED=2`, `NEEDS_RESET=5`, `END_OF_STREAM=7`, `CLOSED=9` |
| Frame/result flags | `FRAME_FINAL_INPUT=1`, `RESULT_STARTUP_PADDING=1`, `RESULT_FINAL_PADDING=2` |

No provider is compiled, registered, packaged or enabled. Every conceptual
selection in this evidence is recorded with `registered=false`,
`enabled_by_default=false` and `descriptor_settings={}`.

## Tool profile coverage

| Profile element | How this package satisfies it |
| --- | --- |
| Version | `0.1.0`, pinned in `adapter.json` and `report.json` |
| Install location | This task-local evidence directory only |
| Provenance | Repository, branch, base commit, interpreter, compiler version and target triple in `report.json` |
| Clean checkout / extracted package | Pinned base commit and pinned sibling-task archive/build ID; no package rebuilt or rerun here |
| One typical CLI/API use | One epoch-1, first-sample-0 process call: consumed=160, produced=160, valid=160, `source_first_sample=0`, then stable `END_OF_STREAM` drain |
| Caller-owned inputs | Deterministic LCG frames and copied k/128 generator; the Python model copies values and retains no caller pointer |
| Malformed inputs | Eight exact probes from the installed C consumer, all rejected with `INVALID_ARGUMENT` and zero valid samples |
| Missing optional selections | Six explicit unsupported/invalid outcomes; no inferred fallback |
| Separate evidence layers | Compile/build, synthetic runtime and measured workload support are separate report objects |

## Exact scenarios reused

All scenario sources are read-only pins. Their bytes are verified by
`SOURCES.sha256` and again inside `verify.py`.

| Group | Count | Source | What is mapped |
| --- | ---: | --- | --- |
| Exact validity cases | 6 | `core/tests/test_validity.c` | Empty provider range, empty stream, `UINT32_MAX` provider overflow, `INT64_MAX`/`INT64_MIN` saturation and underflow |
| Delay boundaries | 7 | `core/tests/test_validity.c` | Delays `0,1,159,160,161,256,512` |
| Final remainders | 1113 | `core/tests/test_validity.c` | Every remainder `1..159` at every delay |
| Conformance lengths | 166 | `conformance/checks.c` | `0`, `1..159`, `160`, `161`, `165`, `319`, `320`, `321` from a 168-slot array |
| Coordinate cases | 4 | `conformance/checks.c`, `bindings/python/tests/test_sdk.py` | `2**53+1` timing and length coordinates; `2**64` epoch and `2**63` first rejection |
| State scenarios | 6 | `conformance/checks.c`, `CONTRACTS.md`, `core/tests/test_session.c` | Strict reset epoch, reset at `123456`, stable drain, typical process, `NEEDS_RESET`, closed handle |
| Malformed probes | 8 | `docs/task-evidence/identity-pcm-and-noop-fixtures/main.c` | Partial-without-final, nonfinite, stale epoch, wrong position, null input, short capacity, short header, after-final |
| Missing selections | 6 | installed-consumer source | Unregistered query/config/create, unadvertised modes 1 and 3, unrequested asset |
| Deterministic corpus | 256 cases, 16 mutators | this package | Seed `20261124`; every case rejected by the reference model; **not** a fuzz-engine run |
| Installed consumer | 3 frames, 357 samples | installed-consumer fixture | `(160,160,37)`, first sample `9007199254740993`, k/128 generator, bit-exact f32 content |

The installed-consumer canonical payload is 4074 bytes with SHA-256
`4e5255802e2be73b84599979855d59d03a4f06eff8e439d23ab7ee09e95be459`; the f32
sample bytes have SHA-256
`9c6165076289d999de0a523ecacc83a840f74edf1dcb9c2a59f1c34756355ff2`. The
pinned qualification README digest is
`f2ab2c4bd874c0147dcfbc98638564dcce1202a4468b557b81a3ed8df6a44871`.

## Optional Clang probe — non-qualifying

A standalone C11 saturating-add probe was compiled and run outside the
worktree. It mirrors `core/src/core/validity.c:8-11` but does **not** include an
SDK header, SDK source, installed library or conformance target. It is recorded
only as toolchain provenance.

| Probe | Result |
| --- | --- |
| `/usr/bin/clang` — Apple clang 21.0.0, target `arm64-apple-darwin27.2.0` | available |
| `-fsanitize=undefined` | compile and run OK; observed `9223372036854775807` |
| `-fsanitize=address` | compile and run OK; observed `9223372036854775807` |
| `-fsanitize=address,undefined` | compile and run OK; observed `9223372036854775807` |
| `-fsanitize=memory` | blocked: unsupported option for target |
| `-fsanitize=fuzzer,address` | blocked: `libclang_rt.fuzzer_osx.a` absent |
| `afl-fuzz` / `honggfuzz` | absent |

Absence of these tools is recorded verbatim. No substitute engine is inferred
and no sanitizer finding is claimed.

## Evidence layers

1. **Compile/build evidence:** `not_run` for the SDK. No instrumented target,
   no build-file or CI change. The standalone probe is not SDK compile evidence.
2. **Synthetic runtime evidence:** the Python reference model passes all exact
   validity, sweep, state, malformed, missing-selection, corpus and installed
   consumer payload checks. Python uses arbitrary-precision integers, so it
   cannot detect a native integer wrap; those overflow facts remain pinned
   source/contract evidence, not measured sanitizer findings.
3. **Measured workload support:** `blocked`. No pacing, deadline, CPU, memory,
   device or load measurement was collected.

## Matrix summary

The matrix has 12 rows across sanitizer, fuzz engine, target, build and
platform axes. Status counts: `not-run=8`, `unavailable=4`, `qualified=0`,
`experimental=0`. Blocked rows are:

- `M-05`, `M-06`: libFuzzer runtime absent.
- `M-07`: `afl-fuzz` absent.
- `M-08`: `honggfuzz` absent.
- `M-09`: MSan unsupported on the probed target.

The remaining rows are `not-run` because no instrumented SDK build or installed
sanitized consumer run exists. See `report.json` for the full row evidence and
notes, and `adapter.json` for the frozen row definitions.

## Gates and adverse observations

Seven gates are `blocked`: instrumented SDK build, SDK-target sanitizer run,
fuzz runtime and target, MSan, installed sanitized consumer, measured workload
support and provider intake. Each has a `reopen` condition in `report.json`.

Five adverse observations are preserved: MSan unsupported, libFuzzer runtime
absent, AFL++/honggfuzz absent, two pinned installed-conformance skips
(`registry.busy`, `buffered.flow`) that are never counted as passes, and the
Python arbitrary-precision model limitation. There is no paired quality or
timing control, so `regressions=[]`.

## Reproduce

Use the pinned interpreter from the worktree root:

```sh
cd docs/task-evidence/clang-sanitizers-qualification-matrix
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_fixture
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

Expected: 28 tests pass; `run.py` prints `qualification_status=not_qualified`,
`controls_all_pass=True`, `qualified_rows=0`; `verify.py` prints
`pins_ok=... json_ok=... licensing_ok=... scope_ok=1 reproduction_ok=1` and
`changed_files` limited to this directory.

Canonical report SHA-256: `f30abce9371e053f962ff1619fad29bc3a97305a69e1e1651da5a2c6b1c3add6`.

## Licensing

New files use `SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes` and
`SPDX&#45;License-Identifier: Apache-2.0`, already covered by `REUSE.toml` `docs/**`.
Read-only pinned sources keep their own SPDX headers and are never modified.
