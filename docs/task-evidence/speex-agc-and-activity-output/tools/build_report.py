# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Build the frozen canonical report from the exact pinned SpeexDSP sources."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import platform
import shutil
import struct
import subprocess
import sys

sys.path.insert(0, str(Path(__file__).resolve().parent))
import common as c
import fixtures as f

VERIFICATION_WS = c.WS_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION.md"
VERIFICATION_PAGES = c.WS_ROOT / "audio-benchmark-platform/plan/swarm/VERIFICATION_PAGES.md"
VERIFICATION_DIGEST = "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910"
SWARM_CHECK = c.WS_ROOT / "audio-benchmark-platform/plan/swarm/check.py"


def digest_path(path: Path) -> str:
    return c.digest_bytes(path.read_bytes())


def run(cmd, cwd=None, check=True):
    proc = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True, check=False)
    if check and proc.returncode != 0:
        raise RuntimeError(f"command failed ({proc.returncode}): {cmd}\n{proc.stdout}\n{proc.stderr}")
    return proc


def sha256_file(path: Path) -> str:
    return digest_path(path)


def main() -> int:
    scratch = Path(os.environ.get(
        "SPEEX_ACTIVITY_SCRATCH", "/private/var/folders/hl/n3qd3bjs2ps_hq801c03w2gh0000gn/T/opencode/speex-agc-activity-report"))
    if scratch.exists():
        shutil.rmtree(scratch)
    scratch.mkdir(parents=True)
    build = scratch / "build"
    preproc_build = scratch / "preprocessed"
    run(["cmake", "-S", str(c.TASK / "adapter"), "-B", str(build),
         "-DCMAKE_BUILD_TYPE=Release", "-DAS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE=ON"])
    run(["cmake", "--build", str(build), "--parallel", "4"])
    smoke = run(["ctest", "--test-dir", str(build), "--output-on-failure"])
    if "100% tests passed, 0 tests failed out of 1" not in smoke.stdout:
        raise RuntimeError("native adapter smoke test did not pass: " + smoke.stdout)
    smoke_summary = "1/1 native adapter smoke test passed"
    cli = build / "speexagc_activity_cli"
    if not cli.is_file():
        raise RuntimeError("CLI not built")

    stimulus_info = f.write_fixtures(scratch)
    stimuli = {name: scratch / (name + ".f32") for name in stimulus_info}

    cases = []
    for spec in c.CASES:
        if spec["id"] == "combined_nonfinite":
            continue
        repeats = []
        for repeat in range(c.REPEATS):
            result = c.run_cli(cli, scratch, stimuli[spec["stimulus"]], spec["config"],
                               spec["id"], repeat)
            repeats.append(result)
        output_digests = [c.digest_bytes(r["output_bytes"]) for r in repeats]
        meta_digests = [c.digest_bytes(r["meta_bytes"]) for r in repeats]
        if len(set(output_digests)) != 1 or len(set(meta_digests)) != 1:
            raise RuntimeError("non-byte-identical repeats for " + spec["id"])
        # Read back the canonical repeat to compute the reported metrics.
        raw = repeats[0]["output_bytes"]
        metrics = c.output_metrics(raw)
        activity = c.activity_metrics(repeats[0]["records"])
        source_sha = sha256_file(stimuli[spec["stimulus"]])
        expected_source = stimulus_info[spec["stimulus"]]["input_sha256"]
        if source_sha != expected_source:
            raise RuntimeError("stimulus digest mismatch")
        cases.append({
            "id": spec["id"],
            "stimulus": spec["stimulus"],
            "control": spec["control"],
            "config": spec["config"],
            "input": {"sha256": source_sha, "bytes": len(raw)},
            "output": {
                "sha256": output_digests[0],
                "bytes": len(raw),
                "metrics": metrics,
                "activity": activity,
                "meta_sha256": meta_digests[0],
            },
            "repeats": {
                "count": c.REPEATS,
                "status": "byte_identical",
                "output_sha256": output_digests,
                "meta_sha256": meta_digests,
            },
        })

    # Fail-closed numerical control: the CLI must reject the intentionally
    # invalid nonfinite stimulus rather than produce output.
    nonfinite = scratch / "nonfinite.f32"
    nonfinite.write_bytes(f.f32_bytes(f.nonfinite()))
    reject = subprocess.run(
        [str(cli), "--input", str(nonfinite), "--output", str(scratch / "nf-out.f32"),
         "--meta", str(scratch / "nf-meta.json")] + c.cli_arguments(c.DEFAULT_CONFIG),
        capture_output=True, text=True, check=False)
    nonfinite_control = {
        "stimulus": "nonfinite",
        "input_sha256": sha256_file(nonfinite),
        "expected": "reject_exit_3",
        "observed_exit": reject.returncode,
        "stderr": reject.stderr.strip(),
        "status": "pass" if reject.returncode == 3 and "samples" in reject.stderr else "fail",
    }

    # Delay measurement: the Speex preprocessor buffers a 160-sample frame
    # before emitting output, so a lone impulse placed at input sample 400 is
    # observed at output sample 560. This is true even with AGC, VAD and
    # denoise all disabled, so "identity" here means identity of the feature
    # flags, not bit-exact passthrough. Only the measured peak indices are
    # reported; no separate gain-delay assertion is made.
    input_impulse_index = 400
    impulse_raw = (scratch / ("identity_impulse-r0.f32")).read_bytes()
    identity_peak_index = max(range(f.SAMPLES), key=lambda i: abs(struct.unpack_from("<f", impulse_raw, i * 4)[0]))
    combined_raw = (scratch / ("combined_impulse-r0.f32")).read_bytes()
    combined_values = struct.unpack("<" + str(f.SAMPLES) + "f", combined_raw)
    combined_peak_index = max(range(f.SAMPLES), key=lambda i: abs(combined_values[i]))
    if identity_peak_index < input_impulse_index or combined_peak_index < input_impulse_index:
        raise RuntimeError("impulse peak moved before input location")

    pins = c.source_pins()
    if any(pin["status"] != "match" for pin in pins):
        raise RuntimeError("source pin mismatch: " + str([p for p in pins if p["status"] != "match"]))

    # Read-only board check; verification itself is read-only and contains no
    # mutable board snapshot. The report must regenerate byte-identically from
    # any clean export at this exact head. Base and parent are pinned from the
    # task definition and worktree history observed before the commit.
    base_parent = "56d9781b984aa493e5c56e0479a20c746351102e"
    verification_digest = digest_path(VERIFICATION_WS)
    if verification_digest != VERIFICATION_DIGEST:
        raise RuntimeError("VERIFICATION.md digest changed: " + verification_digest)
    verification_pages_digest = digest_path(VERIFICATION_PAGES) if VERIFICATION_PAGES.is_file() else None
    check_proc = run(["python3", str(SWARM_CHECK), "--task", c.TASK_ID],
                     cwd=c.SDK_ROOT, check=False)
    if check_proc.returncode != 0:
        raise RuntimeError("swarm check failed: " + check_proc.stderr)

    sources_digest = c.digest_bytes((c.TASK / "SOURCES.sha256").read_bytes())
    adapter_json_digest = sha256_file(c.TASK / "adapter.json")
    contract_json_digest = sha256_file(c.TASK / "contract.json")

    report = {
        "schema": c.SCHEMA,
        "task": c.TASK_ID,
        "status": "proposal_only_synthetic_complete_pending_review",
        "claim_level": "synthetic_evidence_only",
        "base_commit": c.BASE_COMMIT,
        "base_parent": base_parent,
        "branch": c.BRANCH,
        "verification": {
            "profile": "plan/swarm/VERIFICATION.md DSP acceptance profile",
            "path": "ws:audio-benchmark-platform/plan/swarm/VERIFICATION.md",
            "sha256": verification_digest,
            "verification_pages_sha256": verification_pages_digest,
            "check_command": ["python3", "plan/swarm/check.py", "--task", c.TASK_ID],
            "check_exit": check_proc.returncode,
            "read_only": True,
        },
        "scope": {
            "write_scope": ["docs/task-evidence/speex-agc-and-activity-output/"],
            "public_api_changed": False,
            "abi_changed": False,
            "default_provider_changed": False,
            "provider_registry_changed": False,
            "shared_sources_modified": [],
            "shared_build_targets_added": [],
            "shared_cmake_modified": False,
            "installed_speex_v0_behavior_changed": False,
            "assets_or_reports_outside_task_dir": [],
            "real_audio_used": False,
            "corpus_model_weights_download_used": False,
            "listening_quality_device_or_pacing_claim": False,
            "public_benchmark_claim": False,
            "tiny16_comparison_claim": False,
            "activity_advisory_only": True,
            "activity_gates_audio": False,
        },
        "adapter": {
            "adapter_json_sha256": adapter_json_digest,
            "contract_json_sha256": contract_json_digest,
            "source_pins": pins,
            "sources_sha256_file_sha256": sources_digest,
            "protocol_version": 1,
            "identity": "speex-agc-activity-reference-v1",
            "registration": "unregistered-developer-only",
            "opt_in_cmake_option": "AS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE",
            "default_enabled": False,
            "preprocessor_instances_per_stream": 1,
            "frame_samples": c.FRAME,
            "sample_rate_hz": 16000,
            "public_api": "speex/speex_preprocess.h",
            "agc_ctl": "SPEEX_PREPROCESS_SET_AGC=1 (float build)",
            "activity_ctl": "speex_preprocess_run() return plus GET_PROB metadata, advisory",
            "audio_path": "float -> PCM16 clamp/lrintf(FE_TONEAREST) -> one preprocessor -> float/32768",
            "denoise_default": 0,
            "dereverb": 0,
            "smoke_test": smoke_summary,
        },
        "stimuli": stimulus_info,
        "cases": cases,
        "controls": {
            "fail_closed_nonfinite": nonfinite_control,
            "input_impulse_index": input_impulse_index,
            "identity_impulse_peak_index": identity_peak_index,
            "combined_impulse_peak_index": combined_peak_index,
            "identity_delay_samples": identity_peak_index - input_impulse_index,
            "combined_delay_samples": combined_peak_index - input_impulse_index,
            "delay_note": "160-sample (10 ms at 16 kHz) shared preprocessor lookahead is present even with all feature flags off; only measured impulse peak indices are reported",
            "combined_activity_sequence_differs_from_agc_only": (
                next(item for item in cases if item["id"] == "combined_speech_like")["output"]["activity"]["advisory_vad_sequence"]
                != next(item for item in cases if item["id"] == "agc_only_speech_like")["output"]["activity"]["advisory_vad_sequence"]),
        },
        "acceptance_profile_coverage": {
            "sweeps": ["combined_chirp", "combined_gain_step"],
            "steps": ["combined_steps", "fast_steps", "reset_steps"],
            "impulses": ["combined_impulse", "identity_impulse"],
            "silence": ["combined_silence", "identity_silence"],
            "clean_speech_control": ["combined_speech_like", "identity_speech_like"],
            "intelligibility_or_load_control": [
                "speech_like surrogate burst envelope (intelligibility-shaped control)",
                "LCG noise_only non-speech control",
            ],
            "gain": ["agc_gain_db_min", "agc_gain_db_max", "agc_gain_db_sequence"],
            "response": ["chirp output metrics", "impulse peak location", "gain_step output metrics"],
            "attack_release": ["combined_steps", "fast_steps", "reset_steps"],
            "headroom": ["peak_abs", "clipped_or_at_one"],
            "delay": ["identity_impulse_peak_index", "combined_impulse_peak_index"],
            "numerical_behavior": ["fail_closed_nonfinite", "nonfinite_count", "output finite check"],
            "state_transitions": ["reset_steps", "silence to speech burst sequence", "loud to quiet step sequence"],
            "interacting_nonlinear_configurations": [
                "combined AGC + advisory VAD",
                "combined_denoise_speech_like",
                "prob_60_40_speech_like",
                "prob_10_5_speech_like",
                "target_4096_speech_like",
                "target_16384_speech_like",
            ],
        },
        "remaining_release_gates": [
            "Reviewer acceptance of this synthetic, task-local evidence package",
            "No public registry, ABI, default or shared build change may be introduced at promotion time",
            "Target-device, real-speech, listening, quality and pacing validation if a product claim is ever sought",
            "If any Tiny16 comparison is desired, obtain S10/protocol clearance, approved independent reference adapter and permitted case manifest first",
            "Exact pinned comparisons and three byte-identical repeats must be preserved in any follow-on evidence",
        ],
        "environment": {
            "python": sys.version,
            "platform": platform.platform(),
            "cmake": run(["cmake", "--version"]).stdout.splitlines()[0],
            "compiler": run(["cc", "--version"]).stdout.splitlines()[0],
            "jsonschema_dependency_used": False,
            "strict_json_validation": "duplicate keys and NaN/Infinity constants rejected; exact key sets and integer types checked",
        },
    }
    report_path = Path(os.environ.get("SPEEX_ACTIVITY_REPORT_PATH", str(c.REPORT_PATH)))
    report_path.parent.mkdir(parents=True, exist_ok=True)
    report_path.write_bytes(c.canonical_bytes(report))
    print("report_sha256=" + digest_path(report_path))
    print("report_bytes=" + str(report_path.stat().st_size))
    print("cases=" + str(len(cases)))
    print("pins=" + str(len(pins)))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
