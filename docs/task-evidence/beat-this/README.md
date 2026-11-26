<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-BEAT-THIS — Beat This! blocker package

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This is a bounded,
deterministic **feasibility and blocker package** for inventory component
`beat-this` (Rate and content, verification profile `Rate`). The exact licensed
Beat This! source checkout, immutable revision, PyTorch weights, model
configuration, runtime, rights record, held-out beat/downbeat cohort and parity
vector are absent. No result in this package qualifies the candidate.

Task owner: `agent-BEAT-THIS`; reviewer: `reviewer-BEAT-THIS`. Claim base:
audio-sdk `df1619f30900db4ae143d87cedb54dbda3477aa6`; branch
`swarm/SDK-BEAT-THIS`. Write scope is only
`docs/task-evidence/beat-this/`.

## What is missing and why nothing qualifies

The pinned research note
`cpp-library/pipeline-validation/playback-speed-candidates.md` (line 94 and the
candidate table) reports Beat This! as **MIT code and weights**, **file-level
inference**, **no documented streaming API**, **PyTorch**, with **8.1 MB
small** and **78 MB main** models. Those are source-reported strings, not
locally verified artifacts. They do not establish a task geometry, a licence
file, a rights grant or an output.

No fixed path in this workspace contains a Beat This! checkout, resolved 40-hex
revision, checkpoint, config, runtime lock, licence text, rights record,
rights-cleared music cohort or parity vector. Nothing is downloaded, vendored,
staged or inferred from the repository URL. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- sample rate, channels, resampling, window, padding and file-level boundary
  are **unestablished** and are not invented;
- no Beat This! output exists, so no beat F-measure, downbeat F-measure, tempo
  accuracy, latency, memory or RTF value is reported;
- missing, adverse, invalid and nonfinite evidence is never promoted to a
  pass, partial qualification or capability claim.

Beat This! is a file-level beat/downbeat tracker candidate, not a time-scale
modifier and not an installed SDK processor. Results from the sibling `aubio`
or `ffmpeg-atempo` packages are not attributed to it.

## Evidence classes and boundaries

- **Pinned research context:** the playback-speed candidate note, the
  real-time candidate note and the structured inventory row. These are
  provenance, not local execution.
- **Sibling context only:** `docs/task-evidence/aubio/README.md` and
  `docs/task-evidence/ffmpeg-atempo/README.md` are pinned as neighbouring
  beat/rate evidence. Their results are not pooled here.
- **Synthetic accounting:** the task-local reference generates deterministic
  analytic click tracks, runs an original log-energy onset detector and derives
  source-anchored inter-onset tempo. It checks exact duration scaling, silence,
  unfamiliar speech, rebuffer gap suppression, drift, the final partial window,
  availability margins and missing/invalid/nonfinite rejection.
- **Not present:** real music or speech, beat/downbeat labels, model weights,
  PyTorch, a model execution, listening, device timing, benchmark or release
  approval.

The synthetic surrogate is **not Beat This!**, performs no inference and cannot
qualify the candidate.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, source/weight/config hashes and licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned PyTorch runtime with a complete lock on a recorded platform | blocked |
| `artifact_rights_and_licence` | Source, weight, training-data, source-audio, output-use and redistribution rights cleared with notices | blocked |
| `exact_reference_parity` | Approved exact-runtime beat/downbeat output matches a frozen caller input and configuration | blocked |
| `beat_cohort_and_scoring` | Rights-cleared held-out music cohort scores beat/downbeat F-measure, tempo accuracy and octave errors | blocked |
| `task_scope_and_geometry` | Sample rate, channels, resampling, window, padding, file boundary and non-streaming limitation established | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision | blocked |
| `public_default_and_release` | Target timing, resource limits, exact-head review, explicit default and release/benchmark approval | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source checkout, unpinned upstream revision, absent
weights/config, unestablished geometry, absent hash-pinned runtime, unverified
licence, uncleared rights/cohort, and absent parity/benchmark evidence. No
blocker is downgraded by the synthetic fixture.

## Rate profile application

The pinned `Rate` row requires source/output mapping, duration, pitch,
transient audibility, playback buffering, 1×, rate changes, unfamiliar speech,
music, silence, rebuffer, drift, the final partial window, source-timestamped
pause/filler decisions and speech preservation. This package applies each item
explicitly:

| Requirement | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Source/output mapping | `rate_profile.source_output_mapping`: analysis events carry exact `source_start`/`source_end`, 160-sample hop and 10,000,000 ns availability | Fixture coordinates only; no rendered output or device clock |
| Duration | `rate_profile.duration`: exact source spans at 0.8×, 1× and 1.2×; `max_error_samples=0` | Event-time scaling, not playback duration |
| Pitch | `rate_profile.pitch.status=not_measurable_analysis_only`, `qualifies=false` | Unmeasured; the corresponding release gate remains blocked |
| Transient audibility | `rate_profile.transient_proxy`: −30-sample frame-quantized onset proxy | Not listening or audibility |
| Playback buffering | `rate_profile.playback_buffering`: 160-sample aggregation, 37-sample final window, zero padding verified | No SDK worker, queue, renderer or fill/flush measured |
| 1× / rate changes | `identity_1x=10000`, `rate_0_8=8000`, `rate_1_2=12000` (BPM×100) | Synthetic periodic surrogates |
| Unfamiliar speech | `speech_like_unfamiliar` has no stable BPM and `qualifies=false` | No speech-preservation measurement |
| Music / silence | Stable 100 BPM music surrogate; silence has no onsets | Analytic surrogates |
| Rebuffer | One cross-gap IOI excluded; no tempo inferred across the gap | No real rebuffer event measured |
| Drift | Monotonic source-anchored IOI decrease recorded | No global BPM claim |
| Final partial | 37 valid samples, exact event digest and zero padding | Exact final-window accounting only |
| Pause/filler + speech preservation | `speech_preservation.status=not_measured`, `qualifies=false` | No real pause/filler decision or preservation result |

Every rejection, adverse, missing or nonfinite outcome is retained in
`adverse_cases` with `qualifies=false`; state-changing frames are rejected
before any state advance. `profile_scoring` contains 24 exact checks; passing it
means only that the synthetic fixture is self-consistent.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the source manifest, weights, config, licence, rights record, runtime lock,
cohort manifest and parity vector; a full 40-hex source revision; a `small` or
`main` variant; mono/stereo bounds; and bounded sample-rate and weight byte
counts. Any missing, malformed, relative, nonfinite, out-of-range, mismatched
or unsupported field is rejected before processing. No upstream revision is
pinned because the merged evidence records only the repository URL. A
shape-valid manifest cannot manufacture qualification.

## Pins and task identity

Paths outside this directory are relative to the `audioml` source root; SDK
boundary paths are relative to the SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Beat This! MIT/model/streaming finding |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Real-time candidate provenance |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Structured component row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build/integration surface |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` / `scripts/ci.py` / `REUSE.toml` | pinned in `SOURCES.sha256` | Unchanged build, CI and licensing |
| `docs/task-evidence/aubio/README.md` | `700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d` | Sibling beat context only |
| `docs/task-evidence/ffmpeg-atempo/README.md` | `11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8` | Sibling rate context only |

The task row is linked by its **stable fields only** (`acceptance`, `component`,
`deliverable`, `depends_on`, `evidence`, `id`, `mode`, `repository`, `title`,
`write_scope`). The projected digest is
`ecb5e7ad8628df34ebb2d2945838b2bb4f1752c39c7598207b02724b0fa5ebc2`.
Mutable fields (`blocked_reason`, `dispatch_priority`, `handoff`, `owner`,
`review`, `status`) are excluded. The mutable full `plan/swarm/TASKS.json` is
**never hashed, pinned or used as a digest source**.

`SOURCES.sha256` additionally pins every task-local artifact; it excludes its
own bytes because a file cannot pin itself. `verify.py` fails closed on a
missing, stale, malformed, duplicated or extra pin, on any worktree change
outside this directory, and on any cold-start byte difference.

## Files

- `contract.json` — strict machine-readable `decision="DEFER"`,
  `proposal_only` / `incomplete`, `qualification.status="not_qualified"`, eight
  blocked gates, eight exact blockers and the caller asset contract.
- `reference.py` — synthetic onset/tempo model, strict validators, absence
  audit, caller-manifest validation and scorer.
- `run.py` — regenerates contract, report, digest sidecar and manifest three
  times and requires byte-identical output.
- `report.json` / `report.json.sha256` — canonical evidence and its digest.
- `SOURCES.sha256` — deterministic manifest of all pinned inputs.
- `test_reference.py` — unittest acceptance suite.
- `verify.py` — read-only strict JSON, pin, profile, licensing, scope and
  three cold-start regeneration verifier.
- `*.json.license`, `*.sha256.license` — REUSE sidecars.

## Reproduction

```sh
cd docs/task-evidence/beat-this
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

`run.py all` repeats three times and fails if any rebuild differs by one byte.
`verify.py` never writes to this directory: it builds three isolated scratch
copies with symlinks to the pinned read-only inputs and checks cold-start
regeneration there.

## Remaining gates

Rights-cleared upstream provenance and licence verification, a pinned
checkpoint/config/runtime, exact-runtime parity, held-out matched music scoring,
target-device pacing and telemetry, opt-in public-surface intake, independent
exact-head review and hosted checks, and release approval all remain blocked.
Missing or adverse evidence never qualifies the candidate. No merge, formal
approval or release action is taken here.
