<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM — Rate-controlled HiFi-GAN speech TSM blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local feasibility evidence for the
Rate-controlled HiFi-GAN speech TSM row. It is **not** a rate-controlled
HiFi-GAN implementation. There is **no candidate** to run: no exact method
source/implementation, task-matched checkpoint, pinned runtime, rights-cleared
corpus, generated waveform, listening result, device measurement, benchmark or
release claim is present. **No result here qualifies Rate-controlled HiFi-GAN
speech TSM.**

The structured inventory marks `rate-controlled-hifi-gan-speech-tsm` as
`evidence_status=blocked` with the **Rate** acceptance profile and disposition
`sdk-model` (`plan/INVENTORY.json`, component `rate-controlled-hifi-gan-speech-tsm`,
task `SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM`). The task mode is `feasibility`.
The pinned candidate-matrix row (45, Disfluency and TSM) states: “Exact method
source/implementation and task-matched checkpoint are absent from the current
worktree; no local inference, output, quality or performance result. Do not
substitute another neural stretcher.” The decision is **DEFER** before
`opt_in_provider_intake`.

## Exact external blocker

| Missing artifact | Exact requirement |
| --- | --- |
| Exact source/implementation | An immutable 40-hex revision or release tag of the exact rate-controlled HiFi-GAN speech TSM source, per-file SHA-256 manifest, reviewed LICENSE/notice bundle, and documented comparison against any derived module |
| Task-matched checkpoint | Caller-selected exact checkpoint/weights at immutable revision with release tag, byte count, SHA-256, declared format, sample rate, feature geometry, rate-control contract and state/drain behavior |
| Runtime | Locked isolated runtime with exact interpreter/framework/wheel digests, lock-file SHA-256, target platform, offline load path and recorded host profile |
| Rights and consent | Reviewed code, weight, model-card and training-data terms for evaluation, redistribution, customer deployment, public playback; consent and permitted output use for any voice material |
| Matched rate evidence | Rights-cleared cohort covering 1×, rate changes, unfamiliar speech, music, silence, rebuffer, drift and final partial window, with source/output mapping, duration, pitch, transient audibility, playback buffering, pause/filler timestamp behavior and speech preservation |
| Candidate results | Exact-runtime reference parity for frozen inputs, independent scoring/listening, and target-runtime first-output/tail/availability/pacing/deadline/memory measurements |

The machine-readable record is `report.json` and `contract.json`. Both carry
DEFER, `proposal_only_incomplete`, `not_qualified`, `qualification.status="not_qualified"`,
and eight blocked release gates.

## What this package verifies

1. **Absence evidence.** Fixed workspace probes are checked; no recursive walk.
   Any probe appearance fails verification so a stale “absent” claim cannot ship.
2. **Stable pins.** Pinned research/plan/boundary/sibling records are SHA-256
   pinned as read-only provenance inputs, not model evidence.
3. **Stable board identity.** Only the linked row's stable fields
   (`id`, `title`, `component`, `mode`, `repository`, `depends_on`, `write_scope`,
   `deliverable`, `acceptance`, `verification_profile`, `dispatch_priority`) are
   projected and hashed. The mutable `plan/swarm/TASKS.json` file is **never
   hashed**; status, owner, claim, review, handoff, blocked_reason, timestamps
   and history never enter canonical bytes and never gate this package.
4. **Fail-closed admission.** Caller-supplied `as_asset_v0` metadata requires
   asset ID, byte count and SHA-256 with `storage=external`; missing/unpinned/
   unsigned/non-admitted candidates are rejected before any processing. A
   synthetic structural control is admitted only as `candidate_asset=false` with
   `qualification_effect=none`.
5. **Adverse/missing/invalid/nonfinite rejection.** Wrong/missing/invalid asset
   metadata, missing opt-in, bad rate, wrong frame shape/type, nonfinite/NaN,
   out-of-range, bool payloads, post-flush/post-close operations are rejected
   without advancing state.
6. **Boundary preservation.** Installed v0 boundary files are pinned and
   verified unchanged. No provider registration, descriptor/registry/default,
   public API/ABI, shared build/CI, board or handoff change. No candidate
   source, weight or runtime downloaded/read/hashed/loaded/executed/bundled.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping, duration | blocked | No candidate output; surrogate rows are synthetic only and not qualifying. |
| Pitch, transient audibility | blocked | No candidate output, no listening, no transient metric on candidate. |
| Playback buffering | blocked | No device/runtime buffering measurement. |
| 1×, rate changes | blocked on candidate | Synthetic deterministic surrogate covers 0.75/1.0/1.25/1.5 for boundary accounting only. |
| Unfamiliar speech, music, silence | blocked on candidate | Synthetic conditions only; no rights-cleared real corpus. |
| Rebuffer, drift, final partial window | blocked | No playback/runtime measurement. |
| Pause/filler tied to source timestamps and speech preservation | blocked | No timestamped pause/filler policy or preservation measure on candidate. |

## Synthetic feasibility surrogate

The surrogate is deterministic, stdlib-only, and models only delay/rate-map
accounting/refusal mechanics. It uses a 160-sample hop and 1-frame lookahead as
**fixture parameters, not candidate geometry**. It is not a neural stretcher,
not HiFi-GAN, not rate-controlled HiFi-GAN speech TSM, and has
`qualification_effect=none`. Paired synthetic diagnostics are fixture
diagnostics only.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `tsm_invoked=false`,
  `sdk_data_dir_added=false`.
- Board is referenced by stable linked-row identity only
  (`tasks[id=SDK-RATE-CONTROLLED-HIFI-GAN-SPEECH-TSM]`, stable-field digest).
  The mutable full `plan/swarm/TASKS.json` is never hashed or pinned.

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
on any change outside `docs/task-evidence/rate-controlled-hifi-gan-speech-tsm/`.

## Digests

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `0b168443744f14f6228cf1d6865d52d830e1964b4036c5baadc046d65290fa55` | 44389 |
| `report.json` | `9d273c370d0fdc377929f03492d6180103d109ce1a93100e9d85b2a05a86163d` | 26630 |
| `report.json.sha256` | `58f5748172ff3052c607cfa0c246c8c84e90dd002ce88d772123e41170056a5c` | 78 |
| `run.py` | `481a3c481cfc3631bc7897e71298ec41f83812fc3d3d784b620323911f20dd9e` | 6157 |
| `test_reference.py` | `7aec3460d5516e15c725bdeee79d1135155be44645e1e69b3d62eb3d13e124f4` | 7756 |
| `verify.py` | `3e8fa9e178dd89ccce8ae37119ba8b7d8b45945cb7d9871ebcf83e312309d878` | 13953 |
<!-- DIGEST_TABLE_END -->
