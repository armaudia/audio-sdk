<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEMO-SCHR-DINGER-BRIDGE-DEREVERBERATION — NeMo Schrödinger-bridge dereverberation feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local feasibility evidence for the NeMo
Schrödinger-bridge dereverberation row. It is **not** a NeMo implementation and
**no candidate result** is present. No official source checkout, checkpoint,
model config, PyTorch/NeMo runtime, corpus, exact output vector, listening
result, device measurement, benchmark or release claim exists. **No result here
qualifies the candidate.**

`plan/INVENTORY.json` records `nemo-schr-dinger-bridge-dereverberation` as
`evidence_status=blocked`, area “Echo and room”, disposition `sdk-model` and the
**Room** acceptance profile. The task mode is `feasibility`. Its deliverable asks
the owner to verify runnable source, exact assets, permitted scope, task geometry
and matched evidence before reproducing the exact model/runtime as a
caller-supplied-asset reference and adding an opt-in adapter. Feasibility fails
at every prerequisite, so the documented decision is **DEFER** before
`offline_checkpoint_staging_and_asset_admission`.

## Exact external blocker

The pinned local records identify one candidate: NVIDIA NeMo
`nvidia/se_der_sb_16k_small`, a 16 kHz mono, **utterance-level** generative
Schrödinger-bridge dereverberator. `research/dereverberation_candidates_20261028.md`
line 23 records it as a single-channel generative model trained/evaluated on
WSJ0-Reverb, with upstream-reported SDE PESQ 2.79, ESTOI .89, SI-SDR 7.4 dB and
WER 4.27%. `adapters/nemo-dereverb/README.md` line 3 adds that it uses an SDE/ODE
sampler over the complete clip, was tested upstream on an NVIDIA V100, has no
streaming API in the model card and lists NeMo 2.0 and CC BY-NC-SA 4.0.

The adapter also states it **has not been executed locally** because the
workspace has no NeMo or PyTorch runtime and the model weights are not present.
The pinned records therefore give scope and upstream scores only. They record
**no** NeMo source revision, tree digest, checkpoint filename, byte count,
SHA-256, model config, sampler defaults, solver, step count, seed behaviour,
accepted audio length, algorithmic latency, rights review or exact output.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | The exact NeMo source at an immutable 40-hex commit, a per-file SHA-256 manifest from a reviewable tree, the reviewed upstream LICENSE and notice bundle |
| Checkpoint | The exact `se_der_sb_16k_small` checkpoint with immutable upstream revision, release tag, filename, byte count and SHA-256 |
| Model config | The exact Hydra/model config with digest, accepted audio length, sampler, solver, step count, seed handling and post-processing |
| Runtime | A locked, reproducible offline NeMo 2.0 and PyTorch environment with interpreter, framework, wheel digests, target platform and load/import digest |
| Rights | Reviewed source, checkpoint, model-card, training-data, corpus, redistribution, product-use and derivative-output terms; the reported CC BY-NC-SA 4.0 noncommercial share-alike terms require separate clearance for any product use |
| Reverberant cohort | A frozen, rights-cleared paired cohort with clean or early targets, measured or frozen RIRs, the early-response definition, strata and identity controls |
| Matched evidence | Exact-runtime reference parity for frozen inputs, independent intrusive or non-intrusive scores, permitted listening, alignment and target-device timing |
| Provider intake | An OFF-by-default opt-in adapter, descriptor/catalog review and an explicit owner default decision after all prerequisites pass |

Fixed absence probes are recorded in `report.json` → `absence_audit`,
`asset_boundary.asset.workspace_probes` and `asset_boundary.asset.home_probes`.
Every candidate source, checkpoint, config, runtime, rights, parity and cohort
probe is absent. The local adapter README is present and hashed read-only for
provenance; it is not admitted as source, weight, runtime or result.

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

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Frozen render/reference | Frozen synthetic early/late/noise decomposition; no measured RIR claimed |
| Channel/rate/hop | Candidate 16 kHz mono whole-utterance; no candidate hop established; 160-sample block is probe-only |
| Excitation | Deterministic harmonic segments plus click transients and an LCG noise stratum |
| Delay | No candidate algorithmic latency or streaming delay claim; candidate is offline |
| Movement | Not applicable: no render path and no measured room movement |
| Noise | Frozen noisy-speech stratum with a deterministic LCG source |
| Reset schedule | Candidate is stateless across whole-clip calls in this package; repeated input is identical |
| Echo-only | Not applicable: no far-end playback reference and no echo path |
| Near-end-only | Not applicable: no near-end/render decomposition is claimed |
| Overlap | Not applicable: no double-talk condition is evaluated |
| No-reference | Not applicable: no candidate output exists to compare |
| Echo attenuation | Not measured; no echo-cancellation claim |
| Near-end damage | Blocked: no real candidate output or early-target score |
| Nonfinite failures | Injected NaN and infinities are rejected before processing; the surrogate produced no nonfinite output |
| Alignment, delayed/missing render | Not applicable: no candidate alignment claim on an offline path |
| No-reference independent comparison | Blocked: no candidate output, corpus or listener |

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
| `tail-after-speech` | 90–99 | Clean source ends; room tail decays |

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
  (`tasks[id=SDK-NEMO-SCHR-DINGER-BRIDGE-DEREVERBERATION]`, stable-field
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
on any change outside `docs/task-evidence/nemo-schr-dinger-bridge-dereverberation/`
and on a drifted stable board projection.

## Digest table

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `285871c896d1a9a1d33b2074c2539025aec8c3f0feef1a1974526957f71a2bbb` | 85991 |
| `report.json` | `334e15b38ffd1ff22b2797721068fac08359dfe86e86b3ff4417eba3519a69b3` | 39157 |
| `report.json.sha256` | `7d1fdbf93867f0cab7861d6782361d8c25240d31cbb44c38bab40e16aa8cf5f7` | 78 |
| `run.py` | `58c963a39734ea7e79d252d0b6b8c46991ef5712ec77fb47ef694c120746ee7d` | 6931 |
| `test_reference.py` | `084761d53cf438f3a73ad2a3717be10a9b07138a4c00ba775f60a42e75019664` | 27736 |
| `verify.py` | `4f86b2b062430f7c977074e1619f41bb814f8d211582a33f7e76d4e726cfd73b` | 32246 |
<!-- DIGEST_TABLE_END -->
