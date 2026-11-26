<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON files).

## Upstream FireRedVAD source

No FireRedVAD source checkout is present in this workspace. The official
source lead is `https://github.com/FireRedTeam/FireRedVAD`, but no commit,
license identifier, license text, file list or per-file digest has been
admitted or verified. No upstream source file, model code, feature extractor,
test audio or license text is copied into this package. The source checkout,
its commit and its license remain an exact open blocker.

## Offline and streaming model weights

No FireRedVAD checkpoint, config, feature/vocabulary asset, model card or terms
file is present, and no Hugging Face or ModelScope snapshot is staged. No
weight fragment, converted tensor, embedding or reconstruction is included,
and no weight file is opened, loaded or executed.

The upstream model leads are `https://huggingface.co/FireRedTeam/FireRedVAD`
and the model folders referenced by the official repository. The research
register says the offline and streaming checkpoints are separately hosted and
that the repository code and model card claim Apache-2.0. No model revision,
variant, per-file byte count or SHA-256 is asserted here. Weight terms,
training-data provenance, redistribution and product-use decisions remain
unresolved. Mere local possession would not be treated as rights evidence, and
the code/card claim does not by itself establish weight terms.

## Labels, cohorts and outputs

The FireRedVAD FLEURS-VAD-102 labels (9,443 clips across 102 languages) are
described as forthcoming and are not available here. No audio, label timeline,
reference oracle, VAD probability, event list or benchmark output is copied,
generated, decoded, scored or admitted. The source-reported multilingual
cohort and any author-reported score are leads only.

## Audio-event detection

FireRedVAD also describes an audio-event-detection path. No AED source,
checkpoint, label set or result is present, and AED is outside this package's
scope.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
