# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local evidence package.

Usage::

    PYTHONDONTWRITEBYTECODE=1 python3 verify.py

Every check fails closed: missing or extra pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, licensing gaps, a cleared gate, a promoted
missing result or any out-of-scope worktree change are hard failures.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import re
import subprocess
import sys
from pathlib import Path
from typing import Any

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference  # noqa: E402
import run as cli  # noqa: E402

SDK_ROOT = reference.SDK_ROOT
TASK_PREFIX = f"docs/task-evidence/{reference.SLUG}/"
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"
MANIFEST_COMMENT = cli.MANIFEST_COMMENT.rstrip("\n")

CONTRACT_KEYS = {
    SPDX_C, SPDX_L, "schema_id", "contract_version", "task", "component",
    "base_commit", "branch", "reviewer", "profile", "status", "evidence_status",
    "decision", "scope", "public_surface", "boundary", "format",
    "candidate_identity", "runtime_identity", "corpus_identity",
    "caller_asset_boundary", "surrogate_model", "reproduction", "release_gates",
    "qualification", "source_pins", "boundary_pins", "artifact_pins",
    "external_asset_pins",
}
ADAPTER_KEYS = {
    SPDX_C, SPDX_L, "protocol_version", "identity", "boundary_identity",
    "input_kind", "output_kinds", "tasks", "modes", "configuration", "entrypoint",
    "supported_formats", "variants", "controls", "asset_binding", "registration",
    "processor_exposure", "real_runtime_used", "weights_loaded", "corpus_used",
    "registered", "enabled_by_default", "status", "decision",
}
PROVIDER_KEYS = {
    SPDX_C, SPDX_L, "schema_id", "identity", "component", "task", "status",
    "qualification_status", "decision", "registered", "enabled_by_default",
    "opt_in_required", "processor_exposure", "c_abi_or_sdk_default_change",
    "shared_build_or_ci_change", "descriptor_registry_change",
    "installed_v0_behavior_change", "asset_delivery", "real_runtime",
    "weights_loaded", "corpus_used", "note",
}
ENHANCEMENT_KEYS = {
    "profile_source", "paired_clean_reference", "scores", "stoi_scorer", "controls",
    "task_matched_baseline", "clean_preservation", "peaks_and_invalid_outputs",
    "alignment", "state_memory_timing", "unpaired_predictive_screen", "listening",
    "resource", "mechanism_findings",
}
REPORT_KEYS = {
    "schema_id", "task_id", "title", "component", "base_commit", "branch", "profile",
    "family", "status", "evidence_status", "qualification_status", "decision",
    "scope", "boundary", "format", "claims", "evidence_classes",
    "enhancement_profile", "conditions", "controls", "clean_preservation",
    "regression_scan", "adverse", "caller_asset_boundary", "readiness",
    "historical_provenance", "gates", "missing_evidence",
    "no_missing_result_qualifies_candidate", "extra", "source_pin_paths",
    "local_file_names",
}


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("nonfinite number: " + where)
    if isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def strict_json(path: Path) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail("duplicate JSON key in " + path.name + ": " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail("nonfinite JSON constant in " + path.name + ": " + token)

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as error:
        fail("cannot parse " + path.name + ": " + str(error))
    if not isinstance(value, dict):
        fail("JSON root is not an object: " + path.name)
    check_finite(value, path.name)
    return value


def read_manifest() -> dict[str, str]:
    try:
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError) as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    if not lines or lines[0] != MANIFEST_COMMENT:
        fail("SOURCES.sha256 header mismatch")
    result: dict[str, str] = {}
    for line in lines[1:]:
        parts = re.fullmatch(r"([0-9a-f]{64})  ([^\s]+(?:\s[^\s]+)*)", line)
        if parts is None:
            fail("malformed pin line: " + repr(line))
        digest, raw = parts.group(1), parts.group(2)
        if raw in result:
            fail("duplicate pin path: " + raw)
        result[raw] = digest
    return result


def manifest_expected_paths() -> set[str]:
    local = {f"worktree:{TASK_PREFIX}{name}" for name in reference.LOCAL_FILES}
    return set(reference.SOURCE_PIN_PATHS) | set(reference.BOUNDARY_PIN_PATHS) | local


def check_pins(manifest: dict[str, str]) -> None:
    expected = manifest_expected_paths()
    if set(manifest) != expected:
        fail("pin set mismatch: missing=" + str(sorted(expected - set(manifest)))
             + " extra=" + str(sorted(set(manifest) - expected)))
    if "worktree:" + TASK_PREFIX + "SOURCES.sha256" in manifest:
        fail("SOURCES.sha256 must not pin itself")
    for raw, digest in sorted(manifest.items()):
        if raw.startswith("source:"):
            path = reference.SOURCE_ROOT / raw.split(":", 1)[1]
        elif raw.startswith("worktree:"):
            path = SDK_ROOT / raw.split(":", 1)[1]
        else:
            fail("unsupported pin prefix: " + raw)
        if not path.is_file() or path.is_symlink():
            fail("missing or non-regular pin target: " + raw)
        if reference.sha256_file(path) != digest:
            fail("pin mismatch: " + raw)
    print(f"verify: {len(manifest)} source/boundary/artifact pins exact")


def check_contract(contract: dict[str, Any], adapter: dict[str, Any],
                   provider: dict[str, Any], manifest: dict[str, str]) -> None:
    if set(contract) != CONTRACT_KEYS:
        fail("contract key set mismatch: " + str(sorted(set(contract) ^ CONTRACT_KEYS)))
    if set(adapter) != ADAPTER_KEYS:
        fail("adapter key set mismatch: " + str(sorted(set(adapter) ^ ADAPTER_KEYS)))
    if set(provider) != PROVIDER_KEYS:
        fail("provider key set mismatch: " + str(sorted(set(provider) ^ PROVIDER_KEYS)))
    source_pins = {key: value for key, value in manifest.items() if key.startswith("source:")}
    boundary_pins = {key: value for key, value in manifest.items()
                     if key in reference.BOUNDARY_PIN_PATHS}
    local_pins = {key.rsplit("/", 1)[-1]: value for key, value in manifest.items()
                  if key.startswith("worktree:" + TASK_PREFIX)
                  and not key.endswith("/contract.json")}
    if contract["source_pins"] != source_pins:
        fail("contract source pins differ from manifest")
    if contract["boundary_pins"] != boundary_pins:
        fail("contract boundary pins differ from manifest")
    if contract["artifact_pins"] != local_pins:
        fail("contract artifact pins differ from manifest")
    if contract["base_commit"] != reference.BASE_COMMIT or contract["branch"] != reference.BRANCH:
        fail("contract base or branch mismatch")
    if contract["task"] != reference.TASK_ID or contract["component"] != reference.COMPONENT:
        fail("contract task or component mismatch")
    if contract["profile"] != reference.PROFILE or contract["status"] != reference.STATUS:
        fail("contract profile or status mismatch")
    if contract["evidence_status"] != reference.EVIDENCE_STATUS:
        fail("contract evidence status is not incomplete")
    if contract["decision"] != reference.DECISION:
        fail("contract decision is not DEFER")
    if contract["reviewer"] != reference.REVIEWER:
        fail("contract reviewer mismatch")
    qualification = contract["qualification"]
    required = {
        "status": "incomplete", "decision": reference.DECISION, "qualifies": False,
        "missing_result_promoted": False, "processor_exposure": False,
        "real_runtime_used": False, "weights_loaded": False, "corpus_used": False,
        "listening_result_used": False, "release_claim": False,
    }
    if any(qualification.get(key) != value for key, value in required.items()):
        fail("contract qualification is not incomplete/DEFER")
    if any(value is not False for value in contract["public_surface"].values()):
        fail("public surface flag is not false")
    for key, value in reference.BOUNDARY.items():
        if contract["boundary"].get(key) != value:
            fail("contract boundary flag mismatch: " + key)
    if contract["format"] != reference.FORMAT:
        fail("contract v0 geometry mismatch")
    if contract["scope"] != reference.SCOPE:
        fail("contract scope flag mismatch")
    if contract["scope"].get("task_local_only") is not True:
        fail("contract scope is not task-local")
    if contract["scope"].get("synthetic_only") is not True:
        fail("contract scope is not synthetic")
    candidate = contract["candidate_identity"]
    if candidate["checkpoint_sha256"] != reference.CHECKPOINT_SHA256 \
            or candidate["model_repo_revision"] != reference.MODEL_REPO_REVISION \
            or candidate["config_sha256"] != reference.CONFIG_SHA256 \
            or candidate["hyperparams_sha256"] != reference.HYPERPARAMS_SHA256 \
            or candidate["checkpoint_bytes"] != reference.CHECKPOINT_BYTES:
        fail("candidate artifact identity mismatch")
    if candidate["model_card_license"] != "Apache-2.0" or candidate["weights_accessed"] is not False:
        fail("candidate license or weight-access statement mismatch")
    runtime = contract["runtime_identity"]
    if runtime["speechbrain_version"] != reference.SPEECHBRAIN_VERSION \
            or runtime["wheel_sha256"] != reference.SPEECHBRAIN_WHEEL_SHA256 \
            or runtime["installed_in_this_worktree"] is not False:
        fail("runtime identity mismatch")
    corpus = contract["corpus_identity"]
    if corpus["mirror"] != reference.CORPUS_MIRROR \
            or corpus["revision"] != reference.CORPUS_REVISION \
            or corpus["test_pairs"] != reference.CORPUS_TEST_PAIRS \
            or corpus["dataset_license"] != reference.CORPUS_LICENSE \
            or corpus["present"] is not False or corpus["downloaded"] is not False:
        fail("corpus identity or availability mismatch")
    for token in ("CC BY 4.0", "ODC-By", "unverified"):
        if token not in json.dumps(corpus):
            fail("corpus provenance note missing: " + token)
    boundary = contract["caller_asset_boundary"]
    if boundary["loaded"] is not False or boundary["executed"] is not False:
        fail("caller asset boundary claims a load or execution")
    if boundary["surrogate_substituted"] is not True:
        fail("caller asset boundary does not record the surrogate substitution")
    if boundary["asset_present"] is not False:
        fail("caller asset boundary claims the asset is present")
    if not contract["release_gates"] or len(contract["release_gates"]) < 10:
        fail("release gates missing")
    for gate in contract["release_gates"]:
        if gate["status"] != "blocked":
            fail("a contract release gate is not blocked: " + gate["name"])
    if adapter["decision"] != reference.DECISION or adapter["status"] != reference.STATUS:
        fail("adapter disposition mismatch")
    for key in ("real_runtime_used", "weights_loaded", "corpus_used",
                "processor_exposure", "registered", "enabled_by_default"):
        if adapter.get(key) is not False:
            fail("adapter flag is not false: " + key)
    if adapter["asset_binding"]["loaded"] is not False:
        fail("adapter asset binding claims a load")
    if provider["decision"] != reference.DECISION \
            or provider["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("provider disposition mismatch")
    for key in ("registered", "enabled_by_default", "processor_exposure",
                "c_abi_or_sdk_default_change", "shared_build_or_ci_change",
                "descriptor_registry_change", "installed_v0_behavior_change",
                "real_runtime", "weights_loaded", "corpus_used"):
        if provider.get(key) is not False:
            fail("provider flag is not false: " + key)
    if provider.get("opt_in_required") is not True:
        fail("provider must require opt-in")
    print("verify: contract, adapter, provider disposition and blockers strict")


def check_report(report: dict[str, Any], digest: str) -> None:
    if set(report) != REPORT_KEYS:
        fail("report key set mismatch: " + str(sorted(set(report) ^ REPORT_KEYS)))
    if report["base_commit"] != reference.BASE_COMMIT or report["branch"] != reference.BRANCH:
        fail("report base or branch mismatch")
    if report["task_id"] != reference.TASK_ID or report["component"] != reference.COMPONENT:
        fail("report task or component mismatch")
    if report["status"] != reference.STATUS or report["evidence_status"] != reference.EVIDENCE_STATUS:
        fail("report status mismatch")
    if report["qualification_status"] != reference.QUALIFICATION_STATUS:
        fail("report qualification mismatch")
    if report["decision"] != reference.DECISION:
        fail("report decision is not DEFER")
    if report.get("no_missing_result_qualifies_candidate") is not True:
        fail("missing-result qualification guard missing")
    for key, value in reference.BOUNDARY.items():
        if report["boundary"].get(key) != value:
            fail("boundary flag mismatch: " + key)
    if report["format"] != reference.FORMAT:
        fail("v0 geometry mismatch")
    if report["profile"] != reference.PROFILE or report["family"] != reference.FAMILY:
        fail("report profile is not enhancement")
    if report["scope"] != reference.SCOPE:
        fail("report scope flag mismatch")
    if any(value is not False for value in report["claims"].values()):
        fail("report contains a forbidden real-world claim")
    if report["extra"]["live_default"] is not False \
            or report["extra"]["task_board_handoff_written"] is not False:
        fail("live default or board handoff recorded as true")
    if set(report["source_pin_paths"]) != set(reference.SOURCE_PIN_PATHS):
        fail("report source pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("report local file names mismatch")
    if set(report["conditions"]) != set(reference.CONDITIONS):
        fail("condition set mismatch")
    for name, condition in report["conditions"].items():
        if set(condition["variants"]) != set(reference.VARIANTS):
            fail("variant set mismatch in " + name)
        if condition["status"] == "validity_control":
            if name != "silence_control":
                fail("unexpected validity control: " + name)
            if condition["input_metrics"]["stoi"] is not None:
                fail("validity control produced a scored STOI")
        for variant, entry in condition["variants"].items():
            metrics = entry["metrics"]
            if metrics["samples"] != reference.SAMPLES:
                fail("output length mismatch: " + name + "/" + variant)
            if metrics["finite"] is not True:
                fail("nonfinite synthetic output: " + name + "/" + variant)
            if metrics["stoi"] is not None and not 0.0 <= metrics["stoi"] <= 1.0:
                fail("STOI outside [0,1]: " + name + "/" + variant)
            if metrics["stoi"] is None and not metrics["stoi_status"]:
                fail("unscored STOI without a reason: " + name + "/" + variant)
    controls = report["controls"]
    if controls["all_present"] is not True:
        fail("matched controls incomplete")
    if set(controls) != {"all_present", "identity", "named_baseline", "candidate",
                         "classical_reference"}:
        fail("control set mismatch")
    if controls["identity"]["exact_passthrough"] is not True:
        fail("identity control is not an exact passthrough")
    if controls["candidate"]["status"] != "surrogate_only":
        fail("candidate control is presented as a real result")
    if set(report["clean_preservation"]) != set(reference.SCORED_CONDITIONS):
        fail("clean preservation condition set mismatch")
    for entry in report["clean_preservation"].values():
        if set(entry["variants"]) != set(reference.CLEAN_PRESERVATION_VARIANTS):
            fail("clean preservation variant set mismatch")
    scan = report["regression_scan"]
    if scan["completed"] is not True or scan["count"] != len(scan["records"]):
        fail("regression scan accounting mismatch")
    for record in scan["records"]:
        if record["delta"] is None or record["delta"] >= 0.0:
            fail("regression record is not a negative delta")
        if record["metric"] not in ("si_sdr_db", "stoi"):
            fail("regression record metric is not paired quality")
    profile = report["enhancement_profile"]
    if set(profile) != ENHANCEMENT_KEYS:
        fail("enhancement profile key set mismatch: "
             + str(sorted(set(profile) ^ ENHANCEMENT_KEYS)))
    if profile["profile_source"] != "plan/swarm/VERIFICATION.md#Enhancement":
        fail("enhancement profile source mismatch")
    if profile["paired_clean_reference"]["real_corpus_used"] is not False:
        fail("paired clean reference claims real corpus use")
    if profile["task_matched_baseline"]["reproduced"] is not False:
        fail("task-matched baseline claims reproduction")
    if profile["task_matched_baseline"]["status"] != "blocked_external_assets":
        fail("task-matched baseline is not recorded as blocked")
    if profile["alignment"]["measured"] is not False \
            or profile["alignment"]["measured_content_delay_samples"] is not None:
        fail("alignment claims a measurement")
    if profile["state_memory_timing"]["status"] != "blocked_unmeasured":
        fail("state/memory/timing is not blocked")
    if profile["listening"]["status"] != "blocked_not_run":
        fail("listening is not blocked")
    if profile["resource"]["measured"] is not False:
        fail("resource usage claims a measurement")
    if profile["resource"]["recorded_provenance_only"]["status"] != \
            "recorded_provenance_only_not_reproduced":
        fail("resource provenance is not quarantined")
    if profile["peaks_and_invalid_outputs"]["invalid_outputs"] != 0:
        fail("invalid synthetic outputs were counted as results")
    findings = profile["mechanism_findings"]
    if findings["unit_peak_normalization_pattern"]["peak_only_max_abs_delta_stoi"] != 0.0:
        fail("unit-peak normalization changed STOI; the level-only claim is false")
    if findings["rms_match_recovers_level_not_content"]["max_abs_si_sdr_change_db"] != 0.0:
        fail("RMS matching changed SI-SDR; the level-only claim is false")
    adverse = report["adverse"]
    for name, case in adverse["config_rejections"].items():
        if not case["status"].startswith("rejected_") or case["controller_created"] is not False:
            fail("config case did not fail closed: " + name)
    for name in ("empty", "nonfinite", "wrong_rate", "stereo", "oversize"):
        if not adverse["frame_rejections"][name].startswith("rejected_"):
            fail("frame case did not fail closed: " + name)
    if adverse["frame_rejections"]["dsp_state_unchanged"] is not True:
        fail("DSP state changed on a rejected frame")
    for name, status_value in adverse["lifecycle"].items():
        if status_value != "rejected_session":
            fail("lifecycle case did not fail closed: " + name)
    validity = adverse["validity"]
    for key in ("invalid_excluded", "missing_result_not_promoted",
                "unknown_never_counted_as_scored", "silence_degenerate",
                "clipped_input_recorded"):
        if validity[key] is not True:
            fail("validity guard missing: " + key)
    asset = report["caller_asset_boundary"]
    if asset["model"] != "caller_supplied_asset_reference":
        fail("caller-supplied asset boundary missing")
    if asset["loaded"] is not False or asset["executed"] is not False \
            or asset["surrogate_substituted"] is not True:
        fail("caller asset boundary claims execution or a missing surrogate")
    if asset["asset_identity"]["checkpoint_sha256"] != reference.CHECKPOINT_SHA256:
        fail("checkpoint identity mismatch")
    if asset["asset_identity"]["config_sha256"] != reference.CONFIG_SHA256:
        fail("config identity mismatch")
    if asset["asset_identity"]["verification"] != \
            "identity_quoted_from_provenance; bytes_absent_not_verified":
        fail("asset identity verification status mismatch")
    if asset["runtime_identity"]["installed_in_this_worktree"] is not False:
        fail("runtime identity claims an install")
    if asset["corpus_identity"]["download_attempted"] is not False:
        fail("corpus identity claims a download")
    for name, outcome in asset["probe"].items():
        if outcome["loaded"] is not False or outcome["executed"] is not False:
            fail("asset probe loaded or executed bytes: " + name)
    if asset["probe"]["absent"]["status"] != "asset_unavailable":
        fail("absent asset probe did not fail closed")
    readiness = report["readiness"]
    if readiness["qualifies"] is not False or readiness["missing_result_promoted"] is not False:
        fail("readiness claims a qualification")
    identifiers = {blocker["id"] for blocker in readiness["external_blockers"]}
    if identifiers != {"checkpoint_assets_absent", "pinned_runtime_absent",
                       "corpus_provenance_uncleared", "recorded_quality_result_negative",
                       "installed_adapter_not_implemented"}:
        fail("external blocker set mismatch")
    for blocker in readiness["external_blockers"]:
        for key in ("requirement", "observation", "reopen_condition"):
            if not blocker[key]:
                fail("incomplete external blocker: " + blocker["id"])
    availability = readiness["asset_availability"]
    for key in ("checkpoint_bytes_present", "runtime_installed", "corpus_present",
                "download_attempted"):
        if availability[key] is not False:
            fail("asset availability claims a present asset: " + key)
    provenance = report["historical_provenance"]
    if not provenance["status"].startswith("recorded_provenance_only"):
        fail("historical provenance is not quarantined")
    if "not_reproduced" not in provenance["upstream_model_card_claim"]["status"]:
        fail("upstream model-card claim is not quarantined")
    if not report["missing_evidence"]:
        fail("missing evidence list is empty")
    if not report["gates"] or any(gate["status"] != "blocked" for gate in report["gates"]):
        fail("all gates must remain blocked")
    payload = reference.canonical_report_bytes(report)
    zero_checked = json.loads(payload.decode("utf-8"))

    def walk(value: Any, where: str) -> None:
        if isinstance(value, float):
            if value == 0.0 and math.copysign(1.0, value) < 0.0:
                fail("negative zero in canonical report at " + where)
        elif isinstance(value, dict):
            for key, item in value.items():
                walk(item, where + "." + key)
        elif isinstance(value, list):
            for index, item in enumerate(value):
                walk(item, where + "[" + str(index) + "]")

    walk(zero_checked, "report")
    digest_line = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if digest_line != digest + "  report.json":
        fail("report sidecar mismatch")
    print("verify: report fields, controls, ablations, adverse cases and gates strict")


def check_reproduction(digest: str) -> None:
    report_bytes = cli.report_bytes()
    if (HERE / "report.json").read_bytes() != report_bytes:
        fail("report.json is not byte-reproducible")
    if hashlib.sha256(report_bytes).hexdigest() != digest:
        fail("canonical digest mismatch")
    if (HERE / "SOURCES.sha256").read_bytes() != cli.manifest_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    code = ("import hashlib,reference; print(hashlib.sha256("
            "reference.canonical_report_bytes(reference.build_report())).hexdigest())")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical report, sidecar, manifest and three cold starts byte-identical")


def check_licensing(manifest: dict[str, str]) -> None:
    explicit = 0
    annotated = 0
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if path.is_dir():
            if path.name == "__pycache__":
                fail("bytecode cache present in evidence directory")
            continue
        name = path.relative_to(HERE).as_posix()
        if not path.is_file():
            fail("non-regular file in evidence directory: " + name)
        if name == "SOURCES.sha256":
            continue
        if name not in reference.LOCAL_FILES:
            fail("file outside fail-closed local set: " + name)
        if path.suffix == ".py":
            head = path.read_text(encoding="utf-8").splitlines()[:3]
            if head[:2] != ["# " + SPDX_C, "# " + SPDX_L] \
                    or path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("missing or repeated SPDX header: " + name)
            explicit += 1
        elif path.suffix == ".md":
            head = path.read_text(encoding="utf-8").splitlines()[:3]
            if head[:2] != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
                fail("missing Markdown SPDX header: " + name)
            explicit += 1
        elif name.endswith(".license"):
            if path.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("invalid license sidecar: " + name)
            annotated += 1
        else:
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file() or sidecar.read_text(encoding="utf-8") != SIDECAR_TEXT:
                fail("missing or invalid license sidecar: " + name + ".license")
            if "worktree:" + TASK_PREFIX + name + ".license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
            annotated += 1
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 coverage missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=True)
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    print("verify: write scope limited to task-local evidence")


def main() -> int:
    manifest = read_manifest()
    check_pins(manifest)
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    provider = strict_json(HERE / "provider.json")
    report = strict_json(HERE / "report.json")
    check_contract(contract, adapter, provider, manifest)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    check_reproduction(digest)
    check_licensing(manifest)
    check_scope()
    print("verify: OK decision=DEFER evidence=incomplete qualification=not_qualified")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
