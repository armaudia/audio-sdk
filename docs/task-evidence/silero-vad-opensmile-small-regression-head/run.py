# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or verify the byte-identical canonical evidence report."""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402


def sidecar_bytes(digest: str) -> bytes:
    return f"{digest}  report.json\n".encode("utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("filename", nargs="?", default="report.json",
                        choices=["report.json"], help="canonical output name")
    parser.add_argument("--out", type=Path, default=HERE, help="output directory")
    parser.add_argument("--check", action="store_true", help="verify without writing")
    args = parser.parse_args(argv)

    payload = reference.canonical_report_bytes(reference.build_report())
    digest = hashlib.sha256(payload).hexdigest()
    output = args.out / args.filename
    sidecar = args.out / (args.filename + ".sha256")
    if args.check:
        ok = output.is_file() and output.read_bytes() == payload
        ok = ok and sidecar.is_file() and sidecar.read_bytes() == sidecar_bytes(digest)
        print(f"check={'ok' if ok else 'failed'} report_sha256={digest} bytes={len(payload)}")
        return 0 if ok else 1
    args.out.mkdir(parents=True, exist_ok=True)
    output.write_bytes(payload)
    sidecar.write_bytes(sidecar_bytes(digest))
    print(f"report_sha256={digest} bytes={len(payload)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
