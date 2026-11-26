<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DUALVC-3 — DualVC 3 source, weights, runtime and rights blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DualVC 3` (`component_id=dualvc-3`, `task=SDK-DUALVC-3`). The structured
inventory assigns the **Voice** acceptance profile
(`verification_profile=voice`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before any
implementation, intake or exposure step; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute DualVC 3, a checkpoint, a weight fragment, an encoder, a vocoder,
PyTorch, ONNX Runtime, a reference voice or an inference path. It decodes,
plays and analyzes no audio, converts no voice and measures no content,
identity, similarity, naturalness, alignment, first-output/tail, peak, device
timing, resource, benchmark or release result. It records the exact missing
artifacts and rights, probes a fixed list of workspace, research, adapter,
environment and home-cache paths to evidence their absence, and defines a
fail-closed request boundary that a future qualified run would need. Only
`docs/task-evidence/dualvc-3/` is written; no provider, registry, descriptor,
public header/ABI, shared CMake, CI workflow or installed-v0 behaviour changes.

## Exact external blocker

The catalogued record (`plan/INVENTORY.json`, `id=dualvc-3`) is
`considered`, `disposition=sdk-model`, `verification_profile=voice`. Its only
evidence link is `research/accent-conversion-20261101/README.md`, line 178:

> **DualVC 3** | Paper/demo inspected; no official runnable checkpoint found. |
> Streaming generic VC, not dedicated accent normalization.
> [Paper/demo](https://arxiv.org/abs/2406.07846)

Consequently:

- no DualVC 3 source tree, release archive, checkout or adapter is staged at
  `research/accent-conversion-20261101/repos/dualvc*`,
  `research/voice-conversion-eval-20261101/repos/dualvc*`,
  `data/checkouts/dualvc*` or `adapters/dualvc*`;
- no immutable source revision, tree digest, file count or upstream license
  exists for the candidate;
- no checkpoint or weight file, SHA-256, byte count, model card, tensor/config
  layout, sample rate, hop, chunk scheme, lookahead, alignment or numeric output
  exists for the candidate;
- no runtime environment, lockfile, wheel hash set or importable model runtime
  exists; `torch`, `torchaudio`, `onnxruntime`, `numpy`, `soundfile`,
  `huggingface_hub` and `transformers` are all absent from the interpreter used
  here;
- no code, weight, training-data, corpus, reference-voice, target-voice,
  consent or output-use rights record exists;
- no real source/target voice pair, permission record, transcript truth,
  identity score, naturalness rating or listening result exists;
- no target-device timing, independent review, provider intake or release
  approval exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; the machine-readable blocker records are
in `contract.json` and `report.json`.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The exact licensed DualVC 3 source: a resolvable upstream repository or release archive, immutable 40-hex revision, tree digest, file count and complete license/notice bundle. No source identity was located. |
| `BLK-02` | The official DualVC 3 checkpoint and every required config/tokenizer/vocoder asset, each with byte count, SHA-256, tensor/config manifest and reviewed weight/model-card terms. |
| `BLK-03` | A reproducible isolated CPU runtime matching the checkpoint (PyTorch or ONNX Runtime plus audio frontends), with a lockfile/wheel hash set, install digest and a fail-closed offline load path. |
| `BLK-04` | Reviewed code, weight, training-data and corpus terms plus explicit source-speaker consent, target-voice consent, reference availability and output-use terms. |
| `BLK-05` | A rights-cleared, consented frozen speech-to-speech cohort with manual transcripts, language/speaker groups, exact target conditions and matched-target, mismatched-target and identity-passthrough controls. |
| `BLK-06` | An agreed Voice protocol that separately measures content preservation, identity/similarity, naturalness, alignment, first-output/tail, nonfinite/peak behaviour, independent listening, device timing, resources and uncertainty. Provider intake is conditional on all prior gates. |

The linked note also classifies DualVC 3 as **generic streaming VC, not
dedicated accent normalization**. No accent-conversion claim is made, and the
row is not promoted into any accent result.

**Reopen condition.** A caller supplies the exact licensed source at an
immutable revision, the official checkpoint with per-file digests, a reviewed
weight/model-card and notice bundle, a locked runtime that loads the snapshot
offline, code/weight/training-data/corpus and voice consent/output-use records,
a frozen rights-cleared cohort with manual transcripts and matched controls,
and the independent quality/listening/timing protocol with agreed margins. The
pinned runtime reproduces approved reference outputs, and a separate versioned
intake records opt-in registration with an OFF default and independent exact-head
review. Until then this task stays `DEFER`.

## Historical execution: none

There is **no** historical DualVC 3 execution in the workspace to preserve.
`research/accent-conversion-20261101/README.md` lists DualVC 3 in its candidate
acquisition table only, with paper/demo inspection and no runnable checkpoint.
`research/voice-conversion-eval-20261101/` has no DualVC 3 row or artefact.
`report.json` therefore records
`historical_evidence.status="no_local_dualvc3_execution_record"`,
`records_found=0`, `source_reported_results=null` and empty audio/metrics lists.
No paper-reported latency, RTF, WER, similarity or MOS is used as a local
measurement.

## What this package actually verifies

1. **Exact linked evidence.** The inventory row and the README line are
   projected field-by-field; the line text, line number, required tokens and
   own SHA-256 are verified. A changed row or line fails closed.
2. **Absence evidence.** Ten fixed source paths, seven fixed weight paths, four
   fixed runtime paths, a bounded filename search over the
   `research/data/adapters/configs` roots (9,556 entries, not truncated) and a
   read-only Hugging Face cache listing are checked. Every candidate path and
   name match is absent. `reference.build_report()` and `verify.py` fail if a
   probe later appears, so a stale “absent” claim cannot be shipped. The only
   DualVC-named directory in the workspace is this task worktree
   (`worktrees/audio-sdk/SDK-DUALVC-3`), which is explicitly excluded as a
   worktree name, not a candidate artefact. The cache has three top-level
   entries (`models--FunAudioLLM--CosyVoice2-0.5B`,
   `models--ResembleAI--chatterbox-nano`, `version.txt`); none is DualVC 3 and
   none is used.
3. **Fail-closed request boundary.** A strict request schema rejects an
   unknown or missing field, wrong candidate, wrong rate/channels/frame, wrong
   sample count, empty samples, booleans, strings, nulls, nonfinite values,
   out-of-range values, negative or non-integral epoch, negative position,
   closed/drained lifecycle, unknown execution mode and any target condition
   other than the explicit unspecified placeholder. The 24 adverse request
   cases, 7 invalid-JSON cases and 8 reset cases are deterministic; a valid
   request still raises `SOURCE_WEIGHTS_RUNTIME_ABSENT`.
4. **Structural reset validation.** `validate_reset` requires a strictly
   increasing epoch and a nonnegative position. It owns no candidate state and
   executes no reset; it proves the admission arithmetic only.
5. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, content preservation, identity/similarity, naturalness, alignment,
   first-output/tail, exact target condition and independent consent/reference/
   output-use gates are each recorded as **blocked**.
6. **Quality and timing accounting.** Content, identity and naturalness are
   separate blocked outcomes; alignment, first-output/tail, device timing,
   peaks and resources are separate blocked rows. No value is inferred from the
   paper, a sibling package or the installed v0 format.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml`, the SDK README,
   `scripts/ci.py` and five merged sibling evidence packages are pinned by
   SHA-256 and verified unchanged.
8. **Determinism and cold start.** `run.py` regenerates `report.json`,
   `report.json.sha256`, `SOURCES.sha256` and `contract.json`; `verify.py`
   rebuilds every payload in memory and runs three independent cold-start
   comparisons. Canonical JSON is sorted-key, compact, `allow_nan=False`, with
   exactly one trailing LF.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze permitted input and target references, task and language/speaker groups | blocked | No source utterance, target voice, consent record, language/speaker group or frozen target condition. |
| Preserve text and semantic content | blocked | No model, manual transcript, cohort or reproduced content metric. |
| Identity/similarity as a separate outcome | blocked | No target-voice reference, similarity score, independent encoder or human identity rating. |
| Naturalness as a separate outcome | blocked | No naturalness rating, blinded listening or preference panel. |
| Record alignment | blocked | No documented hop, chunk, lookahead, content delay or alignment measurement. |
| Record first-output/tail timing | blocked | No output chunks, first-output or tail timing record. |
| Record the exact target condition | blocked | No documented target voice or target condition; only an explicit unspecified placeholder is admitted. |
| Consent, reference availability and output use as independent gates | blocked | No code/weight/data/corpus/voice consent, availability or output-use record. |

## Request contract (task-local; not an SDK, DualVC 3 or Voice contract)

- Exactly ten fields: `candidate` (`dualvc-3`), `sample_rate_hz` (`16000`),
  `channels` (`1`), `frame_samples` (`160`), `samples` (exactly 160 finite
  floats, `abs<=4`), `epoch` (nonnegative integer), `first_input_sample`
  (nonnegative integer), `lifecycle` (`prepared` or `processing`),
  `execution_mode` (`1`, `2` or `3`) and `target_condition`
  (`streaming_generic_target_unspecified`).
- Unknown and missing fields are rejected. Booleans and floats are not
  accepted where integers are required. `NaN`, `Infinity`, strings and nulls
  are rejected as samples.
- A valid request raises `SOURCE_WEIGHTS_RUNTIME_ABSENT` before any candidate
  call. There is no fallback, surrogate converter or identity substitution.
- Reset requires `epoch > previous_epoch` and a nonnegative position; equal,
  lower, negative, boolean and float epochs are rejected.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local
artifact and excludes its own bytes. The mutable shared board is **not** pinned;
only the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Exact `dualvc-3` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `source:research/accent-conversion-20261101/README.md` | `c266b6486939b6af0a244358f8273325a23d9ec0733b9ed16686f8e6d25a3a9c` | Exact line-178 evidence row |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI entry |
| `docs/task-evidence/survey-trn-03/README.md` | `9f1310a624f14d5238dfee2566cbd0dcf1e7f1c17a94ef445644ae90a7309f50` | Merged accent map, boundary only |
| `docs/task-evidence/survey-trn-03/report.json` | `aef09671dd0bf39ec7996096f5a866bff564b0110bc1a1e6340fd5fb993f5fe2` | Merged accent map, not reused |
| `docs/task-evidence/survey-trn-04/README.md` | `e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae` | Merged VC survey, boundary only |
| `docs/task-evidence/survey-trn-04/report.json` | `fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446` | Merged VC survey, not reused |
| `docs/task-evidence/llvc/README.md` | `f6d663bc171026181107a6e9ddcf1356fa9eb9e2fd16625267b35a5bc3bda717` | Sibling VC blocker, boundary only |
| `docs/task-evidence/llvc/report.json` | `22d30a3c4f70143ba38f099019c3fcc6b123f4f4f3120f6ee73932d82fed342f` | Sibling VC blocker, not reused |
| `docs/task-evidence/chatterbox-vc/README.md` | `7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c` | Sibling VC blocker, boundary only |
| `docs/task-evidence/chatterbox-vc/report.json` | `321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee` | Sibling VC blocker, not reused |
| `docs/task-evidence/convert-and-speak/README.md` | `a89653d3b127f7d2b6cc7f5abc767fb24259b580b4dec2e29ddaed10c74630be` | Sibling VC blocker, boundary only |
| `docs/task-evidence/convert-and-speak/report.json` | `2423c9cff507fd2c88045ca279367da76a2355168af3d62f29aea425630fcce1` | Sibling VC blocker, not reused |

`report.json` carries the same `source_pins` and `boundary_pins` maps, and
`verify.py` recomputes every digest. The shared board row is read only through
the stable projection `{id,title,component,mode,repository}`; `status`, `owner`,
`claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` are
excluded, so a board state transition cannot promote or block this package.
The full mutable `TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Source/weight/runtime/voice rights boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/projection checks, request/reset validators, canonical report. |
| `run.py` | Byte-identical regeneration of `report.json`, `report.json.sha256`, `SOURCES.sha256` and `contract.json`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, absence, gates, licensing, merge-base scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/dualvc-3` with Python 3.11+ and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py --all
python3 -m unittest -v test_reference.py
python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` prints matching report/sidecar/sources/contract digests;
three independent `run.py --verify-repro` cold starts each print `ok=1` with
identical digests, and `verify.py` prints `pins_ok=35 reproduction_ok=1
repeats_ok=3 semantics_ok=1 boundary_ok=1 licensing_ok=1 git_scope_ok=1
absent_source_weights_ok=1`; all unittest checks pass with 0 failed and 0
skipped; REUSE reports no missing or bad license; `git diff --check` is clean.
`verify.py` writes only to the current interpreter's subprocess pipes and never
to this package.

Scope verification compares the branch against the newest merge-base between
`HEAD` and `origin/main` (falling back to `main`), not a fixed historical
commit. Commits merged into `main` after this task therefore never count as
this branch's out-of-scope edits. Any committed or uncommitted path outside
`docs/task-evidence/dualvc-3/` still fails as `base_out_of_scope_change`, and
an unresolvable base ref fails closed as `scope_base_unavailable`.

Current counts: 10 source-path + 7 weight-path + 4 runtime-path probes (0
present), 9,556 bounded name-search entries (0 DualVC matches), 3 Hugging Face
cache entries (0 DualVC matches), 24 rejected request controls, 7 rejected
invalid-JSON cases, 8 reset controls (1 expected accept), 8 blocked Voice rows,
3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates, 0
qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license | blocked | Exact licensed source with 40-hex revision, tree digest, file count and license/notice bundle supplied and reviewed. |
| `RG-02` weights, assets, model card and terms | blocked | Official checkpoint plus config/tokenizer/vocoder assets with per-file digests and reviewed weight/model-card terms. |
| `RG-03` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned snapshot offline with a fail-closed missing-asset path. |
| `RG-04` code/data/voice rights and output use | blocked | Reviewed code/weight/training-data/corpus terms plus source and target voice consent, availability and output-use records. |
| `RG-05` rights-cleared voice cohort and separate outcomes | blocked | Immutable cohort, manual transcripts, groups, target conditions, matched controls, and separate content/identity/naturalness/listening results. |
| `RG-06` chunking, alignment, timing and numerical behavior | blocked | Documented and measured chunk/hop/lookahead/delay, alignment, first-output/tail, peaks, nonfinite and reset behavior. |
| `RG-07` target-device timing, resources and listening | blocked | Paced device runs record timing, content delay, CPU, memory and callback suitability with approved listening/ASR controls. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision, independent exact-head review and release approval. |

No synthetic control or sibling package opens a gate. No missing result is
promoted.

## Separation from other evidence

`survey-trn-03` maps DualVC 3 as a `source_reported_research_candidate` with no
local accent-aware streaming run; `survey-trn-04` links it at the
speech-to-speech VC boundary. This package does not reuse either package's
numbers, status or conclusions. The merged `llvc`, `chatterbox-vc` and
`convert-and-speak` packages are separate Voice-profile proposals with their own
assets, fixtures, metrics and dispositions; none is pooled, scored or
reinterpreted as DualVC 3 evidence. TokAN, MeanVC2, Seed-VC, RVC, OpenVoice,
CosyVoice 2, Kokoro and other voice results are boundaries only. The three
L2-ARCTIC clips described in the shared accent note are not DualVC 3
input/target pairs and are not used here.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only
(`tasks[id=SDK-DUALVC-3]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed, pinned or used as a digest source. No
provider, descriptor, registry, installed default, shared build or CI is
changed.

## Expected digest

`report.json` SHA-256:
`c1291422d48e3b15d8d6539d2c399b680a35ac37502ccc54b719fc54dc11b8be`.
