<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-NANSY-ANALYSIS-RESYNTHESIS - NANSY readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local feasibility evidence for the NANSY
analysis/resynthesis row. It is **not** a NANSY implementation, adapter,
analyzer, resynthesizer or voice converter. No official source, weight,
checkpoint, config, content/pitch/energy/timbre analysis module, generator,
vocoder, runtime, licence text, model card, reference voice, target voice,
rights-cleared speech input, real audio, candidate output, parity result,
listening result, device measurement, benchmark or release claim is present.
**No result here qualifies NANSY.**

`plan/INVENTORY.json` records `nansy-analysis-resynthesis` as
`evidence_status=considered`, `disposition=sdk-model`, area `Voice and
synthesis`, with the **Voice** acceptance profile, task
`SDK-NANSY-ANALYSIS-RESYNTHESIS` and plan note:

> Stage exact model, validate analysis-to-waveform parity and speech
> preservation.

Its only evidence link is `research/category_registry.json`, whose source S35
is the NeurIPS 2021 "NANSY analysis and resynthesis paper" URL. The pinned
research records are a paper lead and a one-line survey row. They contain no
repository, revision, checkpoint, config, runtime, terms or measurement. That
is source-reported context, not a local run.

## Exact external blocker

The exact **official source snapshot**, the **checkpoint and resynthesis
assets**, the **pinned offline runtime**, the **candidate task geometry**, the
**reviewed rights and consent** and the **matched Voice evidence** are absent.
Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count or SHA-256 is asserted as verified. The paper
URL is provenance only.

| Missing artifact | Exact requirement |
| --- | --- |
| Source snapshot | The official NANSY repository at an immutable 40-hex commit or release tag, with reviewed licence text, README, model/API definitions and a per-file SHA-256 manifest |
| Checkpoint and resynthesis assets | Every content, pitch, energy and timbre analysis module, generator, vocoder and inference config at an immutable revision, with byte counts and SHA-256 values per file |
| Runtime | A locked offline runtime with exact interpreter, package versions, wheel hashes, platform, device, dtype, determinism settings and install location |
| Task geometry | The exact analysis/resynthesis contract: sample rate, channels, analysis frame, hop, lookahead, latency, reset and drain behaviour |
| Rights | Code, weight, training-data, corpus and derived-output terms, plus source and target voice consent, reference availability and redistribution decisions |
| Matched evidence | A frozen, rights-cleared cohort with a same-condition baseline, analysis-to-waveform parity, speech preservation, content, identity/similarity, naturalness, alignment, first-output/tail and timing measurements on the exact runtime |

The machine-readable record is `report.json` -> `candidate_identity`,
`task_geometry`, `absence_evidence`, `profile_rows`, `matched_evidence`,
`asset_declaration`, `exact_blockers`, `release_gates` and `qualification`.
`contract.json` carries the same disposition, pins, geometry, assets, blockers
and eight blocked release gates.

## Task geometry and profile fit

| Field | Record |
| --- | --- |
| Candidate | `NANSY analysis/resynthesis` (NeurIPS 2021 paper lead) |
| Source-reported input | speech |
| Source-reported output | resynthesised speech |
| Source-reported stages | self-supervised content analysis, pitch/energy analysis, timbre analysis, conditioned generator, neural vocoder |
| Candidate geometry documented | no |
| Sample rate / frame / hop / channels | not documented |
| Lookahead / latency / reset / drain | not documented |
| Voice profile fit | `unverified_candidate_geometry_absent` |

The installed v0 contract (16 kHz, mono, float32, 160 samples per frame) is
reported for boundary provenance only. It is not claimed as NANSY geometry.

## Voice profile application

`plan/swarm/VERIFICATION.md` Voice row is applied item by item in
`report.json` -> `profile_rows`, and the verifier checks every phrase of the
pinned row:

| Required item | State | Evidence |
| --- | --- | --- |
| Permitted input and target references | blocked | No permitted input speech, target voice or reference record exists |
| Task and language/speaker groups | blocked | No frozen cohort or group definition exists |
| Text and semantic content | blocked | No transcript, cohort or output exists |
| Identity and similarity | blocked | No reference/target pair and no converted output exist |
| Naturalness | blocked | No candidate output and no authorized listening or MOS exist |
| Alignment, first-output and tail timing | blocked | No runtime, chunk, lookahead, delay or device timing exists |
| Exact target condition | blocked | Only an unspecified identity-resynthesis placeholder is accepted |
| Consent, reference availability and output use | blocked | No consent, reference availability or output-use decision exists |
| Analysis-to-waveform parity | blocked | No analysis frontend, decoder, runtime or pair exists |
| Speech preservation | blocked | No paired input/output, scorer or cohort exists |
| Paired quality control | blocked | No source/weights/runtime and no comparable baseline exist |
| Numerical and nonfinite | partial harness only | Only a task-local request validator exists; no candidate output |

Every row is `qualifies=false`. There are **zero** real results and **zero**
synthetic results. The package contains no surrogate analyzer, vocoder,
feature extractor, parity number or preservation score. Such a surrogate would
not be NANSY and would add no feasibility evidence for the missing model.

## Fail-closed caller-supplied asset declaration

`asset_declaration` defines the exact shape a future caller must supply. It is
shape-checked only:

- source, weights and runtime presence must be declared absent with `null`
  revision and digest fields;
- geometry must be declared absent with `null` rate/frame/hop/channel fields;
- code, weight, training-data, input, output-use, target-voice and
  redistribution rights must be false with no review reference;
- the disposition must be `DEFER` and `qualifies=false`.

Any presence claim, set digest, invented geometry, rights claim or
qualification claim is rejected. The package cannot verify external bytes, so
it must not accept a presence claim; a future intake verifies hashes in a
separate gate. The declaration never resolves a path, imports a module, reads a
weight, opens media or runs inference.

`report.json` records **46** rejected declarations and **9** strict-JSON
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
| `RG-01` exact source revision and licence provenance | blocked | Stage the official source at an immutable revision with a tree digest and complete licence/notice/README bundle, then record independent review. |
| `RG-02` exact weights, config and weight terms | blocked | Stage every checkpoint/config/vocoder asset with per-file byte counts and SHA-256, plus reviewed weight/model-card terms. |
| `RG-03` pinned runtime, offline load and geometry | blocked | Provide a locked offline runtime with wheel hashes, install location and the exact analysis/resynthesis rate, frame, hop, channels, latency, reset and drain behaviour. |
| `RG-04` code, weight, training-data, input and output-use rights | blocked | Record reviewed code/weight/training-data/corpus terms and source/target voice consent, reference availability and output-use decisions. |
| `RG-05` reproduced analysis-to-waveform parity and preservation | blocked | Execute the pinned assets offline and record parity, tolerated reconstruction difference, speech preservation, peaks, nonfinite behaviour and exact repeats. |
| `RG-06` Voice profile against a rights-cleared cohort | blocked | Freeze a rights-cleared cohort with permitted input/target references, groups and exact target conditions, then score content, identity/similarity and naturalness separately. |
| `RG-07` alignment, timing, resources and listening | blocked | Measure alignment, first-output/tail timing, content delay, CPU, memory and callback suitability on the intended device, and complete approved blinded listening. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No schema control opens a gate. `DEFER` remains in force.

## Evidence classes and separation

| Class | Content | Admitted as result |
| --- | --- | --- |
| Source-reported paper lead | `research/category_registry.json` S35 | no |
| Source-reported survey row | `research/category_survey/sources.md` S35 | no |
| Merged sibling survey | `docs/task-evidence/survey-trn-02/report.json` family MF-M1 | no |
| Schema-only declaration control | This package's unpopulated declaration | no |
| Missing real candidate evidence | All Voice-profile rows | no |
| Sibling voice candidates | OpenVoice V2, DualVC 3, Seed-VC packages | no |

The merged survey records NANSY in family MF-M1 as
`blocked_no_checkpoint_decoder_runtime_or_target_reference` and links gap G07.
Sibling voice-conversion and content-encoder packages are distinct candidates.
No source, checkpoint, rejection count, stimulus, control or metric is
inherited or pooled.

## Scope and boundary

Only `docs/task-evidence/nansy-analysis-resynthesis/` is added. No provider
registration, descriptor, registry, default, public header, ABI, shared CMake,
CI workflow, installed-v0 behaviour, board or handoff is changed. No network
access or download is attempted. The scope gate resolves the newest merge-base
with `origin/main` (falling back to `main`), fails closed with
`scope_base_unavailable` when no base resolves, and reports
`base_out_of_scope_change:<path>` for any committed path outside this task
directory.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands, gates. |
| `LICENSES.md` | Source/asset/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, identity, geometry, assets, blockers, eight gates, declaration schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, board projection, absence probes, snippet checks, declaration validator, scope helpers, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256`, README digest tables and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, checkpoint, audio or voice input. |
| `verify.py` | Read-only strict-JSON, pin, README digest, reproduction, licensing and merge-base scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduction

Requires CPython `3.12.16`, the interpreter used for the canonical bundle, with
`PYTHONDONTWRITEBYTECODE=1`.

```sh
cd docs/task-evidence/nansy-analysis-resynthesis
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
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
<!-- digest-table: end -->

The mutable shared board `plan/swarm/TASKS.json` is **not** pinned. Only the
stable linked-row projection `{id,title,component,mode,repository,depends_on}`
is gated; mutable status, owner, claim, review, handoff, blocked-reason,
dispatch-priority and history fields are excluded.

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
| `sdk:docs/task-evidence/mp-senet/report.json` | `989c64c1c069e55d9b871f308a607669507d605247f85f614f13132efa2b010f` |
| `sdk:docs/task-evidence/nara-wpe-reference-tools/report.json` | `7ed65ec26de33815a42514b51921cc939e72fb2f57294e31e56b357f5ac87ee9` |
| `sdk:docs/task-evidence/neural-atsm/report.json` | `3dd7b111cb8af978fd5581f0ffbab6d6907e8ba2eb3e9469b19b15af72e1057b` |
| `sdk:docs/task-evidence/survey-trn-02/report.json` | `a594cd9e0c1c638835e11263c84b147b592ac1f344f0e83da4480ef310703f3a` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

Every generated artifact except this README and `SOURCES.sha256` (which cannot
pin itself) is listed with its live digest and byte count.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `08abc1b5248cd54fede251876ad78ae5f4d11b821faffefdd8eb7c210b0c72b2` | 1859 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `3affc3a5db1a69e728ab9c372f743f2930a40bf83fda12b82854dac3457b2514` | 35548 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `8d2cb89881a3ab69ae8c728fc44581ff057f3bc73bec610b7d86cefdd5fd7640` | 101745 |
| `report.json` | `bf9d7cfe29ba18ebc800b54594b59e4a3fd028b9bc985624b25e0ce74d680633` | 51898 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `8b41d247bbc9adb067f8729f60983925ea09e4f7973ba2d498bedc7ab7ad4381` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `f09d5082e28711ec096d53f0ec2facb73754cdd495f534218fc7b8696bcd3247` | 4269 |
| `test_reference.py` | `a182db25a0ef86a10d33594ddf65d85386043e993f3235b568cfa2c0ef94926f` | 16512 |
| `verify.py` | `9650b52defe6a0710f35778c88a9316e0c894a8d7693bf5280baf609ae4e3d60` | 24286 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Explicit non-claims

- No NANSY source, checkpoint, weight, config, analyzer, generator, vocoder or
  inference implementation is present, loaded, deserialised or reconstructed.
- No PyTorch, TensorFlow, ONNX Runtime or other model runtime is imported,
  installed or linked.
- No remote code, model, weight, dataset, corpus, reference voice or binary is
  downloaded.
- No analysis-to-waveform parity, speech-preservation, content, identity,
  naturalness, listening, alignment, device-timing or benchmark result exists.
- The caller-supplied asset declaration is a fail-closed shape check only; it
  is not an adapter, runtime, model or qualification.
- No provider, descriptor, registry, default, installed v0, public ABI, shared
  build or CI path is changed.
- The paper URL and survey prose are source-reported context only and are not
  measured evidence.
- No sibling voice-conversion, vocoder or analysis evidence is inherited or
  pooled as a NANSY result.
