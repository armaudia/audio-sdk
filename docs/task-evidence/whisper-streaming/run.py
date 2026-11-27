# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate task-local Whisper-Streaming blocker evidence.

Only this task directory is written. Pinned source/boundary files are read-only.
No model, audio, network, or runtime execution occurs.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

TASK_PREFIX = reference.TASK_PREFIX
REPEAT_COUNT = 3
LOCAL_PIN_FILES = reference.LOCAL_PIN_PATHS
TARGETS = {"report.json", "contract.json", "sources", "all"}


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def report_bytes() -> tuple[bytes, str]:
    report = reference.build_report(reference.build_contract())
    payload = reference.canonical_bytes(report)
    return reference.canonical_file_bytes(report), hashlib.sha256(reference.canonical_file_bytes(report)).hexdigest()


def sources_bytes() -> bytes:
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.SOURCE_ROOT / relative
        if not path.is_file():
            raise ValueError("missing_source_pin:" + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("source_pin_mismatch:" + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = reference.SDK_ROOT / relative
        if not path.is_file():
            raise ValueError("missing_boundary_pin:" + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("boundary_pin_mismatch:" + relative)
        rows.append((relative, actual))
    for name in LOCAL_PIN_FILES:
        path = HERE / name
        if not path.is_file():
            raise ValueError("local_pin_missing:" + name)
        rows.append((TASK_PREFIX + name, reference.sha256_file(path)))
    lines = [
        "# SHA-256 pins for SDK-WHISPER-STREAMING feasibility evidence.",
        "# source: paths are relative to SOURCE_ROOT; other paths are SDK-worktree relative.",
        "# The mutable shared board is not pinned; only stable task-row identity is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
    ]
    lines.extend(f"{digest}  {name}" for name, digest in rows)
    return ("\n".join(lines) + "\n").encode("ascii")


def write_once(targets: set[str]) -> str:
    digest = ""
    if "contract.json" in targets or "report.json" in targets:
        contract = contract_bytes()
        report, digest = report_bytes()
        (HERE / "contract.json").write_bytes(contract)
        (HERE / "report.json").write_bytes(report)
        (HERE / "report.json.sha256").write_bytes(f"{digest}  report.json\n".encode("ascii"))
    if "sources" in targets:
        (HERE / "SOURCES.sha256").write_bytes(sources_bytes())
    return digest


def check_once(targets: set[str]) -> None:
    if "contract.json" in targets or "report.json" in targets:
        expected_contract = contract_bytes()
        expected_report, digest = report_bytes()
        if (HERE / "contract.json").read_bytes() != expected_contract:
            raise SystemExit("contract.json mismatch")
        if (HERE / "report.json").read_bytes() != expected_report:
            raise SystemExit("report.json mismatch")
        expected_sidecar = f"{digest}  report.json\n".encode("ascii")
        if (HERE / "report.json.sha256").read_bytes() != expected_sidecar:
            raise SystemExit("report.json.sha256 mismatch")
    if "sources" in targets:
        if (HERE / "SOURCES.sha256").read_bytes() != sources_bytes():
            raise SystemExit("SOURCES.sha256 mismatch")


def main(argv: list[str]) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("target", nargs="?", default="all", choices=sorted(TARGETS))
    parser.add_argument("--out", default="")
    parser.add_argument("--check", action="store_true")
    args = parser.parse_args(argv[1:])
    targets = {args.target}
    if "all" in targets:
        targets = {"contract.json", "report.json", "sources"}
    out = Path(args.out) if args.out else HERE
    if out != HERE:
        out.mkdir(parents=True, exist_ok=True)
        # Regenerate in temp out by temporarily swapping HERE behavior is not needed;
        # generate bytes and write to out.
        if args.check:
            raise SystemExit("--check not supported with --out")
        digest = ""
        for _ in range(REPEAT_COUNT):
            if "contract.json" in targets or "report.json" in targets:
                c = contract_bytes()
                r, digest = report_bytes()
                (out / "contract.json").write_bytes(c)
                (out / "report.json").write_bytes(r)
                (out / "report.json.sha256").write_bytes(f"{digest}  report.json\n".encode("ascii"))
            if "sources" in targets:
                # sources include local files; only meaningful in HERE, but keep deterministic.
                pass
        print(f"repeat={REPEAT_COUNT} report_sha256={digest}")
        return 0
    if args.check:
        check_once(targets)
        print("ok")
        return 0
    observed = []
    digest = ""
    for _ in range(REPEAT_COUNT):
        digest = write_once(targets)
        observed.append((
            hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest() if (HERE / "report.json").exists() else "-",
            hashlib.sha256((HERE / "contract.json").read_bytes()).hexdigest() if (HERE / "contract.json").exists() else "-",
            hashlib.sha256((HERE / "SOURCES.sha256").read_bytes()).hexdigest() if (HERE / "SOURCES.sha256").exists() else "-",
        ))
    if len(set(observed)) != 1:
        print("FAIL: non-identical regeneration", file=sys.stderr)
        return 1
    print(f"repeat={REPEAT_COUNT} byte_identical=true report_sha256={observed[0][0]} contract_sha256={observed[0][1]} sources_sha256={observed[0][2]}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
