<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CRNN-VAD - CRNN VAD architecture, checkpoint and rights blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`CRNN VAD` (`component_id=crnn-vad`). The acceptance profile is **Analysis**,
assigned by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`.
Decision: **DEFER**, recorded before `opt_in_adapter_exposure`;
`evidence_status=incomplete` and `qualification.status=not_qualified`. A
missing, blocked or rejected result may never qualify the candidate.

The exact licensed CRNN architecture, checkpoint, source, runtime, adapter,
immutable revision, feature/timestamp geometry and numeric output are **absent**.
This package records that exact blocker, applies the Analysis profile to a
bounded deterministic synthetic VAD surrogate, and makes no accuracy, FN/FP,
calibration, latency, listening, benchmark or release claim. It is **not a
CRNN**: no convolution, recurrent layer, learned parameter, weight file, native
library, real audio, corpus, model or device clock is present, copied,
downloaded, loaded, imported or executed. Only this task-local directory is
added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=crnn-vad`) is `blocked`,
`disposition=sdk-model`, `verification_profile=analysis`, area `Detection`.
Its only evidence link is `research/voice-enhancement-20261101/candidate_matrix.csv`
record 3, whose finding is:

> No exact CRNN architecture/checkpoint/source or adapter is selected; accuracy
> and performance cannot be measured for an undefined candidate.

The comparison baseline is "WebRTC and Silero integration paths". No source
repository, immutable revision, paper/technical report, checkpoint, weight
digest, parameter count, sample rate, hop, window, feature normalization,
recurrent layout, timestamp protocol, output geometry, license identity,
training-data statement or numeric output is recorded. The record is not a code
or weight license.

Consequently:

- no CRNN source, checkpoint, runtime, adapter or pinned revision is staged at
  `data/checkouts/crnn-vad`, `data/models/crnn-vad`, `data/envs/crnn-vad` or
  `adapters/crnn-vad`;
- no immutable source/weight hash, build/archive identity, parameter layout,
  sample rate, hop, window, feature contract or numeric output exists for CRNN
  VAD itself;
- no upstream LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; no learned
  model, tensor runtime or analysis event ABI is admitted here;
- no real speech, noisy/silent cohort, consent, held-out split, FN/FP,
  calibration or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CRNN-VAD`, `7b00d762530bb69ca58d4cdb8194a83839e1d58c` |
| Task mode | `feasibility` |
| Acceptance profile | `analysis` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/window/parameter count asserted |
| Surrogate | fixed integer RMS plus zero-crossing frame probability |
| Surrogate content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer frame classifier over a frozen synthetic mono
fixture. It is **not CRNN**, is not learned, uses no weights and cannot qualify
the candidate.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Timestamped probabilities | synthetic only | 260 per-frame `probability_micro` records on exact half-open source intervals |
| Event boundaries | synthetic only | 3 detected runs against 3 fixture-construction active segments |
| Quiet and active speech | synthetic only | 170 active frames and 90 quiet frames from declared segments |
| Idle noise | synthetic only | Deterministic low-amplitude integer LCG noise in three idle regions |
| Known positives and negatives | synthetic only | Labels come from segment construction; no real recordings |
| Onset/offset delay | synthetic only | 0-frame onset and offset delay at the declared boundary |
| Stratified FN/FP | synthetic only | Active-speech and quiet-noise strata; no held-out cohort |
| Validity separate from nonspeech | synthetic only | Invalid/missing frames carry null probability and are excluded from denominators |
| Independent state | synthetic only | Two interleaved sessions match independent solo digests |
| Exact source intervals | synthetic only | Contiguous half-open sample intervals; 137-sample final partial frame |
| Availability | synthetic only | Declared monotone synthetic formula; no device clock or service time |
| Dropped/stale events | synthetic only | Bounded bus records stale-epoch, stale-sequence and queue-full drops |
| Cross-hop behavior | synthetic only | Four caller chunk plans reproduce one event digest |

All thirteen rows are `synthetic_only`; none is promoted to candidate evidence.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Length: 41,600 samples (2.6 s), exactly 260 frames, fixture digest
  `878c40a0674885f39010a97a121bc5ebe5883eb95e557e2d8a0d90f1fc81862a`.
- Segments, all frame-aligned:
  - `idle_lead` `[0, 6400)` noise;
  - `speech_a` `[6400, 16000)` active, sine steps 3/5;
  - `pause` `[16000, 19200)` quiet;
  - `speech_b` `[19200, 28800)` active, sine steps 5/7;
  - `idle_mid` `[28800, 32000)` noise;
  - `speech_c` `[32000, 40000)` active, sine steps 7/9;
  - `idle_tail` `[40000, 41600)` noise.
- Active generation: two embedded 64-entry sine-table oscillators, a 16-step
  syllable envelope and deterministic LCG broadband at amplitude 1,000.
- Idle generation: deterministic integer LCG at amplitude 500; pause at 120.
- Surrogate features: integer RMS and zero-crossing count over 160 valid
  samples. Probability is an energy Hill term times a zero-crossing voicing
  weight, all integer arithmetic, scale 1,000,000.
- Decision rule: threshold 500,000 micro, onset confirmation 2 frames, hangover
  3 frames. Both settings and the feature formula are pinned in
  `surrogate_model.spec` (`sha256=914231a686dd2d6c28c7c6e91c934abe0c2fb29967150099f39aaee2a32d9b93`).
- Scorer: Brier micro, frame hit/miss counts, onset/offset frame delay and
  stratified ppm rates, pinned separately at
  `sha256=8307aab726e9f182fc84e52318152c22589bce41ff8d69ded6ed8951ea242af0`.
  The scorer is not an oracle and never imports candidate output.

Measured synthetic observations (all unqualified):

| Item | Value |
| --- | ---: |
| Frames / events | 260 |
| Active / quiet frames | 170 / 90 |
| Brier score, micro | 9,879 |
| Frame accuracy, ppm | 1,000,000 |
| True / false positives | 170 / 0 |
| True / false negatives | 90 / 0 |
| FN rate, ppm | 0 |
| FP rate, ppm | 0 |
| Detected speech runs | 3 |
| Maximum onset / offset delay, frames | 0 / 0 |
| Threshold 950,000 FN rate, ppm | 758,824 (129 frames, sensitivity control) |
| First / last availability, ns | 1,012,500,000 / 3,602,500,000 |
| Event digest, SHA-256 | `2757ecc35710f76ad6101bb6805d69c3ac524fb2c8c584ffc4240975ac2f6c24` |

The perfect frame score is an artifact of a deliberately separable synthetic
tone/noise fixture, not evidence of real VAD performance. The 950,000-threshold
control demonstrates that the stratified FN count responds to the decision
setting.

## Adverse, missing and invalid handling

`report.json` records 73 rejected inputs. Each record carries a live
`state_digest_before` and `state_digest_after` measured around the rejection;
`state_unchanged` is the measured equality result, and a test deliberately
mutates local state behind the same probe to prove the check is live.
Rejections include duplicate JSON key, `NaN`/`Infinity`/`-Infinity` constants,
malformed JSON, non-object root, trailing data, BOM, missing/extra config
fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame, `int16`, boolean rate, float
epoch, negative epoch/position, unsupported mode/resampling/clock, missing
origin, nonfinite sample values, string and boolean samples, wrong frame count,
partial frame without final marker, zero/oversized valid count, non-zero
padding, invalid validity token, out-of-range probability override, stale or
duplicate sequence, processing after final, malformed/relative/vendored/bad-hash
caller manifests, malformed events, invalid reset epochs, invalid bus epochs and
invalid chunk plans.

Missing real recordings, source, checkpoint, runtime outputs and labels are
`blocked`, never passes. The caller manifest validates declaration identity
only; it never reads, loads, imports or executes a source tree, weight file or
runtime. A hash-matched placeholder is never accepted as the pinned CRNN
artifact.

## Streaming, reset and determinism

The probe is frame-clocked. Caller chunk plans `160`-only, a 15-frame cycle
`160/320/480/800/640`, a 22-frame cycle `800/480/160/320/640` and one 41,600
chunk all reproduce the same event digest (`all_match=true`). Reset to epoch 2
matches a fresh epoch-2 session after clearing events and counters; epoch 0,
negative and boolean epochs are rejected with state unchanged. A 137-sample
final partial frame advances exactly 137 samples, zero-pads 23 samples, marks
the event interval `[0, 137)` and rejects later processing. `run.py` builds every
generated payload three times and refuses to write unless all rounds are
byte-identical.

## Separation from sibling evidence

The merged `webrtc-vad`, `silero-vad-6-2-3-reference` and `conv-tasnet` packages
are separate proposals with their own fixtures, assets, metrics and
dispositions. This package does not import, pool, score or reuse their source,
fixtures, metrics or results. Their README and report files are pinned only as
read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen fixture, integer surrogate, session, scorer, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Analysis report; strict JSON, sorted keys, LF. |
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
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:reports/vad-research/chaining-evaluation.md` | `f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234` |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
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
| `sdk:docs/task-evidence/webrtc-vad/README.md` | `1b3c5968c187b97bd67dcf2006581bd111d3cddc03911d5530d9e14325dfbc65` |
| `sdk:docs/task-evidence/webrtc-vad/report.json` | `762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb` |
| `sdk:docs/task-evidence/silero-vad-6-2-3-reference/README.md` | `90b5cb35ce83428782b6901eaff8a479d2acdb49709a40b7fc0450e7ea9237b8` |
| `sdk:docs/task-evidence/silero-vad-6-2-3-reference/report.json` | `dac376c116b9734a63a9ee9931ccd11223bbda998503e8ff7bd2a00d7491a319` |
| `sdk:docs/task-evidence/conv-tasnet/README.md` | `3560a2b238bb7d18b5ad6c057f1385c650a8cda246c7e87fee2db16e6d3a0290` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CRNN-VAD/docs/task-evidence/crnn-vad
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CRNN-VAD diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical (3x cold-start
regeneration). External reproduction runs `run.py` three times and compares the
resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned CRNN VAD source, checkpoint and runtime with an immutable
   revision, weight digest, license identity, parameter/feature geometry and
   timestamp protocol.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build, verified
   weight identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` exact candidate rate, hop, window, feature, timestamp and event
   geometry mapped into the installed mono stream with byte-level parity.
5. `RG-05` task-matched held-out speech qualification with independently pinned
   FN/FP, boundary, calibration and stratified validity scoring.
6. `RG-06` streaming state, reset, stale/dropped events, availability, cross-hop
   and nonfinite behavior at the exact runtime.
7. `RG-07` target-device pacing, timing, memory and power with independent
   listening and/or downstream ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed CRNN VAD architecture, checkpoint
and runtime with immutable source and weight digests, documented geometry and
feature/timestamp protocol; admit an isolated hash-pinned runtime; clear code,
weight, training-data and corpus rights; map exact candidate output into the
installed mono boundary with parity; qualify FN/FP, boundary and calibration on
a rights-cleared task-matched held-out speech cohort; measure target timing; and
complete opt-in provider intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-CRNN-VAD]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
