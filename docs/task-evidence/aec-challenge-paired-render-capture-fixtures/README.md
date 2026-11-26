<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES — declared-only blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
the Microsoft AEC Challenge paired render/capture fixtures
(`component_id=aec-challenge-paired-render-capture-fixtures`). The acceptance
profile is **Evidence**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`optional_evidence_adapter_exposure`; `evidence_status=incomplete`,
`status=proposal_only_incomplete`, `qualification.status=not_qualified`.
A missing result may never qualify the candidate.

The local pilot **metadata** is present and is parsed strictly: two manifests,
two selection CSVs, a provisional source crosswalk, a rights audit and three
prior aggregate reports. The licensed **audio bytes** and the pinned upstream
`meta.csv` are **absent**, and neither subset has an approved rights record. The
package therefore records the declared partitions, item digests, pair structure
and missing-byte controls, and stops. Nothing is downloaded, copied, vendored,
loaded or executed; no audio byte, model, runtime, scorer, cohort or device is
used. Only this task-local directory is added.

## Exact blocker

| Required artifact | Recorded local state |
| --- | --- |
| 48 declared synthetic WAVs | Declared under `data/tmp/aec-challenge-synthetic-pilot/`; directory absent, 0 of 48 bytes present |
| 108 declared recorded WAVs | Manifest records hashes, frames and durations but **no local audio directory**; 0 of 108 bytes present |
| Pinned upstream `datasets/synthetic/meta.csv` | SHA-256 `6b867aa6…06f3e5` declared; file absent at both documented candidate paths |
| Rights approval (synthetic) | Provisional source-family mapping only; scenario 5561's noise source unidentified |
| Rights approval (recorded) | No participant consent, privacy/publicity or intended-use terms |
| Paired cohort, holdout, scorer, aggregation | None; no representative valid result |
| Optional SDK evidence adapter | Not exposed; DEFER before intake and independent review |

The manifest-declared item digests are recorded exactly as declared and are
**not** re-verified against bytes. No absent artifact is given a fabricated
hash. Prior pilot CSVs are pinned provenance only; they are not re-executed,
adopted or pooled with this package.

## Declared partitions (kept separate)

`fixture_partitions` in `report.json` keeps the two training subsets apart with
independent manifests, ledgers, counts and rights states. No pooling or
cross-subset deduplication is performed or claimed.

| Property | `synthetic_train` | `recorded_train` |
| --- | ---: | ---: |
| Declared scenarios / device groups | 12 | 12 |
| Declared audio items | 48 | 108 |
| Roles per unit | 4 | 9 |
| Declared items present | 0 | 0 |
| Declared items verified | 0 | 0 |
| Declared total | 15,362,072 bytes | 19,547,568 frames / 1221.723 s |
| Declared ledger SHA-256 | `53e8ff69…e46fc1` | `c938c4df…5581f84` |
| Split | `train only; no held-out test rows` | non-blind `datasets/real` train groups |
| Rights | `provisional_source_family_mapping_not_approved` | `not_cleared_no_participant_terms` |

The synthetic subset declares 4 `linear_clean`, 4 `nonlinear_clean` and 4
`farend_noisy` scenarios with SER values −8, −3, +2 and +7 dB in every stratum
and a near-end scale in (0, 1] (declared range 0.5554605135214555 to
0.8347643515788602). Each scenario declares all four roles — far-end reference,
echo component, clean near-end target and microphone capture — and the four
declared byte counts in each scenario are equal (maximum spread 0). The
manifest declares byte counts only: it records **no** sample rate, channel count
or frame count, so its paired declaration cannot be expressed without
inference (recorded as `synthetic_declaration_gap`, code
`unsupported_sample_rate`). The canonical WAV header size (44 bytes) is used
only to describe the declared byte count and is labelled an assumption.

The recorded subset declares 12 GUID groups with nine scenario files each:
`farend_singletalk`, `farend_singletalk_with_movement`, `doubletalk` and
`doubletalk_with_movement` in microphone/loopback pairs, plus
`nearend_singletalk_mic`. Every file declares 16 kHz, mono, a positive frame
count and a duration matching `frames / 16000` within one sample.
`blind_test_data_used=false`, and no declared name contains `blind`.

## Paired length structure (declared, not re-verified)

33 of the 48 declared microphone/loopback pairs have **unequal** frame counts;
the maximum declared delta is **1760 frames (110.0 ms)** and 15 pairs are
declared equal. The research note states that unequal tails were truncated to
the shorter stream at evaluation time. That policy is recorded here as declared
upstream behaviour and is **not** re-executed or verified. No alignment,
resampling or clock-drift result is claimed.

## Evidence profile application

`plan/swarm/VERIFICATION.md` Evidence row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Pin scorer, corpus and cohort | Blocked: no scorer, rights-cleared corpus or frozen cohort |
| Pin aggregation, failed items and controls | Blocked: no aggregation or failed-item policy result |
| Separate evidence kinds | Declared only: synthetic and recorded partitions separated; no paired, unpaired, human or source-reported scoring exists |
| Validate one invalid/missing case | Recorded: the live recorded declaration is rejected with 108/108 bytes missing; 48 adverse metadata cases are rejected without state change |
| Validate one representative valid result | Blocked: no valid item or result exists; the missing half is recorded, never promoted |
| Exact references and rights | Blocked: item digests are declared but unverified; no rights approval |

## Fail-closed admission gate

`reference.admission_decision()` validates a caller-supplied declaration
strictly and can verify caller-owned bytes, but it has **no admitting branch**:

| Situation | Decision |
| --- | --- |
| Declared bytes missing | `DEFER`, `declared_fixture_bytes_unverified` |
| Bytes verified, rights not approved | `DEFER`, `rights_not_approved` |
| Bytes verified and rights cleared | `DEFER`, `no_approved_cohort_or_independent_result` |
| Metadata only | `DEFER`; metadata alone can never qualify |

The live control builds a declaration from the recorded manifest metadata and
finds 108 of 108 declared files missing at the documented root. Unit tests
exercise the byte-verification branch only with caller-owned temporary bytes;
those bytes are never committed, reported as a fixture result or counted as
evidence.

## Declared results (metadata invariants only, not fixture results)

All values are exact `report.json` values. They describe declared metadata, not
audio, not a model and not a release.

| Invariant | Exact value |
| --- | ---: |
| Synthetic declared items / scenarios | 48 / 12 |
| Synthetic strata | 4 / 4 / 4 |
| Synthetic declared bytes | 15,362,072 |
| Synthetic max declared byte spread per scenario | 0 |
| Recorded declared items / groups | 108 / 12 |
| Recorded declared frames | 19,547,568 |
| Recorded declared seconds | 1221.723 |
| Recorded unequal mic/loopback pairs | 33 of 48 |
| Recorded max declared pair delta | 1760 frames / 110.0 ms |
| Declared items present / verified | 0 / 0 of 156 |
| Adverse metadata rejections | 48 of 48 |
| Live missing-byte control | `DEFER`, 108 missing |
| Representative valid result | absent |
| Release gates blocked | 8 of 8 |

No SI-SDR, STOI, ERLE, AECMOS, listening, ASR, device-timing, benchmark or
release result is claimed. No missing or rejected case is promoted.

## Failure controls (exact failures recorded as failures)

- **Synthetic manifest:** uppercase revision, uppercase digest, missing/extra
  field, duplicate name, unknown role, incomplete scenario, zero/odd/bool byte
  count, scenario length spread, non-train split, stale selection digest,
  claimed rights approval, blind-test name, duplicate JSON key, non-finite JSON
  constant and invalid JSON are rejected.
- **Recorded manifest:** blind-test flag, multi-channel, 44.1 kHz, zero frames,
  duration/frame mismatch, incomplete group, unselected group, duplicate name,
  uppercase digest and extra field are rejected.
- **Declarations:** wrong schema, unknown role, subset role mismatch, duplicate
  item/name, zero frames, multi-channel, 8 kHz, non-train split, extra item
  field, blind-test name and incomplete group are rejected.
- **Selections:** bad header, out-of-set SER, unknown condition, out-of-range
  scale, test split, missing row, wrong folder and duplicate group are rejected.
- **Presence:** the build fails closed if a declared fixture byte or documented
  upstream metadata path appears, so this package cannot silently claim absence
  after data is staged.

Every rejection is immutable: the input digest before and after the call is
identical.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Strict manifest/selection parsers, partition ledgers, fail-closed admission gate, controls, report/contract/manifest builders. |
| `run.py` | Builds the report three times, requires byte identity, then regenerates all artifacts. |
| `report.json` | Canonical machine-readable Evidence report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network, no licensed audio. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for generated artifacts and the manifest. |

## Source pins (SHA-256)

`source:` paths are relative to the pinned research workspace root. Every row
is machine-checked by `verify.py` and by the test suite. Only provenance files
that exist are pinned; no absent audio or upstream metadata is given a
fabricated hash.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/aec_research_20261028.md` | `dc733f29c999ed83d9b3a8c14b21df4abd6cfeecd6ba0c3b78e1c6f4d2218180` |
| `source:research/aec_challenge_synthetic_pilot_manifest.json` | `38b6bb4939a254d702d2ab12e95fde641957e1ced2b752eb9fb2dd8b215202b6` |
| `source:research/aec_challenge_real_pilot_manifest.json` | `7fd467330537107873759cdab2b63e59ff0f77e9aca324f8249c7801b109079f` |
| `source:research/aec_challenge_synthetic_pilot_selection.csv` | `f3d69044e8040613fc31ba0e7438e790289a41f1ac2170582a09e38a0c1322a7` |
| `source:research/aec_challenge_real_pilot_selection.csv` | `840caee9487c1480cd9b68bd87a3b36233464e706759465d374372cd0ab19585` |
| `source:realtime-audio-library/research/aec_challenge_rights_audit_20261030.md` | `1f138036f4567b4df173c18ea2dbb7d3c1cc63723e9d0acc6b339dd294b27a0d` |
| `source:realtime-audio-library/research/aec_challenge_synthetic_pilot_source_crosswalk.csv` | `0243ba30936ed62e15ccf157bb128c4eee2615e483708e7559c6d18064f068fa` |
| `source:reports/aec_challenge_synthetic_pilot_20261028.csv` | `f5da248a22a632e7221464c03c2de25386e3c7091ca68c1644f18a34dec39ef5` |
| `source:reports/aec_challenge_real_pilot_20261028.csv` | `32b41d1cab6b6b28a03cb6db164debfb408441822642c2a0c1a9b42b5889aba3` |
| `source:reports/aec_challenge_real_pilot_summary_20261028.csv` | `4784755161aa0fa4027b2b6524f8dd34b7ccc9390ecd785103dda95b65bb27e7` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`sdk:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## External artifact identity

No external artifact is pinned. The repository revision
`8f861f0f8ffca26a3d1d16f17f2594ea89abe7ac` and the upstream metadata digest
`6b867aa68f510e4bafc9ffa05202930ffc1bb54bb0cffe66aa1ec3bcc606f3e5` are
declared provenance only. The 156 WAV SHA-256 values are recorded as declared
by the local manifests and are unverified. `present=false`,
`verified=false`, `rights=not_approved`, `approval_record=null`. If any declared
fixture byte or the upstream metadata appears, this evidence package is stale
and must reopen.

## Reproduce

Run from this directory with the pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES
TASK=$WT/docs/task-evidence/aec-challenge-paired-render-capture-fixtures
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
python3 -m reuse lint
git -C "$WT" diff --check
```

`run.py` builds the report three times in one process and refuses to write
unless all payloads are byte-identical. External reproduction runs `run.py`
three times in fresh processes and compares the resulting bytes.

## Remaining gates (eight blocked)

1. `RG-01` exact verified fixture bytes (48 synthetic + 108 recorded).
2. `RG-02` pinned upstream `meta.csv` and a reproduced source/term crosswalk.
3. `RG-03` participant consent, privacy/publicity and intended-use terms.
4. `RG-04` data-owner approval for retention, evaluation, acceptance and
   redistribution scope.
5. `RG-05` frozen rights-cleared paired cohort with an untouched holdout.
6. `RG-06` pinned scorer, metric protocol, aggregation and failed-item policy.
7. `RG-07` invalid/missing and representative-valid validation at the exact
   head.
8. `RG-08` explicit opt-in evidence-adapter exposure decision and independent
   review.

Each exact requirement is recorded in `contract.json:release_gates` and
`report.json:release_gates`.

**Reopen condition.** Supply the exact fixture bytes and upstream metadata,
reproduce the per-file source/term crosswalk, obtain the participant and
data-owner approvals, freeze a rights-cleared cohort and holdout, pin the
scorer and aggregation, validate a representative result at the exact head and
record an explicit opt-in adapter decision. Until then the candidate stays
**DEFER**, **incomplete** and **not qualified**.

## Boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_added=false`, `sdk_data_dir_added=false`, `asset_bundled=false`,
`weights_vendored=false`, `audio_loaded=false`, `audio_executed=false`,
`network_used=false`. Installed v0 remains 16 kHz, mono, float32, 160 samples
per frame. The board is referenced by stable linked-row identity only
(`tasks[id=SDK-AEC-CHALLENGE-PAIRED-RENDER-CAPTURE-FIXTURES]`, stable-field
digest); the mutable full `plan/swarm/TASKS.json` is never read into, hashed by
or pinned to this package. No provider, descriptor, registry, installed
default, public ABI, shared build or CI is changed.

## Separation from sibling evidence

The paired SpeexDSP/WebRTC AEC3, fixed-RLS/NLMS AEC, LocalVQE echo-only and
WebRTC AEC3+APM-NS packages are **separate evidence** with different
candidates, fixtures, cadences and dispositions. This package does not pool,
import, reuse or reinterpret their outputs, metrics or adapters. The prior AEC
Challenge aggregate CSVs are pinned provenance only and are not attributed to
this package.
