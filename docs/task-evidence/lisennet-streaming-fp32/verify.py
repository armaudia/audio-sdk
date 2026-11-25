# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Every check fails closed: stale pins, a stale README digest table, duplicate
JSON keys, nonfinite constants, noncanonical regeneration, disposition drift, a
promoted missing result, licensing gaps or any out-of-scope worktree change is a
hard failure.
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
from typing import Any, Dict, List

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

EXPECTED_REASONS = list(reference.ASSET_ADMISSION_REASONS)
EXPECTED_GATES = {name for name, _ in reference.GATE_DEFINITIONS}
EXPECTED_VARIANTS = {
    "identity_passthrough", "noisy_control",
    "surrogate_stream_160", "surrogate_whole_call",
}


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


def strict_json(path: Path) -> Dict[str, Any]:
    def pairs(items: List[tuple]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
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


def read_manifest() -> Dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != cli.MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: Dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  ([^\s]+(?:\s[^\s]+)*)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set:
    local = {f"worktree:{TASK_PREFIX}{name}" for name in reference.LOCAL_FILES}
    return ({f"source:{name}" for name in reference.SOURCE_PINS}
            | {f"worktree:{name}" for name in reference.BOUNDARY_PINS}
            | local)


def check_pins(manifest: Dict[str, str]) -> None:
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


def check_readme_digest_table() -> int:
    if not (HERE / "README.md").is_file():
        fail("README.md missing")
    try:
        rows = reference.readme_pin_rows()
    except (OSError, ValueError, UnicodeError) as error:
        fail("readme_table_unreadable: " + str(error))
    if not rows:
        fail("readme_digest_table_missing")
    seen: Dict[str, str] = {}
    for path, digest in rows:
        if path in seen:
            fail("readme_duplicate_row: " + path)
        seen[path] = digest
        if path.startswith(TASK_PREFIX):
            fail("readme_row_for_local_artifact: " + path)
        try:
            target = reference.qualify_pin_path(path)
        except ValueError as error:
            fail("readme_row_path_invalid: " + str(error))
        if not target.is_file():
            fail("readme_row_target_missing: " + path)
        if reference.sha256_file(target) != digest:
            fail("readme_row_digest_stale: " + path)
    missing = sorted(set(reference.SOURCE_PINS) - set(seen))
    extra = sorted(set(seen) - set(reference.SOURCE_PINS))
    if missing or extra:
        fail("readme table set mismatch: missing=" + str(missing)
             + " extra=" + str(extra))
    for path, digest in reference.SOURCE_PINS.items():
        if seen.get(path) != digest:
            fail("readme_row_pin_disagreement: " + path)
    print(f"verify: README digest table has {len(rows)} exact source rows")
    return len(rows)


def check_disposition(contract: Dict[str, Any], adapter: Dict[str, Any],
                      readiness: Dict[str, Any]) -> None:
    for name, document in (("contract", contract), ("adapter", adapter),
                           ("readiness", readiness)):
        if document.get("decision") != reference.DECISION:
            fail(name + " decision is not DEFER")
    if contract.get("status") != reference.STATUS:
        fail("contract status mismatch")
    if contract.get("evidence_status") != reference.EVIDENCE_STATUS:
        fail("contract evidence status mismatch")
    if contract.get("qualification_status") != reference.QUALIFICATION_STATUS:
        fail("contract qualification status mismatch")
    if any(value is not False for key, value in contract["boundary"].items()
           if isinstance(value, bool) and key != "installed_v0_geometry_preserved"):
        fail("contract boundary flag is not false")
    if contract["boundary"]["installed_v0_geometry_preserved"] is not True:
        fail("contract geometry-preserved flag is not true")
    if contract["boundary"]["descriptor_settings"] != {}:
        fail("contract descriptor settings are not empty")
    if contract["boundary"] != reference.BOUNDARY:
        fail("contract boundary differs from the frozen boundary")
    for key in ("registered", "enabled_by_default", "default_selected",
                "public_api_abi_change", "provider_registration",
                "descriptor_registry_change", "installed_v0_behavior_change",
                "implemented", "quality_claim", "real_runtime_used",
                "weights_accessed"):
        if adapter.get(key) is not False:
            fail("adapter fail-closed flag is not false: " + key)
    if adapter["descriptor_settings"] != {}:
        fail("adapter descriptor settings are not empty")
    if adapter["asset_readiness"] != "blocked":
        fail("adapter reports a ready asset")
    if adapter["asset_present"] is not False:
        fail("adapter reports a present asset")
    if readiness["status"] != "blocked" or readiness["qualified"] is not False:
        fail("readiness is not blocked/not qualified")
    if readiness["admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("readiness reason codes drifted")
    if readiness["admission"]["status"] != "blocked":
        fail("readiness admission is not blocked")
    for key in ("download_attempted", "vendor_runtime_invoked",
                "asset_bytes_read"):
        if readiness["admission"][key] is not False:
            fail("readiness admission performed a forbidden action: " + key)
    for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                "ready_for_release", "quality_pass"):
        if readiness[key] is not False:
            fail("readiness promotion flag is not false: " + key)
    for token in ("not ready", "ONNX Runtime", "7-hex abbreviation",
                  "rights are not cleared"):
        if token not in readiness["readiness_conclusion"]:
            fail("readiness conclusion is missing: " + token)
    if len(readiness["external_blockers"]) != 4:
        fail("readiness external blocker count mismatch")
    if len(readiness["blocked_gates"]) != len(reference.GATE_DEFINITIONS):
        fail("readiness blocked gate count mismatch")
    print("verify: contract, adapter and readiness are blocked/DEFER and OFF")


def check_report(report: Dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT:
        fail("report base commit mismatch")
    if report["branch"] != reference.BRANCH:
        fail("report branch mismatch")
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
        fail("installed v0 geometry mismatch")
    if report["boundary"] != reference.BOUNDARY:
        fail("report boundary mismatch")
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")

    geometry = report["geometry"]
    for key, value in (("sample_rate_hz", 16000), ("channels", 1),
                       ("n_fft", 512), ("hop_samples", 256),
                       ("n_freqs", 257), ("compress_power", 0.3),
                       ("state_slot_count", 17),
                       ("state_past_frame_rows", 71),
                       ("public_v0_frame_samples", 160),
                       ("content_lag_samples", 0),
                       ("availability_lag_samples", 256)):
        if geometry[key] != value:
            fail("streaming geometry mismatch: " + key)

    cache = report["state_cache"]
    if cache["slot_count"] != 17 or cache["past_frame_rows"] != 71:
        fail("state cache dimensions mismatch")
    if len(cache["slots"]) != 17:
        fail("state cache slot list mismatch")
    if cache["asset_state_bytes"] is not None:
        fail("opaque asset state bytes were invented")
    if cache["surrogate_cache_bytes"] != 71 * 3 * 257 * 4:
        fail("surrogate state cache byte count mismatch")

    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for name, block in report["conditions"].items():
        variants = block["variants"]
        if set(variants) != EXPECTED_VARIANTS:
            fail("variant set mismatch in " + name)
        for variant in variants.values():
            if variant["nonfinite_samples"] != 0 or variant["clipped_samples"] != 0:
                fail("invalid output in condition " + name)
            if variant["output_samples"] != reference.SAMPLES:
                fail("output length mismatch in " + name)
            if not (0.0 <= variant["peak_abs_output"] <= 1.0):
                fail("peak outside the unit guard in " + name)
        identity = variants["identity_passthrough"]
        noisy = variants["noisy_control"]
        if identity["output_sha256"] != noisy["output_sha256"]:
            fail("identity and noisy controls differ in " + name)
        if variants["surrogate_stream_160"]["output_sha256"] != \
                variants["surrogate_whole_call"]["output_sha256"]:
            fail("large chunk does not match the 160-sample stream in " + name)
        if not block["large_chunk_matches_160"]:
            fail("large chunk flag false in " + name)
        tail = block["tail_validity"]
        if tail["input_samples"] != reference.SAMPLES:
            fail("tail input accounting mismatch in " + name)
        if tail["valid_samples"] != reference.SAMPLES:
            fail("valid sample accounting mismatch in " + name)
        if tail["emitted_before_flush"] + tail["flush_emitted"] != tail["valid_samples"]:
            fail("emitted/flush accounting mismatch in " + name)
        if tail["internal_tail_reflection_samples"] != reference.HOP_SAMPLES:
            fail("tail reflection accounting mismatch in " + name)

    boundary = report["streaming_boundary"]
    if boundary["declared_content_lag_samples"] != 0:
        fail("declared content lag mismatch")
    if boundary["declared_availability_lag_samples"] != reference.HOP_SAMPLES:
        fail("declared availability lag mismatch")
    if boundary["lag_measured"] is not False or \
            boundary["lag_modeled_in_fixture"] is not True:
        fail("lag is claimed as measured")
    if boundary["clock_id"] != reference.CLOCK_ID:
        fail("fixture clock identity mismatch")
    cross = boundary["chunk_invariance"]
    if not cross["chunk_invariant"] or not cross["whole_call_matches_chunked"]:
        fail("chunk invariance failed")
    if set(cross["chunk_sizes_tested"]) != set(reference.CHUNK_SIZES):
        fail("chunk size set mismatch")
    if set(cross["records"]) != {str(size) for size in reference.CHUNK_SIZES}:
        fail("chunk record set mismatch")
    reference_digest = cross["records"][str(reference.SAMPLES)]["output_sha256"]
    for size, record in cross["records"].items():
        if record["output_samples"] != reference.SAMPLES:
            fail("chunk output accounting mismatch at " + size)
        if record["output_sha256"] != reference_digest:
            fail("chunk output digest mismatch at " + size)
        if record["emitted_before_flush"] + record["flush_emitted"] != reference.SAMPLES:
            fail("chunk emitted/flush accounting mismatch at " + size)
    alignment = boundary["alignment_probe"]
    if (alignment["input_peak_sample"] != reference.IMPULSE_INDEX
            or alignment["output_peak_sample"] != reference.IMPULSE_INDEX
            or alignment["residual_lag_samples"] != 0
            or alignment["lag_measured"] is not False):
        fail("alignment probe is not zero content lag")
    state = boundary["state"]
    if not all(state[key] is True for key in (
            "replay_identical", "independent_session_identical",
            "cross_stream_reset_identical", "reset_restores_initial_state")):
        fail("streaming state/reset evidence failed")
    if state["real_recurrent_state_loaded"] is not False:
        fail("real recurrent state is claimed")
    if state["slot_count"] != 17 or state["past_frame_rows"] != 71:
        fail("state evidence dimensions mismatch")
    flush = boundary["flush"]
    if (not flush["second_flush_empty"]
            or not flush["process_after_flush_rejected"]
            or not flush["reset_after_flush_allows_new_stream"]):
        fail("flush lifecycle evidence failed")
    if flush["emitted_before_flush"] + flush["flush_emitted"] != reference.SAMPLES:
        fail("flush accounting mismatch")
    if flush["total_emitted"] != reference.SAMPLES:
        fail("flush total emitted mismatch")
    accounting = boundary["frame_accounting"]
    if accounting["output_samples"] != accounting["input_samples"]:
        fail("frame accounting output/input mismatch")
    if accounting["emitted_before_flush"] + accounting["flush_emitted"] != \
            accounting["input_samples"]:
        fail("frame accounting emitted/flush mismatch")

    asset = report["asset_boundary"]
    if asset["readiness"] != "blocked" or asset["reason_codes"] != EXPECTED_REASONS:
        fail("asset boundary is not blocked with the exact reasons")
    if asset["asset"]["sha256"] != reference.MODEL_SHA256:
        fail("asset digest mismatch")
    if asset["asset"]["byte_count"] != reference.MODEL_BYTES:
        fail("asset byte count mismatch")
    if asset["asset"]["source_revision"] != reference.MODEL_REVISION:
        fail("asset revision mismatch")
    if asset["asset"]["bytes_present"] is not False:
        fail("asset bytes are claimed present")
    if asset["asset"]["rights_cleared"] is not False:
        fail("asset rights are claimed cleared")
    if asset["admission"]["download_attempted"] is not False or \
            asset["admission"]["asset_bytes_read"] is not False:
        fail("asset admission performed I/O")
    control = asset["synthetic_admission_control"]
    if control["status"] != "admitted" or control["not_the_pinned_candidate"] is not True:
        fail("synthetic admission control is not fail-closed")

    profile = report["enhancement_profile"]
    if profile["name"] != "enhancement" or \
            profile["identity_and_noisy_controls"] is not True:
        fail("enhancement profile identity/controls missing")
    if profile["established_baseline"]["status"] != "not_reproduced":
        fail("an established baseline is claimed reproduced")
    if profile["stoi"]["status"] != "synthetic_only":
        fail("STOI is claimed on a real cohort")
    if profile["content_and_availability_timing"]["measured"] is not False:
        fail("timing is claimed as measured")
    if profile["listening"]["status"] != "not_run":
        fail("listening is claimed")
    if profile["real_runtime"] is not False or \
            profile["real_clean_references"] is not False:
        fail("enhancement profile claims a real runtime or cohort")
    if profile["state_and_memory"]["asset_state_bytes"] is not None:
        fail("asset state bytes are invented")
    peaks = profile["peaks_and_invalid_outputs"]
    if peaks["invalid_or_clipped_samples"] != 0 or peaks["all_finite"] is not True:
        fail("invalid surrogate output is present")
    if peaks["max_peak_abs_output"] > 1.0:
        fail("surrogate peak exceeds the unit guard")

    adverse = report["adverse"]
    configs = adverse["config_rejections"]
    expected_configs = {
        "wrong_sample_rate_hz", "wrong_channels", "wrong_n_fft",
        "wrong_hop_samples", "wrong_n_freqs", "wrong_compress_power",
        "wrong_state_slot_count", "wrong_sample_format", "wrong_sha256",
        "wrong_byte_count", "missing_field", "extra_field",
        "relative_caller_path", "surrogate_without_opt_in",
        "caller_asset_unavailable", "synthetic_admission_control",
    }
    if set(configs) != expected_configs:
        fail("config adverse case set mismatch")
    for name, case in configs.items():
        if name == "synthetic_admission_control":
            if case["status"] != "admitted" or \
                    case["not_the_pinned_candidate"] is not True:
                fail("synthetic admission control was not exercised")
        elif name == "caller_asset_unavailable":
            if case["status"] != "blocked":
                fail("caller asset was admitted without bytes")
        elif not case["status"].startswith("rejected"):
            fail("config case did not fail closed: " + name)
    frames = adverse["frame_cases"]["cases"]
    for name, case in frames.items():
        if name == "empty_chunk":
            if case["status"] != "accepted_empty":
                fail("empty chunk did not behave as an empty control")
        elif not case["status"].startswith("rejected"):
            fail("frame case did not fail closed: " + name)
        if case["state_unchanged"] is not True:
            fail("frame case changed state: " + name)
    if adverse["frame_cases"]["flush_idempotent"] is not True:
        fail("flush is not idempotent")
    if adverse["frame_cases"]["state_after_rejected_process_unchanged"] is not True:
        fail("state changed after a rejected process")
    lifecycle = adverse["lifecycle"]
    if (not lifecycle["flush_returns_samples"]
            or not lifecycle["second_flush_empty"]
            or not lifecycle["reset_after_flush_works"]
            or not lifecycle["zero_length_stream_flush"]):
        fail("lifecycle evidence failed")
    if lifecycle["post_flush_calls"]["process_after_flush"] != "rejected:process_after_flush":
        fail("post-flush process did not fail closed")
    if lifecycle["post_flush_calls"]["flush_after_flush_returns_empty"] != "accepted_empty":
        fail("second flush is not empty")

    if not report["regressions"]:
        fail("no synthetic regression was recorded")
    for item in report["regressions"]:
        if item["adverse"] is not True:
            fail("a regression is not marked adverse")
    repeat = report["repeatability"]
    if repeat["count"] != 3 or repeat["byte_identical"] is not True:
        fail("repeatability is not byte-identical")
    if len(set(repeat["digests"])) != 1:
        fail("repeatability digests differ")

    if {gate["name"] for gate in report["gates"]} != EXPECTED_GATES:
        fail("release gate set mismatch")
    for gate in report["gates"]:
        if gate["status"] != "blocked" or not gate["evidence"] or not gate["reopen"]:
            fail("a release gate is not blocked with evidence and reopening")
    blockers = " ".join(report["exact_blockers"])
    for token in ("7-hex abbreviation", "onnxruntime", "MIT",
                  "No qualification evidence"):
        if token not in blockers:
            fail("exact blocker text missing: " + token)
    for token in ("full immutable repository commit", "pinned ONNX Runtime",
                  "written artifact-specific"):
        if token not in " ".join(report["reopen_conditions"]):
            fail("reopening condition missing: " + token)
    if len(report["missing_evidence"]) < 9:
        fail("missing evidence list is incomplete")

    context = report["source_reported_context"]
    if context["paired_items"] != 30:
        fail("source-reported paired item count drifted")
    if context["mean_delta_si_sdr_db"] != -6.6148:
        fail("source-reported SI-SDR context drifted")
    if context["mean_delta_stoi"] != -0.0515:
        fail("source-reported STOI context drifted")
    if context["batch_rtf"] != 0.0212:
        fail("source-reported RTF context drifted")
    if "Not reproduced" not in context["scope"]:
        fail("source context is not separated as provenance")
    if "not reproduced" not in context["disclaimer"]:
        fail("source context disclaimer is missing")

    if set(report["source_pin_paths"]) != set(reference.SOURCE_PINS):
        fail("source pin paths mismatch")
    if set(report["boundary_pin_paths"]) != set(reference.BOUNDARY_PINS):
        fail("boundary pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("local file names mismatch")
    if reference.has_negative_zero(report):
        fail("negative zero in canonical report")
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report boundary, accounting, adverse cases and gates strict")


def check_reproduction(manifest: Dict[str, str], report_digest: str) -> None:
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
    code = "import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())"
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != report_digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical artifacts, sidecar, manifest and three cold starts exact")


def check_licensing(manifest: Dict[str, str]) -> None:
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
    present = {path.relative_to(HERE).as_posix()
               for path in HERE.rglob("*") if path.is_file()}
    for name in sorted(expected - present):
        fail("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True,
                            check=True)
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
    check_readme_digest_table()
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    readiness = strict_json(HERE / "readiness.json")
    report = strict_json(HERE / "report.json")
    check_disposition(contract, adapter, readiness)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    check_reproduction(manifest, digest)
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} "
          f"decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
