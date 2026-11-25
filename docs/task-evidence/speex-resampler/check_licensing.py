# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Local SPDX/REUSE checks for the task-local Speex resampler evidence."""

from __future__ import annotations

from pathlib import Path
import sys

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REUSE_FILE = SDK_ROOT / "REUSE.toml"
LICENSES = SDK_ROOT / "LICENSES"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_APACHE = "SPDX" "-License-Identifier: Apache-2.0"
REQUIRED = (
    "README.md", "LICENSE", "THIRD_PARTY_NOTICES.md", "harness.c",
    "reference.py", "run.py", "verify.py", "check_licensing.py",
    "test_reference.py", "contract.json", "report.json",
    "report.json.sha256", "SOURCES.sha256",
)


def main() -> int:
    problems = []
    for name in REQUIRED:
        if not (HERE / name).is_file():
            problems.append("missing " + name)
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_COPYRIGHT not in head:
            problems.append("missing copyright SPDX: " + path.name)
        if SPDX_APACHE not in head:
            problems.append("missing license SPDX: " + path.name)
    harness = "\n".join((HERE / "harness.c").read_text(encoding="utf-8").splitlines()[:3])
    if SPDX_COPYRIGHT not in harness or SPDX_APACHE not in harness:
        problems.append("missing SPDX header: harness.c")
    for name in ("README.md", "LICENSE", "THIRD_PARTY_NOTICES.md"):
        head = "\n".join((HERE / name).read_text(encoding="utf-8").splitlines()[:4])
        if "SPDX" not in head:
            problems.append("missing SPDX note: " + name)
    notices = (HERE / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    if "SpeexDSP" not in notices or "BSD-3-Clause" not in notices:
        problems.append("third-party notice is incomplete")
    reuse = REUSE_FILE.read_text(encoding="utf-8")
    if '"docs/**"' not in reuse:
        problems.append("REUSE.toml does not cover docs/**")
    if "SPDX" '-License-Identifier = "Apache-2.0"' not in reuse:
        problems.append("REUSE.toml docs annotation is not Apache-2.0")
    for name in ("Apache-2.0.txt", "BSD-3-Clause.txt"):
        if not (LICENSES / name).is_file():
            problems.append("LICENSES/" + name + " missing")
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        return 1
    print(f"licensing_ok files={len(REQUIRED)} explicit_spdx={len(list(HERE.glob('*.py')))}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
