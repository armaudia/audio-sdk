<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SURVEY-ENG-03 — Jitter buffering and adaptive playout evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This is a bounded,
deterministic, task-local coverage map for the single catalogue category
**`ENG-03` — Jitter buffering and adaptive playout**. It is not a
qualification, not a general `ENG` taxonomy survey and not a language or
language-identification scope. `ENG-01`, `ENG-02`, `ENG-04`, `REC-02` and
`whisper-tiny-en-int8-via-sherpa-onnx` are outside this task. The map reads no
board, handoff or file outside `docs/task-evidence/survey-eng-03/` for writing
and modifies none of them.

## Scope and boundary

- Pinned task base: `c9296ae96a2b58efae559bd22e7760122c886df8`; branch
  `swarm/SDK-SURVEY-ENG-03`.
- Only `docs/task-evidence/survey-eng-03/` is written. No task is created,
  edited or dispatched; no board/handoff/reviewer state changes.
- No provider registration, descriptor/registry/default change, processor
  exposure, `CONTRACTS.md`, public header/ABI, shared `CMakeLists.txt`, CI
  workflow or installed-v0 behavior change. The installed 16 kHz mono f32,
  160-sample v0 geometry is preserved and no SDK callback is invoked.
- No real corpus, packet capture, codec/model/NetEq runtime, PCM, device
  timing, paced playback, rendered listening, benchmark or release claim is
  made. No reported or vendor result is reused as a local result.
- **API block size is not total latency.** Adaptive playout is not
  user-selected speed control; fixed-rate time-scale engines are recorded as
  adjacent controls and are never pooled with jitter-buffer evidence.

## Evidence inputs and pins

Workspace-relative inputs (`SOURCE_ROOT` defaults to the `audioml` directory
two levels above the SDK worktree; override with `SOURCE_ROOT`):

| Input | SHA-256 | Use |
| --- | --- | --- |
| `research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | Authoritative `ENG-03` record, method families and `S41` lead |
| `audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Readable companion row and live/comparison boundary |
| `research/task_backlog.json` | `0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc` | Legacy `F16` backlog entry and snapshot |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component evidence statuses and dispositions |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `b583d08dd6ac063bf1885fcf921ebea8c5927ed1a9a70fad78c4998d84e247ca` | Selected task identity/mode/component records; mutable status is observed only |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Evidence and rate acceptance profiles |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery/reuse boundary |
| `…/handoffs/SDK-FND-ELASTIC.md` | `8f7aec856f92d7090935c86ba89fa99e1f5b3ebb6e6a67c081eed9d2c9c94b5c` | Variable-count PCM/packet timing outcome |
| `…/handoffs/SDK-BUFFER-OCCUPANCY-CONTROLLER.md` | `0a0d92d52990f851b96cf38e4c010276136c28d620bc7d6db72c38e8506bb12a` | Synthetic occupancy outcome |
| `…/handoffs/SDK-RUBBER-BAND-R3-OFFLINE.md` | `df84500595acf96bb07808334c3f2bc6101b4f3f0c8a3179a06cfd15f9c60792` | Offline time-stretch outcome |
| `…/handoffs/SDK-RUBBER-BAND-R3-STREAMING.md` | `b70f9ed4dd2625894c6ba24ca8bd308c2c9cf0584b5d322c58ef8c52ad42c024` | Streaming time-stretch outcome |

SDK-worktree boundary pins include `CONTRACTS.md`, both public v0 headers,
`CMakeLists.txt`, both `.github/workflows` files and every cited task-local
component README. `SOURCES.sha256` enumerates source, boundary and local
artifact pins; `verify.py` rejects a missing, stale, duplicated, malformed or
unpinned file, non-canonical/nonfinite/duplicate-key JSON, quote drift, a
second `ENG` category and any change outside this directory.

## Catalogue record

`research/category_registry.json` (taxonomy revision 2, survey
`2026-10-27`) records `ENG-03` as group "Delivery and audio interface
support", scope `support`, discovery `catalogued`, candidate census
`not_started` and benchmark `not_started`. Input/output is
`Timestamped packets → regular PCM playout`; the boundary is
"API block size is not total latency; distinguish adaptive playout from
user-selected speed control." The companion row and the legacy `F16`
`catalogued` backlog entry agree. These are catalogue records, not results.

## Method-family map

Three classical families are catalogued. Each is matched to existing
components with its comparison inputs, controls, assets, local outcomes,
reported-only outcomes and limits recorded in [`report.json`](report.json).

### Adaptive buffers

Mapped components: `webrtc-neteq`, `buffer-occupancy-controller`,
`capsc-buffer-occupancy-pacing` and the `SDK-FND-ELASTIC` foundation
`elastic-pcm-packets`.

Comparison inputs are virtual-clock FIFO traces and exact variable-count PCM
maps; no RTP timestamp sequence, receive arrival log or NetEq trace exists.
Controls are a 200 ms target, 600 ms capacity, integer-ppm proportional
control, `[0.95, 1.05]` clamp, at most 50 ppm/tick (0.5 percentage points/s)
slew and a matched fixed 1× run. A queue that cannot cover a full nonfinal
block enters rebuffer with no source consumption or new rate command.

Local synthetic outcomes: mean absolute live queue error was **12.569 versus
240.800** source samples at `+1000 ppm` and **17.806 versus 133.483** at
`−1000 ppm`; a 400 ms delivery hold produced one **3360-sample (210 ms)**
rebuffer in both runs; `+60,000 ppm` overflowed at virtual sample **241280
versus 109280**. The elastic fixture maps 80/160/240-sample chunks exactly,
changes only later chunks after a `1 → 2` ratio update, produces a finite
320-sample tail at ratio `0.5` and separates single-erasure parity from PCM.
Neither executes reordering, a loss-driven delay target or device pacing.

### Acceleration/deceleration

Mapped components: `buffer-occupancy-controller`,
`rubber-band-r3-offline`, `rubber-band-r3-streaming` and `ffmpeg-atempo`.

Comparison inputs are source-timestamped synthetic schedules at 1×, 1.25×,
1.5×, 0.8×, 0.9× and rational atempo changes, plus controller commands inside
±5%. Controls are identity 1×, fixed 1× against the controller, and explicit
unsmoothed-rate-step and varispeed adverse cases. These are automatic playout
corrections or user-selected rate changes, not a jitter buffer.

Local synthetic outcomes: offline OLA/WSOLA maps identity
`19200 → 19200`, `1.25× → 15360`, `1.5× → 12800`, `0.8× → 24000` and
`0.9× → 21333` with zero duration error, while a **1600-sample** uncompensated
rebuffer deficit and a transient proxy of `102` versus identity `40` remain
recorded gates. Streaming OLA/WSOLA passed 32/32 tests but its duration
relative error **+0.0367552310** fails the proposed 1 ms/s gate; an
**800-sample** interruption drained 32 buffered samples and refilled 128, and
first output appeared at input frame 3 (30 ms). The atempo reference reached
exact target length with zero duration error on every rational schedule. None
is device pacing or FFmpeg/Rubber Band parity.

### PLC integration

Mapped components: `linear-interpolation-plc`, `pitch-period-repeat-plc`,
`zero-fill-plc`, `opus-1-4-standard-decoder-plc`, `autoregressive-plc` and the
elastic packet fixture.

Comparison inputs are frozen synthetic 16 kHz mono f32 160-sample frames,
250-frame / 40,000-sample cohorts, a 2.5 s stream and fixed isolated,
two-frame and four-frame erasure bursts across voiced, unvoiced and silence
strata. Controls are identity clean delivery, zero fill, hold and linear
interpolation. Concealed slots carry result flag `4` with `valid_count = 0`
and cannot satisfy sample conservation; the 800-sample host buffer is an
adapter scheduling choice, not intrinsic candidate delay.

Local synthetic outcomes: linear interpolation scored **11.820617 dB**
SI-SDR and **0.949594** STOI versus zero fill at **10.983909 dB** and
**0.951020**; pitch-period repeat scored **22.139532 dB** and **0.851298**
versus zero fill at **13.589343 dB** / **0.807333**; zero fill scored
**11.790410 dB** / **0.876922** and regressed against hold by **−0.117563 dB**
SI-SDR and **0.000352** lost-region RMSE; the decoder-PLC-style surrogate
scored **11.089522 dB** / **0.946857**, losing SI-SDR and lost-region RMSE to
all three controls while gaining STOI. No Opus library, codec stream, packet
trace or codec-native PLC is executed, and none of these fixtures is
integrated with a reordering jitter buffer.

### Machine-learning audit

The catalogue records **"No ML requirement"**. No learned jitter-buffer, delay
estimator or playout policy is catalogued. Neural PLC and codec variants
belong to `ENG-04` or conditional leads and are not an `ENG-03` family.
Missing evidence is therefore explicit: there is no catalogued ML family to
evaluate, and any future learned playout policy would need its own category
record, rights scope and matched cohort. No ML asset, weight or runtime is
present.

### Adjacent but excluded

`sonic`, `soundtouch`, `signalsmith-stretch`, `psola-praat`, `granular-tsm`,
`ola-sola` and `phase-vocoder-baseline` are catalogued user-selected
time-scale engines. They are audited for coverage but explicitly recorded as
`counted_as_jitter_buffer=false` and
`counted_as_adaptive_playout=false`; pooling them with automatic jitter or
drift correction is rejected by the validator.

## Local versus reported outcomes

Local evidence is limited to deterministic synthetic fixtures, virtual clocks
and state controls. Reported evidence is limited to the `S41` NetEq
documentation lead, registry/backlog statuses, inventory `evidence_status`
and board status observations. The two classes are never pooled. A pinned
README quote is provenance, not a reproduced run; a board `done` record is
not a quality, timing or release outcome.

## Actionable gaps and existing follow-ups

| Gap | Statement | Linked existing board task |
| --- | --- | --- |
| `ENG-03-G1` | No local NetEq trace replay, timestamp-domain reordering run or codec-integrated playout execution exists for `S41`. | `SDK-WEBRTC-NETEQ` (`feasibility`, queued) |
| `ENG-03-G2` | No matched occupancy-controller and fixed-1× run on a pinned variable-count actuator with instrumented playout exists. | `SDK-CAPSC-BUFFER-OCCUPANCY-PACING` (`feasibility`, queued) |
| `ENG-03-G3` | PLC fixtures are standalone host-adapter controls with no reordering buffer, loss-driven delay target or codec-native concealment decision. | None: board PLC tasks are done implementations; `SDK-PIPE-RECEIVE` is a blocked pipeline. `no_task_reason` recorded. |

No task is invented and no board row is edited. The `invented` flag is
`false` for every gap and is validated before state admission.

## Release boundary and prohibited claims

All eight gates in `report.json.gates` are `blocked`: rights-cleared packet
traces/cohort, pinned permitted runtime/assets, independent listening,
target-device pacing, provider intake, public default selection, exact
external reference parity and independent review/board transition.

This package is not a NetEq implementation, jitter buffer, adaptive playout
controller, codec, PLC integration, playback actuator, benchmark bundle,
native build/CTest result, installed-package result, device measurement,
listening result or release decision. No quality, latency, availability,
throughput, pitch or speech-preservation claim is made. Reopening requires
independently pinned runnable assets, exact scope and rights, agreed
coverage/margins/budgets, matched controls, target-runtime/device evidence and
separate versioned integration/release work.

## Determinism and adverse controls

`reference.py` is stdlib-only. It strict-parses every pinned input, requires
the registry, companion row, inventory row and legacy backlog to agree, rebuilds
the map from exact records, verifies every quoted phrase still appears in its
pinned source, and emits canonical sorted-key compact JSON. `MapState` rejects
an out-of-scope category, wrong id, unknown or non-feasibility follow-up,
invented gap, missing family or ML audit, invalid source id, pooled adjacent
speed control, forbidden timing/listening/codec/release claim, component
qualification, duplicate JSON keys and `NaN`/`Infinity`. Every rejection occurs
before state admission; the report records before/after digests and
`state_unchanged=true`.

`repeatability` hashes the canonical core report in three fresh interpreter
processes with `PYTHONDONTWRITEBYTECODE=1`. `run.py all` is idempotent and
regenerates `report.json`, `report.json.sha256` and `SOURCES.sha256`
byte-for-byte.

## Reproduce

From this directory with pinned Python 3.12.16 and stdlib only:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
```

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output /tmp/survey-eng-03-ci
python3 -m reuse lint
git diff --check
```

Expected: all tests pass, `run.py all` reproduces the committed bytes,
`verify.py` prints `PASS`, `scripts/ci.py` passes on the unchanged SDK, REUSE
reports no missing/bad license and `git diff --check` is clean. Canonical
`report.json` SHA-256: `d7ff9ea111bf3ca8da8915b2bbda58a65143ec51f00620ed63b423424cb35ddf`.

## Canonical artifacts

- [`report.json`](report.json): canonical UTF-8 JSON, sorted keys, compact
  separators, one trailing newline.
- [`report.json.sha256`](report.json.sha256): SHA-256 of `report.json`.
- [`SOURCES.sha256`](SOURCES.sha256): SHA-256 of every source, boundary and
  task-local artifact.
- [`contract.json`](contract.json): strict machine-readable scope and pins.
- [`run.py`](run.py): byte-identical report/sidecar/manifest regeneration.
- [`verify.py`](verify.py): read-only strict verifier.
- [`test_reference.py`](test_reference.py): deterministic acceptance tests.
