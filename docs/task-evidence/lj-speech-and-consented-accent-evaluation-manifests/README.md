<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS — manifest/consent blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LJ Speech and consented accent evaluation manifests`
(`component_id=lj-speech-and-consented-accent-evaluation-manifests`).
Acceptance profile: **Evidence**, assigned by `plan/INVENTORY.json` and defined
in `plan/swarm/VERIFICATION.md`. Task mode: **research-control**. Machine-readable
decision: **`DEFER`**; `status=proposal_only_incomplete`,
`evidence_status=incomplete`, `qualification.status=not_qualified`,
`qualification.candidate_qualified=false`, `candidate_metrics=null`. No result
qualifies any evaluation.

The pinned research notes retain a fixed LJ Speech source clip, an RT-VC demo
target reference and three L2-ARCTIC accent clips. Five local copies are
present and are **hash-pinned as observations only**. No machine-readable
source, accent-group, target-reference, cohort, consent, terms, scoring or
approval manifest exists. The target-reference provenance is explicitly
unconfirmed; the L2-ARCTIC copies carry no per-speaker consent; the TokAN
sample copy is reported without a visible licence. Nothing is admitted,
decoded, copied, measured or published.

Pinned base: `b4960fdba1991a35c07ff7f22cda5257c4749768`.
Branch: `swarm/SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS`.
Worktree: `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS`.

## Exact blockers

1. **Source manifest absent.** Only a prose table in
   `research/voice-conversion-eval-20261101/README.md` describes
   `LJ001-0001.wav`; no JSON manifest pins the transcript, geometry, byte
   count, SHA-256, licence or rights record.
2. **Accent-group manifest absent.** The three local L2-ARCTIC copies
   (`ABA_arctic_a0046.wav`, `RRBI_arctic_a0391.wav`,
   `HJK_arctic_a0103.wav`) have no manifest with speaker, clip identifier, L1
   group, source locator, byte count, duration or transcript. The README
   publishes no digest for them.
3. **Target-reference provenance absent.** The p360 FLAC is hash-pinned, but
   the pinned README states that its dataset/licence provenance is not yet
   confirmed; no speaker or redistribution permission exists.
4. **Per-speaker consent absent.** No consent record covers LJ001, p360, ABA,
   RRBI or HJK for conversion, accent modification, output publication,
   retention or redistribution.
5. **Dataset terms and redistribution unresolved.** The pinned notes report
   CC BY-NC 4.0 for L2-ARCTIC, no visible licence file for the TokAN sample
   repository, and only a source-reported public-domain claim for LJ Speech.
   No attribution, noncommercial boundary or redistribution grant is recorded
   for the local copies.
6. **Rights-cleared cohort and split absent.** No frozen cohort, paired or
   unpaired roles, held-out speakers/items, negative or quiet controls, or
   permitted-use statement exists.
7. **Evidence separation, scoring and controls absent.** No pinned scorer,
   manual transcript, accent ground truth, aggregation plan, failed-item policy
   or bundle path exists. The accent classifier is a directional proxy, not
   L2-ARCTIC ground truth; blinded listening remains outstanding.
8. **Approved adapter and release absent.** No opt-in adapter decision,
   independent exact-head review, default policy or release/benchmark approval
   exists.

## Present local observations

The audit reads fixed workspace paths and computes SHA-256 over file bytes. It
does **not** decode, play, resample, copy or admit any clip.

| Role | Workspace path | SHA-256 | Declared in pinned README? |
| --- | --- | --- | --- |
| LJ Speech source | `research/voice-conversion-eval-20261101/data/source_ljspeech_lj001-0001.wav` | `adc9736d0a02b8efe57128b2c6843605e81ab24027f23f6fc7d05bcd6107753b` | **Yes**, exact match |
| Target reference | `research/voice-conversion-eval-20261101/data/target_rtvc_p360.flac` | `fcfffdbf9b96bdc720f924de1877f515766e438242afe2306f4a919ba6809b44` | **Yes**, exact match; provenance unconfirmed |
| Arabic accent | `research/accent-conversion-20261101/data/l2accent/ABA_arctic_a0046.wav` | `bee4a2b42ef31e3bec2407a0c86d57a80fb5709e0ce19ae2524960797afb1f48` | No digest published |
| Hindi accent | `research/accent-conversion-20261101/data/l2accent/RRBI_arctic_a0391.wav` | `90622687e541f0b2ea2893d8125ec27e8600f13e5d085f67c5c6bef3764fe763` | No digest published |
| Korean accent | `research/accent-conversion-20261101/data/l2accent/HJK_arctic_a0103.wav` | `136cf347d8ed8e33c1811c9507ee7ff3ccb6bfa7fc7f1ad66e43349cc25ab3c2` | No digest published |

Every observed artifact has `admitted=false` and `consent_status=absent`.
Presence is not permission. If a fourth accent clip appears, or any reserved
manifest/consent path appears, `verify.py` fails closed so the blocker must be
re-evaluated rather than silently promoted.

## Reserved absent artifacts

The package reserves, but does not create, these paths:

- `data/manifests/lj-speech-and-accent-eval/source.json`
- `data/manifests/lj-speech-and-accent-eval/accent-groups.json`
- `data/manifests/lj-speech-and-accent-eval/target-references.json`
- `data/manifests/lj-speech-and-accent-eval/cohort.json`
- `data/rights/lj-speech-and-accent-eval/consent.json`
- `data/rights/lj-speech-and-accent-eval/terms.json`
- `data/reference/lj-speech-and-accent-eval/scoring-plan.json`
- `data/runs/lj-speech-and-accent-eval/approval.json`

## Caller-supplied manifest contract

A manifest is accepted only when it has exactly the declared 31 top-level
fields and exactly three accent entries with the declared 10 fields each. Every
path must be absolute, unique and present; every SHA-256 must match; geometry
must be 16 kHz / mono / `f32` / 160 samples; the source must be
`ljspeech_lj001_0001`; the target must be `rtvc_p360`; and the accent entries
must exactly cover ABA/`arctic_a0046`/arabic, RRBI/`arctic_a0391`/hindi and
HJK/`arctic_a0103`/korean. Transcripts, licences, provenance, consent, terms,
cohort, scoring and approval records are all required.

Structural acceptance always returns `admitted_for_evaluation=false`,
`accepted_for_qualification=false`, `consent_verified=false`,
`rights_approved=false`, `reviewer_approved=false` and
`qualification_effect=none`. The validator never decodes audio, creates a
manifest, downloads anything or grants permission. All assets are
caller-owned; nothing is vendored.

## Evidence-profile application

`plan/swarm/VERIFICATION.md` Evidence row requires a pinned scorer, corpus and
cohort, aggregation, failed items and controls, separation of paired, unpaired,
synthetic, human and source-reported evidence, and validation of one
invalid/missing case and one representative valid result through the reported
bundle.

| Requirement | Package status |
| --- | --- |
| Scorer pin | `absent` |
| Corpus pin | `partial_observations_only` |
| Cohort pin | `absent` |
| Aggregation plan | `absent` |
| Failed-item policy | `absent` |
| Controls | `structural_only` |
| Paired/unpaired separation | `structural_only` |
| Source-reported label | `preserved` |

`satisfied_for_qualification=[]` and `real_measurements=null`. The synthetic
control is the only executable piece:

- A complete synthetic manifest shape passes structural validation with 10
  files checked, then is **not** admitted.
- One invalid case (missing consent field), one missing case (missing target
  file) and one nonfinite case (`NaN` sample rate) are invoked and rejected.
- 53 adverse cases are actually invoked: malformed schema/IDs, wrong geometry,
  duplicate/relative/missing paths, uppercase or mismatched hashes, nonfinite
  and boolean durations, unknown or duplicate accent entries, bad permission
  digests, missing consent/terms/cohort/scoring/approval files and more.
- Deterministic aggregation records one synthetic failure, zero measured
  entries, one item per L1 group, no pooling across evidence classes and a
  canonical digest.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `source_manifest_and_exact_identity`
2. `accent_group_manifest_and_l1_labels`
3. `target_reference_provenance_and_permission`
4. `speaker_consent_and_output_use`
5. `dataset_terms_and_redistribution`
6. `rights_cleared_cohort_and_split`
7. `evidence_separation_scoring_and_controls`
8. `opt_in_adapter_and_release`

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`,
  `adapter_code_added=false`, `manifests_fabricated=false`,
  `consent_claimed=false`, `rights_approved=false`,
  `audio_copied_into_package=false`, `network_used=false`.
- `real_audio_decoded=false`, `real_audio_copied=false`,
  `real_corpus_ingested=false`, `real_corpus_scored=false`,
  `model_executed=false`, `runtime_invoked=false`, `weights_loaded=false`.
- Only SHA-256 observation of the five present clip files occurs; no audio
  content is interpreted.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter, processor exposure or release decision is made.

## Source-reported context

The pinned notes report LJ Speech 1.1 as public domain, the RT-VC p360 target
as unconfirmed provenance, the three accent clips as TokAN demo samples using
L2-ARCTIC speakers with CC BY-NC 4.0 corpus terms, no visible TokAN licence,
and an accent classifier that is only a proxy. All of that is
`source_reported_not_measured_here`; no local run result is reproduced or
promoted.

## Files

- `reference.py` — stdlib-only workspace audit, caller manifest contract,
  synthetic manifest/aggregation control and report model.
- `run.py` — regenerates `report.json`, its SHA-256 sidecar and
  `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `test_reference.py` — Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three cold regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

Canonical report SHA-256:
`84079002f61410bb22c1086d8bbcc813ad08a38d995b3aa3ec4fba0694519a64`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-LJ-SPEECH-AND-CONSENTED-ACCENT-EVALUATION-MANIFESTS
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Any appearance of a manifest,
consent, terms, cohort, scoring, approval record, extra accent clip or changed
present clip makes `verify.py` fail closed so the blocker must be re-evaluated
rather than silently promoted.

## Non-claims

No real manifest, consent record, rights grant, cohort, transcript set, accent
ground truth, scorer, converted audio, listening result, latency, memory, RTF,
device timing, public benchmark or release result is claimed. Five local clips
are observed by digest only. Missing evidence never qualifies this task; the
decision remains `DEFER`.
