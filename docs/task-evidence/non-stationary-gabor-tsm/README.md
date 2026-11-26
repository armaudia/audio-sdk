<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NON-STATIONARY-GABOR-TSM - non-stationary Gabor TSM readiness blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory is bounded, deterministic, task-local feasibility evidence for the
non-stationary Gabor TSM row. It is **not** a non-stationary Gabor transform,
time-scale modifier, LTFAT wrapper or rate controller. No reference source,
LTFAT checkout, wheel, binary, dual window, window schedule, licence text,
runtime, audio, corpus, candidate output, listening result, device
measurement, benchmark or release claim is present. **No result here
qualifies the catalogued candidate.**

`plan/INVENTORY.json` records `non-stationary-gabor-tsm` as
`evidence_status=considered`, `disposition=sdk-reference`, area
`Rate and content`, with the **Rate** acceptance profile and task
`SDK-NON-STATIONARY-GABOR-TSM`. Its only evidence link is
`cpp-library/pipeline-validation/playback-speed-candidates.md`, section 5.9
(line 415), with the finding (diacritics transliterated to ASCII):

- Paper: Prusa and Holighaus, "Phase vocoder done right", EUSIPCO 2017.
- Idea: use a non-stationary Gabor transform with time-varying windows and a
  well-conditioned inverse, avoiding the usual phase-vocoder heuristics.
- Cost/latency: higher than a plain STFT; research-grade.
- Use: if we need a principled, high-quality spectral stretcher and have DSP
  time. Reference implementations may be copyleft (LTFAT is GPL-3.0), so
  treat them as papers, not vendored code.

That is source-reported context, not a local run. The inventory plan note is:
"Reproduce the chosen technique on exact rate ratios before a streaming API
claim."

## Exact external blocker

The exact **reference source snapshot**, the **LTFAT or equivalent runtime**,
the **exact time-varying transform geometry**, the **reviewed terms** and the
**matched rate evidence** are absent. Nothing was fabricated, reconstructed,
mirrored, downloaded or substituted. No revision, file name, byte count or
SHA-256 is asserted as verified. The paper DOI is provenance only.

| Missing artifact | Exact requirement |
| --- | --- |
| Reference source | An exact NSGT/non-stationary Gabor or LTFAT source tree at an immutable 40-hex commit or release tag, with reviewed licence text, README, window/transform definitions and a per-file SHA-256 manifest |
| Runtime | A locked offline runtime with exact package and wheel hashes, FFT and numeric dependency pins, platform, device, dtype, determinism settings and install location; or an explicit GPL-compatible isolation decision |
| Transform geometry | Sample rate, channels, frame, hop, analysis window schedule, synthesis/dual-window rule, transform length, coefficient/phase mapping, latency, reset and drain behaviour |
| Rights | Code, dependency and reference terms including the GPL-3.0 implication of LTFAT; rights-cleared speech/music input with acquisition, evaluation, derived-output and redistribution decisions |
| Matched evidence | A frozen, rights-cleared cohort with 1x control, exact constant ratios, step/ramp changes, unfamiliar speech, music, silence, rebuffer, drift, final-partial and speech-preservation measurements on the exact runtime |

The machine-readable record is `report.json` -> `source_reported_identity`,
`task_geometry`, `absence_evidence`, `rate_profile`, `matched_evidence`,
`asset_declaration`, `rate_request`, `exact_blockers`, `gates` and
`qualification`. `contract.json` carries the same disposition, pins, geometry,
assets, blockers and eight blocked release gates.

## Task geometry and profile fit

| Field | Record |
| --- | --- |
| Candidate | `Non-stationary Gabor TSM` (EUSIPCO 2017) |
| Source-reported input | audio waveform |
| Source-reported output | time-scaled audio waveform |
| Source-reported transform | non-stationary Gabor transform with time-varying windows and a well-conditioned inverse |
| Source-reported cost | higher than a plain STFT; research-grade |
| Recorded reference | LTFAT, reported GPL-3.0 |
| Audio-in/audio-out family | plausible |
| Exact geometry | not documented |
| Rate profile fit | `plausible_unverified` |

The catalogue describes an audio-to-audio spectral stretcher, so the Rate
profile is a plausible family fit. Unlike a text-conditioned renderer, the
method needs no text frontend. However, no exact window schedule, dual-window
rule, transform length, hop, latency or reset policy is recorded, and the only
named reference is copyleft. The geometry is therefore unverified and no
execution exists.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `rate_profile`, and the verifier checks each phrase of the
pinned row:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No reference runtime or exact mapping exists |
| Duration | blocked | No candidate output; no target or actual duration |
| Pitch | blocked | No candidate output and no listening result |
| Transient audibility | blocked | No candidate output and no listening result |
| Playback buffering | blocked | No device, scheduler, fill/flush or deadline measurement |
| 1x control | blocked | No runtime, so no identity/passthrough control was run |
| Rate changes | blocked | No exact ratio or step/ramp execution exists |
| Unfamiliar speech | blocked | No rights-cleared audio |
| Music | blocked | No rights-cleared music and no negative control |
| Silence | blocked | No empty or silent input execution |
| Rebuffer, drift, final partial | blocked | No playback or buffer execution |
| Pause/filler and preservation | blocked | No timestamped policy, VAD or preservation measure |
| Separate evidence categories | documented | Source-reported, schema-only, missing-real and sibling sections stay distinct |

Every row is `qualifies=false`. There are **zero** real results and **zero**
synthetic results. The package contains no surrogate transform, no synthetic
audio, no stft substitute and no position map: none would be the catalogued
method or add feasibility evidence for an absent reference.

## Fail-closed caller-supplied controls

The package models what a future intake must supply in
`asset_declaration_schema` and `rate_request_schema`. Both are shape-checked
only and never resolve a path, import a module, read a weight, open media or
apply a transform.

The asset declaration requires:

- source, reference, dependency and geometry presence to be declared absent
  with `null` revisions, digests and dimensions;
- the recorded reference implementation to be `ltfat` with no revision,
  licence id, licence-text digest or binary digest;
- code, reference, input, output-use and redistribution rights to be false
  with no review reference;
- the disposition to be `DEFER` and `qualifies=false`.

The rate request requires:

- input presence to be declared absent;
- a canonical decimal ratio string from `0.5` to `2`, no exponent, sign,
  leading zero, redundant trailing zero, `NaN`, `Infinity` or other
  nonfinite token;
- one of `constant`, `step` or `ramp`, with a strictly increasing schedule
  starting at source sample zero;
- runtime presence declared absent;
- the disposition to be `DEFER` and `qualifies=false`.

Any presence claim, set digest, invented geometry, rights claim, nonfinite
ratio, invalid mode, bad schedule or qualification claim is rejected. A
structurally valid request still returns `deferred_missing_reference` and is
never executed.

`report.json` records **43** rejected asset declarations, **58** rejected rate
requests and **9** strict-JSON rejections. The strict loader rejects duplicate
keys, `NaN`, `Infinity`, `-Infinity`, trailing data, byte-order marks,
non-object roots, empty input and unterminated documents.

## Absence evidence

Twenty fixed probes are checked with no recursive walk: 12 workspace paths
(checkouts, environments, references, audio, runs and research directories),
6 SDK-worktree paths (adapter, provider schema, third-party and installed
site-packages) and 2 home-cache paths. All 20 are absent in the canonical
bundle; `verify.py` fails if any probe later appears, so a stale "absent"
statement cannot ship. Asset and source digests are never asserted: the
required-artifact rows carry `sha256=null`, `revision=null` and `bytes=null`.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and licence provenance | blocked | Stage an exact reference source at an immutable revision with complete licence, notice and README records, and record independent review including the GPL-3.0 implication. |
| `RG-02` pinned runtime and offline install | blocked | Provide a locked offline runtime with package/wheel hashes, FFT and numeric dependency pins, install location and clean-room import digest. |
| `RG-03` transform assets and dependencies | blocked | Stage the NSGT or isolated LTFAT transform assets and verify every window schedule, dual-window, FFT and dependency byte count and SHA-256. |
| `RG-04` rights-cleared terms and inputs | blocked | Freeze permitted, digest-pinned audio inputs with corpus, evaluation, derived-output and redistribution decisions plus code and dependency terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned reference offline and record output hashes, finite and length behaviour, exact repeats, peak/RSS and identity-control values. |
| `RG-06` Rate profile against real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with 1x, exact constant ratios, step/ramp changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode and platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No schema control opens a gate. `DEFER` remains in force.

## Evidence classes and separation

| Class | Content | Admitted as result |
| --- | --- | --- |
| Source-reported candidate note | `playback-speed-candidates.md` section 5.9 | no |
| Inventory and plan scope | `INVENTORY.json`, `INVENTORY.md`, `plan/audio-sdk/README.md` | no |
| Rate acceptance profile | `plan/swarm/VERIFICATION.md` | no |
| Schema-only declaration and request controls | This package | no |
| Missing real candidate evidence | All Rate-profile rows | no |
| Sibling TSM and rate evidence | DiffATSM, Granular TSM, USC mrate, libsamplerate | no |

Granular TSM is a distinct time-domain grain overlap-add reference with its
own synthetic fixtures and optional provider. DiffATSM is a raw-audio
diffusion TSM system. USC mrate is a rate estimator, not a stretcher.
libsamplerate changes sample rate and duration at fixed playback rate, not
pitch-preserving time scale. No source, fixture, case, rejection count or
metric from any sibling is inherited or pooled.

## Scope and boundary

Only `docs/task-evidence/non-stationary-gabor-tsm/` is added. No provider
registration, descriptor, registry, default, public header, ABI, shared CMake,
CI workflow, installed-v0 behaviour, board or handoff is changed. No network
access or download is attempted. The scope gate resolves the newest
merge-base with `origin/main` (falling back to `main`), fails closed with
`scope_base_unavailable` when no base resolves, and reports
`base_out_of_scope_change:<path>` for any committed path outside this task
directory.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands, gates. |
| `LICENSES.md` | Source/asset/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, identity, geometry, blockers, eight gates, Rate rows, declaration and rate-request schemas, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, board projection, absence probes, snippet checks, fail-closed validators, scope helpers, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256`, README digest tables and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, reference, audio or corpus. |
| `verify.py` | Read-only strict-JSON, pin, README digest, reproduction, licensing and merge-base scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduction

Requires CPython `3.12.16`, the interpreter used for the canonical bundle, with
`PYTHONDONTWRITEBYTECODE=1`.

```sh
cd docs/task-evidence/non-stationary-gabor-tsm
PYTHONDONTWRITEBYTECODE=1 python3 reference.py   # print the canonical report
PYTHONDONTWRITEBYTECODE=1 python3 run.py all     # 3x byte-identical regeneration
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py      # strict read-only verification
```

Expected final line: `PASS verify.py ...`. `run.py` writes only this directory.
`verify.py` performs a fresh three-run cold-start regeneration in a temporary
directory and compares the committed bytes.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:research/speech-rate-tsm-evaluation-20261101.md` | `525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:research/tsm-followup-20261101/agent-stretchers/REPORT.md` | `8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb` |
<!-- digest-table: end -->

The mutable shared board `plan/swarm/TASKS.json` is **not** pinned. Only the
stable linked-row projection `{id,title,component,mode,repository,depends_on}`
is gated; mutable status, owner, claim, review, handoff, blocked-reason and
dispatch-priority fields are excluded.

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:docs/task-evidence/diffatsm/report.json` | `8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a` |
| `sdk:docs/task-evidence/granular-tsm/report.json` | `3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138` |
| `sdk:docs/task-evidence/usc-mrate/report.json` | `d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

Every generated artifact except this README and `SOURCES.sha256` (which cannot
pin itself) is listed with its live digest and byte count.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `1130508190893fc9eecfeb12b41473c2e8f3a44c413fbdb172b6f9ff144bb2ce` | 1604 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `eaf6557f17130104cac2d7db5a81119695961dda2afa357fa21578e358602e24` | 44611 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `0212f5dbb5338b100e0ceafbfed34b2ad3f7fa85e74861d1ef86c905b791458b` | 91227 |
| `report.json` | `a89d9e49067e17e850267aaa6c23803d210ce6b503ac241a623aeb295a47dfdf` | 49521 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `e63609d673e2106eccb2c1225a45c659ddf02e68e1941d58f8209dd7b5a15c9f` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `21347f9d677cd7178943ff549031be7e567eafaa00e7124fcf5effb8992e1413` | 4503 |
| `test_reference.py` | `bd37b4b7dc4ee0cfe05bf4a1f5964004b4385d6fdbb70ef5d679fe6a3ea3171c` | 24387 |
| `verify.py` | `17e9c8c5194d93b3aca5876578685151dab375dd469cec974f3c7f1488256657` | 28627 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Explicit non-claims

- No non-stationary Gabor transform, NSGT or LTFAT source, wheel, binary,
  object, revision, licence text or notice is present, imported, linked,
  deserialised or executed.
- No FFT, STFT, phase-vocoder, NSGT analysis, dual-window, coefficient
  modification, synthesis or resampling routine is implemented or applied.
- No audio, corpus, music, speech, synthetic signal or candidate output is
  read, generated, stored or scored.
- No rate, duration, pitch, transient, preservation, buffering, listening,
  device or benchmark result exists.
- The caller-supplied declarations are fail-closed shape checks only; they
  are not adapters, runtimes, references or qualifications.
- No provider, descriptor, registry, default, installed v0, public ABI,
  shared build, CI, board or handoff path is changed.
- The research note and paper DOI are source-reported context only and are
  not measured evidence.
- No sibling TSM, estimator or sample-rate converter result is inherited.
