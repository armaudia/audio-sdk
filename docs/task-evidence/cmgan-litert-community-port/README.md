<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CMGAN-LITERT-COMMUNITY-PORT — source/model/runtime/parity blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`CMGAN-LiteRT community port` (`component_id=cmgan-litert-community-port`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact third-party port, converted LiteRT model, LiteRT runtime, delegate,
Android target, conversion record, numeric output and license chain are
**absent**. This package records that exact blocker, applies the Enhancement
profile to a bounded deterministic synthetic surrogate, and makes no
enhancement, parity, quality, timing, listening, benchmark or release claim. It
is **not CMGAN** and **not the community LiteRT port**: no conformer, metric GAN,
STFT mask network, FP16 tensor, TFLite flatbuffer, interpreter, delegate, NPU,
Android device, corpus, model, weight, clock or upstream code is present,
copied, downloaded, loaded, imported or executed. Only this task-local directory
is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`,
`id=cmgan-litert-community-port`, matrix record 88) is `blocked`,
`disposition=sdk-model`, `verification_profile=enhancement`. Its finding is:
"No local LiteRT weights/runtime or Android target; third-party conversion
parity unverified." Its evidence chain is
`research/voice-enhancement-20261101/candidate_matrix.csv`,
`research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md` and
`research/voice-enhancement-20261101/agent-denoise/REPORT.md`.

The pinned audit identifies only the public community card
`https://huggingface.co/litert-community/CMGAN-LiteRT`. It records a
source-reported re-authored FP16 Android/edge model with vendor-reported device
timing and output correlations, a failed Galaxy NPU run, and an explicit warning
that this is not the official CMGAN checkpoint or evaluation. It records no
immutable revision, model filename, byte count, SHA-256, LiteRT version,
delegate, tensor geometry, conversion script or numeric output.

Consequently:

- no port source, converted model, weight file, LiteRT runtime, delegate,
  adapter or pinned revision is staged at `data/checkouts/CMGAN-LiteRT`,
  `data/models/cmgan-litert`, `data/envs/litert` or `adapters/cmgan-litert`;
- no immutable source/model/runtime hash, flatbuffer identity, tensor layout,
  sample rate, hop, window, precision, content delay, lookahead or numeric
  output exists for the candidate itself;
- no upstream LICENSE, model card terms, weight terms, training-data statement,
  conversion/derivative review, attribution bundle, corpus rights or product-use
  review is staged; no license identity is asserted;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream. No LiteRT
  runtime, Android target, delegate, NPU behavior or provider geometry is
  admitted;
- no official CMGAN reference backend or local/reference-to-LiteRT parity run
  exists, so third-party conversion parity is unverified and unmeasured;
- no real speech, rights-cleared cohort, clean reference, baseline run, STOI,
  MOS, listening result or device timing exists;
- no target-device pacing, memory, availability, independent review, provider
  intake or release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CMGAN-LITERT-COMMUNITY-PORT`, `6967a728b5c4048fb01ed4522a76a6906fbcffe2` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/tensor/delay asserted |
| Surrogate | synthetic 16 kHz mono clean/noise fixture, adaptive frame-energy suppressor |
| Added content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded deterministic noise-floor tracker plus
square-root subtraction gain and a per-frame gain ramp. It is **not CMGAN**, is
not learned, uses no weights, STFT, FP16 or LiteRT, and cannot qualify the
candidate.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json -> acceptance_profile` and `enhancement_profile`, and each item is
checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity/noisy control | synthetic only | Exact passthrough on the same frozen synthetic fixture |
| Task-matched baseline | blocked | Official CMGAN and FastEnhancer Small named only; neither run |
| Paired SI-SDR | synthetic only | Paired SI-SDR on generated clean references, integer millidB |
| STOI | blocked | No permitted STOI scorer executed; no intelligibility claim |
| Clean-speech preservation | synthetic only | Active-region level change, SI-SDR and a labeled envelope proxy |
| Peaks and invalid outputs | synthetic only | Peak bound, finite-output count, nonfinite input rejection |
| Unpaired predictive screen | blocked | No unpaired speech or DNSMOS-style predictor run |
| Listening | blocked | No authorized listening test |
| Alignment | blocked | Candidate delay/alignment undocumented; surrogate declares 0 |
| State, memory, timing | blocked/unmeasured | No LiteRT runtime, device, RTF, memory or availability trace |
| Held-out qualification | blocked | No rights-cleared task-matched held-out cohort |

Every synthetic observation is `qualifies=false`. Synthetic exactness means only
that the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Fixture length: 8,000 samples (0.5 s), four contiguous segments:
  `speech_a` 0–2400, `pause` 2400–3200, `speech_b` 3200–6400,
  `tail_silence` 6400–8000.
- Clean: deterministic three-tone speech-like source with a fixed 16-step
  syllabic envelope and integer scale 6000. Pause and tail are exact zero.
- Noise: deterministic integer LCG at amplitude 1600, independent seeds for
  clean and noise.
- Surrogate: per-frame RMS, fast-down/slow-up noise-floor tracker, square-root
  subtraction gain clamped to `[0.15, 1.0]`, linear per-frame gain ramp.
- Active metric region: `[0,6400)`; overall metrics include pause/tail.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity/noisy SI-SDR / SNR | 937 / 926 mdB |
| Surrogate SI-SDR / SNR | 3544 / 4953 mdB |
| Δ SI-SDR / Δ SNR | +2607 / +4027 mdB |
| Active surrogate SI-SDR / SNR | 3675 / 5065 mdB |
| Active level change | −513 mdB |
| Envelope-correlation proxy | 954 / 1000 |
| Max peak, identity / surrogate | 209 / 186 milli |
| Nonfinite output samples | 0 |

The positive deltas are an artifact of an exact synthetic stationary noise floor,
not evidence of real-world denoising, intelligibility or deployment quality.
The envelope-correlation proxy is not STOI, MOS or listening.

## Adverse, missing and invalid handling

`report.json` records 46 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame,
`int16`, clock drift, linear resampling, nonzero algorithmic latency, FP16
surrogate precision, boolean rate, missing frame, epoch mismatch, wrong count,
invalid valid-count, nonfinite input, nonzero padding, string and boolean
samples, wrong input position, reset epoch 0/−1/non-increasing, negative reset
position, missing/relative/bad-hash/bad-revision/wrong-rate/wrong-channel/
wrong-frame/wrong-format/wrong-precision/unknown-delegate/zero-byte/extra-field
caller manifests, and malformed fixture length/segment/gap/amplitude
specifications. Missing real audio, model, runtime, target, weights and labels
are `blocked`, never passes.

The caller asset contract validates identity only. It never reads, loads,
imports or executes a source tree, model flatbuffer or runtime. A hash-matched
placeholder is never accepted as the pinned candidate artifact.

## Streaming, reset and determinism

The probe is frame-clocked: arbitrary caller chunks
`160/320/480/800/640/160` reproduce the full-block output exactly
(`all_match=true`, `accepted_samples=8000`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0, negative and non-increasing epochs are rejected with
the state digest unchanged. A 137-sample final partial frame advances state by
exactly 137 samples, emits 160 outputs and leaves the tail invalid samples zero.
`run.py` builds the report, contract and manifest three times and refuses to
write unless every payload is byte-identical; `verify.py` repeats the build in
three cold-start interpreter processes.

## Separation from sibling evidence

No merged CMGAN or LiteRT evidence package exists at this base revision. The
merged `metricgan-speechbrain-voicebank` package is a separate enhancement
proposal, and `cagcrn-joint-aec-and-ns` is a separate Room/AEC proposal. Their
README, report and contract files are pinned only as read-only boundary
references. This package does not import, pool, score or reuse their source,
fixtures, metrics or results.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen synthetic fixture, surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, cold-start reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/agent-denoise-trials/REPORT.md` | `c00e26847c119928f068cb5da00ba88106a2d977b67bf8b325ec27093eca8f4e` |
| `source:research/voice-enhancement-20261101/agent-denoise/REPORT.md` | `eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
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
| `sdk:docs/task-evidence/metricgan-speechbrain-voicebank/README.md` | `0ce5593cda4ed6412d755ecd013c4ef65f3e1c50c4f264a1abb4782b57990f22` |
| `sdk:docs/task-evidence/metricgan-speechbrain-voicebank/report.json` | `8f04d6f06cea71f6497277131d3b4adcb7b5381c5fc25b4fa646fe91476935e2` |
| `sdk:docs/task-evidence/metricgan-speechbrain-voicebank/contract.json` | `f7cab2bb7aa92a43f7efb2c009ecc6f8b9b6cadf690f09cb5bb362186d720d00` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/README.md` | `aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/report.json` | `697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CMGAN-LITERT-COMMUNITY-PORT/docs/task-evidence/cmgan-litert-community-port
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --all
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CMGAN-LITERT-COMMUNITY-PORT diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `verify.py`, which builds each payload in three cold-start interpreter
processes and compares the bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned CMGAN-LiteRT card/source, converted model and LiteRT
   runtime with immutable revision, license identity and artifact hashes.
2. `RG-02` isolated hash-pinned LiteRT runtime admission, reproducible
   conversion/build, verified model identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data, conversion/derivative and corpus rights
   plus attribution, notices, redistribution, product-use and output-use review.
4. `RG-04` exact candidate I/O geometry: rate, channels, frame, STFT
   hop/window, normalization, tensor layout, precision, padding, content delay
   and lookahead from pinned metadata.
5. `RG-05` official-CMGAN reference backend versus LiteRT numeric parity on
   identical frozen inputs, with an exact tolerance and CPU plus target runs.
6. `RG-06` enhancement qualification on a rights-cleared task-matched held-out
   cohort with identity/noisy control, paired SI-SDR and STOI where permitted,
   clean preservation, peaks and invalid outputs.
7. `RG-07` named Android target pacing, delegate timing/memory, availability,
   reset/state behavior, documented NPU failure mode and listening/predictive
   controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed CMGAN-LiteRT revision, converted
model and LiteRT runtime with immutable hashes and a named Android target, clear
code/weight/training-data/conversion/corpus rights, document exact I/O geometry
and delay, reproduce numeric parity against an official CMGAN reference
backend, qualify enhancement and preservation on a rights-cleared task-matched
held-out cohort, measure target timing and listening, and complete opt-in
provider intake. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-CMGAN-LITERT-COMMUNITY-PORT]`, stable-field digest); the mutable
full `plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source.
No provider, descriptor, registry, installed default, shared build or CI is
changed.
