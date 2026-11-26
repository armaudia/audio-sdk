<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-HUBERT-CONVERSION-ENCODER — HuBERT conversion-encoder blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the `hubert-conversion-encoder` row. It
is **not** a HuBERT conversion encoder: no HuBERT weights, conversion
mapper/decoder, feature tensor, converted waveform, real corpus read, listening
result, device measurement, benchmark or release claim is included. **No result
here qualifies the encoder.**

## Exact blocker: weights, a conversion pipeline and the runtime are absent

A pinned downstream consumer checkout and the transformers-format HuBERT
**config** are present. The exact `pytorch_model.bin` weights, an end-to-end
content-to-target mapper/decoder checkpoint and a hash-pinned
PyTorch/Transformers runtime are **absent**. Nothing was fabricated,
reconstructed, substituted or downloaded.

| Item | Status |
| --- | --- |
| Consumer source | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/rvc`, RVC checkout at `81eed5e8f68b6bed1789f682fe78cdd324495afc`, MIT `LICENSE`, five per-file core pins plus two RVC-MLX declaration pins |
| HuBERT config | **Present and pinned**: `assets/hubert_base/config.json` and `preprocessor_config.json`; `HubertModelWithFinalProj`, 768 hidden, 12 layers, 320-sample stride, 256-wide projection. Both are **untracked** relative to the pinned commit and are pinned per file |
| Required encoder weights | **Absent**: `assets/hubert_base/pytorch_model.bin`; **no SHA-256 or byte count exists locally** |
| End-to-end conversion pipeline | **Absent**: no content-to-target mapper, no decoder/vocoder and no matched conversion checkpoint. A representation alone does not produce converted speech |
| Upstream HuBERT source | **Absent**: no `facebook/hubert-base-ls960` checkout, weight identity or upstream licence text is present |
| Required runtime | **Absent/unpinned**: `torch`, `torchaudio`, `transformers`, `numpy`, `soundfile` and `huggingface_hub` are not importable; no installed environment or lockfile exists |
| Weight / conversion-asset rights | **Unresolved**: MIT covers the pinned RVC consumer only; HuBERT upstream/weight terms, conversion-checkpoint terms, caller-supplied-asset use and input/derived-output rights are not recorded |
| Standalone result | **None**: the candidate matrix records HuBERT/WavLM-based conversion as unavailable/blocked; the transform report records HuBERT as "researched but not run"; no timing, feature, quality or audio result exists |
| Workspace search | Bounded read-only checks found the config and empty asset directories but **no** `pytorch_model.bin`, `.safetensors`, `hubert.npz`, `hubert_base.pt`, fairseq checkpoint, mapper or decoder/vocoder checkpoint |
| Rights requirement | Recorded upstream HuBERT source/weight terms, conversion-checkpoint terms, a caller-supplied-asset redistribution/use decision, permission for every input clip and derived feature or converted waveform, and consent for any target voice, all before any reproduction, adapter, timing run or release |

The pinned requirements text constrains `torch==2.4.1+cpu`,
`torchaudio==2.4.1+cpu` and `transformers>=4.49.0,<4.50`; the config declares
Transformers `4.49.0` and `torch_dtype` `float16`. A requirements text is not
an installed runtime, install digest or verified offline load path.

The machine-readable record is `report.json` → `upstream_blocker`
(`status="blocked_weights_runtime_and_conversion_pipeline_absent"`,
`weights.sha256=null`, `weights.byte_count=null`,
`conversion_pipeline.status="absent_no_end_to_end_mapper_decoder_or_checkpoint"`,
`runtime_digest=null`, `no_upstream_parity_claim=true`), plus `source_probe`,
`weights_probe`, `conversion_probe`, `runtime_probe` and
`historical_evidence`. `contract.json` carries the same blocker and all eight
blocked release gates.

Because the weights, the conversion pipeline and the runtime are missing, **no
result qualifies the conversion encoder**, no provider is registered, and
release gate `RG-01` stays blocked.

## Exact scope

- Work is confined to `docs/task-evidence/hubert-conversion-encoder/`. Shared
  CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, board/handoff files, CI, rulesets and `main` are
  untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  HuBERT provider is installed or registered.
- There is no C provider, installed target or public API/ABI change. The exact
  encoder needs caller-supplied weights, a matched conversion pipeline and a
  heavy Python model runtime, so a truthful adapter cannot exist before those
  gates pass.
- No request is ever processed as an encoder or converter. Valid requests fail
  closed with `WEIGHTS_ABSENT`.
- Missing, invalid, nonfinite and out-of-range requests fail closed with no
  metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim and history never enter canonical bytes and are
  never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed** into
  any canonical artifact.

## Pinned HuBERT geometry

Only static declarations from the pinned `config.json`,
`preprocessor_config.json` and `infer/hubert.py` are used. They are arithmetic
facts about a declared architecture, **not** measurements and **not** a model
output.

| Field | Value | Derivation |
| --- | --- | --- |
| Input rate | 16 000 Hz | preprocessor `sampling_rate` and v0 contract |
| Feature normalisation | off | preprocessor `do_normalize: false` |
| Convolution layers | 7 | config `num_feat_extract_layers` |
| Convolution width | 512 | config `conv_dim` |
| Convolution stride | `[5, 2, 2, 2, 2, 2, 2]` | config `conv_stride` |
| Content stride | 320 samples (20.0 ms) | product of strides |
| Content frame rate | 50 Hz | 16 000 / 320 |
| v0 frames per content frame | 2 | 320 / 160 |
| Convolutional receptive field | 400 samples (25.0 ms) | `1 + Σ (k−1)·Π(previous strides)` |
| Hidden width | 768 | config `hidden_size` |
| Encoder layers | 12 | config `num_hidden_layers` |
| Attention heads | 12 | config `num_attention_heads` |
| Feed-forward width | 3 072 | config `intermediate_size` |
| Final projection | 256 | config `classifier_proj_size` |
| v1 path | layer 9 → `final_proj` → 256 | pinned `infer/hubert.py` |
| v2 path | layer 12 `last_hidden_state` → 768 | pinned `infer/hubert.py` |
| Declared dtype | `float16` | config `torch_dtype` |
| Declared Transformers | `4.49.0` | config `transformers_version` |
| Declared conversion status | no end-to-end mapper/decoder/checkpoint | `conversion_probe` and candidate matrix |

`geometry.measured_here=false`, `geometry.representation_only=true` and
`geometry.produces_converted_audio=false`. No weight was loaded, no feature was
computed and no waveform was converted.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not an encoder:

1. **Strict request validation** at the public v0 geometry. Exactly
   `candidate`, `sample_rate_hz`, `channels`, `frame_samples`, `samples`,
   `epoch`, `first_input_sample`, `lifecycle`, `execution_mode` and
   `output_layer` are accepted. Unknown or missing fields, wrong geometry,
   wrong sample count, booleans, strings, nonfinite values, out-of-range
   values, negative epoch or position, closed/drained lifecycle, unknown modes
   and any layer other than 9 or 12 are rejected before any candidate call.
2. **Fail-closed candidate dispatch.** A valid request raises `WeightsAbsent`.
   There is no fallback encoder, surrogate feature extractor, mapper,
   decoder/vocoder or identity substitution. Layer 9 selects the declared
   256-wide `final_proj` path and layer 12 selects the declared 768-wide
   `last_hidden_state` path; neither path exists without weights, and neither
   is a conversion pipeline.
3. **Exact source probe.** It checks the pinned RVC revision, MIT licence text
   and per-file digests for the config, preprocessor config, loader,
   requirements and licence, plus the RVC-MLX declaration files. It never
   imports or executes upstream code. It also confirms the upstream HuBERT
   checkout is absent.
4. **Weights, conversion and runtime probes.** Bounded file, directory and
   module-name checks only; no cache blob, archive, weight file or checkpoint
   is opened, no network is used and nothing is installed.
5. **Config-derived geometry.** It parses the pinned JSON config, preprocessor
   config and loader declarations and re-checks the values against exact pins.
6. **Generated harness stimuli** for silence, impulse, step, sweep and
   speech-like surrogates. Only peak, RMS, digest, finite counts and
   arithmetic 320-sample stride framing are reported; no encoder is applied and
   no audio is converted.
7. **Stable board identity** from the linked row only.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a model, implement a convolutional or transformer
encoder, project final features, implement a mapper/decoder, score
content/semantic/conversion fidelity or produce audio.

## No historical candidate measurement exists

The only local HuBERT conversion statements are explicit non-results:

- `research/voice-enhancement-20261101/candidate_matrix.csv` records
  **HuBERT / WavLM-based conversion** as `unavailable/blocked`: “No end-to-end
  mapper/decoder or local conversion checkpoint; representations alone do not
  produce converted speech.”
- `research/voice-enhancement-20261101/agent-transform-space/REPORT.md`
  records HuBERT as “researched but not run”, with no local encoder or
  downstream VC benchmark, and requires a frozen encoder **plus** mapper and
  decoder/vocoder for a fair candidate.
- `research/accent-conversion-20261101/README.md` records **HuBERT / WavLM
  encoders** as content encoders, not accent converters, and not tested as
  standalone models.

The research voice-conversion README also reports an RVC whole-file pipeline
initialisation and timing. That is a **different system**; it is explicitly
excluded and is not attributed to this component. There is no HuBERT
conversion block, feature, timing, memory, first-output, tail, quality,
semantic, listening or converted-audio result to preserve.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the voice profile. With weights, a
conversion pipeline and the runtime absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Permitted input and target reference scope | `blocked_no_permitted_cohort_and_no_conversion_checkpoint` |
| Task and language/speaker groups | `blocked_not_tested` |
| Text and semantic content | `blocked_no_candidate_feature` |
| Identity / similarity | `not_applicable_encoder_only` |
| Naturalness | `not_applicable_encoder_only` |
| Alignment, first output and tail timing | `blocked_no_runtime_or_device_measurement` |
| Exact target condition | `blocked_no_conversion_checkpoint` |
| Consent, reference availability and output use | `blocked_no_corpus_or_asset_rights` |
| Paired quality control | `blocked_weights_runtime_and_conversion_pipeline_absent` |
| Clean-reference preservation | `blocked_no_candidate` |
| Numerical / nonfinite behaviour | `partial_local_harness_only` |
| Candidate output | `blocked_weights_runtime_and_conversion_pipeline_absent` |

## Deterministic local results (not candidate results)

Harness stimulus characterisation on generated 16 kHz samples:

| Stimulus | Samples | Full 320-sample frames | Peak | RMS | Nonfinite |
| --- | ---: | ---: | ---: | ---: | ---: |
| `silence` | 1 600 | 5 | 0.000000 | 0.000000 | 0 |
| `impulse` | 1 600 | 5 | 0.500000 | 0.012500 | 0 |
| `step` | 1 600 | 5 | 0.250000 | 0.176777 | 0 |
| `sweep` 200→3000 Hz | 1 600 | 5 | 0.300000 | 0.212109 | 0 |
| `speech_like` | 3 200 | 10 | 0.344139 | 0.146388 | 0 |

The speech-like surrogate has source-anchored voiced/pause RMS contrast
**49.35 dB**; this is a signal proxy, not intelligibility, MOS or listening.
The “full frames” column is arithmetic floor division on the declared stride,
not model output length.

Rejection evidence:

- 24 invalid request cases: all rejected, `metrics=null`;
- 6 invalid JSON cases (duplicate key, NaN, ±Infinity, trailing data, syntax):
  all rejected;
- missing result: `status=blocked`, `metrics=null`,
  `qualifies_candidate=false`;
- harness identity control: byte-identical for every generated stimulus;
- valid layer-9 and layer-12 requests: both rejected with `WEIGHTS_ABSENT`;
- weights probe: absent; conversion probe: absent; runtime probe:
  absent/unpinned.

Every candidate row remains
`blocked_weights_runtime_and_conversion_pipeline_absent` with `metrics=null`.
There are no HuBERT features, conversion scores, content scores, quality
scores, speaker similarity, naturalness, latency or device claims.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact source, config, weight and conversion-checkpoint pin | RVC consumer and HuBERT config are pinned; the encoder weights, an end-to-end conversion checkpoint and the upstream HuBERT weight identity are absent with no SHA-256/byte count. |
| `RG-02` licence, rights and asset review | The consumer source is MIT, but upstream HuBERT source/weight terms, conversion-checkpoint terms and caller-supplied-asset/corpus rights are unresolved. |
| `RG-03` exact runtime build and install parity | No PyTorch/Transformers environment is installed; requirements text is not an install digest or verified offline load path. |
| `RG-04` geometry, layer, delay, drain and mode parity | No weight load; 320-sample stride, 768-wide hidden state, layer-9 projection and layer-12 paths, delay, state/reset, finite drain and mode ownership were not exercised. |
| `RG-05` rights-qualified cohort and conversion/content fidelity | No end-to-end converter was run; no permitted cohort, paired reference features or conversion-fidelity score exists. |
| `RG-06` content preservation and adverse cases | No silence, clipping, nonfinite, unfamiliar-speech or adverse case was run through the exact encoder or conversion pipeline. |
| `RG-07` target-runtime timing, memory and callback suitability | There is no standalone HuBERT conversion-encoder timing or memory result; RVC pipeline timing is a different system and is excluded. |
| `RG-08` provider intake, public surface, review and release | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory:

```sh
python3 run.py --all
python3 test_reference.py
python3 verify.py
```

`run.py --verify-repro` regenerates every canonical byte in memory and compares
it with the committed files; `verify.py` additionally runs three cold-start
regenerations, checks strict JSON, exact pins, stable board identity, licensing,
task-local git scope and blocker semantics. All four must pass.

## Non-claims

No HuBERT config weight, conversion checkpoint, feature, waveform, runtime,
corpus, consent, listening panel, content/semantic/conversion score, latency,
callback, benchmark or release claim is made. No installed v0, public API, C
ABI, descriptor, registry, default, shared build, CI, board or handoff change is
made. The only numerical values are synthetic harness characterisation and
static architecture arithmetic; none qualifies the HuBERT conversion encoder.
