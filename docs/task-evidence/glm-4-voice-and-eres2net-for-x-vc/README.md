<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-GLM-4-VOICE-AND-ERES2NET-FOR-X-VC — dependency and weight blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the GLM-4-Voice and ERes2Net for X-VC
row. It is **not** the X-VC pipeline: no X-VC checkpoint, GLM-4-Voice-Tokenizer
weight, ERes2Net weight, runtime, converted audio, real corpus read, listening
result, device measurement, benchmark or release claim is included. **No result
here qualifies the candidate.**

## Exact blocker: both dependency weights and the runtime are absent

The MIT **X-VC source checkout is present** at an exact revision. The X-VC
checkpoint, the GLM-4-Voice-Tokenizer weights, the ERes2Net weights and a
hash-pinned runtime are **absent**. Nothing was fabricated, reconstructed,
substituted or downloaded.

| Item | Status |
| --- | --- |
| X-VC source checkout | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/x-vc`, `Jerrister/X-VC` commit `49df8c591eafc48b096e466d96f9839f9c0dd739`, MIT, 82 non-`.git` files, working-tree digest `d0fad742b6eeb3cff3ddc644460bf69c48f14c41adea839b92f94912f78338f0` |
| GLM-4-Voice-Tokenizer | **Absent**: `zai-org/glm-4-voice-tokenizer` config, vocabulary/codebook and weight files; **no SHA-256 or byte count exists locally** |
| ERes2Net speaker encoder | **Absent**: `iic/speech_eres2net_sv_en_voxceleb_16k` `configuration.json` and the weight file it names; **no SHA-256 or byte count exists locally** |
| X-VC checkpoint | **Absent**: `chenxie95/X-VC` `ckpts/xvc.pt`; the pinned config declares `checkpoint: null`; **no SHA-256 or byte count exists locally** |
| Required runtime | **Absent/unpinned**: exact versions are declared, but no environment, lockfile or wheel set exists and no listed module is importable |
| Checkpoint/runtime memory | **Not measured**: the ledger reports a 5.01 GB checkpoint against an 8 GB host budget; joint checkpoint plus runtime memory was not measured here |
| Weight licence / asset rights | **Unresolved**: MIT covers the source checkout only; X-VC checkpoint, GLM-4-Voice and ERes2Net weight terms and the caller-supplied-asset use scope are not recorded |
| Historical X-VC run | **None**: the ledger says “Not downloaded” and “Blocked” |
| Workspace search | Bounded read-only checks found no `xvc.pt`, GLM-4-Voice tokenizer or ERes2Net weight file and no pinned runtime |
| Rights requirement | Reviewed weight terms for all three artifacts, MIT caller-supplied-asset obligations, corpus/training-data rights, source-speaker and target-voice consent, reference availability and output-use terms, all before any reproduction, adapter, timing run or release |

The linked ledger row
(`research/voice-conversion-eval-20261101/README.md`, line 20) says:

> | X-VC | Experimental zero-shot streaming VC | `repos/x-vc` | Not downloaded | Blocked | Official HF checkpoint is 5.01 GB and the pipeline also requires GLM-4-Voice and ERes2Net encoders; checkpoint alone exceeds this host's 8 GB memory budget. |

That is provenance text, not local availability evidence. The machine-readable
record is `report.json` → `upstream_blocker`
(`status="blocked_weights_and_runtime_absent"`,
`weights.x_vc_checkpoint.sha256=null`,
`weights.glm_4_voice_tokenizer.sha256=null`,
`weights.eres2net.sha256=null`, `runtime_digest=null`,
`checkpoint_memory.measured_here=false`, `no_upstream_parity_claim=true`), plus
`source_probe`, `weights_probe`, `runtime_probe`, `dependency_resolution` and
`historical_evidence`. `contract.json` carries the same blocker and all eight
blocked release gates.

Because all three weight artifacts and the runtime are missing, **no result
qualifies the candidate**, neither dependency is resolved, no provider is
registered, and release gate `RG-01` stays blocked.

## Exact dependency resolution

The pinned X-VC README requires both dependencies and the checkpoint. The
pinned config names both repositories explicitly.

| Dependency | Pinned locator | Role | Local status |
| --- | --- | --- | --- |
| GLM-4-Voice-Tokenizer | `zai-org/glm-4-voice-tokenizer` (`configs/xvc.yaml` → `semantic_encoder.encoder.from_pretrained.hf_repo`) | Semantic tokenization; declared 1280-wide feature interface | **`blocked_weights_absent`** |
| ERes2Net | `pretrained/speech_eres2net_sv_en_voxceleb_16k` (`configs/xvc.yaml` → `speaker_encoder.pretrained_dir`) | Speaker embedding; 80-bin fbank input, 192-dimensional output | **`blocked_weights_absent`** |
| X-VC checkpoint | `ckpts/xvc.pt` (`scripts/infer_single.sh`) | Streaming conversion model | **`blocked_weights_absent`** |

The request contract accepts **exactly** the ordered dependency list
`["glm-4-voice-tokenizer", "eres2net"]`. A missing, extra, reordered,
duplicated, non-string or unknown dependency is rejected before any candidate
call. A valid request still fails closed with
`SOURCE_WEIGHTS_RUNTIME_ABSENT`. There is no partial-dependency, placeholder or
surrogate path.

## Exact scope

- Work is confined to
  `docs/task-evidence/glm-4-voice-and-eres2net-for-x-vc/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  X-VC, tokenizer or speaker-encoder provider is installed or registered.
- There is no C provider, installed target or public API/ABI change. The exact
  pipeline needs caller-supplied weights and a heavy Python model runtime, so a
  truthful adapter cannot exist before the weight/runtime gates pass.
- No request is ever processed as X-VC. Valid requests fail closed with
  `SOURCE_WEIGHTS_RUNTIME_ABSENT`.
- Missing, invalid, nonfinite and out-of-range requests fail closed with no
  metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim and history never enter canonical bytes and are
  never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed** into
  any canonical artifact.

## Pinned declared geometry

`configs/xvc.yaml` declares 16 kHz input, `n_fft=1024`, `win_length=640`,
`hop_length=320`, `num_mels=128`, `latent_hop_length=1280`, acoustic encoder
rates `[2, 4, 5, 8]`, a 1280-wide semantic adapter input, a 192-dimensional
speaker predictor, and `checkpoint: null`. `scripts/infer_single.sh` declares
`ckpt="ckpts/xvc.pt"` and CLI defaults `current=00`, `chunk=2400`,
`future=100`, `smooth=20`.

| Field | Value | Derivation |
| --- | --- | --- |
| Input rate | 16 000 Hz | pinned config and v0 contract |
| Acoustic hop | 320 samples (20.0 ms) | product of `[2, 4, 5, 8]` and declared `hop_length` |
| Acoustic frame rate | 50 Hz | 16 000 / 320 arithmetic |
| Latent frame rate | 12.5 Hz | 16 000 / 1280 arithmetic |
| v0 frames per acoustic frame | 2 | 320 / 160 arithmetic |
| Semantic feature width | 1 280 | `semantic_adapter.input_channels` |
| Speaker embedding width | 192 | `speaker_predictor.output_dim` and `ERes2Net_VOX["embedding_size"]` |
| ERes2Net fbank bins | 80 | `ERes2Net_VOX["feat_dim"]` |
| Streaming chunk | 2 400 samples (150.0 ms) | declared `chunk` CLI default |
| Declared runtime pins | torch/torchaudio 2.5.1, transformers 4.44.1, numpy 1.26.4, soundfile 0.12.1, librosa 0.10.2, scipy 1.12.0 | `requirements.txt` |
| Checkpoint path | `ckpts/xvc.pt` | inference script |

These are arithmetic facts about the declared config, requirements and script,
**not** measurements. `geometry.measured_here=false` and
`geometry.candidate_output=false`. The CLI `future`/`smooth` semantics, true
streaming chunking, lookahead, content delay, alignment and tail behaviour are
not documented well enough to claim a mapping.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a model:

1. **Strict request validation** at the public v0 geometry. Exactly
   `candidate`, `sample_rate_hz`, `channels`, `frame_samples`, `samples`,
   `epoch`, `first_input_sample`, `lifecycle`, `execution_mode`,
   `target_condition` and `dependencies` are accepted. Unknown or missing
   fields, wrong geometry, wrong sample count, booleans, strings, nulls,
   nonfinite values, out-of-range values, negative epoch or position,
   closed/drained lifecycle, unknown modes, any concrete target condition and
   any deviation from the exact ordered dependency pair are rejected before any
   candidate call.
2. **Fail-closed candidate dispatch.** A valid request raises
   `CandidateAbsent`. There is no fallback tokenizer, speaker encoder, vocoder,
   checkpoint substitute or identity conversion.
3. **Exact source probe.** It recomputes the digest over every non-`.git` file
   in the pinned local checkout and checks the commit, file count and MIT
   licence pin. It never imports or executes upstream code.
4. **Three-artifact weights probe.** Bounded file, directory, cache and
   weight-filename checks for the X-VC checkpoint, GLM-4-Voice-Tokenizer and
   ERes2Net; no cache blob, archive or weight file is opened, no network is
   used and nothing is installed.
5. **Declared geometry.** It parses only the required fields from the pinned
   config, requirements and inference script, then checks them against the
   pinned digests and exact expected values.
6. **Generated harness stimuli** for silence, impulse, step, sweep and
   speech-like surrogates. Only peak, RMS, digest, finite counts and arithmetic
   320-sample framing are reported; no model is applied.
7. **Stable board identity** from the linked row only.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a model, implement a tokenizer, speaker encoder, vocoder or
transformer, run conversion, score content, identity or naturalness, or produce
audio.

## Historical evidence is not a local result

There is **no** historical X-VC execution in the workspace. The linked ledger
lists X-VC in its candidate table with “Not downloaded” and “Blocked”. The only
X-VC-adjacent numbers are source-reported ledger values:

| Field | Value | Local status |
| --- | --- | --- |
| Checkpoint size | 5.01 GB | source-reported only |
| Host memory budget | 8 GB | source-reported only |
| Joint checkpoint/runtime memory | unknown | **not measured** |
| Local X-VC output | none | **none** |
| ASR / WER | not scored | still not scored |
| Identity / naturalness | not scored | still not scored |
| Timing / RTF | none | **no local measurement** |

`report.json` therefore records
`historical_evidence.status="no_local_xvc_execution_record"`,
`records_found=0`, empty audio/metrics/transcript lists and
`timing=null`. No ledger, paper or sibling number is used as a local
measurement.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With all weights and the
runtime absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Permitted input and target reference scope | `blocked_no_source_target_pair_or_rights_record` |
| Task and language/speaker groups | `blocked_no_frozen_cohort_or_groups` |
| Text and semantic content | `blocked_no_model_transcript_or_cohort` |
| Identity / similarity | `blocked_not_scored` |
| Naturalness | `blocked_no_listening_or_mos` |
| Alignment, first output and tail timing | `blocked_no_documented_or_measured_timing` |
| Exact target condition | `blocked_no_documented_target_voice_or_condition` |
| Consent, reference availability and output use | `blocked_rights_and_consent_absent` |
| Paired quality control | `blocked_weights_and_runtime_absent` |
| Clean-reference preservation | `blocked_no_paired_clean_reference` |
| Numerical / nonfinite behaviour | `partial_local_harness_only` |
| GLM-4-Voice tokenizer resolution | `blocked_weights_absent` |
| ERes2Net resolution | `blocked_weights_absent` |
| Joint checkpoint/runtime memory | `blocked_not_measured` |
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
The “full frames” column is arithmetic floor division on the declared 320-
sample acoustic hop, not model output length.

Rejection evidence:

- 33 invalid request cases: all rejected, `metrics=null`, including 8 dependency
  cases (missing, extra, reordered, duplicate, unknown, non-list, non-string,
  empty);
- 7 invalid JSON cases (duplicate key, NaN, ±Infinity, trailing data, syntax,
  empty text): all rejected;
- 8 structural reset cases: match expectation, no candidate state owned;
- missing result: `status=blocked`, `metrics=null`,
  `qualifies_candidate=false`;
- harness identity control: byte-identical for every generated stimulus;
- valid X-VC request: rejected with `SOURCE_WEIGHTS_RUNTIME_ABSENT`;
- weights probe: all three artifacts absent; runtime probe: absent/unpinned;
- bounded weight-name search: 0 matches, not truncated; both dependency caches
  have no matching entry.

Every candidate row remains `blocked_weights_and_runtime_absent` with
`metrics=null`. There are no converted outputs, semantic scores, content
scores, quality scores, speaker similarity, naturalness, latency or device
claims.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact source and dependency weight pin | X-VC source is pinned; the X-VC checkpoint, GLM-4-Voice-Tokenizer weights and ERes2Net weights are absent with no SHA-256/byte count. |
| `RG-02` licence, rights and asset review | MIT source terms are recorded, but all three weight terms, caller-supplied-asset scope, corpus rights and voice consent are unresolved. |
| `RG-03` exact runtime build and install parity | Versions are declared but no environment, lockfile or wheel hashes exist and no listed module is importable. |
| `RG-04` dependency geometry, tokenizer, speaker, alignment and drain | No weight load; GLM-4-Voice tokenization, 1 280-wide semantic path, 192-dimensional ERes2Net embedding, 320-sample hop, chunking, state/reset, finite drain and mode ownership were not exercised. |
| `RG-05` rights-qualified cohort, content, identity and naturalness | No permitted cross-lingual cohort, transcript, target condition, matched control or score. |
| `RG-06` content preservation, adverse and nonfinite cases | No candidate output; silence, peaks, nonfinite, unfamiliar speech and language mismatch were not run through the exact pipeline. |
| `RG-07` checkpoint/runtime memory, timing and callback suitability | 5.01 GB vs 8 GB is a source report, not a local measurement; no paced device timing, first-output/tail, memory, listening or callback run exists. |
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
task-local merge-base git scope and blocker semantics. All must pass.

## Non-claims

No X-VC checkpoint, GLM-4-Voice-Tokenizer weight, ERes2Net weight, converted
audio, runtime, corpus, consent, listening panel, semantic/content score,
identity score, naturalness score, latency, callback, benchmark or release
claim is made. No installed v0, public API, C ABI, descriptor, registry,
default, shared build, CI, board or handoff change is made. Ledger-reported
values remain labelled with their original candidate-table scope.
