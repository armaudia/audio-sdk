<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION - readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local feasibility evidence for the Phase vocoder with neural
transient preservation row. It is **not** an implementation, adapter, model,
runtime or rate controller. No named method, official source, weight,
checkpoint, model card, runtime, licence text, rights-cleared speech or music
input, audio, candidate output, listening result, device measurement, benchmark
or release claim is present. **No result here qualifies.**

`plan/INVENTORY.json` records `phase-vocoder-with-neural-transient-preservation`
as `evidence_status=blocked`, `disposition=sdk-model`, area `Rate and content`,
with the **Rate** acceptance profile and task
`SDK-PHASE-VOCODER-WITH-NEURAL-TRANSIENT-PRESERVATION`. Its evidence cites
`research/voice-enhancement-20261101/candidate_matrix.csv` record 40:

> **unavailable/blocked:** No phase-vocoder/transient model implementation or
> weights; the adjacent atempo screen is not this candidate.

The pinned research treats this as an unnamed candidate family, not a pinned
method. Rubber Band R3/R2 is a classical control with phase resets on percussive
transients, but it is explicitly not neural transient preservation and is not
substituted. That is source-reported context, not a local run.

## Exact external blocker

The exact **named method**, **official source snapshot**, **neural
transient/model/checkpoint assets**, **pinned runtime and streaming geometry**,
**reviewed terms** and **matched rate evidence** are absent. Nothing was
fabricated, reconstructed, mirrored, downloaded or substituted. No revision,
file name, byte count or SHA-256 is asserted as verified. Classical
phase-vocoder, Rubber Band, SoundTouch, OLA/SOLA, PSOLA and FFmpeg atempo
results are different candidates and are not inherited.

| Missing artifact | Exact requirement |
| --- | --- |
| Named method and source | A named method with official repository at an immutable 40-hex commit or release tag, reviewed licence text, README, model/API definitions and a per-file SHA-256 manifest |
| Neural/transient assets | Every neural transient-preservation model, checkpoint, phase-vocoder integration module and inference config at an immutable revision, with byte counts and SHA-256 values per file and tensor layout |
| Runtime and geometry | A locked offline runtime with exact interpreter, package versions, wheel hashes, platform, device, dtype, determinism settings and install location, plus sample rate, channels, frame, hop, lookahead, latency, reset and drain behaviour |
| Rights | Code, weight, training-data and derived-output terms, plus consent, acquisition, evaluation, attribution and redistribution decisions for speech and music inputs |
| Matched evidence | A frozen, rights-cleared cohort with same-condition baseline, 1x control, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final-partial and speech-preservation measurements on the exact runtime |

Machine-readable records: `contract.json` (contract pins/gates/blockers) and
`report.json` (canonical DEFER readiness report). `report.json.sha256` pins the
report bytes. `SOURCES.sha256` pins source, boundary and task-local artifacts.

## Task geometry and profile fit

| Field | Record |
| --- | --- |
| Candidate | `Phase vocoder with neural transient preservation` (candidate family) |
| Catalogued status | `unavailable/blocked` |
| Named method | none |
| Paper or venue | none recorded |
| Baselines named by screen | Rubber Band phase vocoder; WSOLA |
| Expected input | audio waveform (family expectation) |
| Expected output | time-scaled audio waveform with transient preservation (family expectation) |
| Audio-in path verified | no |
| Sample rate / frame / hop / channels | not documented |
| Rate profile fit | `unverified` |

The Rate profile expects an audio source mapped to a stretched audio output with
frozen rate/frame/hop geometry. The candidate family matches that direction in
principle, but no named method, streaming contract or exact geometry is
documented, so the fit cannot be verified. This package does not invent one.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `rate_profile`, and the verifier checks each phrase of the
pinned row:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No named method or runtime; no audio-in mapping exists |
| Duration | blocked | No candidate output; no target or actual duration |
| Pitch | blocked | No candidate output and no listening result |
| Transient audibility | blocked | No candidate output and no listening result |
| Playback buffering | blocked | No device, scheduler, fill/flush or deadline measurement |
| 1x control | blocked | No runtime, so no identity/passthrough control was run |
| Rate changes | blocked | No step or ramp execution exists |
| Unfamiliar speech | blocked | No rights-cleared audio |
| Music | blocked | No rights-cleared music and no negative control |
| Silence | blocked | No empty or silent input execution |
| Rebuffer, drift, final partial | blocked | No playback or buffer execution |
| Pause/filler and preservation | blocked | No timestamped policy, VAD, speech or preservation measure |
| Separate evidence categories | documented | Source-reported, schema-only, classical-control, missing-real and sibling sections stay distinct |

Every row is `qualifies=false`. There are **zero** real results and **zero**
synthetic results. No surrogate rate envelope, synthetic audio or position-map
substitute is included: a classical phase-vocoder control would be a different
candidate and is not substituted.

## Fail-closed caller-supplied asset declaration

`report.json` -> `asset_declaration` records the shape-checked schema and an
accepted unpopulated control. The declaration is shape-checked only:

- source, weights and runtime presence must be declared absent with `null`
  revision and digest fields;
- the candidate must not name a method or paper, and must be audio-in/audio-out;
- geometry must be declared absent with `null` rate/frame/hop/channel fields;
- code, weight, training-data, input, output-use and redistribution rights must
  be false with no review reference;
- the disposition must be `DEFER` and `qualifies=false`.

Any presence claim, named-method claim, set digest, invented geometry, rights
claim or qualification claim is rejected. The package cannot verify external
bytes, so it must not accept a presence claim. The declaration never resolves a
path, imports a module, reads a weight, opens media or runs inference.

`report.json` records **41** rejected declarations and **9** strict-JSON
rejections. The strict loader rejects duplicate keys, `NaN`, `Infinity`,
`-Infinity`, trailing data, byte-order marks, non-object roots, empty input and
unterminated documents.

## Absence evidence

Twenty fixed probes are checked with no recursive walk: 12 workspace paths, 5
SDK-worktree paths and 3 home-cache paths. All 20 are absent in the canonical
bundle; `verify.py` fails if any probe later appears. Asset and source digests
are never asserted: required-artifact rows carry `sha256=null`, `revision=null`
and `bytes=null`.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` named method, source revision and licence provenance | blocked | Name the exact method and stage the official source at an immutable revision with complete licence, notice and README records, then record independent review. |
| `RG-02` pinned runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and exact inference settings. |
| `RG-03` neural/model/checkpoint assets | blocked | Stage every neural transient/model/phase-vocoder integration asset and verify each byte count and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze permitted, digest-pinned speech and music inputs with corpus, evaluation, derived-output and redistribution decisions plus weight and training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned assets offline and record output hashes, finite and length behaviour, exact repeats and peak/RSS values. |
| `RG-06` Rate profile against the real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode and platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No schema control opens a gate. `DEFER` remains in force.

## Evidence classes and separation

| Class | Content | Admitted as result |
| --- | --- | --- |
| Source-reported candidate screen | `candidate_matrix.csv` record 40 | no |
| Source-reported artifact review | `agent-vad-asr-trials/REPORT.md` line 15 | no |
| Candidate-family screen | `agent-segmentation/REPORT.md` line 32 | no |
| Blocked reaudit | `agent-blocked-reaudit/REPORT.md` line 20 | no |
| Schema-only declaration control | This package's unpopulated declaration | no |
| Classical phase-vocoder baseline | `phase-vocoder-baseline` evidence package | no |
| Classical transient-aware control | Rubber Band R3/R2 research note | no |
| Adjacent classical control | FFmpeg atempo screen | no |
| Sibling neural candidate | Neural WSOLA / Neural ATSM / DiffATSM blocker packages | no |
| Missing real candidate evidence | All Rate-profile rows | no |

Classical time-stretch results are conventional engine evidence, not this neural
candidate. No sibling source, checkpoint, fixture, envelope case, rejection
count or metric is inherited or pooled.

## Scope and boundary

Only `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/` is
added. No provider registration, descriptor, registry, default, public header,
ABI, shared CMake, CI workflow, installed-v0 behaviour, board or handoff is
changed. No network access or download is attempted. The scope gate resolves the
newest merge-base with `origin/main` (falling back to `main`), fails closed with
`scope_base_unavailable` when no base resolves, and reports
`base_out_of_scope_change:<path>` for any committed path outside this task
directory.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands, gates. |
| `LICENSES.md` | Source/asset/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, identity, geometry, assets, blockers, eight gates, Rate rows, declaration schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, board projection, absence probes, snippet checks, declaration validator, scope helpers, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256`, README digest tables and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, checkpoint or audio input. |
| `verify.py` | Read-only strict-JSON, pin, README digest, reproduction, licensing and merge-base scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduction

Requires CPython `3.11.5`, the interpreter used for the canonical bundle, with
`PYTHONDONTWRITEBYTECODE=1`.

```sh
cd docs/task-evidence/phase-vocoder-with-neural-transient-preservation
PYTHONDONTWRITEBYTECODE=1 python3 reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

Expected final line: `PASS verify.py ...`. `run.py` writes only this directory.
`verify.py` performs a fresh three-run cold-start regeneration in a temporary
directory and compares the committed bytes.

## Source pins (SHA-256)

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `docs/task-evidence/diffatsm/report.json` | `8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a` |
| `docs/task-evidence/neural-atsm/report.json` | `3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b` |
| `docs/task-evidence/neural-wsola/report.json` | `81b8823caabd2738e728fc787f6072fd9ba769e11446ecd32ff7d8b244c8a842` |
| `docs/task-evidence/phase-vocoder-baseline/report.json` | `555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact pins (SHA-256)

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 |
| --- | --- |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/LICENSES.md` | `1966b93fe80df48c72a5a9d176f87186a0268bb2d4dff1e197d7e045a84fac23` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/contract.json` | `b8fe83ce933ebd8ef44ed705a8382d94a59f21b8ee3bed01af0c9a3d791a82ce` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/reference.py` | `3f6fd450d410f7684b304d1f268f3722fe86c46f36607885c91ca3afb18b14a3` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json` | `131640f3c436426827a3cc18c0183195dbb3839cf96b85353e0d79864f222dc5` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json.sha256` | `95ade3729975e6d67d9db8fa92e7800a07ca2bb833b7b5c9fd456ffec130a24d` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/run.py` | `ca7cefa7eb7f9fceb39b4383c4d678c1144bf51807569a933ead757be73e1175` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/test_reference.py` | `793d04c1189a5508b442486d16a64e42eb9e1b9beaf5815056b71267152b8c11` |
| `docs/task-evidence/phase-vocoder-with-neural-transient-preservation/verify.py` | `32fc0e685ce573c8e5d9502e59626ff3e5655056480d96496b8cc88d63248a39` |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
