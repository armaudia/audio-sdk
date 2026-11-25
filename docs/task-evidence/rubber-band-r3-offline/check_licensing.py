# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed rights and dependency audit for this task-local directory."""

from __future__ import annotations

import ast
from pathlib import Path
import sys

TASK_DIR = Path(__file__).resolve().parent

# Kept split so this checker never embeds a complete license marker as a Python
# string literal. Generated C headers are not used by this task.
LICENSE_MARKER = "SPDX" "-License-Identifier: Apache-2.0"
COPYRIGHT_MARKER = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
STDLIB_ONLY = {
    "__future__", "argparse", "ast", "hashlib", "json", "math", "os", "pathlib",
    "subprocess", "sys", "tokenize", "io", "typing", "collections", "graphlib",
    "datetime", "unittest",
}
LOCAL_MODULES = {"check_licensing", "fixture", "reference", "run", "scorer", "verify"}
FORBIDDEN_MODULES = {
    "numpy", "scipy", "soundfile", "librosa", "torch", "tensorflow", "pystoi",
    "rubberband", "rubberbandpy", "pyrubberband", "soundtouch", "ctypes",
}
FORBIDDEN_TEXT = (
    "GPL-2.0-or-later", "GPL-3.0", "GPL-2.0+", "commercial SDK binary",
    "vendored rubberband", "downloaded codec binary",
)
BINARY_SUFFIXES = {".so", ".dylib", ".dll", ".a", ".wav", ".mp3", ".flac", ".ogg", ".bin", ".pth", ".onnx"}


def audit() -> list[str]:
    problems: list[str] = []
    files = sorted(path for path in TASK_DIR.rglob("*") if path.is_file())
    for path in files:
        relative = path.relative_to(TASK_DIR).as_posix()
        if path.suffix.lower() in BINARY_SUFFIXES:
            problems.append(f"binary or corpus asset: {relative}")
        if path.suffix == ".py":
            text = path.read_text(encoding="utf-8")
            if LICENSE_MARKER not in text.splitlines()[1] or COPYRIGHT_MARKER not in text.splitlines()[0]:
                problems.append(f"missing SPDX header: {relative}")
            tree = ast.parse(text, filename=relative)
            for node in ast.walk(tree):
                names = []
                if isinstance(node, ast.Import):
                    names = [alias.name.split(".")[0] for alias in node.names]
                elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                    names = [node.module.split(".")[0]]
                for name in names:
                    if name in FORBIDDEN_MODULES:
                        problems.append(f"forbidden dependency {name}: {relative}")
                    elif name not in STDLIB_ONLY and name not in LOCAL_MODULES:
                        problems.append(f"non-stdlib import {name}: {relative}")
    for relative in ("contract.json", "adapter.json", "provider.json", "report.json"):
        path = TASK_DIR / relative
        if not path.is_file():
            problems.append(f"missing descriptor: {relative}")
    text_blob = "\n".join(
        path.read_text(encoding="utf-8", errors="ignore")
        for path in files
        if path.suffix in {".py", ".json", ".md"} and path.name != "check_licensing.py"
    )
    low = text_blob.lower()
    for phrase in FORBIDDEN_TEXT:
        if phrase.lower() in low:
            problems.append(f"forbidden rights phrase in evidence: {phrase}")
    if any(path.name.endswith(".h") or path.name == "CMakeLists.txt" for path in files):
        problems.append("C or CMake boundary files are outside this task-local package")
    return problems


def main() -> int:
    problems = audit()
    if problems:
        print("licensing: FAIL")
        for problem in problems:
            print(f"- {problem}")
        return 1
    print("licensing: ok")
    print("stdlib_only_python=true")
    print("binary_assets=0")
    print("c_or_cmake_boundary=0")
    print("external_runtime=none")
    return 0


if __name__ == "__main__":
    sys.exit(main())
