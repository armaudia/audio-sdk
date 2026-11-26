<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CAPSC-BUFFER-OCCUPANCY-PACING — CAPSC / buffer-occupancy pacing blocker

`audio-sdk/capsc-buffer-occupancy-pacing/0.1`

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
| Pinned base | `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |

This directory is a bounded, task-local blocker package for **CAPSC / buffer-
occupancy pacing**. It is **not** an implementation, adapter, provider,
playout device, benchmark or release. It records why the candidate cannot be
qualified from the artifacts that are actually present, and it reproduces only
declared integer queue-debt arithmetic and deterministic synthetic controls.
Nothing here may be promoted to a runtime, device or quality claim.

## Why DEFER

The pinned candidate note names **CAPSC (ACM MMSys 2021)** as the
control-theory reference for the *debt side*: content-aware playback-rate
control for low-latency live streaming, with the same slow-down/speed-up
trade-off against a latency target. It also names CAPSC as prior art for the
latency-threshold element of a pending patent. That is all it supplies.

- The note gives only DOI `10.1145/3458305.3478437` and states that the
  publisher returns **403 to automated fetches**.
- It records **no CAPSC source, executable, equations, parameters, content
  classes, queue-debt definition, latency target, rate bounds, slew, underrun
  policy, recovery policy, dataset or measured result**.
- No CAPSC paper PDF, source tree, binary, runtime package, licence grant or
  terms text exists anywhere in the project workspace.
- The note's own section 8.6 debt-controller formulation is explicitly labelled
  as research that reads on `US20260075269A1` and says **do not ship it without
  counsel review**. It is not CAPSC and it is not used here.
- No public paced-playout adapter exists in SDK v0. The installed boundary is a
  fixed 16 kHz mono f32 160-sample synchronous/buffered processor, not a
  playback controller or device clock.
- No qualified speech/content estimator, rights-cleared playback cohort,
  matched Rate result, listening study or target-device timing exists.

Nothing was downloaded, copied, reconstructed or fabricated. Supplying the
missing artifacts and rights reopens the task; absence of a result is the
correct outcome.

## Exact blockers

| ID | Missing artifact | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Permitted CAPSC paper and any official implementation artifact | Exact DOI/version, immutable acquisition record, full SHA-256 of every supplied file, and a written grant covering execution, benchmarking, redistribution, derivative output, commercial use and patent risk. |
| `BLK-02` | CAPSC controller geometry and a paced-playout host | CAPSC queue-debt definition, content classes, latency target, rate bounds, slew, underrun/recovery policy, final-partial semantics, plus a pinned public adapter with instrumented source FIFO and device clock. |
| `BLK-03` | Qualified speech/content estimator | Pinned provider/runtime/assets, measured coverage and accuracy, confidence/unknown semantics, source timestamps, and proof that estimation is separate from the playout controller. |
| `BLK-04` | Rights-cleared playback cohort | Immutable unfamiliar-speech, music, silence and transient recordings with consent, terms, exact digests, source timestamps and an output-use decision. |
| `BLK-05` | Matched results, controls, listening and device timing | Measured Rate-profile results and adverse/missing/nonfinite controls on the admitted runtime and cohort, including queue debt, underruns, recovery, preservation, listening, deadlines and resources. |
| `BLK-06` | OFF-by-default intake and release review | Separate versioned intake with exact descriptor/config, no registry/ABI/default/shared-build/CI change, clean-install proof and independent exact-head review after the prior gates clear. |

The eight blocked release gates are enumerated in `report.json` under `gates`.
Every gate is `blocked` and `qualifies=false`.

## What is pinned

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless marked
as SDK-worktree relative.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | CAPSC main note (line 922), prior-art row (line 981), DOI/403 reference (line 1046), section 8.6 (line 606), patent note (line 656), D2 design (line 951) and do-not-ship line (line 1005). |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row `capsc-buffer-occupancy-pacing`; Rate profile; sdk-reference disposition; plan note to keep playout control separate from speech estimation and record queue debt, underruns and recovery. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK implementation plan and optional-reference boundary. |

The unchanged public boundary is pinned separately: `CONTRACTS.md`,
`api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h`,
`CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml` and `README.md`.

Merged sibling evidence is pinned under `docs/task-evidence/`: the
buffer-occupancy controller, pipe playout, D1 whole-clip planner, duplex clock
contract, elastic PCM/packet contract, adaptive-energy VAD, Silero VAD v5, USC
mrate, browser `playbackRate`, Apple time-pitch blocker and Signalsmith
Stretch. Exact values are in `SOURCES.sha256` and `report.json`. None of them
is CAPSC, and none supplies a qualified CAPSC result.

The mutable full `plan/swarm/TASKS.json` is **never hashed**. Only the stable
linked-row projection (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`, `evidence`) is read; board status, owner, claim and review fields
gate nothing.

## Parameter provenance

The candidate note records no numeric CAPSC parameter. Therefore:

- `documented_parameter_envelope` leaves latency target, queue-debt definition,
  underrun/recovery policy, rate bounds, slew and defaults `null`, and marks
  `semantics_verified_here=false`.
- `synthetic_control_envelope` is a **synthetic validation envelope** only:
  16 kHz, 160-sample blocks, 3200-sample target (200 ms nominal), 9600-sample
  capacity (600 ms nominal), rate `19/20..21/20`, slew 50 ppm per block,
  proportional gain `1/4`. It is not a CAPSC range, default or policy and cannot
  qualify a result.

## Synthetic arithmetic controls

`controller_control` evaluates an occupancy-only control law:

```text
debt = queued - target
raw_ppm = 1_000_000 + debt * 1_000_000 * gain / target
command = clamp(raw_ppm, 950_000, 1_050_000), then slew from last by <= 50 ppm
```

The controller accepts only `queued_samples`, `target_samples` and
`last_rate_ppm`. It never reads a speech/content label. Ten cases cover 1x,
excess, deficit, both clamps, both slew directions, capacity and one-block
excess; all are labelled `synthetic_contract_control_not_evidence` and have
`qualifies=false`.

`playout_control` adds exact integer/Fraction accounting for queue debt,
arrivals, consumption, rebuffer, underrun and recovery. Cases cover steady,
excess, deficit, hold/release, slow drift, whole-arrival overflow, empty start,
underrun with recovery, rebuffer without recovery and at-target. It emits no
PCM, reads no audio and measures no device.

`separation_control` feeds the same queue trace with five different content
labels and shows one identical command sequence, proving that labels do not
enter the controller. The estimator is not executed. This is the plan's
"keep a playout controller separate from speech estimation" boundary as a
synthetic control only.

`final_partial_control` reproduces the declared 160-sample block remainder
(16000 exact, 16001 partial, 16165 -> 5 samples, 16159 -> 159 samples).

## Admission and fail-closed behaviour

`admission` validates a caller-authored qualification manifest that requires
an exact CAPSC DOI and artifact digests, licence and patent approvals, exact
controller geometry, a separate qualified estimator, a rights-cleared cohort
with source timestamps, a Rate result and an OFF-by-default scope with no
registration, ABI or shared-build change. All 57 mutations (missing/unknown
field, wrong schema, malformed DOI/digest, false rights, unsupported policy,
out-of-range geometry, joined estimator, missing timestamps, registration or
ABI change, wrong flag types) are rejected with their expected code and no
state advance. The synthetic manifest is admitted as a **schema control only**;
it is never `admitted` and always `qualifies=false` because no CAPSC artifact
exists.

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
strict JSON, canonical bytes, all controls, eight blocked gates, six open
blockers, licensing, task-local git scope and three cold-start regenerations.
No network, CAPSC artifact, runtime, audio file, device or player is used.

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
- No CAPSC paper, source, binary, runtime, model, dataset, licence text or
  parameter set was copied, imported, built, loaded or reconstructed.
- The candidate note is provenance only: it is not CAPSC source and records no
  CAPSC geometry or result.
- The section 8.6 debt-controller formulation is research with a patent
  warning; it is not CAPSC, is not shipped and is not used here.
- The synthetic occupancy controller, queue-debt, underrun and recovery
  arithmetic are controls only; no audio, queue or device was measured.
- No audio was read or played; no cohort, consent or output-use grant exists.
- No duration, pitch, transient, buffering, rebuffer, drift, queue-debt,
  underrun, recovery or final-partial result was rendered or measured.
- No listening, target-device timing, resource, benchmark or release review was
  performed.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI,
  shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
