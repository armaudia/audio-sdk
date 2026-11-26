<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary — SDK-PODCASTFILLERS

This package contains task-local evidence code and machine-readable records
only. No PodcastFillers dataset audio, annotation, label, model weight, or
runtime binary is vendored.

| Item | License / status | Notes |
| --- | --- | --- |
| This evidence package (`docs/task-evidence/podcastfillers/**`) | Apache-2.0 | SPDX headers/sidecars present; covered by repository `REUSE.toml` `docs/**` rule. |
| PodcastFillers annotations (recorded claim) | Non-commercial (separate terms) | Exact terms bundle not staged; not a rights basis for commercial SDK use. No annotation data included. |
| PodcastFillers audio/data | Not present | No dataset acquisition performed; research acquisition remains outside SDK artifact. |
| VAD/ASR/classifier pipeline idea | N/A (concept only) | No code, model, or runtime imported, built, or executed. |

No third-party license text is vendored because no third-party asset is present.
A future intake must supply exact terms, rights review, and a written
commercial/output-use decision before any data/model use.
