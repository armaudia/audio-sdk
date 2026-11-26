<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WAVLM-BASE-RIDGE — DEFER blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`wavlm-base-ridge` (`component_id=wavlm-base-ridge`): the frozen
`microsoft/wavlm-base-plus` encoder plus a standardized ridge head that the
historical pilot used to estimate **syllables/second**. The structured inventory
assigns the **Rate** acceptance profile (`verification_profile: rate`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER** before implementation or intake; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. No result qualifies.

This package does **not** import, load, execute, copy or download WavLM,
PyTorch, Transformers, a checkpoint, a feature archive, audio or a corpus. It
does not estimate rate on speech, render stretched audio, time a callback,
listen, measure a device, or claim a benchmark or release result. It pins the
research metadata that happens to be present, proves that the weight, runtime,
licence and qualification artifacts are absent, defines a fail-closed caller
boundary, and records one explicitly **synthetic** standardized-ridge arithmetic
control labelled `synthetic_ridge_arithmetic_control_not_evidence` that can never
qualify. Only `docs/task-evidence/wavlm-base-ridge/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact external blocker: absent weights, absent licence, absent runtime

The research source record is present and pinned, but none of the artifacts
needed to reproduce the candidate are:

1. **No weight snapshot.** `research/tsm-followup-20261101/agent-neural/run/
   wavlm-base-plus_source.json` pins `microsoft/wavlm-base-plus` revision
   `4c66d4806a428f2e922ccfa1a962776e232d487b` and `pytorch_model.bin` at
   **377,617,425 bytes**, SHA-256
   `3bb273a6ace99408b50cfc81afdbb7ef2de02da2eab0234e18db608ce692fe51`.
   No such file exists in the data/model probes or the Hugging Face cache. No
   weight was downloaded or reconstructed.
2. **No licence or model card.** The same source record sets `license: null`.
   No `LICENSE`, `NOTICE`, model-card text, redistribution permission,
   commercial-use permission or generated-output-use decision is staged or
   reviewed. Presence of metadata is not a grant.
3. **No pinned runtime.** Qualification needs Python 3.10.13, torch 2.2.2 and
   transformers 4.40.2, CPU, deterministic, offline, with wheel hashes and a
   lockfile. None of the available interpreters exposes torch or transformers,
   and no isolated install or load record exists.
4. **No rights-cleared cohort.** The historical pilot is 210 four-second
   windows from one AMI EN2003a meeting with transcript-plus-CMUdict syllable
   labels, not human syllable nuclei; AMI and CMUdict terms are not reviewed
   here.
5. **No reproduced result.** The recorded MAE/RMSE/r and encoder timing are
   quoted context only. The derived embedding archive is pinned but not loaded,
   parsed or scored, and no adverse, missing or nonfinite control was exercised
   against the real encoder.
6. **No rate-profile, listening, device-timing or release evidence.** A
   syllables/second estimate is not a preferred speed factor, a TSM setting or a
   product policy.

**Reopen condition.** A caller supplies the exact immutable snapshot and a
written model/output-use grant; the pinned offline runtime with wheel digests,
lock and load proof; a consented, speaker/meeting-disjoint cohort with checked
syllable labels; a reproduced encoder-plus-ridge result with adverse controls; a
measured Rate profile on the target device; and a separate OFF-by-default
provider intake with independent exact-head review. Until then this task stays
`DEFER` and all eight release gates stay `blocked`.

## Pinned research context (quoted, not reproduced)

`research/tsm-followup-20261101/README.md` line 30 documents the prior external
evaluation of this checkpoint as a frozen encoder plus a ridge rate head:
**MAE .609 syll/s, RMSE .760, r .849**, CPU encoder **p95 462 ms** per 4 s clip,
**94,381,936** parameters / **377,617,425** weight bytes, and **no license field
on the model card**. The fixture records these under
`observed_provenance.documented_context` with `reproduced_here=false`. No
weight, runtime, local corpus or authorization backs them; this PR does not
reproduce, confirm or extend that result.

## What this package actually verifies

1. **Exact pins of present provenance.** Eleven read-only research/plan files
   and fourteen SDK boundary/merged-sibling files are pinned by SHA-256. The
   documented four-file model tree digest is fixed. These are provenance pins,
   not an admission.
2. **Absence of weights, runtime and rights.** Probes show no snapshot in the
   data/model paths or the Hugging Face cache, no WavLM source checkout, no
   torch/transformers runtime, no model-card licence marker and no
   rights-cleared corpus or labels. Every corresponding artifact is `blocked`.
3. **Fail-closed caller admission.** A strict caller manifest covers source
   revision and licence, the exact weight set, pinned runtime, feature-extractor
   geometry, 4 s windows, standardized-ridge head, outcomes and six rights
   flags. Unknown/missing/invalid/nonfinite/aliased/out-of-range values are
   rejected. One synthetic schema control is admitted only to prove the
   validator is not blanket-rejecting; it is labelled
   `synthetic_schema_control_not_evidence` and `qualifies=false`.
4. **Deterministic ridge arithmetic control.** A stdlib-only exact-rational
   StandardScaler + Ridge(alpha=10) fit over 24 synthetic four-feature windows
   (18 calibration, 6 evaluation) exercises the head arithmetic used by the
   candidate. It emits no audio, reads no WavLM feature and is illustrative
   arithmetic, not an accuracy result.
5. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, CI, the SDK README and merged sibling reports
   are pinned and verified unchanged.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| 1× control | blocked | No measured 1× playback or estimator-to-policy control. |
| Source/output mapping and rate changes | blocked | No source-to-output mapping; the candidate only estimates syllables/second. |
| Duration identity and error | blocked | No rendered output duration exists. |
| Pitch | blocked | No stretched waveform or pitch measurement. |
| Transient audibility | blocked | No waveform, listening or transient analysis. |
| Buffering, rebuffer and drift | blocked | No device clock, fill/flush or drift run. |
| Unfamiliar speech, music and silence | blocked | No rights-cleared stratified corpus; the pilot is one meeting of speech. |
| Final partial window and speech preservation | blocked | No final partial window, timestamp-tied pause/filler decision or preservation score. |

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only the
stable row projection `{id, title, repository, mode, depends_on, component,
evidence}` gates anything. The full mutable `plan/swarm/TASKS.json` bytes are
never hashed.

| Input group | Count | Use |
| --- | ---: | --- |
| Research source record, report, runner, manifest, results, embeddings | 8 | Documented provenance, declared/absent rights |
| Plan inventory, verification profile, SDK plan | 3 | Profile and boundary |
| SDK boundary files and merged sibling reports | 14 | Unchanged public/build/CI surface |

Key digests:

| Input | SHA-256 |
| --- | --- |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `source:…/wavlm-base-plus_source.json` | `5210619f683caf2da4ee0c5e0973dba62fca8db8e06f47a215bdec54efe868d1` |
| `source:…/wavlm-base-plus_results.json` | `9e041bf0369ebbc5f6142a9230ba41e84c86fd4ce2a6ba10bf94effa36570297` |
| `source:…/wavlm-base-plus_fp32_embeddings.npz` | `12372ed9f204f1668778bc21096633758d1169bcde8e2db5d947f6ffd06776a1` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/dynamic-int8-wav2vec2-base/report.json` | `6f166a5bc05a31064780f0957e5d1fb2046d5939180175b40b72f70a36e856c9` |
| `docs/task-evidence/distil-wav2vec2-adult-child-ridge/report.json` | `ff7b70f389b8c7908c917aa2488728d7f972a8acd22bf66c56d9a671cd5a65d4` |

## Files

| File | Purpose |
| --- | --- |
| `README.md` | Scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Absent-licence and absent-rights boundary; no vendored text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, gates, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, presence/licence probes, exact ridge arithmetic, admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, its digest and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile, pins, presence/licence, report bytes/digest, gates, licensing, write scope, three cold starts. |
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

Expected: `run.py` reports `repeat=3 byte_identical=true`; all 47 unittest
checks pass with 0 failed and 0 skipped; `verify.py` prints `PASS pins=25
gates=8 blockers=6 artifacts=10 admission_cases=74 cold_starts=3/3
byte_identical=true profile=Rate status=incomplete decision=DEFER`; REUSE
reports no missing or bad licence; `git diff --check` is clean. `verify.py`
writes only to a temporary directory and never to this package.

`reference.py` (via `run.py`/`verify.py`) requires Python 3.10 or newer; the
pinned regeneration interpreter is 3.12.16. Source pins resolve from
`AUDIOML_ROOT`, defaulting to the workspace three parents above this worktree
(`/Users/htsakanyan/workspace/audio/audioml`). The plan checker reads the board
outside this worktree and never modifies it.

Committed digest:
`cc20fc6696d723163b0213702c32d014e67758d670cd7685cefb49add1d30b2f`.

## Expected deterministic results (synthetic only)

- Control cohort: 24 synthetic windows, 4 exact-rational features, 18
  calibration / 6 evaluation, standardized with training statistics only,
  Ridge(alpha=10); labels are `syllables/4` from deterministic integer
  syllables. No WavLM feature, weight, audio or human label is used.
- Evaluation (6 windows): nonnegative MAE **0.336356622** syll/s, RMSE
  **0.377616427**, bias **−0.121267953**, Pearson r² **0.763982069**; zero
  negative raw predictions.
- Constant calibration-mean baseline (`2.333333333`): MAE **0.750000000**,
  RMSE **0.881917103**, r² **−0.287356322**.
- Rejection results: **74/74** invalid or missing inputs rejected, including
  missing/unknown fields, wrong schema/component ids, bad revision/licence,
  placeholder licences, wrong weight set, zero bytes, duplicate/traversal
  names, wrong runtime versions/threads/device, nonfinite or float features and
  rates, misaligned/noncontiguous/short windows, bad head/outcome values,
  self-qualified outcomes and false rights flags. One synthetic schema control
  is admitted but never qualifies.
- These numbers are wiring/regression evidence for the ridge arithmetic only.
  They must not be compared with the pinned WavLM context as if this fixture
  reproduced it. No real accuracy, runtime, preference or product claim follows.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, model card and licence | blocked | Exact upstream revision/tree, complete model card and licence/notice set, plus an independent terms and output-use review. |
| `RG-02` weight snapshot and redistribution rights | blocked | Immutable four-file snapshot with byte counts and SHA-256, plus a written redistribution and product-use decision. |
| `RG-03` pinned offline runtime | blocked | Python 3.10.13 / torch 2.2.2 / transformers 4.40.2 wheel digests, lockfile, CPU thread and deterministic settings, offline install and load proof. |
| `RG-04` rights-cleared cohort and labels | blocked | Consented, speaker/meeting-disjoint cohort with reviewed corpus/dictionary terms, independent syllable labels and source timestamps. |
| `RG-05` frozen encoder and ridge reproduction | blocked | Reproduce the exact encoder/head on the qualified cohort with frozen folds, accuracy/bias/correlation, nonfinite, identity and constant controls. |
| `RG-06` external accuracy generalization | blocked | Score the exact artifact on a reviewed multi-speaker/multi-meeting corpus with pre-agreed margins. |
| `RG-07` rate-profile mapping, buffering and preservation | blocked | Measured source/output mapping, 1×/rate-change, duration, pitch, transient, buffering, rebuffer, drift, final partial window and preservation. |
| `RG-08` provider intake, device timing and release | blocked | Target-device timing/resources/deadlines and a separate OFF-by-default versioned provider intake with independent exact-head review. |

No synthetic admission control or arithmetic case opens a gate. No missing
result is promoted.

## Separation from other evidence

`SDK-DYNAMIC-INT8-WAV2VEC2-BASE` and
`SDK-DISTIL-WAV2VEC2-ADULT-CHILD-RIDGE` are merged wav2vec2 rate-encoder/ridge
boundaries, not WavLM evidence. `SDK-SMALL-LOG-MEL-GRU`, `SDK-SYLNET` and
`SDK-USC-MRATE` are merged rate-estimator pilots with different front ends.
`SDK-PHASE-VOCODER-BASELINE` is a model-free rate baseline.
`SDK-VOSK-SMALL-EN-US-0-15-PLAYBACK-GATE` is a rate-playback DEFER boundary.
None is pooled, reinterpreted or substituted for this gate. The source-reported
WavLM values are provenance only and are not repeated as local results.

## Expected digest

`report.json` SHA-256:
`cc20fc6696d723163b0213702c32d014e67758d670cd7685cefb49add1d30b2f`.
