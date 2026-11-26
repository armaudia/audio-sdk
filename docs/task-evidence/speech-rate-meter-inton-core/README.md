<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECH-RATE-METER-INTON-CORE — speech-rate-meter / inton-core blocker

**Decision `DEFER`; status `proposal_only_blocked_incomplete`; evidence `incomplete`; qualification `not_qualified`; eight release gates blocked.** This directory is a bounded, deterministic, task-local feasibility record for `speech-rate-meter / inton-core` (task `SDK-SPEECH-RATE-METER-INTON-CORE`, mode `feasibility`, profile `rate`, repository `audio-sdk`). It is **not** a candidate implementation, adapter, provider, benchmark, listening result, timing result or release claim. No speech-rate-meter or inton-core source, binary, runtime, model, corpus or device measurement is present. **No result here qualifies the candidate.** No provider, default, descriptor, registry, installed v0 path, public API/ABI, shared build, dependency lock, CI, board or handoff file is changed.

## Exact external blocker

The pinned source `cpp-library/pipeline-validation/playback-speed-candidates.md` records `speech-rate-meter / inton-core` as an MIT C++ reference reporting wpm, articulation rate and pause statistics, with desktop/Qt heritage and low maintenance; it also records the repository locator `https://github.com/zhitko/speech-rate-meter`. The same note states no local build or benchmark of speech-rate-meter was performed.

The note supplies **no** immutable revision, reviewed license/notice bundle, dependency/runtime pin, machine-readable output schema, timestamp/window definition, rights-cleared cohort, or matched rate evidence. Missing artifacts are not downloaded, reconstructed, mirrored, substituted or inferred.

The exact blocker is therefore: **no caller-supplied, identity-verified, rights-cleared speech-rate-meter / inton-core source/runtime, no mapped timestamp/metric contract, and no matched rate-profile evidence at the installed 16 kHz mono f32 160-sample boundary.**

Six open blocker classes (eight release gates):

| Blocker | Missing artifact / requirement |
| --- | --- |
| `BLK-01` | Exact immutable source revision, reviewed MIT/license text, notice bundle and clean checkout. |
| `BLK-02` | Pinned offline runtime/build, dependency digests and deterministic execution trace. |
| `BLK-03` | Written rights/scope for source, dependencies, corpora and outputs. |
| `BLK-04` | Exact timestamp mapping and WPM/articulation-rate/pause definitions, units, windowing and invalid/nonfinite behavior. |
| `BLK-05` | Rights-cleared matched rate cohort: 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, with independent controls/failure cases. |
| `BLK-06` | Target-runtime timing/memory/deadline and OFF-by-default opt-in provider intake with independent exact-head review. |

**Reopen condition.** Supply the exact source revision and reviewed license/notice, a pinned offline runtime/build, written rights/scope, a mapped timestamp/metric contract, rights-cleared matched rate evidence with required strata and controls, target-runtime timing, and OFF-by-default opt-in provider intake with independent exact-head review. Until then the candidate stays `DEFER`, incomplete and not qualified.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | `SDK-SPEECH-RATE-METER-INTON-CORE` | Stable board-row identity only; mutable TASKS.json not hashed |
| Candidate | speech-rate-meter / inton-core | No source/checkout/runtime present |
| Reported metrics | wpm, articulation rate, pause statistics | No output schema or measurement |
| Reported license | MIT | Unverified claim only |
| Repository | https://github.com/zhitko/speech-rate-meter | Locator only; no fetch |
| Installed SDK v0 geometry | 16 kHz, mono, f32, 160 samples/frame | Unchanged; no candidate mapping |

## What this package verifies

1. **Absence evidence.** Fixed probes for source/runtime/adapter locations are checked; present probes fail verification.
2. **Stable pins and digests.** Source, SDK boundary and local artifact digests are pinned in `SOURCES.sha256`; README digest tables are validated.
3. **Stable board identity.** Only stable linked-row fields are gated by SHA-256. The mutable full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to this package.
4. **Rate-profile application.** All eight release gates are blocked. No missing result is promoted.
5. **Fail-closed caller-asset validation.** A strict manifest schema rejects unknown/missing fields, bad hashes, relative/missing paths, bad geometry and nonfinite/float/bool issues. A schema-only control is validated but marked not qualifying.
6. **Deterministic synthetic boundary surrogate.** A small stdlib-only surrogate exercises timestamp/rate accounting and rejection behavior; it is explicitly not the candidate and cannot qualify.
7. **Deterministic regeneration.** `run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, the README artifact table and `SOURCES.sha256` with three byte-identical report builds.

## Rate profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Source/output mapping and duration | blocked | No candidate output or mapped timestamp contract. |
| Pitch and transient audibility | blocked | No candidate audio processing or listening result. |
| Playback buffering and drift | blocked | No runtime/buffer/drift measurement. |
| Identity 1x control | blocked | No candidate 1x result. |
| Rate changes | blocked | No candidate rate-change result. |
| Unfamiliar speech, music and silence | blocked | No rights-cleared cohort. |
| Rebuffer and final partial window | blocked | No runtime/rebuffer/final-partial measurement. |
| Pause/filler tied to source timestamps | blocked | Reported pause metrics are unverified; no timestamp contract. |

## Reproduction

```sh
cd docs/task-evidence/speech-rate-meter-inton-core
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

## Source pins

<!-- DIGEST_TABLE_SOURCE_START -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- DIGEST_TABLE_SOURCE_END -->

## Boundary pins

<!-- DIGEST_TABLE_BOUNDARY_START -->
| Path | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `sdk:README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- DIGEST_TABLE_BOUNDARY_END -->

## Artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `README.md` | `0000000000000000000000000000000000000000000000000000000000000000` | 8983 |
| `contract.json` | `0353cd20089d2368753ba3a918df85e359fed8883396a113c16db7d20f441b60` | 10752 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `69c3e4ab50c583bf96ebbb3556a7041c82bc8153c8e952b818fccd5d6cde4446` | 40031 |
| `report.json` | `083b98cee53b90920c77f17c41524678f1e947c2c09ee29897fa299210756a82` | 13632 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `6c92209f1351429c5808d2311a091ed7838df844871870c787325572bce07aae` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `aaebbfb63feadc982575e5134a260f39f6778e8f3ceba129956a32e3aadb9aa7` | 1566 |
| `test_reference.py` | `44865ed990e425f809c9f18d5c9814ecb7fac6ac2640b563165fd85a8e8be53a` | 7172 |
| `verify.py` | `8e8944257e389dd5d9ac6cd6f5824d686f2d738dda26aaaa0d7e3496310016fd` | 14838 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
