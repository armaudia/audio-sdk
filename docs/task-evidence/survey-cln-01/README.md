<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-01 — cleaning/restoration category evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-01` (Background noise suppression, legacy family `F01`). It matches the
original method families, the three named source leads and historical local or
source-reported executions to existing board components. It creates **no new
execution, model, corpus, provider, processor, ABI, default, build, CI, board,
handoff or release change**.

Owner: `agent-SURVEY-CLN-01`. Reviewer: `reviewer-SURVEY-CLN-01`. Claim base:
`c9296ae96a2b58efae559bd22e7760122c886df8` (after merging current `origin/main`).
The board row depends on `SDK-FND-AUDIT` and `SDK-FND-EVIDENCE`; the mapped
acceptance profile is **Enhancement** from
`audio-benchmark-platform/plan/swarm/VERIFICATION.md`. “Historical local” below
means a pinned record documents an execution in the original workspace; it does
**not** mean that anything ran for this survey. “Source-reported” means a vendor
or upstream claim with no local matched execution.

## Scope and boundary

- Category: `CLN-01`, group “Acoustic cleanup and spatial processing”, requested,
  waveform output. Purpose: reduce additive noise while preserving wanted
  speech. Discovery is `catalogued`; candidate census and benchmark are both
  `not_started`.
- The comparison boundary keeps stationary noise, changing noise and competing
  speech separate. Current speed is not an admission gate. Adjacent `CLN-02`
  (clicks), `CLN-04` (dereverberation), `CLN-05/06` (echo), `CLN-09` (gain),
  `CLN-12` (near-end listening) and the `RST-*` restoration categories are
  **outside** this category; they appear only as documented boundary controls.
- Documented public v0 geometry remains 16 kHz mono float32, 160 samples per
  frame. No production callback, provider, descriptor, registry or public API
  is implemented or changed.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `provider_registration=false`, `processor_exposure=false`,
  `public_api_abi_changed=false`, `installed_v0_changed=false`,
  `descriptor_registry_changed=false`, `shared_cmakelists_changed=false`,
  `ci_changed=false`, `board_changed=false`, `handoff_changed=false`.
- No real speech, corpus bytes, weights, runtime invocation, device timing,
  listening result, benchmark result, parity result or release claim is made.
  Rights and exact asset versions remain unresolved where the pinned records
  leave them unresolved.

## Original sources and method families

| Registry lead | Mapping in this package |
| --- | --- |
| **S16 — Pyroomacoustics classical denoising** (direct) | Spectral subtraction and Wiener filtering have mapped components and historical 30-pair pilot results. The **subspace** family has no mapped component or exact pinned source revision; see `G02` and the existing `SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS` / `SDK-SOX-NOISERED` board rows. |
| **S17 — RNNoise implementation** (search excerpt / prior inspection) | `rnnoise-v0-2` and `rnnoise-speech-probability`. Pilot ΔSI-SDR +3.139 dB and ΔSTOI +0.0215; clean-input distortion SNR median 17.32 dB. The measured RTF covers `rnnoise_process_frame` only; the local adapter is offline at 48 kHz. Gap `G03` links the existing ARM INT8 feasibility row. |
| **S18 — DeepFilterNet implementation** (direct in prior brainstorm) | `deepfilternet3-v0-5-6`. Pilot ΔSI-SDR +6.660 dB and ΔSTOI +0.0258; 743-item EARS DNSMOS values are predictions, not human MOS. The implementation row is blocked on rights; gap `G04` links the existing `SDK-DEEPFILTERGAN` feasibility row. |

Both catalogued branches are covered:

- **Classic:** spectral subtraction, Wiener filtering, subspace methods, plus
  SpeexDSP NS, WebRTC APM NS levels 0–3 and FFmpeg `afftdn`/`afwtdn` as
  conventional baselines. The historical spectral-subtraction and Wiener noise
  estimates used the whole clip and are explicitly noncausal.
- **ML:** band-gain networks (FastEnhancer Tiny/Small), complex masks and
  complex-domain filtering (DeepFilterNet3, GTCRN, CMGAN), deep filtering
  (DPFN, DPCRN, DTLN) and neural restoration/generative postfilters.
  Larger FastEnhancer checkpoints and TFLite/LiteRT paths remain feasibility
  gaps with existing board links.

## Comparison inputs, controls and outcomes

- **Paired synthetic (historical local):** 30 DNS2020 no-reverb pairs with
  identity/noisy-input, clean references, classical baselines, conventional
  baselines and neural candidates. Documented paired ΔSI-SDR values include
  spectral subtraction +1.3068 dB, Wiener +0.4269 dB, SpeexDSP +1.0608 dB,
  RNNoise +3.1387 dB, DeepFilterNet3 +6.6596 dB, FastEnhancer Small +8.1120 dB
  and FFmpeg `afwtdn` −2.2115 dB. These are engineering-screen values, not a
  frozen benchmark or qualification.
- **Clean-preservation diagnostic (historical local):** the same 30 clean
  references passed through each candidate as if noisy. Median clean distortion
  SNR: Wiener 50.58 dB, spectral subtraction 38.42 dB, FastEnhancer Small
  38.53 dB, FFmpeg `afftdn` −2.95 dB. No blinded listening follows.
- **Unpaired predictive screen (historical local):** 743 EARS inputs with saved
  enhancer outputs scored by DNSMOS P.835 predictions. DeepFilterNet3 predicted
  SIG −0.063 and OVL +0.386 relative to input; these are predictions on
  CC BY-NC research audio, not human ratings or rights clearance.
- **Strength sweep (historical local):** WebRTC APM NS levels 0–3 showed
  increasingly negative mean ΔSTOI (−0.0056 to −0.0466) on this cohort.
- **Prepared only:** a VCTK v3 +5 dB pink-noise listening comparison was
  prepared but is not a collected rating and is not imported here.
- **Source-reported only:** vendor denoiser claims and batch RTF/worker-wall
  figures are provenance. Concurrent worker timing is not callback scheduling,
  target-device availability or a benchmark result.

All values and caveats are transcribed from the pinned documents and anchored
by `reference.py`; none was recomputed or pooled for this survey. Full per-row
metadata, component census, asset classes and evidence-class separation are in
`report.json`.

## Actionable gaps and existing board links

Each gap is mapped to an **existing** board task. No new task was filed by this
survey and no task id was invented. Where no feasibility row exists, the report
says so and names the existing research-control or foundation owner instead.

| Gap | Existing board follow-up(s) | Mode |
| --- | --- | --- |
| `G01` causal noise estimation for spectral/Wiener | `SDK-SOX-NOISERED` | feasibility |
| `G02` S16 subspace family with pinned source and controls | `SDK-PYROOMACOUSTICS-CANDIDATE-TOOLS`, `SDK-SOX-NOISERED` | feasibility |
| `G03` frame-causal 16 kHz / quantized RNNoise path | `SDK-RNNOISE-INT8-ARM-ML-MODEL-ZOO` | feasibility |
| `G04` DeepFilterNet rights and successor variants | `SDK-DEEPFILTERGAN` | feasibility |
| `G05` exact FastEnhancer Base/Medium/Large checkpoints | `SDK-FASTENHANCER-BASE-REFERENCE`, `SDK-FASTENHANCER-MEDIUM-REFERENCE`, `SDK-FASTENHANCER-LARGE-REFERENCE` | feasibility |
| `G06` complex-mask / TFLite streaming runtime | `SDK-CMGAN-LITERT-COMMUNITY-PORT`, `SDK-DPCRN-DNS3-TFLITE` | feasibility |
| `G07` neural restoration / diffusion family | `SDK-SPEECHBRAIN-SGMSE-VOICEBANK`, `SDK-SNR-ALIGNED-CONSISTENT-DIFFUSION-DIFFSE` | feasibility |
| `G08` competing speech vs additive-noise split | `SDK-CONV-TASNET`, `SDK-TARGET-SPEAKER-EXTRACTION-FAMILY` | feasibility (boundary with `SPK-01/02`) |
| `G09` rights-qualified cohorts and preservation screen | `SDK-VCTK-DNS2020-AMI-EARS-AND-SMARD-EVIDENCE-MANIFESTS`, `SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS` | research-control; no feasibility task found |
| `G10` target-device timing, memory, deadlines | `SDK-FND-TIMING`, `SDK-FND-EVIDENCE` | foundation; no feasibility task found |

Board **status** is deliberately excluded from the gated projection because it
is mutable; exact `id`, `title` and `mode` of the linked rows are pinned by
`report.json:board_link_projection_sha256`. The mutable full-file board hash is
deliberately excluded from every deterministic artifact so regeneration remains
byte-identical after board status edits.

## Release boundary

Keep paired clean-reference results, paired input-similarity diagnostics,
no-reference predictions, synthetic controls, prepared listening, actual human
judgments and vendor/source claims separate. Freeze comparison geometry,
candidate revision/settings, code/model hashes, cohort rights, outcomes and
denominators before any qualification run. Retain adverse and incomplete
results. Scoped research use does not authorize redistribution, listener
exposure or public playback. Historical CPU/wall/RTF is not end-to-end
availability. No routing default or release change follows from this map.
All eight release gates in `report.json` are `blocked=true`.

## Files

- `reference.py` — stdlib-only deterministic map builder, strict JSON parser,
  pin/anchor/taxonomy/board checks and atomic state holder.
- `run.py` — byte-identical regeneration of `report.json`,
  `report.json.sha256`, `contract.json` and `SOURCES.sha256`.
- `verify.py` — read-only strict verifier for pins, canonical bytes, digests,
  licensing, scope, disposition, links and git scope.
- `test_reference.py` — unittest suite including adverse, missing, invalid and
  nonfinite rejection with unchanged state.
- `report.json` / `report.json.sha256` — canonical evidence map and digest.
- `contract.json` / `SOURCES.sha256` — exact local and external pins; the
  generated JSON artifacts have SPDX `.license` sidecars.

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
/Users/htsakanyan/.local/bin/reuse lint
git diff --check
```

`verify.py` fails closed on changed or missing pins, duplicate/nonfinite JSON,
non-canonical bytes, a wrong report digest, a license gap, a non-`DEFER`
disposition, an unblocked gate, an invented board link or an out-of-scope git
change. Three fresh-process regenerations must be byte-identical.
