# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Normalize the installed-consumer and conformance reports into pinned JSON."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from fixture import SOURCE_PINS, canonical_fixture, canonical_json, digest

SUMMARY_SCHEMA = "audio-sdk/task-evidence/identity-pcm-summary/0.1"


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def write_canonical(out_dir: Path, name: str, value: dict[str, Any]) -> str:
    text = canonical_json(value)
    path = out_dir / f"{name}.canonical.json"
    path.write_text(text + "\n", encoding="utf-8")
    value_digest = digest(text)
    (out_dir / f"{name}.canonical.json.sha256").write_text(
        f"{value_digest}  {path.name}\n", encoding="utf-8")
    return value_digest


def check_counts(checks: list[dict[str, Any]]) -> dict[str, int]:
    counts = {"total": len(checks), "pass": 0, "fail": 0, "skip": 0}
    for check in checks:
        result = check.get("result")
        if result in counts:
            counts[result] += 1
        else:
            raise ValueError(f"unknown conformance result: {result!r}")
    return counts


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--consumer", type=Path, required=True)
    parser.add_argument("--conformance", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--base", required=True)
    args = parser.parse_args()

    args.out.mkdir(parents=True, exist_ok=True)
    consumer = load(args.consumer)
    conformance = load(args.conformance)
    if conformance.get("schema_id") != "audio-sdk/conformance/0.1":
        raise ValueError("unexpected conformance report schema")
    if consumer.get("schema_id") != "audio-sdk/task-evidence/identity-pcm/0.1":
        raise ValueError("unexpected installed-consumer report schema")
    if consumer.get("conformance_exit") != 0:
        raise ValueError("installed conformance did not exit cleanly")
    if consumer.get("build_id") != conformance.get("build_id"):
        raise ValueError("consumer and conformance build IDs differ")
    if consumer.get("provider_id") != conformance.get("provider_id"):
        raise ValueError("consumer and conformance provider IDs differ")

    checks = conformance["checks"]
    counts = check_counts(checks)
    adverse = [{"id": check.get("id"), "result": check["result"],
                "detail": check.get("detail", "")}
               for check in checks if check.get("result") != "pass"]
    case_failures = [case for case in consumer.get("cases", [])
                     if case.get("result") != "pass"]

    consumer_digest = write_canonical(args.out, "consumer-report", consumer)
    conformance_digest = write_canonical(args.out, "conformance-report", conformance)
    fixture_text, fixture_digest = canonical_fixture()

    summary: dict[str, Any] = {
        "schema_id": SUMMARY_SCHEMA,
        "base_commit": args.base,
        "source_pins": dict(SOURCE_PINS),
        "fixture_digest": fixture_digest,
        "fixture_bytes": len(fixture_text.encode("utf-8")),
        "installation": {
            "version": consumer.get("version"),
            "build_id": consumer.get("build_id"),
            "location_label": consumer.get("install_location"),
            "archive_sha256": consumer.get("archive_sha256"),
            "provenance": "clean pinned checkout, native Release build, normalized extracted archive",
        },
        "consumer": {
            "report_digest": consumer_digest,
            "provider_id": consumer.get("provider_id"),
            "cases": consumer.get("cases", []),
            "failed_cases": case_failures,
        },
        "conformance": {
            "report_digest": conformance_digest,
            "provider_id": conformance.get("provider_id"),
            "descriptor_digest": conformance.get("descriptor_digest"),
            "counts": counts,
            "adverse": adverse,
        },
        "workload_support": {
            "status": "not_measured",
            "reason": "synthetic conformance only; no pacing, CPU, deadline, device or model workload",
        },
        "status": "complete" if not adverse and not case_failures
                  and counts["fail"] == 0 and counts["skip"] == 0
                  and consumer.get("result") == "pass" else "incomplete",
    }
    summary_digest = write_canonical(args.out, "summary", summary)
    print(json.dumps({
        "summary": str(args.out / "summary.canonical.json"),
        "summary_sha256": summary_digest,
        "consumer_sha256": consumer_digest,
        "conformance_sha256": conformance_digest,
        "fixture_sha256": fixture_digest,
        "status": summary["status"],
        "checks": counts,
    }, sort_keys=True))


if __name__ == "__main__":
    main()
