# SDK-ADAPTIVE-ENERGY-VAD · deterministic analysis fixture

**Status: proposal-only / synthetic; qualification `incomplete`.** This is
task-local evidence for an optional adaptive-energy VAD reference. The installed
SDK, its public API/ABI, `CONTRACTS.md`, `CMakeLists.txt`, descriptors, registry
defaults and behavior are unchanged. No real speech, corpus, weights,
downloads, licensed runtime, target-device result or listening claim is made.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono, float32, 160-sample frames.
- `fixture.py`: deterministic generator, per-session reference detector,
  timestamped speech-probability and speech-event model, scorer, adverse
  controls and canonical report generator. It is model-free and uses only the
  Python standard library.
- `provider/`: optional, unregistered C reference on the public
  `audio_sdk/provider_v0.h` / `audio_sdk/session_v0.h` boundary. It passes audio
  through unchanged and keeps per-session adaptive state. The CMake option
  `AS_ENABLE_ADAPTIVE_ENERGY_VAD` is OFF by default; the source is not built,
  linked, installed or registered by the SDK. Analysis events are **not** v0
  ABI and remain in the proposal fixture.
- Write scope is limited to this directory.

The historical adapter declares `frame_samples: 320`; v0 is fixed at 160 and
was not changed. This fixture therefore does **not** claim numeric parity with
the historical 20 ms adapter or its reported AMI numbers.

## Source pins (SHA-256)

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate row 8: adaptive-energy FN 33.15%, FP 21.58%; desktop baseline only |
| `adapters/adaptive-energy-vad/adapter.json` | `b2b10b8fcfb7d54b30d4090111a251060ab4de534c59672d8c9b28528e3993f3` | Config values and 320-sample adapter divergence |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Local baseline status and chained-policy synthetic failure |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | v0 frame format, epochs, source intervals, validity and analysis model |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Analysis acceptance profile |
| `audio-sdk/api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Optional C provider table |
| `audio-sdk/api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Session lifecycle and source coordinates |

Pinned task base: `0673cb354cceb66f2f71faf9af7703b5a5d2fcfa`.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `README.md` | _this file; excluded from its own digest table_ |
| `contract.json` | `88ca75214a7dddf11396305e736088da6b06428adbca1ff8bc7cb6b245ae4746` |
| `fixture.py` | `c9f2bc1347f8f639f1ba061836558ebba0209bece9b540b9f28ae015cd0d9394` |
| `test_fixture.py` | `10cd61c54476f9659f2af04e5e9d120b0a3c688919090e03b877d8682ab79da0` |
| `report.json` | `88bd3aa18bf9b20bf7f57b80b8031aa0e8b9939fe1316ebf80ae829770b12da7` |
| `provider/CMakeLists.txt` | `e0891f9dcc3092ec2082d6ae330274a6b81f02998db550f9734160518d51150b` |
| `provider/adaptive_energy_vad_provider.c` | `17f502e5e572489139285bc059f5e01c20af2d32304d5e2e0d8c69bf89f7fd4b` |
| `provider/config/config.json` | `042226bb950c5e4798847b283e0857210a782c903ad6f334479e605d279e29b5` |
| `provider/config/descriptor.h.in` | `9c7030e7f26d08f968f3538b012c9e4e75aa450c5eb0df2f40de01460dbf5d36` |
| `provider/tests/test_provider.c` | `5947df2b27e08e54fbb1e1a8eae0a0cc317748522841051b01751270e27a84de` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`); the digest above is the file digest. The fixture spec digest
is `b9daee795b5200d261ceb1ac0d2cd2858d9c8c80594c1b791f61aaa2c31954b0` and the
detector config digest is
`4cdea896499cb1494d587a1c6dd9357ddc3aa640360c7a0bde4a4eba2c43437c`.

## Fixture summary (synthetic)

All signals are generated from a seeded LCG and analytic speech-like tones.
There are 330 frames / 52,800 samples: idle, quiet speech, noise-only, active
speech, a low-level negative noise burst, another quiet span, idle tail and an
explicit unknown tail. The first 300 frames (48,000 samples) are scored; the
final 30 frames (4,800 samples) are unknown validity and excluded.

- PCM f32 digest: `d29c7b9ab0a3f7c3782a83479f8538fcf37e26b35ad5f64e3e7fa8219fb3eb82`
- Probability stream digest: `080d725129f87626abc89fc090332185cd9ccc3ab0372c8b4a7db1f91bf2e400`
- Speech-event digest: `b93cfb44f6d05d9d351888a62f34d07bb2bd9fb9f8c9309e24e2491f045d2b80`
- Events: 300 known probability, 30 unknown probability, 3 speech events,
  333 admitted bus events, 0 dropped in the scored run.
- Detection counts: `TP=147, FN=3, FP=6, TN=144` (sum 300 scored frames);
  speech miss rate `0.02`, false alarm rate `0.04`.
- Stratified FN: quiet-a 1, active-a 1, quiet-b 1; FP: idle-b 2,
  noise-burst 2, idle-c 2.
- Onset delay 160 samples (one frame) and offset delay 320 samples
  (two frames) for each of the three speech spans.
- Strict separation: known zero probability is nonspeech; NaN, infinity,
  out-of-range probability and `validity: invalid` are rejected as invalid
  analysis and never counted as nonspeech; `validity: unknown` is retained but
  excluded from scoring.
- Adverse controls: missing/short/wrong-shape frames, nonfinite/out-of-range
  windows, stale epoch, pre-stream interval, stale availability, wrong clock,
  dropped/stale-event audit, overlapping sessions, adaptation-state leakage
  and reset, and exact cross-hop placement `[150,330) -> (0,10),(1,160),(2,10)`.
  Every control has an explicit result in `report.json`; no missing result
  qualifies a candidate.

## Reproduction

From the workspace root:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-ADAPTIVE-ENERGY-VAD
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ADAPTIVE-ENERGY-VAD diff --check
```

Expected: board checker exits 0; no diff whitespace errors.

From the fixture directory:

```sh
cd docs/task-evidence/adaptive-energy-vad
PYTHONDONTWRITEBYTECODE=1 python3 fixture.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_fixture.py
python3 -c "import json; [json.load(open(f)) for f in ('contract.json','report.json')]; print('json ok')"
```

Expected: `fixture.py` rewrites an identical `report.json` (digest above);
16 Python tests pass; JSON validation prints `json ok`.

Optional C boundary check (SDK installed outside the worktree):

```sh
TMPVAD=$(mktemp -d)
SDK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ADAPTIVE-ENERGY-VAD
PROVIDER=$SDK/docs/task-evidence/adaptive-energy-vad/provider
cmake -S "$SDK" -B "$TMPVAD/sdk-build" -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$TMPVAD/sdk-build" --parallel 2
cmake --install "$TMPVAD/sdk-build" --prefix "$TMPVAD/sdk-prefix"
cmake -S "$PROVIDER" -B "$TMPVAD/off" -DCMAKE_PREFIX_PATH="$TMPVAD/sdk-prefix" -DAS_ENABLE_ADAPTIVE_ENERGY_VAD=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMPVAD/off" --parallel 2 && ctest --test-dir "$TMPVAD/off" --output-on-failure
cmake -S "$PROVIDER" -B "$TMPVAD/on" -DCMAKE_PREFIX_PATH="$TMPVAD/sdk-prefix" -DAS_ENABLE_ADAPTIVE_ENERGY_VAD=ON -DCMAKE_BUILD_TYPE=Release
cmake --build "$TMPVAD/on" --parallel 2 && ctest --test-dir "$TMPVAD/on" --output-on-failure
```

Expected: OFF build leaves built-ins unchanged and the optional provider
unregistered (1/1 ctest); ON build registers a caller-local provider, verifies
exact audio passthrough/source intervals, rejects nonfinite input, passes
reset/short-final/drain/close (1/1 ctest). The C check is a boundary smoke
test, not parity with the full Python report.

## Blockers, deferrals and non-claims

Frozen as blocked until real assets/runtime and an agreed execution profile
exist:

1. **Frozen matched cohort — blocked.** No rights-cleared, label-complete
   held-out VAD corpus with per-frame speech labels and source pins is staged
   here. Historical AMI percentages are source-reported desktop baselines,
   not reproduced results.
2. **Intended execution profile — blocked.** No licensed/native runtime,
   target device, CPU/memory budget, availability clock or deadline budget is
   available. No RTF, latency, p95, power or production availability result is
   reported.
3. **Adapter identity — deferred.** The adapter's 320-sample frame cannot be
   reproduced without changing the frozen v0 frame size; this fixture is a
   v0-adapted reference, not adapter parity.
4. **Analysis ABI — deferred.** Typed analysis events are a proposal from the
   analysis foundation task, not installed v0 behavior. The optional provider
   passes audio through; it does not publish analysis through the v0 ABI.
5. **Release qualification — blocked.** No provider intake, rights/license
   review, descriptor registration, catalog entry, or release approval was
   performed. Nothing is enabled by default.

Historical context preserved without reuse as qualification: the candidate
matrix records adaptive-energy FN 33.15% / FP 21.58% on held-out AMI and a
separate frozen adaptive→Silero chain screen that produced 100% false
negatives on a noisy synthetic fixture. The local evidence chart also flags
the need for live state recovery; this fixture supplies deterministic controls
only.
