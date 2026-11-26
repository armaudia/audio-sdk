<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MS-ISTFT-GENERATOR — MS-iSTFT-Generator feasibility blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision `DEFER`;
qualification `not_qualified`; eight release gates blocked.** This directory
contains bounded, deterministic, task-local feasibility evidence for the
MS-iSTFT-Generator row. It is **not** an MS-iSTFT-Generator implementation and
**no candidate result** is present. No official source checkout, generator
checkpoint, acoustic feature contract, PyTorch/ONNX runtime, corpus, voice pair,
generated waveform, listening result, device measurement, benchmark or release
claim exists. **No result here qualifies MS-iSTFT-Generator.**

The structured inventory marks `ms-istft-generator` as
`evidence_status=considered` with the **Voice** acceptance profile and
disposition `sdk-model` (`plan/INVENTORY.json`). The task mode is `feasibility`.
Its deliverable asks the owner to verify runnable source, exact assets,
permitted scope, task geometry and matched evidence before reproducing the exact
model/runtime as a caller-supplied-asset reference and adding an opt-in adapter.
Feasibility fails at every prerequisite, so the documented decision is **DEFER**
before `opt_in_provider_intake`.

## Exact external blocker

The pinned research record is a negative run record, not candidate evidence:

> `research/accent-conversion-20261101/README.md` line 168 — **MS-iSTFT-Generator
> | Not run.** Vocoder component only; **no compatible accent-converter acoustic
> model/checkpoint was identified for an end-to-end local run.**

The inventory carries the same finding. No official source repository,
revision, LICENSE digest, weight byte count, SHA-256, release tag, runtime lock
or rights entry is recorded. A derived module is visible in an unrelated
checkout, but it is not admitted:

| Copy | Revision | License | Weight present | Admitted |
| --- | --- | --- | --- | --- |
| `research/voice-conversion-eval-20261101/repos/llvc` (`minimal_quickvc/models.py`, `Multistream_iSTFT_Generator` selected by `ms_istft_vits=True`) | `1627c5d358cf9bb2b92b0ccc513d8b36807c923d` | MIT (containing project) | No | No |

The observed file is source provenance only. It is not an official
MS-iSTFT-Generator release, has no model card or weight of any kind, and the
LLVC checkpoint used for the documented full-system any-to-one voice-conversion
run was removed after evaluation. No isolated vocoder parity, quality or timing
result exists. Nothing was fabricated, reconstructed, mirrored, downloaded or
substituted.

| Missing artifact | Exact requirement |
| --- | --- |
| Official source checkout | The exact MS-iSTFT-Generator source at an immutable 40-hex commit, a per-file SHA-256 manifest from a reviewable tree, the reviewed upstream LICENSE and notice text, and a recorded comparison against the observed LLVC-derived module |
| Generator checkpoint | The caller-selected MS-iSTFT-Generator generator at an immutable revision, with release tag, byte count, SHA-256, selected format (PyTorch/ONNX), declared sample rate, spectral feature contract, iSTFT FFT/hop layout, subband count, upsample layout and state behaviour |
| Runtime | A locked, reproducible isolated Python runtime with exact interpreter, framework, wheel digests, lock-file SHA-256, target platform, offline load path and recorded host profile |
| Rights and scope | Reviewed code, weight, model-card and training-data terms that settle attribution, evaluation, redistribution, customer deployment, public playback and generated-output use; MIT source for LLVC does not clear any MS-iSTFT-Generator weight or output |
| Voice cohort | A frozen, rights-cleared paired cohort with permitted source and target references, language and speaker groups, held-out splits, consent and output-use permission |
| Matched task evidence | A fixed upstream acoustic feature contract and an end-to-end accent-conversion context that isolates the vocoder; a multi-stream iSTFT vocoder alone does not transform voice or accent |
| Candidate results | Exact-runtime reference parity for frozen inputs, independent semantic-preservation, speaker-identity and naturalness scoring, permitted listening, alignment, first-output/tail timing, state, memory, availability and resources |

The machine-readable record is `report.json` → `feasibility`, `absence_audit`,
`asset_boundary`, `asset_admission`, `workspace_observations`, `rights`,
`voice_profile`, `native_evidence`, `exact_blockers` and `release_gates`.
`contract.json` carries the same disposition, absent geometry, pins and all
eight blocked release gates.

## Feasibility conclusion

`report.json:feasibility` records the pinned basis:

- `plan/INVENTORY.json` component `ms-istft-generator`, disposition `sdk-model`,
  area “Voice and synthesis”, profile `voice`, finding **“Not run. Vocoder
  component only; no compatible accent-converter acoustic model/checkpoint was
  identified for an end-to-end local run.”**
- `research/accent-conversion-20261101/README.md` line 168 repeats the negative
  row in the accent-conversion candidate table.
- A derived `Multistream_iSTFT_Generator` exists in LLVC, but no official source,
  weight, runtime, rights, consent, geometry or matched voice evidence exists
  locally, so a caller-supplied-asset reference cannot be built and an opt-in
  adapter cannot be admitted.

The decision is therefore **DEFER**. A comparison was neither retained nor
reproduced, because there is **no candidate** to run. This is not a negative
quality result; it is an evidence and feasibility blocker.

## What this package verifies

1. **Absence evidence.** Fixed workspace and home-cache probes are checked; no
   recursive walk is performed. All official candidate probes are absent.
   `reference.build_report()` and `verify.py` fail if any probe later appears, so
   a stale “absent” claim cannot be shipped.
2. **Observed derived copy is pinned and not admitted.** The LLVC checkout is
   recorded with its containing-project revision, MIT license digest and
   `minimal_quickvc/models.py` digest. The verifier fails if the copy disappears,
   changes its pinned files, claims exact upstream provenance, or gains a weight.
   It is never used for parity, quality, timing or qualification.
3. **Stable pins.** The research records, planning records, rights register,
   observed LLVC source/license files and SDK boundary files are pinned by
   SHA-256, plus the merged sibling `hifi-gan-vocoder`, `vocos` and
   `micro-hifi-gan` READMEs as adjacent boundary references. These are read-only
   provenance inputs, not model evidence.
4. **Stable board identity.** Only the linked row's `id`, `title`, `repository`,
   `mode`, `component`, `depends_on`, `write_scope`, `deliverable`,
   `acceptance`, `evidence` and `dispatch_priority` are projected and hashed.
   The mutable `plan/swarm/TASKS.json` file is **never hashed**; status, owner,
   claim, review, handoff, blocked reason, timestamps and history never enter
   canonical bytes and never gate this package.
5. **Fail-closed admission.** The caller-supplied `as_asset_v0` boundary
   requires an asset ID, byte count and SHA-256 with `storage=external`; a
   missing, unpinned, unsigned or non-admitted candidate is rejected before any
   processing. One synthetic structural control is accepted to prove the
   validator is not blanket-rejecting; it is explicitly `candidate_asset=false`,
   is not MS-iSTFT-Generator and has `qualification_effect=none`.
6. **Adverse, missing, invalid and nonfinite rejection.** Wrong model, rate,
   channels, format, feature bins, hop, lookahead, delay, state layout, target
   condition and consent are rejected; empty, oversized, string, boolean,
   negative, out-of-range, nonfinite and repeated streams are rejected;
   malformed, nonfinite and out-of-range states and frames are rejected without
   advancing state.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the root `README.md` and the
   Apache-2.0 license are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No MS-iSTFT-Generator
   provider is installed or registered; no descriptor, default, ABI, shared
   build, CI, board or handoff change is made.

## Voice profile application

| Voice requirement | Status here | Evidence |
| --- | --- | --- |
| Frozen permitted input and target references | blocked | No rights-cleared source/target references, consent or output-use permission. |
| Task and language/speaker groups | blocked | No task-matched cohort, language grouping or held-out split. |
| Text/semantic content preserved | blocked | No candidate output, transcript or independent semantic scorer. |
| Identity/similarity | blocked | No target reference, independent identity model or similarity result. |
| Naturalness | blocked | No naturalness assessment, score or permitted listening panel. |
| Alignment, first-output and tail timing | blocked | No candidate output or exact-runtime timing on the target condition. |
| Exact target condition | blocked | Code, weight, features, runtime and corpus versions are all unpinned. |
| Consent, reference availability and output use | blocked | Independent gates; none is recorded. |

## Synthetic feasibility surrogate

The surrogate mirrors only delay, accounting and refusal mechanics.

- Fixed synthetic 80-bin feature-like frames, a 160-sample output hop and a
  declared two-frame lookahead/delay. These are fixture parameters, **not**
  candidate geometry; no spectral or subband layout is inferred from the
  observed derived file.
- One delayed frame queue. Payloads are fixture values, not model tensors or
  candidate state. Candidate geometry fields are recorded as `null`.
- Each frame returns the delayed frame; the first 320 output samples are invalid
  startup, matching the declared fixture buffering delay. Two zero flush frames
  release the tail within the declared maximum of two calls and 320 samples.
- A 7-frame control returns exactly 1,120 samples; a partial tail is not
  dropped. A single-frame impulse at source frame 8 first appears at the
  source-aligned output sample `8*160 = 1280` after the declared 320-sample
  startup-invalid prefix, preserving delay and content mapping.
- Frame-loop and whole-stream drivers are byte-identical; split-half driving is
  deliberately different, proving the state boundary is exercised.
- Outputs are finite, bounded and deterministic. Paired synthetic SNR/SI-SDR
  values are fixture diagnostics only and are not semantic, identity or
  naturalness evidence.

## Boundary

- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `vocoder_invoked=false`,
  `sdk_data_dir_added=false`. No proposal `adapter.json` or `readiness.json` is
  added; machine-readable state lives in `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-MS-ISTFT-GENERATOR]`, stable-field digest). The mutable full
  `plan/swarm/TASKS.json` is never hashed or pinned.
- No candidate weight, checkpoint, graph or runtime was downloaded, read,
  hashed, loaded, compiled, executed or bundled. The observed LLVC source and
  LICENSE files are pinned read-only for provenance; the LLVC full-system run is
  quoted context, not an isolated MS-iSTFT-Generator result.

## Reproduction

From this directory, with Python 3 standard library only:

```sh
python3 reference.py            # imports the deterministic boundary/surrogate
python3 -m unittest -v test_reference.py
python3 run.py --all            # report, README table, contract, SOURCES.sha256
python3 verify.py               # strict read-only verification
python3 -m reuse lint           # repository licensing gate
```

`verify.py` runs `run.py --digest` three times from a cold start, requires one
byte-identical digest, and compares it with `report.json.sha256`. It also fails
on any change outside `docs/task-evidence/ms-istft-generator/` and on a drifted
stable board projection.

## Digest table

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `103001f04cb34ee486c7516764f345193e0f154c5e154ff3d21eabcf35a085cc` | 98209 |
| `report.json` | `79e22225bdf56bc2b178b657f701462d5d1ccf8aa9e2e0bd7e484c4f254c892c` | 56446 |
| `report.json.sha256` | `44b8561f145f32e082fe0800b8c07b17e913d613fcac62e539f2ec9f62537834` | 78 |
| `run.py` | `32e05cfb922ba0b9cef7a0e7ab5af8c6b75d347dec636b3789c6cbbcffa9cb79` | 6381 |
| `test_reference.py` | `50559f384b528ac354c40a05ea59d0e35cdb230f843bebd8e459e05a05edf829` | 33543 |
| `verify.py` | `893ac79904c3ca47f4d01ed2cddb10ddba827bd51896016433432a60e4c49fce` | 29825 |
<!-- DIGEST_TABLE_END -->
