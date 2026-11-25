<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-LLVC — LLVC blocker evidence

**Status: `proposal_only_not_qualified`; readiness `incomplete`; decision
`DEFER`; qualification `not_qualified`.** This directory contains bounded,
deterministic, task-local evidence for the LLVC voice-conversion row. It is
**not LLVC**: no checkpoint, weights, vocoder, model output, real corpus,
downloaded runtime, listening result, device measurement, benchmark or release
claim is included. **No result here qualifies LLVC.**

## Exact blocker: the checkpoint and pinned runtime are absent

The MIT-licensed **source checkout is present** at an exact revision, but the
exact checkpoint and the historical evaluation runtime are **not present**.
Nothing was fabricated, reconstructed or downloaded.

| Item | Status |
| --- | --- |
| Source checkout | **Present and pinned**: `research/voice-conversion-eval-20261101/repos/llvc`, `KoeAI/LLVC` commit `1627c5d358cf9bb2b92b0ccc513d8b36807c923d`, MIT licence, 51 non-`.git` files, tree digest `e7930ed0181722b6e6e701d662241e76552dd4f16c600a4f8a84c55977aa762b` |
| Required checkpoint | **Absent**: `G_500000.pth`, source-reported 37.7 MiB, upstream `KoeAI/llvc` download path; **no SHA-256 or byte count exists locally** |
| Required runtime | **Absent/unpinned**: the historical PyTorch / TorchAudio / SpeechBrain / Auraloss environment was removed; there is no lockfile or wheel hash set, and `torch` is not importable here |
| Weight licence / consent | **Unresolved**: MIT covers the source checkout only; checkpoint redistribution terms and consent for the built-in any-to-one target voice are not established |
| Historical target reference | **Provenance unconfirmed**: the p360 reference came from an upstream RT-VC demo and is not included or used |
| Historical evidence | One 9.655 s LJ Speech conversion, Whisper Tiny EN WER 0%, source-reported RTF 0.123 and 120.785 ms inferred latency; **not reproduced here** and never qualified |
| Workspace search | Bounded read-only checks found the empty `research/voice-conversion-eval-20261101/checkpoints/` directory but **no** `G_500000.pth`, `llvc_models`, checkpoint file, pinned eval environment or local Hugging Face LLVC cache |
| Rights requirement | Recorded weight/consent decision, confirmed target-reference provenance, and an approved use/redistribution scope for the checkpoint, runtime and converted output, all before any reproduction, adapter or release |

The machine-readable record is `report.json` → `upstream_blocker`
(`status="blocked_weights_and_runtime_absent"`, `weights.sha256=null`,
`weights.byte_count=null`, `runtime_digest=null`,
`no_upstream_parity_claim=true`), plus `source_probe`, `weights_probe` and
`runtime_probe`. `contract.json` carries the same blocker and all eight blocked
release gates.

Because the checkpoint and runtime are missing, **no result qualifies LLVC**,
no provider is registered, and release gate `RG-01` stays blocked.

## Exact scope

- Work is confined to `docs/task-evidence/llvc/`. Shared CMake,
  `CONTRACTS.md`, public headers, descriptor registry/defaults, installed v0
  behaviour, board/handoff files, CI, rulesets and `main` are untouched.
- Installed v0 remains **16 kHz, mono, float32, 160 samples per frame**. No
  voice-conversion provider is installed or registered.
- There is no C provider, installed target or public API/ABI change. LLVC
  needs caller-supplied weights and a heavy Python model runtime, so a truthful
  adapter cannot exist before the weights/runtime gates pass.
- No request is ever processed as LLVC. Valid requests fail closed with
  `WEIGHTS_ABSENT`.
- Missing, invalid, nonfinite and out-of-range requests fail closed with no
  metrics. No missing result qualifies the candidate.
- Board linkage is projected from **stable row identity only** (`task_id`,
  `title`, `mode`, `repository`, `component`). Mutable status, owner, review,
  handoff, priority, claim and history never enter canonical bytes and are
  never a gate. The full mutable `plan/swarm/TASKS.json` is **not hashed** into
  any canonical artifact.

## What `reference.py` actually does

`reference.py` is a standard-library-only evidence builder, not a voice
converter:

1. **Strict request validation** at the public v0 geometry. Exactly
   `candidate`, `sample_rate_hz`, `channels`, `frame_samples`, `samples`,
   `epoch`, `first_input_sample`, `lifecycle`, `execution_mode` and
   `target_condition` are accepted. Unknown or missing fields, wrong geometry,
   wrong sample count, booleans, strings, nonfinite values, out-of-range values,
   negative epoch or position, closed/drained lifecycle, unknown modes and any
   target other than `builtin_any_to_one` are rejected before any candidate
   call.
2. **Fail-closed candidate dispatch.** A valid request raises `WeightsAbsent`.
   There is no fallback model, surrogate converter or identity substitution.
3. **Exact source probe.** It recomputes the digest over every non-`.git` file
   in the pinned local checkout and checks the commit, file count and MIT
   licence pin. It never imports or executes upstream code.
4. **Weights/runtime probes.** Bounded file, directory and module-name checks
   only; no archive is opened, no network is used and nothing is installed.
5. **Config-derived geometry.** From the pinned `experiments/llvc/config.json`
   and the historical ASR record it derives 208-sample (13.0 ms) chunks,
   32-sample lookahead, 240 samples (15.0 ms) algorithmic offset and 743 chunks
   for the 9.6550625 s source. These are arithmetic facts about the declared
   config, **not measurements**.
6. **Generated harness stimuli** for silence, impulse, step, sweep and
   speech-like surrogates. Only peak, RMS, digest and finite counts are
   reported; no candidate processing is applied.
7. **Stable board identity** from the linked row only.
8. **Canonical report and contract bytes** with `sort_keys=True`, compact
   separators, `allow_nan=False` and exactly one trailing LF.

It does **not** load a checkpoint, implement an encoder/decoder, estimate a
vocoder, score identity or naturalness, or produce audio.

## Historical measurements are not local results

The only LLVC-specific quality/timing numbers in the workspace are
*source-reported* by the historical evaluation README. They are pinned for
provenance and reproduced as explicit source-reported fields:

| Field | Historical value | Local status |
| --- | --- | --- |
| Utterances | 1 (LJ Speech `LJ001-0001`, 9.655 s) | not re-run |
| ASR | Whisper Tiny EN WER 0.00% | historical JSON only; not re-scored |
| Chunk | 13 ms (208 samples) | derived from pinned config |
| Algorithmic offset | 15 ms (240 samples = 2·L + chunk) | derived from pinned config |
| RTF | 0.123 (≈8.1× slower than real time) | **not measured here** |
| Inferred end-to-end | 120.785 ms | inferred upstream; **not device-measured** |
| Identity/similarity | not scored | still not scored |
| Naturalness | not scored | still not scored |
| Target | built-in any-to-one, **not** p360 | recorded; p360 provenance unconfirmed |

Arithmetic on the source-reported RTF gives ≈105.69 ms average inference and
≈120.69 ms inferred end-to-end, reinforcing that the 13 ms chunk deadline is
missed by ≈9.3×. This is arithmetic, not a new measurement.

## Voice acceptance profile application

`plan/swarm/VERIFICATION.md` assigns the voice profile. With the checkpoint and
runtime absent, the profile maps as follows:

| Required element | Local status |
| --- | --- |
| Permitted input and target reference scope | `blocked_single_utterance_and_unconfirmed_target_provenance` |
| Task and language/speaker groups | `blocked_one_english_speaker_no_groups` |
| Text and semantic content | `source_reported_one_utterance_wer_not_reproduced` |
| Identity / similarity | `blocked_not_scored` |
| Naturalness | `blocked_no_listening_or_mos` |
| Alignment, first output and tail timing | `source_reported_inferred_not_device_measured` |
| Exact target condition | `recorded_builtin_any_to_one_not_p360` |
| Consent, reference availability and output use | `blocked_rights_and_consent_unconfirmed` |
| Paired quality control | `blocked_weights_and_runtime_absent` |
| Clean-reference preservation | `blocked_no_paired_clean_reference` |
| Numerical / nonfinite behaviour | `partial_local_harness_only` |
| Candidate output | `blocked_weights_and_runtime_absent` |

## Deterministic local results (not candidate results)

Harness stimulus characterisation on generated 16 kHz samples:

| Stimulus | Samples | Peak | RMS | Nonfinite |
| --- | ---: | ---: | ---: | ---: |
| `silence` | 1,600 | 0.000000 | 0.000000 | 0 |
| `impulse` | 1,600 | 0.500000 | 0.012500 | 0 |
| `step` | 1,600 | 0.250000 | 0.176777 | 0 |
| `sweep` 200→3000 Hz | 1,600 | 0.300000 | 0.212109 | 0 |
| `speech_like` | 3,200 | 0.344139 | 0.146388 | 0 |

The speech-like surrogate has source-anchored voiced/pause RMS contrast
**49.35 dB**; this is a signal proxy, not intelligibility, MOS or listening.

Rejection evidence:

- 20 invalid request cases: all rejected, `metrics=null`;
- 6 invalid JSON cases (duplicate key, NaN, ±Infinity, trailing data, syntax):
  all rejected;
- missing result: `status=blocked`, `metrics=null`,
  `qualifies_candidate=false`;
- harness identity control: byte-identical for every generated stimulus;
- valid LLVC request: rejected with `WEIGHTS_ABSENT`;
- weights probe: absent; runtime probe: absent/unpinned.

Every candidate row remains `blocked_weights_and_runtime_absent` with
`metrics=null`. There are no candidate metrics, quality scores, speaker
similarity, naturalness, latency or device claims.

## Eight blocked release gates

| Gate | Blocked reason |
| --- | --- |
| `RG-01` exact source and checkpoint pin | Source is pinned; `G_500000.pth` is absent with no SHA-256/byte count. |
| `RG-02` licence, rights and target-reference review | Weight terms, built-in target consent and p360 provenance are unresolved. |
| `RG-03` exact runtime build and install parity | The historical environment was removed; no lockfile or wheel hashes exist. |
| `RG-04` model geometry, delay, drain and mode parity | No checkpoint load; 208/32/240-sample geometry was not exercised. |
| `RG-05` rights-qualified paired cohort, identity and naturalness | Only one historical utterance; identity/naturalness unscored. |
| `RG-06` content preservation and adverse cases | The single WER result was not reproduced; clean/peak/nonfinite controls absent. |
| `RG-07` target-runtime timing, memory and callback suitability | Historical RTF/latency is not a paced device or callback measurement. |
| `RG-08` provider intake, public surface, review and release | No adapter, descriptor, public-surface decision or independent review exists. |

## Reproduction and verification

From this directory:

```sh
python3 run.py --all
python3 test_reference.py
python3 verify.py
```

`run.py --verify-repro` regenerates every canonical byte in memory and compares
it with the committed files; `verify.py` additionally runs three cold-start
regenerations, checks strict JSON, exact pins, stable board identity, licensing,
task-local git scope and blocker semantics. All four must pass.

## Non-claims

No LLVC checkpoint, weights, output, runtime, corpus, consent, listening panel,
identity/naturalness score, latency, callback, benchmark or release claim is
made. No installed v0, public API, C ABI, descriptor, registry, default, shared
build, CI, board or handoff change is made. Historical values remain labeled
with their original one-utterance scope.
