# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-CLN-07 evidence map.

This script never writes. It recomputes every artifact from its pinned inputs,
checks canonical bytes and digests, verifies licensing and scope, and rejects
any git change outside this task directory.
"""

from __future__ import annotations

import re
import subprocess
import sys
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

SOURCE_LINE = re.compile(r"^([0-9a-f]{64})  (local|source|worktree):(.+)$")
LOCAL_PREFIX = "docs/task-evidence/survey-cln-07/"


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
    _check(contract["qualification"]["decision"] == reference.DECISION, "contract decision")
    _check(contract["qualification"]["status"] == reference.QUALIFICATION_STATUS, "contract qualification status")
    _check(contract["qualification"]["qualification_status"] == reference.QUALIFICATION_STATUS, "contract qualification")
    _check(contract["qualification"]["readiness"] == reference.READINESS, "contract readiness")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["category_scope"] == reference.CATEGORY_SCOPE, "contract category scope")
    _check(contract["spatial_boundary"] == reference.SPATIAL_BOUNDARY, "contract spatial boundary")
    _check(contract["adjacent_boundary"] == reference.ADJACENT_BOUNDARY, "contract adjacent boundary")
    _check(contract["public_surface"] == reference.BOUNDARY, "contract public surface")
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract source pins")
    _check(contract["boundary_pins"] == reference.WORKTREE_PINS, "contract boundary pins")
    _check(reference.BOARD_PATH not in contract["source_pins"], "contract pins mutable board")
    _check(reference.BOARD_PATH not in contract["boundary_pins"], "contract pins mutable board as boundary")
    _check(contract["follow_up_policy"]["invent_new_tasks"] is False, "contract invents tasks")
    _check(contract["follow_up_policy"]["board_only"] is True, "contract is not board-only")
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
    _check(report["qualification_status"] == "not_qualified", "qualification is not not_qualified")
    _check(report["readiness"] == "incomplete", "readiness is not incomplete")
    _check(report["qualification"]["status"] == "not_qualified", "qualification object status")
    _check(report["qualification"]["decision"] == "DEFER", "qualification object decision")
    _check(report["qualification"]["readiness"] == "incomplete", "qualification object readiness")
    _check(report["qualification"]["proposal_only"] is True, "qualification is not proposal-only")
    _check(report["qualification"]["qualifies"] is False, "qualification object qualifies")
    _check(len(report["release_gates"]) == 8, "release gate count is not eight")
    _check(all(gate["blocked"] is True for gate in report["release_gates"]), "a release gate is open")
    _check(report["taxonomy"]["id"] == reference.CATEGORY_ID, "taxonomy id")
    _check(report["taxonomy"]["name"] == "Beamforming and spatial filtering", "taxonomy name")
    _check(report["taxonomy"]["scope"] == "discovered_extension", "taxonomy scope")
    _check(report["taxonomy"]["source_ids"] == ["S24", "S25"], "taxonomy source ids")
    _check(report["taxonomy"]["discovery_status"] == "catalogued", "taxonomy discovery status")
    _check(report["taxonomy"]["candidate_census_status"] == "not_started", "candidate census status")
    _check(report["taxonomy"]["benchmark_status"] == "not_started", "benchmark status")
    _check(report["category_scope"] == reference.CATEGORY_SCOPE, "report category scope")
    _check(report["category_scope"]["not_localization_category"] == "CLN-08", "CLN-08 boundary")
    _check(report["category_scope"]["not_dereverberation_category"] == "CLN-04", "CLN-04 boundary")
    _check(report["category_scope"]["not_source_separation_category"] == "SPK-01", "SPK-01 boundary")
    _check(report["category_scope"]["not_target_speaker_extraction_category"] == "SPK-02", "SPK-02 boundary")
    _check(report["spatial_boundary"] == reference.SPATIAL_BOUNDARY, "report spatial boundary")
    _check(report["spatial_boundary"]["synchronized_array_channels_required"] is True, "array requirement removed")
    _check(report["spatial_boundary"]["array_geometry_and_channel_calibration_in_contract"] is True, "geometry removed")
    _check(report["spatial_boundary"]["oracle_and_estimated_mask_groups_are_separate"] is True, "oracle groups merged")
    _check(report["spatial_boundary"]["adjacent_multichannel_dereverberation_is_not_beamforming"] is True, "WPE pooled")
    _check(report["spatial_boundary"]["real_array_corpus_staged"] is False, "array corpus claimed")
    _check(report["spatial_boundary"]["pinned_beamformer_source_or_runtime_staged"] is False, "beamformer runtime claimed")
    _check(report["spatial_boundary"]["neural_spatial_weights_staged"] is False, "neural weights claimed")
    _check(report["spatial_boundary"]["array_timing_or_geometry_measured"] is False, "array timing claimed")
    _check(report["spatial_boundary"]["human_listening_result"] is False, "human listening claimed")
    for key in (
        "real_array_corpus_staged",
        "pinned_beamformer_source_or_runtime_staged",
        "neural_spatial_weights_present",
        "array_geometry_or_calibration_measured",
        "independent_heldout_array_split_present",
        "real_provider_runtime_parity_present",
    ):
        _check(report["discovery"][key] is False, "discovery claim is not closed: " + key)
    _check([lead["source_id"] for lead in report["source_leads"]] == ["S24", "S25"], "source leads are not S24/S25")
    branches = {row["branch"] for row in report["method_families"]}
    _check(branches == {"classic", "ml"}, "both catalogued branches are not covered")
    families = " ".join(row["family"].lower() for row in report["method_families"])
    _check("delay-and-sum" in families, "delay-and-sum family missing")
    _check("mvdr" in families, "MVDR/MPDR family missing")
    _check("learned masks" in families, "mask-based family missing")
    _check("neural spatial" in families, "neural spatial family missing")
    _check(report["board_links"], "no board links")
    _check(report["gaps"], "no gaps mapped")
    for gap in report["gaps"]:
        _check(gap["follow_up_ids"], "gap has no board link: " + gap["id"])
        _check(gap["owner_note"], "gap has no owner note: " + gap["id"])
    for link in report["board_links"]:
        _check(
            link["mode"] in ("feasibility", "research-control", "foundation", "external-adapter"),
            "unexpected link mode",
        )
        _check(link["linked_gaps"], "board link has no gap: " + link["task_id"])
    _check(
        report["board_link_projection_sha256"] == reference._board_projection(
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
    _check(report["adjacent_boundary"] == reference.ADJACENT_BOUNDARY, "report adjacent boundary")
    _check(report["adjacent_boundary"]["pooled_with_cln_07"] is False, "adjacent WPE pooled")
    _check(report["adjacent_boundary"]["results_promoted"] is False, "adjacent WPE promoted")
    _check(report["evidence_classes"]["new_execution_in_this_survey"] is False, "new execution claim")
    _check(report["evidence_classes"]["parity_or_qualification_claim"] is False, "parity/qualification claim")
    _check(report["evidence_classes"]["classic_beamformer_execution"] is False, "classic beamformer claim")
    _check(report["evidence_classes"]["neural_spatial_model_execution"] is False, "neural spatial claim")
    _check(report["evidence_classes"]["array_geometry_or_calibration_measured"] is False, "array calibration claim")
    _check(report["evidence_classes"]["independent_heldout_benchmark"] is False, "held-out benchmark claim")
    _check(report["evidence_classes"]["human_listening_result"] is False, "human listening result claim")
    _check(report["evidence_classes"]["device_timing"] is False, "device timing claim")
    _check(report["evidence_classes"]["release_claim"] is False, "release claim")
    _check(report["evidence_classes"]["source_only_beamformer_documentation"] is True, "source-only class missing")
    _check(report["evidence_classes"]["adjacent_multichannel_synthetic_historical_local"] is True, "adjacent class missing")
    census = {row["component_id"] for row in report["component_census"]}
    for row in report["historical_executions"]:
        _check(row.get("component_ids"), "historical execution without component link: " + row["id"])
        _check(
            set(row["component_ids"]) <= census,
            "historical execution links an uncensused component: " + row["id"],
        )
        _check(
            row["outcome_class"] == "historical_local_adjacent_multichannel_dereverberation",
            "historical execution is not adjacent: " + row["id"],
        )
        _check("not a beamforming result" in row["scope"], "historical execution is not bounded: " + row["id"])
        _check("not rerun by this survey" in row["scope"], "historical execution not labelled: " + row["id"])
    for family in report["method_families"]:
        _check(
            not (set(family["components"]) & set(report["adjacent_boundary"]["components"])),
            "adjacent WPE appears in a method family",
        )
    for key, value in report["boundary"].items():
        _check(value is False, "boundary flag is not false: " + key)
    for key in (
        "real_speech",
        "real_corpus",
        "real_array_audio",
        "weights",
        "runtime_invocation",
        "listening",
        "device_timing",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
    ):
        _check(report["scope"][key] is False, "scope flag is not false: " + key)
    for key in ("task_local_only", "documentation_and_metadata_only", "no_new_execution", "synthetic_only_where_cited"):
        _check(report["scope"][key] is True, "scope flag is not true: " + key)

    digest = reference.sha256_bytes(raw)
    digest_raw = (HERE / "report.json.sha256").read_bytes()
    _check(digest_raw == (digest + "  report.json\n").encode("ascii"), "report.json.sha256 mismatch")
    return digest


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
    except (VerifyError, reference.MapError, OSError, ValueError) as exc:
        print("FAIL " + str(exc), file=sys.stderr)
        return 1
    print("PASS decision=DEFER status=incomplete qualification=not_qualified")
    print("PASS category=CLN-07 beamforming_spatial_filtering=true gates=8-blocked")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete tests=state-unchanged scope=task-local-only")
    print("PASS mutable_board_gate=false linked_row_projection_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
