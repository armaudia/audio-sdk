<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NVIDIA-NEMO-SCHR-DINGER-BRIDGE-DENOISER-SE-DEN-SB-16K-SMALL — NVIDIA NeMo Schrödinger-bridge denoiser (se_den_sb_16k_small) feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local feasibility evidence for the NeMo
Schrödinger-bridge dereverberation row. It is **not** a NeMo implementation and
**no candidate result** is present. No official source checkout, checkpoint,
model config, PyTorch/NeMo runtime, corpus, exact output vector, listening
result, device measurement, benchmark or release claim exists. **No result here
qualifies the candidate.**

`plan/INVENTORY.json` records `nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small` as `evidence_status=considered`, area "Enhancement", disposition `sdk-model` and the **Enhancement** acceptance profile. The task mode is `feasibility`. Feasibility fails before implementation because no exact source revision, checkpoint, config, locked NeMo/PyTorch runtime, rights decision, cohort or matched evidence is present. The documented decision is **DEFER** before `offline_checkpoint_staging_and_asset_admission`.

## Exact external blocker

Pinned census/INVENTORY records identify NVIDIA NeMo `nvidia/se_den_sb_16k_small`: a 16 kHz offline generative speech denoiser (WSJ0+CHiME) exposed through the official NeMo Speech checkpoint catalog. Published availability is not a local benchmark result.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | Exact NeMo source at immutable 40-hex commit, per-file SHA-256 manifest, reviewed LICENSE and notice bundle |
| Checkpoint/config | Exact `se_den_sb_16k_small` checkpoint and model/config with filename, byte count, SHA-256, sampler/solver/step config and acquisition record |
| Runtime | Locked offline NeMo 2.0 + PyTorch environment with interpreter/framework/wheel digests, target platform and offline load/import digest |
| Rights | Reviewed source, checkpoint, model-card, training-data, corpus, redistribution, product-use and derivative-output terms; reported CC BY-NC-SA 4.0 remains unreviewed and noncommercial/share-alike |
| Cohort/evidence | Rights-cleared paired noisy/clean cohort, exact-reference parity outputs, independent SI-SDR/STOI/listening where permitted, and target-device timing |
| Provider intake | OFF-by-default opt-in adapter with caller-supplied assets, descriptor/catalog review and explicit owner default decision after prerequisites pass |

Fixed absence probes are recorded in `report.json`. Every candidate source, checkpoint, config, runtime, rights, parity and cohort probe is absent; the package is caller-supplied-asset ready only as a blocker spec, not as an admitted asset.

## Task geometry

The candidate is a whole-utterance offline dereverberator. The model card
reports 16 kHz mono audio and an SDE/ODE sampler over the complete clip; it
reports **no streaming API**. No exact accepted length, hop, frame, solver,
step count, seed handling or algorithmic latency is established in the pinned
records. This package therefore records candidate frame/hop/latency fields as
`null` and does not fabricate them.

The synthetic harness uses a **probe-only** 16,000-sample mono `float32`
fixture, 160-sample segments, four fixed integer refinement steps and two
probe-only sampler labels. Those values are fixture parameters, not candidate
geometry. Installed SDK v0 remains 16 kHz mono `float32` at **160 samples**; no
installed geometry, default, ABI, contract, registry, descriptor, shared build
or CI file is changed.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied in `report.json` → `acceptance_profile` and checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Identity/noisy control and task-matched baseline | Synthetic identity/noisy strata only; no candidate output or task-matched baseline run |
| Paired SI-SDR and STOI on permitted clean references | Blocked: no clean-reference paired corpus or candidate output |
| Clean-speech preservation, peaks and invalid outputs | Surrogate finite/bounded on synthetic control only; no candidate preservation claim |
| Unpaired predictive screen or authorized listening | Blocked: no unpaired corpus, predictive screen or authorized listening |
| Alignment, state, memory and measured content/availability timing | Blocked: no exact runtime, alignment, state, memory or timing measurement |

## Fixture and surrogate

`reference.build_fixture()` synthesises 16,000 samples (1 s, 100 blocks of 160)
from integer arithmetic: a fixed 64-entry sine table, integer phases and
envelopes, fixed early and late room responses and one deterministic LCG noise
source. Every sample is quantised to int16 and exposed as `float32 / 32768`.
Segment boundaries are multiples of 160 samples. The exact decomposition
`reverb = early + late + noise` is retained for structural checks.

| Stratum | Frames | Condition |
| --- | ---: | --- |
| `silence-a` | 0–19 | Exact digital silence |
| `speech-a` | 20–49 | Harmonic speech-like segment |
| `speech-b` | 50–69 | Harmonic segment plus deterministic click transients |
| `noisy-speech` | 70–89 | Harmonic segment plus frozen LCG noise |
| `tail-after-speech` | 90–99 | Clean source ends; noise tail decays |

The surrogate is a deterministic, non-adaptive, model-free whole-clip boundary
harness: a fixed causal late-reverberation subtraction followed by a fixed
integer soft limit and a configurable number of refinement passes. It contains
no neural network, sampler, checkpoint, weights or runtime, and it is **not**
NeMo. Identity is not used as a substitute for candidate parity. No int16
codec, real room, corpus or listening is involved.

## Results (surrogate invariants only, not NeMo results)

All values are exact `report.json` values. They are surrogate behaviour
observations, **not NeMo results**, not device timing and not a release claim.
No SI-SDR, STOI, ESTOI, PESQ, SRMR or perceptual score is claimed because no
candidate output exists.

| Invariant | Exact value |
| --- | ---: |
| Fixture samples | 16,000 |
| One-shot input / output samples | 16,000 / 16,000 |
| Maximum absolute surrogate output | 0.779937744 |
| Nonfinite surrogate outputs | 0 |
| Clipped surrogate outputs | 0 |
| Silence stratum exact zero | true |
| Deterministic repeat equal | true |
| SDE and ODE fixture strings differ | true |
| One-step and four-step fixture strings differ | true |
| Stateless repeat | true |
| Multi-chunk input rejected | true |
| Partial input rejected | true |

The surrogate cannot qualify the candidate. It only proves that the local
harness enforces whole-clip accounting, finite bounded output, exact silence,
deterministic statelessness, full-clip-only refusal and fail-closed validation.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates both hashes, the runtime hash, byte count and 16 kHz mono geometry,
  but reports `loaded=false`, `executed=false`, `imported=false`,
  `candidate_asset=false` and `qualification_effect=none`. Missing-field,
  extra-field, relative-path, absent-file, checkpoint-hash, config-hash,
  runtime-hash, byte-count, short-commit, 48 kHz, two-channel, `int16`, unknown
  sampler, zero-step, boolean-step, non-external-storage and empty-license
  manifests are rejected. A caller placeholder is never admitted as the
  candidate; the candidate path fails closed with
  `upstream_revision_not_verified`, `checkpoint_identity_not_verified`,
  `runtime_not_pinned`, `license_scope_unresolved` and
  `rights_register_entry_absent`.
- **Config adverse:** 48 kHz, two channels, `int16`, 8,000 samples, `ddim`,
  zero or three steps, negative or boolean seed, `real_runtime=true`,
  model-used, surrogate-disabled, opt-out, missing key and extra key are
  rejected before processing.
- **Input adverse:** empty, short, long, string, bytes, nested, boolean, NaN,
  ±Infinity and out-of-range utterances are rejected; no state or output is
  produced.
- **Streaming adverse:** a two-chunk feed and a partial feed are rejected with
  `utterance_level_offline_only` and `utterance_length_mismatch`; only one
  complete utterance is accepted and no streaming claim is made.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `sdk_data_dir_added=false`. No proposal
  `adapter.json` or `readiness.json` is added; machine-readable state lives in
  `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-NVIDIA-NEMO-SCHR-DINGER-BRIDGE-DENOISER-SE-DEN-SB-16K-SMALL]`, stable-field
  digest). The mutable full `plan/swarm/TASKS.json` is never hashed or pinned.
- No candidate weight, checkpoint, config, graph or runtime was downloaded,
  read, hashed, loaded, compiled, executed or bundled. The adapter README is
  hashed read-only for provenance. Its upstream-reported scores are quoted
  context, not a local result.
- No rights entry exists. The reported CC BY-NC-SA 4.0 terms are unreviewed and
  do not clear evaluation, redistribution, customer deployment or public
  playback.

## Reproduction

From this directory, with Python 3 standard library only:

```sh
python3 reference.py            # imports the deterministic boundary surrogate
python3 -m unittest -v test_reference.py
python3 run.py --all            # report, README table, contract, SOURCES.sha256
python3 verify.py               # strict read-only verification
python3 -m reuse lint           # repository licensing gate
```

`verify.py` runs `run.py --digest` three times from a cold start, requires one
byte-identical digest, and compares it with `report.json.sha256`. It also fails
on any change outside `docs/task-evidence/nvidia-nemo-schr-dinger-bridge-denoiser-se-den-sb-16k-small/`
and on a drifted stable board projection.

## Digest table

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `0e6305babaa76152dfa248844ec5fb5eec8ba0de788728b089ac243ac3cce8ca` | 87594 |
| `report.json` | `b280fbb0df0cc3e09e56ab6ad30fae5272d75431ad000480a4f37ac4da372d49` | 37268 |
| `report.json.sha256` | `d2c61bb8f2620c8dc2c17329e67cd2abb91f89f553f40bab4c20ad7c2e545d51` | 78 |
| `run.py` | `2514e87b6c4bbcd2d193f7a9d922a359786521ac6e505657baa979c322103b48` | 6951 |
| `test_reference.py` | `f419a871aaa3c822a0a170ff81037e166b2872ea56f2b9ad53278b617461f1a9` | 27579 |
| `verify.py` | `89505c317fed1e593646c1a08e8421590c1da6dd34e1c490d6cdd623c1d7ab2a` | 32473 |
<!-- DIGEST_TABLE_END -->
