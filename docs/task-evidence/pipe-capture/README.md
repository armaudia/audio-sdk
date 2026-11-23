# SDK-PIPE-CAPTURE · task-local capture recipe/host fixture

**Status: proposal-only, model-free, synthetic and `incomplete`.** This is one
task-local recipe and deterministic host example with its integration fixtures.
It is not an SDK provider, engine plugin, public API/ABI change, installed native
behavior, build/CI wiring, paced-workload result, device result, corpus/model
evaluation, benchmark claim or release qualification. Fixed v0 remains
**16 kHz mono float32, 160-sample frames**. No file outside
`docs/task-evidence/SDK-PIPE-CAPTURE.md` and `docs/task-evidence/pipe-capture/`
is changed.

Pinned base: `d665c298e8cce8b4d576dc45f3c7f7d3b3457425`. Parent:
`dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc`. Branch:
`swarm/SDK-PIPE-CAPTURE`.

## Files

| Path | Role |
| --- | --- |
| `recipe.json` | One opt-in recipe set: identity, three single-stage ablations, base chain, voice-focus with advisory tap, explicit bypass and timeout control. |
| `fixtures.json` | Frozen synthetic stimulus parameters, source/dependency pins, control constants and explicit exclusions. No raw audio, model or build bytes. |
| `host.py` | Deterministic reference host: validation, buffered frames, monotonic clock, declared costs/timeouts, ordered stages, read-only tap, drain, failure bypass, scores and canonical report builder. |
| `generate_report.py` | Regenerates `report.json` and its SHA-256 sidecar byte-for-byte. |
| `report.json` | Canonical result: variant comparisons, paired scores, clipping counts, startup/tail/conservation, measured delay, bypass and control results. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `test_host.py` | 22 offline acceptance tests, including three byte-identical report regenerations and a protected-path diff check. |
| `README.md` | This scope, reproduction, digest, blocker and non-claim record. |

## Proposed control

* **Activation**: `default_enabled=false`, `opt_in_only=true`, no build targets,
  no shared sources, no descriptor/registry/default change. The chain is always
  explicitly selected by recipe variant.
* **Ordered audio path**: capture/control frames enter one linear path. The base
  chain is `dsp.highpass80.v0 → speex.ns.v0 → fixture.peak_limiter.v0`. Node
  IDs, ports, declared delays, declared costs and settings must match the pinned
  provider policy before a session exists. No fan-in, hot swap or provider
  substitution is modeled.
* **High-pass**: fixed 80 Hz, Q `0.7071067811865476`, double state, float32
  output, zero buffering delay, mirrored from the pinned provider source.
* **Speex NS policy**: pinned denoise-only settings, PCM16 quantization and
  declared 160-sample buffering delay. `host.py` is a deterministic
  task-local stationary-noise policy surrogate calibrated on the synthetic
  lead-in; it is **not** vendored SpeexDSP bit parity and not a quality result.
* **Limiter**: pinned ceiling `0.98`, release `50 ms`, copy fast path, double
  gain state, one-pole release and float32 clamp mirrored from the pinned
  reference arithmetic.
* **Advisory RMS tap**: `voice_focus` adds an analysis node on the limiter output.
  It emits RMS events only and never appears in `audio_path`; `basic_chain` has
  no analysis node and works unchanged.
* **Failure policy**: an explicit backend failure at epoch 7 moves that session
  to `needs_reset`. The failed session is drained, then the host opens a fresh
  epoch-8 `bypass` identity session at the failed source coordinate. There is no
  automatic retry or silent substitution.
* **Clock and buffers**: synthetic origin `1_000_000_000 ns`, `62500 ns/sample`,
  queue capacity 3, frame timeout `25_000_000 ns`. Submission clocks must be
  monotonic; declared availability is source-complete time plus declared stage
  cost. Declared cost is never measured stage time or measured availability.
* **Assets**: zero external assets, weights, downloads, corpora or devices.

## Reproduction

From the worktree root:

```sh
task=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PIPE-CAPTURE/docs/task-evidence/pipe-capture
cd "$task"
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_host.py
PYTHONDONTWRITEBYTECODE=1 python3 generate_report.py
python3 -m json.tool report.json >/dev/null
python3 -m json.tool recipe.json >/dev/null
python3 -m json.tool fixtures.json >/dev/null
shasum -a 256 recipe.json fixtures.json report.json report.json.sha256
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-PIPE-CAPTURE
```

Observed on macOS arm64, CPython 3.11.5: **22 tests passed, 0 failed, 0
skipped** in about `1.6 s`; all JSON files parse; the board checker reports
`SDK-PIPE-CAPTURE` as `in_progress`. `generate_report.py` rewrote identical bytes
on three independent runs; the canonical report repeats are byte-identical.

## Expected digests and counts

| Artifact / property | Expected value |
| --- | --- |
| `recipe.json` file / canonical digest | `08d5e1fa42327f1830e623c27ccb5ef0b03d40ca84cc7613342d1e3fa8cf8141` / `1766bbc2ff55037fb0502f221cbf6ece429759a4031cd042e3a9356115345f67` |
| `fixtures.json` file / canonical digest | `23b4d9e589239a8662d28e3c8dbc11371d22ebcbcc4de80d37217936dcc49e30` / `1dfc172da444dce16b30056738e76e700ecd0640ff12a4b9cf162e87b4181868` |
| `report.json` file / canonical report digest | `30734c321a8150cc2adea332e3b2c8daeeea24eb64b733fdfc0d0efd00609a37` / `3c5d380168a7ed221307c383e0513e24c2b830db9de207a7327fcee685bdd8f6` |
| `report.json.sha256` sidecar file | `11c8eeedb2d6265c13c80f69a0991b17f64686bd5ff13b356c365c5309987c75` |
| Source pins verified | `7/7` |
| Dependency pin | SpeexDSP `1.2.1`, revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`, vendored, no network fetch |
| Byte-identical report regenerations / internal repeats | `3` / `3` |
| Acceptance tests | `22` passed, `0` failed, `0` skipped |
| Partial conservation stimulus | `357/357` accepted/delivered valid samples for each variant; `0` missing, `0` duplicate |
| Failure-bypass stimulus | `800/800` combined valid samples after epoch 7 → 8; `320` drained before failure, `480` bypassed |
| Paired stimulus | `3200` samples; SI-SDR is arithmetic against the synthetic clean signal only |
| Tap events | `0` for `basic_chain`, `20` for `voice_focus`, all `mutates_audio=false` |
| Measured raw offset / content lag after declared alignment | identity `0`/`0`; base chain `160`/`0` samples |
| Clipping control | limiter-only output `0` clipped samples and `42` samples at/above the `0.98` ceiling |

The paired stimulus stays below the limiter ceiling, so identity and
limiter-only are bit-identical on that stimulus because the pinned copy fast
path applies. The separate clipping stimulus distinguishes them. The synthetic
80 Hz high-pass reduces low-frequency energy in the vocal surrogate, so the
base-chain paired SI-SDR delta is negative; that is a deterministic arithmetic
observation, not a listening, suitability or release result.

## Pipeline profile coverage

| Profile item | Task-local evidence |
| --- | --- |
| Stage ordering and acceptance | `recipe.json` declares one ordered audio path per variant; `host.validate_recipe` rejects bad format, default-on activation, provider mismatch, port breaks, non-read-only taps and hot-swap/retry settings before a session exists. |
| Control and stage-removed ablations | Identity, high-pass-only, NS-only, limiter-only, base chain and voice-focus outputs are compared with exact f32 digests. |
| Failure policy | Explicit backend failure at epoch 7; drained accepted prefix; fresh epoch-8 bypass at the failed source coordinate; no automatic retry. Timeout, clock, epoch, nonfinite and padding rejections are explicit. |
| Lifetime | `prepared → processing → drained → closed`; failure path passes through `needs_reset`; no hot swap or automatic substitution. |
| End-to-end clock and buffer accounting | Synthetic monotonic origin/period, declared availability, per-frame deadline, queue capacity 3, startup `160` samples for NS variants, final partial-frame tail and exact valid intervals. |
| Asset scope and paced workload | Zero assets; paced workload, deadlines under load, target device, microphone/acoustic path and listening are `blocked_not_measured`. |
| Stage timing independent of availability | `clock.measured_stage_time_ns` and `clock.measured_end_to_end_availability_ns` are `null`; declared costs are not inferred from source timestamps. |

Adverse/control results are non-empty and never qualify a candidate:
`rejected_timeout`, `rejected_bad_clock`, `rejected_stale_epoch`,
`rejected_nonfinite_input` and `rejected_bad_padding`. Missing STOI is recorded
as `blocked_missing_pinned_scorer`; no STOI value is reported.

## Blockers, deferrals and explicit non-claims

* **Blocked — native/API qualification**: no C build/CTest, header, ABI,
  descriptor, registry, installed native consumer or public v0 behavior was
  changed or tested. The Speex stage is a task-local policy surrogate, not
  vendored SpeexDSP parity.
* **Blocked — paced/real-device support**: no paced workload, CPU load,
  deadline, queue timing under load, microphone, acoustic or target-device
  measurement was performed. Declared clocks are synthetic.
* **Deferred — real audio/assets**: no corpus, real weights, downloads,
  licensed runtimes, model inference, listening test or quality score exists.
* **Excluded — Tiny16/adverse exploratory comparison**: no real Tiny16 parity
  or adverse exploratory comparison is claimed without S10/protocol clearance,
  an approved independent reference adapter and a permitted case manifest.
* **Not claimed — benchmark or release**: no public benchmark claim, default
  promotion, board/handoff edit, PR, merge or release qualification is implied.

Reopen only with exact scoped digests for a native implementation and approved
reference adapter, a measured paced/target-device workload with explicit clocks
and buffer accounting, or a rights-cleared real-audio qualification that
preserves the fixed v0 boundary.
