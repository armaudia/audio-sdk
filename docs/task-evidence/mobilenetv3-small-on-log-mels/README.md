<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MOBILENETV3-SMALL-ON-LOG-MELS — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`mobilenetv3-small-on-log-mels` (`component_id=mobilenetv3-small-on-log-mels`,
title "MobileNetV3-small on log-mels"). Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute a MobileNetV3-small checkpoint, PyTorch, torchvision, librosa, an audio
signal, AMI audio/annotations, CMUdict, a syllable label, a log-mel feature
cache or an inference path. It reads no `.wav`, `.npz` or `.pt` array and
scores no prediction. Only whole-file SHA-256 and byte-count provenance checks
are performed on the pinned research artifacts, and none is used as a signal or
as a model. It records the exact missing artifacts and rights, probes fixed
workspace/environment/home-cache paths to evidence absence, and defines a
fail-closed admission boundary for a future multi-meeting MobileNetV3 rate
cohort. Only `docs/task-evidence/mobilenetv3-small-on-log-mels/` is written; no
provider, registry, descriptor, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

The trained checkpoints, feature cache and exact runtime are **absent**:

- The detailed report names `mobilenet_rate_optimized_last_fold.pt` as the
  final-fold checkpoint. No such file exists under
  `research/tsm-followup-20261101/agent-neural/run/`. The recipe saves only the
  last fold after the final fold's evaluation, so checkpoints for folds 0–4 do
  not exist either. The 210 out-of-fold predictions therefore cannot be
  reproduced from stored weights.
- The historical runtime is Python 3.10.13 with torch 2.2.2, torchvision 0.17.2,
  four CPU threads and one inter-op thread. The `data/envs/sylnet-py310`
  environment is absent, and the available Python 3.10.13/3.11.5/3.12.16
  interpreters expose no `torch`, `torchvision` or `librosa`. The exact
  librosa, NumPy, SciPy and SoundFile versions and wheel hashes were never
  recorded, and `torch.use_deterministic_algorithms` was not enabled.
- The 24×64 log-mel feature tensor was cached in memory and never persisted.
  The front end depends on undocumented librosa defaults and an unpinned
  version, so the feature cache cannot be reconstructed bit-exactly.
- The historical cohort is one AMI EN2003a meeting (210 four-second windows).
  Reference syllables are transcript/CMUdict 1.1.1-derived, not human
  syllable-nucleus labels. AMI audio/annotation and CMUdict terms are not
  reviewed here, and no audio byte is read.
- The training scripts and trained weights have no declared license, notice or
  product-use decision. The torchvision/torch/librosa wheel license bundles are
  not staged.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Five fold state dicts, or one checkpoint plus a bit-exact retraining recipe, with SHA-256/byte counts and a reviewed trained-weight license/terms decision. The report's `mobilenet_rate_optimized_last_fold.pt` is absent. |
| `BLK-02` | A locked offline Python 3.10.13 / torch 2.2.2 / torchvision 0.17.2 / librosa runtime with every wheel hash, install/import digest, deterministic algorithms, seed 20261101 and 4/1 threads. |
| `BLK-03` | The exact persisted 24×64 log-mel feature cache with SHA-256/byte count, or a pinned front-end that reproduces the cache digest. |
| `BLK-04` | A rights-cleared, multi-meeting, speaker-disjoint rate cohort with reviewed AMI/annotation/CMUdict terms, checked syllable labels, language/speaker groups and source timestamps. |
| `BLK-05` | A reproduced five-fold CV on that cohort with a frozen scorer, constant baseline, fold stability, finite-output and adverse/missing/nonfinite controls. |
| `BLK-06` | Exact Rate-profile mapping/buffering/condition/preservation evidence, target-device timing/resources, and a separate OFF-by-default provider intake after the earlier gates clear. |

**Reopen condition.** A caller supplies the exact torchvision/dependency source
and license bundle, all five checkpoints (or a bit-exact recipe), a locked
offline runtime with wheel hashes, the persisted feature cache, a rights-cleared
multi-meeting cohort, a reproduced CV/control result, the exact Rate-profile
protocol and target-device measurements, then records a separate opt-in intake
with an OFF default and independent exact-head review. Until then this task
stays `DEFER`.

## Historical execution: provenance only

The research record contains one full five-fold training run of a
from-scratch one-channel log-mel MobileNetV3-small regressor on 210 AMI
EN2003a windows. It is transcribed with its original scope and is **not rerun,
not merged task evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | MobileNetV3-small from scratch, one-channel log-mel regressor |
| Architecture | `torchvision.models.mobilenet_v3_small(weights=None)`, first conv 1 channel, classifier 1 output, softplus |
| Parameters | 1,518,593 |
| Input | 24 mel bins, 25 ms FFT, 10 ms hop, resize 24×64, fold-local train mean/std |
| Runtime | Python 3.10.13, torch 2.2.2, torchvision 0.17.2, CPU, 4 threads |
| Training | 20 epochs/fold, batch 42, Adam `lr=1e-3`, `weight_decay=1e-4`, seed 20261101 |
| Cohort | 210 four-second windows, one AMI EN2003a meeting, 64,000 samples/window |
| OOF MAE / RMSE | `2.7566285133361816` / `3.0773868560791016` syll/s |
| OOF bias / Pearson / Spearman | `-2.728549003601074` / `-0.19302583407184123` / `-0.23494190136006463` |
| Constant-fold-mean baseline | MAE `1.1604056358337402`, RMSE `1.430286169052124` |
| Fold MAE | `2.573607921600342`, `3.300530195236206`, `2.1830849647521973`, `2.781320810317993`, `2.944597005844116` |
| Training time | `692.9195104186656` CPU seconds across folds |
| Feature-cache time | `3.597043916990515` s |
| Model-only CPU batch | median `5.366532737666387` ms/clip, excludes features |
| Device / listening / preference | absent |

The historical finding is that the from-scratch CNN was a **poor fit** on this
single-meeting cohort: it underperformed the constant-fold-mean baseline on all
aggregate metrics, with negative correlations in four of five folds. A
2.757 syll/s error is not a preferred speed factor, a TSM setting, a listener
preference or a product claim. The result is quoted only to establish why the
task stays deferred until a materially different dataset/initialization is
proposed.

## What this package actually verifies

1. **Source/recipe presence and exact pins.** The research README, detailed
   report, both training scripts, both results JSON files, the per-epoch
   progress trace, interrupt note, cohort manifest, inventory row, Rate profile
   and SDK delivery plan are pinned by SHA-256. The optimized script contains
   every required recipe element: `weights=None`, one-channel first conv,
   one-output classifier, softplus, seed 20261101, 4/1 threads, channels-last,
   20 epochs, batch 42, Adam settings, five chronological folds, exact log-mel
   arguments and the checkpoint save. This is provenance, not a weight or
   runtime qualification.
2. **Absence evidence.** Sixteen fixed workspace/worktree probes and four fixed
   home-cache/runtime probes are checked (no recursive workspace walk). All are
   absent. The documented checkpoint is named in the report but missing, so the
   contradiction is recorded explicitly. `reference.build_report()` and
   `verify.py` raise or fail if any probe later appears, so a stale "absent"
   claim cannot be shipped.
3. **Deterministic front-end arithmetic.** Pure-integer log-mel geometry
   (64,000 samples → 401 frames, 201 FFT bins, 24 mel bands, 1,536 values per
   window, 322,560 cohort values) and an exact `Fraction`-based reproduction of
   the `F.interpolate(..., size=(24,64), mode="bilinear",
   align_corners=False)` source-index/weight grid are computed with the
   standard library only. This is a resize-arithmetic reference, not feature
   extraction or a model execution.
4. **Admission boundary.** A caller-supplied MobileNetV3 rate-cohort manifest
   has a strict, task-local schema. Every malformed, missing, invalid,
   nonfinite, aliased, duplicated, out-of-range or non-integral control is
   rejected before any state change. One structural control is admitted to
   prove the validator is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
5. **Rate-profile accounting.** Source/output mapping, duration, pitch/transient
   audibility, playback buffering, 1×/rate changes, unfamiliar speech/music/
   silence, rebuffer/drift/final partial window, timestamp-tied pause/filler
   decisions and the preferred-speed policy are each recorded as **blocked**.
6. **Quality and timing accounting.** CV accuracy, fold stability, baseline
   comparison and finite/adverse controls are separate blocked outcomes;
   feature extraction, model-only latency, end-to-end p95 and device
   deadline/resources are separate blocked timing rows. No value is inferred
   from the historical run or from a sibling estimator task.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README, the merged
   Distil-Wav2Vec2 sibling package and the merged dynamic-int8 sibling package
   are pinned by SHA-256 and verified unchanged.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Measure source/output mapping and duration | blocked | The candidate is an estimator, not a TSM renderer; no mapping or duration output exists. |
| Measure pitch and transient audibility | blocked | No rendered output, F0/transient metric or listening result exists. |
| Measure playback buffering | blocked | No playback chain, queue, fill/flush or buffering measurement exists. |
| Include 1× and rate changes | blocked | No speed-factor comparison exists; syllables/second is not a speed factor. |
| Include unfamiliar speech, music and silence | blocked | One meeting of speech only; no unfamiliar/language/music/silence coverage. |
| Include rebuffer, drift and final partial window | blocked | No stream, rebuffer, clock-drift or partial-window behavior was measured. |
| Tie pause/filler decisions to source timestamps and measure preservation | blocked | No pause/filler controller, timestamp mapping or preservation measurement exists. |
| Map estimated rate to a reviewed preferred-speed policy | blocked | No preference/acceptability labels or rate-to-speed policy exists. |

## Admission contract (task-local; not an SDK, MobileNetV3 or Rate contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `architecture`, `checkpoints`,
  `runtime`, `frontend`, `audio`, `labels`, `controls`, `outcomes`, `rights`.
  Unknown and missing fields are rejected.
- **Architecture**: exactly `torchvision.models.mobilenet_v3_small`, random
  initialization, `pretrained=false`, one input channel, shape `[24,64]`, one
  output class, softplus and 1,518,593 parameters.
- **Checkpoints**: exactly five folds (`0`–`4`), unique 64-hex SHA-256 digests
  and positive byte counts. Duplicate folds or digests are rejected.
- **Runtime**: Python `3.10.13`, torch `2.2.2`, torchvision `0.17.2`, pinned
  librosa/NumPy/SciPy/SoundFile versions, CPU, four intra-op and one inter-op
  thread, channels-last, deterministic algorithms on, offline on and seed
  `20261101`.
- **Frontend**: 16,000 Hz, 64,000 samples, `n_fft=400`, `hop_length=160`,
  24 mel bands, power `2.0`, log offset `1e-10`, center padding, resize
  `[24,64]`, bilinear, `align_corners=false`, fold-train mean/std and a 64-hex
  feature-cache digest.
- **Audio**: exactly 210 unique windows, canonical absolute paths, 64-hex
  digests, `language="en"`, non-empty meeting/speaker groups, at least two
  meetings, exactly four-second spans, positive active duration and a finite
  reference rate in `[0, 20]`.
- **Labels**: `cmudict-first-pronunciation`, `cmudict` version `1.1.1`, a
  64-hex dictionary digest, `human_syllable_nuclei=false` and coverage `0.75`.
- **Controls**: exactly one each of `cv_candidate`,
  `constant_fold_mean_baseline` and `featureless_mean_baseline`.
- **Outcomes**: MAE/RMSE 0–10, bias −10–10, Pearson/Spearman −1–1, baseline MAE
  0–10, `nonfinite_count=0` and `sample_count=210`. These are admission bounds,
  not measured results.
- **Rights**: non-empty dataset/model/frontend/output-use/review references and
  `claims_qualified=false`. The schema does not assert that any real right has
  been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Candidate scorecard; MobileNetV3 row |
| `source:…/agent-neural/REPORT.md` | `f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73` | Detailed recipe, result and checkpoint reference |
| `source:…/run/train_mobilenet_rate_optimized.py` | `9e998642fe167437291bd3bbba538202c3e0056edd7c8483a4a8e53d68db768a` | Exact optimized training recipe |
| `source:…/run/train_mobilenet_rate.py` | `f8149f0158308f1cb2d267610f95fa522bf90d2f425249fd6b0ecdb67707acff` | Original full-resolution recipe |
| `source:…/run/mobilenet_rate_optimized_results.json` | `97389d23235bd853036f12c048b6e61e2b019f11aa42651a22be54f7dd7b69d8` | Recorded CV/timing; not reproduced |
| `source:…/run/mobilenet_rate_results.json` | `848f727771102bab83265034cf6acdd46bc8b78209e8fb1e0ef827bbf7cac146` | Older two-epoch screen; history only |
| `source:…/run/mobilenet_rate_optimized_progress.jsonl` | `2a1d7a236c94d0da1e6835eda0543a03efe9d1f99e3c65aac7a7b8ee67c74ffe` | Per-epoch trace |
| `source:…/run/mobilenet_original_run_interrupt.txt` | `6dcbe0bed125b92b1fa955f562922a46ec2b824c3bce09febdc72af33d47dfaf` | Interrupted-run history |
| `source:…/run/syl_eval_manifest.json` | `3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2` | Cohort shape/labels and declared audio digest |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `mobilenetv3-small-on-log-mels` row, Rate profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |

## Reproduce and verify

Standard library only. The commands are run from this directory.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` writes `contract.json`, `report.json`, `report.json.sha256` and
`SOURCES.sha256` three times and requires all four outputs to be
byte-identical. `verify.py` checks the committed bytes against a fresh
cold-start copy in a temporary tree, including the pinned source/boundary
symlinks, so path-dependent output cannot pass by accident.

## Non-claims

- No MobileNetV3 weight, checkpoint or state dict is present.
- No PyTorch, torchvision or librosa runtime is imported or executed.
- No audio signal, feature array, model weight or log-mel cache is read or
  decoded.
- No transcript text, syllable label or prediction is extracted, used or
  scored.
- No CV, accuracy, timing or baseline result is reproduced.
- No listening, device timing, benchmark, pipeline or release claim is made.
- No provider, registry, descriptor, public ABI, shared build or CI change
  exists.
- The historical negative result is context, not a local result or a product
  decision.
- A syllables/second estimate is not a preferred speed factor or a TSM setting.
