<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FFMPEG-AFFTDN — task-local synthetic frequency-domain NS evidence

**Status: `proposal_only_not_qualified`; qualification `incomplete`; decision
`DEFER` before any processor exposure.**
This package is a deterministic, fully synthetic frequency-domain
noise-suppression reference at a task-local, protocol-v1-shaped enhancement
boundary. It is **not** FFmpeg `afftdn`, not an FFmpeg binary/source wrapper,
not a GPL component, not a licensed runtime, not an SDK provider, not a
registered descriptor and not a release or quality qualification. No public
API/ABI, `CONTRACTS.md`, shared `CMakeLists.txt`, descriptor registry, default,
installed v0 behavior, board, handoff, ruleset, main branch or other worktree
was changed. Installed v0 remains 16 kHz mono `float32`, 160 samples.

Pinned base: `2bc2a13aa4c5b398933fd9097d09746ce151216e`. Branch:
`swarm/SDK-FFMPEG-AFFTDN`. All files live only under
`docs/task-evidence/ffmpeg-afftdn/`.

## Exact scope and boundary

- Boundary anchor: public adapter `adapters/ffmpeg-denoise/adapter.json`,
  identity `ffmpeg-denoise-v1`, which declares offline CLN-01 waveform I/O.
  The task-local identity is `ffmpeg-afftdn-synthetic-frequency-domain-v1`;
  it emits waveform output but **no numeric FFmpeg parity** is claimed.
- The method is a frozen Hann-windowed STFT power-subtraction reference:
  256-sample window, 160-sample hop, 96-sample lookahead, spectral exponent
  1.7, gain floor 0.125, per-bin gain release 0.7. The noise profile is the
  mean bin power over the explicit noise-only calibration span `[0,1600)`.
  A gain of 1 is an exact overlap-add identity by construction.
- FFmpeg was probed before implementation: `ffmpeg -version` and `which -a ffmpeg`
  were unavailable and the historical imageio-ffmpeg binary path was absent.
  `tool-provenance.json` records these invocations and the pinned historical
  GPL provenance. **No FFmpeg binary, source, download, GPL configuration
  string, configure flags, or licensed runtime is present here.** No numeric
  parity claim is made because the real pinned tool is unavailable.
- `provider.json` is a proposal-only manifest: `registered: false`,
  `default_enabled: false`, `processor_exposure: false`, `decision: DEFER`.
  No C boundary is compiled, linked or registered; no opt-in consumer exists.
- All outputs are synthetic evidence. Missing, rejected, invalid, unrun or
  blocked results do not qualify and are never promoted to a pass.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests and
`verify.py` fail closed on a missing or changed pin; there is no substitution,
pooling or tolerance.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` |
| `adapters/ffmpeg-denoise/adapter.json` | `2909f28275cd05df650af3d38ee7ec523cab00e8a5a52ed89773dd450a35a4fe` |
| `adapters/ffmpeg-denoise/README.md` | `cb498047caa12890f89754411a478e9d870ff03100876031ee0abe84889b3530` |
| `adapters/ffmpeg-denoise/run.py` | `db183ece8d8c4f04a97ce0fd1ce588ec07f8946061096008a51de3ae45c4ab4b` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

The mutable board snapshot (`plan/swarm/TASKS.json`,
`77d43709d7bffa83ba52410818f1da76527dc1dd5697d39012d6932320e5458b` at read
time) is provenance only and never gates this evidence. Historical FFmpeg
afftdn pilot values are source-reported context only and are **not** rerun,
pooled or qualified here.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` → `acceptance_profile` and checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Identity/noisy control and documented synthetic baseline | `noisy_identity_control` and `synthetic_fixed_gain_baseline` scored for every paired item |
| Paired SI-SDR and STOI-style scores | `scorer.py` computes SI-SDR and a labeled non-standard band-cosine surrogate on frozen clean references |
| Clean-speech preservation, peaks, invalid outputs | `clean_speech_preservation` scores, peak/finite checks, explicit NaN/peak rejection controls |
| Unpaired speech predictive proxy only | `unpaired_predictive_proxy` is labeled `predictive_proxy_not_quality_not_listening`; no MOS/ASR/human listening |
| Alignment, state, unpaced synthetic timing | 160-sample hops, 256-window, 96-sample lookahead, epoch-scoped state reset, deterministic operation count only |

No real authoritative NS baseline is claimed. No device timing, pacing,
availability, target workload, listening, intelligibility, quality acceptance
or release qualification is claimed.

## Method

1. `fixture.py` synthesises four paired 8,000-sample (0.5 s) 16 kHz mono
   items from integer LCG states, a fixed harmonic speech envelope and a
   deterministic noise/hum/burst mixture. The first 1,600 samples are
   noise-only calibration; speech gates are frozen at `[1600,2400)`,
   `[2800,4800)`, `[5200,7200)`.
2. `reference.py` computes a mean power spectrum over calibration frames,
   then applies real gain-only STFT power subtraction with OLA normalisation.
   The processor validates epoch, sequence, format and frame length; rejected
   frames never mutate state.
3. `scorer.py` reports SI-SDR (120 dB cap) and a non-standard STOI-style band
   cosine surrogate. The surrogate is explicitly labeled and is not STOI.
4. `run.py --report` generates the report three times, requires byte-identical
   payloads, and only then writes `report.json` and `report.json.sha256`.
5. `verify.py` checks pins, strict JSON, disposition, repeat determinism,
   licensing controls, scope and minimum test count.

## Results (synthetic only)

Four paired synthetic items, 50 frames per item (160 samples), 96-sample
declared lookahead. All peaks finite and <= 1.0. No invalid output accepted.

| Condition | Mean SI-SDR dB | Mean STOI-style |
| --- | ---: | ---: |
| noisy identity control | 9.796 | 0.818 |
| synthetic fixed-gain baseline (0.7) | 9.796 | 0.739 |
| synthetic afftdn reference | 12.344 | 0.809 |
| clean-speech preservation | 120.000 | 1.000 |

The fixed-gain baseline is documented as a synthetic control, not an
authoritative NS baseline. The clean-preservation item processes clean speech
with a zero-noise calibration profile, so its exact identity is a boundary
control rather than a quality result. The non-standard STOI-style surrogate
is reported for completeness, not used as an acceptance gate: in this cohort
the enhanced output improves paired SI-SDR but not the surrogate. The unpaired
proxy reports only deterministic energy-ratio changes and is labeled
non-quality.

## FFmpeg/tool provenance and blocked context

`tool-provenance.json` records: `ffmpeg -version` unavailable
(`FileNotFoundError` / exit 127), `which -a ffmpeg` returned not found, and
the historical imageio-ffmpeg 7.1 binary path absent. Historical asset
provenance is pinned from `research/noise_suppression_assets_20261027.json`
(binary SHA-256 `6d175a4743ca50256e89a8cdd731100f9cee33bd79aeea46894d209410dc6617`,
49,368,728 bytes, reported GPL-2.0-or-later, configure flags unavailable).
No binary was vendored, downloaded, executed, or used for parity.

## Failure controls

- Invalid/nonfinite frame: rejected, state unchanged.
- Wrong epoch/rate/channels/format/length: rejected.
- Duplicate/future sequence: rejected.
- Peak-above-one / NaN output: rejected by scorer, never promoted.
- Missing result: never promoted to pass.
- State reset: epoch-scoped digest changes and prior sequence state is cleared.

## Reproduction

Python 3.11+, standard library only. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
python3 -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
```

From the worktree root:

```sh
scratch="${TMPDIR:-/tmp}/sdk-afftdn-check-$$"
cmake -S . -B "$scratch/sdk" -DCMAKE_BUILD_TYPE=Release \
  -DCMAKE_INSTALL_PREFIX="$scratch/prefix" -DCMAKE_INSTALL_LIBDIR=lib
cmake --build "$scratch/sdk" --parallel 4
ctest --test-dir "$scratch/sdk" --output-on-failure
cmake --install "$scratch/sdk"
git diff --check
git diff --cached --check
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-FFMPEG-AFFTDN
```

REUSE lint 6.3.0 must be clean. SPDX annotations are required on all files;
Python/JSON split or escape the license token to avoid a literal `SPDX&#45;License-Identifier:` token inside Python/JSON strings, and Markdown prose uses the HTML escape.

## Remaining gates / non-claims

No real FFmpeg runtime, GPL binary review, real speech, corpus, recording,
listening, quality, intelligibility, device timing, pacing, power, production
availability or release qualification is claimed. No public-surface,
installed-behavior, board or cross-task change exists; no gate was weakened.

Remaining gates before any processor exposure or qualification claim:
independent exact-head review; hosted CI; rights-cleared paired cohort with
permitted clean references; exact local FFmpeg build/version/configure/GPL
configuration; real pinned-tool parity run; pinned target device/deadline
pacing and availability workload; independent provider intake; S10/protocol
clearance; release approval. `DEFER` remains in force until every gate is
closed.
