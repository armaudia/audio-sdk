<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-COSYVOICE-2-0-5B — CosyVoice 2 0.5B readiness blocker

**Status: `proposal_only_incomplete`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the CosyVoice 2 0.5B voice row. It is
**not** a CosyVoice 2 0.5B implementation: no exact weight bundle, pinned
runtime, caller output, rights-cleared cohort, listening result, device
measurement, benchmark or release claim is included. **No result here
qualifies CosyVoice 2 0.5B.**

## Exact blocker: the 0.5B weight bundle and pinned runtime are absent

The **Apache-2.0 source checkout is present and verified** at an exact revision.
The exact **CosyVoice2-0.5B inference weights** and the **isolated Python
runtime** are **not present**. Nothing was fabricated, reconstructed or
downloaded.

| Item | Status |
| --- | --- |
| Source checkout | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/cosyvoice`, `FunAudioLLM/CosyVoice` commit `074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc`, Apache-2.0 `LICENSE` SHA-256 `c71d239d…`, 156 tracked regular files + 8 symlinks (3,073,286 bytes), tree digest `9b0d2b60…` |
| Source submodule | **Present and pinned**: `third_party/Matcha-TTS`, `shivammehta25/Matcha-TTS` commit `dd9105b34bf2be2230f4aa1e4769fb586a3c824e`, 107 files + 1 symlink (826,391 bytes), tree digest `de380235…` |
| Exact 0.5B weights | **Absent**: required files include `cosyvoice2.yaml`, `llm.pt`, `flow.pt`, `hift.pt`, `campplus.onnx`, `speech_tokenizer_v2.onnx`, `spk2info.pt` and `CosyVoice-BlankEN`. Model revision reference `eec1ae6c79877dbd9379285cf8789c9e0879293d` |
| Hugging Face cache | **Metadata only**: `~/.cache/huggingface/hub/models--FunAudioLLM--CosyVoice2-0.5B` has `refs/main` (SHA-256 `969a3cde…`) but **no `snapshots/` and no `blobs/`**; not admitted and never opened |
| Pinned Python runtime | **Absent**: the isolated CPython 3.11 `.venv-chatterbox` path and every fixed `data/envs/*` path are absent; reported packages include torch 2.6.0, torchaudio 2.6.0, numpy 1.26.4, soundfile 0.14.0, transformers 4.51.3 and a NumPy-1.x-compatible onnxruntime |
| Historical reference WAV | **Present but not admitted**: `results/cosyvoice2/source_prompt_streaming_tts.wav`, 480,044 bytes, SHA-256 `4a74fdd7…`, 24 kHz, 10.0 s; not regenerable without the removed weights |
| Voice/prompt rights | **Unresolved**: model-weight terms, training-data provenance, prompt-speaker consent, reference-voice permitted use and output-use/redistribution clearance |
| Caller output / cohort | **Absent**: no approved caller reference pair, frozen multi-item prompt/text cohort or language/speaker-group definition |

The machine-readable record is `report.json` → `source_probe`,
`weights_probe`, `runtime_probe`, `absence_evidence`, `exact_blockers`,
`voice_profile` and `gates`. `contract.json` carries the same disposition,
pins, geometry and all eight blocked release gates.

Because the exact bundle and runtime are missing, **no result qualifies
CosyVoice 2 0.5B**, no provider is registered, and release gate `RG-01` stays
blocked.

## The historical run is TTS, not speech-to-speech conversion

The one historical run used the official `stream=True` zero-shot TTS path with
the fixed LJ Speech clip as both prompt audio and prompt transcript:

| Field | Historical value | Scope and status |
| --- | --- | --- |
| Output | 10.0 s in four chunks, 24 kHz | One English prompt/text pair; research provenance only |
| First chunk | 23.810076 s from the inference call | Includes prompt loading and encoding; no device or transport buffering |
| Total generation | 80.661524 s; file RTF 8.066152 | CPU-only Apple M1; not a live-call latency claim |
| Model initialization | 22.421157 s | Separate from generation |
| ASR / clipping | WER 0.0%; clipped fraction 0.0 | One utterance, Whisper Tiny English |
| Output SHA-256 | `4a74fdd7fbf29c51da8c8c66f29b366605eb9d9b4b466fd753bb18b84785beb1` | File present, weights absent, parity not reproducible |

These values never enter `report.json` as floats or as candidate results. They
are labeled `historical_research_not_reproduced_not_qualified`. They do not
promote the blocked source-speech `CosyVoice` conversion row and do not
establish identity similarity, naturalness, consent, output use or
microphone-to-output timing.

## Exact scope

- Work is confined to `docs/task-evidence/cosyvoice-2-0-5b/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, board/handoff files, CI, rulesets and `main` are
  untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  CosyVoice provider is installed or registered.
- The documented upstream geometry is separate from installed v0: 24 kHz mono
  f32 generated audio, streaming chunks defined by the provider and **not
  pinned here**, output length generated rather than identity, and a
  text-to-speech source mapping rather than an audio-in/audio-out conversion.
- No request is ever processed as CosyVoice 2 0.5B. Valid requests fail closed
  because the exact bundle and runtime are absent.
- Missing, invalid, nonfinite and out-of-range manifest cases fail closed with
  no metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`). Mutable status, owner,
  review, handoff, priority, claim and history never enter canonical bytes and
  are never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed**
  into any canonical artifact.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a TTS engine:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF.
2. **Source verification.** It recomputes a digest over the tracked non-`.git`
   files and symlinks in the pinned checkout and its submodule, checks the
   commit, counts, byte totals and Apache-2.0 licence pin. It never imports or
   executes upstream code.
3. **Fixed-path absence probes.** It checks a bounded list of weight, runtime
   and cohort locations without a recursive workspace walk.
4. **Weights probe.** It records the required model files, the HF ref-only
   cache state and the exact model revision reference. It never opens a blob,
   loads a weight or downloads an artifact.
5. **Runtime probe.** Fixed-path checks only; no package is imported, no
   archive is opened, no package is installed and no network is used.
6. **Asset admission.** It validates an exact caller-supplied manifest with
   fail-closed revision, digest, runtime, format, rights, consent, reference,
   cohort and finiteness checks. A structural schema control is labeled
   non-evidence and never qualifies.
7. **Stable board identity** from the linked row and its four dependencies.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a weight bundle, create a model or runtime session,
implement a network, synthesize speech, score quality, run listening or produce
audio.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With the exact bundle,
runtime and rights absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Permitted input and target references | `blocked_no_exact_bundle_or_consent` |
| Task, language and speaker groups | `blocked_single_historical_pair` |
| Text and semantic content preserved | `blocked_no_regenerated_output` |
| Identity/similarity separate | `blocked_no_similarity_result` |
| Naturalness separate | `blocked_no_listening_or_mos` |
| Alignment, first-output/tail timing, target condition | `blocked_not_measured` |
| Consent, reference availability, output use | `blocked_rights_unresolved` |

## Admission controls

`report.json` → `admission.cases` contains **66 synthetic adverse cases**, all
rejected with no state change, plus one structurally valid schema control that
is explicitly **not evidence**. The cases cover missing objects and fields,
malformed revisions and digests, model-file path traversal and oversize
counts, unresolved weight terms, wrong runtime and package versions, wrong
sample rate or channel count, missing consent and output-use rights, missing
reference and cohort gates, duplicate JSON keys, NaN/Infinity and BOM input.
The summary records `qualifying_results=0`, `weights_loaded=false`,
`runtime_invoked=false`, `audio_read=false` and `inference_performed=false`.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact licensed source and 0.5B weight bundle pinned | The source is pinned, but the exact bundle is absent. |
| `RG-02` exact pinned Python runtime and package lock | The isolated CPython 3.11 environment, lock and digest are absent. |
| `RG-03` weight terms, training data, consent and output use | Model/training terms, prompt-speaker consent and output-use rights are unresolved. |
| `RG-04` exact reference parity | No approved reference pair or regenerable output exists. |
| `RG-05` frozen rights-cleared voice/TTS cohort | No multi-item permitted prompt/text cohort exists. |
| `RG-06` independent content, identity and naturalness results | No independent WER/content, similarity, naturalness or authorized listening result exists. |
| `RG-07` alignment, first-output/tail, memory and streaming | No exact-runtime timing, memory or streaming measurement exists. |
| `RG-08` opt-in provider intake and release decision | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory, with the pinned interpreter and no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py all` regenerates the canonical report, sidecar, contract and source
manifest three times in one process and requires byte-identical output.
`verify.py` additionally runs three cold-start regenerations in fresh scratch
trees, checks strict JSON, exact pins, stable board identity, licensing,
task-local git scope and blocker semantics.

## Non-claims

No exact CosyVoice 2 0.5B weight bundle, model output, runtime, corpus, prompt
consent, listening panel, speaker similarity, naturalness, latency, device,
callback, benchmark or release claim is made. No installed v0, public API, C
ABI, descriptor, registry, default, shared build, CI, board or handoff change
is made. Historical values remain labeled with their original scope.
