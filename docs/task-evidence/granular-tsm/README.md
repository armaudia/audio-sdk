# SDK-GRANULAR-TSM — task-local granular time-stretch evidence

A deterministic, synthetic-only reference for windowed-grain overlap-add
granular time-stretch (TSM) at the public SDK adapter boundary. This is
**reference evidence only**: the installed SDK, public API, ABI, descriptor
registry, defaults, shared `CMakeLists.txt`, installed v0 behavior and `main`
are unchanged. The optional C provider is unregistered and compiled only by a
caller that opts in.

Pinned base: `97a2299d42517b9d50dcb1251dd5e313c866699e`.
Branch: `swarm/SDK-GRANULAR-TSM`.
Provider ID when explicitly registered: `rate.granular-tsm-reference.v0`.

## Scope and boundary

- Installed v0 remains 16 kHz, mono `f32`, 160-sample frames. No variable-frame
  playback actuator is installed.
- Whole-clip and 160-frame streaming TSM fixtures are task-local only.
- `reference.py` is the deterministic granular engine, fixture generator and
  report model. `run.py` writes the canonical report, digest sidecar and C
  parity header. `test_reference.py` contains the acceptance suite.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`. The option
  `AS_ENABLE_GRANULAR_TSM` is **OFF** by default; `ON` compiles and registers
  one caller-local provider.
- `SOURCES.sha256` pins every file in this directory except itself.
  `contract.json` records the task contract, exact pins and artifact digests.

## Reference geometry

- Grain `512` samples, overlap `384` samples (75%), density `2`, analysis hop
  `128`, synthesis hop `64`, Hann window with overlap-add denominator
  normalization, phase denominator `1,000,000`.
- Declared grid: grain sizes `{256, 512}`, overlap ratios `{0.5, 0.75, 0.875}`
  and densities `{1, 2}`; all 12 combinations are scored.
- Rate bounds `0.75–1.50`, bounded slew `0.006` per grain, dynamic schedule
  `(0, 1.0) → (3600, 1.25) → (7200, 1.0) → (10000, 1.5)`, drift/rebuffer
  schedule `(0, 1.0) → (3200, 1.05) → (6400, 0.95) → (9600, 1.0)`.
- Controls: identity `1x`, fixed-rate density-1 baseline (50% overlap),
  dynamic density-1 control, `varispeed` adverse control and unsmoothed
  rate-step adverse control. No missing result qualifies a candidate.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | §5.7 granular synthesis note (parameter geometry only). |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | v0 provider/session contract provenance. |
| `audio-benchmark-platform/audio-sdk/README.md` | `9047036096a967bed5cd59e7d3b939258d327578b2079445da1b683b52a8fdb9` | SDK boundary provenance. |

Unchanged public boundary pins:

| Header | SHA-256 |
| --- | --- |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Reproduction

From this task directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
```

`run.py --report` rewrites `report.json`, `report.json.sha256` and
`provider/expected_vectors.h` byte-identically. The Python suite verifies the
canonical digest, all source pins, clean-checkout regeneration and every
acceptance metric.

Optional C boundary build (SDK install and both consumer builds stay outside
the worktree):

```sh
SDK=<worktree root>
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/granular-tsm-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_GRANULAR_TSM=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_GRANULAR_TSM=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-GRANULAR-TSM
git diff --check
```

## Results summary

- Python acceptance suite: **39/39** passed.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_GRANULAR_TSM=OFF`: **1/1** passed; provider unlinked
  and unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_GRANULAR_TSM=ON`: **1/1** passed; registration,
  duplicate rejection, descriptor/config gating, frame/config rejections,
  78-frame Python/C parity, rate mapping, final partial frame, drain
  completion and ordered reset replay.
- Duration mapping on the 12,457-sample speech-like stimulus: identity
  `12457`, fixed-rate density-1 baseline `9984`, dynamic density-2 candidate
  `11456`, dynamic density-1 control `11776`, unsmoothed adverse `11072` and
  varispeed control `9966` samples. Whole-clip and 160-frame chunking are
  bit-exact for the causal scheduler.
- Drift/rebuffer: observed `12416` versus `12473.04` expected,
  relative error `-0.0045730711833019645`; source-map repeat bounded at `3`
  samples, with `44` out-of-order source transitions explicitly recorded under
  the sub-unity drift segment.
- Frequency scale on the 220 Hz tonal stationary prefix (`512..2560`):
  identity, density-2 candidate and density-1 control `220 → 220` Hz
  (ratio `1.0`); fixed-rate density-1 baseline `220 → 212` Hz
  (ratio `0.963636`, recorded as pitch modulation); varispeed control
  `220 → 276` Hz (ratio `1.254545`, adverse control that must shift pitch).
- Rate updates at source samples `3600`, `7200` and `10000` are all recorded
  with local adjacent-delta checks. The candidate's bounded slew is
  `0.006` per grain (`108` updates); the unsmoothed adverse step reaches
  `0.5` (`3` updates) and is reported separately.
- Final partial window: `137` valid input samples, target `91` output samples,
  finite output, peak `1.0`, explicit output digest.
- Overlap-add denominator normalization on the stationary tonal stimulus gives
  RMS ratio `0.894488` versus `3.457584` unnormalized.
- Transient proxies at known synthetic boundaries are numerical local peaks
  only; audibility is explicitly `false` and no listening claim is made.
- All reported outputs have zero nonfinite and zero clipping samples; no
  missing result qualifies a candidate.

The SDK drain API masks tail padding as zero-valid output and loops internally
until end-of-stream. With the descriptor's `max_drain_calls=16`, the public
drain call returns `AS_END_OF_STREAM` without a backend failure. The buffered
non-content count (`1099` for the C vector) remains pinned in the Python model
and `report.json`; it is not asserted through `produced_count` because the SDK
intentionally hides that padding.

## Adverse cases and explicit non-claims

Status is `synthetic-fixture-only`; candidate status is
`synthetic-reference-only`; boundary status is `conditional-blocked`.

- **BLK-01** — The frozen v0 boundary is exactly 160 f32 samples per process
  call and cannot express `r<1` device-time expansion. Slow-down is measured
  only in the task-local whole-clip fixture; the C reference covers identity
  and `1.25x`/`1.5x` speed-up. Reopen with a versioned variable-frame playback
  actuator or a caller-owned TSM FIFO with explicit source/output timestamps
  outside v0.
- **BLK-02** — No target-device pacing, playback buffering, fill/flush,
  deadline, CPU, memory or availability measurement was run. Reopen with a
  paced target workload and resource telemetry under the intended profile.
- **BLK-03** — No listening test, real or unfamiliar speech, music recording,
  intelligibility score or release-quality assessment was run. Speech-like
  and music-like stimuli are analytic surrogates. Reopen with held-out
  permitted cohorts, matched controls, authorized scoring and rights review.
- **BLK-04** — The C provider is unregistered, opt-in and not part of the
  installed SDK or descriptor registry. Reopen with explicit provider intake,
  rights/license review, a versioned public-surface decision and independent
  review.
- **BLK-05** — No external granular implementation, model weights or licensed
  runtime was vendored or reproduced; this is a minimal analytic reference.
  Reopen with rights-cleared exact source or a caller-supplied runtime, pinned
  build and matched reference evidence before any implementation claim.

No real weights, downloads, licensed runtime, target-device timing, listening
result, release qualification, shared build changes, board/handoff edit or
`main` change is claimed or included.
