<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SURVEY-ENG-03 — ENG category evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This is a bounded,
deterministic, task-local map of pinned category records, not a qualification.
Every release gate is blocked. No candidate is promoted by a missing, unrun or
invalid case.

`ENG` is the **engineering Delivery and audio interface support** category in
`plan/INVENTORY.json` (`ENG-01`…`ENG-04`). It is **not** an English-language or
language-identification category: `REC-02` and `whisper-tiny-en-int8-via-sherpa-onnx`
are explicitly outside this scope. This evidence map explicitly does not
read, create or modify the board, handoffs or any file outside
`docs/task-evidence/survey-eng-03/`.

## Boundary

- Pinned base: `c9296ae96a2b58efae559bd22e7760122c886df8`; branch
  `swarm/SDK-SURVEY-ENG-03`. The pre-existing task subtree was absent at merge.
- No provider registration, descriptor/registry/default change, processor
  exposure, `CONTRACTS.md`, public header/ABI, `CMakeLists.txt`, CI workflow or
  installed-v0 behavior change. The installed 16 kHz mono f32, 160-sample v0
  geometry is preserved and no SDK callback is invoked.
- No real corpus, weights, codec/model runtime, rendered playback, listening,
  device timing, benchmark or release claim. No vendor result is reused as a
  local result.
- All source and board records are provenance and coverage inputs; inventory
  `evidence_status` and board `status` values are not reproduced outcomes.

## Pinned inputs

Workspace-relative source pins (default workspace root is two parents above the
SDK worktree root; override with `SOURCE_ROOT`):

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | ENG taxonomy, method families, source leads, component evidence statuses |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery/reuse boundary; local vs reported separation |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Evidence profile and installed/benchmark separation |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `16b37d5bc3a2018a1f1754ca2436727791d815e55ffc64bf6a3f420729bb8bd3` | Selected board task identity/mode records (`SOURCE_PIN_SELECTORS`); feasibility follow-up linkage. Mutable `status` is a frozen observation, not a pin. |

SDK-worktree boundary pins include `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`,
`api/include/audio_sdk/session_v0.h`, `CMakeLists.txt`, both `.github/workflows`
files, and the pinned component README files named in `contract.json`.
`SOURCES.sha256` enumerates every source, boundary and task-local artifact pin.
`verify.py` fails closed on a missing, stale, duplicated, malformed or unpinned
file, on non-canonical/nonfinite/duplicate-key JSON, and on any change outside
this directory.

## Category map

| Category | Method families audited | Source leads | Matched component evidence | Actionable gaps / linked feasibility follow-ups |
| --- | --- | --- | --- | --- |
| `ENG-01` Framing, format conversion and resampling | classic framing/channel mapping and bandlimited resampling; ML `No ML requirement` | `S42` | NumPy/SciPy/SoundFile offline fixture; typed frame/resample/drift diagnostics | `ENG-01-G1` → `SDK-SPEEX-RESAMPLER` (queued); `ENG-01-G2` → no board feasibility task |
| `ENG-02` Clock drift, alignment and reference synchronization | classic delay estimation/rate adjustment/drift compensation; ML optional research | `S27`, `S41` | typed frame/drift diagnostics; CoreAudio duplex host record | `ENG-02-G1` → `SDK-3D-MICROPHONE-SPATIAL-TIME-ALIGNMENT` (queued); `ENG-02-G2` → no board feasibility task |
| `ENG-03` Jitter buffering and adaptive playout | classic adaptive buffers/acceleration-deceleration/PLC integration; ML `No ML requirement` | `S41` | elastic PCM/packets fixture; synthetic buffer-occupancy controller | `ENG-03-G1` → `SDK-WEBRTC-NETEQ` (queued); `ENG-03-G2` → `SDK-CAPSC-BUFFER-OCCUPANCY-PACING` (queued) |
| `ENG-04` Codec/packetization, FEC, DTX and comfort noise | classic negotiation/packet duration/FEC/DTX/comfort noise; ML neural codec variants conditional | `S43`, `S44`, `S30` | synthetic decoder-PLC-style control; elastic packet contract | `ENG-04-G1` → `SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE` (queued); `ENG-04-G2` → `SDK-OPUS-DRED` (queued); `ENG-04-G3` → no board feasibility task (`SDK-PIPE-RECEIVE` is a blocked pipeline) |

Every linked id is an existing board task with `mode=feasibility`. Where no such
task exists, `follow_up_task_id` is `null` and a `no_task_reason` is recorded;
no task is invented and the board is not edited. The `invented` flag is `false`
for every gap and is validated before state admission.

Evidence classes remain separate: catalogued source leads, pinned component
README evidence, inventory/board statuses, and deterministic synthetic controls
are never pooled into a quality, timing or release result. For `ENG-03` in
particular, API block size is not total latency, and adaptive playout is not
user-selected speed control.

## Determinism and adverse controls

`reference.py` is stdlib-only. It strict-parses the pinned inventory and board,
builds the map from exact records, and emits canonical sorted-key compact JSON.
`MapState` rejects missing categories, unknown or non-feasibility follow-up ids,
invented-task flags, wrong method-family keys, invalid source ids, missing
required keys, duplicate JSON keys, and `NaN`/`Infinity` constants. Every
rejection occurs before state admission; the report records the before/after
state digest and `state_unchanged=true`.

`repeatability` hashes the canonical core report in three fresh interpreter
processes with `PYTHONDONTWRITEBYTECODE=1`. `run.py all` is idempotent and
regenerates `report.json`, `report.json.sha256` and `SOURCES.sha256`
byte-for-byte.

## Reproduce

From this directory, with Python 3.11+ and stdlib only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
reuse lint
```

Expected: all tests pass, `run.py all` reproduces the committed bytes, and
`verify.py` prints `PASS`. Canonical `report.json` SHA-256:
`9de9f8f9921f0a0dcddcea811d2f68022d74584c407d7efbe1ff42ade7f13b8d`.

## Frozen gates and non-claims

All eight gates in `report.json.gates` are `blocked`: rights-cleared cohort,
pinned runtime/assets, independent listening, target-device pacing,
provider intake, explicit public default selection, exact external reference
parity, and independent review/board transition. This package is not a
provider, engine, codec, decoder, resampler, buffer implementation, benchmark
bundle, native build/CTest result, installed-package result, device measurement
or release decision.

Reopening requires independently pinned runnable assets, exact scope and
rights, agreed coverage/margins/budgets, matched controls, target-runtime and
device evidence, and separate versioned integration/release work.
