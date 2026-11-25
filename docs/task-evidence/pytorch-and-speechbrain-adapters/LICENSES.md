<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-PYTORCH-AND-SPEECHBRAIN-ADAPTERS

This task-local evidence package is authored under Apache-2.0. It includes no
vendored PyTorch, torchaudio, SpeechBrain or HyperPyYAML source, wheel,
library, header, checkpoint, model weight, config, hyperparams file, audio,
corpus, license text or notice. External files are pinned by SHA-256 only and
are never copied into this directory.

The pinned adapter sources (`research/voice-enhancement-20261101/
agent-metricgan-eval/` and `agent-sepformer-eval/`) are project-local research
runners. They are referenced by digest for provenance; their own terms and the
terms of the works they wrap are not re-licensed by this package.

The model cards for `speechbrain/metricgan-plus-voicebank` at revision
`be514d321f66b5352c5a8d59c44700f57aa8c8f5` and
`speechbrain/sepformer-dns4-16k-enhancement` at revision
`e8c258546300102a240fa2595854d473cbfee49a` state Apache-2.0. Those statements
are upstream model-card lines, not staged license/notice bundles, weight
grants, training-data reviews or product-use decisions. No checkpoint byte is
present, downloaded or reconstructed here.

The recorded runtime is CPython 3.11.5 with torch 2.14.1, torchaudio 2.11.0,
SpeechBrain 1.0.3 and the HyperPyYAML/ruamel/sentencepiece overlay. Those
packages are absent, and their wheel bytes, licenses and notices are not
redistributed. The SpeechBrain wheel SHA-256
`9859d4c1b1fb3af3b85523c0c89f52e45a04f305622ed55f31aa32dd2fba19e9` is quoted
provenance only.

The historical screens used an exploratory DNS2020 no-reverb 30-pair subset.
No audio, manifest payload, corpus term, annotation or derived output is
included. Any future qualified run must stage the exact corpus/input rights,
the checkpoint training-data terms and the derived-output/redistribution
decisions.

No file in this directory may be treated as an upstream license grant, a
weight term, a corpus right or a product-use decision. See `BLK-01` through
`BLK-06`, `RG-01` through `RG-08` and `contract.json:licensing`.
