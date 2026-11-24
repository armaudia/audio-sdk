# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Bridge descriptor validation and canonical synthetic report model.

This is a deterministic tool/evidence boundary. It validates descriptors and
manifests; it does not resolve entrypoints, spawn subprocesses, create SDK
sessions, register providers or qualify any candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
from typing import Any, Dict, List, Optional, Tuple

import fixture

ROOT = Path(__file__).resolve().parent
CONTRACT = "contract.json"
ADAPTER = "adapter.json"
PROVIDER = "provider.json"
SOURCES = "SOURCES.sha256"
REPORT = "report.json"
SIDECAR = "report.json.sha256"
REPORT_SCHEMA = "audio-sdk/bench-subprocess-evidence-report/0.1"
STATUS_PROPOSAL = "proposal_only_not_qualified"
COPYRIGHT_TAG = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
LICENSE_TAG = "SPDX" "-License-Identifier: Apache-2.0"
REQUEST_ID = re.compile(r"^[a-z0-9][a-z0-9-]{2,63}$")
REASON_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{1,95}$")
HEX64 = re.compile(r"^[0-9a-f]{64}$")


class Reject(Exception):
    """Explicit fail-closed validation outcome with a stable reason code."""

    def __init__(self, reason: str, field: str = "") -> None:
        super().__init__(reason)
        self.reason = reason
        self.field = field


def strict_loads(text: str) -> Dict[str, Any]:
    """Strict JSON: duplicate keys, NaN/Infinity and non-object roots fail."""
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise Reject("strict_json_duplicate_key", key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise Reject("strict_json_nonfinite", token)

    try:
        value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    except Reject:
        raise
    except (ValueError, TypeError) as error:
        raise Reject("strict_json_invalid", str(error)) from error
    if not isinstance(value, dict):
        raise Reject("strict_json_non_object")
    return value


def load_package_json(name: str) -> Dict[str, Any]:
    return strict_loads((ROOT / name).read_text(encoding="utf-8"))


def _nonfinite_path(value: Any, path: str = "$") -> Optional[str]:
    if isinstance(value, float) and not math.isfinite(value):
        return path
    if isinstance(value, dict):
        for key in sorted(value, key=str):
            found = _nonfinite_path(value[key], path + "." + str(key))
            if found:
                return found
    if isinstance(value, (list, tuple)):
        for index, item in enumerate(value):
            found = _nonfinite_path(item, "%s[%d]" % (path, index))
            if found:
                return found
    return None


def canonical_bytes(value: Any) -> bytes:
    """Canonical, sorted, compact, finite-only JSON encoding."""
    path = _nonfinite_path(value)
    if path:
        raise Reject("nonfinite_value", path)
    try:
        text = json.dumps(value, sort_keys=True, separators=(",", ":"),
                          ensure_ascii=True, allow_nan=False)
    except (TypeError, ValueError) as error:
        raise Reject("canonicalization_failed", str(error)) from error
    return text.encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def canonical_digest(value: Any) -> str:
    return sha256_bytes(canonical_bytes(value))


def fixture_digest(item: Dict[str, Any]) -> str:
    """Digest all fixture inputs including deliberately invalid JSON text."""
    text = json.dumps(item, sort_keys=True, separators=(",", ":"),
                      ensure_ascii=True, allow_nan=True, default=repr)
    return sha256_bytes(text.encode("utf-8"))


def _require(value: Dict[str, Any], key: str, field: str = "") -> Any:
    if key not in value:
        raise Reject("field_missing", field or key)
    return value[key]


def _is_hex64(value: Any) -> bool:
    return isinstance(value, str) and bool(HEX64.fullmatch(value))


def validate_descriptor(descriptor: Dict[str, Any]) -> str:
    """Validate the evidence bridge descriptor; return its canonical digest."""
    if not isinstance(descriptor, dict):
        raise Reject("descriptor_not_object")
    digest = canonical_digest(descriptor)
    if descriptor.get("protocol") != fixture.PROTOCOL:
        raise Reject("unsupported_protocol", "protocol")
    if descriptor.get("deny_network") is not True:
        raise Reject("network_not_denied", "deny_network")
    if descriptor.get("downloads") != "denied":
        raise Reject("downloads_not_denied", "downloads")
    if descriptor.get("nested_sandbox_policy") != "fail_closed":
        raise Reject("nested_policy_not_fail_closed", "nested_sandbox_policy")
    if descriptor.get("production_callback") != "none":
        raise Reject("production_callback_not_none", "production_callback")
    if descriptor.get("registration") != "unregistered":
        raise Reject("provider_registration_declared", "registration")
    if descriptor.get("entrypoint_invoked") is not False:
        raise Reject("entrypoint_invoked", "entrypoint_invoked")
    cli = _require(descriptor, "cli")
    if not isinstance(cli, dict) or cli.get("single_attempt") is not True:
        raise Reject("cli_not_single_attempt", "cli")
    if cli.get("request_flag") != "--request" or cli.get("result_flag") != "--result":
        raise Reject("cli_flags_invalid", "cli")
    if descriptor.get("workspace_root") != "/workspace":
        raise Reject("workspace_root_invalid", "workspace_root")
    if descriptor.get("entrypoint_resolution") != "workspace_root_relative":
        raise Reject("entrypoint_resolution_invalid", "entrypoint_resolution")
    attempt = descriptor.get("attempt_dir")
    if not isinstance(attempt, str) or not attempt.startswith("/attempt/"):
        raise Reject("attempt_dir_invalid", "attempt_dir")
    writable = _require(descriptor, "writable_roots")
    if not isinstance(writable, list) or writable != [attempt]:
        raise Reject("writable_root_escape", "writable_roots")
    grants = _require(descriptor, "read_grants")
    if not isinstance(grants, list) or not grants:
        raise Reject("read_grant_missing", "read_grants")
    seen = set()
    for grant in grants:
        if not isinstance(grant, str) or grant in seen:
            raise Reject("read_grant_invalid", "read_grants")
        seen.add(grant)
        if not grant.startswith(("/caller/", "/workspace/")) or ".." in grant.split("/"):
            raise Reject("read_grant_outside_scope", "read_grants")
    for required in ("/caller/input", "/caller/assets", "/workspace/adapters"):
        if required not in seen:
            raise Reject("read_grant_missing", required)
    sources = _require(descriptor, "source_paths")
    if not isinstance(sources, list) or not sources:
        raise Reject("source_paths_missing", "source_paths")
    for path in sources:
        if not isinstance(path, str) or path.startswith("/") or ".." in path.split("/"):
            raise Reject("source_path_invalid", "source_paths")
    return digest


def validate_frame(frame: Any) -> None:
    if not isinstance(frame, dict):
        raise Reject("frame_not_object", "frame")
    if frame.get("sample_rate_hz") != 16000:
        raise Reject("sample_rate_mismatch", "frame.sample_rate_hz")
    if frame.get("channels") != 1:
        raise Reject("channels_mismatch", "frame.channels")
    if frame.get("dtype") != "float32":
        raise Reject("dtype_mismatch", "frame.dtype")
    if frame.get("samples") != 160:
        raise Reject("frame_samples_mismatch", "frame.samples")
    if not _is_hex64(frame.get("data_digest")):
        raise Reject("frame_digest_invalid", "frame.data_digest")
    extra = set(frame) - {"sample_rate_hz", "channels", "dtype", "samples", "data_digest"}
    if extra:
        raise Reject("frame_field_unknown", sorted(extra)[0])


def validate_assets(assets: Any) -> None:
    if not isinstance(assets, list) or not assets:
        raise Reject("assets_missing", "assets")
    expected = fixture.synthetic_asset()
    expected_digest = expected["sha256"]
    expected_count = expected["byte_count"]
    ids = set()
    for asset in assets:
        if not isinstance(asset, dict):
            raise Reject("asset_not_object", "assets")
        asset_id = _require(asset, "asset_id")
        if not isinstance(asset_id, str) or not REQUEST_ID.fullmatch(asset_id.replace(".", "-")):
            raise Reject("asset_id_invalid", "asset_id")
        if asset_id in ids:
            raise Reject("duplicate_asset_id", asset_id)
        ids.add(asset_id)
        location = _require(asset, "location")
        if (not isinstance(location, str)
                or not location.startswith(("/caller/assets/", "/workspace/adapters/"))
                or ".." in location.split("/")):
            raise Reject("asset_location_not_granted", "location")
        if "rights_ref" not in asset:
            raise Reject("asset_rights_ref_missing", "rights_ref")
        if asset.get("rights_ref") != fixture.RIGHTS_REF:
            raise Reject("asset_rights_ref_invalid", "rights_ref")
        if asset.get("sha256") != expected_digest:
            raise Reject("asset_hash_mismatch", asset_id)
        if asset.get("byte_count") != expected_count:
            raise Reject("asset_byte_count_mismatch", asset_id)


def validate_request(request: Any, descriptor: Dict[str, Any]) -> str:
    """Validate a synthetic request; return 'ok' or 'ok_omitted'."""
    if not isinstance(request, dict):
        raise Reject("request_not_object")
    nonfinite = _nonfinite_path(request)
    if nonfinite:
        raise Reject("nonfinite_value", nonfinite)
    if request.get("protocol_version") != fixture.PROTOCOL:
        raise Reject("unsupported_protocol", "protocol_version")
    request_id = request.get("request_id")
    if not isinstance(request_id, str) or not REQUEST_ID.fullmatch(request_id):
        raise Reject("request_id_invalid", "request_id")
    if request.get("execution_mode") != "buffered_worker":
        raise Reject("execution_mode_unsupported", "execution_mode")
    validate_frame(request.get("frame"))
    manifest = _require(request, "input_manifest")
    if not isinstance(manifest, dict):
        raise Reject("input_manifest_invalid", "input_manifest")
    location = manifest.get("location")
    attempt = descriptor["attempt_dir"].rstrip("/") + "/"
    if not isinstance(location, str) or not location.startswith("/caller/input/"):
        raise Reject("input_manifest_inside_attempt_dir", "input_manifest.location")
    if location.startswith(attempt) or ".." in location.split("/"):
        raise Reject("input_manifest_inside_attempt_dir", "input_manifest.location")
    if not _is_hex64(manifest.get("sha256")):
        raise Reject("input_manifest_digest_invalid", "input_manifest.sha256")
    if not isinstance(manifest.get("byte_count"), int) or isinstance(manifest.get("byte_count"), bool):
        raise Reject("input_manifest_byte_count_invalid", "input_manifest.byte_count")
    validate_assets(request.get("assets"))
    if request.get("download_assets") is True:
        raise Reject("download_requested", "download_assets")
    if "descriptor_digest" in request:
        if not _is_hex64(request["descriptor_digest"]):
            raise Reject("descriptor_digest_invalid", "descriptor_digest")
        if request["descriptor_digest"] != canonical_digest(descriptor):
            raise Reject("descriptor_digest_mismatch", "descriptor_digest")
    if "optional_selections" not in request:
        return "ok_omitted"
    selections = request["optional_selections"]
    if not isinstance(selections, dict):
        raise Reject("optional_selections_invalid", "optional_selections")
    if set(selections) - {"selection"}:
        raise Reject("optional_selection_unknown", sorted(set(selections) - {"selection"})[0])
    selection = selections.get("selection")
    if selection is None:
        raise Reject("optional_selection_null", "selection")
    allowed = {"identity-pcm", "passthrough-frame"}
    if selection not in allowed:
        raise Reject("optional_selection_unknown", "selection")
    return "ok"


def validate_result(result: Optional[Dict[str, Any]], request: Dict[str, Any],
                    descriptor: Dict[str, Any], request_status: str) -> None:
    if result is None:
        raise Reject("result_missing")
    if not isinstance(result, dict):
        raise Reject("result_not_object")
    nonfinite = _nonfinite_path(result)
    if nonfinite:
        raise Reject("nonfinite_value", nonfinite)
    if result.get("protocol_version") != fixture.PROTOCOL:
        raise Reject("unsupported_protocol", "result.protocol_version")
    if result.get("request_id") != request["request_id"]:
        raise Reject("result_request_id_mismatch", "result.request_id")
    if "status" not in result:
        raise Reject("result_field_missing", "status")
    status = result.get("status")
    if status not in {"ok", "ok_omitted", "blocked"}:
        raise Reject("result_status_invalid", "status")
    if status != request_status and status != "blocked":
        raise Reject("result_status_mismatch", "status")
    reason = result.get("reason_code")
    if not isinstance(reason, str) or not REASON_ID.fullmatch(reason):
        raise Reject("result_reason_invalid", "reason_code")
    expected_digest = sha256_bytes(fixture.pseudo_bytes(53, 128))
    if "result_manifest_digest" not in result:
        raise Reject("result_field_missing", "result_manifest_digest")
    if result.get("result_manifest_digest") != expected_digest:
        raise Reject("result_digest_mismatch", "result_manifest_digest")
    metrics = _require(result, "metrics")
    if not isinstance(metrics, dict):
        raise Reject("result_metrics_invalid", "metrics")
    if metrics.get("finite") is not True:
        raise Reject("result_metrics_invalid", "metrics.finite")
    if metrics.get("frames") != 1 or metrics.get("samples") != 160:
        raise Reject("result_metrics_invalid", "metrics.frames")
    if metrics.get("quality_score") != 0.0:
        raise Reject("result_metrics_invalid", "metrics.quality_score")
    result_assets = _require(result, "assets")
    if not isinstance(result_assets, list) or not result_assets:
        raise Reject("result_assets_missing", "assets")
    allowed_ids = {asset["asset_id"] for asset in request["assets"]}
    expected = fixture.synthetic_asset()
    for asset in result_assets:
        if not isinstance(asset, dict):
            raise Reject("result_asset_invalid", "assets")
        if asset.get("asset_id") not in allowed_ids:
            raise Reject("result_asset_unknown", "asset_id")
        if asset.get("sha256") != expected["sha256"]:
            raise Reject("result_asset_hash_mismatch", "asset_id")
        if asset.get("byte_count") != expected["byte_count"]:
            raise Reject("result_asset_byte_count_mismatch", "asset_id")


def evaluate_case(item: Dict[str, Any]) -> Dict[str, Any]:
    """Validate one fixture and return a canonical decision record."""
    case_id = item["case_id"]
    try:
        if item.get("request_text") is not None:
            request = strict_loads(item["request_text"])
        else:
            request = item["request"]
        validate_descriptor(item["descriptor"])
        request_status = validate_request(request, item["descriptor"])
        result = item.get("result")
        validate_result(result, request, item["descriptor"], request_status)
        status = "incomplete" if result is None else result["status"]
        reason = "result_missing" if result is None else result["reason_code"]
    except Reject as error:
        reason = error.reason
        status = "incomplete" if reason == "result_missing" else "rejected"
    decision = {
        "case_id": case_id,
        "category": item["category"],
        "expected_status": item["expected_status"],
        "expected_reason": item["expected_reason"],
        "actual_status": status,
        "actual_reason": reason,
        "input_digest": fixture_digest(item),
        "note": item["note"],
        "qualified": False,
    }
    return decision


def build_report() -> Dict[str, Any]:
    """Generate the complete deterministic synthetic evidence report."""
    contract = load_package_json(CONTRACT)
    adapter = load_package_json(ADAPTER)
    provider = load_package_json(PROVIDER)
    if contract["status"] != STATUS_PROPOSAL:
        raise Reject("contract_status_invalid", "status")
    if provider["status"] != STATUS_PROPOSAL or provider["registration"] != "unregistered":
        raise Reject("provider_boundary_invalid", "provider.json")
    validate_descriptor(adapter)

    decisions = [evaluate_case(fixture.build_fixture(case_id)) for case_id in fixture.fixture_ids()]
    for decision in decisions:
        if (decision["actual_status"] != decision["expected_status"]
                or decision["actual_reason"] != decision["expected_reason"]):
            raise Reject("fixture_expected_outcome_mismatch", decision["case_id"])
        if decision["qualified"]:
            raise Reject("candidate_qualified", decision["case_id"])

    counts = {status: 0 for status in ("ok", "ok_omitted", "blocked", "rejected", "incomplete")}
    for decision in decisions:
        counts[decision["actual_status"]] += 1
    categories: Dict[str, int] = {}
    for decision in decisions:
        categories[decision["category"]] = categories.get(decision["category"], 0) + 1

    cases_without_valid_result = [d for d in decisions
                                  if d["actual_status"] in {"blocked", "rejected", "incomplete"}]
    checks = {
        "strict_json_inputs": True,
        "descriptor_boundary_validated": True,
        "asset_identity_fail_closed": all(d["actual_status"] == "rejected"
                                          for d in decisions if d["category"] == "asset"),
        "sandbox_profile_fail_closed": all(d["actual_status"] in {"rejected", "blocked"}
                                           for d in decisions if d["category"] == "sandbox"),
        "missing_optional_selections_explicit": all(d["actual_status"] in {"ok_omitted", "rejected"}
                                                    for d in decisions if d["category"] == "missing_optional"),
        "nonfinite_controls_rejected": all(d["actual_status"] == "rejected"
                                           for d in decisions if d["category"] == "nonfinite"),
        "no_missing_result_qualifies": all(not d["qualified"] for d in cases_without_valid_result),
        "no_production_callback": adapter["production_callback"] == "none"
                                  and provider["production_callback"] == "none",
        "no_registration_or_linkage": (adapter["registration"] == "unregistered"
                                       and provider["registration"] == "unregistered"
                                       and provider["linked"] is False),
        "installed_v0_unchanged": contract["frame"]["installed_v0_unchanged"] is True
                                  and provider["installed_v0_unchanged"] is True,
        "fixture_expected_outcomes_match": True,
    }
    summary = {
        "cases_total": len(decisions),
        "status_counts": counts,
        "category_counts": dict(sorted(categories.items())),
        "qualified_candidates": 0,
        "invalid_or_missing_qualified": 0,
        "all_checks_green": all(checks.values()),
    }
    copyright_key, copyright_value = COPYRIGHT_TAG.split(": ", 1)
    license_key, license_value = LICENSE_TAG.split(": ", 1)
    report: Dict[str, Any] = {
        copyright_key: copyright_value,
        license_key: license_value,
        "schema_id": REPORT_SCHEMA,
        "status": STATUS_PROPOSAL,
        "task_id": contract["task_id"],
        "base_commit": contract["base_commit"],
        "scope": contract["scope"],
        "tool_profile": contract["tool_profile"],
        "descriptor_digests": {
            "contract_json": canonical_digest(contract),
            "adapter_json": canonical_digest(adapter),
            "provider_json": canonical_digest(provider),
        },
        "source_pins": contract["source_pins"],
        "fixture_digests": {d["case_id"]: d["input_digest"] for d in decisions},
        "cases": decisions,
        "summary": summary,
        "checks": checks,
        "evidence_separation": contract["observations"],
        "boundary": contract["boundary"],
        "canonical_report_rule": "sha256 of canonical JSON of this object without canonical_report_digest",
    }
    report["canonical_report_digest"] = canonical_digest(report)
    return report


def read_sidecar() -> str:
    text = (ROOT / SIDECAR).read_text(encoding="ascii")
    for line in text.splitlines():
        parts = line.split()
        if len(parts) >= 2 and bool(HEX64.fullmatch(parts[0])):
            return parts[0]
    raise Reject("sidecar_digest_missing", SIDECAR)


def report_bytes(report: Optional[Dict[str, Any]] = None) -> bytes:
    value = build_report() if report is None else report
    return canonical_bytes(value) + b"\n"


def sidecar_bytes(data: bytes) -> bytes:
    header = "# " + COPYRIGHT_TAG + "\n# " + LICENSE_TAG + "\n"
    return (header + sha256_bytes(data) + "  " + REPORT + "\n").encode("ascii")


def parse_sources(text: str) -> Dict[str, str]:
    """Parse workspace:/pkg: prefixed sha256sum-style source pin lines."""
    pins: Dict[str, str] = {}
    for line in text.splitlines():
        stripped = line.strip()
        if not stripped or stripped.startswith("#"):
            continue
        parts = stripped.split(None, 1)
        if len(parts) != 2:
            raise Reject("source_line_invalid", stripped)
        digest, location = parts
        if not _is_hex64(digest) or ":" not in location:
            raise Reject("source_line_invalid", stripped)
        prefix, relative = location.split(":", 1)
        if prefix not in {"workspace", "pkg"} or not relative or relative.startswith("/"):
            raise Reject("source_line_invalid", location)
        pins[location] = digest
    return pins


def find_workspace(explicit: Optional[str] = None) -> Optional[Path]:
    if explicit:
        return Path(explicit).expanduser().resolve()
    env = os.environ.get("AUDIOML_WORKSPACE")
    if env:
        return Path(env).expanduser().resolve()
    marker = ROOT
    while marker != marker.parent:
        if (marker / "adapters" / "README.md").is_file():
            return marker
        marker = marker.parent
    return None


def check_sources(workspace: Optional[str] = None) -> Dict[str, Any]:
    """Verify every SOURCES.sha256 pin against the pinned roots."""
    pins = parse_sources((ROOT / SOURCES).read_text(encoding="ascii"))
    root = find_workspace(workspace)
    problems: List[str] = []
    checked = 0
    for location, expected in sorted(pins.items()):
        prefix, relative = location.split(":", 1)
        if prefix == "workspace" and root is None:
            problems.append("workspace root unavailable: " + location)
            continue
        path = (root / relative) if prefix == "workspace" else (ROOT / relative)
        if not path.is_file():
            problems.append("missing pin: " + location)
            continue
        actual = sha256_bytes(path.read_bytes())
        if actual != expected:
            problems.append("digest mismatch: " + location)
            continue
        checked += 1
    contract = load_package_json(CONTRACT)
    for name, pin in contract["source_pins"].items():
        if "pkg_relative_path" in pin:
            location = "pkg:" + pin["pkg_relative_path"]
        else:
            location = "workspace:" + pin["workspace_relative_path"]
        if pins.get(location) != pin["sha256"]:
            problems.append("source pin not recorded: " + location + " (" + name + ")")
    return {
        "status": "ok" if not problems else "failed",
        "workspace": str(root) if root else "unavailable",
        "pins_total": len(pins),
        "pins_checked": checked,
        "problems": problems,
        "adapters_readme_sha256": pins.get("workspace:adapters/README.md"),
    }
