<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-BREATH-DETECTOR-REMOVAL — breath detector / removal blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility and blocker package** for inventory
component `breath-detector-removal` (Rate and content, verification profile
`rate`). The exact licensed breath detector/removal source, revision,
inference weights, calibration, target definition, preservation policy,
natural breath event labels, runtime, rights record, output-use grant,
matched cohort and parity vector are absent. It creates **no new execution,
model, corpus, real audio, label, provider, processor, ABI, default, build,
CI, board, handoff or release change**.

Task owner: `agent-BREATH-DETECTOR-REMOVAL`; reviewer:
`reviewer-BREATH-DETECTOR-REMOVAL`. Claim base: audio-sdk
`d7f4f9d4426b007be8fc9c24f3a1d58203b69257`; branch
`swarm/SDK-BREATH-DETECTOR-REMOVAL`. The task depends on `SDK-FND-AUDIT`,
`SDK-FND-EVIDENCE` and `SDK-FND-PROVIDER`; write scope is the task-local
evidence directory only (`docs/task-evidence/breath-detector-removal/`).

## What is missing and why no result can qualify

The merged research evidence contains candidate-matrix row 38, *"Waveform
gates for breaths/clicks"*, marked **partially evaluated**. Its finding is a
synthetic click screen on 12 EARS clips: a fixed 7-sample median-residual gate
found no false positives in the tested synthetic conditions but missed every
±0.20 click and every width-5 pulse. The row finding ends with the decisive
limit: **natural clicks and breaths untested**. The linked reports repeat the
boundary:

- `agent-click-gate-expanded/REPORT.md`: *"It is synthetic click evidence only
  and does not evaluate natural clicks, breaths, speech disfluencies, or live
  microphone use."*
- `agent-click-gate-eval/REPORT.md`: *"It does not evaluate breath removal,
  stutter/filler handling, or natural click recordings."* It also warns that
  breaths are not disposable clicks and need separate target definitions.
- `agent-segmentation/REPORT.md`: *"No breath-removal candidate/evaluation."*
  Breath suppression *"requires policy labels because breaths can be
  expressive/linguistic turn cues."*
- `agent-vad-asr-trials/REPORT.md`: no event-level breath truth labels were
  available, deleting breaths may remove useful cues, and no gate was tested.

No fixed path in this workspace contains a breath detector/removal checkout,
resolved 40-hex revision, detector/classifier weights, calibration, target
config, breath policy, natural event-label manifest, runtime environment,
runtime lock, licence grant, rights record, output-use grant, matched cohort or
parity vector. Nothing is downloaded, vendored or inferred. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- the detector/removal geometry (sample rate, channels, frame/hop, detection
  window, lookahead, content delay, removal gain/attenuation, final-padding
  rule) is not established; only the SDK v0 input boundary is asserted;
- the breath target and preservation policy are not established, so
  "removable" versus "expressive/linguistic" breath classes cannot be scored;
- no natural breath event labels exist, so detection precision, recall,
  false-positive and false-negative behavior cannot be measured;
- no candidate output exists, so suppression depth, speech/consonant
  preservation, SI-SDR, STOI, WER, MOS, latency, memory, RTF or listening
  results are not reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

## Evidence classes and boundaries

- **Merged research metadata:** candidate-matrix row 38 and the linked
  click-gate, segmentation, VAD/ASR and matrix-audit reports. These are
  provenance, not local breath execution.
- **Merged sibling package:** `docs/task-evidence/median-residual-click-gate/`
  is a synthetic, opt-in click/transient gate. It is **adjacent evidence, not
  breath evidence**. Its own README says it closes only the opt-in synthetic
  reference question and does not qualify a candidate; its blockers include
  absent natural click, breath, consonant and disfluency labels.
- **Synthetic accounting:** the task-local control generates deterministic
  synthetic PCM at 16 kHz mono, declares an oracle label ledger with three
  `breath_removable` and two `breath_preserve` intervals, and checks:
  nonfinite/invalid/missing rejection, exact non-overlapping half-open source
  intervals, exact source-timestamp mapping (`62500 ns` per sample), duration
  conservation, finite/peak bounds, and that only `breath_removable` samples
  are gated. It performs **no breath detection, no model inference and no
  candidate removal evaluation**; the gated signal is a structural surrogate,
  not candidate output.
- **Not present:** real speech, natural breath events, a pinned detector
  source, weights, calibration, policy approval, consent/rights record,
  output-use grant, frozen cohort, parity vector, runtime invocation, human
  listening, device timing, public benchmark or release approval.

The failure envelope is explicit: a label named "breath" does not make a click
gate a breath detector; a synthetic zeroed interval does not prove suppression
quality or speech preservation; and the absent source, weights, labels and
policy mean neither detection nor removal suitability can be evaluated.

## Breath policy is a first-class gate

Breaths can be expressive, prosodic or turn-taking cues. The merged
segmentation report therefore requires policy labels before suppression. This
package treats that as an exact blocker, not a tuning detail:

- removable and preserve labels must be defined for the intended product;
- events must be tied to exact source intervals and source timestamps;
- speaker, language, noise and expressive-use strata must be frozen;
- voice/breath recording consent and output-use rights must be cleared;
- no default, always-on or shared-build behavior is proposed.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, detector weights/config/calibration hashes and source licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned runtime with a complete lock on a recorded platform | blocked |
| `artifact_rights_and_licence` | Weight, training-data, breath-recording consent, source-audio, output-use and redistribution rights cleared | blocked |
| `breath_target_and_policy` | Exact target definition and preservation policy approved, including expressive/linguistic cues | blocked |
| `event_label_cohort_and_scoring` | Rights-cleared held-out natural breath cohort scores precision/recall and stratified FN/FP | blocked |
| `removal_preservation_and_quality` | Paired/unpaired evidence separates suppression from speech/consonant preservation, peaks, alignment and listening | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and public-surface decision; optional only | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release/benchmark approval; off by default | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent candidate source, absent weights/calibration, unestablished
geometry and policy, absent hash-pinned runtime, unverified licence, absent
natural breath labels, uncleared consent/rights/output-use, and absent
parity/cohort/quality evidence. All ten `rate` profile requirements are
unsatisfied for qualification; three are structural-only or synthetic-only and
none has a qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the detector weights, config, calibration, runtime lock, licence record,
rights record, breath policy, natural event-label manifest, cohort manifest,
parity vector and output-use grant; a full 40-hex source revision; exactly
16 kHz mono with 160-sample frames; and the declared frame-causal variant
`frame_causal_breath_detection_and_removal`. Any missing, malformed,
nonfinite, out-of-range, mismatched or unapproved variant is rejected before
processing. No upstream revision is pinned because the merged evidence records
no breath-detector/removal candidate source; a shape-valid manifest cannot
manufacture qualification.

## Rate-profile reporting

The package reports the rate profile but qualifies none of it:

- source/output mapping and duration are structural-only;
- 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the
  final partial window are not run;
- pitch and transient audibility are not measured;
- speech/consonant preservation is not measured;
- playback buffering, fill/flush, device pacing and deadlines are absent;
- pause/filler/breath decisions are tied to source timestamps only in the
  synthetic oracle ledger;
- no quality, listening or benchmark result is claimed.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path asset
  audit, caller manifest validation, synthetic PCM/interval accounting and 40
  adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers and the caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK contract files
  and package files. The mutable full `plan/swarm/TASKS.json` is **never
  hashed**; only the stable linked-row fields are projected to a digest.
- `run.py` — byte-identical regeneration of report, contract and sources.
- `test_reference.py` — canonical output, identity, audit, manifest, PCM,
  interval, accounting, report and adverse-rejection tests.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/breath-detector-removal
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

JSON, digest, manifest and contract files have SPDX `Apache-2.0` sidecars. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched. No merge, formal approval or release action is taken.
Workspace pins are SHA-256 values of read-only documents; a pin grants no
rights and verifies no media. `SOURCE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.

## Exact blockers and reopening conditions

This package does **not** close the conditional implementation. Reopen only
when all of the following are supplied and independently reviewable:

1. An exact breath detector/removal source checkout at a full 40-hex revision,
   with per-file SHA-256 values and a source licence.
2. Exact detector/classifier/removal weights, configuration and calibration at
   one immutable revision, with byte counts and SHA-256 values.
3. The exact task geometry: 16 kHz mono 160-sample input plus detection window,
   lookahead, content delay, removal gain/attenuation, final-padding rule and
   reset behavior.
4. An approved breath target and preservation policy that defines removable
   versus expressive/linguistic/non-removable classes.
5. A rights-cleared natural breath event-label manifest with exact source
   intervals, speaker/noise strata, known positives and negatives.
6. An isolated hash-pinned runtime and lock on a recorded platform, plus a
   frozen parity vector from one approved caller input.
7. Voice/breath consent, training-data, source-audio, output-use and
   redistribution rights, with notices and an output-use grant.
8. A matched held-out cohort and authorized evaluation covering detection
   precision/recall, stratified FN/FP, suppression, speech/consonant
   preservation, peaks, nonfinite failures, alignment, timing, memory and
   listening where permitted.

No result in this package qualifies the candidate. No provider, descriptor,
registry, installed v0 path, default, shared build, CI, board or handoff is
changed. No merge, formal approval or release action is taken.
