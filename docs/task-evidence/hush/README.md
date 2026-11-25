<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-HUSH — Hush caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Hush` (`component_id=hush`, `SPK-01`). The acceptance profile is **Spatial**,
assigned by `plan/INVENTORY.json` (`verification_profile: spatial`) and defined
in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, `spatial_acceptance_cleared=false`.
Missing evidence never qualifies a candidate.

This package models the exact Hush enhancement boundary as a
**caller-supplied-asset reference** at 16 kHz mono with 160-sample (10 ms)
frames, a caller-set `atten_limit_db` and the upstream-reported ~20 ms
algorithmic latency. Because the compiled runtime, a caller asset manifest and
artifact-specific rights are unavailable, it executes a **stdlib/numpy
synthetic surrogate** and records a strict readiness conclusion. It is **not
Hush source**, does not load the ONNX bundle, does not download or vendor
anything, does not read audio, does not invoke a native runtime, does not
measure a device clock, does not conduct listening, does not benchmark the SDK
and makes no release, spatial or quality claim. Only this task-local directory
is added.

## Exact blocker

The exact upstream identity is pinned: `pulp-vision/Hush` at commit
`9f6414e91461a8f4bdf9840c0cdcdcb7da986339`, Apache-2.0 `LICENSE`, the
deployment C header, the wrapper source, the ONNX bundle
`deployment/models/advanced_dfnet16k_model_best_onnx.tar.gz` and the three
platform runtime libraries, all by SHA-256 from the external research checkout.
No caller asset manifest or copy exists in the SDK worktree. The artifacts were
obtained upstream through a **placeholder release URL** and are not published
with a verifiable digest; the declared model-card revision exposes no weights.
No legal review, artifact-specific redistribution/product-use grant or
training-data provenance exists. Nothing was copied, vendored, built,
downloaded or redistributed.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers`, `report.json:exact_blockers` and
`readiness.json:exact_blocker`. Every release gate remains `blocked`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI or installed behavior.
- The task-local caller asset contract requires exactly `library_path`,
  `library_sha256`, `model_bundle_path`, `model_bundle_sha256`,
  `source_commit`, `sample_rate_hz`, `channels`, `frame_samples` and
  `atten_limit_db`; it pins 16 kHz, mono, 160 samples, `atten_limit_db=100` and
  the Hush commit.
- A manifest is accepted only when both files are absolute, present and
  SHA-256-matched and the geometry/commit/attenuation fields match. Validation
  never loads or executes the library. Missing, absent, hash-mismatched,
  relative-path, extra-field or wrong-geometry manifests fail closed before
  processing.
- The surrogate runs natively at 16 kHz, models a 160-sample (10 ms) frame
  delay and compensates it before returning the waveform. The measured impulse
  is at 4160 samples without compensation and at 4000 samples with
  compensation (content lag 0 samples). The upstream ~20 ms algorithmic
  latency is recorded separately and is not measured.
- `atten_limit_db` sets the surrogate attenuation floor
  (`max(0.15, 10^(-atten/20))`); `0 dB` is bit-exact identity, `100 dB` keeps
  the 0.15 floor. This models the C-API parameter, not Hush behavior.
- Availability is a **modeled** source-derived clock
  (`fixture-monotonic-not-device`), not a wall-clock or device measurement.

## Spatial profile application

- Geometry, layout, timestamp calibration, source/target/reference conditions
  and permissions are recorded in `report.json:spatial_geometry` and
  `report.json:timestamp_calibration`.
- Identity/noisy control: the unprocessed mixture is the baseline at each
  target-to-interferer ratio.
- Candidate boundary: the deterministic frame-gate surrogate runs on the same
  frozen stimuli. It is **not** Hush, has no ONNX graph, DeepFilterNet blocks,
  weights or checkpoint, and accepts no enrollment prompt.
- Paired SI-SDR and STOI use exact synthetic clean-target references. The clean
  voiced target (f0 125 Hz) and the disjoint voiced interferer (f0 205 Hz) are
  deterministic; mixtures are scored at +12/+18/+24 dB SIR under a shared
  0.95 peak guard.
- Six conditions are scored: `target_only`, `mixture_sir12`, `mixture_sir18`,
  `mixture_sir24`, `interferer_only` and `silence`. Interferer-only and silence
  have a zero reference and are explicitly invalid, never silently scored.
- Leakage and target damage are reported separately per stratum:
  target retention, interferer leakage retention, least-squares
  target-to-interferer projection-ratio gain and target projection SNR delta.
- Clean preservation, peaks, invalid/missing/nonfinite outputs, alignment,
  state, caller-asset validation, timestamp calibration and availability are
  recorded separately.
- Channel loss, array geometry, room/reference change, held-out speaker/room
  labels and enrollment-conditioned extraction are explicitly **absent**; no
  localization, extraction or spatial-acceptance result is claimed.
- No established task-matched Hush baseline is reproduced: the pinned
  source-reported pilot values are provenance only and are never pooled with
  the surrogate metrics.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, boundary surrogate, spatial metrics, canonical report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Spatial report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, geometry, pins, blockers, gates, invariants. |
| `test_reference.py` | 38 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, README-digest-table, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `requirements.lock` | Pinned NumPy/SciPy/pystoi versions for deterministic metrics. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all external and task-local files. |

## Pinned source and asset digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
SDK paths are relative to this worktree. Every row is machine-checked against
the file and against `SOURCES.sha256` by `verify.py`.

| Source/asset | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Spatial acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `hush` component record and spatial profile assignment. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Hush "partially evaluated" row. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | 16 kHz causal competing-speaker candidate note. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Local frame/latency/quality caveat. |
| `research/voice-enhancement-20261101/agent-hush-ears-expanded/REPORT.md` | `d9285694209a54b26db0aa89a27a11b004fa0159d7ee08fc5fff0728c0869545` | Source-reported 30-pair x 3-SIR screen. |
| `research/voice-enhancement-20261101/agent-hush-ami/REPORT.md` | `f25be2b5e5e09fe3aacc9bece33e5e9ec56a548f1349871e916d46f4ba2a5acf` | Source-reported AMI speaker-dominant diagnostic. |
| `research/voice-enhancement-20261101/agent-hush-eval/REPORT.md` | `bf6be1fb4f302cc41f5eebbe9a66baf1d510d622158406e25564ba3d0e353068` | Source-reported five-pair pilot. |
| `research/voice-enhancement-20261101/agent-hush-synthetic-eval/REPORT.md` | `fa0962ec9194f4267a283c8d24d80b4b63ac2e52447e0c8fa8e163e7713ab096` | Source-reported synthetic LibriSpeech diagnostic. |
| `adapters/hush/adapter.json` | `4746e674385c2e3e377e7455d9f56e0d06a6a47532ed37c784bb0616e3105b40` | Research-workspace SPK-01 adapter descriptor; not executed, registered or changed. |
| `adapters/hush/README.md` | `c9ac19950af4138b50dc7a5d0560b4d79ed6b01dc81ec0af6a5a4bea84a8a94d` | Pinned asset hashes and HF revision declaration. |
| `adapters/hush/run.py` | `79ad67b3ff814930b1833b21254f19a63aec74d790617c826c83156a34f90d24` | Research-workspace ctypes wrapper; not executed here. |
| `data/checkouts/Hush/LICENSE` | `d2650f8a0a002d02377a5157e60071a39cc710113bf2c19f808db7045edda198` | Apache-2.0 upstream license. |
| `data/checkouts/Hush/README.md` | `6c1ae0349b459dd03bb627438a3d6af3a00afff2817da291228b603b833ebd38` | Upstream 16 kHz / ~20 ms / ~8 MB source claims. |
| `data/checkouts/Hush/deployment/README.md` | `af4b9e2df9b9b13f8207942714f71fdc12af839d0c1d9f0ad819f6ab9fdd302a` | Placeholder download URL and C-API quickstart. |
| `data/checkouts/Hush/deployment/include/weya_nc.h` | `887640d07b0147b8172ae8247cb16c460dce06e7cd54cfd9c1cfe13d1fef9f86` | Exact C ABI surface. |
| `data/checkouts/Hush/native/weya_nc_build/weya_nc/src/lib.rs` | `3aa0b16ea0c39fab4bd9fd5f85566aa3e2e18066b55fdd0ce986d16b9a99bf68` | Pinned wrapper source context. |
| `data/checkouts/Hush/deployment/models/advanced_dfnet16k_model_best_onnx.tar.gz` | `45632ccaa82b71bb743d6caa7c78e983fe2f2790a3af7f6ec48e6ed7ba085df6` | ONNX bundle; external only, not copied or loaded. |
| `data/checkouts/Hush/deployment/models/model_best.ckpt` | `a2221e335c7de2c3453b422bf7f3c609723e453f4ca29c86137fd707d62f841b` | Excluded checkpoint; pinned only to record non-use. |
| `data/checkouts/Hush/deployment/lib/libweya_nc.dylib` | `4bcd38634000d456ad68db4b6ff97fe4a462542aa65ac5f910fbf374ca33fbaa` | macOS arm64 runtime; not copied or loaded. |
| `data/checkouts/Hush/deployment/lib/libweya_nc.so` | `c4a5915c92e9500a49e6cd14804e6e88319277de2ef7d4d5cf6c0ac4456f3bbf` | Linux runtime; not copied or loaded. |
| `data/checkouts/Hush/deployment/lib/weya_nc.dll` | `633958ef839c94af6f8f5f9f8fb33c4daedaeec0373cb39a03934fdd7efa6a32` | Windows runtime; not copied or loaded. |

Boundary pins also cover `CONTRACTS.md`, both public v0 headers, `CMakeLists.txt`,
`REUSE.toml` and `scripts/ci.py`; all are unchanged and machine-checked in
`SOURCES.sha256` and `report.json:boundary_pins`.

## Reproduction

All outputs are task-local. `SOURCE_ROOT` is needed only by the verifier and
tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-HUSH
TASK=$WT/docs/task-evidence/hush
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/hush-ci
python3 -m reuse lint
git diff --check
```

## Results (synthetic boundary surrogate only)

Paired deltas are surrogate minus same-mixture identity. Positive SI-SDR/STOI
delta is better; a negative value is an adverse result. These numbers are **not
Hush results** and are **not** a quality or spatial-acceptance pass.

| Condition | SI-SDR identity → surrogate (Δ) | STOI identity → surrogate (Δ) | RMS gain | Peak | Invalid/clipped |
| --- | --- | --- | --- | --- | --- |
| `target_only` | undefined (`zero_error_identity_exact`) → undefined | 1.000000 → 1.000000 (+0.000000) | 1.000000 | 0.500000 | 0 |
| `mixture_sir12` | 12.016853 → 12.703896 (+0.687043) | 0.744795 → 0.749650 (+0.004855) | 0.985008 | 0.619790 | 0 |
| `mixture_sir18` | 18.008576 → 18.568065 (+0.559489) | 0.856772 → 0.855291 (−0.001481) | 0.991815 | 0.559661 | 0 |
| `mixture_sir24` | 24.004425 → 23.643381 (−0.361044) | 0.922980 → 0.916539 (−0.006441) | 0.992923 | 0.529525 | 0 |
| `interferer_only` | zero reference (invalid) | zero reference (invalid) | 0.150797 | 0.123558 | 0 |
| `silence` | zero reference (invalid) | zero reference (invalid) | undefined | 0.000000 | 0 |

Target/leakage view of the same synthetic runs (least-squares projection):

| Stratum | Target retention | Interferer leakage retention | Target/interferer ratio gain (dB) | Target projection SNR Δ (dB) |
| --- | --- | --- | --- | --- |
| +12 dB | 0.991190 | 0.856568 | +1.267908 | +0.687043 |
| +18 dB | 0.993701 | 0.891592 | +0.941789 | +0.559489 |
| +24 dB | 0.993230 | 0.950971 | +0.377650 | −0.361044 |

The gate is deliberately simple: it attenuates frames below twice the initial
interferer level and passes louder frames. Leakage retention falls only
modestly and the +24 dB stratum regresses, so the metrics are boundary
conformance observations, not evidence that the surrogate separates speakers.
Every valid output is finite, with no sample at or above 1.0. Interferer-only
and silence are invalid references and are never scored as speech.

Caller-asset and frame controls all fail closed: missing manifest, absent file,
library or model hash mismatch, wrong source commit, sample rate, channels,
frame size or attenuation limit, relative path, extra field, short or
two-dimensional input, NaN input, out-of-range attenuation and truncated
output. The valid-manifest control validates hashes and geometry but reports
`loaded=false` and `executed=false`. Separate instances are uncoupled, reset is
bit-identical, epoch 2 propagates, different stimuli differ and
`atten_limit_db=0` is bit-exact identity.

## Gates and reopen conditions

The package records eleven blocked gates: caller asset present/verified, model
bundle and runtime rights, exact runtime reproduction, native streaming
boundary, task-matched held-out spatial labels, enrollment-conditioned
extraction scope, real-cohort leakage and target damage, independent listening,
target-runtime timing/memory, opt-in adapter intake, and public default
selection. `readiness.json` is the concise strict conclusion;
`report.json:gates` and `contract.json:gates` carry the exact reopen condition
for each.

Reopen only when a caller supplies the pinned 16 kHz library and ONNX bundle
with matching hashes/commit/attenuation limit, artifact-specific model and
runtime rights plus a verifiable distribution channel and training-data
provenance are cleared, the exact runtime is reproduced with an approved
reference vector, the native streaming boundary is verified, a rights-cleared
held-out spatial cohort with speaker and room labels is scored, the
enrollment/reference-conditioning scope is decided, real-overlap leakage and
target damage are measured, independent listening exists, target timing/memory
is measured, opt-in intake is complete and a public default decision is
recorded. Until then the candidate stays DEFER, incomplete and not qualified.

## Separation from other Hush work

The research-workspace adapter `adapters/hush/` and the
`research/voice-enhancement-20261101/agent-hush-*` reports are pinned external
provenance. They were not executed, imported, pooled or reinterpreted by this
package, and no DNS-2020 pilot is treated as valid SPK-01 evidence.
