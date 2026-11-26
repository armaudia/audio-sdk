<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-DPCRN-DNS3-TFLITE — missing-artifact feasibility blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DPCRN DNS3 / TFLite` (`component_id=dpcrn-dns3-tflite`). The acceptance profile
is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Machine-readable disposition: **`decision=DEFER`**,
`evidence_status=incomplete`, `status=proposal_only_synthetic_blocker_incomplete`,
`qualification.status=not_qualified`. A missing result never qualifies the
candidate.

The task is a feasibility task: verify runnable source, exact assets, permitted
scope, task geometry and matched evidence, then reproduce the exact model/runtime
as a caller-supplied-asset reference **if those prerequisites exist**. The pinned
census and candidate accounting locate only a public repository lead with status
`located_unverified`. No immutable commit, `.tflite` bytes, checkpoint identity,
byte count, SHA-256, license terms or pinned TFLite runtime exists. Under the
task rule — **do not fabricate and do not download** — the exact candidate cannot
be reproduced. This package therefore records an exact external blocker and
ships only:

1. a fail-closed caller-supplied-artifact requirement with explicit unresolved
   fields;
2. a deterministic, stdlib-only **synthetic surrogate** at a declared
   DPCRN-family complex-STFT boundary, used only for geometry, sample
   accounting, chunking, finiteness and refusal mechanics; and
3. a strict `not_ready` conclusion with all **eight** release gates `blocked`.

The surrogate is opt-in, unregistered and OFF by default. It is **not DPCRN**,
not a TFLite graph, not a quantized kernel and not a model inference. It
substitutes for no gate.

No `.tflite` graph, checkpoint, source checkout, TensorFlow install or TFLite
interpreter was downloaded, copied into this worktree, opened, hashed, loaded or
invoked. No media, corpus, device clock, listener, benchmark or release artifact
is present or claimed. No public API/ABI, `CONTRACTS.md`, descriptor, registry,
installed default, shared build, CI, board or handoff file changes. Only this
task-local directory is added.

## Exact external blocker

The pinned census records `DPCRN DNS3 / TFLite` as a dual-path convolutional
recurrent network and a real-time/quantized edge reference, and says the author
repository identifies an official DNS3 implementation, a pretrained-model
directory and a smaller uploaded TFLite model with single-file and streaming
inference. The same row records the decisive gaps: **“TensorFlow 1.x real-time
path is legacy; exact checkpoint hash and weight licensing were not found.”**
The candidate accounting row carries the same status: `blocked`,
`located_unverified`.

The concrete missing prerequisites are:

1. **No admitted artifact identity.** There is no immutable upstream commit, no
   `.tflite` path, no byte count and no SHA-256. The asset ledger
   `research/noise_suppression_assets_20261027.json` has no DPCRN DNS3 entry.
   A repository URL is a lead, not an artifact identity.
2. **No exact runtime.** No TFLite interpreter version, ABI, Python binding,
   CPU/edge delegate or package digest is pinned. `tensorflow`,
   `tflite_runtime` and `ai_edge_litert` are not importable in the pinned
   CPython 3.12.16 evidence interpreter, and the legacy TensorFlow 1.x path is
   unverified.
3. **No artifact-specific rights.** Weight licensing was not found. There is no
   code license pin for this repository, no model-weight or checkpoint terms, no
   conversion/quantization terms, no DNS3 training-data provenance or
   evaluation-overlap assessment, and no redistribution, product-use or legal
   decision. A repository description is not clearance.
4. **No qualification evidence.** There is no real-model parity run, frozen
   reference output vector, rights-cleared held-out paired real cohort,
   independent clean-reference scorer, permitted listening result,
   target-runtime timing/memory/deadline measurement, benchmark or release
   result.

**Reopen condition.** Admit the candidate only when an authorized caller supplies
an immutable upstream commit and the exact `.tflite` graph plus the conversion
source/checkpoint, each addressed by path, byte count and SHA-256; a pinned TFLite
interpreter version/ABI and CPU/edge delegate with a package or build digest in
an approved isolated runner; written code, model-weight, checkpoint,
training-data, conversion and runtime terms plus a positive legal,
redistribution and product-use decision; and then real-model parity with verified
geometry, content delay, state and alignment, a rights-cleared held-out paired
real cohort with an independent scorer, authorized listening or a separately
labeled predictive screen, and target-runtime timing/memory/deadline evidence.
Until then every release gate stays `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`report.json:exact_blockers` and `report.json:readiness`.

## Task-row identity without the mutable board

The full `plan/swarm/TASKS.json` is mutable and is **never read, hashed or
pinned** by this package. Only the stable linked inventory-row projection is
gated:

| Field | Value |
| --- | --- |
| task_id | `SDK-DPCRN-DNS3-TFLITE` |
| component_id | `dpcrn-dns3-tflite` |
| name | `DPCRN DNS3 / TFLite` |
| repository | `audio-sdk` |
| verification_profile | `enhancement` |
| disposition | `sdk-model` |
| evidence_status | `considered` |
| linked evidence | `research/noise_suppression_candidate_census.md` line 20 |

`task_identity.row_projection_sha256` is the SHA-256 of that canonical
projection, and `verify.py` re-derives it from
`audio-benchmark-platform/plan/INVENTORY.json`. `SOURCES.sha256` contains no
`TASKS.json` line by construction and by verification.

## Boundary

- Installed public v0 geometry is preserved and unchanged: 16 kHz, mono, `f32`,
  160 samples per frame, zero installed content delay.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `processor_exposure=false`, `realtime_streaming_exposed=false`.
- The candidate is offline-file and streaming/quantized-edge capable upstream
  according to the census, but neither path is reproduced or exposed here. No
  stream state, look-ahead, delegate or pacing surface is added.
- The caller-supplied-artifact contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no artifact bytes are read, and no
  download is attempted.
- The surrogate path and the real path are distinct. The real path fails closed
  and never silently falls back to the surrogate.

## Synthetic surrogate semantics

The fixture uses only standard-library floats and a deterministic PRNG. It
models a declared **DPCRN-family expectation**, not a verified upstream fact:

| Item | Value |
| --- | --- |
| sample rate / channels / format | 16 kHz / mono / `f32` |
| processing mode | offline whole utterance, non-causal |
| n_fft / window / hop | 512 / 512-sample `sqrt(periodic Hann)` / 256 samples |
| hop duration | 16 ms |
| STFT representation | 257 real/imag bins |
| surrogate frequency chunks | 16 contiguous dual-path-shaped chunks |
| frame count | `T = 1 + floor(N/256)` |
| STFT padding | 256 samples on each side, centered |
| output length | exactly `N` |
| source-time mapping | identity |
| exact artifact geometry verified | **false** |
| exact artifact stream delay | **null / unresolved** |

Signal handling is strict. Empty, one-sample, string, boolean, non-finite and
out-of-range samples are rejected before any state change. Configurations with
missing, extra, unknown, absolute-path or traversal values are rejected. A
well-formed request that claims fabricated pins is still rejected as
`blocked_unpinned_artifact`. Identity/noisy-input controls and a synthetic
clean-preservation diagnostic are reported with the candidate; regressions are
recorded verbatim, not hidden.

The surrogate uses a chunk-wise magnitude gain from a low-energy noise estimate,
with centered three-tap temporal smoothing. It has no convolutions, recurrent
state, learned weights, quantized kernels or TFLite delegate. Its SI-SDR and
STOI values are **synthetic only**, are not a listening proxy, and are excluded
from qualification.

## Evidence classification

- `synthetic_paired_metrics` — synthetic surrogate only.
- `analytical_geometry_and_alignment` — sample-count and identity mapping only.
- `pinned_source_inventory_and_census` — locator and linked-row identity.
- `deterministic_bytes_and_digests` — canonical JSON, SHA-256 sidecars, 3× cold
  start.
- `explicit_missing_artifact_blocker` — the exact external blocker above.

The merged PureSound DPCRN-Mamba v1/v2/v3 packages are **different upstream
artifacts**. Their DNS pilot metrics and 480-sample streaming delay share only
the DPCRN name and are neither pooled nor used as a result for this candidate.

## Canonical artifacts and local digests

<!-- run.py refresh_readme() rewrites the SHA-256 column; verify.py fails on drift. -->

| File | SHA-256 |
| --- | --- |
| `contract.json` | `09034b82f18fb99173d03f08f214a500ecf7c3681998c2998861ec3d8b9b5cdd` |
| `reference.py` | `5b901f0ac1c333318425e565c484118976a1bf1031ab87feeaa6507b8c603638` |
| `scorer.py` | `7c2f900d64f6eca086ffdfee4d23eb15bf9f0a528f90fc925b8a1846065b318c` |
| `run.py` | `7553584c01eeb5f8668fa0a5bec4ac71c8ceaf6dfa23e47880be7d7a25b69612` |
| `test_reference.py` | `37d6944c0c0273aaefbc12170faf95a1d225de1ae1b70724d931406dd094a092` |
| `verify.py` | `c32fd155c9ca695a146023a4910ef6e68971cf4d78314770581730e5e7661999` |
| `report.json` | `e6489f75d1f4b3dcf5fb2bcc48919a156c2d7f94101b68a81bd33f02e62ddc39` |
| `report.json.sha256` | `8bbe31637812662efc4611b7f90cd42f115368a8e5f0cb2120e89c7e8ffacbbd` |

`SOURCES.sha256` separately pins every local artifact except itself, every
`source:` evidence file and the public boundary headers/contract. It never pins
`TASKS.json`.

## Remaining gates (all blocked)

1. `exact_artifact_identity_and_hash_pinned` — no immutable commit, `.tflite`
   path, byte count or SHA-256.
2. `exact_runtime_and_delegate_pinned` — no TFLite interpreter version/ABI,
   delegate or package digest.
3. `weight_runtime_and_training_data_rights_cleared` — no weight, conversion,
   training-data or runtime terms and no legal decision.
4. `real_model_parity_and_alignment` — no real-model run, frozen output vector or
   verified geometry/delay/state.
5. `held_out_paired_denoising_cohort` — no rights-cleared real paired cohort and
   no independent scorer.
6. `independent_listening_or_predictive_screen` — no permitted listening and no
   separately labeled predictive screen.
7. `target_runtime_timing_memory_and_deadline` — no device/edge timing, memory,
   throughput or deadline measurement.
8. `provider_intake_descriptor_and_default_review` — no opt-in provider intake,
   descriptor review or explicit default-selection review.

## Reproduce

```sh
cd docs/task-evidence/dpcrn-dns3-tflite
PYTHONDONTWRITEBYTECODE=1 ~/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 ~/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 ~/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
```

`run.py --all` performs three cold-start passes for the contract, report and
source manifest and refuses to write if any pass differs. `verify.py` is
read-only and fails on non-canonical JSON, stale pins, stale README digests,
accepted invalid/missing/non-finite inputs, a non-blocked artifact gate, a
mutable-board pin, license gaps, out-of-scope changes or a dirty
`git diff --check`.
