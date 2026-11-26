<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPUS-PACKETIZATION-FEC-DTX-AND-COMFORT-NOISE — task-local blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `opus-packetization-fec-dtx-and-comfort-noise`. The structured
inventory assigns the **Tool** acceptance profile
(`verification_profile: tool`, `plan/INVENTORY.json`, category `ENG-04`), defined
in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**; `status=incomplete`,
`candidate_status=proposal_only_not_qualified`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does not contain, import, build, link, load, execute, download or
wrap Opus, libopus, CELT, SILK, DRED, LACE, a codec, an RTP stack, a packet
capture, a corpus or any other runtime. It reads no audio, replays no captured
packet trace, measures no clock and makes no quality, timing, availability,
parity or release claim. Only `docs/task-evidence/opus-packetization-fec-dtx-and-comfort-noise/`
is written; no provider, registry, descriptor, public header/ABI, shared CMake,
CI workflow or installed-v0 behavior changes.

## Exact external blocker

The catalogue lead is category `ENG-04 — Codec/packetization, FEC, DTX and
comfort noise` with named sources S43 (RFC 7587 Opus RTP), S44 (RFC 7874 WebRTC
audio requirements) and S30 (Opus 1.5 neural enhancement/loss recovery) in
`research/category_registry.json`. These are documentation/lead records only:
the registry pins no revision, source archive, runtime, trace or result. The
merged sibling map `docs/task-evidence/survey-eng-04/` records the same gap and
links this component.

Six exact blockers, all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | Permitted Xiph.Org Opus / libopus source snapshot with an exact immutable revision and archive SHA-256. No such snapshot exists at any fixed admitted probe. |
| `BLK-02` | The upstream Opus BSD-3-Clause `COPYING`, `LICENSE_PLEASE_READ.txt`, copyright notices and rights decision for that revision. None is present. |
| `BLK-03` | A reproducible pinned Opus build, install location, exported ABI and artifact digest. Nothing was built or installed. |
| `BLK-04` | A rights-cleared frozen packet trace with packetization mode, DTX state, in-band FEC/LBRR presence, payload digests and an exact erasure mask. Only synthetic traces exist here. |
| `BLK-05` | A rights-cleared speech/noise cohort and an approved listening or independent quality protocol for DTX, comfort-noise and FEC. None is present. |
| `BLK-06` | A target-runtime/device harness with agreed pacing, deadline, CPU, memory and workload budgets. None exists. |

Opus is normally distributed under the BSD-3-Clause license together with a
patent/implementation notice bundle. The license files, notices, source
revision and redistribution/product-use scope for any specific artifact are
**unverified here**. Nothing was copied, vendored, built, downloaded or
redistributed. `DEFER` is the only defensible decision: without the permitted
source and runtime, Opus packetization, FEC, DTX and comfort noise cannot be
reproduced, compared or measured, and inventing a substitute would misstate the
boundary.

**Observed but never admitted.** One `libopus.0.dylib` (version string
`libopus 1.6.1`, SHA-256
`dca12b81b778f51dc5cecbc789fffaac472de09b102a164d5348b360b238a202`) exists
inside a **gitignored, mutable PyAV virtualenv** of an unrelated pipeline
(`cpp-library/pipeline-validation/playback-speed/.venv/.../av/.dylibs/`). It
ships no Opus license text, no source revision and no rights review, and it is
not the exact licensed pinned artifact. It is recorded as provenance only and is
**not** admitted, linked, executed or used for any result. A read-only
version-string probe during authoring is the only contact.

**Reopen condition.** A caller supplies the permitted Opus source revision and
immutable archive, the license/notices bundle, a reproducible build and
runtime, rights-cleared packet/erasure traces with declared timestamp domain
and DTX/FEC state, a rights-cleared media cohort with an approved quality
protocol, and a target harness with agreed budgets; the pinned runtime
reproduces approved reference outputs; and a separate versioned intake task
records opt-in registration, an explicit OFF default and independent review.
Until then this task stays `DEFER`.

## What this package actually verifies

1. **Absence evidence.** Twenty fixed probe locations are checked in the
   workspace and the SDK worktree (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any
   admitted probe later appears, so a stale "absent" claim cannot be shipped.
2. **Admission boundary.** A caller-asset manifest, a transmit packet and a
   packet trace have strict, task-local schemas. Every malformed, missing,
   invalid, nonfinite, aliased, duplicated or non-integral control is rejected
   before any state change. Three structural controls are admitted to prove the
   validators are not blanket-rejecting, and are explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`.
3. **Synthetic packet-container model.** A deterministic, integer-only
   first-order delta + zigzag-varint container exercises packetization,
   previous-frame redundancy, DTX/comfort-noise accounting and PLC fallback
   behaviour at the *contract* level. It is explicitly **not Opus, not RFC
   6716, not CELT/SILK and not a codec result**; no payload size, recovery
   depth or comfort-noise level describes any real implementation.
4. **Tool profile accounting.** Version, install location, provenance, clean
   checkout, typical use, caller-owned inputs, malformed inputs and missing
   optional selections are each recorded as blocked except the task-local
   malformed-input check. Compile/build, codec synthetic-runtime and
   measured-workload evidence are all `false`.
5. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and the cited
   merged sibling evidence are pinned by SHA-256 and verified unchanged. The
   installed v0 geometry (16 kHz mono f32, 160 samples) is restated, not
   modified.

## Tool profile application

| Tool requirement | Status here | Evidence |
| --- | --- | --- |
| Version, install location, provenance | blocked | No admitted source/runtime exists; all three fields are null. |
| Clean checkout or extracted package | blocked | No checkout or archive is present. |
| One typical CLI/API use | blocked | Nothing to invoke. |
| Caller-owned inputs | blocked | Manifest/packet/trace schemas exist; no real input is supplied. |
| Malformed inputs | verified task-local only | 49 adverse controls rejected; 3 schema-only controls. |
| Missing optional selections | blocked | No runtime selection can be exercised. |
| Compile/build vs codec synthetic runtime vs workload | all false | No build, no codec runtime, no workload. The container model is not runtime evidence. |

## Packet contract (task-local; distinct from PCM)

The contract is `audio-sdk/synthetic-packet-container/0.1`. It is deliberately
a **packet** contract, not a PCM frame contract.

- **PCM frame fields:** `sample_index`, `label`, `samples[160]` (signed integer
  proxy).
- **Transmit packet fields:** `seq`, `timestamp`, `duration_samples`,
  `frame_count`, `kind`, `fec_copy_of`, `payload_bytes`, `payload_sha256`,
  `payload_hex`.
- **Receive packet fields:** `seq`, `timestamp`, `duration_samples`,
  `frame_count`, `arrival`, `status`, `recovery`, `payload_sha256`.
- **Tag byte:** bits 0–1 `frame_count−1`, bit 2 `fec_copy_present`, bits 3–4
  `kind` (0 audio, 1 comfort noise), bits 5–7 reserved and must be zero.
- **Frame encoding:** first-order sample delta, zigzag signed mapping, 7-bit
  little-endian varint; each frame length-prefixed with two big-endian bytes.
- **FEC model:** a synthetic copy of the previous packet's first frame embedded
  in the next contiguous audio packet, one packet deep. Not Opus LBRR.
- **DTX model:** deterministic mean-absolute-energy gate. `omit` drops silent
  source frames; `cn` emits one bounded comfort-noise packet per silent run.

The model verifies: exact encoder/decoder round-trip, 10/20/30 ms packetization
grids, DTX suppression, bounded comfort noise, single-loss FEC recovery, a
two-packet burst recovering only the last packet, PLC fallback, complete frame
accounting and byte-reproducible packet traces. None of these is a codec
result.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row projection gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | `ENG-04` record and S30/S43/S44 leads |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` | Readable companion row |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row, Tool profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Tool acceptance profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery/build boundary |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Adjacent Opus 1.4 row provenance only |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Adjacent component provenance only |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/survey-eng-04/README.md` | `c3c2f353f7fd647f2a1a0ea59736acfb49c1913915e1d5053d7172b0d4c82666` | Merged `ENG-04` map |
| `docs/task-evidence/survey-eng-04/contract.json` | `d13c92601c151d04bf026c4ab166d42f85836351b0c7123e75b8d880d2476ea0` | Merged `ENG-04` contract |
| `docs/task-evidence/survey-eng-04/report.json` | `c11355762f528e51c8ea92782d921414b8221b0eb0b3ecee74227ac735e97583` | Merged `ENG-04` report |
| `docs/task-evidence/elastic-pcm-packets/contract.json` | `2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85` | Packet/PCM separation, bounded drain |
| `docs/task-evidence/elastic-pcm-packets/README.md` | `15ebaa6b2b7768faa5c1bd2fc45b900db7f71d49b7ad1292685263555953e742` | Merged packet timing boundary |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/README.md` | `ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df` | Codec-PLC control, no codec integration |
| `docs/task-evidence/webrtc-neteq/contract.json` | `4a6c8e05189db69ea537b3a7715ac076ca2a8bf779c139589dde5088fc75666f` | Receive-side boundary, tool profile |
| `docs/task-evidence/webrtc-neteq/README.md` | `315f5ba9835f1c09df0981740c9dbaf3da6f0224001c012b0e138cc90cb01857` | Merged blocked sibling |

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license boundary notes; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, packet model, disposition. |
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, manifest/packet/trace admission validators, deterministic synthetic packet-container model, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | 101 deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report/contract bytes, sidecars, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/opus-packetization-fec-dtx-and-comfort-noise` with
Python 3.12 and stdlib only:

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

Expected: `run.py` reports `repeat=3 byte_identical=true`; **101 tests pass, 0
failed, 0 skipped**; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Tool status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 20 absence probes (0 present), 6 required artifacts (0 present),
6 open blockers, 49 rejected admission controls, 3 schema-only controls, 8
blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `G1` rights-cleared frozen packet traces and media | blocked | Rights-cleared immutable traces with provenance, timestamp domain and erasure mask. |
| `G2` permitted source, runtime and assets | blocked | Exact Opus revision, reproducible runtime and license/notices bundle pinned and permitted. |
| `G3` independent listening and DTX/CN quality | blocked | Approved listening or predictive protocol for the exact conditions. |
| `G4` target runtime timing and resources | blocked | Paced target runs with instrumented clocks, deadlines and resource limits. |
| `G5` opt-in provider intake | blocked | Separate versioned intake with OFF default and independent review. |
| `G6` public default selection | blocked | Explicit owner default decision after intake. |
| `G7` exact external reference parity | blocked | Same packetization inputs and erasure masks replayed through the approved runtime. |
| `G8` independent review and board transition | blocked | Reviewer verification from the pinned revision and a coordinator board transition. |

No synthetic admission control or container-model result opens a gate. No
missing result is promoted.

## Separation from other evidence

`survey-eng-04` maps category `ENG-04` and names this component; it executes no
codec and is used here only as a pinned sibling record. The merged
`elastic-pcm-packets` fixture separates PCM chunks from timestamped packets and
proves single-erasure XOR recovery, but it is **not** codec FEC, Opus LBRR, RTP
or DTX/CNG. `opus-1-4-standard-decoder-plc`, `zero-fill-plc`,
`pitch-period-repeat-plc`, `autoregressive-plc`, `linear-interpolation-plc` and
`webrtc-neteq` are adjacent deterministic controls; none of their numbers is
reused, pooled or reinterpreted as an Opus packetization, FEC, DTX or
comfort-noise result. This package adds no board row, handoff, provider,
adapter or release artifact.
