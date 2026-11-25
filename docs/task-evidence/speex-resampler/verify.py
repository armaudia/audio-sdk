# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the task-local Speex resampler evidence package.

Rechecks every SHA-256 pin, strict-loads JSON, regenerates the canonical report
in memory, runs three fresh cold-start probes, checks SPDX/license sidecars and
confirms the git write scope. No file is written and no network, real corpus,
device or listening result is used.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, List

import reference
import run

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
JSON_FILES = ("report.json", "contract.json")
TASK_PREFIX = reference.TASK_PREFIX
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
EXPECTED_GATE_IDS = {gate["id"] for gate in reference.QUALIFICATION_GATES}


class VerifyError(ValueError):
    pass


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_load(path: Path) -> Dict[str, Any]:
    def reject(value: str) -> None:
        raise VerifyError("non-finite JSON constant " + value)

    def unique_keys(items: Iterable[Any]) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise VerifyError("duplicate JSON key " + str(key))
            result[key] = value
        return result

    payload = json.loads(path.read_text(encoding="utf-8"),
                         parse_constant=reject, object_pairs_hook=unique_keys)
    if not isinstance(payload, dict):
        raise VerifyError("root is not an object")
    return payload


def check_pins(errors: List[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    expected_paths: Dict[str, str] = {}
    for path, digest in reference.SOURCE_PINS.items():
        expected_paths["source:" + path] = digest
    for path, digest in reference.BOUNDARY_PINS.items():
        expected_paths[path] = digest
    for path, digest in reference.VENDORED_PINS.items():
        expected_paths[path] = digest
    for name in run.SOURCE_ARTIFACT_NAMES:
        expected_paths[TASK_PREFIX + name] = ""
    parsed: Dict[str, str] = {}
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(line))
            continue
        parsed[parts[1]] = parts[0]
    if set(parsed) != set(expected_paths):
        errors.append("pin path set mismatch")
        return len(lines)
    for path, expected in expected_paths.items():
        actual = parsed[path]
        if expected and actual != expected:
            errors.append("pinned source digest changed: " + path)
        if not expected:
            relative = path.split(TASK_PREFIX, 1)[1]
            candidate = HERE / relative
            if not candidate.is_file():
                errors.append("pinned artifact missing: " + relative)
            elif sha256(candidate.read_bytes()) != actual:
                errors.append("pinned artifact changed: " + relative)
        else:
            root = SOURCE_ROOT if path.startswith("source:") else SDK_ROOT
            candidate = root / (path.split(":", 1)[1] if path.startswith("source:") else path)
            if not candidate.is_file():
                errors.append("pinned file missing: " + path)
            elif sha256(candidate.read_bytes()) != actual:
                errors.append("pinned bytes changed: " + path)
    return len(lines)


def check_json(errors: List[str]) -> int:
    loaded = 0
    for name in JSON_FILES:
        try:
            strict_load(HERE / name)
            loaded += 1
        except (OSError, ValueError) as error:
            errors.append("invalid JSON " + name + ": " + str(error))
    try:
        sidecar = SIDECAR.read_text(encoding="ascii").strip()
        if sidecar != sha256(REPORT.read_bytes()):
            errors.append("report.json.sha256 does not match report.json")
    except (OSError, UnicodeError) as error:
        errors.append("invalid report digest sidecar: " + str(error))
    return loaded


def check_semantics(errors: List[str]) -> None:
    try:
        report = strict_load(REPORT)
        contract = strict_load(HERE / "contract.json")
    except (OSError, ValueError) as error:
        errors.append("semantic load failed: " + str(error))
        return
    if report.get("schema_id") != reference.SCHEMA_ID:
        errors.append("report schema mismatch")
    expected_status = {
        "task": reference.TASK,
        "component": reference.COMPONENT,
        "status": "proposal_only_not_qualified",
        "candidate_status": "proposal_only_not_qualified",
        "qualification_status": "not_qualified",
        "decision": "DEFER",
    }
    for key, expected in expected_status.items():
        if report.get(key) != expected:
            errors.append("report " + key + " mismatch")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing-result gate is disabled")
    qualification = report.get("qualification", {})
    if (qualification.get("status") != "not_qualified"
            or qualification.get("readiness") != "incomplete"
            or qualification.get("decision") != "DEFER"
            or qualification.get("processor_exposure") != "deferred_until_independent_review"):
        errors.append("qualification decision is not DEFER/incomplete/not_qualified")
    if not all(qualification.get("required_results", {}).values()):
        errors.append("a required synthetic result is missing")
    if qualification.get("all_required_results_present") is not True:
        errors.append("all-required-results flag is not true")
    if report.get("fixture_digest") != reference.fixture_digest():
        errors.append("fixture digest is stale")
    pins = report.get("artifact_pins", {})
    if set(pins) != set(reference.ARTIFACT_FILES):
        errors.append("report artifact pin set mismatch")
    for name, digest in pins.items():
        candidate = HERE / name
        if not candidate.is_file() or sha256(candidate.read_bytes()) != digest:
            errors.append("report artifact pin changed: " + name)
    identity = report.get("linked_row_identity", {})
    if identity.get("identity_sha256") != reference.linked_row_identity():
        errors.append("linked-row identity changed")
    if identity.get("gating_basis") != "stable_linked_row_identity_only":
        errors.append("gating is not bound to stable linked-row identity")
    gates = report.get("gates", [])
    if {gate.get("id") for gate in gates} != EXPECTED_GATE_IDS:
        errors.append("qualification gate set mismatch")
    if len(gates) != 8:
        errors.append("expected exactly eight blocked release gates")
    if any(gate.get("status") != "blocked" or not gate.get("reopen")
           or not gate.get("reason") for gate in gates):
        errors.append("a gate is open or has no reason/reopening condition")
    if report.get("remaining_gates") != [gate["id"] for gate in gates]:
        errors.append("remaining gates mismatch")
    if report.get("remaining_gate_count") != 8:
        errors.append("remaining gate count is not eight")
    regressions = report.get("regressions", [])
    if len(regressions) != report.get("regression_count") or not regressions:
        errors.append("regression count mismatch")
    if any(not entry.get("excluded_from_qualification") for entry in regressions):
        errors.append("an adverse regression is not excluded")
    mapped = report.get("profile", {}).get("mapped_cases", {})
    expected_cases = {
        "source_output_mapping", "duration_and_rate_change",
        "pitch_characterization", "transient_audibility_proxy",
        "playback_buffering", "identity_1x", "unfamiliar_speech_proxy",
        "music_negative_control", "silence", "rebuffer", "drift",
        "final_partial_window", "speech_preservation_proxy",
    }
    if set(mapped) != expected_cases or not all(mapped.values()):
        errors.append("rate profile mapped cases incomplete")
    boundary = report.get("boundary", {})
    if (boundary.get("public_api_abi_changed") or boundary.get("registry_changed")
            or boundary.get("descriptor_registration") or boundary.get("enabled_by_default")
            or boundary.get("provider_registered") or not boundary.get("opt_in_required")
            or not boundary.get("installed_v0_unchanged")
            or boundary.get("shared_cmake_changed") or boundary.get("ci_changed")
            or boundary.get("real_corpus_or_weights")):
        errors.append("public boundary invariant violated")
    fmt = boundary.get("format", {})
    if fmt != {"sample_rate_hz": reference.SAMPLE_RATE_HZ, "channels": 1,
               "sample_format": "float32", "frame_samples": reference.FRAME_SAMPLES}:
        errors.append("installed format mismatch")
    rate_cases = report.get("rate_cases", {})
    if set(rate_cases) != {case["label"] for case in reference.SPEED_CASES}:
        errors.append("rate case set mismatch")
    for label, case in rate_cases.items():
        if not case.get("duration_exact"):
            errors.append("a duration case is not exact: " + label)
        if not case.get("consumed_all_input"):
            errors.append("a case did not consume all input: " + label)
        if case.get("expected_output_samples") != case.get("observed_output_samples"):
            errors.append("expected/observed output length mismatch: " + label)
        if case.get("transient_max_abs_residual_samples") != 0:
            errors.append("source/output anchor residual is nonzero: " + label)
        proxy = case.get("speech_preservation_proxy", {})
        if not proxy.get("contrast_preserved"):
            errors.append("speech pause contrast was not preserved: " + label)
    pitch = report.get("pitch", {})
    if pitch.get("identity_1x", {}).get("ratio") != 1.0:
        errors.append("identity pitch proxy is not 1.0")
    adverse = pitch.get("varispeed_adverse_control", {})
    ratio = adverse.get("ratio")
    if ratio is None or abs(ratio - 1.0) < 0.10:
        errors.append("varispeed adverse control did not shift pitch")
    for case in reference.SPEED_CASES:
        label = case["label"]
        speed = float(case["num"]) / int(case["den"])
        observed = pitch.get("cases", {}).get(label, {}).get("ratio")
        if observed is None or abs(observed - speed) > 0.03:
            errors.append("pitch ratio is not the declared speed: " + label)
    for label, case in report.get("silence", {}).items():
        if case.get("peak_abs") != 0.0 or case.get("nonfinite_count") != 0:
            errors.append("silence control produced energy: " + label)
    drift = report.get("drift_and_rebuffer", {}).get("drift", {})
    if drift.get("observed_output_samples") != drift.get("expected_output_samples"):
        errors.append("drift duration is not exact")
    if drift.get("anchors", {}).get("max_abs_residual_samples") != 0:
        errors.append("drift anchor mapping is not exact")
    fifo = report.get("drift_and_rebuffer", {}).get("rebuffer", {}).get(
        "synthetic_fifo", {})
    if not fifo.get("stall_refill_resume_observed") \
            or fifo.get("played_samples") != fifo.get("expected_output_samples"):
        errors.append("synthetic rebuffer was not exercised and drained")
    partial = report.get("final_partial_window", {})
    if not partial.get("exact") \
            or partial.get("observed_output_samples") != partial.get("expected_output_samples"):
        errors.append("final partial window is not exact")
    if not report.get("crosscheck", {}).get("byte_identical"):
        errors.append("in-process renderer crosscheck failed")
    adverse_controls = report.get("adverse", {})
    for name in ("nonfinite_input", "out_of_range_speed_low",
                 "out_of_range_speed_high", "invalid_quality",
                 "missing_result"):
        entry = adverse_controls.get(name, {})
        if entry.get("status") != "rejected" or entry.get("metrics") is not None:
            errors.append("failure control did not fail closed: " + name)
    if adverse_controls.get("nonfinite_output_guard", {}).get("status") != "checked":
        errors.append("nonfinite output guard is not present")
    statements = " ".join(report.get("source_evidence_statements", []))
    if "provenance only" not in statements:
        errors.append("source context is not marked provenance-only")
    if contract.get("task") != reference.TASK or contract.get("decision") != "DEFER":
        errors.append("contract task or decision mismatch")
    if contract.get("qualification_status") != "not_qualified":
        errors.append("contract qualification status mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract source pins mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract boundary pins mismatch")
    if contract.get("vendored_pins") != reference.VENDORED_PINS:
        errors.append("contract vendored pins mismatch")
    if contract.get("linked_row_identity") != report.get("linked_row_identity"):
        errors.append("contract linked-row identity mismatch")
    canonical = contract.get("canonical_report", {})
    if canonical.get("file_sha256") != sha256(REPORT.read_bytes()):
        errors.append("contract report file digest is stale")
    if contract.get("remaining_gates") != report.get("remaining_gates"):
        errors.append("contract remaining gates mismatch")


def check_reproduction(errors: List[str]) -> str:
    regenerated = reference.canonical_report(reference.build_report())[0].encode(
        "utf-8") + b"\n"
    actual = REPORT.read_bytes()
    if regenerated != actual:
        errors.append("report.json is not byte-reproducible")
    if not regenerated.endswith(b"\n"):
        errors.append("canonical report has no trailing newline")
    probe = reference.repeat_probe()
    if not probe["byte_identical"] or probe["runs"] != 3:
        errors.append("three cold-start probes are not byte-identical")
    return sha256(actual)


def check_licensing(errors: List[str]) -> int:
    checked = 0
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append("missing SPDX header: " + path.name)
        checked += 1
    harness = "\n".join((HERE / "harness.c").read_text(encoding="utf-8").splitlines()[:3])
    if SPDX_LICENSE_LINE not in harness or SPDX_COPYRIGHT_LINE not in harness:
        errors.append("missing SPDX header: harness.c")
    checked += 1
    notices = (HERE / "THIRD_PARTY_NOTICES.md").read_text(encoding="utf-8")
    if "SpeexDSP" not in notices or "BSD-3-Clause" not in notices:
        errors.append("third-party notice does not record SpeexDSP BSD-3-Clause")
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX' '-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    for name in ("Apache-2.0.txt", "BSD-3-Clause.txt"):
        if not (SDK_ROOT / "LICENSES" / name).is_file():
            errors.append("LICENSES/" + name + " is missing")
    return checked


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"], capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        checked = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                                 capture_output=True, text=True)
        if checked.returncode != 0:
            errors.append("git " + " ".join(arguments) + " failed: "
                          + checked.stdout.strip())
    return changed


def main() -> int:
    errors: List[str] = []
    pin_count = check_pins(errors)
    json_count = check_json(errors)
    check_semantics(errors)
    report_digest = check_reproduction(errors)
    licensing_count = check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok={json_count} reproduction_ok=1 "
          f"repeats_ok=3 licensing_ok={licensing_count} scope_ok=1 "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
