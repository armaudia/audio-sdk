<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FINDSYLLS — source-absent Rate-profile blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `findsylls` (`component_id=findsylls`). The acceptance profile is
**Rate**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact `findsylls` source tree, immutable revision, LICENSE text, dependency
lock, entrypoint, output schema, runtime and reference output are **absent**.
The only pinned record is a research note that names
`https://github.com/hjvm/findsylls` as an **MIT**, Python, **offline-only**
syllable segmentation/embedding toolkit for evaluation, says **“use for
evaluation”**, and states that **no local build or benchmark of findsylls was
made**. Nothing was downloaded, copied, vendored, imported, executed or
fabricated as the candidate.

This package applies the Rate profile to a bounded, deterministic,
stdlib-only **synthetic Q15 frame-energy surrogate** and an exact integer
syllable-nuclei proxy. It is **not findsylls**: it reads no audio, no corpus, no
candidate source, no model and no runtime; it renders no output; it measures no
duration, pitch, transient audibility, playback buffering, device clock,
listening, benchmark or release result. There is **no candidate result** and no
gate is closed.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=findsylls`) is `considered`,
`disposition=sdk-reference`, `verification_profile=rate`. Its only evidence link
is `cpp-library/pipeline-validation/playback-speed-candidates.md`, line 885:

> | Offline syllable ground truth | **findsylls** | MIT | Python toolkit for
> syllable segmentation/embedding | Offline only; use for evaluation |

The same pinned note names the URL at line 1043 and states at line 790 that
there was “No local build or benchmark of … findsylls.” Consequently:

- no checkout exists at `data/checkouts/findsylls`, and no source tree,
  entrypoint, module inventory or immutable commit is staged;
- no byte count or SHA-256 identifies the implementation, LICENSE, dependency
  lock or any model/feature artifact;
- no MIT LICENSE text, attribution notice, citation, `requirements` lock,
  Python version constraint, optional dependency map or installer is staged;
- no syllable definition, frame/hop, boundary convention, language scope,
  confidence field, output schema or API/CLI contract is documented;
- the candidate is offline whole-utterance only; no mapping onto the installed
  v0 16 kHz mono `float32` 160-sample contract exists;
- no rights-cleared speech corpus, independent audited syllable annotation,
  reference output, permitted listening, renderer, rate output or target-device
  timing exists.

The four exact blockers are recorded verbatim in
`contract.json:exact_blockers` and `report.json:exact_blockers`. All **eight**
release gates are `blocked`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-FINDSYLLS`, `7a8d801e48ccf42da20c48dae3b0bbe6e1766e24` |
| Task mode | `feasibility` |
| Acceptance profile | `rate` |
| Decision | `DEFER` before `processor_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate geometry | not documented; offline whole-utterance Python toolkit |
| Candidate artifacts | absent; no source, LICENSE, lock, entrypoint or runtime |
| Candidate rights | recorded `MIT` only; no licence text or written scope decision |
| Surrogate | frozen synthetic Q15 frame-energy nuclei proxy |
| Surrogate clock | `fixture-monotonic-not-device`; sample coordinates only |
| Provider registration, default, ABI, CI | none |

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`source_tree_vendored=false`, `source_tree_downloaded=false`,
`source_tree_imported=false`, `source_tree_executed=false`,
`dependency_installed=false`, `sdk_data_dir_added=false`. Only this task-local
directory is added. The board is referenced by stable linked-row identity only
(`tasks[id=SDK-FINDSYLLS]`, stable-field digest); the mutable full
`plan/swarm/TASKS.json` is never hashed or pinned.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json:rate_profile.requirements` and checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic only | Exact integer `floor(source_samples * denominator / numerator)` with recorded remainder |
| Duration | synthetic only | Target duration arithmetic only; `duration_measured=false` |
| Pitch | blocked | No renderer and no pitch analysis |
| Transient audibility | blocked | No renderer, analysis or listening |
| Playback buffering | fixture accounting only | Source/output slot counts and final partial slots; no device queue or deadline |
| 1× and rate changes | synthetic only | `1/1`, `4/5`, `5/4` target-duration cases |
| Unfamiliar speech | synthetic only | Different seed and faster synthetic envelope; not a real speaker |
| Music | synthetic only | Periodic non-speech energy control |
| Silence | synthetic only | All-zero control with undefined nuclei rate |
| Rebuffer | fixture accounting only | One deterministic zeroed gap and queue counts |
| Drift | synthetic only | A level shift across frames, explicitly not a clock drift |
| Final partial window | synthetic only | `64,037` source samples, `37` final partial samples, exact output partials |
| Pause/filler decisions | not applicable | No decision is made; intervals stay source-sample anchored |
| Speech preservation | blocked | No real speech, renderer, intelligibility measure or listening |
| Listening | not run | No listener, protocol or permitted audio |
| Device timing | blocked | All coordinates are fixture sample coordinates |
| Benchmark | blocked | No benchmark, workload, corpus or target runtime was run |

Seven frozen conditions have three rate cases each: **21 synthetic cases**.
The source window is `64,000` samples (`400` slots) except
`tail_partial=64,037` (`401` slots with a `37`-sample final slot). Every case
records exact source and output intervals, remainders, partial coordinates,
nuclei-proxy count and milli-per-second density (undefined for silence), and
explicitly unmeasured metric fields. Counts are synthetic proxies, not
transcripts, corpus labels or preferred-speed targets.

## Controls and adverse cases

- `controls.identity_echo_exact`: `1/1` maps every source interval to itself.
  Its zero error is trivial by construction and is labelled as such.
- `controls.target_duration_exact`: every computed target equals its exact
  integer target for all 21 cases.
- `controls.constant_count_control`: a frozen constant count of `20` over
  speech-like conditions, with per-condition absolute errors recorded. It is not
  a reproduction of any research baseline.
- `controls.silence_zero_nuclei`: the all-zero control yields zero nuclei and an
  undefined rate.
- `controls.nonzero_mapping_remainders`: only the `tail_partial` rate cases have
  nonzero remainders (`4/5 -> 1`, `5/4 -> 3`); nothing is silently rounded away.
- `adverse.config_cases`: missing, non-object, missing/extra field, 8 kHz,
  stereo, `i16`, 256-sample frame, wrong window, unknown condition, unsupported
  or zero rate terms, boolean/negative epoch, negative first position,
  nonfinite/string threshold, zero/oversized source and no surrogate opt-in are
  rejected before processing with stable reason codes.
- `adverse.slot_cases`: missing, non-object, empty, short, long, boolean, string,
  float, negative, out-of-range and nonfinite slots, stale/boolean/negative
  epoch, unknown condition and wrong condition length are rejected with
  `processed_slots=0` and `state_unchanged=true`. One valid synthetic control is
  accepted.
- `adverse.artifact_cases`: an absent source tree is `blocked`; present metadata
  is validated for identity and geometry only; malformed format, commit, hash,
  licence, rate, channel, frame, mode, missing or extra fields are rejected.
- `use_scope_cases`: only `research_evaluation` is accepted here; commercial
  product, redistribution, public playback and customer deployment are rejected
  with `license_scope_not_permitted`.
- Missing source, licence, runtime, rights, ground truth and reference output
  are `blocked`, never passes. Nonfinite input is never counted as silence.

The caller-supplied source-artifact contract
`audio-sdk/findsylls/caller-supplied-source/0.1` is metadata only. It requires
`artifact_format`, `channels`, `entrypoint`, `frame_samples`, `license_id`,
`license_sha256`, `operating_mode`, `python_requires`, `repository`,
`requirements_lock_sha256`, `sample_rate_hz`, `source_commit` and
`source_sha256`. Absent artifacts are rejected before processing; present
artifacts would only be identity/geometry-validated, never imported or executed.
A hash-shaped synthetic metadata control proves the admission branch and has
`qualification_effect=none`.

## Separation from sibling evidence

The merged `sylnet`, `psola-praat`, `granular-tsm`, `ola-sola`, `soundtouch` and
`usc-mrate` packages are separate syllable/rate references with their own
assets, fixtures, metrics and dispositions. This package does not import, pool,
score or reuse their source, fixtures, metrics or results. Their README/report
files are pinned only as read-only boundary references.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, Rate application, controls, pins, gates. |
| `reference.py` | Strict parsers, frozen Q15 fixture, integer nuclei proxy, exact rate mapping, report and contract builders. |
| `run.py` | Builds every generated artifact three times, requires byte identity, writes the package. |
| `report.json` | Canonical machine-readable Rate report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only strict-JSON, pin, digest, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest below is
checked by `SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Candidate row, offline-only finding, URL and MIT label. |
| `source:research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | Sibling TSM/rate scope; provenance only. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence and component tracks. |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Installed v0 geometry and boundary. |
| `source:audio-benchmark-platform/audio-sdk/README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | SDK build and verification entry. |
| `source:audio-benchmark-platform/audio-sdk/RELEASING.md` | `67e996fc8b1e4bc3e1e90b6bf8e60a98287a9f64177eda2c409f15187a9c65d3` | Release policy boundary. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract. |
| `worktree:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | Licensing metadata. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Installed provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Installed session facade. |
| `worktree:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI entry. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Apache-2.0 text. |
| `worktree:docs/task-evidence/sylnet/README.md` | `cbc7794abb6550783a03c6a70bc013d69e157bdd2a222d1ea1b905758726220c` | Sibling syllable/rate boundary only. |
| `worktree:docs/task-evidence/sylnet/report.json` | `b81b1cd8691528f4cd492deaced8a589309048cdca54ab256c7cb0926bd32331` | Sibling syllable/rate boundary only. |
| `worktree:docs/task-evidence/psola-praat/report.json` | `c8126e10ec682b6960bc379a2d5a5db9222abedcd37b6fe62d176c47e07de614` | Sibling rate boundary only. |
| `worktree:docs/task-evidence/granular-tsm/report.json` | `3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138` | Sibling rate boundary only. |
| `worktree:docs/task-evidence/ola-sola/report.json` | `90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93` | Sibling rate boundary only. |
| `worktree:docs/task-evidence/soundtouch/report.json` | `83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947` | Sibling rate boundary only. |
| `worktree:docs/task-evidence/usc-mrate/report.json` | `d74c03b0e93c9e6c729fb5f10d17dc253e828dfade2579b9e3b586b11c02f246` | Sibling rate boundary only. |

## Canonical artifacts and local digests

`report.json` is canonical JSON (`sort_keys`, minimal separators, ASCII, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself. The table below
is refreshed by `run.py --all` and checked by `verify.py`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `a4f1194723934f837bb78fbd089f5cf9215cdc47265f66a449dcadc541c3e13a` | 64311 |
| `report.json` | `7981a84f50f53244e210ef51e52e7894d9cbad5b8617a206568605f5a6f4ea27` | 55253 |
| `report.json.sha256` | `3f895918e5ea0eef8c43cc9d5bcc1909fb18f50e9b1965e806417bda8102d017` | 78 |
| `run.py` | `312661644169a8c1ad4400e61fac44b2369f7480dca387ad37df77cca2738af5` | 7930 |
| `test_reference.py` | `cfcdb5ff54866364dd32c40e94a217195aa788200e14b2a1a9a7be09f7c19813` | 18124 |
| `verify.py` | `0dba369da5dc77cd268214a2e205aa1d4ca8883224ffd3e6fad74a7ae7872d66` | 22123 |
<!-- DIGEST_TABLE_END -->

## Reproduce

Run from this directory with the pinned interpreter and no bytecode:

```sh
TASK=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FINDSYLLS/docs/task-evidence/findsylls
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --all
PYTHONDONTWRITEBYTECODE=1 $PY run.py --check
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-FINDSYLLS diff --check
```

`run.py` builds all generated payloads three times in one process and refuses
to write unless they are byte-identical. `verify.py` additionally performs
three cold-start digest runs and checks that the files were not mutated.

## Remaining gates (all blocked, eight total)

1. `exact_upstream_source_and_license`
2. `isolated_runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `syllable_ground_truth_quality`
6. `rate_profile_qualification`
7. `target_runtime_timing_and_memory`
8. `provider_intake_and_default_selection`

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Replace the absent, unpinned, rights-uncleared record with
an exact caller-supplied findsylls source tree at an immutable revision, with
MIT LICENSE text, dependency lock, entrypoint, API/output schema and recorded
digests; admit an isolated hash-pinned offline runtime; validate identity and
geometry without import until a reviewed run; clear the evaluation,
redistribution, product-use and generated-output scopes in writing; reproduce
approved outputs across three cold starts; measure syllable-ground-truth quality
on a rights-cleared audited cohort; and measure the full Rate profile, target
timing and memory. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.
