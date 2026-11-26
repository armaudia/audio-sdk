<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS — blocker and harness

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence
for `EARS preservation screen and scorer harness`
(`component_id=ears-preservation-screen-and-scorer-harness`). The acceptance
profile is **Evidence**, assigned by `plan/INVENTORY.json` and defined in
`plan/swarm/VERIFICATION.md`. Decision: **DEFER** before
`processor_exposure`; `evidence_status=incomplete`,
`qualification.status=not_qualified`. A missing, blocked, synthetic or
rejected result may never qualify the harness, a scorer or a denoiser.

The exact EARS archive, prepared cohort, candidate outputs, pystoi 0.4.1
source, DNSMOS P.835 script/models and rights grant are **absent**. This
package records that exact blocker and exercises a bounded deterministic
**author-written integer Q15 preservation-score harness** on frozen synthetic
controls. It is **not** the historical EARS run, not pystoi, not DNSMOS, not a
denoiser, not a listening test and not a processor. It makes no preservation,
intelligibility, predicted-MOS, listening, device-timing, benchmark or release
claim. Only this task-local directory is added.

## Exact blocker

The catalogued record (`plan/INVENTORY.json`,
`id=ears-preservation-screen-and-scorer-harness`) is `evaluated`,
`disposition=research-control`, `verification_profile=evidence`, with the plan
note “Keep blind no-clean-reference preservation metrics and rights-gated
listening separate.” The linked evidence is
`research/voice-enhancement-20261101/agent-ears-preservation-743/REPORT.md`
(SHA-256 `d3a2206056eac182f62e3c7d3ea6f249b65ecdb001d5b847142d87ccc5627467`).
That report describes 743 mono 48 kHz EARS WAVs and prepared 16 kHz inputs,
but none of the audio, inputs, candidate outputs or scorers is staged in this
workspace.

Consequently:

- `data/runs/voice-enhancement-20261101-ears-preservation-743/` is absent,
  including `inputs/manifest.json` (documented SHA-256
  `1b21465dd02ede9089f7aabcc97ecc20fc562411988a170e5060a157ebe9f121`),
  `fastenhancer_small-results.json` and `deepfilternet3-results.json`;
- no EARS archive path, item manifest, archive digest, CC BY-NC 4.0 licence
  copy, consent/playback grant or redistribution review is staged;
- no pystoi 0.4.1 source, NumPy/SciPy scoring environment or exact STOI
  scorer is staged; the sibling `stoi-estoi` algorithm port is not imported
  or treated as the licensed scorer;
- no DNSMOS P.835 `dnsmos.py`, `sig.onnx` or `bak_ovr.onnx` artifact is
  staged at the documented paths;
- no real candidate output, RTF, memory, speaker label, transcript or
  authorized listening result exists.

Nothing was downloaded, copied, vendored, decoded, imported, loaded or
executed. The eight release gates are `blocked`; the machine-readable blocker
records are in `contract.json` and `report.json`.

## Scope and boundary

| Field | Record |
| --- | --- |
| Repository | `audio-sdk` |
| Branch and base | `swarm/SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS`, `b43a7e13175949cda78f0ea64953e4a585d43c67` |
| Task mode | `research-control` |
| Acceptance profile | `evidence` |
| Decision | `DEFER` before `processor_exposure` |
| Evidence / qualification | `incomplete` / `not_qualified` |
| Installed v0 | unchanged: 16 kHz mono `f32`, 160 samples/frame |
| Harness input | authored integer Q15, 16 kHz, 9,600 samples |
| Historical alignment bound | ±100 ms (±1,600 samples), not run on real audio |
| Real corpus / scorer / runtime | absent |
| Provider registration, default, ABI, CI | none |

The harness exercises strict JSON and manifest parsing, exact Q15
preservation metrics, item-weighted aggregation, file-hash admission,
adverse/missing/invalid/nonfinite rejection and a fail-closed real-screen
gate. It is **not** a candidate adapter and cannot establish exact-runtime
parity. A synthetic control addresses only the meaning of the reported
metrics; it closes no source, rights, corpus, scorer or release gate.

## Screen contract

`reference.py` defines the exact manifest that a real screen must satisfy:

- one `audio-sdk/ears-preservation-screen-manifest/0.1` object with a
  `corpus_id`, `corpus_license`, `corpus_archive_sha256`, preparation-recipe
  digest, 16 kHz prepared rate, 48 kHz original rate, 160-sample frame and
  `expected_items=743` for the EARS cohort;
- one item per recording with `sample_id`, original/input SHA-256, relative
  prepared-input path, duration and one or more candidate output records;
- one output per candidate with immutable SHA-256, relative path and an exact
  sample count equal to the item duration;
- exact `stoi` and `dnsmos_p835` scorer pins with source digest, licence ID
  and `pinned`/`blocked` status.

`validate_manifest` never reads audio and never runs a scorer.
`validate_manifest_files` only hashes the declared files. `real_screen_gate`
fails closed unless the documented run directory, its digests, the EARS
archive search roots and both exact scorers are present and matching.
`require_real_screen` then raises `blocked_real_screen:<artifact>` before any
item is read.

## Exact metric definitions

The harness references the same original input; it has **no clean
reference**. It implements only the following stdlib metrics:

| Metric | Exact definition |
| --- | --- |
| SI-SDR | Zero-mean `10·log10(‖proj‖²/‖y₀−proj‖²)`, `proj=(⟨y₀,s₀⟩/⟨s₀,s₀⟩)·s₀`; integer dot products before the logarithm; perfect reconstruction capped at `+999000` millidB |
| SNR | Uncentered `10·log10(⟨s,s⟩/⟨y−s,y−s⟩)` in millidB |
| Level change | `10·log10(⟨y,y⟩/⟨s,s⟩)` in millidB |
| RMSE | `floor(1000·sqrt(mean((y−s)²)))` Q15 milli-units |
| Lag | Deterministic raw cross-correlation; ties prefer the smallest absolute lag |
| Peak / clipping | Q15 peak milli-units and samples at or above the declared threshold |

STOI and DNSMOS P.835 are **never approximated**. Both remain blocked until
the exact pinned artifacts are staged and hash-admitted. The historical
report's STOI, SI-SDR, RMSE and RTF values are retained as source-reported
aggregates only; they are not recomputed, pooled or promoted.

## Frozen synthetic controls

All controls use one authored 9,600-sample Q15 fixture with six segments:
initial clean speech, noisy speech, low-SNR speech, a noise-only pause, final
clean speech and restored noisy speech. The fixture is generated from integer
triangle harmonics and an integer LCG noise stream. No audio file is written.

| Control | Purpose | Global SI-SDR (millidB) | Global SNR (millidB) | Level change (millidB) |
| --- | --- | ---: | ---: | ---: |
| `identity_input` | Exact identity | 999000 (cap) | 999000 (cap) | 0 |
| `noise_only_quarter` | Attenuate pause noise only | 32632 | 32634 | −4 |
| `speech_initial_tenth` | Damage initial speech only | 6657 | 7494 | −1066 |
| `half_gain` | Gain-only change | 83140 | 6021 | −6021 |
| `dc_offset_plus_500` | Offset-only change | 999000 (cap) | 23139 | 21 |
| `bounded_8000` | Hard saturation | 11369 | 9442 | −2476 |

The identity control is bit-identical. The gain-only control demonstrates
that SI-SDR alone does not detect level change; SNR and level change do.
Per-region attenuation likewise stays SI-SDR-invariant, while its global
SI-SDR falls only because changed and unchanged segments are mixed. This is
why the harness reports gain-sensitive metrics beside SI-SDR. The
speech-damage and saturation controls demonstrate that the screen can detect
preservation loss. All controls are `is_candidate=false`,
`is_ears_candidate_output=false`, `qualifies=false` and
`is_scorer_qualified=false`.

The alignment probes use fixed zero-lag scoring of shifted copies at
−16, −8, 0, +8 and +16 samples. Zero shift is the unique best SI-SDR probe;
this is a synthetic alignment check, not a measured content delay.

## Adverse, missing and invalid handling

`report.json` records 60 rejected inputs, each with an unchanged synthetic
state. Rejections include duplicate JSON keys, NaN/Infinity constants,
malformed JSON, missing/extra manifest/item/output/scorer fields, wrong
schema, corpus ID or licence, unsupported rates and frame, zero/oversized
item counts, duplicate sample or candidate IDs, bad SHA-256 values, absolute/
traversal/non-`data/` paths, zero/huge durations, empty outputs, output sample
count mismatch, missing/extra/invalid scorer pins, missing/empty/mismatched
signals, nonfinite/out-of-range/string/bool samples, invalid lag and clipping
bounds, duplicate/out-of-range/nonfinite aggregate rows, missing manifest
files, absent/unknown scorers and the blocked real-screen gate.

Missing real corpus, real scorer, real outputs and listening evidence are
`blocked`, not passes. The valid synthetic control and the invalid/missing
cases are both validated through the same reported bundle.

## Reproduction

Run from this directory. Python 3.11+ and the standard library are sufficient.

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest discover -s . -p 'test_*.py' -v
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
```

`run.py` performs three cold-start regenerations and requires byte-identical
`report.json`, `report.json.sha256`, `contract.json` and `SOURCES.sha256`.
The current report file SHA-256 is
`077f6acfb253dfc7d0de6a72b77d1c977fdf5289ec6333d1a3620dd372f45a1f`.

The board check is run read-only from the separate platform repository:

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-EARS-PRESERVATION-SCREEN-AND-SCORER-HARNESS
```

## Evidence-profile application

| Required item | State | Evidence |
| --- | --- | --- |
| Scorer, corpus and cohort pinned | blocked | No EARS archive, prepared cohort, pystoi or DNSMOS artifact is staged |
| Aggregation and failed items | synthetic only | Deterministic item-weighted mean/median/p95 and explicit failed/blocked lists on authored controls |
| Paired/unpaired/synthetic/human separation | synthetic only | Input-referenced synthetic controls only; no clean-reference, human or source-reported pooling |
| Invalid and valid case validation | synthetic only | One representative valid control row and 60 rejected cases through the same bundle |
| Rights, provenance and listening separation | blocked | CC BY-NC 4.0 local non-commercial terms retained; no audio, consent, listening set or playback grant |
| Exact runtime or source | blocked | No scorer runtime, source revision, dependency lock, model digest or candidate output |

## Remaining release gates

All eight gates are `blocked`:

1. Exact EARS archive, provenance, CC BY-NC 4.0 terms and rights review.
2. Exact prepared input manifest and candidate outputs with SHA-256.
3. Hash-admitted pystoi 0.4.1 and DNSMOS P.835 artifacts.
4. Frozen 743-item no-clean-reference protocol and aggregation.
5. Representative valid and invalid real items through the exact bundle.
6. Separate rights-cleared listening or ASR/content control.
7. Opt-in harness review with no SDK boundary, build or CI change.
8. Explicit proceed/defer decision and independent exact-head approval.

No provider, descriptor, registry entry, installed v0 behavior, ABI, default,
shared build, dependency lock or CI is changed.
