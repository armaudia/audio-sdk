<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-WAVLM-ACOUSTIC-DISFLUENCY-MODEL

This task-local evidence package is authored under Apache-2.0. It includes no
vendored WavLM source, backbone weight, disfluency checkpoint, tokenizer/
preprocessor asset, PyTorch or Transformers runtime, audio, transcript, frame
label, license text, notice or corpus from the `amritkromana/
disfluency_detection_from_audio` authors, Microsoft, AMI, Switchboard, LDC, the
corrected-annotation archive or any other third party. It pins read-only files
by SHA-256 and records provenance only.

The pinned upstream repository at commit
`a2512e5fa0d2bf200861f049a2f08a2600c3f27c` contains no `LICENSE`, `LICENCE`,
`COPYING` or `NOTICE` file, and its README, demo and model definition state no
license or terms. The Google Drive weight payload is described without a
license or terms statement. Presence of the repository checkout is therefore
not a license grant for the source or the checkpoint. No `acoustic.pt`,
`disfluency_acoustic.pt`, WavLM configuration or weight file is present,
copied or reconstructed here.

The recorded smoke loaded a locally acquired 377,639,565-byte checkpoint whose
SHA-256 is `8724aaac4da9ae4d6e04f55dc394650a2517fbf529f5f4cd00b1353c74547036`.
That file is not in this workspace. The WavLM Base+ configuration used only to
instantiate the architecture is recorded at revision
`4c66d4806a428f2e922ccfa1a962776e232d487b`; its model card records a null
license field. Neither artifact may be redistributed or productized without a
reviewed grant.

The historical smoke used one AMI EN2003a crop. Its audio, annotation and
Switchboard-derived frame labels are not included, and AMI/LDC and annotation
terms have not been reviewed for this package. The upstream label pipeline uses
the Zayats et al. corrected reannotation archive; its terms are also unreviewed
here. A future qualified run must stage the exact corpus, annotation and
dictionary/label terms plus a product-use decision.

The historical environment used Python 3.10.13, torch 2.2.2 and transformers
4.40.2. Those packages, their licenses and their wheel bytes are absent and are
not redistributed. The upstream README separately declares pandas 1.5.0,
torch 1.12.1, transformers 4.22.2, torchaudio 0.12.1, whisper_timestamped 1.14.4
and gdown 5.1.0; they are recorded as provenance, not staged.

No file in this directory may be treated as an upstream license grant, a
weight term, a corpus/annotation right or a product-use decision. See `BLK-01`
through `BLK-05`, `RG-01`, `RG-02` and `RG-04` in `contract.json`.
