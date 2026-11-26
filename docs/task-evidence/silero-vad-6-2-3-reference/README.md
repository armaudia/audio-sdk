<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SILERO-VAD-6-2-3-REFERENCE — task-local Analysis-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Silero VAD 6.2.3 reference` (`component_id=silero-vad-6-2-3-reference`).
Acceptance profile: **Analysis**, assigned by `plan/INVENTORY.json` and defined
in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package records the exact upstream identity of Silero VAD 6.2.3 from the
merged research and evidence packages and audits the fixed workspace paths.
The official stateful ONNX graph is present only as an unqualified
`cpp-library/.deps` build dependency. The official sequence graph, the pinned
PyPI wheel, the isolated NumPy 2.2.6 / ONNX Runtime 1.24.1 runtime, the complete
source revision, the per-weight rights record, the real analysis cohort and an
approved exact-runtime parity vector are absent. The package therefore contains
a **stdlib-only deterministic asset/header verifier** and a **synthetic
probability-trace control**. It does not import NumPy or ONNX Runtime, does not
load or execute a model, does not read or write audio, does not download,
does not use a device clock, does not listen, does not benchmark and makes no
release claim. Only this task-local directory is added.

Pinned base: `d50bf1d324bf2a98607b56c2dccbc72d7f143932`.
Branch: `swarm/SDK-SILERO-VAD-6-2-3-REFERENCE`.

## Exact blockers

1. **Offline sequence graph absent.** The official
   `silero_vad_16k_sequence.onnx` (SHA-256
   `9ccdacc4719d8aa7e45a77536bfabec45a03ba1f2fad5e241ab4060b24238a85`) is not
   present anywhere in the workspace.
2. **Exact runtime absent.** The pinned isolated environment
   `data/envs/silero-vad-6.2.3` with NumPy `2.2.6`, ONNX Runtime `1.24.1` and
   lock SHA-256
   `3a4f56764ebde51fc1da3e1b82d715488f7649547bc1616fffd0f549d7424528`
   is absent. An unrelated validation venv contains ONNX Runtime `1.31.1` /
   NumPy `2.4.6`; the C dependency bundle contains ONNX Runtime `1.31.1`.
3. **Official wheel and lock absent.** The PyPI wheel
   `silero_vad-6.2.3-py3-none-any.whl` (SHA-256
   `7b7f5436cfcb02fae583a05b512ea96467fd449fe54cb49a5e4f06c51a1e43b8`),
   `requirements.lock` and `wheel-hashes.txt` are not present as
   caller-owned artifacts.
4. **Full source revision unpinned.** The merged evidence records only the
   short release-tag commit `5cd7945` for tag `v6.2.3`; no full 40-hex commit is
   recorded. A short prefix is not an exact source pin.
5. **Per-weight rights uncleared.** The PyPI package declares MIT, but no
   per-weight terms or training-data provenance statement exists. The
   repository model manifest sets `redistributed=false` and requires
   independent review.
6. **Stateful graph present but unqualified.** `cpp-library/.deps/silero_vad.onnx`
   matches the pinned SHA-256
   `1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3` and the
   expected ONNX interface, but it is an unversioned build dependency outside
   task custody, with no signed 6.2.3 identity, rights record or parity run.
7. **Real analysis cohort absent.** No rights-cleared held-out cohort with
   continuous speech/nonspeech truth, quiet/active/idle strata and onset/offset
   labels exists. `data/runs/vad-chaining-ami-20261031-01/heldout-results.json`
   is recorded as a missing historical artifact.
8. **Approved reference parity absent.** No approved exact-runtime Silero 6.2.3
   probability and interval vector, fresh-session trace or byte-level parity
   record is available.

## Asset audit (fixed paths, no network)

| Artifact | Required pin | Observation |
| --- | --- | --- |
| Stateful ONNX | `1a153a22…8788e3`, 2,327,524 bytes | **Present and header-matched** at `cpp-library/.deps/silero_vad.onnx`; unqualified |
| Sequence ONNX | `9ccdacc4…38a85` | **Absent** |
| PyPI wheel 6.2.3 | `7b7f5436…e43b8` | **Absent** |
| Runtime | NumPy 2.2.6 / ORT 1.24.1 | **Absent**; unrelated 1.31.1 / 2.4.6 only |
| Runtime lock | `3a4f5676…24528` | **Absent** |
| Source revision | tag `v6.2.3`, full commit | **Short `5cd7945` only** |
| Per-weight rights | MIT plus per-weight terms | **Absent** |
| Held-out results | `data/runs/vad-chaining-ami-20261031-01/heldout-results.json` | **Absent** |

The bounded ONNX reader validates only `ir_version=8`, default-domain opset 16,
inputs `input`/`state`/`sr`, outputs `output`/`stateN` and the declared element
types/ranks. It does not execute a node, load a tensor or establish model
identity beyond the SHA-256 pin.

## Reference protocol and Analysis-profile controls

`reference.py` implements a deterministic synthetic control at the model
boundary:

- 16 kHz mono synthetic signal, 12,325 samples: 24 full 512-sample frames plus a
  37-sample final partial frame, zero-padded to 512 for model input.
- 64-sample carried context, 576-sample model input, recurrent state shape
  `[2,1,128]`, threshold `0.5`, and exact half-open source intervals.
- The probability trace is a **caller-supplied synthetic control**, explicitly
  labelled `caller_supplied_synthetic_control_trace_not_model_output`. It is
  not Silero output.
- Speech events, unknown intervals, stratified FN/FP, onset/offset delay and the
  160-sample SDK to 512-sample model hop are computed structurally.
- Known zero is nonspeech; `NaN`, infinity, out-of-range, boolean and string
  probabilities are rejected; `unknown` is admitted but never counted as
  nonspeech.
- 19 adverse controls are actually invoked and all fail closed.
- No real-model metric, candidate metric, timing result or quality result exists.

Synthetic control totals are `TP=10, FN=7, FP=1, TN=6` with one unknown frame;
the strata are idle `FP=1/TN=6`, quiet `TP=5/FN=1`, active `TP=5/FN=1`, stress
`TP=0/FN=5`. These numbers only prove that the interval/scoring contract works;
they are not a VAD result and cannot qualify the candidate.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `analysis_cohort_and_scoring`
6. `streaming_offline_separation`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK adapter remains blocked behind the gates.
- The caller-supplied-asset manifest requires exact hashes, an absolute present
  runtime lock and rights record, a full `5cd7945…` revision, the 512/64
  geometry and ONNX Runtime 1.24.1. Validation never executes the model.

## Source-reported context

The merged candidate matrix reports held-out AMI `FN 19.43%`, `FP 8.20%` and
`68.35 µs` per 20 ms frame over three held-out meetings. That record is copied
as `source_reported_not_measured_here`; it is not reproduced, re-scored or
promoted.

## Files

- `reference.py` — stdlib-only ONNX header/asset audit, framing, probability
  control, scoring, caller manifest and report model.
- `run.py` — regenerates `report.json`, its SHA-256 sidecar and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `test_reference.py` — 52 Python unittest acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three cold regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

Canonical report SHA-256:
`dac376c116b9734a63a9ee9931ccd11223bbda998503e8ff7bd2a00d7491a319`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SILERO-VAD-6-2-3-REFERENCE
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Any appearance of a required asset
makes `verify.py` fail closed so the blocker must be re-evaluated rather than
silently promoted.

## Non-claims

No Silero output, model execution, weight load, wheel install, runtime call,
network access, real audio, corpus, annotation, accuracy, miss/FA rate, latency,
memory, RTF, device timing, listening, public benchmark or release result is
claimed. The stateful graph observation is a hash/header audit only. Missing
evidence never qualifies this candidate.
