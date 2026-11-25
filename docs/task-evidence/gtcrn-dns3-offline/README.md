<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-GTCRN-DNS3-OFFLINE — offline caller-asset boundary and synthetic readiness evidence

Proposal-only, incomplete and **not qualified** evidence for `GTCRN DNS3 offline`
(`reference_family=gtcrn`, `component_id=gtcrn-dns3-offline`). The acceptance
profile is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`provider_registration`; `status=proposal_only_synthetic_offline_incomplete`,
`qualification_status=not_qualified`, readiness conclusion `not_ready`. Missing
evidence never qualifies a candidate.

This package models the documented GTCRN DNS3 **offline** boundary and runs a
deterministic pure-Python whole-utterance STFT/ISTFT surrogate at that boundary.
It is **opt-in, unregistered and OFF by default**. It does not change the public
API/ABI, installed v0 geometry, defaults, descriptor settings, provider registry,
shared build, CI, board or handoffs. No weight is downloaded, no torch runtime is
imported, no model is loaded, and no real audio, device timing, listening result,
benchmark or release claim is made. The caller-supplied-asset path and the
surrogate path are distinct; the real path fails closed and never silently falls
back.

## Why this is a readiness conclusion, not an implementation

The pinned adapter (`adapters/gtcrn/run.py`) is a usable offline integration
anchor and the pinned pilot records a real local run. But this SDK worktree has
**no GTCRN DNS3 source/checkpoint asset**, **no CPython 3.10 torch 1.13.1
runtime**, and **no checkpoint-specific or redistribution clearance**. The task
forbids downloading weights, using real audio, invoking devices and making
benchmark or release claims. Under those constraints the exact offline model
cannot be reproduced, so this package ships:

1. a caller-supplied-asset reference boundary with the exact offline tensor
   contract and pins;
2. a deterministic surrogate that preserves the 512/256 geometry, centered
   framing, identity sample mapping and exact output length;
3. a strict `not_ready` conclusion with the exact external blocker and reopen
   condition.

## Exact external blocker

The upstream identity is pinned: repository
`https://github.com/Xiaobin-Rong/gtcrn` at commit
`502ebfab64da7c4a9af78dcb9c6ceef1ebb01c73`, its MIT source licence, the
`gtcrn.py` file (13,504 bytes) and the DNS3 checkpoint
`checkpoints/model_trained_on_dns3.tar` (579,819 bytes), all by SHA-256 from the
pinned research ledger. The assets are **not present in this SDK worktree**; the
adapter lock targets **CPython 3.10 / macOS arm64** with **torch 1.13.1** and
**torchaudio 0.13.1**, while the pinned evidence interpreter is **CPython
3.12.16**, where `torch` is not importable. Checkpoint terms, DNS3 training-data
provenance/overlap, redistribution and product-use clearance are **not**
established; only upstream source code MIT is recorded and there has been no
legal review. Nothing was copied, vendored, built, downloaded, installed or
redistributed. The four exact blockers are recorded verbatim in
`contract.json:exact_blockers` and `report.json:exact_blockers`; every release
gate stays `blocked`.

Reopen condition: an authorized caller supplies both immutable hash-pinned
assets with recorded SHA-256, byte size and checkpoint-specific terms, installs
the pinned CPython 3.10 torch 1.13.1 runtime in an approved isolated runner, and
records positive training-data/redistribution/product legal clearance; only then
rerun real offline parity, a held-out real paired denoising cohort, independent
listening or a separately labeled predictive screen, and target-runtime
timing/memory before provider intake.

## Boundary

- Installed public v0 geometry is documented only and preserved: 16 kHz, mono,
  `f32`, 160 samples per call, zero integer content delay.
- The offline model geometry is separate from installed v0: one whole-utterance
  waveform, 512-point `sqrt(periodic Hann)` analysis/synthesis window, 256-sample
  hop, 257 real/imag bins, centered STFT with 256-sample padding, and one
  `[1,257,T,2]` model input/output.
- The adapter maps output sample `n` to input sample `n` with zero compensation;
  this is an offline whole-utterance alignment, explicitly **not causal** and not
  a streaming or device-delay claim.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `shared_cmakelists_change=false`, `installed_v0_behavior_change=false`,
  `processor_exposure=false`, `ci_change=false`.
- No provider registration, no installed-v0/ABI/registry/default/shared-build
  or CI change, no board or handoff write. Only this task-local directory is
  added.
- Configuration, signal, geometry, missing, invalid, nonfinite, oversized and
  caller-supplied-asset rejections fail closed without producing output or
  loading a model.

## Preserved offline geometry

| Item | Value |
|---|---|
| sample rate / channels / format | 16 kHz / mono / f32 |
| processing mode | offline whole utterance, non-causal |
| n_fft / window / hop | 512 / 512-sample `sqrt(periodic Hann)` / 256 samples |
| hop duration | 16 ms |
| STFT representation | 257 real/imag bins; model tensor `[1,257,T,2]` |
| frame count | `T = 1 + floor(N/256)` |
| STFT padding | 256 samples on each side, centered |
| output length | exactly the input sample count |
| source-time mapping | identity, zero compensation |
| measured timing / memory | **none claimed** |

The installed v0 frontend (16 kHz mono f32, 160-sample frames, zero content
delay) is recorded and preserved unchanged. The 512/256 model geometry is
task-local offline geometry, not an installed v0 geometry change.

## Enhancement profile application

| Profile case | Evidence here | Status |
|---|---|---|
| Identity + noisy control | `controls.identity`, `controls.named_baseline` | synthetic only |
| Established task-matched baseline | named `noisy_input_no_processing` | synthetic only |
| Paired SI-SDR / STOI | per-condition paired synthetic clean references | synthetic only |
| Clean-speech preservation | `controls.clean_speech_preservation`, exact WOLA identity reconstruction | synthetic only |
| Peaks + invalid outputs | per-condition peaks; `adverse` rejections | synthetic only |
| Unpaired speech / listening | none | not applicable, not run |
| Alignment, state, memory, timing | analytical identity mapping and zero offline delay | partial analytical |

The scorer is a dependency-free port of non-extended pystoi 0.4.1 and the
zero-mean SI-SDR formula, byte-identical apart from `SCORER_ID` to the merged
`online-multichannel-wpe` scorer. It is not an oracle, not the audio-bench
scorer, and carries no real-speech or listening claim.

## Caller-supplied asset contract

`asset.json` declares, but never opens, hashes or executes, the exact two-file
offline asset:

- `gtcrn.py` — 13,504 bytes,
  `20bf0610702506fa45cd543454b84bbeb862d73c7c20a3f8d820fdc04da6099b`;
- `checkpoints/model_trained_on_dns3.tar` — 579,819 bytes,
  `a630d992cf792daf4ce2bb5bcf9c4d389f740a8f09c6e0971184697fe6371b79`;
- source commit `502ebfab64da7c4a9af78dcb9c6ceef1ebb01c73`;
- runtime `cpython-3.10-macos-arm64-torch-1.13.1-torchaudio-0.13.1`.

`asset_present=false`, `sha256` is expected but not declared present,
`license=unverified_absent`. `validate_asset_request` rejects a missing or extra
key, wrong commit, wrong rate/FFT/hop, wrong file count, wrong path, wrong
size/hash, unknown runtime or unavailable runtime. The reported environment
returns `blocked_asset_absent` when no asset is supplied and
`blocked_runtime_unavailable` when a hypothetical caller asset is supplied
without the pinned runtime. A positive gate-logic control reaches
`ready_for_caller_execution` but still sets `inference_executed=false` and
`asset_opened=false`. The real mode
(`mode=caller_supplied_gtcrn`) always returns
`rejected_asset_unavailable`; there is no silent fallback.

## Synthetic surrogate and conditions

The surrogate computes whole-utterance centered STFT frames, estimates a
per-bin noise magnitude from the lowest-energy frames, applies oversubtracted
magnitude gains with three-point frequency smoothing and minimum gain, then
overlap-adds the inverse transform with exact window normalization. It is a
scalar spectral-gain proxy, **not** GTCRN, not a learned model, not torch and not
a recurrent cache. Seven frozen conditions (`speech`, `unfamiliar_speech`,
`nonstationary_noise`, `clean_speech`, `clipped`, `tail_partial`, `silence`) each
use a deterministic paired clean target and observed input with fixed LCG seeds.
`tail_partial` has 9,819 samples, proving exact non-multiple-of-hop output length.
`silence` has an all-zero reference, so SI-SDR and STOI are undefined and the
condition is excluded, not counted as a win. Regressions are recorded verbatim,
including any synthetic clean-preservation loss.

## Controls and adverse cases

- `controls.identity`: exact observed input; its zero improvement is trivial by
  construction and labeled as such.
- `controls.named_baseline`: plain noisy input, not a GTCRN run.
- `controls.candidate`: offline surrogate on the speech condition.
- `controls.clean_speech_preservation`: surrogate on a synthetic clean target.
- `adverse.config_rejections`: ten invalid configuration cases.
- `adverse.signal_rejections`: seven invalid signal cases, including nonfinite,
  bool, string and oversized samples.
- `adverse.asset_gate`: absent, hash-mismatch, size-mismatch, wrong commit,
  wrong geometry, one file, unknown key, wrong runtime and runtime-unavailable.
- `adverse.asset_gate_control`: positive gate logic only; no inference.
- Identity WOLA reconstruction is analytically exact with unit gains; the
  verifier recomputes the record rather than trusting it.
- Three cold-start regenerations are byte-identical; no tolerance or
  substitution.

## Prior pilot is provenance, not qualification

The pinned DNS pilot reports GTCRN DNS3 median SNR gain +5.381 dB, mean SI-SDR
gain +5.412 dB, median STOI .9484 and median batch RTF .0124 on a 30-pair
exploratory DNS2020 subset; its paired STOI interval includes zero. The official
DNS3 table separately reports DNSMOS-P.808 BAK/SIG/OVRL 3.44/3.90/2.70. Those
values are reproduced **only as provenance** (`prior_pilot_provenance`), are not
measured here, are not pooled with the surrogate and are not used for
qualification. Training/evaluation overlap remains unresolved.

## Remaining gates (all blocked)

1. `exact_assets_and_runtime_present` — both hash-pinned caller assets and the pinned CPython 3.10 torch 1.13.1 runtime are present in an approved isolated runner.
2. `weight_and_runtime_rights_cleared` — checkpoint terms, DNS3 training-data provenance/overlap, torch redistribution/product terms and a positive legal decision are recorded.
3. `real_offline_parity_and_alignment` — the exact GTCRN offline model matches the pinned source for output length, identity alignment, finiteness and numerical parity.
4. `held_out_paired_denoising_cohort` — a predeclared held-out real paired cohort with matched identity/noisy controls and paired SI-SDR/STOI is run.
5. `independent_listening_or_predictive_screen` — authorized independent listening or a separately labeled predictive screen is collected.
6. `target_runtime_timing_and_memory` — content/availability timing, memory and deadlines are measured on the exact target.
7. `provider_intake_descriptor_and_default_review` — provider intake, descriptor review and explicit default-selection review are completed before any registry or catalog change.

## Canonical artifacts and local digests

| File | SHA-256 |
| --- | --- |
| `contract.json` | `ef0ce43cd36191bbf8cdc8140e5d3075481751acf1071c825bfc8af6a8065782` |
| `adapter.json` | `1ca8beb698c8ec882c8f3b30146d8d98ac7917d612ee79413a2302fa4cac6986` |
| `provider.json` | `05cd326ea2d614eabb0b4875d49148c17ca8676fe0e0b77c8930db32acb2492a` |
| `asset.json` | `b78755cc080fba7dcb746ea7e39edd49011952c415324d2b6cf9cf1c4778f784` |
| `reference.py` | `214035b7aeda8ef73cc8cee7ce823a24b8c07cca662b880e5b1ebc5a2b1a45fe` |
| `scorer.py` | `e2f481630cadfbb66d8167e6ba08f3da59e17bba669e74f58736f607fb38488e` |
| `run.py` | `cab52447318781b50cbf6b1a28e694ab21209e16d7052e203fbda114da9ce596` |
| `test_reference.py` | `233cdea591376fc9313e6bacaa3703e0ccdf271c82a7a4d1924c897e069127a2` |
| `verify.py` | `32a6ea371fa81b7b7b2e45192f21312369815a83089a1a54629b78b6e5ff953f` |
| `report.json` | `b4768c1ee3b6f9934c576496a9f224a7293edc2c09993b11892c03535b8557bd` |
| `report.json.sha256` | `a27ba5d6ca3f7d1847e97dee6f9bcbea4a92a96b6ab00d4cd6303024089af933` |

`report.json` is canonical JSON (`sort_keys`, minimal separators, no `-0.0`/NaN/
Infinity, trailing newline). `report.json.sha256` is regenerated from those exact
bytes. `SOURCES.sha256` is a generated manifest of every pinned boundary and
every file in this directory except itself.

## Files

- `reference.py` — deterministic synthetic generator, offline surrogate, asset gate and report builder.
- `scorer.py` — pinned dependency-free SI-SDR / non-extended STOI port.
- `run.py` — regenerates manifests, contract, report, digest sidecar, README digests and `SOURCES.sha256`.
- `contract.json` / `adapter.json` / `provider.json` / `asset.json` — task-local boundary manifests.
- `test_reference.py` — Python unittest suite.
- `verify.py` — read-only pins/JSON/geometry/reproduction/README digest table/invalid-case/licensing/scope verifier.
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
assets. The verifier also recomputes the WOLA identity reconstruction and
validates every digest in the README table rather than trusting it.
