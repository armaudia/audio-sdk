# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic stdlib-only tests for the DPDFNet baseline streaming evidence.

No network, no downloads, no weights, no skips.  Every check runs against the
synthetic boundary model only; nothing here qualifies the candidate.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

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
    "rights_cleared_paired_cohort",
    "independent_scoring_and_listening",
    "target_runtime_timing",
    "provider_intake_and_default_selection",
}
EXPECTED_CONFIG = {
    "wrong_sample_rate": "sample_rate_hz_mismatch",
    "wrong_channels": "channels_mismatch",
    "wrong_sample_format": "sample_format_mismatch",
    "wrong_frame_samples": "frame_samples_mismatch",
    "wrong_max_stream_samples": "max_stream_samples_invalid",
    "offline_mode_unsupported": "mode_unsupported",
    "wrong_declared_lag": "declared_lag_mismatch",
    "caller_asset_unavailable": "asset_not_admitted",
    "surrogate_without_opt_in": "surrogate_opt_in_required",
    "wrong_asset_identity": "asset_identity_mismatch",
    "wrong_asset_bytes": "asset_identity_mismatch",
}
EXPECTED_FRAMES = {
    "empty_frame": "rejected:frame_length",
    "short_frame": "rejected:frame_length",
    "oversized_frame": "rejected:frame_length",
    "nonfinite_sample": "rejected:nonfinite_sample",
    "infinite_sample": "rejected:nonfinite_sample",
    "string_frame": "rejected:frame_type_invalid",
    "boolean_sample": "rejected:sample_type_invalid",
    "out_of_range_sample": "rejected:out_of_range_sample",
    "stale_epoch": "rejected:stale_epoch",
    "final_padding_nonzero": "rejected:final_padding_nonzero",
    "final_valid_count_invalid": "rejected:final_valid_count",
    "valid_count_without_final": "rejected:valid_count_without_final",
    "after_final": "rejected:final_input_already_seen",
    "after_close": "rejected:session_closed",
    "stream_oversized": "rejected:stream_oversized",
    "drain_before_final": "rejected:not_draining",
}


def _no_duplicates(pairs):
    seen = set()
    for key, _value in pairs:
        if key in seen:
            raise ValueError("duplicate key: " + key)
        seen.add(key)
    return dict(pairs)


def load_strict(name: str):
    return json.loads((HERE / name).read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)


def report() -> dict:
    return reference.build_report()


class TestCanonicalJson(unittest.TestCase):
    def test_canonical_bytes_sorted_compact(self):
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": [2, 3]}), b'{"a":[2,3],"b":1}')

    def test_negative_zero_normalized(self):
        self.assertEqual(reference.canonical_bytes({"x": -0.0}), b'{"x":0.0}')

    def test_nonfinite_rejected(self):
        for bad in (float("nan"), float("inf"), float("-inf")):
            with self.assertRaises(ValueError):
                reference.canonical_bytes({"x": bad})

    def test_duplicate_keys_rejected(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / "dup.json"
            path.write_text('{"a":1,"a":2}\n', encoding="ascii")
            with self.assertRaises(ValueError):
                json.loads(path.read_text(encoding="ascii"), object_pairs_hook=_no_duplicates)

    def test_report_bytes_end_with_single_newline(self):
        payload = reference.canonical_report_bytes(report())
        self.assertTrue(payload.endswith(b"\n"))
        self.assertFalse(payload.endswith(b"\n\n"))
        payload.decode("ascii")


class TestTaskIdentity(unittest.TestCase):
    def test_stable_digest_is_stable_and_excludes_mutable_fields(self):
        identity = reference.task_identity()
        self.assertEqual(identity["stable_sha256"], reference.stable_identity_digest())
        for key in ("status", "owner", "claim", "review", "handoff", "blocked_reason"):
            self.assertNotIn(key, identity)
        self.assertFalse(identity["board_full_file_hashed"])
        self.assertEqual(identity["id"], reference.TASK)

    def test_stable_digest_ignores_reordered_input(self):
        reordered = dict(reversed(list(reference.STABLE_TASK_IDENTITY.items())))
        self.assertEqual(
            reference.stable_identity_digest(reordered),
            reference.stable_identity_digest(),
        )

    def test_mutable_board_file_is_not_pinned(self):
        text = "\n".join(reference.SOURCE_PINS) + "\n" + "\n".join(reference.BOUNDARY_PINS)
        self.assertNotIn("plan/swarm/TASKS.json", text)
        self.assertFalse(report()["pins"]["board_file_pinned"])


class TestAssetBoundary(unittest.TestCase):
    def test_exact_candidate_pins(self):
        ref = reference.asset_ref()
        self.assertEqual(ref["asset_id"], "baseline.onnx")
        self.assertEqual(ref["byte_count"], 8_722_707)
        self.assertEqual(
            ref["sha256"],
            "371d26182aff0e1e0d31354e24c81f79cd57458f5a7dd003fc10a7ebf64255e0",
        )
        self.assertEqual(ref["storage"], "external")
        self.assertIsNone(ref["model_revision"])
        self.assertEqual(ref["official_model_snapshot"], "1a80d48e150711322f84cb9d4c91b3520045cf64")
        self.assertFalse(ref["runtime_available"])
        self.assertFalse(ref["rights_cleared"])
        self.assertFalse(ref["asset_bytes_read"])

    def test_candidate_admission_blocked(self):
        admission = reference.asset_admission()
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(
            admission["reason_codes"],
            [
                "model_revision_unpinned",
                "download_revision_mutable",
                "asset_bytes_absent",
                "runtime_unavailable",
                "rights_not_cleared",
            ],
        )
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])

    def test_candidate_bytes_absent(self):
        self.assertFalse((reference.SDK_ROOT / reference.ASSET_PATH).is_file())

    def test_synthetic_admission_control_is_not_candidate(self):
        control = reference.synthetic_admission_control()
        self.assertEqual(control["status"], "admitted_synthetic_control")
        self.assertFalse(control["candidate_asset"])
        self.assertFalse(control["vendor_runtime_invoked"])
        self.assertEqual(control["qualification_effect"], "none")
        self.assertNotEqual(control["asset_id"], reference.ASSET_ID)

    def test_synthetic_asset_is_derived_not_model_bytes(self):
        self.assertEqual(
            reference.SYNTHETIC_ASSET_SHA256,
            hashlib.sha256(reference.SYNTHETIC_ASSET_BYTES).hexdigest(),
        )
        self.assertLess(len(reference.SYNTHETIC_ASSET_BYTES), 100_000)
        self.assertNotIn(b"ONNX", reference.SYNTHETIC_ASSET_BYTES)


class TestConfigRejections(unittest.TestCase):
    def test_matrix_exact_statuses(self):
        cases = reference.config_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_CONFIG) | {"synthetic_admission_control"})
        for name, reason in EXPECTED_CONFIG.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], "rejected")
                self.assertEqual(cases[name]["reason_codes"], [reason])
                self.assertFalse(cases[name]["processing_attempted"])
        self.assertEqual(cases["synthetic_admission_control"]["status"], "admitted_synthetic_control")

    def test_unknown_key_rejected(self):
        config = reference.default_config()
        config["unknown"] = 1
        self.assertEqual(reference.admit_config(config)["reason_codes"], ["config_keys_mismatch"])

    def test_non_dict_config_rejected(self):
        self.assertEqual(reference.admit_config([])["reason_codes"], ["config_type_invalid"])

    def test_candidate_config_never_creates(self):
        session = reference.StreamingSession()
        self.assertFalse(session.created)
        result = session.process([0.0] * reference.FRAME_SAMPLES)
        self.assertEqual(result["status"], "rejected:not_admitted")
        self.assertFalse(result["qualifies"])

    def test_synthetic_requires_opt_in(self):
        config = reference.synthetic_config()
        config["surrogate_opt_in"] = False
        self.assertEqual(reference.admit_config(config)["reason_codes"], ["surrogate_opt_in_required"])

    def test_small_stream_limit_is_admissible(self):
        config = reference.synthetic_config()
        config["max_stream_samples"] = reference.FRAME_SAMPLES
        self.assertTrue(reference.admit_config(config)["status"].startswith("admitted"))


class TestFrameRejections(unittest.TestCase):
    def test_matrix_exact_statuses_and_state_unchanged(self):
        cases = reference.frame_rejection_matrix()
        self.assertEqual(set(cases), set(EXPECTED_FRAMES))
        for name, status in EXPECTED_FRAMES.items():
            with self.subTest(name=name):
                self.assertEqual(cases[name]["status"], status)
                self.assertTrue(cases[name]["state_unchanged"])
                self.assertEqual(cases[name]["output_samples"], 0)

    def test_length_boundaries(self):
        session = reference.StreamingSession(reference.synthetic_config())
        self.assertEqual(session.process([0.0] * 159)["status"], "rejected:frame_length")
        self.assertEqual(session.process([0.0] * 161)["status"], "rejected:frame_length")
        self.assertEqual(session.process([0.0] * reference.FRAME_SAMPLES)["status"], "ok")

    def test_max_abs_boundary(self):
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process([reference.MAX_ABS_INPUT] + [0.0] * 159)
        self.assertEqual(result["status"], "ok")
        session = reference.StreamingSession(reference.synthetic_config())
        result = session.process([reference.MAX_ABS_INPUT + 1e-6] + [0.0] * 159)
        self.assertEqual(result["status"], "rejected:out_of_range_sample")

    def test_rejection_after_success_does_not_advance(self):
        session = reference.StreamingSession(reference.synthetic_config())
        first = session.process([0.01] * reference.FRAME_SAMPLES)
        self.assertEqual(first["status"], "ok")
        digest = session.state_digest()
        for bad in ([], "x", [float("nan")] * 160, [True] * 160):
            result = session.process(bad)
            self.assertTrue(result["status"].startswith("rejected:"))
            self.assertEqual(session.state_digest(), digest)

    def test_stream_limit_rejects_before_advancing(self):
        config = reference.synthetic_config()
        config["max_stream_samples"] = reference.FRAME_SAMPLES
        session = reference.StreamingSession(config)
        self.assertEqual(session.process([0.01] * 160)["status"], "ok")
        digest = session.state_digest()
        self.assertEqual(session.process([0.01] * 160)["status"], "rejected:stream_oversized")
        self.assertEqual(session.state_digest(), digest)


class TestStreamingSemantics(unittest.TestCase):
    def test_full_stream_accounting(self):
        _target, observed = reference.synth("active_speech")
        run = reference.run_stream(observed)
        self.assertEqual(run["input_samples"], reference.SAMPLES)
        self.assertEqual(run["process_calls"], reference.SAMPLES // reference.FRAME_SAMPLES)
        self.assertEqual(run["drain_calls"], 4)
        self.assertEqual(run["raw_length"], reference.SAMPLES + reference.DECLARED_LAG_SAMPLES)
        self.assertEqual(run["valid_length"], reference.SAMPLES)
        self.assertEqual(run["startup_invalid_samples"], reference.DECLARED_LAG_SAMPLES)
        self.assertTrue(run["conservation_exact"])
        self.assertEqual(run["intervals"][0]["source_start"], 0)
        self.assertEqual(run["intervals"][0]["output_start"], reference.DECLARED_LAG_SAMPLES)
        self.assertEqual(run["intervals"][-1]["source_end"], reference.SAMPLES)

    def test_partial_tail_accounting(self):
        _target, observed = reference.synth("active_speech")
        partial = observed + observed[:123]
        run = reference.run_stream(partial)
        self.assertEqual(run["input_samples"], 32_123)
        self.assertEqual(run["process_calls"], 201)
        self.assertEqual(run["drain_calls"], 4)
        self.assertEqual(run["final_padding_samples"], 37)
        self.assertEqual(run["raw_length"], 32_123 + reference.DECLARED_LAG_SAMPLES)
        self.assertEqual(run["valid_length"], 32_123)
        self.assertTrue(run["conservation_exact"])
        self.assertEqual(run["intervals"][-1]["source_end"], 32_123)

    def test_short_and_empty_streams(self):
        _target, observed = reference.synth("active_speech")
        short = reference.run_stream(observed[:100])
        self.assertEqual(short["process_calls"], 1)
        self.assertEqual(short["drain_calls"], 4)
        self.assertEqual(short["raw_length"], 100 + reference.DECLARED_LAG_SAMPLES)
        self.assertEqual(short["valid_length"], 100)
        self.assertTrue(short["conservation_exact"])
        empty = reference.run_stream([])
        self.assertEqual(empty["raw_length"], 0)
        self.assertEqual(empty["valid_length"], 0)
        self.assertEqual(empty["drain_calls"], 0)
        self.assertTrue(empty["conservation_exact"])

    def test_block_control_matches_streamed(self):
        _target, observed = reference.synth("active_speech")
        streamed = reference.run_stream(observed)
        self.assertEqual(reference.output_digest(reference.raw_block_output(observed)),
                         streamed["raw_digest"])
        self.assertEqual(reference.output_digest(reference.surrogate_block(observed)),
                         streamed["valid_digest"])

    def test_impulse_lag_is_exactly_declared(self):
        probe = reference.streaming_semantics()["impulse_probe"]
        self.assertEqual(probe["raw_lag_samples"], reference.DECLARED_LAG_SAMPLES)
        self.assertEqual(probe["residual_lag_samples"], 0)
        self.assertFalse(probe["measured_latency"])

    def test_non_divisible_delay_mapping(self):
        mapping = reference.streaming_semantics()["mapping_control"]
        self.assertEqual(mapping["delay_samples"], 400)
        self.assertFalse(mapping["delay_divisible_by_frame"])
        self.assertEqual(mapping["valid_offset"], 80)
        self.assertEqual(mapping["valid_count"], 80)
        self.assertEqual(mapping["source_first_sample"], -80)
        self.assertTrue(mapping["matches_expected"])

    def test_reset_replay_and_rejections(self):
        probe = reference.streaming_semantics()["reset_probe"]
        self.assertEqual(probe["reset_status"], "ok_reset")
        self.assertTrue(probe["reset_replay_identical"])
        self.assertEqual(probe["first_stream_digest"], probe["after_reset_digest"])
        self.assertEqual(probe["stale_epoch_rejected"], "rejected:epoch_not_greater")
        self.assertEqual(probe["negative_origin_rejected"], "rejected:first_input_sample_invalid")

    def test_reset_during_draining_cancels(self):
        session = reference.StreamingSession(reference.synthetic_config())
        self.assertEqual(session.process([0.01] * 160, final=True)["status"], "ok")
        self.assertEqual(session.phase, "draining")
        result = session.reset(2, 0)
        self.assertEqual(result["status"], "ok_reset")
        self.assertEqual(session.phase, "processing")
        self.assertGreater(session.counters["cancelled_intervals"], 0)

    def test_drain_finite_and_eos_idempotent(self):
        session = reference.StreamingSession(reference.synthetic_config())
        session.process([0.01] * 160, final=True)
        calls = 0
        while True:
            result = session.drain()
            if result["status"] == "end_of_stream":
                break
            self.assertEqual(result["status"], "ok")
            calls += 1
            self.assertLessEqual(calls, reference.MAX_DRAIN_CALLS)
        self.assertLessEqual(calls, reference.MAX_DRAIN_CALLS)
        self.assertEqual(session.drain()["status"], "end_of_stream")
        self.assertEqual(session.process([0.01] * 160)["status"],
                         "rejected:final_input_already_seen")

    def test_begin_drain_is_not_repeated(self):
        session = reference.StreamingSession(reference.synthetic_config())
        session.process([0.01] * 160)
        self.assertEqual(session.begin_drain()["status"], "ok")
        self.assertEqual(session.begin_drain()["status"], "rejected:drain_already_begun")

    def test_deterministic_runs_and_state(self):
        _target, observed = reference.synth("quiet_speech")
        one = reference.run_stream(observed)
        two = reference.run_stream(observed)
        self.assertEqual(one["raw_digest"], two["raw_digest"])
        self.assertEqual(one["valid_digest"], two["valid_digest"])
        self.assertEqual(one["final_state_digest"], two["final_state_digest"])


class TestSyntheticResults(unittest.TestCase):
    def test_identity_is_exact_passthrough(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            self.assertTrue(results[condition]["identity_exact"])
            self.assertEqual(
                results[condition]["identity_passthrough"]["output_sha256"],
                results[condition]["noisy_control"]["output_sha256"],
            )

    def test_block_control_matches_streamed(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            self.assertTrue(results[condition]["block_matches_streamed"])

    def test_outputs_finite_and_peak_bounded(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant in ("identity_passthrough", "noisy_control",
                            "surrogate_streamed_160", "surrogate_block_control"):
                with self.subTest(condition=condition, variant=variant):
                    metrics = results[condition][variant]
                    self.assertEqual(metrics["nonfinite_count"], 0)
                    self.assertEqual(metrics["output_samples"], reference.SAMPLES)
                    self.assertLessEqual(metrics["peak_abs"], 1.0)
                    self.assertEqual(metrics["clipped_count"], 0)

    def test_idle_noise_has_no_target_metrics(self):
        metrics = reference.synthetic_results()["idle_noise"]["surrogate_streamed_160"]
        self.assertIsNone(metrics["noisy_snr_db"])
        self.assertIsNone(metrics["surrogate_snr_db"])
        self.assertIsNone(metrics["delta_snr_db"])

    def test_metrics_are_finite_or_none(self):
        results = reference.synthetic_results()
        for condition in reference.CONDITIONS:
            for variant, metrics in results[condition].items():
                if not isinstance(metrics, dict):
                    continue
                for key, value in metrics.items():
                    if isinstance(value, float):
                        self.assertTrue(math.isfinite(value), f"{condition}/{variant}/{key}")


class TestReportDisposition(unittest.TestCase):
    def test_machine_readable_disposition(self):
        value = report()
        self.assertEqual(value["decision"], "DEFER")
        self.assertEqual(value["defer_before"], "processor_exposure")
        self.assertEqual(value["status"], "proposal_only_synthetic_incomplete")
        self.assertEqual(value["evidence_status"], "incomplete")
        self.assertEqual(value["qualification"]["status"], "not_qualified")
        self.assertFalse(value["qualification"]["qualified"])
        self.assertFalse(value["qualification"]["missing_result_may_qualify"])

    def test_exactly_eight_blocked_gates(self):
        value = report()
        gates = value["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual(value["release_gate_count"], 8)
        self.assertEqual({gate["name"] for gate in gates}, EXPECTED_GATES)
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(value["counts"]["release_gates_blocked"], 8)

    def test_no_claim_is_true(self):
        for name, claimed in report()["claims"].items():
            with self.subTest(claim=name):
                self.assertFalse(claimed)

    def test_boundary_preserved(self):
        boundary = report()["boundary"]
        for name in ("registered", "enabled_by_default", "default_selected",
                     "public_api_abi_change", "provider_registration",
                     "descriptor_registry_change", "installed_v0_behavior_change",
                     "shared_build_or_ci_change", "processor_exposure",
                     "task_board_or_handoff_write", "streaming_mode_added",
                     "adapter_json_added", "readiness_json_added"):
            self.assertFalse(boundary[name], name)
        self.assertTrue(boundary["installed_v0_geometry_preserved"])

    def test_enhancement_profile_unmeasured_fields(self):
        profile = report()["enhancement_profile"]
        self.assertEqual(profile["stoi"], "blocked_unmeasured")
        self.assertEqual(profile["content_availability_timing"], "blocked_unmeasured")
        self.assertEqual(profile["alignment"], "fixture_delay_modelled_not_measured")
        self.assertEqual(profile["listening"], "not_run")
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["candidate_result_present"])

    def test_streaming_semantics_has_no_latency_claim(self):
        semantics = report()["streaming_semantics"]
        self.assertEqual(semantics["declared_lag_samples"], reference.DECLARED_LAG_SAMPLES)
        self.assertFalse(semantics["device_timing"])
        self.assertFalse(semantics["latency_claim"])
        self.assertFalse(semantics["candidate_output_present"])

    def test_report_has_no_self_digest(self):
        value = report()
        self.assertNotIn("report_sha256", value)
        self.assertNotIn("artifact_pins", value)

    def test_source_reporting_is_separated(self):
        context = report()["source_reported_context"]
        self.assertEqual(context["measured_package_stream_lag_samples"], 640)
        self.assertEqual(context["scheduled_cpp_reported_content_delay_samples"], 800)
        self.assertIn("not reproduced", context["disclaimer"])
        self.assertFalse(context["local_vctk_screen"]["reproduced_here"])


class TestRegeneration(unittest.TestCase):
    def test_report_sha256_sidecar_and_contract_pins(self):
        value = report()
        payload = reference.canonical_report_bytes(value)
        digest = hashlib.sha256(payload).hexdigest()
        sidecar = (HERE / "report.json.sha256").read_text(encoding="ascii")
        self.assertEqual(sidecar, f"{digest}  report.json\n")
        self.assertEqual((HERE / "report.json").read_bytes(), payload)

        pins = cli.contract_pins()
        self.assertNotIn("contract.json", pins)
        self.assertIn("README.md", pins)
        contract = load_strict("contract.json")
        self.assertEqual(contract["artifact_pins"], pins)
        for name, pinned in pins.items():
            self.assertEqual(reference.sha256_file(HERE / name), pinned)

    def test_manifest_pins_and_no_board_hash(self):
        lines = (HERE / "SOURCES.sha256").read_text(encoding="utf-8").splitlines()
        self.assertTrue(lines[0].startswith("#"))
        entries = [line for line in lines[1:] if line]
        paths = [line.split("  ", 1)[1] for line in entries]
        self.assertEqual(len(paths), len(set(paths)))
        self.assertNotIn("plan/swarm/TASKS.json", "\n".join(paths))
        for line in entries:
            digest, path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            if path.startswith("source:"):
                self.assertEqual(reference.sha256_file(reference.SOURCE_ROOT / path[len("source:"):]), digest)
            elif path.startswith("worktree:"):
                self.assertEqual(reference.sha256_file(reference.SDK_ROOT / path[len("worktree:"):]), digest)

    def test_readme_digest_table_matches(self):
        text = (HERE / "README.md").read_text(encoding="utf-8")
        block = text.split("<!-- DIGEST_TABLE_START -->", 1)[1].split("<!-- DIGEST_TABLE_END -->", 1)[0]
        for name in cli.TABLE_FILES:
            payload = (HERE / name).read_bytes()
            row = f"| `{name}` | `{hashlib.sha256(payload).hexdigest()}` | {len(payload)} |"
            self.assertIn(row, block)

    def test_three_cold_start_regenerations_byte_identical(self):
        with tempfile.TemporaryDirectory() as tmp:
            copy = Path(tmp) / "evidence"
            shutil.copytree(
                HERE,
                copy,
                ignore=shutil.ignore_patterns("__pycache__", "*.pyc"),
            )
            baseline = {
                name: (HERE / name).read_bytes()
                for name in reference.LOCAL_FILES
                if (HERE / name).is_file()
            }
            baseline["SOURCES.sha256"] = (HERE / "SOURCES.sha256").read_bytes()
            env = dict(os.environ)
            env["PYTHONDONTWRITEBYTECODE"] = "1"
            env["SDK_ROOT"] = str(reference.SDK_ROOT)
            env["SOURCE_ROOT"] = str(reference.SOURCE_ROOT)
            snapshots = []
            for _ in range(3):
                result = subprocess.run(
                    [sys.executable, str(copy / "run.py"), "--all"],
                    cwd=str(copy),
                    env=env,
                    capture_output=True,
                    text=True,
                    check=False,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                snapshot = {}
                for name in sorted(baseline):
                    snapshot[name] = (copy / name).read_bytes()
                snapshots.append(snapshot)
            self.assertEqual(snapshots[0], snapshots[1])
            self.assertEqual(snapshots[1], snapshots[2])
            self.assertEqual(snapshots[0], baseline)


class TestLicensingAndScope(unittest.TestCase):
    def test_python_spdx_headers(self):
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            head = (HERE / name).read_text(encoding="utf-8").splitlines()[:2]
            self.assertEqual(head, ["# " + SPDX_C, "# " + SPDX_L], name)

    def test_markdown_spdx_header(self):
        head = (HERE / "README.md").read_text(encoding="utf-8").splitlines()[:2]
        self.assertEqual(head, ["<!-- " + SPDX_C + " -->", "<!-- " + SPDX_L + " -->"])

    def test_sidecars(self):
        for name in SIDECAR_FILES:
            self.assertEqual((HERE / name).read_text(encoding="utf-8"), SIDECAR, name)

    def test_fail_closed_local_set(self):
        present = {
            path.relative_to(HERE).as_posix()
            for path in HERE.rglob("*")
            if path.is_file() and "__pycache__" not in path.parts
        }
        expected = set(reference.LOCAL_FILES) | {"SOURCES.sha256"}
        self.assertEqual(present, expected)

    def test_no_network_or_download_imports(self):
        forbidden = ("import " + "requests", "import " + "urllib", "import " + "socket",
                     "import " + "http.client", "url" + "open", "url" + "retrieve",
                     "pip " + "install")
        for name in ("reference.py", "run.py", "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            for token in forbidden:
                self.assertNotIn(token, text, f"{name}: {token}")

    def test_no_asset_path_access_in_reference(self):
        text = (HERE / "reference.py").read_text(encoding="utf-8")
        self.assertIn("(SDK_ROOT / ASSET_PATH).is_file()", text)
        self.assertNotIn("ASSET_PATH).read", text)
        self.assertNotIn("open(ASSET_PATH", text)


if __name__ == "__main__":
    unittest.main(verbosity=2)
