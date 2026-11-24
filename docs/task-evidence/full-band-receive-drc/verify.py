# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the task-local receive DRC evidence package.

Rechecks every SHA-256 pin, strict-loads every JSON artifact, regenerates the
canonical report in memory for an exact byte comparison, reruns three cold-start
probes, checks SPDX headers and confirms the git write scope stays inside this
task directory. No file is written and no network, scorer download or real-audio
asset is used.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, List

import fixture
import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
JSON_FILES = ("report.json", "contract.json", "adapter.json", "provider.json")
TASK_PREFIX = "docs/task-evidence/full-band-receive-drc/"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
REUSE_ANNOTATION = '"docs/**"'
REUSE_LICENSE = "SPDX" "-License-Identifier = \"Apache-2.0\""
EXPECTED_GATE_IDS = {
    "authorized_real_listening", "real_speech_paired_cohort", "target_runtime_pacing",
    "provider_intake_and_exposure", "representative_synthetic_control_fidelity",
}


class VerifyError(ValueError):
    """Raised for a malformed artifact or a failed semantic gate."""


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_load(path: Path) -> Dict[str, Any]:
    def reject(value: str) -> None:
        raise VerifyError("non-finite JSON constant " + value)

    def unique_keys(items: Iterable[Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise VerifyError("duplicate JSON key " + str(key))
            result[key] = value
        return result

    payload = json.loads(path.read_text(encoding="utf-8"),
                         parse_constant=reject, object_pairs_hook=unique_keys)
    if not isinstance(payload, dict):
        raise VerifyError("root is not an object")
    return payload


def check_pins(errors: List[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(line))
            continue
        digest, raw_path = parts
        root = SOURCE_ROOT if raw_path.startswith("source:") else SDK_ROOT
        relative = raw_path.split(":", 1)[1] if ":" in raw_path else raw_path
        path = root / relative
        if not path.is_file():
            errors.append("pinned file missing: " + str(path))
        elif sha256(path.read_bytes()) != digest:
            errors.append("pinned bytes changed: " + relative)
    expected_count = (len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS)
                      + len(reference.artifact_pins()) + 3)
    if len(lines) != expected_count:
        errors.append("pin manifest count is not " + str(expected_count))
    return len(lines)


def check_json(errors: List[str]) -> int:
    loaded = 0
    for name in JSON_FILES:
        try:
            strict_load(HERE / name)
            loaded += 1
        except (OSError, ValueError) as error:
            errors.append(f"invalid JSON {name}: {error}")
    try:
        sidecar = SIDECAR.read_text(encoding="ascii").strip()
        if sidecar != sha256(REPORT.read_bytes()):
            errors.append("report.json.sha256 does not match report.json")
    except (OSError, UnicodeError) as error:
        errors.append("invalid report digest sidecar: " + str(error))
    return loaded


def check_semantics(errors: List[str]) -> Dict[str, Any]:
    try:
        report = strict_load(REPORT)
        contract = strict_load(HERE / "contract.json")
        adapter = strict_load(HERE / "adapter.json")
        provider = strict_load(HERE / "provider.json")
    except (OSError, ValueError) as error:
        errors.append("semantic load failed: " + str(error))
        return {}
    if report.get("schema_id") != reference.SCHEMA_ID:
        errors.append("report schema mismatch")
    if report.get("status") != "proposal_only_not_qualified":
        errors.append("report status is not proposal_only_not_qualified")
    if report.get("candidate_status") != "proposal_only_not_qualified":
        errors.append("candidate status is not proposal_only_not_qualified")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification status is not not_qualified")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing-result gate is disabled")
    qualification = report.get("qualification", {})
    if qualification.get("status") != "not_qualified":
        errors.append("qualification section is not not_qualified")
    if qualification.get("readiness") != "incomplete":
        errors.append("readiness is not incomplete")
    if qualification.get("decision") != "DEFER":
        errors.append("no DEFER decision")
    if qualification.get("processor_exposure") != "deferred_until_independent_review":
        errors.append("processor exposure is not deferred")
    if not all(qualification.get("required_results", {}).values()):
        errors.append("a required synthetic result is missing")
    if report.get("fixture_digest") != reference.fixture_digest():
        errors.append("report fixture digest is stale")
    for name, digest in report.get("artifact_pins", {}).items():
        if not (HERE / name).is_file():
            errors.append("pinned artifact missing: " + name)
        elif sha256((HERE / name).read_bytes()) != digest:
            errors.append("report artifact pin changed: " + name)
    if set(report.get("artifact_pins", {})) != set(reference.artifact_pins()):
        errors.append("artifact pin set mismatch")
    gates = report.get("gates", [])
    if {gate.get("id") for gate in gates} != EXPECTED_GATE_IDS:
        errors.append("qualification gate set mismatch")
    if any(gate.get("status") != "blocked" or not gate.get("reopen") for gate in gates):
        errors.append("a qualification gate is open or has no reopening condition")
    if len(report.get("remaining_gates", [])) != len(gates):
        errors.append("remaining gates count mismatch")
    regressions = report.get("regressions", [])
    if len(regressions) != report.get("regression_count"):
        errors.append("regression count mismatch")
    if not regressions or any(not entry.get("excluded_from_qualification")
                              for entry in regressions):
        errors.append("adverse regressions are not excluded from qualification")
    if "clean_speech_rms_loss" not in {entry.get("entry_id") for entry in regressions}:
        errors.append("clean-speech loss regression missing")
    profile = report.get("dsp_profile", {})
    if profile.get("profile") != "dsp":
        errors.append("dsp profile not recorded")
    if set(profile.get("mapped_cases", {})) != {
            "sweeps", "steps", "impulses", "silence", "clean_speech_synthetic",
            "intelligibility_or_load_control"}:
        errors.append("dsp mapped cases incomplete")
    if not {"gain", "frequency_response", "attack_release", "headroom", "delay",
            "numerical_behavior"} <= set(profile.get("measured", [])):
        errors.append("dsp measured metric set incomplete")
    off_on = report.get("off_on_probe", {})
    if not off_on.get("off_is_bit_exact_identity") or not off_on.get("on_differs_from_off"):
        errors.append("opt-in OFF/ON probe failed")
    clamp = report.get("ceiling_clamp_probe", {})
    if "NOT" not in clamp.get("claim", "") or not clamp.get(
            "off_is_bit_exact_below_ceiling"):
        errors.append("above-ceiling identity clamp is not disclosed")
    if not clamp.get("modes", {}).get("identity", {}).get("engine_hard_clip_count", 0):
        errors.append("identity clamp probe did not observe the safety clamp")
    transitions = report.get("alignment_and_state", {}).get("state_transitions", {})
    if not transitions.get("chunked_matches_whole") or not transitions.get(
            "reset", {}).get("replay_matches_original"):
        errors.append("chunking/reset state control failed")
    if not transitions.get("causality_probe", {}).get("prefix_byte_identical") \
            or not transitions.get("causality_probe", {}).get("future_frame_differs"):
        errors.append("causality probe failed")
    control = report.get("near_end_listening_baseline_synthetic_control", {})
    if "SYNTHETIC" not in control.get("claim", "") \
            or control.get("excluded_from_qualification") is not True:
        errors.append("level/masker control is not explicitly synthetic and excluded")
    if len(control.get("conditions", {})) != len(reference.LEVEL_DBFS) * len(reference.TMR_DB):
        errors.append("level/masker sweep conditions incomplete")
    if any(item.get("status") != "measured" for item in control.get(
            "conditions", {}).values()):
        errors.append("a level/masker condition is not measured")
    adverse = report.get("adverse", {})
    if adverse.get("missing_reference", {}).get("status") != "blocked" \
            or adverse.get("missing_reference", {}).get("metrics") is not None:
        errors.append("missing-reference case is not blocked without metrics")
    if any(entry.get("controller_created") for entry in adverse.get(
            "config_rejections", {}).values()):
        errors.append("an invalid configuration created a controller")
    if not adverse.get("frame_rejections", {}).get("dsp_state_unchanged"):
        errors.append("a rejected frame changed DSP state")
    if contract.get("task") != reference.TASK:
        errors.append("contract task mismatch")
    if contract.get("base_commit") != reference.BASE_COMMIT:
        errors.append("contract base commit mismatch")
    if str(contract.get("profile", "")).upper() != "DSP":
        errors.append("contract verification profile mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract source pins mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract boundary pins mismatch")
    boundary = contract.get("boundary", {})
    if (boundary.get("public_c_abi_change") or boundary.get(
            "installed_v0_behavior_change") or boundary.get("registry_change")
            or boundary.get("descriptor_registration") or boundary.get(
            "enabled_by_default") or not boundary.get("opt_in_required")):
        errors.append("contract public-boundary invariant violated")
    if provider.get("registered") is not False or provider.get(
            "enabled_by_default") is not False or provider.get(
            "opt_in_required") is not True:
        errors.append("provider manifest is not opt-in, disabled and unregistered")
    if provider.get("public_abi_change") or provider.get("sdk_default_change") \
            or provider.get("descriptor_registration"):
        errors.append("provider manifest claims a public change")
    if adapter.get("registered") is not False or adapter.get(
            "default_enabled") is not False or adapter.get(
            "real_time_v0_provider") is not False:
        errors.append("adapter manifest is not an unregistered opt-in reference")
    adapter_identity = adapter.get("adapter_id", adapter.get("identity"))
    if adapter.get("protocol_version") != 1 or adapter_identity != reference.ADAPTER_ID:
        errors.append("adapter identity/protocol mismatch")
    statements = " ".join(report.get("source_evidence_statements", []))
    if "context only" not in statements or any(value in statements for value in (
            "0.6873", "0.5752", "+0.0033", "+0.0072")):
        errors.append("source-only predictors leaked into report claims")
    return report


def check_reproduction(errors: List[str]) -> str:
    regenerated = fixture.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    if regenerated != actual:
        errors.append("report.json is not byte-reproducible")
    if not regenerated.endswith(b"\n"):
        errors.append("canonical report has no trailing newline")
    repeats = reference.repeat_probe()
    if not repeats["byte_identical"] or repeats["runs"] != 3:
        errors.append("three cold-start probes are not byte-identical")
    return sha256(actual)


def check_licensing(errors: List[str]) -> int:
    checked = 0
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append("missing SPDX header: " + path.name)
        checked += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if REUSE_ANNOTATION not in reuse or REUSE_LICENSE not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        errors.append("LICENSES/Apache-2.0.txt is missing")
    return checked


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        checked = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                                 capture_output=True, text=True)
        if checked.returncode != 0:
            errors.append("git " + " ".join(arguments) + " failed: "
                          + checked.stdout.strip())
    return changed


def main() -> int:
    errors: List[str] = []
    pin_count = check_pins(errors)
    json_count = check_json(errors)
    check_semantics(errors)
    report_digest = check_reproduction(errors)
    licensing_count = check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok={json_count} reproduction_ok=1 repeats_ok=3 "
          f"licensing_ok={licensing_count} scope_ok=1 "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
