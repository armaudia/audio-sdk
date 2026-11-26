<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CAGCRN-JOINT-AEC-AND-NS - CAGCRN joint AEC/NS source, rights and paired-render blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`CAGCRN` (`component_id=cagcrn-joint-aec-and-ns`). The acceptance profile is
**Room**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed CAGCRN source, weights, runtime, adapter, immutable revision,
I/O geometry and numeric output are **absent**. This package records that exact
blocker, applies the Room profile to a bounded deterministic synthetic paired
render/capture surrogate, and makes no echo, noise-suppression, quality, timing,
listening, benchmark or release claim. It is **not CAGCRN**: no cross-attention
block, CRN, weight file, native library, real audio, corpus, model, device clock
or upstream code is present, copied, downloaded, loaded, imported or executed.
Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`,
`id=cagcrn-joint-aec-and-ns`) is `considered`, `disposition=sdk-model`,
`verification_profile=room`, with the plan note "Use task-matched
source/weights and separate echo and near-end conservation tests." Its only
evidence link is `research/aec_research_20261028.md`.

The pinned research note says only: "Paper reports a 0.07M-parameter
cross-attention gated CRN with delay alignment and joint echo/noise processing.
Strong compact-model lead; usable source and checkpoint acquisition/compatibility
still needs verification before implementation." It later states: "CAGCRN is the
smallest reported joint AEC/noise-suppression paper candidate (70K parameters),
but no runnable code/checkpoint was verified during this pass." The cited
Interspeech 2025 paper link is the only provenance.

Consequently:

- no CAGCRN source, weights, runtime, adapter or pinned revision is staged at
  `data/checkouts/CAGCRN`, `data/models/cagcrn`, `data/envs/cagcrn` or
  `adapters/cagcrn`;
- no immutable source/weight hash, build/archive identity, parameter layout,
  sample rate, hop, channel layout, render delay, lookahead or numeric output
  exists for CAGCRN itself;
- no upstream LICENSE, model card, weight terms, training-data statement,
  attribution bundle, corpus rights or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream; there is no
  accepted paired render/capture AEC provider geometry. The merged duplex
  evidence is a model-free proposal only;
- no real room, paired recording, consent, held-out split, AECMOS/STOI/ASR
  score or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CAGCRN-JOINT-AEC-AND-NS`, `c399af9eded97f44c19c512433640589277e9017` |
| Task mode | `feasibility` |
| Acceptance profile | `room` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; no rate/hop/delay asserted |
| Surrogate | synthetic paired 16 kHz mono render/capture, integer taps |
| Added content delay | 0 samples; no device timing claim |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer-tap NLMS echo canceller plus a deterministic
residual energy gate. It is **not CAGCRN**, is not learned, uses no weights and
cannot qualify the candidate.

## Room profile application

`plan/swarm/VERIFICATION.md` Room row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Render/reference freeze | synthetic only | Frozen 16 kHz mono 160-sample render, fixed taps, declared 16-sample delay, noise levels, path switch and reset |
| Echo-only | synthetic only | Two far-end-only regions before and after one coefficient switch |
| Near-end-only | synthetic only | Two near-end regions with known clean near component and injected noise |
| Overlap | synthetic only | One synthetic render plus near-end region; one fixed SER, no device or listener |
| No-reference comparison | synthetic only | Independent gate-only control without AEC on the same synthetic mic |
| Echo attenuation | synthetic only | Joint and AEC-only ERLE in integer millidB on echo-only regions |
| Near-end damage | synthetic only | Near-reference SNR, level change and peak on near-only regions |
| Nonfinite failures | synthetic only | Nonfinite input/output checks and peak bound; no runtime failure |
| Alignment, delayed/missing render | synthetic only | Declared 16-sample delay; 32-sample shifted render and all-zero render probes |
| Movement/path change | synthetic only | One fixed synthetic coefficient switch at sample 7200 |
| Task-matched held-out qualification | blocked | No rights-cleared paired AEC cohort, held-out split, AECMOS/STOI/ASR or listening result |

Every echo, near-end, overlap and alignment row is `qualifies=false`. Synthetic
exactness means only that the fixture is self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample.
- Fixture length: 12,000 samples (0.75 s), five contiguous segments:
  `echo_only_initial` 0-2400, `near_only_clean` 2400-4800,
  `overlap_double_talk` 4800-7200, `echo_only_after_path_change` 7200-9600,
  `near_only_noisy` 9600-12000.
- Render: deterministic integer LCG excitation at amplitude 8000 in active
  segments; near-end: deterministic three-tone speech-like source with a fixed
  16-step syllable envelope; noise: deterministic LCG at amplitude 20, 80 or
  120 depending on the segment.
- Echo paths: seven fixed integer taps at offsets 0, 4, 8, 12, 16, 20 and 24
  from a declared 16-sample render delay. Coefficients switch exactly once at
  sample 7200. Convolution is exact integer arithmetic with a Q10 divisor.
- Surrogate: 64-tap NLMS, step `35/100`, per-sample update; residual energy gate
  with a 0.25 gain floor and deterministic noise-floor tracking.
- Echo-only ERLE regions: `[1200,2400)` and `[8400,9600)` (convergence skipped).
- Near-end regions: `[2400,4800)` and `[9600,12000)`; overlap `[4800,7200)`.

Measured synthetic observations (integer millidB, unqualified):

| Item | Value |
| --- | --- |
| Joint ERLE, initial echo-only | 61123 mdB |
| Joint ERLE, after path change | 56691 mdB |
| AEC-only ERLE, initial / after change | 49082 / 45279 mdB |
| Near-reference SNR, clean / noisy | 30966 / 21525 mdB |
| Near level change, clean / noisy | -14 / +47 mdB |
| Overlap near-reference SNR | 8046 mdB |
| No-reference control ERLE | 10987 mdB |
| AEC echo gain over control | 38095 mdB |
| Aligned / delayed / missing-render ERLE | 61123 / 10576 / 10987 mdB |

The high echo-only ERLE is an artifact of an exact linear synthetic path, not
evidence of real-room performance; the research note makes the same caution for
its own linear simulation. Delayed and missing render are detected by the
ERLE collapse, but a missing render *frame* is rejected before processing.

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
placeholder is never accepted as the pinned CAGCRN artifact.

## Streaming, reset and determinism

The probe is frame-clocked: arbitrary caller chunks
`160/320/480/800/640/160` reproduce the full-block output exactly
(`all_match=true`, `accepted_samples=12000`). Reset to epoch 2 matches a fresh
epoch-2 session; epoch 0, negative and non-increasing epochs are rejected with
the state digest unchanged. A 137-sample final partial frame advances state by
exactly 137 samples, emits 160 outputs and leaves the tail invalid samples zero.
`run.py` builds the report three times and refuses to write unless every payload
is byte-identical.

## Separation from sibling evidence

The merged `localvqe-compact-full` and `erle-and-double-talk-preservation`
packages are separate AEC proposals with their own fixtures, assets, metrics and
dispositions. The merged `nlms-aec`, `webrtc-aec3` and `duplex-clocks` evidence
are separate model-free or DSP references. This package does not import, pool,
score or reuse their source, fixtures, metrics or results. Their README, report
and contract files are pinned only as read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, frozen paired fixture, joint suppressor surrogate, metrics, report and contract builders. |
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
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
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
| `sdk:docs/task-evidence/localvqe-compact-full/README.md` | `d584017431cdcbf1e2eddcb0225e802d3094a8700638e9f6fed96daa8fa09e29` |
| `sdk:docs/task-evidence/localvqe-compact-full/report.json` | `08c75119706877d323fdb4299f53b274f86c6ab27f7a683d8764cc61a1a73f4a` |
| `sdk:docs/task-evidence/localvqe-compact-full/contract.json` | `32e9d371ccf72edcdc1619ee0db3149323e20296a7b853b6ee9ac8a95b0054e7` |
| `sdk:docs/task-evidence/erle-and-double-talk-preservation/README.md` | `0f8ddc78f41459734f4ed096eb71789ecf5bcc809d833c5b65f63319ef11db2e` |
| `sdk:docs/task-evidence/erle-and-double-talk-preservation/report.json` | `6860139e8c1a9f5c01fa219f81b6b8f5ee3f43160dd139d00e45cfb853d63b50` |
| `sdk:docs/task-evidence/duplex-clocks/contract.json` | `c09f5a45862fda31039be5b7ebccff07be904c606d51a6f3accde9bea6f04cb4` |
| `sdk:docs/task-evidence/nlms-aec/report.json` | `2910e9e986259a9de738822c35a2908e47a836a9daabc292118f6c7389988f6a` |
| `sdk:docs/task-evidence/webrtc-aec3/report.json` | `da1c2d7bc30fd8e2ae533110cd4130b623859a1747415312386044f41c8c2283` |
<!-- digest-table: end -->

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CAGCRN-JOINT-AEC-AND-NS/docs/task-evidence/cagcrn-joint-aec-and-ns
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CAGCRN-JOINT-AEC-AND-NS diff --check
```

`run.py` builds the report, contract and manifest three times in one process and
refuses to write unless all payloads are byte-identical. External reproduction
runs `run.py` three times and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact pinned CAGCRN source, weights and runtime with an immutable
   revision, license identity, parameter/geometry record and adapter settings.
2. `RG-02` isolated hash-pinned runtime admission, reproducible build, verified
   weight identity and fail-closed absent behavior.
3. `RG-03` code, weight, training-data and corpus rights plus attribution,
   notices, redistribution, product-use and derivative-output review.
4. `RG-04` paired render/capture geometry, declared delay and clock mapping into
   the SDK duplex contract with byte-level output parity.
5. `RG-05` echo-only, near-end-only, overlap and no-reference qualification on a
   rights-cleared task-matched held-out paired cohort.
6. `RG-06` streaming state, reset, latency, availability, path change,
   delayed/missing render and nonfinite behavior at the exact runtime.
7. `RG-07` target-device pacing, timing and memory with independent listening
   and/or ASR controls.
8. `RG-08` opt-in provider intake, descriptor review, independent exact-head
   review and default/release approval.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Pin the exact licensed CAGCRN source, weights and runtime
with an immutable revision and documented geometry, admit an isolated
hash-pinned runtime, clear code/weight/training-data/corpus rights, map paired
render/capture delay and clocks into the accepted duplex contract, reproduce
exact output, qualify echo-only, near-end-only, overlap and no-reference behavior
on a rights-cleared task-matched held-out cohort, measure target timing and
complete opt-in provider intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-CAGCRN-JOINT-AEC-AND-NS]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.
