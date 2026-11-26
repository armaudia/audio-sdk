<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FULLSUBNET-ORIGINAL — FullSubNet original readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the
FullSubNet original feasibility row. It is **not** a FullSubNet
implementation. No upstream source checkout, pretrained checkpoint, config,
training statistic, runtime, corpus, noisy/clean pair, enhanced waveform,
listening result, device measurement, benchmark or release claim is present.
**No result here qualifies FullSubNet original.**

The structured inventory marks `fullsubnet-original` as `evidence_status=blocked`
with the **Enhancement** acceptance profile (`verification_profile:
enhancement`, `plan/INVENTORY.json`). The row asks for runnable source, exact
assets, permitted scope, task geometry and matched evidence before a
caller-supplied-asset reference and an opt-in adapter; none of those
prerequisites exists locally.

## Exact external blocker

The exact **source**, **official v0.2 checkpoint/weights bundle** and
**Linux/CUDA/GPU runtime** are all absent.

The pinned census describes FullSubNet original as *"Full-band/sub-band
recurrent fusion; single-channel real-time design"* and records *"Official MIT
repo and v0.2 release checkpoints with reported WB/NB-PESQ, SI-SDR and STOI"*
under the action *"Pin/hash checkpoint; validate dependencies, CPU and
latency."* The pinned selected-candidate record adds that the official setup
*"calls for Linux/CUDA/GPU and does not support CPU"*, that a project issue
reports an extreme CPU memory allocation, and that the checkpoint's separate
terms and hash still need review; it defers the candidate *"until a suitable
GPU worker is available."* Those are source-reported context only. The
upstream-reported no-reverb STOI `0.964` and SI-SDR `17.635` are not local
measurements and are not admitted as results.

Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count, parameter count or SHA-256 is asserted as
verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `Audio-WestlakeU/FullSubNet` at an immutable 40-hex commit, with the reviewed MIT license text, a per-file SHA-256 manifest from a reviewable tree, and a recorded provenance decision for the v0.2 release |
| Checkpoint bundle | The caller-selected official v0.2 checkpoint at an immutable identity, including every weight, inference config, training statistic, model card and terms file, with byte count and SHA-256 per file |
| Runtime | A locked, reproducible Linux/CUDA/GPU runtime with exact interpreter and `torch`/`torchaudio` versions, a driver and device profile, a lock SHA-256, an offline load path and a recorded host profile |
| Rights | Reviewed MIT code license, separate weight and model-card terms, training-data provenance, corpus rights, clean-reference permission, output use and redistribution |
| Cohort | A frozen, rights-cleared paired 16 kHz mono noisy/clean cohort with exact durations, language and speaker groups, held-out splits, and identity/noisy, task-matched-baseline, clean-preservation, peak/invalid and unpaired controls |
| Enhancement results | Independent paired SI-SDR and STOI, clean-speech preservation, peaks and invalid (including nonfinite) outputs, authorized listening or a labeled predictive screen, alignment, content delay, state, memory, availability timing, resources and uncertainty on the exact target runtime |

The machine-readable record is `report.json` → `source_probe`, `weights_probe`,
`runtime_probe`, `absence_evidence`, `required_artifacts`, `exact_blockers`,
`enhancement_profile` and `gates`. `contract.json` carries the same
disposition, pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** The candidate matrix, the selected-candidate record, the
   noise-suppression candidate census, the inventory, the SDK plan and the
   verification profile are pinned by SHA-256. These are read-only provenance
   inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local Enhancement cohort manifest
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted entries, unresolved
   tokens, non-integral or out-of-range integers, unsupported sample rates
   (including 48 kHz and 44.1 kHz), non-offline runtimes, unconsented pairs and
   false rights are rejected. One synthetic structural control is accepted to
   prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control` and `qualifies=false`.
5. **Enhancement profile accounting.** Identity/noisy control, task-matched
   baseline, paired SI-SDR and STOI, clean-speech preservation, peaks and
   invalid outputs, authorized listening, alignment, content delay, state,
   memory, availability timing and the independent rights gates are each
   recorded as **blocked**.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No FullSubNet provider is installed or
   registered; no descriptor, default, ABI, shared build, CI, board or handoff
   change is made.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control and established task-matched baseline | blocked | No control or baseline output exists on the exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared paired cohort and no score. |
| Clean-speech preservation | blocked | No clean-input preservation measurement. |
| Peaks and invalid outputs | blocked | No peak, clipping, nonfinite or invalid-value record. |
| Unpaired predictive screen or authorized listening | blocked | No screen, listening protocol or panel. |
| Alignment and content delay | blocked | No impulse, speech or content-delay measurement. |
| State, memory and measured content/availability timing | blocked | No state, memory or availability-timing record on the runtime. |
| Independent corpus, clean-reference and output-use gates | blocked | Asset, corpus and output terms are unresolved. |

## Historical and sibling boundary

The pinned records contain a FullSubNet original **source lead**, a v0.2
release reference and upstream-reported context only. There is no local
FullSubNet original run, output, metric, corpus or runtime. No value is
inferred from merged peer enhancement evidence packages:

- `cmgan`, `metricgan-speechbrain-voicebank` and `dpcrn-dns3-tflite` are
  adjacent 16 kHz enhancement blockers with different models and only synthetic
  mechanism evidence.
- `gtcrn-streaming-onnx` is a causal streaming candidate with a different mask
  and runtime; its geometry does not transfer to the original full-band/sub-band
  design.
- `rnnoise-v0-2` is a hybrid DSP/RNN baseline with different geometry and its
  own unresolved weight terms.
- `survey-cln-01` is a merged coverage survey and supplies no measured result.

The **FullSubNet+ sibling** (`SDK-FULLSUBNET`) is a different channel-attention,
complex-mask model. Its merged task-evidence package is not present in this
tree; only the read-only research readiness report and the fail-closed
`adapters/fullsubnet-plus/adapter.json` record exist outside this repository.
Neither is task evidence, and neither supplies original FullSubNet source,
weights, runtime, cohort or metric. They are listed under
`historical_evidence.sibling_records` with `merged_task_evidence=false` and
`admitted_as_result=false`.

Adjacent ASR, finetuning, voice or pipeline packages are likewise not
inherited: their transcripts, metrics, timings and rights records do not apply
to FullSubNet original.

## Admission contract (task-local; not an SDK, FullSubNet or Enhancement contract)

The schema is `audio-sdk/fullsubnet-original-enhancement-cohort/0.1`. Unknown
and missing fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe
paths, duplicate or unsorted entries, unresolved tokens, non-integral or
out-of-range integers, unsupported sample rates, non-offline runtimes,
unconsented pairs and any false right are rejected. The one accepted control
is synthetic and never qualifies. Admission never reads audio, loads weights
or invokes a model.

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` writes `contract.json`, canonical `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires all three
cold writes to be byte-identical. `verify.py` re-runs three independent
cold-start regenerations in scratch trees and fails on any pin drift,
out-of-scope change, missing sidecar, missing SPDX header or absent blocker. It
also gates this branch's merge-base diff so committed out-of-scope files cannot
pass.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.pt`, `.pth`, `.onnx`, `.safetensors`, binary library, compiled object,
upstream source copy, license text copy or model weight.
