# SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS · typed frame / resample / drift diagnostics

**Status: proposal-only, synthetic, model-free. Qualification: `incomplete`.**
This is a deterministic Python developer tool model. No public v0 header, ABI,
`CONTRACTS.md`, `CMakeLists.txt`, descriptor, registry default, installed
behavior, board/handoff file or any file outside this task-local directory is
changed. Every real-device, measured-workload and quality claim is frozen as
blocked below. No missing or unrun control is promoted to a pass.

## Scope

The adapter adds **explicit conversions outside the fixed v0 provider ABI** and
documents their boundaries. The fixed v0 boundary remains 16 kHz mono f32 in
160-sample (10 ms) frames; it is never converted or negotiated inside a
provider. Rate/channel/PCM conversions, source clock maps, drift bounds and
finite-tail accounting are developer tooling only.

| File | Role |
| --- | --- |
| `contract.json` | Frozen versioned proposal `audio-sdk/typed-frame-resample-drift/0.1` |
| `fixture.py` | Model-free adapter, clock map, delay probe, bounded drain and adverse controls |
| `generator.py` | Typical CLI/API entry point; writes the report and digests |
| `test_fixture.py` | 24 offline `unittest` acceptance tests |
| `report.json` | Canonical machine-readable report with counts, controls and blockers |
| `report.json.sha256` | SHA-256 sidecar for `report.json` |

## Source pins, version and provenance

Pinned task base: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`.
Branch: `swarm/SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS`.
Tool version: `0.1.0`. Install location (recording run):
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS/docs/task-evidence/typed-frame-resample-and-drift-diagnostics`.
Provenance: `https://github.com/armaudia/audio-sdk.git`, task-local fixture
directory only. Runner: Python 3.11.5, macOS-27.2.1-arm64-arm-64bit.

| Pinned source (workspace-relative) | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format, epoch/sample coordinates, content mapping, bounded drain, padding/non-content semantics |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Tool acceptance profile: version/install/provenance, clean checkout, typical use, caller-owned and malformed inputs, separate evidence layers |
| `audio-benchmark-platform/audio-sdk/README.md` | `9047036096a967bed5cd59e7d3b939258d327578b2079445da1b683b52a8fdb9` | Explicit: no implicit resampling, no capture or neural model; no production latency/quality claim from a synthetic conformance run |

Each pin is recomputed from the pinned workspace path during report generation
and recorded in `report.json.source_pin_verification`; all three verified `true`
in the recording run.

## Proposed contract

`contract.json` declares `audio-sdk/typed-frame-resample-drift/0.1`:

- Allowed explicit source conversions: 48000/32000/16000 Hz → 16000 Hz by
  integer decimation (3:1/2:1/1:1), 2/1 channels → mono by arithmetic mean,
  `s16`/`f32` → f32 by `value/32768` scaling. Every required conversion must be
  explicitly selected; an absent selection is rejected, never inferred.
- One declared monotonic clock domain. Source timestamps are exact integer
  rational maps from source sample index to nanoseconds (16 kHz sample =
  62500 ns); wall UTC is provenance only. Timestamps must be unique and inside
  the declared domain. Absolute drift is bounded at 10000 ppm.
- Integer buffering/content delay `D=173` samples (deliberately not a multiple
  of 160). It is measured by a synthetic impulse in source coordinates, not by
  wall time, source timestamp subtraction or acoustic-phase fitting.
- Drain is bounded (`max_drain_calls=4`). Accepted content is released up to the
  source end; post-input decay and all padding are **non-content**. Host-flagged
  concealment is never produced content and never satisfies conservation.

## Worked example and counts

Three full 48 kHz stereo `s16` frames (480 source samples each) plus a final
partial frame (45 valid source samples) convert to four v0 frames with 160,
160, 160 and 15 valid samples. With `D=173`, valid output source intervals are
`[0,147)`, `[147,307)`, `[307,467)`, `[467,495)`: a gapless, non-overlapping
union equal to the 495 accepted source samples. One drain frame releases
`[467,495)` and then reports end-of-stream.

| Count | Value |
| --- | --- |
| Source frames / valid source samples | 4 / 1485 |
| v0 input frames / produced samples | 4 / 640 + 1 drain frame = 800 produced |
| Accepted / delivered valid samples | 495 / 495 |
| Drain calls / rejected frames | 1 / 0 |
| Startup non-content / tail non-content / budget | 173 / 132 / 160 samples |
| Concealment frames | 0 |
| Adverse controls total / passed / missing | 13 / 13 / 0 |
| Fixture tests | 24 passed |

800 produced = 495 valid + 173 startup non-content + 132 tail non-content.

## Key digests

| Artifact | SHA-256 |
| --- | --- |
| `contract.json` (file and reported contract identity) | `b43576a081848b8339b8a35b124fc887652c924ccac40aa5be47c7a1a8c090dc` |
| `report.json` (file and sidecar) | `81cfcb73343437b42991ec31565144b038eed2a44a95e1280ae8b03ba2128d64` |
| Source PCM, valid interleaved s16 little-endian | `3cb688787637a8c204298f48f19eb4f9447f14ffb5cc24c8972a85371ef3d9fa` |
| Produced v0 output, f32 little-endian | `273680b78b95f9b7b8609c236109f345c8294595fe284638367a9e0d91e684d3` |
| `fixture.py` | `47af6e00ee2c310500fac7e133d9c00c54315b23a4c903cebeb8438f826c55cb` |
| `generator.py` | `4e56567548523ba38c4168fe07406742c682338b32beda99d2e4b8d5ec674c21` |
| `test_fixture.py` | `cd6756b1f418917cd3593a739f17bb6e22a81c6f735bd19a0131f3e9c26f4877` |

## Exact reproduction commands

From the workspace root:

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-TYPED-FRAME-RESAMPLE-AND-DRIFT-DIAGNOSTICS
```

Expected: exit 0; task returned as `in_progress` for `agent-typed-frame-resample`.

From the worktree root:

```sh
cd docs/task-evidence/typed-frame-resample-and-drift-diagnostics
PYTHONDONTWRITEBYTECODE=1 python3 generator.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -m json.tool report.json >/dev/null
shasum -a 256 contract.json report.json
```

Expected: `generator.py` prints the two digests above; 24 tests pass; JSON
parses; file digests match the table. Regeneration is byte-identical. A clean
checkout / extracted-package control copies only `fixture.py` and `generator.py`
to a temporary directory, regenerates with an explicit `--install-location`,
and requires byte-identical `contract.json`, `report.json` and sidecar. It runs
inside `test_fixture.py`, so no network, compiler, installed SDK or external
asset is needed.

## Tool acceptance profile evidence

| Requirement | Evidence in this fixture |
| --- | --- |
| Version, install location, provenance | `report.json.tool_profile`: `0.1.0`, absolute install path, repository/branch/base commit, runner version/platform, three recomputed source pins |
| Clean checkout or extracted package | `test_clean_checkout_extracted_package_regeneration`; isolated regeneration compared byte-for-byte |
| One typical CLI/API use | `python3 generator.py` writes `contract.json`, `report.json`, `report.json.sha256`; `fixture.TypedFrameAdapter.convert()` is the API analogue |
| Caller-owned inputs | `test_caller_owned_inputs_are_copied`; converted values are copied, source containers are never retained |
| Malformed inputs | 8 explicit rejection controls (rate, channel, shape, nonfinite, clock domain/timestamp, config, epoch, duplicate timestamp, drift) |
| Missing optional selections | `missing_optional_selection` control returns `rejected_missing_selection`; identity conversions are also explicitly selected |
| Compile/build evidence | `not_applicable_model_free`: no compiler/CMake/CTest/package run is claimed |
| Synthetic runtime evidence | `complete`: deterministic generator, 24 tests, 13 explicit controls, canonical report |
| Measured workload support | `blocked_not_run`: no pacing, CPU/memory, deadline, availability or target-device data |

## Adverse controls (all observed, none missing)

| Control | Observed result |
| --- | --- |
| Wrong sample rate (44100 Hz) | `rejected_sample_rate` |
| Wrong channel count (3) | `rejected_channels` |
| Wrong interleaved frame shape | `rejected_bad_frame_shape` |
| Nonfinite (NaN) input | `rejected_nonfinite_input` |
| Wrong clock domain | `rejected_clock_domain` |
| Timestamp inconsistent with source clock map | `rejected_clock_domain` |
| Missing explicit rate/channel/format selection | `rejected_missing_selection` |
| Malformed config (unknown key) | `rejected_bad_config` |
| Stale epoch | `rejected_stale_epoch` |
| Duplicate source timestamp | `rejected_duplicate_timestamp` |
| Drift beyond declared 10000 ppm bound | `rejected_drift_bound` |
| Tail non-content above a reduced 64-sample budget | `rejected_tail_overrun` |
| Finite-tail/non-content accounting | `ok`: 495 + 173 + 132 = 800, concealment 0 |

## Frozen blockers / deferrals for real qualification

1. No native C/C++ compile, CTest or installed-package build was run; this is a stdlib Python model.
2. No installed SDK library, public header consumer, provider registration or ABI/API change was exercised.
3. No real weights, downloads, corpora or licensed runtime; no model-quality or speech-quality result.
4. No target-device, paced-workload, CPU/memory, deadline or physical-availability measurement was run.
5. The measured delay is a deterministic source-coordinate impulse probe, not acoustic, phase or group delay.
6. No listening test and no frequency-dependent transfer or artifact claim is supported.
7. Independent reviewer approval and board transition are outside this task-local fixture.

## Explicit non-claims

Not a production SDK provider, engine, plugin or installed behavior. Not a native
build, CTest, wheel or package-identity result. Not a recording, real-audio
corpus, model or listening evaluation. Not a device, latency, throughput,
deadline or quality qualification. No candidate is qualified by a missing,
skipped or unrun control.

## Boundary and reopening

This closes only the versioned tool-model question for explicit conversion,
source clock mapping, integer delay measurement and finite-tail accounting.
Reopen for implementation when a real developer adapter names its installed
location and runtime, declares exact conversion and clock policy, provides a
native build/CTest and installed-consumer run, and supplies paced workload plus
target-device timing/resource evidence under the intended profile.
