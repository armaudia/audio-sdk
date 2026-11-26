# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verifier for the SDK-ESSENTIA blocker package.

It checks strict JSON, canonical bytes, exact pins, DEFER/not-qualified
semantics, the documented external boundary, stable linked-row identity (never
the full mutable board), licensing, prohibited artifacts, task-local git scope,
`python3 -m reuse lint`, and three cold-start byte-identical regenerations. It
never writes package evidence.
"""

from __future__ import annotations

import hashlib
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
from typing import Any, Dict, List, Tuple

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run  # noqa: E402

SDK_ROOT = HERE.parents[2]
WORKSPACE = HERE.parents[5]
REPORT_PATH = HERE / "report.json"
SIDECAR_PATH = HERE / "report.json.sha256"
CONTRACT_PATH = HERE / "contract.json"
SOURCES_PATH = HERE / "SOURCES.sha256"
BOARD_PATH = WORKSPACE / "audio-benchmark-platform/plan/swarm/TASKS.json"
TASK_PREFIX = "docs/task-evidence/essentia/"
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
TASK_ID = "SDK-ESSENTIA"
COMPONENT = "essentia"
BASE_COMMIT = "23526250a3a0a66c1f93089ff6fb697b5e776965"
GATE_IDS = ["RG-0" + str(number) for number in range(1, 9)]
EXPECTED_LINK = {
    "task_id": TASK_ID,
    "title": "Essentia",
    "mode": "feasibility",
    "repository": "audio-sdk",
    "component": COMPONENT,
}
ARTIFACT_FILES = (
    "README.md",
    "contract.json",
    "reference.py",
    "report.json",
    "report.json.sha256",
    "run.py",
    "SOURCES.sha256",
    "test_reference.py",
    "verify.py",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
PROHIBITED_SUFFIXES = {
    ".wav", ".flac", ".mp3", ".ogg", ".opus", ".onnx", ".pt", ".pth",
    ".ckpt", ".safetensors", ".bin", ".so", ".dylib", ".a", ".o", ".zip",
    ".tar", ".gz", ".whl", ".npy", ".pyc", ".wasm", ".elf", ".hex",
}
PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility "
    "and playback buffering.",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window.",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation.",
)
CHECK_IDS = (
    "identity_1x_factor",
    "rate_0_8_factor",
    "rate_1_2_factor",
    "duration_mapping_exact",
    "speech_no_stable_factor",
    "silence_no_onsets",
    "music_stable_factor",
    "rebuffer_gap_suppressed",
    "drift_recorded",
    "final_partial_valid",
    "final_partial_event_in_window",
    "availability_nonnegative",
    "pitch_unmeasured",
    "device_buffer_unmeasured",
    "factor_not_audio_output",
    "candidate_processing_false",
    "all_requests_rejected",
    "all_json_rejected",
    "missing_result_blocked",
    "all_gates_blocked",
    "no_result_qualifies",
)


def check(condition: Any, message: str, problems: List[str]) -> None:
    if not condition:
        problems.append(message)


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(Path(path).read_bytes())


def strict_load(path: Path) -> Any:
    return reference.strict_json_load(path)


def check_profile_source(problems: List[str]) -> None:
    path = WORKSPACE / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
    expected = reference.SOURCE_PINS.get(
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    check(path.is_file(), "verification profile source is missing", problems)
    if not path.is_file():
        return
    check(sha256_file(path) == expected,
          "verification profile source is not pinned", problems)
    text = path.read_text(encoding="utf-8")
    rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    check(len(rows) == 1, "rate profile row is not unique", problems)
    if len(rows) != 1:
        return
    for phrase in PROFILE_PHRASES:
        check(phrase in rows[0],
              "rate profile phrase missing: " + phrase[:32], problems)


def expected_pin_map(report_payload: bytes, sidecar_payload: bytes
                     ) -> Dict[str, Tuple[str, Path]]:
    expected: Dict[str, Tuple[str, Path]] = {}
    for path, digest in reference.SOURCE_PINS.items():
        expected["source:" + path] = (digest, WORKSPACE / path)
    for path, digest in reference.BOUNDARY_PINS.items():
        expected[path] = (digest, SDK_ROOT / path)
    for name in run.MANIFEST_FILES:
        if name == "report.json":
            digest = sha256_bytes(report_payload)
        elif name == "report.json.sha256":
            digest = sha256_bytes(sidecar_payload)
        else:
            digest = sha256_file(HERE / name)
        expected[TASK_PREFIX + name] = (digest, HERE / name)
    return expected


def check_pins(report_payload: bytes, sidecar_payload: bytes,
               sources_payload: bytes, problems: List[str]) -> int:
    check(SOURCES_PATH.is_file(), "SOURCES.sha256 is missing", problems)
    if not SOURCES_PATH.is_file():
        return 0
    expected = expected_pin_map(report_payload, sidecar_payload)
    seen: Dict[str, str] = {}
    count = 0
    for line in SOURCES_PATH.read_text(encoding="utf-8").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        parts = line.split("  ", 1)
        check(len(parts) == 2, "malformed pin line: " + repr(line), problems)
        if len(parts) != 2:
            continue
        digest, name = parts
        check(len(digest) == 64 and
              all(char in "0123456789abcdef" for char in digest),
              "malformed pin digest for " + name, problems)
        check(name in expected, "unexpected pin: " + name, problems)
        check(name not in seen, "duplicate pin: " + name, problems)
        if name in seen or name not in expected:
            continue
        seen[name] = digest
        pinned, path = expected[name]
        check(digest == pinned, "pinned digest mismatch: " + name, problems)
        check(path.is_file(), "pin target missing: " + name, problems)
        if path.is_file():
            check(sha256_file(path) == digest,
                  "pinned bytes changed: " + name, problems)
    for name in sorted(set(expected) - set(seen)):
        problems.append("pin absent: " + name)
    check(SOURCES_PATH.read_bytes() ==
          run.build_sources_bytes(report_payload, sidecar_payload),
          "SOURCES.sha256 is not deterministically generated", problems)
    full_board_digest = sha256_file(BOARD_PATH) if BOARD_PATH.is_file() else ""
    check(bool(full_board_digest) and
          full_board_digest not in SOURCES_PATH.read_text(encoding="utf-8"),
          "SOURCES.sha256 pins the mutable full board", problems)
    return count


def check_contract(contract: Dict[str, Any], report: Dict[str, Any],
                   problems: List[str]) -> None:
    check(contract.get("schema_id") == reference.CONTRACT_SCHEMA_ID,
          "contract schema id mismatch", problems)
    for key, value in (
            ("task", reference.TASK), ("component", reference.COMPONENT),
            ("mode", reference.MODE), ("branch", reference.BRANCH),
            ("base_commit", BASE_COMMIT),
            ("verification_profile", "Rate"),
            ("status", "proposal_only_not_qualified"),
            ("decision", "DEFER"),
            ("qualification_status", "not_qualified")):
        check(contract.get(key) == value,
              "contract field mismatch: " + key, problems)
    check(contract.get("incomplete") is True, "contract is not incomplete",
          problems)
    check(contract.get("proposal_only") is True,
          "contract is not proposal-only", problems)
    check(contract.get("board_full_file_hashed") is False,
          "contract hashes the full mutable board", problems)
    qualification = contract.get("qualification", {})
    check(qualification.get("status") == "not_qualified",
          "contract qualification status mismatch", problems)
    check(qualification.get("decision") == "DEFER",
          "contract qualification decision mismatch", problems)
    check(qualification.get("candidate_qualified") is False,
          "contract candidate is qualified", problems)
    check(qualification.get("readiness") == "incomplete",
          "contract readiness is not incomplete", problems)
    check(contract.get("comparison_status") ==
          "blocked_source_rights_runtime_models_and_fixtures_absent",
          "contract comparison status mismatch", problems)
    gates = contract.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "contract gate ids mismatch", problems)
    check(len(gates) == 8 and all(
        gate.get("status") == "blocked" and gate.get("reason") and
        gate.get("reopen") for gate in gates),
        "contract release gates are not eight blocked entries", problems)
    check(contract.get("remaining_gates") == GATE_IDS,
          "contract remaining gates mismatch", problems)
    artifacts = contract.get("required_artifacts", [])
    check(len(artifacts) == 6 and all(
        row.get("status") == "absent" and row.get("rights_reviewed") is False
        and row.get("sha256") is None for row in artifacts),
        "contract required artifacts are not all absent", problems)
    check(contract.get("missing_artifacts") ==
          [row.get("artifact") for row in artifacts],
          "contract missing artifacts mismatch", problems)
    blocker = contract.get("upstream_blocker", {})
    check(blocker.get("status") ==
          "blocked_source_rights_runtime_models_and_fixtures_absent",
          "contract upstream blocker status mismatch", problems)
    check(blocker.get("source", {}).get("revision") is None and
          blocker.get("source_digest") is None and
          blocker.get("runtime_digest") is None and
          blocker.get("models_digest") is None and
          blocker.get("fixture_digest") is None and
          blocker.get("license_digest") is None,
          "contract blocker hides a present digest", problems)
    check(contract.get("geometry") == report.get("geometry"),
          "contract geometry mismatch", problems)
    bound = contract.get("boundary", {})
    check(bound.get("installed_v0_unchanged") is True and
          bound.get("provider_registered") is False and
          bound.get("descriptor_registration") is False and
          bound.get("enabled_by_default") is False and
          bound.get("opt_in_required") is True and
          bound.get("public_api_abi_changed") is False and
          bound.get("ci_changed") is False,
          "contract boundary claims a shared change", problems)
    check(contract.get("source_pins") == reference.SOURCE_PINS,
          "contract source pins mismatch", problems)
    check(contract.get("boundary_pins") == reference.BOUNDARY_PINS,
          "contract boundary pins mismatch", problems)
    pins = contract.get("artifact_pins", {})
    check(sorted(pins) == sorted(run.CONTRACT_ARTIFACTS),
          "contract artifact pin set mismatch", problems)
    for name in run.CONTRACT_ARTIFACTS:
        if name == "report.json":
            actual = sha256_bytes(REPORT_PATH.read_bytes())
        elif name == "report.json.sha256":
            actual = sha256_bytes(SIDECAR_PATH.read_bytes())
        elif name == "SOURCES.sha256":
            actual = sha256_bytes(SOURCES_PATH.read_bytes())
        else:
            target = HERE / name
            actual = sha256_file(target) if target.is_file() else ""
        check(pins.get(name) == actual,
              "contract artifact pin mismatch: " + name, problems)
    check(contract.get("canonical_report", {}).get("file_sha256") ==
          sha256_bytes(REPORT_PATH.read_bytes()),
          "contract canonical report file digest mismatch", problems)
    check(contract.get("canonical_report", {}).get("canonical_digest") ==
          sha256_bytes(reference.canonical_bytes(report)),
          "contract canonical report digest mismatch", problems)


def check_report(report: Dict[str, Any], problems: List[str]) -> None:
    for key, value in (
            ("schema_id", reference.SCHEMA_ID), ("task", reference.TASK),
            ("component", reference.COMPONENT), ("mode", reference.MODE),
            ("verification_profile", "Rate"),
            ("base_commit", BASE_COMMIT), ("branch", reference.BRANCH),
            ("status", "proposal_only_not_qualified"),
            ("decision", "DEFER"),
            ("qualification_status", "not_qualified"),
            ("comparison_status",
             "blocked_source_rights_runtime_models_and_fixtures_absent")):
        check(report.get(key) == value,
              "report field mismatch: " + key, problems)
    check(report.get("incomplete") is True, "report is not incomplete",
          problems)
    check(report.get("proposal_only") is True,
          "report is not proposal-only", problems)
    qualification = report.get("qualification", {})
    check(qualification == reference.qualification(),
          "report qualification mismatch", problems)
    gates = report.get("release_gates", [])
    check([gate.get("id") for gate in gates] == GATE_IDS,
          "report gate ids mismatch", problems)
    check(len(gates) == 8 and all(
        gate.get("status") == "blocked" and gate.get("reason") and
        gate.get("reopen") for gate in gates),
        "report does not have eight blocked release gates", problems)
    check(report.get("remaining_gates") == GATE_IDS,
          "report remaining gates mismatch", problems)
    artifacts = report.get("required_artifacts", [])
    check(len(artifacts) == 6 and all(
        row.get("status") == "absent" and row.get("rights_reviewed") is False
        for row in artifacts), "report artifacts are not all absent", problems)
    check(report.get("missing_artifacts") ==
          [row.get("artifact") for row in artifacts],
          "report missing artifacts mismatch", problems)
    check(report.get("required_results") ==
          {key: "blocked" for key in report.get("required_results", {})} and
          len(report.get("required_results", {})) == 12,
          "a required result is not blocked", problems)
    check(report.get("profile_mapping", {}).get("candidate_output") ==
          "blocked_source_rights_runtime_models_and_fixtures_absent",
          "candidate output is not blocked", problems)
    score = report.get("local_harness_score", {})
    check(score.get("passed") is True and score.get("failed_checks") == [],
          "local harness score did not pass", problems)
    check(score.get("checks") == len(CHECK_IDS),
          "local harness check count mismatch", problems)
    rows = report.get("local_harness_check_rows", [])
    check(tuple(row.get("id") for row in rows) == CHECK_IDS,
          "local harness check ids mismatch", problems)
    check(all(row.get("passed") is True for row in rows),
          "a local harness check failed", problems)
    check(all(value is True
              for value in report.get("local_harness_checks", {}).values()),
          "a local harness boolean is false", problems)

    adverse = report.get("adverse", {})
    for name in ("invalid_requests", "invalid_json_numeric_fields"):
        block = adverse.get(name, {})
        check(block.get("all_rejected") is True and
              block.get("accepted_count") == 0 and
              block.get("case_count") == len(block.get("cases", [])),
              name + " is not fully rejected", problems)
        for case in block.get("cases", []):
            check(case.get("accepted") is False and
                  case.get("qualifies_candidate") is False,
                  name + " accepted an adverse case", problems)
    missing = adverse.get("missing_result", {})
    check(missing.get("status") == "blocked" and
          missing.get("qualifies_candidate") is False and
          missing.get("metrics") is None,
          "missing result is not blocked", problems)
    check(adverse.get("invalid_requests", {}).get("case_count") == 33 and
          adverse.get("invalid_json_numeric_fields", {}).get("case_count")
          == 7, "adverse case inventory changed", problems)
    blocker = report.get("upstream_blocker", {})
    check(blocker.get("status") ==
          "blocked_source_rights_runtime_models_and_fixtures_absent" and
          blocker.get("license", {}).get("network_use_approved") is False and
          blocker.get("license", {}).get("outbound_compatibility_approved")
          is False and
          blocker.get("license", {}).get("license_text_present") is False and
          blocker.get("pinned_revision") is None,
          "upstream blocker is not a rights blocker", problems)
    check(report.get("board_full_file_hashed") is False,
          "report hashes the full mutable board", problems)

    probe = report.get("harness_probe", {})
    check(probe.get("candidate_processing") is False,
          "harness processed the candidate", problems)
    check(probe.get("not_upstream_essentia") is True,
          "harness is claimed as Essentia", problems)
    check(probe.get("deterministic") is True,
          "harness is not deterministic", problems)
    check(probe.get("qualifies_candidate") is False,
          "harness qualifies the candidate", problems)
    rate = probe.get("rate_profile", {})
    check(rate.get("identity_1x") ==
          {"stimulus": "music_1x", "factor_bpm_x100": "10000"},
          "identity 1x factor mismatch", problems)
    check(rate.get("rate_changes") == [
        {"stimulus": "rate_0_8", "expected_bpm_x100": "8000",
         "observed_bpm_x100": "8000"},
        {"stimulus": "music_1x", "expected_bpm_x100": "10000",
         "observed_bpm_x100": "10000"},
        {"stimulus": "rate_1_2", "expected_bpm_x100": "12000",
         "observed_bpm_x100": "12000"}],
        "rate change factors mismatch", problems)
    check(rate.get("duration", {}).get("max_error_samples") == 0,
          "duration mapping is not exact", problems)
    mapping = rate.get("source_output_mapping", {})
    check(mapping.get("audio_output_produced") is False and
          mapping.get("factor_output_produced") is False and
          mapping.get("analysis_event_source_anchor") is True and
          isinstance(mapping.get("min_availability_margin_ns"), int) and
          mapping.get("min_availability_margin_ns") >= 0,
          "source/output mapping is not a harness mapping", problems)
    check(rate.get("pitch", {}).get("qualifies") is False,
          "pitch is promoted", problems)
    check(rate.get("playback_buffering", {}).get("device_buffer_measured")
          is False, "device buffering is claimed", problems)
    check(rate.get("final_partial_window", {}).get("valid_count") == "137"
          and rate["final_partial_window"].get("event_beyond_source_end")
          is False, "final partial window is invalid", problems)
    check(rate.get("speech_unfamiliar", {}).get("qualifies") is False and
          rate["speech_unfamiliar"].get("status") != "stable",
          "unfamiliar speech is promoted", problems)
    check(rate.get("music", {}).get("status") == "stable" and
          rate.get("silence", {}).get("status") == "no_onsets",
          "music or silence harness outcome mismatch", problems)
    check(rate.get("rebuffer", {}).get("cross_gap_ioi_suppressed") is True,
          "rebuffer gap is not suppressed", problems)
    check(rate.get("drift", {}).get("monotonic_ioi_decrease") is True,
          "drift is not recorded", problems)
    check(rate.get("factor_is_candidate_output") is False,
          "factor is claimed as candidate output", problems)

    candidate = report.get("candidates", {}).get(COMPONENT, {})
    check(candidate.get("qualifies_candidate") is False and
          candidate.get("result") is None and
          candidate.get("metrics") is None,
          "candidate is qualified or has a result", problems)
    for name, control in report.get("controls", {}).items():
        check(control.get("qualifies_candidate") is False,
              "control qualifies the candidate: " + name, problems)
    ref = report.get("reference", {})
    check(ref.get("candidate_processing") is False and
          ref.get("not_upstream_essentia") is True and
          ref.get("upstream_parity") is False and
          ref.get("real_component_source_present") is False and
          ref.get("pinned_runtime_present") is False and
          ref.get("rights_approved") is False and
          ref.get("downloads") is False and ref.get("model_weights") is False,
          "reference claims candidate source, rights or parity", problems)
    for rows_block in (report.get("source_pins", {}),
                       report.get("boundary_pins", {})):
        for name, row in rows_block.items():
            check(row.get("verified") is True and
                  row.get("sha256") == row.get("actual"),
                  "unverified pin in report: " + name, problems)
    payload = REPORT_PATH.read_text(encoding="utf-8")
    for needle in ("/Users/", "/home/"):
        check(needle not in payload,
              "report leaks an absolute local path", problems)


def check_board(contract: Dict[str, Any], report: Dict[str, Any],
                problems: List[str]) -> None:
    board = strict_load(BOARD_PATH)
    check(isinstance(board, dict) and isinstance(board.get("tasks"), list),
          "TASKS.json shape is invalid", problems)
    if not isinstance(board, dict):
        return
    rows = [row for row in board.get("tasks", [])
            if isinstance(row, dict) and row.get("id") == TASK_ID]
    check(len(rows) == 1, "linked task row is missing or duplicated", problems)
    if len(rows) != 1:
        return
    stable = {
        "task_id": rows[0].get("id"),
        "title": rows[0].get("title"),
        "mode": rows[0].get("mode"),
        "repository": rows[0].get("repository"),
        "component": rows[0].get("component"),
    }
    check(stable == EXPECTED_LINK, "stable linked-row identity changed",
          problems)
    expected = sha256_bytes(reference.canonical_bytes([stable]))
    check(report.get("board_links") == [stable],
          "report board projection mismatch", problems)
    check(report.get("board_link_fields") == list(reference.LINK_FIELDS),
          "board link fields mismatch", problems)
    check(report.get("board_link_projection_sha256") == expected,
          "board projection digest mismatch", problems)
    check(contract.get("board_links") == [stable] and
          contract.get("board_link_projection_sha256") == expected,
          "contract board projection mismatch", problems)
    for mutable in ("status", "owner", "review", "handoff", "claim",
                    "history", "blocked_reason", "dispatch_priority",
                    "depends_on", "write_scope"):
        check(mutable in report.get("board_mutable_fields_excluded", []),
              "mutable board field not excluded: " + mutable, problems)
    full_digest = sha256_file(BOARD_PATH)
    blob = (REPORT_PATH.read_text(encoding="utf-8")
            + CONTRACT_PATH.read_text(encoding="utf-8")
            + SOURCES_PATH.read_text(encoding="utf-8"))
    check(full_digest not in blob,
          "full mutable TASKS.json digest appears in a canonical artifact",
          problems)


def check_licensing(problems: List[str]) -> None:
    for name in SIDECAR_FILES:
        path = HERE / name
        check(path.is_file(), "missing SPDX sidecar: " + name, problems)
        if not path.is_file():
            continue
        text = path.read_text(encoding="utf-8")
        check(SPDX_COPYRIGHT in text,
              "sidecar lacks copyright line: " + name, problems)
        check(SPDX_NEEDLE in text,
              "sidecar lacks Apache-2.0 line: " + name, problems)
    for name in ("README.md", "reference.py", "run.py",
                 "test_reference.py", "verify.py"):
        path = HERE / name
        check(path.is_file(), "missing package file: " + name, problems)
        if path.is_file():
            text = path.read_text(encoding="utf-8")
            check(SPDX_NEEDLE in text,
                  "missing SPDX header: " + name, problems)
            check(SPDX_COPYRIGHT in text,
                  "missing SPDX copyright: " + name, problems)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    reuse_token = "SPDX-License-" 'Identifier = "Apache-2.0"'
    check('"docs/**"' in reuse and reuse_token in reuse,
          "REUSE docs coverage is missing", problems)
    for path in HERE.iterdir():
        check(path.suffix.lower() not in PROHIBITED_SUFFIXES or
              path.name.endswith(".sha256"),
              "prohibited binary/audio/model artifact: " + path.name,
              problems)
        check(not path.is_symlink(), "task symlink: " + path.name, problems)
        check(path.name not in {"CMakeLists.txt", "provider.json",
                                "adapter.json"},
              "provider artifact: " + path.name, problems)
        check(not (path.is_file() and path.name.startswith("LICENSE")),
              "vendored license file: " + path.name, problems)


def check_absence_live(problems: List[str]) -> None:
    check(reference.source_probe().get("present") is False,
          "Essentia source appeared; revisit the blocker package", problems)
    check(reference.license_probe().get("license_text_present") is False,
          "a license text appeared; revisit the blocker package", problems)
    check(reference.rights_probe().get("review") == "blocked",
          "rights review is no longer blocked", problems)
    runtime = reference.runtime_probe()
    check(runtime.get("pinned") is False,
          "a pinned runtime appeared; revisit the blocker package", problems)
    check(runtime.get("present") is False,
          "an Essentia runtime appeared; revisit the blocker package",
          problems)
    check(reference.fixture_probe().get("present") is False,
          "a matched fixture appeared; revisit the blocker package", problems)


def check_reuse_lint(problems: List[str]) -> str:
    process = subprocess.run(
        [sys.executable, "-m", "reuse", "lint"], cwd=str(SDK_ROOT),
        capture_output=True, text=True, check=False, timeout=300)
    if process.returncode != 0:
        tail = (process.stdout + process.stderr).strip().splitlines()[-12:]
        problems.append("reuse lint failed: " + " | ".join(tail))
        return "failed"
    return "ok"


def check_reproduction(report_payload: bytes,
                       problems: List[str]) -> bool:
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    process = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--stdout-report"],
        cwd=str(HERE), capture_output=True, env=environment, check=False)
    if process.returncode != 0:
        problems.append("in-process report regeneration failed")
        return False
    check(process.stdout == report_payload, "in-process report bytes differ",
          problems)
    repro = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--verify-repro"],
        cwd=str(HERE), capture_output=True, env=environment, check=False)
    if repro.returncode != 0 or b"ok=1\n" not in repro.stdout:
        problems.append("in-memory bundle reproduction is not ok: " +
                        repro.stdout.decode("utf-8", "replace") +
                        repro.stderr.decode("utf-8", "replace"))
        return False
    return process.stdout == report_payload


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / ("cold-" + str(index))
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-ESSENTIA"
    target = sdk / "docs/task-evidence/essentia"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(WORKSPACE / relative)
    board = scratch / "audioml/audio-benchmark-platform/plan/swarm/TASKS.json"
    board.parent.mkdir(parents=True, exist_ok=True)
    board.symlink_to(BOARD_PATH)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(SDK_ROOT / relative)
    return target


def check_cold_starts(problems: List[str]) -> List[str]:
    committed = (
        REPORT_PATH.read_bytes() if REPORT_PATH.is_file() else b"",
        SIDECAR_PATH.read_bytes() if SIDECAR_PATH.is_file() else b"",
        SOURCES_PATH.read_bytes() if SOURCES_PATH.is_file() else b"",
        CONTRACT_PATH.read_bytes() if CONTRACT_PATH.is_file() else b"",
    )
    if not all(committed):
        problems.append("committed artifacts missing")
        return []
    digests: List[str] = []
    environment = dict(os.environ)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    environment["PYTHONHASHSEED"] = "0"
    with tempfile.TemporaryDirectory(prefix="sdk-essentia-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run(
                [sys.executable, "run.py", "--all"], cwd=target,
                capture_output=True, text=True, env=environment)
            if process.returncode != 0:
                problems.append("cold_start_" + str(index) + "_failed: " +
                                process.stdout.strip() +
                                process.stderr.strip())
                continue
            generated = (
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
                (target / "contract.json").read_bytes(),
            )
            if generated != committed:
                problems.append("cold_start_" + str(index) + "_bytes_differ")
            digests.append(sha256_bytes(generated[0]))
    if len(digests) != 3 or len(set(digests)) != 1:
        problems.append("cold_start_not_byte_identical")
    return digests


def check_git_scope(problems: List[str]) -> List[str]:
    process = subprocess.run(
        ["git", "status", "--porcelain=v1", "--untracked-files=all"],
        cwd=str(SDK_ROOT), capture_output=True, text=True, check=False)
    if process.returncode != 0:
        problems.append("git status failed in the SDK worktree")
        return []
    changed: List[str] = []
    for line in process.stdout.splitlines():
        if not line.strip():
            continue
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        check(path.startswith(TASK_PREFIX),
              "change outside task-local scope: " + path, problems)
    diff = subprocess.run(
        ["git", "diff", "--check"], cwd=str(SDK_ROOT),
        capture_output=True, text=True, check=False)
    check(diff.returncode == 0 and not diff.stdout.strip(),
          "git diff --check failed: " + diff.stdout.strip(), problems)
    allowed = set(run.MANIFEST_FILES) | {"contract.json", "SOURCES.sha256"}
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            check(path.name in allowed, "unpinned task file: " + path.name,
                  problems)
    return changed


def main() -> int:
    problems: List[str] = []
    reuse_status = "not_run"
    try:
        contract = strict_load(CONTRACT_PATH)
        report = strict_load(REPORT_PATH)
        report_payload = REPORT_PATH.read_bytes()
        sidecar_payload = SIDECAR_PATH.read_bytes()
        sources_payload = SOURCES_PATH.read_bytes()
        check(isinstance(contract, dict), "contract root is not an object",
              problems)
        check(isinstance(report, dict), "report root is not an object",
              problems)
        check(reference.finite_json(report),
              "report contains a nonfinite value", problems)
        check(reference.finite_json(contract),
              "contract contains a nonfinite value", problems)
        check(reference.canonical_bytes(report) + b"\n" == report_payload,
              "report bytes are not canonical", problems)
        check(reference.canonical_bytes(contract) + b"\n" ==
              CONTRACT_PATH.read_bytes(), "contract bytes are not canonical",
              problems)
        check(report_payload.endswith(b"\n") and
              not report_payload.endswith(b"\n\n"),
              "report must have exactly one trailing newline", problems)
        check(sidecar_payload ==
              (sha256_bytes(report_payload) + "  report.json\n").encode("ascii"),
              "report sidecar is stale", problems)
        check_profile_source(problems)
        pins = check_pins(report_payload, sidecar_payload, sources_payload,
                          problems)
        check_contract(contract, report, problems)
        check_report(report, problems)
        check_board(contract, report, problems)
        check_licensing(problems)
        check_absence_live(problems)
        reuse_status = check_reuse_lint(problems)
        reproduction_ok = check_reproduction(report_payload, problems)
        digests = check_cold_starts(problems)
        changed = check_git_scope(problems)
    except (OSError, reference.EvidenceError, ValueError, KeyError,
            TypeError) as error:
        problems.append("verification exception: " + str(error))
        reproduction_ok = False
        digests = []
        pins = 0
        changed = []
    digest = (sha256_file(REPORT_PATH) if REPORT_PATH.is_file()
              else "unavailable")
    if problems:
        for problem in problems:
            print("FAIL: " + problem)
        print("verification_failed=" + str(len(problems)) +
              " report_sha256=" + digest)
        return 1
    print("PASS pins=" + str(pins) + " reproduction_ok=" +
          str(int(reproduction_ok)) + " cold_starts=3/3 "
          "byte_identical=true profile=Rate reuse=" + reuse_status +
          " status=proposal_only_not_qualified decision=DEFER "
          "qualification=not_qualified gates_blocked=8 "
          "report_sha256=" + digest + " changed_files=" + str(len(changed)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
