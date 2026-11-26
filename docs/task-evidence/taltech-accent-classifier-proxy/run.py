# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or check the deterministic task-local evidence package."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPORT = "report.json"
SIDECAR = "report.json.sha256"
SOURCES = "SOURCES.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar_bytes(digest: str) -> bytes:
    return f"{digest}  report.json\n".encode("utf-8")


def write_report(out: Path) -> str:
    payload = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(payload)
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT).write_bytes(payload)
    (out / SIDECAR).write_bytes(sidecar_bytes(digest))
    return digest


def check_report(out: Path) -> bool:
    expected = reference.canonical_report_bytes(reference.build_report())
    digest = sha256(expected)
    report = out / REPORT
    sidecar = out / SIDECAR
    return (
        report.is_file()
        and report.read_bytes() == expected
        and sidecar.is_file()
        and sidecar.read_bytes() == sidecar_bytes(digest)
    )


def write_sources() -> str:
    payload = reference.sources_bytes()
    (HERE / SOURCES).write_bytes(payload)
    return sha256(payload)


def check_sources() -> bool:
    payload = reference.sources_bytes()
    target = HERE / SOURCES
    return target.is_file() and target.read_bytes() == payload


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=REPORT,
                        choices=[REPORT, "sources", "all"],
                        help="artifact to generate or check")
    parser.add_argument("--out", type=Path, default=HERE,
                        help="output directory for report.json")
    parser.add_argument("--check", action="store_true",
                        help="verify without writing")
    args = parser.parse_args(argv)

    out = args.out.resolve()
    if out != HERE and args.target in ("sources", "all"):
        parser.error("sources and all may only target this package directory")

    if args.target in (REPORT, "all"):
        if args.check:
            ok = check_report(out)
            digest = sha256(reference.canonical_report_bytes(reference.build_report()))
            print(f"check={'ok' if ok else 'failed'} report_sha256={digest}")
            if not ok:
                return 1
        else:
            digest = write_report(out)
            print(f"wrote={out / REPORT} report_sha256={digest}")

    if args.target in ("sources", "all"):
        if args.check:
            ok = check_sources()
            print(f"check={'ok' if ok else 'failed'} sources={HERE / SOURCES}")
            if not ok:
                return 1
        else:
            digest = write_sources()
            print(f"wrote={HERE / SOURCES} sources_sha256={digest}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
