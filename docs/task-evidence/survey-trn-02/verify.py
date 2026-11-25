# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-TRN-02 evidence map.

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

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

import reference  # noqa: E402
import run  # noqa: E402

SOURCE_LINE = re.compile(r"^([0-9a-f]{64})  (local|source|worktree):(.+)$")
LOCAL_PREFIX = "docs/task-evidence/survey-trn-02/"


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
    _check(contract["category_id"] == "TRN-02", "contract category")
    _check(contract["legacy_family"] == "F13", "contract legacy family")
    _check(contract["base_commit"] == reference.BASE_COMMIT, "contract base commit")
    _check(contract["status"] == reference.STATUS, "contract status")
    _check(contract["decision"] == "DEFER", "contract decision")
    _check(contract["qualification"]["status"] == "not_qualified", "contract qualification")
    _check(contract["qualification"]["qualification_status"] == "not_qualified", "contract qualification_status")
    _check(contract["qualification"]["readiness"] == "incomplete", "contract readiness")
    _check(contract["qualification"]["decision"] == "DEFER", "contract qualification decision")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["qualification"]["proposal_only"] is True, "contract is not proposal-only")
    _check(contract["public_surface"] == reference.BOUNDARY, "contract public surface")
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract source pins")
    _check(contract["boundary_pins"] == reference.WORKTREE_PINS, "contract boundary pins")
    _check(len(contract["release_gates"]) == 8, "contract release gate count")
    expected_artifacts = set(run.LOCAL_FILES) - set(run.CONTRACT_EXCLUDED)
    _check(set(contract["artifact_pins"]) == expected_artifacts, "contract artifact coverage")
    _check("contract.json" not in contract["artifact_pins"], "contract pins itself")
    _check("SOURCES.sha256" not in contract["artifact_pins"], "contract pins SOURCES")
    _check(contract["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    _check("sha256_at_read" not in contract["mutable_provenance"], "mutable board hash is gated")
    _check(contract["follow_up_policy"]["invent_new_tasks"] is False, "contract invents tasks")
    _check(
        set(contract["follow_up_policy"]["linked_task_ids"])
        == {link["task_id"] for link in reference.BOARD_LINKS},
        "contract follow-up ids differ from board links",
    )


def _check_report() -> str:
    raw = (HERE / "report.json").read_bytes()
    expected = reference.canonical_bytes(reference.build_report())
    _check(raw == expected, "report.json is not byte-identical")
    report = reference.strict_json_loads(raw.decode("utf-8"))
    _check(report["decision"] == "DEFER", "decision is not DEFER")
    _check(report["status"] == reference.STATUS, "status changed")
    _check("incomplete" in report["status"], "status is not incomplete")
    _check(report["qualification"]["status"] == "not_qualified", "qualification is not not_qualified")
    _check(report["qualification"]["qualification_status"] == "not_qualified", "qualification_status differs")
    _check(report["qualification"]["readiness"] == "incomplete", "readiness is not incomplete")
    _check(report["qualification"]["survey_status"] == "incomplete", "survey status is not incomplete")
    _check(report["qualification"]["proposal_only"] is True, "survey is not proposal-only")
    _check(report["qualification"]["qualifies"] is False, "report qualifies")
    _check(report["qualification"]["designated_pitch_shift_execution_present"] is False, "pitch shift promoted")
    _check(report["qualification"]["formant_preservation_measurement_present"] is False, "formant promoted")
    _check(report["qualification"]["prosody_editing_execution_present"] is False, "prosody promoted")
    _check(report["qualification"]["human_listening_result_present"] is False, "listening promoted")
    gates = report["release_gates"]
    _check(len(gates) == 8, "release gate count is not eight")
    _check([gate["id"] for gate in gates] == ["RG-0%d" % k for k in range(1, 9)], "gate ids changed")
    _check(all(gate["blocked"] is True for gate in gates), "a release gate is open")
    _check(report["taxonomy"]["id"] == "TRN-02", "taxonomy id changed")
    _check(report["taxonomy"]["scope"] == "discovered_extension", "taxonomy scope changed")
    _check(report["taxonomy"]["source_ids"] == ["S34", "S35"], "taxonomy source leads changed")
    _check(report["legacy_backlog"]["family_id"] == "F13", "legacy family changed")
    _check(
        report["category_scope"]["pitch_shift_formant_preservation_and_full_prosody_differ"] is True,
        "pitch/formant/prosody boundary",
    )
    _check(report["category_scope"]["emotion_manipulation_out_of_scope"] is True, "emotion boundary")
    _check(
        report["category_scope"]["rate_change_is_not_designated_pitch_shift"] is True,
        "rate/pitch boundary",
    )
    _check(report["scope"]["no_new_execution"] is True, "survey claims a new execution")
    _check(report["scope"]["historical_citations_include_real_speech"] is True, "historical speech scope")
    _check(
        report["scope"]["historical_citations_include_synthetic_proxies"] is True,
        "synthetic proxy scope",
    )
    for key in (
        "real_speech_used_here",
        "real_corpus_used_here",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "designated_pitch_shift_here",
        "formant_preservation_measured_here",
        "prosody_editing_here",
        "emotion_manipulation_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "perceptual_pitch_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        _check(report["scope"][key] is False, "scope must stay closed: " + key)
    _check(report["non_claims"], "non-claims are missing")
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
    _check("sha256_at_read" not in report["mutable_provenance"], "mutable board hash is gated")
    classes = report["evidence_classes"]
    for key in (
        "designated_pitch_shift_execution",
        "formant_preservation_measurement",
        "full_prosody_editing_execution",
        "emotion_manipulation",
        "perceptual_pitch_accuracy",
        "human_listening_result",
        "real_speech_used_here",
        "real_corpus_benchmark",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "device_timing",
        "latency_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "release_claim",
        "benchmark_claim",
        "processor_exposure",
        "public_default",
        "network_access",
    ):
        _check(classes[key] is False, "unsupported evidence class: " + key)
    _check(classes["historical_research_rate_f0_proxy"] is True, "historical F0 proxy missing")
    _check(classes["task_local_synthetic_pitch_proxy"] is True, "task-local pitch proxy missing")
    _check(classes["source_reported_vocoder_documentation"] is True, "vocoder documentation missing")
    _check(classes["source_reported_prosody_audit"] is True, "prosody audit missing")
    _check(
        {row["branch"] for row in report["method_families"]} == {"classic", "ml"},
        "both catalogued method branches must be covered",
    )
    _check(
        {lead["source_id"] for lead in report["source_leads"]} == {"S34", "S35"},
        "source lead coverage mismatch",
    )
    census = {row["component_id"] for row in report["component_census"]}
    for row in report["historical_executions"]:
        _check(row.get("component_ids"), "historical execution without component link: " + row["id"])
        _check(
            set(row["component_ids"]) <= census,
            "historical execution links an uncensused component: " + row["id"],
        )
        _check(row.get("scope_class") == "historical_research_execution", "execution scope class: " + row["id"])
        _check(row.get("merged_task_evidence") is False, "execution promoted to merged evidence: " + row["id"])
        _check(row.get("not_rerun") is True, "execution is not marked unrerun: " + row["id"])
        _check("not rerun by this survey" in row["scope"], "execution scope is not bounded: " + row["id"])
        _check(row.get("values"), "execution has no values: " + row["id"])
    for row in report["local_evidence"]:
        _check(row["component_id"] in census, "local evidence links an uncensused component: " + row["id"])
        _check(row["path"] in reference.WORKTREE_PINS, "local evidence path is unpinned: " + row["id"])
        _check(
            row["sha256"] == reference.WORKTREE_PINS[row["path"]],
            "local evidence digest mismatch: " + row["id"],
        )
        _check(row["evidence_class"] == "task_local_synthetic_pitch_proxy", "local evidence class: " + row["id"])
        _check(row["qualifies_candidate"] is False, "local evidence promoted: " + row["id"])
        _check("not a designated pitch-shift" in row["scope"], "local evidence scope: " + row["id"])
        _check(row["not_measured"], "local evidence hides gaps: " + row["id"])
    outcome = report["local_vs_reported_outcomes"]
    _check(
        outcome["reported"]["classification"] == "source_reported_not_reproduced",
        "reported outcome classification",
    )
    _check(
        outcome["local"]["classification"] == "task_local_synthetic_reference_only",
        "local outcome classification",
    )
    _check(outcome["reported"]["qualifies_candidate"] is False, "reported outcome promoted")
    _check(outcome["local"]["qualifies_candidate"] is False, "local outcome promoted")
    _check(outcome["cross_comparison"]["performed"] is False, "cross comparison performed")
    _check(outcome["cross_comparison"]["numeric_parity_claimed"] is False, "numeric parity claimed")
    for row in outcome["ledger"]:
        _check(row["comparison_performed"] is False, "ledger comparison promoted")
        _check(row["qualifies_candidate"] is False, "ledger candidate promoted")
    local = {row["id"] for row in report["historical_executions"]}
    reported = {row["id"] for row in report["reported_outcomes"]}
    _check(local and reported and not (local & reported), "local and reported outcomes are not distinct")
    for row in report["reported_outcomes"]:
        _check(row["class"].startswith("source_reported_"), "reported outcome class: " + row["id"])

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
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete cold_start=3x-byte-identical scope=task-local-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
