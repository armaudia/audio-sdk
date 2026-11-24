# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the task-local FFmpeg-afftdn evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Checks exact source pins, strict JSON, local artifact pins, contract and
adapter/provider disposition, three cold-start repeats of every CLI mode,
byte-identical report regeneration, SPDX/licensing controls, minimum test
count and write-scope containment.  Missing or changed evidence is a hard
failure.
"""

from __future__ import annotations

import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

import fixture
import reference
import run as cli

TASK = Path(__file__).resolve().parent
WORKTREE = TASK.parents[2]
TASK_PREFIX = TASK.relative_to(WORKTREE).as_posix()
SPDX_TAG = "SPDX" "-License-Identifier:"
SPDX_COPY = "SPDX" "-FileCopyrightText:"
LIC_ID = "Apache" "-2.0"

CONTRACT_KEYS = {
    "SPDX" "-FileCopyrightText", "SPDX" "-License-Identifier", "schema_id", "task",
    "component", "base_commit", "branch", "profile", "status", "qualification",
    "public_surface", "scope", "source_pins", "boundary_pins", "mutable_provenance",
    "artifact_pins", "reproduction", "release_gates",
}
ADAPTER_KEYS = {
    "SPDX" "-FileCopyrightText", "SPDX" "-License-Identifier", "protocol_version",
    "identity", "boundary_identity", "input_kind", "output_kinds", "tasks", "modes",
    "configuration", "entrypoint", "supported_formats", "asset_readiness",
    "registration", "processor_exposure", "real_runtime_used",
    "numeric_parity_with_ffmpeg", "status", "decision",
}
PROVIDER_KEYS = {
    "SPDX" "-FileCopyrightText", "SPDX" "-License-Identifier", "schema_id", "identity",
    "component", "task", "status", "qualification_status", "decision", "registered",
    "default_enabled", "opt_in_required", "processor_exposure",
    "c_abi_or_sdk_default_change", "shared_cmakelists_change",
    "descriptor_registry_change", "installed_v0_behavior_change", "audio_path",
    "boundary", "real_runtime", "wheel_or_licensed_asset", "ffmpeg_binary_available",
    "numeric_ffmpeg_parity_claimed", "note",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key in " + path.name + ": " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail("nonfinite JSON constant in " + path.name + ": " + token)

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, json.JSONDecodeError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        fail("JSON root is not an object: " + path.name)
    check_finite(value, path.name)
    return value


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number at " + where)
    elif isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def check_pins() -> None:
    for name, expected in fixture.SOURCE_PINS.items():
        path = fixture.resolve_pin_path(name)
        if not path.is_file():
            fail("missing pinned source: " + name)
        actual = fixture.sha256_file(path)
        if actual != expected:
            fail("pinned source changed: " + name + " " + actual + " != " + expected)
    print("verify: %d external source pins exact" % len(fixture.SOURCE_PINS))


def check_local_manifest() -> None:
    manifest = cli.read_manifest()
    if "SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for name, expected in manifest.items():
        path = TASK / name
        if not path.is_file():
            fail("missing local artifact: " + name)
        actual = fixture.sha256_file(path)
        if actual != expected:
            fail("local artifact changed: " + name + " " + actual + " != " + expected)
    pinned = set(manifest)
    for path in TASK.rglob("*"):
        if path.is_file() and path.name != "SOURCES.sha256":
            name = path.relative_to(TASK).as_posix()
            if name not in pinned:
                fail("unpinned local artifact: " + name)
    print("verify: %d local artifacts exact" % len(manifest))


def check_contract(contract: dict[str, Any], adapter: dict[str, Any],
                   provider: dict[str, Any]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch")
    if set(adapter) != ADAPTER_KEYS:
        fail("adapter key set mismatch")
    if set(provider) != PROVIDER_KEYS:
        fail("provider key set mismatch")
    if contract["source_pins"] != fixture.SOURCE_PINS:
        fail("contract source pins differ from fixture pins")
    if contract["base_commit"] != reference.BASE_COMMIT or contract["branch"] != reference.BRANCH:
        fail("contract base or branch mismatch")
    if contract["status"] != reference.STATUS:
        fail("contract status mismatch")
    qualification = contract["qualification"]
    if (qualification["status"] != "incomplete" or qualification["decision"] != "DEFER"
            or qualification["qualifies"] is not False
            or qualification["missing_result_promoted"] is not False
            or qualification["processor_exposure"] is not False):
        fail("contract qualification is not incomplete/DEFER")
    surface = contract["public_surface"]
    for key, value in surface.items():
        if value is not False:
            fail("public surface flag is not false: " + key)
    for name, expected in contract["artifact_pins"].items():
        path = TASK / name
        if not path.is_file() or fixture.sha256_file(path) != expected:
            fail("contract artifact pin mismatch: " + name)
    if adapter["decision"] != "DEFER" or adapter["processor_exposure"] is not False \
            or adapter["real_runtime_used"] is not False \
            or adapter["numeric_parity_with_ffmpeg"] is not False:
        fail("adapter disposition mismatch")
    if provider["registered"] is not False or provider["processor_exposure"] is not False \
            or provider["decision"] != "DEFER" \
            or provider["qualification_status"] != "incomplete" \
            or provider["ffmpeg_binary_available"] is not False \
            or provider["numeric_ffmpeg_parity_claimed"] is not False:
        fail("provider disposition mismatch")
    print("verify: contract, adapter and provider record incomplete/DEFER")


def check_report(report: dict[str, Any]) -> None:
    if set(report) != reference.REPORT_KEYS:
        fail("report key set mismatch")
    expected, digest = reference.canonical_report(reference.build_report())
    raw = (TASK / "report.json").read_bytes()
    if raw != expected.encode("utf-8"):
        fail("report.json is not byte-identical after regeneration")
    sidecar = (TASK / "report.json.sha256").read_text(encoding="ascii").strip()
    if sidecar != fixture.sha256_bytes(raw) or sidecar != digest:
        fail("report.json.sha256 does not match report.json")
    repeat = report["repeat_runs"]
    core = dict(report)
    core.pop("repeat_runs")
    core_digest = fixture.sha256_bytes(fixture.canonical_bytes(core))
    if repeat["three_repeats"] != 3 or repeat["byte_identical"] is not True \
            or repeat["canonical_digests"] != [core_digest] * 3:
        fail("report repeat_runs are not three exact repeats")
    if (report["status"] != "proposal_only_not_qualified"
            or report["qualification_status"] != "incomplete"
            or report["decision"] != "DEFER" or report["processor_exposure"] is not False
            or report["public_surface_changed"] is not False
            or report["installed_v0_changed"] is not False
            or report["ffmpeg_available"] is not False
            or report["numeric_ffmpeg_parity_claimed"] is not False
            or report["human_listening_used"] is not False
            or report["target_device_measured"] is not False):
        fail("report disposition mismatch")
    profile = report["acceptance_profile"]
    required = ("identity_noisy_control", "documented_synthetic_baseline", "paired_si_sdr",
                "paired_stoi_style", "clean_speech_preservation", "peaks_checked",
                "invalid_outputs_rejected", "unpaired_predictive_proxy_separately_labeled",
                "alignment_and_state_declared", "unpaced_synthetic_timing_labeled",
                "no_authoritative_ns_baseline_claim", "no_human_listening",
                "no_target_device_measurement")
    if profile["profile"] != "enhancement" or any(profile.get(key) is not True for key in required):
        fail("enhancement profile checklist incomplete")
    if profile["scorer_sha256"] != fixture.sha256_file(TASK / "scorer.py"):
        fail("scorer pin mismatch")
    for name in ("noisy_identity_control", "synthetic_fixed_gain_baseline",
                 "synthetic_afftdn_reference", "clean_speech_preservation"):
        for item in report["items"]:
            score = item["scores"][name]
            if "sisdr_db" not in score or "stoi_style" not in score:
                fail("missing score for " + item["id"] + " " + name)
    if report["unpaired_predictive_proxy"]["label"] != "predictive_proxy_not_quality_not_listening":
        fail("unpaired proxy not labeled")
    print("verify: report canonical, byte-identical, digest " + digest)


def check_cli_repeats() -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    report_bytes = (TASK / "report.json").read_bytes()
    for flag in ("--report", "--sources", "--crosscheck", "--inspect"):
        outputs = []
        for _ in range(3):
            result = subprocess.run([sys.executable, "run.py", flag], cwd=TASK, env=env,
                                    stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if result.returncode != 0:
                fail("run.py " + flag + " failed: " + result.stderr.decode("utf-8", "replace"))
            outputs.append(result.stdout)
        if len(set(outputs)) != 1:
            fail("run.py " + flag + " output differs across three cold starts")
        if flag == "--report" and (TASK / "report.json").read_bytes() != report_bytes:
            fail("--report changed report.json bytes")
    print("verify: 3/3 byte-identical cold-start repeats for all CLI modes")


def check_licensing() -> None:
    literal = "SPDX" + "-License-Identifier"
    for path in sorted(TASK.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines[0].startswith("# " + SPDX_COPY) \
                or lines[1] != "# " + SPDX_TAG + " " + LIC_ID \
                or text.count(SPDX_TAG) != 1:
            fail("SPDX header missing or literal token repeated in string: " + path.name)
        if literal in "\n".join(lines[2:]):
            fail("literal SPDX token found in python file: " + path.name)
    for path in sorted(TASK.glob("*.json")):
        text = path.read_text(encoding="utf-8")
        if literal in text:
            fail("literal SPDX token found in json file: " + path.name)
        if "SPDX\\u002dLicense-Identifier" not in text and (SPDX_TAG[:-1]) not in text:
            # license key must be escaped in JSON
            fail("missing escaped license key in json file: " + path.name)
    readme = (TASK / "README.md").read_text(encoding="utf-8")
    prose = "\n".join(readme.splitlines()[2:])
    if literal in prose:
        fail("literal SPDX token found in README.md prose")
    if "SPDX&#45;License-Identifier" not in readme:
        fail("README missing HTML-escaped license token in prose")
    reuse = (WORKTREE / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or (SPDX_TAG[:-1] + ' = "' + LIC_ID + '"') not in reuse:
        fail("REUSE.toml missing docs/** Apache coverage")
    print("verify: licensing controls ok")


def check_spdx_and_tests() -> None:
    tests = (TASK / "test_reference.py").read_text(encoding="utf-8")
    count = len(re.findall(r"^    def test_", tests, flags=re.MULTILINE))
    if count < 30:
        fail("fewer than 30 reference tests: %d" % count)
    print("verify: %d reference tests" % count)


def check_scope() -> None:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=WORKTREE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                            check=False)
    if result.returncode != 0:
        print("verify: git scope check skipped (not a git worktree)")
        return
    for line in result.stdout.decode("utf-8", "replace").splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path.startswith(TASK_PREFIX + "/"):
            fail("change outside task-local evidence directory: " + path)
    print("verify: working tree changes confined to " + TASK_PREFIX)


def main() -> int:
    check_pins()
    contract = strict_json(TASK / "contract.json")
    adapter = strict_json(TASK / "adapter.json")
    provider = strict_json(TASK / "provider.json")
    strict_json(TASK / "tool-provenance.json")
    report = strict_json(TASK / "report.json")
    check_contract(contract, adapter, provider)
    check_report(report)
    check_local_manifest()
    check_cli_repeats()
    check_licensing()
    check_spdx_and_tests()
    check_scope()
    print("verify: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
