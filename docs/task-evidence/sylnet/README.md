<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SYLNET — task-local synthetic Rate-profile evidence

Proposal-only, incomplete and **not qualified** evidence for `SylNet`
(`component_id=sylnet`). The acceptance profile is **Rate**, assigned by
`plan/INVENTORY.json` and defined in `plan/swarm/VERIFICATION.md`. Decision:
**DEFER**, before `processor_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. Missing evidence never qualifies a
candidate.

This package applies the Rate profile to a **stdlib-only deterministic
surrogate** over caller-supplied frozen synthetic feature frames. It is **not**
SylNet source, does not load a checkpoint or weights, does not download or
vendor anything, does not read audio, does not invoke a vendor runtime, does
not render playback, does not measure a device clock or callback deadline,
does not conduct listening, does not benchmark the SDK and makes no release
claim. Every timestamp is a half-open source-sample coordinate on
`fixture-monotonic-not-device`. Evaluation fixture and any future production
callback path are distinct; no production callback is implemented.

## Exact blocker

The exact upstream identity is pinned: repository `shjang-97/SylNet` at commit
`29eb34d614907073735f9c2d8c31da22c1be2282`, its MIT `LICENSE`, the TF2 runner
and model source, checkpoint shards and normalization arrays, all by SHA-256
from the external research checkout. The pinned source, checkpoint, config and
weights are **not present in this SDK worktree**, no SylNet runtime is
installed, and product/redistribution and training-data rights are not cleared.
The MIT license covers the upstream repository snapshot as distributed; it is
not a product or redistribution clearance and no legal review exists. Nothing
was copied, vendored, built, downloaded or redistributed. The four exact
blockers are recorded verbatim in `contract.json:exact_blockers` and
`report.json:exact_blockers`; all release gates stay `blocked`. Real-model pilot
numbers below are provenance only and are never reproduced, pooled or used as
thresholds.

## Boundary

- Documented public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per
  frame; every frozen window is exactly 64,000 samples (400 full-sample slots),
  with 37 valid samples in the final slot of one condition.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `shared_cmakelists_change=false`, `installed_v0_behavior_change=false`,
  `processor_exposure=false`, `ci_change=false`.
- No provider registration, no installed-v0/ABI/registry/default/shared-build
  or CI change, no board or handoff write. Only this task-local directory is
  added.
- Configuration, window, shape, missing-feature, invalid, nonfinite, epoch,
  position, validity and lifecycle rejections fail closed without advancing
  surrogate state.

## Rate profile application

`report.json:rate_profile` pins the profile source and records three specified
rate cases (`1`, `4/5`, `5/4`) with exact target durations (`64000`, `80000`,
`51200` samples). No stretcher or renderer is executed: `renderer_executed`,
`duration_measured`, pitch, transient audibility and listening results are
explicitly unmeasured. `playback_buffering` is fixture queue accounting only;
it contains no measured deadline or device clock drift.

Seven frozen conditions (`speech`, `unfamiliar_speech`, `music`, `silence`,
`rebuffer`, `drift`, `tail_partial`) each have three rate cases. Every case
records exact source intervals, accepted frame intervals, fixture-clock
availability, thresholded nuclei proxy count and intervals, a frozen synthetic
target count, count/rate absolute error, unknown-frame accounting, exact final
partial coordinates and explicit unmeasured-metric fields. Counts are
synthetic proxies, not transcripts, corpus labels or preferred-speed targets.
The `drift` condition is a deterministic level shift across frozen feature
frames; it does not inject or measure a device clock drift.

## Controls and adverse cases

- `controls.identity`: no estimation; the 64,000-sample source interval is
  echoed exactly. Its zero count error is trivial by construction and is
  labeled as such.
- `controls.named_baseline`: a frozen constant-count control computed from the
  frozen synthetic targets; it is not a reproduction of the research
  constant-median baseline.
- `controls.mismatch`: wrong-window, stale-epoch and nonfinite inputs are
  actually fed to the surrogate and rejected with unchanged state.
- `adverse`: six config cases, ten frame cases (including missing and
  nonfinite features), one missing-final-frame case, two lifecycle cases and
  unknown-validity retention are produced by calling the validators; all
  rejections are recorded with stable reason codes and state digests.
- Regressions, including surrogate/target count disagreements and the
  constant-count control, are recorded verbatim; no losing result is hidden.

## Pinned sources and boundary

Paths prefixed `source:` in `SOURCES.sha256` are relative to
`/Users/htsakanyan/workspace/audio/audioml`; other paths are SDK-worktree
relative.

SDK, plan and research inputs:

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | SylNet task/profile assignment. |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` | SylNet row and pilot scope; provenance only. |
| `research/tsm-followup-20261101/root-baselines/REPORT.md` | `63ea22bd4d027467a1abe97639f7c9ff6e00cdc2c6c753a52c2bd5e4028bab85` | Shared-window pilot details; provenance only. |
| `research/tsm-followup-20261101/agent-neural/REPORT.md` | `f2f1b55234364eceff8b0626411590fbb97476cac918d9bf34138babc5820b73` | Exact upstream URL/commit/license and pilot runtime; provenance only. |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract. |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |

Upstream SylNet provenance, hash-pinned read-only from the external research
checkout (`data/checkouts/sylnet-evaluation`, commit
`29eb34d614907073735f9c2d8c31da22c1be2282`); no asset is copied into this
package or the SDK repository:

| Source | SHA-256 | Use |
| --- | --- | --- |
| `data/checkouts/sylnet-evaluation/LICENSE` | `d1442b2f494e4b639e8561912717c8082cef4989401f359a8134857fc514915c` | MIT license text, `Copyright (c) 2019 Shreyas Seshadri`. |
| `data/checkouts/sylnet-evaluation/README.md` | `7581fb7f5d6986dc2c2ff8e0542673451bb72394edcacab4784220f170849405` | Upstream usage, citation and runtime notes. |
| `data/checkouts/sylnet-evaluation/run_SylNet_tf2.py` | `d588b38a8bd38ce7b143e0e37660e22adaa9d295250b0248e15e086618683eb2` | Exact TF2 runner and front-end parameters. |
| `data/checkouts/sylnet-evaluation/SylNet_model_tf2.py` | `663b4c4b0984b86c378601ab1887dd4751859329b016ed0e6933d60b5f943f1e` | Exact model definition. |
| `data/checkouts/sylnet-evaluation/trained_models/model_trained.ckpt.data-00000-of-00001` | `90aabcf981a8a68ce9a8003565c51bb576e8787461d841af9c61d47f7d7ba1e3` | Pretrained checkpoint shard, 33,806,412 bytes. |
| `data/checkouts/sylnet-evaluation/trained_models/model_trained.ckpt.index` | `6076f70f9175ea35ed77fdb8f106053b6cad8aee7f2299a75e53ae44e31ae1a2` | Checkpoint index shard. |
| `data/checkouts/sylnet-evaluation/trained_models/model_trained.ckpt.meta` | `0577000a8dc3f48ff97c9f61012bfdfe44bc7bd006c58c1fcb74156efed86894` | Checkpoint graph metadata. |
| `data/checkouts/sylnet-evaluation/trained_models/means.npy` | `52813c80049b322b3224c9afa1c6e05fe30109520f528e2d9685fb0567ae3e01` | Feature normalization means. |
| `data/checkouts/sylnet-evaluation/trained_models/stds.npy` | `3ce79025350250bd423c8992b7e0148f9eb4d24c0166f15bd4c2d50cd8c31cca` | Feature normalization standard deviations. |
| `research/tsm-followup-20261101/agent-neural/run/sylnet-predictions.txt` | `28b4291e1adb1197735278a2a9c602aa6e4fc371acad34fe3b0d13c9be11b76f` | Pilot count predictions; not an approved reference vector. |
| `research/tsm-followup-20261101/agent-neural/run/sylnet-predictions_files.txt` | `b2787d4498b69430707741ed8d096edbb2e2ff563f876ff25a91b0f8e29ef77d` | Pilot prediction/file mapping. |

`SOURCES.sha256` enumerates every source, boundary and task-local artifact
pin, including the upstream provenance pins above. `verify.py` fails closed on
a missing, stale, malformed, duplicated or out-of-scope pin, non-canonical
JSON, duplicate keys, non-finite constants, a stale digest sidecar, uncaught
invalid cases, licensing gaps, unpinned task files and any worktree change
outside this directory.

## Licensing analysis

- Task files are `Apache-2.0` with REUSE SPDX headers/sidecars.
- Upstream repository source and tracked checkpoint files are under the pinned
  MIT `LICENSE` text at the exact commit; the MIT notice obligation is
  preserved by pinning, not by copying any upstream portion.
- No separate model-card, weights or checkpoint terms were found in the pinned
  snapshot. That absence is recorded, not treated as permission.
- Training-data provenance, product use, redistribution and legal review are
  **not established**. The rights gate stays `blocked`; no upstream asset is
  copied, vendored, built, packaged, downloaded or redistributed.

## Source-reported pilot values (provenance only)

The pinned top-level research report states count MAE 2.64 / RMSE 3.23 and rate
MAE 0.69 syllables/s, RMSE 0.85, r=0.894 on 210 four-second EN2003a windows
with dictionary-derived labels from one meeting and legacy-stack runtime
overhead. The pinned neural report records the same pilot as count MAE 2.643 /
RMSE 3.226, count bias +2.091, rate MAE 0.661, r=0.896, 88.03 s wall time for
210 clips, a 32 MB checkpoint in a 69 MB checkout, and Python 3.10.13 /
TensorFlow 2.12.0 runtime. The reports differ in rounding and one rate value;
both are transcribed as-is and neither is reproduced, pooled, resolved into a
threshold or used as a product claim.

## Files

- `contract.json` — task-local proposal manifest, scope, boundary, blockers.
- `reference.py` — deterministic stdlib surrogate, frozen frames and report model.
- `run.py` — byte-identical 3x regeneration of contract, report, sidecar and manifest.
- `report.json` / `report.json.sha256` — canonical evidence and digest.
- `SOURCES.sha256` — SHA-256 manifest for pinned upstream provenance, boundaries and task files.
- `test_reference.py` — Python unittest acceptance suite.
- `verify.py` — read-only pins/JSON/reproduction/invalid-case/licensing/scope verifier.
- `*.json.license`, `SOURCES.sha256.license` — REUSE sidecars for generated artifacts.

## Reproduction

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and the pinned
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
reuse lint
git -C <worktree> diff --check
```

`run.py` accepts `contract.json`, `report.json`, `sources` and `all`; every
target is regenerated three times and refused if any pass differs. The
canonical report digest is the content of `report.json.sha256`; the manifest
digest is the SHA-256 of `SOURCES.sha256` itself.

## Remaining gates (all blocked)

1. Pinned checkpoint/config/runtime present in the worktree plus
   product/redistribution and training-data rights clearance.
2. Rights-cleared held-out real speech cohort with exact labels.
3. Independent listening or user-preference labels; count proxies cannot qualify.
4. Target-runtime content/availability timing, memory and deadline evidence.
5. Opt-in provider intake, descriptor and catalog review.
6. Explicit public default selection.
7. Exact approved SylNet reference parity vector.

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
