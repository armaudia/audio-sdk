<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-SMALL-LOG-MEL-GRU

This task-local evidence package is authored under Apache-2.0. It includes no
vendored PyTorch/librosa source, complete GRU weight set, state dict, runtime,
audio, transcript, syllable label, log-mel feature array, license text, notice
or corpus from the PyTorch project, AMI, CMU or any third party. It pins
read-only files by SHA-256 and records provenance only.

The historical recipe uses a locally defined `TinyRateGRU` built from
`torch.nn.GRU` and `torch.nn.Linear` under torch 2.2.2. It was trained from
scratch; no pretrained weight is present, copied or reconstructed. One
final-fold checkpoint file exists and is hashed without being loaded or
decoded. The PyTorch/librosa source trees, their license/notice bundles, the
trained-weight terms and a product-use decision are not staged here. No model
artifact is redistributed.

The historical cohort is one AMI EN2003a meeting. Its audio, word annotations
and derived syllable labels are not included, and AMI corpus terms have not
been reviewed for this package. The reference syllable counts use CMUdict 1.1.1
first pronunciations; the dictionary is not included and its terms have not
been reviewed here. A future qualified run must stage the exact corpus,
annotation and dictionary terms plus a product-use decision.

The historical pilot used Python 3.10.13, PyTorch 2.2.2 and librosa. Those
packages, their licenses and their wheel bytes are absent and are not
redistributed. A future qualified run must stage the exact runtime, every wheel
hash and an install/import digest.

No file in this directory may be treated as an upstream license grant, a
weight term, a corpus/dictionary right or a product-use decision. See `BLK-01`,
`BLK-02`, `BLK-04`, `RG-01`, `RG-02` and `RG-05` in `contract.json`.
