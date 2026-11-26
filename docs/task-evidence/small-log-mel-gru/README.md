<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SMALL-LOG-MEL-GRU — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`small-log-mel-gru` (`component_id=small-log-mel-gru`, title "Small log-mel
GRU"). Decision: **DEFER** before any implementation or intake step;
`status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute a complete GRU weight set, PyTorch, librosa, an audio signal, AMI audio
or annotations, CMUdict, a syllable label, a log-mel feature cache or an
inference path. It never decodes an audio clip and never loads or decodes a
model checkpoint. The one final-fold checkpoint file that exists is read only
for a whole-file SHA-256 and byte count. The 210 declared clip files are
`stat`-checked for presence, not opened. Only
`docs/task-evidence/small-log-mel-gru/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed-v0
behavior changes.

## Exact external blocker

The complete trained weights, feature cache and exact runtime are **absent**:

- Only `small_gru_last_fold.pt` exists (SHA-256
  `8740b3078433f758c9d0b3106d5de40beae8653a1c9cc3ac49edb1a65a114e7f`,
  27,792 bytes). The recipe saves only the last model after the fold loop, so
  folds 0–3 have no checkpoint. The published out-of-fold predictions cannot
  be reproduced from stored weights.
- The historical runtime is Python 3.10.13 with torch 2.2.2 and librosa. The
  `data/envs/sylnet-py310` environment is absent, and the available Python
  3.10.13/3.11.5/3.12.16 interpreters expose no `torch` or `librosa`. Exact
  librosa, NumPy, SciPy and SoundFile versions and wheel hashes were never
  recorded, and `torch.use_deterministic_algorithms` was not enabled.
- The 401×24 log-mel feature tensor was cached in memory and never persisted.
  The front end depends on undocumented librosa defaults and an unpinned
  version, so the feature cache cannot be reconstructed bit-exactly.
- The historical cohort is one AMI EN2003a meeting (210 four-second windows).
  Reference syllables are transcript/CMUdict 1.1.1-derived, not human
  syllable-nucleus labels. AMI audio/annotation and CMUdict terms are not
  reviewed here.
- The training script, trained weights and dependencies have no staged license,
  notice or product-use decision.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Four missing fold state dicts (or one checkpoint plus a bit-exact retraining recipe), with SHA-256/byte counts and a reviewed trained-weight license/terms decision. Only the final fold is present. |
| `BLK-02` | A locked offline Python 3.10.13 / torch 2.2.2 / librosa runtime with every wheel hash, install/import digest, deterministic algorithms, seed 20261101 and 1/1 threads. |
| `BLK-03` | The exact persisted 401×24 log-mel feature cache with SHA-256/byte count, or a pinned front-end that reproduces the cache digest. |
| `BLK-04` | A rights-cleared, multi-meeting, speaker-disjoint rate cohort with reviewed AMI/annotation/CMUdict terms, checked syllable labels, language/speaker groups and source timestamps. |
| `BLK-05` | A reproduced five-fold CV on that cohort with a frozen scorer, constant baseline, fold stability, finite-output and adverse/missing/nonfinite controls. |
| `BLK-06` | Exact Rate-profile mapping/buffering/condition/preservation evidence, target-device timing/resources, and a separate OFF-by-default provider intake after the earlier gates clear. |

**Reopen condition.** A caller supplies the exact source and license bundle,
all five checkpoints (or a bit-exact recipe), a locked offline runtime with
wheel hashes, the persisted feature cache, a rights-cleared multi-meeting
cohort, a reproduced CV/control result, the exact Rate-profile protocol and
target-device measurements, then records a separate opt-in intake with an OFF
default and independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one five-fold chronological CV run of a
6,113-parameter causal unidirectional log-mel GRU on 210 AMI EN2003a windows.
It is transcribed with its original scope and is **not rerun, not merged task
evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | small causal unidirectional GRU rate regressor |
| Architecture | `TinyRateGRU`: GRU input 24, hidden 32, 1 layer, unidirectional; head 32→16 ReLU→1 Softplus |
| Parameters | 6,113 |
| Input | 401 frames × 24 mel bins; 25 ms FFT, 10 ms hop; full 4 s clip; fold-local train mean/std |
| Runtime | Python 3.10.13, torch 2.2.2, CPU, 1 thread, 1 inter-op thread |
| Training | 30 epochs/fold, batch 16, Adam `lr=1e-3`, `weight_decay=1e-4`, seed 20261101 |
| Cohort | 210 four-second windows, one AMI EN2003a meeting, 64,000 samples/window |
| OOF MAE / RMSE | `1.1418471336364746` / `1.4151802062988281` syll/s |
| OOF bias / Pearson / Spearman | `-0.06459982693195343` / `0.12446770109689413` / `0.08822100920951738` |
| Constant-fold-mean baseline | MAE `1.1604056358337402`, RMSE `1.430286169052124` |
| Fold MAE | `1.0375840663909912`, `1.3106143474578857`, `1.0556423664093018`, `1.0843007564544678`, `1.2210943698883057` |
| Model-only CPU batch | median `0.7324007858100924` ms/clip, excludes features |
| Final-fold checkpoint | `small_gru_last_fold.pt`, 27,792 bytes, hashed only |
| Device / listening / preference | absent |

The historical finding is that the tiny GRU was cheap but only weakly ranked
rate on this single-meeting pilot: its MAE barely improved on the constant
baseline and its Pearson correlation was `r=.124`. A 1.142 syll/s error is not
a preferred speed factor, a TSM setting, a listener preference or a product
claim. The result is quoted only to explain why the task stays deferred.

## What this package actually verifies

1. **Source/recipe presence and exact pins.** The research README, detailed
   report, training script, results JSON, cohort manifest, final-fold
   checkpoint, inventory row, Rate profile and SDK delivery plan are pinned by
   SHA-256. The script contains every required recipe element: `TinyRateGRU`,
   GRU 24/32/1 unidirectional, 32→16→1 head with ReLU and Softplus, seed
   20261101, 1/1 threads, 30 epochs, batch 16, Adam settings, five
   chronological folds, exact log-mel arguments and the checkpoint save. This
   is provenance, not a weight or runtime qualification.
2. **Absence evidence.** Sixteen fixed workspace/worktree probes and four fixed
   home-cache/runtime probes are checked (no recursive workspace walk). All are
   absent. The final-fold checkpoint is present and pinned; its scope is
   explicitly final-fold-only. `reference.build_report()` and `verify.py`
   raise or fail if missing fold/feature/runtime artifacts later appear, so a
   stale "absent" claim cannot be shipped.
3. **Deterministic model arithmetic.** Pure-integer GRU and head parameter
   arithmetic is computed with the standard library only and must sum to
   6,113. This is an architecture reference, not a weight load or inference.
4. **Deterministic front-end arithmetic.** Pure-integer log-mel geometry
   (64,000 samples → 401 frames, 201 FFT bins, 24 mel bands, 9,624 values per
   window, 2,021,040 cohort values) is computed with the standard library
   only. This is a geometry reference, not feature extraction.
5. **Recorded-prediction consistency.** The 210 published OOF prediction rows
   are checked for finite values, five 42-row folds and aggregate
   MAE/RMSE/bias/Pearson agreement within `1e-6`. This is arithmetic
   provenance, not a reproduced CV, model execution or independent result.
6. **Admission boundary.** A caller-supplied rate-cohort manifest has a strict,
   task-local schema. Every malformed, missing, invalid, nonfinite, aliased,
   duplicated, out-of-range or non-integral control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
7. **Rate-profile accounting.** Source/output mapping, duration,
   pitch/transient audibility, playback buffering, 1×/rate changes, unfamiliar
   speech/music/silence, rebuffer/drift/final partial window, timestamp-tied
   pause/filler decisions and the preferred-speed policy are each recorded as
   **blocked**.
8. **Quality and timing accounting.** CV accuracy, fold stability, baseline
   comparison and finite/adverse controls are separate blocked outcomes;
   feature extraction, model-only latency, end-to-end p95 and device
   deadline/resources are separate blocked timing rows. No value is inferred
   from the historical run or from a sibling estimator task.
9. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README, the merged
   MobileNetV3 log-mel sibling, the Distil-Wav2Vec2 sibling and the dynamic-int8
   sibling are pinned by SHA-256 and verified unchanged.

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

## Release gates

All eight gates are blocked and `qualifies=false`:

| Gate | Blocked condition |
| --- | --- |
| `RG-01` | Source revision and license/notice/product-use provenance are incomplete. |
| `RG-02` | Complete five-fold trained weights are absent; only the final fold exists. |
| `RG-03` | No pinned deterministic runtime with wheel hashes and deterministic algorithms. |
| `RG-04` | No persisted log-mel feature cache or pinned reproducible front end. |
| `RG-05` | No rights-cleared multi-meeting cohort or checked human/label policy. |
| `RG-06` | No reproduced CV, baseline, fold-stability or finite/adverse controls. |
| `RG-07` | No Rate-profile, listening or target-device timing evidence. |
| `RG-08` | No OFF-by-default provider intake or independent exact-head release review. |

## Admission contract (task-local; not an SDK, GRU or Rate contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `architecture`, `checkpoints`,
  `runtime`, `frontend`, `audio`, `labels`, `controls`, `outcomes`, `rights`.
  Unknown and missing fields are rejected.
- **Architecture**: exactly `TinyRateGRU`, random initialization,
  `pretrained=false`, input shape `[401,24]`, one output class, softplus and
  6,113 parameters.
- **Checkpoints**: exactly five folds (`0`–`4`), unique 64-hex SHA-256 digests
  and positive byte counts. Duplicate folds or digests are rejected.
- **Runtime**: Python `3.10.13`, torch `2.2.2`, pinned
  librosa/NumPy/SciPy/SoundFile versions, CPU, one intra-op and one inter-op
  thread, deterministic algorithms on, offline on and seed `20261101`.
- **Frontend**: 16,000 Hz, 64,000 samples, `n_fft=400`, `hop_length=160`,
  24 mel bands, power `2.0`, log offset `1e-10`, center padding, fold-train
  mean/std and a 64-hex feature-cache digest. No resize stage is admitted.
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
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Candidate scorecard; GRU row |
| `source:…/agent-neural/REPORT.md` | `f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73` | Detailed recipe, result and checkpoint reference |
| `source:…/run/train_small_gru.py` | `dba40141ca2a6d74f98a814e8c5fa8e3762b550e4d42233394978f1508e37291` | Exact training and fold recipe |
| `source:…/run/small_gru_results.json` | `9206b6ff1fff8dd25ec511b88c2227178f67f95d603521370c460427f7cf15ef` | Recorded CV/timing/OOF rows; not reproduced |
| `source:…/run/syl_eval_manifest.json` | `3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2` | Cohort shape/labels and declared audio digest |
| `source:…/run/small_gru_last_fold.pt` | `8740b3078433f758c9d0b3106d5de40beae8653a1c9cc3ac49edb1a65a114e7f` | Final-fold bytes; hashed only, never loaded |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `small-log-mel-gru` row, Rate profile |
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

- No complete five-fold GRU weight set is present; only one final-fold torch
  checkpoint file is hashed, never loaded or decoded.
- No PyTorch or librosa runtime is imported or executed.
- No audio signal is decoded and no log-mel feature array or model weight is
  loaded or executed.
- No transcript text or syllable label is extracted or used; no new model
  prediction is produced or scored.
- Published OOF prediction rows are checked only for aggregate arithmetic
  consistency; that check is provenance, not a reproduced CV result.
- No listening, device timing, benchmark, pipeline or release claim is made.
- No provider, registry, descriptor, public ABI, shared build or CI change
  exists.
- The historical weak result is context, not a local result or a product
  decision.
- A syllables/second estimate is not a preferred speed factor or a TSM setting.
