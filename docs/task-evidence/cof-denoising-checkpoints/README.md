<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-COF-DENOISING-CHECKPOINTS — source, checkpoint and runtime feasibility blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`cof-denoising-checkpoints` (title "CoF denoising checkpoints", mode
`feasibility`). Decision: **DEFER**; `status=incomplete`,
`proposal_only=true`, `qualification.status=not_qualified`. Missing evidence
never qualifies a candidate.

This package does **not** contain or execute CoF source, a repository snapshot,
a checkpoint, weight, configuration, sampler implementation, generative
runtime, corpus, audio signal, model output, listening result or benchmark
result. It pins the census/inventory/acceptance boundary that exists, probes a
fixed path inventory to evidence absence, exercises a fail-closed
caller-supplied run manifest and a synthetic protocol envelope with no model,
and defines the exact external artifacts and rights required before any
implementation could be considered. Only
`docs/task-evidence/cof-denoising-checkpoints/` is written; no provider,
registry, descriptor, public header/ABI, shared CMake, CI workflow, default
selection or installed v0 behavior changes.

## Exact external blocker

The candidate is named by one census sentence and nothing else:

> **CoF denoising checkpoints** | Diffusion / flow generative speech
> enhancement, offline quality reference | Official 2026 repository publishes
> VoiceBank+Demand and WSJ0+WHAM denoising checkpoints for two formulations and
> both pretrained and corrective-forcing stages. | Research-only/high-compute;
> verify weight/code/data terms, sampler, hardware and output fidelity. Compare
> as a separate generative family, not a real-time contender.

`research/noise_suppression_candidate_census.md`, line 62.

That sentence records **no** repository URL, immutable commit or release tag,
source file, code license, notice, checkpoint file name, revision, byte count,
SHA-256, sampler, step count, seed, dtype, device, context, padding recipe,
training-data term or output. Fixed workspace, SDK-worktree and home-cache
probes find no CoF source, checkpoint, environment, wheel, model cache or
manifest. The probed CPython `3.12.16` interpreter exposes no `torch` or
`torchaudio` (`ModuleNotFoundError: No module named 'torch'`), and no CoF
runtime is pinned.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The exact upstream repository URL and immutable revision for both formulations, the complete source snapshot, the code license and notice text, and a formulation-to-file map. No download is permitted here. |
| `BLK-02` | The complete checkpoint set for VoiceBank+Demand and WSJ0+WHAM, both formulations and both pretrained and corrective-forcing stages, with exact file names, immutable revision, byte counts and matching SHA-256 values, plus artifact-specific terms. |
| `BLK-03` | A locked offline Python/PyTorch-class runtime with wheel names, versions, byte counts, SHA-256 values and install location, plus the exact sampler, steps, seed, dtype, device, context and padding recipe. |
| `BLK-04` | A digest-pinned, rights-reviewed caller-owned input set with corpus, acquisition, evaluation, derived-output and redistribution decisions, checkpoint training-data terms for both corpora, and attribution. |
| `BLK-05` | A deterministic reproduced run with per-item hashes, finite/length-preserving checks, exact repeats, identity/noisy controls, task-matched baseline, paired SI-SDR/STOI, clean-speech preservation, peaks, alignment, state, memory and content/availability timing. |
| `BLK-06` | Separate mode/platform timing and resource measurements, authorized listening or a separately labeled predictive screen, then a versioned OFF-by-default provider intake with clean-install proof and independent exact-head review. |

**Reopen condition.** A caller supplies the exact source revision with reviewed
license/notice, the complete checkpoint set with per-file byte counts and
SHA-256, a locked offline runtime and sampler recipe, rights-cleared inputs and
training-data terms, a reproduced deterministic run with the full Enhancement
profile, separate mode/platform and listening evidence, and a separate
OFF-by-default intake with independent review. Until then this task stays
`DEFER`.

## What is present and pinned

`contract.json` and `report.json` pin only the evidence and policy boundary:

| Input | SHA-256 | Use |
| --- | --- | --- |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | The single candidate sentence |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Enhancement profile and `sdk-model` disposition |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` | Human-readable inventory |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK delivery boundary |

Thirteen SDK-worktree boundary files are pinned: `CONTRACTS.md`, the unchanged
provider/session v0 headers, the Python binding, `CMakeLists.txt`, CI,
`REUSE.toml`, `docs/provider-intake.md`, and the merged
`classical-wiener-denoising` and `cleanunet-dns-large-high` sibling
README/report boundaries. Sibling fixtures, checkpoints and results are **not**
reused.

The shared board row is read only through the stable projection
`{id, title, component, mode, repository, depends_on}`. `status`, `owner`,
`claim`, `review`, `handoff`, `blocked_reason` and `dispatch_priority` are
excluded from gating. The mutable `plan/swarm/TASKS.json` bytes are never
hashed or pinned.

## Checkpoint scope: named by the census, not identified

The census reports two corpora, two formulations and two stages but does not map
file names or identities. No artifact count is asserted.

| Row | Corpus | Stage | Formulations reported | File names / revision / bytes / SHA-256 | Present |
| --- | --- | --- | --- | --- | --- |
| `CS-01` | VoiceBank+DEMAND | pretrained | 2, unmapped | none | no |
| `CS-02` | VoiceBank+DEMAND | corrective forcing | 2, unmapped | none | no |
| `CS-03` | WSJ0+WHAM | pretrained | 2, unmapped | none | no |
| `CS-04` | WSJ0+WHAM | corrective forcing | 2, unmapped | none | no |

## Enhancement acceptance profile

Pinned from `audio-benchmark-platform/plan/swarm/VERIFICATION.md`. No row is
satisfied; no missing result is promoted.

| Row | Requirement | Status |
| --- | --- | --- |
| `ENH-01` | Identity/noisy control plus an established task-matched baseline | blocked |
| `ENH-02` | Paired SI-SDR and STOI where permitted clean references exist | blocked |
| `ENH-03` | Clean-speech preservation, peaks and invalid outputs | blocked |
| `ENH-04` | Alignment, state, memory and measured content/availability timing | blocked |
| `ENH-05` | Separately labeled predictive screen or authorized listening | blocked |
| `ENH-06` | Quiet/active speech, idle noise, low SNR and onset/offset coverage | blocked |
| `ENH-07` | Separate paired, unpaired, synthetic, human and source-reported evidence | documented |

The synthetic envelope exercises only one deterministic placeholder frame, not
speech. It proves finite/peak/length plumbing on copied bytes and is explicitly
not an enhancement result.

## Fail-closed exercise (synthetic only)

`report.json:admission` records **90** actual rejections across strict JSON,
structure, model identity, runtime, command, asset, input, output, rights,
control and nonfinite groups. Exactly one structural schema control is admitted
to prove the validator is not blanket-rejecting; it is labelled
`synthetic_schema_control_not_evidence` and `qualifies=false`. No admission
case reads source, loads weights, imports a runtime, invokes a model or touches
audio.

`report.json:protocol_envelope` exercises a deterministic 160-sample
binary-fraction frame through the documented request/result shape:

- caller-owned bytes are copied, hash-checked and returned unchanged;
- input/output SHA-256 is the same 640-byte payload with peak `0.78125`;
- replay and reset-replay are byte-identical, close is idempotent and a
  post-close call is rejected with `adapter_closed`;
- **20** malformed/missing/nonfinite/out-of-range cases are rejected with zero
  calls and unchanged state, including a `NaN` payload, invalid hex and a step
  count outside `1..1024`.

This proves protocol plumbing only. It is not a diffusion/flow sampler, a
model, a checkpoint, an inference, a quality result or a qualification.

## Release gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `RG-01` source revision and license provenance | blocked | Stage both formulation snapshots at an immutable revision with complete license, notice, model-card and mapping records, then review independently. |
| `RG-02` pinned runtime and offline install | blocked | Provide a locked offline runtime with wheel hashes, install location, clean-room import digest and the exact sampler configuration. |
| `RG-03` checkpoint assets and per-file digests | blocked | Stage every checkpoint/config/metadata file for both corpora and both stages with verified byte counts and SHA-256. |
| `RG-04` rights-cleared inputs and training data | blocked | Freeze a permitted, digest-pinned input set with corpus, evaluation, derived-output and redistribution decisions plus training-data terms. |
| `RG-05` reference execution and output validity | blocked | Execute the pinned checkpoints offline and record output hashes, finite/length preservation, repeats, sampler settings and peak/RSS. |
| `RG-06` Enhancement profile against the real runtime | blocked | Run every profile case on a rights-cleared cohort with controls, baseline, SI-SDR/STOI, preservation and timing. |
| `RG-07` mode, platform, timing, resources and listening | blocked | Measure each mode/platform separately with latency, resources, pacing and authorized listening or a labeled screen. |
| `RG-08` provider intake, public surface and release | blocked | Open a separate versioned OFF-by-default intake with clean-install proof and independent exact-head review after all prior gates clear. |

No synthetic admission or envelope control opens a gate.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, pins, counts, commands, gates. |
| `LICENSES.md` | Source/checkpoint/runtime/input boundary; no vendored third-party text or bytes. |
| `contract.json` | Machine-readable contract: pins, checkpoint scope, artifacts, blockers, eight gates, Enhancement rows, admission schema, disposition. |
| `reference.py` | Stdlib-only strict JSON, pins, absence probes, inventory/snippet checks, admission validator, synthetic envelope, canonical report. |
| `run.py` | Byte-identical regeneration of `contract.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256`, repeated three times. |
| `report.json` | Canonical sorted-key compact JSON report; decision `DEFER`, `not_qualified`. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs and task-local artifacts. |
| `test_reference.py` | 41 deterministic unittest checks; no skips, network, runtime, checkpoint or audio. |
| `verify.py` | Read-only verifier: profile phrases, pins, report bytes/digest, gates, licensing, scope and three cold-start regenerations. |
| `*.license` | REUSE sidecars for generated JSON/digest artifacts. |

## Reproduce

From `docs/task-evidence/cof-denoising-checkpoints` with the pinned interpreter
and stdlib only:

```sh
export PYTHONDONTWRITEBYTECODE=1
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 run.py all
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 -m unittest -v test_reference.py
/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3 verify.py
```

From the SDK worktree root:

```sh
python3 -m reuse lint
git diff --check
```

Expected: `run.py` reports `repeat=3 byte_identical=true`; all 41 unittest
checks pass with 0 failed and 0 skipped; `verify.py` prints `PASS ... gates=8
blockers=6 ... cold_starts=3/3 byte_identical=true profile=Enhancement
status=incomplete decision=DEFER`; REUSE reports no missing or bad license;
`git diff --check` is clean. `verify.py` writes only to a temporary directory.

Current counts: 27 absence probes (16 workspace, 6 SDK worktree, 5 home; 0
present), 18 boundary/source pins, 7 required artifacts (1 evidence register
present, 6 blocked), 6 open blockers, 7 Enhancement rows (6 blocked, 1
documented, 0 real), 3 mode/platform rows, 90 admission rejections plus 1
schema-only control, 20 envelope rejections plus 1 lifecycle control, 8 blocked
gates, 0 qualifying results.

## Expected digest

`report.json` SHA-256:
`ff100450d2cabcddfd49c9d3c98ba06dfcc0c2191a71652ffb88485c44490e3a`.

`contract.json` object digest:
`b3d6457802ccd0097fcedbd76a20562415a5edbeb148b6573bc77e06fdbd3eea`.

## Separation from other evidence

No merged CoF package exists. `classical-wiener-denoising` is a model-free
synthetic enhancement reference and `cleanunet-dns-large-high` is a different
neural checkpoint blocker; both are pinned only as separate sibling boundaries.
Their fixtures, corpora, checkpoints and results are never substituted here.
The `pytorch-and-speechbrain-adapters` package is a separate runtime boundary
and is not pooled with this candidate. The census line remains source-reported
context, not measured evidence.
