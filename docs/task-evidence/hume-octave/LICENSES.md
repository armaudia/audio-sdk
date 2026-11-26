<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files and manifests).

## Candidate service and assets

No Hume Octave credential, entitlement, API contract, vendor terms record,
data-processing record, voice reference, voice consent, client runtime or
rights record is present in this workspace or this worktree. Candidate matrix
record 55 names only the product page, so no contract revision, endpoint,
model/voice version or asset can be pinned.

No generated audio, voice embedding, model fragment or reconstruction is
included in this package, and no credential or network client is opened, loaded
or executed. Vendor service terms, data-processing and retention terms,
training use, generated-output ownership, target-voice consent and output-use,
redistribution and product-use decisions therefore remain unresolved. The
package records this as a blocker; mere account possession or a local client
would not be treated as rights evidence.

## Research sources

`research/voice-enhancement-20261101/candidate_matrix.csv` record 55 and the
audit report listed in `report.json` → `source_reported_context` are pinned
read-only in `SOURCES.sha256`. They are not copied or re-licensed here. No
result from any sibling accent, voice-conversion, prosody, emotion or TTS task
is attributed to this row.

## Installed v0 boundary

`CONTRACTS.md`, `CMakeLists.txt`, the public provider/session headers,
`REUSE.toml` and `scripts/ci.py` are pinned read-only in `SOURCES.sha256`. They
are not modified by this package. The installed v0 contract remains 16 kHz
mono `float32` at 160 samples per frame.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
