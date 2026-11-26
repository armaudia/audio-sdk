# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the combined AEC3 + APM NS level package.

Checks strict JSON, exact external/boundary/sibling/local pins, the stable
linked task-row identity, canonical report bytes, three cold-start repeats,
eight blocked gates, the single configured APM instance and all toggles,
adverse/missing/invalid/nonfinite controls, SPDX annotations, dependency
hygiene and task-local scope containment.  The mutable full board file is never
hashed; only the stable linked row is compared.
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

CONTRACT_KEYS = {
    "schema_id", "task", "component", "profile", "base_commit", "branch",
    "status", "completeness", "decision", "qualification", "task_row",
    "mutable_provenance", "source_pins", "boundary_pins", "sibling_pins",
    "scope", "public_surface", "instance_summary", "required_artifacts",
    "release_gates", "artifact_pins", "reproduction", "non_claims",
}
FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "pystoi", "torch", "tensorflow",
    "onnxruntime", "webrtc", "requests", "pandas",
}
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".m4a", ".onnx", ".tflite", ".bin", ".whl",
    ".so", ".dylib", ".dll", ".a",
}
FORBIDDEN_CALLS = {"urlopen", "urlretrieve", "requests_get", "download", "wget"}


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
    for document in (contract, report):
        text = json.dumps(document, sort_keys=True, allow_nan=False)
        if "sha256_at_read" in text or "sha256_now" in text:
            fail("mutable board digest must not enter canonical bytes")
    manifest_text = (ROOT / "SOURCES.sha256").read_text(encoding="utf-8")
    for item in ("TASKS.json", "sha256_at_read"):
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


def check_contract(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch")
    if contract["schema_id"] != reference.SCHEMA_ID:
        fail("contract schema id mismatch")
    if contract["task"] != reference.TASK_ID or contract["component"] != reference.COMPONENT:
        fail("contract task/component mismatch")
    if contract["profile"] != "room":
        fail("contract profile is not room")
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
    expected_instance = {
        "instance_count": 1,
        "instance_id": "apm-aec3-ns-levels-1-3-synthetic.v1",
        "levels": [1, 2, 3],
        "toggle_names": list(reference.APM_TOGGLE_NAMES),
        "only_ns_level_varies": True,
    }
    if contract["instance_summary"] != expected_instance:
        fail("contract instance summary mismatch")
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


def _check_level_config(payload: Dict[str, Any]) -> None:
    if payload["instance_count"] != 1:
        fail("configured APM instance count is not one")
    if payload["levels_benchmarked"] != [1, 2, 3]:
        fail("configured APM levels are not 1-3")
    if payload["toggle_names"] != list(reference.APM_TOGGLE_NAMES):
        fail("configured APM toggle names mismatch")
    if set(payload["toggles"]) != set(reference.APM_TOGGLE_NAMES):
        fail("configured APM toggles are incomplete")
    if not payload["only_ns_level_varies"]:
        fail("configured APM changes more than the NS level")
    for row in payload["per_level"]:
        level = row["level"]
        expected = reference.sha256_bytes(
            reference.canonical_bytes(reference.apm_instance(level)))
        if row["config_sha256"] != expected:
            fail("configured APM level digest mismatch: " + str(level))
        if row["only_delta"] != {"noise_suppression.level": level}:
            fail("configured APM level delta mismatch: " + str(level))


def check_report(report: Dict[str, Any]) -> None:
    if set(report) != reference.REPORT_KEYS:
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
    _check_level_config(report["configured_apm_instance"])

    levels = report["per_level_runs"]
    if [row["ns_level"] for row in levels] != [1, 2, 3]:
        fail("per-level runs are not NS levels 1-3")
    if len({row["output_sha256"] for row in levels}) != 3:
        fail("per-level runs are not independent outputs")
    for row in levels:
        if row["qualifies"] is not False or row["ns_enabled"] is not True:
            fail("per-level row is not a non-qualifying NS run")
        if row["toggles_delta"] != {"noise_suppression.level": row["ns_level"]}:
            fail("per-level row changes more than the NS level")
        metrics = row["metrics"]
        if metrics["nonfinite_count"] != 0:
            fail("per-level run produced nonfinite output")
        for key in ("erle_late_db", "near_snr_late_db", "near_energy_change_db"):
            if not math.isfinite(float(metrics[key])):
                fail("per-level metric is not finite: " + key)
        if metrics["peak_abs"] > reference.MAX_ABS_INPUT:
            fail("per-level output peak exceeds the frozen input bound")

    ablation = report["level_ablation"]
    if len(ablation) != 3 or any(row["qualifies"] is not False for row in ablation):
        fail("level ablation is not three non-qualifying rows")
    if any(not row["independent_level_run"] or not row["only_ns_level_differs"]
           for row in ablation):
        fail("level ablation does not isolate the NS level")

    controls = report["controls"]
    required_controls = {
        "identity", "fixed_attenuation", "aec_only", "no_reference_passthrough",
        "delayed_render", "reference_dropout", "near_only", "echo_only", "reset",
    }
    if not required_controls <= set(controls):
        fail("room control set is incomplete")
    if controls["no_reference_passthrough"]["status"] != "blocked_no_reference":
        fail("no-reference control is not blocked")
    if controls["delayed_render"]["status"] != "misaligned_reference":
        fail("delayed-render control is not misaligned")
    if controls["reference_dropout"]["status"] != "partial_reference":
        fail("reference-dropout control is not partial")
    if controls["reset"]["reset_replay"]["byte_identical"] is not True:
        fail("reset replay is not byte-identical")
    for name in required_controls:
        if controls[name]["qualifies"] is not False:
            fail("control qualifies: " + name)

    profile = report["acceptance_profile"]
    if profile["profile"] != "room" or profile["all_qualify"] is not False:
        fail("room profile application is not non-qualifying")
    if profile["qualifies"] is not False or profile["missing_result_promoted"] is not False:
        fail("room profile promotes a result")
    if not profile["items"] or any(item["qualifies"] is not False for item in profile["items"]):
        fail("room profile item qualifies or is empty")
    if any(item["status"] not in {"synthetic_fixture_only", "synthetic_only",
                                  "synthetic_proxy_only", "synthetic_control_only",
                                  "blocked"}
           for item in profile["items"]):
        fail("room profile item has an unexpected status")

    if report["decision"] != "DEFER":
        fail("decision is not DEFER")
    gates = report["release_gates"]
    if len(gates) != 8:
        fail("report must have exactly eight release gates")
    if any(gate["status"] != "blocked" or gate["qualifies"] is not False
           for gate in gates):
        fail("report release gate is not blocked")
    if gates != reference.RELEASE_GATES:
        fail("report release gates mismatch")

    controls_failure = report["failure_controls"]
    if controls_failure["all_explicit"] is not True:
        fail("failure controls are not explicit")
    if not all(controls_failure["checks"].values()):
        fail("failure control check failed")
    if controls_failure["rejected_count"] < 10:
        fail("failure controls do not cover enough rejections")
    if controls_failure["blocked_count"] < 1:
        fail("failure controls do not cover a blocked case")

    if not report["adverse_results"]:
        fail("adverse results are missing")
    if any(row["qualifies"] is not False for row in report["adverse_results"]):
        fail("an adverse result qualifies")
    if not report["missing_results"]:
        fail("missing results are missing")
    for row in report["missing_results"]:
        if row["status"] != "blocked" or row["metrics"] is not None \
                or row["qualifies"] is not False:
            fail("missing result was promoted: " + row["result_id"])

    assessment = report["artifact_assessment"]
    if assessment["all_required_absent"] is not True:
        fail("artifact assessment does not record the exact blocker")
    if assessment["runtime_presence"]["present"] is not False:
        fail("runtime is unexpectedly present; re-evaluate the package")
    if assessment["package_assets"]["present"] is not False:
        fail("package unexpectedly contains a licensed asset")
    if not assessment["conclusion"].startswith("BLOCKED:"):
        fail("artifact conclusion is not an explicit blocker")

    fixture = report["fixture"]
    if (fixture["sample_rate_hz"] != reference.SAMPLE_RATE_HZ
            or fixture["frame_samples"] != reference.FRAME_SAMPLES
            or fixture["frames"] != reference.FIXTURE_FRAMES):
        fail("fixture geometry mismatch")
    for key in ("render_sha256", "near_sha256", "echo_sha256",
                "microphone_sha256", "reference_sha256"):
        if len(fixture[key]) != 64:
            fail("fixture digest is not SHA-256: " + key)
    if report["ranking"]["order"] != "not_ranked" or report["ranking"]["qualifies"] is not False:
        fail("level ranking is not explicitly withheld")
    assert_no_qualifying(report)
    print("verify: report canonical, byte-identical, digest " + digest)


def check_three_repeats() -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    original = (ROOT / "report.json").read_bytes()
    for flag in ("--report", "--sources", "--inspect"):
        outputs: List[bytes] = []
        for _ in range(3):
            completed = subprocess.run([sys.executable, "run.py", flag], cwd=ROOT,
                                       env=environment, stdout=subprocess.PIPE,
                                       stderr=subprocess.PIPE, check=False)
            if completed.returncode != 0:
                fail("run.py " + flag + " failed: "
                     + completed.stderr.decode("utf-8", "replace"))
            outputs.append(completed.stdout)
        if len(set(outputs)) != 1:
            fail("run.py " + flag + " output differs across three cold starts")
        if flag == "--report" and (ROOT / "report.json").read_bytes() != original:
            fail("--report changed report.json bytes")
        if flag == "--sources" and outputs[0] != (ROOT / "SOURCES.sha256").read_bytes():
            fail("--sources does not reproduce SOURCES.sha256")
    print("verify: 3/3 byte-identical cold-start repeats for --report/--sources/--inspect")


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
    for name in ("contract.json", "report.json", "report.json.sha256", "SOURCES.sha256"):
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
        check_contract(contract, report)
        check_report(report)
        check_three_repeats()
        check_hygiene()
        check_scope()
    except (OSError, ValueError, KeyError, TypeError, IndexError,
            subprocess.SubprocessError) as error:
        print("verify: FAIL " + str(error), file=sys.stderr)
        return 1
    print("verify: PASS strict-json pins linked-row canonical repeats gates "
          "instance toggles controls hygiene scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
