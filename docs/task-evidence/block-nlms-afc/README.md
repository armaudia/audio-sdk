# SDK-BLOCK-NLMS-AFC — task-local evidence

Optional, task-local Block-NLMS acoustic feedback cancellation reference at the
public v0 provider boundary. It is compiled only by a caller that opts in;
nothing in this directory is installed by the SDK, registered by default, or
linked into installed v0 behavior.

Pinned base: `dc6b8ecb5c7fa0a6a00072ddf9c6a2e168b68acc` · branch:
`swarm/SDK-BLOCK-NLMS-AFC`.

Provider ID: `dsp.block-nlms-afc.afcref.v0`. Required caller asset:
`afc.playback-reference.f32` (f32 LE, 20,224 bytes; 5,056 samples). The asset
prefix is 256 samples; playback sample 0 is at asset index 256. External
provider settings must be `{}`. The CMake opt-in switch is
`AS_ENABLE_BLOCK_NLMS_AFC` and is `OFF` by default.

## Public boundary

Only `as_provider_table_v0` from `api/include/audio_sdk/provider_v0.h` and
`as_session_v0.h` are used. No public API/ABI, descriptor registry, default,
installed provider, shared CMake file, board record or handoff was changed.
The explicit playback reference is a caller-owned, descriptor-pinned asset; a
missing, wrong-id, wrong-size, wrong-digest or nonfinite asset fails create.
There is no implicit far-end inference.

The installed v0 format remains 16 kHz mono f32, 160 samples per frame. The
provider declares `buffering_delay_samples: 0`, `native_hop_samples: 160`,
`execution_modes: [2]` (processing thread) and `max_drain_calls: 1`. A partial
final `as_frame_v0` is zero-padded for the fixed 160-sample block update and
reported with `AS_RESULT_FINAL_PADDING`.

Live streaming delivery of a playback reference is **not** available in v0:
`as_frame_v0` has no reference field. This reference uses a pinned asset that
contains the actual playback sequence in frame order. An offline leading
reference is generated only for the alignment sweep and is explicitly marked
noncausal for live streaming.

## Reproduction

Build and install the unmodified SDK from this worktree into a temporary
prefix:

```sh
cmake -S <repo> -B <tmp>/sdk -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_LIBDIR=lib -DAS_BUILD_TESTS=OFF \
  -DAS_BUILD_CONFORMANCE=OFF -DAS_BUILD_EXAMPLES=OFF
cmake --build <tmp>/sdk --parallel 4
cmake --install <tmp>/sdk --prefix <tmp>/prefix
```

Build the opt-in consumer with the provider disabled and enabled:

```sh
cmake -S <task>/provider -B <tmp>/consumer-off \
  -DCMAKE_PREFIX_PATH=<tmp>/prefix -DAS_ENABLE_BLOCK_NLMS_AFC=OFF
cmake --build <tmp>/consumer-off && ctest --test-dir <tmp>/consumer-off --output-on-failure

cmake -S <task>/provider -B <tmp>/consumer-on \
  -DCMAKE_PREFIX_PATH=<tmp>/prefix -DAS_ENABLE_BLOCK_NLMS_AFC=ON
cmake --build <tmp>/consumer-on && ctest --test-dir <tmp>/consumer-on --output-on-failure
```

Regenerate and verify the deterministic evidence:

```sh
python3 <task>/tools/generate_fixtures.py
python3 <task>/tools/evaluate.py
python3 -m unittest discover -s <task>/tools -p 'test_*.py' -v
python3 <task>/tools/verify.py --workspace <workspace>
```

`verify.py` checks all 12 entries in `SOURCES.sha256`, all 7 entries in
`fixtures/FIXTURES.sha256`, 5 pinned external sources/boundary headers, all 17
required report sections, recursively rejects absent or nonfinite results, and
fails unless `evidence/report.json` regenerates byte-identically.

## Results summary

- Full SDK suite with default test/conformance targets: **11/11** CTest tests passed.
- Consumer with `AS_ENABLE_BLOCK_NLMS_AFC=OFF`: **1/1** passed (built-ins only,
  unlinked AFC provider absent).
- Consumer with `AS_ENABLE_BLOCK_NLMS_AFC=ON`: **1/1** passed (registration,
  duplicate rejection, descriptor/settings/assets/mode gates, nonfinite and
  shape controls, epoch/position controls, block-NLMS residual reduction, reset
  reproducibility, partial-final alignment, drain, interleave isolation and
  isolated registry).
- Python reference suite: **9/9** passed.
- Echo-return loss: early 3.795 dB, steady (frames 80–159) 8.040 dB, final
  9.082 dB; 6 dB trailing mean at frame 23, 9 dB at frame 104.
- Tracking: 6.583 dB before path change, 8.291 dB immediately after, 7.477 dB
  late; recovery within 3 dB at frame 0 of the reporting window.
- Double talk: 1.511 dB ERLE versus 7.999 dB echo-only; near-end SDR 8.607 dB;
  bias is reported, not qualified away.
- Frequency sweep min/max ERLE: 41.953 / 44.287 dB; chirp ERLE 7.614 dB.
- Waveform controls: impulse/step added delay 0 samples; silence peak 0;
  clean-speech RMS ratio 1.0 and envelope correlation 1.0 (synthetic screen,
  not standard STOI).
- Simulator-relative gain-before-feedback: max stable loop gain identity 0.6,
  AFC 1.2, AFC margin 1.6, fixed margin 1.2; AFC margin +8.519 dB versus
  identity. Tail at loop gain 0.8 is -41.655 dB versus -15.157 dB identity.
- Adverse controls at loop gain 1.2 include dual paths, pre-tanh nonlinearity
  and post-clip limiting; rejections and sustained identity feedback are
  reported as fail-closed outcomes, never as wins.

See `evidence/REPORT.md` and `evidence/report.json` for the full records.
Key digests:

- `SOURCES.sha256`: `26522ccb48ec9ad14eb763c97beaf50c3ec9142f74d965e7591e573b8f509efa`
- `fixtures/FIXTURES.sha256`: `0fe388c234e65865c51e2919415605bf8050fd2d2de81ad424e2c9f2fb4d4ddf`
- `evidence/report.json`: `8f61033f4a27ccfa1cd0e0193c5a9b4ba022fd0f38144fc940005941a528a069`

## Full file list

```text
SOURCES.sha256
README.md
evidence/REPORT.md
evidence/report.json
fixtures/FIXTURES.sha256
fixtures/impulse.f32
fixtures/near_end.f32
fixtures/playback_a.f32
fixtures/playback_b.f32
fixtures/reference_asset.f32
fixtures/silence.f32
fixtures/step.f32
provider/CMakeLists.txt
provider/config/config.json
provider/config/descriptor.h.in
provider/src/block_nlms_afc_provider.c
provider/src/block_nlms_afc_provider.h
provider/tests/test_provider.c
tools/afc_reference.py
tools/evaluate.py
tools/generate_fixtures.py
tools/test_reference.py
tools/verify.py
```

## Scope, blockers and reopening conditions

No measured acoustic room or loop, real weights, licensed runtime, listening
test, target-device timing, CPU/deadline measurement, release claim, board or
handoff mutation, shared-file change or installed v0 behavior change is
claimed. All DSP evidence is deterministic analytic or seeded synthetic data.

Reopening qualification requires, in order: (1) a live reference delivery path
through a future public API extension with a reviewed ABI contract; (2) a
measured acoustic loop and device with pinned geometry and gain calibration;
(3) listening/MOS and real-speech evaluation with rights cleared; (4) target
device pacing, CPU/deadline and RSS measurements; (5) descriptor intake,
license and release review. Until then every gate has `release_gate: blocked`
and `release_qualification` is `not_performed`.

Delivery: pull request
https://github.com/armaudia/audio-sdk/pull/45 was opened against `main` without
merging. The evidence commit at PR creation was
`aa4556b9d503541b290be19dc6a86266533c89a9`; the exact final delivery head SHA
is recorded in the task response.
