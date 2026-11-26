<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-KOKORO-82M

This task-local evidence package is authored under Apache-2.0. It includes no
vendored Kokoro source, generated waveform, binary, model weight, config,
preset voice-style tensor, runtime, license text, notice or corpus from
hexgrad or any third party. It pins read-only files by SHA-256 and records
provenance only.

The upstream Kokoro code checkout is present at revision
`dfb907a02bba8152ca444717ca5d78747ccb4bec` and carries an Apache-2.0 `LICENSE`
(SHA-256 `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4`).
That license text is **not copied** into this directory. The code license is a
source-code grant only: it does not establish terms for the
`hexgrad/Kokoro-82M` weights, `config.json`, the `af_heart` preset voice-style
asset, the model card, training data or generated-output use.

No weight, config, voice-style, model-card or output-use term has been staged
or reviewed. The research record states the weights were removed after the one
historical run; this package treats that as a provenance note, not a rights
grant. The historical output `af_heart.wav` is hashed as a whole file and is
not decoded, played, reused or promoted.

No file in this directory may be treated as an upstream license grant, a weight
term, a voice-style asset availability record or a product-use decision. A
future qualified run must stage the exact weight/model-card and voice-style
terms, the complete notice bundle and explicit voice-availability and
output-use records before any artifact is used (see `BLK-01`, `BLK-03` and
`RG-02`/`RG-04` in `contract.json`).
