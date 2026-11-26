<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SILERO-VAD-V5-ONNX-REFERENCE — readiness blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`silero-vad-v5-onnx-reference` (`component_id=silero-vad-v5-onnx-reference`,
title "Silero VAD v5 ONNX reference"). Decision: **DEFER**;
`status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. The acceptance profile is **Analysis**,
as assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`.

Pinned base: `acefdd1df870fd19f990eba92fd15bf38f171f75`.
Branch: `swarm/SDK-SILERO-VAD-V5-ONNX-REFERENCE`.

This package does **not** register a provider, change any descriptor, registry,
default, shared build, CI workflow or installed-v0 behavior, or touch the
shared board, handoffs or another worktree. It does not import ONNX Runtime,
decode tensor values, execute the graph, read audio, measure a device, run a
listening test or make a benchmark or release claim.

## Exact external blocker

One ONNX artifact is present, but the *exact licensed reference* is not. The
package therefore stays `DEFER`:

- **Version is not proven.** In-repo cpp-library documents call
  `cpp-library/.deps/silero_vad.onnx` the pinned **Silero VAD v5** model. The
  same SHA-256 is recorded in `research/plans/F02/vad_sources.md` as the
  **silero-vad 6.2.3 bundled standard ONNX** graph. The model has no embedded
  version string. No upstream release tag, commit, model card or artifact
  manifest resolves the conflict.
- **License and weight terms are absent.** No upstream license/notice bundle,
  per-weight terms or product-use decision is staged. The cpp-library manifest
  only says "distributed by its authors under their own terms; verify before
  redistribution".
- **Exact upstream source and wrapper are absent.** The pinned cpp-library
  wrappers are project code, not the upstream v5 wrapper. No official v5
  `utils_vad` source, frozen wrapper or warmup/reset oracle is present.
- **Exact runtime is absent.** No v5 Python/ONNX Runtime/NumPy lock, wheel
  hash, install/import digest, deterministic setting or offline environment is
  recorded. An unrelated playback-speed venv is neither the v5 runtime nor
  pinned, and is not imported or used.
- **No reference outputs or corpus.** No frozen PCM/probability/event oracle,
  no finite/adverse/missing/stale/nonfinite controls, no rights-cleared
  continuous-label cohort and no analysis result exists.
- **No timing or intake.** No paced target-device availability, deadline,
  resource, finite-drain or reset measurement exists, and no provider intake or
  independent exact-head release review exists.

The merged Silero evidence packages are pinned only as boundary context. They
use synthetic traces, surrogate feature vectors or a model-free stub and do not
contain v5 model output, so none is reused as a reference result.

## Present artifact (pinned, structurally scanned, never executed)

| Field | Value |
| --- | --- |
| Path | `cpp-library/.deps/silero_vad.onnx` |
| SHA-256 | `1a153a22f4509e292a94e67d6f9b85e8deb25b4988682b7e174c65279d8788e3` |
| Bytes | `2,327,524` |
| Producer / IR version | `spox` / `8` |
| Graph inputs / outputs | `input`, `state`, `sr` / `output`, `stateN` |
| State shape | `[2, 1, 128]`, float32 |
| Structural fingerprint SHA-256 | `b513ef1ca141febaa5a8fa09ecdc83d9b87c7302cead9b8a35260c30093023f4` |
| Tensor values decoded | **No** |
| Graph executed | **No** |

The standard-library protobuf scanner reads only protobuf structure, tensor
dimensions, element type and byte counts. It does not decode floating-point
weights and does not run the graph. The fingerprint matches both documented
rate branches:

| Branch | STFT basis | Encoder input channels | Parameters | Weight bytes |
| --- | --- | --- | --- | --- |
| 8 kHz | `130 × 1 × 128` | `65` | `235,649` | `942,596` |
| 16 kHz | `258 × 1 × 256` | `129` | `309,633` | `1,238,532` |
| Total | — | — | `545,282` | `2,181,128` |

Each branch has the same four 3-tap encoder convolutions
(`129→128→64→64→128` at 16 kHz, `65→128→64→64→128` at 8 kHz), a
`512 × 128` input/recurrent LSTM pair with `512` biases, and a single
`1 × 128 × 1` output convolution. The graph's `sr` guard is `16000`; the
8 kHz branch is selected by the other `If` branch.

## Cadence and warmup reference (documented, not output-parity verified)

| Rate | Model window | Context | Input per step | Model hop | v0 frames per window | Cross-hop |
| --- | --- | --- | --- | --- | --- | --- |
| 16 kHz | 512 | 64 | 576 | 32 ms | `16/5` | 16 v0 frames = 5 windows |
| 8 kHz | 256 | 32 | 288 | 32 ms | `8/5` | 8 v0 frames = 5 windows |

- Public v0 geometry remains 16 kHz mono float32 with 160-sample frames.
- The model emits at 32 ms quantization; v0 frames are 10 ms. The LCM relation
  is exact, but a one-model-window output cannot be aligned to every 10 ms v0
  frame. This is a cross-hop question, not a measured availability result.
- The declared initial state and context are zeros, but **no upstream v5
  wrapper is present** to verify warmup, reset or first-output semantics.
- The local cpp wrapper aggregates 160-sample frames, caches the last
  probability and adds a three-silent-window shortcut. It is useful provenance
  but it is not an independent exact v5 wrapper; `exact_warmup_parity=false`.

## Analysis-profile application

| Analysis requirement | Status here | Evidence |
| --- | --- | --- |
| Score timestamped probabilities | blocked | No probability trace exists; the graph was not executed. |
| Score event boundaries and detections | blocked | No event or detection output exists. |
| Include quiet and active speech, idle noise | blocked | No rights-cleared audio or condition-stratified cohort exists. |
| Include known positives and negatives | blocked | No labeled positive or negative case exists. |
| Measure onset and offset delay | blocked | No timestamped reference/model pair exists. |
| Report stratified FN/FP | blocked | No condition labels, predictions or scorer exist. |
| Separate validity from nonspeech | blocked | No validity policy was exercised against a caller-supplied trace. |
| Verify independent state, exact intervals, availability, dropped/stale events and cross-hop behavior | blocked | No independent-state, interval, availability or cross-hop run exists. |

These are deliberately not replaced with synthetic proxies, sibling-package
numbers or upstream claims.

## Release gates

All eight gates are blocked and `qualifies=false`:

| Gate | Blocked condition |
| --- | --- |
| `RG-01` | Upstream v5 revision, model-version resolution, license/notice and weight-use decision are absent. |
| `RG-02` | No exact upstream wrapper, warmup/reset policy or 8/16 kHz output parity. |
| `RG-03` | No pinned deterministic v5 runtime with wheel hashes and import digest. |
| `RG-04` | No frozen PCM/probability/event oracle or finite/adverse/missing/stale/nonfinite controls. |
| `RG-05` | No rights-cleared continuous-label analysis cohort. |
| `RG-06` | No reproduced timestamped, boundary, detection, validity, interval, state, cross-hop or stratified FN/FP result. |
| `RG-07` | No target-device paced availability, deadline, resource or finite-drain evidence. |
| `RG-08` | No OFF-by-default provider intake or independent exact-head release review. |

## Admission contract (task-local, schema-only)

`contract.json.admission_schema` defines a strict caller-supplied reference
bundle: exact model digest, byte count, producer, IR version, graph I/O, rates
and structural fingerprint; exact upstream source revision and wrapper digest;
exact runtime version, Python, wheel digest, 1/1 threads, deterministic and
offline; exact 8/16 kHz window/context, state shape, `0.5` threshold and zero
state/context warmup and reset policies; eight unique fixtures covering both
rates with PCM/probability/event digests and `nonfinite_count=0`; reviewed
rights references with `claims_qualified=false`; and finite/adverse/missing/
nonfinite/stale controls. Outcomes can never qualify at admission.

`reference.py` actually executes 24 rejection controls (missing/extra fields,
bad schema, model/byte/producer/structural/rate mismatch, bad revision, missing
license, bad runtime version/threads/determinism, cadence mismatch,
noncanonical threshold, bad digest, nonfinite fixture, duplicate id, missing
rate coverage, rights/outcome qualification claims, failed controls) plus one
structurally valid synthetic schema control. The control is accepted for schema
coverage only, is labelled
`synthetic_schema_control_not_evidence`, and `qualifies=false`. Admission never
imports a runtime, reads audio, loads weights or executes a model.

## Pins

`SOURCES.sha256` pins every read-only source/boundary input and every task-local
artifact except its own bytes and `README.md`. The present ONNX artifact is
pinned by its exact SHA-256 and byte count; a missing or changed artifact makes
regeneration fail closed. The mutable full `plan/swarm/TASKS.json` is **not**
pinned. Only the stable, non-mutable identity projection
(`id`, `title`, `component`, `mode`, `repository`, `depends_on`) of this row and
its five linked foundation rows gates anything; status, owner, claim, review,
handoff and priority never enter canonical bytes.

## Files

- `README.md` — this blocker and scope record.
- `LICENSES.md` — licensing boundary.
- `contract.json` — task contract, graph/cadence reference, gates, blockers and
  admission schema.
- `reference.py` — standard-library pins, protobuf structure scan, cadence
  arithmetic, strict JSON, admission controls and canonical report builder.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest.
- `run.py` — 3x byte-identical regeneration of the four generated artifacts.
- `test_reference.py` — Python unittest acceptance suite.
- `verify.py` — read-only pins/JSON/reproduction/licensing/scope verifier.
- `*.json.license` / `SOURCES.sha256.license` — REUSE sidecars.

Canonical report SHA-256:
`54e24f7069e6e127f66d630f196a5a88573d3a9a581425978aec71fbbf5e9a0d`.

## Reproduce and verify

Standard library only. Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git -C ../../.. diff --check
```

`run.py` writes `contract.json`, `report.json`, `report.json.sha256` and
`SOURCES.sha256` three times and requires byte-identical output. `verify.py`
checks the committed bytes against three fresh cold-start copies in temporary
trees, including source/boundary symlinks and the exact model artifact, so
path-dependent output or a stale absence/label claim cannot pass by accident.
The model artifact is caller-supplied and is not redistributed here.

## Non-claims

- No upstream v5 source revision, wrapper, model card or license grant is
  present.
- The present ONNX bytes are not version-proven as v5; the 6.2.3 label for the
  same SHA-256 is an open conflict.
- No tensor value is decoded, no graph is executed and no probability is
  produced.
- No audio, annotation, corpus, reference output, listening result, device
  timing, benchmark result or release claim exists.
- Structural shapes and exact pins are not a model-version, license, output or
  product qualification.
- A present ONNX file is not a provider registration, default selection or
  supported capability.
- No merged Silero package is reused as a v5 result; those packages are
  synthetic or model-free boundary context.
- Missing evidence never qualifies the candidate.
