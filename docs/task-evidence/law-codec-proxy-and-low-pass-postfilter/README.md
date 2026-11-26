# SDK-LAW-CODEC-PROXY-AND-LOW-PASS-POSTFILTER — DEFER research-control evidence

<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

Task-local, **proposal-only**, **incomplete** and **not qualified**
**Restoration**-profile evidence for the µ-law codec proxy and low-pass
postfilter research-control candidate.

**Decision: `DEFER`.** No result in this package qualifies the candidate and
no processor is exposed.

> **No real-codec claim.** The 4-bit and 8-bit signals here are a
> peak-normalised logarithmic companding **proxy** copied from a first-party
> synthetic pilot. They are **not** ITU-T G.711 µ-law, not MP3/AAC/Opus/AMR,
> and not a transport-codec, tandem-coding or packet-loss result. The
> low-pass postfilter is a 3900 Hz zero-phase forward-backward filter applied
> to a whole clip. It is not frame-causal.

## Boundary

The package is limited to
`docs/task-evidence/law-codec-proxy-and-low-pass-postfilter/**`. It changes
no installed v0 behaviour, public API/ABI, `CONTRACTS.md`, descriptor
registry, registry default, shared CMake, dependency lock, CI workflow,
board row or handoff. Installed v0 stays **16 kHz, mono, float32, 160 samples
per call**.

No provider is registered, no descriptor is added, nothing is enabled by
default, and no codec, model, corpus, media, weight or runtime is downloaded,
read, hashed, loaded, compiled, executed or bundled.

## What is reproduced

The pinned first-party pilot is present and digest-verified:

| Artifact | Role |
| --- | --- |
| `research/distortion_restoration_20261028.md` | research record and limits |
| `src/audioml_eval/distortion_restoration.py` | exact quantizer and postfilter source |
| `scripts/evaluate_distortion_restoration.py` | exact RST-03 pipeline |
| `reports/distortion-restoration/20261028-synthetic-screen.json` | frozen metric rows (provenance only) |
| `tests/test_distortion_restoration.py` | pilot unit tests |

`reference.py` is standard-library only and reproduces, on a deterministic
synthetic stimulus:

1. the pilot's `mulaw_roundtrip` quantizer, bit-for-bit in development
   comparison with the pinned function;
2. the pilot's `scipy.signal.resample_poly` 16 kHz ↔ 8 kHz geometry,
   reimplemented as a Kaiser β=5.0, 81-tap polyphase FIR;
3. the pilot's 4th-order Butterworth 3900 Hz `sosfiltfilt` postfilter,
   reimplemented with odd edge padding and per-section steady-state
   initialisation;
4. paired SI-SDR and RMSE on a deterministic harmonic speech-like fixture,
   with an identity control and explicit finite/peak bounds.

The committed verifier does **not** invoke numpy, scipy, pystoi, soundfile or
any external runtime. A one-off development cross-check against an unrelated,
unpinned workspace virtual environment is documented here as non-qualifying
provenance; the evidence does not depend on it and its presence is not
embedded in the report bytes.

The fixture reproduces the **formulas**, not the pilot corpus or its metric
rows. `pilot_numeric_parity=false`.

## Why DEFER

The frozen pilot is a small, contradictory signal:

| Condition | Decoded SI-SDR | Postfiltered SI-SDR | Delta |
| --- | ---: | ---: | ---: |
| 4-bit stress proxy | 16.427 dB | 16.709 dB | **+0.282 dB** |
| 8-bit proxy | 37.993 dB | 33.120 dB | **−4.873 dB** |

STOI is effectively unchanged in both conditions (0.8751 → 0.8749 and
0.9984 → 0.9977). The postfilter helps only the non-standard 4-bit stress
proxy and harms the 8-bit proxy. The pilot itself states that the 4-bit case
is not a standard codec and that neither case models MP3/AAC/Opus transform
coding, tandem coding or jitter.

Every one of these blockers is independent:

- **No exact licensed codec reference.** No G.711 implementation,
  conformance vector, real transport codec binary or revision is admitted.
  `audioop` would expose a CPython G.711 µ-law path, but it is
  deprecated/removed on target Python 3.12+, unpinned, and is not the proxy.
- **No admitted pilot runtime.** numpy, scipy, pystoi and soundfile are not
  pinned or admitted. The report embeds no live interpreter probe; an
  unrelated workspace virtual environment has no lock or wheel digests and is
  not invoked.
- **No corpus.** `data/datasets/ears-blind/audio` is absent. No EARS audio
  was read.
- **No rights or consent.** The rights register has no law-codec entry.
  Acquisition, evaluation, redistribution, deployment, playback and consent
  are unknown.
- **No exact-reference parity.** No approved output exists for a frozen input
  under an exact runtime.
- **No restoration-profile evidence.** No real-codec decoded intervals,
  degradation/erasure/bandwidth strata, STOI, independent scoring or
  permitted listening.
- **No target-runtime timing.** Global peak normalisation and zero-phase
  whole-clip filtering are non-causal; no first-output, tail, pacing,
  deadline or memory measurement exists.
- **No provider intake or default decision.**

## Fixture results (non-qualifying)

The deterministic 3200-sample synthetic fixture is a mechanical control only.

| Condition | Decoded SI-SDR | Postfiltered SI-SDR | Delta |
| --- | ---: | ---: | ---: |
| 4-bit stress proxy | 19.865 dB | 20.091 dB | +0.226 dB |
| 8-bit proxy | 38.799 dB | 37.078 dB | −1.721 dB |

The signs match the pilot; the magnitudes do not, because the stimulus and
corpus differ. The postfilter's own distortion bounds the identity control at
about 43.6 dB SI-SDR. STOI is `null` with
`stoi_status="not_computed_runtime_absent"`; it is never fabricated.

These numbers are **not** pilot reproduction and **cannot** qualify the
candidate.

## Frame and adverse behaviour

`process_frame` validates a v0-shaped 160-sample request and applies only the
proxy quantizer. The postfilter is rejected on the frame path with
`FRAME_POSTFILTER_UNSUPPORTED` because it needs the whole clip. The fixture
rejects, without advancing state:

- missing, empty, short and long sample sequences;
- NaN, +Inf, −Inf and non-numeric samples;
- zero or sub-floor peaks and peaks above the declared range;
- 3-bit and 9-bit widths, non-integer and boolean widths;
- 8 kHz, two-channel and 320-sample geometry;
- a true or non-boolean postfilter flag and unknown modes;
- unknown or missing config keys and non-object configs.

`ProxySession` exercises epoch/position ordering, stale epochs, duplicate and
out-of-order frames, increasing-epoch reset, negative reset positions,
post-reset continuation, closed sessions and independent per-session state.
Strict JSON rejects duplicate keys, `NaN`, `Infinity`, `-Infinity`, truncated
documents and wrong roots. All rejection counts are recorded in `report.json`.

## Eight blocked release gates

| Gate | Status |
| --- | --- |
| RG-01 exact codec reference identity | blocked |
| RG-02 pilot runtime and reproduction | blocked |
| RG-03 rights-cleared corpus | blocked |
| RG-04 exact reference parity | blocked |
| RG-05 restoration quality evidence | blocked |
| RG-06 independent scoring and listening | blocked |
| RG-07 target runtime timing | blocked |
| RG-08 provider intake and default selection | blocked |

`contract.json` and `report.json` carry the exact reason and reopen condition
for each gate. No gate may be marked passed from this package.

## Files

| Path | Purpose |
| --- | --- |
| `reference.py` | Standard-library quantizer, resampler, postfilter, metrics, frame/session validation, probes, report builder. |
| `run.py` | Regenerates report, sidecar, sources and contract byte-for-byte. |
| `report.json` | Canonical machine-readable report. |
| `report.json.sha256` | SHA-256 of the committed report bytes. |
| `contract.json` | Machine-readable decision, boundary, pins, blockers and gates. |
| `SOURCES.sha256` | Pins for all external/boundary/task-local artifact bytes. |
| `test_reference.py` | Standard-library unittest suite. |
| `verify.py` | Strict read-only verifier: pins, semantics, licensing, scope, three cold starts. |
| `*.license` | SPDX sidecars for machine-readable files. |

## Reproduce and verify

```sh
cd docs/task-evidence/law-codec-proxy-and-low-pass-postfilter
python3 run.py --all
python3 test_reference.py
python3 verify.py
python3 -m reuse lint   # from the SDK root
git diff --check
```

`run.py --verify-repro` regenerates every byte in memory and compares it with
the committed files; `verify.py` performs three fresh cold-start runs and
requires all report, sidecar, source and contract bytes to agree.

## Reopen conditions

Reopening requires, at minimum: an exact licensed real-codec reference with
revision and artifact digest; admitted conformance vectors; a pinned runtime
with wheel digests; the frozen pilot inputs and a three-cold-start metric
reproduction; a rights-cleared paired corpus with recorded consent; real
transport-codec degradation/erasure/bandwidth strata; decoded-interval
accounting; STOI or another independent scorer; permitted listening; a
frame-causal or explicitly delayed streaming design with target-runtime
timing; and an explicit opt-in provider decision with OFF default. Until
then, `DEFER`, `incomplete`, `not_qualified` and eight blocked gates stand.
