<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the JSON and manifest
files). It contains only text, JSON and Python source.

## LiveKit turn detection

No LiveKit model weight, ONNX file, package, runtime, source checkout, Python
wheel, binary, header, patch, trial or licence text is present in this
workspace. The public documentation and source-tree URLs are cited only as
identity references:

- <https://docs.livekit.io/agents/logic/turns/turn-detector.md>
- <https://github.com/livekit/agents/tree/main/livekit-plugins/livekit-plugins-turn-detector>

The documentation states that the text model and the local `v1-mini` model use
the **LiveKit Model License**, not Apache-2.0. That identifier is recorded as
source-reported only. The licence text, redistribution terms, output-use terms
and any commercial or research grant were not observed, reviewed or accepted
here. No licence file is copied into this package.

## Assets and outputs

No model, weight, tokenizer, vocabulary, preset, corpus, reference audio, turn
cohort, label file, parity vector, consent record or output-use grant is
present. No LiveKit probability, endpoint decision, cutoff measurement,
end-of-turn measurement, latency, memory value or listening score from the
candidate is generated, retained, decoded, played, scored or admitted. The
synthetic control trace is authored in `reference.py` and is not LiveKit
output. Vendor and corpus rights remain independent open gates.

## No vendored media or binaries

This directory contains no `.wav`, `.flac`, `.mp3`, `.mp4`, `.opus`, `.pt`,
`.pth`, `.onnx`, `.safetensors`, `.model`, `.bin`, `.so`, `.dylib`, `.dll`,
`.a`, `.lib`, `.o`, `.wasm`, binary library or compiled object, and no vendored
upstream license text.
