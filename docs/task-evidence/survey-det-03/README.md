<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-DET-03 — overlapping speech detection and speaker count evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`DET-03` (Overlapping speech detection and speaker count, legacy family
`F05`). It matches the catalogued classic and ML method families, the single
named source lead (`S02`) and the available adjacent historical executions to
existing components. It creates **no new execution, model, corpus, provider,
detector, ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-DET-03`; independent reviewer not dispatched.
Claim base: audio-sdk `8213704719f641582db9493788305f2cd3629354`; branch
`swarm/SDK-SURVEY-DET-03`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to pool

Overlapping speech detection reports whether simultaneous speech is present and
may estimate an active-speaker count. It is **not** speech activity detection
(`DET-01`), endpointing (`DET-02`), sound-event analysis (`DET-04`),
target-speaker VAD (`DET-05`), source separation (`SPK-01`), target-speaker
extraction (`SPK-02`), speaker-change segmentation (`SPK-03`), anonymous
diarization (`SPK-04`), speaker identity (`SPK-05`), beamforming (`CLN-07`) or
source localization (`CLN-08`). Those rows are named only as boundaries; their
results are **not pooled** into a DET-03 claim. Detection neither separates
waveforms nor identifies unwanted speech.

The local record contains **no dedicated overlap-detection or speaker-count
execution**. The only local rows are adjacent: an any-speaker VAD comparison,
a positive-span-only VAD diagnostic and a synthetic additive-mixture
construction from non-overlap turns. None produces an overlap interval, a
natural-overlap label or an active-speaker count. Pyannote, diarization,
embedding, BIC and spatial rows have no staged weights, runtime, calibrated
array or local execution.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: energy/spectral activity statistics with thresholds or adaptive noise floors | `fixed-rms-vad`, `adaptive-energy-vad`, `webrtc-vad`, `speexdsp-vad`, plus the adjacent Silero/fast-vad/Earshot rows: held-out AMI any-speech comparison on three speaker-disjoint meetings | Any-speaker VAD only; no overlap intervals, overlap labels or speaker count. High false-alarm and miss trade-offs remain visible in the adjacent VAD record |
| Classic: spatial statistics from calibrated arrays, beamforming and direction-of-arrival | `delay-and-sum-beamformer`, `mvdr-beamforming`, `source-localization-direction-of-arrival`, `auxiva`, `spatialnet` (considered or blocked) | No array geometry, synchronized multichannel recording, local beamformer/DoA run or overlap result. Mono activity cannot validate a spatial overlap detector |
| Classic: statistical speaker-change segmentation such as BIC | `bayesian-information-criterion-speaker-segmentation` (considered) | No local BIC implementation or boundary/count result; speaker change is not overlap truth |
| ML: multi-label neural segmentation | `pyannote-segmentation-vad` (blocked) | No weights, checkpoint, token, exact revision, runtime, adapter or local inference; no capability inferred from the model card |
| ML: diarization and clustering for active speaker count | `pyannote-diarization` (considered) | No local diarization run or count metric; diarization is adjacent, not overlap detection |
| ML: speaker representation and embedding controls | `x-vector-speaker-embeddings` (considered), `resemblyzer-speaker-similarity-proxy` and `speechbrains-ecapa-speaker-similarity` (partial research controls) | Identity/similarity proxies only; no active-speaker count or overlap truth and no identity claim |
| ML: separation, extraction and personal-VAD boundary | `conv-tasnet`, `beam-tasnet-beam-guided-tasnet`, `target-speaker-extraction-family`, `voicefilter`, `voicefilter-lite-personal-vad` | Catalogued separation/extraction candidates, not overlap detectors; no clean-target overlap corpus or local execution |

`report.json` holds the full records: both catalogued branches, the `S02`
source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
counts are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Seven-candidate held-out AMI any-speech VAD comparison | WebRTC, Silero, fast-vad, Earshot, SpeexDSP, adaptive RMS, fixed RMS | Three speaker-disjoint meetings, 20 ms frames; 0 overlap intervals, 0 overlap metric rows, 0 count estimates |
| `HE-2` | audEERING positive-span-only VAD diagnostic | The same seven adjacent VAD candidates | Four recordings, 588 annotated positive spans; no speaker IDs or overlap labels; complement unknown |
| `HE-3` | Hush synthetic AMI speaker-pair mixtures | `hush` | One meeting, seven directed pairs, 21 additive mixtures at +12/+18/+24 dB; not natural overlap and no detector/count |

Comparison inputs separate the adjacent any-speech VAD rows, the synthetic
overlap construction, the pyannote model card, source-reported overlap corpus
metadata and the **missing** rights-qualified overlap reference, pyannote
runtime/weights and frozen overlap/count benchmark. Published corpus and model
claims are source-reported only; no audio, labels, permissions, scored regions
or split is staged.

## Evidence classes and failure envelope

- **Historical local adjacent any-speech:** `HE-1`, `HE-2`. These establish
  that VAD has been compared on AMI and positive-only audEERING spans; they do
  not establish overlap detection or speaker count.
- **Historical local synthetic overlap construction:** `HE-3`. Constructed
  additive examples from non-overlap turns in one mono meeting demonstrate a
  fixture path, not natural overlap, clean references or detection quality.
- **Source-reported only:** `S02` pyannote card, overlap/diarization corpus
  metadata, BIC/spatial rows, embedding controls and separation/extraction
  rows. None is reproduced or locally run.
- **Not present:** a natural-overlap local execution, an overlap-label scorer,
  an active-speaker-count execution, pyannote weights/runtime, calibrated array
  geometry, target-device timing, listening, a passed benchmark or a release.
- The failure envelope is adverse: the available AMI VAD rows report
  false-alarm/miss trade-offs on any-speech truth, not overlap truth; the Hush
  AMI mixtures are explicitly synthetic and reduced target SI-SDR/STOI on the
  cited task; the positive-only audEERING record has an unknown complement.
  None of these is evidence that an overlap detector or speaker counter works.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G03`, `G04`, `G05`,
`G06`, `G07`, `G08`) link **existing** spatial, BIC, pyannote, embedding,
speaker-change, diarization and extraction rows. Gaps without a dedicated
category row (`G01`, `G02`, `G09`, `G10`) link existing research-control or
foundation rows and carry a `no dedicated DET-03 ...` owner note. Those links
are scoping leads only: no detector is enabled, no capability is implemented
and no missing result is promoted. Board status is excluded from all gates;
only linked `id`/`title`/`mode` are projected to a stable digest. The mutable
board file is referenced by path and **never hashed into canonical bytes**, so
status edits elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

No overlap-detection, speaker-count, separation, diarization, identity,
benchmark, device-timing or release claim is made. No audio, labels, weights,
provider enablement, default, ABI, build or CI change is included. All files are
inside this task directory; board, handoff and reviewers were not changed or
dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, repeats the build in three cold-start
processes and rejects any out-of-scope change; `test_reference.py` checks
canonical output, adverse rejections and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-det-03
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `8223e0de13fb83ea32686ff1379ace9ea8285a9c30845c70f3d8d5ea77cc98c9`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
