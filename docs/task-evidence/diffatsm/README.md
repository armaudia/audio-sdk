<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DIFFATSM - DiffATSM source, checkpoint, runtime and rights blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DiffATSM` (`component_id=diffatsm`). The acceptance profile is **Rate**,
assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `status=incomplete`, `proposal_only=true` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed DiffATSM source, PPG extractor, diffusion checkpoint,
vocoder, runtime, immutable revision and output are **absent**. The recorded
upstream repository states that the full implementation will be released after
publication and currently publishes only an abstract, citation, planned code
structure and dependencies. This package records that exact blocker, applies
the Rate profile to a bounded deterministic integer position envelope, and
makes no rate, time-scale-modification, quality, latency, listening, benchmark
or release claim. It is **not DiffATSM**: no PPG model, diffusion model, weight
file, native library, real audio, corpus, model, device clock or upstream code
is present, copied, downloaded, loaded, imported or executed. Only this
task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=diffatsm`) is `blocked`,
`disposition=sdk-model`, `verification_profile=rate`, area `Rate and content`,
with the finding:

> **Not runnable as released:** no complete executable
> implementation/checkpoint available. It is an audio renderer candidate, not a
> standalone lightweight rate estimator.

Its only evidence link is `research/tsm-followup-20261101/README.md`, line 36.
The same row records "Repository/release inspected" and "Raw-audio diffusion
TSM, not a rate-only model". The follow-up report adds that the official
repository README states the full implementation will be released after
publication and currently provides only an abstract/citation, planned code
structure and dependencies.

A second research record,
`research/speech-rate-tsm-evaluation-20261101.md` line 29, names the repository
`https://github.com/shjang-97/DiffATSM`, says the official repository reports
the full implementation as forthcoming, and identifies the method as raw-audio
time-scale modification with phonetic posteriorgrams and diffusion
postprocessing. `agent-text/REPORT.md` line 48 repeats that description.

Consequently:

- no DiffATSM source tree, commit, release tag, `COPYING`/`NOTICE`, license
  text or model card is staged at any probed path;
- no PPG extractor, acoustic model, diffusion checkpoint, vocoder, inference
  config, dependency lock, byte count or SHA-256 exists for DiffATSM;
- no runtime, interpreter lock, accelerator, device, dtype, diffusion step
  schedule, seed or padding recipe is pinned;
- no weight, code, training-data, derived-output or redistribution term is
  reviewed;
- no real speech, corpus, consent, held-out split, candidate output, duration,
  pitch, transient, preservation or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DIFFATSM`, `fe0b37a0d0b8b70054cc55f301a83108abdeba77` |
| Task mode | `feasibility` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/PPG/diffusion geometry asserted |
| Surrogate | fixed 19,200-sample integer position envelope |
| Provider registration, default, ABI, CI | none |

The surrogate maps declared source sample counts to output positions with exact
integer arithmetic. It is **not DiffATSM**, synthesizes no audio and cannot
qualify the candidate. The catalogued rate profile is itself a poor fit: the
candidate is an audio renderer, not a rate-only estimator, so no rate estimate
can be produced even if a renderer were released.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` -> `rate_profile`, and every item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No candidate source, runtime or output; only a synthetic integer position map exists |
| Duration | blocked | No candidate output; synthetic targets are exact by construction |
| Pitch | blocked | No candidate output and no listening result |
| Transient audibility | blocked | No candidate output and no listening result |
| Playback buffering | blocked | No device, scheduler, fill/flush or deadline measurement |
| 1x control | synthetic only | Integer identity map `19200 -> 19200`, not audio passthrough |
| Rate changes | synthetic only | Position maps only; no step or ramp audio execution |
| Unfamiliar speech | blocked | No rights-cleared audio |
| Music | blocked | No rights-cleared music and no negative control |
| Silence | synthetic only | Empty/zero duration is rejected; no candidate behaviour |
| Rebuffer, drift, final partial | synthetic only | Position arithmetic only; no playback or buffering |
| Pause/filler and speech preservation | blocked | No speech, VAD, timestamped policy or preservation measure |
| Separate evidence categories | documented | Synthetic, admission, source-reported and missing-real sections stay distinct |

Every real-result row is `qualifies=false`. Synthetic exactness means only that
the integer fixture is self-consistent.

## Synthetic envelope and admission

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Envelope input: 19,200 source samples; target
  `(input*denominator)//numerator`; output index `j` maps to source
  `(j*numerator)//denominator`.
- Mapping digest: SHA-256 over ASCII lines `"{output_index},{source_index}\n"`.
- Five cases: `1/1 -> 19200`, `5/4 -> 15360`, `3/2 -> 12800`,
  `4/5 -> 24000`, `9/10 -> 21333`. Every duration error is `0` samples.
- Identity `1/1` is exact and bounded. All maps are monotone and remain inside
  the source interval.
- The synthetic frame fixture uses 160 values
  `((index*37) % 201 - 100)/128`, peak `0.78125`.

Measured synthetic observations (all unqualified):

| Item | Value |
| --- | ---: |
| Envelope cases | 5 |
| Identity case | 19200 -> 19200 |
| Maximum target | 24000 |
| Duration error, all cases | 0 samples |
| Invalid manifest rejections | 49 |
| Strict JSON rejections | 9 |
| Absence probes | 14, all absent |
| Source snippets verified | 7 |
| Real candidate results | 0 |

The envelope proves integer position plumbing and strict admission on synthetic
metadata. It proves no renderer, PPG extraction, diffusion step, vocoder
output, rate estimate or qualification.

## Adverse, missing and invalid handling

`report.json` records **49** rejected manifests, each rejected before any
candidate state could exist. Rejections include missing/extra sections and
keys, bad schema/request IDs, online mode, candidate source/weight/runtime
claims, a non-null revision or license, non-boolean flags, 8 kHz input, stereo,
zero/oversized/non-integer sample counts, `f16`, `finite=false`, `NaN` /
`Infinity` / negative / over-one / non-canonical peaks, zero or non-reduced
rates, out-of-bounds `1/3` and `3/1` speeds, wrong output count, malformed or
mismatched mapping digests, wrong source bounds, missing/duplicate/unknown
controls, `claims_qualified=true`, and missing/extra/empty rights fields.
Missing real recordings, weights, checkpoints, runtime outputs and labels are
`blocked`, never passes.

The strict JSON loader rejects duplicate keys, `NaN`, `Infinity`, `-Infinity`,
trailing data, byte-order marks, non-object roots, empty input and truncated
documents.

The caller manifest contract validates declaration identity only. It never
reads, loads, imports or executes a source tree, PPG model, checkpoint,
vocoder or runtime. A hash-matched placeholder is never accepted as the pinned
DiffATSM artifact.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Stage the DiffATSM source at an immutable revision with complete license, notice and README records, then record independent review. |
| `RG-02` pinned diffusion runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and exact inference settings. |
| `RG-03` checkpoint, PPG and diffusion assets | blocked | Stage every PPG, diffusion, vocoder and config file and verify each byte count and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze a permitted, digest-pinned input set with corpus, evaluation, derived-output and redistribution decisions plus weight and training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned assets offline and record output hashes, finite/length preservation, exact repeats and peak/RSS. |
| `RG-06` Rate profile against the real runtime | blocked | Run every Rate-profile case on a rights-cleared cohort with 1x, rate changes, silence, rebuffer, drift and the final partial window. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode/platform separately with timing, resources and pacing, and complete authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission or envelope control opens a gate.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands, gates. |
| `LICENSES.md` | Source/asset/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, source-reported identity, artifacts, blockers, eight gates, Rate rows, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, board projection, absence probes, snippet checks, admission validator, integer envelope, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks; no skips, network, runtime, checkpoint or audio. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/speech-rate-tsm-evaluation-20261101.md` | `525a25c12753ea7fad71aa7101b2c872d5511813fd0ea9b18231b347a8fda96d` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:research/tsm-followup-20261101/agent-text/REPORT.md` | `86657ba0d2c82d64110dc058f40082e2d701ce0ff2427fe2e0d3a3f1719bfd93` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
<!-- digest-table: end -->

The mutable shared board `plan/swarm/TASKS.json` is **not** pinned. Only the
stable linked-row projection `{id,title,component,mode,repository,depends_on}`
is gated; mutable status, owner, claim, review and handoff fields are excluded.

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Reproduction

Requires CPython `3.11.5`, the interpreter used for the canonical bundle.

```sh
cd docs/task-evidence/diffatsm
python3 reference.py            # print the canonical report
python3 run.py all              # 3x byte-identical regeneration
python3 -m unittest -v test_reference.py
python3 verify.py               # strict read-only verification
```

Expected final line: `PASS verify.py ...`. `run.py` writes only this directory.
`verify.py` performs a fresh three-run cold-start regeneration in a temporary
directory and compares the committed bytes.

## Explicit non-claims

- No DiffATSM source, repository snapshot, PPG extractor, diffusion
  checkpoint, vocoder, config or inference implementation is present.
- No remote code, model, weight, dataset or binary is downloaded.
- No candidate inference, time-scale modification, rate estimate, duration,
  pitch, transient, preservation, listening, device or benchmark result exists.
- The integer envelope is protocol plumbing only and is not a model, a
  renderer, a rate estimator or a qualification.
- No provider, descriptor, registry, default, installed v0, public ABI, shared
  build or CI path is changed.
- The research prose and repository URL are source-reported context only and
  are not measured evidence.
