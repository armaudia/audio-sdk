# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Every check fails closed: missing pins, duplicate keys, nonfinite constants,
extra or unpinned files, noncanonical regeneration, licensing gaps or any
out-of-scope change are hard failures.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = f"docs/task-evidence/{reference.SLUG}/"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"
MANIFEST_COMMENT = cli.MANIFEST_COMMENT.rstrip("\n")

CONTRACT_KEYS = {
    SPDX_C, SPDX_L, "artifact_pins", "base_commit", "boundary", "boundary_pins",
    "branch", "component", "contract_version", "decision", "documented_chain",
    "format", "profile", "public_surface", "qualification", "reproduction",
    "release_gates", "schema_id", "scope", "source_pins", "status", "task",
}
ADAPTER_KEYS = {
    SPDX_C, SPDX_L, "protocol_version", "identity", "boundary_identity",
    "input_kind", "output_kinds", "tasks", "modes", "configuration", "entrypoint",
    "supported_formats", "stage_order", "controls", "ablations", "asset_readiness",
    "registration", "processor_exposure", "real_runtime_used", "listening_result_used",
    "registered", "enabled_by_default", "status", "decision",
}
PROVIDER_KEYS = {
    SPDX_C, SPDX_L, "schema_id", "identity", "component", "task", "status",
    "qualification_status", "decision", "registered", "enabled_by_default",
    "opt_in_required", "processor_exposure", "c_abi_or_sdk_default_change",
    "shared_build_or_ci_change", "descriptor_registry_change",
    "installed_v0_behavior_change", "audio_path", "boundary", "real_runtime",
    "weights_accessed", "note",
}
PIPELINE_KEYS = {
    "stage_order", "scene_chains", "matched_controls", "stage_removed_ablations",
    "documented_comparison_order", "failure_policy", "lifetime", "end_to_end_clock",
    "buffer_behavior", "asset_scope", "paced_workload", "stage_timing_independent",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


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
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        fail("JSON root is not an object: " + path.name)
    check_finite(value, path.name)
    return value


def read_manifest() -> dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  ([^\s]+(?:\s[^\s]+)*)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set[str]:
    local = {f"worktree:{TASK_PREFIX}{name}" for name in reference.LOCAL_FILES}
    return set(reference.SOURCE_PIN_PATHS) | set(reference.BOUNDARY_PIN_PATHS) | local


def check_pins(manifest: dict[str, str]) -> None:
    expected = manifest_expected_paths()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if "SOURCES.sha256" in manifest or "worktree:" + TASK_PREFIX + "SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for raw, digest in sorted(manifest.items()):
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            fail("unsupported pin prefix: " + raw)
        if not path.is_file() or path.is_symlink():
            fail("missing or non-regular pin target: " + raw)
        if reference.sha256_file(path) != digest:
            fail("pin mismatch: " + raw)
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact")


def check_contract(contract: dict[str, Any], adapter: dict[str, Any],
                   provider: dict[str, Any], manifest: dict[str, str]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch")
    if set(adapter) != ADAPTER_KEYS:
        fail("adapter key set mismatch")
    if set(provider) != PROVIDER_KEYS:
        fail("provider key set mismatch")
    source_pins = {key: value for key, value in manifest.items() if key.startswith("source:")}
    boundary_pins = {key: value for key, value in manifest.items()
                     if key in reference.BOUNDARY_PIN_PATHS}
    local_pins = {key.split("/", 1)[1].split("/", 1)[-1].split("/")[-1]: value
                  for key, value in manifest.items()
                  if key.startswith("worktree:" + TASK_PREFIX)
                  and not key.endswith("/contract.json")}
    if contract["source_pins"] != source_pins:
        fail("contract source pins differ from manifest")
    if contract["boundary_pins"] != boundary_pins:
        fail("contract boundary pins differ from manifest")
    if contract["artifact_pins"] != local_pins:
        fail("contract artifact pins differ from manifest")
    if contract["base_commit"] != reference.BASE_COMMIT or contract["branch"] != reference.BRANCH:
        fail("contract base or branch mismatch")
    if contract["task"] != reference.TASK_ID or contract["component"] != reference.SLUG:
        fail("contract task or component mismatch")
    if contract["profile"] != reference.PROFILE or contract["status"] != reference.STATUS:
        fail("contract profile or status mismatch")
    if contract["decision"] != reference.DECISION:
        fail("contract decision is not DEFER")
    qualification = contract["qualification"]
    required = {
        "status": "incomplete", "decision": reference.DECISION, "qualifies": False,
        "missing_result_promoted": False, "processor_exposure": False,
        "real_runtime_used": False, "listening_result_used": False, "release_claim": False,
    }
    if any(qualification.get(key) != value for key, value in required.items()):
        fail("contract qualification is not incomplete/DEFER")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("public surface flag is not false")
    if any(value is not False for key, value in contract["scope"].items() if key.endswith("_claim")
           or key in {"real_runtime", "real_media", "weights_accessed", "device_timing",
                      "listening", "benchmark", "wheel_download"}):
        fail("contract scope has a false claim flag set true")
    if contract["scope"].get("synthetic_only") is not True or contract["scope"].get("task_local_only") is not True:
        fail("contract scope is not synthetic/task-local")
    chain = contract["documented_chain"]
    expected_chain_keys = {
        "owner_preference_date", "stage_order", "scene_chains", "checkpoint_blockers",
        "artifact_identity", "no_live_default",
    }
    if set(chain) != expected_chain_keys:
        fail("documented chain key set mismatch")
    if chain["owner_preference_date"] != "2026-10-31" or chain["no_live_default"] is not True:
        fail("dated prototype choice or no-live-default invariant missing")
    blocker_text = " ".join(chain["checkpoint_blockers"])
    for token in ("SDK-DEEPFILTERNET3-V0-5-6", "remains blocked", "checkpoint",
                  "config", "rights", "no weights accessed"):
        if token not in blocker_text:
            fail("checkpoint/rights blocker missing: " + token)
    artifact = chain["artifact_identity"]
    if artifact["checkpoint_sha256"] != "23b92884f63ccf54bb026014604625ab231657b6480df65db4095c4c171e6003" \
            or artifact["config_sha256"] != "415eb925d44990d938fb739f514aa3662c1ec0ea836cff044fa1291b82cb4290" \
            or artifact["source_revision"] != "978576aa8400552a4ce9730838c635aa30db5e61" \
            or artifact["checkpoint_terms"] != "unclear; see upstream issue #712" \
            or artifact["weights_accessed"] is not False:
        fail("exact checkpoint/config/licensing identity mismatch")
    if adapter["decision"] != reference.DECISION or adapter["status"] != reference.STATUS:
        fail("adapter disposition mismatch")
    for key in ("real_runtime_used", "listening_result_used", "processor_exposure",
                "registered", "enabled_by_default"):
        if adapter.get(key) is not False:
            fail("adapter flag is not false: " + key)
    if provider["decision"] != reference.DECISION or provider["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("provider disposition mismatch")
    for key in ("registered", "enabled_by_default"):
        if provider.get(key) is not False:
            fail("provider registration/default flag is not false: " + key)
    for key in ("processor_exposure", "c_abi_or_sdk_default_change", "shared_build_or_ci_change",
                "descriptor_registry_change", "installed_v0_behavior_change", "real_runtime",
                "weights_accessed"):
        if provider.get(key) is not False:
            fail("provider flag is not false: " + key)
    if provider.get("opt_in_required") is not True:
        fail("provider must require opt-in")
    if not contract["release_gates"] or len(contract["release_gates"]) < 7:
        fail("release gates missing")
    print("verify: contract, adapter, provider disposition and blockers strict")


def check_report(report: dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        fail("report base or branch mismatch")
    if report["status"] != reference.STATUS or report["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("report status mismatch")
    if report["decision"] != reference.DECISION:
        fail("report decision is not DEFER")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("missing-result qualification guard missing")
    for key, value in reference.BOUNDARY.items():
        if report["boundary"].get(key) != value:
            fail("boundary flag mismatch: " + key)
    if report["format"] != reference.FORMAT:
        fail("v0 geometry mismatch")
    if report["profile"] != reference.PROFILE or report["family"] != reference.FAMILY:
        fail("report profile is not pipeline")
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")
    if report["extra"]["live_default"] is not False or report["extra"]["task_board_handoff_written"] is not False:
        fail("live default or board handoff recorded as true")
    if report["extra"]["dated_prototype_choice"] != "2026-11-24-local-only":
        fail("dated prototype choice mismatch")
    if set(report["source_pin_paths"]) != set(reference.SOURCE_PIN_PATHS):
        fail("report source pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("report local file names mismatch")
    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for condition in report["conditions"].values():
        if set(condition["variants"]) != set(reference.STAGE_CHAINS):
            fail("variant set mismatch")
        if not math.isfinite(condition["baseline_metrics"]["mean_abs_error"]):
            fail("nonfinite baseline metric")
    controls = report["controls"]
    if controls["all_present"] is not True or set(controls) < {"identity", "named_baseline", "candidate"}:
        fail("matched controls incomplete")
    for condition, ablation in report["ablations"].items():
        if set(ablation["stage_removed"]) != set(reference.ABLATIONS):
            fail("stage-removed ablation missing in " + condition)
    if not report["regressions"]:
        fail("no regressions were recorded")
    for case in report["adverse"]["config_rejections"].values():
        if not case["status"].startswith("rejected") or case["controller_created"] is not False:
            fail("config case did not fail closed")
    for status in report["adverse"]["frame_rejections"].values():
        if isinstance(status, str) and status.startswith("rejected"):
            continue
        if status is not True:
            fail("frame case did not fail closed")
    for status in report["adverse"]["lifecycle"].values():
        if not status.startswith("rejected"):
            fail("lifecycle case did not fail closed")
    if report["adverse"]["frame_rejections"]["dsp_state_unchanged"] is not True:
        fail("DSP state changed on rejected frame")
    repeat = report["repeatability"]
    if repeat["count"] != 3 or repeat["byte_identical"] is not True or len(set(repeat["digests"])) != 1:
        fail("repeatability is not byte-identical")
    profile = report["pipeline_profile"]
    if set(profile) != PIPELINE_KEYS:
        fail("pipeline profile key set mismatch")
    if profile["stage_order"] != list(reference.STAGE_ORDER):
        fail("pipeline stage order mismatch")
    if set(profile["matched_controls"]) != set(reference.MATCHED_CONTROLS):
        fail("matched controls mismatch")
    if set(profile["stage_removed_ablations"]) != set(reference.ABLATIONS):
        fail("stage-removed ablation set mismatch")
    for key in ("end_to_end_clock", "paced_workload", "stage_timing_independent"):
        if profile[key]["status"] == "blocked_unmeasured" and profile[key]["measured"] is not False:
            fail("timing gate measured flag mismatch: " + key)
    if profile["asset_scope"]["weights_accessed"] is not False or profile["asset_scope"]["vendor_runtime_invoked"] is not False:
        fail("asset scope claims weights or vendor runtime access")
    if not report["gates"] or any(gate["status"] != "blocked" for gate in report["gates"]):
        fail("all gates must remain blocked")
    if b"-0.0" in reference.canonical_report_bytes(report):
        fail("negative zero in canonical report")
    digest_line = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if digest_line != digest + "  report.json":
        fail("report sidecar mismatch")
    print("verify: report fields, controls, ablations, adverse cases and gates strict")


def check_reproduction(digest: str) -> None:
    report_bytes = cli.report_bytes()
    if (HERE / "report.json").read_bytes() != report_bytes:
        fail("report.json is not byte-reproducible")
    if hashlib.sha256(report_bytes).hexdigest() != digest:
        fail("canonical digest mismatch")
    if (HERE / "SOURCES.sha256").read_bytes() != cli.manifest_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    code = ("import hashlib,reference; print(hashlib.sha256("
            "reference.canonical_report_bytes(reference.build_report())).hexdigest())")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical report, sidecar, manifest and three cold starts byte-identical")


def check_licensing(manifest: dict[str, str]) -> None:
    explicit = 0
    annotated = 0
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if not path.is_file() or "__pycache__" in path.parts:
            fail("unexpected file in evidence directory: " + path.name)
        name = path.relative_to(HERE).as_posix()
        if name == "SOURCES.sha256":
            continue
        if name not in reference.LOCAL_FILES:
            fail("file outside fail-closed local set: " + name)
        if path.suffix == ".py":
            head = path.read_text(encoding="utf-8").splitlines()[:3]
            if head[:2] != ["# " + SPDX_C, "# " + SPDX_L] or path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("missing or repeated SPDX header: " + name)
            explicit += 1
        elif path.suffix == ".md":
            head = path.read_text(encoding="utf-8").splitlines()[:3]
            if head[:2] != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
                fail("missing Markdown SPDX header: " + name)
            explicit += 1
        elif name.endswith(".license"):
            if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("invalid license sidecar: " + name)
            annotated += 1
        else:
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("missing or invalid license sidecar: " + name + ".license")
            if "worktree:" + TASK_PREFIX + name + ".license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
            annotated += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 coverage missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    print("verify: write scope limited to task-local evidence")


def main() -> int:
    manifest = read_manifest()
    check_pins(manifest)
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    provider = strict_json(HERE / "provider.json")
    report = strict_json(HERE / "report.json")
    check_contract(contract, adapter, provider, manifest)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    check_reproduction(digest)
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
