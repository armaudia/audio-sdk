# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Independent SPDX/REUSE check for the task-local evidence package.

The repository annotates ``docs/**`` with an aggregate Apache-2.0 annotation.
This check additionally requires explicit SPDX headers on Python and Markdown
sources, exact sidecars on generated artifacts, a fail-closed local file set and
the shared Apache-2.0 license text.
"""

from __future__ import annotations

import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
FULL_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR = f"{COPYRIGHT}\n{LICENSE}\n"


def check() -> dict[str, object]:
    problems: list[str] = []
    explicit = 0
    annotated = 0
    expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if path.is_dir():
            continue
        relative = path.relative_to(HERE).as_posix()
        if "__pycache__" in path.parts or relative not in expected:
            problems.append("file outside fail-closed local set: " + relative)
            continue
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.suffix == ".py":
            head = text.splitlines()[:2]
            if head != ["# " + COPYRIGHT, "# " + LICENSE]:
                problems.append("missing explicit SPDX header: " + relative)
            elif text.count(FULL_TOKEN) != 1:
                problems.append("full identifier token repeated in Python body: " + relative)
            else:
                explicit += 1
        elif path.suffix == ".md":
            head = text.splitlines()[:2]
            if head != ["<!-- " + COPYRIGHT + " -->", "<!-- " + LICENSE + " -->"]:
                problems.append("missing explicit Markdown SPDX header: " + relative)
            else:
                explicit += 1
        elif relative.endswith(".license"):
            if text != SIDECAR:
                problems.append("invalid license sidecar: " + relative)
            else:
                annotated += 1
        elif relative == "SOURCES.sha256":
            sidecar = HERE / "SOURCES.sha256.license"
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR:
                problems.append("missing or invalid license sidecar: SOURCES.sha256.license")
            else:
                annotated += 1
        else:
            sidecar = HERE / (relative + ".license")
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR:
                problems.append("missing or invalid license sidecar: " + relative + ".license")
            else:
                annotated += 1
    present = {path.relative_to(HERE).as_posix()
               for path in HERE.rglob("*") if path.is_file()}
    for name in sorted(expected - present):
        problems.append("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        problems.append("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        problems.append("LICENSES/Apache-2.0.txt missing")
    return {
        "status": "ok" if not problems else "failed",
        "explicit_spdx_files": explicit,
        "annotated_artifacts": annotated,
        "problems": problems,
    }


def main() -> int:
    result = check()
    print("licensing: %s %d explicit SPDX files, %d annotated artifacts, %d problem(s)"
          % (result["status"], result["explicit_spdx_files"],
             result["annotated_artifacts"], len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    raise SystemExit(main())
