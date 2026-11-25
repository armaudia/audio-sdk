<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-11 — feedback and howling control evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-11` (Feedback and howling control, legacy family `F08`). It matches the
catalogued method families, both named source leads (`S48`, `S49`) and the
available historical executions to existing components. It creates **no new
execution, model, corpus, provider, processor, ABI, default, build, CI, board,
handoff, benchmark or release change**.

Survey owner: `agent-SURVEY-CLN-11`; independent reviewer not dispatched.
Claim base: audio-sdk `9536dbef4a8c150702ef2be9a34ab360c45c1039`; branch
`swarm/SDK-SURVEY-CLN-11`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-cln-11/` only |
| Owner and independent reviewer | `agent-SURVEY-CLN-11`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-25, `swarm/SDK-SURVEY-CLN-11`, `SDK-SURVEY-CLN-11`, `9536dbef4a8c150702ef2be9a34ab360c45c1039` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no provider, recipe, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S48` Espressif HOWL 1.4.2 documentation (direct), `S49` Interspeech 2023 Hybrid AHS (search excerpt), plus the pinned read-only documents and reports in `SOURCES.sha256` |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-cln-11/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is a **waveform and/or loop control**: reducing gain,
notching a growing tone or cancelling an estimated feedback path. It is not an
ordinary AEC result, not a residual-echo suppressor, not plain noise
suppression, not a DRC curve and not a narrow tonal filter with a fixed
frequency. Feedback control only exists inside an affected microphone–speaker
loop, and the loop that produced a measurement must travel with the number.

`CLN-05` (reference-based AEC), `CLN-06` (residual echo suppression), `CLN-01`
(background noise suppression), `CLN-09` (gain/loudness/DRC), `CLN-10` (tonal
correction and interference filtering), `CLN-07` (beamforming), `CLN-08`
(source localization) and `ENG-02` (reference/clock alignment) are named only
as boundaries. Their rows are not feedback-control evidence and are never
pooled into a CLN-11 claim.

Six dedicated components have **merged local synthetic DSP evidence**:
`adaptive-feedback-notch`, `adaptive-notch-with-gain-margin`,
`fixed-feedback-gain-margin`, `block-nlms-afc`, `block-nlms-afc-with-margin`
and `logistic-feedback-gain-controller`. A seventh row, `narrow-biquad-notch`,
is a **partial CLN-10 primitive**, not a howl detector. Nothing in this package
is a physical loudspeaker–microphone loop, a measured gain-before-feedback
value, a neural howling execution, a listening result, a labelled howl
benchmark or a release decision.

## Method families and mapped evidence

| Catalogued family | Mapped component(s) | Status and boundary |
| --- | --- | --- |
| Classic: gain reduction / fixed feedback gain margin | `fixed-feedback-gain-margin`, `adaptive-notch-with-gain-margin`, `logistic-feedback-gain-controller` | Evaluated on synthetic fixtures only; −5 dB margin is a comparator, not a selection |
| Classic: adaptive notch detection with dynamic biquads | `adaptive-feedback-notch`, `adaptive-notch-with-gain-margin`, `narrow-biquad-notch` (primitive) | Evaluated on synthetic fixtures; false activations on tonal vowels/music and silence remain a material stratum |
| Classic: adaptive feedback cancellation | `block-nlms-afc`, `block-nlms-afc-with-margin` | Evaluated on synthetic fixtures; requires an explicit playback reference and has no prediction-error decorrelator or path-change detector |
| Classic: Kalman adaptive feedback cancellation | `kalman-afc` | Considered only; no local implementation, execution, checkpoint or covariance result |
| ML: neural-assisted Kalman filtering | `hybrid-ahs-self-attentive-rnn-and-kalman`, `neuralkalmanahs-covariance-reference-variants` | Candidate rows are blocked; no source, checkpoint, licensed weights or runtime |
| ML: hybrid feedback suppression | `neural-plus-kalman-howling-control`, `hybrid-ahs-self-attentive-rnn-and-kalman`, `afc-spex` | Considered/blocked; no runnable hybrid and no compatible three-channel checkpoint |
| ML: neural direct howling suppression | `neural-direct-howling-suppression`, `afc-spex` | Considered; no published model selected and no weights |
| ML-adjacent: learned feedback-risk gain control | `logistic-feedback-gain-controller` | Evaluated small supervised logistic baseline on simulator labels; explicitly **not** a published neural AHS |

`report.json` holds the full records: all eight catalogued/adjacent family
rows, both source-lead mappings, the 14-row component census checked against
`INVENTORY.json`, adjacent boundaries, comparison inputs, controls, assets,
historical executions, local-versus-reported outcomes, the DSP acceptance
mapping, ten gaps, board links and all eight blocked release gates. Transcribed
numbers keep their original synthetic or pilot scope; they are **not** rerun,
pooled into a benchmark or promoted to a pass.

## Historical executions and local-versus-reported outcomes

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | AMI ES2004a closed-loop synthetic pilot, 36 runs per candidate / 216 total | five classical feedback components | Simulated recursive loop on one meeting; fixed margin 5.193 dB median SDR versus identity −6.511 dB; 19 no-loop notch false activations |
| `HE-2` | SMARD measured-IR-shape pilot, 144 runs per candidate | five classical feedback components | Measured IR shapes, per-path normalization and simulated loop; AFC 8.427 dB and AFC+margin 8.429 dB median SDR; not calibrated gain-before-feedback |
| `HE-3` | Held-out-loudspeaker logistic detector pilot, 72 runs per candidate | `logistic-feedback-gain-controller`, `fixed-feedback-gain-margin` | Train on configuration 0000, evaluate on 1000/2000; held-out precision 0.6443, recall 0.652, 38 clean-speech events; not a neural AHS |
| `HE-4` | Merged adaptive-notch fixture | `adaptive-feedback-notch` | 3-frame attack, 23-frame release, zero clean-speech false activations, identity tail 31.51 dB versus margin −208.59 dB |
| `HE-5` | Merged notch-plus-margin fixture | `adaptive-notch-with-gain-margin` | Fixed-gain program SDR 7.194 dB, notch-plus-margin −0.598 dB, state unchanged on rejection |
| `HE-6` | Merged fixed-margin fixture | `fixed-feedback-gain-margin` | −5 dB program SDR 7.177 dB, RMS ratio 0.562341325, six explicit FIR feedback cases, no candidate selected |
| `HE-7` | Merged block-NLMS-AFC-plus-margin fixture | `block-nlms-afc-with-margin` | 48 taps, 160-sample loop delay, six closed-loop cases; AFC-only sustained feedback at the dual-path case; no missing result qualifies a candidate |
| `HE-8` | Merged logistic-controller fixture | `logistic-feedback-gain-controller` | Held-out precision 0.9731, recall 0.9968, FPR 0.0612 on generated paths; fixture-trained coefficients, not production weights |

`HE-1`–`HE-3` are **historical survey pilots**; `HE-4`–`HE-8` are **merged
task-local component fixtures**. The two groups are not the same protocol and
are not averaged. `HE-8`'s high synthetic SDR is not the `HE-3` pilot result:
the earlier SMARD-held-out pilot reported 5.138 dB median SDR with 38 false
events. Comparison inputs also include the source-only `S48`/`S49` protocol,
the catalogued but unavailable ML rows, and the **missing** physical loop,
rights-qualified real-howl corpus, neural checkpoint and frozen benchmark
scorer. Every historical row says "not a physical-loop result" and "not rerun
by this survey".

## Evidence classes, failure envelope and release boundary

- **Local synthetic component evidence:** six merged deterministic DSP
  reports. They prove bounded gain, notch/AFC mechanics and fail-closed
  rejection on analytic fixtures; they do not prove a physical PA, hearing-aid
  or device result.
- **Historical survey pilots:** AMI speech and/or measured SMARD IR shapes
  inside a **simulated** loop. One meeting/room and normalized paths prevent a
  generalization or gain-before-feedback claim.
- **Source-only frozen protocol:** Espressif HOWL documentation and the Hybrid
  AHS paper excerpt. Method descriptions and author-reported numbers only.
- **Source-reported candidate gap:** Kalman, neural-direct, neural-plus-Kalman,
  Hybrid AHS, NeuralKalmanAHS and AFC-SPEX rows are considered/blocked.
- **Missing:** a physical loop, calibrated gain-before-feedback, real howl
  labels, licensed checkpoints/weights, device timing, listening, a labelled
  held-out benchmark and any release qualification.
- **Deliberately not claimed:** ordinary AEC performance, residual-echo
  suppression, noise suppression, DRC behaviour, tonal-filter rejection, speech
  intelligibility, product safety, maximum stable gain and public default.

The failure envelope is explicit: an open-loop overlay of a prerecorded howl
tone is not a closed-loop stability test; sustained residual howl is a failure,
not a slow pass; a fixed margin that stabilizes a loop by attenuating wanted
speech is a baseline, not a selection; and a notch that fires on music or a
sustained vowel is a false positive even when the target tone is removed.

## Bounded gaps and feasibility links

Ten gaps are recorded. `G03`, `G04` and `G08` link existing feasibility rows;
the rest link existing implementation, foundation or external-adapter rows and
carry an explicit `no dedicated CLN-11 ...` owner note where no feasibility row
exists. The ML rows are scoping leads only: no processor is enabled, no
capability is implemented and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The mutable board file is referenced by path and **never hashed
into canonical bytes**, so status edits elsewhere in the swarm cannot change
this map or break its digest.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three byte-identical cold-start repeats. JSON
and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-11
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256 is recorded in `report.json.sha256` and printed
by `verify.py`. The change is task-local documentation and stdlib tooling; no
installed package, descriptor catalog, ABI, build input or CI workflow is
touched.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
