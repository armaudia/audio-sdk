<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-CISCO-PASE — Cisco PASE artifact/runtime blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`Cisco PASE` (`component_id=cisco-pase`). The acceptance profile is
**Enhancement**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER**, before
`opt_in_adapter_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing result may never qualify the
component.

The package records the exact artifact, runtime, rights, corpus and scoring
requirements, then runs a bounded deterministic **external-asset admission and
frame/drain conservation surrogate** on synthetic values. It is **not** Cisco
PASE, contains no licensed source, checkpoint, weight, WavLM component,
vocoder, runtime, corpus, device, listener or benchmark, and changes no
provider, descriptor, registry, installed v0 behavior, ABI, default, shared
build, CI, board row or handoff. Only this task-local directory is added.

## Exact blocker

The catalogue record describes a 16 kHz Phonologically Anchored Speech
Enhancer with WavLM denoising-representation distillation and a dual-stream
vocoder, and repeats a model-card claim of Apache-2.0 plus a released
checkpoint. None of the material needed to reproduce or qualify it is staged:

- **No artifact identity.** No PASE source tree, enhancer checkpoint, WavLM or
  feature-extractor weights, vocoder weights or inference config exists in the
  workspace. The census record names only
  `https://huggingface.co/cisco-ai/pase`, `https://github.com/cisco-open/pase`
  and `https://arxiv.org/abs/2511.13300`; it records no filename, byte count,
  SHA-256 or immutable revision. There is no manifest to admit.
- **No runtime.** PyTorch, transformers, torchaudio, ONNX Runtime and any PASE
  package are absent. No framework, wheel/sdist digest, accelerator build,
  precision, seed or deterministic setting is pinned, so no exact-runtime
  parity can be produced.
- **No cleared rights.** Apache-2.0 is a research-census claim for the model
  card and repository only. Weight-specific terms, feature-extractor and
  vocoder component terms, training-data provenance (DNS-style noise, public
  speech, OpenSLR RIRs), redistribution and product-use clearance are
  unverified. No upstream portion may be copied, downloaded or redistributed.
- **No task-matched evidence.** There is no rights-cleared paired 16 kHz
  noisy/clean cohort, independent SI-SDR/STOI scorer pin, WER or
  speaker-similarity model, authorized listening result, real output,
  content/availability timing, RTF, memory measurement, provider intake or
  independent review.
- **No verified task geometry.** The census describes a joint
  noise/reverberation generative enhancer. Exact segment geometry, content
  delay, sampler, seed, vocoder rate and the phonologically anchored evaluation
  protocol are not staged. The proposal geometry below is not a verified PASE
  setting.

The record is therefore `available` / `located_unverified` in the pinned
candidate accounting and `blocked` for eligibility. The exact blockers and the
eight blocked release gates are machine-readable in `contract.json` and
`report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-CISCO-PASE`, `d45e0f22883021412b4206c77df4e1d8cf89dbd5` |
| Task mode | `feasibility` |
| Acceptance profile | `enhancement` |
| Decision | `DEFER` before `opt_in_adapter_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Declared intake | 16 kHz mono, 160-sample frame, 320-sample anchor hop, 400-sample anchor window |
| Asset boundary | caller-supplied `external` only; no bytes read, no download |
| Provider registration, default, ABI, CI | none |

The declared anchor hop and window are **proposal defaults** used to exercise
integer rate geometry. They are not read from, and must not be cited as, the
PASE configuration.

## Exact arithmetic

- One 16 kHz sample is exactly **62,500 ns**, following the `CONTRACTS.md`
  timing record.
- Accepted audio is a half-open source interval `[0, accepted_samples)`.
  Output sample `n` maps to source `n - D` for declared content delay
  `D`, with `0 <= D <= 16,000`.
- A process call consumes exactly 160 samples. A final partial frame is
  zero-padded by the caller; zero padding is **never** valid content.
- Valid output is the intersection of the 160-sample output interval with
  content `[start_exclusion, accepted - end_exclusion)`. Conservation is
  **interval-union equality**, not merely a matching total.
- `drain` emits the remaining content from the first unmapped source position
  in 160-sample calls, bounded by `max_drain_calls <= 1024`. An empty stream
  drains immediately with no audio call.
- An anchor hop that is not a whole number of 160-sample frames is rejected;
  it is never interpolated or silently rounded.
- All synthetic values are dyadic rationals and all alignment arithmetic is
  integer, so the identity control is bit-exact and the case-matrix digest is
  stable across the three cold-start rounds.

## Enhancement profile application

`plan/swarm/VERIFICATION.md` Enhancement row is applied item by item in
`report.json` → `acceptance_profile`, and each item is checked by `verify.py`:

| Required item | State | Evidence |
| --- | --- | --- |
| Identity and noisy control | synthetic only | Bit-exact zero-anchor identity; no real noisy recording |
| Established task-matched baseline | blocked | No installed baseline or pinned candidate output |
| Paired SI-SDR | blocked | No rights-cleared clean reference; synthetic values are controls only |
| Paired STOI | blocked | No clean-reference cohort and no pinned independent scorer |
| Clean-speech preservation | synthetic only | Block-hold negative control damages synthetic clean speech |
| Peaks and invalid outputs | synthetic only | Deterministic bounds and nonfinite rejection on synthetic values |
| Unpaired screen or authorized listening | blocked | No predictive model, listening test or listener |
| Alignment, state, memory | synthetic only | Integer source mapping and deterministic block state only |
| Content and availability timing | blocked | No device clock, deadline, RTF or pacing measurement |

## Frozen conservation cases

Generated from integer arithmetic only. `D` is the declared content delay.
Every case is checked for overlap freedom and interval-union equality.

| Case | Accepted | `D` | Process | Drain | Valid | Zero pad | Content |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| `zero_input` | 0 | 160 | 0 | 0 | 0 | 0 | `[0,0)` |
| `single_sample` | 1 | 160 | 1 | 1 | 1 | 159 | `[0,1)` |
| `partial_final_159` | 159 | 160 | 1 | 1 | 159 | 1 | `[0,159)` |
| `exact_frame_160` | 160 | 160 | 1 | 1 | 160 | 0 | `[0,160)` |
| `one_frame_plus_one_161` | 161 | 160 | 2 | 1 | 161 | 159 | `[0,161)` |
| `two_frames_320` | 320 | 160 | 2 | 1 | 320 | 0 | `[0,320)` |
| `two_frames_plus_one_321` | 321 | 160 | 3 | 1 | 321 | 159 | `[0,321)` |
| `odd_length_1000` | 1000 | 160 | 7 | 1 | 1000 | 120 | `[0,1000)` |
| `delay_not_multiple_160` | 250 | 100 | 2 | 1 | 250 | 70 | `[0,250)` |
| `max_declared_delay` | 400 | 16000 | 3 | 100 | 400 | 80 | `[0,400)` |
| `edge_exclusions_16` | 320 | 160 | 2 | 1 | 304 | 0 | `[8,312)` |

The sweep additionally checks 4,105 combinations: lengths `0..400` plus
`999..1001` and `3999..4001`, delays `0,1,99,100,159,160,161,320,1000,16000`,
and edge exclusions `(1,1)`, `(8,8)`, `(80,80)`, `(0,160)`, `(160,0)`. All
conserve.

## Dual-rate and preservation controls

The 320-sample anchor hop equals two 160-sample frames, so every anchor block
boundary lands exactly on a frame edge. With a zero residual, the held anchor
sequence is reproduced bit-exactly (`exact=true`,
`status=synthetic_only_not_qualified`). A hop of 170 is rejected as
`anchor_hop_not_frame_multiple`; nothing is interpolated.

The clean-preservation control applies the block hold to a deterministic
synthetic clean target (`3,200` samples, values in multiples of `1/64`). It is a
**negative control** and cannot qualify:

| Metric | Value |
| --- | ---: |
| SI-SDR | -57.953416 dB |
| SNR | -3.382601 dB |
| Max absolute error | 1.5625 |
| Peak output | 0.78125 |
| Correlation | 0.001266 |
| Bit-identical | no |
| Status | `surrogate_only_not_qualified` |

This shows only that a trivial zero-order hold destroys the synthetic signal.
It is not PASE, produces no enhancement benefit and is not a candidate result.

## Adverse, missing and invalid handling

`report.json` records 52 rejected inputs, each with an unchanged frozen
evaluation state. Rejections cover duplicate/uppercase/path asset IDs, short,
uppercase or non-hex SHA-256, zero/negative/bool byte counts, embedded storage,
missing or extra asset fields, too many assets, total size over 512 MiB,
unsupported adapter schema/ID/rate/channels/frame, non-frame-multiple or
out-of-range anchor hop, invalid window, delay and drain bounds, extra adapter
fields, callback/unknown execution modes, negative/oversized/bool accepted
counts, an exhausted drain budget, wrong input count, zero/oversized valid
count, partial frame without final, unknown flags, nonzero final padding,
sample-count and output-capacity mismatch, nonfinite/wrong-type/out-of-range
samples, misaligned residual, anchor block-count mismatch, nonfinite anchor or
residual, empty stream, duplicate JSON key, nonfinite JSON constant and
malformed JSON. Missing upstream artifacts, real recordings, runtime, rights
and scores are `blocked`, not passes.

## Reproduction

```sh
cd docs/task-evidence/cisco-pase
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
```

`run.py` performs three cold-start rounds and refuses to accept non-identical
report, contract or source bytes. `verify.py` is read-only and fails closed on
stale pins, non-canonical JSON, a promoted result, an unblocked release gate, a
license gap, out-of-scope changes or `git diff --check` damage. Expected:
all tests pass and `verify.py` prints
`pins_ok=… json_ok=2 report_sha256=… repeats_ok=3 licensing_ok=1 scope_ok=1`.

## Release gates and reopening

All eight gates are `blocked`: exact artifact/source identity (RG-01), pinned
runtime (RG-02), artifact and training-data rights (RG-03), exact-runtime
parity on frozen synthetic inputs (RG-04), rights-cleared paired scoring
(RG-05), preservation/peaks/timing (RG-06), opt-in intake and independent
review (RG-07), and default/release approval (RG-08).

Reopen only with immutable PASE artifacts and revision, an installing pinned
runtime, cleared artifact and training-data rights, exact-runtime parity,
rights-cleared paired scoring with independent scorers, measured preservation
and target-host timing, and independent opt-in provider review. Until then the
decision stays `DEFER`, the evidence stays `incomplete` and no result may
qualify.
