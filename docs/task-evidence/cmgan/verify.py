# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Read-only strict verification of the task-local CMGAN evidence package.

Every check fails closed: missing or stale pins, duplicate JSON keys, nonfinite
constants, noncanonical regeneration, disposition drift, a promoted missing
result, a stale README digest table, licensing gaps or any out-of-scope worktree
change is a hard failure.
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
TASK_PREFIX = reference.TASK_PREFIX
SPDX_C = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"
SPDX_L = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_TOKEN = "SPDX" "-License-Identifier:"
SIDECAR_TEXT = f"{SPDX_C}\n{SPDX_L}\n"

EXPECTED_GATES = {
    "exact_asset_identity": "clear",
    "runtime_admission": "blocked",
    "artifact_rights": "blocked",
    "exact_reference_parity": "blocked",
    "rights_cleared_cohort": "blocked",
    "independent_scoring_and_listening": "blocked",
    "target_runtime_timing": "blocked",
    "provider_intake": "blocked",
    "public_default_selection": "blocked",
}
EXPECTED_CONFIG_CASES = {
    "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
    "wrong_model_name", "wrong_source_revision", "wrong_checkpoint_sha",
    "wrong_checkpoint_bytes", "wrong_n_fft", "wrong_hop_length",
    "wrong_cut_length", "wrong_num_channel", "wrong_num_features",
    "wrong_power_exponent", "mode_unsupported", "surrogate_without_opt_in",
    "missing_field", "unknown_field",
}
EXPECTED_ASSET_CASES = {
    "provider_storage", "provider_file_access", "download_attempted",
    "wrong_asset_id", "wrong_source_revision", "wrong_checkpoint_path",
    "wrong_checkpoint_bytes", "bool_checkpoint_bytes", "wrong_checkpoint_sha",
    "malformed_checkpoint_sha", "wrong_checkpoint_git_blob", "wrong_code_license",
    "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
    "missing_field", "unknown_field",
}
EXPECTED_FRAME_CASES = {
    "chunk_empty", "chunk_oversized", "chunk_non_numeric", "chunk_boolean",
    "chunk_nonfinite", "chunk_out_of_range",
}
EXPECTED_CHUNKS_TOTAL = (
    1 + sum((32_000 + size - 1) // size for size in reference.CHUNK_SIZES))


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
    if not lines or lines[0] != cli.MANIFEST_COMMENT:
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
    source = {"source:" + path for path in reference.SOURCE_PINS}
    boundary = {"worktree:" + path for path in reference.BOUNDARY_PINS}
    return local | source | boundary


def check_pins(manifest: dict[str, str]) -> None:
    if set(manifest) != manifest_expected_paths():
        fail("SOURCES.sha256 path set mismatch")
    for raw, digest in reference.SOURCE_PINS.items():
        path = reference.SOURCE_ROOT / raw
        if not path.is_file() or path.is_symlink():
            fail("source pin is not a regular file: " + raw)
        if reference.sha256_file(path) != digest:
            fail("stale source pin: " + raw)
        if manifest["source:" + raw] != digest:
            fail("manifest source pin mismatch: " + raw)
    for raw, digest in reference.BOUNDARY_PINS.items():
        path = SDK_ROOT / raw
        if not path.is_file() or path.is_symlink():
            fail("boundary pin is not a regular file: " + raw)
        if reference.sha256_file(path) != digest:
            fail("stale boundary pin: " + raw)
        if manifest["worktree:" + raw] != digest:
            fail("manifest boundary pin mismatch: " + raw)
    for name in reference.LOCAL_FILES:
        path = HERE / name
        if not path.is_file() or path.is_symlink():
            fail("local artifact is not a regular file: " + name)
        digest = reference.sha256_file(path)
        if manifest[f"worktree:{TASK_PREFIX}{name}"] != digest:
            fail("manifest local pin mismatch: " + name)
        if not name.endswith(".license") and path.suffix not in (".py", ".md"):
            sidecar = HERE / (name + ".license")
            if not sidecar.is_file():
                fail("missing license sidecar for " + name)
            if f"worktree:{TASK_PREFIX}{name}.license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
    print(f"verify: {len(manifest)} pins exact (source, boundary, asset-adjacent, local)")


def check_disposition(contract: dict[str, Any], adapter: dict[str, Any],
                      readiness: dict[str, Any], report: dict[str, Any]) -> None:
    for name, value in (("contract", contract), ("report", report),
                        ("readiness", readiness)):
        if value["decision"] != reference.DECISION:
            fail(name + " decision drift")
        if value["qualification_status"] != reference.QUALIFICATION_STATUS:
            fail(name + " qualification drift")
    for name, value in (("contract", contract), ("report", report),
                        ("readiness", readiness)):
        if value["component"] != reference.COMPONENT:
            fail(name + " component drift")
        if value["profile"] != reference.PROFILE:
            fail(name + " profile drift")
    if contract["status"] != reference.STATUS:
        fail("contract status drift")
    if contract["base_commit"] != reference.BASE_COMMIT:
        fail("contract base commit drift")
    if contract["branch"] != reference.BRANCH:
        fail("contract branch drift")
    if contract["disposition"] != reference.DISPOSITION:
        fail("contract disposition drift")
    if contract["defer_before"] != reference.DEFER_BEFORE:
        fail("contract defer boundary drift")
    if report["base_commit"] != reference.BASE_COMMIT:
        fail("report base commit drift")
    if report["branch"] != reference.BRANCH:
        fail("report branch drift")

    if adapter["registered"] is not False:
        fail("adapter may not register")
    if adapter["enabled_by_default"] is not False:
        fail("adapter may not be enabled by default")
    if adapter["default_selected"] is not False:
        fail("adapter may not be selected by default")
    if adapter["provider_intake"] is not False:
        fail("provider intake may not be claimed")
    if adapter["entrypoint"] is not None:
        fail("adapter entrypoint must be absent")
    if adapter["qualifies"] is not False:
        fail("adapter may not qualify")
    if adapter["modes"] != ["offline"]:
        fail("adapter mode drift")
    if adapter["asset"]["asset_readiness"] != "blocked":
        fail("adapter asset readiness must stay blocked")
    if adapter["asset"]["storage"] != "external":
        fail("adapter asset storage must stay external")
    if adapter["asset"]["checkpoint_sha256"] != reference.CHECKPOINT_SHA256:
        fail("adapter checkpoint digest drift")
    if adapter["sample_rate_hz"] != reference.SAMPLE_RATE_HZ:
        fail("adapter sample rate drift")
    if adapter["channels"] != reference.CHANNELS:
        fail("adapter channel count drift")
    if adapter["frame_samples"] != reference.FRAME_SAMPLES:
        fail("adapter frame geometry drift")

    if readiness["ready"] is not False:
        fail("readiness must stay false")
    if readiness["proposal_only"] is not True:
        fail("readiness must stay proposal-only")
    if readiness["blocked_release_gates"] != 8:
        fail("readiness blocked gate count drift")
    if readiness["open_exact_blockers"] != len(reference.EXACT_BLOCKERS):
        fail("readiness blocker count drift")
    if readiness["exact_external_blocker"] != reference.EXACT_BLOCKERS[0]:
        fail("readiness primary blocker drift")
    prerequisites = readiness["prerequisites"]
    for key in ("official_source_present_and_pinned", "exact_checkpoint_identity_verified",
                "task_geometry_verified_statically", "permitted_scope_unchanged"):
        if prerequisites[key] is not True:
            fail("readiness prerequisite should be true: " + key)
    for key in ("runtime_available", "cuda_or_validated_accelerator_available",
                "torch_installed_in_pinned_interpreter",
                "exact_reference_output_available", "rights_cleared_cohort",
                "independent_scorer_available", "permitted_listening_available",
                "target_timing_measured", "provider_intake_approved"):
        if prerequisites[key] is not False:
            fail("readiness prerequisite must stay false: " + key)
    print("verify: DEFER / incomplete / not_qualified disposition is fail-closed")


def check_report(report: dict[str, Any], digest: str) -> None:
    if report["schema"] != reference.SCHEMA_ID:
        fail("report schema mismatch")
    if report["status"] != reference.STATUS:
        fail("report status drift")
    if report["evidence_status"] != reference.EVIDENCE_STATUS:
        fail("report evidence status drift")
    if report["defer_before"] != reference.DEFER_BEFORE:
        fail("report defer boundary drift")
    if report["qualifying_results"] != 0:
        fail("a qualifying result was promoted")
    if report["blocked_release_gates"] != 8:
        fail("blocked release gate count drift")
    if report["open_exact_blockers"] != len(reference.EXACT_BLOCKERS):
        fail("exact blocker count drift")

    gates = {item["gate"]: item["status"] for item in report["gates"]}
    if gates != EXPECTED_GATES:
        fail("gate status drift")
    if gates["exact_asset_identity"] != "clear":
        fail("exact asset identity must be recorded as locally verified")
    if sum(1 for status in gates.values() if status == "blocked") != 8:
        fail("exactly eight release gates must remain blocked")

    if report["exact_blockers"] != list(reference.EXACT_BLOCKERS):
        fail("exact blockers drift")
    if report["reopen_conditions"] != list(reference.REOPEN_CONDITIONS):
        fail("reopen conditions drift")
    if not report["exact_blockers"][0].startswith("PRIMARY:"):
        fail("primary blocker is not identified first")

    for key, value in report["claims"].items():
        if value is not False:
            fail("a non-claim was promoted: " + key)

    candidate = report["candidate"]
    expected_candidate = {
        "candidate_id": reference.CANDIDATE_ID,
        "source_repository": reference.SOURCE_REPOSITORY,
        "source_revision": reference.SOURCE_REVISION,
        "code_license": reference.CODE_LICENSE,
        "checkpoint_path": reference.CHECKPOINT_PATH,
        "checkpoint_bytes": reference.CHECKPOINT_BYTES,
        "checkpoint_sha256": reference.CHECKPOINT_SHA256,
        "checkpoint_git_blob": reference.CHECKPOINT_GIT_BLOB,
        "immutable_identity": True,
        "asset_present_in_sdk_worktree": False,
        "asset_bytes_read_by_package": 0,
    }
    for key, value in expected_candidate.items():
        if candidate[key] != value:
            fail("candidate field drift: " + key)

    geometry = report["task_geometry"]
    for key, value in (
            ("sample_rate_hz", 16000), ("channels", 1),
            ("n_fft", 400), ("hop_length", 100), ("window", "hamming"),
            ("stft_bins", 201), ("num_channel", 64), ("num_features", 201),
            ("power_exponent", 0.3), ("cut_length_samples", 256000),
            ("declared_lag_samples", 0), ("streaming_api", False)):
        if geometry[key] != value:
            fail("task geometry drift: " + key)
    probes = geometry["geometry_probes"]
    if probes["32000"]["wrap_padding_samples"] != 0:
        fail("32000-sample geometry padding drift")
    if probes["32123"]["wrap_padding_samples"] != 77:
        fail("32123-sample geometry padding drift")
    if probes["256000"]["batch_size"] != 1:
        fail("16 s geometry batch drift")
    if probes["256001"]["batch_size"] != 2:
        fail("16 s plus one batch drift")
    if probes["1000000"]["batch_size"] != 4:
        fail("1,000,000-sample batch drift")
    for probe in probes.values():
        if probe["output_samples"] != probe["input_samples"]:
            fail("geometry is not length preserving")
        if probe["padded_samples_emitted"] != 0:
            fail("geometry emits padding")
        if probe["source_time_mapping"] != "identity":
            fail("geometry mapping drift")
        if probe["stft_bins"] != 201:
            fail("STFT bin count drift")

    asset = report["asset_reference"]
    if asset["reference"] != reference.asset_ref():
        fail("asset reference drift")
    if asset["admission"]["admitted"] is not True:
        fail("exact pinned asset reference should pass schema admission")
    if asset["admission"]["qualifies"] is not False:
        fail("asset admission may not qualify")
    if asset["bytes_read_by_package"] != 0 or asset["file_access"] is not False:
        fail("asset reference must not read bytes")
    if asset["download"] is not False:
        fail("asset reference must not download")
    if set(asset["adverse_cases"]) != EXPECTED_ASSET_CASES:
        fail("asset adverse case set mismatch")
    if any(case["admitted"] for case in asset["adverse_cases"].values()):
        fail("an adverse asset reference was admitted")
    for name, case in asset["adverse_cases"].items():
        if not case["rejected"] or not case["errors"]:
            fail("asset adverse case did not fail closed: " + name)

    partial = report["partial_local_observation"]
    if partial["downloaded_by_this_task"] is not False:
        fail("a download was recorded")
    if partial["copied_into_worktree"] is not False:
        fail("an asset copy into the worktree was recorded")
    if partial["checkpoint_sha256_observed"] != reference.CHECKPOINT_SHA256:
        fail("observed checkpoint digest drift")

    conditions = report["synthetic_surrogate"]["conditions"]
    if set(conditions) != set(reference.CONDITIONS):
        fail("synthetic condition set mismatch")
    if report["synthetic_surrogate"]["not_cmgan"] is not True:
        fail("synthetic surrogate must never be labelled CMGAN")
    if report["synthetic_surrogate"]["qualifies"] is not False:
        fail("synthetic surrogate may not qualify")
    if report["synthetic_surrogate"]["total_synthetic_samples"] != 160_000:
        fail("synthetic sample total drift")
    for name, block in conditions.items():
        if block["synthetic_not_cmgan"] is not True:
            fail("condition promoted as CMGAN: " + name)
        if block["identity_exact"] is not True:
            fail("identity control is not exact: " + name)
        if block["identity_matches_noisy_control"] is not True:
            fail("identity control diverges from noisy control: " + name)
        if block["clipped"] is not False or block["nonfinite"] is not False:
            fail("surrogate output is clipped or nonfinite: " + name)
        if name == "idle_noise":
            if block["noisy_control"]["snr_db"] is not None:
                fail("idle noise must not report SNR")
        elif block["noisy_control"]["snr_db"] is None:
            fail("missing noisy SNR: " + name)

    recomputed = reference._regressions(conditions)
    if report["synthetic_surrogate"]["regressions"] != recomputed:
        fail("synthetic regressions are not recomputed exactly")

    controls = report["controls"]
    if controls["identity_passthrough_exact"] is not True:
        fail("identity pass-through is not exact")
    cross_hop = controls["cross_hop"]
    if cross_hop["all_match_whole_clip"] is not True:
        fail("chunked surrogate output diverges from the whole clip")
    if cross_hop["caller_chunks_total"] != EXPECTED_CHUNKS_TOTAL:
        fail("caller chunk accounting drift")
    if report["counts"]["caller_chunks_total"] != EXPECTED_CHUNKS_TOTAL:
        fail("report chunk count drift")
    if report["counts"]["emitted_padding_samples"] != 0:
        fail("emitted padding drift")
    if report["counts"]["real_audio_samples"] != 0:
        fail("real audio samples were recorded")

    config_cases = report["adverse_cases"]["config"]
    if set(config_cases) != EXPECTED_CONFIG_CASES:
        fail("config adverse case set mismatch")
    if any(not case["rejected"] for case in config_cases.values()):
        fail("an invalid configuration was accepted")
    if set(report["adverse_cases"]["frame"]) != EXPECTED_FRAME_CASES:
        fail("frame adverse case set mismatch")
    for name, case in report["adverse_cases"]["frame"].items():
        if not case["rejected"] or not case["state_unchanged"]:
            fail("frame adverse case did not fail closed: " + name)
    lifecycle = report["adverse_cases"]["lifecycle"]
    if not all(lifecycle[key] for key in (
            "finish_twice_rejected", "feed_after_finish_rejected",
            "reset_after_finish_allowed", "close_idempotent",
            "feed_after_close_rejected")):
        fail("lifecycle rejection drift")
    if lifecycle["empty_clip_output_samples"] != 0:
        fail("empty clip produced samples")

    alignment = report["alignment"]
    if alignment["length_preserved"] is not True or alignment["finite"] is not True:
        fail("alignment probe failed")
    if alignment["source_time_mapping"] != "identity":
        fail("alignment mapping drift")
    if alignment["padded_samples_emitted"] != 0:
        fail("alignment emitted padding")
    tail = report["tail"]
    if (tail["input_samples"] != 32_123 or tail["wrap_padding_samples"] != 77
            or tail["output_samples"] != 32_123):
        fail("tail probe drift")
    state = report["state"]
    if state["identical_state_chain"] is not True:
        fail("independent session state chain mismatch")
    if state["reset_restores_initial_state"] is not True:
        fail("reset did not restore initial state")

    profile = report["enhancement_profile"]
    if profile["stoi"] != "blocked_unmeasured":
        fail("STOI must stay blocked")
    if profile["listening"] != "not_run":
        fail("listening must stay not_run")
    if profile["real_runtime"] is not False or profile["qualifies"] is not False:
        fail("enhancement profile was promoted")

    matched = report["matched_evidence"]
    if matched["paired_dns2020_30"]["run"] is not False:
        fail("a 30-pair run was claimed")
    if matched["ears_screen"]["run"] is not False:
        fail("an EARS run was claimed")
    if matched["baseline_pairing"]["matched_measured_baseline_against_cmgan"] is not False:
        fail("a matched baseline was claimed")
    if matched["candidate_matrix"]["status"] != "unavailable/blocked":
        fail("candidate matrix status drift")
    if report["upstream_claims"]["reproduced_here"] is not False:
        fail("upstream claim was marked reproduced")
    if report["upstream_claims"]["pesq"] != 3.41:
        fail("upstream PESQ transcription drift")
    prior = report["prior_attempt"]
    if prior["pairs_completed"] != 0 or prior["quality_score_available"] is not False:
        fail("prior attempt was promoted")
    if prior["recorded_as_rtf"] is not False:
        fail("prior bound was recorded as RTF")
    if prior["smoke_retry01"]["outputs"] != 0:
        fail("prior smoke outputs drift")

    if report["test_count"] != reference.EXPECTED_TEST_COUNT:
        fail("test count drift")
    if set(report["source_pin_paths"]) != set(reference.SOURCE_PINS):
        fail("source pin paths mismatch")
    if set(report["boundary_pin_paths"]) != set(reference.BOUNDARY_PINS):
        fail("boundary pin paths mismatch")
    if set(report["local_file_names"]) != set(reference.LOCAL_FILES):
        fail("local file names mismatch")
    if report["readme_digest_files"] != list(reference.README_DIGEST_FILES):
        fail("README digest file list mismatch")
    if re.search(rb"-0\.0(?=[,}\]])", reference.canonical_report_bytes(report)):
        fail("negative zero in canonical report")
    sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8").strip()
    if sidecar != digest + "  report.json":
        fail("report digest sidecar mismatch")
    print("verify: report boundary, geometry, accounting, adverse cases and gates strict")


def _readme_table_rows() -> list[tuple[str, str, int]]:
    text = (HERE / "README.md").read_text(encoding="utf-8")
    if text.count(reference.README_TABLE_START) != 1:
        fail("README digest table start marker is not unique")
    if text.count(reference.README_TABLE_END) != 1:
        fail("README digest table end marker is not unique")
    start = text.index(reference.README_TABLE_START)
    end = text.index(reference.README_TABLE_END)
    if end <= start:
        fail("README digest table markers are ordered incorrectly")
    block = text[start + len(reference.README_TABLE_START):end].strip().splitlines()
    expected_header = ["| Artifact | SHA-256 | Bytes |", "| --- | --- | ---: |"]
    if block[:2] != expected_header:
        fail("README digest table header mismatch")
    rows: list[tuple[str, str, int]] = []
    for line in block[2:]:
        parts = re.fullmatch(r"\| `([^`]+)` \| `([0-9a-f]{64})` \| ([0-9]+) \|", line)
        if parts is None:
            fail("malformed README digest row: " + repr(line))
        rows.append((parts.group(1), parts.group(2), int(parts.group(3))))
    return rows


def check_readme() -> None:
    rows = _readme_table_rows()
    expected = [(name, reference.sha256_file(HERE / name),
                 (HERE / name).stat().st_size)
                for name in reference.README_DIGEST_FILES]
    if rows != expected:
        fail("README digest table is stale or incomplete")
    text = (HERE / "README.md").read_text(encoding="utf-8")
    token = (f"Tests: **{reference.EXPECTED_TEST_COUNT} passed, "
             "0 failed, 0 skipped**")
    if token not in text:
        fail("README test count token is stale")
    if "contract.json" in text.split(reference.README_TABLE_START)[1].split(
            reference.README_TABLE_END)[0]:
        fail("README digest table must not pin contract.json (cycle)")
    print(f"verify: README digest table exact for {len(rows)} artifacts")


def check_reproduction(manifest: dict[str, str], report_digest: str) -> None:
    if (HERE / "report.json").read_bytes() != cli.report_bytes():
        fail("report.json is not byte-reproducible")
    if (HERE / "adapter.json").read_bytes() != (
            reference.canonical_bytes(reference.build_adapter()) + b"\n"):
        fail("adapter.json is not byte-reproducible")
    if (HERE / "readiness.json").read_bytes() != (
            reference.canonical_bytes(reference.build_readiness()) + b"\n"):
        fail("readiness.json is not byte-reproducible")
    if (HERE / "README.md").read_bytes() != cli.readme_bytes():
        fail("README.md digest table is not byte-reproducible")
    if (HERE / "contract.json").read_bytes() != cli.contract_bytes(cli.contract_pins()):
        fail("contract.json is not byte-reproducible")
    if (HERE / "SOURCES.sha256").read_bytes() != cli.manifest_bytes():
        fail("SOURCES.sha256 is not byte-reproducible")
    if hashlib.sha256(cli.report_bytes()).hexdigest() != report_digest:
        fail("canonical report digest mismatch")
    code = ("import hashlib,run; print(hashlib.sha256(run.report_bytes()).hexdigest())")
    env = dict(os.environ, PYTHONDONTWRITEBYTECODE="1")
    for _ in range(3):
        result = subprocess.run([sys.executable, "-c", code], cwd=HERE, env=env,
                                capture_output=True, text=True, check=False)
        if result.returncode != 0 or result.stdout.strip() != report_digest:
            fail("cold-start reproduction failed: " + result.stderr.strip())
    print("verify: canonical artifacts, sidecar, README table, manifest and three cold starts exact")


def check_licensing(manifest: dict[str, str]) -> None:
    explicit = 0
    annotated = 0
    expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
    for path in sorted(HERE.rglob("*"), key=lambda item: item.relative_to(HERE).as_posix()):
        if not path.is_file():
            fail("non-file entry in evidence directory")
        if "__pycache__" in path.parts:
            fail("unexpected __pycache__ in evidence directory")
        name = path.relative_to(HERE).as_posix()
        if name not in expected:
            fail("file outside fail-closed local set: " + name)
        if name == "SOURCES.sha256":
            if not (HERE / "SOURCES.sha256.license").is_file():
                fail("SOURCES.sha256.license missing")
            annotated += 1
            continue
        if path.suffix == ".py":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["# " + SPDX_C, "# " + SPDX_L]:
                fail("missing explicit Python SPDX header: " + name)
            if path.read_text(encoding="utf-8").count(SPDX_TOKEN) != 1:
                fail("repeated SPDX identifier token: " + name)
            explicit += 1
        elif path.suffix == ".md":
            lines = path.read_text(encoding="utf-8").splitlines()[:3]
            if lines[:2] != ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"]:
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
            if f"worktree:{TASK_PREFIX}{name}.license" not in manifest:
                fail("license sidecar is unpinned: " + name + ".license")
            annotated += 1
    for name in sorted(expected - {path.relative_to(HERE).as_posix()
                                   for path in HERE.rglob("*") if path.is_file()}):
        fail("expected file missing: " + name)
    reuse = (SDK_ROOT / "REUSE.toml").read_text(encoding="utf-8")
    if '"docs/**"' not in reuse or 'SPDX-License-Identifier = "Apache-2.0"' not in reuse:
        fail("REUSE.toml docs/** Apache-2.0 annotation missing")
    if not (SDK_ROOT / "LICENSES" / "Apache-2.0.txt").is_file():
        fail("LICENSES/Apache-2.0.txt missing")
    print(f"verify: {explicit} explicit SPDX files, {annotated} annotated artifacts licensed")


def check_scope() -> None:
    result = subprocess.run(["git", "-C", str(SDK_ROOT), "status", "--porcelain=v1",
                             "--untracked-files=all"], capture_output=True, text=True,
                            check=True)
    for line in result.stdout.splitlines():
        path = line[3:] if len(line) > 3 else ""
        if " -> " in path:
            path = path.split(" -> ", 1)[1]
        if path and not path.startswith(TASK_PREFIX):
            fail("out of scope change: " + path)
    print("verify: write scope limited to the task-local evidence directory")


def check_local_asset() -> None:
    probe = reference.local_asset_probe()
    if not probe["checkout_present"]:
        print("verify: pinned checkout absent; asset identity checked from recorded pins only")
        return
    if probe["mismatches"]:
        fail("local pinned asset mismatch: " + ",".join(probe["mismatches"]))
    if probe["checkpoint_bytes"] != reference.CHECKPOINT_BYTES:
        fail("local checkpoint byte count mismatch")
    if probe["checkpoint_sha256"] != reference.CHECKPOINT_SHA256:
        fail("local checkpoint digest mismatch")
    print(f"verify: local pinned checkout matches {probe['checked']} source files and the checkpoint")


def main() -> int:
    manifest = read_manifest()
    check_pins(manifest)
    contract = strict_json(HERE / "contract.json")
    adapter = strict_json(HERE / "adapter.json")
    readiness = strict_json(HERE / "readiness.json")
    report = strict_json(HERE / "report.json")
    check_disposition(contract, adapter, readiness, report)
    digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
    check_report(report, digest)
    check_readme()
    check_reproduction(manifest, digest)
    check_licensing(manifest)
    check_scope()
    check_local_asset()
    print(f"verify: PASS report_sha256={digest} status={reference.STATUS} "
          f"decision={reference.DECISION}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
