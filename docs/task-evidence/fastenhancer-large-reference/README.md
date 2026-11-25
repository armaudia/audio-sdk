<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FASTENHANCER-LARGE-REFERENCE — caller-supplied-asset blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `FastEnhancer Large reference`
(`component_id=fastenhancer-large-reference`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline reference as a **caller-supplied external
asset** exactly as `CONTRACTS.md` `as_asset_v0` requires: asset ID, byte count,
SHA-256 and `storage=external`, supplied by the caller, with no provider file
access and no download. It also records the exact documented Large streaming
geometry from the pinned MIT source checkout.

The MIT **source checkout is present and pinned**, but the exact **Large
weights and the pinned runtime are absent**, and no linked record pins a Large
byte count or SHA-256. A deterministic stdlib **synthetic delayed-causal chunk
surrogate** exercises only the boundary, accounting and refusal mechanics. It
is explicitly opt-in, **is not FastEnhancer-L**, and substitutes for no gate.

No candidate artifact was downloaded, hashed, loaded, built, compiled, executed
or bundled. No Large weight, derived weight, ONNX graph, ONNX Runtime, native
engine, media, corpus, device clock, listener, benchmark or release artifact is
present or claimed. There is **no candidate output or result**. No public
API/ABI, `CONTRACTS.md`, descriptor, registry, installed default, shared build,
dependency lock, CI, board or handoff file changes. Only this task-local
directory is added.

## Exact external blocker

### 1. The exact Large asset is absent and unpinned

The pinned MIT source checkout is present at
`data/checkouts/FastEnhancer`, revision
`49ab55a57e3a064d94c6412cd0f0a383a55ca0f8`, tree digest
`30e6a40df543545c1d16d77031db1135e4201acae27dca356c752799d0737ad0`
(85 files, 654,180 bytes, MIT `LICENSE` SHA-256 `38164c22…`).

The checkout contains the Large training config
`configs/fastenhancer/l.yaml` and export code, **not** a trained Large
checkpoint or ONNX graph. Every fixed Large probe is absent:
`data/models/fastenhancer/fastenhancer_l.onnx`,
`fastenhancer_l_spec.onnx`, `fastenhancer_l.pt`, `fastenhancer_l.pth`,
`cpp-library/.deps/fastenhancer_l.onnx`, `cpp-library/logs/fastenhancer_l` and
the Pro large model/processor paths.

No linked record pins a Large identity. The asset ledger
(`research/noise_suppression_assets_20261027.json`) records only the 16 kHz DNS
Tiny and Small ONNX artifacts. The rights register records only
`fastenhancer_m`, `fastenhancer_s`, `fastenhancer_t` and
`fastenhancer_t_16k`. The release tags `onnx-vd-v1.0.0` and
`ckpt-vd-v1.0.0` exist in the checkout, but their release assets are not local
and no byte count or SHA-256 for a Large artifact is recorded anywhere.
Acquisition is **not permitted** by this package.

**Required action.** Supply an exact FastEnhancer-L checkpoint or ONNX graph as
a caller-owned external asset with an immutable upstream revision, release tag,
byte count and SHA-256, verified without a network download.

### 2. The pinned runtime is absent

`adapters/fastenhancer/requirements.lock` pins CPython 3.10 macOS arm64 with
`onnxruntime==1.20.1` (wheel SHA-256 `e50ba5ff…`), NumPy 1.26.4 and SoundFile
0.13.1. The adapter records `data/envs/dtln-onnx` as its evaluator
environment. Neither the environment nor the wheel is present at any fixed
probe, and `onnxruntime` is not importable in the evidence interpreter. No
exact-runtime run, inference or parity vector was produced.

**Required action.** Install the exact hash-pinned environment in an approved
isolated runner, record every artifact digest, and document its distribution
and product-use terms.

### 3. Rights are not cleared for Large

The upstream repository is MIT-licensed. The release page records **no separate
pretrained-model terms**, and the ledger records
`not specified separately; retain local only`. There is **no Large entry** in
the rights register. The only explicit evaluation-only attestation covers the exact
Tiny16 asset and aggregate benchmark scores; it does not transfer to Large.
Acquisition, redistribution, customer deployment and public playback remain
**unknown**. No weight, derived weight, executable or output may be bundled,
repackaged, exposed or redistributed.

**Required action.** Supply written Large-specific model-weight,
training-data and runtime terms, the complete notice bundle, and an explicit
redistribution/product-use decision.

### 4. No exact parity, cohort, scoring, timing or provider evidence

There is no approved Large reference output, frozen input vector or output
digest under the pinned runtime; no rights-cleared paired real cohort; no
independent SI-SDR/STOI scorer or permitted listening result; and no target
device pacing, deadline, memory or chunk-boundary measurement. The documented
Large VoiceBank-Demand table is author-reported provenance only, never a local
measurement, threshold or release claim. All **eight** release gates stay
`blocked`.

**Reopen condition.** Admit the candidate only when all four blockers clear and
approved exact-runtime outputs, a rights-cleared cohort, independent scoring or
listening, target timing and an opt-in provider intake are available. Until
then **no candidate result may qualify** the component.

## Documented Large geometry (transcribed, not executed)

| Domain | Geometry |
| --- | --- |
| Public v0 | 16 kHz, mono, `f32`, 160 samples per 10 ms frame; preserved, not changed |
| Large reference | 16 kHz VoiceBank-Demand, mono, `f32` |
| STFT | 512-point FFT, 512-sample Hann window, 100-sample native hop, 257 bins |
| Encoder | 128 channels, kernels `[8,3,3,3,3]`, stride 4, 64 RNNFormer bins |
| RNNFormer | 5 blocks, 96 channels, 64 frequency bins, 4 heads |
| Caches | 2 × `[1,412]` STFT/iSTFT + 5 × `[1,64,96]` RNNFormer = 7 caches |
| Delay | 412-sample buffering/content delay, 412 invalid startup samples |
| Drain | 5 flush hops / 500 produced samples; declared bound 8 calls / 800 samples |
| Output | identity output length; final partial tail preserved |

The 100-sample native hop is **not** the installed 160-sample v0 frame and is
**not** the 256-hop 16 kHz DNS Tiny/Small geometry. No v0 frame adapter,
resampler or native engine is implemented or claimed.

## Source-reported Large VBD values (provenance only)

| Metric | Value |
| --- | ---: |
| Parameters | 1,105 K |
| MACs | 11 G |
| RTF (Xeon) | 0.313 |
| RTF (M1) | 0.632 |
| DNSMOS P.808 | 3.53 |
| DNSMOS P.835 SIG / BAK / OVL | 3.44 / 4.04 / 3.16 |
| SCOREQ | 0.239 |
| SI-SDR | 19.6 dB |
| PESQ | 3.26 |
| STOI | 0.952 |
| ESTOI | 0.877 |
| WER | 3.1 % |

These are the authors' VoiceBank-Demand 16 kHz test-table values from the
pinned checkout. They are **not** reproduced here, **not** the local DNS pilot,
**not** device timing, **not** this fixture's metrics, **not** a listening
result and **not** a release claim.

## Synthetic fixture (not a candidate result)

The surrogate is a synthetic delayed-causal gain path with the documented
**100-sample chunk**, **412-sample delay line** and **seven cache shapes**. It
runs five frozen synthetic conditions over 4,000 samples each. It does not
reproduce the model's tensor semantics.

Verified mechanics (all synthetic only):

- identity control is exact passthrough; the named noisy control is the
  observed input scored against the synthetic target;
- the independent chunk-loop driver is byte-identical to the stream driver;
- reset-at-midpoint split halves differ at the 412-sample boundary, which is
  recorded rather than hidden;
- a chunk-aligned prefix is stable against the full stream;
- a 1,093-sample partial tail returns exactly 1,093 samples;
- an impulse at source index 2,000 keeps output peak index 2,000;
- every output is finite, no output is clipped, and the largest synthetic peak
  is below 0.4;
- three cold-start regenerations are byte-identical; no tolerance is used.

No synthetic condition lost SNR or SI-SDR versus the noisy control in this
fixture; that is a property of the surrogate, not evidence about FastEnhancer-L.
No STOI, intrusive quality, listening, real cohort, device timing or candidate
parity result exists. The surrogate **cannot** qualify the component.

## Controls and adverse cases

- Config rejections: wrong model ID, sample rate, channels, sample format,
  native hop, FFT size, window size, window, buffering delay or cache layout;
  unpinned caller asset; unknown asset ID; surrogate without opt-in; altered
  synthetic asset identity or byte count. A fully pinned synthetic admission
  control proves the admission branch; it is explicitly not the candidate and
  has `qualification_effect=none`.
- Stream rejections: empty, oversized, string, boolean, non-finite, infinite and
  out-of-range streams fail with unchanged state; a second stream and any
  post-close call fail closed.
- Chunk rejections: wrong length/type, non-finite and out-of-range chunks, wrong
  cache set/shape, non-finite/boolean cache values and a non-finite delay fail
  before state or cache mutation.
- Non-finite input is never counted as silence; a missing or unpinned asset
  never qualifies.

## Sibling FastEnhancer evidence

The Tiny, Small and Medium packages are present only on sibling swarm branches
at this base, not merged into `a1e7573`; the source-linked wrapper is merged.
All are `DEFER` / `not_qualified` and none supplies Large bytes, runtime, rights
or parity:

| Package | Report SHA-256 | Decision | Gates |
| --- | --- | --- | ---: |
| `fastenhancer-tiny-reference` (77d58c4) | `20f007a5…` | DEFER | 8 blocked |
| `fastenhancer-small-reference` (14729af) | `ecb188b4…` | DEFER | 8 blocked |
| `fastenhancer-medium-reference` (2742d8c) | `2d062bd1…` | DEFER | 8 blocked |
| `fastenhancer-source-linked-onnx-wrapper` (56f40ef) | `34edd5df…` | DEFER | 7 blocked |

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `onnxruntime_invoked=false`, `native_engine_built=false`,
  `sdk_data_dir_added=false`, `files_outside_task_directory_written=false`.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  FastEnhancer provider is installed or registered.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-FASTENHANCER-LARGE-REFERENCE]`, stable-field digest). The
  mutable full `plan/swarm/TASKS.json` is **never hashed or pinned**.
- No request is ever processed as FastEnhancer-L. Valid candidate requests fail
  closed because the exact asset identity and runtime are absent.
- No proposal `adapter.json` or `readiness.json` is added; machine-readable
  state lives in `contract.json` and `report.json`.

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | Use |
| --- | --- |
| `source:data/checkouts/FastEnhancer/LICENSE` | MIT source license. |
| `source:data/checkouts/FastEnhancer/configs/fastenhancer/l.yaml` | Large geometry. |
| `source:data/checkouts/FastEnhancer/docs/docs/onnx.md` | 100-hop and 412-delay streaming recipe. |
| `source:data/checkouts/FastEnhancer/models/fastenhancer/default/model.py` | Seven cache shapes and recurrence. |
| `source:adapters/fastenhancer/requirements.lock` | CPython 3.10 / `onnxruntime==1.20.1` pin. |
| `source:research/noise_suppression_assets_20261027.json` | Tiny/Small-only ledger, no Large entry. |
| `source:audio-benchmark-platform/audio-pro/inventory/rights-register.json` | No Large rights entry. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `as_asset_v0` external asset and no-download rule. |
| `worktree:docs/task-evidence/fastenhancer-source-linked-onnx-wrapper/*` | Merged sibling boundary evidence, DEFER. |

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, geometry, results, pins, commands, gates. |
| `reference.py` | Deterministic source/weights/runtime probes, delayed-causal surrogate, metrics and report/contract model. |
| `run.py` | Regenerates `report.json`, its sidecar, the README digest table, `contract.json` and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions, rights scope and pins. |
| `test_reference.py` | Deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README-digest, reproduction, disposition, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Canonical artifacts and local digests

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself. The table below
is refreshed by `run.py --all` and checked by `verify.py`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `9e5556fc6b60e1393790efe8ada3a8c580dd509fbc98b11dd645bd2a67f90359` | 97987 |
| `report.json` | `feb8be5978ba6cffdba8348bce5cdf1ee1ca505e203b69d4fdf8457199cbb9d6` | 50070 |
| `report.json.sha256` | `662e3563d167744767f85f979dd577bc653a175a88fa234d2dee390d3e92c2b1` | 78 |
| `run.py` | `7f50b325d30b17396c473ebe429d71c55963265bd2520b6c2e49d8521663f61d` | 6093 |
| `test_reference.py` | `8a4550b503e0b965faefc952101fd05e5cee084e7410d09ab816e07c789a9445` | 35291 |
| `verify.py` | `0a10db010a540332e97f485176321048a70a97d94a778b2db69febe1af637f32` | 23551 |
<!-- DIGEST_TABLE_END -->

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
git -C <worktree> diff --check
```

`run.py` and `verify.py` are deterministic and read no network, model or media
assets. Full reproduction is performed in a fresh private scratch tree before
submission; no board, handoff or installed-package state is written.

## Remaining gates (all eight blocked)

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `rights_cleared_paired_cohort`
6. `independent_scoring_and_listening`
7. `target_runtime_timing`
8. `provider_intake_and_default_selection`

A readiness conclusion with these **exact external blockers** is the accepted
investigation handoff for this feasibility task. It does **not** close the
conditional implementation, and no missing result may qualify the candidate.
