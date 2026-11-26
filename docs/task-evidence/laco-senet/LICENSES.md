<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and digest
files).

## Upstream LaCo-SENet source

No LaCo-SENet source checkout is present. The merged evidence links
`https://github.com/yskim3271/LaCo-SENet` and states that the repository root
exposes no `LICENSE` entry. No commit, license text, notice, file list or
per-file digest is recorded. No upstream source file, streaming wrapper, model
code, Hydra configuration or license text is copied into this package. The
source checkout, its immutable revision, its license identity and its
component map remain open blockers. A model-card MIT label does not prove the
source-code license.

## Model checkpoints and Hydra configuration

No LaCo-SENet checkpoint, weight fragment, Hydra config, overrides file, model
card or terms file is present. The local Hugging Face, Torch and interpreter
caches contain no LaCo-SENet artifact. The merged evidence records one
checkpoint identity (`M1_12.5ms/s2039/model_279000.th`, 5,707,759 bytes,
SHA-256 `4fc07683a0b346630f51c68046cca1a8e547ae816f961aeac57b34ba6696f6a2`)
at model revision `022c7f9190449619be9815629dd905671c193815`. That identity is
recorded only: it is not independently verified from local bytes and it is not
a rights grant. Checkpoint-specific terms and training-data provenance remain
unresolved; local possession would not be treated as rights evidence.

## Corpus, audio and outputs

No recording, corpus, speaker consent, clean reference, enhanced output or
output-use grant is present. No LaCo-SENet output is generated, retained,
decoded, played or scored. Corpus rights, clean-reference permission and
output use are independent open gates. The upstream VoiceBank+DEMAND scores
quoted in the README are source-reported claims, not local measurements.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.th`, `.onnx`, `.safetensors`, binary library
or compiled object.
