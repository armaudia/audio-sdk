<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CLEANUNET-DNS-LARGE-HIGH — caller-supplied-asset whole-clip blocker evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`CleanUNet DNS-large-high` (`component_id=cleanunet-dns-large-high`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json` and
defined in `plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
candidate.

This package models the offline boundary as a **caller-supplied external asset
reference**, exactly as `CONTRACTS.md` `as_asset_v0` requires: an asset ID, byte
count, SHA-256 and `storage=external`, supplied by the caller, with no provider
file access and no download. The pinned candidate cannot cross that boundary
here, so there is **no candidate output**, real corpus, listening result, device
timing, benchmark or release claim.

The exact upstream **source** is present at
`data/checkouts/cleanunet` (commit `2f930ce…`), and the checkpoint identity is
pinned by an immutable Git LFS oid. The **checkpoint bytes and the PyTorch CPU
runtime are absent**, so nothing was deserialized or executed. This package
contains a deterministic stdlib **synthetic whole-clip surrogate** that exercises
only the documented accounting and refusal mechanics; it is explicitly opt-in,
is not CleanUNet, and substitutes for no gate.

## Exact external blocker

The pinned ledger records
`exp/DNS-large-high/checkpoint/pretrained.pkl` at immutable commit
`2f930ce6660e76b6265c07da4027b414adb24ab1` as LFS object
`sha256:513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829`,
184,336,765 bytes, staged at
`data/models/cleanunet/dns-large-high/pretrained.pkl`. That is not enough to run
or qualify it:

1. **The checkpoint bytes are absent.** The LFS pointer and source commit pin the
   identity exactly, but the staged `pretrained.pkl` is not present in the
   workspace and no bytes were downloaded or read. No `torch.load` was attempted.
2. **The CPU runtime is absent and unpinned.** The pinned evaluation used
   CPython 3.11.5, PyTorch 2.14.1 and torchaudio 2.11.0 in
   `data/envs/clearvoice`; that environment is gone, no PyTorch is installed for
   the available interpreters, and no wheel, hash lock or environment digest is
   pinned here. The official `denoise.py` hard-codes `.cuda()`; CPU placement is
   an adapter-local change, not an upstream contract.
3. **Artifact-specific rights are not cleared.** MIT covers the pinned repository
   source. The LFS checkpoint has no separate written artifact terms, DNS2020
   training-data provenance is not stated for redistribution or product use,
   legal review is absent, and deserializing a 177 MB external pickle requires a
   trusted-origin decision. No upstream portion may be copied, packaged or
   redistributed by this package.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort, independent clean-reference scorer, permitted listening result, target
   pacing/deadline measurement or approved exact whole-clip reference vector for
   these frozen inputs.

**Reopen condition.** Admit the candidate only when caller-held bytes at
`data/models/cleanunet/dns-large-high/pretrained.pkl` match 184,336,765 bytes and
SHA-256 `513d9e4f69483bf2bcc3059dd6b3644140763bf3f22df41d7ee366cc2cbd1829` and
are tied to the immutable LFS oid at commit `2f930ce…`; a pinned CPython/PyTorch
CPU runtime with a recorded wheel or environment digest installs; written
checkpoint, runtime and DNS2020 training-data terms plus a rights/redistribution
decision exist; and a rights-cleared cohort, independent scorer, permitted
listening and exact whole-clip reference outputs for these frozen inputs are
available. Until then all eight release gates stay `blocked`.

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
  (`tasks[id=SDK-CLEANUNET-DNS-LARGE-HIGH]`, stable-field digest). The mutable
  full `plan/swarm/TASKS.json` is never hashed or pinned.

## Whole-clip semantics modelled

The fixture models one complete caller-owned clip of 1 to 160,000 samples
(10 s, the upstream training crop length). There is no incremental, streaming,
flush or reset protocol.

- One `process_clip` call consumes the complete clip and returns exactly one
  output sample for every input sample. A second call fails with
  `offline_clip_already_complete`; there is no method to append, flush or reset.
- The pinned `CleanUNet.forward()` normalises by the **whole-clip** standard
  deviation (`torch.std(dim=2)` with Bessel correction) plus `1e-3`, pads with
  `padding(x, D=8, K=4, S=2)`, runs the network, crops to the input length and
  multiplies by the same standard deviation. The surrogate reproduces that
  accounting exactly: the padded length is `256 * bottleneck_length + 510`
  (254 modulo 256), never below the input, and the padding is discarded by the
  crop. A 32,000-sample clip pads 254 samples internally and emits 32,000; a
  10-second clip pads 254 and emits 160,000.
- A 32,123-sample control pads 131 samples internally and still emits 32,123.
- Extending a 16,000-sample prefix with future audio changes all 16,000 prefix
  samples, so a prefix is not final before the full clip is supplied.
  `prefix_not_final_before_full_clip` is `true`.
- Processing the two halves independently changes 30,533 of 32,000 samples versus
  the whole clip. Independent segment processing is therefore not offline
  equivalent; the control is recorded, not hidden.
- The whole-clip normalisation is only approximately scale-equivariant, because
  the additive `1e-3` term does not scale with the input. Doubling the input and
  halving the expected output leaves a relative difference of about `2.2e-15`;
  this is recorded as `scale_equivariance_approx=true`,
  `scale_equivariance_exact=false`.
- A fully silent clip is exactly zero (degenerate std → `1e-3`, zero input).
- An independent frame-loop path over the same gain sequence is byte-identical
  to the contiguous whole-clip path.
- A synthetic impulse probe preserves the peak index exactly
  (`input=4000`, `output=4000`). No algorithmic lag, content delay, latency or
  device timing is modelled or measured.
- Sessions are one-shot and stateless across clips: replaying a clip is
  bit-identical, and no state is carried. Availability and all coordinates are
  source-sample positions on `fixture-sample-coordinate-not-device`. There is no
  wall clock, device clock, callback deadline, paced workload or end-to-end
  latency measurement.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SNR and SI-SDR on a common full output length, peak/clipping/nonfinite
checks and explicit unmeasured fields. STOI is `blocked_unmeasured` (no
rights-cleared clean-reference cohort and no installed scorer), clean-speech
preservation is `synthetic_only`, state/memory is `stateless_synthetic_only`,
content/availability timing is `blocked_unmeasured`, listening is `not_run`,
and real runtime/real clean references are `false`.

### Synthetic fixture results (not a candidate result)

Scores are computed on the same 32,000-sample clip for every variant. They
describe the surrogate only.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Noise attenuation dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 6.953471 | 7.239835 | +0.286365 | 6.961875 | 6.939884 | -0.021991 | -3.089986 |
| quiet_speech | 4.553064 | 5.795628 | +1.242564 | 4.533636 | 4.517168 | -0.016468 | -3.088108 |
| low_snr_speech | -5.176332 | -2.340617 | +2.835715 | -5.230262 | -5.234969 | -0.004706 | -3.075520 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -3.063672 |
| onset_offset | 3.218529 | 5.755372 | +2.536843 | 3.175917 | 4.701665 | +1.525747 | -1.864740 |

`idle_noise` has no target, so SNR/SI-SDR are not applicable; only the RMS
change is reported. No output is clipped or non-finite; the largest synthetic
peak is the low-SNR output at about 0.471.

### Honest regressions

Three small SI-SDR regressions are recorded verbatim in
`report.json:regressions`: `active_speech` -0.021991 dB, `quiet_speech`
-0.016468 dB and `low_snr_speech` -0.004706 dB versus the noisy control. The
global noise reference attenuates the target as well as the noise, so SI-SDR can
fall while SNR rises. These are properties of the synthetic fixture, not evidence
about CleanUNet, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact, and its metrics equal the noisy control.
- `noisy_control` is the observed input scored against the synthetic target.
- `surrogate_whole_clip` is the one-call whole-clip path; the independent
  `surrogate_frame_loop_control` must match it byte-for-byte.
- `surrogate_split_halves` must not match the whole clip; its difference is a
  boundary control, not a quality result.
- Config rejections: wrong sample rate, channels, sample format, frame size or
  maximum clip, unsupported streaming mode, unavailable candidate asset, altered
  asset identity/byte count, and surrogate without opt-in all fail before
  instance creation. A fully pinned synthetic admission control is created to
  prove the admission branch; it is explicitly not the candidate and has
  `qualification_effect=none`.
- Clip rejections: empty, oversized, string, boolean, non-finite, infinite and
  out-of-range clips fail with unchanged state digests; a second clip and any
  post-close call fail closed.
- Lifecycle: one call only, close is idempotent, and there is no `process`,
  `flush` or `reset` streaming API to call.
- The pinned padding helper was exercised on boundary lengths; it never
  truncates and its result is 254 modulo 256, not a 256 multiple. This is a
  source-derived accounting control, not a candidate output.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, blockers, modelled boundary, results, pins, commands, gates. |
| `reference.py` | Deterministic signals, whole-clip surrogate, padding contract, accounting, metrics and report/contract model. |
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
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | Candidate-matrix `CleanUNet DNS-large-high` record. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Model family, checkpoint and LFS description. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-readiness/REPORT.md` | `16be8783b1345d96b65f910fe6364b0996f925c82744b07185d4420f2346b148` | Source/checkpoint identity and CUDA-only reference path. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/REPORT.md` | `062e30c97843d257cabd251ce6991b21d578c5fb96df75e9f3b1399524da66fa` | Recorded 30-pair metrics, runtime versions and clean diagnostics. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.json` | `d224b980b6444d5ea190645c17fcfebe9d05fe8a8db276c91f3be115ebdc0af7` | Evaluation adapter descriptor. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.lock.json` | `255b756d46e02c1bddc69167e772dfec587d1d36190aa1364bb11bd68fd4a9ab` | Exact checkpoint and source file pins. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/adapter.py` | `39d401019b4db443194bbfb6973660a6a8eee672e3b76a7a27e6fa5dcfb24c8e` | CPU adapter: hash check, strict state dict, whole waveform. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/cleanunet_noisy_results.json` | `84ef5edd19ccb2b464b42c30b150c1cfd219e64bf94bc8ac2e47f3a0b621ee4c` | Per-item noisy results and paired aggregates. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-eval/cleanunet_clean_results.json` | `0152c89e9caa0e0d1e237f5f86aacdcda018bfbb393cd8a7eb90364dc23d8515` | Clean-input diagnostics. |
| `source:research/voice-enhancement-20261101/agent-cleanunet-result-audit/REPORT.md` | `2456cd2c570ef79d55a82169c9fb00488554fd3611a95140848a466ecf87f93f` | Independent result-integrity audit. |
| `source:research/voice-enhancement-20261101/evaluation_records.md` | `962bd5a8f75e64a7ba22bc51ff26cb5bdb648002544c87cacbef64dad62d723a` | Coordinator register and overlap caveat. |
| `source:REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Runtime/quality summary and whole-utterance note. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `source:data/checkouts/cleanunet/configs/DNS-large-high.json` | `e2a115f1a5e983b22fc6a2e95bca27c4f93625390205327575d9b963467b5063` | Exact network configuration. |
| `source:data/checkouts/cleanunet/network.py` | `c5ba1b7bb4ad7afc4697e597bc5a373715ed7d73af36d8043a9f971d56926957` | Pinned forward, normalisation and padding helper. |
| `source:data/checkouts/cleanunet/util.py` | `619bd6ac680b6432816a15fd302881e2100baea6e83ceef4d61e23a19cf1ef7f` | Pinned sampling helper. |
| `source:data/checkouts/cleanunet/LICENSE` | `da9858d516047d82096d01c112a61bd67f26d289039464d668a1d45f91738ecc` | MIT source license text. |
| `source:data/checkouts/cleanunet/README.md` | `ba48ec3c4e4a7b1afad57f4fbb0f34a7f76087f3ec5c2652e1c84cd5546796e7` | Upstream scope, LFS and no-reverb limitation notes. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | `as_asset_v0` external asset and no-download rule. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |

### Source-reported values (provenance only)

The pinned evaluation records 30 DNS2020 pairs: mean ΔSNR +9.0947 dB
(95% paired interval [7.7225, 10.5831], 30/30 wins), mean ΔSI-SDR +9.1951 dB
([7.7724, 10.6572], 30/30 wins), mean ΔSTOI +0.04436 ([0.03436, 0.05521],
30/30 wins), mean inference-only RTF 0.03976 (median 0.03955, p95 0.04102, max
0.04217) and noisy-worker peak child RSS 1,021,964,288 bytes. On 30 clean inputs
the output averaged STOI 0.99958 with ΔSTOI -0.000417 ([−0.000718, −0.000194],
0/0/30 wins/ties/losses), mean SI-SDR 37.31 dB, mean SNR 33.36 dB and mean RTF
0.03967. The 10-second smoke completed in 0.4437 s (RTF 0.04437, peak child RSS
1,014,824,960 bytes). The runtime was CPython 3.11.5 with PyTorch 2.14.1 and
torchaudio 2.11.0 on CPU; no lock or wheel digest for it is pinned. The local
subset belongs to the DNS2020 no-reverb test family, so it is a
reproduction/comparative screen, not independent generalization evidence. The
published inference path is whole-utterance only; the bottleneck uses a causal
attention mask, but no streaming state, callback or delay is claimed. All these
values are transcribed only to preserve the separation required by the Evidence
profile and are not pooled with the synthetic numbers above, not device timing
and not a quality or release claim.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CLEANUNET-DNS-LARGE-HIGH diff --check
```

`run.py --all` regenerates the report, digest sidecar, README digest table,
contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical; the test suite performs the full
three-run regeneration in an isolated copy.

## Expected counts and digests

- Five conditions, 32,000 samples each; 160,000 synthetic observed samples.
- One complete whole-clip call per variant per condition; 200 frames per full
  clip; no startup, tail or flush samples in the emitted output.
- Eleven config adverse cases (ten rejections plus one synthetic admission
  control); nine clip adverse cases; all rejections leave state unchanged.
- 32,123-sample partial-tail control: 32,123 output samples, 32,254 official
  padded length, 131 internal padding samples discarded.
- A 32,000-sample clip pads 254 samples; a 160,000-sample (10 s) clip pads 254.
- Extending a 16,000-sample prefix to 32,000 changes all 16,000 prefix samples;
  independent half-clip processing changes 30,533 of 32,000 samples.
- `report.json` SHA-256 and byte count are in the table below.
- Eight release gates, all `blocked`.

<!-- DIGEST_TABLE_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `reference.py` | `ae93970837359afff707125e435792ba884b7a9335490c1177b0a0529b0e23fe` | 64582 |
| `report.json` | `23289aecb0e5b502e92a14ee43f2d94be0a2a069b466eebeb7f6281e58a84468` | 39931 |
| `report.json.sha256` | `d0adeed33b243a655da4a1ee59054f191f23f872475d046d0f4410fd34ffb6a9` | 78 |
| `run.py` | `5cf767ca8723e358f7e29b29b11a95b5d9aa32c99e554116aa2804b85aa0530b` | 6000 |
| `test_reference.py` | `d087cacce8001201283446483a4ff5066e0828f9cefae54598eb10fdc6c0feda` | 26712 |
| `verify.py` | `d290c2841dc942fe950392c48ff888ef5a6c55686c3513a29e1436cfe3183946` | 18153 |
<!-- DIGEST_TABLE_END -->

## Gates (all blocked)

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | blocked | Caller-held bytes matching the pinned LFS oid, byte count and SHA-256. |
| `runtime_admission` | blocked | Pinned CPython/PyTorch CPU runtime artifact with a recorded digest and terms. |
| `artifact_rights` | blocked | Written checkpoint/runtime/training-data terms, pickle-trust and redistribution decision. |
| `exact_reference_parity` | blocked | Approved whole-clip reference outputs for the frozen inputs. |
| `rights_cleared_paired_cohort` | blocked | Paired real speech cohort with clean references and overlap statement. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target whole-clip latency, memory, pacing and deadline evidence. |
| `provider_intake_and_default_selection` | blocked | Opt-in provider intake, OFF default, review and explicit default decision. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.
