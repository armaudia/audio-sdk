<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FIXED-RLS-TO-NLMS-AEC — optional fixed RLS→NLMS acoustic echo cancellation reference

Task-local, deterministic, synthetic-only evidence for a causal RLS warmup that
hands its weights and far-end history to NLMS at a fixed frame-aligned boundary.
It exercises an **explicit playback/render sidechain** at the public v0
adapter/provider boundary. This is **proposal-only, incomplete and not
qualified**: the installed SDK, ABI, descriptors, registry, defaults, frozen v0
behavior, shared CMake files, board and main are unchanged. No measured room
acoustics, real recording, licensed corpus, AECMOS model, listening test,
loudspeaker loop measurement, device timing or release approval is claimed.

Branch scope: `swarm/SDK-FIXED-RLS-TO-NLMS-AEC`, rebased onto the refreshed SDK
main `941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce` (parent of the single local
commit). All changes are new files under `docs/task-evidence/fixed-rls-to-nlms-aec/`.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame.
- Python reference: `reference.py` (controller, frozen synthetic fixtures,
  metrics, report), `run.py` (task-local protocol-v1-shaped paired adapter and
  byte-identical report regeneration), `crosscheck.py` (C/Python vectors),
  `test_reference.py` (deterministic unittest suite), `check_licensing.py`.
- C reference: `provider/` (optional, unregistered provider source, task-local
  sidechain helper and opt-in CMake consumer test). It includes only the public
  `audio_sdk/provider_v0.h` and `audio_sdk/session_v0.h`; it is not built,
  registered or linked by default.
- The v0 frame carries one mono stream, so render is supplied through the
  **task-local** `fixed_rls_nlms_feed_reference` helper on the provider
  instance. This is not an SDK API/ABI change. With no reference fed, the
  provider passes the microphone through and never adapts.
- CMake option `AS_ENABLE_FIXED_RLS_NLMS_AEC` defaults to `OFF`. Descriptor
  `settings` remain `{}`; no catalog or default is modified.
- Room acceptance profile is interpreted as **DSP-adjacent synthetic evidence**;
  no measured room impulse response or device measurement is used.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` | RLS converges quickly but is numerically fragile with weak/silent reference; NLMS is lighter but delay/path-change/double-talk sensitive. Motivates the fixed handoff and guard. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Hybrid/RLS recorded-pilot history and no production readiness. No RTF or recorded score is reproduced here. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Room profile: freeze render/reference, excitation, delay, movement, noise, reset; include echo-only, near-only, overlap and no-reference; report attenuation, near damage, nonfinite failures and delayed/missing render. |
| `audio-benchmark-platform/plan/swarm/check.py` | `5488bf52cea2965b0b36a7ec6bbba45c1b3be7b2f514051ac56f994d3101d539` | Read-only board check used for this task. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate matrix provenance for hybrid AEC status. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-expanded/REPORT.md` | `d07d4cc5781396451ce7261cd9b3ed2c35d02cc211af4d55daac65c9f5f528bf` | Prior expanded hybrid AEC findings. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-expanded/results.json` | `9baca7ead9cd37b54fe95147362d7661acaca5000cf9b8a70d03ff258e21c86a` | Machine-readable prior expanded results. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-followup/REPORT.md` | `acf72565e69538a1a6e32cb4a40fac80d8ae7e3bfce63806312984b5804e5d26` | Prior follow-up findings. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-followup/results.json` | `79d7c3c47a5e6fd28e2646ed224ca76e2879948b2995c2e78d9d7ff714440ba2` | Machine-readable prior follow-up results. |
| `research/voice-enhancement-20261101/agent-hybrid-aec-real/REPORT.md` | `4577d59347d9f48a693228ccbf40a9de77494294e7d0df111c98e8591c3e438e` | Historical full RLS nonfinite on 12/12 near-end-only recordings; mechanism reproduced analytically here. |
| `src/audioml_eval/aec.py` | `84544219098d2c012da38163d49196379eb4f12094fb09cf106e57295ed69351` | Prior metric/algorithm provenance only; this implementation is independent and task-local. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The mutable board snapshot `audio-benchmark-platform/plan/swarm/TASKS.json` had
SHA-256 `47ba70216c23a07b3829696d5536ba830ec742bcccaa8070bbdedbe03c3419ed`
when read. It is provenance only and never qualifies this evidence.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `contract.json` | `3ff52a7bb3004bc24761b76ed420c72cab95a2f9201b64d520ce078a3e3a2192` |
| `adapter.json` | `52314de137351634c3bd96c4eace703eb4721bc209ce0e5b04bc63cfb875bbf8` |
| `check_licensing.py` | `a82ae223c30fecde4d504c3222a9511e4a78066a5f312780c8ce770e2c7f4d30` |
| `crosscheck.py` | `d9ffb14625185e393de1ae249acc0d190fd583832fdef8f5942bef3b5fdb62cb` |
| `reference.py` | `20ca866e6f2839719320aa01e39bbee1f7ffd9a2ec2fa3912e44874f712faaf9` |
| `run.py` | `3183a97e1d11dd0e0db8ea2c0b0251064b13509052bedb4d38514e9bf4cde174` |
| `test_reference.py` | `18a3983c441f6e817b881d043d230dc0d7d8219c53b86ca140469276807c9cb9` |
| `report.json` (file bytes) | `94cc863242f8b7b0320ae670cd24722ce197e6c588bfe8bb498bfa8ae0684fce` |
| `report.json.sha256` (file bytes) | `23252c3060c17c0a4d74b7918d209026abbcafb81c5c48eb624400659c24ef56` |
| `provider/CMakeLists.txt` | `85a1ecb78665c5dedcf5f9869b33a9c25b82d04c6968bd77d69433a78a6256d4` |
| `provider/crosscheck_vectors.h` | `6fa68adf9ec355cd2a37629bfd5bd7b89eb13970232728b2dd56ff22805e0617` |
| `provider/fixed_rls_nlms_provider.c` | `2d6ce909bda8e3de813df2bd5122350e4806d0f23b0241d1e647c1f2b0183f06` |
| `provider/fixed_rls_nlms_provider.h` | `795b8aaeee9b9b24a315d8003fbb78175d5f626721e598be6e750bedf10b2e38` |
| `provider/config/config.json` | `87662ce0d1250d70784d89f3c18fc2f30ba1db774bbdcfb0b3d491e025355e60` |
| `provider/config/descriptor.h.in` | `bd0fd6f4f08c0d46cd605693b5e8a857839ec6d176f89028168f90c347c0542f` |
| `provider/tests/test_provider.c` | `61569134c9983527465d4fffc24ba16ba3f145e1c46501a880d26f587d8ec819` |

`SOURCES.sha256` pins every file in this directory except itself. `README.md`
and `SOURCES.sha256` are not repeated inside `contract.json` to avoid a
self-referential digest cycle. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`) plus one trailing
newline:

- canonical report digest: `df0a622f0fb2f496d88ddae7c114837f4262b5b2227a2fb8b8ed7c37324c46ff`
- fixture specification digest: `bf01e40b6c2b18668edae534116e39055b2f90d1c6af4ad0020d5c5ea510dd91`
- regeneration from `python3 run.py --report` is byte-identical and asserted by
  `test_reference.py`.

## Frozen synthetic fixture

All signals are generated from seeded LCG noise and analytic sources; no files,
corpora or assets are read. 16 kHz mono, 160-sample frames, 51,200 samples
(3.2 s). The explicit playback stream drives two frozen sparse linear echo
paths (primary taps at 8 and 16 samples). Segments: silence to 0.40 s,
far-end-only to 1.40 s, double talk to 2.20 s, abrupt path change at 2.20 s,
far-end-only reconvergence to 2.60 s, then double talk. The render reference is
delayed by 16 samples in the delayed-render condition and withheld for the
1,200-sample dropout condition; one fixture has no reference at all. Capture
noise is deterministic at 0.0015 full scale. Reset schedule, excitation, paths,
noise and all metric windows are pinned in `report.json:fixture_spec`.

Measured render-reference latency (cross-correlation over the echo-only
interval): **8 samples**, equal to the intended primary tap; alignment error 0
samples. The delayed-render condition measures 16 samples of misalignment.
Algorithmic and buffering delay are both 0; this is fixture alignment, not
device or scheduling latency.

## Evidence summary (all synthetic)

Adaptive candidate metrics from `report.json:runs` (ERLE/echo-return loss is
measured only on far-end-only intervals; near SNR counts residual echo as error
and is measured only under double talk):

| Condition | Status | Qualifies | Early ERLE (dB) | Late ERLE (dB) | Double-talk near SNR (dB) | GBF proxy (dB) | Peak |
| --- | --- | --- | ---: | ---: | ---: | ---: | ---: |
| single_talk | ok_synthetic | no | 40.389 | 40.301 | n/a | 39.279 | 0.083 |
| double_talk | ok_synthetic | no | 40.389 | 40.301 | 43.832 | 35.908 | 0.379 |
| delay_change | ok_synthetic | no | 40.389 | 40.301 | 43.832 | 8.389 | 0.379 |
| near_only | ok_synthetic | no | 0.000 | 0.000 | 44.496 | -2.212 | 0.380 |
| delayed_render | misaligned_reference | no | 0.000 | 0.000 | 3.385 | -2.212 | 0.545 |
| reference_dropout | partial_reference | no | 40.389 | 40.301 | 10.031 | 35.908 | 0.485 |
| missing_reference | blocked_no_reference | no | n/a | n/a | n/a | n/a | n/a |

Delay change: pre-change ERLE 40.301 dB, early post-change 17.633 dB, late
post-change 24.970 dB (reconvergence +7.337 dB). The double-talk hold fired on
191/320 frames in `double_talk` and 190/320 in `delay_change`. Delayed render,
reference dropout and missing reference are explicitly non-qualifying.

Controls are reported separately in `report.json:controls` and never qualify
the adaptive candidate:

| Control / condition | ERLE (dB) | Double-talk near SNR (dB) | GBF proxy (dB) |
| --- | ---: | ---: | ---: |
| fixed −6.02 dB / single_talk | 6.021 | n/a | -2.212 |
| fixed −6.02 dB / double_talk | 6.021 | 4.360 | -2.212 |
| identity / single_talk | 0.000 | n/a | -2.212 |
| identity / double_talk | 0.000 | 3.385 | -2.212 |
| rls_only_frozen / single_talk | 40.562 | n/a | 29.200 |
| rls_only_frozen / double_talk | 40.562 | 44.061 | 29.200 |
| nlms_only / single_talk | 40.274 | n/a | 39.279 |
| nlms_only / double_talk | 40.274 | 43.821 | 35.923 |

Honest regressions in `report.json:regressions`: hybrid early ERLE is 0.173 dB
below `rls_only_frozen`; hybrid double-talk near SNR is 0.230 dB below
`rls_only_frozen`; `rls_only_frozen` late post-change ERLE is 25.657 dB below
hybrid (frozen weights cannot reconverge); hybrid late post-change ERLE is only
0.001 dB above `nlms_only` on this fixture. GBF is a synthetic L1
residual-path loop-margin proxy (`-20 log10(sum|h - ŵ|)`), **not** a measured
loudspeaker feedback margin.

## Handoff, finite behavior and safety

- Handoff is fixed at sample 4000 (0.25 s, frame 25) for all four adaptive
  runs, frame-aligned, with reason `scheduled`. Weights/history are copied and
  the RLS covariance is drained.
- The historical zero-reference RLS covariance windup is reproduced
  analytically: first nonfinite sample 140683 of a separate frozen 160,000-sample
  extension with `lambda=0.995`, `P0=100`; iterative steps match the closed form
  to relative error < 1e-12.
- The candidate's 160,000-sample near-only zero-reference extension remains
  finite with bounded weights, scheduled handoff at 4000 and zero safety
  handoffs. A forced nonfinite-state safety check restores finite bounded state
  and hands off to NLMS; output and weights remain finite.
- Impulse peak at sample 1608 (1600 + primary tap 8, zero added algorithmic
  delay), step first non-zero at 1608, silence peak 0, clean-speech-like
  near-only near SNR 44.390 dB with a silent render.

## Commands run (from the task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 crosscheck.py
python3 check_licensing.py
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool adapter.json >/dev/null
python3 -m json.tool report.json >/dev/null
```

Result: **34 Python tests passed**; report/crosscheck/source regeneration is
byte-identical; JSON valid; local SPDX/REUSE/licensing check passed.

Optional C boundary check (SDK installed to a temporary prefix; all builds
outside the worktree):

```sh
cmake -S <worktree> -B <tmp>/sdk-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <tmp>/sdk-build --parallel 4
ctest --test-dir <tmp>/sdk-build --output-on-failure
cmake --install <tmp>/sdk-build --prefix <tmp>/sdk-prefix
cmake -S provider -B <tmp>/provider-off \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_FIXED_RLS_NLMS_AEC=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-off --parallel 2 && ctest --test-dir <tmp>/provider-off --output-on-failure
cmake -S provider -B <tmp>/provider-on \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_FIXED_RLS_NLMS_AEC=ON -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-on --parallel 2 && ctest --test-dir <tmp>/provider-on --output-on-failure
```

Result: **11/11 SDK baseline ctest passed**; OFF build unlinked/unregistered,
1/1 ctest passed; ON build registered one caller-local provider and passed 1/1
ctest with 26-frame Python/C output parity across the handoff boundary (max
error < 2e-5), weight-L1/phase/handoff parity, explicit-reference adaptation,
no-reference passthrough with unchanged weights, invalid sidechain/frame
rejection, epoch-ordered reset, session lifecycle and final partial frame.
Built-in provider queries were unchanged in both builds.

Read-only board and whitespace/licensing checks:

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-FIXED-RLS-TO-NLMS-AEC
git diff --check
```

## Adverse cases, skips and explicit non-claims

- Rejected controls: invalid config values, nonfinite/out-of-range/short
  microphone or reference frames, stale epoch and stale position; all leave DSP
  state unchanged. No-reference runs are passthrough with `metrics: null`.
- Delayed, dropped, misaligned and missing reference runs are scored or blocked
  and explicitly excluded from qualification; a missing result never qualifies
  a candidate.
- No numpy/scipy, corpus, WAV, model weights, download, licensed runtime,
  AECMOS model, listening test, real-speech MOS/STOI, target-device pacing,
  measured room response or loop-gain measurement is included.
- The generated-header script splits the identifier token as
  `"SPDX" "-License-Identifier: Apache-2.0"`; no literal full token is embedded
  in the generator string. The C header itself carries the normal SPDX comment.
- The C provider is intentionally not installed, registered by default or added
  to any catalog. The mutable board digest is a snapshot only.
- Source findings (recorded nonfinite RLS, hybrid pilot damage) are provenance,
  not results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Paired licensed render/capture recordings with known loop timing and
   held-out speech rights.
2. Measured loudspeaker-loop gain-before-feedback and device timing with
   buffers, clock drift and target-device CPU/memory/deadline measurement.
3. Double-talk, path-change and nonlinear-loudspeaker evaluation with
   AECMOS/ASR/listening preservation and attenuation gates.
4. Provider/license/catalog intake before any default, installed or
   production claim.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behavior stays frozen.
