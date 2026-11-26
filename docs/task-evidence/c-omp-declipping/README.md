<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-C-OMP-DECLIPPING — C-OMP declipping blocker

**Disposition: `DEFER` / `incomplete` / `not_qualified`.** This package is a
bounded, deterministic **research-control and blocker package** for inventory
component `c-omp-declipping` (Restoration, verification profile `restoration`).
The exact licensed `declipping2020_codes` source, a resolved toolbox revision,
the MATLAB runtime, LTFAT, CVX, the documented C-OMP experiment, its expected
numeric output, rights record, paired clipped/clean cohort and parity vector are
absent. It creates **no new execution, toolbox, corpus, real audio, provider,
processor, ABI, default, build, CI, board, handoff or release change**.

Task owner: `agent-C-OMP-DECLIPPING`; reviewer: `reviewer-C-OMP-DECLIPPING`.
Claim base: audio-sdk `c399af9eded97f44c19c512433640589277e9017`; branch
`swarm/SDK-C-OMP-DECLIPPING`. The task depends on `SDK-FND-AUDIT` and
`SDK-FND-EVIDENCE`; write scope is the task-local evidence directory only
(`docs/task-evidence/c-omp-declipping/`).

## What is missing and why no result can qualify

The merged research document `research/distortion_restoration_20261028.md`
(RST-01, declipping/saturation) records the only C-OMP provenance:

> The established next comparison is a constrained sparse declipper such as
> SPADE or social sparsity. The authors’ open MATLAB toolbox evaluates many
> sparse/constrained methods, but requires MATLAB, LTFAT and (for C-OMP) CVX,
> so it was not runnable in the current Python pilot.

It records the authors’ project page `https://rajmic.github.io/declipping2020/`
and repository `https://github.com/rajmic/declipping2020_codes`. It does **not**
record a resolved commit, a toolbox licence, a C-OMP experiment configuration,
a numeric C-OMP row or a local output. The paired synthetic screen
`reports/distortion-restoration/20261028-synthetic-screen.json` contains only
`clipped_input`, `linear_interpolation` and `bandlimited_POCS` methods for
RST-01; there is no C-OMP method row.

No fixed path in this workspace contains a `declipping2020_codes` checkout, a
40-hex toolbox revision, a MATLAB installation, LTFAT, CVX, an environment
manifest, a documented C-OMP experiment, an expected output, a licence record,
a rights record, a paired cohort or a parity vector. Nothing is downloaded,
vendored or inferred from the recorded URLs. Consequently:

- source/toolbox identity, hashes and licence terms cannot be pinned;
- MATLAB is a proprietary runtime and neither LTFAT nor CVX is present; no
  licensed, isolated environment can be admitted;
- the C-OMP experiment geometry — dictionary/frame, window and hop, block
  length, clipping threshold and exact mask policy, sparsity/target
  cardinality, stopping tolerance, iteration cap, regularization and output
  interval mapping — is not recorded;
- no candidate output exists, so no SI-SDR, RMSE, STOI, WER, MOS, latency,
  memory, RTF or listening value is reported;
- missing evidence is never promoted to a pass, partial qualification or
  capability claim.

C-OMP is a sparse declipping research control in the `RST-01` family. It is
**not** an SDK processor, streaming provider, validated product default or
completed comparison. The merged band-limited POCS and linear-interpolation
packages are separate controls and are not attributed to this candidate.

## Evidence classes and boundaries

- **Merged research metadata:** the RST-01 boundary, the C-OMP toolbox
  dependency statement, the project and repository URLs, and the paired pilot
  source. These are provenance, not local C-OMP execution.
- **Merged sibling packages:** `band-limited-pocs-declipping` and
  `linear-interpolation-declipping` are separate deterministic controls on
  frozen synthetic data. Both list C-OMP parity as not run; their fixtures,
  metrics and results are not pooled or reused here.
- **Synthetic accounting:** the task-local control generates deterministic
  binary32 PCM at 16 kHz mono, applies exact binary32 hard clipping at
  thresholds `0.35` and `0.55`, derives the exact mask by equality with the
  quantized threshold, and checks unmasked-sample preservation, exact
  occupancy, exact half-open mask intervals, duration conservation and
  finite/peak bounds. It performs **no sparse recovery, interpolation,
  MATLAB/LTFAT/CVX invocation or declipping**; the clipped input is a damaged
  baseline, not candidate output.
- **Not present:** real paired speech, a frozen C-OMP experiment, toolbox
  source, runtime invocation, clean-reference quality, human listening,
  device timing, public benchmark or release approval.

The failure envelope is explicit: a known clipping mask does not prove peak
recovery; a duration-conserving clipped baseline does not prove restoration;
and the absent source/runtime/experiment means neither parity nor suitability
can be evaluated.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `exact_source_and_asset_identity` | Full 40-hex source/toolbox revisions, MATLAB/LTFAT/CVX identity, experiment config and metadata hashes, and source licence match exact pins | blocked |
| `runtime_admission` | Isolated, licensed MATLAB/LTFAT/CVX runtime with a complete environment manifest on a recorded platform | blocked |
| `artifact_rights_and_licence` | Source, MATLAB, LTFAT, CVX, source-audio, clean-reference, output-use and redistribution rights cleared with notices | blocked |
| `exact_reference_parity` | Approved exact-runtime C-OMP output matches the documented reference experiment on a frozen input and config | blocked |
| `restoration_cohort_and_scoring` | Rights-cleared held-out cohort stratifies threshold, occupancy and bandwidth and scores quality, peaks and preservation separately | blocked |
| `task_scope_and_geometry` | Rates, block length, dictionary, padding, delay and validity intervals established without overclaiming a streaming processor | blocked |
| `opt_in_processor_intake` | Explicit opt-in intake, licence review, descriptor review and independent public-surface decision; optional only | blocked |
| `public_default_and_release` | Explicit default selection, resource/deadline evidence and release or benchmark approval; off by default | blocked |

The eight exact blockers in `report.json` name the concrete artifact or rights
requirement: absent source checkout, unpinned upstream revision, absent
MATLAB/LTFAT/CVX runtime, absent documented reference experiment, unestablished
geometry, unverified source/dependency rights, uncleared rights/cohort, and
absent parity/benchmark evidence. All seven `restoration` profile requirements
are unsatisfied for qualification; four are explicitly synthetic-only or
structural-only, and none has a qualification effect.

## Caller-supplied asset contract

`reference.py` validates a future caller-owned asset manifest without importing
or executing anything. It requires absolute paths and lowercase SHA-256 values
for the experiment config, licence record, rights record, reference experiment,
cohort manifest, parity vector and output-use grant; full 40-hex source, LTFAT
and CVX revisions; a nonempty MATLAB version; exactly 16 kHz mono; a block size
between 160 and 65,536 samples aligned to the 160-sample SDK frame; and the
declared `offline_block_constrained_omp_declipping` variant. Any missing,
malformed, nonfinite, out-of-range, mismatched or unapproved variant is
rejected before processing. No upstream revision is pinned because the merged
evidence records only project and repository URLs; a shape-valid manifest
cannot manufacture qualification.

## Restoration-profile reporting

The package reports the restoration profile but qualifies none of it:

- frozen corruption and metadata are synthetic-only (two thresholds and exact
  masks on one deterministic signal);
- the clipped-input damaged baseline is present only as an accounting anchor;
- there is no matched sparse/POCS comparison run here;
- threshold/occupancy strata are synthetic-only and not a real-speech cohort;
- discrete validity and exact mask intervals are synthetic-only;
- task-specific quality is not measured;
- output peak/duration bounds are structural-only;
- missing, invalid, nonfinite and adverse control results are recorded.

No quality, listening, timing, benchmark or real-speech result is claimed.

## Synthetic control (not C-OMP)

The control uses 16,000 samples (1.0 s) at 16 kHz mono, exactly 62,500 ns per
sample. Clean samples are deterministic binary32 triangle/LCG values with a
declared peak bound of 0.90. Hard clipping is symmetric at the binary32
quantization of each threshold; the mask is exact equality with that threshold.
A quiet no-clip case at threshold 0.55 has zero occupancy.

Every case reports exact occupancy, mask interval count, clean/clipped digests,
finite peak bounds and `candidate_output=false`. The frozen observations are:

| Case | Threshold | Clipped samples | Occupancy | Mask runs | Peak in → clipped |
| --- | ---: | ---: | ---: | ---: | ---: |
| `clipped_0_35` | 0.35 | 5,996 / 16,000 | 37.4750% | 594 | 0.9000 → 0.3500 |
| `clipped_0_55` | 0.55 | 2,374 / 16,000 | 14.8375% | 371 | 0.9000 → 0.5500 |
| `quiet_no_clip_0_55` | 0.55 | 0 / 16,000 | 0% | 0 | 0.1800 → 0.1800 |

The control never computes a declipped sample, SI-SDR, RMSE, STOI or a
listening score. All eight `acceptance_outcomes` are `measured=false` with
`value=null`.

## Adverse, missing and invalid handling

`report.json` records every rejection with its reason and unchanged state:
empty/non-sequence/`None` PCM, wrong rate, stereo, `NaN`/`±Inf`, out-of-range,
boolean/string samples, missing/extra config fields, threshold 0/1/negative/
above-one/nonfinite/boolean/string, duplicate JSON keys, nonfinite JSON
constants, and caller manifests with missing/extra fields, relative paths, bad
hashes, short/nonhex source/LTFAT/CVX revisions, empty MATLAB version, wrong
variant/rate/channels, too-small/misaligned block, missing asset, missing
directory or hash mismatch. Missing real recordings, toolbox source, runtime,
experiment, quality and labels are `blocked`, never passes.

## Files and reproduction

- `reference.py` — strict JSON, stable linked-row identity, fixed-path
  source/toolbox/runtime audit, caller manifest validation, exact binary32
  clipping-mask accounting and 41 adverse controls.
- `contract.json` — machine-readable `decision="DEFER"`, `incomplete`,
  proposal-only status, `qualification.status="not_qualified"`, eight blocked
  gates, eight exact blockers, runtime requirements and caller asset contract.
- `report.json` + `report.json.sha256` — canonical report and digest.
- `SOURCES.sha256` — pins for read-only source documents, SDK contract files,
  sibling controls and package files. The mutable full
  `plan/swarm/TASKS.json` is **never hashed**; only the stable linked-row
  fields are projected to a digest.
- `run.py` — three byte-identical in-process regenerations before writing.
- `test_reference.py` — deterministic unittest checks; no skips or network.
- `verify.py` — strict JSON, exact pins, licensing, task-local git scope and
  three cold-start regeneration checks.

```sh
cd docs/task-evidence/c-omp-declipping
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

JSON, digest and manifest files have SPDX `Apache-2.0` sidecars. All files are
inside this task directory; board, handoff and reviewers were not changed or
dispatched. No merge, formal approval or release action is taken. Workspace
pins are SHA-256 values of read-only documents; a pin grants no rights and
verifies no media. `SOURCE_ROOT` can point to the enclosing `audioml` checkout
if automatic discovery is unavailable.

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row is
machine-checked by `verify.py` and by the test suite.

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

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:docs/task-evidence/band-limited-pocs-declipping/README.md` | `8e6bfec06db0b02321d6b6313536cf4a438204680d28240c15c9f57189dcdc65` |
| `sdk:docs/task-evidence/band-limited-pocs-declipping/report.json` | `8d893e8055cdc2e982a4e568e7996b45d1b6dd73841ac2b701a15ec5160dc65b` |
| `sdk:docs/task-evidence/linear-interpolation-declipping/README.md` | `ab68e2a7b000f5b73e26e97e0ebb95c45ff15e1db2922d26365ac96466758a6d` |
| `sdk:docs/task-evidence/linear-interpolation-declipping/report.json` | `c3252fd080299e4b1804a9facf3fea02fe66f0df31728426476346f28d8dc310` |
<!-- digest-table: end -->

## Exact blockers and reopening conditions

This package does **not** close the conditional implementation or the comparison.
Reopen only when all of the following are supplied and independently reviewable:

1. An exact `declipping2020_codes` source checkout at a full 40-hex revision,
   with per-file SHA-256 values and a source licence.
2. A licensed MATLAB runtime plus LTFAT and CVX at exact revisions, with a
   complete environment manifest and recorded platform.
3. The exact documented C-OMP experiment: dictionary/frame, window/hop, block
   length, threshold/mask policy, sparsity, tolerance, iteration cap,
   regularization and expected numeric output.
4. A pinned task geometry: 16 kHz mono proceeds to the block layer, with exact
   output intervals, padding, content delay and reset behavior.
5. A rights-cleared paired clipped/clean speech cohort with threshold and
   occupancy strata, plus authorized output-use and redistribution terms.
6. One approved exact-runtime C-OMP output and a frozen parity vector.
7. Task-specific quality, peak, alignment, nonfinite, timing and listening
   evidence as permitted.
8. An explicit opt-in processor/public-surface decision, independent exact-head
   review and release approval; the component remains off by default.

No result in this package qualifies the candidate. No provider, processor,
descriptor, registry, installed v0 path, default, shared build, CI, board or
handoff is changed. No merge, formal approval or release action is taken.
