# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

## Upstream Seed-VC

The local research checkout at
`research/voice-conversion-eval-20261101/repos/seed-vc` is **Plachtaa/seed-vc**
at commit `51383efd921027683c89e5348211d93ff12ac2a8` and is licensed
**GPL-3.0** (upstream `LICENSE`, pinned in `SOURCES.sha256`). No upstream source
file, preset, test audio, model code or licence text is copied into this
package. The checkout is read-only evidence and is not executed.

## XLS-R-300M encoder

The preset at
`configs/presets/config_dit_mel_seed_uvit_xlsr_tiny.yml` selects
`facebook/wav2vec2-xls-r-300m` for semantic feature extraction at
`output_layer: 12`. The encoder config, preprocessor config and weight files
are **not present** in the workspace. No weight SHA-256, byte count or
redistribution term is recorded here. Nothing was fabricating, reconstructed,
substituted or downloaded.

The XLS-R-300M weight licence/terms and the GPL-3.0 obligations for a
caller-supplied-asset adapter must be reviewed before any reproduction.

## Historical one-block reference

The historical output
`research/accent-conversion-20261101/results/seedvc-realtime-ABA-a0046-block.wav`
is referenced by path and SHA-256 only. It is not copied into this package and
is not re-run or re-scored. The referenced timing log
`results/seedvc-realtime.log` is absent.

The source clip `data/l2accent/ABA_arctic_a0046.wav` is present in the research
workspace but is **not read or used**. The accent-conversion README records
L2-ARCTIC under CC BY-NC 4.0; no corpus or output-use permission is established
here.

## What is not licensed or included

No model weights, checkpoints, feature tensors, converted audio, real corpus
audio, model code, upstream licence text or vendor claim is included. No
provider is registered or enabled. The package contains only standard-library
prose, test and verifier code plus canonical JSON evidence.
