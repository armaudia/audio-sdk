<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-PHASE-LOCKING-PHASE-VOCODER - Phase-locking phase vocoder blocker

Task-local, **proposal-only**, **incomplete**, **not qualified** evidence for
`phase-locking-phase-vocoder`. Profile: **Rate**. Decision: **DEFER** before
`opt_in_adapter_exposure`. `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. Missing/blocked/rejected results never
qualify.

## Exact blocker

The task requires a runnable source, exact assets, permitted scope, task
geometry, and matched evidence; then a minimal reference compared against the
baseline phase vocoder at identical ratios. No exact licensed phase-locking
phase vocoder source/reference, immutable revision, license text/notice, pinned
offline runtime, rights-cleared inputs, deterministic candidate output, or
identical-ratio baseline comparison is present or reproducible in this
worktree. No artifact was downloaded, copied, vendored, imported, loaded, or
executed.

Sibling evidence reviewed: `docs/task-evidence/phase-vocoder-baseline/` (defer,
synthetic offline baseline comparison; no installed/public playback actuator)
and other TSM task packages under `docs/task-evidence/` remain separate and
unpooled.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch / base | `swarm/SDK-PHASE-LOCKING-PHASE-VOCODER`, `d0972e776bdc1ff231298caef1845cd1432c78be` |
| Task mode | `feasibility` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before opt-in adapter exposure |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Provider/default/ABI/registry/shared build/CI | no change |

## Rate profile (all blocked / not qualifying)

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | blocked | No candidate/runtime/output. |
| Duration | blocked | No candidate/runtime/output. |
| Pitch | blocked | No candidate/runtime/output. |
| Transient audibility / listening | blocked | No candidate/runtime/output or authorized listening. |
| Playback buffering / fill/flush / deadline | blocked | No runtime/device/scheduler measurement. |
| 1x identity control | blocked | No candidate/baseline comparison at identical ratios. |
| Rate changes | blocked | No candidate/baseline comparison at identical ratios. |
| Unfamiliar speech | blocked | No rights-cleared input. |
| Music + synthetic music negative control | blocked | No rights-cleared input. |
| Silence / empty input | blocked | No candidate/runtime/output. |
| Rebuffer, drift, final partial window | blocked | No playback/runtime measurement. |
| Pause/filler tied to source timestamps; speech preservation | blocked | No speech/VAD/preservation result. |
| Separate evidence categories | documented | Source-reported, synthetic envelope, admission, and missing-real sections are separate; none pooled. |

## Synthetic envelope and admission (protocol plumbing only)

Deterministic integer position envelope only: 16 kHz mono, 19200-sample frozen
input, exact integer `target=(input*denominator)//numerator` and
`source=(output*numerator)//denominator` for 1/1, 5/4, 3/2, 4/5, 9/10. It is
**not** phase-locking phase vocoder, not audio synthesis, not a baseline
comparison, and not qualification.

Measured synthetic observations (all unqualified): 5 envelope cases; 49 invalid
manifest rejections; 9 strict-JSON rejections; 14 absence probes, all absent;
7 evidence snippets present; 0 real candidate results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| RG-01 source revision and license provenance | blocked | Stage exact reference at immutable revision with complete license/notice/README and independent review. |
| RG-02 pinned runtime and offline install | blocked | Provide locked offline runtime with hashes, install location, clean-room import digest. |
| RG-03 exact task geometry and phase-locking mode | blocked | Pin window/hop, phase-locking mode, transient handling, latency/reset/drain, rate schedule semantics. |
| RG-04 rights-cleared inputs and terms | blocked | Freeze permitted digest-pinned inputs with code/license/evaluation/derived-output/redistribution decisions. |
| RG-05 reference execution and output validity | blocked | Execute pinned candidate offline with output hashes, finite/length preservation, exact repeats, peak/RSS. |
| RG-06 Rate profile against baseline phase vocoder | blocked | Run every Rate-profile case on rights-cleared inputs against baseline phase vocoder at identical ratios. |
| RG-07 mode/platform timing/resources/listening | blocked | Measure mode/platform timing/resources/pacing and complete authorized listening or labeled screen. |
| RG-08 provider intake/public surface/release | blocked | Separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after prior gates clear. |

## Reproduction

```sh
export PYTHONDONTWRITEBYTECODE=1
D=docs/task-evidence/phase-locking-phase-vocoder
python3 -m unittest discover -s "$D" -p test_reference.py -v
python3 "$D/run.py"
python3 "$D/verify.py"
```

`run.py` regenerates `contract.json`, `report.json`, `report.json.sha256`, and
`SOURCES.sha256` 3x and fails on non-identical bytes. `verify.py` is read-only
and checks strict JSON, pins, sidecars, admission/absence suites, scope, and a
cold-start 3x regeneration.
