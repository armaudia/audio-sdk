<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RVC-FAISS-RETRIEVAL — RVC FAISS retrieval blocker package

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`RVC FAISS retrieval` (`component_id=rvc-faiss-retrieval`). The structured
inventory assigns the **Voice** acceptance profile
(`verification_profile: voice`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain, import, build, link, download, load or
execute RVC, `Mp226rmvpe.pth`, the IVF1161 FAISS index, `faiss-cpu`, PyTorch,
TorchAudio, numpy or soundfile. It decodes, plays and analyzes no audio,
executes no FAISS search, reproduces no crash, converts no voice and measures no
content, identity, similarity, naturalness, alignment, first-output/tail, peak,
device timing, resource, benchmark or release result. Only whole-file SHA-256
and byte-count provenance checks are performed on the historical media path,
and it is not loaded as a signal. It records the exact missing artifacts and
rights, probes a fixed list of workspace and home-cache paths to evidence their
absence, isolates the **pinned call sites** of the locally observed crash
without claiming a root cause, defines the no-retrieval conditioning control as
an unpaired historical observation, and defines a fail-closed admission
boundary for a future qualified reproducer. Only
`docs/task-evidence/rvc-faiss-retrieval/` is written; no provider, registry,
descriptor, public header/ABI, shared CMake, CI workflow or installed-v0
behavior changes.

## Exact external blocker

The RVC fork checkout is present at the pinned revision
`81eed5e8f68b6bed1789f682fe78cdd324495afc` with an MIT `LICENSE`. The p226
checkpoint `Mp226rmvpe.pth`, the matching 137 MB
`added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index`, the FAISS/Torch runtime and
the original crash trace are **absent**. The whole historical `models` tree is
gone; the current interpreter has no `faiss`, `torch`, `torchaudio`, `numpy` or
`soundfile` module; the historical venvs are gone; the local Hugging Face cache
has no `Nekochu/RVC-VCTK_Voice-sample` entry. No download, reconstruction or
substitute was attempted. Source-code presence is not a checkpoint, index,
dataset, voice, consent or output-use grant.

Seven exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The immutable `Mp226rmvpe.pth` checkpoint with a 40-hex revision, byte count, SHA-256 and reviewed weight terms. |
| `BLK-02` | The matching `added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index` (reported approximately 137 MB) with bytes, SHA-256 and recorded `d=768`, `IndexIVFFlat`, `nlist=1161`, `nprobe=1`, metric L2 and `ntotal`. |
| `BLK-03` | A locked Python 3.11 runtime with the documented torch 2.15.0 / torchaudio 2.11.1 main stack, a pinned `faiss-cpu>=1.13.0` build, recorded OMP/OpenBLAS threads and a fail-closed offline load. Historical FAISS version/build was never recorded. |
| `BLK-04` | The retained crash artifact: exact invocation, stdout/stderr/native stack, exit code or signal, FAISS build, query/index/checkpoint digests and a minimized failing case. |
| `BLK-05` | A paired no-retrieval control from the same staged artifacts, runtime and input as the retrieval-enabled failure, with both outputs, logs and timings. |
| `BLK-06` | A reviewed 109-entry speaker map. The checkpoint has no `speaker_info`; `speaker_id=1 -> p226` is presumed from the path and VCTK order, not verified. |
| `BLK-07` | Reviewed checkpoint/index/dataset terms, source-speaker and target-voice consent, reference availability, output use, a rights-cleared frozen cohort and the agreed Voice quality/timing/listening protocol. |

**Reopen condition.** A caller supplies the immutable checkpoint and index with
every digest and metadata field, the reviewed terms and consents, the locked
runtime, the complete retained crash artifact plus a paired control, the
verified speaker map and the rights-cleared voice protocol. The pinned runtime
reproduces the failure and the control three times, and a separate versioned
intake records opt-in registration with an OFF default and independent
exact-head review. Until then this task stays `DEFER`.

## What "isolation" means here

The research record says enabling the matching index "crashes inside native
`index.search()`" and that retrieval was disabled for the retained output. No
traceback, signal, stderr, FAISS build string, index metadata or minimal case
survives. This package therefore pins the exact reachable call sites and
records the missing evidence rather than inventing a root cause:

| Path | Pinned fact |
| --- | --- |
| Offline `infer/vc/pipeline.py` | `Pipeline.vc` calls `score, ix = index.search(npy, k=8)` at line 186 with **no try/except** at the call site. `read_index`/`reconstruct_n` are caught separately at lines 279-283 and degrade to `index = None`; a native abort at `search` would not be caught. |
| Realtime `infer/rtrvc.py` | `self.index.search(npy, k=8)` at line 253 sits inside `except Exception:` / `traceback.print_exc()` at lines 274-275. A native abort is still uncatchable. The realtime/Metal path was not exercised. |
| Builder `train/train_index.py` | `faiss.index_factory(256 if version == "v1" else 768, "IVF%s,Flat")` at lines 209-210 with `nprobe=1`; consistent with the `_v2` 768-d index name. |
| Resolver `infer/cli.py` | `if index_rate == 0:` selects the no-retrieval condition; `trained` names are rewritten to `added`. |

The deterministic reference models only the **branch contract** (index_rate=0
control vs the guarded retrieval branch, dimension/finiteness/k/nprobe
preconditions). It does not allocate a matrix, read an index or run a search.
`retrieval_isolation.crash_observation.isolation_status` is
`call_site_pinned_but_root_cause_unlocalized` and `failure_and_control.failure`
is `not_reproduced`, `root_cause=unlocalized`, `qualifies=false`.

## Historical execution and control: provenance only

The research record contains one successful **no-retrieval** whole-file
conversion and one prose crash observation with retrieval enabled. Neither is
rerun, merged task evidence, a qualification or a result.

| Field | Recorded value |
| --- | --- |
| Candidate | RVC v2 multi-speaker VCTK checkpoint (`Nekochu/RVC-VCTK_Voice-sample`, p226 path) |
| Mode | official RVC PyTorch pipeline, CPU, 4 threads, file input, RMVPE F0, retrieval disabled |
| Output | `source_to_p226.wav`, 40 kHz, 9.64 s, 771,244 bytes, SHA-256 `7fa0516e7475b6870267da9f4a894d0d18e67714e1081cd9d3c7d63db30bd8c7` |
| Index rate | `0.0`; index path empty; index not assigned |
| Init + HuBERT | `0.34603404195513576` s |
| Conversion | `7.748765500029549` s; file RTF `0.8038138485507831` |
| Peak / clipping | `0.497772216796875` / `0.0` |
| ASR proxy | Whisper Tiny English WER `0.0` on the one source utterance |
| Retrieval-enabled run | crash inside native `index.search()`; no traceback, signal, index bytes, checkpoint or runtime retained |
| Paired control | **no**: the control is a different (retained) session/artifact state and cannot be re-run |
| Device timing, listening, identity, naturalness, multi-utterance | absent |

The historical output is listed only to preserve provenance. It is not decoded,
played, scored, pooled or promoted; only a whole-file SHA-256 and byte-count
provenance check is recorded. A 0.00 WER proxy is not a content, semantic,
identity or naturalness certificate, and 0.804 file RTF is not a call-device
latency.

## What this package actually verifies

1. **Source presence and exact pins.** The RVC revision, MIT `LICENSE`, README,
   requirements, offline/realtime pipelines, resolver, index builder and
   historical runner/metrics/ASR/output are pinned by SHA-256. This is a
   source-code provenance fact, not a checkpoint, index or runtime
   qualification.
2. **Call-site facts.** The verifier reads the pinned source and confirms each
   recorded retrieval line/fragment, the unique `k=8` search calls, the absence
   of a local handler on the offline call site, the realtime handler and the
   IVF/`nprobe=1` builder. Any drift fails closed.
3. **Absence and runtime evidence.** Twenty-six fixed workspace/worktree probes
   and four fixed home-cache probes are checked (no recursive workspace walk).
   All are absent. `reference.build_report()` and `verify.py` raise or fail if
   any probe later appears. `assets/rmvpe` (empty) and
   `assets/hubert_base` (config only) are recorded as present-but-insufficient,
   and any new file there fails closed. The runtime probe uses
   `importlib.util.find_spec` metadata only and requires every module absent.
4. **Branch contract model.** A deterministic, stdlib-only classifier encodes
   the pinned preconditions and the `index_rate=0` conditioning control. It
   rejects nonfinite/out-of-range rates, dimension mismatch, empty/oversized
   frame counts, non-`float32`, nonfinite query state, invalid `k`, `nlist` and
   `nprobe`. It never executes FAISS and every output has `qualifies=false`.
5. **Reproducer admission boundary.** A caller bundle has a strict task-local
   schema (candidate, checkpoint, index, runtime, query, observations, control,
   rights). Every malformed, missing, invalid, nonfinite, aliased, duplicated,
   out-of-range, inconsistent-exit or unpaired control is rejected before any
   state change. One structural control is admitted to prove the validator is
   not blanket-rejecting, and is labelled
   `synthetic_schema_control_not_evidence` with `qualifies=false`. Admission
   never reads audio, loads weights/index or invokes FAISS or a model.
6. **Voice profile accounting.** Permitted inputs/targets, groups, content,
   identity, naturalness, alignment, first-output/tail, target condition and
   independent consent/reference/output-use gates are each recorded as
   **blocked**.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the SDK README and merged
   sibling Voice packages are pinned by SHA-256 and verified unchanged.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Freeze input/target references, task and groups | blocked | One unconsented LJ Speech clip and a presumed p226 target; no frozen target condition, language/speaker group or rights record. |
| Preserve text and semantic content | blocked | The historical WER proxy is not a manual transcript or semantic result and was not rerun for retrieval. |
| Identity/similarity separately | blocked | No target-voice score, and the target mapping itself is unverified. |
| Naturalness separately | blocked | No naturalness rating or blinded listening. |
| Record alignment | blocked | No word/phoneme, onset or source-content alignment. |
| Record first-output/tail timing | blocked | Only whole-file control timing exists; retrieval-enabled timing is absent. |
| Record exact target condition | blocked | Presumed `speaker_id=1` p226 path with the matching index; map, bytes and consent absent. |
| Consent, reference availability and output use | blocked | No consent or output-use record; the MIT source license clears none. |

## Admission contract (task-local; not an SDK, RVC or Voice contract)

- **Manifest** fields: `schema_id`, `experiment_id`, `candidate`, `checkpoint`,
  `index`, `runtime`, `query`, `observations`, `control`, `rights`. Unknown and
  missing fields are rejected.
- **Candidate**: exact repository, 40-hex revision `81eed5e8…`, canonical
  absolute source/license paths, `license_id="MIT"` and 64-hex license digest.
- **Checkpoint**: name exactly `Mp226rmvpe.pth`, 64-hex SHA-256, 1 B–8 GiB,
  exactly 109 speakers, no embedded `speaker_info`, a 64-hex reviewed speaker
  map with `speaker_map_verified=true`, and a 64-hex terms digest.
- **Index**: name exactly
  `added_IVF1161_Flat_nprobe_1_Mp226rmvpe_v2.index`, 64-hex SHA-256, 1 B–2 GiB,
  `IndexIVFFlat`, 768 dimensions, `nlist=1161`, `nprobe=1`, metric `l2`,
  positive read/reconstruct times.
- **Runtime**: Python 3.11.x, torch `2.15.0`, torchaudio `2.11.1`,
  `faiss-cpu` `1.x >= 1.13.0`, a non-empty FAISS build string, numpy `1.26.x`,
  CPU, 1–64 torch/OMP/OpenBLAS threads and `deterministic_algorithms=true`.
- **Query**: canonical path, exactly the historical source SHA-256/byte count,
  16 kHz, `9.655` s, 768-d `float32`, 1–1,000,000 frames, all finite and a
  64-hex query digest.
- **Observations**: retrieval enabled and index assigned, a boolean search
  outcome, `exit_kind` in `native_crash|uncaught_exception|clean`, a consistent
  exit code/signal (native crash must record `128+signal` or `-signal`), a
  retained traceback path/digest for non-clean exits, and result digests only
  for a clean run.
- **Control**: retrieval disabled, `index_rate=0.0`, no index assigned, a
  canonical output path with 64-hex digest/bytes, and `paired=true` plus
  `same_artifacts=true`.
- **Rights**: non-empty checkpoint/index terms, source-speaker consent,
  target-voice consent, dataset reference and output use, with slug review and
  cohort IDs. The schema does not assert that any real right has been granted.

## Pinned inputs (SHA-256)

`source:` paths are relative to the `audioml` workspace; the rest are relative
to this SDK worktree. `SOURCES.sha256` pins these plus every task-local artifact
and excludes its own bytes. The mutable shared board is **not** pinned; only
the stable row identity gates anything.

| Input | Use |
| --- | --- |
| `source:research/voice-conversion-eval-20261101/README.md` | Historical VC/RVC run and crash observation |
| `source:…/agent-matrix-crosswalk/REPORT.md` | Crosswalk disposition context |
| `source:…/scripts/run_rvc_vctk_eval.py` | Exact historical invocation |
| `source:…/results/rvc/metrics.json` | Historical no-retrieval timing/peaks |
| `source:…/results/rvc/asr.json` | Historical one-utterance ASR proxy |
| `source:…/results/rvc/source_to_p226.wav` | Historical output, hash-only provenance |
| `source:…/repos/rvc/LICENSE` | MIT source-code license, not weight/index terms |
| `source:…/repos/rvc/README.md` | Fork scope |
| `source:…/infer/vc/pipeline.py` | Offline retrieval call site and branch |
| `source:…/infer/vc/modules.py` | `vc_single` call path |
| `source:…/infer/vc/utils.py` | Index-name resolution |
| `source:…/infer/cli.py` | `index_rate=0` control resolver |
| `source:…/infer/rtrvc.py` | Realtime retrieval call site and handler |
| `source:…/train/train_index.py` | IVF/Flat builder and `nprobe=1` |
| `source:…/requirments_cpu_py312.txt` | `faiss-cpu>=1.13.0,<2` and numpy constraint |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `rvc-faiss-retrieval` row, Voice profile |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | Voice profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | SDK delivery boundary |
| `CONTRACTS.md` | Unchanged v0 contract |
| `api/include/audio_sdk/*.h` | Unchanged provider/session tables |
| `CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml`, `README.md` | Unchanged shared build, licensing, CI and build surface |
| `docs/task-evidence/{chatterbox-vc,cosyvoice-2-0-5b,openvoice-v2,survey-trn-04}/*` | Merged sibling Voice evidence, boundary only |

Exact digests live in `reference.SOURCE_PINS`, `reference.BOUNDARY_PINS` and
`SOURCES.sha256`. The shared board row is read only through the stable
projection `{id, title, component, mode, repository, depends_on}`. `status`,
`owner`, `claim`, `review`, `handoff`, `blocked_reason` and
`dispatch_priority` are excluded from gating, so a board state transition
cannot promote or block this package's claims. The full mutable `TASKS.json`
bytes are never hashed.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blocker, crash isolation, provenance, pins, commands, counts, gates. |
| `LICENSES.md` | Source/checkpoint/index/reference-voice boundary; no vendored license text. |
| `contract.json` | Machine-readable contract: pins, artifacts, blockers, eight gates, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence/runtime probes, retrieval/control branch model, manifest admission validator, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network, no runtime). |
| `verify.py` | Read-only verifier: profile phrases, pins, call-site lines, report bytes/digest, absence, gates, licensing, write scope, three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/rvc-faiss-retrieval` with Python 3.11+ and stdlib only:

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
byte_identical=true profile=Voice status=incomplete decision=DEFER`; REUSE
reports no missing or bad license; `git diff --check` is clean. `verify.py`
itself writes only to a temporary directory and never to this package.

Current counts: 26 workspace/worktree absence probes plus 4 home-cache probes
(0 present), 7 required artifacts (1 source present, 6 blocked), 7 open
blockers, 120 rejected admission controls, 1 schema-only control, 8 blocked
Voice rows, 3 blocked quality outcomes, 3 blocked timing rows, 8 blocked gates,
0 qualifying results.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source, model revision, archive and license provenance | blocked | Both source archives, 40-hex revisions, tree digests and complete license/notice/checkpoint/index terms supplied and reviewed. |
| `RG-02` checkpoint, index assets, metadata and speaker map | blocked | Immutable checkpoint/index bytes, digests, index metadata and verified 109-entry speaker map staged. |
| `RG-03` pinned runtime and offline load | blocked | Locked runtime with install digest loads the pinned checkpoint/index offline with recorded threads and deterministic settings. |
| `RG-04` retained crash evidence and root cause | blocked | Exact reproducer, full crash artifact, minimized case and localized root cause reproduced on the pinned runtime. |
| `RG-05` paired no-retrieval conditioning control | blocked | Same-input/artifact/runtime `index_rate=0` vs `index_rate>0` runs with outputs, logs, timings and a declared comparison. |
| `RG-06` verified speaker map, rights and cohort | blocked | Verified map, reviewed terms, signed consents and a rights-cleared frozen cohort. |
| `RG-07` voice quality, timing and listening | blocked | Pinned scorers, approved blinded listening and paced device runs separate content, identity, naturalness, alignment, timing and resources. |
| `RG-08` provider intake, public surface and release | blocked | Separate versioned intake with OFF default, public-surface decision and independent exact-head review. |

No synthetic admission control opens a gate. No missing result is promoted.

## Separation from other evidence

The merged Chatterbox VC, CosyVoice 2, OpenVoice v2 and Voice survey packages
are boundaries only. This package does not reuse their numbers, status or
conclusions. RVC-MLX realtime and RVC v2 VCTK p226 are separate queued tasks;
their future results are not pooled here. Sibling VC results do not substitute
for a retained RVC retrieval crash, index, checkpoint or control.

## Expected digest

`report.json` SHA-256:
`da64f7ac95942bbff2e015dcd9a79334b8024aa11eefdb19a4a932e6cdf99727`.
