<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK — vendor-boundary blocker

**Decision `DEFER`; status `proposal_only_incomplete`; evidence `incomplete`;
qualification `not_qualified`; eight release gates blocked.** This directory is
a bounded, deterministic, task-local external-comparison record for
`krisp-noise-cancellation-background-voice-cancellation-sdk` (title "Krisp
Noise Cancellation / Background Voice Cancellation SDK", mode
`external-adapter`, `verification_profile: enhancement`). It is **not** a Krisp
adapter, vendor integration or benchmark. No Krisp SDK, platform build,
entitlement key, model bundle, licence text, runtime, processed data, vendor
output, listening result, device timing, benchmark or release claim is present.
**No result here qualifies any Krisp product.**

Pinned base: `cb3d9812875b741a320c6cfe22de8043952fdd16`.
Branch: `swarm/SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK`.
Owner: `agent-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK`.
Reviewer: `reviewer-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK`.

## Exact external blocker

The merged census records exactly one matching candidate:

> **Krisp Noise Cancellation / Background Voice Cancellation SDK** | Commercial
> low-latency call SDK; distinct environmental-noise and competing-voice model
> families | Official RTC SDK docs enumerate versioned outbound/inbound noise
> cancellation and background voice cancellation models, sample-rate profiles,
> CPU tiers and on-request MAX models. | Include only as licensed SDK reference
> when entitlement permits; product-level comparison, with BVC evaluated in a
> competing-speaker stratum and artifact/API/version pinned.

`research/noise_suppression_candidate_census.md`, line 78.

The record supplies a vendor name, two model families, versioned
outbound/inbound models, multiple but unspecified sample-rate profiles, CPU
tiers, on-request MAX models and licence-gated access. It supplies **no**
release version, SDK version, ABI, platform build, artifact file name, byte
count, SHA-256, licence text, entitlement key, telemetry statement, deployment
grant, channel layout, frame/hop/reset/drain contract, processed data, vendor
output or score. The local 20-row asset register has no Krisp entry, and the
three sibling Krisp tasks have no merged evidence package in this branch.

The exact blocker is therefore: **no approved, identity-pinned, rights-cleared
Krisp entitlement and runtime, and no rights-cleared processed data or vendor
output.** Missing artifacts are not downloaded, reconstructed, mirrored,
substituted or inferred from adjacent commercial-vendor, open-model or
Voice-Isolation evidence.

Eight open blockers:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Approved Krisp licence and entitlement for the exact NC/BVC SDK, with scope, duration, seats, permitted use and key reference. |
| `BLK-02` | The exact product release and platform build: SDK version, ABI, install layout, byte counts, SHA-256 values and a signed artifact manifest. |
| `BLK-03` | The exact noise-cancellation and background-voice-cancellation model bundles, selected family, sample-rate profile, CPU tier or on-request MAX model, each with a digest. |
| `BLK-04` | A locked offline host runtime with exact OS, interpreter/SDK versions, packages, device, determinism settings and install digest. |
| `BLK-05` | Reviewed vendor evaluation, telemetry, data-handling, retention, offline, deployment, redistribution, attribution and output-use terms. |
| `BLK-06` | A frozen isolation contract: model selection, other features disabled, mono channel layout, rate/frame/hop/reset/drain and state behavior. |
| `BLK-07` | A rights-cleared input cohort with consent and vendor-processed output produced on the approved runtime. |
| `BLK-08` | Separated local-runtime, vendor-output-scoring and vendor-claim results with controls, baseline, paired metrics, preservation, peaks, invalid outputs, unpaired screen or listening, alignment, state, memory and measured timing. |

**Reopen condition.** A caller supplies approved entitlement, the exact release
and platform artifact with verified identity and rights, a locked offline
runtime, the frozen isolation contract, a rights-cleared cohort, vendor
outputs, separated scoring/claim records, and an opt-in OFF-by-default provider
intake with independent exact-head review. Until then this task stays `DEFER`.

## Vendor boundary

| Property | Reported by source | Verified here |
| --- | --- | --- |
| Vendor | Krisp | Name only; no legal entity or terms record |
| Product | Noise Cancellation / Background Voice Cancellation SDK | Name only; no release identity |
| Noise cancellation | Versioned outbound/inbound models | Not mapped, loaded or executed |
| Background voice cancellation | Competing-voice model family | Not mapped, loaded or executed |
| Sample-rate profiles | Multiple, unspecified | No rate list, frame, hop or resampling policy |
| CPU tiers | Reported | No measured resource profile |
| On-request MAX models | Reported | Not requested, present or identified |
| Access | Licensed SDK only | Not approved; no key present |
| Telemetry / deployment terms | Not reported | Not documented or reviewed |
| Latency / timing | Low-latency call SDK | No value reported; not measured |
| Processed data / output | Not reported | Absent |
| Source or model portability | Not a portability claim | Explicitly out of scope |

The installed v0 geometry is unchanged at 16 kHz, mono, float32, 160 samples
per frame. It is not a Krisp path, and no vendor rate, frame, channel or drain
mapping is asserted.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row requires identity/noisy control
and a task-matched baseline; paired SI-SDR and STOI where permitted clean
references exist; clean-speech preservation, peaks and invalid outputs; a
separately labeled predictive screen or authorized listening for unpaired
speech; and alignment, state, memory, content delay and availability timing for
the exact runtime. Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control | structural only | Synthetic passthrough at v0 geometry; no candidate. |
| Task-matched baseline | blocked | No established local baseline run. |
| Paired SI-SDR and STOI | blocked | No licensed output or permitted clean set. |
| Clean-speech preservation | blocked | No real candidate output. |
| Peaks and invalid outputs | structural only | Synthetic validity accounting only. |
| Unpaired predictive screen or listening | blocked | No screen or authorized panel. |
| Alignment, state, memory | blocked | No vendor runtime or device clock. |
| Content/availability timing | blocked | No paced vendor runtime measurement. |

## What this package verifies

1. **Absence evidence.** Twenty-two fixed workspace, SDK-worktree and home-cache
   probes are checked without a recursive walk. All are absent, and the report
   builder plus `verify.py` fail if any later appears.
2. **Asset-register absence.** The pinned register is parsed strictly: 20
   candidates, no Krisp or NC/BVC entry. No release or artifact identity is
   invented.
3. **Stable pins and digests.** Every source and boundary input is pinned by
   SHA-256; `SOURCES.sha256` covers every task-local file except itself.
4. **Stable board identity.** Only `id`, `title`, `component`, `depends_on`,
   `mode`, `repository`, `deliverable`, `acceptance`, `evidence` and
   `write_scope` are projected and gated. The mutable `plan/swarm/TASKS.json`
   bytes are never hashed; status, owner, claim, review, handoff, priority and
   history never enter canonical bytes.
5. **Fail-closed licensed-deployment validation.** A strict manifest requires
   exact product, semver-like release, platform, entitlement approval and ID,
   telemetry disclosure, noise-cancellation enablement, background-voice
   selection, other features disabled, mono geometry, an admitted rate,
   absolute paths, exact SHA-256 values and the licensed scope. Unknown or
   missing fields, duplicate JSON keys, nonfinite values, floats, booleans in
   numeric fields, unsafe or relative paths, unsupported rates, wrong product,
   wrong scope, unapproved entitlement, undisclosed telemetry, enabled extra
   features and false isolation are rejected before use. One synthetic schema
   control is accepted to prove the validator is not blanket-rejecting and
   remains `qualifies=false`, with files hashed from this package only and no
   vendor SDK imported or executed.
6. **Enhancement accounting control.** A deterministic synthetic noisy signal,
   an exact identity/noisy passthrough and an exact 0.5 gain control are
   generated at the public v0 geometry. Sample conservation, peak bounds,
   nonfinite rejection, exact rational energy ratios (`1` and `1/4`) and the
   160-sample frame mapping are checked. It is labelled
   `synthetic_enhancement_identity_and_energy_accounting_control_not_vendor_output`
   and is not vendor output or a metric result.
7. **Scope enforcement.** `verify.py` resolves the pinned base, fails closed if
   the repository is unavailable, and reports any branch-added path outside the
   task directory as out of scope.

## Fallback and disclosure

Without a licensed runtime, code or asset, the package can only:

- prove a fixed absence inventory and the absence of a local asset-register row;
- validate a caller-supplied licensed-deployment manifest for shape and
  internal consistency, without importing a vendor SDK, reading a key,
  resolving an install, loading a model or opening audio;
- disclose `DEFER` and `not_qualified` explicitly, with no score, ranking,
  latency, resource or quality claim.

The fallback produces **no** Krisp output. It cannot substitute for the vendor
runtime, a rights-cleared cohort, processed data or an approved scorer.

## Evidence classes kept separate

| Class | State |
| --- | --- |
| Local runtime result | Empty: no runtime present or executed |
| Vendor-output scoring | Empty: no output bundle, scorer or score |
| Vendor claim | Empty: no claim record; nothing verified |
| Synthetic schema/accounting control | Present, `qualifies=false`, not evidence |
| Sibling Krisp tasks | Not merged here; nothing inherited |
| Peer commercial-vendor evidence | Not inherited or pooled |
| Krisp Voice Isolation public benchmark | Different product, separate task, not inherited |

## Eight blocked release gates

All eight gates remain `blocked`:

1. `entitlement_and_access`
2. `exact_release_and_artifact_identity`
3. `runtime_admission`
4. `vendor_terms_and_data_handling`
5. `isolation_and_release_contract`
6. `rights_cleared_cohort_and_output`
7. `enhancement_evidence_and_separation`
8. `opt_in_provider_intake_and_release`

## Sibling context is not attributed

`research/cpp-library-krisp-benchmark-20261109.md` scores Krisp **Voice
Isolation 2.5** public outputs on its own 265-file corpus (default DNSMOS-C
3.815). That is a different product, a different task and a different evidence
class; the audio is not in this repository and no value is inherited. The
sibling tasks `SDK-KRISP-VOICE-ISOLATION-2-5`,
`SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING` and
`SDK-KRISP-ACCENT-CONVERSION` have no merged package in this branch. Hecttor,
Hume Octave, ai-coustics Quail/Rook, Desert Ant Labs Clear and H-GTCRN are
separate commercial-vendor or open-model blockers; their manifests, controls,
terms and scores are not Krisp evidence.

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK adapter remains blocked behind the gates.

## Files

- `reference.py` — stdlib-only absence/asset audit, licensed-deployment
  manifest, synthetic enhancement accounting control and report/contract model.
- `run.py` — regenerates `contract.json`, `report.json`, its SHA-256 sidecar and
  `SOURCES.sha256` three times and requires byte-identical output.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `test_reference.py` — Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three independent cold-start regenerations.
- `LICENSES.md`, `*.json.license`, `*.sha256.license` — licensing and SPDX
  sidecars for generated artifacts.

Canonical report SHA-256:
`6d4a02614b3018454026a9a18672dde9eece2ff98d7f51aa85d8b3a98adeaa4a`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

`run.py all` performs three cold writes and requires all four artifacts to be
byte-identical. `verify.py` re-runs three independent cold-start regenerations
in scratch trees and fails on any pin drift, out-of-scope change, missing
sidecar, missing SPDX header or absent blocker. It also gates the branch diff
against the pinned base so committed out-of-scope files cannot pass.

## Non-claims

No Krisp SDK, entitlement, model, runtime or output is used. No denoising,
background-voice cancellation, SI-SDR, STOI, DNSMOS, PESQ, WER, latency, memory,
RTF, device timing, listening, benchmark or release result is claimed. The
audit is a fixed-path presence and file-hash observation only. Missing evidence
never qualifies this candidate.
