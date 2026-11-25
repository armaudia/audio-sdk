<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FASTENHANCER-MEDIUM-REFERENCE — blocker package

Proposal-only, incomplete and **not qualified** feasibility evidence for the
`FastEnhancer Medium reference` component (`reference_family=fastenhancer`,
`component_id=fastenhancer-medium-reference`). Decision: **DEFER**, before
`processor_exposure`. `status=proposal_only_incomplete`,
`qualification_status=not_qualified`. A missing result never qualifies a
candidate.

The task asks for an exact SDK reference only when the licensed source, weights
and runtime are all present and permitted. The exact source and weight
identities are pinned, but the runtime is absent from this SDK worktree, the
weights are private evaluation assets, and the recorded rights register leaves
Medium48 q8 redistribution **unknown**. Implementing a stand-in model would
fabricate a result, so this package records a concrete blocker instead.

Nothing here registers a provider or changes the public API/ABI, installed v0
behaviour, descriptor settings, registry, defaults, shared build, CMake, CI,
board or handoffs. No real audio, model download, weight read, vendor runtime
call, device timing, listening result, benchmark or release claim is made.

## Exact pins

All pins are SHA-256. `source:` paths are workspace-relative; `worktree:` paths
are SDK-worktree-relative. The full mutable `plan/swarm/TASKS.json` is
deliberately **not pinned or hashed**; only the stable linked-row identity is
projected.

| Identity | SHA-256 |
|---|---|
| `cpp-library/src/stages/fastenhancer_native.cpp` | `75d50ad23d299a3d05b52bbe39a820521608b750e32015307115a3df7ada1326` |
| `cpp-library/src/stages/fastenhancer.cpp` | `b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510` |
| Pro medium processor README | `e2752bb6b06231b10ec1adc46df84e9d70b93011a0c6c9ec409bdd5e628f9aef` |
| Pro upstream manifest (52 blobs) | `b1422bdbfc3de24e51ce5bf46a6828ac116aaa6ee897c668020f144948b7f238` |
| Pro frozen oracle (104 keys + 10 controls) | `cdde3ca7341893f8066b546af820331e4b579b3e17fa8a0d4029ffd2c6d78448` |
| Pro configuration schema | `e92dac8d17133d9b0441b600af24a4e0074a6ebbac4f80cf88575f513a7d2b8f` |
| Pro legacy snapshot manifest (7 blobs) | `49ab91e0b6ed23c13a0fb5a00d79a50fb2dc9c8baa5e98550f82edf381f51c9c` |
| Pro evidence record | `03b6cb6f010f42aa43bd0e0d336cc15811933981fc2cd11a065816598d320f08` |
| Rights register | `e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44` |
| Pro handoff | `90b55394089ce89736b79d17fe245728a0b641056dbe05fc6bb1eb9480d5e2c3` |
| `plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| Candidate census | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| Candidate matrix | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Exact model asset identity (recorded, **not** read, copied or admitted):

| Field | Value |
|---|---|
| Asset | `fe.q8` |
| Byte count | `565108` |
| SHA-256 | `d6f98e186bee6ed655b52a2edf5f707ccf761c755bb69de8de7f68cad42d7837` |
| Git blob | `ab6f8c711d3e23ace911c5e1e11203fadd43ca19` |
| Source revision | `3e2446fc58886fc02b099b54651adc9a10a65454` |

## Task geometry (transcribed, not measured)

| Domain | Geometry |
|---|---|
| SDK v0 | 16 kHz, mono, f32, 160 samples per 10 ms call, declared delay 235 |
| Native | 48 kHz, mono, 480-sample analysis chunk, native hop 320, native delay 704 |
| Modes | processing-thread `2` and buffered-worker `3`; `callback_safe=false`; drain bound 3 |
| CPU | `fe_qgemm_init()` admission; ARM NEON or x86 AVX2+FMA3+F16C; no scalar tier |

The SDK delay 235 is the nearest SDK-domain integer to 704/3 and is not a
measurement. No session, tool, SIMD kernel or drain path is created here.

## Why the exact reference is not implemented

The conjunction required by the task fails on four recorded facts:

1. **Weights are private.** `audio-pro/docs/rights-register.md` records
   FastEnhancer Medium48 q8 evaluation, redistribution, customer deployment and
   public playback as **unknown**. The Pro handoff confirms rights for private
   evaluation only and states that model bytes, derived assets and build output
   remain private, with no public redistribution implied. The asset is absent
   from this SDK worktree (`sdk_worktree_asset_probe.found=[]`).
2. **No SDK-consumable runtime.** The only exact runtime is the pinned native
   `faster-enhancer.c` SIMD backend. It requires explicit `fe_qgemm_init()`
   admission, has no scalar tier, and is not present in the SDK worktree. There
   is no ONNX or pure-Python Medium runtime that could be pinned here.
3. **Exact parity is not reproducible here.** The 104-key frozen oracle is
   pinned, but regenerating or comparing it requires that native backend. No
   candidate output or parity vector exists.
4. **No matched evidence exists.** There is no rights-cleared paired cohort,
   independent listening, target timing/memory/deadline measurement, provider
   intake or release review.

A synthetic surrogate would not reproduce the model and could be mistaken for
a result, so this package produces no candidate, no quality metric and no
output vector. The deterministic fixture exercises only framing, admission
rejection and repeatability.

## What the deterministic reference does

`reference.py` is standard-library only. It:

- projects only the stable linked task-row fields
  (`task_id`, `title`, `mode`, `repository`, `component`) and never hashes the
  mutable full board;
- records the pinned source/weight/runtime identities and proves the exact
  asset is absent from the SDK worktree;
- rejects missing, malformed, out-of-scope, duplicate and nonfinite JSON;
- rejects invalid requests (geometry, mode, epoch, position, lifecycle, bool,
  string, nonfinite and out-of-range samples) before any controller exists;
- rejects missing/invalid/size/digest asset admissions; the admission mechanism
  is proven with a synthetic spec, never the private `fe.q8` bytes;
- runs a passive identity harness over five frozen synthetic stimuli and
  verifies byte-exact framing;
- regenerates the report three times with no tolerance or substitution.

The identity harness is **not** FastEnhancer, not a denoiser, not a baseline and
not a quality result.

## Enhancement acceptance profile

Profile `enhancement` is pinned from `plan/swarm/VERIFICATION.md`.

| Profile case | Status here |
|---|---|
| Identity and noisy control | harness identity only; no candidate |
| Established task-matched baseline | source-reported only; not run |
| Paired SI-SDR / STOI | blocked: no candidate output; no surrogate score |
| Clean-speech preservation | blocked: no candidate output |
| Peaks and invalid outputs | admission rejections only |
| Unpaired speech screen / listening | not applicable; not run |
| Alignment, state, memory, timing | documented boundary only; not measured |

## Eight blocked release gates

1. `RG-01` exact source and weight identity
2. `RG-02` rights and redistribution clearance
3. `RG-03` SDK-consumable runtime and toolchain
4. `RG-04` exact reference parity oracle
5. `RG-05` rights-cleared paired cohort
6. `RG-06` independent listening or screen
7. `RG-07` target runtime timing, memory and deadline
8. `RG-08` provider intake, public surface and release review

Every gate is `blocked`; none is waived, and no missing result qualifies the
candidate.

## Files and local digests

`report.json` is canonical JSON (sorted keys, compact separators, no `-0.0`,
NaN or Infinity, one trailing newline). `report.json.sha256` is regenerated from
those exact bytes. `SOURCES.sha256` pins every boundary source and every package
file except itself.

| File | Role |
|---|---|
| `README.md` | this blocker record |
| `contract.json` | task-local boundary and exact-blocker manifest |
| `reference.py` | deterministic evidence builder |
| `report.json` | canonical machine-readable result |
| `report.json.sha256` | report digest sidecar |
| `SOURCES.sha256` | generated pin manifest |
| `verify.py` | strict read-only verifier |
| `test_reference.py` | Python unittest suite |
| `run.py` | three-pass regeneration |
| `*.license` | SPDX sidecars |

## Reproduction

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and the pinned
interpreter `/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
git -C <worktree> diff --check
```

`run.py` and `verify.py` read no network, model, weight or media asset. Only
this task directory is written.
