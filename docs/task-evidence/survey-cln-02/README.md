<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-02 — transient interference and click repair evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-02` (Transient interference and click repair, legacy family `F08`). It
matches the original method families, both named source leads (`S17`, `S19`)
and historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-02`; independent reviewer:
`reviewer-SURVEY-CLN-02`. Claim base: audio-sdk
`c9296ae96a2b58efae559bd22e7760122c886df8`; branch
`swarm/SDK-SURVEY-CLN-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: transient detection, interpolation, gating | `median-residual-click-gate` (partial): 7-sample median residual on 12 synthetic EARS clips, 180/180 one-sample impulses at threshold 0.35 with zero false positives, repaired mean SI-SDR 51.52 dB versus 8.19 dB identity; `linear-interpolation-plc`, `linear-interpolation-declipping`, `band-limited-pocs-declipping`, PLC controls | Generated pulses and supplied masks only; no natural keyboard recordings, blind detection or consonant-overlap result |
| Classic: sparse constrained restoration | `spade-and-social-sparsity-declipping` (considered), `c-omp-declipping` (blocked), `matlab-ltfat-cvx-sparse-declipping-tools` (blocked external adapter) | No local sparse-tool execution; feasibility scoping only |
| Classic: FFmpeg conventional filters (`S19`) | `ffmpeg-afwtdn`, `ffmpeg-afftdn` evaluated for noise suppression with negative quality in the tested configuration | No pinned filter revision or click-specific invocation; direct documentation scope only |
| ML: transient-aware suppression/restoration | `transient-aware-phase-vocoder` (considered), `phase-vocoder-with-neural-transient-preservation` (blocked) | Time-scale modification preservation context, not a click-removal capability |
| ML: generative / codec-aware PLC | `complex-bin2bin-generative-plc`, `opus-deep-plc`, `lyra-ii-v2-codec-plc` (all blocked or considered) | No local execution, weights or rights-cleared asset found |
| ML: RNNoise (`S17`) | `rnnoise-v0-2`, `rnnoise-speech-probability`; noise-suppression pilot mean ΔSI-SDR +3.14 dB, ΔSTOI +0.0215, process-frame RTF 0.0662 | Search-excerpt source scope; offline 48 kHz adapter; no click-specific or native frame-causal path |

`report.json` holds the full records: both catalogued branches, source-lead
mappings, component census checked against `INVENTORY.json`, comparison inputs,
controls, assets, local versus reported outcomes, acceptance mapping, gaps,
board links and all eight blocked release gates. Historical numbers are
transcribed verbatim from pinned reports with their original scope; they are
**not** rerun, pooled into a benchmark or promoted to a pass.

## Evidence classes and failure envelope

- **Historical local paired synthetic:** one-sample click gate, width/amplitude
  stress sweep, hard-clipping/POCS screen, and supplied-mask PLC screen. Every
  historical row names the censused component it exercised.
- **Historical local adjacent context:** RNNoise noise-suppression pilot and
  realtime candidate summary; not a click cohort.
- **Source-reported only:** RNNoise project lead and FFmpeg filter documentation.
- **Not present:** natural acoustic keyboard events, human ratings, paired
  real-click cohort, target-device timing, weights, or a new execution. No
  clean-preservation diagnostic (clean speech passed through a candidate) and
  no unpaired predictive score were found, so both evidence classes are
  recorded as `false` instead of being inherited from the adjacent
  noise-suppression survey.
- The fixed detector's own stress screen is an adverse result: 0% recall at
  amplitude 0.20 and at five-sample pulses, despite clean recall for louder
  1–3 sample events. Breaths, fillers and stutters are explicitly separate
  target definitions, not disposable clicks.

## Bounded gaps and feasibility links

Eleven gaps are recorded. Gaps with no component owner (`G01`, `G04`, `G05`,
`G06`, `G11`) link **existing** feasibility rows for transient handling, sparse
declipping, generative PLC, RNNoise runtime and disfluency policy. Those links
are scoping leads only: no processor is enabled, no capability is implemented,
and no missing result is promoted. Other gaps link existing research-control or
foundation rows for frozen masks, rights, listening, timing and provider
intake. Board status is excluded from all gates; only linked `id`/`title`/
`mode` are projected to a stable digest.

## Release boundary

Keep acoustic keyboard noise and corrupted digital samples separate; preserve
speech consonants; keep paired synthetic, adjacent noise-suppression,
source-reported and prepared-listening results distinct. No public
benchmark/quality/device/listening/release claim is made. No assets, real
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
cd docs/task-evidence/survey-cln-02
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
