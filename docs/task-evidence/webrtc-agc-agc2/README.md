<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WEBRTC-AGC-AGC2 — WebRTC AGC / AGC2 blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the WebRTC AGC / AGC2 feasibility row.
It is **not WebRTC**: no upstream source, header, library, wheel, `NOTICE`,
model, weights, licensed runtime, real corpus, device measurement, listening
result, benchmark or release claim is present. **No result here qualifies
WebRTC AGC or AGC2.**

## Exact blocker: the WebRTC APM AGC/AGC2 artifact is absent

The task requires the exact licensed source/runtime for the WebRTC Audio
Processing Module legacy AGC (`WebRtcAgc`) and AGC2. It is **not present in the
workspace**, and nothing was fabricated or downloaded:

| Item | Status |
| --- | --- |
| Upstream artifact | WebRTC APM source tree at an exact pinned revision |
| Required source files | `modules/audio_processing/include/audio_processing.h`, `audio_processing_impl.cc`, `agc/gain_control.h`, `agc/legacy/gain_control.c`, `agc/agc_manager_direct.cc`, `agc2/adaptive_digital_gain_controller.cc`, `agc2/adaptive_agc.cc`, `agc2/fixed_digital_level_estimator.cc`, `agc2/input_volume_controller.cc`, `agc2/limiter.cc`, `agc2/rnn_vad/rnn_vad_weights.cc`, the revision's `BUILD.gn` and its `LICENSE`/`NOTICE` |
| Required runtime | a built APM library exposing `AudioProcessor` or `GainControl`, or a pinned `pywebrtc-audio==0.2.0` wheel with documented AGC coverage |
| Expected licence | **Apache-2.0** for WebRTC source, subject to the exact revision's `NOTICE` and third-party terms |
| Pinned revision | **none** (no locally verified commit, tag, tree or file digest) |
| Source digest | **none** |
| Runtime digest | **none** |
| Workspace search | Bounded read-only name probe visited more than 11,000 entries in this SDK worktree (including `third_party/` and `deps/`), plus `adapters/`, `data/` and `cpp-library/`: **0** required source/runtime names found. `third_party/` holds only `speexdsp`; `deps/lock.json` pins only SpeexDSP 1.2.1; `data/envs/webrtc` is absent; `pywebrtc_audio` is not importable |
| Local binding pin | `adapters/webrtc-ns/requirements.lock` declares `pywebrtc-audio==0.2.0` for noise suppression, but the adapter states **AGC are disabled**. The pin is not AGC API coverage |
| Rights requirement | exact Apache-2.0 text and `NOTICE`, third-party notice set, patent-grant review, an explicit decision for any embedded/generated weights, and an approved redistribution model for source, native library or wheel, all before any wrapper, build, comparison or release |

The three upstream revision URLs quoted in
`research/level_tone_control_20261028.md:20` and
`research/voice-enhancement-20261101/agent-transform-space/REPORT.md:39` are
recorded in the report as **documentation only** with
`verified_locally=false`. They are not pins and no file was fetched.

The machine-readable record is `report.json` →
`upstream_blocker` (`status="blocked_upstream_absent"`,
`pinned_revision=null`, `source_digest=null`, `runtime_digest=null`,
`no_upstream_parity_claim=true`). `contract.json` carries the same blocker and
all eight blocked release gates.

Because the artifact is missing, **no result qualifies either candidate**, no
provider is registered, and release gate `RG-01` stays blocked.

## Exact scope

- Work is confined to `docs/task-evidence/webrtc-agc-agc2/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  gain-control provider is installed or registered.
- There is no C provider, no installed target and no public API/ABI change. The
  package deliberately has no provider or adapter manifest: WebRTC AGC/AGC2 is
  unavailable, so there is nothing truthful to wrap or register.
- No request is ever processed as WebRTC AGC or AGC2. Both candidate paths fail
  closed with `UPSTREAM_ABSENT`.
- Missing, invalid, nonfinite and out-of-range requests fail closed with no
  metrics. No missing result qualifies a candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority and history never enter canonical bytes and are never a
  gate. The full mutable `plan/swarm/TASKS.json` is **not hashed** into any
  canonical artifact.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a gain
controller:

1. **Strict request validation** at the public v0 geometry. Exactly
   `candidate`, `sample_rate_hz`, `channels`, `frame_samples`, `samples`,
   `epoch`, `first_input_sample`, `lifecycle` and `execution_mode` are
   accepted. Unknown or missing fields, wrong geometry, wrong sample count,
   booleans, strings, nonfinite values, out-of-range values, negative epoch or
   position, closed/drained lifecycle and unknown modes are rejected before any
   candidate call.
2. **Fail-closed candidate dispatch.** A valid request for `webrtc_agc` or
   `webrtc_agc2` raises `UpstreamAbsent`. There is no fallback surrogate.
3. **Generated stimulus characterisation** for silence, impulse, step, sweep
   and speech-like surrogates. Only peak, RMS, digest and finite counts are
   reported; no candidate filtering or gain is applied.
4. **Bounded absence probe** over explicit roots with skipped build, VCS and
   environment directories, a 200,000-entry cap and a 14-level depth cap. It
   checks file/directory names only; it never loads or executes anything.
5. **Stable board identity** from the linked row only.
6. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** estimate a gain law, limiter, attack/release, noise floor,
headroom, delay, AGC2 adaptive digital gain or RNN-VAD speech probability.

## DSP profile application

`plan/swarm/VERIFICATION.md` assigns the DSP profile. With the candidate absent,
the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Sweeps, steps, impulses, silence, clean speech | Stimuli are generated and characterised only. No candidate output. |
| Gain and frequency response | `blocked_upstream_absent` — requires candidate output. |
| Attack and release | `blocked_upstream_absent` — requires candidate output. |
| Headroom and peak limit | `blocked_upstream_absent` — requires candidate output. |
| Delay and drain | `blocked_upstream_absent` — no APM API, delay or drain was exercised. |
| Numerical behaviour | `partial_local_harness_only` — nonfinite/invalid rejection and identity control only. |
| State transitions | `blocked_upstream_absent` — no reset/epoch/session behaviour exists. |
| Interacting nonlinear configurations | `blocked_upstream_absent` — no gain/limiter/AGC2 setting was exercised. |
| Intelligibility or load-specific control | `blocked_upstream_absent` — no corpus, scorer or candidate output. |
| Separate DSP AGC comparison | `blocked_upstream_absent` — no candidate output exists to compare. |
| APM mode ownership | `unresolved` — `AudioProcessor`/`GainControl`, legacy AGC/AGC2 and inline/processing-thread/buffered-worker ownership are unqualified. |
| Identity/noisy control and paired SI-SDR/STOI | `blocked_upstream_absent` — no candidate output; no real clean references. |

## Deterministic local results (not candidate results)

Stimulus characterisation on generated 16 kHz samples:

| Stimulus | Samples | Peak | RMS | Nonfinite |
| --- | ---: | ---: | ---: | ---: |
| `silence` | 1,600 | 0.000000 | 0.000000 | 0 |
| `impulse` | 1,600 | 0.500000 | 0.012500 | 0 |
| `step` | 1,600 | 0.250000 | 0.176777 | 0 |
| `sweep` 200→3000 Hz | 1,600 | 0.300000 | 0.212109 | 0 |
| `speech_like` | 3,200 | 0.344139 | 0.146388 | 0 |

The speech-like surrogate has source-anchored voiced/pause RMS contrast
**49.35 dB**; this is a signal proxy, not intelligibility, MOS or listening.

Rejection evidence:

- 19 invalid request cases: all rejected, `metrics=null`;
- 6 invalid JSON cases (duplicate key, NaN, ±Infinity, trailing data, syntax):
  all rejected;
- missing result: `status=blocked`, `metrics=null`,
  `qualifies_candidate=false`;
- identity control: byte-identical for every generated stimulus.

Every candidate row remains `blocked_upstream_absent` with `metrics=null`.
There are no candidate metrics, no paired quality scores, no gain or limiter
measurements, no delay measurement and no listening result.

## Eight blocked release gates

| Gate | Status | Reopen condition |
| --- | --- | --- |
| `RG-01` upstream source and revision pin | blocked | Stage the exact WebRTC AGC/AGC2 source with verified commit/tree/file digests. |
| `RG-02` upstream licence, notice and rights review | blocked | Vendor Apache-2.0 `LICENSE`/`NOTICE`, review third-party and weight terms, approve distribution. |
| `RG-03` exact APM build and runtime install parity | blocked | Build/install the pinned APM library or wheel and prove clean import. |
| `RG-04` AGC/AGC2 API, geometry, delay, drain and mode parity | blocked | Measure the real API paths at 16 kHz mono and map them to v0. |
| `RG-05` separate DSP AGC comparison and rights-qualified cohort | blocked | Freeze a permitted paired cohort and compare identical settings. |
| `RG-06` gain/response/attack/release/headroom/preservation | blocked | Measure the full DSP profile with paired clean references and adverse cases. |
| `RG-07` target runtime timing, memory and callback suitability | blocked | Measure paced device timing and callback behaviour independently. |
| `RG-08` provider intake, public surface, review and release | blocked | Complete intake, public-surface decision, independent review and approval. |

## Pinned sources and boundary

Paths prefixed `source:` are relative to
`/Users/htsakanyan/workspace/audio/audioml`; all other paths are relative to
this SDK worktree. Exact digests are in `SOURCES.sha256` and `contract.json`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `research/level_tone_control_20261028.md` | `b9178c7c486bec81222919977f8111d4e5c5508ee31d8dbd44c6600e51e25c44` | Documents WebRTC AGC2 as adaptive digital gain plus limiter with headroom and bounded changes; records upstream revision URLs as documentation only. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Component matrix context; AGC/envelope rows are not WebRTC AGC2 results. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Component provenance only. |
| `adapters/webrtc-ns/requirements.lock` | `c289d4c0ab4af3f54e2bf693f1f81a01aa7cc479627f9e7a3161b2f1f792d591` | Declares `pywebrtc-audio==0.2.0`; runtime absent and AGC disabled. |
| `adapters/webrtc-ns/README.md` | `8893bace6b0289135f6d1ccad949a9eba44a824e37f45765f30b4192f82c5992` | States APM noise suppression is used with AGC disabled. |
| `cpp-library/PIPELINE_DESIGN_REPORT.md` | `f603bd8eb27a44a1861a61e9f90d7085d785cbb77af9694b332677bd5e38b093` | Records that no integrated duplex APM run with AGC exists. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Inventory record: `considered`, `verification_profile=dsp`. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | DSP acceptance profile. |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Fixed v0 format, mapping and lifecycle. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Public boundary pin, read-only. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Public boundary pin, read-only. |

Claim base: `74fb3cd9f6f3e4b96a542d925461d24e1472c21d`.
Branch: `swarm/SDK-WEBRTC-AGC-AGC2`. Stable board projection digest:
`a5622f0295e02bbf9100816c1e819b81307d6f87cf8cc9b82a13156cfdd9ee90`
(one linked row; mutable fields excluded). The full mutable `TASKS.json` digest
is deliberately not recorded or gated.

## Files

| File | Purpose |
| --- | --- |
| `README.md` | This disclosure, blocker, profile mapping, results and reproduction guide. |
| `reference.py` | Stdlib-only deterministic validation, stimulus characterisation, absence probe, stable board identity and report model. |
| `run.py` | `--all`, `--report`, `--sources`, `--contract`, `--stdout-report`, `--verify-repro` generator. |
| `verify.py` | Strict read-only verifier: strict JSON, pins, semantics, canonical bytes, three cold starts, licensing, absent upstream and git scope. |
| `test_reference.py` | Deterministic standard-library acceptance suite; no skips, no network. |
| `check_licensing.py` | Local SPDX/REUSE checks; rejects fabricated upstream license or binary artifacts. |
| `contract.json` | Frozen task contract, artifact/source pins, blocker and eight blocked gates. |
| `report.json` | Canonical machine-readable blocker evidence. |
| `report.json.sha256` | SHA-256 of the canonical report bytes. |
| `SOURCES.sha256` | Curated pins for context sources, boundary headers, package artifacts and the report. |
| `LICENSE`, `LICENSES.md`, `THIRD_PARTY_NOTICES.md` | Apache-2.0 sidecar and exact absent-upstream rights notes. |
| `*.license` | REUSE SPDX sidecars for JSON and digest files. |

## Reproduction

Run from this directory on the pinned worktree, with Python 3.11+ and no
third-party packages:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 run.py --verify-repro
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
```

`run.py --all` regenerates `report.json`, `report.json.sha256`,
`SOURCES.sha256` and `contract.json` byte-identically. `run.py --verify-repro`
rebuilds every canonical artifact in memory and compares it to the committed
bytes; `verify.py` runs it three times in fresh processes and requires identical
output. JSON is canonical (`sort_keys=True`, compact separators,
`allow_nan=False`) with one trailing newline.

No result in this package may be promoted to a WebRTC AGC/AGC2 claim until every
blocked gate above is reopened with the exact upstream artifact and independent
exact-head review.
