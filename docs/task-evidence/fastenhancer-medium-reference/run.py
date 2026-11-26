# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical contract, report, digest sidecar and source manifest."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def _write_three_pass(name: str, factory) -> bytes:
    payloads = [factory() for _ in range(3)]
    if len(set(payloads)) != 1:
        raise SystemExit(f"refusing to write: three passes differ for {name}")
    payload = payloads[0]
    (HERE / name).write_bytes(payload)
    return payload


def generate_contract() -> bytes:
    return _write_three_pass("contract.json", reference.contract_bytes)


def generate_report() -> str:
    payload = _write_three_pass(
        "report.json", lambda: reference.canonical_report_bytes(reference.build_report())
    )
    digest = hashlib.sha256(payload).hexdigest()
    sidecar = f"{digest}  report.json\n".encode("utf-8")
    (HERE / "report.json.sha256").write_bytes(sidecar)
    return digest


def generate_sources() -> int:
    payload = _write_three_pass("SOURCES.sha256", reference.sources_bytes)
    return len(reference.parse_pin_lines(payload.decode("utf-8")))


def main(argv: list[str]) -> int:
    commands = {"--all", "--contract", "--report", "--sources"}
    if len(argv) != 2 or argv[1] not in commands:
        print("usage: run.py {--all|--contract|--report|--sources}", file=sys.stderr)
        return 2
    command = argv[1]
    if command == "--contract":
        payload = generate_contract()
        print(f"contract_sha256={hashlib.sha256(payload).hexdigest()} bytes={len(payload)}")
    elif command == "--report":
        digest = generate_report()
        print(f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size}")
    elif command == "--sources":
        print(f"pins={generate_sources()}")
    else:
        contract = generate_contract()
        digest = generate_report()
        pins = generate_sources()
        print(
            f"contract_sha256={hashlib.sha256(contract).hexdigest()} "
            f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size} "
            f"pins={pins}"
        )
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
