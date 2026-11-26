<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION — task-local Voice-profile blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`.** This directory is bounded, deterministic,
task-local evidence for the board row `Emotion / expressive prosody
transformation` (`component_id=emotion-expressive-prosody-transformation`, mode
`feasibility`). It is **not** an emotion/prosody model, conversion adapter,
provider or result. No input-speech conversion checkpoint, target-emotion label
set, style conditioning asset, consent-cleared target voice, runtime, converted
output, listening result, device measurement, benchmark or release claim is
included. **No result here qualifies the candidate.**

The acceptance profile is **Voice**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. The decision is **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`.

Pinned base: `b43a7e13175949cda78f0ea64953e4a585d43c67`.
Branch: `swarm/SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION`.

## Exact blocker: no candidate artifact exists

Candidate matrix record 57 is `unavailable/blocked`: *"No input-speech
conversion model, target emotion labels or consent-cleared target voices are
staged."* The record names no model, repository, revision, checkpoint, label
set or runtime, so no candidate identity can be pinned. Nothing was fabricated,
reconstructed or downloaded.

| Item | Status |
| --- | --- |
| Input-speech transformation source | **Absent**; the record names no model or repository |
| Full 40-hex source revision | **Absent**; none is recorded, so none is invented |
| Inference checkpoint / model config | **Absent**; no filename, byte count or SHA-256 is known |
| Target emotion/style label set and intensity scale | **Absent**; the record states no target emotion labels are staged |
| Style conditioning asset / embedding table | **Absent** |
| Consent-cleared target/reference voices | **Absent**; the record states no consent-cleared target voices are staged |
| Runtime and package lock | **Absent**; no environment exists at `data/envs/emotion-expressive-prosody-transformation` |
| Rights, consent and output use | **Unresolved**; code, weight, training-data, corpus, target-voice, derivative-output and redistribution terms are not staged |
| Frozen voice cohort | **Absent** |
| Approved parity vector | **Absent** |
| Converted output, scores, timing | **Absent**; no audio, content/identity/emotion result, listening, alignment, first-output/tail, memory or streaming measurement |

The machine-readable record is `report.json` → `candidate`, `asset_audit`,
`absence_probes`, `asset_requirements`, `caller_asset_contract`,
`voice_profile`, `reference_protocol`, `controls`, `gates`, `exact_blockers`,
`source_reported_context` and `missing_historical_artifacts`. `contract.json`
carries the same disposition, pins, geometry, invariants, blockers and all eight
blocked release gates.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-EMOTION-EXPRESSIVE-PROSODY-TRANSFORMATION`, `b43a7e13175949cda78f0ea64953e4a585d43c67` |
| Task mode | `feasibility` |
| Acceptance profile | `voice` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Declared control geometry | 16 kHz mono `float32`, 160-sample frame — **control only, not candidate geometry** |
| Candidate geometry | `unestablished`; no rate, frame, label taxonomy, intensity scale or output geometry is asserted |
| Asset boundary | caller-supplied `external` only; no bytes read, no download |
| Provider registration, default, ABI, CI | none |

- Work is confined to `docs/task-evidence/emotion-expressive-prosody-transformation/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, board/handoff files, CI and other worktrees are
  untouched.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`,
  `evidence`, `write_scope`). Mutable status, owner, review, handoff, priority,
  claim and history never enter canonical bytes and are never a gate. The
  mutable full `plan/swarm/TASKS.json` is **not hashed** into any canonical
  artifact.
- No request is ever processed as an emotion/prosody transformation. Valid
  non-identity targets fail closed because the candidate artifact and runtime
  are absent.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a conversion
engine:

1. **Strict JSON** with duplicate-key, NaN, Infinity, BOM and root-type
   rejection; canonical compact sorted-key bytes with one trailing LF and no
   floats.
2. **Fixed-path source/asset audit.** It checks a bounded list of candidate
   source, weight, label, consent, runtime, rights, cohort and parity paths
   without a recursive workspace walk. Every probe is currently absent; any
   later presence makes `reference.build_report()` and `verify.py` fail closed.
3. **Caller-supplied-asset manifest contract.** It validates exact fields,
   absolute paths, file/directory existence, SHA-256 values, a full 40-hex
   revision, mono geometry, admitted rates, task kind, baseline, offline
   variant, an emotion label and a bounded integer intensity. It hashes the
   caller's files but never imports or executes the caller's source and never
   loads a checkpoint.
4. **Target-condition admission.** It accepts only the declared
   `identity_prosody` comparison baseline at full intensity. Any non-identity
   emotion label, reduced intensity, TTS task kind, voice-conversion task kind,
   streaming variant or wrong baseline is rejected with
   `absent_candidate_transform` because the candidate transform is absent.
5. **Synthetic identity-prosody control.** It generates 2.0 s of deterministic
   integer-derived 16 kHz mono PCM, applies only the identity baseline, and
   checks exact sample count, exact duration, digest equality, peak bound and
   offline-only alignment. It is labelled
   `caller_supplied_synthetic_identity_prosody_acceptance_plan_not_model_output`
   and has `qualification_effect=none`.
6. **Adverse rejection.** 45 malformed, missing, invalid, nonfinite,
   wrong-domain and non-identity controls are actually invoked; all fail closed.
7. **Stable board identity** from the linked row and its three dependencies.
8. **Canonical report, contract and source-manifest bytes.**

It does **not** load a model bundle, create a model or runtime session,
transform prosody, synthesize audio, score emotion, run listening or produce any
audio.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the Voice profile. With the candidate
artifact, labels, consent, runtime and cohort absent, the profile maps as
follows (`report.json` → `voice_profile`; each row is also verified):

| Required element | Local status |
| --- | --- |
| Permitted input and target references | `absent` — no permitted source/target pair |
| Task, language, speaker and emotion groups | `absent` — no cohort |
| Text and semantic content preserved | `not_measured` — no candidate output |
| Identity/similarity separate | `not_measured` — no similarity result |
| Target emotion realization separate | `not_measured` — no label set or scorer |
| Naturalness separate | `not_measured` — no listening or MOS |
| Alignment, first-output/tail timing, exact target condition | `structural_only` — offline accounting only |
| Consent, reference availability, output use | `absent` — rights unresolved |

`satisfied_for_qualification=[]` and `real_model_metrics=null`. No sibling
accent, voice-conversion or TTS value is copied into this report as a candidate
metric.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `exact_source_and_artifact_identity` | No model, revision, checkpoint, config, label set or style asset exists. |
| `runtime_admission` | No isolated environment, lock or environment digest exists. |
| `artifact_rights_consent_and_output_use` | Model, training-data, corpus, target-voice, derivative-output and redistribution terms are unresolved. |
| `exact_reference_parity` | No approved candidate output or identity-baseline parity vector exists. |
| `frozen_voice_cohort` | No label-complete, rights-cleared, task-matched cohort exists. |
| `content_identity_emotion_naturalness_results` | No independent content, identity, target-emotion or naturalness result exists. |
| `alignment_timing_and_streaming` | No exact-runtime alignment, first-output/tail, memory, streaming or device measurement exists. |
| `opt_in_adapter_intake_and_release` | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory, with the pinned interpreter and no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

`run.py` regenerates the canonical report, sidecar, contract and source
manifest three times in one process and refuses to write unless all rounds are
byte-identical. `verify.py` additionally runs three cold-start regenerations in
fresh scratch copies, checks strict JSON, exact pins, stable board identity,
licensing, task-local git scope and blocker semantics. Expected: all tests pass
and `verify.py` prints
`PASS pins=… gates=8 blockers=8 cold_starts=3/3 … decision=DEFER`.

When the package is copied out of the worktree, set `SDK_ROOT` to the SDK
checkout and `SOURCE_ROOT` to the common workspace root. Any appearance of a
required asset or licence makes `verify.py` fail closed so the blocker must be
re-evaluated rather than silently promoted.

## Files

- `reference.py` — stdlib-only absence/asset audit, caller manifest contract,
  fail-closed target admission, synthetic identity control and report model.
- `run.py` — 3× byte-identical regeneration of `report.json`, its SHA-256
  sidecar, `contract.json` and `SOURCES.sha256`; `--check` is read-only.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, pins, invariants, blockers
  and eight gates.
- `test_reference.py` — deterministic Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/control/licensing/
  reproduction/scope verifier, including three cold regenerations.
- `LICENSES.md` — licensing and provenance statement.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

## Non-claims

No input-speech emotion/prosody model, checkpoint, config, target-emotion label
set, style embedding, target voice, consent record, runtime, converted audio,
content preservation, identity similarity, emotion accuracy, naturalness,
latency, memory, RTF, device timing, callback, benchmark or release result is
claimed. The synthetic identity control is not candidate output and cannot
qualify the candidate. No installed v0, public API, C ABI, descriptor, registry,
default, shared build, CI, board or handoff change is made. Missing evidence
never qualifies this row; the decision remains **DEFER**.
