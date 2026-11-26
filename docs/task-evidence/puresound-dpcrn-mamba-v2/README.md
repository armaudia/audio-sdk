<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-PURESOUND-DPCRN-MAMBA-V2 — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`PureSound DPCRN-Mamba v2` (`component_id=puresound-dpcrn-mamba-v2`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result never qualifies the
candidate, and all **eight** release gates stay blocked.

The package models the offline whole-clip boundary as a **caller-supplied
external asset reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an
asset ID, byte count, SHA-256 and `storage=external`, supplied by the caller,
with no provider file access and no download. The pinned candidate cannot cross
that boundary here. A deterministic stdlib **synthetic surrogate** exercises only
the whole-clip accounting and refusal mechanics at the pinned 512/160 geometry,
including the 480-sample streamed hold and its exact trim; it is explicitly
opt-in, is not PureSound DPCRN-Mamba and substitutes for no gate.

No graph, manifest, source checkout, `puresound-streaming` package or ONNX
Runtime was downloaded, copied into this worktree, loaded or invoked. No media,
corpus, device clock, listener, benchmark or release artifact is present or
claimed. No public API/ABI, `CONTRACTS.md`, descriptor, registry, installed
default, shared build, CI, board or handoff file changes. Only this task-local
directory is added.

## Candidate identity and the v1 sibling

- Candidate: `PureSound-noise-suppression-dpcrn-mamba-v2`.
- Upstream catalog ID: `noise-suppression-dpcrn-mamba-v2`; catalog role
  **default**, described as v1 fine-tuned with a MetricGAN PESQ critic.
- Graph: `egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.onnx`,
  **2,282,757 bytes**, SHA-256
  `a28cc5c9736f415a5ed603bd97cc415d11d8088cb2e288d20334a0713f723c86`.
- Manifest: `egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.json`,
  **3,545 bytes**, SHA-256
  `e5c54c5df8d7f3ee253c86ff09d4906f57efc01e2a6eeca80183ecf0fa88171d`.
- Source revision: `79fad1f1c753da5e40a0cbb00c6507c9fce2db3a`.

The merged sibling package `docs/task-evidence/puresound-dpcrn-mamba-v1/`
(PR #167, head `ca47268316779efb5161fc29571b2e5b313d31c3`, merge
`a91a45e32428df353dbf55a7a9fd2ec052760539`, report SHA-256
`b6967e090b8aed2e04f0e898e2f6094bc7870ffc3a7b1f0b8dfb2fa582dfbd8c`) is a
**different graph** (`eabdca9f…04bfab`) at the same source revision. It reaches
the same `DEFER` / `incomplete` / `not_qualified` disposition for its own asset
identity. No v1 metric, output, gate result or disposition is promoted to v2.
The v2 manifest differs from v1 only in the ONNX path, `created_at` and the
CPU-optimization native graph (`dpcrn_mamba_v2.native.onnx`, SHA-256
`b47fa2378ab57885463a08305741caf11ba192425f144392617c1089b5ec0426`); the
512/512/160, 257-bin, 256-feature, 3-frame streaming geometry is identical.

## Exact external blocker

The pinned ledger and catalog identify the v2 graph and manifest above. The
bytes are present in the external research checkout and were re-hashed there.
That is not enough to run or qualify the candidate:

1. **Asset identity is not admitted.** The ledger records no immutable
   `model_revision` and no retrieval-time download record. The graph and
   manifest are known only by digest/byte count in an external mutable checkout;
   no caller-held copy exists in this SDK worktree, the manifest content is not
   admitted as caller-supplied content, and the package neither reads nor admits
   the bytes.
2. **The runtime is absent and unpinned.** The exact runtime is
   `puresound-streaming` 0.1.0 (a source package in the external checkout with no
   built wheel/sdist digest) plus `onnxruntime==1.24.1`. The pinned CPython
   3.12.16 interpreter cannot import `onnxruntime` (`ModuleNotFoundError`), the
   adapter requirements lock (numpy 2.2.6, onnxruntime 1.24.1, soundfile 0.13.1)
   is not installed, and `adapters/puresound-dpcrn-mamba/run.py` is not
   executed.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   original PureSound code, SDK, configuration, documentation and model-zoo
   checkpoints/ONNX exports, and the upstream `NOTICE` permits commercial use
   and redistribution under the license. The `NOTICE` excludes third-party
   material and datasets/audio recordings; exact training-data provenance and
   third-party dataset terms are not established, and no artifact-specific
   redistribution/product-use legal review or decision is recorded.
   Apache-2.0 metadata alone is not clearance. The upstream default role for v2
   grants no SDK default selection.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target-runtime timing/memory/throughput measurement, approved exact reference
   output vector or benchmark/release result.

**Reopen condition.** Admit the candidate only when the exact
`dpcrn_mamba_v2.onnx` and `dpcrn_mamba_v2.json` bytes are addressed by an
immutable model artifact revision plus byte count and SHA-256 in a retrieval
record, the manifest fields are verified, and both resolve from the caller's own
storage without a provider file access or download; a pinned
`puresound-streaming` 0.1.0 wheel or sdist with a recorded digest and a pinned
`onnxruntime==1.24.1` install in an approved isolated environment and run the
adapter under the requirements lock; written artifact-specific weight, runtime
and training-data terms plus a legal/redistribution/product-use decision exist;
and a rights-cleared cohort, independent scorer, permitted listening, exact
reference outputs for these frozen inputs and target timing/memory/throughput
evidence are available. Until then all eight release gates stay `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary and linked-row identity

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `realtime_streaming_exposed=false`, `processor_exposure=false`.
- The upstream model is offline-file and realtime-streaming capable. This
  package exposes **offline mode only**, because the upstream adapter runs the
  streaming SDK over a whole file and trims its look-ahead; no streaming
  provider, pacing or callback surface is added.
- The task-local `adapter.json` is a proposal descriptor, not a provider. It
  advertises `modes=["offline"]`, the external graph plus manifest requirement
  and `asset_readiness="blocked"`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no asset bytes are read by the admission
  path and no download is attempted.
- The upstream configuration fields are modelled exactly:
  `repository_dir`, `code_revision`, `model_id`, `model_path`, `manifest_path`,
  `model_sha256`, `sample_rate`, `provider`, `variant`; path fields are replaced
  by caller-owned symbolic references in this package.
- `report.json:task_link` gates only the stable projection of this task's own
  `plan/swarm/TASKS.json` row (id, title, repository, mode, component,
  dependencies, evidence, deliverable, acceptance and claim branch/base/reviewer)
  plus a projection digest. The mutable full board file is **never** hashed and
  never appears in `SOURCES.sha256`; unrelated board edits cannot stale this
  package.

## Offline semantics modelled

The fixture models the boundary at the upstream adapter's offline contract and
the pinned streaming manifest:

- Input is mono 16 kHz `f32` in `[-1, 1]`. Empty, oversized, string, boolean,
  non-finite and out-of-range samples are rejected before state changes.
- Caller chunks are buffered and the whole clip is enhanced once at `finish()`.
  Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280` and a single 32,000-sample
  call all produce **identical** output digests, so the result is independent of
  caller chunking.
- The pinned manifest is 512/512/160 with 257 frequency bins, 256 feature bins
  and `streaming_delay_frames=3`: a **480-sample** content hold. The runtime
  emits `input + 480` samples and the adapter trims `480`; the modelled output
  has exactly the input length (`valid_samples=32000`), identity source-time
  mapping, `delay_compensation_samples=480` and `padded_samples=0`.
- The manifest's declared input-to-output algorithmic latency is 52-62 ms
  (832-992 samples: look-ahead plus the 512-sample window, minus one hop). It
  explicitly excludes compute, chunk buffering, device buffering and transport.
  It is **not measured here**; the fixture only models the sample-coordinate
  hold and trim.
- A partial final hop is zero-padded **only for gain estimation**; it is counted
  as `internal_frame_padding_samples` and never emitted. The dedicated probe
  feeds 32,123 samples, reports 37 internal padding samples, a 32,603-sample
  streamed hold and 32,123 output samples.
- A complete clip is required: `finish()` after `finish()` is rejected, and a
  second clip needs an explicit `reset()`. `reset` restores the exact initial
  state and replay is bit-identical. A fresh independent session produces the
  same per-chunk state digest chain, and a foreign feed after `reset` is
  bit-identical to a fresh session.
- The manifest is a required auxiliary artifact. Its structured fields are
  modelled and checked fail-closed (`model_type`, `processor`, sample rate,
  512/512/160 geometry, 257/256 bins, 3 delay frames, 480-sample look-ahead,
  52-62 ms latency, v2 native graph digest). Missing, invalid, extra and
  nonfinite fields are rejected before admission. The fields are observed
  read-only in the external checkout and are **not** admitted as caller-supplied
  content in this worktree.
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
| active_speech | 9.465938 | 10.055733 | +0.589794 | 9.428855 | 9.898232 | +0.469377 | -1.582343 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -17.873253 |
| low_snr_speech | -7.566055 | 0.948645 | +8.514699 | -7.555871 | -6.109770 | +1.446101 | -14.897484 |
| onset_offset | 13.403405 | 14.179711 | +0.776307 | 13.390136 | 14.047976 | +0.657841 | -0.507399 |
| quiet_speech | 12.428716 | 11.526140 | -0.902575 | 12.419033 | 11.584269 | -0.834765 | -1.213092 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the active-speech noisy control at about 0.273 and the largest surrogate
output is about 0.256.

### Honest regressions

Two regressions are recorded verbatim in `report.json:regressions`:

| Condition | Metric | Noisy control | Surrogate | Delta |
| --- | --- | ---: | ---: | ---: |
| quiet_speech | snr_db | 12.428716 | 11.526140 | -0.902575 |
| quiet_speech | si_sdr_db | 12.419033 | 11.584269 | -0.834765 |

The fixture uses the 50th percentile of frame power as a naive noise floor, so
quiet speech is over-suppressed. This is a property of the synthetic fixture, not
evidence about PureSound, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_offline_chunked_160` is the 160-sample caller feed; the
  `surrogate_offline_whole_clip` control must match it byte-for-byte.
- Config rejections: wrong sample rate, channels, sample format, model ID (v3),
  variant, provider, code revision or model digest, unsupported mode, surrogate
  without opt-in and an unavailable caller asset all fail before instance
  creation. A fully pinned synthetic admission control is created to prove the
  admission branch; it is explicitly not the candidate.
- Manifest rejections: a complete field set is the only admitted control;
  missing `processor`, wrong model type, wrong hop length, wrong native digest,
  nonfinite/infinite latency, an unexpected field and a non-object all fail
  closed with exact reasons.
- Frame rejections: empty, oversized, string, boolean, non-finite and
  out-of-range chunks fail with unchanged state digests.
- Lifecycle: process after finish/close, finish after finish/close and reset
  after close are rejected; close is idempotent; a zero-length clip finishes to
  no samples.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, 512/160 surrogate, 480-sample hold/trim accounting, manifest admission, metrics and report model. |
| `run.py` | Regenerates `adapter.json`, `asset.json`, `readiness.json`, `report.json`, the README digest table, sidecars, `contract.json` and `SOURCES.sha256`; `--all` proves three byte-identical cold starts. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, qualification, task link, blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline adapter descriptor. |
| `asset.json` | Exact caller-supplied graph/manifest/asset pins and runtime/rights status. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `requirements.lock` | Pinned external runtime package set; not installed here. |
| `LICENSES.md` | Recorded upstream Apache-2.0/NOTICE scope and exclusions. |
| `test_reference.py` | 47 deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, JSON, task-link, README digest table, reproduction, runtime probe, disposition, licensing and scope verifier. |
| `check_licensing.py` | Independent SPDX/REUSE and fail-closed file-set check. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned sources and boundary

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every digest is checked by
`SOURCES.sha256` and `verify.py`. `plan/swarm/TASKS.json` is intentionally absent:
only the stable row projection in `report.json:task_link` is gated.

| Pin | SHA-256 | Use |
| --- | --- | --- |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | v2 candidate row, evaluated 30-clip DNS2020 scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | v2 default description, MetricGAN fine-tune and source-reported pilot. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Graph/manifest digest, byte count, revision and license metadata. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Paired pilot provenance; not reproduced. |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | 30-clip completion and 480-sample compensation note. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | v2 batch RTF and 480-sample look-ahead record. |
| `source:adapters/puresound-dpcrn-mamba/adapter.json` | `ee1fb16e50a0808711994a190037f53be392e6b1148cf015ddef602425d4e037` | Adapter identity, tasks, modes and entrypoint. |
| `source:adapters/puresound-dpcrn-mamba/README.md` | `c4cb52f917c4a3123d169fb68811984c75ea3b815eb1583bc42a9127bf8220f5` | Official IDs, 10 ms chunks, isolated runtime and license scope. |
| `source:adapters/puresound-dpcrn-mamba/run.py` | `e378d09da875a9b11bc93fd84ff9b4ddefe48ba9803343f800698419fe00a5f4` | Config checks, v2 catalog hash, 480-sample trim and manifest checks. |
| `source:adapters/puresound-dpcrn-mamba/requirements.lock` | `797d0a91bd7c7cc49ccc8d46b97988c98fdd74d1197e53ab363c16caef57c916` | Pinned runtime package set; not installed here. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence, build boundary and release policy. |
| `source:data/checkouts/puresound-dpcrn-mamba/model_zoo/catalog.yaml` | `fc4d903bf141e62a5f5a9a88d9969e965ea7eef22678c40c62e33e46cf3cd373` | Pinned v2 catalog row, default role, graph digest and capabilities. |
| `source:data/checkouts/puresound-dpcrn-mamba/egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.onnx` | `a28cc5c9736f415a5ed603bd97cc415d11d8088cb2e288d20334a0713f723c86` | Exact external graph; not copied, loaded or admitted. |
| `source:data/checkouts/puresound-dpcrn-mamba/egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v2.json` | `e5c54c5df8d7f3ee253c86ff09d4906f57efc01e2a6eeca80183ecf0fa88171d` | Exact external manifest; fields observed, not admitted. |
| `source:data/checkouts/puresound-dpcrn-mamba/sdk/python/puresound_streaming/runtime.py` | `b8f38810aa81aea0563eb900c562ee33cb106787bf535371ce2387b301f3fdb0` | Streaming runtime, 480-sample `dry_delay` and OLA geometry. |
| `source:data/checkouts/puresound-dpcrn-mamba/sdk/python/pyproject.toml` | `35bb2fadb8861a832e39a5dd2aa2553cff17cb904f02495f20fa356aea92b5ab` | Package 0.1.0, Python >=3.12 and ONNX Runtime dependencies. |
| `source:data/checkouts/puresound-dpcrn-mamba/NOTICE` | `ecce4d8c6a7bf96b90027ba1250ae734d33d4c260cd83fb67fcdce2286b435e1` | Apache-2.0 scope and third-party/dataset exclusions. |
| `source:data/checkouts/puresound-dpcrn-mamba/LICENSE` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Apache-2.0 text. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned pilot reports, for the 30 paired DNS2020 clips, median output SNR
16.455 dB, median SNR gain +7.152 dB, mean ΔSI-SDR +6.690 dB and median STOI
0.9705. The paired-difference table records mean ΔSNR +6.7304 dB (95% CI
[5.2930, 8.1975]), mean ΔSI-SDR +6.6897 dB (CI [5.2726, 8.1394]) and mean ΔSTOI
+0.0334 (CI [0.0248, 0.0420]), with 28/0/2 clips improved/tied/degraded on SNR
and SI-SDR and 29/0/1 on STOI. Mean adapter time was 1.9953 s and median CPU RTF
0.1942; the 480-sample streaming look-ahead was compensated during scoring. The
upstream catalog describes v2 as the **default**, v1 fine-tuned with a MetricGAN
PESQ critic, reporting VCTK-DEMAND PESQ-WB 2.57 and DNS-5 DNSMOS OVR 2.83. All of
these values are **not reproduced**, not pooled with the synthetic numbers above,
not device timing and not a quality or release claim. They are transcribed only
to preserve the separation required by the Enhancement profile. The upstream
default role selects no SDK default.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PURESOUND-DPCRN-MAMBA-V2 diff --check
```

The installed-package SDK check runs from the worktree root with the pinned
interpreter after installing `requirements-build.txt`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py
```

`run.py --all` regenerates the adapter, asset, readiness, report, digest sidecar,
README digest table, contract and source manifest, then runs three fresh
interpreter processes and requires byte-identical report digests. `report.json`
is canonical JSON (`sort_keys=True`, compact separators, `allow_nan=False`,
negative zero normalized) plus one trailing newline. `verify.py` requires CPython
3.12.16, re-probes the absent ONNX Runtime, checks the external research checkout
digests and byte counts, and re-reads only the stable task-row projection from
`plan/swarm/TASKS.json`.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- Eight chunk sizes plus one whole-call control; 37,698 caller chunks total in
  the boundary record (chunk size 1 alone contributes 32,000 calls).
- Output 32,000 samples per full 32,000-sample clip; 0 emitted before `finish`;
  a 32,480-sample streamed hold; 480 samples trimmed; identity source-time
  mapping; 0 emitted padding.
- Partial-final-hop probe: 32,123 input/output samples, a 32,603-sample
  streamed hold, 37 internal padding samples, 0 emitted padding.
- Eight release gates, all `blocked`; no missing result qualifies the candidate.
- `report.json` SHA-256: `65fff1e0a79e33f6d25cba4a245692c2d4abfbfd5c8de33066f1af708d841f34`.
- Tests: **47 passed, 0 failed, 0 skipped** (Python 3.12.16).

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `7650735f3f92044ccc179461d1662028097784d16144722d48f03dc7b5f9f9bf` | 1448 |
| `adapter.json` | `a8d1f93959a762b1c0340cc140cbd965ef84caea094c5cf541f00cb09ae60129` | 2206 |
| `asset.json` | `549bd1db97e3cd6857c4966821b19dc6a79d4c8bad00333225e9628ecacbcbd6` | 3412 |
| `readiness.json` | `ab74c9cbe494958cb8969878284bb54ec1953dbed31f2f3e5e93eca7c682cd86` | 7017 |
| `reference.py` | `c66428bd43dcf6fe57cd65eef6774f87e81ff4ef5ac60ad0c1c4673369e0a2ff` | 89032 |
| `report.json` | `65fff1e0a79e33f6d25cba4a245692c2d4abfbfd5c8de33066f1af708d841f34` | 43780 |
| `requirements.lock` | `bd3dc83f358efb63e07db64a92b51f6ac5ccb86dc10c06f10fe36ec24c8b067c` | 198 |
| `run.py` | `bf8848720edb115866890d26ab11ee70f59fb73040b2e987bd1f00c47b05fd8e` | 7085 |
| `test_reference.py` | `cfa7969aeecb8f95a7b5f5baba56306b1d14b7dee7f9356a8954a60b30615d91` | 26835 |
| `verify.py` | `308b7238e081efbd30eb3accd41d05366926a6a12a367cd6a644c433d0acf38c` | 39116 |
<!-- digest-table:end -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable graph/manifest artifact revision + byte count + SHA-256, verified manifest and caller-held bytes. |
| `runtime_admission` | blocked | Pinned `puresound-streaming` 0.1.0 artifact and `onnxruntime==1.24.1` installed and executed with a digest. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms, third-party dataset exclusions and a redistribution decision. |
| `exact_reference_parity` | blocked | Approved DPCRN-Mamba v2 reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target timing, throughput, memory and offline availability evidence. |
| `provider_intake_and_default_selection` | blocked | Opt-in provider intake, OFF default, independent review and an explicit SDK default decision. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
