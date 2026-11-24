# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for this task-local evidence directory.

REUSE.toml already covers docs/** with an aggregate Apache-2.0 annotation;
this check additionally requires explicit tags on every new file. The
identifier token is split inside Python strings so REUSE lint never sees a
literal tag in string content.
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from typing import Any, Dict, List

import reference

ROOT = Path(__file__).resolve().parent
COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
FORBIDDEN_DRAFT_KEYS = ("framing", "gates", "qualification_status")


def repo_root() -> Path:
    """Find the SDK repo even when only this package was copied out."""
    workspace = os.environ.get("AUDIOML_WORKSPACE")
    if workspace:
        candidate = (Path(workspace) / "worktrees" / "audio-sdk"
                     / "SDK-BENCH-SUBPROCESS-PROTOCOL-SANDBOX-AND-ASSET-IDS")
        if (candidate / "REUSE.toml").is_file():
            return candidate
    marker = ROOT
    while marker != marker.parent:
        if (marker / "REUSE.toml").is_file() and (marker / "LICENSES").is_dir():
            return marker
        marker = marker.parent
    return ROOT.parents[2]


def _json_has_tags(text: str) -> bool:
    try:
        value = json.loads(text)
    except (ValueError, TypeError):
        return False
    if not isinstance(value, dict):
        return False
    copyright_key, copyright_value = COPYRIGHT.split(": ", 1)
    license_key, license_value = LICENSE.split(": ", 1)
    return (value.get(copyright_key) == copyright_value
            and value.get(license_key) == license_value)


def check() -> Dict[str, Any]:
    problems: List[str] = []
    tagged = 0
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        head = "\n".join(text.splitlines()[:12])
        if path.suffix == ".json":
            ok = _json_has_tags(text)
        else:
            ok = COPYRIGHT in head and LICENSE in head
        if not ok:
            problems.append("missing SPDX tag: " + relative)
        else:
            tagged += 1
        if path.suffix == ".py":
            body = "\n".join(text.splitlines()[2:])
            if LICENSE.split(":", 1)[0] + ":" in body:
                problems.append("literal license token in Python string: " + relative)

    root = repo_root()
    reuse_file = root / "REUSE.toml"
    license_file = root / "LICENSES" / "Apache-2.0.txt"
    reuse = reuse_file.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if not license_file.is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")

    contract = reference.load_package_json(reference.CONTRACT)
    report = reference.load_package_json(reference.REPORT)
    for name, value in (("contract", contract), ("report", report)):
        if value.get("status") != "proposal_only_not_qualified":
            problems.append(name + " is not proposal_only_not_qualified")
        boundary = value.get("boundary", {})
        if boundary.get("status") != "proposal_only_not_qualified":
            problems.append(name + " boundary is not proposal_only_not_qualified")
        if boundary.get("release_gate") != "DEFER":
            problems.append(name + " release gate is not DEFER")
        for key in FORBIDDEN_DRAFT_KEYS:
            if key in value:
                problems.append(name + " contains draft key: " + key)

    return {
        "status": "ok" if not problems else "failed",
        "files_checked": tagged + len(problems),
        "explicitly_tagged_files": tagged,
        "problems": problems,
        "reuse_annotation": "docs/** aggregate Apache-2.0",
    }


def main() -> int:
    result = check()
    print("%s: %d files tagged, %d problem(s)" % (
        result["status"], result["explicitly_tagged_files"], len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
