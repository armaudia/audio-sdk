<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-FREGAN — caller-supplied-asset blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** feasibility
evidence for `FreGAN` (`component_id=fregan`). The acceptance profile is
**Voice**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline reference as a **caller-supplied external
asset** exactly as `CONTRACTS.md` `as_asset_v0` requires: asset ID, byte count,
SHA-256 and `storage=external`, supplied by the caller, with no provider file
access and no download. A deterministic stdlib **synthetic frame-accounting
surrogate** exercises only delay, accounting and refusal mechanics; it is
explicitly opt-in, is **not FreGAN**, is not UnivNet and is not a vocoder. It
substitutes for no gate.

No candidate source, checkpoint, derived weight, acoustic model, graph,
PyTorch/ONNX runtime, corpus, media, device clock, listener, benchmark or
release artifact was downloaded, hashed, loaded, built, compiled, executed or
bundled. There is **no candidate output or result**. No public API/ABI,
`CONTRACTS.md`, descriptor, registry, installed default, shared build,
dependency lock, CI, board or handoff file changes. Only this task-local
directory and the receipts below are added.

## Exact external blocker

The only pinned mention of this candidate is a research classification row:
`research/accent-conversion-20261101/README.md` line 170 records
“FreGAN / UnivNet — Not run. General vocoder families, not accent-conversion
systems. No task-compatible acoustic model/checkpoint pair acquired.” The
workspace contains **no FreGAN or UnivNet source checkout, license text,
repository revision, weight URL, byte count or digest**.

| Item | Status |
| --- | --- |
| Source checkout | **Absent and unpinned**: no `data/checkouts/FreGAN`, `fregan` or `UnivNet`; no commit or LICENSE digest |
| Code license | **Unknown**: no pinned source or license text |
| Exact weights | **Absent and unpinned**: no generator checkpoint, acoustic model checkpoint, byte count, SHA-256 or release tag |
| Fixed asset probes | **Absent**: `data/models`, `data/models/fregan`, `fregan_generator.pt`, `fregan_generator.onnx`, `fregan_acoustic_model.pt`, `data/models/univnet`, `cpp-library/.deps/fregan.onnx` |
| Pinned runtime | **Absent**: no Python/PyTorch/ONNX Runtime version, wheel digest, lock file or evaluator environment |
| Rights entry | **Absent**: the rights register has no `fregan` or `univnet` record |
| Speaker consent | **Absent**: source/target reference permission and output-use permission are not recorded |
| Candidate geometry | **Unknown**: no sample rate, hop, feature contract, generator layout or streaming state is recorded |
| Caller output / cohort | **Absent**: no approved reference output, frozen input vector, paired voice cohort or permitted listening result |

The machine-readable record is `report.json` → `asset_boundary`,
`asset_admission`, `rights`, `voice_profile`, `native_evidence`,
`exact_blockers` and `release_gates`. `contract.json` carries the same
disposition, absent geometry, pins and all eight blocked release gates.

1. **The exact source and weights are absent and unpinned.** No linked
   asset-ledger row or local file records an identity for either a FreGAN/
   UnivNet generator checkpoint or the acoustic model/checkpoint pair the task
   needs. A vocoder checkpoint alone would not satisfy the voice task.
2. **Task fit is unestablished.** The pinned research row classifies the family
   as a general vocoder, not an accent-conversion system. A vocoder cannot
   convert accent by itself, and no task-compatible acoustic model/checkpoint
   pair was acquired.
3. **The exact runtime is absent.** No interpreter, PyTorch, ONNX Runtime,
   wheel digest, target platform or lock file is recorded. No exact-runtime
   reference run or parity vector was produced.
4. **Rights and consent are unresolved.** Evaluation, acquisition,
   redistribution, customer deployment and public playback are all `unknown`.
   No artifact-specific written terms exist. For voice, consent for source and
   target speaker references, permitted reference availability and permitted
   output use are independent gates and none is recorded. Evaluation-only
   status is not established.
5. **No candidate evidence exists.** There is no output, exact reference
   parity, rights-cleared paired voice cohort, independent semantic or
   speaker-identity scorer, naturalness assessment, listening result or
   target-runtime timing. All eight release gates stay `blocked`, and **no
   result may qualify the candidate**.

**Reopen condition.** Admit the candidate only when a specific FreGAN or
UnivNet source revision is pinned by commit and LICENSE digest and its task role
is documented; an exact generator checkpoint and a task-compatible acoustic
model/checkpoint pair are supplied as caller-owned external assets with
immutable revision, release tag, byte count and SHA-256; the exact runtime
installs with recorded digests and documented terms; written rights decisions
and recorded speaker consent exist; and approved exact-runtime reference
outputs, a rights-cleared cohort, independent scoring/listening and target
timing are available. Until then **no result may qualify the candidate**.

## Boundary

- Public v0 geometry preserved: 16 kHz, mono, `f32`, 160 samples per frame.
- Candidate geometry is **unknown and not fabricated**. `report.json:
  reference_interface` records `candidate_geometry_known=false` with every
  candidate rate/hop/window/feature/state field `null`. The surrogate uses the
  installed v0 160-sample hop only as a fixture parameter.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `public_api_abi_change=false`, `provider_registration=false`,
  `descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
  `shared_build_or_ci_change=false`, `processor_exposure=false`,
  `adapter_json_added=false`, `readiness_json_added=false`,
  `asset_bundled=false`, `weights_vendored=false`,
  `model_runtime_invoked=false`, `vocoder_invoked=false`,
  `sdk_data_dir_added=false`. No proposal `adapter.json` or `readiness.json`
  is added; machine-readable state lives in `contract.json` and `report.json`.
- The board is referenced by stable linked-row identity only
  (`tasks[id=SDK-FREGAN]`, stable-field digest). The mutable full
  `plan/swarm/TASKS.json` is never hashed or pinned.
- No v0 frame adapter, resampler, vocoder or model runtime is implemented or
  claimed.

## Streaming semantics modelled

The surrogate mirrors only delay, accounting and refusal mechanics.

- One 160-sample delayed state line plus a synthetic envelope scalar. Payloads
  are fixture values, not model tensors or candidate state.
- Each chunk returns the previous delayed chunk; the first 160 output samples
  are invalid startup, matching the declared fixture buffering delay. One zero
  flush hop releases the tail within the declared maximum of two calls and 320
  samples.
- A 1,093-sample control returns 1,093 samples; a partial tail is not dropped.
- A chunk-aligned prefix of 15,360 samples is stable against the full stream.
  Processing two independently reset halves changes only the boundary chunk,
  which is recorded rather than hidden.
- An impulse probe preserves the peak index exactly (`input=4000`,
  `output=4000`). No algorithmic lag, content delay, latency or device timing is
  measured; all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`.
- Reset zeroes the synthetic state, clears the stream and replays
  bit-identically on a fresh epoch. Sessions are one stream per session; a
  second stream or a chunk after completion is rejected.

## Voice profile application

`report.json:voice_profile` applies the Voice profile without inventing a
voice result:

| Outcome | Status |
| --- | --- |
| Permitted input/target references | `absent` |
| Task / language / speaker groups | `not_defined` |
| Consent | `not_recorded` |
| Semantic preservation | `blocked_unmeasured` |
| Speaker identity / similarity | `blocked_unmeasured` |
| Naturalness | `blocked_unmeasured` |
| Alignment | `not_measured_no_candidate_output` |
| First-output / tail timing | `blocked_unmeasured` |
| Output use | `blocked` |
| Listening | `not_run` |
| Candidate result | `false` |

The synthetic table in `report.json:synthetic_results` records paired signal
SNR and SI-SDR on a common full output length, peak/clipping/nonfinite checks
and split/identity controls. These are **not** semantic, speaker-identity or
naturalness metrics and are never interpreted as voice quality. The pinned
Vocos decoder benchmark is a different model, decoder-only and synthetic-input;
it is context only and never transfers to FreGAN.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_stream` is the documented chunk driver; the independent
  `surrogate_chunk_loop_control` must match it byte-for-byte.
- `surrogate_split_halves` must not match the whole stream; its boundary
  difference is a control, not a quality result.
- Config rejections: wrong model ID, sample rate, channels, sample format,
  native hop, buffering delay, state layout, target condition or consent scope;
  unsupported asset mode; unavailable candidate asset; altered asset
  identity/byte count; and surrogate without opt-in. A fully pinned synthetic
  admission control proves the admission branch; it is explicitly not the
  candidate and has `qualification_effect=none`.
- Stream rejections: empty, oversized, string, boolean, non-finite, infinite and
  out-of-range streams fail with unchanged state; a second stream and any
  post-close call fail closed.
- Chunk rejections: wrong length/type, non-finite and out-of-range chunks, wrong
  state set/shape and non-finite/boolean state values fail before state
  mutation.
- Nonfinite input is never counted as silence; a missing asset never qualifies.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, pins, commands, gates. |
| `reference.py` | Deterministic signals, delayed-boundary surrogate, accounting, metrics and report/contract model. |
| `run.py` | Regenerates `report.json`, its sidecar, the README digest table, `contract.json` and `SOURCES.sha256`. |
| `report.json` / `report.json.sha256` | Canonical Voice report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions, rights/consent scope and pins. |
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
| `source:research/accent-conversion-20261101/README.md` | `c266b648…` | The only FreGAN/UnivNet mention; task-fit and absence finding. |
| `source:research/accent-conversion-20261101/results/vocos-cpu-benchmark.json` | `1948ef27…` | Different decoder-only Vocos context; not FreGAN. |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50…` | SDK sequence, provider boundaries and evidence expectations. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f263133…` | Voice acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945…` | Component/profile assignment and task-fit evidence row. |
| `source:audio-benchmark-platform/audio-pro/docs/rights-register.md` | `e61a406f…` | Rights summary with no fregan/univnet entry. |
| `source:audio-benchmark-platform/audio-pro/inventory/rights-register.json` | `24cbdb65…` | Scoped rights records with no fregan/univnet entry. |
| `worktree:CONTRACTS.md` | `f6fdd18f…` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965a…` | Installed v0 boundary. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74…` | Installed v0 session boundary. |
| `worktree:REUSE.toml` / `LICENSES/Apache-2.0.txt` | `c6f61bc9…` / `cfc7749b…` | Licensing metadata and Apache-2.0 text. |

## Canonical artifacts and local digests

`report.json` is canonical JSON (`sort_keys`, minimal separators, no
`-0.0`/NaN/Infinity, trailing newline). `report.json.sha256` is regenerated
from those exact bytes. `SOURCES.sha256` is a generated manifest of every
pinned boundary and every file in this directory except itself. The table below
is refreshed by `run.py --all` and checked by `verify.py`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `fa40af3614a756b1d082ec610905b78413b96f0844dea441f1e54b1cfe325e86` | 73677 |
| `report.json` | `950c971346aea1d71c086871ea70af5a1f473f36c100c0561fe8ce822dd06824` | 41792 |
| `report.json.sha256` | `8f646a2105e03380012c1b1e71ec30ae6395481fdebcc5768c90f148b3de0629` | 78 |
| `run.py` | `c2f5f12d04f39bb67a79044ea5bd2045e6fd7861fe6e9578849d82c21c71b350` | 5991 |
| `test_reference.py` | `16255bc80d1fe554014b19a655bd3d8c4fb5a5af26caff65d5100f5e063e4cb6` | 29759 |
| `verify.py` | `fc09be7229bd177aa6b136b102fb8c9da74bce7e5d09bd10ccb51a02fa59ef34` | 20752 |
<!-- DIGEST_TABLE_END -->

## Reproduction (pinned interpreter, no bytecode)

Run from this directory with `PYTHONDONTWRITEBYTECODE=1` and
`/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C <worktree> diff --check
```

`run.py` and `verify.py` are deterministic and read no network, model or media
assets. Three cold-start regenerations are byte-identical and are checked by
the test suite and verifier.

## Remaining gates (all blocked, eight total)

1. `exact_asset_identity`
2. `runtime_admission`
3. `artifact_rights`
4. `exact_reference_parity`
5. `rights_cleared_paired_cohort`
6. `independent_scoring_and_listening`
7. `target_runtime_timing`
8. `provider_intake_and_default_selection`
