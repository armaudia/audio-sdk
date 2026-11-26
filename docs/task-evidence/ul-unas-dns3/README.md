<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-UL-UNAS-DNS3 - exact source/runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
**UL-UNAS DNS3** (`component_id=ul-unas-dns3`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, recorded before
`opt_in_adapter_exposure`; `evidence_status=incomplete` and
`qualification.status=not_qualified`. A missing, blocked or rejected result may
never qualify the candidate.

The exact licensed UL-UNAS source tree, pre-trained DNS3 checkpoint, documented
streaming ONNX/runtime, immutable revisions, I/O geometry, numeric output,
rights review and task-matched qualification evidence are **absent**. This
package records that exact blocker, applies the Enhancement profile to a
bounded deterministic synthetic paired clean/noisy surrogate, and makes no
noise-suppression, DNSMOS, PESQ, STOI, quality, timing, listening, benchmark or
release claim. The surrogate is **not UL-UNAS**, **not a U-Net**, **not
NAS-derived** and **not a learned model**: no neural network, weight tensor,
ONNX graph, native library, real audio, corpus, model or upstream code is
present, copied, downloaded, loaded, imported or executed. Only this task-local
directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`, `id=SDK-UL-UNAS-DNS3`, component
`ul-unas-dns3`) is a feasibility task. The pinned census row in
`research/noise_suppression_candidate_census.md` says:

> **UL-UNAS DNS3** | Ultra-lightweight U-Net family found through neural
> architecture search; real-time streaming candidate | Official project
> publishes pre-trained DNS3 checkpoint and inference; the repository also
> documents streaming ONNX. An independent Core AI export reports a hashed DNS3
> artifact and MIT model license, but is not upstream-authoritative. |
> High-priority efficiency candidate. Pin upstream checkpoint and terms, choose
> a reproducible streaming backend, and measure quality, speech deletion, CPU
> RTF and latency on the common set. Author and community-export claims remain
> secondary evidence.

Consequently:

- the census names a pre-trained DNS3 checkpoint and streaming ONNX but records
  no upstream repository URL, release, immutable commit, byte count or SHA-256
  for source/checkpoint/ONNX;
- no UL-UNAS source, checkpoint, ONNX, runtime, adapter or caller manifest is
  staged in this worktree;
- no input/output tensor layout, hop, frame, channel layout, lookahead, state,
  reset behavior, latency or output alignment is documented or asserted;
- the independent Core AI export's MIT/license/hash claim is recorded as
  **secondary evidence only** and is not upstream-authoritative; no upstream
  LICENSE text, model-card copy, checkpoint-weight terms, training-data
  statement, notice bundle, attribution or product-use review is staged;
- installed v0 accepts one 16 kHz mono `float32` 160-sample stream and has no
  model or caller-asset admission path;
- no rights-cleared paired clean/noisy cohort, pinned SI-SDR/STOI/PESQ scorer,
  established baseline, listening result or held-out split exists;
- no target-runtime pacing, content/availability timing, memory or independent
  review exists.

Nothing was downloaded, copied, vendored, built, imported, loaded or executed.
The eight release gates are `blocked`; machine-readable blocker records are in
`contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-UL-UNAS-DNS3`, `26bc48c58f9d69571571fa651862dcbe0fe1172d` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `float32`, 160 samples/frame |
| Candidate architecture | ultra-lightweight NAS U-Net family (census description, not verified) |
| Candidate rate | 16 kHz (census statement only) |
| Candidate hop/frame/channels/latency | not documented; not asserted |
| Candidate artifacts | absent; no source, checkpoint, ONNX, configuration or runtime |
| Surrogate | synthetic 16 kHz mono integer block energy gate |
| Surrogate content delay | 0 samples; 160-sample block lookahead declared |
| Provider registration, default, ABI, CI | none |

The surrogate is a bounded integer per-block energy gate: a 160-sample block
mean magnitude against a fixed fixture-tuned threshold of 850 Q15, gain 1000
per mille when above and 280 below, applied to the same block. It is **not a
network**, not UL-UNAS, not a U-Net, not NAS-derived, has no weights and cannot
qualify the candidate. Its declared 160-sample block lookahead is a fixture
property only; it is not a candidate latency or delay claim.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` -> `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity/noisy control | synthetic only | Frozen synthetic noisy microphone plus authored clean Q15 reference; per-region identity/noisy SI-SDR and SNR |
| Established task-matched baseline | blocked | No baseline is pinned, licensed or run; sibling evidence is not reused |
| Paired SI-SDR | synthetic only | Exact integer SI-SDR in millidB against the authored synthetic clean reference only |
| Paired STOI | blocked | No pinned STOI scorer and no permitted rights-cleared clean references; not computed and not fabricated |
| Clean-speech preservation | synthetic only | SI-SDR, SNR, level change and peak on two synthetic near-clean regions |
| Peaks and invalid outputs | synthetic only | Peak bound, clamping and nonfinite-output counts on synthetic frames |
| Unpaired screen or listening | blocked | No predictive screen, authorized listening or rights-cleared unpaired speech |
| Alignment / content mapping | synthetic only | Declared 0 surrogate content delay with -16/-8/0/+8/+16 shift probes; no candidate alignment asserted |
| Runtime availability timing | blocked | No exact runtime, device clock, deadline, availability or measured content delay |
| Streaming state and reset | synthetic only | Chunk invariance, reset to epoch 2 and a 137-sample final partial frame |
| Runtime memory | blocked | No measured runtime memory; only a declared 32-byte surrogate state |
| Task-matched held-out qualification | blocked | No rights-cleared held-out paired cohort, independent scorer or listening result |

Every paired, clean-preservation, peak, alignment, streaming and reset row is
`qualifies=false`. Synthetic exactness means only that the fixture is
self-consistent.

## Exact synthetic geometry and fixtures

- Rate: 16,000 Hz mono `float32`, 160 samples per frame, 62,500 ns per sample,
  0.75 s fixture (12,000 samples).
- Six contiguous segments: `clean_only_initial` 0-2400 (speech, noise
  amplitude 8), `noisy_speech` 2400-4800 (speech, 900),
  `noisy_speech_low_snr` 4800-7200 (speech, 2400),
  `speech_pause_noise_only` 7200-8400 (no speech, 1200),
  `clean_only_final` 8400-9600 (speech, 8), `noisy_speech_restore` 9600-12000
  (speech, 1500).
- Clean reference: deterministic three-tone Q15 source with a frozen ten-frame
  syllable envelope (levels 0-3000); noise: deterministic LCG (seed 20261127)
  amplitudes scaled by the segment level; microphone: exact integer sum clamped
  to Q15.
- Surrogate: 160-sample block mean magnitude, fixed 850 threshold, gain
  1000/280 per mille, exact integer multiply/floor; state is 32 bytes.

## Adverse, missing and invalid handling

`report.json` records the adverse rejection matrix, each case with the exact
expected code, the observed code and unchanged processing state. Rejections
include duplicate JSON key, `NaN`/`Infinity` constants, malformed JSON,
missing/extra config fields, unsupported rates/channels/frame sizes/formats,
clock drift, resampling, missing/short/long/nonfinite/out-of-range frame input,
nonzero padding, epoch/position mismatch, invalid reset, invalid caller
manifest, bad fixture segments and unknown artifact/precision/configuration
identifiers. No rejection is promoted to a pass.

## Caller-supplied-asset contract

The package records a caller-supplied-asset contract
`audio-sdk/ul-unas-dns3/caller-supplied-asset/0.1`. It is **not loaded** and
**not executed**. Required fields include adapter/variant/configuration id,
artifact format, precision, sample rate/channels/frame/hop, algorithmic latency,
absolute model/library paths, model/weights/source/library SHA-256 digests and
source commit. Present behavior is validate identity/configuration/geometry
only; absent behavior is reject before processing.

## Regeneration and verification

Run from this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -q test_reference
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` regenerates `report.json`, `report.json.sha256`, `contract.json` and
`SOURCES.sha256` only after three cold-start rounds are byte-identical.
`verify.py` is read-only and fails closed on stale/corrupt artifacts, promoted
results, fabricated geometry/STOI, open gates, scope violations or a dirty
`git diff --check`.

## Files

- `reference.py` - strict parsers, synthetic fixture, bounded surrogate, report/contract builders.
- `run.py` - deterministic 3x regeneration.
- `verify.py` - read-only strict verifier.
- `test_reference.py` - deterministic acceptance suite.
- `contract.json` - machine-readable contract and blocker record.
- `report.json` - machine-readable evidence report.
- `report.json.sha256` - report digest sidecar.
- `SOURCES.sha256` - source/boundary/artifact pin manifest.
- `*.license` - SPDX sidecars for non-Python generated/text artifacts.

## Release gates

All eight release gates are `blocked`: RG-01 exact source/checkpoint/ONNX/runtime,
RG-02 isolated hash-pinned runtime admission, RG-03 rights/attribution/review,
RG-04 SDK boundary admission and parity, RG-05 rights-cleared paired
qualification, RG-06 streaming/state/reset/latency/nonfinite behavior, RG-07
target-device timing/memory/listening controls, RG-08 opt-in provider intake and
default/release approval.

## Reopen condition

Pin the exact licensed UL-UNAS source, DNS3 checkpoint and streaming
ONNX/runtime with immutable revisions and verified lineage; document exact
input, hop, frame, lookahead, state and output geometry; admit an isolated
hash-pinned runtime; clear code, checkpoint-weight, training-data and corpus
rights; map the asset through the caller-supplied SDK boundary and reproduce
exact output; run an established baseline and paired SI-SDR/STOI plus
clean-preservation and peak qualification on a rights-cleared task-matched
held-out cohort; measure availability, timing and memory at the exact runtime
and complete opt-in provider intake. Until then the candidate stays DEFER,
incomplete and not qualified.
