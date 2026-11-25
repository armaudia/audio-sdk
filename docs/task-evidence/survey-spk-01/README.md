<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-SPK-01 — generic speech/source separation evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`SPK-01` (Generic speech/source separation, legacy family `F05`). It matches
the catalogued classic and ML method families, the single named source lead
(`S08`) and the available adjacent historical local or source-reported
executions to existing components. It creates **no new execution, model,
corpus, provider, processor, ABI, default, build, CI, board, handoff,
benchmark or release change**.

Survey owner: `agent-SURVEY-SPK-01`; independent reviewer not dispatched.
Claim base: audio-sdk `3ba7466f644111318a71693900e4262e25b92176`; branch
`swarm/SDK-SURVEY-SPK-01`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested` / `catalogued` with candidate
census and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-spk-01/` only |
| Owner and independent reviewer | `agent-SURVEY-SPK-01`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-SPK-01`, `SDK-SURVEY-SPK-01`, `3ba7466f644111318a71693900e4262e25b92176` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no separator, baseline, provider, processor or runtime is selected |
| Source, model and dataset revisions/digests | `S08` Conv-TasNet paper (direct), the SpeechBrain SepFormer DNS4 checkpoint at its pinned Hub revision, the Hush source commit and ONNX bundle, and the pinned read-only documents in `SOURCES.sha256`; no weights or media are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-spk-01/`; planning and gap scoping only |

## What this map covers and what it refuses to claim

The catalogued output is a **set of source waveform estimates** from a
mixture. It is not overlapping-speech detection or speaker count (`DET-03`),
not target-speaker extraction or personalized enhancement (`SPK-02`), not
speaker-change segmentation (`SPK-03`), not anonymous diarization (`SPK-04`),
not speaker identity (`SPK-05`), not background noise suppression (`CLN-01`)
and not beamforming or localization alone. Those categories are named only as
boundaries. A separated stream is never permission to mute, delete, time-scale
or otherwise alter any source.

The catalogued boundary is preserved verbatim in `report.json`: **source
order, continuity and source count require handling, and separation does not
decide which sources to keep.** A target/masker ratio gain is not a separated
waveform. A single-output denoiser named "SepFormer" is not a multi-source
separator. A diarization label is not a source estimate. A speaker cue is not a
generic separation control.

The reviewed records contain **no SPK-01 multi-source separation execution**:
no Conv-TasNet run, no AuxIVA run, no two- or three-source cohort, no
permutation-invariant score and no separated-waveform listening result. Three
adjacent local rows are included only to show what exists nearby, and all are
explicitly marked `adjacent: true`, `not_component_evidence: true` and "not
rerun by this survey". No missing result is promoted to a pass.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Statistical/source-factorization (AuxIVA/ICA/NMF) | `auxiva`, `h-gtcrn` | Candidate only: AuxIVA is named in a two-microphone H-GTCRN census note; no staged implementation, geometry, initialization, permutation policy or local run |
| Classic | Spatial filtering, beamforming and localization boundary | `delay-and-sum-beamformer`, `mvdr-beamforming`, `source-localization-direction-of-arrival` | Adjacent spatial boundary; a beamformer or angle is not a generic multi-source waveform output |
| Classic | Speaker segmentation, diarization and identity boundary | `pyannote-diarization`, `bayesian-information-criterion-speaker-segmentation`, `x-vector-speaker-embeddings` | Annotation or identity rows (`SPK-03/04/05`), not separated waveforms |
| ML | Learned time-domain encoder/mask/decoder (`S08`) | `conv-tasnet` | Considered only: paper-level method and permutation-invariant objective; no revision, checkpoint, cohort or local output |
| ML | Time-frequency masking / dual-path transformer boundary | `speechbrain-sepformer-dns4` | Adjacent single-output DNS4 enhancer: one full waveform per call, offline; not multi-source separation |
| ML | Multichannel or beam-guided neural separation | `beam-tasnet-beam-guided-tasnet`, `spatialnet`, `neural-beamforming` | Blocked: exact architecture/checkpoint and synchronised array data unresolved |
| ML | Speaker-conditioned extraction and personal VAD | `target-speaker-extraction-family`, `voicefilter`, `voicefilter-lite-personal-vad` | `SPK-02` boundary only; blocked and cue-conditioned, not generic separation |
| ML-adjacent | Single-channel competing-speaker suppression | `hush` | Adjacent partially evaluated primary/background suppressor; one output, no enrollment, no isolated sources |

`report.json` holds the full records: both catalogued branches, the `S08`
source-lead mapping, the seventeen-row component census checked against
`INVENTORY.json`, comparison inputs, controls, assets, local-versus-reported
outcomes, the Spatial acceptance mapping, eleven gaps, twenty-five board links
and all eight blocked release gates. Source-reported numbers keep their
original documentation scope; they are **not** rerun, pooled into a benchmark
or promoted to a pass.

## Historical executions and comparison inputs

| ID | Execution or input | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | SpeechBrain SepFormer DNS4 offline enhancement screen | `speechbrain-sepformer-dns4` | **Adjacent.** 30 paired DNS2020 files plus 30 clean diagnostics; native ΔSI-SDR +8.525 dB, ΔSTOI +0.03313, ΔSNR −19.432 dB; mean RTF 0.693, peak RSS 1.89 GB; one output stream and whole-utterance inference |
| `HE-2` | Hush EARS primary/background suppression screen | `hush` | **Adjacent.** 30 target × 30 masker recordings at +12/+18/+24 dB SIR (90 mixtures); target/masker ratio gain +8.08 to +8.46 dB but target SI-SDR −9.33/−14.54/−20.23 dB and STOI −0.141/−0.176/−0.197; 10 ms observed delay |
| `HE-3` | Hush AMI speaker-dominant proxy diagnostic | `hush` | **Adjacent.** One AMI meeting, seven directed pairs and 21 synthetic mixtures; target SI-SDR −13.17/−18.41/−24.18 dB; target/masker-ratio intervals include zero in every stratum |
| `CI-1` | Conv-TasNet paper protocol (`S08`) | source lead | Source-reported method definition only; no weights, cohort or local score |
| `CI-2`–`CI-4` | SepFormer and Hush adjacent rows | component links | Same adjacent evidence as `HE-1`–`HE-3`; not separation |
| `CI-5` | AuxIVA / H-GTCRN classic lead | classic boundary | Census and plan notes; no execution |
| `CI-6` | Beam-TasNet, SpatialNet and neural beamforming | multichannel boundary | Blocked; no weights, geometry or array corpus |
| `CI-7` | TSE, VoiceFilter and VoiceFilter-Lite | `SPK-02` boundary | Blocked; cue-conditioned extraction, not generic separation |
| `CI-8` | Rights-qualified multi-source cohort with permutation-invariant scoring | **missing** | Absence recorded as missing, not as a negative separation result |

`HE-1`–`HE-3` are **adjacent historical local** rows, not SPK-01 separator
results. The source-reported rows describe candidate or protocol claims and
cannot establish local weights, labels, separation quality, latency or rights.
The missing row keeps an absent cohort explicit instead of silently empty.

## Evidence classes and failure envelope

- **Adjacent local single-output enhancement:** one SepFormer DNS4 offline
  screen on 30 DNS pairs. It proves the pinned checkpoint loads and improves
  single-stream SI-SDR/STOI; it does not produce multiple sources, resolve
  source count or establish streaming or mobile suitability.
- **Adjacent local competing-speaker suppression:** Hush EARS and AMI screens.
  They raise the relative target-to-masker projection ratio while lowering
  absolute target SI-SDR and STOI; AMI intervals include zero. Neither reports
  isolated source estimates, speaker IDs or a reference-conditioned extraction.
- **Classic and ML candidates:** AuxIVA, Conv-TasNet, Beam-TasNet, SpatialNet
  and the beamformers are plan notes, paper descriptions or blocked rows. No
  weights, array geometry or multi-source corpus is staged.
- **Source-reported only:** Conv-TasNet's method family, SepFormer DNS4's
  upstream DNSMOS values, Hush's vendor description and the multichannel
  architecture leads.
- **Not present:** a rights-qualified multi-source cohort, isolated references
  with natural overlap, a permutation-invariant scorer, source-count and
  continuity handling, real weights/runtime, listening, target-device timing
  and a benchmark.
- The failure envelope is adverse by omission: the only evaluated local rows
  are single-output and adjacent, and the only foundation-style inputs are
  manifests and evidence rules. Separation, detection, extraction, diarization
  and denoising are not interchangeable, so no capability is inherited from an
  adjacent task.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with a genuine feasibility lead (`G01`, `G02`,
`G05`, `G06`, `G07`) link existing Conv-TasNet, AuxIVA, multichannel, TSE and
diarization/identity rows. Gaps without a component owner (`G03`, `G04`, `G08`,
`G09`, `G10`, `G11`) link existing foundation or research-control rows and
carry an explicit `no component owner ...` note. Those links are scoping leads
only: no separator is enabled, no capability is implemented and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep multi-source separation, single-output enhancement, competing-speaker
suppression, target-speaker extraction, diarization, identity, beamforming and
noise suppression separate; keep candidate-documentation, adjacent-local,
prepared-manifest and missing evidence distinct; and require a source-count,
source-order and continuity policy before any downstream action. No public
benchmark/quality/device/listening/release claim is made. No provider
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
cd docs/task-evidence/survey-spk-01
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

The canonical `report.json` SHA-256 is written to `report.json.sha256` and
recomputed by `verify.py`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
