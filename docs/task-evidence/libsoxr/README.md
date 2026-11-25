<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-LIBSOXR — task-local rate evidence (DEFER, blocker package)

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, synthetic probe evidence for the libsoxr feasibility row. It is
**not libsoxr**: no upstream source, header, binary, notice bundle, weights,
licensed runtime, real corpus, device measurement, listening result,
benchmark or release claim is present. No result here qualifies libsoxr.

## Exact blocker: upstream libsoxr is absent

The task requires the exact licensed source/runtime for libsoxr. It is **not
present in the workspace**, and nothing was fabricated or downloaded:

| Item | Status |
| --- | --- |
| Upstream artifact | libsoxr source tree at an exact pinned revision |
| Required files | `include/soxr.h` (or generated `src/soxr.h`), `src/soxr.c`, `src/rate.c`, the revision's FFT sources such as `src/fft4g64.c`, `CMakeLists.txt`, `LICENCE` |
| Expected licence | **LGPL-2.1-or-later**, to be verified against the exact files |
| Pinned revision | **none** (no commit, tag, tree or file digest exists) |
| Source digest | **none** |
| Workspace search | `third_party/` holds only `speexdsp`; `deps/lock.json` pins only SpeexDSP 1.2.1; no `soxr.h`, `src/soxr.c`, FFT source or archive exists anywhere; no CMake, lock, registry or descriptor reference |
| Rights requirement | exact LGPL-2.1-or-later text, upstream notices, a dynamic/static linking decision and relink/source-offer obligations, plus an exact revision/digest and rights review before any wrapper, build or comparison |

The machine-readable record is `report.json` → `upstream_blocker`
(`status="blocked_upstream_absent"`, `pinned_revision=null`,
`source_digest=null`, `no_upstream_parity_claim=true`). `contract.json` carries
the same blocker and all eight blocked release gates.

Because that artifact is missing, **no result qualifies libsoxr**, no provider
is registered, and release gate `RG-01` stays blocked. The reference below is a
documented stand-in that exercises the SDK `rate` acceptance profile; it is not
upstream parity and must not be read as libsoxr performance or quality.

## Exact scope

- Work is confined to `docs/task-evidence/libsoxr/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  variable-rate actuator is installed or registered. The 24 conversion cases,
  transient/tone probes and the caller-clock FIFO are task-local fixtures only.
- There is no C provider, no installed target and no public API/ABI change. The
  package has no provider manifest by design: libsoxr is unavailable, so there
  is nothing truthful to wrap or register.
- Missing, invalid, nonfinite, out-of-range, inexact-rational and
  missing-stimulus cases fail closed with no metrics. No missing result
  qualifies a candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner and history
  never enter canonical bytes and are never a gate.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure, geometry, results and reproduction guide. |
| `reference.py` | Stdlib-only deterministic windowed-sinc converter, synthetic fixtures, metrics and canonical report model. |
| `run.py` | `--report`, `--sources`, `--contract`, `--stdout-report` generator. |
| `verify.py` | Strict read-only verifier: strict JSON, pins, semantics, byte reproduction, three cold starts, licensing, absent upstream and git scope. |
| `test_reference.py` | Deterministic standard-library acceptance suite. |
| `check_licensing.py` | Local SPDX/REUSE checks; rejects a fabricated upstream licence sidecar. |
| `contract.json` | Frozen task contract, pins, blocker and eight blocked gates. |
| `report.json` | Canonical machine-readable synthetic evidence. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |
| `SOURCES.sha256` | Curated pins for context sources, boundary headers, package artifacts and the report. |
| `LICENSE` | Apache-2.0 sidecar for this directory. |
| `THIRD_PARTY_NOTICES.md` | libsoxr absence and LGPL-2.1-or-later rights pointer. |

## Pinned sources and boundary

Paths prefixed `source:` are relative to
`/Users/htsakanyan/workspace/audio/audioml`; all other paths are relative to
this SDK worktree. Exact digests are in `SOURCES.sha256` and `contract.json`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Candidate context: libsoxr is a varispeed-only cheap fallback if pitch shift is acceptable; LGPL obligations noted. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Component provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `rate` acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Inventory record: `evidence_status=considered`, `verification_profile=rate`. |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format and mapping. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public boundary pin, read-only. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public boundary pin, read-only. |

Claim base: `a91a45e32428df353dbf55a7a9fd2ec052760539`.
Branch: `swarm/SDK-LIBSOXR`. Stable board projection digest:
`094d9ccd97800ee817fd70c87ecae20b81d05a1a8533c433445d33b44fee9b0f`.

## What the reference actually does

`reference.py` implements a Blackman-windowed sinc converter with 12 taps per
side and exact rational geometry:

- The output count is `round_half_up(source_samples * up / down)` using integer
  arithmetic.
- Output sample `k` maps to source position `k * down / up` using integer
  `divmod`; no floating output clock is accumulated.
- Edge samples use zero padding and are excluded from the valid region; the
  excluded counts are reported per case.
- The kernel is DC-normalised by the full weight sum, so silence stays exactly
  zero.
- A 1:1 ratio takes an explicit identity fast path and copies samples
  bit-exactly.
- Two call paths (cached polyphase table and direct Fraction positions) must
  agree bit-exactly; that is the crosscheck.

**Sample-rate conversion is not time stretching.** At ratio `r` the tone
frequency in Hz is preserved at the converter's own output rate. If that output
is played at the input rate, speed and pitch both scale by `1/r` (varispeed).
Those playback cases are recorded as **adverse controls**, not supported modes.
The pinned candidate note already labels libsoxr a cheap fallback only if pitch
shift is acceptable.

## Rate profile application

`VERIFICATION.md` requires source/output mapping, duration, pitch, transient
audibility and playback buffering with 1×, rate changes, unfamiliar speech,
music, silence, rebuffer, drift and the final partial window. This package maps
each item to a **synthetic proxy**:

| Profile item | Local synthetic evidence |
| --- | --- |
| Source/output mapping | Exact floor source maps on 24 cases; maps monotonic; half-open intervals partition `[0, n)`; edge exclusions reported. |
| Duration | Exact integer length on all 24 cases at ratios `0.5, 0.75, 1.0, 1.25, 1.5, 2.0`. |
| Pitch | 220 Hz tone reads 220 Hz at 8/16/32 kHz output; identity 1.0, decimate 0.5× and interpolate 2.0× are varispeed adverse controls. Goertzel proxy, not listening. |
| Transient audibility | Synthetic impulse train; peak timing error is 0 output samples on every ratio. Peak retention is 0.50 at 0.5×, 0.75 at 0.75× and 1.0 at ≥1×; this is the declared cutoff/DC-normalisation response, not a listening result. |
| Playback buffering | Caller-clock 160-sample FIFO with 480-sample prefill and a four-frame source gap: 9600 samples played, 1 underrun tick, 0 overflow ticks, 0 skipped samples. Synthetic accounting, not device playout. |
| 1× / rate changes | Bit-exact 1× identity; piecewise 1.0 → 1.03 → 0.97 segments on exact grids (6000 + 6180 + 5820 = 18000). No smooth `soxr_set_io_ratio` behaviour is claimed. |
| Unfamiliar speech | Seeded speech-like harmonic spans with pauses and a filler; source-anchored voiced/pause RMS contrast 46.28 dB. Proxy only, not intelligibility. |
| Music | Deterministic chord/click surrogate; a negative control, never a quality claim. |
| Silence | Exact zero output on every ratio. |
| Rebuffer | Source gap, refill and resume with every sample played and no skip. |
| Drift | 20,600-output 1.03× control; reference position error 0 samples, naive float accumulator error 3e-09 samples. No device clock. |
| Final partial window | 12,737 source samples at 1.25× → exactly 15,921 outputs, 15,893 valid after 14/14 edge exclusions, final 53-sample partial frame. |
| Speech preservation | Voiced/pause RMS contrast > 10 dB; not WER, MOS or comprehension. |

Full values, digests, adverse observations and gate reasons are in
`report.json`. Source-reported numbers from the pinned notes are **not**
imported as results.

## Exact recorded results

| Signal | Source samples | Ratios | Output lengths | 1× identity | Silence |
| --- | --- | --- | --- | --- | --- |
| `tonal_220hz` | 4,800 | 0.5–2.0 | 2,400 / 3,600 / 4,800 / 6,000 / 7,200 / 9,600 | bit-exact | n/a |
| `speech_like` | 9,600 | 0.5–2.0 | 4,800 / 7,200 / 9,600 / 12,000 / 14,400 / 19,200 | bit-exact | n/a |
| `music_like` | 6,400 | 0.5–2.0 | 3,200 / 4,800 / 6,400 / 8,000 / 9,600 / 12,800 | bit-exact | n/a |
| `silence` | 1,600 | 0.5–2.0 | 800 / 1,200 / 1,600 / 2,000 / 2,400 / 3,200 | bit-exact | exact zero |

Spectral proxies (Goertzel, not listening):

| Check | Filtered reference | Adverse control |
| --- | --- | --- |
| 6 kHz → 8 kHz alias at 2 kHz | `-74.22 dB` | nearest-sample decimation `0.00 dB` |
| 6 kHz → 32 kHz image at 10 kHz | `-74.06 dB` | linear interpolation `-10.21 dB` |

Adverse controls (all fail closed, no metrics): 18 invalid
configuration/input cases (zero, negative, too-large, NaN/inf, string/bool
ratios, nonfinite/out-of-range/bool/string/nested/empty samples, unknown config
keys, wrong rate/frame), 5 strict-JSON cases (duplicate key, NaN, Infinity,
root array, trailing text) and a blocked missing-stimulus result. The reference
also scans every output for nonfinite values.

## Exact digests

| Artifact | SHA-256 |
| --- | --- |
| `report.json` | `a749dd98c489db72f5ae1f932fc9bbfa102e18fc7c1d4b2e34b8d20d186fc3ba` |
| `report.json` canonical text | `f67da45e2177e17eaaad220d4d43b7bf11adabacfe119748fc9f12fcf77ac028` |
| `reference.py` | `bd46a8101b64c69b8a099299cadfb5c49d72e313c8ecc3e46a834f4649e65b65` |
| `run.py` | `dd8b31a7456c102f254aeb2e6ec8f08068afb0afa1d81ba97d959ed7ef2e1d3d` |
| `verify.py` | `a76ac79aa14716cc69e021eedcc0687cf35fb7358f372b824f0fbc725f6bdd3f` |
| `test_reference.py` | `11a7a66a93df848e17477948eda05dcc7cd6d52daf177aecd484e7f7222b4f7a` |
| `check_licensing.py` | `f642fc61cafb49f7a4b8a407d90488016a73ca54c4dd7c2ffa584981bc741478` |

`contract.json` is generated last and pins every artifact except itself.

## Reproduction

All commands run from this directory with Python 3 and the standard library
only. No build output, download or cache is written outside it.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LIBSOXR/docs/task-evidence/libsoxr

PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --contract
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
python3 -m json.tool report.json >/dev/null
shasum -a 256 report.json
git -C ../../.. diff --check
```

Expected: the report digest above, all tests pass, `verify.py` prints
`pins_ok=... reproduction_ok=1 repeats_ok=3 ...`, licensing passes and the diff
check is clean. Three cold-start interpreters must reproduce `report.json`
byte-for-byte; `verify.py` enforces this by launching `run.py --stdout-report`.
Regenerating in the order `--report`, `--sources`, `--contract` keeps the
self-referential pins consistent.

## Licensing

Every new Python and Markdown file carries an explicit SPDX header. The
repository's `REUSE.toml` already annotates `docs/**` as aggregate Apache-2.0,
and `LICENSES/Apache-2.0.txt` is present. No upstream LGPL licence text is
included, because no upstream artifact exists; `check_licensing.py` fails if a
fabricated `COPYING`/`LGPL-2.1.txt` sidecar appears. `THIRD_PARTY_NOTICES.md`
records the expected LGPL-2.1-or-later disposition and the rights review that
must precede any use.

## Remaining release gates (all blocked)

1. `RG-01 upstream_source_and_revision_pin` — exact libsoxr source and
   revision/digest.
2. `RG-02 upstream_license_and_notice_review` — LGPL-2.1-or-later text,
   notices, linking/relink decision and rights review.
3. `RG-03 exact_build_and_install_parity` — build/install the pinned revision
   and compare it.
4. `RG-04 exact_api_delay_drain_and_variable_rate_parity` — `soxr_create`,
   `soxr_process`, `soxr_delay`, `soxr_clear` and `soxr_set_io_ratio`
   semantics mapped to v0 content mapping.
5. `RG-05 rights_qualified_rate_cohort` — permitted real speech/music cohort.
6. `RG-06 independent_listening_and_transient_audibility` — blind listening
   with a frozen score sheet.
7. `RG-07 target_runtime_timing_and_memory` — device fill/flush, deadline, CPU
   and memory measurement.
8. `RG-08 provider_intake_public_surface_and_release` — provider intake,
   public-surface decision, independent exact-head review and release approval.

**Exact blocker for any libsoxr qualification:** a rights-qualified,
task-matched real speech/music cohort on a locked host, with independent
clock/drift telemetry, authorized listening, an installed pinned libsoxr
build and its LGPL-2.1-or-later compliance review. None of those artifacts is
present in this workspace, so this package cannot qualify the component. It
deliberately records `DEFER`, `incomplete` and `not_qualified` rather than
inventing them.

## Non-claims

No public API/ABI, installed v0, descriptor, registry, default, shared build,
CI or board/handoff change. No provider registration. No real corpus, model,
weight, download, device timing, listening result, benchmark, publication or
release qualification. No libsoxr parity or performance claim. No
pitch-preserving time-stretch claim. No missing result qualifies a candidate.
