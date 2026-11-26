<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-TOKAN — task-local Voice-profile blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`TokAN` (`component_id=tokan`). Acceptance profile: **Voice**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. No missing result qualifies the candidate.

This package records the exact upstream TokAN identity from the merged research
and evidence package. The **source checkout is present** at full 40-hex revision
`cbfc09a2716003463a0501ceae04ee62809c3822` and its pinned files match, but the
repository ships **no licence file**, the three inference checkpoints and the
WavLM-Large layer-22 encoder cache are **absent**, no exact checkpoint SHA-256 is
published anywhere in the merged evidence, and there is no hash-pinned runtime,
rights record, consent record, rights-cleared voice cohort or approved parity
vector. The package therefore contains a **stdlib-only deterministic
source/asset auditor**, a **caller-supplied-asset manifest contract** and a
**synthetic PCM voice-acceptance accounting control**. It does not import
PyTorch, torchaudio, Transformers, Resemblyzer, NumPy or SoundFile, does not
load or execute a model, does not read or write real audio, does not download,
does not use a device clock, does not listen, does not benchmark and makes no
release claim. Only this task-local directory is added.

Pinned base: `2f4251b9abc92584b025f9b6ea665d9f3ec6e991`.
Branch: `swarm/SDK-TOKAN`.

## Exact blockers

1. **Checkpoints absent.** `Piping/TokAN` checkpoints `arlm.pt`,
   `quantizer.pt` and `hift.pt` under `checkpoints/default` are not present in
   the research workspace or this worktree. The recorded sizes (approximately
   690 MB, 393 MB and 83 MB) are observations, not byte pins.
2. **Checkpoint digests unpublished.** No exact byte count or SHA-256 exists for
   any of the three checkpoints or the WavLM-Large encoder at an immutable
   Hugging Face revision. This package therefore records `sha256=null` rather
   than inventing a digest.
3. **WavLM-Large cache absent.** The `microsoft/wavlm-large` layer-22 encoder
   cache (approximately 1.2 GB) was removed in the reported disk cleanup; no
   exported encoder or manifest remains.
4. **Runtime unpinned and absent.** The research run used Python 3.11.5 with
   compatibility pins Transformers 4.45.2 and setuptools 80.9.0, but the
   upstream `requirements.txt` leaves torch, torchaudio, NumPy, SciPy,
   SoundFile, Resemblyzer and `vector_quantize_pytorch` unpinned. No isolated
   environment or `data/envs/tokan/requirements.lock` exists.
5. **Source licence absent.** The pinned checkout has no `LICENSE`, `COPYING`
   or licence declaration, and the README paper metadata is a placeholder.
   Derivative-work, redistribution and product-use rights are unresolved.
6. **Rights and consent uncleared.** The three demo clips use L2-ARCTIC, whose
   corpus terms are CC BY-NC 4.0 research-only. There is no weight, training
   data, speaker-reference, consent or output-use rights record.
7. **Voice cohort absent.** Only three demo utterances exist, each using the
   source clip as its own speaker reference. There is no held-out cohort, no
   frozen language/speaker grouping, no manual transcript truth and no
   authorized listening panel.
8. **Approved reference parity absent.** No exact-runtime TokAN output,
   fresh-process reset trace or byte-level parity vector exists for beam size
   10 and 32 flow steps.

## Source and asset audit (fixed paths, no network)

| Artifact | Required identity | Observation |
| --- | --- | --- |
| TokAN source | commit `cbfc09a2…c3822` | **Present, exact and file-hash matched** |
| Source licence | `LICENSE`/`COPYING` at that commit | **Absent** |
| `arlm.pt` | exact SHA-256 | **Absent**, ~690 MB recorded |
| `quantizer.pt` | exact SHA-256 | **Absent**, ~393 MB recorded |
| `hift.pt` | exact SHA-256 | **Absent**, ~83 MB recorded |
| WavLM-Large L22 | exact manifest | **Absent**, ~1.2 GB recorded |
| Runtime | Python 3.11.5 + lock | **Absent**, compatibility pins only |
| Rights/consent | artifact-specific record | **Absent** |
| Voice cohort | frozen rights-cleared manifest | **Absent**; only 3 demo clips |

The audit reads `.git/HEAD` and its ref directly, hashes the 9 pinned TokAN
source files and checks the 16 source-level pins. It never executes the source
and never loads a checkpoint.

## Caller-supplied-asset contract

A caller manifest is accepted only when it has exactly the declared fields,
every path is absolute and present, every declared SHA-256 matches, the source
revision is the full pinned `cbfc09a2…c3822`, geometry is 16 kHz input / 24 kHz
output / mono, and `variant=offline_whole_utterance`. Streaming and partial
variants are rejected. Validation hashes the caller's files but never imports
or executes the source and never loads a checkpoint.

## Voice-profile application

`plan/swarm/VERIFICATION.md` Voice row requires permitted input and target
references, frozen task/language/speaker groups, separate text/semantic,
identity/similarity and naturalness outcomes, alignment and first-output/tail
timing, and independent consent, reference-availability and output-use gates.
Every item is `absent`, `not_measured` or `structural_only`;
`satisfied_for_qualification=[]` and `real_model_metrics=null`.

`reference.py` implements a deterministic synthetic control at the acceptance
boundary:

- 3.0 s synthetic 16 kHz mono source PCM and 2.0 s synthetic 24 kHz mono output
  PCM generated with integer-only triangles plus an LCG; no libm synthesis.
- Exact duration accounting: `2/3`, reported as a reduced fraction.
- Offline whole-utterance alignment: first output sample 0, tail at the final
  output sample, `streaming_supported=false`, whole clip required.
- Text/semantic, identity/similarity and naturalness outcomes remain
  explicitly unmeasured and separate.
- 23 adverse controls are actually invoked: 11 malformed PCM cases and 12
  malformed manifest cases, including missing, invalid, out-of-range, boolean,
  string, wrong-rate, stereo, nonfinite, short-revision, wrong-variant and
  missing-asset inputs. All fail closed.
- The synthetic control is labelled
  `caller_supplied_synthetic_voice_acceptance_plan_not_model_output` and has
  `qualification_effect=none`.

## Eight blocked release gates

All eight gates remain `blocked`:

1. `exact_source_and_asset_identity`
2. `runtime_admission`
3. `artifact_rights_and_consent`
4. `exact_reference_parity`
5. `voice_cohort_and_scoring`
6. `offline_streaming_separation`
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
- TokAN remains offline and non-incremental. The package never presents it as
  a streaming processor and makes no first-output or tail timing claim.

## Source-reported context

The merged candidate matrix reports three L2-ARCTIC demo utterances with
Whisper-tiny WER 0.00, Resemblyzer cosine 0.798–0.874, duration ratios
0.661–0.911 and CPU RTF 17.38–20.56 on an Apple M1. The accent-classifier proxy
did not show consistent movement toward General American and no blinded human
listening occurred. Those values are copied as
`source_reported_not_measured_here`; they are not reproduced, re-scored or
promoted. The runtime includes process startup, checkpoint loading, feature
extraction and waveform writing, and is not a streaming latency measurement.

## Files

- `reference.py` — stdlib-only source/asset audit, caller manifest, synthetic
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
`6cd151f2178d95d6e5c98b389a9b71f80097a01efaaa92a4450a7c26db1bcd13`.

## Reproduction

Use the pinned interpreter with bytecode writing disabled. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py report.json
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py sources
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-TOKAN
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

No TokAN output, model execution, weight load, encoder cache, runtime call,
network access, real audio, corpus, transcript, consent, accent conversion,
WER, speaker similarity, naturalness, latency, memory, RTF, device timing,
listening, public benchmark or release result is claimed. The source audit is a
git-reference and file-hash observation only. Missing evidence never qualifies
this candidate.
