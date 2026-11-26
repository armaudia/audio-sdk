<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for SDK-SILERO-VAD-V5-ONNX-REFERENCE

This task-local evidence package is authored under Apache-2.0. It includes no
vendored Silero source, ONNX Runtime, Python runtime, model weights, audio,
annotation, corpus, license text, notice or product-use grant from Silero,
ONNX Runtime, Microsoft, or any third party. One ONNX file outside this package
is read-only inspected for a whole-file SHA-256 and protobuf structural shapes;
its tensor values are not decoded, no graph is executed, and it is not copied
or redistributed.

The present ONNX artifact is labelled "Silero VAD v5" by in-repo cpp-library
documents and the same SHA-256 is labelled "silero-vad 6.2.3 bundled standard
ONNX" by `research/plans/F02/vad_sources.md`. That conflict is unresolved. An
upstream release tag, commit, model card, per-weight terms, license/notice
bundle and product-use decision for the exact bytes are absent. No label in
this package is an upstream license grant, a trained-weight term, a corpus
right or a product-use decision. See `BLK-01`, `RG-01` and `RG-02` in
`contract.json`.

The merged Silero evidence packages are pinned only as boundary context. They
use synthetic traces, surrogate feature vectors or a model-free stub. They do
not include v5 weights, runtime, audio or outputs and are not relicensed here.

No file in this directory may be treated as a redistribution right for the
ONNX artifact, a runtime wheel, a corpus or a released product capability.
