# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Fail-closed licensing/provenance check for the task-local rate evidence.

This check must never download, install, or invoke FFmpeg.  It verifies that the
package records FFmpeg as absent/unavailable context and that no binary/source
artifact is present under the task-local directory.
"""

from __future__ import annotations

from pathlib import Path
import re
import sys

import reference

TASK = Path(__file__).resolve().parent
FORBIDDEN_PATTERNS = (
    re.compile(r"(^|/)(ffmpeg|ffprobe)(\.exe)?$", re.IGNORECASE),
    re.compile(r"\.(so|dylib|dll|a|lib)$", re.IGNORECASE),
    re.compile(r"(^|/)(COPYING|LICENSE\.GPL|LICENSE\.LGPL)", re.IGNORECASE),
)
TEXT_EXT = {".py", ".json", ".md", ".sha256", ".txt"}
# Assembled from fragments so the checker itself never contains the forbidden
# literal instruction strings it rejects in evidence files.
FORBIDDEN_TEXT = tuple(" ".join(parts) for parts in (
    ("download", "ffmpeg"),
    ("apt", "install", "ffmpeg"),
    ("brew", "install", "ffmpeg"),
    ("pip", "install", "ffmpeg"),
))


def fail(message: str) -> None:
    print("check_licensing: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def main() -> int:
    report = reference.build_report()
    licensing = report["licensing"]
    context = report["ffmpeg_context"]
    if licensing["ffmpeg_binary_or_source"] != "absent":
        fail("ffmpeg binary/source must be absent")
    if licensing["download_or_install"] != "none":
        fail("download/install must be none")
    if context["binary_invoked"] is not False or context["source_vendored"] is not False:
        fail("ffmpeg invocation or vendoring recorded")
    if context["hidden_assumption"] is not False:
        fail("hidden ffmpeg assumption")
    if context["numeric_parity_claimed"] is not False:
        fail("numeric parity with ffmpeg must not be claimed")

    for path in TASK.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(TASK).as_posix()
        for pattern in FORBIDDEN_PATTERNS:
            if pattern.search(relative):
                fail("forbidden artifact name: " + relative)
        if path.suffix.lower() in TEXT_EXT:
            text = path.read_text(encoding="utf-8", errors="ignore").lower()
            for needle in FORBIDDEN_TEXT:
                if needle in text:
                    fail("forbidden install/download text in " + relative)

    print("check_licensing: OK (no ffmpeg binary/source/download, explicit absent context)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
