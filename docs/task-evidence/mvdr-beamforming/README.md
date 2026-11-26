<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-MVDR-BEAMFORMING — source/runtime, mask and real-array blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`MVDR beamforming` (`component_id=mvdr-beamforming`). The acceptance profile is
**Spatial**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked, surrogate or rejected
result may never qualify the component.

No licensed MVDR/MPDR source, package, runtime, adapter, immutable revision,
licence grant, mask estimator, covariance estimator, immutable asset or
rights-cleared synchronized array corpus is staged. This package records that
exact blocker and runs a bounded deterministic **validator + frozen synthetic
fixture with an exact equal-weight delay-and-sum control**. It implements **no
MVDR beamformer**: no covariance matrix is estimated, no mask is applied, no
steering vector is fitted and no beamformed output exists. It is not the
catalogued `S24` (Pyroomacoustics) or `S25` (TorchAudio mask-based MVDR)
candidate, does not import, load, vendor or download either, and makes no
beamforming-quality, mask-quality, distortion, localization, leakage,
listening, device-timing, benchmark or release claim. Only this task-local
directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=mvdr-beamforming`) is
`considered`, `disposition=sdk-model`, `verification_profile=spatial`, with the
plan note “Validate masks, reference timing, channel calibration and distortion
against delay-and-sum.” The only evidence link is
`research/category_registry.json`, where category `CLN-07` maps MVDR/MPDR to
source leads **`S24`** (“Pyroomacoustics beamforming implementation”) and
**`S25`** (“TorchAudio mask-based MVDR example”), both with
`access_scope="search excerpt"`. The merged `survey-cln-07` map records the
same boundary and gap **`G03`**: “Execute MVDR/MPDR against delay-and-sum and
keep oracle-mask/oracle-steering and estimated-mask groups separate” — with the
explicit evidence gap “no covariance estimator, mask model, oracle separation
or local score exists.”

Consequently:

- no exact MVDR/MPDR source tree, package, archive, executable, runtime,
  adapter or immutable revision is staged at `data/checkouts`, `data/envs`,
  `data/models` or `adapters`;
- no licence identity, artifact hash, build identity or adapter setting exists
  for `S24` or `S25`;
- no mask estimator checkpoint, oracle-mask definition, covariance
  configuration, steering-vector source or mask-quality result exists;
- no rights-cleared synchronized real multichannel recording, geometry
  manifest, calibration file, consent/usage grant or target/reference
  condition is staged;
- no measured device synchronization, clock offset/drift, channel loss or
  target-device deadline exists;
- no task-matched held-out localization/activity/extraction labels, distortion,
  leakage, target-damage or channel-loss scorer, independent review, provider
  intake or release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-MVDR-BEAMFORMING`, `f8416852b07c700d232f75b28daba3de84748696` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Fixture geometry | 4 microphones, planar, 16 kHz, integer nanometres |
| Mask validation | structural only; never applied |
| MVDR output | absent; comparison `blocked` |
| Added content delay | 0 samples |
| Provider registration, default, ABI, CI | none |

The included baseline exercises strict parsing, exact plane-wave steering
arithmetic, a frozen synthetic fixture, structural mask/plan validation and
adverse rejection. It is **not** the catalogued candidate and cannot establish
exact-runtime parity. It addresses only the *validation half* of survey gap
`G03`; it closes no source, mask, covariance, rights, corpus, device, scoring or
release gate.

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
- Steering delays are exact rational `q16` sample values
  `relative_q16_i = (tdoa_i - tdoa_ref) * 65536 / 62,500`. A non-integral
  residual is **rejected** (`fractional_steering_not_exact`); this package has
  no fractional steering surrogate.
- The frozen control is the arithmetic mean of the aligned channels:
  `y[n] = (1/N) * Σ x_i[n + relative_q16_i/Q16]`. Weights are equal `1/N`.
  There is no adaptive coefficient, mask, covariance estimate or learned
  parameter.
- Synthetic channel samples and the control output are exact integers and
  reduced fractions. No tolerance is applied.
- Nonzero `clock_ppm`, non-unity `calibration_gain_q16`, unknown or duplicate
  channels, non-normalizable directions and nonfinite samples are rejected.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry and layout | declared synthetic only | One frozen 4-microphone planar geometry in integer nanometres; no measured array, orientation or device layout |
| Timestamp calibration | declared synthetic only | Exact 62,500 ns sample period, synchronous unity-gain channels, declared reference `m0`; no measured device clock |
| Source/target/reference conditions and permissions | blocked | No real recording, condition, consent or usage grant |
| Task-matched held-out localization/activity/extraction | blocked | No labels, MVDR output or scorer |
| Leakage, target damage, channel loss | blocked | No real target or interference stratum; the delay-and-sum control is not an MVDR comparison |
| Room/reference changes | blocked | No measured room or reference change; adjacent WPE evidence is not pooled |

MVDR-specific items required by the task deliverable:

| Item | State | Evidence |
| --- | --- | --- |
| Mask validity | blocked | 2×3 oracle mask validated for shape, group, range, finiteness and timing only; never applied; no mask model or quality result |
| Reference timing | declared synthetic only | Exact rational delays relative to `m0`; no measured device reference timing |
| Channel calibration | declared synthetic only | Unity gain and zero drift required; no measured calibration |
| Distortion against delay-and-sum | blocked | Control exists; no MVDR output exists, so no comparison can be computed |

## Frozen synthetic fixture

The single frozen fixture is generated from integer arithmetic and stays under
`docs/task-evidence/mvdr-beamforming/`. The reference channel is `m0`; a target
click arrives at the declared reference index and every channel must align to
that index before equal-weight summation.

| Property | Value |
| --- | --- |
| Array | 4 planar microphones, 107.1875 mm × 26.796875 mm grid |
| Steering | `(3,4,0)`, exact norm 5 |
| Declared relative samples | `0, -3, -1, -4` (`q16` `0, -196608, -65536, -262144`) |
| Frame | 160 samples |
| Click index / amplitude | 16 / 1000 integer units |
| Interference rule | `((index*37+11)%101)-50` |
| Control peak | index 16, exact `2049/2` |
| Control maximum | exact `2049/2` |
| Fixture digest | `67be2fef509341b8d064aea59a9a580bceb261a0ed6e66b1056a6f4415786670` |
| Geometry digest | `df739d554a224a21f27e3152415e91c69fa3e3790932e577f38e00e5240b352e` |
| Control output digest | `dba63b195e4b28bc81934b382838d03389ba332ca887389ce4f75aa4cf4abdb9` |

The delay-and-sum control is `is_mvdr=false`,
`status=control_only_not_qualified`, `qualification_status=not_qualified`,
`mask_applied=false`, `covariance_used=false`. It is a distortion reference
only. Because no MVDR output exists, `distortion_comparison.status` is
`blocked` and `metric`/`value` are `null`.

## Structural mask and plan validation

`reference.py` parses a declared mask manifest strictly: exact field set,
`mask_group` must be exactly one of `oracle` or `estimated` (mixing is
rejected), 16 kHz and 160-sample hop must match, frame/bin counts must match the
declared rectangle, every value must be finite and inside `[0,1]`, and the
timing mode must be `causal` or `offline_declared`. This is **shape validation
only**: no mask is applied to a beamformer and no mask-quality claim is made.

It also parses a declared MVDR plan structurally: exact field set, immutable
hex source revision, source SHA-256, non-empty licence grant, runtime/adapter
IDs, geometry digest, single mask group, covariance estimator with diagonal
loading, smoothing frames and rank, and a delay-and-sum baseline ID. Structural
acceptance is **not** qualification: in this package the plan is absent, so
`mvdr_plan.status=blocked`, `present=false`, `executed=false`.

## Adverse, missing and invalid handling

`report.json` records 40 rejected inputs, each with an unchanged synthetic
fixture state. Rejections include duplicate microphone position or ID, unknown
reference, non-integer or out-of-range position, non-normalizable or zero
steering direction, unsupported rate or speed, wrong microphone counts, extra
geometry field, missing/duplicate/unknown channel, nonzero clock drift,
non-unity or non-integer calibration, fractional steering, nonfinite or
wrong-type samples, length/channel mismatch, empty channel, oversized sample,
out-of-range click, negative/above-one/nonfinite mask values, mask frame/bin
shape mismatch, mixed mask groups, extra mask field, missing/invalid plan
source revision or digest, invalid plan mask group, invalid covariance rank,
extra plan field, duplicate JSON key, NaN/Infinity JSON constant and malformed
JSON. Missing MVDR output, missing mask model, missing real recordings and
delayed/missing real references are `blocked`, not passes.

## Reproduction

```sh
cd docs/task-evidence/mvdr-beamforming
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` performs three cold-start rounds and refuses to accept non-identical
report, contract or source bytes. `verify.py` is read-only and fails closed on
stale pins, non-canonical JSON, a promoted MVDR or mask or control result, a
qualified claim, an unblocked release gate, a license gap, out-of-scope changes
or `git diff --check` damage. Expected: all tests pass and `verify.py` prints
`pins_ok=40 json_ok=2 report_sha256=… repeats_ok=3 licensing_ok=1 scope_ok=1`.

Canonical `report.json` SHA-256:
`e0380461ab6897c63ad4bbd95861796c903942f6bbfc6976df78b46056304e3d`.

## Release gates and reopening

All eight gates are `blocked`: exact licensed source/runtime (`RG-01`), exact
mask/covariance configuration (`RG-02`), measured geometry/calibration and
reference channel (`RG-03`), rights-cleared synchronized real corpus (`RG-04`),
exact-runtime parity on the frozen fixture (`RG-05`), measured device
synchronization/drift/channel loss (`RG-06`), task-matched held-out spatial
scoring including distortion against the delay-and-sum control (`RG-07`), and
opt-in provider intake plus independent review and release approval (`RG-08`).

Reopen only with a rights-cleared real multichannel corpus, one pinned licensed
MVDR/MPDR source or runtime with exact mask/oracle definition and covariance
settings, exact-runtime parity on the frozen fixture, distortion compared
against the delay-and-sum control, measured device synchronization and drift,
held-out spatial scoring including leakage, target damage and channel loss, and
independent opt-in provider review. Until then the decision stays `DEFER`, the
evidence stays `incomplete`, and no result may qualify.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This boundary record |
| `reference.py` | Stdlib-only fixture, exact delay-and-sum control, strict mask/plan validators and report builder |
| `test_reference.py` | Deterministic arithmetic, rejection and disposition tests |
| `run.py` | Three-round byte-identical regeneration of report, contract and pins |
| `verify.py` | Read-only strict verifier |
| `report.json` / `.sha256` | Canonical report and its SHA-256 |
| `contract.json` | Machine-readable disposition, blockers, gates and pins |
| `SOURCES.sha256` | Exact source, boundary and artifact pins |
| `*.license` | SPDX sidecars for generated non-Python files |

No provider, descriptor, registry, installed v0 behavior, ABI, default, shared
build, CI workflow, board row or handoff is changed.
