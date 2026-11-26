<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic feasibility, blocker, and synthetic-control evidence
package for inventory component `speechbrains-ecapa-speaker-similarity`
(category `SPK-05` boundary research control, verification profile `evidence`,
mode `research-control`). No exact licensed SpeechBrain ECAPA source checkout, pinned
encoder weights/model asset, isolated runtime/build record, rights record,
parity vector, or matched held-out benchmark is present in this workspace as a
qualified SDK asset. This package creates **no new execution, provider,
descriptor, registry, analysis surface, ABI, default, shared build, CI, board,
handoff, or release change**.

Task owner: `agent-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY`; reviewer:
`reviewer-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY`. Claim base: audio-sdk
`4c0f5464eeddff2204b527e8bc4ad09c41b2a657`; branch
`swarm/SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY`; worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY`.
Dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`. Write scope is task-local
only: `docs/task-evidence/speechbrains-ecapa-speaker-similarity/`.

## What is present and what is missing

Merged evidence pins this component as a partial research-control proxy:

| Source | Pinned finding | Not attributed here |
| --- | --- | --- |
| `plan/INVENTORY.json` (`speechbrains-ecapa-speaker-similarity`) | `evidence_status=partial`, `disposition=research-control`, task `SDK-SPEECHBRAINS-ECAPA-SPEAKER-SIMILARITY`; plan note requires encoder revision and source/target/enrollment geometry recorded independently from converter | Any qualified SpeechBrain ECAPA runtime result, identification, verification, or release evidence |
| `research/accent-conversion-20261101/README.md` | TokAN smoke test reports SpeechBrain ECAPA cosine as a quick similarity proxy (not human identity rating); same-clip reference geometry used; no blinded listening panel | Any independent speaker identity/verification claim, any qualified proxy benchmark |
| `docs/task-evidence/survey-spk-05/README.md` | SPK-05 survey records SpeechBrain ECAPA as partial research control: in-model similarity only, not independent identity evidence | Any qualified SPK-05 identification/verification score |

No workspace path contains an approved SpeechBrain ECAPA checkout, pinned encoder
weights, runtime lock, build record, licence/rights record, parity vector, or
matched cohort manifest for this exact component. Nothing is downloaded,
vendored, cloned, or inferred as approved. Therefore:

- source identity, revision, encoder asset hash, and licence terms cannot be
  pinned as qualified evidence;
- no upstream/runtime output exists, so no exact parity can be evaluated;
- no rights-cleared labeled audio/corpus is read, so no identification,
  verification, diarization, listening, device timing, benchmark, or release
  value is reported;
- missing evidence is never promoted to pass/qualification.

## Task-local synthetic control

`reference.py` includes a deterministic synthetic signal-domain embedding/cosine
control over generated frames. It exists only to prove deterministic local
arithmetic/reporting and rejection behavior. It is explicitly:

- `qualifies_candidate = false`
- `not_speechbrain-ecapa = true`
- `not_real_audio_corpus = true`
- `not_identification = true`
- `not_verification = true`
- `metric_scope = synthetic_signal_domain_not_a_speechbrain-ecapa_or_corpus_result`

All `candidate_metrics` values are `null` with `measured=false` and
`derived_from_synthetic_control=false`.

## Caller-supplied asset contract (validation only)

`contract.json` defines `speechbrain_ecapa_speaker_similarity_research_control_adapter`
manifest validation. Validation checks absolute paths, SHA-256 fields, full
40-hex nonzero source revision, variant, capability, v0 geometry (16kHz/mono/
160), and task geometry (`same_clip_proxy|cross_clip_proxy|enrollment_proxy`).
A structurally valid manifest is **not qualification**; this package supplies
no approved manifest/runtime/assets.

## Adverse controls

`report.json` records rejected adverse cases covering missing/extra manifest
fields, relative/traversing paths, malformed SHA-256, short/nonhex/zero
revision, wrong variant/capability/geometry/rate/frame, nonfinite/short/long/
out-of-range/bool/string frame inputs, embedding dimension mismatch, nonfinite/
zero-norm embeddings, strict JSON duplicate keys, and non-finite JSON constants.
Every case is `rejected`; missing evidence never qualifies.

## Evidence acceptance profile

Profile `evidence` is applied conservatively: pinned scorer/proxy and cohort
are unmeasured; evidence classes remain separated; invalid/missing cases are
rejected by controls; source/target/enrollment geometry is unestablished; and
similarity proxy is explicitly not promoted to identification, verification,
diarization, or release evidence.

## Eight blocked release gates

| Gate | Status | Requirement |
| --- | --- | --- |
| `exact_source_and_asset_identity` | blocked | Exact approved source repo/URL, full 40-hex revision, per-file SHA-256, encoder weights identity, dependency lock. |
| `runtime_admission` | blocked | Isolated hash-pinned runtime and reproducible build/execution record. |
| `artifact_rights_and_licence` | blocked | Verified implementation/model/dependency/corpus rights; no unapproved redistribution. |
| `exact_reference_parity` | blocked | Approved exact-runtime outputs match frozen caller input/geometry. |
| `evidence_cohort_and_scoring` | blocked | Rights-cleared held-out proxy cohort with frozen geometry, scorer, and separated evidence classes. |
| `task_geometry_and_adapter_boundary` | blocked | Fixed source/target/enrollment geometry, normalization, scoring contract, opt-in research-control boundary. |
| `opt_in_provider_intake` | blocked | Opt-in intake, licence/descriptor review, optional-runtime absence behavior, independent public-surface decision. |
| `public_default_and_release` | blocked | Explicit default/release/public-benchmark approval; off by default and not qualified. |

## Reproduction

```sh
cd docs/task-evidence/speechbrains-ecapa-speaker-similarity
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
