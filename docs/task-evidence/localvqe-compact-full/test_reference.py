# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the LocalVQE compact full package.

Run with::

    PYTHONDONTWRITEBYTECODE=1 python3 -m unittest -v test_reference.py

No test uses a network, a real recording, a model, a weight, a native library
or a third-party runtime.  Tests that read generated artifacts fail closed when
the artifacts are stale.
"""

from __future__ import annotations

import hashlib
import json
import tempfile
import unittest
from pathlib import Path

import fixture
import reference
import scorer

HERE = Path(__file__).resolve().parent


def _manifest(root: Path) -> dict:
    model = root / reference.FULL_MODEL_FILENAME
    library = root / reference.LIBRARY_FILENAME
    model.write_bytes(b"deterministic model placeholder\n")
    library.write_bytes(b"deterministic library placeholder\n")
    return {
        "model_path": str(model),
        "model_sha256": fixture.sha256_file(model),
        "library_path": str(library),
        "library_sha256": fixture.sha256_file(library),
        "source_commit": reference.UPSTREAM_COMMIT,
        "variant": "compact-full",
        "sample_rate_hz": fixture.SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": fixture.FRAME_SAMPLES,
        "input_format": "float32",
        "render_delay_samples": 0,
        "algorithmic_latency_samples": fixture.ALGORITHMIC_LATENCY_SAMPLES,
    }


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = fixture.build_components()

    def test_stream_length(self) -> None:
        self.assertEqual(len(self.components["mic"]), fixture.TOTAL_SAMPLES)
        self.assertEqual(fixture.TOTAL_SAMPLES, 64000)

    def test_frame_count(self) -> None:
        frames = fixture.build_frames()
        self.assertEqual(len(frames), fixture.TOTAL_FRAMES)
        self.assertEqual(fixture.TOTAL_FRAMES, 250)

    def test_segments_partition(self) -> None:
        position = 0
        for segment in fixture.SEGMENTS:
            self.assertEqual(segment["start"], position)
            position = segment["end"]
        self.assertEqual(position, fixture.TOTAL_SAMPLES)

    def test_decomposition_is_exact(self) -> None:
        for index in (0, 5000, 20000, 35000, 50000, 63000):
            self.assertEqual(
                self.components["mic"][index],
                self.components["echo"][index]
                + self.components["near"][index]
                + self.components["noise"][index])

    def test_reference_silent_in_near_only(self) -> None:
        for segment in fixture.SEGMENTS:
            if "near_only" in segment["roles"]:
                self.assertTrue(all(
                    value == 0.0 for value in
                    self.components["ref"][segment["start"]:segment["end"]]))

    def test_near_silent_in_echo_only(self) -> None:
        for segment in fixture.SEGMENTS:
            if "echo_only" in segment["roles"]:
                self.assertTrue(all(
                    value == 0.0 for value in
                    self.components["near"][segment["start"]:segment["end"]]))

    def test_stream_is_deterministic(self) -> None:
        self.assertEqual(fixture.stream_digest(), fixture.stream_digest())
        self.assertEqual(len(fixture.FIXTURE_SPEC_DIGEST), 64)

    def test_fixture_has_no_nonfinite(self) -> None:
        for values in self.components.values():
            self.assertTrue(all(isinstance(value, float) for value in values))
            self.assertTrue(all(abs(value) <= 1.0 for value in values))

    def test_segment_totals_sum(self) -> None:
        self.assertEqual(sum(fixture.segment_totals().values()),
                         fixture.TOTAL_SAMPLES)

    def test_primary_path_has_delay(self) -> None:
        self.assertEqual(fixture.PRIMARY_PATH["delay_samples"], 512)
        self.assertEqual(len(fixture.PRIMARY_PATH["taps"]), 5)

    def test_movement_change_inside_echo_stratum(self) -> None:
        segment = next(item for item in fixture.SEGMENTS
                       if item["id"] == "echo-only-b-change")
        self.assertTrue(segment["start"] < fixture.MOVEMENT_CHANGE_SAMPLE
                        < segment["end"])


class SurrogateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = fixture.build_components()
        cls.session = reference._run(cls.components, session_id="test", epoch=1)
        cls.results = scorer.score(cls.components["mic"],
                                   cls.components["near"],
                                   cls.session.output)

    def test_output_length(self) -> None:
        self.assertEqual(len(self.session.output), fixture.TOTAL_SAMPLES)

    def test_first_hop_is_delay(self) -> None:
        self.assertEqual(self.session.output[:256], [0.0] * 256)

    def test_aligned_prefix_is_available(self) -> None:
        aligned, valid = scorer.align_output(self.session.output)
        self.assertEqual(valid, fixture.TOTAL_SAMPLES - 256)
        self.assertEqual(len(aligned), valid)
        self.assertEqual(aligned[0], self.session.output[256])

    def test_echo_only_erle(self) -> None:
        self.assertGreater(
            self.results["strata"]["echo-only-a"]["echo_erle_db"], 10.0)

    def test_echo_pre_movement_better_than_post(self) -> None:
        self.assertGreater(self.results["echo"]["pooled_pre_movement"]["erle_db"],
                           self.results["echo"]["pooled_post_movement"]["erle_db"])

    def test_movement_drop_is_recorded(self) -> None:
        self.assertGreater(self.results["echo"]["movement_drop_db"], 0.0)

    def test_near_snr_is_finite(self) -> None:
        self.assertIsInstance(
            self.results["strata"]["near-only-a"]["near_snr_db"], float)

    def test_near_si_sdr_is_finite(self) -> None:
        self.assertIsInstance(
            self.results["strata"]["near-only-a"]["near_si_sdr_db"], float)

    def test_quiet_near_damage(self) -> None:
        row = self.results["strata"]["near-only-quiet"]
        self.assertLess(row["near_snr_db"], row["identity_near_snr_db"])

    def test_alignment_matters(self) -> None:
        self.assertGreater(self.results["near_end"]["alignment_gain_db"], 0.0)

    def test_output_is_finite_and_bounded(self) -> None:
        self.assertEqual(self.results["peaks"]["nonfinite_output_samples"], 0)
        self.assertEqual(self.results["peaks"]["clipped_samples"], 0)
        self.assertTrue(self.results["peaks"]["within_unit_range"])

    def test_output_is_deterministic(self) -> None:
        again = reference._run(self.components, session_id="again", epoch=1)
        self.assertEqual(self.session.output, again.output)

    def test_tail_is_not_scored(self) -> None:
        self.assertEqual(self.results["availability"]["unavailable_tail_samples"],
                         256)


class CallerAssetTests(unittest.TestCase):
    def test_valid_manifest_is_not_loaded(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            result = reference.validate_caller_asset(_manifest(Path(directory)))
        self.assertEqual(result["verified"], True)
        self.assertEqual(result["loaded"], False)
        self.assertEqual(result["executed"], False)
        self.assertEqual(result["imported"], False)

    def _reject(self, mutate) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = _manifest(Path(directory))
            mutate(manifest)
            with self.assertRaises(ValueError):
                reference.validate_caller_asset(manifest)

    def test_missing_manifest_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.validate_caller_asset({})

    def test_absent_file_rejected(self) -> None:
        self._reject(lambda m: m.update(
            model_path="/nonexistent/localvqe-model.gguf"))

    def test_relative_path_rejected(self) -> None:
        self._reject(lambda m: m.update(
            model_path=reference.FULL_MODEL_FILENAME))

    def test_hash_mismatch_rejected(self) -> None:
        self._reject(lambda m: m.update(model_sha256="0" * 64))

    def test_library_hash_mismatch_rejected(self) -> None:
        self._reject(lambda m: m.update(library_sha256="0" * 64))

    def test_wrong_source_commit_rejected(self) -> None:
        self._reject(lambda m: m.update(source_commit="0" * 40))

    def test_wrong_sample_rate_rejected(self) -> None:
        self._reject(lambda m: m.update(sample_rate_hz=48000))

    def test_wrong_channels_rejected(self) -> None:
        self._reject(lambda m: m.update(channels=2))

    def test_wrong_frame_size_rejected(self) -> None:
        self._reject(lambda m: m.update(frame_samples=512))

    def test_wrong_input_format_rejected(self) -> None:
        self._reject(lambda m: m.update(input_format="int16"))

    def test_wrong_variant_rejected(self) -> None:
        self._reject(lambda m: m.update(variant="echo-only"))

    def test_wrong_render_delay_rejected(self) -> None:
        self._reject(lambda m: m.update(render_delay_samples=256))

    def test_wrong_latency_rejected(self) -> None:
        self._reject(lambda m: m.update(algorithmic_latency_samples=0))

    def test_extra_field_rejected(self) -> None:
        self._reject(lambda m: m.update(extra_field="x"))

    def test_placeholder_never_matches_pinned_identity(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            manifest = _manifest(Path(directory))
            with self.assertRaises(ValueError):
                reference.pinned_asset_identity(manifest)


class FrameTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.frames = fixture.build_frames()

    def _session(self) -> reference.Session:
        session = reference.Session(fixture.CONFIG, "frame", 2)
        session.process_frame(self.frames[0]["mic"], self.frames[0]["ref"])
        return session

    def test_nan_mic_rejected(self) -> None:
        session = self._session()
        before = session.state_digest()
        with self.assertRaises(ValueError):
            session.process_frame([float("nan")] + [0.0] * 255,
                                  self.frames[1]["ref"])
        self.assertEqual(session.state_digest(), before)

    def test_inf_ref_rejected(self) -> None:
        session = self._session()
        before = session.state_digest()
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"],
                                  [float("inf")] + [0.0] * 255)
        self.assertEqual(session.state_digest(), before)

    def test_short_nonfinal_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"][:128],
                                  self.frames[1]["ref"][:128])

    def test_long_frame_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"] + [0.0],
                                  self.frames[1]["ref"] + [0.0])

    def test_empty_frame_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame([], [])

    def test_out_of_range_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame([1.5] + [0.0] * 255,
                                  self.frames[1]["ref"])

    def test_bool_sample_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame([True] + [0.0] * 255,
                                  self.frames[1]["ref"])

    def test_ref_length_mismatch_rejected(self) -> None:
        session = self._session()
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"],
                                  self.frames[1]["ref"][:255])

    def test_partial_tail_padded(self) -> None:
        session = reference.Session(fixture.CONFIG, "partial", 3)
        session.process_frame(self.frames[0]["mic"], self.frames[0]["ref"])
        session.process_frame(self.frames[1]["mic"][:128],
                              self.frames[1]["ref"][:128], final=True,
                              valid_samples=128)
        self.assertEqual(session.frames[-1]["end_sample"], 384)
        self.assertEqual(session.frames[-1]["padded_samples"], 128)
        self.assertEqual(len(session.drain()), 256)

    def test_partial_length_mismatch_rejected(self) -> None:
        session = reference.Session(fixture.CONFIG, "partial", 3)
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"][:128],
                                  self.frames[1]["ref"][:128], final=True,
                                  valid_samples=127)


class ConfigTests(unittest.TestCase):
    def _reject(self, key: str, value) -> None:
        config = dict(fixture.CONFIG)
        config[key] = value
        with self.assertRaises(ValueError):
            reference.Session(config, "config", 1)

    def test_wrong_sample_rate(self) -> None:
        self._reject("sample_rate_hz", 48000)

    def test_wrong_channels(self) -> None:
        self._reject("channels", 2)

    def test_wrong_format(self) -> None:
        self._reject("sample_format", "s16")

    def test_wrong_frame(self) -> None:
        self._reject("frame_samples", 320)

    def test_wrong_latency(self) -> None:
        self._reject("algorithmic_latency_samples", 0)

    def test_wrong_render_delay(self) -> None:
        self._reject("render_delay_samples", 256)

    def test_real_runtime_rejected(self) -> None:
        self._reject("real_runtime", True)

    def test_model_use_rejected(self) -> None:
        self._reject("model_or_library_used", True)

    def test_missing_session_id_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.Session(dict(fixture.CONFIG), "", 1)

    def test_negative_epoch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.Session(dict(fixture.CONFIG), "x", -1)


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = fixture.build_components()
        cls.frames = [
            {"mic": cls.components["mic"][index * 256:(index + 1) * 256],
             "ref": cls.components["ref"][index * 256:(index + 1) * 256]}
            for index in range(fixture.TOTAL_FRAMES)
        ]

    def test_reset_matches_fresh(self) -> None:
        result = reference.reset_control(self.frames)
        self.assertTrue(result["reset_matches_fresh_digest"])
        self.assertTrue(result["epoch_propagated"])

    def test_independent_sessions(self) -> None:
        result = reference.reset_control(self.frames)
        self.assertTrue(result["independent_sessions_uncoupled"])

    def test_streaming_parity(self) -> None:
        result = reference.streaming_parity_control(self.components)
        self.assertTrue(result["events_identical"])
        self.assertEqual(result["offline_digest"], result["streaming_digest"])

    def test_delayed_render_fails(self) -> None:
        result = reference.delay_and_render_control(self.components)
        self.assertTrue(result["delayed_render_is_failure"])

    def test_missing_render_fails(self) -> None:
        result = reference.delay_and_render_control(self.components)
        self.assertTrue(result["missing_render_is_failure"])

    def test_no_reference_misuse_labeled(self) -> None:
        result = reference.delay_and_render_control(self.components)
        self.assertTrue(result["no_reference_is_misuse_not_a_pass"])

    def test_frame_adverse_control(self) -> None:
        result = reference.frame_adverse_control()
        self.assertTrue(result["all_fail_closed"])
        self.assertEqual(result["final_partial_end_sample"], 384)

    def test_asset_control_fail_closed(self) -> None:
        result = reference._asset_controls()
        self.assertTrue(result["all_fail_closed"])
        self.assertEqual(result["workspace_pinned_asset"]["status"], "rejected")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.contract_payload()
        cls.readiness = reference.readiness_payload()
        cls.adapter = reference.adapter_payload()

    def test_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"], "not_qualified")

    def test_profile_is_room(self) -> None:
        self.assertEqual(self.report["profile"], "room")

    def test_boundary_is_unchanged(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertFalse(value)

    def test_gates_are_blocked(self) -> None:
        self.assertEqual(len(self.report["gates"]),
                         len(reference.GATE_DEFINITIONS))
        for gate in self.report["gates"]:
            self.assertEqual(gate["status"], "blocked")

    def test_no_missing_result_qualifies(self) -> None:
        self.assertTrue(self.report["no_missing_result_qualifies_candidate"])

    def test_canonical_bytes_are_stable(self) -> None:
        first = reference.canonical_report_bytes(self.report)
        second = reference.canonical_report_bytes(self.report)
        self.assertEqual(first, second)

    def test_repeatability(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_contract_digest(self) -> None:
        self.assertEqual(
            self.report["contract_sha256"],
            reference.sha256(reference.contract_bytes()))

    def test_readiness_is_strict(self) -> None:
        self.assertEqual(self.readiness["decision"], "DEFER")
        self.assertFalse(self.readiness["ready_for_opt_in_adapter"])
        self.assertFalse(self.readiness["ready_for_provider_registration"])
        self.assertFalse(self.readiness["ready_for_release"])

    def test_adapter_is_proposal_only(self) -> None:
        self.assertFalse(self.adapter["implemented"])
        self.assertFalse(self.adapter["registered"])
        self.assertTrue(self.adapter["requires_far_end_reference"])

    def test_acceptance_profile_items(self) -> None:
        for item in reference.ACCEPTANCE_PROFILE_ITEMS:
            self.assertTrue(self.report["acceptance_profile"][item])

    def test_source_reported_not_used(self) -> None:
        self.assertEqual(self.report["source_reported"]["status"],
                         "source_reported_not_reproduced")
        self.assertFalse(self.report["source_reported"]["used_for_qualification"])

    def test_licensing_is_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        self.assertFalse(licensing["model_redistribution_clearance"])
        self.assertFalse(licensing["product_use_clearance"])
        self.assertFalse(licensing["asset_copied_vendored_built_or_downloaded"])

    def test_no_negative_zero(self) -> None:
        self.assertFalse(reference.has_negative_zero(self.report))

    def test_strict_json_duplicate_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":NaN}')

    def test_pin_lines_reject_traversal(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_pin_lines("a" * 64 + "  ../escape")

    def test_readme_digest_tables(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(fixture.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(fixture.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.LOCAL_ARTIFACT_PATHS))
        self.assertEqual(counts["external-absent"],
                         len(fixture.EXTERNAL_ASSET_PINS))
        self.assertEqual(counts["external-runtime"],
                         len(fixture.EXTERNAL_RUNTIME_PINS))

    def test_sources_pin_manifest(self) -> None:
        pins = reference.parse_pin_lines(
            (HERE / "SOURCES.sha256").read_text(encoding="ascii"))
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))

    def test_report_json_matches_builder(self) -> None:
        self.assertEqual((HERE / "report.json").read_bytes(),
                         reference.canonical_report_bytes(self.report))

    def test_report_sidecar_matches(self) -> None:
        digest = hashlib.sha256((HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
