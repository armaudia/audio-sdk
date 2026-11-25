<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# License and rights boundary — SDK-ATENNUATE-0-1-1

This task-local evidence package is Apache-2.0. It ships no upstream source,
wheel, checkpoint, weight, model card, license text or notice file. No
third-party artifact was copied, vendored, downloaded or redistributed.

## Upstream metadata recorded, not cleared

| Item | Recorded metadata | Status here |
| --- | --- | --- |
| `attenuate==0.1.1` package | Apache-2.0 per the PyPI package page | metadata only; wheel bytes absent |
| `PeaBrane/aTENNuate` checkpoint | Apache-2.0 per the Hugging Face model card | metadata only; checkpoint bytes absent |
| aTENNuate code repository | Apache-2.0 metadata; the adapter README records a malformed package source URL and an unavailable linked source location | provenance unresolved |
| Training data | not established by the pinned ledger | unresolved |
| CBS/speech codec training material | not established | unresolved |
| Third-party notices | not supplied | unresolved |

Apache-2.0 metadata is **not** an artifact-specific rights clearance. The exact
checkpoint terms, training-data provenance, third-party notices and a written
redistribution/product-use decision are required before any artifact enters the
package or a release. See `RG-03` and `BLK-03`.

## This package's files

- `reference.py`, `run.py`, `test_reference.py`, `verify.py`: Apache-2.0 with
  explicit SPDX headers.
- `README.md`, `LICENSES.md`: Apache-2.0 with explicit SPDX headers.
- `contract.json`, `report.json`, `report.json.sha256`, `SOURCES.sha256`: each
  has a `.license` REUSE sidecar with the same Apache-2.0 identifier and
  copyright line.

No `LICENSE`, `NOTICE`, `COPYING` or third-party license text is copied into
this directory. `LICENSES/Apache-2.0.txt` remains the shared SDK license text
and is pinned read-only by `SOURCES.sha256`.
