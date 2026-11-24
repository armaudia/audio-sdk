# SDK-PSOLA-PRAAT — task-local synthetic PSOLA / Praat-style evidence

A deterministic, synthetic-only TD-PSOLA-style time-scale-modification
reference exercised at the public SDK adapter boundary. This is **reference
evidence only**: the installed SDK, public API, ABI, descriptor registry,
defaults, shared `CMakeLists.txt`, installed v0 behavior and `main` are
unchanged. The optional C provider is unregistered and compiled only by a
caller that opts in.

Pinned base: `68e3e292b0b2c4b0a96b5f3d3002bb9cb36282d4`.
Branch: `swarm/SDK-PSOLA-PRAAT`.
Provider ID when explicitly registered: `rate.psola-praat-reference.v0`.

## Scope and boundary

- Installed v0 remains 16 kHz, mono `f32`, 160-sample frames. No variable-frame
  playback actuator is installed.
- Whole-clip and 160-frame streaming PSOLA fixtures are task-local only.
- `reference.py` is the deterministic engine: absolute-value pitch marking,
  Hann-window excision, per-sample overlap-denominator normalization, and
  mark selection from a rate schedule with slew. `run.py` writes the canonical
  report, digest sidecar and C parity header. `test_reference.py` is the
  acceptance suite.
- Stimuli are analytic surrogates (`silence`, `tonal`, `speech_like`,
  `unfamiliar_speech`, `music_like`, integer-exact `c_vector`). No corpus,
  WAV, model weight, download, real speaker, real music or listening test is
  used.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`. The option
  `AS_ENABLE_PSOLA_PRAAT` is **OFF** by default; `ON` compiles and registers
  one caller-local provider.
- `SOURCES.sha256` pins every file in this directory except itself.
  `contract.json` records the task contract, exact pins and artifact digests.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Task-listed PSOLA/Praat follow-up context. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Task-listed candidate context. |
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
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/psola-praat-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_PSOLA_PRAAT=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_PSOLA_PRAAT=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
git diff --check
```

`reuse lint` is not installed locally, so local REUSE verification is
**skipped / unavailable**; every new source file carries an SPDX header and
`REUSE.toml` annotates `docs/**`.

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `reference.py` | `a7d1a61d75ba78fd56e80471056fa0c5862e131a014df2cb91256c46c5d451ab` |
| `run.py` | `893f666dfb8c512083e31565284fe647bbea1b2eff94e0cb43b21959770aaeff` |
| `test_reference.py` | `715d57eb77e97648bb95b7183b61d0a55bfaab6daf00426a07199953c22bb77f` |
| `report.json` (file bytes) | `c8126e10ec682b6960bc379a2d5a5db9222abedcd37b6fe62d176c47e07de614` |
| `report.json.sha256` (file bytes) | `fcf031c88edbd29347989f43b747328d2342d28380385dfbdb0ca1519ee5d684` |
| `provider/CMakeLists.txt` | `be5a2cbb4819db5b8da2d9ffbb278c1fa39370cc3138cfb1ef0372162f62e129` |
| `provider/psola_praat_provider.c` | `4fb961b2a3ee0ee0bb439a4e6a1dd8f21d92e0cd2caacc8a57e47305a8a418a9` |
| `provider/expected_vectors.h` | `18198cec430faf06a59aeb387d301f3a2279a82befea2090c2d5efc4f2d0a8a0` |
| `provider/config/config.json` | `f3f1270cc6fff80abd377aeccc33bdfc6c2621403afb4ba9580148b5776a8212` |
| `provider/config/descriptor.h.in` | `86b2a7418375b0af58d05ad40d578e6a8ccda8e282c66c55b9937025b9c2d9e7` |
| `provider/tests/test_provider.c` | `59da0ddf13e00d2b76129a7bcca6484e9a15e30377576c7b3925457799a27924` |

Canonical report digest: `9f53748ad93800f67a487f86d5184e4b5dcedb1afdfa9df30287794dbe1a8fce`.
C content digest: `68c36aa288f0d36017dd5b83c44c02649667825fe9505d5c667e1e2daa4d666e`
(`11240` content samples, `78` frames, `199` buffered non-content samples).

## Results summary

- Python acceptance suite: **34/34** passed.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_PSOLA_PRAAT=OFF`: **1/1** passed; provider unlinked
  and unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_PSOLA_PRAAT=ON`: **1/1** passed; registration,
  duplicate rejection, descriptor/config gating, frame/config rejections,
  78-frame Python/C parity, rate mapping, final partial frame, drain
  completion and ordered reset replay.
- Pitch marks: silence `0`; tonal `172` (mean period `72.75` samples, ~`220`
  Hz), speech-like `153` (~`196` Hz), unfamiliar-speech surrogate `176`
  (~`225` Hz), music-like `125` (~`160` Hz), integer c-vector `129`
  (~`166.7` Hz). All minimum gaps are >= `64` samples and maximum gaps are
  <= `112` samples; no unvoiced silence synthesis is invented.
- Duration mapping over `12457` input samples: identity `12457`; fixed-rate
  PSOLA `9903`–`10008` (effective rates `1.245`–`1.258`); dynamic schedule
  `11439`–`11463` (effective rates `1.087`–`1.089`); varispeed adverse control
  `9966`. Whole-clip slow `r=0.95` output `13113` (effective `0.950`),
  fixture-only.
- Frequency scale on the 220 Hz tonal stimulus: identity and PSOLA
  `220 -> 220` Hz (ratio `1.0`, pitch preserved); varispeed adverse `1.2455`
  (pitch shifted); mismarked adverse `2.0` with mean period below the
  `64`-sample minimum (pitch doubled, recorded as a failure mode).
- Overlap/add manipulation: normalized RMS ratio `0.999639` versus
  unnormalized `0.806510`; candidate has `0` uncovered samples. The short
  `18`-sample excision-window adverse control has `5133` uncovered samples.
- Rate updates at source samples `4800`, `8000` and `11200` are recorded with
  slew (`applied_rate` `1.05`, `1.2`, `1.05` for the c-vector); an unsmoothed
  step is scored separately as an adverse case. Drift/rebuffer observed
  `12447` versus `12473.04` expected (relative error `-0.002088`).
- Final partial window: `137` valid input samples, `11456` output samples,
  finite, peak `0.46875`, explicit output digest.
- Streaming reset replay is bit-exact and source-offset aware. Whole-clip and
  160-frame streaming digests intentionally differ (causal boundary marking);
  this is recorded as `expected_lookahead_difference`.
- Explicit invalid/missing/nonfinite cases: `nonfinite_input`,
  `out_of_range`, `wrong_shape`, `wrong_position`, `stale_epoch`,
  `process_after_final`, missing rate selection, invalid config, invalid
  schedule, drain-before-final and flush-before-final all reject with an unchanged
  state digest. No missing result qualifies a candidate.

The SDK drain API masks tail padding as zero-valid output and loops internally
until end-of-stream. The withheld non-content sample count (`199` for the
c-vector) remains pinned in `report.json` and `expected_vectors.h`; it is not
asserted through `produced_count` because the SDK intentionally hides it.

## Blockers and explicit non-claims

Status is `synthetic-fixture-only`; candidate status is
`synthetic-reference-only`; boundary status is `conditional-blocked`.

- **BLK-01** — The frozen v0 boundary is exactly 160 f32 samples per process
  call and cannot express `r<1` device-time expansion. Slow-down (`0.95`) is
  measured only in the task-local whole-clip fixture; the C reference covers
  identity and `1.25x`/`1.5x` speed-up. Reopen with a versioned variable-frame
  playback actuator or a caller-owned TSM FIFO with explicit source/output
  timestamps outside v0.
- **BLK-02** — No target-device pacing, fill/flush, CPU, memory, deadline or
  availability measurement was run. Reopen with a paced target workload and
  resource telemetry under the intended profile.
- **BLK-03** — No listening test, real-speech or real-music corpus,
  intelligibility score or release-quality assessment was run. Praat/psola
  results in the linked research are source-reported context, not reproduced
  here. Reopen with rights-qualified held-out material, matched controls and
  authorized listening/intelligibility scoring.
- **BLK-04** — The C provider is unregistered, opt-in and not part of the
  installed SDK or descriptor registry. Reopen with explicit provider intake,
  rights/license review, a versioned public-surface decision and independent
  review.

No real weights, downloads, licensed runtime, target-device timing, listening
result, release qualification, shared build changes, board/handoff edit or
`main` change is claimed or included.
