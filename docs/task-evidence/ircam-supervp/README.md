<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-IRCAM-SUPERVP — IRCAM SuperVP readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the IRCAM
SuperVP external-adapter row. It is **not** a SuperVP integration. No vendor
source, SDK, binary, host plug-in, trial, runtime, commercial agreement, price,
rate cohort, reference, parity vector, real audio, listening result, device
measurement, benchmark or release claim is present. **No result here qualifies
IRCAM SuperVP.**

The structured inventory marks `ircam-supervp` as
`evidence_status=considered`, disposition `external-adapter`, with the **Rate**
acceptance profile (`verification_profile: rate`, `plan/INVENTORY.json`). The
task is an external-adapter/feasibility investigation: verify runnable source,
exact assets, permitted scope, task geometry and matched evidence, then either
model a caller-supplied-asset adapter reference or record a strict readiness
conclusion with the exact external blocker and reopen condition. None of those
prerequisites exists.

Pinned base: `f006454da9a72fbfd394e2b5bd05105201a9cd29`.
Branch: `swarm/SDK-IRCAM-SUPERVP`. Owner: `agent-IRCAM-SUPERVP`.
Reviewer: `reviewer-IRCAM-SUPERVP`.

## Exact external blocker

IRCAM SuperVP is a **commercial/research vendor engine**, not open source. The
recorded research note
(`cpp-library/pipeline-validation/playback-speed-candidates.md`, §3.9) states:

> **Licence:** commercial/research access through the IRCAM Forum software
> suite; no public open-source licence. Terms must be negotiated with IRCAM.
>
> **Commercial use:** possible under an agreement; not verified in this pass.
>
> **Limits:** heavy integration, research-grade API, procurement. TS2 is
> distributed as an application; embedding it needs a separate agreement with
> IRCAM.
>
> **Evidence status:** product description verified from the IRCAM/Anasynth
> page; current SDK availability and pricing not verified.

Public identity references only: <http://anasynth.ircam.fr/home/english/software/supervp>
and <https://forum.ircam.fr/projects/detail/ts2/>. In short, embedding the
engine requires a separate agreement with IRCAM before any adapter exists.

No licensed SuperVP SDK, engine binary, host runtime, version, build number,
platform artifact, per-file SHA-256, API reference, sample rate, channel
layout, hop, latency, rate semantics, price, quote, commercial agreement,
redistribution grant, output-use right or indemnity term is present or
recorded. **The commercial licensing path is itself the blocker**, not a
formality: embedding TS2 in this SDK requires a separate negotiated IRCAM
agreement before any adapter can be modelled.

Nothing was fabricated, reconstructed, mirrored, downloaded, purchased,
licensed, trialed or substituted. No revision, file name, byte count or SHA-256
is asserted as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Licensed vendor engine | The exact IRCAM SuperVP SDK or host runtime at a pinned version and build, with a reviewed licence and terms record and per-file SHA-256 |
| Vendor build identity | Version, build number, platform artifact and digest; only a public product description is recorded |
| Commercial agreement | A signed IRCAM Forum or direct commercial agreement covering embedding, redistribution, output use, attribution, price and patent/indemnity |
| Runtime and platform lock | An isolated offline runtime, lock file and recorded platform |
| API and geometry reference | The licensed API reference fixing rate semantics, sample rate, channels, hop, latency, reset, flush and final partial-window behaviour |
| Rate cohort and references | A rights-cleared frozen cohort covering 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window |
| Parity vector | An approved exact-runtime output vector on a frozen caller-supplied input and configuration |
| Rights and outputs | Permitted source, reference, output-use, redistribution and patent terms with complete notices |

The machine-readable record is `report.json` → `upstream_record`,
`source_reported_context`, `asset_requirements`, `asset_audit`,
`absence_probes`, `caller_asset_contract`, `exact_blockers`, `geometry`,
`rate_profile` and `gates`. `contract.json` carries the same disposition,
pins, geometry and all eight blocked release gates.

## Candidate context (read, not attributed)

The same research note reviews the time-stretch and rate candidates as a
group. It ranks Bungee Basic (MPL-2.0), Signalsmith Stretch (MIT), SoundTouch
(LGPL-2.1 or commercial) and Sonic (Apache-2.0) as the practical permissive or
LGPL options, with zplane elastique, Zynaptiq ZTX, Bungee Pro and IRCAM SuperVP
as paid premium options. It places SuperVP as a **research/premium fallback**,
not a first prototype, because of procurement, a research-grade API and a
separate embedding agreement. No sibling candidate's result, digest, timing,
licence conclusion or asset is inherited or attributed here.

## What this package verifies

1. **Absence evidence.** Seventeen fixed workspace/worktree probes are checked;
   no recursive walk is performed and no home cache is scanned. All are absent.
   `reference.absence_probes()` and `verify.py` fail if any probe later
   appears, so a stale "absent" claim cannot be shipped.
2. **Stable pins.** The inventory, the Rate acceptance profile, the SDK plan
   instructions and the playback-speed research note are pinned by SHA-256.
   These are read-only provenance inputs, not vendor evidence. The public v0
   boundary files (`CONTRACTS.md`, both public headers, `CMakeLists.txt`,
   `REUSE.toml`, the CI workflow, the Apache licence and `scripts/ci.py`) are
   pinned and verified unchanged.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`, `evidence`
   and `write_scope` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff and priority never enter canonical bytes and never gate this
   package.
4. **Fail-closed admission schema.** A task-local caller-supplied-asset
   manifest has a strict schema: unknown or missing fields, duplicate JSON
   keys, nonfinite values, floats where integers are required, unsafe or
   relative paths, non-integral or out-of-range integers, an unacknowledged
   commercial term, a bad platform or version, a streaming variant, a
   non-TSM scope and hash mismatches are rejected. One synthetic structural
   control is accepted to prove the validator is not blanket-rejecting; it is
   labelled `synthetic_structure_only_manifest`, has
   `qualification_effect=none`, and hashes package files only.
5. **Rate profile accounting.** Source/output mapping, duration, pitch,
   transient audibility, playback buffering, 1× and rate changes, unfamiliar
   speech, music, silence, rebuffer, drift, the final partial window, source
   timestamps and speech preservation are each recorded as **blocked** or
   **not measured**. The synthetic control is integer rate accounting only.
6. **Adverse and missing controls.** Thirty malformed PCM and manifest cases
   are actually invoked. Missing assets, invalid values, nonfinite values,
   wrong geometry, a wrong variant, a wrong scope and unacknowledged commercial
   terms all fail closed before any processing.
7. **Boundary preservation.** Installed v0 remains 16 kHz, mono, float32, 160
   samples per frame. No SuperVP provider is installed or registered; no
   descriptor, default, ABI, shared build, CI, board or handoff change is made.

## Rate acceptance profile application

`plan/swarm/VERIFICATION.md` Rate row requires source/output mapping, duration,
pitch, transient audibility, playback buffering, 1×, rate changes, unfamiliar
speech, music, silence, rebuffer, drift, the final partial window, source
timestamp policy and speech preservation. Every item is `blocked` or
`not_measured`; `satisfied_for_qualification=[]` and
`real_engine_metrics=null`.

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No licensed engine; structural integer table only. |
| Duration and rate accuracy | blocked | No engine output, clock or measurement. |
| Pitch preservation | not measured | No audio, engine or pitch analysis. |
| Transient audibility | not measured | No audio, engine or listening. |
| Playback buffering | blocked | No runtime, queue, device clock or first-output measurement. |
| 1×, rate changes, unfamiliar speech, music, silence | blocked | No rights-cleared stratum or engine. |
| Rebuffer, drift, final partial window | blocked | Structural accumulator only; no rebuffer or device result. |
| Source timestamp pause/filler policy | blocked | No policy runtime or source-timestamp replay. |
| Speech preservation | not measured | No reference transcript, scorer or listening panel. |

## Geometry and scope mismatch recorded, not resolved

No licensed API description establishes SuperVP's sample rate, channels, hop,
latency, rate semantics, streaming support, reset/flush behaviour or final
partial-window policy. This package records
`supervp_geometry_status=unestablished`, asserts no SuperVP geometry, and does
not present the candidate as a ready streaming actuator. The task scope is
`time_scale_modification_actuator`; voice conversion, synthesis, denoising,
AEC and spatial processing are out of scope.

The synthetic control runs only at the public SDK v0 boundary (16 kHz, mono,
float32, 160 samples) and computes exact integer sample counts for 0.75×, 1×,
1.25× and 1.5×, a chunked accumulator and a final partial window. It is not
SuperVP output, not TSM, not real audio and not a quality or timing result.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every file path is absolute and present, every directory path is absolute and
present, every declared SHA-256 matches, the vendor version and platform are
well formed, the commercial terms are acknowledged, channels are in `[1, 8]`,
input and output rates are integers in `[8000, 192000]`, the rate range is in
integer basis points within `[2500, 40000]` with `min <= max`, `scope` is
`time_scale_modification_actuator`, and `variant` is `offline_whole_clip`.
Streaming and rate-automation variants are rejected. Validation hashes the
caller's files but never imports or executes the vendor engine.

Because no public source or licensable revision is recorded, the contract sets
`required_source_revision=null` and `revision_pin_available=false`. The
validator enforces the version shape but cannot compare it to a known vendor
build; the vendor-identity gate remains blocked until an exact build is
supplied.

## Blocker map

| Blocker | Artifact | Gates | State |
| --- | --- | --- | --- |
| `BLK-01` | `ART-01` | `RG-01` | open: licensed vendor engine absent |
| `BLK-02` | `ART-01` | `RG-01` | open: version/build identity unpinned |
| `BLK-03` | `ART-02` | `RG-03` | open: commercial terms unresolved |
| `BLK-04` | `ART-03` | `RG-02` | open: runtime/platform absent |
| `BLK-05` | `ART-04` | `RG-06` | open: API and geometry unverified |
| `BLK-06` | `ART-05` | `RG-05` | open: rate cohort absent |
| `BLK-07` | `ART-06` | `RG-04` | open: parity vector absent |
| `BLK-08` | `ART-07`, `ART-08` | `RG-07`, `RG-08` | open: scoring, intake, default and release absent |

## Remaining gates (eight blocked)

1. `RG-01` exact licensed vendor engine, version, build, platform and per-file
   SHA-256.
2. `RG-02` isolated runtime, lock and offline platform admission.
3. `RG-03` commercial agreement, redistribution, output use, attribution,
   price and indemnity.
4. `RG-04` exact-runtime parity on a frozen caller-supplied rate vector.
5. `RG-05` rights-cleared rate cohort and separate rate/quality outcomes.
6. `RG-06` TSM scope, rate semantics and complete geometry.
7. `RG-07` opt-in external-adapter intake, licence review and independent
   public-surface decision.
8. `RG-08` default decision, resource/deadline evidence and release or
   public-benchmark approval.

**Reopen condition.** Obtain a signed IRCAM agreement covering commercial
embedding, redistribution, output use, attribution and indemnity; supply the
exact licensed SDK or host runtime at a pinned version and build with per-file
SHA-256 and reviewed terms; admit a locked offline runtime and platform; supply
the licensed API/geometry reference; reproduce an approved exact-runtime parity
vector; qualify a rights-cleared rate cohort across 1×, rate changes,
unfamiliar speech, music, silence, rebuffer, drift and the final partial window;
measure target timing; and complete opt-in external-adapter intake and
independent exact-head review. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. No IRCAM licence text, binary,
SDK header, patch, model or media file is copied.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-IRCAM-SUPERVP/docs/task-evidence/ircam-supervp
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-IRCAM-SUPERVP diff --check
```

`run.py` writes `contract.json`, canonical `report.json`, `report.json.sha256`,
the README artifact table and `SOURCES.sha256` three times and requires all
three cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift,
out-of-scope change, missing sidecar, missing SPDX header, stale README digest or
absent blocker. It also resolves the newest merge-base against `origin/main`
(falling back to `main`), emits `scope_base_unavailable` rather than passing
silently when no base exists, and fails closed with `base_out_of_scope_change`
for any committed path outside this task directory.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py`, by the README digest-table check and by the test
suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `b7bc3cfae6e82423d7be8767c2689dac4c232c929f93496e7bdfbb260a18e995` | 1818 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `4f6c6b886086d9c118e4e46979593e5da5b29d8fde138f752d25efd3736c62fa` | 20145 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `6a755a1e605645b55b013e0ba7e7ff63eaff223c9b799ab231171c0f3261f845` | 79070 |
| `report.json` | `5574e17be5bc5fbbaf9cf79a558e58d4a73382602c7d692d83d2a461eec0570c` | 47483 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `dcf75dd8fddfd8def2028af7480a368d29063f50bc4d8ef7862348e2e3369b83` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `17735fdc7175c7e4d7e5f5337344e0443e57c7a6af84531f855827ab50fe6955` | 6068 |
| `test_reference.py` | `6ec753d5fcc188617c0f3a6919c578b77861186f4d0791ec54903153ddc5a66f` | 21801 |
| `verify.py` | `60140296b423bedac646e5a9dc9b7e650668af28bfb60af05a05bea024895bd4` | 31675 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Non-claims

No IRCAM SuperVP source, SDK, binary, runtime, licence, commercial term, price,
rate cohort, reference, parity vector, TSM output, pitch, transient, buffering,
latency, memory, RTF, device timing, listening, public benchmark or release
result is claimed. Missing evidence never qualifies this candidate.
