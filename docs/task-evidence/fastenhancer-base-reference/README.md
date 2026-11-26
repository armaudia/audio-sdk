<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FASTENHANCER-BASE-REFERENCE — caller-supplied-asset blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `FastEnhancer Base reference`
(`component_id=fastenhancer-base-reference`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline reference as a **caller-supplied external asset**
exactly as `CONTRACTS.md` `as_asset_v0` requires: asset ID, byte count, SHA-256
and `storage=external`, supplied by the caller, with no provider file access and
no download. It records the exact 16 kHz DNS geometry and cache layout specified
by the pinned MIT training configuration. A deterministic stdlib **synthetic
chunk surrogate** exercises only the boundary, accounting and refusal
mechanics; it is explicitly opt-in, is not FastEnhancer-B, and substitutes for
no gate.

No candidate artifact was downloaded, hashed, loaded, built, compiled, executed
or bundled. No weight, derived weight, ONNX graph, ONNX Runtime, native engine,
media, corpus, device clock, listener, benchmark or release artifact is present
or claimed. There is **no candidate output or result**. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build,
dependency lock, CI, board or handoff file changes. Only this task-local
directory is added.

## Exact external blocker

The pinned MIT source checkout is present at `data/checkouts/FastEnhancer`,
revision `49ab55a57e3a064d94c6412cd0f0a383a55ca0f8`. It contains the Base
training configuration `configs/fastenhancer/b.yaml` and export code, **not** a
trained Base checkpoint or ONNX graph.

| Item | Status |
| --- | --- |
| Source checkout | **Present and pinned**: `data/checkouts/FastEnhancer`, `aask1357/fastenhancer` commit `49ab55a57e3a064d94c6412cd0f0a383a55ca0f8` |
| Base training config | **Present and pinned**: `configs/fastenhancer/b.yaml`, SHA-256 `bbfa1a69…` |
| Exact Base ONNX/checkpoint | **Absent and unpinned**: no linked ledger row, release digest or local file records a byte count or SHA-256 |
| Local Base probes | **Absent**: `data/models/fastenhancer/fastenhancer_b.onnx`, `fastenhancer_b_spec.onnx`, `.pt`, `.pth`, `cpp-library/.deps/fastenhancer_b.onnx` and Pro Base paths |
| Pinned Python runtime | **Absent**: `onnxruntime` 1.20.1 is not importable; only unrelated 1.31.1 installations exist |
| Rights entry | **Absent**: the rights register records only `fastenhancer_m`, `fastenhancer_s`, `fastenhancer_t` and `fastenhancer_t_16k` |
| Caller output / cohort | **Absent**: no approved reference output, frozen input vector, rights-cleared paired cohort or permitted listening result |
| Weight terms | **Unresolved**: MIT covers the source checkout only; the release page states no separate model terms and the ledger records “not specified separately; retain local only” |

The machine-readable record is `report.json` → `asset_boundary`,
`asset_admission`, `rights`, `native_evidence`, `exact_blockers` and
`release_gates`. `contract.json` carries the same disposition, geometry, pins
and all eight blocked release gates.

1. **The exact Base artifact is absent and its identity is unpinned.**
   `research/noise_suppression_assets_20261027.json` records only the 16 kHz DNS
   Tiny and Small ONNX artifacts. No linked record pins a Base byte count or
   SHA-256. Source presence is not a weight, graph or runtime artifact.
2. **The exact pinned runtime is absent.** `adapters/fastenhancer/requirements.lock`
   pins CPython 3.10 macOS arm64 with `onnxruntime==1.20.1` (wheel SHA-256
   `e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439`) and the
   adapter records `data/envs/dtln-onnx` as its evaluator environment. Neither
   is present. No exact-runtime reference run or parity vector was produced.
3. **Rights are not cleared for Base.** There is no Base entry in the rights
   register, so evaluation, acquisition, redistribution, customer deployment
   and public playback are all `unknown`. Rights are not evaluation-only; no
   permission exists. Nothing may be bundled, repackaged, exposed or
   redistributed.
4. **No exact reference parity exists.** There is no Base native processor,
   trace or parity vector. The present native artifacts cover Tiny, Small and
   Medium only and never transfer to Base. No exact model output under the
   pinned runtime, no rights-cleared paired real cohort, no independent scorer
   or listening result and no target pacing, deadline or memory measurement
   exist. All eight release gates stay `blocked`.

**Reopen condition.** Admit the candidate only when an exact FastEnhancer-B
checkpoint or ONNX graph is supplied as a caller-owned external asset with an
immutable upstream revision, release tag, byte count and SHA-256; the pinned
`onnxruntime==1.20.1` artifact with a recorded digest installs in the intended
environment and its terms are documented; written evaluation, redistribution,
customer-deployment and public-playback decisions exist; and approved
exact-runtime reference outputs, a rights-cleared cohort, independent
scoring/listening and target timing are available. Until then **no result may
qualify the candidate**.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- The candidate model's configuration-derived native geometry is quoted, not
  executed: 512-point periodic-Hann STFT, 256-sample hop, 257 spec bins,
  48 encoder channels, kernel `[8,3,3]`, stride 4, three RNNFormer blocks with
  36 channels / 24 frequency bins / 4 heads, 16 recurrent frames, five graph
  caches (two STFT caches plus three recurrent caches of `[1,24,36]`), a
  256-sample buffering delay, 256 invalid startup samples, two flush hops, and a
  finite drain bound of four calls / 640 samples.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `onnxruntime_invoked=false`, `native_engine_built=false`,
  `sdk_data_dir_added=false`. No proposal `adapter.json` or `readiness.json`
  is added; machine-readable state lives in `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-FASTENHANCER-BASE-REFERENCE]`, stable-field digest). The mutable
  full `plan/swarm/TASKS.json` is never hashed or pinned.
- The v0 160-sample frame adapter is **not implemented**; this package models
  the documented 256-sample native chunk boundary only.

## Streaming semantics modelled

The surrogate mirrors only the documented interface and accounting bounds.

- Caches use the configuration-derived shapes `[1,256]`, `[1,256]`,
  `[1,24,36]`, `[1,24,36]` and `[1,24,36]`; their payloads are synthetic
  placeholders, not model tensors.
- Each 256-sample chunk returns the previous delayed chunk as `wav_out`; the
  first 256 output samples are invalid startup, matching the declared
  buffering delay. Two zero flush hops release the tail within the declared
  maximum of four calls and 640 samples.
- A 1,093-sample control returns 1,093 samples; a partial tail is not dropped.
- A chunk-aligned prefix of 15,360 samples is stable against the full stream.
  Processing two independently reset halves changes only the 256-sample
  boundary chunk, which is recorded rather than hidden.
- An impulse probe preserves the peak index exactly (`input=4000`,
  `output=4000`). No algorithmic lag, content delay, latency or device timing is
  measured; all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`.
- Reset zeroes every cache, clears the stream and replays bit-identically on a
  fresh epoch. Sessions are one stream per session; a second stream or a chunk
  after completion is rejected.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on a common full output length, peak/clipping/nonfinite
checks and explicit unmeasured fields. STOI is `blocked_unmeasured` (no
rights-cleared clean-reference cohort and no installed scorer), clean-speech
preservation is `synthetic_only`, state/memory is `synthetic_cache_shapes_only`,
content/availability timing is `blocked_unmeasured`, listening is `not_run`,
and real runtime/real clean references are `false`.

The synthetic table is generated by `report.json:synthetic_results`; no table
values are transcribed from Tiny, Small or author reports. No Base pilot exists,
so there is **no candidate metric, no candidate output** and no claim: the
scores describe only the surrogate. Author-reported family ranges and the
12-clip EARS Small screen remain labelled source-reported provenance.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_stream` is the documented chunk driver; the independent
  `surrogate_chunk_loop_control` must match it byte-for-byte.
- `surrogate_split_halves` must not match the whole stream; its boundary
  difference is a control, not a quality result.
- Config rejections: wrong model ID, sample rate, channels, sample format,
  native hop, FFT size, window, buffering delay or cache layout; unsupported
  asset mode; unavailable candidate asset; altered asset identity/byte count;
  and surrogate without opt-in. A fully pinned synthetic admission control is
  created to prove the admission branch; it is explicitly not the candidate and
  has `qualification_effect=none`.
- Stream rejections: empty, oversized, string, boolean, non-finite, infinite and
  out-of-range streams fail with unchanged state; a second stream and any
  post-close call fail closed.
- Chunk rejections: wrong length/type, non-finite and out-of-range chunks, wrong
  cache set/shape and non-finite/boolean cache values fail before state or cache
  mutation.
- Nonfinite input is never counted as silence; a missing asset never qualifies.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, pins, commands, gates. |
| `reference.py` | Deterministic signals, cache-shaped streaming surrogate, accounting, metrics and report/contract model. |
| `run.py` | Regenerates `report.json`, its sidecar, the README digest table, `contract.json` and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions, rights scope and pins. |
| `test_reference.py` | Deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README-digest, reproduction, disposition, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:adapters/fastenhancer/adapter.json` | `2a42cef166dc514488f4fdfe9b37c87427183444bcc19a2f6a4e96e77f87026b` | Adapter identity, tasks and offline mode. |
| `source:adapters/fastenhancer/README.md` | `32a856af0f7f32efb35b0b00c6551564f6383cf6446285c060294504cdf341ea` | Source commit, ONNX release, no separate model terms, evaluator environment. |
| `source:adapters/fastenhancer/run.py` | `7c34889410f7ac144d73f2c141686243e70ea057eeacd1e947917199fdebf50f` | Exact 256-hop streaming interface, cache handling and 256-sample alignment drop. |
| `source:adapters/fastenhancer/requirements.lock` | `1195f7e838fd20dc1fff30b3808324131c9f7acbedf63f9bf4084de78aa6a86c` | CPython 3.10 arm64 lock with `onnxruntime==1.20.1`. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Tiny/Small asset rows only; no Base artifact. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Candidate description and author-reported ranges. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | 30-pair DNS pilot provenance; no Base run. |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | Tiny/Small pilot completion and EARS/DNSMOS scope. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Candidate selection context. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Tiny/Small pilot values and live-chunk boundary. |
| `source:cpp-library/src/stages/fastenhancer.cpp` | `b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510` | Source-linked boundary constraints, inspected only. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:audio-benchmark-platform/audio-pro/docs/rights-register.md` | `e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44` | Rights summary with no Base entry. |
| `source:audio-benchmark-platform/audio-pro/inventory/rights-register.json` | `24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923` | Scoped rights records with no Base entry. |
| `source:data/checkouts/FastEnhancer/configs/fastenhancer/b.yaml` | `bbfa1a69c30828c6ed22634b3b2361f395457936e08fa774acfae2135956ba59` | Base model geometry and training settings. |
| `source:data/checkouts/FastEnhancer/docs/docs/onnx.md` | `ed05be57ea44917dbdc13d16ba47250424f901e7fbb78cb2ffd31217f137837c` | wav2wav chunk/delay semantics and default 512/256 settings. |
| `source:data/checkouts/FastEnhancer/models/fastenhancer/default/model.py` | `0e9b1ac34fe1725f7a09f53260b630360c38f8f185052bb37127e34957ec3380` | RNNFormer recurrent cache shapes and model forward path. |
| `source:data/checkouts/FastEnhancer/functional/audio_modules.py` | `6d474b3f2869182339b9f1d9f34c2076099e8ad7b1779c142cfd1b50a5acf8ae` | STFT/iSTFT cache initialization. |
| `source:data/checkouts/FastEnhancer/scripts/export_onnx.py` | `28d6758481c24dd8b4758e43bbf0624b3745d21fa7f998e8a263771795f72e04` | Named cache inputs/outputs in ONNX export. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Installed v0 boundary. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Installed v0 session boundary. |
| `worktree:REUSE.toml` / `LICENSES/Apache-2.0.txt` | `c6f61bc9…` / `cfc7749b…` | Licensing metadata and Apache-2.0 text. |

## Canonical artifacts and local digests

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself. The table below
is refreshed by `run.py --all` and checked by `verify.py`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `1d3615853411034e9e9f88c4c3cbf9a718efd2aa16da6d81ad11bd22ed4f3541` | 74883 |
| `report.json` | `ba25f77559d3b5d5166a0e0d813f02c3ac9ba9805bc8be7571418da1da7953a7` | 42671 |
| `report.json.sha256` | `518a5a011a98cc84d00cb9c99acf8514afcb63630f22bae4524d42e466e16d6f` | 78 |
| `run.py` | `737e3f2f00b6273036cd2d9e13c7d06f88be17f7ff2167a333580673aef1af79` | 6007 |
| `test_reference.py` | `8ad2a940226bebcd51933dc0f9dc58d690b16e62c66eb18af75a1f57c0a9105c` | 29589 |
| `verify.py` | `3d8fec8a0fc7d66213baa5b1e460b04683c14c03abb0e3e00de2e4ea3753702b` | 18632 |
<!-- DIGEST_TABLE_END -->

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C <worktree> diff --check
```

`run.py` and `verify.py` are deterministic and read no network, model or media
assets. Three cold-start regenerations are byte-identical and are checked by
the test suite and verifier.

## Remaining gates (all blocked, eight total)

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `rights_cleared_paired_cohort`
6. `independent_scoring_and_listening`
7. `target_runtime_timing`
8. `provider_intake_and_default_selection`
