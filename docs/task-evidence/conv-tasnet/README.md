<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CONV-TASNET - Conv-TasNet source, rights and separation-evidence blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Conv-TasNet` (`component_id=conv-tasnet`). The acceptance profile is
**Spatial**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed Conv-TasNet source, weights, runtime, adapter, immutable
revision, I/O geometry and numeric output are **absent**. This package records
that exact blocker, applies the Spatial profile to a bounded deterministic
synthetic two-source separation surrogate, and makes no separation, quality,
latency, listening, benchmark or release claim. It is **not Conv-TasNet**: no
learned encoder, mask network, decoder, weight file, native library, real audio,
corpus, model, device clock or upstream code is present, copied, downloaded,
loaded, imported or executed. Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=conv-tasnet`) is `considered`,
`disposition=sdk-model`, `verification_profile=spatial`, area
`Spatial and speaker`, with the plan note "Pin the separation model and score
permutation and target leakage independently." Its only evidence link is
`research/category_registry.json`.

The pinned registry supplies only a paper reference, `S08` "Conv-TasNet paper",
`https://arxiv.org/abs/1809.07454` (arXiv 1809.07454), under the `SPK-01`
generic speech/source separation category. It records no source repository, immutable revision,
checkpoint, weight digest, parameter count, sample rate, hop, window, source
count, license identity, training-data statement or numeric output. It is not a
code or weight license.

Consequently:

- no Conv-TasNet source, weights, runtime, adapter or pinned revision is staged
  at `data/checkouts/Conv-TasNet`, `data/checkouts/conv-tasnet`,
  `data/models/conv-tasnet`, `data/envs/conv-tasnet` or
  `adapters/conv-tasnet`;
- no immutable source/weight hash, build/archive identity, parameter layout,
  sample rate, hop, window, source count, permutation policy, lookahead or
  numeric output exists for Conv-TasNet itself;
- no upstream LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and returns
  one stream; there is no accepted multi-output separation provider geometry,
  descriptor, registry entry or output-channel mapping;
- no real speech, two-speaker corpus, mixture/clean pair, consent, held-out
  split, SI-SDR/leakage/damage score or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CONV-TASNET`, `6967a728b5c4048fb01ed4522a76a6906fbcffe2` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/window/source count asserted |
| Surrogate | fixed 25-tap complementary integer low/high band split |
| Surrogate content delay | 12 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer FIR band splitter over a frozen synthetic
mono two-source mixture. It is **not Conv-TasNet**, is not learned, uses no
weights and cannot qualify the candidate.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry, layout, timestamp calibration | blocked | No array geometry, channel layout, device clock or calibration; mono synthetic sample indices only |
| Source/target/reference conditions | synthetic only | Two declared synthetic sources, one fixed mixture and one fixed noise level |
| Permissions | blocked | No corpus consent, licence or recording permission |
| Task-matched held-out labels | blocked | No rights-cleared cohort, source labels, mixture/clean pairs or scorer |
| Localization/activity | blocked | Not applicable to mono generic separation; no candidate output exists |
| Extraction | synthetic only | Band-split surrogate on the synthetic mixture; unqualified |
| Target leakage | synthetic only | Independent orthogonal-projection interference leakage per source |
| Target damage | synthetic only | Zero-mean SI-SDR and level change per source; no listening |
| Channel loss | synthetic only | Mono fixture has no channel; missing-source and no-substitution probes only |
| Room/reference change | synthetic only | Reference-order swap replay on identical mixture bytes; no room change |
| Listening | blocked | No permitted listening or MUSHRA-style result |

Every extraction, leakage, damage, channel and reference row is
`qualifies=false`. Synthetic exactness means only that the fixture is
self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Fixture length: 8,064 samples (0.504 s), two sources plus one fixed noise
  level.
- Source 0 `tonal_low_band`: embedded 64-entry sine table at index steps 1, 2
  and 3 with a 16-step envelope, nominal amplitude 12,000 in integer sample
  units.
- Source 1 `broadband_high_band`: deterministic LCG values with alternating
  sample sign and an 8-step envelope, nominal amplitude 9,000.
- Noise: deterministic LCG at amplitude 30; mixture is the clamped integer sum.
- Surrogate: fixed symmetric 25-tap low-band FIR (Q15 integer, scale 32,768),
  and a high band equal to the declared 12-sample delayed input minus the low
  band. The two bands reconstruct the delayed mixture exactly.
- Calibration region `[0, 2000)` selects the permutation by maximum integer
  correlation sum. Evaluation region `[4000, 8000)` scores the selected
  assignment; the two regions do not overlap.
- Metric: zero-mean scale-invariant SDR in integer millidB. Leakage is the
  orthogonal projection of the target estimate onto the interfering source,
  reported relative to the target energy.

Measured synthetic observations (all unqualified):

| Item | Source 0 | Source 1 |
| --- | ---: | ---: |
| Evaluation SI-SDR, millidB | 7839 | 9790 |
| Mixture-passthrough control, millidB | -1646 | 1809 |
| Improvement over control, millidB | 9485 | 7981 |
| Target level change, millidB | -379 | -543 |
| Interference leakage, millidB | -17136 | -19850 |
| Peak, milli | 371 | 346 |

The calibration assignment is `[0, 1]`, matches the evaluation oracle and beats
the swapped assignment by 53,547 millidB. The separation model digest and the
scoring-protocol digest are pinned separately; the leakage measure does not
depend on the permutation choice. The high separation values are an artifact of
a deliberately band-disjoint synthetic fixture, not evidence of real two-speaker
performance.

## Adverse, missing and invalid handling

`report.json` records 60 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, non-object root, missing/extra config fields, 8 kHz, 44.1 kHz, stereo,
256-sample frame, `int16`, one/three separated sources, clock drift, linear
resampling, boolean rate/source count, missing frame, wrong frame count, invalid
valid-count, nonfinite input, non-zero padding, string and boolean samples,
wrong input position, epoch mismatch, reset epoch 0/-1/non-increasing, negative
reset position, missing/extra/relative/bad-hash/bad-commit/wrong-channel/
wrong-source-count/wrong-format/wrong-frame/negative-latency caller manifests,
malformed fixture length/source/tap/region/delay specs, tampered or learned
model specs, tampered or oracle-claiming scoring specs, and invalid chunk plans.
Missing real recordings, weights, runtime outputs and labels are `blocked`,
never passes.

The caller asset contract validates declaration identity only. It never reads,
loads, imports or executes a source tree, weight file or runtime. A hash-matched
placeholder is never accepted as the pinned Conv-TasNet artifact.

## Streaming, reset and determinism

The probe is frame-clocked: arbitrary caller chunks
`160/320/480/800/640/160` reproduce the full-block low and high bands exactly
(`all_match=true`, `accepted_samples=8064`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0, negative and non-increasing epochs are rejected with
the state digest unchanged. A 137-sample final partial frame advances state by
exactly 137 samples, emits 160 outputs per band and leaves the tail invalid
samples zero. `run.py` builds the report three times and refuses to write unless
every payload is byte-identical.

## Separation from sibling evidence

The merged `beam-tasnet-beam-guided-tasnet` spatial admission package and the
`speechbrain-sepformer-dns4` enhancement blocker are separate proposals with
their own fixtures, assets, metrics and dispositions. The merged
`si-sdr-sdr-and-snr` package is a separate metric note. This package does not
import, pool, score or reuse their source, fixtures, metrics or results. Their
README, report and contract files are pinned only as read-only boundary
references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen two-source fixture, band-split surrogate, pinned model/scoring, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Spatial report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sdk:docs/task-evidence/beam-tasnet-beam-guided-tasnet/README.md` | `a114f3b8ca0d870bf6059bed42c6a799dfce7b54b57fef124e3bb99bf1ae23f5` |
| `sdk:docs/task-evidence/beam-tasnet-beam-guided-tasnet/report.json` | `52c470ef552a0dac700e7a041ccb95794677c241a8c9ff9717d8a49c79ef8d7b` |
| `sdk:docs/task-evidence/beam-tasnet-beam-guided-tasnet/contract.json` | `adfab4e9cb4aee3e49e66472433fae27e55876400c6903ad3d1beff8e495c350` |
| `sdk:docs/task-evidence/speechbrain-sepformer-dns4/README.md` | `1cc709249b21f2cdb5ad4bc3510b9479e3e07f6630aa45bea4cad22ea8698ecc` |
| `sdk:docs/task-evidence/speechbrain-sepformer-dns4/report.json` | `e56b83bde079fca411ca8d98890fcc75e8302834b0df268c0fc87d43b2d32013` |
| `sdk:docs/task-evidence/speechbrain-sepformer-dns4/contract.json` | `0443cccff0e709c0893e6821e090fa1145f40fc4f0933600bab256c8dadbcb1e` |
| `sdk:docs/task-evidence/si-sdr-sdr-and-snr/README.md` | `16bc05e63afdb209ba2a9657b7977c29f7d15f9eb3d6e8d24e316b3d2ef671a3` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CONV-TASNET/docs/task-evidence/conv-tasnet
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CONV-TASNET diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned Conv-TasNet source, weights and runtime with an immutable
   revision, license identity, parameter/geometry record and adapter settings.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build, verified
   weight identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` exact candidate input rate, hop, window, source count, permutation and
   output alignment mapped into the installed mono stream with byte-level
   parity.
5. `RG-05` task-matched held-out two-speaker separation qualification with
   independently pinned permutation, SI-SDR, leakage, target damage and
   channel/room/source-condition strata.
6. `RG-06` streaming state, reset, latency, availability, source-count change and
   nonfinite behavior at the exact runtime.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or downstream ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed Conv-TasNet source, weights and
runtime with an immutable revision and documented geometry, admit an isolated
hash-pinned runtime, clear code/weight/training-data/corpus rights, admit a mono
two-output separation boundary with exact parity, pin the permutation and
leakage scoring independently, reproduce exact output, qualify separation on a
rights-cleared task-matched held-out two-speaker cohort, measure target timing
and complete opt-in provider intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-CONV-TASNET]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
