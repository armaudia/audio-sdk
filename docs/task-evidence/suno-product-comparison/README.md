<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SUNO-PRODUCT-COMPARISON — Suno product comparison blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Suno product comparison` (`component_id=suno-product-comparison`). The
acceptance profile is **external**. Decision: **DEFER**, before
`exact_source_rights_runtime_and_comparison_admission`;
`evidence_status=incomplete`, `qualification_status=not_qualified`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

Suno is retained as market context for music generation; voice DSP integration is
a separate decision. This package records only source-only context from the
pinned research note. No Suno source, SDK, model, weight, API runtime, output
bundle, comparison corpus, listening result, target-device timing, or opt-in
provider intake is present/admitted. Nothing is downloaded, copied, vendored,
imported, loaded, or executed.

The deterministic surrogate in this package validates comparison-metadata
fail-closed behavior only. It is **not Suno**, **not audio processing**, and
cannot qualify the candidate.

## Exact blocker

| Required artifact | Recorded local state |
| --- | --- |
| Exact source/service/runtime identity | Absent; no pinned Suno source checkout, SDK package, model, API contract, or admitted runtime |
| Rights/terms clearance | Absent; no source/output/corpus/redistribution/product-use/derivative-evidence rights bundle |
| Frozen comparison corpus/protocol | Absent; no rights-cleared prompts/inputs/corpus/protocol with hashes |
| Exact output bundle | Absent; no pinned Suno or comparator outputs/manifests |
| Independent scoring/listening | Absent; no independent score or authorized listening with controls |
| Target runtime timing | Absent; no device p50/p95/p99, RTF, memory, deadline evidence |
| Opt-in provider intake | Absent; no provider/descriptor/registry/default/shared build/CI change made |

## External profile application

| Required item | Evidence |
| --- | --- |
| Allowed access/exact candidate or processed data | Not present; only source-only research context is pinned |
| Local runtime vs vendor-output scoring separation | Explicitly separated as blocked/missing; no runtime/output scoring performed |
| Fallback/disclosure without licensed runtime/code/asset | This package discloses blockers only; no licensed Suno asset bundled |
| Failure/invalid/missing controls | Deterministic record-adverse and nonfinite rejection controls included |

## Deterministic controls

- **Comparison digest:** fixed synthetic comparison metadata records produce a
  byte-identical digest across runs. Records are metadata only, not Suno results.
- **Record adverse:** missing fields, extra fields, empty/invalid strings, and
  non-boolean flags are rejected.
- **Nonfinite:** strict JSON rejects NaN/Infinity/-Infinity.
- **Missing artifacts:** required artifact classes are recorded absent; missing
  results do not qualify.
- **Scope:** no network, no download, no runtime execution, no weights, no real
  audio, no provider registration, task-local only.

## Release gates

All 8 gates are `blocked` with `qualifies=false`: exact source/service identity,
rights/redistribution clearance, frozen comparison corpus, exact output bundle,
independent scoring/listening, target runtime timing, failure/nonqualification
controls, and opt-in provider intake.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, blockers, controls, gates. |
| `reference.py` | Deterministic report/contract builders, strict parsers, controls. |
| `run.py` | Builds report 3x, requires byte identity, regenerates artifacts. |
| `report.json` | Canonical machine-readable external report. |
| `report.json.sha256` | Digest of committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and manifest. |

## Source pins (SHA-256)

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/cpp-lib-market-benchmark-20261109.md` | `d1a4edbf72257ebb989d9639e542cf2c50152e323dc9081f2af868708064a3e7` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->

| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `748abebbaf6335a821dc9cf4e0af626a9bbdf85c9a49b78eeab117fbfae12022` | 9865 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `81f461b177ae1e28e9aa05d983ef8bb1a87958a8eb946c3a22e406572a006558` | 34171 |
| `report.json` | `27da738546f7436754d382ccbbc03aba956b196cc9f724af4565fb09a3a84dfd` | 11742 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `2c1957e3631d8ee9f013f7b2d213983bde796b9dcf6d3ff786f352f0e8de6da1` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `61d5a673f728752e680fe9df2da542f9b16fc7063003750956c3e3ae3802d172` | 1997 |
| `test_reference.py` | `b835d97867a434b38b6800b396e17529ef80a937633aa4550bd392259e69bd52` | 6017 |
| `verify.py` | `5d23c8ff644e8e23e8118d8d079aeddc5720c96f84a596991258b9e71727532d` | 13566 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
