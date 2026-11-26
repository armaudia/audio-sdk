<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MARBLENET-VAD — MarbleNet readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local evidence for the MarbleNet feasibility row. It is
**not** a MarbleNet implementation or adapter. No NVIDIA NeMo source checkout,
NGC checkpoint, general/multilingual/telephony weight file, model card text,
feature asset, runtime, frozen oracle, rights record, audio, corpus, listening
result, device measurement, benchmark or release claim is present. **No result
here qualifies MarbleNet.**

`plan/INVENTORY.json` records `marblenet-vad` as `evidence_status=blocked`,
`disposition=sdk-model`, with the **Analysis** acceptance profile. The only
linked evidence is `research/voice-enhancement-20261101/candidate_matrix.csv`,
which reports the grouped candidate row as unavailable/blocked: no exact
weights, source checkout or adapter are staged. The pinned research register
describes a neural CNN frame classifier with general, multilingual and
telephony variants, mono 16 kHz frame predictions, and an NGC-hosted
`vad_marblenet` collection. It also records that the source-reported release
`1.0.0rc1` is 360.59 kB, that NGC terms apply unless stated otherwise, and that
the exact checkpoint, model card, runtime and weights hash still need review.
None of that is a local run.

## Exact external blocker

The exact **MarbleNet source**, the **caller-selected variant checkpoint**, the
**reviewed model-card/NGC terms** and the **isolated NeMo/PyTorch runtime** are
absent. Nothing was fabricated, reconstructed, mirrored, downloaded or
substituted. No revision, file name, byte count or SHA-256 is asserted as
verified. The source-reported "360.59 kB", `vad_multilingual_marblenet` 1.10.0
name and "NeMo/Torch" note are provenance only.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `https://github.com/NVIDIA/NeMo` at an immutable 40-hex commit, with reviewed upstream license text, a per-file SHA-256 manifest and the frame-VAD model/API definitions |
| Variant checkpoint | The caller-selected MarbleNet variant (general, multilingual or telephony) at an immutable NGC/model revision, including every weight, config, feature asset, model card and terms file, with byte count and SHA-256 per file; another variant is never substituted |
| Runtime | A locked, reproducible isolated NeMo/PyTorch runtime with exact interpreter and package versions, wheel hashes, platform, deterministic settings and an offline load path |
| Rights | Reviewed NeMo code license, NGC/weight terms, model-card terms, training-data provenance, account-access conditions, redistribution, derivative-output and product-use approval; a repository code license does not by itself clear the weights |
| Analysis cohort | A frozen, rights-cleared cohort with continuous speech/nonspeech truth, scored regions, preserved unknown spans, quiet/active/idle/noisy strata, onsets/offsets, sessions and language/speaker groups |
| Analysis results | Independent timestamped-probability, boundary, stratified FN/FP, validity, state/reset, cross-hop, availability, nonfinite, target-device timing, resource and uncertainty results on the exact pinned variant |

The machine-readable record is `report.json` → `asset_audit`,
`source_reported_context`, `upstream_record`, `candidate_requirements`,
`exact_blockers`, `variant_separation`, `analysis_profile` and `gates`.
`contract.json` carries the same disposition, pins, geometry and all eight
blocked release gates.

## What this package verifies

1. **Absence evidence.** Nine fixed workspace probes are checked; no recursive
   walk is performed. `reference.audit_assets()` and `verify.py` fail if any
   probe later appears, so a stale "absent" claim cannot be shipped.
2. **Stable pins.** Reviewed planning records, the VAD source register, the
   discovery note, the open-model assessment, the synthesis note, the
   candidate matrix and the SDK boundary files are pinned by SHA-256. These are
   read-only provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`, `evidence`
   and `write_scope` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local caller-supplied-reference
   manifest has a strict schema. Missing, extra, duplicate, nonfinite,
   wrong-format, unresolved, non-integral, out-of-range, cross-variant,
   mismatched-hash, invalid execution-path or qualification-claiming cases are
   rejected before any state change. One synthetic structural control is
   accepted to prove the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence` and `qualifies=false`.
5. **Variant separation.** General, multilingual and telephony are recorded as
   three distinct unresolved identities. A control proves their canonical
   identity digests differ and that an oracle declaring another variant is
   rejected. No variant is selected, downloaded or substituted.
6. **Analysis profile accounting.** Timestamped probabilities, event
   boundaries, quiet/active/idle/noisy strata, known positives and negatives,
   onset/offset delay, stratified FN/FP, validity versus nonspeech, independent
   state, exact source intervals, availability/dropped/stale events and
   cross-hop behavior are each recorded as **blocked** for qualification.
7. **Framewise/offline separation.** A deterministic synthetic two-path
   control compares a framewise classifier with four frames of left context
   against a centred offline smoother with six frames of lookahead. The control
   is explicitly **not** MarbleNet: the offline path is never presented as
   framewise output, and neither path has any qualification effect.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the Apache-2.0 text, the CI workflow,
   `.gitattributes` and `scripts/ci.py` are pinned by SHA-256 and verified
   unchanged. Installed v0 remains 16 kHz, mono, float32, 160 samples per frame.
   No MarbleNet provider is installed or registered; no descriptor, default,
   ABI, shared build, CI, board or handoff change is made.

## Analysis profile application

| Analysis requirement | Status here | Evidence |
| --- | --- | --- |
| Timestamped probabilities | control only | Synthetic integer trace with exact half-open intervals; no model probability. |
| Event boundaries and detections | control only | Synthetic midpoint/mean decisions only; no MarbleNet event. |
| Quiet and active speech | blocked | No rights-cleared quiet/active cohort. |
| Idle noise | blocked | No real nonspeech audio or false-alarm measurement. |
| Known positives and negatives | blocked | No real labels or matched controls. |
| Onset/offset delay | control only | Synthetic boundary error only; not operational latency. |
| Stratified FN/FP | blocked | No real cohort and no stratified scoring. |
| Validity versus nonspeech | control only | Unknown spans are preserved; invalid values are rejected. |
| Independent state | blocked | No checkpoint, per-stream cache or reset. |
| Exact source intervals | control only | Synthetic sample mapping only. |
| Availability, dropped/stale events | blocked | No target runtime or event bus. |
| Cross-hop behavior | blocked | Candidate window/shift is unresolved; only the 160-sample SDK hop is fixed. |

## Release gates (all blocked)

- **RG-01** Exact MarbleNet source revision, selected variant checkpoint
  digest, byte count, format, parameter layout and tensor schema are not
  pinned.
- **RG-02** No isolated runtime reproduces an approved probability/event vector
  for the selected variant.
- **RG-03** Code, NGC/weight, model-card, training-data, corpus, access,
  redistribution, derivative-output and product-use rights are unresolved.
- **RG-04** Feature frontend, analysis window, frame shift, left context,
  lookahead, chunking, pooling, thresholds, smoothing and cache reset are
  undocumented; framewise and offline paths are not contracted.
- **RG-05** No rights-cleared held-out cohort with continuous truth and
  preserved unknown spans is scored.
- **RG-06** Framewise state, independent caches, reset, exact intervals,
  dropped/stale events, cross-hop and nonfinite behavior are unverified.
- **RG-07** No target-device pacing, availability, deadline, memory or finite
  drain measurement exists.
- **RG-08** No opt-in provider intake, descriptor/license review or independent
  exact-head release approval exists.

Exact blocker IDs: `no_reviewed_implementation`,
`no_checkpoint_or_weights`, `no_runtime_lock`, `no_rights_record`,
`no_geometry_or_inference_contract`, `no_frozen_oracle_or_parity`,
`no_rights_cleared_cohort`, `no_timing_or_intake`.

## Peer and historical boundary

The merged sibling VAD evidence packages are adjacent controls or blockers on
different candidates. None supplies a MarbleNet source, checkpoint, runtime,
cohort or metric, and no value is inherited or pooled:

- `docs/task-evidence/cnn-bilstm-vad/report.json` — a different neural VAD
  literature lead with no implementation or checkpoint; its synthetic
  bidirectional/framewise control is not MarbleNet.
- `docs/task-evidence/crnn-vad/report.json` — an architecture-class blocker,
  not a pinned MarbleNet model.
- `docs/task-evidence/silero-vad-6-2-3-reference/report.json` — a different
  model with its own ONNX path; no timing, probability or accuracy transfers.
- `docs/task-evidence/webrtc-vad/report.json` — an installed DSP control, not a
  neural frame classifier.

## Admission contract (task-local; not an SDK or MarbleNet contract)

The schema is `audio-sdk/marblenet-vad/admission/0.1`. Unknown and missing
fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths, duplicate
or unsorted events, unresolved tokens, non-integral or out-of-range integers,
invalid context/lookahead combinations, a cross-variant oracle and any false
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
out-of-scope change, missing sidecar, missing SPDX header or absent blocker.

## Pinned inputs

Source pins (SHA-256):

- `audio-benchmark-platform/audio-sdk/CONTRACTS.md` —
  `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69`
- `audio-benchmark-platform/audio-sdk/README.md` —
  `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35`
- `audio-benchmark-platform/plan/INVENTORY.json` —
  `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c`
- `audio-benchmark-platform/plan/swarm/VERIFICATION.md` —
  `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910`
- `reports/vad-research/20261028-synthesis-v7.md` —
  `2bc353e9d6d648a7e58204e202a5f4a03b75859b58f3fd515ec37216168a5a6c`
- `reports/vad-research/attempt-discovery-20261028-01/findings.md` —
  `9d5c555c1c5f2db9ce3eb27da2d3f625c2e25621f6700521f82c8af300ff59d5`
- `reports/vad-research/attempt-neural-01/assessment.md` —
  `74232ba9f36976ef1b238bca12305d6c02a614adb73fb2981f6fc3f07133cfe1`
- `reports/vad-research/attempt-open-models-20261028-01/assessment.md` —
  `565d4330d625dd8eec9e607811df300749382feffc87ef54d5e4924e09448ad6`
- `research/plans/F02/vad_sources.md` —
  `374784f6f1cea620f376da59691e4260aafc582e1203be4f98837752cfdf75ec`
- `research/voice-enhancement-20261101/agent-segmentation/REPORT.md` —
  `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2`
- `research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` —
  `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f`
- `research/voice-enhancement-20261101/candidate_matrix.csv` —
  `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245`

Boundary pins (SHA-256):

- `.gitattributes` —
  `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185`
- `.github/workflows/ci.yml` —
  `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415`
- `CMakeLists.txt` —
  `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04`
- `CONTRACTS.md` —
  `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69`
- `LICENSES/Apache-2.0.txt` —
  `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30`
- `REUSE.toml` —
  `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8`
- `api/include/audio_sdk/provider_v0.h` —
  `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766`
- `api/include/audio_sdk/session_v0.h` —
  `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1`
- `scripts/ci.py` —
  `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f`

Task identity: `SDK-MARBLENET-VAD`, base commit
`0cc1e79e592d7fc25f054fcd98824053be281f5e`, branch
`swarm/SDK-MARBLENET-VAD`.

## Licensing

This package is Apache-2.0; see `LICENSES.md` and the `.license` sidecars. It
contains only text, JSON and Python source. It contains no `.wav`, `.flac`,
`.nemo`, `.pt`, `.pth`, `.onnx`, `.safetensors`, binary library, compiled
object, upstream source copy, license text copy or model weight.
