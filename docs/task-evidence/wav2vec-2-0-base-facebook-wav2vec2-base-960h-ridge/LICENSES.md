<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-WAV2VEC-2-0-BASE-FACEBOOK-WAV2VEC2-BASE-960H-RIDGE

This task-local evidence package is authored under Apache-2.0. It includes no
vendored wav2vec2 source, model weight, tokenizer asset, ridge-head artifact,
ONNX/PyTorch runtime, audio, transcript, syllable label, embedding array,
license text, notice or corpus from Facebook/Meta, AMI, CMU or any third party.
It pins read-only files by SHA-256 and records provenance only.

The pinned research source record describes `facebook/wav2vec2-base-960h` at
revision `22aad52d435eb6dbaf354bdad9b0da84ce7d6156` as Apache-2.0. That record
is not a staged model card, a complete license/notice bundle, a weight grant or
a redistribution decision. No `model.safetensors`, `config.json`,
`preprocessor_config.json`, tokenizer file or ridge-head artifact is present,
copied or reconstructed here.

The historical cohort is one AMI EN2003a meeting. Its audio, word annotations
and derived syllable labels are not included, and AMI corpus terms have not
been reviewed for this package. The reference syllable counts use CMUdict
1.1.1 first pronunciations; the dictionary is not included and its terms have
not been reviewed here. A future qualified run must stage the exact corpus,
annotation and dictionary terms plus a product-use decision.

The historical pilot used PyTorch 2.2.2, Transformers 4.40.2, scikit-learn and
numpy. Those packages, their licenses and their wheel bytes are absent and are
not redistributed. A future qualified run must stage the exact runtime, wheel
hashes and install/import digest.

No file in this directory may be treated as an upstream license grant, a
weight term, a corpus/dictionary right or a product-use decision. See `BLK-01`,
`BLK-03`, `BLK-04`, `RG-01`, `RG-02` and `RG-04` in `contract.json`.
