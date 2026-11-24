# SDK-ONLINE-MONO-WPE-REFERENCE — optional online mono WPE reference

Task-local, synthetic, model-free dereverberation evidence exposed at an
optional protocol-shaped waveform adapter boundary. The reference is
**frame-causal**: each emitted 160-sample frame is computed from the current
input frame and strictly earlier frames only. This is **synthetic comparison
evidence only**: the installed SDK, its ABI, descriptors, registry, defaults,
frozen v0 behavior and main are unchanged. No real room impulse, device,
listening, quality, pacing or release claim is made. All assets, reports and
build output remain private.

Rebased base/head: `549dec7fd6e0d9a930a968c77b7415d3c6158710`; branch
`swarm/SDK-ONLINE-MONO-WPE-REFERENCE`. No merge was used.

## Scope and boundary

- Fixed v0 grid only: 16 kHz, mono `f32`, 160 samples/frame. The v0 format is
  the fixture format and the streaming call shape; no installed realtime v0
  provider is added.
- One output frame is returned per input call. The first three output frames
  are causal priming silence: content delay is 480 samples (30 ms). Three
  final zero frames flush the overlap-add accumulator; no future input is read.
- Analysis uses a 512-point FFT, 160-sample hop, 8-frame (80 ms) prediction
  delay, 3 taps and 80–110 ms predictor history. These are task-local
  parameters, not SDK settings.
- `reference.py` is the causal WPE engine, frozen synthetic fixture generator,
  controller/state machine and canonical report model. `scorer.py` is the
  dependency-free SI-SDR/STOI scorer. `run.py` is the opt-in adapter and report
  generator. `fixture.py` exposes read-only frozen digests and the three-repeat
  check; `verify.py` performs read-only byte/schema/pin/scope validation;
  `test_reference.py` is the acceptance suite.
- `provider.json` and `adapter.json` document an **opt-in, unregistered,
  disabled-by-default** boundary. There is no C provider, CMake subtree,
  descriptor setting, registry entry, public catalog entry or installed default
  change.
- Write scope is limited to this directory. No shared SDK file,
  `CMakeLists.txt`, `CONTRACTS.md`, public header, board file or other worktree
  was touched.

## Exact source pins and room profile

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Row 65, online/offline WPE dereverberation candidate provenance. |
| `adapters/wpe/README.md` | `b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e` | Algorithm parameters: 512 FFT, 128 hop, 5 taps, 8-frame delay; ~80 ms algorithmic latency; offline is not real time. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Line 59: stateful frame-causal WPE, median RTF 0.260 on measured SMARD RIRs, estimated 80 ms delay, negligible gains over identity and mixed synthetic tradeoffs. Provenance only, not reproduced here. |
| `research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` | Early-reflection target convention and room-dependent WPE findings. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `room` acceptance profile used for the evidence structure. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The immutable board snapshot read at task setup
(`audio-benchmark-platform/plan/swarm/TASKS.json`) had SHA-256
`4f33f1bde5978db569e5079eb77c3ed6c72ea6ce726396419010445064f0e030`.
The board is mutable provenance and never gates or qualifies this evidence.
All 11 source/boundary/artifact pins are also enumerated in `SOURCES.sha256`.

Room profile application is recorded in `report.json.room_profile`: frozen RIR
and rate/channel/hop, excitation, movement gain schedule, additive noise and
reset schedule; mapped echo-only, near-end-only, overlap and no-reference
cases; reported alignment, nonfinite/shape failures and reset controls. The
delayed/missing-render case is not applicable to a mono dereverberation fixture
with no separate render/echo-return channel and remains an open gate for any
AEC-style qualification. No measured room, echo attenuation or device timing is
claimed.

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
validate the shared scorer only. They are not online candidate results, an
online oracle, an acceptance threshold or a provider substitution. The pinned
merged offline-WPE report is likewise read only as an explicitly noncausal
upper-bound control (`used_as_candidate_oracle: false`); whole-clip prediction
uses future frames and cannot qualify a causal implementation.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `SOURCES.sha256` | `e61468ee3906f8f1840a1b6031bc8442aec27d507ee9fc841b5403fdcfba1025` |
| `contract.json` | `7f4535840b9613d52c8d2b54422c6ac5db4dc0a5b241385dd936c74bf64a71b6` |
| `adapter.json` | `e667e0fb00982bd9f107c35d9649c17aaefcb460a8a56227f6c87fc476fc86ba` |
| `provider.json` | `5cb6c92f3f4a2c5ca9a99c1b9b56626342bd51cacc2fd12c2879328ac90b1fed` |
| `scorer.py` | `626781163b043e09f67a35aaaf3eb4239735e345efd63812f67be2332919c06a` |
| `reference.py` | `7c77bc33409dd2c5519dc6b607927095c013d9a9a819fed1030d05ed28fe6b3e` |
| `run.py` | `ec9642412f6e81432f98dbb5a3fe1855338eada6e4735246cb54a8422c51ba0d` |
| `fixture.py` | `95ac14de12feb83d6cf6cc3b9755b4725b9eb8c22c26303305f6374991f71778` |
| `verify.py` | `1295b31ef2ae7eeb819cfef3cc48fadaa730287fba2f30b1a6aeed94387c34d2` |
| `test_reference.py` | `61bebece1b565ac99c18f1582cbf89b13a245b2f6b11de4fe0a1d324a838b039` |
| `crosscheck_vectors.json` | `7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2` |
| `report.json` (file bytes) | `77d5268a5b4e5c798fcbae5ef0d23dcf6008ed3534523d15fb21806fbb36fdd4` |
| `report.json.sha256` (file bytes) | `efd6cd4a7ecbdd371ce1e6b2051fd6abd98a353f705ed58e78b7d9789fbf79ba` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. The canonical digest in
`report.json.sha256` is
`fe369226db457fc42a22a809e297d6e55f3e83e78c42f6a89318d37423081130`; the
`fixture_digest` inside the report is
`40fbd2e3d9fe8e6472defeb07d087467f3f02152aabc7b88973cd04d9bf96bf3`.
Regeneration is byte-identical and asserted by the acceptance suite.

## Synthetic evidence summary

All material is generated by seeded LCG noise and an analytic vowel-like
resonator source; no recordings or assets are read. RIRs are synthetic with
pinned RT60, early taps, low-passed exponential tail and configured
direct-to-diffuse ratio. The target keeps the direct response plus 50 ms of
early reflections. Every score is paired against that generated target, with
the identity/mixture reference shifted by the measured 480-sample content
delay; unaligned scores are recorded separately and not used for comparison.

| Condition | RT60 | D/R | Variant | SI-SDR (dB) | ΔSI-SDR | STOI | ΔSTOI | Peak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short_rt60 | 250 ms | 12 dB | identity | 17.180000 | 0.0 | 0.993442 | 0.0 | 0.270314 |
| short_rt60 | 250 ms | 12 dB | online WPE | 9.247946 | -7.895549 | 0.968823 | -0.024383 | 0.243150 |
| medium_rt60 | 550 ms | 6 dB | identity | 5.695038 | 0.0 | 0.925421 | 0.0 | 0.265067 |
| medium_rt60 | 550 ms | 6 dB | online WPE | 5.369194 | -0.275546 | 0.906599 | -0.014213 | 0.226017 |
| long_rt60 | 900 ms | 0 dB | identity | 0.317238 | 0.0 | 0.802410 | 0.0 | 0.394965 |
| long_rt60 | 900 ms | 0 dB | online WPE | 0.367169 | +0.105803 | 0.798267 | -0.009731 | 0.338682 |

Noisy identity and online-WPE-on-noisy controls are also scored for all three
rooms: ΔSI-SDR `-7.129243`, `-0.386890`, `+0.061516` dB and ΔSTOI `-0.024283`,
`-0.013784`, `-0.009012` respectively. The result is **mixed and reported as
measured**: SI-SDR improves only in the long-RT60 room while STOI regresses in
every room, and the short-RT60 SI-SDR regression is severe. All 12 variants are
finite, below clipping and explicitly scored; no missing result qualifies the
candidate. No superiority, selection or real-room qualification follows.

Measured 50 ms early-to-late RIR energy ratios are `20.465145`, `11.506049`
and `4.749543` dB respectively. The configured D/R is direct/early taps versus
the whole diffuse tail, while the measured ratio also includes tail energy
inside the 50 ms target window; the report states this difference explicitly.

Clean-source preservation is explicit: identity is bit-exact (STOI `1.0`,
SI-SDR undefined at perfect reconstruction and excluded); the causal WPE gives
SI-SDR `11.071693` dB and STOI `0.977112` against the aligned clean source.
Spectral tilt, movement and overlapping-second-talker controls are present in
the report, each with paired scores against the frozen target.

Alignment/state/duration: impulse peak at sample 480 (matching the 30 ms
causal content delay), silence peak `0.0`, equal input/output duration
(25,600 samples), chunked == single-stream digest, independent sessions differ,
reset to epoch 3 over a 1,920-sample clip replays exactly, and a partial final
frame (5,157 samples) keeps its input length. A strict causality probe feeds
identical eight-frame prefixes and a divergent ninth frame: all eight emitted
frames are byte-identical while the later output differs. Three cold-start
passes over one pinned 960-sample probe produce byte-identical f32 digests; no
tolerance widening or provider substitution is used.

Adverse controls: nonfinite, stale session, wrong shape, out-of-range, stale
epoch and stale position are rejected with DSP state unchanged (invalid-count
delta 6); finalize is idempotent against reuse; missing key, unknown key,
nonfinite, out-of-range, wrong type, bad STFT geometry and bad prediction cap
are rejected without controller creation; missing reference is `blocked` with
`metrics: null` and excluded from qualification. The opt-in adapter is tested
OFF (bit-exact identity) and ON (causal WPE) through
`test_provider_off_is_identity_and_on_uses_causal_wpe`.

## Commands run (from this task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool adapter.json >/dev/null
python3 -m json.tool provider.json >/dev/null
python3 -m json.tool crosscheck_vectors.json >/dev/null
```

Result: 29 task-local tests passed; report regeneration byte-identical;
`verify.py` passed with strict JSON, 11 pins, three-repeat, licensing and scope
checks.

SDK baseline build and CTest were run **outside the worktree** in
`/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/online-mono-wpe-ctest`:

```sh
cmake -S <worktree> -B <temp-build> -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <temp-build> --parallel 4
ctest --test-dir <temp-build> --output-on-failure --timeout 60
```

Result: 11/11 SDK baseline tests passed; no build bytes were written inside
the worktree and no SDK source file was changed.

Read-only board check and whitespace check (from the platform/worktree roots):

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-ONLINE-MONO-WPE-REFERENCE
git -C <worktree> diff --check
```

Result: passed; component `online-mono-wpe-reference` is `verification_profile:
room`, `disposition: sdk-reference`, `evidence_status: evaluated`.

## Adverse cases, skips and explicit non-claims

- No numpy/scipy/pystoi is required to run the fixture. The external venv used
  only for the recorded inherited cross-check is not a report dependency and
  no `pystoi==0.4.1` runtime is claimed.
- No real speech, corpus, WAV, RIR recording, model weights, download, licensed
  runtime, listening test, real-speech MOS/STOI, target-device pacing or
  CPU/deadline measurement is included.
- RT60 and D/R values are generated stratification parameters, not measured
  room properties. Synthetic STOI is not a human intelligibility score.
- No C provider is added. The opt-in provider manifest is disabled,
  unregistered and has no descriptor settings or ABI/default effect.
- The mutable board digest is a snapshot only; board changes do not qualify or
  disqualify this evidence.
- Source statements about measured SMARD RTF, ~80 ms algorithmic latency and
  room-dependent WPE outcomes are provenance, not results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Held-out real-room or standards-room paired dereverberation SI-SDR/STOI with
   pinned RIR provenance, rights, a defined early-reflection target and
   identity/noisy controls.
2. Listening/MOS assessment on licensed real speech with a declared protocol.
3. Target-device causal/streaming CPU, memory, pacing, content-delay and
   deadline evidence on the exact 160-sample grid before any provider
   proposal; complete the room profile's delayed/missing-render case for any
   AEC-style scope.
4. Exact-head independent review, hosted CI, provider intake, rights, license,
   descriptor and public catalog review, then explicit release approval.

Until those gates pass, this directory remains optional task-local synthetic
reference evidence and installed v0 behavior stays frozen.
