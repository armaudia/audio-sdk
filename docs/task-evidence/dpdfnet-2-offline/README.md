<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DPDFNET-2-OFFLINE — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DPDFNet-2 offline` (`component_id=dpdfnet-2-offline`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before `processor_exposure`;
`evidence_status=incomplete`, `qualification_status=not_qualified`. A missing
result never qualifies the candidate.

The package models the offline boundary as a **caller-supplied external asset
reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an asset ID, byte
count, SHA-256 and `storage=external`, supplied by the caller, with no provider
file access and no download. The pinned candidate cannot cross that boundary
here. A deterministic stdlib **synthetic whole-clip surrogate** exercises only
the offline accounting and refusal mechanics; it is explicitly opt-in, is not
DPDFNet-2 and substitutes for no gate.

No candidate artifact was downloaded, loaded, built, vendored or invoked. No
weight, ONNX graph, `dpdfnet` package, ONNX Runtime, media, corpus, device clock,
listener, benchmark or release artifact is present or claimed. No public
API/ABI, `CONTRACTS.md`, descriptor, registry, installed default, shared build,
CI, board or handoff file changes. Only this task-local directory is added.

## Exact external blocker

The pinned ledger records `dpdfnet2.onnx` as **10,178,747 bytes**, SHA-256
`4f0ee28935b4a32abecc717d745416976565834d839601acf43031094b4dc94c`, under
source revision `dd6818d00f50c836fed43a6243ebe49116de5964` and package
`dpdfnet==0.6.0`. That is not enough to run or qualify it:

1. **Asset identity is not immutable.** The ledger's `model_revision` is
   `null` and `model_download_revision` is `main (mutable; retrieval-time commit
   not recorded)`. The exact bytes are known only by digest/byte count; no
   immutable artifact revision resolves them, and the asset is absent from this
   worktree.
2. **The offline runtime is absent and unpinned.** The offline whole-clip
   runtime is the external CPU ONNX `dpdfnet` 0.6.0 package. It is not installed
   here, has no pinned wheel/sdist digest in this worktree, and no vendor
   runtime is invoked.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   package and model card, but weight-specific terms, training-data provenance,
   redistribution and product-use clearance, and legal review are absent. No
   upstream portion may be copied, packaged, downloaded or redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target pacing/deadline measurement or approved exact offline reference
   vector.

**Reopen condition.** Admit the candidate only when the exact `dpdfnet2.onnx`
bytes are addressed by an immutable artifact revision plus byte count and
SHA-256 in a retrieval record and resolve from the caller's own storage; a
pinned `dpdfnet` 0.6.0 runtime artifact with a recorded digest installs in the
intended environment; written artifact-specific weight, runtime and
training-data terms plus a rights/redistribution decision exist; and a
rights-cleared cohort, independent scorer, permitted listening, exact whole-clip
offline reference outputs for these frozen inputs and target pacing/deadline
evidence are available. Until then all nine release gates stay `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `streaming_mode_added=false`, `processor_exposure=false`.
- The task-local `adapter.json` is a proposal descriptor, not a provider. It
  advertises `modes=["offline"]`, the external asset requirement,
  `whole_clip_only=true`, `streaming_supported=false` and
  `asset_readiness="blocked"`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no bytes are read and no download is
  attempted.

## Offline semantics modelled

The fixture models the boundary at one complete caller-owned clip of 1 to
160,000 samples; there is no incremental, streaming, flush or reset protocol.

- One `process_clip` call consumes the complete clip and returns exactly one
  output sample for every input sample. A second call fails with
  `offline_clip_already_complete`; there is no method to append, flush or reset.
- A partial final frame is zero-padded **only for gain estimation**; the padding
  is discarded and never emitted. The 32,123-sample control returns 32,123
  samples with 37 internal padding samples.
- The whole-clip gain path uses a non-causal six-frame (960-sample) smoothing
  window and a global noise reference. Extending a 16,000-sample prefix with
  future audio changes 13,117 of its first 16,000 output samples, so a prefix is
  not final before the full clip is supplied. `prefix_available_before_full_clip`
  is `false`.
- Processing the two halves independently changes 14,077 samples versus the
  whole clip. Independent segment processing is therefore not offline
  equivalent; the control is recorded, not hidden.
- An independent frame-loop path over the same gain sequence is byte-identical
  to the contiguous whole-clip path.
- A synthetic impulse probe preserves the peak index exactly
  (`input=4000`, `output=4000`). No algorithmic lag, content delay, latency or
  device timing is modelled or measured.
- Sessions are one-shot and stateless across clips: a fresh clip B is identical
  before or after clip A, replaying A is bit-identical, and no state is carried.
- Availability and all coordinates are source-sample positions on
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
| active_speech | 9.465938 | 10.373626 | +0.907688 | 9.428855 | 11.643358 | +2.214503 | -2.357213 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -18.416375 |
| low_snr_speech | -7.566055 | 0.963173 | +8.529227 | -7.555871 | -5.972759 | +1.583112 | -16.321200 |
| onset_offset | 13.403405 | 14.613191 | +1.209786 | 13.390136 | 14.702978 | +1.312842 | -0.710461 |
| quiet_speech | 12.428716 | 11.698028 | -0.730688 | 12.419033 | 13.646722 | +1.227689 | -1.986792 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the active-speech output at about 0.240.

### Honest regression

One regression is recorded verbatim in `report.json:regressions`:

| Condition | Metric | Noisy control | Surrogate | Delta |
| --- | --- | ---: | ---: | ---: |
| quiet_speech | snr_db | 12.428716 | 11.698028 | -0.730688 |

The global noise reference over-suppresses some low-level quiet-speech frames,
so total error rises even though SI-SDR improves. This is a property of the
synthetic fixture, not evidence about DPDFNet-2, and no threshold was tuned
against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_whole_clip` is the one-call whole-clip path; the independent
  `surrogate_frame_loop_control` must match it byte-for-byte.
- `surrogate_split_halves` must not match the whole clip; its difference is a
  boundary control, not a quality result.
- Config rejections: wrong sample rate, channels, sample format, frame size or
  maximum clip, unsupported streaming mode, surrogate without opt-in, and an
  unavailable caller asset all fail before instance creation. A fully pinned
  synthetic admission control is created to prove the admission branch; it is
  explicitly not the candidate.
- Clip rejections: empty, oversized, string, boolean, non-finite and
  out-of-range clips fail with unchanged status digests; a second clip and any
  post-close call fail closed.
- Lifecycle: one call only, close is idempotent, and there is no `process`,
  `flush` or `reset` streaming API to call.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, offline whole-clip surrogate, accounting, metrics and report model. |
| `run.py` | Regenerates `adapter.json`, `readiness.json`, `report.json`, `contract.json`, sidecars and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline adapter descriptor. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `test_reference.py` | 55 deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README-digest, reproduction, disposition, licensing and scope verifier. |
| `check_licensing.py` | Independent SPDX/REUSE and fail-closed file-set check. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate-matrix `DPDFNet-2 offline` record, evaluated offline scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | DPDFNet-2 offline description and source-reported pilot. |
| `source:adapters/dpdfnet/adapter.json` | `6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c` | Existing DPDFNet adapter identity and modes. |
| `source:adapters/dpdfnet/README.md` | `9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472` | DPDFNet package identity and wrapper provenance. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset digest, byte count, revisions and license metadata. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | DPDFNet-2 identity and measured offline scope. |
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

The pinned pilot records DPDFNet-2 offline mean ΔSNR +7.8522 dB (median
+7.2029, 95% descriptive interval [6.3114, 9.4949]), mean ΔSI-SDR +7.7973 dB
(median +7.1112, [6.2713, 9.4698]), mean ΔSTOI +0.0329 (median 0.0286,
[0.0231, 0.0434], 27/0/3 wins/ties/losses) and batch RTF 0.0989 on 30 DNS2020
pairs. The selected-candidate note separately records clean-input median STOI
0.9803 and distortion SNR 23.00 dB. `REALTIME_COMPONENT_CANDIDATES.md` records
an 800-sample (50 ms) content delay only for the experimental C++ streaming
backend; that value is **not applicable to the offline adapter** and is not
reproduced. All these values are transcribed only to preserve the separation
required by the Evidence profile and are not pooled with the synthetic numbers
above, not device timing and not a quality or release claim.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DPDFNET-2-OFFLINE diff --check
```

`run.py --all` regenerates the adapter, readiness, report, digest sidecar,
contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical.

The repository's installed-package gate is run from the SDK root on the exact
head:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- One complete whole-clip call per condition; 200 frames per full clip; no
  startup, tail or flush samples.
- Nine config adverse cases (eight rejections plus one synthetic admission
  control); nine clip adverse cases; all rejections leave status unchanged.
- 32,123-sample partial-tail control: 32,123 output samples, 37 internal
  padding samples discarded.
- Extending a 16,000-sample prefix to 24,000 changes 13,117 prefix samples;
  independent half-clip processing changes 14,077 samples.
- `report.json` SHA-256 and byte count are in the table below.
- Tests: **55 passed, 0 failed, 0 skipped** (Python 3.12.16).

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `adapter.json` | `5cb4d29771d95449f75a6bfd5553e1e4e87c9a52bfaae43ac52dcd68ffe71a3f` | 1188 |
| `check_licensing.py` | `7164f60c2b4e5426868564e7713d970e29960b811d1a787c43eed7357a9f3fb3` | 4137 |
| `readiness.json` | `e73d5b4c5074eb7959ac5d08a786c6a3b8ac0e473923d3f8906a33f024e39f48` | 3977 |
| `reference.py` | `0c3a2f6661c18fb00609d444ed7396dfca77c1e93c7f39ec4cafd1290437c561` | 59318 |
| `report.json` | `b5ab66036c59e47799a8f0a089cacd524f9389ebaf26c29c22fb109fea7368ce` | 31147 |
| `run.py` | `466519536f3d78fd88c24e9b9bdfa43eee42a76fb761e39626a81b4801bb1706` | 4617 |
| `test_reference.py` | `10a65d07a96297bb92b3560eeb21efcbd6ca17f4a03611f232c3583870304b5a` | 23692 |
| `verify.py` | `e8e3bd4e45be8799807a3d4ec2af4405eef27216776301a046483cdcf3ab09d9` | 30773 |
<!-- DIGEST_TABLE_END -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable artifact revision + byte count + SHA-256, caller-held bytes. |
| `runtime_admission` | blocked | Pinned `dpdfnet` 0.6.0 runtime artifact with digest and terms. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `exact_reference_parity` | blocked | Approved whole-clip offline reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target end-to-end timing, memory, pacing and deadline evidence. |
| `provider_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
