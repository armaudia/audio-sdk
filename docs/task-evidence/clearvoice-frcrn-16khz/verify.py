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
    "download_revision_unrecorded",
    "pointer_artifact_unverified",
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
EXPECTED_CONFIG_CASES = {
    "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
    "wrong_model_name", "wrong_package_version", "mode_unsupported",
    "surrogate_without_opt_in", "caller_asset_unavailable",
    "caller_asset_wrong_checkpoint_sha", "caller_asset_admission_control",
}
EXPECTED_VARIANTS = {
    "identity_passthrough", "noisy_control",
    "surrogate_offline_chunked_160", "surrogate_offline_whole_clip",
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
    if contract["offline_boundary"] != reference.OFFLINE_BOUNDARY:
        fail("contract offline boundary differs")
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
    if adapter.get("modes") != ["offline"]:
        fail("adapter mode is not the offline boundary")
    if readiness["status"] != "blocked" or readiness["qualified"] is not False:
        fail("readiness is not blocked/not qualified")
    if readiness["admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("readiness reason codes drifted")
    if readiness["admission"]["status"] != "blocked":
        fail("readiness admission is not blocked")
    for key in ("download_attempted", "vendor_runtime_invoked", "asset_bytes_read"):
        if readiness["admission"][key] is not False:
            fail("readiness admission performed a forbidden action: " + key)
    for token in ("not ready", "clearvoice 0.1.2",
                  "no immutable model artifact revision",
                  "pointer content is unverified"):
        if token not in readiness["readiness_conclusion"]:
            fail("readiness conclusion is missing: " + token)
    print("verify: contract, adapter and readiness are blocked/DEFER and OFF")


def check_report(report: dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        fail("report base or branch mismatch")
    if report["task_id"] != reference.TASK:
        fail("report task mismatch")
    if report["component"] != reference.COMPONENT or report["slug"] != reference.SLUG:
        fail("report component or slug mismatch")
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
    if report["offline_boundary"] != reference.OFFLINE_BOUNDARY:
        fail("report offline boundary mismatch")
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
        if not block["whole_clip_matches_chunked"]:
            fail("whole clip does not match the chunked feed in " + name)
        tail = block["tail_validity"]
        if tail["output_samples"] != tail["input_samples"]:
            fail("output length is not the input length in " + name)
        if tail["valid_samples"] != tail["input_samples"]:
            fail("valid sample accounting mismatch in " + name)
        if tail["internal_frame_padding_samples"] != (
                (-tail["input_samples"]) % reference.FRAME_SAMPLES):
            fail("internal frame padding mismatch in " + name)
        if tail["padded_samples_emitted"] != 0:
            fail("padding was emitted in " + name)
        if tail["delay_compensation_samples"] != 0:
            fail("delay compensation is not zero in " + name)
        if tail["source_time_mapping"] != "identity":
            fail("source time mapping is not identity in " + name)
    controls = report["controls"]
    if not controls["all_present"] or not controls["identity"]["exact_passthrough"]:
        fail("matched controls incomplete")
    if controls["candidate"]["real_candidate"] is not False:
        fail("surrogate is presented as the real candidate")

    boundary = report["offline_processing"]
    if boundary["declared_algorithmic_lag_samples"] != 0:
        fail("declared lag is not zero")
    if boundary["declared_algorithmic_lag_ns"] != 0:
        fail("declared lag nanoseconds are not zero")
    if boundary["lag_measured_here"] is not False or boundary["lag_modeled_in_fixture"] is not True:
        fail("lag is claimed as measured")
    if boundary["clock_id"] != reference.CLOCK_ID:
        fail("fixture clock identity mismatch")
    if boundary["upstream_config_fields"] != list(reference.CALLER_CONFIG_FIELDS):
        fail("upstream config fields mismatch")
    if boundary["pointer_requirement"]["required_content"] != reference.POINTER_REQUIRED_CONTENT:
        fail("pointer requirement mismatch")
    if boundary["pointer_requirement"]["content_verified_here"] is not False:
        fail("pointer is claimed as verified")
    cross = boundary["chunk_invariance"]
    if not cross["output_chunk_invariant"] or not cross["whole_call_matches_chunked"]:
        fail("chunk invariance failed")
    if set(cross["chunk_sizes_tested"]) != set(reference.CHUNK_SIZES):
        fail("chunk size set mismatch")
    if set(cross["records"]) != {str(size) for size in reference.CHUNK_SIZES}:
        fail("chunk record set mismatch")
    for size, record in cross["records"].items():
        if record["output_length"] != 32000 or record["valid_samples"] != 32000:
            fail("chunk accounting mismatch at " + size)
        if record["emitted_before_finish"] != 0:
            fail("offline session emitted before finish at " + size)
        if record["finish_emitted"] != record["output_length"]:
            fail("finish emission accounting mismatch at " + size)
    alignment = boundary["alignment_probe"]
    if (alignment["output_lag_samples"] != 0
            or alignment["residual_lag_samples"] != 0
            or alignment["measured_latency"] is not False):
        fail("alignment probe is not the modelled zero-lag boundary")
    state = boundary["state"]
    if not all(state[key] is True for key in (
            "reset_replay_identical", "independent_session_identical",
            "cross_stream_reset_identical")):
        fail("offline state/reset evidence failed")
    if state["real_recurrent_state_loaded"] is not False:
        fail("real recurrent state is claimed")
    tail_probe = boundary["tail_probe"]
    if (tail_probe["input_samples"] != 32123 or tail_probe["output_samples"] != 32123
            or tail_probe["internal_frame_padding_samples"] != 37
            or tail_probe["padded_samples_emitted"] != 0
            or tail_probe["exact_length"] is not True):
        fail("partial final frame probe failed")

    asset = report["asset_boundary"]
    if asset["readiness"] != "blocked" or asset["reason_codes"] != EXPECTED_REASONS:
        fail("asset boundary is not blocked with the exact reasons")
    if asset["asset"]["sha256"] != reference.CHECKPOINT_SHA256:
        fail("asset digest mismatch")
    if asset["asset"]["byte_count"] != reference.CHECKPOINT_BYTES:
        fail("asset byte count mismatch")
    if asset["asset"]["source_revision"] != reference.SOURCE_REVISION:
        fail("asset source revision mismatch")
    if asset["asset"]["model_revision"] is not None:
        fail("unpinned model revision was replaced")
    if asset["asset"]["model_download_revision"] is not None:
        fail("unrecorded download revision was replaced")
    if asset["auxiliary_assets"][0]["sha256"] != reference.POINTER_SHA256:
        fail("pointer digest mismatch")
    if asset["auxiliary_assets"][0]["byte_count"] != reference.POINTER_BYTES:
        fail("pointer byte count mismatch")
    if asset["auxiliary_assets"][0]["content_verified"] is not False:
        fail("pointer content is claimed as verified")
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
    if profile["alignment"]["status"] != "modelled_zero_lag":
        fail("alignment status is not the modelled zero-lag boundary")

    adverse = report["adverse"]
    configs = adverse["config_rejections"]
    if set(configs) != EXPECTED_CONFIG_CASES:
        fail("config adverse case set mismatch")
    for name, case in configs.items():
        if name == "caller_asset_admission_control":
            if case["status"] != "created" or case["session_created"] is not True:
                fail("synthetic admission control was not created")
        elif case["status"] != "rejected" or case["session_created"] is not False:
            fail("config case did not fail closed: " + name)
    frames = adverse["frame_cases"]["cases"]
    if set(frames) != {
            "empty_chunk", "oversized_chunk", "nonfinite_sample",
            "infinite_sample", "string_chunk", "boolean_sample",
            "out_of_range_sample", "process_after_finish",
            "finish_after_finish", "process_after_close",
            "finish_after_close", "reset_after_close"}:
        fail("frame adverse case set mismatch")
    for name, case in frames.items():
        if not case["status"].startswith("rejected") or case["state_unchanged"] is not True:
            fail("frame case did not fail closed: " + name)
    if adverse["frame_cases"]["state_after_finish_unchanged_by_rejected_calls"] is not True:
        fail("state changed after a rejected post-finish call")
    if adverse["frame_cases"]["state_after_close_unchanged_by_rejected_calls"] is not True:
        fail("state changed after rejected post-close calls")
    lifecycle = adverse["lifecycle"]
    if (not lifecycle["finish_returns_samples"] or not lifecycle["reset_finish_empty"]
            or not lifecycle["close_idempotent"] or not lifecycle["zero_length_finish"]):
        fail("lifecycle evidence failed")
    if not lifecycle["second_finish"].startswith("rejected"):
        fail("second finish did not fail closed")
    for key in ("process_after_close", "finish_after_close", "reset_after_close"):
        if not lifecycle[key].startswith("rejected"):
            fail("post-close lifecycle did not fail closed: " + key)

    if not report["regressions"]:
        fail("no synthetic regression was recorded")
    for item in report["regressions"]:
        if item["metric"] not in ("snr_db", "si_sdr_db"):
            fail("unknown regression metric")
        if item["surrogate_offline_chunked_160"] >= item["noisy_control"]:
            fail("regression is not a regression")
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
    for token in ("161,053,751", "b22256adbb91b68cf5a3db8f6657a4fb17066eecd5f069803e59c186c1cf3ebb",
                  "model_revision is absent", "clearvoice 0.1.2", "Apache-2.0",
                  "open and private", "No rights-cleared"):
        if token not in blockers:
            fail("exact blocker text missing: " + token)
    for token in ("immutable model artifact revision", "pinned clearvoice 0.1.2 runtime",
                  "written artifact-specific", "rights-cleared"):
        if token not in " ".join(report["reopen_conditions"]):
            fail("reopening condition missing: " + token)
    if not report["missing_evidence"] or len(report["missing_evidence"]) < 8:
        fail("missing evidence list is incomplete")

    context = report["source_reported_context"]
    if context["pilot_30_clip_mean_delta_si_sdr_db"] != 10.05:
        fail("source-reported SI-SDR context drifted")
    if context["pilot_30_clip_mean_adapter_rtf"] != 3.74:
        fail("source-reported mean RTF context drifted")
    if context["pilot_30_clip_median_cpu_rtf"] != 3.59:
        fail("source-reported median RTF context drifted")
    if context["ears_12_clip_no_reference_screen"]["clips"] != 12:
        fail("source-reported EARS clip count drifted")
    if context["upstream_author_reported_dns2020"]["PESQ"] != 3.24:
        fail("upstream author PESQ context drifted")
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
    if report["readme_digest_files"] != list(reference.README_DIGEST_FILES):
        fail("README digest file list mismatch")
    if re.search(rb"-0\.0(?=[,}\]])", reference.canonical_report_bytes(report)):
        fail("negative zero in canonical report")
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report boundary, accounting, adverse cases and gates strict")


def _readme_table_rows() -> list[tuple[str, str, int]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    if text.count(reference.README_TABLE_START) != 1:
        fail("README digest table start marker is not unique")
    if text.count(reference.README_TABLE_END) != 1:
        fail("README digest table end marker is not unique")
    start = text.index(reference.README_TABLE_START)
    end = text.index(reference.README_TABLE_END)
    if end <= start:
        fail("README digest table markers are ordered incorrectly")
    block = text[start + len(reference.README_TABLE_START):end].strip().splitlines()
    expected_header = ["| Artifact | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    if block[:2] != expected_header:
        fail("README digest table header mismatch")
    rows: list[tuple[str, str, int]] = []
    for line in block[2:]:
        parts = re.fullmatch(r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|", line)
        if parts is None:
            fail("malformed README digest row: " + repr(line))
        rows.append((parts.group(1), parts.group(2), int(parts.group(3))))
    return rows


def check_readme() -> None:
    rows = _readme_table_rows()
    expected = [(name, reference.sha256_file(HERE / name),
                 (HERE / name).stat().st_size)
                for name in reference.README_DIGEST_FILES]
    if rows != expected:
        fail("README digest table is stale or incomplete")
    text = (HERE / "README.md").read_text(encoding="utf-8")
    token = (f"Tests: **{reference.EXPECTED_TEST_COUNT} passed, "
             "0 failed, 0 skipped**")
    if token not in text:
        fail("README test count token is stale")
    if "contract.json" in text.split(reference.README_TABLE_START)[1].split(
            reference.README_TABLE_END)[0]:
        fail("README digest table must not pin contract.json (cycle)")
    print(f"verify: README digest table exact for {len(rows)} artifacts")


def check_reproduction(manifest: dict[str, str], report_digest: str) -> None:
    if (HERE / "report.json").read_bytes() != cli.report_bytes():
        fail("report.json is not byte-reproducible")
    if (HERE / "adapter.json").read_bytes() != (
            reference.canonical_bytes(reference.build_adapter()) + b"\n"):
        fail("adapter.json is not byte-reproducible")
    if (HERE / "readiness.json").read_bytes() != (
            reference.canonical_bytes(reference.build_readiness()) + b"\n"):
        fail("readiness.json is not byte-reproducible")
    if (HERE / "README.md").read_bytes() != cli.readme_bytes():
        fail("README.md digest table is not byte-reproducible")
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
    print("verify: canonical artifacts, sidecar, README table, manifest and three cold starts exact")


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
    check_readme()
    check_reproduction(manifest, digest)
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} "
          f"decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
