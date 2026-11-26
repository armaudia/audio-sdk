<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SEED-VC-XLS-R-300M-CONTENT-ENCODER — XLS-R-300M blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the Seed-VC XLS-R-300M content-encoder
row. It is **not** the encoder: no XLS-R-300M config, weights, feature tensor,
Seed-VC checkpoint, vocoder, real corpus read, listening result, device
measurement, benchmark or release claim is included. **No result here
qualifies the encoder.**

## Exact blocker: the encoder weights and pinned runtime are absent

The GPL-3.0 **source checkout is present** at an exact revision. The
`facebook/wav2vec2-xls-r-300m` encoder config and weights, and the historical
PyTorch/Transformers runtime, are **absent**. Nothing was fabricated,
reconstructed, substituted or downloaded.

| Item | Status |
| --- | --- |
| Source checkout | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/seed-vc`, `Plachtaa/seed-vc` commit `51383efd921027683c89e5348211d93ff12ac2a8`, GPL-3.0, 111 non-`.git` files, working-tree digest `e3a67ec3228aecb40ddeb5069eb6d1f6f237945f625a559736058546dcf8d3bf` |
| Required encoder weights | **Absent**: `facebook/wav2vec2-xls-r-300m` (`config.json`, `preprocessor_config.json`, `pytorch_model.bin` or `model.safetensors`); **no SHA-256 or byte count exists locally** |
| Required runtime | **Absent/unpinned**: no PyTorch, Transformers, NumPy or SoundFile runtime is importable; there is no hash-pinned lockfile or wheel set |
| Downstream Seed-VC checkpoint | **Absent**: `DiT_uvit_tat_xlsr_ema.pth` is named by the pinned preset but is not present and is not required for the encoder-alone probe |
| Weight licence / asset rights | **Unresolved**: GPL-3.0 covers the source checkout only; XLS-R-300M weight terms and the caller-supplied-asset redistribution/use scope are not recorded |
| Historical one-block run | One 240 ms output block, source-reported 254.01 s load, 22.21 s block time, 92.55× real time and 12.20 s semantic extraction; **not reproduced here** |
| Historical timing log | **Absent**: `results/seedvc-realtime.log` is referenced but missing; the output WAV is present and digest-pinned |
| Workspace search | Bounded read-only checks found the empty `hf-cache/` and `checkpoints/` directories but **no** XLS-R-300M config or weight file and no pinned runtime |
| Rights requirement | Recorded XLS-R-300M weight terms, an approved GPL-3.0 caller-supplied-asset decision, and permission for every input clip and derived feature/output, all before any reproduction, adapter, timing run or release |

The historical accent-conversion README says "the checkpoint bundle and
XLS-R-300M encoder were downloaded locally." No such weights remain in the
workspace, and no SHA-256 or byte count was ever recorded. That statement is
provenance text, not local availability evidence.

The machine-readable record is `report.json` → `upstream_blocker`
(`status="blocked_weights_and_runtime_absent"`, `weights.sha256=null`,
`weights.byte_count=null`, `runtime_digest=null`,
`no_upstream_parity_claim=true`), plus `source_probe`, `weights_probe`,
`runtime_probe` and `historical_evidence`. `contract.json` carries the same
blocker and all eight blocked release gates.

Because the encoder weights and runtime are missing, **no result qualifies the
content encoder**, no provider is registered, and release gate `RG-01` stays
blocked.

## Exact scope

- Work is confined to
  `docs/task-evidence/seed-vc-xls-r-300m-content-encoder/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  content-encoder provider is installed or registered.
- There is no C provider, installed target or public API/ABI change. The exact
  encoder needs caller-supplied weights and a heavy Python model runtime, so a
  truthful adapter cannot exist before the weights/runtime gates pass.
- No request is ever processed as an encoder. Valid requests fail closed with
  `WEIGHTS_ABSENT`.
- Missing, invalid, nonfinite and out-of-range requests fail closed with no
  metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim and history never enter canonical bytes and are
  never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed** into
  any canonical artifact.

## Pinned encoder geometry

The preset
`configs/presets/config_dit_mel_seed_uvit_xlsr_tiny.yml` selects
`speech_tokenizer.type: xlsr`,
`speech_tokenizer.name: facebook/wav2vec2-xls-r-300m` and
`speech_tokenizer.output_layer: 12`. Its length regulator declares
`in_channels: 1024` and `channels: 384` with sampling ratios `[1, 1, 1, 1]`;
the DiT declares `content_dim: 384` and `content_type: discrete`.

| Field | Value | Derivation |
| --- | --- | --- |
| Input rate | 16 000 Hz | v0 contract and `Wav2Vec2FeatureExtractor` call |
| Encoder stride | 320 samples (20.0 ms) | pinned one-block run script `block_frame_16k = 320 * return_length` |
| Content frame rate | 50 Hz | 16 000 / 320 arithmetic |
| v0 frames per content frame | 2 | 320 / 160 arithmetic |
| Truncated layer count | 12 | pinned preset `output_layer` |
| Hidden width | 1 024 | pinned preset length regulator `in_channels` |
| Content width | 384 | pinned preset `content_dim` / length regulator `channels` |
| One-block left context | 35 200 samples (2.2 s) | `skip_head=110` × 320 |
| One-block emit | 3 840 samples (0.24 s) | `return_length=12` × 320 |
| One-block right context | 3 200 samples (0.2 s) | `skip_tail=10` × 320 |
| Total context | 42 240 samples (2.64 s) | arithmetic sum |
| Diffusion steps | 10 | pinned run script |

These are arithmetic facts about the declared config and run script, **not
measurements**. `geometry.measured_here=false` and
`geometry.candidate_output=false`.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not an encoder:

1. **Strict request validation** at the public v0 geometry. Exactly
   `candidate`, `sample_rate_hz`, `channels`, `frame_samples`, `samples`,
   `epoch`, `first_input_sample`, `lifecycle`, `execution_mode` and
   `output_layer` are accepted. Unknown or missing fields, wrong geometry,
   wrong sample count, booleans, strings, nonfinite values, out-of-range
   values, negative epoch or position, closed/drained lifecycle, unknown
   modes and any layer other than 12 are rejected before any candidate call.
2. **Fail-closed candidate dispatch.** A valid request raises `WeightsAbsent`.
   There is no fallback encoder, surrogate feature extractor or identity
   substitution.
3. **Exact source probe.** It recomputes the digest over every non-`.git` file
   in the pinned local checkout and checks the commit, file count and GPL-3.0
   licence pin. It never imports or executes upstream code.
4. **Weights/runtime probes.** Bounded file, directory and module-name checks
   only; no cache blob, archive or weight file is opened, no network is used
   and nothing is installed.
5. **Config-derived geometry.** It parses only the required fields from the
   pinned YAML preset and the pinned one-block run script, then checks the
   values against the pinned digests.
6. **Generated harness stimuli** for silence, impulse, step, sweep and
   speech-like surrogates. Only peak, RMS, digest, finite counts and
   arithmetic 320-sample stride framing are reported; no encoder is applied.
7. **Stable board identity** from the linked row only.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a model, implement a convolutional or transformer
encoder, truncate layers, extract features, score semantic fidelity or produce
audio.

## Historical measurements are not local results

The only encoder-adjacent numbers in the workspace are *source-reported* by the
accent-conversion README for one first block of the generic streaming path.
They are pinned for provenance and reproduced as explicit source-reported
fields:

| Field | Historical value | Local status |
| --- | --- | --- |
| Blocks | 1 (240 ms emitted) | not re-run |
| Context | 2.2 s left, 0.2 s right, 10 diffusion steps | derived from pinned run script |
| Model load | 254.01 s | source-reported only |
| Block compute | 22.21 s | source-reported only |
| RTF | 92.55× real time | **not measured here** |
| Semantic extraction | 12.20 s | source-reported only; not separately profiled |
| Output | 22 050 Hz mono, 5 292 frames, 0.24 s | structural metadata of the pinned WAV only |
| ASR / WER | not scored | still not scored |
| Semantic fidelity | not scored | still not scored |
| Identity / naturalness | not scored | still not scored |
| Target | generic streaming VC, not the V2 accent-aware path | recorded |

Arithmetic on the source-reported values gives a 92.54× block RTF and a 4.62×
ratio of semantic extraction to the 2.64 s total context window. This is
arithmetic, not a new measurement. The historical output WAV is present and its
SHA-256 matches the pin; the timing log is absent. Neither artifact qualifies
the candidate.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the voice profile. With the encoder
weights and runtime absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Permitted input and target reference scope | `blocked_one_l2_arctic_clip_and_no_permitted_cohort` |
| Task and language/speaker groups | `blocked_one_arabic_l2_speaker_no_groups` |
| Text and semantic content | `blocked_one_short_block_not_asr_scored` |
| Identity / similarity | `not_applicable_encoder_only` |
| Naturalness | `not_applicable_encoder_only` |
| Alignment, first output and tail timing | `source_reported_block_only_not_device_measured` |
| Exact target condition | `recorded_generic_streaming_not_v2_accent_aware` |
| Consent, reference availability and output use | `blocked_corpus_and_asset_rights_unconfirmed` |
| Paired quality control | `blocked_weights_and_runtime_absent` |
| Clean-reference preservation | `blocked_no_paired_clean_reference` |
| Numerical / nonfinite behaviour | `partial_local_harness_only` |
| Candidate output | `blocked_weights_and_runtime_absent` |

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
The "full frames" column is arithmetic floor division on the declared stride,
not model output length.

Rejection evidence:

- 23 invalid request cases: all rejected, `metrics=null`;
- 6 invalid JSON cases (duplicate key, NaN, ±Infinity, trailing data, syntax):
  all rejected;
- missing result: `status=blocked`, `metrics=null`,
  `qualifies_candidate=false`;
- harness identity control: byte-identical for every generated stimulus;
- valid encoder request: rejected with `WEIGHTS_ABSENT`;
- weights probe: absent; runtime probe: absent/unpinned.

Every candidate row remains `blocked_weights_and_runtime_absent` with
`metrics=null`. There are no encoder features, semantic scores, content
scores, quality scores, speaker similarity, naturalness, latency or device
claims.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact source and encoder-weight pin | Seed-VC source is pinned; XLS-R-300M config and weights are absent with no SHA-256/byte count. |
| `RG-02` licence, rights and asset review | GPL-3.0 source terms are recorded, but XLS-R-300M weight terms and caller-supplied-asset/corpus rights are unresolved. |
| `RG-03` exact runtime build and install parity | The historical PyTorch/Transformers environment was removed; no lockfile or wheel hashes exist and the modules are not importable. |
| `RG-04` encoder geometry, layer, delay, drain and mode parity | No weight load; layer-12 truncation, 1 024-wide hidden state, 320-sample stride, state/reset, finite drain and mode ownership were not exercised. |
| `RG-05` rights-qualified cohort and semantic fidelity | Only one short historical block; no permitted cohort, paired reference features or semantic-fidelity score. |
| `RG-06` content preservation and adverse cases | The block is too short for ASR/WER; silence, peaks, nonfinite and unfamiliar speech were not run through the exact encoder. |
| `RG-07` target-runtime timing, memory and callback suitability | 12.20 s semantic extraction is a one-block source report, not a warmed-up paced device or callback measurement. |
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

No XLS-R-300M config, weights, feature, output, runtime, corpus, consent,
listening panel, semantic/content score, latency, callback, benchmark or
release claim is made. No installed v0, public API, C ABI, descriptor,
registry, default, shared build, CI, board or handoff change is made.
Historical values remain labeled with their original one-block scope.
