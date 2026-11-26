<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-VOCOS

This task-local evidence package is authored under Apache-2.0. It includes no
vendored Vocos source, JIT weight, PyTorch runtime, feature tensor, generated
waveform, binary, model card, license text, notice or corpus from Vocos, MeanVC2
or any third party. It pins read-only files by SHA-256 and records provenance
only.

The modified Vocos-derived source copy lives outside this package at
`research/voice-conversion-eval-20261101/repos/meanvc/vocos` inside the MeanVC2
checkout at revision
`fe5286ae205a26ad4eba64395513130bd5974b46`. The containing repository's root
`LICENSE` is **Apache-2.0** (`c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`).
The vendored directory has no separate Vocos `LICENSE`, `NOTICE` or package
metadata. MeanVC2's README credits `gemelo-ai/vocos`; the exact upstream Vocos
revision and its MIT license/notice set are **not present** in this checkout and
are not copied here. A modified vendored copy is not a substitute for the
upstream source grant.

The MeanVC2-bundled `vocos.pt` JIT decoder (32 MB) was downloaded for a
historical synthetic benchmark and later removed. No weight file, model card,
byte count or SHA-256 is retained or staged. No reviewed weight/output term,
consent, feature-availability record or output-use decision exists.

No file in this directory may be treated as an upstream license grant, a
weight term, a model-card term, a reference-feature consent record or a
product-use decision. A future qualified run must stage the exact upstream
source and notices, the immutable weight snapshot and its terms, the complete
notice bundle, a locked runtime, and explicit consent, feature-availability,
output-use and commercial-terms records before any artifact is used (see
`BLK-01` through `BLK-05` and `RG-01` through `RG-08` in `contract.json`).
