# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-DUAL-PATH-ECHO-NET package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-room profile, a promoted metric, a resolved or substituted
family identity, a fabricated geometry, a qualified claim, an open release
gate, license gaps, out-of-scope branch or worktree changes, whitespace damage
or a dirty ``git diff --check``. Never writes.
"""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

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
REQUIRED_REPORT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "status", "decision", "defer_before",
    "evidence_status", "profile", "acceptance_profile", "profile_blockers",
    "candidate_identity", "reference_status", "format", "room_harness",
    "baseline", "listening", "runtime_timing", "state_and_memory", "nonfinite",
    "admission_control", "adverse_rejections", "adverse_all_rejected",
    "external_artifacts", "licensing", "provenance", "caller_asset",
    "board_row", "boundary", "boundary_pins", "source_pins", "scope",
    "qualification", "exact_blockers", "required_artifacts", "release_gates",
    "reopen_condition", "negative_claims", "surrogate", "repeatability",
    "scope_note",
}
REQUIRED_CONTRACT_KEYS = {
    "schema_id", "task", "title", "component", "repository", "version",
    "base_commit", "branch", "reviewer", "status", "decision", "defer_before",
    "evidence_status", "qualification_status", "profile",
    "verification_profile", "task_prefix", "acceptance_profile",
    "candidate_identity", "reference_status", "format", "licensing",
    "artifact_pins", "board_row", "boundary", "boundary_pins", "source_pins",
    "scope", "exact_blockers", "required_artifacts", "release_gates",
    "reopen_condition", "negative_claims", "admission_schema", "invariants",
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


def _false(errors: List[str], section: Dict[str, Any], keys: List[str],
           label: str) -> None:
    for key in keys:
        if section.get(key) is not False:
            errors.append(label + " claims true: " + key)


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
    _eq(errors, "contract board identity is stale", contract.get("board_row"),
        live)
    row = report.get("board_row", {})
    if row.get("full_tasks_json_hashed") is not False:
        errors.append("full task board is hashed")
    if row.get("linked_row_identity_only") is not True:
        errors.append("linked-row identity mode is not declared")
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    if reference.object_digest(row.get("linked_rows", [])) != row.get(
            "linked_rows_sha256"):
        errors.append("linked row hash mismatch")
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
    _false(errors, qualification, [
        "qualifies", "all_required_results_present", "missing_result_promoted",
        "canonical_identity_resolved", "exact_source_present",
        "exact_weights_present", "exact_runtime_outputs_present",
        "checkpoint_identity_verified", "rights_cleared_room_cohort",
        "geometry_and_delay_documented", "echo_attenuation_qualified",
        "near_end_damage_qualified", "alignment_qualified",
        "double_talk_qualified", "no_reference_comparison",
        "baseline_qualified", "nonfinite_output_qualified", "timing_measured",
        "memory_measured", "listening", "real_corpus_used"], "qualification")

    gates = report["release_gates"]
    if len(gates) != 8:
        errors.append("expected exactly eight release gates")
    if [gate.get("id") for gate in gates] != [
            f"RG-{index:02d}" for index in range(1, 9)]:
        errors.append("release gate IDs are not RG-01..RG-08")
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("a release gate is not blocked")

    artifacts = report["required_artifacts"]
    if [row.get("id") for row in artifacts] != [
            f"ART-{index:02d}" for index in range(1, 8)]:
        errors.append("required artifact IDs are not ART-01..ART-07")
    if artifacts and (
            artifacts[0].get("present") is not True
            or artifacts[0].get("verified") is not True
            or artifacts[0].get("blocked") is not False):
        errors.append("ART-01 provenance is not verified")
    for row in artifacts[1:]:
        if row.get("present") is not False:
            errors.append("missing artifact is claimed present: "
                          + str(row.get("id")))
        if row.get("blocked") is not True:
            errors.append("missing artifact is not blocked: "
                          + str(row.get("id")))

    profile = report["acceptance_profile"]
    _eq(errors, "room profile not recorded", profile.get("profile"), "room")
    items = profile.get("required_items", {})
    if set(items) != set(reference._acceptance_profile()["required_items"]):
        errors.append("room profile item set mismatch")
    for name, item in items.items():
        if item.get("status") not in {"synthetic_only", "blocked"}:
            errors.append("profile item promoted: " + name)
    expected_blockers = sorted(
        name for name, item in items.items() if item.get("status") == "blocked")
    _eq(errors, "profile blocker list mismatch", report["profile_blockers"],
        expected_blockers)
    for name in ("echo_attenuation", "near_end_damage",
                 "rights_cleared_room_qualification",
                 "no_reference_suppressor_comparison",
                 "device_timing_resources"):
        if items.get(name, {}).get("status") != "blocked":
            errors.append("required room item is not blocked: " + name)

    identity = report["candidate_identity"]
    _eq(errors, "identity status", identity.get("status"),
        "family_unresolved")
    _eq(errors, "identity resolved", identity.get("identity_resolved"), False)
    _eq(errors, "identity match count",
        identity.get("exact_canonical_match_count"), 0)
    for key in ("canonical_citation", "canonical_doi", "canonical_arxiv_id",
                "canonical_repository", "canonical_checkpoint_id",
                "canonical_paper_title"):
        if identity.get(key) is not None:
            errors.append("canonical identity is fabricated: " + key)
    probes = identity.get("substitution_probes", [])
    if not probes:
        errors.append("no substitution probes recorded")
    for row in probes:
        if row.get("status") != "rejected":
            errors.append("substitution probe not rejected: "
                          + repr(row.get("input")))
        if row.get("observed_code") != row.get("expected_code"):
            errors.append("substitution probe code mismatch: "
                          + repr(row.get("input")))
        if row.get("substitution_accepted") is not False:
            errors.append("substitution was accepted: "
                          + repr(row.get("input")))
    _eq(errors, "substitution rejection count",
        identity.get("substitution_probes_rejected"),
        identity.get("substitution_probes_total"))
    _eq(errors, "all substitutions rejected flag",
        identity.get("all_substitutions_rejected"), True)
    related = identity.get("related_but_distinct", [])
    if len(related) != 4:
        errors.append("expected four related-but-distinct papers")
    for row in related:
        if row.get("substitutable") is not False:
            errors.append("related paper marked substitutable: "
                          + str(row.get("name")))

    status = report["reference_status"]
    _eq(errors, "reference status", status.get("status"), "blocked")
    _false(errors, status, [
        "source_present", "weights_present", "runtime_present",
        "implementation_present", "adapter_present",
        "exact_numeric_output_present", "checkpoint_identity_verified",
        "surrogate_is_candidate"], "reference_status")
    for key in ("license_identity", "pinned_revision"):
        if status.get(key) is not None:
            errors.append("reference identity is fabricated: " + key)

    fmt = report["format"]
    _eq(errors, "sdk rate", fmt.get("sdk_v0_sample_rate_hz"), 16000)
    _eq(errors, "sdk channels", fmt.get("sdk_v0_channels"), 1)
    _eq(errors, "sdk frame", fmt.get("sdk_v0_frame_samples"), 160)
    _eq(errors, "sdk format", fmt.get("sdk_v0_sample_format"), "float32")
    _eq(errors, "resampling", fmt.get("resampling"), "none")
    for key in ("candidate_reported_sample_rate_hz",
                "candidate_reported_hop_samples",
                "candidate_reported_channels",
                "candidate_reported_lookahead_samples"):
        if fmt.get(key) is not None:
            errors.append("candidate geometry is fabricated: " + key)
    _false(errors, fmt, ["candidate_geometry_documented",
                         "model_asset_in_installed_v0"], "format")

    room = report["room_harness"]
    if room.get("synthetic_only") is not True:
        errors.append("room harness is not declared synthetic")
    if room.get("audio_generated") is not False:
        errors.append("room harness claims generated audio")
    if room.get("qualifies") is not False:
        errors.append("room harness is promoted")
    cases = {case["name"]: case for case in room.get("cases", [])}
    if set(cases) != {"echo_only", "near_end_only", "double_talk"}:
        errors.append("room case set mismatch")
    else:
        for case in cases.values():
            if case.get("qualifies") is not False:
                errors.append("room case is promoted: " + case["name"])
            if case.get("scope") != "synthetic_arithmetic_oracle":
                errors.append("room case scope mismatch: " + case["name"])
        if cases["echo_only"].get(
                "echo_return_loss_enhancement_millidb") != 20709:
            errors.append("echo-only oracle ERLE arithmetic drift")
        if cases["echo_only"].get("near_end_snr_millidb") is not None:
            errors.append("echo-only case fabricates a near-end SNR")
        if cases["near_end_only"].get("near_end_snr_millidb") != 23687:
            errors.append("near-end-only oracle SNR arithmetic drift")
        if cases["near_end_only"].get(
                "echo_return_loss_enhancement_millidb") is not None:
            errors.append("near-end-only case fabricates an ERLE")
        if cases["double_talk"].get("near_end_snr_millidb") != 23868:
            errors.append("double-talk oracle SNR arithmetic drift")
        if cases["double_talk"].get(
                "echo_return_loss_enhancement_millidb") is not None:
            errors.append("double-talk case fabricates a far-end ERLE")

    paths = room.get("path_components", {})
    _eq(errors, "primary path delay", paths.get("primary", {}).get(
        "delay_samples"), 240)
    _eq(errors, "secondary path delay", paths.get("secondary", {}).get(
        "delay_samples"), 560)
    _eq(errors, "primary path taps", paths.get("primary", {}).get(
        "tap_count"), 3)
    _eq(errors, "secondary path taps", paths.get("secondary", {}).get(
        "tap_count"), 2)

    delay = room.get("delay_estimation", {})
    _eq(errors, "nominal delay lag", delay.get("nominal", {}).get(
        "lag_samples"), 240)
    _eq(errors, "delayed render lag", delay.get("delayed_render", {}).get(
        "lag_samples"), 720)
    quiet = delay.get("missing_render", {})
    _eq(errors, "missing render status", quiet.get("status"), "not_estimable")
    _eq(errors, "missing render code", quiet.get("observed_code"),
        "no_render_reference")
    if quiet.get("lag_samples") is not None:
        errors.append("missing render fabricates a lag")
    geometry = room.get("geometry", {})
    _eq(errors, "room rate", geometry.get("sample_rate_hz"), 16000)
    _eq(errors, "room channels", geometry.get("channels"), 1)
    _eq(errors, "room frame", geometry.get("frame_samples"), 160)
    _eq(errors, "room path count", geometry.get("path_count"), 2)
    _eq(errors, "room primary delay",
        geometry.get("primary_path_delay_samples"), 240)
    _eq(errors, "room secondary delay",
        geometry.get("secondary_path_delay_samples"), 560)
    _eq(errors, "room response kind", geometry.get("room_impulse_response"),
        "synthetic_fixed_not_measured")
    _false(errors, geometry, ["movement_modeled", "recorded_audio"], "geometry")

    control = report["admission_control"]
    _eq(errors, "admission control admitted", control.get("admitted"), True)
    _eq(errors, "admission control qualifies", control.get("qualifies"), False)
    _false(errors, control, ["loaded", "executed", "audio_read",
                             "is_real_cohort"], "admission_control")
    _eq(errors, "admission control placeholder",
        control.get("placeholder_values"), True)

    adverse = report["adverse_rejections"]
    expected_cases = reference.adverse_rejections()
    _eq(errors, "adverse rejection count", len(adverse), len(expected_cases))
    _eq(errors, "adverse rejection flag", report.get("adverse_all_rejected"),
        True)
    for item in adverse:
        if item.get("status") != "rejected":
            errors.append("adverse case not rejected exactly: "
                          + item.get("case_id", "?"))
        if item.get("expected_code") != item.get("observed_code"):
            errors.append("adverse code mismatch: " + item.get("case_id", "?"))
        if item.get("state_unchanged") is not True:
            errors.append("adverse case changed state: "
                          + item.get("case_id", "?"))

    external = report["external_artifacts"]
    _eq(errors, "external artifact status", external.get("status"), "blocked")
    _eq(errors, "external artifact presence", external.get("any_present"),
        False)
    _eq(errors, "external artifact count", external.get("present_count"), 0)

    licensing = report["licensing"]
    if licensing.get("reported_upstream_license") is not None:
        errors.append("an upstream license is asserted")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    _false(errors, licensing, [
        "license_text_staged", "attribution_notice_staged",
        "weights_terms_staged", "training_data_statement_staged",
        "redistribution_reviewed", "product_use_reviewed",
        "output_use_reviewed"], "licensing")

    provenance = report["provenance"]
    if provenance.get("all_present") is not True:
        errors.append("a provenance phrase is missing")
    if provenance.get("is_qualification") is not False:
        errors.append("provenance is promoted to qualification")

    nonfinite = report["nonfinite"]
    if nonfinite.get("rejected_nonfinite_inputs", 0) < 2:
        errors.append("nonfinite input rejection count too low")
    if nonfinite.get("candidate_output_nonfinite_count") is not None:
        errors.append("candidate nonfinite output is fabricated")
    _eq(errors, "candidate output finite flag",
        nonfinite.get("candidate_output_finite"), False)

    baseline = report["baseline"]
    _eq(errors, "baseline status", baseline.get("status"), "blocked")
    if baseline.get("baseline_id") is not None:
        errors.append("baseline is fabricated")

    listening = report["listening"]
    _eq(errors, "listening status", listening.get("status"), "not_run")
    _false(errors, listening, ["authorized"], "listening")
    if listening.get("result") is not None:
        errors.append("listening result is fabricated")

    timing = report["runtime_timing"]
    _eq(errors, "timing status", timing.get("status"), "blocked_unmeasured")
    _false(errors, timing, ["availability_modeled", "wall_clock_measured",
                            "resource_measurement"], "runtime_timing")
    for key in ("real_time_factor", "deadline_ns", "content_delay_samples"):
        if timing.get(key) is not None:
            errors.append("timing value is fabricated: " + key)

    state = report["state_and_memory"]
    _eq(errors, "state status", state.get("status"),
        "synthetic_pure_function_only")
    _false(errors, state, ["memory_measured"], "state_and_memory")
    if state.get("candidate_state_bytes") is not None:
        errors.append("candidate state size is fabricated")

    surrogate = report["surrogate"]
    _false(errors, surrogate, [
        "is_candidate", "is_learned", "is_dual_path_network",
        "is_echo_canceller", "uses_network", "uses_weight_file",
        "uses_float_arithmetic_in_signal_path",
        "qualifies_candidate"], "surrogate")

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
    _eq(errors, "contract/report identity differ",
        contract.get("candidate_identity"), report.get("candidate_identity"))
    _eq(errors, "contract/report format differ",
        contract.get("format"), report.get("format"))
    _eq(errors, "contract/report licensing differ",
        contract.get("licensing"), report.get("licensing"))
    _eq(errors, "admission schema qualifies", contract.get(
        "admission_schema", {}).get("qualifies"), False)

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
    cold = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        capture_output=True, text=True)
    if cold.returncode != 0:
        errors.append("cold-start run.py --check failed: "
                      + (cold.stderr.strip() or cold.stdout.strip()))


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md is missing its SPDX header")
    if not (HERE / "LICENSES.md").is_file():
        errors.append("missing LICENSES.md")
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


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    for token in ("DEFER", "incomplete", "not_qualified", "proposal-only",
                  "RG-01", "RG-08", "not Dual-Path Echo Net", "room",
                  "blocked", "family", "substitut"):
        if token not in text:
            errors.append("README is missing token: " + token)
    for digest in (list(reference.SOURCE_PINS.values())
                   + list(reference.BOUNDARY_PINS.values())):
        if digest not in text:
            errors.append("README is missing pinned digest: " + digest)
    if report:
        for token in (reference.BASE_COMMIT, reference.TASK_ID):
            if token not in text:
                errors.append("README is missing identity: " + token)


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed: " + result.stderr.strip())
        return []
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "diff", "--check"],
        capture_output=True, text=True)
    if diff_check.returncode != 0 or diff_check.stdout.strip():
        errors.append("git diff --check failed: " + diff_check.stdout.strip())
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change: " + path)
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
    print(f"PASS pins_ok={pin_count} json_ok=2 report_sha256="
          f"{reference.file_digest(REPORT)} cold_starts=3/3 "
          f"byte_identical=true profile=room status=incomplete "
          f"decision=DEFER qualification=not_qualified "
          f"licensing_ok=1 scope_ok=1 changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
