<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-BEATNET - BeatNet source/weights/runtime and rate-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`BeatNet` (`component_id=beatnet`). The acceptance profile is **Rate**, assigned
by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, recorded before `opt_in_adapter_exposure`; `evidence_status=incomplete`
and `qualification.status=not_qualified`. A missing, blocked or rejected result
may never qualify the candidate.

The exact licensed BeatNet source, weights, runtime, adapter, immutable revision
and numeric output are **absent**. This package records that exact blocker,
applies the Rate profile to a bounded deterministic synthetic click surrogate,
and makes no beat, downbeat, meter, tempo, quality, timing, listening, benchmark
or release claim. It is **not BeatNet**: no CRNN, particle filter, weight file,
native library, real audio, corpus, model, device clock or upstream code is
present, copied, downloaded, loaded, imported or executed. Only this task-local
directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=beatnet`) is `considered`,
`disposition=sdk-reference`, `verification_profile=rate`, with the note
"CRNN + particle filter; 22.05 kHz input." Its only evidence link is
`cpp-library/pipeline-validation/playback-speed-candidates.md`, where BeatNet is
one row in a factor-provider table. That row reports CC-BY-4.0, online modes and
22.05 kHz input; it does not provide a source revision, weight artifact, runtime,
license text, adapter, numeric result or corpus.

Consequently:

- no BeatNet source, weights, runtime, adapter or pinned revision is staged at
  `data/checkouts/beatnet`, `data/models/beatnet`, `data/envs/beatnet` or
  `adapters/beatnet`;
- no immutable source/weight hash, build/archive identity or adapter setting
  exists for BeatNet itself;
- the reported 22.05 kHz native input conflicts with installed v0 16 kHz mono
  160-sample geometry and `resampling=none`; no approved resampler is contracted;
- no CC-BY-4.0 license text, attribution bundle, weight terms, training-data
  statement or rights review is staged;
- no real music or speech, beat/downbeat/meter label, consent, corpus terms,
  held-out split or task-matched score exists;
- no target-device timing, listening result, independent review, provider intake
  or release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-BEATNET`, `d7f4f9d4426b007be8fc9c24f3a1d58203b69257` |
| Task mode | `feasibility` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate native rate | 22.05 kHz, incompatible with v0 and `resampling=none` |
| Surrogate | synthetic integer click trains, 16 kHz mono |
| Added content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate derives a causal log-energy onset envelope from caller-owned
160-sample frames, estimates tempo from source-anchored inter-onset intervals,
votes on meter/downbeat phase from synthetic accent strengths, and checks block
invariance, reset, gap exclusion and adverse rejection. It is **not BeatNet** and
cannot qualify the candidate.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic only | Events carry exact source intervals and frame-monotonic availability; no audio output or device clock |
| Duration | synthetic only | Exact event-span mapping at 0.8x, 1.0x and 1.2x in integer samples (`max_error_samples=0`) |
| Pitch and transient audibility | blocked | No pitch preservation, transient audibility, TSM or listening test |
| Playback buffering | synthetic only | 160-sample frame aggregation and one 137-sample final window; no worker/queue/renderer measured |
| 1x, rate changes, unfamiliar speech, music, silence | synthetic only | Stable 100 BPM at 1x; 80 BPM at 0.8x; 120 BPM at 1.2x; unstable speech-like train; silence has no onsets |
| Rebuffer, drift, final partial window | synthetic only | One cross-gap IOI excluded; monotonic IOI decrease without a global BPM; explicit 137-sample final frame |
| Speech preservation and pause decisions | blocked | No real speech, preservation score, pause or filler decision tied to source timestamps |
| Task-matched held-out qualification | blocked | No rights-cleared held-out music/speech cohort, labels or matched score |

Every tempo, beat and meter row is `qualifies=false`. Synthetic exactness means
only that the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  exactly 10,000,000 ns per full frame.
- Candidate native rate: 22,050 Hz is rejected before state advance with
  `candidate_native_rate_requires_resampling`; installed v0 accepts only
  16 kHz and `resampling=none`.
- Click burst: 96 samples from a fixed 64-entry integer sine table at 150 Hz,
  scaled by a linear decay; amplitudes are integer milli-units.
- Beat times are exact integer frame coordinates; all periodic intervals are
  multiples of 160 samples.
- Ten stimuli: `steady_music_1x` (100 BPM 4/4), `rate_0_8` (80 BPM),
  `rate_1_2` (120 BPM), `tempo_step` (100 then 150 BPM), `syncopated_offbeat`,
  `speech_like_unfamiliar`, `rebuffer_gap`, `drift_decreasing`, `silence`,
  `final_partial`.
- `rebuffer_gap` excludes exactly the cross-gap IOI `[48000, 72000)`; no tempo
  is inferred across that gap.
- `final_partial` has 137 valid samples, zero padding, and one click at source
  sample 64,010 detected in frame 400 at source 64,000 (`-10` sample
  frame-quantization error).
- `tempo_step` yields exact local segments `[10000, 15000]` BPM x100 while the
  global estimate remains `unstable`; no global tempo is claimed.

All synthetic beat matches are exact (`false_positives=0`,
`false_negatives=0`). The meter vote returns 4 for the three 4/4 surrogates and
`ambiguous` for the syncopated offbeat control. Those are synthetic observations
only; real beat/downbeat/meter qualification remains blocked.

## Adverse, missing and invalid handling

`report.json` records 40 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, missing/extra config fields, 8 kHz, 44.1 kHz, 22.05 kHz, stereo,
256-sample frame, `int16`, clock drift, boolean rate, missing input, wrong epoch,
wrong count, invalid valid-count, nonfinite input, nonzero padding, string and
boolean samples, unknown stimulus kind, zero period, negative/out-of-range
amplitude, noninteger period, nonzero silence, misaligned final partial, length
mismatch, reset epoch 0/-1, and missing/relative/bad-commit/wrong-rate/
wrong-channel/bad-hash/extra-field caller manifests. Missing real recordings,
weights, runtime outputs and labels are `blocked`, never passes.

The caller asset contract validates identity only. It never reads, loads,
imports or executes a source tree, weight file or runtime. A hash-matched
placeholder is never accepted as the pinned BeatNet artifact.

## Streaming, reset and determinism

The analyzer is frame-clocked: arbitrary caller chunks
`160/480/800/137/641` reproduce the full-block event list exactly
(`all_match=true`, `accepted_samples=64137`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0 and negative epochs are rejected with the state digest
unchanged. `run.py` builds the report three times and refuses to write unless
every payload is byte-identical.

## Separation from sibling evidence

The merged `aubio` package is a separate GPL-3.0 onset/tempo blocker with its own
fixtures and disposition. The merged `soundtouch` and `signalsmith-stretch`
packages are separate TSM actuator proposals. This package does not import,
pool, score or reuse their source, fixtures, metrics or results. Their README
and report files are pinned only as read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen stimuli, causal analyzer, tempo/beat/meter estimators, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Rate report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sdk:docs/task-evidence/aubio/README.md` | `700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d` |
| `sdk:docs/task-evidence/aubio/report.json` | `0ee56f1ecc66440b25f8d0c54e88ba5d2ba4f66c316fe8b0c3a4e626896e06f1` |
| `sdk:docs/task-evidence/aubio/contract.json` | `3777518ee55fdf6927b66e66060a1a3503dcca455452a10a5aa8f4d00dd7f768` |
| `sdk:docs/task-evidence/soundtouch/README.md` | `951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550` |
| `sdk:docs/task-evidence/soundtouch/report.json` | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` |
| `sdk:docs/task-evidence/signalsmith-stretch/README.md` | `446398e0c3aa27528e5ceacf1d4d0b6102f8c8e541c76aa6ac2a8abe62691934` |
| `sdk:docs/task-evidence/signalsmith-stretch/report.json` | `e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-BEATNET/docs/task-evidence/beatnet
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-BEATNET diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned BeatNet source, weights and runtime with an immutable
   revision, license identity and adapter settings.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build, weight
   identity and fail-closed absent behavior.
3. `RG-03` CC-BY-4.0 attribution, weight/training-data and corpus rights,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` 22.05 kHz native input versus installed 16 kHz mono v0 with
   `resampling=none`: exact mapping decision and byte-level parity.
5. `RG-05` beat, downbeat, meter and tempo qualification on rights-cleared
   task-matched held-out music and speech.
6. `RG-06` online state, reset, latency, availability, final partial window,
   drift and rebuffer behavior at the exact runtime.
7. `RG-07` target-device pacing and playback integration with independent
   pitch/transient controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed BeatNet source, weights and runtime
with an immutable revision, admit an isolated hash-pinned runtime, clear the
CC-BY-4.0 attribution and weight/corpus rights, resolve the 22.05 kHz input to
installed 16 kHz geometry without an unapproved resampler, reproduce exact
beat/downbeat/meter/tempo outputs and qualify them on a rights-cleared
task-matched held-out cohort, measure target timing and complete opt-in provider
intake. Until then the candidate stays **DEFER**, **incomplete** and **not
qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`. Installed v0 remains 16 kHz, mono, float32, 160
samples per frame. The board is referenced by stable linked-row fields only
(`tasks[id=SDK-BEATNET]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source. No
provider, descriptor, registry, installed default, shared build or CI is changed.
