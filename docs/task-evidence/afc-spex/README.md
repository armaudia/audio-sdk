<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-AFC-SPEX: AFC-SPEX feasibility blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local feasibility evidence for the `afc-spex` row. It is
**not** AFC-SPEX: no source, model config, checkpoint, weight, three-channel
recording, runtime, feature output, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies AFC-SPEX.**

## Exact blocker: source, config, checkpoint, matched input and runtime absent

A bounded, read-only search of named workspace paths found **no local AFC-SPEX
checkout**, **no `model_config.yaml` or `infer_config.yaml`**, **no pretrained
checkpoint**, **no three-channel matched input** and **no hash-pinned runtime**.
Nothing was cloned, downloaded, reconstructed, upmixed or substituted.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local copy of `https://github.com/ZLiNJU/AFC-SPEX`; revision, tree digest, file count and license file are `null` |
| Model / inference config | **Absent.** `afcspex/configs/model_config.yaml` and `afcspex/configs/infer_config.yaml` are not present, so rate, hop, frame, layers and preprocessing remain unverified |
| Pretrained checkpoint | **Absent.** Only the pinned research note records an author-local experiment path; no resolved path, SHA-256, byte count or weight terms exist |
| Three-channel matched input | **Absent.** The pinned note records three required microphone channels and a mono AMI source; a mono excerpt is not matched and is never upmixed or duplicated |
| Runtime | **Absent/unpinned.** No AFC-SPEX runtime, lockfile or wheel set exists; import checks report only the current interpreter |
| Rights | **Unrecorded/blocked.** Repository license, checkpoint weight terms, input corpus permission and redistribution scope are not recorded locally |
| Candidate execution | **None.** No model load, feature extraction, howling suppression, timing or listening run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_checkpoint_input_and_runtime_absent"`, with every
digest and byte count `null`), `required_artifacts` (A1-A6),
`source_probe`, `checkpoint_probe`, `input_probe`, `runtime_probe`,
`rights_probe` and `geometry`. `contract.json` carries the same blocker, the
same missing artifacts and all eight blocked release gates.

## What the task asks and what is proven here

The board row is feasibility mode and asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence before reproducing
the model as a caller-supplied-asset reference and adding an opt-in adapter
once prerequisites pass. The row also requires an exact pretrained checkpoint
and three-channel matched input, and requires the speaker-extraction result to
stay separate from mono howling control.

This package proves only the **negative** side of that gate:

- the exact source/config/checkpoint/input/runtime/rights prerequisites are
  absent (bounded probes, no network);
- every structurally valid three-channel request is rejected with `DEFER`
  because the artifacts are absent;
- invalid, missing, wrong-shape, nonfinite and out-of-range requests are
  rejected before any artifact check;
- the declared three-channel task cannot be represented by installed v0 mono;
- speaker extraction and mono howling control are separate, non-interchangeable
  result classes and neither is measured;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that AFC-SPEX is unsuitable. It records the exact external
condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/afc-spex/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, provider registration, board/handoff files, CI, rulesets and
  `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  AFC-SPEX provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider.
- No provider is registered, enabled by default or selected as a default.
- No real corpus or weights are read. All harness stimuli are analytic or
  seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain,
  feedback-cancellation, benchmark or release claim is made.
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
| Delay / content mapping | `blocked_no_candidate_output` | No delay is assumed or fitted |
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only, not model numerics |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Candidate output | `blocked_source_checkpoint_input_runtime_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Task separation

- `speaker_extraction` records the declared multichannel target-speaker
  extraction task. It is blocked, has no metrics and
  `may_be_reported_as_mono_howling_control=false`.
- `mono_howling_control` is `not_evaluated_by_this_task`; it has no metrics,
  no maximum-stable-gain claim and no feedback-cancellation claim.
- `task_separation_enforced=true` and `no_missing_result_qualifies_candidate=true`.

A future AFC-SPEX extraction result must never be presented as mono howling
control evidence, and a mono howling control must never be presented as
AFC-SPEX extraction evidence.

## Pins

Paths outside `docs/task-evidence/afc-spex/` are relative to the `audioml`
workspace root; SDK boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | AFC-SPEX three-channel / author-local checkpoint finding |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `afc-spex` row, DSP profile, blocked status |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Feasibility / caller-supplied-asset sequence |
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
cd docs/task-evidence/afc-spex
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact source revision, tree digest and license pin.
2. `RG-02` exact pretrained checkpoint, SHA-256/byte count and weight rights.
3. `RG-03` rights-qualified three-channel matched input and pinned geometry.
4. `RG-04` hash-pinned runtime and install/import parity.
5. `RG-05` exact model reproduction: parameter identity, delay, state/reset,
   finite drain and execution modes.
6. `RG-06` full DSP matrix: gain, response, attack/release, headroom, delay,
   numerical behavior, state transitions and nonlinear configurations.
7. `RG-07` separation of multichannel speaker extraction from mono howling
   control, with held-out talkers, rooms/paths and matched controls.
8. `RG-08` multichannel provider intake/public surface, paced timing, memory,
   callback suitability, authorized listening, benchmark validation,
   independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
