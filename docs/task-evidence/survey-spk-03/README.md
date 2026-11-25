<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-SPK-03 — speaker change detection and segmentation evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`SPK-03` (Speaker change detection and segmentation, legacy family `F06`). It
matches the catalogued classic and ML method families, both named source leads
(`S04`, `S02`) and the available adjacent historical executions to existing
components. It creates **no new execution, model, corpus, provider,
segmenter, ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-SPK-03`; independent reviewer not dispatched.
Claim base: audio-sdk `f9b95afa668623733d0d8fd25f616d3b65172fd9`; integration
base at generation time: `98234bb363064e5374b8b3654ca019cc90410610`; branch
`swarm/SDK-SURVEY-SPK-03`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to pool

Speaker change detection marks a boundary between locally homogeneous speaker
segments. It may also emit the segments themselves. It is **not** speech
activity detection (`DET-01`), endpointing or turn completion (`DET-02`),
overlapping speech detection or speaker count (`DET-03`), generic source
separation (`SPK-01`), target-speaker extraction (`SPK-02`), anonymous
diarization (`SPK-04`), speaker identification/verification (`SPK-05`),
beamforming (`CLN-07`) or source localization (`CLN-08`). Those rows are named
only as boundaries; their results are **not pooled** into an SPK-03 claim. A
change point does not link a speaker's later turns and does not give a personal
identity.

The local record contains **no dedicated speaker-change or segmentation
execution**. The only local rows are adjacent: an any-speaker VAD comparison
with utterance onset/offset diagnostics, a positive-span-only VAD diagnostic
and a synthetic additive-mixture construction from non-overlap AMI turns. None
produces a speaker-change boundary, a locally homogeneous segment label, a
segment-purity score or a speaker link. The BIC row is `considered`; pyannote
segmentation is `blocked`; pyannote diarization, x-vector embeddings and the
separation/extraction rows are `considered` or `blocked`; the Resemblyzer and
ECAPA similarity rows are `partial` identity controls. No BIC implementation,
pyannote weights, runtime, token or adapter is staged.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: adjacent-window energy/spectral statistics with thresholds or adaptive noise floors | `fixed-rms-vad`, `adaptive-energy-vad`, `webrtc-vad`, `speexdsp-vad`; the held-out AMI any-speech comparison also covers Silero, fast-vad and Earshot | Activity detection only. Its onset/offset values are utterance boundaries, not speaker-change boundaries, and it emits no segment label or speaker link. |
| Classic: Bayesian information criterion (BIC) speaker-change segmentation over adjacent windows with a model-selection penalty | `bayesian-information-criterion-speaker-segmentation` (`S04`) | Considered only. No local implementation, window/hop/penalty configuration, annotated change-point cohort, boundary score or segment-purity result exists. |
| ML: neural segmentation of speaker turns and change points | `pyannote-segmentation-vad` (`S02`) | Blocked. The candidate register and audit report no staged weights, checkpoint, token, exact revision, runtime or adapter; no inference and no boundary metric. |
| ML: neural diarization and embedding clustering for anonymous speaker labels | `pyannote-diarization`, `x-vector-speaker-embeddings` | Considered only. Diarization labels who spoke when; it is not a change-point detector or speaker link. No local run or segment purity result. |
| ML: speaker-embedding similarity controls adjacent to identity | `resemblyzer-speaker-similarity-proxy`, `speechbrains-ecapa-speaker-similarity` | Partial research controls only. Similarity is not a change point, a segment label or an identity claim, and is not pooled here. |
| ML: separation, target-speaker extraction and personal-VAD boundary | `conv-tasnet`, `beam-tasnet-beam-guided-tasnet`, `target-speaker-extraction-family`, `voicefilter`, `voicefilter-lite-personal-vad` | Catalogued separation/extraction candidates, not change detectors. No local execution or change-point reference; results are not pooled. |

`report.json` holds the full records: both catalogued branches, both source
leads, the component census checked against `INVENTORY.json`, comparison
inputs, controls, assets, local versus reported outcomes, acceptance mapping,
gaps, board links and all eight blocked release gates. Historical counts are
transcribed verbatim from pinned reports with their original scope; they are
**not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Seven-candidate held-out AMI any-speech VAD comparison with utterance boundary diagnostics | WebRTC, Silero, fast-vad, Earshot, SpeexDSP, adaptive RMS, fixed RMS | Three speaker-disjoint meetings, 20 ms frames; 0 change-point intervals, 0 change-point metric rows, 0 segment-purity rows, no speaker-boundary labels |
| `HE-2` | audEERING positive-span-only VAD diagnostic | The same seven adjacent VAD candidates | Four recordings, 588 annotated positive spans; no speaker IDs or change labels; complement unknown; 0 change-point estimates |
| `HE-3` | Hush synthetic AMI speaker-pair mixtures | `hush` | One meeting, seven directed pairs, 21 additive mixtures at +12/+18/+24 dB; turn speaker IDs known, no isolated tracks, not natural speaker change, 0 change-point estimates |

Comparison inputs separate the adjacent any-speech VAD rows, the synthetic
speaker-pair construction, the BIC method paper, the pyannote model card and the
**missing** rights-qualified speaker-change reference, BIC/pyannote
runtime/weights and frozen change-point benchmark. Published papers and model
claims are source-reported only; no audio, change labels, segment truth,
permissions, scored regions or split is staged.

## Evidence classes and failure envelope

- **Historical local adjacent any-speech:** `HE-1`, `HE-2`. These establish
  that VAD has been compared on AMI and positive-only audEERING spans; they do
  not establish speaker-change detection or segmentation.
- **Historical local synthetic speaker-pair construction:** `HE-3`.
  Constructed additive examples from non-overlap turns in one mono meeting
  demonstrate a fixture path, not natural speaker change, segment truth or
  boundary quality.
- **Source-reported only:** `S04` BIC paper, `S02` pyannote card, BIC and
  pyannote plan rows, embedding controls and separation/extraction rows. None
  is reproduced or locally run.
- **Not present:** a natural speaker-change local execution, a change-point
  scorer, a segment-purity execution, a BIC implementation, pyannote
  weights/runtime, independent boundary-label review, target-device timing,
  listening, a passed benchmark or a release.
- The failure envelope is adverse: the available AMI VAD rows report
  false-alarm/miss trade-offs on any-speech truth, not speaker-change truth;
  the Hush AMI mixtures are explicitly synthetic and reduced target SI-SDR/STOI
  on the cited task; the positive-only audEERING record has an unknown
  complement. None of these is evidence that a change detector or segmenter
  works.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G03`, `G04`, `G06`,
`G09`) link **existing** BIC, pyannote, embedding, diarization, extraction and
personal-VAD rows. Gaps without a dedicated category row (`G01`, `G02`, `G05`,
`G07`, `G08`, `G10`) link existing research-control or foundation rows and
carry a `No dedicated ...` owner note. Those links are scoping leads only: no
segmenter is enabled, no capability is implemented and no missing result is
promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

No speaker-change, segmentation, diarization, identity, overlap, endpointing,
separation, benchmark, device-timing or release claim is made. No audio,
change labels, weights, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and
reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, repeats the build in three cold-start
processes and rejects any out-of-scope change; `test_reference.py` checks
canonical output, adverse rejections and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-spk-03
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `c0d86aa1bc19bcc8720ac4c06610dd4747a05b95b18928b284f19a473e81eaf5`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is not
modified or exercised by this task because no integration surface changed; it
remains a release-time check for changes that do touch an installed surface.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
