# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only pin, JSON, licensing, scope and reproduction verifier."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
PROVENANCE = HERE / "tool-provenance.json"
TASK_PREFIX = "docs/task-evidence/ebu-r128-ffmpeg-loudnorm/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
BASE_COMMIT = "bb8b2849a57c6d1848f14f75d3d54a68fdf16ee0"
FORBIDDEN_SUFFIXES = (".wav", ".mp3", ".flac", ".ogg", ".bin", ".exe",
                      ".dylib", ".so", ".dll", ".a", ".o")
FORBIDDEN_NAMES = ("ffmpeg", "ffmpeg.exe", "ffmpeg-macos-aarch64-v7.1")


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin line: {line!r}")
            continue
        digest, raw_path = parts
        source = raw_path.startswith("source:")
        relative = raw_path.split(":", 1)[1] if source else raw_path
        path = SOURCE_ROOT / relative if source else SDK_ROOT / relative
        if not path.is_file():
            errors.append(f"pinned file missing: {path}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pinned bytes changed: {relative}")
    return len(lines)


def strict_json(path: Path, errors: list[str]) -> dict[str, object] | None:
    def reject(value: str) -> None:
        raise ValueError(f"non-finite JSON constant {value}")

    try:
        payload = json.loads(path.read_text(encoding="utf-8"),
                             parse_constant=reject)
    except (OSError, ValueError) as error:
        errors.append(f"invalid JSON {path.name}: {error}")
        return None
    if not isinstance(payload, dict):
        errors.append(f"{path.name} root is not an object")
        return None
    return payload


def check_json(errors: list[str]) -> int:
    count = 0
    report = strict_json(REPORT, errors)
    if report is not None:
        count += 1
        if report.get("base_commit") != BASE_COMMIT:
            errors.append("report.json base commit is not pinned")
        if report.get("profile") != "DSP":
            errors.append("report.json acceptance profile is not DSP")
        if report.get("candidate_status") != "proposal_only_synthetic_incomplete":
            errors.append("report.json candidate status is not proposal-only")
        if report.get("qualification_status") != "not_qualified":
            errors.append("report.json qualification status is not not_qualified")
        if report.get("no_missing_result_qualifies_candidate") is not True:
            errors.append("missing-result gate disabled")
        boundary = report.get("boundary")
        if not isinstance(boundary, dict) or boundary.get("registered") is not False \
                or boundary.get("enabled_by_default") is not False \
                or boundary.get("descriptor_settings") != {}:
            errors.append("report.json boundary is not optional/unregistered")
    provenance = strict_json(PROVENANCE, errors)
    if provenance is not None:
        count += 1
        if provenance.get("status") != "blocked":
            errors.append("tool provenance is not blocked")
        handling = provenance.get("binary_handling")
        if not isinstance(handling, dict) or not all(
                handling.get(key) is False for key in
                ("vendored", "downloaded", "shipped", "wrapped")):
            errors.append("tool provenance does not exclude binary handling")
    try:
        recorded = REPORT_SHA.read_text(encoding="utf-8").strip()
    except OSError as error:
        errors.append(f"missing report digest: {error}")
        recorded = ""
    if sha256(REPORT.read_bytes()) != recorded:
        errors.append("report.json.sha256 does not match report.json")
    else:
        count += 1
    return count


def check_reproducible(errors: list[str]) -> str:
    import reference  # noqa: PLC0415 - deterministic task-local module

    expected = reference.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    if expected != actual:
        errors.append("report.json is not byte-reproducible")
    return sha256(actual)


def check_licensing(errors: list[str]) -> None:
    import reference  # noqa: PLC0415 - deterministic task-local module

    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append(f"missing SPDX header: {path.name}")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    for path in sorted(HERE.iterdir()):
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append(f"forbidden binary/media file in task dir: {path.name}")
    source = (HERE / "reference.py").read_text(encoding="utf-8")
    if "subprocess" in source or "ffmpeg" in source.lower() and "subprocess" in source:
        errors.append("reference.py appears to invoke an external tool")
    if reference.TOOL_PROVENANCE["synthetic_loudnorm_invocation"]["status"] != "not_run":
        errors.append("synthetic FFmpeg invocation is not recorded as not_run")


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append(f"change outside task scope: {path}")
    return changed


def main() -> int:
    errors: list[str] = []
    pin_count = check_pins(errors)
    json_count = check_json(errors)
    report_digest = check_reproducible(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        return 1
    print(f"pins_ok={pin_count} json_ok={json_count} licensing_ok=1 "
          f"scope_ok=1 reproduction_ok=1 report_sha256={report_digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
