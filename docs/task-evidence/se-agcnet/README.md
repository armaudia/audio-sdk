<!-- SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SE-AGCNET SE-AGCNet feasibility evidence

**Decision: `DEFER` · Qualification: `not_qualified` · Status: `proposal_only_incomplete`**

This package is a bounded, task-local blocker/proposal record for `SDK-SE-AGCNET`.
It does **not** implement SE-AGCNet, load weights, run inference, download assets,
register a provider, change installed v0/API/ABI/registry/default/shared build/CI,
or make any benchmark, listening, device-timing, or release claim.

## Exact external blocker

No exact SE-AGCNet source revision, license/NOTICE review bundle, model
weights/checkpoint identity, runnable offline runtime, feature/gain/loudness
geometry, rights-cleared matched cohort, or qualified DSP evidence is locally
present or recorded. Research describes the method, but no candidate result can
be reproduced, measured, or qualified in this workspace.

## Reopen condition

A caller must supply the exact SE-AGCNet source revision and reviewed
license/NOTICE/third-party terms, exact model/checkpoint bytes and digests, an
offline locked runtime, frozen audio/feature/loudness geometry and any SDK
bridge, a rights-cleared matched cohort, independent DSP evidence including
separate DSP AGC comparison and content/timing/resource measurements, and opt-in
OFF-by-default intake with exact-head independent review. Every gate must clear
before this task reopens.

## Source pins

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
<!-- digest-table: end -->

## Artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 |
| --- | --- |
| `docs/task-evidence/se-agcnet/LICENSES.md` | `a03a4f0397ad1719548ea063987e7188eeb8ef21d3c0714963d611f3e9c642b7` |
| `docs/task-evidence/se-agcnet/SOURCES.sha256.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `docs/task-evidence/se-agcnet/contract.json` | `f68f0305ca0004bdd5ac0f0751392376e3f3a6365d8c29b22123c7bd0843febc` |
| `docs/task-evidence/se-agcnet/contract.json.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `docs/task-evidence/se-agcnet/reference.py` | `f9756524954a0af6f4c65c9f49d9572a9e22bb2e8e7850d2375839a210f550c8` |
| `docs/task-evidence/se-agcnet/report.json` | `5c1cf14eef4c3a81e79260a46449beb39f4f7831e2c30bfa40cc7ce312e0f8e4` |
| `docs/task-evidence/se-agcnet/report.json.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `docs/task-evidence/se-agcnet/report.json.sha256` | `7cfb2718024ee0b2ab7c0c614cea7b04601cd6df7dade147f195cd6ba91b90b1` |
| `docs/task-evidence/se-agcnet/report.json.sha256.license` | `44791d7328a25c7bbda2c869e9139d06a156774909550fc3cd2e8ce8efda85c8` |
| `docs/task-evidence/se-agcnet/run.py` | `ad8dda2e120af027438018282a6f46bb8380228687ce9dcd81d94f3687ff1fdd` |
| `docs/task-evidence/se-agcnet/test_reference.py` | `5118782a1668e9c5cabf5be8819420e29672ecaf45f93b0d29b355c4f253bf23` |
| `docs/task-evidence/se-agcnet/verify.py` | `f407f0a095c7fda21eb35cb2b61eae7fbdb0af745cc885abb6dcecfe8015cea8` |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Release gates

All eight release gates are blocked: upstream source/model pin, license/NOTICE/rights
review, offline runtime/deterministic load, geometry/delay/state/SDK bridge,
separate DSP AGC comparison and cohort, DSP gain/response/attack-release/headroom/numerics,
target timing/memory/callback suitability, and provider intake/independent review/release.

## Regeneration

```sh
python3 docs/task-evidence/se-agcnet/run.py
python3 docs/task-evidence/se-agcnet/verify.py
python3 -m unittest docs/task-evidence/se-agcnet/test_reference.py
```
