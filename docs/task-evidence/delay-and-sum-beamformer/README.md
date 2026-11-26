<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DELAY-AND-SUM-BEAMFORMER — source/runtime and real-array blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Delay-and-sum beamformer` (`component_id=delay-and-sum-beamformer`). The
acceptance profile is **Spatial**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked, surrogate or rejected
result may never qualify the component.

The catalogued candidate source, runtime, adapter, immutable revision, licence
identity, numeric output and rights-cleared synchronized array corpus are
**absent**. This package records that exact blocker and runs a bounded
deterministic **author-written synthetic equal-weight delay-and-sum baseline**
on frozen integer geometries. It is **not** the catalogued `S24`
(Pyroomacoustics) candidate, does not import, load, vendor or download
Pyroomacoustics or any beamformer runtime, and makes no beamforming-quality,
localization, leakage, listening, device-timing, benchmark or release claim.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=delay-and-sum-beamformer`) is
`considered`, `disposition=sdk-reference`, `verification_profile=spatial`, with
the plan note “Use synchronous calibrated channels and a declared reference
channel.” The only evidence link is `research/category_registry.json`, where
category `CLN-07` maps the classic delay-and-sum family to source lead **`S24`**
(“Pyroomacoustics beamforming implementation”) with
`access_scope="search excerpt"`. The merged `survey-cln-07` map records the
same boundary: delay-and-sum is *catalogued* and has **no local implementation,
fixture, execution or metric record** (gap `G01`), and no pinned source,
package, executable, licence grant or array recording is staged.

Consequently:

- no exact delay-and-sum source tree, package, archive, executable, runtime,
  adapter or immutable revision is staged at `data/checkouts`, `data/envs`,
  `data/models` or `adapters`;
- no licence identity, artifact hash, build identity or adapter setting exists
  for the `S24` candidate itself;
- no rights-cleared synchronized real multichannel recording, geometry
  manifest, calibration file, consent/usage grant or target/reference condition
  is staged;
- no measured device synchronization, clock offset/drift, channel loss or
  target-device deadline exists;
- no task-matched held-out localization/activity/extraction labels, leakage,
  target-damage or channel-loss scorer, independent review, provider intake or
  release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DELAY-AND-SUM-BEAMFORMER`, `91c16ba867dd9cba8a41bd9202d00712d409277a` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Surrogate geometry | 2–16 channels, 16 kHz, synthetic integer-nanometre geometry only |
| Steered channels | synchronous only, `clock_ppm == 0`, unity `calibration_gain_q16` |
| Added content delay | 0 samples; steering is an explicit q16 shift |
| Provider registration, default, ABI, CI | none |

The included baseline exercises strict parsing, exact plane-wave steering
arithmetic, equal-weight summation, streaming-boundary padding, identity and
adverse rejection. It is **not** the catalogued candidate and cannot establish
exact-runtime parity. A synthetic baseline addresses only survey gap `G01`
(“implement and execute a deterministic delay-and-sum baseline on a frozen
synthetic array fixture with declared geometry and steering”); it closes no
source, rights, corpus, device, scoring or release gate.

## Exact arithmetic

- Microphone positions and steering components are integers.
- Positions use **nanometres**; bounds are ±10 m per axis and 2–16 unique
  microphones.
- The speed of sound is pinned to **343 nm/ns** (343 m/s).
- One 16 kHz sample is exactly **62,500 ns**, following the `CONTRACTS.md`
  timing record.
- A steering direction is an integer vector whose squared norm is a perfect
  square, so the unit vector is rational and exact; no floating-point
  trigonometry or platform-dependent `sin`/`cos` is used.
- Plane-wave time difference for microphone `i` relative to the declared
  reference is `tdoa_i = -(d_i · u) / c` with `d_i` in nm and `c = 343 nm/ns`.
- The steering delay is a fixed-point `q16` sample value
  `relative_q16_i = (tdoa_i - tdoa_ref) * 65536 / 62,500`. A delay on an
  integer sample is exact; a non-integral residual uses fixed-point linear
  interpolation and is labelled a **surrogate**, never a sub-sample
  qualification result.
- The beamformer output is the arithmetic mean of the aligned channels:
  `y[n] = (1/N) * Σ x_i[n + relative_q16_i/Q16]`. Weights are equal `1/N`;
  there is no adaptive coefficient, mask, covariance estimate or learned
  parameter.
- Nonzero `clock_ppm`, non-unity `calibration_gain_q16`, unknown or duplicate
  channels, non-normalizable directions and non-finite samples are rejected.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry and layout | synthetic only | Two frozen integer geometries: 3-mic linear and 4-mic planar; no measured array, orientation or device layout |
| Timestamp calibration | synthetic only | Explicit integer ns steering with synchronous, unity-gain channels; drift and non-unity calibration rejected; no measured device clock |
| Source/target/reference conditions and permissions | blocked | No real recording, condition, consent or usage grant |
| Task-matched held-out localization/activity/extraction | blocked | No labels, output or scorer; this is a delay-and-sum arithmetic baseline only |
| Leakage, target damage, channel loss | blocked | No real target or interference stratum; the steering-mismatch case is a synthetic control only |
| Room/reference changes | blocked | No measured room or reference change; adjacent WPE evidence is not pooled |

## Frozen synthetic cases

All cases are generated from integer arithmetic and stay under
`docs/task-evidence/delay-and-sum-beamformer/`. The reference channel is `m0`;
a target click arrives at the declared reference index and every channel must
align to that index before equal-weight summation.

| Case | Microphones | Steering | Declared relative samples | Click index | Output peak | Expected | Max amplitude error |
| --- | --- | --- | --- | ---: | ---: | ---: | ---: |
| `linear_3mic_endfire` | 3 linear, 21.4375 mm spacing | `(1,0,0)` | `0, -1, -2` | 8 | 0.5 | 0.5 | 0.0 |
| `planar_4mic_oblique` | 4 planar, 107.1875 mm × 26.796875 mm grid | `(3,4,0)`, norm 5 | `0, -1, -3, -4` | 16 | 0.5 | 0.5 | 0.0 |
| `fractional_half_sample_control` | 3 linear, ±10.71875 mm | `(1,0,0)` | `0, -0.5, +0.5` | 8 | 0.5666666667 | 0.8 | surrogate |
| `steering_mismatch_control` | 3 linear (fixture from `+x`) | steered to `-x` | `0, +1, +2` | 8 | 0.25 | 0.5 | control |

Both exact cases recover the declared reference index and the equal-weight mean
bit-exactly (`max_abs_amplitude_error = 0.0`). The fractional control is
`arithmetic_exact_only=false` and `status=surrogate_only_not_qualified`; its
half-sample linear interpolation attenuates the synthetic click and is
reported, not promoted. The steering-mismatch case is
`status=control_only_not_qualified`; steering to the opposite direction breaks
coherent summation and halves the observed peak (ratio `0.5`). The identity
control uses four synchronous unity-gain channels with zero steering delay and
returns the input sequence bit-identically (`bit_identical=true`).

## Adverse, missing and invalid handling

`report.json` records 31 rejected inputs, each with an unchanged synthetic
state. Rejections include duplicate microphone position or ID, unknown
reference, non-integer or out-of-range position, non-normalizable or zero
steering direction, unsupported rate or speed, missing/duplicate/unknown
channel, nonzero clock drift, non-unity or non-integer channel calibration,
extra geometry field, too many microphones, nonfinite or wrong-type samples,
length/channel mismatch, empty channel, oversized sample, out-of-range click,
bad amplitude count/type/nonfinite amplitude, invalid source time, duplicate
JSON key, NaN/Infinity JSON constant and malformed JSON. Missing reference
channels, missing real recordings and delayed/missing real references are
`blocked`, not passes.

## Reproduction

```sh
cd docs/task-evidence/delay-and-sum-beamformer
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` performs three cold-start rounds and refuses to accept non-identical
report, contract or source bytes. `verify.py` is read-only and fails closed on
stale pins, non-canonical JSON, a promoted fractional or mismatch control, a
qualified claim, an unblocked release gate, a license gap, out-of-scope changes
or `git diff --check` damage. Expected: all tests pass and `verify.py` prints
`pins_ok=… json_ok=2 report_sha256=… repeats_ok=3 licensing_ok=1 scope_ok=1`.

Canonical `report.json` SHA-256:
`9dce5b38ce76197c1650af10c6c4fb3dad4f454e8d87d60d807cdde85b8f8af2`.

## Release gates and reopening

All eight gates are `blocked`: exact licensed source/runtime (`RG-01`),
measured geometry/calibration and reference channel (`RG-02`), rights-cleared
synchronized real corpus (`RG-03`), exact-runtime parity (`RG-04`), measured
device synchronization/drift/channel loss (`RG-05`), task-matched held-out
spatial scoring (`RG-06`), opt-in provider intake and independent review
(`RG-07`), and default/release approval (`RG-08`).

Reopen only with a rights-cleared real multichannel corpus, one pinned licensed
delay-and-sum source/runtime with exact adapter settings, exact-runtime parity
on known synthetic steering delays, measured device synchronization and drift,
held-out spatial scoring including leakage, target damage and channel loss, and
independent opt-in provider review. Until then the decision stays `DEFER`, the
evidence stays `incomplete`, and no result may qualify.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This boundary record |
| `reference.py` | Stdlib-only synthetic equal-weight delay-and-sum baseline and strict validation |
| `test_reference.py` | Deterministic arithmetic, rejection and report tests |
| `run.py` | Three-round byte-identical regeneration of report, contract and pins |
| `verify.py` | Read-only strict verifier |
| `report.json` / `.sha256` | Canonical report and its SHA-256 |
| `contract.json` | Machine-readable disposition, blockers, gates and pins |
| `SOURCES.sha256` | Exact source, boundary and artifact pins |
| `*.license` | SPDX sidecars for generated non-Python files |

No provider, descriptor, registry, installed v0 behavior, ABI, default, shared
build, CI workflow, board row or handoff is changed.
