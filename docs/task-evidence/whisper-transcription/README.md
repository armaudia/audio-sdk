<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WHISPER-TRANSCRIPTION — Whisper transcription evidence boundary

Task-local, proposal-only, incomplete, not-qualified evidence for
`whisper-transcription` (`SDK-WHISPER-TRANSCRIPTION`, `research-control`,
Evidence profile). Decision: **DEFER**. Missing evidence never qualifies.

This package does **not** register a provider, expose a processor, change
public API/ABI, change `CONTRACTS.md`, change shared build/CI behavior,
download models, read real audio, perform listening, measure device timing,
run benchmarks, or make release/streaming-ASR claims.

## Scope

The task asks for an optional SDK developer/evidence adapter alongside
audio-bench with a documented proceed/defer decision before exposing Whisper
transcription as a processor. Use frozen decoding and transcript normalization
for WER; no streaming ASR claim from scoring.

Current evidence is external research-only: the pinned voice-conversion
evaluation records Whisper Tiny English ASR scoring and WER normalization.
This package preserves that boundary as deterministic, auditable DEFER
evidence only.

## Source pins

| Path | SHA-256 |
| --- | --- |
| `research/voice-conversion-eval-20261101/README.md` | `b2c5e168713eebe0e6ddd186d3bf5b9833839b8db93fe7ff2231bb784cbfa074` |
| `research/voice-conversion-eval-20261101/scripts/score_conversion.py` | `d5e351c7e33645eb54ec30c23fa14f8c228bb628898856eaa94a4263c6cfbdbd` |
| `research/voice-conversion-eval-20261101/scripts/run_llvc_eval.py` | `d268eb6dca48f88ae03802efd566f7053ac375be82555bd3dac343d750a5488c` |
| `research/voice-conversion-eval-20261101/results/source_asr.json` | `890e2e5c5000a9251142881645eb1fc406861e740cd84e12d556b3830999035c` |
| `research/voice-conversion-eval-20261101/results/llvc_asr.json` | `2d8f31e91ea06efed6611a0aa41edf2babb08625a2da22fe30f4333554115c41` |
| `research/voice-conversion-eval-20261101/agent-matrix-crosswalk/REPORT.md` | `b7db9a73b45b3a8918e99453e0de00c9f8f2f64604acee56c3838d3a10e2f9b6` |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |

## Boundary pins

| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |

## Exact external blockers

| ID | Status | Summary |
| --- | --- | --- |
| `BLK-01` | open | No in-worktree Whisper transcription adapter/runtime package; cited ASR use remains external research-only. |
| `BLK-02` | open | No rights-cleared pinned audio/corpus/license bundle for transcription scoring. |
| `BLK-03` | open | No deterministic task-local conformance bundle for valid/invalid/missing transcription scoring cases. |
| `BLK-04` | open | No measured device/runtime timing or streaming-ASR evidence; WER scoring is not a streaming claim. |
| `BLK-05` | open | No independent review/hosted CI/release decision. |

## Release gates

| ID | Status | Summary |
| --- | --- | --- |
| `RG-01` | blocked | No frozen Whisper transcription adapter/runtime staged in this task-local package. |
| `RG-02` | blocked | No rights-cleared, pinned audio/corpus/license bundle. |
| `RG-03` | blocked | No deterministic task-local conformance run or invalid/missing-case bundle. |
| `RG-04` | blocked | No device/runtime timing or streaming-ASR evidence; scoring only. |
| `RG-05` | blocked | No independent review, hosted CI, or release decision. |

## Reproduce

From this directory, with pinned Python and deterministic env:

```sh
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0 python3.12 verify.py
```

From SDK worktree root:

```sh
python3 scripts/ci.py
python3 -m reuse lint
git diff --check
```

`verify.py` is read-only for committed evidence files; it writes only to a
temporary directory for cold-start regeneration checks.
