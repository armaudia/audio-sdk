<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-2S-DEREVERB — multichannel WPE plus postfilter blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`2S-Dereverb` (`component_id=2s-dereverb`). The acceptance profile is **Room**,
assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`source_revision_and_checkpoint_admission`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, `qualification.status=not_qualified`.
A missing result may never qualify the candidate.

This package records the exact candidate locator and the declared task
geometry, then records the missing source, checkpoints, runtime, rights and
evidence as explicit blockers. It runs a deterministic, stdlib-only two-stage
*synthetic boundary surrogate* so that multichannel geometry, the declared probe
delay, reset behavior and adverse/missing/invalid/nonfinite rejection can be
checked mechanically. The surrogate is **not 2S-Dereverb**, contains no DNN, no
weights, no checkpoint and no runtime, and no surrogate observation may qualify
the candidate. Nothing is downloaded, copied, vendored, imported, loaded or
executed. Only this task-local directory is added.

## Exact blocker

The local research record names `https://github.com/sp-uhh/2sderev` and the
author dereverberation project, describes research code for DNN-supported
multichannel WPE plus a single-channel nonlinear postfilter, and states that
checkpoints are separately downloaded. It records **no** immutable commit, tag,
archive digest, licence, checkpoint filename, byte count or SHA-256. None is
fabricated here.

The exact source tree, both stage checkpoints and the runtime environment are
absent:

| Required artifact | Recorded local state |
| --- | --- |
| Source checkout | No `data/checkouts/2sderev`, no `adapters/2sderev` |
| Stage-1 multichannel-WPE checkpoint | No file and no recorded filename, byte count or SHA-256 |
| Stage-2 single-channel nonlinear-postfilter checkpoint | No file and no recorded filename, byte count or SHA-256 |
| Runtime environment | No `data/envs/2s-dereverb` |
| Rights | No established code, checkpoint, training-data, corpus or output-use terms |

A native runtime, a build, a model import and an inference call were **not**
attempted. Observed path presence is not runtime admission, reproducibility or
ABI evidence. Every release gate remains `blocked`.

## Task geometry

The candidate is conditional on **multichannel** input: the first stage is a
multichannel WPE-style dereverberator and the second stage is a **single-channel**
nonlinear postfilter. The research note records no channel count, sample rate,
hop, STFT/WOLA window, predictor delay, lookahead or total algorithmic latency,
and explicitly calls the latency unverified.

The harness therefore declares a **probe-only** geometry of 3 channels, 16 kHz,
`float32`, 256-sample / 16 ms hops and one 256-sample / 16 ms output delay. It is
not the upstream geometry. A reader must not infer that 2S-Dereverb uses 3
channels, 16 kHz, 256-sample hops or 16 ms latency. Installed SDK v0 remains
16 kHz mono `float32` at **160 samples**; the cadence divergence is recorded and
no installed geometry, default, ABI, contract, registry, descriptor, shared
build or CI file is changed.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Frozen render/reference | Frozen synthetic 3-channel early/late/noise decomposition; no measured RIR claimed |
| Channel/rate/hop | Probe-only 3 channels, 16 kHz mono-per-channel `float32`, 256-sample hop, 250 hops |
| Excitation | Deterministic harmonic segments plus click transients and per-channel LCG noise |
| Delay | Declared probe delay 256 samples / 16 ms; impulse at 2000 maps to 2256 |
| Movement | Not applicable: no render path and no measured room movement |
| Noise | Frozen noisy-speech stratum with deterministic LCG sources |
| Reset schedule | Reset to epoch 1 matches a fresh session; epoch 0 and −1 are rejected |
| Echo-only | Not applicable: no far-end playback reference and no echo path |
| Near-end-only | Not applicable: no near-end/render decomposition is claimed |
| Overlap | Not applicable: no double-talk condition is evaluated |
| No-reference | Not applicable: no candidate output exists to compare |
| Echo attenuation | Not measured; no echo-cancellation claim |
| Near-end damage | Blocked: no real candidate output or early-target score |
| Nonfinite failures | Zero nonfinite outputs; injected nonfinite inputs rejected before state change |
| Alignment, delayed/missing render | Impulse delay mapping only; no candidate alignment claim |
| No-reference independent comparison | Blocked: no candidate output, corpus or listener |

## Fixture and surrogate

`reference.build_fixture()` synthesises 64,000 samples per channel (4 s, 250
frames) from integer arithmetic: a fixed 64-entry sine table, integer phases and
envelopes, three different early/late room responses and three deterministic LCG
noise sources. Every sample is quantised to int16 and exposed as
`float32 / 32768`. Segment boundaries are multiples of 256 samples. The exact
decomposition `reverb = early + late + noise` is retained per channel for
structural checks.

| Stratum | Frames | Condition |
| --- | ---: | --- |
| `silence-a` | 0–49 | Exact digital silence |
| `speech-a` | 50–99 | Harmonic speech-like segment |
| `speech-b` | 100–149 | Harmonic segment plus deterministic click transients |
| `noisy-speech` | 150–199 | Harmonic segment plus frozen LCG noise |
| `tail-after-speech` | 200–249 | Clean source ends; room tail decays |

The surrogate is a deterministic, non-adaptive, model-free **two-stage boundary
harness**: a fixed causal multichannel late-reverberation subtraction followed by
a single-channel static nonlinear compression and one 256-sample output delay.
It has no neural network, checkpoint, weights or runtime, and it is **not
2S-Dereverb**. Identity is the mandatory control. No int16 codec, real room,
corpus or listening is involved.

## Results (surrogate invariants only, not 2S-Dereverb results)

All values are exact `report.json` values. They are surrogate behavior
observations, **not 2S-Dereverb results**, not device timing and not a release
claim. No SI-SDR, STOI, SRMR or perceptual score is claimed because no candidate
output exists.

| Invariant | Exact value |
| --- | ---: |
| Probe channels | 3 |
| Scored samples | 63,744 |
| Maximum absolute surrogate output | 0.643650536 |
| Nonfinite surrogate outputs | 0 |
| Clipped surrogate outputs | 0 |
| Silence stratum exact zero | true |
| Impulse peak index / expected | 2256 / 2256 |
| Partial-tail valid samples | 232 |
| Streaming/offline parity | true |
| Reset fresh-session parity | true |
| Mono stream rejected | true |
| Other channels change the output | true |

The surrogate cannot qualify the candidate. It only proves that the local
harness enforces the declared multichannel geometry, finite output, exact delay,
state reset and fail-closed validation.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates both stage hashes, the runtime hash and multichannel geometry, but
  reports `loaded=false`, `executed=false`, `imported=false`,
  `pinned_asset=false`. Missing, relative-path, absent-file, stage-1-hash,
  stage-2-hash, runtime-hash, short-commit, zero-rate, zero-frame,
  negative-latency, mono, out-of-range-reference, `int16`, wrong-stage-ID,
  non-single-channel-stage-2, boolean, extra-field and workspace-absent
  manifests are rejected. A caller placeholder is never admitted as the pinned
  source or checkpoint; the pinned-identity path fails closed with
  `upstream_commit_not_established`.
- **Config adverse:** 48 kHz, 1 or 2 channels, `int16`, 320-sample frames, zero
  or negative latency, `multichannel=false`, out-of-range reference channel,
  wrong stage IDs, `real_runtime=true`, model-used, surrogate-disabled, extra
  keys, empty session id, negative epoch and boolean epoch are rejected before
  state creation.
- **Frame adverse:** mono, two-channel, four-channel, ragged, empty final,
  255-sample nonfinal, 257-sample nonfinal, string outer, string channel, NaN,
  ±Infinity, out-of-range, boolean, nested, `None` and 128-sample nonfinal frames
  are rejected with the state digest and accepted-sample counter unchanged.
- **Nonfinite input:** NaN is never counted as silence; the accepted counter and
  state digest are unchanged and the reason is `mic_nonfinite`.
- **Delay:** an impulse at source index 2000 keeps output peak index **2256**,
  exactly one declared probe hop later. The second-stage static nonlinearity
  reduces the peak below the input peak while remaining finite.
- **Partial tail:** a 1,000-sample stream preserves length, returns
  `tail_valid=232` from drain and matches the full-stream prefix exactly.
- **Reset:** resetting to epoch 1 reproduces a fresh epoch-1 session; epoch 0
  and −1 are rejected and leave the stale session digest unchanged.
- **Silence:** a 512-sample zero stream returns exact zero and finiteness.
- **Streaming:** arbitrary 160/480/320/256/137/641/1000-sample chunks produce
  byte-identical output to offline framing.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Deterministic multichannel fixture, two-stage surrogate, strict parsers, controls, report/contract/manifest builders. |
| `run.py` | Builds the report three times, requires byte identity, then regenerates all artifacts. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite. Only provenance files
that exist are pinned; no absent candidate artifact is given a fabricated hash.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
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

## External artifact identity

No external artifact is pinned: the source revision, licence, checkpoint
filenames, byte counts and SHA-256 values are not established. The report
records `commit=null`, `license=null`, `checkpoint_identity=null` and
`present=false` for the source, both checkpoints and the runtime. If any of
those artifacts appears, this evidence package is stale and must reopen.

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The table is refreshed by `run.py` and checked by
`verify.py`. `SOURCES.sha256` pins every artifact and this README; it does not
pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `a53ca9a6c15ff9c5f3cd2b432c7a5a6677940b6e38eb0fcd2f33ac069f31929a` | 14797 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `7ca720f5ba4aa2b34849f97dd05760e0960efc0217d1e29dfb417272b1e0daf9` | 81611 |
| `report.json` | `af8c401072654f8220d7aa807daecc0145308bf10c4c9b334486e57cfea6382e` | 29062 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `fe511bd1a860c73646e9cf25fd350bc898735cf9eedf2a1ac9708a6bee655ffc` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `0c385c3c726156772f74ff3e4496b3800f4d384734087b3d273d6eb94b45ed35` | 2053 |
| `test_reference.py` | `0768f5300d6c69ce8b87d4f20e114b9fab9285a69b5f6600a9b6153d39a8ac4e` | 33642 |
| `verify.py` | `a828f039da357ce4d70560bd08f491154c8082e6dfaf9e24c74c02b97228233b` | 24319 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-2S-DEREVERB
TASK=$WT/docs/task-evidence/2s-dereverb
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C "$WT" diff --check
```

`run.py` builds the report three times in one process and refuses to write
unless all payloads are byte-identical. External reproduction runs `run.py`
three times in fresh processes and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `exact_source_revision_and_license`
2. `checkpoint_identity_and_terms`
3. `pinned_runtime_and_offline_load`
4. `multichannel_geometry_and_latency`
5. `exact_reference_parity`
6. `rights_cleared_paired_cohort`
7. `independent_scoring_and_listening`
8. `target_runtime_timing_and_opt_in_provider`

Each exact requirement is recorded in `contract.json:gates` and
`report.json:gates`.

**Reopen condition.** Supply the exact source revision and licence, both stage
checkpoints with byte counts and SHA-256, a locked offline runtime, the exact
multichannel geometry and total latency, and clear artifact and corpus rights.
Then reproduce exact-runtime outputs, score a rights-cleared paired cohort with
independent metrics or permitted listening, measure target timing and complete
an OFF-by-default opt-in provider intake. Until then the candidate stays
**DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `multichannel_abi_change=false`,
`provider_registration=false`, `descriptor_registry_change=false`,
`installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
`processor_exposure=false`, `adapter_json_added=false`,
`readiness_json_added=false`, `asset_bundled=false`, `weights_vendored=false`,
`onnxruntime_invoked=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-2S-DEREVERB]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never read into, hashed by or pinned to this package.
No provider, descriptor, registry, installed default, public ABI, shared build
or CI is changed.

## Separation from sibling evidence

The LocalVQE dereverberation probe, the SRMR/reverb metrics package, the
CLN-04 survey package, the classical online/offline WPE research adapters and
the NeMo dereverberation adapter are **separate evidence**. They use different
candidates, fixtures, cadences, checkpoints and dispositions. This package does
not pool, import, reuse or reinterpret their outputs, metrics or adapters. The
research note and survey are pinned provenance only; they are not source
archives, runnable candidates or checkpoints, and they are not changed.
