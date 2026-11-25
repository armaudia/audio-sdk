# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local licensing and dependency-boundary checks.

The tag constants are intentionally split so a literal full tag token never
appears inside a Python string. This check is limited to this evidence
directory; it does not relicense or modify any shared SDK file.
"""

from __future__ import annotations

import ast
import json
import math
from pathlib import Path
import sys
from typing import Any, Dict, List, Set

ROOT = Path(__file__).resolve().parent
SDK_ROOT = ROOT.parents[2]
LICENSE_TAG = "SPDX" "-License-Identifier: Apache-2.0"
COPYRIGHT_TAG = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_KEY = "SPDX-" "License-Identifier"
COPYRIGHT_KEY = "SPDX-" "FileCopyrightText"

# The runtime-free evidence modules must stay standard-library only. verify.py
# is intentionally excluded because it runs cold-start subprocesses.
RUNTIME_FREE_MODULES = ("reference.py", "scorer.py", "run.py", "check_licensing.py")
FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "pystoi", "torch", "tensorflow", "onnxruntime", "ffmpeg",
}
FORBIDDEN_SUFFIXES = {
    ".wav", ".mp3", ".flac", ".ogg", ".bin", ".exe", ".dylib", ".so", ".dll", ".a", ".o", ".whl",
}
FORBIDDEN_NAMES = {"ffmpeg", "ffmpeg.exe", "ffmpeg-macos-aarch64-v7.1", "CMakeLists.txt"}
DOWNLOAD_CALLS = {"urlopen", "urlretrieve", "download", "wget", "requests_get"}


def _python_files() -> List[Path]:
    return sorted(path for path in ROOT.glob("*.py") if path.is_file())


def _strict_json(path: Path) -> Dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError("non-finite JSON " + value)

    def pairs(items: List[tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError(f"duplicate JSON key {key} in {path.name}")
            result[key] = value
        return result

    value = json.loads(path.read_text(encoding="utf-8"),
                       object_pairs_hook=pairs, parse_constant=reject)
    if not isinstance(value, dict):
        raise ValueError("JSON root is not an object: " + path.name)
    return value


def _check_spdx_headers() -> bool:
    for path in _python_files():
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:2])
        if LICENSE_TAG not in head or COPYRIGHT_TAG not in head:
            return False
    for name in ("report.json.license", "report.json.sha256.license", "SOURCES.sha256.license"):
        text = (ROOT / name).read_text(encoding="utf-8")
        if LICENSE_TAG not in text or COPYRIGHT_TAG not in text:
            return False
    readme_head = "\n".join((ROOT / "README.md").read_text(encoding="utf-8").splitlines()[:4])
    return LICENSE_TAG in readme_head and COPYRIGHT_TAG in readme_head


def _check_imports() -> bool:
    for name in RUNTIME_FREE_MODULES:
        tree = ast.parse((ROOT / name).read_text(encoding="utf-8"), filename=name)
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
    for path in ROOT.iterdir():
        if not path.is_file():
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            return False
    return True


def _check_json_licensing() -> bool:
    for name in ("provider.json", "contract.json", "tool-provenance.json"):
        value = _strict_json(ROOT / name)
        if value.get(LICENSE_KEY) != "Apache-2.0":
            return False
        if value.get(COPYRIGHT_KEY) != "2026 Tsakanyan Hovhannes":
            return False
    provider = _strict_json(ROOT / "provider.json")
    contract = _strict_json(ROOT / "contract.json")
    provenance = _strict_json(ROOT / "tool-provenance.json")
    return (provider["decision"] == "DEFER"
            and provider["registered"] is False
            and contract["qualification"]["decision"] == "DEFER"
            and provenance["status"] == "blocked"
            and provenance["numeric_parity_with_ffmpeg"] is False)


def _check_no_download_api() -> bool:
    for path in _python_files():
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            if (isinstance(node, ast.Call) and isinstance(node.func, ast.Name)
                    and node.func.id in DOWNLOAD_CALLS):
                return False
    return True


def _check_reuse_coverage() -> bool:
    text = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    return '"docs/**"' in text and 'SPDX-License-Identifier = "Apache-2.0"' in text


def main() -> int:
    try:
        checks = {
            "spdx_headers": _check_spdx_headers(),
            "dependency_free_imports": _check_imports(),
            "no_native_or_asset_artifacts": _check_no_artifacts(),
            "licensing_json_consistent": _check_json_licensing(),
            "no_download_calls": _check_no_download_api(),
            "reuse_docs_coverage": _check_reuse_coverage(),
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
