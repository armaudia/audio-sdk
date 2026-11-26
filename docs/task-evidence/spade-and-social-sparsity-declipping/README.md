<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING — SPADE and social-sparsity declipping strict readiness evidence

**Status: `proposal_only_synthetic_incomplete`; qualification `incomplete`; qualification status `not_qualified`; decision `DEFER` before any processor exposure, default, registration or release claim.**

This package is a deterministic, task-local investigation handoff for the `SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING` feasibility row. It is **not** a SPADE implementation, not a social-sparsity implementation, not a wrapped MATLAB/LTFAT/CVX toolbox, not a vendored source, not a licensed runtime, not an installed SDK provider, and not a listening, device-timing, benchmark or production qualification. No public API/ABI, `CONTRACTS.md`, shared `CMakeLists.txt`, descriptor default or registry, installed v0 behavior, board, handoff, ruleset, main branch or other worktree was changed.

Pinned base: `b369ee5b64de0493b96b3f99ede9a2560b130bb2`. Branch: `swarm/SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING`. All files live only under `docs/task-evidence/spade-and-social-sparsity-declipping/`.

## What was checked

1. **Exact scope.** The branch diff against the newest available merge-base of `HEAD` with `origin/main` (falling back to `main`) is enumerated. Any tracked change outside this task directory fails closed as `base_out_of_scope_change`; if no base ref resolves, verification fails with `scope_base_unavailable`.
2. **Task-board and inventory identity.** Only stable identity fields of the `SDK-SPADE-AND-SOCIAL-SPARSITY-DECLIPPING` row and the `spade-and-social-sparsity-declipping` inventory record enter canonical bytes. Mutable status, owner, claim, review, handoff and history fields are excluded and never treated as evidence.
3. **Source and asset identity.** Pinned research names SPADE/social sparsity as the established next constrained sparse declipping comparison and cites the author `declipping2020_codes` toolbox. The toolbox requires MATLAB/LTFAT and C-OMP requires CVX; no exact runnable source revision, immutable bytes, SHA-256, reviewed licence/redistribution record, or pinned runtime is staged. Bounded read-only probes confirm absence at declared workspace, SDK and home-cache paths; no download, import, load or audio read occurs.
4. **Installed geometry.** The contract accepts only 16 kHz, mono, float32 and 160-sample frames. Synthetic integer grid/occupancy probes cover installed-grid framing and clipping-occupancy strata as structural fixtures; they are not SPADE parameters, not measured renderer output and cannot qualify the candidate.
5. **Caller-supplied boundary.** A metadata-only manifest is validated for adapter, configuration, source revision, digests, rights and format. Even a hash-matched local file fails closed as `SPADE_SOURCE_IDENTITY_UNPINNED`: no source is read as code, loaded or executed, and no renderer is promoted.
6. **Restoration profile.** Identity/noisy control, POCS/clipped-identity comparison, SI-SDR/STOI, speech preservation, peaks/invalid outputs, alignment/state/memory and content/availability timing are blocked because no exact source, runtime or rights-cleared cohort exists. Source-reported descriptions are not local results.
7. **Adversarial controls.** All caller-manifest mutations, invalid JSON forms and invalid pin lines are rejected. Three cold-start SHA-256 builds of the canonical report are byte-identical.

## Decision and reopening

`DEFER` at `opt_in_adapter_exposure`: all eight gates `RG-01`…`RG-08` remain `blocked` and `qualifies: false`. Exact external blockers:

- `XB-01` — exact runnable SPADE/social-sparsity source absent. Reopen with an exactly pinned runnable source/artifact (revision, bytes, SHA-256 and reviewed rights record).
- `XB-02` — runtime and installed geometry unpinned. Reopen with a pinned MATLAB/LTFAT/CVX or rights-cleared port runtime and deterministic 16 kHz mono float32 160-sample geometry on a hash-matched caller asset.
- `XB-03` — matched restoration cohort and scorers absent. Reopen with a frozen rights-cleared clipped-speech cohort, corruption metadata, clean references and matched POCS/clipped-identity controls with pinned SI-SDR/STOI/preservation scorers.
- `XB-04` — release and timing gates unmet. Reopen with target-runtime paced availability/content-delay/memory evidence, rights/runtime clearance, and independent opt-in review with default OFF.

This is an accepted investigation handoff. It does **not** close the conditional implementation row. Missing, blocked, source-reported or synthetic results do not qualify the candidate.

## Reproduce

From this directory, with pinned Python 3.12.16:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

From the worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

## Source pins (workspace-relative, `source:` prefix)

<!-- digest-table: source -->
| Path | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` |
<!-- digest-table: end -->

## SDK-worktree boundary pins

<!-- digest-table: boundary -->
| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/band-limited-pocs-declipping/README.md` | `8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65` |
| `docs/task-evidence/linear-interpolation-declipping/README.md` | `ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d` |
| `docs/task-evidence/survey-rst-01/README.md` | `5888f8745720a90a6926ccbd158597e5804c0fc1fb937918f26da495b053d68a` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->
