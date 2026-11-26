<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-HIFI-GAN-VOCODER — HiFi-GAN research-control blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local evidence for the HiFi-GAN vocoder
research-control row. It is **not** a HiFi-GAN implementation and it does **not**
retain or reproduce the requested comparison. No official source checkout,
generator checkpoint, acoustic feature contract, PyTorch/ONNX runtime, corpus,
voice pair, generated waveform, listening result, device measurement, benchmark
or release claim is present. **No result here qualifies HiFi-GAN.**

The structured inventory marks `hifi-gan-vocoder` as `evidence_status=considered`
with the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`). The task mode is `research-control`. Its deliverable asks
for the comparison to be retained or reproduced as an optional developer/evidence
adapter with a documented proceed/defer decision before processor exposure. The
pinned research record classifies the candidate as **out of scope**, and the
exact source, weights, runtime, rights and consent are all absent, so the
documented decision is **DEFER** before `processor_exposure`.

## Exact external blocker

A **derived HiFi-GAN module** is visible inside two unrelated project checkouts,
but neither is the official `jik876/hifi-gan` release and neither contains a
generator weight:

| Copy | Revision | License | Weight present | Admitted |
| --- | --- | --- | --- | --- |
| `research/voice-conversion-eval-20261101/repos/cosyvoice` (`cosyvoice/hifigan`) | `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc` | Apache-2.0 (containing project) | No | No |
| `research/voice-conversion-eval-20261101/repos/seed-vc` (`modules/hifigan`, HiFT variant) | `51383efd921027683c89e5348211d93ff12ac2a8` | GPL-3.0 (containing project) | No | No |

The exact **official source**, **generator checkpoint** and **isolated runtime**
are absent. The pinned census only links to the authors' paper
(`arXiv:2010.05646`) and the official repository URL. Nothing was fabricated,
reconstructed, mirrored, downloaded or substituted. No revision, file name, byte
count or SHA-256 is asserted for a candidate artifact.

| Missing artifact | Exact requirement |
| --- | --- |
| Official source checkout | `jik876/hifi-gan` at an immutable 40-hex commit, a per-file SHA-256 manifest from a reviewable tree, the reviewed upstream LICENSE and notice text, and a recorded comparison against the two derived modules observed in the workspace |
| Generator checkpoint | The caller-selected universal or fine-tuned HiFi-GAN generator at an immutable revision, with release tag, byte count, SHA-256, selected format (PyTorch/ONNX), declared sample rate, mel/feature configuration, upsample layout and state behaviour |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter, framework, wheel digests, lock-file SHA-256, target platform, offline load path and recorded host profile |
| Rights | Reviewed code, weight, model-card and training-data terms that settle attribution, evaluation, redistribution, customer deployment, public playback and generated-output use; the GPL-3.0 Seed-VC copy needs an explicit compatibility decision |
| Voice cohort | A frozen, rights-cleared paired cohort with permitted source and target references, language and speaker groups, held-out splits, consent and output-use permission |
| Comparison design | Fixed upstream acoustic features and a decoder-only vocoder-swap control; a vocoder alone does not transform input voice or accent |
| Candidate results | Exact-runtime reference parity for frozen inputs, independent semantic-preservation, speaker-identity and naturalness scoring, permitted listening, alignment, first-output/tail timing, state, memory, availability and resources |

The machine-readable record is `report.json` → `research_control`,
`asset_boundary`, `asset_admission`, `workspace_observations`, `rights`,
`voice_profile`, `native_evidence`, `exact_blockers` and `release_gates`.
`contract.json` carries the same disposition, absent geometry, pins and all
eight blocked release gates.

## Documented proceed/defer decision

`report.json:research_control` records the exact pinned basis:

- `plan/INVENTORY.json` component `hifi-gan-vocoder`, disposition
  `research-control`, evidence record 53 “HiFi-GAN / Vocos vocoders”,
  record status **out of scope**, finding “Vocoder components do not
  independently transform input voice/accent”.
- `research/voice-enhancement-20261101/candidate_matrix.csv` line 54 and
  `research/voice-enhancement-20261101/agent-transform-space/REPORT.md` line 23
  state that a neural vocoder reconstructs waveform from acoustic features and
  is a synthesis component, not a standalone voice/accent transform.
- A controlled decoder comparison would need fixed upstream features and an
  explicit TTS/VC pipeline; neither exists locally.

The decision is therefore **DEFER**. A comparison was neither retained nor
reproduced, because there is **no candidate** to run. This is not a negative
quality result; it is an evidence and scope blocker.

## What this package verifies

1. **Absence evidence.** Fixed workspace and home-cache probes are checked; no
   recursive walk is performed. All candidate probes are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale “absent” claim cannot be shipped.
2. **Observed derived copies are not admitted.** Both workspace copies are
   recorded with their containing-project revision, license and generator-file
   digest. The verifier fails if either copy disappears, changes its pinned
   files, claims exact upstream provenance, or gains a weight. Neither copy is
   used for parity, quality, timing or qualification.
3. **Stable pins.** Reviewed planning records, the candidate census, the survey
   report, the rights register and the SDK boundary files are pinned by SHA-256.
   These are read-only provenance inputs, not model evidence.
4. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on`, `write_scope`, `deliverable`,
   `acceptance`, `verification_profile` and `dispatch_priority` are projected and
   hashed. The mutable `plan/swarm/TASKS.json` file is **never hashed**; status,
   owner, claim, review, handoff, priority, timestamps and history never enter
   canonical bytes and never gate this package.
5. **Fail-closed admission.** The caller-supplied `as_asset_v0` boundary
   requires an asset ID, byte count and SHA-256 with `storage=external`; a
   missing, unpinned, unsigned or non-admitted candidate is rejected before any
   processing. One synthetic structural control is accepted to prove the
   validator is not blanket-rejecting; it is explicitly `candidate_asset=false`,
   is not HiFi-GAN and has `qualification_effect=none`.
6. **Adverse, missing, invalid and nonfinite rejection.** Wrong model, rate,
   channels, format, hop, delay, state layout, target condition and consent are
   rejected; empty, oversized, string, boolean, out-of-range, nonfinite and
   repeated streams are rejected; malformed, nonfinite and out-of-range states
   and chunks are rejected without advancing state.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the root `README.md` and the
   Apache-2.0 license are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No HiFi-GAN provider is
   installed or registered; no descriptor, default, ABI, shared build, CI, board
   or handoff change is made.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Frozen permitted input and target references | blocked | No rights-cleared source/target references, consent or output-use permission. |
| Task and language/speaker groups | blocked | No task-matched cohort, language grouping or held-out split. |
| Text/semantic content preserved | blocked | No candidate output, transcript or independent semantic scorer. |
| Identity/similarity | blocked | No target reference, independent identity model or similarity result. |
| Naturalness | blocked | No naturalness assessment, score or permitted listening panel. |
| Alignment, first-output and tail timing | blocked | No candidate output or exact-runtime timing on the target condition. |
| Exact target condition | blocked | Code, weight, features, runtime and corpus versions are all unpinned. |
| Consent, reference availability and output use | blocked | Independent gates; none is recorded. |

## Historical and peer boundary

The pinned record contains a HiFi-GAN **source lead** and source-reported context
only. There is no local HiFi-GAN run, output, metric, corpus or runtime. No value
is inferred from merged sibling vocoder evidence packages:

- `vocos` is an adjacent blocker for a different neural vocoder; its MIT-code
  provenance and historical JIT decoder-only timing never transfer to HiFi-GAN.
- `phase-vocoder-baseline` is a classical DSP phase vocoder, not a neural
  generator, and supplies no learned-model evidence.
- `cmgan`, `deepfiltergan`, `clearvoice-mossformergan` and other enhancement
  blockers have different tasks, geometry and rights records.
- The CosyVoice/Seed-VC copies observed in the workspace are derived modules in
  unrelated projects, not merged candidate evidence.

## Admission contract (task-local; not an SDK, HiFi-GAN or Voice contract)

The synthetic fixture uses `audio-sdk/task-evidence/hifi-gan-vocoder/report/0.1`.
Unknown and missing configuration fields, duplicate JSON keys, `NaN`/`Infinity`,
floats, unsafe assets, wrong geometry, wrong state layout and mismatched consent
are rejected before state change. The surrogate is opt-in via
`surrogate_opt_in=true`; the candidate branch is never admitted.

## Streaming semantics modelled

The surrogate mirrors only delay, accounting and refusal mechanics.

- One 160-sample delayed state line plus a synthetic envelope scalar. Payloads
  are fixture values, not model tensors or candidate state.
- Each chunk returns the previous delayed chunk; the first 160 output samples are
  invalid startup, matching the declared fixture buffering delay. One zero flush
  hop releases the tail within the declared maximum of two calls and 320 samples.
- A 1,093-sample control returns 1,093 samples; a partial tail is not dropped.
- Chunk-loop and whole-stream drivers are byte-identical; split-half driving is
  deliberately different, proving the state boundary is exercised.
- An impulse peak at input sample 4,000 remains at output sample 4,000.

The 160-sample hop is an installed-v0 fixture parameter. Candidate geometry is
unknown and is recorded as `null`; no v0 frame adapter, resampler or vocoder is
implemented.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `vocoder_invoked=false`,
  `sdk_data_dir_added=false`. No proposal `adapter.json` or `readiness.json` is
  added; machine-readable state lives in `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-HIFI-GAN-VOCODER]`, stable-field digest). The mutable full
  `plan/swarm/TASKS.json` is never hashed or pinned.
- No candidate source, weight or runtime was downloaded, read, hashed, loaded,
  compiled, executed or bundled.

## Reproduction

From this directory, with Python 3 standard library only:

```sh
python3 reference.py            # imports the deterministic boundary/surrogate
python3 -m unittest -v test_reference.py
python3 run.py --all            # report, README table, contract, SOURCES.sha256
python3 verify.py               # strict read-only verification
python3 -m reuse lint           # repository licensing gate
```

`verify.py` runs `run.py --digest` three times from a cold start, requires one
byte-identical digest, and compares it with `report.json.sha256`. It also fails
on any change outside `docs/task-evidence/hifi-gan-vocoder/`.

## Digests

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `b3b8979aa94a003e084435079586529c31e920802c486fa306224ee052d071e8` | 82055 |
| `report.json` | `a5e698b6d6c15a35fe89fa52e2a33c66e5055f8c4698a71cc819c297bf838c86` | 48378 |
| `report.json.sha256` | `92d7a6fe3503d82f288eb8e989ed377bfa641cbadade2a97635d45511038e193` | 78 |
| `run.py` | `3b2a343159795396c24bddfd50ca68f0072ec84c3cb435e8d33236ef9e5800bf` | 6001 |
| `test_reference.py` | `fdbfa42de2ceb5f82b1f03ecb0211134686b218fd7da37963b98e161593359db` | 31860 |
| `verify.py` | `9f028579d169f6462e235ad42982cc264cc4408164bc21e29465b77c64354274` | 23091 |
<!-- DIGEST_TABLE_END -->
