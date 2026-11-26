<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files and manifests).

## Candidate model and weights

No input-speech emotion/expressive-prosody transformation source, checkpoint,
model configuration, target-emotion label set, style conditioning asset, target
voice, runtime or rights record is present in this workspace or this worktree.
Candidate matrix record 57 names no model, repository, revision, checkpoint,
label set or runtime, so no upstream identity or weight can be pinned.

No weight fragment, style embedding, label table, converted tensor or
reconstruction is included in this package, and no weight file is opened,
loaded or executed. Model and training-data terms, target-voice consent and
output-use, redistribution and product-use decisions therefore remain
unresolved. The package records this as a blocker; mere local possession would
not be treated as rights evidence.

## Research sources

`research/voice-enhancement-20261101/candidate_matrix.csv` record 57 and the two
audit reports listed in `report.json` → `source_reported_context` are pinned
read-only in `SOURCES.sha256`. They are not copied or re-licensed here. No
result from any sibling accent, voice-conversion or TTS task is attributed to
this row.

## Installed v0 boundary

`CONTRACTS.md`, `CMakeLists.txt`, the public provider/session headers,
`REUSE.toml` and `scripts/ci.py` are pinned read-only in `SOURCES.sha256`. They
are not modified by this package. The installed v0 contract remains 16 kHz
mono `float32` at 160 samples per frame.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
