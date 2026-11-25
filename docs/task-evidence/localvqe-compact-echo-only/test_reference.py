# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unittest coverage for the LocalVQE compact echo-only package.

Run with::

    PYTHONDONTWRITEBYTECODE=1 SOURCE_ROOT=<workspace> \
        python3 -m unittest -v test_reference.py

No test uses a network, a real recording, a model, a weight, a native library
or a third-party runtime. Tests that read generated artifacts fail closed when
the artifacts are stale.
"""

from __future__ import annotations

import hashlib
import tempfile
import unittest
from pathlib import Path

import reference

HERE = Path(__file__).resolve().parent


def _manifest(root: Path) -> dict:
    model = root / reference.ECHO_MODEL_FILENAME
    library = root / reference.LIBRARY_FILENAME
    model.write_bytes(b"deterministic echo model placeholder\n")
    library.write_bytes(b"deterministic library placeholder\n")
    return {
        "model_path": str(model),
        "model_sha256": reference.sha256_file(model),
        "library_path": str(library),
        "library_sha256": reference.sha256_file(library),
        "source_commit": reference.UPSTREAM_COMMIT,
        "variant": "compact-echo-only",
        "sample_rate_hz": reference.SAMPLE_RATE_HZ,
        "channels": 1,
        "frame_samples": reference.FRAME_SAMPLES,
        "input_format": "float32",
        "render_delay_samples": 0,
        "algorithmic_latency_samples": reference.ALGORITHMIC_LATENCY_SAMPLES,
    }


class FixtureTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = reference.build_components()

    def test_stream_length(self) -> None:
        self.assertEqual(len(self.components["mic"]), reference.TOTAL_SAMPLES)
        self.assertEqual(reference.TOTAL_SAMPLES, 64000)

    def test_frame_count(self) -> None:
        frames = reference.build_frames()
        self.assertEqual(len(frames), reference.TOTAL_FRAMES)
        self.assertEqual(reference.TOTAL_FRAMES, 250)

    def test_segments_partition(self) -> None:
        position = 0
        for segment in reference.SEGMENTS:
            self.assertEqual(segment["start"], position)
            position = segment["end"]
        self.assertEqual(position, reference.TOTAL_SAMPLES)

    def test_decomposition_is_exact(self) -> None:
        for index in (0, 5000, 20000, 35000, 50000, 63000):
            self.assertEqual(
                self.components["mic"][index],
                self.components["echo"][index]
                + self.components["near"][index]
                + self.components["noise"][index])

    def test_reference_silent_in_near_only(self) -> None:
        for segment in reference.SEGMENTS:
            if "near_only" in segment["roles"]:
                self.assertTrue(all(
                    value == 0.0 for value in
                    self.components["ref"][segment["start"]:segment["end"]]))

    def test_near_silent_in_echo_only(self) -> None:
        for segment in reference.SEGMENTS:
            if "echo_only" in segment["roles"]:
                self.assertTrue(all(
                    value == 0.0 for value in
                    self.components["near"][segment["start"]:segment["end"]]))

    def test_stream_is_deterministic(self) -> None:
        self.assertEqual(reference.stream_digest(), reference.stream_digest())
        self.assertEqual(len(reference.FIXTURE_SPEC_DIGEST), 64)

    def test_fixture_has_no_nonfinite(self) -> None:
        for values in self.components.values():
            self.assertTrue(all(isinstance(value, float) for value in values))
            self.assertTrue(all(abs(value) <= 1.0 for value in values))

    def test_segment_totals_sum(self) -> None:
        self.assertEqual(sum(reference.segment_totals().values()),
                         reference.TOTAL_SAMPLES)

    def test_primary_path_has_delay(self) -> None:
        self.assertEqual(reference.PRIMARY_PATH["delay_samples"], 512)
        self.assertEqual(len(reference.PRIMARY_PATH["taps"]), 5)

    def test_movement_change_inside_echo_stratum(self) -> None:
        segment = next(item for item in reference.SEGMENTS
                       if item["id"] == "echo-only-b-change")
        self.assertTrue(segment["start"] < reference.MOVEMENT_CHANGE_SAMPLE
                        < segment["end"])


class SurrogateTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = reference.build_components()
        cls.session = reference._run(cls.components, session_id="test", epoch=1)
        cls.results = reference.score(cls.components["mic"],
                                      cls.components["near"],
                                      cls.session.output)

    def test_output_length(self) -> None:
        self.assertEqual(len(self.session.output), reference.TOTAL_SAMPLES)

    def test_first_hop_is_delay(self) -> None:
        self.assertEqual(self.session.output[:256], [0.0] * 256)

    def test_aligned_prefix_is_available(self) -> None:
        aligned, valid = reference.align_output(self.session.output)
        self.assertEqual(valid, reference.TOTAL_SAMPLES - 256)
        self.assertEqual(len(aligned), valid)
        self.assertEqual(aligned[0], self.session.output[256])

    def test_echo_only_erle(self) -> None:
        self.assertGreater(
            self.results["strata"]["echo-only-a"]["echo_erle_db"], 10.0)

    def test_echo_pre_movement_better_than_post(self) -> None:
        self.assertGreater(
            self.results["echo"]["pooled_pre_movement"]["erle_db"],
            self.results["echo"]["pooled_post_movement"]["erle_db"])

    def test_movement_drop_is_recorded(self) -> None:
        self.assertGreater(self.results["echo"]["movement_drop_db"], 0.0)

    def test_near_only_matches_identity_exactly(self) -> None:
        row = self.results["strata"]["near-only-a"]
        self.assertEqual(row["near_snr_db"], row["identity_near_snr_db"])
        self.assertEqual(row["near_si_sdr_db"], row["identity_near_si_sdr_db"])

    def test_overlap_improves_over_identity(self) -> None:
        row = self.results["strata"]["overlap-a"]
        self.assertGreater(row["near_snr_db"], row["identity_near_snr_db"])

    def test_overlap_si_sdr_is_finite(self) -> None:
        self.assertIsInstance(
            self.results["strata"]["overlap-a"]["near_si_sdr_db"], float)

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
        self.assertEqual(
            self.results["availability"]["unavailable_tail_samples"], 256)

    def test_echo_only_session_has_no_noise_stage(self) -> None:
        report = reference.build_report()
        self.assertFalse(report["surrogate"]["noise_suppression_stage"])
        self.assertFalse(report["surrogate"]["dereverberation_stage"])


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
            model_path="/nonexistent/localvqe-echo.gguf"))

    def test_relative_path_rejected(self) -> None:
        self._reject(lambda m: m.update(
            model_path=reference.ECHO_MODEL_FILENAME))

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

    def test_full_variant_rejected(self) -> None:
        self._reject(lambda m: m.update(variant="compact-full"))

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
        cls.frames = reference.build_frames()

    def _session(self) -> reference.Session:
        session = reference.Session(reference.CONFIG, "frame", 2)
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
        session = reference.Session(reference.CONFIG, "partial", 3)
        session.process_frame(self.frames[0]["mic"], self.frames[0]["ref"])
        session.process_frame(self.frames[1]["mic"][:128],
                              self.frames[1]["ref"][:128], final=True,
                              valid_samples=128)
        self.assertEqual(session.frames[-1]["end_sample"], 384)
        self.assertEqual(session.frames[-1]["padded_samples"], 128)
        self.assertEqual(len(session.drain()), 256)

    def test_partial_length_mismatch_rejected(self) -> None:
        session = reference.Session(reference.CONFIG, "partial", 3)
        with self.assertRaises(ValueError):
            session.process_frame(self.frames[1]["mic"][:128],
                                  self.frames[1]["ref"][:128], final=True,
                                  valid_samples=127)


class ConfigTests(unittest.TestCase):
    def _reject(self, key: str, value) -> None:
        config = dict(reference.CONFIG)
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

    def test_wrong_variant(self) -> None:
        self._reject("variant", "compact-full")

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
            reference.Session(dict(reference.CONFIG), "", 1)

    def test_negative_epoch_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.Session(dict(reference.CONFIG), "x", -1)


class ControlTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.components = reference.build_components()
        cls.frames = [
            {"mic": cls.components["mic"][index * 256:(index + 1) * 256],
             "ref": cls.components["ref"][index * 256:(index + 1) * 256]}
            for index in range(reference.TOTAL_FRAMES)
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
        self.assertEqual(result["offline_digest"],
                         result["streaming_digest"])

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
        self.assertEqual(result["workspace_pinned_asset"]["status"],
                         "rejected")
        self.assertEqual(result["pinned_placeholder"]["status"], "rejected")

    def test_full_variant_asset_rejected(self) -> None:
        result = reference._asset_controls()
        self.assertEqual(result["wrong_variant"]["status"], "rejected")


class ReportTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()
        cls.contract = reference.contract_payload()

    def test_disposition(self) -> None:
        self.assertEqual(self.report["decision"], "DEFER")
        self.assertEqual(self.report["status"], "proposal_only_incomplete")
        self.assertEqual(self.report["evidence_status"], "incomplete")
        self.assertEqual(self.report["qualification_status"],
                         "not_qualified")
        self.assertEqual(self.report["qualification"]["status"],
                         "not_qualified")
        self.assertFalse(self.report["qualification"]["qualified"])

    def test_profile_is_room(self) -> None:
        self.assertEqual(self.report["profile"], "room")

    def test_boundary_is_unchanged(self) -> None:
        for key, value in self.report["boundary"].items():
            if key == "descriptor_settings":
                self.assertEqual(value, {})
            else:
                self.assertFalse(value)

    def test_exactly_eight_blocked_gates(self) -> None:
        self.assertEqual(self.report["release_gate_count"], 8)
        self.assertEqual(len(self.report["release_gates"]), 8)
        for gate in self.report["release_gates"]:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen_condition"])

    def test_gate_names_are_exact(self) -> None:
        expected = {
            "exact_echo_asset_identity",
            "model_and_runtime_rights",
            "exact_runtime_reproduction",
            "streaming_boundary_and_one_hop_latency",
            "rights_cleared_paired_reference_cohort",
            "room_echo_near_overlap_no_reference_acceptance",
            "target_runtime_timing_memory",
            "provider_intake_and_default_selection",
        }
        self.assertEqual(
            {gate["name"] for gate in self.report["release_gates"]}, expected)

    def test_no_missing_result_qualifies(self) -> None:
        self.assertTrue(
            self.report["no_missing_result_qualifies_candidate"])
        self.assertFalse(
            self.report["qualification"]["missing_result_may_qualify"])

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

    def test_source_checkout_present(self) -> None:
        probe = self.report["source_probe"]
        self.assertTrue(probe["present"])
        self.assertEqual(probe["revision"], reference.UPSTREAM_COMMIT)
        self.assertEqual(probe["license_sha256"],
                         reference.SOURCE_LICENSE_SHA256)
        self.assertFalse(probe["executed"])

    def test_library_present_but_not_executed(self) -> None:
        library = self.report["runtime_asset_pin"]["asset:native_library"]
        self.assertTrue(library["present"])
        self.assertTrue(library["sha256_matches_pin"])
        self.assertFalse(library["loaded"])
        self.assertFalse(library["executed"])

    def test_models_absent(self) -> None:
        for key, meta in self.report["asset_pins"].items():
            self.assertFalse(meta["present"], key)
            self.assertFalse(meta["loaded"], key)
            self.assertFalse(meta["executed"], key)

    def test_echo_model_is_primary(self) -> None:
        model = self.report["model_provenance"]["model"]
        self.assertEqual(model["filename"], reference.ECHO_MODEL_FILENAME)
        self.assertEqual(model["sha256"], reference.ECHO_MODEL_SHA256)
        self.assertEqual(model["variant"], "compact-echo-only")

    def test_full_sibling_is_separate(self) -> None:
        sibling = self.report["model_provenance"]["full_enhancement_sibling"]
        self.assertEqual(sibling["filename"], reference.FULL_MODEL_FILENAME)
        self.assertEqual(sibling["sha256"], reference.FULL_MODEL_SHA256)

    def test_acceptance_profile_items(self) -> None:
        for item in reference.ACCEPTANCE_PROFILE_ITEMS:
            self.assertTrue(self.report["acceptance_profile"][item])

    def test_source_reported_not_used(self) -> None:
        self.assertEqual(self.report["source_reported"]["status"],
                         "source_reported_not_reproduced")
        self.assertFalse(
            self.report["source_reported"]["used_for_qualification"])

    def test_licensing_is_blocked(self) -> None:
        licensing = self.report["licensing_analysis"]
        self.assertFalse(licensing["model_redistribution_clearance"])
        self.assertFalse(licensing["product_use_clearance"])
        self.assertFalse(
            licensing["asset_copied_vendored_built_or_downloaded"])

    def test_no_negative_zero(self) -> None:
        self.assertFalse(reference.has_negative_zero(self.report))

    def test_strict_json_duplicate_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":1,"a":2}')

    def test_strict_json_nan_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":NaN}')

    def test_strict_json_infinity_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.strict_loads('{"a":Infinity}')

    def test_pin_lines_reject_traversal(self) -> None:
        with self.assertRaises(ValueError):
            reference.parse_pin_lines("a" * 64 + "  ../escape")

    def test_task_identity_is_stable_only(self) -> None:
        identity = self.report["task_identity"]
        self.assertEqual(identity["id"], reference.TASK)
        self.assertEqual(identity["component"], reference.COMPONENT)
        self.assertEqual(identity["claim_branch"], reference.BRANCH)
        self.assertFalse(identity["mutable_full_board_hashed_or_pinned"])
        self.assertEqual(len(identity["stable_field_digest"]), 64)

    def test_board_full_file_not_pinned(self) -> None:
        pins = (HERE / "SOURCES.sha256").read_text(encoding="ascii")
        for line in pins.splitlines():
            if line.startswith("#"):
                continue
            self.assertNotIn("TASKS.json", line)
        self.assertNotIn(reference.sha256(
            (reference.workspace_root() / "audio-benchmark-platform" / "plan"
             / "swarm" / "TASKS.json").read_bytes()), pins)

    def test_readme_digest_tables(self) -> None:
        counts = reference.verify_readme_digests(
            (HERE / "README.md").read_text(encoding="utf-8"))
        self.assertEqual(counts["source"], len(reference.SOURCE_PINS))
        self.assertEqual(counts["boundary"], len(reference.BOUNDARY_PINS))
        self.assertEqual(counts["artifacts"],
                         len(reference.LOCAL_ARTIFACT_PATHS))
        self.assertEqual(counts["external-absent"],
                         len(reference.EXTERNAL_ASSET_PINS))
        self.assertEqual(counts["external-runtime"],
                         len(reference.EXTERNAL_RUNTIME_PINS))

    def test_sources_pin_manifest(self) -> None:
        pins = reference.parse_pin_lines(
            (HERE / "SOURCES.sha256").read_text(encoding="ascii"))
        self.assertEqual(len(pins), len(reference.allowed_pin_keys()))

    def test_report_json_matches_builder(self) -> None:
        self.assertEqual((HERE / "report.json").read_bytes(),
                         reference.canonical_report_bytes(self.report))

    def test_contract_json_matches_builder(self) -> None:
        self.assertEqual((HERE / "contract.json").read_bytes(),
                         reference.contract_bytes())

    def test_report_sidecar_matches(self) -> None:
        digest = hashlib.sha256(
            (HERE / "report.json").read_bytes()).hexdigest()
        self.assertEqual(
            (HERE / "report.json.sha256").read_text(encoding="ascii"),
            f"{digest}  report.json\n")


if __name__ == "__main__":
    unittest.main()
