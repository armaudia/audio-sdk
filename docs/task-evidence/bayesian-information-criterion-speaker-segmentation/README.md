<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility, blocker and synthetic-arithmetic
package** for inventory component
`bayesian-information-criterion-speaker-segmentation` (category `SPK-03`, legacy
family `F06`, verification profile `spatial`, mode `feasibility`). The exact
licensed implementation, source revision, runtime, licence/rights record,
annotated-meeting change corpus, task geometry, parity vector and benchmark are
absent. It creates **no new execution, provider, descriptor, registry, analysis
surface, ABI, default, shared build, CI, board, handoff or release change**.

Task owner: `agent-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION`;
reviewer: `reviewer-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION`.
Claim base: audio-sdk
`72a52fc65f0b6db703d22714b8f7305642e4b412`; branch
`swarm/SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION`; worktree
`/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-BAYESIAN-INFORMATION-CRITERION-SPEAKER-SEGMENTATION`.
The task depends on `SDK-FND-AUDIT`, `SDK-FND-EVIDENCE` and
`SDK-FND-PROVIDER`; write scope is the task-local evidence directory only
(`docs/task-evidence/bayesian-information-criterion-speaker-segmentation/`).

Canonical `report.json` SHA-256:

`daf1213b91b1887178ef50b9be4496c9b95c1407c78701d4910529f37c844023`

## What is present and what is missing

The merged evidence records the component as a **paper lead only**. The
category registry (`research/category_registry.json`, `SPK-03`) names
`S04` — *Speaker segmentation using the Bayesian information criterion* — and
the classic family “Adjacent-window statistics; Bayesian information criterion
(BIC)”. `S04` supplies a title and an ISCA URL. It supplies **no code
repository, commit, release, artifact digest, licence grant, feature front end,
window/hop/lookahead configuration, penalty, threshold, annotation schema,
runtime, build record or corpus**.

The merged sibling maps confirm the same boundary:

| Sibling package | What it records | Not attributed here |
| --- | --- | --- |
| `SDK-SURVEY-SPK-03` (`docs/task-evidence/survey-spk-03/`) | BIC row is `considered` only; no local implementation, change-point cohort or boundary score | Any speaker-change execution or result |
| `SDK-SURVEY-SPK-04` (`docs/task-evidence/survey-spk-04/`) | BIC segmentation is `considered`; anonymous labels and DER/JER are absent | Any diarization or speaker-label claim |
| `SDK-SURVEY-DET-01`, `SDK-ADAPTIVE-ENERGY-VAD`, `SDK-WEBRTC-VAD` | Adjacent any-speech VAD history exists | Speaker-change boundaries, segment purity or speaker identity |

No path in the workspace contains a BIC checkout, runtime, weights, licence
record, rights record, annotated `speaker-change-ami` corpus, adapter config,
parity vector or benchmark. Nothing is downloaded, vendored, cloned or inferred
from an invented URL. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- no upstream output exists, so no exact parity can be evaluated;
- no audio or annotated meeting is read, so no boundary, false-alarm, miss,
  segment-purity, diarization, identity, listening, device-timing, benchmark or
  release value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

## Task-local BIC reference and synthetic control

`reference.py` implements the classical adjacent-window BIC comparison in
stdlib-only exact rational arithmetic:

```text
D = N*ln|Sigma_pooled| - N1*ln|Sigma_left| - N2*ln|Sigma_right|
    - lambda*0.5*(d + d*(d+1)/2)*ln(N)
```

where `D > threshold` favours a change point. The task-local control uses
15-frame left/right windows, a 1-frame scan hop, 15-frame minimum segment
separation, 150 ms lookahead, `lambda = 1`, threshold `0` and a deterministic
score-descending, earliest-tie, minimum-separation suppression policy. It
operates on **caller-supplied 2-D synthetic feature vectors**. It does **not**
extract MFCCs, filterbank features or audio, and it is **not** an upstream
implementation.

The bounded synthetic control plants change points at frames 30 and 60 in a
90-frame, three-segment stream and recovers exactly `[30, 60]` with zero
synthetic false alarms and zero synthetic misses. A one-segment jittered stream
returns no change, and an identical-frame singular stream is rejected. These
are **arithmetic-control facts only**. They are not audio segmentation, meeting
false-alarm rates, speaker-change accuracy, segment purity, generalization or
parity with any upstream segmenter. `candidate_metrics` is entirely `null`.

The control is deliberately labelled:

- `metric_scope =
  "synthetic_feature_domain_not_a_segmentation_result"`;
- `not_audio = true`, `not_speaker_evidence = true`,
  `qualifies_candidate = false`;
- `candidate_metrics.derived_from_synthetic_control = false`.

## Adapter boundary and task geometry

The SDK v0 boundary is preserved at 16 kHz, mono, float32 and 160 samples per
frame. BIC speaker segmentation is an **annotation** output, not a waveform
processor, and v0 has no public analysis-event surface. The versioned
analysis-events contract is proposal-only. Therefore this package adds no
provider, descriptor, event bus, registry entry, default or shared adapter. Any
future exposure would be an offline annotation adapter that validates a
caller-supplied manifest, not a registered v0 provider.

The real task geometry is **unestablished**: feature front end, window, hop,
lookahead, penalty, threshold, minimum segment, merge policy, annotation schema,
availability policy and collar/unknown-region policy are all `null` in the
report. The declared control geometry is reproducible test scaffolding only.
`contract.json` fixes the caller-asset shape: absolute paths, exact SHA-256
values, a full nonzero 40-hex source revision, the
`bic_offline_annotation_adapter` variant, 16 kHz mono, 160-sample frames and a
positive canonical-decimal penalty. A structurally valid manifest is
**explicitly not qualification**; every submission remains `not_qualified`.

## Failure envelope and adverse controls

The merged historical evidence is adjacent at best:

- AMI any-speech VAD comparisons report speech/nonspeech misses and false
  alarms, not speaker-change truth;
- positive-only audEERING spans have an unknown complement;
- Hush AMI speaker-pair mixtures are synthetic constructions, not natural
  speaker turns;
- sibling survey maps contain no BIC execution or segment-purity row.

The task-local reference therefore rejects, rather than guesses:

- empty, non-sequence, non-numeric, boolean, string, out-of-range,
  wrong-dimensional, NaN and ±Infinity features;
- singular or non-positive covariance, too-short windows/streams, zero hop,
  negative penalty, non-finite threshold and minimum segment below window;
- missing/extra manifest fields, relative or traversing paths, malformed
  SHA-256, short/non-hex/zero revisions, wrong variant, false capability,
  wrong channels/rate/frame size, non-integer geometry and exponent/zero
  penalty or threshold;
- duplicate JSON keys and `NaN`/`Infinity` JSON constants.

Forty adverse cases are retained in `report.json`; every one is `rejected`.

## Spatial acceptance profile

The inventory assigns the `spatial` profile. The profile still requires
geometry/layout, timestamp calibration, source/target/reference conditions,
permissions, task-matched held-out labels, leakage/target-damage/channel-loss
reporting and room/reference-condition reporting where applicable. For a
single-channel change-point annotation there is no array geometry, but the
geometry/clock/permission and task-matched held-out-label requirements still
apply. All profile rows are `measured: false`; no held-out annotated meeting,
RTTM/UEM reference, collar policy, scored region, split or permission exists.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Exact approved BIC source, canonical URLs, full 40-hex revision, per-file SHA-256 and source licence at immutable pins | blocked |
| `runtime_admission` | Isolated hash-pinned runtime and reproducible build record on a recorded platform | blocked |
| `artifact_rights_and_licence` | Verified implementation licence, notices, source/output use and annotated-meeting corpus rights with dated evidence | blocked |
| `exact_reference_parity` | Approved exact-runtime output matches a frozen caller input, feature configuration and annotation schema | blocked |
| `spatial_cohort_and_scoring` | Rights-cleared, speaker/session-disjoint annotated-meeting cohort scores boundaries, false alarms, misses, boundary deviation and segment purity | blocked |
| `task_geometry_and_adapter_boundary` | Feature front end, window, hop, lookahead, penalty, threshold, minimum segment, merge policy, annotation schema and adapter boundary fixed and reviewed | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review, optional-runtime absence behaviour and public-surface decision | blocked |
| `public_default_and_release` | Explicit default selection, paced resource/deadline evidence and release/benchmark approval; this package is off by default | blocked |

The eight exact blockers in `report.json` name the concrete missing artifact or
rights requirement: absent source checkout, unpinned upstream identity, absent
build/runtime record, unverified licence/rights, absent annotated-meeting
corpus and rights, unestablished task geometry/adapter, absent exact-parity
vector, and absent held-out benchmark/release record.

## Evidence classes and boundaries

- **Merged metadata:** the pinned inventory row, category registry row, source
  list, survey map and adjacent VAD packages. Provenance, not execution.
- **Task-local synthetic arithmetic:** exact rational BIC scoring and
  deterministic synthetic feature-stream detection. No audio and no speaker.
- **Adverse/control evidence:** structural rejection of malformed, missing,
  invalid, non-finite and overclaiming inputs.
- **Not present:** upstream source, runtime, weights, real audio, annotated
  meetings, speaker-change labels, RTTM/UEM, scorer, rights review, exact
  parity, listening, device timing, benchmark, release approval.

## Files and reproduction

| File | Role |
| --- | --- |
| `README.md` | Bounded disposition, scope, gates and reproduction |
| `contract.json` | Caller-asset, geometry, formula and non-qualification contract |
| `reference.py` | Stdlib-only deterministic pins, BIC arithmetic, controls and report builder |
| `run.py` | Byte-identical regeneration of report, sidecar, contract and source manifest |
| `report.json` | Machine-readable `DEFER` / `incomplete` / `not_qualified` evidence |
| `report.json.sha256` | Exact canonical report digest |
| `SOURCES.sha256` | Sorted SHA-256 pins for package, source and boundary files |
| `verify.py` | Read-only fail-closed recomputation, licensing, scope and 3x cold-start checks |
| `test_reference.py` | Acceptance, adverse, atomic-rejection and determinism tests |

```sh
cd docs/task-evidence/bayesian-information-criterion-speaker-segmentation
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

Expected: 48 tests pass; `run.py all` regenerates byte-identical artifacts;
`verify.py` prints `PASS decision=DEFER status=proposal_only_incomplete
qualification=not_qualified` with eight blocked gates and three byte-identical
cold-start repeats.

The mutable full board file `audio-benchmark-platform/plan/swarm/TASKS.json` is
**never hashed**. Only the stable linked-row identity (`id`, `title`, `mode`,
`component`, `repository`, `deliverable`, `acceptance`, `depends_on`,
`evidence`, `write_scope`, plus the claim pins) is projected into
`report.json`. Board status, owner, handoff, review and dispatch edits cannot
change this package's canonical bytes.

## Non-claims

No BIC or other speaker-change implementation is loaded, built, linked or
executed. No upstream URL, revision, release, digest, build record or licence
grant is invented. The `S04` paper lead is a method citation, not a source
checkout or rights grant. No network, download, real audio, annotated meeting,
change-point label set, RTTM/UEM reference or corpus is used. The synthetic
feature-domain control is not audio segmentation and does not qualify the
candidate. No speaker-change boundary, false-alarm, miss, segment-purity,
diarization, identity, listening, device-timing, benchmark or release result is
claimed. No provider, descriptor, registry, analysis event surface, installed
v0 path, shared build or CI changed.

## Reopen conditions

Reopen only when all eight gate requirements are satisfied by exact evidence:
the approved source and identity, a reproducible runtime/build, verified
licence and rights, exact-runtime parity, a rights-cleared held-out annotated
meeting cohort, a reviewed task geometry and annotation adapter, opt-in
provider intake, and explicit default/benchmark/release approval. A partial
submission remains `not_qualified`; missing evidence never creates a pass.
