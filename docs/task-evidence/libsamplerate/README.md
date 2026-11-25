<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LIBSAMPLERATE — task-local sample-rate conversion evidence (DEFER)

This directory contains **proposal-only, incomplete, not-qualified** evidence
for a deterministic sample-rate conversion reference at a protocol-shaped
adapter boundary. It is **not libsamplerate**: no upstream source, header,
binary, notice bundle, weights, licensed runtime, real corpus, device
measurement, listening result or release claim is present. Decision: **DEFER**;
status `proposal_only_not_qualified`; readiness `incomplete`; qualification
`not_qualified`.

## Exact blocker: upstream libsamplerate is absent

The task requires the exact licensed source/runtime for libsamplerate. It is
**not present in the workspace**, and nothing was fabricated or downloaded:

| Item | Status |
| --- | --- |
| Upstream artifact | `erikd/libsamplerate` source tree at an exact revision |
| Required files | `include/samplerate.h`, `src/samplerate.c`, `src/src_sinc.c`, `src/common.h`, `CMakeLists.txt` or `configure.ac`, `COPYING` |
| Expected license | BSD-2-Clause plus upstream copyright notices |
| Pinned revision | **none** (no commit, tag, tree or file digest exists) |
| Source digest | **none** |
| Workspace search | `third_party/` holds only `speexdsp`; `deps/lock.json` pins only SpeexDSP 1.2.1; no `samplerate.h`, `src_sinc.c` or archive exists anywhere; no CMake, lock, registry or descriptor reference |
| Rights requirement | BSD-2-Clause text, upstream notices, exact revision/digest and a completed rights review before any wrapper, build or comparison |

The machine-readable record is `report.json` → `upstream_blocker`
(`status="blocked_upstream_absent"`, `pinned_revision=null`,
`source_digest=null`, `no_upstream_parity_claim=true`).

Because that artifact is missing, **no result in this package qualifies
libsamplerate**, no provider is registered, and release gate `RG-01` stays
blocked. The reference below is a documented stand-in that exercises the rate
acceptance profile; it is not upstream parity.

## Exact scope

- Work is confined to `docs/task-evidence/libsamplerate/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behavior, board/handoff files, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  variable-rate actuator is installed; 24 synthetic conversion cases plus a
  caller-clock pacing trace are task-local fixtures only.
- `adapter.json` and `provider.json` describe an **unregistered, default-OFF,
  opt-in** developer boundary. There is no C provider, no installed target, no
  descriptor registration and no public API/ABI change. With the provider
  switch OFF the adapter is bit-exact identity.
- No missing result qualifies a candidate. Invalid, nonfinite, out-of-range,
  inexact-rational and missing-stimulus cases fail closed with no metrics.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`); mutable status, owner and history never enter canonical
  bytes and are never a gate.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure and reproduction guide. |
| `SOURCES.sha256` | SHA-256 pins for external sources, public headers, implementation, manifests and report. |
| `contract.json` | Task contract, rate profile, pins, upstream blocker and release gates. |
| `adapter.json` | Unregistered, default-OFF protocol-v1 conversion adapter manifest. |
| `provider.json` | Conceptual opt-in provider manifest; no C provider is built or registered. |
| `reference.py` | Deterministic windowed-sinc converter on an exact rational output grid, fixture generators and report model. |
| `scorer.py` | Dependency-free duration, mapping, Goertzel, alias/image, transient, envelope and FIFO metrics. |
| `fixture.py` | Read-only canonical report, frozen fixture digests and cold-start probe. |
| `run.py` | Adapter prototype, report/sidecar generator, source-pin generator and renderer crosscheck. |
| `verify.py` | Strict read-only verifier for pins, JSON, semantics, byte reproduction, licensing and git scope. |
| `check_licensing.py` | Local SPDX/REUSE checks with split identifier literals; rejects a fabricated upstream license sidecar. |
| `test_reference.py` | 70 deterministic standard-library unit tests. |
| `report.json` | Canonical synthetic evidence report. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |

## Source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` for
`source:` rows and to the SDK worktree for header rows. Exact digests are in
`SOURCES.sha256` and reproduced in `contract.json`.

| Source | Use |
| --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | Candidate context: libsamplerate is listed as a varispeed/resampling cheap fallback "if pitch shift is acceptable". |
| `REALTIME_COMPONENT_CANDIDATES.md` | Component-candidate provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `rate` acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | Inventory record: `evidence_status=considered`, `verification_profile=rate`. |
| `CONTRACTS.md`, `api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h` | Public boundary pins, read-only. |

Claim base: `8defcae2b153b52668c93791463497ea261b7fb1`.

## What the reference actually does

`reference.py` implements a Blackman-windowed sinc converter with 12 taps per
side and exact rational geometry:

- The output count is `round_half_up(source_samples * up / down)`.
- Output sample `k` maps to source position `k * down / up` using integer
  `divmod`, so no floating output clock is accumulated.
- Edge samples use zero padding and are excluded from the valid region; the
  excluded counts are reported per case.
- The kernel is DC-normalised by the full weight sum; silence stays exactly
  zero.
- A 1:1 ratio takes an explicit identity fast path and copies samples
  bit-exactly.
- Two call paths (cached polyphase table and direct Fraction positions) must
  agree bit-exactly; that is the crosscheck.

**Sample-rate conversion is not time stretching.** At ratio `r` the tone
frequency in Hz is preserved at the converter's own output rate. If that output
is played at the input rate, speed and pitch both scale by `1/r` (varispeed).
Those playback cases are recorded as **adverse controls** and excluded from
qualification; the pinned candidate note already says libsamplerate is a cheap
fallback only if pitch shift is acceptable.

## Rate profile application

`VERIFICATION.md` requires source/output mapping, duration, pitch, transient
audibility and playback buffering with 1×, rate changes, unfamiliar speech,
music, silence, rebuffer, drift and the final partial window. This package maps
each item to a **synthetic proxy**:

- **Source/output mapping** — every output sample carries a floor source index;
  maps are monotonic and the half-open source intervals partition `[0, n)` for
  all 24 cases. Edge exclusions are explicit.
- **Duration** — 24 cases at ratios `0.5, 0.75, 1.0, 1.25, 1.5, 2.0` over four
  signals; every observed length equals the exact rounded expectation.
- **Pitch proxy** — a 220 Hz analytic tone reads 220 Hz at output rates
  8/16/32 kHz (Goertzel grid, not listening). The varispeed adverse control
  reads exactly `0.5×` and `2.0×` when converted audio is played at 16 kHz.
- **Transient audibility** — adjacent local peaks on a synthetic impulse train
  at four source positions; timing error is at most 1 output sample for every
  ratio and peak retention stays inside `0.80–1.08`.
- **Anti-alias / imaging** — a 6 kHz tone decimated to 8 kHz folds to 2 kHz:
  the filtered path measures `-74.22 dB` relative to the passband while
  unfiltered nearest-sample decimation measures `+0.001 dB`. Interpolating the
  same tone to 32 kHz puts the image at 10 kHz: filtered `-74.06 dB` versus
  linear-interpolation `-10.21 dB`.
- **Playback buffering** — a caller-owned FIFO with a 480-sample prefill and a
  four-tick source gap records a stall, refill burst and resume with one
  underrun tick and no overflow. This is synthetic sample accounting, not
  device playout.
- **Unfamiliar speech / speech preservation** — seeded noise plus analytic
  harmonics with explicit voiced/pause/filler spans; source-anchored RMS span
  ratios read `0.9998` for all four voiced spans at 1.25×. Not WER, MOS or
  comprehension.
- **Music** — a synthetic tone/click surrogate is a **negative control** and
  never qualifies the candidate.
- **Pause/filler decisions** — spans are source-sample intervals; nothing is
  inferred from output time.
- **Drift** — two 1.03× segments are each converted on their own exact grid.
  A naive float accumulator over 40,000 outputs accrues `2e-08` samples of
  position error; the reference reports exactly zero.
- **Final partial window** — 12,737 source samples at 1.25× produce 15,921
  outputs, 15,893 valid after edge exclusions, and a final 81-sample partial
  frame. Output digest and nonfinite count are recorded.

Full values, digests, adverse observations and gate reasons are in
`report.json`. Source-reported numbers from the pinned notes are **not**
imported as results.

## Failure controls and adverse cases

- Configuration: zero, nonfinite, out-of-bounds and non-rational ratios, wrong
  sample rate, wrong frame size and unknown keys are rejected before any
  converter is created.
- Input: nonfinite, out-of-range (`|x| > 4.0`), boolean, string, nested and
  empty vectors are rejected with no output metrics.
- Protocol: boolean/string/float/wrong-integer `protocol_version`, non-boolean
  provider switch, unknown stimulus, missing stimulus, non-list-exceeding
  sample payloads, malformed refs, non-string attempt IDs, duplicate JSON keys
  and `NaN`/`Infinity` JSON constants are rejected before any result is written.
- Varispeed playback, unfiltered decimation, linear interpolation and the naive
  float clock are adverse controls, each marked
  `excluded_from_qualification`.
- A missing named stimulus is blocked with `metrics: null`; no default success
  is synthesized.

No gate was weakened to obtain a pass. No listening, device-timing, resource or
release result is hidden in the report.

## Reproduction

From this directory, with Python 3.11.5 and the standard library only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

Three cold-start interpreter probes must reproduce `report.json` byte-for-byte;
`verify.py` regenerates the canonical bytes in memory and compares them.

The adapter can also be exercised without writing evidence:

```sh
python3 run.py --request request.json --result result.json
```

A request carries integer `protocol_version` `1`, `operation` (`inspect` or
`run`), `candidate_ref`, `adapter_ref`, `configuration`, and for `run` also
`attempt_id`, `ratio` and numeric `samples`. Results are canonical JSON with a
trailing newline and a synthetic-only disclosure.

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-LIBSAMPLERATE
git diff --check
git diff --cached --check
python3 -m reuse lint
```

## Licensing

Every new Python and Markdown file carries an explicit SPDX header. No Python
body embeds a full identifier token as a string; checks use split string
literals. The repository's `REUSE.toml` already annotates `docs/**` as
aggregate Apache-2.0, and `LICENSES/Apache-2.0.txt` is present. No upstream
BSD-2-Clause license file is included, because no upstream artifact exists;
`check_licensing.py` fails if one appears.

## Remaining release gates

All eight are **blocked**; none is satisfied by this package:

1. `RG-01 upstream_source_and_revision_pin` — exact libsamplerate source and
   revision/digest.
2. `RG-02 upstream_license_and_notice_review` — BSD-2-Clause text, notices and
   rights review.
3. `RG-03 exact_build_and_install_parity` — build/install the pinned revision
   and compare it.
4. `RG-04 exact_api_delay_and_drain_parity` — `SRC_STATE` latency,
   `end_of_input`, ratio-change and reset semantics mapped to v0 content
   mapping.
5. `RG-05 rights_qualified_rate_cohort` — permitted real speech/music cohort.
6. `RG-06 independent_listening_and_transient_audibility` — blind listening
   with a frozen score sheet.
7. `RG-07 target_runtime_timing_and_memory` — device fill/flush, deadline, CPU
   and memory measurement.
8. `RG-08 provider_intake_public_surface_and_release` — provider intake,
   public-surface decision, independent exact-head review and release approval.

## Final digests

- `report.json` SHA-256: `c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc`
- Canonical report digest: `a7fb2c8e23fc826a2be8ab1499311030fbaeb3fa9b830c7650c90454245ac21f`
- Frozen synthetic fixture digest: `d159c2bf0c0d88a7165df1dba1c8901772e0a275276d7571917bbf72b0def907`
- Board link identity projection: `53cfb69425d0a88526dfbba70e3742ba0ae2c6ed14818ee3f04cc2028025ce11`
- Base commit: `8defcae2b153b52668c93791463497ea261b7fb1`
- Branch: `swarm/SDK-LIBSAMPLERATE`
