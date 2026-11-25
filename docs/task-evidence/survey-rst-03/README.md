<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-RST-03 — codec-artifact restoration evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`RST-03` (Codec-artifact restoration, legacy family `F10`). It matches the
catalogued classic and ML method families, both named source leads (`S30`,
`S45`) and historical local or source-reported executions to existing
components. It creates **no new execution, model, codec run, corpus, provider,
processor, ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-RST-03`; independent reviewer not dispatched.
Claim base: audio-sdk
`2a475defe0d0d6ff4fed3c0044c1aa2566292552`; branch
`swarm/SDK-SURVEY-RST-03`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: decoder postfilters and noise shaping | `law-codec-proxy-and-low-pass-postfilter` (evaluated): 12-clip µ-law pilot, 8-bit at 8 kHz and a non-standard 4-bit stress proxy. Decoded-input SI-SDR 37.99 dB (8-bit) and 16.43 dB (4-bit); the fixed low-pass postfilter falls to 33.12 dB on 8-bit (−4.87 dB) and rises only 0.28 dB on 4-bit with effectively unchanged STOI (0.8751 → 0.8749) | One generic low-pass on companded PCM; no noise shaping, deemphasis, decoder state or real transform codec |
| Classic: adjacent decoder/redundancy and residual-postfilter boundary | `opus-1-4-standard-decoder-plc` (evaluated, RST-04), `opus-dred` (considered), `opus-packetization-fec-dtx-and-comfort-noise` (considered), `speex-mdf-residual-postfilter` (evaluated, AEC) | Packet-loss concealment and AEC residual suppression are adjacent inverse problems, not codec-artifact restoration |
| ML: codec-integrated neural postfilters (`S30`) | `opus-1-5-lace` and `opus-1-5-nolace` (considered): documented as decoder-integrated neural postfilters in Opus 1.5, not enabled by default | No compatible build, decoder feature stream, exact flag, checkpoint or local output exists |
| ML: codec-latent neural enhancement | `se-nac-codec-latent-enhancement-family` (considered): census record with released variants and checkpoints | Census metadata only; no weight, license, task data or local inference |
| ML: universal multi-distortion baselines (`S45`) | `urgent-bsrnn` (blocked), `urgent-bsrnn-flow` and `tf-gridnet-urgent-2025-baseline` (considered) | Challenge baselines for general enhancement; no codec-stratified run, registered data or score |
| ML: adjacent neural concealment and codec I/O | `opus-deep-plc`, `lyra-ii-v2-codec-plc` (blocked/considered), `torchaudio-torchcodec-and-soundfile-compatibility-for-llvc` (partial) | RST-04 and tool scope; no post-decode artifact result |

`report.json` holds the full records: both catalogued branches, both source
leads, component census checked against `INVENTORY.json`, comparison inputs,
controls, assets, local-pilot versus source-reported outcomes, acceptance
mapping, eleven gaps, eighteen linked board rows and all eight blocked release
gates. Historical numbers are transcribed verbatim from pinned reports with
their original scope; they are **not** rerun, pooled into a benchmark or
promoted to a pass.

## Evidence classes and failure envelope

- **Historical local paired synthetic/pilot:** the 12-clip µ-law package uses
  frozen deterministic corruptions from the EARS subset, a pre-companding
  narrowband reference and a decoded-input baseline. The 48 codec rows are
  provenance only; bytes were not staged or rerun by this survey.
- **Clean/reference identity:** the decoded input is the task-matched damaged
  baseline at both bit depths. It is never described as a restored or enhanced
  output. The 4-bit condition is explicitly a stress proxy, not a standard
  codec.
- **Classic postfilter outcome:** the fixed low-pass harms the standard 8-bit
  condition by 4.87 dB SI-SDR and gains only 0.28 dB on the 4-bit proxy while
  STOI is marginally lower. That is a small pilot effect, not a method
  recommendation.
- **Adjacent evidence kept separate:** the Opus 1.4 PLC screen belongs to
  RST-04 (2.39 dB isolated / 0.92 dB burst SI-SDR against same-codec controls);
  the Speex MDF residual postfilter belongs to the room profile (near ratio
  0.968517 → 0.687357). Neither is codec-artifact restoration.
- **Source-reported only:** Opus 1.5 LACE/NoLACE, SE-NAC and the URGENT 2026
  baselines. A documented claim is not a local runtime, exact revision,
  checkpoint, matched cohort or numeric parity.
- **Not present:** real MP3/AAC/Opus transform coding, tandem coding, jitter,
  packet traces, human ratings, rights-qualified paired decoded speech,
  target-device timing or a new execution. Prepared VCTK listening items exist
  with zero collected ratings, so that class is recorded `true` while
  `human_listening_result` stays `false`.
- The category boundary is explicit: a codec-integrated method may require
  information unavailable to a generic PCM filter. Generic postfiltering is a
  control, never a codec-artifact surrogate.

## Bounded gaps and board links

Eleven gaps are recorded. `G01` (Opus LACE/NoLACE), `G04` (SE-NAC), `G05`
(URGENT baselines) and `G06` (PLC/DRED/Lyra separation) link existing
feasibility rows. Every other gap has no component owner and links existing
research-control, foundation or implementation rows for real codec coverage,
classic noise shaping, cohort manifests, listening, timing, provider intake
and codec I/O compatibility. Those links are scoping leads only: no processor
is enabled, no capability is implemented, and no missing result is promoted.
Board status is excluded from all gates; only linked `id`/`title`/`mode` are
projected to a stable digest. The board file is referenced by path and never
hashed into canonical bytes, so status edits elsewhere in the swarm cannot
change this map or break its digest.

## Release boundary

Keep decoder postfilters, codec-integrated neural postfilters, codec-latent
enhancement, universal enhancement baselines and packet-loss concealment as
distinct subcases. Keep the µ-law proxy separate from real transport codecs;
keep the adjacent AEC and RST-04 results separate. No public benchmark,
quality, device, listening or release claim is made. No assets, real audio,
codecs, weights, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and
reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rst-03
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
