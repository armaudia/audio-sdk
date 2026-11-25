<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-05 — reference-based acoustic echo cancellation evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-05` (Reference-based acoustic echo cancellation, legacy family `F04`). It
matches the catalogued method families, the named source leads (`S21`, `S22`)
and historical local or source-reported executions to existing components. It
creates **no new execution, model, corpus, provider, processor, ABI, default,
build, CI, board, handoff or release change**.

Survey owner: `agent-SURVEY-CLN-05`; independent reviewer:
`reviewer-SURVEY-CLN-05`. Claim base: audio-sdk
`6f58f3d721908806f8c4a0a1e0dc6de846cef54c`; branch
`swarm/SDK-SURVEY-CLN-05`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map does and does not cover

The catalogued boundary is explicit: reference timing, double talk, drift and
changing echo paths are part of the contract. A reference-based canceller needs
an **explicit playback/render sidechain**; a one-input blind suppressor,
residual echo suppressor, dereverberator or feedback/howler is a different
catalogued task and is not pooled into a CLN-05 claim.

`CLN-06` (residual echo suppression), `CLN-11` (feedback and howling control)
and `CLN-04` (dereverberation) are named only as boundaries or adjacent
controls. Their results are not pooled here. The SpeexDSP residual postfilter is
mapped only as an adjacent part of the MDF evidence and stays default OFF.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: adaptive FIR, NLMS, RLS and fixed RLS→NLMS hybrid | `nlms-aec` (evaluated): synthetic 96-tap explicit-reference fixture, 35.17 dB single-talk ERLE, 10.55 dB double-talk near SNR, zero nonfinite; `rls-aec` (partial): guarded synthetic RLS and analytic legacy nonfinite control; `fixed-rls-to-nlms-aec` (partial): synthetic 128-tap fixed handoff screen | No recorded room, corpus, drift, listening or device timing; synthetic ERLE is not a room result |
| Classic: frequency-domain partitioned-block adaptive filtering (MDF, PBFDAF/AUMDF) | `speexdsp-mdf-reference` (evaluated): vendored SpeexDSP 1.2.1 MDF with a frozen synthetic oracle; `pbfdaf-aumdf` (considered) | MDF evidence is paired synthetic; PBFDAF/AUMDF has no local implementation or long-tail room result |
| Classic: production AEC with delay estimation and optional residual attenuation | `webrtc-aec3` (evaluated): task-local AEC3-shaped synthetic shadow-filter/NLMS reference only; `speex-mdf-residual-postfilter` (evaluated) | No pinned WebRTC source, binary, runtime or weights and no parity; residual postfilter stays OFF because near-end preservation was not recovered |
| ML: neural-assisted adaptation or neural Kalman filtering (`S21`) | `neural-kalman-filtering-nkf` (considered) | Repository lead only; no source, checkpoint, weights or reference-timing contract staged |
| ML: reference-conditioned streaming neural AEC and joint AEC plus NS | `localvqe-compact-echo-only` and `localvqe-compact-full` (evaluated, historical local); `dtln-aec-128-256-512` (blocked); `cagcrn-joint-aec-and-ns`, `deepaec`, `dual-path-echo-net` (considered or blocked) | Historical LocalVQE/TTS and training-split values only; DTLN-AEC checkpoint missing; no independent dev/test, human rating or device loop |
| ML: neural residual echo suppression attached to a canceller | `dual-branch-residual-echo-suppressor` (considered) | Adjacent CLN-06 boundary; catalogued only and never pooled with cancellation |

`report.json` holds the full records: both catalogued branches, the `S21`/`S22`
source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | NLMS paired synthetic 96-tap path | `nlms-aec` | 51,200 samples, delay change, no-reference and delayed render; no real room |
| `HE-2` | Guarded RLS plus legacy nonfinite reproduction | `rls-aec` | Synthetic RLS; legacy recursion first nonfinite at sample 140,683 (8.793 s) |
| `HE-3` | Fixed RLS→NLMS hybrid synthetic screen | `fixed-rls-to-nlms-aec` | Fixed 128-tap handoff screen; one synthetic configuration |
| `HE-4` | Historical fixed-hybrid recorded training pilot | `fixed-rls-to-nlms-aec` | AEC Challenge TRAIN; Δ near SNR −17.74 dB, peaks 715.78; AECMOS predicted |
| `HE-5` | SpeexDSP MDF with optional residual postfilter | `speexdsp-mdf-reference`, `speex-mdf-residual-postfilter` | Five paired synthetic conditions; near ratio 0.968517 → 0.687357, ERLE 15.676 → 15.590 dB |
| `HE-6` | AEC3-shaped synthetic reference | `webrtc-aec3` | Synthetic paired fixture; no pinned WebRTC source, binary, runtime or weights |
| `HE-7` | AEC Challenge synthetic TRAIN pilot | LocalVQE, WebRTC, SpeexDSP | 12 scenarios, TRAIN only at revision `8f861f0f…`; no held-out data |
| `HE-8` | AEC Challenge real TRAIN pilot | LocalVQE, WebRTC, SpeexDSP, AECMOS | 12 device groups, 108 WAV; AECMOS predicted, not human |
| `HE-9` | LocalVQE compact paired TTS check | LocalVQE echo-only/full | 7.55 s TTS, five-tap path, 256-sample output delay; no room or listening |

Comparison inputs separate paired synthetic fixtures, synthetic and recorded
AEC Challenge TRAIN subsets, the frozen official protocol, AECMOS predicted
scores and a **missing** independent licensed dev/test corpus. The training-split
results are training-only and not an independent benchmark; LocalVQE upstream
blind-set and Swift-port parity claims are source-reported only. Every historical
row says "not rerun by this survey".

## Evidence classes and failure envelope

- **Historical local paired synthetic:** NLMS, guarded RLS, fixed hybrid,
  SpeexDSP MDF/postfilter and the AEC3-shaped reference. These prove
  deterministic behavior on seeded fixtures, not room performance.
- **Historical local training-split:** AEC Challenge synthetic and real TRAIN
  pilots. Training-only, partly rights-unresolved and not independent.
- **Historical local neural reference execution:** LocalVQE compact paired TTS
  check only. No upstream blind-set reproduction.
- **Predicted metric:** AECMOS v4 echo/degradation predictions. Never relabelled
  as human ratings.
- **Source-reported only:** LocalVQE upstream blind-set claim, Swift-port parity
  caveat, NKF-AEC repository lead, Speex MDF documentation, CAGCRN paper and
  DTLN-AEC upstream checkpoints.
- **Not present:** independent licensed dev/test corpus, real provider parity,
  DTLN/NKF/CAGCRN runnable checkpoints, clock-drift or device-loop timing,
  human listening, ASR, public default or release approval.

The failure envelope is explicit: the recorded fixed-hybrid pilot combines
echo attenuation with severe near-end degradation and peaks up to 715.78; full
RLS was nonfinite on all 12 near-end-only clips; the Speex residual postfilter
lowers the overlap near ratio from 0.968517 to 0.687357 without improving ERLE.
These are cautions, not a family verdict.

## Bounded gaps and feasibility links

Ten gaps are recorded. Gaps with a feasibility owner (`G03`, `G04`, `G05`,
`G06`) link **existing** DTLN-AEC, NKF, PBFDAF and end-to-end neural
feasibility rows. Gaps without a component owner (`G01`, `G02`, `G07`, `G08`,
`G09`, `G10`) link existing research-control or foundation rows and carry a
`no dedicated CLN-05 ...` owner note. Those links are scoping leads only: no
processor is enabled, no capability is implemented, and no missing result is
promoted. Board status is excluded from all gates; only linked
`id`/`title`/`mode` are projected to a stable digest. The mutable board file is
referenced by path and **never hashed into canonical bytes**, so status edits
elsewhere in the swarm cannot change this map or break its digest.

## Release boundary

Keep cancellation, residual suppression, dereverberation and feedback control
separate; keep echo attenuation and double-talk preservation separate; keep
synthetic, training-split, predicted, source-reported and missing results
distinct. No public benchmark/quality/device/listening/release claim is made. No
assets, real echo audio, weights, provider enablement, default, ABI, build or CI
change is included. All files are inside this task directory; board, handoff and
reviewers were not changed or dispatched.

## Files and reproduction

`reference.py` builds the map with strict JSON parsing and SHA-256 pins;
`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` byte-for-byte; `verify.py` recomputes all artifacts, checks
licensing and task-local git scope; `test_reference.py` checks canonical
output, adverse rejections and three cold-start repeats. JSON and manifest
files have SPDX license sidecars.

```sh
cd docs/task-evidence/survey-cln-05
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `c217ef5dff12472dc4e55fa0471cbd73897dd06df56b51ca3d5f9c07ebcdd9b9`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched. The
repository's installed-package gate `PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py` is run
from the SDK root on the exact head as a release-safety check.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
