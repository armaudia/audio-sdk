<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-AUDIOTK — AudioTK blocker and supporting-DSP audit

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **feasibility, blocker and supporting-DSP reuse
package** for inventory component `audiotk` (Rate and content, verification
profile `rate`, mode `research-control`). The exact licensed AudioTK source,
resolved revision, build record, runtime, licence grant, rights record,
supporting-DSP plan, rate cohort and parity vector are absent. It creates **no
new execution, build, provider, processor, ABI, default, registry, shared
build, CI, board, handoff or release change**.

Task owner: `agent-AUDIOTK`; reviewer: `reviewer-AUDIOTK`. Claim base: audio-sdk
`d7f51ea0800508ee36c4ea1a90e07f3127bf1e02`; branch `swarm/SDK-AUDIOTK`. The
task depends on `SDK-FND-AUDIT` and `SDK-FND-EVIDENCE`; write scope is the
task-local evidence directory only (`docs/task-evidence/audiotk/`).

## What the merged evidence records and what is missing

The pinned survey (`cpp-library/pipeline-validation/playback-speed-candidates.md`,
line 279) records exactly:

> **AudioTK** (BSD-3-Clause) — general DSP/filter toolkit. This pass did not
> identify a ready-made time-stretch stage in it, so it is not listed as a
> stretcher; it may still be useful for supporting DSP.

That is the whole merged identity: a name, a BSD-3-Clause string, a negative
time-stretch finding and a possible supporting-DSP role. It records no
repository URL, project URL, release, commit, artifact digest, build record,
API surface, filter list or runtime. No fixed path in this workspace contains
an AudioTK checkout, header, build, binary, licence file, rights record,
supporting-DSP plan, rate cohort or parity vector. Nothing is downloaded,
vendored, cloned or inferred from an invented URL. Consequently:

- source identity, artifact hashes and licence terms cannot be pinned;
- "BSD-3-Clause" is a **survey string, not a verified grant or notice review**;
- the absent time-stretch stage means AudioTK cannot be represented as a rate
  actuator, and no pitch or transient behaviour is invented;
- no AudioTK output exists, so no duration, pitch, transient, speech
  preservation, latency, RTF, listening or benchmark value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

## Proceed/defer decision

The task asks for a documented proceed/defer decision before exposing AudioTK
as a processor. The decision is **DEFER before `opt_in_provider_intake`** for
three independent reasons:

1. **No source or identity.** There is no checkout, URL, revision or digest to
   reproduce, so no reference can be implemented or pinned exactly.
2. **No rate capability.** The survey explicitly did not find a ready-made
   time-stretch stage. AudioTK remains a *possible* general DSP/filter toolkit,
   not a playback-rate actuator.
3. **No supporting-DSP reuse case.** A supporting-DSP decision needs a concrete
   filter surface, geometry mapping and a statement of why existing SDK DSP is
   insufficient. None of that exists.

The deferral does not reject AudioTK permanently. It records the exact
reopening conditions below and leaves the candidate unqualified.

## Supporting DSP reuse check

`reference.py::audit_supporting_dsp` performs fixed local reads only. It records
the installed SDK DSP inputs that could otherwise be confused with AudioTK
reuse:

- `core/providers/highpass/highpass_provider.c` and its config;
- `core/providers/speex/speex_provider.c` and its config;
- the vendored `third_party/speexdsp` licence;
- `docs/provider-intake.md` and `docs/provider-v0.md`.

It also records the merged sibling rate packages (aubio, Bungee Basic,
Signalsmith Stretch, Sonic, SoundTouch) as
`sibling_rate_evidence_not_attributed`. The reuse decision is
`no_audiotk_reuse`: those inputs are separate provenance, are not AudioTK
filters, are not measured here, and do not establish AudioTK suitability. No
SDK DSP file was compiled, linked, modified or re-attributed. No AudioTK filter
was built, so there is no supporting-DSP result to qualify.

## Evidence classes and boundaries

- **Merged survey metadata:** one pinned line and the inventory record
  (`plan/INVENTORY.json`) with profile `rate`, disposition `research-control`
  and the plan note. This is provenance, not execution.
- **Sibling maps:** the merged rate packages and the existing SDK DSP
  providers are context only. They contribute no AudioTK source or result.
- **Synthetic accounting:** the task-local control generates deterministic
  synthetic PCM at 16 kHz mono and performs exact rational arithmetic on a
  declared rate plan: 1x identity, scalar rate values, a four-segment rate
  schedule, duration ratios, final-partial-window accounting and
  source-anchored pause/filler intervals. It performs **no time-scale
  modification, pitch shift, transient processing, rendering, listening or
  device timing**, and is never AudioTK output.
- **Not present:** real speech, music, silence, rebuffer or drift material,
  AudioTK source, build, runtime, actual output, pitch/transient/speech
  measurement, listening, device timing, public benchmark or release approval.

The failure envelope is explicit: declared arithmetic does not prove pitch
preservation; a 1x copy is not a stretcher; an interval ratio is not a quality
or availability result; and the absent source/stage means neither parity nor
suitability can be evaluated.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex revision, canonical upstream URLs, source/artifact hashes and licence at exact pins | blocked |
| `runtime_admission` | Isolated, hash-pinned C++ build and runtime with a reproducible toolchain/dependency record | blocked |
| `artifact_rights_and_licence` | BSD-3-Clause notice, output-use, redistribution and cohort rights verified with notices | blocked |
| `exact_reference_parity` | Approved exact-runtime AudioTK output matches a frozen caller input and configuration | blocked |
| `rate_cohort_and_scoring` | Rights-cleared matched cohort scores mapping, duration, pitch, transient audibility and playback buffering | blocked |
| `task_scope_and_supporting_dsp_reuse` | Supporting-DSP-only role, exact filter surface, geometry and absence of a ready-made time-stretch stage documented | blocked |
| `opt_in_provider_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision | blocked |
| `public_default_and_release` | Explicit default selection, paced resource/deadline evidence and release or benchmark approval | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source checkout, unpinned upstream identity, absent
build/runtime record, unverified BSD-3-Clause grant and rights, absent
time-stretch stage, absent supporting-DSP reuse plan, absent rate geometry and
cohort, and absent parity/benchmark evidence. All eight `rate` profile
requirements are unsatisfied for qualification; two are explicitly
synthetic-accounting-only, three are structural-only, three are absent, and
none has a qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing,
building, linking or executing anything. It requires absolute paths and
lowercase SHA-256 values for the licence, rights record, runtime lock, build
record, supporting-DSP plan, rate cohort and parity vector; a full 40-hex source
revision; mono geometry; an admitted sample rate; canonical non-exponential
rate bounds that include 1x; the `supporting_dsp_only_offline_comparator`
variant; and `claimed_time_stretch_capability=false`. A manifest that claims a
time-stretch capability is rejected because the survey did not establish one.
Any missing, malformed, nonfinite, out-of-range, mismatched or relative input is
rejected before processing. No upstream revision is pinned, so a shape-valid
manifest cannot manufacture qualification.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path
  absence/source/build audit, supporting-DSP reuse audit, caller manifest
  validation, exact rate accounting and 46 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers and the caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK boundary files
  and package files. The mutable full `plan/swarm/TASKS.json` is **never
  hashed**; only the stable linked-row fields are projected to a digest.
- `run.py` — byte-identical regeneration of report, contract and sources.
- `test_reference.py` — canonical output, identity, audit, supporting-DSP,
  rate-schedule, duration, final-window, pause-policy, PCM, manifest and
  adverse-rejection tests.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/audiotk
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
git diff --check
```

JSON, digest and manifest files have SPDX `Apache-2.0` sidecars. All files are
inside this task directory; board, handoff and reviewers were not changed or
dispatched. No merge, formal approval or release action is taken. Workspace
pins are SHA-256 values of read-only documents; a pin grants no rights and
verifies no media. `SOURCE_ROOT` can point to the enclosing `audioml` checkout
if automatic discovery is unavailable.
