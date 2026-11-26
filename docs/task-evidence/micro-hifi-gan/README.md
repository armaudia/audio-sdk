<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MICRO-HIFI-GAN — Micro-HiFi-GAN feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local feasibility evidence for the
Micro-HiFi-GAN row. It is **not** a Micro-HiFi-GAN implementation. There is **no
candidate** to run: no official source checkout, generator checkpoint, acoustic
feature contract, PyTorch/ONNX runtime, corpus, voice pair, generated waveform,
listening result, device measurement, benchmark or release claim is present.
**No result here qualifies Micro-HiFi-GAN.**

The structured inventory marks `micro-hifi-gan` as `evidence_status=considered`
with the **Voice** acceptance profile and disposition `sdk-model`
(`plan/INVENTORY.json`). The task mode is `feasibility`. Its deliverable asks the
owner to verify runnable source, exact assets, permitted scope, task geometry and
matched evidence before reproducing the exact model/runtime as a
caller-supplied-asset reference and adding an opt-in adapter. Feasibility fails
at every prerequisite, so the documented decision is **DEFER** before
`opt_in_provider_intake`.

## Exact external blocker

The pinned research record is a negative run record, not candidate evidence:

> `research/accent-conversion-20261101/README.md` line 169 — **Micro-HiFi-GAN |
> Not run.** Vocoder component only; pruning/causal claims do not establish
> end-to-end accent conversion latency. **No compatible checkpoint acquired.**

The inventory carries the same finding. No source repository, revision, LICENSE
digest, weight byte count, SHA-256, release tag, runtime lock or rights entry is
recorded. A fixed probe set covers the likely checkout, model, runtime, rights,
cohort and parity paths; **all probes are absent** and nothing was fabricated,
reconstructed, mirrored, downloaded or substituted.

| Missing artifact | Exact requirement |
| --- | --- |
| Official source checkout | An immutable 40-hex revision of the exact Micro-HiFi-GAN source, a per-file SHA-256 manifest from a reviewable tree, and reviewed upstream LICENSE and notice text |
| Generator checkpoint | The caller-selected Micro-HiFi-GAN generator at an immutable revision, with release tag, byte count, SHA-256, selected format (PyTorch/ONNX), declared sample rate, feature configuration, upsample layout, pruning schedule and state behaviour |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter, framework, wheel digests, lock-file SHA-256, target platform, offline load path and recorded host profile |
| Rights and scope | Reviewed code, weight, model-card and training-data terms that settle attribution, evaluation, redistribution, customer deployment, public playback and generated-output use |
| Voice cohort | A frozen, rights-cleared paired cohort with permitted source and target references, language and speaker groups, held-out splits, consent and output-use permission |
| Matched task evidence | A fixed upstream acoustic feature contract and an end-to-end accent-conversion context that isolates the vocoder; a vocoder alone does not transform voice or accent, and pruning/causal claims are not end-to-end latency evidence |
| Candidate results | Exact-runtime reference parity for frozen inputs, independent semantic-preservation, speaker-identity and naturalness scoring, permitted listening, alignment, first-output/tail timing, state, memory, availability and resources |

The machine-readable record is `report.json` → `feasibility`, `absence_audit`,
`asset_boundary`, `asset_admission`, `workspace_observations`, `rights`,
`voice_profile`, `native_evidence`, `exact_blockers` and `release_gates`.
`contract.json` carries the same disposition, absent geometry, pins and all
eight blocked release gates.

## Feasibility conclusion

`report.json:feasibility` records the pinned basis:

- `plan/INVENTORY.json` component `micro-hifi-gan`, disposition `sdk-model`,
  area “Voice and synthesis”, profile `voice`, finding **“Not run. Vocoder
  component only; pruning/causal claims do not establish end-to-end accent
  conversion latency. No compatible checkpoint acquired.”**
- `research/accent-conversion-20261101/README.md` line 169 repeats the negative
  row in the accent-conversion candidate table.
- No source, weight, runtime, rights, consent, geometry or matched voice
  evidence exists locally, so a caller-supplied-asset reference cannot be built
  and an opt-in adapter cannot be admitted.

The decision is therefore **DEFER**. A comparison was neither retained nor
reproduced, because there is **no candidate** to run. This is not a negative
quality result; it is an evidence and feasibility blocker.

## What this package verifies

1. **Absence evidence.** Fixed workspace and home-cache probes are checked; no
   recursive walk is performed. All candidate probes are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears, so
   a stale “absent” claim cannot be shipped.
2. **No observed workspace copy.** No Micro-HiFi-GAN source or derived module
   was found anywhere in the workspace. The observed-copy list is empty and is
   re-checked; no copy is admitted to any gate.
3. **Stable pins.** The research record, planning records, rights register and
   SDK boundary files are pinned by SHA-256, plus the merged sibling
   `hifi-gan-vocoder` and `vocos` READMEs as adjacent boundary references. These
   are read-only provenance inputs, not model evidence.
4. **Stable board identity.** Only the linked row's `id`, `title`, `repository`,
   `mode`, `component`, `depends_on`, `write_scope`, `deliverable`,
   `acceptance`, `evidence` and `dispatch_priority` are projected and hashed.
   The mutable `plan/swarm/TASKS.json` file is **never hashed**; status, owner,
   claim, review, handoff, blocked reason, timestamps and history never enter
   canonical bytes and never gate this package.
5. **Fail-closed admission.** The caller-supplied `as_asset_v0` boundary
   requires an asset ID, byte count and SHA-256 with `storage=external`; a
   missing, unpinned, unsigned or non-admitted candidate is rejected before any
   processing. One synthetic structural control is accepted to prove the
   validator is not blanket-rejecting; it is explicitly `candidate_asset=false`,
   is not Micro-HiFi-GAN and has `qualification_effect=none`.
6. **Adverse, missing, invalid and nonfinite rejection.** Wrong model, rate,
   channels, format, feature bins, hop, lookahead, delay, state layout, target
   condition and consent are rejected; empty, oversized, string, boolean,
   negative, out-of-range, nonfinite and repeated streams are rejected;
   malformed, nonfinite and out-of-range states and frames are rejected without
   advancing state.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the root `README.md` and the
   Apache-2.0 license are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No Micro-HiFi-GAN
   provider is installed or registered; no descriptor, default, ABI, shared
   build, CI, board or handoff change is made.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Frozen permitted input and target references | blocked | No rights-cleared source/target references, consent or output-use permission. |
| Task and language/speaker groups | blocked | No task-matched cohort, language grouping or held-out split. |
| Text/semantic content preserved | blocked | No candidate output, transcript or independent semantic scorer. |
| Identity/similarity | blocked | No target reference, independent identity model or similarity result. |
| Naturalness | blocked | No naturalness assessment, score or permitted listening panel. |
| Alignment, first-output and tail timing | blocked | No candidate output or exact-runtime timing on the target condition. |
| Exact target condition | blocked | Code, weight, features, runtime and corpus versions are all unpinned. |
| Consent, reference availability and output use | blocked | Independent gates; none is recorded. |

## Synthetic feasibility surrogate

The surrogate mirrors only delay, accounting and refusal mechanics.

- Fixed synthetic 80-bin feature frames, a 160-sample output hop and a declared
  two-frame lookahead/delay. These are fixture parameters, **not** candidate
  geometry.
- One delayed feature queue. Payloads are fixture values, not model tensors or
  candidate state. Candidate geometry fields are recorded as `null`.
- Each frame returns the delayed frame; the first 320 output samples are invalid
  startup, matching the declared fixture buffering delay. Two zero flush frames
  release the tail within the declared maximum of two calls and 320 samples.
- A 7-frame control returns exactly 1,120 samples; a partial tail is not
  dropped. A single-frame impulse at source frame 8 first appears at the
  source-aligned output sample `8*160 = 1280` after the declared 320-sample
  startup-invalid prefix, preserving delay and content mapping.
- Frame-loop and whole-stream drivers are byte-identical; split-half driving is
  deliberately different, proving the state boundary is exercised.
- Outputs are finite, bounded and deterministic. Paired synthetic SNR/SI-SDR
  values are fixture diagnostics only and are not semantic, identity or
  naturalness evidence.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `vocoder_invoked=false`,
  `sdk_data_dir_added=false`. No proposal `adapter.json` or `readiness.json` is
  added; machine-readable state lives in `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-MICRO-HIFI-GAN]`, stable-field digest). The mutable full
  `plan/swarm/TASKS.json` is never hashed or pinned.
- No candidate source, weight or runtime was downloaded, read, hashed, loaded,
  compiled, executed or bundled.

## Reproduction

From this directory, with Python 3 standard library only:

```sh
python3 reference.py            # imports the deterministic boundary/surrogate
python3 -m unittest -v test_reference.py
python3 run.py --all            # report, README table, contract, SOURCES.sha256
python3 verify.py               # strict read-only verification
python3 -m reuse lint           # repository licensing gate
```

`verify.py` runs `run.py --digest` three times from a cold start, requires one
byte-identical digest, and compares it with `report.json.sha256`. It also fails
on any change outside `docs/task-evidence/micro-hifi-gan/` and on a drifted
stable board projection.

## Digest table

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `02d9940a51d42a17f873694cddd673227b41f7a5ac6314f8ac1e45486d794f7c` | 92179 |
| `report.json` | `c7dfee4c7f346bc91446697bc58ccb58f3971b3fad24814541fee7c567db8891` | 51007 |
| `report.json.sha256` | `eb84d3c6eefa25606b479d8ae396f34302f9fcdb3f52fa9a52f681a82094c43a` | 78 |
| `run.py` | `6b6a302f7933f489ecdf30b64c1dd27417ee2f3dcb3ca7bf6a929116471ebaec` | 6377 |
| `test_reference.py` | `1f4a668f88ed2b57544ec3bfa808697b1f33f27e04e73dea2f06e0c9bdab93d8` | 32831 |
| `verify.py` | `dd5003da05414bbde0eb48cae5d631edff4f293733837f2af05c958ad774e9b1` | 28098 |
<!-- DIGEST_TABLE_END -->
