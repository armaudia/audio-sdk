<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CLEARSCALE — ClearScale rate/TSM blocker

**Disposition: `DEFER` / `proposal_only_incomplete` / `not_qualified`
(evidence `incomplete`).** This package is a
bounded, deterministic **feasibility and blocker package** for inventory
component `clearscale` (Rate and content, verification profile `rate`,
disposition `research-control`). The exact licensed ClearScale source, resolved
revision, binary/implementation artifact, licence/status, rate geometry,
runtime, rights record, cohort and parity vector are absent. It creates **no
new execution, TSM implementation, model, corpus, real audio, provider,
processor, ABI, default, build, CI, board, handoff or release change**.

Task owner: `agent-CLEARSCALE`; reviewer: `reviewer-CLEARSCALE`. Claim base:
audio-sdk `38f502b8e67a4cfef7dd72425aae6b0044846aad`; branch
`swarm/SDK-CLEARSCALE`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is the task-local evidence directory only
(`docs/task-evidence/clearscale/`).

## What is missing and why no result can qualify

The merged research note contains one decisive ClearScale line:

> **ClearScale** — abandoned open-source predecessor of DIRAC; no usable
> current licence/status.

The same note says DIRAC is the legacy name for the DSP Dimension technology,
current licensing is through Zynaptiq, and old free binaries should not be
adopted without checking their terms. It records no current ClearScale project
URL, repository, revision, API, rate geometry, source, binary, coefficient
table, runtime, licence text, rights record, output or quality result.
ClearScale is a DSP time-stretch technology, **not a neural model**, so no
neural weight is applicable; the relevant artifact is the exact licensed
source or binary implementation and any coefficient table it needs.

No fixed path in this workspace contains a ClearScale checkout, resolved 40-hex
revision, implementation artifact, runtime environment, runtime lock, licence
record, rights record, output-use grant, cohort manifest or parity vector.
Nothing is downloaded, vendored, reconstructed or inferred. Consequently:

- source and implementation identity, artifact hashes and licence terms cannot
  be pinned;
- the abandoned-project status means no current licence, redistribution,
  derivative-output use, patent or commercial-use right can be assumed;
- the rate geometry (sample rate, channels, frame/hop, rate/pitch semantics,
  rate-change bounds, content delay, latency, final-padding rule, reset
  behavior) is not established; only the SDK v0 input boundary is asserted;
- no candidate output exists, so duration, pitch, transient, buffering,
  rebuffer, drift, final-partial, speech-preservation, SI-SDR, STOI, WER, MOS,
  latency, memory or RTF results are not reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

## Evidence classes and boundaries

- **Merged research metadata:** the pinned note's §3.14 exclusion line and §3.13
  DIRAC context; the component row in `plan/INVENTORY.json` (`blocked`);
  the `rate` acceptance profile in `plan/swarm/VERIFICATION.md`; and the
  audio-sdk implementation plan. These are provenance, not local execution.
- **Synthetic accounting:** the task-local control generates deterministic PCM
  at 16 kHz mono, declares exact rational rate schedules for 1x, 3/2, 2/3, a
  1→3/2→2/3 rate change and 7/4, and checks PCM validity, contiguous source
  coverage, exact source/output mapping, floor/ceil duration, cumulative drift,
  the final partial window, and nonfinite/invalid/missing rejection. It
  performs **no time-scale modification**, emits **no candidate audio** and
  asserts no pitch, transient, preservation, buffering or listening result.
- **Merged sibling packages:** SoundTouch, Bungee Basic, Bungee Pro,
  Signalsmith Stretch and the D1 duration planner are adjacent rate/TSM
  evidence; AudioSR (diffusion restoration) and GTCRN (enhancement) are
  adjacent restoration/enhancement blockers. None is ClearScale, none contains
  ClearScale output, and none is used as a parity oracle. Their own statuses
  remain proposal-only or `DEFER` with no qualification effect here.
- **Not present:** real speech/music/silence, a pinned ClearScale source,
  implementation binary, coefficient table, licence, rights record,
  output-use grant, frozen cohort, parity vector, runtime invocation, human
  listening, device timing, public benchmark or release approval.

The failure envelope is explicit: a synthetic rational mapping is not a TSM
engine; a name match to an abandoned library is not a source, licence or
runtime; and the absent source, rights and cohort mean neither pitch-preserving
speed control nor playback suitability can be evaluated.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, exact implementation/coefficient hashes and source licence match exact pins | blocked |
| `runtime_admission` | Isolated hash-pinned runtime, compiler/link mode and platform recorded | blocked |
| `artifact_rights_and_licence` | Abandoned-status, ownership, source/binary, redistribution, derivative-output, patent and commercial rights cleared | blocked |
| `task_geometry_and_rate_semantics` | Exact rate/pitch/rate-change, content-delay, latency, final-padding and reset geometry pinned | blocked |
| `rate_cohort_and_scoring` | Rights-cleared held-out cohort covers 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window | blocked |
| `quality_and_playback_timing` | Duration/pitch/transient/preservation and peaks/alignment are measured; device pacing, deadlines and resources measured separately | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence and descriptor review, public-surface decision; optional only | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release/benchmark approval; off by default | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source, unusable licence/status, absent implementation
artifact, unestablished geometry, absent runtime, uncleared rights/output-use,
absent cohort/parity, and absent quality/timing/release evidence. All ten
`rate` profile requirements are unsatisfied for qualification; two are
structural-only, one is synthetic-only, two are not-measured and five are
absent, and none has a qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the implementation artifact, config, runtime lock, licence record, rights
record, cohort manifest, parity vector and output-use grant; a full 40-hex
source revision; exactly 16 kHz mono with 160-sample frames; and the declared
variant `clearscale_pinned_time_scale_modification`. Any missing, malformed,
nonfinite, out-of-range, mismatched or unapproved variant is rejected before
processing. No upstream revision is pinned because the merged evidence records
only an abandoned project; a shape-valid manifest cannot manufacture
qualification.

## Rate-profile reporting

The package reports the rate profile but qualifies none of it:

- source/output mapping and duration are structural-only;
- 1x, rate changes, unfamiliar speech, music, silence, rebuffer, drift and the
  final partial window are not run on a candidate;
- pitch and transient audibility are not measured;
- speech, consonant and intelligibility preservation are not measured;
- playback buffering, fill/flush, device pacing and deadlines are absent;
- rate decisions are tied to source timestamps only in the synthetic declared
  schedules;
- no quality, listening or benchmark result is claimed.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path asset
  audit, caller manifest validation, synthetic PCM/rational rate accounting and
  53 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers and the caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK boundary files,
  merged sibling packages and package files. The mutable full
  `plan/swarm/TASKS.json` is **never hashed**; only the stable linked-row
  fields are projected to a digest.
- `run.py` — byte-identical regeneration of report, contract and sources.
- `test_reference.py` — canonical output, identity, audit, manifest, PCM, rate,
  accounting, report and adverse-rejection tests.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/clearscale
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

JSON, digest, manifest and contract files have SPDX `Apache-2.0` sidecars. All
files are inside this task directory; board, handoff and reviewers were not
changed or dispatched. No merge, formal approval or release action is taken.
Workspace pins are SHA-256 values of read-only documents; a pin grants no
rights and verifies no media. `SOURCE_ROOT` can point to the enclosing
`audioml` checkout if automatic discovery is unavailable.

## Exact blockers and reopening conditions

This package does **not** close the conditional implementation. Reopen only
when all of the following are supplied and independently reviewable:

1. An exact ClearScale source checkout or licensed binary at a full 40-hex
   revision, with per-file SHA-256 values and any coefficient tables.
2. A current licence and project-status record covering copyright ownership,
   source/binary terms, redistribution, derivative-output use, patent status
   and commercial use; the abandoned status is resolved, not assumed.
3. The exact task geometry: 16 kHz mono 160-sample input plus rate/pitch
   semantics, rate-change bounds, frame/hop, content delay, latency,
   final-padding rule and reset behavior.
4. An isolated hash-pinned runtime and lock on a recorded platform, including
   exact compiler, link mode and instruction-set assumptions.
5. A rights-cleared held-out cohort and parity vector covering 1x, rate
   changes, unfamiliar speech, music, silence, rebuffer, drift and the final
   partial window, with known failures and controls.
6. Authorized evaluation of duration, pitch, transient audibility, speech
   preservation, peaks, nonfinite failures, alignment, buffering, deadlines,
   memory, CPU and listening where permitted.
7. Explicit opt-in provider intake, descriptor and licence review, an OFF
   default, and an independent public-surface decision.
8. Release or public-benchmark approval with target-device resource/deadline
   evidence and review at the exact head.

No result in this package qualifies the candidate. No provider, descriptor,
registry, installed v0 path, default, shared build, CI, board or handoff is
changed. No merge, formal approval or release action is taken.
