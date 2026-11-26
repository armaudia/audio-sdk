# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for
SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP.

Standard-library only and deterministic. This module never loads AVFAudio,
instantiates an Audio Unit, starts AVAudioEngine, reads audio, or uses the
network. It pins the provenance that is present, proves that the exact
licensed Apple implementation/runtime, its terms, a pinned offline render
host and a rights-cleared rate cohort are absent, and reproduces only the
declared rate/pitch/overlap arithmetic and deterministic synthetic controls.
None of it is runtime evidence and none of it can qualify.

The pinned candidate note records ``AVAudioUnitTimePitch`` (``rate``,
``pitch``, ``overlap``) as an OS platform API, states that the source is not
available and that behaviour can change between OS versions. No Apple OS
runtime manifest, Audio Unit host, implementation source, licence bundle,
render trace or playback cohort exists in the project workspace. Nothing is
fabricated or downloaded.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import struct
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
from typing import Any

TASK = "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP"
COMPONENT_ID = "avaudiounittimepitch-rate-pitch-overlap"
TASK_TITLE = "AVAudioUnitTimePitch (rate, pitch, overlap)"
CONTRACT_ID = "audio-sdk/avaudiounittimepitch-rate-pitch-overlap/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
SCHEMA_MANIFEST_ID = (
    "audio-sdk/avaudiounittimepitch-rate-pitch-overlap/qualification/0.1")
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "feasibility"
BASE_COMMIT = "aacd6b19b51d4ae2d125ed40488a0e5a8357ec82"
BRANCH = "swarm/SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP"
REVIEWER = "reviewer-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP"
TASK_PREFIX = (
    "docs/task-evidence/avaudiounittimepitch-rate-pitch-overlap/")
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

CANDIDATE_NOTE = (
    "cpp-library/pipeline-validation/playback-speed-candidates.md")
CANDIDATE_MARKER = (
    "`AVAudioUnitTimePitch` (`rate`, `pitch`, `overlap`)")
CANDIDATE_SECTION_MARKER = "### 4.1 Apple"
CANDIDATE_LINK_MARKER = (
    "developer.apple.com/documentation/avfaudio/avaudiounittimepitch")

SOURCE_PINS: dict[str, str] = {
    "audio-benchmark-platform/plan/INVENTORY.json":
        "46d09945deb235cdd948eb48f827aa15fc24ddc8c902668810f7718fc00f889c",
    "audio-benchmark-platform/plan/audio-sdk/README.md":
        "f72d6b50a61e7ff469cda0480e8f5ffa93edbfe747a45624db5faad54847be06",
    "audio-benchmark-platform/plan/swarm/VERIFICATION.md":
        "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910",
    CANDIDATE_NOTE:
        "661a471ad50e3335b18fdb6d8664f6fda0534ad37196fb9e3f58ff61c58f34b3",
}

BOUNDARY_PINS: dict[str, str] = {
    "CONTRACTS.md":
        "f6fdd18f9d5361ab9592015dce1db9733e18674b15bf0c3f657add1416653c69",
    "api/include/audio_sdk/provider_v0.h":
        "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
    "api/include/audio_sdk/session_v0.h":
        "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
    "CMakeLists.txt":
        "af72dba58c79637fb006720aa1a6f9dd3bad3ae1f70520b7151a1f260c659d04",
    "REUSE.toml":
        "c6f61bc93dd65da80edd41b69527e401b43a7437a31e8adaf97cc6f4ac9490f8",
    ".github/workflows/ci.yml":
        "ba8cc6cdb85eb69beacac9eefecf6875eb896c101fe573e7730733f56eeb9415",
    "README.md":
        "4f6171cb0184ebab76385cbfc1307040ab301f7337a39ca0829bf4827db73c35",
}

SIBLING_PINS: dict[str, str] = {
    "docs/task-evidence/apple-and-browser-runtime-qualification/README.md":
        "5f86e98fa15c1de6ba2e6ed4690315ced2340dfb6c1b7a254e8907365cd97dd1",
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/report.json":
        "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4",
    "docs/task-evidence/buffer-occupancy-controller/report.json":
        "9dc73683b42a47801efcd71449b7d93fbd40a490beae54c46cc29680ebead47c",
    "docs/task-evidence/coreaudio-audiounit-duplex-host/capture.json":
        "2cab2f81fdd03430444617ccddf87095d92f11c90a73f6d91e8ce7974d0e58bc",
    "docs/task-evidence/coreaudio-audiounit-duplex-host/render.json":
        "249e26185bd1815af6dfff70d2a3fea7a4bfa8596d9a15f8f105d6fadb912d44",
    "docs/task-evidence/d1-whole-clip-duration-planner/fixtures/report.json":
        "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98",
    "docs/task-evidence/granular-tsm/report.json":
        "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138",
    "docs/task-evidence/libsamplerate/report.json":
        "c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc",
    "docs/task-evidence/ola-sola/report.json":
        "90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93",
    "docs/task-evidence/phase-vocoder-baseline/report.json":
        "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7",
    "docs/task-evidence/rubber-band-r3-offline/report.json":
        "b9dda54f2ae86a200b1cfd251f56abb4f9d741ee28778145544650ea38fb10db",
    "docs/task-evidence/signalsmith-stretch/report.json":
        "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231",
    "docs/task-evidence/survey-trn-02/report.json":
        "a594cd9e0c1c638835e11263c84b147b592ac1f344f0e83da4480ef310703f3a",
    "docs/task-evidence/vosk-small-en-us-0-15-playback-gate/report.json":
        "57f355f51582c131812172e779ac8a6e3638491542c8e4e44efc46fd69cc2cc2",
}

LOCAL_PIN_FILES = (
    "README.md",
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

PROFILE_PHRASES = (
    "source/output mapping", "duration", "pitch", "transient audibility",
    "playback buffering", "1×", "rate changes", "unfamiliar speech", "music",
    "silence", "rebuffer", "drift", "final partial window", "speech preservation",
    "source timestamps",
)

FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".gguf", ".lib", ".m4a",
    ".mdl", ".model", ".mp3", ".mp4", ".npy", ".npz", ".o", ".onnx", ".opus",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wav", ".wasm", ".weights",
}

HERE = Path(__file__).resolve().parent
WORKTREE = HERE.parents[2]
AUDIO_ROOT = Path(
    os.environ.get("AUDIOML_ROOT", str(WORKTREE.parents[2]))).resolve()

FRAME_SAMPLES = 160
CONTROL_KINDS = (
    "identity_1x", "rate_change", "pitch_shift", "overlap_change",
    "final_partial_window", "rebuffer")
RUNTIME_OSES = ("macos", "ios")
HOST_ARCHES = ("arm64", "x86_64")
FRAMEWORKS = ("AVFAudio",)
AUDIO_UNIT_HOSTS = ("avaudioengine-offline-manual-rendering",)
AU_TYPES = ("aufx",)
AU_SUBTYPES = ("tpit",)
AU_MANUFACTURERS = ("appl",)
IMPLEMENTATION_LICENSES = ("Apple-SDK-License", "Proprietary-OS-Component")
AUDIO_SAMPLE_RATES = (8000, 16000, 44100, 48000)
AUDIO_FRAME_SAMPLES = (128, 160, 256, 480, 1024)
AUDIO_CHANNELS = (1, 2)
RATE_MIN = Fraction(1, 32)
RATE_MAX = Fraction(32)
PITCH_CENTS_MIN = -2400
PITCH_CENTS_MAX = 2400
OVERLAP_MIN = Fraction(3)
OVERLAP_MAX = Fraction(32)

MANIFEST_FIELDS = (
    "schema_id", "run_id", "runtime", "implementation", "audio", "mapping",
    "controls", "rights")
RUNTIME_FIELDS = (
    "os", "os_version", "os_build", "host_arch", "framework",
    "framework_sha256", "audio_unit_host", "render_sample_rate_hz", "pinned")
IMPLEMENTATION_FIELDS = (
    "api", "au_type", "au_subtype", "au_manufacturer", "closed_source",
    "license_id", "license_sha256", "spec_sha256")
AUDIO_FIELDS = (
    "fixture_id", "sha256", "sample_rate_hz", "channels", "frame_samples",
    "total_samples")
MAPPING_FIELDS = (
    "rate", "pitch_cents", "overlap", "source_duration_samples",
    "output_duration_samples", "pitch_ratio", "map_contiguous",
    "final_partial_window")
CONTROL_FIELDS = ("id", "kind", "passes")
RIGHTS_FIELDS = (
    "consent_recorded", "platform_terms_reviewed", "output_use_defined",
    "commercial_use_approved", "listening_protocol_approved")

HEX40 = re.compile(r"^[0-9a-f]{40}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
SEMVER = re.compile(r"^(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)$")
OS_BUILD = re.compile(r"^[0-9]{2}[A-Z][0-9]{3,4}[a-z]?$")
FRACTION = re.compile(r"^(0|[1-9][0-9]{0,8})(/([1-9][0-9]{0,8}))?$")

PRESENCE_PROBES = (
    "adapters/apple",
    "adapters/avfaudio",
    "adapters/avfoundation",
    "adapters/avaudioengine",
    "adapters/coreaudio",
    "bindings/apple",
    "bindings/avfaudio",
    "bindings/coreaudio",
    "cpp-library/pipeline-validation/avaudio",
    "cpp-library/pipeline-validation/avfaudio",
    "cpp-library/pipeline-validation/avaudiounittimepitch",
    "data/checkouts/avfaudio",
    "data/checkouts/avfoundation",
    "data/runtimes/macos",
    "data/runtimes/ios",
    "docs/apple",
    "docs/avfaudio",
    "docs/avaudiounittimepitch",
    "research/avaudio",
    "research/avfaudio",
    "research/avaudiounittimepitch",
    "third_party/avfaudio",
    "third_party/avfoundation",
    "third_party/coreaudio",
    "vendor/avfaudio",
    "vendor/avfoundation",
    "vendor/coreaudio",
    "src/apple",
    "src/avfaudio",
)

HOST_PROBES = (
    "data/checkouts/avaudioengine",
    "data/runtimes/avaudioengine",
    "docs/avaudioengine",
    "examples/avaudioengine",
    "tools/avaudioengine",
    "tools/avaudiounittimepitch",
    "tools/coreaudio-host",
)


# ---------------------------------------------------------------------------
# Strict JSON and canonicalization
# ---------------------------------------------------------------------------

def _reject_constant(value: str) -> None:
    raise ValueError("json_nonfinite_constant:" + value)


def _strict_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise ValueError("json_duplicate_key:" + key)
        result[key] = value
    return result


def read_strict_json(path: Path) -> Any:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError as error:
        raise ValueError("json_not_utf8") from error
    try:
        value = json.loads(
            text, object_pairs_hook=_strict_object,
            parse_constant=_reject_constant)
    except json.JSONDecodeError as error:
        raise ValueError("json_malformed:" + str(error)) from error
    _no_floats(value)
    return value


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("float_not_allowed")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("nonstring_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def canonical_bytes(value: Any) -> bytes:
    _no_floats(value)
    return (json.dumps(value, sort_keys=True, separators=(",", ":"),
                       ensure_ascii=True, allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return hashlib.sha256(canonical_bytes(value)).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), hashlib.sha256(payload).hexdigest()


# ---------------------------------------------------------------------------
# Linked-row identity
# ---------------------------------------------------------------------------

def board_row_projection(path: Path) -> dict[str, Any]:
    board = read_strict_json(path)
    rows = board.get("tasks") if isinstance(board, dict) else None
    if not isinstance(rows, list):
        raise ValueError("board_tasks_missing")
    matches = [row for row in rows
               if isinstance(row, dict) and row.get("id") == TASK]
    if len(matches) != 1:
        raise ValueError("board_row_not_unique")
    row = matches[0]
    missing = [field for field in BOARD_ROW_FIELDS if field not in row]
    if missing:
        raise ValueError("board_row_field_missing:" + missing[0])
    return {field: row[field] for field in BOARD_ROW_FIELDS}


def board_row_digest(projection: dict[str, Any]) -> str:
    return object_digest(projection)


LINKED_ROWS = (
    {"task": "SDK-GRANULAR-TSM",
     "role": "merged granular TSM synthetic reference; no Apple AudioUnit evidence",
     "report_sha256":
         "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138"},
    {"task": "SDK-OLA-SOLA",
     "role": "merged OLA/SOLA synthetic reference; no Apple AudioUnit evidence",
     "report_sha256":
         "90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93"},
    {"task": "SDK-SIGNALSMITH-STRETCH",
     "role": "merged Signalsmith stretch reference; not the Apple unit",
     "report_sha256":
         "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231"},
    {"task": "SDK-RUBBER-BAND-R3-OFFLINE",
     "role": "merged Rubber Band offline reference; not the Apple unit",
     "report_sha256":
         "b9dda54f2ae86a200b1cfd251f56abb4f9d741ee28778145544650ea38fb10db"},
    {"task": "SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH",
     "role": "merged browser playbackRate DEFER blocker; no Apple unit evidence",
     "report_sha256":
         "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4"},
    {"task": "SDK-LIBSAMPLERATE",
     "role": "merged varispeed/resampling reference; pitch changes with rate",
     "report_sha256":
         "c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc"},
    {"task": "SDK-PHASE-VOCODER-BASELINE",
     "role": "merged phase-vocoder baseline; no platform unit",
     "report_sha256":
         "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7"},
    {"task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
     "role": "merged synthetic duration planner; no playback runtime",
     "report_sha256":
         "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98"},
    {"task": "SDK-COREAUDIO-AUDIOUNIT-DUPLEX-HOST",
     "role": "merged offline CoreAudio duplex replay fixture; no time-pitch unit",
     "report_sha256": None},
    {"task": "SDK-APPLE-AND-BROWSER-RUNTIME-QUALIFICATION",
     "role": "merged Apple link/probe; no Audio Unit or Core Audio I/O execution",
     "report_sha256": None},
    {"task": "SDK-SURVEY-TRN-02",
     "role": "merged pitch/prosody survey; records the closed platform caveat only",
     "report_sha256":
         "a594cd9e0c1c638835e11263c84b147b592ac1f344f0e83da4480ef310703f3a"},
)


def linked_rows_digest() -> str:
    return object_digest([dict(row) for row in LINKED_ROWS])


# ---------------------------------------------------------------------------
# Source presence, licensing and pins
# ---------------------------------------------------------------------------

def verify_pins() -> tuple[
        dict[str, dict[str, Any]], dict[str, dict[str, Any]],
        dict[str, dict[str, Any]]]:
    def collect(pins: dict[str, str], root: Path,
                label: str) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for relative, expected in sorted(pins.items()):
            path = root / relative
            if not path.is_file():
                raise ValueError(label + "_pin_missing:" + relative)
            actual = sha256_file(path)
            if actual != expected:
                raise ValueError(label + "_pin_mismatch:" + relative)
            result[relative] = {
                "sha256": expected, "actual": actual, "verified": True}
        return result

    return (
        collect(SOURCE_PINS, AUDIO_ROOT, "source"),
        collect(BOUNDARY_PINS, WORKTREE, "boundary"),
        collect(SIBLING_PINS, WORKTREE, "sibling"),
    )


def candidate_note_probe() -> dict[str, Any]:
    path = AUDIO_ROOT / CANDIDATE_NOTE
    empty = {
        "present": False,
        "line": None,
        "link_line": None,
        "section_line": None,
        "statement": None,
        "what_it_is": None,
        "cons": None,
        "rate_range_recorded": False,
        "pitch_unit_recorded": False,
        "overlap_recorded": False,
        "licence_recorded": None,
        "links": [],
        "records_closed_source": False,
        "records_os_variation": False,
        "records_os_platform_licence": False,
        "records_portability_limitation": False,
        "qualifies": False,
    }
    if not path.is_file():
        return empty
    lines = path.read_text(encoding="utf-8").splitlines()
    line = None
    link_line = None
    section_line = None
    statement = None
    what_it_is = None
    cons = None
    licence = None
    links: list[str] = []
    in_section = False
    for index, text in enumerate(lines, start=1):
        if text.startswith(CANDIDATE_SECTION_MARKER):
            section_line = index
            in_section = True
            continue
        if in_section and text.startswith("### "):
            in_section = False
        if line is None and CANDIDATE_MARKER in text:
            line = index
            cells = [cell.strip() for cell in text.strip().strip("|").split("|")]
            if len(cells) >= 5:
                licence = cells[2]
                statement = cells[-1]
        if in_section:
            if what_it_is is None and text.startswith("- **What it is:**"):
                what_it_is = text.split("**What it is:**", 1)[1].strip()
            if cons is None and text.startswith("- **Cons:**"):
                cons = text.split("**Cons:**", 1)[1].strip()
            if CANDIDATE_LINK_MARKER in text:
                link_line = index
                for token in text.split():
                    if token.startswith("<https://") and token.endswith(">"):
                        url = token[1:-1]
                        if url not in links:
                            links.append(url)
    combined = " ".join(part for part in (statement, what_it_is, cons)
                        if part)
    return {
        "present": True,
        "line": line,
        "link_line": link_line,
        "section_line": section_line,
        "statement": statement,
        "what_it_is": what_it_is,
        "cons": cons,
        "rate_range_recorded": bool(
            what_it_is and "0.03125" in what_it_is and "32" in what_it_is),
        "pitch_unit_recorded": bool(
            what_it_is and "pitch" in what_it_is and "cents" in what_it_is),
        "overlap_recorded": bool(what_it_is and "overlap" in what_it_is),
        "licence_recorded": licence,
        "links": links,
        "records_closed_source": (
            "source is not available" in combined
            or "closed implementation" in combined),
        "records_os_variation": (
            "OS versions" in combined or "OS version" in combined),
        "records_os_platform_licence": bool(
            licence and "OS platform" in licence),
        "records_portability_limitation": (
            "cannot be used on Android/Linux/Windows" in combined),
        "qualifies": False,
    }


def _probe_present(relative: str) -> bool:
    return (AUDIO_ROOT / relative).exists()


def source_presence() -> dict[str, Any]:
    note = candidate_note_probe()
    present_probes = [probe for probe in PRESENCE_PROBES
                      if _probe_present(probe)]
    host_probes = [probe for probe in HOST_PROBES
                   if _probe_present(probe)]
    return {
        "probe_scope": (
            "project workspace only; host OS frameworks, SDK installations, "
            "Xcode and user profiles are not inspected or invoked"),
        "presence_probes": list(PRESENCE_PROBES),
        "present_probes": present_probes,
        "host_probes": list(HOST_PROBES),
        "present_host_probes": host_probes,
        "candidate_note_present": note["present"],
        "candidate_note_records_closed_source": note["records_closed_source"],
        "candidate_note_records_os_variation": note["records_os_variation"],
        "candidate_note_is_implementation": False,
        "apple_runtime_manifest_present": False,
        "implementation_source_present": False,
        "spec_text_present": False,
        "audio_unit_host_present": bool(host_probes),
        "framework_source_present": bool(present_probes),
        "licensed_implementation_runtime_present": False,
        "exact_licensed_source_weights_runtime_present": False,
        "rights_cleared_cohort_present": False,
        "measured_render_trace_present": False,
        "listening_record_present": False,
        "device_timing_record_present": False,
        "presence_is_not_admission": True,
        "admitted": False,
        "framework_loaded": False,
        "audio_unit_instantiated": False,
        "audio_engine_launched": False,
        "runtime_imported": False,
        "network_used": False,
        "download_attempted": False,
        "audio_read": False,
        "audio_played": False,
        "pitch_measured": False,
        "overlap_measured": False,
        "qualifies": False,
    }


def license_marker_probe() -> dict[str, Any]:
    presence = source_presence()
    return {
        "apple_platform_terms_present": False,
        "apple_sdk_license_present": False,
        "implementation_source_license_present": False,
        "spec_text_present": presence["spec_text_present"],
        "platform_terms_reviewed": False,
        "apple_sdk_license_reviewed": False,
        "redistribution_approved": False,
        "commercial_use_approved": False,
        "output_use_defined": False,
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Deterministic synthetic controls (never evidence)
# ---------------------------------------------------------------------------

def _exact_int(value: Any, label: str, minimum: int = 0,
               maximum: int | None = None) -> int:
    if type(value) is not int:
        raise ValueError(label + "_not_int")
    if value < minimum:
        raise ValueError(label + "_below_minimum")
    if maximum is not None and value > maximum:
        raise ValueError(label + "_above_maximum")
    return value


def _choice_int(value: Any, label: str,
                choices: tuple[int, ...]) -> int:
    if type(value) is not int:
        raise ValueError(label + "_not_int")
    if value not in choices:
        raise ValueError(label)
    return value


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def parse_fraction(value: Any, label: str, low: Fraction,
                   high: Fraction) -> Fraction:
    if isinstance(value, str):
        if not FRACTION.match(value):
            raise ValueError(label + "_malformed")
        if "/" in value:
            numerator, denominator = value.split("/")
            parsed = Fraction(int(numerator), int(denominator))
        else:
            parsed = Fraction(int(value))
    elif type(value) is int and value > 0:
        parsed = Fraction(value)
    else:
        raise ValueError(label + "_not_fraction")
    if parsed < low or parsed > high:
        raise ValueError(label + "_out_of_range")
    return parsed


def _canonical_decimal(value: Decimal, places: int = 12) -> str:
    quantised = value.quantize(
        Decimal(1).scaleb(-places), rounding=ROUND_HALF_EVEN)
    text = format(quantised, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    if text in ("", "-0"):
        text = "0"
    return text


def pitch_ratio_text(cents: Any) -> str:
    if type(cents) is not int:
        raise ValueError("pitch_cents_not_int")
    if cents < PITCH_CENTS_MIN or cents > PITCH_CENTS_MAX:
        raise ValueError("pitch_cents_out_of_range")
    if cents == 0:
        return "1"
    with localcontext() as context:
        context.prec = 40
        value = Decimal(2) ** (Decimal(cents) / Decimal(1200))
    return _canonical_decimal(value, 12)


def map_timeline(total_samples: Any, rate: Any, pitch_cents: Any,
                 overlap: Any,
                 segments: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    total = _exact_int(total_samples, "total_samples", 1, 1_000_000_000)
    primary_rate = parse_fraction(rate, "rate", RATE_MIN, RATE_MAX)
    overlap_value = parse_fraction(overlap, "overlap", OVERLAP_MIN, OVERLAP_MAX)
    pitch_ratio = pitch_ratio_text(pitch_cents)
    records: list[dict[str, Any]] = []
    if segments is None:
        segments = [{"start_sample": 0, "end_sample": total,
                     "rate": _fraction_text(primary_rate)}]
    if not isinstance(segments, list) or not segments:
        raise ValueError("segments_invalid")
    cursor = 0
    output_cursor = Fraction(0)
    for index, segment in enumerate(segments):
        if not isinstance(segment, dict):
            raise ValueError("segment_not_object")
        if set(segment) != {"start_sample", "end_sample", "rate"}:
            raise ValueError("segment_fields")
        start = _exact_int(segment["start_sample"], "segment_start", 0)
        end = _exact_int(segment["end_sample"], "segment_end", 0)
        if start != cursor:
            raise ValueError("segment_not_contiguous")
        if end <= start:
            raise ValueError("segment_empty")
        if end > total:
            raise ValueError("segment_out_of_range")
        segment_rate = parse_fraction(
            segment["rate"], "segment_rate", RATE_MIN, RATE_MAX)
        duration = Fraction(end - start, 1) / segment_rate
        records.append({
            "index": index,
            "start_sample": start,
            "end_sample": end,
            "rate": _fraction_text(segment_rate),
            "output_start": _fraction_text(output_cursor),
            "output_end": _fraction_text(output_cursor + duration),
            "qualifies": False,
        })
        cursor = end
        output_cursor += duration
    if cursor != total:
        raise ValueError("segments_incomplete")
    floor = output_cursor.numerator // output_cursor.denominator
    ceil = -((-output_cursor.numerator) // output_cursor.denominator)
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "total_samples": total,
        "rate": _fraction_text(primary_rate),
        "pitch_cents": pitch_cents,
        "pitch_ratio": pitch_ratio,
        "overlap": _fraction_text(overlap_value),
        "overlap_effect_modeled": False,
        "output_duration": _fraction_text(output_cursor),
        "output_duration_samples_floor": floor,
        "output_duration_samples_ceil": ceil,
        "duration_identity": output_cursor == total,
        "source_mapping_contiguous": True,
        "final_partial_window": {
            "block_samples": 1600,
            "final_window_samples": total % 1600 or 1600,
            "partial": total % 1600 != 0,
        },
        "records": records,
        "qualifies": False,
    }


def _synthetic_frame() -> list[float]:
    state = 0x12345678
    values: list[float] = []
    for _ in range(FRAME_SAMPLES):
        state = (1103515245 * state + 12345) & 0x7FFFFFFF
        sample = ((state >> 8) % 65536) - 32768
        values.append(sample / 32768.0)
    return values


def validate_frame(samples: Any) -> dict[str, Any]:
    if not isinstance(samples, list):
        raise ValueError("frame_not_list")
    if len(samples) != FRAME_SAMPLES:
        raise ValueError("frame_length")
    peak = 0
    for value in samples:
        if type(value) is bool:
            raise ValueError("frame_bool")
        if not isinstance(value, (int, float)):
            raise ValueError("frame_non_numeric")
        if not math.isfinite(value):
            raise ValueError("frame_nonfinite")
        if abs(value) > 1.0:
            raise ValueError("frame_out_of_range")
        quantised = int(round(value * 32768))
        quantised = max(-32768, min(32767, quantised))
        peak = max(peak, abs(quantised))
    payload = struct.pack("<" + "f" * FRAME_SAMPLES,
                          *[float(value) for value in samples])
    return {
        "frame_samples": FRAME_SAMPLES,
        "peak_int16": peak,
        "digest_sha256": hashlib.sha256(payload).hexdigest(),
        "finite": True,
        "qualifies": False,
    }


def frame_control() -> dict[str, Any]:
    frame = _synthetic_frame()
    accepted = validate_frame(frame)

    def replaced(index: int, value: Any) -> list[Any]:
        candidate = list(frame)
        candidate[index] = value
        return candidate

    cases: list[tuple[str, Any, str]] = [
        ("nan", replaced(0, float("nan")), "frame_nonfinite"),
        ("positive_infinity", replaced(0, float("inf")), "frame_nonfinite"),
        ("negative_infinity", replaced(0, float("-inf")), "frame_nonfinite"),
        ("boolean", replaced(0, True), "frame_bool"),
        ("string", replaced(0, "0.0"), "frame_non_numeric"),
        ("none", replaced(0, None), "frame_non_numeric"),
        ("short_159", frame[:-1], "frame_length"),
        ("long_161", frame + [0.0], "frame_length"),
        ("empty", [], "frame_length"),
        ("out_of_range", replaced(0, 8.5), "frame_out_of_range"),
        ("nested", replaced(0, [0.0]), "frame_non_numeric"),
        ("not_list", "frame", "frame_not_list"),
    ]
    rejected: list[dict[str, Any]] = []
    for case_id, candidate, expected in cases:
        try:
            validate_frame(candidate)
        except ValueError as error:
            actual = str(error)
            rejected.append({
                "id": case_id,
                "status": "rejected" if actual == expected else "wrong_code",
                "code": actual,
                "expected_code": expected,
                "qualifies": False,
                "state_unchanged": True,
            })
        else:
            rejected.append({
                "id": case_id,
                "status": "unexpectedly_admitted",
                "code": "",
                "expected_code": expected,
                "qualifies": False,
                "state_unchanged": False,
            })
    rejected.sort(key=lambda row: row["id"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": "deterministic frame validation and finite-range rejection",
        "accepted": {
            "frame_samples": accepted["frame_samples"],
            "peak_int16": accepted["peak_int16"],
            "digest_sha256": accepted["digest_sha256"],
            "finite": accepted["finite"],
            "qualifies": False,
        },
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for row in rejected
                                  if row["status"] == "rejected"),
            "all_rejected": all(row["status"] == "rejected"
                                for row in rejected),
            "all_codes_match": all(row["code"] == row["expected_code"]
                                   for row in rejected),
            "qualifying_results": 0,
            "audio_read": False,
            "audio_written": False,
            "network_used": False,
        },
        "qualifies": False,
    }


def gate_control() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def add(case_id: str, total: int, rate: str, cents: int, overlap: str,
            segments: list[dict[str, Any]] | None = None) -> None:
        mapping = map_timeline(total, rate, cents, overlap, segments)
        cases.append({
            "id": case_id,
            "evidence_class": "synthetic_contract_control_not_evidence",
            "mapping": mapping,
            "qualifies": False,
        })

    add("identity_1x", 16000, "1", 0, "8")
    add("rate_2x", 16000, "2", 0, "8")
    add("rate_half", 16000, "1/2", 0, "8")
    add("pitch_up_1200", 16000, "1", 1200, "8")
    add("pitch_down_1200", 16000, "1", -1200, "8")
    add("pitch_and_rate", 16000, "3/2", -700, "8")
    add("overlap_max", 16000, "1", 0, "32")
    add("final_partial", 16165, "1", 0, "8")
    add("rate_change_schedule", 16000, "1", 0, "8", [
        {"start_sample": 0, "end_sample": 4000, "rate": "1"},
        {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
        {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
    ])
    add("rate_minimum", 16000, "1/32", 0, "8")
    identity_passes = sum(
        1 for case in cases if case["mapping"]["duration_identity"])
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": (
            "declared AVAudioUnitTimePitch rate/pitch/overlap duration and "
            "pitch arithmetic only; no Apple framework, Audio Unit, render "
            "host, TSM algorithm or measured waveform"),
        "synthetic_control_envelope": {
            "rate_min": _fraction_text(RATE_MIN),
            "rate_max": _fraction_text(RATE_MAX),
            "pitch_cents_min": PITCH_CENTS_MIN,
            "pitch_cents_max": PITCH_CENTS_MAX,
            "overlap_min": _fraction_text(OVERLAP_MIN),
            "overlap_max": _fraction_text(OVERLAP_MAX),
        },
        "cases": cases,
        "frame": frame_control(),
        "summary": {
            "case_count": len(cases),
            "identity_passes": identity_passes,
            "explicit_nonidentity_controls": len(cases) - identity_passes,
            "qualifying_results": 0,
            "framework_loaded": False,
            "audio_unit_instantiated": False,
            "audio_engine_launched": False,
            "runtime_imported": False,
            "audio_read": False,
            "audio_played": False,
            "pitch_measured": False,
            "overlap_measured": False,
            "network_used": False,
        },
        "qualifies": False,
    }


# ---------------------------------------------------------------------------
# Caller qualification manifest admission (fail-closed)
# ---------------------------------------------------------------------------

def _exact_keys(value: Any, fields: tuple[str, ...], label: str) -> dict:
    if not isinstance(value, dict):
        raise ValueError(label + "_not_object")
    if set(value) != set(fields):
        raise ValueError(label + "_fields")
    return value


def _hex(value: Any, label: str, pattern: re.Pattern[str]) -> str:
    if not isinstance(value, str) or not pattern.match(value):
        raise ValueError(label + "_malformed")
    return value


def _slug(value: Any, label: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise ValueError(label)
    return value


def validate_manifest(manifest: Any) -> dict[str, Any]:
    root = _exact_keys(manifest, MANIFEST_FIELDS, "manifest")
    if root["schema_id"] != SCHEMA_MANIFEST_ID:
        raise ValueError("manifest_schema_id")
    _slug(root["run_id"], "run_id")

    runtime = _exact_keys(root["runtime"], RUNTIME_FIELDS, "runtime")
    if runtime["os"] not in RUNTIME_OSES:
        raise ValueError("runtime_os")
    if not isinstance(runtime["os_version"], str) \
            or not SEMVER.match(runtime["os_version"]):
        raise ValueError("runtime_os_version")
    if not isinstance(runtime["os_build"], str) \
            or not OS_BUILD.match(runtime["os_build"]):
        raise ValueError("runtime_os_build")
    if runtime["host_arch"] not in HOST_ARCHES:
        raise ValueError("runtime_host_arch")
    if runtime["framework"] not in FRAMEWORKS:
        raise ValueError("runtime_framework")
    _hex(runtime["framework_sha256"], "runtime_framework_sha256", HEX64)
    if runtime["audio_unit_host"] not in AUDIO_UNIT_HOSTS:
        raise ValueError("runtime_audio_unit_host")
    if type(runtime["render_sample_rate_hz"]) is not int:
        raise ValueError("runtime_render_sample_rate_not_int")
    if runtime["render_sample_rate_hz"] not in AUDIO_SAMPLE_RATES:
        raise ValueError("runtime_render_sample_rate")
    if runtime["pinned"] is not True:
        raise ValueError("runtime_pinned")

    implementation = _exact_keys(
        root["implementation"], IMPLEMENTATION_FIELDS, "implementation")
    if implementation["api"] != "AVAudioUnitTimePitch":
        raise ValueError("implementation_api")
    if implementation["au_type"] not in AU_TYPES:
        raise ValueError("implementation_au_type")
    if implementation["au_subtype"] not in AU_SUBTYPES:
        raise ValueError("implementation_au_subtype")
    if implementation["au_manufacturer"] not in AU_MANUFACTURERS:
        raise ValueError("implementation_au_manufacturer")
    if implementation["closed_source"] is not True:
        raise ValueError("implementation_closed_source")
    if implementation["license_id"] not in IMPLEMENTATION_LICENSES:
        raise ValueError("implementation_license_id")
    _hex(implementation["license_sha256"],
         "implementation_license_sha256", HEX64)
    _hex(implementation["spec_sha256"], "implementation_spec_sha256", HEX64)

    audio = _exact_keys(root["audio"], AUDIO_FIELDS, "audio")
    _slug(audio["fixture_id"], "audio_fixture_id")
    _hex(audio["sha256"], "audio_sha256", HEX64)
    if type(audio["sample_rate_hz"]) is not int:
        raise ValueError("audio_sample_rate_not_int")
    if audio["sample_rate_hz"] not in AUDIO_SAMPLE_RATES:
        raise ValueError("audio_sample_rate")
    if type(audio["channels"]) is not int:
        raise ValueError("audio_channels_not_int")
    if audio["channels"] not in AUDIO_CHANNELS:
        raise ValueError("audio_channels")
    if type(audio["frame_samples"]) is not int:
        raise ValueError("audio_frame_samples_not_int")
    if audio["frame_samples"] not in AUDIO_FRAME_SAMPLES:
        raise ValueError("audio_frame_samples")
    total = _exact_int(audio["total_samples"], "audio_total_samples", 1,
                       1_000_000_000)

    mapping = _exact_keys(root["mapping"], MAPPING_FIELDS, "mapping")
    rate = parse_fraction(mapping["rate"], "mapping_rate",
                          RATE_MIN, RATE_MAX)
    if type(mapping["pitch_cents"]) is not int:
        raise ValueError("mapping_pitch_cents_not_int")
    cents = mapping["pitch_cents"]
    if cents < PITCH_CENTS_MIN or cents > PITCH_CENTS_MAX:
        raise ValueError("mapping_pitch_cents_out_of_range")
    overlap = parse_fraction(mapping["overlap"], "mapping_overlap",
                             OVERLAP_MIN, OVERLAP_MAX)
    source_duration = _exact_int(
        mapping["source_duration_samples"],
        "mapping_source_duration_samples", 1, 1_000_000_000)
    output_duration = _exact_int(
        mapping["output_duration_samples"],
        "mapping_output_duration_samples", 0, 8_000_000_000)
    if source_duration != total:
        raise ValueError("mapping_source_duration_mismatch")
    expected = Fraction(source_duration, 1) / rate
    if expected.denominator != 1:
        raise ValueError("mapping_noninteger_duration")
    if output_duration != int(expected):
        raise ValueError("mapping_output_duration_mismatch")
    expected_pitch = pitch_ratio_text(cents)
    if mapping["pitch_ratio"] != expected_pitch:
        raise ValueError("mapping_pitch_ratio")
    if mapping["map_contiguous"] is not True:
        raise ValueError("mapping_map_contiguous")
    if mapping["final_partial_window"] is not True:
        raise ValueError("mapping_final_partial_window")

    controls = root["controls"]
    if not isinstance(controls, list) or len(controls) != len(CONTROL_KINDS):
        raise ValueError("controls_count")
    seen_ids: set[str] = set()
    seen_kinds: set[str] = set()
    for entry in controls:
        row = _exact_keys(entry, CONTROL_FIELDS, "control")
        _slug(row["id"], "control_id")
        if row["id"] in seen_ids:
            raise ValueError("control_id_duplicate")
        seen_ids.add(row["id"])
        if row["kind"] not in CONTROL_KINDS:
            raise ValueError("control_kind")
        if row["kind"] in seen_kinds:
            raise ValueError("control_kind_duplicate")
        seen_kinds.add(row["kind"])
        if row["passes"] is not True:
            raise ValueError("control_not_passed")

    rights = _exact_keys(root["rights"], RIGHTS_FIELDS, "rights")
    for field in RIGHTS_FIELDS:
        if rights[field] is not True:
            raise ValueError("rights_" + field)

    return {
        "admitted": True,
        "qualifies": False,
        "evidence_class": "synthetic_schema_control_not_evidence",
        "run_id": root["run_id"],
        "mapping_digest": object_digest(mapping),
        "control_count": len(controls),
        "duration_identity": output_duration == source_duration,
        "rate": _fraction_text(rate),
        "pitch_cents": cents,
        "overlap": _fraction_text(overlap),
        "pitch_ratio": expected_pitch,
    }


def _base_manifest() -> dict[str, Any]:
    def syn(name: str) -> str:
        return hashlib.sha256(("synthetic:" + name).encode("ascii")).hexdigest()

    return {
        "schema_id": SCHEMA_MANIFEST_ID,
        "run_id": "synthetic-schema-control",
        "runtime": {
            "os": "macos",
            "os_version": "26.0.0",
            "os_build": "25A354",
            "host_arch": "arm64",
            "framework": "AVFAudio",
            "framework_sha256": syn("avfaudio-framework"),
            "audio_unit_host": "avaudioengine-offline-manual-rendering",
            "render_sample_rate_hz": 48000,
            "pinned": True,
        },
        "implementation": {
            "api": "AVAudioUnitTimePitch",
            "au_type": "aufx",
            "au_subtype": "tpit",
            "au_manufacturer": "appl",
            "closed_source": True,
            "license_id": "Apple-SDK-License",
            "license_sha256": syn("apple-sdk-license"),
            "spec_sha256": syn("apple-timepitch-spec"),
        },
        "audio": {
            "fixture_id": "synthetic-schema-fixture",
            "sha256": syn("fixture"),
            "sample_rate_hz": 48000,
            "channels": 1,
            "frame_samples": 128,
            "total_samples": 16000,
        },
        "mapping": {
            "rate": "5/4",
            "pitch_cents": -700,
            "overlap": "8",
            "source_duration_samples": 16000,
            "output_duration_samples": 12800,
            "pitch_ratio": pitch_ratio_text(-700),
            "map_contiguous": True,
            "final_partial_window": True,
        },
        "controls": [
            {"id": "control-identity", "kind": "identity_1x", "passes": True},
            {"id": "control-rate", "kind": "rate_change", "passes": True},
            {"id": "control-pitch", "kind": "pitch_shift", "passes": True},
            {"id": "control-overlap", "kind": "overlap_change", "passes": True},
            {"id": "control-final", "kind": "final_partial_window",
             "passes": True},
            {"id": "control-rebuffer", "kind": "rebuffer", "passes": True},
        ],
        "rights": {
            "consent_recorded": True,
            "platform_terms_reviewed": True,
            "output_use_defined": True,
            "commercial_use_approved": True,
            "listening_protocol_approved": True,
        },
    }


def _mutations() -> list[tuple[str, str, Any]]:
    def setter(path: tuple[Any, ...], value: Any):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            target[path[-1]] = value
        return apply

    def deleter(path: tuple[str, ...]):
        def apply(manifest: dict[str, Any]) -> None:
            target: Any = manifest
            for key in path[:-1]:
                target = target[key]
            del target[path[-1]]
        return apply

    return [
        ("manifest_missing_rights", "manifest_fields",
         deleter(("rights",))),
        ("manifest_unknown_field", "manifest_fields",
         setter(("extra",), True)),
        ("manifest_schema", "manifest_schema_id",
         setter(("schema_id",), "audio-sdk/other/0.1")),
        ("run_id", "run_id",
         setter(("run_id",), "Bad Id")),
        ("runtime_os", "runtime_os",
         setter(("runtime", "os"), "android")),
        ("runtime_os_version", "runtime_os_version",
         setter(("runtime", "os_version"), "26")),
        ("runtime_os_build", "runtime_os_build",
         setter(("runtime", "os_build"), "25a354")),
        ("runtime_host_arch", "runtime_host_arch",
         setter(("runtime", "host_arch"), "riscv64")),
        ("runtime_framework", "runtime_framework",
         setter(("runtime", "framework"), "AudioToolbox")),
        ("runtime_framework_digest", "runtime_framework_sha256_malformed",
         setter(("runtime", "framework_sha256"), "a" * 63)),
        ("runtime_audio_unit_host", "runtime_audio_unit_host",
         setter(("runtime", "audio_unit_host"), "manual")),
        ("runtime_sample_rate", "runtime_render_sample_rate",
         setter(("runtime", "render_sample_rate_hz"), 22050)),
        ("runtime_sample_rate_float", "runtime_render_sample_rate_not_int",
         setter(("runtime", "render_sample_rate_hz"), 48000.0)),
        ("runtime_not_pinned", "runtime_pinned",
         setter(("runtime", "pinned"), False)),
        ("runtime_unknown_field", "runtime_fields",
         setter(("runtime", "extra"), "x")),
        ("implementation_api", "implementation_api",
         setter(("implementation", "api"), "AVAudioUnitVarispeed")),
        ("implementation_au_type", "implementation_au_type",
         setter(("implementation", "au_type"), "augn")),
        ("implementation_au_subtype", "implementation_au_subtype",
         setter(("implementation", "au_subtype"), "tptx")),
        ("implementation_au_manufacturer", "implementation_au_manufacturer",
         setter(("implementation", "au_manufacturer"), "abcd")),
        ("implementation_closed_source", "implementation_closed_source",
         setter(("implementation", "closed_source"), False)),
        ("implementation_license", "implementation_license_id",
         setter(("implementation", "license_id"), "MIT")),
        ("implementation_license_digest",
         "implementation_license_sha256_malformed",
         setter(("implementation", "license_sha256"), "z" * 64)),
        ("implementation_spec_digest",
         "implementation_spec_sha256_malformed",
         setter(("implementation", "spec_sha256"), "A" * 64)),
        ("implementation_unknown_field", "implementation_fields",
         setter(("implementation", "extra"), "x")),
        ("audio_fixture_id", "audio_fixture_id",
         setter(("audio", "fixture_id"), "Bad Fixture")),
        ("audio_sha", "audio_sha256_malformed",
         setter(("audio", "sha256"), "g" * 64)),
        ("audio_sample_rate", "audio_sample_rate",
         setter(("audio", "sample_rate_hz"), 22050)),
        ("audio_sample_rate_float", "audio_sample_rate_not_int",
         setter(("audio", "sample_rate_hz"), 48000.0)),
        ("audio_channels", "audio_channels",
         setter(("audio", "channels"), 3)),
        ("audio_frame_samples", "audio_frame_samples",
         setter(("audio", "frame_samples"), 100)),
        ("audio_total", "audio_total_samples_below_minimum",
         setter(("audio", "total_samples"), 0)),
        ("audio_total_float", "audio_total_samples_not_int",
         setter(("audio", "total_samples"), 16000.0)),
        ("audio_unknown_field", "audio_fields",
         setter(("audio", "extra"), "x")),
        ("mapping_rate_malformed", "mapping_rate_malformed",
         setter(("mapping", "rate"), "1/0")),
        ("mapping_rate_zero", "mapping_rate_out_of_range",
         setter(("mapping", "rate"), "0")),
        ("mapping_rate_high", "mapping_rate_out_of_range",
         setter(("mapping", "rate"), "33")),
        ("mapping_pitch_not_int", "mapping_pitch_cents_not_int",
         setter(("mapping", "pitch_cents"), "0")),
        ("mapping_pitch_high", "mapping_pitch_cents_out_of_range",
         setter(("mapping", "pitch_cents"), 2401)),
        ("mapping_pitch_low", "mapping_pitch_cents_out_of_range",
         setter(("mapping", "pitch_cents"), -2401)),
        ("mapping_overlap_malformed", "mapping_overlap_malformed",
         setter(("mapping", "overlap"), "1/0")),
        ("mapping_overlap_low", "mapping_overlap_out_of_range",
         setter(("mapping", "overlap"), "2")),
        ("mapping_source", "mapping_source_duration_samples_below_minimum",
         setter(("mapping", "source_duration_samples"), 0)),
        ("mapping_source_mismatch", "mapping_source_duration_mismatch",
         setter(("mapping", "source_duration_samples"), 8000)),
        ("mapping_duration", "mapping_output_duration_mismatch",
         setter(("mapping", "output_duration_samples"), 16000)),
        ("mapping_noninteger", "mapping_noninteger_duration",
         lambda manifest: (
             manifest["audio"].update({"total_samples": 16001}),
             manifest["mapping"].update(
                 {"source_duration_samples": 16001}))),
        ("mapping_pitch_ratio", "mapping_pitch_ratio",
         setter(("mapping", "pitch_ratio"), "1")),
        ("mapping_contiguous", "mapping_map_contiguous",
         setter(("mapping", "map_contiguous"), False)),
        ("mapping_final", "mapping_final_partial_window",
         setter(("mapping", "final_partial_window"), False)),
        ("mapping_unknown_field", "mapping_fields",
         setter(("mapping", "extra"), "x")),
        ("controls_missing", "controls_count",
         lambda manifest: manifest["controls"].pop()),
        ("controls_duplicate_kind", "control_kind_duplicate",
         setter(("controls", 1, "kind"), "identity_1x")),
        ("controls_duplicate_id", "control_id_duplicate",
         setter(("controls", 1, "id"), "control-identity")),
        ("controls_unknown_kind", "control_kind",
         setter(("controls", 0, "kind"), "music")),
        ("controls_not_passed", "control_not_passed",
         setter(("controls", 0, "passes"), False)),
        ("control_unknown_field", "control_fields",
         setter(("controls", 0, "extra"), "x")),
        ("rights_consent", "rights_consent_recorded",
         setter(("rights", "consent_recorded"), False)),
        ("rights_platform", "rights_platform_terms_reviewed",
         setter(("rights", "platform_terms_reviewed"), False)),
        ("rights_output", "rights_output_use_defined",
         setter(("rights", "output_use_defined"), False)),
        ("rights_commercial", "rights_commercial_use_approved",
         setter(("rights", "commercial_use_approved"), False)),
        ("rights_listening", "rights_listening_protocol_approved",
         setter(("rights", "listening_protocol_approved"), False)),
        ("rights_unknown_field", "rights_fields",
         setter(("rights", "extra"), "x")),
    ]


def admission_controls() -> dict[str, Any]:
    base = _base_manifest()
    control = validate_manifest(base)
    rejected: list[dict[str, Any]] = []
    for case_id, code, mutate in _mutations():
        candidate = json.loads(json.dumps(base))
        mutate(candidate)
        try:
            validate_manifest(candidate)
        except ValueError as error:
            actual = str(error)
            status = "rejected" if actual == code else "wrong_code"
            rejected.append({
                "id": case_id,
                "status": status,
                "code": actual,
                "expected_code": code,
                "qualifies": False,
                "state_unchanged": True,
            })
        else:
            rejected.append({
                "id": case_id,
                "status": "unexpectedly_admitted",
                "code": "",
                "expected_code": code,
                "qualifies": False,
                "state_unchanged": False,
            })
    rejected.sort(key=lambda row: row["id"])
    return {
        "control": {
            "id": "synthetic_schema_control",
            "accepted": True,
            "admitted": bool(control["admitted"]),
            "qualifies": False,
            "evidence_class": control["evidence_class"],
            "run_id": control["run_id"],
            "rate": control["rate"],
            "pitch_cents": control["pitch_cents"],
            "overlap": control["overlap"],
            "pitch_ratio": control["pitch_ratio"],
            "duration_identity": control["duration_identity"],
            "mapping_digest": control["mapping_digest"],
        },
        "cases": rejected,
        "summary": {
            "case_count": len(rejected),
            "rejected_count": sum(1 for row in rejected
                                  if row["status"] == "rejected"),
            "all_rejected": all(row["status"] == "rejected"
                                for row in rejected),
            "all_codes_match": all(row["code"] == row["expected_code"]
                                   for row in rejected),
            "accepted_schema_controls": 1,
            "qualifying_results": 0,
            "state_advanced_on_rejection": False,
            "framework_loaded": False,
            "audio_unit_instantiated": False,
            "audio_engine_launched": False,
            "runtime_invoked": False,
            "audio_read": False,
            "audio_played": False,
            "pitch_measured": False,
            "overlap_measured": False,
            "network_used": False,
        },
    }


# ---------------------------------------------------------------------------
# Contract and report
# ---------------------------------------------------------------------------

def _scope() -> dict[str, Any]:
    return {
        "task_local_only": True,
        "directory": TASK_PREFIX,
        "provider_registration": False,
        "descriptor_registry_change": False,
        "installed_v0_behavior_change": False,
        "public_api_abi_change": False,
        "shared_build_or_ci_change": False,
        "default_selected": False,
        "benchmark_claim": False,
        "release_claim": False,
        "network_used": False,
        "download_attempted": False,
        "apple_framework_copied": False,
        "runtime_imported": False,
        "framework_loaded": False,
        "audio_unit_instantiated": False,
        "audio_engine_launched": False,
        "audio_read": False,
        "audio_played": False,
        "render_produced": False,
        "pitch_measured": False,
        "overlap_measured": False,
        "listening_conducted": False,
        "device_timing_measured": False,
        "benchmark_run": False,
    }


def _boundary() -> dict[str, Any]:
    return {
        "installed_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
            "unchanged": True,
        },
        "provider_or_abi_change": False,
        "descriptor_or_registry_change": False,
        "default_change": False,
        "shared_build_or_ci_change": False,
        "board_or_handoff_change": False,
        "external_assets_copied": False,
    }


def _non_claims() -> list[str]:
    return [
        "No result in this package is a qualification, benchmark or release.",
        "The candidate note records only a closed Apple OS platform API name "
        "and parameter names; it is not an implementation or a specification.",
        "AVAudioUnitTimePitch is closed source; no implementation source, "
        "algorithm revision, binary or framework was copied, imported or "
        "loaded.",
        "No Apple OS runtime manifest, AVFAudio framework digest, Audio Unit "
        "host or AVAudioEngine render was present, instantiated or measured.",
        "No rate, pitch, overlap, duration, transient, buffering, rebuffer, "
        "drift or final-partial window was rendered or measured.",
        "No audio was read or played; no rights-cleared speech, music or "
        "silence cohort, consent record or output-use grant is present.",
        "No listening panel, target-device timing, resource measurement, "
        "benchmark or release review was performed.",
        "No provider, descriptor, registry, default, installed-v0, ABI, "
        "shared-build, CI, board or handoff file is changed.",
    ]


def _required_results() -> dict[str, bool]:
    return {
        "apple_runtime_build_identity_admitted": False,
        "avaudiounittimepitch_parameter_semantics_admitted": False,
        "apple_platform_terms_reviewed": False,
        "pinned_avaudioengine_offline_host_admitted": False,
        "official_rate_pitch_overlap_geometry_admitted": False,
        "measured_render_trace_present": False,
        "rate_pitch_overlap_measurement_present": False,
        "rights_cleared_cohort_present": False,
        "rate_acceptance_profile_measured": False,
        "speech_preservation_measured": False,
        "listening_measured": False,
        "device_timing_measured": False,
        "provider_intake_approved": False,
        "release_approved": False,
        "no_result_qualifies": True,
    }


def _required_artifacts() -> list[dict[str, Any]]:
    presence = source_presence()
    return [
        {
            "id": "A01",
            "name": "pinned Apple OS build, architecture and AVFAudio runtime",
            "present": presence["apple_runtime_manifest_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-01",
        },
        {
            "id": "A02",
            "name": "AVAudioUnitTimePitch implementation identity",
            "present": presence["implementation_source_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-02",
        },
        {
            "id": "A03",
            "name": "Apple platform terms and SDK license bundle",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-02",
        },
        {
            "id": "A04",
            "name": "pinned AVAudioEngine/AudioUnit offline render host",
            "present": presence["audio_unit_host_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-03",
        },
        {
            "id": "A05",
            "name": "official rate, pitch and overlap geometry contract",
            "present": presence["spec_text_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-04",
        },
        {
            "id": "A06",
            "name": "measured render trace with final partial window",
            "present": presence["measured_render_trace_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-04",
        },
        {
            "id": "A07",
            "name": "rights-cleared speech, music and silence cohort",
            "present": presence["rights_cleared_cohort_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-05",
        },
        {
            "id": "A08",
            "name": "approved pitch, transient and preservation scorer",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-05",
        },
        {
            "id": "A09",
            "name": "blind listening and target-device timing record",
            "present": presence["listening_record_present"]
            or presence["device_timing_record_present"],
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-06",
        },
        {
            "id": "A10",
            "name": "opt-in adapter intake and release review",
            "present": False,
            "verified": False,
            "licensed": False,
            "admitted": False,
            "blocked": True,
            "sha256": None,
            "blocker": "BLK-06",
        },
    ]


def _exact_blockers() -> list[dict[str, Any]]:
    return [
        {
            "id": "BLK-01",
            "artifact_id": "A01",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A pinned Apple OS/runtime identity: OS name and exact "
                "version, exact OS build, host architecture, AVFAudio "
                "framework digest and a recorded host profile. No Apple "
                "runtime manifest or framework digest exists in the project "
                "workspace."),
            "required_action": (
                "Supply the exact macOS/iOS build, architecture, AVFAudio "
                "framework SHA-256, host profile and immutable acquisition "
                "record for the claimed runtime."),
        },
        {
            "id": "BLK-02",
            "artifact_id": "A02",
            "status": "open",
            "qualifies": False,
            "missing": (
                "The AVAudioUnitTimePitch implementation identity: Apple "
                "Audio Unit type/subtype/manufacturer, algorithm identity, "
                "parameter semantics and an exact revision. The candidate "
                "note states the source is not available and that behaviour "
                "can change between OS versions, so no vendorable source "
                "revision exists."),
            "required_action": (
                "Supply a reviewed Apple platform/terms decision, exact OS "
                "build binding for the Audio Unit, and a pinned public "
                "parameter/geometry reference for rate, pitch and overlap."),
        },
        {
            "id": "BLK-03",
            "artifact_id": "A04",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A pinned offline render host: AVAudioEngine or Audio Unit "
                "host identity, render mode, sample rate, channel layout, "
                "launch configuration, toolchain and reproducible build/run "
                "record. No Apple host, Xcode project or automation exists "
                "in the project workspace."),
            "required_action": (
                "Supply the exact host/toolchain version, offline render "
                "configuration, lockfile or build record, sample rate, "
                "layout and recorded host profile."),
        },
        {
            "id": "BLK-04",
            "artifact_id": "A06",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A measured render trace and the official parameter/geometry "
                "contract: rate and duration mapping, pitch in cents, overlap "
                "semantics, defaults, valid ranges, latency, channel "
                "handling, rate-change behavior and the final partial window. "
                "Only synthetic arithmetic exists here."),
            "required_action": (
                "Supply the pinned Apple parameter/geometry reference and an "
                "exact offline render trace covering 1x, rate changes, pitch "
                "shifts, overlap changes, final partial window and rebuffer."),
        },
        {
            "id": "BLK-05",
            "artifact_id": "A07",
            "status": "open",
            "qualifies": False,
            "missing": (
                "A rights-cleared frozen playback cohort with unfamiliar "
                "speech, music and silence, consent/output-use terms, and "
                "approved pitch/transient preservation labels or scorer. No "
                "cohort or consent record is present."),
            "required_action": (
                "Supply an immutable consented cohort with stratified "
                "speech/music/silence, matched controls, output-use terms and "
                "human-verified preservation labels."),
        },
        {
            "id": "BLK-06",
            "artifact_id": "A10",
            "status": "open",
            "qualifies": False,
            "missing": (
                "Rate-profile acceptance results: measured duration, pitch, "
                "overlap/transient audibility, buffering/rebuffer/drift, "
                "speech preservation, blind listening, target-device timing, "
                "resources, separate opt-in intake and release review."),
            "required_action": (
                "Supply measured rate-profile evidence, independent listening "
                "and scoring, target-device timing, and an approved opt-in "
                "intake with an OFF default and exact-head review."),
        },
    ]


def _rate_profile_rows() -> list[dict[str, Any]]:
    return [
        {"id": "RATE-01", "requirement": "1x control",
         "status": "blocked", "qualifies": False,
         "evidence": "No measured 1x Apple Audio Unit render control."},
        {"id": "RATE-02", "requirement": "source/output mapping and rate changes",
         "status": "blocked", "qualifies": False,
         "evidence": "Synthetic arithmetic only; no Audio Unit source-to-output "
                     "trace."},
        {"id": "RATE-03", "requirement": "duration identity and error",
         "status": "blocked", "qualifies": False,
         "evidence": "No measured Apple output duration or error."},
        {"id": "RATE-04", "requirement": "pitch",
         "status": "blocked", "qualifies": False,
         "evidence": "No rendered waveform, pitch tracker or cents-shift "
                     "measurement."},
        {"id": "RATE-05", "requirement": "transient audibility",
         "status": "blocked", "qualifies": False,
         "evidence": "No waveform, transient analysis or listening; overlap "
                     "effect is unmeasured."},
        {"id": "RATE-06", "requirement": "playback buffering, rebuffer and drift",
         "status": "blocked", "qualifies": False,
         "evidence": "No Apple audio clock, buffering, fill/flush or drift "
                     "run."},
        {"id": "RATE-07", "requirement": "unfamiliar speech, music and silence",
         "status": "blocked", "qualifies": False,
         "evidence": "No rights-cleared stratified playback cohort exists."},
        {"id": "RATE-08",
         "requirement": "final partial window and speech preservation",
         "status": "blocked", "qualifies": False,
         "evidence": "Synthetic final-window arithmetic only; no Apple render "
                     "or preservation score."},
    ]


def _rate_outcomes() -> list[dict[str, Any]]:
    rows = []
    for row in _rate_profile_rows():
        rows.append({
            "id": row["id"].replace("RATE", "OUT"),
            "requirement": row["requirement"],
            "status": "blocked",
            "value": None,
            "qualifies": False,
        })
    return rows


def _release_gates(projection: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [
        ("RG-01", "Apple OS and AVFAudio runtime identity",
         "Exact macOS/iOS build, architecture, AVFAudio framework digest and "
         "recorded host profile."),
        ("RG-02", "closed implementation identity, parameter semantics and terms",
         "Reviewed Apple platform terms, exact OS build binding, Audio Unit "
         "type/subtype/manufacturer and pinned rate/pitch/overlap semantics."),
        ("RG-03", "pinned AVAudioEngine offline render host",
         "Pinned host/toolchain, render mode, sample rate, layout, launch "
         "configuration and reproducible build/run record."),
        ("RG-04", "official parameter and geometry contract",
         "Pinned reference for rate, pitch cents, overlap, defaults, ranges, "
         "latency, channel handling and final partial window."),
        ("RG-05", "rights-cleared playback cohort",
         "Immutable consented speech/music/silence cohort with output-use "
         "terms and matched controls."),
        ("RG-06", "rate acceptance profile",
         "Measured 1x/rate-change/pitch/overlap/duration/transient/buffering/"
         "rebuffer/drift/final-partial results on the pinned Apple host."),
        ("RG-07", "speech preservation and independent scoring",
         "Approved pitch/transient preservation labels or scorer, stratified "
         "speech results and blind listening."),
        ("RG-08", "device timing, opt-in intake and release",
         "Target-device timing/power/resources, separate opt-in adapter intake "
         "with OFF default, benchmark review and release approval."),
    ]
    return [{"id": gate_id, "title": title, "status": "blocked",
             "qualifies": False, "reopen_condition": condition,
             "linked_row": dict(projection)}
            for gate_id, title, condition in rows]


def _candidate_provenance() -> dict[str, Any]:
    note = candidate_note_probe()
    return {
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
        "path": CANDIDATE_NOTE,
        "line": note["line"],
        "section_line": note["section_line"],
        "link_line": note["link_line"],
        "recorded_api": "AVAudioUnitTimePitch (rate, pitch, overlap)",
        "recorded_statement": note["statement"],
        "recorded_what_it_is": note["what_it_is"],
        "recorded_cons": note["cons"],
        "recorded_licence": note["licence_recorded"],
        "recorded_links": note["links"],
        "recorded_parameters": ["rate", "pitch", "overlap"],
        "rate_range_recorded": note["rate_range_recorded"],
        "pitch_unit_recorded": note["pitch_unit_recorded"],
        "overlap_recorded": note["overlap_recorded"],
        "closed_source_recorded": note["records_closed_source"],
        "os_variation_recorded": note["records_os_variation"],
        "portability_limitation_recorded": note[
            "records_portability_limitation"],
        "algorithm_specified": False,
        "defaults_recorded": False,
        "latency_recorded": False,
        "runtime_identity_recorded": False,
        "render_result_recorded": False,
        "not_reproduced_here": True,
        "framework_loaded_here": False,
        "audio_unit_instantiated_here": False,
        "audio_read_here": False,
        "network_used_here": False,
    }


def _documented_envelope() -> dict[str, Any]:
    note = candidate_note_probe()
    return {
        "evidence_class": "public_api_documentation_reported_not_remeasured",
        "source": (
            "Apple AVAudioUnitTimePitch documentation link recorded in the "
            "pinned candidate note"),
        "link_recorded": bool(note["links"]),
        "rate": {
            "unit": "ratio",
            "min": "0.03125" if note["rate_range_recorded"] else None,
            "max": "32" if note["rate_range_recorded"] else None,
            "default": None,
        },
        "pitch": {
            "unit": "cents" if note["pitch_unit_recorded"] else None,
            "min": None,
            "max": None,
            "default": None,
        },
        "overlap": {
            "unit": "unrecorded",
            "name_recorded": note["overlap_recorded"],
            "min": None,
            "max": None,
            "default": None,
        },
        "defaults_recorded_in_candidate_note": False,
        "numeric_pitch_and_overlap_bounds_recorded_in_candidate_note": False,
        "semantics_verified_here": False,
        "qualifies": False,
    }


def _synthetic_envelope() -> dict[str, Any]:
    return {
        "evidence_class": "synthetic_contract_control_not_evidence",
        "purpose": (
            "control constants used only to validate the synthetic manifest; "
            "they are not pinned runtime evidence"),
        "rate_min": _fraction_text(RATE_MIN),
        "rate_max": _fraction_text(RATE_MAX),
        "pitch_cents_min": PITCH_CENTS_MIN,
        "pitch_cents_max": PITCH_CENTS_MAX,
        "overlap_min": _fraction_text(OVERLAP_MIN),
        "overlap_max": _fraction_text(OVERLAP_MAX),
        "defaults_recorded": False,
        "qualifies": False,
    }


def _reproduction() -> dict[str, Any]:
    return {
        "python": "3.11 or newer, standard library only",
        "commands": [
            "export PYTHONDONTWRITEBYTECODE=1",
            "python3 run.py all",
            "python3 -m unittest -v test_reference.py",
            "python3 verify.py",
        ],
        "repeat_count": 3,
        "byte_identical_required": True,
        "network_used": False,
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    source_pins, boundary_pins, sibling_pins = verify_pins()
    presence = source_presence()
    markers = license_marker_probe()
    return {
        "contract_id": CONTRACT_ID,
        "schema_id": CONTRACT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "qualification_status": "not_qualified",
            "blocked_before": "implementation_or_intake",
            "qualifying_results": 0,
            "blocked_release_gates": 8,
        },
        "qualification": {
            "status": "not_qualified",
            "evidence_status": "incomplete",
            "proposal_only": True,
            "qualifying_results": 0,
            "blocked_release_gates": 8,
            "open_blockers": 6,
            "candidate_note_present": presence["candidate_note_present"],
            "licensed_implementation_runtime_present": False,
            "apple_runtime_present": False,
            "reasons": [
                "no pinned Apple OS build, architecture, AVFAudio framework "
                "digest or host profile",
                "AVAudioUnitTimePitch is closed source; no implementation "
                "revision or algorithm identity is available",
                "no reviewed Apple platform terms, output-use or "
                "redistribution decision",
                "no pinned AVAudioEngine/AudioUnit offline render host",
                "no measured rate/pitch/overlap render trace or final-partial "
                "behavior",
                "no rights-cleared cohort, preservation scorer, listening or "
                "device-timing result",
            ],
        },
        "scope": _scope(),
        "boundary": _boundary(),
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "non_claims": _non_claims(),
        "profile_phrases": list(PROFILE_PHRASES),
        "profile_source": "audio-benchmark-platform/plan/swarm/VERIFICATION.md",
        "source_pins": SOURCE_PINS,
        "boundary_pins": BOUNDARY_PINS,
        "sibling_pins": SIBLING_PINS,
        "source_presence": presence,
        "license_findings": markers,
        "observed_provenance": {
            "candidate_note": _candidate_provenance(),
            "sibling_evidence": [dict(row) for row in LINKED_ROWS],
            "synthetic_frame_digest": frame_control()["accepted"][
                "digest_sha256"],
        },
        "documented_parameter_envelope": _documented_envelope(),
        "synthetic_control_envelope": _synthetic_envelope(),
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "release_gates": _release_gates(projection),
        "rate_profile_requirements": _rate_profile_rows(),
        "rate_outcomes": _rate_outcomes(),
        "required_results": _required_results(),
        "linked_row_projection": projection,
        "linked_row_fields": list(BOARD_ROW_FIELDS),
        "linked_rows": [dict(row) for row in LINKED_ROWS],
        "linked_rows_sha256": linked_rows_digest(),
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "reproduction": _reproduction(),
    }


def build_report() -> dict[str, Any]:
    contract = build_contract()
    contract_sha = object_digest(contract)
    source_pins, boundary_pins, sibling_pins = verify_pins()
    presence = source_presence()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "decision": "DEFER",
        "status": "incomplete",
        "qualification_status": "not_qualified",
        "proposal_only": True,
        "contract_sha256": contract_sha,
        "disposition": contract["disposition"],
        "qualification": contract["qualification"],
        "scope": contract["scope"],
        "boundary": contract["boundary"],
        "public_v0_geometry": contract["public_v0_geometry"],
        "non_claims": contract["non_claims"],
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "sibling_pins": sibling_pins,
        "source_presence": presence,
        "license_findings": contract["license_findings"],
        "observed_provenance": contract["observed_provenance"],
        "documented_parameter_envelope":
            contract["documented_parameter_envelope"],
        "synthetic_control_envelope": contract["synthetic_control_envelope"],
        "required_artifacts": contract["required_artifacts"],
        "exact_blockers": contract["exact_blockers"],
        "gates": contract["release_gates"],
        "rate_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "source": contract["profile_source"],
            "rows": contract["rate_profile_requirements"],
        },
        "rate_outcomes": {"rows": contract["rate_outcomes"]},
        "gate_control": gate_control(),
        "admission": admission_controls(),
        "linked_row_identity": {
            "projection": contract["linked_row_projection"],
            "sha256": board_row_digest(contract["linked_row_projection"]),
            "fields": contract["linked_row_fields"],
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": contract["linked_rows"],
            "linked_rows_sha256": contract["linked_rows_sha256"],
        },
        "required_results": contract["required_results"],
        "reproduction": contract["reproduction"],
    }


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "contract_id", "schema_id", "task", "component", "decision", "status",
        "qualification_status", "proposal_only", "qualification",
        "release_gates", "exact_blockers", "required_artifacts",
        "rate_profile_requirements", "rate_outcomes", "linked_row_projection",
        "board_file_pinned", "documented_parameter_envelope",
        "synthetic_control_envelope",
    )
    for field in required:
        if field not in contract:
            raise ValueError("contract_field_missing:" + field)
    if contract["task"] != TASK:
        raise ValueError("contract_task")
    if contract["component"] != COMPONENT_ID:
        raise ValueError("contract_component")
    if contract["decision"] != "DEFER" \
            or contract["status"] != "incomplete" \
            or contract["qualification_status"] != "not_qualified" \
            or contract["proposal_only"] is not True:
        raise ValueError("contract_disposition")
    gates = contract["release_gates"]
    if not isinstance(gates, list) or len(gates) != 8:
        raise ValueError("contract_gates")
    for index, gate in enumerate(gates, start=1):
        if gate.get("id") != f"RG-{index:02d}" \
                or gate.get("status") != "blocked" \
                or gate.get("qualifies") is not False:
            raise ValueError("contract_gate:" + str(index))
    if len(contract["exact_blockers"]) != 6:
        raise ValueError("contract_blockers")
    if len(contract["required_artifacts"]) != 10:
        raise ValueError("contract_artifacts")
    if len(contract["rate_profile_requirements"]) != 8:
        raise ValueError("contract_rate_rows")
    if len(contract["rate_outcomes"]) != 8:
        raise ValueError("contract_rate_outcomes")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if contract["documented_parameter_envelope"].get("qualifies") is not False:
        raise ValueError("contract_documented_envelope")
    if contract["synthetic_control_envelope"].get("qualifies") is not False:
        raise ValueError("contract_synthetic_envelope")
    for pins in (contract["source_pins"], contract["boundary_pins"],
                 contract["sibling_pins"]):
        if BOARD_TASK_ROW in pins:
            raise ValueError("mutable_board_pinned")


def verify_sources_manifest(payload: bytes) -> None:
    lines = payload.decode("ascii").splitlines()
    if not lines or not lines[0].startswith("# SHA-256 pins for"):
        raise ValueError("sources_header")
    seen: set[str] = set()
    for line in lines:
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if not HEX64.match(digest):
            raise ValueError("sources_digest")
        if name in seen:
            raise ValueError("sources_duplicate")
        seen.add(name)
    expected = {"source:" + name for name in SOURCE_PINS}
    expected |= {"boundary:" + name for name in BOUNDARY_PINS}
    expected |= {"sibling:" + name for name in SIBLING_PINS}
    expected |= {TASK_PREFIX + name for name in LOCAL_PIN_FILES}
    if seen != expected:
        raise ValueError("sources_set")
    if TASK_PREFIX + "SOURCES.sha256" in seen:
        raise ValueError("sources_self_pinned")
