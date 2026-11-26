# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, stdlib-only Media3 SonicAudioProcessor DEFER package.

This is a *proposal-only* rate-profile feasibility package for
``androidx.media3.common.audio.SonicAudioProcessor`` (the Media3 Java port of
the Sonic C library).  It does not contain, link, import, install, download,
execute or emulate the Media3 Java source, a Media3 AAR/JAR, a Java/Android
build, a device/emulator, a real corpus, a listening panel or a benchmark.

The exact licensed Media3 Java source and the exact runtime are absent, so
there is nothing exact to reproduce here and every candidate result is ``None``
with an explicit status.  No result qualifies.

What is reproduced mechanically is only a bounded, deterministic *arithmetic*
control for a declared playback-rate request:

* a strict synthetic SonicAudioProcessor-shaped request with exact rational
  speed/pitch and the installed v0 host grid;
* exact ``floor(source_position / speed)`` sample mapping over an integer
  fixture, with exact duration-error arithmetic, a final partial window and a
  one-hour chunk-sum check;
* explicit ``blocked`` sections for Media3 runtime geometry, pitch, transient,
  buffer, device timing, speech preservation and listening evidence; and
* adverse, missing, invalid, nonfinite, out-of-range, candidate-claim,
  source-file-identity and file-mismatch cases rejected before any state
  change.

No synthetic number here is a Media3 measurement, a Media3 default, a Java
runtime result, a device timing result, a listening result, a benchmark or a
release claim.
"""

from __future__ import annotations

import hashlib
import json
from fractions import Fraction
from pathlib import Path
import re
from typing import Any, Dict, List, Tuple

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]

TASK_ID = "SDK-MEDIA3-SONICAUDIOPROCESSOR-JAVA-PORT-OF-SONIC"
COMPONENT = "media3-sonicaudioprocessor-java-port-of-sonic"
TITLE = "Media3 SonicAudioProcessor (Java port of Sonic)"
BASE_COMMIT = "9074704819a6af4168f8c9cf3bbe8da50484c29a"
BRANCH = "swarm/SDK-MEDIA3-SONICAUDIOPROCESSOR-JAVA-PORT-OF-SONIC"
SCHEMA_ID = "audio-sdk/task-evidence-contract/0.1"
PROFILE = "rate"
STATUS = "proposal_only_incomplete_not_qualified"
COMPLETENESS = "incomplete"
DECISION = "DEFER"
QUALIFICATION_STATUS = "not_qualified"
PROPOSAL_ONLY = True
LOCAL_IDENTITY = (
    "media3-sonicaudioprocessor-java-port-of-sonic-rate-reference-v1"
)

# Installed v0 stays untouched; these constants are boundary facts only.
SAMPLE_RATE_HZ = 16000
CHANNELS = 1
FRAME_SAMPLES = 160
SAMPLE_FORMAT = "f32"

# Declared task-local rate boundary.  The pinned research note says Media3's
# SonicAudioProcessor is an Apache-2.0 Java implementation of Sonic that
# "supports speed and pitch".  It does not establish the library's accepted
# speed/pitch ranges, defaults, buffering or sample geometry.  The values
# below are the first-product policy from the same note, not Media3 behaviour.
DECLARED_MIN_SPEED = Fraction(3, 4)
DECLARED_MAX_SPEED = Fraction(3, 2)
DECLARED_PITCH = Fraction(1, 1)

REQUEST_SCHEMA_ID = "audio-sdk/media3-sonic-audioprocessor-request/0.1"
REQUEST_FIELDS: Tuple[str, ...] = (
    "schema_id",
    "sample_rate_hz",
    "channels",
    "frame_samples",
    "speed_numerator",
    "speed_denominator",
    "pitch_numerator",
    "pitch_denominator",
    "request_id",
    "is_candidate_result",
)

# Deterministic synthetic integer fixture: not speech, not music, not audio.
CONTROL_TOTAL_SAMPLES = 16000
CONTROL_FINAL_WINDOW_SOURCE_FRAMES = 165
CONTROL_SPEEDS: Tuple[Tuple[int, int], ...] = (
    (1, 1),
    (3, 4),
    (5, 4),
    (3, 2),
)
LONG_RUN_SOURCE_FRAMES = 57_600_000  # one hour at 16 kHz
LONG_RUN_SPEED = Fraction(5, 4)
MAX_SOURCE_FRAMES = 10 ** 12

CANDIDATE_LOCATOR = (
    "cpp-library/pipeline-validation/playback-speed-candidates.md#L79"
)
CANDIDATE_FAMILY = (
    "AndroidX Media3 Java audio processor (Java port of the Sonic C library)"
)
CANDIDATE_SOURCE_REPORTED = (
    "Apache-2.0 source; useful as a reference and as the platform-native path."
)
CANDIDATE_SECTION_REPORTED = (
    "Apache-2.0 Java implementation of Sonic, used by ExoPlayer's audio "
    "pipeline; supports speed and pitch."
)
CANDIDATE_CONS_REPORTED = (
    "Java/Kotlin, not our C++ library; Android-only. "
    "AudioTrack.setPlaybackParams is the platform-level alternative."
)

MANIFEST_FIELDS: Tuple[str, ...] = (
    "artifact_id",
    "caller_attestation",
    "source_revision",
    "sonic_audio_processor_path",
    "sonic_audio_processor_sha256",
    "sonic_pitch_shifter_path",
    "sonic_pitch_shifter_sha256",
    "media3_license_path",
    "media3_license_sha256",
    "build_toolchain_lock_path",
    "build_toolchain_lock_sha256",
    "runtime_manifest_path",
    "runtime_manifest_sha256",
    "rights_approval_path",
    "rights_approval_sha256",
    "measurement_manifest_path",
    "measurement_manifest_sha256",
    "listening_protocol_id",
    "terms_accepted",
)
MANIFEST_PATH_FIELDS: Tuple[str, ...] = (
    "sonic_audio_processor_path",
    "sonic_pitch_shifter_path",
    "media3_license_path",
    "build_toolchain_lock_path",
    "runtime_manifest_path",
    "rights_approval_path",
    "measurement_manifest_path",
)
MANIFEST_HASH_FIELDS: Tuple[str, ...] = (
    "sonic_audio_processor_sha256",
    "sonic_pitch_shifter_sha256",
    "media3_license_sha256",
    "build_toolchain_lock_sha256",
    "runtime_manifest_sha256",
    "rights_approval_sha256",
    "measurement_manifest_sha256",
)
CALLER_ATTESTATION = "caller_owned_and_rights_reviewed"
HASH_RE = re.compile(r"^[0-9a-f]{64}$")
REVISION_RE = re.compile(r"^[0-9a-f]{40}$")
ID_RE = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._+-]{0,95}$")

SOURCE_PINS: Dict[str, str] = {
    "cpp-library/pipeline-validation/playback-speed-candidates.md":
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    "audio-benchmark-platform/audio-pro/docs/rights-register.md":
        "e61a406fe7601569c10f07a5072b8835903344bacd74434cc33921aadbe77e44",
    "audio-benchmark-platform/audio-pro/inventory/rights-register.json":
        "24cbdb6536999585285de85f8046eef8c16a9e59b795f470d897e0a789c45923",
    "cpp-library/third_party/sonic/sonic.c":
        "ae9a7c39a537ebcd23db639c1130d113482d38df724dbb3c40f2b8abf937508e",
    "cpp-library/third_party/sonic/sonic.h":
        "0ad2caa7909497d55271accf8eb5c5f417e14d01b47ed77eca120c8073b98216",
    "cpp-library/third_party/sonic/LICENSE":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
}
BOUNDARY_PINS: Dict[str, str] = {
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "LICENSES/Apache-2.0.txt":
        "cfc7749b96f63bd31c3c42b5c471bf756814053e847c10f3eb003417bc523d30",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "scripts/ci.py":
        "64d229ef4bc1c11b007eb4fd828846c57121467e7e530a0fd45e135507f9bc9f",
}
SIBLING_PINS: Dict[str, str] = {
    "docs/task-evidence/sonic/contract.json":
        "dea2168b7ad7466a848d1fdfbee4047f84062c31d265c3cde0686cee8beaccf1",
    "docs/task-evidence/sonic/report.json":
        "2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2",
    "docs/task-evidence/signalsmith-stretch/contract.json":
        "cec65c71a339e76bb668cb9d895285b7b152229d6a9af20c2401b69c7785ff9e",
    "docs/task-evidence/signalsmith-stretch/report.json":
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231",
    "docs/task-evidence/audiotrack-setplaybackparams-playbackparams/contract.json":
        "1f09b9c39fb63ee8e36058a86ed3c16a02e41a41d73327c7874625dda92d61ed",
    "docs/task-evidence/audiotrack-setplaybackparams-playbackparams/report.json":
        "d4a45b242f788edd173357db9c3f1ef032cc745cc7701a36f8c37fb1c5c5cc90",
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/contract.json":
        "c9dd9bc2b818127f35dcb27969d7e0c91ceda58c1242aa8126323174db01b9d8",
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/report.json":
        "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4",
    "docs/task-evidence/pitch-period-repeat-plc/report.json":
        "114f0107fc06176857157801f127a22e88639204b488cd2267bf80ee9b467445",
}
NATIVE_SONIC_PINS: Dict[str, str] = {
    "cpp-library/third_party/sonic/sonic.c": SOURCE_PINS[
        "cpp-library/third_party/sonic/sonic.c"],
    "cpp-library/third_party/sonic/sonic.h": SOURCE_PINS[
        "cpp-library/third_party/sonic/sonic.h"],
    "cpp-library/third_party/sonic/LICENSE": SOURCE_PINS[
        "cpp-library/third_party/sonic/LICENSE"],
}

TASK_ROW_IDENTITY: Dict[str, Any] = {
    "id": TASK_ID,
    "title": TITLE,
    "repository": "audio-sdk",
    "mode": "feasibility",
    "component": COMPONENT,
    "depends_on": ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"],
    "write_scope": [
        "SDK provider, tool or evidence directory for "
        "media3-sonicaudioprocessor-java-port-of-sonic and its own fixtures",
    ],
    "deliverable": (
        "Verify runnable source, exact assets, permitted scope, task geometry "
        "and matched evidence. Then implement or wrap a minimal reference "
        "using the relevant public adapter boundary and ship it as optional "
        "initially. Record a concrete blocker if feasibility fails."
    ),
    "acceptance": (
        "Apply the rate acceptance profile; record exact scope, evidence, "
        "failure/control results, and remaining release gates. A readiness "
        "conclusion with an exact external blocker is an accepted "
        "investigation handoff; it does not close the conditional "
        "implementation."
    ),
    "evidence": [
        "cpp-library/pipeline-validation/playback-speed-candidates.md",
    ],
    "dispatch_priority": 3,
    "base_commit": BASE_COMMIT,
    "branch": BRANCH,
}
MUTABLE_PROVENANCE: Dict[str, Any] = {
    "path": "audio-benchmark-platform/plan/swarm/TASKS.json",
    "mutable": True,
    "hashed": False,
    "gate": False,
    "note": (
        "Only the stable linked-row projection above is compared. The mutable "
        "full board file is never hashed by or pinned to this package."
    ),
}
SCOPE: Dict[str, Any] = {
    "android_runtime": False,
    "audio_processed": False,
    "benchmark_claim": False,
    "candidate_licensed_source_or_binary": False,
    "device_or_emulator": False,
    "device_timing": False,
    "downloads": False,
    "gradle_or_maven_artifact": False,
    "installed_v0_format": "16 kHz mono float32, 160 samples",
    "java_build": False,
    "listening": False,
    "media3_source": False,
    "native_sonic_c_present": True,
    "network_used": False,
    "provider_registered": False,
    "real_speech_or_corpus": False,
    "release_claim": False,
    "synthetic_only": True,
    "task_local_only": True,
}
PUBLIC_SURFACE: Dict[str, bool] = {
    "abi_change": False,
    "benchmark_claim": False,
    "ci_change": False,
    "descriptor_default_change": False,
    "installed_v0_behavior_change": False,
    "processor_exposure": False,
    "provider_registration": False,
    "public_api_change": False,
    "registry_change": False,
    "release_claim": False,
    "shared_cmakelists_change": False,
}

PROFILE_ITEMS: Tuple[Tuple[str, str, str], ...] = (
    ("source_output_mapping", "synthetic_control_only",
     "Exact floor(source_position/speed) mapping on the integer fixture."),
    ("duration", "synthetic_control_only",
     "Exact duration-error arithmetic; no Media3 or Java run."),
    ("unity_1x", "synthetic_control_only",
     "Exact identity mapping at speed 1/1."),
    ("final_partial_window", "synthetic_control_only",
     "165-frame source window mapped in two 160-frame chunks."),
    ("drift_over_long_run", "synthetic_control_only",
     "One-hour chunk-output sum equals the closed-form total."),
    ("adverse_missing_invalid_nonfinite", "synthetic_control_only",
     "Request, mapping and manifest rejections are fail-closed."),
    ("pitch", "blocked",
     "No Media3 runtime, Java pitch behaviour or pitch measurement."),
    ("transient_audibility", "blocked",
     "No Media3 actuator, audio path or listening asset."),
    ("playback_buffering", "blocked",
     "No Media3/Android playout FIFO, fill or rebuffer run."),
    ("rebuffer", "blocked",
     "No buffer-occupancy injection or Media3 rebuffer trace."),
    ("rate_changes", "blocked",
     "No Media3 runtime or step/ramp trace."),
    ("unfamiliar_speech", "blocked",
     "No real speech or held-out corpus."),
    ("music", "blocked",
     "No music corpus or Media3 run."),
    ("silence", "blocked",
     "No Media3 audio path or silence run."),
    ("source_timestamp_tied_decisions", "blocked",
     "No source-timestamp pause/filler policy on a Media3 runtime."),
    ("speech_preservation", "blocked",
     "No candidate output or preservation metric."),
    ("device_timing", "blocked",
     "No device/emulator, audio HAL or paced run."),
    ("release_and_distribution_terms", "blocked",
     "No Media3, AndroidX, Android or output-use approval."),
)
ALLOWED_PROFILE_STATUS = {"synthetic_control_only", "blocked"}

MISSING_RESULTS: Tuple[Tuple[str, str], ...] = (
    ("media3_java_source_identity", "No exact Media3 source checkout."),
    ("media3_runtime_sample_format", "No Media3 AAR/JAR or Java runtime."),
    ("media3_speed_range", "No Media3 runtime or source geometry."),
    ("media3_pitch_range", "No Media3 runtime or source geometry."),
    ("source_output_mapping_runtime", "No Media3 runtime."),
    ("duration_error_measured", "No Media3 runtime."),
    ("pitch_error_cents", "No pitch measurement."),
    ("transient_audibility", "No actuator or listening."),
    ("playback_buffer_fill_ms", "No playout FIFO run."),
    ("device_output_latency_ms", "No device timing."),
    ("rebuffer_behavior", "No rebuffer injection."),
    ("speech_preservation", "No candidate output or metric."),
    ("listening_or_comprehension", "No protocol or panel."),
    ("release", "No license or release approval."),
)
QUALIFICATION_SLOTS: Tuple[str, ...] = (
    "speed_range_verified",
    "pitch_range_verified",
    "source_output_mapping",
    "duration_error_ms_per_audio_second",
    "pitch_error_cents",
    "transient_audibility",
    "playback_buffer_fill_ms",
    "device_output_latency_ms",
    "release",
)
FAILURE_CHECK_IDS: Tuple[str, ...] = (
    "strict_json_rejects_nan",
    "strict_json_rejects_infinity",
    "strict_json_rejects_duplicate_keys",
    "request_rejections_are_explicit",
    "mapping_rejections_are_explicit",
    "manifest_rejections_are_explicit",
    "no_rejected_value_is_scored",
    "no_missing_value_is_promoted",
    "all_release_gates_blocked",
    "all_qualification_slots_null",
    "all_profile_items_nonqualifying",
    "all_adverse_nonqualifying",
    "all_manifest_controls_nonqualifying",
    "all_required_artifacts_absent",
    "media3_source_absent",
    "media3_artifact_absent",
    "pinned_runtime_absent",
    "device_timing_absent",
    "pitch_measurement_absent",
    "buffer_measurement_absent",
    "speech_preservation_absent",
    "listening_absent",
    "candidate_claim_rejected",
    "nonfinite_rejected",
    "source_files_identity_controls",
    "native_c_is_not_media3",
    "no_qualifying_result",
)

REQUIRED_ARTIFACTS: List[Dict[str, Any]] = [
    {
        "id": "exact_media3_java_source",
        "artifact": (
            "The exact Media3 source checkout containing "
            "SonicAudioProcessor.java and Sonic.java at an immutable 40-hex "
            "revision, with a full per-file SHA-256 manifest and the reviewed "
            "upstream LICENSE and notice text."
        ),
        "present": False,
        "rights_requirement": (
            "AndroidX/Google source terms plus a written grant to read, "
            "reproduce and publish the named revision."
        ),
        "why_blocked": (
            "No Media3, AndroidX or ExoPlayer checkout exists locally; the "
            "pinned note gives a documentation link but no revision, source "
            "tree or file digest."
        ),
    },
    {
        "id": "exact_media3_artifact_and_runtime",
        "artifact": (
            "The exact Media3 AAR/JAR built from the pinned source revision "
            "and a locked Java/Android runtime with a recorded sample format, "
            "buffering and state contract."
        ),
        "present": False,
        "rights_requirement": (
            "AndroidX artifact terms, runtime distribution terms and approval "
            "to execute and measure the named artifact."
        ),
        "why_blocked": (
            "No Media3 AAR/JAR, Gradle cache, Maven cache, Java build or "
            "pinned runtime exists locally; no runtime manifest is recorded."
        ),
    },
    {
        "id": "java_android_build_toolchain_lock",
        "artifact": (
            "A locked Java/Android build toolchain (JDK, Gradle wrapper, "
            "Android Gradle Plugin and dependency versions) with install "
            "digests for the exact Media3 revision."
        ),
        "present": False,
        "rights_requirement": (
            "Toolchain distribution and Android SDK terms for the exact "
            "versions used to build and run the artifact."
        ),
        "why_blocked": (
            "No Gradle wrapper, dependency lock, build configuration or "
            "pinned toolchain is present for Media3."
        ),
    },
    {
        "id": "license_and_output_rights",
        "artifact": (
            "Reviewed Media3, AndroidX, Android and output-use terms and a "
            "signed rights decision for execution, measurement, "
            "redistribution and generated-output use."
        ),
        "present": False,
        "rights_requirement": (
            "Source, artifact and platform rightsholder terms plus "
            "commercial/derivative output approval for the named revision."
        ),
        "why_blocked": (
            "The rights register has no Media3, Sonic or AndroidX entry; "
            "Apache-2.0 source text alone does not settle Android platform, "
            "toolchain, corpus or output rights."
        ),
    },
    {
        "id": "declared_media3_semantics_and_geometry",
        "artifact": (
            "The official Media3 speed/pitch ranges, defaults, sample "
            "formats, content delay, buffering, state and drain behaviour "
            "reproduced from the exact source revision."
        ),
        "present": False,
        "rights_requirement": (
            "Documentation and source terms that permit quoting and "
            "reproducing the declared semantics."
        ),
        "why_blocked": (
            "The pinned note only says SonicAudioProcessor supports speed and "
            "pitch; it establishes no ranges, formats, buffering or geometry."
        ),
    },
    {
        "id": "rights_cleared_speech_music_corpus",
        "artifact": (
            "A rights-cleared cohort covering unfamiliar speech, music, "
            "silence, rate changes and rebuffer cases with a frozen manifest."
        ),
        "present": False,
        "rights_requirement": (
            "Corpus, participant, annotation, redistribution and "
            "model-evaluation rights for every recording."
        ),
        "why_blocked": (
            "No real speech, music or silence corpus and no rights record is "
            "assigned to this task."
        ),
    },
    {
        "id": "measured_rate_pitch_transient_buffer_and_device_timing",
        "artifact": (
            "Measured source/output mapping, duration, pitch, transient "
            "audibility, buffer fill, rebuffer and device timing on the exact "
            "Media3 runtime."
        ),
        "present": False,
        "rights_requirement": (
            "Approval to run and publish measurements from the named runtime "
            "and device or emulator."
        ),
        "why_blocked": (
            "No Media3 runtime, Java build, device or measurement harness "
            "exists; nothing is measured or inferred."
        ),
    },
    {
        "id": "listening_protocol_and_release_review",
        "artifact": (
            "An authorized listening/speech-preservation protocol, an "
            "OFF-by-default opt-in adapter intake and independent exact-head "
            "release review."
        ),
        "present": False,
        "rights_requirement": (
            "Panel consent, participant-data terms, reviewer approval and "
            "release-authority approval."
        ),
        "why_blocked": (
            "No listening protocol, panel, adapter, registration, review or "
            "release decision exists; none is added here."
        ),
    },
]
RELEASE_GATES: List[Dict[str, Any]] = [
    {
        "id": "exact_media3_source_and_sonic_java_identity",
        "requirement": (
            "An exact Media3 source revision containing "
            "SonicAudioProcessor.java and Sonic.java, each with an immutable "
            "40-hex commit and full SHA-256."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "media3_semantics_sample_format_and_geometry",
        "requirement": (
            "Declared speed/pitch ranges, defaults, sample formats, content "
            "delay, buffering, state and drain behaviour reproduced for the "
            "exact runtime."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "license_and_output_rights",
        "requirement": (
            "Reviewed Media3/AndroidX/Android terms and written approval for "
            "execution, benchmarking, redistribution and generated-output "
            "use."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "java_android_and_build_toolchain_lock",
        "requirement": (
            "A locked JDK, Gradle wrapper, Android Gradle Plugin, Android SDK "
            "and dependency set with install digests."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "rights_cleared_speech_music_corpus_and_listening",
        "requirement": (
            "A rights-cleared speech/music/silence cohort and an authorized "
            "listening or speech-preservation result separate from device "
            "timing."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "measured_source_output_duration_pitch_transient",
        "requirement": (
            "Measured source/output mapping, duration drift, pitch error and "
            "transient audibility on the exact Media3 runtime."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "measured_buffering_rebuffer_drift_and_device_timing",
        "requirement": (
            "Measured playback buffering, rebuffer, long-run drift and "
            "target-device output timing/resources for the exact runtime."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
    {
        "id": "opt_in_adapter_intake_and_release_review",
        "requirement": (
            "An OFF-by-default opt-in adapter intake, independent exact-head "
            "review of this evidence and explicit release approval."
        ),
        "status": "blocked",
        "evidence": None,
        "qualifies": False,
    },
]
EXACT_BLOCKERS: List[str] = [
    (
        "No exact Media3 Java source is present or pinned. There is no "
        "Media3/AndroidX/ExoPlayer checkout, no 40-hex source revision, no "
        "SonicAudioProcessor.java or Sonic.java digest, and no reviewed "
        "LICENSE bundle for the release. The pinned research note links a "
        "documentation page and describes the candidate; it does not provide "
        "source, revision or file bytes."
    ),
    (
        "No exact Media3 artifact or runtime exists. No Media3 AAR/JAR, "
        "Gradle cache, Maven cache, Java build, Android runtime image, device "
        "or emulator is present. No sample format, speed/pitch range, "
        "buffering, content delay, state or drain contract is recorded."
    ),
    (
        "No pinned Java/Android build toolchain exists. No JDK, Gradle "
        "wrapper, Android Gradle Plugin, Android SDK, dependency lock or "
        "reproducible build output is recorded for the candidate."
    ),
    (
        "Rights are unresolved. The rights register has no Media3, Sonic or "
        "AndroidX entry, so evaluation, redistribution, customer deployment, "
        "public playback and output use are unknown. Apache-2.0 source text "
        "is not a signed rights decision and does not clear Android platform, "
        "toolchain, corpus or output rights."
    ),
    (
        "No candidate semantics or geometry are known. The pinned note says "
        "SonicAudioProcessor is an Apache-2.0 Java implementation of Sonic "
        "that supports speed and pitch; it establishes no accepted ranges, "
        "defaults, sample formats, buffering, content delay or state "
        "behaviour. This package fabricates none and exposes no provider."
    ),
    (
        "The present native Sonic C original is not the candidate. "
        "cpp-library/third_party/sonic contains the Apache-2.0 Sonic C "
        "library by Bill Cox, pinned read-only for provenance. It is a "
        "different implementation from Media3's Java port, has no Media3 "
        "Android integration, and is not admitted for parity, quality or "
        "qualification."
    ),
    (
        "No candidate evidence exists. There is no Media3 output, exact-"
        "reference parity, rights-cleared corpus, independent pitch, "
        "transient or preservation scorer, permitted listening result or "
        "target-runtime timing. The synthetic arithmetic control is not "
        "Media3 and cannot qualify the candidate. All eight release gates "
        "remain blocked and no result may qualify the candidate."
    ),
]
NON_CLAIMS: List[str] = [
    "No Media3 SonicAudioProcessor, Sonic.java, AndroidX source, AAR/JAR, Java build, Android runtime, device or emulator is present, linked, imported, executed or reproduced.",
    "No Media3, AndroidX, ExoPlayer, Android SDK, corpus or recording is downloaded, copied, vendored or substituted; the present native Sonic C files are hashed read-only for provenance only.",
    "No Media3 speed/pitch range, default, sample format, buffering, content delay, device latency or state behaviour is claimed; every candidate result is null.",
    "The synthetic arithmetic control is not a Media3 output, a Java runtime result, a platform rate result or a listening result.",
    "Pitch, transient, buffering, device timing, speech preservation and listening are reported as separate blocked evidence classes; none is relabelled, pooled or promoted.",
    "The native Sonic C original is not the Media3 Java port and is never used for parity, quality, timing or qualification.",
    "No real speech, music, held-out corpus, listening panel, device timing, benchmark or release claim is made.",
    "No installed v0, ABI, registry, descriptor, default, shared build or CI behavior is changed; no provider or processor is registered, exposed or default-enabled.",
    "No missing, blocked or adverse result is promoted; no result qualifies.",
]
REPRODUCTION: List[str] = [
    "PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py",
    "python3 run.py --report",
    "python3 run.py --contract",
    "python3 run.py --sources",
    "python3 run.py --inspect",
    "python3 verify.py",
]
LOCAL_FILES: Tuple[str, ...] = (
    "README.md",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)
REPORT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "absence_audit",
    "acceptance_profile",
    "adverse_results",
    "artifact_assessment",
    "base_commit",
    "boundary_pins",
    "branch",
    "candidate_record",
    "completeness",
    "component",
    "control_envelope",
    "decision",
    "declared_contract",
    "exact_blockers",
    "failure_controls",
    "manifest_contract",
    "manifest_controls",
    "mapping_adverse_results",
    "missing_results",
    "mutable_provenance",
    "native_sonic_c_provenance",
    "non_claims",
    "observed_provenance",
    "profile",
    "proposal_only",
    "public_surface",
    "qualification",
    "qualification_slots",
    "ranking",
    "regeneration",
    "release_gates",
    "reproduction",
    "required_artifacts",
    "schema_id",
    "scope",
    "sibling_pins",
    "source_pins",
    "status",
    "task",
    "task_row",
    "title",
}
CONTRACT_KEYS = {
    "SPDX-FileCopyrightText",
    "SPDX-License-Identifier",
    "absence_audit",
    "artifact_pins",
    "base_commit",
    "boundary_pins",
    "branch",
    "candidate_record",
    "completeness",
    "component",
    "decision",
    "declared_contract",
    "exact_blockers",
    "local_files",
    "manifest_contract",
    "mutable_provenance",
    "native_sonic_c_provenance",
    "non_claims",
    "profile",
    "proposal_only",
    "public_surface",
    "qualification",
    "release_gates",
    "reproduction",
    "required_artifacts",
    "schema_id",
    "scope",
    "sibling_pins",
    "source_pins",
    "status",
    "task",
    "task_row",
    "title",
}

CHECKED_PATHS: Tuple[str, ...] = (
    "workspace:adapters/media3-sonicaudioprocessor-java-port-of-sonic",
    "workspace:data/checkouts/androidx",
    "workspace:data/checkouts/androidx-media",
    "workspace:data/checkouts/androidx-media3",
    "workspace:data/checkouts/exoplayer",
    "workspace:data/checkouts/media3",
    "workspace:data/checkouts/media3-exoplayer",
    "workspace:data/envs/media3",
    "workspace:data/licenses/androidx-media3",
    "workspace:data/manifests/media3-sonic.json",
    "workspace:data/reference/media3-sonic",
    "workspace:data/sources/androidx-media",
    "worktree:third_party/androidx",
    "worktree:third_party/media3",
)
HOST_PATH_PROBES: Tuple[str, ...] = (
    "home:.gradle/caches/modules-2/files-2.1/androidx.media3",
    "home:.gradle/caches/modules-2/files-2.1/androidx.media3/media3-common",
    "home:.m2/repository/androidx/media3",
)

SPDX_COPYRIGHT_KEY = "SPDX-FileCopyrightText"
SPDX_LICENSE_KEY = "SPDX-License-" "Identifier"


class ReferenceError(ValueError):
    """Explicit rejection; no rejected value is scored or promoted."""


# ---------------------------------------------------------------------------
# Strict JSON and canonical serialization
# ---------------------------------------------------------------------------

def _reject_constant(value: str) -> None:
    raise ValueError("non_json_constant:" + value)


def parse_strict_json_text(text: str) -> Any:
    """Parse strict JSON; duplicate keys, NaN and Infinity are rejected."""
    def unique_pairs(pairs: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    value = json.loads(text, parse_constant=_reject_constant,
                       object_pairs_hook=unique_pairs)
    if not isinstance(value, dict):
        raise ValueError("json_root_is_not_an_object")
    return value


def read_strict_json(path: Path) -> Any:
    return parse_strict_json_text(path.read_text(encoding="utf-8"))


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=False).encode("utf-8")


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(report, sort_keys=True, indent=2, ensure_ascii=True,
                      allow_nan=False)
    payload = (text + "\n").encode("utf-8")
    return text, sha256_bytes(payload)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def digest_file(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _ratio_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return "%d/%d" % (value.numerator, value.denominator)


def _int_field(value: Any, field: str) -> int:
    if type(value) is not int:
        raise ReferenceError(field + "_not_integer")
    return value


# ---------------------------------------------------------------------------
# Strict synthetic SonicAudioProcessor-shaped request
# ---------------------------------------------------------------------------

def valid_request() -> Dict[str, Any]:
    return {
        "schema_id": REQUEST_SCHEMA_ID,
        "sample_rate_hz": SAMPLE_RATE_HZ,
        "channels": CHANNELS,
        "frame_samples": FRAME_SAMPLES,
        "speed_numerator": 5,
        "speed_denominator": 4,
        "pitch_numerator": 1,
        "pitch_denominator": 1,
        "request_id": "request-rate-125",
        "is_candidate_result": False,
    }


def parse_rate_request(request: Any) -> Dict[str, Any]:
    if not isinstance(request, dict):
        raise ReferenceError("request_not_an_object")
    missing = [key for key in REQUEST_FIELDS if key not in request]
    if missing:
        raise ReferenceError("request_missing_fields:" + ",".join(missing))
    extra = sorted(set(request) - set(REQUEST_FIELDS))
    if extra:
        raise ReferenceError("request_extra_fields:" + ",".join(extra))
    if request["schema_id"] != REQUEST_SCHEMA_ID:
        raise ReferenceError("request_schema_id_invalid")
    if not isinstance(request["request_id"], str) \
            or not ID_RE.match(request["request_id"]):
        raise ReferenceError("request_id_invalid")

    sample_rate = _int_field(request["sample_rate_hz"],
                             "request_sample_rate_hz")
    if sample_rate != SAMPLE_RATE_HZ:
        raise ReferenceError("request_sample_rate_not_supported")
    channels = _int_field(request["channels"], "request_channels")
    if channels != CHANNELS:
        raise ReferenceError("request_channels_not_supported")
    frame = _int_field(request["frame_samples"], "request_frame_samples")
    if frame != FRAME_SAMPLES:
        raise ReferenceError("request_frame_samples_not_supported")

    speed_num = _int_field(request["speed_numerator"],
                           "request_speed_numerator")
    speed_den = _int_field(request["speed_denominator"],
                           "request_speed_denominator")
    if speed_num <= 0:
        raise ReferenceError("request_speed_numerator_not_positive")
    if speed_den <= 0:
        raise ReferenceError("request_speed_denominator_not_positive")
    speed = Fraction(speed_num, speed_den)
    if speed < DECLARED_MIN_SPEED:
        raise ReferenceError("request_speed_below_declared_floor")
    if speed > DECLARED_MAX_SPEED:
        raise ReferenceError("request_speed_above_declared_ceiling")

    pitch_num = _int_field(request["pitch_numerator"],
                           "request_pitch_numerator")
    pitch_den = _int_field(request["pitch_denominator"],
                           "request_pitch_denominator")
    if pitch_num <= 0:
        raise ReferenceError("request_pitch_numerator_not_positive")
    if pitch_den <= 0:
        raise ReferenceError("request_pitch_denominator_not_positive")
    pitch = Fraction(pitch_num, pitch_den)
    if pitch != DECLARED_PITCH:
        raise ReferenceError("request_pitch_not_unity")

    if request["is_candidate_result"] is not False:
        raise ReferenceError("request_candidate_claim")

    return {
        "schema_id": REQUEST_SCHEMA_ID,
        "sample_rate_hz": sample_rate,
        "channels": channels,
        "frame_samples": frame,
        "speed": _ratio_text(speed),
        "speed_numerator": speed_num,
        "speed_denominator": speed_den,
        "pitch": _ratio_text(pitch),
        "request_id": request["request_id"],
        "is_candidate_result": False,
        "is_synthetic_control": True,
        "is_media3_runtime_result": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Exact declared sample mapping
# ---------------------------------------------------------------------------

def _output_position(speed: Fraction, source_position: int) -> int:
    return (source_position * speed.denominator) // speed.numerator


def map_source_to_output(speed: Any, source_frames: Any,
                         chunk_frames: int = FRAME_SAMPLES,
                         include_chunks: bool = True) -> Dict[str, Any]:
    if not isinstance(speed, Fraction) or isinstance(speed, bool):
        raise ReferenceError("mapping_speed_not_fraction")
    if speed <= 0:
        raise ReferenceError("mapping_speed_not_positive")
    if speed < DECLARED_MIN_SPEED:
        raise ReferenceError("mapping_speed_below_declared_floor")
    if speed > DECLARED_MAX_SPEED:
        raise ReferenceError("mapping_speed_above_declared_ceiling")
    if type(source_frames) is not int:
        raise ReferenceError("mapping_source_frames_not_integer")
    if source_frames < 0:
        raise ReferenceError("mapping_source_frames_negative")
    if source_frames > MAX_SOURCE_FRAMES:
        raise ReferenceError("mapping_source_frames_too_large")
    if type(chunk_frames) is not int or not 1 <= chunk_frames <= FRAME_SAMPLES:
        raise ReferenceError("mapping_chunk_frames_invalid")

    total_output = _output_position(speed, source_frames)
    chunks: List[Dict[str, Any]] = []
    chunk_sum = 0
    start = 0
    while start < source_frames:
        end = min(start + chunk_frames, source_frames)
        out_end = _output_position(speed, end)
        chunk_sum += out_end - _output_position(speed, start)
        if include_chunks:
            chunks.append({
                "source_start": str(start),
                "source_end_exclusive": str(end),
                "output_start": str(_output_position(speed, start)),
                "output_end_exclusive": str(out_end),
            })
        start = end
    error = Fraction(total_output) - Fraction(source_frames, 1) / speed
    return {
        "speed": _ratio_text(speed),
        "source_frames": str(source_frames),
        "output_frames": str(total_output),
        "duration_error_samples_exact": _ratio_text(error),
        "duration_error_ms_exact": _ratio_text(error / 16),
        "chunk_frames": chunk_frames,
        "chunk_count": (source_frames + chunk_frames - 1) // chunk_frames,
        "chunk_output_sum": str(chunk_sum),
        "chunk_sum_matches_total": chunk_sum == total_output,
        "chunks": chunks,
        "is_candidate_result": False,
        "qualifies": False,
    }


def _rate_row(speed: Fraction) -> Dict[str, Any]:
    mapping = map_source_to_output(speed, CONTROL_TOTAL_SAMPLES)
    chunks = mapping["chunks"]
    return {
        "speed": mapping["speed"],
        "source_samples": mapping["source_frames"],
        "output_samples": mapping["output_frames"],
        "duration_error_samples_exact":
            mapping["duration_error_samples_exact"],
        "duration_error_ms_exact": mapping["duration_error_ms_exact"],
        "chunk_count": mapping["chunk_count"],
        "chunk_sum_matches_total": mapping["chunk_sum_matches_total"],
        "first_chunk": chunks[0],
        "last_chunk": chunks[-1],
        "is_candidate_result": False,
        "qualifies": False,
    }


def control_envelope_payload() -> Dict[str, Any]:
    rates = [_rate_row(Fraction(num, den))
             for num, den in CONTROL_SPEEDS]
    identity = map_source_to_output(Fraction(1, 1), CONTROL_TOTAL_SAMPLES)
    final_window = map_source_to_output(
        Fraction(5, 4), CONTROL_FINAL_WINDOW_SOURCE_FRAMES)
    long_run = map_source_to_output(
        LONG_RUN_SPEED, LONG_RUN_SOURCE_FRAMES, include_chunks=False)
    return {
        "control_id": (
            "media3-sonicaudioprocessor-java-port-of-sonic/"
            "declared-rate-arithmetic-control/0.1"
        ),
        "design": {
            "is_media3_sonic": False,
            "is_candidate_result": False,
            "is_synthetic_control": True,
            "declared_min_speed": _ratio_text(DECLARED_MIN_SPEED),
            "declared_max_speed": _ratio_text(DECLARED_MAX_SPEED),
            "declared_pitch": _ratio_text(DECLARED_PITCH),
            "host_grid": {
                "sample_rate_hz": SAMPLE_RATE_HZ,
                "channels": CHANNELS,
                "frame_samples": FRAME_SAMPLES,
                "sample_format": SAMPLE_FORMAT,
            },
            "speed_range_is_a_measurement": False,
            "pitch_is_a_measurement": False,
            "mapping_formula": (
                "output_position = floor(source_position / speed)"
            ),
            "qualifies": False,
        },
        "identity": {
            "speed": identity["speed"],
            "source_samples": identity["source_frames"],
            "output_samples": identity["output_frames"],
            "duration_error_samples_exact":
                identity["duration_error_samples_exact"],
            "duration_error_ms_exact": identity["duration_error_ms_exact"],
            "chunk_sum_matches_total": identity["chunk_sum_matches_total"],
            "is_candidate_result": False,
            "qualifies": False,
        },
        "rates": rates,
        "final_partial_window": {
            "speed": final_window["speed"],
            "source_frames": final_window["source_frames"],
            "output_frames": final_window["output_frames"],
            "duration_error_samples_exact":
                final_window["duration_error_samples_exact"],
            "chunk_count": final_window["chunk_count"],
            "chunks": final_window["chunks"],
            "is_candidate_result": False,
            "qualifies": False,
        },
        "long_run": {
            "speed": long_run["speed"],
            "source_frames": long_run["source_frames"],
            "output_frames": long_run["output_frames"],
            "duration_error_samples_exact":
                long_run["duration_error_samples_exact"],
            "chunk_count": long_run["chunk_count"],
            "chunk_sum_matches_total": long_run["chunk_sum_matches_total"],
            "chunk_sum_is_closed_form": True,
            "is_candidate_result": False,
            "qualifies": False,
        },
        "media3_runtime": {
            "status": "blocked",
            "output_sample_rate_hz": None,
            "content_delay_samples": None,
            "state_layout": None,
            "reason": "No Media3 AAR/JAR, Java source or Java runtime.",
            "qualifies": False,
        },
        "pitch_measurement": {
            "status": "blocked",
            "pitch_error_cents": None,
            "reason": "No Media3 runtime, pitch measurement or audio path.",
            "qualifies": False,
        },
        "transient_measurement": {
            "status": "blocked",
            "transient_audibility": None,
            "reason": "No Media3 actuator, audio corpus or listening asset.",
            "qualifies": False,
        },
        "playback_buffer": {
            "status": "blocked",
            "fill_ms": None,
            "rebuffer_count": None,
            "underrun_count": None,
            "reason": "No Media3/Android playout FIFO, paced run or rebuffer injection.",
            "qualifies": False,
        },
        "device_timing": {
            "status": "blocked",
            "output_latency_ms": None,
            "callback_jitter_ms": None,
            "reason": "No device/emulator, audio HAL or monotonic timing run.",
            "qualifies": False,
        },
        "speech_preservation": {
            "status": "blocked",
            "preservation_metric": None,
            "reason": "No candidate output, corpus or metric.",
            "qualifies": False,
        },
        "listening": {
            "status": "blocked",
            "protocol_id": None,
            "preference": None,
            "comprehension": None,
            "reason": "No listening protocol, panel or authorization.",
            "qualifies": False,
        },
        "separation": {
            "candidate_and_control_separate": True,
            "control_is_candidate": False,
            "device_timing_is_listening": False,
            "measured_and_synthetic_separate": True,
            "pooled_metric": None,
            "native_c_is_media3_java": False,
            "qualifies": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Declared candidate boundary (proposal only)
# ---------------------------------------------------------------------------

def candidate_record() -> Dict[str, Any]:
    return {
        "candidate": "androidx.media3.common.audio.SonicAudioProcessor",
        "component": COMPONENT,
        "family": CANDIDATE_FAMILY,
        "locator": CANDIDATE_LOCATOR,
        "source_reported_claim": CANDIDATE_SOURCE_REPORTED,
        "source_reported_section": CANDIDATE_SECTION_REPORTED,
        "source_reported_cons": CANDIDATE_CONS_REPORTED,
        "source_reported_only": True,
        "public_implementation_found": False,
        "media3_source_present": False,
        "media3_artifact_present": False,
        "java_source_present": False,
        "android_runtime_present": False,
        "gradle_or_maven_artifact_present": False,
        "license_reviewed": False,
        "artifact_present": False,
        "reproduced_here": False,
        "qualifies": False,
    }


def declared_contract() -> Dict[str, Any]:
    return {
        "contract_id": (
            "media3-sonicaudioprocessor-java-port-of-sonic/"
            "declared-rate-boundary/0.1"
        ),
        "adapter_status": (
            "proposal_only_no_media3_java_source_or_runtime"
        ),
        "media3_runtime_verified": False,
        "declared_speed_range": [
            _ratio_text(DECLARED_MIN_SPEED),
            _ratio_text(DECLARED_MAX_SPEED),
        ],
        "declared_pitch": _ratio_text(DECLARED_PITCH),
        "host_grid": {
            "sample_rate_hz": SAMPLE_RATE_HZ,
            "channels": CHANNELS,
            "frame_samples": FRAME_SAMPLES,
            "sample_format": SAMPLE_FORMAT,
        },
        "speed_range_is_a_measurement": False,
        "pitch_is_a_measurement": False,
        "semantics_source": "pinned_research_note_only",
        "media3_semantics_contract": "not_established",
        "sample_format_contract": "not_established",
        "device_geometry": "not_established",
        "availability_contract": "not_established",
        "buffering_contract": "not_established",
        "content_delay_contract": "not_established",
        "final_partial_window_contract": "not_established",
        "reset_contract": "not_established",
        "drain_contract": "not_established",
        "installed_v0_unchanged": True,
        "qualifies": False,
    }


def qualification_payload() -> Dict[str, Any]:
    return {
        "status": QUALIFICATION_STATUS,
        "qualifies": False,
        "incomplete": True,
        "proposal_only": True,
        "all_release_gates_blocked": True,
        "media3_source_present": False,
        "media3_artifact_present": False,
        "java_runtime_pinned": False,
        "device_present": False,
        "license_approved": False,
        "media3_semantics_verified": False,
        "measured_rate_present": False,
        "pitch_measurement_present": False,
        "buffer_measurement_present": False,
        "device_timing_present": False,
        "speech_preservation_present": False,
        "listening_present": False,
        "local_control_is_candidate": False,
        "native_c_is_candidate": False,
        "missing_result_promoted": False,
    }


def native_sonic_c_provenance() -> Dict[str, Any]:
    present = all((WORKSPACE / name).is_file() for name in NATIVE_SONIC_PINS)
    digests_match = present and all(
        digest_file(WORKSPACE / name) == expected
        for name, expected in NATIVE_SONIC_PINS.items()
    )
    return {
        "present": present,
        "digests_match": digests_match,
        "path": "cpp-library/third_party/sonic",
        "license": "Apache-2.0",
        "files": dict(NATIVE_SONIC_PINS),
        "exact_media3_java_port": False,
        "admitted_for_candidate": False,
        "used_for_qualification": False,
        "bytes_read_beyond_hash": False,
        "executed": False,
        "note": (
            "Apache-2.0 Sonic C original by Bill Cox, present as a read-only "
            "upstream provenance artifact. It is not the Media3 Java port, "
            "has no Media3 Android integration or parity result, and is never "
            "admitted for candidate qualification."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Absence audit
# ---------------------------------------------------------------------------

def _probe_checked_paths() -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    for key in CHECKED_PATHS:
        base, relative = key.split(":", 1)
        root = WORKSPACE if base == "workspace" else WORKTREE
        result[key] = (root / relative).exists()
    return result


def _probe_host() -> Dict[str, bool]:
    result: Dict[str, bool] = {}
    for key in HOST_PATH_PROBES:
        relative = key.split(":", 1)[1]
        result[key] = (Path.home() / relative).exists()
    return result


def absence_audit() -> Dict[str, Any]:
    checked = _probe_checked_paths()
    host = _probe_host()
    all_absent = not any(checked.values()) and not any(host.values())
    return {
        "all_candidate_artifacts_absent": all_absent,
        "media3_source_present": False,
        "media3_artifact_present": False,
        "gradle_or_maven_artifact_present": False,
        "android_runtime_present": False,
        "pinned_runtime_present": False,
        "checked_paths": checked,
        "host_probes": host,
        "note": (
            "Fixed, non-recursive probes only. No Media3 source, artifact, "
            "cache, runtime, device or emulator is present."
        ),
        "qualifies": False,
    }


def artifact_assessment() -> Dict[str, Any]:
    audit = absence_audit()
    all_absent = audit["all_candidate_artifacts_absent"]
    if not all_absent:
        raise ReferenceError("required_artifact_appeared")
    return {
        "all_required_absent": True,
        "media3_source_present": False,
        "media3_artifact_present": False,
        "java_source_present": False,
        "gradle_or_maven_artifact_present": False,
        "android_runtime_present": False,
        "pinned_runtime_present": False,
        "device_or_emulator_present": False,
        "license_approved": False,
        "measured_evidence_present": False,
        "listening_present": False,
        "adapter_present": False,
        "package_assets_present": False,
        "checked_paths": audit["checked_paths"],
        "host_probes": audit["host_probes"],
        "conclusion": (
            "BLOCKED: no Media3 SonicAudioProcessor or Sonic.java source, "
            "Media3 AAR/JAR, Gradle/Maven cache, Java build, Android runtime, "
            "device or emulator, licence/rights approval, corpus, measurement "
            "or listening result exists locally; nothing was downloaded, "
            "copied or executed."
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller-supplied qualified Media3 bundle (shape and hash only)
# ---------------------------------------------------------------------------

def valid_manifest() -> Dict[str, Any]:
    return {
        "artifact_id": "androidx-media3-sonic-audioprocessor",
        "caller_attestation": CALLER_ATTESTATION,
        "source_revision": "0" * 40,
        "sonic_audio_processor_path": (
            "/caller/media3/libraries/common/src/main/java/androidx/"
            "media3/common/audio/SonicAudioProcessor.java"
        ),
        "sonic_audio_processor_sha256": "1" * 64,
        "sonic_pitch_shifter_path": (
            "/caller/media3/libraries/common/src/main/java/androidx/"
            "media3/common/audio/Sonic.java"
        ),
        "sonic_pitch_shifter_sha256": "2" * 64,
        "media3_license_path": "/caller/licenses/media3/LICENSE",
        "media3_license_sha256": "3" * 64,
        "build_toolchain_lock_path": "/caller/media3/gradle/toolchain.lock",
        "build_toolchain_lock_sha256": "4" * 64,
        "runtime_manifest_path": "/caller/evidence/runtime-manifest.json",
        "runtime_manifest_sha256": "5" * 64,
        "rights_approval_path": "/caller/rights/media3-approval.txt",
        "rights_approval_sha256": "6" * 64,
        "measurement_manifest_path": "/caller/evidence/measurements.json",
        "measurement_manifest_sha256": "7" * 64,
        "listening_protocol_id": "media3-sonic-listening-v1",
        "terms_accepted": True,
    }


def _validate_manifest_path(key: str, value: Any) -> str:
    if not isinstance(value, str) or not value.startswith("/"):
        raise ReferenceError("manifest_path_not_absolute:" + key)
    if not value.isascii():
        raise ReferenceError("manifest_path_not_ascii:" + key)
    if "//" in value or value.endswith("/"):
        raise ReferenceError("manifest_path_not_normalized:" + key)
    parts = value.split("/")[1:]
    if any(part in ("", ".", "..") for part in parts):
        raise ReferenceError("manifest_path_traversal:" + key)
    return value


def parse_manifest(document: Any) -> Dict[str, Any]:
    if not isinstance(document, dict):
        raise ReferenceError("manifest_not_an_object")
    missing = [key for key in MANIFEST_FIELDS if key not in document]
    if missing:
        raise ReferenceError("manifest_missing_fields:" + ",".join(missing))
    extra = sorted(set(document) - set(MANIFEST_FIELDS))
    if extra:
        raise ReferenceError("manifest_extra_fields:" + ",".join(extra))
    if not isinstance(document["artifact_id"], str) \
            or not ID_RE.match(document["artifact_id"]):
        raise ReferenceError("manifest_artifact_id_invalid")
    if not isinstance(document["source_revision"], str) \
            or not REVISION_RE.match(document["source_revision"]):
        raise ReferenceError("manifest_source_revision_invalid")

    seen: Dict[str, str] = {}
    for key in MANIFEST_PATH_FIELDS:
        value = _validate_manifest_path(key, document[key])
        if value in seen:
            raise ReferenceError(
                "manifest_paths_not_unique:" + seen[value] + ":" + key)
        seen[value] = key
    if not document["sonic_audio_processor_path"].endswith(
            "/SonicAudioProcessor.java"):
        raise ReferenceError("manifest_processor_basename_invalid")
    if not document["sonic_pitch_shifter_path"].endswith("/Sonic.java"):
        raise ReferenceError("manifest_pitch_shifter_basename_invalid")
    for key in MANIFEST_HASH_FIELDS:
        value = document[key]
        if not isinstance(value, str) or not HASH_RE.match(value):
            raise ReferenceError("manifest_hash_invalid:" + key)
    if document["sonic_audio_processor_sha256"] == \
            document["sonic_pitch_shifter_sha256"]:
        raise ReferenceError("manifest_source_files_not_distinct")
    if document["terms_accepted"] is not True:
        raise ReferenceError("manifest_terms_not_accepted")
    if document["caller_attestation"] != CALLER_ATTESTATION:
        raise ReferenceError("manifest_attestation_invalid")
    listening = document["listening_protocol_id"]
    if not isinstance(listening, str) or not ID_RE.match(listening) \
            or listening == "not_established" \
            or listening in ("device_timing", "media3_semantics"):
        raise ReferenceError("manifest_listening_protocol_invalid")

    normalized = dict(document)
    normalized["files_verified"] = False
    normalized["official_identity"] = False
    normalized["qualifies"] = False
    return normalized


def verify_manifest_files(document: Dict[str, Any]) -> Dict[str, Any]:
    """Hash caller-owned bytes only; never parse, import, link or execute."""
    results: Dict[str, bool] = {}
    for key in MANIFEST_PATH_FIELDS:
        path = Path(document[key])
        if not path.is_file():
            raise ReferenceError("manifest_file_missing:" + key)
        digest = digest_file(path)
        expected_key = key[:-5] + "_sha256"
        if digest != document.get(expected_key):
            raise ReferenceError("manifest_file_digest_mismatch:" + key)
        results[key] = True
    return {
        "files_verified": True,
        "official_identity": False,
        "all_match": all(results.values()),
        "checked_files": results,
        "executed": False,
        "loaded": False,
        "qualifies": False,
    }


def manifest_contract() -> Dict[str, Any]:
    return {
        "contract_id": (
            "media3-sonicaudioprocessor-java-port-of-sonic/"
            "caller-supplied-qualified-media3-bundle/0.1"
        ),
        "required_fields": list(MANIFEST_FIELDS),
        "checksum_policy": (
            "full_sha256_required_for_sonic_audio_processor_sonic_pitch_"
            "shifter_media3_license_build_toolchain_lock_runtime_manifest_"
            "rights_approval_and_measurement_manifest"
        ),
        "caller_owned": True,
        "vendored": False,
        "loaded": False,
        "executed": False,
        "official_identity_requires_rights_review": True,
        "source_files_must_be_distinct": True,
        "device_timing_and_listening_must_be_separate": True,
        "files_behavior": (
            "hash caller-owned bytes and geometry only; never parse, import, "
            "link or execute the Java source, AAR/JAR, runtime, corpus or "
            "measurement manifest"
        ),
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Adverse and failure controls
# ---------------------------------------------------------------------------

def _mutated_request(key: str, value: Any) -> Dict[str, Any]:
    request = valid_request()
    request[key] = value
    return request


def _request_without(key: str) -> Dict[str, Any]:
    request = valid_request()
    del request[key]
    return request


def _adverse_vectors() -> List[Tuple[str, Any, str]]:
    return [
        ("nan_speed_numerator",
         _mutated_request("speed_numerator", float("nan")),
         "request_speed_numerator_not_integer"),
        ("infinity_speed_denominator",
         _mutated_request("speed_denominator", float("inf")),
         "request_speed_denominator_not_integer"),
        ("boolean_speed_numerator",
         _mutated_request("speed_numerator", True),
         "request_speed_numerator_not_integer"),
        ("string_speed_numerator",
         _mutated_request("speed_numerator", "5"),
         "request_speed_numerator_not_integer"),
        ("zero_speed_denominator",
         _mutated_request("speed_denominator", 0),
         "request_speed_denominator_not_positive"),
        ("negative_speed_numerator",
         _mutated_request("speed_numerator", -5),
         "request_speed_numerator_not_positive"),
        ("negative_speed_denominator",
         _mutated_request("speed_denominator", -4),
         "request_speed_denominator_not_positive"),
        ("speed_below_floor",
         _mutated_request("speed_numerator", 1),
         "request_speed_below_declared_floor"),
        ("speed_above_ceiling",
         valid_request() | {"speed_numerator": 2, "speed_denominator": 1},
         "request_speed_above_declared_ceiling"),
        ("pitch_not_unity",
         valid_request() | {"pitch_numerator": 6, "pitch_denominator": 5},
         "request_pitch_not_unity"),
        ("zero_pitch_denominator",
         _mutated_request("pitch_denominator", 0),
         "request_pitch_denominator_not_positive"),
        ("negative_pitch_numerator",
         _mutated_request("pitch_numerator", -1),
         "request_pitch_numerator_not_positive"),
        ("nonfinite_pitch_numerator",
         _mutated_request("pitch_numerator", float("inf")),
         "request_pitch_numerator_not_integer"),
        ("boolean_sample_rate",
         _mutated_request("sample_rate_hz", True),
         "request_sample_rate_hz_not_integer"),
        ("float_sample_rate",
         _mutated_request("sample_rate_hz", 16000.0),
         "request_sample_rate_hz_not_integer"),
        ("wrong_sample_rate",
         _mutated_request("sample_rate_hz", 48000),
         "request_sample_rate_not_supported"),
        ("boolean_channels",
         _mutated_request("channels", True),
         "request_channels_not_integer"),
        ("wrong_channels",
         _mutated_request("channels", 2),
         "request_channels_not_supported"),
        ("boolean_frame_samples",
         _mutated_request("frame_samples", True),
         "request_frame_samples_not_integer"),
        ("wrong_frame_samples",
         _mutated_request("frame_samples", 320),
         "request_frame_samples_not_supported"),
        ("candidate_claim",
         _mutated_request("is_candidate_result", True),
         "request_candidate_claim"),
        ("candidate_claim_string",
         _mutated_request("is_candidate_result", "false"),
         "request_candidate_claim"),
        ("wrong_schema_id",
         _mutated_request("schema_id", "audio-sdk/other/0.1"),
         "request_schema_id_invalid"),
        ("empty_request_id",
         _mutated_request("request_id", ""),
         "request_id_invalid"),
        ("missing_field", _request_without("sample_rate_hz"),
         "request_missing_fields"),
        ("extra_field", _mutated_request("extra", 1),
         "request_extra_fields"),
        ("non_object_request", ["not", "a", "request"],
         "request_not_an_object"),
        ("empty_request", {}, "request_missing_fields"),
    ]


def adverse_results() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for result_id, vector, expected in _adverse_vectors():
        try:
            parse_rate_request(vector)
        except ReferenceError as error:
            actual = str(error)
            rows.append({
                "result_id": result_id,
                "status": "rejected",
                "expected_error": expected,
                "actual_error": actual,
                "matches_expected": actual == expected
                              or actual.startswith(expected + ":"),
                "qualifies": False,
            })
        else:
            rows.append({
                "result_id": result_id,
                "status": "accepted_unexpectedly",
                "expected_error": expected,
                "actual_error": None,
                "matches_expected": False,
                "qualifies": False,
            })
    return rows


def _mapping_vectors() -> List[Tuple[str, Any, Any, str]]:
    return [
        ("nonfinite_speed", float("nan"), 160, "mapping_speed_not_fraction"),
        ("boolean_speed", True, 160, "mapping_speed_not_fraction"),
        ("zero_speed", Fraction(0, 1), 160, "mapping_speed_not_positive"),
        ("below_floor_speed", Fraction(1, 2), 160,
         "mapping_speed_below_declared_floor"),
        ("above_ceiling_speed", Fraction(2, 1), 160,
         "mapping_speed_above_declared_ceiling"),
        ("boolean_source_frames", Fraction(1, 1), True,
         "mapping_source_frames_not_integer"),
        ("negative_source_frames", Fraction(1, 1), -1,
         "mapping_source_frames_negative"),
        ("huge_source_frames", Fraction(1, 1), MAX_SOURCE_FRAMES + 1,
         "mapping_source_frames_too_large"),
    ]


def mapping_adverse_results() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for result_id, speed, source_frames, expected in _mapping_vectors():
        try:
            map_source_to_output(speed, source_frames)
        except ReferenceError as error:
            actual = str(error)
            rows.append({
                "result_id": result_id,
                "status": "rejected",
                "expected_error": expected,
                "actual_error": actual,
                "matches_expected": actual == expected
                              or actual.startswith(expected + ":"),
                "qualifies": False,
            })
        else:
            rows.append({
                "result_id": result_id,
                "status": "accepted_unexpectedly",
                "expected_error": expected,
                "actual_error": None,
                "matches_expected": False,
                "qualifies": False,
            })
    return rows


def _manifest_controls() -> List[Tuple[str, Any, str]]:
    def run(control_id: str, document: Any, expected: str) -> Tuple:
        return (control_id, document, expected)

    cases: List[Tuple[str, Any, str]] = [
        run("valid_shape", valid_manifest(), ""),
        run("missing_artifact_id",
            {k: v for k, v in valid_manifest().items()
             if k != "artifact_id"}, "manifest_missing_fields"),
        run("extra_field", valid_manifest() | {"extra": 1},
            "manifest_extra_fields"),
        run("uppercase_revision",
            valid_manifest() | {"source_revision": "A" * 40},
            "manifest_source_revision_invalid"),
        run("short_revision",
            valid_manifest() | {"source_revision": "0" * 39},
            "manifest_source_revision_invalid"),
        run("wrong_processor_basename",
            valid_manifest() | {
                "sonic_audio_processor_path":
                "/caller/media3/SonicAudioProcessor.txt"},
            "manifest_processor_basename_invalid"),
        run("wrong_pitch_shifter_basename",
            valid_manifest() | {
                "sonic_pitch_shifter_path":
                "/caller/media3/SonicAudioProcessor.java"},
            "manifest_pitch_shifter_basename_invalid"),
        run("relative_processor_path",
            valid_manifest() | {
                "sonic_audio_processor_path":
                "media3/SonicAudioProcessor.java"},
            "manifest_path_not_absolute"),
        run("parent_traversal",
            valid_manifest() | {
                "runtime_manifest_path": "/caller/../runtime.json"},
            "manifest_path_traversal"),
        run("duplicate_paths",
            valid_manifest() | {
                "media3_license_path":
                valid_manifest()["sonic_audio_processor_path"]},
            "manifest_paths_not_unique"),
        run("uppercase_hash",
            valid_manifest() | {"sonic_audio_processor_sha256": "E" * 64},
            "manifest_hash_invalid"),
        run("bad_hash_length",
            valid_manifest() | {"sonic_pitch_shifter_sha256": "9" * 63},
            "manifest_hash_invalid"),
        run("source_files_not_distinct",
            valid_manifest() | {
                "sonic_pitch_shifter_sha256":
                valid_manifest()["sonic_audio_processor_sha256"]},
            "manifest_source_files_not_distinct"),
        run("terms_not_accepted",
            valid_manifest() | {"terms_accepted": False},
            "manifest_terms_not_accepted"),
        run("wrong_attestation",
            valid_manifest() | {"caller_attestation": "trust_me"},
            "manifest_attestation_invalid"),
        run("empty_artifact_id",
            valid_manifest() | {"artifact_id": ""},
            "manifest_artifact_id_invalid"),
        run("empty_listening_protocol",
            valid_manifest() | {"listening_protocol_id": ""},
            "manifest_listening_protocol_invalid"),
        run("listening_not_established",
            valid_manifest() | {"listening_protocol_id": "not_established"},
            "manifest_listening_protocol_invalid"),
        run("non_ascii_path",
            valid_manifest() | {
                "media3_license_path": "/caller/licenses/m\u00e9dia3/LICENSE"},
            "manifest_path_not_ascii:media3_license_path"),
    ]
    return cases


def manifest_controls() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for control_id, document, expected in _manifest_controls():
        try:
            parsed = parse_manifest(document)
        except ReferenceError as error:
            actual = str(error)
            rows.append({
                "control_id": control_id,
                "accepted": False,
                "expected_error": expected,
                "actual_error": actual,
                "matches_expected": bool(expected)
                              and (actual == expected
                                   or actual.startswith(expected + ":")),
                "files_verified": False,
                "official_identity": False,
                "qualifies": False,
            })
        else:
            rows.append({
                "control_id": control_id,
                "accepted": True,
                "expected_error": None,
                "actual_error": None,
                "matches_expected": control_id == "valid_shape",
                "files_verified": parsed["files_verified"],
                "official_identity": parsed["official_identity"],
                "qualifies": False,
            })
    return rows


def failure_controls(report: Dict[str, Any]) -> Dict[str, Any]:
    def rejects(text: str) -> bool:
        try:
            parse_strict_json_text(text)
        except ValueError:
            return True
        return False

    checks = {
        "strict_json_rejects_nan":
            rejects('{"value": NaN}'),
        "strict_json_rejects_infinity":
            rejects('{"value": Infinity}'),
        "strict_json_rejects_duplicate_keys":
            rejects('{"a": 1, "a": 2}'),
        "request_rejections_are_explicit":
            all(row["status"] == "rejected"
                and row["matches_expected"] is True
                for row in report["adverse_results"]),
        "mapping_rejections_are_explicit":
            all(row["status"] == "rejected"
                and row["matches_expected"] is True
                for row in report["mapping_adverse_results"]),
        "manifest_rejections_are_explicit":
            all(row["accepted"] is False and row["matches_expected"] is True
                for row in report["manifest_controls"][1:]),
        "no_rejected_value_is_scored":
            all(row["qualifies"] is False
                for row in report["adverse_results"]),
        "no_missing_value_is_promoted":
            all(row["value"] is None and row["qualifies"] is False
                for row in report["missing_results"]),
        "all_release_gates_blocked":
            len(report["release_gates"]) == 8
            and all(gate["status"] == "blocked"
                    and gate["evidence"] is None
                    and gate["qualifies"] is False
                    for gate in report["release_gates"]),
        "all_qualification_slots_null":
            len(report["qualification_slots"]) == 9
            and all(slot["value"] is None
                    and slot["qualifies"] is False
                    for slot in report["qualification_slots"].values()),
        "all_profile_items_nonqualifying":
            all(item["qualifies"] is False
                for item in report["acceptance_profile"]["items"]),
        "all_adverse_nonqualifying":
            all(row["qualifies"] is False
                for row in report["adverse_results"]),
        "all_manifest_controls_nonqualifying":
            all(row["qualifies"] is False
                for row in report["manifest_controls"]),
        "all_required_artifacts_absent":
            all(item["present"] is False
                for item in report["required_artifacts"]),
        "media3_source_absent":
            report["artifact_assessment"]["media3_source_present"] is False,
        "media3_artifact_absent":
            report["artifact_assessment"]["media3_artifact_present"] is False,
        "pinned_runtime_absent":
            report["artifact_assessment"]["pinned_runtime_present"] is False,
        "device_timing_absent":
            report["control_envelope"]["device_timing"]["output_latency_ms"]
            is None,
        "pitch_measurement_absent":
            report["control_envelope"]["pitch_measurement"]["pitch_error_cents"]
            is None,
        "buffer_measurement_absent":
            report["control_envelope"]["playback_buffer"]["fill_ms"] is None,
        "speech_preservation_absent":
            report["control_envelope"]["speech_preservation"][
                "preservation_metric"] is None,
        "listening_absent":
            report["control_envelope"]["listening"]["protocol_id"] is None,
        "candidate_claim_rejected":
            any(row["result_id"] == "candidate_claim"
                and row["status"] == "rejected"
                for row in report["adverse_results"]),
        "nonfinite_rejected":
            any(row["result_id"] == "nan_speed_numerator"
                and row["status"] == "rejected"
                for row in report["adverse_results"]),
        "source_files_identity_controls":
            report["manifest_contract"][
                "source_files_must_be_distinct"] is True
            and any(row["control_id"] == "source_files_not_distinct"
                    and row["accepted"] is False
                    for row in report["manifest_controls"]),
        "native_c_is_not_media3":
            report["native_sonic_c_provenance"][
                "exact_media3_java_port"] is False
            and report["native_sonic_c_provenance"][
                "used_for_qualification"] is False,
        "no_qualifying_result":
            not _contains_qualifying(report),
    }
    return {
        "all_explicit": all(checks.values()),
        "checks": checks,
        "rejected_request_documents": len(report["adverse_results"]),
        "rejected_mapping_vectors": len(report["mapping_adverse_results"]),
        "rejected_manifest_documents": len(report["manifest_controls"]) - 1,
        "blocked_release_gates": len(report["release_gates"]),
        "qualifies": False,
    }


def _contains_qualifying(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "qualifies" and item is not False:
                return True
            if _contains_qualifying(item):
                return True
    elif isinstance(value, list):
        for item in value:
            if _contains_qualifying(item):
                return True
    return False


# ---------------------------------------------------------------------------
# Report sections
# ---------------------------------------------------------------------------

def acceptance_profile() -> Dict[str, Any]:
    items = []
    for item_id, status, evidence in PROFILE_ITEMS:
        items.append({
            "item": item_id,
            "status": status,
            "evidence": evidence,
            "qualifies": False,
        })
    return {
        "profile": PROFILE,
        "items": items,
        "all_qualify": False,
        "missing_result_promoted": False,
        "qualifies": False,
    }


def missing_results() -> List[Dict[str, Any]]:
    return [
        {
            "result_id": result_id,
            "status": "blocked",
            "value": None,
            "reason": reason,
            "qualifies": False,
        }
        for result_id, reason in MISSING_RESULTS
    ]


def qualification_slots() -> Dict[str, Dict[str, Any]]:
    return {
        slot: {"value": None, "source": "blocked", "qualifies": False}
        for slot in QUALIFICATION_SLOTS
    }


def observed_provenance() -> Dict[str, Any]:
    rows = [
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 79,
            "finding": (
                "Apache-2.0 source; useful as a reference and as the "
                "platform-native path."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 309,
            "finding": "Section 4.2 is titled Media3 SonicAudioProcessor.",
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 311,
            "finding": (
                "Documentation link only; no source revision or artifact."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 312,
            "finding": (
                "Apache-2.0 Java implementation of Sonic, used by ExoPlayer; "
                "supports speed and pitch."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 315,
            "finding": (
                "Java/Kotlin, not our C++ library; Android-only; "
                "AudioTrack.setPlaybackParams is the platform alternative."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 26,
            "finding": (
                "A time stretcher changes frame count and cannot be a "
                "fixed-frame Stage; it needs a buffered playback module."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 37,
            "finding": "Output frames per input frame = 1 / r.",
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 486,
            "finding": (
                "First-product speech clamp 0.75-1.5x is design guidance, "
                "not a Media3 range."
            ),
        },
        {
            "source":
            "cpp-library/pipeline-validation/playback-speed-candidates.md",
            "line": 500,
            "finding": (
                "Apache-2.0 permits commercial closed-source use with notice "
                "and a patent grant."
            ),
        },
    ]
    for row in rows:
        row["is_source_reported"] = True
        row["is_measurement"] = False
        row["is_human_rating"] = False
        row["reproduced_here"] = False
        row["qualifies"] = False
    return {
        "documented_context": rows,
        "reproduced_here": False,
        "device_timing_is_listening": False,
        "native_c_is_media3_java": False,
        "qualifies": False,
    }


def ranking_payload() -> Dict[str, Any]:
    return {
        "order": "not_ranked",
        "recommendation": None,
        "reason": (
            "No qualified Media3 runtime, measurement or listening result; "
            "ranking requires measured evidence."
        ),
        "qualifies": False,
    }


def build_report_core() -> Dict[str, Any]:
    report = {
        SPDX_COPYRIGHT_KEY: "2026 Tsakanyan Hovhannes",
        SPDX_LICENSE_KEY: "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": qualification_payload(),
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "control_envelope": control_envelope_payload(),
        "manifest_controls": manifest_controls(),
        "adverse_results": adverse_results(),
        "mapping_adverse_results": mapping_adverse_results(),
        "missing_results": missing_results(),
        "qualification_slots": qualification_slots(),
        "acceptance_profile": acceptance_profile(),
        "observed_provenance": observed_provenance(),
        "artifact_assessment": artifact_assessment(),
        "absence_audit": absence_audit(),
        "native_sonic_c_provenance": native_sonic_c_provenance(),
        "ranking": ranking_payload(),
        "release_gates": RELEASE_GATES,
        "exact_blockers": EXACT_BLOCKERS,
        "non_claims": NON_CLAIMS,
        "reproduction": REPRODUCTION,
    }
    report["failure_controls"] = failure_controls(report)
    return report


def build_report() -> Dict[str, Any]:
    first = build_report_core()
    second = build_report_core()
    third = build_report_core()
    digests = [sha256_bytes(canonical_bytes(item))
               for item in (first, second, third)]
    if len(set(digests)) != 1:
        raise ReferenceError("non_deterministic_report")
    report = dict(first)
    report["regeneration"] = {
        "runs": 3,
        "byte_identical": True,
        "canonical_digests": digests,
        "mode": "three_in_process_canonical_builds_plus_cold_start_verify",
    }
    return report


def report_payload() -> Dict[str, Any]:
    return build_report()


def render_report() -> Tuple[bytes, str, str]:
    report = build_report()
    text, file_digest = canonical_report(report)
    payload = (text + "\n").encode("utf-8")
    canonical_digest = sha256_bytes(canonical_bytes(report))
    return payload, file_digest, canonical_digest


def _local_artifact_names() -> List[str]:
    names: List[str] = []
    for path in sorted(ROOT.rglob("*")):
        if not path.is_file():
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        names.append(path.relative_to(ROOT).as_posix())
    return names


def contract_payload() -> Dict[str, Any]:
    pins: Dict[str, str] = {}
    for name in _local_artifact_names():
        if name in ("contract.json", "SOURCES.sha256"):
            continue
        pins[name] = digest_file(ROOT / name)
    return {
        SPDX_COPYRIGHT_KEY: "2026 Tsakanyan Hovhannes",
        SPDX_LICENSE_KEY: "Apache-2.0",
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "title": TITLE,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "qualification": qualification_payload(),
        "task_row": TASK_ROW_IDENTITY,
        "mutable_provenance": MUTABLE_PROVENANCE,
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "scope": SCOPE,
        "public_surface": PUBLIC_SURFACE,
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "manifest_contract": manifest_contract(),
        "required_artifacts": REQUIRED_ARTIFACTS,
        "release_gates": RELEASE_GATES,
        "absence_audit": absence_audit(),
        "native_sonic_c_provenance": native_sonic_c_provenance(),
        "exact_blockers": EXACT_BLOCKERS,
        "artifact_pins": pins,
        "local_files": list(LOCAL_FILES),
        "reproduction": REPRODUCTION,
        "non_claims": NON_CLAIMS,
    }


def inspect_payload() -> Dict[str, Any]:
    envelope = control_envelope_payload()
    audit = absence_audit()
    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "profile": PROFILE,
        "status": STATUS,
        "completeness": COMPLETENESS,
        "decision": DECISION,
        "proposal_only": PROPOSAL_ONLY,
        "qualification": qualification_payload(),
        "candidate_record": candidate_record(),
        "declared_contract": declared_contract(),
        "required_artifacts": [
            {"id": item["id"], "present": item["present"]}
            for item in REQUIRED_ARTIFACTS
        ],
        "control_envelope": {
            "identity_output_samples": envelope["identity"]["output_samples"],
            "identity_error_samples":
                envelope["identity"]["duration_error_samples_exact"],
            "rates": [
                {
                    "speed": row["speed"],
                    "output_samples": row["output_samples"],
                    "duration_error_samples_exact":
                        row["duration_error_samples_exact"],
                }
                for row in envelope["rates"]
            ],
            "long_run_output_samples":
                envelope["long_run"]["output_frames"],
            "long_run_chunk_sum_matches_total":
                envelope["long_run"]["chunk_sum_matches_total"],
        },
        "absence_audit": {
            "all_candidate_artifacts_absent":
                audit["all_candidate_artifacts_absent"],
            "checked_paths": audit["checked_paths"],
            "host_probes": audit["host_probes"],
        },
        "native_sonic_c_provenance": {
            "present": native_sonic_c_provenance()["present"],
            "exact_media3_java_port": False,
            "admitted_for_candidate": False,
            "used_for_qualification": False,
        },
        "ranking": ranking_payload(),
        "release_gates": [
            {"id": gate["id"], "status": gate["status"]}
            for gate in RELEASE_GATES
        ],
        "qualifies": False,
    }
