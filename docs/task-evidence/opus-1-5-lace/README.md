<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OPUS-1-5-LACE — Opus 1.5 LACE readiness blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `Opus 1.5 LACE` (`component_id=opus-1-5-lace`). The structured
inventory assigns the **Restoration** acceptance profile
(`verification_profile: restoration`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before any implementation or
intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing evidence never qualifies a
candidate.

This package does **not** contain, import, build, link, download or execute
Opus 1.5, libopus, OSCE, LACE, NoLACE, a decoder, a model, a weight, a codec
stream or any other runtime. It reads no audio, decodes no packet, replays no
traffic, measures no output peak or clock and makes no quality, listening,
timing, benchmark or release claim. It records the exact missing artifacts,
probes a fixed list of task-local paths to evidence their absence, and defines a
fail-closed admission boundary for the cohort manifest a future qualified run
would need. Only `docs/task-evidence/opus-1-5-lace/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow or
installed-v0 behavior changes.

## Exact external blocker

The catalogue lead is `S30` — “Opus 1.5 neural enhancement and loss recovery” at
`https://opus-codec.org/demo/opus-1.5/` (`research/category_registry.json`,
pinned below). It is a public documentation lead only: the registry pins no
revision, source archive, runtime, model asset or result. The inventory record
(`opus-1-5-lace`, `evidence_status=considered`) and
`research/distortion_restoration_20261028.md` point to the same gap: LACE/NoLACE
are codec-integrated Opus 1.5 postfilters that are **not enabled by default**,
and no local Opus 1.5 build or packet-level integration exists.

Six exact blockers, all open:

| Blocker | Missing artifact requirement |
| --- | --- |
| `BLK-01` | Permitted Opus 1.5 source tree at an exact 40-hex revision with immutable archive SHA-256, including the OSCE/LACE decoder paths. No such snapshot exists at any fixed probe path. |
| `BLK-02` | The upstream license text, copyright notices, model-data/weight terms and complete third-party notice bundle for that revision, with an explicit rights review. |
| `BLK-03` | A reproducible pinned libopus 1.5 build with the exact decoder option name, accepted values, default state, install location and artifact digest. |
| `BLK-04` | The exact LACE/NoLACE model assets or compiled model blobs, inference runtime, feature/state geometry, per-asset SHA-256 and permitted-use terms. |
| `BLK-05` | A rights-cleared frozen cohort of genuine low-bitrate Opus traffic with packet metadata, degradation/erasure/bandwidth strata and the corresponding clean/audio packet baseline. |
| `BLK-06` | A task-specific quality, independent listening, output-peak and target-runtime timing/resource protocol with agreed margins, deadlines and limits. |

Opus source is normally distributed under the Xiph BSD-3-Clause license, but the
license file, notices, model/weight terms, source revision and
redistribution/product-use scope for any specific artifact are **unverified
here**. Nothing was copied, vendored, built, downloaded or redistributed.
`DEFER` is the only defensible decision: without the source, model asset and a
permitted runtime, LACE cannot be reproduced, selected, compared or measured,
and inventing a generic postfilter would misstate the boundary. The pinned
research note explicitly warns that generic postfiltering should be avoided when
the codec is unknown (`RST-03`), so no surrogate is shipped.

**Reopen condition.** A caller supplies the permitted Opus 1.5 source revision
and immutable archive, the license/notices/model-terms bundle, a reproducible
build with the exact LACE decoder option and default state, the exact model
assets and inference runtime, rights-cleared genuine low-bitrate traffic with
packet metadata and a clean/packet baseline, and a target-runtime/quality/
listening harness with agreed budgets; the pinned runtime reproduces approved
reference outputs; and a separate versioned intake task records opt-in
registration, an explicit default decision and independent review. Until then
this task stays `DEFER`.

## What this package actually verifies

1. **Absence evidence.** Nineteen fixed probe locations are checked in the
   workspace and the SDK worktree (no recursive workspace walk). All are absent.
   `reference.build_report()` and `verify.py` raise or fail if any probe later
   appears, so a stale “absent” claim cannot be shipped.
2. **Admission boundary.** A caller cohort manifest has a strict, task-local
   schema. Every malformed, missing, invalid, nonfinite, aliased, duplicated,
   out-of-range or non-integral control is rejected before any state change. One
   structural control is admitted to prove the validator is not
   blanket-rejecting, and is explicitly labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads a payload, invokes a decoder or computes concealment.
3. **Restoration profile accounting.** Corruption freeze, metadata, clean/audio
   packet baseline, degradation/erasure/bandwidth strata, discrete concealment/
   validity, decoded intervals, task-specific quality, output peaks and timing
   are each recorded as **blocked**. The structural schema control is not a
   result.
4. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and the cited sibling
   evidence are pinned by SHA-256 and verified unchanged. The installed v0
   geometry (16 kHz mono f32, 160 samples) is restated, not modified.

## Restoration profile application

| Restoration requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze corruption, metadata and corresponding clean/audio packet baseline | blocked | No genuine traffic, packet metadata or clean baseline is present. |
| Stratify by degradation, erasure burst and bandwidth | blocked | Strata exist only as an unused admission schema. |
| Discrete concealment/validity and decoded intervals | blocked | Nothing is decoded; no received/lost/concealed/valid interval is reported. |
| Task-specific quality on genuine low-bitrate traffic | blocked | No LACE output, clean reference, pinned scorer or listening result. |
| Output peak and timing bounds | blocked | No output samples and no runtime measurement. |

No synthetic or schema-control value is promoted into any of these rows.

## Admission contract (task-local; not an SDK or Opus contract)

- **Manifest** fields: `schema_id`, `cohort_id`, `source_revision` (40 lower
  hex), `source_sha256`, `source_path`, `license_path`, `license_sha256`,
  `runtime_path`, `runtime_sha256`, `decoder_option`, `traffic`,
  `clean_reference`, `strata`, `packets`. Paths must be absolute and normalized;
  digests must be 64 lower-hex. Unknown and missing fields are rejected.
- **Decoder option**: exact `name`, `value` (bool/int/string only), `source_path`
  and `source_sha256`. This records what a future pinned build must identify; it
  does not assert that any particular API or constant exists.
- **Traffic**: `codec="opus"`, `codec_version="1.5"`, one of 8/12/16/24/48 kHz,
  1–2 channels, `packet_duration_us` in 2,500–120,000 and a multiple of 250,
  `bitrate_bps` in 6,000–512,000, plus an immutable corpus path/digest and a
  rights reference. No audio is opened.
- **Clean reference**: absolute path, digest, alignment in
  `{sample_exact, declared_offset}` and a non-negative offset. `sample_exact`
  requires offset zero.
- **Strata**: non-empty, unique IDs, degradation in
  `{low_bitrate, packet_loss, bandwidth_limited, mixed}`, bandwidth 0–48,000 Hz
  and burst length 0–1,000 frames.
- **Packets**: at most 100,000, contiguous indexes, status in
  `{received, lost, concealed}`. `received` carries positive valid and decoded
  samples plus a non-empty payload digest; `lost`/`concealed` carry zero valid
  samples and the empty-payload digest. At least one received packet is
  required. No reordering, PLC, decoding or timing analysis is performed.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` | `S30` public lead |
| `source:research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | `RST-03` LACE/NoLACE boundary |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Adjacent Opus 1.4 control, not LACE |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `opus-1-5-lace` component row |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Restoration profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/README.md` | `ac4ed82328dbbfc1af8aefbd43f2efc5ce36bde9f004e6f40bbc46b23db962df` | Merged PLC sibling, not LACE |
| `docs/task-evidence/opus-1-4-standard-decoder-plc/report.json` | `ec4c9ea5e46e02d9866920458b4d6365d300d8bcd626d2e05bf7f4c4955a080e` | Merged PLC sibling, not reused |

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
| `reference.py` | Stdlib-only strict JSON, pin/absence/projection checks, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/opus-1-5-lace` with Python 3.12 and stdlib only:

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

Current counts: 19 absence probes (0 present), 6 required artifacts (0
present), 6 open blockers, 41 rejected admission controls, 1 schema-only
control, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` upstream source and revision pin | blocked | Exact source revision, tree and archive digests recorded from a reviewable source root. |
| `RG-02` license, model terms and notices | blocked | Complete license/notices/model-terms bundle supplied and reviewed. |
| `RG-03` exact build and decoder-option parity | blocked | Pinned build/install with the exact LACE option, values and default state mapped to this boundary. |
| `RG-04` LACE asset and runtime integrity | blocked | Every model asset/runtime pinned by SHA-256 with geometry, provenance and permitted use. |
| `RG-05` rights-cleared low-bitrate cohort | blocked | Immutable genuine low-bitrate traffic, metadata, strata and clean/packet baseline supplied. |
| `RG-06` task-specific quality and listening | blocked | Pinned scorers and an approved listening protocol/panel produce reviewed results. |
| `RG-07` target-runtime timing, peaks and resources | blocked | Paced runs record timing, peaks, CPU, memory and deadline behavior against agreed limits. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, explicit public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

`opus-1-4-standard-decoder-plc` is an adjacent deterministic *synthetic*
decoder-PLC-style control. It does not vendor, link or execute Opus, and its
README explicitly says it is not Opus 1.5 deep PLC/DRED. It is **not** LACE, not
OSCE and not a decoder-option result; none of its numbers is reused, pooled or
reinterpreted here. `REALTIME_COMPONENT_CANDIDATES.md` records the same 1.4
boundary. This package adds no board row, handoff, provider, adapter or release
artifact.

## Expected digest

`report.json` SHA-256:
`9b98c595d812b724b523a5d748828452980946b9292a9d54c0ac9b804dabbf5b`.
