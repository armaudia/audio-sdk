<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-SPK-02 — target-speaker extraction and personalized enhancement evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`SPK-02` (Target-speaker extraction and personalized enhancement, legacy family
`F05`). It matches the catalogued classic and ML method families, both named
source leads (`S07`, `S50`) and the available adjacent local or source-reported
executions to existing components. It creates **no new execution, model,
corpus, checkpoint, enrollment cue, provider, processor, ABI, default, build,
CI, board, handoff, benchmark or release change**.

Survey owner: `agent-SURVEY-SPK-02`; independent reviewer not dispatched.
Claim base: audio-sdk `ba77ffbae0b879c1b4099ccace5065ffb31fffdb`; branch
`swarm/SDK-SURVEY-SPK-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `requested` / `catalogued` with candidate census
and benchmark both `not_started`.

| Field | Record |
| --- | --- |
| Repository and scope | `audio-sdk`; task-local documentation and stdlib tooling under `docs/task-evidence/survey-spk-02/` only |
| Owner and independent reviewer | `agent-SURVEY-SPK-02`; reviewer not dispatched |
| Claim time, branch, worktree and base commit | 2026-11-26, `swarm/SDK-SURVEY-SPK-02`, `SDK-SURVEY-SPK-02`, `ba77ffbae0b879c1b4099ccace5065ffb31fffdb` |
| Outcome | Deferred; proposal-only survey, no qualification |
| Implementation commit and integration revision | Survey-only evidence commit on the branch above; no SDK integration |
| Provider, recipe or tool ID and effective settings | None; no provider, extractor, separator or runtime is selected |
| Source, model and dataset revisions/digests | `S07` VoiceFilter paper (direct), `S50` audio-visual target-speaker enhancement (search excerpt in prior brainstorm), plus the pinned read-only documents in `SOURCES.sha256`; no weights, checkpoints or enrolled corpus are staged |
| Approved evidence location and permitted uses | `docs/task-evidence/survey-spk-02/`; planning and gap scoping only |

## What this map covers and what it refuses to conflate

The catalogued output is a **waveform**: the selected speaker's speech recovered
from a mixture, conditioned on a target cue. It is not generic source separation
(`SPK-01`), not speaker-change detection (`SPK-03`), not anonymous diarization
(`SPK-04`), not speaker identification or verification (`SPK-05`), not
target-speaker/personalized VAD (`DET-05`), not overlap detection or speaker
count (`DET-03`), not beamforming as a category (`CLN-07`) and not noise
suppression (`CLN-01`). Those rows are named only as boundaries.

The catalogued boundary is explicit and is preserved verbatim in `report.json`:
**Enrollment, spatial or visual cues are input facets. Identity matching does
not define who the user wants to hear.** An enrolled voice is a cue, not the
definition of the preferred speaker. A spatial direction is not an identity. A
visual track is not an audio-only enrollment protocol. A generic separator that
returns several sources is not a target selector. A competing-speaker suppressor
that raises a target/masker ratio while damaging the target is not an extractor.
An identity score is not a waveform.

The reviewed records contain **no SPK-02 extraction execution**: no
enrollment-conditioned run, no target-selected waveform, no clean target
reference comparison, no target-absent or impostor set, no natural-overlap
target extraction and no listening or device-timing result. The two local
executions are **adjacent Hush suppression diagnostics** and are explicitly
marked `adjacent: true`, `not_component_evidence: true` and "not rerun by this
survey". No missing result is promoted to a pass.

## Method families and mapped evidence

| Catalogued branch | Family | Mapped components | Status and boundary |
| --- | --- | --- | --- |
| Classic | Cue-based filtering with spatial or statistical filters (`MF-C1`) | `delay-and-sum-beamformer`, `mvdr-beamforming`, `auxiva`, `3d-microphone-spatial-time-alignment` | Considered only: filters a spatial direction or separates sources; no enrolled voice cue, calibrated array or target-selected output |
| Classic | Statistical target-speaker family search, still open (`MF-C2`) | none | No statistical extractor, target model, cohort or execution; the open search is recorded, not filled with a generic denoiser |
| ML | Speaker-conditioned masks/filters, VoiceFilter family (`MF-M1`, `S07`) | `voicefilter` (blocked), `voicefilter-lite-personal-vad` (blocked) | Original Google weights/runtime are not open; VoiceFilter-Lite is vendor-reported; personal VAD is activity, not a waveform |
| ML | Other cue-conditioned extraction, spatial or visual (`MF-M2`, `S50`) | `target-speaker-extraction-family` (blocked) | No selected model, cue modality or corpus; `S50` is a search excerpt with no video track or checkpoint |
| ML | Adjacent generic separation and multichannel extraction (`MF-M3`) | `conv-tasnet` (considered), `beam-tasnet-beam-guided-tasnet` (blocked), `spatialnet` (blocked) | Separation returns several sources with permutation and count questions; it does not choose the requested speaker |
| ML | Adjacent causal competing-speaker suppression (`MF-M4`) | `hush` (partial) | No enrollment prompt or speaker IDs; raises target/masker ratio while lowering target SI-SDR and STOI |
| ML | Adjacent speaker-embedding and similarity cue suppliers (`MF-M5`) | `x-vector-speaker-embeddings`, `resemblyzer-speaker-similarity-proxy`, `speechbrains-ecapa-speaker-similarity` | Cue suppliers only; in-model cosines are encoder-specific diagnostics, not verification or extraction |
| ML | Adjacent vendor voice-isolation output scoring (`MF-M6`) | `krisp-voice-isolation-public-output-scoring` | Company-produced external benchmark of its own feature; no local runtime or matched cohort |

`report.json` holds the full records: both catalogued branches, both
source-lead mappings, a 22-row component census checked against `INVENTORY.json`,
eleven comparison inputs, nine controls, nine assets, two adjacent historical
executions, six reported outcomes, the Spatial acceptance mapping, fourteen
gaps, twenty-eight linked board rows and all eight blocked release gates.
Transcribed numbers keep their original scope; they are **not** rerun, pooled
into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Adjacent execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Hush EARS primary/background screen, 30 pairs × 3 SIR = 90 mixtures | `hush`, SI-SDR/STOI scorers | Target/masker ratio +8.14/+8.08/+8.46 dB but target SI-SDR −9.33/−14.54/−20.23 dB and STOI −.141/−.176/−.197; no speaker IDs, no enrollment prompt, 10 ms observed delay |
| `HE-2` | Hush AMI ES2004a speaker-dominant diagnostic, 7 directed pairs × 3 SIR = 21 mixtures | `hush`, SI-SDR/STOI scorers | Constructed non-overlap turn proxies from one mono meeting; target SI-SDR −13.17/−18.41/−24.18 dB, STOI −.193/−.200/−.207; ratio gains +3.70/+7.33/+3.37 dB with intervals including zero |

`CI-1` and `CI-2` are the direct `S07` and search-excerpt `S50` protocol leads.
`CI-3`–`CI-5` are the three blocked candidate rows. `CI-6` and `CI-7` are the
two adjacent Hush screens. `CI-8` records in-model speaker-similarity cosines
(0.890, 0.669, 0.702) as an identity diagnostic. `CI-9` is the Krisp vendor
benchmark. `CI-10` is the adjacent spatial/separation component boundary.
`CI-11` is the **missing** rights-qualified enrolled-speaker corpus with clean
target references, real overlap and target-absent negatives. Missing evidence is
recorded explicitly rather than silently empty.

## Evidence classes and failure envelope

- **Adjacent local suppression:** `HE-1` and `HE-2` only. The exact Hush API
  accepts no enrollment or reference waveform, EARS has no speaker identities
  and the AMI crops are speaker-dominant proxies, not isolated references.
- **Source-only protocol:** the VoiceFilter paper (`S07`) and the audio-visual
  search excerpt (`S50`). Method context, not weights or a run.
- **Source-reported candidate:** VoiceFilter, VoiceFilter-Lite/personal VAD and
  the target-speaker extraction family. All are blocked or vendor-reported.
- **Source-reported vendor benchmark:** the Krisp Voice Isolation study scores
  its own feature on target-speaker segments. It is external and untransferred.
- **In-model similarity diagnostic:** encoder-specific cosines from
  voice-conversion evaluations. They are not verification and not comparable
  across encoders.
- **Missing:** enrollment-conditioned execution, target-selected output,
  clean-target-reference accuracy, real overlap, target-absent negatives,
  weights/runtime, human listening, device timing and a benchmark.
- The failure envelope is adverse by construction: generic separation cannot
  decide which source to keep, suppression can improve a ratio while damaging
  the target, an identity score is not a waveform, and an unenrolled region is
  unknown rather than non-target.

## Bounded gaps and feasibility links

Fourteen gaps are recorded. Gaps with a genuine feasibility lead (`G01`, `G02`,
`G04`, `G05`, `G08`, `G09`, `G11`) link existing VoiceFilter, TSE-family,
embedding, beamformer, separation or cross-reference rows. Gaps without a
dedicated SPK-02 component owner (`G03`, `G06`, `G07`, `G10`, `G12`, `G13`,
`G14`) link existing foundation, research-control or taxonomy rows and carry an
explicit `no dedicated SPK-02 ...` owner note. Those links are scoping leads
only: no extractor or separator is enabled, no capability is implemented and no
missing result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep target extraction separate from generic separation, competing-speaker
suppression, personalized VAD, diarization and identity policy. Keep enrollment,
spatial and visual cues as distinct input facets, and keep an identity match
from defining the preferred speaker. Require a clean target reference, real
overlap and target-absent negatives before any extraction claim; require target
preservation and off-target suppression together; require sample-count, finite
output and device timing before any runtime claim. No extraction quality,
separation, identity, perceptual, device, benchmark or release claim is made. No
provider registration, installed-v0/ABI/registry/default/shared-build/CI change,
real corpus, weights, runtime invocation, audio mutation, listening,
device-timing, benchmark or release approval is included. All files are inside
this task directory; board, handoff and reviewers were not changed or
dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope, and repeats the build in three cold-start
processes; `test_reference.py` checks canonical output, adverse and nonfinite
rejection, adjacent-execution boundaries and three cold-start repeats. JSON and
manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-spk-02
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `4458c4dffbe1633d82669f3b13411d5813148555df1ed2e5ba502bb886b6f8e1`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media, weights or annotations. `AUDIOML_WORKSPACE_ROOT` can
point to the enclosing `audioml` checkout if automatic discovery is unavailable.
