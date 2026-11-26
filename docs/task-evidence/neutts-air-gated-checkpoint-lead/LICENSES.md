<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-NEUTTS-AIR-GATED-CHECKPOINT-LEAD

This task-local evidence package is authored under Apache-2.0. It includes no
vendored NeuTTS source, Air weight, Q4/Q8 GGUF snapshot, NeuCodec asset,
generated waveform, binary, runtime, model card, license text, notice or corpus
from Neuphonic or any third party. It pins read-only files by SHA-256 and
records provenance only.

The upstream `neuphonic/neutts` code checkout is present at revision
`ac69851f28fc63a487917e7c2e27f0d75c759cba` and its repository `LICENSE` (SHA-256
`c3308963748766e2617138a754a0f6915564aae7a4cc31c7d60dc30abf326224`) is the
**NeuTTS Open License v1.0**. That text is **not copied** into this directory.
It conditions commercial use on a revenue threshold and conditions Output use.

The same upstream `README.md` states in its licence table that **NeuTTS-Air is
Apache-2.0** while NeuTTS-Nano and NeuTTS-2E are NeuTTS Open License 1.0. The
gated `neuphonic/neutts-air` model card that would resolve which terms govern
the weights and Outputs is absent. This package therefore records an
**unresolved license conflict** (`LICENSE_REVIEW` in `contract.json`). It does
not assert Apache-2.0 for the Air weights, and it does not apply the NeuTTS
Open License 1.0 beyond the repository text that is actually present.

No weight, model-card, reference-voice, consent or output-use term has been
staged or reviewed. The upstream checkout bundles demo samples and one
`output.wav`; they are treated as repository content, not as a consent, cohort,
output-use or quality record. Only the whole-file SHA-256 of `output.wav` is
recorded, and no audio is decoded, played or scored.

No file in this directory may be treated as an upstream license grant, a weight
term, a codec term, a reference-voice consent record or a product-use decision.
A future qualified run must stage the exact gated-access grant, weight/model-card
terms, the complete notice bundle and explicit consent, reference-availability,
output-use and commercial-threshold records before any artifact is used (see
`BLK-01` through `BLK-05` and `RG-01` through `RG-08` in `contract.json`).
