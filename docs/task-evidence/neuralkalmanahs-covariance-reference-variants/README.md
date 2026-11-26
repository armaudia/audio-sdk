<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS: readiness blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the `neuralkalmanahs-covariance-reference-variants` row. It is **not**
NeuralKalmanAHS: no upstream source, model code, covariance-integration or
reference-integration checkpoint, weight, configuration, license text,
runtime, corpus, candidate output, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies either
integration variant.**

## Exact blocker: source, variant checkpoints, runtime, rights and cohort absent

A bounded, read-only search of named workspace paths found **no local
`NeuralKalmanAHS` or `AHS_2023` checkout**, **no trained covariance-variant or
reference-variant checkpoint, model card or configuration**, **no hash-pinned
inference runtime or streaming harness**, **no matched closed-loop cohort** and
**no written rights decision**. Nothing was cloned, downloaded, installed,
extracted, ported, reconstructed, trained, fitted or substituted.

The pinned research note records the exact upstream situation: the public
`YIXUANZ/NeuralKalmanAHS` and `YIXUANZ/AHS_2023` repositories expose README and
demo HTML/CSS/audio files, **no source implementation or model checkpoints**
were present in their visible file listings, and **no release assets were
listed for NeuralKalmanAHS**. The journal study compares cascaded NN+Kalman,
recursively trained variants, and neural networks embedded in Kalman
reference/covariance estimation. Those are research references, not a runnable
candidate.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local `NeuralKalmanAHS`/`AHS_2023` tree; revision, tree digest, file count and license file are `null` |
| Runnable implementation | **Absent/reported demo-only.** The pinned note records README/demo materials without source |
| Covariance-variant checkpoint | **Absent.** No `.pt`, `.pth`, `.ckpt`, `.onnx`, `.safetensors`, `.bin` or `.pkl` state; no covariance parameterisation, model card or config digest |
| Reference-variant checkpoint | **Absent.** No trained reference-integration state, model card or config digest |
| Runtime | **Absent/unpinned.** No interpreter lock, framework version, platform record, offline path or import-parity vector |
| License and rights | **Absent/blocked.** No byte-identical license text, SHA-256 or written use/redistribution/derived-output decision |
| Candidate geometry | **Absent.** No sample rate, frame, hop, STFT size, channel count, Kalman state dimension, covariance parameterisation, network structure, layer count or parameter count is recorded per variant |
| Matched cohort | **Absent.** No rights-cleared closed-loop corpus with loop gain, delay, saturation and held-out speakers/paths |
| Candidate execution | **None.** No build, model load, inference, SDR, PESQ, stability, timing or listening run occurred |

The machine-readable record is `report.json` -> `integration_variants`,
`source_probe`, `checkpoint_probe`, `runtime_probe`, `cohort_probe`,
`license_probe`, `rights_probe`, `required_artifacts` (ART-01 to ART-07),
`exact_blockers` (BLK-01 to BLK-06), `release_gates` (RG-01 to RG-08),
`geometry` and `research_controls`. `contract.json` carries the same blocker,
artifacts, gates and variant split.

## Covariance and reference integration are kept separate

The task exists to distinguish two integration points in the NeuralKalmanAHS
family. They are recorded separately and neither is inferred.

| Variant | Integration point | Reported mechanism | Local state |
| --- | --- | --- | --- |
| `reference` | `kalman_reference_estimate` | Network output supplies the Kalman reference used by the recursive update | **Absent.** No source, checkpoint, config or output |
| `covariance` | `kalman_covariance_or_process_noise` | Network is embedded in Kalman covariance or process-noise estimation | **Absent.** No source, checkpoint, config or output |

The pinned note names the family and the general integration points but records
no per-variant architecture, state vector, covariance parameterisation,
checkpoint identity or runtime. `exact_variant_identity_recorded=false`,
`separately_checkpointed=false`, `separately_measured_here=false`, and
`qualifies_candidate=false` for both. The author-reported SDR/PESQ values are
not attributed to either variant (`variant_attribution=not_disambiguated_in_note`).

## What the task asks and what is proven here

The board row is `feasibility` mode. It asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence; reproduce the
exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK
adapter once prerequisites pass; record a concrete blocker if feasibility
fails; and **distinguish covariance and reference integration**. It applies the
DSP acceptance profile.

This package proves only the **negative** side of that gate:

- the exact source, per-variant checkpoints, runtime, rights and cohort
  prerequisites are absent (bounded probes, no network);
- the source is reported as demo materials rather than a runnable
  implementation;
- every structurally valid caller-supplied-asset request is rejected with
  `DEFER` because the artifacts and rights are absent;
- invalid, missing, wrong-shape, nonfinite, out-of-range, unknown-variant and
  inconsistent asset-manifest requests are rejected before any artifact check;
- the covariance and reference integration points are recorded as distinct and
  neither is collapsed into the other;
- the author-reported results are retained with their original scope and are
  never presented as local measurements;
- no candidate geometry is inferred from the paper description;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that NeuralKalmanAHS is unsuitable. It records the exact
external condition required to reopen the investigation.

## Exact scope

- Work is confined to
  `docs/task-evidence/neuralkalmanahs-covariance-reference-variants/`. Shared
  CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  NeuralKalmanAHS provider, descriptor, installed target or public API/ABI
  change exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, checkpoint, weight or audio file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain, SDR,
  PESQ, covariance, Kalman, neural-network, benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`). Mutable status, owner,
  review, handoff, priority, claim, history and every other mutable field never
  enter canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## DSP profile application

The structured inventory assigns the **DSP** acceptance profile
(`plan/swarm/VERIFICATION.md`, pinned below). The profile asks for sweeps,
steps, impulses, silence, clean speech and an intelligibility or load-specific
control, with gain, response, attack/release, headroom, delay, numerical
behavior, state transitions and interacting nonlinear configurations.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Sweeps / steps / impulses / silence | `stimulus_probe`: synthetic harness characterization only | No candidate input or output |
| Clean speech and task control | `profile_mapping` and `required_results` mark blocked | No permitted cohort |
| Gain and response | `blocked_no_candidate_output` | Unmeasured |
| Attack / release | `blocked_no_candidate_output` | Unmeasured |
| Headroom / peaks | `blocked_no_candidate_output` | Unmeasured |
| Delay / content mapping | `blocked_no_candidate_output` | No delay assumed or fitted |
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Covariance/reference distinction | `recorded_variant_split_no_exact_config` | Split recorded; no exact variant identity |
| Candidate output | `blocked_source_checkpoint_runtime_rights_and_cohort_absent` | None |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Historical controls retained, not rerun

The pinned note also contains a prior classical feedback-control pilot on AMI
speech and SMARD measured paths. It is retained as `research_controls` with
`rerun_here=false`, `qualifies_candidate=false` and
`evidence_class=prior_pilot_author_reported_not_rerun`. Its identity, fixed
margin, adaptive-notch, notch-plus-margin, block-NLMS AFC and AFC-plus-margin
rows are **not NeuralKalmanAHS rows**, are not pooled or inherited, and cannot
be used as matched evidence for either integration variant.

## Pins

Paths outside this directory are relative to the `audioml` workspace root; SDK
boundary paths are relative to this SDK worktree. Pinned base:
`feb342c735740f32d64a668cf2234e488cdcdbfe`. Branch:
`swarm/SDK-NEURALKALMANAHS-COVARIANCE-REFERENCE-VARIANTS`.

### Source pins (SHA-256)

<!-- DIGEST_TABLE_SOURCE_START -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` |
<!-- DIGEST_TABLE_SOURCE_END -->

### Boundary pins (SHA-256)

<!-- DIGEST_TABLE_BOUNDARY_START -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
<!-- DIGEST_TABLE_BOUNDARY_END -->

### Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded from this table to avoid a self-reference cycle.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `070f8210326af93027527ed39652521a558037da5c1c00b32786d04879e94705` | 17734 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `668eb4b5d5490c3eb3fe89b6e5d0adcfe371a725e0e14c47ebbe92a20fe06339` | 94621 |
| `report.json` | `6299ed706586384d705ef4fc53698d08a5681a67a1e6d3f452aa42ce445b9789` | 46522 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `0c0c9eed8053e6af62331c3acf57884214db5775a867de979ef3ca320f95fa24` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `69ea2dfc7d0b3cb49dddd279369374d4ddd21a344e03f6abb300ba2604bb5b9b` | 4581 |
| `test_reference.py` | `0b742e1e9c53088330bf8c3c739ac522e533f41c649578d21f21c3205ce7e0d6` | 17441 |
| `verify.py` | `bea7b130353f77678dc6fc58387bd7b1191b033567c8686e598947a6a7c1b5c3` | 16248 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`report.json` is canonical JSON (sorted keys, compact separators,
`allow_nan=False`, no trailing newline); its SHA-256 is also the canonical
report digest. `SOURCES.sha256` pins every source, boundary and task-local
artifact except itself and `README.md`. `verify.py` fails closed on any missing,
stale, malformed, duplicated or extra pin and on any worktree change outside
this directory.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only probes, strict validators, fail-closed admission
  gate, covariance/reference split, synthetic harness controls and canonical
  report builder.
- `run.py`: regenerates report, sidecar, contract, README tables and manifest
  three times and fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance and scope regression suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, README digest-table, merge-base scope and cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/neuralkalmanahs-covariance-reference-variants
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` repeats three times and fails if report, sidecar, contract, README
tables or manifest bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there.

## Eight blocked release gates

1. `RG-01` exact licensed NeuralKalmanAHS/AHS_2023 source revision pinned.
2. `RG-02` covariance and reference checkpoints, model cards and configs
   pinned.
3. `RG-03` rights-cleared matched closed-loop cohort frozen.
4. `RG-04` source, checkpoint, training-data, cohort and output rights
   recorded.
5. `RG-05` runtime, geometry and per-variant integration points pinned.
6. `RG-06` DSP acceptance matrix and numerical behavior measured.
7. `RG-07` author-reported results reconciled and covariance/reference
   distinction measured.
8. `RG-08` opt-in adapter, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies either
variant. The exact reopen conditions are recorded on each gate and in
`contract.json -> upstream_blocker.reopen_condition`.
