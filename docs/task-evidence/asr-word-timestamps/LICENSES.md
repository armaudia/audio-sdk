<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for `asr-word-timestamps`

This task-local evidence package is Apache-2.0. It vendors no third-party
source, weight, tokenizer, model, runtime, audio, transcript, annotation or
binary. The upstream artifacts below are named and, where present in a mutable
scratch tree, pinned by SHA-256 only. **None is distributed by this package and
none is loaded or executed here.**

| Component | Recorded terms | Review status |
| --- | --- | --- |
| Vosk / Kaldi and `vosk 0.3.44` | Study README records Apache-2.0 code; the installed `dist-info` has no `LICENSE` and `METADATA` says `License: UNKNOWN` | Not reviewed. No source revision, package archive, licence/notice text or bundled-third-party attribution is staged. Metadata is not a grant. |
| `vosk-model-small-en-us-0.15` | No licence, notice, copying or model card in the 14-file tree; `README` states only `Copyright 2020 Alpha Cephei Inc` | Not reviewed. No official archive digest, model card, commercial/output-use decision or attribution is staged. |
| sherpa-onnx / Whisper tiny.en | Study README records MIT code / OpenAI model terms, evaluation only; `sherpa_onnx 2.0.1` `METADATA` says Apache-2.0 | Not reviewed. No source revision, complete notice set, model card, archive digest or output-use decision is staged. |
| `sherpa-onnx-whisper-tiny.en` model tree | No licence, README or model card in the 9-file tree | Not reviewed. The `test_wavs` bytes are pinned but never read or distributed. |
| ONNX Runtime, CTranslate2, faster-whisper, PyTorch | Distributions exist only inside a mutable `.venv` | Not reviewed. No wheel/sdist archives, lockfile, install/import digests or complete notices are staged. |
| AMI EN2003a stitched audio | CC BY 4.0 recorded; attribution required | Not reviewed. The stitch has no transcript, no attribution file and no output-use decision. |
| macOS `say` TTS clips | Synthetic construction-time labels | Not an independent gold reference and not a model or corpus licence grant. |

There is no redistribution approval, commercial/product-use approval, generated
output-use approval or model-card review for any ASR engine, weight, tokenizer,
runtime or corpus in this package. The recorded licence identifiers are
provenance notes from research material, **not a grant**. A caller must supply
the complete licence, notice, model-card and attribution texts and a reviewed
product/output-use decision before any release gate can reopen.

`report.json`, `contract.json`, `report.json.sha256` and `SOURCES.sha256` are
generated task-local artifacts covered by the `.license` sidecars in this
directory. No upstream licence text is copied because no upstream artifact is
included.
