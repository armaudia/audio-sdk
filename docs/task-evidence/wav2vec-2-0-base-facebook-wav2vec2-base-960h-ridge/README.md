<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE — wav2vec2-base-960h + ridge readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge` (title "wav2vec 2.0 base
(`facebook/wav2vec2-base-960h`) + ridge"). Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute `facebook/wav2vec2-base-960h`, `model.safetensors`, a ridge head,
PyTorch, Transformers, scikit-learn, numpy, an audio signal, AMI
audio/annotations, CMUdict, a syllable label or any inference path. It reads no
`.npz` array and scores no embedding. Only whole-file SHA-256 and byte-count
provenance checks are performed on the pinned research artifacts, and none is
used as a signal, a model or a head. It records the exact missing artifacts and
rights, probes fixed workspace/environment/home-cache paths to evidence
absence, and defines a fail-closed admission boundary for a future FP32 rate
cohort. Only `docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge/`
is written; no provider, registry, descriptor, public header/ABI, shared CMake,
CI workflow or installed v0 behavior changes.

## Exact external blocker

The upstream snapshot, the exact runtime and a serialized ridge head are
**absent**:

- The research source record pins `facebook/wav2vec2-base-960h` at revision
  `22aad52d435eb6dbaf354bdad9b0da84ce7d6156`, Apache-2.0, 94,371,712
  parameters, `model.safetensors` 377,607,901 bytes with SHA-256
  `8aa76ab2243c81747a1f832954586bc566090c83a0ac167df6f31f0fa917d74a`.
  No local file exists at the runner's model checkpoint directory,
  `data/checkouts`, `data/models`, or `~/.cache/huggingface/hub`.
- The historical pilot fitted `StandardScaler` + `Ridge(alpha=10)` per fold on
  mean-pooled last-hidden-state features and stored only predictions in
  `wav2vec2-base-960h_results.json`. No joblib/npz head, scaler statistics or
  fold index was serialized. `wav2vec2-base-960h_fp32_embeddings.npz` is a
  derived feature archive, not a head.
- The required runtime — Python 3.10.13, torch 2.2.2, transformers 4.40.2,
  scikit-learn and numpy — is absent. The available 3.11.5 interpreter exposes
  no `torch`, `transformers` or scikit-learn for this task, and the historical
  `data/envs/sylnet-py310` environment is absent. No import, load, fit or
  inference was attempted.
- The historical cohort is one AMI EN2003a meeting (210 four-second windows).
  Reference syllables are transcript/CMUdict 1.1.1-derived, not human
  syllable-nucleus labels. AMI audio/annotation and CMUdict terms are not
  reviewed here, and no audio byte is read.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable `facebook/wav2vec2-base-960h` snapshot at revision `22aad52d…`: `model.safetensors`, `config.json`, preprocessor/feature-extractor configs and tokenizer assets, with per-file byte counts and SHA-256, plus the reviewed model card, license/notice bundle and redistribution/product-use decision. |
| `BLK-02` | A locked offline runtime (Python 3.10.13, torch 2.2.2, transformers 4.40.2, scikit-learn, numpy, 1/1 threads, deterministic algorithms) with wheel hashes and an install/import digest. |
| `BLK-03` | A serialized per-fold ridge head (StandardScaler + Ridge alpha=10) with SHA-256/byte count, or a reproducible head-training record pinning fold boundaries, feature dims, scaler statistics and the resulting artifact digest. |
| `BLK-04` | A rights-cleared, speaker/meeting-disjoint speech-rate cohort with permitted AMI/corpus and CMUdict terms, human-checked syllable labels, language/speaker groups and source-timestamp provenance. |
| `BLK-05` | A fresh FP32 run on that cohort with reproduced accuracy, nonnegative-rate and finite-output checks, constant-fold-mean/zero-rate baselines and adverse/missing controls. |
| `BLK-06` | Exact Rate-profile mapping/buffering/condition/preservation evidence, target-device timing/resources, and a separate OFF-by-default provider intake after the earlier gates clear. |

**Reopen condition.** A caller supplies the immutable upstream snapshot with
every digest, the reviewed terms, a locked runtime that loads offline, a
reproducible/pinned ridge head, a rights-cleared cohort, a reproduced FP32
result with baselines and adverse controls, the exact Rate-profile protocol and
target-device measurements, then records a separate opt-in intake with an OFF
default and independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The research record contains one successful offline evaluation of a frozen
wav2vec2-base encoder plus a ridge rate head, applied to 210 four-second AMI
windows. It is transcribed with its original scope and is **not rerun, not
merged task evidence, not used for evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | `facebook/wav2vec2-base-960h` frozen SSL encoder + ridge |
| Revision / license | `22aad52d435eb6dbaf354bdad9b0da84ce7d6156` / Apache-2.0 per source record |
| Weights | 377,607,901 bytes; SHA-256 `8aa76ab2…`; 94,371,712 parameters |
| Runtime | Python 3.10.13, torch 2.2.2, transformers 4.40.2, CPU |
| Feature / head | Mean-pooled last hidden state; StandardScaler + `Ridge(alpha=10)`, refit in each of five chronological folds |
| Cohort | 210 four-second windows, one AMI EN2003a meeting, 64,000 samples/window |
| FP32 CV (recorded) | MAE `0.5985195144024282`, RMSE `0.7615091902895115`, bias `0.0002114877787809256`, r `0.8517433538738032` |
| FP32 nonnegative (recorded) | MAE `0.5926580504015446`, RMSE `0.7516435944561558`, bias `0.006072951779664482`, r `0.8538743418149306`; 2 negative raw predictions, min `-0.6596407890319824`, max `7.112451076507568` |
| Training-fold mean baseline (recorded) | MAE `1.1604056617480316`, RMSE `1.4302861304687302`, r `-0.23446437948354898` |
| Encoder timing (recorded) | mean `173.837601348281` ms, p50 `172.8633120073937` ms, p95 `184.23033093858973` ms, RTF `0.04345940033707025` per 4 s clip |
| Device / listening / preference | absent |

The historical finding is that frozen wav2vec2-base features plus a ridge head
gave the strongest rate estimate on the pilot set, but it is an estimator:
`0.593` syllables/second MAE is not a preferred speed factor, a TSM setting, a
listener preference or a product claim. The archived FP32 embedding file is
listed only by whole-file digest and is never decoded, loaded or scored.

## What this package actually verifies

1. **Source/recipe presence and exact pins.** The research README, detailed
   report, exact FP32 runner, nonnegative scoring script, source record,
   results JSON, cohort manifest and derived FP32 embedding archive are pinned
   by SHA-256. The runner contains all six required recipe snippets (1/1
   threads, StandardScaler + Ridge alpha=10, mean pooling, local-only load,
   pinned revision) and the scorer contains the nonnegative clip. This is
   provenance, not a weight, head or runtime qualification.
2. **Absence evidence.** Eighteen fixed workspace/worktree probes and four
   fixed home-cache probes are checked (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any
   probe later appears, so a stale "absent" claim cannot be shipped.
3. **Admission boundary.** A caller-supplied FP32 rate cohort manifest has a
   strict, task-local schema. Every malformed, missing, invalid, nonfinite,
   aliased, duplicated, out-of-range or non-integral control is rejected before
   any state change. One structural control is admitted to prove the validator
   is not blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
4. **Rate-profile accounting.** Source/output mapping, duration, pitch/transient
   audibility, playback buffering, 1×/rate changes, unfamiliar speech/music/
   silence, rebuffer/drift/final partial window, timestamp-tied pause/filler
   decisions and the preferred-speed policy are each recorded as **blocked**.
5. **Quality and timing accounting.** FP32 accuracy, nonnegative-clipped
   accuracy, finite-output bounds and constant-baseline comparison are separate
   blocked outcomes; p95, RTF, device deadline and resources are separate
   blocked timing rows. No value is inferred from the historical run or from a
   sibling estimator task.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and the
   merged Distil-Wav2Vec2 and dynamic-int8 sibling packages are pinned by
   SHA-256 and verified unchanged.

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

## Admission contract (task-local; not an SDK, wav2vec2 or Rate contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `encoder`, `weights`,
  `runtime`, `feature_extractor`, `head`, `audio`, `labels`, `controls`,
  `outcomes`, `rights`. Unknown and missing fields are rejected.
- **Encoder**: exactly `facebook/wav2vec2-base-960h`, revision
  `22aad52d…` (40 lowercase hex), `license_id="apache-2.0"` and the pinned model
  card SHA-256 `fc52a0…`.
- **Weights**: exactly `config.json`, `feature_extractor_config.json`,
  `model.safetensors`, `preprocessor_config.json`, `tokenizer_config.json` and
  `vocab.json`, each with the pinned byte count and SHA-256 plus a 64-hex terms
  digest. `model.safetensors` must be 377,607,901 bytes and
  `8aa76ab2…`; any extra or missing file is rejected.
- **Runtime**: Python `3.10.13`, torch `2.2.2`, transformers `4.40.2`, CPU,
  one intra-op and one inter-op thread, deterministic algorithms on, offline on.
- **Feature extractor**: 16,000 Hz, 64,000 samples, normalization on and the
  pinned preprocessor digest.
- **Head**: ridge, alpha `10`, standard scaler, five folds, an unsigned 32-bit
  seed and a 64-hex serialized-artifact digest.
- **Audio**: exactly 210 unique windows with canonical absolute paths, 64-hex
  digests, `language="en"`, speaker/meeting slugs, nonnegative finite start,
  exactly four-second spans, positive active duration and a finite reference
  rate in `[0, 20]`.
- **Labels**: `cmudict-first-pronunciation`, CMUdict `1.1.1`,
  `ami-orthographic`, `human_syllable_nuclei=false` and coverage `0.75`.
- **Controls**: exactly one each of `fp32_candidate`,
  `constant_fold_mean_baseline` and `zero_rate_baseline`.
- **Outcomes**: MAE/RMSE 0–10, bias −10–10, Pearson r −1–1, p95 0–60,000 ms,
  `nonfinite_count=0` and `sample_count=210`. These are admission bounds, not
  measured results.
- **Rights**: non-empty dataset/model/dictionary/output-use/review references
  and `claims_qualified=false`. The schema does not assert that any real right
  has been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Candidate scorecard; line 28 base FP32 finding |
| `source:…/agent-neural/REPORT.md` | `f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73` | Detailed FP32 result and runtime |
| `source:…/run/run_ssl_encoder_cv.py` | `09b7e3cc4ff5fa01768cd925f38d972b555f9864feaf38036fafac7c6350f660` | Exact FP32 encoder + ridge recipe |
| `source:…/run/score_nonnegative_heads.py` | `201f88580dfc3f0fe46d063d48a1fa306e1345c60c90581eac7a012c97512790` | Nonnegative clip recipe |
| `source:…/run/wav2vec2-base-960h_source.json` | `6d56532312237861170b63bcecaa8d9071b30f80e6be1195ff9dfc1436b436d6` | Upstream revision and file digests |
| `source:…/run/wav2vec2-base-960h_results.json` | `11c0aef3121857f71e037acbca64a2546d1f206a9271fd95922530b85267d9d1` | Recorded metrics/timing, not reproduced |
| `source:…/run/wav2vec2-base-960h_fp32_embeddings.npz` | `8e5a4aadd0b7d88b363658e82e72c087950dd40a378e6ebcdc451c1db9ad8c92` | Derived archive; not loaded |
| `source:…/run/syl_eval_manifest.json` | `3c7b3731cf6d2312e42e3333cae03bc631f6d1dbf557b773e134468c867897e2` | Cohort shape and labels |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `wav2vec-2-0-base-…-ridge` row, Rate profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/distil-wav2vec2-adult-child-ridge/README.md` | `adb751885024bcaab88a373602f3d19326cee356559d62b0cc334cbc25afceca` | Merged sibling boundary only |
| `docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json` | `ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4` | Merged sibling, not reused |
| `docs/task-evidence/dynamic-int8-wav2vec2-base/README.md` | `3da6772383eb9b44ccd8eeab4272bf69e4dbd2640f045e42c4fa6ed24f275533` | Merged int8 sibling boundary |
| `docs/task-evidence/dynamic-int8-wav2vec2-base/contract.json` | `ccc997cb695fde535c5408a91cd9f0e5ecdbd6cc1687f5abf82530944c5ef509` | Merged int8 sibling, not reused |
| `docs/task-evidence/dynamic-int8-wav2vec2-base/report.json` | `6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9` | Merged int8 sibling, not reused |

The shared board row is read only by `verify.py` and the unit tests, and only
through the stable projection `{id, title, component, mode, repository,
depends_on}`. `status`, `owner`, `claim`, `review`, `handoff`,
`blocked_reason` and `dispatch_priority` are excluded from gating, so a board
state transition cannot promote or block this package's claims. The full
mutable `TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Model/weight/head/runtime/corpus/dictionary boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge` with
Python 3.12 and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 18 workspace/worktree absence probes plus 4 home-cache probes
(0 present), 7 required artifacts (1 provenance source present, 6 blocked), 6
open blockers, 70 rejected admission controls, 1 schema-only control, 8 blocked
Rate rows, 4 blocked quality outcomes, 4 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Pin the exact source archive/tree, 40-hex revision and complete model card/license/notice set with independent terms review. |
| `RG-02` weights assets and head artifact | blocked | Supply the immutable weight snapshot with per-file digests and a reproducible/pinned ridge head. |
| `RG-03` pinned runtime and offline load | blocked | A locked offline runtime loads the snapshot, fits or loads the ridge head and records deterministic repeats. |
| `RG-04` rights-cleared rate corpus and labels | blocked | A permitted, speaker/meeting-disjoint cohort with reviewed corpus/dictionary terms and checked syllable labels. |
| `RG-05` FP32 accuracy, finite output and baselines | blocked | Reproduce the FP32 path with fixed folds, frozen scoring, finite-output checks and constant-fold-mean/zero-rate baselines. |
| `RG-06` Rate-profile condition coverage | blocked | Score mapping, duration, pitch/transient, buffering, rate changes, unfamiliar speech/music/silence, rebuffer/drift, final partial window and timestamp-tied pause/filler decisions. |
| `RG-07` target timing, resources and deadlines | blocked | Measure paced p95/p99 deadline, CPU/memory/energy and fill/flush on the intended device. |
| `RG-08` provider intake, public surface and release | blocked | A separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

The merged Distil-Wav2Vec2 package
(`docs/task-evidence/distil-wav2vec2-adult-child-ridge/`) is a different encoder
and ridge head; its synthetic rate results, features and caller-protocol are
never substituted here. The merged dynamic-int8 wav2vec2 package
(`docs/task-evidence/dynamic-int8-wav2vec2-base/`) is a quantization variant of
the same encoder; none of its int8 numbers, artifacts or gates are reused as
FP32 evidence. WavLM, SylNet, mrate, the small GRU and MobileNetV3 are
boundaries only; none is pooled or reinterpreted as wav2vec2-base + ridge
evidence.

## Expected digest

`report.json` SHA-256:
`1ce7faa0b87faa8a8782083bd23ba6dd5803f9bd45ae5ef2db9a8692b0858f48`.
