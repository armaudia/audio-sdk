<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-SPK-05 — speaker representation, identification and verification evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`SPK-05` (Speaker representation, identification and verification, legacy
family `F06`). It matches the catalogued classic and ML method families, the
single named source lead (`S05`) and the available adjacent historical local
executions to existing components. It creates **no new execution, model,
corpus, provider, verifier, ABI, default, build, CI, board, handoff, privacy,
benchmark or release change**.

Survey owner: `agent-SURVEY-SPK-05`; independent reviewer not dispatched.
Claim base: audio-sdk `87a8107a0b495378f5fb5ead55cf32a0f222ad56`; branch
`swarm/SDK-SURVEY-SPK-05`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `catalogued` with candidate census and benchmark
both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-spk-05/` only |
| Owner and independent reviewer | `agent-SURVEY-SPK-05`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-SPK-05`, `SDK-SURVEY-SPK-05`, `87a8107a0b495378f5fb5ead55cf32a0f222ad56` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no embedding model, verifier, gallery, threshold or runtime is selected |
| Source, model and dataset revisions/digests | `S05` x-vector paper (direct), the pinned TokAN/Resemblyzer, MeanVC2/WavLM+ECAPA, OpenVoice V2 and RVC records at their cited revisions, and the pinned read-only documents in `SOURCES.sha256`; no weights or media are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-spk-05/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is a **speaker representation, a gallery match or a
verification score**. It is not speech activity detection (`DET-01`),
overlapping-speech detection or speaker count (`DET-03`), target-speaker VAD
(`DET-05`), generic speech separation (`SPK-01`), target-speaker extraction
(`SPK-02`), speaker-change segmentation (`SPK-03`), anonymous diarization
(`SPK-04`), noise suppression (`CLN-01`) or a policy for preserving speech.
Those categories are named only as boundaries. An identity is not permission to
mute, delete, time-scale, enhance or otherwise alter any speech.

The catalogued boundary is preserved verbatim in `report.json`:
**Identification and verification need separate outputs/metrics. An identity is
not a policy for preserving speech.** A cluster label is not an enrolled
identity. An in-model cosine is not a calibrated verification score. A
target-speaker extraction cue is not a verification decision. A same-clip
similarity proxy is not an identification result.

The reviewed records contain **no SPK-05 identification or verification
execution**: no x-vector run, no classic GMM-UBM/MAP baseline, no enrolled
gallery, no genuine/impostor trial list, no rank-1/mAP or EER/minDCF score and
no calibrated operating point. Three adjacent local rows are included only to
show what exists nearby, and all are explicitly marked `adjacent: true`,
`not_component_evidence: true` and "not rerun by this survey". No missing result
is promoted to a pass.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Statistical speaker models and likelihood scoring (GMM-UBM/MAP) | none | Candidate only: the catalogued classic family has no component row, staged model, enrolment set, likelihood calibration or local score |
| Classic | Speaker-change segmentation and anonymous clustering boundary | `bayesian-information-criterion-speaker-segmentation`, `pyannote-diarization` | Annotation boundary: change points and anonymous cluster IDs are not verified identities |
| Classic | Speaker-conditioned extraction and personal VAD boundary | `target-speaker-extraction-family`, `voicefilter`, `voicefilter-lite-personal-vad` | `SPK-02`/`DET-05` boundary: an enrolment cue selects a target; it does not verify a claimed identity |
| ML | Speaker embeddings; x-vectors/TDNN (`S05`) | `x-vector-speaker-embeddings` | Considered only: paper-level method; no revision, checkpoint, trial list or local embedding output |
| ML | Cosine/PLDA scoring over deep embeddings | `x-vector-speaker-embeddings` | Scoring family documented; no gallery, score normalisation, threshold or verification metric |
| ML | Research-control deep embedding similarity proxies | `resemblyzer-speaker-similarity-proxy`, `speechbrains-ecapa-speaker-similarity` | Partial research controls; in-model similarity only, not independent identity evidence |
| ML-adjacent | In-model speaker cosines inside voice conversion | `tokan`, `meanvc2`, `openvoice-v2`, `rvc-v2-vctk-p226` | Adjacent conversion rows: one fixed pair or same-clip reference; the RVC target identity is presumed, not verified |

`report.json` holds the full records: both catalogued branches, the `S05`
source-lead mapping, the twelve-row component census checked against
`INVENTORY.json`, comparison inputs, controls, assets, local-versus-reported
outcomes, the Spatial acceptance mapping, twelve gaps, nineteen board links and
all eight blocked release gates. Source-reported numbers keep their original
documentation scope; they are **not** rerun, pooled into a benchmark or promoted
to a pass.

## Historical executions and comparison inputs

| ID | Execution or input | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | TokAN same-clip accent conversion with Resemblyzer cosine | `tokan`, `resemblyzer-speaker-similarity-proxy` | **Adjacent.** Three accent-labelled Arabic/Hindi/Korean utterances, same source clip used as the speaker reference, CPU offline; cosines 0.838/0.798/0.874, WER 0.00, output 24 kHz; a quick similarity proxy, not verification |
| `HE-2` | MeanVC2 in-model WavLM+ECAPA target similarity | `meanvc2` | **Adjacent.** One LJ Speech source and one p360 target, two configs; cosines 0.669/0.702, file RTF 0.959/0.396, WER 0.00; in-model diagnostic only |
| `HE-3` | OpenVoice V2 in-model target similarity | `openvoice-v2` | **Adjacent.** One fixed source/target pair, offline whole-file; cosine 0.890, RTF 0.341, WER 0.00; model-internal, not perceptual |
| `CI-1` | X-vector/TDNN speaker-recognition study (`S05`) | source lead | Source-reported method definition only; no weights, trial list or local score |
| `CI-2`–`CI-4` | TokAN, MeanVC2 and OpenVoice adjacent rows | component links | Same adjacent evidence as `HE-1`–`HE-3`; not identification or verification |
| `CI-5` | RVC p226 target provenance | `rvc-v2-vctk-p226` | Target ID 1 is presumed p226 but unverified; no speaker metric |
| `CI-6`–`CI-7` | Resemblyzer and SpeechBrain ECAPA controls | research controls | Similarity proxies; no encoder revision, enrolment geometry or impostor distribution |
| `CI-8` | Pyannote diarization and BIC segmentation | annotation boundary | Anonymous labels and change points, not identities |
| `CI-9` | TSE, VoiceFilter and personal VAD | `SPK-02` boundary | Blocked; enrolment-conditioned extraction, not verification |
| `CI-10` | Rights-qualified, consent-cleared speaker trial list | **missing** | Absence recorded as missing, not as a negative verification result |
| `CI-11` | Classic GMM-UBM/MAP likelihood-ratio baseline | **absent** | Catalogued classic family with no component or local score |

`HE-1`–`HE-3` are **adjacent historical local** rows, not SPK-05 verifier
results. The source-reported rows describe candidate or protocol claims and
cannot establish local weights, labels, identity truth, false accepts, latency
or rights. The missing row keeps an absent trial list explicit instead of
silently empty.

## Evidence classes and failure envelope

- **Adjacent same-clip similarity proxy:** `HE-1`. The same clip is both source
  and reference, so the screen tests retention on an easy pair. Resemblyzer
  cosine is a quick proxy, not a human identity rating.
- **Adjacent in-model speaker similarity:** `HE-2`, `HE-3`. The reported cosines
  come from each converter's own encoder or the MeanVC2 target encoder. They
  compare only within their own pair and are not independent, calibrated or
  comparable across encoders.
- **Adjacent identity provenance:** the RVC p226 target is presumed, not
  verified. A guessed target identity cannot serve as an enrolment record.
- **Classic and ML candidates:** GMM-UBM/MAP and x-vector/TDNN are paper or
  plan rows. No weights, enrolment set, gallery, score distribution or trial
  list is staged.
- **Research controls:** Resemblyzer and SpeechBrain ECAPA are partial
  evaluation controls. They can support a diagnostic, not an identity decision.
- **Source-reported only:** the `S05` method family, the VoiceFilter/Personal
  VAD descriptions and the diarization/BIC boundary notes. None is reproduced
  or locally run.
- **Not present:** a consent-cleared genuine/impostor trial list, speaker-disjoint
  held-out speakers, a gallery, separate rank-1/mAP and EER/minDCF metrics,
  calibration, a threshold policy, real weights/runtime, listening, privacy
  approval, target-device timing and a benchmark.
- The failure envelope is adverse by omission: the only evaluated local rows are
  fixed-pair or same-clip conversions, the only similarity measures are in-model
  cosines, and the only foundation-style inputs are manifests and evidence
  rules. Identification, verification, diarization, extraction, separation and
  enhancement are not interchangeable, so no capability is inherited from an
  adjacent task.

## Bounded gaps and feasibility links

Twelve gaps are recorded. Gaps with a genuine feasibility lead (`G01`, `G02`,
`G05`, `G06`, `G07`) link existing x-vector, research-control, diarization, BIC
and extraction rows. Gaps without a component owner (`G03`, `G04`, `G08`,
`G09`, `G10`, `G11`, `G12`) link existing foundation or research-control rows
and carry an explicit `no component owner ...` note. Those links are scoping
leads only: no verifier is enabled, no capability is implemented and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep speaker representation, open-set identification, verification, diarization,
speaker-change segmentation, target-speaker extraction, speech separation,
enhancement and speech preservation separate; keep source-documented,
adjacent-local, research-control, prepared-manifest and missing evidence
distinct; and require separate identification and verification outputs, an
explicit gallery/threshold policy and consent-cleared enrolment before any
downstream action. No public identity, verification, biometric, privacy,
benchmark, quality, device, listening or release claim is made. No provider
registration, installed-v0/ABI/registry/default/shared-build/CI change, real
corpus, weights, runtime invocation, audio mutation, listening, device-timing,
benchmark or release approval is included. All files are inside this task
directory; board, handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, and repeats the build in three cold-start
processes; `test_reference.py` checks canonical output, adverse and nonfinite
rejection, adjacent-execution boundaries and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-spk-05
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

The canonical `report.json` SHA-256 is written to `report.json.sha256` and
recomputed by `verify.py`. Canonical digest: `4ea9baeec0425148269708f574f678aed2679b12aa3cf22897d6f2909a2b69d3`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
