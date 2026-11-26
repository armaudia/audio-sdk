<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LIVEKIT-PYTHON-HOST-ADAPTER — LiveKit Python host-adapter readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the LiveKit
Python host adapter row. It is **not** a LiveKit integration. No LiveKit host
package, wheel, sdist, lock file, install tree, room, token, participant,
media, real audio, host geometry, conversion, pacing, cancellation, drain,
device timing, listening result, benchmark or release claim is present. **No
result here qualifies the LiveKit host adapter.**

This package records the **LiveKit Python host adapter** readiness conclusion.

The structured inventory marks `livekit-python-host-adapter` as
`evidence_status=considered`, disposition `sdk-tool`, with the **Tool**
acceptance profile (`verification_profile: tool`, `plan/INVENTORY.json`). The
task is a feasibility investigation: verify runnable source, exact assets,
permitted scope, host-adapter geometry and matched evidence, then either model
a caller-supplied host-adapter contract or record a strict readiness
conclusion with the exact external blocker and reopen condition. None of the
runtime prerequisites exists.

Pinned base: `b02dbf12499038abc4f9b6b1c06cdecc76a79dcd`.
Branch: `swarm/SDK-LIVEKIT-PYTHON-HOST-ADAPTER`. Owner:
`agent-LIVEKIT-PYTHON-HOST-ADAPTER`. Reviewer:
`reviewer-LIVEKIT-PYTHON-HOST-ADAPTER`.

## Exact external blocker

The pinned acceptance matrix already records the blocker:

> `| S09 LiveKit host | Blocked / excluded | No pinned/tested LiveKit host
> package pair; no claim |`
>
> `| S-T11 LiveKit | Excluded | S09 blocked |`

The pinned matrix records **No pinned/tested LiveKit host package pair** as the
S09 blocker. No pinned or tested LiveKit host package pair is present in this
workspace or in the pinned CPython 3.12.16 environment. `importlib.util.find_spec` reports
no `livekit`, `livekit.agents`, `livekit.rtc` or `audio_sdk` module. No host
wheel, sdist, lock file, install tree, per-file SHA-256, host API record or
host geometry record exists. Package installs and downloads are prohibited in
this task, so no pin can be created by this execution.

The second blocker is the SDK side: no installed `audio-sdk` Python wheel or
matching native library exists at the pinned base in this worktree, and
`AUDIO_SDK_LIBRARY` is unset. The Python binding cannot be imported without an
explicit library path and contract version 0.1 identity.

The third blocker is rights and media: no rights-cleared participant media,
room/token scope, output-use grant or redistribution grant is present. Real
audio is prohibited in this task.

The fourth blocker is evidence: no 10 ms host pacing run, conversion record,
participant reset, cancellation, queue-full, stale-epoch, abrupt-close or
managed drain/close record exists. The Tool profile therefore cannot be
satisfied.

Nothing was fabricated, reconstructed, installed, downloaded, mirrored,
imported, executed or substituted. No LiveKit revision, package version,
wheel name, byte count, API signature, frame size, sample rate, channel count,
sample format or SHA-256 is asserted as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Pinned host package pair | One exact LiveKit Python host package pair at immutable versions, with wheel/sdist platform artifacts, per-file SHA-256 and a lock file |
| Installed SDK binding | The `audio-sdk` Python wheel and matching native library built from an exact commit, contract 0.1 and a recorded build ID |
| Host API and geometry | A pinned LiveKit API record fixing frame size, sample rate, channel count, sample format, pacing, reset and close behaviour |
| Rights-cleared audio | Participant media and room/token scope with output-use and redistribution terms, stored outside the package |
| Conversion and capture | One typical host API use verifying s16-to-f32 conversion, exact resampling/rechunking, source order and the explicit 30 ms host shift plus D |
| Lifecycle evidence | Participant reset, cancellation with pending work, expected output unavailable, queue full, malformed format, stale epoch, abrupt close and managed drain/close |
| Tool evidence | Clean package, version/install location/provenance, caller-owned inputs, malformed inputs, missing optional selections and measured workload support |
| Independent review | Exact-head independent review, default decision and release or public-benchmark approval |

The machine-readable record is `report.json` → `host_source`,
`source_reported_context`, `acceptance_matrix_evidence`, `geometry`,
`tool_profile`, `asset_requirements`, `asset_audit`, `absence_probes`,
`module_absence`, `caller_asset_contract`, `exact_blockers` and `gates`.
`contract.json` carries the same disposition, pins, geometry and all eight
blocked release gates.

## What this package verifies

1. **Absence evidence.** Twenty-one fixed workspace/worktree probes are checked;
   no recursive walk is performed and no home cache is scanned. All are absent.
   `reference.absence_probes()` and `verify.py` fail if any probe later
   appears, so a stale "absent" claim cannot be shipped.
2. **Module absence.** `importlib.util.find_spec` checks `livekit`,
   `livekit.agents`, `livekit.rtc` and `audio_sdk` in the pinned interpreter
   without importing them. All are absent. A later installation fails closed
   and requires reopening the blocker.
3. **Stable pins.** The inventory, Tool acceptance profile, acceptance matrix,
   SDK test plan, SDK Python binding, Python project metadata, SDK provider
   tests and public v0 boundary files are pinned by SHA-256. These are
   read-only provenance inputs, not host evidence.
4. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`, `evidence`
   and `write_scope` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never** hashed; status, owner, claim,
   review, handoff and priority never enter canonical bytes and never gate this
   package.
5. **Fail-closed admission schema.** A task-local caller-supplied host-adapter
   manifest has a strict schema: unknown or missing fields, duplicate JSON
   keys, nonfinite values, floats where integers are required, unsafe or
   relative paths, non-integral or out-of-range integers, a wrong Python
   version, a bad host version or platform, a wrong scope or variant, a wrong
   host shift, a non-10-ms frame, a non-integer decimation ratio, a wrong SDK
   contract version, a provider/delay mismatch, an unacknowledged rights term
   and hash mismatches are rejected. One synthetic structural control is
   accepted to prove the validator is not blanket-rejecting; it is labelled
   `synthetic_structure_only_manifest`, has `qualification_effect=none`, and
   hashes package files only.
6. **Tool profile accounting.** Version/install location/provenance, clean
   package, typical CLI/API use, caller-owned inputs, malformed inputs, missing
   optional selections, build/synthetic/measured separation and measured
   workload support are each recorded as **blocked**, **partial synthetic** or
   **not measured**. The synthetic control is structural only.
7. **Adverse and missing controls.** Thirty-nine malformed PCM, geometry and
   manifest cases are actually invoked. Missing assets, invalid values,
   nonfinite values, wrong geometry, a wrong variant, a wrong scope, a wrong
   Python version, a provider/delay mismatch and unacknowledged rights all fail
   closed before any processing.
8. **Boundary preservation.** Installed v0 remains 16 kHz, mono, float32, 160
   samples per frame. No LiveKit provider or adapter package is installed,
   registered or exposed; no descriptor, default, ABI, shared build, CI, board
   or handoff change is made.

## Host-adapter geometry

The **SDK boundary** is source-verified from `TEST_PLAN.md` S-T11 and
`bindings/python/audio_sdk/__init__.py`: 16 kHz, mono, float32, exactly 160
samples per frame, 10 ms frame duration, synchronous `AS_MODE_PROCESSING_THREAD`
mode only, explicit 30 ms host shift plus provider delay `D`, first three SDK
frames invalid startup, wrong lengths including 161/320/800 samples rejected,
finite conversion, no event-loop wait for inference, stop on missed output or
admission, no old-epoch output, abrupt close records a cancelled tail, and
managed drain/close is bounded.

The **LiveKit host boundary** is `unestablished`. No pinned LiveKit API record
fixes its frame size, sample rate, channel count, sample format, pacing, reset
or close semantics. The package therefore asserts no LiveKit geometry. It
models a labelled **structural 48 kHz → 16 kHz 10 ms control**: 480 host s16
samples per host frame, integer decimation by 3, 160 SDK f32 samples per SDK
frame, 480 SDK samples (30 ms) of host shift, and exact packing for 1, 3, 30,
100 and 600 frames. This is arithmetic and s16 range validation only; it is
not LiveKit output, not resampling quality and not a timing result.

| Geometry item | Value here | Status |
| --- | --- | --- |
| SDK sample rate / channels / format | 16 kHz / mono / f32 | pinned source, verified |
| SDK frame | 160 samples / 10 ms | pinned source, verified |
| Host shift | 480 SDK samples / 30 ms | pinned plan model |
| Provider delays | `dsp.highpass80.v0` 0; `speex.ns.v0` 160 | pinned SDK test source |
| Wrong lengths rejected | 161, 320, 800 samples | pinned plan/control |
| LiveKit frame / rate / format | — | unestablished, not asserted |
| LiveKit pacing / reset / close | — | unestablished, not executed |

## Tool acceptance profile application

`plan/swarm/VERIFICATION.md` Tool row requires version, install location and
provenance; a clean checkout or extracted package; one typical CLI/API use;
caller-owned inputs; malformed inputs; missing optional selections; separate
compile/build, synthetic runtime and measured workload evidence; and measured
workload support. Every item is `blocked`, `partial_synthetic`,
`separated_in_package_only` or `not_measured`; `satisfied_for_qualification=[]`
and `measured_workload_result=null`.

| Tool requirement | Status here | Evidence |
| --- | --- | --- |
| Version, install location, provenance | blocked | No host package pair; no install tree. |
| Clean checkout or extracted package | blocked | No host wheel, sdist, lock or checkout. |
| Typical CLI/API use | not measured | No host package, room or participant. |
| Caller-owned inputs | blocked | No rights-cleared caller media; synthetic package files only. |
| Malformed inputs | partial synthetic | 39 adverse cases fail closed in this package, not in a host. |
| Missing optional selections | partial synthetic | Manifest rejects missing assets and directories. |
| Build/synthetic/measured separation | separated in package only | No build or measured workload exists. |
| Measured workload support | blocked | No workload, resource, deadline or device result. |

## Caller-supplied host-adapter contract

A caller manifest is accepted only when it has exactly the declared fields,
every file path is absolute and present, every directory path is absolute and
present, every declared SHA-256 matches, the host package version, Python
3.12.16, platform and SDK build ID are well formed, the SDK contract version is
`0.1`, the provider and delay agree with the pinned SDK test source, the host
sample rate is an integer multiple of 16 kHz with integer decimation, the host
frame is exactly 10 ms, the SDK geometry is 16 kHz/mono/160, the host shift is
480 samples, `scope` is `livekit_python_host_audio_adapter`, `variant` is
`caller_clocked_paced_streaming`, and rights-cleared audio is acknowledged.
Validation hashes the caller's files but never imports or executes the host
package, the SDK binding or audio.

Because no host package or API is recorded, the contract sets
`required_revision=null` (no host revision), `host_package_version` is a
caller-declared value, and the host-identity gate remains blocked until an
exact pair is supplied.

## Blocker map

| Blocker | Artifact | Gates | State |
| --- | --- | --- | --- |
| `BLK-01` | `ART-01` | `RG-01` | open: pinned host package pair absent |
| `BLK-02` | `ART-02` | `RG-02` | open: installed SDK binding absent |
| `BLK-03` | `ART-03` | `RG-03` | open: rights-cleared audio and participant scope absent |
| `BLK-04` | `ART-04` | `RG-04` | open: host API and geometry unverified |
| `BLK-05` | `ART-05` | `RG-05` | open: conversion and capture unverified |
| `BLK-06` | `ART-06` | `RG-06` | open: lifecycle and termination unverified |
| `BLK-07` | `ART-07` | `RG-07` | open: Tool profile and measured workload absent |
| `BLK-08` | `ART-08` | `RG-08` | open: review, default and release absent |

## Remaining gates (eight blocked)

1. `RG-01` exact LiveKit Python host package pair, immutable versions,
   wheel/sdist artifacts, per-file SHA-256, lock file and install tree.
2. `RG-02` installed `audio-sdk` Python binding and matching native library
   from an exact commit, contract 0.1 and recorded build ID.
3. `RG-03` rights-cleared participant media, room/token scope, output-use and
   redistribution terms.
4. `RG-04` pinned LiveKit API and geometry record for frame size, sample rate,
   channels, format, pacing, reset and close.
5. `RG-05` typical host API use, s16-to-f32 conversion, exact
   resampling/rechunking, source order and 30 ms host shift plus D.
6. `RG-06` participant reset, cancellation with pending work, expected output
   unavailable, queue full, malformed format, stale epoch, abrupt close and
   managed drain/close.
7. `RG-07` Tool profile: clean package, typical use, caller-owned inputs,
   malformed/missing selections and measured workload support.
8. `RG-08` independent exact-head review, default decision and release or
   public-benchmark approval.

**Reopen condition.** Supply one exact LiveKit Python host package pair at
immutable versions with wheel/sdist artifacts, lock file, install tree and
per-file SHA-256; install it offline into an owned Python 3.12.16 environment;
build and install the `audio-sdk` Python binding with its matching native
library from an exact commit and record contract 0.1 plus the build ID; supply
a pinned LiveKit API/geometry record and rights-cleared participant media with
room/token, output-use and redistribution scope; run one typical host API use
and the complete S-T11 matrix (10 ms pacing, 161/320/800 rejection, participant
reset, cancellation with pending work, expected output unavailable, queue full,
malformed format, source order, 30 ms host shift plus D, first three invalid
frames, finite conversion, no event-loop wait, stop on missed output/admission,
no stale-epoch output, abrupt-close cancelled tail, managed drain/close); then
record measured workload support and complete independent exact-head review.
Until then the candidate stays **DEFER**, **incomplete** and **not qualified**.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. No LiveKit licence text, wheel,
binary, source file, patch, model or media file is copied. No host licence
status is asserted.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LIVEKIT-PYTHON-HOST-ADAPTER/docs/task-evidence/livekit-python-host-adapter
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LIVEKIT-PYTHON-HOST-ADAPTER diff --check
```

`run.py` writes `contract.json`, canonical `report.json`, `report.json.sha256`,
the README artifact table and `SOURCES.sha256` three times and requires all
three cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift,
out-of-scope change, missing sidecar, missing SPDX header, stale README digest,
present absence probe or absent blocker. It also resolves the newest merge-base
against `origin/main` (falling back to `main`), emits `scope_base_unavailable`
rather than passing silently when no base exists, and fails closed with
`base_out_of_scope_change` for any committed path outside this task directory.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py`, by the README digest-table check and by the test
suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/docs/acceptance-matrix.md` | `2e5fbeee8b9a25578f0a03ca3c5291c295756de7f5d8cf9a313b53eecf7e5e1e` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
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
| `sdk:TEST_PLAN.md` | `f0508583243ab5decd6d61a6d69c50ecd878c60b32e77bbb0b080c03a11fa4e5` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:bindings/python/pyproject.toml` | `0f3b1e736dd807a984cbb9daa10cd0ba32668f7833994c3c4f0a5021799c95a4` |
| `sdk:bindings/python/tests/test_sdk.py` | `32c4cecab24b00fc3be312f64e9def05a5391b0f475cd9d461321e8fc4d4c101` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `7307ed87238e1faf71816f68285a5ffbf7a7d5e37012839007fcfbfffc21d5c9` | 1478 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `8615cb721054907646a6465bf106df806cb69bb3fbf6ed484dcac90ec6c31d01` | 25225 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `d42775414e1b799a90ebcc3075db2ced2094083fe69a9b769c6b559d2c2d4a4f` | 91291 |
| `report.json` | `c6c8c868b6f918bf5a418813fc62866cb3e8929313d2f3b278f61d5e1595cfd7` | 57303 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `9adaceeaab7a0954775a34036b3dfbc16812e2daf5a1c18abdd054c7db583183` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `4a5d34e74e3622fe49c4141e340f851ab349cec3d76f5ae53d9733f5b841f82c` | 6116 |
| `test_reference.py` | `fb50cbee9e19d31c37987ce50d2ad7672f75f25025a8a751fdfa8f88301270e3` | 28483 |
| `verify.py` | `e347a0c53e5b885375c69ccc655402c6ff8a08d2a3f4e2601e47d0b9eef8a6da` | 37122 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Non-claims

No LiveKit host package, wheel, sdist, lock file, install tree, room, token,
participant, track, device, capture, real audio, host geometry, conversion,
pacing, cancellation, drain, latency, memory, RTF, device timing, listening,
public benchmark or release result is claimed. Missing evidence never qualifies
this candidate.
