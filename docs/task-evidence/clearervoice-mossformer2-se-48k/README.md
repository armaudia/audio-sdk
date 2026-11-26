<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CLEARERVOICE-MOSSFORMER2-SE-48K — absent-asset feasibility blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ClearerVoice MossFormer2_SE_48K` (`component_id=clearervoice-mossformer2-se-48k`).
The acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, and all eight release gates are `blocked`.
A missing result never qualifies the candidate.

The exact licensed source, checkpoint and runtime are **absent**. This package
therefore records the exact external requirement and runs a deterministic,
stdlib-only boundary probe. The probe is explicitly **not MossFormer2_SE_48K**:
it has no attention block, neural network, checkpoint, weight, PyTorch graph or
ClearerVoice import. Nothing was downloaded, copied, built, loaded, executed,
vendored or redistributed. No provider, descriptor, registry, installed-v0
path, shared build, dependency lock, CI, board or handoff file was changed.
Only this task-local directory was added.

## Exact external blocker

The merged sibling evidence pins the ClearerVoice source revision
`dcb1b20e1e44d435090072ab9b223c792ea1f624` and package identity
`ClearerVoice-Studio-clearvoice-0.1.2` under Apache-2.0 code terms. The model
card is `https://huggingface.co/alibabasglab/MossFormer2_SE_48K`.

That is not enough to run or qualify the candidate:

1. **Source absent.** `data/checkouts/ClearerVoice-Studio` is absent. No source
   tree, submodule, wheel or sdist is present in this workspace.
2. **Checkpoint identity unrecorded and bytes absent.** No pinned local ledger
   records a `MossFormer2_SE_48K` artifact revision, filename, byte count or
   SHA-256. The expected path
   `data/models/clearvoice/MossFormer2_SE_48K/last_best_checkpoint.pt` is
   absent. The filename is an upstream-convention hint, not a verified pin.
   A hash-matched placeholder is never accepted as the pinned model.
3. **Runtime absent.** `data/envs/clearvoice` and the `clearvoice` package are
   absent. `adapters/clearvoice/run.py` was not imported or executed. No wheel,
   sdist, ABI, platform or PyTorch runtime is admitted here.
4. **Rights unresolved.** The code and model card are reported Apache-2.0, but
   upstream states open and private training data with undisclosed corpus
   exposure. Weight-specific terms, training-data provenance, corpus terms,
   redistribution, product-use, derivative-output and legal review are absent.
5. **Geometry and mapping unqualified.** The candidate is declared at 48 kHz
   mono; installed SDK v0 remains 16 kHz mono `f32` at 160 samples. No
   resampling, content-delay, drain or edge-exclusion implementation exists.
6. **No qualification evidence.** There is no exact output vector,
   rights-cleared paired 48 kHz cohort, independent SI-SDR/STOI score,
   permitted listening result, target-device timing or opt-in provider intake.

**Reopen condition.** Supply the pinned source and exact checkpoint identity and
bytes, admit a hash-pinned `clearvoice`/PyTorch runtime, clear all artifact and
corpus rights, establish the 48 kHz geometry and installed-16-kHz mapping,
reproduce exact outputs, score a rights-cleared paired cohort independently,
measure target timing and complete opt-in provider intake with an OFF default.
Until then the candidate stays **DEFER**, **incomplete** and **not qualified**.

The same requirement is machine-readable in `contract.json:exact_blockers`,
`report.json:exact_blockers` and `contract.json:release_gates`.

## What this package actually contains

- A deterministic 48 kHz mono fixture of 192,000 samples (4 s), built with
  integer triangle waves, an LCG noise source and int16 quantisation. It is
  synthetic; it is not real speech, a corpus or a clean reference.
- A strict caller-supplied-asset manifest validator that checks absolute paths,
  byte count, SHA-256, pointer text and declared geometry without loading or
  executing a model.
- A strict whole-clip session that buffers caller chunks, rejects adverse and
  nonfinite input before state change, preserves length and replays exactly
  after reset.
- A model-free first-order DC-blocker **mechanism probe**. It demonstrates
  finite, deterministic, length-preserving whole-clip processing only.
- Canonical contract/report generation, a SHA-256 pin manifest, README digest
  tables, deterministic tests and a read-only verifier.

No candidate result is produced. The probe's metric values describe the
surrogate, not MossFormer2_SE_48K, and are never pooled with source-reported
values.

## Scenario and geometry

- Scenario: offline whole-utterance enhancement (`CLN-01`), not streaming.
- Candidate declared geometry: 48 kHz, mono, `float32`, whole-clip buffering.
  The 480-sample / 10 ms hop is a **proposal only**, not a verified native hop.
- Installed SDK v0 geometry is unchanged: 16 kHz, mono, `f32`, 160 samples.
- Candidate algorithmic latency is **not measured**; no content delay, finite
  drain or 48 kHz-to-16-kHz mapping is claimed.
- The surrogate has zero algorithmic delay and preserves input length exactly
  on the synthetic fixture.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json:acceptance_profile` and checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Identity/noisy control | Observed mixture on the same frozen clip |
| Task-matched baseline | **Blocked**: no candidate or established baseline output exists |
| Paired SI-SDR | Synthetic identity and surrogate only; no real clean reference |
| STOI | **Not run**: no qualified candidate scorer or rights-cleared cohort |
| Clean-speech preservation | Target retention and clean strata on the synthetic clip |
| Peaks and invalid outputs | Maximum absolute output, clamp count, nonfinite count |
| Alignment | Whole-clip length preservation; no candidate delay claimed |
| State | Reset replay parity and unchanged state digests on rejection |
| Memory | **Blocked**: no runtime, so no memory measurement |
| Content/availability timing | **Blocked**: no runtime or device clock |
| Listening | **Not run** |
| Real runtime / real clean references | **false** |

## Synthetic fixture and surrogate

| Stratum | Samples | Condition |
| --- | ---: | --- |
| `silence-a` | 24,000 | Exact digital silence |
| `quiet-speech` | 48,000 | Low-level integer harmonic segment plus LCG noise |
| `active-speech` | 48,000 | Higher-level harmonic segment, clicks, LCG noise |
| `low-snr-speech` | 48,000 | Harmonic segment with strong LCG noise |
| `tail-silence` | 24,000 | Exact digital silence |

The surrogate is `y[n] = x[n] - x[n-1] + (32000 * y[n-1]) // 32768`, clamped
to int16. It is a first-order DC blocker with no model, no weights and no
candidate behavior. Its severe low-frequency loss is recorded as a surrogate
regression, not hidden or promoted.

## Results (synthetic surrogate only)

All values are generated from `report.json`; the table is replaced by `run.py`
and checked byte-for-byte by `verify.py`. They are **not** MossFormer2_SE_48K
results, not device timing and not a release claim.

<!-- RESULTS_TABLE_START -->
| Metric | Identity (noisy) | DC-blocker probe |
| --- | ---: | ---: |
| SNR vs clean (dB) | 7.542481085 | 2.406468410 |
| SI-SDR vs clean (dB) | 7.541730407 | -0.541958267 |
| Target retention | 0.999913558 | 0.611531661 |
| Delta SI-SDR (dB) | n/a | -8.083688674 |

| Stratum | Identity SI-SDR (dB) | Probe SI-SDR (dB) |
| --- | ---: | ---: |
| `active-speech` | 19.959251547 | 1.271424489 |
| `low-snr-speech` | 2.085518225 | -2.609693189 |
| `quiet-speech` | 18.115141907 | -0.847818865 |
| `silence-a` | n/a | n/a |
| `tail-silence` | n/a | n/a |
<!-- RESULTS_TABLE_END -->

## Failure controls (recorded as failures)

- **Caller asset:** a generic manifest with caller-owned temporary files
  validates byte count, SHA-256, pointer text and geometry but reports
  `pinned_model=false`, `loaded=false`, `executed=false`, `imported=false`.
  Absent, relative-path, model-hash, pointer-hash, byte-count, extra-field,
  missing-field, wrong-source, wrong-package, wrong-model, 16 kHz, stereo,
  `int16`, streaming, unknown-license, wrong-pointer and placeholder claims are
  rejected. Candidate admission returns
  `asset_model_identity_unrecorded`; an uncleared rights decision returns
  `asset_rights_not_cleared`. A placeholder is never accepted as the pinned
  model.
- **Config adverse:** 16 kHz, stereo, `int16`, 0- or 160-sample frames,
  streaming, `real_runtime=true`, `model_used=true`, resampling, extra keys,
  negative epoch, boolean epoch, nonzero first position and a wrong schema are
  rejected before session creation.
- **Chunk adverse:** empty, string, `None`, nested, boolean, NaN, ±Infinity and
  out-of-range chunks are rejected with the state digest and accepted-sample
  counter unchanged.
- **Nonfinite input:** NaN is never counted as silence and never changes state.
- **Silence:** a 2,048-sample zero stream returns exact zero.
- **Partial tail:** a 48,123-sample stream preserves length, and split feeding
  matches the single-call prefix exactly.
- **Chunking:** sizes `1, 7, 160, 480, 481, 4096, 12000` produce byte-identical
  output.
- **Reset:** reset to epoch 1 reproduces a fresh epoch-1 session; same, lower,
  negative and boolean epochs are rejected with an unchanged stale digest.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, geometry, results, pins, commands, gates. |
| `reference.py` | Deterministic fixture, strict asset/config/chunk parsers, session probe, metrics, contract/report/tables/pins. |
| `run.py` | Builds contract and report three times, requires byte identity, regenerates artifacts and tables. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: disposition, boundary, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks; no network, no skips. |
| `verify.py` | Read-only strict pin, JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root
(`SOURCE_ROOT`). Every row is machine-checked.

<!-- DIGEST_TABLE_SOURCE_START -->
| Key | SHA-256 |
| --- | --- |
| `source:adapters/clearvoice/README.md` | `9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5` |
| `source:adapters/clearvoice/adapter.json` | `ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff` |
| `source:adapters/clearvoice/requirements.lock` | `3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91` |
| `source:adapters/clearvoice/run.py` | `c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
<!-- DIGEST_TABLE_SOURCE_END -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree and are unchanged.

<!-- DIGEST_TABLE_BOUNDARY_START -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/task-evidence/clearvoice-frcrn-16khz/README.md` | `2ba56bbe54c825818143aa27859f2e001077bf0024932321a45e764fd40ef75d` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/README.md` | `4cce8370c8af8bd2a5a83f05bf15e540756f1f7d61f63170b6a9626f65d6bbce` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/contract.json` | `cd98bc7b615b0861923d2a53a24ec91fd939c6dcade0818022912a5a5e34869c` |
| `sdk:docs/task-evidence/clearvoice-mossformergan/report.json` | `5c806186d35c1f39021617dc5649bf32d87030a1a059d26e35492a69ee1a7afc` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- DIGEST_TABLE_BOUNDARY_END -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). `README.md` and `SOURCES.sha256` are excluded from this
table to avoid a self-reference; `SOURCES.sha256` pins every artifact and this
README but does not pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `ef2b787ecc7d34561387dddc1d4ce049bfd1dfa89ea9e1c20e854a5e0f020e67` | 18810 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `5cfcce6b25609d49a0ae7700d2ab06cf35106d5d7fd3ad5890f1015f189c33a6` | 69636 |
| `report.json` | `b9de47ff855a51205874c843fea61928b4a2e6167032b3cda1462b9f194b2a23` | 24348 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `5dee98e93286755dbd9902ec41dfe75ce01697aeab8343524f5ff2e28b5744f9` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `d9fd0ba34c4ca330d305ff22e6ff895e744587cd7864a5b620b4dd15887a9aeb` | 2456 |
| `test_reference.py` | `d272d7ce3bf616c1082a23b8d6393b474de4b127eb27d94f467eb1f008cb5696` | 22482 |
| `verify.py` | `36124df4dab9dcecaa0dc2a6fa79740edea0360eb4e551d99138bd0b7ae03112` | 23835 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduce

Run from this directory with Python 3.12 and keep bytecode out of the tree.
`SOURCE_ROOT` is needed by the verifier and tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CLEARERVOICE-MOSSFORMER2-SE-48K
TASK=$WT/docs/task-evidence/clearervoice-mossformer2-se-48k
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C "$WT" diff --check
```

`run.py` builds the contract and report three times in one process and refuses
to write unless all payloads are byte-identical. External reproduction runs
`run.py` three times in separate cold-start processes and compares the bytes.

## Remaining release gates (eight blocked)

<!-- GATES_TABLE_START -->
| Gate | Status | Requirement |
| --- | --- | --- |
| `exact_source_and_model_identity` | `blocked` | Pinned ClearerVoice source revision plus an immutable MossFormer2_SE_48K artifact revision, byte count and SHA-256, verified pointer and caller-held bytes. |
| `runtime_admission` | `blocked` | Hash-pinned isolated CPython/clearvoice 0.1.2/PyTorch runtime with archive, wheels, ABI, platform and distribution terms recorded. |
| `artifact_and_training_rights` | `blocked` | Weight, training-data, corpus, runtime, redistribution, product-use and derivative-output rights cleared with complete notices and legal review. |
| `exact_reference_parity_48k` | `blocked` | Approved exact-runtime MossFormer2_SE_48K output vectors and byte-level parity on the declared 48 kHz mono geometry. |
| `rights_cleared_paired_cohort` | `blocked` | Frozen rights-cleared paired 48 kHz clean/noisy corpus, strata, edge exclusions, content delay and reset schedule. |
| `independent_scoring_and_listening` | `blocked` | Independent SI-SDR/STOI or permitted listening, identity and task-matched baselines, failure/nonfinite controls and clean preservation. |
| `target_runtime_timing_and_resampling` | `blocked` | Target-device p50/p95/p99, RTF, memory, deadline, whole-clip availability and the exact 48 kHz to installed 16 kHz mapping. |
| `opt_in_provider_intake_and_default` | `blocked` | Opt-in provider intake, descriptor/asset review, OFF default and an explicit owner default decision. |
<!-- GATES_TABLE_END -->

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:gates`. `qualification.release_gate_count` is 8,
`qualification.all_blocked` is true and `qualification.status` is
`not_qualified`.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `weights_vendored=false`, `real_asset_read=false`,
`network_used=false`, `surrogate_is_candidate=false`,
`task_board_or_handoff_write=false`. Installed v0 remains 16 kHz, mono,
float32, 160 samples per frame. The board is referenced by stable linked-row
identity only (`tasks[id=SDK-CLEARERVOICE-MOSSFORMER2-SE-48K]`, stable-field
digest); the mutable full `plan/swarm/TASKS.json` is never read into, hashed by
or pinned to this package.

## Separation from sibling evidence

`docs/task-evidence/clearvoice-mossformergan/` and
`docs/task-evidence/clearvoice-frcrn-16khz/` are different candidates with
different checkpoints and geometries. Their outputs, metrics, adapters and
source-reported values are **not** pooled, imported, reused or reinterpreted
here. The research-workspace `adapters/clearvoice/` files, candidate census,
asset ledger and candidate matrix are pinned provenance only; they were not
executed, imported or treated as evidence for this probe.
