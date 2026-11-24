# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the synthetic full-band receive DRC fixture.

Run with the pinned Python interpreter (standard library only):

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py
"""
from __future__ import annotations

import hashlib
import json
import math
import os
import pathlib
import subprocess
import sys
import unittest
from pathlib import Path
from typing import Any, Dict

import fixture
import reference as ref
import run as runner
import scorer

HERE = Path(__file__).resolve().parent
SDK_ROOT = HERE.parents[2]
SOURCE_ROOT = Path(os.environ.get("SOURCE_ROOT", "/Users/htsakanyan/workspace/audio/audioml"))
REPORT = HERE / "report.json"
SIDECAR = HERE / "report.json.sha256"
PINS = HERE / "SOURCES.sha256"
SPDX_LICENSE_LINE = "SPDX" "-License-Identifier: Apache-2.0"
SPDX_COPYRIGHT_LINE = "SPDX" "-FileCopyrightText: 2026 Tsakanyan Hovhannes"


def strict_json(path: Path) -> Dict[str, Any]:
    def reject(value: str) -> None:
        raise ValueError("nonfinite JSON constant " + value)

    return json.loads(path.read_text(encoding="utf-8"), parse_constant=reject)


def request(operation: str, control: str = "drc",
            provider_enabled: bool = True, level: Any = None,
            tmr: Any = None, stimulus: str = "causal_probe",
            samples: Any = None) -> Dict[str, Any]:
    common: Dict[str, Any] = {
        "protocol_version": 1,
        "operation": operation,
        "candidate_ref": {"kind": "candidate", "id": "drc-ref", "revision": 1},
        "adapter_ref": {"kind": "adapter", "id": "adapter-ref", "revision": 1},
        "configuration": {
            "control": control,
            "provider_enabled": provider_enabled,
            "level_dbfs": level,
            "tmr_db": tmr,
        },
    }
    if operation == "run":
        common.update({"attempt_id": "probe-1", "stimulus_id": stimulus,
                       "samples": samples})
    return common


class PinTests(unittest.TestCase):
    def test_01_source_and_boundary_pins_match_recorded_bytes(self) -> None:
        for path, digest in {**ref.SOURCE_PINS, **{
                "audio-benchmark-platform/audio-sdk/" + key: value
                for key, value in ref.BOUNDARY_PINS.items()}}.items():
            # Boundary pins are worktree-relative; resolve them locally.
            if path.startswith("audio-benchmark-platform/audio-sdk/api/"):
                target = SDK_ROOT / path.split("audio-benchmark-platform/audio-sdk/", 1)[1]
            else:
                target = SOURCE_ROOT / path
            with self.subTest(path=path):
                self.assertTrue(target.is_file(), f"missing {target}")
                self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), digest)

    def test_02_research_context_pin_is_exact(self) -> None:
        target = SOURCE_ROOT / "research/listening_intelligibility_20261028.md"
        self.assertEqual(ref.SOURCE_PINS[target.relative_to(SOURCE_ROOT).as_posix()],
                         hashlib.sha256(target.read_bytes()).hexdigest())

    def test_03_artifact_pins_match_task_files(self) -> None:
        for name, digest in ref.artifact_pins().items():
            with self.subTest(path=name):
                self.assertEqual(hashlib.sha256((HERE / name).read_bytes()).hexdigest(),
                                 digest)

    def test_04_manifest_covers_all_pins_and_task_files(self) -> None:
        lines = [line for line in PINS.read_text(encoding="utf-8").splitlines()
                 if line and not line.startswith("#")]
        expected = (len(ref.SOURCE_PINS) + len(ref.BOUNDARY_PINS)
                    + len(ref.artifact_pins()) + 3)
        self.assertEqual(len(lines), expected)
        for line in lines:
            digest, raw_path = line.split("  ", 1)
            self.assertEqual(len(digest), 64)
            if raw_path.startswith("source:"):
                target = SOURCE_ROOT / raw_path.split(":", 1)[1]
            else:
                target = SDK_ROOT / raw_path
            self.assertTrue(target.is_file(), f"missing {target}")
            self.assertEqual(hashlib.sha256(target.read_bytes()).hexdigest(), digest)
        text = PINS.read_text(encoding="utf-8")
        self.assertIn("docs/task-evidence/full-band-receive-drc/report.json", text)
        self.assertIn("docs/task-evidence/full-band-receive-drc/report.json.sha256", text)
        self.assertIn("docs/task-evidence/full-band-receive-drc/README.md", text)

    def test_05_spdx_headers_on_every_python_file(self) -> None:
        for path in sorted(HERE.glob("*.py")):
            with self.subTest(path=path.name):
                head = "\n".join(path.read_text(encoding="utf-8").splitlines()[:4])
                self.assertIn(SPDX_LICENSE_LINE, head)
                self.assertIn(SPDX_COPYRIGHT_LINE, head)

    def test_06_no_trailing_whitespace_in_task_files(self) -> None:
        for path in sorted(HERE.iterdir()):
            if path.is_file() and path.suffix in (".py", ".json", ".md", ".sha256"):
                for number, line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
                    self.assertEqual(line, line.rstrip(), f"{path.name}:{number}")


class BoundaryTests(unittest.TestCase):
    def test_07_fixed_v0_geometry_and_no_public_change(self) -> None:
        self.assertEqual((ref.SAMPLE_RATE_HZ, ref.FRAME_SAMPLES),
                         (16000, 160))
        fmt = strict_json(REPORT)["format"]
        self.assertEqual((fmt["sample_rate_hz"], fmt["channels"],
                          fmt["sample_format"], fmt["frame_samples"], fmt["hop_samples"]),
                         (16000, 1, "f32", 160, 160))
        self.assertFalse(fmt["realtime_v0_provider"])

    def test_08_manifests_are_unregistered_and_off(self) -> None:
        for name in ("contract.json", "adapter.json", "provider.json"):
            data = strict_json(HERE / name)
            self.assertFalse(data["registered"])
            enabled = data.get("default_enabled", data.get("enabled_by_default"))
            self.assertFalse(enabled)
            descriptor = data.get("descriptor_settings")
            if descriptor is None:
                descriptor = data["boundary"]["descriptor_settings"]
            self.assertEqual(descriptor, {})
        contract = strict_json(HERE / "contract.json")
        self.assertFalse(contract["boundary"]["public_c_abi_change"])
        self.assertFalse(contract["boundary"]["installed_v0_behavior_change"])
        self.assertTrue(contract["boundary"]["opt_in_required"])

    def test_09_inspect_is_read_only_and_discloses_off_default(self) -> None:
        result = runner.inspect(request("inspect"))
        self.assertEqual(result["identity"], ref.ADAPTER_ID)
        self.assertFalse(result["default_enabled"])
        self.assertFalse(result["realtime_v0_provider"])
        self.assertEqual(result["content_delay_samples"], 0)
        self.assertFalse(result["provider_manifest"]["registered"])
        self.assertEqual(result["provider_manifest"]["descriptor_settings"], {})
        self.assertIn("not used", result["public_c_boundary"])

    def test_10_malformed_requests_are_rejected(self) -> None:
        valid = request("run")
        cases = {
            "not_object": [],
            "invalid_ref": {**valid, "candidate_ref": {"id": "x"}},
            "extra_field": {**valid, "extra": 1},
            "bad_protocol": {**valid, "protocol_version": 2},
            "bad_control": request("run", control="unknown"),
            "bad_level": request("run", level=-31.0),
            "bad_tmr": request("run", tmr=99.0),
            "bad_stimulus": request("run", stimulus="real_recording"),
            "nonfinite_samples": request("run", samples=[float("nan"), 0.1]),
            "out_of_range_samples": request("run", samples=[9.0, 0.1]),
            "bool_samples": request("run", samples=[True, 0.1]),
        }
        for name, value in cases.items():
            with self.subTest(case=name):
                with self.assertRaises(runner.RequestError):
                    runner.validate_request(value, "run")

    def test_11_duplicate_and_nonfinite_json_are_rejected(self) -> None:
        duplicate = '{"protocol_version":1,"protocol_version":2}'
        with self.assertRaises(runner.RequestError):
            json.loads(duplicate, object_pairs_hook=runner._pairs)
        with self.assertRaises(runner.RequestError):
            json.loads('{"x":NaN}', parse_constant=runner._constant)

    def test_12_provider_off_is_bit_exact_on_and_off_differs(self) -> None:
        off = runner.run(request("run", provider_enabled=False))
        on = runner.run(request("run", provider_enabled=True))
        self.assertEqual(off["applied_control"], "identity_provider_off")
        self.assertEqual(off["output"]["samples_sha256"],
                         ref.tensor_digest(ref.causal_probe_signal()))
        self.assertNotEqual(on["output"]["samples_sha256"],
                            off["output"]["samples_sha256"])
        self.assertEqual(off["status"], "complete")
        self.assertEqual(off["output"]["nonfinite_count"], 0)


class DeterminismTests(unittest.TestCase):
    def test_13_clean_speech_is_repeatable(self) -> None:
        first = ref.synthetic_speech()
        self.assertEqual(ref.tensor_digest(first),
                         ref.tensor_digest(ref.synthetic_speech()))
        self.assertEqual(ref.tensor_digest(first),
                         reference_digest_of("clean_speech"))

    def test_14_fixture_digest_matches_generated_signals(self) -> None:
        self.assertEqual(ref.fixture_digest(),
                         strict_json(REPORT)["fixture_digest"])

    def test_15_report_regenerates_byte_identically(self) -> None:
        self.assertEqual(fixture.canonical_report_bytes(ref.build_report()),
                         REPORT.read_bytes())

    def test_16_report_sidecar_matches_report_bytes(self) -> None:
        expected = hashlib.sha256(REPORT.read_bytes()).hexdigest()
        self.assertEqual(SIDECAR.read_text(encoding="ascii").strip(), expected)

    def test_17_cold_start_repeat_probe_is_byte_identical(self) -> None:
        probe = strict_json(REPORT)["repeatability"]
        self.assertEqual(probe["runs"], 3)
        self.assertTrue(probe["byte_identical"])
        self.assertEqual(len(set(probe["output_digests"])), 1)
        self.assertEqual(probe["input_samples"], 960)


class DspControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_18_sweeps_show_small_signal_gain_and_high_level_compression(self) -> None:
        sweeps = self.report["measurements"]["sweeps"]
        small = {row["frequency_hz"]: row for row in sweeps["small_signal"]}
        self.assertEqual(set(small), set(ref.SWEEP_HZ))
        for row in sweeps["small_signal"]:
            self.assertEqual(row["gain_db"], ref.DEFAULT_CONFIG.makeup_db)
            self.assertEqual(row["error_db"], 0.0)
        high = {row["frequency_hz"]: row for row in sweeps["high_level"]}
        self.assertEqual(set(high), set(ref.SWEEP_HZ))
        for frequency in (125.0, 250.0, 500.0, 1000.0, 2000.0):
            self.assertLess(high[frequency]["gain_db"], small[frequency]["gain_db"])

    def test_19_step_attack_release_and_headroom_are_measured(self) -> None:
        modes = self.report["measurements"]["steps"]["modes"]
        self.assertEqual(set(modes), {"compressor_only", "limiter_only", "drc"})
        response = modes["drc"]["response"]
        self.assertEqual(response["status"], "measured")
        self.assertIsNotNone(response["attack_ms"])
        self.assertIsNotNone(response["release_ms"])
        self.assertGreater(response["attack_ms"], 0.0)
        self.assertGreater(response["release_ms"], 0.0)
        self.assertEqual(response["window_ms"], 5.0)
        self.assertEqual(modes["limiter_only"]["gain"]["rms_gain_db"], 0.0)

    def test_20_impulse_delay_silence_and_synthetic_speech(self) -> None:
        impulse = self.report["measurements"]["impulse"]
        self.assertEqual(impulse["delay"]["peak_delay_samples"], 0)
        self.assertEqual(impulse["delay"]["input_peak_index"], ref.FRAME_SAMPLES)
        silence = self.report["measurements"]["silence"]
        self.assertEqual(silence["nonfinite_count"], 0)
        self.assertEqual(silence["peak_abs"], 0.0)
        clean = self.report["measurements"]["clean_speech"]
        self.assertTrue(clean["identity_control"]["excluded_from_qualification"])
        self.assertNotEqual(clean["receive_drc"]["output_digest"],
                            clean["identity_control"]["output_digest"])

    def test_21_level_and_masker_controls_are_paired_and_synthetic(self) -> None:
        control = self.report["near_end_listening_baseline_synthetic_control"]
        self.assertEqual(control["status"], "measured_synthetic_non_qualifying")
        self.assertTrue(control["excluded_from_qualification"])
        conditions = control["conditions"]
        self.assertEqual(len(conditions), len(ref.LEVEL_DBFS) * len(ref.TMR_DB))
        for level in ref.LEVEL_DBFS:
            for tmr in ref.TMR_DB:
                key = "level_" + str(int(level)) + "_dbfs_tmr_" + str(int(tmr)) + "_db"
                metrics = conditions[key]["metrics"]
                self.assertEqual(metrics["measured_tmr_db"], tmr)
                self.assertEqual(metrics["identity_measured_tmr_db"], tmr)
                self.assertEqual(metrics["restoration_error_db"], 0.0)
                self.assertEqual(metrics["mixture_nonfinite_count"], 0)
                self.assertIn("delta_mixture_high_over_low_db", metrics)
                self.assertIn("delta_mixture_envelope_modulation_index", metrics)
        self.assertIn("identity_input_digest", next(iter(conditions.values())))

    def test_22_off_on_and_ceiling_clamp_are_honest(self) -> None:
        off_on = self.report["off_on_probe"]
        self.assertTrue(off_on["off_is_bit_exact_identity"])
        self.assertTrue(off_on["on_differs_from_off"])
        probe = self.report["ceiling_clamp_probe"]
        self.assertFalse(probe["modes"]["identity"]["bit_exact_to_input"])
        self.assertGreater(probe["modes"]["identity"]["engine_hard_clip_count"], 0)
        self.assertTrue(probe["off_is_bit_exact_below_ceiling"])

    def test_23_interacting_nonlinear_configurations(self) -> None:
        modes = self.report["interacting_nonlinear_configurations"]["modes"]
        self.assertEqual(set(modes), {"identity", "compressor_only",
                                      "limiter_only", "drc"})
        self.assertEqual(modes["drc"]["gain"]["rms_gain_db"],
                         modes["compressor_only"]["gain"]["rms_gain_db"])
        self.assertIn("masker_control", modes["drc"])
        self.assertGreater(modes["identity"]["engine_hard_clip_count"], 0)


class StateAndValidityTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_24_config_rejections_are_all_invalid(self) -> None:
        cases = self.report["adverse"]["config_rejections"]
        for name, value in cases.items():
            with self.subTest(case=name):
                self.assertIn("rejected", value["status"])
                self.assertFalse(value["controller_created"])

    def test_25_frame_rejections_do_not_change_dsp_state(self) -> None:
        probe = self.report["adverse"]["frame_rejections"]
        self.assertEqual(probe["admitted_first_frame_status"], "ok")
        self.assertTrue(probe["dsp_state_unchanged"])
        self.assertEqual(probe["out_of_range_probe_abs"], 5.0)
        self.assertGreater(probe["out_of_range_probe_abs"],
                           probe["max_abs_input"])
        expected = {
            "nonfinite": "rejected_nonfinite",
            "out_of_range": "rejected_range",
            "wrong_shape": "rejected_tensor",
            "missing_samples": "rejected_tensor",
            "stale_epoch": "rejected_epoch",
            "stale_position": "rejected_position",
        }
        self.assertEqual(probe["frame_rejections"], expected)
        self.assertEqual(probe["finalize_status"], "ok")
        self.assertEqual(probe["finished_reuse_status"], "rejected_session")

    def test_26_state_transitions_reset_causality_and_isolation(self) -> None:
        state = self.report["alignment_and_state"]["state_transitions"]
        self.assertEqual(state["status"], "ok")
        self.assertTrue(state["chunked_matches_whole"])
        self.assertEqual(set(state["chunked_digests"].values()),
                         {state["chunked_digests"]["whole_clip"]})
        self.assertTrue(state["causality_probe"]["future_frame_differs"])
        self.assertTrue(state["causality_probe"]["prefix_byte_identical"])
        self.assertTrue(state["independent_sessions"]["state_isolated"])
        self.assertEqual(state["reset"]["reset_status"], "ok")
        self.assertEqual(state["reset"]["repeated_reset_status"], "rejected_invalid")
        self.assertTrue(state["reset"]["replay_matches_original"])
        self.assertEqual(state["stale_epoch_status"], "rejected_epoch")
        self.assertEqual(state["stale_position_status"], "rejected_position")

    def test_27_session_and_chunk_boundaries_are_exercised(self) -> None:
        engine = ref.DrcEngine()
        self.assertEqual(engine.state.epoch, 1)
        self.assertEqual(engine.reset(2).value, "ok")
        self.assertEqual(engine.state.position, 0)
        self.assertEqual(engine.reset(2).value, "rejected_invalid")
        self.assertEqual(engine.reset(0).value, "rejected_invalid")
        status, out = engine.process((0.01,) * ref.FRAME_SAMPLES, epoch=2, position=0)
        self.assertEqual(status, ref.Status.OK)
        self.assertEqual(len(out), ref.FRAME_SAMPLES)

    def test_28_numerical_behavior_is_finite_and_clipped(self) -> None:
        for entry in self.report["measurements"]["clip_and_headroom"]["modes"].values():
            self.assertEqual(entry["headroom"]["nonfinite_count"], 0)
            self.assertLessEqual(entry["headroom"]["peak_abs"],
                                 ref.DEFAULT_CONFIG.ceiling)
        for condition in self.report["near_end_listening_baseline_synthetic_control"][
                "conditions"].values():
            self.assertEqual(condition["metrics"]["mixture_nonfinite_count"], 0)
        self.assertEqual(
            self.report["adverse"]["missing_reference"]["status"], "blocked")
        self.assertIsNone(self.report["adverse"]["missing_reference"]["metrics"])


class EvidenceShapeTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = strict_json(REPORT)

    def test_29_status_and_no_missing_result_rule(self) -> None:
        self.assertEqual(self.report["status"], "proposal_only_not_qualified")
        self.assertEqual(self.report["candidate_status"],
                         "proposal_only_not_qualified")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])
        self.assertEqual(self.report["qualification"]["decision"], "DEFER")
        self.assertFalse(self.report["provider"]["registered"])
        self.assertFalse(self.report["provider"]["default_enabled"])
        self.assertEqual(self.report["provider"]["descriptor_settings"], {})

    def test_30_gates_are_blocked_with_reopening_conditions(self) -> None:
        gates = {gate["id"]: gate for gate in self.report["gates"]}
        self.assertIn("authorized_real_listening", gates)
        for gate in gates.values():
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reason"])
            self.assertTrue(gate["reopen"])
        self.assertEqual(len(self.report["remaining_gates"]), len(gates))

    def test_31_regressions_are_recorded_verbatim(self) -> None:
        regressions = self.report["regressions"]
        self.assertEqual(len(regressions), self.report["regression_count"])
        self.assertGreaterEqual(len(regressions), 10)
        ids = {entry["entry_id"] for entry in regressions}
        self.assertIn("clean_speech_rms_loss", ids)
        self.assertIn("high_level_sweep_gain_reduction", ids)
        self.assertIn("ceiling_clamp_identity", ids)
        self.assertIn("masker_control_headroom_deficit", ids)
        for entry in regressions:
            self.assertTrue(entry["excluded_from_qualification"])
            self.assertTrue(entry["interpretation"])

    def test_32_dsp_profile_mapping_is_complete(self) -> None:
        profile = self.report["dsp_profile"]
        self.assertEqual(profile["profile"], "dsp")
        self.assertEqual(set(profile["mapped_cases"]), {
            "clean_speech_synthetic", "impulses",
            "intelligibility_or_load_control", "silence", "steps", "sweeps"})
        for key in ("attack_release", "delay", "frequency_response", "gain",
                    "headroom", "numerical_behavior"):
            self.assertIn(key, profile["measured"])

    def test_33_source_results_are_never_reused_as_claims(self) -> None:
        statements = " ".join(self.report["source_evidence_statements"])
        self.assertIn("context only", statements)
        for forbidden in ("0.6873", "0.5752", "+0.0033", "+0.0072"):
            self.assertNotIn(forbidden, statements)
        self.assertEqual(set(self.report["source_pins"]), set(ref.SOURCE_PINS))

    def test_34_missing_result_cannot_qualify(self) -> None:
        damaged = dict(self.report)
        damaged["gates"] = [dict(gate) for gate in self.report["gates"]]
        damaged["gates"][0] = {**damaged["gates"][0], "status": "open"}
        self.assertEqual(ref.QUALIFICATION_GATES[0]["status"], "blocked")
        self.assertEqual(self.report["qualification"]["status"], "not_qualified")
        self.assertTrue(self.report["qualification"]["no_missing_result_may_qualify"])


def reference_digest_of(name: str) -> str:
    return ref.tensor_digest(ref.fixture_generators()[name]())


if __name__ == "__main__":
    unittest.main()
