# SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE — deterministic synthetic evidence

Task-local, **proposal-only**, **incomplete**, and **not qualified** evidence for
a head-only ridge adult/child classifier reference over deterministic synthetic
embeddings representing `bookbot/distil-wav2vec2-adult-child-cls-37m` encoder
outputs. No model weights, no real audio, no download, no network, no device, no
listening test, and no public benchmark are used.

## Scope and honesty

- Status: `proposal_only_synthetic_incomplete` / `not_qualified`.
- `no_missing_result_qualifies_candidate=true`.
- Conceptual provider is unregistered, `enabled_by_default=false`, `descriptor_settings={}`.
- No public API/ABI/default/registry/build/CI/board/shared-source change.
- Installed v0 boundary untouched: **16 kHz, mono, float32, 160 samples/call**.
- Evidence is deterministic synthetic only; it does not qualify real model quality, runtime, or deployment.

## Missing requested evidence

Task prompt asked to consult:
- `ml-audio-research-experience.md` — **missing in accessible workspace**; not pinned, not reused.
- `research/speech_intelligence_20261028.md` — **missing in accessible workspace**; not pinned, not reused.

Both are recorded in `report.json["missing_evidence"]`. Their absence blocks any stronger claim.

## Public boundary model

The fixture models a task-local analysis boundary at v0-shaped cadence: one
timestamped event per synthetic clip with exact half-open source sample
interval, decimal-string `source_first_sample`, `source_last_sample_exclusive`,
`epoch`, and `available_ns` on `fixture-monotonic-v0` with origin
`1767225600000000000`. Events carry `prob_child`, `prob_adult`, predicted label,
ground-truth label, stratum, and explicit `validity`. Invalid analysis is
rejected; `unknown` validity is retained but excluded from FN/FP counting and is
never relabeled as nonspeech/adult/child.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | Scope, pins, reproduction, results, gates. |
| `reference.py` | Deterministic cohort, ridge fit, calibration, metrics, validity/state/cross-hop, report builder. |
| `run.py` | Regenerates `report.json` and `report.json.sha256` byte-for-byte. |
| `report.json` | Canonical machine-readable Analysis report. |
| `report.json.sha256` | Digest of committed `report.json`. |
| `SOURCES.sha256` | SHA-256 manifest for pinned external/worktree/task-local files. |
| `test_reference.py` | Deterministic unittest suite (no skips, no network). |
| `verify.py` | Read-only verifier: pins, strict JSON, reproduction, SPDX, scope. |
| `adapter.json` | Task-local proposal-only adapter descriptor; unregistered, OFF by default. |

## Pinned source/boundary digests

| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Reproduction

From this directory, with pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE
```

## Expected deterministic results

- Cohort: seed 20261124, 120 train + 60 held-out synthetic clips, 20 frames/clip, 16-dim embeddings, labels adult/child, strata clean/boundary_quiet/noisy_overlap/short_utterance.
- Ridge head: lambda 0.001, train-only fit, logistic probability for child class.
- Calibrated threshold selected by held-out balanced error over 0.05..0.95 grid; default 0.5 control retained.
- Controls: always-adult and always-child degenerate classifiers.
- Validity: invalid out-of-range probability, empty interval, invalid validity tag, stale epoch rejected; unknown retained but not counted as nonspeech.
- State/cross-hop: session key disjointness, cross-hop clip interval coverage, stale epoch rejection, reset epoch acceptance.

See `report.json` for exact metrics, stratified FN/FP, onset/offset delays, regressions, gates, and digests.

## Gates / reopening conditions

| Gate | Status | Reopen condition |
| --- | --- | --- |
| real_model_weights_and_runtime | blocked | Pin exact model revision/license/hashes/runtime and execute real head-only inference on approved runner. |
| rights_qualified_labeled_audio | blocked | Freeze permitted labeled adult/child/nonspeech/unknown cohort with independent scoring. |
| calibration_and_threshold_validation | blocked | External calibration/operating-point validation on independently reviewed permitted cohort. |
| target_runtime_timing | blocked | Paced target-device deadline/CPU/memory measurement of exact installed build. |
| provider_intake | blocked | Opt-in provider intake review with OFF default and empty descriptor settings. |

No gate is satisfied. No missing result qualifies the candidate.
