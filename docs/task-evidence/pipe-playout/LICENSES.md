<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-PIPE-PLAYOUT

This task-local evidence package is authored under Apache-2.0. It contains no
vendored Bungee Basic source, header, object, static library, binary, notice or
license text; no real audio, corpus, model, weight, annotation asset, listening
response or device trace; and no third-party code. It pins read-only files by
SHA-256 and records provenance only.

Bungee Basic is described by its upstream `LICENSE` as MPL-2.0. A source
checkout at revision `61f52bf34be577d189d388772ddfa3696dee77d8` and a local
static `libbungee.a` exist outside this worktree and are pinned by digest as
provenance. They are **not** an admitted runtime artifact, are not linked,
loaded or executed here, and do not carry a distribution, relink,
source-availability or product-use decision for this pipeline.

The research pilot used ten four-second AMI EN2003a clips. AMI audio,
annotations and derived material are not included, and AMI corpus terms have
not been reviewed for this package. No music, transition, silence or tagged
impulse asset is included. A future qualified run must stage the exact cohort,
its terms and an output-use decision.

The SDK's peak limiter and analysis contracts are referenced only through their
read-only documentation and merged sibling evidence. No provider, adapter,
descriptor, registry default, shared build or CI file is changed.

No file in this directory may be treated as an upstream license grant, an audio
right, a model term or a product-use decision. See `BLK-01`, `BLK-02`, `RG-01`
and `RG-02` in `contract.json`.
