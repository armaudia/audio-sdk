# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DTLN-AEC-128-256-512 package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-room profile, a promoted echo/near/overlap result, a
qualified claim, an open release gate, a loaded or executed caller asset, a
fabricated model delay/state shape, license gaps, out-of-scope worktree
changes, whitespace damage or a dirty ``git diff --check``. Never writes.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

import reference  # noqa: E402

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
LOCAL_DIGEST_FILES = (
    "report.json",
    "report.json.sha256",
    "reference.py",
    "run.py",
    "test_reference.py",
    "verify.py",
)
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "evidence_status", "profile", "acceptance_profile", "profile_blockers",
    "candidate", "reference", "format", "fixtures", "echo_attenuation",
    "near_end_preservation", "overlap_double_talk", "no_reference_comparison",
    "alignment", "nonfinite", "movement_path_change", "final_partial",
    "streaming", "reset", "adverse_rejections", "adverse_all_rejected",
    "external_artifacts", "runtime_probe", "licensing", "caller_asset",
    "board_row", "boundary", "boundary_pins", "source_pins", "scope",
    "qualification", "exact_blockers", "release_gates", "reopen_condition",
    "negative_claims", "surrogate", "repeatability", "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile", "candidate",
    "format", "licensing", "artifact_pins", "board_row", "boundary",
    "boundary_pins", "source_pins", "scope", "reference", "exact_blockers",
    "release_gates", "reopen_condition", "negative_claims",
    "caller_asset_contract", "invariants",
}


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.load_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    if not isinstance(payload, dict):
        errors.append("JSON root is not an object: " + label)
        return {}
    return payload


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        expected, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != expected.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if SIDECAR.read_text(encoding="ascii") != digest + "\n":
            errors.append("report.json.sha256 is stale")
    if contract:
        if CONTRACT.read_bytes() != (
                reference.canonical_text(contract) + "\n").encode("utf-8"):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    count = 0
    try:
        lines = PINS.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    for raw in lines:
        if not raw or raw.startswith("#"):
            continue
        count += 1
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, raw_path = parts
        if raw_path.startswith("source:"):
            path = reference.SOURCE_ROOT / raw_path.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw_path
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif reference.file_digest(path) != digest:
            errors.append("pinned bytes changed: " + raw_path)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic generated bytes")
    except (OSError, reference.ReferenceRejection) as error:
        errors.append("pin regeneration failed: " + str(error))
    return count


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    live = reference.board_row()
    _eq(errors, "report board identity is stale", report.get("board_row"), live)
    _eq(errors, "contract board identity is stale", contract.get("board_row"), live)
    row = report.get("board_row", {})
    if row.get("full_tasks_json_hashed") is not False:
        errors.append("full task board is hashed")
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    if stable.get("id") != reference.TASK_ID:
        errors.append("stable board task id mismatch")
    for section in ("source_pins", "boundary_pins"):
        for path in report.get(section, {}):
            if path.endswith("TASKS.json"):
                errors.append("mutable task board is pinned in " + section)


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    missing = REQUIRED_REPORT_KEYS - set(report)
    if missing:
        errors.append("report missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected report schema", report["schema_id"],
        reference.REPORT_SCHEMA)
    _eq(errors, "report status", report["status"], reference.STATUS)
    _eq(errors, "report evidence status", report["evidence_status"],
        "incomplete")
    _eq(errors, "report decision", report["decision"], "DEFER")
    _eq(errors, "report defer point", report["defer_before"],
        "opt_in_adapter_exposure")
    _eq(errors, "report profile", report["profile"], "room")
    _eq(errors, "report task", report["task"], reference.TASK_ID)
    _eq(errors, "report component", report["component"], reference.COMPONENT)
    _eq(errors, "report base commit", report["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report["branch"], reference.BRANCH)

    qualification = report["qualification"]
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    for key in ("qualifies", "all_required_results_present",
                "missing_result_promoted", "exact_source_present",
                "exact_weights_present", "exact_runtime_outputs_present",
                "rights_cleared_cohort", "model_delay_documented",
                "state_shapes_documented", "paired_render_contract_qualified",
                "echo_only_qualified", "near_end_qualified",
                "overlap_qualified", "no_reference_qualified",
                "timing_measured", "listening", "real_corpus_used"):
        if qualification.get(key) is not False:
            errors.append("qualification promotes a missing result: " + key)
    if qualification.get("io_geometry_documented") is not True:
        errors.append("documented I/O geometry is not recorded")

    gates = report["release_gates"]
    if len(gates) != 8:
        errors.append("expected exactly eight release gates")
    if [gate.get("id") for gate in gates] != [
            f"RG-{index:02d}" for index in range(1, 9)]:
        errors.append("release gate IDs are not RG-01..RG-08")
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("a release gate is not blocked")

    profile = report["acceptance_profile"]
    _eq(errors, "room profile not recorded", profile.get("profile"), "room")
    items = profile.get("required_items", {})
    if len(items) != 11:
        errors.append("room profile item set mismatch")
    for name, item in items.items():
        if item.get("status") not in {"synthetic_only", "blocked"}:
            errors.append("room item promoted: " + name)
    expected_blockers = sorted(
        name for name, item in items.items() if item.get("status") == "blocked")
    _eq(errors, "profile blocker list mismatch", report["profile_blockers"],
        expected_blockers)

    candidate = report["candidate"]
    _eq(errors, "candidate rate", candidate.get(
        "reported_input_sample_rate_hz"), 16000)
    _eq(errors, "candidate block", candidate.get("reported_block_samples"), 512)
    _eq(errors, "candidate hop", candidate.get("reported_hop_samples"), 128)
    _eq(errors, "candidate variants", candidate.get("reported_unit_variants"),
        [128, 256, 512])
    if candidate.get("reported_content_delay_samples") is not None:
        errors.append("candidate content delay is fabricated")
    if candidate.get("reported_parameter_count") is not None:
        errors.append("candidate parameter count is fabricated")
    if candidate.get("io_geometry_documented") is not True:
        errors.append("documented I/O geometry is not marked")
    for key in ("model_delay_documented", "state_shapes_documented",
                "source_present", "weights_present", "runtime_present",
                "exact_numeric_output_present"):
        if candidate.get(key) is not False:
            errors.append("candidate claim is not false: " + key)

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    _eq(errors, "candidate block format", fmt.get(
        "candidate_reported_block_samples"), 512)
    _eq(errors, "candidate hop format", fmt.get(
        "candidate_reported_hop_samples"), 128)
    _eq(errors, "surrogate framing delay", fmt.get(
        "surrogate_framing_delay_samples"), 384)
    for key in ("candidate_model_delay_documented",
                "paired_render_in_installed_v0"):
        if fmt.get(key) is not False:
            errors.append("format claim is not false: " + key)

    reference_record = report["reference"]
    for key in ("source_present", "weights_present", "runtime_present",
                "implementation_present", "exact_numeric_output_present",
                "surrogate_is_candidate"):
        if reference_record.get(key) is not False:
            errors.append("reference claim is not false: " + key)
    if reference_record.get("adapter_wrapper_present") is not True:
        errors.append("present adapter wrapper is not recorded")
    if reference_record.get("adapter_wrapper_mock_tested_only") is not True:
        errors.append("adapter wrapper coverage is overstated")
    if reference_record.get("status") != "blocked":
        errors.append("reference status is not blocked")

    if len(report["exact_blockers"]) != 6:
        errors.append("expected six exact blockers")

    attenuation = report["echo_attenuation"]
    regions = attenuation["regions"]
    _eq(errors, "echo region count", len(regions), 2)
    for region in regions:
        if region.get("qualifies") is not False:
            errors.append("echo region is promoted: " + region.get("segment", "?"))
        if region.get("erle_millidb", 0) <= 20000:
            errors.append("echo region ERLE is not positive: "
                          + region.get("segment", "?"))
    _eq(errors, "echo min ERLE", attenuation.get("min_erle_millidb"),
        min(region["erle_millidb"] for region in regions))
    _eq(errors, "echo max ERLE", attenuation.get("max_erle_millidb"),
        max(region["erle_millidb"] for region in regions))

    near = report["near_end_preservation"]
    _eq(errors, "near region count", len(near["regions"]), 2)
    for region in near["regions"]:
        if region.get("qualifies") is not False:
            errors.append("near region is promoted: " + region.get("segment", "?"))
        if region.get("near_reference_snr_millidb", 0) <= 12000:
            errors.append("near-reference SNR is not positive: "
                          + region.get("segment", "?"))
        if abs(region.get("level_change_millidb", 0)) >= 500:
            errors.append("near level change is not small: "
                          + region.get("segment", "?"))
        if region.get("peak_milli", 1000) >= 1000:
            errors.append("near peak is not bounded: "
                          + region.get("segment", "?"))
    _eq(errors, "near min SNR", near.get("min_near_reference_snr_millidb"),
        min(region["near_reference_snr_millidb"]
            for region in near["regions"]))
    _eq(errors, "near nonfinite count", near.get("nonfinite_output_count"), 0)

    overlap = report["overlap_double_talk"]
    if overlap.get("qualifies") is not False:
        errors.append("overlap result is promoted")
    if overlap.get("near_reference_snr_millidb", 0) <= 0:
        errors.append("overlap near-reference SNR is not positive")
    if overlap.get("peak_milli", 1000) >= 1000:
        errors.append("overlap peak is not bounded")

    control = report["no_reference_comparison"]
    if control.get("qualifies") is not False:
        errors.append("no-reference control is promoted")
    if control.get("aec_echo_gain_over_control_millidb", 0) <= 10000:
        errors.append("AEC echo gain over control is not positive")
    if control.get("aec_near_reference_snr_millidb", 0) <= control.get(
            "control_near_reference_snr_millidb", 0):
        errors.append("AEC does not preserve more near-end than the control")

    alignment = report["alignment"]
    if alignment.get("qualifies") is not False:
        errors.append("alignment is promoted")
    if alignment.get("delayed_render_detected") is not True:
        errors.append("delayed render is not detected")
    if alignment.get("missing_render_detected") is not True:
        errors.append("missing render is not detected")
    if alignment.get("missing_render_hop_rejected") is not True:
        errors.append("missing render hop is not rejected before processing")
    if alignment.get("candidate_model_delay_measured") is not False:
        errors.append("candidate model delay is claimed measured")
    _eq(errors, "surrogate framing delay", alignment.get(
        "surrogate_framing_delay_samples"), 384)

    nonfinite = report["nonfinite"]
    _eq(errors, "nonfinite output count", nonfinite.get(
        "output_nonfinite_count"), 0)
    _eq(errors, "output finite", nonfinite.get("output_finite"), True)
    if nonfinite.get("qualifies") is not False:
        errors.append("nonfinite section is promoted")

    movement = report["movement_path_change"]
    _eq(errors, "real movement", movement.get("real_movement"), False)
    if movement.get("qualifies") is not False:
        errors.append("movement result is promoted")

    partial = report["final_partial"]
    _eq(errors, "final partial valid count", partial.get("valid_count"), 100)
    _eq(errors, "final partial output count", partial.get("output_samples"), 128)
    _eq(errors, "final partial advance", partial.get("advanced_samples"), 100)
    _eq(errors, "final partial padding", partial.get("padding_zero"), True)
    _eq(errors, "final partial tail", partial.get("tail_zero"), True)

    streaming = report["streaming"]
    _eq(errors, "streaming match", streaming.get("all_match"), True)
    _eq(errors, "streaming accepted", streaming.get("accepted_samples"), 8192)
    _eq(errors, "streaming output", streaming.get("output_samples"), 8576)
    _eq(errors, "streaming chunk sum", sum(streaming.get("chunks", [])), 8576)
    _eq(errors, "streaming scheduler", streaming.get("scheduler_measured"),
        False)
    if streaming.get("qualifies") is not False:
        errors.append("streaming is promoted")

    reset = report["reset"]
    _eq(errors, "reset freshness", reset.get("matches_fresh"), True)
    _eq(errors, "reset epoch", reset.get("epoch"), 2)

    adverse = report["adverse_rejections"]
    _eq(errors, "adverse rejection count", len(adverse), 57)
    _eq(errors, "adverse rejection flag", report.get("adverse_all_rejected"),
        True)
    for item in adverse:
        if item.get("status") != "rejected" or item.get("state_unchanged") is not True:
            errors.append("adverse case not rejected immutably: "
                          + item.get("case_id", "?"))

    external = report["external_artifacts"]
    _eq(errors, "external artifact status", external.get("status"), "blocked")
    _eq(errors, "external artifact presence", external.get("any_present"),
        False)
    _eq(errors, "generic DTLN accepted as candidate",
        external.get("generic_dtln_is_candidate"), False)
    _eq(errors, "generic DTLN checkout missing",
        external.get("present", {}).get("generic_dtln_checkout"), True)
    _eq(errors, "DTLN-AEC weights reported present",
        external.get("present", {}).get("weights"), False)

    probe = report["runtime_probe"]
    _eq(errors, "runtime probe is stale", probe, reference.runtime_probe())
    if probe.get("tflite_runtime_importable") is not False:
        errors.append("tflite runtime is reported importable")
    if probe.get("tensorflow_importable") is not False:
        errors.append("TensorFlow is reported importable")

    caller = report["caller_asset"]
    _eq(errors, "caller asset contract", caller.get("contract_id"),
        "audio-sdk/dtln-aec-128-256-512/caller-supplied-asset/0.1")
    _eq(errors, "caller variants", caller.get("variants"),
        ["dtln_aec_128", "dtln_aec_256", "dtln_aec_512"])
    _eq(errors, "caller unit variants", caller.get("variant_unit_counts"),
        [128, 256, 512])
    _eq(errors, "caller stage files", caller.get("stage_files_per_variant"), 2)
    _eq(errors, "caller gate", caller.get("probe_gate", {}).get("status"),
        "blocked_asset_absent")
    for key in ("loaded", "executed", "imported"):
        if caller.get(key) is not False:
            errors.append("caller asset claim is not false: " + key)
    if caller.get("status") != "blocked":
        errors.append("caller asset status is not blocked")

    licensing = report["licensing"]
    if licensing.get("reported_upstream_license") is not None:
        errors.append("an upstream license is asserted")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    if licensing.get("generic_dtln_mit_not_accepted") is not True:
        errors.append("generic DTLN MIT license is accepted as DTLN-AEC")
    for key in ("license_text_staged", "attribution_notice_staged",
                "weights_terms_staged", "training_data_statement_staged",
                "redistribution_reviewed", "product_use_reviewed"):
        if licensing.get(key) is not False:
            errors.append("license claim is not false: " + key)

    repeat = report["repeatability"]
    _eq(errors, "repeatability runs", repeat.get("runs"), 3)
    _eq(errors, "repeatability byte identity", repeat.get("byte_identical"),
        True)
    digests = repeat.get("case_matrix_digests", [])
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("case-matrix repeat digests differ")

    boundary = report["boundary"]
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("a boundary flag claims a change")
    scope = report["scope"]
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("scope flag is not false: " + key)

    text = reference.canonical_text(report)
    if '"qualifies":true' in text or '"status":"qualified"' in text:
        errors.append("canonical report contains a qualified claim")
    if "TASKS.json" in reference.canonical_text(report["source_pins"]):
        errors.append("mutable task board appears in source pins")


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    missing = REQUIRED_CONTRACT_KEYS - set(contract)
    if missing:
        errors.append("contract missing sections: " + ", ".join(sorted(missing)))
        return
    _eq(errors, "unexpected contract schema", contract["schema_id"],
        reference.CONTRACT_SCHEMA)
    _eq(errors, "contract task", contract["task"], reference.TASK_ID)
    _eq(errors, "contract component", contract["component"],
        reference.COMPONENT)
    _eq(errors, "contract base commit", contract["base_commit"],
        reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract["branch"], reference.BRANCH)
    _eq(errors, "contract decision", contract["decision"], "DEFER")
    _eq(errors, "contract evidence status", contract["evidence_status"],
        "incomplete")
    _eq(errors, "contract qualification", contract["qualification_status"],
        "not_qualified")
    _eq(errors, "contract verification profile",
        contract["verification_profile"], "room")
    _eq(errors, "contract/report release gates differ",
        contract.get("release_gates"), report.get("release_gates"))
    _eq(errors, "contract/report blockers differ",
        contract.get("exact_blockers"), report.get("exact_blockers"))
    _eq(errors, "contract/report source pins differ",
        contract.get("source_pins"), report.get("source_pins"))
    _eq(errors, "contract/report boundary pins differ",
        contract.get("boundary_pins"), report.get("boundary_pins"))
    _eq(errors, "contract/report candidate differ",
        contract.get("candidate"), report.get("candidate"))
    _eq(errors, "contract/report format differ",
        contract.get("format"), report.get("format"))
    _eq(errors, "contract/report licensing differ",
        contract.get("licensing"), report.get("licensing"))
    _eq(errors, "contract/report caller asset differ",
        contract.get("caller_asset_contract"), report.get("caller_asset"))

    boundary = contract.get("boundary", {})
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("contract boundary flag claims a change")
    scope = contract.get("scope", {})
    if (scope.get("synthetic_only") is not True
            or scope.get("task_local_only") is not True):
        errors.append("contract scope must be synthetic-only and task-local")
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("contract scope flag is not false: " + key)

    pins = contract.get("artifact_pins", {})
    expected_names = {reference.TASK_PREFIX + name
                      for name in reference.ARTIFACT_FILES}
    if set(pins) != expected_names:
        errors.append("artifact pin set mismatch")
    for path, digest in pins.items():
        full = SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact pin missing: " + path)
        elif reference.file_digest(full) != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256"):
        if reference.TASK_PREFIX + forbidden in pins:
            errors.append("self-referential artifact pin: " + forbidden)


def check_repeats(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    texts = []
    for _ in range(3):
        built = reference.build_report()
        text, _ = reference.canonical_report(built)
        texts.append(text)
    if len(set(texts)) != 1:
        errors.append("three fresh report builds differ")
    if texts and texts[0].encode("utf-8") != REPORT.read_bytes():
        errors.append("fresh build does not match report.json")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md is missing its SPDX header")
    for name in LICENSE_SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing license sidecar: " + name)
            continue
        content = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in content or SPDX_COPYRIGHT not in content:
            errors.append("invalid license sidecar: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or (
            'SPDX' '-License-Identifier = "Apache-2.0"') not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def _readme_digest_rows(text: str) -> List[Tuple[str, str]]:
    rows: List[Tuple[str, str]] = []
    for name in LOCAL_DIGEST_FILES:
        match = re.search(r"\| `" + re.escape(name) + r"` \| `([0-9a-f]{64})` \|",
                          text)
        if match:
            rows.append((name, match.group(1)))
    return rows


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "not DTLN-AEC", "room", "paired", "512", "128", "blocked",
                  "tflite_runtime", "not accepted"):
        if token not in text:
            errors.append("README is missing token: " + token)
    for digest in (list(reference.SOURCE_PINS.values())
                   + list(reference.BOUNDARY_PINS.values())):
        if digest not in text:
            errors.append("README is missing pinned digest: " + digest)
    rows = _readme_digest_rows(text)
    if len(rows) != len(LOCAL_DIGEST_FILES):
        errors.append("README local digest table is incomplete")
    for name, digest in rows:
        if reference.file_digest(HERE / name) != digest:
            errors.append("README local digest is stale: " + name)
    if report:
        for token in (reference.BASE_COMMIT, reference.TASK_ID):
            if token not in text:
                errors.append("README is missing identity: " + token)


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: " + diff_check.stdout.strip())
    return changed


def main() -> int:
    errors: List[str] = []
    loaded = check_json_files(errors)
    report = loaded.get("report", {})
    contract = loaded.get("contract", {})
    pin_count = check_pins(errors)
    check_report(errors, report)
    check_contract(errors, contract, report)
    if report and contract:
        check_board(errors, report, contract)
    check_repeats(errors, report)
    check_readme(errors, report)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256="
          f"{reference.file_digest(REPORT)} repeats_ok=3 "
          f"licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
