<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary

This task-local evidence package is licensed under Apache-2.0. It contains no
third-party source, diffusion checkpoint, input-SNR estimator, weight, tensor,
sampler configuration, model card, licence text, notice, corpus or audio
payload bytes.

## Upstream declarations, not staged licences

The pinned census names the `yh-jun/SNR-Aligned_diffSE` repository and a 2025
paper. It reports baseline checkpoints exposed through Drive folders and a
source-reported `+0.12 PESQ` mean over SE-Bridge on VoiceBank-DEMAND. It also
states that the repository's own licence text was not verified, checkpoint
terms are unresolved, and the upstream SGMSE MIT license must not be treated as
covering this fork or its weights. This package does not copy, download,
verify or redistribute any upstream artifact. The repository and paper URLs
are source-reported context only.

## Required rights review before implementation

- Fork source licence text, `COPYING`/`NOTICE`, README and third-party notices
  at an immutable revision, reviewed separately from upstream SGMSE MIT terms.
- DiffSE checkpoint-specific terms, model-card terms and training-data
  statement, including VoiceBank-DEMAND and SE-Bridge provenance and overlap.
- Input-SNR estimator checkpoint terms, feature-extraction configuration and
  training-data statement, kept separate from the checkpoint terms.
- One-step sampler, metric-script and test-sample dependency licences.
- Rights-cleared speech inputs with consent, acquisition, evaluation,
  derived-output and redistribution decisions.
- Attribution and notice bundle for any redistributed derived output.

## Boundary

No vendored third-party bytes. No provider, descriptor, registry, installed
default, public ABI, shared build or CI change. No release claim.
