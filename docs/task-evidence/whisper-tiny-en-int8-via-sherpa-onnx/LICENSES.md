<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licenses and rights boundary

This task-local evidence package is authored for this repository and is covered
by the repository `Apache-2.0` licensing metadata. It vendors **no** sherpa-onnx
source, Whisper model weights, ONNX files, tokenizer, audio, transcript, runtime
binary, wheel, or third-party license text.

## Pinned upstream records (not vendored here)

| Item | Recorded identity | Recorded license / terms | Status in this package |
| --- | --- | --- | --- |
| sherpa-onnx source/runtime | `k2-fsa/sherpa-onnx`; exact revision, archive digest, and complete license/notice bundle not staged | Apache-2.0 is commonly reported upstream; not independently reviewed here | absent / not vendored |
| whisper tiny.en int8 ONNX model files | `sherpa-onnx-whisper-tiny.en` file set; local scratch copies hashed as provenance only | Upstream model/weight terms not staged or reviewed here; OpenAI Whisper model terms and any conversion/distribution terms unresolved | absent from package / not admitted |
| Playback-speed prototype evidence | `cpp-library/pipeline-validation/playback-speed/README.md` and local scratch model bytes | Repository-local research artifact; not a license grant for model redistribution | provenance only |

## Rights and use boundary

- No model weight, tokenizer, audio, transcript, or runtime is redistributed.
- No commercial/product/runtime-use right is asserted.
- No benchmark, listening, device-timing, release, or provider-qualification claim is made.
- Any future intake requires exact source revision, complete license/NOTICE
  bundle, exact model/asset identity and digests, reviewed output-use terms,
  pinned offline runtime, and independent exact-head review.
