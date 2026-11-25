# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical task evidence artifacts for the ONNX Runtime boundary."""

from __future__ import annotations

import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

LICENSE_TEXT = (reference.SPDX_COPYRIGHT_LINE + "\n"
                + reference.SPDX_LICENSE_LINE + "\n")
SIDECARS = (
    "contract.json.license",
    "adapter.json.license",
    "provider.json.license",
    "synthetic_model.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)


def _write(path: Path, payload: bytes) -> None:
    path.write_bytes(payload)


def generate_documents() -> None:
    _write(HERE / "synthetic_model.json", reference.model_bytes())
    _write(HERE / "contract.json", reference.contract_bytes())
    _write(HERE / "adapter.json", reference.adapter_bytes())
    _write(HERE / "provider.json", reference.provider_bytes())
    for name in SIDECARS:
        _write(HERE / name, LICENSE_TEXT.encode("utf-8"))


def generate_report() -> str:
    payloads = [reference.canonical_report_bytes(reference.build_report()) for _ in range(3)]
    if len(set(payloads)) != 1:
        raise SystemExit("refusing to write: three in-process passes differ")
    payload = payloads[0]
    _write(HERE / "report.json", payload)
    digest = hashlib.sha256(payload).hexdigest()
    _write(HERE / "report.json.sha256", f"{digest}  report.json\n".encode("utf-8"))
    return digest


def generate_sources() -> int:
    payloads = [reference.sources_bytes() for _ in range(3)]
    if len(set(payloads)) != 1:
        raise SystemExit("refusing to write: three source-manifest passes differ")
    _write(HERE / "SOURCES.sha256", payloads[0])
    return len(reference.parse_pin_lines(payloads[0].decode("utf-8")))


def main(argv: list[str]) -> int:
    commands = {"report.json", "--report", "--sources", "--all"}
    if len(argv) != 2 or argv[1] not in commands:
        print("usage: run.py {report.json|--report|--sources|--all}", file=sys.stderr)
        return 2
    command = argv[1]
    if command == "--sources":
        print(f"pins={generate_sources()}")
        return 0
    generate_documents()
    digest = generate_report()
    if command in ("report.json", "--report"):
        print(f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size}")
        return 0
    pins = generate_sources()
    print(f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size} pins={pins}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
