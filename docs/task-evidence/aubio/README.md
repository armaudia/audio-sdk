# SDK-AUBIO — task-local synthetic Rate-profile evidence

Proposal-only, incomplete and **not qualified** evidence for the `aubio` factor
provider candidate. The structured inventory assigns the **Rate** acceptance
profile (`plan/swarm/VERIFICATION.md`, pinned below). This package applies that
profile to an original, stdlib-only onset/tempo surrogate. It is **not** aubio
source, a vendored aubio build, a licensed aubio runtime, an aubio result or a
release qualification.

## Disposition and boundary

- Status: `proposal_only_not_qualified`; decision `incomplete` / `DEFER`.
- All seven release gates are blocked; no synthetic check opens a gate.
- No upstream aubio source, binary, GPL runtime, weights, model, corpus or asset
  is present, downloaded or executed. `GPL-3.0` appears only as a pinned
  provenance/blocker string, never as the license of a task file.
- No provider is registered, exposed as a processor, enabled by default or
  selected as a descriptor default.
- No public API or ABI change, header change, descriptor/registry change,
  installed-v0 behavior change, shared build/CMake change, CI change, board or
  handoff write, or other task's files are changed.
- Only `docs/task-evidence/aubio/` is written. The pinned source and SDK
  boundary files are read-only inputs.
- No listening, device timing, wall-clock playback measurement, pitch
  preservation, transient audibility, benchmark or release claim is made. No
  audio is produced, modified or played.

The preserved `contract.json` and `fixtures.json` remain byte-identical to the
starting work. Four minimal corrections were made to the preserved
`reference.py` scaffold so its own validator and scorer are self-consistent:
the onset hysteresis is 7 frames (70 ms, matching the irregular fixture's
70 ms gap); the unfamiliar-speech check accepts any non-stable/no-BPM outcome;
rebuffer suppression is derived from the excluded cross-gap IOI count; and the
availability margin is computed from event lists and asserted as nonnegative
rather than equal to zero. No algorithm, fixture, gate or disposition was
loosened into a release claim.

## Rate profile application

The pinned source-of-truth row requires source/output mapping, duration, pitch,
transient audibility and playback buffering, with 1×, rate changes, unfamiliar
speech, music, silence, rebuffer, drift and the final partial window, and ties
pause/filler decisions to source timestamps with speech preservation measured.
This package records those items as follows:

| Requirement | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Source/output mapping | `rate_profile.source_output_mapping`: analysis events carry `source_start`/`source_end` and fixture-monotonic availability; no audio output produced | Fixture coordinates only; no rendered output or device clock |
| Duration | `rate_profile.duration`: exact source-sample spans at 0.8×, 1× and 1.2× (`max_error_samples=0`) | Event-time scaling, not playback duration |
| Pitch | `rate_profile.pitch.status=not_measurable_analysis_only`, `qualifies=false` | Unmeasured; BLK-07 remains blocked |
| Transient audibility | `rate_profile.transient_proxy`: −50-sample frame-quantized onset proxy | Not listening or audibility |
| Playback buffering | `rate_profile.playback_buffering`: 160-sample aggregation, 137-sample final window, zero padding verified | No SDK worker, queue, renderer or fill/flush measured |
| 1× / rate changes | `identity_1x=10000`, `rate_0_8=8000`, `rate_1_2=12000` (BPM×100) | Synthetic periodic surrogates |
| Unfamiliar speech | `speech_like_unfamiliar` has no stable BPM and `qualifies=false` | No speech-preservation measurement; BLK-03 remains blocked |
| Music / silence | Stable 100 BPM music surrogate; silence has no onsets | Analytic surrogates |
| Rebuffer | One cross-gap IOI excluded; no tempo inferred across the gap | No real rebuffer event measured |
| Drift | Monotonic source-anchored IOI decrease recorded | No global BPM claim |
| Final partial | 137 valid samples, explicit event digest and zero padding | Exact final-window accounting only |

Every rejection, adverse, missing or nonfinite outcome is retained in
`adverse_cases` with `qualifies=false`; state-changing frames are rejected
before any state advance. `profile_scoring` contains all 16 exact checks and
passing it means only that the synthetic fixture is self-consistent.

## Pins

Paths outside `docs/task-evidence/aubio/` are relative to the `audioml`
source root; SDK boundary paths are relative to the SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | aubio GPL-3.0 / proprietary-use finding |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Real-time candidate provenance |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build/integration surface |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 aggregate coverage |

`SOURCES.sha256` additionally pins every task-local artifact; it excludes its
own bytes because a file cannot pin itself. `verify.py` fails closed on a
missing, stale, malformed, duplicated or extra pin and on any worktree change
outside this directory.

## Files

- `contract.json` / `fixtures.json` — preserved strict proposal inputs.
- `reference.py` — synthetic onset/tempo model, strict validators and scorer.
- `run.py` — regenerates the report, digest sidecar and manifest three times.
- `report.json` / `report.json.sha256` — canonical evidence and its digest.
- `SOURCES.sha256` — deterministic manifest of all pinned inputs.
- `test_reference.py` — unittest acceptance suite.
- `verify.py` — read-only canonical JSON, pin, profile, licensing and scope verifier.
- `*.json.license`, `*.sha256.license` — REUSE sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/aubio
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py all` and each single-target mode repeat three times and fail if any
rebuild differs by one byte. `verify.py` never writes to this directory: it
builds three isolated scratch copies with symlinks to the pinned read-only
inputs and checks cold-start regeneration there.

## Remaining gates

Rights-cleared upstream provenance and relicensing, held-out matched speech and
music cohorts, target-device pacing and telemetry, public-surface intake,
pitch/transient qualification with authorized listening, independent exact-head
review and hosted checks, and release approval all remain blocked. Missing or
adverse evidence never qualifies the candidate.
