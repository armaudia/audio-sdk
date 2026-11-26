<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ESPRESSIF-NSNET3: Espressif NSNet3 feasibility blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Espressif NSNet3 row. It is **not** ESP-SR and **not** NSNet3: no vendor
source, model, graph, header, configuration, object code, firmware, license
text, runtime, rights-cleared cohort, scorer, listening result, device
measurement, benchmark or release claim is included. **No result here
qualifies the candidate.**

## Exact blocker: source, model, terms, runtime, geometry and cohort absent

A bounded, read-only search of named workspace paths found **no `esp-sr`
checkout**, **no NSNet3 model or graph artifact**, **no local code/model terms
text**, **no ESP-IDF or ESP-SR toolchain**, **no licensed portable host
runtime**, **no pinned configuration** and **no rights-cleared matched
cohort**. Nothing was cloned, downloaded, extracted, ported,
reverse-engineered or substituted.

The pinned census records only that official ESP-SR documentation describes a
tiny 16 kHz, low-power embedded noise suppressor with 48.2k parameters and a
32 ms frame / 16 ms hop, and that NSNet3 is a special-target candidate not
directly comparable to a desktop CPU pilot until a portable adapter exists. It
records no revision, digest, code/model terms, training-data provenance,
runtime lock, delay, memory, latency or quality result. None was invented.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local `esp-sr` copy; revision, tree digest, file count and license file are `null` |
| Model artifact | **Absent.** No NSNet3 model/graph path, byte count, SHA-256, conversion recipe, precision or quantization |
| Code/model/training-data terms | **Absent/blocked.** No terms text, digest or written rights decision; the pinned census records no terms |
| Eligible runtime | **Absent/unpinned.** No ESP-IDF/ESP-SR toolchain, lockfile, reproducible firmware or licensed portable host runtime |
| Configuration | **Absent.** No pinned header or configuration declaring channel handling, features, output mapping, delay, reset/drain or quantization |
| Matched cohort and scorer | **Absent.** No rights-cleared paired noisy/clean speech, approved SI-SDR/STOI implementation or authorized listening |
| Candidate execution | **None.** No build, flash, inference, denoising, quality, timing or listening run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_model_terms_runtime_and_matched_cohort_absent"`, with
every digest and byte count `null`), `required_artifacts` (A1-A8),
`source_probe`, `weights_probe`, `license_probe`, `hardware_probe`,
`runtime_probe`, `cohort_probe`, `scorer_probe`, `rights_probe`, `geometry`,
`model_boundary` and `enhancement_control`. `contract.json` carries the same
blocker, the same missing artifacts and all eight blocked release gates.

## Model boundary

| Field | Recorded value |
| --- | --- |
| Vendor | Espressif Systems |
| Component | ESP-SR NSNet (NSNet3) |
| Version | NSNet3, unpinned revision |
| SDK disposition | `sdk-model` |
| Distribution model | ESP-SR component for embedded targets |
| Declared target | ESP-SR supported embedded target |
| Host target here | macOS / Python 3 workspace |
| Host target eligible | **No** (no portable adapter or portable runtime) |
| Reported parameters | 48.2k (census/source-reported, not measured here) |
| Reported geometry | 16 kHz, 32 ms frame, 16 ms hop (source-reported) |
| Local terms name | **None recorded** |
| Use/redistribution approved | **No** |
| Local runtime | **Absent** |
| Weights present | **No** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

Only the single 16 kHz rate, the 32 ms frame and the 16 ms hop are recorded by
the pinned census. The validator uses the arithmetic 512-sample frame and
256-sample hop at 16 kHz solely to exercise validation and rejection; they are
**not** pinned vendor API constants. Channel handling, feature extraction,
output mapping, buffering delay, reset/drain semantics and quantization are
absent and were not inferred. A request with any other rate, frame or hop is
rejected with `RATE_NOT_RECORDED`, `WRONG_DECLARED_FRAME` or
`WRONG_DECLARED_HOP`; that is a local evidence limit, not a claim about the
vendor API.

## What the task asks and what is proven here

The board row is `feasibility` mode. It asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence, then reproduce
the exact model/runtime as a caller-supplied-asset reference and add an opt-in
SDK adapter once its prerequisites pass. The inventory assigns disposition
`sdk-model` and the **Enhancement** acceptance profile. It also requires a
concrete blocker if feasibility fails.

This package proves only the **negative** side of that gate:

- the exact source/model/terms/runtime/cohort/scorer prerequisites are absent
  (bounded probes, no network);
- the only documented facts are the 16 kHz rate, 32 ms frame, 16 ms hop,
  48.2k parameters and embedded target support; nothing else is inferred;
- every structurally valid documented-geometry request is rejected with
  `DEFER` because the artifacts and rights are absent;
- invalid, missing, wrong-shape, nonfinite, out-of-range and unrecorded-
  geometry requests are rejected before any artifact check;
- the declared 512/256 geometry is not representable by installed v0 without
  an adapter;
- source-reported characteristics are kept separate from local measurements,
  and neither vendor output nor a local result exists;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Espressif NSNet3 is unsuitable. It records the exact
external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/espressif-nsnet3/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, provider registration, board/handoff files, CI, rulesets and
  `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  NSNet3 provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, model, weights, graph or vendor file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, memory, latency, quality,
  benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim, history and every other mutable field never enter
  canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## Enhancement profile application

The structured inventory assigns the **Enhancement** acceptance profile
(`plan/swarm/VERIFICATION.md`, pinned below). The profile asks for an
identity/noisy control, an established task-matched baseline, paired SI-SDR
and STOI where permitted clean references exist, clean-speech preservation,
peaks and invalid outputs, alignment, state, memory and measured content/
availability timing, and a separately labeled predictive screen or authorized
listening for unpaired speech.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Identity / noisy control | `enhancement_control.identity_noisy_control=null` | No candidate output |
| Task-matched baseline | `blocked_no_permitted_baseline` | No baseline run |
| Paired SI-SDR / STOI | `scorer_probe` and `scorer` mark unapproved | No scorer implemented or applied |
| Clean-speech preservation | `blocked_no_permitted_cohort` | Unmeasured |
| Peaks / invalid outputs | `partial_local_harness_rejection_only` | Local rejection tests only |
| Alignment / content delay | `blocked_no_candidate_instance` | No delay assumed or fitted |
| State / reset / drain | `blocked_no_candidate_instance` | No instance exists |
| Memory | `blocked_no_paced_measurement` | Unmeasured |
| Availability timing | `blocked_no_paced_measurement` | Unmeasured |
| Unpaired speech | `blocked_no_permitted_cohort_or_panel` | No screen or panel |
| Candidate output | `blocked_source_model_terms_runtime_and_matched_cohort_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Pins

Paths outside `docs/task-evidence/espressif-nsnet3/` are relative to the
`audioml` workspace root; SDK boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | NSNet3 census row: 16 kHz, 48.2k parameters, 32 ms frame, 16 ms hop, embedded target and comparability note |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `espressif-nsnet3` row, Enhancement profile, `sdk-model` disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Caller-supplied-asset / opt-in adapter sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile |
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
cd docs/task-evidence/espressif-nsnet3
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact ESP-SR source revision, tree digest and license pin.
2. `RG-02` exact NSNet3 model/graph artifact, conversion recipe and digest.
3. `RG-03` code/model/training-data terms and a written rights decision.
4. `RG-04` eligible target or licensed portable runtime with a pinned
   toolchain and reproducible artifact.
5. `RG-05` pinned declared geometry, features, configuration and delay.
6. `RG-06` caller-supplied reference reproduction, reset/drain and state
   parity.
7. `RG-07` full Enhancement matrix on a rights-cleared matched cohort with an
   approved scorer, plus adverse, state, memory and paced timing results.
8. `RG-08` opt-in adapter intake, public surface, authorized listening,
   benchmark validation, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
