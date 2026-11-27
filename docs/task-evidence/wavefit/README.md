<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAVEFIT — WaveFit research-control blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory is
task-local evidence for `SDK-WAVEFIT` (`component=wavefit`,
`mode=research-control`, Enhancement profile). It is **not** a WaveFit
implementation and **not** a qualification result. No WaveFit source import,
weight load, runtime, audio, corpus, listening, device timing, benchmark, or
release claim is present. **No result here qualifies WaveFit.**

## Proceed / defer decision

**DEFER.** The pinned candidate matrix classifies WaveFit as **out of scope**
for the PLC claim: "Primary source identifies a neural vocoder, not a
standalone packet-loss concealment system" (`research/voice-enhancement-20261101/candidate_matrix.csv`).
No exact WaveFit source revision, license/notice bundle, immutable weights,
pinned runtime, reviewed output/weight terms, or rights-cleared evaluation
cohort are present. The comparison cannot be retained or reproduced as a
qualified PLC/enhancement processor. Before any processor exposure, this row
needs exact source+weights+runtime identity, a reviewed rights boundary, a
task-matched packet-loss/enhancement protocol with conventional controls, and
an explicit OFF-by-default separate intake.

## Scope

- Task-local only: `docs/task-evidence/wavefit/`.
- Stable linked-row identity gating only; the mutable board file is not hashed.
- Deterministic stdlib-only regeneration, strict JSON, exact pins, 3x
  byte-identical cold-start regen, and adverse/missing/invalid/nonfinite
  rejection coverage.
- No provider registration, installed-v0/ABI/registry/default/shared-build/CI
  change, real corpus/weights/runtime, listening, device timing, benchmark, or
  release claim.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3 verify.py
```

Cold-start regeneration repeats 3x and must be byte-identical. Network and
runtime are not required.

## Pinned source digests

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-denoise/REPORT.md` | `eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` |
<!-- digest-table: source:end -->

## Pinned boundary digests

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
<!-- digest-table: boundary:end -->

## Task-local artifact digests

<!-- digest-table: artifacts -->
| Path | SHA-256 |
| --- | --- |
| `docs/task-evidence/wavefit/contract.json` | `1d46a54b5bb65bd7fdcfeaa989b0d605b2abddd51d0c7cd6e990ccc3dbab13f4` |
| `docs/task-evidence/wavefit/contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/wavefit/LICENSES.md` | `ff7d99c40ae7ab7b1ede66791c1f9bf1cd0e5c0ec42a8be2caaf946dc78e3086` |
| `docs/task-evidence/wavefit/reference.py` | `631a121adbe14c6b2aa10464fd2de85eacbcbb1533a46bb498c81542418f4491` |
| `docs/task-evidence/wavefit/report.json` | `8d79bed2914fec248b9fb00ed256a81bc79ac030c7a2ce7fe4c5e4ce43973356` |
| `docs/task-evidence/wavefit/report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/wavefit/report.json.sha256` | `d5c9f20e0bc9e1335270f388a19a5b70f8bf0ab297d75d14ed201bfbc46d08ce` |
| `docs/task-evidence/wavefit/report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/wavefit/run.py` | `c2d5b3a0ee64d6e7b537062b4eceb2c4953d552ad78d0455d41141a4b880ddcc` |
| `docs/task-evidence/wavefit/SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/wavefit/test_reference.py` | `0f695ce3c9c131a5c111134645805a3bb4689fea368f0198c4329307f3c4766b` |
| `docs/task-evidence/wavefit/verify.py` | `2c4d0cc840190d9b727b6f024a2a6da8e99d89955a1b045ea67c900f8445f3e5` |
<!-- digest-table: artifacts:end -->
