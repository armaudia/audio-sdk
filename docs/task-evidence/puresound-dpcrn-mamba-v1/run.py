# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local evidence artifacts, sidecars, README table and pins."""

from __future__ import annotations

import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Dict

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

MANIFEST_COMMENT = (
    "# SHA-256 pins for SDK-PURESOUND-DPCRN-MAMBA-V1; source: is workspace-relative, "
    "worktree: is SDK-worktree-relative."
)


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


def contract_pins() -> Dict[str, str]:
    pins: Dict[str, str] = {}
    for name in reference.LOCAL_FILES:
        if name == "contract.json":
            continue
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular local artifact: " + name)
        pins[name] = reference.sha256_file(path)
    return pins


def readme_table() -> str:
    rows = []
    for name in reference.README_DIGEST_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular README digest target: " + name)
        data = path.read_bytes()
        rows.append(f"| `{name}` | `{hashlib.sha256(data).hexdigest()}` | {len(data)} |")
    return "\n".join([
        reference.README_TABLE_START,
        "| Artifact | SHA-256 | Bytes |",
        "| --- | --- | ---: |",
        *rows,
        reference.README_TABLE_END,
    ])


def readme_bytes() -> bytes:
    path = HERE / "README.md"
    text = path.read_text(encoding="utf-8")
    start = text.index(reference.README_TABLE_START)
    end = text.index(reference.README_TABLE_END) + len(reference.README_TABLE_END)
    return (text[:start] + readme_table() + text[end:]).encode("utf-8")


def manifest_bytes() -> bytes:
    pins: Dict[str, str] = {}
    for raw, digest in reference.SOURCE_PINS.items():
        path = reference.SOURCE_ROOT / raw
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular source pin: " + raw)
        if reference.sha256_file(path) != digest:
            raise RuntimeError("stale source pin: " + raw)
        pins["source:" + raw] = digest
    for raw, digest in reference.BOUNDARY_PINS.items():
        path = reference.SDK_ROOT / raw
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular boundary pin: " + raw)
        if reference.sha256_file(path) != digest:
            raise RuntimeError("stale boundary pin: " + raw)
        pins["worktree:" + raw] = digest
    for name in reference.LOCAL_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            raise RuntimeError("missing or non-regular local artifact: " + name)
        pins[f"worktree:{reference.TASK_PREFIX}{name}"] = reference.sha256_file(path)
    expected = (len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS)
                + len(reference.LOCAL_FILES))
    if len(pins) != expected:
        raise RuntimeError("duplicate pin path")
    lines = [MANIFEST_COMMENT]
    lines.extend(f"{digest}  {raw}" for raw, digest in sorted(pins.items()))
    return ("\n".join(lines) + "\n").encode("utf-8")


def write_report() -> Dict[str, Any]:
    payload = report_bytes()
    (HERE / "report.json").write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    (HERE / "report.json.sha256").write_text(f"{digest}  report.json\n", encoding="utf-8")
    return {"digest": digest, "bytes": len(payload)}


def write_static() -> None:
    _write_json(HERE / "adapter.json", reference.build_adapter())
    _write_json(HERE / "asset.json", reference.build_asset())
    _write_json(HERE / "readiness.json", reference.build_readiness())


def write_readme() -> bool:
    payload = readme_bytes()
    current = (HERE / "README.md").read_bytes()
    if current != payload:
        (HERE / "README.md").write_bytes(payload)
        return True
    return False


def write_contract() -> None:
    payload = contract_bytes(contract_pins())
    (HERE / "contract.json").write_bytes(payload)


def write_manifest() -> int:
    payload = manifest_bytes()
    (HERE / "SOURCES.sha256").write_bytes(payload)
    return len(payload.splitlines()) - 1


def main(argv: list[str]) -> int:
    modes = {"--all", "--report", "--static", "--readme", "--contract",
             "--sources", "--digest"}
    if len(argv) != 2 or argv[1] not in modes:
        print("usage: run.py --all | --report | --static | --readme | --contract | "
              "--sources | --digest", file=sys.stderr)
        return 2
    mode = argv[1]
    if mode in ("--static", "--all"):
        write_static()
        print("wrote adapter.json asset.json readiness.json")
    if mode in ("--report", "--all"):
        info = write_report()
        print(f"report_sha256={info['digest']} bytes={info['bytes']}")
    if mode in ("--readme", "--all"):
        changed = write_readme()
        print("updated README.md digest table" if changed else "README.md digest table current")
    if mode in ("--contract", "--all"):
        write_contract()
        print("wrote contract.json")
    if mode in ("--sources", "--all"):
        print(f"source_pins={write_manifest()}")
    if mode == "--digest":
        print(hashlib.sha256(report_bytes()).hexdigest())
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
