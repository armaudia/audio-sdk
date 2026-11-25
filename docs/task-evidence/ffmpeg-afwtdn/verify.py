# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Strict read-only verification of the SDK-FFMPEG-AFWTDN evidence package.

Fails closed on any changed pin, unpinned local file, duplicate or nonfinite
JSON key, missing artifact, non-DEFER disposition, license gap, out-of-scope
change or non-reproducible canonical report.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
from pathlib import Path
import re
import subprocess
import sys
from typing import Any

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
TASK_PREFIX = "docs/task-evidence/ffmpeg-afwtdn/"
SPDX_TAG = "SPDX" "-License-Identifier:"
SPDX_COPYRIGHT = "SPDX" "-FileCopyrightText:"
MANIFEST = HERE / "SOURCES.sha256"
REPORT = HERE / "report.json"
REPORT_SHA = HERE / "report.json.sha256"
CONTRACT = HERE / "contract.json"
PROVIDER = HERE / "provider.json"
PROVENANCE = HERE / "tool-provenance.json"

REPORT_KEYS = frozenset({
    "schema_id", "task_id", "title", "component", "branch", "base_commit", "profile",
    "family", "status", "qualification_status", "decision", "no_missing_result_qualifies_candidate",
    "scope", "boundary", "format", "deliverable", "external_tool", "tool_provenance_status",
    "numeric_parity_with_ffmpeg", "ffmpeg_invoked", "ffmpeg_binary_vendored",
    "license_qualified_runtime_present", "source_context", "acceptance_profile", "conditions",
    "controls", "clean_speech_preservation", "alignment_and_state", "adverse", "regressions",
    "qualification", "gates", "missing_evidence", "evidence_classes", "source_pins",
    "boundary_pins", "scorer", "repeat_runs",
})
CONTRACT_KEYS = frozenset({
    "SPDX-FileCopyrightText", "SPDX-License-Identifier", "schema_id", "task", "component",
    "base_commit", "branch", "profile", "status", "qualification", "public_surface", "scope",
    "source_pins", "boundary_pins", "mutable_provenance", "artifact_pins", "reproduction",
    "release_gates",
})
PROVIDER_KEYS = frozenset({
    "SPDX-FileCopyrightText", "SPDX-License-Identifier", "schema_id", "task", "component",
    "status", "qualification_status", "decision", "registered", "default_enabled",
    "opt_in_required", "processor_exposure", "c_abi_or_sdk_default_change",
    "shared_cmakelists_change", "descriptor_registry_change", "installed_v0_behavior_change",
    "audio_path", "boundary", "real_runtime", "ffmpeg_invocation", "licensed_asset", "note",
})
PROVENANCE_KEYS = frozenset({
    "SPDX-FileCopyrightText", "SPDX-License-Identifier", "schema_id", "task", "base_commit",
    "status", "exact_runtime", "binary_handling", "external_tool_invocations",
    "synthetic_afwtdn_invocation", "historical_source_reported", "license_qualified_runtime",
    "numeric_parity_with_ffmpeg", "source_gate",
})
PROFILE_PRESENT = frozenset({
    "identity_control", "noisy_control", "matched_noisy_identity_baseline", "paired_si_sdr",
    "stoi", "clean_speech_preservation", "peaks_and_invalid_outputs", "alignment_and_state",
    "nonfinite_and_edge_rejections",
})
PROFILE_BLOCKED = frozenset({
    "task_matched_external_baseline", "content_and_availability_timing", "exact_runtime",
})
LICENSE_SIDECARS = ("report.json.license", "report.json.sha256.license", "SOURCES.sha256.license")
FORBIDDEN_SUFFIXES = (".wav", ".mp3", ".flac", ".ogg", ".bin", ".exe",
                      ".dylib", ".so", ".dll", ".a", ".o")
FORBIDDEN_NAMES = ("ffmpeg", "ffmpeg.exe", "ffmpeg-macos-aarch64-v7.1")
PIN_LINE = re.compile(r"^([0-9a-f]{64})  (\S+)$")


def fail(message: str) -> None:
    print("verify: FAIL " + message, file=sys.stderr)
    raise SystemExit(1)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def strict_json(path: Path, expected_keys: frozenset[str]) -> dict[str, Any]:
    def pairs(items: list[tuple[str, Any]]) -> dict[str, Any]:
        result: dict[str, Any] = {}
        for key, value in items:
            if key in result:
                fail(f"duplicate JSON key in {path.name}: {key}")
            result[key] = value
        return result

    def constant(token: str) -> None:
        fail(f"non-finite JSON constant in {path.name}: {token}")

    try:
        value = json.loads(path.read_text(encoding="utf-8"),
                           object_pairs_hook=pairs, parse_constant=constant)
    except (OSError, ValueError) as error:
        fail(f"cannot parse {path.name}: {error}")
    if not isinstance(value, dict):
        fail(f"JSON root is not an object: {path.name}")
    check_finite(value, path.name)
    if frozenset(value) != expected_keys:
        fail(f"key set mismatch in {path.name}: "
             f"missing={sorted(expected_keys - frozenset(value))} "
             f"extra={sorted(frozenset(value) - expected_keys)}")
    return value


def check_finite(value: Any, where: str) -> None:
    if isinstance(value, float) and not math.isfinite(value):
        fail("non-finite number at " + where)
    elif isinstance(value, dict):
        for key, item in value.items():
            check_finite(item, where + "." + key)
    elif isinstance(value, list):
        for index, item in enumerate(value):
            check_finite(item, where + "[" + str(index) + "]")


def read_manifest() -> dict[str, str]:
    try:
        lines = MANIFEST.read_text(encoding="utf-8").splitlines()
    except OSError as error:
        fail("cannot read SOURCES.sha256: " + str(error))
    manifest: dict[str, str] = {}
    for number, line in enumerate(lines, 1):
        if not line:
            continue
        if line.startswith("#"):
            if line not in ("# " + SPDX_COPYRIGHT + " 2026 Tsakanyan Hovhannes",
                            "# " + SPDX_TAG + " Apache-2.0"):
                fail(f"unexpected manifest comment at line {number}")
            continue
        match = PIN_LINE.match(line)
        if match is None:
            fail(f"malformed pin line {number}: {line!r}")
        digest, raw = match.group(1), match.group(2)
        if raw in manifest:
            fail("duplicate pin: " + raw)
        if raw == "SOURCES.sha256" or raw == "local:SOURCES.sha256":
            fail("SOURCES.sha256 must not pin itself")
        manifest[raw] = digest
    if not manifest:
        fail("empty source manifest")
    return manifest


def check_pins(manifest: dict[str, str]) -> None:
    import reference  # noqa: PLC0415 - task-local deterministic module

    for raw, expected in manifest.items():
        prefix = raw.split(":", 1)[0]
        if prefix not in ("source", "worktree", "local"):
            fail("unknown pin prefix: " + raw)
        path = reference.resolve_pin(raw)
        if not path.is_file():
            fail("pinned file missing: " + raw)
        actual = sha256(path.read_bytes())
        if actual != expected:
            fail(f"pinned bytes changed: {raw} {actual} != {expected}")
    expected_raw = {raw for raw, _ in reference.pin_entries()}
    if frozenset(manifest) != expected_raw:
        fail(f"manifest coverage mismatch: missing={sorted(expected_raw - frozenset(manifest))} "
             f"extra={sorted(frozenset(manifest) - expected_raw)}")
    local_pins = {raw.split(":", 1)[1] for raw in manifest if raw.startswith("local:")}
    actual_files = set(reference.local_files())
    if local_pins != actual_files:
        fail(f"unpinned or stale local artifact: missing={sorted(actual_files - local_pins)} "
             f"extra={sorted(local_pins - actual_files)}")
    print(f"verify: {len(manifest)} pins exact and complete")


def check_contract(contract: dict[str, Any], manifest: dict[str, str]) -> None:
    import reference  # noqa: PLC0415 - task-local deterministic module

    if contract["SPDX-License-Identifier"] != "Apache-2.0" \
            or contract["SPDX-FileCopyrightText"] != "2026 Tsakanyan Hovhannes":
        fail("contract SPDX metadata mismatch")
    if contract["schema_id"] != reference.CONTRACT_SCHEMA_ID \
            or contract["task"] != reference.TASK_ID \
            or contract["component"] != reference.COMPONENT \
            or contract["base_commit"] != reference.BASE_COMMIT \
            or contract["branch"] != reference.BRANCH \
            or contract["profile"] != reference.PROFILE \
            or contract["status"] != "proposal_only_synthetic_incomplete":
        fail("contract identity mismatch")
    qualification = contract["qualification"]
    if (qualification["status"] != "incomplete" or qualification["decision"] != "DEFER"
            or qualification["qualifies"] is not False
            or qualification["missing_result_promoted"] is not False
            or qualification["processor_exposure"] is not False
            or qualification["all_required_synthetic_results_present"] is not True):
        fail("contract qualification is not incomplete/DEFER")
    for key, value in contract["public_surface"].items():
        if value is not False:
            fail("public surface flag is not false: " + key)
    scope = contract["scope"]
    truthful = ("synthetic_only", "task_local_only")
    for key, value in scope.items():
        if key in truthful:
            if value is not True:
                fail("scope flag is not true: " + key)
        elif key == "installed_v0_format":
            if value != "16 kHz mono float32, 160 samples":
                fail("installed v0 geometry changed in contract")
        elif value is not False:
            fail("scope flag is not false: " + key)
    if contract["source_pins"] != reference.source_pins() \
            or contract["boundary_pins"] != reference.boundary_pins():
        fail("contract pins differ from current pinned inputs")
    for path, digest in contract["source_pins"].items():
        if manifest.get("source:" + path) != digest:
            fail("contract source pin absent from manifest: " + path)
    for path, digest in contract["boundary_pins"].items():
        if manifest.get("worktree:" + path) != digest:
            fail("contract boundary pin absent from manifest: " + path)
    if "SOURCES.sha256" in contract["artifact_pins"] or "contract.json" in contract["artifact_pins"]:
        fail("contract artifact pins must not pin itself or the manifest")
    for name, digest in contract["artifact_pins"].items():
        path = HERE / name
        if not path.is_file() or sha256(path.read_bytes()) != digest:
            fail("contract artifact pin mismatch: " + name)
    if frozenset(contract["artifact_pins"]) != frozenset(reference.artifact_pins()):
        fail("contract artifact pin coverage mismatch")
    mutable = contract["mutable_provenance"]
    if mutable["gate"] is not False or not re.fullmatch(r"[0-9a-f]{64}", mutable["sha256_at_read"]):
        fail("mutable board provenance is gating or malformed")
    if not contract["release_gates"] or "verify.py" not in contract["reproduction"]["verify"]:
        fail("contract release gates or reproduction commands missing")
    print("verify: contract incomplete/DEFER with exact pins")


def check_provider(provider: dict[str, Any]) -> None:
    import reference  # noqa: PLC0415 - task-local deterministic module

    if provider["SPDX-License-Identifier"] != "Apache-2.0" \
            or provider["SPDX-FileCopyrightText"] != "2026 Tsakanyan Hovhannes":
        fail("provider SPDX metadata mismatch")
    if provider["schema_id"] != reference.PROVIDER_SCHEMA_ID \
            or provider["task"] != reference.TASK_ID \
            or provider["component"] != reference.COMPONENT \
            or provider["status"] != "proposal_only_synthetic_incomplete" \
            or provider["qualification_status"] != "not_qualified" \
            or provider["decision"] != "DEFER":
        fail("provider disposition mismatch")
    for key in ("registered", "default_enabled", "processor_exposure", "real_runtime",
                "ffmpeg_invocation", "licensed_asset", "c_abi_or_sdk_default_change",
                "shared_cmakelists_change", "descriptor_registry_change",
                "installed_v0_behavior_change"):
        if provider[key] is not False:
            fail("provider flag is not false: " + key)
    if provider["opt_in_required"] is not True:
        fail("provider is not opt-in")
    if provider["boundary"] != {
        "registered": False, "enabled_by_default": False, "default_selected": False,
        "descriptor_settings": {}, "public_api_abi_change": False, "format": reference.FORMAT,
    }:
        fail("provider boundary or v0 geometry mismatch")
    print("verify: provider unregistered, OFF by default and DEFER")


def check_provenance(provenance: dict[str, Any]) -> None:
    import reference  # noqa: PLC0415 - task-local deterministic module

    if provenance["SPDX-License-Identifier"] != "Apache-2.0" \
            or provenance["SPDX-FileCopyrightText"] != "2026 Tsakanyan Hovhannes":
        fail("tool provenance SPDX metadata mismatch")
    if provenance["schema_id"] != reference.PROVENANCE_SCHEMA_ID \
            or provenance["task"] != reference.TASK_ID \
            or provenance["base_commit"] != reference.BASE_COMMIT \
            or provenance["status"] != "blocked":
        fail("tool provenance identity or status mismatch")
    handling = provenance["binary_handling"]
    for key in ("downloaded", "shipped", "vendored", "wrapped", "invoked",
                "source_present", "licensed_runtime_present"):
        if handling[key] is not False:
            fail("binary handling is not excluded: " + key)
    runtime = provenance["exact_runtime"]
    if (runtime["version"] != "7.1" or runtime["license"] != "GPL-2.0-or-later"
            or runtime["build_configuration"] is not None
            or runtime["configuration_available_locally"] is not False):
        fail("exact FFmpeg 7.1 / GPL provenance gap is not explicit")
    if provenance["synthetic_afwtdn_invocation"]["status"] != "not_run":
        fail("synthetic FFmpeg invocation is not recorded as not_run")
    for invocation in provenance["external_tool_invocations"]:
        if invocation["status"] != "blocked_not_run" or invocation["returncode"] is not None:
            fail("an FFmpeg invocation is not blocked: " + str(invocation["argv"]))
    if (provenance["numeric_parity_with_ffmpeg"] is not False
            or provenance["license_qualified_runtime"]["available"] is not False
            or provenance["source_gate"]["status"] != "blocked"):
        fail("FFmpeg parity or rights gate is not blocked")
    print("verify: FFmpeg 7.1 GPL provenance gap explicit and blocked")


def check_report(report: dict[str, Any], manifest: dict[str, str]) -> str:
    import reference  # noqa: PLC0415 - task-local deterministic module

    if report["base_commit"] != reference.BASE_COMMIT \
            or report["task_id"] != reference.TASK_ID \
            or report["component"] != reference.COMPONENT \
            or report["branch"] != reference.BRANCH \
            or report["profile"] != reference.PROFILE \
            or report["status"] != "proposal_only_synthetic_incomplete" \
            or report["qualification_status"] != "not_qualified" \
            or report["decision"] != "DEFER" \
            or report["no_missing_result_qualifies_candidate"] is not True:
        fail("report identity or DEFER disposition mismatch")
    if report["boundary"] != reference.BOUNDARY or report["format"] != reference.FORMAT:
        fail("report boundary or v0 geometry mismatch")
    for key in ("numeric_parity_with_ffmpeg", "ffmpeg_invoked", "ffmpeg_binary_vendored",
                "license_qualified_runtime_present"):
        if report[key] is not False:
            fail("report FFmpeg boundary flag is not false: " + key)
    if report["tool_provenance_status"] != "blocked_unavailable":
        fail("report tool provenance is not blocked")
    profile = report["acceptance_profile"]
    if profile["profile"] != reference.PROFILE:
        fail("acceptance profile name mismatch")
    for key in PROFILE_PRESENT:
        if profile[key] is not True:
            fail("Enhancement profile result missing: " + key)
    for key in PROFILE_BLOCKED:
        if profile[key] is not False:
            fail("Enhancement gate not blocked: " + key)
    if frozenset(report["conditions"]) != frozenset(reference.CONDITIONS):
        fail("condition set mismatch")
    if report["controls"]["all_present"] is not True \
            or report["controls"]["task_matched_baseline"]["status"] != "blocked_external_runtime" \
            or report["controls"]["task_matched_baseline"]["numeric_parity_claimed"] is not False:
        fail("matched controls are incomplete or claim parity")
    if report["source_pins"] != reference.source_pins() \
            or report["boundary_pins"] != reference.boundary_pins():
        fail("report pins differ from current pinned inputs")
    for path, digest in report["source_pins"].items():
        if manifest.get("source:" + path) != digest:
            fail("report source pin absent from manifest: " + path)
    if report["scorer"]["local_scorer_digest"] != sha256((HERE / "scorer.py").read_bytes()):
        fail("local scorer digest mismatch")
    if report["qualification"]["decision"] != "DEFER" \
            or report["qualification"]["qualifies"] is not False \
            or report["qualification"]["no_missing_result_may_qualify"] is not True:
        fail("report qualification is not DEFER")
    if not report["gates"] or any(gate["status"] != "blocked" for gate in report["gates"]):
        fail("some release gates are not blocked")
    if not all("reason" in gate and "reopen" in gate for gate in report["gates"]):
        fail("release gates lack reason or reopening condition")
    expected = reference.canonical_report_bytes(reference.build_report())
    raw = REPORT.read_bytes()
    if raw != expected:
        fail("report.json is not byte-identical after regeneration")
    digest = sha256(raw)
    sidecar = REPORT_SHA.read_text(encoding="ascii").strip()
    if sidecar != f"{digest}  report.json":
        fail("report.json.sha256 does not match report.json")
    core = dict(report)
    core.pop("repeat_runs")
    core_digest = sha256(reference.canonical_bytes(core))
    repeats = report["repeat_runs"]
    if (repeats["three_repeats"] != 3 or repeats["byte_identical"] is not True
            or repeats["canonical_digests"] != [core_digest] * 3):
        fail("repeat_runs are not three exact canonical repeats")
    if b"-0.0" in raw:
        fail("canonical report contains negative zero")
    print("verify: report canonical, DEFER, digest " + digest)
    return digest


def check_cold_repeats(report_bytes: bytes) -> None:
    env = dict(os.environ)
    env["PYTHONDONTWRITEBYTECODE"] = "1"
    outputs: list[bytes] = []
    for _ in range(3):
        result = subprocess.run([sys.executable, "run.py", "report.json"], cwd=HERE, env=env,
                                stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
        if result.returncode != 0:
            fail("run.py report.json failed: " + result.stderr.decode("utf-8", "replace"))
        outputs.append(result.stdout)
        if REPORT.read_bytes() != report_bytes:
            fail("run.py report.json changed canonical bytes")
    if len(set(outputs)) != 1:
        fail("three cold-start regenerations produced different output")
    print("verify: 3/3 byte-identical cold-start regenerations")


def check_licensing(manifest: dict[str, str]) -> None:
    for path in sorted(HERE.glob("*.py")):
        head = path.read_text(encoding="utf-8").splitlines()[:2]
        if len(head) != 2 or not head[0].startswith("# " + SPDX_COPYRIGHT) \
                or head[1] != "# " + SPDX_TAG + " Apache-2.0":
            fail("missing SPDX header: " + path.name)
    for name in LICENSE_SIDECARS:
        text = (HERE / name).read_text(encoding="utf-8")
        if SPDX_COPYRIGHT not in text or SPDX_TAG + " Apache-2.0" not in text:
            fail("missing SPDX sidecar annotations: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml no longer covers docs/** as Apache-2.0")
    for path in sorted(HERE.iterdir()):
        if path.name in FORBIDDEN_NAMES or path.suffix.lower() in FORBIDDEN_SUFFIXES:
            fail("forbidden binary or media file in task dir: " + path.name)
    for name in ("reference.py", "scorer.py", "run.py"):
        source = (HERE / name).read_text(encoding="utf-8")
        if "subprocess" in source or "os.system" in source or "Popen" in source:
            fail("task-local reference appears to invoke an external tool: " + name)
    import reference  # noqa: PLC0415 - task-local deterministic module

    scorer_pin = "source:" + "audio-benchmark-platform/audio-sdk/docs/task-evidence/classical-wiener-denoising/scorer.py"
    if sha256((HERE / "scorer.py").read_bytes()) != manifest.get(scorer_pin):
        fail("local scorer is not the pinned crosschecked port")
    tests = (HERE / "test_reference.py").read_text(encoding="utf-8")
    count = len(re.findall(r"^    def test_", tests, flags=re.MULTILINE))
    if count < 30:
        fail(f"fewer than 30 reference tests: {count}")
    print(f"verify: licensing annotations exact and {count} reference tests")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True, check=False)
    if result.returncode != 0:
        fail("git scope check failed: " + result.stderr.strip())
    changed: list[str] = []
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path:
            changed.append(path)
            if not path.startswith(TASK_PREFIX):
                fail("change outside task-local evidence directory: " + path)
    print(f"verify: {len(changed)} working-tree paths confined to {TASK_PREFIX}")


def main() -> int:
    manifest = read_manifest()
    check_pins(manifest)
    contract = strict_json(CONTRACT, CONTRACT_KEYS)
    provider = strict_json(PROVIDER, PROVIDER_KEYS)
    provenance = strict_json(PROVENANCE, PROVENANCE_KEYS)
    report = strict_json(REPORT, REPORT_KEYS)
    check_contract(contract, manifest)
    check_provider(provider)
    check_provenance(provenance)
    digest = check_report(report, manifest)
    check_cold_repeats(REPORT.read_bytes())
    check_licensing(manifest)
    check_scope()
    print(f"verify: PASS decision=DEFER report_sha256={digest} pins={len(manifest)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
