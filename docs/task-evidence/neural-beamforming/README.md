<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-NEURAL-BEAMFORMING — model/weights/runtime, geometry and corpus blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Neural beamforming` (`component_id=neural-beamforming`). The acceptance
profile is **Spatial**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked, surrogate or rejected
result may never qualify the component.

The catalogued record is an unspecified **method family**, not one model:
"Algorithm family lacks a concrete local model, array geometry and multichannel
target benchmark." The named family leads — SpatialNet and Beam-TasNet /
Beam-Guided TasNet — are research references only, and the CLN-07 category
sources `S24`/`S25` are search excerpts. No licensed neural-beamformer source
tree, package, archive, executable, runtime, adapter, immutable revision,
checkpoint, weight bytes, licence grant, training-data right, measured array
geometry, reference channel, calibration or rights-cleared synchronized array
corpus is staged.

This package records that exact blocker and runs a bounded deterministic
**validator + fixed-list absence probe + frozen synthetic fixture with exact
identity and delay-and-sum control baselines**. It implements **no neural
beamformer**: no network is defined, no weight is loaded, no mask is estimated,
no spatial loss is applied and no neural output exists. It is not SpatialNet,
Beam-TasNet or Beam-Guided TasNet, does not import, load, vendor or download
any of them, and makes no beamforming-quality, extraction, leakage,
localization, listening, device-timing, benchmark or release claim. Only this
task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=neural-beamforming`) is
`blocked`, `disposition=sdk-model`, `verification_profile=spatial`, with the
finding “Algorithm family lacks a concrete local model, array geometry and
multichannel target benchmark.” The only evidence link is
`research/voice-enhancement-20261101/candidate_matrix.csv`, record 60
(`unavailable/blocked`), with baseline “Multichannel WPE; identity” and report
paths to the spatial-trials and spatial audit reports. Category `CLN-07`
(S24 Pyroomacoustics, S25 TorchAudio mask-based MVDR) is the surrounding
beamforming category, not a concrete neural candidate.

Consequently:

- no exact neural-beamformer source tree, package, archive, executable,
  runtime, adapter or immutable revision is staged at `data/checkouts`,
  `data/envs`, `data/models` or `adapters`;
- no model identity, weight digest, checkpoint size, parameter count, licence
  identity, build identity or adapter setting exists;
- no training recipe, spatial loss, target definition, oracle/estimated mask
  definition, training-data right or model-quality result exists;
- no rights-cleared synchronized real multichannel recording, geometry
  manifest, calibration file, consent/usage grant or target/reference
  condition is staged;
- no measured device synchronization, clock offset/drift, channel loss or
  target-device deadline exists;
- no task-matched held-out localization/activity/extraction labels,
  distortion, leakage, target-damage or channel-loss scorer, independent
  review, provider intake or release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The fixed-list absence probe checks 25 model/weight/runtime paths across the
workspace, this SDK worktree and fixed home-cache locations; all are absent.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-NEURAL-BEAMFORMING`, `9074704819a6af4168f8c9cf3bbe8da50484c29a` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Fixture geometry | 4 microphones, planar, 16 kHz, integer nanometres |
| Mask validation | structural only; never applied |
| Neural output | absent; comparison `blocked` |
| Added content delay | 0 samples |
| Provider registration, default, ABI, CI | none |

The included baseline exercises strict parsing, exact plane-wave steering
arithmetic, a frozen synthetic fixture, structural mask/plan validation,
adverse rejection and a fixed-list absence probe. It is **not** the catalogued
candidate and cannot establish exact-runtime parity. It closes no source,
weights, model, target, rights, corpus, device, scoring or release gate.

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
- Synthetic channel samples and both control outputs are exact integers and
  reduced fractions. No tolerance is applied.
- Nonzero `clock_ppm`, non-unity `calibration_gain_q16`, unknown or duplicate
  channels, non-normalizable directions, nonfinite samples and non-integer
  sample types are rejected.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry and layout | declared synthetic only | One frozen 4-microphone planar geometry in integer nanometres; no measured array, orientation or device layout |
| Timestamp calibration | declared synthetic only | Exact 62,500 ns sample period, synchronous unity-gain channels, declared reference `m0`; no measured device clock |
| Source/target/reference conditions and permissions | blocked | No real recording, condition, consent or usage grant |
| Task-matched held-out localization/activity/extraction | blocked | No labels, neural output or scorer |
| Leakage, target damage, channel loss | blocked | No real target or interference stratum; the controls are not neural comparisons |
| Room/reference changes | blocked | No measured room or reference change; adjacent WPE evidence is not pooled |

Neural-specific items:

| Item | State | Evidence |
| --- | --- | --- |
| Model identity and weights | blocked | No concrete model, source revision, weight digest, checkpoint size, licence grant or runtime |
| Target definition | blocked | No direction, enrollment embedding or oracle target is declared for a concrete model |
| Mask validity | blocked | 2×3 oracle mask validated for shape, group, range, finiteness and timing only; never applied; no mask model or quality result |
| Spatial loss and training rights | blocked | No spatial loss, training recipe, training-data right or adaptation protocol |
| Exact runtime parity | blocked | No candidate module was imported or executed and no output digest exists |
| Extraction, leakage, target damage | blocked | No real target, off-target or channel-loss stratum exists |

## Frozen synthetic fixture

The single frozen fixture is generated from integer arithmetic and stays under
`docs/task-evidence/neural-beamforming/`. The reference channel is `m0`; a
target click arrives at the declared reference index and every channel must
align to that index before any spatial combination.

| Property | Value |
| --- | --- |
| Array | 4 planar microphones, 107.1875 mm × 26.796875 mm grid |
| Steering | `(3,4,0)`, exact norm 5 |
| Declared relative samples | `0, -3, -1, -4` (`q16` `0, -196608, -65536, -262144`) |
| Frame | 160 samples |
| Click index / amplitude | 16 / 1500 integer units |
| Interference rule | `((index*37+11)%101)-50` |
| Identity control peak | index 16, exact `1548/1` |
| Delay-and-sum control peak | index 16, exact `3049/2` |
| Fixture digest | `2761b412914a6b631738eaedaf5b4963802a254b11a690b2cc547bc5b04e5996` |
| Core repeat digest | `4e943c662ccec8b4233399ae9ec720fbba32ecaa8a9185884289b03215e3e274` |

The identity control passes through the declared reference channel; the
delay-and-sum control is the exact equal-weight mean of the aligned channels.
Both are `is_neural_beamformer=false`,
`status=control_only_not_qualified`, `qualification_status=not_qualified`,
`model_weights=false`, `mask_applied=false`, `spatial_loss_used=false`. They
are distortion references only. Because no neural output exists,
`distortion_comparison.status` is `blocked` and `metric`/`value` are `null`.

## Structural mask and plan validation

`reference.py` parses a declared mask manifest strictly: exact field set,
`mask_group` must be exactly one of `oracle` or `estimated` (mixing is
rejected), 16 kHz and 160-sample hop must match, frame/bin counts must match
the declared rectangle, every value must be finite and inside `[0,1]`, and the
timing mode must be `causal` or `offline_declared`. This is **shape validation
only**: no mask is applied and no mask-quality claim is made.

It also parses a declared neural-beamforming plan structurally: exact field
set, model/source/runtime/adapter IDs, immutable hex source revision, source
SHA-256, weight SHA-256, non-empty weight licence, geometry digest, reference
mic, target definition, beamformer kind, channel count, rate/hop, spatial loss,
mask group, checkpoint bytes and parameter count, with mask-group/kind
consistency. Structural acceptance is **not** qualification: in this package
the plan is absent, so `neural_plan.status=blocked`, `present=false`,
`executed=false`.

## Absence probe

`report.json` → `absence_evidence` records a fixed, read-only list of 25 paths
for checkouts, models, environments, references, audio, runs, research and
adapters under the workspace and SDK worktree, plus fixed home-cache/model
locations. It reports `present_count=0`, `all_absent=true`,
`network_used=false`, `download_attempted=false`, `audio_read=false`,
`candidate_module_imported=false` and `candidate_runtime_executed=false`. A
present artifact would fail generation rather than be promoted silently.

## Adverse, missing and invalid handling

`report.json` records 46 rejected inputs, each with an unchanged synthetic
fixture state. Rejections include duplicate microphone position or ID, unknown
reference, non-integer or out-of-range position, non-normalizable or zero
steering direction, unsupported rate or speed, wrong microphone counts, extra
geometry field, missing/duplicate/unknown channel, nonzero clock drift,
non-unity or non-integer calibration, fractional steering, nonfinite or
wrong-type samples, length/channel mismatch, empty channel, oversized sample,
out-of-range click, out-of-range/nonfinite mask values, mask frame/bin shape
mismatch, mixed mask groups, extra mask field, missing/invalid plan source or
weight digest, empty weight licence, invalid target definition, invalid
beamformer kind, inconsistent mask group, invalid spatial loss, bad checkpoint
size, mixed plan mask group, extra plan field, duplicate JSON key, NaN/Infinity
JSON constant and malformed JSON. Missing neural output, missing weights,
missing real recordings and delayed/missing real references are `blocked`, not
passes.

## Reproduction

```sh
cd docs/task-evidence/neural-beamforming
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` performs three cold-start rounds and refuses to accept non-identical
report, contract or source bytes. `verify.py` is read-only and fails closed on
stale pins, non-canonical JSON, a promoted neural result or control, a
qualified claim, an unblocked release gate, a license gap, out-of-scope changes
or `git diff --check` damage. Expected: all tests pass and `verify.py` prints
`pins_ok=46 json_ok=2 report_sha256=… repeats_ok=3 licensing_ok=1 scope_ok=1`.

Canonical `report.json` SHA-256:
`15c3426398ae8b7a90aceac3c154b11d2c365a3e346b07b9e043cfd63c49356f`.

## Release gates and reopening

All eight gates are `blocked`: exact licensed source/weights/runtime (`RG-01`),
exact model/target/spatial-loss configuration (`RG-02`), measured
geometry/calibration and reference channel (`RG-03`), rights-cleared
synchronized real corpus (`RG-04`), exact-runtime parity on the frozen fixture
(`RG-05`), measured device synchronization/drift/channel loss (`RG-06`),
task-matched held-out spatial scoring with leakage, target damage and channel
loss against identity and delay-and-sum controls (`RG-07`), and opt-in provider
intake plus independent review and release approval (`RG-08`).

Reopen only with a rights-cleared real multichannel corpus, one pinned licensed
neural-beamformer source **and weight artifact** with exact target definition,
spatial loss, runtime and adapter settings, exact-runtime parity on the frozen
fixture, measured device synchronization and drift, held-out spatial scoring
including leakage, target damage and channel loss, and independent opt-in
provider review. Until then the decision stays `DEFER`, the evidence stays
`incomplete`, and no result may qualify.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This boundary record |
| `reference.py` | Stdlib-only fixture, fixed absence probe, exact identity and delay-and-sum controls, strict mask/plan validators and report builder |
| `test_reference.py` | Deterministic arithmetic, absence, rejection and disposition tests |
| `run.py` | Three-round byte-identical regeneration of report, contract and pins |
| `verify.py` | Read-only strict verifier |
| `report.json` / `.sha256` | Canonical report and its SHA-256 |
| `contract.json` | Machine-readable disposition, blockers, gates and pins |
| `SOURCES.sha256` | Exact source, boundary and artifact pins |
| `*.license` | SPDX sidecars for generated non-Python files |

No provider, descriptor, registry, installed v0 behavior, ABI, default, shared
build, CI workflow, board row or handoff is changed.
