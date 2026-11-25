<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-REC-01 — speech recognition / transcription (ASR/STT) evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`REC-01` (Speech recognition / transcription, legacy family `F11`). It matches
the catalogued classic and ML method families, the named source leads (`S09`,
`S11`, `S47`) and historical research or source-reported executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-REC-01`; independent reviewer not dispatched. Claim
base: audio-sdk `871201c187c42291410245344aacee5c80051b48`; branch
`swarm/SDK-SURVEY-REC-01`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested_optional` / `catalogued` with candidate
census and benchmark both `not_started`. The package is deliberately
`proposal_only_survey_incomplete`; it is not a benchmark, provider intake or
release candidate.

## What this map covers and what it refuses to claim

The catalogued boundary is explicit: file transcription is **not** proof of
causal streaming, and partial/final timing plus word preservation are distinct
from listening quality. This map therefore covers:

- classic HMM/DNN-HMM acoustic modeling with a lexicon and n-gram decoding, and
  forced alignment used only as a timing reference;
- encoder-decoder attention recognition (Whisper-style file transcription),
  including int8 exports and a non-commercial lead;
- CTC/transducer/Conformer streaming recognition;
- joint meeting transcription with diarization/overlap context (`S47`); and
- code-switching/multilingual recognition (`S11`).

It does **not** pool speech activity detection (`DET-01`), utterance endpointing
or turn completion (`DET-02`), language identification/code-switch handling
(`REC-02`), speaker diarization (`SPK-04`), translation, listening quality
(`OBS-01`) or speech enhancement (`CLN-01`) into a REC-01 result. Those rows are
named only as boundaries and their results are not promoted here.

No reviewed record is a rights-qualified ASR benchmark. The strongest local
numbers are one 15 s AMI crop (34 reference words, 11.76% WER), a ten-clip
paired Whisper screen (136 reference words), an offline int8 transcript-drift
scorer over two TTS clips plus one real clip with no reference transcript, and a
Vosk content gate scored against construction-time block labels. There is no
independent human transcript review, no word-timestamp gold, no confidence
calibration, no streaming run and no multi-domain corpus. Recognition accuracy
and latency are therefore **not measured by this survey**.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: HMM/DNN-HMM acoustic modeling with lexicon + n-gram decoding | `vosk` (considered), `vosk-small-en-us-0-15-playback-gate` (partial) | Only a block-level content gate on two TTS clips was measured: IoU 0.94–0.95, 12 false-speech and 24 missed-speech blocks of 345/467; no transcript, speaker or recognition score |
| Classic: feature front end, lexicon and forced alignment as a timing reference | `whisper-timestamp-and-mfa-tooling` (partial), `whisper-tiny-en-mfa` (evaluated) | MFA 3.4.3 alignment on one 15 s crop; the AMI reference is itself forced alignment and was not manually corrected |
| ML: encoder-decoder attention recognition (Whisper-style offline file transcription) | `whisper-transcription`, `whisper-tiny-en-int8-via-sherpa-onnx` (partial), `whisper-tiny-en-mfa` (evaluated), `crisperwhisper` (considered) | 11.76% WER on one 34-word crop; fixed-scorer WER deltas on 136 words; one-utterance cross-task WER 0%; CrisperWhisper is non-commercial |
| ML: CTC/transducer and Conformer streaming recognition | `whisper-streaming`, `simulstreaming`, `streaming-conformer-ted`, `fastconformer-streaming-asr` (all blocked) | No checkpoint, streaming runtime or adapter; no partial/final, latency or WER result |
| ML: meeting transcription with diarization/overlap (`S47`) | `speech-recognition-translation-controls` (considered), `whisper-transcription` (partial) | External protocol lead only; no CHiME-8 corpus, array layout, diarization output or local pipeline |
| ML: code-switching/multilingual recognition (`S11`) | `speech-recognition-translation-controls` (considered) | External study lead only; no code-switched audio, language labels, script mapping or execution |

`report.json` holds the full records: both catalogued branches, the `S09`/`S11`/
`S47` source-lead mapping, the component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, twelve gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Whisper tiny.en + MFA on one 15 s AMI crop | `whisper-tiny-en-mfa`, `whisper-timestamp-and-mfa-tooling` | 34 reference words, 4 errors (11.76% WER); MFA oracle boundary MAE 23.79 ms, ASR-transcript MAE 23.17 ms / 91.7% within 50 ms; one English meeting crop |
| `HE-2` | Paired Whisper tiny.en fixed-scorer screen | `whisper-transcription` | 10 four-second crops, 136 reference words, 90 paired decodes; source WER 30.1–30.15%; pooled deltas are transcript-drift proxies |
| `HE-3` | Whisper tiny.en int8 sherpa-onnx transcript-drift scorer | `whisper-tiny-en-int8-via-sherpa-onnx` | Two TTS clips with exact transcript plus one real AMI clip without reference; 15,708 blocks, 0 deadline misses; offline scoring only |
| `HE-4` | Vosk small-en-us-0.15 content-gate boundary screen | `vosk-small-en-us-0-15-playback-gate`, `vosk` | Two TTS clips, construction-time block labels, IoU 0.94–0.95, 12 false-speech / 24 missed-speech blocks; gate is not a recognizer |

All four rows are **historical research executions, not merged task evidence**.
Every row is marked `merged_task_evidence: false`, `not_rerun: true` and "not
rerun by this survey". Comparison inputs separate the single-crop transcript,
the fixed-scorer cohort, the transcript-drift corpus, the Vosk gate labels, the
three source-lead documents and the missing rights-qualified corpus. Local and
source-reported outcome ids are disjoint.

## Evidence classes and failure envelope

- **Historical local single-crop ASR/alignment:** HE-1. It proves that one
  Whisper tiny.en run and one MFA comparison produced the cited numbers, not
  general accuracy or independent timing gold.
- **Historical local fixed scorer:** HE-2 and HE-3. Whisper is a scoring
  instrument for other experiments; its WER does not rank recognizers and the
  source error rate is high.
- **Historical local adjacent gate:** HE-4. Vosk word boundaries power a 100 ms
  content gate; the gate is not a transcript and is a poor production boundary
  source.
- **Source-reported only:** Whisper documentation (`S09`), the CHiME-8 pipeline
  (`S47`), the code-switching study (`S11`), the CrisperWhisper licence
  constraint, the blocked streaming-ASR rows and the cross-task one-utterance
  WER 0%.
- **Not present:** a rights-qualified multi-domain corpus, independent human
  transcripts, word-timestamp gold, confidence calibration, streaming execution,
  code-switch execution, meeting transcription, entity-error scoring, listening,
  device timing, latency, provider intake or release approval. These classes are
  `false`, not inherited from an adjacent survey.

The failure envelope is adverse. One 34-word crop gives 11.76% WER but cannot
represent accents, languages, noise or devices. The ten-clip screen has a 30.1%
source WER and per-clip variation in both directions, so a pooled delta can hide
regressions and improvements. The int8 scorer's corpus is mostly synthetic TTS
and the real clip has no reference transcript. The Vosk gate missed 24 blocks and
raised 12 false-speech blocks on construction-time labels, which is inadequate
for a production boundary. Low WER on one converted utterance is not
comprehension.

## Bounded gaps and feasibility links

Twelve gaps are recorded. Gaps with an existing feasibility owner (`G01`, `G02`,
`G03`, `G05`, `G06`, `G07`, `G08`, `G09`, `G10`, `G12`) link Vosk, word-timestamp,
streaming-ASR, transcript-control, REC-02, ASR-guided-planner and DET-02 rows.
Gaps without a component feasibility owner (`G04`, `G11`) link existing
research-control, implementation, foundation or audit rows and carry an explicit
owner note. Those links are scoping leads only: no recognizer is enabled, no
capability is implemented and no missing result is promoted. Board status is
excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The mutable board file is referenced by path and **never hashed
into canonical bytes**, so status edits elsewhere in the swarm cannot change this
map or break its digest.

## Release boundary

Keep recognition separate from speech activity, utterance endpointing, language
identification, diarization, translation, listening quality and enhancement.
File transcription is not causal streaming. A transcript is not an independent
human reference, and an alignment against another forced alignment is not word
timing gold. Unknown or missing audio is never an empty transcript or
non-speech. Synthetic, adjacent-gate, single-crop, fixed-scorer, source-reported
and missing results stay distinct. No public benchmark, quality, device,
listening, latency or release claim is made. No assets, real audio, weights,
model, provider enablement, default, ABI, build or CI change is included. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte and checks three cold-start builds; `verify.py`
recomputes all artifacts, checks licensing, repeats the build in three fresh
processes and enforces task-local git scope; `test_reference.py` checks
canonical output, adverse rejections, domain boundaries and three cold-start
repeats. JSON and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rec-01
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `b89364422f6e2796d0fd6d955417066d7f01da59420e817f0a781e4e69c20ac5`.

The change is task-local documentation and stdlib tooling; no installed package,
descriptor catalog, ABI, build input or CI workflow is touched. The repository's
installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or transcripts. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
