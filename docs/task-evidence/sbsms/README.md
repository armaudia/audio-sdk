<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SBSMS — SBSMS blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local evidence for the SBSMS playback-speed
row. It is **not** an SBSMS implementation. There is **no SBSMS candidate**
executed here: no exact libsbsms source revision, commercial/licensing decision,
build/runtime, rights-cleared corpus, generated waveform, listening result,
device measurement, benchmark or release claim is present. **No result here
qualifies SBSMS.**

Pinned workspace records classify SBSMS as a TSM candidate with the **Rate**
acceptance profile (`plan/INVENTORY.json`, component `sbsms`, task `SDK-SBSMS`).
`cpp-library/pipeline-validation/playback-speed-candidates.md` marks SBSMS as
**Excluded** because libsbsms is GPL-2.0 and not usable in a closed-source product
without a separate licence from the author. The decision is **DEFER** before any
opt-in provider intake.

## Exact external blocker

| Missing artifact | Exact requirement |
| --- | --- |
| Exact source/licensing | Immutable libsbsms source revision or separately licensed commercial artifact, reviewed GPL-2.0/commercial terms, per-file SHA-256 manifest, and explicit SDK distribution decision |
| Pinned build/runtime | Isolated build/runtime with recorded toolchain/dependency digests, target platform, and deterministic reference outputs reproducible across three cold starts |
| Rights and consent | Reviewed code/licence terms for evaluation, redistribution, customer deployment, public playback; consent/output-use for any voice material |
| Matched rate evidence | Rights-cleared cohort covering 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window, with source/output mapping, duration, pitch, transient audibility, playback buffering, pause/filler timestamp behavior and speech preservation |
| Target-runtime measurements | First-output, tail, availability, pacing, deadline and memory measurements on the target runtime |
| Intake/default decision | Separate opt-in adapter/provider intake with OFF default and explicit owner default decision; no processor exposure without qualification |

The machine-readable record is `report.json` and `contract.json`. Both carry
DEFER, `proposal_only_incomplete`, `not_qualified`,
`qualification.status="not_qualified"`, and eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace probes are checked; no recursive walk.
   Any probe appearance fails verification so a stale “absent” claim cannot ship.
2. **Stable pins.** Pinned research/plan/boundary/sibling records are SHA-256
   pinned as read-only provenance inputs, not SBSMS evidence.
3. **Stable board identity.** Only the linked row's stable fields
   (`id`, `title`, `component`, `mode`, `repository`, `depends_on`,
   `write_scope`, `deliverable`, `acceptance`, `verification_profile`,
   `dispatch_priority`) are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**.
4. **Fail-closed admission.** Caller-supplied `as_asset_v0`-style metadata
   requires asset ID, byte count and SHA-256 with `storage=external`;
   missing/unpinned/unsigned/non-admitted candidates are rejected before any
   processing. A synthetic structural control is admitted only as
   `candidate_asset=false` with `qualification_effect=none`.
5. **Adverse/missing/invalid/nonfinite rejection.** Wrong/missing/invalid asset
   metadata, missing opt-in, bad rate, wrong frame shape/type, nonfinite/NaN,
   out-of-range, bool payloads, post-flush/post-close operations are rejected
   without advancing state.
6. **Boundary preservation.** Installed v0 boundary files are pinned and
   verified unchanged. No provider registration, descriptor/registry/default,
   public API/ABI, shared build/CI, board or handoff change. No SBSMS source,
   binary, runtime, corpus or media downloaded/read/hashed/compiled/executed.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping, duration | blocked | No SBSMS output; surrogate rows are synthetic only and not qualifying. |
| Pitch, transient audibility | blocked | No SBSMS output, no listening, no transient metric on candidate. |
| Playback buffering | blocked | No device/runtime buffering measurement. |
| 1×, rate changes | blocked on candidate | Synthetic deterministic surrogate covers 0.75/1.0/1.25/1.5 for boundary accounting only. |
| Unfamiliar speech, music, silence | blocked on candidate | Synthetic conditions only; no rights-cleared real corpus. |
| Rebuffer, drift, final partial window | blocked | No playback/runtime measurement. |
| Pause/filler tied to source timestamps and speech preservation | blocked | No timestamped pause/filler policy or preservation measure on candidate. |

## Synthetic feasibility surrogate

The surrogate is deterministic, stdlib-only, and models only delay/rate-map
accounting/refusal mechanics. It uses a 160-sample hop and 1-frame lookahead as
**fixture parameters, not SBSMS geometry**. It is not SBSMS, not WSOLA, not a
neural stretcher, and has `qualification_effect=none`.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `tsm_invoked=false`.
- Board is referenced by stable linked-row identity only
  (`tasks[id=SDK-SBSMS]`, stable-field digest). The mutable full
  `plan/swarm/TASKS.json` is never hashed or pinned.

## Reproduction

From this directory, with Python 3 standard library only:

```sh
python3 reference.py
python3 -m unittest -v test_reference.py
python3 run.py --all
python3 verify.py
python3 -m reuse lint
```

`verify.py` runs `run.py --digest` three times from a cold start, requires one
byte-identical digest, and compares it with `report.json.sha256`. It also fails
on any change outside `docs/task-evidence/sbsms/`.

## Digests

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `eb028d5e561737985fc9af20d716b30c51563c7a9667cfbb600d1b9b74b44c00` | 39561 |
| `report.json` | `f260eb98a0c359f1f7bd831defae80ba07b02e84c602c73fa6e49232f6761225` | 22722 |
| `report.json.sha256` | `ff38614bfc29489ea071697ba465398a6f4019a7d597a91b7fca786cada2f9a1` | 78 |
| `run.py` | `90fb45d78c70ad8b3dfed6a45a59b222d551dd6471849fad0c8d761986043092` | 5963 |
| `test_reference.py` | `04a52a2c412e7bd4b6ab5dd2119258b2a802949728a0752834670c42483ae1b3` | 7403 |
| `verify.py` | `cdbaa9290d24d572944dc92b16a150a8d22f91a8787e74dd16805f6cda1d778b` | 13940 |
<!-- DIGEST_TABLE_END -->
