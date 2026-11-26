<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->

# SDK-SHERPA-ONNX — sherpa-onnx readiness blocker

**Decision `DEFER`; status `incomplete`; evidence `incomplete`; qualification
`not_qualified`; eight release gates blocked.** This directory is a bounded,
deterministic, task-local feasibility record for `sherpa-onnx` (title
"sherpa-onnx", mode `feasibility`, `verification_profile: rate`, area "Rate and
content", disposition `sdk-reference`). It is **not** a sherpa-onnx
implementation, adapter, provider, model registry entry or benchmark. No
upstream checkout, wheel archive, ONNX Runtime binary, model weight, tokenizer,
audio, transcript, timestamp, WER, listening, device timing, benchmark or
release claim is present. **No result here qualifies sherpa-onnx.** No provider,
default, ABI, CONTRACTS.md, registry, shared build or CI workflow is changed.

## Exact external blocker

The pinned census
`cpp-library/pipeline-validation/playback-speed-candidates.md` line 877 records:

> | Content gate (all-in-one) | **sherpa-onnx** | Apache-2.0 | C++ API;
> streaming ASR, VAD, keyword spotting, audio tagging, token timestamps,
> endpointing | Each model has its own licence; verify the card |

The same source records no local build or benchmark of sherpa-onnx and leaves
the planned streaming gate at P1. The pinned
`research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` records
that sherpa-onnx was absent in the checked runtime and that no local ASR
checkpoint or streaming adapter was staged. The pinned inventory row marks it
`considered` / `sdk-reference` / `evidence_status: partial` for the sibling
`whisper-tiny-en-int8-via-sherpa-onnx` entry only.

The census supplies a capability list and an `Apache-2.0` code label. It
supplies **no** immutable revision, source file, license text, notice bundle,
wheel archive, lockfile, offline load trace, model card, per-model license,
commercial/output-use decision, exact streaming geometry, buffering delay,
right context, endpoint policy or matched cohort. The nine Whisper tiny.en
files that happen to exist in a mutable scratch tree are pinned only as
provenance bytes: they carry no license or model card and their `.wav` files
are never read as audio.

The exact blocker is therefore: **no caller-supplied, identity-verified,
rights-cleared sherpa-onnx source, runtime, streaming model and matched cohort,
and no measured 16 kHz mono f32 160-sample token-timestamp result.** Missing
artifacts are not downloaded, reconstructed, mirrored, substituted or inferred
from census prose or from adjacent Whisper/Vosk/Kaldi evidence.

Six open blockers:

| Blocker | Missing artifact and rights requirement |
| --- | --- |
| `BLK-01` | The exact `k2-fsa/sherpa-onnx` source at an immutable 40-hex commit with reviewed Apache-2.0 license text, notice and bundled third-party attribution (`ART-01`). |
| `BLK-02` | Pinned wheel/sdist archives, hashes, lockfile and an isolated offline install for the exact 2.0.1 runtime including `sherpa-onnx-core` (`ART-02`). |
| `BLK-03` | A deterministic clean-room load trace, thread policy and availability/first-output evidence at 16 kHz mono f32 160-sample frames (`ART-03`). |
| `BLK-04` | An exact streaming model with model card, per-model license and commercial/output-use rights; the present offline Whisper tiny.en tree has none (`ART-04`). |
| `BLK-05` | Proof that the chosen model emits source-timestamped tokens at the installed geometry with bounded right context and endpoint/reset behavior; the census says timestamps are model-dependent (`ART-05`). |
| `BLK-06` | A consented, rights-cleared matched cohort with independent references, controls, Rate-profile results, device timing and separate OFF-by-default provider intake with independent exact-head review (`ART-06`). |

**Reopen condition.** A caller supplies the exact source revision and notices,
hash-pinned offline runtime archives and lockfile, an exact streaming model with
card and per-model rights, a proven token-timestamp geometry at the installed
16 kHz mono f32 160-sample boundary, a rights-cleared matched cohort with
independent controls, device timing and failure behavior, a deterministic
reproduced Rate result set, and an opt-in OFF-by-default provider intake with
independent exact-head review. Until then this task stays `DEFER`; a structural
manifest that passes validation advances no gate and claims nothing.

## Task geometry

| Property | Reported value | Verified here |
| --- | --- | --- |
| Task | Rate/content gate: streaming ASR token timestamps / VAD / keyword spotting / tagging | No execution |
| Capabilities (census) | streaming ASR, VAD, keyword spotting, audio tagging, token timestamps, endpointing | Provenance only, not evidence |
| Source revision | not reported | No source checkout |
| Code license (census) | Apache-2.0 | License identity unverified |
| Model license / card | "verify the card" | Absent for present bytes |
| Sample rate / channels / format | not reported | unverified |
| Frame / native hop / buffering delay | not reported | unverified |
| Right context / endpoint policy / decoding state | not reported | unverified |
| Token timestamps | model-dependent per census | Not verified |
| SDK v0 installed geometry | 16 kHz, mono, f32, 160 samples/frame | unchanged; no sherpa-onnx mapping |

The public v0 mono path is preserved. No descriptor, provider, registry,
default, public API/ABI, shared CMake or CI change is made.

## What this package verifies

1. **Absence evidence.** A fixed list of 15 workspace, SDK-worktree and
   home-cache probes is checked without a recursive walk. All are absent. The
   report builder and verifier fail if any later appears, so a stale absence
   claim cannot ship.
2. **Provenance pins.** Every census/plan/runtime-metadata input and every one
   of the nine present Whisper tiny.en files is pinned by SHA-256. The present
   model tree is re-digested (9 files, 256603197 bytes); no file is opened as
   audio and no output is produced.
3. **Stable pins and digests.** The README digest tables are validated against
   live bytes, and `SOURCES.sha256` covers all task-local files except itself.
4. **Stable board identity.** Only `id`, `title`, `component`, `mode`,
   `repository`, `depends_on` and `evidence` are projected and gated. The
   mutable `plan/swarm/TASKS.json` bytes are never hashed; status, owner,
   claim, review, handoff, priority and history never enter canonical bytes.
5. **Rate-profile application.** The pinned `VERIFICATION.md` Rate row phrases
   are checked; all eight Rate requirements and all eight release gates remain
   blocked. No missing result is promoted.
6. **Fail-closed caller-asset validation.** A task-local manifest schema
   requires exact source, runtime, asset, model, control and rights fields.
   Unknown or missing fields, duplicate JSON keys, nonfinite values, floats,
   unsafe paths, wrong interpreter, stereo geometry, wrong rate/format/frame,
   unproven token timestamps, batch-only mode, wall-time events, absent rights
   and embedded assets are all rejected. One synthetic schema control is
   accepted to prove the validator is not blanket-rejecting; it is marked
   `qualifies=false` and is not evidence. A separate integer-only final-window
   control confirms padding conservation without any audio.
7. **Scope enforcement.** The verifier resolves the newest merge-base against
   `origin/main` and `main`, fails closed with `scope_base_unavailable` when no
   base exists, and reports any branch-added path outside
   `docs/task-evidence/sherpa-onnx/` as `base_out_of_scope_change`. Regression
   tests cover sibling merges, an out-of-scope branch edit and a missing base
   ref.
8. **Deterministic regeneration.** `run.py` writes canonical bytes three times
   and requires byte-identical output; `verify.py` replays three cold-start
   regenerations in a temporary directory and compares every byte.

## Rate profile application

| Requirement | Status | Evidence |
| --- | --- | --- |
| Source/output mapping and duration | blocked | No sherpa-onnx output or timing record. |
| Pitch and transient audibility | blocked | No control, output or listening result. |
| Playback buffering and drift | blocked | No runtime, buffering or drift evidence. |
| Identity 1× control | blocked | No synthetic or real 1× result. |
| Rate changes | blocked | No rate-change result. |
| Unfamiliar speech, music and silence | blocked | No cohort or stratum. |
| Rebuffer and final partial window | blocked | Integer-only padding control is not evidence. |
| Pause/filler tied to source timestamps | blocked | Token timestamps are unverified and model-dependent. |

## Matched-evidence boundary

`whisper-tiny-en-int8-via-sherpa-onnx`, `whisper-tiny-en-mfa`,
`asr-word-timestamps` and `vosk-small-en-us-0-15-playback-gate` are separate
components. None of their fixtures, weights, scores, timings, state models or
rights records are inherited. The nine pinned Whisper tiny.en bytes are the
same tree already pinned by `asr-word-timestamps`, but that pin establishes
identity only and grants no rights or qualification here. No snippet of census
prose is treated as a result.

## Reproduction

The canonical bytes were generated with CPython `3.12.16` and
`PYTHONDONTWRITEBYTECODE=1`. From this directory:

```
PYTHONDONTWRITEBYTECODE=1 python3.12 run.py all
PYTHONDONTWRITEBYTECODE=1 python3.12 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3.12 verify.py
```

`run.py` regenerates `contract.json`, `report.json`, the report sidecar, the
README digest tables and `SOURCES.sha256` three times and requires
byte-identical output. `verify.py` is read-only in the worktree and writes only
to a temporary directory. Repository checks are
`python scripts/ci.py` (installed native/C++/Python wheel path),
`python3 -m reuse lint` and `git diff --check`. No sherpa-onnx runtime is
imported at any step.

## Source pins

<!-- digest-table: source -->
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/INVENTORY.md` | `5154a8205516f145a719efc6f1598811f29c9df674b696ba25b78afa7af66130` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx-2.0.1.dist-info/METADATA` | `7f0a256489f0705f53f93ec9e85381ba05d7993625198e73afefc506a38cd97d` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx-2.0.1.dist-info/RECORD` | `4c2fda5d01068e258a034b42c65f7cb1b5c68c894c7e0d7d5d238772abbc6479` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx-2.0.1.dist-info/WHEEL` | `632a756fb02f4b7e2e52739240510251e3a147bd72a1e0f3a139f8395c193af8` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx-2.0.1.dist-info/licenses/LICENSE` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx/__init__.py` | `f99e43cc249dbfef58acaa02348892984e4c7dfa07923d9144bec5b51639d8ef` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx/online_recognizer.py` | `a80620a5eb35e06a190584c2c643e5210bff672410283e5a8f106655c1519c9e` |
| `source:cpp-library/pipeline-validation/playback-speed/.venv/lib/python3.11/site-packages/sherpa_onnx_core-2.0.1.dist-info/METADATA` | `f1af234dcfeca76f7ab4e16bdc903311e76069419b8b67c1806a7bf149d8945d` |
| `source:cpp-library/pipeline-validation/playback-speed/README.md` | `a7bde2c76ba2deaf0920b14d75b5d1bf72861ed3b1d6d735bfe0bbe83256635f` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/test_wavs/0.wav` | `6bc58a4efdf20daac252b6b1502632601a71efe0308f6757dc1eda34891a7e4f` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/test_wavs/1.wav` | `5143a6ba93c4b274e2c4ac22deb75c2c48936c853f0519add1de828b6c79cc5a` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/test_wavs/8k.wav` | `f6f3c8b33e2534cdc154fe773ad2750f1f6a2ca5096179cdf037ae782456613e` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/test_wavs/trans.txt` | `b9ac44e7b794abb1a2d5faf0005e98a665971e7ac2ed15435832cc34edaa9100` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-decoder.int8.onnx` | `06c0e6ff6348d427e51839219d1c886c18cfdf411e629e33f5e1679bff9c1527` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-decoder.onnx` | `54d5a5fd2a757175aeb70a837a8404fc9c31b659610724694f5a0e2c51715f94` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-encoder.int8.onnx` | `0ce578b827c94a961aacb8fa14b02f096504b337e5c94be37c36238cbe3e8bc6` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-encoder.onnx` | `dc7de696432d97a3d64387800b230ac69d18e5e4efea0eec0613209dd8b7b0c9` |
| `source:cpp-library/pipeline-validation/playback-speed/models/sherpa-onnx-whisper-tiny.en/tiny.en-tokens.txt` | `306cd27f03c1a714eca7108e03d66b7dc042abe8c258b44c199a7ed9838dd930` |
| `source:research/voice-enhancement-20261101/agent-vad-asr-trials/REPORT.md` | `5801684f5e36263a6449abccfea86d2d33141d98c5eb71aafd377ace184e3a8f` |
<!-- digest-table: end -->

## Boundary pins

<!-- digest-table: boundary -->
| `sdk:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `sdk:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `sdk:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `sdk:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `sdk:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `sdk:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `sdk:bindings/python/audio_sdk/__init__.py` | `3b7d11f0518af444c4ed7b96401cef4016e6af8a707685628d263a31f46c3864` |
| `sdk:docs/provider-intake.md` | `e32610ecf0f3f611269ddebd009ff81ca09cc3b92206fe93c9a149b9960463b5` |
| `sdk:docs/task-evidence/asr-word-timestamps/README.md` | `30915db04b0229d03729b8dd03bac8e0eb88ad285781069de1607ff2c4559de4` |
| `sdk:docs/task-evidence/asr-word-timestamps/report.json` | `318bec24c9d388fa122e80974cfc6772b144f7f651e87d5e88ac0677975d437e` |
| `sdk:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/README.md` | `1ccece1085e1d6e821891feffb0c19fc494227bfd5e8a656657ffd7081cf959c` |
| `sdk:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json` | `57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2` |
| `sdk:docs/task-evidence/whisper-tiny-en-mfa/README.md` | `7c24422f782bf934d22e2a752e2be2ead2d184cfd8728452c7f7a5dd68f25c7f` |
| `sdk:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Task-local artifact digests

<!-- DIGEST_TABLE_ARTIFACTS_START -->
| Path | SHA-256 | Bytes |
| --- | --- | ---: |
| `LICENSES.md` | `2c8ec9fc043a2eddc6af2b56ae1ff61ce6965c2234cc3d25618b873ec20e88ff` | 2747 |
| `SOURCES.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `contract.json` | `155667966ec39799bfcaeac46bd154332ec089dad93d85dc5cd8e7477e64e4a5` | 67615 |
| `contract.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `reference.py` | `3cbbcf40de27aadc2d45d73e420b35a69086480b941e37eafaf47eaea55b93bb` | 59835 |
| `report.json` | `6930e23ae120ff01cddd0a57aa495da7b1af0631a34c458162067a42abf93c52` | 68625 |
| `report.json.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `report.json.sha256` | `7c594439f5f8a526e18b5cc1a451add9c8451cff13bc4074be3821365871c7d9` | 78 |
| `report.json.sha256.license` | `0cee6dbd32d491e605ec18007dec80715aeff3e7a7d90e36361b0261cb42bf47` | 85 |
| `run.py` | `12118a5c07cff6a5b1446c2a415cd1275e103cee1cca4f6f03e46b5a4078bf05` | 4881 |
| `test_reference.py` | `ba8b6708715baf5b88273172b2816439cdffb1a83e9a2f60885b17277d935e4e` | 20414 |
| `verify.py` | `89da081307df73b23998e34006988e59880d6d5f6392c9f3324764fdb5a518bc` | 25596 |
<!-- DIGEST_TABLE_ARTIFACTS_END -->

`SOURCES.sha256` also pins `README.md`; a file cannot pin its own bytes, which
is why `SOURCES.sha256` is absent from the artifact table.
