<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-WEBRTC-VAD — task-local synthetic VAD analysis evidence

**Status: `proposal_only_not_qualified`; qualification `incomplete`; decision
`DEFER` before any processor exposure.**
This package is a deterministic, fully synthetic VAD *surrogate* at a
task-local, protocol-v1-shaped analysis boundary. It is **not** WebRTC VAD, not
a wheel download, not a licensed runtime, not an SDK provider, not a registered
descriptor and not a release or accuracy qualification. No public API/ABI,
`CONTRACTS.md`, shared `CMakeLists.txt`, descriptor registry, default, installed
v0 behavior, board, handoff, ruleset, main branch or other worktree was
changed. Installed v0 remains 16 kHz mono `float32`, 160 samples.

Pinned base: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`. Branch:
`swarm/SDK-WEBRTC-VAD`. All files live only under
`docs/task-evidence/webrtc-vad/`.

## Exact scope and boundary

- Boundary anchor: public adapter `adapters/webrtcvad-wheels/adapter.json`,
  identity `webrtcvad-wheels-2.0.14.post1`, which declares 16 kHz mono and
  **320-sample/20 ms** frames. The frozen SDK v0 uses **160-sample/10 ms**
  frames. That divergence is recorded; **no numeric parity** with the wheel or
  with historical source-reported AMI figures is claimed.
- The local identity is `webrtc-vad-synthetic-reference-v1`. It produces
  timestamped `speech_probability` events and advisory `speech_event` runs on
  exact half-open source intervals, with epoch, session, sequence, validity,
  availability clock and an explicit rejection/drop audit.
- Probabilities are an **uncalibrated logistic surrogate** of frame RMS and
  zero-crossing rate from deterministic integer synthesised waveforms. They
  are not WebRTC posteriors, not calibrated confidences and not a control
  signal. Decision rule is `probability >= 0.5` with one synthetic hangover
  frame; both settings are frozen in `fixture.py`.
- The historical wheel adapter's README, lock file and `run.py` are pinned as
  provenance only. They are never installed, imported or executed; no wheel,
  binary, model weight or licensed asset is present in this package.
- `provider.json` is a proposal-only manifest: `registered: false`,
  `default_enabled: false`, `processor_exposure: false`, `decision: DEFER`.
  There is no C boundary, no opt-in consumer and no native parity crosscheck.
- All detections are advisory: they never gate audio, never alter PCM and are
  never promoted by a missing, rejected, stale or unrun result.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests and
`verify.py` fail closed on a missing or changed pin; there is no substitution,
pooling or tolerance.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `reports/vad-research/chaining-evaluation.md` | `f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234` |
| `adapters/webrtcvad-wheels/adapter.json` | `beb429aadd4927a981af3b8c12a5a0cc2e79979ca0f65b8b73257d1b0a98886c` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `adapters/webrtcvad-wheels/run.py` | `814147bf1c2a27872b63dd79412cd4865ecff3a9fdede347a0230eca44615306` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

The mutable board snapshot (`plan/swarm/TASKS.json`,
`721c972afbce171752475a1f082f822b29b59c31cd22b3534124d481530f724a` at read
time) is provenance only and never gates this evidence. Source-reported AMI
values for WebRTC (FN 7.31%, FP 49.54%; 6.38 µs/20 ms frame) remain historical
and are **not** reproduced, pooled or used as an oracle.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` → `acceptance_profile`, and each item is verified by
`verify.py`:

| Required item | Evidence |
| --- | --- |
| Timestamped probabilities | 100 exact source-interval events, Brier and log-loss reported |
| Event boundaries | 3 truth runs matched by overlap; onset/offset delay in samples and ms |
| Detections | TP/FN/FP/TN by sample, overall and per frozen stratum |
| Quiet and active speech | `quiet-a`, `quiet-b`, `active-a` strata |
| Idle noise | `idle-a/b/c/d` and `noise-burst` strata |
| Known positives/negatives | 4,800 speech samples, 9,600 nonspeech samples |
| Onset/offset delay | `quiet-a` +480/−0 samples; `active-a` 0/0; `quiet-b` missed |
| Stratified FN/FP | `quiet-a` FN 480, `quiet-b` FN 800, `noise-burst` FP 320 |
| Validity separate from nonspeech | 1,600 unknown samples excluded; invalid never scored as negative |

Also verified: independent session state, exact source intervals, strict
availability monotonicity, explicit dropped/stale/nonfinite/missing cases and
cross-hop projection. No missing result qualifies a candidate.

## Method

1. `fixture.py` synthesises 16,000 samples (1 s) from integer arithmetic: a
   fixed 64-entry waveform table, a deterministic LCG noise source and a frozen
   segment table. Samples are quantised to int16 and exposed as `float32 / 32768`.
2. Nine frozen truth segments cover quiet speech, active speech,
   below-threshold quiet speech, idle noise, a loud noise burst and an
   explicitly unknown tail. Segment boundaries are all multiples of 160
   samples, so every event has one unambiguous source label.
3. `reference.py` drives a 160-sample session. Each accepted frame emits one
   probability record with `start_sample`, `end_sample`, `probability`,
   `decision`, `validity`, epoch, sequence and availability. Known events use
   `available_ns = origin_ns + end_sample × 62500 + 5,000,000` on clock
   `webrtc-vad-fixture-monotonic-v0`; unknown events carry no availability and
   no decision.
4. Contiguous known decisions form advisory speech events with one hangover
   frame. A run closes at the first inactive frame and becomes available at
   that frame's end; an unterminated run closes on drain.
5. `scorer.py` scores probabilities (Brier/log-loss), weighted confusion,
   per-stratum FN/FP and overlap-matched boundaries. Unknown samples are
   excluded; invalid records are rejected before scoring.
6. `run.py --report` generates the report three times, requires byte-identical
   payloads, and only then writes `report.json` and `report.json.sha256`.
   `--sources` and `--crosscheck` are likewise deterministic and are checked
   across three cold-start subprocess repeats by `verify.py`.

## Canonical report and digests

`report.json` is canonical JSON (sorted keys, compact separators,
`allow_nan=False`, LF, one trailing newline, 47,071 bytes).

| Name | SHA-256 |
| --- | --- |
| `report.json` file / canonical digest / sidecar | `762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb` |
| Fixture spec | `b57b86c959d6b6f16dcc8f09ce3c15d0409a0d5479fd3a79b90785f060d4d530` |
| Crosscheck payload | `e44c3040aaea8325133d149bbba9fb3a0e0af3f7bd94b892badb285985708f53` |

Local artifact digests are in `SOURCES.sha256`; `contract.json` pins the code
and JSON artifacts independently. All comparisons are exact.

## Results (synthetic only)

100 frames / 16,000 samples, 90 known events (14,400 samples) and 10 unknown
events (1,600 samples), 3 advisory speech events, 0 invalid admissions.

| Metric | Exact value |
| --- | ---: |
| TP / FN / FP / TN (samples) | 3520 / 1280 / 320 / 9280 |
| Speech miss rate (FN / 4800) | 0.266666666667 |
| False-alarm rate (FP / 9600) | 0.033333333333 |
| Brier score | 0.068882732117 |
| Log loss | 0.187664190183 |
| Mean probability (known) | reported in `report.json` |

Stratified detections: `quiet-a` TP 1120 / FN 480, `active-a` TP 2400,
`quiet-b` FN 800, `noise-burst` FP 320 / TN 480, `idle-a` TN 800, `idle-b` TN
800, `idle-c` TN 800, `idle-d` TN 6400. Unknown-tail contributes to no
denominator.

Boundaries: `quiet-a` truth `[800,2400)` matched by `[1280,2400)` (onset
+480 samples / +30 ms, offset 0); `active-a` `[3200,5600)` matched exactly
(0/0); `quiet-b` `[6400,7200)` missed. One false event `[6080,6400)` arises
from the synthetic noise-burst hangover. Positive onset means a late start;
negative offset would mean an early stop. These are source-coordinate effects,
not device or availability latency.

## Failure controls (all exact; failures recorded as failures)

- **Invalid vs nonspeech:** invalid/missing validity, nonfinite and
  out-of-range probabilities are rejected by both session and scorer. An
  unknown event is admitted to the audit but excluded from all denominators;
  it is never relabeled nonspeech.
- **Frame adverse:** NaN, Inf, 80-sample nonfinal, and 161-sample frames are
  rejected with the state digest unchanged. A valid final 80-sample frame is
  accepted with end coordinate 240 and exact availability.
- **Config adverse:** 48 kHz, 2 channels, `s16`, 320-sample frames,
  `real_runtime=true` and empty session id are rejected.
- **Event bus:** sequences 2, 5 and 17 are explicitly dropped, producing gaps
  `[[2,2],[5,5],[17,17]]` and zero fabricated events. Stale epoch, missing and
  nonfinite probability, out-of-range probability, wrong clock, stale
  availability, wrong interval, duplicate sequence and unknown validity token
  cases are all rejected without state mutation.
- **Independent state:** two sessions (epochs 3 and 8) produce distinct event
  digests; resetting one to epoch 4 matches a fresh session and leaves the
  other unchanged; an epoch-3 event cannot revive analysis after reset.
- **Intervals and availability:** frame and probability intervals form the
  exact partition `[0,16000)`; known availability is strictly increasing and
  follows the pinned formula; speech events stay in bounds.
- **Cross-hop:** `[150,330)` projects to `[(0,10),(1,160),(2,10)]` with total
  overlap 180; the truth run `[800,2400)` spans exactly 10 full hops / 1,600
  samples.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Reproduction

Python 3.11.5, standard library only. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
```

Expected: 47 tests pass; three byte-identical repeats for every CLI mode;
report digest `762086dffc6cfc504035c99648e66065157e852cc4fb4b2500d646d7ce77d6cb`;
`verify.py` prints `verify: OK`.

From the worktree root (baseline build/install only; nothing here is linked):

```sh
scratch="${TMPDIR:-/tmp}/webrtc-vad-check-$$"
cmake -S . -B "$scratch/sdk" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$scratch/prefix" -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk" --parallel 4
ctest --test-dir "$scratch/sdk" --output-on-failure          # 11/11
cmake --install "$scratch/sdk"

git diff --check
git diff --cached --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-WEBRTC-VAD
```

REUSE lint 6.3.0 must be clean; every new file carries an SPDX annotation and
Python files split the license token to avoid a literal token inside a string.

## Remaining gates / non-claims

No real WebRTC runtime, wheel download, licensed asset, real speech, corpus,
recording, listening, quality, intelligibility, device timing, pacing, power,
production availability or release qualification is claimed. There is no
adverse Tiny16 comparison (no S10/protocol clearance, approved independent
reference adapter or permitted case manifest). No public-surface,
installed-behavior, board or cross-task change exists; no gate was weakened.

Remaining gates before any processor exposure or qualification claim:
independent exact-head review; hosted CI; rights-cleared label-complete cohort
and frozen candidate outputs; pinned target runtime/device/deadline workload;
independent provider intake; S10/protocol clearance; release approval. `DEFER`
remains in force until every gate is closed.
