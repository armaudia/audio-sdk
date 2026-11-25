<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-EARSHOT-1-2-2 — Earshot 1.2.2 caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Earshot 1.2.2` (`component_id=earshot-1-2-2`). The acceptance profile is
**Analysis**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package models the exact Earshot 1.2.2 VAD/processing boundary as a
**caller-supplied-asset reference** at 16 kHz mono with 256-sample (16 ms)
frames, `float32` input and decision threshold 0.5. Because the pinned wheel,
its embedded weights and an isolated runtime environment are unavailable, it
executes a **stdlib-only deterministic synthetic surrogate** and records a
strict readiness conclusion. It is **not Earshot source**, does not import or
load a wheel or weights, does not download or vendor anything, does not read
audio, does not invoke a native runtime, does not measure a device clock, does
not conduct listening, does not benchmark the SDK and makes no release or
quality claim. Only this task-local directory is added.

## Exact blocker

The exact upstream identity is pinned: pykeio `earshot` 1.2.2, provenance commit
`c400f15bd232dda30a297eec90235bd09066cab7`, `MIT OR Apache-2.0`, PyPI release
2026-08-19, source-archive SHA-256
`a2aad72917334d2b9e7385b73dc837bd30244714ccf27d45fbfcc0e038cfcaeb` and macOS
arm64 wheel SHA-256
`bf696faad73a996c40bea8115622a5dcbc9c6da01498885bfd9eae8be1a11ecd`. The wheel
expected at
`data/wheels/vad-candidates/earshot-1.2.2-cp38-abi3-macosx_11_0_arm64.whl` is
**absent**, and the isolated environment expected at
`data/envs/earshot-vad-1.2.2` does **not** exist. No network access, install or
wheel import is permitted here, so the exact runtime cannot be loaded or
reproduced. The wheel metadata declares `MIT OR Apache-2.0`, but no standalone
license file is bundled, and embedded-weight/training-data provenance plus
redistribution, product-use and legal review remain unresolved. Nothing was
copied, vendored, built, downloaded or redistributed.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers`, `report.json:exact_blockers` and
`readiness.json:exact_blocker`. Every release gate remains `blocked`.

## Boundary model

- The pinned research adapter declares 16 kHz mono `float32`, exactly
  **256 samples / 16 ms** per stateful `Detector.predict_f32` call, score
  threshold `0.5`, `reset()` per recording, and the same sequential path for
  offline and streaming modes. A final partial frame is zero-padded for
  inference and its decision interval is clipped to real samples.
- Installed SDK v0 remains 16 kHz mono `f32`, **160 samples**. The cadence
  divergence is recorded; no numeric parity with the real runtime is claimed
  and no installed geometry, default, ABI, contract, registry, descriptor,
  shared build or CI file changes.
- The task-local caller asset contract requires exactly `wheel_path`,
  `wheel_sha256`, `source_commit`, `sample_rate_hz`, `channels`,
  `frame_samples`, `threshold` and `input_format`; it pins 16 kHz, mono,
  256 samples, 0.5 and `float32`. A manifest is accepted only when the wheel
  path is absolute, present and SHA-256-matched, and geometry/commit/threshold
  match. Validation never imports or executes the wheel. Missing, relative,
  hash-mismatched, wrong-geometry, wrong-threshold or extra-field manifests
  fail closed before processing.
- Earshot embeds its weights in the wheel, so there is **no separate model
  archive**. The wheel is the caller asset; `weights` is recorded as
  `embedded-in-wheel` and never loaded.
- The surrogate is a deterministic per-frame RMS and zero-crossing logistic
  gate with threshold 0.5, no smoothing, no hangover and no postprocessing. It
  is **not Earshot**, has no neural network, checkpoint or weights, and its
  probabilities are uncalibrated synthetic observations.
- Availability is a **modeled** source-derived clock
  (`earshot-1-2-2-fixture-monotonic-v0`), not a wall-clock or device
  measurement.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Timestamped probabilities | 125 exact 256-sample interval records, Brier and log loss reported |
| Event boundaries | 3 truth runs matched by overlap; onset/offset delay in samples and ms |
| Detections | TP/FN/FP/TN by sample, overall and per frozen stratum |
| Quiet and active speech | `quiet-a`, `quiet-b`, `active-a` strata |
| Idle noise | `idle-a/b/c/d` and `noise-burst` strata |
| Known positives/negatives | 15360 speech samples, 13312 nonspeech samples |
| Onset/offset delay | `quiet-a` +1536/+0 samples; `active-a` 0/0; `quiet-b` missed |
| Stratified FN/FP | `quiet-a` FN 1536; `quiet-b` FN 3328; `noise-burst` FP 1280 |
| Validity separate from nonspeech | 3328 unknown samples excluded; invalid never scored as negative |
| Independent state | Separate sessions, reset identity, epoch propagation and fresh determinism |
| Exact source intervals | Frame and probability intervals partition `[0,32000)` exactly |
| Availability | Strictly increasing modeled clock with the pinned formula |
| Dropped/stale events | Sequences 2, 5 and 17 dropped; stale/missing/nonfinite cases rejected |
| Cross-hop | `[150,330)` projects to `[(0,106),(1,74)]`; truth run spans 16 exact hops |

Also verified: fail-closed caller-asset, frame, config and event-bus controls;
offline/streaming parity with 160/480/800-sample chunk buffering; a final
128-sample tail; and the always-speech / always-nonspeech diagnostic baselines.
No missing, stale, unrun or blocked result is promoted to a pass or used to
qualify the candidate.

## Method

1. `fixture.py` synthesises 32000 samples (2 s) from integer
   arithmetic: a fixed 64-entry waveform table, a deterministic LCG noise
   source and a frozen segment table. Samples are quantised to int16 and
   exposed as `float32 / 32768`. Every segment boundary is a multiple of 256
   samples, so each frame has one unambiguous source label.
2. Nine frozen truth segments cover quiet speech, active speech, a
   below-threshold quiet run, idle noise, a loud noise burst and an explicit
   unknown tail. The unknown span is admitted to the audit but excluded from
   every denominator.
3. `reference.Session` drives one 256-sample frame at a time. Each accepted
   frame emits one probability record with `start_sample`, `end_sample`,
   `probability`, `decision`, `validity`, epoch, sequence and availability.
   Known events use
   `available_ns = origin_ns + end_sample × 62500 + 1,000,000` on the modeled
   fixture clock; unknown events carry no availability and no decision.
4. Contiguous `decision=true` frames form advisory speech events with no
   hangover. A run closes at the first inactive frame and becomes available at
   that frame's end; an unterminated run closes on drain.
5. `scorer.py` scores probabilities (Brier/log loss, five calibration bins),
   sample-weighted confusion, per-stratum FN/FP and overlap-matched boundaries.
   Unknown samples are excluded; invalid records are rejected before scoring.
6. `run.py` builds the report three times and requires byte-identical payloads
   before writing `report.json` and `report.json.sha256`.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `fixture.py` | Deterministic stimuli, frozen truth segments, source/boundary/asset pins. |
| `scorer.py` | Analysis-profile probabilities, confusion, calibration and boundaries. |
| `reference.py` | Session, surrogate, controls, canonical report/contract/readiness builders, strict parsers. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Analysis report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | 44 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verification. |
| `requirements.lock` | Pinned CPython 3.12.16; standard library only, no third-party runtime. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all source and task-local files. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:adapters/earshot-vad/adapter.json` | `f3d391cf015cc897be20b19fab563bdef4f63310f4aceaad4d1c0bab0db3d091` |
| `source:adapters/earshot-vad/run.py` | `541e08619480b63c2a77bd7fd45f454ee8828a90737a65af707a4c017a6fd8a8` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:reports/vad-research/20261028-synthesis-v6.md` | `d8bc5d7481ffc40ee7c16caba6b570255e24aef2a99e7f03b0293721c37d8df3` |
| `source:reports/vad-research/attempt-earshot-20261028-01/findings.md` | `cefe94dea241e7ce98071f0be336e463cbf2b9f5fa90785b0e4c4b5439f14a8f` |
| `source:reports/vad-research/chaining-evaluation-status.json` | `3b66ba722c06673fdcc698e3f10e716e13aae74bc2f2c0ebd046316ed6fd068c` |
| `source:reports/vad-research/chaining-evaluation.md` | `f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234` |
| `source:research/plans/F02/vad_sources.md` | `374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The digest below is the file digest, the canonical digest
and the sidecar digest. `SOURCES.sha256` pins every artifact and this README;
it does not pin itself.

<!-- digest-table: artifacts -->
| Key | SHA-256 |
| --- | --- |
| `LICENSES.md` | `8f07e1375efaa47a9aafed39550310b8053c326d219775c0c1859aadc3c6148f` |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `adapter.json` | `49967a5d47a2dab0c06fa1437012a23d4a4a9556a01d6b7c7a740393e7c6fff9` |
| `adapter.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `contract.json` | `debcb9edcc7b53ccf77e113aa90799c104fa31c5c081c66afec98d031214c3ab` |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `fixture.py` | `9ef1013c926b71a12b12000bb128269757de08a9f26e456296ef7a9b162c7485` |
| `readiness.json` | `d396929aa01695c134bd3b68b66888855e2db6d9574d3a822382a282193d070d` |
| `readiness.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `reference.py` | `26be3925de29e1894041b976a623ef14c7b55cca6559d696d41d2143042150f9` |
| `report.json` | `b0a8585df49bb0eaa49d175ba7113c9ea5281ca265a02d97d62f42cb6ff1815b` |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `report.json.sha256` | `3890e6fc71d036c60d7ee04557bd6ffd033f0a2d1c5de074b68bc153c59e88e0` |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `requirements.lock` | `b2b1cd05c7cdec1a178b2da8f24da7df1fbbd33523d7a1ba5918c407e9a6a53e` |
| `requirements.lock.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `run.py` | `b5f895b572ea5c28833d4e2026a10f5569dacd19901218f33e5c11618f45c377` |
| `scorer.py` | `18ed157621032d9c48bc2f7d1dc53835c0fb6f611ae96fabd92db9cf6a64e321` |
| `test_reference.py` | `8ec05384cc59c7030c564f508d602e988446abd21f9e3b86de12de7d2867a451` |
| `verify.py` | `07497fb1f4fa8706338361974554a55c9ee71366fbf9695f0ee66b1dcef66f0b` |
<!-- digest-table: end -->

## External asset identity (expected, absent)

These values are recorded identity only. The wheel path is checked for absence:
if the file appears, this evidence package is stale and must reopen. Nothing in
this table is present, downloaded, copied, imported, loaded or executed.

<!-- digest-table: external-absent -->
| Key | SHA-256 |
| --- | --- |
| `asset:source_archive` | `a2aad72917334d2b9e7385b73dc837bd30244714ccf27d45fbfcc0e038cfcaeb` |
| `asset:wheel` | `bf696faad73a996c40bea8115622a5dcbc9c6da01498885bfd9eae8be1a11ecd` |
<!-- digest-table: end -->

## Reproduction

All outputs are task-local. Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-EARSHOT-1-2-2
TASK=$WT/docs/task-evidence/earshot-1-2-2
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/earshot-1-2-2-ci
python3 -m reuse lint
git diff --check
```

Local results: `run.py` regenerated the report; the package tests passed
**44/44**; `verify.py` printed `PASS`; `python3 -m
reuse lint` passed; `git diff --check` was clean. The pinned `scripts/ci.py` gate passed: repository unittest 52/52, API CTest 1/1, native CTest 11/11, external CTest 14/14, fixture off/on 1/1 each, installed Python wheel 5/5, and both release archive gates refused the missing-Speex catalog as expected.

## Results (synthetic boundary surrogate only)

The surrogate is a conformance fixture, not Earshot and not a quality result.
Overall sample-weighted detections on 28672 known samples
(15360 speech, 13312 nonspeech) with
3328 unknown samples excluded:

| Metric | Exact value |
| --- | ---: |
| TP / FN / FP / TN (samples) | 10496 / 4864 / 1280 / 12032 |
| Speech miss rate (FN / 15360) | 0.316666666667 |
| False-alarm rate (FP / 13312) | 0.096153846154 |
| Brier score | 0.148916190266 |
| Log loss | 0.420839669414 |
| Mean probability (known) | 0.395308947297 |

Stratified detections: `active-a` TP 7936 / FN 0; `quiet-a` TP 2560 / FN
1536; `quiet-b` TP 0 / FN 3328; `noise-burst` FP
1280 / TN 1280; `idle-a/b/c/d` TN 10752 with no false alarms. The
unknown tail contributes to no denominator.

Boundaries: `quiet-a` truth `[2048,6144)` is matched by `[3584,6144)` (onset
+1536 samples / +96 ms, offset 0);
`active-a` `[8192,16128)` is matched exactly (0/0); `quiet-b` `[18688,22016)`
is missed. One false event `[17408,18688)` comes from the synthetic noise
burst. Positive onset means a late start; negative offset would mean an early
stop. These are source-coordinate effects, not device or availability timing.

Diagnostic baselines expose metric behavior: always-speech gives FN 0 / FP
13312 and always-nonspeech gives FN 15360 / FP 0. Neither is a useful product
recommendation.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** valid wheel manifest validates hash and geometry but
  reports `loaded=false`, `executed=false`, `imported=false`. Missing,
  absent-file, relative-path, hash-mismatched, wrong-commit, 48 kHz, stereo,
  512-sample, threshold-0.6, `int16` and extra-field manifests are rejected.
- **Frame adverse:** NaN, Inf, 128-sample nonfinal, 257-sample, empty and
  boolean-bearing frames are rejected with the state digest unchanged. Final
  `valid_samples` of 0 and 257 are rejected; a valid final 128-sample frame is
  accepted with end coordinate 384, 128 padded inference samples and exact
  availability.
- **Config adverse:** 48 kHz, 2 channels, `s16`, 320-sample frames,
  threshold 0.6, `real_runtime=true`, wheel-used and empty session id are
  rejected.
- **Event bus:** sequences 2, 5 and 17 are explicitly dropped, producing gaps
  `[[2,2],[5,5],[17,17]]` and zero fabricated events. Stale epoch, missing and
  nonfinite probability, out-of-range probability, wrong clock, stale
  availability, wrong interval, duplicate sequence, nonfinite frame and unknown
  validity token cases are all rejected without state mutation.
- **Independent state:** two sessions (epochs 3 and 8) produce distinct event
  digests; resetting one to epoch 4 matches a fresh session and leaves the
  other unchanged; an epoch-3 event cannot revive analysis after reset.
- **Offline/streaming:** arbitrary 160/480/800-sample chunks are buffered into
  exact 256-sample frames; offline, streaming and fresh-session event and
  speech-event digests are identical.
- **Intervals and availability:** frame and probability intervals form the
  exact partition `[0,32000)`; known availability is strictly increasing and
  follows the pinned formula; unknown events have no availability.
- **Cross-hop:** `[150,330)` projects to `[(0,106),(1,74)]` with total overlap
  180; the truth run `[2048,6144)` spans exactly 16 hops.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Gates and reopen conditions

The package records nine blocked gates: caller wheel present/verified, wheel and
embedded-weight rights, exact runtime reproduction, streaming boundary
conformance, rights-cleared label-complete cohort, target-runtime timing/memory,
opt-in adapter intake, descriptor/registry review, and public default selection.
`readiness.json` is the concise strict conclusion; `report.json:gates` and
`contract.json:gates` carry the exact reopen condition for each.

Reopen only when a caller supplies the pinned 16 kHz / 256-sample wheel with
matching SHA-256 and provenance commit, wheel/embedded-weight/training-data and
redistribution/product-use rights are cleared, the exact runtime is reproduced
with an approved reference posterior vector, native streaming plus partial-tail
and reset behavior are verified, a rights-cleared label-complete cohort is
scored, target timing/memory is measured, opt-in intake and descriptor review
are complete, and a public default decision is recorded. Until then the
candidate stays DEFER, incomplete and not qualified.

## Separation from sibling evidence

`docs/task-evidence/fast-vad-0-2-1/`, `webrtc-vad/`, `survey-det-01/` and
`rnnoise-v0-2/` are separate tasks with their own fixtures, scorers, cadences
and dispositions. This package does not import, reuse, pool or reinterpret
their events, metrics, adapters or reports. The research adapter at
`adapters/earshot-vad/` is pinned provenance only; it is not present in the SDK
worktree, not installed, imported or executed, and not changed.
