<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WEBRTC-APM — rate-category feasibility blocker

**Decision: `DEFER` · status `proposal_only_not_qualified` · completeness
`incomplete` · qualification `not_qualified`.** This is a self-contained,
deterministic, task-local evidence package. It does **not** contain, download,
link, install, execute or wrap WebRTC APM. It makes no rate, audio-quality,
benchmark, device-timing, listening or release claim.

## Exact scope and boundary

- Installed v0 stays 16 kHz mono `float32`, 160 samples per frame. No C ABI,
  header, registry, descriptor, default, shared CMake, CI or installed behavior
  is changed.
- `reference.py` is the smallest verifiable **feasibility probe**, not an APM
  implementation. It performs strict 160-sample frame accounting, rejects
  invalid/missing/nonfinite requests, and records that APM has no rate-control
  surface. It produces no APM audio and never fabricates an actuator output.
- The probe is stdlib-only, deterministic and independent of the mutable board
  file. It never hashes `plan/swarm/TASKS.json`; only the stable linked-row
  identity is gated.
- No real speech, corpus, weights, model, wheel, binary, runtime, device timing,
  playback harness or listening panel is present.

## Why the task is blocked

The exact task evidence, `research/tsm-followup-20261101/README.md`, records:

> **WebRTC Audio Processing (APM)** — Echo/noise processing, gain, and related
> call processing — **Not a TSM executor.** Do not include as a time stretcher;
> a VAD component can be evaluated separately.

The task asks for the **rate** acceptance profile, whose required object is a
source/output rate actuator. WebRTC APM is a call-processing module (AEC/NS/
AGC/VAD) with a 1:1 10 ms frame boundary and no documented rate or time-scale
modification control. In addition, the workspace contains no licensed APM
source, wheel, binary or runtime:

- candidate workspace/worktree paths were probed and are absent;
- `webrtc_audio`, `webrtc_apm` and `pywebrtc_audio` are not importable;
- no `.wav`, model, wheel or native artifact is bundled here.

Because the exact licensed source/runtime/asset is absent, the package does not
invent a substitute. It records the exact missing artifact and rights
requirements and remains `DEFER`.

## Source pins

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. SHA-256 is
exact; a changed pin is a hard verification failure. The mutable full board is
**not** pinned or hashed.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Records APM as not a TSM executor and defines the rate-category blocker. |
| `research/tsm-followup-20261101/agent-stretchers/REPORT.md` | `8c738676e69f152696e74780546b8adca1100542676f3a0461fc71e94f5195cb` | Rate-pilot protocol context; no WebRTC APM run is inferred. |
| `adapters/webrtc-ns/README.md` | `8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992` | APM NS adapter boundary: 16 kHz mono, 10 ms framing, separate settings. |
| `adapters/webrtc-ns/adapter.json` | `42aac7a2a0f5709e24785eb87d5922fdd30cabadd54336604ff739dc70fa874a` | Integration-scope evidence only. |
| `adapters/webrtc-aec/README.md` | `c074f84c859dcfb2ac7414a775dbcddcf2f2646deca66810c9241fcf7adec050` | APM AEC boundary and measured content offset; not a rate control. |
| `plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence and task-local optional-reference policy. |
| `plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile applied below. |

Boundary pins (worktree-relative): `CONTRACTS.md`
`f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69`,
`api/include/audio_sdk/provider_v0.h`
`f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766`, and
`api/include/audio_sdk/session_v0.h`
`a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1`.

Merged sibling evidence is pinned by `report.json` and `contract.json` digests
for `webrtc-apm-ns`, `webrtc-aec3` and `webrtc-vad` in `contract.json` and
`report.json`. The linked task row is gated only by stable identity fields
(`id`, title, repository, mode, component, dependencies, evidence, base commit,
branch). The full mutable `TASKS.json` is never hashed into canonical bytes.

## Rate profile application

The rate profile is applied as a completeness/blocker checklist, not as a
quality claim. Every element is `blocked`, `analytic_only` or
`not_applicable`; none qualifies.

| Required element | Result |
| --- | --- |
| Source/output mapping, duration, pitch | Blocked: APM has no rate control or actuator output. |
| Transient audibility, speech preservation | Blocked: no actuator, rights-cleared cohort or listening panel. |
| Playback buffering, rebuffer, drift | Blocked: no playback harness or device clock. |
| 1× control | Analytic sample-count identity only; explicitly not an audio measurement. |
| Rate changes, 0.5×/2.5× extremes | Blocked: unsupported; extremes are retained as adverse, unvalidated results. |
| Unfamiliar speech, music, silence | Blocked: no rights-cleared held-out cohort. |
| Final partial window | Blocked: no rate output or playback harness. |
| Pause/filler decisions | Not applicable: no pause/filler controller is in scope. |

## Probe and failure controls

`run.py --request` implements a strict protocol-v1 request with exact candidate
and adapter references. Representative results:

- `identity_1x_boundary_accounting`: `analytic_identity_only`; in/out sample
  counts equal; `qualifies=false`.
- `rate_0_5x`, `rate_1_25x`, `rate_2_5x`: `blocked_unsupported_rate_control`;
  0.5× and 2.5× are additionally retained as adverse unvalidated extremes.
- `rate_1x`: `blocked_missing_licensed_runtime`; even 1× execution is blocked.
- `runtime_claim`, `cohort_claim`: explicit missing-runtime / missing-cohort
  blockers.
- partial frame, wrong type, nonfinite sample/rate, out-of-range input, rate
  range, unknown runtime/cohort and missing input: explicit `rejected_*`
  results, never scored or dropped.
- Strict JSON rejects duplicate keys, NaN/Infinity and non-object roots.

No missing or adverse result is promoted. All results carry `qualifies=false`.

## Eight blocked release gates

1. Pinned, hash-verified licensed APM source/runtime with LICENSE/NOTICE and
   execution approval.
2. A documented APM rate/time-scale control surface at the frozen geometry.
3. Rights-cleared matched speech/music/silence/rebuffer/drift cohort with exact
   timestamps and final partial windows.
4. Paired duration, pitch, transient and speech-preservation measurements.
5. Measured playback buffering, rebuffer, drift and end-padding behavior.
6. Target-device content/availability timing, memory and deadline budget.
7. Authorized listening or approved naturalness assessment.
8. Provider/catalog/license intake, descriptor/public-surface review and release
   approval.

All eight are `blocked`; none has evidence.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Pinned WebRTC APM source revision or `pywebrtc-audio==0.2.0` wheel/source with SHA-256 | Apache-2.0 LICENSE and NOTICE for the exact revision/binding, redistribution terms, and approval to execute the native runtime. |
| Documented APM rate/time-scale control | Upstream public API documentation for the exact revision. |
| Rights-cleared rate cohort (speech, music, silence, rebuffer, drift) | Written corpus rights for evaluation and derived outputs. |
| Playback/rebuffer/drift and device-timing harness | Harness license and target-device access approval. |

No download, fabrication or substitution was attempted.

## Reproduction

Run from this directory on the pinned worktree:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
```

`run.py --report` builds the report three times and writes only byte-identical
output; `verify.py` separately launches three cold starts for `--report`,
`--sources` and `--inspect`, checks exact external/boundary/sibling/local pins,
the stable linked row, canonical bytes, eight blocked gates, all adverse/
missing/invalid/nonfinite controls, SPDX annotations, dependency hygiene and
task-local scope containment. JSON is canonical (`sort_keys=True`, compact
separators, `allow_nan=False`) with one trailing newline.

Report digest: see [`report.json.sha256`](report.json.sha256), the canonical
SHA-256 of the byte-identical [`report.json`](report.json). No self-referential
digest is repeated in this README.

## Failure controls and non-claims

- No WebRTC APM algorithm, rate actuator, time stretcher or audio output is
  implemented.
- No WebRTC APM source, wheel, binary, runtime, model, weight, real corpus or
  licensed asset is present.
- No real speech, listening, benchmark, device-timing or release claim is made.
- No installed v0, ABI, registry, descriptor, default, shared build or CI change
  is included.
- No provider is registered, exposed or default-enabled.
- Historical source statements are provenance only; none is reproduced or used
  as a threshold here.

## Remaining gates / reopen

`DEFER` until all eight gates pass for the exact runtime and workload. Reopen
only with an exact licensed APM artifact or a different, licensed rate actuator
that has the required public rate-control surface, plus the rights-cleared
cohort and measurement harness above.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.
