<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-HYBRID-AHS-SELF-ATTENTIVE-RNN-AND-KALMAN: Hybrid AHS feasibility blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Hybrid AHS self-attentive RNN and Kalman row. It is **not** Hybrid AHS or
NeuralKalmanAHS: no upstream source, model code, checkpoint, weight,
configuration, license text, runtime, corpus, candidate output, listening
result, device measurement, benchmark or release claim is included. **No
result here qualifies the candidate.**

## Exact blocker: source, checkpoint, runtime, rights and cohort absent

A bounded, read-only search of named workspace paths found **no
`AHS_2023` or `NeuralKalmanAHS` checkout**, **no trained checkpoint or
inference state**, **no pinned model runtime**, **no local license text or
written rights decision**, and **no matched closed-loop cohort**. Nothing was
cloned, downloaded, installed, extracted, ported, reverse-engineered,
reconstructed or substituted.

The pinned research note records the exact upstream situation: the public
`YIXUANZ/NeuralKalmanAHS` and `YIXUANZ/AHS_2023` repositories expose README and
demo HTML/CSS/audio files, **no source implementation or model checkpoints**
were present in their visible file listings, and **no release assets were
listed for NeuralKalmanAHS**. The paper describes a frequency-domain Kalman
filter plus a self-attentive RNN, teacher-forced offline training, and streaming
inference where the fixed network output becomes the Kalman reference. Those
are research references, not a runnable candidate.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local `AHS_2023`/`NeuralKalmanAHS` tree; revision, tree digest, file count and license file are `null` |
| Runnable implementation | **Absent/reported demo-only.** The pinned note records README/demo materials without source |
| Checkpoint/weights | **Absent.** No `.pt`, `.pth`, `.ckpt`, `.onnx`, `.safetensors`, `.bin` or `.pkl` state; no model revision, parameter count or model card |
| Runtime | **Absent/unpinned.** No interpreter lock, framework version, platform record, offline path or import-parity vector |
| License and rights | **Absent/blocked.** No byte-identical license text, SHA-256 or written use/redistribution/derived-output decision |
| Candidate geometry | **Absent.** No sample rate, frame, hop, STFT size, channel count, Kalman state dimension, RNN structure, layer count or parameter count is recorded |
| Matched cohort | **Absent.** No rights-cleared closed-loop corpus with loop gain, delay, saturation and held-out speakers/paths |
| Candidate execution | **None.** No build, model load, inference, SDR, PESQ, stability, timing or listening run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_checkpoint_runtime_rights_and_cohort_absent"`, with
every digest and byte count `null`), `required_artifacts` (A1-A6),
`source_probe`, `checkpoint_probe`, `runtime_probe`, `license_probe`,
`cohort_probe`, `rights_probe`, `geometry`, `method_provenance`,
`author_reported_results` and `external_boundary`. `contract.json` carries the
same blocker, the same missing artifacts and all eight blocked release gates.

## Author-reported results retained, not reproduced

The pinned note records the HybridAHS/NeuralKalmanAHS journal comparison on
200 utterances at loop gains 2, 2.5 and 3. NeuralKalmanAHS is reported at
**SDR 2.65, 1.98 and 1.45 dB** and **PESQ 2.33, 2.17 and 2.04** for those
three conditions. HybridAHS v2 complex-ratio-mask results are described
qualitatively as the strongest overall trade-off in parts of the study.

Those values are retained exactly as `author_reported_not_reproduced` with
`local_metrics=null`, `reproduced_here=false` and
`qualifies_candidate=false`. They are paper results on the author setup, not
results from this repository, not comparable to the current CLN-01 DNS screen,
and not a qualification. No SDR or PESQ value was computed here.

## Method boundary

| Field | Recorded value |
| --- | --- |
| Candidate | Hybrid AHS self-attentive RNN and Kalman |
| Paper | Interspeech 2023, `zhang23q` |
| Journal comparison | 2024 HybridAHS / NeuralKalmanAHS study |
| Upstream repositories | `YIXUANZ/AHS_2023`, `YIXUANZ/NeuralKalmanAHS` |
| Method | Frequency-domain Kalman filter plus self-attentive RNN |
| Training | Teacher-forced offline on Kalman-preprocessed and ideal microphone signals |
| Inference | Streaming; fixed network output becomes the Kalman reference |
| Reported evaluation | Simulated and real-recorded (author-reported) |
| Local source present | **No** |
| Local checkpoint present | **No** |
| Local runtime present | **No** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

No architecture detail, geometry, weight, score or output is inferred from the
paper description. The pinned note does not record a license name or text, so
none is asserted.

## What the task asks and what is proven here

The board row is `feasibility` mode. It asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence; reproduce the
exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK
adapter once prerequisites pass; record a concrete blocker if feasibility
fails; retain author-reported closed-loop results; and check for exact runnable
state/checkpoints before an experiment. It applies the DSP acceptance profile.

This package proves only the **negative** side of that gate:

- the exact source, checkpoint, runtime, rights and cohort prerequisites are
  absent (bounded probes, no network);
- the source is reported as demo materials rather than a runnable
  implementation;
- every structurally valid caller-supplied-asset request is rejected with
  `DEFER` because the artifacts and rights are absent;
- invalid, missing, wrong-shape, nonfinite, out-of-range and inconsistent
  asset-manifest requests are rejected before any artifact check;
- the author-reported results are retained with their original scope and are
  never presented as local measurements;
- no candidate geometry is inferred from the paper description;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Hybrid AHS is unsuitable. It records the exact
external condition required to reopen the investigation.

## Exact scope

- Work is confined to
  `docs/task-evidence/hybrid-ahs-self-attentive-rnn-and-kalman/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, provider registration, board/handoff files, CI, rulesets and
  `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  Hybrid AHS provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, checkpoint, weight or audio file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain, SDR,
  PESQ, Kalman, RNN, benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim, history and every other mutable field never enter
  canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## DSP profile application

The structured inventory assigns the **DSP** acceptance profile
(`plan/swarm/VERIFICATION.md`, pinned below). The profile asks for sweeps,
steps, impulses, silence, clean speech and an intelligibility or load-specific
control, with gain, response, attack/release, headroom, delay, numerical
behavior, state transitions and interacting nonlinear configurations.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Sweeps / steps / impulses / silence | `stimulus_probe`: synthetic harness characterization only | No candidate input or output |
| Clean speech and task control | `profile_mapping` and `required_results` mark blocked | No permitted cohort |
| Gain and response | `blocked_no_candidate_output` | Unmeasured |
| Attack / release | `blocked_no_candidate_output` | Unmeasured |
| Headroom / peaks | `blocked_no_candidate_output` | Unmeasured |
| Delay / content mapping | `blocked_no_candidate_output` | No delay assumed or fitted |
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Candidate output | `blocked_source_checkpoint_runtime_rights_and_cohort_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Pins

Paths outside `docs/task-evidence/hybrid-ahs-self-attentive-rnn-and-kalman/`
are relative to the `audioml` workspace root; SDK boundary paths are relative
to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | Hybrid AHS method, repositories, author-reported results and runnable status |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `hybrid-ahs-self-attentive-rnn-and-kalman` row, DSP profile, sdk-model disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Caller-supplied-asset / opt-in adapter sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | Unchanged licensing metadata |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` | Unchanged Git attributes |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |

`SOURCES.sha256` additionally pins every task-local artifact and excludes
itself because a file cannot pin its own bytes. `contract.json` is excluded
from `SOURCES.sha256` because it pins the manifest; it is pinned by the
verifier and by review. `verify.py` fails closed on a missing, stale,
malformed, duplicated or extra pin and on any worktree change outside this
directory.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission gate, harness controls and canonical report builder.
- `run.py`: regenerates report, sidecar, manifest and contract three times and
  fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, scope and three-cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/hybrid-ahs-self-attentive-rnn-and-kalman
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact source revision and upstream license pin.
2. `RG-02` exact trained checkpoint, inference state and per-file weight
   identity.
3. `RG-03` locked isolated runtime, framework versions and offline parity.
4. `RG-04` declared geometry, Kalman/RNN configuration and layer reproduction.
5. `RG-05` full DSP matrix: gain, response, attack/release, headroom, delay,
   numerical behavior, state transitions and nonlinear configurations.
6. `RG-06` reconciliation of the author-reported SDR/PESQ values.
7. `RG-07` closed-loop stability, maximum stable gain, adverse behavior and a
   held-out matched cohort.
8. `RG-08` opt-in adapter intake, benchmark validation, authorized listening,
   independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
