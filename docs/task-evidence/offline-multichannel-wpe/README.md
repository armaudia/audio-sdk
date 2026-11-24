<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-OFFLINE-MULTICHANNEL-WPE — task-local synthetic evidence

**Status: `proposal_only_not_qualified` · completeness `incomplete` · decision `DEFER`.**

This directory is optional, opt-in, unregistered and disabled by default task-local
evidence. It applies the `room` acceptance profile from
`audio-benchmark-platform/plan/swarm/VERIFICATION.md` to a frozen, fully synthetic,
deterministic two-channel dereverberation fixture set. It is **not** a processor
exposure, a provider registration, an installed SDK v0 behavior change or a
release qualification. No candidate is qualified by any result here.

## What is implemented

- A pure-Python, whole-clip, **noncausal** frequency-domain multichannel WPE
  reference (`reference.py`): 512-point FFT, 160-sample hop, 3 taps per channel,
  a 2-frame predictor delay, 2 iterations, diagonal loading, complex Gaussian
  elimination with partial pivoting, a prediction-energy cap, sqrt-Hann
  analysis/synthesis and zero added content delay. Covariance statistics are
  accumulated over the entire buffer before any frame is enhanced; every output
  frame depends on frames after it. This is never a streaming or real-time claim.
- A frozen analytic fixture generator: seeded vowel-like source with a noise-free
  leading prefix, two seeded synthetic RIRs per condition with frozen geometric
  TDOA, six early taps, a low-passed exponential tail, colored additive noise,
  a piecewise-linear per-channel movement schedule, a delayed lower-pitched
  analytic overlapping talker, and a frozen reset schedule.
- Paired per-channel SI-SDR and STOI against a frozen 50 ms early-reflection
  target, with primary channel 0 plus per-channel and worst-channel reporting.
  Identity and noisy identity controls, a clean near-end preservation control,
  a blocked missing-reference case, a blind no-reference suppressor control and
  adverse/out-of-range/nonfinite cases are all reported. No missing result may
  qualify a candidate.
- An opt-in Python waveform adapter (`run.py`, `adapter.json`, `provider.json`)
  that is unregistered and disabled by default. OFF is a bit-exact identity;
  ON invokes the whole-clip reference. The installed v0 remains 16 kHz mono
  float32 at 160 samples/frame; the 160-sample grid here only freezes fixture
  chunk shapes.
- The scorer (`scorer.py`) is inherited byte-identically from
  `docs/task-evidence/offline-mono-wpe/scorer.py` except for `SCORER_ID`. The
  inherited cross-check vectors are copied byte-identically and validate only
  the scoring code, not any multichannel candidate result.

## Measured result — the candidate did not qualify

The whole-clip multichannel WPE produced a measurable **regression** against the
frozen early-reflection target on all three synthetic RIR stratifications.
These are reported as measured, not tuned away, and are one reason for DEFER:

| Condition | RT60 ms | D/R dB | identity SI-SDR dB | WPE SI-SDR dB | ΔSI-SDR dB | ΔSTOI |
|---|---:|---:|---:|---:|---:|---:|
| short_rt60 | 250 | 12 | 17.144701 | 15.281656 | -1.863045 | -0.004987 |
| medium_rt60 | 550 | 6 | 5.641561 | 5.071096 | -0.570465 | -0.004827 |
| long_rt60 | 900 | 0 | 0.257586 | -0.382394 | -0.639980 | -0.004030 |

Worst-channel ΔSI-SDR is -2.317771 dB (short), -0.841903 dB (medium) and
-0.639980 dB (long). The movement control is -0.636604 dB and the overlap
control is -0.718387 dB. Clean near-end preservation scores 21.707406 dB
SI-SDR / 0.998243 STOI; the provider OFF path is a bit-exact identity and the
ON path differs. Three fresh cold-start passes over the pinned two-channel probe
produce byte-identical f32 tensor digests. No listening, MOS, real-speech STOI,
real RIR, target-device timing or release qualification was attempted.

## Scope and non-claims

- No real recording, RIR measurement, model weight, download, licensed runtime,
  listening test, target-device timing, quality acceptance or release claim.
- No oracle use: the legacy mono noncausal and causal results are read only as
  explicitly scoped comparison rows; neither is a target, threshold or
  substitute for the multichannel candidate.
- No public API/ABI, header, descriptor, registry, default, installed v0 source
  or shared build file is modified. No provider is registered.
- The optional C boundary is intentionally **skipped**: the hard write scope
  permits only this task-local evidence directory, while `provider/tests/` and
  shared build files are out of scope. OFF/ON behavior is instead exercised at
  the opt-in Python adapter boundary. No generated C header or unlinked C
  consumer is added.
- The room profile's delayed/missing render case is not applicable to a
  dereverberation fixture with no separate render/echo-return channel; it stays
  open for any future AEC-style qualification.

## Reproduction

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report       # prints report digest
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources      # prints SOURCES digest
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_reference
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

`run.py --report` writes canonical `report.json` (sorted keys, compact
separators, no NaN, one trailing newline) and its sidecar. `verify.py` is
read-only and re-checks pins, strict JSON, canonical bytes, the sidecar, three
byte-identical cold-start passes, the acceptance structure, SPDX coverage and
write scope. Licensing is additionally checked with REUSE 6.3.0 `reuse lint`
from the SDK root.

## Key digests

- Base commit: `bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0`
- Fixture digest: `404af1cb4fbafea873a9a0bf62a8eac14bbda7b10d4944a1850149168a705edb`
- `report.json` SHA-256: `4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba`
- Canonical report digest (sidecar): `1dd484332e2bed68598f5bf5ffac924b48acca7cfe60e1d0596cb0095a14faee`
- `SOURCES.sha256` SHA-256: `e7f7fc6a5d11b65a9a6d0796d50a45e2a79f38701aae1a0b392b5c6f5891f235`
- Scorer cross-check vectors digest: `7455e1a8ab5a94a5307f2cb990ceaf31cd0fbd1cd4c0f2e8e9a3c8a109b65e78`

All external provenance, boundary and sibling-artifact pins are recorded in
`SOURCES.sha256`, `contract.json` and the report. The mutable board snapshot is
recorded with its read-time digest and is never used as a runtime input.

## Remaining gates before any exposure

1. Held-out real-room or standards-room paired SI-SDR/STOI with pinned RIR
   provenance, rights and a defined early-reflection target.
2. Listening/MOS on licensed real speech with a declared listener protocol.
3. A genuinely causal multichannel variant measured on the exact target device
   (CPU, memory, pacing, deadlines, content delay); the present algorithm is
   noncausal and cannot support a realtime claim.
4. A separate render/echo-return fixture for any AEC-style delayed/missing
   render qualification.
5. Provider intake, license, descriptor and public catalog review.
6. Explicit release approval; no default, registry or public catalog change
   before then.
