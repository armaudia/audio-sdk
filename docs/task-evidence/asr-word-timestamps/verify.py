# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the ASR word-timestamp boundary DEFER package.

Checks strict JSON, exact source/boundary/sibling/local pins, the stable linked
task-row identity, canonical contract/report bytes, three cold-start repeats,
eight blocked release gates, the declared external boundary, present-but-
unlicensed model/runtime bytes, adverse/missing/invalid/nonfinite controls,
SPDX annotations, dependency hygiene and task-local scope containment. The
mutable full board file is never hashed; only the stable linked row is compared.
"""

from __future__ import annotations

import ast
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

WORKTREE = HERE.parents[2]
AUDIO_ROOT = reference.AUDIO_ROOT
CONTRACT = HERE / "contract.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
SPDX = "SPDX" "-License-Identifier:"
SPDX_COPY = "SPDX" "-FileCopyrightText:"

FORBIDDEN_SUFFIXES = {
    ".onnx", ".pt", ".pth", ".wav", ".flac", ".mp3", ".m4a", ".bin", ".so",
    ".dylib", ".dll", ".a", ".zip", ".tar", ".gz", ".whl", ".pyc",
    ".safetensors", ".ort", ".tflite",
}
FORBIDDEN_IMPORT_ROOTS = {
    "numpy", "scipy", "soundfile", "librosa", "onnxruntime", "torch", "vosk",
    "sherpa_onnx", "faster_whisper", "ctranslate2", "transformers",
    "requests", "httpx", "aiohttp",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def strict_json(path: Path) -> dict:
    try:
        return reference.read_strict_json(path)
    except (OSError, ValueError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    raise AssertionError("unreachable")


def sha(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def parse_manifest() -> dict[str, str]:
    manifest: dict[str, str] = {}
    for line in PINS.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        digest, name = line.split("  ", 1)
        if name in manifest:
            fail("duplicate manifest entry: " + name)
        manifest[name] = digest
    return manifest


def check_pins(errors: list[str]) -> int:
    count = 0
    for relative, expected in reference.SOURCE_PINS.items():
        path = AUDIO_ROOT / relative
        if not path.is_file():
            errors.append("missing pinned source: " + relative)
            continue
        actual = sha(path)
        if actual != expected:
            errors.append("pinned source changed: " + relative + " " + actual)
        count += 1
    for group, pins in (("boundary", reference.BOUNDARY_PINS),
                        ("sibling", reference.SIBLING_PINS)):
        for relative, expected in pins.items():
            path = WORKTREE / relative
            if not path.is_file():
                errors.append("missing " + group + " pin: " + relative)
                continue
            actual = sha(path)
            if actual != expected:
                errors.append(group + " pin changed: " + relative + " "
                             + actual)
            count += 1
    manifest = parse_manifest()
    if "audio-benchmark-platform/plan/swarm/TASKS.json" in manifest:
        errors.append("mutable board file must not be in SOURCES.sha256")
    return count


def check_local_manifest(errors: list[str]) -> None:
    manifest = parse_manifest()
    if "SOURCES.sha256" in manifest:
        errors.append("SOURCES.sha256 must not pin itself")
    for name, expected in manifest.items():
        if not name.startswith(reference.TASK_PREFIX):
            continue
        path = HERE / name[len(reference.TASK_PREFIX):]
        if not path.is_file():
            errors.append("missing local artifact: " + name)
            continue
        if sha(path) != expected:
            errors.append("local artifact changed: " + name)
    allowed = set(run.LOCAL_PIN_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned task file: " + path.name)
    for name in run.LOCAL_PIN_FILES:
        if (reference.TASK_PREFIX + name) not in manifest:
            errors.append("local file not pinned: " + name)


def check_present_assets(errors: list[str]) -> None:
    for label, model in (("vosk", reference.VOSK_MODEL),
                         ("sherpa", reference.SHERPA_MODEL)):
        root = AUDIO_ROOT / model["relative"]
        if not root.exists():
            continue
        if not root.is_dir():
            errors.append("present asset is not a directory: " + label)
            continue
        digest, count, size = reference.tree_digest(root)
        if digest != model["tree_sha256"]:
            errors.append("tree digest changed: " + label + " " + digest)
        if count != model["file_count"]:
            errors.append("tree file count changed: " + label)
        if size != model["byte_count"]:
            errors.append("tree byte count changed: " + label)
        for relative, expected in model["files"].items():
            path = root / relative
            if not path.is_file():
                errors.append("model file missing: " + label + ":" + relative)
            elif sha(path) != expected:
                errors.append("model file changed: " + label + ":" + relative)
    runtime_root = AUDIO_ROOT / reference.SCRATCH_ROOT
    for relative, expected in reference.RUNTIME_FILES.items():
        path = runtime_root / relative
        if not path.is_file():
            continue
        if sha(path) != expected:
            errors.append("runtime file changed: " + relative)
    for label, model in (("vosk", reference.VOSK_MODEL),
                         ("sherpa", reference.SHERPA_MODEL)):
        root = AUDIO_ROOT / model["relative"]
        if not root.is_dir():
            continue
        for name in ("LICENSE", "LICENSE.txt", "NOTICE", "COPYING"):
            if (root / name).is_file():
                errors.append("unexpected license text in model tree: "
                              + label + ":" + name)


def check_contract(report: dict, errors: list[str]) -> None:
    contract = strict_json(CONTRACT)
    try:
        reference.validate_contract(contract)
    except ValueError as error:
        errors.append("contract validation: " + str(error))
    expected = reference.canonical_bytes(reference.build_contract())
    if CONTRACT.read_bytes() != expected:
        errors.append("contract.json is not canonical build_contract bytes")
    if contract.get("mode") != "feasibility":
        errors.append("contract mode must be feasibility")
    if contract.get("profile") != "rate":
        errors.append("contract profile must be rate")
    if report.get("contract_sha256") != reference.object_digest(contract):
        errors.append("report contract_sha256 mismatch")
    if contract["boundary"]["linked_row"] != report["linked_row_identity"][
            "projection"]:
        errors.append("report linked row projection mismatch")
    if contract["boundary"]["linked_row_sha256"] != report[
            "linked_row_identity"]["sha256"]:
        errors.append("report linked row digest mismatch")


def check_report(errors: list[str]) -> dict:
    report = strict_json(REPORT)
    if report.get("schema_id") != reference.REPORT_SCHEMA_ID:
        errors.append("report schema_id")
    if report.get("task") != reference.TASK:
        errors.append("report task")
    if report.get("decision") != "DEFER":
        errors.append("report decision")
    if report.get("status") != "incomplete":
        errors.append("report status")
    if report.get("proposal_only") is not True:
        errors.append("report proposal_only")
    if report.get("qualification_status") != "not_qualified":
        errors.append("report qualification_status")
    qualification = report.get("qualification", {})
    if qualification.get("not_qualified") is not True:
        errors.append("report not_qualified")
    if qualification.get("all_release_gates_blocked") is not True:
        errors.append("report all_release_gates_blocked")
    if qualification.get("real_result_present") is not False:
        errors.append("report real_result_present")

    gates = report.get("gates", [])
    if len(gates) != 8:
        errors.append("report gate count")
    if [gate.get("id") for gate in gates] != [
            f"RG-{index:02d}" for index in range(1, 9)]:
        errors.append("report gate ids")
    for gate in gates:
        if gate.get("status") != "blocked" or gate.get("qualifies") is not False:
            errors.append("report gate not blocked: " + str(gate.get("id")))
        if not gate.get("reopen_condition"):
            errors.append("report gate missing reopen: " + str(gate.get("id")))

    blockers = report.get("exact_blockers", [])
    if len(blockers) != 6:
        errors.append("report blocker count")
    gate_ids = {row.get("id") for row in gates}
    for blocker in blockers:
        if blocker.get("status") != "open":
            errors.append("report blocker not open")
        if blocker.get("qualifies") is not False:
            errors.append("report blocker qualifies")
        for gate in blocker.get("linked_gates", []):
            if gate not in gate_ids:
                errors.append("report blocker gate unknown: " + str(gate))

    artifacts = report.get("required_artifacts", [])
    if len(artifacts) != 7:
        errors.append("report artifact count")
    if not artifacts or artifacts[0].get("verified") is not True:
        errors.append("report research artifact not verified")
    model_artifact = next((row for row in artifacts
                           if row.get("id") == "ART-03"), None)
    if model_artifact is None:
        errors.append("report ART-03 missing")
    else:
        if model_artifact.get("present") is not True:
            errors.append("report ART-03 must record present bytes")
        if model_artifact.get("blocked") is not True:
            errors.append("report ART-03 must be blocked")

    rate = report.get("rate_profile", {})
    if rate.get("blocked_rows") != 8:
        errors.append("report rate rows not all blocked")
    for row in rate.get("rows", []):
        if row.get("status") != "blocked":
            errors.append("report rate row not blocked")

    models = report.get("exact_models", {})
    if set(models) != {"vosk", "sherpa_whisper_tiny_en"}:
        errors.append("report exact_models keys")
    for name, model in models.items():
        if model.get("present_bytes") is not True:
            errors.append("report model bytes absent: " + name)
        if model.get("digests_verified") is not True:
            errors.append("report model digests unverified: " + name)
        if model.get("rights_verified") is not False:
            errors.append("report model rights verified: " + name)
        if model.get("loaded_or_executed_here") is not False:
            errors.append("report model executed: " + name)
        if model.get("qualifies") is not False:
            errors.append("report model qualifies: " + name)

    assets = report.get("present_assets", {})
    for key in ("vosk_model", "sherpa_whisper_model"):
        row = assets.get(key, {})
        if not re.fullmatch(r"[0-9a-f]{64}", str(row.get("tree_sha256"))):
            errors.append("report asset tree digest: " + key)
        if row.get("file_count", 0) < 1 or row.get("byte_count", 0) < 1:
            errors.append("report asset counts: " + key)
    for name, expected in assets.get("runtime_files", {}).items():
        if not re.fullmatch(r"[0-9a-f]{64}", str(expected)):
            errors.append("report runtime digest: " + name)

    admission = report.get("admission", {})
    cases = admission.get("cases", [])
    if len(cases) != 37 or admission.get("case_count") != 37:
        errors.append("report admission case count")
    if admission.get("accepted_count") != 1:
        errors.append("report admission accepted count")
    if admission.get("rejected_count") != 36:
        errors.append("report admission rejected count")
    if admission.get("all_cases_match") is not True:
        errors.append("report admission mismatch")
    if admission.get("qualifies") is not False:
        errors.append("report admission qualifies")
    if admission.get("structural_only") is not True:
        errors.append("report admission not structural_only")
    reasons = {row.get("expected_reason") for row in cases}
    for required in ("keys", "decimal_format", "words.order", "words.overlap",
                     "audio.channels", "outcomes.nonfinite",
                     "rights.claims_qualified", "reference.not_independent"):
        if required not in reasons:
            errors.append("report admission missing case: " + required)

    control = report.get("scorer_control", {})
    if control.get("kind") != (
            "synthetic_arithmetic_control_not_evidence"):
        errors.append("report control kind")
    if control.get("matches") is not True or control.get("qualifies") is not False:
        errors.append("report control disposition")
    if control.get("observed", {}).get("words_per_minute_total") != "75.000":
        errors.append("report control arithmetic")

    for name in ("source_pins", "boundary_pins", "sibling_pins"):
        if not report.get(name):
            errors.append("report pins missing: " + name)
    if report.get("source_pins", {}) != reference.pin_rows(
            reference.SOURCE_PINS, reference.AUDIO_ROOT):
        errors.append("report source pins stale")

    identity = report.get("linked_row_identity", {})
    if identity.get("board_file_pinned") is not False:
        errors.append("report board file pinned")
    if identity.get("gating") != "stable_identity_only":
        errors.append("report gating mode")
    projected = reference.board_row_projection(
        reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    if identity.get("projection") != projected:
        errors.append("report linked row projection stale")
    if identity.get("sha256") != reference.board_row_digest(projected):
        errors.append("report linked row digest stale")
    if set(projected) != set(reference.BOARD_ROW_FIELDS):
        errors.append("report projection fields")

    payload, digest = reference.canonical_report(reference.build_report())
    if REPORT.read_bytes() != payload.encode("utf-8"):
        errors.append("report.json is not canonical build_report bytes")
    if SIDECAR.read_text(encoding="ascii") != digest + "  report.json\n":
        errors.append("report.json.sha256 sidecar mismatch")
    check_contract(report, errors)
    return report


def check_licensing(errors: list[str]) -> None:
    text = (HERE / "LICENSES.md").read_text(encoding="utf-8")
    for token in ("UNKNOWN", "Apache-2.0", "CC BY 4.0", "not a grant"):
        if token not in text:
            errors.append("LICENSES.md missing token: " + token)
    for name in ("contract.json", "report.json", "report.json.sha256",
                 "SOURCES.sha256"):
        sidecar = HERE / (name + ".license")
        if not sidecar.is_file():
            errors.append("missing SPDX sidecar: " + name + ".license")
            continue
        body = sidecar.read_text(encoding="utf-8")
        if SPDX not in body or SPDX_COPY not in body:
            errors.append("sidecar missing SPDX: " + name)


def check_source_hygiene(errors: list[str]) -> None:
    for name in ("reference.py", "run.py", "verify.py",
                 "test_reference.py"):
        path = HERE / name
        text = path.read_text(encoding="utf-8")
        if SPDX not in text or SPDX_COPY not in text:
            errors.append("missing SPDX header: " + name)
        tree = ast.parse(text)
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    if alias.name.split(".")[0] in FORBIDDEN_IMPORT_ROOTS:
                        errors.append("forbidden import: " + name + ":"
                                      + alias.name)
            elif isinstance(node, ast.ImportFrom) and node.module:
                if node.module.split(".")[0] in FORBIDDEN_IMPORT_ROOTS:
                    errors.append("forbidden import: " + name + ":"
                                  + node.module)
    for path in HERE.iterdir():
        if path.is_file() and path.suffix in FORBIDDEN_SUFFIXES:
            errors.append("forbidden artifact: " + path.name)


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(WORKTREE), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True)
    if result.returncode != 0:
        errors.append("git_status_failed:" + result.stderr.strip())
        return []
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(run.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(WORKTREE), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    base_diff = subprocess.run(
        ["git", "-C", str(WORKTREE), "diff", "--name-only",
         reference.BASE_COMMIT, "--", "."],
        capture_output=True, text=True)
    if base_diff.returncode != 0:
        errors.append("git_base_diff_failed:" + base_diff.stderr.strip())
    else:
        for path in base_diff.stdout.splitlines():
            if path and not path.startswith(run.TASK_PREFIX):
                errors.append("base_out_of_scope_change:" + path)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-ASR-WORD-TIMESTAMPS"
    target = sdk / reference.TASK_PREFIX.rstrip("/")
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    board = scratch / "audioml" / reference.BOARD_TASK_ROW
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(reference.AUDIO_ROOT / reference.BOARD_TASK_ROW)
    (scratch / "audioml/cpp-library").mkdir(parents=True, exist_ok=True)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(WORKTREE / relative)
    for relative in sorted(reference.SIBLING_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(WORKTREE / relative)
    return target


def check_cold_start(errors: list[str]) -> list[str]:
    committed = (
        (CONTRACT.read_bytes() if CONTRACT.is_file() else b""),
        (REPORT.read_bytes() if REPORT.is_file() else b""),
        (SIDECAR.read_bytes() if SIDECAR.is_file() else b""),
        (PINS.read_bytes() if PINS.is_file() else b""),
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(
            prefix="sdk-asr-word-timestamps-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"],
                                     cwd=target, capture_output=True,
                                     text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:"
                              + process.stderr.strip())
                continue
            generated = (
                (target / "contract.json").read_bytes(),
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[1]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    pins = check_pins(errors)
    check_local_manifest(errors)
    check_present_assets(errors)
    report = check_report(errors)
    check_licensing(errors)
    check_source_hygiene(errors)
    changed = check_scope(errors)
    digests = check_cold_start(errors)
    digest = (sha(REPORT) if REPORT.is_file() else "unavailable")
    if errors:
        for error in errors:
            print("FAIL: " + error, file=sys.stderr)
        print(f"FAIL pins={pins} cold_starts={len(digests)} "
              f"report_sha256={digest} changed_files={len(changed)} "
              f"failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} gates={len(report['gates'])} "
          f"blockers={len(report['exact_blockers'])} "
          f"admission_cases={len(report['admission']['cases'])} "
          f"cold_starts=3/3 byte_identical=true profile=Rate "
          f"status={report['status']} decision=DEFER "
          f"report_sha256={digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
