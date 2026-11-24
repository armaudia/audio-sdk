<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NIGHTLY-RELEASE-EVIDENCE-AND-PYTHON-C-INSTALLER — task-local Tool-profile evidence

**Proposal-only, synthetic, incomplete and not qualified.** This package adds a
deterministic, task-local matrix extending the existing local
package/conformance record with one row set for **Python wheel + installed C
consumer**. It applies the **Tool** acceptance profile. It is not a nightly
build, a publication, a signature, a target-platform qualification, a workload
measurement or a release claim.

It changes **no** CI file, build file (`CMakeLists.txt`, cmake modules, package
scripts), release workflow, `RELEASING.md`, `CONTRACTS.md`, public API/ABI,
descriptor registry, registry default, advertised support or installed v0
behavior. All real build/install commands in the reproduction write **only to a
caller-owned scratch directory outside the worktree**; no sealed candidate is
created and nothing is published. The installed v0 geometry stays exactly
**16 kHz, mono, float32, 160 samples per call**.

## Exact public-boundary model

The shipped v0 facade has a registry/session API
(`api/include/audio_sdk/session_v0.h`), a provider ABI
(`api/include/audio_sdk/provider_v0.h`), one 160-sample call, a source-coordinate
`first_input_sample`, declared provider delay and startup/drain flags. The
Python wheel is a thin stdlib `ctypes` binding that requires an explicit
`AUDIO_SDK_LIBRARY` absolute path; it performs no implicit library lookup.
The installed C consumer includes the installed public headers, links
`-laudio_sdk` and exercises registry create/close; the C++20 consumer checks
`AS_ABI_MAJOR`.

The pure-stdlib `fixture.py` models **boundary metadata only** (counts, flags,
source mapping, epochs, state, malformed-call rejection and missing-selection
rejection). It never synthesizes or substitutes native provider DSP. Native
provider output digests are recorded observations, not model outputs; the
crosscheck compares metadata and explicitly reports `native_dsp_not_modelled=true`.
Both built-in providers are recorded as `registered_by_this_task=false`,
`enabled_by_default_by_this_task=false`, `descriptor_settings={}`. No new
provider is compiled, registered or enabled.

## Files

| Path | Purpose |
| --- | --- |
| `fixture.py` | Frozen observed constants, seeded synthetic generator, v0 reference boundary model, controls, crosscheck and report builder. |
| `tooling.py` | Developer-facing reproducible installer/probe entry point (`--print` / `--run <fresh-dir>`); local tooling only, no network, no worktree writes. |
| `run.py` | Regenerates `report.json` byte-for-byte from frozen inputs; no build/install/network. |
| `report.json` | Canonical machine-readable Tool-profile evidence. |
| `report.json.sha256` | Sidecar digest of the committed report. |
| `SOURCES.sha256` | SHA-256 pins for every external/boundary file and every task-local artifact. |
| `test_fixture.py` | 28 unittest checks: pins, licensing, determinism, profile, matrix, gates, controls, state, scope. No skips, no network. |
| `verify.py` | Read-only pin/JSON/reproduction/licensing/scope verifier. |
| `README.md` | This file. |

## Pinned source, boundary and artifact digests (SHA-256)

`RELEASING.md` is pinned **exactly** at
`67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3`.
External paths are workspace-relative; other paths are worktree-relative. All
are machine-checked in `SOURCES.sha256`.

| Path | SHA-256 |
| --- | --- |
| `audio-benchmark-platform/audio-sdk/RELEASING.md` | `67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` |
| `docs/acceptance-matrix.md` | `2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e` |
| `docs/task-evidence/s06.md` | `6edef4993e22512157cd9a99ffda6d8551da31f388461e6b2cc2f5f0b8bf7620` |
| `docs/task-evidence/s07-build-identity.md` | `10efd7bacc3566b638a40a45d6876abf365be5ad7287b0f35a91ddf2b23a7d3a` |
| `docs/task-evidence/s08.md` | `6fa3622269f48b7366dd89c1dc25f9f8a857a2e1bf6dd222578c8a18d2a37c3f` |
| `docs/evidence-handoff.md` | `05ffddfecec4679fbd0f4ec1e1814bd8f4fb00ede69f787e4e8bd19784502f72` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `bindings/python/pyproject.toml` | `0f3b1e736dd807a984cbb9daa10cd0ba32668f7833994c3c4f0a5021799c95a4` |
| `bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `bindings/python/tests/test_sdk.py` | `32c4cecab24b00fc3be312f64e9def05a5391b0f475cd9d461321e8fc4d4c101` |
| `conformance/main.c` | `71cf0c7a480ef384e0f1500a5af3c35ed85c9a17625efa3d0d09fddb458287ea` |
| `conformance/evidence/positive/input.json` | `a112e8c106b4b013f8fdf16af325e3d60b7ee4666bb3e57deec9bb1749369492` |
| `conformance/evidence/negative/input.json` | `1d465ecb667a8979a2256da02f060c59827ea213ec45afb592b67c452a331d52` |
| `conformance/evidence/incomplete/input.json` | `fdc30570da1cc70c6c387bec1391a8856d96d29ab3043225a6fbd81ced12b1d6` |
| `scripts/verify_install.sh` | `6a0737031697c7e4551a294c6df3185b0e6a6101c86143341c57c9b620cae390` |
| `scripts/package.sh` | `b9f9e52cc5e36fec03ab01e81bcfa45de87be4faae71f44922a7446e40a132e2` |
| `fixture.py` | `91ce94b27250028280380b579cbf15ac369e3863c73281055515e2c8cca9b5af` |
| `tooling.py` | `83f2d525d98862e9c64b08e10084da4a10a356b417740d81114f94f90bf7e8e7` |
| `run.py` | `01d57a18af71bdc9012f6dc7a15b1d248173ffd18dd566005cc923835ef206fe` |
| `test_fixture.py` | `1576802e529764c2f7f8fa546b3afa32b8738c2499365255f22a3adab1758aba` |
| `verify.py` | `b63c04dff93204e1814ba3f8dd3e34faf85c3c11a72b5d628ca2359534e40d1d` |
| `report.json` | `fb30319869045fa6b953c87a8c0f16558757cf511df6a7011e11f4aa39ba9584` |

## Toolchain pins (observed locally)

Pinned interpreter **`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`**
(Python 3.12.16); pip 25.0.1, setuptools 84.2.1, wheel 0.48.0; CMake 3.27.4;
AppleClang 21.0.0.21000401 (C11 and C++20); Darwin arm64, Release build. No
network, no download, no licensed/vendor runtime, no real audio, no device.

## Reproducible setup (exact commands)

From this directory, read-only checks with the pinned interpreter:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_fixture.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-NIGHTLY-RELEASE-EVIDENCE-AND-PYTHON-C-INSTALLER
```

Print the exact developer-facing installer matrix (no writes):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 tooling.py --print
```

Re-execute the local-only setup in a **fresh scratch directory outside the
worktree** (the entry point refuses any path inside the worktree and refuses a
non-empty directory):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 tooling.py --run <fresh-scratch-dir>
```

The ordered commands executed by `--run` are (with `<WT>` the pinned checkout,
`<WORK>` the scratch dir, `<PREFIX>=<WORK>/install/audio-sdk-0.1.0`):

```sh
git -C <WT> rev-parse HEAD && git -C <WT> status --porcelain
cmake -S <WT> -B <WORK>/build -DCMAKE_BUILD_TYPE=Release
cmake --build <WORK>/build --parallel 2
ctest --test-dir <WORK>/build --output-on-failure
cmake --install <WORK>/build --prefix <PREFIX>
cc -std=c11 -Wall -Wextra -Werror -I<PREFIX>/include <WORK>/consumer/consumer.c -L<PREFIX>/lib -laudio_sdk -Wl,-rpath,<PREFIX>/lib -o <WORK>/consumer/consumer-c && <WORK>/consumer/consumer-c
c++ -std=c++20 -Wall -Wextra -Werror -I<PREFIX>/include <WORK>/consumer/consumer.cpp -L<PREFIX>/lib -laudio_sdk -Wl,-rpath,<PREFIX>/lib -o <WORK>/consumer/consumer-cpp && <WORK>/consumer/consumer-cpp
<PREFIX>/bin/audio_sdk_conformance --provider speex.ns.v0 --report <WORK>/reports/speex-report.json
<PREFIX>/bin/audio_sdk_conformance --provider dsp.highpass80.v0 --report <WORK>/reports/highpass-report.json
<P312> -m pip wheel --no-deps --no-build-isolation --wheel-dir <WORK>/wheels <WT>/bindings/python
<P312> -m venv <WORK>/venv312
<WORK>/venv312/bin/python -m pip install --no-index --no-deps <WORK>/wheels/audio_sdk-0.1.0-py3-none-any.whl
AUDIO_SDK_LIBRARY=<PREFIX>/lib/libaudio_sdk.0.1.0.dylib PYTHONDONTWRITEBYTECODE=1 <WORK>/venv312/bin/python -m unittest discover -s <WORK>/acceptance/tests -v
AUDIO_SDK_LIBRARY=<PREFIX>/lib/libaudio_sdk.0.1.0.dylib PYTHONDONTWRITEBYTECODE=1 <WORK>/venv312/bin/python <WORK>/probe.py
```

`scripts/package.sh` is deliberately **not** run: it creates a sealed release
candidate and is part of the release workflow, which this task does not touch.

## Expected counts and digests (observed 2026-11-24)

- Base: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`; clean checkout before build.
- Build ID: `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.
- CTest: **11/11 passed**, 0 failed, 0 skipped.
- Native install: dylib `4db4ee75061e47513530ed1ce37de63867c41f9560d51d7aff21ff44796a3d5f`; static lib `caafbbeaf0463ae7634eacb20dc0d153a7c1f89dd6e87a526025b3a94cf18384`; `build-info.json` `5848b1c126a662da24ad9a30c77581e0ca798e8a42eefad1bda55971a6f957b2`.
- Installed C11 and C++20 consumers: compile/run all exit 0, `-Werror`.
- Installed conformance: `speex.ns.v0` 40/40 pass, report `accbe82e7460ec79a66f29b8b7b791a3d1cf7da56cf5d432a0f60de00c30f529`; `dsp.highpass80.v0` 40/40 pass, report `d8f5963cd949e4c7654c84a152ef0911256d282f042f846966f9f7d1220311ea`.
- Wheel `audio_sdk-0.1.0-py3-none-any.whl`: first build `fc7012d6bdc441e9c19c932833bff5bc607ee6fb9351493f1f52713cfc8a91d5`; second build `c8a6fbe39ee545f3f7bdfb93e20329e90225b89e932b64590cd450917d2d58b7`; third build via `tooling.py --run` `0716f91e12dd417b0fe8ccd7c9973f12a4d85afea08a459a20c9d3927d56a9b6` (three distinct digests — see regressions). Clean venv, no source-tree import.
- Installed-package tests: **5/5 passed**, 0 failed, 0 skipped.
- Synthetic probe: seed `31337`, 8 frames / 1,280 samples, input f32 digest `dde869989a497e3f522af8ab20bf1124ee0690f2740882a98b726eff07039324`; two runs byte-identical; probe output digest `344dff2f98cd7c856c3721f115ded222653637f81a8c349e627d7722be06e5cf`.
  - `dsp.highpass80.v0`: 1,280 produced, 1,280 valid, 0 drain, output `586fb886a72e83664c91fd1f5b14fea57fcf25069fcd3c9709b87a7f0b37abc9`, flags all 0, sources `0..1120`, all finite, caller inputs unchanged.
  - `speex.ns.v0`: 1,280 produced, 1,120 valid, 1 drain, output `a3e8f15e622c07310363bf3ba74945ef57dc05a178a84ec41b1ad82ae3251527`, first flag `1` (startup padding), sources `-160..960`, all finite, caller inputs unchanged.
- Malformed inputs: `short_frame`, `nonnumeric_valid_count`, `negative_epoch` each `ValueError` with state intact.
- Missing optional selections: unknown provider `RuntimeError`; unset `AUDIO_SDK_LIBRARY` → `OSError: set AUDIO_SDK_LIBRARY to an explicit SDK library path`; wrong path → `OSError: AUDIO_SDK_LIBRARY must name an existing absolute path`. No fallback or substitution.
- Crosscheck: all metadata checks pass; native DSP is explicitly not modelled.
- `tooling.py --run <fresh-scratch-dir>` was executed end-to-end: exit 0, probe
  output byte-identical across its two runs, and all deterministic matches
  true (head, build ID, dylib digest, both conformance report digests, probe
  output digest, probe byte-identity, wheel name). Only the wheel archive
  digest differed again, as recorded above.
- `report.json` SHA-256: `fb30319869045fa6b953c87a8c0f16558757cf511df6a7011e11f4aa39ba9584`.
- Spec digest: `6e5cfd696c25023cc35d2862aa2877898da579f872542364298cc118dfa2f40f`.
- Tests: 28 passed, 0 failed, 0 skipped.

## Support separation (no implication of wider support)

| Support class | Status | What it covers |
| --- | --- | --- |
| compile/build | observed_local | clean checkout, CMake configure/build, installed C11/C++20 consumer compile, wheel build/install (M01, M02, M04, M06, M11–M13 blocked where publication/targets are concerned). |
| synthetic_runtime | observed_local, **non-qualifying** | 11/11 CTest, 40+40 conformance, 5/5 installed wheel tests, deterministic 8-frame synthetic probe, malformed/missing-selection controls (M03, M05, M07–M09). |
| measured_workload | **blocked** | No paced/deadline/CPU/memory/device measurement; no workload support claim (M10, M14). |

The matrix adds **no advertised support**: every row records
`advertised_support_delta="none"`. The existing matrix's S12 "broader formats
and hosts excluded", S07/S-T12 "no new sealed candidate" and
"local macOS arm64 only" scope are preserved. Linux x86-64, Windows
(compilers removed from PATH), WebAssembly/Node and hosted CI were **not** run.

## Honest regressions / limitations (verbatim)

1. **Wheel is not byte-reproducible**: three builds of the same pinned checkout
   gave `fc7012d6…`, `c8a6fbe3…` and `0716f91e…`. No reproducible-package claim.
2. **Historical wheel digest differs**: `s08.md` records `ea4ce935…` from a
   different toolchain/environment; it is pinned context, not pooled.
3. **Historical counts changed**: the acceptance matrix/s06/s08 record 10/10
   CTest and 4/4 Python tests; this base observed 11/11 and 5/5. Reported
   verbatim, not as an advertised support change.
4. **Historical build IDs differ**: s07 records `307f828c…` and `fe66742b…`;
   this build reports `0bc71dca…`. Identity difference alone proves no
   reproducibility.
5. **No target breadth**: Darwin arm64 only; no new target claim and no
   publication or release result.

No losing control is hidden: the model-vs-native crosscheck is metadata-only,
the native DSP digests are observations, and every blocked gate remains blocked.

## Explicit gates and reopening conditions

`no_missing_result_qualifies_candidate=true`: any blocked gate or missing result
keeps the candidate `not_qualified`. Status is
`proposal_only_synthetic_incomplete`. Nothing here may be promoted to a release
or quality claim.

| Gate | Status | Exact reopening condition |
| --- | --- | --- |
| `actual_nightly_publication` | blocked | Define and review an explicit nightly channel; run it on approved infrastructure with an up-to-date branch; record the published immutable artifact digest and location. |
| `signing_and_attestation` | blocked | Produce and independently verify signatures/attestations for the exact published artifacts under the release environment with recorded key provenance. |
| `target_platform_breadth` | blocked | Run the pinned procedure on each advertised target with recorded toolchain, archive digests and installed-consumer results, without widening support by implication. |
| `release_claim` | blocked | Complete hosted CI, rights/license decisions, clean install evidence on advertised targets, limitations and release notes under `RELEASING.md`, with independent review. |
| `measured_workload_support` | blocked | Measure the exact installed build on the intended host under pacing, load and explicit deadline/CPU/memory budgets. |
| `sealed_archive_reproducibility` | blocked | Seal two clean-build candidates with normalized metadata and verify byte-identical archives and installed bytes on pinned toolchains. |

No real weights, downloads, licensed runtime, listening result, device trace,
published artifact, signature, provider registration or shared-source change is
used. Base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`.
