<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and asset notes — SDK-RNNOISE-V0-2

## Task-local files

All files in `docs/task-evidence/rnnoise-v0-2/` are original task-local work
and are Apache-2.0. The `docs/**` aggregate annotation in the repository
`REUSE.toml` covers them; `.license` sidecars are provided for generated JSON
and text artifacts for readers outside the REUSE aggregate.

## Upstream RNNoise

- Repository: `https://github.com/xiph/rnnoise`
- Pinned commit: `70f1d256acd4b34a572f999a05c87bf00b67730d`
- Source license: **BSD-3-Clause**, `COPYING` SHA-256
  `45d37ca1cdb278c088e1aa85e0e65ca3a534ed86a28dcc96ca16810248a61d35`
- The BSD-3-Clause notice obligations apply if the source or a binary is
  redistributed. This package copies no upstream source or binary.

## Model archive and runtime

The pinned model archive
`rnnoise_data-0a8755f8e2d834eff6a54714ecc7d75f9932e845df35f8b59bc52a7cfe6e8b37.tar.gz`
is present only in the external research checkout. Its SHA-256 is pinned, but
separate pretrained-model/archive terms, redistribution rights, product-use
rights and training-data provenance are **not established**. The compiled
runtime library expected at `data/envs/rnnoise/librnnoise.dylib` is absent.
No weight, archive, library or model source is downloaded, copied, built,
vendored, loaded or redistributed by this package.

## Synthetic stimuli

The clean voiced surrogate, band-limited noise, silence and impulse are
generated deterministically by `reference.py`. They are not recorded speech,
not a corpus and not a source-reported RNNoise output.

## Separate task

The existing `docs/task-evidence/rnnoise-speech-probability/` package is a
different Analysis-profile task. It is not used, imported, pooled or conflated
with this Enhancement-profile evidence.
