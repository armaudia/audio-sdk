<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-NEUTTS-NANO-Q4

This task-local evidence package is authored under Apache-2.0. It includes no
vendored NeuTTS source, GGUF weight, NeuCodec asset, generated waveform, binary,
runtime, model card, license text, notice or corpus from Neuphonic or any third
party. It pins read-only files by SHA-256 and records provenance only.

The upstream `neuphonic/neutts` code checkout is present at revision
`ac69851f28fc63a487917e7c2e27f0d75c759cba` and carries the **NeuTTS Open
License 1.0** (`LICENSE`, SHA-256
`c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224`). That text
is **not copied** into this directory. It is not an OSI-approved license: the
upstream README states that the NeuTTS-Nano models use the NeuTTS Open License
1.0, which conditions commercial use on a revenue threshold and conditions
Output use. The NeuTTS-Air row's Apache-2.0 terms do **not** apply to Nano.

No weight, model-card, reference-voice, consent or output-use term has been
staged or reviewed. The upstream checkout bundles demo samples and one
`output.wav`; they are treated as repository content, not as a consent, cohort,
output-use or quality record. Only the whole-file SHA-256 of `output.wav` is
recorded, and no audio is decoded, played or scored.

No file in this directory may be treated as an upstream license grant, a weight
term, a codec term, a reference-voice consent record or a product-use decision.
A future qualified run must stage the exact weight/model-card/license terms, the
complete notice bundle and explicit consent, reference-availability,
output-use and commercial-threshold records before any artifact is used (see
`BLK-01` through `BLK-05` and `RG-02` through `RG-08` in `contract.json`).
