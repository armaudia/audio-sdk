<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-NOISE-AWARE-SHAPING-PLUS-DRC — receiver-side ablation blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Noise-aware shaping plus DRC` (`component_id=noise-aware-shaping-plus-drc`,
board mode `research-control`). The acceptance profile is **DSP**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `receiver_side_adapter_and_listener_admission`;
`evidence_status=incomplete`, `qualification_status=not_qualified`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

The pinned research note defines the lane and already contains an **offline,
non-causal numpy/scipy research prototype** (`src/audioml_eval/nele.py`). That
prototype is not a licensed SDK reference: it is a small whole-file research
baseline, it restores whole-file target-speech RMS, it estimates the masker from
the complete masker file, its shaping is explicitly **not** a faithful
OptFractASII reproduction, and the note records only STOI/ESTOI predictors with
no listener study. This package therefore keeps the lane as a **receiver-side
ablation**, records the exact missing artifacts and rights, and runs a
deterministic, stdlib-only **causal local approximation** only so that the
installed v0 grid, finite output, bounded energy equalization, zero content
delay, state reset and adverse/missing/invalid/nonfinite rejection can be
checked mechanically. The local approximation is **not** the research candidate
and **not** OptFractASII; no observation from it may qualify the candidate.
Nothing is downloaded, copied, vendored, imported, loaded or executed. Only this
task-local directory is added.

## Exact blocker

The local inventory records `noise-aware-shaping-plus-drc` as an
`evaluated`, `research-control` component whose only evidence link is the
pinned research note. The note records a small objective screen, not a licensed
streaming implementation, published parameter set, runtime or listener result.

| Required artifact | Recorded local state |
| --- | --- |
| Licensed streaming implementation | No `data/sources/noise-aware-shaping-plus-drc`; research module is offline, non-causal and not an SDK reference |
| Licence and product-use terms | No `data/licenses/noise-aware-shaping-plus-drc`; no written product, redistribution or derivative-output terms |
| Published algorithm and parameters | No gammatone filterbank, standard SII table, exact water level, shaping limits, DRC parameters or configuration digest |
| Runtime environment | No `data/envs/noise-aware-shaping-plus-drc`; no framework or dependency lock |
| Reference output | No `data/reference/noise-aware-shaping-plus-drc`; no exact output vector |
| Configuration identity | No `data/config/noise-aware-shaping-plus-drc`; no canonical configuration or digest |
| Rights-cleared masker and listener cohort | No independent participant-level masker set, consent, hearing profile or listening protocol |
| Listener outcomes | No listening panel, word recognition or listening-effort result; STOI/ESTOI only |

The research module and its screen were **not** imported, rerun or reproduced.
Observed path presence is not runtime admission, reproducibility or ABI
evidence. Every release gate remains `blocked`.

## Scope and invariants

- Work is confined to `docs/task-evidence/noise-aware-shaping-plus-drc/`. Shared
  CMake, contracts, public headers, descriptor registry, defaults, installed v0
  behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. The local
  approximation is causal and has 0 samples of content delay on that exact grid.
- The local approximation is deterministic, model-free and standard-library
  only. It imports no research module, numpy or scipy. It is default OFF,
  unregistered and not a provider.
- No real speech corpus, listener panel, licensed runtime, model weights,
  network download, target-device timing, STOI/ESTOI computation, quality score
  or release qualification is used. Every signal is analytic or seeded-noise.
- Missing, invalid, nonfinite, out-of-range, stale-session, short-masker and
  missing-reference cases fail closed. No missing result may qualify the
  candidate.
- Fixed DSP controls, the historical research screen and the local
  approximation are reported separately and are never pooled.

## Evidence classes kept apart

1. **Fixed DSP controls** — identity, static +6 dB gain, a fixed seven-band
   tilt, a noise-aware shaping control and a full-band compressor. These are
   measured locally on synthetic signals and are controls, not candidate
   results.
2. **Research evidence** — the pinned note and the offline
   OptFractASII-approximation prototype are recorded as provenance only. They
   are not rerun, not reproduced, not independent and not SDK results. The
   published OptFractASII locator is held as a literature locator only.
3. **Local approximation** —
   `local_causal_noise_aware_shaping_plus_drc_surrogate`, a causal seven-band
   importance-weighted noise-aware shaper with a bounded energy equalizer, a
   smoothed full-band DRC and a peak guard. It is
   `is_research_candidate=false`, `is_optfractasii=false`,
   `surrogate_only=true` and `candidate_result=false`.

The local approximation is not evidence that the research candidate works, and
the research screen is not evidence that the local approximation matches it.

## DSP profile application

`plan/swarm/VERIFICATION.md` DSP row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Sweeps | Deterministic piecewise frequency sweep, 250–6000 Hz tone gains and a six-tone band response |
| Steps | Quiet-to-loud and loud-to-quiet steps with measured transition windows |
| Impulses | Single impulse at index 2000; zero-delay peak at 2000 |
| Silence | 512-sample zero stream returns exact zero in every mode |
| Clean speech | Synthetic harmonic speech-like segments; no real corpus |
| Intelligibility or load control | None: no listener, listening effort, STOI/ESTOI or word recognition |
| Gain | Fixture RMS gain and six-tone band response per mode |
| Response | Band-energy redistribution on a six-tone probe |
| Attack/release | Measured step transitions; 5 ms attack / 120 ms release design |
| Headroom | Peak ceiling 0.95; clipped-sample counts recorded honestly |
| Delay | Local content delay 0 samples; research/deployed delay not established |
| Numerical behavior | Nonfinite target and masker rejected before state change; zero nonfinite outputs |
| State transitions | Reset to epoch 1 matches a fresh session; stale/negative epochs rejected |
| Interacting nonlinear configurations | Shaper + equalizer + DRC + peak guard measured together; no masked claim |
| Listening | Blocked: no panel, hearing profile, masker rights or playback clearance |

## Fixture and local approximation

`reference.build_fixture()` synthesises 64,000 samples (4 s, 400 frames) from
integer arithmetic: a fixed 64-entry sine table, integer phases, integer
amplitude envelopes, a 31-bit LCG and one-pole low/high masker tilts. Every
sample is quantised to int16 and exposed as `float32 / 32768`. Segment
boundaries are multiples of 160 samples.

| Stratum | Frames | Condition |
| --- | --- | --- |
| `silence-head` | 0–49 | Exact digital silence |
| `quiet-speech` | 50–99 | Quiet speech-like harmonic segment, low masker |
| `masked-speech` | 100–149 | Speech-like segment, loud low-tilted masker |
| `level-step-up` | 150–199 | Loud speech-like harmonic segment |
| `speech-clicks` | 200–249 | Harmonic segment plus deterministic clicks, moderate high-tilted masker |
| `sweep` | 250–299 | Rising frequency sweep, moderate high-tilted masker |
| `impulse-train` | 300–349 | Fixed-period impulsive transients |
| `silence-tail` | 350–399 | Exact digital silence |

The local approximation splits target and oracle masker into seven causal
first-order subtractive bands at 100/250/500/1000/2000/4000 Hz, tracks a slow
low-fractile masker power per band, computes bounded importance-weighted
shaping gains (±6 dB), applies a bounded causal energy equalizer (±12 dB,
50 ms tracker), adds a smoothed full-band gain computer (−24 dBFS threshold,
3:1 ratio, 5 ms attack, 120 ms release) and a 0.95 peak ceiling. It is
zero-delay, model-free and not the research candidate.

The masker is an **oracle synthetic** listener-side track. It is not a deployed
noise estimate, and no masker rights are established.

## Results (local surrogate invariants only, not candidate results)

All values are exact `report.json` values. They are local surrogate behavior
observations, **not** research-candidate results, not device timing and not a
release claim. No intelligibility, quality, listening, STOI/ESTOI or perceptual
score is claimed.

| Mode | RMS gain dB | Level slope dB/dB | Max abs | Clipped samples | Silence exact zero | Clean correlation |
| --- | ---: | ---: | ---: | ---: | --- | ---: |
| Identity | 0.0 | 1.0 | 0.610351562 | 0 | true | 1.0 |
| Static +6 dB | 5.958852238 | 0.996431349 | 0.95 | 5 | true | 0.999426027 |
| Fixed seven-band tilt | 0.186947811 | 1.0 | 0.598681755 | 0 | true | 0.975992066 |
| Noise-aware shaping | -0.095140346 | 1.0 | 0.604395762 | 0 | true | 0.99158955 |
| Full-band compressor | -1.740780446 | 0.492063664 | 0.610351562 | 0 | true | 0.994520449 |
| Local approximation | -1.780558476 | 0.487432122 | 0.604395762 | 0 | true | 0.985955212 |

Additional exact invariants: the impulse peak is at index **2000** with 0
declared delay; streaming/offline parity is **true** for
160/137/641/320/1000/73/211/160-sample chunks; reset to epoch 1 matches a fresh
session; epoch 0 and −1 are rejected; the 512-sample silence stream is exact
zero; five nonfinite inputs (three target, two masker) are rejected with the
accepted counter and state digest unchanged; no mode produces a nonfinite
output; the shaping-only modes are energy-neutral within 1 dB and the static
gain clips exactly 5 samples at the 0.95 ceiling.

Measured attack/release transition windows are 0/0 ms for identity, 0/0 ms for
the energy-equalized shaping controls, 12.5/200.0 ms for the full-band
compressor and 12.5/202.5 ms for the local approximation. These are window
observations of the local surrogate, not deployed latency or listener timing.

### Masker-band adaptation probe

With a silent target and the same oracle masker run under two tilts, the local
shaping control converges to different band gains: band 1 (100–250 Hz) is
**+7.64 dB** higher under the low masker than under the high masker, and band 6
(>4 kHz) is **−1.43 dB** lower. The probe demonstrates bounded noise-aware
redistribution only. It is not evidence of intelligibility, listener benefit or
agreement with OptFractASII.

## Historical research screen (quoted provenance, not reproduced)

The pinned note reports the following equal-target-power objective screen:
12 locally staged EARS anechoic utterances, three GPLv3 VADToolkit masker
scenes, SNRs −5/0/+5 dB, 108 pairs per method, STOI/ESTOI predictors, no
listener study.

| Candidate | Mean STOI | Mean ESTOI | ESTOI Δ vs identity |
| --- | ---: | ---: | ---: |
| Identity | 0.6897 | 0.5719 | — |
| Fixed spectral tilt | 0.7006 | 0.5760 | +0.0040 |
| Noise-aware OptFractASII approximation | 0.6876 | 0.5627 | −0.0092 |
| Noise-aware shaping + DRC | 0.6898 | 0.5683 | −0.0036 |
| DRC alone | 0.6873 | 0.5752 | +0.0033 |

These numbers are **quoted, not rerun**. The note records that the
noise-aware candidates underperformed identity on the aggregate, that the fixed
tilt lead is not robust to its clustered interval, that the masker set is not an
independent participant-level corpus, and that no deployment choice is made.
`report.json:historical_research_screen` marks `reproduced=false`,
`verified_independently=false`, `result_claim=false` and
`is_candidate_result=false` for exactly that reason.

## Failure controls (exact failures recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates all seven hashes and the declared geometry, but reports
  `loaded=false`, `executed=false`, `official_identity=false`. Missing,
  relative-path, absent-file, wrong-hash, short/negative commit, zero-rate,
  zero-frame, stereo, negative-latency, positive-energy, boolean-latency,
  wrong-algorithm, empty-version, extra-field and missing-field manifests are
  rejected. A caller placeholder is never admitted as the official or
  listener-qualified artifact; `pinned_asset_identity` always fails with
  `official_and_listener_identity_not_established`.
- **Config adverse:** 48 kHz, stereo, `int16`, 320-sample frames, whole-file
  energy equalization, estimated masker source, wrong band set, disabled
  noise-awareness, non-streaming, official algorithm ID, zero attack, zero
  release, negative shaping limit, NaN/Infinity threshold or ratio, positive
  threshold, real runtime, model used, surrogate disabled, default enabled,
  extra key, empty session id, negative epoch and boolean epoch are rejected
  before state creation.
- **Frame adverse:** empty, zero-length final, 159-sample nonfinal, 161-sample
  nonfinal/final, string outer, string sample, NaN, ±Infinity, out-of-range,
  boolean, nested, `None` and short final frames are rejected; a 159-sample
  masker, 161-sample masker, nonfinite masker, string masker and
  length-mismatched masker are also rejected. Nonfinite input is never counted
  as silence and leaves the accepted counter and state digest unchanged.
- **Reset:** reset to epoch 1 reproduces a fresh epoch-1 session; epoch 0 and −1
  are rejected and leave the stale session unchanged.
- **Peak guard:** static +6 dB clamps at 0.95 and records the exact
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

No external artifact is pinned: no licensed streaming source revision, published
parameter set, licence, version, runtime, reference output, masker cohort or
listener outcome is established. The report records `commit=null`,
`license=null`, `version=null`, `algorithm_parameters=null`,
`reference_output=null`, `runtime=null` and `present=false` for every absent
asset path. If any of those artifacts appears, this evidence package is stale
and must reopen.

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The table is refreshed by `run.py` and checked by
`verify.py`. `SOURCES.sha256` pins every artifact and this README; it does not
pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `c4ff79c42eefb9715ba596722c6d48dd8b77eee027403889d55d3dcb524e313c` | 17444 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `7f44a419f751d30cd93cb82dd58fe7e52a41ee5275234d85863167dfa0ebf24d` | 99885 |
| `report.json` | `aa65d7aa9d6896287c04778dfb9deb2232677b13f40e8cb2a83a5f87f87ca647` | 47258 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `34d03e432f80bb4030537de0c25b8d003c0b7f838db376a506125f726623bb77` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `43c489306b9b8a3812ce08ae4105d4954c5a6f727c2f187134f7d465068d3e5c` | 2065 |
| `test_reference.py` | `f6f5d91ea96cf1f4d064f62134bc2e57566a84f7eb900e5150720ca7ad180129` | 24281 |
| `verify.py` | `450f724c62b7bcb3531404c74793a9307d5da8f9764afb0bc01fcc279e0dce9c` | 30897 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-NOISE-AWARE-SHAPING-PLUS-DRC
TASK=$WT/docs/task-evidence/noise-aware-shaping-plus-drc
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

1. `exact_streaming_source_revision_and_license`
2. `published_algorithm_and_parameter_identity`
3. `pinned_runtime_and_reference_output`
4. `receiver_geometry_energy_and_content_delay`
5. `fixed_dsp_and_research_control_separation`
6. `rights_cleared_masker_and_listener_cohort`
7. `independent_intelligibility_energy_and_timing`
8. `opt_in_provider_intake_and_default_review`

Each exact requirement is recorded in `contract.json:gates` and
`report.json:gates`.

**Reopen condition.** Supply a licensed streaming source revision at an
immutable commit, the exact published filterbank, importance vector and
parameters, a locked runtime with approved reference outputs, the deployed
receiver geometry with a causal masker estimate and an energy contract, and a
rights-cleared independent masker and listener cohort. Then score listener
outcomes independently, audit output energy, measure target timing and complete
an OFF-by-default opt-in provider intake. Until then the candidate stays
**DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`,
`onnxruntime_invoked=false`, `runtime_invoked=false`,
`native_engine_built=false`, `sdk_data_dir_added=false`,
`research_module_imported=false`, `numpy_or_scipy_imported=false`,
`listener_outcome_claimed=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-NOISE-AWARE-SHAPING-PLUS-DRC]`, stable-field digest); the mutable
full `plan/swarm/TASKS.json` is never read into, hashed by or pinned to this
package. No provider, descriptor, registry, installed default, public ABI,
research module, shared build or CI is changed.

## Separation from sibling evidence

The full-band receive DRC, feed-forward compressor, envelope AGC, EBU
R128/loudnorm, static target gain with peak ceiling, peak limiter,
AdaptDRC/SSDRC and STOI/ESTOI packages are **separate evidence**. They use
different candidates, fixtures, cadences and dispositions. This package does
not pool, import, reuse or reinterpret their outputs, metrics or adapters. The
research note and inventory are pinned provenance only; they are not source
archives, qualified references or listener outcomes, and they are not changed.
