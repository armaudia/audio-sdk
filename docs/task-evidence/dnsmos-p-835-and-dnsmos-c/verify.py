# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the DNSMOS P.835 / DNSMOS-C DEFER package.

Checks strict JSON, exact external/boundary/sibling/local pins, the stable
linked task-row identity, canonical report bytes, three cold-start repeats,
eight blocked gates, the two distinct scorer contracts, recomputed window,
tiling, post-processing and aggregation arithmetic, null score slots,
adverse/missing/invalid/nonfinite controls, artifact absence at the exact
recorded paths, non-substitution of incidental ONNX copies, SPDX annotations,
dependency hygiene and task-local scope containment.  The mutable full board
file is never hashed into canonical bytes; only the stable linked row is
compared.
"""

from __future__ import annotations

import ast
import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any, Dict, List

import reference

ROOT = Path(__file__).resolve().parent
WORKTREE = ROOT.parents[2]
WORKSPACE = WORKTREE.parents[2]
TASK_PREFIX = ROOT.relative_to(WORKTREE).as_posix() + "/"
SPDX_TAG = "SPDX" "-License-Identifier:"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText:"

CONTRACT_KEYS = reference.CONTRACT_KEYS
REPORT_KEYS = reference.REPORT_KEYS
FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "librosa", "onnxruntime", "pystoi",
    "torch", "tensorflow", "webrtc", "requests", "pandas", "onnx",
}
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".m4a", ".onnx", ".tflite", ".bin", ".whl",
    ".so", ".dylib", ".dll", ".a", ".pt", ".pth", ".ckpt", ".safetensors",
}
FORBIDDEN_CALLS = {"urlopen", "urlretrieve", "requests_get", "download", "wget"}
SCORER_IDS = ["dnsmos_p835", "dnsmos_c"]
CONTROL_IDS = set(reference.CONTROL_STATUS)
ALLOWED_PROFILE_STATUS = {
    "synthetic_control_only", "synthetic_geometry_only", "proposal_only",
    "blocked",
}
ALLOWED_CATEGORIES = {
    "strict_json", "p835_window", "dnsmos_c", "aggregation", "postprocess",
    "manifest", "admission",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def strict_json(path: Path) -> Dict[str, Any]:
    try:
        return reference.read_strict_json(path)
    except (OSError, ValueError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    raise AssertionError("unreachable")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest() -> Dict[str, str]:
    manifest: Dict[str, str] = {}
    for line in (ROOT / "SOURCES.sha256").read_text(encoding="utf-8").splitlines():
        if not line:
            continue
        digest, name = line.split("  ", 1)
        if name in manifest:
            fail("duplicate manifest entry: " + name)
        manifest[name] = digest
    return manifest


def check_pins() -> None:
    for name, expected in reference.SOURCE_PINS.items():
        path = WORKSPACE / name
        if not path.is_file():
            fail("missing pinned source: " + name)
        actual = sha(path)
        if actual != expected:
            fail("pinned source changed: " + name + " " + actual + " != " + expected)
    for group, pins in (("boundary", reference.BOUNDARY_PINS),
                        ("sibling", reference.SIBLING_PINS)):
        for name, expected in pins.items():
            path = WORKTREE / name
            if not path.is_file():
                fail("missing " + group + " pin: " + name)
            actual = sha(path)
            if actual != expected:
                fail(group + " pin changed: " + name + " " + actual + " != " + expected)
    manifest = parse_manifest()
    if "audio-benchmark-platform/plan/swarm/TASKS.json" in manifest:
        fail("mutable board file must not be in SOURCES.sha256")
    print("verify: %d external, %d boundary, %d sibling pins exact"
          % (len(reference.SOURCE_PINS), len(reference.BOUNDARY_PINS),
             len(reference.SIBLING_PINS)))


def check_local_manifest() -> None:
    manifest = parse_manifest()
    if "SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for name, expected in manifest.items():
        path = ROOT / name
        if not path.is_file():
            fail("missing local artifact: " + name)
        actual = sha(path)
        if actual != expected:
            fail("local artifact changed: " + name + " " + actual + " != " + expected)
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        name = path.relative_to(ROOT).as_posix()
        if name not in manifest:
            fail("unpinned local artifact: " + name)
    print("verify: %d local artifacts exact" % len(manifest))


def check_linked_row(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    board = WORKSPACE / "audio-benchmark-platform" / "plan" / "swarm" / "TASKS.json"
    data = strict_json(board)
    rows = [row for row in data.get("tasks", []) if row.get("id") == reference.TASK_ID]
    if len(rows) != 1:
        fail("linked task row count is not exactly one")
    row = rows[0]
    claim = row.get("claim") or {}
    stable = {
        "id": row.get("id"),
        "title": row.get("title"),
        "repository": row.get("repository"),
        "mode": row.get("mode"),
        "component": row.get("component"),
        "depends_on": row.get("depends_on"),
        "evidence": row.get("evidence"),
        "base_commit": claim.get("base_commit"),
        "branch": claim.get("branch"),
    }
    if stable != reference.TASK_ROW_IDENTITY:
        fail("stable linked-row identity mismatch")
    board_digest = sha(board)
    for document in (contract, report):
        if document.get("mutable_provenance") != reference.MUTABLE_PROVENANCE:
            fail("mutable provenance record mismatch")
        text = json.dumps(document, sort_keys=True, allow_nan=False)
        if board_digest in text:
            fail("mutable board digest must not enter canonical bytes")
        if "sha256_at_read" in text or "sha256_now" in text:
            fail("mutable board digest fields must not enter canonical bytes")
    manifest_text = (ROOT / "SOURCES.sha256").read_text(encoding="utf-8")
    for item in ("TASKS.json", "sha256_at_read", board_digest):
        if item in manifest_text:
            fail("mutable board provenance leaked into SOURCES.sha256")
    print("verify: stable linked-row identity exact; mutable board not hashed")


def assert_no_qualifying(value: Any, where: str = "$") -> None:
    if isinstance(value, dict):
        for key, item in value.items():
            if key == "qualifies" and item is not False:
                fail("qualifying result at " + where + "." + key)
            assert_no_qualifying(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            assert_no_qualifying(item, where + "[" + str(index) + "]")


def check_contract(contract: Dict[str, Any]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch")
    if contract["schema_id"] != reference.SCHEMA_ID:
        fail("contract schema id mismatch")
    if contract["task"] != reference.TASK_ID or contract["component"] != reference.COMPONENT:
        fail("contract task/component mismatch")
    if contract["profile"] != "evidence":
        fail("contract profile is not evidence")
    if contract["base_commit"] != reference.BASE_COMMIT or contract["branch"] != reference.BRANCH:
        fail("contract base/branch mismatch")
    if (contract["status"] != reference.STATUS
            or contract["completeness"] != reference.COMPLETENESS
            or contract["decision"] != reference.DECISION):
        fail("contract is not proposal-only/incomplete/DEFER")
    qualification = contract["qualification"]
    if (qualification.get("status") != "not_qualified"
            or qualification.get("qualifies") is not False
            or qualification.get("incomplete") is not True
            or qualification.get("missing_result_promoted") is not False):
        fail("contract qualification is not not_qualified/incomplete")
    if contract["task_row"] != reference.TASK_ROW_IDENTITY:
        fail("contract task_row mismatch")
    if contract["mutable_provenance"] != reference.MUTABLE_PROVENANCE:
        fail("contract mutable provenance mismatch")
    if contract["source_pins"] != reference.SOURCE_PINS:
        fail("contract source pins mismatch")
    if contract["boundary_pins"] != reference.BOUNDARY_PINS:
        fail("contract boundary pins mismatch")
    if contract["sibling_pins"] != reference.SIBLING_PINS:
        fail("contract sibling pins mismatch")
    if contract["scope"] != reference.SCOPE:
        fail("contract scope mismatch")
    if contract["public_surface"] != reference.PUBLIC_SURFACE:
        fail("contract public surface mismatch")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("contract public surface flag is not false")
    if contract["scorer_contract_summary"] != reference.scorer_contract_summary():
        fail("contract scorer summary mismatch")
    if contract["release_gates"] != reference.RELEASE_GATES:
        fail("contract release gates mismatch")
    if len(contract["release_gates"]) != 8:
        fail("contract must have exactly eight release gates")
    if any(gate["status"] != "blocked" or gate["qualifies"] is not False
           for gate in contract["release_gates"]):
        fail("contract release gate is not blocked")
    if contract["non_claims"] != reference.NON_CLAIMS:
        fail("contract non-claims mismatch")
    if contract["reproduction"] != reference.REPRODUCTION:
        fail("contract reproduction mismatch")
    required = contract["required_artifacts"]
    expected_ids = [item["id"] for item in reference.REQUIRED_ARTIFACTS]
    if [item["id"] for item in required] != expected_ids:
        fail("contract required artifact ids mismatch")
    if any(item["present"] is not False for item in required):
        fail("contract claims a required artifact is present")
    manifest = parse_manifest()
    expected_pins = set(manifest) - {"contract.json"}
    if set(contract["artifact_pins"]) != expected_pins:
        fail("contract artifact pins do not cover every local artifact")
    for name, expected in contract["artifact_pins"].items():
        if manifest.get(name) != expected:
            fail("contract artifact pin mismatch: " + name)
    assert_no_qualifying(contract)
    print("verify: contract incomplete/DEFER/not_qualified with 8 blocked gates")


def _check_p835_case(case: Dict[str, Any], where: str) -> None:
    plan = reference.p835_window_plan(case["input_samples"])
    for key in ("doublings", "padded_samples", "num_hops",
                "uncovered_samples"):
        if case[key] != plan[key]:
            fail(where + ": " + key + " mismatch")
    if case["first_window"] != [plan["windows"][0]["start"],
                                plan["windows"][0]["end"]]:
        fail(where + ": first window mismatch")
    if case["last_window"] != [plan["windows"][-1]["start"],
                               plan["windows"][-1]["end"]]:
        fail(where + ": last window mismatch")
    if case["first_window_original_samples"] != \
            plan["windows"][0]["original_samples"]:
        fail(where + ": first-window original samples mismatch")
    if plan["window_samples"] != reference.P835_WINDOW_SAMPLES:
        fail(where + ": window size mismatch")
    if plan["num_hops"] < 1:
        fail(where + ": no window planned")
    if case["scored"] is not False or case["qualifies"] is not False:
        fail(where + ": case is scored or qualifying")


def _check_dnsc_case(case: Dict[str, Any], where: str) -> None:
    plan = reference.dnsmos_c_segment_plan(case["duration_ms"],
                                           case["segment_kind"])
    for key in ("dropped", "repeated", "repeat_count", "tiling_truncated_ms",
                "window_count", "end_aligned_tail"):
        if case[key] != plan[key]:
            fail(where + ": " + key + " mismatch")
    if case["dropped"]:
        if case["first_window"] is not None or case["last_window"] is not None:
            fail(where + ": dropped segment exposes a window")
    else:
        if case["first_window"] != [plan["windows"][0]["start_ms"],
                                    plan["windows"][0]["end_ms"]]:
            fail(where + ": first window mismatch")
        if case["last_window"] != [plan["windows"][-1]["start_ms"],
                                   plan["windows"][-1]["end_ms"]]:
            fail(where + ": last window mismatch")
        for window in plan["windows"]:
            if window["end_ms"] - window["start_ms"] != reference.DNSC_WINDOW_MS:
                fail(where + ": window length mismatch")
    if case["scored"] is not False or case["qualifies"] is not False:
        fail(where + ": case is scored or qualifying")


def check_report(report: Dict[str, Any]) -> None:
    if set(report) != REPORT_KEYS:
        fail("report key set mismatch")
    text, digest = reference.canonical_report(report)
    raw = (ROOT / "report.json").read_bytes()
    if raw != (text + "\n").encode("utf-8"):
        fail("report.json is not byte-identical after regeneration")
    sidecar = (ROOT / "report.json.sha256").read_text(encoding="ascii").strip()
    if sidecar != hashlib.sha256(raw).hexdigest() or sidecar != digest:
        fail("report.json.sha256 does not match report.json")
    regeneration = report["regeneration"]
    core = dict(report)
    core.pop("regeneration")
    core_digest = hashlib.sha256(reference.canonical_bytes(core)).hexdigest()
    if (regeneration["runs"] != 3 or regeneration["byte_identical"] is not True
            or regeneration["canonical_digests"] != [core_digest] * 3):
        fail("report regeneration is not three exact repeats")
    if (report["status"] != reference.STATUS
            or report["completeness"] != reference.COMPLETENESS
            or report["decision"] != reference.DECISION):
        fail("report is not proposal-only/incomplete/DEFER")
    qualification = report["qualification"]
    if (qualification.get("status") != "not_qualified"
            or qualification.get("qualifies") is not False
            or qualification.get("incomplete") is not True
            or qualification.get("missing_result_promoted") is not False):
        fail("report qualification is not not_qualified/incomplete")
    if report["task_row"] != reference.TASK_ROW_IDENTITY:
        fail("report task_row mismatch")
    if report["mutable_provenance"] != reference.MUTABLE_PROVENANCE:
        fail("report mutable provenance mismatch")
    if report["source_pins"] != reference.SOURCE_PINS:
        fail("report source pins mismatch")
    if report["boundary_pins"] != reference.BOUNDARY_PINS:
        fail("report boundary pins mismatch")
    if report["sibling_pins"] != reference.SIBLING_PINS:
        fail("report sibling pins mismatch")
    if report["scope"] != reference.SCOPE or report["public_surface"] != reference.PUBLIC_SURFACE:
        fail("report scope/public surface mismatch")
    if any(value is not False for value in report["public_surface"].values()):
        fail("report public surface flag is not false")

    scorers = report["scorers"]
    if [scorer["id"] for scorer in scorers] != SCORER_IDS:
        fail("report does not keep the two scorers separate")
    for scorer in scorers:
        if scorer["status"] != "blocked":
            fail("scorer is not blocked: " + scorer["id"])
        if any(value is not None for value in scorer["score_slots"].values()):
            fail("scorer emitted a score: " + scorer["id"])
        if scorer["scores_reproduced"] is not False \
                or scorer["scores_are_human_ratings"] is not False \
                or scorer["scores_are_predictions"] is not True:
            fail("scorer score labels mismatch: " + scorer["id"])
        if not scorer["score_status"].startswith("unavailable_"):
            fail("scorer score status is not unavailable: " + scorer["id"])
    p835 = scorers[0]
    if p835["outputs"] != ["SIG", "BAK", "OVL"]:
        fail("P.835 output names mismatch")
    if (p835["sample_rate_hz"] != 16000 or p835["window_samples"] != 144160
            or p835["hop_samples"] != 16000):
        fail("P.835 geometry mismatch")
    if sorted(model["name"] for model in p835["models"]) != ["bak_ovr.onnx", "sig.onnx"]:
        fail("P.835 model set mismatch")
    if p835["scorer"]["expected_sha256"] != reference.P835_SCORER_SHA256:
        fail("P.835 scorer digest mismatch")
    dnsc = scorers[1]
    if dnsc["outputs"] != ["DNSMOS_C"]:
        fail("DNSMOS-C output name mismatch")
    if (dnsc["segment_kinds"] != ["primary", "mix"]
            or dnsc["min_segment_ms"] != 1000
            or dnsc["window_ms"] != 10000 or dnsc["hop_ms"] != 5000):
        fail("DNSMOS-C protocol constants mismatch")
    if dnsc["checkpoint"]["path"] != "runs/NISQA/model_best.pt" \
            or dnsc["checkpoint"]["present"] is not False:
        fail("DNSMOS-C checkpoint record mismatch")
    if dnsc["source"]["pinned_revision"] is not None:
        fail("DNSMOS-C source claims a pinned revision")

    audit = report["scorer_documentation_audit"]
    if audit["p835_script"]["all_tokens_present"] is not True:
        fail("P.835 documentation tokens are not all present")
    if audit["dnsmos_c_report"]["all_tokens_present"] is not True:
        fail("DNSMOS-C documentation tokens are not all present")
    if audit["reproduces_scores"] is not False \
            or audit["reproduces_feature_values"] is not False:
        fail("documentation audit claims reproduction")

    geometry = report["geometry_reference"]
    if [case["input_samples"] for case in geometry["p835_cases"]] != \
            [12000, 144159, 144160, 144161, 300000]:
        fail("P.835 geometry case list mismatch")
    for case in geometry["p835_cases"]:
        _check_p835_case(case, "p835:" + str(case["input_samples"]))
    if [case["duration_ms"] for case in geometry["dnsmos_c_cases"]] != \
            [999, 1000, 4000, 10000, 12345, 15000, 20000]:
        fail("DNSMOS-C geometry case list mismatch")
    for case in geometry["dnsmos_c_cases"]:
        _check_dnsc_case(
            case, "dnsmos-c:%d" % case["duration_ms"])
    if geometry["p835_bits_reproduced"] is not False \
            or geometry["dnsmos_c_bits_reproduced"] is not False:
        fail("geometry claims bit reproduction")

    post = report["postprocessing_reference"]
    recomputed = reference.p835_postprocess(2.5, 3.0, 2.8)
    if post["standard"] != recomputed["mapped"] or post["is_model_output"] is not False:
        fail("post-processing reference does not recompute")
    if post["coefficient_source_verified"] is not False:
        fail("post-processing coefficients claimed verified")

    aggregation = report["aggregation_reference"]
    if aggregation["mean_example"] != reference.exact_mean([3.0, 4.25, 3.5, 4.75]):
        fail("mean reference does not recompute")
    if aggregation["scenario_average"] != reference.scenario_average(
            {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0}):
        fail("scenario average does not recompute")
    if aggregation["mean_is_order_invariant"] is not True:
        fail("mean is not order invariant")

    fixture = report["fixtures"]
    if fixture["p835"]["float32_digest"] != reference.digest_float32(
            reference.p835_fixture_values()):
        fail("fixture digest does not recompute")
    if fixture["p835"]["samples"] != reference.P835_FIXTURE_SAMPLES:
        fail("fixture size mismatch")
    if len(fixture["dnsmos_c"]["segments"]) != len(reference.DNSC_FIXTURE_SEGMENTS):
        fail("DNSMOS-C fixture segments mismatch")

    runs = report["runs"]
    if len(runs) != len(reference.p835_cases()) + len(reference.dnsmos_c_cases()):
        fail("run count mismatch")
    for row in runs:
        if row["status"] != "geometry_only_not_scored":
            fail("run status mismatch: " + row["run_id"])
        if any(value is not None for value in row["scores"].values()):
            fail("run emitted a score: " + row["run_id"])
        if row["qualifies"] is not False or row["scores_are_human_ratings"] is not False:
            fail("run is qualifying or human-labelled: " + row["run_id"])

    controls = report["controls"]
    if set(controls) != CONTROL_IDS:
        fail("control set mismatch")
    for name, row in controls.items():
        if row["status"] != reference.CONTROL_STATUS[name]:
            fail("control status mismatch: " + name)
        if any(value is not None for value in row["scores"].values()):
            fail("control emitted a score: " + name)
        if row["qualifies"] is not False:
            fail("control qualifies: " + name)

    adverse = report["adverse_results"]
    if len(adverse) < 50:
        fail("adverse results do not cover enough rejections: %d" % len(adverse))
    if not all(row["rejected"] for row in adverse):
        fail("an adverse case was accepted")
    if not all(row["state_unchanged"] and row["qualifies"] is False
               for row in adverse):
        fail("an adverse case changed state or qualifies")
    if not {row["category"] for row in adverse} <= ALLOWED_CATEGORIES:
        fail("adverse category outside the declared set")
    if {row["category"] for row in adverse} != ALLOWED_CATEGORIES:
        fail("adverse categories are incomplete")
    ids = [row["result_id"] for row in adverse]
    if len(ids) != len(set(ids)):
        fail("duplicate adverse result id")
    for required in ("substitute_p808_model_as_p835",
                     "substitute_combined_p835_model",
                     "json_duplicate_key", "postprocess_nan"):
        if required not in ids:
            fail("required adverse case missing: " + required)

    missing = report["missing_results"]
    if len(missing) < 8:
        fail("missing results are incomplete")
    for row in missing:
        if row["status"] != "blocked" or row["scores"] is not None \
                or row["qualifies"] is not False:
            fail("missing result was promoted: " + row["result_id"])

    failure = report["failure_controls"]
    if failure["all_explicit"] is not True:
        fail("failure controls are not explicit")
    if not all(failure["checks"].values()):
        fail("failure control check failed")
    if failure["rejected_count"] != len(adverse) \
            or failure["blocked_count"] != len(missing):
        fail("failure control counts are wrong")

    profile = report["acceptance_profile"]
    if profile["profile"] != "evidence" or profile["all_qualify"] is not False:
        fail("evidence profile application is not non-qualifying")
    if profile["qualifies"] is not False or profile["missing_result_promoted"] is not False:
        fail("evidence profile promotes a result")
    if not profile["items"] or any(item["qualifies"] is not False
                                   for item in profile["items"]):
        fail("evidence profile item qualifies or is empty")
    if any(item["status"] not in ALLOWED_PROFILE_STATUS
           for item in profile["items"]):
        fail("evidence profile item has an unexpected status")

    provenance = report["observed_provenance"]
    if provenance["reproduced_here"] is not False:
        fail("observed provenance is claimed reproduced")
    for item in provenance["documented_context"]:
        if item["reproduced_here"] is not False \
                or item["is_human_rating"] is not False \
                or item["is_mos"] is not False:
            fail("observed provenance relabels a source or human rating")
    if provenance["documented_context"][3]["admitted"] is not False:
        fail("incidental ONNX copy is admitted")

    assessment = report["artifact_assessment"]
    if assessment["all_required_absent"] is not True:
        fail("artifact assessment does not record the exact blocker")
    for key in ("weights_presence", "scorer_presence",
                "dnsmos_c_checkpoint_presence", "runtime_presence",
                "corpus_presence", "package_assets"):
        if assessment[key]["present"] is not False:
            fail("artifact presence is not false: " + key)
    if assessment["crosscheck"]["admitted"] is not False \
            or assessment["crosscheck"]["pinned_for_qualification"] is not False:
        fail("incidental artifact must not be admitted")
    if assessment["substitution"]["performed"] is not False:
        fail("artifact substitution was performed")
    if not assessment["conclusion"].startswith("BLOCKED:"):
        fail("artifact conclusion is not an explicit blocker")

    if report["separation_from_siblings"]["reused_source_fixtures_metrics_or_results"] is not False:
        fail("sibling evidence is reused")
    ranking = report["ranking"]
    if ranking["order"] != "not_ranked" or ranking["recommendation"] is not None \
            or ranking["qualifies"] is not False:
        fail("ranking is not explicitly withheld")

    gates = report["release_gates"]
    if len(gates) != 8:
        fail("report must have exactly eight release gates")
    if any(gate["status"] != "blocked" or gate["qualifies"] is not False
           for gate in gates):
        fail("report release gate is not blocked")
    if gates != reference.RELEASE_GATES:
        fail("report release gates mismatch")
    assert_no_qualifying(report)
    print("verify: report canonical, byte-identical, digest " + digest)


def check_artifact_absence() -> None:
    for path in (
        reference.P835_MODEL_DIR + "/sig.onnx",
        reference.P835_MODEL_DIR + "/bak_ovr.onnx",
        reference.P835_SCORER_PATH,
        reference.DNSC_CHECKPOINT,
    ):
        if (WORKSPACE / path).exists():
            fail("expected-absent artifact is present: " + path)
    incidental = WORKSPACE / (
        "research/voice-conversion-eval-20261101/repos/seed-vc/baselines/dnsmos"
    )
    if incidental.is_dir():
        for name, pinned in reference.P835_MODELS.items():
            candidate = incidental / name
            if candidate.is_file() and sha(candidate) == pinned:
                fail("incidental checkout matches a pinned P.835 weight: " + name)
        for candidate, wrong_name in (("model_v8.onnx", "model_v8.onnx"),
                                      ("sig_bak_ovr.onnx", "sig_bak_ovr.onnx")):
            path = incidental / candidate
            if path.is_file():
                try:
                    reference.classify_observed_artifact(
                        wrong_name, "dnsmos_p835", sha(path))
                except reference.ReferenceError:
                    continue
                fail("incidental artifact was admitted: " + candidate)
    print("verify: expected artifacts absent; incidental copies not admitted")


def check_three_repeats() -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    names = ("report.json", "report.json.sha256", "contract.json",
             "SOURCES.sha256")
    original = {name: (ROOT / name).read_bytes() for name in names}
    outputs: List[bytes] = []
    for _ in range(3):
        completed = subprocess.run([sys.executable, "run.py", "--all"], cwd=ROOT,
                                   env=environment, stdout=subprocess.PIPE,
                                   stderr=subprocess.PIPE, check=False)
        if completed.returncode != 0:
            fail("run.py --all failed: "
                 + completed.stderr.decode("utf-8", "replace"))
        outputs.append(completed.stdout)
    if len(set(outputs)) != 1:
        fail("run.py --all output differs across three cold starts")
    for name in names:
        if (ROOT / name).read_bytes() != original[name]:
            fail("--all changed bytes: " + name)
    for flag in ("--inspect", "--sources"):
        repeats: List[bytes] = []
        for _ in range(3):
            completed = subprocess.run([sys.executable, "run.py", flag], cwd=ROOT,
                                       env=environment, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, check=False)
            if completed.returncode != 0:
                fail("run.py " + flag + " failed: "
                     + completed.stderr.decode("utf-8", "replace"))
            repeats.append(completed.stdout)
        if len(set(repeats)) != 1:
            fail("run.py " + flag + " output differs across three cold starts")
    print("verify: 3/3 byte-identical cold-start repeats for --all/--inspect/--sources")


def check_hygiene() -> None:
    for path in sorted(ROOT.glob("*.py")):
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) < 2:
            fail("short Python file: " + path.name)
        if lines[0] != "# " + SPDX_COPYRIGHT + " 2026 Tsakanyan Hovhannes":
            fail("SPDX copyright header missing: " + path.name)
        if lines[1] != "# " + SPDX_TAG + " Apache-2.0":
            fail("SPDX license header missing: " + path.name)
        if text.count(SPDX_TAG) != 1:
            fail("SPDX tag literal repeated in a string: " + path.name)
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    if SPDX_TAG not in readme or SPDX_COPYRIGHT not in readme:
        fail("README SPDX annotation missing")
    for name in ("contract.json", "report.json", "report.json.sha256",
                 "SOURCES.sha256"):
        sidecar = ROOT / (name + ".license")
        if not sidecar.is_file():
            fail("SPDX sidecar missing: " + sidecar.name)
        text = sidecar.read_text(encoding="utf-8")
        if SPDX_TAG not in text or SPDX_COPYRIGHT not in text:
            fail("SPDX sidecar incomplete: " + sidecar.name)
    tests = (ROOT / "test_reference.py").read_text(encoding="utf-8")
    count = len(re.findall(r"^    def test_", tests, flags=re.MULTILINE))
    if count < 30:
        fail("fewer than 30 reference tests: %d" % count)
    for path in sorted(ROOT.glob("*.py")):
        tree = ast.parse(path.read_text(encoding="utf-8"), filename=path.name)
        for node in ast.walk(tree):
            roots = set()
            if isinstance(node, ast.Import):
                roots = {alias.name.split(".")[0] for alias in node.names}
            elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                roots = {node.module.split(".")[0]}
            if roots & FORBIDDEN_IMPORT_ROOTS:
                fail("forbidden dependency import in " + path.name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in FORBIDDEN_CALLS:
                fail("download-like call in " + path.name)
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_ARTIFACT_SUFFIXES:
            fail("forbidden native/asset artifact: " + path.name)
    readme_text = (ROOT / "README.md").read_text(encoding="utf-8")
    for name, expected in reference.SOURCE_PINS.items():
        if expected not in readme_text:
            fail("source digest missing from README: " + name)
    for name, expected in reference.BOUNDARY_PINS.items():
        if expected not in readme_text:
            fail("boundary digest missing from README: " + name)
    print("verify: SPDX annotations, %d tests, dependency and artifact hygiene" % count)


def check_scope() -> None:
    result = subprocess.run(["git", "status", "--porcelain", "--untracked-files=all"],
                            cwd=WORKTREE, stdout=subprocess.PIPE,
                            stderr=subprocess.PIPE, check=False)
    if result.returncode != 0:
        print("verify: git scope check skipped (not a git worktree)")
        return
    for line in result.stdout.decode("utf-8", "replace").splitlines():
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if "__pycache__" in path or path.endswith(".pyc"):
            continue
        if not path.startswith(TASK_PREFIX):
            fail("change outside task-local evidence directory: " + path)
    print("verify: working tree changes confined to " + TASK_PREFIX)


def main() -> int:
    try:
        contract = strict_json(ROOT / "contract.json")
        report = strict_json(ROOT / "report.json")
        check_pins()
        check_local_manifest()
        check_linked_row(contract, report)
        check_contract(contract)
        check_report(report)
        check_artifact_absence()
        check_three_repeats()
        check_hygiene()
        check_scope()
    except (OSError, ValueError, KeyError, TypeError, IndexError,
            subprocess.SubprocessError) as error:
        print("verify: FAIL " + str(error), file=sys.stderr)
        return 1
    print("verify: PASS strict-json pins linked-row canonical repeats gates "
          "scorers geometry null-scores controls hygiene scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
