<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FSMN-VAD — FSMN VAD source, checkpoint, runtime and analysis blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local evidence for the FSMN VAD
feasibility row. It is **not** an FSMN-VAD implementation. No FunASR source
checkout, checkpoint, weight, config, feature asset, runtime, adapter, corpus,
probability vector, event vector, real audio, listening result, device
measurement, benchmark or release claim is present. **No result here qualifies
FSMN VAD.**

The structured inventory marks `fsmn-vad` as `evidence_status=blocked` with the
**Analysis** acceptance profile (`verification_profile: analysis`,
`plan/INVENTORY.json`) and the plan note "Separate bidirectional/offline results
from framewise availability." The row asks for runnable source, exact assets,
permitted scope, task geometry and matched evidence before a caller-supplied
asset reference and an opt-in adapter; none of those prerequisites exists
locally.

## Exact external blocker

The exact **source**, **checkpoint bundle**, **isolated runtime**, **rights
record** and **analysis cohort** are all absent. The pinned VAD register
(`research/plans/F02/vad_sources.md`) records FunASR FSMN-VAD as:

> checkpoint ID `iic/speech_fsmn_vad_zh-cn-16k-common-pytorch`; official
> streaming guide documents ordered stateful chunks and start/end sentinel
> events. Toolkit MIT does not establish checkpoint rights; exact model
> revision/hash/terms remain missing, and chunk finalization adds buffering.

The pinned candidate matrix records the wider row as
`unavailable/blocked`: "No exact candidate weights, source checkout, or adapter
are staged in the checked local stores/environments." The pinned VAD/ASR and
segmentation reports record no local model, adapter or accuracy evaluation. The
noise-suppression census is pinned as adjacent context only; it does not provide
an FSMN-VAD artifact.

Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count, SHA-256, sample rate or hop is asserted as
verified. The sparse declared `16k` is name-derived and is explicitly marked
unverified in `report.json` → `geometry`.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout (`ART-01`) | FunASR at an immutable 40-hex commit, with the reviewed upstream license text, a per-file SHA-256 manifest and the streaming VAD entry point identified |
| Checkpoint bundle (`ART-02`) | `iic/speech_fsmn_vad_zh-cn-16k-common-pytorch` (or a caller-pinned variant) at an immutable 40-hex revision, including every weight, config, feature asset, model card and terms file with byte count and SHA-256 |
| Runtime (`ART-03`) | A locked, reproducible isolated Python and native/ONNX runtime with exact interpreter and package versions, a lock SHA-256, an offline load path and a recorded host profile |
| Rights (`ART-04`) | Reviewed toolkit, checkpoint and model-card terms, training-data provenance, corpus rights, output use and redistribution; toolkit MIT does not establish checkpoint rights |
| Cohort (`ART-05`) | A frozen rights-cleared speech/nonspeech cohort with continuous truth, scored regions, preserved unknown spans, condition strata, known positives and negatives, timestamps and held-out splits |
| Analysis results (`ART-06`) | Independent timestamped probabilities, event boundaries and detections, quiet/active speech, idle noise, onset/offset delay, stratified FN/FP, validity separation, independent state, exact source intervals, availability, dropped/stale events and cross-hop behavior |

The machine-readable records are `report.json` → `source_probe`,
`weights_probe`, `runtime_probe`, `absence_evidence`, `required_artifacts`,
`exact_blockers`, `analysis_profile` and `gates`, and `contract.json` carries
the same disposition, pins, geometry and eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** Reviewed planning records, both censuses, the candidate
   matrix, the evidence reports, the category registry and the SDK boundary
   files are pinned by SHA-256. These are read-only provenance inputs, not model
   evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local caller-supplied-asset bundle
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted entries, unresolved
   tokens, non-integral or out-of-range integers, unsupported sample rates,
   non-mono or non-streaming geometry, undeclared chunk finalization,
   non-offline runtimes, unconsented items and false rights are rejected. One
   synthetic structural control is accepted to prove the validator is not
   blanket-rejecting; it is labelled `synthetic_schema_control` and
   `qualifies=false`.
5. **Analysis profile accounting.** Every Analysis requirement is recorded as
   **blocked** with `qualification_effect=none`; no real-model metric exists.
6. **READ digest tables.** The `source`, `boundary` and `artifacts` digest
   tables are parsed and checked against the live pinned files and byte sizes.
7. **Merge-base scope gate.** `verify.py` resolves the newest merge-base against
   `origin/main`/`main` and fails closed as `scope_base_unavailable` or
   `base_out_of_scope_change` when the branch diff leaves this task directory.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, `.gitattributes` and
   `scripts/ci.py` are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No FSMN-VAD provider is
   installed or registered; no descriptor, default, ABI, shared build, CI, board
   or handoff change is made.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` → `analysis_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Score timestamped probabilities | blocked | No FSMN-VAD probability vector or timestamp grid exists. |
| Event boundaries and detections | blocked | No start/end sentinel events or detection list is produced. |
| Quiet and active speech | blocked | No real condition-labelled speech exists. |
| Idle noise | blocked | No real idle-noise item exists. |
| Known positives and negatives | blocked | No rights-cleared known item exists. |
| Onset and offset delay | blocked | No source interval or decision time exists. |
| Stratified FN/FP | blocked | No continuous truth or scored region exists. |
| Separate validity from nonspeech | blocked | No validity state or unknown span is defined. |
| Independent state | blocked | No recurrent state or fresh-session parity exists. |
| Exact source intervals | blocked | No hop, window or timestamp base is pinned. |
| Availability, dropped/stale events | blocked | No target runtime or deadline measurement exists. |
| Cross-hop behavior | blocked | No hop or chunk schedule exists. |

## Task geometry

| Field | Record |
| --- | --- |
| Task kind | `neural_streaming_voice_activity_endpoint_detection` |
| Upstream toolkit | FunASR |
| Candidate family | FSMN streaming VAD |
| Model identifier | `iic/speech_fsmn_vad_zh-cn-16k-common-pytorch` |
| Declared rate | 16 kHz (name-derived; **not verified**) |
| Channels | mono (not verified) |
| Streaming | ordered stateful chunks with start/end sentinel events |
| Buffering | chunk finalization adds buffering (declared) |
| Hop / lookahead / threshold | unresolved; no geometry pinned |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-FSMN-VAD`, `77d7800cac82899eb02a8aa55535d00e4faa8946` |
| Task | `SDK-FSMN-VAD` |
| Task mode | `feasibility` |
| Acceptance profile | `analysis` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Write scope | `docs/task-evidence/fsmn-vad/` only |
| Provider registration, default, ABI, CI | none |

## Admission contract (task-local; not an SDK, FunASR or VAD contract)

The schema is `audio-sdk/fsmn-vad-reference-bundle/0.1`. It requires an exact
40-hex source revision, SPDX license and license SHA-256, caller-owned weight
files with SHA-256 and byte counts, a reviewed-terms flag, a locked offline
runtime, mono 16 kHz streaming geometry with a positive hop and declared chunk
finalization, a consented cohort with known conditions and held-out splits, all
declared conditions and outcomes, and all rights cleared. Admission never reads
audio, loads weights or invokes a model, and the accepted control never
qualifies.

## Reproduction

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FSMN-VAD/docs/task-evidence/fsmn-vad
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FSMN-VAD diff --check
```

`run.py` writes `contract.json`, canonical `report.json`, `report.json.sha256`,
the README artifact table and `SOURCES.sha256` three times and requires all
three cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift,
out-of-scope change, missing sidecar, missing SPDX header, stale README digest or
absent blocker. It also gates this branch's merge-base diff so committed
out-of-scope files cannot pass.

## Blocker map

| Blocker | Artifact | Linked gates | State |
| --- | --- | --- | --- |
| `BLK-01` | `ART-01` | `RG-01`, `RG-04` | open: exact FunASR source absent |
| `BLK-02` | `ART-02` | `RG-01`, `RG-04` | open: exact checkpoint absent |
| `BLK-03` | `ART-03` | `RG-04`, `RG-07` | open: pinned runtime absent |
| `BLK-04` | `ART-04` | `RG-01`, `RG-03` | open: rights unresolved |
| `BLK-05` | `ART-05` | `RG-02`, `RG-05` | open: analysis cohort absent |
| `BLK-06` | `ART-06` | `RG-02`, `RG-05`, `RG-06`, `RG-07`, `RG-08` | open: analysis results absent |

## Remaining gates (eight blocked)

1. `RG-01` exact FunASR source revision, checkpoint digest, byte count, weight
   format and configuration.
2. `RG-02` rights-cleared frozen cohort with continuous truth, preserved unknown
   spans and held-out splits.
3. `RG-03` toolkit, checkpoint, training-data, corpus, output-use and
   redistribution rights.
4. `RG-04` pinned source, checkpoint, runtime and verified sample rate, hop,
   feature frontend, lookahead and threshold policy.
5. `RG-05` timestamped probabilities, event boundaries, detections, onset/offset
   delay and stratified FN/FP.
6. `RG-06` independent state, exact source intervals, availability,
   dropped/stale events and cross-hop behavior.
7. `RG-07` target-device pacing, availability delay, memory and finite drain.
8. `RG-08` opt-in provider intake and independent exact-head review.

**Reopen condition.** Pin the exact licensed FunASR source and FSMN-VAD
checkpoint at immutable revisions with per-file digests and reviewed terms;
admit an isolated hash-pinned runtime; clear toolkit/checkpoint/training-data/
corpus rights; reproduce exact probability and event output; qualify a
rights-cleared task-matched cohort with unknown spans preserved; measure target
timing; and complete opt-in provider intake. Until then the candidate stays
**DEFER**, **incomplete** and **not qualified**.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py`, by the README digest-table check and by the test
suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/plans/F02/vad_sources.md` | `374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact pins (SHA-256)

Task-local artifacts generated by `run.py`. `README.md` and `SOURCES.sha256`
are excluded to avoid circular self-pinning.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `7e74484619b65a7c6a302e23537f66c7a7d9636aef807536cf1c6661843466fb` | 1901 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `9796bf043b343ad94978c070dc3444422fd817d12c4d40c193e459b4bb47fce6` | 32604 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `f414baf81f87fb107a7263335de6a58d5fc95cb136ac0891b0ac57a77cfae55c` | 86431 |
| `report.json` | `1e354bcae3e0f7ef39fc7ac3d34778e50e446a4d2845129b3131f558cdcaeec3` | 45165 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `5d65632d9360a78fecf647e32af6449dabdad8b9b91ad6945e3eb2a4a380032a` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `889693fb9dd0bc36a2ea4cf4224483db37f0fe391a7e5cf2d8adaa138b5f0346` | 6153 |
| `test_reference.py` | `7c92c2c898e708ec35c4566f7910f14b342a0f0e7349ae2783a6bf771dfee827` | 29538 |
| `verify.py` | `d98313f9970ef85fd0bc962d4b49283071e8aed26d6138556921ce3ece1df2e6` | 31717 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->
