# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only task-local verification for the rate-profile fixture."""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", str(HERE.parents[5])))
PINS = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
TASK_PREFIX = "docs/task-evidence/distil-wav2vec2-adult-child-ridge/"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
FORBIDDEN_FIELDS = (
    "prob_child", "prob_adult", "predicted_label", "ground_truth_label",
    "fn_rate", "fp_rate", "balanced_error", "threshold_grid",
)
REQUIRED_GATES = (
    "model_revision_and_rights", "real_frozen_extractor_and_head",
    "rights_qualified_labeled_audio", "external_accuracy_generalization",
    "preferred_speed_claim", "target_runtime_timing",
    "rate_profile_condition_coverage", "source_output_mapping_and_preservation",
    "provider_intake",
)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def check_pins(errors: list[str]) -> int:
    lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
             if line and not line.startswith("#")]
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) != 2 or len(parts[0]) != 64:
            errors.append(f"malformed pin: {line!r}")
            continue
        digest, raw = parts
        if raw.startswith("source:"):
            path = SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            path = SDK_ROOT / raw
        if not path.is_file():
            errors.append(f"missing pin target: {raw}")
        elif sha256(path.read_bytes()) != digest:
            errors.append(f"pin mismatch: {raw}")
    return len(lines)


def strict_load(path: Path, errors: list[str]):
    def reject(value):
        raise ValueError(f"non-finite {value}")
    try:
        obj = json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)
    except Exception as exc:
        errors.append(f"json invalid {path.name}: {exc}")
        return None
    if not isinstance(obj, dict):
        errors.append(f"json root not object: {path.name}")
    return obj


def check_json(errors: list[str]) -> bool:
    report = strict_load(REPORT, errors)
    if report is None:
        return False
    if report.get("base_commit") != "ff0d92cc1a994e3f93adcab4b1d37bcd2a8a4a5d":
        errors.append("base_commit mismatch")
    if report.get("status") != "proposal_only_synthetic_incomplete":
        errors.append("status mismatch")
    if report.get("qualification_status") != "not_qualified":
        errors.append("qualification_status mismatch")
    if report.get("profile") != "rate":
        errors.append("report profile is not rate")
    if report.get("task", {}).get("kind") != "measured_syllable_rate_regression":
        errors.append("task kind is not rate regression")
    if report.get("model", {}).get("classifier_head_used") is not False:
        errors.append("classifier head marked as used")
    if report.get("model", {}).get("documented_context_not_reproduced", {}).get("reproduced_here") is not False:
        errors.append("research context claimed as reproduced")
    if report.get("boundary", {}).get("window_samples") != 64000:
        errors.append("window is not exactly 64,000 samples")
    cv = report.get("training", {})
    held = report.get("held_out", {})
    if cv.get("evaluation_fold") != held.get("fold") or held.get("evaluation_labels_used_in_fit") is not False:
        errors.append("evaluation fold separation broken")
    if held.get("evaluation_labels_used_for_alpha_selection") is not False:
        errors.append("evaluation fold used for alpha selection")
    if report.get("evidence_classes", {}).get("synthetic_wiring_mae_rmse_r") != "wiring_only_not_accuracy":
        errors.append("synthetic metrics not labeled as wiring evidence")
    if any(case.get("status") != "rejected" for case in report.get("validation", {}).get("cases", [])):
        errors.append("invalid input accepted")
    if report.get("validation", {}).get("all_rejected") is not True:
        errors.append("rejection gate not all-rejected")
    chains = report.get("state_and_cross_hop", {}).get("cross_hop", {})
    if any(not chain.get("exact_half_open_interval") or chain.get("gap_count")
           or chain.get("overlap_count") for chain in chains.values()):
        errors.append("cross-hop coverage not exact")
    text = REPORT.read_text(encoding="utf-8")
    for field in FORBIDDEN_FIELDS:
        if field in text:
            errors.append(f"classification field present: {field}")
    gates = report.get("gates", [])
    for gate in gates:
        if gate.get("status") != "blocked":
            errors.append(f"gate not blocked: {gate.get('id')}")
    gate_ids = {gate.get("id") for gate in gates}
    for gate_id in REQUIRED_GATES:
        if gate_id not in gate_ids:
            errors.append(f"missing gate: {gate_id}")
    return True


def check_reproduction(errors: list[str]) -> tuple[bool, str]:
    sys.path.insert(0, str(HERE))
    import reference  # noqa: E402
    reference.require_supported_runtime()
    expected = reference.canonical_report_bytes(reference.build_report())
    actual = REPORT.read_bytes()
    ok = expected == actual
    if not ok:
        errors.append("report.json not byte-reproducible")
    digest = sha256(actual)
    sha_line = REPORT_SHA.read_text(encoding="utf-8").strip() if REPORT_SHA.exists() else ""
    if sha_line != f"{digest}  report.json":
        errors.append("report.json.sha256 mismatch")
        ok = False
    return ok, digest


def check_licensing(errors: list[str]) -> bool:
    ok = True
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_L not in head or SPDX_C not in head:
            errors.append(f"missing SPDX: {path.name}")
            ok = False
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        errors.append("REUSE.toml docs/** coverage missing")
        ok = False
    return ok


def check_scope(errors: list[str]) -> bool:
    result = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
        capture_output=True, text=True, check=True)
    ok = True
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            errors.append(f"out of scope change: {path}")
            ok = False
    return ok


def main() -> int:
    errors: list[str] = []
    pins = check_pins(errors)
    json_ok = check_json(errors)
    reproduction_ok, digest = check_reproduction(errors)
    licensing_ok = check_licensing(errors)
    scope_ok = check_scope(errors)
    if errors:
        for error in errors:
            print(f"FAIL: {error}")
        print(f"pins_ok={not any('pin' in e for e in errors)} json_ok={json_ok} "
              f"licensing_ok={licensing_ok} scope_ok={scope_ok} "
              f"reproduction_ok={reproduction_ok} report_sha256={digest}")
        return 1
    print(f"pins_ok=True json_ok=True licensing_ok=True scope_ok=True reproduction_ok=True "
          f"pins={pins} report_sha256={digest}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
