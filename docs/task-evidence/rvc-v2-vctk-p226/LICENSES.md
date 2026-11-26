<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-RVC-V2-VCTK-P226

This task-local evidence package is authored under Apache-2.0. It includes no
vendored RVC source, checkpoint, HuBERT or RMVPE weight, binary, runtime,
license text, notice, corpus, reference voice or converted waveform from
RVC-Project, Nekochu, VCTK, LJ Speech or any third party. It pins read-only
files by SHA-256 and records provenance only.

The RVC fork checkout is present at revision
`81eed5e8f68b6bed1789f682fe78cdd324495afc` and carries an MIT `LICENSE`
(SHA-256 `bec61ed1eb9a3748644ddbc50303aa6978e14eeaba46822e59a006c722b52585`).
That MIT text is **not copied** into this directory. It is a source-code grant
only: it does not establish terms for the separately distributed
`Nekochu/RVC-VCTK_Voice-sample` checkpoint (`Mp226rmvpe.pth`), the
ContentVec/HuBERT base (`pytorch_model.bin`), the RMVPE base (`rmvpe.pt`), the
VCTK dataset, the source speaker, the p226 target voice or generated output
use.

The historical evaluation used a public VCTK-derived checkpoint, a presumed
`speaker_id=1 -> p226` mapping and an LJ Speech source clip whose dataset page
describes the recordings as public domain. No checkpoint/base-asset terms
review, dataset reference, source-speaker consent, target-voice consent,
reference-availability record or output-use record is staged. The staged
`target_rtvc_p360.flac` is a different target (p360) and is not a p226
reference. The MIT mention is not a weight, dataset, voice or output-use
clearance.

No file in this directory may be treated as an upstream license grant, a
weight term, a reference-voice consent record or a product-use decision. A
future qualified run must stage the exact checkpoint/base-asset/model-card
terms, the complete notice bundle and explicit source-speaker consent,
target-voice consent, reference-availability and output-use records before any
artifact is used (see `BLK-01`, `BLK-02`, `BLK-03`, `BLK-06` and
`RG-01`/`RG-04` in `contract.json`).
