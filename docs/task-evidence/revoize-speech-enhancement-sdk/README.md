<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic feasibility, blocker, and synthetic-control evidence
package for inventory component `revoize-speech-enhancement-sdk` (verification
profile `enhancement`, mode `external-adapter`). No exact licensed Revoize
SDK/runtime package, selected model/variant, credentials, rights record, parity
vector, enhancement cohort, or device timing evidence is present in this
workspace. This package creates **no new execution, provider, descriptor,
registry, ABI, default, shared build, CI, board, handoff, or release change**.

Task owner: `agent-REVOIZE-SPEECH-ENHANCEMENT-SDK`; reviewer:
`reviewer-REVOIZE-SPEECH-ENHANCEMENT-SDK`. Claim base: audio-sdk
`a9cf338c0b363d69408c931071071583a49ebdc1`; branch
`swarm/SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK`; worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK`.
Dependencies: `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE`.
Write scope is task-local only:
`docs/task-evidence/revoize-speech-enhancement-sdk/`.

## What is present and what is missing

| Source | Pinned finding | Not attributed here |
| --- | --- | --- |
| `plan/INVENTORY.json` (`revoize-speech-enhancement-sdk`) | `evidence_status=considered`, `disposition=external-adapter`, task `SDK-REVOIZE-SPEECH-ENHANCEMENT-SDK` | Any Revoize runtime result |
| `research/noise_suppression_candidate_census.md` line 81 | "Commercial native SDK with selectable models and fixed-chunk real-time processing" | Any vendor score, license grant, or local measurement |

No workspace path contains a Revoize SDK/runtime package, model asset, runtime
lock/build record, licence/rights record, parity vector, or matched cohort
manifest for this exact component. Nothing is downloaded, vendored, or inferred
from invented URLs/packages. Therefore:

- exact runtime/model/version identity and SHA-256 cannot be pinned;
- vendor licence, redistribution, telemetry/data-use, and credential terms are
  unverified;
- task geometry (denoise-only vs restoration/dereverb scope, sample rate,
  channel/chunk, lookahead, content delay, reset/drain) is unestablished;
- no runtime output exists, so no exact parity/provenance can be evaluated;
- no rights-cleared enhancement cohort is read, so no SI-SDR/STOI, clean-speech
  preservation, peak/nonfinite, listening, device timing, benchmark, or release
  value is reported;
- missing evidence is never promoted to pass/qualification.

## Task-local synthetic control

`reference.py` includes a deterministic synthetic signal-domain RMS-threshold
control over generated frames. It exists only to prove deterministic local
arithmetic/reporting and rejection behavior. It is explicitly:

- `qualifies_candidate = false`
- `not_revoize = true`
- `not_real_audio_corpus = true`
- `metric_scope = synthetic_signal_domain_not_revoize_or_corpus_result`

All `candidate_metrics` values are `null` with `measured=false` and
`derived_from_synthetic_control=false`.

## Caller-supplied asset contract (validation only)

`contract.json` defines `revoize_speech_enhancement_sdk_external_adapter`
manifest validation. Validation checks absolute paths, SHA-256 fields, immutable
non-empty source/release pin, variant, capability, channels=1, bounded sample
rate/frame size, and bounded model selection. A structurally valid manifest is
**not qualification**; this package supplies no approved manifest/runtime/assets.

## Adverse controls

`report.json` records rejected adverse cases covering missing/extra manifest
fields, relative/traversing paths, malformed SHA-256, bad release pin, wrong
variant/capability/channels/sample-rate/frame/model selection, nonfinite/short/
long/out-of-range/bool/string frame inputs, strict JSON duplicate keys, and
non-finite JSON constants. Every case is `rejected`; missing evidence never
qualifies.

## Enhancement acceptance profile

Profile `enhancement` is applied as blocked/unmeasured requirements: identity/
noisy control and task-matched baseline, paired SI-SDR/STOI where permitted,
clean-speech preservation/peaks/nonfinite bounds, alignment/state/memory and
measured content/availability timing for the exact runtime, and separately
labeled predictive screen or authorized listening for unpaired speech. All are
`measured:false`.

## Eight blocked release gates

| Gate | Status | Requirement |
| --- | --- | --- |
| `exact_runtime_and_asset_identity` | blocked | Exact approved Revoize SDK/runtime package, selected model variant, platform build, immutable version/revision, and SHA-256 identities pinned. |
| `rights_licence_and_redistribution` | blocked | Vendor licence, evaluation/redistribution, telemetry/data-use constraints, and credential/model rights verified with dated evidence. |
| `reproducible_isolated_execution` | blocked | Isolated reproducible execution record on documented platform without network during scoring; credentials/keys absent or explicitly scoped. |
| `exact_reference_parity_or_provenance` | blocked | Frozen inputs produce exact/declared-tolerance outputs matched to approved runtime/model; synthetic controls are not parity. |
| `enhancement_cohort_and_scoring` | blocked | Rights-cleared enhancement-profile cohort with identity/noisy controls, paired SI-SDR/STOI where permitted, preservation/peak/nonfinite, and adverse controls. |
| `task_geometry_and_boundary` | blocked | Sample-rate/channel/chunk/lookahead/content-delay/reset/drain, denoise-only-vs-restoration scope, and external-adapter boundary fixed and reviewed. |
| `opt_in_provider_intake` | blocked | Explicit opt-in intake, descriptor review, optional-runtime absence behavior, independent public-surface decision; no default registration or shared build/CI change. |
| `public_default_and_release` | blocked | Explicit default selection, paced resource/deadline/device evidence, and release/public-benchmark approval; off by default and not qualified. |

## Reproduction

```sh
cd docs/task-evidence/revoize-speech-enhancement-sdk
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
