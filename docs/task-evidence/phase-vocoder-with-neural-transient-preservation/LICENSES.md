<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# Licensing and asset boundary

This package is task-local feasibility evidence only. It contains no vendored
third-party source, no model weights, no checkpoints, no audio, no binaries and
no generated candidate outputs.

| Surface | Status | Notes |
| --- | --- | --- |
| Task-local Python/Markdown/JSON/digest files | Apache-2.0 | Authored for this task; SPDX headers/sidecars included. |
| Pinned source research files | Read-only external inputs | SHA-256 pinned in `SOURCES.sha256`; not copied, modified or redistributed by this package. |
| Candidate source/runtime/weights/config | Absent | No file present, downloaded, loaded or executed. No license text staged. |
| Rights-cleared speech/music inputs | Absent | No audio or corpus material present. |
| Candidate outputs/metrics | Absent | No runtime result exists; report is a blocker/readiness record only. |

The unpopulated asset declaration schema requires rights fields to be `false`
or `null` and rejects any presence/rights claim. Any future intake must supply
reviewed code, weight, training-data, input, output-use and redistribution
terms at immutable identities before qualification can be reconsidered.
