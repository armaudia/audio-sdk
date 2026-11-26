<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-WAVLM-BASE-RIDGE

This task-local evidence package is authored under Apache-2.0. It includes no
vendored WavLM source, model weight, config, tokenizer, feature archive, ONNX or
PyTorch runtime, audio, transcript, syllable label, license text, notice or
corpus from Microsoft, Meta, AMI, CMU or any third party. It pins read-only files
by SHA-256 and records provenance only.

The pinned research source record describes `microsoft/wavlm-base-plus` at
revision `4c66d4806a428f2e922ccfa1a962776e232d487b` with `license: null`. That
record is not a staged model card, a license/notice bundle, a weight grant, a
redistribution decision or a product-use decision. No `pytorch_model.bin`,
`config.json`, `preprocessor_config.json`, model-card `README.md`, tokenizer
file or derived feature archive is present, copied, loaded or reconstructed
here.

The historical cohort is 210 four-second windows from one AMI EN2003a meeting.
Its audio, word annotations and derived syllable labels are not included, and
AMI corpus terms have not been reviewed for this package. The reference syllable
counts used CMUdict 1.1.1 first pronunciations; the dictionary is not included
and its terms have not been reviewed here. A future qualified run must stage the
exact corpus, annotation and dictionary terms plus a product-use decision.

The historical pilot used Python 3.10.13, PyTorch 2.2.2 and Transformers 4.40.2.
Those packages, their licenses and their wheel bytes are absent and are not
redistributed. A future qualified run must stage the exact runtime, wheel
hashes and install/import digest.

No file in this directory may be treated as an upstream license grant, a weight
term, a corpus/dictionary right or a product-use decision. See `BLK-02`,
`BLK-04`, `RG-01`, `RG-02` and `RG-04` in `contract.json`.
