<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-OPUS-DEEP-PLC

This task-local evidence package is authored under Apache-2.0. It includes no
vendored source, binary, model, weight, license text, notice or corpus from
Opus, libopus, the Xiph.Org Foundation or any third party.

Opus source and the deep-PLC components are normally distributed by the
Xiph.Org Foundation under the BSD-3-Clause license, with `COPYING`,
`LICENSE_PLEASE_READ.txt`, copyright notices, and separate terms for some
model or third-party material. Those files are **not present** in this
workspace at any fixed probe. No license, notice, model term or rights decision
for a deep-PLC artifact has been reviewed, and this package makes no statement
about redistribution, patent, product-use or commercial scope.

One unqualified transitive PyAV 18.1.0 wheel dylib reports `libopus 1.6.1` and
exports DRED decoder symbols. It is recorded only as provenance metadata in
`report.json` and is never linked, loaded or executed. The wheel ships a PyAV
project license, not the Opus `COPYING`/notices, pins no Opus source revision,
exposes no identified deep-PLC selector and has no rights review. It is not
admitted as a source, runtime or asset.

No file in this directory may be treated as an upstream license grant. A future
qualified run must stage the exact upstream license/notices/model-terms bundle
and record an explicit rights decision before any artifact is used (see
`BLK-02` and `RG-02` in `contract.json`).
