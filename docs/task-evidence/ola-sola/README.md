# SDK-OLA-SOLA — task-local OLA/SOLA reference evidence

A deterministic, synthetic-only reference for overlap-add (OLA) and
waveform-similarity overlap-add (SOLA) time-stretch at the public SDK adapter
boundary. This is **reference evidence only**: the installed SDK, public API,
ABI, descriptor registry, defaults, shared `CMakeLists.txt`, installed v0
behavior and `main` are unchanged. The optional C provider is unregistered and
compiled only by a caller that opts in.

Pinned base: `d665c298e8cce8b4d576dc45f3c7f7d3b3457425`.
Branch: `swarm/SDK-OLA-SOLA`.
Provider ID when explicitly registered: `rate.ola-sola-reference.v0`.

## Scope and boundary

- Installed v0 remains 16 kHz, mono `f32`, 160-sample frames. No variable-frame
  playback actuator is installed.
- Whole-clip and 160-frame streaming TSM fixtures are task-local only.
- `reference.py` is the deterministic OLA/SOLA engine, fixture generator and
  report model. `run.py` writes the canonical report, digest sidecar and C
  parity header. `test_reference.py` contains the acceptance suite.
- `provider/` is a standalone opt-in consumer project. Its only SDK includes
  are `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`. The option
  `AS_ENABLE_OLA_SOLA` is **OFF** by default; `ON` compiles and registers one
  caller-local provider.
- `SOURCES.sha256` pins every file in this directory except itself.
  `contract.json` records the task contract, exact pins and artifact digests.

## Exact source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | §5.1 OLA/SOLA, §6.5 smoothing/clamping, §8 integration. |
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
TMP=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/ola-sola-check
cmake -S "$SDK" -B "$TMP/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMP/sdk-build" --parallel 4
ctest --test-dir "$TMP/sdk-build" --output-on-failure
cmake --install "$TMP/sdk-build" --prefix "$TMP/sdk-prefix"

cmake -S provider -B "$TMP/provider-off" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_OLA_SOLA=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-off" --parallel 2
ctest --test-dir "$TMP/provider-off" --output-on-failure

cmake -S provider -B "$TMP/provider-on" -DCMAKE_PREFIX_PATH="$TMP/sdk-prefix" \
  -DAS_ENABLE_OLA_SOLA=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMP/provider-on" --parallel 2
ctest --test-dir "$TMP/provider-on" --output-on-failure
```

Read-only checks from the worktree root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-OLA-SOLA
git diff --check
```

## Local artifact digests (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `reference.py` | `bdb43b1aaf69b19c6ecce41463e2e45ed55fcf53bb84275983da8f3f20085b9d` |
| `run.py` | `13044a56d51ef057eb04ede79fdfb9c5751b534eedcac4674ad39736ed655ee9` |
| `test_reference.py` | `9ae017422bec72450aa9c1feff91eb4e275a21f6c1a185a07fced618cd8a9684` |
| `report.json` (file bytes) | `90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93` |
| `report.json.sha256` (file bytes) | `14fa25612ddefad383179f8af7dd766d387add4baffa6349f60ed700e55a912c` |
| `provider/CMakeLists.txt` | `ee8f3eeeea9610871a320969eb05bb42f85ec7b893aa7620f8b840ca08c762ca` |
| `provider/ola_sola_provider.c` | `8cf4a79bac0918e3809f81942b7088736f42c89c49d5eea1e8778d19a89fcdec` |
| `provider/expected_vectors.h` | `a87f049c31ec7a96c2bc0d050646465fced8ed80b5de9f5941978265ebe2f455` |
| `provider/config/config.json` | `68ae86e9549fddf6c9b1f83dbba64af198de1fa59df435161212b818f2e18c8e` |
| `provider/config/descriptor.h.in` | `02e4623a3754945fce887045ff88394b05d114560ccb33faa37e740f305d6d41` |
| `provider/tests/test_provider.c` | `e6887da7e607ca0687618e31481db19c900b911037b1611849f289161abbc2b0` |

Canonical report digest: `1e258cf29b929e5f3a70386144fe4be64c7177ed162e0cce6060465221b3cfa2`.
C content digest: `00acf0178b929b262ac2beb36ead79cc9ee691d4715e4ecd69eec073ae232275`
(`10728` content samples, `78` frames, `1304` buffered non-content samples,
final frame valid count `91`).

## Results summary

- Python acceptance suite: **33/33** passed.
- SDK baseline CTest: **11/11** passed.
- Consumer with `AS_ENABLE_OLA_SOLA=OFF`: **1/1** passed; provider unlinked and
  unregistered, built-ins unchanged.
- Consumer with `AS_ENABLE_OLA_SOLA=ON`: **1/1** passed; registration, duplicate
  rejection, descriptor/config gating, frame/config rejections, 78-frame
  Python/C parity, rate mapping, final partial frame, drain completion and
  ordered reset replay.
- Duration mapping: input/identity `12457`, fixed-rate OLA `9984`, dynamic SOLA
  `12032`, varispeed control `9966` samples. Drift/rebuffer observed `12288`
  versus `12473.04` expected, relative error `-0.014835204470072047`.
- Frequency scale on the 220 Hz tonal stimulus: identity and SOLA `220 -> 220`
  Hz (ratio `1.0`); fixed-rate OLA `220 -> 212` Hz (ratio `0.963636`, recorded
  as pitch modulation); varispeed control `220 -> 274` Hz (ratio `1.245455`,
  adverse control that must shift pitch).
- Rate updates at source samples `4800`, `8000` and `11200` are all recorded
  with local adjacent-delta checks and source-map bounds. An unsmoothed
  rate-step adverse control is reported separately.
- Final partial window: `137` valid input samples, target `91` output samples,
  finite output, peak `1.0`, explicit output digest.
- Streaming reset replay is bit-exact and source-offset aware. Whole-clip and
  160-frame streaming digests intentionally differ because streaming is causal
  with bounded lookahead; this is recorded as `expected_lookahead_difference`.
- Overlap-add denominator normalization on the stationary tonal stimulus gives
  RMS ratio `0.999234` versus `0.981008` unnormalized.
- All reported outputs have zero nonfinite and zero clipping samples; no
  missing result qualifies a candidate.

The SDK drain API masks tail padding as zero-valid output and loops internally
until end-of-stream. With the descriptor's `max_drain_calls=16`, the public
drain call returns `AS_END_OF_STREAM` without a backend failure. The buffered
non-content count (`1304` for the C vector) remains pinned in the Python model
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
- **BLK-02** — No target-device pacing, fill/flush, CPU, memory, deadline or
  availability measurement was run. Reopen with a paced target workload and
  resource telemetry under the intended profile.
- **BLK-03** — No listening test, real-speech corpus, intelligibility score,
  model or release-quality assessment was run. Reopen with held-out permitted
  speech, matched controls, authorized scoring and rights review.
- **BLK-04** — The C provider is unregistered, opt-in and not part of the
  installed SDK or descriptor registry. Reopen with explicit provider intake,
  rights/license review, a versioned public-surface decision and independent
  review.

No real weights, downloads, licensed runtime, target-device timing, listening
result, release qualification, shared build changes, board/handoff edit or
`main` change is claimed or included.
