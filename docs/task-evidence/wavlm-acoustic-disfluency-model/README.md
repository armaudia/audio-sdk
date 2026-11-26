<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL — WavLM frame-detector readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`wavlm-acoustic-disfluency-model` (`component_id=wavlm-acoustic-disfluency-model`,
title "WavLM acoustic disfluency model"). Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download, load or
execute `amritkromana/disfluency_detection_from_audio`, `disfluency_acoustic.pt`,
`acoustic.pt`, `microsoft/wavlm-base`, `microsoft/wavlm-base-plus`,
PyTorch, Transformers, an audio signal, AMI audio/annotations, Switchboard
data, a frame disfluency label, a WavLM hidden state or any inference path. It
reads no weight byte and scores no frame. Only whole-file SHA-256 and byte-count
provenance checks are performed on the pinned research and source artifacts;
none is used as a signal, weight or model. It records the exact missing
artifacts and rights, probes fixed workspace/environment/home-cache paths to
evidence absence, and defines a fail-closed admission boundary for a future
frame-level disfluency cohort. Only
`docs/task-evidence/wavlm-acoustic-disfluency-model/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or installed
v0 behavior changes.

## Exact external blocker

The upstream source is present but **unlicensed**, and the checkpoint, backbone
assets and runtime are **absent**:

- The source checkout is present at `data/checkouts/disfluency_detection_from_audio`
  on commit `a2512e5fa0d2bf200861f049a2f08a2600c3f27c`. It contains no
  `LICENSE`, `LICENCE`, `COPYING` or `NOTICE` file; its README, `demo.py` and
  `models.py` declare no license, terms or redistribution grant. The Google
  Drive weight payload is described without terms.
- The 377,639,565-byte `disfluency_acoustic.pt` checkpoint
  (`acoustic.pt`, Google Drive id `1wWrmopvvdhlBw-cL7EDyih9zn_IJu5Wr`,
  SHA-256 `8724aaac4da9ae4d6e04f55dc394650a2517fbf529f5f4cd00b1353c74547036`)
  is absent. No local file exists at the runner path, the checkout
  `demo_models/` path, `data/models`, `data/envs` or the Hugging Face/torch
  caches. Nothing was downloaded or reconstructed.
- The repository instantiates
  `WavLMModel.from_pretrained('microsoft/wavlm-base')`. The smoke instantiated
  the architecture from a local `microsoft/wavlm-base-plus` config at revision
  `4c66d4806a428f2e922ccfa1a962776e232d487b` (config 2,232 bytes, SHA-256
  `fea6df1c2700a3954fc07e70588aecc9055eeb28db2ff57151a2db0d19180ed4`) because
  the checkpoint supplies all state. Neither backbone config/weights are
  present, and the Base+ model card records a **null** license field.
- The Python 3.10.13 / torch 2.2.2 / transformers 4.40.2 runtime is absent.
  `data/envs` is absent and the pinned interpreter exposes no `torch` or
  `transformers`. The upstream README separately declares pandas 1.5.0,
  torch 1.12.1, transformers 4.22.2, torchaudio 0.12.1,
  whisper_timestamped 1.14.4 and gdown 5.1.0. No import, load or inference was
  attempted.
- No rights-cleared frame-labeled cohort is staged. The historical run used one
  AMI EN2003a crop as an unlabeled smoke. AMI supplies no matching framewise
  FP/RP/RV/RS/PW labels; the upstream labels derive from Switchboard and a
  corrected annotation archive whose LDC/annotation terms are unreviewed here.
  No audio byte was read for this package.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | A written, reviewed license/terms grant for the source repository and the Google Drive checkpoint, plus a product-use and redistribution decision. |
| `BLK-02` | The immutable 377,639,565-byte `acoustic.pt` checkpoint with SHA-256 `8724aaac…`, an acquisition record and reviewed weight terms. |
| `BLK-03` | The exact WavLM backbone configuration/weights used at training (or proof that the Base+ smoke configuration is compatible), with per-file digests, a 40-hex revision and reviewed terms. |
| `BLK-04` | A locked offline Python 3.10.13/torch 2.2.2/transformers 4.40.2 runtime with wheel hashes, an install/import digest and a clean-room deterministic load. |
| `BLK-05` | A rights-cleared, speaker/meeting-disjoint cohort with verified per-frame FP/RP/RV/RS/PW labels, reviewed corpus/annotation terms, groups and timestamps. |
| `BLK-06` | A reproduced per-label quality/control, Rate-profile, target-timing and separate OFF-by-default provider-intake bundle. |

**Reopen condition.** A caller supplies the reviewed source/checkpoint grant,
the exact checkpoint and backbone assets with every digest, a locked offline
runtime, a rights-cleared frame-labeled cohort, reproduced per-label quality
and adverse controls, the exact Rate-profile protocol, target-device
measurements, then records a separate opt-in intake with an OFF default and
independent exact-head review. Until then this task stays `DEFER`.

## Historical execution: provenance only

The pinned research bundle contains one successful **inference-only smoke** of
the acoustic WavLM head on a single 4 s AMI crop. It is transcribed with its
original scope and is **not rerun, not merged task evidence, not used for
evidence and not a qualification**.

| Field | Recorded value |
| --- | --- |
| Candidate | `amritkromana/disfluency_detection_from_audio` acoustic WavLM head |
| Repository commit | `a2512e5fa0d2bf200861f049a2f08a2600c3f27c` |
| Checkpoint | `disfluency_acoustic.pt`, 377,639,565 bytes, SHA-256 `8724aaac…` |
| Architecture | WavLM backbone + `Linear(768,5)`, sigmoid, threshold `0.5` |
| Config used | `microsoft/wavlm-base-plus` local config, revision `4c66d48…` |
| Labels | `FP`, `RP`, `RV`, `RS`, `PW` (20 ms frames; 199 outputs for 4 s) |
| Sample | `EN2003a_0004`, 4.0 s, AMI EN2003a crop |
| CPU model-only time | `180.35912496270612` ms (one observation) |
| State load | all checkpoint keys loaded; 0 missing, 0 unexpected |
| Positive frames | `FP=0`, `RP=10`, `RV=0`, `RS=0`, `PW=3` |
| Accuracy / F1 / onset | absent; AMI has no matching framewise labels |
| License / terms | absent for repository and checkpoint |
| Device / listening / preference | absent |

The recorded counts are **not** precision, recall, F1, a detection result, a
preferred speed factor or a product claim. The checkpoint is never loaded,
scored or promoted here. One unlabeled AMI crop is recorded as existing in the
research bundle but is not read.

## What this package actually verifies

1. **Source presence and exact pins.** The research scorecard, detailed neural
   report, smoke runner/output, WavLM Base+ source record, shared AMI manifest,
   upstream README/models/demo and the checkout HEAD commit are verified. The
   source contains the model definition, the five labels, the Google Drive
   weight id and no license statement.
2. **Absence evidence.** Fifteen fixed workspace probes and four fixed
   home-cache probes are checked (no recursive workspace walk). All are absent.
   Any later-present path makes `reference.build_report()` and `verify.py` fail,
   so a stale "absent" claim cannot ship.
3. **Unlicensed-source accounting.** The checkout is present at the exact
   commit but has no license file or declaration; ART-02 is present yet blocked,
   and `RG-01` cannot open on source presence alone.
4. **Admission boundary.** A caller-supplied frame-level cohort manifest has a
   strict, task-local schema. Every malformed, missing, invalid, nonfinite,
   aliased, duplicated, out-of-range or non-integral control is rejected before
   any state change. One structural control is admitted to prove the validator
   is not blanket-rejecting, and is labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights or invokes a model.
5. **Rate-profile accounting.** Source/output mapping, duration, pitch/transient
   audibility, playback buffering, 1×/rate changes, unfamiliar speech/music/
   silence, rebuffer/drift/final partial window, timestamp-tied pause/filler
   decisions and preservation are each recorded as **blocked**.
6. **Quality and timing accounting.** Per-label precision/recall/F1,
   onset/offset delay, stratified FN/FP, nonspeech separation and
   missing/adverse/nonfinite controls are separate blocked outcomes. Latency,
   RTF, device deadline and resources are separate blocked timing rows. No value
   is inferred from the smoke or from a sibling estimator task.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and four
   merged sibling evidence packages are pinned by SHA-256 and verified
   unchanged.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Measure source/output mapping and duration | blocked | The candidate is a frame classifier, not a TSM renderer; no mapping or rendered duration exists. |
| Measure pitch and transient audibility | blocked | No rendered output, F0/transient metric or listening result exists. |
| Measure playback buffering | blocked | No playback chain, queue, fill/flush or buffering measurement exists. |
| Include 1× and rate changes | blocked | No speed-factor comparison exists; frame probabilities are not a speed factor. |
| Include unfamiliar speech, music and silence | blocked | One AMI speech crop only; no unfamiliar/language/music/silence coverage. |
| Include rebuffer, drift and final partial window | blocked | No stream, rebuffer, clock-drift or partial-window behavior was measured. |
| Tie pause/filler decisions to source timestamps and measure preservation | blocked | No timestamped decision, deletion policy or preservation measurement exists. |
| Map detections to a reviewed preferred-speed policy | blocked | A disfluency detector is not a rate estimator; no preference labels or policy exist. |

## Admission contract (task-local; not an SDK, WavLM or Rate contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source`, `weights`,
  `backbone`, `runtime`, `feature_extractor`, `labels`, `audio`, `controls`,
  `outcomes`, `rights`. Unknown and missing fields are rejected.
- **Source**: exactly `amritkromana/disfluency_detection_from_audio`, commit
  `a2512e5f…` (40 lowercase hex), a non-empty reviewed `license_id` (not
  `none`/`unlicensed`/`unknown`) and a non-empty license reference.
- **Weights**: exactly `acoustic.pt`, SHA-256 `8724aaac…`, exactly 377,639,565
  bytes, and a non-empty terms reference.
- **Backbone**: exactly `microsoft/wavlm-base` or `microsoft/wavlm-base-plus`,
  a 40-hex revision, a non-zero 64-hex config digest and a non-empty license id.
- **Runtime**: Python `3.10.13`, torch `2.2.2`, transformers `4.40.2`, CPU and
  offline on.
- **Feature extractor**: 16,000 Hz, 20 ms frames, normalization on.
- **Labels**: exactly `["FP","RP","RV","RS","PW"]`, a non-empty human frame-label
  source and `human_verified=true`.
- **Audio**: 1–4,096 unique windows with canonical absolute paths, non-zero
  64-hex digests, `language` 2–3 lowercase letters, speaker/meeting slugs,
  nonnegative finite starts, exactly four-second spans and 16,000 Hz.
- **Controls**: exactly one each of `human_frame_label_baseline`, `candidate`
  and `all_negative_baseline`, with unique ids.
- **Outcomes**: positive frame count 1–100,000, `nonfinite_count=0`, and exactly
  one ordered per-label row for each of the five labels with precision/recall/F1
  in `[0,1]` and finite onset delay in `[-5000,5000]` ms. These are admission
  bounds, not measured results.
- **Rights**: non-empty dataset/source/weights/label/output-use/review
  references and `claims_qualified=false`. The schema does not assert that any
  real right has been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity `{id,title,component,mode,repository,depends_on}` gates
anything. `status`, `owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` never gate and the full `TASKS.json` bytes are never hashed.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/tsm-followup-20261101/README.md` | `01618a85…` | Candidate scorecard, line 32 |
| `source:…/agent-neural/REPORT.md` | `f2f1b552…` | Detailed smoke and no-license finding |
| `source:…/run/run_acoustic_disfluency_smoke.py` | `b748fdc6…` | Exact smoke runner |
| `source:…/run/disfluency_acoustic_smoke.json` | `a97735da…` | Recorded smoke values |
| `source:…/run/wavlm-base-plus_source.json` | `5210619f…` | Config revision/digests, null license |
| `source:…/run/syl_eval_manifest.json` | `3c7b3731…` | Shared 210-window AMI shape |
| `source:data/checkouts/disfluency_detection_from_audio/README.md` | `1b6cb882…` | Weight id, labels, no license |
| `source:data/checkouts/disfluency_detection_from_audio/models.py` | `8b079699…` | Exact architecture |
| `source:data/checkouts/disfluency_detection_from_audio/demo.py` | `e526d9fe…` | Inference contract |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | Rate profile and partial status |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f263133…` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50…` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f…` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965a…` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74…` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba5…` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc9…` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cd…` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb…` | Unchanged build surface |
| `docs/task-evidence/dynamic-int8-wav2vec2-base/*` | `3da67723…`, `6f166a5b…` | Merged rate sibling boundary only |
| `docs/task-evidence/distil-wav2vec2-adult-child-ridge/*` | `adb75188…`, `ff7b70f3…` | Merged rate sibling boundary only |
| `docs/task-evidence/silero-vad-pause-duration-rules/*` | `b6e422c5…`, `9aebd32c…` | Merged pause sibling boundary only |
| `docs/task-evidence/usc-mrate/*` | `28f837e3…`, `d74c03b0…` | Merged rate sibling boundary only |

The shared board row is read only by `verify.py` and the unit tests, and only
through the stable projection above, so a board state transition cannot promote
or block this package's claims.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Model/weight/backbone/runtime/corpus/annotation boundary; no vendored text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, source/license inspection, absence checks, admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/wavlm-acoustic-disfluency-model` with Python 3.12 and
stdlib only:

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

Current counts: 15 workspace absence probes plus 4 home-cache probes (0
present), 8 required artifacts (2 present; 1 of those rights-blocked; 6 absent),
6 open blockers, 77 rejected admission controls, 1 schema-only control, 8
blocked Rate rows, 4 blocked quality outcomes, 4 blocked timing rows, 8 blocked
gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Pin the exact source tree and commit and stage a reviewed license/terms grant plus a product-use/redistribution decision. |
| `RG-02` weights checkpoint and backbone assets | blocked | Supply the immutable checkpoint and exact backbone config/weights with byte counts, digests, revisions and terms. |
| `RG-03` pinned runtime and offline load | blocked | A locked offline runtime loads the checkpoint, verifies every state key and records deterministic repeats. |
| `RG-04` rights-cleared frame-labeled cohort | blocked | A permitted, speaker/meeting-disjoint cohort with verified framewise FP/RP/RV/RS/PW labels and reviewed terms. |
| `RG-05` frame-level quality and controls | blocked | Reproduce per-label precision/recall/F1, onset/offset delay, stratified FN/FP, nonspeech and missing/adverse/nonfinite controls. |
| `RG-06` Rate-profile coverage and preservation | blocked | Score mapping, duration, pitch/transient, buffering, rate changes, unfamiliar speech/music/silence, rebuffer/drift, final partial window and timestamp-tied pause/filler preservation. |
| `RG-07` target timing, resources and deadlines | blocked | Measure paced p50/p95/p99 latency, RTF, CPU/memory/energy and deadline behavior on the intended device. |
| `RG-08` provider intake, public surface and release | blocked | A separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

The merged Distil-Wav2Vec2 and dynamic-int8 wav2vec2 packages are different
SSL encoders with trained rate heads; their features, synthetic rate results
and caller protocols are never substituted here. The WavLM Base+ + ridge pilot
is a separate rate estimator, not this frame-level disfluency checkpoint. The
Silero/pause and USC mrate packages are different pause/rate boundaries. AMI,
Switchboard, LDC, the corrected annotation archive and the Google Drive
checkpoint are not pooled or reinterpreted as disfluency evidence.

## Expected digest

`report.json` SHA-256:
`5d9c69ec8365d65c3ef437494318b74ef18b5524be14fcbf740ea9ff29b29532`.
