<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-07 — beamforming and spatial-filtering evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-07` (Beamforming and spatial filtering, legacy family `F07`). It matches
the catalogued method families, the named source leads (`S24`, `S25`) and
historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-07`; independent reviewer:
`reviewer-SURVEY-CLN-07`. Claim base: audio-sdk
`afe0d324ab5534cc45297f4c7361c87c0cc1f005`; branch
`swarm/SDK-SURVEY-CLN-07`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map does and does not cover

The catalogued boundary is explicit: a beamformer consumes **synchronized array
channels plus declared spatial assumptions** and outputs a waveform. Extra
microphones, oracle masks and oracle steering are different comparison groups,
and geometry and channel mismatch matter. A mono suppressor, dereverberator,
localization estimator, source separator, target-speaker extractor or echo
canceller is a different catalogued task and is not pooled into a CLN-07 claim.

`CLN-08` (source localization and tracking), `CLN-04` (dereverberation),
`SPK-01` (generic source separation), `SPK-02` (target-speaker extraction) and
`CLN-05` (reference-based AEC) are named only as boundaries. Their results are
not pooled here. The two adjacent multichannel WPE runs are cited strictly as
array-fixture, channel-influence and clean-preservation controls; WPE is
dereverberation, is **not** a beamformer, and stays outside every CLN-07
outcome.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: delay-and-sum with explicit steering delays and equal weighting | `delay-and-sum-beamformer` and `pyroomacoustics-candidate-tools` (considered) | Catalogued only; no local implementation, frozen array fixture or execution |
| Classic: MVDR/MPDR with noise-only or mask covariance estimation | `mvdr-beamforming`, `3d-microphone-spatial-time-alignment`, `pyroomacoustics-candidate-tools` (considered) | Catalogued only; the `SDK-MVDR-BEAMFORMING` feasibility contract already requires validation against delay-and-sum |
| ML: learned masks or spatial statistics feeding an MVDR-style beamformer | `mvdr-beamforming` (considered), `neural-beamforming` (blocked), `h-gtcrn` (considered, conditional two-microphone candidate) | Mask-based family has no staged model, array geometry, target definition or local score; H-GTCRN terms/hashes and stereo data are unverified |
| ML: neural spatial filters and end-to-end multichannel separation-plus-beamforming | `spatialnet` and `beam-tasnet-beam-guided-tasnet` (blocked), `auxiva` (considered, boundary) | No exact checkpoint, adapter or synchronized multichannel target corpus; Beam-TasNet and Beam-Guided TasNet remain distinct unresolved architectures |

`report.json` holds the full records: both catalogued branches, the `S24`/`S25`
source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Source-reported
claims are transcribed with their original scope; they are **not** rerun, pooled
into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Adjacent offline two-channel multichannel WPE synthetic regression screen | `offline-multichannel-wpe` | 16,960 samples; three synthetic RIR strata; ΔSI-SDR −1.863045 / −0.570465 / −0.639980 dB; **not a beamformer** |
| `HE-2` | Adjacent causal two-channel multichannel WPE synthetic regression screen | `online-multichannel-wpe` | 25,600 samples; ΔSI-SDR −7.257785 / −2.480089 / −1.136101 dB; 480-sample content delay; **not a beamformer** |

Comparison inputs separate source-only beamformer documentation (`S24`, `S25`),
an adjacent two-channel synthetic dereverberation fixture, a **missing**
rights-cleared synchronized array corpus, a **missing** separated
oracle-mask/steering group, source-only blocked neural candidates and a
source-only competition scenario group. Every historical row says "not rerun by
this survey" and "not a beamforming result".

## Evidence classes and failure envelope

- **Source-only documentation:** Pyroomacoustics beamforming docs (delay-and-sum,
  MVDR, MPDR, SRP-PHAT) and the TorchAudio mask-based MVDR tutorial. No package,
  model, array audio or local score is staged.
- **Adjacent historical local:** the offline and causal multichannel WPE
  synthetic screens. These prove deterministic behavior on the merged CLN-04
  fixtures, not beamforming gain or array calibration.
- **Source-reported only:** SpatialNet, Beam-TasNet/Beam-Guided TasNet, neural
  beamforming, H-GTCRN, CHiME-6 multi-array recipes and L3DAS23 ambisonic
  beamforming. Candidate and upstream claims are never relabelled as local
  measurements.
- **Not present:** rights-cleared synchronized array corpus, measured geometry
  or channel calibration, pinned delay-and-sum/MVDR source or runtime, neural
  spatial weights, oracle-mask/steering separation, held-out array labels,
  human listening, target-device timing, provider parity and release approval.

The failure envelope is explicit: the adjacent WPE runs regress in SI-SDR in
every paired near-end condition (worst short-RT60 ΔSI-SDR −7.257785 dB for the
causal variant) and are included only to show that multichannel synthetic
fixtures exist and expose channel influence. They are not evidence that a
beamformer works.

## Bounded gaps and feasibility links

Eight gaps are recorded. `G01`–`G07` link **existing** feasibility or
foundation rows (`delay-and-sum`, MVDR, SpatialNet, Beam-TasNet, neural
beamforming, H-GTCRN, 3D microphone alignment, timing, duplex, audit and
evidence). `G08` has no dedicated CLN-07 feasibility owner; it links existing
research-control rows for listening and metric design and carries a
`no dedicated CLN-07 ...` owner note. Those links are scoping leads only: no
processor is enabled, no capability is implemented, and no missing result is
promoted. Board status is excluded from all gates; only linked `id`/`title`/
`mode` are projected to a stable digest. The mutable board file is referenced
by path and **never hashed into canonical bytes**, so status edits elsewhere in
the swarm cannot change this map or break its digest.

## Release boundary

Keep beamforming, localization, dereverberation, separation, target extraction
and echo cancellation separate; keep oracle masks/steering and estimated
groups separate; keep synthetic, adjacent, source-reported and missing results
distinct. No public benchmark/quality/device/listening/release claim is made. No
assets, real array audio, weights, provider enablement, default, ABI, build or CI
change is included. All files are inside this task directory; board, handoff and
reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-07
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `aad53c0a3e6d90c4d27fea6abb4001d40168700a8fa2d717f53b03091a9c5a6a`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
