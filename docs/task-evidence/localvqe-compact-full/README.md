<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LOCALVQE-COMPACT-FULL — LocalVQE compact full caller-supplied-asset boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LocalVQE compact full` (`component_id=localvqe-compact-full`). The acceptance
profile is **Room**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package models the exact LocalVQE compact full-enhancement boundary as a
**caller-supplied asset** at 16 kHz mono with synchronized microphone and
far-end render frames, 256-sample (16 ms) hops, `float32` input and one
256-sample (16 ms) algorithmic output delay. The compact full checkpoint is
jointly trained for **echo cancellation, noise suppression and
dereverberation**, so the boundary is explicitly not a pure noise-only or
pure dereverberation candidate. Because the pinned model, its artifact rights
and an isolated runtime are unavailable, the package executes a
**stdlib-only deterministic synthetic surrogate** and records a strict
readiness conclusion. It is **not LocalVQE source**, does not import or load a
model, weight, GGML library or runtime, does not download or vendor anything,
does not read audio, does not measure a device clock, does not conduct
listening, does not benchmark the SDK and makes no release or quality claim.
Only this task-local directory is added.

## Exact blocker

The exact upstream identity is pinned: `localai-org/LocalVQE`, source revision
`7f61cd05095d42e56a135b303f5bb4d761da22b9`, `Apache-2.0`. The compact full
model is `localvqe-pi-v1-49k-f32.gguf` with SHA-256
`0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26`; the
parallel echo-only checkpoint is `localvqe-pi-aec-v1-49k-f32.gguf` with SHA-256
`b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8`; the
native library is `liblocalvqe.0.1.0.dylib` with SHA-256
`bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298`. The
**model files are absent** from
`data/models/localvqe/`, and no isolated environment exists at
`data/envs/localvqe-compact-full`. The exact runtime cannot be loaded or
reproduced here. The native library path was not read, hashed, loaded or
executed by this package; observed presence alone is not exact-runtime
evidence.

The source and model repository are described as Apache-2.0 upstream, but
artifact-specific model terms, training-data provenance, redistribution,
product-use and legal review remain unresolved. Nothing was copied, vendored,
built, downloaded, imported, loaded, executed or redistributed.

The open blockers are recorded verbatim in `contract.json:exact_blockers`,
`report.json:exact_blockers` and `readiness.json:exact_blocker`. Every release
gate remains `blocked`.

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
  `compact-full`, 16 kHz, mono, 256 samples, `float32`, zero render delay and
  one 256-sample output hop. A manifest is accepted only when both paths are
  absolute and present, both SHA-256 values match the files, and
  geometry/commit/variant/delay match. Validation never loads or executes the
  model or library. Missing, relative, hash-mismatched, wrong-geometry,
  wrong-variant, wrong-delay or extra-field manifests fail closed before
  processing. A hash-matched placeholder is **never** accepted as the pinned
  model: pinned identity is checked separately and rejects
  `model_hash_not_pinned`, while the workspace pinned asset rejects as
  `asset_file_missing:model_path`.
- The model is a **separate caller asset**; weights are not embedded in the
  SDK or the runtime. `weights_embedded=false` and
  `separate_model_archive_required=true`.
- The surrogate is a deterministic, non-adaptive, model-free paired-reference
  boundary operator: a fixed 5-tap echo replica at the frozen 512-sample
  primary path, 0.85 residual subtraction, a per-hop RMS Wiener gate with floor
  0.02, a one-pole smoother at 0.35 and one 256-sample output delay. It is
  **not LocalVQE**, has no neural network, checkpoint or weights, and its
  synthetic ERLE and near-reference SNR are uncalibrated boundary observations.
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
| Near-end damage | Near-reference SNR, SI-SDR and RMS ratio against the known near component |
| Nonfinite failures | Zero nonfinite outputs; injected nonfinite inputs rejected |
| Alignment, delayed/missing render | Delay-compensated scoring; delayed/missing render failure controls |
| No-reference independent comparison | Zero-reference ERLE and near-SNR versus identity, labeled misuse |

Also verified: fail-closed caller-asset, frame, config and render controls;
partial-tail padding; reset independence; and offline/streaming parity with
160/480/800/320/256/137/641-sample chunk buffering. No missing, stale, unrun or
blocked result is promoted to a pass or used to qualify the candidate.

## Method

1. `fixture.py` synthesises 64000 samples (4 s) from integer arithmetic: a
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
   coordinates, valid/padded samples, RMS, gate value, finite output and state.
4. `scorer.py` compensates the one-hop delay, computes pooled and stratified
   echo attenuation on echo-only regions, near-reference SNR and SI-SDR on
   near-only/overlap regions, alignment gain, peaks, and nonfinite counts.
   Identity is scored on the same strata as the mandatory paired control.
5. `run.py` builds the report three times and requires byte-identical payloads
   before writing `report.json` and `report.json.sha256`.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `fixture.py` | Deterministic paired-reference stimuli, frozen paths and strata. |
| `scorer.py` | Room-profile echo, near-end, alignment, peak and nonfinite scoring. |
| `reference.py` | Session, surrogate, controls, canonical report/contract/readiness builders, strict parsers. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | 89 deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verification. |
| `requirements.lock` | Pinned CPython 3.12.16; standard library only, no third-party runtime. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all source and task-local files. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

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
| `LICENSES.md` | `68d9d83eb0fc56d12064e7047c1fd5fef0f4a4dcaab75a789972c16766873187` |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `adapter.json` | `32e1a0ad05f25ce97cb77585083d49adeee80de59ca50310b32135e02decdb8e` |
| `adapter.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `contract.json` | `32e9d371ccf72edcdc1619ee0db3149323e20296a7b853b6ee9ac8a95b0054e7` |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `fixture.py` | `6dd57e938b694cf1cf5308864d79f2d2e3bd8850873e3e75eec525c849d2d8a7` |
| `readiness.json` | `762dc430ce4b4153ab46ed048c00222b4dce461488d0d280ad38293787b5e623` |
| `readiness.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `reference.py` | `1230fb8d127ed1db50987aba92098e87f0e498c7d77581977ca253c1604613ed` |
| `report.json` | `08c75119706877d323fdb4299f53b274f86c6ab27f7a683d8764cc61a1a73f4a` |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `report.json.sha256` | `b001f26bab2bfbb81bf6afaab4e6a50853e68f68e9d1476af047a62b764646c4` |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `requirements.lock` | `106f80f1b66883c20b328592f2164828606a087ce8855df2c607e003f74bab17` |
| `requirements.lock.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `run.py` | `4d82d80ed9bc6529e13f3072b33a7d50910221eacc8932ff581fa05861303ab8` |
| `scorer.py` | `d77678211fb3fb369b0b299f900281bef4cae10dde1bafc07ae74dc09537ba32` |
| `test_reference.py` | `e69b7884562898ff5d59fc36719fb909c1c127da0358483af297173ad4b4049c` |
| `verify.py` | `c164fffd075372aa0a36aeade95b24e1b1c38751055cae49d2871ffa449adb6f` |
<!-- digest-table: end -->

## External asset identity (expected, absent or pinned)

These values are recorded identity only. The full and echo model paths are
checked for absence: if either appears, this evidence package is stale and must
reopen. The native library path is recorded as expected identity; it is not
read, hashed, loaded or executed, and its presence is not exact-runtime
evidence. Nothing in these tables is downloaded, copied, imported, loaded or
executed.

<!-- digest-table: external-absent -->
| Key | SHA-256 |
| --- | --- |
| `asset:echo_model` | `b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8` |
| `asset:full_model` | `0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26` |
<!-- digest-table: end -->

<!-- digest-table: external-runtime -->
| Key | SHA-256 |
| --- | --- |
| `asset:native_library` | `bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298` |
<!-- digest-table: end -->

## Reproduction

All outputs are task-local. Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LOCALVQE-COMPACT-FULL
TASK=$WT/docs/task-evidence/localvqe-compact-full
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/localvqe-compact-full-ci
python3 -m reuse lint
git diff --check
```

Local results: `run.py` regenerated the report; the package tests passed
**89/89**; `verify.py` printed `PASS`; `python3 -m reuse lint` passed;
`git diff --check` was clean. The pinned installed-package `scripts/ci.py`
gate passed: repository unittest 52/52, API CTest 1/1, native CTest 11/11,
external CTest 14/14, fixture off/on 1/1 each, installed Python wheel 5/5, and
both release archive gates refused the missing-Speex catalog as expected.

## Results (synthetic boundary surrogate only)

The surrogate is a conformance fixture, not LocalVQE and not a quality result.
Echo attenuation is measured only on echo-only samples after compensating the
declared one-hop delay. Near-end preservation is measured against the known
synthetic near component; identity is the mandatory paired control.

| Metric | Exact value |
| --- | ---: |
| Echo-only ERLE, `echo-only-a` | 18.957225896943 dB |
| Echo-only ERLE, pooled pre-movement | 18.968770162789 dB |
| Echo-only ERLE, pooled post-movement | 2.941218027271 dB |
| Movement ERLE drop | 16.027552135518 dB |
| Echo-only ERLE, all echo-only samples | 8.893315281925 dB |
| Near SNR, `near-only-quiet` (identity) | 5.030926376592 dB (19.475314536573 dB) |
| Near SNR, `near-only-a` (identity) | 25.067248368652 dB (41.750877114473 dB) |
| Near SNR, `overlap-a` (identity) | 15.435723783439 dB (−0.910768422051 dB) |
| Near SNR, `overlap-b-noisy` (identity) | 5.334473260565 dB (2.654789797802 dB) |
| Near SNR, pooled near (identity) | 11.542809605694 dB (2.560397946542 dB) |
| Overlap SI-SDR, `overlap-a` | 15.335121970075 dB |
| Aligned vs unaligned overlap SNR | 15.435723783439 / −5.590693993359 dB |
| Alignment gain | 21.026417776798 dB |
| Max absolute output | 0.591328567152 |
| Clipped / nonfinite samples | 0 / 0 |

The quiet near-only stratum shows material near-end damage from the crude
fixed gate and smoother: its output near SNR is 5.03 dB versus identity's
19.48 dB and its RMS ratio is 0.470947645512. The normal near-only stratum is
25.07 dB versus identity's 41.75 dB (RMS ratio 0.987457481391). In overlap the
joint echo/noise stages improve near-reference SNR over identity, but the
surrogate does not preserve the near component as well as identity on
near-only speech. These are surrogate behavior observations, not LocalVQE
results.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a valid generic manifest validates both hashes and the
  geometry but reports `loaded=false`, `executed=false`, `imported=false`.
  Missing, absent-file, relative-path, model-hash, library-hash,
  wrong-commit, 48 kHz, stereo, 512-sample, `int16`, echo-only-variant,
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
- **Config adverse:** 48 kHz, 2 channels, `s16`, 320-sample frames, zero
  algorithmic latency, nonzero render delay, `real_runtime=true`,
  model-or-library-used, empty session id, negative epoch and boolean epoch are
  rejected.
- **Delayed render:** shifting the render reference by one hop lowers
  echo-only ERLE from 18.957225896943 dB to −4.683002706048 dB, a
  23.640228602991 dB collapse. Recorded as a failure, not a pass.
- **Missing render:** a zero render reference leaves echo-only ERLE at
  0.098910701903 dB, an 18.85831519504 dB collapse. This is the independent
  no-reference comparison: on `overlap-a` the zero-reference output near SNR is
  −0.846096135092 dB versus identity's −0.910768422051 dB, so it does not
  damage near-end more than identity there, but it provides essentially no echo
  attenuation. Labeled misuse, not a suppressor pass.
- **Movement:** the fixed surrogate path does not adapt after sample 45056;
  ERLE drops from 18.968770162789 dB to 2.941218027271 dB. Recorded as a
  regression.
- **Reset:** resetting to epoch 4 reproduces a fresh epoch-4 session
  bit-for-bit and leaves a second session unchanged; epoch-3 and epoch-8 state
  digests differ.
- **Streaming:** arbitrary 160/480/800/320/256/137/641-sample chunks produce
  byte-identical output to offline framing; the final hop is unavailable until
  stream end and is never scored.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Gates and reopen conditions

The package records ten blocked gates: caller model present/verified,
model-and-runtime rights, exact runtime reproduction, streaming boundary and
one-hop latency, rights-cleared paired cohort, echo/near/overlap/no-reference
acceptance, target-runtime timing/memory, opt-in adapter intake,
descriptor/registry review, and public default selection. `readiness.json` is
the concise strict conclusion; `report.json:gates` and `contract.json:gates`
carry the exact reopen condition for each.

Reopen only when a caller supplies `localvqe-pi-v1-49k-f32.gguf` with matching
SHA-256 and provenance revision; model, training-data, library, redistribution
and product-use rights are cleared; the exact runtime and an approved
paired-reference output vector are reproduced; the native 16 kHz / 256-sample
paired-reference streaming boundary, one-hop delay, partial-tail, reset/flush
and offline/streaming parity are verified; a rights-cleared paired cohort is
scored under the Room profile with echo-only, near-only, overlap, movement,
delayed/missing render and no-reference comparisons; target timing/memory is
measured; opt-in intake and descriptor review are complete; and a public
default decision is recorded. Until then the candidate stays DEFER, incomplete
and not qualified.

## Separation from sibling evidence

`docs/task-evidence/clearvoice-frcrn-16khz/`, `hush/`, `sylnet/`,
`gtcrn-streaming-onnx/`, `dpdfnet-2-streaming/` and the survey packages are
separate tasks with their own fixtures, scorers, cadences and dispositions.
This package does not import, reuse, pool or reinterpret their outputs,
metrics, adapters or reports. The LocalVQE **echo-only** checkpoint is a
separate task boundary and is never pooled with the compact full result. The
zero-reference dereverberation probe is an engineering misuse screen, not a
joint AEC result. The research adapter at `adapters/localvqe-aec/` is pinned
provenance only; it is not present in the SDK worktree, not installed, imported
or executed, and not changed.
