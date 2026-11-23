# SDK-NARROW-BIQUAD-NOTCH — optional deterministic narrow biquad notch fixture

Task-local, model-free, synthetic-only DSP evidence for an explicitly configured
RBJ notch filter at the public SDK v0 provider boundary. Status is
**proposal-only / synthetic** and the qualification fields in `report.json` are
`incomplete` because real speech, listening and measured nonlinear/device
qualification are blocked. The installed SDK, ABI, descriptors, registry,
defaults and frozen v0 behavior are unchanged.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame. No partial-frame
  or alternate-rate qualification.
- `fixture.py` designs a double-precision RBJ notch from explicit
  `frequency_hz` and `bandwidth_hz` (`Q = f0 / bandwidth`), processes frames with
  transposed direct-form-II state, and generates all stimuli and metrics.
  Optional explicit `q` must match the derived Q; zero/NaN/inf are rejected.
- `provider/` is an optional C reference compiled only with
  `AS_ENABLE_NARROW_NOTCH=ON`. It uses only `audio_sdk/provider_v0.h` and
  `audio_sdk/session_v0.h`, is never installed, registered by default or added
  to a catalog. The caller registers it explicitly on one registry.
- The SDK facade admits empty settings for external providers, so the explicit
  `(frequency_hz, bandwidth_hz)` selection is carried in a caller-local
  provider ID (`dsp.narrow-notch-<f0>-<bw>.v0`). A nonempty settings object is
  rejected by the facade and is exercised as a control.
- Write scope is exactly this directory. No shared SDK source, CMake file,
  descriptor, registry, board or handoff was modified.

## Source pins (SHA-256)

| Source | SHA-256 |
| --- | --- |
| `research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

The research record states that narrow-notch code exists locally without a
dedicated real-speech benchmark; the candidate list repeats that finding. This
fixture is the deterministic control for that gap, not the missing benchmark.
The DSP profile in `VERIFICATION.md` requires sweeps, steps, impulses, silence,
clean speech and an intelligibility/load-specific control, plus gain, response,
attack/release, headroom, delay, numerical behavior, state transitions and
interacting nonlinear configurations.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `fixture.py` | `20bc26ca1b88b2680911330d171186781437a665ee70a59f432370c35d1b4dfa` |
| `generate.py` | `c72b5f952553807641dd5edef880a0125f8dd305e0fe49698329faa7714ec110` |
| `test_fixture.py` | `3d527dfa52c28ac2d11de8f27ff439472244e1dee62e09dde118ee4f6e715416` |
| `report.json` | `c80db3087434ed0e8d5755b037e052ff3dfa5ae03d582f858ba76526253e99dd` |
| `contract.json` | `8a8f36803538846a35f6128c755aa72c12f0e60c674a7505984a842a8db1a7bc` |
| `provider/narrow_notch_provider.c` | `935423930613bb18f9fc088380f6b900a4317f033f468a50d7c347b2c3a487cc` |
| `provider/narrow_notch_provider.h` | `5800a7ad3d7aa6f201a21693a1cd6aba43491d5c0d0e2625fd563264341f358f` |
| `provider/CMakeLists.txt` | `138058c68ee07d877140f5a4023b7c53cc55e8f72f0bc0ed0c7515c5dd57c7bf` |
| `provider/config/config.json` | `a400ceffe5929247e720c6e2a2c2380775e41995df2fd3eb508da11b5ebd019d` |
| `provider/config/descriptor.h.in` | `35700de703e72fd9da78378867dc446f53d00a1910db8c21ce7dafa6ea4e536d` |
| `provider/tests/test_provider.c` | `1f45a967cad364a376fd2b5c6bf3c42464bbdc0d17b65bf89458a7b872f0528f` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`); its file digest is also the canonical report digest above.
`fixture_digest` inside the report is
`b98e9b2a711dce687ec62002eb72487df871b7ce10aaaa2864d831258327fb22` and pins
the format, controls, seeds, sweep grid and loop constants.

## Exact reproduction commands

From the worktree root, with builds outside the worktree:

```sh
SDK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-NARROW-BIQUAD-NOTCH
TASK="$SDK/docs/task-evidence/narrow-biquad-notch"
SCRATCH=/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/narrow-notch-build

cmake -S "$SDK" -B "$SCRATCH/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$SCRATCH/sdk-build" --parallel 4
ctest --test-dir "$SCRATCH/sdk-build" --output-on-failure
cmake --install "$SCRATCH/sdk-build" --prefix "$SCRATCH/prefix"

cmake -S "$TASK/provider" -B "$SCRATCH/provider-off" \
  -DCMAKE_PREFIX_PATH="$SCRATCH/prefix" -DAS_ENABLE_NARROW_NOTCH=OFF \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$SCRATCH/provider-off" --parallel 2
ctest --test-dir "$SCRATCH/provider-off" --output-on-failure

cmake -S "$TASK/provider" -B "$SCRATCH/provider-on" \
  -DCMAKE_PREFIX_PATH="$SCRATCH/prefix" -DAS_ENABLE_NARROW_NOTCH=ON \
  -DCMAKE_BUILD_TYPE=Release
cmake --build "$SCRATCH/provider-on" --parallel 2
ctest --test-dir "$SCRATCH/provider-on" --output-on-failure

cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 python3 generate.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -c "import json; [json.load(open(f)) for f in ('contract.json','report.json')]; print('json ok')"

cd /Users/htsakanyan/workspace/audio/audioml
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-NARROW-BIQUAD-NOTCH

git -C "$SDK" diff --check
```

Results observed:

- SDK build tests: 11/11 passed.
- Optional C consumer OFF: 1/1 passed (unlinked/unregistered, built-ins unchanged).
- Optional C consumer ON: 1/1 passed (two explicit `(f0, bw)` registrations,
  tone attenuation, invalid controls, stale epoch, reset, drain, close).
- Python fixture tests: 21/21 passed. JSON validation passed.
- Two consecutive `generate.py` runs produced byte-identical `report.json`;
  no wall-clock value enters canonical artifacts.
- Read-only swarm check exited 0; `git diff --check` passed.

## Expected counts and key digests

From `report.json` `counts`: 16 conditions, 78 sweep frequencies, 4 explicit
centre/bandwidth pairs, 12 adverse config cases, 5 adverse frame cases, 4 source
pins, 2 boundary pins, 2,000 load frames, 1,320 long-stability frames,
8,168 processed frames and 1,306,880 processed samples.

| Result | Key values | f32 output digest |
| --- | --- | --- |
| silence | peak 0.0 | `c65206769723a13afe80c0d925531639ceef9c2eb97eee3b1b542739ec40597f` |
| impulse | peak at sample 0, 0.490613 | `2cf94e6dfec4b128902b92aa5b2464275ef3f0afe4dd6a237a8ad50c8032ae88` |
| step | steady mean 0.25, transient crossing 72 samples, peak 0.269297 | `adcb7d0bba8ed970102fdaab0ac9f9e3f8c5494a956826120c118be5b2dd5d18` |
| chirp | 40 frames, finite, peak 0.092257 | `310a53b82515af9905bcd705ea787e13abfdb8848c1b08f1c5266963571ff9c3` |
| frequency sweep | 78/78 analytic matches, max error 0.006 dB, centre gain 0.004751 | `dad78e813f4d8243c83aa7d724cd1ef95b814b91874df4700be9c511398f8aba` |
| explicit f0/bw controls | centre gains 0.004388–0.007645, skirt gains 0.993076–1.002146 | `9e4717705c800e3e112f34d44a7d57c65aed84cdc7b9e7996e1479d2a3dbebb2` |
| attack/release | 700 Hz probe, attack 0 frames, release 1 frame | `2af71f440d76c78e9dac2bd3a0fe6e5494e281b944d1f35b0a4c5af6c9c486ab` |
| clean synthetic speech | 300 frames, RMS delta −0.056 dB, envelope correlation 0.999763 | `4e9ba0d5abe102f245c241c134c83bc45e1288c4d116a187051651d91dd450c1` |
| 1 kHz tone in speech | 24.518 dB tone-power reduction | `85f7adbf5d07ee8f96ccaffa01db2d73a105126460a97e2fa3d358f7b366fa48` |
| load control | 2,000 frames, finite, no timing claim | `275f77fc62e3df16590f0ec5571c47ac7e93dfe70c77a9b5a371bf6d13fe7ded` |
| long stability | 1,320 frames, 0 rejected, tail RMS 0.0 | `a9df5f0b3d5e8c618e04e0586eadf35e343e6aa340c8eea8a130dadaf56c693a` |

## DSP evidence summary (synthetic)

- Gain/response: the 100 Hz–7,800 Hz sweep tracks the analytic biquad to
  0.006 dB away from the exact notch zero; centre gain is 0.004751 (noise
  floor of the generator), and passband gain stays within 1.0005. Four explicit
  `(f0, bw)` pairs (1000/100, 120/12, 250/25, 4000/400 Hz) all give `Q = 10`,
  reject the centre tone below 0.008 gain and pass a skirt tone at `f0 + 5·bw`
  above 0.99 gain.
- Delay/headroom: the impulse peaks at sample 0 (no added buffering delay);
  the step has a finite IIR transient but settles to 0.25. Full-scale headroom
  is not claimed; all generated levels are bounded and finite.
- Attack/release: a static notch has no detector attack; the 700 Hz probe
  starts in frame 20 with 0-frame onset delay and decays below the release
  threshold in 1 frame after frame 120.
- Speech impact: the synthetic formant proxy changes RMS by −0.056 dB with
  envelope correlation 0.999763 versus bypass. This is not STOI, intelligibility
  or a listening result. A 1 kHz tone injected into that proxy is reduced by
  24.518 dB while the untouched region is measurable separately (the notch
  also removes natural speech energy there; no "no impact" claim is made).
- Load-specific control: 2,000 frames / 320,000 samples are processed with
  exact counts, finite outputs and a fixed digest. No RTF, deadline, pacing or
  device availability is claimed.
- Numerical behavior/state: rejections leave the state digest unchanged;
  long silence plus alternating impulse trains stay finite, bounded and
  zero-rejected; two sessions hold distinct state and output; reset with a
  strictly greater epoch clears state without touching the other session.
- Interacting nonlinear configurations: a frame-causal feedback loop at gains
  1.05/1.15/1.30 compares bypass, notch and notch plus tanh saturation. At
  1.05 the notch tail is −71.266 dB relative to program with zero rejected
  frames. At 1.15/1.30 the notch alone does **not** guarantee loop stability
  (tails +38.135/+31.1 dB); saturation bounds output peaks to 0.240/0.481 with
  zero rejected and zero nonfinite frames. These are synthetic-loop findings,
  not a maximum-stable-gain claim.

## Adverse controls (all present in `report.json`)

- Config: missing frequency, unknown key, wrong type, out-of-range frequency
  and bandwidth, bandwidth above frequency, mismatched Q, zero Q, NaN/inf Q,
  NaN/inf frequency and NaN bandwidth all fail with explicit statuses.
- Coefficients: NaN frequency, zero bandwidth, NaN Q and zero Q raise instead
  of producing coefficients.
- Frames: NaN sample, inf sample, out-of-range sample, 159-sample and
  161-sample frames are rejected with state unchanged.
- Epoch/position: stale epoch returns `rejected_epoch`, noncontiguous source
  position returns `rejected_position`, then a valid frame succeeds.
- State isolation: two sessions with different explicit notches produce
  distinct states and outputs; reset affects only the target session.
- Lifecycle: double close, process after close and reset after close all return
  `closed`.
- Stability: 1,000 silence frames, 120 alternating impulses and 200 tail
  silence frames stay finite with zero rejections.

No result is omitted: `test_no_missing_result_and_incomplete_qualification`
fails if any required section or qualification gate is missing or `None`.

## Explicit non-claims, blockers and deferrals

- No real or recorded speech, music, corpus, download, model weights, licensed
  runtime, target-device run, CPU/memory measurement, deadline or availability
  result. No STOI/intelligibility score, human listening, room or playback path.
- No measured amplifier/loudspeaker/microphone loop, gain-before-feedback,
  maximum stable gain or real nonlinearity result. The synthetic loop is a
  control only; its nonlinear-interaction qualification is `incomplete`.
- No descriptor, registry entry, installed artifact, default provider, public
  API or ABI change. The C provider is opt-in and caller-registered only.
- Blocked until an authorized paired corpus and blinded protocol exist:
  real-speech impact and listening qualification.
- Blocked until a pinned measured acoustic loop exists: nonlinear interaction
  and maximum-stable-gain qualification.
- Blocked until an intended runtime is supplied: CPU, memory, latency and
  availability qualification.
- Blocked until provider intake, rights/license and catalog review: any default
  or installed provider claim.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behavior stays frozen.
