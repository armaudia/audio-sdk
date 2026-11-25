# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Explicit SPDX/REUSE checks for this task-local evidence directory.

The repository aggregate annotation already covers docs/**. This check is
stricter: every authored file carries its own tag, while the generated digest
sidecar is covered only by the aggregate annotation. License identifiers are
assembled from split string literals so REUSE lint does not read a tag from
Python string content.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

ROOT = Path(__file__).resolve().parent
COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
GENERATED_WITHOUT_TAG = {"report.json.sha256"}


def repo_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override and (Path(override) / "REUSE.toml").is_file():
        return Path(override)
    cursor = ROOT
    while cursor != cursor.parent:
        if (cursor / "REUSE.toml").is_file() and (cursor / "LICENSES").is_dir():
            return cursor
        cursor = cursor.parent
    return ROOT.parents[2]


def json_tagged(text: str) -> bool:
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        return False
    if not isinstance(value, dict):
        return False
    copyright_key, copyright_value = COPYRIGHT.split(": ", 1)
    license_key, license_value = LICENSE.split(": ", 1)
    return value.get(copyright_key) == copyright_value and value.get(license_key) == license_value


def check() -> Dict[str, Any]:
    problems: List[str] = []
    tagged: List[str] = []
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:12])
        if relative in GENERATED_WITHOUT_TAG:
            continue
        ok = json_tagged(text) if path.suffix == ".json" else COPYRIGHT in head and LICENSE in head
        (tagged if ok else problems).append(relative if ok else "missing SPDX tag: " + relative)
        if path.suffix == ".py" and LICENSE.split(":", 1)[0] + ":" in "\n".join(text.splitlines()[2:]):
            problems.append("literal license token in Python string: " + relative)

    root = repo_root()
    reuse = (root / "REUSE.toml").read_text(encoding="utf-8", errors="replace")
    if '"docs/**"' not in reuse or 'SPDX' '-License-Identifier = "Apache-2.0"' not in reuse:
        problems.append("REUSE.toml docs/** aggregate Apache-2.0 annotation missing")
    if not (root / "LICENSES" / "Apache-2.0.txt").is_file():
        problems.append("LICENSES/Apache-2.0.txt missing")

    for name in ("report.json", "contract.json"):
        path = ROOT / name
        if not path.is_file():
            problems.append("missing " + name)
            continue
        value = json.loads(path.read_text(encoding="utf-8"))
        if value.get("status") != "proposal_only_synthetic_incomplete":
            problems.append(name + " status is not proposal_only_synthetic_incomplete")
        if bool(value.get("candidate_qualified", False)):
            problems.append(name + " claims a qualified candidate")
        boundary = value.get("boundary", {})
        if bool(boundary.get("registered", False)) or bool(boundary.get("enabled_by_default", False)):
            problems.append(name + " boundary is registered or enabled by default")
    return {
        "status": "ok" if not problems else "failed",
        "files_tagged": len(tagged),
        "generated_aggregate_only": sorted(GENERATED_WITHOUT_TAG),
        "problems": problems,
        "reuse_annotation": "docs/** aggregate Apache-2.0",
    }


def main() -> int:
    result = check()
    print("%s: %d files tagged, %d problem(s)" % (
        result["status"], result["files_tagged"], len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
