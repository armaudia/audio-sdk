# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Verify pins, strict JSON, scope, licensing and exact reproduction.

Usage (from the task-local directory)::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Everything except the advisory git scope probe is read-only.  Reproducibility
is checked by three independent ``run.py --report`` processes compared to the
committed artifact.  No native SDK target or measured workload is implied.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import fixture as fx

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PYTHON = sys.executable
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
ADAPTER = HERE / "adapter.json"
REQUIRED_FILES = (
    "README.md", "fixture.py", "run.py", "adapter.json", "report.json",
    "report.json.sha256", "SOURCES.sha256", "test_fixture.py", "verify.py",
)
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
PASS_GATES = {
    "clean_checkout_and_pins", "one_typical_api_use", "caller_owned_inputs",
    "malformed_input_oracle", "missing_optional_selection",
    "stream_sequence_replay", "deterministic_reproduction",
}
BLOCKED_GATES = {
    "sdk_libfuzzer_target", "native_sdk_linked_replay",
    "measured_workload_support", "provider_intake",
}


def strict_json(data: bytes | str) -> dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError("nonfinite JSON constant " + value)

    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key " + key)
            result[key] = value
        return result

    payload = json.loads(data, parse_constant=reject, object_pairs_hook=pairs)
    if not isinstance(payload, dict):
        raise ValueError("JSON root is not an object")
    return payload


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ["git", "-C", str(SDK_ROOT), *args], capture_output=True,
        text=True, check=False)


def check_pins() -> list[str]:
    errors: list[str] = []
    for pin in fx.SOURCE_PINS:
        path = SOURCE_ROOT / pin["path"]
        if not path.is_file() or sha256(path) != pin["sha256"]:
            errors.append("source pin mismatch: " + pin["path"])
    toolchain = Path("/") / fx.TOOLCHAIN_PIN["path"]
    if not toolchain.is_file() or sha256(toolchain) != fx.TOOLCHAIN_PIN["sha256"]:
        errors.append("toolchain pin mismatch")
    for pin in fx.artifact_pins():
        path = HERE / pin["path"]
        if not path.is_file() or sha256(path) != pin["sha256"]:
            errors.append("artifact pin mismatch: " + pin["path"])
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    expected: dict[str, str] = {
        f"source:{pin['path']}": pin["sha256"] for pin in fx.SOURCE_PINS
    }
    expected[f"toolchain:{fx.TOOLCHAIN_PIN['path']}"] = fx.TOOLCHAIN_PIN["sha256"]
    for pin in fx.artifact_pins():
        expected[f"docs/task-evidence/{fx.SLUG}/{pin['path']}"] = pin["sha256"]
    # SOURCES.sha256 cannot pin itself; all other task-local files are pinned.
    for name in ("README.md", "report.json", "report.json.sha256"):
        expected[f"docs/task-evidence/{fx.SLUG}/{name}"] = sha256(HERE / name)
    manifest: dict[str, str] = {}
    for line in lines:
        digest, raw_path = line.split("  ", 1)
        manifest[raw_path] = digest
    if set(manifest) != set(expected):
        errors.append("SOURCES.sha256 path set mismatch")
    for path, digest in expected.items():
        if manifest.get(path) != digest:
            errors.append("SOURCES.sha256 digest mismatch: " + path)
    return errors


def check_json_and_claims() -> tuple[list[str], dict[str, Any]]:
    errors: list[str] = []
    report = strict_json(REPORT.read_bytes())
    adapter = strict_json(ADAPTER.read_bytes())
    if adapter["schema_id"] != fx.ADAPTER_SCHEMA_ID:
        errors.append("adapter schema_id")
    if adapter["task"] != fx.TASK_ID or report["task"] != fx.TASK_ID:
        errors.append("task id")
    if report["schema_id"] != fx.SCHEMA_ID:
        errors.append("report schema_id")
    if report["profile"] != "Tool":
        errors.append("profile")
    if report["status"] != "proposal_only_synthetic_incomplete":
        errors.append("status")
    if report["qualification_status"] != "not_qualified":
        errors.append("qualification_status")
    if report["no_missing_result_qualifies_candidate"] is not True:
        errors.append("no_missing_result_qualifies_candidate")
    if report["base_commit"] != fx.BASE_COMMIT:
        errors.append("base_commit")
    boundary = report["boundary"]
    if (boundary["format"] != {
            "sample_rate_hz": 16000, "channels": 1,
            "sample_format": "f32", "frame_samples": 160}):
        errors.append("boundary format")
    if boundary["abi"] != {"major": 0, "minor": 1}:
        errors.append("boundary abi")
    if boundary["compiled_sdk_calls"] != 0:
        errors.append("compiled_sdk_calls")
    if boundary["registered"] or boundary["enabled_by_default"]:
        errors.append("registration/default claims")
    if boundary["descriptor_settings"] != {}:
        errors.append("descriptor_settings")

    def walk(value: Any) -> None:
        if isinstance(value, float):
            if not math.isfinite(value):
                errors.append("nonfinite JSON float")
        elif isinstance(value, dict):
            for item in value.values():
                walk(item)
        elif isinstance(value, list):
            for item in value:
                walk(item)
    walk(report)
    walk(adapter)

    gates = {gate["id"]: gate for gate in report["gates"]}
    if set(gates) != PASS_GATES | BLOCKED_GATES:
        errors.append("gate id set")
    for name in PASS_GATES:
        if gates.get(name, {}).get("status") != "pass":
            errors.append("gate not pass: " + name)
    for name in BLOCKED_GATES:
        if gates.get(name, {}).get("status") != "blocked":
            errors.append("gate not blocked: " + name)
        if not gates.get(name, {}).get("reopen"):
            errors.append("gate has no reopen condition: " + name)
    evidence = report["evidence_classes"]
    if set(evidence) != {"compile_build", "synthetic_runtime",
                         "measured_workload_support"}:
        errors.append("evidence class set")
    if any(item["qualifying"] for item in evidence.values()):
        errors.append("non-qualifying evidence marked qualifying")
    if not report["stream_sequence"]["all_replays_pass"]:
        errors.append("stream invariant failure")
    if not report["malformed_output"]["all_replays_pass"]:
        errors.append("malformed oracle failure")
    if report["malformed_output"]["failing_explicit_cases"]:
        errors.append("explicit malformed failures")
    tool = report["toolchain"]["libfuzzer"]
    if tool["sdk_target_status"] != "blocked":
        errors.append("SDK libFuzzer target not blocked")
    if tool["authoritative_evidence"] != "deterministic_python_replay":
        errors.append("authoritative evidence")
    probes = {probe["compiler_path"]: probe for probe in tool["probe_invocations"]}
    if probes.get("/usr/bin/clang++", {}).get("result") != "link_failed":
        errors.append("Apple probe provenance")
    if probes.get("/opt/homebrew/opt/llvm/bin/clang++", {}).get(
            "result") != "compiled_and_ran":
        errors.append("Homebrew probe provenance")
    lines = [line for line in REPORT_SHA.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    if len(lines) != 1:
        errors.append("report.json.sha256 line count")
        digest, name = "", ""
    else:
        digest, name = lines[0].split()
    if name != "report.json" or digest != sha256(REPORT):
        errors.append("report.json.sha256")
    return errors, report


def check_licensing() -> list[str]:
    errors: list[str] = []
    for name in required_files():
        path = HERE / name
        if not path.is_file():
            errors.append("missing " + name)
            continue
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if name.endswith(".json"):
            license_ok = '"SPDX-License-Identifier":"Apache-2.0"' in head
            copyright_ok = '"SPDX-FileCopyrightText":"2026 Tsakanyan Hovhannes"' in head
        else:
            license_ok = SPDX_LICENSE in head
            copyright_ok = SPDX_COPYRIGHT in head
        if not license_ok or not copyright_ok:
            errors.append("SPDX header: " + name)
    readme = (HERE / "README.md").read_text(encoding="utf-8")
    if SPDX_LICENSE not in readme[:400]:
        errors.append("README SPDX notice")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml annotation")
    return errors


def required_files() -> tuple[str, ...]:
    return REQUIRED_FILES


def check_scope() -> list[str]:
    errors: list[str] = []
    branch = git("rev-parse", "--abbrev-ref", "HEAD")
    if branch.returncode != 0 or branch.stdout.strip() != fx.BRANCH:
        errors.append("unexpected branch: " + branch.stdout.strip())
    head = git("rev-parse", "HEAD")
    if head.returncode != 0:
        errors.append("cannot read HEAD")
    elif head.stdout.strip() != fx.BASE_COMMIT:
        # Uncommitted evidence files are expected before commit; pre-commit and
        # post-commit HEADs are both accepted if the base is an ancestor.
        ancestry = git("merge-base", "--is-ancestor", fx.BASE_COMMIT, "HEAD")
        if ancestry.returncode != 0:
            errors.append("base commit is not an ancestor of HEAD")
    status = git("status", "--porcelain", "--untracked-files=all")
    if status.returncode != 0:
        errors.append("git status failed")
        return errors
    prefix = f"docs/task-evidence/{fx.SLUG}/"
    for line in status.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:].split(" -> ")[-1]
        if not path.startswith(prefix):
            errors.append("out-of-scope git change: " + path)
    return errors


def check_reproduction() -> list[str]:
    errors: list[str] = []
    expected = REPORT.read_bytes()
    for attempt in range(3):
        result = subprocess.run(
            [PYTHON, str(HERE / "run.py"), "--report"],
            capture_output=True, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"),
            check=False)
        if result.returncode != 0:
            errors.append(f"regeneration {attempt} failed: {result.stderr[:200]!r}")
        elif result.stdout != expected:
            errors.append(f"regeneration {attempt} is not byte-identical")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    suite = subprocess.run(
        [PYTHON, "-m", "unittest", "test_fixture.py"], cwd=HERE,
        capture_output=True, env=env, check=False)
    if suite.returncode != 0:
        errors.append("unit suite failed: " + suite.stderr[-500:])
    return errors


def main() -> int:
    try:
        pins = check_pins()
        json_errors, _ = check_json_and_claims()
        licensing = check_licensing()
        scope = check_scope()
        reproduction = check_reproduction()
    except (OSError, ValueError, KeyError) as error:
        print("verify_error: " + repr(error), file=sys.stderr)
        return 2
    checks = {
        "pins_ok": not pins,
        "json_ok": not json_errors,
        "licensing_ok": not licensing,
        "scope_ok": not scope,
        "reproduction_ok": not reproduction,
    }
    print(json.dumps(checks, sort_keys=True, separators=(",", ":")))
    for label, errors in (("pins", pins), ("json", json_errors),
                          ("licensing", licensing), ("scope", scope),
                          ("reproduction", reproduction)):
        for error in errors:
            print(f"{label}_error: {error}", file=sys.stderr)
    return 0 if all(checks.values()) else 1


if __name__ == "__main__":
    sys.exit(main())
