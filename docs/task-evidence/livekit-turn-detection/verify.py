#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local LiveKit evidence.

The original directory is never written. Regeneration runs in three independent
scratch trees with fresh interpreter processes and symlinks to the pinned,
read-only source and boundary files. The branch scope gate resolves the newest
merge-base against an available PR base ref and fails closed.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import re
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

TEMP_ROOT = Path(
    "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode")
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"
TASK_PREFIX = reference.TASK_PREFIX
# Concatenated so this literal never contains a contiguous SPDX token.
SPDX_LICENSE = "SPDX-License-" + "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".lib", ".m4a",
    ".model", ".mp3", ".mp4", ".o", ".onnx", ".opus", ".pcap", ".pcapng",
    ".pt", ".pth", ".pyc", ".safetensors", ".so", ".wasm", ".wav", ".weights",
}
REPORT_KEYS = {
    "absence_probes", "analysis_profile", "asset_audit", "asset_requirements",
    "base_commit", "boundary", "boundary_pins", "branch", "caller_asset_contract",
    "candidate_metrics", "component", "component_id", "decision", "defer_before",
    "depends_on", "determinism", "evidence_status", "exact_blockers", "format",
    "gates", "geometry", "incomplete", "missing_historical_artifacts", "mode",
    "non_claims", "profile", "profile_key", "proposal_only",
    "public_v0_geometry", "qualification", "qualification_reason",
    "qualification_status", "release_gates", "repository", "reproduction",
    "reviewer", "schema_id", "scope", "source_pins", "source_reported_context",
    "status", "synthetic_policy_control", "task", "task_id",
    "task_row_identity", "title", "upstream_record", "worktree", "write_scope",
}
CONTRACT_KEYS = {
    "absence_probes", "analysis_requirement_ids", "asset_audit",
    "asset_requirements", "base_commit", "boundary", "boundary_pins", "branch",
    "caller_asset_contract", "candidate_metrics", "component", "component_id",
    "contract_id", "decision", "defer_before", "depends_on", "determinism",
    "evidence_status", "exact_blockers", "format", "gates", "geometry",
    "incomplete", "missing_historical_artifacts", "mode", "non_claims", "profile",
    "profile_key", "proposal_only", "public_v0_geometry", "qualification",
    "qualification_reason", "qualification_status", "reference_status",
    "release_gates", "repository", "reproduction", "required_artifacts",
    "reviewer", "schema_id", "scope", "source_pins", "source_reported_context",
    "status", "task", "task_id",
    "task_row_identity", "title", "upstream_record", "worktree", "write_scope",
}


def sdk_root() -> Path:
    override = os.environ.get("SDK_ROOT")
    if override and (Path(override) / "REUSE.toml").is_file():
        return Path(override)
    cursor = HERE
    while cursor != cursor.parent:
        if (cursor / "REUSE.toml").is_file() and (cursor / "LICENSES").is_dir():
            return cursor
        cursor = cursor.parent
    return HERE.parents[2]


SDK = sdk_root()
SOURCE_ROOT = Path(os.environ.get(
    "SOURCE_ROOT", str(reference.SOURCE_ROOT))).resolve()


def _expect(condition: bool, message: str, errors: list[str]) -> bool:
    if not condition:
        errors.append(message)
    return bool(condition)


def check_profile_source(errors: list[str]) -> None:
    try:
        source = reference.profile_source()
    except (OSError, ValueError) as error:
        errors.append("profile_source_failed:" + str(error))
        return
    if source["profile"] != "analysis" or source["key"] != "Analysis":
        errors.append("profile_source_not_analysis")
    if not source["row"].startswith("| Analysis |"):
        errors.append("profile_row_not_analysis")


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    text = PINS.read_text(encoding="ascii")
    try:
        rows = reference.parse_pin_lines(text)
    except ValueError as error:
        errors.append(str(error))
        return 0
    expected = reference.allowed_pin_keys()
    seen: set[str] = set()
    verified = 0
    for digest, path in rows:
        if path in seen:
            errors.append("duplicate_pin:" + path)
            continue
        seen.add(path)
        if path not in expected:
            errors.append("unexpected_pin:" + path)
            continue
        if path.startswith("source:"):
            target = SOURCE_ROOT / path[len("source:"):]
        elif path.startswith("sdk:"):
            target = SDK / path[len("sdk:"):]
        else:
            target = HERE / path[len(TASK_PREFIX):]
        if not target.is_file():
            errors.append("pin_target_missing:" + path)
            continue
        if reference.sha256_file(target) != digest:
            errors.append("pin_mismatch:" + path)
            continue
        verified += 1
    for path in sorted(expected - seen):
        errors.append("missing_pin:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return verified


def _check_common(document: dict | None, label: str,
                  errors: list[str]) -> bool:
    if document is None:
        return False
    ok = True

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, label + ":" + message, errors) and ok

    expect(document.get("task") == reference.TASK, "task mismatch")
    expect(document.get("task_id") == reference.TASK, "task_id mismatch")
    expect(document.get("component") == reference.COMPONENT,
           "component mismatch")
    expect(document.get("component_id") == reference.COMPONENT_ID,
           "component_id mismatch")
    expect(document.get("repository") == reference.REPOSITORY,
           "repository mismatch")
    expect(document.get("mode") == reference.MODE, "mode mismatch")
    expect(document.get("profile") == reference.PROFILE, "profile mismatch")
    expect(document.get("profile_key") == reference.PROFILE_KEY,
           "profile key mismatch")
    expect(document.get("status") == reference.STATUS, "status mismatch")
    expect(document.get("evidence_status") == reference.EVIDENCE_STATUS,
           "evidence_status mismatch")
    expect(document.get("decision") == reference.DECISION, "decision mismatch")
    expect(document.get("defer_before") == reference.DEFER_BEFORE,
           "defer_before mismatch")
    expect(document.get("qualification_status")
           == reference.QUALIFICATION_STATUS, "qualification mismatch")
    expect(document.get("base_commit") == reference.BASE_COMMIT,
           "base commit mismatch")
    expect(document.get("branch") == reference.BRANCH, "branch mismatch")
    expect(document.get("worktree") == reference.CLAIM_WORKTREE,
           "worktree mismatch")
    expect(document.get("reviewer") == reference.REVIEWER, "reviewer mismatch")
    expect(document.get("write_scope") == reference.WRITE_SCOPE,
           "write scope mismatch")
    expect(document.get("proposal_only") is True, "proposal_only missing")
    expect(document.get("incomplete") is True, "incomplete missing")
    expect(document.get("source_pins") == reference.SOURCE_PINS,
           "source pins differ")
    expect(document.get("boundary_pins") == reference.BOUNDARY_PINS,
           "boundary pins differ")
    expect(document.get("public_v0_geometry")
           == reference.PUBLIC_V0_GEOMETRY, "public v0 geometry changed")
    boundary = document.get("boundary", {})
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "production_callback_registered", "descriptor_registry_change",
                "shared_build_or_ci_change", "installed_v0_behavior_change",
                "asset_bundled", "binary_vendored", "sdk_callback_invoked",
                "network_used", "adapter_json_added", "provider_json_added",
                "board_changed", "handoff_changed", "processor_exposure",
                "provider_intake_complete", "release_approval"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    scope = document.get("scope", {})
    for key in ("real_audio", "real_corpus", "model_loaded", "model_executed",
                "network_used", "download_attempted", "package_installed",
                "binary_committed", "device_timing", "listening",
                "public_benchmark", "release_claim", "numeric_parity_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")
    expect(scope.get("synthetic_only") is True, "synthetic_only is not true")
    gates = document.get("gates", [])
    expect([gate.get("id") for gate in gates] == list(reference.GATE_IDS),
           "gate IDs or order mismatch")
    expect(all(gate.get("blocked") is True for gate in gates),
           "a gate is not blocked")
    blockers = document.get("exact_blockers", [])
    expect([item.get("id") for item in blockers]
           == list(reference.BLOCKER_IDS), "blocker IDs or order mismatch")
    expect(all(item.get("state") == "open" for item in blockers),
           "a blocker is not open")
    qualification = document.get("qualification", {})
    expect(qualification.get("status") == reference.QUALIFICATION_STATUS,
           "nested qualification mismatch")
    expect(qualification.get("candidate_qualified") is False,
           "candidate appears qualified")
    expect(qualification.get("missing_result_promoted") is False,
           "a missing result is promoted")
    expect(qualification.get("no_missing_result_qualifies_candidate") is True,
           "missing-result guard missing")
    expect(qualification.get("processor_exposure") is False,
           "processor exposure is enabled")
    expect(qualification.get("blocked_gate_count") == len(reference.GATE_IDS),
           "blocked gate count mismatch")
    expect(qualification.get("blocked_gate_ids") == list(reference.GATE_IDS),
           "blocked gate IDs differ")
    upstream = document.get("upstream_record", {})
    expect(upstream.get("exact_revision") is None, "fabricated revision")
    expect(upstream.get("revision_pin_available") is False,
           "revision claims a pin")
    expect(upstream.get("asset_sha256") is None, "fabricated asset digest")
    expect(upstream.get("asset_digest_observed") is False,
           "asset digest claims observation")
    expect(upstream.get("weights_available_offline") is False,
           "offline weights claimed")
    expect(upstream.get("network_required_for_full_model") is True,
           "full model network requirement missing")
    expect(upstream.get("credentials_required_for_full_model") is True,
           "full model credentials requirement missing")
    expect(upstream.get("package_install_required_for_local_variant") is True,
           "local package install requirement missing")
    expect(upstream.get("license_id") == reference.UPSTREAM_LICENSE_ID,
           "licence identity mismatch")
    expect(upstream.get("license_text_observed") is False,
           "licence text claims observation")
    expect(upstream.get("license_apache_2_0") is False,
           "licence claims Apache-2.0")
    expect(len(upstream.get("variants", [])) == 3, "variant count mismatch")
    for variant in upstream.get("variants", []):
        expect(variant.get("asset_sha256") is None,
               "variant fabricates a digest: " + str(variant.get("id")))
        expect(variant.get("weights_digest_observed") is False,
               "variant claims digest observation: " + str(variant.get("id")))
    geometry = document.get("geometry", {})
    expect(geometry.get("model_geometry_status") == "unestablished",
           "geometry status is not unestablished")
    expect(geometry.get("audio_frame_geometry_published") is False,
           "audio geometry claimed")
    expect(geometry.get("sample_rate_hz") is None, "sample rate fabricated")
    expect(geometry.get("channels") is None, "channels fabricated")
    expect(geometry.get("hop_samples") is None, "hop fabricated")
    expect(geometry.get("latency_samples") is None, "latency fabricated")
    expect(geometry.get("preprocessing_published") is False,
           "preprocessing claimed")
    expect(geometry.get("policy_defaults_measured") is False,
           "policy defaults claim measurement")
    identity = document.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
    expect(identity.get("source") == reference.BOARD_TASK_ROW,
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == set(reference.MUTABLE_FIELDS_EXCLUDED),
           "mutable field exclusion mismatch")
    expect(document.get("candidate_metrics") is None,
           "candidate metrics are not null")
    expect(document.get("missing_historical_artifacts")
           == list(reference.MISSING_HISTORICAL_ARTIFACTS),
           "missing historical artifacts differ")
    expect(document.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")
    requirements = {item.get("id"): item
                    for item in document.get("asset_requirements", [])}
    expect(len(requirements) == len(reference.ASSET_REQUIREMENTS),
           "asset requirement count")
    expect(all(item.get("status") == "absent"
               for item in requirements.values()),
           "an asset requirement is not absent")
    audit = document.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent", "asset audit result")
    expect(audit.get("absence", {}).get("all_probes_absent") is True,
           "absence summary is not absent")
    expect(audit.get("absence", {}).get("present_count") == 0,
           "an absence probe reports a present artifact")
    probes = document.get("absence_probes", [])
    expect(len(probes) == len(reference.ABSENCE_PROBE_PATHS),
           "absence probe count")
    expect(all(probe.get("present") is False for probe in probes),
           "an absence probe is present")
    return ok


def check_report(errors: list[str]) -> bool:
    if not REPORT.is_file():
        errors.append("report.json missing")
        return False
    try:
        report = reference.read_strict_json(REPORT)
    except (OSError, ValueError) as error:
        errors.append("report_strict_json_failed:" + str(error))
        return False
    if set(report) != REPORT_KEYS:
        errors.append("report key set mismatch")
        return False
    ok = _check_common(report, "report", errors)
    try:
        reference.assert_no_float(report)
    except ValueError as error:
        errors.append("report:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "report:" + message, errors) and ok

    expect(isinstance(report.get("qualification_reason"), str)
           and bool(report["qualification_reason"].strip()),
           "qualification reason missing")
    profile = report.get("analysis_profile", {})
    expect(profile.get("profile") == "analysis", "analysis profile name")
    expect(profile.get("candidate_evaluated") is False,
           "analysis profile claims candidate evaluation")
    expect(profile.get("satisfied_for_qualification") == [],
           "analysis profile claims a satisfied item")
    items = profile.get("required_items", [])
    expect(len(items) == len(reference.ANALYSIS_REQUIREMENTS),
           "analysis requirement count")
    expect([item.get("id") for item in items]
           == [item[0] for item in reference.ANALYSIS_REQUIREMENTS],
           "analysis requirement IDs differ")
    expect(all(item.get("satisfied_for_qualification") is False
               and item.get("qualification_effect") == "none"
               for item in items),
           "an analysis item has qualification effect")
    contract_data = report.get("caller_asset_contract", {})
    expect(contract_data.get("schema_id") == reference.ASSET_SCHEMA_ID,
           "caller asset schema")
    expect(contract_data.get("absent_behavior")
           == "reject_before_processing", "caller absent behavior")
    expect(contract_data.get("asset_is_vendored") is False,
           "caller asset is vendored")
    expect(contract_data.get("revision_pin_available") is False,
           "caller revision claims a pin")
    expect(contract_data.get("asset_sha256_required") is True,
           "caller digest not required")
    expect(contract_data.get("positive_fixture_accepted") is True,
           "positive fixture is not accepted")
    expect(contract_data.get("all_probes_rejected") is True,
           "an admission probe was accepted")
    control = report.get("synthetic_policy_control", {})
    expect(control.get("label")
           == "synthetic_endpoint_policy_control_not_model_output",
           "synthetic control label")
    framewise = control.get("framewise_vad", {})
    expect(framewise.get("tp_samples") == 14400, "framewise tp")
    expect(framewise.get("fn_samples") == 3200, "framewise fn")
    expect(framewise.get("fp_samples") == 3200, "framewise fp")
    expect(framewise.get("tn_samples") == 84800, "framewise tn")
    expect(framewise.get("unknown_samples") == 6400, "framewise unknown")
    expect(framewise.get("speech_miss_rate") == "2/11", "speech miss rate")
    expect(framewise.get("false_alarm_rate") == "2/55", "false alarm rate")
    probability = control.get("probability_control", {})
    expect(probability.get("scaled_permille_squared_brier") == "3/200",
           "control Brier")
    policies = control.get("policies", {})
    vad = policies.get("vad_only", {})
    gated = policies.get("gated", {})
    expect([item.get("decision_frame") for item in vad.get("decisions", [])]
           == [69, 189, 319, 369], "vad decision frames")
    expect([item.get("delay_samples") for item in vad.get("decisions", [])]
           == [-1600, -3200, 8000, -43200], "vad delays")
    expect(vad.get("cutoff_count") == 3, "vad cutoff count")
    expect([item.get("decision_frame") for item in gated.get("decisions", [])]
           == [80, 239, 319, 589], "gated decision frames")
    expect([item.get("delay_samples") for item in gated.get("decisions", [])]
           == [160, 4800, 8000, -8000], "gated delays")
    expect(gated.get("cutoff_count") == 1, "gated cutoff count")
    expect(gated.get("max_wait_forced_count") == 1, "max-wait count")
    streams = control.get("event_streams", {})
    expect(streams.get("gated", {}).get("activity_events") == 660,
           "gated activity events")
    expect(streams.get("gated", {}).get("endpoint_events") == 4,
           "gated endpoint events")
    expect(streams.get("vad_only", {}).get("endpoint_events") == 4,
           "vad endpoint events")
    expect(streams.get("gated", {}).get("digest")
           != streams.get("vad_only", {}).get("digest"),
           "policy digests are equal")
    expect(control.get("cross_hop", {}).get("total_overlap_samples") == 300,
           "cross-hop total")
    adverse = control.get("adverse_controls", {})
    expect(adverse.get("all_rejected") is True, "adverse cases not rejected")
    expect(adverse.get("positive_fixture_accepted") is True,
           "positive asset fixture")
    expect(adverse.get("unknown_never_scored") is True,
           "unknown validity is scored")
    expect(adverse.get("missing_result_never_qualifies") is True,
           "missing result qualifies")
    expect(report.get("source_reported_context", {}).get("label")
           == "source_reported_not_measured_here",
           "source-reported context not labelled")
    expect(report.get("source_reported_context", {}).get("not_reproduced")
           is True, "source-reported context claims reproduction")
    expect(bool(report.get("non_claims")), "non-claims missing")
    return ok


def check_contract(errors: list[str]) -> bool:
    if not CONTRACT.is_file():
        errors.append("contract.json missing")
        return False
    try:
        contract = reference.read_strict_json(CONTRACT)
    except (OSError, ValueError) as error:
        errors.append("contract_strict_json_failed:" + str(error))
        return False
    if set(contract) != CONTRACT_KEYS:
        errors.append("contract key set mismatch")
        return False
    ok = _check_common(contract, "contract", errors)
    try:
        reference.assert_no_float(contract)
    except ValueError as error:
        errors.append("contract:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "contract:" + message, errors) and ok

    expect(contract.get("contract_id") == reference.CONTRACT_ID,
           "contract id mismatch")
    expect(contract.get("analysis_requirement_ids")
           == [item[0] for item in reference.ANALYSIS_REQUIREMENTS],
           "analysis requirement IDs differ")
    required = contract.get("required_artifacts", [])
    expect(required == list(run.LOCAL_PIN_FILES), "required artifacts differ")
    for name in required:
        expect((HERE / name).is_file(), "required artifact missing: " + name)
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3, "cold-start count")
    status = contract.get("reference_status", {})
    expect(status.get("asset_present") is False, "contract asset is present")
    expect(status.get("asset_pinned") is False, "contract asset is pinned")
    expect(status.get("model_loaded") is False, "contract model is loaded")
    expect(status.get("model_executed") is False, "contract model executed")
    expect(status.get("synthetic_control_present") is True,
           "contract synthetic control missing")
    expect(status.get("qualification_from_control") == "none",
           "contract control has qualification effect")
    return ok


def check_task_row_identity(errors: list[str]) -> bool:
    try:
        projection = reference.board_row_projection()
    except (OSError, ValueError) as error:
        errors.append("task_board_identity_failed:" + str(error))
        return False
    ok = True
    for label, path in (("report", REPORT), ("contract", CONTRACT)):
        try:
            document = reference.read_strict_json(path)
        except (OSError, ValueError) as error:
            errors.append(label + "_identity_read_failed:" + str(error))
            ok = False
            continue
        identity = document.get("task_row_identity", {})
        ok = _expect(identity.get("stable_sha256")
                     == projection["stable_sha256"],
                     f"{label}:task identity digest is stale", errors) and ok
        ok = _expect(identity.get("stable_fields")
                     == projection["stable_fields"],
                     f"{label}:stable fields differ from the board",
                     errors) and ok
        ok = _expect(identity.get("claim") == projection["claim"],
                     f"{label}:claim differs from the board", errors) and ok
        encoded = reference.canonical_text(document)
        if re.search(r'TASKS\.json"\s*:\s*"[0-9a-f]{64}"', encoded):
            errors.append(label + ":contains a whole-file TASKS.json digest")
            ok = False
    return ok


def check_assets(errors: list[str]) -> bool:
    try:
        probes = reference.absence_probes()
    except (OSError, ValueError) as error:
        errors.append("absence_probe_failed:" + str(error))
        return False
    summary = reference.absence_summary(probes)
    ok = True
    ok = _expect(summary["all_probes_absent"] is True,
                 "an absence probe is present; re-evaluate the blocker",
                 errors) and ok
    ok = _expect(summary["present_count"] == 0,
                 "an absence probe reports a present artifact", errors) and ok
    if REPORT.is_file():
        report = reference.read_strict_json(REPORT)
        audit = report.get("asset_audit", {})
        ok = _expect(audit.get("observed_absence_probes") == probes,
                     "asset audit observation is stale", errors) and ok
    return ok


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    for name in ("README.md", "LICENSES.md"):
        text = ((HERE / name).read_text(encoding="utf-8") if
                (HERE / name).is_file() else "")
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_markdown_spdx:" + name)
    reuse_path = SDK / "REUSE.toml"
    if not reuse_path.is_file():
        errors.append("reuse_toml_missing")
    else:
        reuse = reuse_path.read_text(encoding="utf-8")
        reuse_token = "SPDX-License-" + 'Identifier = "Apache-2.0"'
        if '"docs/**"' not in reuse or reuse_token not in reuse:
            errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name in {"LICENSE", "LICENSE.txt",
                                            "COPYING", "NOTICE"}:
            errors.append("vendored_license_file:" + path.name)


def check_readme(errors: list[str]) -> None:
    if not README.is_file():
        errors.append("README missing")
        return
    text = README.read_text(encoding="utf-8")
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "BLK-01", "BLK-08", "Analysis", "LiveKit", "v1-mini",
                  "text", "caller-supplied", "LiveKit Model License",
                  reference.TASK, reference.TITLE, reference.BASE_COMMIT,
                  "endpoint", "framewise", "cutoff"):
        if token not in text:
            errors.append("README is missing token: " + token)
    try:
        reference.verify_readme_digests(text)
    except (OSError, ValueError) as error:
        errors.append("readme_digest_table_failed:" + str(error))


def check_sources_reproduction(errors: list[str]) -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    result = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE), env=environment, capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("committed_artifacts_not_reproducible:" +
                      (result.stderr.strip() or result.stdout.strip()))


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base = reference.scope_base(SDK)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    workspace = scratch / "audioml"
    sdk = workspace / "worktrees/audio-sdk/SDK-LIVEKIT-TURN-DETECTION"
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    names = ("contract.json", "report.json", "report.json.sha256",
             "SOURCES.sha256", "README.md")
    committed = tuple((HERE / name).read_bytes() for name in names)
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1",
                       PYTHONHASHSEED="0", SOURCE_ROOT=str(SOURCE_ROOT))
    root_parent = TEMP_ROOT if TEMP_ROOT.is_dir() else None
    with tempfile.TemporaryDirectory(prefix="sdk-livekit-turn-cold-",
                                     dir=root_parent) as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py"],
                                     cwd=target, capture_output=True,
                                     text=True, env=environment)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" +
                              process.stderr.strip())
                continue
            generated = tuple((target / name).read_bytes() for name in names)
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    report_ok = check_report(errors)
    contract_ok = check_contract(errors)
    identity_ok = check_task_row_identity(errors)
    assets_ok = check_assets(errors)
    check_licensing(errors)
    check_readme(errors)
    check_sources_reproduction(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = (hashlib.sha256(REPORT.read_bytes()).hexdigest()
              if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} report_ok={report_ok} "
              f"contract_ok={contract_ok} identity_ok={identity_ok} "
              f"assets_ok={assets_ok} cold_starts={len(digests)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(reference.GATE_IDS)} "
          f"blockers={len(reference.BLOCKER_IDS)} "
          f"analysis_items={len(reference.ANALYSIS_REQUIREMENTS)} "
          f"adverse_cases={len(reference.ADVERSE_ASSET_CASE_IDS)} "
          f"cold_starts=3/3 byte_identical=true profile=Analysis "
          f"status={reference.STATUS} decision=DEFER "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
