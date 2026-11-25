<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-TRN-03 — accent conversion evidence map

**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**
This package is a bounded, deterministic **taxonomy and comparison map** for
inventory category `TRN-03` (Accent conversion, legacy family `F14`). It matches
the catalogued classic and ML method families, the named source leads (`S36`,
`S37`) and historical research executions to existing components. It creates
**no new execution, model, corpus, provider, processor, ABI, default, build, CI,
board, handoff or release change**.

Survey owner: `agent-SURVEY-TRN-03`; independent reviewer not dispatched. Claim
base: audio-sdk `b4ccacaff0e82dbfc027404fbb7ac81d4885f768`; branch
`swarm/SDK-SURVEY-TRN-03`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested_transform` / `catalogued` with
candidate census and benchmark both `not_started`. The package is deliberately
`proposal_only_survey_incomplete`; it is not a benchmark, provider intake or
release candidate.

## What this map covers and what it refuses to claim

The catalogued boundary is explicit: pronunciation change is not speaker/timbre
conversion, an accent difference is not an audio defect, and a streaming label
does not establish low conversational delay. This map therefore covers:

- classic formant/phonetic mapping and duration/pitch modification;
- ML content-feature/PPG conversion with neural resynthesis, including WavLM/VQ
  token, autoregressive and neural-vocoder components;
- accent-aware streaming and generic zero-shot streaming voice conversion as a
  *boundary*, not as an accent result; and
- accent-controlled TTS and closed vendor products as external leads only.

It does **not** pool time-scale modification (`TRN-01`), pitch/prosody control
(`TRN-02`), speech-to-speech voice conversion (`TRN-04`), TTS/voice cloning
(`TRN-05`), quality assessment (`OBS-01`), enhancement (`CLN-01`), recognition,
translation or language identification into a TRN-03 result. Those rows are
named only as boundaries and their results are not promoted here.

No reviewed record is a rights-qualified accent-conversion benchmark. The
strongest local numbers are a three-clip TokAN smoke run with same-clip speaker
references, a six-class accent-classifier proxy without a Korean class, one
240 ms Seed-VC Realtime block on a generic VC path, a blocked MeanVC2 attempt,
and a decoder-only Vocos timing on synthetic mel. There is no independent target
accent, no manual transcript review, no blinded listening panel, no speaker
identity rating, no sustained-stream measurement and no multi-accent cohort.
Accent movement, naturalness and latency are therefore **not measured by this
survey**.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: formant/phonetic mapping (`S36`) | `ppg-foreign-accent-conversion` (considered) | Paper lead only; no code, checkpoint, corpus or local execution |
| Classic: duration/pitch modification | `soundtouch`, `psola-praat`, `rubber-band-r3-streaming` (evaluated, TRN-01) | Adjacent time-scale evidence; a duration/pitch change is not pronunciation mapping |
| ML: content-feature/PPG conversion with neural resynthesis | `tokan` (partial), `wavlm-large-in-tokan` (partial), `meanvc2` (partial), `seed-vc-25m` (partial), `seed-vc-xls-r-300m-content-encoder` (partial), `rvc-v2-vctk-p226` (partial) | Three-clip TokAN smoke, one generic VC block and a blocked MeanVC2 attempt; no accent-aware gold |
| ML: accent-aware streaming and zero-shot conversion (`S37`) | `seed-vc-v2-accent-aware-path`, `streaming-non-autoregressive-accent-conversion`, `dualvc-3`, `convert-and-speak`, `psdn-zero-shot-ac`, `voice-preserving-zero-shot-multiple-accent-conversion` (considered), `streamvc` (blocked) | Paper/demo or blocked rows; no local accent-aware streaming run |
| ML: neural resynthesis/vocoder | `vocos` (partial), `univnet`, `micro-hifi-gan`, `ms-istft-generator`, `fregan` (considered) | Decoder or component only; Vocos timing uses synthetic mel and is not end-to-end |

`report.json` holds the full records: both catalogued branches, the `S36`/`S37`
source-lead mapping, a 36-row component census checked against
`INVENTORY.json`, comparison inputs, controls, assets, local versus reported
outcomes, acceptance mapping, 15 gaps, 38 stable board links and all eight
blocked release gates. Historical numbers are transcribed from the pinned
accent-conversion report and result JSON with their original scope; they are
**not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | TokAN on three L1-accented English clips | `tokan`, `wavlm-large-in-tokan` | 3 speakers, 3 L1 groups; duration ratios 0.661–0.911; RTF 17.38–20.56; WER 0.00 vs source ASR; Resemblyzer cosine 0.798–0.874; finite 24 kHz mono; offline |
| `HE-2` | Six-class accent classifier on source/TokAN pairs | `tokan` | 3 pairs; ΔP(US) +0.170/+0.009/−0.051; no Korean class; uncalibrated directional proxy |
| `HE-3` | Seed-VC Realtime one 240 ms block | `seed-vc-xls-r-300m-content-encoder` | 2.2 s left / 0.2 s right context, 10 diffusion steps; 254.01 s load; 22.21 s block (92.55× real-time); generic VC, not accent-aware V2 |
| `HE-4` | MeanVC2 40 ms end-to-end attempt | `meanvc2` | ASR checkpoint loads; inference blocked on `wavlm_large.pt` and `wavlm_large_finetune.pth`; no converted audio or latency |
| `HE-5` | Vocos JIT decoder CPU timing | `vocos` | Synthetic 1 s 80-bin mel; 173 ms mean, RTF 0.175, finite 0.99 s output; decoder-only |

All five rows are **historical research executions, not merged task evidence**.
Every row is marked `merged_task_evidence: false`, `not_rerun: true` and "not
rerun by this survey". Comparison inputs separate the three TokAN pairs, the
classifier proxy, the Seed-VC block, the MeanVC2 blocked attempt, the Vocos
synthetic benchmark, the two source leads, the closed product documentation and
the missing rights-qualified cohort. Local and source-reported outcome ids are
disjoint.

## Evidence classes and failure envelope

- **Historical local three-clip smoke:** HE-1. It proves that one offline TokAN
  run produced finite audio and same-transcript proxies for three short clips,
  not that accent conversion is consistent or that identity is preserved.
- **Historical local classifier proxy:** HE-2. Only the Arabic pair shows a
  material P(US) increase; Hindi stays low and Korean decreases. The classifier
  has no Korean class and its Latin class uses about 100 samples.
- **Historical local generic streaming block:** HE-3. One first block at 92.55×
  real-time and 254 s load is far outside an interactive budget and is not a
  warmed-up sustained stream or the accent-aware V2 path.
- **Historical local blocked attempt:** HE-4. The MeanVC2 paper's 80 ms figure
  is a generic VC design-latency claim, not an accent-conversion result, and the
  local run produced no audio.
- **Historical local decoder component:** HE-5. Decoder-only CPU timing on
  synthetic features is not end-to-end conversion or quality.
- **Source-reported only:** the classical study (`S36`), the streaming study
  (`S37`, about 0.8 s), Convert and Speak, PSDN, multiple-accent conversion,
  AccentCL, AccentBox/GenAID, Krisp (~180 ms), Sanas, StreamVC and DualVC 3.
- **Not present:** a rights-cleared multi-accent corpus, target-accent gold,
  manual transcripts, human identity ratings, blinded listening, classifier
  calibration, sustained/device timing, rights-cleared target references,
  provider intake or release approval. These classes are `false`, not inherited
  from an adjacent survey.

The failure envelope is adverse. Three short clips cannot represent accents,
languages, noise or devices; same-clip speaker reference makes the TokAN result
a partial normalization test, not identity-preserving conversion. The classifier
moves only one of three samples materially toward US and cannot score Korean.
TokAN shortened one output by 34% and the others by about 9%, so duration
behaviour needs control. One generic VC block misses the interactive target by
orders of magnitude and the MeanVC2 run never reached conversion. A decoder-only
RTF of 0.175 says nothing about end-to-end accent conversion.

## Bounded gaps and feasibility links

Fifteen gaps are recorded. Gaps with an existing feasibility owner (`G03`,
`G06`, `G09`, `G10`, `G13`, `G14`) link classifier, streaming, PPG,
accent-aware, synthesis and vocoder rows. Gaps without a component feasibility
owner (`G01`, `G02`, `G04`, `G05`, `G07`, `G08`, `G11`, `G12`, `G15`) link
existing manifest, pipeline, research-control, implementation, foundation,
taxonomy or external-adapter rows and carry an explicit owner note. Those links
are scoping leads only: no converter is enabled, no capability is implemented
and no missing result is promoted. Board status is excluded from all gates; only
linked `id`/`title`/`mode` are projected to a stable digest. The mutable board
file is referenced by path and **never hashed into canonical bytes**, so status
edits elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep accent conversion separate from time-scale, pitch/prosody, voice
conversion, TTS/cloning, quality assessment, enhancement and recognition.
Pronunciation change is not timbre change; accent difference is not an audio
defect; streaming labels do not establish conversational delay. A classifier
probability is not target-accent gold; a speaker cosine is not a human identity
rating; one block is not a sustained stream; and a decoder benchmark is not an
end-to-end converter. Synthetic, adjacent-control, single-block, blocked,
source-reported and missing results stay distinct. No public benchmark, quality,
device, listening, latency or release claim is made. No assets, real audio,
weights, model, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and reviewers
were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte and checks three cold-start builds; `verify.py`
recomputes all artifacts, checks licensing, repeats the build in three fresh
processes and enforces task-local git scope; `test_reference.py` checks
canonical output, adverse rejections, domain boundaries and three cold-start
repeats. JSON and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-trn-03
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2`.

The change is task-local documentation and stdlib tooling; no installed package,
descriptor catalog, ABI, build input or CI workflow is touched. The repository's
installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` and its
inputs remain unchanged; no installed-package result is claimed here.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights, transcripts or consent. `AUDIOML_WORKSPACE_ROOT`
can point to the enclosing `audioml` checkout if automatic discovery is
unavailable.
