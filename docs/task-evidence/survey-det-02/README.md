<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-DET-02 — utterance endpointing and turn-completion evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`DET-02` (Utterance endpointing and turn completion, legacy family `F11`). It
matches the catalogued classic and ML method families, the named source lead
(`S03`) and historical local or source-reported executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-DET-02`; independent reviewer not dispatched.
Claim base: audio-sdk `f2811bda1d07660fa5a98c538bfa9c845d0e1b0f`; branch
`swarm/SDK-SURVEY-DET-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to claim

The catalogued boundary is explicit: endpointing is useful for optional
recognition or voice-agent workflows, is **not** a required filter on ordinary
human calls, and pauses can occur within a turn. This map therefore covers
fixed and adaptive silence timers/state machines and acoustic, prosodic or
semantic turn models. It does **not** pool speech activity detection (`DET-01`),
pause trimming or playback rate policy, ASR segmentation, disfluency editing or
transcript controls into a DET-02 result. Those rows are named only as
boundaries, and their results are not promoted here.

No reviewed record contains a real utterance or turn boundary label. The only
local endpointing-like execution is a synthetic pause-duration controller; the
only model lead is documentation; the remaining rows are activity-only,
playback-only, blocked or source-reported. Endpoint accuracy, cutoff delay and
end-of-turn delay are therefore **not measured**.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: fixed/adaptive silence timers with hangover and state-machine completion | `silero-vad-pause-duration-rules` (partial): merged synthetic 9-condition × 3-rate fixture, guarded 120/360 ms thresholds with 200 ms retention, exact 160-sample intervals, unknown validity retained; long-pause candidate retains 3,237 pause samples and zero word-span overlap versus the unguarded baseline's 1,280-sample overlap | Synthetic probability trace only; no real Silero runtime, speech, turn label, rendered audio or endpoint accuracy |
| Classic: framewise VAD activity suppliers as timer input | `webrtc-vad`, `silero-vad-6-2-3-reference`, `adaptive-energy-vad`, `speexdsp-vad`, `fixed-rms-vad` (evaluated): held-out AMI activity rows FN/FP 7.31/49.54%, 19.43/8.20%, 33.15/21.58%, 2.45/77.03% and 62.95/25.35% | Activity only: AMI has speech/nonspeech labels, **not** utterance or turn boundaries; no cutoff or end-of-turn delay is derived |
| Classic: VAD-conditioned pause trimming and playback policy | `source-vad-conditioning-for-playback` (considered), `d1-whole-clip-duration-planner` (partial): 23 synthetic rate variants, 21 adverse controls, 18 identity passes and one deliberate `fixed_125` bounds failure | Playback budgeting only; typed silence/filler labels never decide that a turn ended and never delete audio |
| ML: acoustic/prosodic end-of-turn with optional semantic context (`S03`) | `livekit-turn-detection`, `livekit-python-host-adapter` (considered) | Documentation lead only: no runtime, weights, exact revision, configuration, turn-labelled cohort or numeric parity |
| ML: acoustic disfluency/pause predictors as adjacent cues | `speechbrain-disfluency-pause-predictor` (blocked), `wavlm-acoustic-disfluency-model` (partial): inference smoke on a 4 s AMI crop, no aligned labels or licence | Disfluency is not turn completion; no score and no usable checkpoint |
| ML: transcript/text-conditioned semantic completion and filler annotation | `speech-recognition-translation-controls` (considered), `text-aware-filler-and-stutter-annotation` (blocked), `waveform-only-filler-stutter-deletion` (considered) | No local transcript source, semantic target or completion execution; text is a boundary, not evidence |
| ML: streaming ASR segmentation and endpointing | `whisper-streaming`, `simulstreaming`, `streaming-conformer-ted`, `fastconformer-streaming-asr` (all blocked) | No checkpoint, streaming runtime or adapter; ASR endpointing is not conversational turn completion |
| ML: prosodic feature regression head with a speech-rate target | `silero-vad-opensmile-small-regression-head` (evaluated): frozen caller-supplied features and a synthetic rate head; held-out head loses to the constant dev-mean baseline | The target is speech rate (syll/s), not end-of-turn; openSMILE is research-only; never pooled with endpointing |

`report.json` holds the full records: both catalogued branches, the `S03`
source-lead mapping, the component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Guarded pause-duration controller on the merged synthetic fixture | `silero-vad-pause-duration-rules` | 9 synthetic conditions × 3 rate cases; exact half-open 160-sample intervals; no real speech or turn labels |
| `HE-2` | Upstream held-out AMI framewise activity comparison | `webrtc-vad`, `silero-vad-6-2-3-reference`, `adaptive-energy-vad`, `speexdsp-vad`, `fixed-rms-vad` | Three held-out meetings, 20 ms activity frames; **no** utterance or turn boundaries |
| `HE-3` | D1 whole-clip planner over typed silence/filler labels | `d1-whole-clip-duration-planner` | 23 synthetic rate variants and 21 adverse controls; playback budget only |

Comparison inputs separate the merged synthetic pause fixture, upstream AMI
activity, the source-reported 1,172 s/282 s pause-trim overlap, the LiveKit
documentation lead, the missing rights-qualified turn corpus and the adjacent
D1 rate planner. Every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local synthetic pause controller:** HE-1. It proves deterministic
  interval behavior on a seeded fixture, not perception or endpoint accuracy.
- **Historical local activity-only:** HE-2. Framewise VAD rows are useful
  upstream context but carry no turn boundary, so endpoint metrics are not
  computable.
- **Historical local adjacent rate planner:** HE-3. Exact playback budgeting
  over typed labels, not a completion decision.
- **Source-reported only:** LiveKit documentation, SpeechBrain blocked status,
  the 1,172 s/282 s pause-trim proxy, the streaming-ASR leads and the WavLM
  inference smoke.
- **Not present:** rights-qualified real conversation, turn labels, semantic
  model execution, real Silero runtime in this task, listening, device timing,
  cutoff/end-of-turn delay, endpoint accuracy, provider intake or release
  approval. These classes are `false`, not inherited from an adjacent survey.

The failure envelope is adverse in both directions. The unguarded 500 ms pause
trim removes 1,172 s while overlapping 282 s of word-labeled speech, so a
silence timer can cut valid speech. The conservative guarded version avoids
synthetic word-span overlap but retains 3,237 pause samples and therefore
compresses far less. Upstream VAD over- and under-triggers heavily (WebRTC FP
49.54%, SpeexDSP FP 77.03%, RMS FN 62.95%), so activity accuracy does not imply
turn correctness. A low synthetic overlap is not a passing endpoint detector.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with an existing feasibility owner (`G03`,
`G04`, `G05`, `G06`, `G09`, `G11`) link LiveKit, transcript/text, disfluency,
streaming-ASR, playback and audit rows. Gaps without a component owner (`G01`,
`G02`, `G07`, `G08`, `G10`) link existing research-control, foundation,
implementation or taxonomy rows for corpus/scoring tooling, real activity
runtimes, live lifecycle and target timing. Those links are scoping leads only:
no endpoint detector is enabled, no capability is implemented and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep endpointing separate from framewise activity, muting, pause trimming,
playback rate, ASR segmentation, disfluency editing and semantic transcript
policy. Unknown time is never nonspeech and never a completed turn. Synthetic,
activity-only, adjacent playback, source-reported and missing results stay
distinct. No public benchmark, quality, device, listening, latency or release
claim is made. No assets, real audio, weights, provider enablement, default,
ABI, build or CI change is included. All files are inside this task directory;
board, handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte and checks three cold-start builds; `verify.py`
recomputes all artifacts, checks licensing, repeats the build in three fresh
processes and enforces task-local git scope; `test_reference.py` checks
canonical output, adverse rejections, domain boundaries and three cold-start
repeats. JSON and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-det-02
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `e586f8436dd488bb1c852110873d77d9f700d9c4ee50387587326c73be2d3218`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
