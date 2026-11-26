#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only, fail-closed verification of the task-local IRCAM SuperVP package.

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
GATE_IDS = ("RG-01", "RG-02", "RG-03", "RG-04", "RG-05", "RG-06", "RG-07",
            "RG-08")
BLOCKER_IDS = ("BLK-01", "BLK-02", "BLK-03", "BLK-04", "BLK-05", "BLK-06",
               "BLK-07", "BLK-08")


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
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT",
                                  str(reference.SOURCE_ROOT))).resolve()


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
    if source["profile"] != "Rate" or source["key"] != "rate":
        errors.append("profile_source_not_rate")
    if not source["row"].startswith("| Rate |"):
        errors.append("profile_row_not_rate")


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
        root = (SOURCE_ROOT if path.startswith("source:")
                else SDK if path.startswith("sdk:") else HERE)
        relative = (path[len("source:"):] if path.startswith("source:")
                    else path[len("sdk:"):] if path.startswith("sdk:")
                    else path[len(TASK_PREFIX):])
        target = root / relative
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
    expect(document.get("repository") == reference.REPOSITORY,
           "repository mismatch")
    expect(document.get("mode") == reference.MODE, "mode mismatch")
    expect(document.get("profile") == reference.PROFILE, "profile mismatch")
    expect(document.get("status") == reference.STATUS, "status mismatch")
    expect(document.get("evidence_status") == reference.EVIDENCE_STATUS,
           "evidence_status mismatch")
    expect(document.get("decision") == reference.DECISION,
           "decision mismatch")
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
                "production_callback_registered",
                "descriptor_registry_change", "shared_build_or_ci_change",
                "installed_v0_behavior_change", "asset_bundled",
                "binary_vendored", "sdk_callback_invoked", "network_used",
                "adapter_json_added", "provider_json_added"):
        expect(boundary.get(key) is False, "boundary flag not false: " + key)
    expect(boundary.get("descriptor_settings") == {},
           "descriptor settings are not empty")
    scope = document.get("scope", {})
    for key in ("real_audio", "real_corpus", "vendor_engine_loaded",
                "vendor_engine_executed", "tsm_output_generated",
                "network_used", "download_attempted", "binary_committed",
                "device_timing", "listening", "public_benchmark",
                "release_claim"):
        expect(scope.get(key) is False, "scope flag not false: " + key)
    expect(scope.get("task_local_only") is True,
           "task_local_only is not true")
    gates = document.get("gates", [])
    expect([gate.get("id") for gate in gates] == list(GATE_IDS),
           "gate IDs or order mismatch")
    expect(all(gate.get("status") == "blocked" for gate in gates),
           "a gate is not blocked")
    blockers = document.get("exact_blockers", [])
    expect([item.get("id") for item in blockers] == list(BLOCKER_IDS),
           "blocker IDs or order mismatch")
    expect(all(item.get("state") == "open" for item in blockers),
           "a blocker is not open")
    expect(document.get("qualification", {}).get("status")
           == reference.QUALIFICATION_STATUS, "nested qualification mismatch")
    expect(document.get("qualification", {}).get("candidate_qualified")
           is False, "candidate appears qualified")
    expect(document.get("qualification", {}).get(
        "no_missing_result_qualifies_candidate") is True,
        "missing-result guard missing")
    expect(document.get("qualification", {}).get("blocked_gate_count") == 8,
           "blocked gate count is not eight")
    expect(document.get("qualification", {}).get("blocked_gate_ids")
           == list(GATE_IDS), "blocked gate IDs differ")
    upstream = document.get("upstream_record", {})
    expect(upstream.get("revision") is None, "fabricated vendor revision")
    expect(upstream.get("revision_pin_available") is False,
           "vendor revision claims a pin")
    expect(upstream.get("public_source_available") is False,
           "public source claimed")
    expect(upstream.get("public_binary_available") is False,
           "public binary claimed")
    expect(upstream.get("embedding_requires_separate_agreement") is True,
           "embedding agreement not required")
    expect(upstream.get("geometry_status") == reference.GEOMETRY_STATUS,
           "geometry status mismatch")
    expect(upstream.get("task_scope") == reference.TASK_SCOPE,
           "task scope mismatch")
    expect(upstream.get("task_kind") == reference.TASK_KIND,
           "task kind mismatch")
    expect(upstream.get("price_recorded") is False, "price fabricated")
    expect(upstream.get("current_sdk_availability_verified") is False,
           "SDK availability overclaimed")
    identity = document.get("task_row_identity", {})
    expect(identity.get("whole_file_hashed") is False,
           "task identity claims a whole-file hash")
    expect(identity.get("source") == reference.BOARD_TASK_ROW,
           "task identity source mismatch")
    expect(set(identity.get("excluded_mutable_fields", []))
           == set(reference.MUTABLE_FIELDS_EXCLUDED),
           "mutable field exclusion mismatch")
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
    ok = _check_common(report, "report", errors)
    try:
        reference.assert_no_float(report)
    except ValueError as error:
        errors.append("report:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "report:" + message, errors) and ok

    qualification = report.get("qualification", {})
    expect(isinstance(qualification.get("reason"), str)
           and bool(qualification["reason"].strip()),
           "qualification reason missing")
    disposition = report.get("disposition", {})
    expect(disposition.get("decision") == "DEFER", "disposition decision")
    expect(disposition.get("status") == "incomplete", "disposition status")
    expect(disposition.get("missing_result_qualifies") is False,
           "disposition missing-result guard")
    expect(disposition.get("default_enabled") is False,
           "disposition default")
    geometry = report.get("geometry", {})
    expect(geometry.get("supervp_geometry_status") == "unestablished",
           "geometry status is not unestablished")
    expect(geometry.get("supervp_geometry_asserted") is False,
           "geometry is asserted")
    expect(geometry.get("sample_rate_hz") is None, "sample rate fabricated")
    expect(geometry.get("channels") is None, "channels fabricated")
    expect(geometry.get("hop_samples") is None, "hop fabricated")
    expect(geometry.get("latency_samples") is None, "latency fabricated")
    expect(geometry.get("rate_semantics_verified") is False,
           "rate semantics overclaimed")
    expect(geometry.get("streaming_supported") is None,
           "streaming support fabricated")
    profile = report.get("rate_profile", {})
    expect(profile.get("name") == "rate", "rate profile name")
    expect(profile.get("satisfied_for_qualification") == [],
           "rate profile claims a satisfied item")
    expect(profile.get("real_engine_metrics") is None,
           "rate profile has real engine metrics")
    expect(len(profile.get("required_items", []))
           == len(reference.RATE_REQUIREMENTS), "rate requirement count")
    expect(all(item.get("qualification_effect") == "none"
               and item.get("satisfied_for_qualification") is False
               for item in profile.get("required_items", [])),
           "a rate item has qualification effect")
    protocol = report.get("reference_protocol", {})
    expect(protocol.get("engine_executed") is False,
           "reference protocol claims engine execution")
    expect(protocol.get("executor") == "absent",
           "reference protocol executor")
    expect(protocol.get("plan_source") == reference.CONTROL_PLAN_PROVENANCE,
           "plan source is not the labelled control")
    expect(protocol.get("qualification_effect") == "none",
           "reference protocol has qualification effect")
    expect(len(protocol.get("rate_mappings", []))
           == len(reference.CONTROL_RATES_BP), "rate mapping count")
    expect(protocol.get("unity_mapping", {}).get("output_samples")
           == protocol.get("source_pcm", {}).get("samples"),
           "unity mapping is not identity")
    expect(all(item.get("drift_samples") == 0
               for item in protocol.get("chunked_accounting", [])),
           "chunked accounting drifts")
    expect(all(item.get("measured") is False
               for item in protocol.get("acceptance_outcomes", [])),
           "an acceptance outcome claims a measurement")
    expect(protocol.get("geometry", {}).get("supervp_geometry_asserted")
           is False, "reference protocol asserts vendor geometry")
    controls = report.get("controls", {})
    expect(controls.get("adverse_all_rejected") is True,
           "adverse controls are not all rejected")
    expect(controls.get("adverse_case_count")
           == len(reference.ADVERSE_CASE_IDS), "adverse case count")
    expect(controls.get("nonfinite_rejected") is True,
           "nonfinite control missing")
    expect(controls.get("missing_asset_rejected_before_processing") is True,
           "missing-asset control missing")
    expect(controls.get("missing_result_never_qualifies") is True,
           "missing-result control missing")
    expect(controls.get("scope_mismatch_rejected") is True,
           "scope mismatch control missing")
    expect(controls.get("streaming_variant_rejected") is True,
           "streaming variant control missing")
    expect(controls.get("commercial_terms_required") is True,
           "commercial terms control missing")
    expect(controls.get("validator_accepts_well_formed_manifest") is True,
           "positive manifest control missing")
    expect(controls.get("absence_probes_all_absent") is True,
           "absence probes are not all absent")
    adverse = controls.get("adverse", [])
    expect(len(adverse) == len(reference.ADVERSE_CASE_IDS),
           "adverse control count")
    expect(all(item.get("result") == "rejected" for item in adverse),
           "an adverse control was accepted")
    audit = report.get("asset_audit", {})
    expect(audit.get("qualified") is False, "asset audit claims qualification")
    expect(audit.get("audit_result") == "absent", "asset audit result")
    expect(audit.get("source", {}).get("present") is False,
           "asset audit claims a source")
    expect(audit.get("runtime", {}).get("pinned_runtime_present") is False,
           "asset audit claims a runtime")
    expect(audit.get("rights", {}).get("commercial_license_verified") is False,
           "asset audit claims commercial terms")
    expect(audit.get("absence", {}).get("all_probes_absent") is True,
           "absence summary is not absent")
    expect(len(report.get("absence_probes", []))
           == len(reference.ABSENCE_PROBE_PATHS), "absence probe count")
    requirements = {item.get("id"): item
                    for item in report.get("asset_requirements", [])}
    expect(set(requirements) == {
        "licensed_vendor_sdk_or_runtime", "vendor_version_and_build_pin",
        "commercial_license_and_terms", "api_reference_and_geometry",
        "runtime_and_platform_lock", "rate_cohort_and_references",
        "parity_vector", "redistribution_and_output_rights"},
        "asset requirement IDs differ")
    for key in ("licensed_vendor_sdk_or_runtime",
                "vendor_version_and_build_pin",
                "commercial_license_and_terms", "api_reference_and_geometry",
                "runtime_and_platform_lock", "rate_cohort_and_references",
                "parity_vector", "redistribution_and_output_rights"):
        expect(requirements.get(key, {}).get("status") == "absent",
               "asset requirement not absent: " + key)
    contract_data = report.get("caller_asset_contract", {})
    expect(contract_data.get("absent_behavior")
           == "reject_before_processing", "caller absent behavior")
    expect(contract_data.get("asset_is_vendored") is False,
           "caller asset is vendored")
    expect(contract_data.get("required_source_revision") is None,
           "caller revision fabricated")
    expect(contract_data.get("revision_pin_available") is False,
           "caller revision claims a pin")
    expect(contract_data.get("required_variant") == reference.CALLER_VARIANT,
           "caller variant")
    expect(contract_data.get("required_scope") == reference.CALLER_SCOPE,
           "caller scope")
    expect(contract_data.get("required_commercial_terms_acknowledged")
           is True, "caller commercial terms not required")
    expect(report.get("candidate_metrics") is None,
           "candidate_metrics is not null")
    expect(report.get("source_reported_context", {}).get("label")
           == "source_reported_not_measured_here",
           "source-reported context not labelled")
    for missing in ("vendor/ircam-supervp", "data/vendor/ircam-supervp",
                    "data/rights/ircam-supervp-rights.json",
                    "data/runs/ircam-supervp-rate-cohort/manifest.json"):
        expect(missing in report.get("missing_historical_artifacts", []),
               "missing artifact not recorded: " + missing)
    expect(report.get("determinism", {}).get(
        "cold_start_regenerations_required") == 3,
        "cold-start requirement is not three")
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
    ok = _check_common(contract, "contract", errors)
    try:
        reference.assert_no_float(contract)
    except ValueError as error:
        errors.append("contract:" + str(error))
        ok = False

    def expect(condition: bool, message: str) -> None:
        nonlocal ok
        ok = _expect(condition, "contract:" + message, errors) and ok

    expect(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID,
           "schema id mismatch")
    expect(len(contract.get("rate_profile_requirements", []))
           == len(reference.RATE_REQUIREMENTS), "rate requirement count")
    expect(len(contract.get("required_artifacts", []))
           == len(reference.REQUIRED_ARTIFACTS), "artifact count")
    expect(contract.get("reproduction", {}).get(
        "cold_start_regenerations") == 3, "cold-start count")
    expect(contract.get("caller_asset_contract", {}).get(
        "revision_pin_available") is False, "contract caller revision pin")
    expect(contract.get("caller_asset_contract", {}).get(
        "required_commercial_terms_acknowledged") is True,
        "contract commercial terms not required")
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
                  "BLK-01", "BLK-06", "rate", "Rate", "IRCAM", "SuperVP",
                  reference.PRODUCT_URL, reference.TASK, reference.TITLE,
                  reference.BASE_COMMIT,
                  "no public open-source licence",
                  "separate agreement with IRCAM"):
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
    sdk = workspace / "worktrees/audio-sdk/SDK-IRCAM-SUPERVP"
    target = sdk / reference.TASK_PREFIX
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for name in ("audio-benchmark-platform", "cpp-library"):
        link = workspace / name
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(SOURCE_ROOT / name)
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
    with tempfile.TemporaryDirectory(prefix="sdk-ircam-supervp-cold-",
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
    print(f"PASS pins={pins} gates={len(GATE_IDS)} blockers={len(BLOCKER_IDS)} "
          f"rate_items={len(reference.RATE_REQUIREMENTS)} "
          f"adverse_cases={len(reference.ADVERSE_CASE_IDS)} "
          f"cold_starts=3/3 byte_identical=true profile=Rate "
          f"status={reference.STATUS} decision=DEFER "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
