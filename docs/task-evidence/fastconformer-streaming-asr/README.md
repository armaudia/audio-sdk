<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FASTCONFORMER-STREAMING-ASR — streaming-ASR readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`FastConformer streaming ASR` (`component_id=fastconformer-streaming-asr`). The
acceptance profile is **Rate**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation,
provider intake or release step; `status=proposal_only_synthetic_incomplete`,
`evidence_status=incomplete`, `qualification.status=not_qualified`. A missing
result never qualifies the candidate.

This package does **not** contain, import, build, link, download, load or
execute FastConformer, Conformer-TED, NeMo, PyTorch, CUDA, ONNX Runtime, a
tokenizer, a checkpoint, weights, real audio, a transcript or any inference
path. It records the exact missing artifacts and rights requirements, pins the
research/plan inputs by whole-file SHA-256, probes fixed workspace/temporary
paths to evidence absence, defines a fail-closed admission boundary for a
future exact candidate manifest, and runs a deterministic stdlib **scheduler
surrogate** that models only frame/chunk accounting. The surrogate performs no
feature extraction, encoding, decoding, token emission or recognition.

Only `docs/task-evidence/fastconformer-streaming-asr/` is written. No provider,
registry, descriptor, public header/ABI, shared CMake/CI, installed default,
board or handoff file changes.

## Exact external blocker

The pinned candidate record is row **35** of
`research/voice-enhancement-20261101/candidate_matrix.csv`:

| Field | Recorded value |
| --- | --- |
| Candidate | `Streaming Conformer-TED / FastConformer` |
| Status | `unavailable/blocked` |
| Finding | No exact TED checkpoint, streaming config or local ASR runtime; using another Conformer would change candidate identity. |
| Baseline | Whisper streaming ASR; fixed transcript |
| Reports | `agent-vad-asr-trials/REPORT.md`; `agent-segmentation/REPORT.md` |

The second report describes a **current concrete analogue** (NVIDIA NeMo
cache-aware streaming FastConformer/RNNT) with source-reported 16 ms transport
frames, 80 ms inference chunks, a persistent encoder cache and GPU-local
operation. That analogue is **not** the candidate and is not substituted. The
label remains underspecified until one exact checkpoint, config, tokenizer and
source revision are named.

Six exact blockers are open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | An exact streaming FastConformer/Conformer-TED model ID, architecture config, tokenizer, decoding configuration and immutable 40-hex source revision. The family label and NeMo analogue do not satisfy identity. |
| `BLK-02` | Every checkpoint/tokenizer/config byte with byte count and SHA-256 under an immutable artifact revision, plus a digest-verified model card and license/notice bundle. No candidate bytes exist in this worktree. |
| `BLK-03` | A pinned NeMo or other exact ASR runtime artifact with a recorded digest, CUDA/cuDNN/GPU declaration, deterministic settings and a clean-room offline load trace. No `nemo`/`nemo_toolkit` module or CUDA runtime is present. |
| `BLK-04` | Written weight, source, training-data, corpus, output-use and redistribution decisions with an independent rights/legal review. An SPDX label alone is not clearance. |
| `BLK-05` | A rights-cleared real speech cohort with verified transcripts, speaker/meeting split, channel/rate mapping and an independent reference whose limits are recorded. Synthetic scheduler events are not a corpus or a transcript. |
| `BLK-06` | Reproduced WER, RTF, end-to-end streaming latency, endpoint and partial-hypothesis behavior, finite-output and adverse controls, target-device p50/p95/p99 timing/resources, listening permission and Rate-profile evidence (or a reviewed waiver). |

**Reopen condition.** Admit the candidate only when one exact candidate is
named with immutable source/checkpoint/tokenizer/config bytes and verified
digests; a pinned offline runtime with CUDA/device requirements loads the bytes;
written rights and output-use terms are approved; a rights-cleared cohort,
transcripts and independent reference exist; WER/streaming latency/endpoint/
finite-output and matched controls are reproduced; target-device timing is
measured; Rate evidence or a reviewed waiver exists; and a separate
OFF-by-default opt-in intake passes independent exact-head review. Until then
all **eight** release gates stay `blocked` and the package remains
`DEFER` / `not_qualified`.

The same blocker text is duplicated in `contract.json:exact_blockers` and
`report.json:exact_blockers`.

## Boundary and geometry

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `processor_exposure=false`.
- No external asset is admitted. `CONTRACTS.md` `as_asset_v0` would require an
  asset ID, byte count, SHA-256 and `storage=external` from the caller, with no
  provider file access or download. No such asset exists for this candidate.
- The mutable shared board is **not** pinned. Only the stable projection
  `id,title,component,mode,repository,depends_on` gates anything; `status`,
  `owner`, `claim`, `review`, `handoff`, `blocked_reason` and
  `dispatch_priority` are excluded from canonical bytes.

## What the scheduler surrogate does and does not do

The executable control is a deterministic 16 kHz, mono, `f32` scheduler:

- Caller samples are validated and buffered into 1280-sample (80 ms) chunks
  over 160-sample (10 ms) frames. A partial final chunk is emitted only on an
  explicit `flush`; its written schedule is zero-padded but the padding is
  counted as `internal_padding_samples` and never claimed as audio.
- Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280, 32000` produce **identical**
  structural event digests for a 32,000-sample synthetic stream. Caller
  chunking does not move the modelled event boundaries.
- One `reset` clears buffer, counters, cache and events and increments the
  cache epoch; replay is structurally identical. `flush` is idempotent, a
  second flush is empty, and `close` is idempotent. Push after flush, or any
  operation after close, is rejected.
- Empty/wrong types, booleans, NaN, infinity, out-of-range samples and invalid
  geometry are rejected before state advances.

**It is not ASR.** It has no model, weights, feature front end, encoder,
decoder, tokenizer, vocabulary, transcript, WER, endpoint decision or latency
measurement. It substitutes for no candidate result.

### Synthetic scheduler results (not a candidate result)

| Condition | Input samples | Completed 80 ms chunks | Final partial chunk | Padding samples | Valid source samples |
| --- | ---: | ---: | ---: | ---: | ---: |
| `SIL-32000` | 32000 | 25 | 0 | 0 | 32000 |
| `RAMP-32000` | 32000 | 25 | 0 | 0 | 32000 |
| `IMP-32000` | 32000 | 25 | 0 | 0 | 32000 |
| `PARTIAL-32037` | 32037 | 25 | 1 (37 real) | 1243 | 32037 |

Nine chunk sizes over 32,000 samples produce one digest and **37,699** caller
chunks total. These are scheduling counts only; no audio or recognition output
exists.

## Fail-closed admission and adverse controls

A future candidate manifest has seven exact top-level sections: `candidate`,
`runtime`, `streaming`, `assets`, `evaluation`, `provider` and `schema_id`.
Admission requires an exact non-family candidate ID, 40-hex immutable source
revision, non-zero checkpoint files with byte counts and 64-hex digests, reviewed
redistribution/output-use terms, an offline runtime artifact digest, external
caller-owned assets with no download, reviewed corpus/transcript/reference
rights and listening permission, and `registered=false` /
`default_selected=false` / `opt_in=true`.

Twenty-five adverse mutations are rejected with a stable code and unchanged
state: wrong schema/family, family-only ID, mutable/short revision, missing/
duplicate checkpoint, bad digest, zero/boolean bytes, unreviewed terms,
forbidden redistribution or output use, online runtime, unknown runtime digest,
download permitted, embedded storage, unreviewed corpus, no listening
permission, missing transcript, registered/default provider, nonfinite/boolean
chunk and negative lookahead. A schema-only control is accepted to prove the
branch, but is explicitly **not the candidate** and `qualifies=false`.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, exact blockers, surrogate, pins, commands, gates. |
| `contract.json` | Task-local contract, eight blocked gates, seven artifacts, six blockers. |
| `reference.py` | Deterministic scheduler surrogate, admission validator, canonical report. |
| `report.json` / `report.json.sha256` | Canonical Rate report and its digest sidecar. |
| `run.py` | Regenerates `contract.json`, `report.json`, sidecar and `SOURCES.sha256` 3x. |
| `test_reference.py` | Deterministic stdlib unittest checks; no network, skips or assets. |
| `verify.py` | Read-only pins, strict JSON, disposition, licensing, scope and cold-start verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `LICENSES.md` | Licensing statement; no upstream bytes are vendored. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned inputs

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c…` | Candidate row 35, blocked status and identity finding. |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f…` | No exact checkpoint or runtime finding. |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d…` | NeMo analogue context and identity warning. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fb…` | ASR/streaming candidate context. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | Component/profile assignment. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f263133…` | Rate acceptance profile. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50…` | SDK dispatch and build guidance. |
| `worktree:CONTRACTS.md` | `f6fdd18f…` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965a…` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74…` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc9…` | `docs/**` Apache-2.0 annotation. |
| `worktree:CMakeLists.txt` | `af72dba5…` | Unchanged shared build. |
| `worktree:docs/task-evidence/whisper-tiny-en-mfa/contract.json` | `fddc819b…` | Merged sibling ASR-rate DEFER pattern. |
| `worktree:docs/task-evidence/dpdfnet-2-streaming/contract.json` | `225e0072…` | Merged sibling streaming-blocker pattern. |
| `worktree:docs/task-evidence/asr-word-timestamps/contract.json` | `65361e29…` | Merged sibling ASR gate pattern. |

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FASTCONFORMER-STREAMING-ASR diff --check
```

`run.py --all` regenerates the contract, report, digest sidecar and source
manifest. `report.json` is canonical JSON (`sort_keys=True`, compact
separators, `allow_nan=False`, no floats) plus one trailing newline.
Regeneration and three cold-start interpreter processes are byte-identical.

## Expected counts and digests

- Four synthetic conditions; 128,037 synthetic samples total; 101 scheduler
  events over the four conditions.
- Nine chunk sizes plus the 32,000-sample whole-call control; **37,699** caller
  chunks in the boundary record (chunk size 1 contributes 32,000 calls).
- `report.json` SHA-256: `c649329e90bfa8dee8ea155e06a07a8b86af4580ef90fb0c51abd88a2f37dbf2` (`35598` bytes).
- `reference.py` SHA-256: `54f5124c510397958826fc9cc598c839540bd3f22c2568dc324b0520104e7be2`.
- `run.py` SHA-256: `06ff08dded1def4ae49cd395335e2bd1d63de9cc3e3a5c405b2c1658cef7b03f`.
- `test_reference.py` SHA-256: `7a849cf6cebeebba7783fc687346f5352ce450762a7ae24788ed021e08f752ab`.
- `verify.py` SHA-256: `b3dc6b52014512cd4f884ca73d71d30d3af2d918dda45c5c35d612b25f248c59`.
- `contract.json` SHA-256: `dd3fb1aa24f492c3de947f09fdbea8bb8875ea92f28055f3abab52c41c5c811b`.
- Tests: **40 passed, 0 failed, 0 skipped**.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source_revision_and_candidate_identity | blocked | Pin one exact candidate's source revision/tree, model ID, config, tokenizer and decoding; independent identity review. |
| `RG-02` checkpoint_weights_and_digests | blocked | Every candidate file with byte count and SHA-256 under an immutable artifact revision; independent retrieval record. |
| `RG-03` pinned_runtime_and_offline_load | blocked | Locked offline NeMo/ASR runtime, CUDA/device declaration, deterministic settings, clean-room load. |
| `RG-04` rights_training_data_and_output_use | blocked | Written weight/source/training-data/output-use terms and independent rights/redistribution decision. |
| `RG-05` rights_cleared_corpus_and_transcripts | blocked | Exact rights-cleared cohort, transcripts, split/channel mapping and independent reference. |
| `RG-06` asr_accuracy_and_streaming_latency_with_controls | blocked | Reproduced WER, RTF, end-to-end latency, endpoint/partial behavior, finite/adverse and matched controls. |
| `RG-07` rate_profile_condition_coverage_or_waiver | blocked | Rate-profile evidence for a composite path or an explicit reviewed waiver. |
| `RG-08` provider_intake_public_surface_and_release | blocked | Separate OFF-by-default opt-in intake, exact descriptor/config, clean-install proof, independent review; no default. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
