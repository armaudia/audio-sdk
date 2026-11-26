<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-KRISP-VOICE-ISOLATION-2-5 — external vendor blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the Krisp
Voice Isolation 2.5 external-adapter row. It is **not** a Krisp adapter, vendor
runtime package or benchmark reproduction. No licensed vendor runtime, SDK
library, entitlement, DNSMOS-C scorer checkpoint, scoring environment, corpus,
processed vendor output, rights approval, comparison manifest or parity vector
is present. **No result here qualifies Krisp Voice Isolation 2.5.**

The structured inventory marks `krisp-voice-isolation-2-5` as
`evidence_status=partial` with the **External** acceptance profile
(`verification_profile: external`, `plan/INVENTORY.json`). The task asks for a
documented vendor boundary, an isolated adapter only if an approved public or
user-supplied runtime is available, and a same-scorer DNSMOS-C comparison on
265 public vendor outputs only if approved. None of those prerequisites exists
locally.

Pinned base: `f006454da9a72fbfd394e2b5bd05105201a9cd29`.
Branch: `swarm/SDK-KRISP-VOICE-ISOLATION-2-5`.
Owner: `agent-KRISP-VOICE-ISOLATION-2-5`.
Reviewer: `reviewer-KRISP-VOICE-ISOLATION-2-5`.

## Exact external blocker

The exact licensed **Krisp Voice Isolation 2.5 SDK runtime**, **commercial
entitlement and terms**, **SDK ABI documentation**, **DNSMOS-C/NISQA
checkpoint**, **hash-pinned scoring runtime**, **CC BY-NC 4.0 corpus**, **265
processed vendor outputs**, **rights approval** and **frozen comparison
manifest** are all absent. The only present item is the pinned research record
`research/cpp-library-krisp-benchmark-20261109.md`, which is source-reported
provenance, not reproducible evidence.

Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
runtime version, ABI, per-file byte count or SHA-256 is asserted as verified
beyond the exact dataset revisions, aggregate byte count and file count that the
research record itself states.

| Missing artifact | Exact requirement |
| --- | --- |
| Vendor runtime | Licensed Krisp Voice Isolation 2.5 SDK at an exact version/build with a per-file SHA-256 manifest and a recorded platform |
| Entitlement and terms | Signed commercial entitlement plus vendor terms for local processing, output retention, scoring, publication and redistribution |
| SDK documentation | Exact ABI, callback contract, sample rate, channel count, frame size, content delay, reset and drain behaviour |
| DNSMOS-C scorer | Official NISQA `runs/NISQA/model_best.pt`, feature extractor and windowing configuration with byte counts and SHA-256 |
| Scoring runtime | Isolated offline Python environment at `data/envs/dnsmos-c/requirements.lock` with a recorded platform |
| Source corpus | `Krisp-AI/VoiceIsolation-Benchmark-Dataset` revision `626bac8ca07fb9b4846d4f62d27c321753160b36`, 265 mono PCM16 WAVs at 32 kHz, CC BY-NC 4.0, with a per-file manifest |
| Processed outputs | `Krisp-AI/VoiceIsolation-Benchmark-Dataset-Processed` revision `8759715197e39e0356125e3f3197a9854c38fa60`, `vi_2_5_default` subset, 265 files, 647,960,782 bytes, with a per-file manifest |
| Rights approval | Noncommercial corpus use, vendor-output retention, scoring, publication and redistribution approval with complete notices |
| Comparison manifest | Frozen 265-file list, scenario mapping, segment windowing, failed-item policy, aggregation and one approved parity vector |

The machine-readable record is `report.json` → `upstream_identity`,
`asset_requirements`, `asset_audit`, `absence_probes`,
`caller_asset_contract`, `exact_blockers`, `external_profile`,
`reference_protocol` and `gates`. `contract.json` carries the same disposition,
pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Twenty-seven fixed workspace probes are checked; no
   recursive walk is performed and no home cache or mutable `/private/tmp` path
   is scanned. All are absent. `reference.audit_assets()` and `verify.py` fail
   if any probe later appears, so a stale "absent" claim cannot be shipped.
2. **Stable pins.** `plan/INVENTORY.json`, the SDK plan instructions, the
   External acceptance profile and the Krisp research record are pinned by
   SHA-256. These are read-only provenance inputs, not model or benchmark
   evidence. The public v0 boundary files (`CONTRACTS.md`, both public headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes`) are
   pinned and verified unchanged.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository`, `depends_on`, `deliverable`, `acceptance`, `evidence`
   and `write_scope` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local caller-supplied-asset
   manifest has a strict schema: unknown or missing fields, duplicate JSON
   keys, nonfinite or fractional scores, floats where integers are required,
   unsafe or relative paths, bad SHA-256 values, a bad vendor version, an empty
   entitlement, a bad platform, a wrong rate, a non-scoring scope or a
   streaming variant are rejected. One synthetic structural control is accepted
   to prove the validator is not blanket-rejecting; it is labelled
   `synthetic_structure_only_manifest`, has `qualification_effect=none`, hashes
   package files only and imports nothing. The overall accounting plan is
   labelled `synthetic_vendor_output_scoring_accounting_control_not_scorer_output`.
5. **External profile accounting.** Allowed access and exact data, separation
   of local runtime from vendor-output scoring and vendor claim, and fallback /
   disclosure without a licensed runtime are each recorded as **blocked**,
   **structural-only** or **not measured**.
6. **Adverse and missing controls.** Eleven malformed PCM cases, ten malformed
   score-aggregation cases and sixteen malformed manifest cases are actually
   invoked. Missing assets, invalid values, nonfinite values, a wrong version,
   a wrong scope and a hash mismatch all fail closed before any processing.
7. **Boundary preservation.** Installed v0 remains 16 kHz, mono, float32, 160
   samples per frame. No Krisp provider is installed or registered; no
   descriptor, default, ABI, shared build, CI, board or handoff change is made.

## External profile application

`plan/swarm/VERIFICATION.md` External row requires the allowed access and exact
candidate or processed data, separation of local runtime, vendor-output scoring
and vendor claim, and verification of fallback and disclosure without a
licensed runtime, code or asset in the default package. Every item is `absent`,
`structural_only` or `declared_not_verified`;
`satisfied_for_qualification=[]` and `real_external_metrics=null`.

| External requirement | Status here | Evidence |
| --- | --- | --- |
| Allowed access and exact data | blocked | No vendor entitlement or approved local corpus/output copy exists. |
| Local runtime vs vendor-output scoring vs vendor claim | structural only | The three lanes are named and separated, but none has real data. |
| Fallback and disclosure without a licensed runtime | declared, not verified | The default package substitutes nothing and labels every vendor number. |

## Documented vendor boundary

- **Vendor runtime**: absent. No library, header, ABI, callback contract,
  package or version is admitted. Vendor runtime geometry is
  `unestablished` and is not asserted.
- **Vendor-output scoring**: not run. The research record names a public
  265-file output set and a DNSMOS-C checkpoint, but neither is retained
  locally and no approval for re-scoring exists.
- **Vendor claim**: source-reported only. The vendor-published DNSMOS-C and WER
  values and the historical research-record values are recorded under
  `source_reported_context` with explicit labels. They are not reproduced.
- **Comparison geometry**: the research record documents 16 kHz mono PCM16 for
  the same-scorer comparison. That is recorded as
  `recorded_for_scoring_only`; it is not a vendor runtime ABI and not a device
  timing result.
- **Fallback**: without a licensed runtime, permission to score, or retained
  audio, this package produces only a deterministic synthetic accounting
  control and a blocker record. It does not substitute another denoiser, vendor
  output, checkpoint or score.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every file path is absolute and present, every directory path is absolute and
present, every declared SHA-256 matches, the vendor runtime version has a
semver shape, the entitlement ID and platform are lowercase tokens, the channel
count is mono, the scoring rate is exactly 16000 Hz, `scope=vendor_output_scoring`
and `variant=offline_whole_utterance`. Live vendor-runtime adapter scopes are
rejected here; that is a separate future gate. Validation hashes the caller's
files but never imports, links or executes the vendor runtime and never loads a
checkpoint.

Because no vendor runtime version is published in the merged evidence, the
contract sets `required_vendor_runtime_version=null` and
`runtime_version_pin_available=false`. The validator enforces the version shape
but cannot compare it to a known pin; the runtime-identity gate remains blocked
until an exact licensed version is supplied.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `vendor_runtime_and_license_identity`
2. `runtime_admission`
3. `artifact_corpus_and_output_rights`
4. `exact_reference_parity`
5. `same_scorer_reproduction`
6. `scope_and_claim_separation`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Sibling context is not attributed

The sibling `SDK-KRISP-ACCENT-CONVERSION` and
`SDK-KRISP-NOISE-CANCELLATION-BACKGROUND-VOICE-CANCELLATION-SDK` tasks are
different vendor observations with their own controls and dispositions; no
Krisp accent, noise-cancellation or Voice Isolation value is inherited here.
The cpp-library `basic.v1` and `voice_focus.v1` numbers are historical
research-record values, not SDK provider results. The 265 processed files are
Krisp vendor outputs, not `audio_enhance` or SDK outputs. No WER value is
produced for `audio_enhance` or the SDK.

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`,
  `vendor_runtime_linked=false`, `vendor_outputs_bundled=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK adapter remains blocked behind the gates.

## Files

- `reference.py` — stdlib-only absence/asset audit, caller manifest, synthetic
  PCM and scenario-balanced scoring accounting control and report/contract
  model.
- `run.py` — regenerates `contract.json`, `report.json`, its SHA-256 sidecar and
  `SOURCES.sha256` three times and requires byte-identical output.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `contract.json` — task contract, scope, boundary, blockers and eight gates.
- `SOURCES.sha256` — fail-closed SHA-256 manifest for sources, boundaries and
  package files. It never pins the mutable full `plan/swarm/TASKS.json`; only
  the linked-row stable identity is gated.
- `test_reference.py` — Python `unittest` acceptance checks.
- `verify.py` — read-only pins/JSON/identity/assets/licensing/reproduction/scope
  verifier, including three independent cold-start regenerations.
- `*.json.license`, `*.sha256.license` — SPDX sidecars for generated artifacts.

Canonical report SHA-256:
`149624c40dc41ed008040c4c70e3528b2d654befc0df202efebdac1d97323e46`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
```

`run.py all` performs three cold writes and requires all four artifacts to be
byte-identical. `verify.py` re-runs three independent cold-start regenerations
in scratch trees and fails on any pin drift, out-of-scope change, missing
sidecar, missing SPDX header or absent blocker. It also gates the branch diff
against the pinned base so committed out-of-scope files cannot pass.

## Non-claims

No Krisp runtime invocation, vendor SDK link, model execution, checkpoint load,
DNSMOS-C score, DNSMOS score, WER, STOI, SI-SDR, naturalness, latency, memory,
RTF, device timing, listening, real corpus, real vendor output, public benchmark
or release result is claimed. The audit is a fixed-path presence and file-hash
observation only. Missing evidence never qualifies this candidate.
