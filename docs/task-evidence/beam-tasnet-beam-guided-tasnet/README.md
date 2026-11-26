<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-BEAM-TASNET-BEAM-GUIDED-TASNET — spatial admission blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Beam-TasNet / Beam-Guided TasNet`
(`component_id=beam-tasnet-beam-guided-tasnet`). The acceptance profile is
**Spatial**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before `processor_exposure`;
`evidence_status=incomplete`, `qualification_status=not_qualified`. A missing
result never qualifies the candidate.

The catalogue label names **two distinct architectures**. Beam-TasNet combines
multichannel Conv-TasNet separation with an MVDR beamformer; Beam-Guided TasNet
is a separate iterative beam-guided framework. Neither exact implementation,
source revision, checkpoint, weight digest or licence is pinned, and no
synchronized rights-cleared microphone-array corpus exists. The package therefore
models the **spatial admission boundary** a caller-supplied external checkpoint
would have to cross: synchronized two-channel f32 input, a declared linear array
geometry, an explicit reference channel, a caller-supplied external asset, and a
fail-closed whole-clip boundary.

A deterministic stdlib **geometry fixture** exercises only that boundary. It is
explicitly opt-in, is not Beam-TasNet or Beam-Guided TasNet, is not a beamformer,
separator, mask estimator, localizer or steering implementation, and substitutes
for no gate.

No candidate artifact was downloaded, loaded, built, vendored or invoked. No
source tree, checkpoint, weight, ONNX graph, framework runtime, array recording,
corpus, device clock, listener, benchmark or release artifact is present or
claimed. No public API/ABI, `CONTRACTS.md`, descriptor, registry, installed
default, shared build, CI, board or handoff file changes. Only this task-local
directory is added.

## Exact external blocker

1. **Architecture identity is unresolved.** The pinned
   `research/voice-enhancement-20261101/candidate_matrix.csv` row and both
   transform reports describe two architectures under one label. Neither has a
   selected implementation, immutable source revision, checkpoint SHA-256/byte
   count or weight licence in the pinned ledgers, and no source or checkpoint for
   either is present in this worktree.
2. **No synchronized rights-cleared array corpus exists.** The catalogue boundary
   needs synchronized array channels, declared geometry, channel calibration,
   timestamp alignment, a reference channel, target/reference directions and
   clean target images. Adjacent offline/online multichannel WPE fixtures are
   two-channel synthetic dereverberation controls; they are not array
   recordings and not beamforming or separation evidence.
3. **No runnable runtime or checkpoint is available.** No `torch`, `asteroid`,
   `speechbrain`, `onnxruntime`, `numpy` or equivalent runtime is installed in
   this worktree, and no pinned vendor runtime or checkpoint digest exists. Even
   a caller-supplied checkpoint could not be executed here.
4. **No qualification evidence exists.** There is no held-out task-matched array
   score, independent scorer, permitted listening result, measured channel
   synchronization, geometry calibration, target-device timing, benchmark or
   release artifact.

**Reopen condition.** Admit the candidate only after one exact implementation is
selected with an immutable source revision and checkpoint SHA-256/byte count and
cleared weight terms; a rights-cleared synchronized microphone-array corpus
declares geometry, calibration, timestamp alignment, reference channel,
directions and clean target images; a pinned runnable runtime artifact installs
in the intended environment with documented distribution/product-use terms; and
task-matched held-out array scoring, an independent scorer, permitted listening
and measured channel/geometry and target-device timing exist. Until then all
eight release gates stay `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame. The
  spatial fixture is a separate task-local model and does not alter v0.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `streaming_mode_added=false`, `processor_exposure=false`.
- The task-local `adapter.json` is a proposal descriptor, not a provider. It
  advertises `modes=["offline"]`, a 2-channel synchronized input, the external
  checkpoint requirement, `streaming_supported=false`,
  `beamforming_supported=false`, `separation_supported=false` and
  `asset_readiness="blocked"`.
- The caller-supplied checkpoint contract is modelled metadata-only. No
  filesystem path enters configuration or errors, no bytes are read and no
  download is attempted.
- The board file is never hashed. Only the stable `id`/`title`/`mode` identity of
  the linked rows, plus the dependency ids, are gated by
  `board_link_projection_sha256`.

## Spatial semantics modelled

- One complete synchronized clip of 1 to 16,000 samples per channel, exactly two
  channels, reference channel `0`, `f32`, 16 kHz. One `process_scene` call
  consumes the complete clip and returns exactly one mono sample per input
  sample. A second call fails with `scene_already_complete`; there is no method
  to append, flush or reset.
- Declared fixture geometry: `linear_uniform_axis_x`, `0.08 m` spacing,
  `343.0 m/s`, target at `+30°`, interferer at `−45°`. Integer-free fractional
  delays are computed from the geometry: target
  `[0.0, 1.865889…]` samples, interferer `[0.0, −2.638766…]` samples.
- The three variants are linear channel maps, not beamformers: reference-channel
  passthrough (identity/CT-1 control), alternate-channel passthrough
  (reference-condition control) and an unsteered equal channel mean (naive-mix
  control). No steering delays, MVDR, masking or separation is applied.
- Channel loss fails closed: in `channel_dropout` the alternate-reference variant
  is `rejected: channel_unavailable`; no channel is silently substituted. The
  naive mean is still scored and its `−6.02 dB` target loss is recorded, not
  hidden.
- A synthetic impulse/geometry probe preserves the reference-channel sample
  index exactly; no algorithmic lag, streaming delay, channel-sync offset or
  device timing is modelled or measured.
- Sessions are one-shot and stateless across clips: a fresh clip B is identical
  before or after clip A, replaying A is bit-identical, and no state is carried.
- Availability and all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`. There is no wall clock, device clock,
  channel calibration, callback deadline, paced workload or end-to-end latency
  measurement.

## Spatial profile application

`report.json:spatial_profile` records declared geometry and reference channel,
then marks every required Spatial comparison explicitly: timestamp calibration
`blocked_unmeasured`, localization/activity `not_applicable_no_candidate`,
extraction `not_performed_no_candidate`, held-out labels
`blocked_missing_array_cohort`, leakage/target-damage/channel-loss/room-change
`synthetic_fixture_only_not_qualified`, listening `not_run`, real array corpus,
runtime and weights `false`, and device timing `blocked_unmeasured`.

### Synthetic fixture results (not a candidate result)

Paired synthetic diagnostics on the same 16,000-sample fixture for every
condition and variant. They describe the fixture only.

| Condition | Variant | SI-SDR dB | Target dB | Leakage dB | Peak |
| --- | --- | ---: | ---: | ---: | ---: |
| target_only | identity_passthrough | 22.138401 | 0.000000 | n/a | 0.241400 |
| target_only | alternate_reference_channel | 13.168732 | -0.005875 | n/a | 0.241461 |
| target_only | naive_channel_mean | 18.762689 | -0.046955 | n/a | 0.238382 |
| interference_only | identity_passthrough | n/a | n/a | 0.000000 | 0.197823 |
| interference_only | alternate_reference_channel | n/a | n/a | -0.032317 | 0.196462 |
| interference_only | naive_channel_mean | n/a | n/a | -0.257367 | 0.187786 |
| target_plus_interference | identity_passthrough | 0.488408 | 0.000000 | 0.000000 | 0.423895 |
| target_plus_interference | alternate_reference_channel | 0.149420 | -0.005875 | -0.032317 | 0.424316 |
| target_plus_interference | naive_channel_mean | 0.619919 | -0.046955 | -0.257367 | 0.409025 |
| channel_dropout | identity_passthrough | 0.489989 | 0.000000 | 0.000000 | 0.426131 |
| channel_dropout | alternate_reference_channel | rejected | rejected | rejected | rejected |
| channel_dropout | naive_channel_mean | 0.489989 | -6.020600 | -6.020600 | 0.213065 |

`n/a` means the fixture condition has no target (interference-only) or no
interferer (target-only), so that ratio is undefined and is not fabricated. No
output is clipped or non-finite; the largest synthetic peak is about `0.426`.

### Honest regressions

Negative paired deltas are recorded verbatim in `report.json:regressions`. On
`target_only`, the alternate channel and the unsteered mean both lose SI-SDR
against the reference-channel control because the geometric target delays are
not compensated. On `channel_dropout`, the naive mean loses `6.0206 dB` of
target energy because one physical channel is absent. The naive mean can also
*raise* SI-SDR on `target_plus_interference` (`+0.1315 dB` over the identity
control) by averaging down uncorrelated noise and interference; that is a
fixture observation, not evidence that averaging is a beamformer. No threshold
was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact: its output digest equals the observed
  reference-channel digest, and its target preservation is exactly `0.0 dB`.
- `alternate_reference_channel` is the reference-condition control.
- `naive_channel_mean` is the unsteered mixing control; its comb/leakage is a
  boundary control, not a quality result.
- Config rejections: wrong sample rate, channels, sample format, frame size,
  maximum clip or reference channel; missing, non-synchronized or zero-spacing
  geometry; surrogate without opt-in; and an unavailable caller checkpoint all
  fail before instance creation. A fully pinned **synthetic admission control**
  is created to prove the admission branch; it is explicitly not the candidate.
- Scene rejections: empty, oversized, wrong-channel-count, ragged, string,
  boolean, non-finite and out-of-range scenes fail with unchanged status
  digests; a second scene and any post-close call fail closed.
- Lifecycle: one call only, close is idempotent, and there is no `process`,
  `flush` or `reset` streaming API to call.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic geometry fixture, admission, accounting, metrics and report model. |
| `run.py` | Regenerates `adapter.json`, `readiness.json`, `report.json`, the README digest table, `contract.json`, sidecars and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Spatial report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline spatial adapter descriptor. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `test_reference.py` | Deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README-digest, board-projection, reproduction, disposition, licensing and scope verifier. |
| `check_licensing.py` | Independent SPDX/REUSE and fail-closed file-set check. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Spatial acceptance profile. |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | CLN-07 catalogue identity. |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Blocked candidate row 59. |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` | Two-architecture description and source lead. |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` | Blocked local-trial record. |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Beacon tasks and array/mask boundary. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Candidate census context. |
| `source:research/pilot_source_research.md` | `c9db16172ffaa1bcf8b5cc334d9401173528c31d1ec966176d6e99a0bbe52fe5` | Competition/scenario boundary context. |
| `source:research/task_backlog.json` | `0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc` | Legacy family F07 status. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |
| `worktree:docs/task-evidence/survey-cln-07/README.md` | `b748f2fda2ffebf10ea5f00923dc1dc1110f0712bada2ded074def53ef682d34` | Merged beamforming/spatial map. |
| `worktree:docs/task-evidence/survey-cln-07/report.json` | `aad53c0a3e6d90c4d27fea6abb4001d40168700a8fa2d717f53b03091a9c5a6a` | Merged blocked-candidate census. |
| `worktree:docs/task-evidence/survey-spk-01/README.md` | `554a9fcc044e89c35ba761bf1fa8f7fed172ba22f797e44bdd64a753c00adc9d` | Merged separation map. |
| `worktree:docs/task-evidence/survey-spk-01/report.json` | `04f17e36954b792bcba59b59fef537f6e699654cc6fd71c39e46567809a6ff2f` | Merged separation blocked leads. |

### Source-reported values (provenance only)

The pinned transform report says: “Beam-TasNet combines multichannel Conv-TasNet
separation and MVDR; Beam-Guided TasNet is a distinct iterative framework.” The
pinned candidate-matrix row records `unavailable/blocked`, an unresolved exact
architecture/checkpoint and no synchronized multichannel target data. No
source-reported numeric quality, array or timing value exists for this candidate,
so none is transcribed, invented or pooled. Sibling maps are cited read-only and
no sibling metric is promoted.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-BEAM-TASNET-BEAM-GUIDED-TASNET diff --check
```

`run.py --all` regenerates the adapter, readiness, report, digest sidecar,
README digest table, contract and source manifest. `report.json` is canonical
JSON (`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical.

The repository's installed-package gate is run from the SDK root on the exact
head:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

## Expected counts and digests

- Four conditions, 16,000 samples per channel, two synchronized channels;
  128,000 synthetic input samples total.
- One complete whole-clip call per condition; 100 frames per clip; no startup,
  tail or flush samples. Three linear variants per condition: 11 scored and one
  `channel_unavailable` rejection.
- Twelve config adverse cases (eleven rejections plus one synthetic admission
  control); eleven scene adverse cases; all rejections leave status unchanged.
- Declared target delays `[0.0, 1.865889…]` and interferer delays
  `[0.0, −2.638765830666999]` samples; no integer rounding is hidden.
- `report.json` SHA-256 and byte count are in the table below.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `adapter.json` | `9d3e2e207b1962c6da56d008876ed77b0ff5cc11c98eefd3d87b5404eca3ca97` | 1228 |
| `check_licensing.py` | `7164f60c2b4e5426868564e7713d970e29960b811d1a787c43eed7357a9f3fb3` | 4137 |
| `readiness.json` | `a78905e96d6d1dc1a1eb0f01af15629dd43a6658d1d68ebf30398dd69b536b10` | 4857 |
| `reference.py` | `1c32816d2e6352c1abfb79225a7cfe7f18db0a7b8d4240a737f94c75ef8fc60d` | 65011 |
| `report.json` | `52c470ef552a0dac700e7a041ccb95794677c241a8c9ff9717d8a49c79ef8d7b` | 34782 |
| `run.py` | `be2229063677f2011c05f8a19baf349d87d972749b8eac18bff141febc114df4` | 6023 |
| `test_reference.py` | `b54220469973cae4f9a6c9d350ef6e36f03a8349c302bca6239cddb6a13c332c` | 26113 |
| `verify.py` | `bbfd846d28b605a7edfed0c35672650ef53f8fc3fcbe50373a6516821fa3006f` | 36985 |
<!-- DIGEST_TABLE_END -->

## Gates (all blocked)

| Gate | Name | Status | Reopening condition |
| --- | --- | --- | --- |
| `RG-01` | `exact_architecture_identity` | blocked | One exact implementation selected with immutable source revision and checkpoint identity. |
| `RG-02` | `source_and_weights` | blocked | Checkpoint digest/byte count, runtime artifact and weight licence cleared. |
| `RG-03` | `array_corpus_and_rights` | blocked | Rights-cleared synchronized array corpus with geometry, calibration and clean targets. |
| `RG-04` | `task_matched_scoring_and_listening` | blocked | Held-out array scoring, independent scorer and permitted listening. |
| `RG-05` | `channel_and_device_timing` | blocked | Measured channel synchronization, geometry mismatch, channel loss and target-device timing. |
| `RG-06` | `provider_intake` | blocked | Opt-in provider intake, OFF default and independent exact-head review. |
| `RG-07` | `public_default_selection` | blocked | Explicit owner default decision after intake. |
| `RG-08` | `release_approval` | blocked | Separate release decision after RG-01…RG-07 close. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
