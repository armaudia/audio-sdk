# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local SDK-NEURAL-KALMAN-FILTERING-NKF evidence bundle.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check

The report is built three times and every payload must be byte-identical before
anything is written. Only this task-local directory is written. Pinned source
and boundary files are read-only inputs. No NKF source or checkpoint is
imported, no audio is opened, and no network or model output is produced.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPEAT_COUNT = 3
LOCAL_PIN_FILES = reference.LOCAL_PIN_FILES


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def canonical_report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("utf-8"), digest


def sources_bytes() -> bytes:
    return reference.sources_bytes()


def build_once() -> dict[str, bytes]:
    contract = contract_bytes()
    payload, digest = canonical_report_bytes()
    return {
        "contract.json": contract,
        "report.json": payload,
        "report.json.sha256": f"{digest}  report.json\n".encode("ascii"),
    }


def check_committed(built: dict[str, bytes]) -> list[str]:
    problems: list[str] = []
    for name, data in built.items():
        path = HERE / name
        if not path.is_file():
            problems.append("missing_artifact:" + name)
        elif path.read_bytes() != data:
            problems.append("artifact_not_regenerated:" + name)
    readme = HERE / "README.md"
    if not readme.is_file():
        problems.append("missing_artifact:README.md")
    else:
        expected = reference.update_readme_artifact_table(
            readme.read_text(encoding="utf-8"))
        if readme.read_text(encoding="utf-8") != expected:
            problems.append("artifact_not_regenerated:README.md")
    pins = HERE / "SOURCES.sha256"
    if not pins.is_file():
        problems.append("missing_artifact:SOURCES.sha256")
    else:
        try:
            expected_pins = sources_bytes()
        except ValueError as error:
            problems.append("pin_generation_failed:" + str(error))
        else:
            if pins.read_bytes() != expected_pins:
                problems.append("artifact_not_regenerated:SOURCES.sha256")
    return problems


def main(argv: list[str]) -> int:
    if argv[1:] == ["--check"]:
        try:
            built = build_once()
        except (OSError, ValueError) as error:
            print("FAIL: build_failed:" + str(error), file=sys.stderr)
            return 1
        problems = check_committed(built)
        if problems:
            for problem in problems:
                print("FAIL: " + problem, file=sys.stderr)
            return 1
        digest = hashlib.sha256(built["report.json"]).hexdigest()
        print(f"check=ok repeats={REPEAT_COUNT} byte_identical=true "
              f"report_sha256={digest}")
        return 0
    if argv[1:]:
        print("usage: run.py [--check]", file=sys.stderr)
        return 2
    observed: list[tuple[str, str, str]] = []
    built: dict[str, bytes] = {}
    for _ in range(REPEAT_COUNT):
        built = build_once()
        observed.append((
            hashlib.sha256(built["contract.json"]).hexdigest(),
            hashlib.sha256(built["report.json"]).hexdigest(),
            hashlib.sha256(built["report.json.sha256"]).hexdigest(),
        ))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    for name, data in built.items():
        (HERE / name).write_bytes(data)
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    (HERE / "README.md").write_text(
        reference.update_readme_artifact_table(readme), encoding="utf-8")
    (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    report_digest = hashlib.sha256(built["report.json"]).hexdigest()
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"report_sha256={report_digest} "
          f"contract_sha256={hashlib.sha256(built['contract.json']).hexdigest()} "
          f"decision={reference.DECISION} status={reference.STATUS} "
          f"qualification={reference.QUALIFICATION_STATUS}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
