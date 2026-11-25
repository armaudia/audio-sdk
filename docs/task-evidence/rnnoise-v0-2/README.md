<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RNNOISE-V0-2 — RNNoise v0.2 caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`RNNoise v0.2` (`component_id=rnnoise-v0-2`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package models the exact RNNoise v0.2 runtime boundary as a
**caller-supplied-asset reference** at 48 kHz mono with 480-sample (10 ms)
frames. Because the compiled runtime, a caller asset manifest, and separate
model/archive rights are unavailable, it executes a **stdlib/numpy synthetic
surrogate** and records a strict readiness conclusion. It is **not RNNoise
source**, does not load a checkpoint or weights, does not download or vendor
anything, does not read audio, does not invoke a native runtime, does not
measure a device clock, does not conduct listening, does not benchmark the SDK
and makes no release or quality claim. Only this task-local directory is added.

## Exact blocker

The exact upstream identity is pinned: Xiph `xiph/rnnoise` at commit
`70f1d256acd4b34a572f999a05c87bf00b67730d`, BSD-3-Clause `COPYING`, the
`model_version` file, the model archive
`rnnoise_data-0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37.tar.gz`
and the relevant source files, all by SHA-256 from the external research
checkout. The compiled runtime expected at
`data/envs/rnnoise/librnnoise.dylib` is **absent**, and no caller asset
manifest is present in the SDK worktree. The model archive is present only in
the external checkout and is **not** copied. The BSD-3-Clause source license
does **not** establish separate model/archive terms, product-use or
redistribution rights, or training-data provenance; no legal review exists.
Nothing was copied, vendored, built, downloaded or redistributed.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers`, `report.json:exact_blockers` and
`readiness.json:exact_blocker`. Every release gate remains `blocked`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI or installed behavior.
- The task-local caller asset contract requires exactly `library_path`,
  `library_sha256`, `model_archive_path`, `model_archive_sha256`,
  `source_commit`, `sample_rate_hz`, `channels` and `frame_samples`; it pins
  48 kHz, mono, 480 samples and the Xiph commit.
- A manifest is accepted only when both files are absolute, present and
  SHA-256-matched and the geometry/commit match. Validation never loads or
  executes the library. Missing, absent, hash-mismatched or wrong-geometry
  manifests fail closed before processing.
- The surrogate resamples 16 kHz → 48 kHz, processes 480-sample frames, models
  a 480-sample algorithmic delay and compensates it before returning to
  16 kHz. The measured impulse is at 4160 samples without compensation and at
  4000 samples with compensation (content lag 0 samples).
- Availability is a **modeled** source-derived clock
  (`fixture-monotonic-not-device`), not a wall-clock or device measurement.

## Enhancement profile application

- Identity/noisy control: the unprocessed synthetic input is the baseline.
- Candidate boundary: the deterministic frame-RMS gate surrogate runs on the
  same frozen stimuli. It is **not** RNNoise and has no neural network,
  weights, checkpoint or model archive.
- Paired SI-SDR and STOI use synthetic clean references. The clean voiced
  surrogate has three voiced segments and deterministic pauses; noise is
  band-limited deterministic LCG noise.
- Five conditions are scored: `clean_only`, `noisy_snr10`, `noisy_snr0`,
  `noise_only` and `silence`. Noise-only and silence have a zero reference and
  are explicitly invalid, never silently scored.
- Clean preservation, peaks, invalid/missing/nonfinite outputs, alignment,
  state, caller-asset validation and availability are recorded separately.
- No established task-matched RNNoise baseline is reproduced: the pinned
  source-reported pilot values are provenance only and are never pooled with
  the surrogate metrics.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, boundary surrogate, metrics, canonical report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | 32 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `requirements.lock` | Pinned NumPy/SciPy/pystoi versions for deterministic metrics. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all external and task-local files. |

## Pinned source and asset digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
SDK paths are relative to this worktree. All are machine-checked in
`SOURCES.sha256`.

| Source/asset | SHA-256 | Use |
| --- | --- | --- |
| `data/checkouts/RNNoise/COPYING` | `45d37ca1cdb278c088e1aa85e0e65ca3a534ed86a28dcc96ca16810248a61d35` | BSD-3-Clause upstream license. |
| `data/checkouts/RNNoise/model_version` | `07bebd6ed8f6f97095cc9382122c7113c6e9ad0e22773cca33679c3df1ef901a` | Names the model archive. |
| `data/checkouts/RNNoise/rnnoise_data-0a8755...tar.gz` | `0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37` | External model archive; not copied or loaded. |
| `data/checkouts/RNNoise/src/denoise.c` | `f12ac3cc97d798cdfd7c7bd4366a08a72c5516c382056c891b61a61cb17eb031` | Pinned source context. |
| `data/checkouts/RNNoise/src/rnn.c` | `c40bbe40082448005873fe970d8963870ab2c9993b7c38d6939ca48f4f31a7bd` | Pinned source context. |
| `data/checkouts/RNNoise/src/nnet.c` | `3a2c1dc09ad7e9dfe3cf32cfb94694935dc462488da8f513d1f308db39f7c087` | Pinned source context. |
| `scripts/build_rnnoise.sh` | `d39acd38a371f73cbe59d2b08584f87c885f6dd99025289ef81ddec1ec31eacd` | Build recipe; not executed here. |
| `adapters/rnnoise/adapter.json` | `6c7ca68df9fe24bf67f249197777674e4bc8f6527bccbb2fcced4637e00abb44` | Research-workspace offline CLN-01 waveform adapter; not in the SDK worktree, not executed, registered or changed. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | RNNoise v0.2 evaluated CLN row. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | 48 kHz mono, 10 ms frames; weight terms unresolved. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset ledger; runtime hash recorded but file absent. |
| `research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Source-reported pilot and weight-rights caveat. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | DNS pilot ΔSI-SDR/ΔSTOI/RTF and offline-adapter caveat. |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported 30-pair pilot. |
| `research/voice-enhancement-20261101/agent-denoise/REPORT.md` | `eb1fef2ab460c11fe382d1a978ef762f91a1c1e93725e7ac443b9b5c05098b07` | Source-reported pilot details. |

Boundary pins also cover `CONTRACTS.md`, both public v0 headers, `CMakeLists.txt`,
`REUSE.toml` and `scripts/ci.py`; all are unchanged and machine-checked.

## Reproduction

All outputs are task-local. `SOURCE_ROOT` is needed only by the verifier and
tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-RNNOISE-V0-2
TASK=$WT/docs/task-evidence/rnnoise-v0-2
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/rnnoise-v0-2-ci
python3 -m reuse lint
git diff --check
```

Local results: `run.py` regenerated the report; the package tests passed
**32/32**; `verify.py` passed; `python3 -m reuse lint` passed; `git diff
--check` was clean. The pinned `scripts/ci.py` gate passed: repository
unittest **52/52**, API CTest **1/1**, native CTest **11/11**, external CTest
**14/14**, fixture off/on **1/1** each, installed Python wheel **5/5**, and
both release archive gates refused the missing-Speex catalog as expected.

## Results (synthetic boundary surrogate only)

Paired deltas are surrogate minus noisy identity. Positive SI-SDR delta is
better; STOI delta can be negative and is reported as an adverse result. These
numbers are **not** RNNoise results and are **not** a quality pass.

| Condition | SI-SDR identity → surrogate (Δ) | STOI identity → surrogate (Δ) | RMS gain | Peak | Invalid/clipped |
| --- | --- | --- | --- | --- | --- |
| `clean_only` | undefined (`zero_error_identity_exact`) → 63.819335 | 1.000000 → 1.000000 (0.000000) | 1.000541 | 0.500630 | 0 |
| `noisy_snr10` | 10.008793 → 11.206457 (+1.197664) | 0.707915 → 0.732485 (+0.024570) | 0.975238 | 0.649650 | 0 |
| `noisy_snr0` | −0.005345 → −0.041223 (−0.035878) | 0.492285 → 0.492283 (−0.000002) | 0.150393 | 0.168914 | 0 (input had 12 clipped samples) |
| `noise_only` | zero reference (invalid) | zero reference (invalid) | 0.150700 | 0.038912 | 0 |
| `silence` | zero reference (invalid) | zero reference (invalid) | undefined | 0.000000 | 0 |

The scalar gate is deliberately simple: SI-SDR is scale-invariant, so the
`noisy_snr0` regression is a boundary/resampling observation, not evidence that
the surrogate is a usable denoiser. The clean-only path is effectively identity.
Every valid output is finite, with no sample at or above 1.0. Noise-only and
silence are invalid references and are never scored as speech.

Caller-asset and frame controls all fail closed: missing manifest, absent file,
hash mismatch, wrong source commit, sample rate, channels or frame size, short
or two-dimensional input, NaN input, truncated output and missing reference.
The valid-manifest control validates hashes and geometry but reports
`loaded=false` and `executed=false`. Separate instances are uncoupled, reset is
bit-identical, epoch 2 propagates, and different stimuli differ.

## Gates and reopen conditions

The package records nine blocked gates: caller asset present/verified, model
and runtime rights, exact runtime reproduction, native streaming boundary,
real cohort, independent listening, target-runtime timing/memory, opt-in
adapter intake, and public default selection. `readiness.json` is the concise
strict conclusion; `report.json:gates` and `contract.json:gates` carry the
exact reopen condition for each.

Reopen only when a caller supplies the pinned 48 kHz library and model archive
with matching hashes/commit, separate model/archive and runtime rights are
cleared, the exact runtime is reproduced with an approved reference vector, the
native streaming boundary is verified, a rights-cleared real cohort is scored,
independent listening exists, target timing/memory is measured, opt-in intake
is complete and a public default decision is recorded. Until then the candidate
stays DEFER, incomplete and not qualified.

## Separation from RNNoise speech probability

`docs/task-evidence/rnnoise-speech-probability/` is a separate
Analysis-profile task about a synthetic `speech_probability` tap. This package
is Enhancement-profile waveform evidence and does not import, reuse, pool or
reinterpret that task's events, metrics or adapter.
