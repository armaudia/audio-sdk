<!-- SPDX-FileCopyrightText: 2026 Hovhannes Tsakanyan -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS — feasibility DEFER evidence

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`.** This directory is bounded, deterministic,
task-local evidence for `SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS`. It is
**not** an ASR/STT/translation implementation, not a runtime, not a model,
not a provider registration, not a benchmark, and not a release claim.

## Exact blocker

No exact runnable ASR/translation runtime, model artifact, tokenizer/language
pack, rights/output-use grant, typed transcript/segmentation/unknown-language
contract, matched cohort, scorer, or target-runtime timing evidence is present
in this worktree. Bounded checks found no staged runtime/artifact under this
task directory and no qualifying local evidence. A hash-matched caller manifest
still fails closed as `ASR_TRANSLATION_RUNTIME_IDENTITY_UNPINNED`.

## Board/inventory linkage (stable identity only)

The mutable full `plan/swarm/TASKS.json` and `plan/INVENTORY.json` are **never**
hashed. Only stable linked-row identity fields gate this package:

| Link | Stable SHA-256 |
| --- | --- |
| board row `SDK-SPEECH-RECOGNITION-TRANSLATION-CONTROLS` | `2dbd125fb0ee6425959db51dd2772e385fd968a6450e5b181242c69452fd90ff` |
| inventory `speech-recognition-translation-controls` | `597efdd515a4decd605f8568f7e38b6271c2808441e5b96bc5c1a37cea8cfcfd` |

Mutable fields excluded: `status`, `owner`, `claim`, `review`, `handoff`,
`blocked_reason`, `dispatch_priority`, `history`, `write_scope`,
`deliverable`, `acceptance`, `evidence`.

## Scope / non-claims

- Installed v0 unchanged: 16 kHz, mono, float32, 160 samples/frame.
- No provider registration, no default, no public API/ABI/shared build/CI change.
- No ASR/translation/diarization/alignment runtime imported, downloaded, loaded, or executed.
- No weights, corpus, transcript, audio, or translation artifact vendored.
- No real transcription/translation/timestamp/confidence/language-ID result.
- No device timing, listening, benchmark, or release claim.
- Synthetic controls are structural only and cannot qualify.

## Release gates (all blocked)

| Gate | Status | Qualifies |
| --- | --- | --- |
| RG-01 exact runtime/artifact and rights identity | blocked | false |
| RG-02 typed transcript and normalization contract | blocked | false |
| RG-03 segmentation clock and endpoint semantics | blocked | false |
| RG-04 unknown language and translation scope | blocked | false |
| RG-05 frozen cohort, controls, and scorers | blocked | false |
| RG-06 adverse/invalid/nonfinite/missing handling | blocked | false |
| RG-07 paced timing and target runtime | blocked | false |
| RG-08 opt-in intake, review, and release | blocked | false |

## Required artifacts to reopen

1. Exact pinned runnable ASR/translation runtime/artifact (revision, bytes, SHA-256, reviewed rights/output-use).
2. Typed transcript/segment/confidence/unknown-language/versioned-normalization contract.
3. Exact segmentation clock, partial/final/end-of-stream semantics, and source timestamp mapping.
4. Rights-cleared matched cohort with references, controls, and pinned scorers.
5. Deterministic adverse coverage: missing/invalid/malformed/nonfinite/out-of-range/rights-missing.
6. Paced target-runtime latency/resource/deadline measurements.
7. Separate opt-in default-OFF intake with independent exact-head review and release approval.

## Reproduce

```sh
cd docs/task-evidence/speech-recognition-translation-controls
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

## Canonical artifacts

- `report.json` — machine-readable DEFER report.
- `report.json.sha256` — `sha256  report.json`.
- `contract.json` — stable contract with blocked gates, blockers, pins, invariants.
- `SOURCES.sha256` — pinned local/source/boundary digests.
- `reference.py` / `run.py` / `verify.py` / `test_reference.py` — stdlib-only deterministic tooling.
