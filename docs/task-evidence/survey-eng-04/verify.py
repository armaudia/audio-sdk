# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the ENG-04 task-local evidence map.

Run with the pinned interpreter from this directory. The verifier fails closed
on stale pins, non-canonical or non-finite JSON, duplicate keys, missing or
promoted claims, licensing gaps, unpinned files and any worktree change outside
the task directory. It never rewrites evidence.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List, Tuple

import reference

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
FOLLOWUP = HERE / "followups" / "FEASIBILITY-ENG-04-01.md"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
REQUIRED_REPORT_KEYS = {
    "schema_id", "task_id", "title", "base_commit", "branch", "mode", "status",
    "qualification_status", "no_missing_result_qualifies_candidate", "decision",
    "scope", "boundary", "catalog", "named_source_leads", "method_family_audit",
    "component_matches", "historical_executions", "comparison_inputs", "controls",
    "assets", "local_outcomes", "reported_outcomes", "release_boundary",
    "missing_evidence", "gates", "followups", "source_pins", "boundary_pins",
    "component_evidence_pins", "contract_id", "contract_sha256",
    "tool_provenance", "verification", "evidence_classes", "repeatability",
}
FORBIDDEN_SCOPE_KEYS = {
    "real_audio", "codec_runtime", "codec_weights", "network_capture",
    "device_timing", "listening", "rendered_playback", "public_benchmark",
    "quality_claim", "release_claim", "provider_enablement", "registered_provider",
    "assets_generated",
}
FORBIDDEN_BOUNDARY_KEYS = {
    "registered", "enabled_by_default", "default_selected", "public_api_abi_change",
    "provider_registration", "descriptor_registry_change", "shared_cmakelists_change",
    "shared_ci_change", "build_option_change", "installed_v0_behavior_change",
    "processor_exposure",
}
FAMILY_IDS = {
    "classic.codec_negotiation", "classic.packet_duration", "classic.fec",
    "classic.silence_suppression_comfort_noise",
    "ml.neural_codec_redundancy_variants",
}
CONTROL_IDS = {
    "identity_no_loss", "blind_plc", "redundancy_assisted_fec",
    "silence_cng_transition", "invalid_state_rejection",
}
LEAD_IDS = {"S43", "S44", "S30"}
FORBIDDEN_ASSET_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".m4a", ".ogg", ".opus", ".bin", ".dylib",
    ".so", ".dll", ".a", ".onnx", ".pt", ".pth", ".safetensors", ".tar",
    ".gz", ".zip", ".pcm", ".raw",
}


def _reject_duplicate(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise ValueError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise ValueError("nonfinite_json_constant:" + token)


def strict_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"),
                         object_pairs_hook=_reject_duplicate,
                         parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise ValueError("root_not_object:" + str(path))
    return payload


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    allowed: Dict[str, Any] = {}
    for path, digest in reference.SOURCE_PINS.items():
        allowed["source:" + path] = ("source", path, digest)
    for mapping in (reference.BOUNDARY_PINS, reference.COMPONENT_EVIDENCE_PINS):
        for path, digest in mapping.items():
            allowed[path] = ("sdk", path, digest)
    for name in reference.LOCAL_PIN_PATHS:
        allowed[reference.TASK_PREFIX + name] = ("local", name, "")
    seen = set()
    count = 0
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64 or any(
                char not in "0123456789abcdef" for char in parts[0]):
            errors.append("malformed_pin:" + repr(line))
            continue
        digest, raw = parts
        if raw in seen:
            errors.append("duplicate_pin:" + raw)
            continue
        seen.add(raw)
        entry = allowed.get(raw)
        if entry is None:
            errors.append("unexpected_pin:" + raw)
            continue
        kind, path, expected = entry
        target = (reference.SOURCE_ROOT / path if kind == "source"
                  else SDK_ROOT / (path if kind == "sdk" else raw))
        if expected and expected != digest:
            errors.append("pinned_digest_mismatch:" + raw)
        if not target.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256(target.read_bytes()) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    for raw in sorted(set(allowed) - seen):
        errors.append("pin_absent:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic")
    return count


def check_report(errors: List[str]) -> Dict[str, Any]:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
        entry = reference.catalog_entry()
        backlog = reference.backlog_entry()
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + str(error))
        return {}
    missing = sorted(REQUIRED_REPORT_KEYS - set(report))
    if missing:
        errors.append("report_missing_keys:" + ",".join(missing))
        return report
    if REPORT.read_bytes() != reference.canonical_report_bytes(report):
        errors.append("report_not_canonical_bytes")
    digest = reference.sha256(REPORT.read_bytes())
    expected_sidecar = f"{digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        errors.append("claim_pin_mismatch")
    if report["status"] != reference.STATUS or report["qualification_status"] != reference.QUALIFICATION:
        errors.append("proposal_status_mismatch")
    if report["decision"] != "DEFER" or not report["no_missing_result_qualifies_candidate"]:
        errors.append("missing_DEFER_disposition")
    for key in FORBIDDEN_SCOPE_KEYS:
        if report["scope"].get(key) is not False:
            errors.append("forbidden_scope_claim:" + key)
    for key in FORBIDDEN_BOUNDARY_KEYS:
        if report["boundary"].get(key) is not False:
            errors.append("boundary_claim_not_false:" + key)
        if report["release_boundary"].get(key) is not False:
            errors.append("release_boundary_claim_not_false:" + key)
    if report["boundary"]["descriptor_settings"] != {}:
        errors.append("descriptor_settings_not_empty")
    geometry = report["boundary"]["public_v0_geometry"]
    if (geometry["sample_rate_hz"], geometry["channels"], geometry["sample_format"],
            geometry["frame_samples"], geometry["sdk_callback_invoked"]) != (16000, 1, "f32", 160, False):
        errors.append("public_v0_geometry_changed")
    if report["source_pins"] != reference.SOURCE_PINS:
        errors.append("report_source_pins_mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        errors.append("report_boundary_pins_mismatch")
    if report["component_evidence_pins"] != reference.COMPONENT_EVIDENCE_PINS:
        errors.append("report_component_evidence_pins_mismatch")
    if report["contract_sha256"] != reference.sha256(CONTRACT.read_bytes()):
        errors.append("contract_digest_mismatch")
    if contract.get("task") != reference.TASK:
        errors.append("contract_task_mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract_source_pins_mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract_boundary_pins_mismatch")
    if contract.get("component_evidence_pins") != reference.COMPONENT_EVIDENCE_PINS:
        errors.append("contract_component_evidence_pins_mismatch")
    for key in FORBIDDEN_SCOPE_KEYS:
        if contract.get("scope", {}).get(key) is not False:
            errors.append("contract_forbidden_scope_claim:" + key)
    for key in FORBIDDEN_BOUNDARY_KEYS:
        if contract.get("boundary", {}).get(key) is not False:
            errors.append("contract_boundary_claim_not_false:" + key)

    catalog = report["catalog"]
    expected_catalog = {
        "name": entry["name"], "group": entry["group"], "scope": entry["scope"],
        "output_kind": entry["output_kind"], "purpose": entry["purpose"],
        "method_families": entry["method_families"], "input_output": entry["input_output"],
        "live_or_comparison_boundary": entry["live_or_comparison_boundary"],
        "source_ids": entry["source_ids"], "discovery_status": entry["discovery_status"],
        "candidate_census_status": entry["candidate_census_status"],
        "benchmark_status": entry["benchmark_status"], "backlog_family_id": backlog["family_id"],
        "backlog_state": backlog["state"], "backlog_activation_state": backlog["activation_state"],
        "backlog_next_action": backlog["next_action"],
    }
    for key, value in expected_catalog.items():
        if catalog.get(key) != value:
            errors.append("catalog_mismatch:" + key)

    leads = report["named_source_leads"]
    if {item["id"] for item in leads} != LEAD_IDS:
        errors.append("source_lead_set_mismatch")
    for item in leads:
        if not item.get("component_ids") or not item.get("match_basis"):
            errors.append("source_lead_unmatched:" + item.get("id", "?"))
        if item.get("outcome_class") != "source_reported_not_reproduced":
            errors.append("source_lead_outcome_promoted:" + item.get("id", "?"))
    lines = reference.source_lead_lines()
    for lead_id in sorted(LEAD_IDS):
        if not any(line.startswith(f"| {lead_id} ") for line in lines):
            errors.append("source_lead_missing_in_ledger:" + lead_id)

    audit = report["method_family_audit"]
    if {item["family_id"] for item in audit} != FAMILY_IDS:
        errors.append("family_audit_set_mismatch")
    for item in audit:
        if not item.get("catalog_text") or not item.get("local_outcome") or not item.get("reported_outcome"):
            errors.append("family_audit_incomplete:" + item.get("family_id", "?"))
        if not item.get("missing_evidence"):
            errors.append("family_missing_evidence_absent:" + item.get("family_id", "?"))
    negotiation = next((item for item in audit if item["family_id"] == "classic.codec_negotiation"), {})
    if (negotiation.get("component_ids") or negotiation.get("component_owner") is not None
            or negotiation.get("status") != "missing_component_owner"
            or negotiation.get("followup_id") != reference.FOLLOWUPS[0]["id"]):
        errors.append("unowned_gap_not_recorded")

    component_ids = {item["id"] for item in report["component_matches"]}
    for item in audit:
        if not set(item.get("component_ids", [])) <= component_ids:
            errors.append("family_component_unmatched:" + item["family_id"])
    for item in leads:
        if not set(item.get("component_ids", [])) <= component_ids:
            errors.append("lead_component_unmatched:" + item["id"])
    for item in report["component_matches"]:
        if not item.get("matched_families") or not item.get("basis"):
            errors.append("component_match_incomplete:" + item.get("id", "?"))
        if not set(item["matched_families"]) <= FAMILY_IDS:
            errors.append("component_match_unknown_family:" + item.get("id", "?"))
        if not set(item.get("matched_source_ids", [])) <= LEAD_IDS:
            errors.append("component_match_unknown_source:" + item.get("id", "?"))

    historical = report["historical_executions"]
    if not historical:
        errors.append("historical_executions_absent")
    for item in historical:
        if not item.get("evidence_class") or not item.get("matched_families"):
            errors.append("historical_execution_incomplete:" + item.get("id", "?"))
        if not item.get("match_basis") or "component_ids" not in item:
            errors.append("historical_component_match_incomplete:" + item.get("id", "?"))
        if not set(item.get("component_ids", [])) <= component_ids:
            errors.append("historical_component_unmatched:" + item.get("id", "?"))
        if item.get("local_outcome") and item.get("evidence_class") == "source_reported_not_reproduced":
            errors.append("reported_outcome_promoted_to_local:" + item.get("id", "?"))
        path = item.get("path", "")
        if path in reference.SOURCE_PINS:
            target = reference.SOURCE_ROOT / path
            if not target.is_file() or reference.sha256(target.read_bytes()) != reference.SOURCE_PINS[path]:
                errors.append("historical_source_unpinned_or_stale:" + item.get("id", "?"))
        elif not (SDK_ROOT / path).exists():
            errors.append("historical_path_missing:" + item.get("id", "?"))

    inputs = report["comparison_inputs"]
    if not all(key in inputs for key in ("session_controls", "packet_fields", "erasure_masks",
                                          "not_present_local", "separation_rules")):
        errors.append("comparison_inputs_incomplete")
    if {item["id"] for item in report["controls"]} != CONTROL_IDS:
        errors.append("control_set_mismatch")
    if any(item.get("codec_claim") is not False for item in report["controls"]):
        errors.append("codec_control_claim_promoted")
    assets = report["assets"]
    for key in ("audio_files", "codec_runtime", "model_weights", "captured_network_traces",
                "generated_binary_assets"):
        if assets.get(key) != []:
            errors.append("asset_not_empty:" + key)
    for item in report["reported_outcomes"]:
        if item.get("class") != "source_reported_not_reproduced":
            errors.append("reported_outcome_class_mismatch:" + item.get("id", "?"))

    if len(report["gates"]) != len(reference.GATES) or any(
            gate["status"] != "blocked" or not gate["reopen_condition"]
            for gate in report["gates"]):
        errors.append("release_gates_not_blocked")
    if len(report["followups"]) != 1:
        errors.append("followup_count_mismatch")
    else:
        followup = report["followups"][0]
        if (followup["id"] != "FEASIBILITY-ENG-04-01"
                or followup["component_owner"] is not None
                or followup["implemented"] is not False
                or followup["status"] != "open_bounded_feasibility_followup"):
            errors.append("followup_not_bounded_unowned")
    repeat = report["repeatability"]
    if repeat["count"] != 3 or not repeat["byte_identical"]:
        errors.append("repeatability_not_byte_identical")
    elif reference.repeatability()["digests"] != repeat["digests"]:
        errors.append("cold_start_repeat_mismatch")
    if b"-0.0" in REPORT.read_bytes():
        errors.append("negative_zero_in_report")
    return report


def check_followup(errors: List[str]) -> None:
    if not FOLLOWUP.is_file() or not README.is_file():
        errors.append("followup_or_readme_missing")
        return
    text = FOLLOWUP.read_text(encoding="utf-8")
    readme = README.read_text(encoding="utf-8")
    for marker in ("Not implemented", "unassigned", "Assign a component owner",
                   "No asset, audio, codec runtime"):
        if marker not in text:
            errors.append("followup_marker_missing:" + marker)
    if "FEASIBILITY-ENG-04-01.md" not in readme:
        errors.append("followup_not_linked_from_readme")
    if "classic.codec_negotiation" not in text:
        errors.append("followup_not_linked_to_family")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.rglob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + str(path.relative_to(HERE)))
    for name in ("SOURCES.sha256.license", "contract.json.license",
                 "report.json.license", "report.json.sha256.license"):
        text = (HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml_docs_coverage_missing")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(reference.TASK_PREFIX):
                errors.append("out_of_scope_change:" + path)
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True)
    if diff.returncode != 0:
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    pinned = {reference.TASK_PREFIX + name for name in reference.LOCAL_PIN_PATHS}
    pinned.add(reference.TASK_PREFIX + "SOURCES.sha256")
    for path in sorted(HERE.rglob("*")):
        if not path.is_file() or "__pycache__" in path.parts:
            continue
        relative = reference.TASK_PREFIX + str(path.relative_to(HERE))
        if relative not in pinned:
            errors.append("unpinned_task_file:" + str(path.relative_to(HERE)))
        if path.suffix.lower() in FORBIDDEN_ASSET_SUFFIXES:
            errors.append("forbidden_asset:" + str(path.relative_to(HERE)))
    return changed


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    report = check_report(errors)
    check_followup(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digest = reference.sha256(REPORT.read_bytes()) if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins_ok={pins == (len(reference.SOURCE_PINS) + len(reference.BOUNDARY_PINS) + len(reference.COMPONENT_EVIDENCE_PINS) + len(reference.LOCAL_PIN_PATHS)) and not any(e.startswith(('malformed_pin', 'duplicate_pin', 'unexpected_pin', 'pin_', 'pinned_', 'SOURCES')) for e in errors)} "
              f"json_ok={bool(report)} reproduction_ok={not any('canonical' in e or 'sidecar' in e or 'repeat' in e for e in errors)} "
              f"report_sha256={digest} changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} files={len(changed)} status={report['status']} "
          f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
