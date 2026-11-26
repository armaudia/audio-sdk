<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SIMULSTREAMING — SimulStreaming caller-supplied-asset feasibility boundary

Task-local, proposal-only, `incomplete`, `not_qualified` feasibility and evidence
package for `SimulStreaming` (`component_id=simulstreaming`). The rate acceptance
profile is defined in `plan/swarm/VERIFICATION.md` and assigned by
`plan/INVENTORY.json` (candidate record 34). Base commit:
`f93d25f3d455a4278030d1bf0a3338dc6f8b95fe`; branch:
`swarm/SDK-SIMULSTREAMING`. Decision: **DEFER** before
`opt_in_adapter_exposure`; no missing, blocked or synthetic result qualifies the
candidate.

## What this package does and does not do

This package models only a metadata **caller-supplied-asset boundary** at
16 kHz, mono, `float32`, 160-sample frames. It validates caller manifest fields,
absolute paths, SHA-256 values, byte counts and format before failing closed
with `SIMULSTREAMING_ASSET_IDENTITY_UNPINNED`. It never imports, builds,
downloads, loads or executes SimulStreaming, Whisper-Streaming, Whisper, NeMo,
sherpa-onnx or any other ASR backend. No source checkout, weights, audio,
cohort or runtime bytes are vendored. No adapter or provider is registered, no
default is selected, and no public API, ABI, registry, build or CI file is
changed.

All rate controls here are **synthetic, deterministic, integer-only sample and
frame geometry**: 165 source samples mapped to one full 160-sample frame plus a
5-sample final partial window with 155 zero-padding samples, half-open source
intervals, and swap/insert/truncate controls. These controls are explicitly
**not audio, not a transcript, not SimulStreaming output and not WER/latency
evidence**. There is no WER/CER score, cutoff or end-of-turn delay, listening
result, device timing, benchmark or release claim. The upstream 3.3 s latency
figure is source-reported and is **no substitution** for local or mobile
evidence.

## Exact readiness conclusion

`DEFER` / `incomplete` / `not_qualified`. Gates `RG-01` through `RG-08` are all
blocked and non-qualifying. The exact external blockers are:

- **XB-01** — the census marks Whisper-Streaming/SimulStreaming
  `unavailable/blocked`: no local ASR checkpoint, streaming runtime or adapter
  and no local WER/latency result. The trials audit found `whisper`,
  `faster_whisper`, NeMo and sherpa-onnx absent; the reaudit found no exact
  weights or streaming adapters. No exact checkpoint path, revision, byte count
  or SHA-256 exists to pin.
- **XB-02** — no locked backend, tokenizer, model, language coverage,
  buffer/lookahead policy, partial/final commit, chunking, maximum-wait or
  drain geometry is staged. Installed v0 accepts only 16 kHz mono `float32`
  160-sample audio frames and exposes no transcript endpoint, so a streaming
  ASR result cannot be inferred from frame counts.
- **XB-03** — no rights-qualified conversational corpus with utterance and
  turn boundaries, explicit unknown regions, reference transcripts,
  speaker/session-disjoint splits, independent label review or pinned
  WER/latency scorer is staged.
- **XB-04** — no local ASR output, WER/CER, cutoff or end-of-turn delay,
  source/output mapping, duration/pitch/transient, playback buffering, paced
  causal state, dropped/stale chunk, device timing, benchmark, opt-in intake
  or independent release review exists.

Reopening requires the exact licensed ASR artifact identity and locked runtime,
reviewed rights, a rights-cleared turn-labelled cohort with pinned scorers,
matched rate and streaming outcomes on that exact runtime, and a separate
opt-in intake reviewed at an exact head with the default OFF.

## Matched source evidence

Five pinned lines are checked byte-for-byte: census record 34
(`candidate_matrix.csv`, line 35), the ASR trials audit
(`agent-vad-asr-trials/REPORT.md`, line 11), the SimulStreaming candidate row
(`agent-segmentation/REPORT.md`, line 26), the blocked reaudit
(`agent-blocked-reaudit/REPORT.md`, line 19) and the matrix audit
(`agent-matrix-audit/REPORT.md`, line 23). They are matched to component
`simulstreaming`, record 34, task `SDK-SIMULSTREAMING` and the `rate` profile.
They are **provenance only**, never a local result.

## Stable board identity

Only stable row fields (`id`, `title`, `repository`, `mode`, `depends_on`,
`component`) enter canonical bytes and gates. The full mutable
`plan/swarm/TASKS.json` is never hashed. Stable-row SHA-256:
`f1320dc5de33e8c529ccde6b8625beb1c3d39097c68ca14b26308aa17c4fe28a`.

## Source pins (SHA-256)

`source:` paths are workspace-relative. Every row is checked by `verify.py`.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:research/voice-enhancement-20261101/agent-blocked-reaudit/REPORT.md` | `5eead5c60d90526c2ce88f249fe813b3ec6e6a9f96f9712269460ae9f81add14` |
| `source:research/voice-enhancement-20261101/agent-matrix-audit/REPORT.md` | `865b0031d357b7009c2876f997ca188440451fb65d5cef3561e9848f34eaf1d0` |
| `source:research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `source:research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `source:research/voice-enhancement-20261101/findings.md` | `78ab7fdf560f2b652a83c0a07ae5735120ae8786f0935a3cf4df8f9dd92bf07c` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

Paths are SDK-worktree-relative. All are unchanged and machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `docs/task-evidence/fastconformer-streaming-asr/README.md` | `12b8a50552a9dbb39fbed6d52bf543a7c54a53165101cf8d7f0aaa3abd5edebc` |
| `docs/task-evidence/seed-tts/README.md` | `5c9e4d3ec5e7940a8aa164cf6957aaebd2fa7be79d7a7b94afd92cb05bd52d83` |
| `docs/task-evidence/survey-det-02/README.md` | `40c05936132ed4add0d1a97a9139f42c170711130c447f18d36b11c7669221b1` |
| `docs/task-evidence/survey-rec-01/README.md` | `01e54b306313f13f97e1c9f4a08f5ebd98cbf570617644a028ae2bca3d4f4acb` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Caller-supplied asset contract

`audio-sdk/simulstreaming/caller-supplied/0.1` is metadata-only. Required fields
are `adapter`, `configuration_id`, `checkpoint_path`, `checkpoint_sha256`,
`checkpoint_byte_count`, `checkpoint_revision`, `source_revision`,
`runtime_lock_digest`, `rights_digest`, `sample_rate_hz`, `channels`,
`frame_samples`, `sample_format`, `transcript_cohort_digest` and
`endpoint_label_digest`. The validator permits only the two declared task-local
metadata configuration labels, requires a 40-hex source revision, the pinned
format, absolute checkpoint paths and hash/size-matched checkpoint bytes. Even
a hash-matched caller file still fails as
`SIMULSTREAMING_ASSET_IDENTITY_UNPINNED`; no asset is loaded or run.

## Scope gate

`verify.py` resolves the newest merge-base of `HEAD` with `origin/main`, falling
back to `main` only when `origin/main` is unavailable. If no base exists it
emits `scope_base_unavailable`. Any tracked branch difference outside
`docs/task-evidence/simulstreaming/` emits `base_out_of_scope_change` and fails
closed, so a sibling evidence package merged to `main` later does not create a
false positive. Three regression tests cover newest-base selection, `main`
fallback and out-of-scope/missing-base rejection.

## Reproduce

All commands are read-only except for the canonical artifacts in this directory
and the temporary CI output under `build/ci`.

```sh
cd /Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-SIMULSTREAMING/docs/task-evidence/simulstreaming
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --all
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 run.py --check
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 verify.py
python3 -m reuse lint
git diff --check
cd ../..
PYTHONDONTWRITEBYTECODE=1 /Users/htsakanyan/.pyenv/versions/3.12.16/bin/python3.12 scripts/ci.py --output build/ci
```

Canonical JSON uses sorted keys, compact separators, `allow_nan=False` and one
trailing LF. Three fresh builds are byte-identical; comparison is exact
SHA-256 with no tolerance. `report.json.sha256` is the canonical sidecar and
`SOURCES.sha256` pins source, boundary and local artifact bytes. `verify.py`
validates both README digest tables against the live pins.

## Licensing

No SimulStreaming, Whisper-Streaming or Whisper source, weights, corpus or
output bytes are redistributed here. Code, weights, data, consent, reference
availability and product-use terms remain unreviewed and independent. All
package files are Apache-2.0 via SPDX headers and the repository `REUSE.toml`
annotation for `docs/**`.
