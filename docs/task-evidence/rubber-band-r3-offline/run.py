# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local report and source-manifest generator for offline TSM evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

import fixture
import reference

TASK_DIR = Path(__file__).resolve().parent
REPORT_FILE = TASK_DIR / "report.json"
SIDECAR_FILE = TASK_DIR / "report.json.sha256"
SOURCES_FILE = TASK_DIR / "SOURCES.sha256"

EXPECTED_LOCAL_FILES = (
    "README.md",
    "SOURCES.sha256",
    "adapter.json",
    "check_licensing.py",
    "contract.json",
    "fixture.py",
    "provider.json",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "scorer.py",
    "test_reference.py",
    "verify.py",
)


def source_manifest_lines() -> list[str]:
    lines = []
    for relative in sorted(EXPECTED_LOCAL_FILES):
        if relative == "SOURCES.sha256":
            continue
        path = TASK_DIR / relative
        if not path.is_file():
            raise FileNotFoundError(f"missing local artifact: {relative}")
        lines.append(f"{fixture.sha256_file(path)}  {relative}")
    return lines


def modes(args: argparse.Namespace) -> int:
    ok = True
    if args.sources:
        pins = fixture.verify_source_pins()
        boundaries = fixture.verify_boundary_pins()
        for path, item in sorted({**pins, **boundaries}.items()):
            status = "verified" if item["verified"] else "MISMATCH"
            print(f"{status:8s} {item['expected']}  {path}")
            ok = ok and item["verified"]
        manifest = SOURCES_FILE.read_text(encoding="utf-8").splitlines()
        expected_manifest = source_manifest_lines()
        manifest_bytes = ("\n".join(manifest) + "\n").encode("utf-8")
        print(f"manifest_lines={len(manifest)}")
        print(f"manifest_digest={fixture.sha256_bytes(manifest_bytes)}")
        ok = ok and manifest == expected_manifest
        print(f"sources_ok={ok}")
        return 0 if ok else 1

    if args.crosscheck:
        report = reference.build_report()
        digests = report["crosscheck"]["cold_start_core_digests"]
        for index, digest in enumerate(digests, 1):
            print(f"cold_start_{index}={digest}")
        print(f"byte_identical={report['crosscheck']['byte_identical']}")
        print(f"recorded_report_digest={json_digest(REPORT_FILE)}")
        print(f"recorded_core_digest={report['crosscheck']['canonical_core_digest']}")
        return 0 if report["crosscheck"]["byte_identical"] else 1

    report = reference.build_report()
    canonical = fixture.canonical_bytes(report)
    text = canonical.decode("utf-8")
    digest = fixture.sha256_bytes(canonical)
    if args.report:
        REPORT_FILE.write_text(text + "\n", encoding="utf-8")
        SIDECAR_FILE.write_text(digest + "\n", encoding="ascii")
    print(f"report_digest={digest}")
    print(f"report_file_digest={fixture.sha256_bytes((text + chr(10)).encode('utf-8'))}")
    print(f"canonical_core_digest={report['crosscheck']['canonical_core_digest']}")
    return 0


def json_digest(path: Path) -> str:
    """Digest of the canonical bytes represented by a checked-in JSON file."""
    import json

    data = json.loads(path.read_text(encoding="utf-8"))
    return fixture.digest_value(data)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group()
    group.add_argument("--report", action="store_true",
                       help="rewrite report.json and its digest sidecar canonically")
    group.add_argument("--sources", action="store_true",
                       help="verify source pins and the local artifact manifest")
    group.add_argument("--crosscheck", action="store_true",
                       help="print three deterministic cold-start core digests")
    return modes(parser.parse_args())


if __name__ == "__main__":
    raise SystemExit(main())
