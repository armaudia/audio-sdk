<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURAL-DIRECT-HOWLING-SUPPRESSION: neural direct howling-suppression feasibility blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Neural direct howling suppression row. It is **not** a neural suppressor:
no published model source, weight, checkpoint, configuration, license text,
runtime, documented task geometry, matched closed-loop fixture, listening
result, closed-loop measurement, benchmark or release claim is included. **No
result here qualifies the candidate.**

## Exact blocker: source, weights, runtime, geometry, rights and fixture absent

A bounded, read-only search of named workspace paths found **no published
model checkout**, **no weight or checkpoint archive**, **no locked inference
runtime**, **no documented model geometry or configuration** and **no matched
closed-loop fixture**. Nothing was cloned, downloaded, extracted, ported,
reverse-engineered or substituted.

The pinned research note records the reviewed public repositories
(`YIXUANZ/NeuralKalmanAHS`, `YIXUANZ/AHS_2023`, `ZLiNJU/AFC-SPEX`) as exposing
README/demo material and, for AFC-SPEX, source whose checked-in inference
configuration expects three microphone channels and an author-local
checkpoint. No checkpoint, runnable single-channel direct suppressor, license
text or matched closed-loop fixture is present locally. Upstream visibility is
not a runnable artifact and not a right to use.

| Item | Status |
| --- | --- |
| Published source | **Absent.** No local HybridAHS v2 complex-ratio-mask checkout; revision, tree digest, file count and license file are `null` |
| Weights / checkpoints | **Absent.** No weight archive, checkpoint, inference configuration, byte count or SHA-256 |
| Runtime | **Absent/unpinned.** No locked interpreter, framework, wheel hashes, device, dtype, determinism settings or install/import record |
| Task geometry | **Absent.** The pinned evidence does not document this variant's rate, channels, frame, hop, lookahead, delay, reset or drain contract |
| Rights | **Blocked.** No license text, model card, training-data terms or written decision for code, weights, input audio, derived output or redistribution |
| Matched fixture | **Absent.** No rights-cleared closed-loop fixture with measured or frozen paths, loop gain, delay, saturation and held-out splits |
| Candidate execution | **None.** No build, load, mask, enhancement, stability, timing or listening run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_weights_runtime_geometry_rights_and_fixture_absent"`,
with every digest and byte count `null`), `required_artifacts` (A1-A7),
`source_probe`, `weights_probe`, `license_probe`, `runtime_probe`,
`geometry_probe`, `fixture_probe`, `rights_probe`, `geometry` and
`external_boundary`. `contract.json` carries the same blocker, the same missing
artifacts and all eight blocked release gates.

## Exact published candidate

The row is `feasibility` mode with disposition `sdk-model`, and its plan note
requires picking an exact published model and verifying safe closed-loop
behaviour first. The pinned note's neural direct-suppression family predicts a
mask or enhanced speech from howling microphone audio. It reports
**HybridAHS v2 complex-ratio-mask** as the strongest overall trade-off in parts
of the expanded AHS journal study (2024), which builds on the Hybrid AHS
(Interspeech 2023) and NeuralKalmanAHS (Interspeech 2024) publications.

That published variant is the exact pick recorded here as
`hybridahs_v2_complex_ratio_mask`. It is provenance only: the note records no
source implementation or checkpoint in the visible repository listings, and
this workspace contains neither. The related NeuralKalmanAHS and AFC-SPEX
candidates are recorded separately with `qualifies_candidate=false`; the
NeuralKalmanAHS paper numbers are kept as source-reported provenance and are
never attributed to the CRM variant or presented as local measurements.

| Field | Recorded value |
| --- | --- |
| Candidate | HybridAHS v2 complex-ratio-mask |
| Family | Neural direct mask suppression |
| Mechanism | Predicts a complex ratio mask or enhanced speech from howling microphone audio |
| Publications | Hybrid AHS (Interspeech 2023), NeuralKalmanAHS (Interspeech 2024), AHS journal comparison (2024) |
| Source present | **No** |
| Weights present | **No** |
| Runtime present | **No** |
| Checkpoint in public repository listing | **No** |
| Runnable | **No** |
| Local runtime | **Absent** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

## What the task asks and what is proven here

The board row asks to verify runnable source, exact assets, permitted scope,
task geometry and matched evidence, reproduce the exact model/runtime as a
caller-supplied-asset reference, add an opt-in adapter only once prerequisites
pass, and record a concrete blocker when feasibility fails. It also requires
the DSP acceptance profile with exact scope, failure/control results and
remaining release gates.

This package proves only the **negative** side of that gate:

- the exact source/weights/runtime/geometry/rights/fixture prerequisites are
  absent (bounded probes, no network);
- every structurally valid installed-v0-geometry request is rejected with
  `DEFER` because the artifacts and rights are absent;
- invalid, missing, wrong-shape, nonfinite, out-of-range and unverified-geometry
  requests are rejected before any artifact check;
- no model geometry is inferred: the only verified harness geometry is the
  unchanged installed v0 baseline;
- published claims, source-reported metrics and local measurements are kept
  separate, and neither published output nor a local result exists;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that neural direct howling suppression is unsuitable. It
records the exact external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/neural-direct-howling-suppression/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  neural suppressor, provider, descriptor, installed target or public API/ABI
  change exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, model file, weight or audio is read. All harness stimuli are
  analytic or seeded synthetic; they are not candidate output.
- No listening, closed-loop stability, maximum-stable-gain, mask, enhancement,
  feedback-cancellation, device timing, wall-clock playback, benchmark or
  release claim is made.
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
| Gain and response | `profile_mapping.gain_and_frequency_response=blocked_no_candidate_output` | Unmeasured |
| Attack / release | `blocked_no_candidate_output` | Unmeasured |
| Headroom / peaks | `blocked_no_candidate_output` | Unmeasured |
| Delay / content mapping | `blocked_no_documented_geometry` | No delay is assumed or fitted |
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only, not model numerics |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Candidate output | `blocked_source_weights_runtime_geometry_rights_and_fixture_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Pins

Paths outside `docs/task-evidence/neural-direct-howling-suppression/` are
relative to the `audioml` workspace root; SDK boundary paths are relative to
this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | Neural direct suppression family, candidates, source-reported metrics and limits |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `neural-direct-howling-suppression` row, DSP profile, `sdk-model` disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Caller-supplied-asset / opt-in adapter sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
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
cd docs/task-evidence/neural-direct-howling-suppression
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact published model source revision, tree digest and license pin.
2. `RG-02` weights, checkpoints and reproduction.
3. `RG-03` pinned inference runtime.
4. `RG-04` documented task geometry and configuration.
5. `RG-05` code, weight, training-data and output rights.
6. `RG-06` full DSP matrix: gain, response, attack/release, headroom, delay,
   numerical behavior, state transitions and nonlinear configurations.
7. `RG-07` closed-loop stability, maximum stable gain, adverse behavior and
   paced timing.
8. `RG-08` adapter intake, public surface, authorized listening, benchmark
   validation, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
