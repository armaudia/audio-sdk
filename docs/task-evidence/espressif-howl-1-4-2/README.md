<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ESPRESSIF-HOWL-1-4-2: Espressif HOWL 1.4.2 external-adapter blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Espressif HOWL 1.4.2 row. It is **not** Espressif HOWL: no vendor source,
header, configuration, object code, firmware, license text, runtime, eligible
hardware, matched closed-loop recording, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies the
candidate.**

## Exact blocker: source, license decision, hardware, runtime and fixture absent

A bounded, read-only search of named workspace paths found **no
`esp_audio_effects` HOWL 1.4.2 checkout**, **no local license text**, **no
ESP-IDF toolchain or lock**, **no approved ESP32-S3R8 runner** and **no matched
closed-loop fixture**. Nothing was cloned, downloaded, extracted, ported,
reverse-engineered or substituted.

The pinned research note also records that the v1.4.2 published Espressif
Modified MIT terms restrict use to Espressif products and prohibit
redistribution for non-Espressif products. That reported restriction makes this
macOS/Python target ineligible without a written license/platform decision,
independently of whether the source is present.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local copy of `esp_audio_effects` HOWL 1.4.2; revision, tree digest, file count and license file are `null` |
| License text and decision | **Absent/blocked.** The restriction is source-reported only; no byte-identical license text, SHA-256 or written non-Espressif use/redistribution approval exists |
| Eligible hardware | **Absent.** No approved ESP32-S3R8 runner, attached device, firmware image or measurement setup |
| Runtime | **Absent/unpinned.** No ESP-IDF checkout, toolchain, lockfile, version or reproducible firmware digest |
| Configuration | **Absent.** No pinned HOWL header or default configuration declaring thresholds, notch limits, channel bound or frame geometry |
| Matched fixture | **Absent.** No rights-cleared loudspeaker-to-microphone closed-loop recording with measured gain, delay and saturation |
| Candidate execution | **None.** No build, flash, detector, notch, margin, timing or listening run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_license_hardware_runtime_and_fixture_absent"`, with
every digest and byte count `null`), `required_artifacts` (A1-A6),
`source_probe`, `license_probe`, `hardware_probe`, `runtime_probe`,
`fixture_probe`, `rights_probe`, `geometry` and `external_boundary`.
`contract.json` carries the same blocker, the same missing artifacts and all
eight blocked release gates.

## Vendor boundary

| Field | Recorded value |
| --- | --- |
| Vendor | Espressif Systems |
| Component | `esp_audio_effects` HOWL |
| Version | 1.4.2 |
| Distribution model | ESP-IDF/SoC component, not a portable host library |
| Eligible target | ESP32-S3R8 / ESP-IDF |
| Host target here | macOS / Python 3 workspace |
| Host target eligible | **No** |
| Reported license | Espressif Modified MIT License (v1.4.2) |
| Reported restriction | Use limited to Espressif products; non-Espressif redistribution prohibited (source-reported, not locally verified) |
| Local runtime | **Absent** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

The documented policy is a design reference only: FFT-based per-bin PAPR,
PHPR, PNPR and optional IMSD criteria, dynamic biquad notches and a loop-margin
gain controller that reduces global gain and restores it gradually. The pinned
note records support at 8, 16, 24, 32, 44.1 and 48 kHz, fixed 512-sample frames
at 16 kHz and 1024-sample frames at 48 kHz, and independent per-channel
operation. Vendor CPU and memory figures are for ESP32-S3R8/ESP-IDF and are
**not** generalized to this workstation.

Only the 16 kHz/512 and 48 kHz/1024 frame sizes are stated by the pinned note.
The 8, 24, 32 and 44.1 kHz frame sizes, the channel bound and every threshold
are **not** recorded and were not invented. A structurally valid request at an
unverified rate is rejected with `UNVERIFIED_FRAME_GEOMETRY`; that is a local
evidence limit, not a claim that the vendor rate is unsupported.

## What the task asks and what is proven here

The board row is `external-adapter` mode. It asks to document the vendor
boundary, prototype an isolated adapter only if an approved public or
user-supplied runtime is available, use the documented detector/notch/margin
policy as reference, and scope any executable comparator to eligible hardware
and approved terms. It also requires the DSP acceptance profile, exact scope,
failure/control results and remaining release gates.

This package proves only the **negative** side of that gate:

- the exact source/license/hardware/runtime/fixture prerequisites are absent
  (bounded probes, no network);
- the reported v1.4.2 terms do not approve this non-Espressif macOS/Python
  target or redistribution;
- every structurally valid documented-geometry request is rejected with
  `DEFER` because the artifacts and rights are absent;
- invalid, missing, wrong-shape, nonfinite, out-of-range and unverified-frame
  requests are rejected before any artifact check;
- the declared external component and its multi-rate/fixed-frame geometry
  cannot be represented by installed v0;
- vendor claims, source-reported characteristics and local measurements are
  kept separate, and neither vendor output nor a local result exists;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Espressif HOWL 1.4.2 is unsuitable. It records the
exact external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/espressif-howl-1-4-2/`. Shared
  CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  HOWL provider, descriptor, installed target or public API/ABI change exists.
  There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, firmware, weights or vendor file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain,
  detector, notch, loop-margin, feedback-cancellation, benchmark or release
  claim is made.
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
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only, not vendor numerics |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Candidate output | `blocked_source_license_hardware_runtime_and_fixture_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Pins

Paths outside `docs/task-evidence/espressif-howl-1-4-2/` are relative to the
`audioml` workspace root; SDK boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` | HOWL 1.4.2 algorithm, rates, frame, license and platform finding |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `espressif-howl-1-4-2` row, DSP profile, external-adapter disposition |
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
cd docs/task-evidence/espressif-howl-1-4-2
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact v1.4.2 source revision, tree digest and license pin.
2. `RG-02` written non-Espressif use and redistribution decision for this host.
3. `RG-03` eligible ESP32-S3R8 hardware and hash-pinned ESP-IDF runtime.
4. `RG-04` pinned declared geometry, headers and configuration.
5. `RG-05` detector, notch and loop-margin reproduction with reset/drain.
6. `RG-06` full DSP matrix: gain, response, attack/release, headroom, delay,
   numerical behavior, state transitions and nonlinear configurations.
7. `RG-07` closed-loop stability, maximum stable gain, adverse behavior and
   paced device timing.
8. `RG-08` external adapter intake, public surface, authorized listening,
   benchmark validation, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
