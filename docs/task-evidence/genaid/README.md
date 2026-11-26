<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-GENAID — GenAID readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the GenAID
feasibility row. It is **not** a GenAID implementation. No upstream source
checkout, pretrained checkpoint, accent embedding, tokenizer, text frontend,
config, runtime, corpus, text-input manifest, target reference, synthesized
waveform, listening result, device measurement, benchmark or release claim is
present. **No result here qualifies GenAID.**

The structured inventory marks `genaid` as `evidence_status=considered` with
the **Voice** acceptance profile (`verification_profile: voice`,
`plan/INVENTORY.json`). The row asks for runnable source, exact assets,
permitted scope, task geometry and matched evidence before a
caller-supplied-asset reference and an opt-in adapter; none of those
prerequisites exists locally.

Pinned base: `77d7800cac82899eb02a8aa55535d00e4faa8946`.
Branch: `swarm/SDK-GENAID`. Owner: `agent-GENAID`. Reviewer: `reviewer-GENAID`.

## Exact external blocker

The exact **source**, **checkpoint/weights bundle**, **accent-condition
assets**, **text frontend/tokenizer** and **isolated runtime** are all absent.
The pinned research record names GenAID as *"AccentBox / GenAID"* and states
plainly: *"Code/demo inspected; no inference weights downloaded.
Accent-controlled TTS and accent embeddings rather than real-time
audio-to-audio conversion. Useful if the product scope expands to synthesis."*
The only upstream identity recorded is the repository URL
`https://github.com/jzmzhong/GenAID/`; no 40-hex revision, file manifest,
checkpoint digest or runtime lock is recorded.

Nothing was fabricated, reconstructed, mirrored, downloaded or substituted. No
revision, file name, byte count or SHA-256 is asserted as verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `https://github.com/jzmzhong/GenAID/` at an immutable 40-hex commit, with the reviewed upstream license text, a per-file SHA-256 manifest from a reviewable tree, and a recorded provenance decision |
| Upstream revision | The resolved full 40-hex commit and its per-file SHA-256 manifest; the merged evidence records only the repository URL |
| Checkpoint bundle | The caller-selected GenAID checkpoint at an immutable revision, including every weight, config and model card with byte count and SHA-256 per file |
| Accent-condition assets | The accent label set, accent embedding table and target accent condition definition, each with an exact digest |
| Text frontend and tokenizer | Every text normalizer, grapheme/phoneme tokenizer, lexicon and text-frontend configuration declared by the resolved upstream revision, each with an exact digest |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter and package versions, a recorded platform, a lock SHA-256 and an offline load path; no `data/envs/genaid/requirements.lock` exists |
| Rights | Reviewed source, weight, training-data, accent-label, text-input, speaker-reference, consent, output-use and redistribution terms |
| Cohort and parity | A frozen, rights-cleared voice cohort with permitted text inputs and target-accent references, language and speaker groups, held-out splits, separate text/identity/naturalness outcomes, and an approved exact-runtime parity vector |

The machine-readable record is `report.json` → `source_reported_context`,
`asset_requirements`, `asset_audit`, `absence_probes`, `caller_asset_contract`,
`exact_blockers`, `voice_profile`, `reference_protocol` and `gates`.
`contract.json` carries the same disposition, pins, geometry and all eight
blocked release gates.

## What this package verifies

1. **Absence evidence.** Sixteen fixed workspace/worktree probes are checked; no
   recursive walk is performed and no home cache is scanned. All are absent.
   `reference.audit_assets()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** The inventory, the Voice acceptance profile, the SDK plan
   instructions and the accent-conversion research record are pinned by
   SHA-256. These are read-only provenance inputs, not model evidence. The
   public v0 boundary files (`CONTRACTS.md`, both public headers,
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
   keys, nonfinite values, floats where integers are required, unsafe or
   relative paths, non-integral or out-of-range integers, unsupported output
   rates, non-offline runtimes, a non-TTS scope, unconsented references and
   false rights are rejected. One synthetic structural control is accepted to
   prove the validator is not blanket-rejecting; it is labelled
   `synthetic_structure_only_manifest`, has `qualification_effect=none`, and
   hashes package files only. The overall accounting plan is labelled
   `caller_supplied_synthetic_voice_accounting_control_not_model_output`.
5. **Voice profile accounting.** Permitted text and target references, task and
   language groups, text/semantic preservation, identity/similarity,
   naturalness, alignment and first-output/tail timing, and the independent
   consent/reference/output-use gates are each recorded as **blocked** or
   **not measured**.
6. **Adverse and missing controls.** Eleven malformed PCM cases and sixteen
   malformed manifest cases are actually invoked. Missing assets, invalid
   values, nonfinite values, a wrong variant and an audio-to-audio scope
   mismatch all fail closed before any processing.
7. **Boundary preservation.** Installed v0 remains 16 kHz, mono, float32, 160
   samples per frame. No GenAID provider is installed or registered; no
   descriptor, default, ABI, shared build, CI, board or handoff change is made.

## Voice profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Permitted text input and target-accent references | blocked | No rights-cleared text manifest or target reference exists. |
| Task, language and speaker groups | blocked | No cohort manifest exists. |
| Text and semantic preservation | blocked | No model, transcript truth or score exists. |
| Identity and similarity | blocked | No embedder, source/target pair or score exists. |
| Naturalness | blocked | No authorized listening protocol or panel. |
| Alignment and first-output/tail timing | blocked | Structural offline accounting only; no runtime or device clock. |
| Consent, reference availability and output use | blocked | Rights and consent terms are unresolved. |

## Scope mismatch recorded, not resolved

The merged evidence classifies GenAID as **accent-controlled text to speech
with accent embeddings**, not real-time audio-to-audio accent conversion. The
task asks for runnable source, exact assets and task geometry; no output sample
rate, channel layout, frame size, text input contract or target-accent
condition is established. This package therefore records
`genaid_geometry_status=unestablished`, asserts no GenAID geometry, and does
not present the candidate as a converter or a low-latency processor.

The synthetic PCM accounting control runs only at the public SDK v0 boundary
(16 kHz, mono, float32, 160 samples). It checks PCM validity, exact duration
accounting (`2/3`, a reduced fraction) and offline-only alignment. It is not
GenAID output, not synthesized speech and not a quality or timing result.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every file path is absolute and present, every directory path is absolute and
present, every declared SHA-256 matches, the source revision is a full 40-hex
commit, the channel count is mono, the output rate is an integer in
`[8000, 192000]`, the target accent label is a lowercase token,
`scope=accent_controlled_tts` and
`variant=offline_whole_utterance`. Streaming, audio-to-audio and partial
variants are rejected. Validation hashes the caller's files but never imports
or executes the source and never loads a checkpoint.

Because no upstream revision is published in the merged evidence, the contract
sets `required_source_revision=null` and `revision_pin_available=false`. The
validator enforces the revision shape but cannot compare it to a known pin; the
source-identity gate remains blocked until an exact revision is supplied.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_source_and_asset_identity`
2. `runtime_admission`
3. `artifact_rights_and_consent`
4. `exact_reference_parity`
5. `voice_cohort_and_scoring`
6. `task_scope_and_geometry`
7. `opt_in_provider_intake`
8. `public_default_and_release`

## Sibling context is not attributed

The sibling `accentbox` task shares the same upstream URL but is a separate
Voice blocker with its own control and disposition; no AccentBox asset, result
or digest is inherited. `accentcl` is an accent classifier with multi-gigabyte
checkpoints and a Whisper-Large-v3 dependency, not GenAID. TokAN, MeanVC2,
Seed-VC, RVC and the accent-classifier proxy are other candidate observations;
none is a GenAID result and none is copied into this report as a candidate
metric.

## Boundary

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `production_callback_registered=false`.
- No descriptor, registry, shared CMake, default, installed-v0 behavior, CI,
  board or handoff change.
- No adapter is added; the opt-in SDK adapter remains blocked behind the gates.

## Files

- `reference.py` — stdlib-only absence/asset audit, caller manifest, synthetic
  PCM accounting control and report/contract model.
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
`de529ff53bbffb84d81cd1d70dbc16896abff2e10f06ff6db0d0b60b1fc46727`.

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

No GenAID output, model execution, weight load, accent embedding, tokenizer
call, runtime invocation, network access, real audio, corpus, text input,
transcript, consent, synthesis, accent conversion, WER, speaker similarity,
naturalness, latency, memory, RTF, device timing, listening, public benchmark
or release result is claimed. The audit is a fixed-path presence and file-hash
observation only. Missing evidence never qualifies this candidate.
