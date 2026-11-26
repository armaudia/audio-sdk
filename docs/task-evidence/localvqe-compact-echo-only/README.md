<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LOCALVQE-COMPACT-ECHO-ONLY — caller-supplied-asset blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LocalVQE compact echo-only` (`component_id=localvqe-compact-echo-only`). The
acceptance profile is **Room**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`, `release_gate_count=8`. Missing evidence
never qualifies a candidate.

This package models the exact LocalVQE compact **echo-only** boundary as a
**caller-supplied asset** at 16 kHz mono with synchronized microphone and
far-end render frames, 256-sample (16 ms) hops, `float32` input and one
256-sample (16 ms) algorithmic output delay. The echo-only checkpoint performs
acoustic echo cancellation only; it retains noise and room sound, so this
package adds no noise-suppression or dereverberation stage and does not pool
the result with the compact full-enhancement sibling.

The pinned Apache-2.0 **source checkout and the hash-matching native library are
present**, but the exact **echo-only GGUF weights are absent**. No model,
weight, corpus or runtime is downloaded, copied, vendored, imported, loaded or
executed. The package executes a **stdlib-only deterministic model-free
paired-reference surrogate** and records a strict readiness conclusion. It is
**not LocalVQE**, does not read audio, does not measure a device clock, does
not conduct listening, does not benchmark the SDK and makes no release or
quality claim. Only this task-local directory is added.

## Exact blocker

The exact upstream identity is pinned: `localai-org/LocalVQE`, source revision
`7f61cd05095d42e56a135b303f5bb4d761da22b9`, `Apache-2.0` source `LICENSE`
SHA-256 `84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54`.
The compact echo-only model is `localvqe-pi-aec-v1-49k-f32.gguf` with SHA-256
`b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8`. It is
**absent** at `data/models/localvqe/localvqe-pi-aec-v1-49k-f32.gguf`; the
compact full-enhancement sibling `localvqe-pi-v1-49k-f32.gguf` (SHA-256
`0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26`) is
absent too, and no isolated environment exists at
`data/envs/localvqe-compact-echo-only`.

The native library `liblocalvqe.0.1.0.dylib` is present at
`data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib` and its SHA-256
matches `bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298`.
It was hashed as identity only; it was **not loaded or executed**. The source
checkout reports a modified `ggml/vendor/ggml` submodule, so clean build
provenance is not verified. Exact weights are still required for any real run,
and library presence plus hash alone is not exact-runtime evidence.

The source and model repository are described as Apache-2.0 upstream, but
artifact-specific model terms, training-data provenance, redistribution,
product-use and legal review remain unresolved. Nothing was copied, vendored,
built, downloaded, imported, loaded, executed or redistributed. The open
blockers are recorded verbatim in `contract.json:exact_blockers` and
`report.json:exact_blockers`; every release gate remains `blocked`.

## Boundary model

- The pinned research adapter declares a stateful native
  `localvqe_process_frame_f32` call on **256-sample / 16 ms** hops with
  aligned, equal-length 16 kHz mono microphone and far-end playback frames.
  LocalVQE adds **one hop (256 samples, 16 ms)** of algorithmic output latency;
  this package models that delay and compensates it before scoring.
- Installed SDK v0 remains 16 kHz mono `f32`, **160 samples**. The cadence
  divergence is recorded; no numeric parity with the real runtime is claimed
  and no installed geometry, default, ABI, contract, registry, descriptor,
  shared build or CI file changes.
- The task-local caller asset contract requires exactly `model_path`,
  `model_sha256`, `library_path`, `library_sha256`, `source_commit`, `variant`,
  `sample_rate_hz`, `channels`, `frame_samples`, `input_format`,
  `render_delay_samples` and `algorithmic_latency_samples`. It pins
  `compact-echo-only`, 16 kHz, mono, 256 samples, `float32`, zero render delay
  and one 256-sample output hop. A manifest is accepted only when both paths
  are absolute and present, both SHA-256 values match the files, and
  geometry/commit/variant/delay match. Validation never loads or executes the
  model or library. Missing, relative, hash-mismatched, wrong-geometry,
  wrong-variant, wrong-delay or extra-field manifests fail closed before
  processing. A hash-matched placeholder is **never** accepted as the pinned
  model: pinned identity is checked separately and rejects
  `model_hash_not_pinned`, while the workspace pinned asset rejects as
  `asset_file_missing:model_path`. The compact full-enhancement variant is
  rejected as the echo-only sibling.
- The model is a **separate caller asset**; weights are not embedded in the
  SDK or the runtime. `weights_embedded=false` and
  `separate_model_archive_required=true`.
- The surrogate is a deterministic, non-adaptive, model-free paired-reference
  echo-only operator: a fixed 5-tap echo replica at the frozen 512-sample
  primary path, 0.85 residual subtraction and one 256-sample output delay.
  There is **no** noise gate, smoothing, noise-suppression stage or
  dereverberation stage. It is **not LocalVQE**, has no neural network,
  checkpoint or weights, and its synthetic ERLE and near-reference SNR are
  uncalibrated boundary observations.
- The fixture is a frozen 4-second stream (64000 samples, 250 hops) with a
  known exact decomposition `mic = echo + near + noise`, a primary render path,
  a secondary path after sample 45056, a quiet near-only stratum, echo-only,
  overlap, render-tail, silence and movement strata. No real audio or measured
  room is used.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Frozen render/reference | Frozen synthetic 5-tap primary and secondary paths; no measured RIR claimed |
| Channel/rate/hop | 16 kHz mono `float32`, 256-sample hop, 250 hops |
| Excitation | Deterministic two-tone render and near components plus LCG noise |
| Delay | Declared 256-sample / 16 ms output delay; aligned and unaligned scoring |
| Movement | Secondary path after sample 45056; pre/post ERLE split |
| Noise | Frozen noise amplitudes across near, overlap, tail and silence strata |
| Reset schedule | Reset to epoch 4 matches a fresh session bit-for-bit |
| Echo-only | `echo-only-a` and `echo-only-b-change` strata |
| Near-end-only | `near-only-quiet` and `near-only-a` strata |
| Overlap | `overlap-a` and `overlap-b-noisy` strata |
| No-reference | Zero-render probe, independently compared with identity |
| Echo attenuation | Pooled echo-only ERLE with pre/post movement values |
| Near-end preservation | Near-reference SNR, SI-SDR and RMS ratio against the known near component |
| Nonfinite failures | Zero nonfinite outputs; injected nonfinite inputs rejected |
| Alignment, delayed/missing render | Delay-compensated scoring; delayed/missing render failure controls |
| No-reference independent comparison | Zero-reference ERLE and near-SNR versus identity, labeled misuse |

Also verified: fail-closed caller-asset, frame, config and render controls;
partial-tail padding; reset independence; and offline/streaming parity with
160/480/800/320/256/137/641-sample chunk buffering. No missing, stale, unrun or
blocked result is promoted to a pass or used to qualify the candidate.

## Method

1. `reference.py` synthesises 64000 samples (4 s) from integer arithmetic: a
   fixed 64-entry waveform table, a deterministic LCG noise source and a frozen
   segment table. Every sample is quantised to int16 and exposed as
   `float32 / 32768`. Every segment boundary is a multiple of 256 samples, and
   render-tail guard strata keep echo tails out of the scored near-end strata.
2. Twelve frozen strata cover silence, echo-only, render tail, quiet
   near-only, near-only, overlap, echo-only with a path change, noisy overlap,
   render tail and silence. The exact decomposition is retained for scoring.
3. `reference.Session` drives one 256-sample paired frame at a time. The first
   output hop is the declared delay; the final input hop is unavailable until
   after the stream ends and is never scored. Each frame records source
   coordinates, valid/padded samples, RMS, finite output and state.
4. The same module compensates the one-hop delay, computes pooled and
   stratified echo attenuation on echo-only regions, near-reference SNR and
   SI-SDR on near-only/overlap regions, alignment gain, peaks, and nonfinite
   counts. Identity is scored on the same strata as the mandatory paired
   control.
5. `run.py` builds the contract, report and sidecar three times from cold start
   and requires byte-identical payloads before writing `report.json`,
   `report.json.sha256`, `SOURCES.sha256` and the README digest tables.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Single stdlib-only module: deterministic paired-reference stimuli, echo-only surrogate, Room scorer, strict parsers and canonical report/contract builders. |
| `run.py` | Regenerates `contract.json`, `report.json`, `report.json.sha256`, README digest tables and `SOURCES.sha256` with 3× cold-start equality. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, eight gates, invariants. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verification. |
| `SOURCES.sha256` | SHA-256 manifest for all source and task-local files. |
| `*.license` | REUSE sidecars for JSON and manifest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite. The source checkout
revision is pinned as `7f61cd05095d42e56a135b303f5bb4d761da22b9`; the three
source files below pin the license, README and public C API header exactly.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:adapters/localvqe-aec/README.md` | `61240419dc9d46af2056316f2a7167b833fb80e9d6a4ce8470b94a8cde488cd1` |
| `source:adapters/localvqe-aec/run.py` | `c4b8b5077e01bf8b7b736ea2e784087a6e811e5aec54f18c922dcda8a240fb5a` |
| `source:adapters/localvqe/README.md` | `b964486bb1f823f9ce6ad52b10210d04b596a8642bda5b46aedb0532eea808e0` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/joint-aec-profile/report.md` | `d3d9b2d0c03245cb1b4f6e11a18093393fc9ed6e11076c32cb94f3aed7f4d7ad` |
| `source:cpp-library/pipeline-validation/run_aec_denoise.py` | `f6242f3af34d331996b114d537ebf99ed3d86507508a92003b94dfcca4d17336` |
| `source:data/checkouts/LocalVQE/LICENSE` | `84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54` |
| `source:data/checkouts/LocalVQE/README.md` | `2eeed279c971cce67f7897ae51bc9c8552c0e88bdd715d27520f956262d2423c` |
| `source:data/checkouts/LocalVQE/ggml/localvqe_api.h` | `ef2871bde8cd8fe9aa8cd5c3b7d11cc72efb7bb1cc29f726522ace87ad490877` |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The digest below is the file digest, the canonical digest
and the sidecar digest. `SOURCES.sha256` pins every artifact and this README;
it does not pin itself.

<!-- digest-table: artifacts -->
| Key | SHA-256 |
| --- | --- |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `contract.json` | `c44d9325733467e7668869c2c228d533a384189ed77bdf4821e40d544fd66f85` |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `reference.py` | `a1f401f574e78c8f58cf27f5ca0f78d68c3572dacdee40e09da503ab45714c2a` |
| `report.json` | `28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369` |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `report.json.sha256` | `5abba7a30d5864fb2e127ec0bcb3c62626fcb27e9aadb8ffe862d4d7cd5ac606` |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `run.py` | `0f6d8891dfb079daba880912047a563edb1a0c21f16f97b0abbba61430fdf4ee` |
| `test_reference.py` | `5ae8f39ed701eaec7a97c4c752f67e5aa7668fd8de3c73469581166299ec5a87` |
| `verify.py` | `ab065964aec14a1e9b14b6f4c5c3a6302c8fb8786165d01fb8230698c974fbdb` |
<!-- digest-table: end -->

## External asset identity (expected, absent)

These values are recorded identity only. The echo model and full sibling paths
are checked for absence: if either appears, this evidence package is stale and
must reopen. Nothing in this table is downloaded, copied, imported, loaded or
executed.

<!-- digest-table: external-absent -->
| Key | SHA-256 |
| --- | --- |
| `asset:echo_model` | `b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8` |
| `asset:full_model` | `0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26` |
<!-- digest-table: end -->

## External runtime identity (present, hash-matched, not executed)

The native library is present and its SHA-256 matches the pin. It was hashed as
identity only; it was not loaded or executed, and its build provenance is not
verified.

<!-- digest-table: external-runtime -->
| Key | SHA-256 |
| --- | --- |
| `asset:native_library` | `bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298` |
<!-- digest-table: end -->

## Reproduction

All outputs are task-local. Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LOCALVQE-COMPACT-ECHO-ONLY
TASK=$WT/docs/task-evidence/localvqe-compact-echo-only
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
python3 -m reuse lint
git diff --check
```

`run.py` is deterministic and reads no network, model, media or device asset.
No board, handoff, installed-package or shared SDK state is written.

## Results (synthetic boundary surrogate only)

The surrogate is a conformance fixture, not LocalVQE and not a quality result.
Echo attenuation is measured only on echo-only samples after compensating the
declared one-hop delay. Near-end preservation is measured against the known
synthetic near component; identity is the mandatory paired control. Because the
echo-only path has no noise-suppression or dereverberation stage, near-only
output matches identity by construction; overlap improves only through echo
subtraction.

| Metric | Exact value |
| --- | ---: |
| Echo-only ERLE, `echo-only-a` | 16.474323833421 dB |
| Echo-only ERLE, pooled pre-movement | 16.471491808227 dB |
| Echo-only ERLE, pooled post-movement | 2.647171469148 dB |
| Movement ERLE drop | 13.824320339079 dB |
| Echo-only ERLE, all echo-only samples | 8.388657449989 dB |
| Near SNR, `near-only-quiet` (identity) | 19.475314536573 dB (19.475314536573 dB) |
| Near SNR, `near-only-a` (identity) | 41.750877114473 dB (41.750877114473 dB) |
| Near SNR, `overlap-a` (identity) | 15.544038242969 dB (−0.910768422051 dB) |
| Near SNR, `overlap-b-noisy` (identity) | 5.155602478546 dB (2.654789797802 dB) |
| Near SNR, pooled near (identity) | 11.499400801413 dB (2.560397946542 dB) |
| Overlap SI-SDR, `overlap-a` | 15.544582430949 dB |
| Aligned vs unaligned overlap SNR | 15.544038242969 / −5.668228491358 dB |
| Alignment gain | 21.212266734327 dB |
| Max absolute output | 0.599232681274 |
| Clipped / nonfinite samples | 0 / 0 |

The quiet near-only RMS ratio is 1.002210998161 and the normal near-only ratio
is 1.000059768464: the echo-only surrogate does not gate or smooth the near
component. Overlap RMS ratios are 1.013915505227 (`overlap-a`) and
1.137268071955 (`overlap-b-noisy`), reflecting residual echo and noise, not
added enhancement. These are surrogate behavior observations, not LocalVQE
results.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a valid generic manifest validates both hashes and the
  geometry but reports `loaded=false`, `executed=false`, `imported=false`.
  Missing, absent-file, relative-path, model-hash, library-hash,
  wrong-commit, 48 kHz, stereo, 512-sample, `int16`, `compact-full`-variant,
  render-delay-256, latency-0 and extra-field manifests are rejected. The
  workspace pinned model manifest is rejected as `asset_file_missing`, and a
  hash-matched placeholder with the pinned digest is rejected as
  `asset_model_hash_mismatch`; a placeholder is never accepted as the pinned
  model.
- **Frame adverse:** NaN, Inf, 128-sample nonfinal, 257-sample, empty,
  out-of-range, boolean-bearing and ref-length-mismatch frames are rejected
  with the state digest unchanged. A final 128-sample partial frame is padded
  to 256, accepted with end coordinate 384, and its pending tail is drained
  separately (not scored).
- **Config adverse:** 48 kHz, 2 channels, `s16`, 320-sample frames,
  `compact-full` variant, zero algorithmic latency, nonzero render delay,
  `real_runtime=true`, model-or-library-used, empty session id, negative epoch
  and boolean epoch are rejected.
- **Delayed render:** shifting the render reference by one hop lowers
  echo-only ERLE from 16.474323833421 dB to −4.726205898953 dB, a
  21.200529732374 dB collapse. Recorded as a failure, not a pass.
- **Missing render:** a zero render reference leaves echo-only ERLE at
  0.0 dB, a 16.474323833421 dB collapse. This is the independent no-reference
  comparison: on `overlap-a` the zero-reference output near SNR is
  −0.910768422051 dB, identical to identity, so it does not damage near-end
  there, but it provides no echo attenuation. Labeled misuse, not a suppressor
  pass.
- **Movement:** the fixed surrogate path does not adapt after sample 45056;
  ERLE drops from 16.471491808227 dB to 2.647171469148 dB. Recorded as a
  regression.
- **Reset:** resetting to epoch 4 reproduces a fresh epoch-4 session
  bit-for-bit and leaves a second session unchanged; epoch-3 and epoch-8 state
  digests differ.
- **Streaming:** arbitrary 160/480/800/320/256/137/641-sample chunks produce
  byte-identical output to offline framing; the final hop is unavailable until
  stream end and is never scored.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Release gates (all eight blocked)

1. `exact_echo_asset_identity`
2. `model_and_runtime_rights`
3. `exact_runtime_reproduction`
4. `streaming_boundary_and_one_hop_latency`
5. `rights_cleared_paired_reference_cohort`
6. `room_echo_near_overlap_no_reference_acceptance`
7. `target_runtime_timing_memory`
8. `provider_intake_and_default_selection`

`report.json:release_gates` and `contract.json:release_gates` carry the exact
evidence and reopen condition for each. Reopen only when a caller supplies
`localvqe-pi-aec-v1-49k-f32.gguf` with matching SHA-256 and provenance
revision; model, training-data, library, redistribution and product-use rights
are cleared; the exact runtime and an approved paired-reference output vector
are reproduced; the native 16 kHz / 256-sample paired-reference streaming
boundary, one-hop delay, partial-tail, reset/flush and offline/streaming parity
are verified; a rights-cleared paired cohort is scored under the Room profile
with echo-only, near-only, overlap, movement, delayed/missing render and
no-reference comparisons; target timing/memory is measured; opt-in provider
intake and descriptor/registry review are complete; and a public default
decision is recorded. Until then the candidate stays DEFER, incomplete and not
qualified.

## Board identity and separation

The board is referenced by **stable linked-row identity only**
(`tasks[id=SDK-LOCALVQE-COMPACT-ECHO-ONLY]`; stable-field digest over `id`,
`component`, `repository` and `claim.branch`). The mutable full
`plan/swarm/TASKS.json` is **never hashed or pinned**.

The compact full-enhancement sibling (`SDK-LOCALVQE-COMPACT-FULL`), the
zero-reference dereverberation probe and the classical AEC packages are
separate tasks with their own fixtures, scorers, cadences and dispositions.
This package does not import, reuse, pool or reinterpret their outputs,
metrics, adapters or reports. The echo-only checkpoint is never pooled with the
compact full result. The research adapter at `adapters/localvqe-aec/` is pinned
provenance only; it is not present in the SDK worktree, not installed, imported
or executed, and not changed.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_cmakelists_change=false`, `processor_exposure=false`, `ci_change=false`.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  LocalVQE provider is installed or registered.
- No request is ever processed as LocalVQE. Valid candidate requests fail
  closed because the exact asset identity and runtime execution are absent.
- No proposal `adapter.json` or `readiness.json` is added; machine-readable
  state lives in `contract.json` and `report.json`.
