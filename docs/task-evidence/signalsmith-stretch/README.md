# SDK-SIGNALSMITH-STRETCH — task-local synthetic stretch reference evidence

A deterministic, synthetic-only reference for a minimal Signalsmith-style
caller-clocked time-stretch at the public SDK adapter boundary. This is
**proposal evidence only**: the installed SDK, public API, ABI, descriptor
registry, descriptor defaults, shared `CMakeLists.txt`, installed v0 behavior
and `main` are unchanged. The optional C provider is unregistered and compiled
only by a caller that opts in.

This is **not** the upstream Signalsmith Stretch library. No upstream source is
vendored, built, licensed-review-verified or benchmarked here. No real speech,
listening result, target-device timing or release qualification is claimed.

Pinned base: `68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4`.
Branch: `swarm/SDK-SIGNALSMITH-STRETCH`.
Provider ID when explicitly registered: `rate.signalsmith-reference.v0`.

## Scope and boundary

- Installed v0 remains 16 kHz, mono `f32`, 160-sample frames. No variable-frame
  playback actuator is installed.
- Whole-clip and 160-frame streaming TSM fixtures are task-local only.
- `reference.py` is the deterministic engine, fixture generator and report
  model: fractional source phase accumulator, caller-owned fractional output
  clock, bounded waveform-similarity search, transient-aware segment placement
  and integer-window overlap-add normalization.
- `run.py` writes the canonical report, digest sidecar and C parity header.
  `test_reference.py` contains the acceptance suite.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`. The option
  `AS_ENABLE_SIGNALSMITH_STRETCH` is **OFF** by default; `ON` compiles and
  registers one caller-local provider.
- `SOURCES.sha256` pins every file in this directory except itself.
  `contract.json` records the task contract, exact pins and artifact digests.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | §6.5 speech clamp and smoothing; §9.5 proposed gates. |
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
`provider/expected_vectors.h` byte-identically. The generated C header contains
a valid SPDX identifier; the split-string construction avoids embedding the
full generated token in the Python generator source.

Optional C boundary build (SDK build and install stay outside the worktree):

```sh
SDK=<worktree root>
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/signalsmith-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SIGNALSMITH_STRETCH=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SIGNALSMITH_STRETCH=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SIGNALSMITH-STRETCH
git diff --check
```

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `reference.py` | `1b53a5e1669e43298eb87775686437ef2066bcd36f12884e6743abf47b4c91e5` |
| `run.py` | `cc334be2aac2371e208838e979a932de382278e9d7e6ba0b79601d911711b268` |
| `test_reference.py` | `3e2b65a4b4108978f3b9dc375b7fad7dec6613a6fa635ba054523a5817c18aeb` |
| `report.json` (file bytes) | `e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231` |
| `report.json.sha256` (file bytes) | `5ea9638dc9fde1ae4f624980090582262e90ac3a0fed9069b38828020c0b936b` |
| `provider/CMakeLists.txt` | `b0daa37b0286044236dc23aade2a5114f1e24e8f2c880756090800368cba91f3` |
| `provider/signalsmith_stretch_provider.c` | `6d685643ae736220b5f48667427cf25180843cba031a6598255bd26d5d0dfe0a` |
| `provider/expected_vectors.h` | `0d6c9baa49fead998b6e92bca32b4ad4dcc6e7d5c483af3d4474ac1183b3e83f` |
| `provider/config/config.json` | `766913a02756a239e1e921319216f4cfc4e33d00bf5ff2b339a2cb3b1312c18e` |
| `provider/config/descriptor.h.in` | `4bf108f0322a43cb691a42f468e13d734a2fd13bf3446b72bd55d05fdd6d763b` |
| `provider/tests/test_provider.c` | `c6eb6419a8adf358fbce026aa5bcbd17f4caf6f31c644e87844b4e0de5bb370a` |

Canonical report digest: `79d8081485b0dceec80a25756053292ddd96f9663ff4a2aa2ca731c8524843aa`.
C content digest: `fe7f7b331f5ce396fa2fbd7d69f9b8a245f41ed30ce4cc276dc56bcf314924d7`
(`10854` content samples, `78` frames, `922` buffered non-content samples,
final frame valid count `91`).

## Results summary

- Python acceptance suite: **32/32** passed.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_SIGNALSMITH_STRETCH=OFF`: **1/1** passed; provider
  unlinked and unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_SIGNALSMITH_STRETCH=ON`: **1/1** passed; registration,
  duplicate rejection, descriptor/config gating, session-level invalid-frame
  rejections, throwaway-session range rejection, 78-frame Python/C parity,
  rate clock, final partial frame, drain completion and ordered reset replay.
- Duration mapping is exact for all five synthetic stimuli at
  `0.75/1.0/1.25/1.5`: zero duration error, zero nonfinite and zero clipping
  samples. For `speech_like`, identity `12457`, fixed `1.25x` `9966`, slow
  `0.75x` `16609`, dynamic `11398` and varispeed adverse control `9966`.
- Source-anchored pause/filler schedule: `12800` input samples, four 2400-sample
  voiced spans at `0.9x` and four 800-sample pause spans at `1.5x`,
  `12800` output samples, zero duration error, seven observed boundaries. No
  filler is invented from output time.
- Drift and rebuffer schedules both map to exact expected output lengths
  (`12473` and `11686` samples) with segment-start-monotonic source maps.
- Frequency scale on the 220 Hz tonal stimulus: identity and dynamic candidate
  `220 -> 220` Hz (ratio `1.0`); fixed `1.25x` reference `220 -> 226` Hz
  (ratio `1.027273`); varispeed adverse control `220 -> 274` Hz
  (ratio `1.245455`, must shift pitch).
- Transient proxy on synthetic tonal/speech-like/music-like surrogates records
  peak retention `1.000`, `0.350` and `0.386/0.553/1.000` respectively, with
  source timing errors `0–25` samples. These are adjacent-delta/peak proxies,
  not audibility judgments; the modest speech-like retention remains a recorded
  reference limitation.
- Rate updates at source samples `4800`, `8000` and `11200` are all observed;
  the unsmoothed adverse control has a larger local adjacent-delta ratio at
  every boundary. Rate changes slew by `0.005` per 64-sample synthesis hop.
- Final partial window: `137` valid input samples, target `11398` output
  samples, finite bounded output, peak `1.0`, explicit output digest.
- Streaming reset replay is bit-exact and source-offset aware. Whole-clip and
  160-frame streaming digests intentionally differ because streaming is causal
  with bounded lookahead; this is recorded as `expected_lookahead_difference`.
  The fixed-frame clock records zero underrun for this fixture.
- Overlap-add normalization on the stationary tonal stimulus gives RMS ratio
  `0.894079` versus `908.686391` unnormalized. This is an energy-scale control,
  not a quality score.
- All reported outputs have zero nonfinite and zero clipping samples; no missing
  result qualifies a candidate.

The SDK drain API masks tail padding as zero-valid output and loops internally
until end-of-stream. With `max_drain_calls=16`, the public drain call returns
`AS_END_OF_STREAM` without a backend failure. The buffered non-content count
(`922` for the C vector) remains pinned in the Python model and `report.json`;
it is not asserted through `produced_count` because the SDK intentionally hides
that padding.

A provider-level `AS_INVALID_ARGUMENT` is mapped by `as_session_process_v0` to
`AS_BACKEND_FAILURE` and leaves the session in `AS_NEEDS_RESET`. The ON consumer
test therefore exercises out-of-range rejection on a throwaway session; the
Python model pins the provider-local rejection code and unchanged state.

REUSE lint is not installed in this environment (`reuse` and
`python3 -m reuse` are unavailable), so SPDX/REUSE lint was **not** verified
locally. Every new file carries an SPDX copyright and license tag; the
generated C header's SPDX line is checked by the Python suite.

## Adverse cases and explicit non-claims

Status is `synthetic-fixture-only`; candidate status is
`synthetic-reference-only`; boundary status is `conditional-blocked`.

- **BLK-01** — The frozen v0 boundary is exactly 160 f32 samples per process
  call and cannot express `r<1` device-time expansion. Slow-down is measured
  only in the task-local whole-clip fixture; the C reference covers identity,
  `1.25x` and `1.5x` speed-up and caller-clock duration mapping. Reopen with a
  versioned variable-frame playback actuator or a caller-owned TSM FIFO with
  explicit source/output timestamps outside v0.
- **BLK-02** — No target-device pacing, fill/flush, CPU, memory, deadline,
  availability or service-time measurement was run. Reopen with a paced target
  workload and resource telemetry under the intended profile.
- **BLK-03** — No listening test, real-speech corpus, real music, intelligibility
  score, WER model or release-quality assessment was run. The stimuli are
  analytic surrogates. Reopen with held-out permitted speech, matched controls,
  authorized scoring and rights review.
- **BLK-04** — The upstream Signalsmith Stretch library is not vendored, built,
  licensed-review-verified or benchmarked. Reopen with pinned upstream source,
  license/notice review, versioned integration and independent comparison.
- **BLK-05** — The C provider is unregistered, opt-in and not part of the
  installed SDK, any descriptor registry or the default build. Reopen with
  explicit provider intake, rights/license review, a versioned public-surface
  decision and independent review.

No real weights, downloads, licensed runtime, target-device timing, listening
result, release qualification, shared build changes, board/handoff edit or
`main` change is claimed or included.
