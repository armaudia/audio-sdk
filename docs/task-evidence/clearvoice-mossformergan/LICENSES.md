<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and asset notes — SDK-CLEARVOICE-MOSSFORMERGAN

## Task-local files

All files in `docs/task-evidence/clearvoice-mossformergan/` are original
task-local work and are Apache-2.0. The `docs/**` aggregate annotation in the
repository `REUSE.toml` covers them; `.license` sidecars are provided for
generated JSON, the manifest, the digest sidecar and the requirements lock for
readers outside the REUSE aggregate.

## Upstream ClearerVoice code

- Repository: `https://github.com/modelscope/ClearerVoice-Studio`
- Pinned source revision: `dcb1b20e1e44d435090072ab9b223c792ea1f624`
- Declared code license: **Apache-2.0**, recorded in the pinned asset ledger
  `research/noise_suppression_assets_20261027.json` (SHA-256
  `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4`).
- The research adapter `adapters/clearvoice/` declares the candidate identity
  `ClearerVoice-Studio-clearvoice-0.1.2` and pins its own requirements lock.
  It is external provenance; it is not executed, imported or redistributed.

## Model card and checkpoint

- Model card: `https://huggingface.co/alibabasglab/MossFormerGAN_SE_16K`.
  The pinned census records the card as Apache-2.0. No card revision is recorded
  in the ledger and the card was not accessed by this package.
- Ledger identity: checkpoint `MossFormerGAN_SE_16K/last_best_checkpoint.pt`,
  38,845,593 bytes, SHA-256
  `04bf00db575389e1ea8b1fcca48d9efcf073e50ad170e6dd5230df3bac98be27`;
  pointer `MossFormerGAN_SE_16K/last_best_checkpoint`, 24 bytes, SHA-256
  `315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0`.
- The ledger records no immutable model artifact revision and no retrieval-time
  download commit. The pointer content is not verified here.
- The model card states open and private training data with exact corpus
  exposure undisclosed. Weight-specific terms, training-data provenance,
  redistribution and product-use clearance, and legal review are **not
  established**.
- No checkpoint, pointer, weight, package, runtime or upstream source is
  downloaded, copied, built, vendored, loaded or redistributed by this package.

## Evidence runtime dependencies

`requirements.lock` pins the evidence runtime: NumPy 2.5.4 and SciPy 1.18.1
(BSD-3-Clause) and pystoi 0.4.1 (MIT). They are installed dependencies used
only to score the authored synthetic fixture; they are not vendored,
redistributed or part of the candidate. The ClearerVoice runtime is a separate,
uninstalled package pinned as provenance in
`adapters/clearvoice/requirements.lock`.

## Synthetic stimuli

The seven condition pairs, impulse, tail probe and all surrogate outputs are
authored deterministically by `reference.py`. They are not recorded speech, not
a corpus, not a room or device capture and not a source-reported MossFormerGAN
output.

## Separation from other ClearVoice research

The pinned candidate matrix, noise-suppression census and asset ledger, the
`adapters/clearvoice/` descriptor and the
`research/voice-enhancement-20261101/agent-mossformer-eval/` report and results
are external provenance only. They were not executed, imported, pooled or
reinterpreted here. The sibling `docs/task-evidence/clearvoice-frcrn-16khz/`
package is a different candidate and is not pooled with this evidence.
