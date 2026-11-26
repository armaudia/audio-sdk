# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for SDK-CLEARERVOICE-MOSSFORMER2-SE-48K evidence.

Usage::

    SOURCE_ROOT=/Users/htsakanyan/workspace/audio/audioml \
        PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale pins,
stale digests, invalid/missing/nonfinite case acceptance, README table drift,
unpinned files, license gaps, out-of-scope worktree changes, whitespace damage
or a dirty diff check.  Never writes.
"""

from __future__ import annotations

import hashlib
import subprocess
import sys
from pathlib import Path
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
TEXT_SUFFIXES = {".md", ".py", ".json", ".sha256", ".license", ".txt"}

REQUIRED_REPORT_KEYS = {
    "acceptance_profile",
    "asset_pins",
    "base_commit",
    "board_row",
    "boundary",
    "branch",
    "caller_asset_contract",
    "claim",
    "component_id",
    "contract_sha256",
    "controls",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "fixture",
    "format",
    "gates",
    "metrics",
    "missing_results",
    "no_missing_result_qualifies_candidate",
    "negative_claims",
    "profile",
    "proposal_only",
    "qualification",
    "qualification_status",
    "reopen_condition",
    "repository",
    "scenario",
    "schema_id",
    "status",
    "surrogate",
    "task_id",
    "title",
    "upstream",
}

REQUIRED_CONTRACT_KEYS = {
    "acceptance_profile",
    "asset_requirements",
    "base_commit",
    "board_row",
    "boundary",
    "boundary_pins",
    "branch",
    "caller_asset_contract",
    "component_id",
    "decision",
    "defer_before",
    "evidence_status",
    "exact_blockers",
    "format",
    "gates",
    "invariants",
    "local_files",
    "mode",
    "negative_claims",
    "profile",
    "proposal_only",
    "qualification",
    "qualification_status",
    "release_gates",
    "reopen_condition",
    "reproduction",
    "repository",
    "reviewer",
    "scenario",
    "schema_id",
    "scope",
    "source_pins",
    "status",
    "task_id",
    "task_row_identity",
    "title",
    "upstream",
    "worktree",
    "write_scope",
}


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
            try:
                path = reference.resolve_source_path(raw.split(":", 1)[1])
            except ValueError as error:
                errors.append("pin_path:" + raw + ":" + str(error))
                continue
        else:
            prefix = "sdk:" if raw.startswith("sdk:") else ""
            path = SDK_ROOT / (raw.split(":", 1)[1] if prefix else raw)
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
    contract_digest = hashlib.sha256(CONTRACT.read_bytes()).hexdigest()
    regenerated = reference.canonical_report_bytes(
        reference.build_report(contract_sha256=contract_digest)
    )
    second = reference.canonical_report_bytes(
        reference.build_report(contract_sha256=contract_digest)
    )
    third = reference.canonical_report_bytes(
        reference.build_report(contract_sha256=contract_digest)
    )
    if REPORT.read_bytes() != regenerated:
        errors.append("report_not_regenerated_bytes")
    if regenerated != second or second != third:
        errors.append("report_not_cold_start_deterministic")
    report_digest = hashlib.sha256(REPORT.read_bytes()).hexdigest()
    expected_sidecar = f"{report_digest}  report.json\n".encode("ascii")
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != expected_sidecar:
        errors.append("report_digest_sidecar_stale")
    if payloads["report"].get("contract_sha256") != contract_digest:
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
        _eq(errors, "contract_disposition_mismatch:" + key,
            contract.get(key), expected)

    for payload_name, payload in (("report", report), ("contract", contract)):
        _eq(errors, payload_name + "_not_proposal_only",
            payload.get("proposal_only"), True)
        qualification = payload.get("qualification", {})
        _eq(errors, payload_name + "_qualification_status",
            qualification.get("status"), reference.QUALIFICATION)
        _eq(errors, payload_name + "_gate_count",
            qualification.get("release_gate_count"), 8)
        _eq(errors, payload_name + "_all_blocked",
            qualification.get("all_blocked"), True)
        _eq(errors, payload_name + "_release_gate_ids",
            qualification.get("release_gates"), reference.release_gate_ids())

    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if not report.get("missing_results"):
        errors.append("missing_results_empty")
    if not report.get("negative_claims"):
        errors.append("negative_claims_empty")

    board = report.get("board_row", {})
    _eq(errors, "board_full_file_hashed",
        board.get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha256_mismatch",
        board.get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields_mismatch",
        board.get("stable_fields"), reference.BOARD_ROW_STABLE_FIELDS)
    contract_board = contract.get("board_row", {})
    _eq(errors, "contract_board_stable_sha256_mismatch",
        contract_board.get("stable_sha256"),
        reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_full_file_hashed",
        contract_board.get("full_tasks_json_hashed"), False)
    row_identity = contract.get("task_row_identity", {})
    _eq(errors, "task_row_full_file_read",
        row_identity.get("full_tasks_json_read"), False)
    _eq(errors, "task_row_stable_sha256",
        row_identity.get("stable_sha256"), reference.BOARD_ROW_STABLE_SHA256)

    _eq(errors, "contract_sha256_mismatch", report.get("contract_sha256"),
        hashlib.sha256(CONTRACT.read_bytes()).hexdigest())
    _eq(errors, "contract_local_files_mismatch",
        contract.get("local_files"), reference.LOCAL_FILES)
    _eq(errors, "contract_source_pins_mismatch",
        contract.get("source_pins"), reference.SOURCE_PINS)
    _eq(errors, "contract_boundary_pins_mismatch",
        contract.get("boundary_pins"), reference.BOUNDARY_PINS)
    _eq(errors, "contract_reviewer_mismatch", contract.get("reviewer"),
        reference.REVIEWER)
    _eq(errors, "claim_worktree_mismatch",
        report.get("claim", {}).get("worktree"), reference.WORKTREE)
    _eq(errors, "claim_base_mismatch",
        report.get("claim", {}).get("base_commit"), reference.BASE_COMMIT)
    _eq(errors, "contract_worktree_mismatch", contract.get("worktree"),
        reference.WORKTREE)
    _eq(errors, "scope_not_local_only",
        contract.get("scope", {}).get("task_local_only"), True)

    gates = report.get("gates", [])
    _eq(errors, "gate_count_mismatch", len(gates), 8)
    expected_gates = reference.release_gate_ids()
    _eq(errors, "gate_order_mismatch",
        [gate.get("id") for gate in gates], expected_gates)
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("gate_not_blocked")
    contract_gates = contract.get("gates", [])
    _eq(errors, "contract_gate_count_mismatch", len(contract_gates), 8)
    if any(gate.get("status") != "blocked" for gate in contract_gates):
        errors.append("contract_gate_not_blocked")
    release_gates = contract.get("release_gates", [])
    _eq(errors, "contract_release_gate_count", len(release_gates), 8)
    if any(gate.get("status") != "blocked" for gate in release_gates):
        errors.append("contract_release_gate_not_blocked")
    _eq(errors, "blocker_count_mismatch",
        len(report.get("exact_blockers", [])), len(reference.EXACT_BLOCKERS))
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
    _eq(errors, "format_geometry", report.get("format"), reference.FORMAT)
    _eq(errors, "contract_format_geometry", contract.get("format"),
        reference.FORMAT)
    _eq(errors, "scenario_mismatch", report.get("scenario"), reference.SCENARIO)

    upstream = report.get("upstream", {})
    _eq(errors, "upstream_source_revision",
        upstream.get("source_revision"), reference.UPSTREAM_SOURCE_REVISION)
    _eq(errors, "upstream_package", upstream.get("package"),
        reference.UPSTREAM_PACKAGE_IDENTITY)
    _eq(errors, "upstream_model", upstream.get("model_name"),
        reference.MODEL_NAME)
    _eq(errors, "upstream_identity_claimed",
        upstream.get("model_artifact_identity_recorded"), False)

    asset_pins = report.get("asset_pins", {})
    for key, path in (
            ("model_checkpoint", reference.MODEL_PATH),
            ("source_checkout", reference.SOURCE_CHECKOUT_PATH),
            ("runtime_environment", reference.RUNTIME_ENV_PATH)):
        pin = asset_pins.get(key, {})
        _eq(errors, "asset_present_flag:" + key, pin.get("present"), False)
        _eq(errors, "asset_loaded_flag:" + key, pin.get("loaded", False),
            False)
        _eq(errors, "asset_executed_flag:" + key, pin.get("executed", False),
            False)
        _eq(errors, "asset_path:" + key, pin.get("expected_path"), path)
        if (reference.workspace_root() / path).exists():
            errors.append("external_asset_present_but_report_says_absent:" + key)
    _eq(errors, "model_identity_claimed",
        asset_pins.get("model_checkpoint", {}).get("identity_recorded"), False)
    _eq(errors, "model_digest_claimed",
        asset_pins.get("model_checkpoint", {}).get("sha256"), None)

    metrics = report.get("metrics", {})
    _eq(errors, "nonfinite_output_count",
        metrics.get("nonfinite_output_samples"), 0)
    _eq(errors, "clipped_output_count",
        metrics.get("output_peak_clipped_samples"), 0)
    _eq(errors, "silence_not_exact_zero",
        metrics.get("silence_exact_zero"), True)
    _eq(errors, "scored_samples_mismatch",
        metrics.get("scored_samples"), reference.TOTAL_SAMPLES)
    _eq(errors, "metric_scope",
        metrics.get("metric_scope"),
        "synthetic_surrogate_only_not_candidate")
    if not isinstance(metrics.get("max_abs_output"), (int, float)):
        errors.append("max_abs_output_missing")
    elif abs(metrics["max_abs_output"]) > 1.0:
        errors.append("max_abs_output_exceeds_unity")
    for name in ("identity", "surrogate"):
        score = metrics.get(name, {})
        if not isinstance(score.get("si_sdr_db"), (int, float)):
            errors.append(name + "_si_sdr_missing")
        if not isinstance(score.get("snr_db"), (int, float)):
            errors.append(name + "_snr_missing")

    controls = report.get("controls", {})
    for name in ("asset", "config", "chunk"):
        _eq(errors, "control_rejected_all:" + name,
            controls.get(name, {}).get("rejected_all"), True)
    _eq(errors, "streaming_parity",
        controls.get("streaming_parity", {}).get("all_identical"), True)
    _eq(errors, "partial_tail_length",
        controls.get("partial_tail", {}).get("length_preserved"), True)
    _eq(errors, "partial_tail_prefix",
        controls.get("partial_tail", {}).get("chunked_prefix_matches"), True)
    _eq(errors, "reset_fresh_match",
        controls.get("reset", {}).get("fresh_matches_reset"), True)
    _eq(errors, "reset_epoch_rejected",
        controls.get("reset", {}).get("higher_epoch_accepted"), True)
    _eq(errors, "reset_stale_changed",
        controls.get("reset", {}).get("stale_digest_unchanged"), True)
    _eq(errors, "silence_control",
        controls.get("silence", {}).get("exact_zero"), True)
    _eq(errors, "nonfinite_counted_silence",
        controls.get("nonfinite_counter", {}).get("counted_as_silence"), False)
    _eq(errors, "nonfinite_counter_changed",
        controls.get("nonfinite_counter", {}).get(
            "accepted_counter_unchanged"), True)
    _eq(errors, "nonfinite_state_changed",
        controls.get("nonfinite_counter", {}).get("state_digest_unchanged"),
        True)
    _eq(errors, "chunk_state_changed",
        controls.get("chunk", {}).get("state_unchanged"), True)
    candidate = controls.get("asset", {}).get("candidate_admission", {})
    _eq(errors, "candidate_asset_accepted", candidate.get("accepted"), False)
    _eq(errors, "candidate_asset_reason", candidate.get("reason"),
        "asset_model_identity_unrecorded")

    fixture = report.get("fixture", {})
    _eq(errors, "fixture_spec_digest", fixture.get("spec_digest"),
        reference.FIXTURE_SPEC_DIGEST)
    _eq(errors, "fixture_component_digests",
        fixture.get("component_digests"), reference.FIXTURE_DIGESTS)
    _eq(errors, "fixture_total_samples", fixture.get("total_samples"),
        reference.TOTAL_SAMPLES)


def check_readme(errors: List[str]) -> int:
    try:
        text = README.read_text(encoding="utf-8")
        payload = reference.strict_object_loads(
            REPORT.read_text(encoding="utf-8")
        )
        counts = reference.verify_readme_digests(text)
        if text != reference.update_readme_tables(text, payload):
            errors.append("readme_table_stale")
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("readme_table_failed:" + str(error))
        return 0
    expected = reference.expected_readme_keys()
    for name in reference.README_SECTIONS:
        if counts.get(name) != len(expected[name]):
            errors.append("readme_section_count_mismatch:" + name)
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
                    errors.append(
                        f"trailing_whitespace:{path.name}:{number}"
                    )
                    break
    return len(changed)


def check_tests(errors: List[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 35:
        errors.append("fewer_than_35_reference_tests:" + str(count))
    return count


def check_no_forbidden_calls(errors: List[str]) -> None:
    source = (HERE / "reference.py").read_text(encoding="utf-8")
    for token in ("import requests", "import socket", "import torch",
                  "import clearvoice", "urllib.request", "http.client",
                  "subprocess."):
        if token in source:
            errors.append("forbidden_reference_token:" + token)


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    readme_rows = check_readme(errors)
    strict_count = check_strict_rejections(errors)
    check_licensing(errors)
    check_no_forbidden_calls(errors)
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
