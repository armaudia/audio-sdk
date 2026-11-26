<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NEURAL-ATSM - Neural ATSM readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local feasibility evidence for the Neural ATSM row. It is
**not** a Neural ATSM implementation, adapter or rate controller. No official
source, weight, checkpoint, text frontend, phoneme-rate head, upsampling or
attention module, VAE/flow decoder, vocoder, runtime, licence text, model card,
rights-cleared text or speech input, audio, candidate output, listening
result, device measurement, benchmark or release claim is present. **No result
here qualifies Neural ATSM.**

`plan/INVENTORY.json` records `neural-atsm` as `evidence_status=considered`,
`disposition=sdk-model`, area `Rate and content`, with the **Rate** acceptance
profile and task `SDK-NEURAL-ATSM`. Its only evidence link is
`research/tsm-followup-20261101/README.md`, line 37, with the finding:

> **Poor fit / not run:** full stack is text-conditioned and reconstructs
> audio; no runnable lightweight audio-only controller artifact found.

The pinned research records describe the Interspeech 2024 Neural ATSM system as
sentence text to phoneme-level rate, with learned upsampling/attention and
VAE/flow reconstruction in the full stack. They record that no official
executable lightweight waveform-to-rate module or checkpoint was identified.
That is source-reported context, not a local run.

## Exact external blocker

The exact **official source snapshot**, the **phoneme-rate and resynthesis
assets**, the **pinned text/inference runtime**, the **audio task geometry**,
the **reviewed terms** and the **matched rate evidence** are absent. Nothing
was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count or SHA-256 is asserted as verified. The paper
URL is provenance only.

| Missing artifact | Exact requirement |
| --- | --- |
| Source snapshot | The official Neural ATSM repository at an immutable 40-hex commit or release tag, with reviewed licence text, README, model/API definitions and a per-file SHA-256 manifest |
| Rate and resynthesis assets | Every text-frontend vocabulary, phoneme-rate head, upsampling/attention module, VAE/flow decoder, vocoder and inference config at an immutable revision, with byte counts and SHA-256 values per file |
| Runtime | A locked offline runtime with exact interpreter, text frontend, package versions, wheel hashes, platform, device, dtype, determinism settings and install location |
| Task geometry | The exact audio-in/rate-out contract: sample rate, channels, frame, hop, lookahead, latency, reset and drain behaviour; or an explicit statement that only text-conditioned resynthesis is supported |
| Rights | Code, weight, training-data, text-corpus and derived-output terms, plus consent, acquisition, evaluation, attribution and redistribution decisions |
| Matched evidence | A frozen, rights-cleared cohort with a same-condition baseline, 1x control, rate changes, unfamiliar speech, music, silence, rebuffer, drift, final-partial and speech-preservation measurements on the exact runtime |

The machine-readable record is `report.json` -> `source_reported_identity`,
`task_geometry`, `absence_evidence`, `rate_profile`, `matched_evidence`,
`asset_declaration`, `exact_blockers`, `gates` and `qualification`.
`contract.json` carries the same disposition, pins, geometry, assets,
blockers and eight blocked release gates.

## Task geometry and profile fit

| Field | Record |
| --- | --- |
| Candidate | `Neural ATSM` (Interspeech 2024) |
| Source-reported input | sentence text |
| Source-reported output | phoneme-level rate and resynthesised audio |
| Source-reported stages | text frontend, phoneme-rate predictor, learned upsampling/attention, VAE/flow reconstruction |
| Audio-in path verified | no |
| Audio-only controller | no |
| Rate-only estimator | no |
| Sample rate / frame / hop / channels | not documented |
| Rate profile fit | `mismatch` |

The catalogued Rate profile expects an audio source mapped to a stretched audio
output with a frozen rate/frame/hop geometry. The source-reported candidate is
text-conditioned and reconstructs audio. Even with released artifacts, it
would not be an audio-only rate controller without an explicit adapter
contract. This package does not invent one.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `rate_profile`, and the verifier checks each phrase of the
pinned row:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | Text-to-rate-to-audio is source-reported only; no audio-in mapping exists |
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
| Separate evidence categories | documented | Source-reported, schema-only, missing-real and sibling sections stay distinct |

Every row is `qualifies=false`. There are **zero** real results and **zero**
synthetic results. The package contains no surrogate rate envelope, no
synthetic audio and no position-map substitute: a position map would not be
Neural ATSM and would add no feasibility evidence for a text-conditioned
renderer.

## Fail-closed caller-supplied asset declaration

The package models what a future caller must supply in
`asset_declaration_schema`. The declaration is shape-checked only:

- source, weights and runtime presence must be declared absent with `null`
  revision and digest fields;
- geometry must be declared absent with `null` rate/frame/hop/channel fields;
- code, weight, training-data, input, output-use and redistribution rights
  must be false with no review reference;
- the disposition must be `DEFER` and `qualifies=false`.

Any presence claim, set digest, invented geometry, rights claim or
qualification claim is rejected. The package cannot verify external bytes, so
it must not accept a presence claim; a future intake verifies hashes in a
separate gate. The declaration never resolves a path, imports a module, reads
a weight, opens media or runs inference.

`report.json` records **41** rejected declarations and **9** strict-JSON
rejections. The strict loader rejects duplicate keys, `NaN`, `Infinity`,
`-Infinity`, trailing data, byte-order marks, non-object roots, empty input and
unterminated documents.

## Absence evidence

Twenty fixed probes are checked with no recursive walk: 12 workspace paths
(checkouts, models, environments, references, audio, runs and a research
directory), 5 SDK-worktree paths (adapter, provider schema, third-party and
installed site-packages) and 3 home-cache paths. All 20 are absent in the
canonical bundle; `verify.py` fails if any probe later appears, so a stale
"absent" statement cannot ship. Asset and source digests are never asserted:
the required-artifact rows carry `sha256=null`, `revision=null` and
`bytes=null`.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and licence provenance | blocked | Stage the official source at an immutable revision with complete licence, notice and README records, then record independent review. |
| `RG-02` pinned runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and exact text-frontend/inference settings. |
| `RG-03` phoneme-rate and resynthesis assets | blocked | Stage every text-frontend, phoneme-rate, upsampling/attention, VAE/flow and vocoder asset and verify each byte count and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze permitted, digest-pinned text and speech inputs with corpus, evaluation, derived-output and redistribution decisions plus weight and training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned assets offline and record output hashes, finite and length behaviour, exact repeats and peak/RSS values. |
| `RG-06` Rate profile against the real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the final partial window. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode and platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No schema control opens a gate. `DEFER` remains in force.

## Evidence classes and separation

| Class | Content | Admitted as result |
| --- | --- | --- |
| Source-reported candidate screen | `research/tsm-followup-20261101/README.md` line 37 | no |
| Source-reported artifact review | `agent-text/REPORT.md` line 49 and the initial screen line 28 | no |
| Rate-engine and neural-estimator context | `agent-stretchers/REPORT.md`, `agent-neural/REPORT.md` | no |
| Schema-only declaration control | This package's unpopulated declaration | no |
| Missing real candidate evidence | All Rate-profile rows | no |
| Sibling candidate | DiffATSM blocker package | no |

The sibling DiffATSM package is a distinct raw-audio diffusion TSM system. No
source, checkpoint, PPG model, envelope case, rejection count or metric is
inherited or pooled. Rate-engine and neural-estimator research in the same
workspace concerns other candidates; none of its measurements is a Neural
ATSM result.

## Scope and boundary

Only `docs/task-evidence/neural-atsm/` is added. No provider registration,
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
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, checkpoint, audio or text input. |
| `verify.py` | Read-only strict-JSON, pin, README digest, reproduction, licensing and merge-base scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduction

Requires CPython `3.12.16`, the interpreter used for the canonical bundle, with
`PYTHONDONTWRITEBYTECODE=1`.

```sh
cd docs/task-evidence/neural-atsm
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
| `source:research/speech-rate-tsm-evaluation-20261101.md` | `525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:research/tsm-followup-20261101/agent-neural/REPORT.md` | `f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73` |
| `source:research/tsm-followup-20261101/agent-stretchers/REPORT.md` | `8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb` |
| `source:research/tsm-followup-20261101/agent-text/REPORT.md` | `86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93` |
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
| `sdk:docs/task-evidence/diffatsm/README.md` | `89a8e7c1bf69dff35149e375ecd81cf5cf27aa0f368c91db95624c84e808f7da` |
| `sdk:docs/task-evidence/diffatsm/report.json` | `8639ffdfa1c75d1aaefdde8491053e2353ef400a06b76ba935d261f703c4dc7a` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

Every generated artifact except this README and `SOURCES.sha256` (which cannot
pin itself) is listed with its live digest and byte count.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `f956fd2851d9bade0254caf3d885f4efeca4c1fec01d0ee5dfb349c09e530978` | 1624 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `c21da3a53f9305a6f6b2aec0bc7909c9872615d685ba5d7236251673096cf24b` | 36349 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `debedfe314619756f80c2f6f82d3ca0ad2b59ee6f8eb31c5ab03740a84f6dac8` | 72725 |
| `report.json` | `3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b` | 41307 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `2854e29283333085eed147a6b6f08393e9a59aa4c2738916b0cd15de8cf2de3b` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `83b7923914626983e513b14d692341bea9b1b9c556e4f9af78c710a2e75cbe41` | 4509 |
| `test_reference.py` | `de19677eeda2f1ef02c694aaa5d67db8cd263163d4a0b0f905d69c533d1a7dd5` | 21288 |
| `verify.py` | `e77988ae605eef8836c5021f606bf30b799bf97d2cb3c4ea7e9c23767f5e8bbf` | 26774 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Explicit non-claims

- No Neural ATSM source, code snapshot, weight, checkpoint, phoneme-rate head,
  text frontend, VAE/flow decoder, vocoder or inference implementation is
  present, loaded, deserialised or reconstructed.
- No PyTorch, TensorFlow, text frontend, vocoder or candidate module is
  imported, installed or linked.
- No remote code, model, weight, dataset, text corpus or binary is downloaded.
- No candidate inference, rate estimate, time-scale modification, duration,
  pitch, transient, preservation, listening, device or benchmark result exists.
- The caller-supplied asset declaration is a fail-closed shape check only; it
  is not an adapter, runtime, model or qualification.
- No provider, descriptor, registry, default, installed v0, public ABI, shared
  build or CI path is changed.
- The research prose and paper URL are source-reported context only and are not
  measured evidence.
