# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

## Pinned downstream consumer (present)

The local research checkout at
`research/voice-conversion-eval-20261101/repos/rvc` is the RVC consumer
checkout at revision `81eed5e8f68b6bed1789f682fe78cdd324495afc` and is licensed
**MIT** (upstream `LICENSE`, pinned in `SOURCES.sha256`). Its `infer/hubert.py`
loads a transformers `HubertModelWithFinalProj` from `assets/hubert_base`. No
upstream source file, config, loader or licence text is copied into this
package; the checkout is read-only evidence and is not executed.

The RVC-MLX consumer at
`research/voice-conversion-eval-20261101/repos/rvc-mlx-realtime` is also read
only. Its `convert/hubert.py` and `model_manager.py` are pinned because they
declare the ContentVec checkpoint and conversion path. That checkout has no
`LICENSE` file of its own, so no licence is asserted for it here.

## ContentVec config (present) and weights (absent)

`assets/hubert_base/config.json` and `assets/hubert_base/preprocessor_config.json`
are present and digest-pinned. They describe a 768-wide, 12-layer
`HubertModelWithFinalProj` at 16 kHz with a 320-sample convolutional stride and
a 256-wide final projection. The required
`assets/hubert_base/pytorch_model.bin` is **absent**. The pinned RVC-MLX
consumer instead names `assets/contentvec/pytorch_model.bin` and an
`IAHispano/Applio` download URL; that path is also absent.

No ContentVec weight SHA-256, byte count, model card or redistribution term is
recorded here. Nothing was fabricated, reconstructed, substituted or
downloaded. The upstream `auspicious3000/ContentVec` checkout, its licence text
and its weight terms are **not present locally** and are not asserted.

## Runtime (absent)

No PyTorch, TorchAudio, Transformers, NumPy or SoundFile runtime is installed.
The pinned requirements text constrains `torch==2.4.1+cpu`,
`torchaudio==2.4.1+cpu` and `transformers>=4.49.0,<4.50`; the config declares
Transformers `4.49.0` and `torch_dtype` `float16`. A requirements text is not
an installed runtime, install digest or verified offline load path.

## What is not licensed or included

No model weights, checkpoints, feature tensors, converted audio, real corpus
audio, model code, upstream licence text or vendor claim is included. No
provider is registered or enabled. The package contains only standard-library
prose, test and verifier code plus canonical JSON evidence. Input-corpus
rights, derived-feature rights and consent for any downstream voice or speaker
are **unresolved**, not granted.
