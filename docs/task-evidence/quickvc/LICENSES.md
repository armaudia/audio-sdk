<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and provenance for SDK-QUICKVC evidence

This task-local package is authored under `Apache-2.0`. The SPDX copyright and
license declarations appear at the top of every source and Markdown file in this
directory. The repository's `REUSE.toml` aggregates `docs/**` under Apache-2.0;
the `.license` sidecars and source headers make the REUSE declaration explicit
for generated artifacts.

**No QuickVC or ContentVec candidate asset is present.** No QuickVC checkpoint,
HuBERT/ContentVec encoder snapshot or config, accent-target model, runtime,
corpus, audio file, listening result or vendor license text is copied, vendored,
downloaded or redistributed here. A generic LLVC QuickVC architecture checkout
and its MIT license text are read-only workspace provenance at revision
`1627c5d358cf9bb2b92b0ccc513d8b36807c923d`; the checkout is not executed and
is not presented as an accent converter. The package therefore carries no
third-party license obligation beyond the repository's own Apache-2.0 terms.

The research records, inventory records, verification profile, CONTRACTS.md and
boundary headers referenced by `SOURCES.sha256` are read-only inputs in the
local `audioml` workspace. They are pinned by SHA-256 only; no bytes are merged
into this package.

Generated artifacts (`report.json`, `report.json.sha256`, `contract.json`,
`SOURCES.sha256`) carry adjacent SPDX sidecars. A file cannot pin its own bytes,
so `SOURCES.sha256` excludes itself; `contract.json` is excluded from its own
`artifact_pins` but is pinned by `SOURCES.sha256`; `report.json` is pinned by its
sidecar, by `contract.json` and by `SOURCES.sha256`.

Any future candidate asset must arrive with byte-identical license text, a full
40-hex source revision, and written code, weight, training-data, reference-voice
consent, output-use and redistribution decisions. Until then licensing remains
blocked and no result qualifies the candidate.

`SOURCES.sha256` never pins the mutable full
`audio-benchmark-platform/plan/swarm/TASKS.json`. Only the stable linked-row
identity (`id`, `title`, `mode`, `repository`, `component`) is read and gated.
