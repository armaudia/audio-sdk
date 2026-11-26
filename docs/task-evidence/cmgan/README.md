<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CMGAN — CMGAN feasibility and caller-supplied-asset boundary evidence

`audio-sdk/cmgan/0.1`

| Field | Value |
| --- | --- |
| Decision | **DEFER** |
| Status | **incomplete** |
| Disposition | **proposal only** |
| Qualification | **not_qualified** |
| Qualifying results | **0** |
| Blocked release gates | **8** |
| Open exact blockers | **4** |
| Profile | Enhancement (`plan/swarm/VERIFICATION.md`) |
| Mode | feasibility |
| Pinned base | `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |

This directory is a bounded, task-local feasibility package for **CMGAN**
(`component_id=cmgan`). It is **not** a provider, adapter, benchmark or release.
The official MIT source and the exact tracked checkpoint were verified, the
upstream task geometry was extracted from the pinned source, and the offline
whole-clip boundary was modelled as a caller-supplied external asset reference.
The candidate still cannot be executed or qualified here, so the disposition
stays `DEFER` / `incomplete` / `not_qualified`. Nothing in this package is a
CMGAN result.

## What was verified

- **Runnable source is present and pinned.** The official repository
  `ruizhecao96/CMGAN` is staged at revision
  `39946005d9b66fa1e824edf4bb6bc9a06088e443` (2024-05-03), MIT licensed.
  `src/evaluation.py`, `src/models/generator.py`, `src/models/conformer.py`,
  `src/utils.py`, `src/requirements.txt` and `LICENSE` were hashed and match the
  recorded identities.
- **The exact checkpoint exists and is immutable.** `src/best_ckpt/ckpt` is a
  tracked Git blob, not an undocumented download: blob
  `cbafab9a5fe739f3662c65cfe7be009dc475e0d1`, **7,488,051 bytes**, SHA-256
  `e57af0ccc3ef1b0ddc6434926d08f34ac3fdbcb1ff17783c00de17a1202f6bcf`. The
  bytes were hashed from the already-staged checkout; this task downloaded
  nothing and copied nothing into the SDK worktree.
- **Task geometry is exact.** Official inference is 16 kHz mono, `n_fft=400`,
  `hop=100`, hamming window, `onesided`, power-0.3 STFT compression,
  `TSCNet(num_channel=64, num_features=201)`, 16-second cut, whole-clip RMS
  normalization, wrap padding to a 100-sample multiple and batch reshape when
  the padded clip exceeds 16 s. Output is length-preserving with identity source
  time mapping and zero declared lag.
- **Permitted scope is unchanged.** No provider, descriptor, registry, default,
  installed-v0 behavior, ABI, `CONTRACTS.md`, shared build, CI, board or handoff
  file changes. Only this directory is added.
- **Matched evidence does not exist.** The candidate matrix row is
  `unavailable/blocked`; the noise-suppression census keeps CMGAN outside the
  runnable count; no 30-pair DNS2020 or EARS result exists; the recorded CPU
  smoke produced zero outputs. There is no CMGAN result to pair with the
  declared FastEnhancer / ClearVoice FRCRN baselines.

## Exact external blocker

**PRIMARY: no execution environment for the exact pinned model exists in this
task.** The upstream evaluation path requires CUDA: `src/evaluation.py` calls
`.cuda()` and the pinned requirements are `torch==1.10.0+cu113` /
`torchaudio==0.10.0+cu113`. The recorded host is macOS arm64 with no CUDA
device; the pinned Python 3.12.16 interpreter has no `torch`; and no pinned,
validated CPU or alternate-accelerator artifact with a recorded digest exists.
The recorded CPU-only smoke (`cmgan_smoke-retry01.json`) entered STFT
preprocessing and hit the **1,200 s** worker bound with **zero outputs** and
**4,143,202,304 B** peak child RSS. There is no stage telemetry proving the
model forward began, and the 1,200 s bound is **not** an RTF or inference time.
Consequently no exact CMGAN reference output exists and the candidate cannot
enter the matched-cohort protocol.

The other three open blockers are:

1. **No matched qualification evidence** — no 30-pair DNS2020 or EARS output, no
   paired SI-SDR/STOI against a clean reference, no clean-speech preservation
   result, no permitted listening and no independent scorer run.
2. **Artifact-specific rights and training-data provenance are not cleared** —
   the repository is MIT and the checkpoint is tracked there, but there is no
   separate weight-specific model card or terms text; VCTK-DEMAND dataset terms,
   redistribution clearance and product-use review are absent.
3. **No target timing, memory, availability, provider intake or release review**
   — nothing is measured on any intended runtime, and no opt-in adapter exists.

**Reopen condition.** Reopen execution only when a pinned runtime artifact
(exact PyTorch build and wheel digest, host OS/architecture, accelerator identity
and driver) loads the exact checkpoint blob
`cbafab9a5fe739f3662c65cfe7be009dc475e0d1` (SHA-256
`e57af0ccc3ef1b0ddc6434926d08f34ac3fdbcb1ff17783c00de17a1202f6bcf`) and
completes the official `enhance_one_track` geometry with a finite,
length-preserving output on a frozen caller-owned synthetic input inside the
bounded worker, with a recorded reference vector. Qualification then requires
the frozen common 30-pair DNS2020 no-reverb cohort, an independent
clean-reference scorer, a clean-speech/silence check, permitted listening and
target timing. Rights and provider intake remain independent gates. A missing or
failed item re-blocks the gate; it never qualifies the candidate.

## Asset identity

| Field | Value |
| --- | --- |
| Candidate | `ruizhecao96/CMGAN-TSCNet` |
| Source | `https://github.com/ruizhecao96/CMGAN` |
| Revision | `39946005d9b66fa1e824edf4bb6bc9a06088e443` |
| Checkpoint | `src/best_ckpt/ckpt` |
| Bytes | `7,488,051` |
| SHA-256 | `e57af0ccc3ef1b0ddc6434926d08f34ac3fdbcb1ff17783c00de17a1202f6bcf` |
| Git blob | `cbafab9a5fe739f3662c65cfe7be009dc475e0d1` |
| Code licence | MIT |
| Weight terms | MIT repository `LICENSE`; no separate model card or weight terms |
| Training data | VCTK-DEMAND 16 kHz; not cleared here |
| Upstream runtime | `torch==1.10.0+cu113`, `torchaudio==0.10.0+cu113` |

The asset is **caller-supplied and external**. The package records an asset ID,
byte count, SHA-256, revision and licence metadata; it never reads a path, opens
a checkpoint, accesses provider storage or downloads anything. `asset_admission`
admits exactly this schema as a **schema control only** (`qualifies=false`) and
rejects provider storage, provider file access, download flags, a wrong digest,
wrong bytes, a wrong blob, a wrong licence, a wrong revision, missing fields and
unknown fields with exact codes.

## Task geometry

| Parameter | Value |
| --- | --- |
| Sample rate / channels / format | 16,000 Hz / 1 / `f32` |
| Frame | 160 samples (unchanged public v0 geometry) |
| STFT | `n_fft=400`, `hop=100`, hamming, `onesided` |
| Frequency bins | 201 |
| Model | `TSCNet(num_channel=64, num_features=201)` |
| Compression | magnitude power `0.3`; inverse `1/0.3` |
| Cut length | 256,000 samples (16 s) |
| Normalization | `c = sqrt(length / sum(x^2))`, inverse-scaled output |
| Padding | wrap the tail to the next 100-sample multiple |
| Batching | reshape the padded clip into equal 16 s rows |
| Output | input length, identity source mapping, 0 declared lag, 0 emitted padding |
| Streaming | no public streaming API |

The geometry block reproduces the declared arithmetic only: `32,000 → 0` wrap
padding, `32,123 → 77`, `256,000 → 1` batch, `256,001 → 2` batches and
`1,000,000 → 4` batches. Every probe is length preserving. No STFT or model
operation is executed.

## Offline boundary and synthetic controls

The caller boundary buffers chunks and enhances the whole clip once at
`finish()`. Output length equals input length for every condition. Chunk sizes
`1, 7, 80, 159, 160, 161, 320, 1280` and one whole-call control produce
**identical** output digests, so the surrogate result is independent of caller
chunking; 37,699 caller chunks are accounted for in the boundary record.

A deterministic stdlib **soft-gate surrogate** exercises only the boundary
mechanics. It is explicitly opt-in, is not CMGAN, loads no weights and
substitutes for no gate. Its scores describe the surrogate only and are
**never** pooled with CMGAN or upstream numbers.

| Condition | Noisy SNR dB | Surrogate SNR dB | Δ SNR dB | Noisy SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | RMS change dB |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| active_speech | 9.839754 | 6.430400 | -3.409354 | 9.814743 | 9.131618 | -0.683125 | -4.849086 |
| idle_noise | n/a | n/a | n/a | n/a | n/a | n/a | -11.747518 |
| low_snr_speech | -11.568511 | -2.239425 | +9.329086 | -11.335822 | -10.273670 | +1.062152 | -10.549343 |
| onset_offset | 8.988580 | 14.184429 | +5.195849 | 8.988062 | 14.734899 | +5.746837 | -1.348941 |
| quiet_speech | 11.414742 | 6.497158 | -4.917584 | 11.426454 | 9.929194 | -1.497260 | -4.899872 |

No output is clipped or non-finite. The largest synthetic peak is the
onset-offset output at about 0.271.

### Honest regressions

Four regressions are recorded verbatim in `report.json:regressions`:

| Condition | Metric | Noisy control | Surrogate | Delta |
| --- | --- | ---: | ---: | ---: |
| quiet_speech | snr_db | 11.414742 | 6.497158 | -4.917584 |
| quiet_speech | si_sdr_db | 11.426454 | 9.929194 | -1.497260 |
| active_speech | snr_db | 9.839754 | 6.430400 | -3.409354 |
| active_speech | si_sdr_db | 9.814743 | 9.131618 | -0.683125 |

The surrogate uses a 25th-percentile frame-RMS noise floor and a fixed gain
floor, so quiet and active speech are over-suppressed. This is a property of the
fixture, not evidence about CMGAN, and no threshold was tuned against real data.

## Controls and adverse cases

- `identity_passthrough` is exact and scores identically to the noisy control in
  every condition.
- The noisy control, 160-sample chunked feed and whole-clip control are all
  recorded; chunked output is byte-identical to the whole clip.
- Config rejections: wrong sample rate, channels, format, model name, revision,
  checkpoint digest/bytes, `n_fft`, hop, cut length, channel count, feature
  count, power exponent, unsupported mode and surrogate use without opt-in.
- Asset rejections: provider storage/file access, any download flag, wrong IDs,
  wrong revision/path/bytes/blob/digest, malformed digest, wrong licence and
  missing/unknown fields.
- Frame rejections: empty, oversized, string, boolean, non-finite and
  out-of-range chunks fail with unchanged state digests.
- Lifecycle: finish twice, feed after finish and feed after close are rejected;
  reset after finish is allowed and restores the initial state; close is
  idempotent; a zero-sample clip finishes to zero samples.
- The 32,123-sample tail probe reports 77 wrap-padding samples and returns
  32,123 output samples with 0 emitted padding.

## Matched evidence (not reproduced)

The pinned candidate matrix records CMGAN as `unavailable/blocked`: the official
checkpoint is staged and hash-pinned, but one 10-second CPU smoke timed out at
1,200 s after entering STFT preprocessing, with no output, 4.14 GB peak RSS and
no quality score. The census kept CMGAN as a follow-up research lead outside the
runnable candidate count at screen time; its no-checkpoint note is superseded by
the later hash-pinned attempt. The declared comparison baselines are FastEnhancer
and ClearVoice FRCRN; **no CMGAN output exists to pair with either**.

The upstream README reports VoiceBank+DEMAND PESQ **3.41** and SSNR
**11.10 dB**. These are author-reported upstream values, not local measurements;
they are not reproduced, not pooled with the synthetic table above and not
evidence for this host.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, verification, blocker, geometry, results, pins, commands, gates. |
| `reference.py` | Deterministic model: asset admission, geometry, surrogate boundary, metrics, report/contract/adapter/readiness. |
| `run.py` | Regenerates the adapter, readiness, report, digest sidecar, README digest table, contract and source manifest. |
| `report.json` / `report.json.sha256` | Canonical Enhancement report and its SHA-256 sidecar. |
| `contract.json` | Task-local contract, asset identity, blockers, reopen conditions and pins. |
| `adapter.json` | Proposal-only, unregistered offline descriptor; no entrypoint. |
| `readiness.json` | Strict readiness conclusion: not ready, blocked, DEFER. |
| `test_reference.py` | 38 deterministic standard-library checks, no network and no skips. |
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
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | CMGAN record 15 (CSV line 16): `unavailable/blocked`, CPU smoke timeout, baselines. |
| `source:research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Follow-up lead; outside the runnable count. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/REPORT.md` | `5ccd8a6bc2d9af5415df9898cf85c3c35835285102c5592bbc66ba326eb2e8d8` | Exact prior attempt, adapter and disposition. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/adapter.json` | `b8fa25e178d19c851804894153a92e3863463baab7e78ff645b261c2a369ffed` | Prior adapter identity, task and mode. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/adapter.lock.json` | `49d7f0b1d53702f89ca33768f45c5dabde5a1f96ecb041d6caaff31ced0061b2` | Checkpoint and source digests, geometry. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/adapter.py` | `16cca93d81ba25a0bb71f2ed5c9f0556c3d13a20f05ad9267afc530971fb7c22` | CPU adapter source; not executed here. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/run_cmgan.py` | `42e61fc0d9eb3c4463b908a1dd2d30daed1aa87aa761d07affd2f51e117bfbc6` | Prior runner; not executed here. |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/cmgan_smoke.json` | `1fced1439b019ce3ec1136275df129f37654d2e6a87db42a3483cd0e2f7b0625` | First smoke failure (wrong path). |
| `source:research/voice-enhancement-20261101/agent-cmgan-eval/cmgan_smoke-retry01.json` | `d9c26a61501a1d8ebbd8278b3a91156fcaeaccf3ede005f20fb2f1df4f430075` | 1,200 s timeout, zero outputs, 4.14 GB RSS. |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Component/profile assignment. |
| `worktree:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | External asset and no-download boundary. |
| `worktree:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table. |
| `worktree:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade. |
| `worktree:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` | `docs/**` Apache-2.0 annotation. |
| `worktree:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` | Shared license text. |
| `worktree:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` | Unchanged build entry. |
| `worktree:README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` | Unchanged public surface. |
| `worktree:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` | Unchanged CI. |

The mutable full `plan/swarm/TASKS.json` is **never hashed**. Only the stable
component row (`component_id`, `verification_profile`, `task`) is read; board
status, claim and review fields gate nothing.

## Reproduction

Use the pinned interpreter and keep bytecode out of the tree. Run from this
directory:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 check_licensing.py
python3 -m reuse lint
git -C /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-CMGAN diff --check
```

The installed-package SDK check runs from the worktree root with the pinned
interpreter after installing `requirements-build.txt`:

```sh
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py
```

`run.py --all` regenerates the adapter, readiness, report, digest sidecar, README
digest table, contract and source manifest. `report.json` is canonical JSON
(`sort_keys=True`, compact separators, `allow_nan=False`, negative zero
normalized) plus one trailing newline. Regeneration and three cold-start
interpreter processes are byte-identical.

## Expected counts and digests

- Five synthetic conditions, 32,000 samples each; 160,000 synthetic samples.
- Eight chunk sizes plus one whole-call control; 37,699 caller chunks total.
- Output 32,000 samples per full clip; 0 emitted before `finish`; identity
  source-time mapping; 0 delay compensation; 0 emitted padding.
- Tail probe: 32,123 input/output samples, 77 wrap-padding samples, 0 emitted.
- Four honest surrogate regressions; no clipped or non-finite output.
- Tests: **38 passed, 0 failed, 0 skipped** (Python 3.12.16).

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `adapter.json` | `06a174fd637463073a77d75e3dbf121035dfd4fc1d5cac43f6a29909ce973077` | 1133 |
| `readiness.json` | `f005c863d0b9e2f89b8f48a086c6fa7668864656df071f10a16b8b5b9ad9fbc3` | 6416 |
| `reference.py` | `8235782f7f76dd7deedd42626b668052bd742da2069b414b1a6f9f152d4c05b8` | 61310 |
| `report.json` | `74b83ced780a6add471af7b36e5a27b011fc32ae5be4f7f371cab91b8af5d8ad` | 28627 |
| `run.py` | `79e46452cec6db6300a453a98a1cc16d2b0a82c5503956bfc3562bd5aee9f24d` | 5967 |
| `test_reference.py` | `1e58bc6f00a08ea0b80c6ce7c7f789b10b9631bfd0b2c56f45b4ab78485ec92a` | 14123 |
| `verify.py` | `cd323d12a8734da3b878cf0bce2a217dbbda9ba98916b7431bc484ec369c6baf` | 30737 |
<!-- digest-table:end -->

## Gates

| Gate | Status | Reopening condition |
| --- | --- | --- |
| `exact_asset_identity` | **clear** | Verified immutable revision + tracked blob + byte count + SHA-256 from the staged checkout; no download. |
| `runtime_admission` | blocked | Pinned PyTorch/accelerator artifact with digest and a completed exact inference. |
| `artifact_rights` | blocked | Written weight, training-data and redistribution terms plus a rights decision. |
| `exact_reference_parity` | blocked | Approved exact CMGAN reference outputs for the frozen inputs. |
| `rights_cleared_cohort` | blocked | Paired real speech cohort with clean references. |
| `independent_scoring_and_listening` | blocked | Independent scorer and permitted listening. |
| `target_runtime_timing` | blocked | Target timing, memory, availability and content delay. |
| `provider_intake` | blocked | Opt-in provider intake, OFF default, independent review. |
| `public_default_selection` | blocked | Explicit owner default decision after intake. |

No missing result qualifies the candidate. This task remains
`proposal_only_synthetic_incomplete` / `not_qualified` / `DEFER`.

## Non-claims

- No result in this package is a qualification, benchmark, quality or release claim.
- The deterministic signal path is an original surrogate. It is not CMGAN, does
  not load the checkpoint and cannot stand in for a CMGAN result.
- No checkpoint, upstream source, audio, corpus, media or runtime was downloaded,
  copied, vendored, packaged or redistributed into this worktree.
- The upstream PESQ 3.41 / SSNR 11.10 dB values are author-reported
  VoiceBank+DEMAND figures; they are not reproduced and not pooled with the
  synthetic numbers.
- No audio was read or played; no cohort, consent, output-use grant or listening
  protocol exists.
- No device clock, content delay, availability, memory or throughput was
  measured. The prior 1,200 s bound is not reported as inference timing.
- No provider, descriptor, registry, default, installed-v0 behavior, ABI,
  shared build, CI, board or handoff file is changed.

SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
SPDX-License-Identifier: Apache-2.0
