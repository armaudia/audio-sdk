# SPDX-FileCopyrightText: 2026 Tsakanyan Hovhannes
# SPDX-License-Identifier: Apache-2.0
"""Deterministic unit checks for the SDK-BEAM-TASNET-BEAM-GUIDED-TASNET package.

No network, no skips, no real audio, weights, runtime or corpus. The checks
exercise canonical bytes, geometry, scenes, variants, config/scene rejection,
lifecycle, admission, the board identity gate and the disposition blocks.
"""

from __future__ import annotations

import copy
import json
import math
import re
import tempfile
import unittest
from pathlib import Path

import reference
import run

HERE = Path(__file__).resolve().parent


class TestCanonicalJson(unittest.TestCase):
    def test_sort_keys_and_compact(self) -> None:
        self.assertEqual(reference.canonical_bytes({"b": 1, "a": [2, 3]}),
                         b'{"a":[2,3],"b":1}')

    def test_report_bytes_trailing_newline(self) -> None:
        self.assertTrue(reference.canonical_report_bytes({"a": 1}).endswith(b"\n"))
        self.assertEqual(reference.canonical_report_bytes({"a": 1}),
                         b'{"a":1}\n')

    def test_negative_zero_normalized(self) -> None:
        encoded = reference.canonical_bytes([-0.0, 0.0])
        self.assertEqual(encoded, b"[0.0,0.0]")
        self.assertNotIn(b"-0.0", encoded)

    def test_nonfinite_rejected(self) -> None:
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("nan")})
        with self.assertRaises(ValueError):
            reference.canonical_bytes({"a": float("inf")})

    def test_strict_json_rejects_duplicate_keys(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "duplicate.json"
            path.write_text('{"a":1,"a":2}', encoding="utf-8")
            with self.assertRaises(reference.EvidenceError):
                reference.strict_json_load(path)

    def test_strict_json_rejects_nonfinite_constant(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "nan.json"
            path.write_text('{"a":NaN}', encoding="utf-8")
            with self.assertRaises(reference.EvidenceError):
                reference.strict_json_load(path)

    def test_sha256_known_vector(self) -> None:
        self.assertEqual(reference.sha256(b"abc"),
                         "ba7816bf8f01cfea414140de5dae2223b00361a396177a9cb410ff61f20015ad")


class TestGeometry(unittest.TestCase):
    def test_target_delays(self) -> None:
        delays = reference.channel_delays_samples(30.0)
        self.assertEqual(delays[0], 0.0)
        self.assertAlmostEqual(delays[1], 640.0 / 343.0, places=12)

    def test_interferer_delays_negative(self) -> None:
        delays = reference.channel_delays_samples(-45.0)
        self.assertAlmostEqual(delays[1], -0.08 * math.sin(math.radians(45.0))
                               / reference.SPEED_OF_SOUND_MPS * reference.SAMPLE_RATE_HZ,
                               places=12)

    def test_zero_delay_is_exact_copy(self) -> None:
        signal = [0.1, -0.2, 0.3, 0.0, -0.4]
        self.assertEqual(reference._fractional_delay(signal, 0.0), signal)

    def test_fractional_delay_preserves_length(self) -> None:
        signal = [float(index) for index in range(11)]
        self.assertEqual(len(reference._fractional_delay(signal, 1.5)), 11)

    def test_geometry_declared_not_measured(self) -> None:
        geometry = reference.geometry()
        self.assertEqual(geometry["channels"], 2)
        self.assertEqual(geometry["reference_channel"], 0)
        self.assertEqual(geometry["mic_spacing_m"], 0.08)
        self.assertTrue(geometry["declared"])
        self.assertFalse(geometry["measured"])
        self.assertFalse(geometry["calibrated"])
        self.assertFalse(geometry["device_verified"])


class TestScenes(unittest.TestCase):
    def test_condition_set(self) -> None:
        self.assertEqual(set(reference.CONDITIONS),
                         {"target_only", "interference_only",
                          "target_plus_interference", "channel_dropout"})

    def test_unknown_condition_rejected(self) -> None:
        with self.assertRaises(reference.EvidenceError):
            reference.synth_scene("unknown")

    def test_deterministic(self) -> None:
        first = reference.synth_scene("target_plus_interference")
        second = reference.synth_scene("target_plus_interference")
        self.assertEqual(reference.sha256(reference.canonical_bytes(first["mixtures"])),
                         reference.sha256(reference.canonical_bytes(second["mixtures"])))

    def test_mixture_is_component_sum(self) -> None:
        scene = reference.synth_scene("target_plus_interference")
        for channel in range(reference.CHANNELS):
            for index in (0, 1, 15999):
                expected = (scene["target_images"][channel][index]
                            + scene["interferer_images"][channel][index]
                            + scene["noise_images"][channel][index])
                self.assertAlmostEqual(scene["mixtures"][channel][index], expected, places=15)

    def test_channel_dropout_zeroes_second_channel(self) -> None:
        scene = reference.synth_scene("channel_dropout")
        self.assertEqual(scene["available_channels"], [0])
        self.assertTrue(all(value == 0.0 for value in scene["mixtures"][1]))

    def test_target_only_has_no_interferer(self) -> None:
        scene = reference.synth_scene("target_only")
        self.assertTrue(all(value == 0.0 for channel in scene["interferer_images"]
                            for value in channel))

    def test_interference_only_has_no_target(self) -> None:
        scene = reference.synth_scene("interference_only")
        self.assertTrue(all(value == 0.0 for channel in scene["target_images"]
                            for value in channel))

    def test_all_scene_values_finite(self) -> None:
        for condition in reference.CONDITIONS:
            scene = reference.synth_scene(condition)
            for channel in scene["mixtures"]:
                self.assertTrue(all(math.isfinite(value) for value in channel))


class TestVariants(unittest.TestCase):
    def test_variant_set(self) -> None:
        self.assertEqual(set(reference.VARIANTS),
                         {"identity_passthrough", "alternate_reference_channel",
                          "naive_channel_mean"})

    def test_identity_is_exact_reference_channel(self) -> None:
        scene = reference.synth_scene("target_plus_interference")
        result = reference.score_variant(scene, "identity_passthrough")
        self.assertEqual(result["output_digest"],
                         reference.sha256(reference.canonical_bytes(scene["mixtures"][0])))

    def test_identity_target_preservation_zero(self) -> None:
        for condition in ("target_only", "target_plus_interference", "channel_dropout"):
            scene = reference.synth_scene(condition)
            result = reference.score_variant(scene, "identity_passthrough")
            self.assertEqual(result["target_preservation_db"], 0.0)

    def test_identity_leakage_zero(self) -> None:
        scene = reference.synth_scene("interference_only")
        result = reference.score_variant(scene, "identity_passthrough")
        self.assertEqual(result["interference_leakage_db"], 0.0)

    def test_naive_mean_weights(self) -> None:
        self.assertEqual(reference.VARIANTS["naive_channel_mean"], [0.5, 0.5])

    def test_alternate_rejected_on_channel_dropout(self) -> None:
        scene = reference.synth_scene("channel_dropout")
        result = reference.score_variant(scene, "alternate_reference_channel")
        self.assertEqual(result["status"], "rejected")
        self.assertEqual(result["reason"], "channel_unavailable")
        self.assertEqual(result["scored_samples"], 0)
        self.assertIsNone(result["output_digest"])

    def test_naive_mean_loses_six_db_on_channel_dropout(self) -> None:
        scene = reference.synth_scene("channel_dropout")
        result = reference.score_variant(scene, "naive_channel_mean")
        self.assertAlmostEqual(result["target_preservation_db"], -6.0206, places=3)

    def test_variant_metrics_finite_or_none(self) -> None:
        for condition in reference.CONDITIONS:
            scene = reference.synth_scene(condition)
            for name in reference.VARIANTS:
                result = reference.score_variant(scene, name)
                for metric in ("si_sdr_db", "target_preservation_db",
                               "interference_leakage_db", "noise_gain_db"):
                    if result[metric] is not None:
                        self.assertTrue(math.isfinite(result[metric]))
                self.assertEqual(result["nonfinite_samples"], 0)
                self.assertEqual(result["clipped_samples"], 0)

    def test_si_sdr_matches_direct_calculation(self) -> None:
        scene = reference.synth_scene("target_plus_interference")
        result = reference.score_variant(scene, "identity_passthrough")
        direct = reference._si_sdr_db(scene["target_images"][0], scene["mixtures"][0])
        self.assertEqual(result["si_sdr_db"], direct)

    def test_interference_only_has_no_si_sdr(self) -> None:
        scene = reference.synth_scene("interference_only")
        result = reference.score_variant(scene, "identity_passthrough")
        self.assertIsNone(result["si_sdr_db"])
        self.assertIsNone(result["target_preservation_db"])


class TestConfig(unittest.TestCase):
    def test_default_config_valid(self) -> None:
        self.assertEqual(reference.validate_config(reference.default_config()), [])

    def test_adverse_case_set(self) -> None:
        self.assertEqual(set(reference.config_adverse_cases()), {
            "wrong_sample_rate", "wrong_channels", "wrong_sample_format",
            "wrong_frame_samples", "wrong_max_clip_samples",
            "reference_channel_out_of_range", "geometry_missing",
            "geometry_not_synchronized", "geometry_spacing_invalid",
            "surrogate_without_opt_in", "caller_weights_unavailable",
            "synthetic_weight_admission_control",
        })

    def test_all_config_cases_fail_closed(self) -> None:
        for name, case in reference.config_adverse_cases().items():
            if name == "synthetic_weight_admission_control":
                self.assertEqual(case["status"], "created")
                self.assertTrue(case["session_created"])
            else:
                self.assertEqual(case["status"], "rejected", name)
                self.assertFalse(case["session_created"], name)

    def test_missing_geometry_rejected(self) -> None:
        config = reference.default_config()
        config.pop("array_geometry")
        self.assertIn("geometry_missing", reference.validate_config(config))

    def test_unsynchronized_array_rejected(self) -> None:
        config = reference.default_config()
        config["array_geometry"]["synchronized"] = False
        self.assertIn("geometry_not_synchronized", reference.validate_config(config))

    def test_surrogate_requires_opt_in(self) -> None:
        config = reference.default_config()
        config["synthetic_surrogate_opt_in"] = False
        self.assertIn("surrogate_opt_in_required", reference.validate_config(config))

    def test_caller_asset_requires_admission(self) -> None:
        config = reference.default_config()
        config["mode"] = "caller-asset"
        self.assertIn("asset_not_admitted", reference.validate_config(config))

    def test_reference_channel_out_of_range(self) -> None:
        config = reference.default_config()
        config["reference_channel"] = 2
        self.assertIn("reference_channel_mismatch", reference.validate_config(config))


class TestAdmission(unittest.TestCase):
    def test_candidate_admission_reasons(self) -> None:
        admission = reference.weight_admission(reference.weight_asset_ref())
        self.assertEqual(admission["status"], "blocked")
        self.assertEqual(admission["reason_codes"], [
            "architecture_not_selected", "source_revision_unpinned",
            "checkpoint_unpinned", "weights_absent", "runtime_unavailable",
            "rights_not_cleared", "array_corpus_absent",
        ])
        self.assertFalse(admission["download_attempted"])
        self.assertFalse(admission["vendor_runtime_invoked"])
        self.assertFalse(admission["asset_bytes_read"])

    def test_candidate_ref_has_no_selected_architecture(self) -> None:
        ref = reference.weight_asset_ref()
        self.assertIsNone(ref["architecture"])
        self.assertIsNone(ref["source_revision"])
        self.assertIsNone(ref["checkpoint_sha256"])
        self.assertFalse(ref["weights_present"])

    def test_synthetic_control_admitted_and_labelled(self) -> None:
        control = reference.synthetic_control_ref()
        self.assertEqual(reference.weight_admission(control)["status"], "admitted")
        self.assertTrue(control["not_the_pinned_candidate"])

    def test_unknown_architecture_rejected(self) -> None:
        ref = reference.weight_asset_ref("SomeOtherModel")
        admission = reference.weight_admission(ref)
        self.assertIn("architecture_not_selected", admission["reason_codes"])

    def test_ambiguous_architecture_record(self) -> None:
        block = reference.candidate_architecture_block()
        self.assertEqual(block["count"], 2)
        self.assertTrue(block["ambiguous"])
        self.assertIsNone(block["selection"])
        self.assertEqual({item["name"] for item in block["distinct_architectures"]},
                         {"Beam-TasNet", "Beam-Guided TasNet"})
        for item in block["distinct_architectures"]:
            self.assertIsNone(item["checkpoint_sha256"])
            self.assertFalse(item["source_or_weights_present"])


class TestSceneBoundary(unittest.TestCase):
    def test_bad_scenes_fail_closed(self) -> None:
        cases = reference.scene_adverse_cases()["cases"]
        self.assertEqual(set(cases), {
            "second_scene", "empty_scene", "channel_count_mismatch",
            "ragged_channels", "oversized_scene", "nonfinite_sample",
            "infinite_sample", "string_sample", "boolean_sample",
            "out_of_range_sample", "after_close",
        })
        for name, case in cases.items():
            self.assertTrue(case["status"].startswith("rejected"), name)
            self.assertTrue(case["state_unchanged"], name)

    def test_process_scene_accounting(self) -> None:
        result = reference.process_scene(reference.fixture_scene())
        self.assertEqual(result["input_channels"], 2)
        self.assertEqual(result["input_samples_per_channel"], reference.SAMPLES)
        self.assertEqual(result["output_channels"], 1)
        self.assertEqual(result["output_samples"], reference.SAMPLES)
        self.assertEqual(set(result["variants"]), set(reference.VARIANTS))

    def test_silent_declared_channel_is_not_channel_loss(self) -> None:
        scene = [[0.0] * 160 for _ in range(2)]
        result = reference.process_scene(scene)
        for variant in result["variants"].values():
            self.assertEqual(variant["status"], "scored")

    def test_ragged_channels_rejected(self) -> None:
        with self.assertRaises(reference.EvidenceError):
            reference.process_scene([[0.0] * 10, [0.0] * 9])


class TestLifecycle(unittest.TestCase):
    def test_one_call_only(self) -> None:
        evidence = reference.lifecycle_evidence()
        self.assertTrue(evidence["one_scene_completed"])
        self.assertTrue(evidence["one_call_only"])
        self.assertTrue(evidence["close_idempotent"])
        self.assertTrue(evidence["zero_length_scene_rejected"])
        self.assertTrue(evidence["process_after_close"].startswith("rejected"))
        self.assertEqual(evidence["calls"], 1)

    def test_no_streaming_api(self) -> None:
        evidence = reference.lifecycle_evidence()
        self.assertTrue(evidence["incremental_process_api_absent"])
        self.assertTrue(evidence["flush_api_absent"])
        self.assertTrue(evidence["reset_api_absent"])

    def test_second_scene_rejected(self) -> None:
        session = reference.SpatialSession()
        session.process_scene(reference.fixture_scene())
        with self.assertRaises(reference.EvidenceError):
            session.process_scene(reference.fixture_scene("target_only"))

    def test_post_close_rejected_without_state_change(self) -> None:
        session = reference.SpatialSession()
        session.close()
        before = session.status_digest()
        with self.assertRaises(reference.EvidenceError):
            session.process_scene(reference.fixture_scene())
        self.assertEqual(session.status_digest(), before)


class TestBoardGate(unittest.TestCase):
    def _board(self) -> dict:
        return reference.load_board()

    def test_projection_is_sha256(self) -> None:
        digest = reference.board_projection_sha256(self._board())
        self.assertEqual(len(digest), 64)
        int(digest, 16)

    def test_projection_contains_only_linked_rows(self) -> None:
        rows = reference.board_rows(self._board())
        self.assertEqual({row["id"] for row in rows},
                         {link["task_id"] for link in reference.BOARD_LINKS})
        for row in rows:
            self.assertEqual(set(row), {"id", "title", "mode"})
        self.assertEqual([row["id"] for row in rows],
                         sorted(row["id"] for row in rows))

    def test_projection_stable_when_mutable_fields_change(self) -> None:
        board = copy.deepcopy(self._board())
        for task in board["tasks"]:
            if task.get("id") in {link["task_id"] for link in reference.BOARD_LINKS}:
                task["status"] = "some-new-status"
                task["owner"] = "someone-else"
                task["blocked_reason"] = "changed"
        self.assertEqual(reference.board_projection_sha256(board),
                         reference.board_projection_sha256(self._board()))

    def test_projection_changes_when_identity_changes(self) -> None:
        board = copy.deepcopy(self._board())
        for task in board["tasks"]:
            if task.get("id") == reference.TASK:
                task["title"] = "Different title"
        self.assertNotEqual(reference.board_projection_sha256(board),
                            reference.board_projection_sha256(self._board()))

    def test_check_board_shape(self) -> None:
        block = reference.check_board()
        self.assertEqual(block["path"], reference.BOARD_PATH)
        self.assertFalse(block["mutable_source_hashed"])
        self.assertEqual(block["projected_fields"], ["id", "title", "mode"])
        self.assertEqual(block["depends_on"],
                         ["SDK-FND-AUDIT", "SDK-FND-EVIDENCE", "SDK-FND-PROVIDER"])


class TestReportBlocks(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.report = reference.build_report()

    def test_identity_and_disposition(self) -> None:
        report = self.report
        self.assertEqual(report["task_id"], reference.TASK)
        self.assertEqual(report["component"], reference.COMPONENT)
        self.assertEqual(report["profile"], "spatial")
        self.assertEqual(report["status"], reference.STATUS)
        self.assertEqual(report["decision"], "DEFER")
        self.assertEqual(report["qualification_status"], "not_qualified")
        self.assertTrue(report["no_missing_result_qualifies_candidate"])

    def test_all_claims_false(self) -> None:
        self.assertTrue(all(value is False for value in self.report["claims"].values()))

    def test_boundary_public_surface_closed(self) -> None:
        for key, value in self.report["boundary"].items():
            if key in ("descriptor_settings", "installed_v0_geometry_preserved"):
                continue
            self.assertIs(value, False, key)
        self.assertEqual(self.report["boundary"]["descriptor_settings"], {})

    def test_eight_release_gates_blocked(self) -> None:
        gates = self.report["release_gates"]
        self.assertEqual(len(gates), 8)
        self.assertEqual({gate["id"] for gate in gates},
                         {f"RG-{index:02d}" for index in range(1, 9)})
        for gate in gates:
            self.assertEqual(gate["status"], "blocked")
            self.assertTrue(gate["evidence"])
            self.assertTrue(gate["reopen"])

    def test_repeatability(self) -> None:
        repeat = self.report["repeatability"]
        self.assertEqual(repeat["count"], 3)
        self.assertTrue(repeat["byte_identical"])
        self.assertEqual(len(set(repeat["digests"])), 1)

    def test_conditions_complete(self) -> None:
        conditions = self.report["conditions"]
        self.assertEqual(set(conditions), set(reference.CONDITIONS))
        for block in conditions.values():
            self.assertEqual(set(block["variants"]), set(reference.VARIANTS))
            self.assertEqual(block["output_accounting"]["output_samples"],
                             reference.SAMPLES)

    def test_regressions_are_negative(self) -> None:
        self.assertTrue(self.report["regression_assessment"]["performed"])
        self.assertTrue(self.report["regressions"])
        for item in self.report["regressions"]:
            self.assertLess(item["delta"], 0.0)

    def test_sibling_evidence_not_pooled(self) -> None:
        sibling = self.report["sibling_evidence"]
        self.assertFalse(sibling["survey_cln_07"]["results_pooled"])
        self.assertFalse(sibling["survey_spk_01"]["results_pooled"])
        self.assertFalse(sibling["adjacent_wpe"]["results_pooled"])

    def test_source_context_has_no_invented_numbers(self) -> None:
        context = self.report["source_reported_context"]
        self.assertIsNone(context["reported_metric_values"])
        self.assertIn("none is invented", context["disclaimer"])

    def test_report_is_finite_and_well_formed_json(self) -> None:
        payload = reference.canonical_report_bytes(self.report)
        loaded = json.loads(payload)
        self.assertEqual(loaded["task_id"], reference.TASK)
        self.assertIsNone(re.search(rb"-0\.0(?=[,\]}]\s*$|[,\]}])", payload))

    def test_build_report_is_stable_across_calls(self) -> None:
        second = reference.build_report()
        self.assertEqual(reference.canonical_report_bytes(self.report),
                         reference.canonical_report_bytes(second))

    def test_board_link_in_report(self) -> None:
        board = self.report["board_link"]
        self.assertFalse(board["mutable_source_hashed"])
        self.assertEqual(board["projection_sha256"],
                         reference.board_projection_sha256(reference.load_board()))


class TestStaticBlocks(unittest.TestCase):
    def test_contract_disposition(self) -> None:
        contract = reference.build_contract()
        self.assertEqual(contract["decision"], "DEFER")
        self.assertEqual(contract["status"], reference.STATUS)
        self.assertEqual(contract["qualification"]["status"], "not_qualified")
        self.assertEqual(contract["qualification"]["evidence_status"], "incomplete")
        self.assertFalse(contract["qualification"]["qualifies"])
        self.assertFalse(contract["qualification"]["missing_result_promoted"])
        self.assertTrue(all(value is False for value in contract["public_surface"].values()))
        self.assertFalse(contract["surrogate"]["substitutes_for_candidate"])
        self.assertFalse(contract["surrogate"]["beamforming_or_separation_modelled"])
        self.assertEqual(contract["artifact_pins"], {})

    def test_adapter_is_unregistered_proposal(self) -> None:
        adapter = reference.build_adapter()
        self.assertEqual(adapter["modes"], ["offline"])
        self.assertEqual(adapter["decision"], "DEFER")
        self.assertFalse(adapter["registration"]["registered"])
        self.assertFalse(adapter["registration"]["enabled_by_default"])
        self.assertFalse(adapter["registration"]["default_selected"])
        self.assertFalse(adapter["configuration"]["streaming_supported"])
        self.assertFalse(adapter["configuration"]["beamforming_supported"])
        self.assertFalse(adapter["configuration"]["separation_supported"])
        self.assertTrue(adapter["architecture_ambiguous"])
        self.assertIsNone(adapter["architecture_selected"])
        self.assertEqual(adapter["asset_readiness"], "blocked")

    def test_readiness_is_blocked(self) -> None:
        readiness = reference.build_readiness()
        self.assertEqual(readiness["status"], "blocked")
        self.assertFalse(readiness["qualified"])
        self.assertEqual(readiness["decision"], "DEFER")
        self.assertEqual(readiness["admission"]["status"], "blocked")
        self.assertEqual(readiness["admission"]["reason_codes"],
                         reference.weight_admission(reference.weight_asset_ref())["reason_codes"])
        for token in ("two distinct architectures", "not ready",
                      "no pinned runnable runtime"):
            self.assertIn(token, readiness["readiness_conclusion"])

    def test_local_file_set_exists(self) -> None:
        for name in reference.LOCAL_FILES:
            self.assertTrue((HERE / name).is_file(), name)
        self.assertTrue((HERE / "reference.py").is_file())


class TestRunHelpers(unittest.TestCase):
    def test_report_bytes_is_canonical_plus_newline(self) -> None:
        payload = run.report_bytes()
        self.assertTrue(payload.endswith(b"\n"))
        self.assertEqual(payload.count(b"\n"), 1)

    def test_readme_table_rows(self) -> None:
        table = run.readme_table().splitlines()
        self.assertEqual(table[0], "| Path | SHA-256 | Bytes |")
        self.assertEqual(table[1], "| --- | --- | ---: |")
        self.assertEqual(len(table), 2 + len(run.README_TABLE_FILES))
        for line in table[2:]:
            self.assertRegex(line, r"^\| `[^`]+` \| `[0-9a-f]{64}` \| [0-9]+ \|$")


if __name__ == "__main__":
    unittest.main()
