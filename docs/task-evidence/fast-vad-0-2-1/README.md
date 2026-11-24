<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FAST-VAD-0-2-1 — task-local synthetic VAD analysis evidence

**Status: `proposal_only_not_qualified`; qualification `incomplete`; decision
`DEFER` before any processor exposure.** This is a deterministic, fully
synthetic VAD *surrogate* at a task-local, protocol-v1-shaped analysis
boundary. It is **not** fast-vad 0.2.1, not a wheel download, not a licensed
runtime, not an SDK provider, not a registered descriptor, not a control signal
and not an accuracy or release qualification.

No public API/ABI, `CONTRACTS.md`, shared `CMakeLists.txt`, descriptor registry,
descriptor default, installed v0 behavior, board file, handoff, ruleset, main
branch or other worktree was changed. Installed v0 remains 16 kHz mono
`float32`, 160 samples.

Task-pinned base: `2bc2a13aa4c5b398933fd9097d09746ce151216e`. Branch:
`swarm/SDK-FAST-VAD-0-2-1`. `origin/main` advanced first to
`ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d` and then to final submission target
`ddce4bc6b7b5a6fb1761933dad50f87c8168bd10`; this branch was rebased onto that
head and all verification was repeated. The upstream commits add other
task-local evidence and fix SPDX string literals in already-merged packages;
the boundary pins below are byte-identical to the pinned base. Every file in
this package lives only under `docs/task-evidence/fast-vad-0-2-1/`.

## Exact scope and boundary

- Boundary anchor: public adapter `adapters/fast-vad/adapter.json`, identity
  `fast-vad-0.2.1-normal-stateful`, `VadStateful.detect_frame`, 16 kHz mono,
  **512-sample/32 ms** frames, mode 1. The frozen installed SDK v0 uses
  **160-sample/10 ms** frames. The cadence divergence is recorded and no
  numeric parity with the real runtime is claimed.
- Local identity: `fast-vad-0-2-1-synthetic-reference-v1`. It emits
  timestamped `speech_probability` records and advisory `speech_event` runs on
  exact half-open source intervals with epoch, session, sequence, validity,
  availability clock and an explicit rejection/drop audit.
- Probabilities are an **uncalibrated logistic surrogate** of frame RMS and
  zero-crossing rate from deterministic integer-synthesised waveforms. They are
  not fast-vad posteriors, not calibrated confidences and never gate audio.
  Decision rule is `probability >= 0.5` with one synthetic hangover frame;
  both are frozen in `fixture.py`.
- The upstream adapter's README, `run.py` and `requirements.lock` are pinned as
  provenance only. They are never installed, imported or executed. No wheel,
  binary, model weight, licensed asset, real corpus or real speech is present
  in this package.
- `provider.json` is proposal-only: `registered: false`,
  `default_enabled: false`, `processor_exposure: false`, `decision: DEFER`.
  The **optional C boundary is not included**: there is no opt-in consumer, no
  native parity crosscheck and no linked or registered code. `--crosscheck`
  is an independent recomputation of the same synthetic scores, **not** a
  fast-vad parity result.
- Historical source-reported values for the stateful path on held-out AMI
  (FN 17.20%, FP 25.21%, 6.34 µs per 20 ms frame; batch path untested) are
  recorded as provenance only. They are not reproduced, pooled or used as an
  oracle, and no host timing is treated as target-device timing.

## Source pins and boundary headers (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests and
`verify.py` fail closed on a missing or changed pin; there is no substitution,
pooling or tolerance.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `reports/vad-research/chaining-evaluation.md` | `f8bf02a7465c880d1a8968b26a3425f55e0bbd6965eea6b0dc734e0fa1f5a234` |
| `adapters/fast-vad/adapter.json` | `003d2f568bf27e590b03a083c8ccf4251b0b40933cdd5c2aa116123366350ee8` |
| `adapters/fast-vad/README.md` | `18f3386925e241f00e6e1a7c07f400073918192ae724f09b80fb07d6da5e0d30` |
| `adapters/fast-vad/requirements.lock` | `3a0b7c528e8d044aa116081daf890f67542bf0b5461fd4c6b0ed442f487b2d95` |
| `adapters/fast-vad/run.py` | `779e628c79b71ea9dee2c881a07739c914b4534de1bcc9dd463a318d81f64140` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Relevant boundary headers recorded verbatim by digest: `provider_v0.h` defines
the 16 kHz/mono/160-sample v0 constants, provider table and descriptor rules;
`session_v0.h` defines the opaque session lifecycle; `CONTRACTS.md` sections
"C boundary and types", "Session facade and scheduling ownership", "Content
mapping, finalization and delay" and "Descriptor and effective configuration
schemas" define the registration, timing and availability semantics. None is
modified and none is instantiated by this package.

The mutable board snapshot (`plan/swarm/TASKS.json`,
`275f2d6550eb3f7357d41f8749d92489ebb8601e9f9c5f025d67898fa577e106` at read
time) is provenance only and never gates this evidence.

## Analysis profile application

`plan/swarm/VERIFICATION.md` Analysis row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Timestamped probabilities | 100 exact source-interval records, Brier and log loss reported |
| Event boundaries | 3 truth runs matched by overlap; onset/offset delay in samples and ms |
| Detections | TP/FN/FP/TN by sample, overall and per frozen stratum |
| Quiet and active speech | `quiet-a`, `quiet-b`, `active-a` strata |
| Idle noise | `idle-a/b/c/d` and `noise-burst` strata |
| Known positives/negatives | 4,960 speech samples, 9,760 nonspeech samples |
| Onset/offset delay | `quiet-a` +1,280/−0 samples; `active-a` 0/0; `quiet-b` missed |
| Stratified FN/FP | `quiet-a` FN 1,280; `quiet-b` FN 800; `noise-burst` FP 320 |
| Validity separate from nonspeech | 1,280 unknown samples excluded; invalid never scored as negative |

Also verified: independent session state, exact source intervals, strict
availability monotonicity, explicit dropped/stale/nonfinite/missing cases and
cross-hop projection. No missing, stale, unrun or blocked result is promoted
to a pass or used to qualify the candidate.

## Method

1. `fixture.py` synthesises 16,000 samples (1 s) from integer arithmetic: a
   fixed 64-entry waveform table, a deterministic LCG noise source and a frozen
   segment table. Samples are quantised to int16 and exposed as `float32 / 32768`.
2. Nine frozen truth segments cover quiet speech, active speech, below-threshold
   quiet speech, idle noise, a loud noise burst and an explicit unknown tail.
   Every boundary is a multiple of 160 samples, so each event has one
   unambiguous source label.
3. `reference.py` drives a 160-sample session. Each accepted frame emits one
   probability record with `start_sample`, `end_sample`, `probability`,
   `decision`, `validity`, epoch, sequence and availability. Known events use
   `available_ns = origin_ns + end_sample × 62500 + 5,000,000` on clock
   `fast-vad-0-2-1-fixture-monotonic-v0`; unknown events carry no availability
   and no decision.
4. Contiguous known decisions form advisory speech events with one hangover
   frame. A run closes at the first inactive frame and becomes available at
   that frame's end; an unterminated run closes on drain.
5. `scorer.py` scores probabilities (Brier/log loss), weighted confusion,
   per-stratum FN/FP and overlap-matched boundaries. Unknown samples are
   excluded; invalid records are rejected before scoring.
6. `run.py --report` generates the report three times, requires byte-identical
   payloads and only then writes `report.json` and `report.json.sha256`.
   `--sources`, `--crosscheck` and `--inspect` are likewise deterministic and
   are checked across three cold-start subprocess repeats by `verify.py`.

## Canonical report and digests

`report.json` is canonical JSON (sorted keys, compact separators,
`allow_nan=False`, LF, one trailing newline). The digest below is both the
canonical digest and the file/SHA-256-sidecar digest.

| Name | SHA-256 |
| --- | --- |
| `report.json` file / canonical digest / sidecar | `6d9933761ee4e00a6503c02ba5331bc92463e734aa791c0bf89bea4d670d7e82` |
| Fixture spec | `dc723fab2334cedf1342fbe1a8726ef488f011a786be466c5588a1128a874dda` |
| Crosscheck payload | `9bc7a8b9e4d23532a52f7f99521646587b47065042db0fa7591c941b0ff6403f` |

Local artifact digests are in `SOURCES.sha256`; `contract.json` pins the code
and JSON artifacts independently. All comparisons are exact.

## Results (synthetic only)

100 frames / 16,000 samples, 92 known events (14,720 samples), 8 unknown
events (1,280 samples) and 3 advisory speech events, with 0 invalid admissions.

| Metric | Exact value |
| --- | ---: |
| TP / FN / FP / TN (samples) | 2880 / 2080 / 320 / 9440 |
| Speech miss rate (FN / 4960) | 0.419354838710 |
| False-alarm rate (FP / 9760) | 0.032786885246 |
| Brier score | 0.089213865607 |
| Log loss | 0.239116188343 |
| Mean probability (known) | 0.254230797762 |

Stratified detections: `quiet-a` TP 320 / FN 1280, `active-a` TP 2560,
`quiet-b` FN 800, `noise-burst` FP 320 / TN 640, `idle-a` TN 960, `idle-b` TN
960, `idle-c` TN 800 and `idle-d` TN 6080. The unknown tail contributes to no
denominator.

Boundaries: `quiet-a` truth `[960,2560)` is matched by `[2240,2560)` (onset
+1,280 samples / +80 ms, offset 0); `active-a` `[3520,6080)` is matched exactly
(0/0); `quiet-b` `[7040,7840)` is missed. One false event `[6720,7040)` comes
from the synthetic noise-burst hangover. Positive onset means a late start;
negative offset would mean an early stop. These are source-coordinate effects,
not device or availability timing.

## Failure controls (exact failures recorded as failures)

- **Invalid vs nonspeech:** invalid/missing validity, nonfinite and
  out-of-range probabilities are rejected by both session and scorer. Unknown
  events are admitted to the audit but excluded from all denominators; they are
  never relabeled nonspeech.
- **Frame adverse:** NaN, Inf, 80-sample nonfinal and 161-sample frames are
  rejected with the state digest unchanged. A valid final 80-sample frame is
  accepted with end coordinate 240 and exact availability.
- **Config adverse:** 48 kHz, 2 channels, `s16`, 320-sample frames,
  `real_runtime=true` and empty session id are rejected.
- **Event bus:** sequences 2, 5 and 17 are explicitly dropped, producing gaps
  `[[2,2],[5,5],[17,17]]` and zero fabricated events. Stale epoch, missing and
  nonfinite probability, out-of-range probability, wrong clock, stale
  availability, wrong interval, duplicate sequence, nonfinite frame and unknown
  validity token cases are all rejected without state mutation.
- **Independent state:** two sessions (epochs 3 and 8) produce distinct event
  digests; resetting one to epoch 4 matches a fresh session and leaves the
  other unchanged; an epoch-3 event cannot revive analysis after reset.
- **Intervals and availability:** frame and probability intervals form the
  exact partition `[0,16000)`; known availability is strictly increasing and
  follows the pinned formula; speech events stay in bounds.
- **Cross-hop:** `[150,330)` projects to `[(0,10),(1,160),(2,10)]` with total
  overlap 180; the truth run `[960,2560)` spans exactly 10 full hops / 1,600
  samples.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Reproduction

Python 3.11.5, standard library only. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 run.py --inspect
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
python3 -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
reuse lint
```

Expected: 47 tests pass; three byte-identical repeats for every CLI mode;
`verify.py` prints `verify: OK`; `check_licensing.py` reports zero problems;
REUSE 6.3.0 lint is clean.

From the worktree root (baseline build/install only; nothing here is linked):

```sh
scratch="${TMPDIR:-/tmp}/fast-vad-0-2-1-check-$$"
cmake -S . -B "$scratch/sdk" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$scratch/prefix" -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk" --parallel 4
ctest --test-dir "$scratch/sdk" --output-on-failure          # 11/11
cmake --install "$scratch/sdk"

git diff --check
git diff --cached --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-FAST-VAD-0-2-1
```

All new Python files split the license token inside strings; JSON files carry
the annotation as a key and sidecars cover the generated hash files. No literal
annotation token appears in prose.

## Remaining gates / non-claims

No real fast-vad runtime, wheel download, licensed asset, upstream code, real
speech, corpus, recording, listening, quality, intelligibility, device timing,
pacing, power, production availability or release qualification is claimed. No
numeric parity claim is made because no C boundary or real-runtime crosscheck
was included. No public-surface, installed-behavior, board or cross-task change
exists; no gate was weakened.

Remaining gates before any processor exposure or qualification claim:
independent exact-head review; hosted CI; rights-cleared, label-complete cohort
and frozen candidate outputs; pinned target runtime/device/deadline workload;
independent provider intake; S10/protocol clearance; release approval. `DEFER`
remains in force until every gate is closed.
