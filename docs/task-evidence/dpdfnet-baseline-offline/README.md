<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DPDFNET-BASELINE-OFFLINE — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DPDFNet baseline offline` (`component_id=dpdfnet-baseline-offline`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline boundary as a **caller-supplied external asset
reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an asset ID, byte
count, SHA-256 and `storage=external`, supplied by the caller, with no provider
file access and no download. The pinned candidate cannot cross that boundary
here. A deterministic stdlib **synthetic whole-clip surrogate** exercises only
the offline accounting and refusal mechanics; it is explicitly opt-in, is not
DPDFNet, and substitutes for no gate.

No candidate artifact was downloaded, loaded, built, vendored or invoked. No
weight, ONNX graph, `dpdfnet` package, ONNX Runtime, media, corpus, device clock,
listener, benchmark or release artifact is present or claimed. There is no candidate
output or result. No public API/ABI, `CONTRACTS.md`, descriptor,
registry, installed default, shared build, CI, board or handoff file changes.
Only this task-local directory is added.

## Exact external blocker

The pinned ledger records `data/models/dpdfnet/baseline.onnx` as **8,722,707
bytes**, SHA-256
`371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0`, under source
revision `dd6818d00f50c836fed43a6243ebe49116de5964` and package
`dpdfnet==0.6.0`. That is not enough to run or qualify it:

1. **Asset identity is not immutable.** The ledger's `model_revision` is
   `null` and `model_download_revision` is `main (mutable; retrieval-time commit
   not recorded)`. The exact bytes are known only by digest/byte count; no
   immutable artifact revision resolves them, and the asset is absent from this
   worktree.
2. **The offline runtime is absent and unpinned.** The offline whole-clip
   runtime is the external CPU ONNX `dpdfnet` 0.6.0 package. It is not installed
   here, has no pinned wheel/sdist digest in this worktree, and no vendor runtime
   or ONNX Runtime is invoked.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   package and model card, but weight-specific terms, training-data provenance,
   redistribution and product-use clearance, and legal review are absent. No
   upstream portion may be copied, packaged, downloaded or redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target pacing/deadline measurement or approved exact offline reference
   vector.

**Reopen condition.** Admit the candidate only when the exact `baseline.onnx`
bytes are addressed by an immutable artifact revision plus byte count and
SHA-256 in a retrieval record and resolve from the caller's own storage; a
pinned `dpdfnet` 0.6.0 runtime artifact with a recorded digest installs in the
intended environment; written artifact-specific weight, runtime and
training-data terms plus a rights/redistribution decision exist; and a
rights-cleared cohort, independent scorer, permitted listening, exact whole-clip
offline reference outputs for these frozen inputs and target pacing/deadline
evidence are available. Until then all eight release gates stay `blocked`.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `streaming_mode_added=false`. No proposal `adapter.json` or `readiness.json`
  is added; machine-readable state lives in `contract.json` and `report.json`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no bytes are read and no download is
  attempted. The candidate asset is reported absent.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-DPDFNET-BASELINE-OFFLINE]`, stable-field digest). The mutable
  full `plan/swarm/TASKS.json` is never hashed or pinned.

## Offline semantics modelled

The fixture models the boundary at one complete caller-owned clip of 1 to
160,000 samples; there is no incremental, streaming, flush or reset protocol.

- One `process_clip` call consumes the complete clip and returns exactly one
  output sample for every input sample. A second call fails with
  `offline_clip_already_complete`; there is no method to append, flush or reset.
- A partial final frame is zero-padded **only for gain estimation**; the padding
  is discarded and never emitted. The 32,123-sample control returns 32,123
  samples with 37 internal padding samples discarded.
- The whole-clip gain path uses a non-causal six-frame (960-sample) smoothing
  window and a global noise reference. Extending a 16,000-sample prefix with
  future audio changes all 16,000 prefix samples, so a prefix is not final
  before the full clip is supplied. `prefix_not_final_before_full_clip` is
  `true`.
- Processing the two halves independently changes all 32,000 samples versus the
  whole clip. Independent segment processing is therefore not offline
  equivalent; the control is recorded, not hidden.
- An independent frame-loop path over the same gain sequence is byte-identical
  to the contiguous whole-clip path.
- A synthetic impulse probe preserves the peak index exactly
  (`input=4000`, `output=4000`). No algorithmic lag, content delay, latency or
  device timing is modelled or measured.
- Sessions are one-shot and stateless across clips: replaying a clip is
  bit-identical, and no state is carried. Availability and all coordinates are
  source-sample positions on
  `fixture-sample-coordinate-not-device`. There is no wall clock, device clock,
  callback deadline, paced workload or end-to-end latency measurement.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on a common full output length, peak/clipping/nonfinite
checks and explicit unmeasured fields. STOI is `blocked_unmeasured` (no
rights-cleared clean-reference cohort and no installed scorer), clean-speech
preservation is `synthetic_only`, state/memory is `stateless_synthetic_only`,
content/availability timing is `blocked_unmeasured`, listening is `not_run`,
and real runtime/real clean references are `false`.

### Synthetic fixture results (not a candidate result)

Scores are computed on the same 32,000-sample whole clip for every variant. They
describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 6.953471 | 7.268239 | +0.314768 | 6.961875 | 6.959015 | -0.002860 | -3.061784 |
| quiet_speech | 4.553064 | 5.810360 | +1.257296 | 4.533636 | 4.532138 | -0.001498 | -3.057238 |
| low_snr_speech | -5.176332 | -2.370990 | +2.805342 | -5.230262 | -5.230312 | -0.000050 | -3.036937 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -3.031852 |
| onset_offset | 3.218529 | 5.763223 | +2.544694 | 3.175917 | 4.695777 | +1.519859 | -1.895552 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the low-SNR output at about 0.471.

### Honest regressions

Three small SI-SDR regressions are recorded verbatim in
`report.json:regressions`: `active_speech` -0.002860 dB, `quiet_speech`
-0.001498 dB and `low_snr_speech` -0.000050 dB versus the noisy control. The
global noise reference slightly distorts some low-energy frames, so SI-SDR falls
even while SNR improves. These are properties of the synthetic fixture, not
evidence about DPDFNet, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_whole_clip` is the one-call whole-clip path; the independent
  `surrogate_frame_loop_control` must match it byte-for-byte.
- `surrogate_split_halves` must not match the whole clip; its difference is a
  boundary control, not a quality result.
- Config rejections: wrong sample rate, channels, sample format, frame size or
  maximum clip, unsupported streaming mode, unavailable candidate asset, altered
  asset identity/byte count, and surrogate without opt-in all fail before
  instance creation. A fully pinned synthetic admission control is created to
  prove the admission branch; it is explicitly not the candidate and has
  `qualification_effect=none`.
- Clip rejections: empty, oversized, string, boolean, non-finite, infinite and
  out-of-range clips fail with unchanged state digests; a second clip and any
  post-close call fail closed.
- Lifecycle: one call only, close is idempotent, and there is no `process`,
  `flush` or `reset` streaming API to call.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, offline whole-clip surrogate, accounting, metrics and report/contract model. |
| `run.py` | Regenerates `report.json`, its sidecar, the README digest table, `contract.json` and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `test_reference.py` | Deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README-digest, reproduction, disposition, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate-matrix `DPDFNet baseline offline` record. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | DPDFNet baseline description and source-reported pilot. |
| `source:adapters/dpdfnet/adapter.json` | `6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c` | Existing DPDFNet adapter identity and modes. |
| `source:adapters/dpdfnet/README.md` | `9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472` | DPDFNet package identity and wrapper provenance. |
| `source:adapters/dpdfnet/run.py` | `40fbd148eb80ec21a33290e4cb4bc9258afb54f65d4d5fd5d82b552deac5ae02` | Exact offline/streaming wrapper and 640-sample lag handling. |
| `source:adapters/dpdfnet/requirements.lock` | `2d43db167c1c221992ac51bd15ae365bfc18ddc21eb405c53ce8a444e5af34a4` | Recorded CPython 3.11 runtime lock including `dpdfnet==0.6.0`. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset digest, byte count, revisions and license metadata. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | DPDFNet baseline identity and measured offline scope. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Offline pilot summary and separate streaming C++ delay note. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported paired pilot values; provenance only. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned pilot records DPDFNet baseline offline median SNR gain +6.754 dB
(median output SNR 17.883 dB), mean ΔSNR +7.6605 dB (95% descriptive interval
[6.0901, 9.3366]), mean ΔSI-SDR +7.5800 dB ([5.9960, 9.2770]), median STOI
0.9691, mean ΔSTOI +0.0288 ([0.0186, 0.0395], 25/0/5 wins/ties/losses) and
median RTF 0.0421 on 30 DNS2020 pairs. The selected-candidate note separately
records clean-input median STOI 0.9883 offline / 0.9884 streaming and an
offline-minus-streaming mean ΔSNR of +0.3773 dB ([0.1996, 0.5778]).
`REALTIME_COMPONENT_CANDIDATES.md` records an 800-sample (50 ms) content delay
only for the experimental C++ streaming backend, and the adapter records a
640-sample (40 ms) compensated streaming lag; neither is applicable to the
offline adapter and neither is reproduced. All these values are transcribed
only to preserve the separation required by the Evidence profile and are not
pooled with the synthetic numbers above, not device timing and not a quality or
release claim.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DPDFNET-BASELINE-OFFLINE diff --check
```

`run.py --all` regenerates the report, digest sidecar, README digest table,
contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical; the test suite performs the full
three-run regeneration in an isolated copy.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- One complete whole-clip call per variant per condition; 200 frames per full
  clip; no startup, tail or flush samples in the emitted output.
- Eleven config adverse cases (ten rejections plus one synthetic admission
  control); nine clip adverse cases; all rejections leave state unchanged.
- 32,123-sample partial-tail control: 32,123 output samples, 37 internal
  padding samples discarded.
- Extending a 16,000-sample prefix to 32,000 changes all 16,000 prefix samples;
  independent half-clip processing changes all 32,000 samples.
- `report.json` SHA-256 and byte count are in the table below.
- Eight release gates, all `blocked`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `c21b1c1a68e1d9a147e64eec3147da70bc2c45835716fae812fed22ea098029e` | 55532 |
| `report.json` | `6efa40dd8d98db63bd6f2d2c4063294227e365fee8b216301900eab455ff0940` | 34651 |
| `report.json.sha256` | `d8b9d7b59ed2b3a20f1e43ad1083494456310f97bf567076ca45d73f5c8cb369` | 78 |
| `run.py` | `833703b983b3fd23143ac8d767a62562bbd9c65ac5fe3ef5fd3358d8ee34cad7` | 6004 |
| `test_reference.py` | `4a70c5f8c296994035fa04e2d9e00846f0ea872f72e639521955cccf6aba9943` | 23634 |
| `verify.py` | `4e86672fc83e0e8da42f50b5e00a90e09be859adf1bff23aed41b5899266b2f7` | 15991 |
<!-- DIGEST_TABLE_END -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable artifact revision + byte count + SHA-256, caller-held bytes. |
| `runtime_admission` | blocked | Pinned `dpdfnet` 0.6.0 runtime artifact with digest and terms. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `exact_reference_parity` | blocked | Approved whole-clip offline reference outputs for the frozen inputs. |
| `rights_cleared_paired_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target end-to-end timing, memory, pacing and deadline evidence. |
| `provider_intake_and_default_selection` | blocked | Opt-in provider intake, OFF default, review and explicit default decision. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
