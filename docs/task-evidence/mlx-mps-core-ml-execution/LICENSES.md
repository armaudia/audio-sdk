<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and asset-rights notes — SDK-MLX-MPS-CORE-ML-EXECUTION

This task-local evidence package is licensed **Apache-2.0** under the repository
aggregate mapping for `docs/**` in [`REUSE.toml`](../../../REUSE.toml).

## What this package contains

Only original text, Python reference code, strict JSON and SHA-256 manifests.
It vendors **no** upstream source, wheel, framework, binding, model, compiled
Core ML artifact, preprocessing asset, corpus or audio. Consequently it carries
no third-party license text or notice bundle, and `LICENSES/` holds only the
repository's Apache-2.0 text.

## What is absent and must be supplied and reviewed

| Runtime | Required licensing input (not present, not verified here) |
| --- | --- |
| MLX | Reviewed upstream license text for the exact `ml-explore/mlx` revision, wheel/source distribution terms and any bundled Metal kernel notices. |
| MPS | Reviewed license text for the exact PyTorch build that provides the MPS backend, including bundled third-party notices and the Metal/MPS dependency terms. |
| Core ML | Reviewed terms for the exact Core ML deployment target and toolchain/binding (`coremltools` or Swift), including Apple SDK/toolchain terms and any compiled-model redistribution terms. |

No runtime, model or training-data license is asserted, inherited or implied by
this package. The model and training-data terms, output use and redistribution
rights are independent open blockers (`BLK-07`). A missing license text is never
treated as permissive.

## Sibling evidence

The pinned sibling Core ML trial under
`realtime-audio-library/evaluation/cpu_saving_20261031/coreml_trial/` is quoted
only as adverse, source-scoped historical evidence. Its ONNX Runtime / Core ML
provider terms, DPDFNet model terms and NVIDIA RE-USE adapter terms are **not**
adopted or redistributed here.
