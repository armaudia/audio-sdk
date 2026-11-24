# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local SPDX/REUSE sanity checks.

The repository's REUSE.toml already annotates docs/** in aggregate.  This check
additionally requires explicit headers on source/markdown files and confirms no
Python string embeds a complete license identifier token.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
HEADER_SUFFIXES = {".py", ".md", ".c", ".h", ".in", ".txt"}
LICENSE_FILE = ROOT.parents[2] / "LICENSES" / "Apache-2.0.txt"
REUSE_FILE = ROOT.parents[2] / "REUSE.toml"
# REUSE-IgnoreStart: split literals below are assertions, not tags.
LICENSE_MARKER = "SPDX" "-License-Identifier: Apache-2.0"
COPYRIGHT_MARKER = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
# REUSE-IgnoreEnd


def check() -> Dict[str, object]:
    problems: List[str] = []
    explicit = 0
    aggregate = 0
    for path in sorted(ROOT.rglob("*"), key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        if path.suffix not in HEADER_SUFFIXES:
            aggregate += 1
            continue
        head = "\n".join(path.read_text(encoding="utf-8", errors="replace").splitlines()[:12])
        if COPYRIGHT_MARKER not in head or LICENSE_MARKER not in head:
            problems.append("missing SPDX header: " + relative)
        else:
            explicit += 1
        if path.suffix == ".py":
            for number, line in enumerate(
                    path.read_text(encoding="utf-8", errors="replace").splitlines()[2:], 3):
                if "SPDX" "-License-Identifier:" in line:
                    problems.append("full license token in Python string: %s:%d"
                                    % (relative, number))
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if not LICENSE_FILE.is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")
    return {
        "status": "ok" if not problems else "failed",
        "explicit_spdx_files": explicit,
        "aggregate_annotated_files": aggregate,
        "problems": problems,
        "reuse_annotation": "docs/** aggregate Apache-2.0",
        "generated_c_headers": 0,
    }


def main() -> int:
    result = check()
    print("%s: %d explicit SPDX files, %d aggregate files, %d problem(s)"
          % (result["status"], result["explicit_spdx_files"],
             result["aggregate_annotated_files"], len(result["problems"])))
    for problem in result["problems"]:  # type: ignore[union-attr]
        print("  " + str(problem))
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
