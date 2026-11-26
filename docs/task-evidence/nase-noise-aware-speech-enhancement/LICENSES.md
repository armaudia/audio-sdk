<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary

This task-local evidence package is licensed under Apache-2.0. It contains no
third-party source, diffusion checkpoint, BEATs encoder, weight, tensor,
sampler configuration, model card, licence text, notice, corpus or audio
payload bytes.

## Upstream declarations, not staged licences

The pinned research records name the `YUCHEN005/NASE` research repository and
describe a pretrained VoiceBank+DEMAND checkpoint, test samples, evaluation
scripts, code and a learned noise-aware BEATs conditioning model. They record
no licence field, licence text, `COPYING`/`NOTICE`, model card, commit, file
name, byte count or SHA-256. This package does not copy, download, verify or
redistribute any upstream artefact. The repository URL and census text are
source-reported context only.

## Required rights review before implementation

- Code licence text, `COPYING`/`NOTICE`, README and any third-party notices at
  an immutable revision.
- NASE checkpoint-specific terms, model-card terms and the training-data
  statement, including VoiceBank+DEMAND provenance and overlap.
- BEATs encoder checkpoint terms, feature-extraction configuration and
  training-data statement, kept separate from the NASE checkpoint terms.
- Diffusion sampler, metric-script and test-sample dependency licences.
- Rights-cleared speech inputs with consent, acquisition, evaluation,
  derived-output and redistribution decisions.
- Attribution and notice bundle for any redistributed derived output.

## Boundary

No vendored third-party bytes. No provider, descriptor, registry, installed
default, public ABI, shared build or CI change. No release claim.
