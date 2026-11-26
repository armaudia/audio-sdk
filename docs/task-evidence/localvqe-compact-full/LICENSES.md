<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licenses and asset rights

- Task-local files: Apache-2.0.
- Upstream LocalVQE source checkout: Apache-2.0, revision
  `7f61cd05095d42e56a135b303f5bb4d761da22b9`.
- Upstream model repository `LocalAI-io/LocalVQE` is described as Apache-2.0.
  The compact full-enhancement GGUF (`localvqe-pi-v1-49k-f32.gguf`, SHA-256
  `0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26`) and the
  echo-only sibling (`localvqe-pi-aec-v1-49k-f32.gguf`, SHA-256
  `b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8`) are not
  present in this workspace. Artifact-specific terms, training-data
  provenance, redistribution and product-use clearance are not established by
  this package.
- The native library
  `liblocalvqe.0.1.0.dylib` (SHA-256
  `bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298`) was not
  read, hashed, loaded or executed by this package.
- No LocalVQE source archive, model, weight, library or runtime is copied,
  vendored, downloaded, built, imported, loaded, executed or redistributed by
  this package. Only SHA-256 identity values are recorded.
- Research inputs are read-only provenance and remain under their own terms.
- The echo-only checkpoint is a separate task boundary and is never pooled
  with the compact full-enhancement result.
