<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE — DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`vosk-small-en-us-0-15-playback-gate` (`component_id=vosk-small-en-us-0-15-playback-gate`).
The structured inventory assigns the **Rate** acceptance profile
(`verification_profile: rate`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before implementation or
intake; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. No result qualifies.

This package does **not** import, load, execute, copy or download Vosk, Kaldi,
`libvosk`, the model tree, audio or a corpus. It does not decode or play audio,
run the gate, time a callback, listen, measure a device, or claim a benchmark or
release result. It pins the model and runtime bytes that happen to be present in
a mutable prototype area, proves that their license/notice/source/rights
identity is absent, defines a fail-closed caller-qualification boundary, and
records one explicitly **synthetic** gate-arithmetic control that is labelled
`synthetic_contract_control_not_evidence` and can never qualify. Only
`docs/task-evidence/vosk-small-en-us-0-15-playback-gate/` is written; no
provider, descriptor, registry, default, installed-v0, ABI, shared-build, CI,
board or handoff file changes.

## Exact external blocker: present bytes, absent license and qualification

The model and runtime **are present** in the git-ignored scratch tree
`cpp-library/pipeline-validation/playback-speed/`, so they are pinned exactly.
Presence is not admission. Five facts block the candidate:

1. **No model license/notice/model card.** The 14-file
   `vosk-model-small-en-us-0.15` tree (70,898,967 bytes, tree SHA-256
   `93e9c774f1c1d81633024ffd0a6674e0da4d3ef110f70501fe11dcd11e582cf2`) contains
   no `LICENSE`, `NOTICE`, `COPYING` or model card. Its `README` states only
   `Copyright 2020 Alpha Cephei Inc`. The official archive name/URL, model
   revision, archive size and archive SHA-256 are not recorded. A written
   Apache-2.0 model grant covering redistribution, commercial use and
   generated-output use is absent.
2. **No Vosk/Kaldi source revision or license.** No `alphacep/vosk-api` or Kaldi
   checkout exists at an exact 40-hex revision, so the decoder, Kaldi
   derivation and bundled third-party notices cannot be reviewed against the
   runtime.
3. **No pinned runtime archive or license.** The local Python `vosk 0.3.44`
   install has `vosk/__init__.py`, `vosk/vosk_cffi.py` and `libvosk.dyld`
   (12,533,472 bytes). The `dist-info` has **no** `LICENSE` file and `METADATA`
   says `License: UNKNOWN`; an Apache classifier is not a grant. There is no
   wheel/sdist archive, lockfile or offline-install record.
4. **No streaming run.** The prototype gate used one batch
   `KaldiRecognizer` call with `SetWords(True)` over the whole clip. Streaming
   chunking, right-context (the model README reports 0.15 s), endpoint/reset,
   dropped/stale events, first-output time, final partial window and callback
   latency were not measured.
5. **No rights-cleared qualification evidence.** There is no consented real
   cohort, no human-verified word/filler/pause span set, no independent
   transcript or scorer, no blind listening, no target-device timing and no
   release review. The prototype has two macOS `say` TTS clips with
   construction-time labels and one unlabeled AMI stitch.

**Reopen condition.** A caller supplies the exact official model archive and
its complete Apache-2.0 license/notice/model-card and output-use decision; the
exact Vosk source revision with license and notice bundle; a pinned wheel/sdist
with digest, lock and offline load proof; a streaming gate trace at a pinned
chunk size including reset/final-partial/availability/latency; a consented,
rights-cleared cohort with human-verified spans and matched controls;
independent content scoring plus blind listening; target-device timing and
resources; and a separate opt-in provider intake with OFF default and exact-head
review. Until then this task stays `DEFER` and all eight release gates stay
`blocked`.

## Source-reported prototype: provenance only

The numbers below are transcribed from the batched prototype README/results and
are **not remeasured, not rerun, not task evidence and not a qualification**.
They open no gate.

| Field | Source-reported value |
| --- | --- |
| Gate | Vosk `small-en-us-0.15` |
| Mode | batch whole-clip `KaldiRecognizer`, `SetWords(True)` |
| Streaming | No |
| Gate RTF (median) | `0.056` (batch call) |
| Gate share of chain cost | about 98 % |
| Total blocks | 15,708 at 100 ms |
| Deadline misses | 0 |
| Gate IoU vs construction-time labels | 0.94–0.95 |
| False-speech / missed-speech blocks | 12 / 24 of 345 and 467 |
| Output duration error vs source | −6 ms to +30 ms |
| Corpus | 2 synthetic TTS clips + 1 unlabeled real clip |
| Listeners | 0 |

## What this package actually verifies

1. **Exact pins of present bytes.** All 14 model files, the runtime Python
   files, `libvosk.dyld` and runtime metadata are pinned by SHA-256. The model
   tree digest and byte count are fixed. These are provenance pins, not a
   license or qualification.
2. **Absence of rights and qualification artifacts.** Fixed probes show no model
   or runtime license marker, no source checkout, no pinned wheel/lock, no
   rights-cleared corpus, no human-verified labels, no streaming trace and no
   listening/device record. Every corresponding artifact is `blocked`.
3. **Fail-closed admission.** A strict caller manifest covers source revision
   and license, the exact 14-file weight set, a pinned deterministic streaming
   runtime, source-timestamped events, four controls, bounded rate outcomes and
   six rights flags. Unknown/missing/invalid/nonfinite/aliased/out-of-range
   values are rejected. One synthetic schema control is admitted only to prove
   the validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence` and `qualifies=false`.
4. **Deterministic gate arithmetic control.** A stdlib-only, exact-rational
   block mapper and duration planner exercises mixed speech/filler/silence,
   all-speech fallback, an insufficient-budget fallback, a 165-sample final
   partial window, a `fixed_1.25` nonidentity control and a `slow_only`
   nonidentity control. It emits no audio and has no model input; it is
   illustrative arithmetic, not a gate result.
5. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, CI, the SDK README and merged sibling reports
   are pinned and verified unchanged.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| 1× control | blocked | No measured 1× gate/actuator playback. |
| Source/output mapping and rate changes | blocked | Synthetic arithmetic only. |
| Duration identity and error | blocked | No measured output duration. |
| Pitch | blocked | No stretched waveform or pitch measurement. |
| Transient audibility | blocked | No waveform, listening or transient analysis. |
| Buffering, rebuffer and drift | blocked | No device clock, fill/flush or drift run. |
| Unfamiliar speech, music and silence | blocked | No rights-cleared stratified corpus. |
| Final partial window and speech preservation | blocked | Synthetic final window only; no real labels or score. |

Pause/filler decisions are tied to source sample timestamps in the synthetic
control, never to wall time or playback position. That is a structural check,
not measured speech preservation.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable row projection `{id, title, repository, mode, depends_on, component,
evidence}` gates anything. The full mutable `plan/swarm/TASKS.json` bytes are
never hashed.

| Input group | Count | Use |
| --- | ---: | --- |
| Model tree (`models/vosk-model-small-en-us-0.15/**`) | 14 | Present bytes, unlicensed |
| Runtime (`vosk/` and `vosk-0.3.44.dist-info/`) | 6 | Present bytes, unlicensed |
| Prototype README, scripts, corpus metadata, WAVs, results | 9 | Source-reported provenance |
| Plan inventory, verification profile, SDK plan | 3 | Profile and boundary |
| SDK boundary files | 13 | Unchanged public/build/CI surface |

Key digests:

| Input | SHA-256 |
| --- | --- |
| `source:…/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` |
| `source:…/vosk-model-small-en-us-0.15/am/final.mdl` | `75370a0137f9daf8f469dedd7daa4513ae7a621f03240c6e512e2b50b656a7b6` |
| `source:…/vosk-model-small-en-us-0.15/graph/HCLr.fst` | `5caafba3081e1646545ac6bff0dd7a318e53dcbdc86f237909ce1d2ac1293d34` |
| `source:…/vosk/libvosk.dyld` | `82fdfba0dde392a7dbba70f9c1a17f6e3da27a50444a9f53939508525a1e6fdf` |
| `source:…/vosk-0.3.44.dist-info/METADATA` | `ea20f0c3c548e68d9b08ccc2a9aa5fef42754915a70d5e67098e2dcd6bec4746` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Present-but-unlicensed and absent-rights boundary; no vendored text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, gates, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, presence/license probes, gate arithmetic control, admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, its digest and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile, pins, presence/license, report bytes/digest, gates, licensing, write scope, three cold starts. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From this directory with Python 3.12 and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all unittest checks
pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... cold_starts=3/3
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
writes only to a temporary directory and never to this package.

Current counts: 32 source pins (14 model + 6 runtime + 9 prototype + 3 plan),
13 boundary pins, 10 required artifacts (2 present but blocked, 8 absent), 6
open blockers, 8 blocked Rate rows, 8 blocked rate outcomes, 41 rejected
admission controls, 1 schema-only control, 5 synthetic gate-arithmetic cases
(3 identity passes, 2 explicit nonidentity controls), 8 blocked release gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` model archive identity, license, notice and model card | blocked | Official archive URL/name, model revision, byte count, SHA-256, complete Apache-2.0 model/notice text and reviewed output-use terms. |
| `RG-02` Vosk source revision, license and notice bundle | blocked | Exact 40-hex source revision, tree digest, Apache-2.0 license and complete notice set corresponding to the pinned runtime. |
| `RG-03` runtime archive, lock and offline load | blocked | Pinned wheel/sdist digest, lockfile, isolated offline install, runtime license text and recorded host profile. |
| `RG-04` streaming gate availability and event integrity | blocked | Pinned chunk size, right-context, endpoint/reset/final-partial behavior, dropped/stale event accounting and measured latency. |
| `RG-05` rights-cleared corpus and human-verified labels | blocked | Signed consent, immutable cohort, speaker/language groups, human-verified word/filler/pause spans and matched controls. |
| `RG-06` rate acceptance profile | blocked | Measured mapping, 1×/rate-change/duration/pitch/transient/buffering/rebuffer/drift/final-partial results with agreed margins. |
| `RG-07` content preservation and independent scoring | blocked | Independent scorer or human transcript, stratified WER/semantic preservation and separation from the source-reported Whisper proxy. |
| `RG-08` listening, device timing, provider intake and release | blocked | Blind listening, target-device timing/power/resources, separate opt-in provider intake with OFF default and exact-head review. |

No synthetic admission control or arithmetic case opens a gate. No missing
result is promoted.

## Separation from other evidence

`SDK-D1-WHOLE-CLIP-DURATION-PLANNER` is a merged synthetic D1 budget-identity
reference; this package does not reuse its report values, corpus or results.
`SDK-DYNAMIC-INT8-WAV2VEC2-BASE` and
`SDK-DISTIL-WAV2VEC2-ADULT-CHILD-RIDGE` are ASR-adjacent DEFER boundaries, not
recognition evidence. `SDK-SURVEY-REC-01` and `SDK-SURVEY-DET-04` record the
same prototype only as an adjacent pre-screen (`HE-4`, `HE-2`).
`SDK-PHASE-VOCODER-BASELINE` is a model-free rate/playback baseline. None is
pooled, reinterpreted or substituted for this gate. The source-reported
Whisper tiny.en WER is a proxy and is not repeated here.

## Expected digest

`report.json` SHA-256:
`57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2`.
