# audio-sdk handoff

Updated 2026-11-14. This is a local macOS arm64 engineering candidate, not a
public or release-qualified SDK.

## Current candidate

- Candidate: `macos-arm64-20261114-foundation-09`
- Archive SHA-256: `5707c4ff688d12876c3ff3e290db7c5eda76f8bdd2fa28e6fe197abd1353a464`
- Candidate manifest: `build/candidates/macos-arm64-20261114-foundation-09/candidate-manifest.json`
- Build ID: `audio-sdk/0.1.0+sha256:15959d8f04e8080c5804b3019decea7c720b27e1593a43352cf9ba97d5a6cb1c`
- Contract revision: 0.1; source-linked C11 API for mono f32, 16 kHz, 160-sample application frames.
- Candidate 09 contains external asset descriptor/config validation, facade-owned byte copies, SHA-256 verification, reset/close overlap test, SPSC queue changes, and a manifest generator that records observed results rather than fixed passing counts.

## Local evidence

On macOS arm64 with Apple clang 21.0.0 and CPython 3.12.16:

- Release CTest: 11/11 passed.
- ASan/UBSan CTest: 11/11 passed.
- TSan CTest: 11/11 passed, including the overlapping reset/close case.
- Installed external-provider CTest: 10/10 passed.
- Speex and high-pass conformance: 37/37 each.
- CPython 3.12 installed-wheel tests: 4/4 passed.
- These are local host results; they do not imply Linux or hosted CI qualification.

Recheck/package commands:

```sh
cmake -S . -B build/all -DCMAKE_BUILD_TYPE=Release
cmake --build build/all --parallel 2
ctest --test-dir build/all --output-on-failure --timeout 60
./scripts/package.sh build/all build/candidates/macos-arm64-20261114-foundation-09
```

The candidate directory already exists; packaging refuses overwrite. Use a new
candidate ID for any changed bytes. `scripts/create_candidate_manifest.py`
reads the actual CTest JUnit reports, conformance JSON, and Python-wheel test
report; absent/stale evidence is recorded as unrun/unverified, never passed.

## Remaining release gates

- Legacy `ae_*_v1` compatibility adapter and ABI/layout review are absent.
- Legal/release clearance for all SDK content has not been independently decided.
- Linux x86-64 build, package, dependency audit, sanitizer run, and hosted CI have not run.
- Independent clean-build reproducibility is not established for Candidate 09.
- Python test scope remains smaller than the complete planned binding acceptance matrix; non-macOS loading is unverified.
- Broad concurrent lifecycle/race stress and complete source-range cancellation accounting remain open. The new deterministic reset/close overlap is one focused regression, not full stress qualification.
- Callback-safe mode 1 is not advertised. Stable binary plugin compatibility is not promised.
- LiveKit S09, rights-gated neural S10, separate engine ABI S11, and broader formats/hosts S12 remain deferred.

## Asset contract and downstream consumers

`CONTRACTS.md` and the installed descriptor schema now define external assets
as ordered `{byte_count,id,sha256,storage:"external"}` entries. Creation
requires exactly those assets; the facade verifies declared IDs, lengths,
configured digests and actual bytes before passing owned copies to provider
creation. Embedded assets are explicitly outside contract 0.1. The synthetic
asset test exercises copy and rejection paths. Pro declares the Tiny16 weights
asset but remains disabled unless a separate documented rights decision is
made; SDK asset support alone does not grant model permission.

Consumers are pinned to Candidate 09 with their own file/schema snapshots:
`../audio-bench/deps/lock.json` and `../audio-pro/deps/lock.json`. Benchmark is
evaluation-only and must never become an SDK runtime dependency.
