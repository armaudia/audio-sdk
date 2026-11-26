<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DEEPFILTERGAN - DeepFilterGAN source, checkpoints, runtime and qualification blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DeepFilterGAN` (`component_id=deepfiltergan`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DeepFilterGAN source tree, the predictive-stage and
GAN-stage checkpoints, the runtime, the adapter, immutable revisions, I/O
geometry, sampling configuration and numeric output are **absent**. This
package records that exact blocker, applies the Enhancement profile to a
bounded deterministic synthetic paired clean/noisy surrogate, and makes no
noise-suppression, PESQ, STOI, quality, timing, listening, benchmark or release
claim. The surrogate is not DeepFilterGAN: no deep-filter network, no GAN, no
weight tensor, no ONNX graph, no native library, no real audio, corpus, model or
upstream code is present, copied, downloaded, loaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=deepfiltergan`) is
`considered`, `disposition=sdk-model`, `verification_profile=enhancement`. Its
only evidence link is `research/noise_suppression_candidate_census.md`. The
pinned census row says, verbatim:

> **DeepFilterGAN** | Full-band predictive DeepFilterNet stage followed by GAN
> stochastic regeneration, intended to reduce over-suppression at real-time
> latency | Interspeech 2025 paper documents the two-stage design and real-time
> objective. A directly attributable public inference repo and released
> checkpoint were not located in this pass. | Research lead only until authors
> publish an attributable, reproducible checkpoint and usage terms. Do not
> substitute an unrelated DeepFilterNet checkpoint for the GAN stage.
> [Interspeech paper](https://www.isca-archive.org/interspeech_2025/serbest25_interspeech.pdf).

Consequently:

- the only provenance is an **Interspeech 2025 paper reference**; no upstream
  author repository, immutable commit, release revision, byte count or SHA-256
  exists for the source, either checkpoint or the runtime;
- no DeepFilterGAN source, predictive checkpoint, GAN checkpoint, adapter or
  runtime is staged at `data/checkouts/DeepFilterGAN`,
  `data/models/deepfiltergan`, `data/envs/deepfiltergan`,
  `adapters/deepfiltergan` or `data/manifests/deepfiltergan.json`;
- no input rate, hop, frame, channel layout, lookahead, output alignment,
  parameter count or sampling seed is documented or asserted;
- no upstream LICENSE text, model card copy, weight terms, training-data
  statement, notice bundle, attribution or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  model or caller-asset admission path;
- no rights-cleared paired clean/noisy cohort, pinned SI-SDR/STOI/PESQ scorer,
  established baseline, listening result or held-out split exists;
- no target-runtime pacing, regeneration repeatability, content/availability
  timing, memory or independent review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DEEPFILTERGAN`, `91c16ba867dd9cba8a41bd9202d00712d409277a` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/frame/latency asserted |
| Candidate artifacts | absent; no source, checkpoint or runtime |
| Surrogate | synthetic two-stage integer predictive/texture fixture |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer two-stage fixture. Stage one is a causal
per-frame mean-magnitude gate against a fixed fixture-tuned threshold of 900
Q15, with an instant-open and one-pole-closing gain (floor 300 per mille).
Stage two adds a deterministic `+/-1..2` Q15 texture only in attenuated blocks.
State is four 64-bit integers (32 bytes). It is **not a network**, has no
weights and cannot qualify the candidate. Its declared 160-sample block
lookahead is a fixture property only; it is not a candidate latency or delay
claim. The texture stage is a determinism/accounting stand-in for GAN
regeneration, never evidence for stochastic quality.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity/noisy control | synthetic only | Frozen synthetic noisy microphone plus authored clean Q15 reference; per-region identity/noisy SI-SDR and SNR |
| Established task-matched baseline | blocked | No baseline is pinned, licensed or run; sibling evidence is not reused |
| Paired SI-SDR | synthetic only | Exact integer SI-SDR in millidB against the authored synthetic clean reference only |
| Paired STOI | blocked | No pinned STOI scorer and no permitted rights-cleared clean references; not computed and not fabricated |
| Clean-speech preservation | synthetic only | SI-SDR, SNR, level change and peak on two synthetic near-clean regions |
| Peaks and invalid outputs | synthetic only | Peak bound, clamping and nonfinite-output counts on synthetic frames |
| Unpaired screen or listening | blocked | No predictive screen, authorized listening or rights-cleared unpaired speech |
| Alignment / content mapping | synthetic only | Declared 0 surrogate content delay with -16/-8/0/+8/+16 shift probes |
| Runtime availability timing | blocked | No exact runtime, device clock, deadline, availability or measured content delay |
| Streaming state and reset | synthetic only | Chunk invariance, reset to epoch 2 and a 137-sample final partial frame |
| Runtime memory | blocked | No measured runtime memory; only a declared 32-byte surrogate state |
| Task-matched held-out qualification | blocked | No rights-cleared held-out paired cohort, independent scorer or listening result |

Every paired, clean-preservation, peak, alignment, streaming and reset row is
`qualifies=false`. Synthetic exactness means only that the fixture is
self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  0.75 s fixture (12,000 samples).
- Six contiguous segments: `clean_only_initial` 0-2400 (speech, noise
  amplitude 8), `noisy_speech` 2400-4800 (speech, 900),
  `noisy_speech_low_snr` 4800-7200 (speech, 2400),
  `speech_pause_noise_only` 7200-8400 (no speech, 1200),
  `clean_only_final` 8400-9600 (speech, 8), `noisy_speech_restore` 9600-12000
  (speech, 1500).
- Clean reference: deterministic three-tone Q15 source with a frozen ten-frame
  syllable envelope (levels 0-3000); noise: deterministic LCG amplitudes scaled
  by the segment level; microphone: exact integer sum clamped to Q15.
- Surrogate: mean magnitude over the valid samples of each 160-sample block;
  threshold 900 Q15; gain 1000 above, one-pole closing toward 300 below; then a
  deterministic position-indexed texture of `+/-1..2` Q15 in attenuated blocks.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 13007 / 13838 (delta +831) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 5409 / 5409 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 9356 / 9780 (delta +424) |
| Minimum / maximum surrogate SI-SDR | 5409 / 13838 |
| Mean delta SI-SDR | +418 |
| Clean-region SI-SDR, initial / final | 55239 / 53697 |
| Clean level change, both regions | 0 |
| Clean peak | 226 milli |
| Overall peak | 298 milli |
| Pause noise attenuation | 6448 milli |
| Alignment SI-SDR at 0 / -16 / +16 samples | 55239 / -10875 / -10943 |

The positive deltas come only from gating synthetic silence blocks; the low-SNR
region shows no change because its noise block mean stays above the fixed
threshold. These are fixture observations, not candidate performance.

## Adverse, missing and invalid handling

`report.json` records 47 rejected inputs, each with the exact expected code, the
observed code and unchanged processing state. Rejections include duplicate JSON
key, `NaN`/`Infinity` constants, malformed JSON, missing/extra config fields,
8 kHz, 44.1 kHz, stereo, 256-sample frame, `int16`, clock drift, linear
resampling, boolean/negative/oversized rate, negative latency, missing input,
short/long frame, zero/oversized valid count, `NaN`/`Infinity` samples,
out-of-range samples, nonzero padding, string/boolean samples, epoch and input
position mismatch, reset epoch 0/-1/non-increasing, negative reset position,
and missing/relative/bad-hash/wrong-rate/wrong-channel/wrong-frame/unknown
artifact format/unknown precision/extra-field caller manifests, plus malformed
fixture length/segment/noise specifications. Missing real recordings,
checkpoints, runtime outputs and labels are `blocked`, never passes.

The caller asset contract validates identity and geometry only. It never reads,
loads, imports or executes a source tree, checkpoint file, ONNX graph or
runtime. A hash-matched placeholder is never accepted as the pinned
DeepFilterGAN artifact, and an unrelated DeepFilterNet checkpoint is never
substituted for the missing GAN stage.

## Separation from sibling evidence

The merged `deepfilternet3-local-listening-preset`, `clearvoice-mossformergan`,
`cmgan`, `rnnoise-v0-2`, `gtcrn-dns3-offline` and `clearvoice-frcrn-16khz`
packages are separate enhancement references or blockers with their own assets,
fixtures, metrics and dispositions. This package does not import, pool, score
or reuse their source, fixtures, metrics or results. Their README/report files
are pinned only as read-only boundary references. In particular, the sibling
DeepFilterNet evidence documents its own unresolved checkpoint terms and
contains no GAN stage; it is not a DeepFilterGAN artifact.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, two-stage integer surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
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
| `sdk:docs/task-evidence/rnnoise-v0-2/README.md` | `d9b83840d67862ab1a196e3096aab64f1d1bf83c18411a06c0c1d62142e1eb74` |
| `sdk:docs/task-evidence/rnnoise-v0-2/report.json` | `f635f1fcd7adbbc969ad99fe8445cb7188dcd733d3dcf1166a668de8b3085ec5` |
| `sdk:docs/task-evidence/gtcrn-dns3-offline/report.json` | `b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd` |
| `sdk:docs/task-evidence/clearvoice-frcrn-16khz/README.md` | `2ba56bbe54c825818143aa27859f2e001077bf0024932321a45e764fd40ef75d` |
| `sdk:docs/task-evidence/deepfilternet3-local-listening-preset/README.md` | `c512bae65ef489556555555e15e186c19dc027802701407525ce10fb675fd46d` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/README.md` | `4cce8370c8af8bd2a5a83f05bf15e540756f1f7d61f63170b6a9626f65d6bbce` |
| `sdk:docs/task-evidence/cmgan/README.md` | `31ad235dbd4d0d57b4e40a57629ee4fe94a19b00a174ec0ff8b78208c3f8cb05` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/deepfiltergan/caller-supplied-asset/0.1` is modelled metadata only.
The required fields are `adapter`, `algorithmic_latency_samples`,
`artifact_format` (`pytorch` or `onnx`), `channels`, `frame_samples`,
`input_format`, `library_path`, `library_sha256`, `model_path`, `model_sha256`,
`precision` (`fp32` or `int8`), `sample_rate_hz`, `source_commit`,
`source_sha256`, `variant` and `weights_sha256`. Absent artifacts are rejected
before processing; present artifacts would only be identity/geometry-validated,
never loaded or executed by this package.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DEEPFILTERGAN/docs/task-evidence/deepfiltergan
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DEEPFILTERGAN diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times in cold-start processes and compares the resulting
bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact attributable DeepFilterGAN inference repository and immutable
   revision with author identity, license identity and a complete notice
   bundle.
2. `RG-02` exact released predictive-stage and GAN-stage checkpoints with
   immutable revisions, byte counts, SHA-256 digests, model cards, a
   determinism/sampling statement and explicit non-substitution of the
   DeepFilterNet checkpoint.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review,
   including inherited DeepFilterNet terms.
4. `RG-04` isolated hash-pinned runtime admission with a reproducible build,
   verified weight identity, declared deterministic sampling seed and
   fail-closed absent behavior.
5. `RG-05` SDK boundary admission: caller-supplied asset identity, whole-clip
   versus frame-causal geometry, algorithmic latency, content delay and
   byte-level output parity.
6. `RG-06` rights-cleared task-matched held-out paired qualification with
   identity/noisy control, established baseline, paired SI-SDR and STOI,
   clean-speech preservation and peaks.
7. `RG-07` streaming state, reset, stochastic regeneration repeatability,
   nonfinite behavior, target-device pacing, timing and memory with independent
   listening and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Locate one attributable public DeepFilterGAN inference
repository and the exact released predictive and GAN checkpoints with immutable
revisions, byte counts, digest and deterministic sampling configuration,
document the exact geometry and training-data terms, admit an isolated
hash-pinned runtime, clear code/weight/training-data/corpus rights including
inherited DeepFilterNet terms, map the asset through the caller-supplied SDK
boundary and reproduce exact output, run an established baseline and paired
SI-SDR/STOI plus clean-preservation and peak qualification on a rights-cleared
task-matched held-out cohort, measure regeneration repeatability,
availability/timing/memory at the exact runtime and complete opt-in provider
intake. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-DEEPFILTERGAN]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
