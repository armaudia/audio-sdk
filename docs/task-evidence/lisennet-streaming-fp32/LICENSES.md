<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing notes

This task-local evidence package is Apache-2.0. It is proposal-only and adds no
SDK source, provider, descriptor, default or build behavior.

## Upstream provenance

- The pinned research port is `LarocheC/eco8-neaixt` at the checkout
  `data/checkouts/eco8-neaixt`; its `LICENSE` is MIT (Copyright (c) 2023 Yexin
  Lu (MP-SENet), Copyright (c) 2025-2026 Clément Laroche). Only source files are
  pinned by SHA-256; nothing is copied, vendored or built.
- The reference implementation is `hyyan2k/LiSenNet` (MIT), cited by the model
  card. It provides no pretrained artifact.
- The published graphs and checkpoints are in the Hugging Face repository
  `claroche1/LiSenNet`; the model card declares MIT. The pinned
  `g_best_streaming_fp32.onnx` is a third-party MIT port of the magnitude-mask
  sub-network; the host STFT/feature/phase code remains outside the graph.

## Rights status

MIT metadata is recorded but is **not** a clearance for this use. Written
weight-specific terms, runtime distribution/product-use terms, training-data
provenance, redistribution permission and legal review are absent.
`model_license_metadata=MIT` and `code_license_metadata=MIT` are metadata
labels only. No weight, graph, runtime or upstream source may be downloaded,
copied, packaged or redistributed by this package.

## Data and outputs

All stimuli are deterministic synthetic floats generated in `reference.py`.
No real audio, corpus item, speaker sample, media, listener, device recording or
network response is present. Synthetic metrics describe the surrogate only and
are not LiSenNet outputs.

The Apache-2.0 text is available at `LICENSES/Apache-2.0.txt` in the SDK
worktree. Generated JSON, digest and manifest artifacts carry adjacent
`.license` sidecars; Python and Markdown sources carry explicit SPDX headers.
