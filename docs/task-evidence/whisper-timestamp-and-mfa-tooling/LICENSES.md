<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licenses / rights boundary

This task-local evidence package contains only metadata, manifests, and stdlib
verification code authored for this task. No Whisper weights, MFA acoustic
models/dictionaries, AMI audio, transcripts, TextGrid files, runtime wheels, or
third-party source copies are vendored.

## Upstream/historical artifacts (not present here)

| Artifact | Recorded license / terms | Status here |
|---|---|---|
| OpenAI Whisper `tiny.en` / `openai-whisper==20250625` | MIT (per pinned historical report) | absent; no weight/package/notice bundle staged |
| Montreal Forced Aligner 3.4.3, `english_us_arpa` acoustic+dictionary | CC-BY-4.0 recorded for model card; MFA source terms not reviewed here | absent; no assets/runtime/notice bundle staged |
| AMI Meeting Corpus crop/annotations referenced by historical run | CC BY 4.0 (recorded) | absent; no audio/annotation copied; terms not reviewed |

## Decision

Rights/provenance gates remain **blocked**. This package makes no license
clearance, redistribution, benchmark, or release claim.
