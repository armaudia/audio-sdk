<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS - PyRoomAcoustics readiness blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local feasibility record for
`pyroomacoustics-candidate-tools` (title "Pyroomacoustics candidate tools",
mode `feasibility`, `verification_profile: tool`). It is **not** a
PyRoomAcoustics implementation, adapter, provider, room simulator or benchmark.
No source checkout, wheel, extracted package, installed module, room geometry,
RIR, excitation, array cohort, label, tool output, listening result, device
timing, benchmark or release claim is present. **No result here qualifies the
candidate.**

Pinned base: `80dc1fb371e1846a5d50f5b28c955ab92bfcbe46`.
Branch: `swarm/SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS`.
Owner: `agent-PYROOMACOUSTICS-CANDIDATE-TOOLS`.
Reviewer: `reviewer-PYROOMACOUSTICS-CANDIDATE-TOOLS`.

## Exact external blocker

The implementation board states the deliverable as verifying runnable source,
exact assets, permitted scope, task geometry and matched evidence, then adding
or reusing an SDK developer-facing adapter, fixture or tooling entry point.
Its acceptance criterion explicitly allows a readiness conclusion with an
exact external blocker instead of closing the conditional implementation.

The pinned inventory records exactly one row for this component:

> `pyroomacoustics-candidate-tools` | Pyroomacoustics candidate tools |
> Runtime and tooling | `considered` | `sdk-tool` | tool profile. Use inspected
> beamforming, RIR and room-simulation tools in reproducible benchmark recipes.

The pinned registry catalogues three PyRoomAcoustics source leads and nothing
more:

| Source | Title | Access scope | Local status |
| --- | --- | --- | --- |
| `S16` | Pyroomacoustics classical denoising implementations | direct | URL/title only; no source byte or licence |
| `S24` | Pyroomacoustics beamforming implementation | search excerpt | URL/title only; no source byte or licence |
| `S26` | Pyroomacoustics direction-of-arrival methods | search excerpt | URL/title only; no source byte or licence |

The related registry categories `CLN-01`, `CLN-04`, `CLN-07` and `CLN-08` are
all `discovery_status: catalogued` with `candidate_census_status: not_started`
and `benchmark_status: not_started`. Dereverberation screen results and online
WPE numbers in `research/dereverberation_candidates_20261028.md` and
`REALTIME_COMPONENT_CANDIDATES.md` belong to separately implemented
candidates; they are not PyRoomAcoustics runs.

The exact blocker is therefore the combination of:

1. **No exact package identity.** There is no immutable source revision, source
   digest, wheel/sdist byte, transitive runtime lock or installed location for
   the three catalogued leads. The Tool profile cannot be satisfied.
2. **No reviewed terms.** No upstream licence text, notice, per-file inventory
   or rights record is staged. A registry URL is not a reviewed dependency.
3. **No frozen room/spatial geometry.** No microphone array positions, room
   dimensions, source/target/reference conditions or timestamp calibration is
   supplied. The public SDK v0 mono path is not mapped to a multichannel array.
4. **No matched evidence.** No measured or caller-simulated RIR, excitation,
   delay/movement/noise schedule, held-out labels or separated leakage, target
   damage, channel loss and room-change results exist.
5. **No opt-in intake.** No caller-owned input rights, output-use permission or
   reviewed OFF-by-default provider/tool entry is approved.

Missing artifacts are not downloaded, reconstructed, mirrored, substituted or
inferred from adjacent WPE, beamforming, DOA or survey evidence.

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | An immutable 40-hex source revision, source SHA-256, per-file inventory and reviewed licence/notice set for the selected PyRoomAcoustics modules. |
| `BLK-02` | Exact wheel/sdist bytes, digests, transitive dependency lock and installed-package location for CPython 3.12.16 on the recorded platform. |
| `BLK-03` | A clean checkout or extracted package and one declared CLI/API use on caller-owned inputs with recorded version and install location. |
| `BLK-04` | Frozen room dimensions, microphone positions, source/target/reference conditions and timestamp calibration. |
| `BLK-05` | Frozen measured or caller-simulated RIR and condition manifests with excitation, delay/movement/noise schedule and held-out labels. |
| `BLK-06` | Reviewed input consent, RIR/corpus terms, output-use permission and an opt-in OFF-by-default entry with exact-head approval. |

**Reopen condition.** A caller supplies the exact reviewed source and licence
set, exact wheel/sdist bytes with digests and a locked runtime, a clean-checkout
Tool-profile run, frozen room/array geometry and calibration, matched RIR and
spatial evidence with separated invalidity outcomes, rights-cleared
caller-owned inputs, and an opt-in OFF-by-default tool intake with independent
exact-head review and explicit public-default approval. Until then this task
stays `DEFER`.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Catalogued denoise, beamforming and DOA tooling; RIR/room-simulation recipe lead | No execution |
| Reported input | Mono or synchronized microphone array with declared geometry | No local array input |
| Channels | 2 to 32 in the caller-tool schema | No calibrated array |
| Sample rate | 16000 Hz in the caller-tool schema | No local audio |
| Frame / hop | Not recorded for the candidate | Unverified |
| Room dimensions | Not recorded | Unverified |
| Microphone / source positions | Not recorded | Unverified |
| Timestamp calibration | Not recorded | Unverified |
| RIR identity / excitation | Not recorded | Unverified |
| Delay / movement / noise schedule | Not recorded | Unverified |
| Held-out labels | Not recorded | Unverified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | Preserved; no candidate mapping |

The synthetic geometry object in the admission schema is labelled
`synthetic_geometry_control` and `simulation_not_real_rir_evidence: true`. It
is a plain shape/validation control. It is **not** an impulse response, a
convolution, a reverberation measurement or a spatial result.

## What this package verifies

1. **Absence evidence.** 17 fixed workspace, SDK-worktree and home-cache probes
   are checked without a recursive walk. All are absent. The report builder and
   verifier fail if any later appears, so a stale absence claim cannot ship.
2. **Registry and inventory discipline.** Only the three catalogued source
   leads and the single `considered` inventory row are projected. No registry
   excerpt is promoted to a local asset, revision, licence or result.
3. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; the README digest tables are validated against live bytes, and
   `SOURCES.sha256` covers all task-local files except itself.
4. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository` and `depends_on` are projected and gated. The mutable
   `plan/swarm/TASKS.json` bytes are never hashed; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
5. **Fail-closed caller-tool validation.** A task-local schema requires exact
   source, package, runtime, room/array geometry, RIR, input, control and
   rights fields. Duplicate keys, nonfinite values, floats, unknown or missing
   fields, unsafe paths, unresolved licence, wrong interpreter, mono geometry,
   missing calibration, false controls, unconsented input, unverified rights
   and promoted simulation claims are rejected. One labelled synthetic
   geometry control is accepted to prove the validator is not blanket-rejecting;
   it is marked `qualifies=false` and is not evidence.
6. **Tool/Room/Spatial accounting.** All nine applicable requirements are
   blocked or documented as schema-only; no missing result is promoted.
7. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/pyroomacoustics-candidate-tools/` as
   `base_out_of_scope_change`. Regression tests cover sibling merges, an
   out-of-scope branch edit and a missing base ref.
8. **Canonical regeneration.** Three cold-start regenerations must produce
   byte-identical `contract.json`, `report.json`, sidecar, sources manifest and
   README bytes.

## Tool, room and spatial profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Record version, install location and provenance | blocked | Three registry leads only; no package revision or install. |
| Verify a clean checkout or extracted package | blocked | No source checkout, wheel or extracted package. |
| Exercise one typical CLI/API use on caller-owned inputs | blocked | No runnable source, runtime or caller-owned input set. |
| Exercise malformed inputs and missing optional selections | documented | Schema-only rejection cases; no candidate API invoked. |
| Separate compile/build, synthetic runtime and measured workload | blocked | No build, runtime or workload evidence for the candidate. |
| Freeze room geometry, layout and timestamp calibration | blocked | No calibrated array or room geometry is staged. |
| Freeze render/reference or measured RIRs and conditions | blocked | No RIR byte, excitation or condition manifest is staged. |
| Separate leakage, target damage, channel loss and room change | blocked | No measurement and no held-out labels exist. |
| Keep permissions and intended-use rights independent | blocked | No source, RIR, corpus or output-use rights record. |

## Matched-evidence boundary

`delay-and-sum-beamformer`, `mvdr-beamforming`, `offline-multichannel-wpe`,
`online-multichannel-wpe`, `survey-cln-07` and `survey-cln-08` are separate
components with their own fixtures, rooms, scores and blockers. Their synthetic
fixtures, WPE screens, survey metrics and timings are not PyRoomAcoustics
results and are not inherited. In particular, the dereverberation screen's
identity/SI-SDR/STOI/RTF values and the online WPE RTF are not evidence for
this candidate.

## Reproduction

The canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, the report sidecar, the
README digest tables and `SOURCES.sha256` three times and requires
byte-identical output. `verify.py` is read-only and writes only to a temporary
directory. Repository checks are the installed-package `python scripts/ci.py`,
`python -m reuse lint` and `git diff --check`.

## Source pins

<!-- digest-table: source -->
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio_categories.md` | `97a3c7e61e0d66f2c3ab18f1dde8661afa2d74a40eb4f46315d95da50c4ff905` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/search_log.jsonl` | `61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `07cd997cfc114ba3f625bb2c397cf12e1fdb12636c2a04557abb9ec2abbe0f77` | 2045 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `349c1170e5219614622fdc27c881a2dfadb504fbb59f3ee9bd2fe1892f8751e1` | 14958 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `30f619cfced47b7d9d9124f40e264223513c4da6e7da21097c9df64c2df87bf1` | 67197 |
| `report.json` | `15d18469e1932a777d0b4636eeedbe0931354ca501ca945bf709e98c9f569353` | 32338 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `9be16c5ee4e24fc90d401530d14a3ae3a643d7086a14e19e938032c83ee6968f` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `5d6260938638dcd46739f743f9f53ca0fad94d21f09e61bf12cef2621ba5badc` | 3368 |
| `test_reference.py` | `09d462dcece2cb1a564136f34a56ffc0ffc1d420c63e0928d4d93e43321755b5` | 23420 |
| `verify.py` | `892d800e449df5a713eafbf7916bea0543d17bfc3130eb1b1b1df4bdffa10c67` | 26832 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.
