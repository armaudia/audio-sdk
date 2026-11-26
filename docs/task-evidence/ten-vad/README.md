<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX License Identifier: Apache-2.0 -->
# SDK-TEN-VAD — task-local Analysis-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`TEN VAD` (`component_id=ten-vad`). Acceptance profile: **Analysis**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package records the exact blocker state from merged evidence: TEN VAD is
grouped in the unavailable/blocked VAD row with no exact source checkout,
weights, runtime, rights record, held-out cohort or approved parity vector
staged in checked local stores/environments. The package therefore contains a
**stdlib-only deterministic synthetic control** and a **caller-supplied asset
manifest validator**. It does not import vendor code, does not load or execute a
model, does not read or write real audio, does not download, does not use a
device clock, does not listen, does not benchmark and makes no release claim.
Only this task-local directory is added.

Pinned base: `26bc48c58f9d69571571fa651862dcbe0fe1172d`.
Branch: `swarm/SDK-TEN-VAD`.
Linked-row stable SHA-256: 1d937742e1a7a2d7424a10b049eabaf2afbb6b385c008ea6393cc70477.

## Exact blockers

1. **Exact source absent.** No exact TEN VAD source checkout, immutable revision,
   build recipe or artifact manifest is staged.
2. **Exact assets absent.** No exact licensed TEN VAD weights/checkpoint/asset
   with SHA-256 and byte count is present.
3. **Exact runtime absent.** No isolated hash-pinned runtime, lock file or
   execution recipe is present.
4. **Artifact rights uncleared.** No per-asset rights/provenance/redistribution
   record is present.
5. **Approved reference parity absent.** No approved exact-runtime probability or
   interval vector on frozen PCM exists.
6. **Real analysis cohort absent.** No rights-cleared held-out cohort with
   quiet/active/idle strata and onset/offset labels exists.
7. **Opt-in intake incomplete.** No adapter, descriptor, registry, default or
   public-surface decision is made.
8. **Public default/release blocked.** No default selection, resource/deadline,
   release or public-benchmark approval exists.

## Asset audit (fixed paths, no network)

The audit checks fixed workspace paths only. It reports `absent` for exact TEN
VAD source/assets/runtime/rights/held-out artifacts. Any appearance of required
assets must fail closed in verification and trigger blocker re-evaluation.

## Reference protocol and Analysis-profile controls

`reference.py` implements a deterministic synthetic control at the model
boundary:

- 16 kHz mono synthetic signal, 12,325 samples: 24 full 512-sample frames plus a
  37-sample final partial frame, zero-padded to 512 for model input.
- 64-sample carried context, 576-sample model input, recurrent state shape
  `[2,1,128]`, threshold `0.5`, and exact half-open source intervals.
- The probability trace is a **caller-supplied synthetic control**, explicitly
  labelled `caller_supplied_synthetic_control_trace_not_model_output`. It is not
  TEN VAD output.
- Speech events, unknown intervals, stratified FN/FP, onset/offset delay and the
  160-sample SDK to 512-sample model hop are computed structurally.
- Known zero is nonspeech; `NaN`, infinity, out-of-range, boolean and string
  probabilities are rejected; `unknown` is admitted but never counted as
  nonspeech.
- 18 adverse controls are actually invoked and all fail closed.
- No real-model metric, candidate metric, timing result or quality result exists.

Synthetic control totals are `TP=10, FN=7, FP=1, TN=6` with one unknown frame;
the strata are idle `FP=1/TN=6`, quiet `TP=5/FN=1`, active `TP=5/FN=1`, stress
`TP=0/FN=5`. These numbers only prove that the interval/scoring contract works;
they are not a VAD result and cannot qualify the candidate.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_source_and_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `analysis_cohort_and_scoring`
6. `streaming_boundary_and_state`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Boundary

- Public v0 geometry is preserved by contract fields: 16 kHz, mono, `f32`, 160
  samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; any opt-in SDK adapter remains blocked behind the gates.
- Caller-supplied asset validation requires absolute paths, SHA-256 matches, a
  full 40-hex source revision and the declared geometry. Validation never
  executes a model.

## Source-reported context

The merged candidate matrix row for
`Additional TEN VAD / PulseVAD / FSMN / MarbleNet / FireRedVAD / pyannote` is
`unavailable/blocked`: no exact candidate weights, source checkout, or adapter
are staged in checked local stores/environments. That row is copied as
`source_reported_not_measured_here`; it is not reproduced, re-scored or promoted.

## Files

- `reference.py` — stdlib-only asset audit, framing, probability control,
  scoring, caller manifest and report model.
- `run.py` — regenerates `report.json`, its SHA-256 sidecar and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `test_reference.py` — Python unittest acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three cold-start regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

## Reproduction

Use a pinned Python with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
PYTHONDONTWRITEBYTECODE=1 python3 run.py sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. Set
`SDK_ROOT` to the SDK checkout and `SOURCE_ROOT` to the common workspace root
when running outside the original worktree layout.

## Non-claims

No TEN VAD output, model execution, weight load, runtime call, network access,
real audio, corpus, annotation, accuracy, miss/FA rate, latency, memory, RTF,
device timing, listening, public benchmark or release result is claimed. Missing
evidence never qualifies this candidate.
