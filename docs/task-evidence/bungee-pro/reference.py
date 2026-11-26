# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local DEFER evidence for SDK-BUNGEE-PRO.

Standard-library only and deterministic. This module never downloads, imports
or executes a Bungee Pro artifact, reads audio, or uses the network. It pins
the provenance that is present, proves that the exact licensed commercial
implementation/runtime, its terms, a pinned integration host and a
rights-cleared rate cohort are absent, and reproduces only declared rate
arithmetic and deterministic synthetic controls. None of it is runtime
evidence and none of it can qualify.

The pinned candidate note records Bungee Pro only as a commercial upgrade to
Bungee Basic: proprietary algorithms, vendor-claimed quality/SIMD/support, no
local evaluation, and no pricing, contract terms or patent indemnity. The
open-source Bungee Basic implementation is a different MPL-2.0 product and is
not a substitute for the Pro artifact or its rights. Nothing is fabricated or
downloaded.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
from decimal import Decimal, localcontext, ROUND_HALF_EVEN
from fractions import Fraction
from pathlib import Path
from typing import Any, Callable

TASK = "SDK-BUNGEE-PRO"
COMPONENT_ID = "bungee-pro"
TASK_TITLE = "Bungee Pro"
CONTRACT_ID = "audio-sdk/bungee-pro/0.1"
CONTRACT_SCHEMA_ID = "audio-sdk/task-evidence-contract/0.2"
REPORT_SCHEMA_ID = "audio-sdk/task-evidence-report/0.3"
MANIFEST_SCHEMA_ID = "audio-sdk/bungee-pro/qualification/0.1"
PROFILE = "rate"
PROFILE_LABEL = "Rate"
MODE = "external-adapter"
BASE_COMMIT = "4d9a7568583fd1764d2ca9006e8e660e8662aaf9"
BRANCH = "swarm/SDK-BUNGEE-PRO"
REVIEWER = "reviewer-BUNGEE-PRO"
TASK_PREFIX = "docs/task-evidence/bungee-pro/"
BOARD_TASK_ROW = "audio-benchmark-platform/plan/swarm/TASKS.json"
BOARD_ROW_FIELDS = (
    "id", "title", "repository", "mode", "depends_on", "component", "evidence")

CANDIDATE_NOTE = (
    "cpp-library/pipeline-validation/playback-speed-candidates.md")
CANDIDATE_MATRIX_MARKER = "| **Bungee Pro** |"
CANDIDATE_SECTION_MARKER = "### 3.8 Bungee Pro"
CANDIDATE_BASIC_LINK_MARKER = "github.com/bungee-audio-stretch/bungee"

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
    "docs/task-evidence/audiobuffersourcenode-playbackrate-preservespitch/report.json":
        "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4",
    "docs/task-evidence/avaudiounittimepitch-rate-pitch-overlap/report.json":
        "33f51433da2938a5dae4ad18fd66da17f78882e2b0aa0301de9d7f52f6474bd0",
    "docs/task-evidence/bungee-basic/README.md":
        "ee6edcc68764888500aed41963169e6e311cec447b511fcbd1f2d4189453d485",
    "docs/task-evidence/bungee-basic/report.json":
        "bb434059ae6c3d07e247d7568d1dad3aab9441194f3b57c54851df4298447f8b",
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
    "docs/task-evidence/sonic/report.json":
        "2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2",
    "docs/task-evidence/soundtouch/report.json":
        "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947",
    "docs/task-evidence/speex-resampler/report.json":
        "6640c7995d3b0bb85338a508a64895d02f298b228eb4d79b8baa273713170898",
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

LINKED_ROWS: tuple[dict[str, Any], ...] = (
    {"task": "SDK-BUNGEE-BASIC",
     "role": "merged open-source Bungee Basic synthetic rate-map fixture; "
             "different implementation and MPL-2.0 licence; not Pro",
     "report_sha256":
         "bb434059ae6c3d07e247d7568d1dad3aab9441194f3b57c54851df4298447f8b"},
    {"task": "SDK-SIGNALSMITH-STRETCH",
     "role": "merged Signalsmith Stretch synthetic reference; not Bungee Pro",
     "report_sha256":
         "e352ef75bd0be91cbd5244dd69c8a5739fd1ec6bf3b86e73ae023948d6007231"},
    {"task": "SDK-SOUNDTOUCH",
     "role": "merged SoundTouch synthetic reference; not Bungee Pro",
     "report_sha256":
         "83ef7edaa82f919f1db0d9027b0b4724f2a95a46cfaea848e2652dcc43bbe947"},
    {"task": "SDK-RUBBER-BAND-R3-OFFLINE",
     "role": "merged Rubber Band R3 offline reference; not Bungee Pro",
     "report_sha256":
         "b9dda54f2ae86a200b1cfd251f56abb4f9d741ee28778145544650ea38fb10db"},
    {"task": "SDK-SONIC",
     "role": "merged Sonic synthetic reference; not Bungee Pro",
     "report_sha256":
         "2bd9ad4099b20593e0e0e63c114f53a40270517839da43adf4b582c629a0ade2"},
    {"task": "SDK-LIBSAMPLERATE",
     "role": "merged varispeed/resampling reference; pitch changes with rate",
     "report_sha256":
         "c7453cf5e5d1a292118fe9a31340d10e0f9324631925e0246a21069d412a30cc"},
    {"task": "SDK-GRANULAR-TSM",
     "role": "merged granular TSM synthetic reference; not Bungee Pro",
     "report_sha256":
         "3aefe97a4d6f7ba28ca5ab7111e0e3b83f623afd382bc50ece0f36868e881138"},
    {"task": "SDK-OLA-SOLA",
     "role": "merged OLA/SOLA synthetic reference; not Bungee Pro",
     "report_sha256":
         "90840821a6cb0de58efcf7e146fb014871e5f794c034ca5e559be848337b0d93"},
    {"task": "SDK-PHASE-VOCODER-BASELINE",
     "role": "merged phase-vocoder baseline; not Bungee Pro",
     "report_sha256":
         "555eda3e2ee17b433afdafbab06f953ee3235168ed0db88a5bf29870ca9568a7"},
    {"task": "SDK-D1-WHOLE-CLIP-DURATION-PLANNER",
     "role": "merged synthetic duration planner; no playback runtime",
     "report_sha256":
         "522f585511ae5c6306914ab250f261fc0d5af56bc7d494a09f62a12b2f179a98"},
    {"task": "SDK-AUDIOBUFFERSOURCENODE-PLAYBACKRATE-PRESERVESPITCH",
     "role": "merged browser playbackRate DEFER blocker; no Bungee Pro evidence",
     "report_sha256":
         "1b4fd95133f958eeb827b809209f02a124e4ef52b7c412d7fc76e4da61ce0be4"},
    {"task": "SDK-AVAUDIOUNITTIMEPITCH-RATE-PITCH-OVERLAP",
     "role": "merged closed Apple time-pitch blocker; no Bungee Pro evidence",
     "report_sha256":
         "33f51433da2938a5dae4ad18fd66da17f78882e2b0aa0301de9d7f52f6474bd0"},
    {"task": "SDK-SPEEX-RESAMPLER",
     "role": "merged varispeed-only resampler reference; pitch changes with rate",
     "report_sha256":
         "6640c7995d3b0bb85338a508a64895d02f298b228eb4d79b8baa273713170898"},
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
PARTIAL_BLOCK = 1600
SYNTHETIC_CLASS = "synthetic_contract_control_not_evidence"
CONTROL_KINDS = (
    "identity_1x", "rate_change", "pitch_shift", "final_partial_window",
    "rebuffer", "duration_mapping")
RUNTIME_OSES = ("macos", "linux", "windows", "android", "ios")
HOST_ARCHES = ("arm64", "x86_64")
AUDIO_SAMPLE_RATES = (8000, 16000, 44100, 48000)
AUDIO_FRAME_SAMPLES = (128, 160, 256, 480, 1024)
AUDIO_CHANNELS = (1, 2)
CONTROL_RATE_MIN = Fraction(1, 4)
CONTROL_RATE_MAX = Fraction(4)
CONTROL_PITCH_MIN = -1200
CONTROL_PITCH_MAX = 1200

PRO_ARTIFACT_PROBES = (
    "adapters/bungee-pro",
    "adapters/bungee_pro",
    "bindings/bungee-pro",
    "bindings/bungee_pro",
    "data/checkouts/bungee-pro",
    "data/checkouts/bungee_pro",
    "data/checkouts/tsm-engines-20261101/bungee-pro",
    "data/checkouts/tsm-engines-20261101/bungee/pro",
    "data/runtimes/bungee-pro",
    "data/runtimes/bungee_pro",
    "docs/bungee-pro",
    "lib/bungee-pro",
    "src/bungee-pro",
    "third_party/bungee-pro",
    "third_party/bungee_pro",
    "tools/bungee-pro",
    "vendor/bungee-pro",
    "vendor/bungee_pro",
)

MANIFEST_FIELDS = (
    "schema_id", "run_id", "vendor", "runtime", "audio", "mapping",
    "controls", "rights")
VENDOR_FIELDS = (
    "product", "version", "artifact_sha256", "license_id", "license_sha256",
    "terms_sha256", "api_identity", "pro_build")
RUNTIME_FIELDS = (
    "os", "os_version", "arch", "package_sha256", "compiler",
    "license_key_present", "pinned")
AUDIO_FIELDS = (
    "fixture_id", "sha256", "sample_rate_hz", "channels", "frame_samples",
    "total_samples")
MAPPING_FIELDS = (
    "rate", "source_duration_samples", "output_duration_samples",
    "pitch_preserved", "final_partial_window")
CONTROL_FIELDS = ("id", "kind", "passes")
RIGHTS_FIELDS = (
    "consent_recorded", "license_execution_approved", "output_use_defined",
    "commercial_use_approved", "redistribution_approved",
    "listening_protocol_approved")

HEX64 = re.compile(r"^[0-9a-f]{64}$")
SLUG = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
RATE_TEXT = re.compile(r"^-?[0-9]+(?:/[0-9]+)?$")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(
        value, sort_keys=True, separators=(",", ":"), ensure_ascii=True,
        allow_nan=False) + "\n").encode("ascii")


def object_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def _no_floats(value: Any) -> None:
    if isinstance(value, float):
        raise ValueError("non_integer_number")
    if isinstance(value, dict):
        for key, item in value.items():
            if not isinstance(key, str):
                raise ValueError("non_string_key")
            _no_floats(item)
    elif isinstance(value, list):
        for item in value:
            _no_floats(item)


def read_strict_json(path: Path) -> Any:
    def no_duplicates(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in pairs:
            if key in result:
                raise ValueError("duplicate_key:" + key)
            result[key] = value
        return result

    def reject_float(_text: str) -> Any:
        raise ValueError("non_integer_number")

    def reject_constant(text: str) -> Any:
        raise ValueError("nonfinite_constant:" + text)

    text = path.read_text(encoding="utf-8")
    value = json.loads(text, object_pairs_hook=no_duplicates,
                       parse_float=reject_float,
                       parse_constant=reject_constant)
    _no_floats(value)
    return value


def _is_int(value: Any) -> bool:
    return isinstance(value, int) and not isinstance(value, bool)


def _require_int(value: Any, code: str) -> int:
    if not _is_int(value):
        raise ValueError(code)
    return value


def _reject_nonfinite(value: Any) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        raise ValueError("nonfinite_value")
    if isinstance(value, dict):
        for item in value.values():
            _reject_nonfinite(item)
    elif isinstance(value, list):
        for item in value:
            _reject_nonfinite(item)


def _require_exact_keys(value: Any, fields: tuple[str, ...]) -> None:
    if not isinstance(value, dict):
        raise ValueError("invalid_type")
    if set(value) - set(fields):
        raise ValueError("unknown_field")
    for field in fields:
        if field not in value:
            raise ValueError("missing_field")


def _require_slug(value: Any, code: str) -> str:
    if not isinstance(value, str) or not SLUG.match(value):
        raise ValueError(code)
    return value


def _require_digest(value: Any) -> str:
    if not isinstance(value, str) or not HEX64.match(value):
        raise ValueError("invalid_digest")
    return value


def _require_bool(value: Any, code: str) -> bool:
    if not isinstance(value, bool):
        raise ValueError(code)
    return value


def parse_rate(value: Any) -> Fraction:
    if not isinstance(value, str) or not RATE_TEXT.match(value):
        raise ValueError("rate_malformed")
    if "/" in value:
        numerator, denominator = value.split("/", 1)
        if int(denominator) == 0:
            raise ValueError("rate_malformed")
        fraction = Fraction(int(numerator), int(denominator))
    else:
        fraction = Fraction(int(value))
    if fraction < CONTROL_RATE_MIN or fraction > CONTROL_RATE_MAX:
        raise ValueError("rate_out_of_range")
    return fraction


def _fraction_text(value: Fraction) -> str:
    if value.denominator == 1:
        return str(value.numerator)
    return f"{value.numerator}/{value.denominator}"


def _decimal_text(value: Decimal) -> str:
    text = format(value, "f")
    if "." in text:
        text = text.rstrip("0").rstrip(".")
    return text or "0"


def pitch_ratio(cents: Any) -> str:
    cents = _require_int(cents, "pitch_cents_not_int")
    if cents < -2400 or cents > 2400:
        raise ValueError("pitch_cents_out_of_range")
    if cents == 0:
        return "1"
    with localcontext() as context:
        context.prec = 50
        ratio = (Decimal(2) ** (Decimal(cents) / Decimal(1200))).quantize(
            Decimal("0.000000000001"), rounding=ROUND_HALF_EVEN)
        return _decimal_text(ratio)


def map_timeline(source_samples: Any, rate: Any, pitch_cents: Any = 0,
                 schedule: Any = None,
                 block_samples: Any = PARTIAL_BLOCK) -> dict[str, Any]:
    source_samples = _require_int(source_samples, "invalid_source_duration")
    if source_samples <= 0:
        raise ValueError("invalid_source_duration")
    block_samples = _require_int(block_samples, "invalid_block_samples")
    if block_samples <= 0:
        raise ValueError("invalid_block_samples")
    primary_rate = parse_rate(rate)
    ratio = pitch_ratio(pitch_cents)
    segments = _schedule_records(schedule, source_samples, rate)
    records: list[dict[str, Any]] = []
    total = Fraction(0)
    for start, end, segment_rate in segments:
        fraction = parse_rate(segment_rate)
        output = Fraction(end - start, 1) / fraction
        total += output
        records.append({
            "start_sample": start,
            "end_sample": end,
            "source_samples": end - start,
            "rate": _fraction_text(fraction),
            "output_duration": _fraction_text(output),
            "output_samples_floor": output.numerator // output.denominator,
            "output_samples_ceil":
                -((-output.numerator) // output.denominator),
        })
    final_window = source_samples % block_samples
    return {
        "source_samples": source_samples,
        "rate": _fraction_text(primary_rate),
        "pitch_cents": pitch_cents,
        "pitch_ratio": ratio,
        "pitch_preserved": pitch_cents == 0,
        "records": records,
        "output_duration": _fraction_text(total),
        "output_samples_floor": total.numerator // total.denominator,
        "output_samples_ceil": -((-total.numerator) // total.denominator),
        "duration_identity": total == source_samples,
        "source_mapping_contiguous": True,
        "final_partial_window": {
            "block_samples": block_samples,
            "final_window_samples": final_window,
            "partial": final_window != 0,
        },
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _schedule_records(schedule: Any, source_samples: int,
                      single_rate: Any) -> list[tuple[int, int, str]]:
    if schedule is None:
        return [(0, source_samples, single_rate)]
    if not isinstance(schedule, list) or not schedule:
        raise ValueError("invalid_schedule")
    records: list[tuple[int, int, str]] = []
    expected_start = 0
    for item in schedule:
        _require_exact_keys(item, ("start_sample", "end_sample", "rate"))
        start = _require_int(item["start_sample"], "invalid_schedule")
        end = _require_int(item["end_sample"], "invalid_schedule")
        if start != expected_start or end <= start:
            raise ValueError("schedule_not_contiguous")
        parse_rate(item["rate"])
        records.append((start, end, item["rate"]))
        expected_start = end
    if expected_start != source_samples:
        raise ValueError("schedule_does_not_cover_source")
    return records


def gate_control() -> dict[str, Any]:
    cases: list[dict[str, Any]] = []

    def add(case_id: str, kind: str, source: int, rate: str,
            pitch: int = 0, schedule: Any = None) -> None:
        mapping = map_timeline(source, rate, pitch, schedule)
        cases.append({
            "id": case_id,
            "kind": kind,
            "mapping": mapping,
            "qualifies": False,
            "evidence_class": SYNTHETIC_CLASS,
        })

    add("C01", "identity_1x", 16000, "1")
    add("C02", "rate_2", 16000, "2")
    add("C03", "rate_half", 16000, "1/2")
    add("C04", "rate_3_4", 16000, "3/4")
    add("C05", "rate_3_2", 16000, "3/2")
    add("C06", "rate_change", 16000, "1/4", schedule=[
        {"start_sample": 0, "end_sample": 4000, "rate": "1"},
        {"start_sample": 4000, "end_sample": 8000, "rate": "3/2"},
        {"start_sample": 8000, "end_sample": 16000, "rate": "3/4"},
    ])
    add("C07", "final_partial_window", 16165, "1")
    add("C08", "envelope_min", 16000, "1/4")
    add("C09", "envelope_max", 16000, "4")
    add("C10", "combined_pitch", 16000, "5/4", pitch=-700)

    summary = {
        "case_count": len(cases),
        "arithmetic_passes": sum(1 for case in cases
                                 if case["mapping"]["output_duration"]),
        "identity_1x_exact": cases[0]["mapping"]["duration_identity"],
        "final_partial_detected":
            cases[6]["mapping"]["final_partial_window"]["partial"],
        "rate_change_contiguous":
            cases[5]["mapping"]["source_mapping_contiguous"],
        "pitch_octave_ratio": pitch_ratio(1200),
        "qualifying_results": 0,
        "vendor_sdk_loaded": False,
        "vendor_runtime_invoked": False,
        "audio_read": False,
        "audio_rendered": False,
        "network_used": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _validate_frame(frame: Any) -> None:
    if not isinstance(frame, list):
        raise ValueError("frame_not_list")
    if len(frame) != FRAME_SAMPLES:
        raise ValueError("wrong_frame_length")
    for sample in frame:
        if isinstance(sample, bool) or not isinstance(sample, (int, float)):
            raise ValueError("sample_not_number")
        if isinstance(sample, float) and not math.isfinite(sample):
            raise ValueError("nonfinite_sample")
        if not (-1.0 <= float(sample) <= 1.0):
            raise ValueError("sample_out_of_range")


def frame_control() -> dict[str, Any]:
    valid = [0] * FRAME_SAMPLES
    mutations: list[tuple[str, Callable[[], Any], str]] = [
        ("F02", lambda: [0] * (FRAME_SAMPLES - 1), "wrong_frame_length"),
        ("F03", lambda: [0] * (FRAME_SAMPLES + 1), "wrong_frame_length"),
        ("F04", lambda: [0.0] * 159 + [float("nan")], "nonfinite_sample"),
        ("F05", lambda: [0.0] * 159 + [float("inf")], "nonfinite_sample"),
        ("F06", lambda: [0.0] * 159 + [float("-inf")], "nonfinite_sample"),
        ("F07", lambda: [0] * 159 + [True], "sample_not_number"),
        ("F08", lambda: [0] * 159 + ["0"], "sample_not_number"),
        ("F09", lambda: [0] * 159 + [None], "sample_not_number"),
        ("F10", lambda: [0] * 159 + [[0]], "sample_not_number"),
        ("F11", lambda: [0] * 159 + [1.5], "sample_out_of_range"),
        ("F12", lambda: [0] * 159 + [-1.5], "sample_out_of_range"),
    ]
    cases: list[dict[str, Any]] = []
    try:
        _validate_frame(valid)
    except ValueError as error:  # pragma: no cover - valid frame is fixed
        raise AssertionError(str(error))
    cases.append({
        "id": "F01",
        "expected_code": None,
        "observed_code": None,
        "status": "accepted",
        "qualifies": False,
    })
    for case_id, maker, expected in mutations:
        observed = None
        status = "accepted"
        try:
            _validate_frame(maker())
        except ValueError as error:
            observed = str(error)
            status = "rejected"
        cases.append({
            "id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": status,
            "qualifies": False,
        })
    summary = {
        "case_count": len(cases),
        "accepted_count": sum(1 for case in cases
                              if case["status"] == "accepted"),
        "rejected_count": sum(1 for case in cases
                              if case["status"] == "rejected"),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "frame_samples": FRAME_SAMPLES,
        "sample_rate_hz": 16000,
        "channels": 1,
        "sample_format": "f32",
        "caller_range": [-1, 1],
        "audio_read": False,
        "vendor_runtime_invoked": False,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def _base_manifest() -> dict[str, Any]:
    return {
        "schema_id": MANIFEST_SCHEMA_ID,
        "run_id": "synthetic-schema-control",
        "vendor": {
            "product": "Bungee Pro",
            "version": "synthetic-control",
            "artifact_sha256": "0" * 64,
            "license_id": "synthetic-license-control",
            "license_sha256": "0" * 64,
            "terms_sha256": "0" * 64,
            "api_identity": "synthetic-api-control",
            "pro_build": True,
        },
        "runtime": {
            "os": "macos",
            "os_version": "synthetic-control",
            "arch": "arm64",
            "package_sha256": "0" * 64,
            "compiler": "synthetic-control",
            "license_key_present": True,
            "pinned": True,
        },
        "audio": {
            "fixture_id": "synthetic-silence",
            "sha256": "0" * 64,
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "total_samples": 16000,
        },
        "mapping": {
            "rate": "5/4",
            "source_duration_samples": 16000,
            "output_duration_samples": 12800,
            "pitch_preserved": True,
            "final_partial_window": 0,
        },
        "controls": [
            {"id": "identity", "kind": "identity_1x", "passes": True},
            {"id": "rate-change", "kind": "rate_change", "passes": True},
        ],
        "rights": {
            "consent_recorded": True,
            "license_execution_approved": True,
            "output_use_defined": True,
            "commercial_use_approved": True,
            "redistribution_approved": True,
            "listening_protocol_approved": True,
        },
    }


def validate_manifest(manifest: Any) -> None:
    if not isinstance(manifest, dict):
        raise ValueError("invalid_type")
    _reject_nonfinite(manifest)
    _require_exact_keys(manifest, MANIFEST_FIELDS)
    if manifest["schema_id"] != MANIFEST_SCHEMA_ID:
        raise ValueError("schema_mismatch")
    _require_slug(manifest["run_id"], "invalid_run_id")

    vendor = manifest["vendor"]
    _require_exact_keys(vendor, VENDOR_FIELDS)
    if vendor["product"] != "Bungee Pro":
        raise ValueError("vendor_product_mismatch")
    _require_slug(vendor["version"], "invalid_slug")
    _require_digest(vendor["artifact_sha256"])
    _require_slug(vendor["license_id"], "invalid_slug")
    _require_digest(vendor["license_sha256"])
    _require_digest(vendor["terms_sha256"])
    _require_slug(vendor["api_identity"], "invalid_slug")
    _require_bool(vendor["pro_build"], "invalid_type")
    if vendor["pro_build"] is not True:
        raise ValueError("not_pro_build")

    runtime = manifest["runtime"]
    _require_exact_keys(runtime, RUNTIME_FIELDS)
    if runtime["os"] not in RUNTIME_OSES:
        raise ValueError("invalid_os")
    _require_slug(runtime["os_version"], "invalid_slug")
    if runtime["arch"] not in HOST_ARCHES:
        raise ValueError("invalid_arch")
    _require_digest(runtime["package_sha256"])
    _require_slug(runtime["compiler"], "invalid_slug")
    _require_bool(runtime["license_key_present"], "invalid_type")
    if runtime["license_key_present"] is not True:
        raise ValueError("license_key_absent")
    _require_bool(runtime["pinned"], "invalid_type")
    if runtime["pinned"] is not True:
        raise ValueError("runtime_not_pinned")

    audio = manifest["audio"]
    _require_exact_keys(audio, AUDIO_FIELDS)
    _require_slug(audio["fixture_id"], "invalid_slug")
    _require_digest(audio["sha256"])
    if not _is_int(audio["sample_rate_hz"]) \
            or audio["sample_rate_hz"] not in AUDIO_SAMPLE_RATES:
        raise ValueError("unsupported_sample_rate")
    if not _is_int(audio["channels"]) or audio["channels"] not in AUDIO_CHANNELS:
        raise ValueError("invalid_channels")
    if not _is_int(audio["frame_samples"]) \
            or audio["frame_samples"] not in AUDIO_FRAME_SAMPLES:
        raise ValueError("unsupported_frame_samples")
    _require_int(audio["total_samples"], "invalid_type")
    if audio["total_samples"] <= 0:
        raise ValueError("invalid_total_samples")

    mapping = manifest["mapping"]
    _require_exact_keys(mapping, MAPPING_FIELDS)
    rate = parse_rate(mapping["rate"])
    _require_int(mapping["source_duration_samples"],
                 "invalid_source_duration")
    if mapping["source_duration_samples"] <= 0:
        raise ValueError("invalid_source_duration")
    _require_int(mapping["output_duration_samples"],
                 "invalid_output_duration")
    if mapping["output_duration_samples"] <= 0:
        raise ValueError("invalid_output_duration")
    expected = Fraction(mapping["source_duration_samples"], 1) / rate
    if mapping["output_duration_samples"] != expected.numerator // expected.denominator:
        raise ValueError("duration_mismatch")
    _require_bool(mapping["pitch_preserved"], "invalid_type")
    if mapping["pitch_preserved"] is not True:
        raise ValueError("pitch_not_preserved")
    _require_int(mapping["final_partial_window"], "invalid_final_partial")
    if mapping["final_partial_window"] < 0:
        raise ValueError("invalid_final_partial")

    controls = manifest["controls"]
    if not isinstance(controls, list):
        raise ValueError("invalid_type")
    if not controls:
        raise ValueError("controls_empty")
    seen: set[str] = set()
    for control in controls:
        _require_exact_keys(control, CONTROL_FIELDS)
        control_id = _require_slug(control["id"], "invalid_control_id")
        if control_id in seen:
            raise ValueError("duplicate_control")
        seen.add(control_id)
        if control["kind"] not in CONTROL_KINDS:
            raise ValueError("invalid_control_kind")
        _require_bool(control["passes"], "invalid_type")
        if control["passes"] is not True:
            raise ValueError("control_failed")

    rights = manifest["rights"]
    _require_exact_keys(rights, RIGHTS_FIELDS)
    for field in RIGHTS_FIELDS:
        _require_bool(rights[field], "invalid_type")
    if not all(rights[field] is True for field in RIGHTS_FIELDS):
        raise ValueError("rights_incomplete")


def assess_manifest(manifest: Any) -> dict[str, Any]:
    validate_manifest(manifest)
    mapping = manifest["mapping"]
    return {
        "schema_valid": True,
        "rights_complete": True,
        "artifact_present": False,
        "admitted": False,
        "qualifies": False,
        "reason": "synthetic_schema_control_no_vendor_artifact",
        "rate": mapping["rate"],
        "source_duration_samples": mapping["source_duration_samples"],
        "output_duration_samples": mapping["output_duration_samples"],
    }


def _mutations() -> list[tuple[str, Callable[[dict[str, Any]], None], str]]:
    def pop_top(manifest: dict[str, Any]) -> None:
        manifest.pop("run_id")

    def unknown_top(manifest: dict[str, Any]) -> None:
        manifest["extra"] = 1

    def wrong_schema(manifest: dict[str, Any]) -> None:
        manifest["schema_id"] = "audio-sdk/other/0.1"

    def empty_run(manifest: dict[str, Any]) -> None:
        manifest["run_id"] = ""

    def bool_run(manifest: dict[str, Any]) -> None:
        manifest["run_id"] = True

    def vendor_list(manifest: dict[str, Any]) -> None:
        manifest["vendor"] = []

    def vendor_missing(manifest: dict[str, Any]) -> None:
        manifest["vendor"].pop("version")

    def vendor_unknown(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["extra"] = 1

    def vendor_product(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["product"] = "Bungee Basic"

    def pro_build_false(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["pro_build"] = False

    def artifact_short(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["artifact_sha256"] = "0" * 40

    def artifact_nonhex(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["artifact_sha256"] = "z" * 64

    def license_digest(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["license_sha256"] = "not-a-digest"

    def api_slug(manifest: dict[str, Any]) -> None:
        manifest["vendor"]["api_identity"] = ""

    def runtime_missing(manifest: dict[str, Any]) -> None:
        manifest["runtime"].pop("arch")

    def runtime_os(manifest: dict[str, Any]) -> None:
        manifest["runtime"]["os"] = "plan9"

    def runtime_arch(manifest: dict[str, Any]) -> None:
        manifest["runtime"]["arch"] = "mips"

    def key_absent(manifest: dict[str, Any]) -> None:
        manifest["runtime"]["license_key_present"] = False

    def runtime_unpinned(manifest: dict[str, Any]) -> None:
        manifest["runtime"]["pinned"] = False

    def package_digest(manifest: dict[str, Any]) -> None:
        manifest["runtime"]["package_sha256"] = "bad"

    def audio_rate(manifest: dict[str, Any]) -> None:
        manifest["audio"]["sample_rate_hz"] = 12345

    def audio_channels_zero(manifest: dict[str, Any]) -> None:
        manifest["audio"]["channels"] = 0

    def audio_channels_bool(manifest: dict[str, Any]) -> None:
        manifest["audio"]["channels"] = True

    def audio_frame(manifest: dict[str, Any]) -> None:
        manifest["audio"]["frame_samples"] = 100

    def audio_total_zero(manifest: dict[str, Any]) -> None:
        manifest["audio"]["total_samples"] = 0

    def audio_total_float(manifest: dict[str, Any]) -> None:
        manifest["audio"]["total_samples"] = 1.5

    def audio_total_nan(manifest: dict[str, Any]) -> None:
        manifest["audio"]["total_samples"] = float("nan")

    def audio_total_bool(manifest: dict[str, Any]) -> None:
        manifest["audio"]["total_samples"] = True

    def audio_digest(manifest: dict[str, Any]) -> None:
        manifest["audio"]["sha256"] = "0" * 63

    def audio_unknown(manifest: dict[str, Any]) -> None:
        manifest["audio"]["extra"] = 1

    def rate_malformed(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["rate"] = "1/0"

    def rate_zero(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["rate"] = "0"

    def rate_high(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["rate"] = "5"

    def rate_nonstring(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["rate"] = 2

    def rate_nan(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["rate"] = "nan"

    def source_zero(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["source_duration_samples"] = 0

    def output_mismatch(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["output_duration_samples"] = 12799

    def output_negative(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["output_duration_samples"] = -1

    def output_float(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["output_duration_samples"] = 12800.5

    def pitch_false(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["pitch_preserved"] = False

    def final_negative(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["final_partial_window"] = -1

    def mapping_unknown(manifest: dict[str, Any]) -> None:
        manifest["mapping"]["extra"] = 1

    def controls_empty(manifest: dict[str, Any]) -> None:
        manifest["controls"] = []

    def controls_dict(manifest: dict[str, Any]) -> None:
        manifest["controls"] = {}

    def control_duplicate(manifest: dict[str, Any]) -> None:
        manifest["controls"].append(dict(manifest["controls"][0]))

    def control_kind(manifest: dict[str, Any]) -> None:
        manifest["controls"][0]["kind"] = "unknown"

    def control_failed(manifest: dict[str, Any]) -> None:
        manifest["controls"][0]["passes"] = False

    def control_id(manifest: dict[str, Any]) -> None:
        manifest["controls"][0]["id"] = ""

    def consent_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["consent_recorded"] = False

    def license_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["license_execution_approved"] = False

    def output_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["output_use_defined"] = False

    def commercial_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["commercial_use_approved"] = False

    def redistribution_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["redistribution_approved"] = False

    def listening_false(manifest: dict[str, Any]) -> None:
        manifest["rights"]["listening_protocol_approved"] = False

    def rights_missing(manifest: dict[str, Any]) -> None:
        manifest["rights"].pop("consent_recorded")

    return [
        ("M01", pop_top, "missing_field"),
        ("M02", unknown_top, "unknown_field"),
        ("M03", wrong_schema, "schema_mismatch"),
        ("M04", empty_run, "invalid_run_id"),
        ("M05", bool_run, "invalid_run_id"),
        ("M06", vendor_list, "invalid_type"),
        ("M07", vendor_missing, "missing_field"),
        ("M08", vendor_unknown, "unknown_field"),
        ("M09", vendor_product, "vendor_product_mismatch"),
        ("M10", pro_build_false, "not_pro_build"),
        ("M11", artifact_short, "invalid_digest"),
        ("M12", artifact_nonhex, "invalid_digest"),
        ("M13", license_digest, "invalid_digest"),
        ("M14", api_slug, "invalid_slug"),
        ("M15", runtime_missing, "missing_field"),
        ("M16", runtime_os, "invalid_os"),
        ("M17", runtime_arch, "invalid_arch"),
        ("M18", key_absent, "license_key_absent"),
        ("M19", runtime_unpinned, "runtime_not_pinned"),
        ("M20", package_digest, "invalid_digest"),
        ("M21", audio_rate, "unsupported_sample_rate"),
        ("M22", audio_channels_zero, "invalid_channels"),
        ("M23", audio_channels_bool, "invalid_channels"),
        ("M24", audio_frame, "unsupported_frame_samples"),
        ("M25", audio_total_zero, "invalid_total_samples"),
        ("M26", audio_total_float, "invalid_type"),
        ("M27", audio_total_nan, "nonfinite_value"),
        ("M28", audio_total_bool, "invalid_type"),
        ("M29", audio_digest, "invalid_digest"),
        ("M30", audio_unknown, "unknown_field"),
        ("M31", rate_malformed, "rate_malformed"),
        ("M32", rate_zero, "rate_out_of_range"),
        ("M33", rate_high, "rate_out_of_range"),
        ("M34", rate_nonstring, "rate_malformed"),
        ("M35", rate_nan, "rate_malformed"),
        ("M36", source_zero, "invalid_source_duration"),
        ("M37", output_mismatch, "duration_mismatch"),
        ("M38", output_negative, "invalid_output_duration"),
        ("M39", output_float, "invalid_output_duration"),
        ("M40", pitch_false, "pitch_not_preserved"),
        ("M41", final_negative, "invalid_final_partial"),
        ("M42", mapping_unknown, "unknown_field"),
        ("M43", controls_empty, "controls_empty"),
        ("M44", controls_dict, "invalid_type"),
        ("M45", control_duplicate, "duplicate_control"),
        ("M46", control_kind, "invalid_control_kind"),
        ("M47", control_failed, "control_failed"),
        ("M48", control_id, "invalid_control_id"),
        ("M49", consent_false, "rights_incomplete"),
        ("M50", license_false, "rights_incomplete"),
        ("M51", output_false, "rights_incomplete"),
        ("M52", commercial_false, "rights_incomplete"),
        ("M53", redistribution_false, "rights_incomplete"),
        ("M54", listening_false, "rights_incomplete"),
        ("M55", rights_missing, "missing_field"),
    ]


def admission_controls() -> dict[str, Any]:
    control_manifest = _base_manifest()
    control = assess_manifest(control_manifest)
    control["accepted"] = True
    control["evidence_class"] = SYNTHETIC_CLASS
    cases: list[dict[str, Any]] = []
    for case_id, mutate, expected in _mutations():
        manifest = json.loads(json.dumps(control_manifest))
        mutate(manifest)
        observed = None
        status = "accepted"
        try:
            validate_manifest(manifest)
        except ValueError as error:
            observed = str(error)
            status = "rejected"
        cases.append({
            "id": case_id,
            "expected_code": expected,
            "observed_code": observed,
            "status": status,
            "state_unchanged": status == "rejected",
            "qualifies": False,
        })
    summary = {
        "case_count": len(cases),
        "rejected_count": sum(1 for case in cases
                              if case["status"] == "rejected"),
        "accepted_schema_controls": 1,
        "all_rejected": all(case["status"] == "rejected" for case in cases),
        "all_codes_match": all(
            case["observed_code"] == case["expected_code"]
            for case in cases),
        "qualifying_results": 0,
        "state_advanced_on_rejection": False,
        "vendor_sdk_loaded": False,
        "vendor_runtime_invoked": False,
        "license_key_used": False,
        "audio_read": False,
        "audio_rendered": False,
        "network_used": False,
        "evidence_class": SYNTHETIC_CLASS,
    }
    return {
        "summary": summary,
        "control": control,
        "cases": cases,
        "qualifies": False,
        "evidence_class": SYNTHETIC_CLASS,
    }


def candidate_note_probe() -> dict[str, Any]:
    path = AUDIO_ROOT / CANDIDATE_NOTE
    present = path.is_file()
    lines = (path.read_text(encoding="utf-8").splitlines()
             if present else [])

    def find(marker: str) -> int | None:
        for index, line in enumerate(lines, start=1):
            if marker in line:
                return index
        return None

    matrix_line = find(CANDIDATE_MATRIX_MARKER)
    section_line = find(CANDIDATE_SECTION_MARKER)
    basic_link_line = find(CANDIDATE_BASIC_LINK_MARKER)
    licence_table_line = None
    for index, line in enumerate(lines, start=1):
        if line.startswith("| Commercial |") and "Bungee Pro" in line:
            licence_table_line = index
            break
    section_text = ""
    if section_line is not None:
        section_text = "\n".join(lines[section_line - 1:
                                        min(section_line + 20, len(lines))])
    not_verified_line = None
    pricing_line = None
    for index, line in enumerate(lines, start=1):
        if "No local build or benchmark" in line and "Bungee Pro" in line:
            not_verified_line = index
        if "No pricing, contract terms or patent indemnity" in line \
                and "Bungee Pro" in line:
            pricing_line = index
    matrix_text = lines[matrix_line - 1] if matrix_line else ""
    return {
        "path": CANDIDATE_NOTE,
        "present": present,
        "line": matrix_line,
        "section_line": section_line,
        "basic_link_line": basic_link_line,
        "licence_table_line": licence_table_line,
        "not_verified_line": not_verified_line,
        "pricing_line": pricing_line,
        "matrix_record": matrix_text,
        "section_heading": (lines[section_line - 1]
                            if section_line else ""),
        "records_commercial_licence": "| Commercial |" in matrix_text,
        "records_proprietary_algorithms":
            "proprietary algorithms" in section_text,
        "records_simd_targets":
            "SIMD optimisations" in section_text,
        "records_professional_support":
            "professional support" in section_text,
        "records_basic_repository_link": basic_link_line is not None,
        "records_pro_dedicated_link":
            "described in the Bungee README" not in section_text,
        "records_latency_as_similar_to_basic":
            "Similar to Basic" in matrix_text,
        "records_rate_control": "Yes" in matrix_text,
        "records_no_local_evaluation": not_verified_line is not None,
        "records_no_pricing_terms_or_patent_indemnity":
            pricing_line is not None,
        "records_upgrade_path": "Upgrade path" in matrix_text,
        "implementation_source_recorded": False,
        "api_identity_recorded": False,
        "numeric_bounds_recorded": False,
        "defaults_recorded": False,
        "audio_read_here": False,
        "network_used_here": False,
        "not_reproduced_here": True,
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
    }


def documented_parameter_envelope() -> dict[str, Any]:
    return {
        "source": CANDIDATE_NOTE + " §2.1 and §3.8",
        "evidence_class": "source_reported_provenance_not_remeasured",
        "product": "Bungee Pro",
        "commercial_upgrade_recorded": True,
        "proprietary_algorithms_recorded": True,
        "simd_targets_recorded": [
            "WebAudioWorklet SIMD128 WebAssembly",
            "Arm NEON",
            "x86-64 SIMD",
        ],
        "professional_support_recorded": True,
        "rate": {
            "min": None,
            "max": None,
            "default": None,
            "unit": "ratio",
            "numeric_bounds_recorded": False,
            "semantics_verified_here": False,
        },
        "pitch": {
            "min": None,
            "max": None,
            "default": None,
            "unit": "unrecorded",
            "numeric_bounds_recorded": False,
            "semantics_verified_here": False,
        },
        "api_identity_recorded": False,
        "latency_numeric_recorded_for_pro": False,
        "defaults_recorded_in_candidate_note": False,
        "numeric_bounds_recorded_in_candidate_note": False,
        "local_evaluation_recorded": False,
        "pricing_terms_or_patent_indemnity_verified": False,
        "semantics_verified_here": False,
        "qualifies": False,
    }


def synthetic_control_envelope() -> dict[str, Any]:
    return {
        "evidence_class": SYNTHETIC_CLASS,
        "purpose": "control constants used only to validate the synthetic "
                   "manifest; they are not vendor evidence and assert no "
                   "Bungee Pro range",
        "rate_min": "1/4",
        "rate_max": "4",
        "pitch_cents_min": CONTROL_PITCH_MIN,
        "pitch_cents_max": CONTROL_PITCH_MAX,
        "partial_block_samples": PARTIAL_BLOCK,
        "defaults_recorded": False,
        "qualifies": False,
    }


def source_presence() -> dict[str, Any]:
    present = [probe for probe in PRO_ARTIFACT_PROBES
               if (AUDIO_ROOT / probe).exists()]
    note = candidate_note_probe()
    return {
        "probe_scope": "project workspace only; host SDK installations, "
                       "license stores, vendor portals and user profiles are "
                       "not inspected or invoked",
        "pro_artifact_probes": list(PRO_ARTIFACT_PROBES),
        "present_probes": present,
        "candidate_note_present": note["present"],
        "candidate_note_is_implementation": False,
        "candidate_note_records_proprietary_algorithms":
            note["records_proprietary_algorithms"],
        "candidate_note_records_commercial_licence":
            note["records_commercial_licence"],
        "candidate_note_records_no_local_evaluation":
            note["records_no_local_evaluation"],
        "pro_artifact_present": bool(present),
        "implementation_source_present": False,
        "runtime_manifest_present": False,
        "license_text_present": False,
        "license_key_present": False,
        "measured_render_trace_present": False,
        "rights_cleared_cohort_present": False,
        "listening_record_present": False,
        "device_timing_record_present": False,
        "licensed_implementation_runtime_present": False,
        "exact_licensed_source_weights_runtime_present": False,
        "vendor_artifact_present": False,
        "admitted": False,
        "network_used": False,
        "download_attempted": False,
        "runtime_imported": False,
        "vendor_runtime_invoked": False,
        "audio_read": False,
        "audio_played": False,
        "presence_is_not_admission": True,
        "qualifies": False,
    }


def license_findings() -> dict[str, Any]:
    note = candidate_note_probe()
    return {
        "candidate_note_records_commercial_licence":
            note["records_commercial_licence"],
        "candidate_note_records_no_pricing_terms":
            note["records_no_pricing_terms_or_patent_indemnity"],
        "pro_license_text_present": False,
        "executed_agreement_present": False,
        "pricing_terms_present": False,
        "patent_indemnity_reviewed": False,
        "terms_reviewed": False,
        "redistribution_approved": False,
        "derivative_output_use_approved": False,
        "commercial_use_approved": False,
        "output_use_defined": False,
        "qualifies": False,
    }


def vendor_record() -> dict[str, Any]:
    return {
        "product": "Bungee Pro",
        "type": "Commercial Bungee upgrade",
        "licence": "Commercial",
        "commercial_use": "Yes, paid",
        "real_time": "Yes",
        "rate_change": "Yes",
        "latency": "Similar to Basic",
        "integration_effort": "Low if Basic is integrated",
        "verdict": "Upgrade path",
        "pro_section_present": True,
        "pro_dedicated_link_recorded": False,
        "basic_repository_recorded": True,
        "vendor_claims_only": True,
        "local_evaluation": False,
        "measured_quality_result": False,
        "pricing_terms_verified": False,
        "patent_indemnity_verified": False,
        "evidence_class": "source_reported_provenance_not_remeasured",
        "qualifies": False,
    }


def basic_substitution_guard() -> dict[str, Any]:
    return {
        "basic_evidence_path": "docs/task-evidence/bungee-basic/report.json",
        "basic_license": "MPL-2.0",
        "basic_is_pro": False,
        "basic_used_here": False,
        "substitution_allowed": False,
        "reason": "Open-source Bungee Basic is a different implementation "
                  "and licence; it cannot stand in for the proprietary "
                  "Bungee Pro artifact, its API identity or its rights.",
        "qualifies": False,
    }


def _pin_map(pins: dict[str, str], root: Path) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for relative, expected in sorted(pins.items()):
        path = root / relative
        actual = sha256_file(path) if path.is_file() else None
        result[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return result


def verify_pins() -> tuple[dict[str, Any], dict[str, Any], dict[str, Any]]:
    return (
        _pin_map(SOURCE_PINS, AUDIO_ROOT),
        _pin_map(BOUNDARY_PINS, WORKTREE),
        _pin_map(SIBLING_PINS, WORKTREE),
    )


def linked_rows_digest() -> str:
    return object_digest(list(LINKED_ROWS))


def board_row_projection(path: Path) -> dict[str, Any]:
    data = read_strict_json(path)
    if not isinstance(data, dict) or not isinstance(data.get("tasks"), list):
        raise ValueError("board_shape_invalid")
    for row in data["tasks"]:
        if isinstance(row, dict) and row.get("id") == TASK:
            missing = [field for field in BOARD_ROW_FIELDS if field not in row]
            if missing:
                raise ValueError("board_row_missing_fields")
            return {field: row[field] for field in BOARD_ROW_FIELDS}
    raise ValueError("board_row_missing")


def board_row_digest(projection: Any) -> str:
    return object_digest(projection)


def _required_artifacts() -> list[dict[str, Any]]:
    rows = (
        ("A01", "licensed Bungee Pro SDK/binary/source package with exact "
                "version and full SHA-256", "BLK-01"),
        ("A02", "exact Bungee Pro build identity and Pro API identity",
         "BLK-01"),
        ("A03", "executed commercial licence, entitlement and license key "
                "for the exact Pro build", "BLK-02"),
        ("A04", "reviewed vendor terms for local execution, benchmarking, "
                "redistribution, derivative output use, commercial use and "
                "patent indemnity", "BLK-02"),
        ("A05", "pinned host, toolchain, link mode, install record and "
                "license-key handling", "BLK-03"),
        ("A06", "official Pro rate/pitch/latency/rate-change/final-partial "
                "geometry and integration contract", "BLK-04"),
        ("A07", "measured offline render trace with source/output mapping, "
                "duration, pitch, transients, buffering, rebuffer, drift and "
                "final partial window", "BLK-04"),
        ("A08", "rights-cleared unfamiliar-speech, music and silence cohort "
                "with output-use terms and matched controls", "BLK-05"),
        ("A09", "approved preservation scorer, stratified speech results and "
                "blind listening protocol/record", "BLK-05"),
        ("A10", "target-device timing/resources, opt-in adapter intake with "
                "OFF default, benchmark review and release approval",
         "BLK-06"),
    )
    return [{
        "id": artifact_id,
        "name": name,
        "blocker": blocker,
        "present": False,
        "verified": False,
        "licensed": False,
        "admitted": False,
        "blocked": True,
        "sha256": None,
    } for artifact_id, name, blocker in rows]


def _exact_blockers() -> list[dict[str, Any]]:
    rows = (
        ("BLK-01", "A01",
         "The exact licensed Bungee Pro distribution artifact is absent. No "
         "Pro SDK package, binary, source snapshot, version, build identity "
         "or full SHA-256 exists in the project workspace. The only Bungee "
         "checkout/evidence is open-source Basic (MPL-2.0), which is not Pro.",
         "Supply the exact Pro version/build, immutable acquisition record "
         "and full SHA-256 of every supplied file, then admit the Pro API "
         "identity."),
        ("BLK-02", "A03",
         "No executed commercial licence, entitlement, license key or "
         "reviewed terms exist. The candidate note explicitly says that no "
         "pricing, contract terms or patent indemnity for Bungee Pro were "
         "verified.",
         "Supply the signed agreement and written review covering execution, "
         "benchmarking, redistribution, derivative output use, commercial "
         "use and patent indemnity for the exact Pro build."),
        ("BLK-03", "A05",
         "No pinned host, toolchain, link/install record or license-key "
         "handling exists for the proprietary Pro package. There is no "
         "verified Pro ABI/API beyond the commercial-upgrade description.",
         "Supply the exact OS/architecture/compiler/link mode, install "
         "location, key handling, ABI/API compatibility record and a "
         "reproducible package install or build record."),
        ("BLK-04", "A06",
         "No official Pro geometry or measured render trace exists. The "
         "candidate note records only vendor claims and 'Similar to Basic'; "
         "it records no numeric Pro rate/pitch bounds, defaults, latency or "
         "algorithm semantics.",
         "Supply a pinned Pro parameter/geometry reference and an exact "
         "offline trace covering 1x, rate changes, pitch, transients, "
         "buffering, rebuffer, drift and the final partial window."),
        ("BLK-05", "A08",
         "No rights-cleared playback cohort, consent record, output-use "
         "grant, matched controls or approved preservation/listening scorer "
         "exists.",
         "Supply an immutable consented unfamiliar-speech/music/silence "
         "cohort with output-use terms, matched controls, an approved "
         "preservation scorer and an authorized blind listening protocol."),
        ("BLK-06", "A10",
         "No Rate-profile acceptance results, target-device timing, resource "
         "telemetry, separate opt-in adapter intake, independent review or "
         "release approval exists.",
         "Supply measured Rate-profile evidence, target-device timing and "
         "resources, an opt-in adapter implementation with OFF default, "
         "independent exact-head review and release approval."),
    )
    return [{
        "id": blocker_id,
        "artifact_id": artifact_id,
        "status": "open",
        "missing": missing,
        "required_action": action,
        "qualifies": False,
    } for blocker_id, artifact_id, missing, action in rows]


def _release_gates(linked_row: dict[str, Any]) -> list[dict[str, Any]]:
    rows = (
        ("RG-01", "licensed Bungee Pro artifact identity",
         "Exact Pro version/build, immutable acquisition record and full "
         "SHA-256 of every supplied file."),
        ("RG-02", "commercial licence and rights decision",
         "Executed agreement and written review of execution, benchmarking, "
         "redistribution, derivative output use, commercial use and patent "
         "indemnity."),
        ("RG-03", "pinned host, toolchain, API and key handling",
         "Exact OS/architecture/compiler/link mode, install record, Pro API "
         "identity, ABI compatibility and license-key handling."),
        ("RG-04", "official Pro geometry and latency contract",
         "Vendor-pinned rate, pitch, latency, rate-change, buffering and "
         "final-partial semantics for the exact Pro build."),
        ("RG-05", "rights-cleared playback cohort",
         "Immutable consented unfamiliar-speech, music and silence cohort "
         "with output-use terms and matched controls."),
        ("RG-06", "Rate acceptance profile",
         "Measured 1x, source/output mapping, duration, pitch, transient, "
         "buffering, rebuffer, drift and final-partial results."),
        ("RG-07", "speech preservation and independent scoring",
         "Approved preservation scorer or labels, stratified speech results "
         "and authorized blind listening."),
        ("RG-08", "device timing, opt-in intake and release",
         "Target-device timing/resources, separate opt-in adapter intake "
         "with OFF default, benchmark review and release approval."),
    )
    return [{
        "id": gate_id,
        "title": title,
        "status": "blocked",
        "qualifies": False,
        "reopen_condition": condition,
        "linked_row": linked_row,
    } for gate_id, title, condition in rows]


def _rate_profile_rows() -> list[dict[str, Any]]:
    rows = (
        ("RATE-01", "1x control",
         "No measured Bungee Pro 1x render or identity control exists."),
        ("RATE-02", "source/output mapping and rate changes",
         "Only synthetic caller-clock arithmetic exists; no Pro mapping "
         "trace or rate-change run exists."),
        ("RATE-03", "duration identity and error",
         "No measured Pro output duration or rational error exists."),
        ("RATE-04", "pitch",
         "No rendered waveform or pitch measurement exists for Pro."),
        ("RATE-05", "transient audibility",
         "Vendor transient claims are unverified; no waveform analysis or "
         "listening exists."),
        ("RATE-06", "playback buffering, rebuffer and drift",
         "No Pro audio clock, fill/flush, rebuffer or drift run exists."),
        ("RATE-07", "unfamiliar speech, music and silence",
         "No rights-cleared stratified playback cohort exists."),
        ("RATE-08", "final partial window and speech preservation",
         "Only synthetic final-window arithmetic exists; no Pro render or "
         "preservation score exists."),
    )
    return [{
        "id": row_id,
        "requirement": requirement,
        "status": "blocked",
        "qualifies": False,
        "evidence": evidence,
    } for row_id, requirement, evidence in rows]


def _rate_outcomes() -> list[dict[str, Any]]:
    requirements = (
        "1x control", "source/output mapping and rate changes",
        "duration identity and error", "pitch", "transient audibility",
        "playback buffering, rebuffer and drift",
        "unfamiliar speech, music and silence",
        "final partial window and speech preservation",
    )
    return [{
        "id": f"OUT-{index:02d}",
        "requirement": requirement,
        "status": "blocked",
        "value": None,
        "qualifies": False,
    } for index, requirement in enumerate(requirements, start=1)]


def _qualification() -> dict[str, Any]:
    return {
        "status": "not_qualified",
        "decision": "DEFER",
        "proposal_only": True,
        "evidence_status": "incomplete",
        "licensed_implementation_runtime_present": False,
        "vendor_artifact_present": False,
        "candidate_note_present": True,
        "blocked_release_gates": 8,
        "open_blockers": 6,
        "qualifying_results": 0,
        "reasons": [
            "no licensed Bungee Pro artifact, version, build identity or "
            "SHA-256 exists in the workspace",
            "no executed commercial licence, terms review, license key or "
            "patent-indemnity decision exists",
            "no pinned Pro host/toolchain, API/ABI identity or key handling "
            "exists",
            "no official Pro geometry or measured render trace exists",
            "no rights-cleared cohort, preservation scorer or listening "
            "result exists",
            "no Rate-profile acceptance, device timing, opt-in intake or "
            "release review exists",
        ],
    }


def build_contract() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    return {
        "schema_id": CONTRACT_ID,
        "contract_version": "0.1",
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "base_commit": BASE_COMMIT,
        "branch": BRANCH,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification": core["qualification"],
        "qualification_status": "not_qualified",
        "disposition": core["disposition"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_parameter_envelope":
            core["documented_parameter_envelope"],
        "synthetic_control_envelope": core["synthetic_control_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "release_gates": core["gates"],
        "rate_profile_requirements": core["rate_profile"]["rows"],
        "rate_outcomes": core["rate_outcomes"]["rows"],
        "linked_row_projection": projection,
        "linked_row_projection_sha256": board_row_digest(projection),
        "linked_rows": core["linked_row_identity"]["linked_rows"],
        "linked_rows_sha256": core["linked_row_identity"]["linked_rows_sha256"],
        "board_file_pinned": False,
        "board_status_is_observation_only": True,
        "source_pins": dict(SOURCE_PINS),
        "boundary_pins": dict(BOUNDARY_PINS),
        "sibling_pins": dict(SIBLING_PINS),
        "basic_substitution_guard": core["observed_provenance"][
            "basic_substitution_guard"],
        "vendor_record": core["observed_provenance"]["vendor_record"],
    }


def _report_core(projection: dict[str, Any],
                 linked_row: dict[str, Any]) -> dict[str, Any]:
    return {
        "qualification": _qualification(),
        "disposition": {
            "decision": "DEFER",
            "status": "incomplete",
            "proposal_only": True,
            "qualification_status": "not_qualified",
            "qualifying_results": 0,
            "blocked_before": "implementation_or_intake",
            "blocked_release_gates": 8,
        },
        "boundary": {
            "provider_registration": False,
            "descriptor_or_registry_change": False,
            "default_change": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
            "board_or_handoff_change": False,
            "external_assets_copied": False,
            "task_local_only": True,
            "installed_v0_geometry": {
                "sample_rate_hz": 16000,
                "channels": 1,
                "sample_format": "f32",
                "frame_samples": 160,
                "unchanged": True,
            },
        },
        "public_v0_geometry": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "sample_format": "f32",
            "frame_samples": 160,
        },
        "scope": {
            "directory": TASK_PREFIX,
            "task_local_only": True,
            "network_used": False,
            "download_attempted": False,
            "vendor_sdk_copied": False,
            "vendor_runtime_imported": False,
            "vendor_runtime_invoked": False,
            "license_key_used": False,
            "audio_read": False,
            "audio_played": False,
            "render_produced": False,
            "listening_conducted": False,
            "device_timing_measured": False,
            "benchmark_run": False,
            "benchmark_claim": False,
            "release_claim": False,
            "provider_registration": False,
            "descriptor_registry_change": False,
            "default_selected": False,
            "installed_v0_behavior_change": False,
            "public_api_abi_change": False,
            "shared_build_or_ci_change": False,
        },
        "non_claims": [
            "No result in this package is a qualification, benchmark or "
            "release.",
            "Bungee Pro is a proprietary commercial product; no vendor "
            "source, binary, SDK package, model, licence key or licence text "
            "was copied, imported, loaded or reconstructed.",
            "The open-source Bungee Basic implementation and evidence are "
            "not Bungee Pro and were not used as a substitute, parity oracle "
            "or measured baseline.",
            "No numeric Pro rate, pitch, latency, API or defaults were "
            "verified; the candidate note records vendor claims only.",
            "No audio was read or played; no cohort, consent or output-use "
            "grant exists.",
            "No rate, duration, pitch, transient, buffering, rebuffer, drift "
            "or final-partial result was rendered or measured.",
            "No listening, target-device timing, resource, benchmark or "
            "release review was performed.",
            "No provider, descriptor, registry, default, installed-v0, ABI, "
            "shared-build, CI, board or handoff file is changed.",
        ],
        "observed_provenance": {
            "candidate_note": candidate_note_probe(),
            "vendor_record": vendor_record(),
            "basic_substitution_guard": basic_substitution_guard(),
            "sibling_evidence": [dict(row) for row in LINKED_ROWS],
        },
        "documented_parameter_envelope": documented_parameter_envelope(),
        "synthetic_control_envelope": synthetic_control_envelope(),
        "source_presence": source_presence(),
        "license_findings": license_findings(),
        "required_artifacts": _required_artifacts(),
        "exact_blockers": _exact_blockers(),
        "required_results": {
            "licensed_pro_artifact_admitted": False,
            "commercial_license_and_rights_reviewed": False,
            "pinned_host_api_and_key_handling_admitted": False,
            "official_pro_geometry_admitted": False,
            "measured_render_trace_present": False,
            "measured_rate_acceptance_profile": False,
            "rights_cleared_cohort_present": False,
            "speech_preservation_measured": False,
            "listening_measured": False,
            "device_timing_measured": False,
            "provider_intake_approved": False,
            "release_approved": False,
            "no_result_qualifies": True,
        },
        "reproduction": {
            "commands": [
                "export PYTHONDONTWRITEBYTECODE=1",
                "python3 run.py all",
                "python3 -m unittest -v test_reference.py",
                "python3 verify.py",
            ],
            "python": "3.11 or newer, standard library only",
            "repeat_count": 3,
            "byte_identical_required": True,
            "network_used": False,
        },
        "gates": _release_gates(linked_row),
        "rate_profile": {
            "profile": PROFILE,
            "profile_label": PROFILE_LABEL,
            "rows": _rate_profile_rows(),
        },
        "rate_outcomes": {"rows": _rate_outcomes()},
        "linked_row_identity": {
            "projection": projection,
            "sha256": board_row_digest(projection),
            "gating": "stable_identity_only",
            "board_file_pinned": False,
            "board_status_gates_anything": False,
            "linked_rows": [dict(row) for row in LINKED_ROWS],
            "linked_rows_sha256": linked_rows_digest(),
        },
    }


def build_report() -> dict[str, Any]:
    projection = board_row_projection(AUDIO_ROOT / BOARD_TASK_ROW)
    linked_row = dict(projection)
    core = _report_core(projection, linked_row)
    contract = build_contract()
    source_pins, boundary_pins, sibling_pins = verify_pins()
    return {
        "schema_id": REPORT_SCHEMA_ID,
        "task": TASK,
        "title": TASK_TITLE,
        "component": COMPONENT_ID,
        "mode": MODE,
        "branch": BRANCH,
        "base_commit": BASE_COMMIT,
        "reviewer": REVIEWER,
        "profile": PROFILE,
        "profile_label": PROFILE_LABEL,
        "decision": "DEFER",
        "status": "incomplete",
        "proposal_only": True,
        "qualification_status": "not_qualified",
        "contract_sha256": object_digest(contract),
        "disposition": core["disposition"],
        "qualification": core["qualification"],
        "boundary": core["boundary"],
        "public_v0_geometry": core["public_v0_geometry"],
        "scope": core["scope"],
        "non_claims": core["non_claims"],
        "observed_provenance": core["observed_provenance"],
        "documented_parameter_envelope":
            core["documented_parameter_envelope"],
        "synthetic_control_envelope": core["synthetic_control_envelope"],
        "source_presence": core["source_presence"],
        "license_findings": core["license_findings"],
        "required_artifacts": core["required_artifacts"],
        "exact_blockers": core["exact_blockers"],
        "required_results": core["required_results"],
        "reproduction": core["reproduction"],
        "gates": core["gates"],
        "rate_profile": core["rate_profile"],
        "rate_outcomes": core["rate_outcomes"],
        "linked_row_identity": core["linked_row_identity"],
        "board_snapshot": {
            "path": BOARD_TASK_ROW,
            "mutable": True,
            "note": "Mutable board path recorded for provenance only; never "
                    "hashed, gated or treated as a result.",
        },
        "source_pins": source_pins,
        "boundary_pins": boundary_pins,
        "sibling_pins": sibling_pins,
        "gate_control": gate_control(),
        "frame_control": frame_control(),
        "admission": admission_controls(),
        "basic_substitution_guard":
            core["observed_provenance"]["basic_substitution_guard"],
        "vendor_record": core["observed_provenance"]["vendor_record"],
    }


def canonical_report(report: dict[str, Any]) -> tuple[str, str]:
    payload = canonical_bytes(report)
    return payload.decode("ascii"), sha256_bytes(payload)


def validate_contract(contract: Any) -> None:
    if not isinstance(contract, dict):
        raise ValueError("contract_not_object")
    required = (
        "schema_id", "contract_version", "task", "component", "decision",
        "status", "proposal_only", "qualification_status", "disposition",
        "boundary", "scope", "non_claims", "release_gates",
        "rate_profile_requirements", "rate_outcomes", "linked_row_projection",
        "source_pins", "boundary_pins", "sibling_pins",
        "basic_substitution_guard", "vendor_record", "board_file_pinned",
        "board_status_is_observation_only",
    )
    missing = [field for field in required if field not in contract]
    if missing:
        raise ValueError("contract_missing_fields")
    if contract["schema_id"] != CONTRACT_ID:
        raise ValueError("contract_schema_mismatch")
    if contract["task"] != TASK or contract["component"] != COMPONENT_ID:
        raise ValueError("contract_identity_mismatch")
    if contract["decision"] != "DEFER" or contract["status"] != "incomplete":
        raise ValueError("contract_disposition_mismatch")
    if contract["qualification_status"] != "not_qualified":
        raise ValueError("contract_qualification_mismatch")
    if contract["board_file_pinned"] is not False:
        raise ValueError("contract_board_pinned")
    if len(contract["release_gates"]) != 8:
        raise ValueError("contract_gate_count")
    if len(contract["rate_profile_requirements"]) != 8:
        raise ValueError("contract_rate_row_count")
    if len(contract["rate_outcomes"]) != 8:
        raise ValueError("contract_rate_outcome_count")
    if BOARD_TASK_ROW in contract["source_pins"]:
        raise ValueError("contract_board_pinned")


def verify_sources_manifest(payload: bytes) -> int:
    checked = 0
    for line in payload.decode("ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        parts = line.split("  ", 1)
        if len(parts) != 2 or not HEX64.match(parts[0]):
            raise ValueError("sources_malformed")
        digest, name = parts
        if name.startswith("source:"):
            path = AUDIO_ROOT / name[len("source:"):]
        elif name.startswith("boundary:") or name.startswith("sibling:"):
            path = WORKTREE / name.split(":", 1)[1]
        else:
            path = WORKTREE / name
        if not path.is_file():
            raise ValueError("sources_missing:" + name)
        if sha256_file(path) != digest:
            raise ValueError("sources_mismatch:" + name)
        checked += 1
    if BOARD_TASK_ROW in payload.decode("ascii"):
        raise ValueError("sources_board_pinned")
    return checked
