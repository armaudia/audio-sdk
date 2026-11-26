<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MEANVC — MeanVC source pin and weights/runtime/rights blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`MeanVC` (`component_id=meanvc`, `task=SDK-MEANVC`). The structured inventory
assigns the **Voice** acceptance profile (`verification_profile=voice`,
`plan/INVENTORY.json`), defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, recorded before any model execution, intake or exposure step;
`status=incomplete`, `proposal_only=true`, `qualification.status=not_qualified`.
Missing evidence never qualifies a candidate.

The exact Apache-2.0 upstream source checkout **is present** and is pinned
read-only. It is **not** built, imported, loaded, copied or executed. The five
required checkpoints and a pinned runtime are **absent**, and no rights record
exists. This package does not contain, import, build, link, download, load or
execute MeanVC, a checkpoint, a weight fragment, an encoder, a vocoder,
PyTorch, ONNX Runtime, a reference voice or an inference path. It decodes,
plays and analyzes no audio, converts no voice and measures no content,
identity, similarity, naturalness, alignment, first-output/tail, peak, device
timing, resource, benchmark or release result. Only
`docs/task-evidence/meanvc/` is written; no provider, registry, descriptor,
public header/ABI, shared CMake, CI workflow or installed-v0 behaviour changes.

## Exact external blocker

The catalogued record (`plan/INVENTORY.json`, `id=meanvc`) is `considered`,
`disposition=sdk-model`, `verification_profile=voice`. Its only evidence link is
`research/voice-conversion-eval-20261101/README.md`, line 22:

> | MeanVC | Previous-generation streaming VC baseline | `repos/meanvc` | Not
> downloaded | Not pursued | Superseded by MeanVC2, which was evaluated in both
> documented streaming configurations. |

Consequently:

- the source **is** staged at `research/voice-conversion-eval-20261101/repos/meanvc`
  as ASLP-lab/MeanVC revision
  `fe5286ae205a26ad4eba64395513130bd5974b46`, tree object
  `e80e92c70babd6e1c05d9bda8d3a0852828f860e`, 62 tracked files, tree-content
  SHA-256 `4ce516a3113164a7dd671dc869d42dcfe714c95ad5c359439d15887797b770d5`,
  clean working tree and an Apache-2.0 `LICENSE`;
- every required weight file is absent: `src/ckpt/model_200ms.safetensors`,
  `src/ckpt/meanvc_200ms.pt`, `src/ckpt/fastu2++.pt`, `src/ckpt/vocos.pt` and
  the manual `src/runtime/speaker_verification/ckpt/wavlm_large_finetune.pth`;
- no checkpoint SHA-256, byte count, model card, tensor/config manifest or
  reviewed weight terms exists;
- no runtime environment, lockfile, wheel hash set or importable model runtime
  exists; `torch`, `torchvision`, `torchaudio`, `onnxruntime`, `numpy`,
  `librosa`, `einops`, `x_transformers`, `omegaconf`, `transformers`,
  `huggingface_hub`, `funasr`, `encodec` and `soundfile` are all absent from
  the interpreter used here;
- no code, weight, training-data, corpus, reference-voice, target-voice,
  consent or output-use rights record exists; the linked shared p360 reference
  has unverified dataset/license provenance;
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
| `BLK-01` | The exact MeanVC DiT checkpoint (`model_200ms.safetensors`) with byte count, SHA-256, tensor manifest, config pairing and reviewed weight terms. |
| `BLK-02` | The exact `meanvc_200ms.pt` TorchScript runtime model, `fastu2++.pt` streaming ASR encoder and `vocos.pt` vocoder, each with byte count, SHA-256, role and reviewed terms. |
| `BLK-03` | The exact `wavlm_large_finetune.pth` WavLM+ECAPA speaker checkpoint, which upstream requires manually from Google Drive: no immutable URL, digest, byte count or redistributable identity. |
| `BLK-04` | A reproducible isolated CPU runtime matching the source (Python 3.11; torch==2.5.1, torchvision==0.20.1, torchaudio==2.5.1 plus pinned librosa, funasr, Vocos and audio I/O), with a lockfile/wheel hash set and a fail-closed offline load path. |
| `BLK-05` | Reviewed weight/model-card, training-data and corpus terms plus explicit source-speaker consent, target-voice consent, target-reference provenance and output-use terms. |
| `BLK-06` | A rights-cleared, consented frozen speech-to-speech cohort with manual transcripts, language/speaker groups, exact target conditions and matched-target, mismatched-target and identity-passthrough controls, plus the independent Voice protocol. |

**Reopen condition.** A caller supplies all five exact checkpoints with
per-file digests, a reviewed weight/model-card and notice bundle, a locked
runtime that loads the snapshot offline, code/weight/training-data/corpus and
voice consent/output-use records including target-reference provenance, a
frozen rights-cleared cohort with manual transcripts and matched controls, and
the independent quality/listening/timing protocol with agreed margins. The
pinned runtime reproduces approved reference outputs, and a separate versioned
intake records opt-in registration with an OFF default and independent exact-head
review. Until then this task stays `DEFER`.

## Historical execution: none

There is **no** historical MeanVC execution in the workspace to preserve.
`research/voice-conversion-eval-20261101/README.md` line 22 records MeanVC as
**Not downloaded** and **Not pursued**, superseded by MeanVC2. A separate
MeanVC2 sibling run exists (`results/meanvc2/*`), but MeanVC2 is a different
model with different assets, configurations and metrics. It is **not** reused,
pooled or reinterpreted as MeanVC evidence. `report.json` therefore records
`historical_evidence.status="no_local_meanvc_execution_record"`,
`records_found=0`, `meanvc2_sibling_results_reused=false`,
`source_reported_results=null` and empty audio/metrics lists. No paper-reported
latency, RTF, WER, similarity or MOS is used as a local measurement.

## What this package actually verifies

1. **Exact linked evidence.** The inventory row and README line are projected
   field-by-field; the line text, line number, required tokens and own SHA-256
   are verified. A changed row or line fails closed.
2. **Exact source identity.** The checkout's HEAD, tree object, tree-content
   digest, tracked-file count, clean status and Apache-2.0 LICENSE digest are
   checked. Ten selected source files (LICENSE, README, requirements,
   downloader, configs, inference/model/runtime entry points) are pinned by
   SHA-256. A moved revision, edited file or dirty checkout fails closed.
   No build, import or execution of that source occurs.
3. **Absence evidence for the model.** Five exact required weight paths are
   checked (all absent), ten candidate weight roots are probed, the pinned
   checkout is scanned for the five required filenames (0 matches), and a
   read-only Hugging Face cache listing is checked (3 top-level entries:
   `models--FunAudioLLM--CosyVoice2-0.5B`, `models--ResembleAI--chatterbox-nano`,
   `version.txt`; 0 MeanVC matches). `reference.build_report()` and `verify.py`
   fail if a required weight later appears, so a stale "absent" claim cannot be
   shipped.
4. **Fail-closed request boundary.** A strict request schema rejects an
   unknown or missing field, wrong candidate, wrong rate/channels/frame, wrong
   sample count, empty samples, booleans, strings, nulls, nonfinite values,
   out-of-range values, negative or non-integral epoch, negative position,
   closed/drained lifecycle, unknown execution mode and any target condition
   other than the explicit unspecified placeholder. The 24 adverse request
   cases, 7 invalid-JSON cases and 8 reset cases are deterministic; a valid
   request still raises `WEIGHTS_RUNTIME_ABSENT`.
5. **Structural reset validation.** `validate_reset` requires a strictly
   increasing epoch and a nonnegative position. It owns no candidate state and
   executes no reset; it proves the admission arithmetic only.
6. **Voice profile accounting.** Permitted inputs/targets, language/speaker
   groups, content preservation, identity/similarity, naturalness, alignment,
   first-output/tail, exact target condition and independent consent/reference/
   output-use gates are each recorded as **blocked**.
7. **Documented geometry, not measurement.** The pinned configs document
   16-frame/160 ms and 20-frame/200 ms chunks at a 10 ms mel hop, and the
   runtime script references a 20-frame runtime chunk and 16 kHz output. These
   values are recorded as `documented`, never as measured content delay,
   lookahead, first-output or device timing.
8. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml`, the SDK README,
   `scripts/ci.py` and six merged sibling evidence packages are pinned by
   SHA-256 and verified unchanged.
9. **Determinism and cold start.** `run.py` regenerates `report.json`,
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
| Record alignment | blocked | Documented chunk/hop only; no measured alignment or content delay. |
| Record first-output/tail timing | blocked | No output chunks, first-output or tail timing record. |
| Record the exact target condition | blocked | No documented target voice or target condition; only an explicit unspecified placeholder is admitted. |
| Consent, reference availability and output use as independent gates | blocked | No code/weight/data/corpus/voice consent, availability or output-use record. |

## Request contract (task-local; not an SDK, MeanVC or Voice contract)

- Exactly ten fields: `candidate` (`meanvc`), `sample_rate_hz` (`16000`),
  `channels` (`1`), `frame_samples` (`160`), `samples` (exactly 160 finite
  floats, `abs<=4`), `epoch` (nonnegative integer), `first_input_sample`
  (nonnegative integer), `lifecycle` (`prepared` or `processing`),
  `execution_mode` (`1`, `2` or `3`, corresponding to the documented
  `infer_ref.sh`, `infer.sh` and `run_rt.py` paths) and `target_condition`
  (`documented_target_unspecified`).
- Unknown and missing fields are rejected. Booleans and floats are not
  accepted where integers are required. `NaN`, `Infinity`, strings and nulls
  are rejected as samples.
- A valid request raises `WEIGHTS_RUNTIME_ABSENT` before any candidate call.
  There is no fallback, surrogate converter or identity substitution.
- Reset requires `epoch > previous_epoch` and a nonnegative position; equal,
  lower, negative, boolean and float epochs are rejected.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these, ten selected source files and
every task-local artifact, and excludes its own bytes. The mutable shared board
is **not** pinned; only the stable row identity gates anything.

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Exact `meanvc` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |
| `source:research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` | Exact line-22 evidence row |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/LICENSE` | `c71d239df91726fc519c6eb72d318ec65820627232b2f796219e87dcf35d0ab4` | Apache-2.0 code license |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/README.md` | `5421a6346a5b1fdb93722307898d5019a3c22756b90333139cd0ac30a94b0f8d` | Required weight names and usage |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/download_ckpt.py` | `f08930c9af4afbe6992809dd27a2d0259f8fe2565d98c207b191f8d064d0f83d` | Exact four HF weight names |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/requirements.txt` | `ec3c05f691eb25320a558d046e81858a98695f945f059740ac32bfa33fd71fae` | Runtime pins and gaps |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/src/config/config_160ms.json` | `67d25db60af94999a7cd113409f8d133ca0709e18d35b8307d35cfa2b6f1bffd` | 16-frame/160 ms documented chunk |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/src/config/config_200ms.json` | `48dbed028991270bde75ebaf0ee8ddb83f3cbca11c0d15ace599fc33495f556d` | 20-frame/200 ms documented chunk |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/src/infer/infer.py` | `6bd587b23d10795c05784094e0cb7819838b1c8087afefa0a66a52f51c59f4af` | Offline inference path |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/src/model/cfm_mean_flow.py` | `e688fc07d0832b8e0646bde9d0c9d9b1f47d3e21d087ca416bff43cf7160a83c` | Mean-flow model file, boundary only |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/src/runtime/run_rt.py` | `8efe3c424bf8110169d6a88eb326d81befcd94b11a54f123ade44689b3423325` | Runtime chunk and weight paths |
| `source:research/voice-conversion-eval-20261101/repos/meanvc/default_config.yaml` | `4972d0beb8714d7a25dc99492e26dc6dec52978084b25440c1d7d5285ff06afa` | Training config boundary |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged v0 contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 coverage |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `README.md` (SDK) | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged build surface |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI entry |
| `docs/task-evidence/dualvc-3/README.md` | `24551d07a453de939da409160d6fe330567a92243e8eadc8e04a6685ba98cf70` | Sibling Voice blocker, boundary only |
| `docs/task-evidence/dualvc-3/report.json` | `1eea7877ce934885a2ebe82a1c50b989a33a062b8b7d34f4441786a52d19b0d1` | Sibling Voice blocker, not reused |
| `docs/task-evidence/seed-vc-xls-r-300m-content-encoder/README.md` | `3ffad57b383c93b98b051d10d8bf7f7ce6a4b7c74940611dfd1853269e103f09` | Sibling VC blocker, boundary only |
| `docs/task-evidence/seed-vc-xls-r-300m-content-encoder/report.json` | `0a661101a938600bf26a07b18b6ae0d1fa2c94e6db6394d169dc052b8b3d19ef` | Sibling VC blocker, not reused |
| `docs/task-evidence/chatterbox-vc/README.md` | `7a624864df916ef87b32655e6e0894bfe00c3da94ca6969352be68654ee1443c` | Sibling VC blocker, boundary only |
| `docs/task-evidence/chatterbox-vc/report.json` | `321fe22b052823b43d772871b5b694df03c0586c6754c04491d40406055b3dee` | Sibling VC blocker, not reused |
| `docs/task-evidence/llvc/README.md` | `f6d663bc171026181107a6e9ddcf1356fa9eb9e2fd16625267b35a5bc3bda717` | Sibling VC blocker, boundary only |
| `docs/task-evidence/llvc/report.json` | `22d30a3c4f70143ba38f099019c3fcc6b123f4f4f3120f6ee73932d82fed342f` | Sibling VC blocker, not reused |
| `docs/task-evidence/survey-trn-04/README.md` | `e0b4ea4d92b122e9820b9857da5e4813db29b048468f2b0383e67ef4264eccae` | Merged VC survey, boundary only |
| `docs/task-evidence/survey-trn-04/report.json` | `fb34a1129db91808c450cf9ce90d68a2f2ff34734b26891763ede6b0915f0446` | Merged VC survey, not reused |
| `docs/task-evidence/vocos/README.md` | `9874b61a5acef218c59ae0fbbdf6165ec3e65c69d12010150a4b041d814c66dd` | Vocoder sibling, boundary only |
| `docs/task-evidence/vocos/report.json` | `3f961e3fbffb63af701e38dd16914711288facb7f1285b054a2ffc1a5ad3b059` | Vocoder sibling, not reused |

`report.json` carries the same `source_pins`, `source_artifacts` and
`boundary_pins` maps, and `verify.py` recomputes every digest. The shared board
row is read only through the stable projection
`{task_id,title,mode,repository,component}`; `status`, `owner`, `claim`,
`review`, `handoff`, `blocked_reason` and `dispatch_priority` are excluded, so a
board state transition cannot promote or block this package. The full mutable
`TASKS.json` bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Source/weight/runtime/voice rights boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, snapshot, blockers, eight gates, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, source/absence probes, request/reset validators, canonical report. |
| `run.py` | Byte-identical regeneration of `report.json`, `report.json.sha256`, `SOURCES.sha256` and `contract.json`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, source/weights/runtime state, gates, licensing, merge-base scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/meanvc` with Python 3.11+ and stdlib only:

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
identical digests, and `verify.py` prints `pins_ok=47 reproduction_ok=1
repeats_ok=3 semantics_ok=1 boundary_ok=1 licensing_ok=1 git_scope_ok=1
source_pinned_weights_runtime_absent_ok=1`; all unittest checks pass with 0
failed and 0 skipped; REUSE reports no missing or bad license; `git diff
--check` is clean. `verify.py` writes only to the current interpreter's
subprocess pipes and never to this package.

Scope verification compares the branch against the newest merge-base between
`HEAD` and `origin/main` (falling back to `main`), not a fixed historical
commit. Commits merged into `main` after this task therefore never count as
this branch's out-of-scope edits. Any committed or uncommitted path outside
`docs/task-evidence/meanvc/` still fails as `base_out_of_scope_change`, and an
unresolvable base ref fails closed as `scope_base_unavailable`.

Current counts: 4 linked-input pins + 10 pinned source-file digests + 1 exact
source revision/tree identity + 5 required weight paths (0 present) + 10
weight-root probes + 4 runtime-path probes + 3 Hugging Face cache entries (0
MeanVC matches) + 20 boundary pins, 24 rejected request controls, 7 rejected
invalid-JSON cases, 8 reset controls (1 expected accept), 8 blocked Voice rows,
12 blocked required-result rows, 8 blocked gates, 0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision, archive and license | blocked | Reviewed release-source decision for the pinned revision, archive digest, file count and complete license/notice bundle. |
| `RG-02` weights, assets, model card and terms | blocked | All five official checkpoints with per-file digests and reviewed weight/model-card terms. |
| `RG-03` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned snapshot offline with a fail-closed missing-asset path. |
| `RG-04` code/data/voice rights and output use | blocked | Reviewed weight/training-data/corpus terms plus source and target voice consent, verified target-reference provenance, availability and output-use records. |
| `RG-05` rights-cleared voice cohort and separate outcomes | blocked | Immutable cohort, manual transcripts, groups, target conditions, matched controls, and separate content/identity/naturalness/listening results. |
| `RG-06` chunking, alignment, timing and numerical behavior | blocked | Documented and measured chunk/hop/lookahead/delay, alignment, first-output/tail, peaks, nonfinite and reset behavior. |
| `RG-07` target-device timing, resources and listening | blocked | Paced device runs record timing, content delay, CPU, memory and callback suitability with approved listening/ASR controls. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision, independent exact-head review and release approval. |

No synthetic control, pinned source or sibling package opens a gate. No missing
result is promoted.

## Separation from other evidence

`survey-trn-04` links MeanVC at the speech-to-speech VC boundary only. This
package does not reuse that package's numbers, status or conclusions. The
merged `dualvc-3`, `seed-vc-xls-r-300m-content-encoder`, `chatterbox-vc`,
`llvc` and `vocos` packages are separate proposals with their own assets,
fixtures, metrics and dispositions; none is pooled, scored or reinterpreted as
MeanVC evidence. The local MeanVC2 run in `research/voice-conversion-eval-20261101`
is a different model and is not reused. TokAN, Seed-VC, RVC, OpenVoice,
CosyVoice 2, Kokoro and other voice results are boundaries only.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `native_engine_built=false`, `sdk_data_dir_added=false`.
Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row fields only (`tasks[id=SDK-MEANVC]`,
stable-field digest); the mutable full `plan/swarm/TASKS.json` is never hashed,
pinned or used as a digest source. No provider, descriptor, registry, installed
default, shared build or CI is changed.

## Expected digest

`report.json` SHA-256:
`e9ce6e224056838848aa5bbe52c2bfa0e1f60abb3ffbf2f7c08449e00c983164`.
