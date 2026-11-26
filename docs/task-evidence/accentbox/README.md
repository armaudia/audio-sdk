<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-ACCENTBOX — task-local Voice-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`AccentBox` (`component_id=accentbox`, title "AccentBox"). Acceptance profile:
**Voice**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package records the exact upstream identity that the merged research and
evidence package preserves: only the repository URL
`https://github.com/jzmzhong/GenAID/` and a code/demo inspection. There is **no
source checkout, no full 40-hex upstream revision, no inference weight, no
accent embedding or label bundle, no runtime lock, no licence record, no rights
or consent record and no voice cohort** in the workspace or this worktree.
Nothing was downloaded or reconstructed. The package therefore contains a
**stdlib-only deterministic absence/asset auditor**, a **caller-supplied-asset
manifest contract** and a **synthetic PCM acceptance-accounting control at the
public v0 geometry**. It does not import PyTorch, torchaudio, Transformers,
NumPy, SoundFile or a TTS runtime, does not load or execute a model, does not
read or write real audio, does not download, does not use a device clock, does
not listen, does not benchmark and makes no release claim. Only this task-local
directory is added.

Pinned base: `8d7982e8eb101004e98f8079f1aeaadbe3981f20`.
Branch: `swarm/SDK-ACCENTBOX`.

## Exact blockers

1. **Source checkout absent.** No AccentBox / GenAID checkout exists under
   `research/accent-conversion-20261101/repos`, `data/checkouts`, the Hugging
   Face cache or any fixed probe path.
2. **Upstream revision unpinned.** The merged evidence records only the
   repository URL. No full 40-hex commit or per-file SHA-256 manifest exists, so
   none is invented here.
3. **Inference weights absent.** No checkpoint, tokenizer or weight file was
   downloaded or identified by byte count or digest.
4. **Accent-condition assets absent.** AccentBox is accent-controlled TTS with
   accent embeddings, so the accent label set, embedding table and target
   accent condition definition are required assets. None is present.
5. **Runtime absent.** There is no isolated environment, package pin or
   `data/envs/accentbox/requirements.lock`.
6. **Source licence unverified.** No `LICENSE`, `COPYING`, `NOTICE` or terms
   statement is present, and the merged evidence records no licence or
   redistribution grant.
7. **Rights and consent uncleared.** There is no weight, training-data,
   accent-label, speaker-reference, consent, output-use or redistribution
   record.
8. **Voice cohort and parity absent.** There is no rights-cleared held-out
   cohort, no permitted source/target-accent reference set and no approved
   exact-runtime parity vector. The three L2-ARCTIC clips in the research bundle
   are sibling TokAN inputs (CC BY-NC 4.0 research-only), not AccentBox evidence.

## Scope mismatch recorded, not resolved

The merged evidence classifies AccentBox as **accent-controlled text to speech
with accent embeddings**, not real-time audio-to-audio accent conversion. The
task asks for runnable source, exact assets and task geometry; no sample rate,
channel layout, frame size, text input contract or target-accent condition is
established. This package therefore records
`accentbox_geometry_status=unestablished`, asserts no AccentBox geometry, and
does not present the candidate as a converter or a low-latency processor.

## Source and asset audit (fixed paths, no network)

| Artifact | Required identity | Observation |
| --- | --- | --- |
| AccentBox / GenAID source | full 40-hex commit | **Absent** |
| Upstream revision | resolved commit + file manifest | **Absent**; URL only |
| Inference weights | exact SHA-256 | **Absent** |
| Tokenizer / accent embeddings | exact SHA-256 | **Absent** |
| Accent label / condition set | exact manifest | **Absent** |
| Runtime | Python + lock | **Absent** |
| Source licence | artifact-specific record | **Absent/unverified** |
| Rights/consent | artifact-specific record | **Absent** |
| Voice cohort | frozen rights-cleared manifest | **Absent** |
| Parity vector | approved exact-runtime output | **Absent** |

The audit probes 15 fixed paths and records whether each exists. Every probe is
currently absent. Any later-present path makes `reference.build_report()` and
`verify.py` fail closed so a stale "absent" claim cannot ship.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every file path is absolute and present, every directory path is absolute and
present, every declared SHA-256 matches, the source revision is a full 40-hex
commit, the channel count is mono, the input and output rates are integers in
`[8000, 192000]`, the target accent label is a lowercase token and
`variant=offline_whole_utterance`. Streaming and partial variants are rejected.
Validation hashes the caller's files but never imports or executes the source
and never loads a checkpoint.

Because no upstream revision is published in the merged evidence, the contract
sets `required_source_revision=null` and `revision_pin_available=false`. The
validator enforces the revision shape but cannot compare it to a known pin; the
source-identity gate remains blocked until an exact revision is supplied.

## Voice-profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

`reference.py` implements a deterministic synthetic control at the public v0
boundary:

- 3.0 s synthetic 16 kHz mono source PCM and 2.0 s synthetic 16 kHz mono output
  PCM generated with integer-only triangles plus an LCG; no libm synthesis.
- Exact duration accounting: `2/3`, reported as a reduced fraction.
- Offline whole-utterance alignment: first output sample 0, tail at the final
  output sample, `streaming_supported=false`, whole clip required.
- Text/semantic, identity/similarity and naturalness outcomes remain explicitly
  unmeasured and separate.
- 26 adverse controls are actually invoked: 11 malformed PCM cases and 15
  malformed manifest cases, including missing, invalid, out-of-range, boolean,
  string, wrong-rate, stereo, nonfinite, short/non-hex revision, wrong-variant,
  empty-label, missing-asset, missing-directory and hash-mismatch inputs. All
  fail closed.
- The synthetic control is labelled
  `caller_supplied_synthetic_accent_acceptance_plan_not_model_output`, asserts
  no AccentBox geometry and has `qualification_effect=none`.

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

The merged accent-conversion research contains TokAN metrics, MeanVC2 and
Seed-VC runs, and an accent-classifier proxy. None of those values is an
AccentBox result and none is copied into this report as a candidate metric.
They are listed as `sibling_context_not_attributed` provenance only.

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
  PCM accounting control and report model.
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
`e01e2e08306e07e51b4b46bcf350ba462dc21ea35fd5a30a4f0c88303e4e088e`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-ACCENTBOX
git diff --check
```

`run.py report.json`, `run.py sources` and `run.py --check` are idempotent.
`verify.py` runs three fresh interpreter regenerations in a private scratch
directory and requires byte-identical report and sidecar output. When the
package is copied out of the worktree, set `SDK_ROOT` to the SDK checkout and
`SOURCE_ROOT` to the common workspace root. Any appearance of a required asset
or licence makes `verify.py` fail closed so the blocker must be re-evaluated
rather than silently promoted.

## Non-claims

No AccentBox output, model execution, weight load, accent embedding, runtime
call, network access, real audio, corpus, transcript, consent, accent
conversion, synthesis, WER, speaker similarity, naturalness, latency, memory,
RTF, device timing, listening, public benchmark or release result is claimed.
The audit is a fixed-path presence and file-hash observation only. Missing
evidence never qualifies this candidate.
