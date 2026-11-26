<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LIBROSA-BEAT-TRACK-TEMPO - librosa beat_track / tempo readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for `librosa beat_track
/ tempo` (component `librosa-beat-track-tempo`, mode `feasibility`,
`verification_profile: rate`). It is **not** librosa and does **not** contain a
librosa source checkout, wheel, sdist, dependency lock, Python runtime, adapter,
real audio, corpus, beat label, numeric output, listening result, device timing,
benchmark or release claim. **No result here qualifies librosa.**

Pinned base: `b02dbf12499038abc4f9b6b1c06cdecc76a79dcd`.
Branch: `swarm/SDK-LIBROSA-BEAT-TRACK-TEMPO`. Owner:
`agent-LIBROSA-BEAT-TRACK-TEMPO`. Reviewer:
`reviewer-LIBROSA-BEAT-TRACK-TEMPO`.

## Exact external blocker

The inventory record (`plan/INVENTORY.json`, `id=librosa-beat-track-tempo`) is
`considered`, `disposition=sdk-reference`, `verification_profile=rate`, and
links one row of
`cpp-library/pipeline-validation/playback-speed-candidates.md` (line 89):

> **librosa** `beat_track` / `tempo` | BPM, beat times | ISC | Yes | No
> (file/window) | Best prototyping reference; DP beat tracking (Ellis 2007).

That row records a licence label and a prototyping role. It does not provide a
source revision, wheel/sdist hash, dependency lock, runtime, adapter, numeric
result or corpus. The standard evaluation note in
`research/speech-rate-tsm-evaluation-20261101.md` also records that the project
Python 3.12 environment had NumPy/SciPy/SoundFile but **no librosa runtime**.

The exact blocker is the combination of:

1. **No librosa runtime under the required pinned interpreter.** The pinned
   CPython `3.12.16` environment has `numpy==2.5.4`, `scipy==1.18.1` and
   `soundfile==0.14.0`, but no `librosa`, `numba`, `llvmlite`, `audioread`,
   `soxr` or `pooch`. Package installs and downloads are outside this task's
   permission. A local unpinned CPython `3.11.5` virtual environment under
   `cpp-library/pipeline-validation/playback-speed/.venv` does contain
   `librosa==0.11.0`; it is recorded only as an observation. It is not the
   required interpreter, is not pinned, and was **not imported, executed,
   hashed as an admitted asset, or used to produce any number in this package**.
2. **No immutable source or dependency identity.** There is no 40-hex librosa
   source revision, wheel/sdist SHA-256, transitive wheel hash set, lock file,
   build recipe or reviewed entrypoint adapter for `librosa.beat.beat_track`
   and `librosa.beat.tempo`.
3. **No caller-supplied tool runtime.** The caller-tool manifest is defined
   below, but no caller has supplied a pinned runtime, an entrypoint adapter,
   an identity record or a fail-closed absent behavior review.
4. **No exact librosa numeric reference.** No beat frame list, tempo estimate,
   tempo prior or numeric digest was produced by librosa. The synthetic
   click/peak surrogate in this directory is **not librosa**.
5. **No rights-cleared task-matched cohort.** No real music, real speech,
   beat/downbeat/meter label, corpus terms, held-out split, consent or
   output-use grant is present.
6. **No timing, listening, benchmark or release evidence.** No target-device
   pacing, content delay, listening result, independent review, opt-in tool
   intake or release approval exists.

Nothing was downloaded, copied, vendored, installed, built, imported, loaded or
executed. The six exact blockers are `BLK-01`..`BLK-06` in `contract.json` and
`report.json`; the eight release gates are `RG-01`..`RG-08` and all are
`blocked`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-LIBROSA-BEAT-TRACK-TEMPO`, `b02dbf12499038abc4f9b6b1c06cdecc76a79dcd` |
| Task mode | `feasibility` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before `caller_tool_admission` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| librosa default geometry | 22.05 kHz, `hop_length=512`, `n_fft=2048` |
| Configured geometry | 16 kHz, `hop_length=160`, 160 samples/frame |
| Surrogate | synthetic integer click trains, 16 kHz mono |
| Added content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate derives a causal integer log-energy onset envelope from
caller-owned 160-sample frames, estimates tempo from source-anchored
inter-onset intervals, checks local tempo segments, votes on meter from
synthetic accent strengths, and checks chunk invariance, reset, gap exclusion
and adverse rejection. It is **not librosa** and cannot qualify the candidate.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic only | Events carry exact source intervals and frame-monotonic availability; no audio output or device clock |
| Duration | synthetic only | Exact event-span mapping at 0.8x, 1.0x and 1.2x in integer samples (`max_error_samples=0`) |
| Pitch and transient audibility | blocked | No pitch preservation, transient audibility, TSM or listening test |
| Playback buffering | synthetic only | 160-sample frame aggregation and one 137-sample final window; no worker/queue/renderer measured |
| 1x, rate changes, unfamiliar speech, music, silence | synthetic only | Stable 100 BPM at 1x; 80 BPM at 0.8x; 120 BPM at 1.2x; irregular speech-like train; silence has no onsets |
| Rebuffer, drift, final partial window | synthetic only | One cross-gap IOI excluded; monotonic IOI decrease without a global BPM; explicit 137-sample final frame |
| Speech preservation and pause decisions | blocked | No real speech, preservation score, pause or filler decision tied to source timestamps |
| Task-matched held-out qualification | blocked | No rights-cleared held-out music/speech cohort, labels or matched score |

Every tempo, beat and meter row is `qualifies=false`. Synthetic exactness means
only that the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  exactly 10,000,000 ns per full frame.
- librosa defaults are 22.05 kHz, `hop_length=512` and `n_fft=2048`. The
  configured surrogate geometry uses 16 kHz and `hop_length=160`; the default
  mismatch is recorded as `native_default_compatible=false`, not as a parity
  result. No resampler is used.
- Click burst: 96 samples from a fixed 32-entry integer triangle table,
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
  sample 48,010 detected in frame 300 at source 48,000 (`-10` sample
  frame-quantization error).
- `tempo_step` yields exact local segments `[10000, 15000]` BPM x100 while the
  global estimate remains `unstable`; no global tempo is claimed.

All synthetic beat matches are exact (`false_positives=0`,
`false_negatives=0`). The meter vote returns 4 for the three 4/4 surrogates and
`ambiguous` for the syncopated offbeat control. Those are synthetic observations
only; real beat/downbeat/meter qualification remains blocked.

## Caller-supplied tool reference (proposed, not admitted)

A future caller-owned reference would invoke exactly these public entrypoints:

- `librosa.beat.beat_track(y, sr=16000, hop_length=160, ...)` -> beat frame
  indices and tempo;
- `librosa.beat.tempo(y, sr=16000, hop_length=160, ...)` -> tempo estimate.

The caller would supply an isolated CPython `3.12.16` runtime, a pinned
`librosa==0.11.0` wheel/sdist and complete transitive dependency lock, and a
JSON manifest with `schema_id`, `tool`, `entrypoint`, `python`,
`librosa_version`, `wheel_sha256`, `dependency_lock_sha256`, `sample_rate_hz`,
`channels`, `hop_length`, `frame_samples` and `byte_count`. The SDK boundary
would validate identity only: it never reads the wheel bytes, loads the source,
imports the module or executes the runtime. A missing, changed, extra or
unreviewed manifest field fails closed. The contract is defined in
`report.json` -> `caller_tool_reference` and `contract.json` ->
`caller_tool_reference`; it is **not admitted** and **not reproduced**.

## Adverse, missing and invalid handling

`report.json` records 40 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, missing/extra config fields, 8 kHz, 22.05 kHz, 44.1 kHz, stereo,
256-sample frame, `int16`, clock drift, boolean rate, missing input, wrong
epoch, wrong count, invalid valid-count, nonfinite input, nonzero padding,
string and boolean samples, unknown stimulus, zero rate, negative/out-of-range
amplitude, noninteger rate, nonzero silence, misaligned final partial, length
mismatch, reset epoch 0/-1, and missing/wrong-python/relative/bad-hash/
wrong-rate/wrong-channel/extra/zero-byte caller manifests. Missing real
recordings, librosa runtime outputs and labels are `blocked`, never passes.

The caller manifest validates identity only. It never reads, loads, imports or
executes a source tree, wheel or runtime. A hash-matched placeholder is never
accepted as the pinned librosa artifact.

## Streaming, reset and determinism

The analyzer is frame-clocked: arbitrary caller chunks
`160/480/800/137/641` reproduce the full-block event list exactly
(`all_match=true`, `accepted_samples=48137`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0 and negative epochs are rejected with the state digest
unchanged. `run.py` builds the report, contract, README tables and pin manifest
three times and refuses to write unless every payload is byte-identical.

## Scope enforcement

`verify.py` resolves the newest merge-base between `HEAD` and the available PR
base refs `origin/main` and `main`. If no base ref is available it fails closed
with `scope_base_unavailable`. It then lists the branch-added paths against that
base and reports every path outside `docs/task-evidence/librosa-beat-track-tempo/`
as `base_out_of_scope_change:<path>`. This keeps later sibling merges out of the
comparison while still rejecting any out-of-scope branch edit. Three regression
tests in `test_reference.py` cover sibling additions after the base, an
out-of-scope branch edit, and a missing base ref.

## Separation from sibling evidence

The merged `aubio` package is a separate GPL-3.0 onset/tempo blocker with its
own fixtures and disposition. The merged `beatnet` package is a separate
CC-BY-4.0 beat/downbeat/meter blocker. The merged `soundtouch`,
`signalsmith-stretch` and `ffmpeg-atempo` packages are separate TSM actuator
proposals. The merged `numpy-scipy-soundfile-wav-resampling` package is a
separate WAV/resampling reference. This package does not import, pool, score or
reuse their source, fixtures, metrics or results. Their README and report files
are pinned only as read-only boundary references.

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
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and merge-base scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:research/speech-rate-tsm-evaluation-20261101.md` | `525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:docs/task-evidence/aubio/README.md` | `700153d2541f9f4836e878fd6bfec631b644d1bf55ab0868e03f880858bd5e1d` |
| `sdk:docs/task-evidence/aubio/report.json` | `0ee56f1ecc66440b25f8d0c54e88ba5d2ba4f66c316fe8b0c3a4e626896e06f1` |
| `sdk:docs/task-evidence/beatnet/README.md` | `d453bda9ea5d3dda875b05ff7fbd238e5ecdef69ad48deb4be26c68f98b8c828` |
| `sdk:docs/task-evidence/beatnet/report.json` | `dc233e50bd901f44e68c01033d0fe753b47955853a28d81f993f22dce0883399` |
| `sdk:docs/task-evidence/ffmpeg-atempo/README.md` | `11773a543c6dab54ff4754989501a0a70a29b247612e51aee5fb54c0050457b8` |
| `sdk:docs/task-evidence/ffmpeg-atempo/report.json` | `a3986e6cb9d7315995aa13c74806c260c620d01b6f545e0837b127565c2ba249` |
| `sdk:docs/task-evidence/numpy-scipy-soundfile-wav-resampling/README.md` | `9f91d406909fe2f9fa7cfd4b954639d081a12ab16005be761707b6f5c998f40c` |
| `sdk:docs/task-evidence/numpy-scipy-soundfile-wav-resampling/report.json` | `091b57f366c1c5d4d395f955da7d237848bdc7564c970e1a087d423fb702f225` |
| `sdk:docs/task-evidence/soundtouch/README.md` | `951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550` |
| `sdk:docs/task-evidence/soundtouch/report.json` | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `6b65e521aa5552ebba84053590ed209e55f408139f55af8bee21ce3781c2077d` | 13750 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `0a27b675ec895a55fbdfe16e3c4e6420459e03ae4dfbc215749abacae6b708a9` | 72167 |
| `report.json` | `dc1b487945d283b1b200bbeadc7dc681df10af145df43a598700e0749bec5b6a` | 27987 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `743d44c4460ff0de2533f588fad962b31940684547d3fa6ff14281d6bc8310e9` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `6fa3ca4ccb2612db69d26f1c9f4890ea47ee4d2cc104e181b61b8c51d39460cd` | 4760 |
| `test_reference.py` | `d62e4fabfe096ecda886fc097c8b93756d17e8e30ac0f63dd16c2539856b0fcc` | 21057 |
| `verify.py` | `ebc3f6488aacf8e69c6e9508b924c7f527aef03f1e307bb1d4795b844ba896c7` | 28744 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LIBROSA-BEAT-TRACK-TEMPO/docs/task-evidence/librosa-beat-track-tempo
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LIBROSA-BEAT-TRACK-TEMPO diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. Repository checks are
the installed-package `python scripts/ci.py`, `python -m reuse lint` and
`git diff --check`.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned librosa source, wheel/sdist, complete dependency lock
   and CPython `3.12.16` identity with immutable hashes.
2. `RG-02` isolated caller-supplied tool runtime, reviewed entrypoint adapter
   and fail-closed absent behavior.
3. `RG-03` ISC attribution and every transitive dependency license, including
   LGPL `soxr`, with redistribution and product-use decisions.
4. `RG-04` explicit 16 kHz mono 160-sample geometry with `hop_length=160` and
   no unapproved resampling.
5. `RG-05` exact librosa `beat_track`/`tempo` numeric reproduction and parity.
6. `RG-06` rights-cleared task-matched held-out music/speech qualification with
   separate tempo, beat and meter results.
7. `RG-07` target-device timing, content delay, buffering and
   speech-preservation evidence.
8. `RG-08` opt-in tool intake, independent exact-head review and release
   approval.

**Reopen condition.** Supply a caller-owned CPython `3.12.16` environment with
a pinned `librosa 0.11.0` distribution, wheel/sdist SHA-256 and a complete
transitive dependency lock; review the ISC and LGPL `soxr` terms; define the
16 kHz mono 160-sample `hop_length=160` adapter; reproduce the exact
`beat_track`/`tempo` outputs; qualify tempo, beat and meter on a rights-cleared
task-matched held-out music/speech cohort; measure target timing and listening
where permitted; and complete opt-in tool intake with independent exact-head
review. Until then the candidate stays **DEFER**, **incomplete** and **not
qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`, `board_or_handoff_changed=false`. Installed v0
remains 16 kHz, mono, float32, 160 samples per frame. The board is referenced by
stable linked-row fields only (`tasks[id=SDK-LIBROSA-BEAT-TRACK-TEMPO]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
