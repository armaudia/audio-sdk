<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-MOBILENETV3-SMALL-ON-LOG-MELS

This task-local evidence package is authored under Apache-2.0. It includes no
vendored torchvision source, MobileNetV3 weight, trained checkpoint, state
dict, PyTorch/librosa runtime, audio, transcript, syllable label, log-mel
feature array, license text, notice or corpus from the PyTorch project, AMI,
CMU or any third party. It pins read-only files by SHA-256 and records
provenance only.

The historical recipe uses `torchvision.models.mobilenet_v3_small(weights=None)`
from torchvision 0.17.2 and trains it from scratch. No ImageNet or other
pretrained weight is present, copied or reconstructed. The torchvision source
tree, its BSD-3-Clause license/notice bundle, the trained weights and the
product-use decision are not staged here. No checkpoint or model artifact is
redistributed.

The historical cohort is one AMI EN2003a meeting. Its audio, word annotations
and derived syllable labels are not included, and AMI corpus terms have not
been reviewed for this package. The reference syllable counts use CMUdict 1.1.1
first pronunciations; the dictionary is not included and its terms have not
been reviewed here. A future qualified run must stage the exact corpus,
annotation and dictionary terms plus a product-use decision.

The historical pilot used PyTorch 2.2.2, torchvision 0.17.2 and librosa. Those
packages, their licenses and their wheel bytes are absent and are not
redistributed. A future qualified run must stage the exact runtime, every wheel
hash and an install/import digest.

No file in this directory may be treated as an upstream license grant, a
weight term, a corpus/dictionary right or a product-use decision. See `BLK-01`,
`BLK-02`, `BLK-04`, `RG-01`, `RG-02` and `RG-05` in `contract.json`.
