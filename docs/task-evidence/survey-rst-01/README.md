<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-RST-01 — declipping and saturation-restoration evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`RST-01` (Declipping and saturation restoration, legacy family `F10`). It
matches the original method families, both named source leads (`S28`, `S31`)
and historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-RST-01`; independent reviewer:
`reviewer-SURVEY-RST-01`. Claim base: audio-sdk
`711c5c2a419edf258d6858fa90293c5900faad82`; branch
`swarm/SDK-SURVEY-RST-01`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: autoregressive / neighbour interpolation | `linear-interpolation-declipping` (evaluated): 20 complete synthetic cases, linear interpolation below the clipped-input anchor in every stratum (very low −3.96 dB, low −4.33 dB, mid −0.99 dB, high −4.34 dB, saturated −39.71 dB); `autoregressive-plc` is adjacent packet-loss evidence, not AR declipping | No AR declipping execution; exact known masks only |
| Classic: band-limited constrained reconstruction | `band-limited-pocs-declipping` (evaluated): 17 complete synthetic cases, POCS above clipped input in four strata (+2.01, +0.76, +0.04, +0.14 dB); clean and zero-occupancy controls bit-identical; 98.68% saturation control only 4.93 dB | 2048-sample offline blocks, generated stimuli, no real speech or streaming |
| Classic: sparse constrained reconstruction / SPADE | `spade-and-social-sparsity-declipping` (considered), `c-omp-declipping` (blocked), `matlab-ltfat-cvx-sparse-declipping-tools` (blocked external adapter) | No local sparse-tool execution; the S28 toolbox needs MATLAB/LTFAT/CVX |
| Classic: level control boundary | `peak-limiter-reference`, `static-target-gain-with-peak-ceiling` | Limiting prevents overload but cannot reconstruct clipped peaks; these are controls, not declippers |
| ML: neural restoration and resynthesis (`S31`) | `voicefixer` (considered) | Search-excerpt source lead; no pinned source, checkpoint, rights review or local output |
| ML: unified multi-distortion restoration | `ccf-aatc-unified-restoration-controls` (considered) | Registration-gated challenge material; no local data, split or score |

`report.json` holds the full records: both catalogued branches, both source
leads, component census checked against `INVENTORY.json`, comparison inputs,
controls, assets, local-pilot versus source-reported outcomes, acceptance
mapping, eleven gaps, fourteen linked board rows and all eight blocked release
gates. Historical numbers are transcribed verbatim from pinned reports with
their original scope; they are **not** rerun, pooled into a benchmark or
promoted to a pass.

## Evidence classes and failure envelope

- **Historical local paired synthetic:** the POCS and linear-interpolation
  packages use frozen 2048-sample stimuli, exact derived masks, damaged-input
  anchors and clean references. Every historical row names the censused
  component it exercised.
- **Historical local pilot, not reproduced:** the 12-clip EARS hard-clipping
  means are transcribed from `research/distortion_restoration_20261028.md`
  (POCS 15.05 dB at threshold 0.35 and 23.32 dB at 0.55; linear interpolation
  10.99 dB; clipped input 14.79 dB). The report itself calls them small pilot
  effects with modest 2.74%/0.55% occupancy and no human evaluation.
- **Clean transparency:** identity, zero-occupancy clipped input and
  zero-occupancy reconstruction are bit-identical to their clean sources in
  both local packages. Broadband clean input is not unconditionally
  transparent because the band-limit is destructive by design.
- **Adverse:** nonfinite input is an explicit adverse result with no
  serialized output and no score. Linear interpolation's fully saturated and
  minimal-anchor cases are controls showing heavy information loss (−34.51 dB
  and −63.52 dB), not successes.
- **Source-reported only:** the S28 author toolbox, S31 VoiceFixer and the CCF
  AATC challenge. No local runtime, exact revision, matched cohort or numeric
  parity follows from a claim.
- **Not present:** human ratings, rights-qualified paired clipped speech,
  blind clipping detection, soft-saturation modelling, target-device timing,
  weights, or a new execution. Prepared VCTK listening items exist with zero
  collected ratings, so that class is recorded `true` while
  `human_listening_result` stays `false`.
- The category boundary is explicit: limiting prevents overload but does not
  reconstruct lost samples; evaluate speech fidelity, not only smoothness.
  Peak limiting is therefore a control, never a declipping surrogate.

## Bounded gaps and board links

Eleven gaps are recorded. `G04` (sparse/SPADE/C-OMP) and `G06` (VoiceFixer)
link existing feasibility rows. Every other gap has no component owner and
links existing research-control, foundation or implementation rows for
blind detection, AR declipping, real-speech scope, saturation separation,
unified-restoration material, cohort manifests, listening, device timing and
provider intake. Those links are scoping leads only: no processor is enabled,
no capability is implemented, and no missing result is promoted. Board status
is excluded from all gates; only linked `id`/`title`/`mode` are projected to a
stable digest. The board file is referenced by path and never hashed into
canonical bytes, so status edits elsewhere in the swarm cannot change this map
or break its digest.

## Release boundary

Keep hard clipping, soft saturation/overload and level limiting as separate
subcases; preserve speech fidelity and avoid rewarding smoothness. Keep
generated fixtures, the historical pilot, adjacent level-control DSP and
source-reported model claims distinct. No public benchmark, quality, device,
listening or release claim is made. No assets, real audio, weights, provider
enablement, default, ABI, build or CI change is included. All files are inside
this task directory; board, handoff and reviewers were not changed or
dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rst-01
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
git diff --check
```

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched.
Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
