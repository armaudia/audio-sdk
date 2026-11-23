# SDK-CLASSICAL-SPECTRAL-SUBTRACTION — task-local evidence

Optional, task-local classical spectral-subtraction reference provider. It is
compiled only by a caller that opts in; nothing in this directory is installed
by the SDK, registered by default, or linked into installed v0 behavior.

Pinned base: `9677040cba2929f9936eaa565f200f585d5270a8`.
Provider ID: `css.reference.v0`. Required caller asset: `css.noise-profile.f32`
(16384 bytes, f32 LE). External provider settings must be `{}`.

## Reproduction

Build and install the SDK from this worktree into a temporary prefix:

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
  -DCMAKE_PREFIX_PATH=<tmp>/prefix -DAS_ENABLE_CSS_PROVIDER=OFF
cmake --build <tmp>/consumer-off && ctest --test-dir <tmp>/consumer-off --output-on-failure

cmake -S <task>/provider -B <tmp>/consumer \
  -DCMAKE_PREFIX_PATH=<tmp>/prefix -DAS_ENABLE_CSS_PROVIDER=ON
cmake --build <tmp>/consumer && ctest --test-dir <tmp>/consumer --output-on-failure
```

Regenerate and verify the deterministic evidence:

```sh
python3 <task>/tools/generate_fixtures.py
python3 <task>/tools/evaluate.py \
  --cli <tmp>/consumer/css_cli \
  --profile <task>/fixtures/noise_profile.f32 \
  --work <tmp>/eval \
  --sources-sha <task>/SOURCES.sha256 \
  --fixture-manifest <task>/fixtures/FIXTURES.sha256 \
  --build-info <tmp>/prefix/share/audio-sdk/build-info.json \
  --controls-ok true
python3 <task>/tools/verify.py \
  --cli <tmp>/consumer/css_cli --work <tmp>/eval \
  --build-info <tmp>/prefix/share/audio-sdk/build-info.json --controls-ok true
```

`verify.py` checks every digest in `SOURCES.sha256` and
`fixtures/FIXTURES.sha256`, regenerates the report and fails unless
`evidence/report.json` is byte-identical.

## Results summary

- Full SDK suite: 11/11 CTest tests passed.
- Consumer with `AS_ENABLE_CSS_PROVIDER=OFF`: 1/1 passed (built-ins only,
  unlinked CSS provider absent).
- Consumer with `AS_ENABLE_CSS_PROVIDER=ON`: 1/1 passed (registration,
  duplicate rejection, descriptor/settings/assets/mode controls, nonfinite,
  wrong shape, stale epoch/session, reset/interleave, partial-final alignment
  and drain, isolated registry).
- Paired synthetic cohort: 3 pairs × 3 modes; mean ΔSI-SDR CSS **+1.352 dB**,
  Speex baseline **+2.182 dB** versus the noisy identity control.
- Mean ΔSTOI screen CSS **-0.050**, Speex **-0.075**; the pinned synthetic
  screen is not standard STOI and is reported without a pass/fail gate.
- Clean-speech preservation: ΔSI-SDR **+16.922 dB**, RMS ratio **0.818**.
- Output integrity: 0 nonfinite samples, maximum absolute peak **0.667086**,
  complete coverage, no collisions and no out-of-range samples.
- Alignment: 160-sample buffering delay, 160 startup-padding samples per
  processed fixture, duration preserved one valid sample per accepted sample.

See `evidence/REPORT.md` and `evidence/report.json` for the full records and
`SOURCES.sha256` / `fixtures/FIXTURES.sha256` for pinned source and fixture
digests. `report.json` SHA-256:
`304a965bed28b2a84e1bf8234e07f15286edba962cbc74fa2b195f426cb5aa75`.

## Scope and blockers

No real weights, downloads, licensed runtime, listening, real-speech MOS/STOI,
target-device pacing, CPU/deadline measurement or release qualification is
claimed. The historical whole-clip noise estimate is noncausal and is not
reproduced here; this is a causal, caller-profile-driven reference. No shared
CMake files, descriptor registry, defaults, public API/ABI, installed v0
behavior, board, handoffs or main branch were changed.
