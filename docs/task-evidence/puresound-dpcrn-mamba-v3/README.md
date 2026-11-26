<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-PURESOUND-DPCRN-MAMBA-V3 — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`PureSound DPCRN-Mamba v3` (`component_id=puresound-dpcrn-mamba-v3`). The
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

## Candidate identity and sibling packages

- Candidate: `PureSound-noise-suppression-dpcrn-mamba-v3`.
- Upstream catalog ID: `noise-suppression-dpcrn-mamba-v3`; catalog role
  **candidate**, described as a wider 16 kHz streaming DPCRN-Mamba with
  mixed-source coverage training, a PESQ critic and a DNSMOS P.835 judge.
- Graph: `egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v3.onnx`,
  **4,146,551 bytes**, SHA-256
  `2a823d830bb87254edda35a8b7ae0743f8d6a203fc4ad3bbad9a2645c1947693`.
- Manifest: `egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v3.json`,
  **3,567 bytes**, SHA-256
  `7880ca7c10ae63f8f414daaafb5205740b063967453a0a255079c9d914dc7a25`.
- Source revision: `79fad1f1c753da5e40a0cbb00c6507c9fce2db3a`.

The merged sibling package `docs/task-evidence/puresound-dpcrn-mamba-v1/`
(PR #167, head `ca47268316779efb5161fc29571b2e5b313d31c3`, merge
`a91a45e32428df353dbf55a7a9fd2ec052760539`, report SHA-256
`b6967e090b8aed2e04f0e898e2f6094bc7870ffc3a7b1f0b8dfb2fa582dfbd8c`) is a
**different graph** (`eabdca9f…04bfab`) at the same source revision. The
sibling v2 package (`a28cc5c9…23c86`, report SHA-256 `43a2a56f…bfb87d3`) was
still a proposal under review and is **not** merged; there is no v2 merge
claim. Both siblings reach the same `DEFER` / `incomplete` / `not_qualified`
disposition for their own asset identities. No v1 or v2 metric, output, gate
result or disposition is promoted to v3.

The v3 manifest keeps the v1/v2 512/512/160, 257-bin, 256-feature, 3-frame
boundary but widens the recurrent state: the manifest declares 128-wide
`up_cache`/`h`/`c` tensors and 48-wide `skip_cache`/LSTM projections instead of
v2's 96/32-wide state, and names the CPU-optimization native graph
`dpcrn_mamba_v3.native.onnx` (SHA-256
`090d227b9fb29d7e4cdc637b01911b481302a95cf9a05ae01e69d7787b0579f3`). The graph
is 4,146,551 bytes versus v2's 2,282,757, about 1.8x, and the catalog reports
about 1.5x the v2 CPU cost.

## Exact external blocker

The pinned ledger and catalog identify the v3 graph and manifest above. The
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
   Apache-2.0 metadata alone is not clearance. The upstream **candidate** role
   for v3 grants no SDK default selection, and its source-reported unresolved
   deletion gates and above-input hard-set WER are risks that stay outside any
   local result.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target-runtime timing/memory/throughput measurement, approved exact reference
   output vector or benchmark/release result.

**Reopen condition.** Admit the candidate only when the exact
`dpcrn_mamba_v3.onnx` and `dpcrn_mamba_v3.json` bytes are addressed by an
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
  52-62 ms latency, v3 native graph digest). Missing, invalid, extra and
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
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | v3 candidate row, evaluated 30-clip DNS2020 scope. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | v3 wider-model description, mixed-source training and source-reported pilot. |
| `source:research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Graph/manifest digest, byte count, revision and license metadata. |
| `source:research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Paired pilot provenance; not reproduced. |
| `source:research/denoising_phase_completion_20261028.md` | `fbed6d30ad11d4ac9c3134077c483c3d58c3e1250ba97aa1cd772b93ddf8645f` | 30-clip completion and 480-sample compensation note. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | v3 batch RTF and 480-sample look-ahead record. |
| `source:adapters/puresound-dpcrn-mamba/adapter.json` | `ee1fb16e50a0808711994a190037f53be392e6b1148cf015ddef602425d4e037` | Adapter identity, tasks, modes and entrypoint. |
| `source:adapters/puresound-dpcrn-mamba/README.md` | `c4cb52f917c4a3123d169fb68811984c75ea3b815eb1583bc42a9127bf8220f5` | Official IDs, 10 ms chunks, isolated runtime and license scope. |
| `source:adapters/puresound-dpcrn-mamba/run.py` | `e378d09da875a9b11bc93fd84ff9b4ddefe48ba9803343f800698419fe00a5f4` | Config checks, v3 catalog hash, 480-sample trim and manifest checks. |
| `source:adapters/puresound-dpcrn-mamba/requirements.lock` | `797d0a91bd7c7cc49ccc8d46b97988c98fdd74d1197e53ab363c16caef57c916` | Pinned runtime package set; not installed here. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Delivery sequence, build boundary and release policy. |
| `source:data/checkouts/puresound-dpcrn-mamba/model_zoo/catalog.yaml` | `fc4d903bf141e62a5f5a9a88d9969e965ea7eef22678c40c62e33e46cf3cd373` | Pinned v3 catalog row, candidate role, graph digest and capabilities. |
| `source:data/checkouts/puresound-dpcrn-mamba/egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v3.onnx` | `2a823d830bb87254edda35a8b7ae0743f8d6a203fc4ad3bbad9a2645c1947693` | Exact external graph; not copied, loaded or admitted. |
| `source:data/checkouts/puresound-dpcrn-mamba/egs/noise_suppression/pretrained_ckpt/streaming/dpcrn_mamba_v3.json` | `7880ca7c10ae63f8f414daaafb5205740b063967453a0a255079c9d914dc7a25` | Exact external manifest; fields observed, not admitted. |
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
16.169 dB, median SNR gain +7.268 dB, mean ΔSI-SDR +6.589 dB and median STOI
0.9711. The paired-difference table records mean ΔSNR +6.6761 dB (95% CI
[5.1645, 8.2574]), mean ΔSI-SDR +6.5894 dB (CI [5.0360, 8.1433]) and mean ΔSTOI
+0.0338 (CI [0.0259, 0.0423]), with 28/0/2 clips improved/tied/degraded on SNR
and SI-SDR and 30/0/0 on STOI. Mean adapter time was 2.6185 s and median CPU RTF
0.2542; the 480-sample streaming look-ahead was compensated during scoring. The
census reports mean ΔSNR +6.68 dB, ΔSI-SDR +6.59 dB, ΔSTOI +0.0338 and adapter
RTF 0.262, and notes quality similar to v1/v2 at higher cost on this subset. The
upstream catalog describes v3 as a **candidate**, not the default: a wider model
with mixed-source coverage training and a PESQ critic plus DNSMOS P.835 judge,
reporting higher PESQ, STOI and DNSMOS than v2 at about 1.5x the CPU, with
deletion gates unresolved and hard-set WER above the unprocessed input. All of
these values are **not reproduced**, not pooled with the synthetic numbers above,
not device timing and not a quality or release claim. They are transcribed only
to preserve the separation required by the Enhancement profile. The upstream
candidate role selects no SDK default.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-PURESOUND-DPCRN-MAMBA-V3 diff --check
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
- `report.json` SHA-256: `a141498ca40e51b2a0774e1c495c0df554dabaa96035b52040d77f3df5e9d478`.
- Tests: **47 passed, 0 failed, 0 skipped** (Python 3.12.16).

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `7650735f3f92044ccc179461d1662028097784d16144722d48f03dc7b5f9f9bf` | 1448 |
| `adapter.json` | `1425182108118c455b2f536d224c3f19ee8403d1ccadfc9f8a6e9cc1f2b41ab1` | 2208 |
| `asset.json` | `c5ba4f2f824e356c3b8c2ddfd72e6204389d5b318a411d913de0f72eb5e1cce0` | 3600 |
| `readiness.json` | `df19ee82a95f99747aecf67afe1f505ae3e7072337ad0282fb0ceb56e6ab9148` | 7430 |
| `reference.py` | `e109dfeb2a9d7fcb75a9a4e69ca46c11ddc1552f95e64799a252c8cf152c3623` | 90655 |
| `report.json` | `a141498ca40e51b2a0774e1c495c0df554dabaa96035b52040d77f3df5e9d478` | 45109 |
| `requirements.lock` | `bd3dc83f358efb63e07db64a92b51f6ac5ccb86dc10c06f10fe36ec24c8b067c` | 198 |
| `run.py` | `491bac4b5e4e21eaff4e5406407c34d9e8be7d5910a8d4ac30b8e327e19e1314` | 7085 |
| `test_reference.py` | `8afb16d0e633898b7a7e44eb16bb7ad0e0d9a5e2ebc218ceb106d423559b0fcc` | 27334 |
| `verify.py` | `fb28b5904adebf26b0c0d6cb778e0c03132ab4aedc1d8c1f2f079f5d57bfcc41` | 39727 |
<!-- digest-table:end -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable graph/manifest artifact revision + byte count + SHA-256, verified manifest and caller-held bytes. |
| `runtime_admission` | blocked | Pinned `puresound-streaming` 0.1.0 artifact and `onnxruntime==1.24.1` installed and executed with a digest. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms, third-party dataset exclusions and a redistribution decision. |
| `exact_reference_parity` | blocked | Approved DPCRN-Mamba v3 reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target timing, throughput, memory and offline availability evidence. |
| `provider_intake_and_default_selection` | blocked | Opt-in provider intake, OFF default, independent review and an explicit SDK default decision. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
