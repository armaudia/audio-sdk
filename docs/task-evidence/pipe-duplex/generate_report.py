# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate or byte-compare the frozen SDK-PIPE-DUPLEX canonical report."""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import host  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--cli", required=True, type=Path,
                        help="path to the merged, opt-in mdf_reference_cli binary")
    parser.add_argument("--work", required=True, type=Path,
                        help="scratch directory outside the worktree")
    parser.add_argument("--write", action="store_true",
                        help="bootstrap the frozen report once")
    parser.add_argument("--force", action="store_true",
                        help="allow --write to replace an existing frozen report")
    args = parser.parse_args()

    payload = host.canonical_bytes(host.build_report(args.cli, args.work))
    report = HERE / "report.json"
    sidecar = HERE / "report.json.sha256"
    if args.write:
        if report.exists() and not args.force:
            raise SystemExit("refusing to overwrite an existing frozen report")
        report.write_bytes(payload)
        sidecar.write_text(host.sha256(payload) + "  report.json\n", encoding="ascii")
    else:
        if not report.is_file():
            raise SystemExit("frozen report is missing; bootstrap once with --write")
        frozen = report.read_bytes()
        if frozen != payload:
            raise SystemExit("report mismatch: generated %s, frozen %s" %
                             (host.sha256(payload), host.sha256(frozen)))
        expected_sidecar = sidecar.read_text(encoding="ascii").split()[0]
        if expected_sidecar != host.sha256(frozen):
            raise SystemExit("report sidecar mismatch")
    print("report_sha256=%s" % host.sha256(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
