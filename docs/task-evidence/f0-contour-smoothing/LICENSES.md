<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance for SDK-F0-CONTOUR-SMOOTHING evidence

This task-local package is authored under `Apache-2.0`. The SPDX copyright and
license declarations appear at the top of every source, Markdown and generated
artifact in this directory. The repository's `REUSE.toml` aggregates `docs/**`
under Apache-2.0; the `.license` sidecars and source headers make the REUSE
declaration explicit for generated artifacts.

**No upstream candidate artifact is present.** No F0-contour smoother source,
header, weight, checkpoint, parameter set, target contour, voicing policy, pitch
reference pair, runtime, corpus, audio file, listening result or vendor license
text is copied, vendored, downloaded or redistributed here. The package
therefore carries no third-party license obligation beyond the repository's own
Apache-2.0 terms.

The research row, inventory record, verification profile and workspace plan
documents referenced by `SOURCES.sha256` are read-only inputs that exist in the
local `audioml` workspace. They are pinned by SHA-256 only; no bytes are merged
into this package.

Generated artifacts (`report.json`, `report.json.sha256`, `contract.json`,
`SOURCES.sha256`) carry adjacent SPDX sidecars. A file cannot pin its own bytes,
so `SOURCES.sha256` excludes itself; `contract.json` is excluded from its own
`artifact_pins` but is pinned by `SOURCES.sha256`; `report.json` is pinned by
its sidecar, `contract.json` and `SOURCES.sha256`.

Any future candidate asset must arrive with a byte-identical license text, a
full 40-hex source revision and a written rights/consent/output-use decision.
Until then the licensing status is deliberately blocked and no result
qualifies the candidate.

`SOURCES.sha256` never pins the mutable full
`audio-benchmark-platform/plan/swarm/TASKS.json`. Only the stable linked-row
identity (`id`, `title`, `mode`, `repository`, `component`) is read and gated.
