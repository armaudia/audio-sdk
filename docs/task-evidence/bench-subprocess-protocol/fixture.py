# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic, fully synthetic fixtures for the bridge-descriptor tool.

No file in this directory is read from disk at runtime except the three JSON
descriptors. Asset bytes, manifests, frames and result payloads are generated
from integer seeds and are never written to a workspace or attempt directory.
"""

from __future__ import annotations

import copy
import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

ROOT = Path(__file__).resolve().parent
_UNSET = object()
PROTOCOL = "audioml-adapter/1"
ASSET_ID = "synthetic.asset.frame-0001"
RIGHTS_REF = "synthetic://task-local-fixture"


def load_json(name: str) -> Dict[str, Any]:
    """Load a package JSON file with strict duplicate-key and nonfinite checks."""
    text = (ROOT / name).read_text(encoding="utf-8")

    def pairs(items: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate JSON key: " + key)
            result[key] = value
        return result

    def constant(token: str) -> Any:
        raise ValueError("nonfinite JSON constant: " + token)

    value = json.loads(text, object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(value, dict):
        raise ValueError("expected a JSON object: " + name)
    return value


def pseudo_bytes(seed: int, length: int) -> bytes:
    """Deterministic xorshift32 byte stream; no OS entropy or clock."""
    state = seed & 0xFFFFFFFF or 0x9E3779B9
    out = bytearray()
    while len(out) < length:
        state ^= (state << 13) & 0xFFFFFFFF
        state ^= state >> 17
        state ^= (state << 5) & 0xFFFFFFFF
        state &= 0xFFFFFFFF
        out.append(state & 0xFF)
    return bytes(out[:length])


def synthetic_asset(asset_id: str = ASSET_ID, size: int = 64, seed: int = 11) -> Dict[str, Any]:
    """Return a content-addressed synthetic asset record (bytes are implied)."""
    data = pseudo_bytes(seed, size)
    return {
        "asset_id": asset_id,
        "location": "/caller/assets/" + asset_id + ".bin",
        "sha256": hashlib.sha256(data).hexdigest(),
        "byte_count": size,
        "rights_ref": RIGHTS_REF,
    }


def base_descriptor() -> Dict[str, Any]:
    return copy.deepcopy(load_json("adapter.json"))


def base_request(with_selection: bool = True) -> Dict[str, Any]:
    asset = synthetic_asset()
    manifest = pseudo_bytes(31, 96)
    frame = pseudo_bytes(41, 160 * 4)
    request: Dict[str, Any] = {
        "protocol_version": PROTOCOL,
        "request_id": "req-0001",
        "execution_mode": "buffered_worker",
        "frame": {
            "sample_rate_hz": 16000,
            "channels": 1,
            "dtype": "float32",
            "samples": 160,
            "data_digest": hashlib.sha256(frame).hexdigest(),
        },
        "input_manifest": {
            "location": "/caller/input/req-0001.manifest.json",
            "sha256": hashlib.sha256(manifest).hexdigest(),
            "byte_count": len(manifest),
        },
        "assets": [asset],
    }
    if with_selection:
        request["optional_selections"] = {"selection": "identity-pcm"}
    return request


def base_result(status: str = "ok", reason_code: str = "valid_synthetic_fixture") -> Dict[str, Any]:
    asset = synthetic_asset()
    payload = pseudo_bytes(53, 128)
    return {
        "protocol_version": PROTOCOL,
        "request_id": "req-0001",
        "status": status,
        "reason_code": reason_code,
        "result_manifest_digest": hashlib.sha256(payload).hexdigest(),
        "metrics": {
            "finite": True,
            "frames": 1,
            "samples": 160,
            "quality_score": 0.0,
        },
        "assets": [{
            "asset_id": asset["asset_id"],
            "sha256": asset["sha256"],
            "byte_count": asset["byte_count"],
        }],
    }


def case(
    case_id: str,
    category: str,
    expected_status: str,
    expected_reason: str,
    note: str,
    descriptor: Optional[Dict[str, Any]] = None,
    request: Optional[Dict[str, Any]] = None,
    result: Any = _UNSET,
    request_text: Optional[str] = None,
) -> Dict[str, Any]:
    return {
        "case_id": case_id,
        "category": category,
        "expected_status": expected_status,
        "expected_reason": expected_reason,
        "note": note,
        "descriptor": base_descriptor() if descriptor is None else descriptor,
        "request": base_request() if request is None else request,
        "result": base_result() if result is _UNSET else result,
        "request_text": request_text,
    }


def valid_request_text(request: Dict[str, Any]) -> str:
    return json.dumps(request, sort_keys=True, separators=(",", ":"), allow_nan=False)


def _duplicate_key_text() -> str:
    text = valid_request_text(base_request())
    needle = '"request_id":"req-0001"'
    if needle not in text:
        raise AssertionError("fixture template changed")
    return text.replace(needle, needle + ',' + needle, 1)


def _nonfinite_json_text() -> str:
    request = base_request()
    request["diagnostic"] = 0.0
    text = valid_request_text(request)
    return text.replace('"diagnostic":0.0', '"diagnostic":NaN', 1)


def build_fixture(case_id: str) -> Dict[str, Any]:
    """Return one deep-copied fixture; callers may mutate it without side effects."""
    fixtures = _all_cases()
    if case_id not in fixtures:
        raise KeyError("unknown fixture case: " + case_id)
    return copy.deepcopy(fixtures[case_id])


def fixture_ids() -> Tuple[str, ...]:
    return tuple(_all_cases().keys())


def _all_cases() -> Dict[str, Dict[str, Any]]:
    descriptor = base_descriptor()
    request = base_request()
    result = base_result()

    no_optional = base_request(with_selection=False)
    valid_omitted_result = base_result("ok_omitted", "optional_selection_omitted")

    unsupported_protocol = base_request()
    unsupported_protocol["protocol_version"] = "audioml-adapter/2"

    duplicate_asset = base_request()
    duplicate_asset["assets"].append(copy.deepcopy(duplicate_asset["assets"][0]))

    bad_hash = base_request()
    bad_hash["assets"][0]["sha256"] = "00" * 32

    bad_count = base_request()
    bad_count["assets"][0]["byte_count"] = 63

    path_escape = base_request()
    path_escape["assets"][0]["location"] = "/caller/assets/../../etc/passwd"

    no_rights = base_request()
    del no_rights["assets"][0]["rights_ref"]

    request_in_attempt = base_request()
    request_in_attempt["input_manifest"]["location"] = "/attempt/caller-owned-request/input.json"

    write_escape = base_descriptor()
    write_escape["writable_roots"].append("/workspace")

    missing_grant = base_descriptor()
    missing_grant["read_grants"].remove("/caller/input")

    network = base_descriptor()
    network["deny_network"] = False

    downloads = base_descriptor()
    downloads["downloads"] = "allowed"

    nested = base_descriptor()
    nested["nested_sandbox_policy"] = "allow"

    production_callback = base_descriptor()
    production_callback["production_callback"] = "registered"

    nonfinite_frame = base_request()
    nonfinite_frame["frame"]["example_sample"] = float("nan")

    wrong_samples = base_request()
    wrong_samples["frame"]["samples"] = 159

    wrong_rate = base_request()
    wrong_rate["frame"]["sample_rate_hz"] = 48000

    empty_id = base_request()
    empty_id["request_id"] = ""

    inline_mode = base_request()
    inline_mode["execution_mode"] = "inline_callback"

    stale_digest = base_request()
    stale_digest["descriptor_digest"] = "00" * 32

    download_request = base_request()
    download_request["download_assets"] = True

    null_optional = base_request()
    null_optional["optional_selections"] = {"selection": None}

    unknown_optional = base_request()
    unknown_optional["optional_selections"] = {"selection": "model-inference"}

    missing_status = base_result()
    del missing_status["status"]

    bad_result_digest = base_result()
    bad_result_digest["result_manifest_digest"] = "11" * 32

    bad_result_asset = base_result()
    bad_result_asset["assets"][0]["asset_id"] = "synthetic.asset.unknown"

    nonfinite_metric = base_result()
    nonfinite_metric["metrics"]["quality_score"] = float("inf")

    malformed_result = base_result()
    del malformed_result["result_manifest_digest"]

    blocked_result = base_result("blocked", "nested_sandbox_denied")

    cases: Dict[str, Dict[str, Any]] = {
        "valid_with_optional": case(
            "valid_with_optional", "valid", "ok", "valid_synthetic_fixture",
            "Explicit optional selection, complete valid descriptor/request/result.",
            descriptor, request, result),
        "valid_without_optional": case(
            "valid_without_optional", "missing_optional", "ok_omitted",
            "optional_selection_omitted",
            "Optional selection omitted; no default is inferred.",
            descriptor, no_optional, valid_omitted_result),
        "unsupported_protocol": case(
            "unsupported_protocol", "malformed", "rejected", "unsupported_protocol",
            "Unknown protocol version fails closed.",
            descriptor, unsupported_protocol, result),
        "duplicate_json_key": case(
            "duplicate_json_key", "malformed", "rejected", "strict_json_duplicate_key",
            "Strict JSON parser rejects a duplicate request_id key.",
            descriptor, request, result, request_text=_duplicate_key_text()),
        "nonfinite_json_constant": case(
            "nonfinite_json_constant", "nonfinite", "rejected", "strict_json_nonfinite",
            "Strict JSON parser rejects a NaN constant.",
            descriptor, request, result, request_text=_nonfinite_json_text()),
        "nonfinite_frame_value": case(
            "nonfinite_frame_value", "nonfinite", "rejected", "nonfinite_value",
            "Nonfinite frame value rejected before canonicalization.",
            descriptor, nonfinite_frame, result),
        "asset_sha_mismatch": case(
            "asset_sha_mismatch", "asset", "rejected", "asset_hash_mismatch",
            "Declared asset hash differs from synthetic content digest.",
            descriptor, bad_hash, result),
        "asset_byte_count_mismatch": case(
            "asset_byte_count_mismatch", "asset", "rejected", "asset_byte_count_mismatch",
            "Declared byte count differs from synthetic content length.",
            descriptor, bad_count, result),
        "duplicate_asset_id": case(
            "duplicate_asset_id", "asset", "rejected", "duplicate_asset_id",
            "Two assets share an immutable asset ID.",
            descriptor, duplicate_asset, result),
        "asset_path_escape": case(
            "asset_path_escape", "asset", "rejected", "asset_location_not_granted",
            "Asset path traversal leaves the explicit read grants.",
            descriptor, path_escape, result),
        "asset_missing_rights_ref": case(
            "asset_missing_rights_ref", "missing_optional", "rejected",
            "asset_rights_ref_missing",
            "Rights reference is not optional for a declared asset.",
            descriptor, no_rights, result),
        "input_manifest_in_attempt_dir": case(
            "input_manifest_in_attempt_dir", "sandbox", "rejected",
            "input_manifest_inside_attempt_dir",
            "Caller-owned manifest may not live in the writable attempt directory.",
            descriptor, request_in_attempt, result),
        "writable_root_escape": case(
            "writable_root_escape", "sandbox", "rejected", "writable_root_escape",
            "Writable roots must contain only the attempt directory.",
            write_escape, request, result),
        "read_grant_missing": case(
            "read_grant_missing", "sandbox", "rejected", "read_grant_missing",
            "A required caller-owned input root has no explicit read grant.",
            missing_grant, request, result),
        "network_allowed": case(
            "network_allowed", "sandbox", "rejected", "network_not_denied",
            "Network denial is mandatory.",
            network, request, result),
        "downloads_allowed": case(
            "downloads_allowed", "sandbox", "rejected", "downloads_not_denied",
            "Adapter must not download assets.",
            downloads, request, result),
        "nested_sandbox_allowed": case(
            "nested_sandbox_allowed", "sandbox", "rejected", "nested_policy_not_fail_closed",
            "Nested Seatbelt profiles must fail closed.",
            nested, request, result),
        "production_callback_declared": case(
            "production_callback_declared", "boundary", "rejected",
            "production_callback_not_none",
            "Evaluation execution must not declare a production callback.",
            production_callback, request, result),
        "wrong_frame_samples": case(
            "wrong_frame_samples", "malformed", "rejected", "frame_samples_mismatch",
            "Fixed v0 frame is 160 samples.",
            descriptor, wrong_samples, result),
        "wrong_sample_rate": case(
            "wrong_sample_rate", "malformed", "rejected", "sample_rate_mismatch",
            "Fixed v0 rate is 16 kHz.",
            descriptor, wrong_rate, result),
        "empty_request_id": case(
            "empty_request_id", "malformed", "rejected", "request_id_invalid",
            "Request ID must be a nonempty token derived by the caller.",
            descriptor, empty_id, result),
        "inline_callback_mode": case(
            "inline_callback_mode", "boundary", "rejected", "execution_mode_unsupported",
            "Production callback modes are outside the tool boundary.",
            descriptor, inline_mode, result),
        "stale_descriptor_digest": case(
            "stale_descriptor_digest", "malformed", "rejected", "descriptor_digest_mismatch",
            "A supplied descriptor digest must match the descriptor bytes.",
            descriptor, stale_digest, result),
        "download_requested": case(
            "download_requested", "sandbox", "rejected", "download_requested",
            "A request may not ask the adapter to fetch assets.",
            descriptor, download_request, result),
        "null_optional_selection": case(
            "null_optional_selection", "missing_optional", "rejected",
            "optional_selection_null",
            "Explicit null selection is not an omitted selection.",
            descriptor, null_optional, result),
        "unknown_optional_selection": case(
            "unknown_optional_selection", "missing_optional", "rejected",
            "optional_selection_unknown",
            "Unknown optional selection fails closed.",
            descriptor, unknown_optional, result),
        "missing_result": case(
            "missing_result", "incomplete", "incomplete", "result_missing",
            "A missing result never qualifies a candidate.",
            descriptor, request, None),
        "result_missing_status": case(
            "result_missing_status", "malformed", "rejected", "result_field_missing",
            "Result status is required.",
            descriptor, request, missing_status),
        "result_manifest_digest_invalid": case(
            "result_manifest_digest_invalid", "malformed", "rejected",
            "result_digest_mismatch",
            "A result manifest digest must match the synthetic payload.",
            descriptor, request, bad_result_digest),
        "result_asset_unknown": case(
            "result_asset_unknown", "asset", "rejected", "result_asset_unknown",
            "A result may not introduce an unverified asset ID.",
            descriptor, request, bad_result_asset),
        "nonfinite_result_metric": case(
            "nonfinite_result_metric", "nonfinite", "rejected", "nonfinite_value",
            "Nonfinite result metrics are rejected.",
            descriptor, request, nonfinite_metric),
        "malformed_result_manifest": case(
            "malformed_result_manifest", "malformed", "rejected", "result_field_missing",
            "Result manifest digest is required.",
            descriptor, request, malformed_result),
        "blocked_nested_sandbox": case(
            "blocked_nested_sandbox", "sandbox", "blocked", "nested_sandbox_denied",
            "A nested sandbox block is explicit and never qualifies.",
            descriptor, request, blocked_result),
    }
    return cases
