<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-REC-02 — language identification and code-switch handling evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`REC-02` (Language identification and code-switch handling; legacy family
`F11`, shared with `DET-02` and `REC-01`). It matches the catalogued classic and
ML method families, both named source leads (`S10`, `S11`) and the available
adjacent executions to existing components. It creates **no new execution,
model, corpus, provider, processor, ABI, default, build, CI, board, handoff,
benchmark or release change**.

Survey owner: `agent-SURVEY-REC-02`; independent reviewer not dispatched.
Claim base: audio-sdk `871201c187c42291410245344aacee5c80051b48`; branch
`swarm/SDK-SURVEY-REC-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `support` / `catalogued` with candidate census
and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-rec-02/` only |
| Owner and independent reviewer | `agent-SURVEY-REC-02`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-REC-02`, `SDK-SURVEY-REC-02`, `871201c187c42291410245344aacee5c80051b48` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no language classifier, recognizer, encoder, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S10` spoken language identification study (direct), `S11` code-switching speech recognition study (direct), plus the pinned read-only documents in `SOURCES.sha256`; no weights, language labels or corpora are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-rec-02/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is an **annotation or control**: language scores and
optional language segments, or optionally a mixed-language transcript, used to
inform an optional policy. It is **not** ASR transcription (`REC-01`), not
speaker-change detection or diarization (`SPK-03`/`SPK-04`), not accent
conversion (`TRN-03`) and not speech-to-speech voice conversion (`TRN-04`).
Those categories are named only as boundaries. A language label is never a
transcript, a speaker identity or a translation.

The catalogued boundary is explicit and is preserved verbatim in `report.json`:
**one language label per clip is different from detecting switches within an
utterance.** A clip-level label is not a language segment. A monolingual
English recognizer is not a multilingual one. A speaker embedding is not a
language embedding. A source-reported study is not a local LID score.

The reviewed records contain **no REC-02 language-identification execution**:
no language inventory, per-clip or segment labels, classic phonotactic model,
neural LID head, multilingual checkpoint, code-switch annotation, mixed-language
transcript, out-of-set policy, per-language score or switch-boundary metric.
Three adjacent local English-only executions are included only to show what
adjacent evidence exists, and all are explicitly marked `adjacent: true`,
`not_component_evidence: true` and "not rerun by this survey". No missing
result is promoted to a pass.

The acceptance profile is also absent: `VERIFICATION.md` defines Analysis,
Enhancement, Room, DSP, Restoration, Spatial, Rate, Voice, Evidence, Tool,
External and Pipeline profiles, but **no Recognition/language profile**. This
map records the absence rather than inventing a profile.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Acoustic/phonotactic statistical classification | none | No inventory component, language-balanced feature extractor, phonotactic model, GMM/SVM or i-vector head or local execution. Energy and spectral statistics are not a language classifier |
| ML | Neural language encoders with a LID head | `wav2vec2-xls-r-transformer-vad`, `x-vector-speaker-embeddings` | Considered only: XLS-R is a VAD candidate and x-vector a speaker-embedding candidate; neither has a language head, language inventory, checkpoint review or LID score |
| ML | Joint multilingual recognition and mixed-language transcripts (`S11`) | `whisper-transcription`, `whisper-tiny-en-int8-via-sherpa-onnx`, `speech-recognition-translation-controls` | Partial ASR controls only; the locally scored Whisper checkpoint is English-only `tiny.en`, and no multilingual token or mixed-language transcript exists |
| ML | Streaming or on-device multilingual recognition | `whisper-streaming`, `fastconformer-streaming-asr` | Blocked: no local checkpoint, streaming runtime, adapter or local WER/latency result |
| ML-adjacent | Monolingual English ASR and encoder controls | `whisper-tiny-en-mfa`, `whisper-timestamp-and-mfa-tooling`, `dynamic-int8-wav2vec2-base`, `distil-wav2vec2-bookbot-distil-wav2vec2-adult-child-cls-37m-ridge`, `wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge` | English-only WER, word-timing and speech-rate controls; none identifies a language, rejects an out-of-set language or detects a switch |
| ML-adjacent | Multilingual corpus and label intake | `librispeech-and-common-voice-evidence-intake` | Considered intake only: no language-balanced split, language label, code-switch segment, consent record or audio staged |
| ML-adjacent | Restricted verbatim annotation tooling | `crisperwhisper` | Non-commercial weights (CC BY-NC 4.0); offline English annotation lead only, not a runtime or rights basis |

`report.json` holds the full records: both catalogued branches, both source-lead
mappings, the fifteen-row component census checked against `INVENTORY.json`,
nine comparison inputs, eight controls, seven assets, local-versus-reported
outcomes, the acceptance mapping, eleven gaps, eighteen board links and all
eight blocked release gates. Adjacent local and source-reported values keep
their original documentation scope; they are **not** rerun, pooled into a
benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Execution or input | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Whisper tiny.en + MFA word-timing crop | `whisper-tiny-en-mfa`, `whisper-timestamp-and-mfa-tooling` | **Adjacent.** One 15 s English AMI crop: 1.45 s CPU inference (RTF 0.096), WER 11.8% (4/34), MFA 33/34 and 23.8 ms mean boundary error, ASR 30 words and 23.2 ms boundary MAE with 91.7% within 50 ms |
| `HE-2` | Paired Whisper tiny.en TSM ASR proxy screen | `whisper-transcription` | **Adjacent.** Ten English AMI clips, 136 reference words, source WER 30.15%; pooled WER deltas at 0.5×/1.25×/1.5×/2.5× for four time-scale engines; not a language or switch result |
| `HE-3` | English-only wav2vec2 and Distil-Wav2Vec2 speech-rate probes | `wav2vec-2-0-base-facebook-wav2vec2-base-960h-ridge`, `dynamic-int8-wav2vec2-base`, `distil-wav2vec2-bookbot-distil-wav2vec2-adult-child-cls-37m-ridge` | **Adjacent.** 210 windows from one English AMI meeting; rate MAE 0.593 / 0.687 / 0.741 syll/s; the heads predict rate, not language |
| `CI-1`–`CI-2` | `S10` LID study and `S11` code-switch ASR study | source rows | Study-language documentation only; no inventory, labels, model, corpus or score |
| `CI-3`–`CI-4` | XLS-R / x-vector and Whisper / sherpa-onnx / ASR-control rows | considered rows | Candidate metadata only; no language head, multilingual checkpoint or mixed-language transcript |
| `CI-5` | Blocked Whisper-Streaming/SimulStreaming and FastConformer rows | blocked rows | No local checkpoint, runtime, adapter or WER/latency |
| `CI-6` | LibriSpeech/Common Voice intake | corpus row | Intake only; no split, consent, labels or audio |
| `CI-7`–`CI-8` | Adjacent English word-timing and speech-rate executions | adjacent rows | Same rows as `HE-1`/`HE-3`; not language identification |
| `CI-9` | Missing REC-02 cohort, language inventory, switch annotation, LID/scorer and benchmark | **missing** | Absence is recorded as missing, not as a negative result |

`HE-1`–`HE-3` are **adjacent historical local** rows, not REC-02 language
results. The source-reported rows describe candidate or study claims and cannot
establish local language labels, weights, accuracy, switch delay or rights. The
missing row keeps an absent cohort explicit instead of silently empty.

## Evidence classes and failure envelope

- **Adjacent local English ASR evidence:** one 15 s Whisper tiny.en + MFA crop.
  It proves an English checkpoint and aligner load and emit word timings; it
  does not prove language identification, out-of-set rejection, code-switch
  detection or bilingual transcript quality.
- **Adjacent local English TSM ASR proxy:** ten clips and 136 AMI reference
  words with a high 30.15% source WER. It is a noisy English intelligibility
  proxy for time-scale engines, not a language or listening result.
- **Adjacent local English encoder probes:** frozen wav2vec2/Distil-Wav2Vec2
  features with rate heads on one meeting. They show encoder use for speech
  rate, not a language encoder or LID head.
- **Source-reported only:** the `S10` LID study, the `S11` code-switch study,
  Whisper's general multilingual family claim, Whisper-Streaming's paper
  latency and the LibriSpeech/Common Voice intake framing.
- **Not present:** a rights-qualified language-balanced or code-switch corpus,
  language inventory and out-of-set policy, per-clip or segment language
  labels, classic or neural LID execution, multilingual/joint checkpoint,
  switch annotation and collar, LID or switch scorer, per-language FN/FP,
  bilingual listening, target-device language-decision timing and a benchmark.
- The failure envelope is adverse by omission: the only local rows are
  **adjacent and English-only**, the only ASR candidates are **partial or
  blocked**, the only corpus lead is **intake-only**, and no acceptance profile
  exists. Language identification, code-switch handling, ASR, speaker change and
  accent/voice conversion are not interchangeable, so no capability is
  inherited from a candidate note or an adjacent task.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with a genuine feasibility lead (`G02`, `G03`,
`G04`) link existing XLS-R, x-vector, Whisper, sherpa-onnx, ASR-control,
Whisper-Streaming and FastConformer rows. Gaps without a component owner
(`G01`, `G05`–`G11`) link existing foundation, research-control, evidence-
manifest or taxonomy rows and carry an explicit `no dedicated REC-02 ...` owner
note. Those links are scoping leads only: no classifier or recognizer is
enabled, no capability is implemented and no missing result is promoted. Board
status is excluded from all gates; only linked `id`/`title`/`mode` are projected
to a stable digest. The mutable board file is referenced by path and **never
hashed into canonical bytes**, so status edits elsewhere in the swarm cannot
change this map or break its digest.

## Release boundary

Keep language identification, code-switch detection, ASR transcription, speaker
change and accent/voice conversion separate; keep per-clip labels separate from
intra-utterance switch boundaries; keep an unlisted language unknown rather than
mapping it to a known language; keep study documentation, adjacent-local,
candidate and missing evidence distinct; and require a language inventory,
out-of-set policy and switch annotation before any language-conditioned action.
No public benchmark/quality/device/listening/release claim is made. No provider
registration, installed-v0/ABI/registry/default/shared-build/CI change, real
corpus, weights, runtime invocation, listening, device-timing, benchmark or
release approval is included. All files are inside this task directory; board,
handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, and repeats the build in three cold-start
processes; `test_reference.py` checks canonical output, adverse and nonfinite
rejection, adjacent-execution boundaries and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rec-02
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
git diff --check
```

Canonical `report.json` SHA-256: `d2e62e3e453e8c56e46ce481984f7379ea97e549084f7022fe6a4d2a2b83129e`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched.
Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
