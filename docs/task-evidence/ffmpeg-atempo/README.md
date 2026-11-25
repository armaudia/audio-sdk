<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX&#45;License&#45;Identifier: Apache-2.0 -->
# SDK-FFMPEG-ATEMPO — task-local synthetic rate-change evidence

**Status: `proposal_only_not_qualified`; qualification `incomplete`; decision
`DEFER` before any processor exposure, default, registration or release claim.**

This package is a deterministic, fully synthetic OLA-style rate-change
*reference* at a task-local evidence boundary. It is **not** FFmpeg `atempo`,
not an FFmpeg emulation, not a wrapped binary, not a vendored source, not a
licensed runtime, not an installed SDK provider, and not a listening, device,
or production qualification. No public API/ABI, `CONTRACTS.md`, shared
`CMakeLists.txt`, descriptor default/registry, installed v0 behavior, board,
handoff, ruleset, main branch, or other worktree was changed.

Pinned base: `2bc2a13aa4c5b398933fd9097d09746ce151216e`. Branch:
`swarm/SDK-FFMPEG-ATEMPO`. All files live only under
`docs/task-evidence/ffmpeg-atempo/`.

## Exact scope

- Boundary anchor: audio-sdk public v0 C headers and `CONTRACTS.md` are pinned
  by SHA-256 as provenance only. Installed v0 remains 16 kHz mono `float32`,
  160 samples per call. This package does not add a provider, descriptor,
  config, or runtime hook.
- The local identity is `ffmpeg-atempo-synthetic-ola-reference-v1`. It performs
  deterministic rational rate change over synthetic integer PCM ticks with
  explicit source-sample clocks. It is a proposal-only task-local reference,
  not FFmpeg.
- FFmpeg context is explicit and blocked: local FFmpeg binary/runtime is
  unavailable at authoring time. That unavailability is recorded as blocked
  context, never as a hidden assumption, never as a pass, and never as numeric
  parity. No FFmpeg binary, source, download, package install, or licensed
  runtime is included or invoked.
- `adapter.json` and `provider.json` are proposal-only manifests:
  unregistered, `default_enabled: false`, `processor_exposure: false`,
  `decision: DEFER`. No C boundary, opt-in consumer, or native parity
  crosscheck is included.
- All evidence is synthetic and deterministic. No real corpus, device timing,
  listening test, release claim, or missing-result qualification is made.

## Source pins (SHA-256)

Paths are relative to `/Users/htsakanyan/workspace/audio/audioml`. Tests and
`verify.py` fail closed on missing or changed pins.

| Source | SHA-256 |
| --- | --- |
| `research/voice-enhancement-20261101/candidate_matrix.csv` | `3bcaf35c406f8deeed5560226130579ffe4dbbd60544b59995876e85b589a245` |
| `research/tsm-followup-20261101/README.md` | `01618a85ee4e8741cda07e6fd3c16d5f7f23d1373e1b853bd2903f295d73228f` |
| `cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `REALTIME_COMPONENT_CANDIDATES.md` | `294ee2fbf04ff00e438cded6365312f575be0f0162854fdf46972f670c688f5d` |
| `audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `audio-benchmark-platform/audio-sdk/CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `audio-benchmark-platform/audio-sdk/api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |

Mutable board snapshot (`plan/swarm/TASKS.json`,
`0c443df7655e040679e48f39524af549deb355569050217a7fb05e4352b2ec74` at read
time) is provenance only and never an acceptance gate.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` → `profile_checklist` and verified by `verify.py`:

| Required item | Evidence |
| --- | --- |
| Source/output mapping | Per-segment rational mapping with source/output start/end and frame source intervals. |
| Duration | Exact target output length for every rational schedule; duration error is 0 samples in all scenarios. |
| Pitch preservation | Integer zero-crossing and lag proxies over source-timestamped speech/music windows. Proxies only, not pitch measurement or listening. |
| Transient audibility | Integer sample-jump proxies around source-timestamped transient positions. Proxy only, not audibility. |
| Playback buffering | Synthetic tick model with 160-sample consumer drain, rebuffer stall, occupancy, underrun, and delivery accounting. Not device timing. |
| 1x and rate changes | 1x identity scenarios and rational changes including 5/4, 4/5, 3/2, 3/4, 11/10. |
| Unfamiliar speech, music, silence | Synthetic unfamiliar speech/music labels, silence and filler/pause segments; no real corpus. |
| Rebuffer, drift, final partial window | `rebuffer_step` inserts a synthetic stall; `drift_partial_tail` changes rate over a 1797-sample input with a final partial analysis window. |
| Pause/filler decisions tied to source timestamps | Pause/filler decisions retain source start/end and never delete audio. |
| Speech preservation | Structural coverage/zero-output checks for speech/music segments; 1x exact equality where applicable. Not listening. |
| Chunked-vs-single identity and reset/replay behavior | Four chunk schedules (`single`, `sdk_frames`, `irregular`, `tiny`) produce byte-identical sample and metadata digests. Reset/replay reproduces baseline and stale epoch is rejected. |

Synthetic proxies must never be presented as listening, target-device timing,
FFmpeg parity, or production qualification.

## Method

1. `fixture.py` synthesizes 8 deterministic scenarios from integer waveform
   tables and a 32-bit LCG. Labels such as `speech_unfamiliar` and
   `music_unfamiliar` are synthetic fixture labels only.
2. `reference.py` implements a stateful OLA-style reference with a 640-sample
   analysis window and 160-sample hop. Rate is a rational `num/den` in
   `[0.5, 2.0]` and may change only at 160-sample source boundaries.
3. Output positions are exact rational functions of source-sample timestamps.
   A source frame at `s` maps to `round(sum den_i/num_i over covered intervals)`.
   Output samples are integer averages of overlapping analysis contributions.
4. The session accepts chunked input with exact source continuity checks,
   rejects gaps/overlaps/stale epochs/invalid samples/config, drains partial
   final windows, and supports reset/replay.
5. `scorer.py` computes profile proxies and failure controls. All values are
   deterministic integers or exact derived integers.
6. `run.py --report` generates three reports, requires byte-identical payloads,
   and only then writes `report.json` and `report.json.sha256`.

## Canonical report and digests

`report.json` is canonical JSON (sorted keys, compact separators,
`allow_nan=False`, LF, one trailing newline). `report.json.sha256` contains the
file digest and must match the canonical report digest.

| Name | Digest source |
| --- | --- |
| `report.json` | generated canonical report |
| `report.json.sha256` | same SHA-256 as report file |
| `SOURCES.sha256` | local artifact manifest; does not pin itself |

Local artifact digests are in `SOURCES.sha256`; `contract.json` pins code/data
artifacts used for verification. All comparisons are exact.

## Results (synthetic only)

Eight scenarios cover 1x, faster/slower rates, unfamiliar speech/music labels,
silence/filler/pause, rebuffer stall, rate drift, and final partial input
window. All required rate-profile checklist items are scored as true in the
canonical report. Duration error is 0 samples for all scenarios. Chunked,
irregular, tiny, and single-chunk schedules are byte-identical per scenario.
Reset/replay reproduces baseline; stale epoch is rejected.

These are synthetic structural/proxy results only. They are not listening
quality, naturalness, pitch accuracy, device timing, or FFmpeg parity evidence.

## Failure controls

- **Invalid config/input:** out-of-range/noncanonical/noninteger rates, bad
  schedule alignment, 48 kHz/stereo/320-frame config, negative epoch,
  NaN/Inf/float/out-of-range/empty samples are rejected.
- **Source continuity:** gaps, overlaps, and stale epochs are rejected without
  mutating output.
- **Reset/replay:** replay after reset matches baseline; stale pre-reset epoch
  cannot append.
- **Final partial window:** `drift_partial_tail` has a non-frame-aligned input
  tail and is drained deterministically.
- **No missing-result promotion:** missing, rejected, stale, unrun, or blocked
  results do not qualify. FFmpeg unavailability is explicit blocked context.
- **No deletion:** pause/filler decisions are source-timestamped and no audio
  is removed.

## Licensing and FFmpeg context

- No FFmpeg binary, source, library, wheel, model, or licensed runtime is
  present in this package.
- `check_licensing.py` fails closed if forbidden FFmpeg artifacts or
  install/download instructions appear in task-local files.
- Research pins mention historical FFmpeg/atempo evidence as provenance only;
  this package claims no numeric parity and no rights to distribute FFmpeg.

## Remaining release gates

- Independent review of this proposal-only evidence.
- Licensing review before any real FFmpeg build, wrapper, or vendored artifact.
- Target-device playback pacing, fill/flush, callback deadline, and thermal
  evidence.
- Blinded listening or task-matched human study; synthetic proxies are not
  listening.
- Unfamiliar real speech/music cohort with rights and consent.
- Registered provider, descriptor/config, and installed behavior review before
  any exposure.
- Hosted CI and release evidence for any support claim.

## Reproduction

Python 3 standard library only. From this directory:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 python3 run.py --sources
PYTHONDONTWRITEBYTECODE=1 python3 run.py --crosscheck
PYTHONDONTWRITEBYTECODE=1 python3 verify.py
PYTHONDONTWRITEBYTECODE=1 python3 check_licensing.py
python3 -m json.tool report.json > /dev/null
shasum -a 256 report.json report.json.sha256
git diff --check
git diff --cached --check
```

SDK build/install/ctest from repo root:

```sh
cmake -S . -B build/verify-atempo -DCMAKE_BUILD_TYPE=Release -DCMAKE_INSTALL_LIBDIR=lib
cmake --build build/verify-atempo --parallel 2
ctest --test-dir build/verify-atempo --output-on-failure --timeout 60
```

Plan check (from audio-benchmark-platform context as instructed by task):

```sh
python3 /Users/htsakanyan/workspace/audio/audioml/audio-benchmark-platform/plan/swarm/check.py --task SDK-FFMPEG-ATEMPO
```

REUSE lint:

```sh
python3 -m reuse lint
```
