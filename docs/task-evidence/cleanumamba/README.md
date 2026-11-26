<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CLEANUMAMBA — source/license/checkpoint and runtime readiness blocker

`audio-sdk/cleanumamba/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **8** |
| Open exact blockers | **6** |
| Profile | Enhancement (`plan/swarm/VERIFICATION.md`) |
| Mode | feasibility |
| Pinned base | `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |

This directory is a bounded, task-local readiness package for **CleanUMamba**
(`component_id=cleanumamba`), the causal waveform U-Net with a Mamba bottleneck
described by `lab-emi/CleanUMamba`. It is **not** an implementation, adapter,
provider, checkpoint bundle, benchmark or release. It records the exact public
upstream identity that can be observed, the license and checkpoint-terms
blocker, and the absent matched evidence. It reproduces only deterministic
metadata, manifest-schema, checkpoint-ledger, geometry and frame controls.
Nothing here may be promoted to a runtime, quality or latency claim.

## Why DEFER

The upstream repository is public and its latest commit is observable, but the
pinned commit contains **no `LICENSE` blob**. The GitHub license field is
`null`, `LICENSE` returns HTTP **404**, and the root tree lists only
`README.md`, `checkpoints/`, `configs/`, `docs/`, `environment.yml` and `src/`.
The README displays an **MIT badge** and the README file-tree diagram lists a
`LICENSE` entry, but neither is a grant of terms. The badge link targets the
same absent file. This is a direct contradiction, not an inferred MIT license.

The checkpoint directories and filenames are observable with byte counts and
exact Git blob SHA-1 identities, but the repository publishes no checkpoint
SHA-256, no checkpoint-specific terms and no immutable retrieval record for the
model files. Two different E8 checkpoints also share the same byte count
(`82,788,482`), so size or filename alone is not identity.

The runtime is absent. Upstream declares Python 3.11, PyTorch 2.2.2, CUDA 11.8,
`mamba-ssm==1.2.2` and `causal-conv1d==1.1.0`; the example loader sets
`device="cuda"` and calls `.cuda()`. No CPU path is verified, no wheel or sdist
is pinned, and no Mamba/PyTorch runtime is installed in this task's evidence
scope. No rights-cleared paired cohort, clean references, matched baseline,
scorer, listening result or device timing exists.

Nothing was cloned, downloaded, copied, imported, built, loaded or executed from
upstream. Supplying the missing license, checkpoint bytes and runtime reopens
the task; absence of a result is the correct outcome.

## Exact upstream observation

| Field | Observed value |
| --- | --- |
| Repository | `https://github.com/lab-emi/CleanUMamba` |
| Default branch | `main` |
| Head commit | `d5810219a534116df1d2e03eaacd517b7ec0a2fa` |
| Commit date | `2025-06-12T06:20:39Z` (unsigned) |
| Root tree | `8e9abac4d880a673d249bbb6de0999566138a1f9` |
| Tree entries | 80 (62 blobs, 18 directories) |
| README | 14,550 bytes, Git blob `7b94c2d32b96523af42dea3845d0c1bb274264c5`, SHA-256 `a2728b41258a1683b7910b1e04a1fa02100f7dc15e25ce59610a44da14bf2db0` |
| License metadata | `null` |
| `LICENSE` HTTP status | `404` |
| README license badge | `MIT` linking to the absent `LICENSE` |
| Checkpoints | 18 `.pkl` files, 261,837,694 bytes total |

The observation was made on **2026-11-26** from public GitHub metadata and raw
text reads at the pinned commit. The repository tree is pinned in
`UPSTREAM_MANIFEST.json`; every file has a byte count and Git blob SHA-1. No
source or checkpoint bytes are stored in this package. The commit is not
cryptographically signed, so the commit hash is the immutable public identity
used here.

Checkpoint family counts are 6 E6, 7 E8 and 5 architecture experiments. The
README's example checkpoint is
`checkpoints/pruned/CleanUMamba-3N-E8_pruned-5M.pkl` (9,744,896 bytes, Git blob
`f6ab36ccf56f6ac411178b36ca222f45ec04825f`), but it is **not selected or
admitted** by this package. No checkpoint was downloaded, so no SHA-256 or
actual bytes were produced.

## Exact blockers

| ID | Missing artifact | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Source license and terms | Add an SPDX-identified `LICENSE` blob at an immutable commit, or supply written permission covering source use, modification, redistribution, product use and derivative output use. The current MIT badge and diagram do not grant this. |
| `BLK-02` | Checkpoint identity and terms | Select one exact checkpoint, supply its caller-computed SHA-256 and byte count, an immutable retrieval record and checkpoint-specific terms. |
| `BLK-03` | Runtime and CPU admission | Pin a Python/PyTorch/Mamba runtime with artifact digests and a CPU-capable path, then load one admitted checkpoint in a bounded isolated-worker smoke with no network. |
| `BLK-04` | Task geometry and streaming contract | Pin the exact model config and checkpoint, chunk/hop, lookahead, state reset, normalization and resampling, and verify the v0 160-sample boundary. |
| `BLK-05` | Matched cohort and scoring | Supply a consented paired clean/noisy cohort with output-use terms, an approved SI-SDR/STOI scorer, matched FastEnhancer/DeepFilterNet3 outputs and a predictive screen or permitted listening. |
| `BLK-06` | Measured profile, timing and review | Measure the Enhancement profile, alignment, state, memory and target-device timing, then complete independent exact-head review and an OFF-by-default opt-in intake. |

Every release gate is `blocked` and `qualifies=false` in `report.json`.

## Task geometry

Installed SDK v0 remains **16 kHz mono `f32`, 160 samples per frame (10 ms)**;
this package changes no public geometry.

Upstream declares 16 kHz mono raw-waveform input, matching the v0 rate and
channel count. It reports **12 ms** lookahead for E6 and **48 ms** for E8, and
the streaming demo uses **4096-sample** chunks. At 16 kHz those are exactly
192 and 768 lookahead samples and a 256 ms chunk. However:

- `4096 mod 160 = 96`, so a demo chunk is **25.6** v0 frames;
- `192 mod 160 = 32` and `768 mod 160 = 128`, so neither declared lookahead is
  v0-frame aligned;
- the caller must therefore re-chunk or rebase, and the exact state/alignment
  contract is unverified.

The lookahead values are **source-reported declarations, not measurements**.
No content delay, availability, callback deadline or device timing was measured.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` is applied item by item. Every item is blocked:

| Requirement | State | Evidence |
| --- | --- | --- |
| Identity/noisy control | blocked | No runtime and no rendered output |
| Established task-matched baseline | blocked | FastEnhancer/DeepFilterNet3 named only; no matched output |
| Paired SI-SDR and STOI with clean references | blocked | No cohort, clean references or approved scorer |
| Clean-speech preservation | blocked | No clean reference or listening |
| Peaks and invalid outputs | blocked | No output waveform |
| Unpaired predictive screen or authorized listening | blocked | No screen and no permission |
| Alignment | blocked | Declared lookahead arithmetic only |
| State and memory | blocked | No streaming session or reset schedule |
| Measured content/availability timing | blocked | No device clock or paced workload |

The source-reported DNS no-reverb values (PESQ-WB 2.42, PESQ-NB 2.95, STOI
95.1% at 442K parameters / 468M MACs) are retained as **upstream claims**, not
remeasured here and never pooled with any local result.

## Caller-supplied asset boundary

`reference.py` implements a fail-closed **metadata** validator for a hypothetical
caller-authored manifest. It requires the exact repository, commit and tree,
one of the 18 ledger checkpoint paths, its byte count and Git blob SHA-1, a
caller-supplied 64-hex checkpoint SHA-256, 16 kHz mono, caller attestation and a
license-evidence block. It never opens, hashes or executes an asset.

The synthetic schema control is intentionally **not admitted**: the control
checkpoint digest is a hash of a synthetic note, `caller_attestation=false` and
license status is `absent`. Schema-valid metadata is not qualification.

## Deterministic controls

- `manifest_control`: 30 rejection cases (missing/unknown fields, wrong
  commit/tree/path/size/blob/digest, 48 kHz or stereo, malformed license fields,
  duplicate JSON keys, malformed JSON, non-object roots) all reject with exact
  codes and no state advance; one schema-valid control is accepted as metadata
  only and remains unadmitted.
- `checkpoint_ledger_control`: recomputes 18 checkpoint rows, 6 E6 / 7 E8 / 5
  experiments, 261,837,694 bytes, zero published SHA-256 values, no license blob
  and the duplicate-size E8 pair with distinct Git blobs.
- `geometry_control`: exact 16 kHz millisecond/sample arithmetic and the
  non-alignment facts above.
- `frame_control`: accepts exactly 160 finite integer milli-samples in
  `[-1000, 1000]` and rejects wrong length, boolean, string, float, nonfinite
  and out-of-range payloads.

No audio is synthesized, read or played. No model is run.

## Reproduce

From this directory with **Python 3.12.16** and the standard library only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py all` regenerates `contract.json`, `report.json`, `report.json.sha256`,
`SOURCES.sha256` and the README artifact digest table three times and requires
byte-identical results. `verify.py` re-checks the Enhancement profile phrases,
all live source/boundary/sibling pins, strict canonical JSON, the report digest
sidecar, the README digest tables, the observed upstream manifest, all controls,
eight blocked gates, six open blockers, licensing/REUSE and task-local git
scope, then performs three cold-start regenerations. No network, runtime,
checkpoint, audio, device or scorer is used.

Repository-level checks used for this task:

```sh
python3 scripts/ci.py
python3 -m reuse lint
git diff --check
```

## Files

| File | Role |
| --- | --- |
| `reference.py` | Strict JSON, pins, upstream ledger, controls, contract/report builders, README digest validation. |
| `run.py` | Three-repeat canonical regeneration. |
| `contract.json` | Canonical task contract and pins. |
| `report.json` | Canonical machine-readable DEFER report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `UPSTREAM_MANIFEST.json` | Observed upstream commit/tree, file byte counts and Git blob SHA-1 values; no upstream bytes. |
| `SOURCES.sha256` | SHA-256 pins for source, boundary, sibling and task-local files. |
| `test_reference.py` | Standard-library test suite. |
| `verify.py` | Read-only package verifier. |
| `*.license` | REUSE/SPDX sidecars for JSON artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/agent-cleanumamba-eval/REPORT.md` | `381029c5e50aff2916b6eb15b021f5fe923f7807ba71dab7dbebab65896b9cc2` |
| `source:research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md` | `c00e26847c119928f068cb5da00ba88106a2d977b67bf8b325ec27093eca8f4e` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Upstream observation fields

These fields are checked against `UPSTREAM_MANIFEST.json` and the constants in
`reference.py`; they are not live network calls.

<!-- digest-table: upstream -->
| Field | Value |
| --- | --- |
| `commit` | `d5810219a534116df1d2e03eaacd517b7ec0a2fa` |
| `tree_sha1` | `8e9abac4d880a673d249bbb6de0999566138a1f9` |
| `readme_sha256` | `a2728b41258a1683b7910b1e04a1fa02100f7dc15e25ce59610a44da14bf2db0` |
| `readme_git_blob_sha1` | `7b94c2d32b96523af42dea3845d0c1bb274264c5` |
| `license_metadata_field` | `absent` |
| `license_path_http_status` | `404` |
| `checkpoint_count` | `18` |
| `checkpoint_bytes` | `261837694` |
| `published_checkpoint_sha256` | `0` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- digest-table: artifacts -->
| File | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `UPSTREAM_MANIFEST.json` | `665058d2db5d644406df9fce81e0d5bb74da54c0f6fe3b182686938a8309cc89` | 8650 |
| `UPSTREAM_MANIFEST.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `72c2391b18aa0e0016356906ad2bff536a13582bd28b75023f8f94dd28f4f06d` | 35249 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `5dd58f97ea20d8bf5baf5dda71e8ca1cd2eebfb36cd56cd14414c6e574d27c97` | 64535 |
| `report.json` | `bbfb69a1a7d964639ab0056e3ac2e3dd735973e32029f26d6ce12f2a0060552e` | 47388 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `2e02037c13b8db05cdcda446cf7a625fac0d1c2478bee01b7b1c8ccbe9785af1` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `ec1cce44954d8eda95f5f313f4e5838d7a70c8493e4639c99666db733366082c` | 2145 |
| `test_reference.py` | `9c341cffefc04e8e96c4f75a2378d00198ffd7ad78fed37df7fab664098b3b7e` | 13741 |
| `verify.py` | `59a5dadff2d458011351657b79e373c43f43504000b8ecd4d65873652e18bc67` | 26816 |
<!-- digest-table: end -->

## Non-claims

- No result in this package is a qualification, benchmark or release.
- No CleanUMamba source, checkpoint, runtime or audio was copied, downloaded,
  imported, built, loaded or executed.
- The MIT badge and diagram are not a license grant; no LICENSE blob exists at
  the pinned commit and the LICENSE path returns 404.
- Git blob SHA-1 metadata is not a checkpoint SHA-256 and does not grant rights.
- No SI-SDR, STOI, PESQ, preservation, peak, invalid-output, state, memory,
  listening or timing result was produced.
- No provider, descriptor, registry, default, installed-v0 behaviour, public
  API/ABI, shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
