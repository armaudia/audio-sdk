# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for this task-local evidence directory.

The repository's REUSE.toml covers ``docs/**`` with an aggregate Apache-2.0
annotation. This check additionally requires explicit SPDX headers on all
human-readable source files and verifies that no Python string embeds a
literal, unsplit SPDX identifier token (the REUSE 6.3.0 defect pattern).
"""

from __future__ import annotations

import pathlib
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parent
HEADER_SUFFIXES = {".py", ".c", ".h", ".in", ".md", ".txt"}
HEADER_NAME = {"CMakeLists.txt"}
LICENSE_FILE = ROOT.parents[2] / "LICENSES" / "Apache-2.0.txt"
REUSE_FILE = ROOT.parents[2] / "REUSE.toml"
COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
LICENSE_PREFIX = "SPDX" "-License-Identifier:"


def check() -> Dict[str, object]:
    problems: List[str] = []
    headers = 0
    annotated = 0
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        explicit = path.suffix in HEADER_SUFFIXES or path.name in HEADER_NAME
        if explicit:
            text = path.read_text(encoding="utf-8", errors="replace")
            head = "\n".join(text.splitlines()[:12])
            # REUSE-IgnoreStart: split literals are assertions, not tags.
            if COPYRIGHT not in head or LICENSE not in head:
                # REUSE-IgnoreEnd
                problems.append("missing SPDX header: " + relative)
            else:
                headers += 1
            if path.suffix == ".py":
                body = "\n".join(text.splitlines()[2:])
                # REUSE-IgnoreStart: assertions only, never a literal tag.
                if LICENSE_PREFIX in body:
                    # REUSE-IgnoreEnd
                    problems.append("unsplit SPDX identifier string: " + relative)
        else:
            annotated += 1
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if not LICENSE_FILE.is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")
    return {
        "status": "ok" if not problems else "failed",
        "explicit_spdx_files": headers,
        "aggregate_annotated_files": annotated,
        "problems": problems,
        "reuse_annotation": "docs/** aggregate Apache-2.0",
    }


def main() -> int:
    result = check()
    print("%s: %d explicit SPDX files, %d aggregate REUSE files, %d problem(s)"
          % (result["status"], result["explicit_spdx_files"],
             result["aggregate_annotated_files"], len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
