<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LLASE-G1 - LLaSE-G1 source, checkpoint, task and qualification blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LLaSE-G1` (`component_id=llase-g1`). The acceptance profile is **Enhancement**,
assigned by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`.
Decision: **DEFER**, recorded before `opt_in_adapter_exposure`;
`evidence_status=incomplete` and `qualification.status=not_qualified`. A
missing, blocked or rejected result may never qualify the candidate.

The exact licensed LLaSE-G1 inference source, the census-reported 16.1 GB
checkpoint, the WavLM feature front-end, the language model, the X-Codec2
tokenizer/vocoder, the runtime, the adapter, immutable revisions, I/O geometry,
the noise-suppression task condition and numeric output are **absent**. This
package records that exact blocker, applies the Enhancement profile to a bounded
deterministic synthetic paired clean/noisy surrogate, and makes no
noise-suppression, generative-quality, PESQ, STOI, SI-SDR, WER, speaker-
similarity, timing, listening, benchmark or release claim. The surrogate is
**not LLaSE-G1**: no token generator, language model, WavLM feature, X-Codec2
token, weight tensor, decoder, native library, real audio, corpus, model or
upstream code is present, copied, downloaded, loaded, imported or executed. Only
this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=llase-g1`) is `considered`,
`disposition=sdk-model`, `verification_profile=enhancement`. Its only evidence
link is `research/noise_suppression_candidate_census.md`. The pinned census row
says, verbatim:

> **LLaSE-G1** | Unified WavLM-feature to X-Codec2 token generator; explicit
> noise-suppression task alongside TSE/AEC/PLC/separation | Official model card
> declares Apache-2.0 and publishes a 16.1 GB checkpoint; inference requires
> WavLM features, the language model, and X-Codec2. | Valuable multi-task
> generative reference, but checkpoint/toolchain is beyond this host's
> practical CPU budget. Hold for supported accelerator and test NS as its own
> task. [Model card](https://huggingface.co/ASLP-lab/LLaSE-G1), [official
> implementation](https://github.com/Kevin-naticl/LLaSE-G1).

Consequently:

- the census gives only a **description, an Apache-2.0 model-card claim, a
  16.1 GB checkpoint size and two links**; it records no immutable commit,
  weight filename, per-asset byte count or SHA-256 for the source, the
  language model, WavLM or X-Codec2;
- no LLaSE-G1 source, checkpoint, WavLM asset, X-Codec2 asset, decoder, runtime
  or adapter is staged at `data/checkouts/llase-g1`,
  `data/models/llase-g1`, `data/envs/llase-g1`,
  `adapters/llase-g1` or `data/manifests/llase-g1.json`;
- no input rate, channel layout, chunk/utterance geometry, hop, algorithmic
  latency, content delay, feature/token rate, decoding policy, seed or streaming
  behavior is documented or asserted;
- the candidate is explicitly multi-task (noise suppression, TSE, AEC, PLC and
  separation), but no task condition, prompt or routing mechanism is documented,
  so no other-task result may be pooled into noise-suppression evidence;
- no upstream LICENSE text, model-card copy, checkpoint terms, training-data
  statement, notice bundle, attribution or product-use review is staged;
- no framework/runtime version, precision, accelerator class or peak-memory
  measurement exists; the census places the checkpoint/toolchain beyond this
  host's practical CPU budget and recommends a supported accelerator;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  multi-asset model admission path;
- no rights-cleared paired clean/noisy noise-suppression cohort, noisy+
  reverberant stratum, transcript set, speaker labels, pinned scorer,
  established baseline, listening result or held-out split exists;
- no target-runtime pacing, content/availability timing, memory or independent
  review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-LLASE-G1`, `b4960fdba1991a35c07ff7f22cda5257c4749768` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/frame/latency/token-rate asserted |
| Candidate artifacts | absent; no source, LM/WavLM/X-Codec2 assets, decoder or runtime |
| Candidate task | `noise_suppression` only; TSE/AEC/PLC/separation excluded |
| Surrogate | synthetic 16 kHz mono integer per-frame energy gate |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer per-frame energy gate: a 160-sample block
mean magnitude against a fixed fixture-tuned threshold of 900 Q15, gain 1000
per mille when at or above and 280 below, applied to the same block. It is **not
a network**, has no weights, no token generator, no language model, no WavLM
feature, no X-Codec2 token and no decoder, and cannot qualify the candidate. Its
declared 160-sample block lookahead is a fixture property only; it is not a
candidate latency or delay claim.

## Noise-suppression task isolation

LLaSE-G1 is reported as a unified multi-task generator. This package records:

- `candidate_task=noise_suppression`; the reported task list is TSE, AEC, PLC
  and separation as well, but only noise suppression is in scope;
- `task_conditioning_documented=false`: no prompt, control token, routing or
  configuration that selects the noise-suppression task is present;
- `noise_suppression_stratum_present=false`: no real noisy/clean noise-only
  cohort exists;
- `other_tasks_must_not_be_pooled=true` and `other_task_results_reused=false`.

No TSE, AEC, PLC or separation source, fixture, metric or result is imported,
pooled, scored or reinterpreted as LLaSE-G1 noise-suppression evidence.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity/noisy control | synthetic only | Frozen synthetic noisy microphone plus authored clean Q15 reference; per-region identity/noisy SI-SDR and SNR |
| Established task-matched baseline | blocked | No noise-suppression baseline is pinned, licensed or run; sibling and other-task evidence is not reused |
| Paired SI-SDR | synthetic only | Exact integer SI-SDR in millidB against the authored synthetic clean reference only |
| Paired STOI | blocked | No pinned STOI scorer and no permitted rights-cleared clean references; not computed and not fabricated |
| Clean-speech preservation | synthetic only | SI-SDR, SNR, level change and peak on two synthetic near-clean regions |
| Peaks and invalid outputs | synthetic only | Peak bound, clamping and nonfinite-output counts on synthetic frames |
| Unpaired screen or listening | blocked | No predictive screen, authorized listening or rights-cleared unpaired speech |
| Alignment / content mapping | synthetic only | Declared 0 surrogate content delay with -16/-8/0/+8/+16 shift probes |
| Runtime availability timing | blocked | No exact runtime, device clock, deadline, availability or measured content delay |
| Streaming state and reset | synthetic only | Chunk invariance, reset to epoch 2 and a 137-sample final partial frame |
| Runtime memory | blocked | No measured runtime memory; only a declared 32-byte surrogate state |
| Task-matched held-out qualification | blocked | No rights-cleared noise-suppression held-out paired cohort, independent scorer or listening result |

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
  syllable envelope (levels 0-3000); noise: deterministic LCG seed 20261126
  amplitudes scaled by the segment level; microphone: exact integer sum clamped
  to Q15.
- Surrogate: 160-sample block mean magnitude, fixed 900 threshold, gain
  1000/280 per mille, exact integer multiply/floor; state is 32 bytes.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Identity SI-SDR / surrogate, `noisy_speech` | 5051 / 5051 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_low_snr` | 2498 / 2498 (delta 0) |
| Identity SI-SDR / surrogate, `noisy_speech_restore` | 3806 / 3806 (delta 0) |
| Minimum / maximum surrogate SI-SDR | 2498 / 5051 |
| Mean delta SI-SDR | 0 |
| Clean-region SI-SDR, initial / final | 58526 / 58299 |
| Clean level change, initial / final | 0 / 1 |
| Clean peak | 195 milli |
| Overall peak | 289 milli |
| Pause noise attenuation | 11057 milli |
| Alignment SI-SDR at 0 / -16 / +16 samples | 58526 / -11023 / -11060 |

All three noisy regions are exact identity because every block mean stays at or
above the fixed threshold; the gate therefore makes no change and reports delta
0. The positive pause attenuation comes only from gating synthetic noise-only
blocks below the threshold. These are fixture observations, not candidate
performance.

## Adverse, missing and invalid handling

`report.json` records 55 rejected inputs, each with the exact expected code, the
observed code and unchanged processing state. Rejections include duplicate JSON
key, `NaN`/`Infinity`/`-Infinity` constants, malformed JSON, a non-object JSON
root, missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame,
`int16`, clock drift, linear resampling, boolean/negative/oversized rate,
negative latency, missing input, short/long frame, zero/oversized valid count,
`NaN`/`Infinity`/`-Infinity` samples, out-of-range samples, nonzero padding,
string/boolean samples, epoch and input position mismatch, reset epoch
0/-1/non-increasing, negative reset position, and
missing/relative/bad-hash/wrong-rate/wrong-channel/wrong-frame/unknown-precision/
unknown-task/extra-field caller manifests, plus malformed fixture
length/segment/noise specifications. Missing real recordings, checkpoints,
runtime outputs, transcripts and labels are `blocked`, never passes.

The caller asset contract validates identity, task and geometry only. It never
reads, loads, imports or executes a source tree, checkpoint, WavLM asset,
X-Codec2 asset or runtime. A hash-matched placeholder is never accepted as the
pinned LLaSE-G1 artifact.

## Separation from sibling evidence

The merged `dac-se1`, `dblm-se-1b`, `cisco-pase`, `cisco-stupase`,
`dasheng-denoiser` and `cof-denoising-checkpoints` packages are separate
generative-enhancement references with their own assets, fixtures, metrics and
dispositions. This package does not import, pool, score or reuse their source,
fixtures, metrics or results. Their report files are pinned only as read-only
boundary references. No compact, diffusion-bridge, flow-matching, codec-token,
PASE or other sibling result stands in for LLaSE-G1.

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
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:`-relative paths are relative to this SDK worktree. All are unchanged and
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
| `sdk:docs/task-evidence/dac-se1/report.json` | `e5e9aad4b1d3571a2fe190f7985d1d120091787cbcf5192fe5cb10a621706f9d` |
| `sdk:docs/task-evidence/dblm-se-1b/report.json` | `9cf30620583319a876c0ae584ab906ceeba49bf80287582d6eddb4b2d2bacc27` |
| `sdk:docs/task-evidence/cisco-pase/report.json` | `233f80869f079711baa637ca41c27483f029d513df4abd207c34c58124e7371c` |
| `sdk:docs/task-evidence/cisco-stupase/report.json` | `9cc6ba33224d2ba1340ff7f8ce2d8fbb62886fed366ddf9a6efeee8dcfb53dfc` |
| `sdk:docs/task-evidence/dasheng-denoiser/report.json` | `cdb85350b4f5d6ccc771813f72be1291049397678151f572127e768297045984` |
| `sdk:docs/task-evidence/cof-denoising-checkpoints/report.json` | `ff100450d2cabcddfd49c9d3c98ba06dfcc0c2191a71652ffb88485c44490e3a` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/llase-g1/caller-supplied-asset/0.1` is modelled metadata only. The
required fields are `adapter`, `algorithmic_latency_samples`, `channels`,
`frame_samples`, `input_format`, `license_bundle_path`,
`license_bundle_sha256`, `lm_checkpoint_path`, `lm_checkpoint_sha256`,
`precision`, `runtime_library_path`, `runtime_library_sha256`, `sample_rate_hz`,
`source_commit`, `source_sha256`, `task`, `variant`,
`wavlm_checkpoint_path`, `wavlm_checkpoint_sha256`,
`xcodec2_checkpoint_path` and `xcodec2_checkpoint_sha256`. Absent artifacts are
rejected before processing; present artifacts would only be identity, task and
geometry validated, never loaded or executed by this package. `task` must be
exactly `noise_suppression`.

## Reproduce

Run from this directory with a pinned Python 3 interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LLASE-G1/docs/task-evidence/llase-g1
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LLASE-G1 diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned LLaSE-G1 inference source, language-model checkpoint,
   WavLM feature front-end and X-Codec2 tokenizer/vocoder with immutable
   revisions, verified model-card lineage, license identity and an exact
   parameter/geometry record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible environment,
   verified component checkpoint identity, frozen decoding policy and seed, an
   explicit noise-suppression task condition, component parity and fail-closed
   absent behavior.
3. `RG-03` code, checkpoint, training-data and generated-output rights,
   verification of the census Apache-2.0 claim for the exact artifacts,
   attribution, notices, redistribution, product-use and derivative-output
   review.
4. `RG-04` SDK boundary admission: caller-supplied multi-asset identity,
   offline whole-clip versus frame-causal geometry, content delay, byte-level
   output parity and explicit noise-suppression-only task selection.
5. `RG-05` rights-cleared task-matched held-out paired noise-suppression
   qualification with identity/noisy control, an established baseline, paired
   SI-SDR and STOI, clean-speech preservation and peaks; TSE, AEC, PLC and
   separation results are never pooled into this task.
6. `RG-06` generative fidelity controls for the noise-suppression task:
   transcript/ASR preservation (WER), speaker similarity and hallucination
   checks on separate noisy and noisy+reverberant strata.
7. `RG-07` target-device pacing, timing, availability, content delay, reset and
   memory for the exact runtime carrying the census-reported 16.1 GB
   checkpoint.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed LLaSE-G1 inference source, language
model, WavLM feature front-end, X-Codec2 tokenizer/vocoder and runtime with
immutable revisions and verified lineage, document the exact input/token
geometry, task condition and decoding schedule, admit an isolated hash-pinned
runtime, clear code/checkpoint/training-data/generated-output rights, map the
multi-asset candidate through the caller-supplied SDK boundary and reproduce
exact output, run an established baseline and paired SI-SDR/STOI plus
clean-preservation and peak qualification together with WER and speaker
similarity on rights-cleared noise-suppression noisy and noisy+reverberant
held-out cohorts without pooling other tasks, measure availability/timing/memory
at the exact runtime and complete opt-in provider intake. Until then the
candidate stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-LLASE-G1]`, stable
digest `719b33953f35ac1f4d1efd1f91ca58389f30c0be04ef62d06893749581d76541`);
the mutable full `plan/swarm/TASKS.json` is never hashed, pinned or used as a
digest source. No provider, descriptor, registry, installed default, shared
build or CI is changed.
