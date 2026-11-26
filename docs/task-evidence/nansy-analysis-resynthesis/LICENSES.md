<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing boundary

This task-local evidence package is licensed under Apache-2.0. It contains no
third-party source, checkpoint, weight, config, analysis frontend, generator,
vocoder, model card, licence text, notice, corpus, speech, reference voice,
audio or manifest payload bytes.

## Upstream declarations, not staged licences

The pinned records name the NeurIPS 2021 "NANSY analysis and resynthesis paper"
and link
`https://proceedings.neurips.cc/paper_files/paper/2021/file/87682805257e619d49b8e0dfdc14affa-Paper.pdf`.
They record no official runnable code, weight, checkpoint or config, no licence
field, no licence text, no `COPYING`/`NOTICE` and no model card. This package
does not copy, download, verify or redistribute any upstream artefact. The
paper reference is source-reported context only.

## Required rights review before implementation

The following decisions must be reviewed and recorded separately before any
source, weight, runtime, input or output is used:

1. Code licence and notice obligations for the exact official revision.
2. Weight/model-card terms, including derivative and commercial use.
3. Training-data and corpus lineage, attribution and redistribution.
4. Reference and target voice consent, permitted use and revocation.
5. Availability of a rights-cleared evaluation cohort.
6. Output-use terms for resynthesised speech and any provider exposure.

No review decision is made or implied by this package. `DEFER` remains in
force and no result qualifies NANSY.

## No third-party bytes

No upstream source file, weight tensor, audio sample, paper PDF, table payload
or licence text is vendored. The pinned SHA-256 values cover local research
records that describe the candidate; they do not grant any licence.
