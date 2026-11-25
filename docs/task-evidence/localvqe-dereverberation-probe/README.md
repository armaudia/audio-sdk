<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LOCALVQE-DEREVERBERATION-PROBE — zero-reference dereverberation blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LocalVQE dereverberation probe` (`component_id=localvqe-dereverberation-probe`).
The acceptance profile is **Room**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. A missing result may never qualify the
candidate.

This package records the exact LocalVQE compact joint checkpoint identity and
the **dereverberation-only, zero-far-end-reference** engineering scenario as a
caller-supplied external asset. The exact GGUF checkpoint, an admitted isolated
runtime and artifact-specific rights are absent, so the package runs a
deterministic, stdlib-only synthetic boundary surrogate and records a strict
readiness conclusion. It is **not LocalVQE source**, does not import or load a
model, weight, GGML library or runtime, does not download or vendor anything,
does not read real audio, does not measure a device clock, does not conduct
listening, does not benchmark the SDK and makes no quality, benchmark or
release claim. Only this task-local directory is added.

## Exact blocker

The upstream identity is pinned: `localai-org/LocalVQE`, source revision
`7f61cd05095d42e56a135b303f5bb4d761da22b9`, `Apache-2.0`. The compact joint
model is `localvqe-pi-v1-49k-f32.gguf` with SHA-256
`0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26`; the
parallel echo-only checkpoint is `localvqe-pi-aec-v1-49k-f32.gguf` with SHA-256
`b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8`.
`data/models/localvqe/localvqe-pi-v1-49k-f32.gguf` is **absent**, so no exact
inference, output vector, parity check or quality result exists. Upstream does
not publish a separate dereverberation-only checkpoint; the joint model is
conditional on a far-end playback reference.

A native library object is present at
`data/checkouts/LocalVQE/ggml/build/liblocalvqe.0.1.0.dylib` (recorded identity
only, SHA-256 `bb30cc40…`). It was **not read, hashed, loaded or executed** by
this package, and observed presence is not runtime admission, reproducibility or
ABI evidence. No isolated environment exists at
`data/envs/localvqe-dereverberation-probe`.

The source and model repository are described as Apache-2.0 upstream, but
artifact-specific model terms, training-data provenance, corpus terms,
redistribution, product-use and legal review remain unresolved. Nothing was
copied, vendored, built, downloaded, imported, loaded, executed or
redistributed. Every release gate remains `blocked`.

## Scenario boundary (distinct from AEC and joint full)

The upstream adapter states that the model is jointly trained for AEC, noise
suppression and dereverberation and is conditional on a far-end playback
reference. The dereverberation-only probe supplies a **zero far-end reference**
to preserve the required two-input contract. This is an engineering misuse
screen for the mono dereverberation question:

- it is **not** paired-reference AEC and does not evaluate echo cancellation;
- it is **not** the joint compact-full paired-reference configuration;
- it does **not** establish that LocalVQE is a pure dereverberator;
- it may still include the model's noise-suppression and joint behavior.

The recorded geometry is 16 kHz mono, `float32`, **256-sample / 16 ms** hops and
one 256-sample / 16 ms algorithmic output delay. Installed SDK v0 remains
16 kHz mono `f32` at **160 samples**; the cadence divergence is recorded, no
numeric parity with the real runtime is claimed and no installed geometry,
default, ABI, contract, registry, descriptor, shared build or CI file changes.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Frozen render/reference | Frozen synthetic early taps and late taps; no measured RIR claimed |
| Channel/rate/hop | 16 kHz mono `float32`, 256-sample hop, 250 hops |
| Excitation | Deterministic harmonic segments plus a click transient and LCG noise |
| Delay | Declared 256-sample / 16 ms output delay; best-lag 256, impulse map 2000 → 2256 |
| Movement | Not applicable: no render path and no measured room movement |
| Noise | Frozen noisy-speech stratum with a deterministic LCG source |
| Reset schedule | Reset to epoch 1 matches a fresh session; epoch 0 and −1 are rejected |
| Echo-only | Not applicable: zero far-end reference is supplied |
| Near-end-only | Not applicable: no near-end/render decomposition is claimed |
| Overlap | Not applicable: no echo path is evaluated |
| No-reference | The whole probe is a zero-far-end misuse screen, labeled as such |
| Echo attenuation | Not measured; no echo cancellation claim |
| Near-end damage | Early-target SI-SDR on speech, transient, noisy and tail strata |
| Nonfinite failures | Zero nonfinite outputs; injected nonfinite inputs rejected before state change |
| Alignment, delayed/missing render | Best-lag and impulse mapping; missing render is the declared scenario, not a pass |
| No-reference independent comparison | Identity is the mandatory paired control on the same early target |

## Fixture and surrogate

`reference.build_fixture()` synthesises 64,000 samples (4 s, 250 frames) from
integer arithmetic: a fixed 64-entry sine table, integer phases and envelopes, a
deterministic LCG noise source and fixed room taps. Every sample is quantised to
int16 and exposed as `float32 / 32768`. Segment boundaries are multiples of 256
samples. The exact decomposition `reverb = early + late + noise` is retained for
scoring; the early target is the response through 50 ms, and the late response
starts at 50 ms.

| Stratum | Frames | Condition |
| --- | ---: | --- |
| `silence-a` | 0–49 | Exact digital silence |
| `speech-a` | 50–99 | Harmonic speech-like segment |
| `speech-b` | 100–149 | Harmonic segment plus deterministic click transients |
| `noisy-speech` | 150–199 | Harmonic segment plus frozen LCG noise |
| `tail-after-speech` | 200–249 | Clean source ends; room tail decays |

The surrogate is a deterministic, non-adaptive, model-free **fixed causal
late-reverberation subtraction**: 72 % of the first ten late taps are predicted
from past input and subtracted, followed by one 256-sample output delay. It has
no neural network, checkpoint or weights, and it is **not LocalVQE**. Identity
is the mandatory control. No int16 quantisation, real room, corpus or listening
is involved.

## Results (synthetic boundary surrogate only)

All values are exact `report.json` values, rounded to 9 decimal places. They are
surrogate behavior observations, **not LocalVQE results**, not device timing and
not a release claim.

| Metric | Exact value |
| --- | ---: |
| Output SI-SDR vs early target | 5.818780881 dB |
| Identity SI-SDR vs early target | 2.123207278 dB |
| Output projection DRR proxy | 10.293077534 dB |
| Identity projection DRR proxy | 1.312349337 dB |
| Projection DRR gain | 8.980728197 dB |
| `speech-a` output / identity SI-SDR | 9.277057029 / 2.863472503 dB |
| `speech-b` output / identity SI-SDR | 2.355547475 / −7.689506933 dB |
| `noisy-speech` output / identity SI-SDR | 6.836443480 / 7.601172824 dB |
| `tail-after-speech` output / identity SI-SDR | −13.082426306 / −4.711008284 dB |
| Maximum absolute output | 0.953328878 |
| Clipped / nonfinite samples | 0 / 0 |
| Silence stratum exact zero | true |

The surrogate improves early-target SI-SDR on `speech-a` and `speech-b` and the
projection DRR proxy overall, but it **regresses** on the noisy-speech stratum
(6.836443480 dB versus identity's 7.601172824 dB) and on the decaying tail
(−13.082426306 dB versus −4.711008284 dB). Those regressions are recorded as
observed failures, not hidden or promoted. The surrogate cannot qualify the
candidate.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates both hashes and the geometry but reports `loaded=false`,
  `executed=false`, `imported=false`, `pinned_model=false`. Missing, absent,
  relative-path, model-hash, library-hash, wrong-commit, 48 kHz, stereo,
  320-sample, `int16`, `compact-echo-only`, `dereverb-only`,
  `paired_reference`, render-delay-256, latency-0 and extra-field manifests are
  rejected. The workspace pinned manifest is rejected as
  `asset_file_missing:model_path`; a manifest that claims the pinned digests for
  placeholder bytes is rejected as `asset_model_hash_mismatch`. A placeholder is
  never accepted as the pinned joint model.
- **Config adverse:** 48 kHz, 2 channels, `int16`, 320-sample frames, zero
  latency, nonzero render delay, `paired_reference`, echo-only variant,
  `real_runtime=true`, model-used, library-used, extra keys, empty session id,
  negative epoch and boolean epoch are rejected before state creation.
- **Frame adverse:** empty final, 255-sample nonfinal, 257-sample nonfinal,
  string, NaN, ±Infinity, out-of-range, boolean, nested, `None` and 128-sample
  nonfinal frames are rejected with the state digest and accepted-sample counter
  unchanged.
- **Nonfinite input:** NaN is never counted as silence; the accepted counter is
  unchanged and the reason is `mic_nonfinite`.
- **Delay:** the best error-energy lag of the output is exactly **256** samples
  versus identity's **0**. An impulse at source index 2000 keeps output peak
  index **2256**, exactly one hop later. Unaligned SI-SDR is 5.488598329 dB
  versus 5.818780881 dB aligned; the small SI-SDR delta is a property of the
  periodic fixture, so the explicit lag and impulse mapping are the primary
  delay evidence.
- **Partial tail:** a 1,000-sample stream preserves length, returns
  `tail_valid=232` from drain and matches the full-stream prefix exactly.
- **Reset:** resetting to epoch 1 reproduces a fresh epoch-1 session; epoch 0
  and −1 are rejected and leave the stale session digest unchanged.
- **Silence:** a 512-sample zero stream returns exact zero and finiteness.
- **Streaming:** arbitrary 160/480/800/320/256/137/641-sample chunks produce
  byte-identical output to offline framing.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Deterministic fixture, surrogate, strict parsers, controls, report/contract/manifest builders. |
| `run.py` | Builds the report three times, requires byte identity, then regenerates all artifacts. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:adapters/localvqe/README.md` | `b964486bb1f823f9ce6ad52b10210d04b596a8642bda5b46aedb0532eea808e0` |
| `source:adapters/localvqe/run.py` | `9f4f331faa5191e05dd8a693d0e0d7f7083b92512059e4320c8269b920c251c6` |
| `source:adapters/localvqe-aec/README.md` | `61240419dc9d46af2056316f2a7167b833fb80e9d6a4ce8470b94a8cde488cd1` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:data/checkouts/LocalVQE/LICENSE` | `84afcb26750e77daeecc0150a6bd031d0d561abd75ef7f2a42508dcdade70d54` |
| `source:data/checkouts/LocalVQE/README.md` | `2eeed279c971cce67f7897ae51bc9c8552c0e88bdd715d27520f956262d2423c` |
| `source:data/checkouts/LocalVQE/ggml/localvqe_api.h` | `ef2871bde8cd8fe9aa8cd5c3b7d11cc72efb7bb1cc29f726522ace87ad490877` |
| `source:data/checkouts/LocalVQE/ggml/model_hash.cpp` | `bbdd538da35f67c70a6726f3c6abf2671e01c5dfb2ce86392ff14acbcc043d58` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
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

## External asset identity (recorded, not read)

These values are identity only. The joint and echo model paths are checked for
absence: if either appears, this evidence package is stale and must reopen. The
native library is recorded as expected identity; it is not read, hashed, loaded
or executed, and its presence is not runtime evidence. Nothing is downloaded,
copied, imported, loaded or executed.

<!-- digest-table: external -->
| Key | SHA-256 |
| --- | --- |
| `asset:echo_model` | `b80b75b9038d0d28079a84afe7d4f0b8f6404f723af4633c05ed4f96fb30b7b8` |
| `asset:joint_model` | `0e0c82a8e9703e818b64dedd0fc306394cf5bbb59fcec1ccca82099d352d0c26` |
| `asset:native_runtime_identity` | `bb30cc40c87e780e3a7277fdf6eee469dac1df684a023f884cefdaa24f945298` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The table is refreshed by `run.py` and checked by
`verify.py`. `SOURCES.sha256` pins every artifact and this README; it does not
pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `87218fabb13b5298ca81fb16cf06cba9ee9c0c1ca905371378e61236895f3021` | 12685 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `5618de9edf5e8a880eb4c849bf0141bf24bf3ab1c359c4019fcfe49a338ac6cb` | 72296 |
| `report.json` | `8ce127dd2e3ac1982d0d6b7426facb2d5f4cbf26b937ae4ec5940301708ee9d8` | 23016 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `7e305ce5cbd4b2af17cb933b8f42c4f899115e1602dd47cdacb2b2babb01faeb` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `4cd63f9d33b68750362576ca01960d1faf7dca562f779921d77da346d15c9cd6` | 1992 |
| `test_reference.py` | `b43988a934cf98c0903399537a75a2b9f373fc631605f6500a4c0e65f1bc63f1` | 25956 |
| `verify.py` | `7342854adbdeeba567ca44caf2f5aa8ce7395485d25e93dd4db0363cb59c1f86` | 21584 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LOCALVQE-DEREVERBERATION-PROBE
TASK=$WT/docs/task-evidence/localvqe-dereverberation-probe
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C "$WT" diff --check
```

`run.py` builds the report three times in one process and refuses to write
unless all payloads are byte-identical. External reproduction runs `run.py`
three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `exact_model_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `zero_reference_scenario_validity`
6. `rights_cleared_paired_cohort`
7. `independent_scoring_and_listening`
8. `target_runtime_timing_and_opt_in_provider`

Each exact requirement is recorded in `contract.json:gates` and
`report.json:gates`.

**Reopen condition.** Admit the exact checkpoint and a hash-pinned runtime,
clear artifact and corpus rights, establish that the zero-reference
dereverberation-only condition is intended or replace it with a paired-reference
AEC task, reproduce approved exact-runtime outputs, score a rights-cleared
paired cohort with independent metrics or permitted listening, measure target
timing and complete opt-in provider intake. Until then the candidate stays
**DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `onnxruntime_invoked=false`,
`native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-LOCALVQE-DEREVERBERATION-PROBE]`, stable-field digest); the
mutable full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to
this package. No provider, descriptor, registry, installed default, shared build
or CI is changed.

## Separation from sibling evidence

`docs/task-evidence/localvqe-compact-full/` is the paired-reference joint full
configuration; `docs/task-evidence/localvqe-compact-echo-only/` (sibling branch)
is the paired-reference echo-only configuration. This package is the
**zero-far-end dereverberation-only engineering probe** and does not pool,
import, reuse or reinterpret their outputs, metrics or adapters. The offline and
online WPE packages, the LocalVQE research adapter and the dereverberation
research note are separate evidence with their own fixtures, cadences and
dispositions. The research adapter at `adapters/localvqe/` is pinned provenance
only; it is not present in the SDK worktree, not installed, imported or
executed, and not changed.
