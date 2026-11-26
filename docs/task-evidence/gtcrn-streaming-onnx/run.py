# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate byte-identical report.json, digest sidecar, README digests and manifest."""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

README_FILES = ("contract.json", "adapter.json", "provider.json", "asset.json",
                "scorer.py", "report.json", "report.json.sha256")


def generate_report() -> str:
    payloads = [reference.canonical_report_bytes(reference.build_report()) for _ in range(3)]
    if len(set(payloads)) != 1:
        raise SystemExit("refusing to write: three in-process passes differ")
    payload = payloads[0]
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    return digest


def refresh_readme() -> int:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    updated = text
    for name in README_FILES:
        digest = hashlib.sha256((HERE / name).read_bytes()).hexdigest()
        pattern = re.compile(r"(\| `" + re.escape(name) + r"` \| `)[0-9a-f]{64}(` \|)")
        updated, count = pattern.subn(lambda match: match.group(1) + digest + match.group(2),
                                      updated, count=1)
        if count != 1:
            raise SystemExit("README digest row missing or duplicated: " + name)
    if updated != text:
        path.write_text(updated, encoding="utf-8")
        return 1
    return 0


def generate_sources() -> int:
    payloads = [reference.sources_bytes() for _ in range(3)]
    if len(set(payloads)) != 1:
        raise SystemExit("refusing to write: three source-manifest passes differ")
    (HERE / "SOURCES.sha256").write_bytes(payloads[0])
    return len(reference.parse_pin_lines(payloads[0].decode("utf-8")))


def main(argv: list[str]) -> int:
    commands = {"report.json", "--report", "--sources", "--readme", "--all"}
    if len(argv) != 2 or argv[1] not in commands:
        print("usage: run.py {report.json|--report|--readme|--sources|--all}", file=sys.stderr)
        return 2
    command = argv[1]
    if command in ("report.json", "--report"):
        digest = generate_report()
        print(f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size}")
    elif command == "--readme":
        print(f"readme_rows_updated={refresh_readme()}")
    elif command == "--sources":
        print(f"pins={generate_sources()}")
    else:
        digest = generate_report()
        refresh_readme()
        pins = generate_sources()
        print(f"report_sha256={digest} bytes={(HERE / 'report.json').stat().st_size} pins={pins}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
