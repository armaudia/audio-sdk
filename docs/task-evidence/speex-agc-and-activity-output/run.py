# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Task-local Speex AGC + advisory activity reference entrypoint.

Three modes:

* ``--report``   rebuild the canonical report from the exact pinned sources and
                 require a byte-identical match with the stored report.
* ``--validate`` strict JSON/schema validation of the stored frozen report.
* ``--request``/``--result``  protocol-v1-shaped inspect/run envelope mirroring
                 the harness-controls adapter boundary. This adapter is
                 unregistered and developer-only; it is not an audio-bench
                 result and it is not an SDK provider.

No corpus, model, weights, download, real audio, device, listening or pacing
claim is involved. The native DSP is built only into private scratch space.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
from pathlib import Path
import re
import struct
import subprocess
import sys
import tempfile

TASK = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK / "tools"))
import common as c
import fixtures as f

ADAPTER_ID = "speex-agc-activity-reference-v1"
COMMON_FIELDS = {"protocol_version", "operation", "candidate_ref", "adapter_ref", "configuration"}
RUN_FIELDS = COMMON_FIELDS | {"attempt_id", "stimulus_id", "reset_frames", "stimulus_samples"}
REQUIRED_TOP_LEVEL = {
    "schema", "task", "status", "claim_level", "base_commit", "base_parent", "branch",
    "verification", "scope", "adapter", "stimuli", "cases", "controls",
    "acceptance_profile_coverage", "remaining_release_gates", "environment",
}
SHA256_RE = re.compile(r"^[0-9a-f]{64}$")


class RequestError(ValueError):
    pass


def read_strict(path: Path):
    return c.read_strict(Path(path))


def validate_report(report: dict) -> None:
    """Strict structural and cross-reference validation of the frozen report."""
    if not isinstance(report, dict):
        raise RequestError("report_not_object")
    if set(report) != REQUIRED_TOP_LEVEL:
        raise RequestError("report_field_set_mismatch")
    if report["schema"] != c.SCHEMA or report["task"] != c.TASK_ID:
        raise RequestError("report_identity_mismatch")
    if report["base_commit"] != c.BASE_COMMIT:
        raise RequestError("report_base_commit_mismatch")
    if report["claim_level"] != "synthetic_evidence_only":
        raise RequestError("report_claim_level_mismatch")
    if not report["status"].startswith("proposal_only_synthetic"):
        raise RequestError("report_status_mismatch")

    scope = report["scope"]
    for key in ("public_api_changed", "abi_changed", "default_provider_changed",
                "provider_registry_changed", "shared_cmake_modified",
                "installed_speex_v0_behavior_changed", "activity_gates_audio",
                "real_audio_used", "corpus_model_weights_download_used",
                "listening_quality_device_or_pacing_claim", "public_benchmark_claim",
                "tiny16_comparison_claim"):
        if scope.get(key) is not False:
            raise RequestError("scope_false_field:" + key)
    for key in ("activity_advisory_only",):
        if scope.get(key) is not True:
            raise RequestError("scope_true_field:" + key)
    if scope.get("shared_sources_modified") != [] or scope.get("shared_build_targets_added") != []:
        raise RequestError("scope_shared_changes_nonempty")
    if scope.get("assets_or_reports_outside_task_dir") != []:
        raise RequestError("scope_outside_writes_nonempty")

    adapter = report["adapter"]
    if adapter.get("protocol_version") != 1 or adapter.get("identity") != ADAPTER_ID:
        raise RequestError("adapter_identity_mismatch")
    if adapter.get("registration") != "unregistered-developer-only":
        raise RequestError("adapter_registration_mismatch")
    if adapter.get("default_enabled") is not False or adapter.get("preprocessor_instances_per_stream") != 1:
        raise RequestError("adapter_geometry_mismatch")
    pins = adapter.get("source_pins")
    if not isinstance(pins, list) or not pins:
        raise RequestError("source_pins_missing")
    for pin in pins:
        if set(pin) != {"scope", "path", "sha256", "observed_sha256", "status"}:
            raise RequestError("source_pin_fields")
        if not SHA256_RE.fullmatch(pin["sha256"]) or pin["status"] != "match":
            raise RequestError("source_pin_not_matched:" + pin["path"])
    if len({pin["path"] for pin in pins}) != len(pins):
        raise RequestError("duplicate_source_pins")

    cases = report["cases"]
    if not isinstance(cases, list) or len(cases) != 23:
        raise RequestError("case_count_mismatch")
    seen = set()
    for item in cases:
        if set(item) != {"id", "stimulus", "control", "config", "input", "output", "repeats"}:
            raise RequestError("case_field_set:" + str(item.get("id")))
        if item["id"] in seen or item["stimulus"] not in f.GENERATORS or item["control"] not in c.CONTROLS:
            raise RequestError("case_identity:" + str(item.get("id")))
        seen.add(item["id"])
        reps = item["repeats"]
        if reps.get("count") != c.REPEATS or reps.get("status") != "byte_identical":
            raise RequestError("case_repeats:" + item["id"])
        if len(set(reps["output_sha256"])) != 1 or len(set(reps["meta_sha256"])) != 1:
            raise RequestError("case_repeat_digests:" + item["id"])
        out = item["output"]
        if set(out) != {"sha256", "bytes", "metrics", "activity", "meta_sha256"}:
            raise RequestError("case_output_fields:" + item["id"])
        for value in (item["input"]["sha256"], out["sha256"], out["meta_sha256"]):
            if not SHA256_RE.fullmatch(value):
                raise RequestError("case_bad_digest:" + item["id"])
        if out["metrics"]["samples"] != c.SAMPLES or out["bytes"] != c.SAMPLES * 4:
            raise RequestError("case_length:" + item["id"])
        if out["metrics"]["nonfinite_count"] != 0 or out["metrics"]["peak_abs"] > 1.0:
            raise RequestError("case_numerics:" + item["id"])
        activity = out["activity"]
        if len(activity["advisory_vad_sequence"]) != c.SAMPLES // c.FRAME:
            raise RequestError("case_activity_frames:" + item["id"])
        if any(flag not in (0, 1) for flag in activity["advisory_vad_sequence"]):
            raise RequestError("case_activity_values:" + item["id"])
        if len(activity["agc_gain_db_sequence"]) != c.SAMPLES // c.FRAME:
            raise RequestError("case_gain_frames:" + item["id"])

    nonfinite = report["controls"].get("fail_closed_nonfinite", {})
    if nonfinite.get("status") != "pass" or nonfinite.get("observed_exit") != 3:
        raise RequestError("nonfinite_control_not_pass")
    if report["controls"].get("identity_delay_samples") != report["controls"].get("combined_delay_samples"):
        raise RequestError("delay_controls_disagree")
    if not report["remaining_release_gates"]:
        raise RequestError("release_gates_missing")
    if report["verification"].get("read_only") is not True or report["verification"].get("check_exit") != 0:
        raise RequestError("verification_not_read_only_or_failed")


def regenerate_report() -> dict:
    """Build the report into a private temp path and return its bytes + digest."""
    with tempfile.TemporaryDirectory(prefix="speex-activity-report-") as tmp:
        out = Path(tmp) / "report.json"
        env = dict(os.environ)
        env["SPEEX_ACTIVITY_REPORT_PATH"] = str(out)
        proc = subprocess.run([sys.executable, str(TASK / "tools/build_report.py")],
                              env=env, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RequestError("report_build_failed:" + proc.stderr.strip())
        raw = out.read_bytes()
    return {"bytes": raw, "sha256": hashlib.sha256(raw).hexdigest()}


def ensure_cli() -> Path:
    build = Path(os.environ.get(
        "SPEEX_ACTIVITY_CLI_BUILD",
        str(Path(tempfile.gettempdir()) / "speex-agc-activity-cli-build")))
    cli = build / "speexagc_activity_cli"
    if cli.is_file():
        return cli
    build.mkdir(parents=True, exist_ok=True)
    for command in (
        ["cmake", "-S", str(TASK / "adapter"), "-B", str(build),
         "-DCMAKE_BUILD_TYPE=Release", "-DAS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE=ON"],
        ["cmake", "--build", str(build), "--parallel", "4"],
    ):
        proc = subprocess.run(command, capture_output=True, text=True, check=False)
        if proc.returncode != 0:
            raise RequestError("native_build_failed:" + proc.stderr.strip())
    if not cli.is_file():
        raise RequestError("native_cli_missing")
    return cli


def validate_ref(ref: dict, name: str) -> None:
    if not isinstance(ref, dict) or set(ref) != {"kind", "id", "revision"}:
        raise RequestError("invalid_" + name)
    if not isinstance(ref["id"], str) or not ref["id"]:
        raise RequestError("invalid_" + name)
    if isinstance(ref["revision"], bool) or not isinstance(ref["revision"], int) or ref["revision"] < 1:
        raise RequestError("invalid_" + name)


def validate_request(request: dict, operation: str) -> dict:
    if not isinstance(request, dict):
        raise RequestError("request_not_object")
    required = COMMON_FIELDS if operation == "inspect" else RUN_FIELDS
    if set(request) - required or not required <= set(request):
        raise RequestError("invalid_request_fields")
    if request["protocol_version"] != 1 or request["operation"] != operation:
        raise RequestError("invalid_protocol_or_operation")
    for name in ("candidate_ref", "adapter_ref"):
        validate_ref(request[name], name)
    config = request["configuration"]
    if not isinstance(config, dict):
        raise RequestError("configuration_not_object")
    control = config.get("control")
    if control not in c.CONTROLS:
        raise RequestError("unknown_control")
    allowed = {"control"} | set(c.DEFAULT_CONFIG)
    if set(config) - allowed:
        raise RequestError("unexpected_configuration_keys")
    if operation == "inspect":
        return config
    if not isinstance(request["attempt_id"], str) or not request["attempt_id"]:
        raise RequestError("invalid_attempt_id")
    if not isinstance(request["stimulus_id"], str):
        raise RequestError("invalid_stimulus_id")
    resets = request["reset_frames"]
    if (not isinstance(resets, list) or any(isinstance(v, bool) or not isinstance(v, int)
                                             or v < 0 for v in resets)):
        raise RequestError("invalid_reset_frames")
    override = request["stimulus_samples"]
    if override is not None:
        if (not isinstance(override, list) or len(override) % c.FRAME or
                any(isinstance(v, bool) or not isinstance(v, (int, float)) or not math.isfinite(v)
                    or abs(v) > 1.0 for v in override)):
            raise RequestError("invalid_stimulus_samples")
    return config


def inspect(request: dict) -> dict:
    config = validate_request(request, "inspect")
    return {
        "protocol_version": 1,
        "operation": "inspect",
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "identity": ADAPTER_ID,
        "configuration": config,
        "requested_control": config["control"],
        "supported_controls": list(c.CONTROLS),
        "supported_tasks": [],
        "supported_modes": ["offline"],
        "supported_formats": ["mono 16 kHz float32, 160-sample frames"],
        "asset_readiness": [],
        "registration": "unregistered developer-only fixture; not an audio-bench result",
        "activity_is_advisory": True,
        "preprocessor_instances_per_stream": 1,
    }


def run(request: dict) -> dict:
    config = validate_request(request, "run")
    control = config["control"]
    cfg = dict(c.CASES[0]["config"])
    for key in c.DEFAULT_CONFIG:
        if key in config:
            cfg[key] = config[key]
    cfg.update(c.CONTROLS[control])
    for key, value in config.items():
        if key in c.CONTROLS[control]:
            cfg[key] = value
    cfg["reset_frames"] = list(request["reset_frames"])

    override = request["stimulus_samples"]
    if override is not None:
        samples = [float(v) for v in override]
        stimulus_id = "caller_samples"
        stimulus_sha = c.digest_bytes(f.f32_bytes(samples))
    else:
        stimuli = f.all_stimuli()
        if request["stimulus_id"] not in stimuli:
            raise RequestError("unknown_stimulus_id:" + request["stimulus_id"])
        samples = stimuli[request["stimulus_id"]]
        stimulus_id = request["stimulus_id"]
        stimulus_sha = c.digest_bytes(f.f32_bytes(samples))
    if len(samples) % c.FRAME:
        raise RequestError("stimulus_not_frame_aligned")

    cli = ensure_cli()
    with tempfile.TemporaryDirectory(prefix="speex-activity-run-") as tmp:
        work = Path(tmp)
        stimulus = work / "stimulus.f32"
        stimulus.write_bytes(f.f32_bytes(samples))
        result = c.run_cli(cli, work, stimulus, cfg, "call", 0)
        raw = result["output_bytes"]
    values = struct.unpack("<" + str(len(raw) // 4) + "f", raw)
    finite = all(math.isfinite(v) for v in values)
    output = {
        "sample_count": len(values),
        "byte_count": len(raw),
        "samples_sha256": c.digest_bytes(raw),
        "nonfinite_count": 0 if finite else sum(1 for v in values if not math.isfinite(v)),
        "peak_abs": round(max((abs(v) for v in values if math.isfinite(v)), default=0.0), 6),
        "advisory_activity": result["records"],
        "meta_sha256": c.digest_bytes(result["meta_bytes"]),
    }
    if finite:
        output["samples"] = list(values)
    return {
        "protocol_version": 1,
        "operation": "run",
        "attempt_id": request["attempt_id"],
        "candidate_ref": request["candidate_ref"],
        "adapter_ref": request["adapter_ref"],
        "configuration": config,
        "control": control,
        "stimulus_id": stimulus_id,
        "stimulus_sha256": stimulus_sha,
        "reset_frames": request["reset_frames"],
        "status": "complete" if finite else "adverse_numerical",
        "errors": [] if finite else [{"kind": "adverse_numerical", "reason": "nonfinite_output"}],
        "output": output,
        "registration": "unregistered developer-only fixture; not an audio-bench result",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--report", action="store_true", help="rebuild and byte-compare report.json")
    parser.add_argument("--validate", action="store_true", help="strictly validate stored report.json")
    parser.add_argument("--request", help="protocol-v1 request JSON path")
    parser.add_argument("--result", help="protocol-v1 result JSON output path")
    args = parser.parse_args()
    modes = int(args.report) + int(args.validate) + int(args.request is not None)
    if modes != 1:
        print("select exactly one of --report, --validate or --request", file=sys.stderr)
        return 2
    try:
        if args.report:
            stored = c.REPORT_PATH.read_bytes()
            rebuilt = regenerate_report()
            match = rebuilt["bytes"] == stored
            print("stored_report_sha256=" + hashlib.sha256(stored).hexdigest())
            print("rebuilt_report_sha256=" + rebuilt["sha256"])
            print("byte_identical=" + ("true" if match else "false"))
            return 0 if match else 1
        if args.validate:
            doc = read_strict(c.REPORT_PATH)
            validate_report(doc)
            if c.canonical_bytes(doc) != c.REPORT_PATH.read_bytes():
                raise RequestError("report_not_canonical")
            print("report_valid=true")
            print("report_sha256=" + hashlib.sha256(c.REPORT_PATH.read_bytes()).hexdigest())
            return 0
        if not args.result:
            raise RequestError("--result is required with --request")
        request = read_strict(args.request)
        if not isinstance(request, dict) or request.get("operation") not in ("inspect", "run"):
            raise RequestError("unknown_operation")
        result = inspect(request) if request["operation"] == "inspect" else run(request)
        path = Path(args.result)
        path.parent.mkdir(parents=True, exist_ok=True)
        temp = path.with_name(path.name + ".tmp")
        temp.write_bytes(c.canonical_bytes(result))
        os.replace(temp, path)
        return 0
    except (RequestError, c.StrictError, KeyError, TypeError, ValueError, OSError) as error:
        print(str(error) or error.__class__.__name__, file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
