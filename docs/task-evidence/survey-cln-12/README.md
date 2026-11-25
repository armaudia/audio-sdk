<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-12 — near-end listening / intelligibility-enhancement evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-12` (Near-end listening / intelligibility enhancement, legacy family
`F09`). It matches the catalogued method families, the named source leads
(`S54`, `S55`, `S56`) and historical local or source-reported executions to
existing components. It creates **no new execution, model, corpus, provider,
processor, ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-12`; independent reviewer:
`reviewer-SURVEY-CLN-12`. Claim base: audio-sdk
`c0be8f341cb14cf1ad7f93d4a171543b2f99a6e4`; branch
`swarm/SDK-SURVEY-CLN-12`. The category remains `discovered_extension` /
`catalogued` with candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to pool

Near-end listening enhancement (NELE) changes received speech before playback
so it is more intelligible against masking near the listener, under an output
power constraint. That is not capture-side denoising (`CLN-01`), not ordinary
gain or loudness control (`CLN-09`), not tonal correction (`CLN-10`) and not an
assessment task (`OBS-01`). Those rows are named only as boundaries and their
results are **not pooled** into a CLN-12 claim.

The local evidence is a small objective screen, synthetic receiver-side masking
and DRC controls, and a task-local STOI/ESTOI scorer cross-check. The screen
used 12 staged EARS anechoic targets and three reused VADToolkit ambient scenes.
No listener panel, listening-effort rating, hearing profile, word recognition,
independent held-out cohort or target-device playback measurement was made.
STOI/ESTOI are objective predictors, not intelligibility or listener benefit.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: spectral energy redistribution via fixed or signal-dependent tilt | `fixed-six-band-spectral-tilt` (evaluated): synthetic receiver-side masking fixture with energy-matched and level-confound controls; `optfractasii-approximation` (evaluated): broad-band local approximation in the 108-pair screen | Synthetic band-energy evidence only; no STOI/ESTOI result for the tilt fixture, no listener result and no robust screen winner |
| Classic: intelligibility-index optimization and noise-aware water-filling | `optfractasii-approximation` and `noise-aware-shaping-plus-drc` (evaluated): both underperformed identity on aggregate ESTOI in the local screen | Deliberately an approximation, not a faithful OptFractASII reproduction; small reused masker set |
| Classic: adaptive dynamic-range compression for receiver-side listening | `full-band-receive-drc-control` (evaluated): synthetic level/masker control; `feed-forward-compressor` (partial): DRC-only screen and synthetic gain-ramp control; `adaptdrc-ssdrc` (considered) | Local compressor is explicitly a small research baseline, not AdaptDRC/SSDRC; no published archive, weights or runtime |
| Classic boundary: simple gain or loudness normalization | `static-target-gain-with-peak-ceiling`, `envelope-agc`, `ebu-r128-ffmpeg-loudnorm` | Adjacent control only; not NELE and not a near-end listening benefit claim |
| ML/hybrid: family search remains open | `se-agcnet`, `self-supervised-neural-multiband-eq-and-dynamics`, `differentiable-biquad-neural-parametric-eq` (all considered) | No exact code, checkpoint, weights, training data, runtime or ML execution; catalogued leads only |

`report.json` holds the full records: both catalogued branches, the `S54`/`S55`/
`S56` source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not rerun, pooled into a benchmark or promoted to a pass**.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | CLN-12 local objective screen | fixed tilt, OptFractASII approximation, shaping+DRC, DRC alone | 12 EARS targets × 3 VADToolkit scenes × 3 SNRs = 108 pairs/method; STOI/ESTOI predictors |
| `HE-2` | Fixed six-band tilt receiver-side masking | `fixed-six-band-spectral-tilt` | Nine synthetic target/masker conditions; band energy only |
| `HE-3` | Full-band receive DRC synthetic control | `full-band-receive-drc-control` | Five levels × three TMRs; excluded from qualification |
| `HE-4` | Feed-forward DRC noisy-DNS gain ramps | `feed-forward-compressor` | 30 paired clips, −9/+9 dB blocks; engineering control |
| `HE-5` | DRC-only screen and synthetic gain-law tracking | `feed-forward-compressor` | RMSE 2.613 dB vs 5.795 identity; synthetic only |
| `HE-6` | STOI/ESTOI scorer cross-check | `stoi-estoi` | Six paired synthetic items; scorer behavior only |

Comparison inputs separate the objective screen, synthetic masking and DRC
controls, the scorer cross-check, source-reported published claims and a
**missing** rights-qualified held-out near-end listening cohort. Published
OptFractASII, AdaptDRC/SSDRC and author-software claims are source-reported only;
the author archive direct access timed out and no runnable candidate is
established. Every historical row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local objective screen:** `HE-1` only. Fixed tilt ranked first by
  aggregate mean STOI/ESTOI, but its utterance-clustered ESTOI interval versus
  identity crosses zero; DRC alone has the only interval above zero, with 12
  clusters and no listener benefit.
- **Historical local synthetic masking/DRC controls:** `HE-2`, `HE-3`, `HE-4`,
  `HE-5`. These prove deterministic control behavior on seeded fixtures, not
  near-end listening quality.
- **Historical local scorer cross-check:** `HE-6`. STOI/ESTOI behavior on
  generated signals; not evidence of speech intelligibility or benefit.
- **Source-reported only:** Villani et al. analysis, Fraunhofer AdaptDRC/SSDRC,
  the author MATLAB-archive lead and published ML claims. None is reproduced.
- **Not present:** human listening, listening effort, hearing profiles, word
  recognition, rights-qualified held-out cohort, published-method reproduction,
  ML weights/runtime/execution, target-device timing, public default or release
  approval.

The failure envelope is explicit: the local OptFractASII approximation and its
DRC extension underperformed identity on aggregate ESTOI; fixed tilt exceeds
unity peak in the synthetic masking fixture without a qualified limiter; and the
local compressor is not AdaptDRC/SSDRC. These are cautions, not a family verdict.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G04`, `G05`, `G09`) link
**existing** OptFractASII, AdaptDRC/SSDRC and learned-NELE feasibility rows.
Gaps without a dedicated category row (`G01`, `G02`, `G03`, `G06`, `G07`,
`G08`, `G10`) link existing research-control or foundation rows and carry a
`no dedicated CLN-12 ...` owner note. Those links are scoping leads only: no
processor is enabled, no capability is implemented and no missing result is
promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

No near-end listening benefit, intelligibility, MOS, benchmark, device-timing
or release claim is made. No audio, maskers, weights, provider enablement,
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
cd docs/task-evidence/survey-cln-12
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `fc9a00c7d5563cdab4a02420ca66beefbb6b40bae4e3b6244faf54f0efcaddc6`.

The change is task-local documentation and stdlib tooling; no installed package,
descriptor catalog, ABI, build input or CI workflow is touched. Workspace pins
are SHA-256 values of read-only documents; a pin does not grant rights or verify
media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing `audioml` checkout if
automatic discovery is unavailable.
