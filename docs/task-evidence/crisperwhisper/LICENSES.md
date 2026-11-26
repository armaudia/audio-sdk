<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for `crisperwhisper`

This task-local evidence package is Apache-2.0. It vendors no third-party
source, model weight, model card, tokenizer, audio, transcript, annotation or
binary. The upstream artifacts below are named and, where recorded, pinned by
SHA-256 only. **None is distributed by this package.**

| Component | Recorded terms | Review status |
| --- | --- | --- |
| `nyrahealth/CrisperWhisper` code | MIT (recorded in the pinned candidate note) | Not reviewed here; no source revision, package archive, digest or MIT notice file is staged. |
| CrisperWhisper model weights on Hugging Face | CC-BY-NC-4.0 (recorded) | Not reviewed here; no model ID, revision, digest, model card, licence text or output-use decision is staged. Non-commercial: a separate reviewed licence is mandatory before any commercial use. |
| Verbatim/filler audio and transcript annotations | Not recorded | Not present; no audio, transcript, annotator, adjudication, agreement or dataset terms exist. |

There is no redistribution approval, commercial/product-use approval, generated
output-use approval or model-card review for CrisperWhisper in this package. The
recorded license identifiers are provenance notes from the pinned candidate
note and inventory row, not a grant. `CC-BY-NC-4.0` is non-commercial, so the
weights cannot be used as a commercial runtime dependency without a separate
negotiated licence. A caller must supply the complete MIT/CC-BY-NC-4.0 license,
notice, model-card and attribution texts plus a reviewed product/output-use
decision before any release gate can reopen.

`report.json`, `contract.json`, `report.json.sha256` and `SOURCES.sha256` are
generated task-local artifacts covered by the `.license` sidecars in this
directory. No upstream license text is copied because no upstream artifact is
included.
