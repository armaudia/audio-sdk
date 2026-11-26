<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PYANNOTE-DIARIZATION - pyannote diarization blocker

Task-local, **proposal-only**, **incomplete**, **not qualified** evidence for
`pyannote-diarization`. Profile: **Spatial**. Decision: **DEFER** before
opt-in adapter exposure. `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing/blocked/rejected/source-reported
results never qualify.

## Exact blocker

The task requires a runnable source, exact assets, permitted scope, task
geometry, and matched evidence; then reproduction of the exact model/runtime as
a caller-supplied-asset reference and an opt-in SDK adapter only after
prerequisites pass. No exact licensed pyannote diarization source, immutable
revision, model weights, Hugging Face/access terms, pinned offline runtime,
rights-cleared diarization corpus, RTTM/UEM/reference labels, or deterministic
DER/JER/timing result is present or reproducible in this worktree. No
artifact was downloaded, copied, vendored, imported, loaded, or executed.

Anonymous speaker IDs must remain separate from verification/identity. Sibling
evidence reviewed: `docs/task-evidence/survey-spk-04/` (category survey,
DEFER/incomplete/not_qualified) is adjacent taxonomy context only; its records
are not pooled into this task's qualification.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch / base | `swarm/SDK-PYANNOTE-DIARIZATION`, `80dc1fb371e1846a5d50f5b28c955ab92bfcbe46` |
| Task mode | `feasibility` |
| Acceptance profile | `spatial` |
| Decision | `DEFER` before opt-in adapter exposure |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Provider/default/ABI/registry/shared build/CI | no change |

## Spatial profile (all blocked / not qualifying)

| Required item | State | Evidence |
| --- | --- | --- |
| Geometry/layout/timestamp calibration and task scope | blocked | No candidate/runtime/corpus/reference. |
| Anonymous speaker-label timeline; overlap represented | blocked | No candidate/runtime/output; anonymous IDs must not be enrolled identities. |
| Task-matched held-out labels on scored regions | blocked | No rights-cleared corpus/reference. |
| DER/JER or task-matched speaker-error metrics | blocked | No candidate/runtime/reference/metric run. |
| Leakage/false alarm, missed speech/target damage, condition changes | blocked | No candidate/runtime/output. |
| Online revision behavior/finalization if claimed | blocked | No candidate/runtime/output. |
| Silence/empty and invalid/nonfinite handling | blocked | No candidate/runtime/output. |
| Mode/platform timing, resources, pacing, device behavior | blocked | No runtime/device measurement. |
| Separate evidence categories | documented | Source-reported, synthetic envelope, admission, and missing-real sections are separate; none pooled. |

## Synthetic envelope and admission (protocol plumbing only)

Deterministic synthetic timestamped anonymous speaker-label intervals only:
16 kHz mono, 19200-sample synthetic duration metadata, anonymous `spk_XX`
labels, overlap represented in the overlap case. It is **not** diarization,
not DER/JER, not speaker identity, not audio synthesis/processing, and not
qualification.

Measured synthetic observations (all unqualified): 4 envelope cases; 40
invalid manifest rejections; 9 strict-JSON rejections; 14 absence probes, all
absent; 7 evidence snippets present; 0 real candidate results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| RG-01 source revision and license provenance | blocked | Stage exact upstream pyannote source/model card at immutable revision with complete license/notice/attribution and independent review. |
| RG-02 pinned assets and offline runtime | blocked | Provide reviewed access terms, caller-supplied asset manifest, and locked offline runtime with hashes and clean-room import digest. |
| RG-03 exact task geometry and scope | blocked | Pin sample rate/channels/windowing/latency/reset behavior and preserve anonymous speaker labels separate from verification/identity. |
| RG-04 rights-cleared corpus and references | blocked | Freeze reviewed rights-cleared inputs/references with RTTM/UEM/scored regions and acquisition/evaluation/derived-output/redistribution decisions. |
| RG-05 deterministic execution and output validity | blocked | Execute pinned candidate offline and record deterministic output hashes, finite/valid timelines, exact repeats, and peak/RSS/resource bounds. |
| RG-06 Spatial profile and diarization metrics | blocked | Run every required Spatial-profile case on rights-cleared inputs with task-matched labels, overlap representation, anonymous IDs separate from verification, and controls. |
| RG-07 mode/platform timing/resources/listening | blocked | Measure each mode/platform separately with timing, resources, pacing, and complete authorized listening or labeled screen where required. |
| RG-08 provider intake/public surface/release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after prior gates clear. |

## Reproduction

```sh
export PYTHONDONTWRITEBYTECODE=1
D=docs/task-evidence/pyannote-diarization
python3 -m unittest discover -s "$D" -p test_reference.py -v
python3 "$D/run.py"
python3 "$D/verify.py"
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, and
`SOURCES.sha256` 3x and fails on non-identical bytes. `verify.py` is read-only
and checks strict JSON, pins, sidecars, admission/absence suites, scope, and a
cold-start 3x regeneration.
