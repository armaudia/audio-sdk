<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FASTSPEECH-2-VITS-DURATION-PREDICTORS — duration-predictor blocker
package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the FastSpeech 2 / VITS
duration-predictor feasibility row. It is **not** an implementation of either
predictor. No upstream source tree, checkpoint, config, phoneme set, duration
statistic, runtime, reference duration label, phoneme alignment, listening
result, device measurement, benchmark or release claim is present. **No result
here qualifies FastSpeech 2, VITS or any duration predictor.**

The structured inventory marks `fastspeech-2-vits-duration-predictors` as
`evidence_status=considered` with the **Rate** acceptance profile
(`verification_profile: rate`, `plan/INVENTORY.json`). The pinned analysis
records inspected the architecture only and concluded that both modules require
text or encoder representations and predict synthesized phoneme durations. No
standalone incoming-audio inference was evaluated.

## Exact external blocker

The exact **FastSpeech 2 source**, the exact **VITS source**, the
**caller-selected checkpoint bundles**, and the **isolated runtime** are all
absent. Nothing was fabricated, reconstructed, mirrored, downloaded or
substituted. No revision, file name, byte count, license or SHA-256 is asserted
as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| FastSpeech 2 source | A reviewed FastSpeech 2 checkout (for example the ESPnet module `espnet2/tts/fastspeech2/fastspeech2.py`) at an immutable 40-hex commit with reviewed upstream license text and a per-file SHA-256 manifest |
| VITS source | The reviewed VITS checkout at an immutable 40-hex commit with reviewed upstream license text and a per-file SHA-256 manifest |
| Checkpoint bundles | The caller-selected FastSpeech 2 and VITS checkpoints at immutable 40-hex model revisions, including every weight, config, phoneme set, duration statistic, hop length, model card and terms file, each with byte count and SHA-256 |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter and package versions including `torch`, a lock SHA-256, an offline load path and a recorded host profile |
| Rights | Reviewed code licenses, weight and model-card terms, training-data provenance, corpus license, output use and redistribution approval for both sources and every checkpoint |
| Cohort | A frozen permitted text and phoneme cohort with reference phoneme duration labels, language groups, 1x, rate-change, unfamiliar-speech, music, silence, rebuffer, drift and final-partial-window cases, held-out splits and matched controls |
| Rate results | Independent duration error and sum consistency, source/output mapping, speech preservation, pitch, transient audibility, playback buffering, nonfinite/peak, device timing, resource and uncertainty results on the exact pinned bundle |

The machine-readable record is `report.json` → `source_probe`,
`weights_probe`, `runtime_probe`, `absence_evidence`, `task_geometry`,
`required_artifacts`, `exact_blockers`, `rate_profile` and `gates`.
`contract.json` carries the same disposition, pins, geometry and all eight
blocked release gates.

## Task geometry: a second, independent blocker

Even with exact sources, checkpoints and a runtime, these modules are **not**
incoming-audio rate estimators. Both consume text-side representations
(`text`, `phoneme_ids`, `text_encoder_states`) and emit per-token duration
frames for a TTS length regulator. The installed v0 provider callback consumes
float32 audio frames, so no public adapter boundary accepts their inputs.

`report.json` → `task_geometry` therefore records
`status="blocked_interface_mismatch"`,
`consumes_incoming_audio=false`, `input_audio_rate_controller=false`,
`public_v0_provider_accepts_text=false` and `adapter_boundary_available=false`.
Reopening this row requires an explicit text-conditioned duration-prior scope
with a separate incoming-audio controller comparison — not a relabel of the
predictor as an audio rate estimator.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** Reviewed planning records, the category registry and
   survey source list, the rate-follow-up README and its text-baseline report,
   plus the SDK boundary files are pinned by SHA-256. These are read-only
   provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`,
   `component`, `mode`, `repository` and `depends_on` are projected and hashed.
   The mutable `plan/swarm/TASKS.json` file is **never hashed**; status, owner,
   claim, review, handoff, priority and history never enter canonical bytes and
   never gate this package.
4. **Fail-closed admission schema.** A task-local duration-cohort manifest has
   a strict schema. Missing, invalid, duplicate, nonfinite, aliased, unordered,
   out-of-range, non-integral, unresolved, unlicensed or duration-inconsistent
   cases are rejected before any state change. Any predictor that claims to
   consume incoming audio is rejected with `geometry_mismatch`. One synthetic
   structural control is accepted to prove the validator is not
   blanket-rejecting; it is labelled `synthetic_schema_control` and
   `qualifies=false`.
5. **Rate profile accounting.** Source/output mapping, duration, pitch,
   transient audibility, playback buffering, the required rate conditions,
   source-timestamped pause/filler decisions and speech preservation are each
   recorded as **blocked**. Text-conditioned scope is not qualified.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No predictor provider is installed or
   registered; no descriptor, default, ABI, shared build, CI, board or handoff
   change is made.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Measure source/output mapping | blocked | No predictor, checkpoint or runtime, so no source interval, token or frame maps to an output. |
| Measure duration | blocked | No predicted or reference phoneme duration exists. |
| Measure pitch | blocked | No synthesized or played waveform exists. |
| Measure transient audibility | blocked | No rendering or playback path exists. |
| Measure playback buffering | blocked | No buffer, scheduler, callback or device queue is exercised. |
| Cover 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final partial window | blocked | No frozen permitted cohort and no predictor output exist. |
| Tie pause/filler decisions to source timestamps | blocked | The text-side predictor has no incoming-audio timestamps. |
| Measure speech preservation | blocked | No audio is produced, transformed or compared. |

## Historical and peer boundary

The pinned read-only records contain an **architecture inspection only**. There
is no local FastSpeech 2 or VITS run, checkpoint, duration label or metric, and
no value is inferred from the merged sibling evidence packages:

- `f5-tts` is an adjacent TTS model blocker with no duration predictor.
- `d1-whole-clip-duration-planner` is a synthetic source-to-playback schedule
  planner, not a text-conditioned duration model.
- `silero-vad-pause-duration-rules` is a pause policy over VAD timelines.
- `usc-mrate` is an audio-side syllable-rate estimator with an unlicensed
  source archive; it is the closest Rate-profile peer but a different task.
- `bungee-basic` is a time-stretch actuator that changes playback duration.

## Admission contract (task-local; not an SDK, TTS or Rate contract)

The schema is `audio-sdk/fastspeech-2-vits-duration-predictors-cohort/0.1`.
Unknown and missing fields, duplicate JSON keys, `NaN`/`Infinity`, floats,
unsafe or unresolved values, duplicate or unsorted entries, non-integral or
out-of-range integers, non-offline runtimes, unlicensed rights and any
incoming-audio predictor are rejected. Duration sums must match the declared
per-item totals. The one accepted control is synthetic and never qualifies.
Admission never reads audio, loads weights or invokes a model.

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` writes `contract.json`, canonical `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires all three
cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift,
out-of-scope change, missing sidecar, missing SPDX header or absent blocker.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pt`, `.pth`, `.onnx`, `.safetensors`, binary library, compiled object,
upstream source copy, license text copy or model weight.
