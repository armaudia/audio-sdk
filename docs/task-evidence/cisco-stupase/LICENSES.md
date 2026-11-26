<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licenses and provenance

## This package

The task-local evidence package is Apache-2.0. It contains no Cisco StuPASE
source, checkpoint, audio, dataset or third-party binary.

## Upstream candidate

- **Cisco-authored code:** Apache-2.0. The repository `LICENSE.md` identifies
  Cisco-authored files; third-party files retain their original headers.
- **Model card:** Apache-2.0 (`license: apache-2.0` on the pinned hub revision).
- **Third-party components:** Microsoft WavLM (MIT), NXAI xLSTM (Apache-2.0),
  WavTokenizer (MIT), SEtrain (MIT), KKKSQJ DeepLearning utilities (MIT),
  urgent-challenge utilities (Apache-2.0), NVIDIA BigVGAN (MIT) and SenSE (MIT).
  The upstream `NOTICE` and `licenses/` directory carry the exact texts.
- **Training data:** DNS5 clean speech (LibriVox subset; public domain/DNS5
  terms), LibriSpeech (CC BY 4.0), LibriTTS (CC BY 4.0), VCTK (CC BY 4.0),
  DNS5 noise (AudioSet CC BY 4.0, Freesound CC0 1.0, DEMAND CC BY-SA 3.0) and
  OpenSLR26/28 RIRs (Apache-2.0).
- **Checkpoints:** no checkpoint bytes are included. The model card declares
  Apache-2.0, but no separate artifact-specific weight license text or written
  output-use/redistribution decision is present. That gap is recorded as
  `BLK-05`, not resolved here.

## External metadata only

The package records public URLs, byte counts and SHA-256 values for the pinned
source commit and hub revision. It does not redistribute the upstream source,
checkpoints or media. The SHA-256 values for the three checkpoints are the hub
LFS object identifiers; the text-file hashes are of the public raw bytes for the
pinned revision. No local asset admission is claimed.

## No redistribution

Nothing in this directory may be copied into a product, SDK distribution,
benchmark bundle or model package as a substitute for the upstream license and
rights review.
