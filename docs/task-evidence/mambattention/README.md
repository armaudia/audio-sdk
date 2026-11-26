<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MAMBATTENTION — MambAttention readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the
MambAttention feasibility row. It is **not** a MambAttention implementation. No
upstream source checkout, checkpoint, config, preprocessing asset, runtime,
corpus, noisy/clean pair, enhanced waveform, listening result, device
measurement, benchmark or release claim is present. **No result here qualifies
MambAttention.**

The structured inventory marks `mambattention` as
`evidence_status=considered` with the **Enhancement** acceptance profile
(`verification_profile: enhancement`, `plan/INVENTORY.json`). The task row is
`mode=feasibility`; its plan note asks for runnable source, exact assets,
permitted scope, task geometry and matched evidence before a
caller-supplied-asset reference and an opt-in adapter. None of those
prerequisites exists locally.

Task owner: `agent-MAMBATTENTION`; reviewer: `reviewer-MAMBATTENTION`. Claim
base: audio-sdk `0cc1e79e592d7fc25f054fcd98824053be281f5e`; branch
`swarm/SDK-MAMBATTENTION`. Write scope is only
`docs/task-evidence/mambattention/`.

## Exact external blocker

The exact **source**, **checkpoint set** and **isolated runtime** are all
absent. The pinned
[noise-suppression candidate census](../../../../../research/noise_suppression_candidate_census.md)
records MambAttention as *"Mamba plus attention for generalizable
single-channel speech enhancement"* with *"Official repository and
checkpoints; paper reports VB-DemandEx PESQ 3.026, DNS2020 2.919, EARS-WHAM v2
2.010, with strong reported out-of-domain intelligibility."* and advises:
*"Valuable robustness/offline comparator; inspect checkpoint release, runtime
dependencies and license; compare per-domain rather than pooling unlike
tests."* The census also groups it under quality or robustness comparisons
*"with separate runtime reporting"*. Those are source-reported strings, not
locally verified artifacts.

No fixed path in this workspace contains a MambAttention checkout, resolved
40-hex revision, checkpoint file, config, preprocessing asset, runtime lock,
license text, rights record, rights-cleared paired cohort or parity vector.
Nothing is downloaded, vendored, staged, mirrored or inferred from the
repository or paper URL. Consequently:

- source identity, checkpoint hashes and license terms cannot be pinned;
- the code license and the checkpoint terms are both unresolved, and no
  training-data or per-domain output rights record exists;
- sample rate, sample format, frame hop, window, preprocessing, streaming
  behaviour and file-level boundary are **unestablished** and are not invented;
- no MambAttention output exists, so no per-domain PESQ, SI-SDR, STOI,
  clean-preservation, peak, latency, memory or RTF value is reported;
- the reported `3.026` / `2.919` / `2.010` PESQ numbers are recorded as
  source-reported strings only, never as a local result;
- missing, adverse, invalid and nonfinite evidence is never promoted to a pass,
  partial qualification or capability claim.

MambAttention is an offline/robustness single-channel enhancement candidate, not
an installed SDK processor and not a causal call-path component. Results from
the sibling `gap-urgenet`, `cmgan`, `clearvoice-frcrn-16khz`,
`fastenhancer-source-linked-onnx-wrapper`, `gtcrn-streaming-onnx` or
`rnnoise-v0-2` packages are not attributed to it.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `NikolaiKyhne/MambAttention` at an immutable 40-hex commit, with reviewed upstream license text and a per-file SHA-256 manifest from a reviewable tree |
| Checkpoint bundle | The caller-selected MambAttention checkpoint set at an immutable revision: every weight, config, preprocessing asset, model card and terms file, with byte count and SHA-256 per file; inspection must remain weights-only |
| Runtime | A locked, reproducible isolated Python/PyTorch/Mamba runtime with exact interpreter and package versions, device profile, lock SHA-256, offline load path, recorded host profile and the exact preprocessing contract |
| Rights | Reviewed source and checkpoint terms, training-data provenance, corpus rights, clean-reference permission, per-domain output rights, output use and redistribution |
| Cohort | A frozen, rights-cleared paired noisy/clean cohort with exact sample rates and durations, language and speaker groups, held-out splits, and identity/noisy, task-matched-baseline, noise-only/silence, clean-preservation, peak/invalid and unpaired controls |
| Enhancement results | Independent paired SI-SDR and STOI, clean-speech preservation, peaks and invalid (including nonfinite) outputs, authorized listening or a labeled predictive screen, alignment, content delay, state, memory, availability timing, resources and uncertainty on the exact runtime, compared per-domain |

The machine-readable record is `report.json` → `source_probe`, `weights_probe`,
`runtime_probe`, `absence_evidence`, `required_artifacts`, `exact_blockers`,
`enhancement_profile` and `gates`. `contract.json` carries the same
disposition, pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace/worktree probes and fixed home-cache
   probes are checked; no recursive walk is performed. All are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears,
   so a stale "absent" claim cannot be shipped.
2. **Stable pins.** The reviewed planning records, the structured inventory,
   the candidate census and the SDK boundary files are pinned by SHA-256. These
   are read-only provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Fail-closed admission schema.** A task-local Enhancement cohort manifest
   has a strict schema: unknown/missing fields, duplicate JSON keys, nonfinite
   values, floats, unsafe paths, duplicate or unsorted entries, unresolved
   tokens, non-integral or out-of-range integers, unsupported sample rates,
   non-offline runtimes, unconsented pairs and false rights are rejected. One
   synthetic structural control is accepted to prove the validator is not
   blanket-rejecting; it is labelled `synthetic_schema_control` and
   `qualifies=false`.
5. **Enhancement profile accounting.** Identity/noisy control, task-matched
   baseline, paired SI-SDR and STOI, clean-speech preservation, peaks and
   invalid outputs, authorized listening, alignment, content delay, state,
   memory, availability timing and the independent rights gates are each
   recorded as **blocked**.
6. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow and `.gitattributes` are
   pinned by SHA-256 and verified unchanged. Installed v0 remains 16 kHz, mono,
   float32, 160 samples per frame. No MambAttention provider is installed or
   registered; no descriptor, default, ABI, shared build, CI, board or handoff
   change is made.

## Enhancement profile application

| Enhancement requirement | Status here | Evidence |
| --- | --- | --- |
| Identity/noisy control and established task-matched baseline | blocked | No control or baseline output exists on the exact assets. |
| Paired SI-SDR and STOI where permitted clean references exist | blocked | No rights-cleared paired cohort and no score. |
| Clean-speech preservation | blocked | No clean-input preservation measurement. |
| Peaks and invalid outputs | blocked | No peak, clipping, nonfinite or invalid-value record. |
| Unpaired predictive screen or authorized listening | blocked | No screen, listening protocol or panel. |
| Alignment and content delay | blocked | No impulse, speech or content-delay measurement. |
| State, memory and measured content/availability timing | blocked | No state, memory or availability-timing record on the runtime. |
| Independent corpus, clean-reference, per-domain and output-use gates | blocked | Asset, corpus, per-domain and output terms are unresolved. |

## Historical and peer boundary

The pinned census and inventory contain a MambAttention **source and checkpoint
lead** and source-reported context only. There is no local MambAttention run,
output, metric, corpus or runtime. No value is inferred from merged sibling
enhancement evidence packages:

- `fastenhancer-source-linked-onnx-wrapper` and `clearvoice-frcrn-16khz` are
  named census baselines with their own caller-supplied-asset blockers; neither
  supplies MambAttention weights or metrics.
- `cmgan` is an adjacent 16 kHz enhancement blocker with different weights and
  only synthetic mechanism evidence.
- `gtcrn-streaming-onnx` is a causal streaming candidate; its geometry does not
  transfer to the unpinned MambAttention reference.
- `rnnoise-v0-2` is a hybrid DSP/RNN baseline with different geometry and its
  own unresolved weight terms.
- `survey-cln-01` is a merged coverage survey and supplies no measured result.

The board has no separate MambAttention second row; this package does not
inherit any adjacent ASR, finetuning, voice, separation or pipeline result.
Their transcripts, metrics, timings and rights records do not apply.

## Admission contract (task-local; not an SDK, MambAttention or Enhancement contract)

The schema is `audio-sdk/mambattention-enhancement-cohort/0.1`. Unknown and
missing fields, duplicate JSON keys, `NaN`/`Infinity`, floats, unsafe paths,
duplicate or unsorted entries, unresolved tokens, non-integral or out-of-range
integers, unsupported sample rates, non-offline runtimes, unconsented pairs and
any false right are rejected. The one accepted control is synthetic and never
qualifies. Admission never reads audio, loads weights or invokes a model.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `RG-01` | Exact licensed source and checkpoint bundle pinned | blocked |
| `RG-02` | Rights-cleared frozen paired cohort and clean references | blocked |
| `RG-03` | Identity/noisy control, task-matched baseline, noise-only/silence control and uncertainty | blocked |
| `RG-04` | Pinned source, checkpoint set, runtime, preprocessing contract and per-weight terms | blocked |
| `RG-05` | Alignment, content delay, state, memory, availability timing and numerical behavior | blocked |
| `RG-06` | Authorized listening or labeled predictive screen | blocked |
| `RG-07` | Opt-in provider intake and independent review | blocked |
| `RG-08` | Release approval | blocked |

## Pinned source and boundary digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
other paths are relative to the SDK worktree. These are read-only provenance
pins, not model evidence.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | MambAttention source/checkpoint/role finding |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Structured component row and Enhancement profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Unchanged plan and build surface |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` / `scripts/ci.py` / `REUSE.toml` | pinned in `SOURCES.sha256` | Unchanged build, CI and licensing |

The complete deterministic manifest, including every task-local artifact, is
`SOURCES.sha256`. `verify.py` fails closed on a missing, stale, malformed,
duplicated or extra pin, on any worktree change outside this directory, and on
any cold-start byte difference.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `contract.json` | Strict machine-readable `decision="DEFER"`, `proposal_only` / `incomplete`, `qualification.status="not_qualified"`, eight blocked gates, six exact blockers and the admission contract. |
| `reference.py` | Strict validators, absence audit, stable board identity, admission controls and canonical report/contract builders. |
| `run.py` | Regenerates contract, report, digest sidecar and manifest three times and requires byte-identical output. |
| `report.json` / `report.json.sha256` | Canonical evidence and its digest. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs. |
| `test_reference.py` | Deterministic unittest acceptance suite (no skips, no network). |
| `verify.py` | Read-only strict JSON, pin, profile, licensing, scope and three cold-start regeneration verifier. |
| `*.json.license`, `*.sha256.license` | REUSE sidecars. |
| `LICENSES.md` | Upstream license and asset-rights notes. |

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
```

`run.py all` repeats three times and fails if any rebuild differs by one byte.
`verify.py` never writes to this directory: it builds three isolated scratch
copies with symlinks to the pinned read-only inputs and checks cold-start
regeneration there. It also gates this branch's merge-base diff so committed
out-of-scope files cannot pass.

## Remaining gates

Rights-cleared upstream provenance and license verification, a pinned
checkpoint/config/runtime/preprocessing contract, exact-runtime parity, a
rights-cleared held-out matched per-domain cohort, target-device pacing and
telemetry, opt-in public-surface intake, independent exact-head review and
hosted checks, and release approval all remain blocked. Missing or adverse
evidence never qualifies the candidate. No merge, formal approval or release
action is taken here.
