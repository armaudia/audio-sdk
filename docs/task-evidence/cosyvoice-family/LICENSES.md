# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the text
artefacts and `.license` sidecars for the JSON files).

## Upstream CosyVoice source

The local research checkout at
`research/voice-conversion-eval-20261101/repos/cosyvoice` is
`FunAudioLLM/CosyVoice` at commit
`074ca6dc9e80a2f424f1f74b48bdd7d3fea531cc` and is licensed **Apache-2.0**
(upstream `LICENSE` SHA-256
`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`,
pinned in `SOURCES.sha256`). Its `third_party/Matcha-TTS` submodule is
`shivammehta25/Matcha-TTS` at commit
`dd9105b34bf2be2230f4aa1e4769fb586a3c824e`. No upstream source file, model
code, test audio or licence text is copied into this package. The checkout is
read-only evidence and is not executed. It is TTS/voice-cloning code and
contains no source-speech conversion checkpoint.

## Conversion model weights

No source-speech conversion checkpoint, adapter or weight bundle is present in
this workspace. The family record names no conversion artifact filename, byte
count, revision or digest, so no weight can be pinned. No weight fragment,
converted tensor, embedding or reconstruction is included in this package, and
no weight file is opened, loaded or executed.

The upstream model and training-data terms are not locally staged.
Conversion-weight terms, training-data provenance, target-speaker consent and
redistribution/product-use decisions therefore remain unresolved. The package
records this as a blocker; mere local possession would not be treated as rights
evidence.

## Routed TTS evidence

The merged sibling package `docs/task-evidence/cosyvoice-2-0-5b/` covers the
CosyVoice 2 0.5B **text-to-speech** row. It is pinned read-only in
`SOURCES.sha256` and is not copied or re-licensed here. Its historical output
WAV is referenced only by path and SHA-256; it is not copied into this package,
not re-licensed here and not admitted as a family conversion result. TTS is a
different task and does not establish source-speech conversion.

## Fixed research pair

The voice-conversion research README describes one LJ Speech source and one
upstream RT-VC demo target. The target dataset/licence provenance is not
confirmed. This package does **not** treat that material as a permitted
conversion pair, as target-speaker consent, as reference-voice permitted use or
as output-use clearance.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
