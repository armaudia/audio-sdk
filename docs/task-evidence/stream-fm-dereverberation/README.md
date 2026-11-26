<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-STREAM-FM-DEREVERBERATION — Stream.FM dereverberation blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Stream.FM dereverberation` (`component_id=stream-fm-dereverberation`). The
acceptance profile is **Room**. Decision: **DEFER**, before
`checkpoint_runtime_and_rights_admission`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, `qualification.status=not_qualified`.
A missing result may never qualify the candidate.

A local Stream.FM source checkout exists and is pinned to commit
`ab2700c1154acc5c2ce67a5344182028336413f5` (AGPL-3.0 repository license).
`config/streamfm_derev.yaml` declares 16 kHz, 512-point STFT, 256-sample hop,
CausalNCSNpp backbone and EARS-Reverb paths. The upstream README references a
public checkpoint folder, but **no local checkpoint file, byte count, SHA-256,
model terms bundle, admitted runtime, exact reference output, rights-cleared
cohort, independent score, listening result, target-device timing or opt-in
provider intake** is present in this workspace.

This package records exact blockers and runs a deterministic, stdlib-only
single-channel boundary surrogate to check declared probe geometry, one-hop
delay, reset behavior and adverse/missing/invalid/nonfinite rejection. The
surrogate is **not Stream.FM**, has no flow matching, no weights, no runtime and
no real audio; no surrogate observation may qualify the candidate. Nothing is
downloaded, copied, vendored, imported, loaded or executed. Only this task-local
directory is added.

## Exact blocker

| Required artifact | Recorded local state |
| --- | --- |
| Source checkout | Present at `data/checkouts/StreamFM`, pinned commit `ab2700c1154acc5c2ce67a5344182028336413f5`, AGPL-3.0 |
| Dereverb checkpoint | Absent; no local `data/models/streamfm/streamfm_derev.ckpt`, no filename/byte count/SHA-256 recorded |
| Runtime environment | Absent; no `data/envs/stream-fm-dereverberation` |
| Rights | Repository AGPL-3.0 present; checkpoint/training-data/corpus/runtime/product-use terms unresolved |
| Exact/runtime evidence | Absent: no exact output, no rights-cleared paired cohort, no independent score/listening, no target timing |

A native/runtime import and model inference were **not** attempted. Observed
source presence is not checkpoint/runtime admission, reproducibility or ABI
evidence. Every release gate remains `blocked`.

## Task geometry

Stream.FM dereverberation is a single-channel candidate in this task. The
checkout config declares 16 kHz, `n_fft=512`, `hop_length=256` (16 ms),
CausalNCSNpp backbone and EARS-Reverb format. The probe harness declares a
**probe-only** 16 kHz mono `float32`, 256-sample / 16 ms hop and one 256-sample
/ 16 ms output delay. It is **not** a measured Stream.FM latency or quality
result. Installed SDK v0 remains 16 kHz mono `float32` at **160 samples**; no
installed geometry, default, ABI, contract, registry, descriptor, shared build
or CI file is changed.

## Room profile application

| Required item | Evidence |
| --- | --- |
| Frozen render/reference | Frozen synthetic 1-channel early/late/noise decomposition; no measured RIR claimed |
| Channel/rate/hop | Probe-only 1 channel, 16 kHz `float32`, 256-sample hop, 250 hops |
| Excitation | Deterministic harmonic segments plus click transients and LCG noise |
| Delay | Declared probe delay 256 samples / 16 ms; impulse at 2000 maps to 2256 |
| Noise | Frozen noisy-speech stratum with deterministic LCG source |
| Reset schedule | Reset to epoch 1 matches a fresh session; epoch 0 and −1 rejected |
| Echo-only / overlap / no-reference | Not applicable: no far-end reference, no AEC, no candidate output |
| Nonfinite failures | Zero nonfinite outputs; injected nonfinite inputs rejected before state change |
| No-reference independent comparison | Blocked: no candidate output, corpus or listener |

## Fixture and surrogate

`reference.build_fixture()` synthesises 64,000 samples (4 s, 250 frames) from
integer arithmetic: fixed 64-entry sine table, integer phases/envelopes, early/
late room responses and deterministic LCG noise. Every sample is quantised to
int16 and exposed as `float32 / 32768`.

| Stratum | Frames | Condition |
| --- | ---: | --- |
| `silence-a` | 0–49 | Exact digital silence |
| `speech-a` | 50–99 | Harmonic speech-like segment |
| `speech-b` | 100–149 | Harmonic segment plus deterministic click transients |
| `noisy-speech` | 150–199 | Harmonic segment plus frozen LCG noise |
| `tail-after-speech` | 200–249 | Clean source ends; room tail decays |

The surrogate is a deterministic, non-adaptive, model-free two-stage boundary
harness: fixed causal late-reverberation subtraction, single-channel static
nonlinear compression and one 256-sample output delay. It has no neural
network, flow matching, checkpoint, weights or runtime and is **not Stream.FM**.

## Results (surrogate invariants only, not Stream.FM results)

All values are exact `report.json` values. They are surrogate behavior
observations, **not Stream.FM results**, not device timing and not a release
claim.

| Invariant | Exact value |
| --- | ---: |
| Probe channels | 1 |
| Scored samples | 63,744 |
| Maximum absolute surrogate output | see `report.json:metrics.max_abs_output` |
| Nonfinite surrogate outputs | 0 |
| Clipped surrogate outputs | 0 |
| Silence stratum exact zero | true |
| Impulse peak index / expected | 2256 / 2256 |
| Partial-tail valid samples | 232 |
| Streaming/offline parity | true |
| Reset fresh-session parity | true |

## Failure controls (exact failures recorded as failures)

- **Caller asset:** generic manifest with caller-owned temporary files validates
  hashes/geometry but reports `loaded=false`, `executed=false`, `imported=false`,
  `pinned_asset=false`. Missing, relative-path, absent-file, hash, commit,
  geometry, format, boolean and workspace-absent cases are rejected. A caller
  placeholder is never admitted as the pinned checkpoint/runtime.
- **Config adverse:** 48 kHz, 2 channels, `int16`, wrong frame/latency,
  `model_used=true`, `real_runtime=true`, `surrogate=false`, extra keys, empty
  session id, negative epoch and boolean epoch are rejected before state creation.
- **Frame adverse:** wrong length, NaN, ±Infinity, out-of-range, boolean, string,
  nested, `None` and non-sequence frames are rejected with state digest/counter
  unchanged.
- **Nonfinite input:** NaN is never counted as silence; accepted counter and
  state digest unchanged and reason is `mic_nonfinite`.
- **Delay:** impulse at source index 2000 keeps output peak index **2256**.
- **Partial tail:** 1,000-sample stream preserves length, returns
  `tail_valid=232` and matches full-stream prefix exactly.
- **Reset:** epoch 1 reproduces a fresh session; epoch 0 and −1 rejected.
- **Silence:** 512-sample zero stream returns exact zero and finiteness.
- **Streaming:** arbitrary chunk sizes produce byte-identical output to offline.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, pins, commands, results, gates. |
| `reference.py` | Deterministic fixture, surrogate, strict parsers, controls, report/contract/manifest builders. |
| `run.py` | Builds report three times, requires byte identity, regenerates artifacts. |
| `report.json` | Canonical machine-readable Room report. |
| `report.json.sha256` | Digest of committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and manifest. |

## Source pins (SHA-256)

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:data/checkouts/StreamFM/LICENSE` | `8486a10c4393cee1c25392769ddd3b2d6c242d6ec7928e1414efff7dfb2f07ef` |
| `source:data/checkouts/StreamFM/README.md` | `add959204bf4f7c69e00e65a88898533bcde0ae1558e9ea25e8d9e3fb7ad6014` |
| `source:data/checkouts/StreamFM/config/streamfm_derev.yaml` | `901538c1ccec5a2805a7b2c50a0407e56b9cdcb931f0c07977732fbe161c4eec` |
| `source:data/checkouts/StreamFM/inference.py` | `c7196c752ac7da7cb322fda8babf93d70883913fd1dcef6c7a16e77b36aba378` |
| `source:data/checkouts/StreamFM/requirements.txt` | `e8ed8ec3c71de0e03d40a778589de6122df3649fc72f9a0f343ad53e95d3fd88` |
| `source:data/checkouts/StreamFM/sgmse/backbones/streaming_unet.py` | `d88c7bb526a97ae11d3cdede0e03e81b7c6e38cd2c6ad92296a37f974668d80a` |
| `source:data/checkouts/StreamFM/sgmse/model.py` | `c766ff24bfdf8dba9a10a3fff8b2070a216c5e61677056dffff964cb46493a75` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

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

## External artifact identity

No external checkpoint/runtime is admitted. The source checkout is present and
pinned to commit `ab2700c1154acc5c2ce67a5344182028336413f5` with AGPL-3.0
repository license. The dereverb checkpoint, runtime, exact outputs, rights
clearance and target timing remain absent/unresolved. If those artifacts appear,
this evidence package is stale and must reopen.

## Artifact digests (SHA-256)

<!-- DIGEST_TABLE_ARTIFACTS_START -->

| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `05de061f15fa517e69edb76745750794081c5475de21306565541aa29c309139` | 13072 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `879773f563b2714272fbaee75b6b10c8c3e099812e8bd239596476a2c073a841` | 63751 |
| `report.json` | `4a3ee8a0fe83c35152ade1f2e98a13ba505851660909cc133e9daf1a8ff865ea` | 18980 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `cd9627fe01127102e00f3a848b70fa6860b1edce9c055f648a01e25b55c8e53e` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `23b03acfb4ff19bb3998fb9218d725efb568a2ecae60da316f522ba9a0cd6dd1` | 2052 |
| `test_reference.py` | `7000e28ed5f883afd1c2855b3e462f2ad93c7cae850edf14a726c50fea3153fd` | 10671 |
| `verify.py` | `97bb9d572eedeea3127a52cfbe9fe54260884c58fc881768730ecdc420a45ffa` | 15536 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory:

```sh
TASK=$PWD
PY=/opt/homebrew/bin/python3
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-STREAM-FM-DEREVERBERATION diff --check
```

`run.py` builds the report three times in one process and refuses to write
unless all payloads are byte-identical. External reproduction runs `run.py`
three times in fresh processes and compares resulting bytes.

## Remaining gates (eight blocked)

1. `exact_checkpoint_identity_and_terms`
2. `pinned_runtime_and_offline_load`
3. `source_checkpoint_rights`
4. `exact_geometry_and_latency`
5. `exact_reference_parity`
6. `rights_cleared_paired_cohort`
7. `independent_scoring_and_listening`
8. `target_runtime_timing_and_opt_in_provider`

**Reopen condition.** Supply the exact Stream.FM dereverb checkpoint with byte
count and SHA-256, an admitted locked runtime, clear artifact and corpus rights
including AGPL distribution review, exact geometry/solver/latency reproduction,
exact-runtime reference outputs, independent paired-cohort scoring or permitted
listening, target-device timing and OFF-by-default opt-in provider intake.
Until then the candidate stays **DEFER**, **incomplete** and **not qualified**.

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
(`tasks[id=SDK-STREAM-FM-DEREVERBERATION]`, stable-field digest); the mutable
full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to this
package. No provider, descriptor, registry, installed default, public ABI,
shared build or CI is changed.

## Separation from sibling evidence

Other dereverberation candidates (2S-Dereverb, LocalVQE dereverb probe, NeMo
Schrödinger Bridge dereverberation, WPE, etc.) are **separate evidence**. They
use different candidates, fixtures, checkpoints, licenses and dispositions.
This package does not pool, import, reuse or reinterpret their outputs, metrics
or adapters.
