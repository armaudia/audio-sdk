# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Every check fails closed: missing or stale pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, disposition drift, a promoted missing
result, a stale README digest table, licensing gaps or any out-of-scope worktree
change is a hard failure.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = reference.TASK_PREFIX
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"

EXPECTED_REASONS = [
    "model_revision_unpinned",
    "download_revision_mutable",
    "asset_bytes_absent",
    "runtime_unavailable",
    "rights_not_cleared",
]
EXPECTED_GATES = {
    "exact_asset_identity", "runtime_admission", "artifact_rights",
    "exact_reference_parity", "rights_cleared_cohort",
    "independent_scoring_and_listening", "target_runtime_timing",
    "provider_intake", "public_default_selection",
}
EXPECTED_VARIANTS = {
    "identity_passthrough", "noisy_control", "surrogate_whole_clip",
    "surrogate_frame_loop_control", "surrogate_split_halves",
}
EXPECTED_CONFIGS = {
    "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
    "wrong_frame_samples", "wrong_max_clip_samples", "streaming_mode_unsupported",
    "surrogate_without_opt_in", "caller_asset_unavailable",
    "caller_asset_admission_control",
}
EXPECTED_CLIPS = {
    "second_clip", "empty_clip", "oversized_clip", "nonfinite_sample",
    "infinite_sample", "string_clip", "boolean_sample", "out_of_range_sample",
    "after_close",
}
README_DIGEST_FILES = (
    "adapter.json",
    "check_licensing.py",
    "readiness.json",
    "reference.py",
    "report.json",
    "run.py",
    "test_reference.py",
    "verify.py",
)
README_ROW = re.compile(r"^\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|$")
README_HEADER = "| Path | SHA-256 | Bytes |"


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key in " + path.name + ": " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail("nonfinite JSON constant in " + path.name + ": " + token)

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        fail("JSON root is not an object: " + path.name)
    check_finite(value, path.name)
    return value


def read_manifest() -> dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != cli.MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  ([^\s]+(?:\s[^\s]+)*)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set[str]:
    local = {f"worktree:{TASK_PREFIX}{name}" for name in reference.LOCAL_FILES}
    return ({f"source:{name}" for name in reference.SOURCE_PINS}
            | {f"worktree:{name}" for name in reference.BOUNDARY_PINS}
            | local)


def check_pins(manifest: dict[str, str]) -> None:
    expected = manifest_expected_paths()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if f"worktree:{TASK_PREFIX}SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for raw, digest in sorted(manifest.items()):
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            fail("unsupported pin prefix: " + raw)
        if not path.is_file() or path.is_symlink():
            fail("missing or non-regular pin target: " + raw)
        if reference.sha256_file(path) != digest:
            fail("pin mismatch: " + raw)
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact")


def readme_digest_pins() -> dict[str, tuple[str, int]]:
    """Parse and validate the README digest table against the files on disk."""
    try:
        text = (HERE / "README.md").read_text(encoding="utf-8")
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read README.md: " + str(error))
    lines = text.splitlines()
    try:
        start = lines.index("## Expected counts and digests")
    except ValueError:
        fail("README is missing the Expected counts and digests section")
    header_index = None
    for index in range(start + 1, len(lines)):
        if lines[index].strip() == README_HEADER:
            header_index = index
            break
    if header_index is None:
        fail("README digest table header missing")
    rows: dict[str, tuple[str, int]] = {}
    index = header_index + 1
    if index >= len(lines) or not lines[index].startswith("| ---"):
        fail("README digest table separator missing")
    index += 1
    while index < len(lines) and lines[index].startswith("|"):
        match = README_ROW.match(lines[index])
        if match is None:
            fail("malformed README digest row: " + repr(lines[index]))
        name, digest, size = match.group(1), match.group(2), int(match.group(3))
        if name in rows:
            fail("duplicate README digest row: " + name)
        rows[name] = (digest, size)
        index += 1
    if set(rows) != set(README_DIGEST_FILES):
        fail("README digest row set mismatch: missing="
             + str(sorted(set(README_DIGEST_FILES) - set(rows)))
             + " extra=" + str(sorted(set(rows) - set(README_DIGEST_FILES))))
    for name in README_DIGEST_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            fail("README digest target missing or non-regular: " + name)
        observed = reference.sha256_file(path)
        expected_digest, expected_size = rows[name]
        if observed != expected_digest:
            fail("README digest is stale for " + name + ": " + expected_digest
                 + " != " + observed)
        if path.stat().st_size != expected_size:
            fail("README byte count is stale for " + name + ": "
                 + str(expected_size) + " != " + str(path.stat().st_size))
    print(f"verify: README digest table exact for {len(rows)} artifacts")
    return rows


def check_disposition(contract: dict[str, Any], adapter: dict[str, Any],
                      readiness: dict[str, Any]) -> None:
    for name, document in (("contract", contract), ("adapter", adapter),
                           ("readiness", readiness)):
        if document.get("decision") != reference.DECISION:
            fail(name + " decision is not DEFER")
    if contract.get("status") != reference.STATUS:
        fail("contract status mismatch")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("contract qualification status mismatch")
    qualification = contract["qualification"]
    required = {
        "status": reference.EVIDENCE_STATUS,
        "decision": reference.DECISION,
        "qualifies": False,
        "missing_result_promoted": False,
        "processor_exposure": False,
        "real_runtime_used": False,
        "quality_claim": False,
        "release_claim": False,
    }
    if any(qualification.get(key) != value for key, value in required.items()):
        fail("contract qualification is not incomplete/DEFER")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("public surface flag is not false")
    required_false = {key: value for key, value in reference.BOUNDARY.items()
                      if key not in ("descriptor_settings", "installed_v0_geometry_preserved")}
    if any(value is not False for value in required_false.values()):
        fail("boundary flag is not false")
    if reference.BOUNDARY["descriptor_settings"] != {}:
        fail("descriptor settings are not empty")
    if contract["boundary"] != reference.BOUNDARY:
        fail("contract boundary differs from the frozen boundary")
    if adapter["registration"] != {
        "registered": False, "enabled_by_default": False,
        "default_selected": False, "descriptor_registry_change": False,
        "public_api_abi_change": False,
    }:
        fail("adapter registration block is not fail-closed")
    for key in ("real_runtime_used", "weights_accessed", "quality_claim"):
        if adapter.get(key) is not False:
            fail("adapter claim flag is not false: " + key)
    if adapter["asset_readiness"] != "blocked":
        fail("adapter reports a ready asset")
    if adapter["modes"] != ["offline"]:
        fail("adapter modes drifted")
    if adapter["configuration"]["streaming_supported"] is not False:
        fail("adapter exposes streaming")
    if adapter["configuration"]["whole_clip_only"] is not True:
        fail("adapter is not whole-clip only")
    if readiness["status"] != "blocked" or readiness["qualified"] is not False:
        fail("readiness is not blocked/not qualified")
    if readiness["admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("readiness reason codes drifted")
    if readiness["admission"]["status"] != "blocked":
        fail("readiness admission is not blocked")
    for key in ("download_attempted", "vendor_runtime_invoked", "asset_bytes_read"):
        if readiness["admission"][key] is not False:
            fail("readiness admission performed a forbidden action: " + key)
    for token in ("not ready", "dpdfnet 0.6.0", "revision is not immutable"):
        if token not in readiness["readiness_conclusion"]:
            fail("readiness conclusion is missing: " + token)
    print("verify: contract, adapter and readiness are blocked/DEFER and OFF")


def check_report(report: dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        fail("report base or branch mismatch")
    if report["task_id"] != reference.TASK or report["component"] != reference.SLUG:
        fail("report identity mismatch")
    if report["profile"] != reference.PROFILE:
        fail("report profile mismatch")
    if report["status"] != reference.STATUS:
        fail("report status mismatch")
    if report["evidence_status"] != reference.EVIDENCE_STATUS:
        fail("report evidence status mismatch")
    if report["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("report qualification status mismatch")
    if report["decision"] != reference.DECISION:
        fail("report decision is not DEFER")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("missing-result qualification guard is absent")
    if report["format"] != reference.FORMAT:
        fail("installed v0 geometry or offline format mismatch")
    if report["boundary"] != reference.BOUNDARY:
        fail("report boundary mismatch")
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")
    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for name, block in report["conditions"].items():
        variants = block["variants"]
        if set(variants) != EXPECTED_VARIANTS:
            fail("variant set mismatch in " + name)
        for variant in variants.values():
            if variant["nonfinite_samples"] != 0 or variant["clipped_samples"] != 0:
                fail("invalid output in condition " + name)
            if not math.isfinite(variant["peak_abs_output"]):
                fail("nonfinite peak in " + name)
        if variants["identity_passthrough"]["snr_db"] != variants["noisy_control"]["snr_db"]:
            fail("identity control is not exact in " + name)
        if variants["identity_passthrough"]["si_sdr_db"] != variants["noisy_control"]["si_sdr_db"]:
            fail("identity SI-SDR control is not exact in " + name)
        accounting = block["output_accounting"]
        if accounting["input_samples"] != accounting["output_samples"]:
            fail("offline output length differs from input in " + name)
        if accounting["output_samples"] != block["scored_samples"]:
            fail("scored prefix differs from output length in " + name)
        if accounting["startup_padding_samples"] != 0:
            fail("startup padding in offline mode: " + name)
        if accounting["tail_padding_emitted_samples"] != 0:
            fail("tail padding emitted in offline mode: " + name)
        if accounting["flush_required"] is not False:
            fail("flush required in offline mode: " + name)
        if accounting["algorithmic_lag_samples"] != 0:
            fail("algorithmic lag in offline mode: " + name)
        if not block["frame_loop_matches_whole"]:
            fail("frame loop differs from whole clip in " + name)
        if block["split_halves_matches_whole"]:
            fail("independent halves matched the whole clip in " + name)
    controls = report["controls"]
    if not controls["all_present"] or not controls["identity"]["exact_passthrough"]:
        fail("matched controls incomplete")
    if controls["candidate"]["real_candidate"] is not False:
        fail("surrogate is presented as the real candidate")
    if not report["regression_assessment"]["performed"]:
        fail("regression assessment was not performed")
    for item in report["regressions"]:
        if item["metric"] not in ("snr_db", "si_sdr_db"):
            fail("unknown regression metric")
        if item["surrogate_whole_clip"] >= item["noisy_control"]:
            fail("regression is not a regression")

    boundary = report["offline_boundary"]
    if boundary["sample_rate_hz"] != reference.SAMPLE_RATE_HZ:
        fail("sample rate mismatch")
    if boundary["channels"] != reference.CHANNELS:
        fail("channel count mismatch")
    if boundary["sample_format"] != reference.SAMPLE_FORMAT:
        fail("sample format mismatch")
    if boundary["frame_samples"] != reference.FRAME_SAMPLES:
        fail("frame size mismatch")
    if boundary["max_clip_samples"] != reference.MAX_CLIP_SAMPLES:
        fail("max clip mismatch")
    if boundary["processing_mode"] != "offline_whole_clip":
        fail("offline processing mode mismatch")
    if boundary["incremental_calls_supported"] is not False:
        fail("incremental calls are supported")
    if boundary["streaming_supported"] is not False:
        fail("streaming is supported")
    if boundary["flush_required"] is not False:
        fail("flush is required")
    if boundary["algorithmic_lag_samples"] != 0:
        fail("non-zero algorithmic lag")
    if boundary["lag_modelled"] is not False or boundary["lag_measured"] is not False:
        fail("lag is claimed")
    if boundary["clock_id"] != reference.CLOCK_ID:
        fail("fixture clock identity mismatch")
    causality = boundary["causality"]
    if causality["requires_complete_clip"] is not True:
        fail("complete-clip requirement is not shown")
    if causality["prefix_samples_changed_by_future_audio"] <= 0:
        fail("future audio did not change the prefix")
    if causality["prefix_available_before_full_clip"] is not False:
        fail("prefix is claimed available before the full clip")
    split = boundary["split_clip_control"]
    if split["split_matches_whole"] is not False:
        fail("split halves matched the whole clip")
    if split["differing_samples"] <= 0:
        fail("split control recorded no difference")
    loop = boundary["frame_loop_equivalence"]
    if loop["outputs_identical"] is not True:
        fail("frame loop control differs from whole clip")
    if loop["whole_digest"] != loop["frame_loop_digest"]:
        fail("frame loop digests differ")
    alignment = boundary["alignment_probe"]
    if alignment["algorithmic_lag_samples"] != 0:
        fail("alignment probe has non-zero lag")
    if alignment["peak_index_preserved"] is not True:
        fail("sample alignment was not preserved")
    if alignment["measured_latency"] is not False:
        fail("latency is claimed as measured")
    tail = boundary["tail_control"]
    if tail["input_samples"] != 32_123 or tail["output_samples"] != 32_123:
        fail("partial-tail input/output accounting mismatch")
    if tail["internal_frame_padding_samples"] != 37:
        fail("partial-tail padding mismatch")
    if tail["padding_emitted_as_audio"] is not False:
        fail("partial-tail padding was emitted")
    state = boundary["statelessness"]
    for key in ("clip_b_independent_of_prior_clip", "clip_a_replay_identical"):
        if state[key] is not True:
            fail("statelessness evidence failed: " + key)
    if state["state_carried_between_clips"] is not False:
        fail("state is carried between clips")
    if state["real_recurrent_state_loaded"] is not False:
        fail("real recurrent state is claimed")
    if boundary["device_clock_used"] is not False or boundary["deadline_measured"] is not False:
        fail("device timing is claimed")

    asset = report["asset_boundary"]
    if asset["readiness"] != "blocked" or asset["reason_codes"] != EXPECTED_REASONS:
        fail("asset boundary is not blocked with the exact reasons")
    if asset["asset"]["sha256"] != reference.MODEL_SHA256:
        fail("asset digest mismatch")
    if asset["asset"]["byte_count"] != reference.MODEL_BYTES:
        fail("asset byte count mismatch")
    if asset["asset"]["model_revision"] is not None:
        fail("unpinned model revision was replaced")
    if asset["download_attempted"] is not False or asset["asset_bytes_read"] is not False:
        fail("asset boundary performed I/O")
    if asset["synthetic_admission_control"]["status"] != "admitted":
        fail("synthetic admission control did not exercise admission")
    if asset["synthetic_admission_control"]["not_the_pinned_candidate"] is not True:
        fail("synthetic admission control is presented as the candidate")

    profile = report["enhancement_profile"]
    if profile["name"] != "enhancement" or profile["identity_and_noisy_controls"] is not True:
        fail("enhancement profile identity/controls missing")
    if profile["stoi"]["status"] != "blocked_unmeasured":
        fail("STOI gate is not blocked")
    if profile["content_and_availability_timing"]["measured"] is not False:
        fail("timing is claimed as measured")
    if profile["listening"]["status"] != "not_run":
        fail("listening is claimed")
    if profile["real_runtime"] is not False or profile["real_clean_references"] is not False:
        fail("enhancement profile claims a real runtime or cohort")
    if profile["whole_clip_requirement"] is not True:
        fail("whole-clip requirement is missing")
    if profile["alignment"]["measured"] is not False:
        fail("alignment is claimed as measured")

    adverse = report["adverse"]
    configs = adverse["config_rejections"]
    if set(configs) != EXPECTED_CONFIGS:
        fail("config adverse case set mismatch")
    for name, case in configs.items():
        if name == "caller_asset_admission_control":
            if case["status"] != "created" or case["session_created"] is not True:
                fail("synthetic admission control was not created")
        elif case["status"] != "rejected" or case["session_created"] is not False:
            fail("config case did not fail closed: " + name)
    clips = adverse["clip_cases"]["cases"]
    if set(clips) != EXPECTED_CLIPS:
        fail("clip adverse case set mismatch")
    for name, case in clips.items():
        if not case["status"].startswith("rejected") or case["state_unchanged"] is not True:
            fail("clip case did not fail closed: " + name)
    if adverse["clip_cases"]["state_after_close_unchanged_by_rejected_call"] is not True:
        fail("state changed after a rejected post-close call")
    lifecycle = adverse["lifecycle"]
    if (lifecycle["one_clip_completed"] is not True
            or lifecycle["one_call_only"] is not True
            or lifecycle["close_idempotent"] is not True
            or lifecycle["zero_length_clip_rejected"] is not True):
        fail("lifecycle evidence failed")
    if not lifecycle["process_after_close"].startswith("rejected"):
        fail("post-close processing did not fail closed")
    for key in ("incremental_process_api_absent", "flush_api_absent", "reset_api_absent"):
        if lifecycle[key] is not True:
            fail("streaming API leaked into offline boundary: " + key)

    repeat = report["repeatability"]
    if repeat["count"] != 3 or repeat["byte_identical"] is not True:
        fail("repeatability is not byte-identical")
    if len(set(repeat["digests"])) != 1:
        fail("repeatability digests differ")

    if set(gate["name"] for gate in report["gates"]) != EXPECTED_GATES:
        fail("release gate set mismatch")
    for gate in report["gates"]:
        if gate["status"] != "blocked" or not gate["evidence"] or not gate["reopen"]:
            fail("a release gate is not blocked with evidence and reopening")
    blockers = " ".join(report["exact_blockers"])
    for token in ("model_revision is null", "dpdfnet 0.6.0", "Apache-2.0",
                  "No rights-cleared"):
        if token not in blockers:
            fail("exact blocker text missing: " + token)
    for token in ("immutable artifact revision", "pinned dpdfnet 0.6.0 runtime",
                  "written artifact-specific", "whole-clip offline reference outputs"):
        if token not in " ".join(report["reopen_conditions"]):
            fail("reopening condition missing: " + token)
    if not report["missing_evidence"] or len(report["missing_evidence"]) < 7:
        fail("missing evidence list is incomplete")

    context = report["source_reported_context"]
    if context["pilot_offline_mean_delta_si_sdr_db"] != 7.7973:
        fail("source-reported offline SI-SDR context drifted")
    if context["pilot_offline_mean_delta_snr_db"] != 7.8522:
        fail("source-reported offline SNR context drifted")
    if context["pilot_offline_mean_delta_stoi"] != 0.0329:
        fail("source-reported offline STOI context drifted")
    if context["pilot_offline_batch_rtf"] != 0.0989:
        fail("source-reported offline RTF context drifted")
    if context["offline_content_delay_samples"] is not None:
        fail("offline source context claims a content delay")
    if context["streaming_only_cpp_content_delay_samples"] != 800:
        fail("streaming-only C++ context drifted")
    if "not reproduced" not in context["scope"]:
        fail("source context is not separated as provenance")
    if "not reproduced" not in context["disclaimer"]:
        fail("source context disclaimer is missing")

    if set(report["source_pin_paths"]) != set(reference.SOURCE_PINS):
        fail("source pin paths mismatch")
    if set(report["boundary_pin_paths"]) != set(reference.BOUNDARY_PINS):
        fail("boundary pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("local file names mismatch")
    if b"-0.0" in reference.canonical_report_bytes(report):
        fail("negative zero in canonical report")
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report boundary, accounting, adverse cases and gates strict")


def check_reproduction(manifest: dict[str, str], report_digest: str) -> None:
    if (HERE / "report.json").read_bytes() != cli.report_bytes():
        fail("report.json is not byte-reproducible")
    if (HERE / "adapter.json").read_bytes() != (
            reference.canonical_bytes(reference.build_adapter()) + b"\n"):
        fail("adapter.json is not byte-reproducible")
    if (HERE / "readiness.json").read_bytes() != (
            reference.canonical_bytes(reference.build_readiness()) + b"\n"):
        fail("readiness.json is not byte-reproducible")
    if (HERE / "contract.json").read_bytes() != cli.contract_bytes(cli.contract_pins()):
        fail("contract.json is not byte-reproducible")
    if (HERE / "SOURCES.sha256").read_bytes() != cli.manifest_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    if hashlib.sha256(cli.report_bytes()).hexdigest() != report_digest:
        fail("canonical report digest mismatch")
    code = ("import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != report_digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical artifacts, sidecar, manifest and three cold starts exact")


def check_licensing(manifest: dict[str, str]) -> None:
    explicit = 0
    annotated = 0
    expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if not path.is_file():
            fail("non-file entry in evidence directory")
        if "__pycache__" in path.parts:
            fail("unexpected __pycache__ in evidence directory")
        name = path.relative_to(HERE).as_posix()
        if name not in expected:
            fail("file outside fail-closed local set: " + name)
        if name == "SOURCES.sha256":
            if not (HERE / "SOURCES.sha256.license").is_file():
                fail("SOURCES.sha256.license missing")
            annotated += 1
            continue
        if path.suffix == ".py":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["# " + SPDX_C, "# " + SPDX_L]:
                fail("missing explicit Python SPDX header: " + name)
            if path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("repeated SPDX identifier token: " + name)
            explicit += 1
        elif path.suffix == ".md":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
                fail("missing Markdown SPDX header: " + name)
            explicit += 1
        elif name.endswith(".license"):
            if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("invalid license sidecar: " + name)
            annotated += 1
        else:
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("missing or invalid license sidecar: " + name + ".license")
            if f"worktree:{TASK_PREFIX}{name}.license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
            annotated += 1
    for name in sorted(expected - {path.relative_to(HERE).as_posix()
                                   for path in HERE.rglob("*") if path.is_file()}):
        fail("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    print("verify: write scope limited to the task-local evidence directory")


def main() -> int:
    manifest = read_manifest()
    check_pins(manifest)
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    readiness = strict_json(HERE / "readiness.json")
    report = strict_json(HERE / "report.json")
    check_disposition(contract, adapter, readiness)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    readme_digest_pins()
    check_reproduction(manifest, digest)
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} "
          f"decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
