<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-CLEARVOICE-MOSSFORMERGAN — caller-supplied-asset offline boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`ClearVoice MossFormerGAN` (`component_id=clearvoice-mossformergan`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`. A missing result never qualifies the
candidate.

The package models the offline whole-clip boundary as a **caller-supplied
external asset reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an
asset ID, byte count, SHA-256 and `storage=external`, supplied by the caller,
with no provider file access and no download. The pinned candidate cannot cross
that boundary here. A deterministic, stdlib-plus-NumPy **synthetic surrogate**
exercises only the boundary mechanics; it is explicitly opt-in, is **not MossFormerGAN**, has no attention block, GAN, weight or checkpoint, and
substitutes for no gate.

Nothing was downloaded, loaded, built, vendored or invoked. No checkpoint,
pointer, PyTorch graph, `clearvoice` package, media, corpus, device clock,
listener, benchmark or release artifact is present or claimed. No public
API/ABI, `CONTRACTS.md`, descriptor, registry, installed default, shared build,
CI, board or handoff file changes. Only this task-local directory is added.

## Exact external blocker

The pinned ledger records `MossFormerGAN_SE_16K/last_best_checkpoint.pt` as
**38,845,593 bytes**, SHA-256
`04bf00db575389e1ea8b1fcca48d9efcf073e50ad170e6dd5230df3bac98be27`, and a
24-byte `MossFormerGAN_SE_16K/last_best_checkpoint` pointer, SHA-256
`315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0`, under
ClearerVoice source revision `dcb1b20e1e44d435090072ab9b223c792ea1f624`. That
is not enough to run or qualify the candidate:

1. **Asset identity is not immutable.** The ledger records no immutable model
   artifact revision (`model_revision is absent`) and no retrieval-time download
   commit. The checkpoint bytes are known only by digest and byte count, the
   24-byte pointer content is not verified against `last_best_checkpoint.pt`,
   and neither artifact is present in this SDK worktree.
2. **The runtime is absent and unpinned.** The runtime is the external
   clearvoice 0.1.2 package (`ClearerVoice-Studio-clearvoice-0.1.2`) with
   PyTorch and the research requirements lock. It is not installed here, has no
   pinned wheel or sdist digest in this worktree, and
   `adapters/clearvoice/run.py` is not executed.
3. **Artifact-specific rights are not cleared.** Apache-2.0 is recorded for the
   code and for the model card at
   `https://huggingface.co/alibabasglab/MossFormerGAN_SE_16K`, but the card
   states open and private training data with exact corpus exposure
   undisclosed. Weight-specific terms, training-data provenance,
   redistribution and product-use clearance, and legal review are absent. No
   upstream portion may be copied, packaged, downloaded or redistributed.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result,
   target-runtime timing measurement or approved exact MossFormerGAN reference
   vector.

**Reopen condition.** Admit the candidate only when the exact
`MossFormerGAN_SE_16K` checkpoint bytes are addressed by an immutable model
artifact revision plus byte count and SHA-256 in a retrieval record; the 24-byte
pointer content is verified to name the checkpoint; both resolve from the
caller's own storage; a pinned `clearvoice` 0.1.2 runtime with a recorded digest
installs and runs `adapters/clearvoice/run.py` under the research requirements
lock; written artifact-specific terms and a rights/redistribution decision
exist; and a rights-cleared cohort, independent scorer, permitted listening,
exact reference outputs for these frozen inputs and target timing evidence are
available. Until then all nine release gates stay `blocked`.

The exact texts are duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per step.
- `registered=false`, `enabled_by_default=false`, `default_selected=false`,
  `descriptor_settings={}`, `public_api_abi_change=false`,
  `provider_registration=false`, `descriptor_registry_change=false`,
  `installed_v0_behavior_change=false`, `shared_build_or_ci_change=false`,
  `processor_exposure=false`, `task_board_or_handoff_write=false`.
- The task-local `adapter.json` is a proposal descriptor, not a provider. It
  advertises `modes=["offline"]`, `tasks=["CLN-01"]`, the external checkpoint
  plus pointer requirement and `asset_readiness="blocked"`.
- The caller-supplied asset contract is modelled metadata-only. No filesystem
  path enters configuration or errors, no bytes are read and no download is
  attempted.
- The upstream configuration fields are modelled exactly:
  `model_name`, `package_version`, `model_revision`, `checkpoint_dir`,
  `checkpoint_file`, `checkpoint_sha256`, `sample_rate`.

## Offline semantics modelled

The fixture models the boundary at the upstream adapter's offline contract:

- Input is mono 16 kHz `f32` in `[-1, 1]`. Empty, oversized, string, boolean,
  non-finite and out-of-range chunks are rejected before state changes.
- Caller chunks are buffered and the whole clip is enhanced once at `finish()`.
  Chunk sizes `1, 7, 80, 159, 160, 161, 320, 1280` and a single 32,000-sample
  call produce **identical** output digests, so the result is independent of
  caller chunking.
- The output has exactly the input length (`valid_samples=32000`), identity
  source-time mapping, `delay_compensation_samples=0` and `padded_samples=0`.
  The declared algorithmic lag is **0**; no latency is measured.
- A partial final frame is zero-padded **only for gain estimation**; it is
  counted as `internal_frame_padding_samples` and never emitted. The dedicated
  probe feeds 32,123 samples, reports 37 internal padding samples and returns
  32,123 output samples.
- A complete clip is required: `finish()` after `finish()` is rejected, and a
  second clip needs an explicit `reset()`. `reset()` restores the exact initial
  state and replay is bit-identical. A fresh independent session produces the
  same per-chunk state digest chain, and a foreign feed after `reset()` is
  bit-identical to a fresh session.
- The 24-byte pointer is modelled as a required auxiliary artifact whose
  stripped text must equal `last_best_checkpoint.pt`; its content is **not
  verified** in this worktree.
- Availability and all coordinates are source-sample positions on
  `fixture-sample-coordinate-not-device`. There is no wall clock, device clock,
  callback deadline, paced workload or latency measurement.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR, SI-SDR and STOI on the full clip, peak/clipping/nonfinite checks
and explicit unmeasured fields. STOI uses the pinned `pystoi` 0.4.1 against
authored synthetic clean references only: there is no rights-cleared real
cohort. Clean-speech preservation is `synthetic_only`, state/memory is
`synthetic_state_only`, content/availability timing is `blocked_unmeasured`,
listening is `not_run`, and real runtime/real clean references are `false`.

The surrogate is a deterministic soft amplitude mask: a 35th-percentile frame
power noise floor, 1.30 over-subtraction, mask exponent 0.85, gain floor 0.20
and attack/release smoothing over 160-sample frames, with interpolated gains and
one whole-clip pass. It is a boundary conformance fixture, not a model.

### Synthetic fixture results (not a candidate result)

Scores are computed on the same 32,000-sample clip for every variant. They
describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `quiet_speech` | 13.372167 | 15.096431 | +1.724264 | 13.370777 | 15.161676 | +1.790899 |
| `active_speech` | 10.565896 | 12.831191 | +2.265295 | 10.561038 | 12.748896 | +2.187858 |
| `low_snr_speech` | −8.278311 | 0.348578 | +8.626889 | −8.377887 | −8.289858 | +0.088029 |
| `onset_offset` | 13.637355 | 15.734594 | +2.097239 | 13.635536 | 15.701212 | +2.065676 |
| `clean_speech` | n/a | 30.174544 | n/a | n/a | 30.889250 | n/a |
| `idle_noise` | n/a | n/a | n/a | n/a | n/a | n/a |
| `silence` | n/a | n/a | n/a | n/a | n/a | n/a |

`clean_speech` has no additive noise, so its noisy SNR/SI-SDR are undefined
(`zero_error_identity_exact`). `idle_noise` and `silence` have a zero clean
reference; they are explicitly invalid and never scored as speech.

| Condition | Noisy STOI | Surrogate STOI | Δ STOI | RMS gain | Surrogate peak | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: |
| `quiet_speech` | 0.527064 | 0.705918 | +0.178854 | 0.927303 | 0.055542 | −0.655565 |
| `active_speech` | 0.500347 | 0.724994 | +0.224647 | 0.895483 | 0.241621 | −0.958850 |
| `low_snr_speech` | 0.410314 | 0.451478 | +0.041164 | 0.211590 | 0.062761 | −13.490118 |
| `onset_offset` | 0.473285 | 0.259053 | −0.214232 | 0.944455 | 0.175706 | −0.496372 |
| `clean_speech` | 1.000000 | 0.981705 | −0.018295 | 0.987517 | 0.132788 | −0.109107 |
| `idle_noise` | n/a | n/a | n/a | 0.206826 | 0.025962 | −13.687895 |
| `silence` | n/a | n/a | n/a | n/a | 0.000000 | n/a |

No output is clipped or non-finite; the largest synthetic peak is the
active-speech output at 0.241621.

### Clean preservation

| Condition | Target retention | Target projection SNR Δ dB |
| --- | ---: | ---: |
| `quiet_speech` | 0.934108 | +1.790899 |
| `active_speech` | 0.909624 | +2.187858 |
| `low_snr_speech` | 0.211028 | +0.088029 |
| `onset_offset` | 0.951772 | +2.065676 |
| `clean_speech` | 0.987090 | n/a (`zero_error_identity_exact`) |

The low-SNR stratum retains only 0.211 of the designated target while removing
interfering energy; that is over-suppression, not separation. The clean-speech
STOI falls from 1.000000 to 0.981705. These are fixture properties, not
MossFormerGAN behaviour.

### Honest regressions

Two regressions are recorded verbatim in `report.json:regressions`:

| Condition | Metric | Control | Control value | Surrogate | Delta |
| --- | --- | --- | ---: | ---: | ---: |
| `onset_offset` | `stoi` | identity | 0.473285 | 0.259053 | −0.214232 |
| `clean_speech` | `stoi` | identity | 1.000000 | 0.981705 | −0.018295 |

The mask attenuates the intentional silence between the two onset/offset
regions, so STOI collapses there even while SNR rises. The clean clip loses
STOI to the same gating. No threshold was tuned against real data, and no
metric was promoted to a qualification result.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_offline_chunked_160` is the 160-sample caller feed; the
  `surrogate_offline_whole_clip` control matches it byte-for-byte.
- Config rejections: wrong sample rate, channels, sample format, model name or
  package version, unsupported mode, surrogate without opt-in, an unavailable
  caller asset and a wrong checkpoint digest all fail before instance creation.
  A fully pinned synthetic admission control is created to prove the admission
  branch; it is explicitly not the candidate and implies no asset or rights.
- Frame rejections: empty, oversized, string, boolean, non-finite and
  out-of-range chunks fail with unchanged state digests.
- Lifecycle: process after finish/close, finish after finish/close and reset
  after close are rejected; close is idempotent; a zero-length clip finishes to
  no samples.
- The asset reference is `blocked` with exactly
  `model_revision_unpinned`, `download_revision_unrecorded`,
  `pointer_artifact_unverified`, `asset_bytes_absent`, `runtime_unavailable`
  and `rights_not_cleared`. No download, runtime call or byte read occurs.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic stimuli, caller-asset admission, surrogate session, metrics and report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its digest sidecar. |
| `contract.json` | Task-local contract, exact blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline adapter descriptor. |
| `readiness.json` | Strict readiness conclusion: blocked, not qualified, DEFER. |
| `test_reference.py` | 40 deterministic unittest checks, no network and no skips. |
| `verify.py` | Read-only strict pin, README digest-table, JSON, reproduction, disposition, licensing and scope verifier. |
| `requirements.lock` | Pinned evidence runtime (NumPy/SciPy/pystoi); not the ClearerVoice runtime. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for source, boundary and task-local pins. |
| `*.license` | REUSE sidecars for every generated artifact and the manifest. |

## Pinned source digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
`worktree:` paths are relative to this SDK worktree. Every row is machine-checked
against the file and against `SOURCES.sha256` by `verify.py`.

| Source/asset | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `clearvoice-mossformergan` record and Enhancement assignment. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Evaluated 30-pair DNS2020 candidate row. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Attention/GAN 16 kHz candidate note and five-clip screen. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Checkpoint/pointer digests, bytes, revision and license metadata. |
| `research/voice-enhancement-20261101/agent-mossformer-eval/REPORT.md` | `8e3171628b3c206cf5153bec13032b7087236756e2f8fcb855f9d40828e57a24` | Source-reported 30-pair report and timing caveats. |
| `research/voice-enhancement-20261101/agent-mossformer-eval/full30-results.json` | `467697784a5e331161bbc4b39e23eb3c58aca43901e52d0bec8ed8667d43bac5` | Source-reported item results, aggregates and intervals. |
| `adapters/clearvoice/adapter.json` | `ecc782d25d7d6421ac6a5cf7b219bbccd061a86df6000aab8e2a0a1e7c3253ff` | Existing adapter identity, tasks, modes and entrypoint. |
| `adapters/clearvoice/README.md` | `9807cd56073eb35cbef71145ac36487fecdab8cbfaa25741474d10a1af3f50d5` | Offline quality-reference scope and immutable-revision claim. |
| `adapters/clearvoice/requirements.lock` | `3914dfba56771fca024d3651db4af02e7a145fb751be7340ee1c39322cb8ab91` | Pinned ClearerVoice runtime package set; not installed here. |
| `adapters/clearvoice/run.py` | `c9896e8fbac4f6eca9e81bb322a17192382eab5ccca218e7c855f64750945d90` | Input range, identity mapping, zero delay/padding and pointer check. |

### Candidate asset identity (from the pinned ledger; not present or hashed here)

| Asset | Bytes | SHA-256 (ledger record) |
| --- | ---: | --- |
| MossFormerGAN_SE_16K/last_best_checkpoint.pt | 38,845,593 | `04bf00db575389e1ea8b1fcca48d9efcf073e50ad170e6dd5230df3bac98be27` |
| MossFormerGAN_SE_16K/last_best_checkpoint | 24 | `315744c841441f8831cb2f896e06102b4d864776bf272febaa30c639c903e1c0` |

The ledger has no `model_revision` and no retrieval record. These digests are
pinned provenance, not artifacts this package hashed, loaded or distributed.

### Source-reported values (provenance only)

The pinned research reports a complete 30/30 frozen DNS2020 quality result for
`ClearVoice MossFormerGAN_SE_16K`: mean SNR 20.70 dB, mean SI-SDR 20.69 dB and
mean STOI 0.9825, versus noisy identity 10.07/10.07/0.9332. Paired changes
versus identity are +10.64 dB SNR (95% CI +8.95 to +12.40), +10.62 dB SI-SDR
(+8.93 to +12.35) and +0.0493 STOI (+0.0386 to +0.0609). Paired SI-SDR
differences are +2.51 dB versus FastEnhancer Small (+2.10 to +2.92), +3.96 dB
versus DeepFilterNet3 (+3.20 to +4.79) and +0.57 dB versus ClearVoice FRCRN
(+0.39 to +0.77). Only the four tail items have adapter times: 105.74, 104.99,
117.59 and 104.96 seconds for 10-second files (RTF 10.50–11.76, median 10.53);
the tail worker wall was 449.74 seconds for 40 seconds of audio and sampled
process-tree peak RSS was 4.53 GB. The five-clip census screen reports mean
ΔSNR +7.91 dB and mean ΔSTOI +0.0461. The upstream ClearerVoice SpeechScore
table reports PESQ 3.57, STOI 0.98, SI-SDR 20.60, P.808 MOS 4.05 and
SIG/BAK/OVRL 3.58/4.18/3.36. All of these values are **not reproduced**, not
pooled with the synthetic numbers above, not device timing and not a quality or
release claim. They are transcribed only to preserve the separation required by
the Enhancement profile.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. `SOURCE_ROOT` is
needed by the verifier and tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CLEARVOICE-MOSSFORMERGAN
TASK=$WT/docs/task-evidence/clearvoice-mossformergan
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/mossformergan-ci
python3 -m reuse lint
git diff --check
```

`run.py` regenerates the contract, adapter, readiness, report, digest sidecar
and source manifest. `report.json` is canonical JSON (`sort_keys=True`,
`indent=2`, `allow_nan=False`, negative zero normalized) plus one trailing
newline. Regeneration and three cold-start interpreter processes are
byte-identical.

## Expected counts and digests

- Seven conditions, 32,000 samples each; 224,000 synthetic observed samples.
- Eight chunk sizes plus one whole-call control; all outputs digests identical.
- Output 32,000 samples per full 32,000-sample clip; 0 emitted before `finish`;
  identity source-time mapping; 0 delay compensation; 0 emitted padding.
- Partial-final-frame probe: 32,123 input/output samples, 37 internal padding
  samples, 0 emitted padding.
- `report.json` SHA-256:
  `5c806186d35c1f39021617dc5649bf32d87030a1a059d26e35492a69ee1a7afc`
  (69,171 bytes).
- Tests: **40 passed, 0 failed, 0 skipped** (Python 3.12.16).

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Immutable model artifact revision + byte count + SHA-256, verified pointer and caller-held bytes. |
| `runtime_admission` | blocked | Pinned `clearvoice` 0.1.2 runtime artifact with digest, terms and installed execution. |
| `artifact_rights` | blocked | Written weight/runtime/training-data terms and a redistribution/product-use decision. |
| `exact_reference_parity` | blocked | Approved MossFormerGAN reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target timing, throughput, memory and offline availability evidence. |
| `provider_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

## Separation from other ClearVoice work

The sibling `docs/task-evidence/clearvoice-frcrn-16khz/` package is a different
candidate with a different checkpoint and is not pooled with this evidence. The
research-workspace `adapters/clearvoice/` files, the candidate matrix, census,
asset ledger and `agent-mossformer-eval` reports are pinned external provenance.
They were not executed, imported, pooled or reinterpreted here, and the
30-pair and five-clip values are never treated as evidence for the surrogate.
