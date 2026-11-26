<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text and Python artifacts and `.license` sidecars for the generated JSON and
SHA-256 files).

## Vendor runtime and SDK terms

Krisp Voice Isolation 2.5 is a closed commercial product. No Krisp SDK
library, runtime, entitlement, licence text, terms statement, ABI
documentation, model card or redistribution grant is present. No vendor binary
is linked, loaded, imported or executed. Commercial and redistribution terms
remain exact open blockers.

## Vendor outputs and corpus

No Krisp corpus audio, transcript, processed vendor output or per-file manifest
is present. The merged research record names the public corpus
`Krisp-AI/VoiceIsolation-Benchmark-Dataset` at revision
`626bac8ca07fb9b4846d4f62d27c321753160b36` under CC BY-NC 4.0, and the public
processed-output dataset `Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed`
at revision `8759715197e39e0356125e3f3197a9854c38fa60`, subset
`vi_2_5_default`, 265 files, 647,960,782 bytes. Those are provenance facts
only. The historical run kept its downloads under `/private/tmp` and did not
add them to any repository; no audio, transcript or output was copied, scored,
retained or redistributed here. Noncommercial scoring permission, output
retention and any publication or redistribution are independent open gates.

## Scorer

No DNSMOS-C/NISQA checkpoint (`runs/NISQA/model_best.pt`), feature extractor,
scoring code, environment lock or scorer output is present. No checkpoint byte
is opened or hashed, no scorer is invoked and no score is produced. The scorer
source URL and checkpoint name are recorded provenance only.

## Source-reported numbers

The vendor benchmark page and the pinned research record are retained as
read-only provenance. Every DNSMOS-C and WER number in `report.json` is labelled
`vendor_published_not_reproduced_here` or
`historical_research_record_not_reproduced_here`. None is a result of this
package.

## No vendored media or weights

This directory contains only text, JSON and Python source. It contains no
`.wav`, `.flac`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library or
compiled object.
