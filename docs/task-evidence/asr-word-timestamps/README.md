<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-ASR-WORD-TIMESTAMPS — ASR word-timestamp speech-rate proxy blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
`asr-word-timestamps` (title "ASR word timestamps"). Decision: **DEFER** before
any implementation or intake step; `status=incomplete`, `proposal_only=true`,
`qualification.status=not_qualified`. No result qualifies.

The evidence source
([`playback-speed-candidates.md`](../../../../cpp-library/pipeline-validation/playback-speed-candidates.md))
calls ASR word timestamps ("words/min") the *most robust speech-rate proxy when
an ASR path already exists*, and notes that licence, commercial use and
availability all depend on the chosen ASR. It names no licensed engine, weight,
runtime or permitted corpus.

This package does **not** import, load, execute, copy or download an ASR engine,
model weight, tokenizer, PyTorch/ONNX runtime, audio signal, transcript, word
span, TextGrid or corpus. It does not extract timestamps, compute a model-backed
speech rate, listen, time a device, run a benchmark or make a release claim. It
pins the exact research inputs, pins the unlicensed model/runtime bytes that
exist in a mutable scratch tree, defines a fail-closed admission boundary for a
future run, implements the exact word-count-to-rate arithmetic that boundary
uses, and records one explicitly synthetic arithmetic control that can never
qualify. Only `docs/task-evidence/asr-word-timestamps/` is written; no provider,
registry, descriptor, default, installed-v0, ABI, shared build, CI, board or
handoff file changes.

## Profile mismatch and exact acceptance scope

The task row and `plan/INVENTORY.json` assign the **Rate** acceptance profile.
`plan/swarm/VERIFICATION.md` defines Rate as source/output mapping, duration,
pitch and transient audibility, playback buffering, 1× and rate changes,
unfamiliar speech/music/silence, rebuffer/drift/final partial window, and
pause/filler decisions tied to source timestamps. ASR word timestamps are a
**measurement proxy**, not a time-stretch renderer or playback controller. All
eight Rate rows are recorded as **blocked** rather than reinterpreted. A future
review must supply Rate evidence for a composite path that contains a renderer
or record an explicit, reviewed waiver.

The task mode is `feasibility`. Its acceptance allows a readiness conclusion
with an exact external blocker as an investigation handoff; that does not close
the conditional implementation.

## Exact external blocker: present bytes, absent licence and qualification

The model and runtime bytes **are present** in the git-ignored scratch tree
`cpp-library/pipeline-validation/playback-speed/`, so they are pinned exactly.
Presence is not admission. Five facts block the candidate:

1. **No ASR source revision or complete licence bundle.** No Vosk/Kaldi or
   sherpa-onnx/Whisper checkout exists at an exact 40-hex revision. The Vosk
   model `README` states only `Copyright 2020 Alpha Cephei Inc`; the installed
   `vosk 0.3.44` `dist-info` has **no** `LICENSE` and `METADATA` says
   `License: UNKNOWN`. The `sherpa_onnx 2.0.1` `METADATA` says `Apache-2.0`, but
   no upstream source revision, complete notice bundle or bundled-third-party
   attribution is staged. A metadata string or classifier is not a grant.
2. **No model card, licence text or output-use decision.** The 14-file
   `vosk-model-small-en-us-0.15` tree (70,898,967 bytes) has no `LICENSE`,
   `NOTICE`, `COPYING` or model card. The 9-file
   `sherpa-onnx-whisper-tiny.en` tree (256,603,197 bytes) has no `LICENSE`,
   `README` or model card. Neither has an official archive name, archive
   SHA-256, source revision, attribution file or commercial/output-use decision.
3. **No pinned runtime or offline load.** The runtime is a mutable, git-ignored
   `.venv`. There is no lockfile, wheel/sdist archive, install digest,
   deterministic thread policy or clean-room offline load trace. No model or
   runtime was imported, loaded or executed here.
4. **No rights-cleared audio or independent word reference.** The two TTS clips
   carry construction-time labels from one synthetic voice; the AMI stitch has
   no reference transcript. There is no second annotator, adjudication,
   agreement statistic, human-verified word/filler/pause span set or reviewed
   AMI/CC BY 4.0 output-use decision. TTS labels are not independent timing
   gold.
5. **No reproduced result or Rate evidence.** The study recorded 121, 122 and 86
   Vosk word spans and batch gate wall times, but reports no words/min, boundary
   error, matched-word accounting, finite-output scan, uniform-timing baseline
   or timestamp-tied pause/filler preservation. Its batch gate time is context,
   not a streaming or device measurement.

Six exact blockers, all open:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | Exact Vosk/Kaldi or sherpa-onnx/Whisper source revisions plus complete licence, notice and bundled-third-party attribution with independent review. |
| `BLK-02` | Official model/tokenizer archives with byte counts and verified SHA-256, model cards, licence/notice text, attribution and a written commercial/output-use decision. |
| `BLK-03` | Locked offline runtimes with exact package/wheel/sdist hashes, archives, install/import digests, deterministic thread settings and a clean-room offline load trace. |
| `BLK-04` | Rights-cleared/consented audio with adjudicated word/filler/pause spans from at least two independent annotators, agreement, transcript and reviewed output-use terms. |
| `BLK-05` | A fresh offline extraction and scoring run with frozen scorer, exact matched-word accounting, finite checks, uniform-timing and no-alignment baselines, adverse/missing controls and a timestamp-tied pause/filler policy. |
| `BLK-06` | Target-device streaming timing/resources/deadlines, then a separate versioned OFF-by-default provider/tool intake with independent exact-head review. |

## Eight blocked release gates

| Gate | Title | Status |
| --- | --- | --- |
| `RG-01` | `source_revision_and_license_provenance` | blocked |
| `RG-02` | `weights_tokenizer_and_digests` | blocked |
| `RG-03` | `pinned_runtime_and_offline_load` | blocked |
| `RG-04` | `rights_cleared_audio_and_independent_word_reference` | blocked |
| `RG-05` | `word_timestamp_and_rate_accuracy_with_controls` | blocked |
| `RG-06` | `rate_profile_and_timestamp_tied_policy` | blocked |
| `RG-07` | `target_runtime_timing_resources_and_deadlines` | blocked |
| `RG-08` | `provider_intake_public_surface_and_release` | blocked |

Every gate is `qualifies=false` and carries an exact reopen condition in
`contract.json`.

## What is pinned

`SOURCES.sha256` pins the research report, playback-speed README, validation and
corpus scripts, corpus labels, recorded results, the SDK boundary files and the
merged sibling evidence packages for Vosk, Whisper+MFA, wav2vec2 and spatial
alignment. The mutable full `plan/swarm/TASKS.json` is **never hashed**; only
the stable projection (`id`, `title`, `component`, `mode`, `repository`,
`depends_on`) of the linked row and its dependencies gates anything.

`report.json` additionally pins the present scratch bytes:

- `vosk-model-small-en-us-0.15`: 14 files, 70,898,967 bytes, tree SHA-256
  `8d6008c80499a5724a91d53ec99e6df0c41064df4443e063af79d9e247bb14bb`.
- `sherpa-onnx-whisper-tiny.en`: 9 files (including test wavs), 256,603,197
  bytes, tree SHA-256
  `fae72e5493c2c9d09e1f2725332ba278952ba2489923fe695e040ecd6ee08da5`.
- Nine runtime metadata/module files, including `libvosk.dyld` (12,533,472
  bytes) and the `vosk 0.3.44` `METADATA` whose licence field is `UNKNOWN`.

The tree digest rule is SHA-256 over sorted
`relative\0file_sha256\0byte_count\n` rows. These bytes are never distributed by
this package.

## Admission boundary and synthetic control

`reference.py` validates a caller-supplied future run manifest: exact source
revision, model/tokenizer digests, licence acceptance, locked deterministic
offline runtime, 16 kHz mono audio with exact sample count, an independent
multi-annotator human reference, ordered non-overlapping finite word spans,
matched-word accounting, zero nonfinite outputs, both required baselines and
non-qualifying rights. It rejects missing/extra fields, absolute or traversal
paths, uppercase hashes, stereo/other rates, boolean-as-integer values, NaN and
Infinity (including non-finite JSON literals), negative/zero/overlapping/
out-of-range spans, count mismatches, a non-finite outcome count, out-of-range
rate/pause values, inconsistent words/min, a single annotator, construction
labels, missing baselines and any `claims_qualified=true`.

The accepted case is a **synthetic shape control**; acceptance is structural
admission only. The separate arithmetic control (5 words in 4.0 s over 1.0 s of
speech) yields exactly 75.000 words/min total, 300.000 words/min over speech and
a 0.750 pause ratio. Both are labelled
`synthetic_arithmetic_control_not_evidence` and `qualifies=false`.

## Reproduce and verify

```sh
cd docs/task-evidence/asr-word-timestamps
python3 run.py all                 # 3x byte-identical contract/report/sources
python3 -m unittest -v test_reference.py
python3 verify.py
```

`verify.py` checks strict JSON, every pin, canonical bytes, the stable linked-row
identity, eight blocked gates, 37 admission cases, SPDX sidecars, dependency
hygiene, task-local scope and three cold-start regenerations.

## Non-claims

- No ASR engine, model, tokenizer or runtime is imported, loaded or executed.
- No audio, transcript, word span or annotation is read as a signal or scored.
- No word timestamp, words/min, boundary, WER or finite-output result exists.
- No provider registration, public ABI, registry/default, shared build or CI
  change exists.
- No listening, device timing, benchmark, pipeline or release claim is made.
- Recorded Vosk word counts and batch times are provenance, not evidence.

See `LICENSES.md` for the licensing boundary.
