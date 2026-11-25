#!/usr/bin/env python3
# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-SURVEY-ENG-01 task-local evidence map."""
from __future__ import annotations

import hashlib
import json
import re
import subprocess
import sys
from pathlib import Path

import build_report as spec

HERE = Path(__file__).resolve().parent
EXPECTED_FILES = {
    "README.md",
    "build_report.py",
    "report.json",
    "report.json.sha256",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256",
    "SOURCES.sha256.license",
    "test_survey_map.py",
    "verify.py",
}
# REUSE-IgnoreStart
LICENSE_TEXT = (
    "SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes\n"
    "SPDX-License-Identifier: Apache-2.0\n"
)
# REUSE-IgnoreEnd
CLAIM_FIELDS = (
    "public_benchmark", "quality", "device", "listening", "release",
    "provider_enablement", "real_audio_or_assets", "default_abi_build_or_ci_change",
)
EXPECTED_FAMILIES = {"framing-channel-mapping", "bandlimited-resampling"}
EXPECTED_COMPONENTS = {
    "typed-frame-resample-and-drift-diagnostics",
    "identity-pcm-and-noop-fixtures",
    "numpy-scipy-soundfile-wav-and-resampling",
    "speex-resampler", "libsamplerate", "libsoxr",
}


def read_report() -> tuple[bytes, dict]:
    raw = (HERE / "report.json").read_bytes()
    return raw, json.loads(raw.decode("utf-8"))


def digest(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def git(*args: str) -> subprocess.CompletedProcess[str]:
    return subprocess.run(
        ("git", "-C", str(spec.WORKTREE), *args),
        capture_output=True, text=True, check=False,
    )


def check_scope() -> tuple[bool, str]:
    result = git("status", "--porcelain", "--untracked-files=all")
    if result.returncode != 0:
        return False, "git status failed"
    prefix = "docs/task-evidence/survey-eng-01/"
    for line in result.stdout.splitlines():
        if len(line) < 4:
            continue
        path = line[3:]
        if path.startswith('"'):
            path = path.strip('"').encode().decode("unicode_escape")
        if path != "docs/task-evidence/survey-eng-01" and not path.startswith(prefix):
            return False, f"change outside evidence scope: {path}"
    return True, "worktree changes confined to survey-eng-01"


def check_base_ancestor() -> tuple[bool, str]:
    exists = git("cat-file", "-e", f"{spec.BASE_COMMIT}^{{commit}}")
    ancestor = git(
        "merge-base", "--is-ancestor", spec.BASE_COMMIT, "HEAD"
    )
    ok = exists.returncode == 0 and ancestor.returncode == 0
    return ok, "base commit is an ancestor of HEAD" if ok else "base commit not in HEAD history"


def check_text_hygiene() -> tuple[bool, str]:
    for path in sorted(HERE.iterdir()):
        if not path.is_file() or path.suffix in {".pyc", ".so", ".dylib", ".wav", ".flac"}:
            continue
        data = path.read_bytes()
        if b"\r\n" in data:
            return False, f"CRLF in {path.name}"
        for number, line in enumerate(data.decode("utf-8").splitlines(), 1):
            if line != line.rstrip():
                return False, f"trailing whitespace in {path.name}:{number}"
    return True, "no CRLF or trailing whitespace"


def main() -> int:
    results: list[tuple[str, bool, str]] = []

    py_ok = sys.version_info[:3] == (3, 12, 16)
    results.append(("python", py_ok, "Python 3.12.16"))
    results.append(("bytecode", bool(sys.dont_write_bytecode), "PYTHONDONTWRITEBYTECODE=1"))

    actual_files = {path.name for path in HERE.iterdir() if path.is_file()}
    results.append((
        "files", actual_files == EXPECTED_FILES,
        f"expected {len(EXPECTED_FILES)} files; found {len(actual_files)}",
    ))

    raw, report = read_report()
    expected_raw = spec.canonical_json(spec.build_report()).encode("utf-8")
    results.append(("canonical", raw == expected_raw, "report.json regenerates byte-for-byte"))

    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
    results.append((
        "report_digest", sidecar == f"{digest(raw)}  report.json\n",
        "SHA-256 sidecar matches report bytes",
    ))

    manifest = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
    results.append((
        "manifest", manifest == spec.build_manifest(),
        "source and local-artifact manifest regenerates byte-for-byte",
    ))

    pins = spec.build_pins()
    pin_ok = (
        report.get("source_pins") == pins
        and report.get("source_pin_verification", {}).get("count") == len(pins)
        and report.get("source_pin_verification", {}).get("all_recomputed") is True
    )
    results.append(("pins", pin_ok, f"{len(pins)} recomputed evidence pins"))

    board_ok = (
        report.get("source_pin_verification", {}).get("board")
        == spec.board_projection()
    )
    results.append(("board", board_ok, "stable board-row projection matches"))

    claims = report.get("claim_gate", {})
    claim_ok = (
        claims.get("no_missing_result_qualifies_candidate") is True
        and all(claims.get(field) is False for field in CLAIM_FIELDS)
        and report.get("disposition") == "taxonomy_and_comparison_only"
        and report.get("qualification_status") == "not_started_no_new_execution"
    )
    results.append(("claims", claim_ok, "no public benchmark/quality/device/listening/release claim"))

    classic = {
        row.get("id") for row in report.get("original_method_families", {}).get("classic", [])
    }
    ml = report.get("original_method_families", {}).get("ml", {})
    components = {
        row.get("component_id") for row in report.get("component_map", [])
    }
    family_ok = (
        classic == EXPECTED_FAMILIES
        and ml.get("status") == "not_applicable"
        and ml.get("mapped_components") == []
        and EXPECTED_COMPONENTS.issubset(components)
    )
    results.append(("families", family_ok, "both classical families and ML N/A audited"))

    lead = next(
        (row for row in report.get("source_leads", []) if row.get("id") == "S42"), None
    )
    lead_ok = bool(
        lead
        and lead.get("registry_revision_pin") == "unpinned master URL"
        and lead.get("local_counterpart", {}).get("sha256")
        == next(p["sha256"] for p in pins
                if p["key"] == "sdk:third_party/speexdsp/libspeexdsp/resample.c")
        and any(
            row.get("component_id") == "speex-resampler"
            for row in lead.get("component_mapping", [])
        )
    )
    results.append(("source_lead", lead_ok, "S42 linked to vendored source and component"))

    executions = report.get("historical_executions", [])
    execution_ok = len(executions) == 4 and all(
        set(("inputs", "controls", "assets", "local_outcomes", "reported_outcomes", "limits"))
        .issubset(row)
        for row in executions
    )
    results.append(("executions", execution_ok, "four historical records with comparison fields"))

    gap = report.get("gap_followup", {})
    gap_ok = (
        gap.get("status") == "proposed_unassigned_not_a_board_entry"
        and gap.get("parent_task") == spec.TASK_ID
        and "no implementation" in gap.get("deliverable", "")
        and gap.get("stop_condition", "").startswith("feasibility only")
    )
    results.append(("gap", gap_ok, "bounded unassigned feasibility follow-up only"))

    license_ok = all(
        (HERE / f"{name}.license").read_text(encoding="utf-8") == LICENSE_TEXT
        for name in ("report.json", "report.json.sha256", "SOURCES.sha256")
    )
    results.append(("licenses", license_ok, "three SPDX sidecars exact"))

    scope_ok, scope_note = check_scope()
    results.append(("scope", scope_ok, scope_note))
    base_ok, base_note = check_base_ancestor()
    results.append(("base", base_ok, base_note))
    hygiene_ok, hygiene_note = check_text_hygiene()
    results.append(("hygiene", hygiene_ok, hygiene_note))

    forbidden = re.compile(
        r"(?i)(passed (quality|device|listening|release)|qualified candidate|"
        r"public benchmark score|production ready|approved release)"
    )
    forbidden_ok = not forbidden.search(raw.decode("utf-8"))
    results.append(("non_claims", forbidden_ok, "no assertive claim language in report"))

    failed = [row for row in results if not row[1]]
    for name, ok, note in results:
        print(f"{'PASS' if ok else 'FAIL'} {name}: {note}")
    summary = " ".join(f"{name}={int(ok)}" for name, ok, _ in results)
    print(f"verify {summary}")
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
