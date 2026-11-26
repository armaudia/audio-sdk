# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON and digest files).

## Upstream LLVC

The local research checkout at
`research/voice-conversion-eval-20261101/repos/llvc` is **KoeAI/LLVC** at commit
`1627c5d358cf9bb2b92b0ccc513d8b36807c923d` and is licensed **MIT** (upstream
`LICENSE` file, pinned in `SOURCES.sha256`). No upstream source file, test audio
file, model code or licence text is copied into this package. The checkout is
read-only evidence and is not executed.

The local evaluation wrapper
`research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py` is pinned by
SHA-256 and quoted only as short API-usage needles in `report.json`. No wrapper
source is copied into this package and it is not executed.

## Runtime and native libraries

No TorchAudio, TorchCodec, SoundFile, torch, SpeechBrain or Auraloss wheel,
module, native library or notice text is included. The recorded wheel set is
absent and unpinned:

- torchaudio `2.11.1` CPU and torch `2.15.0` CPU wheels are not present in the
  required CPython `3.11.5` interpreter.
- The TorchCodec version required by torchaudio `2.11.1` is **not recorded**
  locally, so no exact TorchCodec artifact can be named or hashed.
- Upstream `requirements.txt` pins `soundfile==0.12.1`; the evaluation
  environment's resolved version is not recorded. An unrelated `0.14.0`
  installation is observed but is not qualified.
- soundfile metadata declares **BSD-3-Clause**. It depends on **libsndfile**,
  whose separate terms govern any bundled native library. Those terms have not
  been reviewed here, and no redistribution decision exists.

Wheel licence and notice review is release gate `RG-02` and remains
**blocked**. The LLVC MIT source licence does not grant rights to runtime
wheels, native libraries or the absent LLVC checkpoint.

## Inputs and outputs

The only audio bytes created here are generated synthetic PCM16 WAV fixtures
inside `report.json` metadata; no WAV file is written to disk. No real corpus,
caller-owned recording, target voice, checkpoint or model output is present.
A rights-cleared caller-owned WAV fixture, with provenance, consent where
applicable, derived-output use and redistribution decisions, is required
before any executed parity result.

## Historical references

The following local research artefacts are referenced by path and SHA-256 only;
they are not copied into this package and they are not re-run:

- `research/voice-conversion-eval-20261101/README.md` — historical evaluation
  narrative, LLVC compatibility note and source-reported timing.
- `research/voice-conversion-eval-20261101/results/llvc_asr.json` — historical
  one-utterance Whisper Tiny EN scoring record.
- `research/voice-conversion-eval-20261101/repos/llvc/infer.py` and
  `requirements.txt` — upstream calls and the soundfile pin.
- Merged sibling evidence (`docs/task-evidence/llvc`,
  `pytorch-and-speechbrain-adapters`,
  `numpy-scipy-soundfile-wav-resampling`) — boundary references only, never
  pooled with this package.
