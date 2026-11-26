<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-AUDIOTRACK-SETPLAYBACKPARAMS-PLAYBACKPARAMS — platform-rate blocker

Task-local, **proposal-only**, **incomplete** and **not qualified** evidence for
**`AudioTrack.setPlaybackParams(PlaybackParams)`**
(`component_id=audiotrack-setplaybackparams-playbackparams`). The structured
inventory assigns the **Rate** acceptance profile
(`verification_profile: rate`, `plan/INVENTORY.json`), defined in
`plan/swarm/VERIFICATION.md`. Machine-readable decision: **`DEFER`**;
`status=proposal_only_incomplete_not_qualified`; `completeness=incomplete`;
`qualification.status=not_qualified`; `qualifies=false`. No result qualifies.

This package does **not** import, load, link, execute, emulate, copy, vendor or
download the Android platform `AudioTrack` / `PlaybackParams` implementation,
an AOSP tree, a framework jar, an `android.jar` SDK stub, a system image, a
device or emulator, a Gradle/Java build, a real speech/music corpus or a
listening panel. It does not process or play audio, run a platform path, listen,
measure a device, time a callback, run a benchmark or make a release claim. It
pins the research note that names the candidate, proves that the exact
implementation, stub, runtime, rights, corpus and measurement evidence are
absent, reproduces only a deterministic arithmetic rate control, and records
the exact deferral condition. Only
`docs/task-evidence/audiotrack-setplaybackparams-playbackparams/` is written; no
provider, descriptor, registry, default, installed-v0, ABI, shared-build, CI,
board or handoff file changes.

## Exact blocker

The pinned note records the candidate only as a platform API row:

> **Android — `AudioTrack.setPlaybackParams(PlaybackParams)`** · OS platform ·
> commercial use yes · "Speed/pitch on the platform audio path; API 23+."
> (`cpp-library/pipeline-validation/playback-speed-candidates.md`, line 80)

The same note names Media3 `SonicAudioProcessor` as the Apache-2.0 Java port of
Sonic and as the readable Android alternative, while
`AudioTrack.setPlaybackParams` is the platform-level path. Neither the platform
implementation nor Media3 is present locally. The note is provenance, not an
implementation, stub, runtime, device measurement or licence decision.

| Required artifact | Recorded local state |
| --- | --- |
| Exact platform `AudioTrack.setPlaybackParams` implementation/runtime | No AOSP checkout, framework jar, revision or full SHA-256 |
| Matching Android SDK `android.jar` stub and API level | No SDK installation, stub, build fingerprint, `adb` or `sdkmanager` |
| Licensed device or emulator runtime image | No system image, emulator, device, audio HAL or timing run |
| Reviewed platform/SDK terms and output rights | No licence text or signed rights decision |
| Declared speed/pitch ranges, defaults, fallback modes, buffering, delay | Not established by the pinned note; no runtime probe |
| Rights-cleared speech/music/silence corpus | No corpus, consent or manifest |
| Measured rate, duration, pitch, transient, buffer, rebuffer, device timing | No runtime or measurement harness |
| Listening/speech-preservation protocol and release review | No protocol, panel, adapter, registration or approval |

Path absence is not a runtime, reproducibility, ABI or quality result. Every
release gate remains `blocked`.

## Scope and invariants

- Work is confined to
  `docs/task-evidence/audiotrack-setplaybackparams-playbackparams/`. Shared
  CMake, contracts, public headers, descriptor registry, defaults, installed v0
  behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider is
  registered, exposed or default-enabled. No adapter, readiness file or
  registry entry is added.
- The reference is deterministic, platform-free and standard-library only. It
  is default OFF, unregistered and not a provider.
- No Android SDK, AOSP source, platform binary, runtime image, real corpus,
  listening panel, network download, target-device timing or release
  qualification is used. Every control is integer or exact rational arithmetic.
- Missing, invalid, nonfinite, out-of-range, candidate-claim,
  stub-equals-implementation and file-mismatch cases fail closed. No missing
  result may qualify the candidate.
- The synthetic control, blocked platform measurements and listening evidence
  are separate classes. None is relabelled, pooled or promoted.
- Source-reported claims, the declared boundary and local synthetic controls are
  reported separately and are never pooled.

## Candidate and declared boundary (proposal only)

`report.json` → `candidate_record` and `declared_contract` record only what the
pinned note states or what the local control declares.

| Field | Declared value | Status |
| --- | --- | --- |
| Candidate | `AudioTrack.setPlaybackParams(PlaybackParams)` | Source-reported |
| Family | Android platform audio path | Source-reported |
| Minimum API level | 23 | Source-reported |
| Platform speed range | Not established | Blocked |
| Platform pitch range/default | Not established | Blocked |
| Platform fallback behaviour | Not established | Blocked |
| Declared local speed range | `3/4` to `3/2` | Declared policy, not measured |
| Declared local pitch | `1/1` | Declared policy, not measured |
| Declared fallback modes | `default`, `mute` | Declared request shape, not verified |
| Declared API range | 23–36 | Declared request shape, not verified |
| Host grid | 16 kHz, mono, float32, 160 samples | Installed v0, unchanged |
| Position mapping | `output_position = floor(source_position / speed)` | Declared arithmetic identity |
| Buffering, content delay, reset, drain, final window | Not established | Blocked |

The local speed clamp, pitch value, fallback modes and API range are **not**
Android behaviour, platform defaults or measurements.

## Synthetic rate arithmetic control

`reference.py` accepts a strict `PlaybackParams`-shaped request with exact
integer speed/pitch, API level, declared fallback mode and an explicit
`is_candidate_result=false` marker. It then applies the declared integer
mapping to a 16,000-sample fixture (1 s at 16 kHz), which is not speech, not a
corpus and not audio.

| Speed | Source samples | Output samples | Duration error (samples) |
| ---: | ---: | ---: | ---: |
| `1` | 16,000 | 16,000 | `0` |
| `3/4` | 16,000 | 21,333 | `-1/3` |
| `5/4` | 16,000 | 12,800 | `0` |
| `3/2` | 16,000 | 10,666 | `-2/3` |

Every output boundary is an integer and each rate's 160-frame chunk-output sum
equals the closed-form total. The identity row is an exact `1×` passthrough.
The final partial window maps 165 source frames at `5/4` in two chunks:
160 → 128 and 5 → 4, for 132 output frames. The one-hour check maps
57,600,000 source frames at `5/4` to 46,080,000 output frames with zero exact
error and a matching 360,000-chunk sum.

The control is labelled `is_synthetic_control=true`,
`is_android_audiotrack=false` and `is_candidate_result=false`. It is **not** an
Android output, a platform rate result or a listening result. It only exercises
the arithmetic that a future qualified runtime control must satisfy.

## Blocked measurement classes

| Evidence class | Status | Value |
| --- | --- | --- |
| Pitch error | `blocked` | `pitch_error_cents=null` |
| Transient audibility | `blocked` | `transient_audibility=null` |
| Playback buffer fill / rebuffer | `blocked` | `fill_ms=null`, `rebuffer_count=null` |
| Device output timing | `blocked` | `output_latency_ms=null`, `callback_jitter_ms=null` |
| Speech preservation | `blocked` | `preservation_metric=null` |
| Listening / comprehension | `blocked` | `protocol_id=null`, `preference=null`, `comprehension=null` |
| Separation | Enforced | `device_timing_is_listening=false`, `pooled_metric=null` |

A device timing run is never relabelled as listening, and an arithmetic control
is never relabelled as a platform result.

## Caller-supplied qualified Android bundle (shape and hash only)

`reference.parse_manifest()` validates a strict 21-field bundle for a
caller-owned qualified artifact: exact key set, artifact/platform/API identity,
ASCII build fingerprint, absolute POSIX paths without traversal or duplication,
full SHA-256 for the SDK stub, platform implementation, `AudioTrack`
implementation, runtime image, licence, rights approval and measurement
manifest, accepted terms, a fixed caller attestation, and an explicit
stub-is-not-implementation check. `reference.verify_manifest_files()` hashes the
caller-owned bytes only. It **never parses, imports, links or executes** the
stub, framework jar, source, runtime image or measurement manifest. Even a fully
hash-matched caller bundle reports `official_identity=false` until platform and
rightsholder review exists.

`report.json` → `manifest_controls` records one accepted shape-only control and
seventeen explicit rejections. All controls have `qualifies=false`.

## Failure controls (exact failures recorded as failures)

- **Request:** 26 adverse vectors are rejected: NaN/infinity/boolean/string
  speed, zero and negative denominator, negative numerator, below-floor and
  above-ceiling speed, non-unity pitch, zero/negative pitch denominator,
  nonfinite pitch, boolean/float API level, API below 23 and above the declared
  range, unsupported fallback mode, candidate claim in boolean and string form,
  wrong schema, empty request ID, missing field, extra field, non-object and
  empty request.
- **Mapping:** 8 adverse vectors are rejected: nonfinite/boolean/zero/below-floor
  /above-ceiling speed, boolean source frames, negative source frames and
  oversized source frames.
- **Manifest:** 17 adverse documents are rejected: missing and extra fields,
  wrong platform, boolean/low API level, relative path, parent traversal,
  duplicate paths, uppercase hash, wrong hash length, stub equals platform
  implementation, rejected terms, wrong attestation, empty artifact ID, empty
  and `not_established` listening protocol, and a non-ASCII build fingerprint.
  Missing files and mismatched bytes are rejected by the file checker.
- **Qualification:** all 14 missing-result rows are `blocked` with
  `value=null`; all 9 qualification slots are null; all eight gates are
  `blocked`.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Rate profile application

`plan/swarm/VERIFICATION.md` Rate row is applied item by item in
`report.json` → `acceptance_profile`; every item is `qualifies=false`.

| Required item | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic_control_only | Exact floor mapping on the integer fixture |
| Duration | synthetic_control_only | Exact integer/rational duration error |
| Unity 1× | synthetic_control_only | Exact identity mapping |
| Final partial window | synthetic_control_only | 165-frame source window in two chunks |
| Drift over a long run | synthetic_control_only | One-hour chunk-sum equals the closed-form total |
| Adverse / missing / nonfinite | synthetic_control_only | 26 request, 8 mapping and 17 manifest rejections |
| Pitch | blocked | No platform runtime or pitch measurement |
| Transient audibility | blocked | No actuator or listening asset |
| Playback buffering | blocked | No playout FIFO or fill run |
| Rebuffer | blocked | No buffer-occupancy injection |
| Rate changes (step/ramp) | blocked | No platform runtime trace |
| Unfamiliar speech | blocked | No real speech or held-out corpus |
| Music | blocked | No music corpus or platform run |
| Silence | blocked | No audio path or platform silence run |
| Source-timestamp-tied decisions | blocked | No pause/filler policy on a platform runtime |
| Speech preservation | blocked | No candidate output or metric |
| Device timing | blocked | No device/emulator, audio HAL or paced run |
| Release and distribution terms | blocked | No platform, SDK or output-use approval |

## Eight blocked release gates

1. `exact_android_platform_runtime_and_stub_identity`
2. `api_level_playbackparams_semantics_and_geometry`
3. `license_and_output_rights`
4. `android_sdk_java_and_build_toolchain_lock`
5. `rights_cleared_speech_music_corpus_and_listening`
6. `measured_source_output_duration_pitch_transient`
7. `measured_buffering_rebuffer_drift_and_device_timing`
8. `opt_in_adapter_intake_and_release_review`

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`.

## Exact missing artifacts and rights

| Missing artifact | Rights requirement |
| --- | --- |
| Exact platform `AudioTrack.setPlaybackParams` implementation/runtime | AOSP/platform and device-image terms, reproduction grant and output-use decision |
| Matching `android.jar` stub and exact build fingerprint | Android SDK licence acceptance for the exact package revision |
| Licensed device or emulator system image with an audio path | Device/emulator runtime terms, hardware access and timing/publication approval |
| Reviewed platform/SDK licence text and rights decision | Platform and SDK rightsholder terms, derivative-output and commercial-use approval |
| Declared speed/pitch ranges, defaults, fallback modes, buffering and geometry | Documentation/runtime terms permitting reproduction |
| Rights-cleared speech/music/silence corpus | Corpus, participant, annotation, redistribution and evaluation rights |
| Measured rate/duration/pitch/transient/buffer/rebuffer/device timing | Approval to run and publish measurements on the named runtime |
| Listening protocol, adapter intake and release review | Panel consent, participant-data terms, reviewer and release-authority approval |

No download, fabrication or substitution was attempted. A research-note row is
not an implementation, an SDK stub, a runtime or a measurement.

## Files

| Path | Purpose |
| --- | --- |
| `README.md` | This file: scope, pins, commands, controls, gates. |
| `reference.py` | Strict request/mapping/manifest controls, declared boundary and report/contract builders. |
| `run.py` | Regenerates the report three times, the contract and the manifest. |
| `report.json` | Canonical machine-readable rate report; strict JSON, sorted keys, LF. |
| `report.json.sha256` | Digest of the committed `report.json`. |
| `contract.json` | Task contract: profile, boundary, pins, blockers, gates, qualification. |
| `test_reference.py` | Deterministic unittest checks, no skips, no network. |
| `verify.py` | Read-only pin, strict-JSON, digest, README-table, reproduction, licensing and scope verifier. |
| `SOURCES.sha256` | SHA-256 manifest for every local artifact and this README. |
| `*.license` | REUSE sidecars for JSON and digest artifacts. |

## Source pins (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked by `verify.py` and the test suite. Only provenance
files that exist are pinned; no absent candidate artifact is given a fabricated
hash. The mutable full `plan/swarm/TASKS.json` is not pinned or hashed.

<!-- digest-table: source -->
| Key | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
<!-- digest-table: end -->

## Boundary pins (SHA-256)

`boundary:` paths are relative to this SDK worktree. All are unchanged and
machine-checked.

<!-- digest-table: boundary -->
| Key | SHA-256 |
| --- | --- |
| `boundary:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `boundary:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |
<!-- digest-table: end -->

## Merged sibling evidence pins (SHA-256)

The sibling packages are separate evidence. They are pinned as prior local
artifacts, not imported, pooled or reinterpreted. `sonic`, the AIx Speed planner
and the Vosk playback gate are rate/playback-adjacent blockers or controls; the
Apple/browser probe and pitch-period PLC package cover separate runtime and
actuator questions. None is Android `AudioTrack.setPlaybackParams`. No merged
Android-audio evidence package exists at this base commit; the Media3
`SonicAudioProcessor` task is still queued and is not pinned as evidence.

<!-- digest-table: sibling -->
| Key | SHA-256 |
| --- | --- |
| `sibling:docs/task-evidence/sonic/contract.json` | `dea2168b7ad7466a848d1fdfbee4047f84062c31d265c3cde0686cee8beaccf1` |
| `sibling:docs/task-evidence/sonic/report.json` | `2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2` |
| `sibling:docs/task-evidence/aix-speed-asr-guided-planner/contract.json` | `c920cf8290eae892f2d282801b7db18bbaa992e8c08c815b1e902aaf7f359fee` |
| `sibling:docs/task-evidence/aix-speed-asr-guided-planner/report.json` | `a71ce94ad0b701c9d302edf1c74338c7d1586d573a7295510fd3584b26110873` |
| `sibling:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/contract.json` | `ee23e6cc21f9f3293a48dab7008a4c41f129074cafa3eb6b273f2f3ef413d694` |
| `sibling:docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json` | `57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2` |
| `sibling:docs/task-evidence/apple-and-browser-runtime-qualification/probe.py` | `027ef12581fd75e8ee441c29a40bf15300c853becfe165312a792ff134cfe2d7` |
| `sibling:docs/task-evidence/pitch-period-repeat-plc/report.json` | `114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445` |
<!-- digest-table: end -->

## Artifact digests (SHA-256)

`report.json` is canonical JSON (sorted keys, indent 2, `allow_nan=False`, LF,
one trailing newline). The canonical digest of the committed bytes is stored in
[`report.json.sha256`](report.json.sha256). `SOURCES.sha256` pins every artifact
and this README; it does not pin itself. No external artifact is pinned: the
implementation, SDK stub, runtime image, licence, corpus and reference output
are not established, and every required-artifact row records `present=false`.

## Reproduce

Run from this directory with a pinned interpreter:

```sh
WT=/Users/htsakanyan/workspace/audio/audioml/worktrees/audio-sdk/SDK-AUDIOTRACK-SETPLAYBACKPARAMS-PLAYBACKPARAMS
TASK=$WT/docs/task-evidence/audiotrack-setplaybackparams-playbackparams
PY=/Users/htsakanyan/.pyenv/versions/3.12.16/bin/python
cd "$TASK"
PYTHONDONTWRITEBYTECODE=1 $PY -m unittest -v test_reference.py
PYTHONDONTWRITEBYTECODE=1 $PY run.py --report
PYTHONDONTWRITEBYTECODE=1 $PY run.py --contract
PYTHONDONTWRITEBYTECODE=1 $PY run.py --sources
PYTHONDONTWRITEBYTECODE=1 $PY run.py --inspect
PYTHONDONTWRITEBYTECODE=1 $PY verify.py
git -C "$WT" diff --check
```

`run.py --report` builds the report three times in one process and refuses to
write unless all payloads are byte-identical. `verify.py` separately launches
three cold starts for each command and compares the exact bytes, and checks the
declared boundary, null candidate slots, blocked measurement separation,
controls, eight blocked gates, SPDX annotations, dependency hygiene and
task-local scope containment.

## Non-claims and boundary

`registered=false`, `enabled_by_default=false`, `default_selected=false`,
`public_api_abi_change=false`, `provider_registration=false`,
`descriptor_registry_change=false`, `installed_v0_behavior_change=false`,
`shared_build_or_ci_change=false`, `processor_exposure=false`,
`adapter_json_added=false`, `readiness_json_added=false`,
`asset_bundled=false`, `android_sdk_present=false`,
`android_stub_present=false`, `runtime_image_present=false`,
`device_or_emulator_present=false`, `audiotrack_impl_present=false`,
`platform_runtime_invoked=false`, `device_timing=false`,
`listening_performed=false`, `sdk_data_dir_added=false`.

Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. The board is
referenced by stable linked-row identity only
(`tasks[id=SDK-AUDIOTRACK-SETPLAYBACKPARAMS-PLAYBACKPARAMS]`, stable-field
projection); the mutable full `plan/swarm/TASKS.json` is never hashed by or
pinned to this package. No provider, descriptor, registry, installed default,
public ABI, shared build or CI is changed.

## Separation from sibling evidence

Sonic, AIx Speed, Vosk, Apple/browser runtime and pitch-period PLC packages are
**separate evidence**. They use different candidates, fixtures and
dispositions. This package does not pool, import, reuse or reinterpret their
outputs, metrics or adapters. The pinned playback-speed note is a local
research/pre-screen note covering D1/D2 planners and Bungee/Signalsmith/Sonic
actuators; it is **not** Android `AudioTrack` and has no Android or listening
result. Its numbers are provenance only and are not remeasured here.

## Reopen condition

Supply (a) the exact AOSP/framework `AudioTrack.setPlaybackParams`
implementation or an authorized runtime image with a 40-hex revision and full
SHA-256; (b) a matching `android.jar` stub, exact API level and build
fingerprint; (c) a licensed device or emulator runtime image with an audio
output path; (d) reviewed platform/SDK terms and a signed output-use decision;
(e) the official speed/pitch ranges, defaults, fallback modes, buffering,
content delay and geometry reproduced for that exact build; (f) a rights-cleared
speech/music/silence corpus; (g) measured mapping, duration, pitch, transient,
buffer, rebuffer, drift and target-device timing; and (h) an authorized
listening/speech-preservation result, independent exact-head review and an
OFF-by-default opt-in adapter intake. Until then the candidate stays **DEFER**,
**incomplete** and **not qualified**.

## License

All files here are first-party `Apache-2.0`, copyright 2026 Tsakanyan Hovhannes.
Python and Markdown files carry file-level SPDX tags; JSON and digest files are
covered by adjacent `.license` sidecars and the repository `REUSE.toml`
annotation for `docs/**`.
