<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-GTCRN-STREAMING-ONNX — task-local synthetic readiness evidence

Proposal-only, incomplete and **not qualified** evidence for `GTCRN streaming ONNX`
(`reference_family=gtcrn`, `component_id=gtcrn-streaming-onnx`). Decision: **DEFER**,
before `provider_registration`. `status=proposal_only_synthetic_readiness_incomplete`,
`qualification_status=not_qualified`, readiness conclusion `not_ready`. Missing
evidence never qualifies a candidate.

This package models the documented GTCRN streaming ONNX boundary and runs a
deterministic pure-Python streaming surrogate at that boundary. It is **opt-in,
unregistered and OFF by default**. It does not change the public API/ABI, installed
v0 geometry, defaults, descriptor settings, provider registry, shared build, CI,
board or handoffs. No weight is downloaded, no ONNX session is created, and no real
audio, device timing, listening result, benchmark or release claim is made. The
caller-supplied-asset path and the surrogate path are distinct; the real path fails
closed and never silently falls back.

## Why this is a readiness conclusion, not an implementation

The pinned adapter (`adapters/gtcrn-streaming/run.py`) is a usable integration
anchor, and the pinned dereverberation screen records a real local run. But this
repository has **no GTCRN weight asset**, **no ONNX Runtime package** in the pinned
interpreter, and **no cleared checkpoint or ONNX Runtime redistribution terms**. The
task forbids downloading weights, using real audio, invoking devices, and making
benchmark or release claims. Under those constraints the exact model/runtime cannot
be reproduced, so this package ships:

1. a caller-supplied-asset reference boundary with the exact tensor contract, and
2. a deterministic surrogate that preserves hop, state-cache shapes and lookahead,
3. a strict `not_ready` conclusion with the exact external blocker and reopen
   condition.

## Pinned boundary and source pins

The boundary anchor is `adapters/gtcrn-streaming/run.py`
(`272cea7120a1e21e67c1f6bfcd37848dd79fe5a7910ee79f2d48c6c31f856ec9`).
Documented constraints were inspected only: CPU execution provider, one 257-bin
real/imag frame per call, three persistent cache tensors zeroed by `reset()`, a
512-point square-root-Hann window with a 256-sample hop, and 256-sample padding on
both utterance sides.

| Identity | SHA-256 |
|---|---|
| `adapters/gtcrn-streaming/run.py` | `272cea7120a1e21e67c1f6bfcd37848dd79fe5a7910ee79f2d48c6c31f856ec9` |
| `research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |

All `source:` pins are workspace-relative; header/contract pins are
SDK-worktree-relative. Pin parsing is strict: malformed, duplicated, traversing or
out-of-scope lines are rejected fail-closed.

## Preserved streaming geometry

| Item | Value |
|---|---|
| sample rate / channels / format | 16 kHz / mono / f32 |
| analysis/synthesis window | 512-sample `sqrt(periodic Hann)` = `sin(pi*n/512)` |
| hop | 256 samples = 16 ms |
| STFT representation | 257 real/imag bins, tensor `[1,257,1,2]` |
| persistent caches | `conv_cache [2,1,16,16,33]`, `tra_cache [2,3,1,1,16]`, `inter_cache [2,1,33,16]` |
| centered-STFT lookahead | 256 samples = 16 ms (as estimated upstream) |
| WOLA synthesis delay | 256 samples = 16 ms |
| analytical content delay | 512 samples = 32 ms |
| measured timing | **none claimed** |

The installed v0 frontend (16 kHz mono f32, 160-sample frames, zero content delay)
is recorded and preserved unchanged. The 256-sample model hop is task-local model
geometry, not an installed v0 geometry change.

## Caller-supplied-asset contract

`asset.json` declares the expected file (`gtcrn_simple.onnx`), inputs and outputs.
`asset_present=false`, `sha256=null`, `license=unverified_absent`. The real mode
(`mode=caller_supplied_onnx`) returns `rejected_asset_unavailable`; there is no
silent fallback. `adverse.config_rejections` records that behavior, plus traversal,
absolute-path, unknown-mode, missing-key, non-finite and wrong-type rejection.

## Enhancement acceptance profile

Profile `enhancement` is pinned from `plan/swarm/VERIFICATION.md` and mapped in
`report.json:acceptance_profile`:

| Profile case | Evidence here | Status |
|---|---|---|
| Identity + noisy control | `controls.identity`, `controls.named_baseline` | synthetic only |
| Established task-matched baseline | named `noisy_input_no_processing` | synthetic only |
| Paired SI-SDR / STOI | per-condition paired synthetic clean references | synthetic only |
| Clean-speech preservation | `controls.clean_speech_preservation`, exact WOLA identity reconstruction | synthetic only |
| Peaks + invalid outputs | per-condition peaks; `adverse` rejections | synthetic only |
| Unpaired speech / listening | none | not applicable, not run |
| Alignment, state, memory, timing | analytical sample counts and modeled caches | partial analytical |

The scorer is a dependency-free port of non-extended pystoi 0.4.1 and the zero-mean
SI-SDR formula, byte-identical apart from `SCORER_ID` to the merged
`online-multichannel-wpe` scorer. It is not an oracle, not the audio-bench scorer,
and carries no real-speech or listening claim.

## Prior screen is provenance, not qualification

The pinned dereverberation screen reports the upstream `gtcrn_simple.onnx` at median
SI-SDR 5.66 dB versus 16.49 dB for identity on 72 paired cases, winning 0/72 pairs,
with median RTF 0.0459 and an estimated 16 ms STFT lookahead. Those values are
reproduced **only as provenance** (`prior_screen_provenance`), are not measured here,
and are not used as qualification. The screen's conclusion stands: GTCRN must not be
treated as a dereverberator, and denoising must be validated separately. The
surrogate's synthetic denoising probe here shows essentially no improvement, which is
consistent with leaving the candidate unqualified.

## Exact external blocker and reopen condition

**Blocker.** No exact GTCRN weight asset (for example `gtcrn_simple.onnx`) with an
immutable URI, SHA-256 and byte size is available, and neither the checkpoint license
nor the ONNX Runtime redistribution terms are cleared for this repository. Weights are
not downloadable under this task.

**Reopen.** An authorized caller supplies a rights-cleared immutable weight asset with
recorded SHA-256, byte size, license and a pinned ONNX Runtime build; then rerun real
streaming parity, a held-out real paired denoising cohort, independent listening and
target-runtime deadline/memory evidence. No board, handoff or reviewer dispatch is
part of this package.

## Canonical artifacts and local digests

| File | SHA-256 |
|---|---|
| `contract.json` | `7ba9e0617d2fdab4ae5b4d46ffb8cb4fdd7a2bbb95530fc842d66e95cbf10078` |
| `adapter.json` | `cdf4b5d0f13de18c7972ebdfc9123f04e7bf6a021c6d0eb3dcb4bbe38fcee987` |
| `provider.json` | `cac831bf03b39a619e17a39750d9c19ca25d4170e07589c63fc8f758b0bb18b3` |
| `asset.json` | `dd0310752e5a43e8fb95c6d06caa1a92c9be4df733d87fac996fdb5382616871` |
| `scorer.py` | `f21d7d1d563fdc0b5afce6ce17ec4b730ac6d941fb4d8079cf7060f2f92fb521` |
| `report.json` | `34970e44019cf99eddccfebddce2c19de1dbddda7108fe69e77040f2b503163d` |
| `report.json.sha256` | `06c49dba70ebeebaf6a90f243c68f730ad145a2f927d0cb8b53d913550a0c43f` |

`report.json` is canonical JSON (`sort_keys`, minimal separators, no `-0.0`/NaN/
Infinity, trailing newline). `report.json.sha256` is regenerated from those exact
bytes. `SOURCES.sha256` is a generated manifest of every pinned boundary and every
file in this directory except itself.

## Evidence content

- Frozen conditions: `identity`, `noisy_control`, `reverberant_control`,
  `frontend_shape`, `silence` (9,728 samples each, fixed LCG seeds).
- Identity and named noisy-input controls are reported beside the candidate;
  regressions are recorded verbatim, losing conditions are not hidden.
- Identity WOLA reconstruction is analytically exact with unit gains; the check is
  recomputed by the verifier.
- Adverse config/frame/lifecycle/validity cases fail closed without advancing stream
  state; nonfinite input is never counted as silence; the real asset path never falls
  back to the surrogate.
- Three cold-start regenerations are byte-identical; no tolerance or substitution.
- Only this task directory is written; board, handoff and reviewer state are untouched.

## Files

- `reference.py` — deterministic synthetic generator, streaming surrogate, controller and report builder.
- `scorer.py` — pinned dependency-free SI-SDR / non-extended STOI port.
- `run.py` — regenerates `report.json`, `report.json.sha256` and `SOURCES.sha256`.
- `contract.json` / `adapter.json` / `provider.json` / `asset.json` — task-local boundary manifests.
- `test_reference.py` — Python unittest suite.
- `verify.py` — read-only pins/JSON/geometry/reproduction/invalid-case/licensing/scope verifier.
- `report.json` / `report.json.sha256` / `SOURCES.sha256` (+ `.license` sidecars).

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output <scratch>/ci
git -C <worktree> diff --check
```

`run.py` and `verify.py` are deterministic and read no network, model or media
assets. The verifier also recomputes the WOLA identity reconstruction rather than
trusting the recorded value.
