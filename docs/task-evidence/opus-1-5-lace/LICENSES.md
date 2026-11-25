<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and rights boundary

## Task-local files

Every file in this directory is original, first-party work licensed
`Apache-2.0` under the repository `REUSE.toml` `docs/**` aggregate. Python files
carry inline SPDX headers; generated JSON and digest artifacts carry `.license`
sidecars. No third-party code, model asset, weight, audio, packet capture,
archive or license text is copied, vendored or redistributed.

## Upstream artifact status

No upstream artifact is present:

- No Opus 1.5 source checkout, archive, patch or build tree.
- No libopus object, dynamic library, executable or install location.
- No OSCE, LACE or NoLACE model file, compiled blob, weight or inference
  runtime.
- No genuine low-bitrate Opus stream, packet capture, PCM, clean reference or
  media file.
- No upstream `LICENSE`, `COPYING`, `NOTICE` or model-terms file.

Opus source is normally published under the Xiph BSD-3-Clause license, but the
exact source revision, copyright notices, model-data/weight terms, third-party
notice bundle and redistribution/product-use scope for any specific artifact
are **unverified here**. That is recorded as a requirement to verify against a
specific pinned revision, not as an established fact for any artifact in this
workspace. Gates `RG-01` and `RG-02` remain blocked.

## Prohibited uses of this package

This package is not an Opus 1.5, OSCE, LACE or NoLACE implementation, decoder,
adapter, provider, model loader, benchmark bundle or release artifact. It grants
no rights to any upstream artifact and makes no licensing, redistribution,
quality, timing or release claim.
