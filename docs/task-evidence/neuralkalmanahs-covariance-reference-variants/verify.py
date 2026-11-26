# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the NeuralKalmanAHS variant blocker.

It checks strict JSON, canonical bytes, exact pins, DEFER/not-qualified
semantics, the covariance/reference split, author-reported provenance, stable
linked-row identity (never the full mutable board), licensing, prohibited
artifacts, task-local git scope and three cold-start byte-identical
regenerations. It never writes package evidence.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

WORKTREE = reference.WORKTREE
SOURCE_ROOT = reference.SOURCE_ROOT
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
README_PATH = HERE / "README.md"
TASK_PREFIX = reference.TASK_PREFIX
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth",
    ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip",
    ".tar", ".gz", ".whl", ".npy", ".pyc", ".wasm", ".elf", ".hex",
}
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)


class VerificationError(AssertionError):
    pass


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def strict_load(path: Path) -> dict:
    try:
        return reference.loads_strict(path.read_text(encoding="utf-8"))
    except reference.EvidenceError as error:
        raise VerificationError(str(error))


def check_canonical(errors: list) -> str:
    report_payload = REPORT_PATH.read_bytes()
    try:
        report = strict_load(REPORT_PATH)
    except VerificationError as error:
        errors.append("report_json:" + str(error))
        return ""
    expected, digest = reference.canonical_report(report)
    if report_payload.decode("ascii", "replace") != expected:
        errors.append("report_not_canonical")
    sidecar = SIDECAR_PATH.read_text(encoding="ascii")
    if sidecar != digest + "  report.json\n":
        errors.append("sidecar_mismatch")
    contract_payload = CONTRACT_PATH.read_bytes()
    try:
        contract = strict_load(CONTRACT_PATH)
    except VerificationError as error:
        errors.append("contract_json:" + str(error))
        return digest
    if contract_payload.decode("ascii", "replace") != \
            reference.canonical_text(contract):
        errors.append("contract_not_canonical")
    return digest


def check_semantics(errors: list) -> None:
    report = strict_load(REPORT_PATH)
    contract = strict_load(CONTRACT_PATH)
    for name, document in (("report", report), ("contract", contract)):
        if document.get("decision") != "DEFER":
            errors.append(name + "_decision")
        if document.get("status") != "proposal_only_not_qualified":
            errors.append(name + "_status")
        if document.get("incomplete") is not True:
            errors.append(name + "_incomplete")
        if document.get("proposal_only") is not True:
            errors.append(name + "_proposal_only")
        if document.get("qualification_status") != "not_qualified":
            errors.append(name + "_qualification_status")
    if report["qualification"].get("status") != "not_qualified":
        errors.append("qualification_not_qualified")
    if report["qualification"].get("candidate_qualified") is not False:
        errors.append("candidate_qualified_true")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing_result_qualifies")
    gates = report.get("release_gates", [])
    if [gate.get("id") for gate in gates] != list(reference.GATE_IDS):
        errors.append("gate_ids")
    if len(gates) != 8:
        errors.append("gate_count")
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append("gate_not_blocked:" + str(gate.get("id")))
        if gate.get("qualifies") is not False:
            errors.append("gate_qualifies:" + str(gate.get("id")))
        if gate.get("linked_row", {}).get("task_id") != reference.TASK:
            errors.append("gate_link:" + str(gate.get("id")))
    artifacts = report.get("required_artifacts", [])
    if [row.get("id") for row in artifacts] != list(reference.ARTIFACT_IDS):
        errors.append("artifact_ids")
    if len(artifacts) != 7:
        errors.append("artifact_count")
    for row in artifacts:
        if row.get("status") != "absent" or row.get("present") is not False:
            errors.append("artifact_not_absent:" + str(row.get("id")))
    blockers = report.get("exact_blockers", [])
    if [row.get("id") for row in blockers] != list(reference.BLOCKER_IDS):
        errors.append("blocker_ids")
    if len(blockers) != 6:
        errors.append("blocker_count")
    for row in blockers:
        if row.get("status") != "open" or row.get("qualifies") is not False:
            errors.append("blocker_state:" + str(row.get("id")))
    variants = report.get("integration_variants", {})
    if variants.get("variant_count") != 2:
        errors.append("variant_count")
    if sorted(variants.get("variants", {})) != sorted(reference.VARIANT_IDS):
        errors.append("variant_ids")
    distinction = variants.get("distinction", {})
    if distinction.get("distinct_integration_points") is not True:
        errors.append("variants_not_distinct")
    if distinction.get("exact_variant_identity_recorded") is not False:
        errors.append("variant_identity_claimed")
    for name, variant in variants.get("variants", {}).items():
        if variant.get("present") is not False:
            errors.append("variant_present:" + name)
        if variant.get("qualifies_candidate") is not False:
            errors.append("variant_qualifies:" + name)
    author = report.get("author_reported_results", {})
    if author.get("reproduced_here") is not False:
        errors.append("author_results_reproduced")
    if author.get("qualifies_candidate") is not False:
        errors.append("author_results_qualify")
    if author.get("local_metrics") is not None:
        errors.append("author_local_metrics")
    controls = report.get("research_controls", {})
    if controls.get("rerun_here") is not False:
        errors.append("prior_pilot_rerun")
    if controls.get("qualifies_candidate") is not False:
        errors.append("prior_pilot_qualifies")
    for probe in ("source_probe", "checkpoint_probe", "cohort_probe"):
        if report.get(probe, {}).get("present") is not False:
            errors.append(probe + "_present")
    if report.get("runtime_probe", {}).get("pinned") is not False:
        errors.append("runtime_pinned")
    if report.get("license_probe", {}).get("review") != "blocked":
        errors.append("license_review")
    if report.get("evidence_status") != "incomplete":
        errors.append("evidence_status")
    boundary = report.get("boundary", {})
    for key in ("provider_registered", "enabled_by_default",
                "public_api_abi_changed", "shared_cmake_changed",
                "registry_changed", "real_corpus_or_weights",
                "benchmark_claim", "release_claim", "ci_changed",
                "descriptor_registration"):
        if boundary.get(key) is not False:
            errors.append("boundary_flag:" + key)
    if boundary.get("installed_v0_unchanged") is not True:
        errors.append("installed_v0_changed")
    for key, value in report.get("local_harness_checks", {}).items():
        if value is not True:
            errors.append("local_harness_check:" + key)
    try:
        reference.validate_contract(contract)
    except reference.EvidenceError as error:
        errors.append("contract_mismatch:" + str(error))
    for key in ("task", "title", "component", "mode", "repository",
                "base_commit", "branch", "decision", "status",
                "qualification_status"):
        if report.get(key) != contract.get(key):
            errors.append("contract_report_mismatch:" + key)


def check_pins(errors: list) -> None:
    try:
        rows = reference.parse_pin_lines(
            SOURCES_PATH.read_text(encoding="ascii"))
    except reference.EvidenceError as error:
        errors.append("pin_parse:" + str(error))
        return
    keys = {path for _, path in rows}
    if keys != reference.allowed_pin_keys():
        errors.append("pin_key_set")
    for forbidden in (
            reference.TASK_PREFIX + "SOURCES.sha256",
            reference.TASK_PREFIX + "README.md",
            "source:" + reference.BOARD_TASK_ROW,
            "sdk:" + reference.BOARD_TASK_ROW):
        if forbidden in keys:
            errors.append("forbidden_pin:" + forbidden)
    if reference.TASK_PREFIX + "contract.json" not in keys:
        errors.append("contract_not_pinned")
    if reference.TASK_PREFIX + "report.json" not in keys:
        errors.append("report_not_pinned")
    if reference.TASK_PREFIX + "report.json.sha256" not in keys:
        errors.append("sidecar_not_pinned")
    for digest, path in rows:
        if path.startswith("source:"):
            target = SOURCE_ROOT / path[len("source:"):]
        elif path.startswith("sdk:"):
            target = WORKTREE / path[len("sdk:"):]
        else:
            target = WORKTREE / path
        if not target.is_file():
            errors.append("pin_target_missing:" + path)
            continue
        if sha256_file(target) != digest:
            errors.append("pin_mismatch:" + path)


def check_readme(errors: list) -> None:
    if not README_PATH.is_file():
        errors.append("readme_missing")
        return
    text = README_PATH.read_text(encoding="utf-8")
    try:
        reference.verify_readme_digests(text)
    except reference.EvidenceError as error:
        errors.append("readme_digest:" + str(error))
    for token in ("proposal_only_not_qualified", "DEFER", "not_qualified",
                  "eight release gates blocked", "covariance",
                  "reference", "ART-01", "RG-08"):
        if token not in text:
            errors.append("readme_token:" + token)
    if reference.update_readme_tables(text) != text:
        errors.append("readme_table_not_regenerated")


def check_board(errors: list) -> None:
    report = strict_load(REPORT_PATH)
    try:
        row = reference.board_row_projection()
        rows = reference.linked_rows()
    except reference.EvidenceError as error:
        errors.append("board:" + str(error))
        return
    if report.get("board_row") != row:
        errors.append("board_row_mismatch")
    if report.get("board_links") != [dict(item) for item in rows]:
        errors.append("board_links_mismatch")
    if report.get("board_link_projection_sha256") != \
            reference.linked_rows_digest(rows):
        errors.append("board_digest_mismatch")
    if report.get("board_full_file_hashed") is not False:
        errors.append("board_full_file_hashed")
    board_digest = sha256_file(SOURCE_ROOT / reference.BOARD_TASK_ROW)
    blob = json.dumps(report, sort_keys=True)
    if board_digest in blob:
        errors.append("full_board_digest_leaked")


def check_prohibited(errors: list) -> None:
    for path in HERE.rglob("*"):
        if path.is_symlink():
            errors.append("symlink:" + path.name)
            continue
        if path.is_dir():
            if path.name == "__pycache__":
                errors.append("pycache_present")
            continue
        if path.suffix.lower() in PROHIBITED_SUFFIXES:
            errors.append("prohibited_suffix:" + path.name)
    for name in SIDECAR_FILES:
        path = HERE / name
        if not path.is_file():
            errors.append("sidecar_missing:" + name)
            continue
        text = path.read_text(encoding="utf-8")
        if SPDX_NEEDLE not in text or SPDX_COPYRIGHT not in text:
            errors.append("sidecar_spdx:" + name)
    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_NEEDLE not in text or SPDX_COPYRIGHT not in text:
            errors.append("source_spdx:" + name)


def check_git_scope(errors: list) -> None:
    try:
        top = subprocess.run(
            ["git", "-C", str(WORKTREE), "rev-parse", "--show-toplevel"],
            check=True, capture_output=True, text=True).stdout.strip()
    except (OSError, subprocess.CalledProcessError):
        errors.append("git_unavailable")
        return
    if Path(top).resolve() != WORKTREE.resolve():
        errors.append("git_toplevel_mismatch")
        return
    result = subprocess.run(
        ["git", "-C", str(WORKTREE), "status", "--porcelain",
         "--untracked-files=all"],
        check=True, capture_output=True, text=True).stdout
    for line in result.splitlines():
        if not line.strip():
            continue
        path = line[3:]
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        path = path.strip().strip('"')
        if not path.startswith(TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / ("cold-" + str(index))
    package = scratch / "sdk" / "docs" / "task-evidence" / reference.COMPONENT
    package.mkdir(parents=True)
    for source in HERE.iterdir():
        if source.is_file():
            shutil.copy2(source, package / source.name)
    sdk_root = package.parents[2]
    for relative in reference.BOUNDARY_PINS:
        target = sdk_root / relative
        target.parent.mkdir(parents=True, exist_ok=True)
        os.symlink(WORKTREE / relative, target)
    return package


def check_cold_start(errors: list) -> list:
    digests = []
    with tempfile.TemporaryDirectory(
            prefix="sdk-neuralkalmanahs-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            package = _prepare_scratch(root, index)
            environment = dict(os.environ)
            environment["PYTHONDONTWRITEBYTECODE"] = "1"
            environment["SOURCE_ROOT"] = str(SOURCE_ROOT)
            result = subprocess.run(
                [sys.executable, "run.py"],
                cwd=str(package), env=environment,
                capture_output=True, text=True)
            if result.returncode != 0:
                errors.append("cold_start_" + str(index) + "_failed:" +
                              result.stderr.strip()[:200])
                continue
            digests.append(sha256_file(package / "report.json"))
            for name in ("report.json", "report.json.sha256",
                         "contract.json", "SOURCES.sha256", "README.md"):
                if (package / name).read_bytes() != (HERE / name).read_bytes():
                    errors.append("cold_start_" + str(index) +
                                  "_bytes_differ:" + name)
        if len(digests) != 3 or len(set(digests)) != 1:
            errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors = []
    digest = check_canonical(errors)
    check_semantics(errors)
    check_pins(errors)
    check_readme(errors)
    check_board(errors)
    check_prohibited(errors)
    check_git_scope(errors)
    digests = check_cold_start(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        return 1
    print("PASS canonical=true decision=DEFER status=proposal_only_not_qualified "
          "qualification=not_qualified gates=8/8_blocked "
          "variants=2/2_blocked cold_starts=" + str(len(digests)) +
          "/3 byte_identical=true report_sha256=" + digest)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
