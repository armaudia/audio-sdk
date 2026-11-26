<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-AUXIVA — AuxIVA source/runtime and permutation blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`AuxIVA` (`component_id=auxiva`). The acceptance profile is **Spatial**, assigned
by `plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact AuxIVA source, runtime, adapter, immutable revision, license identity,
numeric output and rights-cleared multi-channel corpus are **absent**. This
package records that exact blocker, separates AuxIVA from the bundled H-GTCRN
component and runs a bounded deterministic **synthetic two-source /
two-microphone boundary surrogate**. It is not AuxIVA, does not import or load
AuxIVA, H-GTCRN, Pyroomacoustics, Asteroid, a checkpoint, a native library, real
audio, a corpus or a device clock, and makes no separation, quality, timing,
listening, benchmark or release claim. Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=auxiva`) is `considered`,
`disposition=sdk-reference`, `verification_profile=spatial`, with the plan note
“Separate the component from bundled H-GTCRN; qualify multi-channel source
permutation.” The only evidence link is
`research/noise_suppression_candidate_census.md`, where AuxIVA appears **only
inside the H-GTCRN row** (“two-microphone low-SNR enhancement combining GTCRN,
FD-WPE, AuxIVA and spatial features”). That row describes H-GTCRN, not a
standalone AuxIVA source, revision, license, runtime or numeric result.

Consequently:

- no exact AuxIVA package, source tree, runtime, adapter or pinned revision is
  staged at `data/checkouts/auxiva`, `data/envs/auxiva`, `data/models/auxiva` or
  `adapters/auxiva`;
- no license identity, artifact hash, build/archive identity or adapter setting
  exists for AuxIVA itself;
- no label-bearing multi-channel mixture, source permutation reference, output
  scale policy or held-out separation score exists;
- no target-device timing, listening result, independent review, provider
  intake or release approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-AUXIVA`, `aacd6b19b51d4ae2d125ed40488a0e5a8357ec82` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Surrogate geometry | 2 sources, 2 microphones, 16 kHz, synthetic samples only |
| Added content delay | 0 samples; no device timing claim |
| Clock drift | not supported; nonzero `clock_ppm` is rejected |
| Provider registration, default, ABI, CI | none |

The surrogate applies a frozen integer mixing matrix and its exact inverse to
fixed synthetic sources. It exists only to exercise strict parsing, fixture
arithmetic, permutation/scale ambiguity, streaming boundary equivalence, reset
and adverse rejection. It is **not** AuxIVA and cannot qualify the candidate.

## Spatial profile application

`plan/swarm/VERIFICATION.md` Spatial row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry and layout | synthetic only | Frozen integer nanometre 3-microphone linear/planar fixture; no measured array or device layout |
| Timestamp calibration | synthetic only | Explicit integer capture offsets and zero drift; one-sample TDOA exact at 16 kHz; no device clock measured |
| Source/target/reference conditions and permissions | blocked | No real multi-channel recording, condition, consent or usage grant |
| Task-matched held-out localization/activity/extraction | blocked | No held-out source labels, separation output or permutation-resolved scorer |
| Leakage, target damage, channel loss | blocked | No real target, interference or channel-loss stratum |
| Room/reference changes | blocked | No measured room or reference change; WPE and H-GTCRN evidence are not pooled |

## Exact synthetic geometry

- Microphone positions and the source direction are integers in nanometres.
- The speed of sound is `343 nm/ns`; one 16 kHz sample is exactly `62,500 ns`.
- `m0=(0,0,0)`, `m1=(21,437,500,0,0)`, `m2=(0,21,437,500,0)` nm; direction
  `(1,0,0)` with exact norm 1.
- Plane-wave TDOA is `[0, -62,500, 0] ns`, exactly `[0, -1, 0]` samples and
  `[0, -65,536, 0]` q16. No floating-point trigonometry is used.
- Capture offsets and clock drift are zero; nonzero drift is rejected.

## Exact fixture and controls

The fixture synthesises 4,096 samples from a fixed 64-entry integer sine table:
`s1` amplitude 12,000 step 1 phase 0; `s2` amplitude 6,000 step 7 phase 11.
The integer mixing matrix is `[[3,1],[2,3]]`; the exact inverse is
`[[3,-1],[-2,3]]` and returns `7·s1` and `7·s2` without residual. Source
energies are `294,886,277,056` and `73,722,206,144`; source correlation is
`-2.1747897e-05`.

| Case | Exact | Assignment | Output RMS | Observation |
| --- | --- | --- | --- | --- |
| `matched_inverse_control` | true | `[0,1]` | `59394.379188896`, `29697.317871053` | Exact identity assignment; residual `0.0` |
| `permuted_inverse_control` | true | `[1,0]` | `29697.317871053`, `59394.379188896` | Equally exact with swapped assignment |
| `scaled_inverse_control` | true | `[0,1]` | `118788.758377792`, `59394.635742106` | Equally exact up to the doubled gain |
| `identity_control` | true | `[0,1]` | `25805.762305879`, `21212.089830669` | Raw mixture passthrough; assignment margin `26.129492343 dB` |

All four cases have `nonfinite_samples=0` and `scale_pinned=false`. The
permuted and scaled controls are **not promoted**: they record exactly why the
separation score alone cannot resolve source identity or output gain.

The fixed-step second-order decorrelation control (16 iterations, step `0.25`,
matrix clamp `±4`) converges to `[[2.266806205889, -1.568654555377],
[-1.568654555377, 2.964008840854]]`. Its SI-SDR is `9.218369316 dB` for output 1
to source 1 and `0.493697268 dB` for output 2 to source 2, with assignment
`[0,1]` and margin `17.449111216 dB`. It is **not AuxIVA**, has no learned
weights and cannot qualify the candidate.

## Permutation and scale qualification (blocked)

A row permutation of the exact inverse produces an equally exact result with
swapped outputs; the synthetic score cannot choose between them. The scale
control doubles every output and remains exact under scale-invariant SI-SDR.
`report.json` therefore records:

- `permutation_qualification.status="blocked"`,
  `heldout_labels_present=false`, `score_alone_resolves_permutation=false`;
- `scale_qualification.status="blocked"`, `scale_resolved=false`,
  `si_sdr_scale_invariant=true`;
- `qualification.permutation_qualified=false` and
  `qualification.scale_qualified=false`.

No external label assignment, permutation resolver, normalization policy or
exact-runtime output exists. Multi-channel source permutation remains
unqualified.

## Adverse, missing and invalid handling

`report.json` records 36 rejected inputs, each with an unchanged fixed-matrix
session digest. Rejections include duplicate JSON key, `NaN`/`Infinity`
constants, malformed JSON, missing/extra/wrong config fields, 8 kHz, mono,
256-sample frame, `int16`, clock drift, boolean fields, duplicate/unknown mic,
non-integer/out-of-range position, non-normalizable direction, wrong matrix
shape, singular/nonfinite/boolean matrix, channel-length mismatch, empty
channel, nonfinite/out-of-range/string/boolean samples, reset epoch 0/-1, and
missing/relative/bad-commit/wrong-rate/wrong-channel/bad-hash/extra-field caller
asset manifests. Missing real recordings, exact runtime outputs and labels are
`blocked`, never passes.

The caller asset contract validates identity only. A generic temporary manifest
with caller-owned files validates both hashes and the declared geometry but
reports `loaded=false`, `executed=false`, `imported=false`. No workspace
manifest is staged. A hash-matched placeholder is never accepted as the pinned
AuxIVA artifact.

## Streaming, reset and determinism

The fixed-matrix session is block invariant: arbitrary 160/480/800/137/641
sample chunks reproduce the full-block output exactly (`all_match=true`,
`accepted_samples=4096`). Reset to epoch 1 matches a fresh session; epoch 0 and
−1 are rejected with the session digest unchanged. `run.py` builds the report
three times and refuses to write unless every payload is byte-identical.

## Separation from H-GTCRN and sibling evidence

H-GTCRN is a separate two-microphone bundle that combines GTCRN, FD-WPE, AuxIVA
and spatial features. This package does not import, pin, execute, score or reuse
H-GTCRN source, checkpoint, adapter, runtime or evidence
(`h_gtcrn_evidence_pooled=false`, `this_package_uses_h_gtcrn=false`). The
merged multichannel WPE packages (`offline-multichannel-wpe`,
`online-multichannel-wpe`) and the mono `speechbrain-sepformer-dns4` package are
separate evidence with their own fixtures, cadences and dispositions. Their
README/report files are pinned only as boundary references; no metric, output
or result is pooled.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, fixture, exact inverse controls, blind surrogate, session, report/contract builders. |
| `run.py` | Builds the report three times, requires byte identity, regenerates artifacts. |
| `report.json` | Canonical machine-readable Spatial report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
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
| `sdk:docs/task-evidence/offline-multichannel-wpe/README.md` | `8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9` |
| `sdk:docs/task-evidence/offline-multichannel-wpe/report.json` | `4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba` |
| `sdk:docs/task-evidence/online-multichannel-wpe/README.md` | `3615f6fc66d3c8d15a4cd77ccdc1f8a2e5f9c6cd9a1a20b9263814bfb2c34013` |
| `sdk:docs/task-evidence/online-multichannel-wpe/report.json` | `df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f` |
| `sdk:docs/task-evidence/speechbrain-sepformer-dns4/README.md` | `1cc709249b21f2cdb5ad4bc3510b9479e3e07f6630aa45bea4cad22ea8698ecc` |
| `sdk:docs/task-evidence/speechbrain-sepformer-dns4/report.json` | `e56b83bde079fca411ca8d98890fcc75e8302834b0df268c0fc87d43b2d32013` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-AUXIVA
TASK=$WT/docs/task-evidence/auxiva
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

1. `RG-01` exact pinned AuxIVA source or runtime and immutable revision.
2. `RG-02` isolated hash-pinned runtime admission and reproducible build.
3. `RG-03` artifact, corpus, redistribution and product-use rights.
4. `RG-04` exact-runtime multi-channel output parity.
5. `RG-05` multi-channel source-permutation qualification.
6. `RG-06` output scale, channel identity and reset qualification.
7. `RG-07` rights-cleared held-out spatial separation scoring.
8. `RG-08` target timing, opt-in provider intake, independent review and release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed AuxIVA source or runtime and
immutable revision, admit an isolated hash-pinned runtime, clear all artifact
and corpus rights, reproduce exact multi-channel outputs, qualify source
permutation and scale on a rights-cleared label-bearing held-out cohort, measure
target timing and complete opt-in provider intake. Until then the candidate
stays **DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-AUXIVA]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry,
installed default, shared build or CI is changed.
