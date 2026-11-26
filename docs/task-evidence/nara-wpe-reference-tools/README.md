<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-NARA-WPE-REFERENCE-TOOLS — NARA-WPE tool readiness blocker

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory is bounded,
deterministic, task-local evidence for the NARA-WPE reference-tools row. The
acceptance profile is **Room**, assigned by
`plan/INVENTORY.json` (`disposition=sdk-reference`,
`evidence_status=considered`). It is **not** a NARA-WPE implementation,
adapter, provider or qualification. No upstream checkout, wheel, revision,
licence, runtime, output vector, real audio, listening result, device timing,
benchmark or release claim is present. **No result here qualifies NARA-WPE.**

The task deliverable asks to verify runnable source, exact assets, permitted
scope, task geometry and matched evidence, then either reproduce the NARA-WPE
reference tools as a caller-supplied tool reference or record a strict
readiness conclusion with the exact external blocker and reopen condition. The
source and assets are absent, so this package records the second option.

## Exact external blocker

The workspace records NARA-WPE only as two provenance rows:

- `research/category_survey/sources.md` source `S20`:
  `https://github.com/fgnt/nara_wpe`, access scope `search excerpt`;
- `research/category_registry.json`: the same source URL and access scope.

Neither record contains excerpt text, an immutable revision, a package name or
version, a wheel or source archive, a per-file hash, licence text, default
STFT/hop/taps/predictor geometry, a runtime lock, an output vector or a
rights record. The dereverberation research note names the project only in its
primary-source list. No NARA-WPE checkout exists under any fixed probe.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `https://github.com/fgnt/nara_wpe` at an immutable 40-hex commit, with a per-file SHA-256 manifest and the reviewed upstream licence text |
| Package identity | Exact package name, version, wheel or source-archive byte count and SHA-256; the register records only the repository URL |
| Runtime | A locked, offline-reproducible Python 3.12.16 environment with exact NumPy/SciPy versions, wheel hashes and platform pin |
| Geometry | Upstream FFT, hop, window, taps, predictor delay, iterations, offline-versus-online behaviour, reset and partial-tail handling; only the project defaults are pinned here |
| Parity vector | Frozen caller input, matched 512/128/5/8 configuration and exact upstream output vector against project `wpe_offline` |
| Rights | Source, package, redistribution, derivative-output and product-use terms; no term is assumed from the URL |
| Room cohort | Rights-cleared paired room fixtures with a frozen 50 ms early-reflection target and identity control |
| Release | Opt-in intake, target-device timing, listening protocol and explicit release approval |

The machine-readable record is `contract.json` and `report.json` →
`upstream_identity`, `task_geometry`, `absence_audit`, `caller_asset_contract`,
`matched_evidence`, `room_profile`, `gates` and `blockers`.

## What this package verifies

1. **Absence evidence.** Thirteen fixed workspace probes are checked without a
   recursive walk. `reference.audit_assets()` and `verify.py` fail if any probe
   appears, so a stale "absent" claim cannot ship.
2. **Stable pins.** The category registry, source register, search log,
   dereverberation note, project WPE adapter README, inventory and Room profile
   are pinned by SHA-256 as read-only provenance. Boundary files, including
   `CONTRACTS.md`, both public v0 headers, `CMakeLists.txt`, `REUSE.toml`,
   `.github/workflows/ci.yml`, `.gitattributes` and `scripts/ci.py`, are pinned
   unchanged. Sibling project WPE reports are pinned as separate evidence only.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes.
4. **Strict caller-supplied tool contract.** A caller manifest schema requires
   exact source revision, package/wheel identity, runtime lock, matched
   geometry, parity vector, cohort and rights fields. Missing, extra,
   duplicate, nonfinite, wrong-type, boolean-as-integer, unsafe-path,
   wrong-digest, wrong-package, wrong-runtime, wrong-geometry and
   qualification-claiming manifests are rejected before any load. One
   synthetic structural control is accepted only to prove the validator is not
   blanket-rejecting; it is labelled `not_evidence` and `qualifies=false`.
5. **Fail-closed pinned admission.** Even a structurally valid caller manifest
   cannot be admitted as the pinned source while the exact upstream checkout is
   absent; the path reports `upstream_source_absent`.
6. **Synthetic geometry control.** A deterministic integer-derived f32 signal
   checks the pinned project grid (16 kHz mono, 512 FFT, 128 hop, 5 taps,
   8-frame delay), the 800-sample/50 ms early-target window, the declared
   256 + 1024 = 1280-sample/80 ms algorithmic latency, the final partial
   frame, identity, and config/nonfinite rejection. It is **not NARA-WPE**, runs
   no STFT or filter, reads no audio and cannot qualify the candidate.
7. **Boundary preservation.** Installed v0 remains 16 kHz, mono, float32 at
   160 samples per frame. No provider, default, public ABI, `CONTRACTS.md`,
   registry, descriptor, shared build, CI, board or handoff change is made.

## Permitted scope

The only write scope is `docs/task-evidence/nara-wpe-reference-tools/`. The
package is optional, unregistered and disabled by default. It does not add a
provider manifest, adapter manifest, descriptor, registry entry, installed
default or shared build file. It performs no download and consumes no real
audio. It makes no listening, device-timing, benchmark, qualification or
release claim.

## Task geometry

The **project** WPE reference geometry is pinned from
`adapters/wpe/README.md` and `docs/task-evidence/offline-mono-wpe/report.json`:

| Field | Pinned project value |
| --- | ---: |
| Sample rate / channels | 16,000 Hz / 1 |
| Sample format | float32 |
| FFT / hop | 512 / 128 samples |
| Prediction taps | 5 |
| Predictor delay | 8 frames |
| Iterations | 3 |
| Early target window | 50 ms / 800 samples |
| Centred-STFT lookahead | 16 ms / 256 samples |
| Predictor delay | 64 ms / 1,024 samples |
| Declared algorithmic latency | 80 ms / 1,280 samples |
| Processing modes | whole-clip offline; frame-causal RLS |

These are **project** defaults. The upstream NARA-WPE geometry is
`unestablished`; no upstream value is asserted. A future parity run must match
the project fields above, and the caller manifest records the declared window
for review because the project report does not pin a window identifier.

## Matched evidence

No NARA-WPE output exists, so no matched SI-SDR, STOI, SRMR, PESQ or RTF row is
reported. The sibling project WPE packages are pinned and named as separate
evidence only:

| Sibling evidence | Role |
| --- | --- |
| `docs/task-evidence/offline-mono-wpe/report.json` | Project mono offline/causal WPE context; not NARA-WPE |
| `docs/task-evidence/offline-multichannel-wpe/report.json` | Project multichannel WPE context; not NARA-WPE |

Their results are never pooled, imported, reinterpreted or substituted. The
matched comparison is `blocked`.

## Room profile application

| Room requirement | Status here | Evidence |
| --- | --- | --- |
| Frozen render/reference | blocked | No NARA-WPE output or frozen render |
| Channel/rate/hop | control only | Project 16 kHz mono 512/128/5/8; upstream unestablished |
| Excitation | not applicable | No dereverberation is run |
| Delay | control only | Declared project 1,280 samples/80 ms; upstream unestablished |
| Movement | not applicable | No render path or measured room movement |
| Noise | blocked | No rights-cleared noisy-speech stratum |
| Reset schedule | blocked | No upstream runtime or candidate state |
| Echo-only | not applicable | Dereverberation is not playback AEC |
| Near-end-only | not applicable | No near-end/render decomposition |
| Overlap | not applicable | No double-talk condition |
| No-reference | blocked | No candidate output to compare |
| Echo attenuation | not measured | No echo cancellation attempted |
| Near-end damage | blocked | No candidate output or early-target score |
| Nonfinite failures | control only | Three injected nonfinite values rejected |
| Alignment, delayed/missing render | control only / not applicable | Exact half-open frame grid; no render channel |
| No-reference independent comparison | blocked | No independent comparison, corpus or listener |

## Geometry control results (not NARA-WPE)

These are exact `report.json` values. They are synthetic structural
observations, not dereverberation results.

| Invariant | Exact value |
| --- | ---: |
| Control source samples | 64,037 |
| Frame hop | 128 |
| Frame count | 501 |
| Final frame source-valid samples | 37 |
| Early target window | 800 |
| Declared algorithmic latency | 1,280 samples / 80 ms |
| Contiguous half-open coverage | true |
| Identity bit-exact | true |
| Config rejections | ≥ 20 |
| Nonfinite rejections | 3 |
| Dereverberation performed | false |
| Qualifies | false |

## Release gates (all blocked)

1. `exact_source_and_asset_identity`
2. `runtime_admission`
3. `artifact_rights_and_licence`
4. `exact_reference_parity`
5. `matched_room_policy`
6. `task_scope_and_geometry`
7. `opt_in_provider_intake`
8. `public_default_and_release`

Exact blocker IDs: `source_checkout_absent`, `upstream_revision_unpinned`,
`package_metadata_and_license_absent`, `runtime_and_lock_absent`,
`matched_parity_vector_absent`, `task_geometry_unestablished`,
`matched_room_cohort_and_rights_absent`,
`opt_in_provider_and_release_absent`.

**Reopen condition.** Supply the exact NARA-WPE source revision and reviewed
licence; the exact package/wheel identity; a hash-pinned offline Python 3.12.16
runtime; the upstream FFT/hop/window/taps/predictor/iterations and
offline/online behaviour; a frozen matched parity vector against project
`wpe_offline`; a rights-cleared paired room cohort with a frozen 50 ms early
target; and an opt-in provider/descriptor review. Then reproduce the exact
outputs, score the cohort with identity and independent controls, measure
target timing and complete an OFF-by-default intake. Until then the candidate
stays **DEFER**, **incomplete** and **not qualified**.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: blocker, scope, geometry, checks, gates, digests. |
| `reference.py` | Absence audit, caller manifest validator, geometry control, builders, scope comparison. |
| `run.py` | Regenerates contract, report, README artifact table and `SOURCES.sha256` three times. |
| `report.json` | Canonical machine-readable Room report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `contract.json` | Task contract: profile, scope, pins, gates, blockers, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips or network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, cold-start, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned audioml workspace root. Every row is
machine-checked by `verify.py` and the test suite.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:adapters/wpe/README.md` | `b36f1af3151ea28df9b6c12f3adb90d0b4f28f4315d0aeccd0ff9c99050c703e` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/category_registry.json` | `cdf1782853fde1291bb8fd3c64144b9e857939856f8caca1666d2d617845728c` |
| `source:research/category_survey/search_log.jsonl` | `61f95809f956537bea9b878cd544f8e997d6c13a24d2e9ea947795f653847b09` |
| `source:research/category_survey/sources.md` | `9dc17cd557480b954af4d5d9cd24911423685ba23675f399500eb080315fac5d` |
| `source:research/dereverberation_candidates_20261028.md` | `6f0f1a07aeb7b865dce766576bcc99cb97a78120253b1f9e1e9618f964098468` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` |
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/task-evidence/offline-mono-wpe/README.md` | `c57df3412bd9e491e5bb4a32b20cf834ecee41da25ce68130d728b48b8877819` |
| `sdk:docs/task-evidence/offline-mono-wpe/report.json` | `2b9be2488c4b0f82f417abd3e131c840729856937ed8239f2645beeaa30d7e61` |
| `sdk:docs/task-evidence/offline-multichannel-wpe/README.md` | `8aa8b92ec4a436aaced397913c45963ae4b95d10a798763062b9cafa53f250c9` |
| `sdk:docs/task-evidence/offline-multichannel-wpe/report.json` | `4362c19cfd0633450af24bf9bc5124dbe2a90c9ad48164edf08b377c24ec8fba` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` and `contract.json` are canonical JSON (sorted keys, indent 2,
`allow_nan=False`, LF, one trailing newline). The table is refreshed by
`run.py` and checked by `verify.py`. `SOURCES.sha256` pins every artifact and
this README; it does not pin itself.

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `40154758982b1a7a2af22c376fc59e2b4797549e6b44b586dc92176b4e1a4b3c` | 19883 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `32d7ec3762cb854496d289045c547b214fd36fcbf9dc1f60840820f61a397034` | 78063 |
| `report.json` | `7ed65ec26de33815a42514b51921cc939e72fb2f57294e31e56b357f5ac87ee9` | 24557 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `aa58cea890d357dcd375b5680ff820ab666e2da7ecff8441615a53ecb34de6ef` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `781acbb1103fa76bd9fd86e362ee1359a9e930f03947eac68d688fd840f7e59e` | 3248 |
| `test_reference.py` | `c6e376378d96b1aabbb2401bdc7a2d95abb9508a0499cc91986831306ea7f917` | 23869 |
| `verify.py` | `22b83d027eca8d779b568f74de53f0ead7db3ec06c8f002dfdaaf43d4c71c24e` | 27901 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

## Reproduction

Run from this directory with the pinned interpreter and bytecode disabled:

```sh
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
PYTHONDONTWRITEBYTECODE=1 "$PY" run.py all
PYTHONDONTWRITEBYTECODE=1 "$PY" -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 "$PY" verify.py
python3 -m reuse lint
git diff --check
```

The installed-package check is run from the SDK worktree root:

```sh
PYTHONDONTWRITEBYTECODE=1 "$PY" scripts/ci.py
```

`run.py` writes the contract, canonical report, README artifact table and
`SOURCES.sha256` three times and requires byte-identical output. `verify.py`
re-runs three independent cold-start regenerations in scratch trees and fails
on any pin drift, out-of-scope branch change, missing sidecar, missing SPDX
header, stale digest table or absent blocker. `scripts/ci.py` packages and
tests the installed SDK only; it never imports or executes NARA-WPE.

## Non-claims

No NARA-WPE source, wheel, revision, licence, runtime or output is present. No
real audio, RIR, corpus, listening, device timing, benchmark, qualification or
release approval is used or claimed. No provider, default, public ABI,
`CONTRACTS.md`, registry, descriptor, shared build, CI, board or handoff change
is made.
