# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only verifier for SDK-STREAMING-CONFORMER-TED evidence."""

from __future__ import annotations

import subprocess
import sys
from pathlib import Path

import reference

FILES = ("report.json", "report.json.sha256", "SOURCES.sha256", "contract.json")


def fail(errors: list[str], message: str) -> None:
    errors.append(message)


def main() -> int:
    errors: list[str] = []
    task = Path(__file__).resolve().parent

    for name in FILES:
        if not (task / name).is_file():
            fail(errors, "missing:" + name)
    if errors:
        for error in errors:
            print(error)
        return 1

    try:
        report = reference.strict_load(task / "report.json")
    except Exception as exc:  # noqa: BLE001
        fail(errors, "report_invalid:" + str(exc))
        report = None
    try:
        contract = reference.strict_load(task / "contract.json")
    except Exception as exc:  # noqa: BLE001
        fail(errors, "contract_invalid:" + str(exc))
        contract = None

    report_bytes = (task / "report.json").read_bytes()
    sidecar = (task / "report.json.sha256").read_bytes()
    sources = (task / "SOURCES.sha256").read_bytes()
    contract_bytes = (task / "contract.json").read_bytes()

    if sidecar != reference.sidecar_bytes(report_bytes):
        fail(errors, "sidecar_mismatch")
    expected_sources = reference.sources_bytes(report_bytes, sidecar)
    if sources != expected_sources:
        fail(errors, "sources_mismatch")
    if report is not None:
        expected_contract = reference.contract_bytes(report_bytes, sidecar, sources, report)
        if contract_bytes != expected_contract:
            fail(errors, "contract_mismatch")

    # Pin/source/boundary checks
    try:
        reference.validate_asset_pins()
    except Exception as exc:  # noqa: BLE001
        fail(errors, "pin_invalid:" + str(exc))

    # README digest table
    try:
        rows = reference.readme_pin_rows()
        expected_rows = [(k, reference.SOURCE_PINS[k.split(":", 1)[1]]) for k in sorted("source:" + p for p in reference.SOURCE_PINS)] + \
                        [(k, reference.BOUNDARY_PINS[k]) for k in sorted(reference.BOUNDARY_PINS)]
        if rows != expected_rows:
            fail(errors, "readme_digest_mismatch")
    except Exception as exc:  # noqa: BLE001
        fail(errors, "readme_digest_invalid:" + str(exc))

    # strict pin parsing / duplicate rejection
    try:
        reference.parse_pin_lines(sources.decode("utf-8"))
    except Exception as exc:  # noqa: BLE001
        fail(errors, "sources_parse_invalid:" + str(exc))

    # license sidecars
    for name in ("report.json", "report.json.sha256", "SOURCES.sha256", "contract.json"):
        lic = task / (name + ".license")
        if not lic.is_file():
            fail(errors, "missing_license_sidecar:" + name)
        else:
            text = lic.read_text(encoding="utf-8")
            if reference.SPDX_COPYRIGHT not in text or reference.SPDX_LICENSE not in text:
                fail(errors, "bad_license_sidecar:" + name)

    # scope
    base = reference.scope_base(reference.SDK_ROOT)
    if base is None:
        fail(errors, "scope_base_unavailable")
    else:
        try:
            changed = reference.scope_changed_paths(reference.SDK_ROOT, base)
            violations = reference.scope_violations(changed)
            for path in violations:
                fail(errors, "base_out_of_scope_change:" + path)
        except Exception as exc:  # noqa: BLE001
            fail(errors, "scope_check_failed:" + str(exc))

    # git diff --check
    result = subprocess.run(["git", "-C", str(reference.SDK_ROOT), "diff", "--check"],
                            capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail(errors, "git_diff_check_failed")

    # 3 fresh builds
    builds = [reference.report_bytes() for _ in range(3)]
    if len(set(builds)) != 1:
        fail(errors, "report_nondeterministic")
    if report is not None and report_bytes != builds[0]:
        fail(errors, "report_not_canonical")

    if report is not None:
        required = {
            "decision": reference.DECISION,
            "evidence_status": reference.EVIDENCE_STATUS,
            "qualification_status": reference.QUALIFICATION_STATUS,
            "status": reference.STATUS,
            "profile": reference.PROFILE,
        }
        for key, value in required.items():
            if report.get(key) != value:
                fail(errors, "report_field_mismatch:" + key)
        if report.get("no_missing_result_qualifies_candidate") is not True:
            fail(errors, "report_missing_no_qualify_invariant")
        if not isinstance(report.get("gates"), list) or len(report["gates"]) != 8:
            fail(errors, "report_gate_count")
        if not isinstance(report.get("exact_blockers"), list) or len(report["exact_blockers"]) != 4:
            fail(errors, "report_blocker_count")
        if report.get("board_link", {}).get("full_tasks_json_hashed") is not False:
            fail(errors, "report_full_tasks_json_hashed")
    if contract is not None:
        if contract.get("board_link", {}).get("stable_sha256") != reference.BOARD_STABLE_SHA256:
            fail(errors, "contract_board_sha_mismatch")

    for error in errors:
        print(error)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
