<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SOX-NOISERED — SoX `noisered` caller-supplied-profile readiness check

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for SoX `noisered` (`component_id=sox-noisered`). The Enhancement
acceptance profile is defined in `plan/swarm/VERIFICATION.md` and assigned by
`plan/INVENTORY.json`. Base commit:
`022a7ad3cedf35aba70ef93b32b71ae51e1e30ca`; branch:
`swarm/SDK-SOX-NOISERED`; reviewer: `reviewer-SOX-NOISERED`. Decision: **DEFER**
before `opt_in_adapter_exposure`. No missing, blocked or synthetic result
qualifies the candidate.

## What this package does and does not do

This package models a **caller-supplied noise-profile asset boundary** and the
installed SDK geometry: **16000 Hz**, **mono**, **float32**, **160-sample
frames**. The profile proxy is 160 synthetic in-memory float32 values (640
bytes) with a recorded SHA-256; it is explicitly **not** a SoX-generated noise
profile. The caller manifest validator checks adapter identity, geometry,
absolute asset paths, byte counts, SHA-256 values, canonical amount and the
required source/build/license identity fields, then fails closed with
`SOX_PROFILE_IDENTITY_UNPINNED`. No asset is loaded or executed.

No SoX source, binary, header, archive, library, noise profile or audio asset is
vendored, downloaded, imported, loaded or run. `shutil.which("sox")` found no
executable, and the fixed absence probes found no source tree, profile, adapter
or asset directory. No real audio, rights-cleared cohort, clean reference,
listening panel, device timing, benchmark result or release claim is present.
No provider, descriptor, registry, default, ABI, `CONTRACTS.md`, shared build or
CI behavior is changed. The only write scope is
`docs/task-evidence/sox-noisered/`.

## Source evidence

The pinned census row at `research/noise_suppression_candidate_census.md:49`
records SoX `noisered` as classical profile-based spectral reduction with no
weights. It is a **conditional baseline**: use only when profile provenance is
supplied, and verify the build licensing configuration. The source row is
read-only evidence, not a quality result. No source-reported SoX number is
present in the row, and no other denoiser score is pooled into this package.

## Exact readiness conclusion and reopen conditions

All Enhancement gates are blocked. The concrete external blockers are:

- **XB-01** — no permitted SoX source tree, exact revision, archive digest,
  installed executable, build ID or build licensing configuration. Reopen by
  staging the exact licensed revision with archive SHA-256, notices, a
  reproducible build ID and a reviewed build-license configuration.
- **XB-02** — no representative noise-only segment or SoX-generated profile
  with provenance, byte count and SHA-256. Reopen by supplying a rights-cleared
  segment, generating its profile with the pinned build, and recording exact
  mode, amount, byte count and SHA-256.
- **XB-03** — no rights-cleared paired cohort, clean references, identity/noisy
  control, established baseline, scorer or listening protocol. Reopen by
  freezing the cohort and controls, agreeing metric margins and the analysis
  plan, then scoring real candidate outputs.
- **XB-04** — no target-runtime alignment/state/memory/deadline evidence,
  opt-in intake, OFF-default decision or independent exact-head review. Reopen
  by running the paced target harness, completing separate opt-in intake with
  default OFF, and obtaining independent exact-head approval.

Gate coverage: `RG-01` exact source/build/license identity; `RG-02` profile
provenance; `RG-03` paired cohort and controls; `RG-04` independent quality or
listening protocol; `RG-05` paired metrics and preservation; `RG-06`
alignment/state/memory/target timing; `RG-07` opt-in intake and OFF public
default; `RG-08` independent exact-head review. Every gate is `blocked`,
`qualifies=false`.

## Evidence classes

| Class | Present here | Qualifies |
|---|---:|---:|
| Pinned census source line | yes | no |
| Synthetic 16 kHz mono float32 geometry | yes | no |
| Synthetic profile proxy | yes | no |
| Strict manifest/JSON/pin rejection controls | yes | no |
| Real local SoX output | no | no |
| Real audio / paired cohort | no | no |
| Listening or authorized predictive score | no | no |
| Device timing / memory / deadline | no | no |
| Benchmark or release claim | no | no |

Adverse controls: 17 caller-manifest cases, 7 strict-JSON cases and 5 pin-parser
cases are all rejected. The geometry cover is exact: two full 160-sample frames
plus a 5-sample final frame with 155 zero-padding samples cover samples
0..324 with no overlap or gap. This is an integer in-memory probe only, not a
measured SoX content delay. Identity control repeats a synthetic frame
byte-for-byte and does not qualify.

## Reproduction

Use the pinned Python 3.12.16 interpreter with bytecode disabled. From the SDK
worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest discover -s docs/task-evidence/sox-noisered -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/sox-noisered/run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/sox-noisered/run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 docs/task-evidence/sox-noisered/verify.py
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/sox-noisered-ci
python3 -m reuse lint
git diff --check
```

`run.py --all` regenerates `report.json`, its SHA-256 sidecar, `SOURCES.sha256`
and `contract.json` in sorted order. It never writes outside this directory.
`run.py --check` and `verify.py` are read-only; `verify.py` also checks README
digest tables, license sidecars, source/boundary pins, duplicate-key and
nonfinite JSON, canonical bytes, the newest-merge-base branch-diff scope,
`git diff --check` and three fresh report builds. The scope verifier uses the
newest merge-base of `HEAD` with an available `origin/main` or `main` ref,
emits `scope_base_unavailable` when neither ref exists, and emits
`base_out_of_scope_change:<path>` for any changed path outside
`docs/task-evidence/sox-noisered/`.

## Source-digest table

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` |
<!-- digest-table: end -->

## Boundary-digest table

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifacts and licensing

`report.json` is the canonical evidence report. `report.json.sha256` is its
SHA-256 sidecar. `SOURCES.sha256` pins the read-only source and boundary files
plus the task-local artifacts. `contract.json` binds the same decision, gates,
blockers and artifact pins. `.license` sidecars cover all generated JSON and
SHA-256 files; `LICENSES.md` records that no third-party SoX artifact is
vendored. REUSE coverage remains the unchanged aggregate `docs/**` rule in
`REUSE.toml`.
