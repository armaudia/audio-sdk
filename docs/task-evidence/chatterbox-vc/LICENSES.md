<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-CHATTERBOX-VC

This task-local evidence package is authored under Apache-2.0. It includes no
vendored Chatterbox source, converted waveform, binary, model weight, conds
asset, runtime, license text, notice or corpus from LAION, Resemble AI or any
third party. It pins read-only files by SHA-256 and records provenance only.

The LAION `chatterbox-voice-conversion` wrapper checkout is present at revision
`9043873c7501033991e9907af7ddf8c394d74522` and carries an Apache-2.0 `LICENSE`
(SHA-256 `1fa474d00e581cc0b506c9d87f4e7d480a5d7944df584e654661ad84e8d4b88a`).
That Apache-2.0 text is **not copied** into this directory. The wrapper license
is a source-code grant only: it does not establish terms for the separately
distributed `ResembleAI/chatterbox` S3Gen weights (`s3gen.safetensors`,
`conds.pt`), the model card, training data, source speakers, target voices,
consent or generated-output use.

The wrapper declares `chatterbox-tts>=0.1.1` and delegates model loading to
`chatterbox.vc.ChatterboxVC`. The historical evaluation report records that the
ResembleAI model card identifies the base Chatterbox model as MIT, but no model
card, weight term or redistribution grant is staged or reviewed here, and the
MIT mention is not a weight or output-use clearance.

The historical p360 target is a demo file from an unrelated upstream voice
conversion repository; the evaluation record explicitly marks its
dataset/license provenance unconfirmed. No source-speaker or target-voice
consent record exists. Chatterbox Nano TTS weights are a different model and are
not a valid substitute for the VC S3Gen weights.

No file in this directory may be treated as an upstream license grant, a weight
term, a reference-voice consent record or a product-use decision. A future
qualified run must stage the exact weight/model-card terms, the complete notice
bundle and explicit source-speaker consent, target-voice consent,
reference-availability and output-use records before any artifact is used (see
`BLK-01`, `BLK-03` and `RG-02`/`RG-04` in `contract.json`).
