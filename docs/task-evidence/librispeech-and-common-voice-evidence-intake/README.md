<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LIBRISPEECH-AND-COMMON-VOICE-EVIDENCE-INTAKE: dataset intake blocker

**Status: `proposal_only_incomplete`; evidence status `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the
LibriSpeech and Common Voice intake row. **No LibriSpeech or Common Voice
archive, audio byte, transcript, metadata file, prepared manifest, license
text, rights decision, scorer, cohort, listening result, device measurement,
benchmark or release claim is included.** No result here qualifies either
dataset.

## Exact blocker: exact licensed data and manifests absent

A bounded, read-only search of the documented workspace and local preparation
paths found **no LibriSpeech test-clean archive, extracted `LibriSpeech
test-clean` tree or prepared manifest** and **no Common Voice release archive,
metadata file or prepared manifest**. No archive was downloaded, extracted,
copied, opened, hashed or decoded. No manifest was fabricated. No network
request was made.

| Required item | Recorded local state |
| --- | --- |
| LibriSpeech `test-clean.tar.gz` | **Absent** at every documented path; reported OpenSLR SLR12 MD5 is recorded, no local byte identity exists |
| LibriSpeech extracted tree | **Absent**; no FLAC or transcript file is read |
| LibriSpeech prepared manifest | **Absent**; no archive-bound items, candidate scope or speaker split |
| Common Voice release archive | **Absent**; the reported `sps-corpus-5.0-2026-09-11` release is not staged |
| Common Voice metadata/prepared manifest | **Absent**; no `client_id` grouping or speaker-disjoint split is verified |
| LibriSpeech rights | **Blocked:** reported CC BY 4.0 only; no license text, attribution, privacy/publicity review or use decision |
| Common Voice rights | **Blocked:** listed CC0-1.0 only; download-time MDC Data Consumer License not inspected or accepted; enhancement is not a stated intended use; no-identification and no-rehosting terms unresolved |
| Per-model overlap audit | **Absent:** LibriVox/MLS risk for DPDFNet is recorded only, Common Voice learned-model overlap unreviewed |
| Frozen cohort, scorer, aggregation, controls | **Absent**; no representative valid result and no local score |
| Optional evidence adapter | **Not exposed:** `DEFER` before `optional_evidence_adapter_exposure` |

The machine-readable record is `report.json` → `blocker`,
`presence_probe`, `datasets`, `rights`, `overlap_matrix`,
`acceptance_profile`, `admission_controls` and `release_gates`.
`contract.json` carries the same blocker, the same required artifacts and all
eight blocked release gates.

## Dataset identities stay distinct

No fact is pooled between the two datasets. The table separates the reported
identity from the local state.

| Field | LibriSpeech test-clean | Common Voice Spontaneous Speech 5.0 English |
| --- | --- | --- |
| Source | OpenSLR SLR12 | Mozilla Data Collective |
| Exact identity | `test-clean.tar.gz`, reported MD5 `32fa31d27d2e1cad72775fee3f4849a9` | dataset `cmu5nqn1h00vwmi07b4dbk085`, release `sps-corpus-5.0-2026-09-11` |
| Reported media / rate | FLAC, 16 kHz | MP3; native sample rate not recorded |
| Reported size / count | official archive, count not asserted | 519.05 MB reported, 5,898 clips, 642 speakers, 18.6 recorded / 8.39 validated hours |
| Reported license | CC BY 4.0 | CC0-1.0 listing; MDC download-time license unresolved |
| Reported derivation / use | LibriVox audiobooks; read English speech | ASR/CALL/language revitalization; not enhancement |
| Local archive | Absent | Absent |
| Local manifest | Absent | Absent |
| Rights cleared | No | No |
| Speaker split verified | No | No |
| Local metric | None | None |

The Common Voice counts are source-reported only. The native sample rate is not
inferred. LibriSpeech and MLS are both reported derived from LibriVox; that
creates an overlap risk for DPDFNet, not proof of exact recording or speaker
overlap.

## Evidence profile application

`plan/swarm/VERIFICATION.md` assigns the **Evidence** profile
(`plan/INVENTORY.json` records `verification_profile=evidence`). The mapping is
machine-readable in `report.json` → `acceptance_profile`.

| Profile item | Evidence | Claim limit |
| --- | --- | --- |
| Pin scorer, corpus and cohort | `required_items.pinned_scorer_corpus_and_cohort = blocked` | No scorer, corpus or cohort |
| Pin aggregation, failed items and controls | `blocked` | No aggregation or failed-item result |
| Separate evidence kinds | `declared_only`; paired, unpaired, synthetic, human and source-reported are separate | Only source-reported has content; nothing scored |
| Validate one invalid/missing case | `recorded`; live control rejects both datasets with 0 archives and 0 manifests, and all adverse declarations are rejected | Structural rejection only |
| Validate one representative valid result | `blocked`; no valid item or result exists | Missing result never promoted |
| Exact references and rights | `blocked`; reported identity only, no local bytes or approval | No provenance pass |

## Fail-closed admission gate

`reference.admit()` validates a caller-supplied intake declaration strictly and
has **no admitting branch**:

| Situation | Decision |
| --- | --- |
| Archive and manifest absent | `DEFER`, `archive_absent` / `prepared_manifest_absent` |
| Manifest present but identity unverified | `DEFER`, `manifest_identity_unverified` |
| Rights absent or inconsistent | `DEFER`, `license_text_absent` / `rights_not_approved` |
| Overlap unreviewed | `DEFER`, `model_overlap_unresolved` |
| Even a structurally valid, fully approved declaration | `DEFER`; the frozen cohort, scorer and representative valid result are still absent |

The unit tests exercise the validator with a **clearly labelled non-corpus
placeholder declaration**. Its synthetic checksums are never recorded as
dataset identity and admission still returns `DEFER`, `qualifies=false`,
`metrics=null`.

## Failure controls (exact failures recorded as failures)

- Corpus identity: unknown corpus, wrong subset, wrong source revision and
  wrong license label are rejected.
- Archive: traversal, absolute and backslash filenames, wrong LibriSpeech
  archive name, wrong or uppercase MD5, wrong checksum kind, missing checksum,
  zero/negative/bool byte count and bool presence are rejected.
- Manifest: missing/uppercase/nonhex digest, zero/negative/bool item count,
  NaN/±Infinity/zero/negative/bool/string duration, missing transcript binding,
  non-speaker-disjoint split, unhashed identifiers, uppercase/Unicode/path
  split versions and split claims without a manifest are rejected.
- Rights: mismatch, text without digest, digest without text, approval without
  terms, Common Voice redistribution, missing no-identification or no-rehosting
  acknowledgement, LibriSpeech redistribution without attribution and
  listening without use are rejected.
- Model: unknown model, invalid overlap status, SpeexDSP with a learned-model
  status or audit, learned model with a no-training-corpus status, exact
  exclusion without an audit and unreviewed status with an audit are rejected.
- Strict JSON: duplicate keys, NaN/Infinity constants, trailing data, invalid
  syntax and non-object roots are rejected.

Every rejection is immutable and no rejected case is promoted.

## Exact scope

- Work is confined to
  `docs/task-evidence/librispeech-and-common-voice-evidence-intake/`. Shared
  CMake, `CONTRACTS.md`, public headers, descriptor registry/defaults,
  installed v0 behaviour, provider registration, board/handoff files, CI,
  rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  audio adapter, provider, descriptor, installed target or public API/ABI
  change exists.
- No provider is registered, enabled by default or selected as a default.
  There is no automatic discovery and no fallback.
- No real corpus, audio file, transcript, metadata row or manifest is read.
  The local control is an analytic empty ledger, not corpus evidence.
- No listening, device timing, wall-clock playback, ASR, SI-SDR, STOI, PESQ,
  benchmark or release claim is made.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim, history and every other mutable field never enter
  canonical bytes and are never a gate. The full mutable
  `plan/swarm/TASKS.json` is **not hashed** into any artifact.

## Pins

Paths outside this directory are relative to the `audioml` workspace root; SDK
boundary paths are relative to this SDK worktree.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:realtime-audio-library/implementation_record.md` | `12b7c17d6ae969cb3e9697f3309667518048f27792b283178d326746e1bbfb81` | LibriSpeech preparation path, absent archive and no real-data run |
| `source:realtime-audio-library/research/holdout_speech_source_assessment_20261028.md` | `a3802ae6ebee5d1ddb1e41154ca2de01c338445fcf6561d7a223663dd3741450` | Common Voice release identity and unresolved MDC terms |
| `source:realtime-audio-library/docs/evaluation_plan.md` | `56f03609e57d3e95c8d1a9ae75a44d345b77e3c476da26a60770b7718f90c2f6` | LibriSpeech MD5, preparation paths, overlap and split scope |
| `source:realtime-audio-library/docs/rights_clearance_inventory.md` | `de540032406b5ca50803d52ba7cf1630a1eb8dcdf8d050e4f351cabbadc29818` | Dataset-scoped not-cleared findings |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Evidence profile and research-control disposition |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Intake / opt-in adapter sequence |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Evidence acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged shared build |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | Unchanged licensing metadata |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI |
| `.gitattributes` | `7ffed4be0021bc3fd2b2816bc3db2ebac9333d9c6ff809e3e3695d6cc6af4185` | Unchanged Git attributes |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` | Unchanged CI driver |

`SOURCES.sha256` additionally pins every task-local artifact and excludes
itself because a file cannot pin its own bytes. `contract.json` is excluded
from `SOURCES.sha256` because it pins the manifest; it is pinned by the
verifier and by review. `verify.py` fails closed on a missing, stale,
malformed, duplicated or extra pin and on any worktree change outside this
directory.

No external archive, manifest, license or model is pinned. The reported
LibriSpeech MD5 and Common Voice release identifiers are provenance only and
are never presented as a local byte hash.

## Files

- `contract.json` / `contract.json.license`: machine-readable DEFER contract.
- `reference.py`: stdlib-only deterministic probes, strict validators,
  fail-closed admission gate, structural control and canonical report builder.
- `run.py`: regenerates report, sidecar, manifest and contract three times and
  fails if any rebuild differs by one byte.
- `report.json` / `report.json.sha256`: canonical evidence and its digest.
- `SOURCES.sha256`: deterministic manifest of pinned inputs and local files.
- `test_reference.py`: unittest acceptance suite.
- `verify.py`: read-only canonical JSON, pin, board-identity, profile,
  licensing, scope and three-cold-start verifier.
- `*.license`: REUSE SPDX sidecars for generated artifacts.

## Reproduction

```sh
cd docs/task-evidence/librispeech-and-common-voice-evidence-intake
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --all
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py --all` repeats three times and fails if report, sidecar, manifest or
contract bytes differ. `verify.py` never writes to this directory: it
regenerates in memory, then builds three isolated scratch copies with symlinks
to the pinned read-only inputs and checks cold-start byte identity there. Its
scope gate diffs this branch against the newest merge-base with `origin/main`
(falling back to `main`), so a committed out-of-scope edit fails as
`base_out_of_scope_change` while unrelated sibling packages added to `main`
later do not; when no base resolves it fails as `scope_base_unavailable`
instead of passing.

## Eight blocked release gates

1. `RG-01` LibriSpeech archive and license identity: exact OpenSLR SLR12
   `test-clean.tar.gz`, official MD5, archive SHA-256, CC BY 4.0 text and
   attribution.
2. `RG-02` LibriSpeech prepared manifest and speaker-disjoint split from
   archive-bound FLAC/transcript bytes.
3. `RG-03` Common Voice exact release, archive checksum and accepted
   download-time Data Consumer License with a defined enhancement scope.
4. `RG-04` Common Voice prepared manifest and speaker-disjoint split from
   hashed `client_id` values only.
5. `RG-05` separate dataset-scoped rights decisions for use, retention,
   evaluation, listening, redistribution and derived outputs.
6. `RG-06` exact per-model, per-dataset overlap audit, including DPDFNet /
   MLS / LibriVox and Common Voice learned-model review.
7. `RG-07` frozen cohort, pinned scorer, aggregation, failed-item policy,
   controls, one invalid/missing and one representative valid result.
8. `RG-08` opt-in adapter decision, benchmark validation, authorized
   listening, independent exact-head review and release approval.

Missing, rejected, adverse or source-reported evidence never qualifies either
dataset. The exact reopen conditions are recorded on each gate and in
`blocker.reopen`.
