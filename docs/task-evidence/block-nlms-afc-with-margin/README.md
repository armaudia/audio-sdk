# Block-NLMS AFC with gain margin — task-local reference evidence

`SDK-BLOCK-NLMS-AFC-WITH-MARGIN`. Optional, synthetic, model-free reference only.
Nothing in this bundle is installed, registered by default, or admitted to the
public catalog. The installed v0 format is fixed: 16 kHz, mono, f32, 160 samples.

## Scope and boundary

- The Python reference (`fixture.py`) implements a causal block-NLMS FIR with a
  caller-supplied playback reference and a fixed −3 dB output margin. The
  reference block for frame *k* is the loudspeaker signal that returned during
  that frame; the loop delay is 160 samples. No whole-clip look-ahead occurs.
- The C provider (`provider/src/afc_provider.c`) uses the public
  `provider_v0.h` registration boundary and `session_v0.h` facade. The caller
  owns the registry and registers explicitly with `as_register_provider_v0`.
  No descriptor registry, config schema, default, installed behavior or shared
  CMake file is modified. `AS_ENABLE_AFC_MARGIN_PROVIDER=OFF` is the default.
- The model uses one required caller asset: a pinned immutable f32-LE playback
  reference. It is copied into provider state at create; no file access,
  discovery, model or download occurs in process/drain.
- The C and Python references agree to f32 rounding on the pinned 30-frame
  cohort; the C-provider f32 digest is pinned in the C test, and the Python
  digest is published in the report. They are not mixed into one score.

## Pinned inputs

See `SOURCES.sha256`. The board snapshot is read-time only; it is mutable shared
state and cannot qualify or disqualify a result.

| Source | SHA-256 |
| --- | --- |
| `research/feedback_control_20261028.md` | `47b17e68a943e5fe3ee1568c81a84ea07eba040011e1d97df1ce61d8800c6b1c` |
| `plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Local artifacts

`contract.json` pins every generated artifact. Key digests:

- `report.json`: `f7326732ffea56f5c8a156df5087ac33b1204e28421350470d4338cdf249c1de`
- fixture digest: `1404c7d698fda9d24b5e754f0875dba38c49f5dcc320d689ed4793f6480fead1`
- C-provider f32 output digest (30 frames): `8255cfecc6e02a4f61f6e89c4e8fae0d1b6107a7dd1f717dad514c80a4232503`
- playback reference asset: `b8edcf122d6494d3c2a41f999ed6094c2e4e4ac2f9a1c4a3d548d431766d1aee`

## Reproduction

From the repository root:

```sh
# Python reference and verification
cd docs/task-evidence/block-nlms-afc-with-margin
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s tests -v
PYTHONDONTWRITEBYTECODE=1 python3 tools/verify.py

# Byte-identical regeneration (stdout has no trailing newline)
PYTHONDONTWRITEBYTECODE=1 python3 report.py > /tmp/report.json
cmp /tmp/report.json report.json

# Frozen f32 fixtures
PYTHONDONTWRITEBYTECODE=1 python3 tools/generate_fixtures.py
(cd fixtures && shasum -c FIXTURES.sha256)

# Build and install the unmodified SDK to a temporary prefix
cmake -S . -B /tmp/afc-sdk-build -DCMAKE_BUILD_TYPE=Release
cmake --build /tmp/afc-sdk-build -j4
cmake --install /tmp/afc-sdk-build --prefix /tmp/afc-sdk-install

# Consumer: OFF must show the provider absent; ON registers it explicitly
cmake -S docs/task-evidence/block-nlms-afc-with-margin/provider \
  -B /tmp/afc-provider-off -DCMAKE_PREFIX_PATH=/tmp/afc-sdk-install
cmake --build /tmp/afc-provider-off -j4
ctest --test-dir /tmp/afc-provider-off --output-on-failure

cmake -S docs/task-evidence/block-nlms-afc-with-margin/provider \
  -B /tmp/afc-provider-on -DCMAKE_PREFIX_PATH=/tmp/afc-sdk-install \
  -DAS_ENABLE_AFC_MARGIN_PROVIDER=ON
cmake --build /tmp/afc-provider-on -j4
ctest --test-dir /tmp/afc-provider-on --output-on-failure

# Boundary measurement CLI (writes only under /tmp)
/tmp/afc-provider-on/afc_cli \
  docs/task-evidence/block-nlms-afc-with-margin/fixtures/mic_loop.f32 \
  docs/task-evidence/block-nlms-afc-with-margin/fixtures/reference_loop.f32 \
  /tmp/afc-cli-output.f32 afc_margin 1 0
```

## DSP evidence summary

All figures are from deterministic synthetic signals; see `report.json` for the
full per-frequency, per-case and per-offset records.

- **Geometry/causality:** impulse peak at sample 0, silence output exactly zero,
  step response finite, added/buffering delay 0 samples.
- **Sweeps:** 13 tones from 200–4000 Hz; late-ERLE residual −26.8 to −41.2 dB,
  all below −10 dB. Chirp mean ERLE 13.8 dB, final-20-frame 18.1 dB.
- **Step/convergence/tracking:** step settles in 5 frames at a +12 dB ERLE
  threshold; convergence in 12 frames with final ERLE 14.9 dB and misalignment
  −0.95 dB; path change retracks in 11 frames with final misalignment −0.02 dB.
- **Reference latency:** best offset is 0 samples; white-noise probe gives
  33.0 dB aligned ERLE. Misaligned offsets degrade or fail to cancel.
- **Double-talk:** adaptive and fixed-gain groups reported separately with
  distinct program-SDR and near-end RMS ratios; no merged score.
- **Clean-speech bias:** continuous speech with no acoustic path reports the
  adaptive filter's effect on wanted speech separately from the fixed control.
- **Closed loop (6 cases):** recursive loop, 160-sample delay, gains 1.05–1.30,
  linear/pre-tanh/post-clip/dual-path conditions. In every case,
  `afc_plus_margin` has a lower tail level than `afc_only`; the fixed-gain
  control is reported separately and is not used to qualify the adaptive path.
- **Numerical/state controls:** missing/invalid/nonfinite/out-of-range config,
  wrong-shape/nonfinite/stale-epoch/wrong-position frames, reset-to-fresh,
  independent sessions, drain and close all pass; state is unchanged on
  rejection.

## Blockers and reopening conditions

This evidence does **not** authorize production use. Exact blockers:

1. No measured acoustic loop, loudspeaker/microphone impulse response,
   gain-before-feedback margin, path-change recording or delay-drift record.
2. No real-speech intelligibility or quality assessment, listening test,
   MOS/STOI, or speaker/path-held-out false-cancellation study.
3. No target-device latency, CPU/memory, deadline or pacing measurement.
4. No provider intake, license/catalog review, default admission or installed
   registry change.
5. No benchmark bundle or hosted claim under the current submission policy.

Reopen when all of the above are supplied and validated under the applicable
policy; only then may a separate task propose a public/default change.
