<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ESSENTIA: Essentia feasibility blocker

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local feasibility evidence for
the Essentia row (`plan/swarm/TASKS.json`, mode `feasibility`, repository
`audio-sdk`, component `essentia`). It is **not** Essentia: no upstream source,
header, configuration, Python module, binary, license text, model, weight,
corpus, listening result, device measurement, benchmark or release claim is
included. **No result here qualifies the candidate.**

## Exact blocker: source, AGPL-3.0 rights, runtime, models and fixture absent

A bounded, read-only probe of named workspace and home paths, the Python module
registry and the CLI PATH found **no Essentia checkout**, **no local license
text**, **no installed Python module or `essentia` CLI**, **no pinned build or
binding record**, **no extractor configuration or model** and **no
rights-cleared matched tempo/beat corpus**. Nothing was cloned, downloaded,
installed, extracted, ported, reverse-engineered or substituted.

The pinned candidate note reports Essentia as a BPM/beat/rhythm factor provider
under **AGPL-3.0**, described as *strong copyleft, including network use*, and
**not usable in a closed-source product**. This SDK's outbound map is
Apache-2.0 for `api/**`, `bindings/**`, `examples/**`, `conformance/**`,
schemas, tools and documentation, and MPL-2.0 for `core/**` (`LICENSE.md`).
No byte-identical license text and no written decision addressing AGPL-3.0
network-use and distribution obligations in this SDK exists. That reported
restriction blocks adapter work independently of whether a source checkout is
present.

| Item | Status |
| --- | --- |
| Source checkout | **Absent.** No local Essentia tree; revision, tree digest, file count and license file are `null` |
| License text and decision | **Absent/blocked.** Only a source-reported AGPL-3.0 name; no license text, SHA-256, network-use decision or outbound compatibility approval |
| Runtime and bindings | **Absent/unpinned.** No Python module, CLI, C++ runtime, dependency lock, reproducible build or install/import parity record |
| Configuration and models | **Absent.** No extractor configuration, model name, weight file or separate model-license review |
| Matched corpus | **Absent.** No permitted held-out speech/music audio with beat, tempo and onset annotations |
| Candidate execution | **None.** No extraction, beat tracking, tempo, onset or factor run occurred |

The machine-readable record is `report.json` -> `upstream_blocker`
(`status="blocked_source_rights_runtime_models_and_fixtures_absent"`, with every
digest and byte count `null`), `required_artifacts` (A1-A6), `source_probe`,
`license_probe`, `rights_probe`, `runtime_probe`, `fixture_probe`, `geometry`,
`external_boundary` and `release_gates`. `contract.json` carries the same
blocker, the same missing artifacts and all eight blocked gates.

## Vendor boundary

| Field | Recorded value |
| --- | --- |
| Vendor | Essentia project |
| Component | Essentia |
| Version | **Not recorded in the pinned note; not inferred** |
| Distribution model | C++ analysis library with Python bindings |
| Reported role | BPM, beat and rhythm factor provider |
| Host target here | macOS / Python 3 workspace |
| Host target eligible | **No** |
| Reported license | AGPL-3.0 |
| Reported restriction | Strong copyleft including network use; not usable in a closed-source product (source-reported, not locally verified) |
| Local runtime | **Absent** |
| Adapter implemented | **No** |
| Default registration | **No** |
| Automatic discovery or fallback | **No / none** |

Only the factor role, the license finding and a reported *some* online
capability are recorded. The pinned note does **not** record an upstream URL,
version, sample rate, frame size, channel count, model, threshold or vendor
measurement, and none was invented. Because no rate or frame geometry is
recorded, `geometry.declared_*` fields are `null` and
`v0_can_represent_declared_input` is `false`: installed v0 produces 160-sample
audio frames only and has no analysis, event or factor output type.

## What the task asks and what is proven here

The board row is `feasibility` mode. It asks to verify runnable source, exact
assets, permitted scope, task geometry and matched evidence, then implement or
wrap a minimal reference at the relevant public adapter boundary and ship it
optional, or record a concrete blocker. It also requires the Rate acceptance
profile, exact scope, failure/control results and remaining release gates.

This package proves only the **negative** side of that gate:

- the exact source, rights, runtime, model and fixture prerequisites are absent
  (bounded probes, no network);
- the reported AGPL-3.0 terms have no recorded outbound-compatibility decision
  for this Apache-2.0/MPL-2.0 distribution;
- every structurally valid request reaches a fail-closed
  `ARTIFACTS_ABSENT` gate and is never processed;
- invalid, missing, wrong-shape, nonfinite, out-of-range and unknown-key
  requests are rejected before any artifact check;
- the declared factor role cannot be represented by installed v0, which has no
  analysis or factor output surface;
- source-reported characteristics and local synthetic harness controls are kept
  separate, and neither vendor output nor a local candidate result exists;
- all eight release gates remain blocked and no missing result qualifies.

It does **not** prove that Essentia is unsuitable. It records the exact external
condition required to reopen the investigation.

## Exact scope

- Work is confined to `docs/task-evidence/essentia/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, provider registration, board/handoff files, CI, rulesets and
  `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  Essentia provider, descriptor, installed target or public API/ABI change
  exists. There is no C provider and no adapter source.
- No provider is registered, exposed as a processor, enabled by default or
  selected as a default. There is no automatic discovery and no fallback.
- No real corpus, model, weight, runtime or vendor file is read. All harness
  stimuli are analytic or seeded synthetic; they are not candidate output.
- No listening, device timing, wall-clock playback, pitch, transient
  audibility, benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim, history and every other mutable field never enter
  canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## Rate profile application

The structured inventory assigns the **Rate** acceptance profile
(`plan/swarm/VERIFICATION.md`, pinned below). The profile asks for
source/output mapping, duration, pitch, transient audibility and playback
buffering across 1x, rate changes, unfamiliar speech, music, silence, rebuffer,
drift and the final partial window, with pause/filler decisions tied to source
timestamps and speech preservation measured.

| Profile item | Evidence in `report.json` | Claim limit |
| --- | --- | --- |
| Source/output mapping | `harness_probe.rate_profile.source_output_mapping`: synthetic events carry source intervals and a frame-monotonic availability margin | Harness coordinates only; no audio, device clock or real factor output |
| Duration | `harness_probe.rate_profile.duration`: exact synthetic spans at 0.8x, 1x and 1.2x (`max_error_samples=0`) | Event-time scaling only |
| Pitch | `pitch.status=not_measurable_factor_analysis_only`, `qualifies=false` | Unmeasured; RG-06 remains blocked |
| Transient audibility | `transient_proxy`: frame-quantized onset proxy only | Not listening or audibility |
| Playback buffering | `playback_buffering`: 160-sample aggregation, 137-sample final window, zero padding verified | No SDK worker, queue, renderer or fill/flush measured |
| 1x / rate changes | `identity_1x`, `rate_changes`: 100, 80 and 120 BPM from synthetic periods | Synthetic periodic surrogates |
| Unfamiliar speech | `speech_unfamiliar` has no stable factor and `qualifies=false` | No speech-preservation measurement; RG-06 remains blocked |
| Music / silence | Stable 100 BPM music surrogate; silence has no onsets | Analytic surrogates |
| Rebuffer | One cross-gap IOI excluded; no factor inferred across the gap | No real rebuffer event |
| Drift | Monotonic source-anchored IOI decrease recorded | No global tempo claim |
| Final partial | 137 valid samples, explicit event digest and zero padding | Exact final-window accounting only |
| Candidate output | `profile_mapping.candidate_output=blocked_..._absent` | None |

Every rejection, adverse, missing or nonfinite outcome is retained with
`qualifies=false`; a rejected frame never advances harness state. Passing the
local harness check means only that this blocker package is self-consistent.

## Pins

Paths outside `docs/task-evidence/essentia/` are relative to the `audioml`
workspace root; SDK boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Essentia BPM/beat/rhythm role and AGPL-3.0 finding |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `essentia` row, Rate profile, sdk-reference disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Source/assets/scope/matched-evidence requirement |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 aggregate coverage |

`SOURCES.sha256` additionally pins every task-local artifact and excludes
itself because a file cannot pin its own bytes. `contract.json` is excluded
from `SOURCES.sha256` because it pins the manifest; it is pinned by the
verifier and by review. `verify.py` fails closed on a missing, stale,
malformed, duplicated or extra pin and on any worktree change outside this
directory.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission gate, synthetic harness controls and canonical report
  builder.
- `run.py`: regenerates report, sidecar, manifest and contract three times and
  fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, scope and three-cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/essentia
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and the stable board row, and checks cold-start
byte identity there.

## Eight blocked release gates

1. `RG-01` exact upstream source revision, tree digest and license pin.
2. `RG-02` AGPL-3.0 network-use and outbound-compatibility decision.
3. `RG-03` hash-pinned runtime and Python binding build.
4. `RG-04` pinned extractor configuration, models and separate model rights.
5. `RG-05` beat, tempo and onset reproduction with reset and finite drain.
6. `RG-06` full Rate matrix: mapping, duration, pitch, transient audibility,
   buffering, rate changes, unfamiliar speech, music, silence, rebuffer, drift
   and the final partial window.
7. `RG-07` paced workload, device timing, memory, CPU and callback suitability.
8. `RG-08` adapter intake, public surface, optional registration, benchmark
   validation, authorized listening, independent exact-head review and release
   approval.

Missing, rejected, adverse or source-reported evidence never qualifies the
candidate. The exact reopen conditions are recorded on each gate and in
`upstream_blocker.reopen`.
