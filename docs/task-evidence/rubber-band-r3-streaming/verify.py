# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify the task-local rubber-band R3 streaming evidence bundle."""

from __future__ import annotations

import json
import sys
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
    for section in ("source_pins", "boundary_pins"):
        for relative, row in report[section].items():
            if not row.get("verified") or row.get("sha256") != row.get("actual"):
                fail(f"unverified pin {section}:{relative}")
    board = report["board_snapshot"]
    if not board.get("mutable"):
        fail("board snapshot must be mutable provenance")
    for name, row in report["frozen_fixtures"].items():
        if not row.get("verified") or row.get("sha256") != row.get("actual"):
            fail(f"unverified frozen fixture {name}")


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
    header = HEADER_FILE.read_text(encoding="utf-8")
    required = [
        'SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes',
        'SPDX' '-License-Identifier: Apache-2.0',
        f'#define RB3_EXPECTED_CONTENT_DIGEST "{expected["content_digest"]}"',
        f'#define RB3_EXPECTED_CONTENT_SAMPLES {expected["content_samples"]}',
        f'#define RB3_EXPECTED_FRAME_COUNT {expected["frames"]}',
        f'#define RB3_EXPECTED_DRAIN_NON_CONTENT_SAMPLES {expected["drain_non_content_samples"]}',
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
    invalid = report.get("invalid_and_adverse") or report.get("invalid_cases")
    if not isinstance(invalid, dict) or not invalid:
        fail("missing invalid/adverse cases")
    for label, row in invalid.items():
        if row.get("status") != "rejected":
            fail(f"invalid case not rejected: {label}")
        if row.get("candidate_qualified") is not False:
            fail(f"invalid case qualified: {label}")


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
    check_identity_and_replay(report)
    for path in (TASK_DIR / "contract.json", TASK_DIR / "adapter.json", TASK_DIR / "provider.json"):
        load_json(path)
    print(f"verify_ok report_digest={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
