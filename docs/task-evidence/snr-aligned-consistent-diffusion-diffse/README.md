<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DiffSE - SNR-Aligned Consistent Diffusion readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE`
(`component_id=snr-aligned-consistent-diffusion-diffse`, mode `feasibility`,
`verification_profile: enhancement`). It is **not** a DiffSE implementation,
adapter or reproduction. No upstream source checkout, diffusion checkpoint,
input-SNR estimator, weight byte, sampler configuration, runtime, corpus,
recording, enhanced waveform, listening result, device timing, benchmark or
release claim is present. **No result here qualifies DiffSE.**

Pinned base: `f93d25f3d455a4278030d1bf0a3338dc6f8b95fe`.
Branch: `swarm/SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE`.
Owner: `agent-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE`.
Reviewer: `reviewer-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE`.

## Exact external blocker

`research/noise_suppression_candidate_census.md`, line 36, records the pinned
row: SNR-conditioned, one-step consistency diffusion enhancement. The row says
the official 2025 paper/repository report M4-M6 and baseline checkpoints, with
a source-reported `+0.12 PESQ` mean over the SE-Bridge baseline on
VoiceBank-DEMAND. It also says the repository prescribes Python 3.8 and exposes
Drive-folder checkpoints. The same row states that the repository's own licence
text was not verified, checkpoint terms, immutable artifact identity/hash and
CPU feasibility are unresolved, input-SNR estimation is required outside
oracle-SNR conditions, and the upstream SGMSE MIT license must not be treated
as covering this fork or weights.

`plan/INVENTORY.md` line 208 links the same candidate to this task.
`plan/swarm/VERIFICATION.md` line 16 defines the Enhancement profile:
identity/noisy control, an established task-matched baseline, paired SI-SDR and
STOI where permitted clean references exist, clean-speech preservation, peaks
and invalid outputs, a separately labeled predictive screen or authorized
listening, and alignment, state, memory and measured content/availability
timing for the exact runtime. `audio-sdk/CONTRACTS.md` line 15 defines the
caller-supplied external asset boundary: descriptor-declared ID, size and
SHA-256 must match caller bytes in descriptor order, and embedded assets are
not supported by contract 0.1.

The exact blocker is therefore the combination of:

1. **No verified fork source identity or licence text.** The repository and
   paper URLs are named, but no immutable commit, `LICENSE` text, notice,
   model card or per-file digest is staged. The upstream SGMSE MIT license is
   not a substitute: no substitution is permitted.
2. **No exact checkpoint identity.** Baseline checkpoints are reported through
   Drive folders, but no file name, revision, byte count, SHA-256, tensor
   schema or checkpoint-specific terms is recorded. A folder link is not an
   immutable artifact.
3. **No input-SNR estimator.** The census requires input-SNR estimation
   outside oracle-SNR conditions, but no estimator checkpoint, revision, byte
   count, SHA-256, feature configuration or separate terms is staged.
4. **No locked runtime or CPU feasibility result.** The repository prescribes
   Python 3.8 while this evidence interpreter is pinned at 3.12.16. No locked
   framework package set, wheel digest, offline loader, deterministic one-step
   sampler, CPU feasibility measurement or device timing exists.
5. **No rights bundle.** Fork licence, checkpoint terms, SE-Bridge baseline
   terms, VoiceBank-DEMAND and training-data provenance, clean-reference
   permission and output-use rights are unresolved.
6. **No frozen offline geometry or matched result.** The evidence reports
   one-step consistency diffusion but records no sample rate, STFT window,
   hop, sampler schedule, SNR conditioning layout, padding, output length,
   normalization, 160-sample SDK mapping, rights-cleared cohort, paired score,
   clean-speech preservation, peak, invalid-output or timing result.
7. **No opt-in intake.** No provider, descriptor, default selection, ABI,
   shared build, CI, board or handoff change is made.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from adjacent NASE, SE-Bridge, DNS2020, MP-SENet, ConvFSENet, GTCRN,
DeepFilterNet3, ROSE-CD or other survey evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The official `yh-jun/SNR-Aligned_diffSE` fork at an immutable 40-hex commit with reviewed licence text, notice, per-file SHA-256 and a map from the model, one-step sampler, SNR estimator and metric scripts to source files. |
| `BLK-02` | The exact baseline DiffSE checkpoint with file name, immutable revision, byte count, SHA-256, tensor schema, inference configuration and checkpoint-specific terms. |
| `BLK-03` | The exact input-SNR estimator used outside oracle-SNR conditions, with immutable identity, feature configuration and separate terms. |
| `BLK-04` | A locked offline runtime reconciling Python 3.8 with the pinned evidence interpreter, with package hashes, CPU/MPS device, deterministic one-step sampler and CPU feasibility evidence. |
| `BLK-05` | Reviewed fork, checkpoint, estimator, SE-Bridge baseline, VoiceBank-DEMAND and training-data terms; corpus and clean-reference permission; output use, redistribution and attribution. |
| `BLK-06` | The frozen offline diffusion contract plus a rights-cleared 16 kHz mono cohort, paired clean references, strata, identity/noisy controls, SE-Bridge baseline and independent Enhancement, listening, timing and preservation results. |

**Reopen condition.** A caller supplies the exact fork and reviewed licence,
the exact baseline checkpoint and input-SNR estimator with verified identity
and terms, an isolated hash-pinned runtime with a deterministic one-step
sampler on a recorded CPU platform, the frozen offline geometry mapped to 16
kHz mono float32 160-sample frames, a rights-cleared 16 kHz matched cohort, a
deterministically reproduced Enhancement result set with separate quality,
preservation and timing evidence, and an opt-in OFF-by-default provider intake
with independent exact-head review. Until then `DEFER` remains in force before
`opt_in_adapter_exposure`.

## Recorded upstream identity

None of the following is a local asset. No byte is present, opened, hashed or
executed here, so every unresolved identity field remains null and cannot
qualify the candidate.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/yh-jun/SNR-Aligned_diffSE` | absent |
| Paper | `https://hi.snu.ac.kr/wp-content/uploads/sites/103/2025/09/jun25_interspeech.pdf` | not read locally |
| Source licence | fork licence text not verified; SGMSE MIT not substituted | unresolved |
| Source commit | not recorded | absent |
| Model revision | not recorded | absent |
| Checkpoint file | not recorded; Drive folder only | absent |
| Checkpoint bytes | not recorded | absent |
| Checkpoint SHA-256 | not recorded | absent |
| Input-SNR estimator | required outside oracle-SNR conditions | identity absent |
| Runtime | Python 3.8 prescribed | absent |
| Reported PESQ delta | `+0.12` mean over SE-Bridge on VoiceBank-DEMAND | source-reported only |
| Local PESQ / STOI | none | not measured here |

The `+0.12 PESQ` line and M4-M6 descriptions are source-reported provenance.
They are not local results, benchmarks or qualification evidence and must not
be compared with project DNS2020 results.

## Geometry and caller-supplied asset boundary

The installed SDK v0 geometry is preserved: 16000 Hz, one channel, float32
(descriptor label `f32`) and 160-sample frames. No DiffSE mapping is present,
and no candidate rate or frame geometry is verified. The caller-supplied asset
declaration is validated as metadata only: exact fields, absolute-free file
names, SHA-256 shapes, byte counts, Python 3.8 runtime shape, one-step sampler
shape, 16000/1/float32/160 geometry, controls and rights are checked before the
declaration fails closed with `DIFFSE_EXACT_ASSET_IDENTITY_UNPINNED`. No asset
bytes are opened, loaded or executed. The accepted schema control is synthetic
and cannot qualify the candidate.

## Release gates

`RG-01` through `RG-08` are all `blocked` and `qualifies=false`: exact source;
exact checkpoint and estimator; locked runtime; rights; frozen geometry;
Enhancement result set; independent listening/screen and timing; opt-in intake
and release approval. No missing, blocked or synthetic result qualifies the
candidate.

## Reproduction

Run from this directory with pinned CPython 3.12.16 and bytecode writes off:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

From the SDK worktree root, repository checks are:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
python3 -m reuse lint
git diff --check
```

`verify.py` checks the newest merge-base of `origin/main` and `main`, fails
closed with `scope_base_unavailable` when no ordered base exists, and reports
`base_out_of_scope_change` for any committed path outside this task directory.
Three scope regression tests cover newest-base sibling selection, an
out-of-scope branch edit and a missing base.

## Source pins

<!-- DIGEST_TABLE_SOURCE_START -->
| Source pin | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
<!-- DIGEST_TABLE_SOURCE_END -->

## Boundary pins

<!-- DIGEST_TABLE_BOUNDARY_START -->
| Boundary pin | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- DIGEST_TABLE_BOUNDARY_END -->

## Generated artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `da4133619c326bd1c1c7bef584c5db9d18297588192f8b67ef661e9b0e438345` | 1904 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `07f16352d2e16f0f4a187365c7c3be6c1c2d63e2a8d07f8292c141c5d56f7ca0` | 23885 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `8936b5c67b8b0f2809edd8a87c4780cabcbef9a25e7a01ce670ec2c0f26d5273` | 78622 |
| `report.json` | `2a6ac5d81718eec48ee2755f240a6fb3896cc78c68fd0b380d8522a62baef87a` | 35687 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `3353681691029460f55d8cb61ae1474efb8c21e2e4a7b256b0013a466996edc2` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `0358eb9347fcf7b8f320b2b9f05d6c2a67e1315a5eba87dd58b1ac9ec1db1bbf` | 4448 |
| `test_reference.py` | `2300011a0e41601aecc279262fcfb6430017c4688b931ec4aa47d87d2aabd923` | 17989 |
| `verify.py` | `b210dc5565e20d97e55f151f5a837f385188ae873fcdb747802e7e0d35fb3b39` | 23500 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
