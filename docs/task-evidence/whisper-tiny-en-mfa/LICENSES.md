<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary for `whisper-tiny-en-mfa`

This task-local evidence package is Apache-2.0. It vendors no third-party
source, weight, acoustic model, dictionary, audio, transcript, annotation or
binary. The upstream artifacts below are named and, where recorded, pinned by
SHA-256 only. **None is distributed by this package.**

| Component | Recorded terms | Review status |
| --- | --- | --- |
| OpenAI Whisper `tiny.en` / `openai-whisper==20250625` | MIT (recorded in the research report) | Not reviewed here; no package archive, source revision or MIT notice file is staged. |
| MFA 3.4.3 (`english_us_arpa` acoustic model and dictionary, Conda Forge) | CC-BY-4.0 model card (recorded) | Not reviewed here; no archive, source revision, license text, attribution file or output-use decision is staged. |
| AMI EN2003a crop and `A.words` annotation | CC BY 4.0 (recorded; attribution required) | Not reviewed here; no audio, annotation, attribution file or output-use decision is staged. |

There is no redistribution approval, commercial/product-use approval, generated
output-use approval or model-card review for Whisper, MFA or the AMI corpus in
this package. The recorded license identifiers are provenance notes from the
research report, not a grant. A caller must supply the complete license,
notice, model-card and attribution texts and a reviewed product/output-use
decision before any release gate can reopen.

`report.json`, `contract.json`, `report.json.sha256` and `SOURCES.sha256` are
generated task-local artifacts covered by the `.license` sidecars in this
directory. No upstream license text is copied because no upstream artifact is
included.
