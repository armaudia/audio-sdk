# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verifier for the SDK-LIBROSA-BEAT-TRACK-TEMPO package.

Fails closed on non-canonical or duplicate-key/nonfinite JSON, stale digests,
stale pins, a non-rate profile, a promoted beat/tempo/meter result, a qualified
claim, an open release gate, license gaps, README digest-table drift,
out-of-scope worktree changes, whitespace damage or a dirty ``git diff
--check``.  Scope is enforced against the newest merge-base with ``origin/main``
or ``main``; a missing base emits ``scope_base_unavailable`` and a branch edit
outside the task directory emits ``base_out_of_scope_change``.  Never writes.
"""

from __future__ import annotations

import json
import os
import platform
import subprocess
import sys
from pathlib import Path
from typing import Any, Dict, List

sys.dont_write_bytecode = True

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402

SDK_ROOT = reference.WORKTREE
REPORT = HERE / "report.json"
CONTRACT = HERE / "contract.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
README = HERE / "README.md"

SPDX_LICENSE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SIDECARS = (
    "SOURCES.sha256.license",
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
)


def _strict(path: Path, errors: List[str], label: str) -> Dict[str, Any]:
    try:
        payload = reference.read_strict_json(path)
    except (OSError, ValueError, UnicodeError) as error:
        errors.append("strict JSON failed: " + label + ": " + str(error))
        return {}
    return payload


def _eq(errors: List[str], label: str, actual: Any, expected: Any) -> None:
    if actual != expected:
        errors.append(label)


def check_interpreter(errors: List[str]) -> None:
    observed = platform.python_version()
    if observed != reference.REQUIRED_INTERPRETER:
        errors.append("verifier_interpreter_mismatch:" + observed)


def check_json_files(errors: List[str]) -> Dict[str, Any]:
    report = _strict(REPORT, errors, "report.json")
    contract = _strict(CONTRACT, errors, "contract.json")
    if report:
        expected, digest = reference.canonical_report(report)
        if REPORT.read_bytes() != expected.encode("utf-8"):
            errors.append("report.json is not canonical byte output")
        if SIDECAR.read_text(encoding="ascii") != (
                digest + "  report.json\n"):
            errors.append("report.json.sha256 is stale")
    if contract:
        if CONTRACT.read_bytes() != reference.canonical_bytes(contract):
            errors.append("contract.json is not canonical byte output")
    return {"report": report, "contract": contract}


def check_pins(errors: List[str]) -> int:
    count = 0
    try:
        lines = PINS.read_text(encoding="ascii").splitlines()
    except OSError as error:
        errors.append("missing SOURCES.sha256: " + str(error))
        return 0
    try:
        rows = reference.parse_pin_lines("\n".join(lines))
    except ValueError as error:
        errors.append("malformed SOURCES.sha256: " + str(error))
        return 0
    for digest, raw_path in rows:
        count += 1
        if raw_path.startswith("source:"):
            path = reference.AUDIO_ROOT / raw_path.split(":", 1)[1]
        elif raw_path.startswith("sdk:"):
            path = reference.SDK_ROOT / raw_path.split(":", 1)[1]
        else:
            path = HERE.parent / raw_path.split("/", 2)[-1]
            path = HERE / raw_path.rsplit("/", 1)[-1]
        if not path.is_file():
            errors.append("pinned file missing: " + raw_path)
        elif reference.sha256_file(path) != digest:
            errors.append("pinned bytes changed: " + raw_path)
        if "TASKS.json" in raw_path:
            errors.append("mutable task board is pinned: " + raw_path)
    try:
        if PINS.read_bytes() != reference.sources_bytes():
            errors.append("SOURCES.sha256 is not the deterministic generated "
                          "bytes")
    except (OSError, ValueError) as error:
        errors.append("pin regeneration failed: " + str(error))
    return count


def check_board(errors: List[str], report: Dict[str, Any],
                contract: Dict[str, Any]) -> None:
    try:
        live = reference._board_row()
    except (OSError, ValueError, KeyError, TypeError) as error:
        errors.append("board row unavailable: " + str(error))
        return
    _eq(errors, "report board identity is stale", report.get("board_row"),
        live)
    _eq(errors, "contract board identity is stale",
        contract.get("board_row"), live)
    row = report.get("board_row", {})
    if row.get("full_tasks_json_hashed") is not False:
        errors.append("full task board is hashed")
    stable = row.get("stable_fields", {})
    if reference.object_digest(stable) != row.get("stable_sha256"):
        errors.append("stable board hash mismatch")
    if stable.get("id") != reference.TASK:
        errors.append("stable board task id mismatch")


def check_report(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    _eq(errors, "unexpected report schema", report.get("schema_id"),
        reference.REPORT_SCHEMA_ID)
    _eq(errors, "report status", report.get("status"),
        reference.STATUS)
    _eq(errors, "report evidence status", report.get("evidence_status"),
        "incomplete")
    _eq(errors, "report decision", report.get("decision"), "DEFER")
    _eq(errors, "report defer point", report.get("defer_before"),
        "caller_tool_admission")
    _eq(errors, "report profile", report.get("profile"), "rate")
    _eq(errors, "report task", report.get("task"), reference.TASK)
    _eq(errors, "report component", report.get("component"),
        reference.COMPONENT_ID)
    _eq(errors, "report base commit", report.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "report branch", report.get("branch"), reference.BRANCH)
    _eq(errors, "report disposition", report.get("disposition"),
        reference.DISPOSITION)
    _eq(errors, "report proposal flag", report.get("proposal_only"), True)
    _eq(errors, "report incomplete flag", report.get("incomplete"), True)

    profile = report.get("acceptance_profile", {})
    _eq(errors, "rate profile not recorded", profile.get("profile"), "rate")
    items = profile.get("required_items", {})
    if len(items) != 10:
        errors.append("rate profile item set mismatch")
    for name, item in items.items():
        if item.get("status") not in {"synthetic_only", "blocked"}:
            errors.append("rate item promoted: " + name)
    expected_blockers = sorted(
        name for name, item in items.items()
        if item.get("status") == "blocked")
    _eq(errors, "profile blocker list mismatch",
        profile.get("profile_blockers"), expected_blockers)
    _eq(errors, "rate profile promoted", profile.get("satisfied"), False)

    candidate = report.get("candidate", {})
    _eq(errors, "candidate default rate", candidate.get(
        "default_sample_rate_hz"), reference.UPSTREAM_DEFAULT_SAMPLE_RATE_HZ)
    _eq(errors, "candidate configured rate", candidate.get(
        "configured_sample_rate_hz"), reference.SAMPLE_RATE_HZ)
    _eq(errors, "candidate sdk rate", candidate.get("sdk_v0_sample_rate_hz"),
        reference.SAMPLE_RATE_HZ)
    _eq(errors, "candidate sdk frame", candidate.get("sdk_v0_frame_samples"),
        reference.FRAME_SAMPLES)
    _eq(errors, "candidate configured hop", candidate.get(
        "configured_hop_length"), reference.HOP_SAMPLES)
    for key in ("native_default_compatible", "source_present",
                "runtime_present", "exact_numeric_output_present",
                "real_corpus_present"):
        if candidate.get(key) is not False:
            errors.append("candidate claim is not false: " + key)

    ref = report.get("reference", {})
    for key in ("is_candidate", "exact_librosa_executed", "source_present",
                "runtime_present", "implementation_present",
                "adapter_present", "exact_numeric_output_present",
                "surrogate_is_candidate"):
        if ref.get(key) is not False:
            errors.append("reference claim is not false: " + key)
    _eq(errors, "surrogate presence", ref.get("surrogate_present"), True)
    _eq(errors, "reference status", ref.get("status"), "synthetic_only")

    environment = report.get("environment", {})
    _eq(errors, "environment interpreter", environment.get(
        "required_interpreter"), reference.REQUIRED_INTERPRETER)
    _eq(errors, "librosa detected", environment.get("librosa_present"), False)
    _eq(errors, "librosa imported", environment.get("librosa_imported"), False)
    _eq(errors, "librosa executed", environment.get("librosa_executed"), False)
    _eq(errors, "package install", environment.get(
        "package_install_or_download"), False)

    local = report.get("local_unpinned_runtime", {})
    for key in ("admitted", "pinned", "imported", "executed"):
        if local.get(key) is not False:
            errors.append("unpinned runtime admitted: " + key)
    _eq(errors, "unpinned runtime version", local.get("librosa_version"),
        "0.11.0")

    qualification = report.get("qualification", {})
    _eq(errors, "qualification status", qualification.get("status"),
        "not_qualified")
    for key, value in qualification.items():
        if key == "status":
            continue
        if value is not False:
            errors.append("qualification promotes a missing result: " + key)

    gates = report.get("release_gates", [])
    _eq(errors, "release gate count", len(gates), 8)
    _eq(errors, "release gate IDs", [gate.get("id") for gate in gates],
        [f"RG-{index:02d}" for index in range(1, 9)])
    if any(gate.get("status") != "blocked" for gate in gates):
        errors.append("a release gate is not blocked")
    blockers = report.get("exact_blockers", [])
    _eq(errors, "exact blocker count", len(blockers), 6)
    _eq(errors, "exact blocker IDs", [item.get("id") for item in blockers],
        [f"BLK-{index:02d}" for index in range(1, 7)])

    tempo = {case.get("stimulus"): case for case in
             report.get("tempo_tracking", {}).get("cases", [])}
    expected_tempo = {
        "steady_music_1x": ("stable", 10000),
        "rate_0_8": ("stable", 8000),
        "rate_1_2": ("stable", 12000),
        "tempo_step": ("unstable", None),
        "syncopated_offbeat": ("stable", 12000),
        "speech_like_unfamiliar": ("unstable", None),
        "rebuffer_gap": ("stable", 12000),
        "drift_decreasing": ("unstable", None),
        "silence": ("no_onsets", None),
        "final_partial": ("stable", 10000),
    }
    if set(tempo) != set(expected_tempo):
        errors.append("tempo case set mismatch")
    for name, (status, bpm) in expected_tempo.items():
        if name not in tempo:
            continue
        _eq(errors, "tempo status mismatch: " + name,
            tempo[name].get("status"), status)
        _eq(errors, "tempo bpm mismatch: " + name,
            tempo[name].get("bpm_x100"), bpm)
        _eq(errors, "tempo case promoted: " + name,
            tempo[name].get("qualifies"), False)
    step = report.get("tempo_tracking", {}).get("tempo_step", {})
    _eq(errors, "tempo-step segments", step.get("observed_segments"),
        [10000, 15000])
    _eq(errors, "tempo-step exact", step.get("exact"), True)
    _eq(errors, "tempo step global status", step.get("global_status"),
        "unstable")

    beats = report.get("beat_tracking", {}).get("cases", [])
    _eq(errors, "beat case count", len(beats), 10)
    for case in beats:
        _eq(errors, "beat case status promoted: " + case.get("stimulus", "?"),
            case.get("status"), "synthetic_only")
        _eq(errors, "beat case qualifies: " + case.get("stimulus", "?"),
            case.get("qualifies"), False)
        if case.get("stimulus") == "silence":
            _eq(errors, "silence produced beats", case.get("detected"), 0)
        else:
            _eq(errors, "beat case false positives: "
                + case.get("stimulus", "?"), case.get("false_positives"), 0)
            _eq(errors, "beat case false negatives: "
                + case.get("stimulus", "?"), case.get("false_negatives"), 0)
            _eq(errors, "beat case F1: " + case.get("stimulus", "?"),
                case.get("f1_x1000"), 1000)

    meters = {case.get("stimulus"): case for case in
              report.get("downbeat_meter", {}).get("cases", [])}
    for name in ("steady_music_1x", "rate_0_8", "rate_1_2"):
        _eq(errors, "meter estimate is not 4 for " + name,
            meters.get(name, {}).get("meter"), 4)
        _eq(errors, "meter estimate is not correct for " + name,
            meters.get(name, {}).get("correct"), True)
    _eq(errors, "syncopated meter is not ambiguous",
        meters.get("syncopated_offbeat", {}).get("status"), "ambiguous")
    _eq(errors, "downbeat labels claimed present",
        report.get("downbeat_meter", {}).get("truth_available"), False)
    if any(case.get("qualifies") is not False for case in meters.values()):
        errors.append("a meter case is promoted")

    rate = report.get("rate_profile", {})
    _eq(errors, "identity tempo", rate.get("identity_1x", {}).get(
        "bpm_x100"), 10000)
    _eq(errors, "identity beats", rate.get("identity_1x", {}).get(
        "detected_beats"), 10)
    _eq(errors, "rate duration error", rate.get("duration", {}).get(
        "max_error_samples"), 0)
    _eq(errors, "rate duration exact", rate.get("duration", {}).get(
        "exact"), True)
    for row in rate.get("rate_changes", []):
        _eq(errors, "rate change observed", row.get("observed_bpm_x100"),
            row.get("expected_bpm_x100"))
        _eq(errors, "rate change exact", row.get("exact"), True)
    _eq(errors, "pitch promoted", rate.get("pitch", {}).get("qualifies"),
        False)
    _eq(errors, "transient proxy", rate.get("transient_proxy", {}).get(
        "final_partial_error_samples"), -10)
    _eq(errors, "speech tempo claim", rate.get("speech_unfamiliar", {}).get(
        "qualifies"), False)
    _eq(errors, "silence status", rate.get("silence", {}).get("status"),
        "no_onsets")
    _eq(errors, "rebuffer suppression", rate.get("rebuffer", {}).get(
        "cross_gap_ioi_suppressed"), True)
    _eq(errors, "drift monotonic", rate.get("drift", {}).get(
        "monotonic_decreasing"), True)
    _eq(errors, "final partial valid count", rate.get("final_partial", {}).get(
        "valid_count"), 137)
    _eq(errors, "final partial error", rate.get("final_partial", {}).get(
        "error_samples"), -10)
    _eq(errors, "playback buffering final count",
        rate.get("playback_buffering", {}).get("final_partial_valid_count"),
        137)
    _eq(errors, "device buffer measured",
        rate.get("playback_buffering", {}).get("device_buffer_measured"),
        False)
    _eq(errors, "source mapping audio output",
        rate.get("source_output_mapping", {}).get("audio_output_produced"),
        False)

    streaming = report.get("streaming", {})
    _eq(errors, "streaming all match", streaming.get("all_match"), True)
    _eq(errors, "streaming chunk schedules", streaming.get("chunk_schedules"),
        [160, 480, 800, 137, 641])
    _eq(errors, "streaming accepted samples",
        streaming.get("accepted_samples"), 48137)
    _eq(errors, "streaming scheduler measured",
        streaming.get("scheduler_measured"), False)
    reset = report.get("reset", {})
    _eq(errors, "reset matches fresh", reset.get("matches_fresh"), True)
    _eq(errors, "reset rejected epochs",
        [row.get("epoch") for row in reset.get("rejected_epochs", [])],
        [0, -1])

    adverse = report.get("adverse_rejections", [])
    _eq(errors, "adverse rejection count", len(adverse), 40)
    _eq(errors, "adverse rejection flag", report.get(
        "adverse_all_rejected"), True)
    for item in adverse:
        if item.get("status") != "rejected" or item.get(
                "state_unchanged") is not True:
            errors.append("adverse case not rejected immutably: "
                          + item.get("case_id", "?"))

    caller = report.get("caller_tool_reference", {})
    for key in ("admitted", "reproduced", "exact_output_present",
                "reads_bytes", "loads_source", "executes_runtime"):
        _eq(errors, "caller tool claim is not false: " + key,
            caller.get(key), False)
    _eq(errors, "caller tool identity only", caller.get("identity_only"),
        True)
    _eq(errors, "caller tool accepted control",
        caller.get("accepted_control"), True)

    external = report.get("external_artifacts", {})
    _eq(errors, "external artifact status", external.get("status"),
        "blocked")
    _eq(errors, "external artifact presence", external.get("any_present"),
        False)

    licensing = report.get("licensing", {})
    _eq(errors, "reported upstream license", licensing.get(
        "reported_upstream_license"), "ISC")
    _eq(errors, "license review", licensing.get("review_status"), "blocked")
    for key in ("license_text_staged", "dependency_lock_staged",
                "attribution_notice_staged", "redistribution_reviewed",
                "product_use_reviewed"):
        _eq(errors, "license claim is not false: " + key,
            licensing.get(key), False)
    _eq(errors, "LGPL dependency not recorded",
        licensing.get("lgpl_dependency_present"), "soxr")

    repeat = report.get("repeatability", {})
    _eq(errors, "repeatability runs", repeat.get("runs"), 3)
    _eq(errors, "repeatability byte identity", repeat.get(
        "byte_identical"), True)
    digests = repeat.get("case_matrix_digests", [])
    if len(digests) != 3 or len(set(digests)) != 1:
        errors.append("case-matrix repeat digests differ")

    boundary = report.get("boundary", {})
    if not boundary or any(value is not False for value in boundary.values()):
        errors.append("a boundary flag claims a change")
    scope = report.get("scope", {})
    _eq(errors, "scope synthetic only", scope.get("synthetic_only"), True)
    _eq(errors, "scope task local", scope.get("task_local_only"), True)
    for key, value in scope.items():
        if key in {"synthetic_only", "task_local_only"}:
            continue
        if value is not False:
            errors.append("scope flag is not false: " + key)

    text = reference.canonical_text(report)
    if '"qualifies":true' in text or '"status":"qualified"' in text:
        errors.append("canonical report contains a qualified claim")
    if "TASKS.json" in reference.canonical_text(report.get("source_pins", {})):
        errors.append("mutable task board appears in source pins")
    _eq(errors, "report base commit differs from pin",
        report.get("base_commit"), reference.BASE_COMMIT)


def check_contract(errors: List[str], contract: Dict[str, Any],
                   report: Dict[str, Any]) -> None:
    if not contract:
        return
    _eq(errors, "unexpected contract schema", contract.get("schema_id"),
        reference.CONTRACT_SCHEMA_ID)
    _eq(errors, "contract task", contract.get("task"), reference.TASK)
    _eq(errors, "contract component", contract.get("component"),
        reference.COMPONENT_ID)
    _eq(errors, "contract base commit", contract.get("base_commit"),
        reference.BASE_COMMIT)
    _eq(errors, "contract branch", contract.get("branch"), reference.BRANCH)
    _eq(errors, "contract decision", contract.get("decision"), "DEFER")
    _eq(errors, "contract evidence status", contract.get("evidence_status"),
        "incomplete")
    _eq(errors, "contract qualification",
        contract.get("qualification_status"), "not_qualified")
    _eq(errors, "contract verification profile",
        contract.get("verification_profile"), "rate")
    for key in ("release_gates", "exact_blockers", "source_pins",
                "boundary_pins", "candidate", "format", "licensing",
                "boundary", "scope", "acceptance_profile",
                "caller_tool_reference"):
        _eq(errors, "contract/report differ: " + key,
            contract.get(key), report.get(key))

    pins = contract.get("artifact_pins", {})
    if not pins:
        errors.append("artifact pins absent")
    for path, digest in pins.items():
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("artifact pin outside task scope: " + path)
            continue
        full = reference.SDK_ROOT / path
        if not full.is_file():
            errors.append("artifact pin missing: " + path)
        elif reference.sha256_file(full) != digest:
            errors.append("artifact pin stale: " + path)
    for forbidden in ("contract.json", "SOURCES.sha256", "report.json",
                      "report.json.sha256"):
        if any(path.endswith("/" + forbidden) for path in pins):
            errors.append("self-referential artifact pin: " + forbidden)


def check_repeats(errors: List[str], report: Dict[str, Any]) -> None:
    if not report:
        return
    texts = []
    for _ in range(3):
        built = reference.build_report()
        text, _ = reference.canonical_report(built)
        texts.append(text)
    if len(set(texts)) != 1:
        errors.append("three fresh report builds differ")
    if texts and texts[0].encode("ascii") != REPORT.read_bytes():
        errors.append("fresh build does not match report.json")
    contract_texts = [reference.canonical_text(reference.build_contract())
                      for _ in range(3)]
    if len(set(contract_texts)) != 1:
        errors.append("three fresh contract builds differ")
    if contract_texts and contract_texts[0].encode(
            "ascii") != CONTRACT.read_bytes():
        errors.append("fresh contract build does not match contract.json")


def check_readme(errors: List[str], report: Dict[str, Any]) -> None:
    try:
        text = README.read_text(encoding="utf-8")
    except OSError as error:
        errors.append("README missing: " + str(error))
        return
    try:
        counts = reference.verify_readme_digests(text)
    except ValueError as error:
        errors.append("readme_digest_table:" + str(error))
        counts = {}
    for section, count in counts.items():
        if count <= 0:
            errors.append("empty README digest table: " + section)
    for token in ("DEFER", "incomplete", "not_qualified", "RG-01", "RG-08",
                  "not librosa", "ISC", "3.12.16",
                  "scope_base_unavailable", "base_out_of_scope_change",
                  reference.BASE_COMMIT, reference.TASK):
        if token not in text:
            errors.append("README is missing token: " + token)


def check_licensing(errors: List[str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
        if SPDX_LICENSE not in head or SPDX_COPYRIGHT not in head:
            errors.append("missing SPDX header: " + path.name)
    readme_head = "\n".join(README.read_text(encoding="utf-8").splitlines()[:4])
    if SPDX_LICENSE not in readme_head or SPDX_COPYRIGHT not in readme_head:
        errors.append("README.md is missing its SPDX header")
    for name in SIDECARS:
        path = HERE / name
        if not path.is_file():
            errors.append("missing license sidecar: " + name)
            continue
        content = path.read_text(encoding="utf-8")
        if SPDX_LICENSE not in content or SPDX_COPYRIGHT not in content:
            errors.append("invalid license sidecar: " + name)
    reuse = (reference.SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or (
            'SPDX' '-License-Identifier = "Apache-2.0"') not in reuse:
        errors.append("REUSE.toml no longer covers docs/** as Apache-2.0")


def check_files(errors: List[str]) -> None:
    actual = {path.name for path in HERE.iterdir() if path.is_file()}
    if actual != reference.EXPECTED_DIR_FILES:
        for name in sorted(actual - reference.EXPECTED_DIR_FILES):
            errors.append("unexpected task file: " + name)
        for name in sorted(reference.EXPECTED_DIR_FILES - actual):
            errors.append("expected task file missing: " + name)
    if [path.name for path in HERE.iterdir() if path.is_dir()]:
        errors.append("unexpected task subdirectory")
    if any(HERE.rglob("__pycache__")) or any(HERE.rglob("*.pyc")):
        errors.append("bytecode cache present")
    for path in HERE.iterdir():
        if path.is_symlink():
            errors.append("task symlink: " + path.name)
        if path.suffix.lower() in reference.FORBIDDEN_SUFFIXES:
            errors.append("forbidden artifact: " + path.name)
        if path.is_file() and path.name in {
                "provider.json", "adapter.json", "asset.json", "LICENSE",
                "LICENSE.txt", "COPYING", "NOTICE"}:
            errors.append("provider or vendored license artifact: "
                          + path.name)


def check_tests(errors: List[str]) -> int:
    text = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = sum(1 for line in text.splitlines()
                if line.startswith("    def test_"))
    if count < 20:
        errors.append("fewer_than_20_reference_tests:" + str(count))
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1", PYTHONHASHSEED="0")
    process = subprocess.run(
        [sys.executable, "-m", "unittest", "-q", "test_reference.py"],
        cwd=HERE, capture_output=True, text=True, env=env, timeout=300)
    if process.returncode != 0:
        errors.append("test_suite_failed:" +
                      (process.stderr.strip() or process.stdout.strip()))
    return count


def check_scope(errors: List[str]) -> List[str]:
    status = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
         "--untracked-files=all"],
        capture_output=True, text=True)
    if status.returncode != 0:
        errors.append("git_status_failed:" + status.stderr.strip())
        return []
    changed: List[str] = []
    for line in status.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if not path:
            continue
        changed.append(path)
        if not path.startswith(reference.TASK_PREFIX):
            errors.append("out_of_scope_change:" + path)
    for arguments in (["diff", "--check"], ["diff", "--cached", "--check"]):
        diff = subprocess.run(["git", "-C", str(SDK_ROOT), *arguments],
                              capture_output=True, text=True)
        if diff.returncode != 0 or diff.stdout.strip():
            errors.append("git_" + "_".join(arguments).replace("--", "")
                          + "_failed:" + diff.stdout.strip())
    ancestor = subprocess.run(
        ["git", "-C", str(SDK_ROOT), "merge-base", "--is-ancestor",
         reference.BASE_COMMIT, "HEAD"], capture_output=True, text=True)
    if ancestor.returncode != 0:
        errors.append("base_commit_not_ancestor")
    base = reference.scope_base(SDK_ROOT)
    if base is None:
        errors.append("scope_base_unavailable")
    else:
        try:
            base_paths = reference.scope_changed_paths(SDK_ROOT, base)
        except ValueError as error:
            errors.append(str(error))
        else:
            for path in reference.scope_violations(base_paths):
                errors.append("base_out_of_scope_change:" + path)
    return changed


def main() -> int:
    errors: List[str] = []
    check_interpreter(errors)
    loaded = check_json_files(errors)
    report = loaded.get("report", {})
    contract = loaded.get("contract", {})
    pin_count = check_pins(errors)
    check_report(errors, report)
    check_contract(errors, contract, report)
    if report and contract:
        check_board(errors, report, contract)
    check_repeats(errors, report)
    check_readme(errors, report)
    check_licensing(errors)
    check_files(errors)
    test_count = check_tests(errors)
    changed = check_scope(errors)
    if errors:
        for error in errors:
            print("FAIL: " + error)
        return 1
    print(f"pins_ok={pin_count} json_ok=2 report_sha256="
          f"{reference.sha256_file(REPORT)} repeats_ok=3 tests_ok="
          f"{test_count} licensing_ok=1 scope_ok=1 changed_files="
          f"{len(changed)}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
