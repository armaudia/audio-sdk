<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-08 — source localization and tracking evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-08` (Source localization and tracking, legacy family `F07`). It matches
the catalogued method families, the named source lead (`S26`) and the available
adjacent historical executions to existing components. It creates **no new
execution, model, corpus, provider, processor, ABI, default, build, CI, board,
handoff or release change**.

Survey owner: `agent-SURVEY-CLN-08`; independent reviewer not dispatched.
Claim base: audio-sdk `0ff69ead80e380d758dbe03057790e62d303e284`; branch
`swarm/SDK-SURVEY-CLN-08`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-cln-08/` only |
| Owner and independent reviewer | `agent-SURVEY-CLN-08`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-25, `swarm/SDK-SURVEY-CLN-08`, `SDK-SURVEY-CLN-08`, `0ff69ead80e380d758dbe03057790e62d303e284` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no provider, recipe, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S26` Pyroomacoustics DOA documentation search excerpt plus the pinned read-only documents in `SOURCES.sha256` |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-cln-08/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is **metadata**: an angle, location or track that can
support steering or selection. It is not a cleaned waveform, not a separated
source and not proof of intended-speaker identity. A beamformer or separator may
consume a direction, but its waveform result is a different category and is not
pooled here.

`CLN-07` (beamforming and spatial filtering), `SPK-01` (generic separation),
`SPK-02` (target-speaker extraction), `SPK-04`/`SPK-05` (diarization and speaker
identity) and `ENG-02` (clock alignment) are named only as boundaries. Their
rows are not localization evidence and are never pooled into a CLN-08 claim.

No CLN-08 component has a local implementation, run, angle output or track. The
component `source-localization-direction-of-arrival` is `considered` only. Two
merged multichannel WPE fixtures are reused as **adjacent geometry controls**:
they declare a synthetic source angle, microphone spacing and channel delays,
but they apply dereverberation, emit no direction and are labelled "not a
localization result".

## Method families and mapped evidence

| Catalogued family | Mapped component | Status and boundary |
| --- | --- | --- |
| Classic: steered response power with phase transform (SRP-PHAT) | `source-localization-direction-of-arrival` (considered) | Catalogued method only; no local implementation, geometry check, ambiguity handling or abstention behavior |
| Classic: subspace estimation with MUSIC and NormMUSIC | `source-localization-direction-of-arrival` (considered) | Catalogued method only; no local implementation, source-count assumption or subspace result |
| ML: learned spatial-feature estimators | `source-localization-direction-of-arrival` (considered) | Candidate search is **pending**; no catalogued candidate declares a direction output, and no checkpoint or licensed weights are staged |

The adjacent `SpatialNet`, `neural beamforming` and `Beam-TasNet /
Beam-Guided TasNet` rows are blocked **spatial-enhancement or separation**
candidates, not locators. `pyannote diarization` and `x-vector speaker
embeddings` answer who spoke or who is speaking, not where. None is relabelled
and none contributes a CLN-08 result.

`report.json` holds the full records: both catalogued branches, the `S26`
source-lead mapping, the component census checked against `INVENTORY.json`,
adjacent boundaries, comparison inputs, controls, assets, execution coverage,
local versus reported outcomes, acceptance mapping, ten gaps, board links and
all eight blocked release gates. Adjacent numbers are transcribed verbatim from
pinned merged reports with their original scope; they are **not** rerun, pooled
into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Adjacent offline multichannel WPE synthetic fixture with declared two-channel geometry | `offline-multichannel-wpe`, `3d-microphone-spatial-time-alignment` | 6 cm spacing, source angle 35°, second source −50°; whole-clip dereverberation only; no direction or track |
| `HE-2` | Adjacent online multichannel WPE synthetic fixture with declared source azimuth | `online-multichannel-wpe`, `3d-microphone-spatial-time-alignment` | 4 cm spacing, azimuth 30°, 0/5-sample microphone delays, 480-sample content delay; frame-causal dereverberation only; no direction or track |

Comparison inputs separate the two adjacent synthetic fixtures, the source-only
`S26` protocol, the blocked ML candidate rows, and the **missing** labelled
localization corpus, calibrated real-array metadata and held-out scoring split.
Every historical row says "not a localization result" and "not rerun by this
survey". Geometry in a dereverberation fixture is not a calibrated array and is
not an angle estimate.

## Evidence classes and failure envelope

- **Adjacent historical local synthetic:** the offline and online multichannel
  WPE fixtures. They prove deterministic room processing on declared synthetic
  geometry; they do not localize.
- **Source-only frozen protocol:** the `S26` documentation excerpt names
  SRP-PHAT, MUSIC and NormMUSIC but supplies no pinned package, runtime,
  geometry, labels or numeric result.
- **Source-reported candidate gap:** the category survey found no dedicated
  runnable neural-localization candidate; blocked SpatialNet, neural-beamforming
  and Beam-TasNet rows are not direction estimators.
- **Missing:** any CLN-08 implementation or execution, labelled angular/track
  corpus, calibrated real array, timestamp/drift measurement, metric
  implementation, human annotation, benchmark or release result.
- **Deliberately not claimed:** front/back mirror resolution, moving-source
  tracking, identity, steering gain, target extraction, listening quality and
  device timing.

The failure envelope is explicit: a forced angle on silence, noise or a single
channel is an error, not a low-information success; a mirrored solution without
an ambiguity report is not a pass; and a fixed-beam gain is not an angular
accuracy result.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps `G01`–`G08` link existing feasibility or foundation
rows; `G09` and `G10` link the asset-boundary and evidence foundations and carry
a `no dedicated CLN-08 ...` owner note. The dedicated
`SDK-SOURCE-LOCALIZATION-DIRECTION-OF-ARRIVAL` row is a scoping lead only: no
processor is enabled, no capability is implemented, and no missing result is
promoted. Board status is excluded from all gates; only linked `id`/`title`/
`mode` are projected to a stable digest. The mutable board file is referenced by
path and **never hashed into canonical bytes**, so status edits elsewhere in the
swarm cannot change this map or break its digest.

## Release boundary

Keep localization metadata separate from beamforming, separation, extraction,
diarization and identity. Keep declared synthetic geometry separate from a
calibrated real array. Keep documentation, blocked candidate rows, adjacent
fixtures and missing results distinct. No public benchmark, quality, device,
listening, identity, steering or release claim is made. No assets, real array
audio, weights, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and reviewers
were not changed or dispatched. `DEFER` remains in force until all eight release
gates close.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical output,
adverse rejections and three cold-start repeats. JSON and manifest files have
SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-08
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256 is recorded in `report.json.sha256` and printed
by `verify.py`. The change is task-local documentation and stdlib tooling; no
installed package, descriptor catalog, ABI, build input or CI workflow is
touched.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
