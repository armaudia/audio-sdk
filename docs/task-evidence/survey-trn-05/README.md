<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-TRN-05 — reference-conditioned voice cloning / TTS evidence map

**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**
This package is a bounded, deterministic **taxonomy and comparison map** for
inventory category `TRN-05` (Reference-conditioned voice cloning / TTS, legacy
family `F14`). It matches the catalogued classic and ML method families, the one
named source lead (`S40`) and the available adjacent historical executions to
existing components. It creates **no new execution, model, corpus, reference
voice, provider, processor, ABI, default, build, CI, board, handoff or release
change**.

Survey owner: `agent-SURVEY-TRN-05`; independent reviewer not dispatched. Board
claim base: audio-sdk `39b8885da4fc3ef8e27becf5df5f0658da3baf65`. The branch was
fast-forwarded to current `origin/main` `62923ffa7dd992da3cea0f6683fab320fb37e6c0`
before authoring so the merged sibling templates (`survey-trn-02`,
`survey-trn-03`) are present; **no board row was edited**. The task depends on
`SDK-FND-AUDIT` and `SDK-FND-EVIDENCE`; write scope is `Category evidence map
and bounded gap handoff`. The category remains `requested_optional_adjacent` /
`catalogued` with candidate census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-trn-05/` only |
| Owner and independent reviewer | `agent-SURVEY-TRN-05`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-TRN-05`, `SDK-SURVEY-TRN-05`, claim `39b8885da4fc3ef8e27becf5df5f0658da3baf65`, integration base `62923ffa7dd992da3cea0f6683fab320fb37e6c0` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no synthesizer, voice-cloning model or runtime is selected or invoked |
| Source, model and dataset revisions/digests | `S40` F5-TTS official implementation (direct lead), plus the pinned read-only documents in `SOURCES.sha256`; no weights, checkpoints, reference voices or consent records are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-trn-05/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is a **generated waveform**: speech synthesized from text
plus a speaker reference (sometimes with reference text). The catalogued
boundary is preserved verbatim: **Cloning via conversion belongs to TRN-04. TTS
is an optional branch, not a required ASR→TTS replacement for a call.** This map
therefore covers:

- the open classical reference/adapted synthesis family search;
- ML reference-conditioned flow-matching synthesis (`S40` F5-TTS);
- zero-shot codec/LLM and flow TTS conditioned on prompt audio (CosyVoice 2,
  Seed-TTS);
- autoregressive or whole-utterance neural TTS conditioned on a voice prompt
  (Chatterbox Nano, StyleTTS 2, YourTTS);
- end-to-end VITS/adversarial and streaming VITS synthesis;
- streaming cloned-voice TTS with gated GGUF checkpoints (NeuTTS Nano/Air); and
- fixed-voice TTS and vocoder/analysis-resynthesis components as *controls and
  boundaries*, never as cloning results.

It does **not** pool speech-to-speech voice conversion (`TRN-04`), accent
conversion (`TRN-03`), pitch/prosody control (`TRN-02`), time-scale modification
(`TRN-01`), ASR/transcription (`REC-01`), speaker identification
(`SPK-05`), enhancement (`CLN-01`) or quality assessment (`OBS-01`) into a
TRN-05 result. Those rows are named only as boundaries and their results are not
promoted here.

No reviewed record is a rights-qualified reference-conditioned TTS benchmark.
The strongest local numbers are one CosyVoice 2 prompt/text streaming run, one
Chatterbox Nano whole-utterance run and one Kokoro 82M fixed-preset control, all
single-text and single-reference on CPU. There is **no reference-voice
similarity score, no naturalness or identity listening, no multi-speaker cohort,
no manual transcript gold, no streaming first-audio measurement and no device
timing**. Cloning fidelity and naturalness are therefore **not measured by this
survey**.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Reference/adapted synthesis family search (`MF-C1`) | none | The catalogued classic string explicitly leaves the search open; no classical reference-adapted synthesizer or execution exists, so the open search is recorded rather than filled with a vocoder |
| ML | Reference-conditioned flow-matching synthesis (`MF-M1`, `S40`) | `f5-tts` (considered) | Official implementation is a source lead; no checkpoint, revision, runtime, reference voice or local sample is staged |
| ML | Zero-shot codec/LLM and flow TTS with prompt audio (`MF-M2`) | `cosyvoice-2-0-5b` (partial), `cosyvoice-family` (blocked), `seed-tts` (blocked) | One adjacent CosyVoice 2 prompt/text run with four chunks; no reference similarity or naturalness; Seed-TTS and the family row stay blocked |
| ML | Autoregressive / whole-utterance prompt-conditioned TTS (`MF-M3`) | `chatterbox-nano` (partial), `styletts-2` (blocked), `yourtts` (blocked) | One adjacent Chatterbox Nano whole-utterance run with no chunks; StyleTTS 2 and YourTTS have no staged checkpoint or run |
| ML | End-to-end VITS/adversarial and streaming VITS (`MF-M4`) | `vits2` (blocked), `vits-streaming-adaptation` (considered) | No canonical VITS2 checkpoint and no sub-100 ms streaming checkpoint identified; a streaming label is not a measured delay |
| ML | Streaming cloned-voice TTS with gated GGUF checkpoints (`MF-M5`) | `neutts-nano-q4` (partial), `neutts-air-gated-checkpoint-lead` (blocked) | Gated download returned HTTP 401; no inference result and no substitute checkpoint |
| ML | Adjacent fixed-voice TTS control and vocoder / analysis-resynthesis components (`MF-M6`) | `kokoro-82m` (partial), `hifi-gan-vocoder`, `vocos-vocoder`, `world-vocoder`, `nansy-analysis-resynthesis`, `fastspeech-2-vits-duration-predictors` (considered) | Fixed-preset control and component rows only; a vocoder or duration predictor is not a reference-conditioned synthesizer |

`report.json` holds the full records: both catalogued branches, the `S40`
source-lead mapping, a 17-row component census checked against
`INVENTORY.json`, nine comparison inputs, nine controls, nine assets, three
adjacent historical executions, seven reported outcomes, the Voice acceptance
mapping, twelve gaps, twenty-six linked board rows and all eight blocked release
gates. Historical numbers are transcribed from the pinned research report and
result JSON with their original scope; they are **not** rerun, pooled into a
benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | CosyVoice 2 0.5B zero-shot streaming TTS, one prompt/text pair | `cosyvoice-2-0-5b` | 10.0 s audio in 4 chunks; first chunk 23.81 s; init 22.42 s; total 80.66 s; file RTF 8.07; peak 0.99; WER 0.00; no clipping; no reference similarity, naturalness or device timing |
| `HE-2` | Chatterbox Nano official reference-conditioned whole-utterance TTS | `chatterbox-nano` | 8.92 s audio; init 11.10 s; generation 11.47 s; file RTF 1.286; peak 0.342; WER 0.00; no clipping; no streaming chunks, reference similarity or naturalness |
| `HE-3` | Kokoro 82M fixed-preset TTS control | `kokoro-82m` | `af_heart` preset with no reference voice; 9.025 s audio; first/only segment 57.297 s; RTF 0.158; explicitly not a zero-shot cloning model |

All three rows are **historical research executions, not merged task
evidence**. Every row is marked `merged_task_evidence: false`, `not_rerun: true`
and "not rerun by this survey". `CI-1`–`CI-2` are the direct `S40` protocol lead
and the considered F5-TTS row; `CI-3`–`CI-5` are the three adjacent local runs;
`CI-6` is the gated NeuTTS blocker; `CI-7` is the blocked Seed-TTS / StyleTTS 2 /
YourTTS / VITS2 set; `CI-8` is the vocoder/duration component boundary; `CI-9`
is the **missing** rights-cleared reference-voice cohort. Local and
source-reported outcome ids are disjoint.

## Evidence classes and failure envelope

- **Adjacent local zero-shot streaming generation:** HE-1 only. It proves one
  CPU prompt/text generation emitted finite, non-clipping chunks; it does not
  measure reference fidelity, naturalness, or first-audio latency on a call
  device, and the first-chunk time includes prompt loading and encoding.
- **Adjacent local whole-utterance generation:** HE-2 only. The official API
  returns a complete waveform with no chunks, so 11.47 s is call-to-return, not
  first-audio latency; there is no similarity or naturalness score.
- **Adjacent local fixed-voice control:** HE-3 only. Kokoro is explicitly not a
  zero-shot cloning model; it is a text-only cost and intelligibility control.
- **Source-only protocol:** `S40` F5-TTS. Method context, not a checkpoint or a
  run.
- **Source-reported candidate:** CosyVoice 2, Chatterbox Nano and the considered
  F5-TTS row as documentation; gated NeuTTS, Seed-TTS, StyleTTS 2, YourTTS and
  VITS2 as blocked rows.
- **Component boundary:** HiFi-GAN, Vocos, WORLD, NANSY and FastSpeech 2 / VITS
  duration predictors are pieces, not synthesizers.
- **Missing:** reference-voice similarity, naturalness/identity listening,
  manual transcript gold, multi-speaker cohort, consent/output-use clearance,
  streaming first-audio/tail, sample-count preservation, nonfinite handling,
  device timing and a benchmark.

The failure envelope is adverse. Every run is one text and one reference, so
speaker, language and text coverage is absent. A 0.00 WER proxy cannot show
naturalness or voice fidelity. A zero-shot streaming path at 8.07× file RTF is
far outside real time on the historical CPU. Whole-utterance generation at
1.286× is slower than real time and exposes no chunks. A fixed preset has no
reference at all. A gated checkpoint that never downloaded and four blocked
candidate rows supply no audio. None of these outcomes is a cloning pass.

## Bounded gaps and feasibility links

Twelve gaps are recorded. Gaps with a genuine feasibility lead (`G01`, `G02`,
`G05`, `G07`, `G09`, `G12`) link F5-TTS, NeuTTS, blocked-candidate, control,
component, streaming and timing rows. Gaps without a dedicated TRN-05 component
owner (`G03`, `G04`, `G06`, `G08`, `G10`, `G11`) link existing manifest,
identity, evidence, timing, taxonomy, pipeline and audit rows and carry an
explicit owner note. Those links are scoping leads only: no synthesizer is
enabled, no capability is implemented and no missing result is promoted. Board
status is excluded from all gates; only linked `id`/`title`/`mode` are projected
to a stable digest. The mutable board file is referenced by path and **never
hashed into canonical bytes**, so status edits elsewhere in the swarm cannot
change this map or break its digest.

## Release boundary

Keep TTS separate from conversion, accent conversion, prosody/rate control, ASR,
identity verification, enhancement and quality assessment. Keep text, reference
audio and optional reference text as distinct input facets. Keep content
preservation, reference-voice similarity and naturalness as separate outcomes,
and keep consent, reference availability and output use as independent gates.
Require a rights-cleared consented reference-voice corpus, frozen text/voice
partitions, mismatched-reference and ignore-reference controls, pinned
checkpoints/terms, and sample-count/finite-output timing before any claim. No
cloning, naturalness, similarity, perceptual, streaming, device, benchmark or
release claim is made. No provider registration, installed-v0/ABI/registry/
default/shared-build/CI change, real corpus, weights, runtime invocation, audio
mutation or listening is included. All files are inside this task directory;
board, handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte and checks three cold-start builds; `verify.py`
recomputes all artifacts, checks licensing, repeats the build in three fresh
processes and enforces task-local git scope; `test_reference.py` checks
canonical output, adverse and nonfinite rejection, domain boundaries and three
cold-start repeats. JSON and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-trn-05
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256 is printed by `run.py all` and recorded in
`report.json.sha256`; the committed value is checked by `verify.py` and by the
cold-start tests.

The change is task-local documentation and stdlib tooling; no installed package,
descriptor catalog, ABI, build input or CI workflow is touched. The repository's
installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` and its
inputs remain unchanged; no installed-package result is claimed here.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights, transcripts, voices or consent.
`AUDIOML_WORKSPACE_ROOT` can point to the enclosing `audioml` checkout if
automatic discovery is unavailable.
