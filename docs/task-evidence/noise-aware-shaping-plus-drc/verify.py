# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for the SDK-NOISE-AWARE-SHAPING-PLUS-DRC package.

Checks exact pins, strict JSON, canonical bytes, three cold-start
regenerations, the report digest sidecar, README digest tables, disposition and
gate status, external-artifact absence, research-module and numpy/scipy
separation, strict rejection examples, SPDX sidecars, task-local scope,
whitespace and test count.  Never writes and never hashes the mutable full
``plan/swarm/TASKS.json``.
"""

from __future__ import annotations

import hashlib
import os
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
COLD_CODE = (
    "import sys; sys.dont_write_bytecode=True; import reference; "
    "sys.stdout.buffer.write(reference.canonical_report_bytes())")
FORBIDDEN_MODULES = ("numpy", "scipy", "audioml_eval")


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
    if any("TASKS.json" in key for key in expected):
        errors.append("mutable_full_board_pinned")
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


def _cold_start_report(errors: List[str]) -> bytes:
    env = os.environ.copy()
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    payloads: List[bytes] = []
    for number in range(3):
        result = subprocess.run(
            [sys.executable, "-c", COLD_CODE],
            cwd=str(HERE), env=env, capture_output=True, check=False)
        if result.returncode != 0:
            errors.append("cold_start_failed:" + str(number) + ":" +
                          result.stderr.decode("utf-8", "replace")[-300:])
            return b""
        payloads.append(result.stdout)
    if any(payload != payloads[0] for payload in payloads[1:]):
        errors.append("cold_start_not_byte_identical")
    return payloads[0]


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
    cold = _cold_start_report(errors)
    if cold and cold != REPORT.read_bytes():
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

    _eq(errors, "report_key_set_mismatch", set(report),
        reference.REQUIRED_REPORT_KEYS)
    _eq(errors, "contract_key_set_mismatch", set(contract),
        reference.REQUIRED_CONTRACT_KEYS)

    _eq(errors, "base_commit_mismatch", report.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "branch_mismatch", report.get("branch"), reference.BRANCH)
    _eq(errors, "profile_not_applied", report.get("profile"),
        reference.PROFILE)
    _eq(errors, "contract_profile_not_applied", contract.get("profile"),
        reference.PROFILE)
    _eq(errors, "report_proposal_only", report.get("proposal_only"), True)
    _eq(errors, "contract_proposal_only", contract.get("proposal_only"), True)
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
    qualification = report.get("qualification", {})
    _eq(errors, "qualification_status_nested",
        qualification.get("status"), reference.QUALIFICATION)
    _eq(errors, "qualification_not_qualified",
        qualification.get("not_qualified"), True)
    _eq(errors, "qualification_readiness",
        qualification.get("readiness"), "incomplete")
    for name in (
            "algorithm_identity_verified",
            "candidate_result_present",
            "energy_equalization_contract_verified",
            "geometry_verified",
            "historical_research_reproduced",
            "listener_outcomes_present",
            "listening_present",
            "local_approximation_is_candidate",
            "masker_cohort_rights_cleared",
            "missing_result_promoted",
            "provider_intake_present",
            "published_control_reproduced",
            "quality_result_present",
            "reference_output_present",
            "release_claim",
            "rights_cleared_cohort_present",
            "runtime_present",
            "source_licensed",
            "source_present",
            "timing_result_present"):
        _eq(errors, "qualification_flag:" + name,
            qualification.get(name), False)
    _eq(errors, "qualification_all_gates_blocked",
        qualification.get("all_release_gates_blocked"), True)
    _eq(errors, "qualification_fixed_dsp_separated",
        qualification.get("fixed_dsp_separated"), True)
    _eq(errors, "contract_qualification_status",
        contract.get("qualification", {}).get("status"),
        reference.QUALIFICATION)
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_rule_absent")
    if not report.get("missing_results"):
        errors.append("missing_results_empty")
    if not report.get("negative_claims"):
        errors.append("negative_claims_empty")

    board = report.get("board_row", {})
    _eq(errors, "board_full_file_hashed",
        board.get("full_tasks_json_hashed"), False)
    _eq(errors, "board_stable_sha256_mismatch", board.get("stable_sha256"),
        reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "board_stable_fields_mismatch", board.get("stable_fields"),
        reference.BOARD_ROW_STABLE_FIELDS)
    _eq(errors, "board_digest_function", reference.board_row_digest(),
        reference.BOARD_ROW_STABLE_SHA256)
    contract_board = contract.get("board_row", {})
    _eq(errors, "contract_board_stable_sha256_mismatch",
        contract_board.get("stable_sha256"),
        reference.BOARD_ROW_STABLE_SHA256)
    _eq(errors, "contract_board_full_file_hashed",
        contract_board.get("full_tasks_json_hashed"), False)

    gates = report.get("gates", [])
    _eq(errors, "gate_count_mismatch", len(gates), 8)
    expected_gates = [gate for gate, _ in reference.GATE_REQUIREMENTS]
    _eq(errors, "gate_order_mismatch", [gate.get("id") for gate in gates],
        expected_gates)
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("gate_not_blocked")
    if any(gate.get("qualifies") is not False for gate in gates):
        errors.append("gate_qualifies")
    contract_gates = contract.get("gates", [])
    _eq(errors, "contract_gate_count_mismatch", len(contract_gates), 8)
    if any(gate.get("status") != "blocked" for gate in contract_gates):
        errors.append("contract_gate_not_blocked")
    _eq(errors, "blocker_count_mismatch", len(report.get("exact_blockers", [])),
        len(reference.EXACT_BLOCKERS))
    _eq(errors, "contract_blocker_count_mismatch",
        len(contract.get("exact_blockers", [])),
        len(reference.EXACT_BLOCKERS))

    _eq(errors, "boundary_mismatch", report.get("boundary"),
        reference.BOUNDARY)
    _eq(errors, "contract_boundary_mismatch", contract.get("boundary"),
        reference.BOUNDARY)
    for name, value in reference.BOUNDARY.items():
        if isinstance(value, bool):
            _eq(errors, "boundary_flag_true:" + name, value, False)
    _eq(errors, "scope_mismatch", report.get("scope"), reference.SCOPE)
    _eq(errors, "contract_scope_mismatch", contract.get("scope"),
        reference.SCOPE)
    _eq(errors, "scope_task_local_only",
        report.get("scope", {}).get("task_local_only"), True)
    for name, value in reference.SCOPE.items():
        if isinstance(value, bool) and name != "task_local_only":
            _eq(errors, "scope_flag_true:" + name, value, False)
    _eq(errors, "caller_asset_contract_mismatch",
        report.get("caller_asset_contract"), reference.CALLER_ASSET_CONTRACT)
    _eq(errors, "contract_caller_asset_mismatch",
        contract.get("caller_asset_contract"),
        reference.CALLER_ASSET_CONTRACT)

    upstream = report.get("upstream", {})
    for key in ("commit", "license", "version", "algorithm_parameters",
                "reference_output", "runtime"):
        _eq(errors, "upstream_not_null:" + key, upstream.get(key), None)
    _eq(errors, "upstream_source_licensed",
        upstream.get("source_licensed"), False)
    _eq(errors, "upstream_research_module_present",
        upstream.get("research_module_present"), True)
    _eq(errors, "upstream_research_module_status",
        upstream.get("research_module_status"),
        reference.UPSTREAM_RESEARCH_MODULE_STATUS)
    _eq(errors, "upstream_published_method_locator",
        upstream.get("published_method_locator"),
        reference.PUBLISHED_METHOD_LOCATOR)
    _eq(errors, "upstream_geometry_status",
        upstream.get("geometry_status"), reference.UPSTREAM_GEOMETRY_STATUS)
    _eq(errors, "contract_upstream_commit",
        contract.get("upstream", {}).get("commit"), None)
    _eq(errors, "contract_upstream_license",
        contract.get("upstream", {}).get("license"), None)

    asset_pins = report.get("asset_pins", {})
    for key in ("asset:source", "asset:license", "asset:runtime",
                "asset:reference_output", "asset:configuration",
                "asset:masker_cohort", "asset:listener_outcomes"):
        pin = asset_pins.get(key, {})
        _eq(errors, "asset_present_flag:" + key, pin.get("present"), False)
        _eq(errors, "asset_loaded_flag:" + key, pin.get("loaded"), False)
        _eq(errors, "asset_executed_flag:" + key, pin.get("executed"), False)
        _eq(errors, "asset_identity_status:" + key,
            pin.get("identity_status"), "not_recorded")
        _eq(errors, "asset_path_status:" + key,
            pin.get("path_status"),
            "candidate_location_not_upstream_verified")
    _eq(errors, "runtime_admitted_flag",
        asset_pins.get("asset:runtime", {}).get("admitted"), False)

    controls = report.get("controls", {})
    for name in ("asset", "config", "frame"):
        _eq(errors, "control_rejected_all:" + name,
            controls.get(name, {}).get("rejected_all"), True)
    _eq(errors, "frame_masker_rejected", controls.get(
        "frame", {}).get("masker_rejected_all"), True)
    _eq(errors, "frame_masker_length_rejected", controls.get(
        "frame", {}).get("masker_length_rejected"), True)
    _eq(errors, "streaming_parity", controls.get(
        "streaming_parity", {}).get("all_identical"), True)
    _eq(errors, "reset_fresh_match", controls.get(
        "reset", {}).get("fresh_matches_reset"), True)
    _eq(errors, "reset_epoch", controls.get(
        "reset", {}).get("higher_epoch_accepted"), True)
    _eq(errors, "reset_zero", controls.get(
        "reset", {}).get("epoch_zero_rejected"), True)
    _eq(errors, "reset_negative", controls.get(
        "reset", {}).get("negative_epoch_rejected"), True)
    _eq(errors, "silence_control", controls.get(
        "silence", {}).get("exact_zero"), True)
    _eq(errors, "nonfinite_rejected", controls.get(
        "nonfinite", {}).get("nonfinite_rejected"), 5)
    _eq(errors, "nonfinite_counted_silence", controls.get(
        "nonfinite", {}).get("counted_as_silence"), False)
    _eq(errors, "nonfinite_counter_changed", controls.get(
        "nonfinite", {}).get("accepted_counter_unchanged"), True)
    _eq(errors, "nonfinite_state_changed", controls.get(
        "nonfinite", {}).get("state_digest_unchanged"), True)
    impulse = controls.get("impulse", {})
    _eq(errors, "impulse_expected_index",
        impulse.get("expected_output_index"),
        impulse.get("observed_peak_index"))
    _eq(errors, "impulse_index", impulse.get("observed_peak_index"),
        2000 + reference.CONTENT_DELAY_SAMPLES)
    _eq(errors, "impulse_delay", impulse.get("declared_delay_samples"),
        reference.CONTENT_DELAY_SAMPLES)
    masker = controls.get("masker_adaptation", {})
    _eq(errors, "masker_adaptation_direction",
        masker.get("adapts_to_masker_band"), True)
    if not isinstance(masker.get("low_minus_high_band_1_db"), (int, float)) or \
            masker.get("low_minus_high_band_1_db", 0.0) <= 0.0:
        errors.append("masker_adaptation_band_1_not_boosted")
    if not isinstance(masker.get("low_minus_high_band_6_db"), (int, float)) or \
            masker.get("low_minus_high_band_6_db", 0.0) >= 0.0:
        errors.append("masker_adaptation_band_6_not_cut")

    fixed = report.get("fixed_dsp_controls", {})
    _eq(errors, "fixed_control_keys", set(fixed),
        {"identity", "static_gain", "fixed_tilt", "noise_aware_shaping",
         "compressor_only"})
    for name, block in fixed.items():
        _eq(errors, "fixed_control_candidate:" + name,
            block.get("candidate_result"), False)
        measurements = block.get("measurements", {})
        _eq(errors, "fixed_control_nonfinite:" + name,
            measurements.get("nonfinite_output_samples"), 0)
        _eq(errors, "fixed_control_silence:" + name,
            measurements.get("silence_exact_zero"), True)
        if not isinstance(measurements.get("max_abs_output"), (int, float)):
            errors.append("fixed_control_max_abs_missing:" + name)
        elif abs(measurements["max_abs_output"]) > 1.0:
            errors.append("fixed_control_max_abs_exceeds_unity:" + name)
        if name in ("identity", "static_gain", "fixed_tilt",
                    "noise_aware_shaping", "compressor_only",
                    "local_approximation"):
            response = measurements.get("band_response", {}).get(
                "band_gain_db", {})
            _eq(errors, "fixed_control_band_response_count:" + name,
                len(response), reference.BAND_COUNT)
    for name in ("fixed_tilt", "noise_aware_shaping"):
        _eq(errors, "shaping_energy_neutral:" + name,
            fixed.get(name, {}).get("measurements", {}).get(
                "energy_neutral"), True)
    _eq(errors, "static_gain_clipping", fixed.get(
        "static_gain", {}).get("measurements", {}).get(
            "clipped_output_samples", 0) > 0, True)

    published = report.get("published_controls_assessment", {})
    for name in ("optfractasii", "research_prototype"):
        block = published.get(name, {})
        _eq(errors, "published_reproduced:" + name,
            block.get("reproduced"), False)
        _eq(errors, "published_source:" + name,
            block.get("source_present"), False)
        _eq(errors, "published_runtime:" + name,
            block.get("runtime_present"), False)
        _eq(errors, "published_result_claim:" + name,
            block.get("result_claim"), False)
    _eq(errors, "research_prototype_causal",
        published.get("research_prototype", {}).get("causal"), False)
    _eq(errors, "research_prototype_sdk_reference",
        published.get("research_prototype", {}).get("sdk_reference"), False)
    separation = published.get("separation", {})
    _eq(errors, "published_pooling", separation.get("pooling_performed"),
        False)
    _eq(errors, "published_controls_reproduced",
        separation.get("published_controls_reproduced"), False)
    _eq(errors, "historical_screen_reproduced",
        separation.get("historical_research_screen_reproduced"), False)
    _eq(errors, "published_local_is_control",
        separation.get("local_approximation_is_published_control"), False)

    screen = report.get("historical_research_screen", {})
    _eq(errors, "historical_screen_reproduced_flag",
        screen.get("reproduced"), False)
    _eq(errors, "historical_screen_independent",
        screen.get("verified_independently"), False)
    _eq(errors, "historical_screen_result_claim",
        screen.get("result_claim"), False)
    _eq(errors, "historical_screen_candidate",
        screen.get("is_candidate_result"), False)
    _eq(errors, "historical_screen_source", screen.get("source_pin"),
        reference.LISTENING_RESEARCH_PATH)
    _eq(errors, "historical_screen_candidates",
        set(screen.get("candidates", {})),
        {"identity", "fixed_tilt", "noise_aware_shaping",
         "noise_aware_shaping_plus_drc", "drc_alone"})

    local = report.get("local_approximation", {})
    _eq(errors, "local_is_research_candidate",
        local.get("is_research_candidate"), False)
    _eq(errors, "local_is_optfractasii", local.get("is_optfractasii"), False)
    _eq(errors, "local_candidate_result", local.get("candidate_result"), False)
    _eq(errors, "local_surrogate_only", local.get("surrogate_only"), True)
    _eq(errors, "local_model_free", local.get("model_free"), True)
    _eq(errors, "local_real_corpus", local.get("uses_real_corpus"), False)
    local_measurements = local.get("measurements", {})
    _eq(errors, "local_nonfinite", local_measurements.get(
        "nonfinite_output_samples"), 0)
    _eq(errors, "local_silence", local_measurements.get(
        "silence_exact_zero"), True)
    if not isinstance(local_measurements.get("max_abs_output"), (int, float)):
        errors.append("local_max_abs_missing")
    elif abs(local_measurements["max_abs_output"]) > 1.0:
        errors.append("local_max_abs_exceeds_unity")

    fixture = report.get("fixture", {})
    _eq(errors, "fixture_spec_digest", fixture.get("spec_digest"),
        reference.FIXTURE_SPEC_DIGEST)
    _eq(errors, "fixture_component_digests",
        fixture.get("component_digests"), reference.FIXTURE_DIGESTS)
    _eq(errors, "fixture_total_samples", fixture.get("total_samples"),
        reference.TOTAL_SAMPLES)
    _eq(errors, "fixture_channels", fixture.get("channels"),
        reference.CHANNELS)
    _eq(errors, "format_geometry", report.get("format"),
        reference._format_block())
    _eq(errors, "format_upstream_verified",
        report.get("format", {}).get("upstream_geometry_verified"), False)

    separation_block = report.get("separation_from_siblings", {})
    _eq(errors, "sibling_pooling", separation_block.get("no_pooling"), True)
    if not separation_block.get("sibling_packages"):
        errors.append("sibling_packages_empty")

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
    _eq(errors, "contract_scenario_id", contract.get("scenario", {}).get("id"),
        "noise-aware-shaping-plus-drc-receiver-side-dsp-blocker-v1")
    _eq(errors, "contract_scenario_geometry",
        contract.get("scenario", {}).get("upstream_geometry_verified"), False)
    _eq(errors, "contract_scenario_masker",
        contract.get("scenario", {}).get("masker_source"),
        "oracle_synthetic")


def check_external_absence(errors: List[str]) -> None:
    for key, path in (
            ("source", reference.SOURCE_PATH),
            ("license", reference.LICENSE_PATH),
            ("runtime", reference.RUNTIME_ENV_PATH),
            ("reference_output", reference.REFERENCE_OUTPUT_PATH),
            ("configuration", reference.CONFIGURATION_PATH),
            ("masker_cohort", reference.MASKER_COHORT_PATH),
            ("listener_outcomes", reference.LISTENER_OUTCOMES_PATH)):
        if reference.resolve_source_path(path).exists():
            errors.append("external_" + key + "_present_but_report_says_absent")
    if reference.UPSTREAM_COMMIT is not None or \
            reference.UPSTREAM_LICENSE is not None or \
            reference.UPSTREAM_PARAMETERS is not None or \
            reference.UPSTREAM_REFERENCE_OUTPUT is not None:
        errors.append("upstream_identity_fabricated")


def check_source_separation(errors: List[str]) -> None:
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        for number, line in enumerate(
                (HERE / name).read_text(encoding="utf-8").splitlines(), 1):
            stripped = line.strip()
            if not stripped.startswith(("import ", "from ")):
                continue
            for module in FORBIDDEN_MODULES:
                if module in stripped:
                    errors.append(
                        f"forbidden_dependency:{name}:{number}:{module}")
    if (HERE / "src").exists() or (HERE / "audioml_eval").exists():
        errors.append("research_module_copied_into_task")


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
    if README.read_text(encoding="utf-8") != \
            reference.update_readme_artifact_table(
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
    if count < 60:
        errors.append("fewer_than_60_reference_tests:" + str(count))
    return count


def main() -> int:
    errors: List[str] = []
    pins = check_pins(errors)
    payloads = check_json(errors)
    if all(payloads.values()):
        check_content(errors, payloads)
    check_external_absence(errors)
    check_source_separation(errors)
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
        f"strict_rejections_ok={strict_count} reproduction_ok=3 "
        f"licensing_ok=1 scope_ok=1 tests={tests} changed_files={changed} "
        f"profile={reference.PROFILE} status={reference.STATUS} "
        f"qualification={reference.QUALIFICATION} decision={reference.DECISION} "
        f"report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
