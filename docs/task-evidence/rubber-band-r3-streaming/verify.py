# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify the task-local rubber-band R3 streaming evidence bundle."""

from __future__ import annotations

import json
from pathlib import Path

import fixture
import reference

TASK_DIR = Path(__file__).resolve().parent
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
SOURCES_FILE = TASK_DIR / "SOURCES.sha256"
HEADER_FILE = TASK_DIR / "provider" / "expected_vectors.h"


def fail(message: str) -> None:
    raise SystemExit(message)


def load_json(path: Path) -> dict:
    return fixture.strict_load(path)


def check_pins(report: dict) -> None:
    fresh = {
        "source_pins": fixture.verify_source_pins(),
        "boundary_pins": fixture.verify_boundary_pins(),
        "frozen_fixtures": fixture.verify_frozen_fixtures(),
    }
    for section, recomputed in fresh.items():
        recorded = report.get(section)
        if not isinstance(recorded, dict) or set(recorded) != set(recomputed):
            fail(f"{section} does not match the recomputed task-local inputs")
        for name, row in recomputed.items():
            if recorded[name] != row or not row.get("verified") or \
                    row.get("sha256") != row.get("actual"):
                fail(f"unverified {section}:{name}")
    board = report["board_snapshot"]
    if not board.get("mutable") or "actual" in board:
        fail("board snapshot must be mutable read-time provenance only")


def check_report(report: dict) -> str:
    text, digest = reference.canonical_report(report)
    if REPORT_FILE.read_text(encoding="utf-8") != text + "\n":
        fail("report.json is not strict canonical form")
    sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()
    if sidecar != digest:
        fail("report sidecar digest mismatch")
    if report.get("status") != "proposal_only_not_qualified":
        fail("report status must be proposal_only_not_qualified")
    if report.get("disposition") != "incomplete":
        fail("report disposition must be incomplete")
    q = report.get("qualification", {})
    if q.get("decision") != "DEFER" or q.get("candidate_qualified") is not False:
        fail("qualification must be DEFER and not qualified")
    if q.get("processor_exposure") != "deferred":
        fail("processor exposure must be deferred")
    if q.get("missing_result_promoted") is not False:
        fail("missing_result_promoted must be false")
    if report.get("task", {}).get("base_commit") != reference.BASE_COMMIT:
        fail("base commit mismatch")
    tool = report.get("tool_profile", {})
    if tool.get("environment_independent") is not True:
        fail("tool profile must be environment independent")
    for key in ("install_location", "runner_python", "runner_platform"):
        if key in tool:
            fail(f"tool profile must not record environment data: {key}")
    scope = report.get("scope", {})
    for key in ("task_local_only", "public_surface_changed", "installed_behavior_changed",
                "descriptor_or_registry_changed", "shared_cmake_changed",
                "board_or_handoff_changed", "real_rubber_band_source_or_binary",
                "model_weights", "licensed_runtime", "real_corpus",
                "playback_device", "listening_or_release_claim"):
        expected = True if key == "task_local_only" else False
        if scope.get(key) is not expected:
            fail(f"scope flag {key} must be {expected}")
    return digest


def check_header(report: dict) -> None:
    expected = report["c_boundary_expected"]
    if expected.get("parity_scope") != "process_bytes_and_frame_shape_only":
        fail("C parity must be limited to process bytes and frame shape")
    if (expected.get("v0_source_mapping") != "unsupported" or
            expected.get("v0_tail_drain") != "unsupported"):
        fail("C evidence must not claim v0 source mapping or tail/drain conformance")
    for key in ("drain_non_content_samples", "first_output_source_samples"):
        if key in expected:
            fail(f"C evidence must not claim {key}")
    header = HEADER_FILE.read_text(encoding="utf-8")
    required = [
        'SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes',
        'SPDX' '-License-Identifier: Apache-2.0',
        f'#define RB3_EXPECTED_CONTENT_DIGEST "{expected["content_digest"]}"',
        f'#define RB3_EXPECTED_CONTENT_SAMPLES {expected["content_samples"]}',
        f'#define RB3_EXPECTED_FRAME_COUNT {expected["frames"]}',
        f'#define RB3_EXPECTED_FIRST_OUTPUT_FRAME {expected["first_output_frame"]}',
        f'#define RB3_EXPECTED_PROVIDER_SOURCE_DIGEST "{expected["provider_source_digest"]}"',
        f'#define RB3_EXPECTED_CONFIG_DIGEST "{expected["config_digest"]}"',
    ]
    for needle in required:
        if needle not in header:
            fail(f"header missing {needle}")
    counts = ", ".join(str(value) for value in expected["valid_counts"])
    if f"{{{counts}}}" not in header:
        fail("header valid-count array mismatch")


def check_sources(report_digest: str) -> None:
    manifest = fixture.read_sources_manifest()
    expected = {}
    for path in sorted(TASK_DIR.rglob("*")):
        relative = path.relative_to(TASK_DIR).as_posix()
        if relative == "SOURCES.sha256" or "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        if path.is_file():
            expected[relative] = reference.sha256_file(path)
    if manifest != expected:
        fail("SOURCES.sha256 does not match task-local tree")
    document = json.loads((TASK_DIR / "contract.json").read_text(encoding="utf-8"))
    if document["base_commit"] != reference.BASE_COMMIT:
        fail("contract base commit mismatch")
    sidecar = SIDECAR_FILE.read_text(encoding="ascii").strip()
    if sidecar != report_digest:
        fail("sidecar/report digest mismatch")


def check_invalid(report: dict) -> None:
    invalid = report.get("invalid_and_adverse")
    executed = reference.invalid_cases()
    if not isinstance(invalid, dict) or invalid != executed:
        fail("invalid/adverse outcomes must come from executed rejection paths")
    for label, row in invalid.items():
        if row.get("status") != "rejected" or not row.get("code"):
            fail(f"invalid case not rejected by execution: {label}")
        if row.get("candidate_qualified") is not False:
            fail(f"invalid case qualified: {label}")


def check_rebuffer(report: dict) -> None:
    rebuffer = report.get("rate_profile", {}).get("rebuffer", {})
    trace = rebuffer.get("trace", {})
    gaps = trace.get("gap_rows", [])
    if not gaps or trace.get("gap_frames") <= 0:
        fail("rebuffer trace has no input interruption")
    if any(trace["rows"][index]["input_frame_start"] is not None
           for index in gaps):
        fail("rebuffer interruption still accepts input frames")
    if trace.get("gap_delivered_samples", 0) <= 0:
        fail("rebuffer interruption never drains the FIFO")
    if trace.get("refill_first_delivered", 0) <= 0:
        fail("rebuffer trace never refills after the interruption")
    if trace.get("device_pacing_measured") is not False:
        fail("rebuffer trace must not claim device pacing")


def check_identity_and_replay(report: dict) -> None:
    streaming = report.get("streaming", {})
    chunking = streaming.get("chunking", {})
    if chunking.get("byte_identical") is not True:
        fail("chunked/single-stream identity must be true")
    replay = streaming.get("reset_replay", {})
    if replay.get("state_replay_identical") is not True:
        fail("reset/replay state must be identical")
    if replay.get("source_offset_respected") is not True:
        fail("reset/replay must respect source offset")


def main() -> int:
    report = load_json(REPORT_FILE)
    digest = check_report(report)
    check_pins(report)
    check_header(report)
    check_sources(digest)
    check_invalid(report)
    check_rebuffer(report)
    check_identity_and_replay(report)
    for path in (TASK_DIR / "contract.json", TASK_DIR / "adapter.json", TASK_DIR / "provider.json"):
        load_json(path)
    print(f"verify_ok report_digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
