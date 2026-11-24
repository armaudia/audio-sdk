# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Developer-facing tool entry point for the deterministic SDK-v0 replay.

Typical uses (from this directory, pinned Python 3.12.16)::

    PYTHONDONTWRITEBYTECODE=1 python3 run.py report.json
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --report
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --scenario stream_sequence --seed 20261124
    PYTHONDONTWRITEBYTECODE=1 python3 run.py --bytes 8101414101022242 --scenario stream_sequence

No SDK provider is registered or installed and no public surface changes.  All
buffers are caller-owned in the model; ``--bytes`` is the caller-owned raw
input path.  Every response is canonical JSON (sorted keys, compact separators,
strict finite numbers).
"""

from __future__ import annotations

import argparse
import hashlib
import sys
from pathlib import Path
from typing import Any

import fixture as fx


def emit(value: Any) -> None:
    sys.stdout.buffer.write(fx.canonical_bytes(value) + b"\n")


def parse_hex(text: str) -> bytes:
    try:
        return bytes.fromhex(text.replace(" ", ""))
    except ValueError as error:
        raise ValueError("invalid_hex_input") from error


def scenario_result(scenario: str, seed: int, data: bytes | None) -> dict[str, Any]:
    if scenario == "stream_sequence":
        if data is None:
            data = fx.fuzz_bytes(seed, "stream_sequence",
                                 fx.MAX_STREAM_OPERATIONS)
        result = fx.replay_stream_seed(
            seed, "caller_supplied" if data is not None else "cli",
            data, max(len(data), 1))
        return {
            "operation": "scenario",
            "scenario": scenario,
            "seed": seed,
            "input_hex": data.hex(),
            "input_digest": hashlib.sha256(data).hexdigest(),
            "trace_digest": result["trace_digest"],
            "accepted": result["accepted"],
            "rejected": result["rejected"],
            "caller_local": result["caller_local"],
            "status_counts": result["status_counts"],
            "all_invariants_pass": result["all_invariants_pass"],
            "invariants": result["invariants"],
        }
    if scenario == "malformed_output":
        if data is None:
            data = fx.fuzz_bytes(seed, "malformed_output", 160)
        records = [fx.replay_output_case(fx.decode_output_case(data, index),
                                         data, index)
                   for index in range(max(len(data), 1))]
        summary = fx.summarize_output_records(records)
        return {
            "operation": "scenario",
            "scenario": scenario,
            "seed": seed,
            "input_digest": hashlib.sha256(data).hexdigest(),
            "accepted": summary["accepted"],
            "rejected": summary["rejected"],
            "status_counts": summary["status_counts"],
            "rule_counts": summary["rule_counts"],
            "records_digest": summary["records_digest"],
            "all_oracle_checks_pass": summary["all_oracle_checks_pass"],
        }
    raise ValueError("unknown scenario: " + scenario)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("output", nargs="?", type=Path,
                        help="write canonical report.json bytes to this path")
    parser.add_argument("--report", action="store_true",
                        help="write canonical report bytes to stdout")
    parser.add_argument("--inspect", action="store_true",
                        help="write the adapter manifest to stdout")
    parser.add_argument("--scenario", choices=("stream_sequence",
                                               "malformed_output"))
    parser.add_argument("--seed", type=int, default=fx.SEED)
    parser.add_argument("--bytes", type=str,
                        help="caller-owned raw input as hex for --scenario")
    options = parser.parse_args(argv)

    selected = sum(bool(flag) for flag in (
        options.report, options.inspect, options.scenario, options.output))
    if selected > 1:
        parser.error("choose one of output path, --report, --inspect or --scenario")
    if options.bytes is not None and options.scenario is None:
        parser.error("--bytes requires --scenario")

    try:
        if options.inspect:
            emit(fx.inspect())
        elif options.scenario is not None:
            data = parse_hex(options.bytes) if options.bytes is not None else None
            emit(scenario_result(options.scenario, options.seed, data))
        else:
            payload = fx.canonical_report_bytes()
            if options.output is not None:
                options.output.write_bytes(payload)
            else:
                sys.stdout.buffer.write(payload)
    except (OSError, ValueError) as error:
        sys.stderr.write("request_error: %s\n" % error)
        return 2
    return 0


if __name__ == "__main__":
    sys.exit(main())
