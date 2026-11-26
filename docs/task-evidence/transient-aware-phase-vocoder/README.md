<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TRANSIENT-AWARE-PHASE-VOCODER - readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`; qualification `not_qualified`.** This directory is bounded, deterministic, task-local feasibility evidence for the Transient-aware phase vocoder row. It is **not** an implementation, adapter, model, runtime, or rate controller. No exact licensed runnable source, immutable revision, pinned runtime, rights-cleared corpus, audio, output, listening result, device measurement, benchmark, or release claim is present. **No result here qualifies.**

`plan/INVENTORY.json` records `transient-aware-phase-vocoder` as `evidence_status=considered`, `disposition=sdk-reference`, area `Rate and content`, with the **Rate** acceptance profile and task `SDK-TRANSIENT-AWARE-PHASE-VOCODER`. The pinned evidence note (`cpp-library/pipeline-validation/playback-speed-candidates.md`) describes transient-aware phase vocoding as a method direction (phase vocoder + phase locking + transient handling), but it does not provide an exact staged implementation, immutable source revision, runtime lock, or matched rate evidence for this task. Classical phase-vocoder-baseline and neural transient-preserving siblings are separate candidates and are not inherited.

## Exact external blocker

The exact **licensed runnable source/implementation at immutable revision**, **pinned runtime and task geometry**, **reviewed rights/terms**, **rights-cleared inputs**, and **matched Rate evidence** are absent. Nothing was fabricated, reconstructed, mirrored, downloaded, or substituted. No revision, file name, byte count, or SHA-256 is asserted as a verified candidate artifact.

| Missing artifact | Exact requirement |
| --- | --- |
| Named source and license | Exact transient-aware phase-vocoder implementation at immutable commit/tag with reviewed license/notice text and per-file SHA-256 manifest. |
| Runtime and geometry | Locked offline runtime with dependency hashes, platform/device, dtype, determinism settings, and exact sample rate/frame/hop/window/phase/latency/reset/drain behavior. |
| Assets/dependencies | Every required asset/dependency with byte counts and SHA-256; no mutable download. |
| Rights-cleared inputs | Reviewed code/asset terms and rights-cleared speech/music/transient inputs with consent, evaluation, and redistribution decisions. |
| Matched evidence | Deterministic outputs and full Rate-profile measurements on a rights-cleared matched cohort; no sibling/control substitution. |

Machine-readable records: `contract.json` and `report.json` (`decision="DEFER"`, `qualification_status="not_qualified"`). `report.json.sha256` pins report bytes. `SOURCES.sha256` pins source, boundary, and task-local artifacts.

## Task identity and scope gate

- Task: `SDK-TRANSIENT-AWARE-PHASE-VOCODER` (`transient-aware-phase-vocoder`, feasibility, audio-sdk).
- Depends on: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
- Claimed base: `26bc48c58f9d69571571fa651862dcbe0fe1172d`, branch `swarm/SDK-TRANSIENT-AWARE-PHASE-VOCODER`.
- Write scope: `docs/task-evidence/transient-aware-phase-vocoder/` only.
- Mutable board fields (`status`, `owner`, `claim`, `review`, `handoff`, `blocked_reason`, `dispatch_priority`) are excluded from gating; only stable linked-row identity is hashed/gated.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in `report.json` -> `rate_profile`. Every required measurement row is `blocked` or `documented` separation-only; no row qualifies. Zero real results, zero synthetic results, no surrogate.

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No exact runnable candidate/runtime/output. |
| Duration | blocked | No candidate output or target/actual duration. |
| Pitch | blocked | No candidate output or listening/result. |
| Transient audibility | blocked | No candidate output or listening/proxy result. |
| Playback buffering | blocked | No device/scheduler/fill/flush/deadline measurement. |
| 1x control | blocked | No runtime. |
| Rate changes | blocked | No step/ramp execution. |
| Unfamiliar speech | blocked | No rights-cleared input. |
| Music | blocked | No rights-cleared music/negative control. |
| Silence | blocked | No silence execution. |
| Rebuffer/drift/final partial | blocked | No playback/buffer execution. |
| Pause/filler timestamps + speech preservation | blocked | No timestamped policy or preservation measure. |
| Separate evidence categories | documented | Source-reported/schema-only/missing-real/sibling sections kept separate. |

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| RG-01 named source/license provenance | blocked | Provide exact immutable source with reviewed license/notice manifest. |
| RG-02 pinned runtime/exact geometry | blocked | Provide locked offline runtime and exact geometry/latency/reset/drain contract. |
| RG-03 assets/dependencies | blocked | Stage/verify required assets with byte counts and SHA-256. |
| RG-04 rights-cleared inputs | blocked | Freeze reviewed terms and rights-cleared matched inputs. |
| RG-05 deterministic execution/output validity | blocked | Execute pinned candidate offline with deterministic finite hashed outputs. |
| RG-06 Rate profile evidence | blocked | Run full Rate profile on rights-cleared matched cohort with required controls. |
| RG-07 timing/resources/listening | blocked | Measure target pacing/resources and complete authorized listening/labeled screen. |
| RG-08 intake/release review | blocked | Separate OFF-by-default intake, clean-install proof, independent exact-head review. |

## Reproduction

Requires CPython 3.11.5 with `PYTHONDONTWRITEBYTECODE=1`.

```sh
cd docs/task-evidence/transient-aware-phase-vocoder
PYTHONDONTWRITEBYTECODE=1 python3 reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates contract/report/sidecar/README tables/SOURCES three times and fails on byte drift. `verify.py` is read-only and re-runs regeneration in a temp dir.

## Source pins (SHA-256)

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `docs/task-evidence/phase-vocoder-baseline/report.json` | `555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json` | `131640f3c436426827a3cc18c0183195dbb3839cf96b85353e0d79864f222dc5` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact pins (SHA-256)

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 |
| --- | --- |
| `docs/task-evidence/transient-aware-phase-vocoder/LICENSES.md` | `2e780cde71c12ee3ad7922a30156f828518e79090603bee59b33218a7f8bcdf0` |
| `docs/task-evidence/transient-aware-phase-vocoder/SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/transient-aware-phase-vocoder/contract.json` | `e1b5757836093c39aa49fb23b09e6cc0ce854a28fc717b25e10a2d08d997d52b` |
| `docs/task-evidence/transient-aware-phase-vocoder/contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/transient-aware-phase-vocoder/reference.py` | `02123a1306841639f58fef32a5e8443c9a98e5312d19ff9c9923b509d9b54705` |
| `docs/task-evidence/transient-aware-phase-vocoder/report.json` | `609067ec3cf3f44dba7844e1be27c6e4ea2139ec62848702fdc3c8d1ba3e7f0a` |
| `docs/task-evidence/transient-aware-phase-vocoder/report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/transient-aware-phase-vocoder/report.json.sha256` | `eb395856677bcd34aabeb19d550c75c21aa49886aa551831f621b11ce8dc41a2` |
| `docs/task-evidence/transient-aware-phase-vocoder/report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/transient-aware-phase-vocoder/run.py` | `d80390f7be5f021596e6c782ca9e7da63525006afbc21c1ee231ca17274020f1` |
| `docs/task-evidence/transient-aware-phase-vocoder/test_reference.py` | `8298eb96b31f7252a19ab188d266d5b7fb625d49e4683bdb0272debbed308eaa` |
| `docs/task-evidence/transient-aware-phase-vocoder/verify.py` | `2bfb070e3db33b026afe8ca726699026cb45ea0d80ffb1c483ab0f0402d57321` |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
