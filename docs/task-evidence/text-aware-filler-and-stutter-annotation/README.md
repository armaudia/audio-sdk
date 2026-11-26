<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-TEXT-AWARE-FILLER-AND-STUTTER-ANNOTATION — DEFER blocker package

Task-local, **proposal-only**, **incomplete**, and **not qualified** evidence for
`text-aware-filler-and-stutter-annotation`. Profile: **rate**. Decision: **DEFER** before
`opt_in_adapter_exposure`. A missing result never qualifies the candidate.

## What is verified

- Stable linked task-row identity is gated; mutable full `TASKS.json` is never hashed.
- Read-only source and boundary pins match expected SHA-256 values.
- Fixed absence probes confirm no checkpoint/runtime/rights/protocol/cohort assets are present.
- Deterministic identity control exercises declared public v0 geometry only (16 kHz mono float32, 160 samples/frame); it has no qualification effect.
- Adverse/missing/invalid/nonfinite request and PCM cases fail closed before processing.
- Eight release gates are blocked with concrete external reopening conditions.
- Scope is task-local to this evidence directory; shared SDK files are unchanged.

## Blocked release gates

- **G1 exact_task_scope_and_source_identity**: No exact licensed source, streaming ASR transcript source, cleanup stage, or text-aware filler/stutter annotation implementation is admitted for this candidate. Inventory records the blocker as unavailable/blocked with no evaluated streaming ASR transcript source or cleanup stage and no semantic-preservation/disfluency target protocol.
- **G2 exact_checkpoint_runtime_and_weight_setup**: Byte-pinned model/checkpoint weights, tokenizer/aligner assets, and a complete runtime/lockfile are absent. No immutable artifact revision, byte count, or SHA-256 exists for required assets.
- **G3 rights_consent_and_redistribution**: Written code, checkpoint, training-data, transcript/corpus, reference-voice consent, output-use, and redistribution terms are not staged. No rights bundle is present.
- **G4 frozen_protocol_and_cohort**: A frozen semantic-preservation/disfluency target protocol, labeled filler/stutter/breath/click cohort, and exact evaluation manifest are absent.
- **G5 rate_profile_matched_evidence**: Rate/profile evidence is absent: no source/output mapping, duration, pitch, transient audibility, 1x/rate-change controls, pause/filler decisions tied to source timestamps, or speech-preservation measurements exist.
- **G6 alignment_timing_and_streaming_behavior**: Exact-runtime alignment, content delay, first-output/tail timing, memory, RTF, paced streaming behavior, and rebuffer/drift/final-partial-window evidence are absent.
- **G7 failure_controls_and_nonqualification**: No real candidate run exists. Missing/invalid/nonfinite/adverse cases must fail closed; no missing result may qualify the candidate.
- **G8 opt_in_adapter_and_release_gates**: No opt-in adapter intake, descriptor/registry/default decision, listening/device timing, benchmark validation, independent exact-head review, or release approval has started.

## Non-claims

- No text-aware filler/stutter annotation was executed.
- No model, checkpoint, weights, runtime, ASR transcript source, or cleanup stage was downloaded, vendored, loaded, or executed.
- No real audio, corpus, or reference transcript was read.
- No semantic-preservation or disfluency target protocol was measured.
- No listening, device timing, RTF, memory, or deadline measurement was run.
- No SDK provider, descriptor, registry, default, public ABI, CONTRACTS.md, shared build, or CI file was changed.
- No benchmark, board, handoff, or release claim was made.

## Reproduction

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --readme
PYTHONDONTWRITEBYTECODE=1 python3 run.py --check
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
```

## Digest table

<!-- digest-table:start -->
| Artifact | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `78cceaa5ea8361b360040c69b19c458d795a33ef712377cf949dbcc03d4dc0eb` | 1885 |
| `reference.py` | `a092673d1b27c1a2e93b90dde4d005e07fc9a42afa9b116faaafc1b06148fd61` | 40347 |
| `report.json` | `2975547974cd4dc963efc1c8b4249d302e68018cf83fa4b5c14d840d60ff287b` | 21429 |
| `run.py` | `fa51961b4d57a336fc30a81deb6ef8d7a76209a2ecc1da0a239a9214b67872c1` | 6557 |
| `test_reference.py` | `f8b1d34e6409c34895b80fc210a0e170c771a96567c90f3eb47d577211eeb93e` | 2536 |
| `verify.py` | `589aa9565515d9bce252616fc369b8839a206ffd562e9d9562ace30d103c156c` | 2608 |
<!-- digest-table:end -->

`contract.json` and `SOURCES.sha256` are excluded from the README table to avoid a self-reference cycle. They are pinned in `SOURCES.sha256` and checked by `verify.py`.
