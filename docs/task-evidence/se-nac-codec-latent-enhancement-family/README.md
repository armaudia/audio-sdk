<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY — SE-NAC readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`se-nac-codec-latent-enhancement-family` (mode `feasibility`, verification
profile `enhancement`). It is **not** a SE-NAC adapter, codec integration,
license grant or benchmark. No source checkout, checkpoint byte, codec runtime,
dependency lock, reviewed terms, rights-cleared cohort, enhanced waveform,
listening result, device timing, benchmark or release claim is present.
**No result here qualifies the SE-NAC codec-latent enhancement family.**

Claim base: audio-sdk `a51e49f718500ec9e81242cf2816f0b576333d00`; branch
`swarm/SDK-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY`. Owner:
`agent-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY`; reviewer:
`reviewer-SE-NAC-CODEC-LATENT-ENHANCEMENT-FAMILY`. Depends on `SDK-FND-AUDIT`,
`SDK-FND-EVIDENCE` and `SDK-FND-PROVIDER`. Write scope is task-local only:
`docs/task-evidence/se-nac-codec-latent-enhancement-family/`.

## Exact external blocker

The census records one row at line 67 of
`research/noise_suppression_candidate_census.md`:

> **SE-NAC codec-latent enhancement family** | Neural audio-codec representation
> speech enhancement; discrete/continuous and autoregressive/non-autoregressive
> variants | Official model card publishes multiple pretrained checkpoints and
> cites ICASSP 2026; task data is LibriMix. Includes a STFT-NAR control variant.
> | Valuable offline architecture-family comparison, but codec token generation
> may be costly and output fidelity is a concern. Pin corresponding code and
> weights, validate license/data lineage, and assess noise-only behavior,
> WER/content preservation and runtime before selection.

The pinned candidate-store snapshot adds: `code: available`, `weights:
located_unverified`, `benchmark_state: not_run`, `eligibility.state: blocked`,
`sample_rate_hz: null`, and variants `D-AR`, `D-NAR`, `D-NAR*`, `C-AR`,
`C-NAR`, `C-FT`, `D-FT`, `STFT-NAR`. The blocker reason is that upstream code
linkage, artifact hashes/terms, codec dependencies and local isolated inference
costs are unverified, and candidate inference is blocked by an unavailable
enforced worker sandbox.

The exact blocker is the combination of:

1. **No locally pinned source identity.** `code: available` is a store fact,
   not a source checkout. No commit, tree hash, immutable revision, file list
   or source terms are present.
2. **No reviewed checkpoint identity or terms.** Eight variants are reported,
   but weights are `located_unverified`. No revision, byte count, SHA-256,
   per-variant terms or data-lineage record exists locally.
3. **No locked codec runtime or enforced worker sandbox.** The store records
   codec dependencies and isolated inference costs as unverified, and
   candidate inference is blocked. No dependency lock or sandbox proof exists.
4. **No rate/tokenizer/frame contract.** The store records
   `sample_rate_hz: null`; the installed v0 path is 16 kHz mono float32 with
   160-sample frames. No codec tokenizer revision, resampler, chunk/hop, reset
   or tail contract is supplied.
5. **No rights-cleared matched cohort or result.** There is no 16 kHz mono
   held-out cohort, identity/noisy control, STFT-NAR or task-matched baseline,
   frozen output, paired score, noise-only behavior, WER/content-preservation
   record or paced timing evidence.
6. **No adapter intake or release decision.** No opt-in descriptor, registry
   review, default decision or public-benchmark approval exists.

| Blocker | State | Requirement to reopen |
| --- | --- | --- |
| `BLK-01` | absent | Immutable upstream source checkout with commit, tree hash and reviewed code terms. |
| `BLK-02` | unreviewed | Reviewed source/checkpoint terms, training-data lineage, deployment terms and output-use rights. |
| `BLK-03` | blocked | Locked codec dependencies and an enforced isolated worker sandbox. |
| `BLK-04` | absent | Exact checkpoint variant, revision, byte count and SHA-256. |
| `BLK-05` | absent | Frozen model-rate/codec-tokenizer, mono, float32, 160-sample mapping with resampler, chunk/hop and reset/tail policy. |
| `BLK-06` | absent | Rights-cleared 16 kHz mono cohort with controls, baselines, frozen outputs and paired scores. |
| `BLK-07` | absent | Codec-cost, alignment, state, memory and paced content/availability timing. |
| `BLK-08` | not_started | Opt-in adapter intake, descriptor/registry review, default decision and release approval. |

**Reopen condition.** A caller supplies the exact source revision and checkpoint
with verified identity, reviewed terms and data lineage, a locked codec runtime
in an enforced worker sandbox, the frozen model-rate/tokenizer-to-16 kHz mono
float32 160-sample contract, a rights-cleared matched cohort, a deterministic
reproduced Enhancement result set with separate quality and timing evidence,
and an opt-in OFF-by-default provider intake with independent exact-head
review. Until then this task stays `DEFER`.

## Recorded upstream identity (source-reported, not locally verified)

| Property | Recorded value | Local status |
| --- | --- | --- |
| Model card | `https://huggingface.co/SofieneK/SE-NAC` | reported only |
| Paper | `https://arxiv.org/abs/2510.26299` | reported only |
| Checkpoint variants | `D-AR`, `D-NAR`, `D-NAR*`, `C-AR`, `C-NAR`, `C-FT`, `D-FT`, `STFT-NAR` | reported only |
| Task data | LibriMix | reported only |
| Sample rate | `null` | not recorded; never defaulted |
| Code state | `available` | reported only; no local checkout |
| Weights | `located_unverified` | reported only; no local byte |
| Benchmark state | `not_run` | reported only |
| Eligibility | `blocked` | reported only |
| Source-reported score | none | not reproduced, pooled or qualified |

The candidate matrix at
`research/voice-enhancement-20261101/candidate_matrix.csv` has **no SE-NAC
row**. No score is attached to this family by any pinned evidence file. Source
and census claims remain provenance only and are never promoted to local
results.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Offline single-channel codec-latent speech enhancement | No execution |
| Model sample rate | `null` | not recorded; not defaulted |
| Codec tokenizer / tokens | not recorded | unverified |
| Variants | eight discrete/continuous and AR/NAR checkpoints plus STFT-NAR | reported only |
| Chunk / frame / hop / resampler | not recorded | unverified |
| Model-rate-to-v0 mapping | not recorded | unverified |
| Reset / tail / pacing | not recorded | unverified |
| SDK v0 installed geometry | 16 kHz, mono, float32, 160 samples/frame | preserved; no model mapping |

The public v0 mono path cannot be assumed compatible with a codec-latent model
whose sample rate and tokenizer are unreported. No descriptor, provider,
registry, default, ABI, shared build or CI mapping is added.

## What this package verifies

1. **Absence evidence.** 20 fixed workspace, SDK-worktree and home-cache
   probes are checked without a recursive walk. All are absent. The report
   builder and verifier fail if any later appears, so a stale absence claim
   cannot ship.
2. **Recorded-identity discipline.** Every source fact is marked
   `source_reported_not_locally_verified`, `locally_verified=false`,
   `admitted_as_result=false` and `qualifies=false`. The eight required
   artifacts keep `sha256`, `bytes` and `revision` null; no local identity is
   invented.
3. **Asset-register absence.** The pinned asset register is parsed strictly;
   it has no SE-NAC entry. No identity is inferred from it.
4. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
5. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, checkpoint, runtime, geometry, input, control and
   rights fields. Unknown or missing fields, duplicate keys, nonfinite values,
   floats, unsafe paths, unresolved text, wrong interpreter, online runtime,
   missing worker sandbox, stereo or non-16 kHz input geometry, an invented
   model rate, an unpinned rate/tokenizer contract, unconsented input, false
   controls and false rights are rejected. One synthetic schema control is
   accepted to prove the validator is not blanket-rejecting; it is synthetic,
   `qualifies=false`, and is not evidence.
7. **Enhancement profile accounting.** Every Enhancement requirement is
   recorded as blocked or documented; no missing result is promoted and no
   source-reported metric is admitted.
8. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/se-nac-codec-latent-enhancement-family/` as
   `base_out_of_scope_change`. Regression tests cover sibling merges, an
   out-of-scope branch edit and a missing base ref.

## Enhancement profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Identity/noisy control and task-matched baseline | blocked | No control, STFT-NAR control, baseline or pinned runtime output. |
| Paired SI-SDR and STOI | blocked | No rights-cleared paired 16 kHz cohort or score. |
| Clean-speech preservation, peaks and invalid outputs | blocked | No preservation, peak, clipping or nonfinite record. |
| Separately labelled predictive screen or authorized listening | blocked | No screen, listener or permission. |
| Alignment, state, memory and timing | blocked | No runtime, tokenizer, codec cost, resampler or paced timing record. |
| Geometry, rate/format/frame and tokenizer contract | blocked | `sample_rate_hz: null`; no frozen contract. |
| Quiet/active, idle-noise and onset/offset strata | blocked | No corpus or stratum definition. |
| Evidence-class separation | documented | Census/store facts are labelled source-reported; no result of any class is promoted. |

## Matched-evidence boundary

The other codec/candidate packages (`dac-se1`, `llase-g1`, `cisco-stupase`,
`dblm-se-1b`, `survey-rst-03`) and historical evidence are separate components
with their own assets, terms, geometry and blockers. Their fixtures,
checkpoints, scores, timings, state models and rights records are not
inherited. No SE-NAC output exists here, so no comparison is made.

## Reproduction

The canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, the report sidecar, the
README digest tables and `SOURCES.sha256` three times and requires
byte-identical output. `verify.py` is read-only and writes only to a temporary
directory. Repository checks are the installed-package `python scripts/ci.py`,
`python -m reuse lint` and `git diff --check`.

## Source pins

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/store/snapshots/e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380cca1d5dc6537.jsonl` | `e44801b2ef3b84d984e3119218e201adc2083884ac0594a6a380cca1d5dc6537` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins

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

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `631e01a5842101d095f077f9a99204881fa1c97380287e0cab5aad99799a08c7` | 2084 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `34faabc0560acea5eb1aea02a50e2bad9933cf2588d51774554bd697e64992d8` | 29043 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `90ad07084f6410c8ea33384d2314822f43432c356a605c7bc2844533f99c4cd4` | 79103 |
| `report.json` | `e14237d8791d5f4a723a3665e070a34244ab513a97de7d83bf361353f4b9bde4` | 44981 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `5161bf658ff3d3a7b964fbf2b789b787c85ac19027899c1bcfe3c2ee2cca4fd1` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `15ab3880839b20c0c13ff7f67d9af814c5a4fa82324f7a533f97c9171613ef13` | 4687 |
| `test_reference.py` | `a3ac8b70bcb251326c46e0033cb66db78ad49cb5dc24e5ea25debbf536e66158` | 20342 |
| `verify.py` | `4041c7a1cf1c0616c1107589abf32a769c1f7a6f4384aa661caabbbf5a5c1219` | 20336 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.
