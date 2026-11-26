<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DEEPVQE-DNS3-NOISE-SUPPRESSION-CONFIGURATION - exact configuration blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the **DeepVQE DNS3 noise-suppression configuration**
(`component_id=deepvqe-dns3-noise-suppression-configuration`). The acceptance
profile is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DeepVQE source tree, public 16 kHz DNS3 checkpoint, the
NS-focused reproduction that removes the **far-end alignment block**, its
configuration/ablation record, runtime, adapter, immutable revisions, I/O
geometry and numeric output are **absent**. This package records that exact
blocker, applies the Enhancement profile to a bounded deterministic synthetic
paired clean/noisy surrogate, and makes no noise-suppression, DNSMOS, PESQ,
STOI, quality, timing, listening, benchmark or release claim. The surrogate is
**not DeepVQE** and is **not a complex-mask** network: no complex-mask U-Net,
far-end alignment block, learned filter, weight tensor, ONNX graph, native
library, real audio, corpus, model or upstream code is present, copied,
downloaded, loaded, imported or executed. Only this task-local directory is
added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=deepvqe-dns3-noise-suppression-configuration`) is `considered`, `disposition=sdk-model`,
`verification_profile=enhancement`. Its only evidence link is
`research/noise_suppression_candidate_census.md`. The pinned census row says,
verbatim:

> **DeepVQE DNS3 noise-suppression configuration** | Complex-mask U-Net,
> originally joint AEC/NS/dereverberation | Public 16 kHz DNS3 checkpoint and
> NS-focused reproduction remove the far-end alignment block; source reports
> DNSMOS-P.808 3.59 and RTF .2. | Medium priority joint-task model tested in
> NS-focused configuration; larger compute than DPCRN with only a small
> reported margin. Measure the exact ablation and verify terms.

Consequently:

- the census names a **public 16 kHz DNS3 checkpoint** but records no upstream
  repository URL, release, immutable commit, byte count or SHA-256 for the
  source or checkpoint;
- no DeepVQE source, checkpoint, NS-focused configuration, ablation patch,
  runtime, adapter or caller manifest is staged at
  `data/checkouts/DeepVQE`, `data/configs/deepvqe-dns3-ns`,
  `data/models/deepvqe-dns3`, `data/envs/deepvqe`, `adapters/deepvqe-dns3` or
  `data/manifests/deepvqe-dns3.json`;
- no hop, frame, channel layout, complex-mask shape, lookahead, output
  alignment or state geometry is documented or asserted beyond the census
  **16 kHz** statement;
- the exact NS-focused ablation is not specified: the census says only that a
  reproduction removes the far-end alignment block from the original joint
  AEC/NS/dereverberation model;
- no upstream LICENSE text, model-card copy, checkpoint-weight terms,
  training-data statement, notice bundle, attribution or product-use review is
  staged, and the census explicitly asks to **verify terms**;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  model, configuration or caller-asset admission path;
- no rights-cleared paired clean/noisy cohort, pinned SI-SDR/STOI/PESQ scorer,
  established baseline, listening result or held-out split exists;
- no target-runtime pacing, content/availability timing, memory or independent
  review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

### Adjacent LocalVQE derivative is not a substitute

A separate `LocalVQE` checkout is present at `data/checkouts/LocalVQE`
(Apache-2.0, commit `7f61cd05095d42e56a135b303f5bb4d761da22b9`). Its README
describes a streaming CPU-tuned **derivative of DeepVQE** that keeps a far-end
alignment block and requires a far-end reference for every published model
(`README.md` SHA-256
`2eeed279c971cce67f7897ae51bc9c8552c0e88bdd715d27520f956262d2423c`;
`pytorch/configs/default.yaml` SHA-256
`4b2f4ba474b9c76c5de8e95ff8fba3276847345b0d456b8401f4538b00be71f6`).
The census NS-focused reproduction instead removes that block. LocalVQE has no
published DeepVQE DNS3 checkpoint staged, is not the catalogued candidate and
was not used, scored or substituted. Its `ggml/tests/gtcrn/gtcrn_aec.gguf`
fixture is a different architecture and is not a DeepVQE weight.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DEEPVQE-DNS3-NOISE-SUPPRESSION-CONFIGURATION`, `91c16ba867dd9cba8a41bd9202d00712d409277a` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate architecture | complex-mask U-Net (census description, not verified) |
| Candidate original task | AEC + noise suppression + dereverberation |
| Claimed NS-focused change | remove the far-end alignment block (not reproduced) |
| Candidate rate | 16 kHz (census statement only) |
| Candidate hop/frame/channels/latency | not documented; not asserted |
| Candidate artifacts | absent; no source, checkpoint, configuration or runtime |
| Surrogate | synthetic 16 kHz mono integer block energy gate |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer per-block energy gate: a 160-sample block
mean magnitude against a fixed fixture-tuned threshold of 850 Q15, gain 1000
per mille when above and 280 below, applied to the same block. It is **not a
network**, has no weights, is not a complex mask and cannot qualify the
candidate. Its declared 160-sample block lookahead is a fixture property only;
it is not a candidate latency, delay or ablation claim.

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
| Alignment / content mapping | synthetic only | Declared 0 surrogate content delay with -16/-8/0/+8/+16 shift probes; no candidate ablation asserted |
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
  syllable envelope (levels 0-3000); noise: deterministic LCG (seed 20261127)
  amplitudes scaled by the segment level; microphone: exact integer sum
  clamped to Q15.
- Surrogate: 160-sample block mean magnitude, fixed 850 threshold, gain
  1000/280 per mille, exact integer multiply/floor; state is 32 bytes.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 13230 / 14547 (delta +1317) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 5295 / 5295 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 9416 / 9948 (delta +532) |
| Minimum / maximum surrogate SI-SDR | 5295 / 14547 |
| Mean delta SI-SDR | +616 |
| Clean-region SI-SDR, initial / final | 55215 / 54213 |
| Clean level change | 0 / +1 |
| Clean peak | 226 milli |
| Overall peak | 290 milli |
| Pause noise attenuation | 8484 milli |
| Alignment SI-SDR at 0 / -16 / +16 samples | 55215 / -10874 / -10942 |

The positive deltas come only from gating synthetic noise-only or low-level
blocks; the low-SNR region shows no change because its noise block mean stays
above the fixed threshold. These are fixture observations, not candidate
performance or configuration evidence.

## Adverse, missing and invalid handling

`report.json` records 53 rejected inputs, each with the exact expected code,
the observed code and unchanged processing state. Rejections include duplicate
JSON key, `NaN`/`Infinity` constants, malformed JSON, missing/extra config
fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame, `int16`, clock drift, linear
resampling, boolean/negative/oversized rate, negative latency, missing input,
short/long frame, zero/oversized valid count, `NaN`/`Infinity` samples,
out-of-range samples, nonzero padding, string/boolean samples, epoch and input
position mismatch, reset epoch 0/-1/non-increasing, negative reset position,
and missing/relative/bad-hash/wrong-rate/bool-rate/zero-channel/zero-frame/
zero-hop/oversized-hop/unknown artifact format/unknown precision/unknown
far-end mode/invalid configuration ID/extra-field caller manifests, plus
malformed fixture length/segment/noise specifications. Missing real
recordings, checkpoint, configuration, runtime outputs and labels are
`blocked`, never passes.

The caller asset contract validates identity, configuration ID, far-end mode
and declared geometry only. It never reads, loads, imports or executes a source
tree, checkpoint, configuration, ONNX graph or runtime. A hash-matched
placeholder is never accepted as the pinned DeepVQE DNS3 artifact.

## Separation from sibling evidence

The merged `rnnoise-v0-2`, `gtcrn-dns3-offline`, `dpdfnet-2-offline`,
`dpdfnet-baseline-offline`, `clearvoice-frcrn-16khz` and
`cagcrn-joint-aec-and-ns` packages are separate enhancement or joint-task
references with their own assets, fixtures, metrics and dispositions. This
package does not import, pool, score or reuse their source, fixtures, metrics
or results. Their README/report files are pinned only as read-only boundary
references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, integer surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
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
| Key | SHA-256 |
| --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
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
| `sdk:docs/task-evidence/dpdfnet-2-offline/report.json` | `b5ab66036c59e47799a8f0a089cacd524f9389ebaf26c29c22fb109fea7368ce` |
| `sdk:docs/task-evidence/dpdfnet-baseline-offline/report.json` | `6efa40dd8d98db63bd6f2d2c4063294227e365fee8b216301900eab455ff0940` |
| `sdk:docs/task-evidence/clearvoice-frcrn-16khz/README.md` | `2ba56bbe54c825818143aa27859f2e001077bf0024932321a45e764fd40ef75d` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/README.md` | `aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/deepvqe-dns3/caller-supplied-asset/0.1` is modelled metadata only.
The required fields are `adapter`, `algorithmic_latency_samples`,
`artifact_format` (`pytorch`, `onnx`, `gguf` or `native`), `channels`,
`configuration_id`, `far_end_mode` (`removed`, `bypass` or `required`),
`frame_samples`, `hop_samples`, `input_format`, `library_path`,
`library_sha256`, `model_path`, `model_sha256`, `precision` (`fp32`, `fp16`,
`bf16` or `int8`), `sample_rate_hz`, `source_commit`, `source_sha256`,
`variant` and `weights_sha256`. Absent artifacts are rejected before
processing; present artifacts would only be identity/configuration/geometry
validated, never loaded or executed by this package. The manifest records a
caller's declared geometry; it does not assert the missing DeepVQE DNS3
geometry or ablation.

## Reproduce

Run from this directory with a Python 3 interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DEEPVQE-DNS3-NOISE-SUPPRESSION-CONFIGURATION/docs/task-evidence/deepvqe-dns3-noise-suppression-configuration
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DEEPVQE-DNS3-NOISE-SUPPRESSION-CONFIGURATION diff --check
```

`run.py` builds the report, contract and manifest three times in one process
and refuses to write unless all payloads are byte-identical. External
reproduction runs `run.py` three times and compares the resulting bytes.

Scope verification compares the branch against the newest merge-base between
`HEAD` and `origin/main` (falling back to `main`), not a fixed historical
commit. Commits merged into `main` after this task therefore never count as
this branch's out-of-scope edits. Any committed or uncommitted path outside
`docs/task-evidence/deepvqe-dns3-noise-suppression-configuration/` still fails
as `base_out_of_scope_change`, and an unresolvable base ref fails closed as
`scope_base_unavailable`.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned DeepVQE source, public 16 kHz DNS3 checkpoint,
   NS-focused configuration and runtime with immutable revisions, verified
   lineage and an exact parameter/geometry record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build,
   checkpoint/configuration identity, joint-task versus NS-focused ablation
   parity and fail-closed absent behavior.
3. `RG-03` code, checkpoint-weight, training-data and corpus rights plus
   attribution, notices, redistribution, product-use and derivative-output
   review.
4. `RG-04` SDK boundary admission: caller-supplied asset and configuration
   identity, far-end block removal, mono versus multi-input geometry, content
   delay and byte-level output parity.
5. `RG-05` rights-cleared task-matched held-out paired qualification with
   identity/noisy control, established baseline, paired SI-SDR and STOI,
   clean-speech preservation and peaks.
6. `RG-06` streaming or whole-clip state, reset, latency, availability,
   content delay and nonfinite behavior at the exact runtime and configuration.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed DeepVQE source, public 16 kHz DNS3
checkpoint and runtime with immutable revisions and verified lineage; pin the
exact NS-focused configuration and far-end-alignment ablation; document the
resulting input, feature, complex-mask, hop, frame, lookahead and output
geometry; admit an isolated hash-pinned runtime; clear code, checkpoint-weight,
training-data and corpus rights; map the asset and configuration through the
caller-supplied SDK boundary and reproduce exact output; run an established
baseline and paired SI-SDR/STOI plus clean-preservation and peak qualification
on a rights-cleared task-matched held-out cohort; measure availability, timing
and memory at the exact runtime and complete opt-in provider intake. Until then
the candidate stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`. Installed v0 remains 16 kHz, mono, float32, 160
samples per frame. The board is referenced by stable linked-row fields only
(`tasks[id=SDK-DEEPVQE-DNS3-NOISE-SUPPRESSION-CONFIGURATION]`, stable-field
digest); the mutable full `plan/swarm/TASKS.json` is never hashed, pinned or
used as a digest source. No provider, descriptor, registry, installed default,
shared build or CI is changed.
