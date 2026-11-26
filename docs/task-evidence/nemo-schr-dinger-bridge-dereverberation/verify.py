# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the NeMo Schrödinger-bridge package.

Every check fails closed: stale pins, duplicate JSON keys, nonfinite JSON
constants, noncanonical regeneration, disposition drift, promoted results, a
stale README digest table, licensing gaps, mutable-board hashing and changes
outside this directory are hard failures.
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
    "exact_source_checkpoint_and_config_identity",
    "pinned_runtime_and_offline_load",
    "artifact_and_output_rights",
    "whole_utterance_geometry_and_sampler",
    "exact_reference_parity",
    "rights_cleared_paired_cohort",
    "independent_scoring_and_listening",
    "target_timing_and_opt_in_provider",
}
EXPECTED_ASSET_REASONS = [
    "checkpoint_identity_not_verified",
    "license_scope_unresolved",
    "rights_register_entry_absent",
    "runtime_not_pinned",
    "upstream_revision_not_verified",
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
    "rights",
)
BOARD_RELATIVE = "audio-benchmark-platform/plan/swarm/TASKS.json"


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
    text = path.read_text(encoding="utf-8")
    value = json.loads(
        text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant
    )
    if not text.endswith("\n") or text.endswith("\n\n"):
        raise ValueError("JSON file must end with exactly one newline: " + path.name)
    return value


def load_board(path: Path) -> Any:
    """Read the mutable board without hashing it; strict JSON, UTF-8 source."""
    text = path.read_text(encoding="utf-8")
    return json.loads(
        text, object_pairs_hook=_no_duplicates, parse_constant=_reject_constant
    )


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
        if report.get("task") != reference.TASK or report.get("component") != reference.COMPONENT:
            fail("report task/component drift")
        if report.get("mode") != "feasibility":
            fail("report mode drift")
        if report.get("verification_profile") != "room":
            fail("report profile drift")
        if report.get("decision") != "DEFER":
            fail("decision is not DEFER")
        if report.get("defer_before") != "offline_checkpoint_staging_and_asset_admission":
            fail("defer_before drift")
        if report.get("status") != "proposal_only_incomplete":
            fail("status is not proposal-only incomplete")
        if report.get("evidence_status") != "incomplete":
            fail("evidence_status is not incomplete")
        qualification = report.get("qualification", {})
        if (
            qualification.get("status") != "not_qualified"
            or qualification.get("qualified") is not False
            or qualification.get("not_qualified") is not True
        ):
            fail("qualification status is not not_qualified")
        if qualification.get("missing_result_may_qualify") is not False:
            fail("a missing result may qualify")
        if qualification.get("missing_result_promoted") is not False:
            fail("a missing result was promoted")
        if qualification.get("candidate_result_present") is not False:
            fail("a candidate result is unexpectedly present")
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
        if asset.get("asset_id") != "nemo_se_der_sb_16k_small_unpinned":
            fail("asset ID drift")
        if asset.get("byte_count") is not None or asset.get("sha256") is not None:
            fail("unpinned candidate identity was given a byte count or digest")
        if asset.get("pinned") is not False:
            fail("asset identity is not marked unpinned")
        if asset.get("ledger_entry_present") is not False:
            fail("asset ledger entry unexpectedly present")
        if asset.get("rights_entry_present") is not False:
            fail("rights entry unexpectedly present")
        if asset.get("storage") != "external":
            fail("asset storage is not external")
        if asset.get("source_revision") is not None:
            fail("unpinned source was given a revision")
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
        if len(copies) != 1:
            fail("observed adapter copy count drift")
        for copy in copies:
            if copy.get("present") is not True:
                fail("observed adapter README disappeared")
            if copy.get("admitted") is not False:
                fail("adapter README admitted as a candidate artifact")
            if copy.get("exact_candidate") is not False:
                fail("adapter README claimed exact candidate identity")
            if copy.get("weights_present") is not False:
                fail("adapter README unexpectedly has weights")
            path = reference.SOURCE_ROOT / str(copy.get("path"))
            if not path.is_file() or reference.sha256_file(path) != copy.get("sha256"):
                fail("adapter README digest drift")
        observations = report.get("native_evidence", {})
        if observations.get("candidate_native_reference_present") is not False:
            fail("candidate native reference unexpectedly present")
        if observations.get("model_parity") != "not_available":
            fail("native evidence overclaims parity")
        if observations.get("model_quality") != "not_assessed":
            fail("native evidence overclaims quality")
        if observations.get("used_for_qualification") is not False:
            fail("native evidence used for qualification")
        audit = report.get("absence_audit", {})
        if audit.get("all_absence_probes_absent") is not True:
            fail("an absence probe is unexpectedly present")
        for key in (
            "source_checkout_present",
            "weights_present",
            "runtime_present",
            "runtime_lock_present",
            "license_record_present",
            "rights_record_present",
            "cohort_manifest_present",
            "parity_manifest_present",
            "download_performed",
            "network_used",
        ):
            if audit.get(key) is not False:
                fail("absence audit flag drift: " + key)
        for key, value in audit.get("fixed_probes", {}).items():
            if value is not False:
                fail("fixed absence probe unexpectedly present: " + key)
        for key, value in audit.get("home_probes", {}).items():
            if value is not False:
                fail("home absence probe unexpectedly present: " + key)
        admission = report.get("asset_boundary", {}).get("asset_admission", {})
        if admission.get("status") != "blocked":
            fail("asset admission is not blocked")
        if admission.get("reason_codes") != EXPECTED_ASSET_REASONS:
            fail("asset admission reason codes drift")
        if admission.get("download_attempted") is not False:
            fail("download attempt recorded")
        if admission.get("model_runtime_invoked") is not False:
            fail("model runtime invocation recorded")
        if admission.get("qualification_effect") != "none":
            fail("asset admission has a qualification effect")
        rights = report.get("rights", {})
        if rights.get("entry_present") is not False:
            fail("rights entry unexpectedly present")
        for scope_name in (
            "acquisition",
            "evaluation",
            "redistribution",
            "customer_deployment",
            "public_playback",
            "output_use",
        ):
            if rights.get(scope_name) != "unknown":
                fail("rights scope unexpectedly cleared: " + scope_name)
        if rights.get("license_review") != "upstream_reported_not_reviewed":
            fail("rights license review drift")
        if rights.get("noncommercial") is not True or rights.get("share_alike") is not True:
            fail("reported noncommercial share-alike terms were promoted")
        if rights.get("blocked") is not True:
            fail("rights are not blocked")
        if rights.get("evaluation_only") is not False or rights.get("packaging_permitted") is not False:
            fail("rights boundary drift")
        interface = report.get("reference_interface", {})
        if interface.get("model_bytes_read") is not False:
            fail("reference interface claims model bytes were read")
        if interface.get("candidate_geometry_known") is not False:
            fail("candidate geometry unexpectedly claimed")
        for key in (
            "candidate_accepts_arbitrary_length",
            "candidate_algorithmic_latency_samples",
            "candidate_config",
            "candidate_frame_geometry",
            "candidate_hop_samples",
            "candidate_sampler",
            "candidate_sampler_steps",
            "candidate_seed_behaviour",
            "candidate_solver",
        ):
            if interface.get(key) is not None:
                fail("candidate geometry field unexpectedly set: " + key)
        if interface.get("candidate_sample_rate_hz") != 16000:
            fail("candidate sample rate drift")
        if interface.get("candidate_channels") != 1:
            fail("candidate channel count drift")
        if interface.get("candidate_streaming_api") is not False:
            fail("candidate streaming API unexpectedly claimed")
        if interface.get("surrogate_fixture", {}).get("samples") != reference.FIXTURE_SAMPLES:
            fail("surrogate fixture length drift")
        feasibility = report.get("feasibility", {})
        if feasibility.get("inventory_record") != reference.INVENTORY_RECORD_ID:
            fail("feasibility inventory record drift")
        if feasibility.get("inventory_disposition") != "sdk-model":
            fail("feasibility disposition drift")
        if feasibility.get("inventory_evidence_status") != "blocked":
            fail("feasibility evidence status drift")
        if feasibility.get("research_path") != reference.RESEARCH_PATH:
            fail("feasibility research path drift")
        if feasibility.get("research_line") != reference.RESEARCH_LINE:
            fail("feasibility research line drift")
        if "WSJ0-Reverb" not in str(feasibility.get("research_finding")):
            fail("feasibility finding drift")
        if feasibility.get("source_revision_pin_available") is not False:
            fail("source revision unexpectedly pinned")
        if feasibility.get("weights_available") is not False:
            fail("weights unexpectedly available")
        if feasibility.get("runtime_available") is not False:
            fail("runtime unexpectedly available")
        if feasibility.get("matched_evidence_present") is not False:
            fail("matched evidence unexpectedly present")
        if feasibility.get("candidate_run_attempted") is not False:
            fail("candidate run unexpectedly attempted")
        if feasibility.get("comparison_retained") is not False or feasibility.get("comparison_reproduced") is not False:
            fail("comparison unexpectedly retained or reproduced")
        if feasibility.get("proceed_defer") != "DEFER":
            fail("feasibility decision is not DEFER")
        if not feasibility.get("required_for_proceed"):
            fail("feasibility proceed requirements missing")
        if report.get("counts", {}).get("release_gates_blocked") != 8:
            fail("blocked gate count drift")
        if report.get("counts", {}).get("exact_blockers") != len(reference.EXACT_BLOCKERS):
            fail("exact blocker count drift")
        if report.get("controls", {}).get("variant_count") != 3:
            fail("control variant count drift")
        controls = report.get("controls", {})
        for section in ("config_adverse", "input_adverse"):
            values = controls.get(section, {})
            names = [name for name in values if not name.endswith(":expected")]
            if not names:
                fail("missing " + section + " controls")
            for name in names:
                if values.get(name) != values.get(name + ":expected"):
                    fail(section + " control mismatch: " + name)
        asset_controls = controls.get("asset", {})
        if asset_controls.get("synthetic_accepted") is not True:
            fail("synthetic structural control was not accepted")
        if asset_controls.get("candidate_manifest_blocked") is not True:
            fail("candidate manifest was not blocked")
        if asset_controls.get("candidate_rejection_reasons") != EXPECTED_ASSET_REASONS:
            fail("candidate asset rejection reason drift")
        synthetic = asset_controls.get("synthetic_control", {})
        if synthetic.get("candidate_asset") is not False:
            fail("synthetic control claimed candidate identity")
        if synthetic.get("loaded") is not False or synthetic.get("executed") is not False:
            fail("synthetic control was loaded or executed")
        if synthetic.get("qualification_effect") != "none":
            fail("synthetic control has a qualification effect")
        rejection_values = asset_controls.get("rejection_controls", {})
        rejection_names = [
            name for name in rejection_values if not name.endswith(":expected")
        ]
        if len(rejection_names) < 18:
            fail("asset rejection control count drift")
        for name in rejection_names:
            if rejection_values.get(name) != rejection_values.get(name + ":expected"):
                fail("asset rejection control mismatch: " + name)
        stream = report.get("streaming_semantics", {})
        if stream.get("candidate_streaming_api") is not False:
            fail("streaming API unexpectedly claimed")
        if stream.get("chunked_input_rejected") is not True:
            fail("chunked input was not rejected")
        if stream.get("partial_input_rejected") is not True:
            fail("partial input was not rejected")
        if stream.get("full_clip_only") is not True:
            fail("full-clip-only boundary missing")
        if stream.get("streaming_claimed") is not False:
            fail("streaming claimed")
        if stream.get("v0_frame_adapter_implemented") is not False:
            fail("v0 frame adapter unexpectedly claimed")
        results = report.get("results", {})
        if results.get("input_samples") != reference.FIXTURE_SAMPLES:
            fail("surrogate input sample count drift")
        if results.get("one_shot_output_samples") != reference.FIXTURE_SAMPLES:
            fail("surrogate output sample count drift")
        if results.get("output_samples_equal_input") is not True:
            fail("surrogate did not conserve samples")
        if results.get("nonfinite_output_count") != 0:
            fail("surrogate produced nonfinite output")
        if results.get("clipped_output_count") != 0:
            fail("surrogate produced clipped output")
        if results.get("silence_exact_zero") is not True:
            fail("surrogate silence is not exact zero")
        if results.get("deterministic_repeat_equal") is not True:
            fail("surrogate is not deterministic")
        if results.get("stateless_repeat") is not True:
            fail("surrogate is not stateless across repeats")
        if results.get("sampler_modes_differ") is not True:
            fail("surrogate sampler modes were not exercised")
        if results.get("sampler_step_variants_differ") is not True:
            fail("surrogate step variants were not exercised")
        if results.get("max_abs_output", 2.0) >= reference.MAX_ABS_AUDIO:
            fail("surrogate output exceeds the declared bound")
        profile = report.get("acceptance_profile", {})
        if profile.get("profile") != "room":
            fail("acceptance profile drift")
        if profile.get("candidate_qualified") is not False:
            fail("acceptance profile overclaims qualification")
        items = profile.get("items", [])
        if len(items) != 16:
            fail("acceptance profile item count drift")
        if not any(item.get("status") == "blocked" for item in items):
            fail("acceptance profile has no blocked items")
        identity = report.get("task_identity", {})
        if identity.get("stable_sha256") != reference.stable_identity_digest(identity):
            fail("stable task identity digest mismatch")
        for key in reference.MUTABLE_BOARD_FIELDS:
            if key in identity:
                fail("mutable board field in stable identity: " + key)
        if identity.get("board_full_file_hashed") is not False:
            fail("board full-file hashing is not disabled")
        if identity.get("depends_on") != ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"]:
            fail("stable dependency list drift")
        board_row = report.get("board_row", {})
        if board_row.get("full_tasks_json_hashed") is not False:
            fail("board full-file hashing is not disabled in board_row")
        stable_fields = board_row.get("stable_fields", {})
        if set(stable_fields) != set(reference.PROJECTED_BOARD_FIELDS):
            fail("projected board fields drift")
        if reference.stable_row_digest(stable_fields) != board_row.get("stable_sha256"):
            fail("projected board fields digest mismatch")
        pins = report.get("pins", {})
        if pins.get("board_file_pinned") is not False:
            fail("board file is pinned")
        if "plan/swarm/TASKS.json" in json.dumps(pins):
            fail("mutable board path appears in pins")
        context = report.get("source_reported_context", {})
        if context.get("model_id") != "nvidia/se_der_sb_16k_small":
            fail("source context model drift")
        if context.get("reported_license") != "CC-BY-NC-SA-4.0":
            fail("source context license drift")
        if context.get("reported_streaming_api") is not False:
            fail("source context streaming drift")
        if "not local measurements" not in str(context.get("note")):
            fail("source context result overclaim")

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
        if contract.get("proposal_only") is not True:
            fail("contract proposal_only drift")
        if contract.get("mode") != "feasibility":
            fail("contract mode drift")
        gates = contract.get("release_gates", [])
        if len(gates) != 8 or contract.get("release_gate_count") != 8:
            fail("contract gate count is not exactly eight")
        if {gate.get("name") for gate in gates} != EXPECTED_GATES:
            fail("contract gate names drift")
        if any(gate.get("status") != "blocked" for gate in gates):
            fail("contract gate not blocked")
        if any(gate.get("qualifies") is not False for gate in gates):
            fail("contract gate qualifies")
        if contract.get("qualification", {}).get("status") != "not_qualified":
            fail("contract qualification block drift")
        if contract.get("qualification", {}).get("qualified") is not False:
            fail("contract qualified is not false")
        if contract.get("artifact_pins") != cli.contract_pins():
            fail("contract artifact pins stale")
        if "contract.json" in contract.get("artifact_pins", {}):
            fail("contract pins itself")
        if "README.md" not in contract.get("artifact_pins", {}):
            fail("contract does not pin README.md")
        if set(contract.get("artifact_pins", {})) != set(reference.LOCAL_FILES) - {
            "contract.json"
        }:
            fail("contract artifact pin set drift")
        for name in reference.SOURCE_PINS:
            path = reference.SOURCE_ROOT / name
            if not path.is_file():
                fail("source pin file missing: " + name)
            elif reference.sha256_file(path) != reference.SOURCE_PINS[name]:
                fail("source pin stale: " + name)
        for name, digest in reference.BOUNDARY_PINS.items():
            path = reference.SDK_ROOT / name
            if not path.is_file() or path.is_symlink():
                fail("boundary pin file missing: " + name)
            elif reference.sha256_file(path) != digest:
                fail("boundary pin stale: " + name)
        for name, digest in reference.SIBLING_PINS.items():
            path = reference.SDK_ROOT / name
            if not path.is_file() or path.is_symlink():
                fail("sibling pin file missing: " + name)
            elif reference.sha256_file(path) != digest:
                fail("sibling pin stale: " + name)

    # Stable linked-row identity is gated from the live board projection, but the
    # mutable file is never hashed or pinned.
    board_path = reference.SOURCE_ROOT / BOARD_RELATIVE
    if not board_path.is_file():
        fail("task board unavailable for stable linked-row identity check")
    else:
        try:
            board = load_board(board_path)
            rows = [
                row
                for row in board.get("tasks", [])
                if isinstance(row, dict) and row.get("id") == reference.TASK
            ]
            if len(rows) != 1:
                fail("task board does not contain exactly one linked row")
            else:
                projected = reference.project_board_row(rows[0])
                expected = {
                    field: reference.STABLE_TASK_IDENTITY[field]
                    for field in reference.PROJECTED_BOARD_FIELDS
                }
                if {
                    field: projected[field] for field in reference.PROJECTED_BOARD_FIELDS
                } != expected:
                    fail("live board stable linked-row projection drifted")
        except Exception as exc:  # noqa: BLE001 - fail closed
            fail(f"stable board projection failed: {exc}")

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
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split(
            "<!-- DIGEST_TABLE_END -->", 1
        )[0]
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
            [sys.executable, "-B", str(HERE / "run.py"), "--digest"],
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
    if digests and digests[0] != (
        HERE / "report.json.sha256"
    ).read_text(encoding="ascii").split()[0]:
        fail("cold-start digest does not match report.json.sha256")
    after = {name: reference.sha256_file(HERE / name) for name in expected_files}
    if before != after:
        fail("read-only verification mutated evidence files")

    try:
        git = subprocess.run(
            [
                "git",
                "-C",
                str(reference.SDK_ROOT),
                "status",
                "--porcelain=v1",
                "--untracked-files=all",
            ],
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
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
