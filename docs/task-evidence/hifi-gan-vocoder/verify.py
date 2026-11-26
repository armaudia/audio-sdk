# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local HiFi-GAN evidence package.

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
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SIDECAR = f"{SPDX_C}\n{SPDX_L}\n"
SIDECAR_FILES = (
    "contract.json.license",
    "report.json.license",
    "report.json.sha256.license",
    "SOURCES.sha256.license",
)
EXPECTED_GATES = {
    "exact_asset_identity",
    "runtime_admission",
    "artifact_rights",
    "exact_reference_parity",
    "rights_cleared_voice_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}
EXPECTED_REASONS = [
    "source_and_identity_unpinned",
    "weights_not_supplied",
    "runtime_unpinned",
    "license_terms_unresolved",
    "consent_not_recorded",
    "voice_task_fit_out_of_scope",
    "redistribution_rights_unknown",
]
CLAIM_KEYS = tuple(reference.CLAIMS)
BOUNDARY_FALSE_KEYS = tuple(
    key for key, value in reference.BOUNDARY.items() if value is False
)
FORBIDDEN_SOURCE_TOKENS = (
    "import " + "requests",
    "import " + "urllib",
    "import " + "socket",
    "url" + "open",
    "url" + "retrieve",
    "pip " + "install",
)
REQUIRED_README_PHRASES = (
    "DEFER",
    "not_qualified",
    "incomplete",
    "eight",
    "caller-supplied",
    "no candidate",
    "blocked",
    "consent",
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

    report: dict = {}
    contract: dict = {}
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
        if report.get("mode") != "research-control":
            fail("report mode drift")
        if report.get("verification_profile") != "voice":
            fail("report profile drift")
        if report.get("decision") != "DEFER":
            fail("decision is not DEFER")
        if report.get("defer_before") != "processor_exposure":
            fail("defer_before drift")
        if report.get("status") != "proposal_only_incomplete":
            fail("status is not proposal-only incomplete")
        if report.get("evidence_status") != "incomplete":
            fail("evidence_status is not incomplete")
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
        for key in BOUNDARY_FALSE_KEYS:
            if report.get("boundary", {}).get(key) is not False:
                fail("boundary flag promoted or missing: " + key)
        if report.get("boundary", {}).get("installed_v0_geometry_preserved") is not True:
            fail("installed v0 geometry flag missing")
        asset = report.get("asset_boundary", {}).get("asset", {})
        if asset.get("asset_id") != reference.ASSET_ID:
            fail("asset ID drift")
        if asset.get("byte_count") is not None or asset.get("sha256") is not None:
            fail("unpinned HiFi-GAN identity was given a byte count or digest")
        if asset.get("pinned") is not False:
            fail("asset identity is not marked unpinned")
        if asset.get("ledger_entry_present") is not False:
            fail("asset ledger entry unexpectedly present")
        if asset.get("rights_entry_present") is not False:
            fail("rights entry unexpectedly present")
        if asset.get("storage") != "external":
            fail("asset storage is not external")
        if asset.get("source_repository") is not None or asset.get("source_revision") is not None:
            fail("unpinned source was given a repository or revision")
        if asset.get("runtime_package") is not None or asset.get("runtime_wheel_sha256") is not None:
            fail("unpinned runtime was given a package or digest")
        if asset.get("bytes_present_in_sdk_worktree") is not False:
            fail("candidate asset unexpectedly present in SDK worktree")
        if asset.get("asset_bytes_read") is not False or asset.get("digest_recomputed") is not False:
            fail("asset bytes were read or hashed")
        if any(asset.get("workspace_probes", {}).values()):
            fail("a fixed source/asset probe is unexpectedly present")
        if any(asset.get("home_probes", {}).values()):
            fail("a fixed home-cache probe is unexpectedly present")
        copies = asset.get("workspace_copies", [])
        if len(copies) != len(reference.OBSERVED_COPIES):
            fail("observed workspace copy count drift")
        for copy in copies:
            if copy.get("present") is not True:
                fail("observed workspace copy disappeared: " + str(copy.get("path")))
            if copy.get("exact_upstream") is not False:
                fail("derived workspace copy claimed exact upstream: " + str(copy.get("path")))
            if copy.get("admitted") is not False:
                fail("derived workspace copy admitted: " + str(copy.get("path")))
            if copy.get("weights_present") is not False:
                fail("candidate weight unexpectedly present in copy: " + str(copy.get("path")))
        observations = report.get("workspace_observations", {})
        if observations.get("exact_official_source_present") is not False:
            fail("exact official source unexpectedly present")
        if observations.get("admitted_copy_count") != 0:
            fail("a workspace copy is admitted")
        admission = report.get("asset_admission", {})
        if admission.get("status") != "blocked":
            fail("asset admission is not blocked")
        if admission.get("reason_codes") != EXPECTED_REASONS:
            fail("asset admission reason codes drift")
        if admission.get("download_attempted") is not False:
            fail("download attempt recorded")
        if admission.get("model_runtime_invoked") is not False:
            fail("model runtime invocation recorded")
        if admission.get("vocoder_invoked") is not False:
            fail("vocoder invocation recorded")
        if admission.get("qualification_effect") != "none":
            fail("asset admission has a qualification effect")
        rights = report.get("rights", {})
        if rights.get("entry_present") is not False:
            fail("rights entry unexpectedly present")
        for scope_name in ("acquisition", "evaluation", "redistribution", "customer_deployment", "public_playback"):
            if rights.get(scope_name) != "unknown":
                fail("rights scope unexpectedly cleared: " + scope_name)
        if rights.get("consent") != "not_recorded":
            fail("consent scope drift")
        if rights.get("speaker_reference_permission") != "unknown":
            fail("speaker reference permission drift")
        if rights.get("output_use") != "unknown":
            fail("output use drift")
        if rights.get("evaluation_only") is not False or rights.get("packaging_permitted") is not False:
            fail("rights boundary drift")
        native = report.get("native_evidence", {})
        if native.get("model_parity") != "not_available" or native.get("model_quality") != "not_assessed":
            fail("native evidence overclaims parity or quality")
        if native.get("used_for_qualification") is not False:
            fail("native evidence used for qualification")
        interface = report.get("reference_interface", {})
        if interface.get("model_bytes_read") is not False:
            fail("reference interface claims model bytes were read")
        if interface.get("candidate_geometry_known") is not False:
            fail("candidate geometry unexpectedly claimed")
        for key in ("candidate_sample_rate_hz", "candidate_hop_samples", "candidate_window",
                    "candidate_feature_contract", "candidate_upsample_layout",
                    "candidate_state_layout"):
            if interface.get(key) is not None:
                fail("candidate geometry field unexpectedly set: " + key)
        if interface.get("surrogate_fixture", {}).get("hop_samples") != reference.SURROGATE_HOP_SAMPLES:
            fail("surrogate hop drift")
        control = report.get("research_control", {})
        if control.get("inventory_record") != reference.INVENTORY_RECORD_ID:
            fail("research-control inventory record drift")
        if control.get("candidate_matrix_record") != 53 or control.get("candidate_matrix_line") != 54:
            fail("research-control census record/line drift")
        if control.get("record_status") != "out of scope":
            fail("research-control status drift")
        if "do not independently transform" not in str(control.get("finding")):
            fail("research-control finding drift")
        if control.get("comparison_retained") is not False or control.get("comparison_reproduced") is not False:
            fail("research-control comparison unexpectedly retained or reproduced")
        if control.get("proceed_defer") != "DEFER":
            fail("research-control decision is not DEFER")
        if not control.get("required_for_proceed"):
            fail("research-control proceed requirements missing")
        if report.get("controls", {}).get("variant_count") != 5:
            fail("control variant count drift")
        if report.get("counts", {}).get("release_gates_blocked") != 8:
            fail("blocked gate count drift")
        identity = report.get("task_identity", {})
        if identity.get("stable_sha256") != reference.stable_identity_digest(identity):
            fail("stable task identity digest mismatch")
        for key in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            if key in identity:
                fail("mutable board field in stable identity: " + key)
        if identity.get("board_full_file_hashed") is not False:
            fail("board full-file hashing is not disabled")
        pins = report.get("pins", {})
        if pins.get("board_file_pinned") is not False:
            fail("board file is pinned")
        if "plan/swarm/TASKS.json" in json.dumps(pins):
            fail("mutable board path appears in pins")
        if report.get("streaming_semantics", {}).get("drain_within_bounds") is not True:
            fail("streaming drain bounds violated")
        if report.get("streaming_semantics", {}).get("v0_frame_adapter_implemented") is not False:
            fail("v0 frame adapter unexpectedly claimed")
        voice = report.get("voice_profile", {})
        if voice.get("profile") != "voice":
            fail("voice profile name drift")
        if voice.get("candidate_result_present") is not False:
            fail("voice candidate result unexpectedly present")
        if voice.get("synthetic_only") is not True:
            fail("voice profile is not synthetic-only")
        if voice.get("task_fit") != "out_of_scope_vocoder_only":
            fail("voice task-fit finding drift")
        if voice.get("consent") != "not_recorded":
            fail("voice consent unexpectedly recorded")
        if voice.get("permitted_reference_input") != "absent":
            fail("permitted voice reference unexpectedly present")
        for key in ("semantic_preservation", "speaker_identity_similarity", "naturalness",
                    "first_output_tail_timing"):
            if voice.get(key) != "blocked_unmeasured":
                fail("voice outcome unexpectedly measured: " + key)
        if voice.get("listening") != "not_run":
            fail("voice listening unexpectedly run")
        if voice.get("output_use") != "blocked":
            fail("voice output use unexpectedly cleared")
        if voice.get("real_runtime") is not False:
            fail("voice real runtime unexpectedly claimed")

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
        if contract.get("mode") != "research-control":
            fail("contract mode drift")
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
        if contract.get("artifact_pins") != cli.contract_pins():
            fail("contract artifact pins stale")
        if "contract.json" in contract.get("artifact_pins", {}):
            fail("contract pins itself")
        if "README.md" not in contract.get("artifact_pins", {}):
            fail("contract does not pin README.md")
        if set(contract.get("artifact_pins", {})) != set(reference.LOCAL_FILES) - {"contract.json"}:
            fail("contract artifact pin set drift")
        for name in reference.SOURCE_PINS:
            if (reference.SOURCE_ROOT / name).is_file():
                if reference.sha256_file(reference.SOURCE_ROOT / name) != reference.SOURCE_PINS[name]:
                    fail("source pin stale: " + name)
            else:
                fail("source pin file missing: " + name)
        for name, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / name
            if not path.is_file() or path.is_symlink():
                fail("boundary pin file missing: " + name)
            elif reference.sha256_file(path) != digest:
                fail("boundary pin stale: " + name)

    if report:
        if cli.report_bytes() != (HERE / "report.json").read_bytes():
            fail("report.json is not the deterministic regeneration")
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        if sidecar != f"{digest}  report.json\n":
            fail("report.json.sha256 stale")
    if contract:
        if cli.contract_bytes(cli.contract_pins()) != (HERE / "contract.json").read_bytes():
            fail("contract.json is not the deterministic regeneration")
    try:
        if cli.manifest_bytes() != (HERE / "SOURCES.sha256").read_bytes():
            fail("SOURCES.sha256 is stale")
    except Exception as exc:  # noqa: BLE001
        fail(f"manifest regeneration failed: {exc}")

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
    print("report_sha256=" + digest)
    print("report_bytes=" + str(len((HERE / "report.json").read_bytes())))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
