<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL: hybrid readiness blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the `neural-plus-kalman-howling-control` row. It is **not** a neural/Kalman
howling suppressor: no neural network, weight loader, inference path, Kalman
filter, covariance update, feedback-path estimator, adaptive gain, checkpoint,
closed-loop simulator, real recording, listening result, device measurement,
benchmark or release claim is included. **No result here qualifies the
catalogued hybrid candidate.**

## Exact blocker: algorithm, checkpoint, closed-loop proxy, runtime and rights absent

A bounded, read-only search of named workspace paths found **no exact
neural-plus-Kalman source**, **no authoritative architecture/parameter set**,
**no released checkpoint**, **no rights-cleared closed-loop proxy with held-out
physical paths**, **no hash-pinned runtime or loader** and **no rights
decision**. Nothing was cloned, downloaded, trained, reconstructed, converted,
fitted or substituted.

| Item | Status |
| --- | --- |
| Source revision | **Absent.** The pinned feedback census names the neural/Kalman hybrid family and cites NeuralKalmanAHS, HybridAHS and AHS_2023, but records no repository carrying source at a 40-hex revision, license, entry point or per-file SHA-256 manifest |
| Algorithm and parameters | **Absent.** Neural architecture, layer/context window, output activation, Kalman FFT/hop/window, process/measurement covariance, forgetting factor, regularization, update order, delay alignment, precision and reset policy are unrecorded |
| Checkpoint | **Absent.** No weights, SHA-256, byte count, format, tensor layout, producing revision, training-data provenance or weight terms exist locally; no weight is opened or loaded |
| Closed-loop proxy | **Absent.** No recursive microphone plus actual playback-reference proxy with path digest, loop gain, delay, saturation, initial state and held-out physical path split exists |
| Runtime | **Absent/unpinned.** No hybrid runtime, checkpoint loader, lockfile, wheel set or closed-loop harness exists; `scripts/ci.py` is the SDK CI, not this candidate |
| Rights | **Unrecorded/blocked.** Source license, weight terms, training-data terms, corpus permission, output-use grant, measured-loop authorization and independent review are all missing |
| Candidate execution | **None.** No network, inference, filter, path estimate, comparison, ablation, listening or timing run occurred |

The machine-readable record is `report.json` -> `source_probe`,
`algorithm_probe`, `checkpoint_probe`, `fixture_probe`, `runtime_probe`,
`rights_probe`, `absence_evidence`, `required_artifacts` (ART-01 to ART-08),
`exact_blockers` (BLK-01 to BLK-07), `gates` (RG-01 to RG-08) and `geometry`.
`contract.json` carries the same blocker, artifacts and gates.

## Literature boundary

| Field | Recorded value |
| --- | --- |
| Candidate family | Neural/Kalman hybrid; a frequency-domain Kalman filter combined with a self-attentive RNN |
| Named public lead | `YIXUANZ/NeuralKalmanAHS` |
| Related papers | Hybrid AHS (Interspeech 2023); NeuralKalmanAHS journal study (2024) |
| Related public lead | `YIXUANZ/AHS_2023` |
| Different-task lead | `ZLiNJU/AFC-SPEX` (multichannel speaker extraction; different task) |
| Reported streaming design | The neural output becomes the reference used to update the Kalman filter |
| Local implementation | **Absent** |
| Local checkpoint | **Absent** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

The pinned note reports paper values only: NeuralKalmanAHS mean SDR of
`2.65 / 1.98 / 1.45 dB` and PESQ of `2.33 / 2.17 / 2.04` at loop gains
`G = 2 / 2.5 / 3` over 200 utterances. Those values belong to that paper's
dataset, loop construction and metric scope. They are **source-reported**, not
reproduced, not pooled and not comparable to this package. The note also records
that the visible public repositories exposed README/demo material and audio
files without source implementation or checkpoints.

## What the task asks and what is proven here

The board row is `feasibility` mode and asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence, then reproduce the
exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK
adapter once its prerequisites pass. The plan note is exact:
**require exact algorithm/checkpoint and a closed-loop proxy with held-out
physical paths.** The board also says a readiness conclusion with an exact
external blocker is an accepted investigation handoff.

This package proves only the **negative** side of the gate:

- the exact source/algorithm/checkpoint/fixture/runtime/rights prerequisites
  are absent (bounded probes, no network, no directory walk, no checkpoint
  open);
- every structurally valid caller-supplied bundle is **deferred** because the
  external artifacts are absent, while invalid, missing, wrong-shape,
  wrong-update-order, nonfinite, synthetic-proxy, missing-held-out-path,
  unresolved-rights and unequal-comparison requests are rejected before any
  artifact check;
- the declared neural-reference plus per-bin Kalman geometry cannot be
  represented by the installed v0 mono path, which has no playback reference
  and no model-asset slot for a neural checkpoint;
- the historical closed-loop pilot contains six controllers but **no
  neural/Kalman hybrid row**, so it cannot be inherited as matched evidence;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that the hybrid family is unsuitable. It records the exact
external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/neural-plus-kalman-howling-control/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  hybrid provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider and no adapter source.
- No provider is registered, enabled by default or selected as a default.
- No real corpus, audio or weights are read. All harness stimuli are analytic
  or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain,
  closed-loop, inference, benchmark or release claim is made.
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
| Sweeps / steps / impulses / silence | `stimulus_probe`: synthetic harness characterisation only | No candidate input or output |
| Clean speech and task control | `dsp_profile` and `profile_mapping` mark blocked | No permitted cohort |
| Gain and response | `profile_mapping.gain_and_frequency_response=blocked_no_candidate_output` | Unmeasured |
| Attack / release | `blocked_no_candidate_output` | Unmeasured |
| Headroom / peaks | `blocked_no_candidate_output` | Unmeasured |
| Delay / content mapping | `blocked_no_candidate_output` | No delay is assumed or fitted |
| Numerical behavior | `partial_local_harness_rejection_only` | Local rejection tests only |
| State transitions | `blocked_no_candidate_instance` | No instance exists |
| Interacting nonlinear configs | `blocked_no_candidate_instance` | No instance exists |
| Closed-loop proxy with held-out physical paths | `blocked_no_fixture_and_no_candidate_output` | No loop, no held-out paths |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Task geometry

- `task_kind`: `acoustic_feedback_cancellation_with_neural_kalman_hybrid`; the
  suppressed quantity is the loudspeaker-to-microphone feedback path.
- The candidate family is a **neural reference refinement plus a
  frequency-domain Kalman filter with recursive covariance/gain updates**. It
  requires synchronized microphone and playback-reference signals, exact
  pretrained weights, real-time state and an exact path/delay model.
- No architecture, context window, output activation, FFT size, hop,
  covariance, forgetting factor, regularization, update order, precision,
  delay alignment or reset policy is declared, so geometry is **unverified**.
- The installed public v0 path is 16 kHz mono `f32`, 160 samples per frame. It
  has one channel, no explicit playback reference and no caller-supplied neural
  asset slot in the described adapter, so it cannot represent the declared
  hybrid geometry without a new contract.
- `candidate_output_measured=false`, `installed_v0=false`,
  `provider_registered=false`, `checkpoint_loaded=false`.

## Matched and source-reported evidence

The pinned pilot ran identity, fixed −5 dB margin, adaptive notch, notch plus
margin, block-NLMS AFC and AFC plus 3 dB margin on synthetic and simulated
measured-IR loops. The report records those six controller rows and proves that
**no row is a neural/Kalman hybrid**. Its values keep their original
synthetic/pilot scope; they are not rerun, pooled, inherited or promoted here.
The AMI ES2004a speech and SMARD measured-IR material remain research references
behind pinned reports, not a staged, rights-cleared closed-loop proxy with
held-out physical paths.

The pinned note's NeuralKalmanAHS SDR/PESQ figures are recorded as
`source_reported_literature` with `admitted_as_result=false`,
`reproduced_here=false` and `comparable_here=false`.

## Pins

Paths outside `docs/task-evidence/neural-plus-kalman-howling-control/` are
relative to the `audioml` workspace root; SDK boundary paths are relative to
this SDK worktree.

Pinned base: `9074704819a6af4168f8c9cf3bbe8da50484c29a`. Branch:
`swarm/SDK-NEURAL-PLUS-KALMAN-HOWLING-CONTROL`.

### Source pins (SHA-256)

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` |
<!-- digest-table: end -->

### Boundary pins (SHA-256)

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/task-evidence/adaptive-notch-with-gain-margin/report.json` | `b6732740cab7fafd9e270953d7b8f72b6d7951ee5e6d08c1e344a6e9ed228645` |
| `sdk:docs/task-evidence/afc-spex/report.json` | `b94ac1cc9fb6209a302ce1e6054befe715479d6cec9c2473cd53ba7827b2868d` |
| `sdk:docs/task-evidence/fixed-feedback-gain-margin/report.json` | `c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf` |
| `sdk:docs/task-evidence/kalman-afc/report.json` | `23c346db59373b6528276cc737b5b9457653d74d2920828ea5f20939a07ddb76` |
| `sdk:docs/task-evidence/survey-cln-11/report.json` | `5e997cf8a4838750aafc29ab650ee95a321311dd17c9588ed952e8e04500c93a` |
<!-- digest-table: end -->

### Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `5f05533f82fa3578511d4f1c8ba927fb4e76e529b96356e0c87884c44f633fc9` | 2038 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `46b2b3603d703f67e296a47c70d9774f7151c5e4b9754aec9e85d466b43d6afc` | 16365 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `de952176745f9be83703b07d2d6d3d7f814d5791876e932faf4506c2bf3954c2` | 87021 |
| `report.json` | `55e605d873ac87cd908afd4113b780e4f711887a969e5fcaab9a3d3d720fe2dc` | 42832 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `a45418b400347b6977d631d73e14603ac0d5fd248414f8dc5332eda603301653` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `5cc84ecd8deb9b4ee2197755c546d1ef85af0358d3576f8490d7f8152050dba6` | 4666 |
| `test_reference.py` | `b3e22fc34761782ca84a1341a58495fb6ad69896ff55088998a7ca3f006f454e` | 17312 |
| `verify.py` | `6542a2efd99dc5a92c104ad5fa95f9117f4504349a118f2b18af87de64592b15` | 32901 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`report.json` is canonical JSON (sorted keys, compact separators, no trailing
newline, `allow_nan=False`); its SHA-256 is also the canonical report digest.
`SOURCES.sha256` pins every source, boundary and task-local artifact except
itself; `README.md` is excluded from both `SOURCES.sha256` and the artifact
table only to avoid a self-reference cycle. `verify.py` fails closed on any
missing, stale, malformed, duplicated or extra pin and on any worktree change
outside this directory.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission gate, synthetic harness controls and canonical report
  builder.
- `run.py`: regenerates report, sidecar, manifest and README table three times
  and fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance and scope regression suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, README digest-table, merge-base scope and cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/neural-plus-kalman-howling-control
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` repeats three times and fails if report, sidecar, manifest or contract
bytes differ. `verify.py` never writes to this directory: it regenerates in
memory, then builds three isolated scratch copies with symlinks to the pinned
read-only inputs and checks cold-start byte identity there. No candidate
runtime is pinned or claimed; the local check used CPython 3.11.5.

## Eight blocked release gates

1. `RG-01` exact neural/Kalman source repository, 40-hex revision and license.
2. `RG-02` exact checkpoint SHA-256, byte count, format, provenance and weight
   terms.
3. `RG-03` rights-cleared closed-loop proxy with path metadata and a held-out
   physical path split.
4. `RG-04` exact neural architecture and Kalman parameter/update-order set,
   runtime lock and installed geometry.
5. `RG-05` hybrid reproduced with identity, Kalman-only and neural-only
   ablations.
6. `RG-06` full DSP matrix and closed-loop failure/adverse controls.
7. `RG-07` held-out physical path result and fixed-margin comparison at equal
   output gain.
8. `RG-08` default-off opt-in adapter, authorized listening, benchmark
   validation, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`contract.json -> upstream_blocker.reopen_condition`.
