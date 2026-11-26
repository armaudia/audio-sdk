<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURAL-KALMAN-FILTERING-NKF: Neural Kalman filtering readiness blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the `neural-kalman-filtering-nkf` row. It is **not** Neural Kalman filtering:
no echo-path model, learned adaptation controller, covariance or gain update,
checkpoint, weight file, model card, streaming harness, matched room fixture,
candidate output, listening result, device measurement, benchmark or release
claim is included. **No result here qualifies the catalogued NKF candidate.**

## Exact blocker: source, model checkpoint, fixture, runtime and rights absent

A bounded, read-only search of named workspace paths found **no exact NKF
source**, **no trained checkpoint, weight file, model card or architecture /
parameter set**, **no paired far-end/microphone room fixture or frozen
RIR/render set**, **no hash-pinned inference runtime or streaming harness** and
**no rights decision**. Nothing was cloned, downloaded, installed, extracted,
trained, reconstructed, fitted or substituted.

| Item | Status |
| --- | --- |
| Source revision | **Absent.** The pinned AEC census names the Neural Kalman filtering family in one row and records no repository, 40-hex revision, license, entry point or per-file SHA-256 manifest |
| Model checkpoint | **Absent.** No `.pt`, `.pth`, `.ckpt`, `.onnx`, `.safetensors`, `.bin` or `.pkl` state; no model card, byte count, parameter count or training-data record |
| Parameter set | **Absent.** Sample rate, frame, hop, STFT size, state dimension, network structure, learned control target, delay alignment, precision and reset/reconvergence policy are unrecorded |
| Matched fixture | **Absent.** No paired far-end reference and microphone capture, measured RIR, render set, movement segment, noise condition, reset schedule or held-out room/device split exists locally |
| Runtime | **Absent/unpinned.** No NKF runtime, checkpoint loader, lockfile, wheel set or streaming harness exists; `scripts/ci.py` is the SDK CI, not this candidate |
| Rights | **Unrecorded/blocked.** Source license, checkpoint and training-data terms, corpus permission, output-use grant, device/participant terms and independent review are missing |
| Candidate execution | **None.** No build, model load, inference, reset, reconvergence, double-talk, reference-timing or listening run occurred |

The machine-readable record is `report.json` -> `source_probe`,
`parameter_probe`, `checkpoint_probe`, `fixture_probe`, `runtime_probe`,
`rights_probe`, `absence_evidence`, `required_artifacts` (ART-01 to ART-07),
`exact_blockers` (BLK-01 to BLK-06), `gates` (RG-01 to RG-08), `room_profile`
and `geometry`. `contract.json` carries the same blocker, artifacts and gates.

## What the task asks and what is proven here

The board row is `feasibility` mode and asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence, then reproduce the
exact model/runtime as a caller-supplied-asset reference and add an opt-in SDK
adapter once its prerequisites pass, record a concrete blocker if feasibility
fails, and **pin the model and compare reset, reconvergence, double-talk and
reference timing**. The acceptance text says a readiness conclusion with an
exact external blocker is an accepted investigation handoff. This package
records that conclusion.

This package proves only the **negative** side of the gate:

- the exact source, checkpoint, model card, fixture, runtime and rights
  prerequisites are absent (bounded probes, no network, no directory walk);
- every structurally valid caller-supplied bundle is **deferred** because the
  external artifacts are absent, while invalid, missing, wrong-shape,
  nonfinite, out-of-range, synthetic-proxy and unresolved-rights requests are
  rejected before any artifact check;
- the declared paired-reference NKF geometry cannot be represented by the
  installed v0 mono single-input path, which has no separate far-end reference
  input; v0 does carry external model assets, but no such asset is exercised
  here;
- the historical local AEC pilot contains five NLMS/SpeexDSP controls but
  **no NKF row**, so it cannot be inherited as matched evidence;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Neural Kalman filtering is unsuitable. It records
the exact external condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/neural-kalman-filtering-nkf/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No NKF
  provider, descriptor, installed target or public API/ABI change exists. There
  is no C provider.
- No provider is registered, enabled by default or selected as a default.
- No real corpus, audio, weights or checkpoint is read. All harness stimuli are
  analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, echo-attenuation,
  reconvergence, double-talk, reference-timing, benchmark or release claim is
  made.
- Board linkage is projected from **stable row identity only** (`id`, `title`,
  `component`, `mode`, `repository`, `depends_on`). Mutable status, owner,
  review, handoff, priority, claim, history and every other mutable field never
  enter canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## Room acceptance profile application

The structured inventory assigns the **Room** acceptance profile
(`plan/swarm/VERIFICATION.md`, pinned below). The profile asks for frozen
render/reference or measured RIRs, channel/rate/hop geometry, excitation,
delay, movement, noise and reset schedule, echo-only, near-end-only, overlap
and no-reference cases, echo attenuation, near-end damage, nonfinite failures
and alignments including delayed/missing render, and an independent comparison
for a no-reference suppressor.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Frozen render/reference or measured RIRs | `room_profile` ROOM-01 marks blocked | No room set |
| Channel, rate and hop geometry | ROOM-02 marks blocked | No candidate geometry |
| Excitation, delay, movement, noise, reset schedule | ROOM-03 marks blocked | No fixture schedule |
| Echo-only, near-end-only, overlap, no-reference | ROOM-04 marks blocked | No candidate or fixture |
| Echo attenuation | ROOM-05 marks blocked | Unmeasured |
| Near-end damage | ROOM-06 marks blocked | Unmeasured |
| Nonfinite failures and alignments | ROOM-07 records local harness rejection only | Local rejection tests only |
| Reset, reconvergence, double-talk | ROOM-08 marks blocked | No instance exists |
| No-reference suppressor comparison | ROOM-09 records not applicable: this candidate requires a reference | No comparison claimed |
| Delayed/missing render | `profile_mapping` marks blocked | Unmeasured |
| Reference timing | `task_requirement` marks blocked | Unmeasured |

Every rejection, missing artifact and nonfinite case is retained with
`qualifies_candidate=false`. Passing the local harness check means only that
this blocker package is self-consistent.

## Task geometry

- `task_kind`: `acoustic_echo_cancellation_with_paired_reference`; the
  suppressed quantity is the loudspeaker echo present in the microphone
  capture.
- The candidate family is a **classical echo-path model plus learned
  adaptation/gain control**, which the pinned census calls Neural Kalman
  filtering. It requires a trained checkpoint, a paired far-end reference and
  microphone stream, real-time state and an exact delay model.
- No architecture, sample rate, frame, hop, STFT size, state dimension,
  parameter count, precision, delay alignment or reset/reconvergence policy is
  declared, so geometry is **unverified**.
- The installed public v0 path is 16 kHz mono `f32`, 160 samples per frame. It
  has one channel, no explicit far-end reference and no exercised model asset
  path, so the declared NKF geometry is not represented by installed v0.
- `candidate_output_measured=false`, `installed_v0=false`,
  `provider_registered=false`.

## Matched evidence

The pinned local AEC pilot ran NLMS at 128/192/256/512 taps and SpeexDSP MDF on
a deterministic synthetic echo path. The report records those five control rows
and proves that **no row is Neural Kalman filtering**. Its values keep their
original synthetic/pilot scope; they are not rerun, pooled, inherited or
promoted here. The AEC-Challenge synthetic and real training material cited by
the pinned notes remains research input behind its own terms, not a staged or
rights-cleared matched room fixture.

## Pins

Paths outside `docs/task-evidence/neural-kalman-filtering-nkf/` are relative to
the `audioml` workspace root; SDK boundary paths are relative to this SDK
worktree.

Pinned base: `9074704819a6af4168f8c9cf3bbe8da50484c29a`. Branch:
`swarm/SDK-NEURAL-KALMAN-FILTERING-NKF`.

### Source pins (SHA-256)

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
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
<!-- digest-table: end -->

### Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `e918f0fdb9e6ba5bd0e4dbdd89e14c693725ebf1917dd98b503b0027901e674a` | 1905 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `79f4b0617797b853ee21a31b614d38cc9645fa7fc04df9daba62b6d6fe97694c` | 14275 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `3e6780123804fb80625de69c03a48338d688d4b47a8bc8b5e22d62bc0d7f8213` | 79331 |
| `report.json` | `794b70f802ab51da7144c9a5b675aeb8d598015b0f73e7203cf735cccf34ce32` | 36845 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `51f9cefaa7994a1b654eeb454a97e4d487340ce55af651673f84df9c103bba76` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `a22ac6077927817b8e6ce4fe87be7ff13579603979eb32e3a8a3946f66726e08` | 4656 |
| `test_reference.py` | `2313d39b48d865b7c2941d3538cbf418fa1136bcca30171b4ab329c6824f494a` | 22462 |
| `verify.py` | `d74bc853813e66b3f561ad3d6471b2724312016331d3da4e0891751037fbb820` | 32344 |
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
  gate, synthetic harness controls, room profile mapping and canonical report
  builder.
- `run.py`: regenerates report, sidecar, manifest and README table three times
  and fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance and scope regression suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, README digest-table, merge-base scope and cold-start verifier.
- `LICENSES.md`: licensing and provenance notes.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/neural-kalman-filtering-nkf
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

1. `RG-01` exact NKF source repository, 40-hex revision and license.
2. `RG-02` trained checkpoint, byte count, model card, training provenance and
   architecture/parameter/config digest.
3. `RG-03` rights-cleared paired far-end/microphone room fixture, frozen RIR or
   render set, delay, movement, noise, reset schedule and held-out split.
4. `RG-04` source, checkpoint, training-data, fixture, output-use and
   device/participant rights.
5. `RG-05` model, runtime, checkpoint loader and installed adapter geometry
   pinned.
6. `RG-06` reset, reconvergence, double-talk, reference timing, echo attenuation
   and near-end damage measured on the exact model.
7. `RG-07` room adverse matrix (delayed/missing render, path change,
   near-end-only), default-off opt-in adapter intake and independent exact-head
   review.
8. `RG-08` benchmark validation, product decision and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`contract.json -> upstream_blocker.reopen_condition`.
