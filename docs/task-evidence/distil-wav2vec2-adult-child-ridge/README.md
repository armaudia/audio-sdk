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
  syllable-rate labels, and emits rate events. The strict path checks the claimed
  model id/revision, requires every returned vector to be bitwise identical to
  the caller vector, and checks each vector against its pinned cohort digest.
  Wrong model id/revision, permuted returns and digest mismatches are rejected;
  the reversed-vector regression is scored only outside the strict path as an
  explicitly unaccepted adverse control.
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
160 samples, exactly 64,000 samples). Each event carries exact half-open source
sample intervals as canonical unsigned decimal strings, `available_ns` on
`fixture-monotonic-v0` with origin `1767225600000000000`, a finite nonnegative
`rate_syllables_per_second`, the matched synthetic label, stratum, feature
digest and explicit `validity`. Validation rejects signed/leading-zero/float
interval strings, a span other than 64,000 samples, frame-misaligned endpoints,
and an `available_ns` that is not `origin_ns + end * 62500`. `known` events are
scored; `unknown` events are retained but never scored as zero or as a different
label; malformed events are rejected. Three-event hop chains in two disjoint
sessions are checked for 400-frame spans, zero gaps and zero overlaps. Epoch,
source position and session-key checks cover stale/restart isolation and
disjoint sessions.

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

From this directory, with the canonical regeneration interpreter Python
3.12.16 (regeneration may be done to a scratch path so tracked outputs stay
untouched):

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DISTIL-WAV2VEC2-BOOKBOT-DISTIL-WAV2VEC2-ADULT-CHILD-CLS-37M-RIDGE
```

`reference.py` (via `run.py`/`verify.py`) requires Python 3.10 or newer; the
exact pinned regeneration version is 3.12.16. Canonical serialization rounds
floats to nine decimal places and treats a constant predictor's correlation as
undefined, so committed bytes are stable on Python
3.10.13/3.11.5/3.12.16 (all three produced the same SHA-256 below). Source pins
resolve from `SOURCE_ROOT`, defaulting to the workspace five parents above this
directory; set `SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml` to
override. The plan checker reads the board outside this worktree; it does not
modify it.

Committed digest:
`ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4`.

## Expected deterministic results (synthetic only)

- Cohort: seed 20261124, 210 four-second windows, five contiguous folds of 42;
  16-dimensional caller vectors; labels `round(latent_rate * active_seconds) /
  active_seconds` in syllables/second; strata clean/short_active/overlap/
  quiet_boundary. Features and labels share the latent rate but use independent
  noise streams; no audio or human syllable judgements exist.
- Head: StandardScaler + Ridge(alpha=10), intercept unregularized. Alpha is
  fixed before any split; folds 0–3 are calibration/OOF only, fold 4 is a
  reserved evaluation fold. The final head is fitted on the 168 calibration
  windows only; no evaluation label is used for fitting, alpha choice or a
  baseline constant. No model weights are loaded or executed.
- Calibration OOF (168 windows) nonnegative MAE **0.271706** syll/s, RMSE
  **0.335911**, bias **+0.003442**, r **0.965619**; raw predictions are
  identical here (zero negatives).
- Reserved evaluation fold (42 windows) nonnegative MAE **0.290807**, RMSE
  **0.336658**, bias **−0.006137**, r **0.969427**. Constant calibration-mean
  control: MAE **1.197024**, RMSE **1.368579**, r undefined (constant vector).
- Identity control: 882 extractor calls over 210 distinct pinned caller
  vectors, all returned bitwise unchanged, no internal model. Wrong
  model id/revision, permuted returns and digest mismatches are rejected by the
  strict path. The unaccepted reversed-vector regression scores MAE **1.625632**,
  r **−0.890098** (expected failure, worse than identity).
- Rejection results: **24/24** invalid or missing inputs rejected, including
  missing/unfrozen/misidentified extractors, `None`/NaN/inf vectors, wrong
  dimension and non-numeric vector, caller-vector identity/digest mismatches,
  missing/NaN/nonpositive label, nonfinite rate, signed/non-decimal/empty/
  misaligned/short intervals, `available_ns` mismatch, stale epoch and invalid
  validity. Unknown validity is retained but not scored.
- State/cross-hop: disjoint session keys, two three-window hop chains with
  400-frame exact half-open intervals, zero gaps and zero overlaps, stale epoch
  rejected, reset epoch accepted.
- Portability: unittest includes three cold starts, a runtime-guard test and a
  cross-version canonical-byte check; report SHA-256 matched on Python
  3.10.13, 3.11.5 and 3.12.16.

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
| `target_runtime_timing` | blocked | Measure the exact installed build under pacing/load/deadline budgets; 157 ms mean / 222 ms p95 are quoted context, not local timing. |
| `rate_profile_condition_coverage` | blocked | Score 1×/rate-change/unfamiliar speech/music/silence/rebuffer/drift/final partial window with separate source references. |
| `source_output_mapping_and_preservation` | blocked | Measure source/output mapping, duration, pitch/transients, playback buffering, preservation and timestamp-tied pause/filler decisions for a reviewed rate policy. |
| `provider_intake` | blocked | Opt-in provider intake after model/data/runtime gates clear; OFF default and empty descriptor settings. |

No gate is satisfied. No missing result qualifies the candidate.
