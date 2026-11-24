# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Frozen contract model and canonical report for task-local RAII evidence.

The report is developer-only ``tool`` evidence. It models ownership, lifetime
and caller-owned buffer rules from the pinned published C headers, records a
synthetic C harness parity check, and explicitly defers any native Rust build
or production exposure. No result here qualifies a processor, provider,
platform, workload or release.
"""

from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, List, Tuple

import fixture

ROOT = Path(__file__).resolve().parent
REPOSITORY_ROOT = ROOT.parents[2]
WORKSPACE_ROOT = ROOT.parents[5]

PROTOCOL = "sdk.raii-rust-c-bindings.evidence.v1"
TASK = "SDK-C-RAII-RUST-AND-C-BINDINGS"
COMPONENT = "c-raii-rust-and-c-bindings"
BASE_COMMIT = "503791ef555ee0385312923df38dce6c14628904"
STATUS = "proposal_only_not_qualified"
PROFILE = "tool"

STATUS_CODES = {
    "OK": 0,
    "INVALID_ARGUMENT": 1,
    "UNSUPPORTED": 2,
    "RESOURCE_EXHAUSTED": 3,
    "BACKEND_FAILURE": 4,
    "NEEDS_RESET": 5,
    "NOT_READY": 6,
    "END_OF_STREAM": 7,
    "BUSY": 8,
    "CLOSED": 9,
    "DUPLICATE": 10,
}

PINS: Tuple[Dict[str, str], ...] = (
    {
        "id": "cpp-library/bindings/README.md",
        "sha256": "239459d0b9a5027387f4bec55401c111c34882175789e4337d63d3fc4a2ab063",
        "use": "published language-binding contract summary (opaque handles, tagged structs, caller-owned buffers)",
    },
    {
        "id": "audio-sdk/api/include/audio_sdk/provider_v0.h",
        "sha256": "f168965ade4f342c8a222b15be625551789158891cab24f9ce135a583f2e1766",
        "use": "published provider ABI v0: tagged structs, status codes, registry and create config",
    },
    {
        "id": "audio-sdk/api/include/audio_sdk/session_v0.h",
        "sha256": "a81f9c74941b3a2e735f1b8f39f6ca0ea610818fc3c402fa2709c4d118fb0ca1",
        "use": "published session facade v0: load-time identity, create/process/close null-safe lifecycle",
    },
)

TOOL = {
    "python": "3.11.5 (pyenv shim; /Users/htsakanyan/.pyenv/versions/3.11.5)",
    "cmake": "3.27.4 (/Users/htsakanyan/.pyenv/shims/cmake)",
    "compiler": "Apple clang 21.0.0 (clang-2100.4.1.1), arm64-apple-darwin27.2.0",
    "reuse": "6.3.0, installed from PyPI with pip into a scratch venv outside the worktree",
    "reuse_install_command": "python3 -m venv <scratch>/craii-reuse-venv && <scratch>/craii-reuse-venv/bin/python -m pip install reuse==6.3.0 charset-normalizer",
    "rust": {
        "rustc": "not found in PATH at verification time",
        "cargo": "not found in PATH at verification time",
        "native_build": "DEFER",
        "reason": "no local Rust toolchain; no registry download or external install is used",
    },
    "network_use": "none for evidence generation; pinned files are read from the provided checkout",
}

BUILD_EVIDENCE = {
    "sdk_native_build_install_ctest": "11/11",
    "sdk_api_only_ctest": "1/1",
    "sdk_installed_fixture_provider_off_ctest": "1/1",
    "sdk_installed_fixture_provider_on_ctest": "1/1",
    "sdk_required_ctest": "11/11 native build/install; separate API-only and installed-consumer OFF/ON checks",
    "task_local_c_boundary_off_ctest": "1/1",
    "task_local_c_boundary_on_ctest": "1/1",
    "installed_consumer": "find_package(AudioSDK 0.1 CONFIG REQUIRED); AudioSDK::audio_sdk; installed public headers only",
    "separation": "compile/build proof, synthetic runtime proof and workload support are recorded separately",
}


def read_strict_json(path: Path) -> Dict[str, Any]:
    """Load a JSON object without duplicate keys, nonfinite constants or array roots."""
    def pairs(items: List[Tuple[str, Any]]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ValueError("duplicate_json_key:" + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ValueError("nonfinite_json_constant:" + token)

    value = json.loads(path.read_text(encoding="utf-8"),
                       object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(value, dict):
        raise ValueError("json_root_not_object")
    return value


def canonical_json(value: Dict[str, Any]) -> Tuple[str, str]:
    text = json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return text, hashlib.sha256(text.encode("utf-8")).hexdigest()


def canonical_report(report: Dict[str, Any]) -> Tuple[str, str]:
    return canonical_json(report)


def pin_paths() -> Dict[str, Path]:
    return {
        "cpp-library/bindings/README.md": WORKSPACE_ROOT / "cpp-library/bindings/README.md",
        "audio-sdk/api/include/audio_sdk/provider_v0.h":
            REPOSITORY_ROOT / "api/include/audio_sdk/provider_v0.h",
        "audio-sdk/api/include/audio_sdk/session_v0.h":
            REPOSITORY_ROOT / "api/include/audio_sdk/session_v0.h",
    }


def pin_records() -> List[Dict[str, str]]:
    return [
        {"id": pin["id"], "sha256": pin["sha256"], "use": pin["use"]}
        for pin in PINS
    ]


def expected_events(case: Dict[str, object]) -> List[str]:
    create_status = str(case["expected_create_status"])
    process_status = case["expected_process_status"]
    if case["case_id"] in {"missing_provider_selection", "unknown_provider"}:
        return [
            "registry_create:OK",
            "session_create:" + create_status,
            "registry_close:OK",
            "registry_close_double:OK",
        ]
    events = [
        "registry_create:OK",
        "effective_config_create:OK",
        "session_create:" + create_status,
    ]
    if process_status is not None:
        events.append("process:" + str(process_status))
        events.extend(["session_close:OK", "session_close_double:OK"])
    events.extend(["registry_close:OK", "registry_close_double:OK"])
    return events


def model_cases() -> List[Dict[str, Any]]:
    rows: List[Dict[str, Any]] = []
    for case in fixture.cases():
        row = dict(case)
        row["events"] = expected_events(case)
        rows.append(row)
    return rows


def model_canonical_text(rows: List[Dict[str, Any]] | None = None) -> str:
    selected = rows if rows is not None else model_cases()
    lines: List[str] = []
    for row in selected:
        process = row["expected_process_status"] or "-"
        lines.append("|".join((
            str(row["case_id"]),
            str(row["expected_create_status"]),
            str(process),
            str(row["input_digest"]),
            ",".join(row["events"]),
        )))
    return "\n".join(lines) + "\n"


def model_digest(rows: List[Dict[str, Any]] | None = None) -> str:
    return f"{fixture.fnv1a64(model_canonical_text(rows).encode('utf-8')):016x}"


def generated_header() -> str:
    """Generate the task-local C header; the SPDX token is built from parts."""
    spdx = "SPDX" "-License-Identifier: Apache-2.0"
    digest = fixture.input_digest()
    model = model_digest()
    return "\n".join((
        "/* SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes",
        " * " + spdx,
        " */",
        "/* Generated by reference.py via run.py --emit-header. Do not edit. */",
        "#ifndef AS_RAII_EVIDENCE_MODEL_H",
        "#define AS_RAII_EVIDENCE_MODEL_H",
        "",
        "#include <stdint.h>",
        "",
        '#define AS_RAII_EVIDENCE_PROTOCOL "' + PROTOCOL + '"',
        '#define AS_RAII_EVIDENCE_BASE_COMMIT "' + BASE_COMMIT + '"',
        '#define AS_RAII_EVIDENCE_PROVIDER_ID "speex.ns.v0"',
        "#define AS_RAII_EVIDENCE_FRAME_SAMPLES 160u",
        "#define AS_RAII_EVIDENCE_CASE_COUNT " + str(len(fixture.cases())) + "u",
        "#define AS_RAII_EVIDENCE_INPUT_DIGEST UINT64_C(0x" + digest.upper() + ")",
        "#define AS_RAII_EVIDENCE_MODEL_DIGEST UINT64_C(0x" + model.upper() + ")",
        "",
        "#endif /* AS_RAII_EVIDENCE_MODEL_H */",
        "",
    ))


def build_report() -> Dict[str, Any]:
    crosscheck_path = ROOT / "crosscheck.json"
    crosscheck = read_strict_json(crosscheck_path)
    harness_path = ROOT / "c_boundary/harness_output.json"
    harness_bytes = harness_path.read_bytes()
    cases = model_cases()
    return {
        "spdx": {
            "SPDX-FileCopyrightText": "2026 Tsakanyan Hovhannes",
            "SPDX" "-License-Identifier": "Apache-2.0",
        },
        "protocol": PROTOCOL,
        "task": TASK,
        "component": COMPONENT,
        "verification_profile": PROFILE,
        "base_commit": BASE_COMMIT,
        "status": STATUS,
        "decision": {
            "promotion": "defer",
            "proposal_only_not_qualified": True,
            "incomplete": True,
            "expose_as_processor": False,
            "registered": False,
            "default_enabled": False,
            "production_exposure": "DEFER",
        },
        "pins": pin_records(),
        "tool": TOOL,
        "installed_v0": {
            "sample_rate_hz": fixture.RATE_HZ,
            "channels": fixture.CHANNELS,
            "frame_samples": fixture.FRAME_SAMPLES,
            "sample_format": "float32",
            "abi_major": 0,
            "abi_minor": 1,
            "changed": False,
        },
        "public_boundary": {
            "api_abi_changed": False,
            "headers_changed": False,
            "descriptor_registry_changed": False,
            "provider_registration_changed": False,
            "installed_behavior": "unchanged",
            "cmake_target_added": False,
            "public_surface": "unchanged",
        },
        "fixture": fixture.fixture_pins(),
        "contract_model": {
            "case_count": len(cases),
            "cases": cases,
            "canonical_model_digest": model_digest(cases),
            "status_codes": STATUS_CODES,
            "ownership_rules": [
                "registry then session on acquire; session then registry on release",
                "as_session_close_v0 and as_registry_close_v0 null the caller pointer",
                "double close is null-safe and leaves the pointer NULL",
                "config_json, frame/input/output buffers and result are caller-owned",
                "borrowed library strings are copied before use and never freed",
            ],
        },
        "crosscheck": {
            "crosscheck_file": "crosscheck.json",
            "crosscheck_sha256": hashlib.sha256((ROOT / "crosscheck.json").read_bytes()).hexdigest(),
            "passed": crosscheck["summary"]["passed"],
            "case_count": crosscheck["summary"]["case_count"],
            "harness_output_file": "c_boundary/harness_output.json",
            "harness_output_sha256": hashlib.sha256(harness_bytes).hexdigest(),
            "kind": "synthetic C harness parity only; not a native Rust build or workload result",
        },
        "build_evidence": BUILD_EVIDENCE,
        "synthetic_runtime_evidence": {
            "kind": "task-local C11 harness against installed SDK headers and library",
            "provider": fixture.PROVIDER_ID,
            "mode": "AS_MODE_PROCESSING_THREAD (2)",
            "case_count": len(cases),
            "nonfinite_and_missing_controls": True,
            "native_rust_build": "DEFER",
        },
        "unclaimed_workload_support": [
            "no target-device latency, throughput, memory or availability measurement",
            "no real Rust crate registry download, cargo check, cargo build or Rust example run",
            "no C#/.NET build or runtime claim",
            "no speech quality, intelligibility, listening or model result",
            "no release, support, platform or production readiness claim",
            "no callback-safe (mode 1) or stable binary plugin ABI claim",
        ],
        "remaining_gates": [
            "exact-head independent review",
            "hosted CI on the exact branch head",
            "native Rust toolchain with pinned provenance before any Rust compile claim",
            "target-device workload and resource evidence before any workload claim",
            "release approval before any production exposure",
        ],
    }
