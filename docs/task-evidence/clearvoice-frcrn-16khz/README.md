<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CLEARVOICE-FRCRN-16-KHZ — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ClearVoice FRCRN 16 kHz` (`component_id=clearvoice-frcrn-16-khz`). The acceptance
profile is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before `processor_exposure`;
`evidence_status=incomplete`, `qualification_status=not_qualified`. A missing
result never qualifies the candidate.

The package models the offline whole-clip boundary as a **caller-supplied
external asset reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an
asset ID, byte count, SHA-256 and `storage=external`, supplied by the caller,
with no provider file access and no download. The pinned candidate cannot cross
that boundary here. A deterministic stdlib **synthetic surrogate** exercises only
the whole-clip boundary mechanics; it is explicitly opt-in, is not ClearerVoice
FRCRN and substitutes for no gate.

Nothing was downloaded, loaded, built, vendored or invoked. No checkpoint,
pointer, PyTorch graph, `clearvoice` package, media, corpus, device clock,
listener, benchmark or release artifact is present or claimed. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build, CI, board
or handoff file changes. Only this task-local directory is added.

## Exact external blocker

The pinned ledger records `FRCRN_SE_16K/last_best_checkpoint.pt` as
**161,053,751 bytes**, SHA-256
`b22256adbb91b68cf5a3db8f6657a4fb17066eecd5f069803e59c186c1cf3ebb`, and a
24-byte `FRCRN_SE_16K/last_best_checkpoint` pointer, SHA-256
`315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0`, under
ClearerVoice source revision `3766e6a64b0d8cb58f08d913d617bf129f11ed53`. That
is not enough to run or qualify the candidate:

1. **Asset identity is not immutable.** The ledger records no immutable model
   artifact revision (`model_revision` is absent) and no retrieval-time download
   commit. The checkpoint bytes are known only by digest/byte count, the 24-byte
   pointer content is not verified against `last_best_checkpoint.pt`, and
   neither artifact is present in this worktree.
2. **The runtime is absent and unpinned.** The runtime is the external
   `clearvoice` 0.1.2 package (`ClearerVoice-Studio-clearvoice-0.1.2`) with
   PyTorch and the adapter's pinned requirements lock. It is not installed here,
   has no pinned wheel/sdist digest in this worktree, and
   `adapters/clearvoice/run.py` is not executed.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   code and model card, but the model card states open and private training data
   with exact corpus exposure undisclosed. Weight-specific terms,
   training-data provenance, redistribution and product-use clearance, and legal
   review are absent. No upstream portion may be copied, packaged, downloaded or
   redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target-runtime timing measurement or approved exact FRCRN reference vector.

**Reopen condition.** Admit the candidate only when the exact `FRCRN_SE_16K`
checkpoint bytes are addressed by an immutable model artifact revision plus byte
count and SHA-256 in a retrieval record; the 24-byte pointer content is verified
to name the checkpoint; both resolve from the caller's own storage; a pinned
`clearvoice` 0.1.2 runtime with a recorded digest installs and runs
`adapters/clearvoice/run.py` under the requirements lock; written
artifact-specific terms and a rights/redistribution decision exist; and a
rights-cleared cohort, independent scorer, permitted listening, exact reference
outputs for these frozen inputs and target timing evidence are available. Until
then all nine release gates stay `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `processor_exposure=false`.
- The task-local `adapter.json` is a proposal descriptor, not a provider. It
  advertises `modes=["offline"]`, the external checkpoint plus pointer
  requirement and `asset_readiness="blocked"`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no bytes are read and no download is
  attempted.
- The upstream configuration fields are modelled exactly:
  `model_name`, `package_version`, `model_revision`, `checkpoint_dir`,
  `checkpoint_file`, `checkpoint_sha256`, `sample_rate`.

## Offline semantics modelled

The fixture models the boundary at the upstream adapter's offline contract:

- Input is mono 16 kHz `f32` in `[-1, 1]`. Empty, oversized, string, boolean,
  non-finite and out-of-range samples are rejected before state changes.
- Caller chunks are buffered and the whole clip is enhanced once at `finish()`.
  Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280` and a single 32,000-sample
  call all produce **identical** output digests, so the result is independent of
  caller chunking.
- The output has exactly the input length (`valid_samples=32000`), identity
  source-time mapping, `delay_compensation_samples=0` and `padded_samples=0`.
  The declared algorithmic lag is **0**; no latency is measured.
- A partial final frame is zero-padded **only for gain estimation**; it is
  counted as `internal_frame_padding_samples` and never emitted. The dedicated
  probe feeds 32,123 samples, reports 37 internal padding samples and returns
  32,123 output samples.
- A complete clip is required: `finish()` after `finish()` is rejected, and a
  second clip needs an explicit `reset()`. `reset` restores the exact initial
  state and replay is bit-identical. A fresh independent session produces the
  same per-chunk state digest chain, and a foreign feed after `reset` is
  bit-identical to a fresh session.
- The 24-byte pointer is modelled as a required auxiliary artifact whose
  stripped text must equal `last_best_checkpoint.pt`; its content is **not**
  verified in this worktree.
- Availability and all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`. There is no wall clock, device clock,
  callback deadline, paced workload or latency measurement.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on the full clip, peak/clipping/nonfinite checks and
explicit unmeasured fields. STOI is `blocked_unmeasured` (no rights-cleared
clean-reference cohort and no installed scorer), clean-speech preservation is
`synthetic_only`, state/memory is `synthetic_state_only`, content/availability
timing is `blocked_unmeasured`, listening is `not_run`, and real runtime/real
clean references are `false`.

### Synthetic fixture results (not a candidate result)

Scores are computed on the same 32,000-sample clip for every variant. They
describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 9.500643 | 9.635843 | +0.135200 | 9.467575 | 10.256624 | +0.789049 | -2.308958 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -17.599896 |
| low_snr_speech | -7.584471 | 0.674391 | +8.258862 | -7.652977 | -7.731061 | -0.078084 | -17.183548 |
| onset_offset | 13.466509 | 14.397407 | +0.930898 | 13.449036 | 14.382898 | +0.933862 | -0.636153 |
| quiet_speech | 12.403286 | 10.457858 | -1.945428 | 12.412695 | 11.590559 | -0.822136 | -2.098753 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the active-speech output at about 0.243.

### Honest regressions

Three regressions are recorded verbatim in `report.json:regressions`:

| Condition | Metric | Noisy control | Surrogate | Delta |
| --- | --- | ---: | ---: | ---: |
| quiet_speech | snr_db | 12.403286 | 10.457858 | -1.945428 |
| quiet_speech | si_sdr_db | 12.412695 | 11.590559 | -0.822136 |
| low_snr_speech | si_sdr_db | -7.652977 | -7.731061 | -0.078084 |

The fixture uses the 56th percentile of frame power as a naive noise floor, so
quiet speech is over-suppressed and the low-SNR waveform is not preserved
exactly. This is a property of the synthetic fixture, not evidence about FRCRN,
and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_offline_chunked_160` is the 160-sample caller feed; the
  `surrogate_offline_whole_clip` control must match it byte-for-byte.
- Config rejections: wrong sample rate, channels, sample format, model name or
  package version, unsupported mode, surrogate without opt-in, an unavailable
  caller asset and a wrong checkpoint digest all fail before instance creation.
  A fully pinned synthetic admission control is created to prove the admission
  branch; it is explicitly not the candidate.
- Frame rejections: empty, oversized, string, boolean, non-finite and
  out-of-range chunks fail with unchanged state digests.
- Lifecycle: process after finish/close, finish after finish/close and reset
  after close are rejected; close is idempotent; a zero-length clip finishes to
  no samples.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, surrogate offline session, accounting, metrics and report model. |
| `run.py` | Regenerates `adapter.json`, `readiness.json`, `report.json`, the README digest table, sidecars, `contract.json` and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline adapter descriptor. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `test_reference.py` | 38 deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, README digest table, reproduction, disposition, licensing and scope verifier. |
| `check_licensing.py` | Independent SPDX/REUSE and fail-closed file-set check. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate row, evaluated 30-clip DNS2020 and EARS scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | ClearerVoice FRCRN description and source-reported pilot. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Checkpoint/pointer digest, byte count, revision and license metadata. |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | 30-clip and EARS source-reported values. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Paired pilot provenance; not reproduced. |
| `source:adapters/clearvoice/adapter.json` | `ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff` | Existing adapter identity, tasks, modes and entrypoint. |
| `source:adapters/clearvoice/README.md` | `9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5` | Offline quality-reference scope and immutable-revision claim. |
| `source:adapters/clearvoice/requirements.lock` | `3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91` | Pinned runtime package set; not installed here. |
| `source:adapters/clearvoice/run.py` | `c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90` | Input range, identity mapping, zero delay/padding and pointer check. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned completion record and census report a 30-clip DNS2020 pilot with mean
ΔSNR +10.10 dB (95% CI +8.51 to +11.84), mean ΔSI-SDR +10.05 dB (CI +8.46 to
+11.74), mean ΔSTOI +0.0474 (CI +0.0371 to +0.0588), all 30 pairs improved on
both, mean adapter RTF 3.74 and median CPU RTF 3.59. The 12-clip EARS blind
screen reports SIG 4.438 (Δ+0.117), BAK 4.606 (Δ+1.080) and OVL 4.053 (Δ+0.549).
The upstream ClearerVoice README author table reports FRCRN PESQ 3.24, STOI
0.98, SI-SDR 19.99, P.808 MOS 4.03 and SIG/BAK/OVRL 3.58/4.15/3.33. All of
these values are **not reproduced**, not pooled with the synthetic numbers above,
not device timing and not a quality or release claim. They are transcribed only
to preserve the separation required by the Enhancement profile.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CLEARVOICE-FRCRN-16-KHZ diff --check
```

The installed-package SDK check runs from the worktree root with the pinned
interpreter after installing `requirements-build.txt`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py
```

`run.py --all` regenerates the adapter, readiness, report, digest sidecar,
README digest table, contract and source manifest. `report.json` is canonical
JSON (`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- Eight chunk sizes plus one whole-call control; 37,699 caller chunks total in
  the boundary record (chunk size 1 alone contributes 32,000 calls).
- Output 32,000 samples per full 32,000-sample clip; 0 emitted before `finish`;
  identity source-time mapping; 0 delay compensation; 0 emitted padding.
- Partial-final-frame probe: 32,123 input/output samples, 37 internal padding
  samples, 0 emitted padding.
- `report.json` SHA-256: `a1c41721ba3866ae4bec22d71494ff235699c2887f10d813cdd834e0a97f8aba` (33,829 bytes).
- Tests: **38 passed, 0 failed, 0 skipped** (Python 3.12.16).

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `adapter.json` | `211c4246ab07433ab2d74f6badd1c9f8095b22fd8c0c8a0a96ddc3315ac8d7e6` | 1551 |
| `readiness.json` | `1527f97b77d9d2fdea2bbff2f2185705af2120fa8e9b365e7d2afb1dfa50fc5f` | 4929 |
| `reference.py` | `f865704f1b251a259e46c934be2edd7cbcedb25cafd506156b8b2dfb067271c8` | 65128 |
| `report.json` | `a1c41721ba3866ae4bec22d71494ff235699c2887f10d813cdd834e0a97f8aba` | 33829 |
| `run.py` | `148120e2823b3327365bf0c86eab13b5d4867d0d7f48dacbacb21252caf988e7` | 5942 |
| `test_reference.py` | `b16feca7dacedfae3e2a802ed40f4fd85bbe25776d862de0c08e0d802fa0beb7` | 19898 |
| `verify.py` | `805d4f8af3a81906929db6aaed238e34ae5f714f8ec25a02e26dd18e353f634d` | 30303 |
<!-- digest-table:end -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable model artifact revision + byte count + SHA-256, verified pointer and caller-held bytes. |
| `runtime_admission` | blocked | Pinned `clearvoice` 0.1.2 runtime artifact with digest, terms and installed execution. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `exact_reference_parity` | blocked | Approved FRCRN reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target timing, throughput, memory and offline availability evidence. |
| `provider_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
