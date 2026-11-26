# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local CLI for deterministic regeneration and inspection.

``--all`` rebuilds the canonical report, its SHA-256 sidecar and the contract in
this process and writes only when the three in-process builds are byte-identical;
``verify.py`` repeats the same command in three cold-start processes.  ``--check``
is read-only.  ``--sources`` prints the local manifest.  ``--inspect`` prints a
small canonical summary.  Nothing outside this evidence directory is written and
nothing is downloaded, imported from a model runtime or scored.
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Dict, List, Tuple

sys.dont_write_bytecode = True

import reference  # noqa: E402

ROOT = Path(__file__).resolve().parent
ROUNDS = 3
FILES = ("report.json", "report.json.sha256", "contract.json", "SOURCES.sha256")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def local_names() -> List[str]:
    names = set()
    for path in ROOT.rglob("*"):
        if not path.is_file():
            continue
        relative = path.relative_to(ROOT).as_posix()
        if relative == "SOURCES.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        names.add(relative)
    names.update(("report.json", "report.json.sha256"))
    return sorted(names)


def _pins(pending: Dict[str, bytes]) -> Dict[str, str]:
    rows: Dict[str, str] = {}
    for name in local_names():
        if name == "contract.json":
            continue
        data = pending.get(name)
        if data is None:
            path = ROOT / name
            if not path.is_file():
                continue
            data = path.read_bytes()
        rows[name] = hashlib.sha256(data).hexdigest()
    return rows


def _sources(pending: Dict[str, bytes]) -> bytes:
    rows = []
    for name in local_names():
        data = pending.get(name)
        if data is None:
            path = ROOT / name
            if not path.is_file():
                continue
            data = path.read_bytes()
        rows.append("%s  %s" % (hashlib.sha256(data).hexdigest(), name))
    return ("\n".join(rows) + "\n").encode("utf-8")


def render_sources() -> bytes:
    return _sources({})


def _round() -> Tuple[Dict[str, bytes], str, str]:
    report_payload, report_digest, core_digest = reference.render_report()
    sidecar = (report_digest + "\n").encode("ascii")
    pending = {
        "report.json": report_payload,
        "report.json.sha256": sidecar,
    }
    contract_payload = reference.canonical_bytes(
        reference.contract_payload(_pins(pending))
    ) + b"\n"
    pending["contract.json"] = contract_payload
    files = dict(pending)
    files["SOURCES.sha256"] = _sources(pending)
    return files, report_digest, core_digest


def generate() -> int:
    rounds = [_round() for _ in range(ROUNDS)]
    if any(result[0] != rounds[0][0] for result in rounds):
        print("FAIL: cold-start rounds are not byte-identical", file=sys.stderr)
        return 1
    files, report_digest, core_digest = rounds[0]
    for name, data in files.items():
        (ROOT / name).write_bytes(data)
    summary = {
        "report_sha256": report_digest,
        "report_core_sha256": core_digest,
        "contract_sha256": hashlib.sha256(files["contract.json"]).hexdigest(),
        "sources_sha256": hashlib.sha256(files["SOURCES.sha256"]).hexdigest(),
        "byte_identical_in_process": True,
    }
    sys.stdout.buffer.write(reference.canonical_bytes(summary) + b"\n")
    return 0


def check() -> int:
    rounds = [_round() for _ in range(ROUNDS)]
    if any(result[0] != rounds[0][0] for result in rounds):
        print("FAIL: cold-start rounds are not byte-identical", file=sys.stderr)
        return 1
    expected, report_digest, _ = rounds[0]
    failures = []
    for name in FILES:
        path = ROOT / name
        if not path.is_file():
            failures.append(name + ": missing")
        elif path.read_bytes() != expected[name]:
            failures.append(name + ": stale")
    if failures:
        for failure in failures:
            print("FAIL: " + failure, file=sys.stderr)
        return 1
    print("check_ok=1 report_sha256=%s rounds=%d" % (report_digest, ROUNDS))
    return 0


def inspect_payload() -> Dict[str, object]:
    return {
        "schema_id": reference.SCHEMA_ID,
        "task": reference.TASK_ID,
        "component": reference.COMPONENT,
        "profile": reference.PROFILE,
        "base_commit": reference.BASE_COMMIT,
        "branch": reference.BRANCH,
        "status": reference.STATUS,
        "completeness": reference.COMPLETENESS,
        "decision": reference.DECISION,
        "qualification": reference.QUALIFICATION,
        "cohort": {
            "item_count": reference.ITEM_COUNT,
            "processed_revision": reference.PROCESSED_REVISION,
            "license": reference.COHORT_LICENSE,
            "present": False,
        },
        "scorer": {
            "id": "dnsmos_c",
            "checkpoint_sha256": None,
            "source_revision": None,
            "score_slots": reference.scorer_record()["score_slots"],
        },
        "adverse_count": len(reference.adverse_results()),
        "missing_count": len(reference.missing_results()),
        "release_gates": [
            {"id": gate["id"], "status": gate["status"],
             "qualifies": gate["qualifies"]}
            for gate in reference.RELEASE_GATES
        ],
        "scope": reference.SCOPE,
        "public_surface": reference.PUBLIC_SURFACE,
        "qualifies": False,
    }


def main(argv: List[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--all", action="store_true",
                       help="regenerate report, sidecar, contract and manifest")
    group.add_argument("--check", action="store_true",
                       help="compare current files with a fresh build")
    group.add_argument("--sources", action="store_true",
                       help="print the local SOURCES.sha256 manifest")
    group.add_argument("--inspect", action="store_true",
                       help="print a canonical evidence summary")
    options = parser.parse_args(argv)
    if options.all:
        return generate()
    if options.check:
        return check()
    if options.sources:
        sys.stdout.buffer.write(render_sources())
        return 0
    sys.stdout.buffer.write(
        reference.canonical_bytes(inspect_payload()) + b"\n"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
