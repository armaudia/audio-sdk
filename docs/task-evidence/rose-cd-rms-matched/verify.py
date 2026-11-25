# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-ROSE-CD-RMS-MATCHED package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, README digest-table
drift, unpinned files, license gaps, out-of-scope worktree changes, whitespace
damage or a dirty diff check.  Never writes.
"""

from __future__ import annotations

import hashlib
import math
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
PINS = HERE / "SOURCES.sha256"
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
README = HERE / "README.md"
SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
REQUIRED_REPORT_KEYS = {
    "acceptance_profile", "asset_pins", "base_commit", "board_row", "boundary",
    "branch", "caller_asset_contract", "claim", "component_id",
    "contract_sha256", "controls", "decision", "defer_before",
    "evidence_status", "exact_blockers", "fixture", "format", "gates",
    "metrics", "missing_results", "no_missing_result_qualifies_candidate",
    "negative_claims", "profile", "qualification_status", "reopen_condition",
    "rms_match", "schema_id", "status", "surrogate", "task_id", "title",
    "upstream",
}
REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile", "base_commit", "board_row", "boundary",
    "boundary_pins", "branch", "caller_asset_contract", "component_id",
    "decision", "defer_before", "evidence_status", "exact_blockers", "format",
    "gates", "invariants", "local_files", "negative_claims", "profile",
    "qualification_status", "reopen_condition", "reviewer",
    "rms_match_contract", "schema_id", "source_pins", "status", "task_id",
    "title", "upstream",
}
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}


def _strict_json(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.strict_loads(path.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + label + ":" + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("json_root_not_object:" + label)
        return {}
    return payload


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def check_pins(errors: List[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    try:
        pins = reference.parse_pin_lines(PINS.read_text(encoding="ascii"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_pin_rejection:" + str(error))
        return 0
    expected = reference.allowed_pin_keys()
    if len(pins) != len(expected):
        errors.append("incomplete_pin_manifest")
    for digest, raw in pins:
        if raw.startswith("source:"):
            path = reference.resolve_source_path(raw.split(":", 1)[1])
        elif raw.startswith("sdk:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append("pin_target_missing:" + raw)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + raw)
    if PINS.read_bytes() != reference.sources_bytes():
        errors.append("SOURCES.sha256_not_deterministic_bytes")
    return len(pins)


def check_json(errors: List[str]) -> Dict[str, Dict[str, Any]]:
    payloads = {
        "contract": _strict_json(CONTRACT, errors, "contract"),
        "report": _strict_json(REPORT, errors, "report"),
    }
    if not all(payloads.values()):
        return payloads
    if CONTRACT.read_bytes() != reference.contract_bytes():
        errors.append("contract_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes(
            payloads["report"]):
        errors.append("report_not_canonical_bytes")
    if REPORT.read_bytes() != reference.canonical_report_bytes():
        errors.append("report_not_regenerated_bytes")
    second = reference.canonical_report_bytes(reference.build_report())
    third = reference.canonical_report_bytes(reference.build_report())
    if REPORT.read_bytes() != second or second != third:
        errors.append("report_not_cold_start_deterministic")
    report_digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != hashlib.sha256(
            CONTRACT.read_bytes()).hexdigest():
        errors.append("report_contract_digest_mismatch")
    for name, payload in payloads.items():
        if reference.has_negative_zero(payload):
            errors.append("negative_zero_in_artifact:" + name)
    return payloads


def check_content(errors: List[str],
                  payloads: Dict[str, Dict[str, Any]]) -> None:
    report = payloads["report"]
    contract = payloads["contract"]

    _eq(errors, "report_key_set_mismatch", set(report), REQUIRED_REPORT_KEYS)
    _eq(errors, "contract_key_set_mismatch", set(contract),
        REQUIRED_CONTRACT_KEYS)

    _eq(errors, "base_commit_mismatch", report.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_not_applied", report.get("profile"),
        reference.PROFILE)
    _eq(errors, "contract_profile_not_applied", contract.get("profile"),
        reference.PROFILE)
    for key, expected in (
            ("task_id", reference.TASK),
            ("title", reference.TITLE),
            ("component_id", reference.COMPONENT),
            ("status", reference.STATUS),
            ("evidence_status", reference.EVIDENCE_STATUS),
            ("qualification_status", reference.QUALIFICATION),
            ("decision", reference.DECISION),
            ("defer_before", reference.DEFER_BEFORE)):
        _eq(errors, "report_disposition_mismatch:" + key,
            report.get(key), expected)
        if key != "component_id":
            _eq(errors, "contract_disposition_mismatch:" + key,
                contract.get(key), expected)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if not report.get("missing_results"):
        errors.append("missing_results_empty")
    if not report.get("negative_claims"):
        errors.append("negative_claims_empty")

    board = report.get("board_row", {})
    _eq(errors, "board_full_file_hashed", board.get("full_tasks_json_hashed"),
        False)
    _eq(errors, "board_stable_sha256_mismatch", board.get("stable_sha256"),
        reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields_mismatch", board.get("stable_fields"),
        reference.BOARD_ROW_STABLE_FIELDS)
    contract_board = contract.get("board_row", {})
    _eq(errors, "contract_board_stable_sha256_mismatch",
        contract_board.get("stable_sha256"),
        reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_full_file_hashed",
        contract_board.get("full_tasks_json_hashed"), False)

    _eq(errors, "contract_sha256_mismatch", report.get("contract_sha256"),
        hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
    _eq(errors, "contract_local_files_mismatch",
        contract.get("local_files"), sorted(reference.LOCAL_FILES))
    _eq(errors, "contract_source_pins_mismatch",
        contract.get("source_pins"), reference.SOURCE_PINS)
    _eq(errors, "contract_boundary_pins_mismatch",
        contract.get("boundary_pins"), reference.BOUNDARY_PINS)
    _eq(errors, "contract_reviewer_mismatch", contract.get("reviewer"),
        reference.REVIEWER)
    _eq(errors, "claim_worktree_mismatch",
        report.get("claim", {}).get("worktree"), reference.CLAIM_WORKTREE)
    _eq(errors, "claim_base_mismatch",
        report.get("claim", {}).get("base_commit"), reference.BASE_COMMIT)

    gates = report.get("gates", [])
    _eq(errors, "gate_count_mismatch", len(gates), 8)
    expected_gates = [gate for gate, _ in reference.GATE_REQUIREMENTS]
    _eq(errors, "gate_order_mismatch", [gate.get("id") for gate in gates],
        expected_gates)
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("gate_not_blocked")
    contract_gates = contract.get("gates", [])
    _eq(errors, "contract_gate_count_mismatch", len(contract_gates), 8)
    if any(gate.get("status") != "blocked" for gate in contract_gates):
        errors.append("contract_gate_not_blocked")
    _eq(errors, "blocker_count_mismatch", len(report.get("exact_blockers", [])),
        len(reference.EXACT_BLOCKERS))
    _eq(errors, "contract_blocker_count_mismatch",
        len(contract.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))

    _eq(errors, "boundary_mismatch", report.get("boundary"),
        reference.BOUNDARY)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"),
        reference.BOUNDARY)
    _eq(errors, "caller_asset_contract_mismatch",
        report.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "contract_caller_asset_mismatch",
        contract.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)

    acceptance = report.get("acceptance_profile", {})
    _eq(errors, "acceptance_profile_name", acceptance.get("name"),
        reference.PROFILE)
    if not acceptance.get("mapped_cases"):
        errors.append("acceptance_mapped_cases_empty")
    if not acceptance.get("not_applicable"):
        errors.append("acceptance_not_applicable_empty")

    rms_match = report.get("rms_match", {})
    if rms_match.get("implicit_peak_clamp") is not False:
        errors.append("rms_match_implicit_clamp")
    if rms_match.get("contract", {}).get("pinned_recipe") is not False:
        errors.append("rms_match_recipe_not_honest")
    if rms_match.get("contract", {}).get("streaming_capable") is not False:
        errors.append("rms_match_claims_streaming")
    _eq(errors, "contract_rms_match_mismatch",
        contract.get("rms_match_contract"), reference.RMS_MATCH_CONTRACT)

    asset_pins = report.get("asset_pins", {})
    checkpoint = asset_pins.get("asset:checkpoint", {})
    _eq(errors, "asset_checkpoint_present", checkpoint.get("present"), False)
    _eq(errors, "asset_checkpoint_loaded", checkpoint.get("loaded"), False)
    _eq(errors, "asset_checkpoint_executed", checkpoint.get("executed"), False)
    _eq(errors, "asset_checkpoint_path", checkpoint.get("expected_path"),
        reference.CHECKPOINT_PATH)
    _eq(errors, "asset_checkpoint_digest", checkpoint.get("sha256"),
        reference.CHECKPOINT_SHA256)
    _eq(errors, "asset_checkpoint_bytes", checkpoint.get("byte_count"),
        reference.CHECKPOINT_BYTES)
    runtime = asset_pins.get("asset:runtime", {})
    _eq(errors, "asset_runtime_present", runtime.get("present"), False)
    _eq(errors, "asset_runtime_admitted", runtime.get("admitted"), False)
    _eq(errors, "asset_runtime_executed", runtime.get("executed"), False)

    metrics = report.get("metrics", {})
    _eq(errors, "raw_nonfinite_count",
        metrics.get("raw_surrogate", {}).get("nonfinite_samples"), 0)
    _eq(errors, "matched_nonfinite_count",
        metrics.get("rms_matched_surrogate", {}).get("nonfinite_samples"), 0)
    _eq(errors, "matched_clipped_count",
        metrics.get("rms_matched_surrogate", {}).get("clipped_samples"), 0)
    _eq(errors, "si_sdr_delta", metrics.get(
        "si_sdr_delta_matched_minus_raw_db"), 0.0)
    _eq(errors, "scored_samples_mismatch", metrics.get("scored_samples"),
        reference.TOTAL_SAMPLES)
    maximum = metrics.get("max_abs_output")
    if not isinstance(maximum, (int, float)):
        errors.append("max_abs_output_missing")
    elif abs(maximum) > 1.0:
        errors.append("max_abs_output_exceeds_unity")

    controls = report.get("controls", {})
    for name in ("asset", "config"):
        _eq(errors, "control_rejected_all:" + name,
            controls.get(name, {}).get("rejected_all"), True)
    shape = controls.get("shape", {})
    _eq(errors, "shape_clip_rejected_all", shape.get("clip_rejected_all"),
        True)
    _eq(errors, "shape_match_rejected_all",
        shape.get("rms_match_rejected_all"), True)
    silence = controls.get("silence", {})
    _eq(errors, "silence_exact_zero", silence.get("exact_zero"), True)
    _eq(errors, "silence_gain_defined", silence.get("gain_defined"), False)
    invariance = controls.get("invariance", {})
    _eq(errors, "invariance_rms", invariance.get(
        "matched_rms_equals_noisy_rms"), True)
    _eq(errors, "invariance_si_sdr", invariance.get("si_sdr_invariant"), True)
    _eq(errors, "invariance_gain", invariance.get(
        "gain_matches_rms_ratio"), True)
    _eq(errors, "invariance_correlation", invariance.get(
        "correlation_matched_raw"), 1.0)
    scale = controls.get("scale_restoration", {})
    _eq(errors, "scale_restored_rms", scale.get(
        "restored_rms_equals_noisy_rms"), True)
    _eq(errors, "scale_si_sdr", scale.get("si_sdr_preserved"), True)
    applied = scale.get("applied_gain_db")
    expected_applied = None
    if isinstance(applied, (int, float)) and isinstance(
            scale.get("attenuation_gain_db"), (int, float)) and isinstance(
            rms_match.get("gain"), (int, float)):
        expected_applied = (-scale["attenuation_gain_db"] +
                            20.0 * math.log10(rms_match["gain"]))
    if expected_applied is None or abs(applied - expected_applied) > 1e-6:
        errors.append("scale_applied_gain")
    scope = controls.get("whole_clip_scope", {})
    _eq(errors, "scope_whole_clip", scope.get("whole_clip_only"), True)
    _eq(errors, "scope_streaming", scope.get("streaming_capable"), False)
    _eq(errors, "scope_prefix", scope.get("prefix_matches_full"), False)
    determinism = controls.get("determinism", {})
    _eq(errors, "determinism_identical", determinism.get("identical"), True)
    _eq(errors, "determinism_runs", determinism.get("runs"), 3)

    fixture = report.get("fixture", {})
    _eq(errors, "fixture_spec_digest", fixture.get("spec_digest"),
        reference.FIXTURE_SPEC_DIGEST)
    _eq(errors, "fixture_component_digests",
        fixture.get("component_digests"), reference.FIXTURE_DIGESTS)
    _eq(errors, "fixture_total_samples", fixture.get("total_samples"),
        reference.TOTAL_SAMPLES)
    _eq(errors, "format_geometry", report.get("format"), reference.FORMAT)
    _eq(errors, "surrogate_is_rose_cd",
        report.get("surrogate", {}).get("is_rose_cd"), False)


def check_external_asset_absence(errors: List[str]) -> None:
    workspace = reference.workspace_root()
    if (workspace / reference.CHECKPOINT_PATH).exists():
        errors.append("external_checkpoint_present_but_report_says_absent")
    if (workspace / reference.RUNTIME_ENV_PATH).exists():
        errors.append("external_environment_present_but_report_says_absent")


def check_readme(errors: List[str]) -> int:
    try:
        counts = reference.verify_readme_digests(
            README.read_text(encoding="utf-8"))
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_digest_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
    if README.read_text(encoding="utf-8") != reference.update_readme_artifact_table(
            README.read_text(encoding="utf-8")):
        errors.append("readme_artifact_table_stale")
    return sum(counts.values())


def check_strict_rejections(errors: List[str]) -> int:
    result = reference.strict_rejection_examples()
    for key, total in (("bad_json", "bad_json_total"),
                       ("bad_pins", "bad_pins_total"),
                       ("bad_readme", "bad_readme_total")):
        if result[key + "_rejected"] != result[total]:
            errors.append("strict_parser_accepted_bad_" + key)
    return (result["bad_json_rejected"] + result["bad_pins_rejected"] +
            result["bad_readme_rejected"])


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    text = README.read_text(encoding="utf-8")
    if f"<!-- {SPDX_COPYRIGHT} -->" not in text or \
            f"<!-- {SPDX_LICENSE} -->" not in text:
        errors.append("missing_markdown_spdx:README.md")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        sidecar = path.read_text(encoding="utf-8") if path.is_file() else ""
        if SPDX_LICENSE not in sidecar or SPDX_COPYRIGHT not in sidecar:
            errors.append("missing_license_sidecar:" + name)
    for path in sorted(HERE.glob("*.json")) + sorted(HERE.glob("*.sha256")):
        if not (HERE / (path.name + ".license")).is_file():
            errors.append("missing_sidecar_for:" + path.name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or \
            'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE_docs_coverage_missing")


def check_scope(errors: List[str]) -> int:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=False)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return 0
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for args in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *args],
                              capture_output=True, text=True, check=False)
        if diff.returncode != 0:
            errors.append("git_" + "_".join(args).replace("-", "") + "_failed")
    expected_files = set(reference.EXPECTED_DIR_FILES)
    actual_files = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual_files != expected_files:
        for name in sorted(actual_files - expected_files):
            errors.append("unpinned_task_file:" + name)
        for name in sorted(expected_files - actual_files):
            errors.append("pinned_task_file_missing:" + name)
    for path in sorted(HERE.iterdir()):
        if path.is_dir():
            errors.append("unexpected_subdirectory:" + path.name)
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode_cache_present")
    for path in sorted(HERE.glob("*")):
        if path.is_file() and path.suffix in TEXT_SUFFIXES:
            data = path.read_bytes()
            if b"\r" in data:
                errors.append("crlf_in_text_file:" + path.name)
            for number, line in enumerate(
                    data.decode("utf-8", "replace").splitlines(), 1):
                if line.rstrip() != line:
                    errors.append(f"trailing_whitespace:{path.name}:{number}")
                    break
    return len(changed)


def check_tests(errors: List[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 40:
        errors.append("fewer_than_40_reference_tests:" + str(count))
    return count


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_external_asset_absence(errors)
    readme_rows = check_readme(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    tests = check_tests(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"pins={pins} json_ok={all(payloads.values())} "
              f"readme_rows={readme_rows} strict_rejections={strict_count} "
              f"report_sha256={digest} failures={len(errors)}")
        return 1
    print(
        f"PASS pins={pins} json_ok=2 readme_rows={readme_rows} "
        f"strict_rejections_ok={strict_count} reproduction_ok=1 "
        f"licensing_ok=1 scope_ok=1 tests={tests} changed_files={changed} "
        f"profile={reference.PROFILE} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} decision={reference.DECISION} "
        f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
