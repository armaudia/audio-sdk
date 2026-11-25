<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DEEPFILTERNET3-LOCAL-LISTENING-PRESET — task-local synthetic chain evidence

Proposal-only, incomplete and **not qualified** evidence for
`DeepFilterNet3 local listening preset`. This package is a **Pipeline-profile
proposal and ablation handoff to the recipe owner**, reconstructed from
pinned documentation with frozen deterministic synthetic signals. It is
optional, unregistered and OFF by default. No public API/ABI, `CONTRACTS.md`,
descriptor, registry, installed default, shared build or CI change is made.

No real DeepFilterNet3 runtime, checkpoint/weight access, media, listening
result, device timing, benchmark result or release claim is produced.

## Documented chain (provenance only)

Pinned sources record a 2026-10-31 owner preference for DeepFilterNet3 as a
first-choice listening candidate, with FastEnhancer Small also rated good.
That preference is not a production or default decision. The documented
comparison order is:

- `fan_hum` and `busy_room`: noisy, C++ Speex NS, FastEnhancer Small,
  DeepFilterNet3, VAD-gated C++ Speex NS (stricter 65/50 start/continue gate on
  noisy input).
- `reverberant_room`: the same five, plus C++ experimental WPE dereverberation
  and C++ Speex NS → WPE.
- Real-voice handoff adds C++ WPE → DeepFilterNet3 → C++ Speex VAD gate. The
  real-voice clip is described in the pinned manifest as one public-domain LJ
  Speech recording; **no media file was read or reused here**.

This package re-expresses that order as frozen synthetic stage surrogates:
`noisy_input → wpe_surrogate → enhancer_surrogate → vad_gate_surrogate`.
`enhancer_surrogate` represents the dated local prototype choice
`2026-11-24-local-only`; it is a bounded smoothing/shrinkage function, not a
vendor model. Stage-removed ablations (`without_wpe`, `without_enhancer`,
`without_vad_gate`) and matched controls (identity, noisy, passthrough, named
Speex surrogate) are scored on the same frozen signals. Regressions are
recorded verbatim.

## Pipeline profile application

From `plan/swarm/VERIFICATION.md`, the Pipeline profile requires stage order,
control and stage-removed ablations, failure policy, lifetime, end-to-end
clock and buffer behavior, asset scope and paced workload, with stage timing
assessed independently of end-to-end availability. All are represented in
`report.json.pipeline_profile`; measured timing, pacing and availability are
explicitly `blocked_unmeasured` / `blocked_not_run`, never inferred from the
synthetic fixture.

## Boundary

- Documented public v0 geometry only: 16 kHz, mono, `f32`, 160 samples/call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `processor_exposure=false`.
- Evaluation fixture and any future production callback paths are distinct;
  no production callback is implemented or invoked.
- Decision remains `DEFER` before processor exposure, provider intake or any
  default selection.

## Exact checkpoint, config and rights blockers

Quoted from pinned `research/noise_suppression_assets_20261027.json` and
`research/selected_audio_enhancement_candidates.md`; **no weights were
accessed or downloaded in this task**:

- Candidate: `DeepFilterNet3-0.5.6`, upstream source revision
  `978576aa8400552a4ce9730838c635aa30db5e61`.
- `data/checkouts/DeepFilterNet3/config.ini` SHA-256
  `415eb925d44990d938fb739f514aa3662c1ec0ea836cff044fa1291b82cb4290` (2,067 bytes).
- `data/checkouts/DeepFilterNet3/checkpoints/model_120.ckpt.best` SHA-256
  `23b92884f63ccf54bb026014604625ab231657b6480df65db4095c4c171e6003` (8,714,073 bytes).
- Upstream code license recorded as `MIT OR Apache-2.0`; artifact-specific
  checkpoint terms recorded as `unclear; see upstream issue #712`.
- `SDK-DEEPFILTERNET3-V0-5-6` remains **blocked**: no approved
  artifact-specific rights for the exact checkpoint/config, no pinned runtime
  and no permitted matched reference cohort. Missing rights are never
  substituted by this proposal.

## Files

`reference.py` is the deterministic generator, stage surrogates and canonical
report model. `run.py` regenerates the report, sidecar and manifest.
`test_reference.py` is the acceptance suite. `verify.py` is a read-only strict
checker. `check_licensing.py` is the independent SPDX/REUSE check.
`contract.json`, `adapter.json` and `provider.json` are task-local,
unregistered disposition manifests. `SOURCES.sha256` pins all external source,
boundary and local artifact bytes; generated JSON and the manifest use exact
`.license` sidecars.

## Reproduction

Use the pinned interpreter; all commands run from this task directory unless
noted:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-DEEPFILTERNET3-LOCAL-LISTENING-PRESET
```

`report.json` is canonical JSON (`sort_keys=True`, compact separators,
`allow_nan=False`, negative zero normalized) plus one trailing newline;
`report.json.sha256` records its exact digest. Regeneration is byte-identical
over three cold-start interpreter processes.

## Gates

All gates remain blocked pending rights-qualified checkpoint/config/runtime,
real cohorts, independent listening, target pacing/deadline, provider intake,
explicit default selection and exact approved external reference parity. The
board and handoff files are untouched; this evidence stays
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
