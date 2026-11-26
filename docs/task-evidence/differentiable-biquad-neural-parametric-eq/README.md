<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ — source, weights, runtime and device-split blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Differentiable-biquad neural parametric EQ`
(`component_id=differentiable-biquad-neural-parametric-eq`, task
`SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ`). The acceptance profile is
**DSP**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact differentiable-biquad neural parametric-EQ implementation, checkpoint,
weights, runtime, immutable revision, parameterization, gain limits, device
response, held-out device/speaker split, frozen oracle and rights record are
**absent**. This package records that exact blocker, applies the DSP profile to
a bounded deterministic synthetic RBJ peaking-biquad control, and makes no
neural-EQ accuracy, device-recovery, latency, listening, benchmark or release
claim. It is **not the candidate model**: no neural network, learned parameter
generator, weight tensor, neural runtime, real device response, real audio,
corpus or device clock is present, copied, downloaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, id
`differentiable-biquad-neural-parametric-eq`) is `considered`,
`disposition=sdk-model`, `verification_profile=dsp`, with the plan note
"Recover known device response before real speech. Apply held-out
device/speaker split and gain limits."

Its only evidence link is `research/level_tone_control_20261028.md`, which says:

> Neural parametric EQ matching with differentiable biquads shows learned
> prediction of EQ parameters as a relevant tone-control family. [DAFx 2020
> paper] A later neural multiband processor proposes self-supervised automatic
> EQ plus dynamics processing. [DAFx 2025 paper]

The note records these as literature references only. It states that the
repository baselines are a small ridge regression over synthetic perturbations,
not a differentiable-biquad neural implementation, and that:

> The learned EQ result shows it can recover part of the controlled synthetic
> coloration, but content, room, and speaker variation were not represented.
> These results do not support model selection for real speech.

The note's 2.577 dB learned-inverse-EQ and 4.414 dB identity figures are
synthetic, are not reproduced here, and are not candidate metrics. The pinned
note also requires, before ranking candidates: a frozen paired set with clean
speech, independent level trajectories, noise-floor cases, clipped/overloaded
cases, **known device EQ coloration**, hum/rumble examples and untouched
controls; **split by speaker/session**; integrated and short-term loudness,
true-peak/clipping, gain range/slew, noise amplification, spectral-response
error, speech quality/intelligibility, runtime/latency and blinded listening;
and confirmed code/checkpoint hashes, licensing, hardware and input/output
scope.

Consequently:

- no candidate source, checkpoint, weight file, tensor archive or digest is
  staged at `data/checkouts/differentiable-biquad-neural-parametric-eq`,
  `data/models/differentiable-biquad-neural-parametric-eq` or any fixed path;
- no neural runtime environment or lock exists at
  `data/envs/differentiable-biquad-neural-parametric-eq`; no neural runtime is
  imported;
- no real device response, rights-cleared corpus or held-out device/speaker
  split exists at `data/datasets/device-response-eq`;
- no frozen parameter/output oracle, adapter or rights record exists;
- no device timing, availability, resource or drain measurement exists.

The artifact audit in `report.json` re-observes every fixed path and must show
`any_present=false`; if an artifact appears, the blocker must be re-evaluated,
not auto-qualified.

## Exact scope and boundary

- Worktree: `audio-sdk` task branch
  `swarm/SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ`, pinned base commit
  `708b9a4197ed35fd2528fad425832c55ef393eb7`.
- Write scope: only
  `docs/task-evidence/differentiable-biquad-neural-parametric-eq/`. No shared
  `CMakeLists.txt`, `CONTRACTS.md`, API/ABI header, descriptor registry,
  installed provider, catalog or build file was touched.
- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame. The installed v0
  behavior is unchanged.
- Processor exposure is **deferred**: `contract.json` and `report.json` record
  `registered=false`, `enabled_by_default=false`, `processor_exposure=false`,
  `provider_registration=false` and no public API/ABI change. No C boundary or
  opt-in consumer is included.
- No external learned model, weights, checkpoint, download, licensed runtime,
  WAV, corpus, real speech, real device response, listening test, device timing
  or release approval.

## Source pins and provenance

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.
The mutable full `plan/swarm/TASKS.json` is **never hashed**; only the stable
linked-row identity is gated (see `report.json:task_row_identity`).

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` | Source study: neural parametric-EQ literature, synthetic-only baselines, device/speaker/rights requirements. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component record and DSP profile assignment. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP profile: sweeps, steps, impulses, silence, clean speech and a control; gain, response, attack/release, headroom, delay and numerical behavior. |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` | Read-only board validator used for this task. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Normative v0 contract, read and pinned; unchanged. |
| `audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | SDK plan and delivery sequence, read and pinned; unchanged. |

Boundary files pinned but not modified:

| File | SHA-256 |
| --- | --- |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |

## DSP-profile application

The `dsp` profile is applied in `report.json:dsp_profile` and exercised in
`reference_protocol.synthetic_control`. Every item is marked
`satisfied_for_qualification=false` and `qualification_effect=none`.

| Profile element | Fixture / measurement |
| --- | --- |
| Sweeps | 50 Hz–7.8 kHz logarithmic sweep, measured vs predicted RMS gain and finite output. |
| Steps | 0.5 level step, DC settling and gain error. |
| Impulses | Unit impulse, first significant sample, delay and analytic-vs-DFT magnitude error on nine probes. |
| Silence | All-zero stimulus; output must be exactly zero and finite. |
| Synthetic clean speech | Deterministic harmonic/formant-like signal with a syllable envelope and seeded noise. |
| Level/load control | Gain-limited fitting of a four-band synthetic device response with a three-band model. |
| Gain | Band-center gain, cascade gain and explicit ±6 dB control limit. |
| Response | Analytic RBJ response, time-domain sweep, impulse DFT and probe comparison. |
| Attack/release | **Blocked** — no candidate adaptation contract exists. |
| Headroom | Near-clip 1.4-peak input, output peak, dB headroom and clipped-sample count. |
| Delay | Zero buffering delay for the synthetic control; candidate delay **blocked**. |
| Numerical behavior | Pole radius, finite checks, 12 invalid-input rejections. |
| State transitions | Frame-vs-whole equality, repeated-impulse reset isolation. |
| Interacting nonlinearity | `peaking_eq -> tanh(1.5x) -> device_eq`, finite and bounded by one. |

The synthetic control uses causal RBJ peaking biquads in direct form I with
normalized `(b0,b1,b2,a1,a2)` coefficients, 16 kHz mono, 160-sample frames and
zero buffering delay. Band gains are differentiated by an analytic
complex-step derivative; a central finite difference independently checks the
gradient. Identity and a frozen synthetic device response are measured before
any synthetic speech-like stimulus. This is a controlled mechanism check only;
it is not a learned model, not a device-recovery product and not real speech.

### Synthetic results (non-qualifying)

- Gradient check at gains `[0.7, −1.2, 0.4] dB`: complex-step vs finite
  difference maximum absolute difference `1.284e−06`, below `1e−4`.
- Exact three-band recovery from a target generated by the same structure:
  initial RMSE `2.088817 dB`, final RMSE `0.0 dB`, maximum gain error
  `0.0 dB` after 320 iterations, no clamping.
- Four-band synthetic device response fitted by a three-band model:
  gains `[+2.429903, −2.744065, +1.144035] dB`, train RMSE `1.248979 dB`,
  held-out frequency RMSE `0.762518 dB`, no clamp events at the ±6 dB limit.
  The held-out probes are a **synthetic frequency holdout**, not a device or
  speaker split.
- Sweep measured vs predicted RMS gain: `0.340983` vs `0.341090 dB`
  (difference `0.000107 dB`); impulse first significant sample `0`, delay `0`,
  maximum analytic-vs-DFT error `0.0 dB`; silence exactly zero; frame-vs-whole
  maximum difference `0.0`; reset difference `0.0`.
- Near-clip input peak `1.4` yields output peak `1.437350`, headroom
  `−3.151249 dB` and `227` clipped samples: adverse, not an accepted operating
  point.
- Nonlinear chain peak `0.321694`, finite and bounded by one.
- Maximum pole radius across −24…+24 dB is `0.993176`, below one.

### Explicit adverse and failure controls

- Three identical +6 dB bands at 1 kHz produce `+18.0 dB` at the center while
  remaining stable; non-qualifying.
- A single +24 dB band remains stable with pole radius `0.947950`; non-qualifying.
- The fitted model's 7.9 kHz response is `+0.000495 dB`; the package records
  the out-of-band value and does not claim a guard.
- A target requiring +8 dB fitted with a 2 dB limit produces final RMSE
  `7.073866 dB` and `898` clamp events; the gain limit is enforced and the
  result is non-qualifying.
- Twelve invalid or missing DSP inputs (nonfinite sample, infinite sample,
  string sample, empty samples, zero Q, negative Q, zero frequency, Nyquist
  frequency, NaN gain, infinite gain, gain above limit, bad state) are all
  rejected with no state advance.
- A caller-manifest schema validates exact files, hashes, geometry, band/Q/gain
  bounds, device response, disjoint device and speaker splits, oracle and
  rights records. Its positive synthetic control is accepted but
  `qualifies=false`; 60 adverse mutations and six malformed strict-JSON
  documents are all rejected. Schema acceptance never qualifies the candidate.

## Release gates

All eight gates are **blocked**:

| Gate | Blocked requirement |
| --- | --- |
| `RG-01` | Exact source revision, checkpoint digest, byte count, weight format, parameter count and biquad tensor schema are pinned. |
| `RG-02` | An isolated hash-pinned runtime reproduces an approved exact-runtime gain/response vector, deterministic gradients, reset and nonfinite rejection. |
| `RG-03` | Code, weight, training-data, runtime-dependency, device-response, corpus, redistribution, derivative-output and product-use rights are cleared. |
| `RG-04` | Parameterization, band count, frequency/Q/gain bounds, hop, update cadence, device-response definition and gain limits are documented. |
| `RG-05` | A rights-cleared held-out device and speaker split recovers a known device response before real speech and is scored for response, gain limits, preservation and peaks. |
| `RG-06` | Streaming state, independent sessions, reset, sample intervals, coefficient updates, frame/whole equivalence and nonfinite output are verified at the exact runtime. |
| `RG-07` | Target-device pacing, inference-plus-filter availability, deadline misses, memory and finite drain are measured. |
| `RG-08` | Explicit opt-in provider intake, descriptor/license review, resource bounds and independent exact-head release approval are complete; the package remains off by default. |

Exact blockers (`report.json:exact_blockers`):

1. `no_reviewed_implementation_or_revision` — no runnable implementation or
   full 40-hex revision.
2. `no_checkpoint_or_weights` — no checkpoint, digest, byte count, format,
   parameter count or tensor schema.
3. `no_runtime_lock` — no isolated hash-pinned neural runtime.
4. `no_rights_record` — no license, model card, per-weight terms or
   product-use decision.
5. `no_geometry_parameterization_or_gain_contract` — no candidate geometry,
   coefficient contract, gain limit or update cadence.
6. `no_frozen_oracle_or_parity` — no parameter/output oracle or exact-runtime
   parity record.
7. `no_rights_cleared_device_speaker_split` — no real device response or
   rights-cleared held-out device/speaker cohort.
8. `no_target_timing_or_provider_intake` — no device timing or provider intake.

Until all gates pass, no default, production, quality or release claim exists;
the installed SDK v0 remains frozen and unchanged.

## Reproduction

Run from this directory unless otherwise noted. Generation order matters:
sources last.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256`, verifies three cold-start rounds are byte-identical, and
writes only after they match. `verify.py` re-pins every source, boundary and
package file, re-checks the strict report/contract schema, recomputes the
linked-row identity from stable fields only, re-observes the absent artifacts,
runs `run.py --check`, rebuilds the report three times in separate cold Python
processes and compares digests, checks SPDX coverage, README tokens and the
task-local scope, and fails on `git diff --check`.

Board and whitespace checks (from the worktree root):

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DIFFERENTIABLE-BIQUAD-NEURAL-PARAMETRIC-EQ
git diff --check
git diff --cached --check
```

The package is stdlib-only Python 3.11+. It does not read audio, download,
import a neural runtime, load weights or execute a model.
