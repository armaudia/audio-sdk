# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the task-local SDK-AUBIO evidence package.

The original directory is never written. Regeneration is performed in three
independent scratch trees with fresh interpreter processes and symlinks to the
pinned, read-only source and boundary files.
"""

from __future__ import annotations

import hashlib
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

SDK_ROOT = HERE.parents[2]
CONTRACT = HERE / "contract.json"
FIXTURES = HERE / "fixtures.json"
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
VERIFICATION = (reference.AUDIO_ROOT
                / "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
SPDX_LICENSE = "SPDX-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "fixtures.json.license",
    "report.json.license",
    "report.json.sha256.license",
)
FORBIDDEN_SUFFIXES = {
    ".a", ".bin", ".dll", ".dylib", ".exe", ".flac", ".model", ".mp3",
    ".o", ".ogg", ".onnx", ".pt", ".pth", ".pyc", ".so", ".wasm", ".wav",
    ".weights",
}
PROFILE_PHRASES = (
    "Measure source/output mapping, duration, pitch, transient audibility "
    "and playback buffering.",
    "Include 1×, rate changes, unfamiliar speech, music, silence, rebuffer, "
    "drift and the final partial window.",
    "Keep pause or filler decisions tied to source timestamps and measure "
    "speech preservation.",
)
EXPECTED_CHECK_IDS = (
    "identity_1x_bpm", "rate_0_8_bpm", "rate_1_2_bpm", "rate_duration_error",
    "speech_no_stable_tempo", "silence_no_onsets", "music_stable",
    "tempo_out_of_range", "low_snr_adverse_nonqualifying",
    "rebuffer_gap_suppressed", "drift_recorded", "final_partial_valid",
    "mapping_nonnegative", "transient_proxy", "all_cases_explicit",
    "all_gates_blocked",
)
REQUIRED_ADVERSE_IDS = {
    "MISS-01", "INV-01", "INV-02", "INV-03", "INV-04", "INV-05", "INV-06",
    "INV-07", "CFG-01", "CFG-02", "CFG-03", "CFG-04",
    "ADV-low_snr_adverse", "ADV-tempo_out_of_range_adverse",
    "ADV-speech_like_unfamiliar", "ADV-silence", "ADV-drift", "ADV-rebuffer",
}
ACCEPTANCE_KEYS = {
    "profile", "source_output_mapping", "duration", "pitch", "transient",
    "playback_buffering", "rate_1x", "rate_changes", "unfamiliar_speech",
    "music", "silence", "rebuffer", "drift", "final_partial_window",
}


def strict_json(path: Path) -> dict:
    """Read a strict JSON object; reject duplicate keys and nonfinite values."""
    return reference.read_strict_json(path)


def check_profile_source(errors: list[str]) -> None:
    expected = reference.SOURCE_PINS.get(
        "audio-benchmark-platform/plan/swarm/VERIFICATION.md")
    if not VERIFICATION.is_file():
        errors.append("verification_source_missing")
        return
    actual = reference.sha256_file(VERIFICATION)
    if actual != expected:
        errors.append("verification_source_unpinned")
    text = VERIFICATION.read_text(encoding="utf-8")
    rate_rows = [line for line in text.splitlines() if line.startswith("| Rate |")]
    if len(rate_rows) != 1:
        errors.append("rate_profile_row_not_unique")
        return
    for phrase in PROFILE_PHRASES:
        if phrase not in rate_rows[0]:
            errors.append("rate_profile_phrase_missing:" + phrase[:32])


def check_pins(errors: list[str]) -> int:
    if not PINS.is_file():
        errors.append("SOURCES.sha256 missing")
        return 0
    expected: dict[str, str | None] = {}
    for relative, digest in sorted(reference.SOURCE_PINS.items()):
        expected["source:" + relative] = digest
    for relative, digest in sorted(reference.BOUNDARY_PINS.items()):
        expected[relative] = digest
    for name in run.LOCAL_PIN_FILES:
        expected[run.TASK_PREFIX + name] = None
    seen: set[str] = set()
    count = 0
    for line in PINS.read_text(encoding="ascii").splitlines():
        if not line or line.startswith("#"):
            continue
        count += 1
        parts = line.split("  ", 1)
        if (len(parts) != 2 or len(parts[0]) != 64
                or any(char not in "0123456789abcdef" for char in parts[0])):
            errors.append("malformed_pin:" + repr(line))
            continue
        digest, name = parts
        if name not in expected:
            errors.append("unexpected_pin:" + name)
            continue
        if name in seen:
            errors.append("duplicate_pin:" + name)
            continue
        seen.add(name)
        if expected[name] is not None and expected[name] != digest:
            errors.append("pinned_digest_mismatch:" + name)
        if name.startswith("source:"):
            path = reference.AUDIO_ROOT / name.split(":", 1)[1]
        else:
            path = SDK_ROOT / name
        if not path.is_file():
            errors.append("pin_target_missing:" + name)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned_bytes_changed:" + name)
    for name in sorted(set(expected) - seen):
        errors.append("pin_absent:" + name)
    if PINS.read_bytes() != run.sources_bytes():
        errors.append("manifest_not_deterministically_generated")
    return count


def check_report(errors: list[str]) -> dict:
    try:
        report = strict_json(REPORT)
        contract = strict_json(CONTRACT)
        fixtures = strict_json(FIXTURES)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict_json_failed:" + str(error))
        return {}
    try:
        reference.validate_contract(contract)
        reference.validate_fixtures(fixtures)
        generated = reference.canonical_report(reference.build_report())[0].encode("utf-8")
    except (OSError, ValueError, TypeError) as error:
        errors.append("reference_build_failed:" + str(error))
        return report
    payload = REPORT.read_bytes()
    if payload != generated:
        errors.append("report_not_regenerated_bytes")
    if payload != reference.canonical_report(report)[0].encode("utf-8"):
        errors.append("report_not_canonical_bytes")
    digest = hashlib.sha256(payload).hexdigest()
    if not SIDECAR.is_file() or SIDECAR.read_bytes() != (
            f"{digest}  report.json\n".encode("ascii")):
        errors.append("report_digest_sidecar_stale")
    if report["contract_sha256"] != reference.object_digest(contract):
        errors.append("contract_digest_mismatch")
    if report["fixtures_sha256"] != reference.object_digest(fixtures):
        errors.append("fixtures_digest_mismatch")

    if report["protocol"] != reference.CONTRACT_ID or report["task"] != reference.TASK:
        errors.append("report_identity_mismatch")
    if report["verification_profile"] != "Rate" or contract["verification_profile"] != "Rate":
        errors.append("rate_profile_not_applied")
    if report["status"] != "proposal_only_not_qualified":
        errors.append("proposal_status_mismatch")
    for key in ("decision", "exact_scope", "installed_v0"):
        if report[key] != contract[key]:
            errors.append("contract_copy_mismatch:" + key)
    decision = report["decision"]
    if (decision["status"] != "incomplete" or decision["promotion"] != "defer"
            or decision["production_exposure"] != "DEFER"
            or decision["incomplete"] is not True
            or decision["proposal_only_not_qualified"] is not True
            or any(decision[key] is not False for key in
                   ("expose_as_processor", "registered", "default_enabled"))):
        errors.append("disposition_not_defer_incomplete")
    scope = report["exact_scope"]
    if any(scope[key] is not False for key in scope if key != "write_scope"):
        errors.append("scope_claim_not_false")
    if scope["write_scope"] != "docs/task-evidence/aubio/ only":
        errors.append("write_scope_mismatch")
    licensing = report["licensing"]
    if (licensing["reported_upstream_license"] != "GPL-3.0"
            or licensing["review"] != "blocked"
            or licensing["task_file_spdx"] != "Apache-2.0"
            or any(licensing[key] is not False for key in
                   ("upstream_source_present", "upstream_runtime_present",
                    "relicensed", "proprietary_release_permitted",
                    "vendored_license_file"))):
        errors.append("licensing_disposition_mismatch")
    expected_source = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.SOURCE_PINS.items()}
    expected_boundary = {
        path: {"sha256": digest, "actual": digest, "verified": True}
        for path, digest in reference.BOUNDARY_PINS.items()}
    if report["source_pins"] != expected_source:
        errors.append("report_source_pins_mismatch")
    if report["boundary_pins"] != expected_boundary:
        errors.append("report_boundary_pins_mismatch")
    for rows in (report["source_pins"], report["boundary_pins"]):
        if any(row["verified"] is not True or row["sha256"] != row["actual"]
               for row in rows.values()):
            errors.append("unverified_pin_in_report")

    scoring = report["profile_scoring"]
    if tuple(row["id"] for row in scoring["checks"]) != EXPECTED_CHECK_IDS:
        errors.append("profile_check_ids_mismatch")
    if (scoring["passed"] is not True or scoring["failed_checks"]
            or any(row["passed"] is not True for row in scoring["checks"])):
        errors.append("profile_scoring_not_passed")
    if scoring["scope"] != "synthetic fixture only; not release qualification":
        errors.append("profile_scope_not_synthetic")
    qualification = report["qualification"]
    if (qualification["synthetic_profile_checks_passed"] is not True
            or qualification["all_release_gates_blocked"] is not True
            or any(qualification[key] is not False for key in
                   ("release_results_present", "missing_result_promoted",
                    "real_source_or_runtime_used", "listening_or_device_timing_claim"))):
        errors.append("qualification_not_blocked")
    if len(report["blockers"]) != 7 or any(
            gate["status"] != "blocked" or gate["qualifies"] is not False
            or not gate["reopen_condition"] for gate in report["blockers"]):
        errors.append("release_gates_not_blocked")
    if report["remaining_gates"] != contract["remaining_gates"]:
        errors.append("remaining_gates_mismatch")

    acceptance = report["acceptance_profile"]
    if acceptance["profile"] != "Rate" or set(acceptance) != ACCEPTANCE_KEYS:
        errors.append("acceptance_profile_not_rate")
    if any(not isinstance(value, str) or not value for value in acceptance.values()):
        errors.append("acceptance_profile_entry_empty")

    rate = report["rate_profile"]
    if rate["identity_1x"] != {"stimulus": "music_like_1x", "bpm_x100": "10000"}:
        errors.append("identity_rate_wrong")
    if rate["rate_changes"] != [
            {"stimulus": "rate_0_8", "expected_bpm_x100": "8000",
             "observed_bpm_x100": "8000"},
            {"stimulus": "music_like_1x", "expected_bpm_x100": "10000",
             "observed_bpm_x100": "10000"},
            {"stimulus": "rate_1_2", "expected_bpm_x100": "12000",
             "observed_bpm_x100": "12000"}]:
        errors.append("rate_changes_wrong")
    if rate["duration"]["max_error_samples"] != 0 or any(
            row["error_samples"] != "0" for row in rate["duration"]["cases"].values()):
        errors.append("duration_mapping_not_exact")
    mapping = rate["source_output_mapping"]
    if (mapping["audio_output_produced"] is not False
            or mapping["analysis_event_source_anchor"] is not True
            or mapping["frame_hop_samples"] != "160"
            or mapping["available_ns_per_frame"] != "10000000"
            or not isinstance(mapping["min_availability_margin_ns"], int)
            or mapping["min_availability_margin_ns"] < 0):
        errors.append("source_output_mapping_invalid")
    if (rate["pitch"]["status"] != "not_measurable_analysis_only"
            or rate["pitch"]["qualifies"] is not False):
        errors.append("pitch_not_left_unmeasured")
    if rate["transient_proxy"]["final_partial_error_samples"] != -50:
        errors.append("transient_proxy_wrong")
    buffering = rate["playback_buffering"]
    if (buffering["device_buffer_measured"] is not False
            or buffering["sdk_worker_count"] != "0"
            or buffering["sdk_queue_depth"] != "0"
            or buffering["analysis_frame_aggregation_samples"] != "160"
            or buffering["final_partial_valid_count"] != "137"
            or buffering["final_padding_zero_verified"] is not True):
        errors.append("playback_buffering_claim_invalid")
    if (rate["speech_unfamiliar"]["status"] == "stable"
            or rate["speech_unfamiliar"]["qualifies"] is not False):
        errors.append("unfamiliar_speech_promoted")
    if (rate["music"]["status"] != "stable" or rate["music"]["bpm_x100"] != "10000"
            or rate["silence"]["status"] != "no_onsets"):
        errors.append("music_or_silence_wrong")
    if (rate["rebuffer"]["excluded_ioi_count"] != "1"
            or rate["rebuffer"]["cross_gap_ioi_suppressed"] is not True):
        errors.append("rebuffer_gap_not_suppressed")
    if rate["drift"]["monotonic_ioi_decrease"] is not True:
        errors.append("drift_not_recorded")
    final = rate["final_partial_window"]
    if (final["valid_count"] != "137" or final["event_source_end"] != "64137"
            or final["event_beyond_source_end"] is not False
            or len(final["event_digest"]) != 64):
        errors.append("final_partial_window_invalid")
    if rate["low_snr_adverse"]["qualifies"] is not False:
        errors.append("low_snr_adverse_promoted")

    try:
        adverse = reference._adverse_cases(fixtures)
    except (ValueError, TypeError) as error:
        errors.append("adverse_cases_not_reproduced:" + str(error))
        adverse = []
    if adverse != report["adverse_cases"]:
        errors.append("adverse_cases_mismatch")
    ids = {case["id"] for case in report["adverse_cases"]}
    if not REQUIRED_ADVERSE_IDS <= ids:
        errors.append("adverse_ids_missing:" + ",".join(sorted(REQUIRED_ADVERSE_IDS - ids)))
    for case in report["adverse_cases"]:
        if case["qualifies"] is not False or case["status"] not in ("rejected", "recorded"):
            errors.append("adverse_case_qualifies:" + case["id"])
        if case["status"] == "rejected" and (
                case["state_unchanged"] is not True or case["onset_count"] != "0"
                or not case["code"]):
            errors.append("rejection_advanced_state:" + case["id"])
    return report


def check_licensing(errors: list[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing_python_spdx:" + path.name)
    for name in SIDECARS:
        text = (HERE / name).read_text(encoding="utf-8") if (HERE / name).is_file() else ""
        if SPDX_LICENSE not in text or SPDX_COPYRIGHT not in text:
            errors.append("missing_license_sidecar:" + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("reuse_docs_coverage_missing")
    for path in sorted(HERE.iterdir()):
        if path.suffix.lower() in FORBIDDEN_SUFFIXES:
            errors.append("forbidden_artifact:" + path.name)
        if path.is_symlink():
            errors.append("task_symlink:" + path.name)
        if path.name in {"CMakeLists.txt", "provider.json", "adapter.json"}:
            errors.append("provider_artifact:" + path.name)
        if path.is_file() and path.name.startswith("LICENSE"):
            errors.append("vendored_license_file:" + path.name)


def check_scope(errors: list[str]) -> list[str]:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True)
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
    diff = subprocess.run(["git", "-C", str(SDK_ROOT), "diff", "--check"],
                          capture_output=True, text=True)
    if diff.returncode != 0 or diff.stdout.strip():
        errors.append("git_diff_check_failed:" + diff.stdout.strip())
    allowed = {name for name in run.LOCAL_PIN_FILES}
    allowed.add("SOURCES.sha256")
    for path in sorted(HERE.iterdir()):
        if path.is_file() and path.name not in allowed:
            errors.append("unpinned_task_file:" + path.name)
    return changed


def _prepare_scratch(root: Path, index: int) -> Path:
    scratch = root / f"cold-{index}"
    sdk = scratch / "audioml/worktrees/audio-sdk/SDK-AUBIO"
    target = sdk / "docs/task-evidence/aubio"
    target.mkdir(parents=True)
    for path in sorted(HERE.iterdir()):
        if path.is_file():
            shutil.copyfile(path, target / path.name)
    for relative in sorted(reference.SOURCE_PINS):
        link = scratch / "audioml" / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.AUDIO_ROOT / relative)
    for relative in sorted(reference.BOUNDARY_PINS):
        link = sdk / relative
        link.parent.mkdir(parents=True, exist_ok=True)
        link.symlink_to(reference.WORKTREE / relative)
    return target


def check_cold_start_regeneration(errors: list[str]) -> list[str]:
    committed = (
        REPORT.read_bytes() if REPORT.is_file() else b"",
        SIDECAR.read_bytes() if SIDECAR.is_file() else b"",
        PINS.read_bytes() if PINS.is_file() else b"",
    )
    if not all(committed):
        errors.append("committed_artifacts_missing")
        return []
    digests: list[str] = []
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    with tempfile.TemporaryDirectory(prefix="sdk-aubio-cold-") as temporary:
        root = Path(temporary)
        for index in range(1, 4):
            target = _prepare_scratch(root, index)
            process = subprocess.run([sys.executable, "run.py", "all"], cwd=target,
                                     capture_output=True, text=True, env=env)
            if process.returncode != 0:
                errors.append(f"cold_start_{index}_failed:" + process.stderr.strip())
                continue
            generated = (
                (target / "report.json").read_bytes(),
                (target / "report.json.sha256").read_bytes(),
                (target / "SOURCES.sha256").read_bytes(),
            )
            if generated != committed:
                errors.append(f"cold_start_{index}_bytes_differ")
            digests.append(hashlib.sha256(generated[0]).hexdigest())
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("cold_start_not_byte_identical")
    return digests


def main() -> int:
    errors: list[str] = []
    check_profile_source(errors)
    pins = check_pins(errors)
    report = check_report(errors)
    check_licensing(errors)
    changed = check_scope(errors)
    digests = check_cold_start_regeneration(errors)
    digest = hashlib.sha256(REPORT.read_bytes()).hexdigest() if REPORT.is_file() else "unavailable"
    if errors:
        for error in errors:
            print("FAIL: " + error)
        print(f"FAIL pins={pins} checks_ok={bool(report)} "
              f"cold_starts={len(digests)} report_sha256={digest} "
              f"changed_files={len(changed)} failures={len(errors)}")
        return 1
    print(f"PASS pins={pins} checks={len(report['profile_scoring']['checks'])} "
          f"cold_starts=3/3 byte_identical=true profile=Rate "
          f"status={report['status']} decision=DEFER report_sha256={digest} "
          f"changed_files={len(changed)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
