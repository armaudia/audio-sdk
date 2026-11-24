# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic checks for the task-local Speex AGC + activity evidence."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

TASK = Path(__file__).resolve().parent
sys.path.insert(0, str(TASK / "tools"))
import common as c  # noqa: E402
import fixtures as f  # noqa: E402
import run as adapter  # noqa: E402

REPORT = c.REPORT_PATH


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_keys_rejected(self):
        with self.assertRaises(c.StrictError):
            c.strict_json('{"a":1,"a":2}')

    def test_nonfinite_constants_rejected(self):
        for token in ("NaN", "Infinity", "-Infinity"):
            with self.assertRaises(c.StrictError):
                c.strict_json('{"a":' + token + '}')

    def test_canonical_bytes_are_ascii_and_sorted(self):
        raw = c.canonical_bytes({"b": 2, "a": 1})
        self.assertEqual(raw, b'{"a":1,"b":2}\n')


class StimulusTests(unittest.TestCase):
    def test_generators_are_deterministic(self):
        one = f.all_stimuli()
        two = f.all_stimuli()
        self.assertEqual(set(one), set(two))
        for name in one:
            self.assertEqual(hashlib.sha256(f.f32_bytes(one[name])).hexdigest(),
                             hashlib.sha256(f.f32_bytes(two[name])).hexdigest())

    def test_stimulus_geometry(self):
        for name, values in f.all_stimuli().items():
            self.assertEqual(len(values), f.SAMPLES)
            self.assertEqual(len(values) % f.FRAME, 0)

    def test_nonfinite_stimulus_carries_expected_values(self):
        values = f.nonfinite()
        self.assertTrue(any(value != value for value in values))
        self.assertTrue(any(value == float("inf") for value in values))


class FrozenReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = c.read_strict(REPORT)
        cls.raw = REPORT.read_bytes()
        cls.digest = hashlib.sha256(cls.raw).hexdigest()

    def test_01_schema_and_canonical_bytes(self):
        adapter.validate_report(self.report)
        self.assertEqual(c.canonical_bytes(self.report), self.raw)
        self.assertEqual(self.digest,
                         "951a004027740a93080204d02215844376ad2f74a6ce6ca2872855a19b255b91")

    def test_02_scope_boundaries(self):
        scope = self.report["scope"]
        self.assertEqual(scope["write_scope"], ["docs/task-evidence/speex-agc-and-activity-output/"])
        for key in ("public_api_changed", "abi_changed", "default_provider_changed",
                    "provider_registry_changed", "installed_speex_v0_behavior_changed",
                    "real_audio_used", "public_benchmark_claim", "tiny16_comparison_claim",
                    "activity_gates_audio"):
            self.assertIs(scope[key], False, key)
        self.assertIs(scope["activity_advisory_only"], True)

    def test_03_source_pins_match_checked_out_files(self):
        for pin in self.report["adapter"]["source_pins"]:
            root = c.SDK_ROOT if pin["scope"] == "sdk" else c.WS_ROOT
            path = root / pin["path"]
            self.assertTrue(path.is_file(), str(path))
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), pin["sha256"])
            self.assertEqual(pin["status"], "match")

    def test_04_case_repeats_are_byte_identical(self):
        cases = {item["id"]: item for item in self.report["cases"]}
        self.assertEqual(len(cases), 23)
        for item in cases.values():
            reps = item["repeats"]
            self.assertEqual(reps["count"], 3)
            self.assertEqual(len(set(reps["output_sha256"])), 1)
            self.assertEqual(len(set(reps["meta_sha256"])), 1)
            self.assertEqual(item["output"]["sha256"], reps["output_sha256"][0])
            self.assertEqual(item["output"]["meta_sha256"], reps["meta_sha256"][0])

    def test_05_stimulus_digests_match_frozen_generators(self):
        generated = f.all_stimuli()
        for name, info in self.report["stimuli"].items():
            raw = f.f32_bytes(generated[name])
            self.assertEqual(info["input_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertEqual(info["byte_count"], len(raw))

    def test_06_advisory_activity_is_present_and_varies(self):
        cases = {item["id"]: item for item in self.report["cases"]}
        combined = cases["combined_speech_like"]["output"]["activity"]
        agc_only = cases["agc_only_speech_like"]["output"]["activity"]
        vad_only = cases["vad_only_speech_like"]["output"]["activity"]
        identity = cases["identity_speech_like"]["output"]["activity"]
        # With VAD disabled the run() return is unconditionally active. With
        # VAD enabled it follows the speech probability and marks 7 gaps.
        self.assertEqual(sum(identity["advisory_vad_sequence"]), 100)
        self.assertEqual(sum(agc_only["advisory_vad_sequence"]), 100)
        self.assertEqual(vad_only["advisory_vad_sequence"], combined["advisory_vad_sequence"])
        self.assertLess(sum(combined["advisory_vad_sequence"]), 100)
        # Enabling VAD changes only advisory metadata: the AGC gain trajectory
        # is byte-for-byte the same as AGC-only.
        self.assertEqual(combined["agc_gain_db_sequence"], agc_only["agc_gain_db_sequence"])
        self.assertEqual(set(vad_only["agc_gain_db_sequence"]), {0})
        self.assertEqual(len(combined["agc_gain_db_sequence"]), 100)

    def test_07_dsp_profile_coverage(self):
        coverage = self.report["acceptance_profile_coverage"]
        for key in ("sweeps", "steps", "impulses", "silence", "clean_speech_control",
                    "intelligibility_or_load_control", "gain", "response", "attack_release",
                    "headroom", "delay", "numerical_behavior", "state_transitions",
                    "interacting_nonlinear_configurations"):
            self.assertTrue(coverage[key], key)

    def test_08_controls(self):
        controls = self.report["controls"]
        self.assertEqual(controls["fail_closed_nonfinite"]["status"], "pass")
        self.assertEqual(controls["fail_closed_nonfinite"]["observed_exit"], 3)
        self.assertEqual(controls["identity_delay_samples"],
                         controls["combined_delay_samples"])
        self.assertEqual(controls["input_impulse_index"], 400)

    def test_09_verification_is_read_only(self):
        verification = self.report["verification"]
        self.assertIs(verification["read_only"], True)
        self.assertEqual(verification["check_exit"], 0)
        self.assertEqual(verification["sha256"],
                         "3f2631333e4436a6441236a2b21f4d5b45fb3bb3619f600767e22eb957f77910")

    def test_10_remaining_gates(self):
        gates = self.report["remaining_release_gates"]
        self.assertTrue(any("Reviewer" in gate for gate in gates))
        self.assertTrue(any("Tiny16" in gate for gate in gates))
        self.assertTrue(any("paced" in gate.lower() or "pacing" in gate.lower() for gate in gates))

    def test_11_report_regenerates_byte_identically(self):
        proc = subprocess.run([sys.executable, str(TASK / "run.py"), "--report"],
                              capture_output=True, text=True, check=False)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIn("byte_identical=true", proc.stdout)
        self.assertEqual(hashlib.sha256(REPORT.read_bytes()).hexdigest(), self.digest)


class AdapterBoundaryTests(unittest.TestCase):
    def refs(self):
        return {
            "candidate_ref": {"kind": "source", "id": "speex-vendored", "revision": 1},
            "adapter_ref": {"kind": "task-local", "id": "speex-agc-activity-reference-v1", "revision": 1},
        }

    def test_inspect_envelope(self):
        request = {"protocol_version": 1, "operation": "inspect", **self.refs(),
                   "configuration": {"control": "combined"}}
        result = adapter.inspect(request)
        self.assertEqual(result["identity"], "speex-agc-activity-reference-v1")
        self.assertEqual(result["supported_controls"], list(c.CONTROLS))
        self.assertIs(result["activity_is_advisory"], True)
        self.assertEqual(result["supported_tasks"], [])

    def test_run_envelope_is_deterministic(self):
        request = {"protocol_version": 1, "operation": "run", **self.refs(),
                   "configuration": {"control": "combined"},
                   "attempt_id": "unit", "stimulus_id": "silence",
                   "reset_frames": [], "stimulus_samples": None}
        one = adapter.run(request)
        two = adapter.run(request)
        self.assertEqual(one["output"]["samples_sha256"], two["output"]["samples_sha256"])
        self.assertEqual(one["output"]["sample_count"], c.SAMPLES)
        self.assertEqual(len(one["output"]["advisory_activity"]), 100)

    def test_bad_requests_rejected(self):
        base = {"protocol_version": 1, "operation": "inspect", **self.refs(),
                "configuration": {"control": "combined"}}
        with self.assertRaises(adapter.RequestError):
            adapter.inspect({**base, "configuration": {"control": "unknown"}})
        with self.assertRaises(adapter.RequestError):
            adapter.inspect({**base, "protocol_version": 2})
        with self.assertRaises(adapter.RequestError):
            adapter.inspect({**base, "configuration": {"control": "combined", "extra": 1}})

    def test_opt_in_default_is_off_and_single_preprocessor(self):
        cmake = (TASK / "adapter/CMakeLists.txt").read_text(encoding="utf-8")
        self.assertIn("AS_ENABLE_SPEEX_AGC_ACTIVITY_REFERENCE", cmake)
        self.assertIn("OFF)", cmake)
        contract = c.read_strict(TASK / "contract.json")
        self.assertIs(contract["default_enabled"], False)
        self.assertIs(contract["one_preprocessor_per_stream"], True)
        self.assertIs(contract["activity_gates_audio"], False)


if __name__ == "__main__":
    unittest.main(verbosity=2)
