# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verification of the task-local libsamplerate evidence package.

Rechecks every SHA-256 pin, strict-loads every JSON artifact, regenerates the
canonical report in memory for an exact byte comparison, runs three cold-start
probes, checks SPDX headers and confirms the git write scope. No file is
written and no network, upstream source, real corpus, device or listening
result is used.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, Iterable, List

import fixture
import reference
import run

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(fixture.SOURCE_ROOT)))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
JSON_FILES = ("report.json", "contract.json", "adapter.json", "provider.json")
TASK_PREFIX = reference.TASK_PREFIX
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
REUSE_ANNOTATION = '"docs/**"'
REUSE_LICENSE = "SPDX" "-License-Identifier = \"Apache-2.0\""
EXPECTED_GATE_IDS = {"RG-0" + str(index) for index in range(1, 9)}
EXPECTED_MAPPED_CASES = {
    "source_output_mapping", "duration_and_rate_change", "pitch_preservation_proxy",
    "transient_audibility_proxy", "playback_buffering", "unfamiliar_synthetic_speech",
    "synthetic_music_negative_control", "silence", "rebuffer", "drift",
    "final_partial_window", "speech_preservation_proxy",
}


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
    for name in sorted(set(run.SOURCE_ARTIFACT_NAMES) | {"contract.json"}):
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
            relative = path.split(TASK_PREFIX, 1)[1] if path.startswith(TASK_PREFIX) else path
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


def _projection(rows: List[Dict[str, Any]]) -> str:
    projection = [
        {"task_id": row.get("task_id"), "title": row.get("title"),
         "mode": row.get("mode")}
        for row in rows
    ]
    return sha256(json.dumps(projection, sort_keys=True,
                             separators=(",", ":")).encode("utf-8"))


def check_semantics(errors: List[str]) -> None:
    try:
        report = strict_load(REPORT)
        contract = strict_load(HERE / "contract.json")
        adapter = strict_load(HERE / "adapter.json")
        provider = strict_load(HERE / "provider.json")
    except (OSError, ValueError) as error:
        errors.append("semantic load failed: " + str(error))
        return
    if report.get("schema_id") != reference.SCHEMA_ID:
        errors.append("report schema mismatch")
    for key, expected in (
            ("task", reference.TASK),
            ("status", "proposal_only_not_qualified"),
            ("candidate_status", "proposal_only_not_qualified"),
            ("qualification_status", "not_qualified"),
            ("decision", "DEFER")):
        if report.get(key) != expected:
            errors.append("report " + key + " mismatch")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        errors.append("missing-result gate is disabled")
    blocker = report.get("upstream_blocker", {})
    if blocker.get("status") != "blocked_upstream_absent":
        errors.append("upstream blocker status mismatch")
    if blocker.get("pinned_revision") is not None or blocker.get("source_digest") is not None:
        errors.append("upstream blocker claims a revision or digest")
    if blocker.get("expected_license") != "BSD-2-Clause":
        errors.append("upstream license expectation mismatch")
    if blocker.get("no_upstream_parity_claim") is not True \
            or len(blocker.get("not_attempted", [])) != 3 \
            or not blocker.get("rights_requirement") or not blocker.get("reopen"):
        errors.append("upstream blocker is incomplete")
    if not blocker.get("workspace_search") or not blocker.get("required_files"):
        errors.append("upstream blocker has no search or required-file record")
    qualification = report.get("qualification", {})
    if (qualification.get("status") != "not_qualified"
            or qualification.get("readiness") != "incomplete"
            or qualification.get("decision") != "DEFER"
            or qualification.get("upstream_parity") is not False
            or qualification.get("candidate_qualified") is not False
            or qualification.get("processor_exposure") != "deferred_until_independent_review"):
        errors.append("qualification decision is not DEFER/incomplete/not_qualified")
    required = report.get("required_results", {})
    if not required or not all(required.values()):
        errors.append("a required synthetic result is missing")
    if report.get("fixture_digest") != reference.fixture_digest():
        errors.append("fixture digest is stale")
    if set(report.get("artifact_pins", {})) != set(reference.ARTIFACT_FILES):
        errors.append("report artifact pin set mismatch")
    for name, digest in report.get("artifact_pins", {}).items():
        candidate = HERE / name
        if not candidate.is_file() or sha256(candidate.read_bytes()) != digest:
            errors.append("report artifact pin changed: " + name)
    gates = report.get("gates", [])
    if {gate.get("id") for gate in gates} != EXPECTED_GATE_IDS:
        errors.append("release gate set mismatch")
    if len(gates) != 8:
        errors.append("release gate count is not eight")
    if any(gate.get("status") != "blocked" or not gate.get("reason")
           or not gate.get("reopen") for gate in gates):
        errors.append("a release gate is open or has no reason/reopening condition")
    if report.get("remaining_gates") != [gate["id"] for gate in gates]:
        errors.append("remaining gates mismatch")
    regressions = report.get("regressions", [])
    if len(regressions) != report.get("regression_count") or not regressions:
        errors.append("regression count mismatch")
    if any(not entry.get("excluded_from_qualification") for entry in regressions):
        errors.append("an adverse regression is not excluded")
    mapped = report.get("profile", {}).get("mapped_cases", {})
    if set(mapped) != EXPECTED_MAPPED_CASES or not all(mapped.values()):
        errors.append("rate profile mapped cases incomplete")
    if report.get("profile", {}).get("name") != "rate":
        errors.append("profile is not the rate profile")
    boundary = report.get("boundary", {})
    if (boundary.get("public_api_abi_changed") or boundary.get("registry_changed")
            or boundary.get("descriptor_registration") or boundary.get("enabled_by_default")
            or boundary.get("provider_registered")
            or boundary.get("provider_intake_complete")
            or boundary.get("release_claim") or boundary.get("benchmark_claim")
            or not boundary.get("opt_in_required")
            or not boundary.get("installed_v0_unchanged")):
        errors.append("public boundary invariant violated")
    fmt = boundary.get("format", {})
    if fmt != {"sample_rate_hz": reference.SAMPLE_RATE_HZ, "channels": 1,
               "sample_format": "float32", "frame_samples": reference.FRAME_SAMPLES}:
        errors.append("installed format mismatch")
    for name, case in report.get("rate_cases", {}).items():
        if not case["duration"]["exact"]:
            errors.append("a duration case is not exact: " + name)
        if not case["map_monotonic"] or not case["source_interval_union_covers_all"]:
            errors.append("a source map is not monotonic or does not cover the source")
        if case["nonfinite_count"] != 0:
            errors.append("a rate case produced nonfinite output: " + name)
        if name.endswith("@1.0") and not case["identity_fast_path"]:
            errors.append("the 1x case did not use the identity fast path")
    if report.get("src_pitch", {}).get("identity_1x", {}).get("ratio") != 1.0:
        errors.append("identity pitch proxy is not 1.0")
    for key in ("interpolate_2x", "decimate_0_5x"):
        value = report.get("src_pitch", {}).get(key, {}).get("ratio")
        if value is None or abs(value - 1.0) > 0.02:
            errors.append("sample-rate conversion did not preserve the tone proxy: " + key)
    alias = report.get("alias_suppression", {})
    image = report.get("image_rejection", {})
    if not alias.get("filtered_suppression_db", 0.0) < \
            alias.get("naive_suppression_db", 0.0) - 20.0:
        errors.append("anti-alias suppression is not better than the naive control")
    if not image.get("filtered_suppression_db", 0.0) < \
            image.get("naive_suppression_db", 0.0) - 20.0:
        errors.append("image rejection is not better than the naive control")
    for key, target in (("interpolate_2_0_played_at_input_rate", 0.5),
                        ("decimate_0_5_played_at_input_rate", 2.0)):
        value = report.get("playback", {}).get("varispeed_pitch", {}).get(key, {}).get("ratio")
        if value is None or abs(value - target) > 0.05:
            errors.append("varispeed adverse control did not shift pitch: " + key)
    reference_block = report.get("reference", {})
    if reference_block.get("real_libsamplerate_source_or_binary") is not False \
            or reference_block.get("upstream_parity") is not False:
        errors.append("reference claims upstream presence or parity")
    if reference_block.get("buffering_delay_samples") != 0:
        errors.append("reference introduces an undeclared buffering delay")
    pacing = report.get("drift_and_rebuffer", {}).get("pacing", {})
    if not pacing.get("rebuffer", {}).get("stall_refill_resume_observed"):
        errors.append("synthetic rebuffer interruption was not exercised")
    drift = report.get("drift_and_rebuffer", {}).get("drift", {})
    if not drift.get("single_pass_1_03", {}).get("duration_exact") \
            or not drift.get("second_segment_1_03", {}).get("duration_exact"):
        errors.append("a drift segment is not duration-exact")
    if drift.get("naive_float_accumulator", {}).get("max_position_error_samples") == 0:
        errors.append("the naive float accumulator control shows no drift")
    if not report.get("final_partial_window", {}).get("output_samples"):
        errors.append("final partial window is missing")
    if report.get("final_partial_window", {}).get("target_samples") != \
            report.get("final_partial_window", {}).get("output_samples"):
        errors.append("final partial window duration is not exact")
    for case in report.get("transient_proxies", {}).values():
        if any(event.get("expected_output_sample") is None
               or event.get("peak_ratio") is None
               for event in case.get("events", [])):
            errors.append("transient score is missing its source-to-output index")
    if not report.get("crosscheck", {}).get("byte_identical"):
        errors.append("renderer crosscheck failed")
    adverse = report.get("adverse", {})
    if adverse.get("nonfinite_input", {}).get("metrics") is not None \
            or adverse.get("out_of_range_input", {}).get("metrics") is not None \
            or adverse.get("missing_result", {}).get("metrics") is not None:
        errors.append("a failure control produced metrics")
    if not adverse.get("invalid_config", {}).get("cases"):
        errors.append("no invalid-configuration cases are recorded")
    links = report.get("board_links", [])
    if _projection(links) != report.get("board_link_projection_sha256"):
        errors.append("board link identity projection mismatch")
    if any(set(row) != {"task_id", "title", "mode"} for row in links):
        errors.append("a board link carries mutable board state")
    if report.get("board_snapshot", {}).get("mutable") is not True:
        errors.append("board snapshot is not marked mutable")
    statements = " ".join(report.get("source_evidence_statements", []))
    if "context only" not in statements:
        errors.append("pinned sources are not declared context only")
    if contract.get("task") != reference.TASK or contract.get("decision") != "DEFER":
        errors.append("contract task or decision mismatch")
    if contract.get("status") != "proposal_only_not_qualified":
        errors.append("contract status mismatch")
    if contract.get("source_pins") != reference.SOURCE_PINS:
        errors.append("contract source pins mismatch")
    if contract.get("boundary_pins") != reference.BOUNDARY_PINS:
        errors.append("contract boundary pins mismatch")
    if contract.get("upstream_blocker") != blocker:
        errors.append("contract upstream blocker mismatch")
    if contract.get("board_link_projection_sha256") != report.get(
            "board_link_projection_sha256"):
        errors.append("contract board projection mismatch")
    if len(contract.get("release_gates", [])) != 8:
        errors.append("contract does not carry eight release gates")
    canonical = contract.get("canonical_report", {})
    if canonical.get("file_sha256") != sha256(REPORT.read_bytes()):
        errors.append("contract report file digest is stale")
    for name, digest in contract.get("artifact_pins", {}).items():
        candidate = HERE / name
        if not candidate.is_file() or sha256(candidate.read_bytes()) != digest:
            errors.append("contract artifact pin changed: " + name)
    if adapter.get("registered") is not False or adapter.get("default_enabled") is not False \
            or adapter.get("real_time_v0_provider") is not False \
            or adapter.get("upstream_libsamplerate_used") is not False:
        errors.append("adapter manifest is not unregistered and default-OFF")
    if adapter.get("adapter_id") != reference.ADAPTER_ID:
        errors.append("adapter identity mismatch")
    if provider.get("registered") is not False or provider.get("enabled_by_default") is not False \
            or provider.get("opt_in_required") is not True:
        errors.append("provider manifest is not opt-in, disabled and unregistered")
    if (provider.get("public_abi_change") or provider.get("sdk_default_change")
            or provider.get("installed_v0_behavior_change")
            or provider.get("upstream_source_present") or provider.get("upstream_parity")
            or provider.get("descriptor_registration")):
        errors.append("provider manifest claims a public or upstream change")
    if provider.get("required_assets") != []:
        errors.append("provider manifest requires assets it does not have")


def check_reproduction(errors: List[str]) -> str:
    regenerated = fixture.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    if regenerated != actual:
        errors.append("report.json is not byte-reproducible")
    if not regenerated.endswith(b"\n"):
        errors.append("canonical report has no trailing newline")
    repeats = fixture.repeat_probe()
    if not repeats["byte_identical"] or repeats["runs"] != 3:
        errors.append("three cold-start probes are not byte-identical")
    return sha256(actual)


def check_licensing(errors: List[str]) -> int:
    checked = 0
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append("missing SPDX header: " + path.name)
        checked += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if REUSE_ANNOTATION not in reuse or REUSE_LICENSE not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        errors.append("LICENSES/Apache-2.0.txt is missing")
    if (HERE / "LICENSES" / "BSD-2-Clause-upstream-absent.txt").exists():
        errors.append("a fabricated upstream license sidecar is present")
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
            errors.append("git " + " ".join(arguments) + " failed: " + checked.stdout.strip())
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
    print(f"pins_ok={pin_count} json_ok={json_count} reproduction_ok=1 repeats_ok=3 "
          f"licensing_ok={licensing_count} scope_ok=1 "
          f"report_sha256={report_digest} changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
