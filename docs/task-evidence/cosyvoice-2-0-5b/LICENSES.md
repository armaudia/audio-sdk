# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

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
read-only evidence and is not executed.

## Model weights

The exact **CosyVoice2-0.5B** inference bundle is **not present** in this
workspace. The local Hugging Face cache directory contains only
`refs/main` pointing at model revision
`eec1ae6c79877dbd9379285cf8789c9e0879293d`; it has no `snapshots/` directory
and no weight blobs. No weight fragment, converted tensor, embedding or
reconstruction is included in this package, and no weight file is opened,
loaded or executed.

The upstream model card at
`https://huggingface.co/FunAudioLLM/CosyVoice2-0.5B` and the training-data
statement are not locally staged. Model-weight terms, training-data provenance
and redistribution/product-use decisions therefore remain unresolved. The
package records this as a blocker; mere local possession is not treated as
rights evidence.

## Prompt, reference and output terms

The historical run used the fixed LJ Speech `LJ001-0001.wav` clip as both prompt
audio and prompt transcript. The evaluation README describes the LJ Speech
recordings as public domain, but this package does **not** treat that statement
as prompt-speaker consent for voice cloning, as reference-voice permitted use,
or as output-use clearance. Consent, reference availability and output use are
independent blockers.

The retained historical WAV is referenced only by path and SHA-256. It is not
copied into this package, not re-licensed here and not admitted as a
qualification result.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
