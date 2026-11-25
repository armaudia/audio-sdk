<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-DET-04 — sound-event, vocal-event and scene-analysis evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`DET-04` (Sound-event, vocal-event and scene analysis; legacy family `F12`). It
matches the catalogued classic and ML method families, all three named source
leads (`S12`, `S13`, `S15`) and the available adjacent executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff, benchmark or release change**.

Survey owner: `agent-SURVEY-DET-04`; independent reviewer not dispatched.
Claim base: audio-sdk `c4419d1ce9783b552d662bd7cd524b20ce48feaa`; branch
`swarm/SDK-SURVEY-DET-04`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-det-04/` only |
| Owner and independent reviewer | `agent-SURVEY-DET-04`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-DET-04`, `SDK-SURVEY-DET-04`, `c4419d1ce9783b552d662bd7cd524b20ce48feaa` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no provider, classifier, detector, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S12` YAMNet tutorial (direct), `S13` AudioSet ontology (direct), `S15` Microsoft DNS challenge and paralinguistic evaluation (direct), plus the pinned read-only documents in `SOURCES.sha256`; no weights or revisions are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-det-04/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is an **annotation or control**: an event label, a score,
or optionally an exact interval, used to inform an optional policy. It is not
speech-activity detection (`DET-01`), not utterance endpointing or turn
completion (`DET-02`), not overlap detection or speaker count (`DET-03`), not
target-speaker or personalized VAD (`DET-05`) and not noise suppression
(`CLN-01`). Those categories are named only as boundaries. A sound-event label
is never permission to mute, delete, time-scale or otherwise alter audio.

The catalogued boundary is explicit and is preserved verbatim in `report.json`:
**tagging and temporal detection differ**, this entry **does not resolve ACR**,
and **laughter/backchannels need a preservation policy**. A clip-level tag is
not an event interval. A generic 521-class AudioSet model is not a podcast
scene analyser. An ontology is not an annotation set. A laughter head is not a
preservation decision.

The reviewed records contain **no DET-04 event execution**: no YAMNet run, no
Zencastr run, no scene/ACR run, no event-boundary scorer, no labelled event
corpus and no laughter/backchannel preservation result. Two adjacent local
executions are included only to show what adjacent evidence exists, and both
are explicitly marked `adjacent: true`, `not_component_evidence: true` and
"not rerun by this survey". No missing result is promoted to a pass.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Signal features and statistical classifiers | none | No inventory component, feature extractor, GMM/SVM head or local execution. Energy/spectral features are not by themselves an event classifier |
| ML | Spectrogram CNN audio tagging with an AudioSet label space (`S12`/`S13`) | `yamnet-onnx` | Considered only: 0.96 s window / 0.48 s hop, 521 classes, Apache-2.0 and CC BY 4.0 label claims; no weights, runtime, replay or event score |
| ML | Single-event vocal-event detection (laughter) | `zencastr-laughter-detection` | Considered only: single-event, close-mic conversational, MIT base encoder; window/hop, cost and laugh false alarms on speech unmeasured |
| ML | Temporal event detection and boundary localization | none | No component turns tags into onset/offset intervals; no labelled interval set, collar or event-boundary scorer |
| ML-adjacent | Multi-purpose audio-tagging host | `sherpa-onnx` | Host with an audio-tagging surface, not a selected event model; each bundled model has its own terms |
| ML-adjacent | Vocal-event frame classifiers for disfluency | `wavlm-acoustic-disfluency-model`, `speechbrain-disfluency-pause-predictor` | One unlabelled 4 s inference smoke without a supplied license; the other row is blocked. Disfluency is a vocal-event subcase, not laughter or scene analysis |
| ML-adjacent | Restricted annotation and label sources | `crisperwhisper`, `podcastfillers` | Non-commercial weights or annotations are an offline annotation lead at most; they are not runtime detectors or a rights basis |

`report.json` holds the full records: both catalogued branches, all three
source-lead mappings, the eight-row component census checked against
`INVENTORY.json`, comparison inputs, controls, assets, local-versus-reported
outcomes, the Analysis acceptance mapping, eleven gaps, thirteen board links
and all eight blocked release gates. Source-reported numbers keep their
original documentation scope; they are **not** rerun, pooled into a benchmark
or promoted to a pass.

## Historical executions and comparison inputs

| ID | Execution or input | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | WavLM disfluency inference smoke | `wavlm-acoustic-disfluency-model` | **Adjacent.** One 4 s AMI crop, 199 frame outputs, 180 ms model-only CPU; positive outputs on repetition and partial-word labels; no aligned labels and no supplied license |
| `HE-2` | Vosk `small-en-us-0.15` ASR content-gate pre-screen | `vosk-small-en-us-0-15-playback-gate` | **Adjacent.** Three clips, 15,708 blocks, 0 deadline misses, gate RTF 0.056, output duration −6 to +30 ms, gate about 98 % of chain cost; batch call, not block streaming |
| `CI-1`–`CI-4` | YAMNet, AudioSet ontology, Zencastr and `S15` paralinguistic protocol | source rows | Source-reported documentation only; no weights, runtime, annotations, audio, scorer or listening item |
| `CI-5` | Typed analysis-event contract and model-free fixture (`SDK-FND-ANALYSIS`) | foundation boundary | Proposed speech, rate and transcript event kinds with exact intervals, clocks and explicit unknown/invalid validity; no sound-event or scene kind and no classifier accuracy |
| `CI-6` | WavLM disfluency smoke | adjacent execution | Same one-crop smoke as `HE-1`; not component evidence |
| `CI-7` | Vosk content gate | adjacent execution | Same three-clip pre-screen as `HE-2`; not event tagging |
| `CI-8` | DET-04 event/scene cohort, ontology, interval scorer and matched benchmark | **missing** | Absence is recorded as missing, not as a negative result |

`HE-1` and `HE-2` are **adjacent historical local** rows, not DET-04 detector
results. `CI-5` is a **merged foundation fixture**, not a DET-04 classifier.
The source-reported rows describe candidate or protocol claims and cannot
establish local weights, labels, accuracy, latency or rights. The missing row
keeps an absent cohort explicit instead of silently empty.

## Evidence classes and failure envelope

- **Adjacent local vocal-event evidence:** one WavLM disfluency inference smoke
  on one crop. It proves the checkpoint loads and emits 199 frames; it does not
  prove event accuracy, onset/offset, licence clearance or product fit.
- **Adjacent local content-gate evidence:** one Vosk batch gate pre-screen on
  three clips. It measures speech/filler gating cost and duration, not sound
  events, laughter or scene labels.
- **Adjacent foundation event contract:** exact half-open intervals, clock,
  unknown/invalid validity and read-only audio publication. It is plumbing and
  contains no sound-event kind.
- **Source-reported only:** YAMNet documentation and the 521-class AudioSet
  ontology, Zencastr's single-event laughter card and the `S15` paralinguistic
  protocol lead.
- **Not present:** a rights-qualified event/scene corpus, frozen ontology and
  annotations, real event weights/runtimes, event intervals, onset/offset or
  FN/FP results, laughter/backchannel preservation evidence, listening,
  target-device timing and a benchmark.
- The failure envelope is adverse by omission: the two candidate rows are
  **considered only**, both local rows are **adjacent**, and the only
  foundation interval evidence has no event classifier behind it. Tagging,
  temporal detection, scene analysis and ACR are not interchangeable, so no
  capability is inherited from a candidate note or an adjacent task.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with a genuine feasibility lead (`G02`, `G03`,
`G07`, `G08`, `G10`) link existing YAMNet, Zencastr, sherpa-onnx, evidence-
manifest, WavLM or SpeechBrain rows. Gaps without a component owner (`G01`,
`G04`, `G05`, `G06`, `G09`, `G11`) link existing foundation, research-control
or taxonomy rows and carry an explicit `no dedicated DET-04 ...` owner note.
Those links are scoping leads only: no classifier or detector is enabled, no
capability is implemented and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The mutable board file is referenced by path and **never hashed
into canonical bytes**, so status edits elsewhere in the swarm cannot change
this map or break its digest.

## Release boundary

Keep tagging, temporal event detection, scene analysis and ACR separate; keep
speech-activity, endpointing, overlap, target-speaker and noise-suppression
rows out of this claim; keep candidate-documentation, adjacent-local,
foundation-fixture and missing evidence distinct; and require a laughter and
backchannel preservation policy before any event-conditioned action. No public
benchmark/quality/device/listening/release claim is made. No provider
registration, installed-v0/ABI/registry/default/shared-build/CI change, real
corpus, weights, runtime invocation, audio mutation, listening, device-timing,
benchmark or release approval is included. All files are inside this task
directory; board, handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, and repeats the build in three cold-start
processes; `test_reference.py` checks canonical output, adverse and nonfinite
rejection, adjacent-execution boundaries and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-det-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `dfbc259cce5c87d186cb6c0aa556724ebdf327c03258f73cdc5ef855c053fd11`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
