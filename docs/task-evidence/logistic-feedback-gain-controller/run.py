#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local protocol-v1-shaped adapter and deterministic report entrypoint."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def canonical_report_bytes() -> bytes:
    return (HERE / "report.json").read_bytes()


def check_outputs() -> dict:
    report = json.loads(canonical_report_bytes().decode("utf-8"))
    expected = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    actual = hashlib.sha256(canonical_report_bytes()).hexdigest()
    if actual != expected:
        raise ValueError(f"report digest mismatch: {actual} != {expected}")
    model_bytes = (HERE / "model.json").read_bytes()
    model = json.loads(model_bytes.decode("utf-8"))
    if hashlib.sha256(reference.canonical_bytes(model)).hexdigest() != report["training"]["model_digest"]:
        raise ValueError("model digest mismatch")
    return {"report_sha256": actual,
            "model_digest": report["training"]["model_digest"],
            "fixture_digest": report["fixture"]["digest"]}


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--report", action="store_true",
                        help="regenerate report.json, model.json and report.json.sha256")
    parser.add_argument("--check", action="store_true",
                        help="validate committed report/model digests")
    options = parser.parse_args()
    if options.report == options.check:
        parser.error("choose exactly one of --report or --check")
    if options.check:
        print(json.dumps(check_outputs(), indent=2))
        return
    report = reference.write_outputs()
    print(json.dumps({
        "report": "report.json",
        "report_sha256": (HERE / "report.json.sha256").read_text(encoding="utf-8").strip(),
        "fixture_digest": report["fixture"]["digest"],
        "model_digest": report["training"]["model_digest"],
        "heldout_detection_metrics": report["heldout_detection_metrics"],
    }, indent=2))


if __name__ == "__main__":
    main()
