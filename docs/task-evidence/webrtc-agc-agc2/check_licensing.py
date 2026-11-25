# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for the task-local WebRTC AGC/AGC2 evidence dir."""

from __future__ import annotations

from pathlib import Path
import sys
from typing import Dict, List

ROOT = Path(__file__).resolve().parent
SDK_ROOT = ROOT.parents[2]
COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
REUSE_FILE = SDK_ROOT / "REUSE.toml"
REQUIRED = (
    "README.md", "LICENSE", "LICENSES.md", "THIRD_PARTY_NOTICES.md",
    "contract.json", "contract.json.license", "reference.py", "report.json",
    "report.json.license", "report.json.sha256",
    "report.json.sha256.license", "run.py", "SOURCES.sha256",
    "SOURCES.sha256.license", "test_reference.py", "verify.py",
    "check_licensing.py",
)
FORBIDDEN_NAMES = (
    "audio_processing.h", "gain_control.h", "gain_control.c",
    "adaptive_digital_gain_controller.cc", "adaptive_agc.cc",
    "agc_manager_direct.cc", "input_volume_controller.cc", "NOTICE",
    "COPYING", "LICENSE.WebRTC",
)


def check() -> Dict[str, object]:
    problems: List[str] = []
    explicit = 0
    for name in REQUIRED:
        if not (ROOT / name).is_file():
            problems.append("missing artifact: " + name)
    for path in sorted(ROOT.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if COPYRIGHT_LINE not in head:
            problems.append("missing copyright SPDX: " + path.name)
        if LICENSE_LINE not in head:
            problems.append("missing licence SPDX: " + path.name)
        explicit += 1
    for name in ("README.md", "LICENSE", "LICENSES.md",
                 "THIRD_PARTY_NOTICES.md"):
        head = "\n".join((ROOT / name).read_text(encoding="utf-8")
                         .splitlines()[:6])
        if "SPDX" not in head:
            problems.append("missing SPDX note: " + name)
    notices = (ROOT / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    for token in ("WebRTC", "Apache-2.0", "AGC2", "absent"):
        if token not in notices:
            problems.append("third-party notice is missing: " + token)
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml has no docs/** aggregate annotation")
    if "SPDX" '-License-Identifier = "Apache-2.0"' not in reuse:
        problems.append("REUSE.toml docs annotation is not Apache-2.0")
    if not (SDK_ROOT / "LICENSES/Apache-2.0.txt").is_file():
        problems.append("missing LICENSES/Apache-2.0.txt")
    for name in FORBIDDEN_NAMES:
        if (ROOT / name).exists():
            problems.append("fabricated upstream artifact: " + name)
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in {
                ".whl", ".onnx", ".pt", ".bin", ".so", ".dylib", ".a",
                ".zip", ".tar", ".gz", ".wav", ".flac", ".mp3", ".opus"}:
            problems.append("binary/model/audio artifact: " + str(path))
    return {
        "status": "ok" if not problems else "failed",
        "explicit_spdx_files": explicit,
        "problems": problems,
        "upstream_license_present": False,
    }


def main() -> int:
    result = check()
    print("%s: %d explicit SPDX files, %d problem(s)"
          % (result["status"], result["explicit_spdx_files"],
             len(result["problems"])))
    for problem in result["problems"]:
        print("  " + problem)
    return 0 if result["status"] == "ok" else 1


if __name__ == "__main__":
    sys.exit(main())
