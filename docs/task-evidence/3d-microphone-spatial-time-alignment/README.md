<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT — geometry / asynchronous-reference blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`3D microphone spatial / time alignment`
(`component_id=3d-microphone-spatial-time-alignment`). The acceptance profile is
**Spatial**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
component.

The package records the exact geometry, layout, timestamp, real-recording,
runtime and rights requirements, then runs a bounded deterministic **integer
geometry / asynchronous-reference alignment surrogate** on synthetic channels.
It is **not** the catalogued candidate, contains no licensed spatial source, no
real array audio, no runtime, no device calibration, no listening test and no
benchmark. It changes no provider, descriptor, registry, installed v0 behavior,
ABI, default, shared build, CI, board row or handoff. Only this task-local
directory is added.

## Exact blocker

No rights-cleared synchronized real 3-D microphone-array asset is staged:

- no recording with microphone positions, orientation, calibration and channel
  timestamps;
- no source/target/reference direction, movement, channel-loss or
  room/reference-condition stratum;
- no consent, usage grant, corpus terms or redistribution permission;
- no exact licensed implementation or runtime, and no immutable revision or
  adapter settings to reproduce;
- no measured device synchronization, clock offset/drift or deadline;
- no task-matched held-out localization/activity/extraction labels, leakage or
  target-damage score and no independent review.

The pinned workspace contains adjacent synthetic two-channel WPE fixtures with
declared geometry and mono 16/48 kHz listening WAVs only. The pinned
`agent-transform-spatial-trials` follow-up reports no compatible multichannel
speaker target corpus, no staged spatial model and no array geometry. Those are
not array calibration, not a 3-D capture and not this component. Source leads
`S24` (Pyroomacoustics beamforming), `S25` (TorchAudio mask-based MVDR) and
`S26` (Pyroomacoustics direction of arrival) are search excerpts, not staged
packages, runtimes, geometry or numeric outputs. The exact blockers and eight
blocked release gates are machine-readable in `contract.json` and
`report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT`, `0eec1f8f9fa420cbae18501583897f4b5faaaf2d` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Model boundary | 2–16 channels, 16 kHz, synthetic samples only |
| Added content delay | 0 samples; alignment is an explicit shift |
| Clock drift | not supported; nonzero `clock_ppm` is rejected |
| Provider registration, default, ABI, CI | none |

This package models only **geometry bookkeeping and time alignment**. It does
not localize, track, beamform, separate, extract a target or score quality. It
does not claim that a delay computed from a declared geometry equals an
installed runtime's behavior.

## Exact arithmetic

- Microphone positions and direction components are integers.
- Positions use **nanometres**; bounds are ±10 m per axis and 2–16 unique
  microphones.
- The speed of sound is pinned to **343 nm/ns** (343 m/s).
- One 16 kHz sample is exactly **62,500 ns**, following the `CONTRACTS.md`
  timing record.
- A direction is an integer vector whose squared norm is a perfect square, so
  the unit vector is rational and exact; no floating-point trigonometry or
  platform-dependent `sin`/`cos` is used.
- Plane-wave time difference for microphone `i` relative to the declared
  reference is `tdoa_i = -(d_i · u) / c` with `d_i` in nm and `c = 343 nm/ns`.
- The asynchronous-reference offset is an explicit integer `capture_offset_ns`
  per channel. The aligned q16 sample shift is
  `relative_q16_i = ((tdoa_i - offset_i) - (tdoa_ref - offset_ref)) * 65536 / 62500`.
- An integer-sample alignment is exact and is the only result class used in the
  synthetic acceptance table. A non-integral residual is applied with
  fixed-point linear interpolation and is labelled a **surrogate**, never a
  sub-sample qualification result.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry and layout | synthetic only | Two frozen integer geometries: 3-mic linear and 4-mic planar; no measured array or device layout |
| Timestamp calibration | synthetic only | Explicit integer ns capture offsets; drift rejected; no measured device clock |
| Source/target/reference conditions and permissions | blocked | No real recording, condition or consent/usage grant |
| Task-matched held-out localization/activity/extraction | blocked | No labels, output or scorer; this is time alignment only |
| Leakage, target damage, channel loss | blocked | No real target or interference stratum; only synthetic integer alignment |
| Room/reference changes | blocked | No measured room or reference change; WPE evidence is not pooled |

## Frozen synthetic cases

All cases are generated from integer arithmetic and stay under
`docs/task-evidence/3d-microphone-spatial-time-alignment/`. The reference
microphone is `m0`; an `m0` click appears at a declared index and every other
channel must land on the same aligned index.

| Case | Microphones | Direction | Declared relative samples | Click index | Recovered peak | Max amplitude error |
| --- | --- | --- | --- | ---: | --- | ---: |
| `linear_3mic_axis` | 3 linear, 21.4375 mm spacing | `(1,0,0)` | `0, -3, -1` | 8 | `8, 8, 8` | 0.0 |
| `planar_4mic_pythagorean` | 4 planar, 34.3 mm grid | `(3,4,0)`, norm 5 | `0, -1, -2, -3` | 16 | `16, 16, 16, 16` | 0.0 |
| `fractional_half_sample_control` | 3 linear, ±10.71875 mm | `(1,0,0)` | `0, -0.5, +0.5` | 8 | `8, 8, 8` | surrogate |

The exact cases recover the declared click index and amplitude bit-exactly
(`max_abs_amplitude_error = 0.0`). The fractional control is
`exact=false` and `status=surrogate_only_not_qualified`; its half-sample
linear interpolation attenuates the synthetic click to `0.3` and `-0.2` and is
reported, not promoted. The reference microphone identity control is
bit-identical to its input.

## Adverse, missing and invalid handling

`report.json` records 23 rejected inputs, each with an unchanged synthetic
state. Rejections include duplicate microphone position or ID, unknown
reference, non-integer or out-of-range position, non-normalizable or zero
direction, unsupported rate or speed, missing/duplicate/unknown channel,
nonzero clock drift, out-of-range capture offset, extra geometry field,
nonfinite or wrong-type samples, length/channel mismatch, empty channel,
duplicate JSON key, NaN/Infinity JSON constant and malformed JSON. Missing
reference channels, missing real recordings and delayed/missing real references
are `blocked`, not passes.

## Reproduction

```sh
cd docs/task-evidence/3d-microphone-spatial-time-alignment
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` performs three cold-start rounds and refuses to accept non-identical
report, contract or source bytes. `verify.py` is read-only and fails closed on
stale pins, non-canonical JSON, a promoted fractional result, an unblocked
release gate, a license gap, out-of-scope changes or `git diff --check`
damage. Expected: 60 tests pass and `verify.py` prints
`pins_ok=… json_ok=2 report_sha256=… repeats_ok=3 licensing_ok=1 scope_ok=1`.

## Release gates and reopening

All eight gates are `blocked`: exact geometry/calibration (RG-01), pinned source
or runtime (RG-02), rights-cleared synchronized real corpus (RG-03),
exact-runtime parity (RG-04), measured device synchronization/drift/channel loss
(RG-05), task-matched held-out scoring incl. leakage and target damage (RG-06),
opt-in provider intake and independent review (RG-07), and default/release
approval (RG-08).

Reopen only with a rights-cleared real array corpus, one pinned licensed or
device-authoritative source/runtime, exact-runtime parity on known synthetic
delays, measured device synchronization and drift, held-out scoring, and
independent opt-in provider review. Until then the decision stays `DEFER`,
the evidence stays `incomplete` and no result may qualify.
