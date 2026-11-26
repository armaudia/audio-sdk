<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance for SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION evidence

This task-local package is authored under `Apache-2.0`. SPDX copyright and
license declarations appear at the top of every source and Markdown file in this
directory. `REUSE.toml` aggregates `docs/**` under Apache-2.0; `.license`
sidecars and source headers make the declaration explicit for generated
artifacts.

**No candidate asset is present.** No text-aware filler/stutter annotation
model, checkpoint, weights, runtime, ASR transcript source, cleanup stage,
disfluency target protocol, audio, corpus, listening result, or third-party
license text is copied, vendored, downloaded, or redistributed here. The
referenced research reports and inventory records are read-only workspace
provenance pinned by SHA-256 only; no bytes are merged into this package.

Generated artifacts (`report.json`, `report.json.sha256`, `contract.json`,
`SOURCES.sha256`) carry adjacent SPDX sidecars. A file cannot pin its own bytes,
so `SOURCES.sha256` excludes itself; `contract.json` is excluded from its own
`artifact_pins` but is pinned by `SOURCES.sha256`; `report.json` is pinned by its
sidecar, by `contract.json`, and by `SOURCES.sha256`.

Any future candidate asset must arrive with byte-identical license text, a full
40-hex source revision, a pinned tree digest, exact checkpoint/runtime identity,
written rights/consent/output-use/redistribution decisions, and a frozen
semantic-preservation/disfluency target protocol. Until then licensing remains
blocked and no result qualifies the candidate.

`SOURCES.sha256` never pins the mutable full
`audio-benchmark-platform/plan/swarm/TASKS.json`. Only the stable linked-row
identity (`id`, `title`, `mode`, `repository`, `component`) is read and gated.
