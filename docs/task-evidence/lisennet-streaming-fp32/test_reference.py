# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest checks for the task-local evidence package."""

from __future__ import annotations

import hashlib
import json
import sys
import unittest
from pathlib import Path

import numpy as np

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import reference as ref  # noqa: E402
import run as cli  # noqa: E402


class CanonicalTests(unittest.TestCase):
    def test_sorted_compact_and_stable(self):
        payload = b'{"a":1,"b":[2,3]}'
        self.assertEqual(ref.canonical_bytes({"b": [2, 3], "a": 1}), payload)
        self.assertEqual(ref.canonical_bytes({"b": [2, 3], "a": 1}), payload)

    def test_rounds_and_removes_negative_zero(self):
        self.assertEqual(json.loads(ref.canonical_bytes({"x": -0.0000001})), {"x": 0.0})
        self.assertEqual(json.loads(ref.canonical_bytes({"x": 1.23456789})), {"x": 1.234568})

    def test_nonfinite_rejected(self):
        with self.assertRaises(ValueError):
            ref.canonical_bytes({"x": float("nan")})

    def test_strict_rejection_examples(self):
        self.assertEqual(ref.strict_rejection_examples(),
                         {"json": 5, "manifests": 4})

    def test_strict_loads_rejects_duplicate_and_nonfinite(self):
        for text in ('{"a":1,"a":2}', '{"a":NaN}', '{"a":Infinity}'):
            with self.assertRaises(ValueError):
                ref.strict_loads(text)

    def test_sha32_is_float32_digest(self):
        signal = np.asarray([0.5, -0.25], dtype=np.float32)
        expected = hashlib.sha256(signal.astype("<f4").tobytes()).hexdigest()
        self.assertEqual(ref.sha32(signal), expected)


class GeometryTests(unittest.TestCase):
    def test_geometry_constants(self):
        self.assertEqual((ref.SAMPLE_RATE_HZ, ref.N_FFT, ref.HOP_SAMPLES,
                          ref.N_FREQS, ref.COMPRESS_POWER),
                         (16000, 512, 256, 257, 0.3))
        self.assertEqual((ref.FRAME_SAMPLES, ref.SAMPLES), (160, 32000))

    def test_state_cache_contract(self):
        self.assertEqual(len(ref.STATE_SLOTS), ref.STATE_SLOT_COUNT)
        self.assertEqual(sum(slot["past_frames"] for slot in ref.STATE_SLOTS),
                         ref.STATE_PAST_FRAME_ROWS)
        self.assertEqual(ref.STATE_SLOT_COUNT, 17)
        self.assertEqual(ref.STATE_PAST_FRAME_ROWS, 71)

    def test_geometry_preserved(self):
        self.assertEqual(ref.FORMAT["frame_samples"], 160)
        self.assertEqual(ref.FORMAT["sample_rate_hz"], 16000)
        self.assertEqual(ref.FORMAT["channels"], 1)
        self.assertTrue(ref.BOUNDARY["installed_v0_geometry_preserved"])


class AssetBoundaryTests(unittest.TestCase):
    def test_default_manifest_validates(self):
        manifest = ref.default_asset_manifest()
        self.assertEqual(ref.validate_asset_manifest(manifest), manifest)

    def test_missing_and_extra_fields(self):
        manifest = ref.default_asset_manifest()
        manifest["extra"] = 1
        with self.assertRaises(ValueError):
            ref.validate_asset_manifest(manifest)
        manifest = ref.default_asset_manifest()
        del manifest["sha256"]
        with self.assertRaises(ValueError):
            ref.validate_asset_manifest(manifest)

    def test_wrong_values_rejected(self):
        for field, value in (("sha256", "0" * 64),
                             ("byte_count", ref.MODEL_BYTES + 1),
                             ("state_slot_count", 16),
                             ("sample_rate_hz", 48000),
                             ("n_fft", 1024)):
            manifest = ref.default_asset_manifest()
            manifest[field] = value
            with self.assertRaises(ValueError):
                ref.validate_asset_manifest(manifest)

    def test_relative_caller_path_rejected(self):
        manifest = ref.default_asset_manifest()
        manifest["caller_path"] = "relative/model.onnx"
        with self.assertRaises(ValueError):
            ref.validate_asset_manifest(manifest)

    def test_absolute_caller_path_accepted_but_never_read(self):
        manifest = ref.default_asset_manifest()
        manifest["caller_path"] = "/nonexistent/caller/model.onnx"
        self.assertTrue(ref.validate_asset_manifest(manifest))
        admission = ref.admit_asset(manifest)
        self.assertFalse(admission["asset_bytes_read"])
        self.assertFalse(admission["asset_file_accessed"])

    def test_admission_is_blocked_with_exact_reasons(self):
        admission = ref.admit_asset(ref.default_asset_manifest())
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(admission["reason_codes"], list(ref.ASSET_ADMISSION_REASONS))
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])

    def test_synthetic_control_is_not_the_candidate(self):
        control = ref.synthetic_admission_control()
        self.assertEqual(control["status"], "admitted")
        self.assertTrue(control["not_the_pinned_candidate"])
        self.assertFalse(control["asset_bytes_read"])


class StreamingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.clean, cls.observed = ref.synth("mixture_snr18")

    def test_opt_in_required(self):
        with self.assertRaises(ValueError):
            ref.StreamingSurrogate(opt_in=False)

    def test_length_and_finite_output(self):
        result = ref.run_stream(self.observed, 160)
        self.assertEqual(result["output"].size, ref.SAMPLES)
        self.assertTrue(np.all(np.isfinite(result["output"])))
        self.assertLessEqual(float(np.max(np.abs(result["output"]))), 1.0)
        self.assertEqual(result["state_slots"], 17)
        self.assertEqual(result["state_past_frame_rows"], 71)

    def test_chunk_invariance(self):
        reference = ref.run_stream(self.observed, 160)
        for size in (1, 7, 159, 161, 256, 257, 1280, ref.SAMPLES):
            result = ref.run_stream(self.observed, size)
            self.assertEqual(result["digest"], reference["digest"], size)

    def test_emitted_before_flush_plus_flush(self):
        result = ref.run_stream(self.observed, 160)
        self.assertEqual(result["emitted_before_flush"] + result["flush_emitted"],
                         ref.SAMPLES)
        self.assertEqual(result["emitted_before_flush"], ref.SAMPLES - 2 * ref.HOP_SAMPLES)

    def test_short_stream_rejected(self):
        session = ref.StreamingSurrogate(opt_in=True)
        session.process(np.zeros(100, dtype=np.float64))
        with self.assertRaises(ValueError):
            session.flush()

    def test_process_after_flush_rejected(self):
        session = ref.StreamingSurrogate(opt_in=True)
        session.process(np.zeros(1024, dtype=np.float64))
        session.flush()
        with self.assertRaises(ValueError):
            session.process(np.zeros(160, dtype=np.float64))

    def test_second_flush_empty(self):
        session = ref.StreamingSurrogate(opt_in=True)
        session.process(np.zeros(1024, dtype=np.float64))
        self.assertGreater(session.flush().size, 0)
        self.assertEqual(session.flush().size, 0)

    def test_reset_replay_identical(self):
        first = ref.run_stream(self.observed, 160)
        replay = ref.run_stream(self.observed, 397)
        self.assertEqual(first["digest"], replay["digest"])
        self.assertEqual(first["state_digest"], replay["state_digest"])

    def test_reset_restores_initial_state(self):
        first = ref.StreamingSurrogate(opt_in=True)
        first.process(np.zeros(2048, dtype=np.float64))
        first.flush()
        first.reset()
        fresh = ref.StreamingSurrogate(opt_in=True)
        self.assertEqual(first.state_digest(), fresh.state_digest())

    def test_invalid_inputs_state_unchanged(self):
        session = ref.StreamingSurrogate(opt_in=True)
        session.process(np.zeros(160, dtype=np.float64))
        before = session.state_digest()
        for bad in (np.zeros((4, 2)), np.asarray([0.0, float("nan")]),
                    np.asarray([0.0, float("inf")]), np.asarray(["a", "b"])):
            with self.assertRaises((ValueError, TypeError)):
                session.process(bad)
            self.assertEqual(session.state_digest(), before)

    def test_empty_chunk(self):
        session = ref.StreamingSurrogate(opt_in=True)
        before = session.state_digest()
        self.assertEqual(session.process(np.zeros(0)).size, 0)
        self.assertEqual(session.state_digest(), before)

    def test_zero_length_stream_flush(self):
        session = ref.StreamingSurrogate(opt_in=True)
        self.assertEqual(session.flush().size, 0)

    def test_alignment_has_zero_content_lag(self):
        probe = ref.alignment_probe()
        self.assertEqual(probe["input_peak_sample"], ref.IMPULSE_INDEX)
        self.assertEqual(probe["output_peak_sample"], ref.IMPULSE_INDEX)
        self.assertEqual(probe["residual_lag_samples"], 0)
        self.assertEqual(probe["availability_lag_samples"], ref.HOP_SAMPLES)
        self.assertFalse(probe["lag_measured"])


class ScoringTests(unittest.TestCase):
    def test_identity_is_exact_and_undefined(self):
        clean, observed = ref.synth("target_only")
        result = ref.score(clean, observed)
        self.assertIsNone(result["snr_db"])
        self.assertIsNone(result["si_sdr_db"])
        self.assertIn("zero_error_identity_exact", result["undefined"])
        self.assertAlmostEqual(result["stoi"], 1.0, places=9)

    def test_zero_reference_is_invalid(self):
        clean, observed = ref.synth("noise_only")
        result = ref.score(clean, observed)
        self.assertIn("zero_reference", result["undefined"])
        self.assertIsNone(result["snr_db"])
        self.assertIsNone(result["si_sdr_db"])

    def test_surrogate_scores_are_finite_and_bounded(self):
        for condition in ref.CONDITIONS:
            clean, observed = ref.synth(condition)
            output = ref.run_stream(observed, 160)["output"]
            result = ref.score(clean, output)
            if result["stoi"] is not None:
                self.assertGreaterEqual(result["stoi"], 0.0)
                self.assertLessEqual(result["stoi"], 1.0)
            self.assertTrue(np.all(np.isfinite(output)))

    def test_target_damage_is_recorded_as_adverse(self):
        clean, _ = ref.synth("target_only")
        report = json.loads(ref.canonical_report_bytes(ref.build_report()))
        target = report["conditions"]["target_only"]["variants"][
            "surrogate_stream_160"]
        self.assertIsNotNone(target["si_sdr_db"])
        self.assertLess(target["si_sdr_db"], 60.0)
        self.assertTrue(any(item["condition"] == "target_only"
                            for item in report["regressions"]))

    def test_stimuli_are_deterministic_and_bounded(self):
        clean_a, observed_a = ref.synth("mixture_snr24")
        clean_b, observed_b = ref.synth("mixture_snr24")
        self.assertTrue(np.array_equal(clean_a, clean_b))
        self.assertTrue(np.array_equal(observed_a, observed_b))
        self.assertLessEqual(float(np.max(np.abs(observed_a))), ref.PEAK_GUARD)


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.report = ref.build_report()
        cls.contract = ref.build_contract()
        cls.adapter = ref.build_adapter()
        cls.readiness = ref.build_readiness()

    def test_identity_and_disposition(self):
        self.assertEqual(self.report["task_id"], ref.TASK)
        self.assertEqual(self.report["component"], ref.SLUG)
        self.assertEqual(self.report["base_commit"], ref.BASE_COMMIT)
        self.assertEqual(self.report["branch"], ref.BRANCH)
        self.assertEqual(self.report["profile"], "enhancement")
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")
        self.assertEqual(self.report["status"], ref.STATUS)

    def test_all_claims_false(self):
        self.assertTrue(self.report["claims"])
        self.assertTrue(all(value is False for value in self.report["claims"].values()))
        self.assertTrue(all(value is False
                            for key, value in self.report["boundary"].items()
                            if isinstance(value, bool)
                            and key != "installed_v0_geometry_preserved"))

    def test_conditions_and_variants(self):
        self.assertEqual(set(self.report["conditions"]), set(ref.CONDITIONS))
        for block in self.report["conditions"].values():
            self.assertEqual(set(block["variants"]), {
                "identity_passthrough", "noisy_control",
                "surrogate_stream_160", "surrogate_whole_call"})
            self.assertTrue(block["large_chunk_matches_160"])
            self.assertEqual(block["tail_validity"]["valid_samples"],
                             ref.SAMPLES)

    def test_streaming_boundary(self):
        boundary = self.report["streaming_boundary"]
        self.assertEqual(boundary["declared_content_lag_samples"], 0)
        self.assertEqual(boundary["declared_availability_lag_samples"], 256)
        self.assertFalse(boundary["lag_measured"])
        self.assertTrue(boundary["chunk_invariance"]["chunk_invariant"])
        self.assertTrue(boundary["chunk_invariance"]["whole_call_matches_chunked"])
        state = boundary["state"]
        self.assertTrue(state["replay_identical"])
        self.assertTrue(state["independent_session_identical"])
        self.assertTrue(state["cross_stream_reset_identical"])
        self.assertFalse(state["real_recurrent_state_loaded"])

    def test_state_cache_exposed(self):
        cache = self.report["state_cache"]
        self.assertEqual(cache["slot_count"], 17)
        self.assertEqual(cache["past_frame_rows"], 71)
        self.assertEqual(len(cache["slots"]), 17)

    def test_asset_boundary_blocked(self):
        asset = self.report["asset_boundary"]
        self.assertEqual(asset["readiness"], "blocked")
        self.assertEqual(asset["reason_codes"], list(ref.ASSET_ADMISSION_REASONS))
        self.assertEqual(asset["asset"]["sha256"], ref.MODEL_SHA256)
        self.assertEqual(asset["asset"]["byte_count"], ref.MODEL_BYTES)
        self.assertFalse(asset["asset"]["bytes_present"])
        self.assertFalse(asset["admission"]["asset_bytes_read"])
        self.assertTrue(asset["synthetic_admission_control"][
            "not_the_pinned_candidate"])

    def test_enhancement_profile(self):
        profile = self.report["enhancement_profile"]
        self.assertEqual(profile["name"], "enhancement")
        self.assertTrue(profile["identity_and_noisy_controls"])
        self.assertEqual(profile["stoi"]["status"], "synthetic_only")
        self.assertFalse(profile["content_and_availability_timing"]["measured"])
        self.assertEqual(profile["listening"]["status"], "not_run")
        self.assertFalse(profile["real_runtime"])
        self.assertFalse(profile["real_clean_references"])

    def test_adverse_cases(self):
        adverse = self.report["adverse"]
        configs = adverse["config_rejections"]
        for name, case in configs.items():
            if name in ("caller_asset_unavailable", "synthetic_admission_control"):
                continue
            self.assertTrue(case["status"].startswith("rejected"), name)
        for name, case in adverse["frame_cases"]["cases"].items():
            if name == "empty_chunk":
                self.assertEqual(case["status"], "accepted_empty")
            else:
                self.assertTrue(case["status"].startswith("rejected"), name)
            self.assertTrue(case["state_unchanged"], name)

    def test_gates_and_blockers(self):
        self.assertEqual(len(self.report["gates"]), 10)
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["reopen"])
        self.assertEqual(len(self.report["exact_blockers"]), 4)
        self.assertEqual(len(self.report["missing_evidence"]), 9)

    def test_no_negative_zero_or_nonfinite(self):
        self.assertFalse(ref.has_negative_zero(self.report))
        payload = ref.canonical_report_bytes(self.report)
        self.assertNotIn(b"NaN", payload)
        self.assertNotIn(b"Infinity", payload)

    def test_repeatability(self):
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_disposition_documents(self):
        self.assertEqual(self.contract["decision"], "DEFER")
        self.assertEqual(self.adapter["decision"], "DEFER")
        self.assertEqual(self.readiness["decision"], "DEFER")
        self.assertEqual(self.readiness["status"], "blocked")
        self.assertFalse(self.readiness["qualified"])
        self.assertFalse(self.adapter["registered"])
        self.assertFalse(self.adapter["implemented"])
        self.assertFalse(self.adapter["quality_claim"])
        for key in ("ready_for_opt_in_adapter", "ready_for_provider_registration",
                    "ready_for_release", "quality_pass"):
            self.assertFalse(self.readiness[key])

    def test_readiness_digests_bound(self):
        report_digest = hashlib.sha256(
            ref.canonical_report_bytes(self.report)).hexdigest()
        contract_digest = hashlib.sha256(
            ref.canonical_bytes(self.contract)).hexdigest()
        self.assertEqual(self.readiness["report_sha256"], report_digest)
        self.assertEqual(self.readiness["contract_sha256"], contract_digest)

    def test_sidecar_and_files_are_canonical(self):
        payload = ref.canonical_report_bytes()
        self.assertEqual((HERE / "report.json").read_bytes(), payload)
        sidecar = (HERE / "report.json.sha256").read_text(encoding="utf-8")
        self.assertEqual(sidecar, hashlib.sha256(payload).hexdigest()
                         + "  report.json\n")
        self.assertEqual((HERE / "adapter.json").read_bytes(),
                         ref.canonical_bytes(ref.build_adapter()) + b"\n")
        self.assertEqual((HERE / "readiness.json").read_bytes(),
                         ref.canonical_bytes(ref.build_readiness()) + b"\n")
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         cli.contract_bytes(cli.contract_pins()))
        self.assertEqual((HERE / "SOURCES.sha256").read_bytes(),
                         cli.manifest_bytes())

    def test_readme_digest_table(self):
        rows = ref.readme_pin_rows()
        self.assertEqual(dict(rows), ref.SOURCE_PINS)
        self.assertEqual(len(rows), len(ref.SOURCE_PINS))

    def test_source_pins_exist(self):
        for path, digest in ref.SOURCE_PINS.items():
            target = ref.SOURCE_ROOT / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(ref.sha256_file(target), digest, path)

    def test_boundary_pins_exist(self):
        for path, digest in ref.BOUNDARY_PINS.items():
            target = ref.SDK_ROOT / path
            self.assertTrue(target.is_file(), path)
            self.assertEqual(ref.sha256_file(target), digest, path)

    def test_local_file_set(self):
        expected = set(ref.LOCAL_FILES) | {"SOURCES.sha256"}
        for name in expected:
            self.assertTrue((HERE / name).is_file(), name)
            if name.endswith(".license"):
                self.assertIn("SPDX" "-License-Identifier: Apache-2.0",
                              (HERE / name).read_text(encoding="utf-8"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
