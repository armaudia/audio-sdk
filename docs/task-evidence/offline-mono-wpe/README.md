# SDK-OFFLINE-MONO-WPE — optional offline mono WPE reference

Task-local, synthetic, model-free dereverberation evidence exposed at an
optional offline waveform adapter boundary. This is **synthetic comparison
evidence only**: the installed SDK, its ABI, descriptors, registry, defaults,
frozen v0 behavior and main are unchanged. No real room, real speech, weights,
downloads, licensed runtime, listening, MOS/STOI on real speech, target-device
timing, CPU/deadline result or release qualification is claimed.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame. The v0 grid is
  used solely as the fixture format and to exercise deterministic chunking of
  an offline buffer.
- **Whole-clip WPE is noncausal**: it estimates one predictor per frequency bin
  from the complete utterance. It cannot be represented by the causal
  160-sample v0 `process()` boundary and is explicitly outside installed realtime
  v0. No v0 provider, registration, descriptor or default was added.
- Python reference: `scorer.py` (dependency-free SI-SDR/STOI), `reference.py`
  (pinned offline WPE, synthetic RIR fixtures, paired controls, state machine
  and report), `run.py` (task-local protocol-v1-shaped adapter plus canonical
  report regeneration).
- Write scope is limited to this directory. No shared SDK file, `CMakeLists.txt`,
  `CONTRACTS.md`, public header, board file or worktree outside this task was
  touched.
- The adapter is unregistered and developer-only. It produces no Bench bundle
  and no SDK provider.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Row 65, offline WPE dereverberation candidate provenance. |
| `adapters/wpe/README.md` | `b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e` | Algorithm parameters: 512 FFT, 128 hop, 5 taps, 8-frame delay; ~80 ms algorithmic latency; offline is not real time. |
| `research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` | Early-reflection target convention and finding that offline WPE regressed on measured direct-dominated rooms. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | `room` acceptance profile used for evidence structure. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The mutable board snapshot `audio-benchmark-platform/plan/swarm/TASKS.json`
had SHA-256 `4f33f1bde5978db569e5079eb77c3ed6c72ea6ce726396419010445064f0e030`
when read. It is provenance only and never gates or qualifies this evidence.

The source evidence reports offline WPE regressing against an early-reflection
target on direct-dominated rooms. This fixture mirrors that shape: WPE improves
the long-RT60/reverberant condition but regresses on the short-RT60/direct
condition. The result is reported as measured, not hidden, and is **not** a
selection, superiority or real-room qualification.

## Pinned scorer cross-check

The report never imports numpy, scipy or pystoi. The pure-Python scorer was
cross-checked in a pre-existing, read-only external venv against pinned
`pystoi 0.4.1` sources and the benchmark zero-mean SI-SDR formula:

- `pystoi/stoi.py`: `482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`
- `pystoi/utils.py`: `0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321`
- scorer algorithm inherited byte-identically from
  `docs/task-evidence/classical-wiener-denoising/scorer.py` (`1c3e9c97f75b838d1677cb5823d679520d9a40557853e8fb6fec0ca560cf2698`),
  with only the `SCORER_ID` constant changed.
- 6 synthetic paired vectors: max |STOI delta| `1.9984014443252818e-15`,
  max |SI-SDR delta| `1.9095836023552692e-14`.
- This is synthetic-scoped scorer validation, not audio-bench scorer parity,
  extended STOI, real-speech MOS/STOI or human listening.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `contract.json` | `d6a60b4eb560fb64fbdfa8df092053c0e7dd195dafac71cd4b98792af1e289e0` |
| `adapter.json` | `12ed0299faac5369ee63e2680d408db413b98c68d4d820f24ec10bed53f393d7` |
| `scorer.py` | `22c2ba7e60dc4f6e0a58b5ad5a5b89bf643e620ec37736082e3a64bffd034d96` |
| `reference.py` | `3a54465d8a20f81507ce1d5c2d47401274dee550aa0570bcd0257c6285f7778c` |
| `run.py` | `e97a0c19c3917bc45d6f6ef47af2f8ec078f57d10d40c4152e16d108bfee71d8` |
| `test_reference.py` | `bd659c2734a2de87578aa0777630b24790e92d4853154c0424b1191e2010571d` |
| `crosscheck_vectors.json` | `7bdd131858306648b4f24b1544a6afb4da2660b3f2d3edcdfb3b715e574a18a2` |
| `report.json` (file bytes) | `2b9be2488c4b0f82f417abd3e131c840729856937ed8239f2645beeaa30d7e61` |
| `report.json.sha256` (file bytes) | `1b7a5e1af8efd625003c386c8fadb79b171c2d0f0e05d830f6cbbf9bbd2a4d88` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. The canonical digest recorded in
`report.json.sha256` is
`990bece0c10a8917f41e2670d5be66e5c35442a664cd0a5ca2797bb993b02255`;
`fixture_digest` inside the report is
`fb2aeb11e2afd5eb1634f506a680867d0b5ca43624718b9e78b73b0e44e647dd`.
Regeneration is byte-identical and is asserted by the tests.

## Synthetic evidence summary

All material is generated by seeded LCG noise and an analytic vowel-like
resonator source; no recordings or assets are read. RIRs are synthetic with
pinned RT60, early-tap delays, low-passed exponential tail and
direct-to-diffuse ratio. The target keeps the direct response plus 50 ms of
early reflections. Every score is paired against that generated target.

| Condition | RT60 | D/R | Variant | SI-SDR (dB) | ΔSI-SDR | STOI | ΔSTOI | Peak |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| short_rt60 | 250 ms | 12 dB | identity control | 17.179000 | 0.0 | 0.993442 | 0.0 | 0.270314 |
| short_rt60 | 250 ms | 12 dB | noisy identity | 16.062101 | 0.0 | 0.991286 | 0.0 | 0.270983 |
| short_rt60 | 250 ms | 12 dB | WPE candidate | 7.016147 | -10.162854 | 0.975013 | -0.018429 | 0.238997 |
| short_rt60 | 250 ms | 12 dB | WPE on noisy | 6.843230 | -9.218870 | 0.972999 | -0.018287 | 0.238294 |
| medium_rt60 | 550 ms | 6 dB | identity control | 5.695038 | 0.0 | 0.925421 | 0.0 | 0.265067 |
| medium_rt60 | 550 ms | 6 dB | noisy identity | 5.608494 | 0.0 | 0.924311 | 0.0 | 0.261932 |
| medium_rt60 | 550 ms | 6 dB | WPE candidate | 5.646481 | -0.048558 | 0.928571 | +0.003150 | 0.224314 |
| medium_rt60 | 550 ms | 6 dB | WPE on noisy | 5.541868 | -0.066626 | 0.926869 | +0.002558 | 0.222977 |
| long_rt60 | 900 ms | 0 dB | identity control | 0.317238 | 0.0 | 0.802410 | 0.0 | 0.394965 |
| long_rt60 | 900 ms | 0 dB | noisy identity | 0.300492 | 0.0 | 0.801823 | 0.0 | 0.394266 |
| long_rt60 | 900 ms | 0 dB | WPE candidate | 2.060709 | +1.743472 | 0.819066 | +0.016656 | 0.273158 |
| long_rt60 | 900 ms | 0 dB | WPE on noisy | 2.031862 | +1.731370 | 0.818956 | +0.017133 | 0.272050 |

All 12 variants are finite, below clipping, and explicitly scored; no missing
result qualifies the candidate. Measured 50 ms early-to-late RIR energy ratios
are `20.465145`, `11.506049` and `4.749543` dB respectively, giving real
stratification across the three conditions. The configured D/R is
direct/early taps versus the whole diffuse tail, while the measured ratio also
includes tail energy inside the 50 ms target window; the report states this
difference explicitly.

Spectral tilt (mid-over-low and high-over-low dB) is present for the early
target, identity control and WPE candidate in every condition, with per-band
deltas against the target. Clean-source preservation is explicit: identity is
bit-exact (STOI `1.0`, SI-SDR undefined at perfect reconstruction and excluded);
WPE on clean source scores SI-SDR `7.893382` dB, STOI `0.979685`, peak
`0.169472`.

Alignment/state/duration: impulse peak at sample 0 (zero added delay), silence
peak `0.0`, equal input/output duration (25,600 samples), chunked == single
buffer digest (20 chunks of 1,280 samples), independent sessions differ, reset
to epoch 3 replays exactly, partial final frame (5,157 samples) keeps its input
length.

Adverse controls: nonfinite, stale session, wrong shape, out-of-range, stale
epoch and stale position are rejected with DSP state unchanged (invalid-count
delta 6); finalize is idempotent against reuse; missing key, unknown key,
nonfinite, out-of-range, wrong type and bad STFT geometry settings are rejected
without controller creation; missing reference is `blocked` with `metrics: null`
and excluded from qualification.

## Commands run (from the task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 -m json.tool contract.json >/dev/null
python3 -m json.tool adapter.json >/dev/null
```

Result: 27 tests, all passed; report regeneration byte-identical; JSON valid.

Read-only board check and whitespace check (from the platform repo):

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-OFFLINE-MONO-WPE
git diff --check
```

Result: passed; component `offline-mono-wpe` is `verification_profile: room`,
`disposition: sdk-reference`, `evidence_status: evaluated`.

## Adverse cases, skips and explicit non-claims

- No numpy/scipy/pystoi is required to run the fixture. The external venv used
  only for the recorded cross-check is not a report dependency and no
  `pystoi==0.4.1` runtime is claimed.
- No real speech, corpus, WAV, RIR recording, model weights, download, licensed
  runtime, listening test, real-speech MOS/STOI, target-device pacing or
  CPU/deadline measurement is included.
- RT60 and D/R values are generated stratification parameters, not measured
  room properties.
- No C provider is added. Whole-clip WPE is outside the causal v0 boundary and
  no realtime provider, descriptor setting or registry entry is proposed.
- The mutable board digest is a snapshot only; board changes do not qualify or
  disqualify this evidence.
- The source findings about measured rooms and ~80 ms algorithmic latency are
  provenance, not results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Held-out real-room or standards-room paired dereverberation SI-SDR/STOI with
   pinned RIR provenance, rights and a defined early-reflection target.
2. Listening/MOS assessment on licensed real speech with a declared protocol.
3. A causal/streaming WPE variant designed and measured on the target device
   before any realtime v0 provider proposal.
4. Provider intake, rights, license, descriptor and public catalog review.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behavior stays frozen.
