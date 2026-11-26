# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# Licensing and provenance

This evidence package is licensed under **Apache-2.0** (SPDX headers on the
text artefacts and `.license` sidecars for the JSON files).

## Upstream LLVC

The local research checkout at
`research/voice-conversion-eval-20261101/repos/llvc` is **KoeAI/LLVC** at commit
`1627c5d358cf9bb2b92b0ccc513d8b36807c923d` and is licensed **MIT** (upstream
`LICENSE` file, pinned in `SOURCES.sha256`). No upstream source file, test audio
file, model code or licence text is copied into this package. The checkout is
read-only evidence and is not executed.

## Checkpoint

`G_500000.pth` (source-reported 37.7 MiB) is **not present** in the workspace.
It is distributed through the upstream `KoeAI/llvc` download path. Its
redistribution terms, any embedded/generated data, and consent for the built-in
any-to-one target voice are **not established** here. No checkpoint, weight
fragment, embedding, surrogate or reconstruction is included.

## Historical evaluation references

The following local research artefacts are referenced by path and SHA-256 only;
they are not copied into this package and they are not re-run:

- `research/voice-conversion-eval-20261101/README.md` — historical evaluation
  narrative and source-reported measurements.
- `research/voice-enhancement-20261101/candidate_matrix.csv` — row 97,
  "LLVC any-to-one streaming VC".
- `research/voice-conversion-eval-20261101/results/llvc_asr.json` — historical
  one-utterance Whisper Tiny EN scoring record.
- `research/voice-conversion-eval-20261101/results/llvc/source_ljspeech_lj001-0001.wav`
  — historical converted output, retained only for digest provenance.
- `research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md` —
  crosswalk that recomputes the historical output digest and flags unconfirmed
  target-reference provenance.

The historical fixed source is described upstream as LJ Speech 1.1
`LJ001-0001.wav` (dataset page describes the recordings as public domain). The
historical p360 target reference comes from an upstream RT-VC demo and its
licence/provenance is **not independently confirmed**; no target reference
audio is used or included here.

## Absent rights decisions

No licence decision is recorded for the checkpoint, its built-in target voice,
or the historical target reference. Those decisions are release gate `RG-02`
and remain **blocked**. The MIT source licence does not automatically grant
rights to the trained weights or the target voice.
