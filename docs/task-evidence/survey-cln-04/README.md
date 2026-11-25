<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-04 — dereverberation evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-04` (Dereverberation, legacy family `F03`). It matches the catalogued
method families, both named source leads (`S20`, `S31`) and historical local or
source-reported executions to existing components. It creates **no new
execution, model, corpus, provider, processor, ABI, default, build, CI, board,
handoff or release change**.

Survey owner: `agent-SURVEY-CLN-04`; independent reviewer:
`reviewer-SURVEY-CLN-04`. Claim base: audio-sdk
`711c5c2a419edf258d6858fa90293c5900faad82`; branch
`swarm/SDK-SURVEY-CLN-04`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested` / `catalogued` with candidate census
and benchmark both `not_started`.

## What this map does and does not cover

The catalogued boundary is explicit: **reverberation is not playback echo**,
and offline, block-online and incremental variants must stay separate. Mono and
synchronized multi-microphone inputs are also separate subcases. This map keeps
those boundaries visible and does **not** pool AEC, echo-suppression or generic
denoising results into a dereverberation claim.

The local evidence is real work but bounded: WPE screens exist on synthetic
EARS excerpts convolved with measured SMARD RIRs, plus task-local synthetic
fixtures. The measured rooms are direct-path dominated, one 50 ms
early-reflection target convention is used, and no captured real-room speech,
human listening, ASR, SRMR-on-real-data or target-device timing result exists.
Identity remained the best measured CPU choice on those direct-dominated rooms;
WPE did not win overall. The task-local causal fixture helps show where a
metric tradeoff appears, not that online WPE is qualified.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: delayed linear prediction; offline WPE | `offline-mono-wpe`, `offline-multichannel-wpe` (evaluated): 72-case EARS/SMARD screen, identity 16.49 dB SI-SDR / .9853 STOI versus offline 13.35 dB / .9699, median RTF .0089, 2/72 SI-SDR wins and 0/72 STOI wins; 18-trial measured-SMARD multichannel screen, offline 13.582 dB / .96829, 0/18 wins | Whole-clip prediction is **noncausal**; direct-dominated rooms; no real-room, listening or causal claim |
| Classic: frame-causal / block-online WPE | `online-mono-wpe-reference`, `online-multichannel-wpe` (evaluated): 72-case screen online 12.28 dB / .9760, median RTF .2604, 1/72 SI-SDR wins, 0/72 STOI wins; 18-trial SMARD online mono 18.431 dB / .99052, 15/18 wins but +0.041 dB over identity; severe synthetic room STOI .597→.619 with SI-SDR 2.41→0.74 dB | Stateful and frame-causal, but no material quality gain on direct-dominated rooms; no device timing |
| Classic: NARA-WPE reference tools (`S20`) | `nara-wpe-reference-tools` (considered) | Search-excerpt lead only; no pinned checkout or local NARA execution |
| Classic: adjacent playback-echo/AEC boundary | `speexdsp-mdf-reference`, `speex-mdf-residual-postfilter` (evaluated) | Named only as echo-cancellation controls; not pooled as dereverberation |
| ML: DNN-supported prediction and nonlinear postfilters | `2s-dereverb` (considered), `nemo-schr-dinger-bridge-dereverberation` (blocked), `localvqe-dereverberation-probe` (partial), `localvqe-compact-full` (evaluated) | NeMo weights missing; 2S-Dereverb has no staged checkpoint; LocalVQE was run with zero far-end, outside its AEC intent |
| ML: restoration, flow-matching and generative resynthesis (`S31`) | `stream-fm-dereverberation` (considered), `rose-cd-ears-reverb-configuration` (source-only), `voicefixer` (considered) | Paper/model-card values only; AGPL/CC BY-NC-SA and cross-domain checkpoint boundaries unresolved |
| ML: generic streaming enhancer as cross-domain probe | `gtcrn-streaming-onnx` (partial): 72-case probe, median SI-SDR 5.66 dB versus identity 16.49 dB, 0/72 wins, RTF .0459 | Not a dereverberation-trained model; STOI not measured; negative cross-domain evidence only |

`report.json` holds the full records: both catalogued branches, the `S20` and
`S31` source-lead mappings, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Offline and online mono WPE 72-case EARS/SMARD screen | `offline-mono-wpe`, `online-mono-wpe-reference` | Synthetic convolution with measured direct-dominated RIRs; no captured speech or listening |
| `HE-2` | Measured-SMARD mono and three-channel WPE screen | `offline-multichannel-wpe`, `online-multichannel-wpe` | 18 controlled trials on channels 4X/4Y/4Z; gains effectively zero |
| `HE-3` | Severe synthetic-room online WPE stress screen | `online-mono-wpe-reference` | 16 synthetic pairs; STOI up, SI-SDR down; metric tradeoff |
| `HE-4` | LocalVQE zero-far-end streaming misuse screen | `localvqe-dereverberation-probe`, `localvqe-compact-full` | 72 pairs; −0.99 dB SI-SDR / .6389 STOI versus identity; outside intended AEC use |
| `HE-5` | GTCRN streaming ONNX cross-domain probe | `gtcrn-streaming-onnx` | 72 pairs; 5.66 dB SI-SDR, 0/72 wins; STOI not measured |
| `HE-6` | Causal online WPE synthetic fixture with clean preservation | `online-mono-wpe-reference` | Three pinned RT60 rooms; seed/analytic source; no real speech |
| `HE-7` | SRMR and C50-style reverb metric fixture | `srmr-and-reverb-metrics` | Three synthetic rooms; complementary metric control only |

Comparison inputs add the declared 50 ms early-reflection target, the noisy and
clean-preservation controls, the measured-SMARD multichannel trials, the
LocalVQE misuse screen, the GTCRN cross-domain probe, and a **missing**
rights-qualified real-room/standard cohort. Reported outcomes separately record
NeMo (PESQ 2.79 / ESTOI .89 / SI-SDR 7.4 dB / WER 4.27%), ROSE-CD (PESQ 2.69 /
ESTOI .82 / WER 15.78%), Stream.FM (PESQ 1.32→2.05 / ESTOI .58→.79 / SI-SDR
−16.6→−13.5 dB at 32 ms algorithmic / 48 ms total) and SB-UFOGen (PESQ 3.36 /
SI-SDR 8.73 dB / ESTOI .88 / MOS Reverb 4.71). Every reported row stays distinct
from the local rows; every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local paired synthetic:** the 72-case EARS/SMARD screen, severe
  synthetic-room stress, LocalVQE misuse, GTCRN cross-domain probe and the
  task-local causal fixture. These are comparison and failure-envelope evidence,
  not real-room qualification.
- **Historical local measured RIR:** the 18-trial SMARD multichannel screen.
  It is a controlled measured-RIR test, not captured array speech.
- **Historical local metric control:** SRMR/C50 on three synthetic rooms.
  Complementary and non-intrusive; never a selection criterion alone.
- **Clean-preservation diagnostic:** synthetic clean-source preservation
  (SI-SDR 11.071693 dB, STOI 0.977112) and bit-exact identity. No real-speech
  preservation or listening result exists.
- **Source-reported only:** NeMo, ROSE-CD, Stream.FM and SB-UFOGen model-card or
  paper values. No local runtime, exact checkpoint, matched cohort or numeric
  parity follows.
- **Not present:** real-room/standard paired cohort, human ratings, ASR,
  live-microphone test, target-device timing, staged dereverb weights, or a new
  execution. Offline WPE is noncausal and is never used as causal evidence.
- The adverse envelope is explicit: offline WPE regressed on direct-dominated
  rooms; online gains were negligible; the severe-room screen improved STOI but
  degraded SI-SDR; LocalVQE and GTCRN lost to identity. These are recorded as
  measured, not smoothed into a selection.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G02`, `G03`, `G04`,
`G08`, `G09`) link **existing** NARA-WPE, 2S-Dereverb, Stream.FM, NeMo,
ROSE-CD or VoiceFixer rows. Gaps without a component owner (`G01`, `G05`,
`G06`, `G07`, `G10`) link existing research-control or foundation rows and
carry a `no dedicated CLN-04 ...` owner note. Those links are scoping leads
only: no processor is enabled, no capability is implemented, and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep reverberation separate from playback echo; keep offline, block-online and
incremental variants separate; keep mono and synchronized multichannel separate;
declare the early-reflection target; preserve clean speech; and keep synthetic,
measured-RIR, source-reported, prepared-listening and missing results distinct.
No public benchmark/quality/device/listening/release claim is made. No assets,
real reverb audio, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and reviewers
were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical output,
adverse rejections and three cold-start repeats. JSON and manifest files have
SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-04
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `4eb1609bde772ab949c84dc5508bf790af05d0847a9cdcd03635dccf5e6369d6`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
