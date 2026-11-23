#!/usr/bin/env python3
"""Reproducible CLI entry point for the typed-frame/drift tool fixture.

Writes the frozen contract, machine-readable report and SHA-256 sidecar. The
fixture is stdlib-only and model-free; it never builds or installs an SDK.
"""

from __future__ import annotations

import argparse
import hashlib
from pathlib import Path
import sys

import fixture


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output-dir", default=str(Path(__file__).resolve().parent),
        help="directory for contract.json, report.json and report.json.sha256",
    )
    parser.add_argument(
        "--install-location", default=None,
        help="recorded install location (defaults to the model directory)",
    )
    args = parser.parse_args(argv)

    output = Path(args.output_dir)
    output.mkdir(parents=True, exist_ok=True)
    contract_bytes = fixture.canonical_bytes(fixture.CONTRACT)
    report_bytes = fixture.build_report(install_location=args.install_location)
    (output / "contract.json").write_bytes(contract_bytes)
    (output / "report.json").write_bytes(report_bytes)
    report_digest = hashlib.sha256(report_bytes).hexdigest()
    (output / "report.json.sha256").write_text(report_digest + "\n", encoding="ascii")
    print(
        f"contract_sha256={hashlib.sha256(contract_bytes).hexdigest()} "
        f"report_sha256={report_digest} output={output}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
