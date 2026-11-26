<!-- SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes -->
<!-- SPDX-License-Identifier: Apache-2.0 -->
# SDK-MEDIA3-SONICAUDIOPROCESSOR-JAVA-PORT-OF-SONIC — feasibility blocker package

**Status: `proposal_only_incomplete_not_qualified`; evidence `incomplete`;
decision `DEFER`; qualification `not_qualified`; eight release gates blocked.**
This directory contains bounded, deterministic, task-local feasibility evidence
for the Media3 SonicAudioProcessor row. It is **not** a Media3 implementation
and **no candidate result** is present. No Media3/AndroidX source checkout,
`SonicAudioProcessor.java`, `Sonic.java`, AAR/JAR, Java/Android build, runtime,
device, corpus, listening result, benchmark or release claim exists. **No result
here qualifies the candidate.**

The structured inventory marks
`media3-sonicaudioprocessor-java-port-of-sonic` as `evidence_status=considered`
with the **Rate** acceptance profile and disposition `sdk-reference`
(`plan/INVENTORY.json`). The task mode is `feasibility`. Its deliverable asks
the owner to verify runnable source, exact assets, permitted scope, task
geometry and matched evidence before implementing or wrapping a minimal
reference at the relevant public adapter boundary and shipping it as optional.
Feasibility fails at every prerequisite, so the documented decision is
**DEFER** before `opt_in_provider_intake`.

## Exact external blocker

The pinned research record names the candidate only as a platform/library row:

> `cpp-library/pipeline-validation/playback-speed-candidates.md` line 79 —
> **Android | Media3 `SonicAudioProcessor` (Java port of Sonic) | Apache-2.0 |
> Yes | Apache-2.0 source; useful as a reference and as the platform-native
> path.**

Section 4.2 adds only a documentation link and a short description:

> **What it is:** Apache-2.0 Java implementation of Sonic, used by ExoPlayer's
> audio pipeline; supports speed and pitch.
>
> **Cons:** Java/Kotlin, not our C++ library; Android-only.
> `AudioTrack.setPlaybackParams` is the platform-level alternative.

That is provenance, not an implementation, revision, artifact, runtime,
licence decision or measurement. No Media3, AndroidX or ExoPlayer checkout is
present. The exact licensed Java source and the exact runtime are absent, so
there is nothing exact to reproduce and a caller-supplied-asset reference or
opt-in adapter cannot be built or verified.

| Missing artifact | Exact requirement |
| --- | --- |
| Exact Media3 Java source | `SonicAudioProcessor.java` and `Sonic.java` from an immutable 40-hex Media3 revision, with a per-file SHA-256 manifest and the reviewed upstream LICENSE/notice bundle |
| Exact Media3 artifact | The AAR/JAR built from that revision, a release or build identity, byte count, SHA-256 and a declared sample format, speed/pitch range, buffering, content-delay, state and drain contract |
| Java/Android runtime | A locked JDK, Gradle wrapper, Android Gradle Plugin, Android SDK, dependency lock, target platform and offline load path with recorded digests |
| Rights and scope | Reviewed Media3/AndroidX/Android source, artifact and platform terms that settle evaluation, redistribution, customer deployment, public playback and generated-output use |
| Rate corpus | A frozen, rights-cleared speech, music and silence cohort with unfamiliar-speech, rate-step, drift, rebuffer and final-window cases |
| Matched task evidence | Exact-runtime source/output mapping, duration, pitch, transient audibility, buffering, rebuffer and device-timing measurements on the named runtime |
| Listening and release | An authorized listening or speech-preservation protocol, an OFF-by-default adapter intake, independent review and explicit release approval |

The machine-readable record is `report.json` → `candidate_record`,
`declared_contract`, `absence_audit`, `native_sonic_c_provenance`,
`artifact_assessment`, `required_artifacts`, `exact_blockers` and
`release_gates`. `contract.json` carries the same disposition, absence audit,
pins and all eight blocked release gates.

## Feasibility conclusion

The decision is **DEFER** because the exact candidate source, artifact,
runtime, semantics, rights and matched evidence are all absent. This is not a
negative quality result; it is an evidence and feasibility blocker. The
pinned note is a research row, not a source tree, binary, runtime or
measurement.

The present `cpp-library/third_party/sonic` directory is the **Apache-2.0 Sonic
C original by Bill Cox**, pinned read-only for provenance. It is a different
implementation from Media3's Java port, has no Media3 Android integration or
parity result, and is not admitted for candidate qualification. It is never
used for parity, quality, timing or qualification.

## What this package verifies

1. **Absence evidence.** Fixed, non-recursive workspace and home-cache probes
   are checked; no recursive walk is performed. No Media3 source, AAR/JAR,
   Gradle/Maven cache, runtime, device or emulator is present. `reference.py`
   refuses to build the report if any probe later appears, so a stale
   "absent" claim cannot be shipped.
2. **Native Sonic C is pinned and not admitted.** `sonic.c`, `sonic.h` and
   `LICENSE` are pinned by SHA-256 and verified unchanged. The record is
   explicit that this is not the Media3 Java port and has
   `qualification_effect=none`.
3. **Stable pins.** The research note, planning records, rights register,
   native Sonic C files and SDK boundary files are pinned by SHA-256, plus
   merged sibling Sonic, Signalsmith Stretch, AudioTrack, Web Audio and
   pitch-repeat evidence packages as adjacent boundary references. These are
   read-only provenance inputs, not Media3 evidence.
4. **Stable board identity.** Only the linked row's `id`, `title`,
   `repository`, `mode`, `component`, `depends_on`, `write_scope`,
   `deliverable`, `acceptance`, `evidence`, `dispatch_priority`, claim
   `base_commit` and claim `branch` are projected and compared. The mutable
   full `plan/swarm/TASKS.json` is **never hashed**; status, owner, claim,
   review, handoff, blocked reason, timestamps and history never enter
   canonical bytes and never gate this package.
5. **Fail-closed admission.** The caller-supplied Media3 bundle requires an
   artifact ID, a 40-hex source revision, distinct paths/digests for
   `SonicAudioProcessor.java` and `Sonic.java`, a Media3 LICENSE, a build
   toolchain lock, a runtime manifest, a rights approval and a measurement
   manifest. Missing, unpinned, duplicate-source or non-admitted candidates
   are rejected before any processing. One synthetic shape-only control is
   accepted to prove the validator is not blanket-rejecting; it is
   `official_identity=false`, is not a real Media3 revision and has
   `qualification_effect=none`.
6. **Adverse, missing, invalid and nonfinite rejection.** Wrong sample rate,
   channels, frame size, speed, pitch, schema, request ID and candidate claim
   are rejected; empty, oversized, string, boolean, negative, out-of-range
   and nonfinite values are rejected; malformed, duplicate, non-ASCII and
   mismatched manifest documents and files are rejected without advancing
   state.
7. **Boundary preservation.** `CONTRACTS.md`, both public v0 headers,
   `CMakeLists.txt`, `REUSE.toml`, the CI workflow, the root `README.md` and
   the Apache-2.0 license are pinned by SHA-256 and verified unchanged.
   Installed v0 remains 16 kHz, mono, float32, 160 samples per frame. No
   Media3 provider is installed or registered; no descriptor, default, ABI,
   shared build, CI, board or handoff change is made.

## Rate profile application

`plan/swarm/VERIFICATION.md` requires source/output mapping, duration, pitch,
transient audibility and playback buffering with 1×, rate changes, unfamiliar
speech, music, silence, rebuffer, drift and the final partial window. This
package separates what the synthetic arithmetic control can prove from what
requires the exact Media3 runtime.

| Required item | Status here | Evidence |
| --- | --- | --- |
| Source/output mapping | synthetic_control_only | Exact `floor(source_position/speed)` on the integer fixture |
| Duration | synthetic_control_only | Exact integer/rational duration error; no Media3 run |
| Unity 1× | synthetic_control_only | Exact identity mapping at `1/1` |
| Final partial window | synthetic_control_only | 165-frame source window in two 160-frame chunks |
| Drift over a long run | synthetic_control_only | One-hour chunk-output sum equals the closed-form total |
| Adverse / missing / nonfinite | synthetic_control_only | 28 request, 8 mapping and 18 manifest rejections |
| Pitch | blocked | No Media3 runtime or pitch measurement |
| Transient audibility | blocked | No Media3 actuator or listening asset |
| Playback buffering | blocked | No Media3/Android playout FIFO or fill run |
| Rebuffer | blocked | No buffer-occupancy injection or Media3 trace |
| Rate changes (step/ramp) | blocked | No Media3 runtime trace |
| Unfamiliar speech | blocked | No real speech or held-out corpus |
| Music | blocked | No music corpus or Media3 run |
| Silence | blocked | No Media3 audio path or silence run |
| Source-timestamp-tied decisions | blocked | No pause/filler policy on a Media3 runtime |
| Speech preservation | blocked | No candidate output or metric |
| Device timing | blocked | No device/emulator, audio HAL or paced run |
| Release and distribution terms | blocked | No Media3, AndroidX, Android or output-use approval |

## Synthetic rate arithmetic control

`reference.py` accepts a strict `SonicAudioProcessor`-shaped request with exact
integer speed/pitch, the installed v0 host grid and an explicit
`is_candidate_result=false` marker. It then applies the declared integer
mapping to a 16,000-sample integer fixture (1 s at 16 kHz), which is not
speech, not a corpus and not audio.

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

The control is labelled `is_media3_sonic=false`,
`is_synthetic_control=true` and `is_candidate_result=false`. It is **not** a
Media3 output, a Java runtime result, a platform rate result or a listening
result. It only exercises the arithmetic that a future qualified runtime
control must satisfy.

## Blocked measurement classes

| Evidence class | Status | Value |
| --- | --- | --- |
| Media3 runtime sample rate / content delay / state | `blocked` | `null` |
| Pitch error | `blocked` | `pitch_error_cents=null` |
| Transient audibility | `blocked` | `transient_audibility=null` |
| Playback buffer fill / rebuffer | `blocked` | `fill_ms=null`, `rebuffer_count=null` |
| Device output timing | `blocked` | `output_latency_ms=null`, `callback_jitter_ms=null` |
| Speech preservation | `blocked` | `preservation_metric=null` |
| Listening / comprehension | `blocked` | `protocol_id=null`, `preference=null`, `comprehension=null` |
| Separation | Enforced | `device_timing_is_listening=false`, `native_c_is_media3_java=false`, `pooled_metric=null` |

A device timing run is never relabelled as listening, the native Sonic C
original is never relabelled as Media3, and an arithmetic control is never
relabelled as a candidate result.

## Failure controls (exact failures recorded as failures)

- **Request:** 28 adverse vectors are rejected: NaN/infinity/boolean/string
  speed, zero and negative denominator, negative numerator, below-floor and
  above-ceiling speed, non-unity pitch, zero/negative pitch denominator,
  nonfinite pitch, boolean/float/wrong sample rate, boolean/wrong channels,
  boolean/wrong frame samples, candidate claim in boolean and string form,
  wrong schema, empty request ID, missing field, extra field, non-object and
  empty request.
- **Mapping:** 8 adverse vectors are rejected: nonfinite/boolean/zero/
  below-floor/above-ceiling speed, boolean source frames, negative source
  frames and oversized source frames.
- **Manifest:** 18 adverse documents are rejected: missing and extra fields,
  uppercase and short source revision, wrong `SonicAudioProcessor.java` and
  `Sonic.java` basenames, relative path, parent traversal, duplicate paths,
  uppercase hash, wrong hash length, identical source-file digests, rejected
  terms, wrong attestation, empty artifact ID, empty and `not_established`
  listening protocol, and a non-ASCII path. Missing files and mismatched bytes
  are rejected by the file checker.
- **Qualification:** all 14 missing-result rows are `blocked` with
  `value=null`; all 9 qualification slots are null; all eight gates are
  `blocked`.
- No missing, rejected, stale, unrun or blocked result is promoted to a pass.

## Eight blocked release gates

1. `exact_media3_source_and_sonic_java_identity`
2. `media3_semantics_sample_format_and_geometry`
3. `license_and_output_rights`
4. `java_android_and_build_toolchain_lock`
5. `rights_cleared_speech_music_corpus_and_listening`
6. `measured_source_output_duration_pitch_transient`
7. `measured_buffering_rebuffer_drift_and_device_timing`
8. `opt_in_adapter_intake_and_release_review`

Each gate is `blocked` with `evidence=null` and `qualifies=false` in
`contract.json` and `report.json`.

## Boundary

- Work is confined to
  `docs/task-evidence/media3-sonicaudioprocessor-java-port-of-sonic/`. Shared
  CMake, contracts, public headers, descriptor registry, defaults, installed
  v0 behavior and other tasks are untouched.
- Installed v0 stays 16 kHz / mono / float32 / 160-sample frames. No provider
  is registered, exposed or default-enabled. No adapter, readiness file or
  registry entry is added.
- The reference is deterministic, platform-free and standard-library only. It
  is default OFF, unregistered and not a provider.
- No Media3 source, AAR/JAR, Gradle/Maven cache, Java build, Android runtime,
  device, real corpus, listening panel, network download or release
  qualification is used. Every control is integer or exact rational
  arithmetic.
- Missing, invalid, nonfinite, out-of-range, candidate-claim,
  source-file-identity and file-mismatch cases fail closed. No missing result
  may qualify the candidate.

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

## Reproduction

From this directory, with Python 3 standard library only:

```sh
PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
python3 run.py --report
python3 run.py --contract
python3 run.py --sources
python3 run.py --inspect
python3 verify.py
python3 -m reuse lint
```

`run.py --report` rebuilds the report three times in one process and writes
only when the bytes are identical. `verify.py` additionally runs `--report`,
`--contract`, `--sources` and `--inspect` three times from a cold start and
requires one byte-identical result. It fails on any change outside
`docs/task-evidence/media3-sonicaudioprocessor-java-port-of-sonic/` and on a
drifted stable board projection.

## Source pins (SHA-256)

`source:` paths are relative to `/Users/htsakanyan/workspace/audio/audioml`.
Every row is machine-checked by `verify.py` and the test suite. Only provenance
files that exist are pinned; no absent candidate artifact is given a fabricated
hash. The mutable full `plan/swarm/TASKS.json` is not pinned or hashed.

| Source | SHA-256 |
| --- | --- |
| `source:cpp-library/pipeline-validation/playback-speed-candidates.md` | `661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3` |
| `source:audio-benchmark-platform/plan/INVENTORY.json` | `46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c` |
| `source:audio-benchmark-platform/plan/audio-sdk/README.md` | `f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06` |
| `source:audio-benchmark-platform/plan/swarm/VERIFICATION.md` | `3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910` |
| `source:audio-benchmark-platform/audio-pro/docs/rights-register.md` | `e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44` |
| `source:audio-benchmark-platform/audio-pro/inventory/rights-register.json` | `24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923` |
| `source:cpp-library/third_party/sonic/sonic.c` | `ae9a7c39a537ebcd23db639c1130d113482d38df724dbb3c40f2b8abf937508e` |
| `source:cpp-library/third_party/sonic/sonic.h` | `0ad2caa7909497d55271accf8eb5c5f417e14d01b47ed77eca120c8073b98216` |
| `source:cpp-library/third_party/sonic/LICENSE` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |

| Boundary | SHA-256 |
| --- | --- |
| `boundary:.github/workflows/ci.yml` | `ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415` |
| `boundary:CMakeLists.txt` | `af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04` |
| `boundary:CONTRACTS.md` | `f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69` |
| `boundary:LICENSES/Apache-2.0.txt` | `cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30` |
| `boundary:README.md` | `4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35` |
| `boundary:REUSE.toml` | `c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8` |
| `boundary:api/include/audio_sdk/provider_v0.h` | `f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766` |
| `boundary:api/include/audio_sdk/session_v0.h` | `a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1` |
| `boundary:scripts/ci.py` | `64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f` |

| Sibling | SHA-256 |
| --- | --- |
| `sibling:docs/task-evidence/sonic/contract.json` | `dea2168b7ad7466a848d1fdfbee4047f84062c31d265c3cde0686cee8beaccf1` |
| `sibling:docs/task-evidence/sonic/report.json` | `2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2` |
| `sibling:docs/task-evidence/signalsmith-stretch/contract.json` | `cec65c71a339e76bb668cb9d895285b7b152229d6a9af20c2401b69c7785ff9e` |
| `sibling:docs/task-evidence/signalsmith-stretch/report.json` | `e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231` |
| `sibling:docs/task-evidence/audiotrack-setplaybackparams-playbackparams/contract.json` | `1f09b9c39fb63ee8e36058a86ed3c16a02e41a41d73327c7874625dda92d61ed` |
| `sibling:docs/task-evidence/audiotrack-setplaybackparams-playbackparams/report.json` | `d4a45b242f788edd173357db9c3f1ef032cc745cc7701a36f8c37fb1c5c5cc90` |
| `sibling:docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/contract.json` | `c9dd9bc2b818127f35dcb27969d7e0c91ceda58c1242aa8126323174db01b9d8` |
| `sibling:docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/report.json` | `1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4` |
| `sibling:docs/task-evidence/pitch-period-repeat-plc/report.json` | `114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445` |

No download, fabrication or substitution was attempted. A research-note row is
not an implementation, a Java source tree, an artifact, a runtime or a
measurement.
