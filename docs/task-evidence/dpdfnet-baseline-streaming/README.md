<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-DPDFNET-BASELINE-STREAMING — caller-supplied-asset streaming boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`DPDFNet baseline streaming` (`component_id=dpdfnet-baseline-streaming`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the streaming boundary as a **caller-supplied external
asset reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an asset
ID, byte count, SHA-256 and `storage=external`, supplied by the caller, with no
provider file access and no download. The pinned candidate cannot cross that
boundary here. A deterministic stdlib **synthetic frame-causal surrogate**
exercises only 160-sample frame accounting, delay mapping, finite drain and
refusal mechanics; it is explicitly opt-in, is not DPDFNet and substitutes for
no gate.

No candidate artifact was downloaded, loaded, built, vendored or invoked. No
weight, ONNX graph, `dpdfnet` package, `StreamEnhancer`, ONNX Runtime, media,
corpus, device clock, listener, benchmark or release artifact is present or
claimed. There is **no candidate output and no candidate result**. No public
API/ABI, `CONTRACTS.md`, descriptor, registry, installed default, shared build,
CI, board or handoff file changes. Only this task-local directory is added.

## Exact external blocker

The pinned ledger records `data/models/dpdfnet/baseline.onnx` as **8,722,707
bytes**, SHA-256
`371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0`, under source
revision `dd6818d00f50c836fed43a6243ebe49116de5964` and package
`dpdfnet==0.6.0`. The artifact-license audit additionally checks the official
snapshot `1a80d48e150711322f84cb9d4c91b3520045cf64`, which lists
`onnx/baseline.onnx` without exposing a file-level digest. That is not enough
to run or qualify the candidate:

1. **Asset identity is not immutable.** The ledger's `model_revision` is
   `null` and `model_download_revision` is `main (mutable; retrieval-time commit
   not recorded)`. The exact bytes are known only by digest/byte count; no
   immutable artifact revision resolves them, the official snapshot does not
   bind the local digest to its listed file, and the asset is absent from this
   worktree.
2. **The streaming runtime is absent and unpinned.** The streaming path is the
   external CPU ONNX `dpdfnet` 0.6.0 `StreamEnhancer`. It is not installed here,
   has no pinned wheel/sdist artifact digest in this worktree, and no vendor
   runtime or ONNX Runtime is invoked. The recorded wrapper processed 160-sample
   chunks, required a final flush, compensated a measured 640-sample lag, and
   zero-padded a flush tail of up to 158 samples. That is wrapper behaviour, not
   a verified provider-native zero-lag drain or a v0 callback-safe runtime.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   package and model card, but weight-specific terms, training-data provenance
   (DNS4, MLS, DPCRN-processed speech, MUSAN, FSD50K, reverberation), VCTK
   speaker privacy/publicity, redistribution and product-use clearance, and
   legal review are absent. No upstream portion may be copied, packaged,
   downloaded or redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   streaming cohort, independent clean-reference scorer, permitted listening
   result, target pacing/deadline/latency measurement or approved exact
   streaming reference vector for these frozen inputs.

**Reopen condition.** Admit the candidate only when the exact `baseline.onnx`
bytes are addressed by an immutable artifact revision plus byte count and
SHA-256 in a retrieval record and resolve from the caller's own storage; a
pinned `dpdfnet` 0.6.0 streaming runtime artifact with a recorded digest
installs in the intended environment and its flush/tail/lag behaviour is
documented; written artifact-specific weight, runtime and training-data terms
plus a rights/redistribution decision exist; and a rights-cleared cohort,
independent scorer, permitted listening, exact 160-sample streaming reference
outputs and target pacing/deadline evidence are available. Until then all eight
release gates stay `blocked`.

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
  (`tasks[id=SDK-DPDFNET-BASELINE-STREAMING]`, stable-field digest). The mutable
  full `plan/swarm/TASKS.json` is never hashed or pinned.

## Streaming semantics modelled

The fixture models the v0 boundary at exactly 160 samples per frame:

- A **640-sample fixture delay** is modelled from the pinned adapter README,
  which reports a consistent 640-sample (40 ms) output lag on 30 DNS clips and
  says the wrapper compensated it. It is **not measured here**, not device
  latency and not a provider-native zero-lag claim. A single impulse at sample
  4,000 appears at raw output sample 4,640 and at valid-output sample 4,000, so
  the fixture residual after the modelled delay is exactly zero.
- The default 32,000-sample stream is 200 process calls of 160 samples. It
  produces 32,640 raw samples: 640 startup samples are invalid, 32,000 are valid
  content, and four finite drain calls release the final 640 samples. The valid
  interval union is exactly `[0, 32000)` with no gap or overlap.
- A 32,123-sample stream adds a 123-sample final partial frame. It is zero
  padded only for frame processing, 37 padding samples are never emitted, the
  raw output is 32,763 samples, and four drain calls release the tail. The valid
  union is exactly `[0, 32123)`.
- A 100-sample stream still produces 640 startup-invalid samples and 100 valid
  samples during finite drain. An empty stream drains immediately with zero
  output.
- A non-frame-aligned mapping control uses a 400-sample delay: at output frame
  start 320 the valid offset is 80 and valid count is 80. This proves the
  half-open integer mapping is not restricted to frame-aligned delays.
- An independent samplewise block reference over the same synthetic gain
  sequence is byte-identical to the streamed raw and valid outputs.
- `reset` with a strictly greater epoch and nonnegative origin restores the
  exact initial state and replay is bit-identical; a stale epoch and a negative
  origin are rejected. `reset` during draining records cancelled intervals.
- Sessions are caller-driven and synchronous. There is no worker, callback,
  queue, paced workload or wall clock. Availability and all coordinates are
  source-sample positions on `fixture-sample-coordinate-not-device`.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on a common valid output length, peak/clipping/
nonfinite checks and explicit unmeasured fields. STOI is `blocked_unmeasured`
(no rights-cleared clean-reference cohort and no installed scorer), clean-speech
preservation is `synthetic_only`, state/memory is `synthetic_state_only`,
content/availability timing is `blocked_unmeasured`, alignment is
`fixture_delay_modelled_not_measured`, listening is `not_run`, and real
runtime/real clean references are `false`.

### Synthetic fixture results (not a candidate result)

Scores are computed on the 32,000-sample valid output for every variant. They
describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 6.953471 | 7.445783 | +0.492312 | 6.961875 | 6.939612 | -0.022263 | -2.705983 |
| quiet_speech | 4.553064 | 5.832797 | +1.279733 | 4.533636 | 4.520399 | -0.013237 | -2.685161 |
| low_snr_speech | -5.176332 | -2.633149 | +2.543183 | -5.230262 | -5.232553 | -0.002290 | -2.725180 |
| onset_offset | 3.218529 | 4.893386 | +1.674857 | 3.175917 | 3.852737 | +0.676820 | -1.478315 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -2.744092 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the low-SNR output at about 0.492.

### Honest regressions

Three small SI-SDR regressions are recorded verbatim in
`report.json:regressions`: `active_speech` -0.022263 dB, `quiet_speech`
-0.013237 dB and `low_snr_speech` -0.002290 dB versus the noisy control. The
causal gain release slightly distorts some low-energy frames, so SI-SDR falls
while SNR improves. These are properties of the synthetic fixture, not evidence
about DPDFNet, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_streamed_160` is the 160-sample caller stream; the independent
  `surrogate_block_control` must match it byte-for-byte.
- Config rejections: wrong sample rate, channels, sample format, frame size,
  maximum stream or declared lag; unsupported offline mode; unavailable
  candidate asset; altered asset identity/byte count; and surrogate without
  opt-in all fail before instance creation. A fully pinned synthetic admission
  control is created to prove the admission branch; it is explicitly not the
  candidate and has `qualification_effect=none`.
- Frame rejections: empty, short, oversized, string, boolean, non-finite,
  infinite, out-of-range, stale-epoch, non-zero final padding, invalid final
  valid-count, non-final partial valid-count, post-final, post-close, stream
  oversize and drain-before-final cases fail with unchanged state digests.
- Lifecycle: drain is finite, repeated drain after completion returns
  `end_of_stream`, process after final input is rejected, and close is
  idempotent. `begin_drain` is not repeatable.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, streaming surrogate, interval accounting, metrics and report/contract model. |
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
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate row 76, evaluated streaming scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | DPDFNet streaming description and source-reported pilot. |
| `source:adapters/dpdfnet/adapter.json` | `6bd90aa93629a372a7b18c4036d3006c593b53c6f2c7f75bd181590c5327973c` | Existing DPDFNet adapter identity and modes. |
| `source:adapters/dpdfnet/README.md` | `9b55bd13bf74f6c268efa3ad5e6d572ea8ef101527bba467760c6cb47f56f472` | 640-sample stream lag and flush provenance. |
| `source:adapters/dpdfnet/run.py` | `40fbd148eb80ec21a33290e4cb4bc9258afb54f65d4d5fd5d82b552deac5ae02` | 160-sample `StreamEnhancer` loop, flush and lag compensation. |
| `source:adapters/dpdfnet/requirements.lock` | `2d43db167c1c221992ac51bd15ae365bfc18ddc21eb405c53ce8a444e5af34a4` | Recorded CPython 3.11 runtime lock including `dpdfnet==0.6.0`. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset digest, byte count, revisions and license metadata. |
| `source:research/selected_audio_enhancement_candidates.md` | `0364d8d6963192789c839fd37ae6bfdfb405303986066a1ac8e30555d9a1f946` | DPDFNet baseline streaming identity and measured scope. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Streaming pilot summary and separate 800-sample C++ note. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported paired pilot values; provenance only. |
| `source:realtime-audio-library/research/dpdfnet_artifact_license_audit_20261029.md` | `356cc14d47f096e58e68b67b412f508dc669901065c56036bfb9ddd0ed3e4d86` | Immutable-artifact and training-source audit. |
| `source:realtime-audio-library/candidate_evidence.md` | `7c9b84bfc5b60227477fc4d0a2fbc488674801d677cfef1f0c3e32b0357d6df2` | Local streaming/native screen, 640-sample lag and 158-sample tail. |
| `source:realtime-audio-library/evaluation/dpdfnet_baseline_streaming_vctk_v3_16k_5db_20261029.json` | `ef22f42d7f80cb3f00094542eb35a2a8f00b172d0a4744b8bd1bc64cd1605e38` | Aggregate-only local VCTK streaming screen. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset, frame and drain rules. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned pilot records DPDFNet baseline streaming median SNR gain **+6.810
dB**, median STOI **0.9690** and batch RTF **0.0458** on 30 DNS2020 pairs; the
streaming adapter mean ΔSI-SDR is **+7.20 dB**, mean ΔSTOI **+0.0288**, and the
clean-input median STOI is **0.9884**. The package emitted a consistent
**640-sample (40 ms)** content lag which the wrapper compensated;
`REALTIME_COMPONENT_CANDIDATES.md` separately records an **800-sample (50 ms)**
content delay for an experimental C++ scheduled backend. A local-only VCTK v3
screen (58 clips/29 speaker groups, synthetic pink noise, aggregate only) reports
mean ΔSI-SDR +9.6766 dB, ΔSTOI +0.05595 and ΔPESQ +1.0666 with the same
640-sample lag and up to 158 zero-padded tail samples; VCTK privacy/publicity
and clip-level redistribution remain unresolved.

Those values are **not reproduced**, not pooled with the synthetic numbers
above, not device timing and not a quality or release claim. They are transcribed
only to preserve the separation required by the Evidence profile. No listening,
device, callback, latency, benchmark or real-corpus result is claimed here.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-DPDFNET-BASELINE-STREAMING diff --check
```

`run.py --all` regenerates the report, digest sidecar, README digest table,
contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical; the test suite performs the full
three-run regeneration in an isolated copy.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic valid samples.
- 200 process calls and four drain calls per 32,000-sample condition; 32,640
  raw samples and 32,000 valid samples; 640 startup-invalid samples.
- Partial-tail control: 32,123 input samples, 201 process calls, 37 internal
  padding samples, 32,763 raw samples, 32,123 valid samples.
- Short-stream control: 100 input samples, 740 raw samples, 100 valid samples.
- Twelve config adverse cases (eleven rejections plus one synthetic admission
  control); sixteen frame/lifecycle adverse cases; all rejections leave state
  unchanged.
- Eight release gates, all `blocked`.
- `report.json` SHA-256 and byte count are in the table below.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `f216c19050831446e07ba1984b6253902034effebd59cf8ea325519d4436fdac` | 79569 |
| `report.json` | `ede5ec8c72fba81da4a9bdf6b5a768865cf6c56dbfbcfaa80bb47b8806fb4be4` | 39335 |
| `report.json.sha256` | `4797cb0794c5318842d7a904151c9c57404a5dda92e96e6bb3245047b836a5b4` | 78 |
| `run.py` | `6aa6a7d087a7f2bca5542c11a109d153d8b4e1e12942ff2d0ca52e7b9b644321` | 6006 |
| `test_reference.py` | `d986b6e5f716533c34ae0b7894f49b217ce7d389966ea97b394ab638e00e8534` | 28743 |
| `verify.py` | `6e6045b14f6d48c52225c0426438511518f778102b4150e01221f69b40aaab14` | 19173 |
<!-- DIGEST_TABLE_END -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable artifact revision + byte count + SHA-256, caller-held bytes. |
| `runtime_admission` | blocked | Pinned `dpdfnet` 0.6.0 streaming runtime artifact with digest and documented flush/tail/lag. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and redistribution decision. |
| `exact_reference_parity` | blocked | Approved 160-sample streaming reference vectors including drain and reset. |
| `rights_cleared_paired_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target callback pacing, deadline, memory, latency and drain-tail evidence. |
| `provider_intake_and_default_selection` | blocked | Opt-in provider intake, OFF default, review and explicit default decision. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
