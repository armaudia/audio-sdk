<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licenses / boundary

This task-local evidence package contains only original metadata, manifests,
scripts, and pinned digests authored for `SDK-WHISPER-TRANSCRIPTION`. It does
not vendor Whisper weights, model binaries, audio corpora, Hugging Face cache
artifacts, or third-party license texts.

Pinned research artifacts are referenced by path and SHA-256 only:
- `research/voice-conversion-eval-20261101/README.md`
- `research/voice-conversion-eval-20261101/scripts/score_conversion.py`
- `research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py`
- `research/voice-conversion-eval-20261101/results/source_asr.json`
- `research/voice-conversion-eval-20261101/results/llvc_asr.json`
- `research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md`

The package records that Whisper ASR scoring was used in external research with
`openai/whisper-tiny.en` and frozen transcript normalization for WER. That
research context is provenance only; this package makes no model/runtime
license clearance, no rights-cleared corpus claim, and no qualified result.

No upstream model, dataset, or third-party source is redistributed here.
