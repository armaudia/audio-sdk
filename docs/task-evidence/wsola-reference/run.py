# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or check deterministic SDK-WSOLA-REFERENCE evidence artifacts."""

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
CONTRACT = "contract.json"
SOURCES = "SOURCES.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar_bytes(digest: str) -> bytes:
    return f"{digest}  report.json\n".encode("ascii")


def build_payloads() -> tuple[bytes, bytes]:
    report = reference.build_report()
    return reference.canonical_bytes(report), reference.canonical_bytes(reference.build_contract(report))


def write_artifacts(out: Path) -> str:
    report_bytes, contract_bytes = build_payloads()
    digest = sha256(report_bytes)
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT).write_bytes(report_bytes)
    (out / SIDECAR).write_bytes(sidecar_bytes(digest))
    (out / CONTRACT).write_bytes(contract_bytes)
    return digest


def check_artifacts(out: Path) -> bool:
    report_bytes, contract_bytes = build_payloads()
    digest = sha256(report_bytes)
    return (
        (out / REPORT).is_file() and (out / REPORT).read_bytes() == report_bytes and
        (out / SIDECAR).is_file() and (out / SIDECAR).read_bytes() == sidecar_bytes(digest) and
        (out / CONTRACT).is_file() and (out / CONTRACT).read_bytes() == contract_bytes
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
                        choices=[REPORT, "sources", "all"])
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out != HERE and args.target in ("sources", "all"):
        parser.error("sources/all may only target package directory")

    if args.target in (REPORT, "all"):
        report_bytes, _ = build_payloads()
        digest = sha256(report_bytes)
        if args.check:
            ok = check_artifacts(out)
            print(f"check={'ok' if ok else 'failed'} report_sha256={digest}")
            if not ok:
                return 1
        else:
            digest = write_artifacts(out)
            print(f"report_sha256={digest}")
    if args.target in ("sources", "all"):
        if args.check:
            ok = check_sources()
            print(f"sources_check={'ok' if ok else 'failed'}")
            if not ok:
                return 1
        else:
            digest = write_sources()
            print(f"sources_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
