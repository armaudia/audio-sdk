<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DBLM-SE-1B - DBLM-SE-1B source, weights, toolchain and qualification blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DBLM-SE-1B` (`component_id=dblm-se-1b`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DBLM-SE-1B inference source, the 1B diffusion-bridge
language-model weights, the WavLM latent front-end, the XCodec2 tokenizer and
vocoder, the runtime, the adapter, immutable revisions, I/O geometry, diffusion
sampler configuration and numeric output are **absent**. This package records
that exact blocker, applies the Enhancement profile to a bounded deterministic
synthetic paired clean/noisy surrogate, and makes no noise-suppression,
generative-quality, PESQ, STOI, SI-SDR, WER, speaker-similarity, timing,
listening, benchmark or release claim. The surrogate is **not DBLM-SE-1B**: no
diffusion bridge, language model, WavLM latent, XCodec2 token, weight tensor,
sampler, native library, real audio, corpus, model or upstream code is present,
copied, downloaded, loaded, imported or executed. Only this task-local
directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=dblm-se-1b`) is `considered`,
`disposition=sdk-model`, `verification_profile=enhancement`. Its only evidence
link is `research/noise_suppression_candidate_census.md`. The pinned census row
says, verbatim:

> **DBLM-SE-1B** | 1B-parameter diffusion-bridge language model over WavLM
> latents to XCodec2 acoustic tokens | Official model card publishes
> Apache-2.0 safetensors and links the inference repository; training setup
> adds DNS-style noise and reverberation. | Research-only, high-compute speech
> restoration candidate. Include only as a separate noisy+reverberant
> generative stratum; verify code/checkpoint pin, hardware requirements and
> transcript/speaker fidelity.

Consequently:

- the census gives only a **description, an Apache-2.0 model-card claim and a
  link to an inference repository**; it records no repository URL, immutable
  commit, weight filename, component revision, byte count or SHA-256 for the
  source, the 1B LM, WavLM or XCodec2;
- no DBLM-SE-1B source, weight file, WavLM asset, XCodec2 asset, sampler, runtime
  or adapter is staged at `data/checkouts/dblm-se-1b`,
  `data/models/dblm-se-1b`, `data/envs/dblm-se-1b`,
  `adapters/dblm-se-1b` or `data/manifests/dblm-se-1b.json`;
- no input rate, channel layout, chunk/utterance geometry, hop, algorithmic
  latency, content delay, latent/token rate, diffusion step count, noise
  schedule, seed policy or streaming behavior is documented or asserted;
- no upstream LICENSE text, model-card copy, weight terms, training-data
  statement, notice bundle, attribution or product-use review is staged;
- no framework/runtime version, precision, accelerator class or peak-memory
  measurement exists; the census classifies the model as research-only and
  high-compute, beyond the current CPU-only worker as published;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  multi-asset model admission path;
- no rights-cleared paired clean/noisy cohort, noisy+reverberant stratum,
  transcript set, speaker labels, pinned scorer, established baseline,
  listening result or held-out split exists;
- no target-runtime pacing, content/availability timing, memory or independent
  review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DBLM-SE-1B`, `f9ad68b200026db72a8d2ec6d3625dd127f1d8ff` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/frame/latency/token-rate asserted |
| Candidate artifacts | absent; no source, LM/WavLM/XCodec2 weights, sampler or runtime |
| Surrogate | synthetic 16 kHz mono integer per-frame energy gate |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer per-frame energy gate: a 160-sample block
mean magnitude against a fixed fixture-tuned threshold of 900 Q15, gain 1000
per mille when at or above and 280 below, applied to the same block. It is **not
a network**, has no weights, no diffusion step, no latent and no token, and
cannot qualify the candidate. Its declared 160-sample block lookahead is a
fixture property only; it is not a candidate latency or delay claim.

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
| Task-matched held-out qualification | blocked | No rights-cleared held-out paired cohort, transcript/speaker labels, independent scorer or listening result |

Every paired, clean-preservation, peak, alignment, streaming and reset row is
`qualifies=false`. Synthetic exactness means only that the fixture is
self-consistent. The generative-fidelity row (`generative_fidelity`) is a
separate `blocked` subsection because the census specifically requires
transcript and speaker-fidelity checks; no WER or speaker-similarity value is
computed or fabricated.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  0.8 s fixture (12,800 samples).
- Six contiguous segments: `clean_only_initial` 0-2240 (speech, noise
  amplitude 6), `noisy_speech` 2240-4800 (speech, 2600),
  `noisy_speech_low_snr` 4800-7360 (speech, 3600),
  `speech_pause_noise_only` 7360-8640 (no speech, 900),
  `clean_only_final` 8640-9920 (speech, 6), `noisy_speech_restore` 9920-12800
  (speech, 3000).
- Clean reference: deterministic three-tone Q15 source with a frozen eight-frame
  syllable envelope (levels 0-3000); noise: deterministic LCG amplitudes scaled
  by the segment level; microphone: exact integer sum clamped to Q15.
- Surrogate: 160-sample block mean magnitude, fixed 900 threshold, gain
  1000/280 per mille, exact integer multiply/floor; state is 32 bytes.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 5346 / 5346 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 2386 / 2386 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 3988 / 3988 (delta 0) |
| Minimum / maximum surrogate SI-SDR | 2386 / 5346 |
| Mean delta SI-SDR | 0 |
| Clean-region SI-SDR, initial / final | 58203 / 58286 |
| Clean level change, both regions | 0 |
| Clean peak | 195 milli |
| Overall peak | 286 milli |
| Pause noise attenuation | 11056 milli |
| Alignment SI-SDR at 0 / -16 / +16 samples | 58203 / -11022 / -11061 |

All three noisy regions are exact identity because every block mean stays at or
above the fixed threshold; the gate therefore makes no change and reports delta
0. The positive pause attenuation comes only from gating synthetic noise-only
blocks below the threshold. These are fixture observations, not candidate
performance.

## Adverse, missing and invalid handling

`report.json` records 52 rejected inputs, each with the exact expected code, the
observed code and unchanged processing state. Rejections include duplicate JSON
key, `NaN`/`Infinity`/`-Infinity` constants, malformed JSON, a non-object JSON
root, missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame,
`int16`, clock drift, linear resampling, boolean/negative/oversized rate,
negative latency, missing input, short/long frame, zero/oversized valid count,
`NaN`/`Infinity`/`-Infinity` samples, out-of-range samples, nonzero padding,
string/boolean samples, epoch and input position mismatch, reset epoch
0/-1/non-increasing, negative reset position, and
missing/relative/bad-hash/wrong-rate/wrong-channel/wrong-frame/unknown-precision/extra-field
caller manifests, plus malformed fixture length/segment/noise specifications.
Missing real recordings, weights, runtime outputs, transcripts and labels are
`blocked`, never passes.

The caller asset contract validates identity and geometry only. It never reads,
loads, imports or executes a source tree, weight file, WavLM asset, XCodec2
asset or runtime. A hash-matched placeholder is never accepted as the pinned
DBLM-SE-1B artifact.

## Separation from sibling evidence

The merged `rnnoise-v0-2`, `gtcrn-dns3-offline`, `clearvoice-frcrn-16khz` and
`atennuate-0-1-1` packages are separate enhancement references with their own
assets, fixtures, metrics and dispositions; `cagcrn-joint-aec-and-ns` is a
separate joint AEC/NS blocker and `convfsenet` is a separate convolutional
enhancement blocker. This package does not import, pool, score or reuse their
source, fixtures, metrics or results. Their README/report files are pinned only
as read-only boundary references.

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
| `sdk:docs/task-evidence/atennuate-0-1-1/report.json` | `a9887810b173ae6f8b26c21412b273c90c964eb45e9536b90fd906f9cd44ffb1` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/README.md` | `aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7` |
| `sdk:docs/task-evidence/convfsenet/README.md` | `f0d09fa165d252d1e5e9b2e3fc8ec86aca1f05eb62a958bd4e991ee4de25ec5e` |
| `sdk:docs/task-evidence/convfsenet/report.json` | `c75931f774e45b7ba9837082366149eafc70ec4f24eb9532bda345b67e22e85e` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/dblm-se-1b/caller-supplied-asset/0.1` is modelled metadata only. The
required fields are `adapter`, `algorithmic_latency_samples`, `channels`,
`frame_samples`, `input_format`, `license_bundle_path`,
`license_bundle_sha256`, `lm_checkpoint_path`, `lm_checkpoint_sha256`,
`precision`, `runtime_library_path`, `runtime_library_sha256`,
`sample_rate_hz`, `source_commit`, `source_sha256`, `variant`,
`vocoder_checkpoint_path`, `vocoder_checkpoint_sha256`,
`wavlm_checkpoint_path` and `wavlm_checkpoint_sha256`. Absent artifacts are
rejected before processing; present artifacts would only be
identity/geometry-validated, never loaded or executed by this package.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DBLM-SE-1B/docs/task-evidence/dblm-se-1b
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --check
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DBLM-SE-1B diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned DBLM-SE-1B inference source, 1B diffusion-bridge LM
   weights, WavLM front-end and XCodec2 tokenizer/vocoder with immutable
   revisions, verified model-card lineage, license identity and an exact
   parameter/geometry record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible environment,
   verified component weight identity, frozen diffusion sampler/noise schedule
   and seed, component parity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and generated-output rights, verification
   of the census Apache-2.0 claim for the exact artifacts, attribution, notices,
   redistribution, product-use and derivative-output review.
4. `RG-04` SDK boundary admission: caller-supplied multi-asset identity,
   offline whole-clip versus frame-causal geometry, content delay and byte-level
   output parity.
5. `RG-05` rights-cleared task-matched held-out paired qualification with
   identity/noisy control, established baseline, paired SI-SDR and STOI,
   clean-speech preservation and peaks.
6. `RG-06` generative fidelity controls: transcript/ASR preservation (WER),
   speaker similarity and hallucination checks on a separate noisy and
   noisy+reverberant stratum.
7. `RG-07` target-device pacing, timing, availability, content delay, reset and
   memory for the exact high-compute runtime.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed DBLM-SE-1B inference source,
diffusion-bridge LM, WavLM front-end, XCodec2 tokenizer/vocoder and runtime with
immutable revisions and verified lineage, document the exact input/token
geometry and generation schedule, admit an isolated hash-pinned runtime, clear
code/weight/training-data/generated-output rights, map the multi-asset candidate
through the caller-supplied SDK boundary and reproduce exact output, run an
established baseline and paired SI-SDR/STOI plus clean-preservation and peak
qualification together with WER and speaker similarity on rights-cleared noisy
and noisy+reverberant held-out cohorts, measure availability/timing/memory at
the exact runtime and complete opt-in provider intake. Until then the candidate
stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-DBLM-SE-1B]`,
stable-field digest `e9bf47fba101ae2c4bdd1bd70318289d8840bb843be44074ae7746465924855e`);
the mutable full `plan/swarm/TASKS.json` is never hashed, pinned or used as a
digest source. No provider, descriptor, registry, installed default, shared
build or CI is changed.
