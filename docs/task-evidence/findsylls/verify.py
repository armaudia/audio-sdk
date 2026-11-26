# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local findsylls evidence package.

Every check fails closed: stale pins, duplicate JSON keys, nonfinite JSON
constants, noncanonical regeneration, disposition drift, promoted results, a
stale README digest table, licensing gaps and changes outside this directory
are hard failures.
"""

from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any, List

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX-License-" "Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_upstream_source_and_license",
    "isolated_runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "syllable_ground_truth_quality",
    "rate_profile_qualification",
    "target_runtime_timing_and_memory",
    "provider_intake_and_default_selection",
}
CLAIM_KEYS = tuple(reference.CLAIMS)
FORBIDDEN_SOURCE_TOKENS = (
    "import " + "requests",
    "import " + "urllib",
    "import " + "socket",
    "url" + "open",
    "url" + "retrieve",
    "pip " + "install",
    "subprocess" + ".run([\"git\", \"clone\"",
)
REQUIRED_README_PHRASES = (
    "DEFER",
    "not_qualified",
    "incomplete",
    "eight",
    "blocked",
    "no candidate",
    "offline",
    "evaluation",
    "caller-supplied",
)


def _no_duplicates(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate JSON key: " + key)
        seen.add(key)
    return dict(pairs)


def _reject_constant(token: str):
    raise ValueError("nonfinite JSON constant: " + token)


def load_strict(path: Path) -> Any:
    text = path.read_text(encoding="ascii")
    value = json.loads(text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant)
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError("JSON file must end with exactly one newline: " + str(path.name))
    return value


def check() -> List[str]:
    problems: List[str] = []

    def fail(message: str) -> None:
        problems.append(message)

    expected_files = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    present = {
        path.relative_to(HERE).as_posix()
        for path in HERE.rglob("*")
        if path.is_file() and "__pycache__" not in path.parts
    }
    for name in sorted(expected_files - present):
        fail("expected file missing: " + name)
    for name in sorted(present - expected_files):
        fail("file outside fail-closed local set: " + name)
    for path in HERE.rglob("*"):
        if "__pycache__" in path.parts:
            fail("bytecode cache present: " + path.relative_to(HERE).as_posix())

    report: Any = {}
    contract: Any = {}
    try:
        report = load_strict(HERE / "report.json")
    except Exception as exc:  # noqa: BLE001 - fail closed with the exact reason
        fail(f"report.json invalid: {exc}")
    try:
        contract = load_strict(HERE / "contract.json")
    except Exception as exc:  # noqa: BLE001
        fail(f"contract.json invalid: {exc}")

    if report:
        if report.get("schema_id") != reference.SCHEMA_ID:
            fail("report schema_id drift")
        if report.get("task") != reference.TASK or report.get("component") != reference.SLUG:
            fail("report task/component drift")
        if report.get("verification_profile") != "rate":
            fail("report profile drift")
        if report.get("decision") != "DEFER":
            fail("decision is not DEFER")
        if report.get("defer_before") != "processor_exposure":
            fail("defer_before drift")
        if report.get("status") != "proposal_only_incomplete":
            fail("status is not proposal-only incomplete")
        if report.get("evidence_status") != "incomplete":
            fail("evidence_status is not incomplete")
        if report.get("proposal_only") is not True or report.get("incomplete") is not True:
            fail("proposal_only/incomplete flags drift")
        qualification = report.get("qualification", {})
        if qualification.get("status") != "not_qualified" or qualification.get("qualified") is not False:
            fail("qualification status is not not_qualified")
        if qualification.get("missing_result_may_qualify") is not False:
            fail("a missing result may not qualify")
        gates = report.get("release_gates", [])
        if len(gates) != 8 or report.get("release_gate_count") != 8:
            fail("release gate count is not exactly eight")
        if {gate.get("name") for gate in gates} != EXPECTED_GATES:
            fail("release gate names drift")
        for gate in gates:
            if gate.get("status") != "blocked":
                fail("release gate not blocked: " + str(gate.get("name")))
            if not gate.get("evidence") or not gate.get("reopen"):
                fail("release gate lacks evidence/reopen: " + str(gate.get("name")))
        for key in CLAIM_KEYS:
            if report.get("claims", {}).get(key) is not False:
                fail("claim promoted or missing: " + key)
        for key, value in report.get("boundary", {}).items():
            if key == "installed_v0_geometry_preserved":
                if value is not True:
                    fail("installed v0 geometry flag missing")
            elif value is not False:
                fail("boundary flag promoted: " + key)
        candidate = report.get("candidate_status", {})
        if candidate.get("source_present") is not False:
            fail("candidate source unexpectedly present")
        if candidate.get("implementation_present") is not False:
            fail("candidate implementation unexpectedly present")
        if candidate.get("pinned_revision") is not None or candidate.get("source_sha256") is not None:
            fail("candidate identity unexpectedly pinned")
        if candidate.get("reported_offline_whole_utterance") is not True:
            fail("candidate offline scope drift")
        if candidate.get("reported_streaming") is not False:
            fail("candidate streaming overclaim")
        if candidate.get("workspace_probes_present") != []:
            fail("unexpected candidate workspace probe")
        reference_status = report.get("reference_evidence", {})
        if reference_status.get("status") != "blocked":
            fail("reference evidence is not blocked")
        if reference_status.get("surrogate_is_candidate") is not False:
            fail("surrogate claimed as candidate")
        if reference_status.get("exact_numeric_output_present") is not False:
            fail("candidate numeric output unexpectedly present")
        rights = report.get("rights", {})
        if rights.get("license_text_staged") is not False:
            fail("licence text unexpectedly staged")
        if rights.get("commercial_use_permitted") is not False:
            fail("commercial use unexpectedly permitted")
        if rights.get("redistribution_permitted") is not False:
            fail("redistribution unexpectedly permitted")
        if rights.get("qualifies") is not False or rights.get("status") != "unverified":
            fail("rights status drift")
        if report.get("artifact_admission", {}).get("status") != "blocked":
            fail("absent artifact admission is not blocked")
        if report.get("artifact_admission", {}).get("qualification_effect") != "none":
            fail("absent artifact admission has a qualification effect")
        if report.get("artifact_admission", {}).get("imported") is not False:
            fail("candidate artifact import recorded")
        if report.get("artifact_admission", {}).get("executed") is not False:
            fail("candidate artifact execution recorded")
        if report.get("artifact_admission", {}).get("download_attempted") is not False:
            fail("download attempt recorded")
        profile = report.get("rate_profile", {})
        if profile.get("profile") != "rate":
            fail("rate profile label drift")
        if profile.get("qualifies") is not False:
            fail("rate profile unexpectedly qualifies")
        if profile.get("rate_case_count") != 21:
            fail("rate case count drift")
        if any(profile.get("measured", {}).values()):
            fail("an unmeasured rate metric is marked measured")
        for name, requirement in profile.get("requirements", {}).items():
            if requirement.get("status") not in (
                "synthetic_only",
                "fixture_accounting_only",
                "blocked",
                "not_applicable",
                "not_run",
            ):
                fail("unexpected rate requirement status: " + name)
        for name in ("pitch", "transient_audibility", "speech_preservation", "device_timing", "benchmark"):
            if profile.get("requirements", {}).get(name, {}).get("status") != "blocked":
                fail("rate requirement is not blocked: " + name)
        results = report.get("rate_results", {})
        if results.get("condition_count") != 7 or results.get("rate_case_count") != 21:
            fail("rate result counts drift")
        if set(results.get("conditions", {})) != set(reference.CONDITIONS):
            fail("rate condition set drift")
        for condition in results.get("conditions", {}).values():
            if set(condition.get("rates", {})) != set(reference.RATE_LABELS):
                fail("rate label set drift")
            for case in condition.get("rates", {}).values():
                if case.get("target_output_samples") != case.get("computed_output_samples"):
                    fail("rate target/computed mismatch")
                for flag in (
                    "renderer_executed",
                    "duration_measured",
                    "pitch_measured",
                    "transient_audibility_measured",
                    "playback_buffering_measured",
                    "device_timing_measured",
                    "listening",
                ):
                    if case.get(flag) is not False:
                        fail("rate case measured flag promoted: " + flag)
        controls = report.get("controls", {})
        if controls.get("identity_echo_exact") is not True:
            fail("identity control failed")
        if controls.get("target_duration_exact") is not True:
            fail("target duration control failed")
        if controls.get("silence_zero_nuclei") is not True:
            fail("silence control failed")
        if controls.get("constant_count_control", {}).get("constant") != 20:
            fail("constant count control drift")
        if controls.get("nonzero_mapping_remainders") != {"tail_partial:4/5": 1, "tail_partial:5/4": 3}:
            fail("mapping remainder control drift")
        adverse = report.get("adverse", {})
        if adverse.get("nonfinite_and_invalid_rejected") is not True:
            fail("nonfinite/invalid rejection not proven")
        if adverse.get("source_absent_blocked") is not True:
            fail("absent source not blocked")
        if adverse.get("config_rejections", 0) < 15:
            fail("config rejection coverage too small")
        if adverse.get("slot_rejections", 0) < 10:
            fail("slot rejection coverage too small")
        if adverse.get("artifact_rejections", 0) < 5:
            fail("artifact rejection coverage too small")
        state = report.get("state", {})
        for flag in ("deterministic_fixture_digest", "deterministic_mapping", "silence_has_undefined_rate"):
            if state.get(flag) is not True:
                fail("state flag missing: " + flag)
        if state.get("valid_control_accepted") is not True:
            fail("valid config control missing")
        if state.get("valid_slot_control_accepted") is not True:
            fail("valid slot control missing")
        identity = report.get("task_identity", {})
        if identity.get("stable_sha256") != reference.stable_identity_digest(identity):
            fail("stable task identity digest mismatch")
        for key in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            if key in identity:
                fail("mutable board field in stable identity: " + key)
        if identity.get("board_full_file_hashed") is not False:
            fail("board full-file hashing is not disabled")
        pins = report.get("pins", {})
        if pins.get("board_file_pinned") is not False or pins.get("board_full_file_hashed") is not False:
            fail("board file pin policy drift")
        if "plan/swarm/TASKS.json" in json.dumps(pins):
            fail("mutable board path appears in report pins")
        if pins.get("source") != reference.SOURCE_PINS:
            fail("report source pins drift")
        if pins.get("boundary") != reference.BOUNDARY_PINS:
            fail("report boundary pins drift")
        if report.get("counts", {}).get("release_gates_blocked") != 8:
            fail("blocked gate count drift")

    if contract:
        if contract.get("schema_id") != reference.CONTRACT_SCHEMA_ID:
            fail("contract schema_id drift")
        if contract.get("decision") != "DEFER":
            fail("contract decision is not DEFER")
        if contract.get("status") != "proposal_only_incomplete":
            fail("contract status drift")
        if contract.get("evidence_status") != "incomplete":
            fail("contract evidence_status drift")
        if contract.get("qualification_status") != "not_qualified":
            fail("contract qualification_status drift")
        if contract.get("qualified") is not False:
            fail("contract qualified is not false")
        if contract.get("proposal_only") is not True or contract.get("incomplete") is not True:
            fail("contract proposal/incomplete flags drift")
        if contract.get("verification_profile") != "rate":
            fail("contract profile drift")
        gates = contract.get("release_gates", [])
        if len(gates) != 8 or contract.get("release_gate_count") != 8:
            fail("contract gate count is not exactly eight")
        if {gate.get("name") for gate in gates} != EXPECTED_GATES:
            fail("contract gate names drift")
        if any(gate.get("status") != "blocked" for gate in gates):
            fail("contract gate not blocked")
        board = contract.get("board_policy", {})
        if board.get("full_file_hashed") is not False or board.get("stable_fields_only") is not True:
            fail("contract board policy drift")
        if "contract.json" in contract.get("artifact_pins", {}):
            fail("contract pins itself")
        if "README.md" not in contract.get("artifact_pins", {}):
            fail("contract does not pin README.md")
        if set(contract.get("artifact_pins", {})) != set(reference.LOCAL_FILES) - {"contract.json"}:
            fail("contract artifact pin set drift")
        for name in reference.SOURCE_PINS:
            path = reference.SOURCE_ROOT / name
            if path.is_file():
                if reference.sha256_file(path) != reference.SOURCE_PINS[name]:
                    fail("source pin stale: " + name)
            else:
                fail("source pin file missing: " + name)
        for name, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / name
            if not path.is_file() or path.is_symlink():
                fail("boundary pin file missing: " + name)
            elif reference.sha256_file(path) != digest:
                fail("boundary pin stale: " + name)

    generated: Any = {}
    try:
        generated = cli.generate_thrice()
    except Exception as exc:  # noqa: BLE001
        fail(f"three-generation build failed: {exc}")
    if generated:
        for name, payload in generated.items():
            if (HERE / name).read_bytes() != payload:
                fail("artifact is not the deterministic three-run regeneration: " + name)
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        if sidecar != f"{digest}  report.json\n":
            fail("report.json.sha256 stale")

    try:
        text = (HERE / "README.md").read_text(encoding="utf-8")
        for phrase in REQUIRED_README_PHRASES:
            if phrase not in text:
                fail("README missing required phrase: " + phrase)
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split("<!-- DIGEST_TABLE_END -->", 1)[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            if row not in block:
                fail("README digest table stale for " + name)
        for name, digest in reference.SOURCE_PINS.items():
            if digest not in text:
                fail("README missing source pin digest: " + name)
        for name, digest in reference.BOUNDARY_PINS.items():
            if digest not in text:
                fail("README missing boundary pin digest: " + name)
    except Exception as exc:  # noqa: BLE001
        fail(f"README digest table invalid: {exc}")

    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
        if head != ["# " + SPDX_C, "# " + SPDX_L]:
            fail("missing explicit Python SPDX header: " + name)
    head = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
    if head != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
        fail("missing explicit Markdown SPDX header: README.md")
    for name in SIDECAR_FILES:
        if (HERE / name).read_text(encoding="utf-8") != SIDECAR:
            fail("invalid or missing SPDX sidecar: " + name)
    reuse = reference.SDK_ROOT / "REUSE.toml"
    if not reuse.is_file() or '"docs/**"' not in reuse.read_text(encoding="utf-8"):
        fail("REUSE.toml docs/** annotation missing")
    if not (reference.SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")

    for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
        text = (HERE / name).read_text(encoding="utf-8")
        for token in FORBIDDEN_SOURCE_TOKENS:
            if token in text:
                fail(f"forbidden network/download token in {name}: {token}")

    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    before = {name: reference.sha256_file(HERE / name) for name in expected_files}
    digests: List[str] = []
    for _ in range(3):
        result = subprocess.run(
            [sys.executable, str(HERE / "run.py"), "--digest"],
            cwd=str(HERE),
            env=env,
            capture_output=True,
            text=True,
            check=False,
        )
        if result.returncode != 0:
            fail("cold-start digest run failed: " + result.stderr.strip())
            break
        digests.append(result.stdout.strip())
    if digests and len(set(digests)) != 1:
        fail("three cold-start regeneration digests differ")
    if digests and digests[0] != (HERE / "report.json.sha256").read_text(encoding="ascii").split()[0]:
        fail("cold-start digest does not match report.json.sha256")

    checked = subprocess.run(
        [sys.executable, str(HERE / "run.py"), "--check"],
        cwd=str(HERE),
        env=env,
        capture_output=True,
        text=True,
        check=False,
    )
    if checked.returncode != 0 or "deterministic=true" not in checked.stdout:
        fail("run.py --check three-generation identity failed: " + checked.stderr.strip())

    after = {name: reference.sha256_file(HERE / name) for name in expected_files}
    if before != after:
        fail("read-only verification mutated evidence files")

    try:
        git = subprocess.run(
            ["git", "-C", str(reference.SDK_ROOT), "status", "--porcelain=v1", "--untracked-files=all"],
            capture_output=True,
            text=True,
            check=False,
        )
        if git.returncode != 0:
            fail("git status unavailable: " + git.stderr.strip())
        else:
            for line in git.stdout.splitlines():
                if not line:
                    continue
                raw = line[3:] if len(line) > 3 else line
                if " -> " in raw:
                    raw = raw.split(" -> ", 1)[1]
                if "__pycache__" in raw or raw.startswith("build/"):
                    continue
                if not raw.startswith(reference.TASK_PREFIX):
                    fail("change outside task evidence directory: " + raw)
    except FileNotFoundError:
        fail("git executable unavailable for scope verification")

    return problems


def main() -> int:
    problems = check()
    if problems:
        print("FAIL")
        for problem in problems:
            print(" - " + problem)
        return 1
    report = load_strict(HERE / "report.json")
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    print("PASS")
    print("decision=" + report["decision"])
    print("status=" + report["status"])
    print("evidence_status=" + report["evidence_status"])
    print("qualification.status=" + report["qualification"]["status"])
    print("release_gates=8 blocked=8")
    print("rate_cases=" + str(report["rate_profile"]["rate_case_count"]))
    print("report_sha256=" + digest)
    print("report_bytes=" + str(len((HERE / "report.json").read_bytes())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
