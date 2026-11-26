# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the Krisp public-output scoring DEFER package.

Checks strict JSON, exact external/boundary/sibling/local pins, the stable
linked-row identity, canonical report bytes, three cold-start repeats, the
eight blocked release gates, cohort/scorer/WER contracts, recomputed segment
and aggregation arithmetic, null real-score slots, adverse/missing/nonfinite
controls, expected artifact absence, SPDX annotations, dependency hygiene and
task-local scope containment.  The mutable full board file is never hashed;
only the stable linked-row fields are compared.
"""

from __future__ import annotations

import ast
import hashlib
import json
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
    "torch", "tensorflow", "requests", "pandas", "onnx", "sounddevice",
}
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".m4a", ".onnx", ".tflite", ".bin", ".whl",
    ".so", ".dylib", ".dll", ".a", ".pt", ".pth", ".ckpt", ".safetensors",
}
FORBIDDEN_CALLS = {"urlopen", "urlretrieve", "requests_get", "download", "wget"}
ALLOWED_PROFILE_STATUS = {
    "blocked", "synthetic_control_only", "proposal_only",
}
ALLOWED_CATEGORIES = {
    "strict_json", "cohort", "scorer", "metric", "wer", "aggregation",
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
            fail("pinned source changed: " + name + " " + actual)
    for group, pins in (("boundary", reference.BOUNDARY_PINS),
                        ("sibling", reference.SIBLING_PINS)):
        for name, expected in pins.items():
            path = WORKTREE / name
            if not path.is_file():
                fail("missing " + group + " pin: " + name)
            actual = sha(path)
            if actual != expected:
                fail(group + " pin changed: " + name + " " + actual)
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
        if sha(path) != expected:
            fail("local artifact changed: " + name)
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
        "deliverable": row.get("deliverable"),
        "acceptance": row.get("acceptance"),
        "evidence": row.get("evidence"),
        "write_scope": row.get("write_scope"),
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
    if contract["task"] != reference.TASK_ID \
            or contract["component"] != reference.COMPONENT:
        fail("contract task/component mismatch")
    if contract["profile"] != "evidence":
        fail("contract profile is not evidence")
    if contract["base_commit"] != reference.BASE_COMMIT \
            or contract["branch"] != reference.BRANCH:
        fail("contract base/branch mismatch")
    if (contract["status"] != reference.STATUS
            or contract["completeness"] != reference.COMPLETENESS
            or contract["decision"] != reference.DECISION):
        fail("contract is not proposal-only/incomplete/DEFER")
    qualification = contract["qualification"]
    if (qualification.get("status") != "not_qualified"
            or qualification.get("qualifies") is not False
            or qualification.get("incomplete") is not True
            or qualification.get("missing_result_promoted") is not False
            or qualification.get("all_release_gates_blocked") is not True):
        fail("contract qualification is not not_qualified/incomplete")
    if contract["task_row"] != reference.TASK_ROW_IDENTITY:
        fail("contract task_row mismatch")
    if contract["mutable_provenance"] != reference.MUTABLE_PROVENANCE:
        fail("contract mutable provenance mismatch")
    for field in ("source_pins", "boundary_pins", "sibling_pins", "scope",
                  "public_surface"):
        if contract[field] != getattr(reference, field.upper()):
            fail("contract " + field + " mismatch")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("contract public surface flag is not false")
    if contract["cohort_contract_summary"] != reference.cohort_contract_summary():
        fail("contract cohort summary mismatch")
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
    if [item["id"] for item in required] != \
            [item["id"] for item in reference.REQUIRED_ARTIFACTS]:
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


def _check_case(case: Dict[str, Any], where: str) -> None:
    plan = reference.dnsmos_c_segment_plan(case["duration_ms"],
                                           case["segment_kind"])
    for key in ("dropped", "repeated", "repeat_count", "window_count",
                "end_aligned_tail"):
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
    for field in ("source_pins", "boundary_pins", "sibling_pins", "scope",
                  "public_surface"):
        if report[field] != getattr(reference, field.upper()):
            fail("report " + field + " mismatch")
    if any(value is not False for value in report["public_surface"].values()):
        fail("report public surface flag is not false")

    cohort = report["cohort"]
    for key, expected in (
        ("dataset_revision", reference.DATASET_REVISION),
        ("processed_revision", reference.PROCESSED_REVISION),
        ("processed_subset", reference.PROCESSED_SUBSET),
        ("item_count", reference.ITEM_COUNT),
        ("processed_total_bytes", reference.PROCESSED_TOTAL_BYTES),
        ("license", reference.COHORT_LICENSE),
    ):
        if cohort[key] != expected:
            fail("cohort " + key + " mismatch")
    if cohort["present"] is not False or cohort["permitted_use_here"] is not False:
        fail("cohort is claimed present or permitted")
    if cohort["scenarios"] != list(reference.SCENARIOS):
        fail("cohort scenario list mismatch")

    scorer = report["scorer"]
    if scorer["id"] != "dnsmos_c" or scorer["status"] != "blocked":
        fail("scorer is not the blocked dnsmos_c row")
    if any(value is not None for value in scorer["score_slots"].values()):
        fail("scorer emitted a score")
    if scorer["checkpoint_sha256"] is not None \
            or scorer["source_revision"] is not None:
        fail("scorer claims an unpinned identity")
    if scorer["measured_here"] is not False or scorer["is_mos"] is not False:
        fail("scorer score labels mismatch")

    wer = report["wer"]
    if wer["measured_here"] is not False \
            or wer["merged_with_dnsmos_c"] is not False:
        fail("WER record is merged or claimed measured")
    if wer["audio_enhance_percent"] is not None:
        fail("WER library column is not unmeasured")
    if wer["config_count"] != reference.WER_CONFIG_COUNT:
        fail("WER config count mismatch")

    scores = report["documented_scores"]
    if scores["reproduced_here"] is not False \
            or scores["is_human_rating"] is not False \
            or scores["is_mos"] is not False:
        fail("documented scores are relabelled")
    if [row["condition"] for row in scores["conditions"]] != [
        "raw", "krisp_vi_2_5_default", "audio_enhance_basic_v1",
        "audio_enhance_voice_focus_v1",
    ]:
        fail("documented score condition list mismatch")

    aggregation = report["aggregation_reference"]
    synthetic = reference.equal_weight_average(
        {"work": 3.0, "call_center": 3.5, "phone_calls": 4.0})
    if aggregation["synthetic_average"] != synthetic:
        fail("synthetic aggregation does not recompute")
    if aggregation["scores_reproduced"] is not False:
        fail("aggregation claims score reproduction")
    for condition, expected in reference.DOCUMENTED_SCORES.items():
        row = aggregation["documented_recomputation"][condition]
        recomputed = reference.equal_weight_average(
            {name: expected[name] for name in reference.SCENARIOS})
        if row["recomputed"] != round(recomputed, 10):
            fail("documented recomputation mismatch: " + condition)

    geometry = report["geometry_reference"]
    if [case["duration_ms"] for case in geometry["segment_cases"]] != \
            [999, 1000, 4000, 10000, 12345, 15000, 20000]:
        fail("geometry case list mismatch")
    for case in geometry["segment_cases"]:
        _check_case(case, "segment:%d" % case["duration_ms"])
    if geometry["bits_reproduced"] is not False \
            or geometry["scored"] is not False:
        fail("geometry claims reproduction or scoring")

    fixture = report["fixtures"]
    if fixture["average"] != synthetic or fixture["contains_audio"] is not False:
        fail("fixture payload mismatch")

    runs = report["runs"]
    if len(runs) != 12:
        fail("run plan count mismatch")
    for row in runs:
        if row["status"] != "not_executed_artifact_and_rights_absent":
            fail("run status mismatch: " + row["run_id"])
        if any(value is not None for value in row["scores"].values()):
            fail("run emitted a score: " + row["run_id"])
        if row["qualifies"] is not False:
            fail("run qualifies: " + row["run_id"])

    controls = report["controls"]
    if set(controls) != set(reference.CONTROL_STATUS):
        fail("control set mismatch")
    for name, row in controls.items():
        if row["status"] != reference.CONTROL_STATUS[name]:
            fail("control status mismatch: " + name)
        if any(value is not None for value in row["scores"].values()):
            fail("control emitted a score: " + name)
        if row["qualifies"] is not False:
            fail("control qualifies: " + name)

    adverse = report["adverse_results"]
    if len(adverse) < 45:
        fail("adverse results do not cover enough rejections: %d" % len(adverse))
    if not reference._check_all_rejected(adverse):
        fail("an adverse case was accepted or changed state")
    categories = {row["category"] for row in adverse}
    if categories != ALLOWED_CATEGORIES:
        fail("adverse categories are incomplete")
    identifiers = [row["result_id"] for row in adverse]
    if len(identifiers) != len(set(identifiers)):
        fail("duplicate adverse result id")
    for required in ("json_duplicate_key", "cohort_item_rights_missing",
                     "scorer_bad_checkpoint_digest", "metric_nan",
                     "wer_library_measured", "aggregation_nan"):
        if required not in identifiers:
            fail("required adverse case missing: " + required)

    missing = report["missing_results"]
    if len(missing) < 12:
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

    assessment = report["artifact_assessment"]
    if assessment["all_required_absent"] is not True:
        fail("artifact assessment does not record the exact blocker")
    for row in assessment["probes"]:
        if row["present"] is not False:
            fail("artifact presence is not false: " + row["id"])
    if assessment["substitution"]["performed"] is not False:
        fail("artifact substitution was performed")
    if assessment["checkpoint_identity"]["digest_recorded"] is not False:
        fail("checkpoint digest is claimed recorded")
    if not assessment["conclusion"].startswith("BLOCKED:"):
        fail("artifact conclusion is not an explicit blocker")

    if report["separation_from_siblings"][
            "reused_source_fixtures_metrics_or_results"] is not False:
        fail("sibling evidence is reused")

    gates = report["release_gates"]
    if len(gates) != 8 or gates != reference.RELEASE_GATES:
        fail("report release gates mismatch")
    if any(gate["status"] != "blocked" or gate["qualifies"] is not False
           for gate in gates):
        fail("report release gate is not blocked")
    assert_no_qualifying(report)
    print("verify: report canonical, byte-identical, digest " + digest)


def check_artifact_absence() -> None:
    for probe in reference.ABSENCE_PROBES:
        path = WORKSPACE / probe["path"]
        if path.exists():
            fail("expected-absent artifact is present: " + probe["path"])
    print("verify: every probed artifact is absent; no substitute admitted")


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
    for flag in ("--check", "--inspect", "--sources"):
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
    print("verify: 3/3 byte-identical cold starts for --all/--check/--inspect/--sources")


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
    for name, expected in reference.SOURCE_PINS.items():
        if expected not in readme:
            fail("source digest missing from README: " + name)
    for name, expected in reference.BOUNDARY_PINS.items():
        if expected not in readme:
            fail("boundary digest missing from README: " + name)
    for name, expected in reference.SIBLING_PINS.items():
        if expected not in readme:
            fail("sibling digest missing from README: " + name)
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
          "cohort scorer wer null-scores controls hygiene scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
