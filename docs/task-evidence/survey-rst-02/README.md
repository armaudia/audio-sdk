<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-RST-02 — bandwidth extension and audio super-resolution evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`RST-02` (Bandwidth extension and audio super-resolution, legacy family `F10`).
It matches the catalogued method families, both named source leads (`S29`,
`S45`) and historical local or source-reported executions to existing
components. It creates **no new execution, model, corpus, provider, processor,
ABI, default, build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-RST-02`; independent reviewer:
`reviewer-SURVEY-RST-02`. Claim base: audio-sdk
`2a475defe0d0d6ff4fed3c0044c1aa2566292552`; branch
`swarm/SDK-SURVEY-RST-02`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to conflate

Bandwidth extension (BWE) and audio super-resolution estimate **missing
high-frequency content** in band-limited speech. That is not declipping
(`RST-01`), not codec-artifact restoration (`RST-03`) and not packet-loss
concealment (`RST-04`). Resampling, interpolation and rate conversion change
the sample rate or bandwidth but **cannot infer missing high frequencies**, so
they are mapped only as an adjacent boundary and are never counted as BWE.

The local evidence is one small paired pilot: 12 staged EARS clips low-passed
at 3.5 kHz and compared against a low-band spectrum-copy proxy and the clean
full-band waveform. No neural model was run, no checkpoint or weight is staged,
no human listening was performed and no target-device timing exists.

## Original method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: envelope/excitation extension; classical code search pending (`MF-C1`) | `spectrum-copy-bandwidth-extension` (evaluated): 12-clip pilot, band-limited input 17.40 dB SI-SDR / 0.9868 STOI; low-band spectrum copy 14.39 dB / 0.9725, worse on all 12 clips; exact envelope/excitation implementation remains an open search | Only a negative classical proxy; no matched envelope/excitation implementation and no listening |
| Classic adjacent: rate conversion and resampling (`MF-C2`) | `numpy-scipy-soundfile-wav-and-resampling` (evaluated), `typed-frame-resample-and-drift-diagnostics` (source-local), `speex-resampler`, `libsamplerate`, `libsoxr` (considered) | Adjacent tooling only; changing rate or bandwidth does not recover missing high-band information |
| ML: bandwidth-conditioned generative upsampling / diffusion (`MF-M1`, `S29`) | `nu-wave-2` (considered): official code/checkpoints reported, 48 kHz output from lower input rates | Direct project access only; no pinned revision, checkpoint digest, rights review, matched cohort or local output |
| ML: codec-integrated neural band extension (`MF-M2`) | `opus-1-5-lace`, `opus-1-5-nolace` (considered): decoder-integrated LACE/NoLACE postfilters | Needs a compatible Opus build, genuine low-bitrate traffic and packet-level integration; not run |
| ML: diffusion/generative super-resolution models (`MF-M3`) | `audiosr`, `vocos-bwe`, `additional-vm-asr-audio-super-resolution` (all blocked) | No pinned source, checkpoint, adapter, candidate output or timing |
| ML: universal multi-distortion generative enhancement (`MF-M4`, `S45`) | `gap-urgenet`, `urgent-bsrnn`, `urgent-bsrnn-flow`, `tf-gridnet-urgent-2025-baseline` (blocked/considered): URGENT challenge family | Challenge-level context only; bandwidth restoration is one distortion among several and no local material is staged |
| ML adjacent: general restoration and vocoder boundary (`MF-M5`) | `voicefixer`, `hifi-gan-vocoder`, `vocos-vocoder`, `world-vocoder` (all considered) | General restoration or waveform synthesis, not a bandwidth-extension result; no weights, runtime or execution |

`report.json` holds the full records: both catalogued branches, the `S29`/`S45`
source-lead mapping, a 20-row component census checked against
`INVENTORY.json`, eight comparison inputs, eight controls, seven assets, four
historical executions, six reported outcomes, the acceptance mapping, fourteen
gaps, twenty-six linked board rows and all eight blocked release gates.
Historical numbers are transcribed verbatim from pinned reports with their
original scope; they are **not rerun, pooled into a benchmark or promoted to a
pass**.

## Comparison inputs, controls and historical executions

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | 12-clip BWE pilot at a 3.5 kHz zero-phase cutoff | `spectrum-copy-bandwidth-extension` | 16 kHz mono, at most 4 s, 2.56% high-band energy removed; means only |
| `HE-2` | Per-clip RST-02 synthetic screen ledger | `spectrum-copy-bandwidth-extension` | 24 rows (12 clips × 2 methods); provenance only |
| `HE-3` | NumPy/SciPy/SoundFile WAV and resampling tooling | `numpy-scipy-soundfile-wav-and-resampling` | 36 resampling cases, 11 bit-exact WAV roundtrips; adjacent tooling |
| `HE-4` | Typed frame / resample and drift diagnostics | `typed-frame-resample-and-drift-diagnostics` | 4 source frames, 800 produced / 495 valid, 173-sample integer delay; adjacent tooling |

Comparison inputs separate the pilot, the per-clip ledger, direct source leads,
the URGENT challenge taxonomy, blocked super-resolution candidates, adjacent
rate-conversion tooling and a **missing** rights-qualified paired
band-limited/full-band speech cohort. Every historical row says "not rerun by
this survey".

## Evidence classes and failure envelope

- **Historical local paired pilot:** `HE-1` only. The band-limited input is the
  damaged baseline; the low-band spectrum-copy proxy is a negative control that
  loses fidelity on every clip.
- **Historical local ledger:** `HE-2` records the per-clip provenance behind the
  pilot means; it was not re-scored.
- **Historical local adjacent tooling:** `HE-3`, `HE-4`. These prove
  deterministic rate-conversion, drift and rejection behavior, not bandwidth
  extension.
- **Source-reported only:** NU-Wave 2, URGENT 2026, AudioSR, Vocos-BWE,
  additional VM-ASR, Opus LACE/NoLACE, VoiceFixer and vocoder leads. None is
  reproduced, and challenge context or a project page is not a local result.
- **Not present:** neural weights, checkpoints, runtimes, codec integration,
  high-band fidelity, content-preservation scores, blind cutoff estimation,
  human listening, rights-qualified held-out cohort, target-device timing,
  public default or release approval.
- The failure envelope is explicit: the copy-spectrum baseline is rejected;
  resampling cannot recover missing high frequencies; generated bands are
  estimates and must be checked for fidelity. These cautions are not a family
  verdict and do not qualify any candidate.

## Bounded gaps and board links

Fourteen gaps are recorded. Gaps with a feasibility owner (`G01`–`G06`, `G13`)
link existing NU-Wave 2, Opus 1.5 LACE/NoLACE, AudioSR, Vocos-BWE, VM-ASR,
URGENT and VoiceFixer feasibility rows. Gaps without a dedicated category row
(`G07`–`G12`, `G14`) link existing research-control, implementation or
foundation rows and carry a `no dedicated RST-02 ...` owner note. Those links
are scoping leads only: no processor is enabled, no capability is implemented
and no missing result is promoted. Board status is excluded from all gates;
only linked `id`/`title`/`mode` are projected to a stable digest. The mutable
board file is referenced by path and **never hashed into canonical bytes**, so
status edits elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

No bandwidth-extension quality, high-band fidelity, content preservation,
intelligibility, MOS, benchmark, device-timing or release claim is made. No
audio, weights, provider enablement, default, ABI, build or CI change is
included. All files are inside this task directory; board, handoff and
reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse/missing/invalid/nonfinite rejections and three cold-start
repeats. JSON and manifest files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-rst-02
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
