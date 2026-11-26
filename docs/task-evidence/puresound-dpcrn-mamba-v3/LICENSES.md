<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Upstream licensing notes

This task-local evidence package is Apache-2.0. It does not copy, vendor or
redistribute any upstream PureSound file.

## Recorded upstream scope

- **Original PureSound code, SDK, configuration, documentation and model-zoo
  checkpoints/ONNX exports** are licensed under Apache-2.0 according to the
  upstream `LICENSE` (SHA-256
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`) and
  `NOTICE` (SHA-256
  `ecce4d8c6a7bf96b90027ba1250ae734d33d4c260cd83fb67fcdce2286b435e1`).
  The upstream README states that others may use, modify, use commercially and
  redistribute these models under the license terms.
- **Third-party material** retains its own license and is not covered by the
  PureSound Apache-2.0 grant.
- **Datasets and audio recordings** are excluded unless explicitly licensed
  otherwise. The pinned ledger does not establish exact training-corpus
  exposure or third-party dataset terms.

## Status in this package

`rights_cleared=false` and `legal_review=false`. Apache-2.0 plus the upstream
NOTICE is metadata, not an artifact-specific redistribution, product-use or
training-data decision. No upstream graph, manifest, package, runtime or source
file is present in this SDK worktree or redistributed by this package; only
SHA-256 digests, byte counts and metadata are recorded.
