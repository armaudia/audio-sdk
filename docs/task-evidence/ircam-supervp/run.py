# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local SDK-IRCAM-SUPERVP evidence bundle.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --check

The report is built three times and every payload must be byte-identical before
anything is written. Only this task-local directory is written. Pinned source
and boundary files are read-only inputs. No vendor engine is loaded, no vendor
package is imported, and no audio, network or engine output is produced.
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
LOCAL_PIN_FILES = (
    "LICENSES.md",
    "README.md",
    "SOURCES.sha256.license",
    "contract.json",
    "contract.json.license",
    "reference.py",
    "report.json",
    "report.json.license",
    "report.json.sha256",
    "report.json.sha256.license",
    "run.py",
    "test_reference.py",
    "verify.py",
)


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def canonical_report_bytes() -> tuple[bytes, str]:
    text, digest = reference.canonical_report(reference.build_report())
    return text.encode("ascii"), digest


def sources_bytes() -> bytes:
    """Build the deterministic SHA-256 manifest from pinned read-only inputs."""
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        actual = reference.sha256_file(reference.SOURCE_ROOT / relative)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        actual = reference.sha256_file(reference.WORKTREE / relative)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append(("sdk:" + relative, actual))
    for name in reference.local_manifest_paths():
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, reference.sha256_file(path)))
    rows.sort(key=lambda item: item[0])
    lines = [
        "# SHA-256 pins for SDK-IRCAM-SUPERVP task-local evidence.",
        "# source: paths are relative to the pinned research workspace root.",
        "# sdk: paths are relative to this SDK worktree.",
        "# The mutable full plan/swarm/TASKS.json is never hashed; only the "
        "stable row identity gates.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {path}" for path, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


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
        text = readme.read_text(encoding="utf-8")
        if text != reference.update_readme_artifact_table(text):
            problems.append("artifact_not_regenerated:README.md")
    pins = HERE / "SOURCES.sha256"
    if not pins.is_file():
        problems.append("missing_artifact:SOURCES.sha256")
    elif pins.read_bytes() != sources_bytes():
        problems.append("artifact_not_regenerated:SOURCES.sha256")
    return problems


def main(argv: list[str]) -> int:
    if argv[1:] == ["--check"]:
        built = build_once()
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
        contract_digest = hashlib.sha256(built["contract.json"]).hexdigest()
        report_digest = hashlib.sha256(built["report.json"]).hexdigest()
        sidecar_digest = hashlib.sha256(built["report.json.sha256"]).hexdigest()
        observed.append((contract_digest, report_digest, sidecar_digest))
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
