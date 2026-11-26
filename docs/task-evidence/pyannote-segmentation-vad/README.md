<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PYANNOTE-SEGMENTATION-VAD

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic feasibility, blocker, and synthetic-control evidence
package for inventory component `pyannote-segmentation-vad` (category `DET-01`,
verification profile `analysis`, mode `feasibility`). No exact licensed
pyannote segmentation/VAD source checkout, model/weights, runtime, build
record, licence/rights record, parity vector, or matched held-out benchmark is
present in this workspace. This package creates **no new execution, provider,
descriptor, registry, analysis surface, ABI, default, shared build, CI, board,
handoff, or release change**.

Task owner: `agent-PYANNOTE-SEGMENTATION-VAD`; reviewer:
`reviewer-PYANNOTE-SEGMENTATION-VAD`. Claim base: audio-sdk
`80dc1fb371e1846a5d50f5b28c955ab92bfcbe46`; branch
`swarm/SDK-PYANNOTE-SEGMENTATION-VAD`; worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PYANNOTE-SEGMENTATION-VAD`.
Dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`, `SDK-FND-PROVIDER`.
Write scope is task-local only:
`docs/task-evidence/pyannote-segmentation-vad/`.

## What is present and what is missing

Merged evidence pins this component as blocked/unavailable for exact local
execution:

| Source | Pinned finding | Not attributed here |
| --- | --- | --- |
| `plan/INVENTORY.json` (`pyannote-segmentation-vad`) | `evidence_status=blocked`, `disposition=sdk-model`, task `SDK-PYANNOTE-SEGMENTATION-VAD` | Any pyannote runtime result |
| `research/voice-enhancement-20261101/candidate_matrix.csv` row 8 | "No exact candidate weights, source checkout, or adapter are staged..." | Any pyannote score |
| `research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | Additional TEN VAD / PulseVAD / FSMN / MarbleNet / FireRedVAD / pyannote had no staged weights/checkpoint/adapter; no inference run | Any candidate-specific accuracy result |
| `research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | Same family listed as researched but not run; no local accuracy evaluation | Any segmentation/VAD measurement |

No workspace path contains a pyannote segmentation/VAD checkout, weights,
runtime lock, build record, licence/rights record, parity vector, or matched
cohort manifest for this exact component. Nothing is downloaded, vendored,
cloned, or inferred from invented URLs. Therefore:

- source identity, revision, asset hashes, and licence terms cannot be pinned;
- no upstream/runtime output exists, so no exact parity can be evaluated;
- no labeled audio/corpus is read, so no timestamped probability, onset/offset
  delay, FN/FP, boundary, diarization, listening, device timing, benchmark, or
  release value is reported;
- missing evidence is never promoted to pass/qualification.

## Task-local synthetic control

`reference.py` includes a deterministic synthetic signal-domain RMS-threshold
control over generated frames. It exists only to prove deterministic local
arithmetic/reporting and rejection behavior. It is explicitly:

- `qualifies_candidate = false`
- `not_pyannote = true`
- `not_real_audio_corpus = true`
- `metric_scope = synthetic_signal_domain_not_a_pyannote_or_corpus_result`

All `candidate_metrics` values are `null` with `measured=false` and
`derived_from_synthetic_control=false`.

## Caller-supplied asset contract (validation only)

`contract.json` defines `pyannote_segmentation_vad_offline_annotation_adapter`
manifest validation. Validation checks absolute paths, SHA-256 fields, full
40-hex nonzero source revision, variant, capability, v0 geometry (16kHz/mono/
160), task geometry (`vad|segmentation|vad+segmentation`), canonical decimal
threshold, and non-negative hangover. A structurally valid manifest is **not
qualification**; this package supplies no approved manifest/runtime/assets.

## Adverse controls

`report.json` records rejected adverse cases covering missing/extra manifest
fields, relative/traversing paths, malformed SHA-256, short/nonhex/zero
revision, wrong variant/capability/geometry/rate/frame, exponent/negative
threshold, nonfinite/short/long/out-of-range/bool/string frame inputs, strict
JSON duplicate keys, and non-finite JSON constants. Every case is `rejected`;
missing evidence never qualifies.

## Analysis acceptance profile

Profile `analysis` is applied as blocked/unmeasured requirements: timestamped
probability/boundary scoring, quiet/active speech and idle/noise positives and
negatives, onset/offset delay and stratified FN/FP, independent state with
exact source intervals/availability/dropped-stale events/cross-hop behavior,
and validity separate from nonspeech. All are `measured:false`.

## Eight blocked release gates

| Gate | Status | Requirement |
| --- | --- | --- |
| `exact_source_and_asset_identity` | blocked | Exact approved source repo/URL, full 40-hex revision, per-file SHA-256, model/weights identity, licence record. |
| `runtime_admission` | blocked | Isolated hash-pinned runtime and reproducible build/execution record. |
| `artifact_rights_and_licence` | blocked | Verified implementation/model/dependency/corpus rights; no gated terms ignored. |
| `exact_reference_parity` | blocked | Approved exact-runtime outputs match frozen caller input/task geometry. |
| `analysis_cohort_and_scoring` | blocked | Rights-cleared, label-complete held-out analysis cohort with required scoring. |
| `task_geometry_and_adapter_boundary` | blocked | Fixed VAD/segmentation boundary, geometry, event schema, availability policy, opt-in adapter boundary. |
| `opt_in_provider_intake` | blocked | Opt-in intake, licence/descriptor review, optional-runtime absence behavior, independent public-surface decision. |
| `public_default_and_release` | blocked | Explicit default/release/public-benchmark approval; off by default and not qualified. |

## Reproduction

```sh
cd docs/task-evidence/pyannote-segmentation-vad
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
git diff --check
```

`verify.py` is read-only and fail-closed. It confirms byte-identical report/
contract/sources regeneration, SPDX/REUSE coverage, git scope limited to this
task directory, rejection behavior, and three cold-start byte-identical runs.

The mutable full board file `audio-benchmark-platform/plan/swarm/TASKS.json`
is never hashed. Only stable linked-row identity is projected into
`report.json`; mutable fields (`status`, `owner`, `handoff`, `review`,
`blocked_reason`, `dispatch_priority`) are excluded.
