<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-KRISP-ACCENT-CONVERSION — proprietary vendor-boundary blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Krisp Accent Conversion` (`component_id=krisp-accent-conversion`). Acceptance
profile: **Voice**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Task mode: **external-adapter**. Machine-readable
decision: **`DEFER`**; `status=proposal_only_incomplete`,
`evidence_status=incomplete`, `qualification.status=not_qualified`,
`qualification.candidate_qualified=false`, `candidate_metrics=null`. No result
qualifies the candidate.

Krisp Accent Conversion is a closed, proprietary commercial SDK/model. The
pinned merged research package inspected vendor documentation only and recorded
the candidate as **"closed/proprietary model, not locally downloadable"** and
**"Product benchmark only"**, with a vendor claim of roughly **180 ms** latency.
No licensed SDK package, model bundle, entitlement, terms record, vendor release
identity, hash-pinned runtime, accent-direction map, rights-cleared cohort,
target reference, reference output or parity vector exists anywhere in this
workspace. This package therefore contains a **stdlib-only deterministic
vendor/source auditor**, a **caller-supplied vendor-package manifest contract**
and a **synthetic 16 kHz / mono / 160-frame pass-through accounting control**.

It does not import, link, load or execute a vendor SDK, model or audio runtime;
does not read or write real audio; does not handle an entitlement token; does
not download anything; does not use a device clock; does not listen; does not
benchmark; and makes no release claim. Only
`docs/task-evidence/krisp-accent-conversion/` is added.

Pinned base: `f006454da9a72fbfd394e2b5bd05105201a9cd29`.
Branch: `swarm/SDK-KRISP-ACCENT-CONVERSION`.
Worktree: `/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-KRISP-ACCENT-CONVERSION`.

## Exact blockers

1. **Vendor SDK artifact absent.** No licensed Krisp Accent Conversion SDK
   package exists at `data/vendor/krisp/accent-conversion`, and the merged
   evidence publishes no vendor release ID, version or artifact digest.
2. **Model bundle digest unpublished.** No accent-conversion model bundle,
   byte count or SHA-256 is published or present; the model is closed and not
   locally downloadable.
3. **Entitlement and terms absent.** No named evaluation agreement,
   subscription entitlement, licence text, redistribution grant or product-use
   approval has been observed. No token is read, stored or handled here.
4. **Runtime unpinned and absent.** No isolated Krisp environment, package
   lock, recorded platform, ABI version or supported-architecture set exists;
   no vendor runtime was ever installed.
5. **Accent directions unpublished.** The merged evidence says only that
   *selected English accent directions* exist. The exact direction identifiers,
   ordering and source/target semantics are absent and are not invented.
6. **Rights and consent uncleared.** Input-speech, speaker-reference, consent,
   output-use and redistribution rights are unresolved for every clip.
7. **Matched cohort and scoring absent.** There is no rights-cleared
   source-accent cohort, no matched target reference set, no language/speaker
   grouping and no held-out ground truth.
8. **Approved reference parity absent.** No exact-runtime output, frame
   accounting, content delay, first-output/tail timing or fresh-process reset
   vector exists for any vendor release.

## Vendor-boundary audit (fixed paths, no network)

| Artifact | Required identity | Observation |
| --- | --- | --- |
| Vendor SDK package | release ID, bytes, SHA-256 | **Absent**; directory and artifact set absent |
| Model bundle | name, bytes, SHA-256 | **Absent** |
| Vendor release identity | exact approved ID | **Absent**; not invented |
| Entitlement record | named agreement | **Absent** |
| Licence and terms | reviewed text | **Absent** |
| Consent record | per-clip rights | **Absent** |
| Accent direction map | exact identifiers and ordering | **Absent** |
| Runtime | isolated lock and platform | **Absent** |
| Cohort and targets | frozen rights-cleared manifest | **Absent** |
| Research demo clips | provenance only | 3 L2-ARCTIC clips; **not used** |

The audit reads fixed workspace paths and records absence. It does not invent a
vendor release, package digest, model digest, direction name or runtime lock.

## Caller-supplied vendor-package contract

A caller manifest is accepted only when it has exactly the declared 26 fields,
every asset path is absolute, unique and present, every declared SHA-256 matches,
the SDK version and release ID are exact ASCII tokens, geometry is
16 kHz / mono / `f32` / 160 samples, `variant=vendor_sdk_caller_frame_160`, and
the runtime platform is in the declared closed catalog. All vendor artifacts are
caller-owned; nothing is vendored. The validator hashes the caller's files but
never imports, links or executes the SDK, and never reads an entitlement token.

Structural acceptance deliberately returns `accepted_for_qualification=false`,
`vendor_release_approved=false`, `entitlement_approved=false`,
`revision_pinned=false` and `qualification_effect=none`, because no vendor
release, entitlement, terms record or parity vector has been approved.

## Voice-profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

`reference.py` implements a deterministic acceptance-boundary control:

- A closed set of two synthetic placeholder direction pairs
  (`synthetic_accent_a` → `synthetic_accent_b`, `synthetic_accent_c` →
  `synthetic_accent_d`). They are **not** vendor accent names.
- Analytic 160-sample frames with a fixed integer pattern, finite and bounded.
- Exact frame validation, direction validation, and a **pass-through** record
  with `transform_applied=false` and `converted_speech=false`.
- Exact integer content-interval accounting for 485 accepted samples at a
  declared synthetic delay of 160 samples: 4 process calls plus 1 drain call,
  valid union `[0, 485)` with no overlap, including the declared startup
  padding at negative source coordinates.
- 40 adverse controls are actually invoked: malformed frames, malformed
  directions, out-of-bounds intervals, nonfinite values, and malformed,
  missing, relative or hash-mismatched vendor packages. All fail closed.
- The control is labelled
  `caller_supplied_synthetic_16k_mono_160_frame_passthrough_accounting_control_not_model_output`
  and has `qualification_effect=none`.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_vendor_sdk_and_model_identity`
2. `entitled_runtime_admission`
3. `vendor_terms_and_rights`
4. `exact_reference_parity`
5. `accent_direction_and_cohort_scoring`
6. `voice_outcome_separation`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`,
  `vendor_sdk_linked=false`, `vendor_sdk_vendored=false`,
  `entitlement_token_handled=false`, `adapter_code_added=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added. The task deliverable permits a prototype only with an
  approved public or user-supplied runtime, which is absent.
- No vendor frame/hop contract is assumed; the 160-sample geometry is a caller
  requirement for SDK v0 compatibility, not a vendor observation.

## Source-reported context

The merged candidate matrix marks the candidate `unavailable/blocked` and the
accent-conversion report records that SDK documentation was inspected, the model
is closed/proprietary and not locally downloadable, and the vendor documents
roughly 180 ms. The transform-space report records "No SDK, model, subscription
entitlement, or local scores found." Those facts are copied as
`source_reported_not_measured_here`; no accent-conversion, content, identity,
naturalness, latency, memory or RTF result exists and none is reproduced or
promoted. The vendor latency figure is not a measured value and does not
establish or violate any delay target here.

## Files

- `reference.py` — stdlib-only vendor audit, caller manifest, synthetic
  pass-through accounting control and report model.
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
`28fc5051facbbc020e5b4bdd1b56b26a5917e5fd18239ee5c43cc8bf6091d288`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-KRISP-ACCENT-CONVERSION
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Any appearance of the vendor SDK,
model bundle, entitlement, licence, consent, direction map, cohort, target
reference or runtime makes `verify.py` fail closed so the blocker must be
re-evaluated rather than silently promoted.

## Non-claims

No Krisp output, model execution, SDK link, entitlement use, network access,
real audio, corpus, transcript, target reference, direction truth, consent,
accent conversion, accent movement, accuracy, listening, latency, memory, RTF,
device timing, public benchmark or release result is claimed. The vendor audit
is a fixed-path local observation only. Missing evidence never qualifies this
candidate.
