# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen synthetic fixtures, pinned digests and source verification."""

from __future__ import annotations

import json
from pathlib import Path

import reference

TASK_DIR = Path(__file__).resolve().parent

# Frozen stimulus digests. A mismatch means the analytic recipe changed and
# the evidence must be regenerated and reviewed, not silently accepted.
STIMULUS_DIGESTS = {
    "silence": "628df5417a5bdafcb0bec3ff499c6438c8bca8bf30a6aac9ee99f6403bde2fc7",
    "tonal": "6ea7d420be5b0c5cf74f597b071644a7bfd3d0638b8f01476e1ccd5ff806790b",
    "speech_like": "79afdb8226b7182fc05a26d576ca2d03e04ef648fbd0bbaad054afdb91b8ff41",
    "music_like": "1cbe298e4adbe01215c3562b531e9f0f5abd5d5efecf69c0d79a3b8d162fa7e2",
    "c_vector": "5512b12ea086f0717587100240ccb6445ac5e58d8a9b3004a83d887174d9fd18",
}

SCHEDULE_DIGESTS = {
    "identity": "2feafd661d5adb384215d1dbb770a874c153608e7f96829dbb691a04dc385e68",
    "dynamic": "b645623932a306e4d2cf7e1b653113bf0732246859ce9769eb7b7e322896e9a5",
    "fixed": "a28ccfca7a68e1eb71cc68142c701e5b2d7c92365a93f2d3e427f4ca95307715",
    "policy": "ee700cdc03ee2f9924d7e39ad67158579d9bb0db5a7c8768ebb080451e400db6",
    "drift": "6316eda4e3fbe759f0539682ef84a5bf3c8bcf9ca67c4fbd5d24d0dd8c8bde06",
    "rebuffer": "7a237d269ebf164d2cee71870ab87c18fe546ab0ef834674bffa1675f674a0ca",
}

SCHEDULES = {
    "identity": reference.IDENTITY_SCHEDULE,
    "dynamic": reference.DYNAMIC_SCHEDULE,
    "fixed": reference.FIXED_SCHEDULE,
    "policy": reference.POLICY_SCHEDULE,
    "drift": reference.DRIFT_SCHEDULE,
    "rebuffer": reference.REBUFFER_SCHEDULE,
}

SCORED_STIMULI = ("silence", "tonal", "speech_like", "music_like")
ALL_STIMULI = tuple(STIMULUS_DIGESTS)

FIXTURE_CASE_IDS = (
    "identity_1x_control",
    "fixed_rate_ola_baseline",
    "candidate_dynamic_wsola_ola",
    "alignment_disabled_control",
    "unsmoothed_step_adverse",
    "varispeed_adverse",
    "source_timestamp_policy",
    "drift_control",
    "rebuffer_control",
)


def pin_rows(pins: dict[str, str], root: Path) -> dict:
    rows = {}
    for relative, expected in pins.items():
        path = root / relative
        actual = reference.sha256_file(path) if path.is_file() else None
        rows[relative] = {
            "sha256": expected,
            "actual": actual,
            "verified": actual == expected,
        }
    return rows


def verify_source_pins() -> dict:
    return pin_rows(reference.SOURCE_PINS, TASK_DIR)


def verify_boundary_pins() -> dict:
    return pin_rows(reference.BOUNDARY_PINS, TASK_DIR)


def verify_board_snapshot() -> dict:
    return {
        "path": reference.BOARD_SNAPSHOT,
        "sha256_at_read": reference.BOARD_SHA256_AT_READ,
        "mutable": True,
        "note": "Read-time provenance only; validate the live board with swarm check.py.",
    }


def verify_frozen_fixtures() -> dict:
    rows = {}
    for name, expected in STIMULUS_DIGESTS.items():
        actual = reference.tensor_digest(reference.analytic_stimulus(name))
        rows[name] = {"sha256": expected, "actual": actual,
                      "verified": actual == expected,
                      "samples": len(reference.analytic_stimulus(name))}
    for name, expected in SCHEDULE_DIGESTS.items():
        schedule = SCHEDULES[name]
        actual = reference.object_digest(
            [[start, float(rate)] for start, rate in schedule])
        rows["schedule_" + name] = {
            "sha256": expected, "actual": actual, "verified": actual == expected,
            "points": [[start, rate] for start, rate in schedule],
        }
    return rows


def sources_document(report_sha256: str | None = None) -> dict:
    manifest = {}
    for path in sorted(TASK_DIR.rglob("*")):
        relative = path.relative_to(TASK_DIR).as_posix()
        if relative == "SOURCES.sha256" or "__pycache__" in path.parts:
            continue
        if path.is_file() and not path.name.endswith(".pyc"):
            manifest[relative] = reference.sha256_file(path)
    sidecar = TASK_DIR / "report.json.sha256"
    recorded = (sidecar.read_text(encoding="ascii").strip()
                if sidecar.is_file() else None)
    return {
        "schema": "audio-sdk/rubber-band-r3-streaming-sources/0.1",
        "task": "SDK-RUBBER-BAND-R3-STREAMING",
        "status": "proposal_only_not_qualified",
        "base_commit": reference.BASE_COMMIT,
        "base_commit_at_claim": reference.BASE_COMMIT_AT_CLAIM,
        "branch": reference.BRANCH,
        "report_sha256": report_sha256 or recorded,
        "source_pins": verify_source_pins(),
        "boundary_pins": verify_boundary_pins(),
        "board_snapshot": verify_board_snapshot(),
        "frozen_fixtures": verify_frozen_fixtures(),
        "task_local_files": manifest,
        "licensing": {
            "spdx_aggregate": "Apache-2.0",
            "external_source": False,
            "model_weights": False,
            "licensed_runtime": False,
            "real_corpus": False,
        },
    }


def sources_manifest_text() -> str:
    document = sources_document()
    lines = [f"{digest}  {relative}"
             for relative, digest in sorted(document["task_local_files"].items())]
    return "\n".join(lines) + "\n"


def read_sources_manifest() -> dict[str, str]:
    path = TASK_DIR / "SOURCES.sha256"
    result = {}
    for line in path.read_text(encoding="ascii").splitlines():
        digest, relative = line.split("  ", 1)
        result[relative] = digest
    return result


def strict_load(path: Path) -> dict:
    text = path.read_text(encoding="utf-8")
    value = json.loads(text, parse_constant=lambda token: (_ for _ in ()).throw(
        ValueError("nonfinite JSON constant: " + token)))
    if not isinstance(value, dict):
        raise ValueError("strict JSON object required: " + str(path))
    if reference.canonical_json(value) + "\n" != text:
        raise ValueError("JSON is not strict canonical form: " + str(path))
    return value
