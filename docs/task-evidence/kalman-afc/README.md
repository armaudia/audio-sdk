<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-KALMAN-AFC: Kalman AFC readiness blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the `kalman-afc` row. It is **not** Kalman AFC: no Kalman filter, feedback-path
estimator, covariance update, adaptive gain, checkpoint, closed-loop harness,
real recording, listening result, device measurement, benchmark or release
claim is included. **No result here qualifies the catalogued Kalman AFC
candidate.**

## Exact blocker: source, parameter set, matched fixture, runtime and rights absent

A bounded, read-only search of named workspace paths found **no exact Kalman AFC
source**, **no authoritative FFT/covariance/forgetting parameter set**, **no
synchronized microphone plus playback-reference matched closed-loop fixture**,
**no hash-pinned runtime or harness** and **no rights decision**. Nothing was
cloned, downloaded, reconstructed, fitted, substituted or upmixed.

| Item | Status |
| --- | --- |
| Source revision | **Absent.** The pinned feedback/AFC census names the family but records no repository, 40-hex revision, license, entry point or per-file SHA-256 manifest |
| Parameter set | **Absent.** FFT size, hop, window, process/measurement covariance, forgetting factor, regularization, delay alignment, precision and reset policy are unrecorded |
| Checkpoint | **Not required by the classical family, absent for named leads.** No hybrid/neural checkpoint is staged or admitted |
| Matched fixture | **Absent.** No microphone plus playback-reference closed loop with path digest, loop gain, delay, saturation and held-out paths exists locally |
| Runtime | **Absent/unpinned.** No Kalman AFC runtime, lockfile, wheel set or closed-loop harness exists; `scripts/ci.py` is the SDK CI, not this candidate |
| Rights | **Unrecorded/blocked.** Source license, corpus permission, output-use grant, measured-loop authorization and independent review are all missing |
| Candidate execution | **None.** No filter, path estimate, covariance update, gain, comparison or listening run occurred |

The machine-readable record is `report.json` -> `source_probe`,
`parameter_probe`, `checkpoint_probe`, `fixture_probe`, `runtime_probe`,
`rights_probe`, `absence_evidence`, `required_artifacts` (ART-01 to ART-07),
`exact_blockers` (BLK-01 to BLK-06), `gates` (RG-01 to RG-08) and `geometry`.
`contract.json` carries the same blocker, artifacts and gates.

## What the task asks and what is proven here

The board row is feasibility mode and asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence, then implement or
wrap a minimal reference on the relevant public adapter boundary and compare
**gain-before-feedback and recovery with fixed margin at equal output gain**. It
also says a readiness conclusion with an exact external blocker is an accepted
investigation handoff. This package records that conclusion.

This package proves only the **negative** side of the gate:

- the exact source/parameter/fixture/runtime/rights prerequisites are absent
  (bounded probes, no network, no directory walk);
- every structurally valid caller-supplied bundle is **deferred** because the
  external artifacts are absent, while invalid, missing, wrong-shape,
  nonfinite, synthetic-proxy, unresolved-rights and unequal-comparison
  requests are rejected before any artifact check;
- the declared reference-based feedback-cancellation geometry cannot be
  represented by the installed v0 mono path;
- the historical closed-loop pilot contains six controllers but **no Kalman
  AFC row**, so it cannot be inherited as matched evidence;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Kalman AFC is unsuitable. It records the exact
external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/kalman-afc/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, provider registration, board/handoff files, CI, rulesets and
  `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  Kalman AFC provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider.
- No provider is registered, enabled by default or selected as a default.
- No real corpus, audio or weights are read. All harness stimuli are analytic
  or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, maximum-stable-gain,
  feedback-cancellation, benchmark or release claim is made.
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
| Gain-before-feedback vs fixed margin | `task_requirement.status=blocked_no_candidate_and_no_measured_loop` | No comparison run |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Task geometry

- `task_kind`: `acoustic_feedback_cancellation_with_reference`; the suppressed
  quantity is the loudspeaker-to-microphone feedback path.
- The candidate family is a **frequency-domain Kalman filter with recursive
  covariance/gain updates**. It requires synchronized microphone and playback
  reference signals, real-time state and an exact path/delay model.
- No FFT size, hop, covariance, forgetting factor, regularization, precision,
  delay alignment or reset policy is declared, so geometry is **unverified**.
- The installed public v0 path is 16 kHz mono `f32`, 160 samples per frame. It
  has one channel and no explicit playback reference, so it cannot represent
  the declared feedback-cancellation geometry without a new contract.
- `candidate_output_measured=false`, `installed_v0=false`,
  `provider_registered=false`.

## Matched evidence

The pinned pilot ran identity, fixed −5 dB margin, adaptive notch, notch plus
margin, block-NLMS AFC and AFC plus 3 dB margin on synthetic and simulated
measured-IR loops. The report records those six controller rows and proves that
**no row is Kalman AFC**. Its values keep their original synthetic/pilot scope;
they are not rerun, pooled, inherited or promoted here. The AMI ES2004a speech
and SMARD measured-IR material remain research references behind pinned
reports, not a staged or rights-cleared matched fixture.

## Pins

Paths outside `docs/task-evidence/kalman-afc/` are relative to the `audioml`
workspace root; SDK boundary paths are relative to this SDK worktree.

Pinned base: `f006454da9a72fbfd394e2b5bd05105201a9cd29`. Branch:
`swarm/SDK-KALMAN-AFC`.

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
| `sdk:docs/task-evidence/fixed-feedback-gain-margin/report.json` | `c7cd3a0518c315a4871b011bd89d74d09207d2d5bf84105c5877a76bf158b2bf` |
| `sdk:docs/task-evidence/survey-cln-11/report.json` | `5e997cf8a4838750aafc29ab650ee95a321311dd17c9588ed952e8e04500c93a` |
<!-- digest-table: end -->

### Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `257b58b6a435ad2d68675b5f24f9fac5cb60e090fb07c6b7127229bb47d8e1e5` | 1813 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `170e95b5c7bb274b92935bbbb4859a77a567e7db46b319b966cc832f40a1b8f7` | 13564 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `8d2845377f18cb5f02854926129447651978c3b88e031bf958b4b15cee00f2de` | 77346 |
| `report.json` | `23c346db59373b6528276cc737b5b9457653d74d2920828ea5f20939a07ddb76` | 35337 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `8d25d57f5ae406da533700730d58bf039310238172f65cef2e3311f0bb676c1c` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `c9e80069098820cd9b8ffc2bfeae2c04509884a320d41542fb35dc117594e67f` | 4632 |
| `test_reference.py` | `856ecee90e26ed7d742fc2f3957b1c77f08ba9fc0ee4694adcf663f7504ffc83` | 19888 |
| `verify.py` | `657aa051275d49ea0e9b157259eb732dc1fc7ad250c3f0bbc237463d1e4e99dd` | 31759 |
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
- `reference.py`: stdlib-only probes, strict validators, fail-closed admission
  gate, synthetic harness controls and canonical report builder.
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
cd docs/task-evidence/kalman-afc
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` repeats three times and fails if report, sidecar, manifest or contract
bytes differ. `verify.py` never writes to this directory: it regenerates in
memory, then builds three isolated scratch copies with symlinks to the pinned
read-only inputs and checks cold-start byte identity there. The final
reproduction uses pinned Python 3.12.16.

## Eight blocked release gates

1. `RG-01` exact Kalman AFC source repository, 40-hex revision and license.
2. `RG-02` rights-cleared synchronized microphone plus playback-reference
   matched closed-loop fixture with path, gain, delay, saturation and held-out
   split.
3. `RG-03` source, fixture, output-use and measured-loop rights.
4. `RG-04` exact parameter/FFT/covariance set, runtime lock and installed
   geometry.
5. `RG-05` candidate gain-before-feedback and recovery measured.
6. `RG-06` fixed-margin comparison at equal output gain with controls and
   adverse cases.
7. `RG-07` default-off opt-in adapter intake and independent exact-head review.
8. `RG-08` benchmark validation, product decision and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`contract.json -> upstream_blocker.reopen_condition`.
