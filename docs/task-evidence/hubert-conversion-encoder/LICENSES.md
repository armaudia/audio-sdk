# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

## Upstream RVC consumer

The local research checkout at
`research/voice-conversion-eval-20261101/repos/rvc` is
**RVC-Project/Retrieval-based-Voice-Conversion-WebUI** at commit
`81eed5e8f68b6bed1789f682fe78cdd324495afc` and is licensed **MIT** (upstream
`LICENSE`, pinned in `SOURCES.sha256`). No upstream source file, test audio,
model code or licence text is copied into this package. The checkout is
read-only evidence and is not executed.

The HuBERT transformer config and preprocessor config under
`assets/hubert_base/` are present in the working tree but are **not tracked**
by that commit; they are digest-pinned per file only.

## HuBERT encoder

The pinned consumer expects a transformers-format
`assets/hubert_base/pytorch_model.bin` that matches the
`HubertModelWithFinalProj` config: 768 hidden, 12 layers, 12 heads, 3 072
intermediate, 512-wide 7-layer convolution with strides
`[5, 2, 2, 2, 2, 2, 2]`, a 256-wide `final_proj`, `torch_dtype` `float16` and
transformers `4.49.0`. The upstream family is `facebook/hubert-base-ls960`, but
the exact upstream weight identity is **unverified** because no local weight
exists.

The encoder config, preprocessor config and weight files are **not present** in
the workspace as weights. No weight SHA-256, byte count or redistribution term
is recorded here. Nothing was fabricated, reconstructed, substituted or
downloaded.

The upstream HuBERT weight licence/terms, the conversion-checkpoint terms and
the caller-supplied-asset obligations must be reviewed before any reproduction.

## Conversion pipeline

A HuBERT representation alone does not emit converted speech. No content-to-
target mapper, decoder/vocoder or matched conversion checkpoint is present. The
candidate matrix and the transform reports record no end-to-end mapper/decoder
or local conversion checkpoint. No conversion asset is copied, downloaded,
reconstructed or claimed.

## Other local systems

The RVC whole-file pipeline timing in
`research/voice-conversion-eval-20261101/README.md` belongs to a different
system. It is referenced only to exclude it, not as a HuBERT conversion-encoder
measurement.

## What is not licensed or included

No model weights, checkpoints, feature tensors, converted audio, real corpus
audio, model code, upstream licence text or vendor claim is included. No
provider is registered or enabled. The package contains only standard-library
prose, test and verifier code plus canonical JSON evidence.
