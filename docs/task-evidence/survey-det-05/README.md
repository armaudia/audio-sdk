<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-DET-05 — target-speaker / personalized VAD evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`DET-05` (Target-speaker / personalized VAD, legacy family `F05`). It matches
the two catalogued method families, both named source leads (`S52`, `S53`) and
the available historical or source-reported evidence to existing components. It
creates **no new execution, model, corpus, checkpoint, enrollment cue, provider,
processor, ABI, default, build, CI, board, handoff, benchmark or release
change**.

Survey owner: `agent-SURVEY-DET-05`; independent reviewer not dispatched.
Claim base: audio-sdk `c4419d1ce9783b552d662bd7cd524b20ce48feaa`; branch `swarm/SDK-SURVEY-DET-05`. The task
depends on `SDK-FND-AUDIT` and `SDK-FND-EVIDENCE`; write scope is `Category
evidence map and bounded gap handoff`. The category remains
`discovered_extension` / `catalogued` with candidate census and benchmark both
`not_started`. The package follows the merged `survey-det-01` and
`survey-cln-11` templates; `survey-det-02` was not present on `origin/main` in
this worktree.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-det-05/` only |
| Owner and independent reviewer | `agent-SURVEY-DET-05`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-DET-05`, `SDK-SURVEY-DET-05`, `c4419d1ce9783b552d662bd7cd524b20ce48feaa` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no provider, recipe, processor, model or runtime is selected |
| Source, model and dataset revisions/digests | `S52` Personal VAD primary paper (direct), `S53` Personal VAD reproduction/checkpoint lead (direct README; no execution/checkpoint access), plus the pinned read-only documents in `SOURCES.sha256` |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-det-05/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is an **annotation or control**: for a selected,
enrolled speaker, emit target-speaker, other-speaker and non-speech frame
scores or intervals. It is not a waveform extractor, not a source separator, not
a mute/gate mandate, not speaker identification or verification, not
diarization and not general any-speaker VAD.

`DET-01` (speech activity detection), `SPK-02` (target-speaker extraction and
personalized enhancement), `SPK-05` (speaker representation, identification and
verification) and `DET-03` (overlapping speech and speaker count) are named only
as boundaries. Their rows are not personalized-VAD evidence and are never
pooled into a DET-05 claim.

Three dedicated components are catalogued and **all are blocked**:
`voicefilter-lite-personal-vad`, `voicefilter` and
`target-speaker-extraction-family`. No local checkpoint, runtime, enrolled
mixture, clean target reference or target-labelled execution exists. The only
local rows are **adjacent** evidence: seven any-speaker VADs on held-out AMI,
two Hush speaker-dominant suppression diagnostics, and in-model
speaker-similarity cosines from voice-conversion evaluations. None measures a
selected speaker's activity.

## Method families and mapped evidence

| Catalogued family | Mapped component(s) | Status and boundary |
| --- | --- | --- |
| Classic: standard VAD plus speaker-scoring pipeline baseline | `silero-vad-6-2-3-reference`, `webrtc-vad`, `resemblyzer-speaker-similarity-proxy`, `speechbrains-ecapa-speaker-similarity`, `x-vector-speaker-embeddings` | Catalogued baseline never assembled; VAD and similarity evidence exist separately with no shared cohort, threshold or enrolled score |
| Classic: statistical speaker segmentation / BIC change detection | `bayesian-information-criterion-speaker-segmentation` | Considered only; turn boundaries are not an enrolled speaker's activity |
| ML: speaker-conditioned neural activity classification (Personal VAD family) | `voicefilter-lite-personal-vad`, `x-vector-speaker-embeddings` | Blocked; no compatible checkpoint, runtime or enrollment-conditioned execution |
| ML: speaker-conditioned neural extraction used only as an adjacent target-dominance proxy | `voicefilter`, `target-speaker-extraction-family`, `hush` | Blocked or partial; suppression changes a waveform and cannot substitute for target-activity scores |
| ML: neural diarization/segmentation supplying speaker turns | `pyannote-diarization`, `pyannote-segmentation-vad` | Considered or blocked; turn labels do not identify an enrolled target |

`report.json` holds the full records: both catalogued branches, both source-lead
mappings, a 22-row component census checked against `INVENTORY.json`, adjacent
boundaries, comparison inputs, controls, assets, historical executions,
local-versus-reported outcomes, the Analysis acceptance mapping, ten gaps,
board links and all eight blocked release gates. Transcribed numbers keep their
original scope; they are **not** rerun, pooled into a benchmark or promoted to a
pass.

## Historical executions and local-versus-reported outcomes

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Hush EARS primary/background screen, 30 pairs × 3 SIR = 90 mixtures | `hush`, SI-SDR/STOI scorers | Adjacent suppression only; +8.14/+8.08/+8.46 dB target/masker ratio but −9.33/−14.54/−20.23 dB target SI-SDR and −.141/−.176/−.197 STOI. EARS has no speaker metadata and Hush accepts no enrollment prompt |
| `HE-2` | Hush AMI ES2004a speaker-dominant diagnostic, 7 directed pairs × 3 SIR = 21 mixtures | `hush`, SI-SDR/STOI scorers | Constructed non-overlap turns, no isolated references or enrollment; −13.17/−18.41/−24.18 dB target SI-SDR, −.193/−.200/−.207 STOI; ratio gains +3.70/+7.33/+3.37 dB with intervals including zero |
| `HE-3` | Seven-candidate held-out AMI any-speaker VAD comparison, 3 meetings | `webrtc-vad`, `silero-vad-6-2-3-reference`, `fast-vad-0-2-1`, `earshot-1-2-2`, `speexdsp-vad`, `adaptive-energy-vad`, `fixed-rms-vad` | Any-speaker relevance only; WebRTC FN 7.31%/FP 49.54%, Silero 19.43%/8.20%, SpeexDSP 2.45%/77.03%, RMS 62.95%/25.35% on 20 ms frames. No target cue, identity or target/other-speech class |

`HE-1` and `HE-2` are **adjacent suppression diagnostics**; `HE-3` is an
**any-speaker VAD baseline**. The three are not the same protocol and are not
averaged. Every row states that it is not a personalized-VAD result and was
"not rerun by this survey". `CI-4` also records in-model speaker-similarity
cosines (0.890, 0.669, 0.702) as a comparison input only; those are
encoder-specific identity diagnostics, not activity scores.

Comparison inputs additionally include the source-only Personal VAD protocol,
the Interspeech 2024 three-class task description, REAL-PS4 target-label and
Open Yap discovery leads, and the **missing** enrolled-speaker corpus with
clean target references. The missing row is explicit rather than filled.

## Evidence classes, failure envelope and release boundary

- **Historical local any-speaker VAD baseline:** three speaker-disjoint AMI
  meetings projected onto 20 ms frames. It identifies speech, not a selected
  speaker, and is only a comparator.
- **Historical local adjacent suppression:** Hush on EARS synthetic pairs and
  AMI speaker-dominant turns. It raises the target/masker ratio while damaging
  the designated target; the AMI ratio intervals include zero.
- **Historical local in-model similarity:** conversion-encoder cosines, not
  verification or activity. Scores from different encoders are not comparable.
- **Source-only protocol:** the Personal VAD paper, reproduction README and
  Interspeech 2024 task description. Method and class definitions only.
- **Source-reported dataset lead:** REAL-PS4 exposes target-speaker labels for
  clipped overlapping utterances; utterance clips are not continuous truth and
  nothing is staged.
- **Missing:** enrolled-speaker mixtures, clean target references,
  target/other/nonspeech labels, impostor and target-absent negatives, a
  compatible checkpoint, a frozen scorer, device timing, listening and any
  benchmark or release qualification.
- **Deliberately not claimed:** target-activity accuracy, EER, target false
  rejection, impostor acceptance, identity verification, extraction quality,
  speech enhancement, diarization quality, muting safety, device latency,
  public default and release approval.

The failure envelope is explicit. A generic VAD with the best any-speaker FN/FP
has no target cue and cannot answer "is *this* speaker active". A suppressor
that improves a target/masker ratio while lowering target SI-SDR and STOI has
not demonstrated target selection. A high in-model similarity cosine is not an
activity decision. An unannotated region is unknown, never non-target. A
reproduction README is not a runnable checkpoint, and a paper number is not a
local result.

## Bounded gaps and feasibility links

Ten gaps are recorded. `G02`, `G04` and `G08` link existing feasibility rows;
the rest link existing foundation, research-control, implementation or taxonomy
rows and carry an explicit `no dedicated DET-05 ...` owner note where no
feasibility row exists. Every follow-up id is an **existing** board row; no task
is invented. Linked rows are scoping leads only: no detector is enabled, no
capability is implemented and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The mutable board file is referenced by path and **never hashed
into canonical bytes**, so status edits elsewhere in the swarm cannot change
this map or break its digest.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing, repeats the build in three cold-start processes and enforces
task-local git scope; `test_reference.py` checks canonical output, adverse
rejections and three byte-identical cold-start repeats. JSON and manifest files
have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-det-05
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
