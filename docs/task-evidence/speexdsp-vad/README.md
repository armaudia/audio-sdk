# SDK-SPEEXDSP-VAD — optional SpeexDSP VAD reference evidence

**Status: proposal-only, synthetic/frozen evidence; qualification `incomplete`;
release decision `not_qualified`.**
This is a deterministic, task-local SpeexDSP VAD reference at the public
`adapters/speexdsp-vad` boundary. The optional C provider is unregistered and is
compiled only by a caller that explicitly opts in with
`AS_ENABLE_SPEEXDSP_VAD=ON`. The installed SDK, public API/ABI, descriptor
registry, defaults, shared `CMakeLists.txt`, installed v0 behavior and board
were **not** changed. Activity/VAD decisions here are **advisory only** and
never gate audio.

This is **not** an accuracy measurement, model qualification, native runtime
profile or real-speech result. Pinned base:
`941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce`; branch
`swarm/SDK-SPEEXDSP-VAD`.

## Scope and boundary

- Public boundary: `adapters/speexdsp-vad` (protocol-v1-shaped `inspect`/`run`),
  identity `speexdsp-vad-7a158783df74efe7c2d1c6ee8363c1e695c71226`, upstream
  revision `7a158783df74efe7c2d1c6ee8363c1e695c71226`.
- The public adapter declares **320-sample/20 ms** frames at 16 kHz. Frozen SDK
  v0 is fixed at **160-sample** frames and is unchanged. The divergence is
  recorded in `report.json`; **no numeric parity** with the historical adapter
  or its source-reported AMI figures is claimed.
- The Python reference models timestamped `speech_probability` and
  `speech_event` events on exact half-open source intervals, with validity,
  availability clock, per-session state, reset/replay and dropped-event audit.
  It is not native SpeexDSP code and not a posterior calibration.
- The optional C provider links the pinned vendored SpeexDSP sources, enables
  only `SPEEX_PREPROCESS_SET_VAD` (denoise/AGC/dereverb disabled), runs
  `speex_preprocess_run` + `SPEEX_PREPROCESS_GET_VAD`, passes PCM through
  unchanged and exposes the binary decision only through a **task-local**
  observation header — never through the v0 ABI. It is not in the default
  build, not registered by default and not installed.
- No adverse Tiny16 comparison was run: there is no S10/protocol clearance,
  approved independent reference adapter or permitted case manifest.

## Source pins (SHA-256)

All 12 paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests
verify every digest and fail closed on a missing or changed source; no
substitution, pooling or tolerance is used.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `research/plans/F02/vad_accuracy_contract.md` | `f6650aa3206cb694dffc4b429e0fe1f34c5ecd097cbfda7e522083cad7be1cec` |
| `adapters/speexdsp-vad/adapter.json` | `ded307574ef9531e4e9232fec82f55e013daf19c931f62dfda07e1e3b070fcc9` |
| `adapters/speexdsp-vad/run.py` | `c211f51e9952c52ea634e8c24ea421c17cabf40e32dbe91b6f56c2a4fedc21c1` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `audio-benchmark-platform/audio-sdk/third_party/speexdsp/UPSTREAM.md` | `3fc7e105de52b75abc65bae310de9066faabbdb7e13a17c3c9dd42f9f1f7bf1d` |
| `audio-benchmark-platform/audio-sdk/deps/speexdsp-files.sha256` | `3ff2b43a21b28a10a87f5a30b3c0339bef67a6b491c22f0f90c45696bd8f7a29` |
| `audio-benchmark-platform/audio-sdk/core/providers/speex/speex_provider.c` | `d1a98e3aff897375db4f0fc7668329be5254faa361ccaba1635a5089ea8a71e6` |

The historical candidate-matrix row (source-reported AMI FN 2.45%, FP 77.03%,
16.88 µs/20 ms frame) is **not** reproduced, confirmed or reused as a local
score. Local artifact digests are in `SOURCES.sha256`.

## Canonical report

`report.json` is canonical JSON (sorted keys, compact separators,
`allow_nan=False`, one trailing newline, 149,520 bytes). `run.py --report`
generates it three times, requires byte-identical payloads and canonical
digests, and only then writes the file and `report.json.sha256`. No tolerance,
retry or provider substitution is allowed.

| Name | SHA-256 |
| --- | --- |
| Report canonical digest / sidecar | `044b886eed6d639d12ffb0d89bb64192c0ec938fb54176c1d9aa7bd605360bcf` |
| `report.json` file digest | `23330682d0dd4b90bcade45b24651409672e9bef1b6ead304457bd21368fd057` |
| Fixture spec | `c9c8f194aaf0c39a4ed6239e322948e8cf60ac4c86c37848fd3a2051fbe17cad` |
| Local config | `c56930594d028448ca8c8d2f8921ee17064e17dad9ce4f57b644174eeb7c0728` |
| PCM f32 / audio view | `c5b5fca516025adbd401b1a4404501275eb9d089a0aa971fd32b3a322d52068d` |
| Probability stream | `53a9a560e94c3e7d95c654d2915d542a18f8f6c7e50c6e0976409982f218e7a2` |
| Speech events | `dab7f5c28986c4f2e791c4bb150e5cc164a4961f330d245391d83cad30307fd5` |
| Primary session events | `54609abe5a7b6e2c5c58df364c3578331dc45eb4cec0f6aac773e5e6de3c7aba` |

## Reproduction

Python 3.12.16, stdlib only. From the evidence directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python run.py --report
PYTHONDONTWRITEBYTECODE=1 python -m unittest -v test_reference.py
python -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
```

Expected: three repeats byte-identical; canonical digest
`044b886eed6d639d12ffb0d89bb64192c0ec938fb54176c1d9aa7bd605360bcf`;
21 tests pass; strict JSON parse succeeds.

From the worktree root (SDK baseline and optional provider boundary, scratch
build outside the worktree):

```sh
scratch="${TMPDIR:-/tmp}/speexdsp-vad-check-$$"
cmake -S . -B "$scratch/sdk" -DCMAKE_INSTALL_PREFIX="$scratch/prefix" -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk" --parallel 4
ctest --test-dir "$scratch/sdk" --output-on-failure          # 11/11
cmake --install "$scratch/sdk"

pr=docs/task-evidence/speexdsp-vad/provider
cmake -S "$pr" -B "$scratch/off" -DCMAKE_PREFIX_PATH="$scratch/prefix" -DAS_ENABLE_SPEEXDSP_VAD=OFF
cmake --build "$scratch/off" && ctest --test-dir "$scratch/off" --output-on-failure  # 1/1, unregistered

cmake -S "$pr" -B "$scratch/on" -DCMAKE_PREFIX_PATH="$scratch/prefix" \
  -DAS_ENABLE_SPEEXDSP_VAD=ON -DAS_SPEEXDSP_SOURCE_DIR="$PWD/third_party/speexdsp"
cmake --build "$scratch/on" && ctest --test-dir "$scratch/on" --output-on-failure  # 1/1, opt-in only

git diff --check
python /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py \
  --task SDK-SPEEXDSP-VAD
```

The optional test checks registration isolation, effective-config modes,
passthrough PCM, exact source coordinates, reset/epoch, final short frame,
drain, nonfinite rejection and advisory-decision observation. It prints
advisory SpeexDSP decisions explicitly with **no accuracy claim**.

## Analysis profile: exact results (synthetic only)

330 SDK frames / 52,800 samples: 300 known frames (48,000 samples), 30 unknown
tail frames (4,800 samples), 0 invalid. 300 known probability events, 30
unknown events, 1 speech run, 331 admitted bus events, 0 dropped events, 279
PCM16 clipping events in conversion (no PCM modification).

| Metric | Exact value |
| --- | --- |
| TP / FN / FP / TN (frames) | 61 / 89 / 30 / 120 |
| Speech miss rate | 0.593333333 (89/150) |
| False alarm rate | 0.2 (30/150) |

Stratified results: `quiet-a` FN 60, `active-a` TP 59/FN 1, `quiet-b` TP 2/FN
28, `noise-burst` FP 30, `idle-a/b/c` TN 60/30/30. `unknown-tail` is excluded
from all denominators.

Onset/offset boundaries: `quiet-a` and `quiet-b` runs are **missed**;
`active-a` has onset frame 151 (160 samples delay), offset frame 242 (5,120
samples delay), 91 detected frames versus 60 truth frames; the single speech
event covers samples `[24160, 38720)`.

Controls (all pass, all exact):

- Invalid vs nonspeech: NaN/out-of-range probabilities and `invalid` validity
  are rejected; `unknown` is admitted but excluded; invalid is never counted as
  nonspeech.
- Frame adverse: missing/nonfinite/infinite/short/long/wrong-shape frames and
  stale epoch/wrong interval are rejected with state unchanged; a final 80-sample
  frame is accepted with exact valid count and end coordinate.
- Event adverse: stale epoch, before-first-sample, stale availability and wrong
  clock are rejected; no admitted event changes.
- Independent state: two sessions produce distinct event digests; reset matches
  a fresh run; the other session is unchanged (epochs 2 and 7).
- Overlapping sessions: first bus accepts its own event, second rejects it with
  distinct audio digests. Cross-hop placement of `[150,330)` on 160-sample hops
  is exactly `[(0,10),(1,160),(2,10)]` with total overlap 180.
- Availability: `available_ns = end_sample * 62500 + 5,000,000` on
  `monotonic-reference-v0`, strictly monotonic; unknown events have no
  availability.

## Failure/limitation record

These are recorded as failures/incomplete, never as passes:

- No rights-cleared, label-complete held-out VAD cohort with per-frame labels is
  staged here; the Analysis profile is applied only to synthetic stimuli.
- No native VAD target-runtime execution profile, target device, CPU/memory
  budget, availability clock or deadline budget exists.
- The 320→160 frame and raw int16-label → threshold-model divergences are
  unresolved; no numeric parity is claimed.
- Typed analysis events are a proposal from SDK-FND-ANALYSIS, not installed v0
  behavior. Synthetic detections are advisory and do not gate audio.
- No adverse Tiny16 comparison was run (no S10/protocol clearance, approved
  independent reference adapter or permitted case manifest).

## Non-claims and remaining gates

No real speech, recordings, corpora, downloads, model weights, licensed
runtime, device result, listening, quality, intelligibility, pacing, power,
production availability or release qualification is claimed. No public SDK
code, ABI, default, board or other worktree was changed. All build bytes and
reports are task-local/private.

Remaining gates before any release or qualification claim: exact-head
independent review, hosted CI, target-runtime evidence, rights/analysis
qualification and release approval.
