<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CCF-AATC-UNIFIED-RESTORATION-CONTROLS — registration/pairing blocker

`audio-sdk/ccf-aatc-unified-restoration-controls/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **8** |
| Open exact blockers | **6** |
| Profile | Evidence (`plan/swarm/VERIFICATION.md`) |
| Mode | research-control |
| Pinned base | `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |

This directory is a bounded, task-local blocker package for the **CCF AATC 2025
Speech Restoration Challenge** as a unified, multi-distortion restoration
benchmark. It is **not** an implementation, adapter, provider, benchmark,
submission or release. It records why the candidate cannot be qualified from
the artifacts that are actually present, and it reproduces only declared
degradation arithmetic and deterministic schema controls. Nothing here may be
promoted to a runtime, quality or unified-score claim.

## Why DEFER

The pinned research note names the challenge as the relevant next benchmark for
learned unified restoration models. It records exactly one hard access fact:
the training/dev data **requires participant registration** and is far larger
than the local pilot. It does not contain the registration terms, the dataset
license, a split manifest, the organizer-permitted multi-distortion pairing
list, the official baseline, the scorer, the submission format or any
reference output.

No participant acceptance, agreement, account, dataset split, pairing
specification, baseline package, scorer, submission schema or reference output
exists in the project workspace. The note's own limits section says the neural
and codec-integrated candidates were researched but not run and that a real
decision needs registered paired material, a codec suite, realistic loss
traces, a held-out speaker split, task-appropriate metrics and blinded
listening. Nothing was downloaded, requested, reconstructed or fabricated.
Supplying the missing artifacts and rights reopens the task; absence of a result
is the correct outcome.

## Challenge registration

Registration is **participant-specific and organizer-controlled**. It is not a
public download and it is not implied by naming the challenge. This package
records only that the requirement is documented in the pinned note:

- `records_registration_required=true`;
- registration was **not attempted**;
- no participant account, acceptance record, agreement, credential or dataset
  grant is present;
- no dataset, baseline, scorer or submission package is present or copied;
- no network client, portal call or download was made.

`required_artifacts` A01–A03 and gates RG-01/RG-02 remain blocked until the
organizer acceptance, the executed agreement, the immutable dataset identity and
the written license terms are supplied and reviewed.

## Multi-distortion pairs

The note divides the area into four different inverse problems. They are not
interchangeable: a limiter cannot recover clipped peaks, resampling cannot infer
missing high frequencies, and packet concealment benefits from codec state or
redundant packets. A single "distortion restoration" score hides those
differences.

| Family | Controlled degradation (note) | Required context | Forbidden substitution |
| --- | --- | --- | --- |
| RST-01 declipping/saturation | hard clipping at 0.35 and 0.55 of normalized peak | clean reference plus threshold or mask | resampling, rate conversion or a limiter cannot recover clipped peaks |
| RST-02 bandwidth extension | zero-phase low-pass at 3.5 kHz | full-band clean reference | resampling or rate conversion does not infer missing high frequencies |
| RST-03 codec artifacts | 8-bit µ-law at 8 kHz and a 4-bit stress proxy | pre-companding narrowband reference and codec identity | a generic PCM postfilter cannot claim codec-integrated restoration |
| RST-04 packet loss | isolated 10% and 17% burst loss | loss mask plus decoder state or redundancy | waveform inpainting cannot substitute for codec-integrated PLC/DRED |

The task-local `synthetic_pairing_envelope` enumerates four single-distortion
controls and the six unordered pairs among the four families **only** to
exercise canonicalization, deduplication and fail-closed admission. It sets
`organizer_permitted=0`, `permitted_for_qualification=false` and
`qualifies=false`. It is not an organizer rule and does not permit any
combination. The official pairing list (RG-03 / BLK-03) must be supplied with an
exact digest and pinned before a unified benchmark.

## What is reproduced

All controls are stdlib-only, integer/rational, labelled
`synthetic_contract_control_not_evidence` and `qualifies=false`.

- `family_control` routes 18 claims across the four families, accepts the four
  family-correct claims and rejects 14 substitutions or malformed claims with
  exact codes (`cross_family_substitution`, `decoder_context_required`,
  `unified_claim_requires_strata`, …).
- `degradation_control` reproduces the declared parameters exactly: clipping
  `7/20` and `11/20`, low-pass fraction `7/32` at 3500/16000 Hz, µ-law levels
  `256`/`16`, loss rates `1/10` and `17/100`, and rejects out-of-range,
  nonfinite and boolean inputs.
- `pair_control` canonicalizes unordered pairs, rejects self-pairs, triples,
  duplicate pairs and malformed families, and proves the synthetic table permits
  nothing.
- `aggregation_control` computes exact per-stratum means and **refuses** any
  unified score. A unified aggregate is `forbidden` with reason
  `organizer_pairing_list_absent`; missing strata, unknown metrics, duplicate
  rows, nonfinite values and pair/family mismatches are rejected.
- `admission` validates a caller-authored qualification manifest (registration,
  dataset, pairing, baseline, four strata, controls, rights, device). All 37
  mutations are rejected with exact codes and no state advance. The base
  manifest is only a **schema control**: `schema_valid=true`, `admitted=false`,
  `qualifies=false`.

No audio is synthesized, read, rendered or played. No challenge runtime,
dataset, baseline, scorer or model is imported or executed.

## Exact blockers

| ID | Missing artifact | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Accepted participant registration and executed agreement | Organizer acceptance, participant/team identity and reviewed agreement digest. |
| `BLK-02` | Licensed train/dev/test dataset | Immutable version, every split file list and full SHA-256, dataset licence and written execution/publication terms. |
| `BLK-03` | Organizer permitted multi-distortion pairing list | Official pair set, corruption parameters, forbidden combinations and exact digest, pinned before a unified run. |
| `BLK-04` | Official baseline, scorer and submission package | Package/scorer SHA-256, metric implementation and weights, submission schema and reference outputs. |
| `BLK-05` | Frozen matched cohorts and rights-cleared scoring | Clean/degraded references, metadata and masks, held-out speakers, failed items, consent/output use and approved listening or predictive scoring. |
| `BLK-06` | Measured Evidence profile, device timing and release review | Evidence-class separation, failed/adverse cases, target-device timing/resources, opt-in adapter with OFF default, independent review and release approval. |

The ten required artifacts are enumerated in `report.json` under
`required_artifacts`; all are `blocked`, none is present. The eight blocked
release gates (`RG-01`–`RG-08`) are enumerated under `gates`; every gate is
`blocked` and `qualifies=false`.

## What is pinned

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml` unless marked
as SDK-worktree relative. Verification is by exact SHA-256; a missing pinned
file is a failure, not a skip.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `research/distortion_restoration_20261028.md` | `8371790cdb2b25a5ef55f07d8a52bc74850522d5e30968c34984c754af95cb71` | Four-family boundary, declared degradation parameters, pilot results, no universal model, challenge registration requirement and limits. |
| `src/audioml_eval/distortion_restoration.py` | `c99b85e619fecd86eef5963c3e7b2720ddb5f61fd13d5d1ac7bd5d6841a6792f` | Normative local classical per-task baselines; not a challenge baseline or unified restorer. |
| `reports/distortion-restoration/20261028-synthetic-screen.json` | `87df91e30905ead24786146b8e82257b7132cd5cd51bcee46570955eff826ece` | Source-reported 12-clip synthetic screen; provenance only, not reproduced. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component row `ccf-aatc-unified-restoration-controls`; Evidence profile; research-control disposition. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Evidence acceptance profile. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK plan and task-local evidence boundary. |

The unchanged public boundary is pinned separately: `CONTRACTS.md`,
`api/include/audio_sdk/provider_v0.h`, `api/include/audio_sdk/session_v0.h`,
`CMakeLists.txt`, `REUSE.toml`, `.github/workflows/ci.yml` and `README.md`.

Merged sibling evidence is pinned under `docs/task-evidence/`: the four
`survey-rst-*` maps, both declipping references, the four PLC controls, standard
Opus 1.4 decoder PLC, Opus deep PLC, DRED, LACE and NoLACE. Exact values are in
`SOURCES.sha256` and `report.json`. Those packages are per-family controls or
blockers; none is a unified restorer or a challenge submission.

The mutable full `plan/swarm/TASKS.json` is **never hashed**. Only the stable
linked-row projection (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`, `evidence`) is read; board status, claim and review fields gate
nothing.

## Reproduce

From this directory, with Python 3.11+ and the standard library only:

```sh
export PYTHONDONTWRITEBYTECODE=1
python3 run.py all
python3 -m unittest -v test_reference.py
python3 verify.py
```

`run.py all` regenerates `contract.json`, `report.json`,
`report.json.sha256` and `SOURCES.sha256` three times and requires
byte-identical results. `verify.py` re-checks the Evidence profile, every exact
pin, strict canonical JSON, all controls, eight blocked gates, six open
blockers, ten blocked artifacts, licensing/task-local git scope and three
cold-start regenerations. No network, challenge portal, dataset, baseline,
runtime, audio file or device is used.

Committed report: `report.json` (one line, LF), SHA-256
`f4fdf76f47c3255adb657f92d5981913083cdbee769c8dd6eb0ede42f91ebcdf`.

## Files

| File | Role |
| --- | --- |
| `reference.py` | Deterministic family/pair/degradation/aggregation controls, manifest admission, pins, contract/report builders. |
| `run.py` | Three-repeat canonical regeneration. |
| `contract.json` | Canonical task contract and pins. |
| `report.json` | Canonical machine-readable DEFER report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `SOURCES.sha256` | SHA-256 pins for all source, boundary, sibling and local files. |
| `test_reference.py` | Standard-library test suite. |
| `verify.py` | Read-only package verifier. |
| `*.license` | REUSE/SPDX sidecars for JSON artifacts. |

## Non-claims

- No result in this package is a qualification, benchmark, submission or
  release.
- No CCF AATC registration was attempted, accepted or implied; no participant
  account, agreement, credential or data grant exists.
- No challenge dataset, split, license text, baseline, scorer, submission
  package or reference output was downloaded, read or copied.
- The four local classical screens are per-task synthetic pilots, not a unified
  restorer, not the challenge baseline and not a substitute for registered data.
- The pairing envelope is a synthetic schema control and permits no
  organizer combination.
- No audio was read or played; no reference was rendered; no listening, consent
  or output-use grant exists.
- No SI-SDR, RMSE, STOI, quality, intelligibility, complexity or unified result
  was measured for the challenge.
- No device timing, resource, benchmark, provider or release review was
  performed.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI,
  shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
