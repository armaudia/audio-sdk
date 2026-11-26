<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-MOONSHINE — Moonshine readiness blocker package

**Status: `proposal_only_incomplete`; evidence `incomplete`; decision
`DEFER`; qualification `not_qualified`; eight release gates blocked.** This
directory contains bounded, deterministic, task-local evidence for the Moonshine
feasibility row. It is **not** a Moonshine implementation, adapter or
provider. No Moonshine source checkout, model, streaming-model checkpoint,
tokenizer, config, runtime, audio, transcript, corpus, listening result, device
measurement, benchmark or release claim is present. **No result here qualifies
Moonshine.**

The structured inventory marks `moonshine` as `evidence_status=considered` with
the **Rate** acceptance profile (`verification_profile: rate`,
`plan/INVENTORY.json`). The task row is `mode=feasibility`; its acceptance asks
for the Rate profile plus exact scope, evidence, failure/control results and
remaining release gates, and explicitly allows a readiness conclusion with an
exact external blocker as an **investigation handoff** without closing the
conditional implementation. None of the prerequisites exists locally.

Task owner: `agent-MOONSHINE`; reviewer: `reviewer-MOONSHINE`. Claim base:
audio-sdk `7dc9c84b2ed963ecda895194b19e8d8979a2f748`; branch
`swarm/SDK-MOONSHINE`. Write scope is only `docs/task-evidence/moonshine/`.

## Candidate role and profile mismatch

The pinned evidence record
[`playback-speed-candidates.md`](../../../../cpp-library/pipeline-validation/playback-speed-candidates.md)
(line 879) records Moonshine as:

- **Role:** "Low-latency English STT".
- **Licence (source-reported):** "MIT code + MIT streaming models".
- **Fit:** "Very low latency, C API, streaming models".
- **Finding:** "English-first; timestamp granularity needs testing".

The note adds: "Moonshine is worth a look if the product is English-only and the
lookahead budget is tight: MIT code and MIT streaming models, low latency, C API.
Confirm token/word timing before relying on it." It is a content-gate
candidate — a speech-rate **measurement proxy** — not an actuator, renderer or
playback controller. Therefore Moonshine cannot by itself satisfy any Rate row
that requires a stretched waveform; all eight Rate rows are recorded as
**blocked**, not reinterpreted. A future review must either supply Rate
evidence for a composite path containing a renderer or record an explicit,
reviewed waiver. The task's `evidence` field points at the playback-speed
candidate record, so this package keeps the rate profile accounting rather than
substituting an ASR quality profile.

## Exact external blocker

The exact **source**, **model/streaming-model bundle** and **pinned runtime**
are all absent. The pinned census names only the public repository
`https://github.com/moonshine-ai/moonshine` and a source-reported licence
summary. It records no commit, license text, NOTICE, model card, checkpoint
identifier, tokenizer, ONNX or native weight, file name, byte count, digest,
runtime version, sample rate, sample format, frame hop or preprocessing
contract. Nothing is downloaded, vendored, staged, mirrored or inferred from
the repository URL or source-reported strings. Consequently:

- source identity, weight identity and licence terms cannot be pinned;
- the code licence and the "MIT streaming models" claim are unverified strings,
  and no training-data or output-use rights record exists;
- sample rate, sample format, tokenizer behaviour, streaming geometry and
  timestamp granularity are **unestablished** and are not invented;
- no Moonshine transcript, token span, word boundary, WER, words/min, latency,
  memory or RTF value exists or is reported;
- no missing, adverse, invalid or nonfinite evidence is promoted to a pass,
  partial qualification or capability claim.

Moonshine is an English-first streaming recognition gate candidate, not an
installed SDK processor and not a causal call-path component. Results from the
sibling ASR, playback-gate, recognition-survey or encoder packages are not
attributed to it.

| Missing artifact | Exact requirement |
| --- | --- |
| Source checkout | `moonshine-ai/moonshine` at an immutable 40-hex commit, with reviewed MIT license text, complete NOTICE and a per-file SHA-256 manifest from a reviewable tree |
| Model bundle | The caller-selected exact model and streaming bundle at an immutable revision: every ONNX or native weight, tokenizer, config, model card and terms file with byte count and SHA-256 per file |
| Runtime | A locked, reproducible, offline Moonshine C-API or Python runtime with exact interpreter, package and ONNX Runtime versions, device profile, lock SHA-256 and clean-room load trace |
| Rights | Reviewed code and weight terms, training-data provenance, output use, commercial use, redistribution and per-language derivative rights |
| Cohort | A frozen, consented English cohort with exact sample rate and duration, language/speaker groups, held-out splits, two-annotator adjudicated token/word/filler/pause spans, and 1×, rate-change, rebuffer, drift, final-partial, unfamiliar-speech, music and silence controls |
| Acceptance | Independent WER, boundary error at the declared granularity, words/min, pause ratio, content preservation, pitch, transient, buffering, drift, first-output/tail timing, resources, uncertainty, blind listening and target-device timing on the exact runtime |

The machine-readable record is `report.json` → `absence`, `upstream_record`,
`required_artifacts`, `exact_blockers`, `rate_profile`, `rate_outcomes`,
`granularity_control`, `admission` and `gates`. `contract.json` carries the same
disposition, pins, geometry and all eight blocked release gates.

## What this package verifies

1. **Absence evidence.** A fixed list of 25 workspace/worktree and home-cache
   probes is checked; no recursive walk is performed and all are absent.
   `reference.py` and `verify.py` fail if any probe later appears, so a stale
   "absent" claim cannot ship.
2. **Stable pins.** The reviewed planning records, the structured inventory and
   the candidate record are pinned by SHA-256, as are the SDK boundary files and
   the six merged sibling evidence reports used only as a boundary. These are
   read-only provenance inputs, not Moonshine evidence.
3. **Stable board identity.** Only the linked row's `id`, `title`, `component`,
   `mode`, `repository` and `depends_on` are projected and hashed. The mutable
   `plan/swarm/TASKS.json` file is **never hashed**; status, owner, claim,
   review, handoff, priority and history never enter canonical bytes and never
   gate this package.
4. **Exact rate arithmetic.** `reference.word_rate()` computes exact
   words/min, speech rate and pause ratio from integer sample spans using
   `fractions.Fraction` and fixed-precision `Decimal` rounding. It rejects empty,
   reversed, overlapping, out-of-range and non-integral spans and unsupported
   sample rates. This is arithmetic on caller-supplied spans, not recognition.
5. **Timestamp-granularity sensitivity.** Moonshine's own recorded caveat says
   timestamp granularity "needs testing". A deterministic synthetic control
   quantizes the same synthetic spans to 5 ms and 80 ms, and proves that a
   coarser declaration changes the derived rate and can make distinct tokens
   overlap. It is labelled
   `synthetic_contract_control_not_evidence` and never qualifies.
6. **Fail-closed admission.** A task-local manifest has a strict schema:
   missing/unknown fields, duplicate JSON keys, `NaN`/`Infinity`, floats,
   unsafe paths, duplicate or unsorted entries, unresolved or non-integral
   values, unsupported rates or granularities, non-offline or
   non-deterministic runtimes, construction-label references, fewer than two
   annotators, self-qualification and any false right are rejected. One
   synthetic structural control is accepted to prove the validator is not
   blanket-rejecting; it is labelled `synthetic_schema_control` and
   `qualifies=false`.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, `.gitattributes` and the
   root README are pinned by SHA-256 and verified unchanged. Installed v0
   remains 16 kHz, mono, float32, 160 samples per frame. No Moonshine provider
   is installed or registered; no descriptor, default, ABI, shared build, CI,
   board or handoff change is made.

## Timestamp granularity control

The control is pure arithmetic on hand-written spans; it uses no recognizer,
audio or transcript. Four synthetic cases:

| Case | Granularity | Result |
| --- | --- | --- |
| `fine_5ms` | 5 ms | Boundaries shift but do not overlap; derived rate changes |
| `coarse_80ms` | 80 ms | Distinct tokens overlap after outward rounding; derived rate unavailable |
| `aligned_80ms` | 80 ms | Already aligned; quantization is the identity |
| `final_partial_window` | 5 ms | 16,065-sample input yields 11 blocks with a 65-sample final partial block |

Summary: 4 cases, 2 boundary-stable, 2 granularity-sensitive, 1 overlapping
quantization, 0 qualifying results. The observation is a mechanism warning, not
a Moonshine measurement: the exact tokenizer and token/word timing remain
unverified.

## Rate profile application

| Rate requirement | Status here | Evidence |
| --- | --- | --- |
| 1× control | blocked | No measured Moonshine gate at 1×. |
| Rate changes and source/output mapping | blocked | No gate run over altered rates. |
| Duration and playback buffering | blocked | No rendered waveform, buffer occupancy or duration run. |
| Pitch | blocked | No stretched output and no pitch measurement. |
| Transient audibility | blocked | No waveform, listening or transient analysis. |
| Unfamiliar speech, music, silence | blocked | No rights-cleared stratified corpus. |
| Rebuffer and drift | blocked | No device clock, rebuffer, fill/flush or drift run. |
| Final partial window, timestamps and speech preservation | blocked | No real final window; granularity and pause/filler decisions uncalibrated. |

## Historical and peer boundary

The pinned candidate record contains one Moonshine **lead** and source-reported
context only. There is no local Moonshine run, output, metric, corpus or
runtime. No value is inferred from merged sibling evidence packages:

- `asr-word-timestamps` has the same Rate-profile *proxy* role but different
  engines, spans, cohort and rights; its architecture and bias notes do not
  transfer.
- `fastconformer-streaming-asr` is a different model family with a scheduler
  surrogate; its frame accounting is not a Moonshine tokenizer or timing result.
- `vosk-small-en-us-0-15-playback-gate` is a different gate engine with its own
  present-but-unlicensed bytes; its source-reported IoU and RTF are not
  Moonshine evidence.
- `whisper-tiny-en-mfa` is a different recognition and forced-alignment stack.
- `dynamic-int8-wav2vec2-base` is an encoder representation track, not an
  English streaming recognizer.
- `survey-rec-01` is a merged coverage survey with no measured Moonshine result.

The pinned `phase-vocoder-baseline` report is a rate/playback baseline pin only;
it contributes no gate content. The board has no separate Moonshine second row;
this package inherits no adjacent ASR, finetuning, voice, separation or pipeline
result.

## Admission contract (task-local; not an SDK, Moonshine or ASR contract)

The schema is `audio-sdk/moonshine-timestamp-cohort/0.1`. It requires an exact
source revision and license digest, a per-file weight manifest, a locked
offline deterministic runtime, 16 kHz or 48 kHz mono audio with exact sample
counts, a two-annotator adjudicated human reference independent of the ASR, an
ordered non-overlapping token span set, all six required controls, internally
consistent rate arithmetic, zero nonfinite/deadline outputs, `qualified=false`
and every right true. Admission never reads audio, loads weights or invokes a
model. A run manifest can be structurally admitted without any result becoming
qualified; promotion still requires the external gates.

## Eight blocked release gates

| Gate | Requirement | Status |
| --- | --- | --- |
| `RG-01` | Exact licensed source revision and snapshot | blocked |
| `RG-02` | Exact model, streaming model and tokenizer bundle | blocked |
| `RG-03` | Pinned offline runtime, device and deterministic load | blocked |
| `RG-04` | Rights, output use, provenance and redistribution | blocked |
| `RG-05` | Rights-cleared cohort and independent adjudicated spans | blocked |
| `RG-06` | Rate acceptance profile and timestamp granularity | blocked |
| `RG-07` | Content preservation, independent scoring and listening | blocked |
| `RG-08` | Opt-in provider intake, independent review and release | blocked |

Six open blockers (`BLK-01`…`BLK-06`) map to artifacts `A01`…`A06`; `A07`
(provider intake) and `A08` (release approval) stay blocked behind `RG-07` and
`RG-08`.

## Pinned source and boundary digests (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`;
other paths are relative to the SDK worktree. These are read-only provenance
pins, not Moonshine evidence.

| Pinned input | SHA-256 | Use |
| --- | --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` | Moonshine role, source-reported licence and granularity caveat |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` | Structured component row and Rate profile |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` | Unchanged plan and build surface |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` | Rate acceptance profile |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` | Unchanged public contract |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` | Unchanged provider table |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` | Unchanged session facade |
| `CMakeLists.txt` / `REUSE.toml` / `.github/workflows/ci.yml` | pinned in `SOURCES.sha256` | Unchanged build, licensing and CI |

The complete deterministic manifest, including every task-local artifact and the
six sibling report pins, is `SOURCES.sha256`. `verify.py` fails closed on a
missing, stale, malformed, duplicated or extra pin, on any worktree change
outside this directory (including committed ones, compared against the newest
merge-base with `origin/main` or `main`), and on any cold-start byte difference.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, expected counts, results, gates. |
| `contract.json` | Strict machine-readable `decision="DEFER"`, `proposal_only` / `incomplete`, `qualification.status="not_qualified"`, eight blocked gates, six open blockers and the admission contract. |
| `reference.py` | Strict validators, absence audit, stable board identity, exact rate arithmetic, granularity control, admission controls and canonical report/contract builders. |
| `run.py` | Regenerates contract, report, digest sidecar and manifest three times and requires byte-identical output. |
| `report.json` / `report.json.sha256` | Canonical evidence and its digest. |
| `SOURCES.sha256` | Deterministic manifest of all pinned inputs. |
| `test_reference.py` | Deterministic unittest acceptance suite (no skips, no network). |
| `verify.py` | Read-only strict JSON, pin, profile, licensing, merge-base scope and three cold-start regeneration verifier. |
| `*.json.license`, `*.sha256.license` | REUSE sidecars. |
| `LICENSES.md` | Upstream licence and asset-rights notes. |

## Reproduction

Run from this directory with bytecode disabled:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py all
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
git diff --check
python3 -m reuse lint
```

`run.py all` repeats three times and fails if any rebuild differs by one byte.
`verify.py` never writes to this directory: it builds three isolated scratch
copies with symlinks to the pinned read-only inputs and checks cold-start
regeneration there. It also gates this branch's merge-base diff so committed
out-of-scope files cannot pass.

## Remaining gates

Verified upstream provenance and licence text, a pinned model/tokenizer/runtime
and preprocessing contract, exact-runtime parity, a rights-cleared held-out
matched English cohort with independent adjudicated spans, calibrated token
timing, target-device pacing and telemetry, opt-in public-surface intake,
independent exact-head review and hosted checks, and release approval all
remain blocked. Missing or adverse evidence never qualifies the candidate. No
merge, formal approval or release action is taken here.
