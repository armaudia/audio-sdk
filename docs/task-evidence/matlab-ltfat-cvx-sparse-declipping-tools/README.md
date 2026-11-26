<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS — vendor/tool blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **vendor-boundary and blocker package** for inventory
component `matlab-ltfat-cvx-sparse-declipping-tools` (Runtime and tooling,
mode `external-adapter`, verification profile `tool`). The task deliverable is
to document the vendor boundary and prototype an isolated adapter **only if**
an approved public or user-supplied runtime is available. No approved runtime
is available, so no adapter is built.

The exact licensed `declipping2020_codes` source, a resolved toolbox revision,
a licensed MATLAB installation, LTFAT, the optional CVX path, one documented
typical tool use, its expected numeric output, the rights record, an approved
public-surface decision, a paired clipped/clean cohort and a parity vector are
absent. This package creates **no adapter, execution, toolbox, corpus, real
audio, provider, processor, ABI, registry, default, shared build, CI, board,
handoff or release change**.

Task owner: `agent-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS`; reviewer:
`reviewer-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS`. Claim base: audio-sdk
`0cc1e79e592d7fc25f054fcd98824053be281f5e`; branch
`swarm/SDK-MATLAB-LTFAT-CVX-SPARSE-DECLIPPING-TOOLS`. The task depends on
`SDK-FND-AUDIT` and `SDK-FND-EVIDENCE`; write scope is the task-local evidence
directory only (`docs/task-evidence/matlab-ltfat-cvx-sparse-declipping-tools/`).

## Vendor boundary (documented, not bridged)

| Boundary item | Recorded state |
| --- | --- |
| Toolbox | `declipping2020_codes` — authors’ open MATLAB toolbox for sparse/constrained declipping |
| Required runtime | MATLAB — proprietary, licensed product; **absent**, no licence basis recorded |
| Required dependency | LTFAT (frame/dictionary) — **absent**, no revision recorded |
| Optional dependency | CVX — optional convex solver path used for the C-OMP comparison; **absent**, no revision recorded |
| Documented typical use | **absent** — no invocation, geometry, expected output or tool version |
| Clean checkout / extracted package | **absent** — no checkout at any alias path |
| Install location and version | **absent** — `version=null`, `install_location=null` |
| Approved public or user-supplied runtime | **absent** — the conditional adapter prototype is not attempted |
| Local runtime vs vendor-output scoring vs vendor claim | all three **absent and kept separate** |
| Fallback without a licensed runtime | merged sibling synthetic controls only; they neither reproduce nor approximate the toolbox |
| Disclosure without a licensed runtime | report the blocker; never present a sibling control as the toolbox method |

The vendor boundary is documented in `contract.json` under
`external_adapter_boundary` and repeated in `report.json`. Nothing is
downloaded, vendored, registered or invoked; `adapter.json` is deliberately not
created and `data/adapters/matlab-ltfat-cvx-tools/adapter.json` is a fixed
absence probe that must stay absent.

## What is missing and why no result can qualify

The merged research document `research/distortion_restoration_20261028.md`
(RST-01, declipping/saturation, evidence line 42) records the only provenance:

> The established next comparison is a constrained sparse declipper such as
> SPADE or social sparsity. The authors’ open MATLAB toolbox evaluates many
> sparse/constrained methods, but requires MATLAB, LTFAT and (for C-OMP) CVX,
> so it was not runnable in the current Python pilot.

It records the authors’ project page `https://rajmic.github.io/declipping2020/`
and repository `https://github.com/rajmic/declipping2020_codes`. It does **not**
record a resolved commit, a toolbox version, a licence, a documented
invocation, a numeric row or a local output. The paired synthetic screen
`reports/distortion-restoration/20261028-synthetic-screen.json` contains only
`clipped_input`, `linear_interpolation` and `bandlimited_POCS` methods for
RST-01; there is no toolbox or C-OMP method row.

`audit_assets()` probes fixed workspace paths and records that no
`declipping2020_codes` checkout (or alias), no MATLAB/LTFAT/CVX installation,
no environment manifest, no documented tool use, no expected output, no
licence, no rights record, no cohort, no parity vector, no output-use grant and
no adapter prototype exist. Nothing is downloaded, vendored or inferred from
the recorded URLs. Consequently:

- tool version, install location, provenance, per-file hashes and licence
  terms cannot be pinned;
- MATLAB is a proprietary runtime and neither LTFAT nor the optional CVX path
  is present; no licensed, isolated environment can be admitted;
- no typical CLI/API use can be executed, so there is no compile/build,
  synthetic runtime or measured-workload evidence to separate;
- no candidate output exists, so no SI-SDR, RMSE, STOI, WER, MOS, latency,
  memory, RTF or listening value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

## Tool-profile reporting (all unsatisfied for qualification)

| Requirement | Package status | Qualification effect |
| --- | --- | --- |
| `version_install_location_and_provenance` | absent | none |
| `clean_checkout_or_extracted_package` | absent | none |
| `typical_cli_or_api_use` | absent | none |
| `caller_owned_inputs` | structural_only | none |
| `malformed_inputs` | synthetic_only | none |
| `missing_optional_selections` | synthetic_only | none |
| `evidence_class_separation` | structural_only | none |

Only rejection/structural accounting is exercised. No tool version, install
location, clean checkout, typical use, real input run, measured workload or
parity exists, so the `tool` profile is not satisfied for qualification.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_tool_identity` | Full 40-hex toolbox/LTFAT/CVX revisions, MATLAB release identity, toolbox version, install location, experiment config and metadata hashes match exact pins | blocked |
| `runtime_and_toolbox_admission` | Isolated, licensed MATLAB runtime plus LTFAT and the optional CVX path with a complete environment manifest on a recorded platform | blocked |
| `artifact_rights_and_licence` | Toolbox, MATLAB, LTFAT, CVX, source-audio, clean-reference, output-use and redistribution rights cleared with notices | blocked |
| `clean_install_and_typical_use` | Clean checkout or extracted package verified and one documented typical CLI/API use produces a reproducible numeric result | blocked |
| `malformed_and_missing_optional_inputs` | Caller-owned inputs validated; malformed inputs and missing optional selections rejected before processing | blocked |
| `vendor_boundary_and_disclosure` | Allowed access, exact candidate data, local runtime versus vendor-output scoring versus vendor claim, fallback and disclosure approved | blocked |
| `opt_in_adapter_intake` | Explicit opt-in adapter intake, licence review and independent public-surface decision complete; optional only | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release or benchmark approval; off by default | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent toolbox checkout, unpinned upstream revision and tool
version, absent licensed MATLAB runtime, absent LTFAT at an exact revision,
absent optional CVX path, absent documented typical tool use, unverified vendor
terms and rights, and absent isolated adapter plus parity/workload evidence.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the experiment config, licence record, rights record, documented tool use,
cohort manifest, parity vector and output-use grant; full 40-hex source, LTFAT
and CVX revisions; nonempty MATLAB and tool version strings; an absolute tool
install location; exactly 16 kHz mono; a block size between 160 and 65,536
samples aligned to the 160-sample SDK frame; and the declared
`isolated_offline_toolbox_adapter` variant. Any missing, malformed, nonfinite,
out-of-range, mismatched or unapproved variant is rejected before processing.
No upstream revision is pinned because the merged evidence records only project
and repository URLs; a shape-valid manifest cannot manufacture qualification.

## Synthetic control (not the toolbox)

The control uses 16,000 samples (1.0 s) at 16 kHz mono, exactly 62,500 ns per
sample. Clean samples are deterministic binary32 triangle/LCG values with a
declared peak bound of 0.90. Hard clipping is symmetric at the binary32
quantization of each threshold; the mask is exact equality with that threshold.
A quiet no-clip case at threshold 0.55 has zero occupancy.

| Case | Threshold | Clipped samples | Occupancy | Mask runs | Peak in → clipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clipped_0_35` | 0.35 | 5,996 / 16,000 | 37.4750% | 594 | 0.9000 → 0.3500 |
| `clipped_0_55` | 0.55 | 2,374 / 16,000 | 14.8375% | 371 | 0.9000 → 0.5500 |
| `quiet_no_clip_0_55` | 0.55 | 0 / 16,000 | 0% | 0 | 0.1800 → 0.1800 |

The control never computes a declipped sample, SI-SDR, RMSE, STOI or a
listening score and never invokes MATLAB, LTFAT, CVX or the toolbox. All eight
`acceptance_outcomes` are `measured=false` with `value=null`.

## Adverse, missing, invalid and nonfinite handling

`report.json` records 43 rejections with their reason and unchanged state:
empty/non-sequence/`None` PCM, wrong rate, stereo, `NaN`/`±Inf`, out-of-range,
boolean/string samples, missing/extra config fields, threshold 0/1/negative/
above-one/nonfinite/boolean/string, duplicate JSON keys, nonfinite JSON
constants, and caller manifests with missing/extra fields, relative paths, bad
hashes, short/nonhex source/LTFAT/CVX revisions, empty MATLAB or tool version,
wrong variant/rate/channels, too-small/misaligned block, missing asset, missing
directory (including the tool install location) or hash mismatch. Missing real
recordings, toolbox source, runtime, documented use, workload and labels are
`blocked`, never passes.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path
  source/toolbox/runtime/vendor audit, caller manifest validation, exact
  binary32 clipping-mask accounting and 43 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers, the vendor boundary, runtime requirements and
  the caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK contract files,
  merged sibling evidence packages and package files. The mutable full
  `plan/swarm/TASKS.json` is **never hashed**; only the stable linked-row
  fields are projected to a digest (`ef55c31a67b2…fedd3a`).
- `run.py` — three byte-identical in-process regenerations before writing.
- `test_reference.py` — deterministic unittest checks; no skips or network.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/matlab-ltfat-cvx-sparse-declipping-tools
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
python3 -m reuse lint   # from the SDK root
```

JSON, digest and manifest files have SPDX `Apache-2.0` sidecars. All files are
inside this task directory; board, handoff and reviewers were not changed or
dispatched. No merge, formal approval or release action is taken. Workspace
pins are SHA-256 values of read-only documents; a pin grants no rights and
verifies no media. `SOURCE_ROOT` can point to the enclosing `audioml` checkout
if automatic discovery is unavailable.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` |
| `source:reports/distortion-restoration/20261028-synthetic-screen.json` | `87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`worktree:` paths are relative to this SDK worktree. All are unchanged and
machine-checked by `SOURCES.sha256`.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `worktree:docs/task-evidence/band-limited-pocs-declipping/README.md` | `8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65` |
| `worktree:docs/task-evidence/band-limited-pocs-declipping/report.json` | `8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b` |
| `worktree:docs/task-evidence/c-omp-declipping/README.md` | `0891576454410a354c3bebb0ed31368b27f48f845bdd78be58048d0cdbcfd3ee` |
| `worktree:docs/task-evidence/c-omp-declipping/report.json` | `eb1e7213fd6abc95d9cc491531e3114d2fe92233f34e9f41280dcbf8c2a6e77e` |
| `worktree:docs/task-evidence/linear-interpolation-declipping/README.md` | `ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d` |
| `worktree:docs/task-evidence/linear-interpolation-declipping/report.json` | `c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310` |
<!-- digest-table: end -->

## Sibling evidence (separate, not attributed)

The merged `band-limited-pocs-declipping`, `linear-interpolation-declipping` and
`c-omp-declipping` packages are separate controls with their own fixtures and
claims. The C-OMP package also records MATLAB/LTFAT/CVX absence, but its
material is not pooled or reused here. None of them reproduces the toolbox.

## Exact blockers and reopening conditions

This package does **not** close the conditional adapter or the C-OMP
comparison. Reopen only when all of the following are supplied and
independently reviewable:

1. An exact `declipping2020_codes` checkout at a full 40-hex revision with a
   per-file SHA-256 manifest, a toolbox version and a source licence.
2. A licensed MATLAB installation at an exact release on a recorded platform,
   plus LTFAT at an exact revision and the optional CVX path for the C-OMP
   comparison, with a complete environment manifest.
3. One documented typical CLI/API use with exact configuration and expected
   numeric output, including an explicit behaviour when CVX is not selected.
4. An isolated adapter prototype that passes malformed, missing, invalid and
   nonfinite rejection before any audio is processed.
5. Cleared toolbox, MATLAB, LTFAT, CVX, source-audio, clean-reference,
   output-use and redistribution rights with notices.
6. An approved exact-runtime output and a frozen parity vector.
7. Evidence-class separation: compile/build, synthetic runtime and measured
   workload support reported as distinct outcomes.
8. An explicit opt-in adapter and public-surface decision, independent
   exact-head review and release approval; the component remains off by
   default.

No result in this package qualifies the candidate. No provider, processor,
descriptor, registry, installed v0 path, default, shared build, CI, board or
handoff is changed. No merge, formal approval or release action is taken.
