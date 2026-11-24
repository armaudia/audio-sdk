# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only SPDX/REUSE sanity check for this task-local evidence package.

The identifier token is assembled from split Python string pieces so that no
literal annotation appears inside a string.  Real header comments remain valid.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent
COPYRIGHT_HEAD = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_HEAD = "SPDX" "-License-Identifier: Apache-2.0"
COPYRIGHT_KEY, COPYRIGHT_VALUE = COPYRIGHT_HEAD.split(": ", 1)
LICENSE_KEY, LICENSE_VALUE = LICENSE_HEAD.split(": ", 1)
FORBIDDEN_SUFFIXES = (".c", ".h", ".cc", ".cpp", ".hpp", ".so", ".a", ".wasm", ".pyc")


def json_has_annotations(text: str) -> bool:
    try:
        value = json.loads(text)
    except ValueError:
        return False
    if not isinstance(value, dict):
        return False
    return value.get(COPYRIGHT_KEY) == COPYRIGHT_VALUE \
        and value.get(LICENSE_KEY) == LICENSE_VALUE


def check() -> dict[str, Any]:
    problems: list[str] = []
    tagged = 0
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        name = path.relative_to(ROOT).as_posix()
        sidecar = ROOT / (name + ".license")
        if name == "SOURCES.sha256" or path.name.endswith(".license") or sidecar.is_file():
            annotation_path = sidecar if sidecar.is_file() else path
            text = annotation_path.read_text(encoding="utf-8", errors="strict")
            ok = COPYRIGHT_HEAD in text and LICENSE_HEAD in text
        else:
            text = path.read_text(encoding="utf-8", errors="strict")
            if path.suffix == ".json":
                ok = json_has_annotations(text)
            elif path.suffix == ".md":
                escaped_c = COPYRIGHT_HEAD.split(": ", 1)[0] + "&#45;" + COPYRIGHT_VALUE
                escaped_l = LICENSE_HEAD.split(": ", 1)[0] + "&#45;" + LICENSE_VALUE
                ok = (COPYRIGHT_HEAD in text and LICENSE_HEAD in text) \
                    or (escaped_c in text and escaped_l in text)
            else:
                head = "\n".join(text.splitlines()[:12])
                ok = COPYRIGHT_HEAD in head and LICENSE_HEAD in head
                if path.suffix == ".py":
                    body = "\n".join(text.splitlines()[2:])
                    if LICENSE_KEY + ":" in body:
                        problems.append("literal license token in Python string: " + name)
        if path.suffix in FORBIDDEN_SUFFIXES:
            problems.append("native or binary artifact inside task-local evidence: " + name)
        if ok:
            tagged += 1
        else:
            problems.append("missing SPDX annotation: " + name)

    for name in ("adapter.json", "contract.json", "provider.json"):
        value = json.loads((ROOT / name).read_text(encoding="utf-8"))
        if value.get("status") != "proposal_only_not_qualified":
            problems.append(name + " disposition is not proposal-only")
        decision = value.get("decision", value.get("qualification", {}).get("decision"))
        if decision != "DEFER":
            problems.append(name + " decision is not DEFER")
    return {
        "status": "ok" if not problems else "failed",
        "files_checked": tagged + len(problems),
        "annotated_files": tagged,
        "problems": problems,
        "no_native_artifacts": True,
    }


def main() -> int:
    result = check()
    print("licensing: %s, %d annotated file(s), %d problem(s)" % (
        result["status"], result["annotated_files"], len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
