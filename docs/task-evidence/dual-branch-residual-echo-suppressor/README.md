<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR - source, weights, rights and paired-reference blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the `Dual-branch residual echo suppressor`
(`component_id=dual-branch-residual-echo-suppressor`). The acceptance profile is
**Room**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed dual-branch residual echo suppressor source, weights,
runtime, adapter, immutable revision, two-branch topology, I/O geometry and
numeric output are **absent**. This package records that exact blocker, applies
the Room profile to a bounded deterministic synthetic paired render/capture
surrogate, and makes no echo, residual-suppression, quality, timing, listening,
benchmark or release claim. It is **not the candidate**: no dual-branch layer,
recurrent or attention block, weight file, native library, real audio, corpus,
model, device clock or upstream code is present, copied, downloaded, loaded,
imported or executed. Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`,
`id=dual-branch-residual-echo-suppressor`) is `considered`,
`disposition=sdk-model`, `verification_profile=room`, with the plan note
"Keep attachment to paired-reference canceller explicit; compare double-talk
preservation." Its only evidence link is `research/aec_research_20261028.md`.

The pinned research note lists neural residual suppression under
"dual-branch guidance / dual-stream residual echo suppressors" as an aim: it
should suppress residual echo while retaining near-end speech, and should be
evaluated after an adaptive filter and in double-talk. It also states:
"Candidate code/checkpoint availability is not yet verified." No source
repository, immutable revision, paper/technical report, checkpoint, weight
digest, parameter count, two-branch topology, sample rate, hop, channel layout,
render delay, lookahead, output geometry, license identity, training-data
statement or numeric output is recorded for this exact candidate.

Consequently:

- no candidate source, weights, runtime, adapter or pinned revision is staged at
  `data/checkouts/dual-branch-residual-echo-suppressor`,
  `data/models/dual-branch-residual-echo-suppressor`,
  `data/envs/dual-branch-residual-echo-suppressor` or
  `adapters/dual-branch-residual-echo-suppressor`;
- no immutable source/weight hash, build/archive identity, two-branch parameter
  layout, sample rate, hop, channel layout, render delay, lookahead or numeric
  output exists for the candidate itself;
- no upstream LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; there is no
  accepted paired render/capture residual-suppressor provider geometry, and
  the merged duplex evidence is a model-free proposal only;
- no real room, paired recording, consent, held-out split, AECMOS/STOI/ASR
  score, double-talk score or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR`, `7c6653f5a7db7f6de34ad709a96a455a9ad3263a` |
| Task mode | `feasibility` |
| Acceptance profile | `room` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/topology/delay asserted |
| Surrogate | synthetic paired 16 kHz mono render/capture, integer taps |
| Added content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer-tap NLMS **paired-reference canceller front
end** plus a deterministic residual energy gate. The front end is an explicit,
fixed stand-in for the paired-reference attachment named by the task plan note;
it is not candidate code and does not implement the candidate's two-branch
topology. It is not learned, uses no weights and cannot qualify the candidate.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Render/reference freeze | synthetic only | Frozen 16 kHz mono 160-sample render, fixed taps, declared 32-sample delay, noise levels, path switch and reset |
| Echo-only | synthetic only | Two far-end-only regions before and after one coefficient switch |
| Near-end-only | synthetic only | Two near-end regions with known clean near component and injected noise |
| Overlap | synthetic only | One synthetic render plus near-end double-talk region; one fixed SER, no device or listener |
| No-reference comparison | synthetic only | Independent gate-only control without a paired-reference canceller on the same synthetic mic |
| Echo attenuation | synthetic only | Chain and canceller-only ERLE in integer millidB on echo-only regions |
| Near-end damage | synthetic only | Near-reference SNR, level change and peak on near-only regions |
| Nonfinite failures | synthetic only | Nonfinite input/output checks and peak bound; no runtime failure |
| Alignment, delayed/missing render | synthetic only | Declared 32-sample delay; 64-sample shifted render collapse probe and missing-render frame rejection |
| Movement/path change | synthetic only | One fixed synthetic coefficient switch at sample 9600 |
| Task-matched held-out qualification | blocked | No rights-cleared paired render/capture cohort, held-out split, AECMOS/STOI/ASR, double-talk score or listening result |

Every echo, near-end, overlap and alignment row is `qualifies=false`. Synthetic
exactness means only that the fixture is self-consistent.

The attachment to a paired-reference canceller is explicit in
`report.json:paired_reference_attachment`: the surrogate consumes a
post-canceller residual plus a render reference, and the candidate attachment
itself is unverified. Double-talk preservation is recorded separately in
`report.json:double_talk_preservation`; it is a synthetic control, not candidate
evidence.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Fixture length: 16,000 samples (1.0 s), five contiguous segments:
  `echo_only_initial` 0-3200, `near_only_clean` 3200-6400,
  `overlap_double_talk` 6400-9600, `echo_only_after_path_change` 9600-12800,
  `near_only_noisy` 12800-16000.
- Render: deterministic integer LCG excitation at amplitude 8000 in active
  segments; near-end: deterministic three-tone speech-like source with a fixed
  16-step syllable envelope; noise: deterministic LCG at amplitude 20, 80 or
  120 depending on the segment.
- Echo paths: seven fixed integer taps at offsets 0, 3, 7, 11, 15, 19 and 23
  from a declared 32-sample render delay. Coefficients switch exactly once at
  sample 9600. Convolution is exact integer arithmetic with a Q10 divisor.
- Surrogate: 64-tap NLMS, step `35/100`, per-sample update; residual energy gate
  with a 0.25 gain floor and deterministic noise-floor tracking.
- Echo-only ERLE regions: `[1600,3200)` and `[11200,12800)` (convergence
  skipped).
- Near-end regions: `[3200,6400)` and `[12800,16000)`; overlap
  `[6400,9600)`.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | ---: |
| Chain ERLE, initial echo-only | 60048 mdB |
| Chain ERLE, after path change | 57951 mdB |
| Canceller-only ERLE, initial / after change | 48078 / 46171 mdB |
| Near-reference SNR, clean / noisy | 36280 / 20677 mdB |
| Near level change, clean / noisy | -2 / +43 mdB |
| Overlap/double-talk near-reference SNR | 6914 mdB |
| Overlap level change | +905 mdB |
| No-reference control ERLE | 11475 mdB |
| Chain echo gain over control | 36603 mdB |
| Aligned / delayed / missing-render ERLE | 60048 / 10545 / 11475 mdB |
| Nonfinite outputs | 0 |
| Adverse rejected inputs | 47 |

The high echo-only ERLE is an artifact of an exact linear synthetic path, not
evidence of real-room or candidate performance. Delayed and missing render are
detected by the ERLE collapse or the missing-frame rejection; a missing render
*frame* is rejected before processing, while an all-zero render is a separate
zero-reference probe, not a missing frame.

## Adverse, missing and invalid handling

`report.json` records 47 rejected inputs, each with unchanged processing state.
Rejections include duplicate JSON key, `NaN`/`Infinity` constants, malformed
JSON, missing/extra config fields, 8 kHz, 44.1 kHz, stereo, 256-sample frame,
`int16`, clock drift, linear resampling, wrong render delay, nonzero algorithmic
latency, boolean rate, missing mic, missing render, epoch mismatch, wrong
mic/render count, invalid valid-count, nonfinite mic, nonfinite render, nonzero
mic/render padding, string and boolean samples, wrong input position, reset
epoch 0/-1/non-increasing, negative reset position, missing/relative/bad-hash/
wrong-rate/wrong-channel/wrong-frame/wrong-delay/extra-field caller manifests,
and malformed fixture length/switch/segment/tap specifications. Missing real
recordings, weights, runtime outputs and labels are `blocked`, never passes.

The caller asset contract validates identity only. It never reads, loads,
imports or executes a source tree, weight file or runtime. A hash-matched
placeholder is never accepted as the pinned candidate artifact.

## Streaming, reset and determinism

The probe is frame-clocked: arbitrary caller chunks
`160/320/480/800/640/160` reproduce the full-block output exactly
(`all_match=true`, `accepted_samples=16000`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0, negative and non-increasing epochs are rejected with
the state digest unchanged. A 137-sample final partial frame advances state by
exactly 137 samples, emits 160 outputs and leaves the tail invalid samples zero.
`run.py` builds the report, contract and manifest three times and refuses to
write unless every payload is byte-identical.

## Separation from sibling evidence

The merged `speex-mdf-residual-postfilter`, `localvqe-compact-echo-only`,
`erle-and-double-talk-preservation`, `cagcrn-joint-aec-and-ns`,
`aec-challenge-paired-render-capture-fixtures`, `webrtc-aec3` and
`nlms-aec` packages are separate proposals with their own fixtures, assets,
metrics and dispositions. The merged `survey-cln-06` map names this component
only as a category lead. This package does not import, pool, score or reuse
their source, fixtures, metrics or results. Their README, report and contract
files are pinned only as read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, paired-reference chain surrogate, metrics, report and contract builders. |
| `run.py` | Builds all artifacts three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Room report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
| `sdk:docs/task-evidence/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER.md` | `b9efbe044c002485d4b5dbcc87ef8bf040daead08f9284f3ce19f61e6a32cc45` |
| `sdk:docs/task-evidence/speex-mdf-residual-postfilter/README.md` | `16c7643cc5550cd7358ee48f7dec62eb4045a3384364246cd357269ce0c28da9` |
| `sdk:docs/task-evidence/speex-mdf-residual-postfilter/report.json` | `ad15c446442058b82c003f15527637edae02a819a2033b0f289bc89042b170b6` |
| `sdk:docs/task-evidence/erle-and-double-talk-preservation/report.json` | `6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50` |
| `sdk:docs/task-evidence/localvqe-compact-echo-only/README.md` | `ed8c3a54297c929154283184eb9fad79b09f57ab4e77a31fb30f993c688e579a` |
| `sdk:docs/task-evidence/localvqe-compact-echo-only/report.json` | `28b17d5ee0afa2f017009456ef58d0fbac6383bf64744682e7400079df862369` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/README.md` | `aeae96f49acad572294b69cafb1b581392c3c3c11171d60545eadd6ede3187c7` |
| `sdk:docs/task-evidence/cagcrn-joint-aec-and-ns/report.json` | `697eb9feb470d529ba8132a8d597cb52308f46f5d2c6afd36803de268f9d7828` |
| `sdk:docs/task-evidence/survey-cln-06/README.md` | `4f9e0c0d901b8a45f3513c918b6f532fa16bed366ce0dee8a642e1bd46b0b96a` |
| `sdk:docs/task-evidence/survey-cln-06/report.json` | `b9db38650de9225a8cff7488f1e84b1a8c6062541300e758baa1f6ae58cfa1dc` |
| `sdk:docs/task-evidence/aec-challenge-paired-render-capture-fixtures/README.md` | `de5b37cb55275da0f130c2eb524c15f4f12fed18171725596156789ef8b41ccf` |
| `sdk:docs/task-evidence/aec-challenge-paired-render-capture-fixtures/report.json` | `da409a1500043ec303e35360de2124aff90c1bee9552939916f387103f69f512` |
| `sdk:docs/task-evidence/webrtc-aec3/report.json` | `da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283` |
| `sdk:docs/task-evidence/nlms-aec/README.md` | `83084ed97c02e21764f9a41daa2184e23afc13d86466dd40e0dfb0fc670bb9e0` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR/docs/task-evidence/dual-branch-residual-echo-suppressor
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical (3x cold-start
regeneration). External reproduction runs `run.py` three times and compares the
resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned dual-branch residual echo suppressor source, weights,
   runtime and two-branch architecture with an immutable revision, license
   identity and geometry record.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build, verified
   weight identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` explicit paired-reference canceller attachment, two-input geometry,
   declared delay and clock mapping into the SDK duplex contract with
   byte-level parity.
5. `RG-05` echo-only, near-end-only, overlap/double-talk and independent
   no-reference qualification on a rights-cleared task-matched held-out paired
   cohort.
6. `RG-06` streaming state, reset, latency, availability, path change,
   delayed/missing render and nonfinite behavior at the exact runtime.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed dual-branch residual echo
suppressor source, weights and runtime with an immutable revision and documented
two-branch geometry; admit an isolated hash-pinned runtime; clear
code/weight/training-data/corpus rights; make the paired-reference canceller
attachment explicit and map paired render/capture delay and clocks into the
accepted duplex contract; reproduce exact output; qualify echo-only,
near-end-only, overlap/double-talk and independent no-reference behavior on a
rights-cleared task-matched held-out cohort; measure target timing; and complete
opt-in provider intake. Until then the candidate stays **DEFER**, **incomplete**
and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-DUAL-BRANCH-RESIDUAL-ECHO-SUPPRESSOR]`, stable-field digest); the
mutable full `plan/swarm/TASKS.json` is never hashed, pinned or used as a digest
source. No provider, descriptor, registry, installed default, shared build or CI
is changed.
