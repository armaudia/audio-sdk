<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER — task-local synthetic evidence

Proposal-only, incomplete and **not qualified** evidence for
`FastEnhancer source-linked ONNX wrapper` (`reference_family=fastenhancer`,
`component_id=fastenhancer-source-linked-onnx-wrapper`). Decision: **DEFER**,
before `processor_exposure`. `status=proposal_only_synthetic_incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a candidate.

This package is a deterministic Python reference over frozen synthetic signals
at a documented, optional adapter boundary linked to one pinned source
identity. It is **opt-in, unregistered and OFF by default**. It does not change
the public API/ABI, installed v0 behavior, descriptor settings, provider
registry, defaults, shared build, CI, board or handoffs. No real audio, model
download, vendor runtime invocation, device timing, listening result, benchmark
or release claim is made. The evaluation fixture and any future production
callback are distinct paths; no production callback is implemented.

## Pinned source-linked boundary

The boundary anchor is `cpp-library/src/stages/fastenhancer.cpp`
(`b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510`).
Its documented constraints were inspected only: `settings.reject_unknown`
accepts just `model`; sessions are 16 kHz or 48 kHz with exactly 10 ms calls;
`wav_in`/`wav_out` are fixed float32 tensors with matching cache tensors;
nonfinite, unknown-key, asset-missing and shape-mismatched cases fail closed.
No C++ stage is built, no ONNX session is created and no weight is loaded.

Exact pins used by this package (full manifest in `SOURCES.sha256`):

| Identity | SHA-256 |
|---|---|
| `cpp-library/src/stages/fastenhancer.cpp` | `b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510` |
| `plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `adapters/fastenhancer/README.md` | `32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea` |

All `source:` pins above are workspace-relative; header/contract pins are
SDK-worktree-relative. Pin parsing is strict: malformed, duplicated,
traversing or out-of-scope lines are rejected fail-closed.

## Frontend and boundary invariants

- Documented public v0 geometry only: 16 kHz, mono, `f32`, 160 samples/call,
  zero integer content delay, one output frame per input frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `processor_exposure=false`,
  `c_public_boundary=false`, `installed_v0_geometry_preserved=true`.
- Public reference family identity preserved; no header, contract, descriptor,
  registry, default, CMake, shared build or CI file is modified.

## Enhancement acceptance profile

Acceptance profile `enhancement` is pinned from
`plan/swarm/VERIFICATION.md` and mapped in `report.json:acceptance_profile`:

| Profile case | Evidence here | Status |
|---|---|---|
| Identity + noisy control | `controls.identity`, `controls.named_baseline` | synthetic only |
| Established task-matched baseline | named `noisy_input_no_processing` | synthetic only |
| Paired SI-SDR / STOI | per-condition paired clean references | synthetic only |
| Clean-speech preservation | `controls.clean_speech_preservation` | synthetic only |
| Peaks + invalid outputs | per-condition peaks; `adverse` rejections | synthetic only |
| Unpaired speech screen / listening | none | not applicable, not run |
| Alignment, state, memory, timing | zero delay/frame state recorded | partial synthetic |

The scorer is a dependency-free port of non-extended pystoi 0.4.1 and the
zero-mean SI-SDR formula, byte-identical apart from `SCORER_ID` to the merged
`online-multichannel-wpe` scorer, cross-checked against six inherited vectors.
It is not an oracle, is not the audio-bench scorer, and carries no real-speech
or listening claim. Real paired cohorts, listening, target-device timing and
installed memory remain absent.

## Canonical artifacts and local digests

| File | SHA-256 |
|---|---|
| `contract.json` | `b33ac0de90b53c837dba51c409bfdf8bf45d09c21b157e2c4841a58b09d144d6` |
| `adapter.json` | `44731a4adee09aa03ad1f0cecc376c4582afdcf728a5cd817ebf160834af71c1` |
| `provider.json` | `3000d76b0ef5b668e2ecbf41b4d1a12681a1c9ecdc80a30fa8f9b5d8f07fcbc0` |
| `scorer.py` | `c9d923646ba75c102ba065ba3f64392e05347c5e5030e812502459b8969dc365` |
| `crosscheck_vectors.json` (inherited) | `7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2` |
| `report.json` | `d67f52708b0a232f06ffd3906060e4711ce99347b7c7c9e160d558bc368c6b66` |
| `report.json.sha256` | `74ddcbadcc44f8434d928ad16771e05e138849b9748233d3efc184276e5813e6` |

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself.

## Evidence content

- Frozen conditions: `identity`, `noisy_control`, `frontend_shape`,
  `malformed_input`, `silence` (9,600 samples each, fixed LCG seeds).
- Identity and named noisy-input controls are reported beside the candidate;
  regressions are recorded verbatim, losing conditions are not hidden.
- Adverse config/frame/lifecycle/validity cases fail closed without advancing
  DSP state; nonfinite input is never counted as silence.
- Three cold-start regenerations are byte-identical; no tolerance or substitution.
- Scorer cross-check deltas and inherited provenance are disclosed, never used
  as an acceptance oracle.

## Independent preset timing (proposal only)

Source-reported Tiny/Small RTF and paced-process CPU figures in
`cpp-library/PIPELINE_DESIGN_REPORT.md` and
`REALTIME_COMPONENT_CANDIDATES.md` are provenance only: not measured here, not
from the target device, not pooled as a controlled benchmark, not transferred
to this fixture and not used as a threshold.

## Rights gap — blocked

Exact upstream source revision, pretrained-model terms and ONNX-runtime
redistribution rights are **not** cleared. The pinned adapter README records a
source release commit but no separate model terms; weights remain local
evaluation assets pending confirmation. No vendoring, build, installed
provider, registry change or release claim is permitted until rights are
cleared. `rights_gap.blocked=true` in `report.json`.

## Remaining gates (all blocked)

1. Real paired cohort with rights-cleared clean references.
2. Independent listening or authorized predictive screen.
3. Target-runtime content/availability timing, memory and deadline evidence.
4. Provider intake, descriptor and catalog review.
5. Explicit public default selection.
6. Exact approved external reference parity.
7. Exact upstream source, model-weight and ONNX-runtime rights clearance.

## Files

- `reference.py` — deterministic synthetic generator, controller and report builder.
- `scorer.py` — pinned dependency-free SI-SDR / non-extended STOI port.
- `run.py` — regenerates `report.json`, `report.json.sha256` and `SOURCES.sha256`.
- `contract.json` / `adapter.json` / `provider.json` — task-local boundary manifests.
- `test_reference.py` — Python unittest suite.
- `verify.py` — read-only pins/JSON/reproduction/invalid-case/licensing/scope verifier.
- `report.json` / `report.json.sha256` / `SOURCES.sha256` (+ `.license` sidecars).

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with
`PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/check_contributors.py --policy sdk --event <event.json>
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output <scratch>/ci
git -C <worktree> diff --check
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-FASTENHANCER-SOURCE-LINKED-ONNX-WRAPPER
```

`run.py` and `verify.py` are deterministic and read no network, model or media
assets. Full reproduction is performed in a fresh private scratch tree before
submission; no board, handoff or installed-package state is written.
