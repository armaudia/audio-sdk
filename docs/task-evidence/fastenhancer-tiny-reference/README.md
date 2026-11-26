<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FASTENHANCER-TINY-REFERENCE — caller-supplied-asset blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`FastEnhancer Tiny reference` (`component_id=fastenhancer-tiny-reference`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline reference as a **caller-supplied external asset**
exactly as `CONTRACTS.md` `as_asset_v0` requires: asset ID, byte count, SHA-256
and `storage=external`, supplied by the caller, with no provider file access and
no download. It also records the exact documented streaming interface of the
pinned model contract. A deterministic stdlib **synthetic chunk surrogate**
exercises only the boundary, accounting and refusal mechanics; it is explicitly
opt-in, is not FastEnhancer, and substitutes for no gate.

No candidate artifact was downloaded, hashed, loaded, built, compiled, executed
or bundled. No weight, derived weight, ONNX graph, ONNX Runtime, native engine,
media, corpus, device clock, listener, benchmark or release artifact is present
or claimed. There is no candidate output or result. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build,
dependency lock, CI, board or handoff file changes. Only this task-local
directory is added.

## Exact external blocker

The pinned ledger and model contract identify the candidate exactly:
`data/models/fastenhancer/fastenhancer_t.onnx`, **125,233 bytes**, SHA-256
`a64663672b31bd1445502ee23328d291af13fb312e11bb574c010e7261a5ee7d`, source
revision `49ab55a57e3a064d94c6412cd0f0a383a55ca0f8` and release
`onnx-dns-v1.0.0`. Exact-digest private copies are retained elsewhere in the
workspace, but that does **not** make them SDK assets:

1. **The exact pinned runtime is absent.** `adapters/fastenhancer/requirements.lock`
   pins CPython 3.10 macOS arm64 with `onnxruntime==1.20.1` (wheel SHA-256
   `e50ba5ff7fed4f7d9253a6baf801ca2883cc08491f9d32d78a80da57256a5439`) and the
   adapter records `data/envs/dtln-onnx` as its evaluator environment. Neither
   is present. Only unrelated `onnxruntime` 1.31.1 installations exist. No
   exact-runtime reference run or parity vector was produced.
2. **The asset is not caller-supplied to the SDK.** The bytes are absent from
   this SDK worktree and were not supplied to any session. This package did not
   open, hash, load, compile or execute them. Possession and metadata inspection
   are not admission, runtime evidence or permission.
3. **Rights are evaluation-only.** The pinned rights register allows evaluation
   of the exact pinned Tiny16 asset and publication of aggregate benchmark
   scores, but acquisition, redistribution, customer deployment and public
   playback remain unknown. No separate model license or redistribution grant is
   documented, so no weight, derived weight, executable or output may be
   bundled, repackaged, exposed or redistributed.
4. **No exact reference parity exists.** The present native fixture records
   fabricated deterministic weights with no model bytes read and marks
   `model_parity=deferred` and `model_quality=not_assessed`. There is no exact
   model output under the pinned runtime, no rights-cleared paired real cohort,
   no independent scorer or listening result, and no target pacing, deadline or
   memory measurement. All eight release gates stay `blocked`.

**Reopen condition.** Admit the candidate only when the exact
`fastenhancer_t.onnx` bytes are supplied as a caller-owned external asset with an
immutable revision, byte count and SHA-256; the pinned `onnxruntime==1.20.1`
artifact with a recorded digest installs in the intended environment and its
terms are documented; written redistribution, customer-deployment and
public-playback decisions exist; and approved exact-runtime reference outputs,
a rights-cleared cohort, independent scoring/listening and target timing are
available. Until then no result may qualify the candidate.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- The candidate model's documented native geometry is quoted, not executed:
  512-point periodic-Hann STFT, 256-sample hop, 257 spec bins, 24 channels,
  16-frame recurrent state of width 20, four graph caches, 256-sample buffering
  delay, 256 invalid startup samples, two flush hops, and a finite drain bound of
  four calls / 640 samples.
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
  (`tasks[id=SDK-FASTENHANCER-TINY-REFERENCE]`, stable-field digest). The mutable
  full `plan/swarm/TASKS.json` is never hashed or pinned.
- The v0 160-sample frame adapter is **not implemented**; this package models
  the documented 256-sample native chunk boundary only.

## Streaming semantics modelled

The surrogate mirrors only the documented interface and accounting bounds.

- Caches use the documented shapes `[1,256]`, `[1,256]`, `[1,16,20]` and
  `[1,16,20]`; their payloads are synthetic placeholders, not model tensors.
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

### Synthetic fixture results (not a candidate result)

Scores describe the surrogate only and are not transferable to FastEnhancer.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 6.953471 | 7.293569 | +0.340098 | 6.961875 | 6.897386 | -0.064489 | -2.946784 |
| quiet_speech | 4.553064 | 5.801635 | +1.248571 | 4.533636 | 4.500798 | -0.032838 | -2.946643 |
| low_snr_speech | -5.176332 | -2.432933 | +2.743399 | -5.230262 | -5.225992 | +0.004271 | -2.960651 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -2.960802 |
| onset_offset | 3.218529 | 4.838534 | +1.620005 | 3.175917 | 3.142612 | -0.033305 | -2.966405 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is about 0.498. These figures are generated by `report.json`; the table is
documentation of that same synthetic run.

### Honest regressions

Small SI-SDR regressions versus the noisy control are recorded verbatim in
`report.json:regressions` for `active_speech`, `quiet_speech` and
`onset_offset`. The causal previous-chunk noise proxy slightly distorts
low-energy speech, so SI-SDR falls even while SNR improves. These are properties
of the synthetic fixture, not evidence about FastEnhancer, and no threshold was
tuned against real data.

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
- Nonfinite input is never counted as silence; missing assets never qualify.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
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
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset digest, byte count, source revision and model terms. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Candidate description and author-reported ranges. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | 30-pair DNS pilot provenance. |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | Tiny/Small pilot completion and EARS/DNSMOS scope. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | Candidate selection context. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Tiny pilot ΔSI-SDR/ΔSTOI/RTF and "live chunk behavior not established". |
| `source:cpp-library/src/stages/fastenhancer.cpp` | `b0c0ffc33e5c1c87f65ae9c82ea61ee2c91f4ec9ab16af9393c04376ad931510` | Source-linked boundary constraints, inspected only. |
| `source:audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16/model-contract.json` | `1af99b0085289d2cc21772462f6aa9159750946d7c742a197e636cf392240a4a` | Exact graph interface, timing fields and asset digest. |
| `source:audio-benchmark-platform/audio-pro/docs/rights-register.md` | `e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44` | Evaluation-only rights summary. |
| `source:audio-benchmark-platform/audio-pro/inventory/rights-register.json` | `24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923` | Scoped rights record and 2026-11-15 attestation. |
| `source:audio-benchmark-platform/audio-pro/processors/fastenhancer_tiny16_native_f32/tests/fixture_trace.json` | `cf5eac8219d4285b13400dc0c3050b159edb146abadce073e92725a46adb0a01` | Fabricated-weight native trace with `model_parity=deferred`. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |

## Canonical artifacts and local digests

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself. The table below
is refreshed by `run.py --all` and checked by `verify.py`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `bcc041cd512cf13388c2be45a5914ae401918a93194b3097fb3fbf9c5b686d46` | 73663 |
| `report.json` | `20f007a5dc330b0dd437e38bc179c9aad19f6ba60b5ecabb854a6ca722488cbe` | 42104 |
| `report.json.sha256` | `7ea029dcc95e4633ba2f37c2833dd4b9bc90b44518a8be28ca7a9e0676c4b266` | 78 |
| `run.py` | `a405ff4f7986d65e1fcbd04360483594a03facb9918c995c8920883658ce0899` | 6007 |
| `test_reference.py` | `14d87f2e57d8e914849b8336e3c8275659e6464c80813d784ef23b91f96f39ec` | 29269 |
| `verify.py` | `01d6a2d2e2558fb66de2f18efd75cbe121d310ba8ea26824954b41509d2b1e08` | 18677 |
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

## Remaining gates (all blocked, eight total)

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `rights_cleared_paired_cohort`
6. `independent_scoring_and_listening`
7. `target_runtime_timing`
8. `provider_intake_and_default_selection`
