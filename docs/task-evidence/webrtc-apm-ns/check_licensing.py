# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local licensing and dependency-boundary checks.

The tag constants are intentionally split so a literal full tag token never
appears inside a Python string. This check is limited to this evidence
directory; it does not relicense or modify any shared SDK file.
"""

from __future__ import annotations

import ast
from pathlib import Path
import sys
from typing import Dict, List, Set

import reference

ROOT = Path(__file__).resolve().parent
LICENSE_TAG = "SPDX" "-License-Identifier: Apache-2.0"
COPYRIGHT_TAG = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "pystoi", "torch", "tensorflow", "onnxruntime", "webrtc",
}
FORBIDDEN_SUFFIXES = {".so", ".dylib", ".dll", ".a", ".wav", ".onnx", ".tflite", ".bin", ".whl"}
FORBIDDEN_NAMES = {"CMakeLists.txt", "provider.c", "provider.h"}


def _python_files() -> List[Path]:
    return sorted(path for path in ROOT.glob("*.py") if path.is_file())


def _check_spdx_headers() -> bool:
    for path in _python_files():
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:5])
        if LICENSE_TAG not in head or COPYRIGHT_TAG not in head:
            return False
    readme = (ROOT / "README.md").read_text(encoding="utf-8").splitlines()[:10]
    header = "\n".join(readme)
    return LICENSE_TAG in header and COPYRIGHT_TAG in header


def _check_imports() -> bool:
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            roots: Set[str] = set()
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = {node.module.split(".")[0]}
            if roots & FORBIDDEN_IMPORT_ROOTS:
                return False
    return True


def _check_no_artifacts() -> bool:
    for path in ROOT.rglob("*"):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        if path.suffix.lower() in FORBIDDEN_SUFFIXES or path.name in FORBIDDEN_NAMES:
            return False
    return True


def _check_json_licensing() -> bool:
    provider = reference.read_strict_json(ROOT / "provider.json")
    licensing: Dict[str, object] = provider.get("licensing", {})
    if licensing.get("spdx_identifier") != "Apache-2.0":
        return False
    if licensing.get("third_party_artifacts") != []:
        return False
    contract = reference.read_strict_json(ROOT / "contract.json")
    return contract.get("status") == "proposal_only_not_qualified" and not contract.get("public_surface_change", True)


def _check_no_download_api() -> bool:
    forbidden_calls = {"urlopen", "urlretrieve", "requests_get", "download", "wget"}
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) and node.func.id in forbidden_calls:
                return False
    return True


def main() -> int:
    try:
        checks = {
            "spdx_headers": _check_spdx_headers(),
            "dependency_free_imports": _check_imports(),
            "no_native_or_asset_artifacts": _check_no_artifacts(),
            "licensing_json_consistent": _check_json_licensing(),
            "no_download_calls": _check_no_download_api(),
        }
    except (OSError, ValueError, KeyError, TypeError, SyntaxError) as error:
        print("FAIL " + str(error), file=sys.stderr)
        return 1
    if not all(checks.values()):
        print("FAIL " + repr(checks), file=sys.stderr)
        return 1
    print("PASS licensing " + " ".join(sorted(checks)))
    return 0


if __name__ == "__main__":
    sys.exit(main())
