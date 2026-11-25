<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LISENNET-STREAMING-FP32 — caller-supplied-asset streaming boundary evidence

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`LiSenNet streaming FP32` (`component_id=lisennet-streaming-fp32`). The
acceptance profile is **Enhancement**, assigned by `plan/INVENTORY.json`
(`verification_profile: enhancement`) and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification_status=not_qualified`, `qualified=false`. Missing evidence never
qualifies a candidate.

This package models the LiSenNet streaming FP32 boundary as a
**caller-supplied external asset**: the 16 kHz frame geometry, the three-channel
host feature contract, the 17-slot causal FIFO state/cache contract and the
chunk/flush/reset streaming contract. Because the exact graph bytes, an
immutable asset revision and the ONNX Runtime are unavailable here, it executes
a deterministic stdlib/NumPy **synthetic streaming surrogate** and records a
strict readiness conclusion. It is **not LiSenNet**, does not load or execute
the ONNX graph or ONNX Runtime, does not download or vendor weights, does not
read real audio or media, does not measure a device clock, does not conduct
listening, does not benchmark the SDK and makes no quality, latency, benchmark
or release claim. Only this task-local directory is added.

## Exact external blockers

1. **Asset identity is not admitted.** The asset ledger records
   `g_best_streaming_fp32.onnx` as **323,489 bytes**, SHA-256
   `64b18acee261d54805c7cbe6b01a23f806160cf594c7c3f6df621c3b50a343db`,
   under `https://huggingface.co/claroche1/LiSenNet` at `source_revision`
   `4fe3356`. That revision is a **7-hex abbreviation** with no immutable
   full-commit retrieval record tying those bytes to it. The artifact is absent
   from this worktree and must resolve from the caller's own storage; no bytes
   were read, hashed, mapped or downloaded.
2. **The runtime is absent and unpinned.** The streaming graph needs an ONNX
   Runtime CPU runtime for `feat` plus 17 state inputs (18 inputs, 18 outputs).
   `onnxruntime` is not installed here and no pinned wheel/sdist digest or
   runtime distribution/product-use terms exist. The host STFT, feature
   extraction and noisy-phase iSTFT in the research adapter are not vendored or
   executed.
3. **Artifact-specific rights are not cleared.** MIT is recorded for the port
   `LICENSE` and the model card, but written weight-specific terms,
   training-data provenance beyond the VoiceBank-DEMAND reporting scope,
   redistribution/product-use clearance and legal review are absent. No weight,
   graph, runtime or upstream source may be copied, packaged, downloaded or
   redistributed by this package.
4. **No qualification evidence exists.** There is no rights-cleared paired real
   cohort with clean references, no independent STOI/SI-SDR result, no
   permitted listening, no target-runtime pacing, availability, deadline or
   memory measurement, and no approved exact streaming reference output vector
   for these frozen inputs. The synthetic surrogate can never stand in for any
   of these.

**Reopen condition.** Admit the candidate only when the exact bytes are
addressed by a **full immutable repository commit** plus byte count and SHA-256
in a retrieval record and resolve from the caller's own storage; a **pinned ONNX
Runtime** CPU artifact with a recorded digest installs in the intended
environment with documented terms; **written artifact-specific** weight,
runtime and training-data terms plus a legal/redistribution decision exist;
the host DSP and state carry reproduce the published graph's parity tolerance;
and a rights-cleared cohort, independent scorer, permitted listening, exact
streaming reference vectors and target timing evidence are available. Until
then all ten release gates stay `blocked`.

The full text is duplicated in `contract.json:exact_blockers`,
`readiness.json:external_blockers` and `report.json:exact_blockers`.

## Boundary model

- Public v0 geometry is preserved: 16 kHz, mono, `f32`, 160 samples per call.
  The package does not change `CONTRACTS.md`, headers, registry, descriptors,
  defaults, shared CMake, CI, board or handoff files.
- The internal streaming geometry is source-derived, not executed: `n_fft=512`,
  `hop=256` (16 ms), `win_length=512`, `n_freqs=257`, `compress_power=0.3`,
  centered STFT with 256-sample reflect padding and a periodic Hann window.
- Features are the documented three channels: compressed magnitude
  `|S|^0.3`, group delay `/π` and instantaneous-frequency difference `/π`.
  Phase recovery is the causal noisy-phase iSTFT; the offline two-iteration
  Griffin-Lim path is explicitly outside this boundary.
- The caller-supplied asset manifest requires exactly `asset_id`, `sha256`,
  `byte_count`, `storage`, `source_repository`, `source_revision`,
  `sample_rate_hz`, `channels`, `n_fft`, `hop_samples`, `n_freqs`,
  `compress_power`, `state_slot_count` and `sample_format`, with an optional
  absolute `caller_path` that is never resolved or read. Missing, extra,
  mistyped, hash-mismatched, wrong-geometry or relative-path manifests fail
  closed before any frame. Validation never opens the file.
- The state contract follows the conv/ wide export: **17 FIFO slots** in
  module-registration order (6 encoder `DSConv` low/high buffers, 2
  `ConvolutionalGLU` depthwise buffers, 8 `_CausalTimeConv` buffers at
  dilations 1/2/4/8, 1 decoder mask buffer) with **71 past-frame rows** in
  total. Shapes are opaque until the caller initializes them from the supplied
  graph; `state_out[n]` feeds `state_in[n+1]` and `reset` restores the exact
  all-zero initial state.
- The surrogate's own cache stores the three-channel feature frame in every
  slot (218,964 bytes). This models the cache mechanics only; it is not the
  graph's activation tensors and no asset state byte count is invented.
- Caller chunks of `1, 7, 80, 159, 160, 161, 255, 256, 257, 320, 1280` and one
  32,000-sample call produce **identical** outputs. Internal frame buffering
  makes the result independent of caller chunking.
- The 32,000-sample stream emits 31,488 samples before flush and 512 on flush;
  the final frames use 256 samples of right reflect padding, counted
  separately and never emitted as extra audio. One flush drains the tail; a
  second flush returns `[]`; `process` after flush fails closed; `reset`
  restores the exact initial state.
- Content alignment is **0 samples** (the adapter declares an identity
  source-time mapping and zero delay compensation). The centered-STFT
  availability lead is **256 samples (one hop)**. Both are modelled on
  `fixture-sample-coordinate-not-device`; there is no wall clock, device clock,
  callback deadline, paced workload or measured latency.

## Enhancement profile application

`report.json:enhancement_profile` records identity/noisy controls, paired
synthetic SI-SDR/SNR and STOI on exact synthetic clean references, clean-speech
preservation, peaks/clipping/nonfinite checks, state/memory and explicit
unmeasured fields. The established task-matched baseline is `not_reproduced`;
source-reported noisy-identity and FastEnhancer comparisons are provenance only.
Real clean references, real runtime, measured content/availability timing and
listening are `false`/`not_run`. All surrogate metrics describe the surrogate
only and clear no gate.

### Synthetic fixture results (not a candidate result)

Scores are computed on the same 32,000-sample prefix for every variant. Δ is
surrogate minus same-mixture identity. A **negative Δ is adverse**. These
numbers are **not LiSenNet results**, not a quality pass and not comparable to
the pinned source-reported cohort.

| Condition | Identity SI-SDR dB | Surrogate SI-SDR dB | Δ SI-SDR dB | Identity STOI | Surrogate STOI | Δ STOI | Surrogate peak |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| `target_only` | undefined (`zero_error_identity_exact`) | 9.620121 | n/a | 1.000000 | 0.979962 | −0.020038 | 0.419601 |
| `mixture_snr12` | 11.989305 | 7.207004 | −4.782301 | 0.653945 | 0.655416 | +0.001471 | 0.465788 |
| `mixture_snr18` | 17.994695 | 8.879159 | −9.115536 | 0.690853 | 0.690565 | −0.000287 | 0.434373 |
| `mixture_snr24` | 23.997395 | 9.420527 | −14.576867 | 0.738590 | 0.736458 | −0.002132 | 0.425471 |
| `noise_only` | zero reference (invalid) | zero reference (invalid) | n/a | invalid | invalid | n/a | 0.665268 |
| `silence` | zero reference (invalid) | zero reference (invalid) | n/a | invalid | invalid | n/a | 0.000000 |

The surrogate gate attenuates a substantial part of the harmonic target while
retaining noise, so every mixture SI-SDR regresses and the target-only control
loses 0.020 STOI. This is a recorded **adverse** result: the fixture exercises
the scoring and preservation paths; it does not demonstrate enhancement.

Least-squares projection of the surrogate output onto target and noise:

| Stratum | Target retention | Noise retention | Target/noise ratio gain dB | Target projection SNR dB |
| --- | ---: | ---: | ---: | ---: |
| +12 dB | 0.606718 | 0.647715 | −0.567943 | 7.207004 |
| +18 dB | 0.607593 | 0.632926 | −0.354812 | 8.879159 |
| +24 dB | 0.608040 | 0.607553 | +0.006964 | 9.420527 |

Every valid output is finite, below the unit peak guard and free of clipping.
`noise_only` and `silence` have zero clean references and are never scored as
speech. Identity/noisy controls are bit-identical at every condition.

### Boundary controls (synthetic only)

| Check | Result |
| --- | --- |
| Chunk invariance over 12 caller chunk sizes | exact (`chunk_invariant=true`) |
| Whole-call vs 160-sample stream | exact digest match |
| Emitted before flush / on flush | 31,488 / 512 samples |
| Output length | 32,000 = input, zero content lag |
| Impulse probe peak | input 4,000 → output 4,000, residual lag 0 |
| Modelled availability lead | 256 samples (one hop), not measured |
| 17-slot / 71-row state cache | reset replay, independent session and cross-stream reset identical |
| Flush lifecycle | first flush emits tail, second empty, process-after-flush rejected, reset works |
| Caller-asset admission | blocked with five exact reasons; synthetic control admitted but not the candidate |

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, results, gates. |
| `reference.py` | Deterministic stimuli, caller-asset validator, streaming boundary surrogate, scoring, canonical report/contract/readiness builders. |
| `run.py` | Regenerates `contract.json`, `adapter.json`, `readiness.json`, `report.json`, `report.json.sha256` and `SOURCES.sha256` byte-identically. |
| `report.json` | Canonical machine-readable Enhancement report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `readiness.json` | Strict readiness conclusion: DEFER, incomplete, not qualified, all gates blocked. |
| `adapter.json` | Task-local proposal-only descriptor; not implemented, unregistered, OFF by default. |
| `contract.json` | Task contract: profile, boundary, geometry, state cache, asset pins, blockers, gates, invariants. |
| `test_reference.py` | Deterministic unittest checks (no skips, no network). |
| `verify.py` | Read-only pin, README-digest-table, strict-JSON, digest, reproduction, licensing and write-scope verification. |
| `requirements.lock` | Pinned NumPy/SciPy/pystoi versions for deterministic metrics. |
| `LICENSES.md` | Upstream license and asset-rights notes. |
| `SOURCES.sha256` | SHA-256 manifest for all external, boundary and task-local files. |

## Pinned source and asset digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked against the file and against `SOURCES.sha256` by
`verify.py`. The asset digest itself is pinned in `report.json:asset_boundary`
and `research/noise_suppression_assets_20261027.json`; the ONNX file is absent
and is not a row here.

| Source/asset | SHA-256 | Use |
| --- | --- | --- |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Enhancement acceptance profile. |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | `lisennet-streaming-fp32` component record and profile assignment. |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` | LiSenNet `evaluated` row and source-reported comparison scope. |
| `research/noise_suppression_candidate_census.md` | `525d1f0e1984539e973d01f3b416fb9a7f8eb747c6f49a7366246b2c2e91e82a` | Ultra-compact causal sub-band U-Net census note. |
| `research/noise_suppression_assets_20261027.json` | `35f871e7d7362070c20fa35a5832115ea5388ffae550be3b25368a72bf5cebf4` | Asset ledger: 323,489 bytes, SHA-256 and revision `4fe3356`. |
| `research/noise_suppression_pilot_20261027.md` | `90adcfb7b612d5a661baf16e69f78df95eebc6f65bbfece973022af902bd9aae` | Source-reported 30-pair DNS2020 deltas and RTF. |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` | Streaming model path and batch RTF context. |
| `adapters/lisennet/adapter.json` | `1a12f0cb768d018b480ca325c9e8b3a9b374e6b53aff9fdad505c8920acb9643` | Research-workspace adapter descriptor; not executed or changed. |
| `adapters/lisennet/README.md` | `aef55b5b753e6d450bb9bb3355e9e12daa49f26b55e835e989f853ee30a714c4` | 16 kHz / 512-256 geometry and asset-path claim. |
| `adapters/lisennet/run.py` | `86ff5220d70b3aa77cefa5b7332935779f9e11f3e048dce501688053174ee6b1` | Host STFT, feature extraction and noisy-phase iSTFT reference. |
| `data/checkouts/eco8-neaixt/LICENSE` | `6239327208515d111fc473c38e620e7154d7d432168e671c4253e2744c0ef166` | MIT upstream port license. |
| `data/checkouts/eco8-neaixt/docs/models/lisennet.md` | `df4bf439dab6b81ef95f881accc1e0e3ae52fb2b5eeaaaa1a0d6bcbd9a57777d` | Architecture, streaming state and reported PESQ. |
| `data/checkouts/eco8-neaixt/lisennet/export_onnx.py` | `4af7044839fcd9270271850b659607a546abd84eb389a08d6b147f6dc09e1a07` | Streaming FP32 export and state I/O contract. |
| `data/checkouts/eco8-neaixt/lisennet/model.py` | `df846e8ceae26b6c9866c3a5bbb919c5f557d02a39051da7bdc8e9ca2c70c813` | Causal time conv and dual-path blocks. |
| `data/checkouts/eco8-neaixt/lisennet/streaming.py` | `5009ba820f1810b1a26b19ac64f24362b3be0982205af448e5c69829c5a17324` | Streamer, state slots and reset semantics. |
| `data/checkouts/eco8-neaixt/push_lisennet_hf.py` | `c03beb8f021909bdfb5d5548cbd2e8a3c7e6ba17f2ceeb035d25a38325645dda` | HF subfolder layout for the published graphs. |
| `data/checkouts/eco8-neaixt/configs/lisennet_conv_wide.json` | `c239b3f8b55f9cc72448738efcf0e7ba83a800906768a952b8ca08444a5edcd9` | nc20 / dilations 1/2/4/8 state geometry. |
| `data/checkouts/eco8-neaixt/benchmarks/published.py` | `bc267a16be1e90803394f19d9de740c488abfe1a15c9a747f08a250c01127bfa` | HF repository treated as the artifact of record. |

Boundary pins also cover `CONTRACTS.md`, `CMakeLists.txt`, `REUSE.toml`, both
public v0 headers, `scripts/ci.py` and `LICENSES/Apache-2.0.txt`; all are
unchanged and machine-checked in `SOURCES.sha256` and
`report.json:boundary_pin_paths`.

## Reproduction

`SOURCE_ROOT` is needed only by the verifier and tests to check external pins.

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-LISENNET-STREAMING-FP32
TASK=$WT/docs/task-evidence/lisennet-streaming-fp32
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
export SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY run.py --all
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
cd "$WT"
PYTHONDONTWRITEBYTECODE=1 $PY scripts/ci.py --output /private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/lisennet-ci
python3 -m reuse lint
git diff --check
```

## Gates and reopen conditions

The package records ten blocked gates: exact asset identity, runtime admission,
artifact rights, host DSP parity, exact reference parity, rights-cleared
cohort, independent scoring and listening, target runtime timing, provider
intake and public default selection. `readiness.json` is the concise strict
conclusion; `report.json:gates` and `contract.json:gates` carry the exact
reopen condition for each.

Reopen only when the full immutable asset commit and caller-held bytes are
admitted, a pinned ONNX Runtime installs with documented terms,
artifact-specific rights and legal review are cleared, host DSP/state parity is
reproduced, approved exact streaming reference vectors exist, a rights-cleared
paired real cohort is scored by an independent scorer, permitted listening is
complete, target pacing/availability/deadline/memory are measured, an opt-in
OFF-by-default provider intake is approved and a public default decision is
recorded. Until then the candidate stays **DEFER**, **incomplete** and
**not qualified**.

## Separation from other work

The research workspace adapter `adapters/lisennet/`, the
`research/noise_suppression_pilot_20261027.md` 30-pair DNS2020 measurement and
the `data/checkouts/eco8-neaixt` port are pinned external provenance. They were
not executed, imported, pooled or reinterpreted by this package. The
source-reported −6.6148 dB mean SI-SDR delta and 0.0212 batch RTF describe a
different cohort and are never treated as this package's result.
