# SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE — Rate-profile fixture

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the Rate-profile role of `bookbot/distil-wav2vec2-adult-child-cls-37m`: a
**caller-supplied frozen feature extractor** plus a small ridge head predicting
**measured syllables/second**. The model's adult/child classification head is
not used. Nothing here predicts age, listener preference, a preferred speed
factor, or a TSM speed setting.

No model weights, checkpoint, tokenizer, real audio, human labels, download,
network access, device timing or listening test is used. The installed v0
geometry is untouched: **16 kHz, mono, float32, 160 samples/call**.

## Scope and honesty

- Status: `proposal_only_synthetic_incomplete` / `not_qualified`.
- `no_missing_result_qualifies_candidate=true`.
- Conceptual boundary is unregistered, `enabled_by_default=false`,
  `descriptor_settings={}`; no public API/ABI/default/registry/build/CI/board change.
- The caller owns the frozen extractor. This fixture only validates the caller's
  vectors, fits a standardized ridge regressor on deterministic synthetic
  syllable-rate labels, and emits rate events. An identity extractor control
  proves vectors are returned unchanged; a reversed-vector control shows the
  expected failure when the caller identity does not match the head.
- All scores below are from matched synthetic features and labels. They are
  wiring/regression evidence, **not** an accuracy estimate for real speech.

## Pinned research context (quoted, not reproduced)

`research/tsm-followup-20261101/README.md` line 31 documents a prior external
evaluation of this checkpoint as a frozen encoder plus a ridge rate head:
MAE **.741** syll/s, RMSE **.929**, r **.768**, mean **157 ms** per 4 s clip,
Apache-2.0, **37.9M** parameters / **151.5 MB** weights. The fixture records
these values under `model.documented_context_not_reproduced` with
`reproduced_here=false`. No exact revision, artifact hashes, permission or
local execution backs them here; this PR does not reproduce, confirm or extend
that result.

## Missing requested evidence

The original task prompt also referenced:

- `ml-audio-research-experience.md` — **missing in accessible workspace**.
- `research/speech_intelligence_20261028.md` — **missing in accessible workspace**.

Both remain recorded in `report.json["missing_evidence"]`; no bytes were pinned
or reused from either.

## Boundary model

One timestamped event per four-second synthetic analysis window (400 frames of
160 samples, 64,000 samples). Each event carries exact half-open source sample
intervals as decimal strings, `available_ns` on `fixture-monotonic-v0` with
origin `1767225600000000000`, a finite nonnegative
`rate_syllables_per_second`, the matched synthetic label, stratum, feature
digest and explicit `validity`. `known` events are scored; `unknown` events are
retained but never scored as zero or as a different label; malformed events are
rejected. Epoch, source position and session-key checks cover stale/restart
isolation, disjoint sessions and cross-hop interval coverage.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | Scope, pins, reproduction, results and gates. |
| `reference.py` | Caller extractor protocol, validation, standardization, ridge fit, five-fold CV, metrics, controls and report builder. |
| `run.py` | Regenerates `report.json` and `report.json.sha256` from pinned Python; accepts a scratch output path. |
| `report.json` | Canonical machine-readable Rate-profile report. |
| `report.json.sha256` | Digest of committed `report.json`. |
| `SOURCES.sha256` | SHA-256 manifest for pinned external/worktree/task-local files. |
| `test_reference.py` | Deterministic unittest suite (no skips, no network). |
| `verify.py` | Read-only verifier: pins, strict JSON, reproduction, SPDX, scope and excluded claims. |
| `adapter.json` | Task-local proposal-only adapter descriptor; unregistered, OFF by default. |

## Pinned source/boundary digests

| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Reproduction

From this directory, with pinned Python 3.12.16 (regeneration may be done to a
scratch path so tracked outputs stay untouched):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE
```

Committed digest:
`f8db5bebd2c250491dba150e9dea0c54790f81f583f02660c71ce7ca37b526e6`.

## Expected deterministic results (synthetic only)

- Cohort: seed 20261124, 210 four-second windows, 5 contiguous folds of 42;
  16-dimensional caller vectors; labels `round(latent_rate * active_seconds) /
  active_seconds` in syllables/second; strata clean/short_active/overlap/
  quiet_boundary. Features and labels share the latent rate but use independent
  noise streams; no audio or human syllable judgements exist.
- Head: StandardScaler + Ridge(alpha=10), intercept unregularized, fitted only
  on the four training folds. No model weights are loaded or executed.
- OOF nonnegative MAE **0.276553** syll/s, RMSE **0.333761**, bias
  **+0.003060**, r **0.966856**; raw predictions are identical here (zero
  negatives).
- Held-out fold (42 windows) nonnegative MAE **0.290807**, RMSE **0.336658**,
  bias **−0.006137**, r **0.969427**. Constant train-mean control:
  MAE **3.141010**, RMSE **3.423863**.
- Identity control: 1,260 extractor calls, 210 distinct caller vectors, all
  returned bitwise unchanged, no internal model. Adverse reversed-vector
  control with the same claimed identity: MAE **1.625632**, r **−0.890098**
  (expected failure, worse than identity).
- Rejection results: **17/17** invalid or missing inputs rejected, including
  missing/unfrozen extractor, `None`/NaN/inf vectors, wrong dimension and
  non-numeric vector, missing/NaN/nonpositive label, nonfinite rate,
  non-decimal/empty/misaligned interval, stale epoch and invalid validity.
  Unknown validity is retained but not scored.
- State/cross-hop: disjoint session keys, exact half-open intervals over 400
  frames, stale epoch rejected, reset epoch accepted.

These numbers must not be compared with the pinned research numbers as if this
fixture reproduced them; they validate the local wiring and failure policy.
No real accuracy, runtime, preference or product claim follows from them.

## Gates / reopening conditions

| Gate | Status | Reopen condition |
| --- | --- | --- |
| `model_revision_and_rights` | blocked | Pin exact revision/hashes, confirm Apache-2.0 terms and authorized execution; never redistribute unverified weights. |
| `real_frozen_extractor_and_head` | blocked | Run the real caller-supplied frozen extractor with the classification head unused and a head fitted on cleared data. |
| `rights_qualified_labeled_audio` | blocked | Freeze a permitted, speaker-disjoint cohort with independently checked syllable-rate labels. |
| `external_accuracy_generalization` | blocked | Score the exact artifact/head on a reviewed corpus with MAE/RMSE/r and baselines; synthetic CV is insufficient. |
| `preferred_speed_claim` | blocked | Collect preference/acceptability labels and a separately reviewed rate-to-speed policy. |
| `target_runtime_timing` | blocked | Measure the exact installed build under pacing/load/deadline budgets; 157 ms is quoted context, not local timing. |
| `provider_intake` | blocked | Opt-in provider intake after model/data/runtime gates clear; OFF default and empty descriptor settings. |

No gate is satisfied. No missing result qualifies the candidate.
