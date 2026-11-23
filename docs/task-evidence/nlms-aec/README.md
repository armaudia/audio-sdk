# SDK-NLMS-AEC — optional NLMS acoustic echo cancellation reference

Task-local, deterministic, synthetic/model-free evidence for a sample-domain
NLMS echo canceller with an **explicit playback/render reference**, exercised on
the public v0 adapter/provider boundary. This is **reference evidence only**:
the installed SDK, ABI, descriptors, registry, defaults, frozen v0 behavior,
shared CMake files and main are unchanged. No measured room acoustics, real
recording, model weight, download, licensed runtime, listening, MOS/STOI on real
speech, target-device timing or release qualification is claimed.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame.
- Python reference: `reference.py` (NLMS controller, synthetic fixtures,
  metrics, report), `run.py` (task-local protocol-v1-shaped paired adapter and
  byte-identical report regeneration), `crosscheck.py` (C/Python vector header).
- C reference: `provider/` (optional, unregistered provider source, task-local
  sidechain helper and opt-in CMake consumer test). It includes only the public
  `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h` from the SDK; it is not
  built, registered or linked by default.
- The v0 frame carries one mono stream, so the render reference is supplied to
  the optional provider through the **task-local** `nlms_aec_feed_reference`
  helper on the provider instance. This is not an SDK API/ABI change. With no
  reference fed, the provider passes the microphone through and never adapts.
- Write scope is limited to this directory. Descriptor `settings` remain `{}`.
- Room acceptance profile is interpreted here as **DSP-adjacent synthetic
  evidence**; no room impulse response or device measurement is used.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | NLMS is a lightweight baseline sensitive to delay, path length, double talk and nonlinearity; the instantaneous hold heuristic reduced ERLE sharply, and recorded pilots found nonfinite RLS and severe double-talk damage in a fixed hybrid. Motivates explicit delay-change, double-talk and safety controls. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | NLMS adaptive filter: local recorded screen, median RTF about 0.072, double-talk preservation still a concern. No RTF or recorded score is reproduced here. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Room profile: freeze render/reference, excitation, delay, movement, noise and reset; include echo-only, near-only, overlap and no-reference; report attenuation, near damage, nonfinite failures and delayed/missing render. |
| `src/audioml_eval/aec.py` | `84544219098d2c012da38163d49196379eb4f12094fb09cf106e57295ed69351` | Prior NLMS reference algorithm shape (causal FIR state, step size, reset, ERLE/near-SNR definitions), pinning provenance only. This implementation is independent and task-local. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The mutable board snapshot `audio-benchmark-platform/plan/swarm/TASKS.json` had
SHA-256 `3154212165862651640b2388b4ce8dd62b5a71ad808152820f9b3831488beb89`
when read. It is provenance only and never qualifies this evidence.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `contract.json` | `cb12c67ce7d857cb77e33aa8eefb1bd2522b398cb0eae407f0cc9e44116e0e4b` |
| `adapter.json` | `39965fdb22f60a49342a3165e0377494ef221a7aaff448b78e266b93e304e7e4` |
| `reference.py` | `12efcf612cb15404bd3cb32c2d215d0424bcfce76cee73078ca5d26c9760b492` |
| `run.py` | `964597d6625fca333ed0a6501cc2d54b2d98472e8d13e0bc700f1af420239723` |
| `test_reference.py` | `6449cc8c1441455b4d153732e7c4609f94158aece05faea1675a3674b861bd29` |
| `crosscheck.py` | `cc48289332f4e37134959d4580cb1eba8151bbc1386877081416d08f120bc3a0` |
| `report.json` (file bytes) | `2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a` |
| `report.json.sha256` (file bytes) | `e79da05478b06e922ef1926cf0ee47c5d228d049f4cec0b9de89420d8cef0336` |
| `provider/CMakeLists.txt` | `29b4d6bc576e0a591374f03fdb1bd7b33dcb7a0c3f2d91210fbb6e14f6d1bf06` |
| `provider/nlms_aec_provider.c` | `823660950ede7ddbf39d3bc994b6f4d90872199842e603344c37d6f36610b196` |
| `provider/nlms_aec_provider.h` | `cc6c5302778d7dfdf31ed2c3185fd671a1d2fc704057a54bb293fa79d2895889` |
| `provider/crosscheck_vectors.h` | `14671c4e24e3d9c94c620d46970db2a488102868ee5239701b83b5bb8205eceb` |
| `provider/config/config.json` | `48a81e2b8263472787352d31422f5dad0f3e2208dce826e17494a8ed4c9c3489` |
| `provider/config/descriptor.h.in` | `f6b4cab7724b32e82a77ddd2a9a42322d3af0de8885ea81c17bc110388f798a2` |
| `provider/tests/test_provider.c` | `6bead3635001819b3289c82db2918e47f9d993bc8f50d99b7f50030e55597864` |

`SOURCES.sha256` pins every file in this directory except itself. `README.md`
and `SOURCES.sha256` are not repeated inside `contract.json` to avoid a
self-referential digest cycle. `report.json` is canonical JSON (`sort_keys=True`,
compact separators, `allow_nan=False`) plus one trailing newline:

- canonical report digest: `dbc4290b56cceca27689af97de6d79235f7c91a3616065a362f16de3712f728c`
- fixture specification digest: `ca153b8613054965b294e02e539936dfc254269071ec55d210f1d853e1e563a3`
- regeneration from `python3 run.py --report` is byte-identical and asserted by
  `test_reference.py`.

## Synthetic fixture

All signals are generated from seeded LCG noise and analytic sources; no files,
corpora or assets are read. 16 kHz mono, 160-sample frames, 51,200 samples
(3.2 s). The explicit playback stream drives a sparse 96-tap synthetic linear
echo path (primary tap at 32 samples). Segments: silence to 0.40 s, far-end-only
to 1.40 s, double talk to 2.20 s, abrupt path delay change (+16 samples),
far-end-only reconvergence to 2.60 s, then double talk. The render reference is
explicitly delayed by 32 samples in the delayed-render condition and zeroed for
1,200 samples in the dropout condition. Capture noise is deterministic at
0.0015 full scale. Reset schedule, excitation, path, noise and all metric
windows are pinned in `report.json:fixture_spec`.

Measured render-reference latency (cross-correlation over the echo-only
interval): **32 samples**, equal to the intended primary tap; alignment error
0 samples. The delayed-render run measures 0 samples against its shifted
reference, i.e. 32 samples of misalignment. Algorithmic and buffering delay are
both 0; this is fixture alignment, not device or scheduling latency.

## Evidence summary (all synthetic)

Adaptive candidate metrics from `report.json:runs` (ERLE and echo-return loss
are measured on far-end-only intervals; near SNR counts residual echo as error):

| Condition | Status | Qualifies | Early ERLE (dB) | Late ERLE / ERL (dB) | Double-talk near SNR (dB) | GBF proxy (dB) | Peak |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| single_talk | ok | yes | 23.816 | 35.170 | n/a | 31.069 | 0.064 |
| double_talk | ok | yes | 23.816 | 35.170 | 10.548 | 15.091 | 0.444 |
| delay_change | ok | yes | 23.816 | 35.170 | 10.548 | -5.275 | 0.556 |
| near_only | ok | yes | 0.000 | 0.000 | 44.496 | -2.212 | 0.380 |
| delayed_render | misaligned_reference | no | 27.628 | 37.949 | 9.642 | -8.770 | 0.442 |
| reference_dropout | partial_reference | no | 23.816 | 35.170 | 7.849 | 15.091 | 0.539 |
| missing_reference | blocked_no_reference | no | n/a | n/a | n/a | n/a | n/a |

Delay change: pre-change ERLE 35.170 dB, early post-change 12.505 dB, late
post-change 15.629 dB (reconvergence +3.124 dB); the negative final GBF proxy
after the path change is reported as an observed limitation, not hidden. The
double-talk hold fired on 136/320 frames in `double_talk` and 138/320 in
`delay_change`.

Fixed-attenuation and identity controls are reported **separately** in
`report.json:controls` and never qualify the adaptive candidate:

| Control / condition | ERLE (dB) | Double-talk near SNR (dB) | GBF proxy (dB) |
| --- | ---: | ---: | ---: |
| fixed −6.02 dB / single_talk | 6.021 | n/a | -2.212 |
| fixed −6.02 dB / double_talk | 6.021 | 4.434 | -2.212 |
| identity / single_talk | 0.000 | n/a | -2.212 |
| identity / double_talk | 0.000 | 3.540 | -2.212 |

The adaptive candidate improves far-end ERLE and double-talk near-end SNR over
both controls on this fixture. GBF is a synthetic L1 residual-path loop-margin
proxy (`-20 log10(sum|h - ŵ|)`), **not** a measured loudspeaker feedback margin.

DSP and safety controls: impulse peak at sample 1632 (1600 + primary tap 32,
zero added algorithmic delay), step first non-zero at 1632, silence peak 0,
clean-speech-like near-only near SNR 44.390 dB with a silent render. All
qualifying runs are finite with peak below clipping; no missing result
qualifies a candidate.

## Commands run (from the task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 crosscheck.py
python3 -m json.tool contract.json >/dev/null
```

Result: **27 Python tests passed**; report regeneration byte-identical; JSON
valid; `crosscheck.py` regenerates the header byte-identically.

Optional C boundary check (SDK installed to a temporary prefix; both builds
outside the worktree):

```sh
cmake -S <worktree> -B <tmp>/sdk-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <tmp>/sdk-build --parallel 4
ctest --test-dir <tmp>/sdk-build --output-on-failure
cmake --install <tmp>/sdk-build --prefix <tmp>/sdk-prefix
cmake -S provider -B <tmp>/provider-off \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_NLMS_AEC=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-off --parallel 2 && ctest --test-dir <tmp>/provider-off --output-on-failure
cmake -S provider -B <tmp>/provider-on \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_NLMS_AEC=ON -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-on --parallel 2 && ctest --test-dir <tmp>/provider-on --output-on-failure
```

Result: 11/11 SDK baseline tests passed; OFF build unlinked/unregistered, 1/1
ctest passed; ON build registered one caller-local provider and passed 1/1
ctest with four-frame Python/C output parity (max error < 2e-5), weight-L1
parity, explicit-reference adaptation, no-reference passthrough with unchanged
weights, invalid sidechain/frame rejection, epoch-ordered reset, session
lifecycle and final partial frame. Built-in provider queries were unchanged in
both builds.

Read-only board check and whitespace check (from the workspace root and
worktree root respectively):

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-NLMS-AEC
git diff --check
```

## Adverse cases, skips and explicit non-claims

- Rejected controls: invalid config values, nonfinite/out-of-range/short
  microphone or reference frames, stale epoch and stale position; all leave
  DSP state unchanged. No-reference runs are passthrough with `metrics: null`.
- Delayed, dropped and misaligned reference runs are scored but explicitly
  excluded from qualification; a missing result never qualifies a candidate.
- No numpy/scipy, corpus, WAV, model weights, download, licensed runtime,
  AECMOS model, listening test, real-speech MOS/STOI, target-device pacing,
  measured room response or loop-gain measurement is included.
- The C provider is intentionally not installed, registered by default or added
  to any catalog. The mutable board digest is a snapshot only.
- Source findings (0.072 RTF, recorded pilot damage/nonfinite results) are
  provenance, not results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Paired recorded far-end/microphone evidence with known render latency,
   pinned real RIRs/path measurements and held-out licensed speech.
2. Double-talk, path-change and nonlinear-loudspeaker evaluation with
   AECMOS/ASR/listening preservation and attenuation gates.
3. Measured loudspeaker-loop gain-before-feedback and stability with device
   buffers, clock drift, and target-device CPU/memory/deadline timing.
4. Provider intake, rights/license, descriptor and public catalog review.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behavior stays frozen.
