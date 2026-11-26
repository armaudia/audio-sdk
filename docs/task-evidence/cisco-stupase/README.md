<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CISCO-STUPASE — Cisco StuPASE readiness blocker

`audio-sdk/cisco-stupase/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **10** |
| Open exact blockers | **8** |
| Profile | Enhancement (`plan/swarm/VERIFICATION.md`) |
| Mode | feasibility |
| Pinned base | `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |
| Pinned Python | `3.12.16` |

This directory is a bounded, task-local feasibility package for **Cisco StuPASE**
(`component=cisco-stupase`). It is **not** an implementation, adapter, provider,
benchmark or release. It records the exact public source and checkpoint
identities, the source-derived task geometry, the fail-closed
caller-supplied-asset contract and a strict readiness conclusion. Nothing here
may be promoted to a runtime, quality or release claim.

## Why DEFER

The project record is unambiguous:

- the candidate record says `code=available`, `weights=located_unverified`,
  `benchmark_state=not_run`, `reported_only=true`;
- its eligibility is `blocked` because exact hashes, a compatible runtime
  footprint and noise-only behaviour are not verified;
- the immutable accounting row repeats `located_unverified` and `blocked`;
- the census note says checkpoints are still unpinned/unverified for evaluation.

Metadata-only inspection identifies the exact public identities:

- official source repository `https://github.com/cisco-open/pase` at commit
  `45614efae73dc49bf36018d1ca6a9319b3050038` (119-entry tree, Apache-2.0
  Cisco-authored code plus MIT/Apache third-party notices);
- official model hub `https://huggingface.co/cisco-ai/stupase` at revision
  `539963f425ae201ac8c379b6480e3b182a4840ad` (Apache-2.0 model card,
  three PyTorch checkpoints and a 53-byte config).

That is identification, **not admission**. No source checkout, checkpoint,
config, PyTorch runtime, audio file or dataset byte exists in this worktree. The
three checkpoint files total **2,262,766,692 bytes**. The released model is
approximately **561M parameters**, with **104 GMAC/s** source-reported and an
8-step Euler CFM sampler. The host is Apple Silicon without CUDA, `torch` is not
installed in the pinned interpreter, and the official `requirements.txt` pins
`torch` and `torchaudio` twice (`2.4.1` and `2.1.1`) without pinning Python.

The two official wrappers also disagree on output peak policy:
`stupase/inference/inference.py` scales the output to the input peak, while
`stupase/inference/infer_flow.py` scales to a fixed `0.5`. The model forward
pads or truncates to the input length, but no measured alignment, tail, peak or
clean-preservation trace exists.

This package therefore records a **strict readiness conclusion** instead of
reproducing the model. Reopening requires the exact external artifacts and
reviews listed below. Supplying any one of them is not enough.

## Exact external blockers

| ID | Title | Minimum reopening condition |
| --- | --- | --- |
| `BLK-01` | Source checkout not admitted | Materialize commit `45614efae73dc49bf36018d1ca6a9319b3050038` in caller-owned storage, record the tree digest and per-file SHA-256, and review `LICENSE.md`/`NOTICE` for the intended use. |
| `BLK-02` | Checkpoint bytes not admitted | Supply `DeWavLM-R.pt` (1,261,990,714 bytes, SHA-256 `4eb21c9e6ab9bf51fe1c24a580e6f4c8f677ad4028e3b997e462e34f17c59ccf`), `CFM.pt` (758,024,988 bytes, SHA-256 `df8e77fcc31554abb1b3481f1f4bc62688e75b9bd83081fb4d336b128f760f5e`) and `Vocoder_Mel-16k.pt` (242,750,990 bytes, SHA-256 `2d38b6adfb29129a4c78f7ed030aa75f1a922f71e0fc87f2e59f2c58d04ee13b`) from the caller's storage with an immutable retrieval receipt. |
| `BLK-03` | Runtime not reproducible | Provide one resolved lock for Python 3.12.16 with artifact hashes for torch, torchaudio, numpy, soundfile, librosa, omegaconf, torchdiffeq, x-transformers and huggingface_hub; install it on the intended target and reproduce an import plus one forward pass without network. |
| `BLK-04` | Wrapper geometry and peak policy ambiguous | Freeze one integration contract for peak normalization, tail handling and source-sample mapping, then reproduce a whole-clip trace with exact lengths, peaks, alignment and final-partial behaviour. |
| `BLK-05` | Rights and data obligations not reviewed | Record a written legal/rights review for the exact checkpoints, the Apache-2.0/MIT third-party notices and the CC BY 4.0, CC0 1.0 and CC BY-SA 3.0 training-data obligations; clear local evaluation, derivative output use, redistribution and any commercial use. |
| `BLK-06` | Matched enhancement evidence absent | Freeze a rights-cleared cohort and scorer; run identity/noisy and task-matched controls; report paired SI-SDR/STOI, clean preservation, peaks, invalid outputs, noise-only and dereverberation strata separately; add permitted listening or a labelled predictive screen. |
| `BLK-07` | Compute feasibility unverified | Measure one whole-clip forward pass on the intended CPU/MPS/CUDA target with wall time, memory, device, thread count and exact runtime, or supply a qualified target runner. |
| `BLK-08` | Provider intake and release gates absent | Only after `BLK-01`–`BLK-07` clear, implement a separate opt-in OFF-by-default adapter, obtain independent exact-head review, and record benchmark and release approval. |

All ten release gates are blocked. The full text is duplicated in
`contract.json:exact_blockers`, `readiness.json:external_blockers` and
`report.json:exact_blockers`.

## Task geometry (source-derived, not executed)

| Item | Value | Source |
| --- | --- | --- |
| Sample rate | 16 kHz mono | model card, `config.json` |
| Processing mode | offline whole-clip | candidate record, official wrappers |
| Mel channels | 100 | `cfg_train_flow.yaml`, `cfg_train_melvocoder.yaml` |
| Mel FFT / hop / window | 1280 / 320 / 1280 samples | `cfg_train_flow.yaml` |
| Mel frame rule | `T = 1 + floor(L / 320)` | torchaudio centered STFT semantics |
| DeWavLM-R output layer | 24 | `cfg_train_flow.yaml` |
| CFM DiT | dim 1024, depth 12, heads 16, text-in 1024 | `cfg_train_flow.yaml` |
| CFM sampler | Euler, 8 steps, CFG 0.5, sway −1.0 | `cfg_train_flow.yaml`, `inference.py` |
| Vocoder | 100 input channels, dim 768, 12 layers | `cfg_train_melvocoder.yaml` |
| Output length | padded/truncated to input length | `stupase/models/stupase.py` |
| Declared content lag | 0 samples (unmeasured) | model forward |
| Peak policy | `input_peak` vs fixed `0.5` (inconsistent) | the two official wrappers |
| Parameter count | ~561M (source-reported) | model card |
| Compute | ~104 GMAC/s (source-reported) | model card |

The public v0 SDK geometry is preserved unchanged: 16 kHz, mono, `f32`, 160
samples per call. StuPASE is an offline whole-clip model; no streaming state or
v0 adapter is implemented here.

## Enhancement profile application

The Enhancement profile requires identity/noisy controls, paired SI-SDR/STOI
where permitted clean references exist, clean-speech preservation, peak and
invalid-output checks, and separate alignment/state/timing reporting.

| ID | Requirement | Status | Evidence |
| --- | --- | --- | --- |
| `ENH-01` | identity/noisy control | synthetic contract control only | identity is bit-exact; noisy control is the input; no model output |
| `ENH-02` | paired SI-SDR | blocked | no rights-cleared cohort or model output |
| `ENH-03` | paired STOI | blocked | no approved scorer or cohort |
| `ENH-04` | clean-speech preservation | blocked | no regression run |
| `ENH-05` | peaks, clipping, invalid outputs | source-derived, unmeasured | wrappers disagree on peak policy |
| `ENH-06` | alignment and final partial window | source-derived, unmeasured | no measured trace |
| `ENH-07` | state, memory, lifetime | not applicable / blocked | offline whole-clip; no state contract |
| `ENH-08` | content and availability timing | blocked | no device clock or paced workload |
| `ENH-09` | generative latency and compute | blocked | no forward-pass timing |
| `ENH-10` | listening or predictive screen | blocked | no authorization or approved screen |

Every row has `qualifies=false`. There are **0** qualifying results.

### Synthetic controls (not a candidate result)

`admission_control` runs **54** rejection cases plus one valid synthetic
manifest: missing/unknown fields, wrong types, malformed
or non-pinned digests, wrong sizes, wrong source/hub identities, wrong sampling,
wrong Mel geometry, unpinned runtime fields, unresolved peak policy and nonzero
content lag. All expected codes match; no state advances; the synthetic control
is schema-valid but **not admitted** because no candidate bytes exist. A
synthetic present-bytes control exercises the admission branch and still has
`qualifies=false`.

`frame_control` runs **12** public-v0 frame cases: one accepted 160-sample frame
and 11 exact rejections for wrong length, nonfinite, non-numeric, boolean and
out-of-range samples.

`mel_geometry_control` runs **11** source lengths and **7** arithmetic checks.
For example, 16,000 samples produce 51 centered Mel frames and 32,000 samples
produce 101; output length equals source length under the model's
pad/truncate contract.

`scoring_control` exercises the metric code on deterministic binary-fraction
signals. Identity SI-SDR/SNR are explicitly undefined at zero error; the noisy
control is the input; halving the output leaves SI-SDR unchanged while changing
scale-sensitive SNR; silence has a zero projection and is never scored as
speech. STOI is **not** scored because no approved scorer or rights-cleared
cohort exists.

These numbers describe the controls only. They are not StuPASE results and clear
no gate.

## Pinned local evidence sources

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked against the file and against `SOURCES.sha256` by
`verify.py`; the README digest table itself is re-read and validated.

| Source | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `cisco-stupase` component record and Enhancement profile assignment. |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | SDK implementation plan and task-local evidence boundary. |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `reports/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7/candidate_accounting.csv` | `7261b99e06460b612dcbebeec3859de60a7040a18444fc19a637ebddc4a58e3c` | Immutable accounting row: `blocked`, `located_unverified`. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset ledger; contains no StuPASE asset entry. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | StuPASE census entry and official source/model-card links. |
| `research/pilot_evaluation_progress.md` | `7f9636606ee88bb7184ced604598918aac6a8d2c95bc6fcb33e5450909f5cedf` | Deferred scope and explicit unpinned-checkpoint note. |
| `research/store/snapshots/c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7.jsonl` | `c21d01c37c0c50203f72a5a9bf1aee6f4fed1a5bc4d2682960f58b26dda922c7` | Immutable method and candidate records. |

Boundary pins also cover `CONTRACTS.md`, `CMakeLists.txt`, `REUSE.toml`,
`README.md`, both public v0 headers, `scripts/ci.py`,
`.github/workflows/ci.yml` and `LICENSES/Apache-2.0.txt`; all are unchanged and
machine-checked in `SOURCES.sha256`.

## External source and asset metadata (not materialized)

These identities were established by public HTTPS metadata only. No source or
checkpoint bytes were downloaded, read or hashed locally. The SHA-256 values for
the three checkpoints are the hub LFS object identifiers; the text-file hashes
are SHA-256 of the public raw bytes returned for the pinned revision. They are
recorded for reopening and are **not** local admission.

| Object | Bytes | SHA-256 | Role |
| --- | ---: | --- | --- |
| `DeWavLM-R.pt` | 1,261,990,714 | `4eb21c9e6ab9bf51fe1c24a580e6f4c8f677ad4028e3b997e462e34f17c59ccf` | semantic enhancement module |
| `CFM.pt` | 758,024,988 | `df8e77fcc31554abb1b3481f1f4bc62688e75b9bd83081fb4d336b128f760f5e` | flow-matching acoustic enhancement |
| `Vocoder_Mel-16k.pt` | 242,750,990 | `2d38b6adfb29129a4c78f7ed030aa75f1a922f71e0fc87f2e59f2c58d04ee13b` | Mel vocoder |
| `config.json` | 53 | `b3229818b05a9ff9ec9bf36323ce3c1b109c0dff861d50f73da03aa68ab48193` | hub config |
| hub `README.md` | 7,943 | `6eccb2ec0798191cfd2ce6fe913e00bab2a7c7d05694f4ed14687e51c8abdd4e` | Apache-2.0 model card |
| `stupase/README.md` | 4,949 | `1565ec7b38aedb611353eb3dbc4f852a72cfe03fdcb11037b76c09396c9b9a7c` | inference and checkpoint description |
| `stupase/configs/cfg_infer.yaml` | 509 | `2bcdd6d9e1ff94d9cbc8ceaa01f0341bd10ed4b0fe1acca119b6aa9fd3454311` | inference schema |
| `stupase/configs/cfg_train_flow.yaml` | 3,927 | `aaa541d8d7c1610f12830e0cd33cc7884e451a942adecc4a594734ba90c21e9c` | CFM/DiT and Mel geometry |
| `stupase/configs/cfg_train_melvocoder.yaml` | 2,505 | `1bb2299c3b1a35e01f8ed53d11f7bede64ade3796b3fd96478665e7086bc3bf9` | vocoder geometry |
| `stupase/models/stupase.py` | 2,138 | `3304b80256d8ed001146d6a15fb9fea3afd8fce708e03d075d6d95eeb7ca93e7` | forward and pad/truncate |
| `stupase/inference/inference.py` | 6,131 | `f30753c617f980bf5e014661f1bc3fb6dafe9fc2b30cc2461bec1aa66b6fc9f3` | input-peak normalization |
| `stupase/requirements.txt` | 308 | `da3a568caaebde12e57f17ff76a9d03170546efb742656cd772f0c81a22b6605` | conflicting duplicate pins |
| `LICENSE.md` | 2,222 | `e270c357f173cacbcaa3a223c2faac631c0e04e368cb7b9781636236026bc36e` | Apache-2.0/third-party policy |
| `NOTICE` | 2,616 | `5d431fc2f1664d3532b7b53775bf1a799752f3f6d8f5091c39653b974480b426` | third-party notices |

Source URLs are `https://github.com/cisco-open/pase/blob/45614efae73dc49bf36018d1ca6a9319b3050038/<path>`.
Asset URLs are `https://huggingface.co/cisco-ai/stupase/blob/539963f425ae201ac8c379b6480e3b182a4840ad/<path>`.
Metadata was observed on 2026-11-26.

## Admission and fail-closed behaviour

`reference.validate_asset_bundle` requires exactly the declared caller-asset
fields and rejects unknown fields, missing fields, wrong types, malformed or
non-pinned digests, wrong byte counts, wrong source commit, wrong hub revision,
wrong sample rate/channels/format, missing or extra modules, relative module
paths, wrong sampling/Mel geometry, unpinned runtime fields, unsupported
devices, unresolved peak policy, nonzero content lag and a relative caller path.

On the non-synthetic path, the three checkpoint SHA-256 values and byte counts
must equal the pinned values, `source_commit` must equal
`45614efae73dc49bf36018d1ca6a9319b3050038`, and `hub_revision` must equal
`539963f425ae201ac8c379b6480e3b182a4840ad`. Validation never opens a file,
resolves a caller path or reads a byte. A valid manifest is still not admitted
unless the caller supplies the bytes; a missing or mismatched asset fails closed
before any frame or clip.

## Reproduce

`SOURCE_ROOT` is needed only by the verifier and tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CISCO-STUPASE
TASK=$WT/docs/task-evidence/cisco-stupase
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
export PYTHONDONTWRITEBYTECODE=1
cd "$TASK"
$PY run.py --all
$PY -m unittest -v test_reference.py
$PY verify.py
cd "$WT"
$PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/cisco-stupase-ci
python3 -m reuse lint
git diff --check
```

`run.py --all` regenerates `adapter.json`, `readiness.json`, `report.json`,
`report.json.sha256`, `contract.json` and `SOURCES.sha256`. `verify.py` checks
the README digest table, every pin, strict JSON, canonical bytes, the report
sidecar, disposition, assets, gates, licensing, write scope and three
cold-start regenerations. No network, source checkout, checkpoint, torch
runtime, audio file or device is used by the package.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, exact blockers, geometry, controls, pins and commands. |
| `reference.py` | Deterministic source/asset identities, manifest validator, synthetic controls and canonical builders. |
| `run.py` | Regenerates all canonical artifacts byte-identically. |
| `contract.json` | Task contract: profile, boundary, geometry, asset identities, blockers, gates and invariants. |
| `readiness.json` | Concise strict readiness conclusion. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, registered or enabled. |
| `report.json` | Canonical machine-readable Enhancement report. |
| `report.json.sha256` | SHA-256 sidecar for `report.json`. |
| `SOURCES.sha256` | SHA-256 pins for external, boundary and task-local files. |
| `test_reference.py` | Standard-library unittest suite. |
| `verify.py` | Read-only strict verifier. |
| `LICENSES.md` | License and provenance notes. |
| `*.license` | REUSE/SPDX sidecars for non-commentable artifacts. |

## Gates and reopen conditions

The package records ten blocked gates: source commit/tree admission, checkpoint
identity/bytes, runtime lock and forward pass, wrapper geometry and peak policy,
rights and data obligations, rights-cleared cohort and baseline, independent
scoring plus listening/predictive screen, clean preservation/peaks/invalid
outputs, compute/timing/resources, and opt-in provider intake plus release
review. Each reopen condition is in `report.json:gates` and
`contract.json:gates`; `readiness.json` is the concise strict conclusion.

Reopen only when **all** exact blockers close. Until then Cisco StuPASE stays
**DEFER**, **incomplete** and **not qualified**.

## Non-claims

- No result in this package is a qualification, benchmark or release.
- No Cisco StuPASE source, checkpoint, runtime, audio or dataset bytes were
  copied, downloaded, imported, loaded or executed.
- The public source and checkpoint identities were established from metadata
  only; no asset bytes were read or hashed.
- The synthetic admission, frame, Mel and scoring controls are contract checks,
  not StuPASE results.
- No paired SI-SDR, STOI, clean-preservation, peak, noise-only, dereverberation,
  listening or WER result exists.
- No device timing, memory, latency, availability, benchmark or resource result
  exists.
- No rights review, output-use grant, redistribution clearance or commercial-use
  decision exists.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI, shared
  build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
