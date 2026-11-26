<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-PBSHIFT — pbshift DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`pbshift` (`component_id=pbshift`, `SDK-PBSHIFT`). Structured inventory assigns
the **Rate** acceptance profile (`verification_profile: rate`). Machine-readable
decision: **`DEFER`**; `status=incomplete`; `proposal_only=true`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, build, execute, download, benchmark, or
qualify pbshift or any runtime. It pins source-reported provenance, proves
exact licensed source/runtime/rights artifacts are absent, reproduces only
declared synthetic duration/pitch arithmetic controls, and records exact
blockers. Only `docs/task-evidence/pbshift/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board, or
handoff file changes.

## Exact blocker

Pinned candidate note (`cpp-library/pipeline-validation/playback-speed-candidates.md`)
reports pbshift as MIT, C++17, streaming pull API, 0.25-4x, automatable rate,
pitch-synchronous voice path, vendor-reported 56-64 ms Live latency at 48 kHz,
and explicitly marks it **pre-1.0, 2 stars, self-reported metrics, not
independently tested**. That is source-reported provenance, not an admitted
implementation, license review, measurement, or qualification.

| Required artifact | Recorded local state |
| --- | --- |
| Pinned pbshift source/revision | No source tree, revision, tree digest, or immutable checkout |
| LICENSE/NOTICE + dependency terms | No reviewed license/notice bundle; MIT claim not verified |
| Pinned build/runtime manifest | No build, host profile, lockfile, or offline runtime manifest |
| Official API/geometry contract | No authoritative feed/available/read, rate-change, final-partial, channel/rate contract |
| Measured playback trace | No 1x/rate-change/duration/rebuffer/drift/final-partial measurement |
| Rights-cleared cohort | No consented speech/music/silence cohort or output-use terms |
| Pitch/transient/preservation scoring | No scorer, labels, or independent listening |
| Target-device timing/resources | No device timing, CPU/memory, or real-time pacing evidence |
| Opt-in provider intake/release | No provider registration, default, intake, or release review |

## Scope and invariants

- Work confined to `docs/task-evidence/pbshift/`.
- Installed v0 stays 16 kHz / mono / float32 / 160 samples. No provider is
  registered, exposed, or default-enabled.
- Deterministic, stdlib-only, default OFF, unregistered, not a provider.
- No real audio, listening, network download, target-device timing, pitch
  measurement, benchmark, or release qualification. Every signal is synthetic.
- Missing, invalid, nonfinite, out-of-range, stale, unapproved, and
  missing-artifact cases fail closed. No missing result may qualify anything.
- Source-reported provenance, synthetic arithmetic, and declared boundary are
  never pooled.

## Declared synthetic controls (not evidence)

`reference.py` provides deterministic synthetic duration/pitch arithmetic and
frame/admission validation only. It is `synthetic_contract_control_not_evidence`
and does not run pbshift.

| Control | Source | Rate | Preserve pitch | Output duration | Pitch ratio | Identity |
| --- | ---: | ---: | --- | ---: | ---: | --- |
| `identity_1x_preserve` | 16000 | 1 | true | 16000 | 1 | yes |
| `identity_final_partial_preserve` | 16165 | 1 | true | 16165 | 1 | yes |
| `faster_3_2_preserve` | 16000 | 3/2 | true | 32000/3 | 1 | no |
| `slower_3_4_preserve` | 16000 | 3/4 | true | 64000/3 | 1 | no |
| `varispeed_5_4_unpreserved` | 16000 | 5/4 | false | 12800 | 5/4 | no |
| `rate_change_schedule` | 16000 | 1→3/2→3/4 | true | 52000/3 | 1 | no |

Frame controls reject NaN/Inf/bool/string/None/short/long/empty/out-of-range/nested/non-list
with exact codes and `state_unchanged=true`.

## Rate profile outcomes (all blocked)

All Rate requirements are blocked: 1x control; source/output mapping and rate
changes; duration identity/error; pitch; transient audibility; playback
buffering/rebuffer/drift; unfamiliar speech/music/silence; final partial window
and speech preservation.

## Release gates (all blocked)

RG-01 pinned source and license; RG-02 pinned build and API/geometry contract;
RG-03 measured deterministic traces; RG-04 rights-cleared playback cohort;
RG-05 pitch/transient/preservation scoring; RG-06 rate acceptance profile;
RG-07 target-device timing and resources; RG-08 opt-in intake and release.

## Reproduction

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, and
`SOURCES.sha256` three times and requires byte-identical output. The mutable
full `plan/swarm/TASKS.json` is never hashed; only the stable linked-row
projection is read and gated.
