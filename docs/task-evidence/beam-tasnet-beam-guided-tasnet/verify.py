# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Every check fails closed: missing or stale pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, disposition drift, a promoted missing
result, a stale README digest table, a mutable-board hash, licensing gaps or any
out-of-scope worktree change is a hard failure.
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
from typing import Any, Dict, Set

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
    "architecture_not_selected",
    "source_revision_unpinned",
    "checkpoint_unpinned",
    "weights_absent",
    "runtime_unavailable",
    "rights_not_cleared",
    "array_corpus_absent",
]
EXPECTED_GATE_IDS = {f"RG-{index:02d}" for index in range(1, 9)}
EXPECTED_GATE_NAMES = {
    "exact_architecture_identity",
    "source_and_weights",
    "array_corpus_and_rights",
    "task_matched_scoring_and_listening",
    "channel_and_device_timing",
    "provider_intake",
    "public_default_selection",
    "release_approval",
}
EXPECTED_VARIANTS = {
    "identity_passthrough",
    "alternate_reference_channel",
    "naive_channel_mean",
}
EXPECTED_CONFIGS = {
    "wrong_sample_rate",
    "wrong_channels",
    "wrong_sample_format",
    "wrong_frame_samples",
    "wrong_max_clip_samples",
    "reference_channel_out_of_range",
    "geometry_missing",
    "geometry_not_synchronized",
    "geometry_spacing_invalid",
    "surrogate_without_opt_in",
    "caller_weights_unavailable",
    "synthetic_weight_admission_control",
}
EXPECTED_SCENES = {
    "second_scene",
    "empty_scene",
    "channel_count_mismatch",
    "ragged_channels",
    "oversized_scene",
    "nonfinite_sample",
    "infinite_sample",
    "string_sample",
    "boolean_sample",
    "out_of_range_sample",
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


def require(condition: bool, message: str) -> None:
    if not condition:
        fail(message)


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
    def pairs(items: list[tuple[str, Any]]) -> Dict[str, Any]:
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


def manifest_expected_paths() -> Set[str]:
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
    if f"source:{reference.BOARD_PATH}" in manifest:
        fail("mutable board file must not be pinned")
    if reference.BOARD_PATH in reference.SOURCE_PINS or reference.BOARD_PATH in reference.BOUNDARY_PINS:
        fail("mutable board file appears in a pin table")
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
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact; board unpinned")


def readme_digest_pins() -> Dict[str, tuple[str, int]]:
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
    rows: Dict[str, tuple[str, int]] = {}
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


def check_disposition(contract: Dict[str, Any], adapter: Dict[str, Any],
                      readiness: Dict[str, Any]) -> None:
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
        "status": reference.QUALIFICATION_STATUS,
        "evidence_status": reference.EVIDENCE_STATUS,
        "decision": reference.DECISION,
        "qualifies": False,
        "missing_result_promoted": False,
        "processor_exposure": False,
        "real_runtime_used": False,
        "real_weights_used": False,
        "quality_claim": False,
        "release_claim": False,
    }
    if any(qualification.get(key) != value for key, value in required.items()):
        fail("contract qualification is not not_qualified/DEFER")
    if contract["qualification"] != reference.qualification_block():
        fail("contract qualification block drifted from the frozen block")
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
    configuration = adapter["configuration"]
    if configuration["streaming_supported"] is not False:
        fail("adapter exposes streaming")
    if configuration["beamforming_supported"] is not False:
        fail("adapter exposes beamforming")
    if configuration["separation_supported"] is not False:
        fail("adapter exposes separation")
    if configuration["whole_clip_only"] is not True:
        fail("adapter is not whole-clip only")
    if configuration["channel_loss_fails_closed"] is not True:
        fail("adapter does not fail closed on channel loss")
    if adapter["architecture_ambiguous"] is not True or adapter["architecture_selected"] is not None:
        fail("adapter architecture identity is not ambiguous")
    if readiness["status"] != "blocked" or readiness["qualified"] is not False:
        fail("readiness is not blocked/not qualified")
    if readiness["admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("readiness reason codes drifted")
    if readiness["admission"]["status"] != "blocked":
        fail("readiness admission is not blocked")
    for key in ("download_attempted", "vendor_runtime_invoked", "asset_bytes_read"):
        if readiness["admission"][key] is not False:
            fail("readiness admission performed a forbidden action: " + key)
    for token in ("two distinct architectures", "not ready", "no pinned runnable runtime"):
        if token not in readiness["readiness_conclusion"]:
            fail("readiness conclusion is missing: " + token)
    print("verify: contract, adapter and readiness are blocked/DEFER and OFF")


def check_report(report: Dict[str, Any], digest: str) -> None:
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        fail("report base or branch mismatch")
    if report["task_id"] != reference.TASK or report["component"] != reference.COMPONENT:
        fail("report identity mismatch")
    if report["profile"] != reference.PROFILE:
        fail("report profile mismatch")
    if report["status"] != reference.STATUS:
        fail("report status mismatch")
    if report["evidence_status"] != reference.EVIDENCE_STATUS:
        fail("report evidence status mismatch")
    if report["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("report qualification status mismatch")
    if report.get("qualification") != reference.qualification_block():
        fail("report qualification block is not not_qualified/DEFER")
    if report["qualification"]["status"] != "not_qualified":
        fail("report qualification status is not not_qualified")
    if report["qualification"]["evidence_status"] != "incomplete":
        fail("report evidence status is not incomplete")
    if report["decision"] != reference.DECISION:
        fail("report decision is not DEFER")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("missing-result qualification guard is absent")
    if report["format"] != reference.FORMAT:
        fail("installed v0 geometry or spatial format mismatch")
    if report["boundary"] != reference.BOUNDARY:
        fail("report boundary mismatch")
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")
    scope = report["scope"]
    if scope.get("task_local_only") is not True:
        fail("scope is not task-local")
    if scope.get("documentation_and_synthetic_fixture_only") is not True:
        fail("scope is not documentation/synthetic-fixture only")
    for key, value in scope.items():
        if key in ("task_local_only", "documentation_and_synthetic_fixture_only"):
            continue
        if value is not False:
            fail("scope flag is not false: " + key)

    identity = report["candidate_identity"]
    if identity["label"] != reference.CANDIDATE_LABEL or identity["count"] != 2:
        fail("candidate identity drifted")
    if identity["selection"] is not None or identity["ambiguous"] is not True:
        fail("candidate architecture was silently selected")
    if identity["no_architecture_chosen"] is not True:
        fail("candidate architecture selection guard is absent")
    names = {item["name"] for item in identity["distinct_architectures"]}
    if names != set(reference.ARCHITECTURE_NAMES):
        fail("candidate architecture names drifted")
    for item in identity["distinct_architectures"]:
        if item["source_revision"] is not None or item["checkpoint_sha256"] is not None:
            fail("candidate architecture claims an unpinned asset as pinned")
        if item["source_or_weights_present"] is not False:
            fail("candidate architecture claims present source/weights")

    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for name, block in report["conditions"].items():
        if block["channels"] != reference.CHANNELS:
            fail("channel count mismatch in " + name)
        if block["samples"] != reference.SAMPLES:
            fail("sample count mismatch in " + name)
        if block["reference_channel"] != reference.REFERENCE_CHANNEL:
            fail("reference channel mismatch in " + name)
        geometry = block["geometry"]
        if geometry["declared"] is not True or geometry["measured"] is not False:
            fail("geometry claim mismatch in " + name)
        if geometry["synchronized"] is not True or geometry["calibrated"] is not False:
            fail("synchronization/calibration claim mismatch in " + name)
        variants = block["variants"]
        if set(variants) != EXPECTED_VARIANTS:
            fail("variant set mismatch in " + name)
        identity_variant = variants["identity_passthrough"]
        if identity_variant["status"] != "scored":
            fail("identity variant is not scored in " + name)
        if identity_variant["output_digest"] != block["reference_channel_digest"]:
            fail("identity passthrough is not exact in " + name)
        if identity_variant["target_preservation_db"] not in (0.0, None):
            fail("identity target preservation is not exact in " + name)
        for variant_name, variant in variants.items():
            if variant["status"] == "rejected":
                if variant_name != "alternate_reference_channel" or name != "channel_dropout":
                    fail("unexpected rejected variant %s in %s" % (variant_name, name))
                if variant["reason"] != "channel_unavailable":
                    fail("channel-loss rejection reason drifted")
                if variant["scored_samples"] != 0 or variant["output_rms"] != 0.0:
                    fail("rejected variant produced output")
                continue
            if variant["status"] != "scored":
                fail("unknown variant status in " + name)
            if variant["nonfinite_samples"] != 0 or variant["clipped_samples"] != 0:
                fail("invalid output in condition " + name)
            if not math.isfinite(variant["peak_abs_output"]):
                fail("nonfinite peak in " + name)
            if variant["scored_samples"] != reference.SAMPLES:
                fail("scored length mismatch in " + name)
            for metric in ("si_sdr_db", "target_preservation_db",
                           "interference_leakage_db", "noise_gain_db"):
                value = variant[metric]
                if value is not None and not math.isfinite(value):
                    fail("nonfinite metric " + metric + " in " + name)
        if "channel_dropout" in name:
            if variants["alternate_reference_channel"]["status"] != "rejected":
                fail("channel loss did not fail closed")
        else:
            if any(variant["status"] != "scored" for variant in variants.values()):
                fail("a variant was rejected without channel loss in " + name)
        accounting = block["output_accounting"]
        if accounting["input_channels"] != reference.CHANNELS:
            fail("input channel accounting mismatch in " + name)
        if accounting["input_samples_per_channel"] != reference.SAMPLES:
            fail("input sample accounting mismatch in " + name)
        if accounting["output_channels"] != 1:
            fail("output channel accounting mismatch in " + name)
        if accounting["output_samples"] != reference.SAMPLES:
            fail("output length mismatch in " + name)
        if accounting["output_samples"] != accounting["scored_samples"]:
            fail("scored prefix differs from output length in " + name)
        if accounting["startup_padding_samples"] != 0:
            fail("startup padding in whole-clip mode: " + name)
        if accounting["tail_padding_emitted_samples"] != 0:
            fail("tail padding emitted in whole-clip mode: " + name)
        if accounting["flush_required"] is not False:
            fail("flush required in whole-clip mode: " + name)
        if accounting["channel_loss_control"] is not (name == "channel_dropout"):
            fail("channel-loss control flag drifted in " + name)

    controls = report["controls"]
    if not controls["all_present"] or not controls["identity"]["exact_passthrough"]:
        fail("matched controls incomplete")
    if controls["candidate"]["real_candidate"] is not False:
        fail("surrogate is presented as the real candidate")
    if not report["regression_assessment"]["performed"]:
        fail("regression assessment was not performed")
    for item in report["regressions"]:
        if item["metric"] not in ("si_sdr_db", "target_preservation_db"):
            fail("unknown regression metric")
        if item["delta"] >= 0.0:
            fail("regression is not a regression")

    profile = report["spatial_profile"]
    if profile["name"] != "spatial" or profile["profile_source"] != "plan/swarm/VERIFICATION.md":
        fail("spatial profile identity missing")
    if profile["geometry"]["declared"] is not True or profile["geometry"]["measured"] is not False:
        fail("spatial geometry claim drifted")
    if profile["timestamp_calibration"]["measured"] is not False:
        fail("timestamp calibration is claimed as measured")
    if profile["timestamp_calibration"]["status"] != "blocked_unmeasured":
        fail("timestamp calibration gate is not blocked")
    if profile["localization_or_activity"]["performed"] is not False:
        fail("localization is claimed")
    if profile["extraction"]["performed"] is not False:
        fail("extraction is claimed")
    if profile["task_matched_heldout_labels"]["present"] is not False:
        fail("held-out labels are claimed")
    if profile["listening"]["status"] != "not_run":
        fail("listening is claimed")
    if profile["real_array_corpus"] is not False or profile["real_runtime"] is not False:
        fail("spatial profile claims a real corpus or runtime")
    if profile["real_weights"] is not False:
        fail("spatial profile claims real weights")
    if profile["device_timing"]["measured"] is not False:
        fail("device timing is claimed as measured")
    if profile["whole_clip_requirement"] is not True:
        fail("whole-clip requirement is missing")
    for key in ("leakage", "target_damage", "channel_loss", "room_reference_changes"):
        if "synthetic_fixture_only" not in profile[key]:
            fail("spatial outcome is over-claimed: " + key)

    boundary = report["spatial_boundary"]
    if boundary["processing_mode"] != "offline_multichannel_whole_clip":
        fail("processing mode mismatch")
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
    if boundary["reference_channel"] != reference.REFERENCE_CHANNEL:
        fail("spatial boundary reference channel mismatch")
    for key in ("device_clock_used", "deadline_measured",
                "channel_synchronization_measured", "geometry_calibration_measured"):
        if boundary[key] is not False:
            fail("device/synchronization measurement is claimed: " + key)

    asset = report["asset_boundary"]
    if asset["readiness"] != "blocked" or asset["reason_codes"] != EXPECTED_REASONS:
        fail("asset boundary is not blocked with the exact reasons")
    if asset["asset"]["architecture"] is not None:
        fail("asset boundary silently selected an architecture")
    if asset["asset"]["source_revision"] is not None:
        fail("unpinned source revision was replaced")
    if asset["asset"]["checkpoint_sha256"] is not None:
        fail("unpinned checkpoint was replaced")
    if asset["download_attempted"] is not False or asset["asset_bytes_read"] is not False:
        fail("asset boundary performed I/O")
    if asset["architectures"]["ambiguous"] is not True:
        fail("architecture ambiguity is not recorded")
    if asset["synthetic_admission_control"]["status"] != "admitted":
        fail("synthetic admission control did not exercise admission")
    if asset["synthetic_admission_control"]["not_the_pinned_candidate"] is not True:
        fail("synthetic admission control is presented as the candidate")
    if report["asset_admission"]["status"] != "blocked":
        fail("candidate asset admission is not blocked")
    if report["asset_admission"]["reason_codes"] != EXPECTED_REASONS:
        fail("candidate asset admission reasons drifted")

    sibling = report["sibling_evidence"]
    for key in ("survey_cln_07", "survey_spk_01"):
        if sibling[key]["results_pooled"] is not False:
            fail("sibling evidence is pooled: " + key)
    if sibling["adjacent_wpe"]["results_pooled"] is not False:
        fail("adjacent WPE evidence is pooled")

    adverse = report["adverse"]
    configs = adverse["config_rejections"]
    if set(configs) != EXPECTED_CONFIGS:
        fail("config adverse case set mismatch")
    for name, case in configs.items():
        if name == "synthetic_weight_admission_control":
            if case["status"] != "created" or case["session_created"] is not True:
                fail("synthetic admission control was not created")
        elif case["status"] != "rejected" or case["session_created"] is not False:
            fail("config case did not fail closed: " + name)
    scenes = adverse["scene_cases"]["cases"]
    if set(scenes) != EXPECTED_SCENES:
        fail("scene adverse case set mismatch")
    for name, case in scenes.items():
        if not case["status"].startswith("rejected") or case["state_unchanged"] is not True:
            fail("scene case did not fail closed: " + name)
    if adverse["scene_cases"]["state_after_close_unchanged_by_rejected_call"] is not True:
        fail("state changed after a rejected post-close call")
    lifecycle = adverse["lifecycle"]
    if (lifecycle["one_scene_completed"] is not True
            or lifecycle["one_call_only"] is not True
            or lifecycle["close_idempotent"] is not True
            or lifecycle["zero_length_scene_rejected"] is not True):
        fail("lifecycle evidence failed")
    if not lifecycle["process_after_close"].startswith("rejected"):
        fail("post-close processing did not fail closed")
    for key in ("incremental_process_api_absent", "flush_api_absent", "reset_api_absent"):
        if lifecycle[key] is not True:
            fail("streaming API leaked into the whole-clip boundary: " + key)

    board = report["board_link"]
    if board["path"] != reference.BOARD_PATH:
        fail("board path drifted")
    if board["mutable_source_hashed"] is not False:
        fail("mutable board file is claimed as hashed")
    if board["projected_fields"] != ["id", "title", "mode"]:
        fail("board projected fields drifted")
    live_board = reference.load_board()
    if board["rows"] != reference.board_rows(live_board):
        fail("linked board rows drifted")
    if board["projection_sha256"] != reference.board_projection_sha256(live_board):
        fail("board link projection mismatch")
    if len(board["projection_sha256"]) != 64:
        fail("board projection is not a SHA-256")
    if board["depends_on"] != ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"]:
        fail("board dependency identity drifted")

    repeat = report["repeatability"]
    if repeat["count"] != 3 or repeat["byte_identical"] is not True:
        fail("repeatability is not byte-identical")
    if len(set(repeat["digests"])) != 1:
        fail("repeatability digests differ")

    gates = report["release_gates"]
    if {gate["id"] for gate in gates} != EXPECTED_GATE_IDS:
        fail("release gate id set mismatch")
    if {gate["name"] for gate in gates} != EXPECTED_GATE_NAMES:
        fail("release gate name set mismatch")
    if len(gates) != 8:
        fail("release gate count is not eight")
    for gate in gates:
        if gate["status"] != "blocked" or not gate["evidence"] or not gate["reopen"]:
            fail("a release gate is not blocked with evidence and reopening")

    blockers = " ".join(report["exact_blockers"])
    for token in ("two distinct architectures", "No rights-cleared synchronized microphone-array corpus",
                  "no torch", "No held-out task-matched"):
        if token not in blockers:
            fail("exact blocker text missing: " + token)
    for token in ("one exact implementation", "rights-cleared synchronized microphone-array corpus",
                  "pinned runnable runtime artifact", "task-matched held-out array scoring"):
        if token not in " ".join(report["reopen_conditions"]):
            fail("reopening condition missing: " + token)
    if not report["missing_evidence"] or len(report["missing_evidence"]) < 8:
        fail("missing evidence list is incomplete")

    context = report["source_reported_context"]
    if "distinct iterative framework" not in context["transform_space_row"]:
        fail("source-reported architecture context drifted")
    if "unavailable/blocked" not in context["candidate_matrix_row"]:
        fail("source-reported blocked status drifted")
    if context["reported_metric_values"] is not None:
        fail("a source-reported value was invented")
    if "none is invented" not in context["disclaimer"]:
        fail("source context disclaimer is missing")
    if "not reproduced" not in context["scope"]:
        fail("source context is not separated as provenance")

    if set(report["source_pin_paths"]) != set(reference.SOURCE_PINS):
        fail("source pin paths mismatch")
    if set(report["boundary_pin_paths"]) != set(reference.BOUNDARY_PINS):
        fail("boundary pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("local file names mismatch")
    if reference.BOARD_PATH in report["source_pin_paths"]:
        fail("mutable board path appears in source pins")
    if re.search(rb"-0\.0(?=[,\]}]\s*$|[,\]}])", reference.canonical_report_bytes(report)):
        fail("negative zero in canonical report")
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: spatial boundary, accounting, adverse cases, board gate and gates strict")


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
    if (HERE / "README.md").read_text(encoding="utf-8") != _readme_with_table():
        fail("README digest table is not byte-reproducible")
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


def _readme_with_table() -> str:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    start = text.index(cli.TABLE_START) + len(cli.TABLE_START)
    end = text.index(cli.TABLE_END)
    return text[:start] + "\n" + cli.readme_table() + "\n" + text[end:]


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
          f"decision={reference.DECISION} gates=blocked(8)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
