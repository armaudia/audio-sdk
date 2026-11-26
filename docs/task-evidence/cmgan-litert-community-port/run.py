# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the byte-identical report, contract and source manifest.

Every payload is built three times before anything is written; a mismatch is a
hard failure. ``--check`` performs the same work without writing.
"""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path
from typing import Dict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def _sha(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def _read(name: str) -> bytes:
    path = HERE / name
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("missing or non-regular local artifact: " + name)
    return path.read_bytes()


def _repeat(payloads: list[bytes], label: str) -> bytes:
    first = payloads[0]
    if len(payloads) != 3 or any(item != first for item in payloads[1:]):
        raise RuntimeError("non-deterministic payload: " + label)
    return first


def build_payloads() -> Dict[str, bytes]:
    reports = [reference.canonical_report(reference.build_report())[0]
               .encode("utf-8") for _ in range(3)]
    report_bytes = _repeat(reports, "report.json")
    report_digest = _sha(report_bytes)
    sidecar_bytes = f"{report_digest}  report.json\n".encode("utf-8")
    report = reference.build_report()

    artifacts: Dict[str, bytes] = {}
    for name in reference.LOCAL_PIN_FILES:
        if name == "report.json":
            artifacts[name] = report_bytes
        elif name == "report.json.sha256":
            artifacts[name] = sidecar_bytes
        elif name == "contract.json":
            continue
        else:
            artifacts[name] = _read(name)

    contracts = [
        (reference.canonical_text(reference.build_contract(
            report, report_digest, artifacts)) + "\n").encode("utf-8")
        for _ in range(3)
    ]
    contract_bytes = _repeat(contracts, "contract.json")
    artifacts["contract.json"] = contract_bytes

    sources = [reference.sources_bytes(overrides=artifacts) for _ in range(3)]
    sources_bytes = _repeat(sources, "SOURCES.sha256")
    return {
        "report.json": report_bytes,
        "report.json.sha256": sidecar_bytes,
        "contract.json": contract_bytes,
        "SOURCES.sha256": sources_bytes,
    }


def main(argv: list[str]) -> int:
    modes = {"--all", "--check", "--digest"}
    if len(argv) != 2 or argv[1] not in modes:
        print("usage: run.py --all | --check | --digest", file=sys.stderr)
        return 2
    mode = argv[1]
    payloads = build_payloads()
    digests = {name: _sha(payload)
               for name, payload in sorted(payloads.items())}
    if mode in ("--all", "--digest"):
        for name, payload in sorted(payloads.items()):
            if mode == "--all":
                (HERE / name).write_bytes(payload)
    print(f"report_sha256={digests['report.json']} "
          f"report_bytes={len(payloads['report.json'])} "
          f"contract_sha256={digests['contract.json']} "
          f"sources_sha256={digests['SOURCES.sha256']}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
