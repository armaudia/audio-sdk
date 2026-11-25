<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-DET-01 — speech activity detection evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`DET-01` (Speech activity detection, VAD/SAD; legacy family `F02`). It matches
the catalogued classic and ML method families, both named source leads (`S01`,
`S02`) and historical local or source-reported executions to existing
components. It creates **no new execution, model, corpus, provider, detector,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-DET-01`; independent reviewer not dispatched.
Claim base: audio-sdk `245d9ad3854d5dcddb223d686a45f2230a9dc5c3`; branch
`swarm/SDK-SURVEY-DET-01`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested` / `catalogued` with candidate census
and benchmark both `not_started`.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: energy/band statistics; fixed or adaptive noise floor | `fixed-rms-vad`, `adaptive-energy-vad`: held-out AMI FN/FP 62.95/25.35% and 33.15/21.58%; positive-span-only misses up to 16.97%; merged task-local 160-sample synthetic fixtures | Real AMI word intervals, synthetic fixtures and unlabeled audEERING gaps stay separate |
| Classic: GMM likelihoods; thresholds and hangover (`S01`) | `webrtc-vad`: held-out AMI FN 7.31%, FP 49.54% at 6.38 µs/20 ms frame; positive-span misses 0.0004–0.9662%; deterministic synthetic surrogate | No local WebRTC runtime, native parity or device timing; high false-alarm rate is preserved |
| Classic: voice-focused SpeexDSP VAD | `speexdsp-vad`: held-out AMI FN 2.45%, FP 77.03%; positive-span misses 0% | Low misses come with heavy overtriggering; not evidence of a good detector |
| Classic + ML: cheap gate with expensive-neural scheduler | `adaptive-energy-to-silero-cascade`, `adaptive-energy-silero-scheduler-implementation`: frozen policy FN 19.83%/FP 7.92% on AMI, 16.37% projected compute saved; 100% FN on the synthetic cross-environment split | Saved-decision replay only; no live pause/resume, warm-up or deadline evidence |
| ML: small causal frame classifiers / stateful streaming | `fast-vad-0-2-1`, `earshot-1-2-2`, `silero-vad-6-2-3-reference`, `silero-vad-v5-onnx-reference`: held-out AMI FN/FP 17.20/25.21%, 24.32/10.30%, 19.43/8.20%; positive-span misses 0–10.42% | No merged real-model task package; fast-vad FN ranged 1–100% across six synthetic recordings |
| ML: neural segmentation and larger classifiers (`S02`) | `pyannote-segmentation-vad` (blocked), `wav2vec2-xls-r-transformer-vad`, `cnn-bilstm-vad`, `crnn-vad`, `marblenet-vad`, `fsmn-vad`, `fireredvad`, `pulsevad`, `ten-vad` (feasibility/blocked) | No weights, checkpoint, adapter or local execution found; no capability inferred from a model card |
| ML: speech probability as collateral output | `rnnoise-speech-probability`, `speex-agc-and-activity-output`, `native-speex-ns-activity-shared-preprocessing`: exploratory AMI side diagnostic FN/FP 25.64/5.44% versus Silero 22.91/7.64% on three 60 s windows; model-free local surrogate | Adjacent diagnostic only; not the CLN-01 denoising pilot and not a general VAD result |
| ML: VAD-conditioned downstream policy | `silero-vad-pause-duration-rules`, `silero-vad-opensmile-small-regression-head`, `source-vad-conditioning-for-playback`: local synthetic Rate-profile packages and considered playback conditioning | Pause/turn/rate decisions are not speech-activity truth and do not gate audio |

`report.json` holds the full records: both catalogued branches, source-lead
mappings, component census checked against `INVENTORY.json`, comparison inputs,
controls, assets, local versus reported outcomes, acceptance mapping, gaps,
board links and all eight blocked release gates. Historical numbers are
transcribed verbatim from pinned reports with their original scope; they are
**not** rerun, pooled into a benchmark or promoted to a pass.

## Evidence classes and failure envelope

- **Historical local held-out real meeting:** three speaker-disjoint AMI
  Mix-Headset meetings with word-interval union, explicit unknown gaps and a
  20 ms projection. Desktop accelerated replay only.
- **Historical local paired synthetic:** six cross-environment recordings
  (517.75 s) with generated noise negatives and reused audEERING speech
  excerpts. Six rows are not six independent speakers.
- **Historical local positive-span only:** four audEERING recordings scored
  inside 588 positive spans; the complement is unknown, so false alarms, full
  accuracy, boundary scores, intervals and rankings are unavailable.
- **Historical local adjacent speech probability:** an exploratory RNNoise side
  diagnostic through a separate native path; not a general accuracy result.
- **Historical local synthetic fixtures:** merged task-local 160-sample
  model-free surrogates. Probabilities are uncalibrated analytic/logistic
  transforms, not detector posteriors.
- **Source-reported only:** WebRTC source, pyannote model card and corpus
  metadata. No exact checkout, weights, matched cohort or numeric parity
  follows from a claim.
- **Not present:** human listening, target-device timing, a new execution,
  real-model runtime in this task, clean-reference accuracy or parity. These
  classes are `false`, not inherited from an adjacent survey.
- The recorded failure envelope is adverse: WebRTC and SpeexDSP overtrigger
  heavily on AMI; the frozen adaptive-energy→Silero chain saved projected
  compute but missed **100%** of speech on the synthetic split; fast-vad's FN
  ranged **1–100%** across conditions. Compute savings and low positive-span
  misses do not establish a usable detector.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps without a component owner (`G01`, `G02`, `G03`,
`G04`, `G07`, `G10`, `G11`) link **existing** research-control, foundation,
implementation or taxonomy rows for corpus tooling, scorer controls, live
scheduling, real Silero runtimes, Earshot, timing and evidence rules. Gaps with
a genuine feasibility lead (`G05`, `G06`, `G08`, `G09`) link existing
feasibility rows for segmentation, blocked small models, turn/endpointing and
personalized VAD. Those links are scoping leads only: no detector is enabled,
no capability is implemented and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The board file is referenced by path and never hashed into
canonical bytes, so status edits elsewhere in the swarm cannot change this map
or break its digest.

## Release boundary

Keep speech-activity detection separate from muting, endpointing, turn
completion, diarization and target-speaker selection; unknown time is never
nonspeech; quiet speech and onset/offset misses remain explicit. Paired real
meeting, synthetic, positive-span-only, adjacent and source-reported results
stay distinct. No public benchmark/quality/device/listening/release claim is
made. No assets, real audio, provider enablement, default, ABI, build or CI
change is included. All files are inside this task directory; board, handoff
and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing, repeats the build in three cold-start processes and enforces
task-local git scope; `test_reference.py` checks canonical output, adverse
rejections and three cold-start repeats. JSON and manifest files have SPDX
license sidecars.

```sh
cd docs/task-evidence/survey-det-01
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `93e4488ece1ce06b5cbb37bb57f9241161cfd97d68ad3bab09c9a998e5e549bf`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
