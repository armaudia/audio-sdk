# SDK-CLASSICAL-WIENER-DENOISING — optional classical Wiener denoising reference

Task-local, synthetic, model-free enhancement evidence on the public v0
adapter/provider boundary. This is **reference evidence only**: the installed
SDK, its ABI, descriptors, registry, defaults, frozen v0 behavior and main are
unchanged. No real speech, weights, downloads, licensed runtime, listening,
MOS, target-device pacing, CPU/deadline result or release qualification is
claimed.

## Scope and boundary

- Fixed v0 format only: 16 kHz, mono `f32`, 160 samples/frame.
- Python reference: `scorer.py` (dependency-free SI-SDR/STOI), `reference.py`
  (causal framewise Wiener, task-matched spectral-subtraction baseline,
  identity control, synthetic fixtures and report), `run.py` (task-local
  protocol-v1-shaped adapter plus deterministic report regeneration).
- C reference: `provider/` (optional, unregistered provider source plus an
  opt-in CMake consumer test). It uses only `audio_sdk/provider_v0.h` and
  `audio_sdk/session_v0.h`; it is not built, registered or linked by default.
- Write scope is limited to this directory. No shared SDK file was modified.
- Descriptor `settings` remain `{}`; no public API, ABI, descriptor registry or
  default provider was changed.

## Source pins and what they establish

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless noted.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Row 24, `Classical spectral subtraction and Wiener`: “30-pair DNS screen; offline whole-clip noise estimates”. |
| `adapters/classical-spectral/adapter.json` | `451f3f083f738743660e55d54f907155728dc89b63cd10778ed43d8f985710b4` | Integration-scope evidence only; no performance or qualification inferred. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Line 43, `Wiener filtering`: DNS pilot mean ΔSI-SDR `+0.43 dB`, batch RTF `0.0489`, and a noncausal whole-clip noise estimate. |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Linked pilot report; pinned as provenance only. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `api/include/audio_sdk/provider_v0.h` (boundary) | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public provider table, unchanged. |
| `api/include/audio_sdk/session_v0.h` (boundary) | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public session facade, unchanged. |

The mutable board snapshot `audio-benchmark-platform/plan/swarm/TASKS.json`
had SHA-256 `277393a97b19c1b338e9db6aacef6d48e3e797944cdc57fb5606f19c691ee3a5`
when read. It is provenance only and never gates or qualifies this evidence.

The source evidence reports a DNS pilot with an offline whole-clip noise
estimate. This fixture deliberately uses a **causal 10-frame noise-only prefix**
and does not reproduce the DNS number or the RTF. The task-matched
spectral-subtraction baseline outperforms the Wiener candidate on these two
synthetic conditions; that result is reported as measured rather than hidden.

## Pinned scorer cross-check

The report never imports numpy, scipy or pystoi. The pure-Python scorer was
cross-checked in an external scratch venv against pinned
`pystoi-0.4.1-py2.py3-none-any.whl` and the benchmark zero-mean SI-SDR formula:

- pystoi wheel: `e277b671663d26d35a2416c9c8010a74084e6c3970354506398051a554896939`
- `pystoi/stoi.py`: `482b30bfa8e60f1453200315afcd5564fc9e9aa1d14aeb9710a58fd7a9f52658`
- `pystoi/utils.py`: `0222df0354a248ccc7f8525eda9bda9da815e5d60106f611a5f4750d1ba7f321`
- 4 synthetic paired vectors: max |STOI delta| `1.1102230246251565e-15`,
  max |SI-SDR delta| `8.43769498715119e-14`.
- This is synthetic-scoped scorer validation, not audio-bench scorer parity,
  extended STOI, real-speech MOS/STOI or human listening.

## Local artifacts (SHA-256)

| Path | SHA-256 |
| --- | --- |
| `contract.json` | `f1d3031fbed42c18cda8317cffb779c43478a401fc80517181c1baf72de303c1` |
| `adapter.json` | `b4b294f452033d6b38c63d39c30d612ae167a00628aae8920d1e26a4deb31337` |
| `scorer.py` | `1c3e9c97f75b838d1677cb5823d679520d9a40557853e8fb6fec0ca560cf2698` |
| `reference.py` | `b60d208e0567980a300cc68cb5be53e114c19506cf7d9de7a11a9c9dc8e97d92` |
| `run.py` | `28ed1beff61270a81052495ae54aa7f42738de35472fb21ba0dfdf3d5f42f3bd` |
| `test_reference.py` | `a838fac4ee5f5342bd8842b9d5fb80ae6ce694cf77418103ad1f1287de28a075` |
| `crosscheck_vectors.json` | `bb79854862b2cb8eb0d5be341e3e7c68bc369a8bae96113c06cd16e11b21c80a` |
| `report.json` (file bytes) | `b395b08417212cdf07988c359dde424e9ee011d5d961adfda0d668b8251be8b0` |
| `report.json.sha256` (file bytes) | `5e1b45c9c5570ac7a0c742544036a2134197151e621bcd53065c8c25be3e56ca` |
| `provider/wiener_provider.c` | `f6a6c3b62addacef7c6fb78e35f3272b8354866f32ad0c9d5ac9561b5e95cb1a` |
| `provider/CMakeLists.txt` | `68d6b915d5c838bb325ab0b3f3155fc30a77f4f997a1b57bfe56c1ce6d10008f` |
| `provider/config/config.json` | `e253c5c5fece9b17a210d775fc8073c59c97514a753c3ae6e18c7f1e3e6671a4` |
| `provider/config/descriptor.h.in` | `de9aa8807a7c5985aa89a2071c063aa9097f15a229533da392fb5c1a3064e0e2` |
| `provider/tests/test_provider.c` | `1e5c658fb3a5ba830ce16651a27b48ad618c7cdd98067517ce181c32358b9861` |

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`) plus one trailing newline. The canonical digest recorded in
`report.json.sha256` is
`6fc8ea1eecab44c6c03ea9c461210587c39bd9a1274b07b4eb06ab124b4feb98`;
`fixture_digest` inside the report is
`21d36e25782c7d3f2293e80049bd98fd3cb5ad59f0d165f25c4a289067f8b1fd`.
Regeneration is byte-identical and is asserted by the tests.

## Synthetic evidence summary

All material is generated by seeded LCG noise and analytic resonator speech;
no recordings or assets are read. Every score is paired against the generated
clean reference.

| Condition | Variant | SI-SDR (dB) | ΔSI-SDR | STOI | ΔSTOI | Peak |
| --- | --- | --- | --- | --- | --- | --- |
| mild | noisy identity | 3.484944 | 0.0 | 0.796250 | 0.0 | 0.225365 |
| mild | spectral subtraction | 4.449801 | +0.964857 | 0.829388 | +0.033138 | 0.207324 |
| mild | Wiener candidate | 4.083588 | +0.598644 | 0.817387 | +0.021137 | 0.216134 |
| hard | noisy identity | -3.928764 | 0.0 | 0.435288 | 0.0 | 0.267639 |
| hard | spectral subtraction | -3.134511 | +0.794253 | 0.484426 | +0.049138 | 0.242841 |
| hard | Wiener candidate | -3.463559 | +0.465205 | 0.465351 | +0.030063 | 0.255939 |

Fixture digests: clean `c66162388cca0b42a903d0550e3a14bbbc61fa80bc1dee25536d693b3d5a6abd`;
mild noisy `19fcf35032854471e0563dc5a485e747c9ab30a275c13830b2eaecf64be4c740`;
hard noisy `e6f997fcd7956eb112163a80151c1640395b0a5563f27834fe61d7cb9a231bd7`.
The identity control is bit-exact to the noisy input. All three variants in
both conditions are finite, below clipping, and explicitly scored; no missing
result qualifies the candidate.

Clean preservation: identity is bit-exact (STOI `1.0`, SI-SDR undefined by
definition at perfect reconstruction and explicitly excluded); spectral
subtraction and Wiener score STOI `1.0` with peaks `0.196552`.

Alignment/state/duration: impulse peak at sample 0 (zero added delay), silence
peak `0.0`, equal input/output duration (33,600 samples), framewise == stream
digest, independent sessions differ, reset to epoch 3 replays exactly, partial
final frame keeps its input length.

Adverse controls: nonfinite, wrong shape, out-of-range, stale epoch and stale
position are rejected with DSP state unchanged (invalid-count delta 5);
`None`, missing key, unknown key, nonfinite, out-of-range and wrong-type
settings are rejected without controller creation; missing reference is
`blocked` with `metrics: null` and excluded from qualification.

## Commands run (from the task directory unless noted)

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 -m json.tool contract.json >/dev/null
```

Result: 22 tests, all passed; report regeneration byte-identical; JSON valid.

Optional C boundary check (SDK installed to a temporary prefix; both builds
outside the worktree):

```sh
cmake -S <worktree> -B <tmp>/sdk-build -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build <tmp>/sdk-build --parallel 4
cmake --install <tmp>/sdk-build --prefix <tmp>/sdk-prefix
ctest --test-dir <tmp>/sdk-build --output-on-failure
cmake -S provider -B <tmp>/provider-off \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_WIENER=OFF -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-off --parallel 2 && ctest --test-dir <tmp>/provider-off --output-on-failure
cmake -S provider -B <tmp>/provider-on \
  -DCMAKE_PREFIX_PATH=<tmp>/sdk-prefix -DAS_ENABLE_WIENER=ON -DCMAKE_BUILD_TYPE=Release
cmake --build <tmp>/provider-on --parallel 2 && ctest --test-dir <tmp>/provider-on --output-on-failure
```

Result: 11/11 SDK baseline tests passed; OFF build unlinked/unregistered, 1/1
ctest passed; ON build registered one caller-local provider, preserved noise
calibration passthrough, attenuated the noise-only-initialized signal
(late RMS ratio `0.916444`), rejected nonfinite/shape/epoch/position/reset
controls, honored a 37-sample final frame, and passed reset/drain/close, 1/1
ctest passed. Built-in provider queries were unchanged in both builds.

Read-only board check and whitespace check (from the worktree root):

```sh
python3 <audio-benchmark-platform>/plan/swarm/check.py --task SDK-CLASSICAL-WIENER-DENOISING
git diff --check
```

Result: passed; component `classical-wiener-denoising` is
`verification_profile: enhancement`, `disposition: sdk-reference`,
`evidence_status: evaluated`. `git diff --check` passed on the staged tree.

## Adverse cases, skips and explicit non-claims

- No numpy/scipy/pystoi is required to run the fixture. The external venv used
  only for the recorded cross-check is not a report dependency and no
  `pystoi==0.4.1` runtime is claimed.
- No real speech, corpus, WAV, model weights, download, licensed runtime,
  listening test, real-speech MOS/STOI, target-device pacing or CPU/deadline
  measurement is included.
- The C provider is intentionally not installed, registered by default or
  added to any catalog. `settings` stay empty because the public configuration
  validator only accepts nonempty settings for built-ins.
- The mutable board digest is a snapshot only; board changes do not qualify or
  disqualify this evidence.
- The DNS `+0.43 dB` and batch RTF `0.0489` figures are source findings, not
  results reproduced here.

## Reopen / release gates

Reopen before any default, production or qualification claim:

1. Held-out real-speech paired SI-SDR/STOI with pinned corpora, rights and
   listening/MOS assessment.
2. Causal noise PSD tracking without a noise-only prefix, including
   nonstationary and adverse noise conditions.
3. Target-device CPU, memory, deadline and real-time pacing measurement.
4. Provider intake, rights, license, descriptor and public catalog review.

Until those gates pass, this directory remains optional task-local reference
evidence and the installed v0 behavior stays frozen.
