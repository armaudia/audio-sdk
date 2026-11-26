<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and digest
files). It is a readiness record only; it conveys no rights to any upstream
source, wheel, model, weights, audio or transcript.

## Upstream sherpa-onnx source

No `k2-fsa/sherpa-onnx` source checkout is present at an immutable revision.
The candidate census (line 877) reports a C++ API with streaming ASR, VAD,
keyword spotting, audio tagging, token timestamps and endpointing and labels
the code `Apache-2.0`, but it records no commit, source file, license text,
notice, third-party attribution or per-file digest. The installed wheel's
`licenses/LICENSE` file is pinned as a presence fact only; its provenance and
the bundled third-party notices are not reviewed here. No upstream source file
is copied into this package.

## runtime wheel and ONNX Runtime

A `sherpa_onnx` 2.0.1 wheel metadata tree and a `sherpa-onnx-core` 2.0.1
metadata tree exist only inside a mutable Python 3.11 scratch virtualenv under
`cpp-library/pipeline-validation/playback-speed/.venv`. Their METADATA, RECORD,
WHEEL and license files are pinned as read-only inputs. No archive, sdist,
lockfile, isolated install or offline load trace is present. No wheel is
installed, imported, loaded from, or executed in the pinned Python 3.12.16
interpreter, and no ONNX Runtime binary is vendored.

## Whisper tiny.en model bytes

Nine files under
`cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en`
are pinned byte-for-byte (tree SHA-256
`fae72e5493c2c9d09e1f2725332ba278952ba2489923fe695e040ecd6ee08da5`,
9 files, 256603197 bytes). They are provenance facts only. The tree contains
no `LICENSE`, `NOTICE`, `COPYING`, `README` or model card. The census explicitly
warns that each model has its own license and that the card must be verified.
No ONNX weight, tokenizer or test wav is opened, decoded, converted or
executed. The `.wav` files are never read as audio.

## Corpus, transcripts and outputs

No consented, rights-cleared matched cohort, independent reference, transcript
use grant, commercial-use decision or output-use decision is present. No ASR
output, timestamp, WER, speech-rate score, listening or device timing result is
generated, retained or claimed.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object, no symlink and no provider, adapter, registry, default, ABI,
shared CMake or CI artifact.
