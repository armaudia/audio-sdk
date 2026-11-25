<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-SPK-04 — anonymous speaker diarization evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`SPK-04` (Anonymous speaker diarization, legacy family `F06`). It matches the
catalogued classic and ML method families, both named source leads (`S06` and
`S47`) and the available adjacent historical local or source-reported records
to existing components. It creates **no new execution, model, corpus,
provider, processor, ABI, default, build, CI, board, handoff, benchmark or
release change**.

Survey owner: `agent-SURVEY-SPK-04`; independent reviewer not dispatched.
Claim base: audio-sdk `af941fdf40195d4b4893c5c0f361d636f5f2510d`; branch
`swarm/SDK-SURVEY-SPK-04`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested` / `catalogued` with candidate
census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-spk-04/` only |
| Owner and independent reviewer | `agent-SURVEY-SPK-04`; reviewer not dispatched |
| Claim time, branch and base commit | 2026-11-26, `swarm/SDK-SURVEY-SPK-04`, `af941fdf40195d4b4893c5c0f361d636f5f2510d` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no diarizer, metric scorer, provider, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S06` pyannote metric documentation and `S47` CHiME-8 pipeline are documentation leads; no weights, media, RTTM/UEM reference or corpus is staged. Exact document pins are in `SOURCES.sha256` |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-spk-04/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is a **timestamped map of anonymous speaker labels**
within a recording or session. It is not speech activity detection (`DET-01`),
endpointing (`DET-02`), overlapping-speech detection or speaker count
(`DET-03`), sound-event analysis (`DET-04`), target-speaker VAD (`DET-05`),
generic separation (`SPK-01`), target-speaker extraction (`SPK-02`),
speaker-change segmentation (`SPK-03`), speaker identity (`SPK-05`),
beamforming (`CLN-07`), source localization (`CLN-08`), transcription or
language identification. Those rows are named only as boundaries; their
results are **not pooled** into an SPK-04 claim.

The catalogued boundary is preserved verbatim in `report.json`: **overlap must
be represented and online revisions are possible; anonymous labels are not
enrolled identities.** A speech-activity timeline is not a speaker-label map.
A change point is not a session-wide anonymous cluster. A similarity score is
not a diarization label. A synthetic speaker-pair mixture is not a natural
meeting. A speaker ID used to build a test fixture is not a DER/JER result.

The reviewed records contain **no SPK-04 diarization execution**: no
session-level label map, no DER/JER or speaker-error score, no session
clustering run, no natural-meeting diarization and no online label revision.
Three adjacent local rows are included only to show what exists nearby, and
all are marked `adjacent: true`, `not_component_evidence: true` and "not rerun
by this survey". No missing result is promoted to a pass.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Segmentation plus statistical speaker representations/clustering | `bayesian-information-criterion-speaker-segmentation`, `x-vector-speaker-embeddings` | Considered only: no local BIC segmentation, session clustering, embedding extraction or DER/JER result |
| ML | Neural segmentation and speaker embeddings followed by clustering | `pyannote-segmentation-vad`, `pyannote-diarization`, `x-vector-speaker-embeddings` | Segmentation is blocked and diarization is considered; no weights, token, exact revision, runtime, adapter or inference |
| ML | End-to-end diarization and meeting-transcription families to search | `pyannote-diarization`, `vctk-dns2020-ami-ears-and-smard-evidence-manifests` | Search obligation only; `S47` is a pipeline lead, not a staged end-to-end diarizer |
| ML-adjacent | Speaker-representation and similarity proxies | `resemblyzer-speaker-similarity-proxy`, `speechbrains-ecapa-speaker-similarity` | Partial identity/similarity controls; no anonymous label map, cluster count or DER/JER |
| Adjacent | Separation, extraction and personal-VAD boundary | `conv-tasnet`, `target-speaker-extraction-family`, `voicefilter-lite-personal-vad`, `hush` | `SPK-01/02` outputs or enrollment-conditioned extraction; none emits anonymous speaker labels |
| Adjacent | Speech activity and speaker-change boundary | `webrtc-vad`, `silero-vad-6-2-3-reference`, `bayesian-information-criterion-speaker-segmentation`, `pyannote-segmentation-vad` | `DET-01`/`SPK-03` boundaries; activity or change detection is not session-wide diarization |

`report.json` holds the full records: both catalogued branches, the `S06` and
`S47` source-lead mappings, the nineteen-row component census checked against
`INVENTORY.json`, comparison inputs, controls, assets, local versus reported
outcomes, the Spatial acceptance mapping, ten gaps, nineteen board links and
all eight blocked release gates. Historical counts are transcribed verbatim
from pinned reports with their original scope; they are **not** rerun, pooled
into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Six-recording AMI any-speech VAD comparison | WebRTC, Silero, fast-vad, Earshot, SpeexDSP, adaptive RMS, fixed RMS | Six Mix-Headset recordings, three development and three speaker-disjoint held-out; 0 speaker-label rows and 0 DER rows |
| `HE-2` | audEERING positive-span-only VAD diagnostic | The same seven adjacent VAD candidates | Four recordings, 588 annotated positive spans; no speaker IDs; complement unknown |
| `HE-3` | Hush AMI speaker-labeled turn mixtures | `hush` | One meeting, seven directed pairs, 21 additive mixtures at +12/+18/+24 dB; speaker IDs used only for mixture construction, no natural overlap and 0 label-output segments |

`HE-1`–`HE-3` are **adjacent historical local** rows, not SPK-04 diarizer
results. `HE-1` shows any-speech VAD has been compared on AMI; `HE-2` shows a
positive-only VAD diagnostic; `HE-3` shows that AMI participant turns can
build synthetic mixtures. None produces a timestamped anonymous speaker map,
DER/JER, speaker-error score or online revision.

Comparison inputs separate the adjacent any-speech, positive-only and
synthetic speaker-pair rows, the `S06` metric documentation, the `S47`
meeting-pipeline metadata, the catalogued classic and ML component rows and
the **missing** rights-qualified diarization corpus, pyannote
runtime/weights and frozen DER/JER benchmark. Published corpus and pipeline
claims are source-reported only; no audio, RTTM/UEM reference, permissions,
scored regions or split is staged.

## Evidence classes and failure envelope

- **Adjacent local any-speech:** `HE-1`, `HE-2`. These establish that VAD has
  been compared on AMI and positive-only audEERING spans; they do not
  establish anonymous speaker labels or diarization quality.
- **Adjacent local synthetic speaker-pair construction:** `HE-3`. AMI turn
  speaker IDs and timing construct additive examples from non-overlap turns in
  one mono meeting; this is a fixture path, not natural diarization or a
  cluster result.
- **Source-only metric documentation:** `S06` describes speaker-analysis
  metrics but supplies no scorer, collar/UEM policy, label-permutation
  handling, value or local reproduction.
- **Source-reported only:** `S47` CHiME-8/DiPCo/NOTSOFAR metadata, pyannote
  candidate rows, BIC/embedding rows, similarity proxies and corpus leads.
  None is reproduced or locally run.
- **Not present:** a rights-qualified diarization corpus with RTTM/UEM and
  speaker-level truth, an anonymous label map, a DER/JER scorer, pyannote
  weights/runtime/token, session clustering, online revision evidence, a
  target-device timing run, listening, a passed benchmark or a release.
- The failure envelope is adverse by omission: the adjacent AMI VAD rows report
  any-speech false-alarm/miss trade-offs, not speaker-label error; the
  audEERING record has an unknown complement and no speaker IDs; the Hush AMI
  fixtures are explicitly synthetic and speaker-dominant. None of these is
  evidence that a diarizer or anonymous session clustering works.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G03`, `G04`, `G05`,
`G06`, `G08`) link **existing** pyannote, BIC, embedding, manifest and
separation/extraction rows. Gaps without a dedicated category row (`G01`,
`G02`, `G07`, `G09`, `G10`) link existing research-control, taxonomy or
foundation rows and carry a `no component owner ...` note. Those links are
scoping leads only: no diarizer is enabled, no capability is implemented and
no missing result is promoted. Board status is excluded from all gates; only
linked `id`/`title`/`mode` are projected to a stable digest. The mutable board
file is referenced by path and **never hashed into canonical bytes**, so
status edits elsewhere in the swarm cannot change this map or break its
digest.

## Release boundary

No diarization, DER/JER, speaker-error, cluster-count, identity, benchmark,
device-timing or release claim is made. No audio, RTTM/UEM reference, weights,
provider enablement, default, ABI, build or CI change is included. All files
are inside this task directory; board, handoff and reviewers were not changed
or dispatched.

## Result and ownership

Deferred and proposal-only. The next owner receives a deterministic,
task-local evidence map, not a diarization implementation. The SDK foundation
rows `SDK-FND-AUDIT` and `SDK-FND-EVIDENCE` are the only dependencies; no
provider, processor, ABI, installed-package or benchmark interface changed.
There is no implementation, integration or independent-review revision; this
branch contains the survey evidence commit only.

## Reproduction and acceptance

- [x] Pinned every read-only document, public boundary and local artifact by
  SHA-256; pins grant no rights and verify no media, weights or annotation.
- [x] Recorded exact commands, working directories and byte-identical
  regeneration for `report.json`, `contract.json` and `SOURCES.sha256`.
- [x] Recorded adjacent historical counts and their denominators with units,
  plus explicit missing, invalid/nonfinite and adverse rejection cases.
- [ ] Task-matched diarization acceptance (anonymous label map, DER/JER,
  collar/UEM, overlap and online revision) remains blocked by `RG-01`–`RG-06`.
- [ ] Installed-package or integration acceptance is not applicable: no
  installed surface, provider, build or CI file changed.
- [x] Evidence and support scope are separated; source-reported and adjacent
  rows are not promoted, and rights remain unresolved.
- [x] All eight release gates are recorded as blocked; `DEFER` remains in force.

## Review and next action

Independent reviewer not dispatched and no approval requested. Reopen when a
rights-qualified speaker-level corpus, a DER/JER scorer and a pinned pyannote
or classic baseline exist; the smallest follow-ups are `G01`/`G02` and `G03`
on board rows `SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS`,
`SDK-FND-EVIDENCE` and `SDK-PYANNOTE-DIARIZATION`. Downstream dependents
`SDK-SURVEY-SPK-01`, `SDK-SURVEY-SPK-02`, `SDK-SURVEY-SPK-03`,
`SDK-SURVEY-SPK-05` and `SDK-SURVEY-DET-03` keep their own claims; none may
inherit an SPK-04 result from this map.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, repeats the build in three cold-start
processes and rejects any out-of-scope change; `test_reference.py` checks
canonical output, adverse and nonfinite rejection, adjacent-execution
boundaries and three cold-start repeats. JSON and manifest files have SPDX
license sidecars.

```sh
cd docs/task-evidence/survey-spk-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256:
`9a698a08935aba7124b16792c069f8f162462bb79c3040fc5e97b67ad13edff3`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
