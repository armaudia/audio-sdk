<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and manifest
files). It contains only text, JSON and Python source.

## Upstream FunASR source and FSMN-VAD checkpoint

No FunASR checkout is present in this workspace. The pinned VAD register names
the toolkit `https://github.com/modelscope/FunASR` and the candidate checkpoint
`iic/speech_fsmn_vad_zh-cn-16k-common-pytorch`, and records that the toolkit is
MIT while the checkpoint's own terms, revision, hash and config are unresolved.
No commit, license text, file list or per-file digest has been admitted or
verified. No upstream source file, model code, test audio or license text is
copied into this package. The source checkout, checkpoint terms and provenance
remain exact open blockers.

## Model weights and assets

No FSMN-VAD checkpoint, config, feature asset, model card or terms file is
present. The local ModelScope and Hugging Face caches contain no matching
snapshot and no weight blob. No weight fragment, converted tensor, embedding or
reconstruction is included, and no weight file is opened, loaded or executed.
Mere local possession would not be treated as rights evidence.

## Corpus, references and outputs

No speech/nonspeech recording, continuous truth, known positive or negative
item, consent record or output-use grant is present. No FSMN-VAD probability,
event, detection or boundary is generated, retained, decoded, played, scored or
admitted. Corpus rights and output use remain independent open gates.

## No vendored media or weights

This directory contains no `.wav`, `.flac`, `.pt`, `.pth`, `.onnx`,
`.safetensors`, binary library or compiled object, and no vendored upstream
license text.
