<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PODCASTFILLERS — PodcastFillers non-commercial annotations blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`podcastfillers` (title "PodcastFillers"). Decision: **DEFER** before any
implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. No result qualifies.

The evidence source
([`playback-speed-candidates.md`](../../../../cpp-library/pipeline-validation/playback-speed-candidates.md))
records PodcastFillers annotations as **non-commercial** and states the useful
part is the VAD+ASR+classifier pipeline, not the data. The inventory row
requires annotating the documented rights scope and keeping research dataset
acquisition outside the SDK artifact. The task row assigns the **Rate** profile.

This package does **not** contain, download, load, execute, or acquire
PodcastFillers data, audio, annotations, models, runtimes, classifiers, VAD,
ASR, or any inference path. It records pinned claims, probes fixed
candidate intake/cache paths to evidence absence, defines a fail-closed
admission boundary for a future rights-cleared manifest, implements
deterministic synthetic filler-span accounting controls, and records explicit
blockers/gates. Only `docs/task-evidence/podcastfillers/` is written.

## Profile mismatch and exact acceptance scope

The task row and `plan/swarm/VERIFICATION.md` assign the **Rate** acceptance
profile. Rate requires source/output mapping, duration, pitch/transient
audibility, playback buffering, 1× and rate changes, unfamiliar speech/music/
silence, rebuffer/drift/final partial window, and source-timestamp-tied
pause/filler decisions with speech preservation. PodcastFillers is a
dataset/annotation lead, not a renderer/playback controller. Every Rate row is
recorded as **blocked**. A future review must supply Rate evidence for a
composite path that contains a renderer, or record an explicit reviewed waiver.

## Exact external blockers

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Exact PodcastFillers dataset identity/version/commit/digest and complete terms bundle with independent rights review; research acquisition remains outside SDK artifact. |
| `BLK-02` | Rights-cleared or separately licensed audio/annotation subset with explicit commercial/output-use decision; non-commercial annotations cannot train/evaluate a shipped model. |
| `BLK-03` | Pinned offline runtime/model identities, digests, deterministic settings, and clean-room offline load trace if any pipeline is reproduced. |
| `BLK-04` | Reproduced filler detection/boundary metrics with frozen scorer, exact accounting, finite/adverse/missing-input rejection, and matched controls on rights-cleared cohort. |
| `BLK-05` | Rate-profile evidence or reviewed waiver, plus target-device paced timing/resources for any runtime path. |
| `BLK-06` | Separate versioned OFF-by-default opt-in intake with exact descriptor/config, clean-install proof and independent exact-head review after all prior gates clear. |

## Recorded claims: provenance only

| Field | Recorded value |
| --- | --- |
| Source URL | `https://podcastfillers.github.io/` |
| Annotations license | Non-commercial (separate terms) |
| Pipeline note | VAD + ASR + classifier (pipeline idea only; not data) |
| Commercial use | Not permitted for shipped model training/evaluation without separate reviewed decision |
| Dataset identity/digest/terms | Not recorded/staged |
| Measured result | Not recorded/reproduced |

## What this package verifies

1. **Source/recipe pins.** Candidate note, inventory row, Rate profile, SDK plan,
   and merged VAD/segmentation sibling packages are pinned by SHA-256. The
   mutable shared board is not hashed; only stable linked-row identity gates.
2. **Absence evidence.** Fixed candidate intake/cache probes are checked (no
   recursive walk). All must be absent; report/verify fail closed if present.
3. **Admission boundary.** A strict, task-local manifest schema rejects
   malformed/missing/invalid/nonfinite/duplicated/out-of-range/non-integral
   cases before any state change. One structural control is admitted as
   `synthetic_schema_control_not_evidence` with `qualifies=false`.
4. **Deterministic synthetic arithmetic.** A stdlib-only filler-span scorer
   computes precision/recall/F1 and boundary MAE/median/within-50ms on synthetic
   spans. It emits no audio and has no model input; it is arithmetic, not a
   result.
5. **Rate/quality/timing accounting.** Every Rate, quality and timing row is
   blocked with explicit evidence.
6. **Boundary preservation.** Contracts, public v0 headers, CMake, REUSE, CI,
   SDK README, and merged VAD/segmentation sibling packages are pinned and
   verified unchanged.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; others are SDK-worktree
relative. `SOURCES.sha256` pins these plus task-local artifacts and excludes its
own bytes.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | PodcastFillers rights/pipeline note |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Inventory row, Rate profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `docs/task-evidence/webrtc-vad/report.json` | `762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb` | Merged VAD sibling boundary |
| `docs/task-evidence/bayesian-information-criterion-speaker-segmentation/report.json` | `daf1213b91b1887178ef50b9be4496c9b95c1407c78701d4910529f37c844023` | Merged segmentation sibling boundary |

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, blockers, provenance, pins, commands, gates. |
| `LICENSES.md` | Apache-2.0 package; no vendored third-party dataset/model assets. |
| `contract.json` | Machine-readable contract: models, pins, artifacts, blockers, 8 gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, admission validator, synthetic scorer, canonical report. |
| `run.py` | Byte-identical regeneration of contract/report/sidecar/SOURCES, repeated three times. |
| `report.json` | Canonical report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime, no audio). |
| `verify.py` | Read-only verifier: profile, pins, report, absence, gates, licensing, scope, 3 cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/podcastfillers` with Python 3.12 (stdlib only):

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

## Release gates (all blocked)

| Gate | Status | Reopen condition |
| --- | --- | --- |
| `RG-01` dataset identity and terms provenance | blocked | Pin exact dataset identity/version/commit/digest and stage complete terms with independent rights review. |
| `RG-02` noncommercial annotations and commercial use decision | blocked | Provide written commercial/output-use decision or separately licensed rights-cleared data reviewed independently. |
| `RG-03` pinned runtime/model and offline load | blocked | Provide exact model/runtime identities, digests, deterministic offline settings and clean-room load trace. |
| `RG-04` rights-cleared cohort and acquisition boundary | blocked | Stage rights-reviewed cohort manifest outside SDK artifact acquisition paths with reviewed terms and provenance. |
| `RG-05` filler detection accuracy with controls | blocked | Reproduce accuracy with frozen scorer, exact accounting, finite checks, and matched controls on rights-cleared cohort. |
| `RG-06` rate profile condition coverage | blocked | Supply Rate-profile evidence or reviewed waiver with separate source references and timestamp-tied preservation accounting. |
| `RG-07` target runtime timing/resources and deadlines | blocked | Measure exact paced target-device timing/resources on intended workload with p50/p95/p99 and fill/flush behavior. |
| `RG-08` provider intake public surface and release | blocked | Open separate versioned OFF-by-default opt-in intake with exact descriptor/config, clean-install proof and independent exact-head review after all prior gates clear. |

No gate is closed. `decision=DEFER`, `status=incomplete`,
`qualification.status=not_qualified`.
