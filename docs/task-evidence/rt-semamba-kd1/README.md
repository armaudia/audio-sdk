<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RT-SEMAMBA-KD1 — RT-SEMamba KD1 caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`RT-SEMamba KD1` (`component_id=rt-semamba-kd1`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json`
(`verification_profile: enhancement`) and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package models the exact RT-SEMamba KD1 enhancement boundary as a
**caller-supplied asset** — checkpoint + KD1 config + pinned source tree +
PyTorch/Mamba runtime — at 16 kHz mono, STFT window 400 samples (25 ms), hop
100 samples (6.25 ms), 25 ms algorithmic latency and the upstream 100 ms
realtime chunk. Because the exact asset set, an immutable distribution record
and artifact-specific rights are unavailable here, it executes a **stdlib/
numpy synthetic STFT-domain surrogate** and records a strict readiness
conclusion. It is **not RT-SEMamba**, does not import PyTorch or Mamba, does
not load the checkpoint, does not read audio, does not invoke a runtime, does
not measure a device clock, does not conduct listening, does not benchmark the
SDK and makes no release or quality claim. Only this task-local directory is
added.

## Exact external blocker

The exact upstream identity is pinned: `RoyChao19477/RT-SEMamba` at commit
`0c9e8c7c42caadd7badb6cc145c8af93f760863c`, MIT `LICENSE`, the KD1 checkpoint
`ckpts/g_00766000.pth` (4,235,024 bytes, SHA-256
`7d76e2c5f322cc0dd58abd0b9b371890b29c3710d7833cdfebb46a823961f5cc`), the KD1
config `recipes/KD1/KD1.yaml` (SHA-256
`2db65c33e66108d7616d47ca509a3dc46983980cae63a216d1ccb98daf0ee222`), the
inference/architecture sources and the vendored pure-PyTorch Mamba fallback,
all hashed from the external research checkout. No caller asset manifest or
copy exists in the SDK worktree, and no PyTorch/Mamba runtime is installed.
The pinned adapter is CPU-only and the research host reports MPS and CUDA
unavailable, so the exact runtime cannot be loaded, reproduced or measured
here.

The repository declares MIT, but checkpoint-specific redistribution and
product-use rights, VCTK-DEMAND dataset terms and provenance, an immutable
distribution record and legal review are not established. Nothing was copied,
vendored, built, downloaded or redistributed. Four exact blockers are recorded
verbatim in `contract.json:exact_blockers`, `report.json:exact_blockers` and
`readiness.json:exact_blocker`; every release gate remains `blocked`.

**Reopen condition.** A caller supplies the KD1 checkpoint, KD1 config and
pinned source tree with matching SHA-256 values, source revision and STFT
geometry; checkpoint redistribution/product-use rights, VCTK-DEMAND terms and
provenance, an immutable distribution record and legal review are cleared; the
pinned PyTorch/Mamba runtime reproduces approved reference outputs; the native
streaming boundary and state semantics are verified; a rights-cleared held-out
paired cohort, clean-speech preservation on real speech and independent
listening exist; and target-runtime timing/memory, opt-in intake and an
explicit default decision are recorded. Until then the candidate stays DEFER.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI or installed behavior. The adapter is offline, so
  no SDK callback is invoked.
- The task-local caller asset contract requires exactly `checkpoint_path`,
  `checkpoint_sha256`, `config_path`, `config_sha256`, `source_revision`,
  `sample_rate_hz`, `channels`, `window_samples`, `hop_samples` and
  `algorithm_latency_samples`; it pins 16 kHz, mono, 400/100 STFT geometry,
  400-sample latency and the RT-SEMamba commit.
- A manifest is accepted only when both files are absolute, present and
  SHA-256-matched and the geometry/revision fields match. Validation never
  imports PyTorch, loads the checkpoint or executes the model. Missing,
  absent, hash-mismatched, relative-path, extra-field or wrong-geometry
  manifests fail closed before processing.
- The surrogate runs natively at 16 kHz, uses a causal periodic-Hann STFT
  (400/100), estimates a per-bin noise floor from the first five frames and
  applies a bounded magnitude gate with a 0.20 floor. A 400-sample (25 ms)
  window delay is modeled then compensated. The measured impulse is at 4400
  samples without compensation and at 4000 samples with compensation (content
  lag 0 samples).
- `clean_control` has a zero noise-floor estimate, so the gate is exactly 1
  and the output is a bit-exact passthrough. `idle_noise` and `silence` have no
  clean reference and are always invalid, never scored as speech.
- Availability is a **modeled** source-derived clock
  (`fixture-sample-coordinate-not-device`), not a wall-clock or device
  measurement.

## Enhancement profile application

- Identity/noisy control: the unprocessed mixture is the baseline at each
  synthetic SNR stratum (+20/+10/+0 dB), with a separate clean-only control and
  noise-only/silence invalid controls.
- Paired SNR, SI-SDR and STOI use the exact synthetic clean target as the
  reference. They are **synthetic-only** and are not a real-cohort score.
- Clean-speech preservation is the clean-only passthrough; it is not a real
  clean-speech result.
- Peaks, clipping, nonfinite outputs and output length are checked for every
  condition; all outputs are finite and below full scale.
- Alignment, state, reset and separate-instance behavior are modeled.
  **Memory and content/availability timing are not measured**; the only memory
  and timing numbers retained are source-reported provenance.
- No established task-matched baseline is reproduced. The pinned research
  FastEnhancer Small and DeepFilterNet3 crop values are provenance only and are
  never pooled with the surrogate metrics.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, STFT boundary surrogate, Enhancement metrics, canonical report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, geometry, pins, blockers, gates, invariants. |
| `test_reference.py` | 43 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, README source/artifact digest-table, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `requirements.lock` | Pinned NumPy/SciPy/pystoi versions for deterministic metrics. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all external and task-local files. |

## Results (synthetic boundary surrogate only)

Paired deltas are surrogate minus same-clip identity. Positive SNR/SI-SDR/STOI
delta is better; a negative value is an adverse result. These numbers are
**not RT-SEMamba results** and are **not** a quality or acceptance pass.

| Condition | SNR identity → surrogate (Δ dB) | SI-SDR identity → surrogate (Δ dB) | STOI identity → surrogate (Δ) | RMS change dB | Peak | Invalid/clipped |
| --- | --- | --- | --- | ---: | ---: | ---: |
| `clean_control` | undefined (`zero_error_identity_exact`) | undefined (`zero_error_identity_exact`) | 1.000000 → 1.000000 (+0.000000) | 0.000000 | 0.423909 | 0 |
| `noisy_snr20` | 20.518808 → 23.398529 (+2.879721) | 20.511439 → 23.604970 (+3.093531) | 0.904367 → 0.904491 (+0.000124) | -0.182939 | 0.417724 | 0 |
| `noisy_snr10` | 10.518808 → 14.331177 (+3.812369) | 10.494632 → 14.228985 (+3.734353) | 0.777191 → 0.766434 (-0.010757) | -0.706975 | 0.422518 | 0 |
| `noisy_snr0` | 0.518808 → 5.798561 (+5.279753) | 0.441269 → 4.782070 (+4.340801) | 0.553513 → 0.513444 (-0.040069) | -2.867688 | 0.567948 | 0 |
| `idle_noise` | zero reference (invalid) | zero reference (invalid) | zero reference (invalid) | -6.755547 | 0.239061 | 0 |
| `silence` | zero reference (invalid) | zero reference (invalid) | zero reference (invalid) | undefined | 0.000000 | 0 |

The surrogate improves SNR and SI-SDR but **regresses STOI** at +10 dB
(−0.010757) and +0 dB (−0.040069). Both regressions are recorded verbatim in
`report.json:regressions`; no threshold was tuned against real data. Clean
passthrough is bit-exact with STOI 1.0 and no sample at or above 1.0.

Source-reported provenance (not reproduced, not pooled): the pinned 30-item
2.5 s DNS crop screen reports mean ΔSNR −12.41 dB (95% CI −15.51, −9.13),
ΔSI-SDR −13.43 dB (−16.49, −10.06), ΔSTOI +0.0043 (−0.0042, +0.0130), median
RTF 5.81, p95 8.15, mean output peak 13.03, maximum 122.06 and process
high-water RSS 3,219,685,376 bytes; the full 10 s CPU attempt timed out.
Upstream reports 3.18 PESQ / 0.95 STOI on VCTK-DEMAND and 0.11 RTF on an
RTX 5090. All are provenance only.

## Controls and adverse cases

- Caller-asset controls fail closed: missing manifest, absent file, checkpoint
  or config hash mismatch, wrong source revision, sample rate, channels, window,
  hop or algorithmic latency, relative path and extra field. The valid-manifest
  control validates hashes and geometry but reports `loaded=false` and
  `executed=false`.
- Frame controls fail closed: short, two-dimensional, nonfinite and truncated
  input, and wrong sample-rate/channel/window/hop configuration. Rejections
  leave surrogate state unchanged; silence is finite and zero.
- State controls: separate instances are uncoupled, reset is bit-identical,
  epoch 2 propagates, different stimuli differ and the explicit bypass path is
  bit-exact identity.

## Pinned source and asset digests (SHA-256)

`source:`-style paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
task-local paths are relative to this directory. Every row is machine-checked
against the file and against `SOURCES.sha256` by `verify.py`.

<!-- SOURCE_DIGEST_TABLE_START -->
| Source/asset | SHA-256 |
| --- | --- |
| `adapters/rt-semamba/README.md` | `497f90ce384570593568c5f597b2f06dc89d9d2bd03b5f4d63e85c5becc65283` |
| `adapters/rt-semamba/adapter.json` | `5572eb0ce171ea6d22c334807584230efbf0ba0114d851348841c33535c08a12` |
| `adapters/rt-semamba/requirements.lock` | `65906eabf3e9c692cc949257976de1f4b789a6bb1223781cdc8cb46f955410ee` |
| `adapters/rt-semamba/run.py` | `c3b006211054b9faa23e8ab518c9acac098e6252c6d8ab4b2315c53c2acae3bb` |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `data/checkouts/RT-SEMamba/LICENSE` | `04b1d017b906f5d0c6815e60cadeabb1a3f5b4fb743c1b77343841fd735eb5e8` |
| `data/checkouts/RT-SEMamba/README.md` | `c69693beb94f5a84acf076d19e9d24703c0a09ae7d642f670f04645f73c530c8` |
| `data/checkouts/RT-SEMamba/ckpts/g_00259000.pth` | `c97bc702d2840f1173ef221e92600a331dbbde64c5a70399f39ef85d4804935b` |
| `data/checkouts/RT-SEMamba/ckpts/g_00766000.pth` | `7d76e2c5f322cc0dd58abd0b9b371890b29c3710d7833cdfebb46a823961f5cc` |
| `data/checkouts/RT-SEMamba/inference.py` | `290da30c93112fb2d30cb1b88e46eb13262c7946a0cec3e1e01d4335ba988629` |
| `data/checkouts/RT-SEMamba/mamba_install_mps/mamba_ssm/__init__.py` | `fd5bb14b209676fc12a2d66c8f9f11d5c1dfef4296ee5633a0e5856ab238cb9d` |
| `data/checkouts/RT-SEMamba/mamba_install_mps/mamba_ssm/modules/mamba_simple.py` | `dc035a4dcfbc9f9809e2bb60764f7bfe38259b6397968399fc33cad159300a43` |
| `data/checkouts/RT-SEMamba/mamba_install_mps/mamba_ssm/ops/selective_scan_interface.py` | `b0e6f888957f48b94ead8b40c9faa12e67c4cfecd31e2a0cdfecaf28c445bd64` |
| `data/checkouts/RT-SEMamba/models/generator.py` | `23380a65d1b12df119985718a339c9dc99469dc3a10b141fee3c3c42b44b9ccd` |
| `data/checkouts/RT-SEMamba/models/stfts.py` | `9da92bdf11f162f41f01ee9fc6951c161c07becd07cb6590cebcee89b508296a` |
| `data/checkouts/RT-SEMamba/recipes/KD1/KD1.yaml` | `2db65c33e66108d7616d47ca509a3dc46983980cae63a216d1ccb98daf0ee222` |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `research/voice-enhancement-20261101/agent-semamba-eval/REPORT.md` | `91b5e3642adbfad49878d0238215163fc475a34c135b309521c4d08a982a599c` |
| `research/voice-enhancement-20261101/agent-semamba-eval/crop_screen_30.py` | `72b0b198b1124276e4ba4cb0e0be2bd78bae8bfa72399b8e4f49d4577a0473f4` |
| `research/voice-enhancement-20261101/agent-semamba-eval/score_crop_stoi.py` | `c4795a0b63723d4c26202ecb2da445234e00233c176abe952c07bc639732795a` |
| `research/voice-enhancement-20261101/agent-semamba-eval/short_crop_diagnostic.py` | `18cb6c2618fca837a66db1ab32d952f7c6f5b9b7cc4f01a5f64066e8c60cc51a` |
| `research/voice-enhancement-20261101/agent-semamba-result-audit/REPORT.md` | `fbc2703c763eae2dd0146c80b212821d44eacb14e8b029766ddb72839c5e2503` |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- SOURCE_DIGEST_TABLE_END -->

## Generated artifact digests

`verify.py` checks every row's digest and byte count, and requires the row set
to equal the declared artifact set. `README.md` and `SOURCES.sha256` are
deliberately excluded to keep the table acyclic.

<!-- ARTIFACT_DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `01315ca93c35ee571c9138df9cd1c006ee959f755d3f50a95bc94890d9b4dca3` | 3190 |
| `adapter.json` | `59fba133f667177fc77faf27b7f4a07a63a699dfb82ad5cdfc0a149592ceaf02` | 944 |
| `adapter.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `fb3e9e5a7e1604f015ffdd66aa971ac1f1023e5e1e93c167cef8eb466b77d402` | 20943 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `readiness.json` | `38c9d863f563d7e157cd8c2ebe733b5a9e31aba860b4b75c4fcea896eae70713` | 3716 |
| `readiness.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `796fba1f288371b77a18f51239853028a3778f396d88e33fde8cafd2f1e6beda` | 82234 |
| `report.json` | `81872b32223f6100c20c9e66e992baa6e4938fe52c01292d86360268f9c29283` | 48635 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `c4dc01bc9755da54fedb31255feb150fd7463973a111bc34c29aa0e0bfd99d85` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `requirements.lock` | `34d25491f027c663133b9164ed9229eda0f898597a0ed1a41407493392f57e50` | 226 |
| `requirements.lock.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `9c42cbc058f505641f4b962d56e062dba261353443dc14d9faf6b43ec380257a` | 1408 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `test_reference.py` | `b2e802b65f344db053bbdd0e9645215651dd4d5fefc134ee260bf898b047f844` | 25052 |
| `verify.py` | `122b28b16be2bcfa1ad53a67df537f1131d76036899ead6f5d5eb28016651391` | 43961 |
<!-- ARTIFACT_DIGEST_TABLE_END -->

Boundary pins also cover `CONTRACTS.md`, both public v0 headers,
`CMakeLists.txt`, `REUSE.toml`, `scripts/ci.py` and
`LICENSES/Apache-2.0.txt`; all are unchanged and machine-checked in
`SOURCES.sha256` and `report.json:boundary_pins`.

## Reproduction

All outputs are task-local. `SOURCE_ROOT` is needed only by the verifier and
tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-RT-SEMAMBA-KD1
TASK=$WT/docs/task-evidence/rt-semamba-kd1
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output build/ci
python3 -m reuse lint
git diff --check
```

## Expected counts and digests

- Six conditions, 32,000 samples each; 192,000 synthetic observed samples.
- 325 causal STFT frames per 2,000 ms clip; no startup, tail or flush samples.
- Three SNR strata (+20/+10/+0 dB), one clean control, one noise-only and one
  silence control; 13 caller-asset adverse cases and 8 frame/config adverse
  cases, all fail closed.
- Impulse: uncompensated index 4400, compensated index 4000, content lag 0.
- Tests: **43 passed, 0 failed, 0 skipped** (CPython 3.12.16).
- `report.json` digest is in the artifact table and in `report.json.sha256`.

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `caller_supplied_asset_present_and_verified` | blocked | Caller-held checkpoint, config and source tree match the pins. |
| `artifact_and_runtime_rights` | blocked | Checkpoint/dataset terms, provenance, distribution record and legal review. |
| `exact_runtime_reproduction` | blocked | Pinned PyTorch/Mamba runtime reproduces approved reference outputs. |
| `streaming_boundary_and_state` | blocked | Native 400/100 boundary, 25 ms latency, chunking and reset/flush. |
| `rights_cleared_task_matched_cohort` | blocked | Rights-cleared held-out paired cohort with clean references. |
| `clean_preservation_and_independent_listening` | blocked | Real clean-speech preservation and permitted listening. |
| `target_runtime_timing_memory` | blocked | Target end-to-end timing, memory, pacing and deadlines. |
| `opt_in_adapter_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

## Separation from other RT-SEMamba work

The research-workspace adapter `adapters/rt-semamba/` and the pinned
`research/voice-enhancement-20261101/agent-semamba-eval/` and
`agent-semamba-result-audit/` reports are external provenance. They were not
executed, imported, pooled or reinterpreted by this package, and no DNS crop
screen is treated as valid real-cohort Enhancement evidence.
