<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-STREAMING-CONFORMER-TED — Streaming Conformer-TED feasibility evidence

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for Streaming Conformer-TED / FastConformer
(`component_id=streaming-conformer-ted`). The Rate acceptance profile is
defined in `plan/swarm/VERIFICATION.md` and assigned by `plan/INVENTORY.json`.
Base commit: `14af17740bf8c571f9a985c88fd56f5b5b8e8ae8`; branch:
`swarm/SDK-STREAMING-CONFORMER-TED`; reviewer:
`reviewer-STREAMING-CONFORMER-TED`. Decision: **DEFER** before
`opt_in_adapter_exposure`. No missing, blocked or synthetic result qualifies the
candidate.

## What this package does and does not do

This package records the exact blocker state and models a **caller-supplied
asset boundary** and the installed SDK geometry: **16000 Hz**, **mono**,
**float32**, **160-sample frames**. The geometry probe uses deterministic
in-memory float32 frames only. The caller manifest validator checks adapter
identity, geometry, absolute asset paths, byte counts, SHA-256 values and
required source/checkpoint/config/runtime/license identity fields, then fails
closed with `CANDIDATE_IDENTITY_UNPINNED`. No asset is loaded or executed.

No Streaming Conformer-TED or FastConformer source, checkpoint, streaming
config, runtime, binary, corpus or audio asset is vendored, downloaded,
imported, loaded or run. Fixed absence probes found no candidate artifact and
no executable/runtime is staged. No real audio, rights-cleared cohort, fixed
transcript, WER/latency scorer, listening panel, device timing, benchmark
result or release claim is present. No provider, descriptor, registry, default,
ABI, `CONTRACTS.md`, shared build or CI behavior is changed. The only write
scope is `docs/task-evidence/streaming-conformer-ted/`.

## Source evidence

Pinned source records identify the candidate as unavailable/blocked:

- `research/voice-enhancement-20261101/candidate_matrix.csv:36` records
  `Streaming Conformer-TED / FastConformer` as `unavailable/blocked`: "No exact
  TED checkpoint, streaming config or local ASR runtime; using another Conformer
  would change candidate identity."
- `research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md:11`
  records the same blocker disposition.
- `research/voice-enhancement-20261101/agent-segmentation/REPORT.md:53` records
  "researched but not run" and notes NeMo cache-aware FastConformer/RNNT as an
  analogue only. That analogue is **not** the exact TED candidate and no NeMo
  asset is present here.

No source-reported WER, latency or streaming quality number is present for the
exact candidate. Source rows are read-only evidence, not qualification.

## Exact readiness conclusion and reopen conditions

All Rate gates are blocked. The concrete external blockers are:

- **XB-01** — no exact Streaming Conformer-TED source revision, TED checkpoint,
  streaming config, local ASR runtime or rights-reviewed license bundle.
  Reopen by staging an exact licensed source revision, TED checkpoint, streaming
  config and runtime with immutable digests, notices and rights review.
- **XB-02** — no rights-cleared matched cohort, fixed transcript policy,
  WER/scoring protocol, control or baseline. Reopen by freezing the cohort,
  transcript policy, controls and scorer, then running the exact candidate on
  real inputs.
- **XB-03** — no real streaming output, source/output mapping, timestamp,
  memory, pacing or target-runtime availability evidence. Reopen by executing
  the pinned runtime on target hardware and recording mapping, state, memory and
  deadline evidence.
- **XB-04** — no opt-in intake, OFF-default decision, independent exact-head
  review or board transition. Reopen by completing separate opt-in intake with
  default OFF and obtaining independent exact-head approval before any exposure.

Gate coverage: `RG-01` exact source/checkpoint/runtime identity; `RG-02` rights
and license clearance; `RG-03` matched cohort and transcript protocol; `RG-04`
streaming ASR quality and preservation; `RG-05` source/output mapping and final
partial; `RG-06` alignment/state/memory/target timing; `RG-07` opt-in intake
and OFF public default; `RG-08` independent exact-head review. Every gate is
`blocked`, `qualifies=false`.

## Evidence classes

| Class | Present here | Qualifies |
|---|---:|---:|
| Pinned source rows / inventory record | yes | no |
| Synthetic 16 kHz mono float32 geometry | yes | no |
| Strict manifest/JSON/pin rejection controls | yes | no |
| Real local model/runtime output | no | no |
| Real audio / matched cohort / transcript score | no | no |
| Listening or authorized predictive score | no | no |
| Device timing / memory / deadline | no | no |
| Benchmark or release claim | no | no |

Adverse controls: 18 caller-manifest cases, 7 strict-JSON cases and 5 pin-parser
cases are all rejected. The geometry cover is exact: two full 160-sample frames
plus a 5-sample final frame with 155 zero-padding samples cover samples
0..324 with no overlap or gap. This is an integer in-memory probe only, not a
measured content delay. Identity control repeats a synthetic frame byte-for-byte
and does not qualify.

## Reproduction

Use a pinned Python 3.12 interpreter with bytecode disabled. From the SDK
worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s docs/task-evidence/streaming-conformer-ted -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/streaming-conformer-ted/run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/streaming-conformer-ted/run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 docs/task-evidence/streaming-conformer-ted/verify.py
python3 -m reuse lint
git diff --check
```

`run.py --all` regenerates `report.json`, its SHA-256 sidecar, `SOURCES.sha256`
and `contract.json` in sorted order. It never writes outside this directory.
`run.py --check` and `verify.py` are read-only; `verify.py` also checks README
digest tables, license sidecars, source/boundary pins, duplicate-key and
nonfinite JSON, canonical bytes, the newest-merge-base branch-diff scope,
`git diff --check` and three fresh report builds. The scope verifier uses the
newest merge-base of `HEAD` with an available `origin/main` or `main` ref,
emits `scope_base_unavailable` when neither ref exists, and emits
`base_out_of_scope_change:<path>` for any changed path outside
`docs/task-evidence/streaming-conformer-ted/`.

## Source-digest table

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary-digest table

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifacts and licensing

`report.json` is the canonical evidence report. `report.json.sha256` is its
SHA-256 sidecar. `SOURCES.sha256` pins the read-only source and boundary files
plus the task-local artifacts. `contract.json` binds the same decision, gates,
blockers and artifact pins. `.license` sidecars cover all generated JSON and
SHA-256 files; `LICENSES.md` records that no third-party candidate artifact is
vendored. REUSE coverage remains the unchanged aggregate `docs/**` rule in
`REUSE.toml`.
