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
CONTRACT = "contract.json"
SOURCES = "SOURCES.sha256"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sidecar_bytes(digest: str) -> bytes:
    return f"{digest}  report.json\n".encode("utf-8")


def build_payloads() -> tuple[bytes, bytes, str]:
    report = reference.build_report()
    report_bytes = reference.canonical_bytes(report)
    contract_bytes = reference.canonical_bytes(reference.build_contract(report))
    return report_bytes, contract_bytes, sha256(report_bytes)


def source_lines() -> list[str]:
    lines = [
        "# SHA-256 pins for SDK-YAMNET-ONNX.",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are relative",
        "# to the SDK checkout; pkg: paths are relative to this task-evidence",
        "# directory. The mutable full plan/swarm/TASKS.json is never hashed; only",
        "# the linked-row stable identity is gated.",
        "",
    ]
    for relative, digest in sorted(reference.SOURCE_PINS.items()):
        path = reference.SOURCE_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"source pin target missing: {relative}")
        if sha256(path.read_bytes()) != digest:
            raise ValueError(f"source pin digest changed: {relative}")
        lines.append(f"{digest}  source:{relative}")
    for relative, digest in sorted(reference.BOUNDARY_PINS.items()):
        path = reference.SDK_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError(f"worktree pin target missing: {relative}")
        if sha256(path.read_bytes()) != digest:
            raise ValueError(f"worktree pin digest changed: {relative}")
        lines.append(f"{digest}  worktree:{relative}")
    for name in reference.LOCAL_PIN_PATHS:
        path = HERE / name
        if not path.is_file():
            raise FileNotFoundError(f"package pin target missing: {name}")
        lines.append(f"{sha256(path.read_bytes())}  pkg:{name}")
    return lines


def write_sources() -> str:
    payload = ("\n".join(source_lines()) + "\n").encode("utf-8")
    (HERE / SOURCES).write_bytes(payload)
    return sha256(payload)


def check_sources() -> bool:
    payload = ("\n".join(source_lines()) + "\n").encode("utf-8")
    target = HERE / SOURCES
    return target.is_file() and target.read_bytes() == payload


def write_artifacts(out: Path) -> str:
    report_bytes, contract_bytes, digest = build_payloads()
    out.mkdir(parents=True, exist_ok=True)
    (out / REPORT).write_bytes(report_bytes)
    (out / SIDECAR).write_bytes(sidecar_bytes(digest))
    (out / CONTRACT).write_bytes(contract_bytes)
    return digest


def check_artifacts(out: Path) -> bool:
    report_bytes, contract_bytes, digest = build_payloads()
    return (
        (out / REPORT).is_file() and (out / REPORT).read_bytes() == report_bytes
        and (out / SIDECAR).is_file() and (out / SIDECAR).read_bytes() == sidecar_bytes(digest)
        and (out / CONTRACT).is_file() and (out / CONTRACT).read_bytes() == contract_bytes
    )


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default=REPORT, choices=[REPORT, "sources", "all"])
    parser.add_argument("--out", type=Path, default=HERE)
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv)
    out = args.out.resolve()
    if out != HERE and args.target in ("sources", "all"):
        parser.error("sources/all may only target this package directory")

    if args.target in (REPORT, "all"):
        report_bytes, _, digest = build_payloads()
        if args.check:
            ok = check_artifacts(out)
            print(f"check={'ok' if ok else 'failed'} report_sha256={digest} bytes={len(report_bytes)}")
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
            sd = write_sources()
            print(f"sources_sha256={sd}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
