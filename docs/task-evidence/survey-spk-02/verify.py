# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-SPK-02 evidence map.

This script never writes. It recomputes every artifact from its pinned inputs,
checks canonical bytes and digests, verifies licensing and scope, repeats the
build in three fresh interpreter processes, and rejects any git change outside
this task directory.
"""

from __future__ import annotations

import os
import re
import subprocess
import sys
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SOURCE_LINE = re.compile(r"^([0-9a-f]{64})  (local|source|worktree):(.+)$")
LOCAL_PREFIX = "docs/task-evidence/survey-spk-02/"
FORBIDDEN_SCOPE = (
    "real_speech",
    "real_corpus",
    "weights",
    "runtime_invocation",
    "listening",
    "device_timing",
    "benchmark_claim",
    "release_claim",
    "numeric_parity_claim",
    "processor_exposure",
    "public_default",
    "network_access",
    "audio_mutation_or_deletion",
    "target_speaker_extraction_claim",
    "source_separation_claim",
    "identity_or_verification_claim",
    "personalized_vad_claim",
    "enrollment_conditioning_claim",
)
TRUE_SCOPE = (
    "task_local_only",
    "documentation_and_metadata_only",
    "no_new_execution",
    "synthetic_only_where_cited",
    "historical_real_speech_transcribed_only",
    "historical_real_corpus_transcribed_only",
)
CRITICAL_FALSE_CLASSES = (
    "spk02_local_extraction_execution",
    "enrollment_conditioned_execution",
    "target_speaker_extraction_accuracy_claim",
    "clean_target_reference_accuracy_claim",
    "real_enrolled_corpus",
    "impostor_or_target_absent_negative_set",
    "real_overlap_corpus",
    "human_listening_result",
    "device_timing",
    "new_execution_in_this_survey",
    "parity_or_qualification_claim",
    "public_default_claim",
    "release_claim",
)


class VerifyError(Exception):
    pass


def _check(condition: bool, message: str) -> None:
    if not condition:
        raise VerifyError(message)


def _check_spdx_header(name: str) -> None:
    text = (HERE / name).read_text(encoding="utf-8").splitlines()[:5]
    joined = "\n".join(text)
    _check("SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes" in joined, "missing copyright in " + name)
    _check("SPDX-License-" + "Identifier: Apache-2.0" in joined, "missing license in " + name)


def _check_licenses() -> None:
    for name in (
        "README.md",
        "reference.py",
        "run.py",
        "test_reference.py",
        "verify.py",
    ):
        _check_spdx_header(name)
    for name in (
        "contract.json.license",
        "report.json.license",
        "report.json.sha256.license",
        "SOURCES.sha256.license",
    ):
        _check((HERE / name).read_text(encoding="utf-8") == reference.LICENSE_TEXT, "bad sidecar: " + name)


def _check_git_scope(sdk_root: Path) -> None:
    process = subprocess.run(
        ["git", "-C", str(sdk_root), "status", "--porcelain=v1", "--untracked-files=all", "-z"],
        capture_output=True,
        text=True,
        check=False,
    )
    _check(process.returncode == 0, "git status failed: " + process.stderr.strip())
    for entry in process.stdout.split("\0"):
        if not entry:
            continue
        path = entry[3:]
        _check(path.startswith(LOCAL_PREFIX), "out-of-scope git change: " + path)


def _check_sources_manifest() -> None:
    raw = (HERE / "SOURCES.sha256").read_bytes()
    _check(raw == run.sources_bytes(), "SOURCES.sha256 is not byte-identical")

    lines = raw.decode("ascii").splitlines()
    parsed = []
    for line in lines:
        match = SOURCE_LINE.match(line)
        _check(match is not None, "malformed SOURCES line: " + line)
        digest, kind, path = match.groups()
        _check(".." not in Path(path).parts, "traversing SOURCES path: " + path)
        parsed.append((kind + ":" + path, digest))
    labels = [label for label, _ in parsed]
    _check(labels == sorted(labels), "SOURCES.sha256 is not sorted")
    _check(len(labels) == len(set(labels)), "SOURCES.sha256 has duplicate labels")
    _check(all(label != "local:SOURCES.sha256" for label in labels), "SOURCES.sha256 pins itself")
    _check(
        all(label not in ("source:" + reference.BOARD_PATH, "worktree:" + reference.BOARD_PATH) for label in labels),
        "mutable board file is present in SOURCES.sha256",
    )

    expected = set()
    for name in run.LOCAL_FILES:
        if name not in run.SOURCES_EXCLUDED:
            expected.add("local:" + name)
    for path in reference.SOURCE_PINS:
        expected.add("source:" + path)
    for path in reference.WORKTREE_PINS:
        expected.add("worktree:" + path)
    _check(set(labels) == expected, "SOURCES.sha256 coverage mismatch")

    workspace = reference.find_workspace()
    sdk_root = reference.find_sdk_root()
    for label, digest in parsed:
        kind, path = label.split(":", 1)
        if kind == "local":
            actual = reference.sha256_file(HERE / path)
        elif kind == "source":
            actual = reference.sha256_file(workspace / path)
        else:
            actual = reference.sha256_file(sdk_root / path)
        _check(actual == digest, "SOURCES digest mismatch: " + label)


def _check_contract() -> None:
    raw = (HERE / "contract.json").read_bytes()
    _check(raw == run.build_contract(), "contract.json is not byte-identical")
    contract = reference.strict_json_loads(raw.decode("utf-8"))
    _check(contract["SPDX-License-Identifier"] == "Apache-2.0", "contract license")
    _check(contract["task"] == reference.TASK, "contract task")
    _check(contract["category_id"] == reference.CATEGORY_ID, "contract category")
    _check(contract["legacy_family"] == reference.LEGACY_FAMILY, "contract legacy family")
    _check(contract["base_commit"] == reference.BASE_COMMIT, "contract base commit")
    _check(contract["status"] == reference.STATUS, "contract status")
    _check(contract["decision"] == reference.DECISION, "contract decision")
    _check(contract["qualification"]["status"] == reference.QUALIFICATION_STATUS, "contract qualification status")
    _check(contract["qualification"]["readiness"] == reference.READINESS, "contract readiness")
    _check(contract["qualification"]["survey_status"] == "incomplete", "contract survey status")
    _check(contract["qualification"]["proposal_only"] is True, "contract proposal-only")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["category_scope"] == reference.CATEGORY_SCOPE, "contract category scope")
    _check(contract["tse_boundary"] == reference.TSE_BOUNDARY, "contract TSE boundary")
    _check(contract["public_surface"] == reference.BOUNDARY, "contract public surface")
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract source pins")
    _check(contract["boundary_pins"] == reference.WORKTREE_PINS, "contract boundary pins")
    _check(reference.BOARD_PATH not in contract["source_pins"], "contract pins mutable board")
    _check(reference.BOARD_PATH not in contract["boundary_pins"], "contract pins mutable board as boundary")
    _check(contract["follow_up_policy"]["invent_new_tasks"] is False, "contract invents tasks")
    _check(contract["follow_up_policy"]["board_only"] is True, "contract is not board-only")
    _check(contract["follow_up_policy"]["linked_row_identity_only"] is True, "contract gates more than identity")
    expected_artifacts = set(run.LOCAL_FILES) - set(run.CONTRACT_EXCLUDED)
    _check(set(contract["artifact_pins"]) == expected_artifacts, "contract artifact coverage")
    _check("contract.json" not in contract["artifact_pins"], "contract pins itself")
    _check("SOURCES.sha256" not in contract["artifact_pins"], "contract pins SOURCES")
    _check(contract["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    _check("sha256_at_read" not in contract["mutable_provenance"], "mutable board hash is gated")


def _check_report() -> str:
    raw = (HERE / "report.json").read_bytes()
    expected = reference.canonical_bytes(reference.build_report())
    _check(raw == expected, "report.json is not byte-identical")
    report = reference.strict_json_loads(raw.decode("utf-8"))
    _check(report["task"] == reference.TASK, "report task")
    _check(report["category_id"] == reference.CATEGORY_ID, "report category")
    _check(report["legacy_family"] == reference.LEGACY_FAMILY, "report legacy family")
    _check(report["decision"] == "DEFER", "decision is not DEFER")
    _check(report["status"] == reference.STATUS, "status changed")
    _check("incomplete" in report["status"], "status is not incomplete")
    _check(report["qualification"]["status"] == "not_qualified", "qualification is not not_qualified")
    _check(report["qualification"]["readiness"] == "incomplete", "readiness is not incomplete")
    _check(report["qualification"]["survey_status"] == "incomplete", "survey status is not incomplete")
    _check(report["qualification"]["proposal_only"] is True, "survey is not proposal-only")
    _check(report["qualification"]["qualifies"] is False, "report qualifies")
    gates = report["release_gates"]
    _check(len(gates) == 8, "release gate count is not eight")
    _check([gate["id"] for gate in gates] == ["RG-0%d" % k for k in range(1, 9)], "gate ids changed")
    _check(all(gate["blocked"] is True for gate in gates), "a release gate is open")
    _check(report["taxonomy"]["id"] == reference.CATEGORY_ID, "taxonomy id")
    _check(
        report["taxonomy"]["name"] == "Target-speaker extraction and personalized enhancement",
        "taxonomy name",
    )
    _check(report["taxonomy"]["scope"] == "requested", "taxonomy scope")
    _check(report["taxonomy"]["output_kind"] == "waveform", "taxonomy output kind")
    _check(report["taxonomy"]["source_ids"] == ["S07", "S50"], "taxonomy source ids")
    _check(report["taxonomy"]["discovery_status"] == "catalogued", "taxonomy discovery status")
    _check(report["taxonomy"]["candidate_census_status"] == "not_started", "candidate census status")
    _check(report["taxonomy"]["benchmark_status"] == "not_started", "benchmark status")
    _check(report["legacy_backlog"]["family_id"] == "F05", "legacy family")
    _check(report["legacy_backlog"]["state"] == "catalogued", "legacy backlog state")
    _check(report["category_scope"] == reference.CATEGORY_SCOPE, "report category scope")
    _check(report["category_scope"]["not_generic_source_separation"] == "SPK-01", "SPK-01 boundary changed")
    _check(report["category_scope"]["not_personalized_vad_or_target_activity"] == "DET-05", "DET-05 boundary changed")
    _check(
        report["category_scope"]["not_speaker_identification_or_verification"] == "SPK-05",
        "SPK-05 boundary changed",
    )
    _check(report["category_scope"]["not_anonymous_diarization"] == "SPK-04", "SPK-04 boundary changed")
    _check(report["category_scope"]["not_beamforming_or_spatial_filtering_category"] == "CLN-07", "CLN-07 boundary changed")
    _check(
        report["category_scope"]["identity_match_does_not_define_desired_speaker"] is True,
        "identity boundary changed",
    )
    _check(report["tse_boundary"] == reference.TSE_BOUNDARY, "report TSE boundary")
    for key in (
        "enrollment_conditioned_execution_present",
        "clean_target_reference_corpus_present",
        "real_overlap_corpus_present",
        "impostor_or_target_absent_negative_set_present",
        "ml_weights_present",
        "ml_runtime_present",
        "target_selected_output_measured",
        "human_listening_result_present",
        "device_timing_present",
        "independent_heldout_benchmark_present",
        "public_default_present",
        "release_approved",
    ):
        _check(report["tse_boundary"][key] is False, "TSE boundary claim is true: " + key)
    for key in (
        "enrollment_is_an_input_facet_not_a_target_definition",
        "spatial_cue_is_an_input_facet_not_an_identity",
        "visual_cue_is_an_input_facet_not_an_identity",
        "generic_separation_is_not_target_selection",
        "competing_speaker_suppression_is_not_target_extraction",
        "target_mask_ratio_without_target_quality_is_insufficient",
        "personal_vad_activity_is_not_a_waveform",
    ):
        _check(report["tse_boundary"][key] is True, "TSE boundary flag missing: " + key)
    _check([lead["source_id"] for lead in report["source_leads"]] == ["S07", "S50"], "source lead set changed")
    for lead in report["source_leads"]:
        _check(lead["mapped_components"], "source lead has no component: " + lead["source_id"])
        _check(lead["gap_ids"], "source lead has no gap: " + lead["source_id"])
    branches = {row["branch"] for row in report["method_families"]}
    _check(branches == {"classic", "ml"}, "both catalogued branches are not covered")
    families = {row["family_id"]: row for row in report["method_families"]}
    _check("cue-based" in families["MF-C1"]["family"].lower(), "classic cue filtering family missing")
    _check("statistical" in families["MF-C2"]["family"].lower(), "open statistical family missing")
    _check(
        "speaker-conditioned" in families["MF-M1"]["family"].lower(),
        "speaker-conditioned ML family missing",
    )
    _check("cue-conditioned" in families["MF-M2"]["family"].lower(), "other cue-conditioned family missing")
    _check(
        families["MF-M1"]["status"] == "candidate_only_blocked_no_local_execution",
        "VoiceFilter family is not blocked",
    )
    _check(report["board_links"], "no board links")
    _check(report["gaps"], "no gaps mapped")
    for gap in report["gaps"]:
        _check(gap["follow_up_ids"], "gap has no board link: " + gap["id"])
        _check(gap["owner_note"], "gap has no owner note: " + gap["id"])
    for link in report["board_links"]:
        _check(link["mode"] in reference.ALLOWED_LINK_MODES, "unexpected link mode")
        _check(link["linked_gaps"], "board link has no gap: " + link["task_id"])
    _check(
        report["board_link_projection_sha256"]
        == reference._board_projection(
            reference.strict_json_load(reference.find_workspace() / reference.BOARD_PATH)
        ),
        "board link projection mismatch",
    )
    _check(report["source_pins"] == reference.SOURCE_PINS, "report source pins")
    _check(report["boundary_pins"] == reference.WORKTREE_PINS, "report boundary pins")
    _check(reference.BOARD_PATH not in report["source_pins"], "report pins mutable board")
    _check(reference.BOARD_PATH not in report["boundary_pins"], "report pins mutable board as boundary")
    _check(report["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    _check("sha256_at_read" not in report["mutable_provenance"], "mutable board hash is gated")
    for key in CRITICAL_FALSE_CLASSES:
        _check(report["evidence_classes"][key] is False, "prohibited evidence class is true: " + key)
    for key in (
        "source_only_tse_protocol",
        "source_excerpt_audiovisual_tse_protocol",
        "source_reported_tse_candidate",
        "source_reported_candidate_documentation",
        "source_reported_vendor_voice_isolation_benchmark",
        "adjacent_primary_background_suppression_local",
        "adjacent_speaker_dominant_suppression_local",
        "adjacent_in_model_speaker_similarity_diagnostic",
        "adjacent_spatial_and_generic_separation",
    ):
        _check(report["evidence_classes"][key] is True, "supported evidence class is missing: " + key)
    census = {row["component_id"] for row in report["component_census"]}
    for row in report["historical_executions"]:
        _check(row.get("component_ids"), "historical execution without component link: " + row["id"])
        _check(
            set(row["component_ids"]) <= census,
            "historical execution links an uncensused component: " + row["id"],
        )
        _check(row.get("adjacent") is True, "historical execution is not adjacent: " + row["id"])
        _check(
            row.get("not_component_evidence") is True,
            "adjacent execution is presented as component evidence: " + row["id"],
        )
        _check("not rerun by this survey" in row["scope"], "historical row is claimed as rerun: " + row["id"])
    _check(
        {row["id"] for row in report["historical_executions"]} == {"HE-1", "HE-2"},
        "historical execution set changed",
    )
    for row in report["historical_executions"]:
        _check("hush" in row["component_ids"], "Hush row lost its component: " + row["id"])
        _check(
            "adjacent" in row["outcome_class"],
            "historical row is not classed adjacent: " + row["id"],
        )
    local = {row["id"] for row in report["historical_executions"]}
    reported = {row["id"] for row in report["reported_outcomes"]}
    _check(local and reported and not (local & reported), "local and reported outcomes are not distinct")
    for row in report["reported_outcomes"]:
        _check("source" in row["class"], "reported outcome is not source-scoped: " + row["id"])
    for key, value in report["boundary"].items():
        _check(value is False, "boundary flag is not false: " + key)
    for key in TRUE_SCOPE:
        _check(report["scope"][key] is True, "scope flag is not true: " + key)
    for key in FORBIDDEN_SCOPE:
        _check(report["scope"][key] is False, "scope flag is not false: " + key)

    digest = reference.sha256_bytes(raw)
    digest_raw = (HERE / "report.json.sha256").read_bytes()
    _check(digest_raw == (digest + "  report.json\n").encode("ascii"), "report.json.sha256 mismatch")
    return digest


def _check_cold_start(expected: bytes) -> None:
    script = (
        "import sys; sys.path.insert(0, %r); import reference; "
        "sys.stdout.buffer.write(reference.canonical_bytes(reference.build_report()))" % str(HERE)
    )
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for attempt in range(3):
        process = subprocess.run(
            [sys.executable, "-c", script],
            capture_output=True,
            env=env,
            check=False,
        )
        _check(process.returncode == 0, "cold-start build failed: " + process.stderr.decode("utf-8", "replace"))
        _check(process.stdout == expected, "cold-start build %d is not byte-identical" % (attempt + 1))


def main() -> int:
    try:
        workspace = reference.find_workspace()
        sdk_root = reference.find_sdk_root()
        reference._check_document_pins(workspace, sdk_root)
        reference._check_anchors(workspace, sdk_root)
        # Strict parse of every JSON artifact; duplicate keys/nonfinite fail here.
        for name in ("report.json", "contract.json"):
            reference.strict_json_loads((HERE / name).read_text(encoding="utf-8"))
        unexpected = sorted(p.name for p in HERE.iterdir() if p.name not in set(run.LOCAL_FILES))
        _check(not unexpected, "unexpected task-local files: " + ",".join(unexpected))
        _check_licenses()
        _check_git_scope(sdk_root)
        _check_sources_manifest()
        _check_contract()
        digest = _check_report()
        _check_cold_start((HERE / "report.json").read_bytes())
    except (VerifyError, reference.MapError, OSError, ValueError) as exc:
        print("FAIL " + str(exc), file=sys.stderr)
        return 1
    print("PASS decision=DEFER status=proposal_only_survey_incomplete qualification=not_qualified")
    print("PASS category=SPK-02 extraction=false separation_as_extraction=false gates=8-blocked")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete cold_start=3x-byte-identical scope=task-local-only")
    print("PASS mutable_board_gate=false linked_row_identity_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
