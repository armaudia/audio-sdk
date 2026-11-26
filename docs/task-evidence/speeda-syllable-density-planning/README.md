<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-SPEEDA-SYLLABLE-DENSITY-PLANNING — task-local feasibility evidence

Task-local, proposal-only, **incomplete** and **not_qualified** feasibility
evidence for `Speeda syllable-density planning`
(`component_id=speeda-syllable-density-planning`). The assigned acceptance
profile is **Rate**. Machine-readable decision: **DEFER**;
`status=proposal_only_asset_intake_incomplete_not_qualified`;
`evidence_status=incomplete`; `qualification.status=not_qualified` (field:
`qualification_status` in `report.json`). No result in this package qualifies
the candidate.

This package does **not** import, load, link, execute, copy, vendor or download
a Speeda implementation, syllable detector, PSOLA/TSM runtime, ASR, audio
corpus or listening panel. It does not read, write, render or play real audio;
does not measure a device clock, callback deadline, FIFO occupancy or
pitch/transient audibility; does not benchmark the SDK; and makes no release
claim. Every interval is a half-open coordinate in a synthetic 16000-sample
fixture at 16 kHz, mono, float32, with 160-sample source frames.

## Boundary

Installed v0 geometry is unchanged and documented only:
`16000 Hz`, 1 channel, `float32`, 160 samples per call. No provider, default,
descriptor, registry entry, ABI, CONTRACTS, shared-build or CI file is changed.
The adapter/provider remains OFF, unregistered and not exposed. No
caller-supplied asset is embedded, downloaded, parsed as source or executed;
the package only models a strict metadata/byte-hash intake shape. Board,
handoff, reviewer dispatch and release state are untouched.

## Decision, gates and blockers

All gates RG-01 through RG-08 are **blocked** and `qualifies=false`: exact
runnable source; exact assets and rights; installed-v0 boundary intake; typed
syllable/pause annotations; syllable-density measurement; Rate-profile
evidence; playback pacing and listening; and public admission review. `DEFER`
is before `opt_in_adapter_exposure`. Exact blockers B-01 through B-04 and their
reopening conditions are in `report.json` and `contract.json`.

Source-reported claims are kept as provenance only. The pinned note describes
Speeda as per-segment rate from syllable density, pauses shortened to ~0.2 s,
target overall duration, with no real-time transport/threshold/prediction
structure. The pre-screen used three clips, no listener result and cannot
select a planner. None of those numbers is reproduced or promoted here.

## Synthetic syllable-density controls

The synthetic envelope uses typed classes `speech` and `pause` in source-sample
coordinates. Speech rate is computed from synthetic syllable count / duration
versus global syllable density, clamped to 3/4-3/2 and made integer-output by
construction of the fixture. Pause segments are shortened toward a 0.2 s target
by bounded rate arithmetic and are **not deletion**. A 200 ms minimum dwell is
enforced. The identity control is a byte-identical integer sequence, explicitly
not a Speeda or TSM result.

This is annotation arithmetic only: no syllable detector, phoneme aligner,
PSOLA/actuator, pitch/transient metric, listening, unfamiliar speech, music,
rebuffer, drift or final partial-window audio behavior is measured.

## Caller-supplied asset contract (not satisfied)

Six external assets are required for reopening: source revision, syllable
detector/alignment model, runtime lock, typed annotation schema, rights-cleared
cohort manifest and matched reference output. Each must be caller-owned,
referenced by exact id, byte count and lowercase SHA-256, with licence/consent
review sidecars. The shape-only verifier rejects duplicate keys, field-set
drift, missing/empty identifiers, bad digests, relative or traversal paths,
duplicate paths, embedded storage, absent bytes, byte-count mismatch and hash
mismatch. A hash-matched placeholder is still shape-only and never qualifies.
No such assets are present in the workspace or SDK worktree; absence is not a
runtime, rights or quality result.

## Reproduction

```text
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m reuse lint
git -C ../../../ diff --check
```

`verify.py` is read-only and fails closed on duplicate-key/nonfinite JSON,
stale pins, stale canonical artifacts, stale README digest tables, unexpected
files, license gaps, whitespace damage, unavailable scope base, branch-diff
changes outside this task prefix (`base_out_of_scope_change:<path>`) and a dirty
diff check. The strict scope gate resolves the newest merge-base of HEAD with
`origin/main` or `main`; if neither ref exists it emits `scope_base_unavailable`.

Canonical artifacts are `report.json`, `report.json.sha256`, `contract.json`
and `SOURCES.sha256`. The board link pins only stable row identity, never the
mutable full `plan/swarm/TASKS.json`.

Base commit: `4c0f5464eeddff2204b527e8bc4ad09c41b2a657`.
Task ID: `SDK-SPEEDA-SYLLABLE-DENSITY-PLANNING`.

<!-- digest-table: source -->
| Pin key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:cpp-library/pipeline-validation/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` |
| `source:cpp-library/pipeline-validation/playback-speed/results/report.md` | `9c9383297b1160dbe4f7261f789b493d70354b11930f4d8527b20b0ca8c87c34` |
| `source:cpp-library/pipeline-validation/playback-speed/results/results.json` | `69b5bcc4dc3740bacc182e93419b6a83d5c3eebba7d9b4dfdd8fe4b09813cfc1` |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
<!-- digest-table: end -->

<!-- digest-table: boundary -->
| Pin key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/aix-speed-asr-guided-planner/README.md` | `4a5748b4e8d4c723b5ef2ce606c270c2d14b07beb9930b062520190cf0d8b28c` |
| `docs/task-evidence/aix-speed-asr-guided-planner/report.json` | `a71ce94ad0b701c9d302edf1c74338c7d1586d573a7295510fd3584b26110873` |
| `docs/task-evidence/d1-whole-clip-duration-planner/README.md` | `4015900d23ad2bbceef0b44f4a3ae954a3adc6ada60398e303ace82dc0545418` |
| `docs/task-evidence/d1-whole-clip-duration-planner/reference.py` | `ffb59e3d09d7cef0580d73cf9772d6e69d0ddfb991457e7878ac4bf86cf7c253` |
| `docs/task-evidence/source-vad-conditioning-for-playback/README.md` | `26d98518eda620228808587d5a396f9111794e80c333cbf594c8365b9a21f135` |
| `docs/task-evidence/source-vad-conditioning-for-playback/report.json` | `1f180b14ef33466f0950fe9128aa88be1004aca141d762bffff96822e7ec007a` |
| `schemas/descriptor.schema.json` | `9db5fee497272ecf2c734f31cfb0a4662b43c01d745f856745ca9bcdcdc9c2ba` |
| `schemas/effective-config.schema.json` | `55956e149b3b8c420599c1a115e2b880ba4659c562128c207f89842b79cc5eea` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->
