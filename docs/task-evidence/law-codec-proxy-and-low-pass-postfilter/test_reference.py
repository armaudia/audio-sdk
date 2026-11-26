# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Standard-library unittest suite for the law-codec-proxy evidence package."""

from __future__ import annotations

import json
import math
from pathlib import Path
import unittest

import reference

HERE = Path(__file__).resolve().parent
SPDX_NEEDLE = "SPDX-License-" "Identifier: Apache-2.0"
PACKAGE_FILES = (
    "README.md", "contract.json", "reference.py", "report.json",
    "report.json.sha256", "run.py", "SOURCES.sha256",
    "test_reference.py", "verify.py",
)


class QuantizerTests(unittest.TestCase):
    def test_known_4bit_vector(self) -> None:
        values = [0.0, 0.1, -0.1, 0.25, -0.25, 0.5, -0.5]
        expected = [
            0.006767501202737221, 0.08822966514109552,
            -0.08822966514109558, 0.22129109437611108,
            -0.22129109437611108, 0.49999999999999994,
            -0.49999999999999994,
        ]
        actual = reference.mulaw_proxy_quantize(values, 4)
        for observed, wanted in zip(actual, expected):
            self.assertAlmostEqual(observed, wanted, places=12)

    def test_known_8bit_vector(self) -> None:
        values = [0.0, 0.1, -0.1, 0.25, -0.25, 0.5, -0.5]
        expected = [
            4.310579782536036e-05, 0.09845638976089535,
            -0.09845638976089535, 0.24833831323329494,
            -0.24833831323329494, 0.4999999999999999,
            -0.4999999999999999,
        ]
        actual = reference.mulaw_proxy_quantize(values, 8)
        for observed, wanted in zip(actual, expected):
            self.assertAlmostEqual(observed, wanted, places=12)

    def test_output_is_peak_bounded(self) -> None:
        values = [0.0, 0.3, -0.7, 0.25]
        for bits in (4, 8):
            actual = reference.mulaw_proxy_quantize(values, bits)
            self.assertLessEqual(max(abs(value) for value in actual),
                                 max(abs(value) for value in values) + 1e-12)

    def test_invalid_bits_rejected(self) -> None:
        for bits in (3, 9, 4.5, True, "4"):
            with self.assertRaises(reference.Rejected):
                reference.mulaw_proxy_quantize([0.1], bits)

    def test_nonfinite_and_empty_rejected(self) -> None:
        for values in ([], [float("nan")], [float("inf")], ["0.1"]):
            with self.assertRaises(reference.Rejected):
                reference.mulaw_proxy_quantize(values, 8)

    def test_zero_and_subfloor_peak_rejected(self) -> None:
        for values in ([0.0, 0.0], [1e-12, -1e-12]):
            with self.assertRaises(reference.Rejected):
                reference.mulaw_proxy_quantize(values, 8)


class ResamplerTests(unittest.TestCase):
    def test_geometry_and_finiteness(self) -> None:
        signal = reference.synthetic_speech_like(1000)
        narrow = reference.resample_poly(signal, 1, 2)
        wide = reference.resample_poly(narrow, 2, 1)
        self.assertEqual(len(narrow), 500)
        self.assertEqual(len(wide), 1000)
        self.assertTrue(all(math.isfinite(value) for value in narrow + wide))

    def test_constant_signal_preserved_in_interior(self) -> None:
        signal = [0.5] * 400
        narrow = reference.resample_poly(signal, 1, 2)
        wide = reference.resample_poly(narrow, 2, 1)
        for value in narrow[50:150]:
            self.assertAlmostEqual(value, 0.5, places=3)
        for value in wide[100:300]:
            self.assertAlmostEqual(value, 0.5, places=3)

    def test_unadmitted_ratio_rejected(self) -> None:
        for up, down in ((1, 1), (1, 3), (3, 1), (0, 1), (1, 0), (2, 2)):
            with self.assertRaises(reference.Rejected):
                reference.resample_poly([0.1] * 32, up, down)

    def test_declared_tap_geometry_matches_implementation(self) -> None:
        self.assertEqual(reference.RESAMPLE_ADMITTED_RATIOS,
                         ((1, 2), (2, 1)))
        self.assertEqual(reference.RESAMPLE_TAPS,
                         2 * 10 * max(2, 2) + 1)
        self.assertEqual(reference.RESAMPLE_TAPS, 41)
        self.assertEqual(reference.RESAMPLE_COMPOSITE_TAPS, 81)
        self.assertEqual(reference.RESAMPLE_COMPOSITE_TAPS,
                         2 * reference.RESAMPLE_TAPS - 1)
        geometry = reference.geometry()["resampler"]
        self.assertEqual(geometry["admitted_ratios"], [[1, 2], [2, 1]])
        self.assertEqual(geometry["taps_per_direction"],
                         reference.RESAMPLE_TAPS)
        self.assertEqual(geometry["taps_formula"],
                         "2 * 10 * max(up, down) + 1")
        self.assertEqual(geometry["composite_cascade_taps"],
                         reference.RESAMPLE_COMPOSITE_TAPS)
        self.assertNotIn("up", geometry)
        self.assertNotIn("down", geometry)
        self.assertNotIn("taps", geometry)
        for up, down in reference.RESAMPLE_ADMITTED_RATIOS:
            taps = reference.resampler_tap_count(up, down)
            self.assertEqual(taps, geometry["taps_per_direction"])
            coefficients = reference._firwin_lowpass(
                taps, 1.0 / max(up, down), reference.RESAMPLE_KAISER_BETA)
            self.assertEqual(len(coefficients), taps)
        with self.assertRaises(reference.Rejected):
            reference.resampler_tap_count(2, 2)


class PostfilterTests(unittest.TestCase):
    def test_constant_preserved(self) -> None:
        signal = [0.25] * 200
        filtered = reference.lowpass_postfilter(signal)
        for value in filtered:
            self.assertAlmostEqual(value, 0.25, places=12)

    def test_impulse_is_finite_and_bounded(self) -> None:
        signal = [0.0] * 200
        signal[100] = 1.0
        filtered = reference.lowpass_postfilter(signal)
        self.assertTrue(all(math.isfinite(value) for value in filtered))
        self.assertLessEqual(max(abs(value) for value in filtered), 0.5)

    def test_cutoff_is_validated(self) -> None:
        for cutoff in (0.0, -1.0, 8000.0, 9000.0):
            with self.assertRaises(reference.Rejected):
                reference.lowpass_postfilter([0.1] * 200, cutoff_hz=cutoff)

    def test_short_signal_rejected(self) -> None:
        with self.assertRaises(reference.Rejected):
            reference.lowpass_postfilter([0.1] * 10)


class MetricTests(unittest.TestCase):
    def test_identity_is_exact(self) -> None:
        value, perfect = reference.si_sdr([0.1, -0.2, 0.3], [0.1, -0.2, 0.3])
        self.assertIsNone(value)
        self.assertTrue(perfect)
        self.assertEqual(reference.rmse([0.1, -0.2], [0.1, -0.2]), 0.0)

    def test_known_si_sdr(self) -> None:
        reference_signal = [1.0, -1.0, 1.0, -1.0]
        estimate = [2.0, 0.0, 0.0, -2.0]
        value, perfect = reference.si_sdr(reference_signal, estimate)
        self.assertFalse(perfect)
        self.assertIsNotNone(value)
        self.assertAlmostEqual(value, 0.0, places=9)

    def test_empty_comparison_rejected(self) -> None:
        with self.assertRaises(reference.Rejected):
            reference.si_sdr([], [])
        with self.assertRaises(reference.Rejected):
            reference.rmse([], [])


class OfflineFixtureTests(unittest.TestCase):
    def test_all_conditions_are_finite_and_bounded(self) -> None:
        fixture = reference.evaluate_offline()
        self.assertTrue(fixture["all_finite"])
        self.assertTrue(fixture["peak_bounded"])
        self.assertFalse(fixture["pilot_numeric_parity"])
        self.assertEqual(fixture["results_role"],
                         "synthetic_fixture_control_not_qualifying")

    def test_postfilter_helps_4bit_and_harms_8bit(self) -> None:
        conditions = reference.evaluate_offline()["conditions"]
        self.assertGreater(conditions["4bit"]["delta_si_sdr_db"], 0.0)
        self.assertLess(conditions["8bit"]["delta_si_sdr_db"], 0.0)

    def test_stoi_is_not_fabricated(self) -> None:
        conditions = reference.evaluate_offline()["conditions"]
        for condition in conditions.values():
            for method in ("decoded_input", "lowpass_postfilter"):
                self.assertIsNone(condition[method]["stoi"])
                self.assertEqual(condition[method]["stoi_status"],
                                 "not_computed_runtime_absent")

    def test_identity_control_is_not_filter_identity(self) -> None:
        control = reference.evaluate_offline()["identity_control"]
        self.assertTrue(control["decoded_bit_exact"])
        self.assertFalse(control["filtered_bit_exact"])
        self.assertGreater(control["postfilter_max_abs_change"], 0.0)


class FrameTests(unittest.TestCase):
    def setUp(self) -> None:
        values = reference.synthetic_speech_like(480)
        self.frame = values[80:240]
        self.config = {
            "sample_rate_hz": 16000,
            "channels": 1,
            "frame_samples": 160,
            "bits": 8,
            "postfilter": False,
            "mode": "proxy_frame_quantize",
        }

    def test_valid_frame_accepted(self) -> None:
        result = reference.process_frame(self.frame, self.config)
        self.assertEqual(result["status"], "accepted")
        self.assertEqual(len(result["samples"]), 160)
        self.assertTrue(all(math.isfinite(value)
                            for value in result["samples"]))

    def test_postfilter_rejected_on_frame_path(self) -> None:
        config = dict(self.config)
        config["postfilter"] = True
        with self.assertRaises(reference.Rejected) as context:
            reference.process_frame(self.frame, config)
        self.assertEqual(context.exception.reason,
                         "FRAME_POSTFILTER_UNSUPPORTED")

    def test_adverse_cases_all_rejected(self) -> None:
        adverse = reference._frame_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)
        self.assertGreaterEqual(adverse["case_count"], 20)

    def test_json_cases_all_rejected(self) -> None:
        adverse = reference._json_cases()
        self.assertTrue(adverse["all_rejected"])
        self.assertEqual(adverse["accepted_count"], 0)


class SessionTests(unittest.TestCase):
    def setUp(self) -> None:
        self.frame = reference.synthetic_speech_like(480)[80:240]

    def test_contiguous_frames_and_reset(self) -> None:
        session = reference.ProxySession(bits=8)
        first = session.process(self.frame, 1, 0)
        second = session.process(self.frame, 1, 160)
        self.assertEqual(first["source_first_sample"], 0)
        self.assertEqual(second["source_end_sample"], 320)
        session.reset(2, 1000)
        third = session.process(self.frame, 2, 1000)
        self.assertEqual(third["source_first_sample"], 1000)

    def test_wrong_epoch_and_position_do_not_advance(self) -> None:
        session = reference.ProxySession(bits=8)
        session.process(self.frame, 1, 0)
        with self.assertRaises(reference.Rejected):
            session.process(self.frame, 9, 160)
        with self.assertRaises(reference.Rejected):
            session.process(self.frame, 1, 12345)
        result = session.process(self.frame, 1, 160)
        self.assertEqual(result["source_first_sample"], 160)

    def test_reset_requires_increasing_epoch(self) -> None:
        session = reference.ProxySession(bits=4)
        for epoch in (1, 0):
            with self.assertRaises(reference.Rejected):
                session.reset(epoch, 0)
        with self.assertRaises(reference.Rejected):
            session.reset(2, -1)
        self.assertEqual(session.reset(2, 0)["status"], "reset")

    def test_sessions_are_independent(self) -> None:
        left = reference.ProxySession(bits=4)
        right = reference.ProxySession(bits=8)
        left_output = left.process(self.frame, 1, 0)["samples"]
        right_output = right.process(self.frame, 1, 0)["samples"]
        self.assertNotEqual(left_output, right_output)


class StrictJsonTests(unittest.TestCase):
    def test_duplicate_key_rejected(self) -> None:
        with self.assertRaises(reference.Rejected):
            reference.strict_json_loads('{"a":1,"a":2}')

    def test_nonfinite_constants_rejected(self) -> None:
        for text in ('{"a":NaN}', '{"a":Infinity}',
                     '{"a":-Infinity}'):
            with self.assertRaises(reference.Rejected):
                reference.strict_json_loads(text)

    def test_canonical_bytes_are_sorted(self) -> None:
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": 2}),
                         b'{"a":2,"b":1}')

    def test_finite_json_detects_nan(self) -> None:
        self.assertFalse(reference.finite_json({"a": [float("nan")]}))
        self.assertTrue(reference.finite_json({"a": [1.0]}))


class ProbeTests(unittest.TestCase):
    def test_source_pins_verify(self) -> None:
        probe = reference.source_probe()
        self.assertEqual(probe["status"], "present_pinned")
        self.assertTrue(probe["verified"])

    def test_codec_reference_is_absent(self) -> None:
        probe = reference.codec_reference_probe()
        self.assertEqual(probe["status"], "absent")
        self.assertFalse(probe["licensed_reference_present"])
        self.assertFalse(probe["admitted"])

    def test_runtime_is_unpinned_and_unadmitted(self) -> None:
        probe = reference.runtime_probe()
        self.assertFalse(probe["pinned"])
        self.assertFalse(probe["unpinned_venv"]["admitted"])
        self.assertEqual(probe["admitted_modules"], [])
        self.assertFalse(probe["downloads"])

    def test_corpus_is_absent_and_unread(self) -> None:
        probe = reference.corpus_probe()
        self.assertFalse(probe["present"])
        self.assertFalse(probe["real_audio_read"])

    def test_rights_entry_is_absent(self) -> None:
        probe = reference.rights_probe()
        self.assertFalse(probe["entry_present"])
        self.assertTrue(probe["blocked"])

    def test_board_projection_is_not_the_full_file_hash(self) -> None:
        links, digest = reference.board_link_projection()
        self.assertEqual(links, [reference.EXPECTED_LINK])
        self.assertNotEqual(digest, reference.sha256_file(reference.BOARD_PATH))
        self.assertNotIn("plan/swarm/TASKS.json", reference.SOURCE_PINS)

    def test_inventory_and_evidence_entry(self) -> None:
        self.assertEqual(reference.inventory_link(),
                         reference.EXPECTED_INVENTORY)
        entry = reference.evidence_entry()
        self.assertEqual(entry["line"], 423)
        for token in reference.EVIDENCE_TOKENS:
            self.assertIn(token, entry["text"])


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.payload = reference.report_bytes()

    def test_report_decision_and_status(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertEqual(self.report["qualification"]["readiness"],
                         "incomplete")
        self.assertFalse(self.report["qualification"]["candidate_qualified"])

    def test_eight_blocked_gates(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual([gate["id"] for gate in gates],
                         reference.GATE_IDS)
        self.assertTrue(all(gate["status"] == "blocked" for gate in gates))
        self.assertTrue(all(gate["reason"] and gate["reopen"]
                            for gate in gates))

    def test_required_results_do_not_pass(self) -> None:
        required = self.report["required_results"]
        self.assertTrue(required)
        self.assertFalse(any(value in ("passed", "qualified")
                             for value in required.values()))

    def test_local_checks_all_true(self) -> None:
        checks = self.report["local_harness_checks"]
        self.assertGreaterEqual(len(checks), 20)
        self.assertTrue(all(checks.values()), checks)

    def test_report_bytes_are_canonical(self) -> None:
        self.assertTrue(self.payload.endswith(b"\n"))
        self.assertFalse(self.payload.endswith(b"\n\n"))
        parsed = reference.strict_json_loads(self.payload.decode("utf-8"))
        self.assertEqual(reference.canonical_bytes(parsed) + b"\n",
                         self.payload)

    def test_report_generation_is_deterministic(self) -> None:
        self.assertEqual(reference.report_bytes(), self.payload)
        self.assertEqual(hashlib_sha(reference.report_bytes()),
                         hashlib_sha(self.payload))

    def test_pilot_provenance_matches_frozen_report(self) -> None:
        pilot = self.report["pilot_evidence"]
        self.assertTrue(pilot["provenance_only"])
        self.assertFalse(pilot["reproduced_here"])
        self.assertFalse(pilot["qualifies_candidate"])
        for key, expected in reference.PILOT_CONDITIONS.items():
            self.assertEqual(pilot["conditions"][key]["decoded_input"],
                             expected["decoded_input"])
            self.assertEqual(
                pilot["conditions"][key]["lowpass_decoder_postfilter"],
                expected["lowpass_decoder_postfilter"])

    def test_boundary_is_unchanged(self) -> None:
        boundary = self.report["boundary"]
        self.assertTrue(boundary["installed_v0_unchanged"])
        for key in ("public_api_abi_changed", "provider_registered",
                    "descriptor_registration", "enabled_by_default",
                    "shared_cmake_changed", "ci_changed",
                    "board_or_handoff_changed", "benchmark_claim",
                    "release_claim", "device_timing_measured",
                    "listening_result"):
            self.assertFalse(boundary[key], key)


class PackageTests(unittest.TestCase):
    def test_required_files_exist(self) -> None:
        for name in PACKAGE_FILES:
            self.assertTrue((HERE / name).is_file(), name)

    def test_report_sidecar_matches(self) -> None:
        digest = reference.sha256_file(HERE / "report.json")
        expected = (digest + "  report.json\n").encode("ascii")
        self.assertEqual((HERE / "report.json.sha256").read_bytes(), expected)

    def test_sidecars_have_spdx(self) -> None:
        for name in ("contract.json.license", "report.json.license",
                     "report.json.sha256.license",
                     "SOURCES.sha256.license"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn("SPDX-FileCopyrightText:", text)
            self.assertIn(SPDX_NEEDLE, text)

    def test_source_files_have_spdx(self) -> None:
        for name in ("README.md", "reference.py", "run.py",
                     "test_reference.py", "verify.py"):
            text = (HERE / name).read_text(encoding="utf-8")
            self.assertIn(SPDX_NEEDLE, text)

    def test_no_prohibited_artifacts(self) -> None:
        for path in HERE.iterdir():
            self.assertNotIn(path.suffix.lower(),
                             reference.PROHIBITED_SUFFIXES, path.name)

    def test_artifact_pins_match(self) -> None:
        pins = reference.artifact_pins()
        for name, digest in pins.items():
            self.assertEqual(reference.sha256_file(HERE / name), digest,
                             name)

    def test_contract_pins_match_report_and_sources(self) -> None:
        contract = json.loads((HERE / "contract.json").read_text(
            encoding="utf-8"))
        self.assertEqual(contract["artifact_pins"]["report.json"],
                         reference.sha256_file(HERE / "report.json"))
        self.assertEqual(contract["board_link_projection_sha256"],
                         reference.board_link_projection()[1])
        sources = (HERE / "SOURCES.sha256").read_text(encoding="utf-8")
        self.assertFalse(any(line.rstrip().endswith("plan/swarm/TASKS.json")
                             for line in sources.splitlines()))
        self.assertIn("report.json", sources)


def hashlib_sha(payload: bytes) -> str:
    import hashlib
    return hashlib.sha256(payload).hexdigest()


if __name__ == "__main__":
    unittest.main(verbosity=2)
