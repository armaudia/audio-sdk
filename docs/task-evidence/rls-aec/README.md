# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0

# SDK-RLS-AEC: task-local synthetic RLS AEC evidence

This directory contains **proposal-only, deterministic, task-local synthetic
evidence** for a guarded recursive-least-squares (RLS) acoustic echo canceller.
It is not a processor release. The documented decision is **DEFER**: do not
expose an RLS processor, do not register it, and do not change installed SDK
behavior.

The evidence is evaluated under the Room acceptance profile as
**DSP-adjacent synthetic evidence**. It uses no measured room impulse response,
real recording, licensed corpus/model weight, download, device loop, listening
test, target-device timing measurement or release qualification. All streams
are generated from fixed seeds and pinned fixture parameters.

## Scope and boundaries

Inside this directory only:

- `reference.py`: dependency-free guarded RLS reference, synthetic fixtures,
  metrics, adverse cases and canonical report construction.
- `run.py`: protocol-v1-shaped developer adapter and canonical report
  regeneration (`python3 run.py --report`).
- `crosscheck.py`: regenerates `provider/crosscheck_vectors.h` used by the C
  parity test.
- `test_reference.py`: Python unittest suite.
- `contract.json`, `adapter.json`, `report.json`, `report.json.sha256`,
  `SOURCES.sha256`: pinned contract, adapter descriptor, canonical report,
  canonical digest and full local source manifest.
- `provider/`: an optional, unregistered C reference provider, a task-local
  render-sidechain helper and the opt-in consumer CMake test.

Nothing outside this directory is changed. There is no change to `api/**`,
`core/**`, CMake at the SDK root, descriptors, defaults, provider registry,
catalog, installed behavior, CONTRACTS, board or handoff files. The C provider
uses only public v0 boundary headers. It is compiled only when the consumer
explicitly sets `AS_ENABLE_RLS_AEC=ON` (default `OFF`), and registration is an
explicit caller-side `as_register_provider_v0` call in that local test.

## What was studied

The synthetic fixture supplies far-end playback, an independent near-end
source, capture noise and a known sparse linear echo path. The microphone is
the mixture. The render reference is a separate sidechain, never inferred from
the microphone. Under the Room profile this is a DSP-adjacent structural study,
not a room measurement.

The candidate controller is causal RLS only (24 taps, `lambda=0.995`,
`P0=1.0`), with:

- explicit render sidechain per frame;
- no cancellation and no adaptation when the reference is withheld;
- zero/degenerate-reference update skip, preventing `P` windup under silence or
  near-end-only conditions;
- boundedness and finite-state checks before committing weight/covariance
  updates;
- restoration of finite state and freeze-on-violation before emitting output;
- frame-level normalized-correlation double-talk adaptation hold;
- epoch/position validation, partial final frames and end-of-stream drain.

Historical provenance is preserved as a control, not as a reproduced real
result: the prior full-RLS pilot was nonfinite on near-end-only recordings. The
unguarded recursion with an all-zero reference is reproduced analytically;
with the pinned legacy constants it first becomes nonfinite at sample 140683
(8.793 s). In the guarded 160000-sample extension, all 160000 updates are
skipped, output remains finite (`0.0015` peak), weights stay zero and the
covariance stays at `1.0`.

## Results (frozen canonical report)

`report.json` has canonical digest
`4be9c4b4efba1bd4618f46508c19d4f8287c59df0a61f6bf30908537d60be234`
and file SHA-256 `3fd2611c1b4619fab5858a78ee62920b66fd7acfb6aaac79b613dffd169e3b25`.
The fixture digest is
`39c3b5759a252aabb0a6effb4127983d0a87024e090e25902cbf56f53c203cfe`.

| Condition | Status | Far-end-only ERLE | Near-end SNR | GBF proxy | Nonfinite | Safety freezes | Qualifies |
| --- | --- | ---: | ---: | ---: | ---: | ---: | --- |
| single_talk | `ok_synthetic` | 40.55 dB | n/a | 36.19 dB | 0 | 0 | no |
| double_talk | `ok_synthetic` | 40.55 dB | 40.50 dB | 12.54 dB | 0 | 0 | no |
| delay_change | `ok_synthetic` | 40.55 dB (pre) / 40.55 dB (post) | 40.50 dB | 33.93 dB | 0 | 0 | no |
| near_only | `ok_synthetic` | n/a (silent render) | 44.50 dB | -2.21 dB | 0 | 0 | no |
| delayed_render | `misaligned_reference` | 40.56 dB | 44.14 dB | -9.02 dB | 0 | 0 | no |
| reference_dropout | `partial_reference` | 40.55 dB | 10.11 dB | 12.54 dB | 0 | 0 | no |
| missing_reference | `blocked_no_reference` | n/a | n/a | n/a | n/a | 0 | no |
| near_burst | `adversarial_near_burst` | 40.55 dB | 43.03 dB | 12.54 dB | 0 | 0 | no |

ERLE/echo-return loss is measured only in far-end-only windows. Near-end SNR
is measured in double-talk/adverse windows. `gain_before_feedback_db` is a
synthetic L1 residual-path loop-margin proxy, **not** a measured loudspeaker
loop gain. Delayed, partial, missing, adversarial and nonfinite cases are
reported but never qualify a candidate. No result is missing.

Double-talk preservation is recorded as a **control only**: guarded RLS
40.50 dB, RLS without hold 12.99 dB, fixed attenuation 4.38 dB, identity
3.44 dB, with 138 hold frames in the double-talk fixture. Analytic impulse,
step and digital-silence controls show zero algorithmic delay (peak at sample
1604 for a 4-sample path after a 1600-sample preamble) and exact silence.
Measured supply-reference lag is 4 samples, matching the intended primary tap;
the delayed fixture is misaligned by 4 samples. These are fixture lags only.

Fixed attenuation (0.5 gain) is reported separately from adaptive RLS. Under
fixed attenuation the far-end-only ERLE is exactly 6.0206 dB, while the
guarded adaptive controller reaches 40.55 dB. Controls never claim the
adaptive result.

## Decision

**Promotion: DEFER. Expose as processor: false.**

Synthetic guarded RLS establishes finite output, zero-reference update skipping
and near-end-only stability in-fixture. It does not clear recorded-room,
double-talk preservation, loop-gain/stability, device/timing or rights gates.
No default, installed, registered, catalog or public ABI change is proposed.

Open release gates:

1. Paired licensed render/capture recordings with known loop timing, pinned
   RIRs/path measurements and held-out speech rights.
2. Measured loudspeaker-loop gain-before-feedback and stability with device
   buffers, clock drift and target-device CPU/memory/deadline timing.
3. Double-talk, path-change and nonlinear-loudspeaker evaluation with
   AECMOS/ASR/listening preservation and attenuation gates.
4. Provider intake, license/rights, descriptor and public catalog review
   before any default, installed or production processor.

## Reproduction

From `docs/task-evidence/rls-aec/`:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 crosscheck.py
python3 check_licensing.py
python3 -c 'import json; json.load(open("contract.json")); json.load(open("report.json")); json.load(open("adapter.json"))'
```

From any SDK consumer with an installed SDK package:

```sh
cmake -S provider -B /tmp/rls-aec-off
cmake --build /tmp/rls-aec-off && ctest --test-dir /tmp/rls-aec-off --output-on-failure
cmake -S provider -B /tmp/rls-aec-on -DAS_ENABLE_RLS_AEC=ON
cmake --build /tmp/rls-aec-on && ctest --test-dir /tmp/rls-aec-on --output-on-failure
```

The OFF build leaves the provider source unlinked and unregistered. The ON
build links and explicitly registers it in the local test only.

## Pinned sources

| Source | SHA-256 |
| --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` |
| `research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md` | `4577d59347d9f48a693228ccbf40a9de77494294e7d0df111c98e8591c3e438e` |
| `src/audioml_eval/aec.py` | `84544219098d2c012da38163d49196379eb4f12094fb09cf106e57295ed69351` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `c7bdd981e0347aa74e32db917fc924303db057ba669e91c2b50d968abe61c950` (snapshot at read; mutable board, not written) |
