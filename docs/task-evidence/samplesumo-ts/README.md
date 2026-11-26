<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SAMPLESUMO-TS - SampleSumo TS vendor boundary and readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`SampleSumo TS` (`component_id=samplesumo-ts`, mode `external-adapter`).
Acceptance profile is **Rate**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before any opt-in
adapter exposure; `status=incomplete`, `proposal_only=true` and
`qualification.status=not_qualified`. A missing, blocked or rejected result can
never qualify the candidate.

No runnable SampleSumo TS SDK, source tree, release tag, binary, install
location, artifact identity, published pricing, licence text, evaluation
entitlement, locked offline runtime, processed data or vendor output exists at
any probed path. This package records that exact external blocker, pins the
evidence that does exist, validates a caller-supplied tool-manifest reference
by shape only, and applies the Rate profile to a deterministic integer position
envelope. It is **not** a SampleSumo TS adapter: nothing is downloaded, copied,
vendored, resolved, imported, linked, loaded or executed. Only this task-local
directory is added.

## Exact external blocker

The catalogued record (`plan/INVENTORY.json`, `id=samplesumo-ts`) is
`considered`, `disposition=external-adapter`, `verification_profile=rate`, area
`Rate and content`, finding:

> Pricing/terms not published; procurement

Its only evidence link is
`cpp-library/pipeline-validation/playback-speed-candidates.md`, line 876:

> Commercial time-varying actuator | SampleSumo TS | Commercial | Explicitly
> documents time-varying factor, push/pull, mono/stereo, desktop/iOS |
> Pricing/terms not published; procurement

The same document (section 14.3) says SampleSumo TS is the commercial option
that advertises this use case and a better functional match for a first quote,
"though pricing is unknown". That is a source-reported capability description,
not measured evidence. The exact blocker is therefore: **no approved,
identity-pinned, rights-cleared SampleSumo TS runtime and no published terms,
matched Rate evidence or vendor output**. Missing artifacts are not downloaded,
reconstructed, mirrored, substituted or inferred from adjacent vendor evidence.

Six open blockers:

| Blocker | Missing artifact and requirement |
| --- | --- |
| `BLK-01` | Immutable source or signed binary release with byte counts and SHA-256 values. |
| `BLK-02` | Published pricing and licence/evaluation/telemetry/deployment/output-use text with procurement review. |
| `BLK-03` | Locked offline runtime with platform build, dependency lock, deterministic settings and install digest. |
| `BLK-04` | Verified rate/frame/hop/reset/drain and push/pull contract matched to the installed 16 kHz mono float32 160-sample geometry. |
| `BLK-05` | Rights-cleared cohort, candidate output and matched Rate controls with separated evidence classes. |
| `BLK-06` | Device-independent structure review, pacing/resource evidence, independent review and release approval. |

**Reopen condition.** A caller supplies approved procurement and entitlement,
the exact SampleSumo TS release with verified artifact identity and published
terms, a locked offline runtime, a reviewed caller tool-manifest with the
installed geometry and a rate/hop/reset/drain contract, a rights-cleared cohort
with matched Rate evidence and separated local/vendor/claim results, timing and
resource records, and a separate OFF-by-default provider intake with
independent exact-head review. Until all eight gates clear, the adapter stays
unregistered and this task stays `DEFER`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-SAMPLESUMO-TS`, `56eeb134b740d41d770940bf47bd0f035d73f097` |
| Task mode | `external-adapter` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before opt-in adapter exposure |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz, mono, `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/drain geometry asserted |
| Surrogate | fixed 19,200-sample integer position envelope |
| Provider, default, ABI, CONTRACTS, registry, shared build, CI | unchanged |
| Downloads, real audio, listening, device timing, benchmark, release claim | none |

The installed geometry is checked against pinned bytes in `CONTRACTS.md`
(`v0 accepts only 16000/1/160 ...`) and `api/include/audio_sdk/provider_v0.h`
(`AS_SAMPLE_RATE_HZ 16000u`, `AS_CHANNELS 1u`, `AS_FRAME_SAMPLES 160u`,
`float *samples`). No candidate mapping is inferred from those installed facts.

## Rate profile application

The Rate row in `plan/swarm/VERIFICATION.md` is applied item by item in
`report.json` -> `rate_profile`; every row has `qualifies=false`:

| Requirement | Status | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No candidate runtime, source interval or output position exists. |
| Duration | blocked | No candidate output; envelope targets are exact by construction. |
| Pitch | blocked | No candidate audio and no authorized listening result. |
| Transient audibility | blocked | No candidate audio and no transient control result. |
| Playback buffering | blocked | No device, scheduler, fill/flush or deadline measurement. |
| 1x control | synthetic only | Integer identity map 19200 -> 19200, not audio passthrough. |
| Rate changes | synthetic only | Five integer position maps only; no step or ramp execution. |
| Unfamiliar speech | blocked | No rights-cleared speech cohort or candidate output. |
| Music | blocked | No rights-cleared music and no negative control. |
| Silence | synthetic only | Empty duration is rejected; no candidate silence behaviour. |
| Rebuffer, drift, final partial | synthetic only | Position arithmetic only; no playback or buffering. |
| Pause/filler and speech preservation | blocked | No speech, timestamps, policy execution or preservation measure. |
| Separate evidence categories | documented | Synthetic, manifest, source-reported and missing-real classes stay distinct. |

## Caller-supplied tool-manifest reference

`reference.py` defines strict schema `audio-sdk/samplesumo-ts-tool-manifest/0.1`
and a fail-closed shape validator. A caller manifest must declare exact vendor
and product identity, local absence of source/runtime/artifacts, a release,
platform build, absolute install root, artifact and terms SHA-256 values,
artifact byte count, telemetry disclosure, no downloads, 16 kHz mono `float32`
160-sample format, bounded numerator/denominator, reviewed rights with
`claims_qualified=false`, unique allowed controls and `qualifies=false`.

The validator never resolves an install root, reads a key, opens audio, imports
a module or loads a vendor artifact. An accepted manifest is only a synthetic
shape control with `qualifies=false`. all 50+ malformed cases are rejected:
missing or extra keys, wrong schema/request IDs, wrong candidate identity,
claimed presence or revisions, bad release/build/digests/sizes, relative or
traversal paths, enabled downloads, 8 kHz or stereo input, `float16`, wrong
frame size, out-of-range rates, false rights, invalid controls and any
qualification claim. A strict JSON loader rejects duplicate keys, nonfinite
constants, non-ASCII, BOM, trailing data, empty input and non-object roots.

## Integer envelope and absence controls

Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
Envelope input is 19,200 source samples; target is
`(input*denominator)//numerator`; output index `j` maps to source
`(j*numerator)//denominator`; the mapping digest is SHA-256 over ASCII lines
`"{output_index},{source_index}\n"`. Five cases: `1/1 -> 19200`,
`5/4 -> 15360`, `3/2 -> 12800`, `4/5 -> 24000`, `9/10 -> 21333`. All maps are
monotone, bounded and exact in duration error. The synthetic frame fixture uses
160 integer numerators `((index*37) % 201 - 100)` over denominator 128, peak
numerator 100. No sample is rendered as audio.

A fixed 13-path probe list checks workspace, SDK-worktree and home-cache
locations for a candidate checkout, model, env, adapter, runtime, artifacts or
weights without a recursive walk. All are absent; the report builder fails if
any later appears. Source phrase checks and boundary pin checks read exact
pinned bytes only.

## Release gates (all blocked)

| Gate | Reopening condition |
| --- | --- |
| `RG-01` source/runtime identity | Stage an immutable release with byte counts, SHA-256 values and published terms; record independent review. |
| `RG-02` pinned offline runtime | Provide locked host, build, install root, dependency lock, install digest and no-download proof. |
| `RG-03` permitted scope and manifest | Supply reviewed rate/frame/hop/reset/drain geometry and 16 kHz mono `float32` 160-sample admission. |
| `RG-04` rights | Record procurement, licence, telemetry, data-handling, deployment and redistribution grants. |
| `RG-05` absence controls | Keep every candidate artifact absent until pinned; prove placeholders and sibling evidence cannot qualify. |
| `RG-06` Rate profile | Run every Rate row on a rights-cleared cohort with separated local, vendor-output and claim results. |
| `RG-07` timing and listening | Measure pacing, backpressure, memory and delivery for the exact runtime; complete authorized listening or a labeled screen. |
| `RG-08` intake and release | Open a separate OFF-by-default intake with clean-install proof and independent exact-head review. |

No synthetic envelope, admission control or source-reported capability opens a
gate.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, blockers, counts, commands and gates. |
| `LICENSES.md` | Boundary: no vendored third-party text, code or bytes. |
| `contract.json` | Machine-readable contract: pins, blockers, gates, Rate rows, manifest schema and disposition. |
| `reference.py` | Stdlib-only strict JSON, board projection, absence probes, snippet checks, manifest validator, integer envelope and canonical report. |
| `run.py` | Byte-identical regeneration of contract, report, sidecar, README tables and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of pinned inputs and task-local files. |
| `test_reference.py` | Deterministic tests, including three scope-gate regression tests; no skips or network. |
| `verify.py` | Read-only strict verifier with newest-merge-base task-local scope enforcement. |
| `*.license` | REUSE sidecars for generated JSON and digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned audioml workspace root. The mutable
shared board `plan/swarm/TASKS.json` is never pinned; only the stable linked-row
projection `{id,title,component,mode,repository,depends_on}` is gated.

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
<!-- digest-table: source-end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree and are unchanged.

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: boundary-end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `5df22f408fdd60bb46616ef3fd4e56d3068adc046959051fb65dec943888d358` | 1098 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `276ad753926a7d62ea9b60b92538571afe7bb9b6669579399ddf4426a3c8aafb` | 10791 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `d2083a0b7b26270e8065dbf24f8219a74ea0b56585ab83d87d793edd709c3d25` | 48129 |
| `report.json` | `5e7c17de493b17bbd8157466d39b8c5172ac1c06ce1d267d192430d6e2b9aa6f` | 20342 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `c7d62714d3f1be8e95ae253cd863152e0e138a856d0c13bba9ab42ec41b134e7` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `bb5720b64a360dac0b69d1def10ec4d3102fffecafc3f44b5f60b8f04da024e1` | 4706 |
| `test_reference.py` | `f1c03d82a3b1d1c5b1d649fbe7803f24036c49e9eb78e04ede8fbb1971c88b85` | 15050 |
| `verify.py` | `8738b56c70bab38357368155bd800daadd553bb8598f679cd4e10418db9ca8c4` | 23939 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

Expected final line: `PASS verify.py ...`. The verifier is read-only and
performs a fresh three-run cold-start regeneration in a temporary directory.
Repository checks: installed-package `python scripts/ci.py`, `python3 -m reuse
lint` and `git diff --check`.

Scope enforcement resolves the newest merge-base against `origin/main`, then
`main`. An unresolved base emits `scope_base_unavailable`; a committed path
outside `docs/task-evidence/samplesumo-ts/` emits
`base_out_of_scope_change:<path>`. Later sibling additions on the base branch
do not become this branch's changes.

## Explicit non-claims

- No SampleSumo TS source, binary, SDK, key, licence text, runtime or asset is
  present, downloaded, imported, linked or executed.
- No real audio, corpus, consent, listening, device timing, pacing or benchmark
  measurement exists.
- No rate, duration, pitch, transient, preservation or quality result is
  claimed; all source capabilities remain source-reported.
- The integer envelope is protocol plumbing only, not a model, renderer, rate
  estimator, audio output or qualification.
- The adapter is OFF and unregistered; no provider, descriptor, registry,
  default, installed v0, public ABI, CONTRACTS, shared build or CI path changes.
