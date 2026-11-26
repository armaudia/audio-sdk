# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the Hecttor Hermes boundary DEFER package.

Checks strict JSON, exact external/boundary/sibling/local pins, the stable
linked task-row identity, canonical report and contract bytes, three cold-start
repeats, eight blocked release gates, the declared external boundary, null
candidate slots, adverse/missing/invalid/nonfinite controls, SPDX annotations,
dependency hygiene and task-local scope containment.  The mutable full board
file is never hashed; only the stable linked row is compared.
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

FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "librosa", "onnxruntime", "pystoi",
    "torch", "tensorflow", "requests", "pandas", "aiohttp", "httpx",
}
FORBIDDEN_ARTIFACT_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".m4a", ".onnx", ".ort", ".tflite", ".bin",
    ".whl", ".so", ".dylib", ".dll", ".a", ".zip", ".tar", ".gz",
}
FORBIDDEN_CALLS = {"urlopen", "urlretrieve", "requests_get", "download",
                   "wget", "system", "popen"}
ALLOWED_PROFILE_STATUS = {
    "synthetic_control_only", "blocked", "proposal_only",
}
MANIFEST_CONTROL_IDS = {
    "valid_shape", "missing_artifact_id", "extra_field", "wrong_candidate",
    "empty_family_id", "relative_artifact_path", "parent_traversal",
    "non_posix_path", "bad_hash_length", "uppercase_hash",
    "checksum_prefix_mismatch", "boolean_rate",
    "out_of_structural_rate_bound", "stereo", "denoise_only_false",
    "voice_boost_enabled", "speed_control_enabled", "telemetry_not_reviewed",
    "terms_not_accepted", "wrong_attestation", "duplicate_paths",
    "empty_sdk_version",
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
            fail("pinned source changed: " + name + " " + actual
                 + " != " + expected)
    for group, pins in (("boundary", reference.BOUNDARY_PINS),
                        ("sibling", reference.SIBLING_PINS)):
        for name, expected in pins.items():
            path = WORKTREE / name
            if not path.is_file():
                fail("missing " + group + " pin: " + name)
            actual = sha(path)
            if actual != expected:
                fail(group + " pin changed: " + name + " " + actual
                     + " != " + expected)
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
            fail("local artifact changed: " + name + " " + actual
                 + " != " + expected)
    actual_files = set()
    for path in ROOT.rglob("*"):
        if not path.is_file() or path.name == "SOURCES.sha256":
            continue
        if "__pycache__" in path.parts or path.suffix == ".pyc":
            continue
        actual_files.add(path.relative_to(ROOT).as_posix())
    if actual_files != set(manifest):
        fail("unpinned or missing local artifact: "
             + ",".join(sorted(actual_files.symmetric_difference(manifest))))
    if actual_files | {"SOURCES.sha256"} != set(reference.LOCAL_FILES):
        fail("local file set does not match the declared contract")
    print("verify: %d local artifacts exact" % len(manifest))


def check_linked_row(contract: Dict[str, Any], report: Dict[str, Any]) -> None:
    board = (WORKSPACE / "audio-benchmark-platform" / "plan" / "swarm"
             / "TASKS.json")
    data = strict_json(board)
    rows = [row for row in data.get("tasks", [])
            if row.get("id") == reference.TASK_ID]
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


def _check_common(document: Dict[str, Any], kind: str) -> None:
    if (document["schema_id"] != reference.SCHEMA_ID
            or document["task"] != reference.TASK_ID
            or document["component"] != reference.COMPONENT
            or document["title"] != reference.TITLE):
        fail(kind + " identity mismatch")
    if document["profile"] != "enhancement":
        fail(kind + " profile is not enhancement")
    if (document["status"] != reference.STATUS
            or document["completeness"] != reference.COMPLETENESS
            or document["decision"] != reference.DECISION
            or document["proposal_only"] is not True):
        fail(kind + " is not proposal-only/incomplete/DEFER")
    if (document["base_commit"] != reference.BASE_COMMIT
            or document["branch"] != reference.BRANCH):
        fail(kind + " base/branch mismatch")
    qualification = document["qualification"]
    if (qualification.get("status") != "not_qualified"
            or qualification.get("qualifies") is not False
            or qualification.get("incomplete") is not True
            or qualification.get("proposal_only") is not True
            or qualification.get("missing_result_promoted") is not False):
        fail(kind + " qualification is not not_qualified/incomplete")
    if document["task_row"] != reference.TASK_ROW_IDENTITY:
        fail(kind + " task_row mismatch")
    if document["mutable_provenance"] != reference.MUTABLE_PROVENANCE:
        fail(kind + " mutable provenance mismatch")
    if document["source_pins"] != reference.SOURCE_PINS:
        fail(kind + " source pins mismatch")
    if document["boundary_pins"] != reference.BOUNDARY_PINS:
        fail(kind + " boundary pins mismatch")
    if document["sibling_pins"] != reference.SIBLING_PINS:
        fail(kind + " sibling pins mismatch")
    if document["scope"] != reference.SCOPE:
        fail(kind + " scope mismatch")
    if document["public_surface"] != reference.PUBLIC_SURFACE:
        fail(kind + " public surface mismatch")
    if any(value is not False
           for value in document["public_surface"].values()):
        fail(kind + " public surface flag is not false")
    if document["vendor_record"] != reference.vendor_record():
        fail(kind + " vendor record mismatch")
    if document["vendor_record"]["declared_latency_ms"] is not None:
        fail(kind + " assumes a vendor latency value")
    if document["vendor_record"]["model_family_count"] != 2:
        fail(kind + " vendor family count mismatch")
    if document["declared_contract"] != reference.declared_contract():
        fail(kind + " declared contract mismatch")
    if document["declared_contract"]["declared_latency_ms"] is not None:
        fail(kind + " declared contract assumes a vendor latency value")
    if document["manifest_contract"] != reference.manifest_contract():
        fail(kind + " manifest contract mismatch")
    if document["release_gates"] != reference.RELEASE_GATES:
        fail(kind + " release gates mismatch")
    if len(document["release_gates"]) != 8:
        fail(kind + " must have exactly eight release gates")
    if any(gate["status"] != "blocked" or gate["qualifies"] is not False
           or gate["evidence"] is not None
           for gate in document["release_gates"]):
        fail(kind + " release gate is not blocked")
    if document["non_claims"] != reference.NON_CLAIMS:
        fail(kind + " non-claims mismatch")
    if document["reproduction"] != reference.REPRODUCTION:
        fail(kind + " reproduction mismatch")
    if document["proposal_only"] is not True:
        fail(kind + " is not proposal-only")


def check_contract(contract: Dict[str, Any]) -> None:
    if set(contract) != reference.CONTRACT_KEYS:
        fail("contract key set mismatch")
    _check_common(contract, "contract")
    required = contract["required_artifacts"]
    if required != reference.REQUIRED_ARTIFACTS:
        fail("contract required artifacts mismatch")
    if len(required) != 8 or any(item["present"] is not False
                                 for item in required):
        fail("contract required artifact is present or missing")
    if contract["local_files"] != list(reference.LOCAL_FILES):
        fail("contract local file list mismatch")
    manifest = parse_manifest()
    expected_pins = set(manifest) - {"contract.json", "SOURCES.sha256"}
    if set(contract["artifact_pins"]) != expected_pins:
        fail("contract artifact pins do not cover every local artifact")
    for name, expected in contract["artifact_pins"].items():
        if manifest.get(name) != expected:
            fail("contract artifact pin mismatch: " + name)
    raw = (ROOT / "contract.json").read_bytes()
    regenerated = reference.canonical_bytes(reference.contract_payload()) + b"\n"
    if raw != regenerated:
        fail("contract.json is not byte-identical after regeneration")
    assert_no_qualifying(contract)
    print("verify: contract incomplete/DEFER/not_qualified with 8 blocked gates")


def _check_control_rows(controls: Dict[str, Any]) -> None:
    design = controls["design"]
    if design["is_hecttor_hermes"] is not False \
            or design["is_candidate_result"] is not False:
        fail("control design claims Hermes or a candidate result")
    expected = {
        "identity_noisy", "fixed_highpass_noisy", "identity_clean",
        "fixed_highpass_clean", "identity_silence", "fixed_highpass_silence",
    }
    if set(controls["rows"]) != expected:
        fail("control row set mismatch")
    for name, row in controls["rows"].items():
        if row["control_id"] != name or row["samples"] != reference.FIXTURE_SAMPLES:
            fail("control row geometry mismatch: " + name)
        if row["is_candidate_result"] is not False or row["qualifies"] is not False:
            fail("control row qualifies: " + name)
        if row["nonfinite_samples"] != 0:
            fail("control row has nonfinite output: " + name)
        for key in ("rms", "peak_abs"):
            if not math.isfinite(float(row[key])):
                fail("control diagnostic is nonfinite: " + name)
        for key in ("output_sha256",):
            if not re.match(r"^[0-9a-f]{64}$", row[key]):
                fail("control digest is not SHA-256: " + name)
    silence = controls["silence"]
    if silence["identity_exact_zero"] is not True \
            or silence["fixed_highpass_exact_zero"] is not True \
            or silence["qualifies"] is not False:
        fail("silence control is not exact zero")
    if controls["rows"]["fixed_highpass_silence"]["peak_abs"] != 0.0:
        fail("fixed high-pass silence peak is not zero")


def _check_manifest_controls(rows: List[Dict[str, Any]]) -> None:
    if len(rows) != len(MANIFEST_CONTROL_IDS):
        fail("manifest control count mismatch")
    ids = [row["control_id"] for row in rows]
    if set(ids) != MANIFEST_CONTROL_IDS:
        fail("manifest control ids mismatch")
    if rows[0]["control_id"] != "valid_shape" or rows[0]["accepted"] is not True:
        fail("valid manifest shape is not accepted")
    if rows[0]["files_verified"] is not False \
            or rows[0]["official_identity"] is not False:
        fail("valid manifest shape claims file verification or identity")
    for row in rows[1:]:
        if row["accepted"] is not False:
            fail("adverse manifest was accepted: " + row["control_id"])
    for row in rows:
        if row["qualifies"] is not False:
            fail("manifest control qualifies")


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
    _check_common(report, "report")
    if report["required_artifacts"] != reference.REQUIRED_ARTIFACTS:
        fail("report required artifacts mismatch")
    if report["fixture"] != reference.fixture_payload():
        fail("report fixture mismatch")
    if report["fixture"]["samples"] != reference.FIXTURE_SAMPLES \
            or report["fixture"]["frames"] != reference.FIXTURE_FRAMES:
        fail("report fixture geometry mismatch")
    _check_control_rows(report["controls"])
    if report["controls"]["rows"]["identity_noisy"]["output_sha256"] \
            != report["fixture"]["mixture_sha256"]:
        fail("identity control is not an exact passthrough")
    _check_manifest_controls(report["manifest_controls"])
    adverse = report["adverse_results"]
    if len(adverse) != 10:
        fail("adverse result count mismatch")
    for row in adverse:
        if row["status"] != "rejected" or row["matches_expected"] is not True \
                or row["qualifies"] is not False:
            fail("adverse result was not rejected as expected: "
                 + row["result_id"])
    missing = report["missing_results"]
    if len(missing) < 10:
        fail("missing results are incomplete")
    for row in missing:
        if row["status"] != "blocked" or row["value"] is not None \
                or row["qualifies"] is not False:
            fail("missing result was promoted: " + row["result_id"])
    slots = report["qualification_slots"]
    if not slots:
        fail("qualification slots are missing")
    for key, slot in slots.items():
        if slot.get("value") is not None or slot.get("qualifies") is not False:
            fail("qualification slot is not null/non-qualifying: " + key)
    failure = report["failure_controls"]
    if failure["all_explicit"] is not True \
            or failure["rejected_audio_vectors"] != 10 \
            or failure["rejected_manifest_documents"] != len(
                MANIFEST_CONTROL_IDS) - 1 \
            or failure["blocked_release_gates"] != 8 \
            or failure["qualifies"] is not False:
        fail("failure controls are not explicit")
    if not all(failure["checks"].values()):
        fail("failure control check failed")
    profile = report["acceptance_profile"]
    if profile["profile"] != "enhancement" or profile["all_qualify"] is not False \
            or profile["qualifies"] is not False \
            or profile["missing_result_promoted"] is not False:
        fail("enhancement profile application is qualifying")
    if not profile["items"] or any(item["qualifies"] is not False
                                   for item in profile["items"]):
        fail("acceptance profile item qualifies or is empty")
    if any(item["status"] not in ALLOWED_PROFILE_STATUS
           for item in profile["items"]):
        fail("acceptance profile item has an unexpected status")
    provenance = report["observed_provenance"]
    if provenance["reproduced_here"] is not False:
        fail("observed provenance is claimed reproduced")
    for item in provenance["documented_context"]:
        if item["reproduced_here"] is not False \
                or item["is_measurement"] is not False \
                or item["is_human_rating"] is not False \
                or item["qualifies"] is not False:
            fail("observed provenance relabels a source or measurement")
    assessment = report["artifact_assessment"]
    if assessment["all_required_absent"] is not True:
        fail("artifact assessment does not record the exact blocker")
    if assessment["vendor_artifact_present"] is not False \
            or assessment["vendor_runtime_present"] is not False \
            or assessment["rights_approval_present"] is not False \
            or assessment["corpus_present"] is not False \
            or assessment["package_assets_present"] is not False:
        fail("a required artifact or runtime appeared; re-evaluate the package")
    if not assessment["conclusion"].startswith("BLOCKED:"):
        fail("artifact conclusion is not an explicit blocker")
    ranking = report["ranking"]
    if ranking["order"] != "not_ranked" or ranking["recommendation"] is not None \
            or ranking["qualifies"] is not False:
        fail("ranking is not explicitly withheld")
    if report["decision"] != "DEFER":
        fail("decision is not DEFER")
    assert_no_qualifying(report)
    print("verify: report canonical, byte-identical, digest " + digest)


def check_three_repeats() -> None:
    environment = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    original_report = (ROOT / "report.json").read_bytes()
    original_contract = (ROOT / "contract.json").read_bytes()
    for flag in ("--report", "--contract", "--sources", "--inspect"):
        outputs: List[bytes] = []
        for _ in range(3):
            completed = subprocess.run(
                [sys.executable, "run.py", flag], cwd=ROOT, env=environment,
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
            if completed.returncode != 0:
                fail("run.py " + flag + " failed: "
                     + completed.stderr.decode("utf-8", "replace"))
            outputs.append(completed.stdout)
        if len(set(outputs)) != 1:
            fail("run.py " + flag + " output differs across three cold starts")
        if flag == "--report" \
                and (ROOT / "report.json").read_bytes() != original_report:
            fail("--report changed report.json bytes")
        if flag == "--contract" \
                and (ROOT / "contract.json").read_bytes() != original_contract:
            fail("--contract changed contract.json bytes")
        if flag == "--sources" \
                and outputs[0] != (ROOT / "SOURCES.sha256").read_bytes():
            fail("--sources does not reproduce SOURCES.sha256")
    print("verify: 3/3 byte-identical cold-start repeats for "
          "--report/--contract/--sources/--inspect")


def _readme_digest_rows() -> Dict[str, Dict[str, str]]:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    groups: Dict[str, Dict[str, str]] = {"source": {}, "boundary": {},
                                         "sibling": {}}
    pattern = re.compile(r"^\| `(source|boundary|sibling):([^`]+)` \| "
                         r"`([0-9a-f]{64})` \|$", re.MULTILINE)
    for group, name, digest in pattern.findall(text):
        groups[group][name] = digest
    return groups


def check_readme() -> None:
    text = (ROOT / "README.md").read_text(encoding="utf-8")
    if SPDX_TAG not in text or SPDX_COPYRIGHT not in text:
        fail("README SPDX annotation missing")
    if "DEFER" not in text or "not_qualified" not in text:
        fail("README decision/qualification statement missing")
    if "eight" not in text.lower():
        fail("README release-gate statement missing")
    rows = _readme_digest_rows()
    if rows["source"] != reference.SOURCE_PINS:
        fail("README source pin table mismatch")
    if rows["boundary"] != reference.BOUNDARY_PINS:
        fail("README boundary pin table mismatch")
    if rows["sibling"] != reference.SIBLING_PINS:
        fail("README sibling pin table mismatch")
    print("verify: README decision, gates and exact pin tables")


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
            elif isinstance(node, ast.ImportFrom) and node.level == 0 \
                    and node.module:
                roots = {node.module.split(".")[0]}
            if roots & FORBIDDEN_IMPORT_ROOTS:
                fail("forbidden dependency import in " + path.name)
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Name) \
                    and node.func.id in FORBIDDEN_CALLS:
                fail("download/process-like call in " + path.name)
    for path in ROOT.rglob("*"):
        if path.is_file() and path.suffix.lower() in FORBIDDEN_ARTIFACT_SUFFIXES:
            fail("forbidden native/asset artifact: " + path.name)
    print("verify: SPDX annotations, %d tests, dependency and artifact hygiene"
          % count)


def check_scope() -> None:
    result = subprocess.run(
        ["git", "status", "--porcelain", "--untracked-files=all"],
        cwd=WORKTREE, stdout=subprocess.PIPE, stderr=subprocess.PIPE,
        check=False)
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
        check_three_repeats()
        check_readme()
        check_hygiene()
        check_scope()
    except (OSError, ValueError, KeyError, TypeError, IndexError,
            subprocess.SubprocessError) as error:
        print("verify: FAIL " + str(error), file=sys.stderr)
        return 1
    print("verify: PASS strict-json pins linked-row canonical repeats gates "
          "boundary null-slots controls hygiene scope")
    return 0


if __name__ == "__main__":
    sys.exit(main())
