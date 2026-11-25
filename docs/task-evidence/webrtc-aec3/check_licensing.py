# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for this task-local evidence directory.

The repository's REUSE.toml already covers docs/** with an aggregate
Apache-2.0 annotation.  This check additionally requires explicit SPDX headers
on human-readable source files, checks that generated-header scripts split the
SPDX identifier token instead of embedding it in one Python string, and ensures
no file in this package contains a literal full SPDX-License-Identifier token
outside an allowed header/comment position.
"""

from __future__ import annotations

import pathlib
from typing import Dict, List

ROOT = pathlib.Path(__file__).resolve().parent
HEADER_SUFFIXES = {".py", ".c", ".h", ".in", ".md", ".txt"}
HEADER_NAME = {"CMakeLists.txt"}
LICENSE_FILE = ROOT.parents[2] / "LICENSES" / "Apache-2.0.txt"
REUSE_FILE = ROOT.parents[2] / "REUSE.toml"
SPDX_ID = "SPDX" "-License-Identifier:"
FULL_ID = "SPDX" + "-License-Identifier:"


def check() -> Dict[str, object]:
    problems: List[str] = []
    headers = 0
    annotated = 0
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        explicit = path.suffix in HEADER_SUFFIXES or path.name in HEADER_NAME
        text = path.read_text(encoding="utf-8", errors="replace")
        if explicit:
            head = "\n".join(text.splitlines()[:12])
            if ("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes" not in head
                    or SPDX_ID not in head):
                problems.append("missing SPDX header: " + relative)
            else:
                headers += 1
        else:
            annotated += 1
        if path.suffix in {".py", ".json"}:
            body = "\n".join(text.splitlines()[2:])
            if FULL_ID in body:
                problems.append("literal full SPDX identifier token in body: " + relative)
        if path.suffix == ".md" and FULL_ID in text:
            problems.append("literal full SPDX identifier token in markdown: " + relative)
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if not LICENSE_FILE.is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")
    for generator_name in ("crosscheck.py", "check_licensing.py"):
        generator = (ROOT / generator_name).read_text(encoding="utf-8")
        body = "\n".join(generator.splitlines()[2:])
        if FULL_ID in body:
            problems.append(generator_name + " embeds a full SPDX identifier token")
        if 'SPDX" "-License-Identifier:' not in generator:
            problems.append(generator_name + " is not split as required")
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
