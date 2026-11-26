<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPUS-DEEP-PLC — Opus deep PLC readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `Opus deep PLC` (`component_id=opus-deep-plc`). The structured
inventory assigns the **Restoration** acceptance profile
(`verification_profile: restoration`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation or
intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download or execute
Opus, libopus, the deep-PLC decoder path, a deep-PLC model or weight, a packet,
a missing-packet event trace, a codec stream, a speech corpus or any other
runtime. It reads no audio, decodes no packet, conceals no interval, generates
no event, measures no peak, delay or quality and makes no listening, timing,
benchmark or release claim. It records the exact missing artifacts, probes a
fixed list of task-local paths to evidence their absence, and defines a
fail-closed admission boundary for the cohort manifest a future qualified run
would need. Only `docs/task-evidence/opus-deep-plc/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

Opus deep PLC is the neural packet-loss-concealment path associated with
Opus 1.5 and later (`research/distortion_restoration_20261028.md`, `RST-04`). The pinned
evidence records the boundary precisely: for Opus transport, evaluate the
built-in deep PLC and DRED redundancy when integration and extra
bitrate/latency are allowed; DRED specifically addresses burst losses through
transmitted redundancy, while deep PLC reconstructs a lost interval from
decoder state. Both require a compatible Opus build and packet-level
integration. The inventory row is `opus-deep-plc`
(`evidence_status=considered`), and no local Opus 1.5+ build, deep-PLC model,
selector, packet corpus or loss trace exists.

**Opus 1.4 standard decoder PLC evidence is not reused.** The merged
`docs/task-evidence/opus-1-4-standard-decoder-plc/` package is a synthetic
deterministic decoder-PLC-style control; it does not vendor, link or execute
Opus, and it is not Opus 1.5 deep PLC. Its numbers are pinned as adjacent
provenance only and never pooled with this package.

Six exact blockers, all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | Permitted Opus source tree at an exact 40-hex revision, version >= 1.5, containing the deep-PLC decoder path and model data, with an immutable archive SHA-256. No such snapshot exists at any fixed probe path. |
| `BLK-02` | Upstream BSD-3-Clause license text, copyright notices, deep-PLC model-data/weight terms and complete third-party notice bundle, with an explicit rights review. |
| `BLK-03` | A reproducible pinned libopus build with the exact deep-PLC selector/API names, accepted values, decoder symbols, default state, standard-PLC contrast and artifact digest. |
| `BLK-04` | The exact deep-PLC model assets or compiled model blobs, inference runtime, feature/state geometry, per-asset SHA-256 and permitted-use terms. |
| `BLK-05` | A rights-cleared frozen packet corpus whose losses are **explicit missing-packet events reported to the decoder**, with packet metadata, loss strata, a matching standard-PLC control and the corresponding clean/source baseline. |
| `BLK-06` | A task-specific quality, independent listening, output-peak, concealment-interval, content/availability-delay and target-runtime timing/resource protocol with agreed margins, deadlines and limits. |

Nothing was copied, vendored, built, downloaded or redistributed. `DEFER` is
the only defensible decision: without the source, model asset, selector, a
matched standard-PLC control and a permitted missing-event trace, deep PLC
cannot be reproduced, selected, compared or measured, and inventing a generic
PLC substitute would misstate the boundary. No surrogate is shipped.

**Reopen condition.** A caller supplies the permitted Opus 1.5+ source revision
and immutable archive, the license/notices/model-terms bundle, a reproducible
build with the exact deep-PLC selector and default state, the exact deep-PLC
model assets and inference runtime, a rights-cleared packet corpus with
explicit missing-packet events plus a standard-PLC control and clean baseline,
and the target-runtime, quality and listening harness with agreed budgets; the
pinned runtime reproduces approved reference outputs; and a separate versioned
intake task records opt-in registration, an explicit default decision and
independent review. Until then this task stays `DEFER`.

## Boundary: v0 frames versus packet-level concealment

The shipped public v0 facade processes `as_frame_v0` float frames at 16 kHz,
mono, 160 samples per call. It has no packet, payload or transport-loss input.
Deep PLC is meaningful only across a packet timeline: a decoder observes an
explicit missing-packet event, advances its recurrent state and produces a
concealment interval. A future deep-PLC adapter therefore needs the separate
packet-I/O contract and an explicit event/reporting model; it cannot be
represented by the current frame callback without inventing a private
transport. This package defines only the admission metadata for that future
cohort and executes nothing. The installed v0 geometry is restated, not
modified.

## What this package actually verifies

1. **Absence evidence.** Twenty-nine fixed probe locations are checked in the
   workspace and the SDK worktree (no recursive workspace walk). All are
   absent. `reference.build_report()` and `verify.py` raise or fail if any probe
   later appears, so a stale “absent” claim cannot be shipped. One unqualified
   PyAV dylib is recorded separately as provenance only (`admitted=false`,
   `executed_by_package=false`, `used_for_evidence=false`).
2. **Explicit missing-packet events.** A caller cohort manifest has a strict,
   task-local schema. Loss is represented only by explicit events: every
   missing packet must be covered by exactly one event, events are ordered and
   non-overlapping, each event must be `reported_to_decoder=true`, and every
   event has exactly one concealment output whose sample count equals
   `packet_count × samples_per_packet`. An inferred loss from a sequence gap is
   rejected. Every malformed, missing, invalid, nonfinite, aliased, duplicated,
   out-of-range or non-integral control is rejected before any state change.
   One structural control is admitted to prove the validator is not
   blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads a payload, invokes a decoder or produces concealment.
3. **Restoration profile accounting.** Corruption freeze, metadata, clean/audio
   packet baseline, degradation/erasure/bandwidth strata, discrete concealment/
   validity, decoded intervals, task-specific quality, output peaks and timing
   are each recorded as **blocked**. The structural schema control is not a
   result.
4. **Deep-PLC measurement accounting.** Explicit missing events, concealed
   interval samples, output peaks, content/availability delay and
   deep-PLC-versus-standard-PLC quality are each recorded as **blocked** with
   `value=null`. No measurement is inferred from the admission schema or from
   another Opus task.
5. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and the cited sibling
   evidence are pinned by SHA-256 and verified unchanged.

## Restoration profile application

| Restoration requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze corruption, metadata and corresponding clean/audio packet baseline | blocked | No genuine packet corpus, explicit missing-packet event trace, packet metadata or clean baseline is present. |
| Stratify by degradation, erasure burst and bandwidth | blocked | Strata exist only as an unused admission schema. |
| Discrete concealment/validity and decoded intervals | blocked | Nothing is decoded; no missing event, concealed, valid or decoded interval is reported. |
| Task-specific quality on genuine low-bitrate traffic | blocked | No deep-PLC output, standard-PLC control, clean reference, pinned scorer or listening result. |
| Output peak and timing bounds | blocked | No output samples and no runtime measurement. |

## Deep-PLC measurement requirements (all blocked)

| ID | Metric | Status | Value |
| --- | --- | --- | --- |
| `MR-01` | explicit_missing_packet_events | blocked | `null` |
| `MR-02` | concealed_interval_samples | blocked | `null` |
| `MR-03` | output_peak_q15 | blocked | `null` |
| `MR-04` | content_and_availability_delay_samples | blocked | `null` |
| `MR-05` | deep_plc_vs_standard_plc_quality | blocked | `null` |

No value is promoted from the schema control, from Opus 1.4 standard decoder
PLC, from DRED, from LACE/NoLACE or from the packetization/FEC task.

## Admission contract (task-local; not an SDK or Opus contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source_revision` (40 lower
  hex), `source_sha256`, `source_path`, `license_path`, `license_sha256`,
  `runtime_path`, `runtime_sha256`, `deep_plc_api`, `restoration`,
  `clean_reference`, `strata`, `missing_events`, `packets`,
  `concealment_outputs`, `score_protocol`. Paths must be absolute and
  normalized; digests must be 64 lower-hex. Unknown and missing fields are
  rejected.
- **Deep-PLC API**: exact `selector_name`, integer `selector_value` 0–65535,
  `default_state` in `{disabled, enabled}`, `decoder_symbol`, `source_path` and
  `source_sha256`. This records what a future pinned build must identify; it
  does not assert that any particular upstream constant exists.
- **Restoration**: `codec="opus"`, `codec_version` matching `1.5`/`1.6` (with an
  optional patch suffix), **16 kHz mono** to map to the SDK boundary, packet
  duration 2,500–120,000 µs in 250 µs steps, `bitrate_bps` 6,000–512,000,
  `concealment_mode` in `{deep_plc, standard_plc_control}`, a loss-trace digest,
  a nonnegative `expected_delay_samples` (<= 96,000) and `baseline_control` in
  `{standard_plc, no_concealment}`. Bounds are this task's admission bounds,
  not claims about upstream API limits.
- **Clean reference**: absolute path, digest, alignment in
  `{sample_exact, declared_offset}` and a non-negative offset. `sample_exact`
  requires offset zero.
- **Strata**: non-empty, unique IDs, degradation in
  `{packet_loss, burst_loss, low_bitrate, mixed}`, bandwidth 0–16,000 Hz and
  burst length 0–1,000 packets.
- **Missing events**: non-empty, unique `event_id`, ordered non-overlapping
  `first_packet_index`/`packet_count` ranges, cause in
  `{network_loss, late_arrival, corrupt_payload}`, detector in
  `{sequence_gap, rtp_marker, explicit_trace}` and `reported_to_decoder=true`.
  Every missing packet and only a missing packet is covered, exactly once.
- **Packets**: at most 100,000, contiguous indexes, status in
  `{received, missing}`. `received` carries exactly `samples_per_packet` valid
  and produced samples, a positive payload byte count and a non-empty payload
  digest. `missing` carries zeros, the empty-payload digest and the covering
  event ID.
- **Concealment outputs**: exactly one per event, in event order,
  `concealed_samples = packet_count × samples_per_packet`,
  `valid_samples=0` and `peak_q15` 0–32767. No audio is generated.
- **Score protocol**: non-empty unique `metrics` from `{si_sdr, stoi, rmse}`,
  `control="standard_plc"`, `paired_clean_reference=true` and
  `minimum_items` 1–10,000.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | Category context (no deep-PLC lead) |
| `source:research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | `RST-04` deep-PLC/DRED boundary |
| `source:research/voice-enhancement-20261101/agent-opus-plc/REPORT.md` | `79cf82e29f231f45ebb65421e5a5e0f712de28c47cd115443b1edae3fcdc850b` | Opus 1.4 PLC sibling, not reused |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Adjacent Opus 1.4 control, not deep PLC |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `opus-deep-plc` component row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/README.md` | `ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df` | Merged PLC sibling, not deep PLC |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/report.json` | `ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e` | Merged PLC sibling, not reused |
| `docs/task-evidence/opus-dred/report.json` | `2997dc6cc9e623a762379ca498c178c22a9607591a39ea8bcf6ef2691544a3f2` | Merged DRED sibling, not reused |
| `docs/task-evidence/pitch-period-repeat-plc/README.md` | `8fb323ffd7ce59c361ac1078d7c434b1b3c0b5f088d9a7d07ae5b2278cfa3ea9` | Merged restoration control, not reused |

The shared board row is read only by `verify.py`, and only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The full mutable
`TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, boundary, pins, commands, counts, gates. |
| `LICENSES.md` | Upstream/license boundary notes; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, explicit-missing-event admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/opus-deep-plc` with Python 3.12 and stdlib only:

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

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Restoration status=incomplete decision=DEFER`;
REUSE reports no missing or bad license; `git diff --check` is clean.
`verify.py` itself writes only to a temporary directory and never to this
package.

Current counts: 29 absence probes (0 present), 6 required artifacts (0
present), 6 open blockers, 88 rejected admission controls, 1 schema-only
control, 5 blocked restoration rows, 5 blocked deep-PLC measurement rows, 8
blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` upstream source and revision pin | blocked | Exact source revision, tree and archive digests recorded from a reviewable source root. |
| `RG-02` license, model terms and notices | blocked | Complete license/notices/model-terms bundle supplied and reviewed. |
| `RG-03` exact build and deep-PLC selection parity | blocked | Pinned build/install with the exact deep-PLC selector, symbols, default state and standard-PLC contrast mapped to this boundary. |
| `RG-04` deep-PLC model and runtime integrity | blocked | Every model asset/runtime pinned by SHA-256 with geometry, provenance and permitted use. |
| `RG-05` rights-cleared explicit missing-event cohort | blocked | Immutable corpus and event trace, metadata, strata, standard-PLC control and clean/source baseline supplied. |
| `RG-06` task-specific quality and listening | blocked | Pinned scorers and an approved listening protocol/panel produce reviewed results. |
| `RG-07` concealment, peaks, delay and resources | blocked | Paced runs record explicit events, concealment intervals, peaks, delay, CPU, memory and deadline behavior against agreed limits. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, explicit public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`opus-1-4-standard-decoder-plc` is an adjacent deterministic *synthetic*
decoder-PLC-style control. It does not vendor, link or execute Opus, and its
README explicitly says it is not Opus 1.5 deep PLC/DRED. `opus-dred` targets
transmitted redundancy, not decoder-state neural concealment. `opus-1-5-lace`
targets codec-integrated LACE/NoLACE postfilters, and
`opus-packetization-fec-dtx-and-comfort-noise` models packet framing, FEC, DTX
and comfort noise. None of their numbers is reused, pooled or reinterpreted
here. This package adds no board row, handoff, provider, adapter or release
artifact.

## Expected digest

`report.json` SHA-256:
`df8cb2dad636a6d1ded205b872297ddf43936c65dfc75febc5e6c5f4f0415df2`.
