<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ACCENTCL — task-local Voice-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`AccentCL` (`component_id=accentcl`). Acceptance profile: **Voice**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

AccentCL is the official seven-class English accent classifier referenced by
the merged accent-conversion research package. That package records the
candidate as **"Not run"**: the official source, seven class checkpoints
(approximately 2.56 GB each), the Whisper-Large-v3 backbone, a hash-pinned
runtime, a licence, a rights record, the class-label map and a matched accent
cohort are all absent. No upstream revision or artifact digest is published in
the merged evidence. This package therefore contains a **stdlib-only
deterministic source/asset auditor**, a **caller-supplied-asset manifest
contract** and a **synthetic seven-class classification accounting control**.

It does not import PyTorch, torchaudio, Transformers, NumPy, SciPy or
SoundFile, does not load or execute a model, does not read or write real audio,
does not download, does not use a device clock, does not listen, does not
benchmark and makes no release claim. Only this task-local directory is added.

Pinned base: `8d7982e8eb101004e98f8079f1aeaadbe3981f20`.
Branch: `swarm/SDK-ACCENTCL`.
Worktree: `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-ACCENTCL`.

## Exact blockers

1. **Source checkout absent.** No checkout exists at
   `research/accent-conversion-20261101/repos/AccentCL`, and the merged
   evidence publishes no full 40-hex upstream commit for
   [PSI-TAMU/AccentCL](https://github.com/PSI-TAMU/AccentCL).
2. **Seven checkpoint digests unpublished.** The merged evidence records only
   "each checkpoint is about 2.56 GB". It does not publish exact filenames,
   byte counts, URLs or SHA-256 values for the seven class checkpoints.
3. **Whisper-Large-v3 absent.** The required backbone weights and
   configuration are absent, and no immutable distribution revision or digest
   is recorded.
4. **Runtime unpinned and absent.** No isolated AccentCL environment or
   `data/envs/accentcl/requirements.lock` exists. The research host recorded
   Python 3.11.5, but AccentCL was never run there.
5. **Source licence absent.** No AccentCL licence file, model card terms or
   redistribution grant has been observed, so derivative-work and product-use
   rights are unresolved.
6. **Rights and consent uncleared.** Weight, training-data, speech-corpus,
   speaker-reference, consent, output-use and redistribution rights are not
   documented.
7. **Accent cohort and labels absent.** There is no rights-cleared accent
   cohort, no exact seven-class label map or ordering, no held-out ground
   truth, and no frozen language/speaker grouping. The three unused L2-ARCTIC
   clips in the research directory are not an AccentCL evaluation.
8. **Approved reference parity absent.** No exact-runtime AccentCL parity
   vector exists for the seven-class posterior, argmax or fresh-process reset.

## Source and asset audit (fixed paths, no network)

| Artifact | Required identity | Observation |
| --- | --- | --- |
| AccentCL source | full 40-hex commit | **Absent**; revision unpublished |
| Source licence | file and review | **Absent** |
| Seven class checkpoints | exact names, bytes, SHA-256 | **Absent**; ~2.56 GB each recorded |
| Whisper-Large-v3 | weights, config, revision, SHA-256 | **Absent** |
| Runtime | isolated lock | **Absent** |
| Rights/consent | artifact-specific record | **Absent** |
| Class label map | seven names and ordering | **Absent** |
| Accent cohort | frozen rights-cleared manifest | **Absent** |
| Research demo clips | provenance only | 3 L2-ARCTIC clips; **not used** |

The audit reads fixed workspace paths and records absence. It does not invent a
revision, checkpoint name, checkpoint digest, model digest or runtime lock.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every path is absolute and present, every declared SHA-256 matches, the source
revision is a full 40-hex commit, geometry is 16 kHz input / mono / seven
classes, and `variant=offline_whole_utterance`. Streaming variants are
rejected. The validator hashes the caller's files but never imports or executes
the source and never loads a checkpoint.

Structural acceptance deliberately returns `accepted_for_qualification=false`
and `revision_pinned=false`, because no upstream revision, licence, rights
record or parity vector has been approved.

## Voice-profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

AccentCL is an offline classifier, not a voice converter. Its applicable
outcome is a seven-class accent posterior and argmax; it produces no converted
speech, so generative text/identity/naturalness outcomes remain explicitly
unmeasured and separate.

`reference.py` implements a deterministic synthetic control at the acceptance
boundary:

- Seven synthetic placeholder labels (`synthetic_class_0` … `synthetic_class_6`).
  They are **not** upstream AccentCL class names; upstream names are absent.
- Hand-written normalized weights `(295,145,120,110,105,115,110)/1000` and a
  tie vector `(500,500,0,0,0,0,0)/1000`.
- Exact seven-entry validation, finite/range checks, normalization, deterministic
  argmax and the lowest-index tie rule.
- 33 adverse controls are actually invoked: malformed score vectors, malformed
  label sets and malformed or missing manifest assets. All fail closed.
- The synthetic control is labelled
  `caller_supplied_synthetic_seven_class_classification_accounting_control_not_model_output`
  and has `qualification_effect=none`.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_source_and_asset_identity`
2. `runtime_admission`
3. `artifact_rights_and_consent`
4. `exact_reference_parity`
5. `accent_cohort_and_scoring`
6. `offline_classification_separation`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK adapter remains blocked behind the gates.
- AccentCL remains offline and non-incremental. The package never presents it
  as a streaming processor and makes no first-output or tail timing claim.

## Source-reported context

The merged candidate matrix records AccentCL as **"Not run"**. Its official
seven-class checkpoint set is approximately 2.56 GB per checkpoint and requires
Whisper-Large-v3; the research host was an Apple M1 Mac with 8 GB RAM and
Python 3.11.5. The reported reason was that the download and run were not
practical on that host. Those facts are copied as
`source_reported_not_measured_here`; no accuracy, posterior, calibration,
listening, latency, memory or RTF result exists and none is reproduced or
promoted.

## Files

- `reference.py` — stdlib-only source/asset audit, caller manifest, synthetic
  seven-class accounting control and report model.
- `run.py` — regenerates `report.json`, its SHA-256 sidecar and `SOURCES.sha256`.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `test_reference.py` — Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three cold regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

Canonical report SHA-256:
`6c8e8dff96f06c1b07140bb72c4989221d41b3a0a0a9ede5c727193e828143f8`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-ACCENTCL
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Any appearance of the source,
checkpoints, backbone, runtime, licence, rights record, label map or cohort
makes `verify.py` fail closed so the blocker must be re-evaluated rather than
silently promoted.

## Non-claims

No AccentCL output, model execution, weight load, Whisper execution, runtime
call, network access, real audio, corpus, transcript, class label truth,
consent, accent classification, accuracy, macro-F1, calibration, listening,
latency, memory, RTF, device timing, public benchmark or release result is
claimed. The source audit is a fixed-path local observation only. Missing
evidence never qualifies this candidate.
