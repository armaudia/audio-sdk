<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPIKING-FULLSUBNET - Spiking-FullSubNet readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`SDK-SPIKING-FULLSUBNET` (`component_id=spiking-fullsubnet`, mode `feasibility`,
`verification_profile: enhancement`). It is **not** a Spiking-FullSubNet
implementation, adapter, reproduction, benchmark or release claim. No upstream
source checkout, checkpoint, SNN/neuromorphic runtime, weight byte, corpus,
recording, enhanced waveform, listening result, device-timing result, power
measurement or qualified result is present. **No result here qualifies
Spiking-FullSubNet.**

Pinned base: `4c0f5464eeddff2204b527e8bc4ad09c41b2a657`.
Branch: `swarm/SDK-SPIKING-FULLSUBNET`.
Owner: `agent-SPIKING-FULLSUBNET`.
Reviewer: `reviewer-SPIKING-FULLSUBNET`.

## Exact external blocker

`research/noise_suppression_candidate_census.md` line 35 records
Spiking-FullSubNet as a spiking-neural-network FullSubNet for low-power
real-time denoising. It reports an official MIT implementation, an Intel
N-DNS Challenge Track 1 winning solution claim, and pretrained models plus a
validation set. It also requires confirming the released checkpoint input
domain, code revision, inference contract and licensing of its weights before
evaluation, and requires supported hardware before any power claim.

`plan/INVENTORY.md` line 213 and `plan/INVENTORY.json` record the same
candidate with task `SDK-SPIKING-FULLSUBNET`. `plan/swarm/VERIFICATION.md`
defines the Enhancement profile: identity/noisy control, an established
task-matched baseline, paired SI-SDR and STOI where permitted clean references
exist, clean-speech preservation, peaks and invalid outputs, a separately
labeled predictive screen or authorized listening, and alignment, state,
memory and measured content/availability timing for the exact runtime.
`audio-sdk/CONTRACTS.md` defines the caller-supplied external asset boundary:
descriptor-declared ID, size and SHA-256 must match caller bytes in descriptor
order; embedded assets are not supported by contract 0.1.

The exact blocker is therefore:

1. **No verified exact source identity.** No immutable 40-hex commit, reviewed
   MIT licence text bytes, per-file SHA-256 manifest or local source checkout
   is present. Repository URL is source-reported context only.
2. **No exact released checkpoint/weight identity.** No checkpoint filename,
   byte count, SHA-256, config mapping, input domain, inference contract,
   released-weight terms or local bytes are present. Not downloaded.
3. **No locked runtime or CPU feasibility.** No locked interpreter/package/SNN
   runtime, deterministic offline load, host profile, CPU feasibility, device
   timing or supported-hardware power evidence is present.
4. **No rights/provenance bundle.** Source MIT status is reported but not
   locally reviewed as bytes; pretrained-weight terms, Intel N-DNS/validation
   set provenance, training-data, corpus, clean-reference, output-use and
   redistribution rights are unresolved.
5. **No frozen geometry/cohort/mapping.** No verified 16 kHz mono input
   domain, 160-sample SDK v0 mapping, state/reset contract, or rights-cleared
   paired cohort with controls is present.
6. **No Enhancement evidence.** No SI-SDR/STOI, clean-speech preservation,
   peaks/invalid outputs, listening/predictive screen, alignment, content
   delay, state, memory, availability timing, resource or uncertainty result
   exists.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Exact `haoxiangsnr/spiking-fullsubnet` source at immutable 40-hex commit with reviewed MIT licence text, NOTICE/README provenance and per-file SHA-256 manifest. |
| `BLK-02` | Exact released checkpoint(s) with filename, byte count, SHA-256, config/input-domain mapping and separately reviewed weight terms. Not downloaded. |
| `BLK-03` | Locked offline runtime with exact package versions, lock SHA-256, deterministic load and recorded CPU feasibility; no power claim without supported hardware. |
| `BLK-04` | Reviewed code/weight/data rights, Intel N-DNS/validation-set provenance, corpus rights, clean-reference permission, output use and redistribution. |
| `BLK-05` | Frozen 16 kHz mono geometry, 160-sample SDK mapping, state/reset contract and rights-cleared paired cohort with controls. |
| `BLK-06` | Independent Enhancement, listening/predictive screen and target-runtime timing/memory/resource evidence on the exact pinned assets. |

**Reopen condition.** A caller supplies the exact source and reviewed licence
bytes, exact released checkpoint(s) with verified identity and terms, a locked
offline deterministic runtime with CPU feasibility on a recorded target, frozen
16 kHz mono/160-sample geometry and rights-cleared cohort, and independent
Enhancement + timing evidence with exact-head review. Until then `DEFER`
remains in force before `opt_in_adapter_exposure`.

## Recorded upstream identity

None of the following is a local asset. No byte is present, opened, hashed or
executed here; unresolved identity fields remain unresolved and cannot qualify.

| Property | Recorded value | Local status |
| --- | --- | --- |
| Source repository | `https://github.com/haoxiangsnr/spiking-fullsubnet` | absent |
| Source licence | MIT reported by census | not locally reviewed as bytes |
| Source commit | not recorded | absent |
| Released checkpoint | pretrained models reported | absent, not downloaded |
| Checkpoint bytes/SHA-256 | not recorded | absent |
| Input domain/inference contract | not verified | unresolved |
| Runtime | not pinned | absent |
| Reported claim | Intel N-DNS Challenge Track 1 winning solution | source-reported only |

## Geometry and caller-supplied asset boundary

The installed SDK v0 geometry is preserved: 16000 Hz, one channel, float32
(descriptor label `f32`) and 160-sample frames. No Spiking-FullSubNet mapping
is present. The caller-supplied asset declaration is validated as metadata
only: exact fields, safe basenames, SHA-256 shapes, byte counts, 16000/1/
float32/160 geometry, controls and rights are checked before the declaration
fails closed. No asset bytes are opened, loaded or executed. The accepted
schema control is synthetic and cannot qualify the candidate.

## Release gates

`RG-01` through `RG-08` are all `blocked` and `qualifies=false`. No missing,
blocked or synthetic result qualifies the candidate.

## Reproduction

Run from this directory with pinned CPython 3.12.16 and bytecode writes off:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

Repository checks from the SDK worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3.12 scripts/ci.py --output build/ci
python3 -m reuse lint
git diff --check
```

`verify.py` checks the newest merge-base of `origin/main` and `main`, fails
closed with `scope_base_unavailable` when no ordered base exists, and reports
`base_out_of_scope_change` for any committed path outside this task directory.

## Source pins

<!-- DIGEST_TABLE_SOURCE_START -->
| Path | SHA-256 |
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
| Path | SHA-256 |
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
| Path | SHA-256 |
| --- | --- |
| `LICENSES.md` | `45ebf52af525142a74c552d011ecd3073262978b1952da8a443b1bb22dc868f9` |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `contract.json` | `6d8e5b4360af8c5cc7f780ddc557db2c5b237000ba23b63dedd42db70e007220` |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `reference.py` | `62e25023314dcbb8b361d709827c2dd32a5afbf075e5dc2cc5c91c59ffcbdd01` |
| `report.json` | `bee59e9dd3a2cd0a890c63ea4aabd4ee6c4a0f43ff9b90d23ff841d0248a4f87` |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `report.json.sha256` | `ce94213845d0053e43d9eac073e2129fe68250e506761cc21fd316158bf82fc8` |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `run.py` | `83d4e0d7897a141f52e4f3a108f1e303fdc9250a140d01bd24f9292801081283` |
| `test_reference.py` | `118c8f1ef6929f4b024fe16cb6f92fe9cf5956de8c6627ec0faf2e19e988904e` |
| `verify.py` | `7384cf0782dd4a7c116c2f8ef06baeb2f8caffc423c6d0c49dad5d41fc492e88` |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
