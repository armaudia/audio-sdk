<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ROSE-CD-ONE-STEP — ROSE-CD one-step caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ROSE-CD one-step` (`component_id=rose-cd-one-step`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package models the pinned official ROSE-CD one-step checkpoint as a
**caller-supplied-asset reference** at 16 kHz mono, offline whole-clip, with the
upstream 510-point / 128-hop STFT geometry and 64-STFT-frame reflection-padding
requirement. Because the 1.22 GiB checkpoint bytes, the exact PyTorch runtime
and artifact-specific rights are unavailable, it executes a **stdlib/numpy
synthetic surrogate** and records a strict readiness conclusion. It is **not
ROSE-CD**, does not import PyTorch, does not load a checkpoint or graph, does
not download or vendor anything, does not read audio, does not invoke a runtime,
does not measure a device clock, does not conduct listening, does not benchmark
the SDK and makes no release or quality claim. Only this task-local directory is
added.

## Exact external blocker

The exact upstream identity is pinned: `LiangXu123/ROSE-CD` at commit
`8a7477f046a133737d6f1744b643fbe3f3ea96cd`, MIT `LICENSE`, the 16 kHz
configuration, the 510/128 `hann` STFT contract, the reflection-padding helper
and the preprocessing/entrypoint source. The intended checkpoint is
`logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt` at Hugging Face revision
`1c80e0863c1a8682f52a8e5be2efdf58a130eb62`, recorded in the external research
ledger as **1,313,064,415 bytes**, SHA-256
`5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4`.

The checkpoint bytes are **absent** from both the external research checkout
and this SDK worktree, no caller manifest exists, and the exact Python 3.11
PyTorch/PyTorch-Lightning runtime is not installed or pinned here. The MIT
source/model-card declaration does not establish artifact-specific checkpoint
redistribution or product-use rights, the VoiceBank-DEMAND/EARS-WHAM
training-data rights chain or a legal review. Nothing was copied, vendored,
built, downloaded, imported or redistributed.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers`, `report.json:exact_blockers` and
`readiness.json:exact_blocker`. Every release gate remains `blocked`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI or installed behavior.
- The task-local caller asset contract requires exactly `checkpoint_path`,
  `checkpoint_sha256`, `source_dir`, `source_revision`,
  `checkpoint_revision`, `sample_rate_hz`, `channels`, `sampler_type`, `steps`
  and `snr`; it pins 16 kHz, mono, the ROSE-CD commit, the Hugging Face
  revision, `sampler_type=stochastic`, `steps=1` and `snr=0.5`.
- A manifest is accepted only when the checkpoint is absolute, present and
  SHA-256-matched; the source directory is absolute, present and contains the
  pinned source markers; and revision/geometry/configuration fields match.
  Validation never imports or executes the source and never loads the
  checkpoint.
- The surrogate buffers caller chunks and enhances the whole clip once at
  `finish()`. Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280` and one
  32,000-sample call all produce identical output digests.
- The upstream STFT boundary is modellistically recorded: `n_fft=510`,
  `hop_length=128`, `center=True`, `hann`, reflection padding to a multiple of
  64 frames. Inputs shorter than 8,064 samples (64 STFT frames) are rejected.
  A 32,000-sample clip yields 251 frames and 5 internal reflection-pad frames;
  the padded frames are never emitted. Output length equals input length.
- A partial final 160-sample frame is zero-padded only for internal gain
  estimation, counted as `internal_frame_padding_samples`, and trimmed before
  output.
- The upstream whole-clip peak normalization is modelled: the peak magnitude is
  divided out before the gate and restored after it. The surrogate has no
  modelled delay and no delay compensation; content lag is 0 samples.
- Availability is a **modeled** source-derived clock
  (`fixture-monotonic-not-device`), not a wall-clock or device measurement. An
  offline whole clip is available only after its final sample.

## Enhancement profile application

`report.json:enhancement_profile` records the identity/noisy control, paired
synthetic SI-SDR/STOI/SNR, clean-speech preservation, peak and invalid-output
checks, alignment, state/memory scope and the explicitly unmeasured fields.
Task-matched baseline reproduction, real clean references, unpaired predictive
screening or listening, real audio, device timing, memory and quality are
`false`/`not_run`/`blocked_unmeasured`.

### Synthetic fixture results (not a ROSE-CD result)

Scores are computed on the same 32,000-sample clip for every condition. Paired
deltas are surrogate minus noisy identity. Positive SI-SDR/STOI delta is better;
a negative value is an adverse result. These numbers are **not ROSE-CD results**
and are **not a quality pass**.

| Condition | SI-SDR identity → surrogate (Δ) | STOI identity → surrogate (Δ) | RMS gain | Peak | Invalid/clipped |
| --- | --- | --- | --- | --- | --- |
| `clean_only` | undefined (`zero_error_identity_exact`) → undefined | 1.000000 → 1.000000 (0.000000) | 1.000000 | 0.500000 | 0 |
| `noisy_snr10` | 10.008793 → 11.212568 (+1.203775) | 0.707915 → 0.732453 (+0.024538) | 0.974693 | 0.648817 | 0 |
| `noisy_snr0` | −0.005345 → −0.055829 (−0.050484) | 0.492285 → 0.492285 (0.000000) | 0.150438 | 0.142500 | 0 |
| `noise_only` | zero reference (invalid) | zero reference (invalid) | 0.150907 | 0.038886 | 0 |
| `silence` | zero reference (invalid) | zero reference (invalid) | undefined | 0.000000 | 0 |

The clean-only path is exactly identity: the peak is 0.5, the normalization
round-trip is exact and STOI is 1.0. The `noisy_snr0` SI-SDR regression is a
property of the naive initial-noise-floor gate, not evidence about ROSE-CD.
The gate estimates the noise level from the first five 10 ms frames and
over-suppresses when speech and noise have equal RMS. Every valid output is
finite, with no sample at or above 1.0. Noise-only and silence have a zero
reference and are never scored as speech.

### Honest regression

One regression is recorded verbatim in `report.json:regressions`:
`noisy_snr0` / `si_sdr_db` / −0.050484 dB. No threshold was tuned against real
data, and no surrogate value is used to qualify or rank ROSE-CD.

## Controls and adverse cases

Caller-asset and clip controls all fail closed before processing:

- missing manifest, absent checkpoint, checkpoint hash mismatch, wrong source
  revision, wrong checkpoint revision, wrong sample rate, channels, sampler
  type, steps or SNR, relative path, extra field and missing source marker;
- short clip below 64 STFT frames, two-dimensional input, NaN input,
  out-of-range input, truncated output and a second `finish()`;
- a missing reference is `invalid`, exact digital silence returns exact zeros
  with `nfe=0`, and a rejected input leaves state unchanged.

The valid-manifest control validates hashes, geometry and source markers but
reports `loaded=false` and `executed=false`. Separate instances are uncoupled,
reset is bit-identical and restores the initial buffer, epoch 2 propagates,
different stimuli differ and chunking never changes the output.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, offline boundary surrogate, metrics, canonical report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
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
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `rose-cd-one-step` component record and Enhancement profile assignment. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | ROSE-CD one-step "evaluated" row. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | 16 kHz offline one-step census note. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Checkpoint byte count, SHA-256, source revision and MIT metadata. |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported 30-pair DNS2020 pilot; raw and RMS-matched separated. |
| `research/ears_blind_noise_screen_20261027.md` | `d521ffc71e5f9b4f77949760578fc0f7f6773b2b1f4f06680f08448d8793ce2e` | Source-reported 12-clip EARS DNSMOS screen. |
| `research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | Completion record and raw/RMS separation. |
| `research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Selection context. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Local runtime/quality caveat. |
| `adapters/rose-cd/adapter.json` | `552aab85aa61b9d4a4c33df930c96bec082156163718fcff867d70b40b4c306c` | Research-workspace CLN-01 adapter descriptor; not executed or changed. |
| `adapters/rose-cd/README.md` | `988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72` | Exact checkpoint hash/revision, STFT padding and runtime constraints. |
| `adapters/rose-cd/run.py` | `9fe6d70f8943da5d669778916df7c9416aa6b2a00389a3ee6e786229b5cbc951` | Research-workspace CPU adapter; not executed here. |
| `data/checkouts/ROSE-CD/LICENSE` | `1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd` | MIT upstream license. |
| `data/checkouts/ROSE-CD/README.md` | `8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3` | Model scope and source-reported results. |
| `data/checkouts/ROSE-CD/config.json` | `815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a` | 16 kHz model configuration. |
| `data/checkouts/ROSE-CD/requirements.txt` | `d5e64c3b28a8c184a1e8e2507e66d210f34602143a452ed8513778f903bc7c48` | Upstream dependency declaration; not installed. |
| `data/checkouts/ROSE-CD/enhancement.py` | `dc19589a8666246fa03d79e8298cd258849d6f07f477139bef778893c49d11ff` | Upstream inference entrypoint context; not executed. |
| `data/checkouts/ROSE-CD/scripts/eval_CT.sh` | `3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c` | Upstream CT evaluation recipe; not executed. |
| `data/checkouts/ROSE-CD/sgmse/model.py` | `1d6187c2997bf0e3184518dbd1c07c6704efa5d3ed50aff790495d4e13872237` | Pinned model class context; not imported or loaded. |
| `data/checkouts/ROSE-CD/sgmse/data_module.py` | `fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b` | STFT `n_fft=510` / `hop=128` contract. |
| `data/checkouts/ROSE-CD/sgmse/util/other.py` | `092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0` | `pad_spec` 64-frame reflection-padding contract. |

The absent checkpoint is **not** a file pin. Its ledger identity
(`data/models/rose-cd/last.ckpt`, 1,313,064,415 bytes, SHA-256
`5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4`) is recorded
in `model_provenance.checkpoint` and `readiness.json:external_asset`. Boundary
pins also cover `CONTRACTS.md`, both public v0 headers, `CMakeLists.txt`,
`REUSE.toml` and `scripts/ci.py`; all are unchanged and machine-checked in
`SOURCES.sha256` and `report.json:boundary_pins`.

## Reproduction

All outputs are task-local. `SOURCE_ROOT` is needed only by the verifier and
tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ROSE-CD-ONE-STEP
TASK=$WT/docs/task-evidence/rose-cd-one-step
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/rose-cd-one-step-ci
python3 -m reuse lint
git diff --check
```

## Expected counts and gates

- `test_reference.py`: **38/38** deterministic checks, no skips, no network.
- `verify.py`: pin manifest, README digest table, canonical JSON, sidecar,
  reproduction, licensing, scope and strict-parser checks all pass.
- Ten gates are blocked: caller asset present/verified, checkpoint and runtime
  rights, exact runtime reproduction, offline clip boundary and padding,
  output-level policy, real cohort, independent listening, target-runtime
  timing/memory, opt-in adapter intake and public default selection.
  `readiness.json` is the concise strict conclusion; `report.json:gates` and
  `contract.json:gates` carry the exact reopen condition for each.

Reopen only when a caller supplies the pinned one-step checkpoint and source
checkout with matching hashes/revisions, artifact-specific checkpoint and
runtime rights plus the training-data rights chain are cleared, the exact
Python 3.11 runtime is reproduced with an approved reference vector, the native
offline whole-clip boundary and 64-frame padding requirement are verified, an
explicit raw-versus-RMS-matched shipped configuration is recorded, a
rights-cleared held-out real cohort is scored, independent listening exists,
target timing/memory is measured, opt-in intake is complete and a public default
decision is recorded. Until then the candidate stays DEFER, incomplete and not
qualified.

## Separation from other ROSE-CD work

The sibling `SDK-ROSE-CD-RMS-MATCHED` task is out of scope; this package models
only the raw pinned one-step checkpoint and never pools raw and RMS-matched
results. `SDK-ROSE-CD-EARS-REVERB-CONFIGURATION` is a separate Room-profile
dereverberation question. The research adapter and reports are pinned external
provenance; they were not executed, imported, pooled or reinterpreted here.
