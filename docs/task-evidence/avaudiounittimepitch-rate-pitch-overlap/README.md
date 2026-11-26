# SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP — closed Apple Audio Unit blocker

`audio-sdk/avaudiounittimepitch-rate-pitch-overlap/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **8** |
| Open exact blockers | **6** |
| Profile | Rate (`plan/swarm/VERIFICATION.md`) |
| Mode | feasibility |
| Pinned base | `aacd6b19b51d4ae2d125ed40488a0e5a8357ec82` |

This directory is a bounded, task-local feasibility package for Apple
`AVAudioUnitTimePitch` (`rate`, `pitch`, `overlap`). It is **not** an
implementation, adapter, provider, benchmark or release. It records why the
candidate cannot be qualified from the artifacts that are actually present,
and it reproduces only declared arithmetic and deterministic synthetic
controls. Nothing here may be promoted to a runtime or quality claim.

## Why DEFER

The pinned inventory record and candidate note are explicit: AVAudioUnitTimePitch
is an Apple OS platform API, its **source is not available**, and its behaviour
can change between OS versions. It is not a library that can be vendored into
this cross-platform SDK. The project workspace contains no pinned Apple runtime
manifest, AVFAudio framework digest, Audio Unit host, AVAudioEngine project,
implementation source, platform licence review, measured render trace or
rights-cleared playback cohort.

Consequently:

- There is no exact, licensed, redistributable implementation/runtime to pin.
- The parameter semantics for `pitch` (cents) and `overlap` are not pinned by
  the candidate note; its rate range is only a documentation report.
- No Apple framework was loaded, no Audio Unit was instantiated, and no
  AVAudioEngine render was run.
- No audio was read or played and no listening, device-timing or benchmark run
  occurred.

Nothing was downloaded and nothing was fabricated. Supplying the missing
artifacts reopens the task; absence of a result is the correct outcome here.

## Exact blockers

| ID | Missing artifact | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Pinned Apple OS/runtime identity | Exact macOS/iOS version and build, architecture, AVFAudio framework SHA-256, recorded host profile and immutable acquisition record. |
| `BLK-02` | Closed implementation identity and terms | Reviewed Apple platform/SDK terms, exact OS-build binding for the `aufx`/`tpit`/`appl` unit, and a pinned public rate/pitch/overlap reference. |
| `BLK-03` | Pinned offline render host | Exact AVAudioEngine/Audio Unit host and toolchain, render mode, sample rate, layout, launch configuration and reproducible build/run record. |
| `BLK-04` | Measured trace and geometry | Official rate/pitch/overlap semantics, defaults, ranges, latency, channel handling and an exact offline render trace including 1x, rate changes, pitch shifts, overlap changes, final partial window and rebuffer. |
| `BLK-05` | Rights-cleared cohort and scorer | Immutable consented speech/music/silence cohort, output-use terms, matched controls and approved pitch/transient preservation labels or scorer. |
| `BLK-06` | Rate acceptance evidence | Measured duration/pitch/overlap/transient/buffering/rebuffer/drift results, blind listening, target-device timing, opt-in intake with OFF default and release review. |

The eight blocked release gates are enumerated in `report.json` under `gates`.
Every gate is `blocked` and `qualifies=false`.

## What is pinned

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless marked
as SDK-worktree relative.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | §2.2 and §4.1 platform API record; closed-source and OS-version caveat. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row `avaudiounittimepitch-rate-pitch-overlap`; Rate profile. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK implementation plan and boundary. |

The required unchanged public boundary is pinned separately: `CONTRACTS.md`,
`api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h`,
`CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml` and `README.md`.
Merged sibling evidence is pinned under `docs/task-evidence/` (granular TSM,
OLA/SOLA, Signalsmith Stretch, Rubber Band R3, browser playbackRate, libsamplerate,
phase vocoder, duration planner, CoreAudio duplex replay, the Apple runtime
probe and the pitch/prosody survey). Exact values are in `SOURCES.sha256` and
`report.json`.

The mutable full `plan/swarm/TASKS.json` is **never hashed**. Only the stable
linked-row projection (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`, `evidence`) is read; board status, claim and review fields gate
nothing.

## Parameter provenance

The candidate note records the parameter **names** and the rate range
`0.03125–32`; it records `pitch` in cents and names `overlap`, but it does not
record numeric pitch/overlap bounds, defaults, latency or algorithm semantics.
The public Apple documentation link is recorded, but no specification text is
present locally.

- `documented_parameter_envelope` in `report.json` therefore leaves numeric
  pitch/overlap bounds and all defaults `null`, and marks
  `semantics_verified_here=false`.
- `synthetic_control_envelope` is a **synthetic validation envelope**
  (rate `1/32–32`, pitch `-2400..2400` cents, overlap `3..32`) used only to
  exercise the fail-closed manifest. It is not runtime evidence and it cannot
  qualify a result.

## Synthetic arithmetic controls

`gate_control` evaluates a declared recipe:

- output duration = source samples / rate for each contiguous rate segment;
- pitch ratio = `2^(cents/1200)` rounded to twelve decimal places;
- `overlap` is validated and recorded, but its audible effect is explicitly
  **not modeled** (`overlap_effect_modeled=false`) because its semantics are
  not pinned;
- final partial window arithmetic uses a declared 1600-sample block.

Cases cover 1x, 2x, 1/2x, ±1200 cents, combined rate and pitch, maximum overlap,
a partial final window, a contiguous rate-change schedule and the minimum rate.
These are labelled `synthetic_contract_control_not_evidence`; every case has
`qualifies=false`.

`frame_control` reproduces the installed v0 16 kHz mono 160-sample frame shape
and rejects non-finite, non-numeric, boolean, wrong-length and out-of-range
inputs with exact codes. No sample is processed by any Apple API.

## Admission and fail-closed behaviour

`admission` validates a caller-authored qualification manifest that requires an
exact OS build and framework digest, the closed `aufx`/`tpit`/`appl` identity,
an offline host identity, a source digest, a mapping block and complete rights.
Every mutation (missing/unknown field, wrong schema, malformed digest,
out-of-range rate/pitch/overlap, non-integer duration, duplicate control, false
rights, non-finite frame value) must be rejected with its expected code and no
state advance. A synthetic manifest can be admitted as a **schema control**
only; it still has `qualifies=false`.

## Reproduce

From this directory, with Python 3.11+ and the standard library only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py all` regenerates `contract.json`, `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires
byte-identical results. `verify.py` re-checks the Rate profile, exact pins,
strict JSON, canonical bytes, all controls, eight blocked gates, licensing,
task-local git scope and three cold-start regenerations. No network, Apple
framework, Audio Unit, AVAudioEngine, audio file or device is used.

## Files

| File | Role |
| --- | --- |
| `reference.py` | Deterministic model, strict JSON, pins, presence probes, controls, contract/report builders. |
| `run.py` | Three-repeat canonical regeneration. |
| `contract.json` | Canonical task contract and pins. |
| `report.json` | Canonical machine-readable DEFER report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `SOURCES.sha256` | SHA-256 pins for all source, boundary, sibling and local files. |
| `test_reference.py` | Standard-library test suite. |
| `verify.py` | Read-only package verifier. |
| `*.license` | REUSE/SPDX sidecars for JSON artifacts. |

## Non-claims

- No result in this package is a qualification, benchmark or release.
- AVAudioUnitTimePitch is closed source and OS-version dependent; no source,
  binary or framework was copied, imported or loaded.
- No Apple OS runtime identity, AVFAudio digest, Audio Unit host or
  AVAudioEngine render was present or measured.
- No rate, pitch, overlap, duration, transient, buffering, rebuffer, drift or
  final-partial result was measured.
- No audio was read or played; no cohort, consent or output-use grant exists.
- No listening, target-device timing, resource, benchmark or release review was
  performed.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI,
  shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
