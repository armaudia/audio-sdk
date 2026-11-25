<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-TRN-02 — pitch and limited prosody control evidence map

**Disposition: `DEFER` / `proposal_only_survey_incomplete` / `not_qualified`.**
This package is a bounded, deterministic **taxonomy and comparison map** for
inventory category `TRN-02` (Pitch and limited prosody control, legacy family
`F13`). It matches the catalogued classic and ML method families, the named
source leads (`S34`, `S35`) and historical or task-local executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-TRN-02`; independent reviewer not dispatched. Claim
base: audio-sdk `b4ccacaff0e82dbfc027404fbb7ac81d4885f768`; branch
`swarm/SDK-SURVEY-TRN-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`. This map is deliberately
`proposal_only_survey_incomplete`; it is not a benchmark, provider intake or
release candidate.

## What this map covers and what it refuses to claim

The catalogued boundary is explicit: **pitch shift, formant preservation and
full prosody editing differ**, and **emotion manipulation is not added to
scope**. A rate engine's F0-distribution shift is not a designated pitch
control. The map therefore covers:

- classic pitch-synchronous overlap-add (PSOLA/TD-PSOLA) and a pitch-synchronous
  OLA reference (`S34` is the separate source-filter lead);
- classic source-filter/vocoder processing and analysis/resynthesis pitch
  engines (WORLD lead, phase vocoder, formant-preserving stretcher, platform
  rate/pitch unit);
- limited F0-contour prosody control, with emotion/expressive prosody excluded;
  and
- disentangled neural analysis/resynthesis (`S35`), with two neural vocoder
  decoder leads kept adjacent rather than promoted.

It does **not** pool time-scale modification (`TRN-01`), accent conversion
(`TRN-03`), voice conversion or cloning, emotion manipulation, listening quality
(`OBS-01`) or speech enhancement (`CLN-01`) into a `TRN-02` result. Those rows
are recorded in `excluded_boundaries`.

The key evidence distinction is carried through every row:

- historical rate-change F0 numbers are `source_reported_not_reproduced`;
- task-local synthetic pitch proxies are `task_local_synthetic_reference_only`;
- neither class is promoted, compared or treated as a designated pitch-shift,
  formant-preservation or prosody-editing result.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `provider_registration=false`, `processor_exposure=false`,
  `descriptor_registry_changed=false`, `public_api_abi_changed=false`,
  `installed_v0_changed=false`, `shared_cmakelists_changed=false`,
  `ci_changed=false`, `board_changed=false`, `handoff_changed=false`,
  `provider_intake_complete=false`, `release_approval=false`.
- Fixed installed v0 geometry is unchanged: 16 kHz, mono, float32, 160 samples
  per frame. No SDK callback is invoked. No source, build file, registry,
  default, CI file, board record or handoff outside this directory is changed.
- No real corpus, weights, runtime, audio, device timing, listening test,
  public benchmark or release claim is present. Source URLs are pinned text
  only and are never fetched. Historical numbers stay
  `source_reported_not_reproduced`; task-local numbers stay
  `task_local_synthetic_reference_only`.

## What is mapped

- **Category cross-check:** the `TRN-02` fields in `plan/INVENTORY.json` and
  `research/category_registry.json` are compared field-by-field and must be
  identical before a report is built. The inventory task is
  `SDK-SURVEY-TRN-02`, the legacy family is `F13`, and the backlog state is
  `catalogued`.
- **Classic family `MF-C1` (pitch-synchronous OLA):** `psola-praat`,
  `td-psola` and `sonic`. PSOLA/Praat and Sonic hold task-local rate fixtures
  with a pitch frequency proxy; TD-PSOLA is considered only.
- **Classic family `MF-C2` (source-filter/vocoder and analysis/resynthesis):**
  `world-vocoder`, `phase-vocoder-baseline`, `rubber-band-r3-offline`,
  `rubber-band-r3-streaming` and
  `avaudiounittimepitch-rate-pitch-overlap`. WORLD is a documentation lead;
  the phase-vocoder and Rubber Band packages are rate-change references; the
  platform unit is source-unavailable.
- **Classic family `MF-C3` (limited prosody):** `f0-contour-smoothing`, which
  is blocked because no exact smoother, desired contour or voicing reference
  exists. Emotion/expressive prosody is mapped as excluded, not as a candidate.
- **ML family `MF-M1` (disentangled neural analysis/resynthesis):**
  `nansy-analysis-resynthesis` (`S35`) plus the `hifi-gan-vocoder` and
  `vocos-vocoder` decoder leads. No checkpoint, configuration, weight, runtime
  or target reference is staged.
- **Source leads:** `S34` (WORLD vocoder implementation) and `S35` (NANSY
  analysis and resynthesis paper) are pinned text-only leads with URLs never
  fetched.
- **Gaps:** every gap links only to an existing board task id. Twelve gaps cover
  WORLD intake, TD-PSOLA designated pitch shift, platform unit pinning, formant
  separation, bounded prosody control, the emotion/accent boundary, NANSY
  intake, neural decoder intake, independent listening, target-device timing,
  replacing rate-change F0 proxies, and rights-cleared/consent-cleared assets.

## Comparison inputs, controls, assets and outcomes

`report.json` records the acceptance inputs explicitly:

- **Comparison inputs:** `CI-1` is the historical ten-window AMI rate screen
  with median F0-distribution shift; `CI-2` through `CI-7` are task-local
  synthetic pitch proxies (PSOLA, Sonic, Rubber Band offline, Rubber Band
  streaming, SoundTouch, phase vocoder); `CI-8` and `CI-9` are text-only
  source leads and prosody audit rows; `CI-10` is the platform caveat; `CI-11`
  is the missing rights-cleared cohort.
- **Controls:** `CT-1` identity/1x pitch and duration, `CT-2` the varispeed
  adverse control that must shift pitch, `CT-3` the autocorrelation/Goertzel
  F0 proxy (octave-equivariant, not perceptual pitch), `CT-4` the fixed
  synthetic formant-style probe (not formant gold), `CT-5` the exact
  source/output sample map, and `CT-6` blocked rows without substitution.
- **Assets:** `AS-1` historical AMI windows (bytes absent, rights uncleared),
  `AS-2` through `AS-7` generated synthetic fixtures, `AS-8` absent WORLD/NANSY
  source and weights, and `AS-9` the missing rights-cleared designated
  pitch/formant/prosody cohort.
- **Local versus reported outcomes:** `historical_executions` are
  `source_reported_not_reproduced`; `local_evidence` is
  `task_local_synthetic_reference_only`. The ledger never promotes either
  class, and `cross_comparison.performed=false` because no matched asset,
  ratio, formant target, runtime or listening protocol is shared.
- **Release boundary:** `release_allowed=false` in practice because every gate
  is blocked. Pitch shift, formant preservation, prosody editing, emotion
  manipulation, perceptual pitch, naturalness, listening, device timing,
  public benchmark and release claims all remain gated or excluded.

## Eight blocked release gates

| Gate | Status | Requirement |
| --- | --- | --- |
| `RG-01` | blocked | Rights-cleared, consent-covered speech corpus with designated pitch, formant and limited-prosody targets and exact labels |
| `RG-02` | blocked | Independent blind listening for pitch shift, formant preservation and prosody naturalness |
| `RG-03` | blocked | Task-matched pitch/formant accuracy protocol with voiced/unvoiced, nonfinite and missing-value handling |
| `RG-04` | blocked | Pinned PSOLA, WORLD, NANSY and neural-vocoder runtimes with exact revisions and per-weight licence terms |
| `RG-05` | blocked | Target-device real-time timing, buffering, content delay and resource evidence |
| `RG-06` | blocked | Formant-preservation and full-prosody separation with identity and content preservation |
| `RG-07` | blocked | Opt-in provider intake and independent exact-head review |
| `RG-08` | blocked | Explicit public default selection and release approval; `DEFER` remains until every gate closes |

Missing evidence never qualifies a candidate: the outcome stays
`proposal_only_survey_incomplete` / `not_qualified` / `DEFER`.

## Pinned inputs

Paths beginning `source:` are relative to the workspace root (the enclosing
`audioml` checkout, overridable with `AUDIOML_WORKSPACE_ROOT`). Paths beginning
`worktree:` are relative to the SDK worktree root.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Category, component census and task identity. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice acceptance profile. |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Published `TRN-02` row and distinctions. |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Platform rate/pitch unit caveat. |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | Original families and `S34`/`S35` leads. |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` | `S34`/`S35` source rows. |
| `source:research/task_backlog.json` | `0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc` | Legacy family `F13` state. |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Historical rate-change F0-distribution shifts. |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` | Prosody/emotion audit and no-substitution rule. |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | FFmpeg atempo F0 control and blocked prosody rows. |
| `worktree:docs/task-evidence/psola-praat/README.md` | `7e64ec614937533168ef31c34d4c8ec4aa7d6d52670e663f0f88ce5f4ec7a6ef` | Pitch-synchronous OLA synthetic rate reference. |
| `worktree:docs/task-evidence/sonic/README.md` | `40f2fdcf708a75fbc3e0df296fabfecd296118e6a9eaee67fc34f8dec0e419cb` | Pitch-synchronous OLA synthetic rate reference. |
| `worktree:docs/task-evidence/rubber-band-r3-offline/README.md` | `de528246089b9f0d2a1ea597ac0cbbb119d5541b2b22a0a383b4d03b7a85aeab` | Offline formant/pitch proxy reference. |
| `worktree:docs/task-evidence/rubber-band-r3-streaming/README.md` | `04583e07678079f1ed179a1b15f50599693a7bc6f6a813237a71d0005d810d97` | Streaming dynamic-rate pitch proxy. |
| `worktree:docs/task-evidence/soundtouch/README.md` | `951726880bc657fa59f0ba3d2508887401f1b07942faf8ee87faa8c58f02c550` | WSOLA rate/varispeed pitch proxy. |
| `worktree:docs/task-evidence/phase-vocoder-baseline/README.md` | `915bd51e7de4b223bdd61bb5ff823e7a0558f03e324f154d7d3d4c77d14f9790` | Pitch-preservation and transient-smear proxy. |
| `worktree:docs/task-evidence/survey-trn-01/README.md` | `20503c685e57ba2b6d15a677cfad1ea7e6f22b391010af61bb4fd6dc63ea8972` | Rate category boundary and adjacent evidence map. |
| `worktree:CONTRACTS.md`, `REUSE.toml`, `api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h` | see `SOURCES.sha256` | Unchanged SDK boundary and licensing coverage. |

`SOURCES.sha256` enumerates every source, worktree and task-local artifact pin.
`verify.py` fails closed on a missing, stale, duplicated or malformed pin,
non-canonical JSON, duplicate/nonfinite JSON keys, a stale digest sidecar, an
unlinked gap, a promoted pitch/formant/prosody/listening claim, an out-of-scope
worktree change or a licensing gap.

## Files

- `contract.json` — task-local map manifest, scope, boundary, linked task ids and gates.
- `reference.py` — stdlib-only deterministic map builder and read-only validators.
- `run.py` — byte-identical regeneration of report, digest, contract and source manifest.
- `report.json` / `report.json.sha256` — canonical map and its SHA-256.
- `SOURCES.sha256` — SHA-256 manifest for all pinned inputs and task files.
- `verify.py` — read-only strict verifier.
- `test_reference.py` — Python unittest acceptance suite.
- `*.json.license`, `SOURCES.sha256.license` — REUSE sidecars for generated artifacts.

`report.json` gates only the **stable identity** of linked board rows — exact
`id`, `title` and `mode` — through `board_link_projection_sha256`. Mutable board
status and owner fields are deliberately excluded, so concurrent board writes do
not change canonical bytes.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
```

`run.py report`, `run.py sources`, `run.py contract` and `run.py all` are
idempotent. The canonical report digest is the content of `report.json.sha256`;
the manifest digest is the SHA-256 of `SOURCES.sha256` itself. Three fresh
interpreter processes producing identical canonical core bytes are checked by
`run.py check` and again by `verify.py`.

## Disposition

The map is complete only as a survey of text and task-local synthetic evidence.
It does not close any component task, qualify a candidate, register a provider,
change a default, manipulate emotion or support a release. Missing evidence
never qualifies a candidate: the outcome is `DEFER` /
`proposal_only_survey_incomplete` / `not_qualified`.
