<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING — task-local DEFER blocker

**Status: `proposal_only_not_qualified`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; `qualifies=false`.** This directory is bounded,
deterministic, task-local evidence for the board row *Krisp Voice Isolation
public output scoring* (`component_id=krisp-voice-isolation-public-output-scoring`,
mode `research-control`). The structured inventory assigns the **Evidence**
acceptance profile (`verification_profile: evidence`, `plan/INVENTORY.json`),
defined in `plan/swarm/VERIFICATION.md`. **No result here qualifies the
candidate, no score is measured, and no processor is exposed.**

Pinned base: `cb3d9812875b741a320c6cfe22de8043952fdd16`.
Branch: `swarm/SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING`.

## Exact blocker: the licensed cohort, scorer and runtime are absent

The only linked evidence is `research/cpp-library-krisp-benchmark-20261109.md`.
It records that 265 Krisp `vi_2_5_default` outputs were downloaded to
`/private/tmp`, scored with a local NISQA-based DNSMOS-C helper, and then
discarded; no audio, transcript, checkpoint, scorer revision or score bundle was
added to any repository. The exact artifacts needed here are therefore absent,
and the report itself records **no NISQA checkpoint digest and no immutable
DNSMOS-C source revision**, so identity cannot be pinned even if a same-named
file appeared.

| Item | Status |
| --- | --- |
| 265 processed `vi_2_5_default` WAVs (647,960,782 bytes, revision `8759715197e39e0356125e3f3197a9854c38fa60`) | **Absent**; no per-file digest manifest |
| 265 raw 32 kHz PCM16 recordings, transcripts, scenario metadata, target-speech labels (revision `626bac8ca07fb9b4846d4f62d27c321753160b36`) | **Absent** |
| NISQA checkpoint `runs/NISQA/model_best.pt` | **Absent**; digest and revision not recorded in the source report |
| Pinned DNSMOS-C feature-extraction source revision | **Absent**; the report names only the project URL |
| Approved `torch`/NISQA/`librosa`/`numpy` runtime, lock and host record | **Absent** |
| Item-level rights for scoring, retention and derived-score redistribution | **Absent**; the corpus is CC-BY-NC-4.0 non-commercial research media |
| Per-item and per-scenario DNSMOS-C score bundle | **Absent**; every real result slot is `null` |
| Local 11-configuration WER ensemble | **Explicitly unrun**; only the vendor/source-reported aggregate is preserved |
| Listening, device timing, benchmark or release evidence | **Absent** |

Nothing was downloaded, copied, reconstructed, substituted or scored. The
bounded absence probes in `report.json` → `absence_probes` are workspace-relative
and currently all `present=false`; `verify.py` fails closed if any later shows
up so the blocker is re-evaluated rather than silently promoted.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-KRISP-VOICE-ISOLATION-PUBLIC-OUTPUT-SCORING`, `cb3d9812875b741a320c6cfe22de8043952fdd16` |
| Task mode | `research-control` |
| Acceptance profile | `evidence` |
| Decision | `DEFER` before `opt_in_evidence_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Cohort | `Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed`, `vi_2_5_default`, 265 items, `CC-BY-NC-4.0` |
| Scorer | DNSMOS-C on the NISQA checkpoint; `primary`/`mix`, ≥1 s, 10 s window / 5 s hop |
| WER | source-reported 11-configuration aggregate; **not run here** |
| Provider registration, default, ABI, CI | none |

- Work is confined to `docs/task-evidence/krisp-voice-isolation-public-output-scoring/`.
  Shared CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, board/handoff files, CI and other worktrees are untouched.
- Board linkage uses **stable row identity only** (`id`, `title`, `repository`,
  `mode`, `component`, `depends_on`, `deliverable`, `acceptance`, `evidence`,
  `write_scope`, claim `base_commit`, claim `branch`). Mutable status, owner,
  review, handoff, priority and history never enter canonical bytes and are never
  a gate. The mutable full `plan/swarm/TASKS.json` is **not hashed** into any
  canonical artifact or into `SOURCES.sha256`.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a scorer:

1. **Strict JSON** with duplicate-key, `NaN`/`Infinity`, malformed, empty, BOM and
   non-object rejection; canonical compact sorted-key bytes with one trailing LF.
2. **Documented protocol arithmetic.** It reproduces only the DNSMOS-C segment
   policy (1 s minimum, 10 s repeat, 10 s window / 5 s hop, end-aligned tail) and
   the equal-weight three-scenario mean over declared synthetic values. No mel
   feature, model output or score is computed.
3. **Caller-supplied cohort contract.** It validates exact dataset/processed
   repositories and revisions, `vi_2_5_default`, 265 items, 647,960,782 total
   bytes, 16 kHz mono, `CC-BY-NC-4.0`, unique item IDs, per-item SHA-256/transcript
   digests, positive sizes and explicit `rights_cleared=true`. A valid manifest
   still returns `admitted_for_scoring=false`.
4. **Caller-supplied scorer contract.** It validates the `dnsmos_c` metric,
   `model_best.pt` name, 40-hex source revision, identified licences and a pinned
   runtime record. A valid manifest still returns `admitted_for_execution=false`.
5. **WER separation.** It accepts only an 11-configuration `jiwer` 4.0.0 /
   NeMo-WFST record whose `library_percent` remains `null`; it never merges WER
   with DNSMOS-C.
6. **Adverse rejection.** 60 malformed, missing, invalid, nonfinite,
   wrong-domain and non-rights-cleared controls are actually invoked; all fail
   closed with exact codes.
7. **Stable board identity** and canonical report/contract bytes.

## Evidence profile application

Each `plan/swarm/VERIFICATION.md` Evidence row is applied in
`report.json` → `acceptance_profile` and checked by `verify.py`:

| Required item | State |
| --- | --- |
| Pin the scorer | `blocked` — checkpoint digest and DNSMOS-C revision are not recorded; no runtime |
| Pin the corpus and cohort | `blocked` — identities recorded, bytes/rights absent |
| Freeze aggregation | `synthetic_control_only` — arithmetic over declared/source-reported values |
| Retain failed items and controls | `synthetic_control_only` — 60 rejection cases, no real failed item |
| Separate paired/unpaired/synthetic/human/source-reported evidence | `proposal_only` — distinct empty/labelled fields |
| Validate one invalid/missing case and one representative valid result | `blocked` — invalid cases checked; no real valid result exists |

`satisfied_for_qualification=[]`, every real `scores` slot is `null`, and no
source-reported value is relabelled as measured.

## Preserved source-reported context (not reproduced)

The following values are retained only as **source-reported** context. They are
not this task's execution, not human ratings and not reproduced here.

| Scenario | Raw | Krisp VI 2.5 Default | `basic.v1` | `voice_focus.v1` |
| --- | ---: | ---: | ---: | ---: |
| Work | 3.374 | 3.944 | 3.575 | 3.636 |
| Call center | 3.600 | 4.018 | 3.794 | 3.829 |
| Phone calls | 3.133 | 3.482 | 3.189 | 3.457 |
| **Scenario average** | **3.369** | **3.815** | **3.519** | **3.641** |

The equal-weight recomputation from the three 3-decimal scenario values matches
the reported average at three decimals, but that is arithmetic, not score
reproduction. The separate WER table (raw 23.24% → Krisp 6.24% over 265 files,
11 configurations) is preserved as `source_reported_not_run_here`; the
`audio_enhance` WER column remains `null`/`not measured`.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `exact_processed_output_identity_and_rights` | No processed WAVs, per-file digests or derived-score permission. |
| `raw_corpus_transcripts_labels_and_rights` | No raw recordings, transcripts, scenario metadata, labels or item-level rights. |
| `dnsmos_c_checkpoint_source_and_terms` | No checkpoint digest, source revision, model card or terms. |
| `approved_scoring_runtime_and_platform` | No pinned/approved torch/NISQA/librosa/numpy host and lock. |
| `scenario_balanced_aggregation_parity` | No numerical parity for segmentation, windows/tail or the 2,352-window / 604-segment accounting. |
| `unrun_wer_ensemble_separation` | No local 11-configuration WER run; the source aggregate stays separate. |
| `valid_invalid_item_validation_and_evidence_separation` | No representative real valid item validated end to end. |
| `evidence_adapter_intake_and_release_review` | No adapter intake, independent review or release admission. |

**Reopen condition.** Supply the exact processed and raw corpora with per-file
digests and item-level rights, the NISQA checkpoint and DNSMOS-C source at
immutable revisions with terms, an approved pinned runtime, and numerical
segmentation/aggregation parity; then validate one valid and one invalid item end
to end, keep DNSMOS-C predictions separate from listening and device timing, and
obtain independent exact-head review. Until then the row stays **DEFER**,
**incomplete** and **not qualified**.

## Reproduction and verification

From this directory, with no bytecode:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
python3 -m reuse lint
```

`run.py --all` rebuilds the report, its SHA-256 sidecar, the contract and
`SOURCES.sha256`, refusing to write unless three in-process builds are
byte-identical; `verify.py` additionally runs three cold-start regenerations in
fresh processes and compares bytes and stdout. Expected: all tests pass and
`verify.py` prints `PASS ... decision=DEFER`.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | Scope, blocker, profile application and gates. |
| `reference.py` | Strict parsers, contracts, protocol arithmetic, report model. |
| `run.py` | 3× byte-identical regeneration; `--check` is read-only. |
| `report.json` / `report.json.sha256` | Canonical evidence and digest. |
| `contract.json` | Task contract, pins, blockers, gates, invariants. |
| `SOURCES.sha256` | Fail-closed SHA-256 manifest for every local artifact. |
| `test_reference.py` | Deterministic unittest acceptance checks. |
| `verify.py` | Read-only pins/JSON/identity/arithmetic/absence/hygiene/scope verifier. |
| `*.license` | SPDX sidecars for generated JSON and manifest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py`, the test suite and this README.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/cpp-library-krisp-benchmark-20261109.md` | `7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Sibling pins (SHA-256)

Read-only boundary references; none is reused as evidence.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sdk:docs/task-evidence/dnsmos-p-835-and-dnsmos-c/README.md` | `eb7d069cc402aa37210dd2ebd43e45e840bc600693a947684e5341eb28fbd579` |
| `sdk:docs/task-evidence/dnsmos-p-835-and-dnsmos-c/report.json` | `f36074f915c3ad94c9441cebc221a23bd7f865969b7fab3009c2baa48ba92bc0` |
| `sdk:docs/task-evidence/ears-preservation-screen-and-scorer-harness/README.md` | `711da725fbddb7ab06272e6e2644a5b960cfb3da42d66748fddf147058dd8ff3` |
| `sdk:docs/task-evidence/ears-preservation-screen-and-scorer-harness/report.json` | `077f6acfb253dfc7d0de6a72b77d1c977fdf5289ec6333d1a3620dd372f45a1f` |
<!-- digest-table: end -->

## Non-claims

No Krisp output, corpus, transcript, checkpoint, scorer, runtime, score, WER
value, listening result, device measurement, benchmark or release result is
claimed. No installed v0, public API, C ABI, descriptor, registry, default,
shared build, CI, board or handoff change is made. Missing evidence never
qualifies this row; the decision remains **DEFER**.
