<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-03 — wind and microphone disturbance evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-03` (Wind and microphone disturbance reduction, legacy family `F08`). It
matches the catalogued method families, the named source lead (`S45`) and
historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-03`; independent reviewer:
`reviewer-SURVEY-CLN-03`. Claim base: audio-sdk
`d507634052555c08f10aa9a3b344576c7429076a`; branch
`swarm/SDK-SURVEY-CLN-03`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map does and does not cover

The catalogued boundary is explicit: wind/turbulence and related capture
interference must use **separate stress tests**, and dedicated wind candidates
and weights still require discovery. Wind noise is broadband and
non-stationary; a fixed high-pass or narrow notch is only a partial
low-frequency control and is **not** promoted here as wind suppression. Gusts,
handling/pops and digital disturbance are separate subcases.

`CLN-07` (beamforming and spatial filtering) and `CLN-10` (tonal correction and
interference filtering) are different catalogued categories. Spatial and
tonal rows are named only as boundaries or adjacent controls; their results are
not pooled into a CLN-03 wind claim.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: detection and frequency-dependent attenuation | `sdk-high-pass-80-hz` (integrated): installed 16 kHz two-pole 80 Hz high-pass; 128/128 fixture checks, −3.01 dB at 80 Hz, 24.10 dB attenuation at 20 Hz, zero content delay, synthetic speech proxy only. `native-variable-cutoff-high-pass` (source-local, unbenchmarked here); `narrow-biquad-notch` (partial): optional synthetic RBJ notch, 78-frequency sweep, 0.006 dB maximum sweep error | No wind, turbulence, gust, real-speech preservation, listening or device-timing result; broadband wind is not a fixed filter response |
| Classic: spectral suppression and adaptive noise estimation | `webrtc-apm-ns`, `speexdsp-ns-reference`, `classical-spectral-subtraction`, `classical-wiener-denoising`; adjacent DNS2020 pilot values only | Additive DNS noise is not a wind/turbulence cohort; whole-clip estimates are non-causal where noted |
| Classic: channel selection and multi-microphone combination | `3d-microphone-spatial-time-alignment`, `delay-and-sum-beamformer`, `mvdr-beamforming`, `source-localization-direction-of-arrival` (all considered) | Catalogued only; no wind, geometry, channel-mismatch or array execution |
| ML: wind-aware universal enhancement (`S45`) | `gap-urgenet` (blocked), `urgent-bsrnn` (blocked), `urgent-bsrnn-flow` (considered), `tf-gridnet-urgent-2025-baseline` (considered) | No URGENT source, checkpoint, weight, training data, evaluation audio or runtime staged |
| ML: general enhancement applied to capture disturbance | `rnnoise-v0-2` (evaluated), `deepfilternet3-v0-5-6` (evaluated), `fastenhancer-small-reference` (evaluated), `clearvoice-frcrn-16-khz` (evaluated) | Historical DNS2020/EARS evidence is adjacent noise suppression, not wind; no wind-condition score |
| ML: neural spatial filtering | `neural-beamforming` (blocked), `spatialnet` (blocked) | No local implementation, weights or wind execution |

`report.json` holds the full records: both catalogued branches, the `S45`
source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Installed 80 Hz high-pass DSP conformance | `sdk-high-pass-80-hz` | Synthetic tones, DC/chirp, 20 Hz rumble plus speech proxy; no wind or real speech |
| `HE-2` | Narrow biquad notch synthetic sweep | `narrow-biquad-notch` | Optional 1000 Hz / 100 Hz-bandwidth notch; narrow tonal control, not broadband wind |
| `HE-3` | RNNoise noise-suppression pilot | `rnnoise-v0-2` | 30 paired DNS2020 items; ΔSI-SDR +3.14 dB, ΔSTOI +0.0215, process-frame RTF 0.0662 |
| `HE-4` | SpeexDSP noise-suppression pilot | `speexdsp-ns-reference` | 30 paired DNS2020 items; ΔSI-SDR +1.06 dB, ΔSTOI −0.0057, batch RTF 0.0006 |

Comparison inputs add the VoiceBank+DEMAND chain-level preset with an 80 Hz
high-pass (`voice_focus.v1` PESQ 2.233 / STOI 0.9086 / SI-SDR 5.72 dB versus
`basic.v1` 2.160 / 0.9086 / 9.44 dB), the URGENT 2025/2026 wind taxonomy, and a
**missing** dedicated wind cohort. The chain comparison is explicitly
confounded: the high-pass is not isolated from Speex NS and limiting, and the
corpus is not wind. Every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local paired synthetic:** high-pass tone/DC/rumble conformance
  and narrow-notch frequency sweep. These prove deterministic filter behavior,
  not wind mitigation or speech preservation.
- **Historical local adjacent noise suppression:** RNNoise and SpeexDSP DNS2020
  pilots. Adjacent additive-noise context only.
- **Historical local adjacent chain:** VoiceBank+DEMAND preset ablation with a
  high-pass in one arm. Chain-level and corpus-mismatched.
- **Source-reported only:** URGENT 2025/2026 wind taxonomy and challenge rules.
- **Not present:** dedicated wind/turbulence or microphone-disturbance audio,
  annotated gust/handling events, clean references, wind-aware weights, local
  wind execution, human ratings, target-device timing or a new benchmark.
- The fixed high-pass is an adverse-scope reminder: it removes low-frequency
  energy but cannot separate broadband wind from wanted low-frequency speech.
  It is recorded as partial, never as a wind result.

## Bounded gaps and feasibility links

Nine gaps are recorded. Gaps with a feasibility owner (`G01`, `G03`, `G04`,
`G05`, `G07`, `G09`) link **existing** URGENT-family, spatial or evidence-manifest
rows. Gaps without a component owner (`G02`, `G06`, `G08`) link existing
research-control or foundation rows and carry a `no dedicated CLN-03 ...` owner
note. Those links are scoping leads only: no processor is enabled, no capability
is implemented, and no missing result is promoted. Board status is excluded
from all gates; only linked `id`/`title`/`mode` are projected to a stable
digest. The mutable board file is referenced by path and **never hashed into
canonical bytes**, so status edits elsewhere in the swarm cannot change this map
or break its digest.

## Release boundary

Keep wind/turbulence, handling/pops and digital disturbance separate; preserve
wanted low-frequency speech; keep synthetic DSP, adjacent noise-suppression,
chain-level, source-reported and missing results distinct. No public
benchmark/quality/device/listening/release claim is made. No assets, real wind
audio, provider enablement, default, ABI, build or CI change is included. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-03
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `a6e14631c8d42287ae0524d573b6e8e6946ab19a5fae1ae70241e6795cf3b116`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
