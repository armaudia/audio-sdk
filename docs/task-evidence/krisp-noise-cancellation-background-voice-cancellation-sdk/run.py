# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Regenerate the task-local Krisp NC/BVC evidence bundle three times.

Only this task-local directory is written. Pinned source and boundary files are
read-only inputs. No vendor SDK, entitlement key, model bundle, runtime or audio
is loaded, imported or produced.
"""

from __future__ import annotations

import argparse
import hashlib
import platform
import sys
from pathlib import Path

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

REPEAT_COUNT = 3
ARTIFACTS = ("contract.json", "report.json", "report.json.sha256",
             "SOURCES.sha256")
TARGETS = ("contract.json", "report.json", "sources", "all")


def require_interpreter() -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        raise SystemExit(
            "run.py requires CPython %s (observed %s); the canonical bundle "
            "pins the interpreter used for regeneration."
            % (reference.REQUIRED_INTERPRETER, observed))


def sidecar_bytes(digest: str) -> bytes:
    return f"{digest}  report.json\n".encode("ascii")


def source_lines() -> list[str]:
    rows: list[tuple[str, str]] = []
    for relative, expected in sorted(reference.SOURCE_PINS.items()):
        path = reference.SOURCE_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("source pin target missing: " + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("source pin digest changed: " + relative)
        rows.append(("source:" + relative, actual))
    for relative, expected in sorted(reference.BOUNDARY_PINS.items()):
        path = reference.SDK_ROOT / relative
        if not path.is_file():
            raise FileNotFoundError("worktree pin target missing: " + relative)
        actual = reference.sha256_file(path)
        if actual != expected:
            raise ValueError("worktree pin digest changed: " + relative)
        rows.append(("worktree:" + relative, actual))
    for name in reference.LOCAL_PIN_PATHS:
        path = HERE / name
        if not path.is_file():
            raise FileNotFoundError("package pin target missing: " + name)
        rows.append(("pkg:" + name, reference.sha256_file(path)))
    lines = [
        "# SHA-256 pins for " + reference.TASK + ".",
        "# source: paths are relative to SOURCE_ROOT; worktree: paths are",
        "# relative to the SDK checkout; pkg: paths are relative to this",
        "# task-evidence directory. The mutable full plan/swarm/TASKS.json is",
        "# never hashed; only the linked-row stable identity is gated.",
        "# SOURCES.sha256 is excluded because a file cannot pin its own bytes.",
        "",
    ]
    lines.extend(f"{digest}  {label}" for label, digest in rows)
    return lines


def contract_bytes() -> bytes:
    return reference.canonical_bytes(reference.build_contract())


def report_bytes() -> tuple[bytes, str]:
    payload = reference.canonical_report_bytes(reference.build_report())
    return payload, reference.sha256(payload)


def sources_bytes() -> bytes:
    return ("\n".join(source_lines()) + "\n").encode("utf-8")


def expected_artifacts() -> dict[str, bytes]:
    contract = contract_bytes()
    report, digest = report_bytes()
    return {
        "contract.json": contract,
        "report.json": report,
        "report.json.sha256": sidecar_bytes(digest),
        "SOURCES.sha256": sources_bytes(),
    }


def write_once(targets: set[str]) -> dict[str, str]:
    digests: dict[str, str] = {}
    if "contract.json" in targets:
        payload = contract_bytes()
        (HERE / "contract.json").write_bytes(payload)
        digests["contract.json"] = reference.sha256(payload)
    if "report.json" in targets:
        payload, digest = report_bytes()
        (HERE / "report.json").write_bytes(payload)
        (HERE / "report.json.sha256").write_bytes(sidecar_bytes(digest))
        digests["report.json"] = reference.sha256(payload)
        digests["report.json.sha256"] = reference.sha256(sidecar_bytes(digest))
    if "sources" in targets:
        payload = sources_bytes()
        (HERE / "SOURCES.sha256").write_bytes(payload)
        digests["SOURCES.sha256"] = reference.sha256(payload)
    return digests


def check(targets: set[str]) -> bool:
    expected = expected_artifacts()
    ok = True
    for name in ARTIFACTS:
        if name == "SOURCES.sha256" and "sources" not in targets:
            continue
        if name == "contract.json" and "contract.json" not in targets:
            continue
        if name in ("report.json", "report.json.sha256") \
                and "report.json" not in targets:
            continue
        path = HERE / name
        if not path.is_file() or path.read_bytes() != expected[name]:
            print("FAIL: " + name + " is not reproducible", file=sys.stderr)
            ok = False
    return ok


def main(argv: list[str] | None = None) -> int:
    require_interpreter()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", nargs="?", default="all", choices=TARGETS)
    parser.add_argument("--check", action="store_true",
                        help="verify committed artifacts without writing")
    args = parser.parse_args(argv)

    targets = {"contract.json", "report.json", "sources"} \
        if args.target == "all" else {args.target}
    if args.check:
        return 0 if check(targets) else 1

    observed: list[tuple[str, ...]] = []
    last: dict[str, str] = {}
    for _ in range(REPEAT_COUNT):
        last = write_once(targets)
        observed.append(tuple(sorted(last.items())))
    if len(set(observed)) != 1:
        print("FAIL: regeneration was not byte-identical", file=sys.stderr)
        return 1
    report_digest = last.get("report.json", "-")
    sources_digest = last.get("SOURCES.sha256", "-")
    print(f"repeat={REPEAT_COUNT} byte_identical=true "
          f"report_sha256={report_digest} sources_sha256={sources_digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
