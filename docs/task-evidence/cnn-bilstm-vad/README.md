<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CNN-BILSTM-VAD - CNN-BiLSTM VAD source, weights and framewise-availability blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`CNN-BiLSTM VAD` (`component_id=cnn-bilstm-vad`). The acceptance profile is
**Analysis**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact CNN-BiLSTM VAD implementation, checkpoint, weights, runtime, adapter,
immutable revision, inference geometry, frozen output and rights record are
**absent**. This package records that exact blocker, applies the Analysis
profile to a bounded deterministic two-path synthetic control, and makes no
VAD accuracy, AUC, miss-rate, false-alarm, timing, listening, benchmark or
release claim. It is **not CNN-BiLSTM**: no convolution, BiLSTM cell, recurrent
state, weight tensor, neural runtime, real audio, corpus, model, device clock or
upstream implementation is present, copied, downloaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=cnn-bilstm-vad`) is
`considered`, `disposition=sdk-model`, `verification_profile=analysis`, with the
plan note "Separate bidirectional/offline results from framewise availability."
Its only evidence link is
`reports/vad-research/attempt-discovery-20261028-01/findings.md`.

The pinned discovery note says only:

> **Wav2Vec2/XLS-R Transformer VAD; CNN-BiLSTM VAD** (research
> implementations) - Interspeech 2024 reports Wav2Vec2-XLS-R VAD evaluated on
> AVA-Speech and a multilingual corpus; AVA-Speech test AUC reported as 96.2%.
> The report is relevant architecture literature, not comparable local
> evidence. ... No reviewed runnable implementation/checkpoint/release/version,
> license, weights digest or inference contract was found in this pass. Large
> ASR encoder runtime likely; offline/bidirectional context must not be
> presented as live streaming.

The pinned VAD source register is more specific
(`research/plans/F02/vad_sources.md`, subject "Transformer-based VAD (Karan et
al., Interspeech 2024)"):

> reports AUC results and CNN-BiLSTM/enterprise baselines. Its target is *clean
> speech* vs. other sound: speech mixed with music/noise is negative. Output
> pooling is about 105 ms; paper reports ROC/AUC and TPR at 10% FPR rather than
> miss/FA event measures. ... No eligible public
> implementation/checkpoint, terms or streaming lookahead verified; literature
> lead only.

The 96.2% AVA-Speech AUC is a **Wav2Vec2-XLS-R** result, not a CNN-BiLSTM
result, and is not used as a candidate metric. The register lists CNN-BiLSTM as
a **paper baseline**, not the reported proposed system.

Consequently:

- no CNN-BiLSTM source, checkpoint, weights, runtime, adapter or pinned
  revision is staged at `data/checkouts/cnn-bilstm-vad`,
  `data/models/cnn-bilstm-vad`, `data/envs/cnn-bilstm-vad` or
  `adapters/cnn-bilstm-vad`;
- no immutable source/weight hash, byte count, build/archive identity,
  parameter layout, tensor schema, sample rate, hop, pooling, bidirectional
  context, lookahead or numeric output exists for CNN-BiLSTM itself;
- no upstream LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged;
- no feature frontend, threshold/hysteresis policy, reset policy, state shape or
  output cadence is documented for the candidate;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; no candidate
  frame/hop geometry is asserted, and no cross-hop mapping is verified;
- no real speech/nonspeech cohort, scored regions, held-out session, consent,
  AUC, miss-rate, false-alarm, boundary or listening result exists;
- no target-device timing, availability, resource, drain, provider intake or
  independent release review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable records are in
`contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CNN-BILSTM-VAD`, `6967a728b5c4048fb01ed4522a76a6906fbcffe2` |
| Task | `SDK-CNN-BILSTM-VAD` |
| Task mode | `feasibility` |
| Acceptance profile | `analysis` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | unresolved; no rate/hop/pooling/lookahead asserted |
| Surrogate | synthetic 16 kHz mono milli-probability frame trace |
| Framewise control | 3-frame causal median, zero lookahead |
| Offline control | 11-frame centred mean, 5-frame lookahead |
| Provider registration, default, ABI, CI | none |

The synthetic control is **not CNN-BiLSTM**, is not learned, uses no weights and
cannot qualify the candidate. It exists only to instantiate the plan note's
separation between bidirectional/offline results and framewise availability.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` -> `analysis_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Score timestamped probabilities | control only | Synthetic milli-probability trace mapped to exact half-open 160-sample intervals; no model probability |
| Score event boundaries and detections | control only | Exact truth and hypothesis runs; maximum-overlap one-to-one pairing |
| Quiet and active speech | blocked | Synthetic strata only; no real condition-labelled speech |
| Idle noise | blocked | Synthetic idle frames only; no real nonspeech |
| Known positives and negatives | blocked | Synthetic labels only; no known-positive or known-negative corpus items |
| Onset and offset delay | control only | Integer sample and millisecond boundary errors for both paths |
| Stratified FN/FP | blocked | Synthetic stratum counts only; no real stratified scoring |
| Separate validity from nonspeech | control only | Unknown region excluded; known false scored; invalid values rejected |
| Independent state | blocked | No CNN-BiLSTM recurrent state or reset exists |
| Exact source intervals | control only | Every frame maps to `[k*160,(k+1)*160)` samples |
| Availability, dropped/stale events | blocked | No target runtime, deadline or stale-event measurement |
| Cross-hop behavior | blocked | Candidate hop is unknown; only the 160-sample surrogate hop exists |

Every row is `qualifies=false` with `qualification_effect=none`. Synthetic
exactness means only that the fixture is self-consistent.

## Synthetic control geometry

- Rate: 16,000 Hz mono, 160 samples per frame, 62,500 ns per sample.
- Fixture length: 800 frames = 128,000 samples = 8.0 s.
- Five conditions, one unknown span and one deliberate 3-frame energy notch:

| Segment | Frames | Samples | Label |
| --- | --- | --- | --- |
| `idle-a` | 0-80 | 0-12,800 | nonspeech |
| `quiet-a` | 80-200 | 12,800-32,000 | speech |
| `idle-b` | 200-300 | 32,000-48,000 | nonspeech |
| `active-a` | 300-460 | 48,000-73,600 | speech |
| `unknown-a` | 460-520 | 73,600-83,200 | **unknown / excluded** |
| `stress-a` | 520-640 | 83,200-102,400 | speech, noisier trace |
| `idle-c` | 640-720 | 102,400-115,200 | nonspeech |
| `active-b` | 720-800 | 115,200-128,000 | speech |

The trace is an integer LCG (`seed=0xC0FFEE42`) around fixed per-condition
levels, clamped to `[0,1000]`; frames 360-362 are forced to `250`. The threshold
is exactly `500` milli-probability. Frame 360-362 lies inside `active-a`, so the
3-frame causal median splits the event while the 11-frame centred mean bridges
it using future frames.

Measured synthetic observations (unqualified, not model results):

| Item | Framewise causal | Bidirectional offline |
| --- | --- | --- |
| Window | 3-frame causal median | 11-frame centred mean |
| Lookahead | 0 samples | 800 samples / 50,000,000 ns |
| Decision available | end of frame `k` | end of frame `k+5` |
| TP / FN / FP / TN frames | 474 / 6 / 2 / 258 | 471 / 9 / 0 / 260 |
| Unknown frames excluded | 60 | 60 |
| Miss rate | `1/80` = 0.0125 | `3/160` = 0.01875 |
| False-alarm rate | `1/130` = 0.007692 | `0` |
| Onset median error | 160 samples / 10 ms | 0 samples / 0 ms |
| Offset median error | 160 samples / 10 ms | 0 samples / 0 ms |
| 90th-percentile absolute onset | 10,240 samples / 640 ms | 640 samples / 40 ms |
| 90th-percentile absolute offset | 160 samples / 10 ms | 480 samples / 30 ms |
| Unmatched truth / hypothesis runs | 0 / 1 | 0 / 0 |

The causal path is not "worse" or "better" than the offline path in general:
the synthetic trace happens to give the offline smoother a lower false-alarm
count while eroding quiet-speech boundaries, and the causal path a lower miss
count while splitting on the notch. These values are artifacts of the fixed
trace, **not** an accuracy ranking and **not** CNN-BiLSTM behavior. The only
claim is structural: the offline path consumes future frames and therefore is
not framewise-available.

## Availability separation

`report.json` -> `reference_protocol.availability` records:

| Field | Value |
| --- | --- |
| `separation_declared` | `true` |
| `framewise_available` | `true` |
| `offline_available` | `false` |
| `offline_streaming_claim` | `false` |
| `causal_lookahead_samples` | `0` |
| `offline_lookahead_samples` | `800` |
| `offline_lookahead_ns` | `50000000` |

Boundary error and availability delay are reported independently. An offline
timestamp error is never called operational latency, and no offline value is
presented as a live-streaming result.

## Adverse, missing and invalid handling

`report.json` records 51 rejected controls, each with unchanged processing
state. Rejections include duplicate JSON keys, `NaN`/`Infinity` constants,
non-object JSON, wrong surrogate length, nonfinite or out-of-range levels,
non-boolean decisions, invalid labels, empty conditions, length mismatches,
non-object/missing/extra-field manifests, wrong schema, short or uppercase
revisions, empty licenses, unsupported weight formats and runtime names,
noncanonical runtime versions, 8 kHz, stereo, 256-sample frames, zero or
oversized hops, bidirectional with zero lookahead or zero context, framewise
with nonzero lookahead, negative context, non-boolean bidirectional flags,
empty/zero/boolean state dimensions, boolean/zero/float thresholds, nonzero
nonfinite counts, fewer than eight frozen cases, failed controls, a manifest
that claims qualification, relative/missing paths, wrong weights/lock/rights/
probability digests, wrong byte counts, nonfinite or out-of-range probabilities,
overlapping/inverted events and rights records that claim qualification.

Missing real recordings, checkpoints, runtime outputs and labels are `blocked`,
never passes. A syntactically valid caller manifest is accepted **only** as a
schema control labelled `synthetic_schema_control_not_evidence`; it has
`qualifies=false`, `executed=false` and `upstream_identity_verified=false`.

## Admission contract (task-local, schema-only)

`contract.json.admission_schema` defines a strict caller-supplied reference
bundle. It requires an exact full 40-hex source revision, SPDX-style license,
caller-owned weight file with SHA-256 and byte count, weight format, isolated
runtime name/version/path/lock hash, 16 kHz mono 160-sample SDK geometry,
candidate hop, bidirectional/offline context and lookahead declaration, state
shape, integer threshold, probability oracle, event oracle, nonfinite count
zero, rights record, corpus record, at least eight frozen cases, passing
controls and `claims_qualified=false`.

A bidirectional manifest must declare positive lookahead and offline context; a
framewise manifest must declare zero for both. The validator never imports a
runtime, reads audio, loads weights or executes a model. It validates local file
identity only and cannot certify upstream identity, rights, parity or accuracy.

## Determinism and reproduction

`run.py` builds `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` three times in one process and refuses to write unless every
payload is byte-identical. `verify.py` additionally runs three fresh cold-start
subprocesses into temporary directories and compares all four artifacts byte for
byte. Canonical JSON is sorted-key, compact, `allow_nan=false`, with a trailing
LF. The surrogate uses integer levels and a fixed LCG seed; no libm, clock,
locale, device or network value enters the report.

## Separation from sibling evidence

The merged `silero-vad-v5-onnx-reference`, `silero-vad-6-2-3-reference`,
`webrtc-vad`, `fast-vad-0-2-1`, `adaptive-energy-vad`, `fixed-rms-vad` and
`speexdsp-vad` packages are separate VAD proposals with their own fixtures,
assets, metrics and dispositions. The merged `vad-research` notes and
`vad_accuracy_contract.md` are read-only boundary references. This package does
not import, pool, score or reuse their source, fixtures, metrics or results.
AVA-Speech remains a lead with unresolved source-media rights and availability;
audEERING vadtoolkit remains positive-only. Neither is scored here.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, fixed audit, synthetic two-path control, admission schema, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Analysis report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, admission schema. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, cold-start, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:reports/vad-research/attempt-dataset-review-20261028-01/assessment.md` | `050194f0e8afb3c636b08ba63bd2a0313a0ab73d3a004a0c7941d34908239152` |
| `source:reports/vad-research/attempt-discovery-20261028-01/findings.md` | `9d5c555c1c5f2db9ce3eb27da2d3f625c2e25621f6700521f82c8af300ff59d5` |
| `source:research/plans/F02/vad_accuracy_contract.md` | `f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec` |
| `source:research/plans/F02/vad_sources.md` | `374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec` |
| `source:research/seeds/dataset_sources.json` | `7d947583f54be304ba4195249b0791747ca0dbf775b61b311a2b39c9abefd7ab` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CNN-BILSTM-VAD/docs/task-evidence/cnn-bilstm-vad
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CNN-BILSTM-VAD diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact CNN-BiLSTM source revision, checkpoint digest, byte count,
   weight format, parameter layout and tensor schema.
2. `RG-02` isolated hash-pinned runtime, approved exact-runtime probability and
   event vector, byte-level parity, fresh-session reset and nonfinite rejection.
3. `RG-03` code, weight, training-data, runtime-dependency, corpus,
   redistribution, derivative-output and product-use rights with notices.
4. `RG-04` feature frontend, geometry, pooling, bidirectional context, lookahead
   and threshold policy, with offline results never presented as framewise.
5. `RG-05` rights-cleared held-out cohort with continuous truth, scored regions,
   unknown spans, condition strata, known positives/negatives, timestamps,
   boundary error and stratified FN/FP.
6. `RG-06` streaming state, independent sessions, reset, exact source intervals,
   dropped/stale events, cross-hop behavior and nonfinite output.
7. `RG-07` target-device pacing, availability delay, deadline misses, memory and
   finite drain on the intended workload with controls.
8. `RG-08` opt-in provider intake, descriptor/license review, resource bounds and
   independent exact-head release or default-selection approval.

Each exact requirement is recorded in `contract.json:gates` and
`report.json:gates`. The machine-readable blocker IDs are
`no_reviewed_implementation`, `no_checkpoint_or_weights`, `no_runtime_lock`,
`no_rights_record`, `no_geometry_or_inference_contract`,
`no_frozen_oracle_or_parity`, `no_rights_cleared_cohort` and
`no_timing_or_intake`.

**Reopen condition.** Pin the exact licensed CNN-BiLSTM source, checkpoint and
runtime with an immutable revision and documented geometry; admit an isolated
hash-pinned runtime; clear code/weight/training-data/corpus rights; map the
bidirectional offline path and any framewise path into the accepted SDK
contract; reproduce exact output; qualify a rights-cleared task-matched
held-out cohort with unknown spans preserved; measure target timing and complete
opt-in provider intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`production_callback_registered=false`, `descriptor_registry_change=false`,
`installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
`processor_exposure=false`, `adapter_json_added=false`,
`readiness_json_added=false`, `asset_bundled=false`, `weights_vendored=false`,
`native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-CNN-BILSTM-VAD]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source. No
provider, descriptor, registry, installed default, shared build or CI is
changed.

Canonical report SHA-256:
`e66ec72dcb8adf9dcd9df97e4e43fd3dd4e519b1e63178f169b2b4cf6721c0fe`.
