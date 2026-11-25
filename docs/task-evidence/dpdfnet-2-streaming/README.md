<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DPDFNET-2-STREAMING — caller-supplied-asset streaming boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DPDFNet-2 streaming` (`component_id=dpdfnet-2-streaming`). The acceptance
profile is **Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before `processor_exposure`;
`evidence_status=incomplete`, `qualification_status=not_qualified`. A missing
result never qualifies the candidate.

The package models the streaming boundary as a **caller-supplied external
asset reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an asset
ID, byte count, SHA-256 and `storage=external`, supplied by the caller, with no
provider file access and no download. The pinned candidate cannot cross that
boundary here. A deterministic stdlib **synthetic surrogate** exercises only
the streaming/frame-boundary mechanics; it is explicitly opt-in, is not
DPDFNet-2 and substitutes for no gate.

Nothing was downloaded, loaded, built, vendored or invoked. No weight, ONNX
graph, `dpdfnet` package, ONNX Runtime, media, corpus, device clock, listener,
benchmark or release artifact is present or claimed. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build, CI,
board or handoff file changes. Only this task-local directory is added.

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
2. **The runtime is absent and unpinned.** The streaming runtime is the
   external CPU ONNX `dpdfnet` 0.6.0 package. It is not installed here, has no
   pinned wheel/sdist digest in this worktree, and no vendor runtime is invoked.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   package and model card, but weight-specific terms, training-data provenance,
   redistribution and product-use clearance, and legal review are absent. No
   upstream portion may be copied, packaged, downloaded or redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target pacing/deadline measurement or approved exact streaming reference
   vector.

**Reopen condition.** Admit the candidate only when the exact `dpdfnet2.onnx`
bytes are addressed by an immutable artifact revision plus byte count and
SHA-256 in a retrieval record and resolve from the caller's own storage; a
pinned `dpdfnet` 0.6.0 runtime artifact with a recorded digest installs in the
intended environment; written artifact-specific weight, runtime and
training-data terms plus a rights/redistribution decision exist; and a
rights-cleared cohort, independent scorer, permitted listening, exact streaming
reference outputs for these frozen inputs and target pacing/deadline evidence
are available. Until then all nine release gates stay `blocked`.

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
  advertises `modes=["streaming"]`, the external asset requirement and
  `asset_readiness="blocked"`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no bytes are read and no download is
  attempted.

## Streaming semantics modelled

The fixture models the boundary at 160-sample frames and arbitrary caller
chunks up to 2 s:

- A 640-sample declared **algorithmic lag** is modelled from the pinned
  adapter README (source-reported on 30 DNS clips). It is not measured here.
  A single impulse probe is placed at sample 4000; the raw peak appears at 4640
  and the lag-compensated peak returns to 4000 with zero residual lag.
- Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280` and a single 32,000-sample
  call all produce **identical** raw and compensated digests. Internal frame
  buffering makes the result independent of caller chunking.
- For a 32,000-sample stream the raw output is 32,640 samples = 32,000 + 640
  startup samples. After dropping the 640 startup samples and appending 640
  zeros, the wrapper truncates to input length, so `valid_samples=32000`.
  A complete flush is required for the final 640 real samples; without it the
  tail is not attributable.
- A partial final frame is zero-padded **only for gain estimation**; it is
  counted as `internal_frame_padding_samples` and never emitted as valid audio.
- One explicit `flush` drains the delay line; a second flush returns `[]`.
  `reset` restores the exact initial state and replay is bit-identical. A fresh
  independent session produces the same per-frame state digest chain, and a
  foreign stream after `reset` is bit-identical to a fresh session.
- Availability and all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`. There is no wall clock, device clock,
  callback deadline, paced workload or latency measurement.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on a common valid prefix, peak/clipping/nonfinite
checks and explicit unmeasured fields. STOI is `blocked_unmeasured` (no
rights-cleared clean-reference cohort and no installed scorer), clean-speech
preservation is `synthetic_only`, state/memory is `synthetic_state_only`,
content/availability timing is `blocked_unmeasured`, listening is `not_run`,
and real runtime/real clean references are `false`.

### Synthetic fixture results (not a candidate result)

Scores are computed after removing the modelled 640-sample lag, on the same
32,000-sample prefix for every variant. They describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 9.500643 | 9.542846 | +0.042204 | 9.467575 | 10.421112 | +0.953536 | -2.473652 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -16.032665 |
| low_snr_speech | -7.584471 | 0.777401 | +8.361873 | -7.652977 | -7.013835 | +0.639142 | -15.169367 |
| onset_offset | 13.466509 | 13.910875 | +0.444365 | 13.449036 | 13.963313 | +0.514277 | -0.754395 |
| quiet_speech | 12.403286 | 10.754870 | -1.648417 | 12.412695 | 12.015241 | -0.397454 | -2.058291 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the active-speech output at about 0.235.

### Honest regressions

Two regressions are recorded verbatim in `report.json:regressions`:

| Condition | Metric | Noisy control | Surrogate | Delta |
| --- | --- | ---: | ---: | ---: |
| quiet_speech | snr_db | 12.403286 | 10.754870 | -1.648417 |
| quiet_speech | si_sdr_db | 12.412695 | 12.015241 | -0.397454 |

The gate over-suppresses quiet speech: its noise estimate tracks the pause
floor, but the release smoothing attenuates low-level speech onsets more than
it removes noise. This is a property of the synthetic fixture, not evidence
about DPDFNet-2, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_streamed_160` is the 160-sample caller stream; the
  `surrogate_large_chunk_32000` control must match it byte-for-byte.
- Config rejections: wrong sample rate, channels, frame size or declared lag,
  unsupported mode, surrogate without opt-in, and an unavailable caller asset
  all fail before instance creation. A fully pinned synthetic admission control
  is created to prove the admission branch; it is explicitly not the candidate.
- Frame rejections: empty, oversized, string, boolean, non-finite and
  out-of-range chunks fail with unchanged state digests.
- Lifecycle: process after flush/close, flush after close and reset after close
  are rejected; flush and close are idempotent; a zero-length stream flushes to
  no samples.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, surrogate streaming session, accounting, metrics and report model. |
| `run.py` | Regenerates `adapter.json`, `readiness.json`, `report.json`, `contract.json`, sidecars and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered streaming adapter descriptor. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `test_reference.py` | 35 deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, reproduction, disposition, licensing and scope verifier. |
| `check_licensing.py` | Independent SPDX/REUSE and fail-closed file-set check. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate row 78, evaluated streaming scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | DPDFNet-2 streaming description and source-reported pilot. |
| `source:adapters/dpdfnet/adapter.json` | `6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c` | Existing DPDFNet adapter identity and modes. |
| `source:adapters/dpdfnet/README.md` | `9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472` | 640-sample stream lag and reset/flush provenance. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset digest, byte count, revisions and license metadata. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | DPDFNet-2 identity and measured scope. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Streaming pilot summary and separate C++ delay note. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported paired pilot values; provenance only. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned pilot records DPDFNet-2 streaming mean ΔSI-SDR +7.5437 dB, mean ΔSNR
+7.6076 dB, mean ΔSTOI +0.0329 and batch RTF 0.1090 on 30 DNS2020 pairs, with a
640-sample lag compensated. `REALTIME_COMPONENT_CANDIDATES.md` separately
records an 800-sample (50 ms) content delay for the experimental C++ scheduled
backend. Those values are **not reproduced**, not pooled with the synthetic
numbers above, not device timing and not a quality or release claim. They are
transcribed only to preserve the separation required by the Evidence profile.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DPDFNET-2-STREAMING diff --check
```

`run.py --all` regenerates the adapter, readiness, report, digest sidecar,
contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- Eight chunk sizes plus one whole-call control; **37,699** caller chunks total
  in the boundary record (chunk size 1 alone contributes 32,000 calls).
- Raw output 32,640 samples per full 32,000-sample stream; valid output 32,000;
  640 startup samples and 640 truncated tail-pad samples.
- `report.json` SHA-256: `8c9f651f00e26b4be550fd53585cda94d68a4f2903ccfdff94440891ae9a8101` (31422 bytes).
- `reference.py` SHA-256: `d07e42f3a7ad57d68ce117c82adce8594edaa8103b561808ae039b49ffd10fea`.
- `run.py` SHA-256: `79804d37e4b74bcf622a7e41515b5440b8e1096c83989bc6b6bbfd3d84782178`.
- `test_reference.py` SHA-256: `5c3bfcc23f6ea6f791c27da5a2b86b8e433f29ead5d212cdc5bdc48bb0583a17`.
- `verify.py` SHA-256: `b54e7eeea5c1fbda7b9b589c72cfdc8c4c291234b6c7dee7377e0c8358f06ac7`.
- `adapter.json` SHA-256: `e4bfb419c1110fc0799976995268a34aa08fe3632ff1b80cd2da11063a3f3b53`.
- `readiness.json` SHA-256: `89abaabf4a9221438647a5e35f02496d7a3612fa3547424d628dccde8c08bc53`.
- Tests: **35 passed, 0 failed, 0 skipped** (Python 3.12.16).

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable artifact revision + byte count + SHA-256, caller-held bytes. |
| `runtime_admission` | blocked | Pinned `dpdfnet` 0.6.0 runtime artifact with digest and terms. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `exact_reference_parity` | blocked | Approved streaming reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target pacing, availability, deadline and memory evidence. |
| `provider_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
