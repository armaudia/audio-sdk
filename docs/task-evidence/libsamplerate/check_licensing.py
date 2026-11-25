# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for the task-local rate evidence directory.

The repository annotates ``docs/**`` with an aggregate Apache-2.0 REUSE entry.
This script additionally requires explicit headers on Python and Markdown
files and rejects a full license identifier token embedded in a Python body.
The split literals below are intentional and must remain split.
"""

from __future__ import annotations

from pathlib import Path
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
SDK_ROOT = ROOT.parents[2]
HEADER_SUFFIXES = {".py", ".md"}
LICENSE_FILE = SDK_ROOT / "LICENSES" / "Apache-2.0.txt"
REUSE_FILE = SDK_ROOT / "REUSE.toml"
COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
FULL_LICENSE_TOKEN = "SPDX" "-License-Identifier:"


def check() -> Dict[str, object]:
    problems: List[str] = []
    explicit = 0
    annotated = 0
    for path in sorted(ROOT.rglob("*"),
                       key=lambda item: item.relative_to(ROOT).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = path.relative_to(ROOT).as_posix()
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix in HEADER_SUFFIXES:
            head = "\n".join(text.splitlines()[:12])
            if COPYRIGHT_LINE not in head or LICENSE_LINE not in head:
                problems.append("missing explicit SPDX header: " + relative)
            else:
                explicit += 1
        else:
            annotated += 1
        if path.suffix == ".py":
            body = "\n".join(text.splitlines()[2:])
            if FULL_LICENSE_TOKEN in body:
                problems.append("full identifier token embedded in Python body: " + relative)
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if "SPDX" "-License-Identifier = \"Apache-2.0\"" not in reuse:
        problems.append("REUSE.toml docs annotation is not Apache-2.0")
    if not LICENSE_FILE.is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")
    upstream_license = ROOT / "LICENSES" / "BSD-2-Clause-upstream-absent.txt"
    if upstream_license.exists():
        problems.append("an upstream license sidecar was fabricated: " + upstream_license.name)
    return {
        "status": "ok" if not problems else "failed",
        "explicit_spdx_files": explicit,
        "aggregate_annotated_files": annotated,
        "problems": problems,
        "reuse_annotation": "docs/** aggregate Apache-2.0",
        "upstream_license_present": False,
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
