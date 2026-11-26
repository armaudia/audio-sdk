<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MADMOM — madmom blocker package

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This is a bounded,
deterministic **feasibility and blocker package** for inventory component
`madmom` (Rate and content, verification profile `Rate`). The exact licensed
madmom source checkout, immutable revision, pretrained models, model
configuration, runtime, licence records, rights record, held-out
beat/downbeat cohort and parity vector are absent, and the pinned evidence
records the shipped pretrained models as **non-commercial**. No result in this
package qualifies the candidate.

Task owner: `agent-MADMOM`; reviewer: `reviewer-MADMOM`. Claim base:
audio-sdk `b4960fdba1991a35c07ff7f22cda5257c4749768`; branch
`swarm/SDK-MADMOM`. Write scope is only `docs/task-evidence/madmom/`.

## What is missing and why nothing qualifies

The pinned research note
`cpp-library/pipeline-validation/playback-speed-candidates.md` reports, across
lines 22, 90, 450, 499 and 506, that madmom returns **BPM, beats and
downbeats**; that its **source is BSD** (BSD-2/3 family) while its
**pretrained models are CC BY-NC-SA 4.0**; that commercial use is **"No with
shipped models"**; that only **some models** are online; that the method is
**RNN/DBN beat and downbeat tracking**; that the repository is
`https://github.com/CPJKU/madmom`; and that callers should **contact JKU** and
**not ship the pretrained models without permission**. Those are
source-reported strings, not locally verified artifacts.

No fixed path in this workspace contains a madmom checkout, resolved 40-hex
revision, pretrained model file, model configuration, runtime lock, licence
text, JKU commercial grant, rights record, rights-cleared music cohort or
parity vector. `madmom` is not importable in the recorded Python 3.11.5
interpreter, and no environment or lock exists. Nothing is downloaded,
vendored, staged or inferred from the repository URL. Consequently:

- source identity, model hashes and licence terms cannot be pinned;
- the reported CC BY-NC-SA 4.0 model terms block commercial release and are
  not resolved by the BSD source licence;
- sample rate, channels, frame hop, window/context, model-specific online
  behaviour and file-level boundary are **unestablished** and are not
  invented;
- no madmom output exists, so no beat F-measure, downbeat F-measure, tempo
  accuracy, latency, memory or RTF value is reported;
- missing, adverse, invalid and nonfinite evidence is never promoted to a
  pass, partial qualification or capability claim.

madmom is a beat/downbeat/tempo analysis candidate, not a time-scale modifier
and not an installed SDK processor. Results from the sibling `beat-this` or
`beatnet` packages are not attributed to it.

## Evidence classes and boundaries

- **Pinned research context:** the playback-speed candidate note, the
  real-time candidate note and the structured inventory row. These are
  provenance, not local execution.
- **Sibling context only:** `docs/task-evidence/beat-this/README.md` and
  `docs/task-evidence/beatnet/README.md` are pinned as neighbouring
  beat/onset evidence. Their results are not pooled here.
- **Synthetic accounting:** the task-local reference generates deterministic
  analytic click tracks, runs an original log-energy onset detector, derives
  source-anchored inter-onset tempo and an analytic accent-period meter
  (downbeat surrogate). It checks exact duration scaling, silence, unfamiliar
  speech, rebuffer gap suppression, drift, meter phase, the final partial
  window, availability margins and missing/invalid/nonfinite rejection.
- **Not present:** real music or speech, beat/downbeat labels, model weights,
  madmom, a model execution, listening, device timing, benchmark or release
  approval.

The synthetic surrogate is **not madmom**, performs no inference and cannot
qualify the candidate. The derived "meter" is an analytic accent period on a
synthetic click track, not musical downbeat detection.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, source/model/config hashes and licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned Python/Cython runtime with a complete lock on a recorded platform | blocked |
| `artifact_rights_and_licence` | Source, model, training-data, source-audio, output-use and redistribution rights cleared, including the non-commercial model terms | blocked |
| `exact_reference_parity` | Approved exact-runtime beats/downbeats/tempo output matches a frozen caller input and configuration | blocked |
| `beat_cohort_and_scoring` | Rights-cleared held-out music cohort scores beat/downbeat F-measure, tempo accuracy and octave errors | blocked |
| `task_scope_and_geometry` | Sample rate, channels, resampling, hop, window/context, online behaviour and file boundary established | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision | blocked |
| `public_default_and_release` | Target timing, resource limits, exact-head review, explicit default and release/benchmark approval | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source checkout, unpinned upstream revision,
**non-commercial pretrained-model rights**, absent models/config, unestablished
geometry/streaming, absent hash-pinned runtime, unverified source licence and
absent parity/cohort/benchmark evidence. The model-rights blocker has state
`restrictive`; every other blocker is `absent`. No blocker is downgraded by
the synthetic fixture.

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
| Unfamiliar speech | `speech_like_unfamiliar` has no stable BPM or meter and `qualifies=false` | No speech-preservation measurement |
| Music / silence | Stable 100 BPM music surrogate with meter 4; silence has no onsets | Analytic surrogates |
| Rebuffer | One cross-gap IOI excluded; no tempo inferred across the gap | No real rebuffer event measured |
| Drift | Monotonic source-anchored IOI decrease recorded | No global BPM claim |
| Final partial | 37 valid samples, exact event digest and zero padding | Exact final-window accounting only |
| Pause/filler + speech preservation | `speech_preservation.status=not_measured`, `qualifies=false` | No real pause/filler decision or preservation result |

Every rejection, adverse, missing or nonfinite outcome is retained in
`adverse_cases` with `qualifies=false`; state-changing frames are rejected
before any state advance. `profile_scoring` contains 31 exact checks; passing
it means only that the synthetic fixture is self-consistent.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the source manifest, weights, model config, licence record, model-licence
text, commercial grant, rights record, runtime lock, cohort manifest and parity
vector; a full 40-hex source revision; a restricted `model_license_id`; a
boolean `commercial_use_permitted`; mono/stereo bounds; and bounded sample-rate
and weight byte counts. Any missing, malformed, relative, nonfinite,
out-of-range, mismatched or unsupported field is rejected before processing.

Validation is metadata-only: a `commercial_use_permitted=true` field is echoed
as caller metadata and never treated as an independently verified JKU grant or
as qualification. No upstream revision is pinned because the merged evidence
records the repository URL but no tag or commit.

## Pins and task identity

Paths outside this directory are relative to the `audioml` source root; SDK
boundary paths are relative to the SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | madmom BSD/CC BY-NC-SA/model/online finding |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Real-time candidate provenance |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Structured component row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build/integration surface |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` / `scripts/ci.py` / `REUSE.toml` | pinned in `SOURCES.sha256` | Unchanged build, CI and licensing |
| `docs/task-evidence/beat-this/README.md` | `55e1b0f327c2e6beb4cf9726fe06dafebb5e8b364a1e7188c91d20f17c4a9f32` | Sibling beat context only |
| `docs/task-evidence/beatnet/README.md` | `d453bda9ea5d3dda875b05ff7fbd238e5ecdef69ad48deb4be26c68f98b8c828` | Sibling onset/beat context only |

The task row is linked by its **stable fields only** (`acceptance`, `component`,
`deliverable`, `depends_on`, `evidence`, `id`, `mode`, `repository`, `title`,
`write_scope`). The projected digest is
`73624c37514f155680c9a30b7c39a6539daa2c7b2eb14107c496986d7e7a4a1d`.
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
  blocked gates, eight exact blockers (including the non-commercial
  model-rights blocker) and the caller asset contract.
- `reference.py` — synthetic onset/tempo/meter model, strict validators,
  absence audit, caller-manifest validation and scorer.
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
cd docs/task-evidence/madmom
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

Rights-cleared upstream provenance and licence verification, resolution of the
CC BY-NC-SA 4.0 pretrained-model restriction (JKU commercial grant or
permissively licensed replacement weights), a pinned model/config/runtime,
exact-runtime parity, held-out matched music scoring, target-device pacing and
telemetry, opt-in public-surface intake, independent exact-head review and
hosted checks, and release approval all remain blocked. Missing or adverse
evidence never qualifies the candidate. No merge, formal approval or release
action is taken here.
