# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only byte, schema, pin, repeat, license and write-scope verification.

Run from this directory with ``python3 verify.py``. Nothing here regenerates or
rewrites evidence: the three report passes are built in memory and compared to
the committed bytes.
"""

from __future__ import annotations

import json
from pathlib import Path
import subprocess
import sys
from typing import Any, Dict, List

import reference
import run

HERE = Path(__file__).resolve().parent
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
REQUIRED_REPORT_KEYS = {
    "schema_id", "contract", "status", "task", "base_commit", "decision",
    "scope", "evidence_kinds", "fixture", "fixture_spec", "source_pins",
    "external_pins", "board_snapshot", "scorer", "cohort", "aggregation",
    "interpretation", "controls", "failed_items", "qualification",
}


class VerifyError(ValueError):
    pass


def _pairs(items: List[Any]) -> Dict[str, Any]:
    result: Dict[str, Any] = {}
    for key, value in items:
        if key in result:
            raise VerifyError("duplicate_json_key:" + key)
        result[key] = value
    return result


def _reject_constant(token: str) -> None:
    raise VerifyError("nonfinite_json_constant:" + token)


def strict_json(path: Path) -> Dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"),
                         object_pairs_hook=_pairs, parse_constant=_reject_constant)
    if not isinstance(payload, dict):
        raise VerifyError("root_not_object:" + path.name)
    return payload


def check_pins(errors: List[str]) -> int:
    count = 0
    external: Dict[str, str] = {}
    for raw in reference.PINS_FILE.read_text(encoding="utf-8").splitlines():
        if not raw or raw.startswith("#"):
            continue
        parts = raw.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append("malformed pin line: " + repr(raw))
            continue
        digest, label = parts
        count += 1
        if label.startswith("external:"):
            external[label.split(":", 1)[1]] = digest
            continue
        path = (reference.SOURCE_ROOT / label[7:]
                if label.startswith("source:") else reference.SDK_ROOT / label)
        if not path.is_file():
            errors.append("pinned file missing: " + label)
        elif reference.sha256(path.read_bytes()) != digest:
            errors.append("pinned bytes changed: " + label)
    expected_external = {
        "srmrpy-archive": reference.EXTERNAL_PINS["srmrpy"]["archive_sha256"],
        "gammatone-wheel": reference.EXTERNAL_PINS["gammatone"]["wheel_sha256"],
    }
    for label, digest in expected_external.items():
        if external.get(label) != digest:
            errors.append("external pin missing or stale: " + label)
    return count


def check_report(errors: List[str]) -> Dict[str, Any]:
    try:
        report = strict_json(reference.REPORT_FILE)
        contract = strict_json(reference.CONTRACT_FILE)
        adapter = strict_json(reference.ADAPTER_FILE)
        provider = strict_json(reference.PROVIDER_FILE)
        crosscheck = strict_json(reference.CROSSCHECK_FILE)
    except (OSError, ValueError) as error:
        errors.append("strict JSON failed: " + str(error))
        return {}
    if not REQUIRED_REPORT_KEYS <= set(report):
        errors.append("report missing sections: " + ", ".join(
            sorted(REQUIRED_REPORT_KEYS - set(report))))
        return report
    expected_bytes, digest = reference.canonical_report(report)
    if reference.REPORT_FILE.read_bytes() != expected_bytes.encode("utf-8") + b"\n":
        errors.append("report.json is not canonical byte output")
    sidecar = reference.SIDECAR_FILE.read_text(encoding="ascii")
    if sidecar != digest + "\n":
        errors.append("report.json.sha256 is stale")
    if report["schema_id"] != reference.REPORT_SCHEMA_ID:
        errors.append("unexpected report schema")
    if report["status"] != "proceed_adapter_defer_processor":
        errors.append("unexpected decision status")
    if report["decision"]["evidence_adapter"] != "proceed":
        errors.append("adapter decision is not proceed")
    if report["decision"]["sdk_processor"] != "defer":
        errors.append("processor decision is not defer")
    if report["decision"]["registration"] != "none":
        errors.append("unexpected registration")
    if report["qualification"]["status"] != "not_qualified":
        errors.append("qualification status is not not_qualified")
    kinds = report["evidence_kinds"]
    if set(kinds) < {"paired_synthetic", "unpaired_synthetic", "synthetic",
                     "human", "source_reported", "real_rir_or_device",
                     "public_benchmark"}:
        errors.append("evidence kinds are not separated")
    if (kinds["human"]["status"] != "none"
            or kinds["public_benchmark"]["status"] != "none"
            or kinds["real_rir_or_device"]["status"] != "none"):
        errors.append("disallowed evidence kind is present")
    if report["aggregation"]["selection_performed"] is not False:
        errors.append("selection must not be performed")
    invalid = report["controls"]["invalid_and_missing"]
    if any(row["status"] != "rejected" for row in invalid.values()):
        errors.append("invalid or missing case was not rejected")
    representative = report["controls"]["representative_valid"]
    if representative["status"] != "scored" or representative["srmr"] is None:
        errors.append("representative valid result is missing")
    if not report["controls"]["identity"]["byte_identical_scores"]:
        errors.append("identity repeat scores differ")
    if not report["controls"]["upstream_crosscheck"]["within_pinned_tolerance"]:
        errors.append("crosscheck exceeds pinned tolerance")
    if len(report["failed_items"]) != 5:
        errors.append("failed item count changed")
    if contract.get("verification_profile") != "evidence":
        errors.append("contract profile mismatch")
    if contract.get("base_commit") != reference.BASE_COMMIT:
        errors.append("contract base commit mismatch")
    if contract["public_boundary"]["public_api_abi_changed"]:
        errors.append("contract claims an API/ABI change")
    if adapter.get("default_enabled") is not False or adapter.get("opt_in_required") is not True:
        errors.append("adapter is not opt-in and disabled by default")
    if adapter.get("registration") != "unregistered-developer-only":
        errors.append("adapter is not unregistered")
    if (provider.get("default_enabled") is not False
            or provider.get("registered") is not False
            or provider.get("processor_exposure") is not False):
        errors.append("provider manifest is not off, unregistered and unexposed")
    for relative, expected in {**report["source_pins"],
                               **report["external_pins"]}.items():
        if not isinstance(expected, (str, dict)):
            errors.append("unexpected pin value: " + relative)
    if report["source_pins"] != reference.read_source_pins():
        errors.append("report source pins do not match SOURCES.sha256")
    crosscheck_digest = reference.sha256(reference.CROSSCHECK_FILE.read_bytes())
    if report["scorer"]["crosscheck_file_sha256"] != crosscheck_digest:
        errors.append("crosscheck file digest mismatch")
    for vector in crosscheck["vectors"]:
        if vector["abs_delta"] > reference.scorer.CROSSCHECK_ABS_TOLERANCE:
            errors.append("crosscheck vector exceeds tolerance: " + vector["case_id"])
    return report


def check_regeneration(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    payloads = []
    for _ in range(3):
        payload, _digest = run.build_report_bytes()
        payloads.append(payload)
    if len(set(payloads)) != 1:
        errors.append("three in-memory report passes are not byte-identical")
    expected, digest = reference.canonical_report(report)
    if payloads[0] != expected.encode("utf-8") + b"\n":
        errors.append("fresh report bytes differ from committed report")
    if reference.SIDECAR_FILE.read_text(encoding="ascii") != digest + "\n":
        errors.append("fresh report digest differs from sidecar")


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE_LINE not in head or SPDX_COPYRIGHT_LINE not in head:
            errors.append("missing SPDX header: " + path.name)
    reuse = (reference.SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_scope(errors: List[str]) -> List[str]:
    result = subprocess.run(
        ["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    changed: List[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if line[:2].strip() else line
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("change outside task scope: " + path)
    diff_check = subprocess.run(["git", "-C", str(reference.SDK_ROOT), "diff", "--check"],
                                capture_output=True, text=True)
    if diff_check.returncode != 0:
        errors.append("git diff --check failed: " + diff_check.stdout.strip())
    return changed


def main() -> int:
    errors: List[str] = []
    pin_count = check_pins(errors)
    report = check_report(errors)
    check_regeneration(errors, report)
    check_licensing(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(
        f"pins_ok={pin_count} json_ok=5 report_sha256="
        f"{reference.sha256(reference.REPORT_FILE.read_bytes())} "
        f"regeneration_ok=3 licensing_ok=1 scope_ok=1 changed_files={len(changed)}"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
