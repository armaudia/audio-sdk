<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SOUNDTOUCH — task-local synthetic time-stretch evidence

A deterministic, synthetic-only reference for a minimal SoundTouch-named
WSOLA-style caller-clocked time-stretch at the public SDK adapter boundary.
This is **proposal-only, not qualified**: the installed SDK, public API, ABI,
descriptor registry, descriptor defaults, shared `CMakeLists.txt`, installed v0
behavior, board, handoff, ruleset, `main` and every other task are unchanged.
The optional C boundary is unregistered, default-OFF and compiled only by a
caller that explicitly opts in.

This is **not** the upstream SoundTouch library. No upstream source, binary,
weights, licensed runtime or real corpus is vendored or used here. No listening
result, target-device timing or release qualification is claimed. Status is
`proposal_only_not_qualified`, decision `incomplete`, promotion `defer`, and
production exposure `DEFER`.

Pinned base: `ddce4bc6b7b5a6fb1761933dad50f87c8168bd10` (the task was originally
claimed at `add40f5cab979995b6114deb2a05302e547c148c`; `origin/main` advanced,
so this branch was rebased before evidence generation). Branch:
`swarm/SDK-SOUNDTOUCH`. Provider ID only if a future caller explicitly
registers it: `rate.soundtouch-reference.v0`.

## Scope and boundary

- Installed v0 remains 16 kHz, mono `f32`, 160-sample frames. No variable-frame
  playback actuator is installed.
- Whole-clip and 160-frame streaming TSM fixtures are task-local only.
- `reference.py` is the deterministic engine, fixture generator and report
  model: fractional source phase accumulator, caller-owned fractional output
  clock, bounded waveform-similarity search, transient-aware segment placement
  and integer-window overlap-add normalization.
- `fixture.py` freezes the analytic stimuli, schedules and the explicit
  invalid/missing/nonfinite/adverse case table. `scorer.py` fails closed on any
  missing, invalid, nonfinite or adverse result; no missing result is promoted.
- `run.py` writes the canonical report, digest sidecars, C parity header and
  crosscheck. `verify.py` is a read-only strict validator; `check_licensing.py`
  checks SPDX/REUSE invariants. `test_reference.py` contains the acceptance
  suite.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`. The option
  `AS_ENABLE_SOUNDTOUCH_REFERENCE` is **OFF** by default; `ON` compiles and
  registers one caller-local provider inside that consumer executable only.
- `SOURCES.sha256` pins every file in this directory except itself, plus the
  exact source and boundary pins below. `contract.json`, `adapter.json` and
  `provider.json` record the task, boundary, opt-in and non-registration
  invariants.

## Exact source pins

Source paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Source-reported SoundTouch 2.4.1 duration, RTF, F0 and paired Whisper context; historical, not re-measured here. |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Rate semantics, 160-frame Stage incompatibility, LGPL/commercial condition and proposed gates. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Stateful tempo API and buffered-playback disposition. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | v0 provider/session contract provenance. |
| `audio-benchmark-platform/audio-sdk/README.md` | `9047036096a967bed5cd59e7d3b939258d327578b2079445da1b683b52a8fdb9` | SDK boundary provenance. |

Unchanged public boundary pins (paths relative to the SDK worktree root):

| Header | SHA-256 |
| --- | --- |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Reproduction

From this task directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --crosscheck
python3 run.py --sources
python3 verify.py
python3 check_licensing.py
```

`run.py --report` rewrites `report.json`, `report.json.sha256` and
`provider/expected_vectors.h` byte-identically. `verify.py` re-derives the
report, sources manifest and generated header three times and requires exact
byte agreement. The generated C header contains a valid SPDX identifier; the
split-string construction avoids embedding the full generated token in the
Python generator source.

Optional C boundary build (SDK build and install stay outside the worktree):

```sh
SDK=<worktree root>
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/soundtouch-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SOUNDTOUCH_REFERENCE=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_SOUNDTOUCH_REFERENCE=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-SOUNDTOUCH
git diff --check
git diff --cached --check
```

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `reference.py` | `25d92b896fba5ac928b450f7a0fa86fbedddde82bf1ef7d47741265c9fa742c6` |
| `run.py` | `9cbc85cacf1dd7c65a763fc2475ec85117212702e170d2c5554fd665e1b4d668` |
| `test_reference.py` | `0b87e786621d164e97c665fff19f26666afde2bbd4c98bd687502f51c4ec4e30` |
| `fixture.py` | `2692356e69de38a970e351e2a3be0fbb064e5db49abe310d419ab8011737f5a1` |
| `scorer.py` | `2b1306171513f535fc1077ce91b726a02609293bfa008027dd9a459a39338c8c` |
| `verify.py` | `762cd297440ede24b7dfcb423b6949144a64d621f8819919f3637b8b3c6f532a` |
| `check_licensing.py` | `e0fb92e8b83da57c2ba36811c605329ca4fd15e0055fdd543fc87a74b635f995` |
| `contract.json` | `c03acab0a218c428eed1556e57c19e1c92d54b45869ed9389a7bdf7a2dd6920a` |
| `adapter.json` | `15d96eb71f735db575782d4bcdf1e37b6939663754147ad9b2e61a5a07a277b9` |
| `provider.json` | `549fbd9067b52b1f07d6c6f67d8630fe47eac3d259f93c869edb65cdcea53b35` |
| `report.json` (file bytes) | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` |
| `report.json.sha256` (file bytes) | `985c077d1d9db073b9e71eb25ffba439bc4e113896928774653ebafd559db772` |
| `crosscheck.json` (file bytes) | `2980e163d8e8c1f53519eb1a3949b6489808fb273083fbe3fa30beb889c15134` |
| `crosscheck.json.sha256` (file bytes) | `86d99f40c8f2b2636022f15412450821dfedac0cf3107e281eb80dcc266d53fc` |
| `provider/CMakeLists.txt` | `1a725f819b069fab726f8e3edc93a7a12d8eb4a25b4ae89eb5b5ac2b273aecf8` |
| `provider/soundtouch_reference_provider.c` | `a63e1205dd3cf6f4bdfa55a93f40fa4fd58fda8486cc4b3c6c1855928fec10dd` |
| `provider/expected_vectors.h` | `a351b93196e7a69a0a4ea8cf28a27f2a9bb24afa042c716e0162707bd199e30a` |
| `provider/config/config.json` | `42ad853605cd6c5e8ccc57830aa88eb2bd12acb3950abcc2be4aacc97079335b` |
| `provider/config/descriptor.h.in` | `dccba2f55308a6a4a287660b5f98c6c32a62af35004e3f04b6f10774517f1613` |
| `provider/tests/test_provider.c` | `7fc7d2586f4a3adcaa415f389b6dcc8d415fa397071a43665190348c3fb44cf0` |
| `provider/consumer_result.json` | `92575681685be5eb341378e37efe6eb485b47f5a47389c146358a6a7bad00ddd` |

Canonical report digest: `7eb9dd49ac1e18e91b23b3e6addc74fe3a15e2ad0e67ce5117b1f1c452e1700b`.
Canonical crosscheck digest: `0811ae8f8899b6cec35cb432e9921719daff4eabe0f4f402fe3aa7dcd6c526b3`.
C content digest: `fe7f7b331f5ce396fa2fbd7d69f9b8a245f41ed30ce4cc276dc56bcf314924d7`
(`10854` content samples, `78` frames, `922` buffered non-content samples,
final frame valid count `91`).

## Results summary

- Python acceptance suite: **40/40** passed.
- SDK baseline CTest: **11/11** passed after build/install.
- Consumer with `AS_ENABLE_SOUNDTOUCH_REFERENCE=OFF`: **1/1** passed; provider
  unlinked and unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_SOUNDTOUCH_REFERENCE=ON`: **1/1** passed; registration,
  duplicate rejection, descriptor/config gating, session-level invalid-frame
  rejections, throwaway-session range rejection, 78-frame Python/C parity,
  rate clock, final partial frame, drain completion and ordered reset replay.
- `verify.py`: PASS (strict JSON, sources manifest, pins, canonical report,
  three cold-start byte-identical repeats, crosscheck, scope, generated header,
  licensing, DEFER). `check_licensing.py`: ok, 13 explicit SPDX files and 10
  aggregate REUSE-annotated files, 0 problems.
- REUSE 6.3.0 repo-wide lint: clean, 1052/1052 files covered, 0 invalid SPDX
  expressions. The main repair is retained; this task introduces no invalid
  SPDX literal or repair to any other task's files.
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
  result qualifies a candidate. Source-reported historical figures from the
  pinned notes are kept separate and are not results of this package.

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

## Adverse cases and explicit non-claims

Status is `proposal_only_not_qualified`; candidate status is
`proposal_only_not_qualified_synthetic_reference`; boundary status is
`conditional-blocked`; decision is `incomplete`; promotion is `defer`;
production exposure is `DEFER`. No gate is weakened and no missing result
qualifies a candidate.

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
- **BLK-04** — The upstream SoundTouch 2.4.1 library (LGPL-2.1 or commercial) is
  not vendored, built, licensed-review-verified or benchmarked. Reopen with
  pinned upstream source or licensed runtime, license/notice review, versioned
  integration and independent comparison under the release profile.
- **BLK-05** — The C provider is unregistered, opt-in and not part of the
  installed SDK, any descriptor registry or the default build. Reopen with
  explicit provider intake, rights/license review, a versioned public-surface
  decision and independent review.
- **BLK-06** — Pinned source findings for real SoundTouch (duration within two
  samples, local RTF, F0 shift and paired Whisper deltas) are historical
  source-reported evidence, not results of this package. Reopen by reproducing
  that protocol on permitted held-out material with rights clearance and keep
  it separately labeled from synthetic results.

No real weights, downloads, licensed runtime, target-device timing, listening
result, release qualification, shared build changes, board/handoff/ruleset edit,
`main` change, other-task change or gate weakening is claimed or included.
