<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-F0-CONTOUR-SMOOTHING — task-local Voice-profile blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory is bounded, deterministic, task-local evidence for the board row
`F0 contour smoothing` (`component_id=f0-contour-smoothing`, mode
`feasibility`). It is **not** an F0-contour smoother, pitch tracker, conversion
adapter, provider or result. No candidate source, checkpoint, parameter set,
desired target contour, voicing policy, pitch reference pair, runtime, cohort,
pitch track, transformed waveform, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies the
candidate.**

The acceptance profile is **Voice**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. The decision is **DEFER** before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`.

Pinned base: `23526250a3a0a66c1f93089ff6fb697b5e776965`.
Branch: `swarm/SDK-F0-CONTOUR-SMOOTHING`.

## Exact blocker: the candidate is not even identified

Candidate matrix record 56 is `unavailable/blocked`: *"No exact smoother or
desired contour/voicing reference is specified; no task accuracy can be
calculated."* The row names no smoother, repository, revision, checkpoint,
parameter set, target contour, voicing rule, pitch reference or metric, so no
candidate identity can be pinned. Nothing was fabricated, reconstructed,
downloaded or substituted.

This is a stronger blocker than a missing weight file: an F0-contour smoother
is an algorithm family, and the merged research notes explicitly record that
the method is underspecified. Without an exact smoother and an exact desired
result, any local implementation would be a new invention, not a reproduction
of a candidate.

| Item | Status |
| --- | --- |
| Named smoother / implementation | **Absent**; the record names no algorithm or repository |
| Full 40-hex source revision | **Absent**; none is recorded, so none is invented |
| Exact parameter set | **Absent**; no window, order, cutoff or smoothing bound is specified |
| Desired target contour | **Absent**; no target F0 contour, units, time base or tolerance |
| Voicing / unvoiced policy | **Absent**; no voiced/unvoiced rule or boundary handling |
| Source/target pitch reference pairs | **Absent**; no rights-cleared pitch tracks or audio pairs |
| Metric and tolerance specification | **Absent**; no pitch/voicing/content/naturalness metric or margin |
| Runtime and package lock | **Absent**; no environment exists at `data/envs/f0-contour-smoothing` |
| Rights, consent and output use | **Unresolved**; code, weight, corpus, reference-voice and derivative-output terms are not staged |
| Frozen voice cohort | **Absent** |
| Approved parity vector | **Absent** |
| Candidate pitch track, smoothed contour or output | **Absent**; no candidate execution, score, timing or listening |

The machine-readable record is `report.json` -> `candidate`, `asset_audit`,
`absence_probes`, `asset_requirements`, `caller_asset_contract`,
`smoother_specification_gate`, `voice_profile`, `reference_protocol`,
`controls`, `gates`, `exact_blockers`, `source_reported_context` and
`missing_historical_artifacts`. `contract.json` carries the same disposition,
pins, geometry, invariants, blockers and all eight blocked release gates.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-F0-CONTOUR-SMOOTHING`, `23526250a3a0a66c1f93089ff6fb697b5e776965` |
| Task mode | `feasibility` |
| Acceptance profile | `voice` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Declared control geometry | 16 kHz mono `float32`, 160-sample frame — **control only, not candidate geometry** |
| Candidate geometry | `unestablished`; no rate, frame, pitch range or contour taxonomy is asserted |
| Asset boundary | caller-supplied `external` only; no bytes read, no download |
| Provider registration, default, ABI, CI | none |

- Work is confined to `docs/task-evidence/f0-contour-smoothing/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI and other worktrees are untouched.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `mode`, `repository`, `component`). Mutable status, owner, review, handoff,
  priority, claim and history never enter canonical bytes and are never a gate.
  The mutable full `plan/swarm/TASKS.json` is **not hashed** into any artifact.
- No request is ever processed as F0-contour smoothing. Valid non-identity
  targets fail closed because the candidate smoother and the target contour are
  absent.
- Merged sibling packages (`psola-praat`, `pitch-period-repeat-plc`,
  `emotion-expressive-prosody-transformation`, `sylnet`) are cited only as
  separate rows. None is a named F0-contour smoother, none supplies a desired
  contour, and none is substituted.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a smoother or a
pitch tracker:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF and no
   floats.
2. **Fixed-path source/asset audit.** It checks a bounded list of candidate
   source, weight, configuration, target-contour, voicing, pitch-reference,
   metric, rights, runtime, cohort and parity paths without a recursive
   workspace walk. Every probe is currently absent; any later presence makes
   `reference.build_report()` and `verify.py` fail closed.
3. **Caller-supplied-asset manifest contract.** It validates exact fields,
   absolute paths, file/directory existence, SHA-256 values, a full 40-hex
   revision, mono duration-preserving geometry, an exact smoother id, task
   kind, baseline and offline variant. It hashes the caller's files but never
   imports or executes the caller's source and never loads a checkpoint.
4. **Smoother-specification admission.** A complete specification needs an
   exact non-placeholder smoother id, algorithm family, non-empty integer/token
   parameters, a defined target contour, a defined voicing policy, a named
   pitch extractor and non-empty unique metric ids. Placeholders such as
   `unspecified`, `default`, `tbd` or `none` are rejected. This is a local
   intake gate only and cannot supply the absent implementation or evidence.
5. **Request admission.** It accepts only the declared `identity_prosody`
   comparison baseline at the control geometry. `contour_smoothing` is rejected
   with `absent_candidate_smoother`; `fixed_contour_target` is rejected with
   `absent_exact_target_contour`. Other targets and baselines fail closed.
6. **Synthetic identity-prosody control.** It generates 2.0 s of deterministic
   integer-derived 16 kHz mono PCM (silence, two voiced periods, unvoiced noise,
   silence), applies only the identity baseline, and checks exact sample count,
   duration, digest, peak bound, segment boundaries and offline-only alignment.
   It is labelled
   `caller_supplied_synthetic_identity_prosody_acceptance_control_not_smoother_output`
   with `qualification_effect=none`.
7. **Adverse rejection.** 59 malformed, missing, invalid, nonfinite,
   wrong-domain, placeholder and non-identity controls are actually invoked;
   all fail closed.
8. **Stable board identity** from the linked row's five stable fields.
9. **Canonical report, contract and source-manifest bytes.**

It does **not** extract pitch, smooth a contour, synthesize or modify audio,
score a candidate, run listening or produce any audio.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With the candidate
absent, the profile maps as follows (`report.json` -> `voice_profile`; each row
is also verified):

| Required element | Local status |
| --- | --- |
| Permitted input and target references | `absent` — no permitted source/target pitch pair |
| Task, language, speaker and prosody groups | `absent` — no cohort |
| Text and semantic content preserved | `not_measured` — no candidate output |
| Identity/similarity separate | `not_measured` — no similarity result |
| Target contour and voicing realization separate | `not_measured` — no contour definition or scorer |
| Naturalness separate | `not_measured` — no listening or MOS |
| Alignment, first-output/tail timing, exact target condition | `structural_only` — offline accounting only |
| Consent, reference availability, output use | `absent` — rights unresolved |

`satisfied_for_qualification=[]` and `real_model_metrics=null`. No sibling pitch,
prosody, rate or voice value is copied into this report as a candidate metric.

## Pins

Paths outside `docs/task-evidence/f0-contour-smoothing/` are relative to the
`audioml` workspace root; SDK boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Record 56 status, baseline and finding |
| `source:research/voice-enhancement-20261101/agent-transform-spatial-trials/REPORT.md` | `fa8033889de77bf0fa2dfd57f5df97fc96e149a6027febe3303b50ab1d70de5b` | Underspecified-method finding |
| `source:research/voice-enhancement-20261101/agent-transform-space/REPORT.md` | `479188be1a9c3cbc6d9a057f6e985e7ed03e454033cb3e8cab2f273da22abcd4` | Required pitch/voicing/contour definition |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row and Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Caller-supplied-asset / opt-in sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice acceptance profile |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |

`SOURCES.sha256` additionally pins every task-local artifact and the unchanged
`CMakeLists.txt`, `REUSE.toml` and `scripts/ci.py`; it excludes itself because a
file cannot pin its own bytes. `contract.json` is excluded from its own
`artifact_pins` but is pinned by `SOURCES.sha256`. `verify.py` fails closed on a
missing, stale, malformed, duplicated or extra pin and on any worktree change
outside this directory. The current canonical report digest is recorded in
`report.json.sha256`.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission, specification gate, identity control and canonical
  report builder.
- `run.py`: regenerates report, sidecar, manifest and contract three times and
  fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, scope and three-cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/f0-contour-smoothing
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates the canonical report, sidecar, contract and source manifest
three times in one process and refuses to write unless all rounds are
byte-identical. `verify.py` never writes to this directory: it regenerates in
memory, then builds three isolated scratch copies and checks cold-start byte
identity there. Expected: all tests pass and `verify.py` prints
`PASS pins=… gates=8 blockers=8 cold_starts=3/3 … decision=DEFER`.

When the package is copied out of the worktree, set `SDK_ROOT` to the SDK
checkout and `SOURCE_ROOT` to the common workspace root. Any appearance of a
required asset or licence makes `verify.py` fail closed so the blocker must be
re-evaluated rather than silently promoted.

## Eight blocked release gates

1. `exact_smoother_identity_and_source` — no named smoother, revision, tree
   digest or license text.
2. `exact_smoother_parameters_and_target_contour` — no pinned parameters,
   target contour, voicing policy or pitch reference pairs.
3. `runtime_admission_and_package_lock` — no isolated hash-pinned runtime.
4. `artifact_rights_and_corpus_licensing` — no rights, consent or output-use
   decision.
5. `frozen_task_matched_pitch_cohort` — no rights-cleared
   language/speaker-stratified cohort.
6. `pitch_voicing_content_and_naturalness_results` — no candidate metric,
   content, identity or naturalness result.
7. `alignment_timing_and_streaming` — no exact-runtime delay, first-output,
   tail, memory, CPU/RTF or paced streaming measurement.
8. `opt_in_adapter_intake_and_release` — no adapter, public-surface decision,
   authorized listening, benchmark validation, independent exact-head review or
   release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`report.json` -> `reopen_conditions`.

## Non-claims

No F0-contour smoother, pitch tracker, parameter set, target contour, voicing
policy, checkpoint, runtime, cohort, pitch track, transformed audio, content
preservation, identity similarity, target-contour accuracy, voicing accuracy,
naturalness, latency, memory, RTF, device timing, callback, benchmark or release
result is claimed. The synthetic identity control is not candidate output and
cannot qualify the candidate. No installed v0, public API, C ABI, descriptor,
registry, default, shared build, CI, board or handoff change is made. Missing
evidence never qualifies this row; the decision remains **DEFER**.
