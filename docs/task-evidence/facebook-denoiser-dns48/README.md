<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FACEBOOK-DENOISER-DNS48 - Facebook Denoiser DNS48 source, weights, runtime and licence blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Facebook Denoiser DNS48` (`component_id=facebook-denoiser-dns48`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact Facebook Denoiser `dns48` source tree, pretrained weight file,
PyTorch inference runtime, adapter, immutable revisions, I/O geometry,
precision and numeric output are **absent**, and the pinned census records a
**CC-BY-NC 4.0 research-only** repository and model licence. This package
records those exact blockers, applies the Enhancement profile to a bounded
deterministic synthetic paired clean/noisy surrogate, and makes no
noise-suppression, PESQ, STOI, quality, timing, listening, benchmark, licence
or release claim. The surrogate is not Facebook Denoiser: no Demucs encoder or
decoder, convolution stack, learned layer, weight tensor, PyTorch graph, native
library, real audio, corpus, model or upstream code is present, copied,
downloaded, loaded, imported or executed. Only this task-local directory is
added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=facebook-denoiser-dns48`) is
`considered`, `disposition=sdk-model`, `verification_profile=enhancement`. Its
only evidence link is `research/noise_suppression_candidate_census.md`. The
pinned census row says, verbatim:

> **Facebook Denoiser DNS48 / DNS64** | Causal waveform Demucs models;
> streaming and higher-capacity references | Official archived repo supplies
> pretrained DNS models and streaming evaluation; repository/model license is
> CC-BY-NC 4.0. | Research-only comparator if license permits. Exclude from
> commercial selection; archived dependency stack and CPU RTF need checking.

Consequently:

- the census names an official archived repository, pretrained DNS models and a
  streaming evaluation path, but no immutable commit, release revision, byte
  count or SHA-256 exists for the source, `dns48` weights, PyTorch graph or
  runtime in this workspace;
- no Facebook Denoiser source, weight file, PyTorch graph, adapter or runtime is
  staged at `data/checkouts/facebook-denoiser-dns48`,
  `data/models/facebook-denoiser-dns48`,
  `data/envs/facebook-denoiser-dns48`, `adapters/facebook-denoiser-dns48` or
  `data/manifests/facebook-denoiser-dns48.json`;
- no input hop, frame, channel layout, hidden-channel width beyond the census
  "48" name, streaming boundary, output alignment, buffering, algorithmic
  latency, parameter count or precision is documented or asserted;
- the recorded CC-BY-NC 4.0 terms are non-commercial: no upstream LICENSE text,
  model card copy, weight terms, training-data or corpus statement, notice
  bundle, attribution, generated-output or product-use review is staged, and
  the census explicitly says to exclude the candidate from commercial
  selection;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  model or caller-asset admission path; the causal streaming model has no
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
| Branch and base | `swarm/SDK-FACEBOOK-DENOISER-DNS48`, `9cf118bc32ff5ac801318158d97d5bb8dd947374` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; only the census-reported causal Demucs family, 48 hidden channels, 16 kHz role and streaming evaluation |
| Candidate artefacts | absent; no source, `dns48` weights, PyTorch graph or runtime |
| Candidate rights | recorded `CC-BY-NC-4.0`, research-only; no licence text or grant staged |
| Surrogate | synthetic 16 kHz mono causal dual-window integer energy gate |
| Surrogate content delay / lookahead | 0 / 0 samples; frame-causal accounting only |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded causal integer frame gate: a 160-sample block is
split into two contiguous half-windows, the larger mean magnitude selects gain
1000 per mille at or above 700 Q15 and gain 250 below it, applied to the same
block. It is **not a network**, has no weights, is not Demucs and cannot qualify
the candidate. The census reports a causal streaming model, but no staged
runtime, frame geometry or reset contract exists; the surrogate's frame
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
| Streaming state and reset | blocked | The census reports streaming, but no candidate runtime, geometry, latency or reset contract is staged. Surrogate mechanics are not candidate streaming |
| Runtime memory | blocked | No measured runtime memory; only a declared 28-byte surrogate state |
| Task-matched held-out qualification | blocked | No rights-cleared held-out paired cohort, independent scorer, hallucination control or listening result |

Every paired, clean-preservation, peak and alignment row is `qualifies=false`.
Synthetic exactness means only that the fixture is self-consistent. Streaming
state and reset are `blocked` for the candidate even though the surrogate
exercises frame accounting.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  0.75 s fixture (12,000 samples).
- Six contiguous segments: `clean_only_initial` 0-2400 (speech, noise
  amplitude 10), `noisy_speech` 2400-4800 (speech, 700),
  `noisy_speech_low_snr` 4800-7200 (speech, 2600),
  `noise_only_pause` 7200-8400 (no speech, 1000), `clean_only_final`
  8400-9600 (speech, 10), `noisy_speech_restore` 9600-12000 (speech, 1600).
- Clean reference: deterministic three-tone Q15 source with a frozen ten-frame
  syllable envelope (levels 0-3000); noise: deterministic LCG amplitudes
  scaled by the segment level; microphone: exact integer sum clamped to Q15.
- Surrogate: two contiguous half-window mean magnitudes per 160-sample frame,
  fixed 700 threshold, gain 1000/250 per mille, exact integer multiply/floor;
  state is 28 bytes.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 15410 / 16753 (delta +1343) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 4604 / 4604 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 8853 / 8853 (delta 0) |
| Minimum / maximum surrogate SI-SDR | 4604 / 16753 |
| Mean delta SI-SDR | +447 |
| Clean-region SI-SDR, initial / final | 53305 / 52336 |
| Clean level change, initial / final | 0 / 1 |
| Clean peak | 226 milli |
| Overall peak | 296 milli |
| Pause noise attenuation | 8963 milli |
| Alignment SI-SDR at 0 samples | 53305 |
| Alignment SI-SDR at -16 / +16 samples | -10874 / -10942 |

The positive delta comes only from gating synthetic near-silent blocks; the
low-SNR and restore regions show no change because their noise block mean stays
above the fixed threshold. These are fixture observations, not candidate
performance.

## Adverse, missing and invalid handling

`report.json` records 51 rejected inputs, each with the exact expected code, the
observed code and unchanged processing state. Rejections include duplicate JSON
key, `NaN`/`Infinity` constants, malformed JSON, non-object JSON root,
missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame,
`int16`, clock drift, linear resampling, boolean/oversized rate, negative or
oversized latency, missing input, short/long frame, zero/oversized valid count,
`NaN`/`Infinity` samples, out-of-range samples, string/boolean samples, nonzero
padding, epoch and input position mismatch, reset epoch 0/equal/boolean,
negative reset position, and missing/extra/wrong-rate/wrong-channel/
wrong-frame/unknown artifact format/unknown precision/relative-path/bad-hash/
bad-commit caller manifests, plus commercial, product-distribution and missing
rights scopes and malformed fixture length/segment specifications. Missing real
recordings, weights, runtime outputs, rights and labels are `blocked`, never
passes.

Three valid controls are accepted deterministically: one silent frame, one
well-formed caller manifest (identity/geometry validation only, never loaded or
executed) and one research-evaluation use scope. The caller asset contract
validates identity and geometry only. It never reads, loads, imports or
executes a source tree, weight file, PyTorch graph or runtime. A hash-matched
placeholder is never accepted as the pinned Facebook Denoiser artifact. Only a
caller-owned PyTorch-format asset with declared precision is admitted by the
metadata schema; nothing is bundled. Any use scope other than
`research_evaluation` is rejected with `license_scope_not_permitted`.

## Separation from sibling evidence

The merged `rnnoise-v0-2`, `gtcrn-dns3-offline`, `dasheng-denoiser`,
`deepvqe-dns3-noise-suppression-configuration`, `clearvoice-frcrn-16khz`,
`atennuate-0-1-1`, `convfsenet` and `cof-denoising-checkpoints` packages are
separate enhancement references with their own assets, fixtures, metrics and
dispositions. This package does not import, pool, score or reuse their source,
fixtures, metrics or results. Their README/report files are pinned only as
read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, integer surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artefacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artefacts and the manifest. |

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
| `sdk:docs/task-evidence/dasheng-denoiser/report.json` | `cdb85350b4f5d6ccc771813f72be1291049397678151f572127e768297045984` |
| `sdk:docs/task-evidence/deepvqe-dns3-noise-suppression-configuration/report.json` | `b5c5eef3f22d39bf8ceea9a177b7d5d6b194ef21326a56742fe69c489e5b3455` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/facebook-denoiser-dns48/caller-supplied-asset/0.1` is modelled
metadata only. The required fields are `adapter`, `algorithmic_latency_samples`,
`artifact_format` (`pytorch`), `channels`, `frame_samples`, `input_format`,
`library_path`, `library_sha256`, `model_path`, `model_sha256`, `precision`
(`fp32`, `fp16` or `bf16`), `sample_rate_hz`, `source_commit`, `source_sha256`,
`variant` and `weights_sha256`. Absent artifacts are rejected before
processing; present artifacts would only be identity/geometry-validated, never
loaded or executed by this package.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FACEBOOK-DENOISER-DNS48/docs/task-evidence/facebook-denoiser-dns48
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FACEBOOK-DENOISER-DNS48 diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned Facebook Denoiser `dns48` source, pretrained weight file
   and PyTorch runtime with immutable revisions, verified archived-repository
   lineage, licence identity and an exact architecture/geometry record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible environment,
   verified weight identity, declared precision and fail-closed absent
   behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use, generated-output and derivative-output
   review under the recorded CC-BY-NC 4.0 research-only terms.
4. `RG-04` SDK boundary admission: caller-supplied asset identity, causal
   streaming versus frame-based geometry, content delay, buffering and
   byte-level output parity.
5. `RG-05` rights-cleared task-matched held-out paired qualification with
   identity/noisy control, established baseline, paired SI-SDR and STOI,
   clean-speech preservation, content faithfulness and peaks.
6. `RG-06` hallucination, insertion, deletion and nonfinite behavior at the
   exact runtime, including clean and noise-only controls.
7. `RG-07` target-device compute, pacing, memory, latency and throughput with
   independent listening and/or ASR content controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Replace the research-only blocker with an exact, legally
reviewed Facebook Denoiser `dns48` source/weight/runtime package whose terms
permit the intended distribution and product use, or obtain an explicit rights
decision; pin immutable revisions and digests, verify archived-repository
lineage, document the exact geometry, latency and framewise mapping, admit an
isolated hash-pinned runtime, map the asset through the caller-supplied SDK
boundary and reproduce exact output, run an established baseline and paired
SI-SDR/STOI plus clean-preservation, hallucination and peak qualification on a
rights-cleared task-matched held-out cohort, measure
compute/availability/memory at the exact runtime and complete opt-in provider
intake. Until then the candidate stays **DEFER**, **incomplete** and **not
qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-FACEBOOK-DENOISER-DNS48]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
