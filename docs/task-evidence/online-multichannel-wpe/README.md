# SDK-ONLINE-MULTICHANNEL-WPE — optional online multichannel WPE evidence

Task-local, synthetic, model-free dereverberation evidence exposed at an
optional protocol-shaped two-channel waveform adapter boundary. The reference is
**frame-causal**: each emitted 160-sample mono frame is computed from the
current two input frames and strictly earlier frames only. This is **synthetic
comparison evidence only**: the installed SDK, its ABI, descriptors, registry,
defaults, frozen v0 behavior and `main` are unchanged. No real room impulse,
recording, model weight, device timing, listening test, quality acceptance or
release claim is made. All assets, reports and build output remain private.

Pinned base: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`; branch
`swarm/SDK-ONLINE-MULTICHANNEL-WPE`. This branch was cut from that pinned base
and was not rebased or merged. Concurrent swarm PRs advanced the remote `main`
tip during preparation; this change adds only a new task-local documentation
directory and does not touch shared code or `main`.

## Scope and boundary

- Installed v0 stays 16 kHz mono `f32`, 160 samples/frame. This task adds a
  task-local opt-in boundary of **2 x 160 `f32` input samples in, 160 `f32`
  output samples out**. It is not an installed realtime v0 provider.
- One mono output frame is returned per two-channel input call. The first three
  output frames are causal priming silence: content delay is 480 samples
  (30 ms). Three final zero frames flush the overlap-add accumulator; no future
  input is read.
- The stacked predictor uses synchronized spectra from both channels, with
  delayed spectra from both channels predicting mic 0. It uses a 512-point FFT,
  160-sample hop, 8-frame (80 ms) prediction delay and 2 taps per channel
  (four stacked coefficients, 80–100 ms predictor history). Task-local settings
  are `forgetting=0.999`, `regularization=1e-6`, `prediction_energy_cap=0.1`
  and `max_abs_input=4.0`.
- `reference.py` is the causal two-channel WPE engine, deterministic fixture
  generator, controller/state machine and canonical report model. `scorer.py`
  is the dependency-free SI-SDR/STOI scorer. `run.py` is the opt-in adapter and
  report generator. `fixture.py` exposes frozen digests and the three-repeat
  check; `verify.py` performs read-only byte/schema/pin/scope validation;
  `test_reference.py` is the 48-test acceptance suite.
- `provider.json` and `adapter.json` document an **opt-in, unregistered,
  disabled-by-default** boundary. There is no C provider, CMake subtree,
  descriptor setting, registry entry, public catalog entry or installed default
  change. The optional C boundary was intentionally not added.
- Write scope is limited to this directory. No shared SDK file,
  `CMakeLists.txt`, `CONTRACTS.md`, public header, board file, handoff, ruleset
  or other worktree was touched.

## Exact source pins and room profile

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Row 65, offline/online/multichannel WPE dereverberation candidate provenance. |
| `adapters/wpe/README.md` | `b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e` | Algorithm parameters: 512 FFT, 128 hop, 5 taps, 8-frame delay; ~80 ms algorithmic latency; offline is not real time. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Line 60: three-channel online WPE had median RTF `0.044` on a measured SMARD screen and no material quality benefit over mono WPE on that direct-dominated set. Provenance only, not reproduced here. |
| `research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576576bcc99cb97a78120253b1f9e1e9618f964098468` | Stateful frame-causal multichannel WPE findings and room/target dependence. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `room` acceptance profile used for the evidence structure. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The mutable board snapshot read at task setup
(`audio-benchmark-platform/plan/swarm/TASKS.json`) had SHA-256
`5702c047fafade7e54b28199b13468ef8e7edb989539499381b51177bb669217`.
It is provenance only and never gates or qualifies this evidence. All 11
source/boundary/artifact pins are enumerated in `SOURCES.sha256`.

Room profile application is recorded in `report.json.room_profile`: frozen
geometry (0.04 m mic spacing, 30-degree source azimuth, 0/5-sample mic delays,
0.82 second-channel gain), RT60 stratification 250/550/900 ms with configured
D/R 12/6/0 dB, rate/channel/hop, seeded analytic excitation, additive noise
amplitude `0.008`, movement gain knots, 50 ms early-reflection target and reset
schedule. Mapped cases are echo-only, near-end-only, overlap and no-reference.
Alignment, echo-attenuation proxy, near-end damage, nonfinite failures, reset
behavior and missing/delayed channel controls are reported. The
delayed/missing-render case is not applicable to a dereverberation fixture with
no calibrated render/echo-return channel and remains an explicit open AEC-style
gate. No measured room, echo attenuation or device timing is claimed.

## Pinned scorer cross-check (inherited, not an online oracle)

The report never imports numpy, scipy or pystoi. The pure-Python scorer is
byte-identical to the merged offline-WPE scorer except its `SCORER_ID`, so the
previously recorded external-venv cross-check is inherited:

- `pystoi/stoi.py`: `482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`
- `pystoi/utils.py`: `0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321`
- prior scorer: `docs/task-evidence/offline-mono-wpe/scorer.py`
  `22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96`
- `crosscheck_vectors.json` (preserved byte-identically):
  `7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2`
- 6 synthetic paired vectors; max |STOI delta| `1.9984014443252818e-15`,
  max |SI-SDR delta| `1.9095836023552692e-14`.

Those vector names and digests refer to **offline fixture signals** and
validate the shared scorer only. They are not multichannel online candidate
results, an oracle, an acceptance threshold or a provider substitution. The
pinned merged offline-WPE report is likewise read only as a labeled noncausal
upper-bound control (`used_as_candidate_oracle: false`); whole-clip prediction
reads future frames, is mono and uses different geometry/hop/delay, so it cannot
qualify this causal two-channel implementation.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `SOURCES.sha256` | `981ca427d3177d8a08a395ecbfd33955daabafaec1ee12ba7c92441f46319dae` |
| `contract.json` | `2e6231b37bbbbc48ac6a4cbdf16798dccc634d10b59b7b53fdb69f8f6370cd7c` |
| `adapter.json` | `67e62ac88901dc7b0d4abe58307991b5f875ea148bd90d71ba4c2281d95b788b` |
| `provider.json` | `90f31b8f5e48ce6b03b460ff9bae53876befbe510b3baf7da02db33f022b2983` |
| `scorer.py` | `a0c1ba9ff21b0d0125c792053f0acefe1eda9266ab276aa370838c0f42dd55a1` |
| `reference.py` | `c4e0ea25dd9ce8d661af559fe86efb78dd34e6ab2d0f316dcb893fbee1836bfa` |
| `run.py` | `9392ff7d834709c62845e9b6a936b2a4194fef7f9bcc4b84cb49a514f417fbc3` |
| `fixture.py` | `c42fbb44339b7edc39385c82ac2817685b131600746144f903ef9f9fb7e707d2` |
| `verify.py` | `2ddd61f0cadcf73281aeda82202b643fbd9824d0db137499b9b22a6d38ccc2d5` |
| `test_reference.py` | `7a8833d6361c9f2bc97947ffd38ee68effdbc173ff674fdc4b377ecbd9a66b69` |
| `crosscheck_vectors.json` | `7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2` |
| `report.json` (file bytes) | `df76b6e78ab86bc21609d3a93d53bc175b9281962396cc3bf1acf8ea2d994e6f` |
| `report.json.sha256` (file bytes) | `527844b13d2475539f95fbb4517880e4aa2ccfa8232610ee087c8bac7b28735e` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. The canonical digest in
`report.json.sha256` is
`838840a0339e78752f31f99ea690d5621b763e500932a001db2f7929dcc15d76`; the
`fixture_digest` inside the report is
`b12c262ebee88151388300ff6d812be6adb76084ec75e2dda25d33d55aa78191`.
Regeneration is byte-identical and asserted by the acceptance suite.

## Synthetic evidence summary

All material is generated by seeded LCG noise and an analytic vowel-like
resonator source; no recordings or assets are read. RIRs are synthetic with
pinned RT60, early taps, low-passed exponential tail and configured
direct-to-diffuse ratio. The target keeps the direct response plus 50 ms of
early reflections. Every score is paired against that generated target, with
the reference and mic-0 identity control shifted by the measured 480-sample
content delay; unaligned scores are recorded separately and not used for
comparison.

| Condition | RT60 | D/R | Variant | SI-SDR (dB) | ΔSI-SDR | STOI | ΔSTOI | Echo proxy (dB) |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short_rt60 | 250 ms | 12 dB | identity | 18.299837 | 0.0 | 0.995469 | 0.0 | — |
| short_rt60 | 250 ms | 12 dB | online MC WPE | 10.939773 | -7.257785 | 0.970255 | -0.024969 | 1.127492 |
| medium_rt60 | 550 ms | 6 dB | identity | 10.475028 | 0.0 | 0.961778 | 0.0 | — |
| medium_rt60 | 550 ms | 6 dB | online MC WPE | 7.893493 | -2.480089 | 0.951914 | -0.009456 | 1.381605 |
| long_rt60 | 900 ms | 0 dB | identity | 3.136533 | 0.0 | 0.821103 | 0.0 | — |
| long_rt60 | 900 ms | 0 dB | online MC WPE | 2.028839 | -1.136101 | 0.821784 | +0.010395 | 2.338525 |

Noisy identity and online-MC-WPE-on-noisy controls are also scored for all three
rooms: ΔSI-SDR `-6.314241`, `-2.470932`, `-1.155031` dB and ΔSTOI `-0.026456`,
`-0.009095`, `+0.011209` respectively. Results are **mixed and reported as
measured**: SI-SDR regresses in every paired near-end condition, while STOI
improves only in the long-RT60 case. All required variants are explicitly
scored, finite and below clipping; no missing result qualifies the candidate.
No superiority, selection or real-room qualification follows.

Measured 50 ms early-to-late RIR energy ratios are `21.355985`, `12.209133`
and `4.545564` dB respectively. The configured D/R is direct/early taps versus
the whole diffuse tail, while the measured ratio also includes tail energy
inside the 50 ms target window; the report states this difference explicitly.
The echo-proxy values above are synthetic late-tail energy reductions, **not**
measured echo attenuation.

Clean-source preservation is explicit: identity is bit-exact (SI-SDR undefined
at perfect reconstruction and excluded); the causal WPE gives SI-SDR
`11.561154` dB and STOI `0.982843` against the aligned clean near-end, with
ΔSTOI `-0.017157`. Movement and overlapping-second-talker controls are scored
against the frozen early target: ΔSI-SDR `-1.136101` and `-1.154625` dB,
ΔSTOI `+0.010334` and `+0.009917`, respectively. Channel influence is proven
by changing only channel 1 while holding channel 0 fixed; a channel-1-only
impulse is non-injecting by construction and marked as such.

Alignment/state/duration: impulse peak at sample 480 (matching the 30 ms causal
content delay), silence peak `0.0`, equal input/output duration (25,600
samples), chunked == single-stream digest, independent sessions differ, reset
to epoch 3 over a 1,920-sample clip replays exactly, and a partial final frame
(677 samples) keeps its input length. A strict causality probe feeds identical
eight-frame stereo prefixes, changes only channel 1 in frame 9 and then feeds
16 more identical frames: all eight pre-divergence emitted frames are
byte-identical, and the first later output difference appears at probe index 8
after the predictor and overlap-add delays. Three fresh cold-start passes over
one pinned 960-sample stereo probe produce byte-identical little-endian f32
digests; no tolerance widening or provider substitution is used.

Adverse controls: nonfinite in either channel, missing channel, delayed channel,
wrong shape, out-of-range, stale session, stale epoch and stale position are
rejected with DSP state unchanged (invalid-count delta 9); finalize is
idempotent against reuse; missing key, unknown key, nonfinite, out-of-range,
wrong type, bad STFT geometry, bad prediction cap and wrong channel count are
rejected without controller creation; missing reference is `blocked` with
`metrics: null` and excluded from qualification. The opt-in adapter is tested
OFF (bit-exact mic-0 passthrough) and ON (causal WPE) through
`test_provider_off_is_identity_and_on_uses_causal_wpe`.

## Commands run (from this task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 - <<'PY'
# strict JSON: duplicate keys and nonfinite constants rejected for every *.json
PY
```

Result: **48 task-local tests passed**; report regeneration, `SOURCES.sha256`
regeneration and the inherited cross-check digest were each byte-identical over
three separate cold-start Python processes. `verify.py` passed with 11 pins,
4 strict JSON files, three-repeat, licensing and write-scope checks.

SDK baseline build, install and CTest were run **outside the worktree** in
`/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/mcwpe-sdk.eJYX6s`:

```sh
cmake -S <worktree> -B <temp-build> -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <temp-build> --parallel 4
cmake --install <temp-build> --prefix <temp-install>
ctest --test-dir <temp-build> --output-on-failure --timeout 60
```

Result: **11/11 SDK baseline tests passed** and install completed; no build
bytes were written inside the worktree and no SDK source file was changed.

Read-only board, whitespace and licensing checks:

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-ONLINE-MULTICHANNEL-WPE
git -C <worktree> diff --check
git -C <worktree> diff --cached --check
python3 -m venv <temp-venv>
<temp-venv>/bin/pip install 'reuse[charset-normalizer]==6.3.0'
<temp-venv>/bin/reuse lint
```

Result: `check.py` exit 0 with component `online-multichannel-wpe`,
`verification_profile: room` and `disposition: sdk-reference`; both whitespace
checks passed; REUSE 6.3.0 reported 0 bad/deprecated/missing licenses,
877/877 files with copyright and license information, and full REUSE 3.3
compliance.

## Adverse cases, skips and explicit non-claims

- No numpy/scipy/pystoi is required to run the fixture. The external venv used
  only for the recorded inherited cross-check is not a report dependency and
  no `pystoi==0.4.1` runtime is claimed.
- No real speech, corpus, WAV, RIR recording, model weight, download, licensed
  runtime, listening test, real-speech MOS/STOI, target-device pacing or
  CPU/deadline measurement is included.
- RT60 and D/R values are generated stratification parameters, not measured
  room properties. Synthetic STOI is not a human intelligibility score.
- No C provider or public boundary is added. The opt-in provider manifest is
  disabled, unregistered and has no descriptor settings or ABI/default effect.
- The mutable board digest is a snapshot only; board changes do not qualify or
  disqualify this evidence.
- Source statements about measured SMARD RTF, ~80 ms algorithmic latency and
  room-dependent WPE outcomes are provenance, not results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Held-out real-room or standards-room paired dereverberation SI-SDR/STOI with
   pinned two-channel RIR provenance, rights, a defined early-reflection target
   and identity/noisy controls.
2. Listening/MOS assessment on licensed real speech with a declared protocol.
3. Target-device causal/streaming CPU, memory, pacing, content-delay and
   deadline evidence on the exact 160-sample grid before any provider proposal;
   close the render/echo-return delayed/missing case for any AEC-style scope.
4. Exact-head independent review, hosted CI, provider intake, rights, license,
   descriptor and public catalog review, then explicit release approval.

Until those gates pass, this directory remains optional task-local synthetic
reference evidence with status `proposal_only_not_qualified` and decision
`DEFER` before processor exposure; installed v0 behavior stays frozen.
