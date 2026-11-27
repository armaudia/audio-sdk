<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-WHISPER-STREAMING — Whisper-Streaming / SimulStreaming feasibility blocker

Task-local, **proposal-only**, **incomplete**, **not qualified** evidence for
`SDK-WHISPER-STREAMING` (`whisper-streaming`, Rate profile, feasibility).
Decision: **DEFER** before any opt-in adapter exposure.

This package records the exact blocker: no local Whisper-Streaming /
SimulStreaming ASR checkpoint, streaming runtime, adapter, rights-cleared
reference transcript cohort, or measured WER/latency/Rate result is present in
this workspace. It makes no quality, timing, device, listening, benchmark, or
release claim. No model, weight, runtime, audio, transcript, or network access
is used.

## Scope boundary

- Write scope: `docs/task-evidence/whisper-streaming/` only.
- No provider/adapter registration, no descriptor/registry/default change.
- No public API/ABI, CONTRACTS, shared build, CI, or installed v0 behavior change.
- No download, model execution, real audio, listening, device timing, benchmark, or release claim.
- Missing evidence never qualifies the candidate.

## Rate profile

Applied from `plan/swarm/VERIFICATION.md` Rate row as blocked requirements:
source/output mapping, duration, pitch/transient audibility, playback
buffering; 1×/rate changes/unfamiliar speech/music/silence/rebuffer/drift/final
partial window; pause/filler decisions tied to source timestamps and speech
preservation. All blocked - no runnable candidate/runtime/cohort exists.

## Exact blockers

| ID | Requirement | State |
| --- | --- | --- |
| BLK-01 | Exact local ASR checkpoint/runtime with immutable hashes/provenance | No local checkpoint/streaming runtime/executable artifact present |
| BLK-02 | Rights-cleared frozen cohort with reference transcripts and WER/latency/Rate scoring | No local reference transcript cohort, scorer, or measured result staged |
| BLK-03 | Rights/publication/redistribution/product-use review | No per-asset rights record or publication review present |
| BLK-04 | Isolated pinned runtime and deterministic command recipe | No lockfile/runtime/execution trace staged |
| BLK-05 | Approved exact-runtime reference parity outputs | No approved reference/parity vectors exist |
| BLK-06 | Streaming chunk/reset/state, buffering, drift, final partial window, content/availability timing | No candidate-specific timing/state contract verified |
| BLK-07 | Optional caller-supplied-asset adapter boundary, off by default, outside installed v0/shared build/CI | No versioned adapter boundary; package adds no adapter/provider/registration |
| BLK-08 | Default-off decision, target-device resource/deadline evidence, release/public-benchmark approval | No device/deadline/default/release review exists |

## Reproduce

Pinned Python 3.12.16:

```sh
export PYTHONDONTWRITEBYTECODE=1 PYTHONHASHSEED=0
PYENV_VERSION=3.12.16 python3 run.py all
PYENV_VERSION=3.12.16 python3 -m unittest -q test_reference.py
PYENV_VERSION=3.12.16 python3 verify.py
```

## Source pins

| Path | SHA-256 |
| --- | --- |
| `audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `research/voice-enhancement-20261101/agent-segmentation/REPORT.md` | `ce894b6d95bbac3999e71b3a847d4e61ed872e2823262abb7ac15ad1cb6456d2` |
| `research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |

## Boundary pins

| Path | SHA-256 |
| --- | --- |
| `.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `README.md` | `b965bab19a48a82d9c5a67da88b781fa3215f3be4e298607d643445446127a61` |
| `REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |

## Local artifact pins

| Path | SHA-256 |
| --- | --- |
| `LICENSES.md` | `c62e303483c84c6694ddab1b503a4e8e40224b45ed5dedb6a981ebc8bfb67026` |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `contract.json` | `e569c1a1e25e0c8a8385706ac143a673eac62eef416371ba57d56b2e35624b7d` |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `reference.py` | `df142e3761bef8ccb7b6c5162ccb4959fed512d5e3ea7091bebdeccbda6d39f7` |
| `report.json` | `3358c6154fd494faf286af94558e7d8b5a07dfa2a8972d34465a24af8b526367` |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `report.json.sha256` | `34603edd00476a0471b31dfe5b2e28474d3028d8b69ae750db18fa021c4b50f5` |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` |
| `run.py` | `7729131435cb723774ab7cec4ada1d76eefe691c0d9bc0a3ffa031a0927ab33b` |
| `test_reference.py` | `18d8dfbcc42c34b4ac778f4ce5836d9323b9a83556d516fd71a897e564a7bb76` |
| `verify.py` | `e4fd5cee98910dc48d74534f1cc8be123f0105e838fa9cdba7fb41f0c223f3a5` |
