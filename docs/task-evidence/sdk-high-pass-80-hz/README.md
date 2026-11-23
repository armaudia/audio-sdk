# SDK-SDK-HIGH-PASS-80-HZ — installed high-pass reference control

This directory is task-local evidence for the pinned installed provider
`dsp.highpass80.v0`. It verifies the existing fixed 80 Hz / 16 kHz mono float32
behavior through the public installed v0 API; it does **not** change the
provider, descriptor, registry, defaults, public API, board, handoffs or any
shared SDK source. No new cutoff, sample rate, frame size, listening score,
corpus result or production workload qualification is claimed.

## Files

| Path | Role |
| --- | --- |
| `harness.c` | C11 installed-consumer probe using only `audio_sdk/session_v0.h`; emits JSON Lines. |
| `stimuli.json` | Deterministic, synthetic fixture definitions and tolerance constants. |
| `verify.py` | Builds the analytic reference, drives the installed library, writes canonical JSON. |
| `test_verify.py` | Unit tests for pins, canonical bytes, scope, DSP results, controls and deterministic regeneration. |
| `report.json` | Canonical result report (no raw timing or bulk PCM). |
| `installed-capture.json` | Canonical captured event metadata and flattened output samples. |

## Pinned inputs

| Input | SHA-256 |
| --- | --- |
| `audio-benchmark-platform/audio-sdk/core/providers/highpass/highpass_provider.c` | `051b423d078835ff1ab23d7303c8e0c8f876d3d4211339682f366797ef7fffef` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/TASKS.json` | `5eea8b61fa70c0e3669ceb878aefc96e9005204f97f1970879583bc710689e80` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `harness.c` | `1ccf81bb7f6542cc00dfd9764029c2030712b0836d0a7410c42c352aac057e8d` |
| `stimuli.json` | `ce82b8d0241a324ede247441356a1f83e9c270eadf3315916e2b95b636f6d142` |
| `verify.py` | `b40d4a1e99c55d04b3a880ee4b9870a7603c4c186c3094e03a2985a5187a77ea` |
| `test_verify.py` | `ed43eff017cb52ecc349d879eebe1fa99804a377c4582f9926a7cbc83400e674` |
| `report.json` | `741babd8aff0e886f10041002213c5556b3a8b11bc69d2028a25c118ffd00d5b` |
| `installed-capture.json` | `5d4b849cfef3e71c68fb20a010a26fcfbe93251111ef5582e7e3de25dd5d6e90` |

The frozen source implements a two-pole 80 Hz high-pass with
`Q = 0.7071067811865476`, double-precision filter state, float32 output and no
buffering delay. The candidate report says two-pole code exists locally for
rumble/DC removal and records no dedicated quality benchmark; this fixture is a
deterministic control, not that missing benchmark. The task entry is
`reference-verification`, owner `agent-sdk-highpass`, reviewer
`reviewer-sdk-highpass`, base `3e2192f5676ffe9d54fd5fc5b7c3710b4bb87f41` and
branch `swarm/SDK-SDK-HIGH-PASS-80-HZ`.

## Build and run outside the worktree

Keep generated artifacts out of the task-local evidence directory:

```sh
SDK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SDK-HIGH-PASS-80-HZ
TASK="$SDK/docs/task-evidence/sdk-high-pass-80-hz"
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/sdk-highpass-build

cmake -S "$SDK" -B "$SCRATCH/build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$SCRATCH/build" --parallel 4
ctest --test-dir "$SCRATCH/build" --output-on-failure --timeout 60
cmake --install "$SCRATCH/build" --prefix "$SCRATCH/prefix"
sh "$SDK/scripts/verify_install.sh" "$SCRATCH/prefix" "$SCRATCH/verify"

cc -std=c11 -Wall -Wextra -Werror \
  -I"$SCRATCH/prefix/include" "$TASK/harness.c" \
  -L"$SCRATCH/prefix/lib" -Wl,-rpath,"$SCRATCH/prefix/lib" \
  -laudio_sdk -lm -o "$SCRATCH/highpass_harness"

PYTHONDONTWRITEBYTECODE=1 python3 "$TASK/verify.py" \
  --prefix "$SCRATCH/prefix" --harness "$SCRATCH/highpass_harness" \
  --output "$TASK/report.json" --capture-output "$TASK/installed-capture.json"

cd "$TASK"
AUDIO_SDK_PREFIX="$SCRATCH/prefix" AUDIO_SDK_HARNESS="$SCRATCH/highpass_harness" \
  PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_verify.py

git -C "$SDK" diff --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SDK-HIGH-PASS-80-HZ
```

## Result summary

- Installed build: `audio-sdk/0.1.0+sha256:0bc71dcab04880033a4ad4c1cfcebb8a05eccb11a20a786b9c844e394c035972`.
- Installed descriptor digest: `d664ddc7977b5ff193e184b12dca48f3923675e8a7f0d4feb79781b0ca7c77e3`.
- Installed high-pass conformance: 40/40 checks pass.
- SDK build tests: 11/11 pass (`as_conformance_highpass` included).
- Installed consumer check: `verify_install.sh` passed for C11 and C++20 consumers and both provider conformance runs.
- Fixture: 25 scenarios, 2,376 processed frames, 380,160 processed samples, 20 invalid/missing/nonfinite controls, 128 checks passed / 0 failed.
- Unit tests: 12/12 pass, including byte-identical double regeneration against the installed prefix. No result is skipped when the installed inputs are supplied.
- Two independent consecutive `verify.py` runs produced byte-identical `report.json` and `installed-capture.json`; raw wall-clock values are excluded from canonical files.

### DSP coverage

- 13 steady tones (20–7800 Hz): measured gain tracks the analytic pinned biquad; 80 Hz is −3.01 dB; no resonant peaking above unity in steady state.
- Log chirp 20–7800 Hz and finite-output check.
- Positive and negative DC steps settle to ~1.9e-15 mean absolute; constant 0.75 DC settles to ~7.3e-15.
- Impulse peaks at sample 0 with first sample `0.978030503` vs analytic `0.9780304792`: zero content delay.
- Exact silence stays exactly zero.
- Synthetic harmonic/formant speech proxy: speech-band gain `+0.0181 dB` vs analytic `+0.0181 dB`, envelope correlation `0.9989`. This is not STOI, real speech or a listening result.
- 20 Hz rumble + speech proxy: rumble attenuation `24.10 dB` vs analytic `24.10 dB`; speech band unchanged.
- Full-scale 1 kHz input: steady-state output peak `0.9940`; finite startup transient peak `1.0761` is the analytic filter transient, not clipping.
- Final partial frame (37 valid), reset to epoch 7 / origin 3200, two drains: exact padding accounting (`123` then `0`), exact delivered/accepted accounting, two zero-produced EOS events.
- Two independent sessions in one registry: bit-identical transformation and distinct epoch coordinates.
- Unpaced single-stream load control: 2,000 frames finite, RTF below 1; no deadline, queue, device or availability claim.

### Controls and adverse cases

All 20 controls fail closed as expected: unsupported rate/channels/frame/mode, null config/id/out/result/frame/input/samples, undersized output capacity, bad source position and recovery via reset, negative reset origin, null drain output/result, and NaN/inf input. Noncontiguous position leaves the session `not_ready` until reset. Nonfinite input returns `invalid_argument`; no nonfinite DSP output is qualified.

Explicitly not claimed: human listening, STOI, corpus scores, audio-bench bundles, alternate frequencies/rates, nonlinear clipping/limiter/VAD interactions, real-time deadlines, multi-device behavior or production workload readiness.

## Scope confirmation

Only files under `docs/task-evidence/sdk-high-pass-80-hz/` were added. No shared SDK source, public API, descriptor, registry, default provider, board file or handoff was edited. The read-only swarm check was run and did not mutate the board.
