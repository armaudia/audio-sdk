<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON files).

## Upstream FastSpeech 2 source

No FastSpeech 2 source checkout is present in this workspace. The reviewed
lead is the ESPnet module `espnet2/tts/fastspeech2/fastspeech2.py` with the
upstream lead `https://github.com/ming024/FastSpeech2`, but no commit, license
identifier, license text, file list or per-file digest has been admitted or
verified. No upstream source file, model code, test audio or license text is
copied into this package. The source checkout, its commit and its license
remain an exact open blocker.

## Upstream VITS source

No VITS source checkout is present. The official source lead is
`https://github.com/jaywalnut310/vits`, but no commit, license identifier,
license text, file list or per-file digest has been admitted or verified. No
upstream source file, model code or license text is copied into this package.

## Checkpoints, phoneme sets and duration statistics

No FastSpeech 2 or VITS checkpoint, config, phoneme set, duration statistic,
hop length, model card or terms file is present. The local Hugging Face cache
contains no FastSpeech 2 or VITS snapshot. No weight fragment, converted
tensor, embedding, duration statistic or reconstruction is included, and no
weight file is opened, loaded or executed.

Checkpoint revisions, variants, per-file byte counts and SHA-256 values are not
asserted here. Weight terms, training-data provenance, corpus license,
redistribution and product-use decisions remain unresolved. Mere local
possession would not be treated as rights evidence.

## Texts, phoneme labels and outputs

No corpus text, phoneme sequence, phone alignment, reference duration label,
consent record or output-use grant is present. No duration prediction is run,
no audio is synthesized or retained, and no output is scored or admitted.
Training-data provenance, corpus license and output use are independent open
gates.

## No vendored media, weights or runtime

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
