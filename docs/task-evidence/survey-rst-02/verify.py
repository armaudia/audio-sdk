# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-RST-02 evidence map.

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
LOCAL_PREFIX = "docs/task-evidence/survey-rst-02/"
FORBIDDEN_SCOPE = (
    "real_speech",
    "real_corpus",
    "real_audio_assets",
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
)
TRUE_SCOPE = (
    "task_local_only",
    "documentation_and_metadata_only",
    "no_new_execution",
    "synthetic_only_where_cited",
    "historical_real_speech_transcribed_only",
    "historical_real_corpus_transcribed_only",
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
    _check(contract["qualification"]["decision"] == reference.DECISION, "contract decision")
    _check(contract["qualification"]["status"] == reference.QUALIFICATION_STATUS, "contract qualification status")
    _check(contract["qualification"]["qualification_status"] == reference.QUALIFICATION_STATUS, "contract qualification")
    _check(contract["qualification"]["readiness"] == reference.READINESS, "contract readiness")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["qualification"]["proposal_only"] is True, "contract proposal-only")
    _check(contract["category_scope"] == reference.CATEGORY_SCOPE, "contract category scope")
    _check(contract["bwe_boundary"] == reference.BWE_BOUNDARY, "contract BWE boundary")
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
    _check(report["qualification"]["status"] == "not_qualified", "nested qualification is not not_qualified")
    _check(report["qualification"]["decision"] == "DEFER", "nested decision is not DEFER")
    _check(report["qualification"]["readiness"] == "incomplete", "nested readiness is not incomplete")
    _check(report["qualification"]["qualifies"] is False, "nested qualification is claimed")
    _check(report["qualification"]["proposal_only"] is True, "nested proposal-only is not set")
    _check(len(report["release_gates"]) == 8, "release gate count is not eight")
    _check(all(gate["blocked"] is True for gate in report["release_gates"]), "a release gate is open")
    _check(report["taxonomy"]["id"] == reference.CATEGORY_ID, "taxonomy id")
    _check(report["taxonomy"]["name"] == "Bandwidth extension and audio super-resolution", "taxonomy name")
    _check(report["taxonomy"]["scope"] == "discovered_extension", "taxonomy scope")
    _check(report["taxonomy"]["source_ids"] == ["S29", "S45"], "taxonomy source ids")
    _check(report["taxonomy"]["discovery_status"] == "catalogued", "taxonomy discovery status")
    _check(report["taxonomy"]["candidate_census_status"] == "not_started", "candidate census status")
    _check(report["taxonomy"]["benchmark_status"] == "not_started", "benchmark status")
    _check(report["category_scope"] == reference.CATEGORY_SCOPE, "report category scope")
    _check(report["category_scope"]["not_declipping_category"] == "RST-01", "declipping boundary changed")
    _check(report["category_scope"]["not_codec_artifact_category"] == "RST-03", "codec boundary changed")
    _check(report["category_scope"]["not_packet_loss_concealment_category"] == "RST-04", "PLC boundary changed")
    _check(report["category_scope"]["resampling_is_not_bandwidth_extension"] is True, "resampling boundary changed")
    _check(report["bwe_boundary"] == reference.BWE_BOUNDARY, "report BWE boundary")
    _check(report["bwe_boundary"]["resampling_alone_recovers_missing_high_band"] is False, "resampling recovery claimed")
    _check(report["bwe_boundary"]["high_band_fidelity_established"] is False, "high-band fidelity claimed")
    _check(report["bwe_boundary"]["content_preservation_established"] is False, "content preservation claimed")
    _check(report["bwe_boundary"]["blind_cutoff_estimation_present"] is False, "blind cutoff claimed")
    _check(report["bwe_boundary"]["ml_weights_present"] is False, "weights claimed")
    _check(report["bwe_boundary"]["ml_runtime_present"] is False, "runtime claimed")
    _check(report["bwe_boundary"]["codec_integration_present"] is False, "codec integration claimed")
    _check(report["bwe_boundary"]["human_listening_result_present"] is False, "human listening claimed")
    _check(report["bwe_boundary"]["independent_heldout_benchmark_present"] is False, "held-out benchmark claimed")
    _check(report["bwe_boundary"]["target_device_timing_present"] is False, "device timing claimed")
    _check(
        report["discovery"]["classic_component_ids"] == reference.DISCOVERY["classic_component_ids"],
        "classic component discovery changed",
    )
    _check(report["discovery"]["ml_candidate_ids"] == reference.DISCOVERY["ml_candidate_ids"], "ML candidates changed")
    _check(
        report["discovery"]["bandwidth_specific_ml_candidate_ids"]
        == reference.DISCOVERY["bandwidth_specific_ml_candidate_ids"],
        "bandwidth-specific ML candidates changed",
    )
    _check(report["discovery"]["weights_present"] is False, "weights claimed")
    _check(report["discovery"]["runtime_present"] is False, "runtime claimed")
    _check(report["discovery"]["checkpoint_digest_present"] is False, "checkpoint digest claimed")
    _check(report["discovery"]["listener_panel_present"] is False, "listener panel discovered")
    _check(report["discovery"]["heldout_benchmark_present"] is False, "held-out benchmark discovered")
    _check(report["discovery"]["published_method_archive_present"] is False, "published archive discovered")
    _check(report["discovery"]["codec_integration_present"] is False, "codec integration discovered")
    _check(report["discovery"]["blind_cutoff_detector_present"] is False, "blind cutoff detector discovered")
    _check([lead["source_id"] for lead in report["source_leads"]] == ["S29", "S45"], "source lead set changed")
    for lead in report["source_leads"]:
        _check(lead["mapped_components"], "source lead has no component: " + lead["source_id"])
        _check(lead["gap_ids"], "source lead has no gap: " + lead["source_id"])
    branches = {row["branch"] for row in report["method_families"]}
    _check(branches == {"classic", "ml"}, "both catalogued branches are not covered")
    families = {row["family_id"]: row for row in report["method_families"]}
    _check("envelope" in families["MF-C1"]["family"].lower(), "classical envelope family missing")
    _check("adjacent" in families["MF-C2"]["family"].lower(), "rate-conversion boundary missing")
    _check("vocoder" in " ".join(row["family"].lower() for row in report["method_families"]), "vocoder family missing")
    _check(report["board_links"], "no board links")
    _check(report["gaps"], "no gaps mapped")
    for gap in report["gaps"]:
        _check(gap["follow_up_ids"], "gap has no board link: " + gap["id"])
        _check(gap["owner_note"], "gap has no owner note: " + gap["id"])
    for link in report["board_links"]:
        _check(
            link["mode"] in reference.ALLOWED_LINK_MODES,
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
    for key in (
        "human_listening_result",
        "high_band_fidelity_result",
        "content_preservation_result",
        "blind_cutoff_estimation_result",
        "ml_weights_or_runtime_present",
        "ml_local_execution",
        "unpaired_predictive_historical_local",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
    ):
        _check(report["evidence_classes"][key] is False, "prohibited evidence class is true: " + key)
    _check(report["evidence_classes"]["paired_synthetic_historical_local"] is True, "paired pilot class missing")
    _check(report["evidence_classes"]["historical_pilot_means_not_reproduced"] is True, "pilot class missing")
    _check(report["evidence_classes"]["local_ledger_provenance_not_reproduced"] is True, "ledger class missing")
    _check(
        report["evidence_classes"]["adjacent_rate_conversion_tooling_historical_local"] is True,
        "rate-conversion class missing",
    )
    _check(
        report["evidence_classes"]["missing_rights_qualified_paired_speech_cohort"] is True,
        "missing-cohort class missing",
    )
    _check(report["evidence_classes"]["prepared_listening_without_ratings"] is True, "prepared-listening class missing")
    _check(report["evidence_classes"]["source_reported_or_inventory_only"] is True, "source-reported class missing")
    census = {row["component_id"] for row in report["component_census"]}
    for row in report["historical_executions"]:
        _check(row.get("component_ids"), "historical execution without component link: " + row["id"])
        _check(
            set(row["component_ids"]) <= census,
            "historical execution links an uncensused component: " + row["id"],
        )
        _check("not rerun by this survey" in row["scope"], "historical row is claimed as rerun: " + row["id"])
    _check(
        {row["id"] for row in report["historical_executions"]} == {"HE-1", "HE-2", "HE-3", "HE-4"},
        "historical execution set changed",
    )
    ml_ids = set(reference.DISCOVERY["ml_candidate_ids"])
    for row in report["historical_executions"]:
        _check(not (set(row["component_ids"]) & ml_ids), "ML execution is claimed: " + row["id"])
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
    print("PASS category=RST-02 bwe_fidelity=false resampling_as_bwe=false gates=8-blocked")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete tests=state-unchanged scope=task-local-only")
    print("PASS mutable_board_gate=false linked_row_identity_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
