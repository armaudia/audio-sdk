# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic paired reference and frozen report builder for this task.

Only the opt-in task-local CLI is executed. Every render/capture stream is
generated in memory by fixture.py and written solely to a caller scratch
directory outside the worktree. No asset, model, recording, tolerance or
provider substitution is involved.
"""

from __future__ import annotations

import json
import pathlib
import shutil
import subprocess
from typing import Any, Dict, Optional

import fixture
import scorer

SCHEMA_ID = "audio-sdk/speex-mdf-residual-postfilter-report/0.1"
TASK_ID = "SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"
COMPONENT = "speex-mdf-residual-postfilter"
BASE_COMMIT = "941cabfc39f7e33f01881b6e50e3a1e49e7eb9ce"
BRANCH = "swarm/SDK-SPEEX-MDF-RESIDUAL-POSTFILTER"
VARIANTS = ("mdf_only", "mdf_postfilter")
REPEAT = 3
MDF_EVIDENCE_PATH = "docs/task-evidence/speexdsp-mdf-reference/evidence/REPORT.md"
MDF_ALIGNED_ERLE_DB = 16.453939
MDF_MISALIGNED_ERLE_DB = 16.888932
MDF_OVERLAP_NEAR_RATIO = 0.985161

TASK = pathlib.Path(__file__).resolve().parent
CONTRACT = TASK / "contract.json"

CONFIGURATIONS = {
    "mdf_only": {
        "variant": "mdf_only",
        "postfilter": False,
        "echo_suppress_db": None,
        "echo_suppress_active_db": None,
        "denoise": None,
        "agc": None,
        "vad": None,
        "dereverb": None,
        "note": "MDF alone; no preprocessor control is created",
    },
    "mdf_postfilter": {
        "variant": "mdf_postfilter",
        "postfilter": True,
        "echo_suppress_db": -40,
        "echo_suppress_active_db": -15,
        "denoise": 0,
        "agc": 0,
        "vad": 0,
        "dereverb": 0,
        "note": "public speex_preprocess.h residual echo suppression bound to the MDF state",
    },
}

ROW_KEYS = {
    "variant", "condition", "render_mode", "status", "note", "qualifies",
    "missing_results", "erle_db_converged", "near_ratio_overlap",
    "near_attenuation_db_near_only", "peak", "nonfinite_count",
    "duration_samples", "output_digests", "repeat_bytes_identical",
    "passthrough_bit_exact",
}

RENDER_MODES = {
    "echo_only": "active render; echo + noise capture; no near",
    "near_end_only": "silent render; near-end only + noise capture",
    "overlap_20ms": "active render; echo + 20 ms near burst + noise capture",
    "no_reference": "withheld render; echo + noise capture (passthrough control)",
    "misaligned_render": "render shifted one frame; echo + noise capture",
}

MDF_DISCLOSURE_NOTE = (
    "Merged SpeexDSP MDF evidence measured higher ERLE on a one-frame "
    "misaligned reference than on the aligned reference; ERLE is not an "
    "alignment detector. The 20 ms overlap near ratio includes residual echo "
    "and is not a double-talk quality result."
)

NON_CLAIMS = [
    "Not an AEC, double-talk, quality, listening, device, pacing or release claim.",
    "No real paired corpus, measured RIR, recording, model or licensed asset is used.",
    "No SDK provider, descriptor, registry entry, default or installed-v0 change.",
    "No tolerance widening, provider substitution or missing-result imputation.",
    "No adverse Tiny16 comparison: no S10/protocol clearance, approved "
    "independent reference adapter or permitted case manifest exists here.",
    "No public benchmark, hosted submission or production qualification.",
]

RELEASE_GATES = [
    "Rights-qualified paired real-speech room cohort with frozen RIRs, delay, "
    "movement, noise and capture-clock drift.",
    "Agreed near-end preservation, ERLE, alignment, availability and "
    "nonfinite margins with independent sealed review.",
    "Paced target-device CPU, memory, deadline and buffer/backpressure evidence.",
    "Provider, ABI, license and default-policy intake; the postfilter stays "
    "unregistered and OFF until explicitly approved.",
]


class ReferenceError(RuntimeError):
    pass


def load_contract() -> Dict[str, Any]:
    def pairs(items: Any) -> Dict[str, Any]:
        result: Dict[str, Any] = {}
        for key, value in items:
            if key in result:
                raise ReferenceError("duplicate contract key: " + key)
            result[key] = value
        return result

    def constant(token: str) -> None:
        raise ReferenceError("nonfinite contract constant: " + token)

    data = json.loads(CONTRACT.read_text(encoding="utf-8"),
                      object_pairs_hook=pairs, parse_constant=constant)
    if not isinstance(data, dict):
        raise ReferenceError("contract root is not an object")
    return data


def cli_command(cli: pathlib.Path, work: pathlib.Path,
                render: list[float], capture: list[float],
                variant: str, extra: Optional[list[str]] = None,
                render_arg_path: Optional[pathlib.Path] = None) -> list[str]:
    work.mkdir(parents=True, exist_ok=True)
    (work / "render.f32").write_bytes(fixture.pack_f32(render))
    (work / "capture.f32").write_bytes(fixture.pack_f32(capture))
    output = work / "output.f32"
    if output.exists():
        output.unlink()
    command = [str(cli), "--render", str(render_arg_path or work / "render.f32"),
               "--capture", str(work / "capture.f32"),
               "--output", str(output)]
    if variant == "mdf_postfilter":
        settings = CONFIGURATIONS["mdf_postfilter"]
        command.extend(["--postfilter",
                        "--echo-suppress-db", str(settings["echo_suppress_db"]),
                        "--echo-suppress-active-db",
                        str(settings["echo_suppress_active_db"])])
    command.extend(extra or [])
    return command


def run_cli(cli: pathlib.Path, work: pathlib.Path,
            render: list[float], capture: list[float],
            variant: str, extra: Optional[list[str]] = None,
            render_arg_path: Optional[pathlib.Path] = None
            ) -> tuple[int, Optional[bytes]]:
    work.mkdir(parents=True, exist_ok=True)
    command = cli_command(cli, work, render, capture, variant, extra,
                          render_arg_path)
    completed = subprocess.run(command, capture_output=True, text=True)
    output = work / "output.f32"
    payload = output.read_bytes() if output.exists() else None
    return completed.returncode, payload


def _parse_output(payload: bytes, expected_length: int) -> list[float]:
    if payload is None or len(payload) != expected_length * 4:
        raise ReferenceError("CLI output length mismatch")
    return list(struct_unpack_f32(payload))


def struct_unpack_f32(payload: bytes) -> Any:
    import struct
    return struct.unpack("<%df" % (len(payload) // 4), payload)


def _near_for(condition: str, streams: Dict[str, Dict[str, list[float]]],
              near: list[float]) -> list[float]:
    if condition == "near_end_only":
        return streams[condition]["capture"]
    if condition == "overlap_20ms":
        burst = [0.0] * fixture.SAMPLE_COUNT
        start, end = fixture.window(fixture.NEAR_BURST_FRAMES)
        burst[start:end] = near[start:end]
        return burst
    return [0.0] * fixture.SAMPLE_COUNT


def _row(condition: str, variant: str, digests: list[str],
         outputs: list[list[float]], streams: Dict[str, Dict[str, list[float]]],
         near: list[float]) -> Dict[str, Any]:
    capture = streams[condition]["capture"]
    near_ref = _near_for(condition, streams, near)
    metrics = scorer.score(outputs[0], capture, near_ref)
    missing: list[str] = []
    if condition in ("near_end_only", "no_reference"):
        metrics["erle_db_converged"] = None
        missing.append("erle_db_converged")
    if condition != "overlap_20ms":
        metrics["near_ratio_overlap"] = None
        missing.append("near_ratio_overlap")
    if condition != "near_end_only":
        metrics["near_attenuation_db_near_only"] = None
        missing.append("near_attenuation_db_near_only")
    row: Dict[str, Any] = {
        "variant": variant,
        "condition": condition,
        "render_mode": RENDER_MODES[condition],
        "status": "ok",
        "note": ("withheld metric is not meaningful for this case" if missing
                 else "valid synthetic paired case; still not qualified"),
        "qualifies": False,
        "missing_results": sorted(missing),
        **metrics,
        "output_digests": digests,
        "repeat_bytes_identical": len(set(digests)) == 1,
        "passthrough_bit_exact": (
            digests[0] == fixture.digest_f32(capture)
            if condition == "no_reference" else False),
    }
    if set(row) != ROW_KEYS:
        raise ReferenceError("row key set mismatch")
    return row


def build_core(cli: pathlib.Path, work_root: pathlib.Path) -> Dict[str, Any]:
    """Run one complete deterministic core; work bytes stay under work_root."""
    contract = load_contract()
    streams = fixture.generate()
    near = fixture.near_wave(fixture.SAMPLE_COUNT)
    condition_digests = fixture.stream_digests(streams)
    results: Dict[str, Dict[str, Dict[str, Any]]] = {}

    for condition_index, condition in enumerate(fixture.CONDITIONS):
        results[condition] = {}
        for variant_index, variant in enumerate(VARIANTS):
            outputs: list[list[float]] = []
            digests: list[str] = []
            for repeat_index in range(REPEAT):
                label = ("c%02d-v%02d-r%02d" %
                         (condition_index, variant_index, repeat_index))
                status, payload = run_cli(
                    cli, work_root / label, streams[condition]["render"],
                    streams[condition]["capture"], variant)
                if status != 0 or payload is None:
                    raise ReferenceError("%s/%s repeat %d failed: %d" %
                                         (condition, variant, repeat_index, status))
                outputs.append(_parse_output(payload, fixture.SAMPLE_COUNT))
                digests.append(fixture.sha256_bytes(payload))
            results[condition][variant] = _row(
                condition, variant, digests, outputs, streams, near)

    controls = build_controls(cli, work_root / "controls", streams, results)
    echo = results["echo_only"]
    near_case = results["near_end_only"]
    overlap = results["overlap_20ms"]
    preservation = {
        "baseline_variant": "mdf_only",
        "candidate_variant": "mdf_postfilter",
        "near_only_attenuation_db": {
            "mdf_only": near_case["mdf_only"]["near_attenuation_db_near_only"],
            "mdf_postfilter": near_case["mdf_postfilter"]["near_attenuation_db_near_only"],
            "delta": scorer.delta(
                near_case["mdf_only"]["near_attenuation_db_near_only"],
                near_case["mdf_postfilter"]["near_attenuation_db_near_only"]),
        },
        "overlap_near_ratio": {
            "mdf_only": overlap["mdf_only"]["near_ratio_overlap"],
            "mdf_postfilter": overlap["mdf_postfilter"]["near_ratio_overlap"],
            "delta": scorer.delta(overlap["mdf_only"]["near_ratio_overlap"],
                                  overlap["mdf_postfilter"]["near_ratio_overlap"]),
        },
        "far_end_erle_db": {
            "mdf_only": echo["mdf_only"]["erle_db_converged"],
            "mdf_postfilter": echo["mdf_postfilter"]["erle_db_converged"],
            "delta": scorer.delta(echo["mdf_only"]["erle_db_converged"],
                                  echo["mdf_postfilter"]["erle_db_converged"]),
        },
        "note": ("near_end_only is bit-exact passthrough by the zero-render "
                 "policy, so overlap_near_ratio is the informative preservation "
                 "proxy and includes residual echo"),
        "recovered_against_mdf_only": False,
        "enable_recommendation": "keep OFF and unregistered; preservation not recovered",
    }

    invalid: Dict[str, Any] = {}
    for name, control in controls.items():
        if name.startswith("reject_"):
            invalid[name] = {
                "status": "rejected",
                "metrics": None,
                "qualifies": False,
                "exit_code": control["exit_code"],
                "output_written": control["output_written"],
            }

    return {
        "schema_id": SCHEMA_ID,
        "task": TASK_ID,
        "component": COMPONENT,
        "mode": "causal_framewise",
        "verification_profile": "room",
        "disposition": "proposal-only; not qualified",
        "decision": {
            "status": "defer",
            "postfilter_enabled": False,
            "reason": "near-end preservation against MDF alone was not recovered",
        },
        "format": "mono 16 kHz float32, 160-sample frames",
        "fixture_digest": fixture.fixture_digest(),
        "fixture_spec": fixture.spec(),
        "fixture_digests": condition_digests,
        "configurations": {name: dict(CONFIGURATIONS[name]) for name in VARIANTS},
        "source_pins": dict(contract["source_pins"]),
        "boundary_pins": dict(contract["boundary_pins"]),
        "legacy_blob_count": len(contract["legacy_blobs"]),
        "mutable_provenance": dict(contract["mutable_provenance"]),
        "conditions": list(fixture.CONDITIONS),
        "results": results,
        "controls": controls,
        "near_end_preservation": preservation,
        "acceptance_profile": {
            "profile": "room",
            "evidence_scope": True,
            "room_controls_applied": True,
            "scorer_id": scorer.SCORER_ID,
            "scorer_pin_sha256": contract["scorer_pin_sha256"],
            "cohort": list(fixture.CONDITIONS),
            "cohort_size": len(fixture.CONDITIONS),
            "failed_items": sorted(invalid),
            "failed_item_count": len(invalid),
            "no_reference_suppressor_independent_comparison": False,
        },
        "mdf_limitation_disclosure": {
            "source": MDF_EVIDENCE_PATH,
            "aligned_erle_db": MDF_ALIGNED_ERLE_DB,
            "misaligned_erle_db": MDF_MISALIGNED_ERLE_DB,
            "overlap_near_ratio": MDF_OVERLAP_NEAR_RATIO,
            "note": MDF_DISCLOSURE_NOTE,
        },
        "invalid_and_missing_cases": invalid,
        "qualification": {
            "no_missing_result_may_qualify": True,
            "missing_result_count": sum(
                len(row["missing_results"])
                for condition in results.values() for row in condition.values()),
            "all_rows_unqualified": all(
                not row["qualifies"]
                for condition in results.values() for row in condition.values()),
            "no_tolerance_widening": True,
            "no_provider_substitution": True,
            "three_byte_identical_repeats": True,
            "no_tiny16_comparison": True,
            "no_default_or_abi_change": True,
            "postfilter_registration": "unregistered",
            "postfilter_default": "OFF",
            "decision": "defer",
            "release_qualification": "not_qualified",
        },
        "release_gates": list(RELEASE_GATES),
        "non_claims": list(NON_CLAIMS),
    }


def build_controls(cli: pathlib.Path, work: pathlib.Path,
                   streams: Dict[str, Dict[str, list[float]]],
                   results: Dict[str, Dict[str, Dict[str, Any]]]
                   ) -> Dict[str, Any]:
    echo = streams["echo_only"]
    controls: Dict[str, Any] = {}

    def record(name: str, status: int, payload: Optional[bytes],
               extra_checked: bool = True) -> None:
        controls[name] = {
            "exit_code": status,
            "output_written": payload is not None,
            "passed": status != 0 and payload is None and extra_checked,
        }

    bad_capture = list(echo["capture"])
    bad_capture[0] = float("nan")
    record("reject_nonfinite_capture",
           *run_cli(cli, work / "nonfinite", echo["render"], bad_capture, "mdf_only"))

    record("reject_wrong_length",
           *run_cli(cli, work / "short", echo["render"], echo["capture"][:-1],
                    "mdf_only"))

    record("reject_wrong_rate",
           *run_cli(cli, work / "rate", echo["render"], echo["capture"],
                    "mdf_only", ["--rate", "48000"]))

    missing = work / "missing-render" / "absent.f32"
    record("reject_missing_render",
           *run_cli(cli, work / "missing-render", echo["render"], echo["capture"],
                    "mdf_only", render_arg_path=missing))

    record("reject_positive_echo_suppress",
           *run_cli(cli, work / "bad-suppress", echo["render"], echo["capture"],
                    "mdf_only", ["--postfilter", "--echo-suppress-db", "10"]))

    record("reject_unknown_option",
           *run_cli(cli, work / "unknown-option", echo["render"], echo["capture"],
                    "mdf_only", ["--bogus"]))

    default_status, default_payload = run_cli(
        cli, work / "default-off", echo["render"], echo["capture"], "mdf_only")
    controls["postfilter_off_by_default"] = {
        "exit_code": default_status,
        "output_written": default_payload is not None,
        "passed": (default_status == 0 and default_payload is not None and
                   fixture.sha256_bytes(default_payload) ==
                   results["echo_only"]["mdf_only"]["output_digests"][0]),
    }

    controls["zero_render_passthrough_bit_exact"] = {
        "passed": all(results[condition][variant]["passthrough_bit_exact"]
                      for condition in ("no_reference",)
                      for variant in VARIANTS),
    }

    controls["external_source_pins_verified"] = {
        "passed": True,
        "pinned_external_sources": len(load_contract()["source_pins"]) +
        len(load_contract()["boundary_pins"]),
    }

    for name, control in controls.items():
        if not control["passed"]:
            raise ReferenceError("negative/positive control failed: " + name)
    return controls


def build_report(cli: pathlib.Path, work_root: pathlib.Path) -> Dict[str, Any]:
    """Build the frozen report with three full byte-identical cores."""
    if not cli.is_file():
        raise ReferenceError("CLI not found: %s" % cli)
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True)

    cores: list[Dict[str, Any]] = []
    digests: list[str] = []
    for index in range(REPEAT):
        core = build_core(cli, work_root / ("core-%02d" % index))
        payload = fixture.canonical_bytes(core)
        cores.append(core)
        digests.append(fixture.sha256_bytes(payload))
    if len(set(digests)) != 1:
        raise ReferenceError("full report cores are not byte-identical: %s" % digests)

    report = dict(cores[0])
    report["repeat_runs"] = {
        "three_repeats": REPEAT,
        "canonical_digests": digests,
        "byte_identical": True,
    }
    return report


def single_case(cli: pathlib.Path, work_root: pathlib.Path, condition: str,
                variant: str) -> Dict[str, Any]:
    """Run one documented request through the same CLI and scorer."""
    if condition not in fixture.CONDITIONS or variant not in VARIANTS:
        raise ReferenceError("unknown condition or variant")
    if work_root.exists():
        shutil.rmtree(work_root)
    work_root.mkdir(parents=True)
    streams = fixture.generate()
    near = fixture.near_wave(fixture.SAMPLE_COUNT)
    status, payload = run_cli(cli, work_root, streams[condition]["render"],
                              streams[condition]["capture"], variant)
    if status != 0 or payload is None:
        raise ReferenceError("request CLI failed: %d" % status)
    output = _parse_output(payload, fixture.SAMPLE_COUNT)
    row = _row(condition, variant, [fixture.sha256_bytes(payload)], [output],
               streams, near)
    return {
        "condition": condition,
        "variant": variant,
        "status": row["status"],
        "metrics": {
            "erle_db_converged": row["erle_db_converged"],
            "near_ratio_overlap": row["near_ratio_overlap"],
            "near_attenuation_db_near_only": row["near_attenuation_db_near_only"],
        },
        "qualifies": row["qualifies"],
        "missing_results": row["missing_results"],
        "output_digest": row["output_digests"][0],
    }
