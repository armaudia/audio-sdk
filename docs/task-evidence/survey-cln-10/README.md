<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-10 — tonal correction and interference-filtering evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-10` (Tonal correction and interference filtering, legacy family `F08`). It
matches the catalogued method families, the named source leads (`S19`, `S46`)
and historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-10`; independent reviewer not dispatched.
Claim base: audio-sdk `d5b11912cd09e87296cd9d4654f1917c9cb94258`; branch
`swarm/SDK-SURVEY-CLN-10`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to claim

The catalogued boundary is explicit: frequency-response correction must stay
separate from generating absent bandwidth, and boosts or filtering can alter
speech. This map therefore covers high-pass rumble/DC control, narrow notch
hum removal, fixed biquad/FIR spectral equalization and learned or neural
inverse-EQ correction. It does **not** treat broadband noise suppression
(`CLN-01`), transient/click repair (`CLN-02`), wind handling (`CLN-03`),
level/loudness/dynamics (`CLN-09`), feedback notches (`CLN-11`), bandwidth
extension (`RST-02`) or codec-artifact restoration (`RST-03`) as CLN-10
results. Those rows are named only as boundaries; their measurements are not
pooled here.

The adaptive feedback-notch components deliberately stay out of the method
families: an adaptive notch inside a howling loop is `CLN-11`, even though it
uses biquad notch code. The Speex preprocessor, noise-aware shaping plus DRC,
µ-law low-pass postfilter and spectrum-copy bandwidth extension appear only in
the component census as adjacent boundaries.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: high-pass filtering for rumble, mains-adjacent low frequency and unwanted DC | `sdk-high-pass-80-hz` (integrated): installed `dsp.highpass80.v0` at fixed 16 kHz; 25 scenarios, 128/128 checks, 0.062575 gain at 20 Hz, 24.0988 dB rumble attenuation, 1.94e-15 DC rejection, zero content delay; `native-variable-cutoff-high-pass` (source-local, unbenchmarked here) | No alternate cutoff, real rumble, real speech, corpus, listening or device loop; the installed provider is fixed at 80 Hz |
| Classic: narrow-band notch and biquad tone removal for mains hum | `narrow-biquad-notch` (partial): task-local RBJ notch, 78-frequency sweep, 0.006 dB maximum sweep error, 0.00462 center gain at 1 kHz/100 Hz bandwidth, 0.999763 synthetic envelope correlation | Optional unregistered provider; no 50/60 Hz hum tracking, real hum, listening or device result |
| Classic: biquad/FIR spectral equalization and band-selective tilt or de-essing | `fixed-six-band-spectral-tilt` (evaluated): six band gains from 0.722494 to 1.584844, 0.039834 maximum probe error, energy-matched and +1 dB confound controls, 4 unity-peak exceedances; `de-esser` (considered): synthetic split-band high-band attenuation 5.398 dB versus 0.094 dB low-band, exact synthetic identity only | Device/room coloration, a desired-response target and natural spectral balance are **not** established; receiver-side band energy and fast/slow envelope values are not intelligibility or listening scores |
| ML: learned static inverse-EQ from labelled perturbations (`S46`) | `learned-inverse-eq` (evaluated): frozen six-band reference, clean synthetic SNR 55.66 dB, 4.3e-4 maximum error, plus a non-qualifying 8.83 dB out-of-band amplification control | Frozen synthetic replay only; no learned weights, real device response, speaker split or speech-quality result |
| ML: neural parametric EQ with differentiable biquads (`S46`) | `differentiable-biquad-neural-parametric-eq` (considered) | Repository candidate row only; no source, checkpoint, runtime, licence or execution |
| ML: self-supervised neural multiband EQ and dynamics (`S46`, adjacent `CLN-09`) | `self-supervised-neural-multiband-eq-and-dynamics` (considered) | Catalogued only; the dynamics half is a `CLN-09` boundary and is never pooled with tone correction |

`report.json` holds the full records: both catalogued branches, the `S19`/`S46`
source-lead mapping, the component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Installed 80 Hz high-pass control | `sdk-high-pass-80-hz` | Synthetic tones, chirp, steps, DC, silence, impulse and a rumble proxy; no real speech |
| `HE-2` | RBJ narrow notch frequency grid | `narrow-biquad-notch` | 78 frequencies, 16 conditions, 12 adverse configs; no hum tracking |
| `HE-3` | Six-band spectral tilt with masking controls | `fixed-six-band-spectral-tilt` | 11 probes, receiver-side band energy, near-clip and tanh cascade; not listening |
| `HE-4` | Frozen six-band inverse-EQ reference | `learned-inverse-eq` | Synthetic clean/perturbed/step/impulse/clipped replay; unregistered adapter |
| `HE-5` | Split-band de-esser with broadband control | `de-esser` | Sibilance bursts/sweeps, mixed noise, near-clip; exact synthetic identity only |
| `HE-6` | Historical synthetic ridge inverse-EQ screen | `learned-inverse-eq` | 240 one-second synthetic clips, 180/60 split, 4.414 dB identity vs 2.577 dB learned RMSE |

Comparison inputs separate analytic filter fixtures, synthetic equalization and
inverse-EQ fixtures, the historical synthetic held-out screen, a missing
rights-qualified real-speech/device cohort, and source-only FFmpeg and ICASSP
SSI documentation. The 60-clip synthetic held-out split is **not** an
independent benchmark; no real speaker, session, device or room is represented.
Every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local paired synthetic:** the installed high-pass, RBJ notch,
  six-band tilt, frozen inverse EQ and de-esser. These prove deterministic
  behavior and response accuracy on seeded fixtures, not perception.
- **Historical local synthetic holdout:** the 180/60 ridge inverse-EQ screen.
  Synthetic only; content, room and speaker variation were not represented.
- **Source-reported only:** FFmpeg filter documentation, ICASSP 2024 SSI
  findings, DAFx neural-EQ paper leads and the candidate catalogue's
  "code exists locally, no dedicated benchmark" finding.
- **Not present:** rights-qualified real speech, calibrated device/room
  response, mains-hum tracking, human listening or naturalness, neural weights,
  target-device timing, public default or release approval.

The failure envelope is explicit: the tilt exceeds unity peak four times
(maximum 1.526155) and its tanh cascade ends at -1.64 dB headroom; the inverse
EQ amplifies ill-conditioned out-of-band noise by 8.83 dB; and the de-esser's
12 dB makeup test drives 20 samples above full scale. These are cautions, not a
family verdict.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with an existing feasibility owner (`G03`,
`G04`, `G05`, `G06`) link existing differentiable-biquad, self-supervised EQ and
de-esser rows. Gaps without a component owner (`G01`, `G02`, `G07`, `G08`,
`G09`, `G10`, `G11`) link existing research-control or foundation rows and
carry a `no dedicated CLN-10 ...` owner note. Those links are scoping leads
only: no processor is enabled, no capability is implemented, and no missing
result is promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep tonal correction separate from noise suppression, transient repair, wind
handling, level/dynamics, feedback control, bandwidth extension and codec
restoration. Keep response accuracy separate from speech preservation, and keep
synthetic, synthetic-held-out, source-reported and missing results distinct. No
public benchmark, quality, device, listening or release claim is made. No
assets, real audio, weights, provider enablement, default, ABI, build or CI
change is included. All files are inside this task directory; board, handoff
and reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-10
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `90c1b2472e8547d3ff78d67d6d0db60b912be5befd6ef4fa4e289cf406642bd5`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
