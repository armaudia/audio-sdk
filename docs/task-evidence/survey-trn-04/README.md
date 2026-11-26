<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-TRN-04 — speech-to-speech voice conversion evidence map

**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**
This package is a bounded, deterministic **taxonomy and comparison map** for
inventory category `TRN-04` (Speech-to-speech voice conversion, legacy family
`F14`). It matches the catalogued classic and ML method families, the two named
source leads (`S38`, `S39`) and the available historical research screens to
existing components. It creates **no new execution, model, corpus, provider,
processor, ABI, default, build, CI, board, handoff, benchmark or release
change**.

Survey owner: `agent-SURVEY-TRN-04`; independent reviewer not dispatched.
Claim base: audio-sdk `39b8885da4fc3ef8e27becf5df5f0658da3baf65`; branch
`swarm/SDK-SURVEY-TRN-04`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested_optional` / `catalogued` with
candidate census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-trn-04/` only |
| Owner and independent reviewer | `agent-SURVEY-TRN-04`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-TRN-04`, `SDK-SURVEY-TRN-04`, `39b8885da4fc3ef8e27becf5df5f0658da3baf65` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no converter, baseline, provider, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S38` StreamVC paper, `S39` Seed-VC upstream implementation, the pinned voice-conversion evaluation, accent-conversion boundary and Vocos timing documents in `SOURCES.sha256`; no weights or media are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-trn-04/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is converted speech for a **designated target speaker or
timbre** while retaining the spoken content. It is not accent conversion
(`TRN-03`), not reference-conditioned TTS or voice cloning (`TRN-05`), not
time-scale modification (`TRN-01`), not pitch/prosody control alone (`TRN-02`),
not generic source separation (`SPK-01`), not target-speaker extraction
(`SPK-02`), not denoising (`CLN-01`) and not quality assessment (`OBS-01`).
Those categories are named only as boundaries. A converted waveform is not a
target-similarity gold, a consent record or a release result.

The catalogued boundary is preserved verbatim in `report.json`: **evaluate
target similarity separately from words, prosody and delay; available
implementation and weights are required.** A speaker-embedding cosine is not a
human identity rating. A Whisper-tiny transcript match is not a content or
prosody certificate. A warm file RTF is not microphone-to-output latency. A
streaming label is not a sustained-stream measurement.

The reviewed records contain **no rights-qualified voice-conversion benchmark**:
no multi-speaker cohort, no multiple target references, no independent
listening panel, no target-similarity gold, no prosody/alignment metric and no
target-device timing. The strongest local numbers are one fixed source/target
pair through MeanVC2, Seed-VC, LLVC, OpenVoice V2, Chatterbox VC and RVC, one
240 ms Seed-VC Realtime block, and a decoder-only Vocos timing on synthetic
mel. All are transcribed historical research screens, not merged task evidence
and not rerun by this survey.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Statistical spectral mapping with vocoders; GMM family to search | `vocos-vocoder`, `hifi-gan-vocoder`, `ms-istft-generator` | Catalogued family has no statistical/GMM mapping component in the inventory; only vocoder boundary controls exist |
| Classic | Neural resynthesis/vocoder boundary | `univnet`, `micro-hifi-gan`, `fregan` | Component only; no acoustic converter, paired features or checkpoint |
| ML | Content/speaker-disentangled decoders | `meanvc2`, `meanvc`, `seed-vc-25m`, `seed-vc-xls-r-300m-content-encoder`, `llvc`, `openvoice-v2`, `chatterbox-vc`, `rvc-v2-vctk-p226`, `rvc-faiss-retrieval`, `rvc-mlx-realtime`, `contentvec`, `hubert-conversion-encoder`, `wavlm-conversion-encoder`, `quickvc` | One-pair historical screens; blocked or considered encoder/RVC rows |
| ML | Streaming and flow/diffusion variants | `streamvc`, `x-vc`, `rt-vc`, `dualvc-3`, `vits-streaming-adaptation`, `vocos` | Blocked or considered; no sustained stream or device run |
| ML-adjacent | Reference-conditioned TTS / voice cloning (`TRN-05`) | `cosyvoice-2-0-5b`, `chatterbox-nano`, `kokoro-82m`, `neutts-nano-q4`, `yourtts` | Boundary only; a TTS/cloning result is not a converted source waveform |
| ML-adjacent | Accent conversion (`TRN-03`) | `tokan`, `seed-vc-v2-accent-aware-path`, `streaming-non-autoregressive-accent-conversion`, `psdn-zero-shot-ac`, `convert-and-speak`, `voice-preserving-zero-shot-multiple-accent-conversion`, `ppg-foreign-accent-conversion` | Boundary only; pronunciation change is not designated-speaker/timbre conversion |

`report.json` holds the full records: both catalogued branches, the `S38`/`S39`
source-lead mapping, a 38-row component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local-versus-reported outcomes, acceptance
mapping, thirteen gaps, forty-four stable board links and all eight blocked
release gates. Historical numbers keep their original documentation scope; they
are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | MeanVC2 40+40 ms file-mode conversion | `meanvc2` | One fixed pair; init 14.4 s, 9.35 s for 9.75 s output, file RTF 0.959, WER 0.00, in-model cosine 0.669; no device path |
| `HE-2` | MeanVC2 120+40 ms file-mode conversion | `meanvc2` | Same pair; init 15.2 s, 3.79 s for 9.59 s output, file RTF 0.396, WER 0.00, in-model cosine 0.702 |
| `HE-3` | Seed-VC 25M file conversion | `seed-vc-25m`, `seed-vc-xls-r-300m-content-encoder` | Four diffusion steps, guidance 0.0; first-run RTF 1.32, warm file RTF 0.244; GUI/device path not exercised |
| `HE-4` | LLVC CPU streaming simulation | `llvc` | 13 ms chunks, about 106 ms inference per chunk, cold 78.836 s for 9.655 s; source WER 3.70%, output WER 0.00%; target similarity unscored |
| `HE-5` | OpenVoice V2 offline conversion | `openvoice-v2` | Whole-file; 3.29 s for 9.648 s, RTF 0.341, WER 0.00, in-model cosine 0.890; no causal streaming |
| `HE-6` | Chatterbox VC offline conversion | `chatterbox-vc` | Whole-file third-party converter; 25.47 s for 9.68 s, RTF 2.63, WER 0.00; not real-time on the host |
| `HE-7` | RVC v2 VCTK p226 file conversion | `rvc-v2-vctk-p226` | RMVPE F0, retrieval disabled; 7.75 s for 9.64 s, RTF 0.804, WER 0.00; speaker id 1 presumed p226, FAISS crashes |
| `HE-8` | Seed-VC Realtime one 240 ms block | `seed-vc-xls-r-300m-content-encoder`, `seed-vc-25m` | 254.01 s load, 22.21 s block (92.55x real-time); one first block, not a sustained stream or the accent-aware V2 path |
| `HE-9` | Vocos JIT decoder CPU timing | `vocos` | Synthetic 1 s 80-bin mel; mean 0.173 s, RTF 0.175, finite 0.99 s output; decoder-only, not end-to-end |

`CI-1` is the fixed LJ Speech source plus the RT-VC p360 reference; `CI-2`–`CI-8`
are the historical screens above; `CI-9` is the text-only `S38`/`S39` lead;
`CI-10` is the missing rights-cleared multi-speaker cohort. The p360 reference is
an upstream demo whose dataset/license provenance is not confirmed, so every
historical row is research-only.

## Evidence classes and failure envelope

- **Historical local file-mode conversion:** MeanVC2, Seed-VC, OpenVoice V2,
  Chatterbox VC and RVC produced finite outputs for one fixed pair. They prove
  local execution and a limited transcript/clipping check, not broad quality,
  multi-speaker generalization or live-call latency.
- **Historical local stream simulation:** LLVC completed its CPU stream
  simulation but missed the 13 ms chunk deadline by a wide margin; Seed-VC
  Realtime produced one 240 ms block at 92.55x real-time. Neither is a warmed-up
  sustained stream or a device-to-device measurement.
- **Decoder-only:** Vocos was timed on synthetic mel and output shape. It is not
  an end-to-end voice converter.
- **Classic and ML candidates:** the statistical/GMM family has no inventory
  component; StreamVC, X-VC and RT-VC are blocked; content encoders and vocoders
  are components only.
- **Source-reported only:** StreamVC's paper, Seed-VC's upstream GUI profile,
  MeanVC2's design-latency figure, LLVC's estimate and RVC checkpoint metadata.
- **Not present:** a rights-cleared cohort, multiple speakers/targets/languages,
  independent listening, target-similarity gold, prosody/alignment metrics,
  staged exact weights, target-device timing, a benchmark and release approval.
- The failure envelope is adverse by omission: a missing result is never a pass,
  and no adjacent TTS, accent or enhancement result is inherited.

## Local versus reported outcomes

`report.json.local_vs_reported_outcomes` keeps the classes disjoint:
`historical_executions` are `historical_local_not_rerun` and
`reported_outcomes` are `source_reported_not_reproduced`. The cross-comparison
is explicitly **not performed** and no numeric parity is claimed, because no
matched frozen asset, runtime, settings or listening protocol is shared. Every
ledger row records `comparison_performed=false` and `qualifies_candidate=false`.

## Bounded gaps and feasibility links

Thirteen gaps are recorded. Gaps with a genuine feasibility lead (`G07`, `G09`,
`G10`, `G11`) link existing streaming, vocoder, TTS and accent rows. Gaps
without a component owner (`G01`–`G06`, `G08`, `G12`, `G13`) link existing
research-control, pipeline, foundation or implementation rows and carry an
explicit `owner_note`. Those links are scoping leads only: no converter is
enabled, no capability is implemented and no missing result is promoted. Board
status is excluded from all gates; only linked `id`/`title`/`mode` are projected
to a stable digest. The mutable board file is referenced by path and **never
hashed into canonical bytes**, so status edits elsewhere in the swarm cannot
change this map or break its digest.

## Release boundary

All eight release gates remain blocked:

1. rights-cleared multi-speaker/multi-target cohort with consented references;
2. frozen partitions with independent listening, naturalness and manual review;
3. independent target-similarity, content/prosody and duration metrics;
4. pinned exact model bundles, revisions, per-weight terms and locked runtimes;
5. causal streaming, first-output/tail, sustained CPU/accelerator and device timing;
6. explicit target-voice and consent policy separating timbre from content/prosody/accent;
7. opt-in provider/external-adapter intake with independent exact-head review;
8. release approval; `DEFER` remains in force until every gate is closed.

No public benchmark, quality, target-similarity, device, listening or release
claim is made. No provider registration, installed-v0/ABI/registry/default/
shared-build/CI change, real corpus, weights, runtime invocation, audio
mutation, listening, device timing, benchmark or release approval is included.
All files are inside this task directory; board, handoff and reviewers were not
changed or dispatched.

## Pinned inputs

Paths beginning `source:` in the manifest are relative to the enclosing
`audioml` workspace; `worktree:` paths are SDK-worktree relative. The pinned
documents include `plan/INVENTORY.json`, the Voice acceptance profile,
`audio_categories.md`, `research/category_registry.json`,
`research/category_survey/sources.md`, the task backlog, the voice-conversion
evaluation README, its matrix crosswalk and breadth audit, the accent-conversion
boundary README and Vocos timing JSON. Sibling `survey-trn-01` and
`survey-spk-01` READMEs are pinned only as adjacent boundaries. Their packages
and `survey-trn-02`, `survey-trn-03` and `survey-spk-05` were not present on
this base, so no unmerged sibling evidence is used.

`SOURCES.sha256` enumerates every source, worktree and local artifact pin.
`verify.py` fails closed on a missing, stale, duplicated or malformed pin,
non-canonical JSON, duplicate/nonfinite JSON keys, stale digest sidecar, an
unlinked gap, an out-of-scope worktree change or a licensing gap.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, and repeats the build in three cold-start
processes; `test_reference.py` checks canonical output, adverse and nonfinite
rejection, boundary separation and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-trn-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

The canonical `report.json` SHA-256 is written to `report.json.sha256` and
recomputed by `verify.py`. The change is task-local documentation and stdlib
tooling; no installed package, descriptor catalog, ABI, build input or CI
workflow is touched.

## Disposition

The map is complete only as a survey of text evidence. It does not close any
component task, qualify a candidate, register a provider, change a default or
support a release. Missing evidence never qualifies a candidate: the outcome is
`DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.
