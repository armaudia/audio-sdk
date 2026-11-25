<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-09 — gain, loudness and dynamic-range control evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-09` (Gain, loudness and dynamic-range control, legacy family `F09`). It
matches the catalogued method families, the named source leads (`S27`, `S19`,
`S46`) and historical local or source-reported executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-09`; independent reviewer:
`reviewer-SURVEY-CLN-09`. Claim base: audio-sdk
`d5b11912cd09e87296cd9d4654f1917c9cb94258`; branch
`swarm/SDK-SURVEY-CLN-09`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map does and does not cover

The catalogued boundary is explicit: **capture gain, digital leveling, peak
limiting and whole-file normalization are separate subcases**, and clipping and
noise amplification must be tracked. A level controller that raises a noise
floor during pauses is not a loudness win; a limiter that only caps peaks is not
a normalizer; an offline two-pass loudness target is not a streaming gain stage.
`CLN-10` (tonal correction), `RST-01` (declipping/saturation restoration),
`CLN-01` (noise suppression) and `CLN-05` (acoustic echo cancellation) are named
only as boundaries or adjacent controls. Their results are not pooled here.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: static and whole-file level normalization | `static-target-gain-with-peak-ceiling` (evaluated): synthetic -24 dBFS target, ±18 dB bounds, -1 dBFS ceiling, zero content delay; `ridge-static-gain` (evaluated): synthetic 180/60 train/held-out split, ridge 4.235 dB mean absolute RMS error versus 2.290 dB for the direct rule; `ebu-r128-ffmpeg-loudnorm` (partial): synthetic offline loudness target, -33.846 → -23.0 LUFS, 0.0 LU target error | No rights-qualified real-speech cohort, no standards meter, no EBU test set and no complete programme |
| Classic: envelope and automatic gain control | `envelope-agc` (partial): synthetic causal 10 ms/250 ms AGC, seven interaction configurations, 212 clipped samples with AGC alone; `speex-agc-and-activity-output` (partial): vendored SpeexDSP preprocessor with advisory VAD, gain -7…+17 dB on the step case | Gain-step tracking was worse than identity; the WebRTC AGC2 (`S27`) candidate is considered only and never executed |
| Classic: feed-forward compression and full-band receive DRC | `feed-forward-compressor` (partial): synthetic gain-law RMSE 1.024914 dB versus 12.82719 dB identity; `full-band-receive-drc-control` (evaluated): synthetic soft-knee compressor, measured 16.1875 ms attack and 165.75 ms release, zero excess ceiling | No live preference evaluation, no matched native chain and no real speech |
| Classic: peak limiting and true-peak ceiling | `peak-limiter-reference` (source-local): synthetic zero-lookahead limiter, 1.107014 → 0.980000 peak, 4 engaged frames on clean speech; `native-zero-latency-sample-peak-limiter` (source-local, audio-pro) | No SDK parity, no true-peak standard and no target-device ceiling study |
| Classic: auditory-model multiband compression and noise-aware shaping | `adaptdrc-ssdrc`, `noise-aware-shaping-plus-drc` (considered / research-control) | Catalogued only; no local candidate execution, checkpoint or comparison |
| ML: learned joint enhancement and loudness control | `se-agcnet` (considered) | Upstream project claim only; no checkpoint, runtime, licence or measurement |
| ML: learned multiband dynamics and neural parametric EQ | `self-supervised-neural-multiband-eq-and-dynamics`, `differentiable-biquad-neural-parametric-eq` (considered) | Paper-level leads only; tone correction belongs to `CLN-10` |
| ML: trainable dynamic-compression feature frontend | `pcen-feature-frontend` (considered) | Adjacent feature frontend, not a waveform loudness controller |

`report.json` holds the full records: both catalogued branches, the `S27`/`S19`/
`S46` source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Static target-RMS gain with hard peak ceiling | `static-target-gain-with-peak-ceiling` | Synthetic level stimuli; zero content delay and zero lookahead |
| `HE-2` | Ridge static-gain synthetic held-out screen | `ridge-static-gain`, `static-target-gain-with-peak-ceiling` | 180 train / 60 held-out synthetic clips; ridge loses to the direct rule |
| `HE-3` | Envelope AGC with interaction controls | `envelope-agc` | 12 cases, 7 chain configurations, gain-step error worse than identity |
| `HE-4` | Feed-forward compressor sweep | `feed-forward-compressor` | 100 amplitude points, 39 frequency points, synthetic only |
| `HE-5` | Full-band receive DRC measurements | `full-band-receive-drc-control` | Clean speech, steps, near-clip and pre-clipped probes; limiter OFF by default |
| `HE-6` | Peak limiter reference | `peak-limiter-reference` | Zero-lookahead limiter on clean speech, impulse and nonfinite probes |
| `HE-7` | EBU R128-style loudness target | `ebu-r128-ffmpeg-loudnorm` | 2.5 s synthetic fixture; Python estimator, not an FFmpeg or EBU meter |
| `HE-8` | Speex AGC + advisory activity output | `speex-agc-and-activity-output` | Native vendored preprocessor, 23 cases × 3 repeats, VAD advisory only |
| `HE-9` | Historical AGC gain-step screen | `envelope-agc` | 743 EARS recordings plus 30 noisy DNS2020 pairs; SI-SDR/STOI declined |
| `HE-10` | Historical FFmpeg 7.1 two-pass loudnorm | `ebu-r128-ffmpeg-loudnorm` | 30 EARS excerpts, 29/30 within ±0.2 LU, self-measured, no independent meter |

Comparison inputs separate synthetic fixtures, recorded research screens, the
frozen DSP acceptance profile, BS.1770/EBU R128 protocol documentation and a
**missing** rights-qualified paired cohort with device gain. The FFmpeg screen is
offline mastering only and self-measured; the EARS AGC screen has no clean
reference. Every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local synthetic:** the eight task-local fixtures (static gain,
  ridge, envelope AGC, compressor, receive DRC, peak limiter, R128 target,
  Speex AGC). These prove deterministic behaviour on seeded stimuli, not speech
  quality.
- **Historical local recorded research:** the 743-clip EARS AGC screen and the
  30-excerpt FFmpeg loudnorm screen. Recorded material, but without clean
  references, independent metering or listening.
- **Source reported only:** WebRTC AGC2 interface behaviour (`S27`), FFmpeg
  loudness/limiter filters (`S19`), SSI challenge framing (`S46`), SE-AGCNet,
  neural parametric EQ / multiband dynamics and the private native limiter.
- **Not present:** rights-qualified paired cohort, independent BS.1770/EBU Mode
  meter and EBU test set, capture/device gain measurement, authorized listening,
  pinned provider parity, target-device timing, release approval.

The failure envelope is explicit. Envelope AGC raised windowed RMS error from
4.447 dB (identity) to 10.646 dB on the gain-step probe and clipped 212 samples
when run alone. The historical AGC screen improved level error while SI-SDR and
STOI declined. AGC-then-limiter only matched AGC-alone because the AGC ceiling
was already below the limiter ceiling, which is a chain-order artifact rather
than a chain benefit. These are cautions, not a family verdict.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with an existing feasibility owner (`G03`, `G05`)
link WebRTC AGC2, SE-AGCNet, AdaptDRC/SSDRC and self-supervised multiband
dynamics rows. Gaps without a component owner (`G01`, `G02`, `G04`, `G06`,
`G07`, `G08`, `G09`, `G10`) link existing research-control or foundation rows
and carry a `no dedicated CLN-09 ...` owner note. Those links are scoping leads
only: no processor is enabled, no capability is implemented, and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep capture gain, digital leveling, whole-file normalization and limiting
separate; keep level tracking and noise amplification separate from speech
quality; keep synthetic, recorded-research, predicted, source-reported and
missing results distinct. No public benchmark, quality, device, listening or
release claim is made. No assets, real speech, weights, provider enablement,
default, ABI, build or CI change is included. All files are inside this task
directory; board, handoff and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical output,
adverse rejections and three cold-start repeats. JSON and manifest files have
SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-09
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `7c4e8f7a29c38970d7ad4a1b1b34e71d62d696a16d4e607c400fae0b685308e1`.

The change is task-local documentation and stdlib tooling; no installed package,
descriptor catalog, ABI, build input or CI workflow is touched. The repository's
installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
