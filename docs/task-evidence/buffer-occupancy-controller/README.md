<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-BUFFER-OCCUPANCY-CONTROLLER

**Synthetic feasibility only; not qualified.** This optional, developer-run
reference recommends speed from input-FIFO occupancy. It is a control law,
not an estimator, stretcher, resampler, content gate, or playback device. No
audio, models, weights, external package, or third-party code are used. It is
not an installed provider, a registration or default change, or a Bench
submission. The installed v0 fixed 160-sample, 16 kHz mono f32 interface is
unchanged. No native playback or release capability is claimed.

Pinned base: `cafa74a1c10fc9d5e927e76183e850277288aade`.
Dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.

## Sources and boundary

| Source | SHA-256 | Evidence used |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Workspace research note: line 97 describes the candidate, §6.1/§6.4 specifies proportional/PI control, direction, clamp and slew; §8 distinguishes buffered playback from fixed-frame stages and algorithmic from queue/device delay. These are design inputs, not matched controller results. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance and installed checks. |
| `adapters/controls/adapter.json` | `3a49362727568dd953427a2c67eb734874fdf6bc9c0a795812a7b812bf780599` | Workspace adapter protocol v1 descriptor shape. |
| `adapters/controls/run.py` | `4d2d531507c33ab7c66859f6268ab7dcba8959a5e323f5a1b780208138904c66` | Workspace adapter protocol v1 `inspect`/`run`, revisioned refs and strict JSON conventions. |
| `docs/task-evidence/elastic-pcm-packets/contract.json` | `2ce960fb63a3ee2e1a888f33a990ce15da1804b0550aa3ad637c941222955e85` | At the SDK base: exact variable-count mapping, bounded admission and finite drain conventions. |
| `docs/task-evidence/duplex-clocks/contract.json` | `c09f5a45862fda31039be5b7ebccff07be904c606d51a6f3accde9bea6f04cb4` | At the SDK base: explicit clock domains, integer ppm and exact sample coordinates. |

First four paths are relative to the `audioml` workspace; last two are relative
to the SDK. The research note supplies no controller executable, assets or
matched device evidence. `reference.py` is an original runnable implementation
of just the proportional case (`Ki = 0`), with no integral windup or onset
detector. `run.py` uses a protocol-v1-shaped envelope with task-local trace
payload and output; it is not a drop-in waveform/Bench adapter or a new public
SDK contract. `report.py` freezes the exact synthetic traces, feeds them
through the adapter with both controller and fixed 1×, and records malformed
controls and SHA-256 digests of the full maps. There are no other input assets.

## Clock and failure policy

- Source coordinates are half-open intervals in millionths of a source sample
  (`*_usamples`); output coordinates are in nominal 16 kHz playout samples.
  Each virtual tick is 160 playout samples (10 ms). Source production is
  `floor((tick + 1) × 160 × (1 + drift_ppm/1e6))`, capped at source length;
  the first batch is visible at tick zero. A hold delays delivery, then one
  batch releases its backlog without reordering. No wall time is read.
- Target is 3200 source samples (200 ms nominal), capacity 9600 (600 ms).
  After arrivals, `1 + 0.25 × (queued − target)/target` is quantized down
  to integer ppm, clamped to `[0.95, 1.05]`, then slewed from the last
  emitted rate by at most 50 ppm/tick (0.5 percentage points/s).
  Rate >1 consumes more source per output period; source intervals never snap
  to frame boundaries. Every request starts fresh at 1×.
- Playback starts at target (or at EOS for short input). If the queue
  cannot cover a full nonfinal block, playout enters rebuffer and leaves
  time with **no source consumption, output content or new rate command**;
  resume at target or EOS, with slew from the last emitted rate. An
  over-capacity arrival is rejected as a whole batch and stops replay without
  silently dropping, accepting, or consuming it.
- At EOS the remaining valid source is consumed once. Final playout duration
  is the exact rational `consumed_usamples / rate_ppm`; it can be fractional
  in this ideal actuator model. There is no padding, fabricated silence or
  unbounded tail. Input is bounded to 30 s nominal, ±200,000 ppm synthetic
  source drift, and up to 200 held ticks; exhausting the loop budget is an
  explicit `tick_limit` failure. These limits are not device specs.

## Matched synthetic results

| Case | Controller vs fixed 1× |
| --- | --- |
| Nominal and final partial | Both map all 32,017 source samples once; 3040 virtual samples of prefill, zero rebuffer. Fixed playback is exactly 32,017 active samples, including a 17-sample tail. Controller remains 1× while the live queue is on target, then slows at EOS and adds 1.539 active samples; its last interval is `18520/999` playout samples. |
| +1000 ppm source clock | Mean absolute live queue error: **12.569 vs 240.800** source samples; active duration **479509.238 vs 479977** playout samples. Both finish without a rebuffer or lost source. |
| −1000 ppm source clock | Mean absolute live queue error: **17.806 vs 133.483**; active duration **480290.012 vs 479977**. Both finish without a rebuffer or lost source; the controller briefly speeds up after prefill overshoots the target, then slows down. |
| 400 ms input hold and release | Both rebuffer once for **3360 playout samples (210 ms)**, producing no content in that gap, then consume all 128,017 source samples. Active duration **126708.287 vs 128017**; the controller drains the released backlog faster but does not prevent the stall. |
| +60,000 ppm source clock | Controller reaches **1.05×** and still overflows. Overflow at virtual sample **241280 vs 109280**; both reject a 170-sample arrival batch. |
| 1 s input hold and release | Both rebuffer then overflow at virtual sample **48000**; the 16,160-sample batch is rejected. Neither claims completion. |

Queue error excludes prefill, gaps and ticks at or after EOS admission. All
12 runs obey cap/slew and interval accounting; both clamp extremes are also
tested directly. Eight malformed/missing/stale/nonfinite controls are
rejected without a timeline. `candidate_qualified` is false even for complete
synthetic runs; a missing case or result, invalid data, nonfinite data, overflow,
or a rebuffered stress outcome cannot qualify the candidate. CLI exit 0 only
indicates a complete inspect or replay, not qualification.

## Reproduce

From the SDK worktree root, with Python 3.11+ and stdlib only:

```sh
(
  cd docs/task-evidence/buffer-occupancy-controller
  export PYTHONDONTWRITEBYTECODE=1
  python3 -m unittest -v test_reference.py
  python3 report.py | cmp - report.json
  shasum -a 256 report.json
)
git diff --check
reuse lint
```

Expected: 8 tests pass, exact report reproduction, report SHA-256
`9dc73683b42a47801efcd71449b7d93fbd40a490beae54c46cc29680ebead47c`.
For the full map, from this task directory (write to a fresh scratch path):

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -c \
  'from report import CASES; from run import canonical, request; print(canonical(request(CASES["nominal_final_partial"])), end="")' \
  > "$scratch/request.json"
PYTHONDONTWRITEBYTECODE=1 python3 run.py --request "$scratch/request.json" --result "$scratch/result.json"
```

Installed SDK checks (fresh scratch, from the SDK root):

```sh
scratch=$(mktemp -d "${TMPDIR:-/tmp}/occupancy-sdk.XXXXXX")
cmake -S . -B "$scratch/all" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/all" --parallel 2
ctest --test-dir "$scratch/all" --output-on-failure --timeout 60
PYENV_VERSION=3.12.16 python3.12 -m venv "$scratch/check-env"
"$scratch/check-env/bin/python" -m pip install --require-hashes -r requirements-build.txt
"$scratch/check-env/bin/python" scripts/ci.py --output "$scratch/ci"
```

These commands check the unchanged SDK, not a native controller build.

## Blocker and conditions to reopen

No matched release evidence is available: there is no pinned variable-count
actuator wired to an instrumented source FIFO and playout device on the
intended target, and no frozen rights-cleared cohort or agreed budgets for
that workload. The source's historical stretcher/gate pre-screens are not
controller results. This reference emits no PCM and cannot measure unfamiliar
speech, music, acoustic silence, onset/transient audibility, pitch or speech
preservation. It makes no pause/filler decisions. A synthetic arrival hold
is not silence or a device underrun observation.

Before qualification, agree on workload, margins, delay/availability,
resource limits and deadlines; pin the permitted actuator, target clocks and
device, and freeze a rights-cleared cohort (held-out speech, music, silence and
transients). Measure matched fixed 1× and controlled native paced runs with
source/output and device clocks, real rebuffer/drift, onset behavior, actual
fill/partial/flush and underruns, duration/pitch/listening/preservation, and
CPU/memory/deadlines. Separate algorithmic, queue, smoothing and device delays.
Require independent review and separate versioned integration/release work.
