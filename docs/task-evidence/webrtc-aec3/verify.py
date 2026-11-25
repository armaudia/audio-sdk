# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the task-local WebRTC-AEC3 evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Checks exact source pins, strict JSON, local artifact pins, contract and
adapter/provider disposition, three cold-start repeats of every CLI mode,
byte-identical report regeneration, SPDX headers, minimum test count and
write-scope containment.  Missing or changed evidence is a hard failure.
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

CONTRACT_KEYS = {
    "SPDX-FileCopyrightText", "SPDX" + "-License-Identifier", "schema_id", "task",
    "component", "base_commit", "branch", "profile", "status", "qualification_status",
    "decision", "public_surface", "scope", "source_pins", "boundary_pins",
    "mutable_provenance", "artifact_pins", "reproduction", "release_gates",
}
ADAPTER_KEYS = {
    "SPDX-FileCopyrightText", "SPDX" + "-License-Identifier", "protocol_version",
    "identity", "boundary_identity", "input_kind", "output_kinds", "tasks", "modes",
    "configuration", "entrypoint", "supported_formats", "asset_readiness",
    "registration", "processor_exposure", "real_runtime_used", "status", "decision",
}
PROVIDER_KEYS = {
    "SPDX-FileCopyrightText", "SPDX" + "-License-Identifier", "schema_id", "identity",
    "component", "task", "status", "qualification_status", "decision", "registered",
    "default_enabled", "opt_in_required", "processor_exposure",
    "c_abi_or_sdk_default_change", "shared_cmakelists_change",
    "descriptor_registry_change", "installed_v0_behavior_change", "audio_path",
    "boundary", "real_runtime", "wheel_or_licensed_asset", "note",
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
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
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
    if contract["status"] != reference.STATUS or contract["decision"] != reference.DECISION:
        fail("contract status/decision mismatch")
    if (contract["qualification_status"] != "incomplete"
            or adapter["decision"] != "DEFER"
            or provider["decision"] != "DEFER"
            or provider["qualification_status"] != "incomplete"):
        fail("contract/adapter/provider not incomplete/DEFER")
    for key, value in contract["public_surface"].items():
        if value is not False:
            fail("public surface flag is not false: " + key)
    manifest = cli.read_manifest()
    expected_pins = set(manifest) - {"contract.json"}
    if set(contract["artifact_pins"]) != expected_pins:
        fail("contract artifact pins do not cover every local artifact")
    for name, expected in contract["artifact_pins"].items():
        if manifest.get(name) != expected:
            fail("contract artifact pin mismatch: " + name)
    if adapter["processor_exposure"] is not False or adapter["real_runtime_used"] is not False:
        fail("adapter disposition mismatch")
    if provider["registered"] is not False or provider["processor_exposure"] is not False:
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
            or report["decision"] != "DEFER"
            or report["processor_exposure"] is not False
            or report["public_surface_changed"] is not False
            or report["installed_v0_changed"] is not False):
        fail("report disposition is not proposal-only/incomplete/DEFER")
    profile = report["acceptance_profile"]
    required = (
        "frozen_render_or_rir", "channels_rate_hop_frozen",
        "excitation_noise_delay_movement_reset_frozen", "echo_only", "near_end_only",
        "overlap", "no_reference", "alignment", "echo_attenuation", "near_end_damage",
        "nonfinite_failures", "reset", "delayed_render", "missing_render",
        "independent_no_reference_comparison", "chunked_single_digest_identity",
        "no_missing_result_promoted", "synthetic_only",
    )
    if profile["profile"] != "room" or any(profile.get(key) is not True for key in required):
        fail("room profile checklist incomplete")
    if report["sources"]["pins"] != fixture.SOURCE_PINS:
        fail("report source pins differ from frozen pins")
    board = report["sources"]["mutable_board"]
    if (board["path"] != fixture.MUTABLE_BOARD
            or board["sha256_at_read"] != fixture.MUTABLE_BOARD_SHA256_AT_READ
            or board["gate"] is not False):
        fail("mutable board provenance is not frozen and ungated")
    algorithm = report["algorithm"]
    if (algorithm["real_webrtc_source_or_weights"] is not False
            or algorithm["real_webrtc_runtime"] is not False
            or algorithm["real_webrtc_model_or_weights"] is not False
            or "BLOCKED" not in algorithm["provenance_gap"]):
        fail("WebRTC runtime/model provenance gap is not explicit and blocked")
    spec = report["fixture_spec"]
    for key in ("far_end", "near_end", "capture_noise", "microphone",
                "echo_path", "double_talk", "reference_sidechain"):
        if not spec["signal_model"].get(key):
            fail("fixture signal model is incomplete: " + key)
    for key in ("erle_proxy", "near_snr", "alignment", "matched_controls"):
        if not spec["metrics"].get(key):
            fail("scoring model is incomplete: " + key)
    causality = report["causality"]
    if causality["future_frame_reads"] is not False or causality["algorithmic_delay_samples"] != 0:
        fail("causality claim invalid")
    if causality["buffering_delay_samples"] != 0:
        fail("buffering delay is not zero in the synthetic reference")
    chunk = causality["chunk_identity"]
    if len(set(chunk.values())) != 1:
        fail("chunked-vs-single digest identity failed")
    for name, run in report["runs"].items():
        if run["qualifies"] is not False:
            fail("run must not qualify: " + name)
    for name, control in report["controls"].items():
        if control["qualifies"] is not False:
            fail("control must not qualify: " + name)
    adverse = {"no_reference": "blocked_no_reference",
               "delayed_render": "misaligned_reference",
               "reference_dropout": "partial_reference"}
    for name, status in adverse.items():
        if report["runs"][name]["status"] != status:
            fail("adverse status mismatch: " + name)
    failures = report["failures"]
    if failures["alignment_direct_path_tap_samples"] != 12:
        fail("direct-path alignment tap changed")
    if not isinstance(failures["alignment_early_measured_samples"], int):
        fail("measured alignment is missing")
    replay = failures["reset_replay"]
    if (replay["byte_identical"] is not True
            or replay["state_digest_identical"] is not True
            or replay["continued_output_sha256"] != replay["fresh_output_sha256"]
            or replay["continued_state_digest"] != replay["fresh_state_digest"]
            or replay["invalid_reset_rejections"] != [
                "stale_or_invalid_epoch", "invalid_first_sample"]):
        fail("reset/replay determinism or invalid-reset rejection failed")
    adaptive = report["runs"]["echo_only"]["metrics"]["erle_early_db"]
    identity = report["controls"]["identity"]["metrics"]["erle_early_db"]
    fixed = report["controls"]["fixed_attenuation"]["metrics"]["erle_early_db"]
    if not (adaptive > identity + 20.0 and adaptive > fixed + 20.0):
        fail("echo-return-loss proxy did not beat matched synthetic controls")
    overlap = report["runs"]["overlap"]["metrics"]["near_snr_overlap_db"]
    if overlap <= report["controls"]["identity"]["metrics"]["near_snr_overlap_db"]:
        fail("double-talk near-end preservation did not beat identity control")
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


def check_spdx_and_tests() -> None:
    for path in sorted(TASK.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if not lines[0].startswith("# SPDX-FileCopyrightText:") \
                or lines[1] != "# " + SPDX_TAG + " Apache-2.0" \
                or text.count(SPDX_TAG) != 1:
            fail("SPDX header missing or literal token repeated in string: " + path.name)
    for path in sorted(TASK.rglob("*")):
        if not path.is_file():
            continue
        if path.suffix in (".py", ".md", ".json", ".c", ".h", ".in") or path.name == "CMakeLists.txt":
            annotation = path
            sidecar = path.parent / (path.name + ".license")
            if sidecar.exists():
                annotation = sidecar
            if annotation.exists():
                text = annotation.read_text(encoding="utf-8")
                identifier = any(token in text for token in (
                    "SPDX" + "-License-Identifier",
                    "SPDX\\u002dLicense-Identifier",
                    'SPDX" "-License-Identifier',
                ))
                if "SPDX-FileCopyrightText" not in text or not identifier:
                    fail("SPDX annotation missing: " + annotation.name)
    tests = (TASK / "test_reference.py").read_text(encoding="utf-8")
    count = len(re.findall(r"^    def test_", tests, flags=re.MULTILINE))
    if count < 30:
        fail("fewer than 30 reference tests: %d" % count)
    print("verify: SPDX annotations present and %d reference tests" % count)


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
    report = strict_json(TASK / "report.json")
    check_contract(contract, adapter, provider)
    check_report(report)
    check_local_manifest()
    check_cli_repeats()
    check_spdx_and_tests()
    check_scope()
    print("verify: OK")
    return 0


if __name__ == "__main__":
    sys.exit(main())
