<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ROSE-CD-RMS-MATCHED — ROSE-CD RMS-matched caller-supplied-asset boundary

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ROSE-CD RMS-matched` (`component_id=rose-cd-rms-matched`). The acceptance
profile is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package records the exact upstream identity of the research
`ROSE-CD input-RMS-matched` configuration: ROSE-CD one-step output rescaled once
over the whole clip so its RMS equals the noisy input RMS, with **no clean
reference**. Because the 1.22 GiB checkpoint, the exact PyTorch runtime and an
approved definition of the RMS-matching recipe are absent, it runs a
**stdlib-only deterministic surrogate** and records a strict readiness
conclusion. It is **not ROSE-CD**, does not import PyTorch, does not load a
checkpoint or graph, does not download or vendor anything, does not read audio,
does not invoke a runtime, does not measure a device clock, does not conduct
listening, does not benchmark the SDK and makes no release or quality claim.
Only this task-local directory is added.

## Exact blockers

The upstream identity is pinned: `LiangXu123/ROSE-CD` at commit
`8a7477f046a133737d6f1744b643fbe3f3ea96cd`, MIT `LICENSE`. The intended
checkpoint is `logs/CT_pesq5e-4_L2/8ar2h6zv/last.ckpt` at Hugging Face revision
`1c80e0863c1a8682f52a8e5be2efdf58a130eb62`, recorded in the external research
ledger as **1,313,064,415 bytes**, SHA-256
`5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4`.

The source checkout **is** present at `data/checkouts/ROSE-CD` on the pinned
commit, but the checkpoint bytes are **absent** from both the research
workspace and this SDK worktree, no caller manifest exists, and PyTorch is not
importable from the available Python 3.10, 3.11 or 3.12 interpreters. The MIT
source/model-card declaration does not establish artifact-specific checkpoint
redistribution or product-use rights, the VoiceBank-DEMAND / EARS-WHAM
training-data rights chain or a legal review. The research record states only
“whole-clip RMS match to the noisy input”; no source file pins the gain formula,
zero/silence handling, peak/clip policy or precision.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers`, `report.json:exact_blockers`:
`checkpoint_absent`, `runtime_absent`, `rms_match_recipe_unpublished` and
`artifact_and_data_rights_uncleared`. Every release gate remains `blocked`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI or installed behavior.
- The task-local caller asset contract requires exactly `checkpoint_path`,
  `checkpoint_sha256`, `source_dir`, `source_revision`,
  `checkpoint_revision`, `sample_rate_hz`, `channels`, `frame_samples`,
  `variant`, `rms_match_scope`, `rms_match_reference` and `peak_policy`; it
  pins 16 kHz, mono, 160 samples, the ROSE-CD commit, the Hugging Face
  revision, `variant=one-step-rms-matched`, `rms_match_scope=whole_clip` and
  `rms_match_reference=noisy_input`.
- A manifest is accepted only when the checkpoint is absolute, present and
  SHA-256-matched and the source directory is absolute and present. Revision
  and geometry fields are then compared to the pins. Validation never imports
  or executes the source and never loads the checkpoint.
- `peak_policy` must remain `unpinned`: pinning `clip_to_unity` or any other
  guessed clamp is rejected because the research recipe does not publish one.
- The whole-clip RMS-matching boundary is real and testable. The *enhancer*
  stage is a clearly labelled, model-free surrogate. The surrogate is never
  described as ROSE-CD and cannot qualify the candidate.
- Availability is **modeled**: whole-clip processing is available only after
  the final sample. There is no streaming result, no device timing and no
  content-delay claim.

## RMS-matched definition

`output = gain * raw_enhanced`, where
`gain = rms(noisy_input) / rms(raw_enhanced)` is computed once over the whole
clip. Consequences enforced by the package:

- output RMS equals noisy-input RMS within float tolerance;
- SI-SDR is invariant under the positive gain;
- waveform correlation between raw and matched output is 1.0;
- a zero noisy RMS returns exact zeros with an undefined gain;
- a zero enhanced RMS with nonzero noisy RMS is rejected;
- no implicit peak clamp is applied, so peak growth is reported, not hidden;
- the gain depends on the complete clip, so the operation is **not**
  streaming-capable.

The research record separates raw and RMS-matched configurations. This package
never pools them: the raw surrogate is a control, and the matched surrogate is
the task configuration.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item. Each
item is checked by `verify.py` against `report.json:acceptance_profile`.

| Required item | Evidence |
| --- | --- |
| Identity/noisy control | Frozen synthetic clip; identity is the mandatory control |
| Established task-matched baseline | Raw surrogate enhancer is the control; real ROSE-CD raw is absent |
| Paired SI-SDR and STOI | SI-SDR and SNR on the synthetic clean reference; STOI is not implemented and not claimed |
| Clean-speech preservation | Positive-gain waveform preservation and correlation |
| Peaks and invalid outputs | Exact peak, zero clipped/nonfinite outputs, fail-closed invalid input |
| Unpaired/predictive screen | Not run; no real corpus or predictive scorer |
| Alignment, state, memory | Declared whole-clip scope; no device timing or memory measured |
| Availability timing | Source-derived whole-clip availability only; no device clock |

Task-matched baseline reproduction, real clean references, STOI, real audio,
device timing, memory, listening and quality remain
`false`/`not_run`/`blocked_unmeasured`.

### Synthetic fixture results (not a ROSE-CD result)

All values are exact `report.json` values rounded to 9 decimals. They are
surrogate behavior observations, **not ROSE-CD results**, **not device timing**
and **not a quality pass**. Paired deltas are relative to the noisy identity.

| Condition | SI-SDR dB | SNR dB | RMS | Peak | Clipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| identity (noisy) | 3.978376769 | 4.013936232 | 0.040454532 | 0.140716553 | 0 |
| raw surrogate | 3.966653915 | 4.123133435 | 0.039894270 | 0.139508839 | 0 |
| RMS-matched surrogate | 3.966653915 | 4.005530815 | 0.040454532 | 0.141468058 | 0 |

Matching gain `1.014043686`. The SI-SDR delta matched-vs-raw is exactly
`0.0 dB`; the SNR delta is `−0.117602620 dB`. The small negative SNR change is
honest: this surrogate does not reproduce ROSE-CD's output-level loss, so the
source-reported scale-sensitive SNR recovery is neither reproduced nor
claimed. The matching post-processor itself is verified by the injected-scale
control, which restores RMS exactly and preserves SI-SDR.

## Controls and adverse cases

Caller-asset and clip controls all fail closed before processing:

- missing/extra manifest field, relative path, absent checkpoint, checkpoint
  hash mismatch, wrong source/checkpoint revision, wrong sample rate, channels
  or frame, raw variant, streaming scope, clean-reference matching and a
  guessed peak policy;
- empty clip, non-sequence, NaN, infinity, boolean sample and out-of-range
  sample;
- mismatched match lengths, zero enhanced RMS with nonzero reference, and
  nonfinite enhanced input;
- exact digital silence returns exact zeros with `gain_defined=false`;
- the whole-clip prefix produces a different gain and is not byte-identical to
  the corresponding full-clip prefix;
- three cold-start runs produce identical matched-output digests.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, whole-clip RMS matcher, surrogate enhancer, metrics, canonical report/contract builders. |
| `run.py` | Regenerates `contract.json`, `report.json`, `report.json.sha256`, `SOURCES.sha256` and the README table byte-identically. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, geometry, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, README-digest-table, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `SOURCES.sha256` | SHA-256 manifest for all external and task-local files. |
| `*.license` | SPDX Apache-2.0 sidecars for generated non-Python artifacts. |

## Pinned source and asset digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
SDK paths are relative to this worktree. Every row is machine-checked against
the file and against `SOURCES.sha256` by `verify.py`.

<!-- digest-table: source -->
| Source | SHA-256 |
| --- | --- |
| `source:adapters/rose-cd/README.md` | `988d1d87847910e13f65ce8e5380c3f76ed9f4be924789be6b9e80ab14719b72` |
| `source:adapters/rose-cd/adapter.json` | `552aab85aa61b9d4a4c33df930c96bec082156163718fcff867d70b40b4c306c` |
| `source:adapters/rose-cd/run.py` | `9fe6d70f8943da5d669778916df7c9416aa6b2a00389a3ee6e786229b5cbc951` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:data/checkouts/ROSE-CD/LICENSE` | `1065d138be7bfe31684e9f1c0bf8446ce7178299a7681746c50d2315f96b0ebd` |
| `source:data/checkouts/ROSE-CD/README.md` | `8ebab9ccee56cac770a3e36a4c8ade1b812a3f6b9736e093b5bf2a9596509fa3` |
| `source:data/checkouts/ROSE-CD/config.json` | `815d6cec4ea0c9492db0b477af30397b92ce577f1823faf43b82d1e7acb2c22a` |
| `source:data/checkouts/ROSE-CD/enhancement.py` | `dc19589a8666246fa03d79e8298cd258849d6f07f477139bef778893c49d11ff` |
| `source:data/checkouts/ROSE-CD/requirements.txt` | `d5e64c3b28a8c184a1e8e2507e66d210f34602143a452ed8513778f903bc7c48` |
| `source:data/checkouts/ROSE-CD/scripts/eval_CT.sh` | `3e422ef8f5e8610def9ab59b530f1534cdad534b92b05d1fac946d08f81c069c` |
| `source:data/checkouts/ROSE-CD/sgmse/data_module.py` | `fbe913c9fad0b68bebe29058a6943b8115d74dfa2532e7856d890cd87987eb0b` |
| `source:data/checkouts/ROSE-CD/sgmse/model.py` | `1d6187c2997bf0e3184518dbd1c07c6704efa5d3ed50aff790495d4e13872237` |
| `source:data/checkouts/ROSE-CD/sgmse/util/other.py` | `092efb6e7da82d11c0afa555e5b124dd950e1216237e1c165a3aea8d4551ffd0` |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Boundary file | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

<!-- digest-table: external -->
| External identity | SHA-256 |
| --- | --- |
| `asset:checkpoint` | `5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4` |
| `asset:runtime_identity` | `746b4a28974916b88c3ec80f802b06414921774efb2c1ad0fc087bcaf4675697` |
<!-- digest-table: end -->

The absent checkpoint is **not** a file pin. Its ledger identity
(`data/models/rose-cd/last.ckpt`, 1,313,064,415 bytes, SHA-256
`5f4fcf08b4f751b1c6d5d7575522a633327302aee0de4613b45d98f7285637a4`) is recorded
in `report.json:asset_pins:asset:checkpoint` and `upstream`. Boundary pins cover
`CONTRACTS.md`, both public v0 headers, `CMakeLists.txt`, `REUSE.toml` and
`scripts/ci.py`; all are unchanged and machine-checked in `SOURCES.sha256`.
`asset:runtime_identity` is the digest of the declared runtime intent, not a
present environment.

### Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `70baa5ccfe13b02910d10e33bad7d88c7370d463888dd5869b908075377a2659` | 13650 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `3b83e633b6949aafcb87def2bf71bec1c41ae03bb02f02160a3581c47c0a5b32` | 62992 |
| `report.json` | `bc40973710ccd9d5e462ce20ebc75027a93d4effe72ce8de4ce54885bf854b90` | 18588 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `49bcd7179357b574f415d36ab64d0631194a4da1ec647884d30d3001001431ed` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `5f77a158d759c6aeb1f3c137459a99654a675e9b7315e76aec55356fe6331470` | 2010 |
| `test_reference.py` | `293ecdb6ddbea81713cd6561899b598010b28b5f0f681fb6c7ae81c187a44059` | 25335 |
| `verify.py` | `a1f6851def11d64576a0bb8873507e2543f36a51e5d8641463bc6696b8792b5f` | 21965 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduction

All outputs are task-local. `SOURCE_ROOT` is needed only by the verifier and
tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ROSE-CD-RMS-MATCHED
TASK=$WT/docs/task-evidence/rose-cd-rms-matched
PY=python3
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
python3 -m reuse lint
git diff --check
```

`run.py` builds the canonical report three times from a cold start and refuses
to write unless every payload is byte-identical.

## Expected counts and gates

- `test_reference.py`: deterministic checks, no skips, no network.
- `verify.py`: pin manifest, README digest tables, canonical JSON, sidecar,
  three-run reproduction, licensing, scope and strict-parser checks pass.
- Eight gates are blocked: exact model identity, runtime admission, artifact
  rights, exact reference parity, pinned RMS-matching recipe, rights-cleared
  real cohort, independent scoring/listening, and target-runtime timing plus
  opt-in provider intake.

Reopen only when a caller supplies the pinned checkpoint and source checkout
with matching hashes/revisions, PyTorch is reproduced in a hash-pinned isolated
environment, artifact and training-data rights are cleared, the exact
whole-clip RMS-matching recipe is approved, an approved reference vector is
reproduced, a rights-cleared paired real cohort is scored independently,
listening/scoring gates are met, target timing and memory are measured, and
opt-in provider intake plus a public default decision are recorded. Until then
the candidate stays DEFER, incomplete and not qualified.

## Separation from other ROSE-CD work

The sibling `SDK-ROSE-CD-ONE-STEP` task models the raw pinned one-step
checkpoint; this package models only its separate noisy-input RMS-matched
configuration and never pools raw and matched results. The research adapter and
reports are pinned external provenance; they were not executed, imported, pooled
or reinterpreted here.
