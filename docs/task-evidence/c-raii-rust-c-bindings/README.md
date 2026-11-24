<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-C-RAII-RUST-AND-C-BINDINGS — task-local synthetic C/Rust binding evidence

**Status:** `proposal_only_not_qualified` / `incomplete`.
**Decision:** `DEFER`. No production exposure, no processor registration, no
default enablement, no public API/ABI change, no installed-behavior change.

This package is developer-only `tool` evidence for the ownership/lifetime
contract at the C boundary of a potential future Rust/C# binding. It is **not**
a Rust build, a processor, a provider, a benchmark result, a quality claim, a
target-device measurement or a release artifact.

## What is recorded

- A frozen, deterministic synthetic fixture: 16 kHz mono float32, 160 samples,
  seed `20261124`, 11 contract cases (valid, malformed, missing optional,
  invalid and non-finite controls). No recording, model, network resource,
  device or licensed runtime is used.
- A documented binding model in `adapter.json` (C shared contract, documented
  C++ RAII owner, documented Rust `Drop` owner, documented C# `SafeHandle`
  owner). Only the C contract is exercised; the managed/Rust parts are models.
- A task-local C11 harness in `c_boundary/` exercising the published v0 ABI:
  registry create → effective-config create → session create → process →
  session close (twice) → registry close (twice). All PCM and control storage
  is caller-owned stack memory. Close is asserted null-safe on double close.
- An exact parity crosscheck (`crosscheck.json`) between the Python contract
  model and the C harness output. No tolerance, threshold, ranking or
  qualification is involved.
- Separate compile/build evidence, synthetic runtime evidence and explicitly
  unclaimed workload support (see `report.json` sections `build_evidence`,
  `synthetic_runtime_evidence`, `unclaimed_workload_support`).

## What is explicitly deferred

`rustc` and `cargo` were not found in `PATH` at verification time. No Rust
crate registry download, `cargo check`, `cargo build`, Rust example run, .NET
build or target-device timing was performed. The native Rust build is recorded
as `DEFER`; ownership/lifetime is covered by the documented model plus the
task-local C harness. See `report.json` → `tool.rust` and
`remaining_gates`.

## Source pins

| Pinned source | SHA-256 |
| --- | --- |
| `cpp-library/bindings/README.md` | `239459d0b9a5027387f4bec55401c111c34882175789e4337d63d3fc4a2ab063` |
| `audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Base commit (post-rebase): `503791ef555ee0385312923df38dce6c14628904`.
This branch was originally based on `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`;
when `origin/main` advanced, the branch was rebased and all evidence was
regenerated and re-verified against the new base.
The pins are re-verified by `verify.py` and recorded in `SOURCES.sha256` with
`PIN` lines.

## Tools (version, location, provenance)

| Tool | Version / provenance |
| --- | --- |
| Python | 3.11.5, pyenv shim at `/Users/htsakanyan/.pyenv/versions/3.11.5` |
| CMake | 3.27.4, `/Users/htsakanyan/.pyenv/shims/cmake` |
| C/C++ compiler | Apple clang 21.0.0 (clang-2100.4.1.1), arm64-apple-darwin27.2.0 |
| REUSE | 6.3.0, installed from PyPI into a scratch venv outside the worktree via `python3 -m venv <scratch>/craii-reuse-venv && <scratch>/craii-reuse-venv/bin/python -m pip install reuse==6.3.0 charset-normalizer` |
| `gh` | 2.104.0 (PR submission only) |
| Rust | `rustc` / `cargo` not found in `PATH` → `DEFER` |

Network use for evidence generation: none. Pinned files are read from the
provided checkout.

## Layout

- `contract.json` — task contract, decision, accepted evidence and remaining gates.
- `adapter.json` — binding model and opt-in C boundary declaration.
- `provider.json` — explicit statement that no provider/descriptor/default was added.
- `fixture.py` — deterministic frame and case table.
- `reference.py` — frozen contract model, canonical JSON helpers, generated header.
- `scorer.py` — exact-match scorer.
- `run.py` — regeneration entry points and the one-item `inspect`/`run`/`validate` API.
- `c_boundary/` — opt-in C11 harness, default-OFF guard and generated header.
- `harness_output.json` (under `c_boundary/`) — recorded synthetic C runtime output.
- `crosscheck.json` + `.sha256` — parity result.
- `report.json` + `.sha256` — canonical developer report.
- `SOURCES.sha256` — digests of every package file plus the three source pins.
- `test_reference.py`, `verify.py`, `check_licensing.py` — checks.

Recorded digests: `crosscheck.json` =
`41734a83381276f5ca9d675988ade034805068eb63546c81892662b20eb139a9`,
`report.json` =
`9d6bd6553ac619c4fb5418101055daedf1fa343f09b7148e9dff04d13f472ce5`.

## Reproduce

Run from this directory with `PYTHONDONTWRITEBYTECODE=1`.

```bash
# 1. SDK build/install + ctest (11/11 native) and separate API-only check
cmake -S <worktree> -B <scratch>/all -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <scratch>/all --parallel 2
ctest --test-dir <scratch>/all --output-on-failure --timeout 60   # 11/11
cmake --install <scratch>/all --prefix <scratch>/prefix
cmake -S <worktree>/api -B <scratch>/api-only
cmake --build <scratch>/api-only --parallel 2
ctest --test-dir <scratch>/api-only --output-on-failure           # 1/1

# 2. Existing installed-consumer checks (OFF/ON), unmodified
cmake -S <worktree>/conformance/provider_registration -B <scratch>/reg-off \
  -DCMAKE_PREFIX_PATH=<scratch>/prefix -DAS_ENABLE_FIXTURE_PROVIDER=OFF
cmake --build <scratch>/reg-off && ctest --test-dir <scratch>/reg-off  # 1/1
cmake -S <worktree>/conformance/provider_registration -B <scratch>/reg-on \
  -DCMAKE_PREFIX_PATH=<scratch>/prefix -DAS_ENABLE_FIXTURE_PROVIDER=ON
cmake --build <scratch>/reg-on && ctest --test-dir <scratch>/reg-on    # 1/1

# 3. Task-local C boundary: guard OFF, then opt-in harness ON
cmake -S c_boundary -B <scratch>/cb-off
cmake --build <scratch>/cb-off && ctest --test-dir <scratch>/cb-off    # 1/1
python3 run.py --emit-header
cmake -S c_boundary -B <scratch>/cb-on -DCMAKE_PREFIX_PATH=<scratch>/prefix \
  -DAS_RAII_EVIDENCE_ENABLE_C_BOUNDARY=ON
cmake --build <scratch>/cb-on && ctest --test-dir <scratch>/cb-on      # 1/1
<scratch>/cb-on/as_raii_harness > c_boundary/harness_output.json

# 4. Regenerate canonical artifacts (order matters)
python3 run.py --crosscheck
python3 run.py --report
python3 run.py --sources

# 5. Checks
python3 -m unittest -v test_reference.py
python3 verify.py
python3 check_licensing.py
<scratch-reuse-venv>/bin/reuse lint            # from worktree root, 894/894 clean
python3 <platform>/plan/swarm/check.py --task SDK-C-RAII-RUST-AND-C-BINDINGS
git diff --check && git diff --cached --check
```

Three cold-start repeats of `--crosscheck`, `--report` and `--sources` were
byte-identical (`cmp` + SHA-256); `verify.py` additionally recomputes the
report, source manifest and generated header three times in memory.

## Typical developer API use

```bash
python3 run.py --request request.json --result result.json
```

`request.json` for `inspect`:

```json
{"protocol_version":1,"operation":"inspect","candidate_ref":{"kind":"synthetic-fixture","id":"c-raii-bindings-synthetic-v1","revision":1},"adapter_ref":{"kind":"developer-adapter","id":"raii-model-evidence-v1","revision":1},"configuration":{"profile":"tool"}}
```

`operation` may be `inspect`, `run` (add `"case_id"`) or `validate`. Every
result carries `expose_as_processor: false`, `registered: false`,
`default_enabled: false`.

## Scope guarantees

Only files under `docs/task-evidence/c-raii-rust-c-bindings/` were added. No
shared CMake file, contract, public header, descriptor registry/default,
provider registration, installed v0 behavior, audio-bench, board, handoff,
ruleset, main or other task was changed. The C boundary is a documentation-
only opt-in: default `OFF`, unlinked and unregistered when off, and never
installed, registered or linked into the SDK in either mode.

## Remaining gates

Exact-head independent review; hosted CI on the exact branch head; native Rust
toolchain with pinned provenance before any Rust compile claim; target-device
workload and resource evidence before any workload claim; release approval
before any production exposure.
