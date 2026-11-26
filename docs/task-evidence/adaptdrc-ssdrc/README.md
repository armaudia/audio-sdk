<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ADAPTDRC-SSDRC — AdaptDRC / SSDRC receiver-side blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`AdaptDRC / SSDRC` (`component_id=adaptdrc-ssdrc`). The acceptance profile is
**DSP**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`published_control_and_rights_admission`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, `qualification.status=not_qualified`.
A missing result may never qualify the candidate.

This package records the public locator and the declared task geometry, then
records the missing official source, algorithm parameters, licence, runtime,
reference output and evidence as explicit blockers. It runs a deterministic,
stdlib-only three-band adaptive DRC **local approximation** so that the exact
installed v0 grid, finite output, zero content delay, reset behavior and
adverse/missing/invalid/nonfinite rejection can be checked mechanically. The
local approximation is **not AdaptDRC**, **not SSDRC**, and no observation from
it may qualify the candidate. Nothing is downloaded, copied, vendored, imported,
loaded or executed. Only this task-local directory is added.

## Exact blocker

The local inventory records `AdaptDRC / SSDRC` as a considered SDK-reference
candidate and gives only the public Fraunhofer product page:

`https://www.idmt.fraunhofer.de/en/institute/projects-products/adaptdrc.html`

The pinned research note `research/listening_intelligibility_20261028.md`
explicitly says its small compressor is **not AdaptDRC/SSDRC**. It records no
immutable commit, version, licence, filterbank, band edges, thresholds, ratios,
time constants, adaptation policy, output-power constraint, runtime or reference
output. None is fabricated here.

| Required artifact | Recorded local state |
| --- | --- |
| Official source / implementation | No `data/sources/adaptdrc-ssdrc`; no commit, version or archive digest |
| Licence and product-use terms | No `data/licenses/adaptdrc-ssdrc`; no written terms |
| Algorithm parameters | No filterbank, band edges, thresholds, ratios, time constants or adaptation policy |
| Runtime environment | No `data/envs/adaptdrc-ssdrc`; no framework or dependency lock |
| Reference output | No `data/reference/adaptdrc-ssdrc`; no exact output vector |
| Configuration identity | No `data/config/adaptdrc-ssdrc`; no canonical configuration or digest |
| Rights-cleared cohort | No target speech, listener-side masker, hearing profile or consent |

A native runtime, a build, an import and an inference call were **not**
attempted. Observed path presence is not runtime admission, reproducibility or
ABI evidence. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/adaptdrc-ssdrc/`. Shared CMake,
  contracts, public headers, descriptor registry, defaults, installed v0
  behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. The local
  approximation is causal and has 0 samples of content delay on that exact grid.
- The local approximation is deterministic, model-free and standard-library
  only. It is default OFF, unregistered and not a provider.
- No real speech corpus, listening panel, licensed runtime, model weights,
  network download, target-device timing, STOI/ESTOI computation, quality score
  or release qualification is used. Every signal is analytic or seeded-noise.
- Missing, invalid, nonfinite, out-of-range, stale-session and missing-reference
  cases fail closed. No missing result may qualify the candidate.
- Fixed DSP controls, published-control locators and the local approximation are
  reported separately and are never pooled.

## Fixed DSP, published controls and local approximation

The package keeps three evidence classes apart:

1. **Fixed DSP controls** — identity, static +6 dB gain, a fixed three-band
   tilt and a full-band compressor. These are measured locally on synthetic
   signals and are controls, not candidate results.
2. **Published controls** — AdaptDRC and SSDRC are recorded as public
   descriptions/locators only. Neither is reproduced. The SSDRC literature
   locator is used for the designation “spectral shaping and dynamic-range
   compression”; no paper, source or parameter set was downloaded or pinned.
3. **Local approximation** — `local_three_band_adaptive_drc_surrogate`, a
   three-band compressor with a bounded high-band balance controller. It is
   `is_adaptdrc=false`, `is_ssdrc=false`, `surrogate_only=true` and
   `candidate_result=false`.

The local approximation is not evidence that AdaptDRC/SSDRC works, and the
published locators are not evidence that the local approximation matches them.

## DSP profile application

`plan/swarm/VERIFICATION.md` DSP row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Sweeps | Deterministic piecewise frequency sweep, 250–6000 Hz tone gains |
| Steps | Quiet-to-loud and loud-to-quiet steps with attack/release transition |
| Impulses | Single impulse at index 2000; zero-delay peak at 2000 |
| Silence | 512-sample zero stream returns exact zero |
| Clean speech | Synthetic harmonic speech-like segments; no real corpus |
| Intelligibility or load control | None: no listener, listening effort, STOI/ESTOI or word recognition |
| Gain | Tone gain and full-fixture RMS gain per mode |
| Response | Fixed-tilt and local three-band tone gains at 250–6000 Hz |
| Attack/release | Measured step transitions; 5 ms attack / 120 ms release design |
| Headroom | Peak ceiling 0.95; clipped-sample counts recorded honestly |
| Delay | Local content delay 0 samples; official delay not established |
| Numerical behavior | Nonfinite input rejected before state change; zero nonfinite outputs |
| State transitions | Reset to epoch 1 matches a fresh session; stale/negative epochs rejected |
| Interacting nonlinear configurations | Compressor + tilt + peak guard measured together; no masked claim |
| Listening | Blocked: no panel, hearing profile or playback clearance |

## Fixture and local approximation

`reference.build_fixture()` synthesises 64,000 samples (4 s, 400 frames) from
integer arithmetic: a fixed 64-entry sine table, integer phases, integer
amplitude envelopes and a 31-bit LCG. Every sample is quantised to int16 and
exposed as `float32 / 32768`. Segment boundaries are multiples of 160 samples.

| Stratum | Frames | Condition |
| --- | --- | --- |
| `silence-a` | 0–24 | Exact digital silence |
| `quiet-speech` | 25–74 | Quiet speech-like harmonic segment |
| `speech-transient` | 75–124 | Harmonic segment plus deterministic clicks |
| `level-step-up` | 125–174 | Loud speech-like harmonic segment |
| `noisy-speech` | 175–224 | Harmonic segment plus frozen LCG noise |
| `sweep` | 225–274 | Rising frequency sweep |
| `impulse-train` | 275–324 | Fixed-period impulsive transients |
| `silence-tail` | 325–399 | Exact digital silence |

The local approximation splits the signal into three causal bands at 400 Hz and
2 kHz, applies a per-band gain computer (−24 dBFS threshold, 3:1 ratio, 5 ms
attack, 120 ms release), adds a fixed 0/2/4 dB tilt and a bounded high-band
balance adjustment, then applies a 0.95 peak ceiling. It is zero-delay,
model-free and not AdaptDRC/SSDRC.

## Results (local surrogate invariants only, not AdaptDRC/SSDRC results)

All values are exact `report.json` values. They are local surrogate behavior
observations, **not AdaptDRC/SSDRC results**, not device timing and not a release
claim. No intelligibility, quality, listening, STOI/ESTOI or perceptual score is
claimed.

| Mode | RMS gain dB | Level slope dB/dB | Max abs | Clipped samples | Silence exact zero |
| --- | ---: | ---: | ---: | ---: | --- |
| Identity | 0.0 | 1.0 | 1.0 | 0 | true |
| Static +6 dB | 0.768964159 | 0.996431349 | 0.95 | 6104 | true |
| Fixed three-band tilt | 0.464994463 | 1.0 | 0.95 | 5610 | true |
| Full-band compressor | -14.733004493 | 0.492063664 | 0.643599794 | 0 | true |
| Local approximation | -10.206623639 | 0.639527304 | 0.95 | 19 | true |

Additional exact invariants: the impulse peak is at index **2000** with 0
declared delay; streaming/offline parity is **true** for
160/137/641/320/1000/73/211/160-sample chunks; reset to epoch 1 matches a fresh
session; epoch 0 and −1 are rejected; the 512-sample silence stream is exact
zero; three nonfinite inputs are rejected with the accepted counter and state
digest unchanged; no mode produces a nonfinite output.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates all five hashes and the declared geometry, but reports
  `loaded=false`, `executed=false`, `official_identity=false`. Missing,
  relative-path, absent-file, wrong-hash, short/negative commit, zero-rate,
  zero-frame, stereo, negative-latency, positive-power, boolean-latency,
  wrong-algorithm, empty-version, extra-field and missing-field manifests are
  rejected. A caller placeholder is never admitted as the official artifact;
  `pinned_asset_identity` always fails with
  `official_artifact_identity_not_established`.
- **Config adverse:** 48 kHz, stereo, `int16`, 320-sample frames, unbounded
  adaptation, official algorithm ID, zero attack, zero release, excess max gain,
  NaN/Infinity threshold or ratio, positive threshold, real runtime, model used,
  surrogate disabled, default enabled, extra key, empty session id, negative
  epoch and boolean epoch are rejected before state creation.
- **Frame adverse:** empty, zero-length final, 159-sample nonfinal, 161-sample
  nonfinal/final, string outer, string sample, NaN, ±Infinity, out-of-range,
  boolean, nested, `None` and short final frames are rejected. Nonfinite input
  is never counted as silence and leaves the accepted counter and state digest
  unchanged.
- **Reset:** reset to epoch 1 reproduces a fresh epoch-1 session; epoch 0 and −1
  are rejected and leave the stale session unchanged.
- **Peak guard:** the local approximation clamps at 0.95 and records the exact
  clipped-sample count; no clipping event is hidden.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Deterministic fixture, local approximation, strict parsers, controls and report/contract builders. |
| `run.py` | Builds the report three times, requires byte identity, then regenerates artifacts. |
| `report.json` | Canonical machine-readable DSP report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite. Only provenance files that
exist are pinned; no absent candidate artifact is given a fabricated hash.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/listening_intelligibility_20261028.md` | `f29de5cdb58676b6f61ac8489ff5af44a88b2125c2022920436a6f064405992a` |
| `source:research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
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

No external artifact is pinned: the official source revision, licence, version,
algorithm parameters, runtime and reference output are not established. The
report records `commit=null`, `license=null`, `version=null`,
`algorithm_parameters=null`, `runtime=null`, `reference_output=null` and
`present=false` for every asset path. If any of those artifacts appears, this
evidence package is stale and must reopen.

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The table is refreshed by `run.py` and checked by
`verify.py`. `SOURCES.sha256` pins every artifact and this README; it does not
pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `ce8aaf4c2aadfcc39ddfef6d2645d81cbeb59800dc5b0b8d377f5a6081e59aa3` | 15721 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `b2bc243fb11820d62580e71b3a679a8dc450174ae42be9f8feed13643f9db8f6` | 81298 |
| `report.json` | `70f3dedc25b6849eb285ecf7bfa6293b17d8dda0008f9fa541c2c57dc6088d0b` | 34287 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `e2d68c673d8b96d426aced10df79fe92b6e7e8a03eb34a08a74836bbcf43e055` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `d84ac06ead3856a49da4e26f20a256c1141e00d8b86e498806d92b48b63ab6e2` | 2034 |
| `test_reference.py` | `adc2364cfe84c2f4ca67362161b246c09f78dfa51c1b5642361f4d4c98ea8072` | 18359 |
| `verify.py` | `b74a56f6a54e9b3ccaaa740b67b62318acd5471ff74951f4cee54259a7257ff8` | 26970 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ADAPTDRC-SSDRC
TASK=$WT/docs/task-evidence/adaptdrc-ssdrc
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
three times in fresh processes and compares the resulting bytes; `verify.py`
also performs three cold-start interpreter probes.

## Remaining gates (eight blocked)

1. `exact_source_revision_and_license`
2. `published_algorithm_and_parameter_identity`
3. `pinned_runtime_and_reference_output`
4. `receiver_side_geometry_and_content_delay`
5. `fixed_dsp_and_published_control_separation`
6. `rights_cleared_listening_and_masker_cohort`
7. `independent_quality_timing_and_power`
8. `opt_in_provider_intake_and_default_review`

Each exact requirement is recorded in `contract.json:gates` and
`report.json:gates`.

**Reopen condition.** Supply the official source revision and licence, the exact
published algorithm and parameters, a locked runtime and approved reference
outputs, the official receiver-side geometry and output-power constraint, and a
rights-cleared target/masker/listening cohort. Then score independently, measure
target timing and complete an OFF-by-default opt-in provider intake. Until then
the candidate stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `onnxruntime_invoked=false`, `runtime_invoked=false`,
`native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-ADAPTDRC-SSDRC]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never read into, hashed by or pinned to this package.
No provider, descriptor, registry, installed default, public ABI, shared build
or CI is changed.

## Separation from sibling evidence

The full-band receive DRC, feed-forward compressor, envelope AGC, EBU
R128/loudnorm, fixed six-band spectral tilt and STOI/ESTOI packages are
**separate evidence**. They use different candidates, fixtures, cadences and
dispositions. This package does not pool, import, reuse or reinterpret their
outputs, metrics or adapters. The research notes and inventory are pinned
provenance only; they are not source archives, runnable candidates or reference
outputs, and they are not changed.
