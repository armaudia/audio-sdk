<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-FINALLY — FINALLY readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the FINALLY
feasibility row. It is **not** a FINALLY implementation. No upstream source
checkout, pretrained checkpoint, WavLM asset, config, runtime, corpus,
noisy/clean pair, enhanced waveform, listening result, device measurement,
benchmark or release claim is present. **No result here qualifies FINALLY.**

The structured inventory marks `finally` as `evidence_status=considered` with
the **Enhancement** acceptance profile (`verification_profile: enhancement`,
`plan/INVENTORY.json`). The row's plan note asks for runnable source, exact
assets, permitted scope, task geometry and matched evidence before a
caller-supplied-asset reference and an opt-in adapter; none of those
prerequisites exists locally.

## Exact external blocker

The exact **source**, **checkpoint/weights bundle** and **isolated runtime** are
all absent. The pinned census records FINALLY as *"48 kHz universal generative
enhancement and restoration; WavLM-conditioned HiFi++"* and states plainly that
the accessible GitHub code is a **later reproduction, not the original authors'
release**: *"Public implementation and checkpoints exist, but accessible GitHub
code is a later reproduction, not the original authors' release."* The census
also records 454M parameters (358M WavLM), 0.03 RTF on a V100, and that CPU cost
and low-delay suitability are poor. Those are source-reported context only.

Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count or SHA-256 is asserted as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `inverse-ai/FINALLY-Speech-Enhancement` at an immutable 40-hex commit, with the reviewed upstream license text, a per-file SHA-256 manifest from a reviewable tree, and a recorded provenance decision versus the original NeurIPS 2024 authors' release |
| Checkpoint bundle | The caller-selected FINALLY checkpoint at an immutable 40-hex revision, including every weight, config, WavLM feature asset, model card and terms file, with byte count and SHA-256 per file (census context: 454M parameters, 358M WavLM, 48 kHz) |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter and `torch` package versions, a GPU device profile, a lock SHA-256, an offline load path and a recorded host profile |
| Rights | Reviewed weight and model-card terms, training-data provenance, corpus rights, clean-reference permission, output use and redistribution |
| Cohort | A frozen, rights-cleared paired noisy/clean cohort with exact sample rates and durations, language and speaker groups, held-out splits, and identity/noisy, task-matched-baseline, clean-preservation, peak/invalid and unpaired controls |
| Enhancement results | Independent paired SI-SDR and STOI, clean-speech preservation, peaks and invalid (including nonfinite) outputs, authorized listening or a labeled predictive screen, alignment, content delay, state, memory, availability timing, resources and uncertainty on the exact 48 kHz runtime |

The machine-readable record is `report.json` → `source_probe`, `weights_probe`,
`runtime_probe`, `absence_evidence`, `required_artifacts`, `exact_blockers`,
`enhancement_profile` and `gates`. `contract.json` carries the same
disposition, pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** Reviewed planning records, the category registry, the
   category survey source list, the noise-suppression candidate census and the
   SDK boundary files are pinned by SHA-256. These are read-only provenance
   inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local Enhancement cohort manifest
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted entries, unresolved
   tokens, non-integral or out-of-range integers, unsupported sample rates,
   non-offline runtimes, unconsented pairs and false rights are rejected. One
   synthetic structural control is accepted to prove the validator is not
   blanket-rejecting; it is labelled `synthetic_schema_control` and
   `qualifies=false`.
5. **Enhancement profile accounting.** Identity/noisy control, task-matched
   baseline, paired SI-SDR and STOI, clean-speech preservation, peaks and
   invalid outputs, authorized listening, alignment, content delay, state,
   memory, availability timing and the independent rights gates are each
   recorded as **blocked**.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No FINALLY provider is installed or
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

## Historical and peer boundary

The pinned census and inventory contain a FINALLY **source lead** and
source-reported context only. There is no local FINALLY run, output, metric,
corpus or runtime. No value is inferred from merged sibling enhancement
evidence packages:

- `cmgan`, `metricgan-speechbrain-voicebank` and `dpcrn-dns3-tflite` are
  adjacent 16 kHz enhancement blockers with different models and only synthetic
  mechanism evidence.
- `gtcrn-streaming-onnx` is a causal streaming candidate; its geometry does not
  transfer to the offline 48 kHz FINALLY reference.
- `rnnoise-v0-2` is a hybrid DSP/RNN baseline with different geometry and its
  own unresolved weight terms.
- `survey-cln-01` is a merged coverage survey and supplies no measured result.

Adjacent ASR, finetuning, voice or pipeline packages are likewise not
inherited: their transcripts, metrics, timings and rights records do not apply
to FINALLY.

## Admission contract (task-local; not an SDK, FINALLY or Enhancement contract)

The schema is `audio-sdk/finally-enhancement-cohort/0.1`. Unknown and missing
fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths, duplicate
or unsorted entries, unresolved tokens, non-integral or out-of-range integers,
unsupported sample rates, non-offline runtimes, unconsented pairs and any false
right are rejected. The one accepted control is synthetic and never qualifies.
Admission never reads audio, loads weights or invokes a model.

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
