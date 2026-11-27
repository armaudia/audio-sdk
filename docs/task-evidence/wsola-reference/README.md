<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WSOLA-REFERENCE — WSOLA reference feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`; qualification `not_qualified`.** This is a bounded, deterministic, task-local feasibility/blocker package for the WSOLA reference row. It is **not** a WSOLA/Sonic/SoundTouch implementation, adapter, runtime, benchmark, or release claim. No provider is registered, no default changes, no public API/ABI/shared build/CI/installed v0 behavior changes, no network/download, no real audio, no listening, no device timing, and no missing result qualifies a candidate.

## Task and boundary

| Field | Value |
| --- | --- |
| Task | `SDK-WSOLA-REFERENCE` |
| Component | `wsola-reference` |
| Mode/profile | `feasibility` / `rate` |
| Base commit | `b50134a300d1daf9cafdded23aa2e511d1cefda9` |
| Branch | `swarm/SDK-WSOLA-REFERENCE` |
| Reviewer | `reviewer-WSOLA-REFERENCE` |
| Worktree | `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-WSOLA-REFERENCE` |
| Write scope | `docs/task-evidence/wsola-reference/` only |

Task deliverable requires a WSOLA reference after elastic output contract and comparison of Sonic, SoundTouch, and fixed-rate baseline. Acceptance requires rate profile evidence and records that a readiness conclusion with exact external blocker is an accepted investigation handoff, not conditional implementation closure.

## Exact blockers

| ID | Gates | Blocker | Required action |
| --- | --- | --- | --- |
| `elastic_output_contract_absent` | RG-01,RG-03,RG-05 | Installed v0 process contract is fixed 160 in/160 out; WSOLA needs variable output/drain semantics. | Reviewed versioned elastic-output/variable-frame adapter contract with deterministic drain/reset/timing before implementation. |
| `isolated_reference_runtime_absent` | RG-02,RG-04,RG-05 | No isolated pinned runtime/build for WSOLA, Sonic, SoundTouch, fixed-rate baseline comparison. | Isolated pinned reproducible runtimes/builds with immutable revisions and exact commands. |
| `rights_and_license_uncleared` | RG-02,RG-07,RG-08 | Compared implementations lack rights/license review for repo boundary/release posture. | Reviewed license/redistribution/product-use terms and required notices per candidate. |
| `matched_rate_evidence_absent` | RG-04,RG-06,RG-08 | No rights-cleared matched rate cohort, outputs, or listening/screen evidence. | Frozen matched rate cohort: 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window, preservation metrics. |

All 8 release gates are blocked. `qualification.candidate_qualified=false`, `qualification.no_missing_result_qualifies_candidate=true`.

## Rate profile (VERIFICATION)

The Rate row is applied item-by-item; no item is satisfied by this blocker package.

| ID | Requirement | Status |
| --- | --- | --- |
| RATE-01 | Source/output mapping for exact runtime. | blocked |
| RATE-02 | Duration/pitch/transient audibility and playback buffering. | blocked |
| RATE-03 | 1x control. | blocked |
| RATE-04 | Rate changes. | blocked |
| RATE-05 | Unfamiliar speech, music, silence. | blocked |
| RATE-06 | Rebuffer, drift and final partial window. | blocked |
| RATE-07 | Pause/filler decisions tied to source timestamps and speech preservation. | blocked |
| RATE-08 | Separate evidence classes; no missing result qualifies. | documented |

## Public v0 boundary (unchanged)

`CONTRACTS.md` pins v0 at 16 kHz, mono `f32`, 160-sample process frames; process input/output counts are exactly 160 and drain semantics are fixed by descriptor max drain calls. This package does not change those contracts. Any WSOLA implementation must wait for a reviewed versioned elastic-output boundary.

## Reproduction

From this package directory, using pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 run.py all --check
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 verify.py
```

From SDK worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 -m pip install -q -r requirements-build.txt
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 scripts/ci.py
python3 -m reuse lint
git diff --check
```

## Source pins (SHA-256)

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- digest-table: artifacts -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `0708aa37cfc97eb32ef07d4e513c1bbee907471d08e61d0814b51bf38cf8c047` | 1450 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `3ed56bf943c01f15ffe01829e93822b436ae85b0cea1d6ce70a9f78d35d3083e` | 19355 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `66405599947739a7bc3efa308b8da8c4f14f835b3071dfa0fbe89b79aa7900fb` | 34072 |
| `report.json` | `8702d9bf50061b77070b2cb825dc869ad8cb2f409a2c74f258b3418f90474f2c` | 24530 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `839bd231a39e61bf1030e04dea5b64f261bf618afbbfc670ecde64ff21c9bda5` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `286b873046e472b483d4c54797982bc04cd69f84980f6f20021f26fc6f4c4304` | 3223 |
| `test_reference.py` | `c767fe2833415f64e23bc22547745c02d087aa0345421435d5229a0966ebd018` | 10094 |
| `verify.py` | `1605d7b3b079ee60e7fbfb292dee729d82581fee4b1951be23685d876a2c893f` | 14090 |
<!-- digest-table: end -->
