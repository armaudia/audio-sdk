<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WEBRTC-NETEQ — WebRTC NetEq receive-side jitter/playout blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `WebRTC NetEq` (`component_id=webrtc-neteq`). The structured
inventory assigns the **Tool** acceptance profile
(`verification_profile: tool`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation or
intake step; `evidence_status=incomplete`, `qualification_status=not_qualified`.
Missing evidence never qualifies a candidate.

This package does not contain, import, build, link, download or execute WebRTC,
NetEq, libwebrtc, Opus, a codec, a jitter buffer, a playout engine or any other
runtime. It reads no audio, replays no packet trace, measures no clock and makes
no quality, timing, availability or release claim. It records the exact missing
artifacts, probes a fixed list of task-local paths to evidence their absence,
and defines a fail-closed admission boundary for the manifest and trace that a
future qualified run would need. Only `docs/task-evidence/webrtc-neteq/` is
written; no provider, registry, descriptor, public header/ABI, shared CMake,
CI workflow or installed-v0 behavior changes.

## Exact external blocker

The catalogue lead is `S41` — the WebRTC NetEq documentation at
`https://webrtc.googlesource.com/src/+/refs/heads/main/modules/audio_coding/neteq/g3doc/index.md`
(`research/category_registry.json`, category `ENG-03`). It is a documentation
lead only: the registry pins no revision, source archive, runtime, trace or
result. The merged sibling map `docs/task-evidence/survey-eng-03/` records the
same gap as `ENG-03-G1` and links it to this task.

Six exact blockers, all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | Permitted WebRTC NetEq source snapshot with an exact 40-hex revision and immutable archive SHA-256. No such snapshot exists at any fixed probe path. |
| `BLK-02` | The upstream license text, copyright notices and complete third-party notice bundle for that revision, with an explicit review decision. |
| `BLK-03` | A reproducible pinned build and artifact digest (toolchain, build configuration, install location, provenance). No libwebrtc/NetEq library or install location exists here. |
| `BLK-04` | A rights-cleared frozen receive trace cohort with per-packet sequence, RTP timestamp, arrival microseconds, payload bytes and payload digests. None is supplied or fabricated. |
| `BLK-05` | The matching codec payload format and pinned decoder/PLC runtime with exact revision, license and PLC settings. |
| `BLK-06` | A target playout device/clock harness plus agreed coverage, margins, deadlines and resource limits. |

WebRTC is normally distributed under the Chromium BSD-3-Clause license, but the
license file, notices, source revision and redistribution/product-use scope for
any specific artifact are **unverified here**. Nothing was copied, vendored,
built, downloaded or redistributed. `DEFER` is the only defensible decision:
without the source and a permitted runtime, NetEq cannot be reproduced,
compared or measured, and inventing a substitute would misstate the boundary.

**Reopen condition.** A caller supplies the permitted NetEq source revision and
immutable archive, license/notices bundle, reproducible build and runtime,
rights-cleared receive traces with declared timestamp domain, the matching
codec runtime, and a target playout harness with agreed budgets; the pinned
runtime reproduces approved reference outputs; and a separate versioned intake
task records opt-in registration, an explicit default decision and independent
review. Until then this task stays `DEFER`.

## What this package actually verifies

1. **Absence evidence.** Fifteen fixed probe locations are checked in the
   workspace and the SDK worktree (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale "absent" claim cannot be shipped.
2. **Admission boundary.** A caller-asset manifest and a timestamped receive
   trace have strict, task-local schemas. Every malformed, missing, invalid,
   nonfinite, aliased, duplicated or non-integral control is rejected before any
   state change. Two structural controls are admitted to prove the validators
   are not blanket-rejecting, and are explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads a payload, resolves a codec, reorders packets or computes jitter.
3. **Tool profile accounting.** Version, install location, provenance, clean
   checkout, typical use, caller-owned inputs, malformed inputs and missing
   optional selections are each recorded as blocked except the task-local
   malformed-input check. Compile/build, synthetic-runtime and measured-workload
   evidence are all `false`.
4. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and the cited sibling
   evidence are pinned by SHA-256 and verified unchanged. The installed v0
   geometry (16 kHz mono f32, 160 samples) is restated, not modified.

## Tool profile application

| Tool requirement | Status here | Evidence |
| --- | --- | --- |
| Version, install location, provenance | blocked | No NetEq source/runtime exists; all three fields are null. |
| Clean checkout or extracted package | blocked | No checkout or archive is present. |
| One typical CLI/API use | blocked | Nothing to invoke. |
| Caller-owned inputs | blocked | Manifest/trace schemas exist; no real input is supplied. |
| Malformed inputs | verified task-local only | 41 adverse controls rejected; 2 schema-only controls. |
| Missing optional selections | blocked | No runtime selection can be exercised. |
| Compile/build vs synthetic runtime vs workload | all false | No build, no runtime, no workload. |

## Admission contract (task-local; not an SDK or WebRTC contract)

- **Manifest** fields: `source_path`, `source_revision` (40 lower-hex),
  `source_sha256`, `license_path`, `license_sha256`, `runtime_path`,
  `runtime_sha256`, `trace_path`, `trace_sha256`,
  `internal_sample_rate_hz`, `packet_duration_ms`, `sdk_sample_rate_hz`,
  `sdk_channels`, `sdk_frame_samples`. Paths must be absolute and normalized;
  digests must be 64 lower-hex. SDK output geometry is fixed at 16000 Hz mono
  160 samples. `internal_sample_rate_hz × packet_duration_ms` must be an exact
  multiple of 1000. With probing enabled, every declared file must exist and
  match its digest.
- **Trace** fields: `trace_id`, `codec`, `sample_rate_hz`,
  `packet_duration_ms`, `packets`. Each packet carries `seq`, `rtp_timestamp`,
  `arrival_us`, `duration_samples`, `payload_bytes`, `payload_sha256` and
  `status` in `{received, lost}`. Packets are listed in receive-arrival order
  (`arrival_us` non-decreasing) and may be reordered by sequence; sequence and
  timestamp must be unique and must satisfy the 32-bit RTP relation against the
  first packet, including wrap. Lost packets must carry zero payload bytes and
  the empty-payload digest. Duplicate keys, `NaN`/`Infinity`, fractional
  integer fields, booleans in integer fields and unknown fields are rejected.
- No reordering, loss concealment, delay-target adaptation, decoding or playout
  is performed or implied by admission.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row projection gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | `ENG-03` record and `S41` lead |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Readable companion row |
| `source:research/task_backlog.json` | `0ac45fef49d433ad751ac2ff2674ea21e3717929d6ccc7dcda1fc3083db84ebc` | Legacy `F16` entry |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `webrtc-neteq` component row, Tool profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Tool acceptance profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery/build boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract, mapping/drain/timing rules |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build/integration surface |
| `docs/task-evidence/survey-eng-03/contract.json` | `1957fa53a5e74b8ea1bc612ef0c06e440a5213077021fd1f52b0361c090bb6c7` | Merged sibling `ENG-03` map |
| `docs/task-evidence/survey-eng-03/report.json` | `d7ff9ea111bf3ca8da8915b2bbda58a65143ec51f00620ed63b423424cb35ddf` | Merged gap/component record |
| `docs/task-evidence/survey-eng-03/README.md` | `d09dc8f09e16c7af0a1898d7c73bda8fc7002fa35cd49c5d8f5b21152fb6d6d9` | Merged scope/boundary |
| `docs/task-evidence/elastic-pcm-packets/contract.json` | `2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85` | Packet/PCM separation, bounded drain |
| `docs/task-evidence/elastic-pcm-packets/README.md` | `15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742` | Merged packet timing boundary |
| `docs/task-evidence/buffer-occupancy-controller/README.md` | `862a94c9add8ecd5e15f09a543ff17100dc5680da00f8a0635a884509cb51a33` | Merged synthetic occupancy control, not NetEq |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/README.md` | `ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df` | Codec-PLC control, no codec integration |
| `docs/task-evidence/granular-tsm/README.md` | `d97f06911fd90667288fe571c7a3f4210ece629f7e839c1d41200ceec48ec0a0` | Adjacent user-selected rate control, not jitter buffering |

The shared board row is read only by `verify.py`, and only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license boundary notes; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, manifest and trace admission validators, canonical report. |
| `run.py` | Byte-identical regeneration of `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | 61 deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/webrtc-neteq` with Python 3.12 and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; **61 tests pass, 0
failed, 0 skipped**; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Tool status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 15 absence probes (0 present), 6 required artifacts (0
present), 6 open blockers, 41 rejected admission controls, 2 schema-only
controls, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `G1` rights-cleared frozen packet traces | blocked | Rights-cleared immutable receive traces with provenance and timestamp domain. |
| `G2` permitted source/runtime/assets | blocked | Exact source revision, built runtime, codec runtime and license bundle pinned and permitted. |
| `G3` independent listening | blocked | Approved listening protocol and panel for the exact conditions. |
| `G4` target-device pacing and resources | blocked | Paced target-device runs with instrumented clocks, deadlines and limits. |
| `G5` opt-in provider intake | blocked | Separate versioned intake with OFF default and independent review. |
| `G6` public default selection | blocked | Explicit owner default decision after intake. |
| `G7` exact external reference parity | blocked | Same timestamped inputs replayed through an approved reference with exact accounting. |
| `G8` independent review and board transition | blocked | Reviewer verification from the pinned revision and a coordinator board transition. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`survey-eng-03` maps category `ENG-03` and names this task as the follow-up; it
contains no NetEq execution and is used here only as a pinned sibling record.
`buffer-occupancy-controller`, `elastic-pcm-packets`, `granular-tsm` and the PLC
packages are adjacent deterministic controls. They are **not** NetEq, not RTP
timestamp-domain replay and not codec-integrated playout, and none of their
numbers is reused, pooled or reinterpreted as a NetEq result. This package adds
no board row, handoff, provider, adapter or release artifact.
