# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Generate deterministic SDK-SOX-TEMPO evidence artifacts."""

from __future__ import annotations

import argparse
from pathlib import Path
import sys

import reference

HERE = Path(__file__).resolve().parent
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"


def sha256_file(path: Path) -> str:
    return reference.sha256_file(path)


def report_bytes() -> bytes:
    report = reference.build_report()
    return reference.canonical_text(report).encode("utf-8")


def contract_bytes() -> bytes:
    report = reference.build_report()
    contract = reference.build_contract(report)
    return reference.canonical_text(contract).encode("utf-8")


def write_atomic(path: Path, payload: bytes) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)


def artifact_names() -> list[str]:
    names = []
    for path in sorted(HERE.iterdir()):
        if not path.is_file():
            continue
        if path.name == "SOURCES.sha256":
            continue
        if path.suffix == ".license":
            continue
        names.append(path.name)
    return names


def build_sources_text() -> str:
    lines = []
    for name in artifact_names():
        digest = sha256_file(HERE / name)
        lines.append(f"{digest}  {reference.TASK_PREFIX}{name}")
    for item in reference.source_pins():
        lines.append(f"{item['sha256']}  {item['path']}")
    for item in reference.boundary_pins():
        lines.append(f"{item['sha256']}  {item['path']}")
    return "\n".join(lines) + "\n"


def write_sources() -> bytes:
    payload = build_sources_text().encode("utf-8")
    write_atomic(SOURCES_PATH, payload)
    return payload


def write_report() -> bytes:
    payload = report_bytes()
    write_atomic(REPORT_PATH, payload)
    write_atomic(SIDECAR_PATH, (reference.sha256_bytes(payload) + "  report.json\n").encode("utf-8"))
    return payload


def write_contract() -> bytes:
    payload = contract_bytes()
    write_atomic(CONTRACT_PATH, payload)
    return payload


def write_all() -> None:
    write_report()
    write_contract()
    # sidecars/licenses are static; sources last because it hashes artifacts.
    write_sources()
    # sources changed, but it is excluded from its own entries by design.


def cmd_report() -> int:
    payload = write_report()
    sys.stdout.write(payload.decode("utf-8"))
    return 0


def cmd_contract() -> int:
    payload = write_contract()
    sys.stdout.write(payload.decode("utf-8"))
    return 0


def cmd_sources() -> int:
    payload = write_sources()
    sys.stdout.write(payload.decode("utf-8"))
    return 0


def cmd_all() -> int:
    write_all()
    print(f"wrote {REPORT_PATH}")
    print(f"wrote {SIDECAR_PATH}")
    print(f"wrote {CONTRACT_PATH}")
    print(f"wrote {SOURCES_PATH}")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    g = parser.add_mutually_exclusive_group(required=True)
    g.add_argument("--report", action="store_true")
    g.add_argument("--contract", action="store_true")
    g.add_argument("--sources", action="store_true")
    g.add_argument("--all", action="store_true")
    args = parser.parse_args()
    if args.report:
        return cmd_report()
    if args.contract:
        return cmd_contract()
    if args.sources:
        return cmd_sources()
    return cmd_all()


if __name__ == "__main__":
    raise SystemExit(main())
