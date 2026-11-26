<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DASHENG-DENOISER - Dasheng Denoiser source, weights, runtime and qualification blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Dasheng Denoiser` (`component_id=dasheng-denoiser`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed Dasheng source tree, 100M-parameter weight files, PyTorch
inference runtime, adapter, immutable revisions, I/O geometry, precision and
numeric output are **absent**. This package records that exact blocker, applies
the Enhancement profile to a bounded deterministic synthetic paired
clean/noisy surrogate, and makes no noise-suppression, PESQ, STOI, quality,
timing, listening, benchmark or release claim. The surrogate is not Dasheng:
no generative audio encoder, embedding module, learned layer, weight tensor,
PyTorch graph, native library, real audio, corpus, model or upstream code is
present, copied, downloaded, loaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=dasheng-denoiser`) is
`considered`, `disposition=sdk-model`, `verification_profile=enhancement`. Its
only evidence link is `research/noise_suppression_candidate_census.md`. The
pinned census row says, verbatim:

> **Dasheng Denoiser** | Generative-audio-encoder embedding denoiser, 16 kHz,
> offline quality candidate | Official Hugging Face PyTorch inference and
> 100M-param weights are published; code/checkpoint/data license and compute
> requirements need review. | Include if artifact terms permit. High-capacity
> model merits hallucination/content-preservation checks and CPU/GPU resource
> measurement.

Consequently:

- the census names an official Hugging Face model card and paper, but no
  immutable commit, release revision, byte count or SHA-256 exists for the
  source, weights, PyTorch graph or runtime in this workspace;
- no Dasheng source, weight file, PyTorch graph, adapter or runtime is staged
  at `data/checkouts/dasheng-denoiser`, `data/models/dasheng-denoiser`,
  `data/envs/dasheng-denoiser`, `adapters/dasheng-denoiser` or
  `data/manifests/dasheng-denoiser.json`;
- no input hop, frame, channel layout, offline boundary, output alignment,
  buffering or precision is documented or asserted;
- no upstream LICENSE text, model card copy, weight terms, training-data or
  corpus statement, notice bundle, attribution or product-use review is staged;
  the census explicitly leaves code/checkpoint/data licensing unresolved;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  model or caller-asset admission path; an offline whole-utterance model has no
  verified mapping onto that frame contract;
- no rights-cleared paired clean/noisy cohort, pinned SI-SDR/STOI/PESQ scorer,
  established baseline, hallucination control, listening result or held-out
  split exists;
- no target-runtime compute, pacing, content/availability timing, memory,
  nonfinite or independent review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DASHENG-DENOISER`, `f9ad68b200026db72a8d2ec6d3625dd127f1d8ff` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; only the census-reported 16 kHz offline role and 100M parameters |
| Candidate artifacts | absent; no source, weights, PyTorch graph or runtime |
| Surrogate | synthetic 16 kHz mono integer per-frame energy gate |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer per-frame energy gate: a 160-sample block
mean magnitude against a fixed fixture-tuned threshold of 900 Q15, gain 1000
per mille when above and 300 below, applied to the same block. It is **not a
network**, has no weights, is not generative and cannot qualify the candidate.
The candidate is an offline whole-utterance model; the surrogate's frame
mechanics are an accounting fixture only, not candidate streaming, latency or
framewise geometry.

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
| Streaming state and reset | blocked | Candidate is offline whole-utterance; no candidate streaming, reset or frame-causal contract. Surrogate mechanics are not candidate streaming |
| Runtime memory | blocked | No measured runtime memory; only a declared 32-byte surrogate state |
| Task-matched held-out qualification | blocked | No rights-cleared held-out paired cohort, independent scorer, hallucination control or listening result |

Every paired, clean-preservation, peak and alignment row is `qualifies=false`.
Synthetic exactness means only that the fixture is self-consistent. Streaming
state and reset are `blocked` for this offline candidate even though the
surrogate exercises frame accounting.

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
- Surrogate: 160-sample block mean magnitude, fixed 900 threshold, gain
  1000/300 per mille, exact integer multiply/floor; state is 32 bytes.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 13007 / 14180 (delta +1173) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 5409 / 5409 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 9356 / 9936 (delta +580) |
| Minimum / maximum surrogate SI-SDR | 5409 / 14180 |
| Mean delta SI-SDR | +584 |
| Clean-region SI-SDR, initial / final | 55391 / 54026 |
| Clean level change, both regions | 0 |
| Clean peak | 226 milli |
| Overall peak | 298 milli |
| Pause noise attenuation | 8220 milli |
| Alignment SI-SDR at 0 / -16 / +16 samples | 55391 / -10875 / -10943 |

The positive deltas come only from gating synthetic silence blocks; the
low-SNR region shows no change because its noise block mean stays above the
fixed threshold. These are fixture observations, not candidate performance.

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
fixture length/segment/noise specifications. Missing real recordings, weights,
runtime outputs and labels are `blocked`, never passes.

The caller asset contract validates identity and geometry only. It never reads,
loads, imports or executes a source tree, weight file, PyTorch graph or runtime.
A hash-matched placeholder is never accepted as the pinned Dasheng artifact.
Only a caller-owned PyTorch-format asset with declared precision is admitted by
the metadata schema; nothing is bundled.

## Separation from sibling evidence

The merged `rnnoise-v0-2`, `gtcrn-dns3-offline`, `clearvoice-frcrn-16khz`,
`atennuate-0-1-1`, `convfsenet` and `cof-denoising-checkpoints` packages are
separate enhancement references with their own assets, fixtures, metrics and
dispositions; `cagcrn-joint-aec-and-ns` is a separate joint AEC/NS blocker.
This package does not import, pool, score or reuse their source, fixtures,
metrics or results. Their README/report files are pinned only as read-only
boundary references.

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
| `sdk:docs/task-evidence/convfsenet/report.json` | `c75931f774e45b7ba9837082366149eafc70ec4f24eb9532bda345b67e22e85e` |
| `sdk:docs/task-evidence/cof-denoising-checkpoints/report.json` | `ff100450d2cabcddfd49c9d3c98ba06dfcc0c2191a71652ffb88485c44490e3a` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/dasheng-denoiser/caller-supplied-asset/0.1` is modelled metadata
only. The required fields are `adapter`, `algorithmic_latency_samples`,
`artifact_format` (`pytorch`), `channels`, `frame_samples`, `input_format`,
`library_path`, `library_sha256`, `model_path`, `model_sha256`, `precision`
(`fp32`, `fp16` or `bf16`), `sample_rate_hz`, `source_commit`, `source_sha256`,
`variant` and `weights_sha256`. Absent artifacts are rejected before
processing; present artifacts would only be identity/geometry-validated, never
loaded or executed by this package.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DASHENG-DENOISER/docs/task-evidence/dasheng-denoiser
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DASHENG-DENOISER diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned Dasheng source, 100M-parameter weight files and
   PyTorch runtime with immutable revisions, verified model-card/paper lineage,
   license identity and an exact architecture/geometry/precision record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible environment,
   verified weight identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, generated-output, product-use and derivative-output
   review.
4. `RG-04` SDK boundary admission: caller-supplied asset identity, offline
   whole-utterance versus frame-based geometry, content delay, buffering and
   byte-level output parity.
5. `RG-05` rights-cleared task-matched held-out paired qualification with
   identity/noisy control, established baseline, paired SI-SDR and STOI,
   clean-speech preservation, content faithfulness and peaks.
6. `RG-06` hallucination, insertion, deletion and nonfinite behavior at the
   exact runtime, including clean and noise-only controls.
7. `RG-07` target-device compute, pacing, memory and throughput with independent
   listening and/or ASR content controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed Dasheng source, 100M-parameter
weights and PyTorch runtime with immutable revisions and verified lineage,
document the exact offline geometry and framewise mapping, admit an isolated
hash-pinned runtime, clear code/weight/training-data/corpus rights, map the
asset through the caller-supplied SDK boundary and reproduce exact output, run
an established baseline and paired SI-SDR/STOI plus clean-preservation,
hallucination and peak qualification on a rights-cleared task-matched held-out
cohort, measure compute/availability/memory at the exact runtime and complete
opt-in provider intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-DASHENG-DENOISER]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
