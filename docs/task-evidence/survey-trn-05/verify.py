# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-TRN-05 evidence map.

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
LOCAL_PREFIX = "docs/task-evidence/survey-trn-05/"


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
        all(
            label not in ("source:" + reference.BOARD_PATH, "worktree:" + reference.BOARD_PATH)
            for label in labels
        ),
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
    _check(contract["category_id"] == "TRN-05", "contract category")
    _check(contract["legacy_family"] == "F14", "contract legacy family")
    _check(contract["base_commit"] == reference.BASE_COMMIT, "contract base commit")
    _check(contract["claim_base_commit"] == reference.CLAIM_BASE_COMMIT, "contract claim base commit")
    _check(reference.CLAIM_BASE_COMMIT == "39b8885da4fc3ef8e27becf5df5f0658da3baf65", "claim base drift")
    _check(contract["status"] == reference.STATUS, "contract status")
    _check(contract["decision"] == "DEFER", "contract decision")
    _check(contract["qualification"]["status"] == "not_qualified", "contract qualification")
    _check(contract["qualification"]["qualification_status"] == "not_qualified", "contract qualification_status")
    _check(contract["qualification"]["readiness"] == "incomplete", "contract readiness")
    _check(contract["qualification"]["decision"] == "DEFER", "contract qualification decision")
    _check(contract["qualification"]["qualifies"] is False, "contract qualifies")
    _check(contract["qualification"]["proposal_only"] is True, "contract is not proposal-only")
    _check(
        contract["qualification"]["reference_conditioned_tts_evaluation_present"] is False,
        "contract promotes a TTS evaluation",
    )
    _check(
        contract["qualification"]["reference_similarity_present"] is False,
        "contract promotes reference similarity",
    )
    _check(
        contract["qualification"]["naturalness_listening_present"] is False,
        "contract promotes naturalness listening",
    )
    _check(
        contract["qualification"]["streaming_first_audio_present"] is False,
        "contract promotes streaming first-audio",
    )
    _check(contract["public_surface"] == reference.BOUNDARY, "contract public surface")
    _check(contract["scope"] == reference.SCOPE, "contract scope")
    _check(contract["source_pins"] == reference.SOURCE_PINS, "contract source pins")
    _check(contract["boundary_pins"] == reference.WORKTREE_PINS, "contract boundary pins")
    _check(reference.BOARD_PATH not in contract["source_pins"], "contract pins mutable board")
    _check(reference.BOARD_PATH not in contract["boundary_pins"], "contract pins mutable board")
    _check(len(contract["release_gates"]) == 8, "contract release gate count")
    expected_artifacts = set(run.LOCAL_FILES) - set(run.CONTRACT_EXCLUDED)
    _check(set(contract["artifact_pins"]) == expected_artifacts, "contract artifact coverage")
    _check("contract.json" not in contract["artifact_pins"], "contract pins itself")
    _check("SOURCES.sha256" not in contract["artifact_pins"], "contract pins SOURCES")
    _check(contract["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    _check("sha256_at_read" not in contract["mutable_provenance"], "mutable board hash is gated")
    _check(contract["follow_up_policy"]["invent_new_tasks"] is False, "contract invents tasks")
    _check(contract["follow_up_policy"]["board_only"] is True, "contract is not board-only")
    _check(
        contract["follow_up_policy"]["linked_task_ids"]
        == sorted(link["task_id"] for link in reference.BOARD_LINKS),
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
    _check(
        report["qualification"]["reference_conditioned_tts_evaluation_present"] is False,
        "TTS evaluation promoted",
    )
    _check(report["qualification"]["reference_similarity_present"] is False, "reference similarity promoted")
    _check(report["qualification"]["naturalness_listening_present"] is False, "listening promoted")
    _check(report["qualification"]["streaming_first_audio_present"] is False, "first audio promoted")
    gates = report["release_gates"]
    _check(len(gates) == 8, "release gate count is not eight")
    _check([gate["id"] for gate in gates] == ["RG-0%d" % k for k in range(1, 9)], "gate ids changed")
    _check(all(gate["blocked"] is True for gate in gates), "a release gate is open")
    _check(report["taxonomy"]["id"] == "TRN-05", "taxonomy id changed")
    _check(report["taxonomy"]["scope"] == "requested_optional_adjacent", "taxonomy scope changed")
    _check(report["taxonomy"]["output_kind"] == "waveform", "taxonomy output kind changed")
    _check(report["taxonomy"]["source_ids"] == ["S40"], "taxonomy source leads changed")
    _check(report["taxonomy"]["discovery_status"] == "catalogued", "discovery status changed")
    _check(report["taxonomy"]["candidate_census_status"] == "not_started", "census status changed")
    _check(report["taxonomy"]["benchmark_status"] == "not_started", "benchmark status changed")
    _check(report["legacy_backlog"]["family_id"] == "F14", "legacy family changed")
    _check(report["legacy_backlog"]["state"] == "catalogued", "legacy backlog state changed")
    _check(report["category_scope"] == reference.CATEGORY_SCOPE, "category scope changed")
    _check(
        report["category_scope"]["cloning_via_conversion_is_not_tts"] is True,
        "conversion/TTS boundary changed",
    )
    _check(
        report["category_scope"]["tts_is_optional_not_required_call_replacement"] is True,
        "optional TTS boundary changed",
    )
    _check(
        report["category_scope"]["streaming_label_is_not_low_conversational_delay"] is True,
        "streaming/latency boundary changed",
    )
    _check(report["scope"]["no_new_execution"] is True, "survey claims a new execution")
    _check(
        report["scope"]["historical_citations_include_real_speech"] is True,
        "historical speech scope",
    )
    _check(
        report["scope"]["historical_citations_include_research_outputs"] is True,
        "historical output scope",
    )
    for key in (
        "real_speech_used_here",
        "real_corpus_used_here",
        "weights_loaded_here",
        "runtime_invoked_here",
        "model_inference_here",
        "streaming_inference_here",
        "listening_here",
        "device_timing_here",
        "latency_claim",
        "benchmark_claim",
        "release_claim",
        "numeric_parity_claim",
        "tts_quality_claim",
        "voice_cloning_claim",
        "reference_similarity_claim",
        "naturalness_claim",
        "content_preservation_claim",
        "network_access",
    ):
        _check(report["scope"][key] is False, "scope must stay closed: " + key)
    for key, value in report["boundary"].items():
        _check(value is False, "boundary flag is not false: " + key)
    _check(report["non_claims"], "non-claims are missing")
    _check(report["provenance"]["board_claim_edited"] is False, "board claim edited")
    _check(report["provenance"]["claim_base_commit"] == reference.CLAIM_BASE_COMMIT, "claim base provenance")
    _check(
        report["provenance"]["integration_base_commit"] == reference.BASE_COMMIT,
        "integration base provenance",
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
    _check(reference.BOARD_PATH not in report["boundary_pins"], "report pins mutable board")
    _check(report["mutable_provenance"]["gate"] is False, "mutable provenance is gated")
    _check("sha256_at_read" not in report["mutable_provenance"], "mutable board hash is gated")
    classes = report["evidence_classes"]
    for key in (
        "reference_cloning_execution",
        "reference_similarity_measured",
        "naturalness_measured",
        "human_listening_result",
        "content_preservation_gold",
        "multi_utterance_or_multi_speaker_cohort",
        "rights_qualified_reference_voice_corpus",
        "streaming_first_audio_claim",
        "device_timing",
        "cpu_accelerator_parity",
        "tts_quality_claim",
        "new_execution_in_this_survey",
        "parity_or_qualification_claim",
        "provider_enablement",
        "release_approval",
    ):
        _check(classes[key] is False, "unsupported evidence class: " + key)
    for key in (
        "historical_research_zero_shot_streaming_tts",
        "historical_research_reference_conditioned_whole_utterance_tts",
        "historical_research_fixed_voice_tts_control",
        "source_only_reference_tts_protocol",
        "source_reported_reference_tts_candidate",
        "source_reported_blocked_candidate",
        "source_reported_candidate_documentation",
        "adjacent_vocoder_component_boundary",
    ):
        _check(classes[key] is True, "supported evidence class is missing: " + key)
    _check({row["branch"] for row in report["method_families"]} == {"classic", "ml"}, "method branches")
    _check({lead["source_id"] for lead in report["source_leads"]} == {"S40"}, "source lead coverage")
    for lead in report["source_leads"]:
        _check(lead["mapped_components"], "source lead has no component: " + lead["source_id"])
        _check(lead["gap_ids"], "source lead has no gap: " + lead["source_id"])
    families = {row["family_id"]: row for row in report["method_families"]}
    _check("statistical" not in families["MF-C1"]["family"].lower(), "classic family is not the open search")
    _check("open" in families["MF-C1"]["family"].lower(), "open classic search missing")
    _check("flow" in families["MF-M1"]["family"].lower(), "flow TTS family missing")
    _check("codec" in families["MF-M2"]["family"].lower(), "codec TTS family missing")
    _check("whole-utterance" in families["MF-M3"]["family"].lower(), "whole-utterance family missing")
    _check("vits" in families["MF-M4"]["family"].lower(), "VITS family missing")
    _check("gated" in families["MF-M5"]["family"].lower(), "gated checkpoint family missing")
    _check("fixed-voice" in families["MF-M6"]["family"].lower(), "fixed-voice control family missing")
    census = {row["component_id"] for row in report["component_census"]}
    _check(len(census) == 17, "component census count changed")
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
    _check(
        {row["id"] for row in report["historical_executions"]} == {"HE-1", "HE-2", "HE-3"},
        "historical execution set changed",
    )
    he1 = report["historical_executions"][0]
    _check(he1["values"]["chunk_count"] == 4, "CosyVoice chunk count changed")
    _check(he1["values"]["file_rtf"] > 8.0, "CosyVoice RTF changed")
    _check(he1["values"]["reference_similarity_measured"] is False, "CosyVoice similarity claimed")
    he2 = report["historical_executions"][1]
    _check(he2["values"]["streaming_chunks_exposed"] is False, "Chatterbox streaming claimed")
    _check(he2["values"]["reference_similarity_measured"] is False, "Chatterbox similarity claimed")
    he3 = report["historical_executions"][2]
    _check(he3["values"]["reference_voice_cloning"] is False, "Kokoro promoted to cloning")
    _check(he3["values"]["reference_audio_seconds"] == 0.0, "Kokoro gained a reference")
    local = {row["id"] for row in report["historical_executions"]}
    reported = {row["id"] for row in report["reported_outcomes"]}
    _check(local and reported and not (local & reported), "local and reported outcomes are not distinct")
    for row in report["reported_outcomes"]:
        _check(row["class"].startswith("source_reported_"), "reported outcome class: " + row["id"])
    missing = [row for row in report["comparison_inputs"] if row["class"] == "missing_required_cohort"]
    _check(len(missing) == 1, "missing cohort is not explicit")
    _check("missing" in missing[0]["boundary"].lower(), "missing cohort boundary is not explicit")
    assets = [row for row in report["assets"] if row["class"] == "missing_asset"]
    _check(assets, "missing asset is not explicit")
    for row in assets:
        _check("not present" in row["status"].lower(), "missing asset is not marked absent")

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
    print("PASS category=TRN-05 cloning_execution=false conversion_as_tts=false gates=8-blocked")
    print("PASS report_sha256=" + digest)
    print("PASS pins=sorted+complete cold_start=3x-byte-identical scope=task-local-only")
    print("PASS mutable_board_gate=false linked_row_identity_only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
