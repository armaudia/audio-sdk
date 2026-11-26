<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SURVEY-CLN-06 — residual echo suppression evidence map

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **taxonomy and comparison map** for inventory category
`CLN-06` (Residual echo suppression, legacy family `F04`). It matches the
catalogued method families, the named source lead (`S23`) and historical local
or source-reported executions to existing components. It creates **no new
execution, model, corpus, provider, processor, ABI, default, build, CI, board,
handoff or release change**.

Survey owner: `agent-SURVEY-CLN-06`; independent reviewer not dispatched.
Claim base: audio-sdk `6f58f3d721908806f8c4a0a1e0dc6de846cef54c`; branch
`swarm/SDK-SURVEY-CLN-06`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is `Category evidence map and bounded gap
handoff`. The category remains `discovered_extension` / `catalogued` with
candidate census and benchmark both `not_started`.

## What this map covers and what it refuses to claim

The catalogued scope is residual echo **after cancellation**, not acoustic echo
cancellation itself. `CLN-05` (reference-based AEC) is a different catalogued
category; `CLN-01` (background noise suppression) and `CLN-02` (transient click
repair) are also separate. Those rows are named only as boundaries. Their
results are not pooled into a CLN-06 claim.

Cancellation and attenuation are kept distinct. A suppressor may lower residual
echo while damaging near-end speech during double talk, so attenuation without a
preservation control is recorded as partial, never as a pass. The blind
one-input route has no far-end reference and is never labeled reference AEC.
Non-echo-aware broadband noise suppression after an AEC is an adjacent control,
not residual echo suppression.

No residual-specific candidate, mask, checkpoint, cohort, tuned configuration or
runtime is staged. The only component-specific local execution is the optional
SpeexDSP MDF residual postfilter, which stayed default OFF because near-end
preservation against MDF alone was not recovered.

## Method families and mapped evidence

| Catalogued family | Mapped components and historical evidence | Boundary |
| --- | --- | --- |
| Classic: echo-aware spectral attenuation and nonlinear postfiltering bound to canceller state | `speex-mdf-residual-postfilter` (evaluated): frozen paired synthetic oracle, 5 conditions × 2 variants × 3 repeats; converged far-end ERLE 15.675997 dB (MDF only) versus 15.590018 dB (postfilter); 20 ms overlap near ratio 0.968517 → 0.687357. `speexdsp-mdf-reference` (evaluated): merged MDF reference with residual-echo disclosure | Synthetic only; overlap ratio includes residual echo; no real speech, double-talk quality, listening or device timing; postfilter optional, default OFF, unregistered |
| Classic: post-AEC broadband noise suppression as an adjacent attenuation control | `webrtc-aec3`, `webrtc-aec3-plus-apm-ns-levels-1-3` (evaluated): 12 synthetic scenarios and 12 recorded training device groups; predicted AECMOS echo 4.06 → 4.51 and degradation 2.51 → 2.38 at NS3 | APM NS is not echo-aware; adjacent control only; predicted scores are not human ratings |
| Classic: blind one-input decaying-tail suppression without far-end reference | `native-blind-residual-echo-suppression` (native-local, audio-pro): source exists, no local SDK execution, identity comparison, cohort or rights clearance | Must not be relabeled reference AEC; independent comparison absent |
| ML: neural residual echo suppression with an explicit paired reference | `dual-branch-residual-echo-suppressor`, `cagcrn-joint-aec-and-ns`, `neural-kalman-filtering-nkf` (all considered) | No exact code, checkpoint, revision, runtime or per-weight rights verified locally |
| ML: end-to-end or jointly trained neural AEC with internal echo-aware postfilters | `localvqe-compact-echo-only`, `localvqe-compact-full` (evaluated), `dtln-aec-128-256-512`, `deepaec`, `dual-path-echo-net` (blocked) | LocalVQE is end-to-end AEC, not a separable residual postfilter; blocked rows have no paired-reference checkpoint; upstream LocalVQE claims are not reproduced |

`report.json` holds the full records: both catalogued branches, the `S23`
source-lead mapping, component census checked against `INVENTORY.json`,
comparison inputs, controls, assets, local versus reported outcomes, acceptance
mapping, gaps, board links and all eight blocked release gates. Historical
numbers are transcribed verbatim from pinned reports with their original scope;
they are **not** rerun, pooled into a benchmark or promoted to a pass.

## Historical executions and comparison inputs

| ID | Historical execution | Component link | Original scope |
| --- | --- | --- | --- |
| `HE-1` | Optional Speex MDF residual postfilter frozen paired synthetic oracle | `speex-mdf-residual-postfilter` | 16 kHz mono 160-sample frames, 5 conditions, 2 variants, 3 repeats; synthetic only |
| `HE-2` | SpeexDSP MDF + residual suppressor on AEC Challenge synthetic train subset | `speexdsp-mdf-reference`, `speex-mdf-residual-postfilter` | 12 training-only paired scenarios; ERLE 7.22 → 7.22 dB, near-reference SNR 4.74 → −3.65 dB, RTF 401× → 307× |
| `HE-3` | Speex residual suppressor Gaussian and TTS double-talk stress | `speex-mdf-residual-postfilter` | Short seeded synthetic echo paths; Gaussian near SNR 15.28 → −2.95 dB, TTS 6.98 → −3.66 dB, ERLE nearly unchanged |
| `HE-4` | SpeexDSP MDF + residual suppression on AEC Challenge real training pilot | `speexdsp-mdf-reference`, `speex-mdf-residual-postfilter` | 12 recorded training device groups; predicted AECMOS, DT echo 3.23 / degradation 3.91, movement 3.14 / 3.86, RTF 298× |
| `HE-5` | WebRTC AEC3 with APM NS levels as adjacent post-cancellation control | `webrtc-aec3`, `webrtc-aec3-plus-apm-ns-levels-1-3` | 12 synthetic scenarios and 12 recorded groups; predicted AECMOS; not echo-aware residual suppression |

Comparison inputs add the residual-echo cohort requirement, source-reported ML
leads and the missing clean near-end double-talk reference. Every historical row
says "not rerun by this survey". The AEC Challenge subsets are training-only,
rights-unresolved and not redistributed.

## Evidence classes and failure envelope

- **Historical local paired synthetic:** the component-specific Speex postfilter
  oracle and direct stress fixtures. These prove deterministic filtering
  behavior and show near-end degradation, not a residual-echo benchmark.
- **Historical local adjacent AEC pilot:** 12 synthetic training scenarios and
  12 recorded training device groups. Adjacent context only; AECMOS is a learned
  metric.
- **Historical local adjacent non-echo-aware suppression:** WebRTC APM NS after
  AEC3. It has no echo-aware postfilter state and is never pooled with the Speex
  postfilter.
- **Source-reported only:** the `S23` API-reference search excerpt, upstream
  LocalVQE blind-set claim and ML model-card claims. No exact revision,
  checkpoint, matched cohort or numeric parity follows.
- **Not present:** a dedicated residual-echo cohort, clean near-end double-talk
  reference, human listening, target-device timing, residual-specific ML
  execution, a new benchmark or a release claim.

## Bounded gaps and feasibility links

Eight gaps are recorded. Gaps with a feasibility owner (`G04`, `G05`) link
**existing** ML feasibility rows for neural residual suppression and blocked
end-to-end AEC. Gaps without a component owner (`G01`, `G02`, `G03`, `G06`,
`G07`, `G08`) link existing research-control or foundation rows and carry a
`no dedicated CLN-06 ...` owner note. Those links are scoping leads only: no
processor is enabled, no capability is implemented, and no missing result is
promoted. Board status is excluded from all gates; only linked `id`/`title`/
`mode` are projected to a stable digest. The mutable board file is referenced
by path and **never hashed into canonical bytes**, so status edits elsewhere in
the swarm cannot change this map or break its digest.

## Release boundary

Keep cancellation, attenuation and near-end preservation separate. Keep
synthetic DSP, adjacent AEC pilots, predicted metrics, source-reported claims
and missing results distinct. No public benchmark, quality, device, listening or
release claim is made. No assets, real residual-echo audio, provider
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
cd docs/task-evidence/survey-cln-06
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Canonical `report.json` SHA-256: `b9db38650de9225a8cff7488f1e84b1a8c6062541300e758baa1f6ae58cfa1dc`.

The change is task-local documentation and stdlib tooling; no installed
package, descriptor catalog, ABI, build input or CI workflow is touched.

Workspace pins are SHA-256 values of read-only documents; a pin does not grant
rights or verify media. `AUDIOML_WORKSPACE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.
