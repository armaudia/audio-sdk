# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

## Upstream FastEnhancer

The local research checkout at `data/checkouts/FastEnhancer` is
`aask1357/fastenhancer` at commit
`49ab55a57e3a064d94c6412cd0f0a383a55ca0f8` and is licensed **MIT** (upstream
`LICENSE` file, pinned in `SOURCES.sha256`). No upstream source file, test audio
file, model code or licence text is copied into this package. The checkout is
read-only evidence and is not executed.

## Model weights

The exact FastEnhancer DNS 16 kHz Small ONNX release graph is **not present** in
this workspace. The external ledger pins 832,813 bytes and SHA-256
`d7c937d6b475dbe89a6e6a69853b685fe62d629f4c96077559c556ac6f8aaa2d` at release
`onnx-dns-v1.0.0`. The release page does not state separate pretrained-model
terms; the ledger records “not specified separately; retain local only”.

A different local file at `cpp-library/.deps/fastenhancer_s.onnx` (875,885
bytes, SHA-256 `f04ece2beed330da367264c54cedded62f65a117fbde5c005d3a88fc796d0ba3`,
`wav_in [1,512]`) is a non-admitted export, consistent with the 48 kHz
variant. No weight fragment, converted tensor, embedding or reconstruction is
included in this package, and no local ONNX file is loaded into a runtime or
executed.

## Runtime

The pinned inference runtime is CPython 3.10 with `onnxruntime 1.20.1`,
`numpy 1.26.4` and `soundfile 0.13.1`, as recorded in
`adapters/fastenhancer/requirements.lock` (pinned in `SOURCES.sha256`). It is
not installed or importable here. A local C++ ONNX Runtime 1.31.1 prebuilt tree
at `cpp-library/.deps/onnxruntime-osx-arm64-1.31.1` is referenced by path and
SHA-256 only; it is not the pinned runtime and was not imported or executed.

## Historical evaluation references

The following local research artefacts are referenced by path and SHA-256 only;
they are not copied into this package and they are not re-run:

- `research/voice-enhancement-20261101/candidate_matrix.csv` — row 16,
  “FastEnhancer Tiny and Small”.
- `research/noise_suppression_candidate_census.md` — FastEnhancer record.
- `research/noise_suppression_assets_20261027.json` — external asset ledger.
- `research/voice-enhancement-20261101/agent-ears-preservation-743/REPORT.md` —
  743-item EARS input-preservation screen.
- `research/native-fastenhancer-alone-20261109/REPORT.md` and `results.json` —
  native Small 48 kHz evaluation, a different variant.
- `REALTIME_COMPONENT_CANDIDATES.md` — 30-clip DNS pilot values.
- `adapters/fastenhancer/` — pinned adapter, lock and streaming boundary.

## Absent rights decisions

No licence decision is recorded for the pretrained weights, their training data
or the ONNX Runtime redistribution terms. Those decisions are release gate
`RG-03` and remain **blocked**. The MIT source licence does not automatically
grant rights to the trained weights or the runtime.
