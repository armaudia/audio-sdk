<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURAL-WSOLA - Neural WSOLA readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local feasibility evidence for the Neural WSOLA row. It is
**not** a Neural WSOLA implementation, adapter or rate controller. No named
method, official source, weight, checkpoint, model card, runtime, licence text,
rights-cleared speech or music input, audio, candidate output, listening
result, device measurement, benchmark or release claim is present. **No result
here qualifies Neural WSOLA.**

`plan/INVENTORY.json` records `neural-wsola` as `evidence_status=blocked`,
`disposition=sdk-model`, area `Rate and content`, with the **Rate** acceptance
profile and task `SDK-NEURAL-WSOLA`. Its only evidence link is
`research/voice-enhancement-20261101/candidate_matrix.csv`, record 39, with the
finding:

> **unavailable/blocked:** No exact neural WSOLA model, checkpoint or
> implementation is staged; FFmpeg atempo was measured as a separate classical
> control.

The pinned research records treat Neural WSOLA as a candidate family rather
than a named method: no exact source is pinned by the request phrase, and a
conventional WSOLA library or generic neural TSM model must not be substituted.
That is source-reported context, not a local run.

## Exact external blocker

The exact **named method**, the **official source snapshot**, the **neural
model/checkpoint assets**, the **pinned runtime and streaming geometry**, the
**reviewed terms** and the **matched rate evidence** are absent. Nothing was
fabricated, reconstructed, mirrored, downloaded or substituted. No revision,
file name, byte count or SHA-256 is asserted as verified. The classical
WSOLA/SOLA, SoundTouch, Sonic, Rubber Band, PSOLA and FFmpeg atempo results are
different candidates and are not inherited.

| Missing artifact | Exact requirement |
| --- | --- |
| Named method and source | A named Neural WSOLA method with the official repository at an immutable 40-hex commit or release tag, reviewed licence text, README, model/API definitions and a per-file SHA-256 manifest |
| Neural assets | Every model, checkpoint, weight, alignment/encoder module and inference config at an immutable revision, with byte counts and SHA-256 values per file and tensor layout |
| Runtime and geometry | A locked offline runtime with exact interpreter, package versions, wheel hashes, platform, device, dtype, determinism settings and install location, plus sample rate, channels, frame, hop, lookahead, latency, reset and drain behaviour |
| Rights | Code, weight, training-data and derived-output terms, plus consent, acquisition, evaluation, attribution and redistribution decisions for speech and music inputs |
| Matched evidence | A frozen, rights-cleared cohort with a same-condition baseline, 1x control, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final-partial and speech-preservation measurements on the exact runtime |

The machine-readable record is `report.json` -> `source_reported_identity`,
`task_geometry`, `absence_evidence`, `rate_profile`, `matched_evidence`,
`asset_declaration`, `exact_blockers`, `gates` and `qualification`.
`contract.json` carries the same disposition, pins, geometry, assets,
blockers and eight blocked release gates.

## Task geometry and profile fit

| Field | Record |
| --- | --- |
| Candidate | `Neural WSOLA` (candidate family) |
| Catalogued status | `unavailable/blocked` |
| Named method | none |
| Paper or venue | none recorded |
| Baseline named by the screen | Classical WSOLA/SOLA |
| Expected input | audio waveform (family expectation) |
| Expected output | time-scaled audio waveform (family expectation) |
| Audio-in path verified | no |
| Sample rate / frame / hop / channels | not documented |
| Rate profile fit | `unverified` |

The catalogued Rate profile expects an audio source mapped to a stretched audio
output with a frozen rate/frame/hop geometry. The candidate family matches that
direction in principle, but no named method, streaming contract or exact
geometry is documented, so the fit cannot be verified. This package does not
invent one.

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
synthetic results. The package contains no surrogate rate envelope, no
synthetic audio and no position-map substitute: a conventional WSOLA/SOLA
envelope would be the classical baseline, not the neural candidate, and the
pinned research explicitly forbids that substitution.

## Fail-closed caller-supplied asset declaration

The package models what a future caller must supply in
`asset_declaration_schema`. The declaration is shape-checked only:

- source, weights and runtime presence must be declared absent with `null`
  revision and digest fields;
- the candidate must not name a method or paper, and must be audio-in/audio-out;
- geometry must be declared absent with `null` rate/frame/hop/channel fields;
- code, weight, training-data, input, output-use and redistribution rights
  must be false with no review reference;
- the disposition must be `DEFER` and `qualifies=false`.

Any presence claim, named-method claim, set digest, invented geometry, rights
claim or qualification claim is rejected. The package cannot verify external
bytes, so it must not accept a presence claim; a future intake verifies hashes
in a separate gate. The declaration never resolves a path, imports a module,
reads a weight, opens media or runs inference.

`report.json` records **41** rejected declarations and **9** strict-JSON
rejections. The strict loader rejects duplicate keys, `NaN`, `Infinity`,
`-Infinity`, trailing data, byte-order marks, non-object roots, empty input and
unterminated documents.

## Absence evidence

Twenty fixed probes are checked with no recursive walk: 12 workspace paths
(checkouts, models, environments, references, audio, runs and research
directories), 5 SDK-worktree paths (adapter, provider schema, third-party and
installed site-packages) and 3 home-cache paths. All 20 are absent in the
canonical bundle; `verify.py` fails if any probe later appears, so a stale
"absent" statement cannot ship. Asset and source digests are never asserted:
the required-artifact rows carry `sha256=null`, `revision=null` and
`bytes=null`.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` named method, source revision and licence provenance | blocked | Name the exact method and stage the official source at an immutable revision with complete licence, notice and README records, then record independent review. |
| `RG-02` pinned runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and exact inference settings. |
| `RG-03` neural model, checkpoint and weight assets | blocked | Stage every neural model, checkpoint, weight and inference config asset and verify each byte count and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze permitted, digest-pinned speech and music inputs with corpus, evaluation, derived-output and redistribution decisions plus weight and training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned assets offline and record output hashes, finite and length behaviour, exact repeats and peak/RSS values. |
| `RG-06` Rate profile against the real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode and platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No schema control opens a gate. `DEFER` remains in force.

## Evidence classes and separation

| Class | Content | Admitted as result |
| --- | --- | --- |
| Source-reported candidate screen | `candidate_matrix.csv` record 39 | no |
| Source-reported artifact review | `agent-vad-asr-trials/REPORT.md` line 15 | no |
| Candidate-family screen | `agent-segmentation/REPORT.md` line 32 | no |
| Blocked reaudit | `agent-blocked-reaudit/REPORT.md` line 20 | no |
| Schema-only declaration control | This package's unpopulated declaration | no |
| Classical WSOLA/SOLA sibling | OLA/SOLA and SoundTouch packages | no |
| Adjacent classical control | FFmpeg atempo screen | no |
| Sibling neural candidate | Neural ATSM and DiffATSM blocker packages | no |
| Missing real candidate evidence | All Rate-profile rows | no |

Classical time-stretch results are conventional engine evidence, not this
neural candidate. The FFmpeg atempo screen is explicitly not a substitute. No
sibling source, checkpoint, fixture, envelope case, rejection count or metric
is inherited or pooled.

## Scope and boundary

Only `docs/task-evidence/neural-wsola/` is added. No provider registration,
descriptor, registry, default, public header, ABI, shared CMake, CI workflow,
installed-v0 behaviour, board or handoff is changed. No network access or
download is attempted. The scope gate resolves the newest merge-base with
`origin/main` (falling back to `main`), fails closed with
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
cd docs/task-evidence/neural-wsola
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
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
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
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:docs/task-evidence/diffatsm/report.json` | `8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a` |
| `sdk:docs/task-evidence/neural-atsm/report.json` | `3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b` |
| `sdk:docs/task-evidence/ola-sola/report.json` | `90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93` |
| `sdk:docs/task-evidence/soundtouch/report.json` | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

Every generated artifact except this README and `SOURCES.sha256` (which cannot
pin itself) is listed with its live digest and byte count.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `0708aa37cfc97eb32ef07d4e513c1bbee907471d08e61d0814b51bf38cf8c047` | 1450 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `aba1983aacb3b3c05b3360ec1c67c51e40dac4a6b202617396bf44b80f143aeb` | 38226 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `7d777d2eb75f0caab63aaf84a12c30993433849ac5edba3e69546dd715d60dd3` | 75656 |
| `report.json` | `81b8823caabd2738e728fc787f6072fd9ba769e11446ecd32ff7d8b244c8a842` | 43475 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `ad8d10f5951e4a377315fab40919f9f0c88e53df30e958181fb76411cf52fd71` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `cdf3efdbe636c596f23339c0913d7f163e02455d3b4d2c024f404b9a4bfe6b13` | 4484 |
| `test_reference.py` | `8ed04519599891d38983919ec1348000e4fd1aa29bf36c7ec28697bda2e0b948` | 22157 |
| `verify.py` | `045c959317420ceb16ed0e9c4e0be2a07c9714988ef65901eef362a8db9388b6` | 27353 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Explicit non-claims

- No Neural WSOLA source, code snapshot, weight, checkpoint, model card or
  inference implementation is present, loaded, deserialised or reconstructed.
- No PyTorch, TensorFlow, ONNX Runtime or other neural runtime is imported,
  installed or linked.
- No remote code, model, weight, dataset or binary is downloaded.
- No candidate inference, rate estimate, time-scale modification, duration,
  pitch, transient, preservation, listening, device or benchmark result exists.
- No classical WSOLA/SOLA, SoundTouch, Sonic, Rubber Band, Bungee, PSOLA or
  FFmpeg atempo result is inherited, pooled or presented as Neural WSOLA.
- The caller-supplied asset declaration is a fail-closed shape check only; it
  is not an adapter, runtime, model or qualification.
- No provider, descriptor, registry, default, installed v0, public ABI, shared
  build or CI path is changed.
- The research prose is source-reported context only and is not measured
  evidence.
