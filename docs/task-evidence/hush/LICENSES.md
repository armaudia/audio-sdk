<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and asset notes — SDK-HUSH

## Task-local files

All files in `docs/task-evidence/hush/` are original task-local work and are
Apache-2.0. The `docs/**` aggregate annotation in the repository `REUSE.toml`
covers them; `.license` sidecars are provided for generated JSON and text
artifacts for readers outside the REUSE aggregate.

## Upstream Hush

- Repository: `https://github.com/pulp-vision/Hush`
- Pinned commit: `9f6414e91461a8f4bdf9840c0cdcdcb7da986339`
- Declared license: **Apache-2.0**. `LICENSE` SHA-256
  `d2650f8a0a002d02377a5157e60071a39cc710113bf2c19f808db7045edda198`.
- Model card: `https://huggingface.co/weya-ai/hush` at declared revision
  `1aee65c0b22e99bc9c8fea933dc25948168d2416`; it also states Apache-2.0. The
  revision is a research-readme declaration, not a locally hashed artifact, and
  the card's files API lists no weights.
- The Apache-2.0 notice obligations apply if the source or a derived binary is
  redistributed. This package copies no upstream source or binary.

## Model bundle and runtime

The pinned deployment ONNX bundle
`advanced_dfnet16k_model_best_onnx.tar.gz` (SHA-256
`45632ccaa82b71bb743d6caa7c78e983fe2f2790a3af7f6ec48e6ed7ba085df6`) and the
platform runtime libraries (`libweya_nc.dylib`, `libweya_nc.so`, `weya_nc.dll`)
are present only in the external research checkout at
`data/checkouts/Hush/deployment/`. Their SHA-256 values are pinned, but:

- the deployment README's download table links a placeholder release URL
  (`https://github.com/YOUR_USERNAME/deepfilternet-se/releases`);
- the declared model-card revision exposes no model files to verify;
- artifact-specific model-bundle and runtime redistribution/product-use rights
  and training-data provenance are **not established**;
- no legal review exists.

The `.ckpt` checkpoint is not used and is pinned only to record that exclusion.
No model, bundle, library or weight is downloaded, copied, built, vendored,
loaded or redistributed by this package.

## Synthetic stimuli

The two voiced sources, the three SIR mixtures, digital silence and the impulse
are generated deterministically by `reference.py`. They are not recorded
speech, not a corpus, not a room capture and not a source-reported Hush output.

## Separation from other Hush research

The pinned research reports (`research/voice-enhancement-20261101/agent-hush-*`)
and the research-workspace adapter (`adapters/hush/`) are external provenance
only. They were not executed, imported, pooled or reinterpreted here.
