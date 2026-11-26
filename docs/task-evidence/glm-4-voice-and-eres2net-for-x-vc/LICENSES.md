# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artifacts and `.license` sidecars for the JSON and checksum files).

## Upstream X-VC

The local research checkout at
`research/voice-conversion-eval-20261101/repos/x-vc` is **Jerrister/X-VC** at
commit `49df8c591eafc48b096e466d96f9839f9c0dd739` and is licensed **MIT**
(upstream `LICENSE`, pinned in `SOURCES.sha256`). No upstream source file,
config, script, test audio, model code or licence text is copied into this
package. The checkout is read-only evidence and is not executed or imported.

The pinned X-VC source bundles wrappers and third-party-style modules
(`semantic_encoder.py`, `speaker_encoder.py`, `utils/ERes2Net.py`) whose
upstream notices remain in the checkout. Those files are cited by path and
digest only.

## GLM-4-Voice-Tokenizer

The pinned `configs/xvc.yaml` selects
`zai-org/glm-4-voice-tokenizer` for semantic tokenization at a declared
1280-wide feature interface. The tokenizer config, vocabulary, codebook and
weight files are **not present** in the workspace. No weight SHA-256, byte
count, model-card term or redistribution right is recorded here. Nothing was
fabricated, reconstructed, substituted or downloaded.

## ERes2Net speaker encoder

The pinned config selects
`pretrained/speech_eres2net_sv_en_voxceleb_16k`, documented upstream as
`iic/speech_eres2net_sv_en_voxceleb_16k`, with a declared 80-bin fbank input
and a 192-dimensional embedding. The `configuration.json`, weight file and any
model card are **not present** in the workspace. No weight SHA-256, byte count
or redistribution term is recorded here.

## X-VC checkpoint

The pinned README names `chenxie95/X-VC` and `ckpts/xvc.pt`; the pinned config
declares `checkpoint: null`. The checkpoint is **not present**. The linked
ledger reports a 5.01 GB checkpoint size against an 8 GB host budget but records
no local download or run.

## What is not licensed or included

No model weights, checkpoints, tokenizer assets, speaker-encoder assets,
converted audio, real corpus audio, model code, upstream licence text or vendor
claim is included. No provider is registered or enabled. The package contains
only standard-library prose, test and verifier code plus canonical JSON
evidence.

Any future use of the X-VC checkpoint, GLM-4-Voice-Tokenizer or ERes2Net
weights requires their own reviewed licence/terms decision, the MIT
caller-supplied-asset obligations, input-corpus and voice-consent rights, and
an approved output-use scope.
