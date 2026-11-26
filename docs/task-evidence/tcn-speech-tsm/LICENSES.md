<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary

This task-local evidence package is licensed under Apache-2.0. It contains no
third-party source, text frontend, phoneme-rate head, weight, checkpoint,
VAE/flow decoder, vocoder, model card, licence text, notice, text corpus,
audio, corpus or manifest payload bytes.

## Upstream declarations, not staged licences

The pinned research records name the Interspeech 2024 TCN speech TSM system and
link `https://www.isca-archive.org/interspeech_2024/lee24m_interspeech.html`.
They record no official runnable code, weight or checkpoint, no licence field,
no licence text, no `COPYING`/`NOTICE` and no model card. This package does not
copy, download, verify or redistribute any upstream artefact. The paper
reference is source-reported context only.

## Required rights review before implementation

- Code licence text, `COPYING`/`NOTICE`, README and any third-party notices at
  an immutable revision.
- Weight-specific terms, model-card terms and the training-data statement.
- Text-frontend vocabulary, phoneme inventory, text-corpus and
  phoneme-alignment terms.
- VAE/flow decoder, upsampling/attention module and vocoder dependency
  licences.
- Rights-cleared text and speech inputs with consent, acquisition, evaluation,
  derived-output and redistribution decisions.
- Attribution and notice bundle for any redistributed derived output.

## Boundary

No vendored third-party bytes. No provider, descriptor, registry, installed
default, public ABI, shared build or CI change. No release claim.
