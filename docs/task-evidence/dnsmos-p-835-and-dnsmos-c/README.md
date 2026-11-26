<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DNSMOS-P-835-AND-DNSMOS-C — DNSMOS P.835 / DNSMOS-C blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DNSMOS P.835 and DNSMOS-C` (`component_id=dnsmos-p-835-and-dnsmos-c`). The
structured inventory assigns the **Evidence** acceptance profile
(`verification_profile: evidence`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

The package keeps **two distinct scorers** separate, because they are not the
same protocol and not interchangeable:

- **DNSMOS P.835** — two ONNX models (`sig.onnx`, `bak_ovr.onnx`) behind the
  DeepFilterNet-packaged `df/scripts/dnsmos.py` scorer, predicting SIG, BAK and
  OVL over 9.01 s windows with a 1 s hop.
- **DNSMOS-C** — the separate NISQA-checkpoint protocol
  (`runs/NISQA/model_best.pt`) that scores only `primary` and `mix` segments,
  repeats short segments to 10 s, uses 10 s windows with a 5 s hop and an
  end-aligned tail, then averages three scenarios equally.

Neither scorer can run here. The package does **not** import, load, link,
execute, emulate, copy or download either scorer, its weights, its source, ONNX
Runtime, PyTorch, NISQA, librosa or numpy. It does not listen, measure a device,
time a callback, run a benchmark or make a release claim. It reproduces only the
documented **windowing, tiling, post-processing and aggregation arithmetic** over
declared synthetic inputs, records the exact missing artifacts and rights, and
proves that no substitute packaging is admitted.

Only `docs/task-evidence/dnsmos-p-835-and-dnsmos-c/` is written; no provider,
descriptor, registry, default, installed-v0, ABI, shared-build, CI, board or
handoff file changes.

## Exact blocker

The task row's only evidence link is
`research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md`, which
records a 743-item EARS P.835 screen executed elsewhere. The second protocol,
DNSMOS-C, is documented in `research/cpp-library-krisp-benchmark-20261109.md`
and is owned by the separate Krisp comparison rows. Neither report supplies the
bytes needed to reproduce a prediction here.

1. **No P.835 weights.** The expected `data/models/dnsmos-p835/sig.onnx`
   (SHA-256 `d2fbdb293bc2366dfbae2b7477c490f981d24a8b4405efd3c11787569c6549d7`)
   and `data/models/dnsmos-p835/bak_ovr.onnx` (SHA-256
   `5f335c90994618150192a656a474bcf8a9cbcedbc47965494ba8da79605d1308`)
   are absent. `data/models` does not exist. Nothing was downloaded, copied or
   substituted.
2. **No P.835 scorer.** The recorded scorer path
   `data/envs/deepfilternet3/lib/python3.10/site-packages/df/scripts/dnsmos.py`
   (SHA-256
   `abcfd3ee61b37a45728b2c7faaed8ced710e11e01d0a58daf4377363bc719fbb`) and its
   environment are absent; no official DNS-Challenge checkout is present either.
3. **No DNSMOS-C checkpoint or source revision.** `runs/NISQA/model_best.pt` is
   absent. The pinned report records no checkpoint digest and no immutable
   DNSMOS-C scorer-code revision, so the checkpoint identity itself is
   unresolved.
4. **No approved runtime.** `onnxruntime` is importable in neither the default
   `python3` 3.11.5 nor the pinned 3.12.16 interpreter; no torch/NISQA runtime
   is pinned. An incidental environment would not be a qualification.
5. **No rights-cleared cohort.** The 743-item EARS media is CC BY-NC 4.0
   non-commercial research media and the 265-output Krisp set is CC BY-NC 4.0.
   Neither clears redistribution of audio, outputs or derived score bundles, and
   the run directories and downloaded outputs are not staged here.
6. **No scored result, listening result, device timing or benchmark.** Every
   score slot is `null` with an explicit `unavailable` status.

### Incidental copies are not admitted

An unrelated voice-conversion research checkout contains two ONNX blobs:

| Observed file | SHA-256 | Identity |
| --- | --- | --- |
| `model_v8.onnx` | `9246480c58567bc6affd4200938e77eef49468c8bc7ed3776d109c07456f6e91` | DNSMOS P.808 packaging, not a P.835 model |
| `sig_bak_ovr.onnx` | `269fbebdb513aa23cddfbb593542ecc540284a91849ac50516870e1ac78f6edd` | combined P.835 packaging, not the two pinned files |

They live under
`research/voice-conversion-eval-20261101/repos/seed-vc/baselines/dnsmos`,
carry no per-file terms, model card or verified revision, and do not match the
pinned EARS artifacts. They are recorded as **unadmitted**; `verify.py` checks
that no incidental file can be admitted. No P.808 score is used as a P.835
substitute and no combined model is presented as the two separate weights.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-DNSMOS-P-835-AND-DNSMOS-C`, `7c6653f5a7db7f6de34ad709a96a455a9ad3263a` |
| Task mode | `research-control` |
| Acceptance profile | `evidence` |
| Decision | `DEFER` before `processor_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| P.835 geometry | 16 kHz mono; 9.01 s / 144160-sample window; 1 s / 16000-sample hop |
| P.835 outputs | `SIG`, `BAK`, `OVL` (predictions, never human MOS) |
| DNSMOS-C geometry | 16 kHz; `primary`/`mix` only; ≥1 s; repeat <10 s to 10 s; 10 s / 5 s hop; end-aligned tail |
| DNSMOS-C output | `DNSMOS_C` (prediction, never human MOS) |
| Provider registration, default, ABI, CI | none |

## P.835 window arithmetic

The historical helper doubles the buffer until it reaches at least 144160
samples, then computes `num_hops = int(floor(len/16000) - 9.01) + 1` and slices
windows of 144160 samples at a 16000-sample hop. Because each doubling repeats
the whole buffer, a padded index maps to `index mod input_samples`.
`reference.py` reproduces only this integer accounting:

| Input samples | Doublings | Padded | Hops | Last window start..end | Uncovered |
| ---: | ---: | ---: | ---: | --- | ---: |
| 12000 | 4 | 192000 | 3 | 32000..176160 | 15840 |
| 144159 | 1 | 288318 | 9 | 128000..272160 | 16158 |
| 144160 | 0 | 144160 | 1 | 0..144160 | 0 |
| 144161 | 0 | 144161 | 1 | 0..144160 | 1 |
| 300000 | 0 | 300000 | 9 | 128000..272160 | 27840 |

These are window counts, not scores. No mel spectrogram, feature value or model
output is computed.

## Documented post-processing arithmetic

The DNSMOS helper family applies a fixed polynomial to the raw SIG/BAK/OVL
outputs. `reference.py` evaluates the documented standard coefficients with
IEEE-754 binary64 Horner arithmetic on declared raw fixture values
`(SIG, BAK, OVL) = (2.5, 3.0, 2.8)`:

| Variant | SIG | BAK | OVL |
| --- | ---: | ---: | ---: |
| standard | 2.532512850 | 3.246400040 | 2.638849867 |
| personalized | 2.758615265 | 3.116676400 | 3.116259658 |

`coefficient_source_verified=false` and `np_polyval_bit_parity_claimed=false`:
the pinned scorer is absent, so the coefficients are transcribed documentation,
not verified parity, and no raw model output exists to map. These numbers are
not MOS values and cannot qualify anything.

## DNSMOS-C segmentation

| Segment (kind, ms) | Dropped | Repeated | Repeat count | Truncated | Windows | Tail |
| --- | --- | --- | ---: | ---: | ---: | --- |
| primary, 999 | yes (<1 s) | no | 0 | 0 | 0 | no |
| mix, 1000 | no | yes | 10 | 0 | 1 | no |
| primary, 4000 | no | yes | 3 | 2000 | 1 | no |
| mix, 10000 | no | no | 1 | 0 | 1 | no |
| primary, 12345 | no | no | 1 | 0 | 2 | yes (2345..12345) |
| mix, 15000 | no | no | 1 | 0 | 2 | no |
| primary, 20000 | no | no | 1 | 0 | 3 | no |

The exact repeat/tail semantics are a reimplementation of the described
protocol and are not verified against the absent official implementation.

## Evidence profile application

`plan/swarm/VERIFICATION.md` Evidence row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Pin the scorer | blocked | P.835 path/digest recorded but absent; DNSMOS-C has no source revision or checkpoint digest |
| Pin the corpus and cohort | blocked | EARS and Krisp sets documented, not staged; CC BY-NC does not clear redistribution |
| Freeze aggregation | synthetic only | Equal-weight mean and three-scenario average on declared synthetic values only |
| Retain failed items and controls | synthetic only | 55 rejected inputs and 8 blocked results retained with exact codes |
| Separate paired/unpaired/synthetic/human/source-reported evidence | proposal only | Predicted scores, human MOS, clean-reference measures and source-reported values are distinct fields |
| Validate one invalid/missing case and one representative valid result | synthetic only | Invalid/missing cases machine-checked; no representative scored result exists to validate |

Every row is `qualifies=false`. Synthetic exactness means only that the fixture
arithmetic is self-consistent.

## Documented historical context (not reproduced here)

These values are preserved as **source-reported predicted scores** from their
own reports. They are not this task's execution, not human MOS and not a
reproduction:

| Source record | Scope | Predicted values |
| --- | --- | --- |
| `agent-dnsmos-ears-743` | 743 EARS items, 9 s / 1 s, ONNX CPU | input SIG/BAK/OVL 3.935/3.273/3.189; FastEnhancer Small 3.800/4.335/3.427; DeepFilterNet3 3.873/4.399/3.575 |
| `cpp-library-krisp-benchmark-20261109` | 265 CC BY-NC items, NISQA-based DNSMOS-C | scenario average raw 3.369; Krisp VI 2.5 Default 3.815; `basic.v1` 3.519; `voice_focus.v1` 3.641 |

Both rows are `reproduced_here=false`, `is_human_rating=false`,
`is_mos=false`. The Krisp report's vendor WER (23.24% → 6.24%) is an
11-configuration aggregate with no local WER and no local Krisp runtime; it is
not used here.

## Adverse, missing and invalid handling

`report.json` records **55 rejected inputs**, each with the exact expected code,
the observed code and unchanged state. Rejections cover: duplicate JSON key,
`NaN`/`Infinity` constants, malformed JSON, top-level non-object, empty
document; boolean/float/zero/negative/text/null/oversized sample counts;
boolean/float/zero/negative/oversized segment durations; unknown/empty segment
kind, empty/non-object/extra-field segment lists; empty/`NaN`/`Infinity`/text/
boolean mean values and empty/two/`NaN` scenario maps; `NaN`/`Infinity`/
out-of-range/boolean/text raw outputs and non-boolean variants; and manifests
with missing/extra fields, unknown metric, wrong rate/channels, malformed
digest, zero bytes, unidentified license, unpinned revision, duplicate model,
wrong model set or path traversal.

Admission tests separately reject `model_v8.onnx` and `sig_bak_ovr.onnx` as
P.835 identities, a wrong digest for `sig.onnx` and an unknown metric. Missing
weights, checkpoints, sources, runtimes, cohorts, listening, device timing,
benchmark and release are `blocked`, never passes.

## Separation from sibling evidence

The merged `aecmos`, `quality-impairment-taxonomy`, `stoi-estoi` and
`srmr-and-reverb-metrics` packages are separate references or blockers with
their own assets, fixtures, metrics and dispositions. This package does not
import, pool, score or reuse their source, fixtures, metrics or results. Their
README/report files are pinned only as read-only boundary references. In
particular, AECMOS is a scenario-aware three-stream echo/degradation predictor,
not a blind single-stream DNSMOS, and the taxonomy row does not contain a scored
DNSMOS bundle.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, controls, gates. |
| `reference.py` | Strict parsers, scorer contracts, window/tiling/post-processing/aggregation arithmetic, report and contract builders. |
| `run.py` | Builds report, contract and manifest; refuses non-identical bytes. |
| `report.json` | Canonical machine-readable Evidence report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, recomputation, absence, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every task-local artifact. |
| `*.license` | REUSE sidecars for the generated JSON and manifest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py`, the test suite and the README digest check.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/voice-enhancement-20261101/agent-dnsmos-ears-743/REPORT.md` | `613f5448418f84a354366de412ecfd8f92a7143b7cea8549899e51dbcb357d21` |
| `source:research/voice-enhancement-20261101/agent-dnsmos-ears-743/score_existing_outputs.py` | `0e0d89720231a161cf4c55dfdbc4c0995a30e377fb97796c5893dcdafd5e8a4b` |
| `source:research/cpp-library-krisp-benchmark-20261109.md` | `7f3c80a2a9f266bbf112fb6ea89bda0bf9ccb1a9045e39cf42fdc5d49496a8e2` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
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
<!-- digest-table: end -->

## Sibling pins (SHA-256)

Read-only boundary references; none is reused as evidence.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sdk:docs/task-evidence/aecmos/README.md` | `502b86005a9782ac5fdb7628b1285adaf535158cd650cc13eda1a22a137b7422` |
| `sdk:docs/task-evidence/aecmos/report.json` | `8055f6627d462c124182743469109a850087c11773899a6f64b02309be16c320` |
| `sdk:docs/task-evidence/quality-impairment-taxonomy/README.md` | `77ad10fae3e41a06adad6cee377616c73dd8d7d458a76c9297aa55d837afcbe5` |
| `sdk:docs/task-evidence/stoi-estoi/report.json` | `a74820ff3e42f80d5ab06038de6ec70989876c6d91b98b34dc059ed2a6858f82` |
| `sdk:docs/task-evidence/srmr-and-reverb-metrics/report.json` | `291897aaacb9d16a40bb68a64dfb84d2c03a559ca9997a9e5fb1c718d633b979` |
<!-- digest-table: end -->

## Scorer manifest contract

`audio-sdk/dnsmos-scorer-manifest/0.1` is modelled metadata only. Required
fields are `schema_id`, `metric` (`dnsmos_p835` or `dnsmos_c`),
`sample_rate_hz` (16000), `channels` (1), `models`, `source_revision` (40-hex)
and `license`. Each model record has exactly `name`, `sha256`, `bytes` and
`license_id`; the model set must match the metric (`sig.onnx` + `bak_ovr.onnx`
for P.835, `model_best.pt` for DNSMOS-C). A valid manifest returns
`admitted_for_execution=false` because this package has no approved runtime,
pinned scorer revision or runner. Presence of a string is never rights
verification.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DNSMOS-P-835-AND-DNSMOS-C/docs/task-evidence/dnsmos-p-835-and-dnsmos-c
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --all
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DNSMOS-P-835-AND-DNSMOS-C diff --check
```

`run.py --all` builds the report, contract and manifest and refuses non-identical
bytes; `verify.py` reruns it three times in cold-start processes and compares
the resulting bytes and stdout.

## Remaining gates (eight blocked)

1. `p835_model_weights_and_terms` exact `sig.onnx` / `bak_ovr.onnx` bytes,
   digests, model cards and weight terms.
2. `dnsmos_c_checkpoint_source_and_terms` exact NISQA checkpoint revision,
   digest, model card, training-data statement and DNSMOS-C source terms.
3. `pinned_scorer_and_runtime` exact scorer revision and approved
   onnxruntime/numpy and torch/NISQA environments.
4. `rights_cleared_cohorts` item-level permissions for the EARS and Krisp sets,
   including redistribution and derived-score policy.
5. `exact_window_and_aggregation_parity` numerical parity for the P.835 replay,
   the DNSMOS-C repeat/tail rules and the three-scenario aggregation.
6. `predicted_score_validation_and_controls` one valid and one invalid/missing
   item validated end to end, with predicted scores never relabelled as human
   MOS, clean-reference accuracy or intelligibility.
7. `listening_and_device_timing_separation` authorized listening kept separate
   from predictions, plus measured target-device timing and memory where a
   device claim is made.
8. `evidence_adapter_intake_and_release_review` opt-in adapter intake,
   independent exact-head review and explicit release admission.

**Reopen condition.** Supply the exact P.835 weights and scorer revision, the
exact NISQA checkpoint and DNSMOS-C source revision, approved pinned runtimes,
item-level rights for a matched cohort, and numerical window/aggregation parity;
then validate one valid and one invalid item end to end and keep predicted
scores labelled as predictions with separate listening and device-timing
evidence. Until then the component stays **DEFER**, **incomplete** and
**not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `native_engine_built=false`,
`sdk_data_dir_added=false`. The board is referenced by stable linked-row fields
only (`tasks[id=SDK-DNSMOS-P-835-AND-DNSMOS-C]`, stable-field identity); the
mutable full `plan/swarm/TASKS.json` is never hashed, pinned or used as a digest
source.
