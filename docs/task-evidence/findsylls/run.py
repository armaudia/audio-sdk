# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local evidence artifacts three times and require identity.

Ordering avoids cycles: the report is written first, the README digest table
covers a fixed subset that excludes the contract and this manifest, the contract
pins the final README/report/etc., and the manifest pins the final contract.
"""

from __future__ import annotations

import hashlib
import re
import sys
from pathlib import Path
from typing import Any, Dict, Tuple

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

MANIFEST_COMMENT = (
    "# SHA-256 pins for SDK-FINDSYLLS; source: is workspace-relative, "
    "worktree: is SDK-worktree-relative. The mutable board file is never pinned."
)
TABLE_FILES: Tuple[str, ...] = (
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "test_reference.py",
    "verify.py",
)
TABLE_START = "<!-- DIGEST_TABLE_START -->"
TABLE_END = "<!-- DIGEST_TABLE_END -->"


def _write_json(path: Path, value: Dict[str, Any]) -> bytes:
    payload = reference.canonical_bytes(value) + b"\n"
    path.write_bytes(payload)
    return payload


def report_bytes() -> bytes:
    return reference.canonical_report_bytes(reference.build_report())


def contract_bytes(artifact_pins: Dict[str, str] | None = None) -> bytes:
    contract = reference.build_contract()
    contract["artifact_pins"] = dict(artifact_pins or {})
    return reference.canonical_bytes(contract) + b"\n"


def _disk_bytes(name: str) -> bytes:
    path = HERE / name
    if not path.is_file() or path.is_symlink():
        raise RuntimeError("missing or non-regular local artifact: " + name)
    return path.read_bytes()


def render_readme(table: str, original: bytes | None = None) -> bytes:
    path = HERE / "README.md"
    text = (original if original is not None else path.read_bytes()).decode("utf-8")
    pattern = re.compile(re.escape(TABLE_START) + r"\n.*?\n" + re.escape(TABLE_END), re.S)
    if not pattern.search(text):
        raise RuntimeError("README digest table markers missing")
    replacement = TABLE_START + "\n" + table + "\n" + TABLE_END
    updated = pattern.sub(lambda _match: replacement, text, count=1)
    return updated.encode("utf-8")


def readme_table(payloads: Dict[str, bytes]) -> str:
    rows = ["| Path | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    for name in TABLE_FILES:
        payload = payloads[name]
        rows.append(f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |")
    return "\n".join(rows)


def generate(original_readme: bytes | None = None) -> Dict[str, bytes]:
    """Build every generated payload without touching the filesystem."""
    report = report_bytes()
    report_digest = hashlib.sha256(report).hexdigest()
    sidecar = f"{report_digest}  report.json\n".encode("ascii")
    table_payloads = {
        "reference.py": _disk_bytes("reference.py"),
        "report.json": report,
        "report.json.sha256": sidecar,
        "run.py": _disk_bytes("run.py"),
        "test_reference.py": _disk_bytes("test_reference.py"),
        "verify.py": _disk_bytes("verify.py"),
    }
    readme = render_readme(readme_table(table_payloads), original_readme)

    partial: Dict[str, bytes] = {
        "README.md": readme,
        "report.json": report,
        "report.json.sha256": sidecar,
    }
    pins: Dict[str, str] = {}
    for name in reference.LOCAL_FILES:
        if name == "contract.json":
            continue
        payload = partial.get(name)
        if payload is None:
            payload = _disk_bytes(name)
        pins[name] = hashlib.sha256(payload).hexdigest()
    contract = contract_bytes(pins)
    partial["contract.json"] = contract

    manifest_pins: Dict[str, str] = {}
    for raw, digest in reference.SOURCE_PINS.items():
        path = reference.SOURCE_ROOT / raw
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular source pin: " + raw)
        if reference.sha256_file(path) != digest:
            raise RuntimeError("stale source pin: " + raw)
        manifest_pins["source:" + raw] = digest
    for raw, digest in reference.BOUNDARY_PINS.items():
        path = reference.SDK_ROOT / raw
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular boundary pin: " + raw)
        if reference.sha256_file(path) != digest:
            raise RuntimeError("stale boundary pin: " + raw)
        manifest_pins["worktree:" + raw] = digest
    for name in reference.LOCAL_FILES:
        payload = partial.get(name)
        if payload is None:
            payload = _disk_bytes(name)
        manifest_pins["worktree:" + reference.TASK_PREFIX + name] = hashlib.sha256(payload).hexdigest()
    expected = len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS) + len(reference.LOCAL_FILES)
    if len(manifest_pins) != expected:
        raise RuntimeError("duplicate pin path")
    lines = [MANIFEST_COMMENT]
    lines.extend(f"{digest}  {raw}" for raw, digest in sorted(manifest_pins.items()))
    partial["SOURCES.sha256"] = ("\n".join(lines) + "\n").encode("utf-8")
    return partial


def generate_thrice() -> Dict[str, bytes]:
    original = (HERE / "README.md").read_bytes()
    payloads = generate(original)
    for _ in range(2):
        again = generate(original)
        if again != payloads:
            raise RuntimeError("three cold-start generations differ")
    return payloads


def write_all() -> Dict[str, Any]:
    payloads = generate_thrice()
    order = ("report.json", "report.json.sha256", "README.md", "contract.json", "SOURCES.sha256")
    for name in order:
        (HERE / name).write_bytes(payloads[name])
    report_digest = hashlib.sha256(payloads["report.json"]).hexdigest()
    return {
        "report_digest": report_digest,
        "report_bytes": len(payloads["report.json"]),
        "source_pins": len([line for line in payloads["SOURCES.sha256"].decode("ascii").splitlines() if line and not line.startswith("#")]),
    }


def main(argv: list[str]) -> int:
    modes = {"--all", "--report", "--contract", "--sources", "--readme", "--digest", "--check"}
    if len(argv) != 2 or argv[1] not in modes:
        print(
            "usage: run.py --all | --report | --contract | --sources | --readme | --digest | --check",
            file=sys.stderr,
        )
        return 2
    mode = argv[1]
    if mode == "--digest":
        print(hashlib.sha256(report_bytes()).hexdigest())
        return 0
    if mode == "--check":
        try:
            payloads = generate_thrice()
        except Exception as exc:  # noqa: BLE001
            print("FAIL " + str(exc), file=sys.stderr)
            return 1
        print("deterministic=true")
        print("report_sha256=" + hashlib.sha256(payloads["report.json"]).hexdigest())
        print("generated_files=" + str(len(payloads)))
        return 0
    if mode == "--report":
        payload = report_bytes()
        (HERE / "report.json").write_bytes(payload)
        digest = hashlib.sha256(payload).hexdigest()
        (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="ascii")
        print(f"report_sha256={digest} bytes={len(payload)}")
        return 0
    if mode == "--readme":
        payloads = generate((HERE / "README.md").read_bytes())
        (HERE / "README.md").write_bytes(payloads["README.md"])
        print("wrote README.md digest table")
        return 0
    if mode in ("--contract", "--sources", "--all"):
        info = write_all()
        print(f"report_sha256={info['report_digest']} bytes={info['report_bytes']}")
        print(f"source_pins={info['source_pins']}")
        print("deterministic_three_generations=true")
        return 0
    return 2


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
