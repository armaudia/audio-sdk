# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-DET-05 evidence map.

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
LOCAL_PREFIX = "docs/task-evidence/survey-det-05/"


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
    _check(contract["qualification"]["decision"] == reference.DECISION, "contract qualification decision")
    _check(contract["qualification"]["status"] == reference.QUALIFICATION_STATUS, "contract qualification status")
    _check(contract["qualification"]["qualification_status"] == reference.QUALIFICATION_STATUS, "contract qualification")
    _check(contract["qualification"]["readiness"] == reference.READINESS, "contract readiness")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["qualification"]["personal_vad_local_execution_present"] is False, "contract claims a personal-VAD run")
    _check(contract["qualification"]["speaker_conditioned_neural_execution_present"] is False, "contract claims a neural run")
    _check(contract["qualification"]["enrollment_conditioned_execution_present"] is False, "contract claims enrollment execution")
    _check(contract["qualification"]["target_label_benchmark_present"] is False, "contract claims a benchmark")
    _check(contract["qualification"]["release_qualification_present"] is False, "contract claims release")
    _check(contract["category_scope"] == reference.CATEGORY_SCOPE, "contract category scope")
    _check(contract["personal_vad_boundary"] == reference.PERSONAL_VAD_BOUNDARY, "contract boundary")
    _check(contract["public_surface"] == reference.BOUNDARY, "contract public surface")
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract source pins")
    _check(contract["boundary_pins"] == reference.WORKTREE_PINS, "contract boundary pins")
    _check(reference.BOARD_PATH not in contract["source_pins"], "contract pins mutable board")
    _check(reference.BOARD_PATH not in contract["boundary_pins"], "contract pins mutable board as boundary")
    _check(contract["follow_up_policy"]["invent_new_tasks"] is False, "contract invents tasks")
    _check(contract["follow_up_policy"]["board_only"] is True, "contract is not board-only")
    _check(contract["follow_up_policy"]["allowed_modes"] == list(reference.ALLOWED_LINK_MODES), "contract modes")
    _check(len(contract["release_gates"]) == 8, "contract release gate count")
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
    _check(report["qualification_status"] == "not_qualified", "qualification is not not_qualified")
    _check(report["qualification"]["status"] == "not_qualified", "nested qualification status")
    _check(report["qualification"]["qualification_status"] == "not_qualified", "nested qualification value")
    _check(report["qualification"]["readiness"] == "incomplete", "readiness is not incomplete")
    _check(report["qualification"]["survey_status"] == "incomplete", "survey status is not incomplete")
    _check(report["qualification"]["proposal_only"] is True, "survey is not proposal-only")
    _check(report["qualification"]["qualifies"] is False, "report qualifies")
    for key in (
        "personal_vad_local_execution_present",
        "speaker_conditioned_neural_execution_present",
        "enrollment_conditioned_execution_present",
        "target_label_benchmark_present",
        "release_qualification_present",
    ):
        _check(report["qualification"][key] is False, "qualification claims a missing result: " + key)
    _check(report["readiness"] == "incomplete", "readiness changed")
    gates = report["release_gates"]
    _check(len(gates) == 8, "release gate count is not eight")
    _check([gate["id"] for gate in gates] == ["RG-0%d" % k for k in range(1, 9)], "gate ids changed")
    _check(all(gate["blocked"] is True for gate in gates), "a release gate is open")
    _check(report["taxonomy"]["id"] == reference.CATEGORY_ID, "taxonomy id")
    _check(report["taxonomy"]["name"] == "Target-speaker / personalized VAD", "taxonomy name")
    _check(report["taxonomy"]["scope"] == "discovered_extension", "taxonomy scope")
    _check(report["taxonomy"]["output_kind"] == "annotation/control", "taxonomy output kind")
    _check(report["taxonomy"]["source_ids"] == ["S52", "S53"], "taxonomy source ids")
    _check(report["taxonomy"]["related_category_ids"] == ["DET-01", "SPK-02", "SPK-05"], "related categories")
    _check(report["taxonomy"]["discovery_status"] == "catalogued", "taxonomy discovery status")
    _check(report["taxonomy"]["candidate_census_status"] == "not_started", "candidate census status")
    _check(report["taxonomy"]["benchmark_status"] == "not_started", "benchmark status")
    _check(report["category_scope"] == reference.CATEGORY_SCOPE, "report category scope")
    _check(report["category_scope"]["not_general_any_speaker_vad_category"] == "DET-01", "DET-01 boundary")
    _check(report["category_scope"]["not_target_speaker_extraction_category"] == "SPK-02", "SPK-02 boundary")
    _check(report["category_scope"]["not_speaker_representation_identification_or_verification_category"] == "SPK-05", "SPK-05 boundary")
    _check(report["personal_vad_boundary"] == reference.PERSONAL_VAD_BOUNDARY, "report personal-VAD boundary")
    _check(report["personal_vad_boundary"]["target_speaker_activity_only"] is True, "target activity rule removed")
    _check(report["personal_vad_boundary"]["three_way_classes_required"] is True, "three-class rule removed")
    _check(report["personal_vad_boundary"]["not_source_separation"] is True, "separation rule removed")
    _check(report["personal_vad_boundary"]["not_mute_or_gate_mandate"] is True, "mute rule removed")
    _check(report["personal_vad_boundary"]["not_speaker_identification_or_verification"] is True, "identity rule removed")
    _check(report["personal_vad_boundary"]["personal_vad_local_execution_present"] is False, "local run claimed")
    _check(report["personal_vad_boundary"]["compatible_checkpoint_or_weights_staged"] is False, "weights claimed")
    _check(report["personal_vad_boundary"]["enrolled_mixture_or_clean_target_reference_staged"] is False, "corpus claimed")
    _check(report["personal_vad_boundary"]["listening_or_human_validation_result"] is False, "listening claimed")
    for key in (
        "personal_vad_local_execution_present",
        "speaker_conditioned_neural_execution_present",
        "enrollment_conditioned_corpus_present",
        "compatible_checkpoint_or_weights_present",
        "target_label_benchmark_present",
        "clean_target_reference_present",
        "runnable_host_adapter_present",
        "device_timing_or_listening_present",
    ):
        _check(report["discovery"][key] is False, "discovery claim is not closed: " + key)
    _check(report["discovery"]["catalog_record_present"] is True, "catalog record not recorded")
    _check(report["discovery"]["any_speaker_vad_baseline_present"] is True, "VAD baseline not recorded")
    _check(report["discovery"]["adjacent_suppression_diagnostic_present"] is True, "adjacent diagnostic not recorded")
    _check([lead["source_id"] for lead in report["source_leads"]] == ["S52", "S53"], "source leads are not S52/S53")
    branches = {row["branch"] for row in report["method_families"]}
    _check(branches == {"classic", "ml"}, "both catalogued branches are not covered")
    families = " ".join(row["family"].lower() for row in report["method_families"])
    for keyword in (
        "standard vad plus independent speaker-scoring",
        "speaker-conditioned neural activity classification",
        "statistical speaker segmentation",
        "neural extraction",
        "diarization",
    ):
        _check(keyword in families, "catalogued family missing: " + keyword)
    coverage = report["execution_coverage"]
    _check(coverage["historical_execution_count"] == 3, "historical execution count")
    _check(coverage["historical_local_any_speaker_vad_execution_count"] == 1, "any-speaker count")
    _check(coverage["historical_local_adjacent_suppression_execution_count"] == 2, "adjacent count")
    _check(coverage["personal_vad_local_execution_count"] == 0, "personal-VAD count")
    _check(coverage["speaker_conditioned_neural_execution_count"] == 0, "neural count")
    _check(coverage["enrollment_conditioned_execution_count"] == 0, "enrollment count")
    _check(coverage["target_label_benchmark_execution_count"] == 0, "benchmark count")
    _check(coverage["dedicated_personal_vad_component_count"] == 3, "dedicated component count")
    _check(coverage["locally_evaluated_personal_vad_component_count"] == 0, "evaluated personal count")
    _check(coverage["any_speaker_vad_component_count"] == 9, "any-speaker component count")
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
    _check("sha256_at_read" not in report["mutable_provenance"], "mutable board hash is gated")
    _check(report["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    classes = report["evidence_classes"]
    for key in (
        "personal_vad_local_execution",
        "speaker_conditioned_neural_execution",
        "target_label_accuracy_claim",
        "speaker_identification_or_verification_claim",
        "source_separation_or_enhancement_claim",
        "device_timing",
        "human_validation_result",
        "listening_result",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
    ):
        _check(classes[key] is False, "unsupported evidence class: " + key)
    for key in (
        "historical_local_any_speaker_vad_baseline",
        "historical_local_adjacent_speaker_dominant_suppression",
        "historical_local_in_model_speaker_similarity_diagnostic",
        "source_only_personal_vad_protocol",
        "source_reported_candidate_gap",
        "missing_enrollment_conditioned_execution",
        "missing_target_label_benchmark",
        "missing_checkpoint_or_weights",
        "missing_clean_target_reference",
        "missing_benchmark_protocol",
    ):
        _check(classes[key] is True, "supported evidence class missing: " + key)
    for key, value in report["boundary"].items():
        _check(value is False, "boundary flag is not false: " + key)
    for key in (
        "real_speech",
        "real_corpus",
        "weights",
        "runtime_invocation",
        "enrollment_cue",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
    ):
        _check(report["scope"][key] is False, "scope flag is not false: " + key)
    for key in ("task_local_only", "documentation_and_metadata_only", "no_new_execution", "synthetic_only_where_cited"):
        _check(report["scope"][key] is True, "scope flag is not true: " + key)
    census = {row["component_id"] for row in report["component_census"]}
    for row in report["historical_executions"]:
        _check(row.get("component_ids"), "historical execution without component link: " + row["id"])
        _check(
            set(row["component_ids"]) <= census,
            "historical execution links an uncensused component: " + row["id"],
        )
        _check("not rerun by this survey" in row["scope"], "historical execution not labelled: " + row["id"])
        _check("personal" not in row["outcome_class"], "adjacent row relabelled as personal: " + row["id"])
    local = {row["id"] for row in report["historical_executions"]}
    reported = {row["id"] for row in report["reported_outcomes"]}
    _check(local and reported and not (local & reported), "local and reported outcomes are not distinct")
    for row in report["reported_outcomes"]:
        _check(row["class"].startswith("source_reported_"), "reported outcome class is not source-reported: " + row["id"])

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
    print("PASS decision=DEFER status=incomplete qualification=not_qualified")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete cold_start=3x-byte-identical scope=task-local-only")
    print("PASS mutable_board_gate=false linked_row_projection_only")
    print("PASS category=DET-05 personal_vad_local_execution=false gates=8-blocked")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
